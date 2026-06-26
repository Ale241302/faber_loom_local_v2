"""SL3a: SKILL.md parser, routine CRUD, skill invocation and @mention tests."""

from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient


SKILL_MD = """---
name: cotizador
persona: Eres un asistente de cotizaciones.
tools: ["calculator"]
schema_output: {"type": "object", "properties": {"precio": {"type": "number"}}, "required": ["precio"]}
triggers: ["@cotizador"]
---
Genera una cotización en JSON con el precio.
"""

SKILL_MD_HITL = """---
name: cotizador_hitl
persona: Eres un asistente de cotizaciones.
tools: ["calculator", "send_email"]
schema_output: {"type": "object", "properties": {"precio": {"type": "number"}}, "required": ["precio"]}
triggers: ["@cotizador_hitl"]
---
Genera una cotización. Requiere confirmación humana.
"""


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "spaceloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SPACELOOM_DB_PATH", str(db_path))

    for name in (
        "OPENAI_API_KEY",
        "SPACELOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "SPACELOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "SPACELOOM_GOOGLE_API_KEY",
        "SPACELOOM_ENABLE_OLLAMA",
        "SPACELOOM_OLLAMA_ENABLED",
        "SPACELOOM_PROVIDER_ALLOWLIST",
        "SPACELOOM_BUDGET_CAP_USD",
        "SPACELOOM_DEV_TRUST_HEADERS",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.router.config_store import ProviderConfigStore

    # Prevent locally-stored provider keys from leaking into isolated tests.
    monkeypatch.setattr(ProviderConfigStore, "all", lambda self: {})

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _compile_payload(skill_md: str) -> dict[str, Any]:
    from app.src.skills import compile_skill_md

    compiled = compile_skill_md(skill_md)
    return {
        "name": compiled["name"],
        "skill_md": skill_md,
        "persona_md": compiled.get("persona", ""),
        "tools_allowlist": json.dumps(compiled.get("tools", [])),
        "schema_output_json": json.dumps(compiled.get("schema_output", {})),
        "trigger_json": json.dumps(compiled.get("triggers", [])),
        "is_active": 1,
        "source_version": "v1",
    }


def _create_routine(client: TestClient, workspace_id: str, skill_md: str) -> dict[str, Any]:
    response = client.post(
        f"/api/workspaces/{workspace_id}/routines",
        json=_compile_payload(skill_md),
    )
    assert response.status_code == 201, response.text
    return response.json()


def _approve_routine(
    client: TestClient, workspace_id: str, routine_id: str, approved_by: str | None = None
) -> dict[str, Any]:
    params = {}
    if approved_by is not None:
        params["approved_by"] = approved_by
    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/{routine_id}/approve",
        params=params,
    )
    assert response.status_code == 200, response.text
    return response.json()


def _patch_fake_router(
    monkeypatch: pytest.MonkeyPatch,
    content_json: dict[str, Any] | None = None,
) -> None:
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    import app.src.api as api_module

    original_build_router = api_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    cost_module.MODEL_ALLOWLIST["fake"] = {"fake-model"}

    class FakeProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="fake",
                    api_key=None,
                    model_default="fake-model",
                    priority=1,
                    is_enabled=True,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            return CompletionResult(
                content=json.dumps(content_json or {"precio": 12.5}),
                model=request.model or "fake-model",
                provider_slug="fake",
                input_tokens=10,
                output_tokens=8,
                cost_usd=0.0,
                duration_ms=5,
            )

    def fake_build_router() -> Router:
        return Router(providers=[FakeProvider()])

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

    def restore() -> None:
        cost_module.MODEL_ALLOWLIST.clear()
        cost_module.MODEL_ALLOWLIST.update(original_allowlist)
        monkeypatch.setattr(api_module, "build_router", original_build_router)

    # Attach restore helper so callers can clean up after assertions if needed.
    monkeypatch.setattr(api_module, "_restore_fake_router", restore, raising=False)


# -----------------------------------------------------------------------------
# Parser sandbox
# -----------------------------------------------------------------------------


def test_compile_skill_md_extracts_fields() -> None:
    from app.src.skills import compile_skill_md

    compiled = compile_skill_md(SKILL_MD)
    assert compiled["name"] == "cotizador"
    assert compiled["persona"] == "Eres un asistente de cotizaciones."
    assert compiled["tools"] == ["calculator"]
    assert compiled["schema_output"]["type"] == "object"
    assert "@cotizador" in compiled["triggers"]
    assert "Genera una cotización" in compiled["instructions"]


def test_compile_skill_md_rejects_script() -> None:
    from app.src.skills import compile_skill_md

    with pytest.raises(ValueError):
        compile_skill_md(SKILL_MD + "\n<script>alert('xss')</script>")


def test_compile_skill_md_rejects_javascript_scheme() -> None:
    from app.src.skills import compile_skill_md

    with pytest.raises(ValueError):
        compile_skill_md(SKILL_MD + "\n[click](javascript:alert('xss'))")


def test_compile_skill_md_rejects_import_os() -> None:
    from app.src.skills import compile_skill_md

    with pytest.raises(ValueError):
        compile_skill_md(SKILL_MD + "\nimport os")


def test_compile_skill_md_rejects_eval() -> None:
    from app.src.skills import compile_skill_md

    with pytest.raises(ValueError):
        compile_skill_md(SKILL_MD + "\neval(1+1)")


def test_compile_skill_md_rejects_excel_formula() -> None:
    from app.src.skills import compile_skill_md

    with pytest.raises(ValueError):
        compile_skill_md(SKILL_MD + "\n=cmd|'/C calc'!A0")


# -----------------------------------------------------------------------------
# Routine CRUD
# -----------------------------------------------------------------------------


def test_create_routine_from_skill_md(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id, SKILL_MD)
    assert routine["name"] == "cotizador"
    assert routine["workspace_id"] == workspace_id
    assert json.loads(routine["tools_allowlist"]) == ["calculator"]


def test_list_routines(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    created = _create_routine(client, workspace_id, SKILL_MD)

    response = client.get(f"/api/workspaces/{workspace_id}/routines")
    assert response.status_code == 200
    routines = response.json()
    assert any(r["id"] == created["id"] for r in routines)


def test_get_routine(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    created = _create_routine(client, workspace_id, SKILL_MD)

    response = client.get(f"/api/workspaces/{workspace_id}/routines/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def _confirmation_token(resource_id: str) -> str:
    import hashlib

    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def test_delete_routine(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    created = _create_routine(client, workspace_id, SKILL_MD)

    response = client.delete(
        f"/api/workspaces/{workspace_id}/routines/{created['id']}",
        params={"confirmation_token": _confirmation_token(created["id"])},
    )
    assert response.status_code == 204

    response = client.get(f"/api/workspaces/{workspace_id}/routines/{created['id']}")
    assert response.status_code == 404


# -----------------------------------------------------------------------------
# Skill invocation
# -----------------------------------------------------------------------------


def test_invoke_routine_with_fake_provider(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_fake_router(monkeypatch, content_json={"precio": 12.5})
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id, SKILL_MD)
    _approve_routine(client, workspace_id, routine["id"], approved_by="tester")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Oxford"}},
    )
    assert response.status_code == 200, response.text
    run = response.json()
    assert run["status"] == "succeeded"
    assert json.loads(run["output_json"])["precio"] == 12.5


def test_invoke_routine_without_providers_fails(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id, SKILL_MD)
    _approve_routine(client, workspace_id, routine["id"], approved_by="tester")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Oxford"}},
    )
    assert response.status_code == 200
    run = response.json()
    assert run["status"] == "failed"


def test_invoke_routine_requires_hitl_for_unallowlisted_tool(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_fake_router(monkeypatch, content_json={"precio": 12.5})
    workspace_id = _demo_workspace_id(client)
    # Allowlist is empty, so any tool triggers HITL.
    payload = _compile_payload(SKILL_MD_HITL)
    payload["tools_allowlist"] = "[]"
    response = client.post(f"/api/workspaces/{workspace_id}/routines", json=payload)
    assert response.status_code == 201, response.text
    routine = response.json()
    _approve_routine(client, workspace_id, routine["id"], approved_by="tester")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Oxford"}},
    )
    assert response.status_code == 200, response.text
    run = response.json()
    assert run["status"] == "requires_hitl"


# -----------------------------------------------------------------------------
# Approve / reject HITL runs
# -----------------------------------------------------------------------------


def test_approve_and_reject_routine_run(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_fake_router(monkeypatch, content_json={"precio": 12.5})
    workspace_id = _demo_workspace_id(client)
    payload = _compile_payload(SKILL_MD_HITL)
    payload["tools_allowlist"] = "[]"
    routine = client.post(f"/api/workspaces/{workspace_id}/routines", json=payload).json()
    _approve_routine(client, workspace_id, routine["id"], approved_by="tester")

    run = client.post(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Oxford"}},
    ).json()
    assert run["status"] == "requires_hitl"

    response = client.post(f"/api/workspaces/{workspace_id}/routine-runs/{run['id']}/approve")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "succeeded"

    # Create a second run to reject.
    run2 = client.post(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Lino"}},
    ).json()
    response = client.post(f"/api/workspaces/{workspace_id}/routine-runs/{run2['id']}/reject")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "cancelled"


# -----------------------------------------------------------------------------
# @mention in chat
# -----------------------------------------------------------------------------


def test_at_mention_invokes_routine(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_fake_router(monkeypatch, content_json={"precio": 12.5})
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id, SKILL_MD)
    _approve_routine(client, workspace_id, routine["id"], approved_by="tester")

    chat = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Skill mention"},
    ).json()

    response = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}/completions",
        json={"message": "@cotizador cuánto sale Oxford"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"]["role"] == "assistant"
    assert "12.5" in data["message"]["content"]

    runs = client.get(f"/api/workspaces/{workspace_id}/routines/{routine['id']}/runs").json()
    assert len(runs) == 1
    assert json.loads(runs[0]["input_json"]) == {"user_request": "cuánto sale Oxford"}


def test_at_mention_unknown_routine_returns_404(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    chat = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Unknown skill"},
    ).json()

    response = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}/completions",
        json={"message": "@desconocido hola"},
    )
    assert response.status_code == 404
    assert "desconocido" in response.json()["detail"]


# -----------------------------------------------------------------------------
# Workspace isolation
# -----------------------------------------------------------------------------


def test_routine_workspace_isolation(client: TestClient) -> None:
    ws_a = _demo_workspace_id(client)
    ws_b = _create_workspace(client, "Other skills")
    routine = _create_routine(client, ws_a, SKILL_MD)

    response_b = client.get(f"/api/workspaces/{ws_b}/routines/{routine['id']}")
    assert response_b.status_code == 404

    response_b_list = client.get(f"/api/workspaces/{ws_b}/routines")
    assert response_b_list.status_code == 200
    assert response_b_list.json() == []

    response_b_run = client.post(
        f"/api/workspaces/{ws_b}/routines/{routine['id']}/run",
        json={"input_json": {}},
    )
    assert response_b_run.status_code == 404


# -----------------------------------------------------------------------------
# Routine HITL approval
# -----------------------------------------------------------------------------


def test_cannot_run_unapproved_routine(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id, SKILL_MD)
    assert routine["approved_by"] is None

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Oxford"}},
    )
    assert response.status_code == 409, response.text
    assert "approved" in response.json()["detail"].lower()


def test_approve_routine_then_run(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_fake_router(monkeypatch, content_json={"precio": 12.5})
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id, SKILL_MD)

    approved = _approve_routine(client, workspace_id, routine["id"], approved_by="human@test")
    assert approved["approved_by"] == "human@test"

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Oxford"}},
    )
    assert response.status_code == 200, response.text
    run = response.json()
    assert run["status"] == "succeeded"


def test_invalid_schema_output_json_returns_422(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    payload = _compile_payload(SKILL_MD)
    payload["schema_output_json"] = '{"type": "string"}'

    response = client.post(f"/api/workspaces/{workspace_id}/routines", json=payload)
    assert response.status_code == 422, response.text


def test_skill_output_fails_schema_validation(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    # Provider returns a number for "precio" but schema expects a string.
    _patch_fake_router(monkeypatch, content_json={"precio": "doce"})
    workspace_id = _demo_workspace_id(client)
    skill_md = """---
name: cotizador_str
persona: Eres un asistente.
tools: []
schema_output: {"type": "object", "properties": {"precio": {"type": "number"}}, "required": ["precio"]}
triggers: ["@cotizador_str"]
---
Devuelve el precio como número.
"""
    routine = _create_routine(client, workspace_id, skill_md)
    _approve_routine(client, workspace_id, routine["id"], approved_by="tester")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Oxford"}},
    )
    assert response.status_code == 200, response.text
    run = response.json()
    assert run["status"] == "failed"
    evidence = json.loads(run["evidence_json"])
    assert any("schema_error" in item for item in evidence)
