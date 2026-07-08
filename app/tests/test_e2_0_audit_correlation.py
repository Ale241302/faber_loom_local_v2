"""E2-0 Bloque 2 — Correlación de eventos de auditoría.

Verifica que las llamadas a audit_writer.write para routines, routine_runs,
skill executions y gold_candidates propaguen un correlation_id estable al
audit_log, permitiendo reconstruir la trazabilidad de un recurso.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

OWNER = {"email": "owner@acme.test", "display_name": "Owner", "password": "s3cret-pass"}

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


def _make_app():
    from app.src.main import create_app

    return create_app()


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "fnd.sqlite3"))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        f'{{"{OWNER["email"]}":"{OWNER["password"]}"}}',
    )
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)
    monkeypatch.setenv("FABERLOOM_BUDGET_CAP_USD", "5.0")

    # Prevent locally-stored provider keys from leaking into isolated tests.
    from app.src.router.config_store import ProviderConfigStore

    monkeypatch.setattr(ProviderConfigStore, "all", lambda self, user_id=None: {})

    with TestClient(_make_app()) as test_client:
        yield test_client


def _bootstrap(client: TestClient) -> dict:
    """Bootstrap Foundation tenant + owner and activate."""
    resp = client.post(
        "/api/foundation/bootstrap/tenant", json={"name": "ACME S.A.", "slug": "acme"}
    )
    assert resp.status_code == 201, resp.text
    resp = client.post("/api/foundation/bootstrap/owner", json=OWNER)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    session = data["session"]
    user = data["user"]
    resp = client.post("/api/foundation/bootstrap/activate", headers={"X-Fnd-Session": session})
    assert resp.status_code == 200, resp.text
    return user


def _login_legacy(client: TestClient) -> None:
    """Login via legacy /api/auth/login (matches FABERLOOM_USERS)."""
    resp = client.post(
        "/api/auth/login", json={"email": OWNER["email"], "password": OWNER["password"]}
    )
    assert resp.status_code == 200, resp.text


def _compile_payload(skill_md: str) -> dict[str, Any]:
    from app.src.skills import _extract_runtime, compile_skill_md

    compiled = compile_skill_md(skill_md)
    runtime = _extract_runtime(skill_md)
    return {
        "name": compiled["name"],
        "skill_md": skill_md,
        "persona_md": runtime.get("persona", ""),
        "tools_allowlist": json.dumps(runtime.get("tools", [])),
        "schema_output_json": json.dumps(runtime.get("schema_output", {})),
        "trigger_json": json.dumps(runtime.get("triggers", [])),
        "is_active": 1,
        "source_version": "v1",
        "category": "skill",
    }


def _patch_fake_router(
    monkeypatch: pytest.MonkeyPatch,
    content_json: dict[str, Any] | None = None,
    cost_usd: float = 0.0,
) -> None:
    """Replace Router with a deterministic fake provider."""
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig, RouterSettings
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
                cost_usd=cost_usd,
                duration_ms=5,
            )

    def fake_build_router(user_id: str | None = None, *, tenant_id: str | None = None, **kwargs) -> Router:
        return Router(
            settings=RouterSettings(budget_cap_usd=5.0),
            providers=[FakeProvider()],
        )

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

    def restore() -> None:
        cost_module.MODEL_ALLOWLIST.clear()
        cost_module.MODEL_ALLOWLIST.update(original_allowlist)
        monkeypatch.setattr(api_module, "build_router", original_build_router)

    monkeypatch.setattr(api_module, "_restore_fake_router", restore, raising=False)


def _create_workspace(client: TestClient, name: str) -> dict[str, Any]:
    resp = client.post("/api/workspaces", json={"name": name})
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_routine(
    client: TestClient, workspace_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    resp = client.post(
        f"/api/workspaces/{workspace_id}/routines",
        json=payload,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _approve_routine(client: TestClient, workspace_id: str, routine_id: str) -> dict[str, Any]:
    resp = client.post(f"/api/workspaces/{workspace_id}/routines/{routine_id}/approve")
    assert resp.status_code == 200, resp.text
    return resp.json()


def _audit_row_for_action(client: TestClient, action: str) -> sqlite3.Row | None:
    """Return the most recent audit_log row for the given action."""
    db_path = os.environ["FABERLOOM_DB_PATH"]
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(
            "SELECT * FROM audit_log WHERE action = ? ORDER BY created_at DESC LIMIT 1",
            (action,),
        ).fetchone()
    finally:
        conn.close()


def test_routine_approved_audit_has_correlation_id(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    user = _bootstrap(client)
    _login_legacy(client)

    workspace = _create_workspace(client, "E2-0 Audit Correlation")
    routine = _create_routine(client, workspace["id"], _compile_payload(SKILL_MD))

    approved = _approve_routine(client, workspace["id"], routine["id"])
    assert approved["approved_by"] == user["id"]

    row = _audit_row_for_action(client, "routine.approved")
    assert row is not None
    assert row["correlation_id"] == routine["id"]
    assert row["actor_id"] == user["id"]
    assert row["user_id"] == user["id"]
    assert row["tenant_id"] == user["tenant_id"]
    assert row["actor_role_at_decision"] == "owner"


def test_skill_executed_audit_has_run_correlation_id(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_fake_router(monkeypatch, content_json={"precio": 12.5})
    _bootstrap(client)
    _login_legacy(client)

    workspace = _create_workspace(client, "E2-0 Run Correlation")
    routine = _create_routine(client, workspace["id"], _compile_payload(SKILL_MD))
    _approve_routine(client, workspace["id"], routine["id"])

    resp = client.post(
        f"/api/workspaces/{workspace['id']}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Oxford"}},
    )
    assert resp.status_code == 200, resp.text
    run = resp.json()
    assert run["status"] == "succeeded"

    row = _audit_row_for_action(client, "skill.executed")
    assert row is not None
    assert row["correlation_id"] == run["id"]
    payload = json.loads(row["payload_json"])
    assert payload["run_id"] == run["id"]


def test_routine_run_approved_audit_has_run_correlation_id(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_fake_router(monkeypatch, content_json={"precio": 12.5})
    _bootstrap(client)
    _login_legacy(client)

    workspace = _create_workspace(client, "E2-0 HITL Correlation")
    payload = _compile_payload(SKILL_MD_HITL)
    payload["tools_allowlist"] = "[]"
    routine = _create_routine(client, workspace["id"], payload)
    _approve_routine(client, workspace["id"], routine["id"])

    resp = client.post(
        f"/api/workspaces/{workspace['id']}/routines/{routine['id']}/run",
        json={"input_json": {"producto": "Oxford"}},
    )
    assert resp.status_code == 200, resp.text
    run = resp.json()
    assert run["status"] == "requires_hitl"

    resp = client.post(f"/api/workspaces/{workspace['id']}/routine-runs/{run['id']}/approve")
    assert resp.status_code == 200, resp.text
    approved_run = resp.json()
    assert approved_run["status"] == "succeeded"

    row = _audit_row_for_action(client, "routine_run.approved")
    assert row is not None
    assert row["correlation_id"] == run["id"]
    payload = json.loads(row["payload_json"])
    assert payload["run_id"] == run["id"]
