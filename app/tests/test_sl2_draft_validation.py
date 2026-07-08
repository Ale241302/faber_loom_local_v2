"""SL2: draft citation validation tests (aliases, labels, source-to-field)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
        "FABERLOOM_ENABLE_OLLAMA",
        "FABERLOOM_OLLAMA_ENABLED",
        "FABERLOOM_PROVIDER_ALLOWLIST",
        "FABERLOOM_BUDGET_CAP_USD",
            ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def _ingest_source(client: TestClient, workspace_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    response = client.post(f"/api/workspaces/{workspace_id}/kb/sources", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def _set_aliases(client: TestClient, workspace_id: str, aliases: dict[str, list[str]]) -> None:
    response = client.patch(
        f"/api/workspaces/{workspace_id}/field-aliases",
        json={"aliases": aliases},
    )
    assert response.status_code == 200, response.text


def test_workspace_alias_resolves_precio_to_precio_usd(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.src.main import create_app
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    import app.src.api as api_module
    import app.src.draft_engine as draft_engine_module

    original_api_build_router = api_module.build_router
    original_engine_build_router = draft_engine_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    cost_module.MODEL_ALLOWLIST["fake"] = {"fake-model"}

    with TestClient(create_app()) as inner:
        workspace_id = _demo_workspace_id(inner)
        _set_aliases(inner, workspace_id, {"precio": ["precio_usd"]})

        csv_text = "sku,nombre,precio_usd,moneda,stock,vigente_desde,vigente_hasta\nTEL-001,Oxford,12.50,USD,240,2026-01-01,2026-12-31"
        source = _ingest_source(
            inner,
            workspace_id,
            {"title": "Pricing", "type": "csv", "content_text": csv_text},
        )
        source_id = source["id"]

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
                response = {
                    "subject": "Cotización Oxford",
                    "body_md": "El precio de Oxford es USD 12.50 por metro [S1].",
                    "hard_facts_used": [
                        {"field": "precio", "value": "12.50", "source_id": source_id},
                    ],
                    "sources": [
                        {
                            "source_id": source_id,
                            "label": "S1",
                            "title": "Pricing",
                            "excerpt": "Oxford USD 12.50",
                        }
                    ],
                    "warnings": [],
                    "requires_confirmation": False,
                }
                return CompletionResult(
                    content=json.dumps(response),
                    model=request.model or "fake-model",
                    provider_slug="fake",
                    input_tokens=20,
                    output_tokens=40,
                    cost_usd=0.0,
                    duration_ms=10,
                )

        make_fake_router = lambda user_id=None, tenant_id=None, **kwargs: Router(providers=[FakeProvider()])  # noqa: E731
        monkeypatch.setattr(api_module, "build_router", make_fake_router)
        monkeypatch.setattr(draft_engine_module, "build_router", make_fake_router)

        try:
            response = inner.post(
                f"/api/workspaces/{workspace_id}/drafts",
                json={"user_request": "Oxford price"},
            )
            assert response.status_code == 201, response.text
            draft = response.json()
            assert draft["requires_confirmation"] is False
            assert json.loads(draft["blockers_json"]) == []
        finally:
            cost_module.MODEL_ALLOWLIST.clear()
            cost_module.MODEL_ALLOWLIST.update(original_allowlist)
            monkeypatch.setattr(api_module, "build_router", original_api_build_router)
            monkeypatch.setattr(draft_engine_module, "build_router", original_engine_build_router)


def test_unknown_source_label_in_body_is_blocker(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.src.main import create_app
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    import app.src.api as api_module
    import app.src.draft_engine as draft_engine_module

    original_api_build_router = api_module.build_router
    original_engine_build_router = draft_engine_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    cost_module.MODEL_ALLOWLIST["fake"] = {"fake-model"}

    with TestClient(create_app()) as inner:
        workspace_id = _demo_workspace_id(inner)
        csv_text = "sku,price\nTEL-001,12.50"
        source = _ingest_source(
            inner,
            workspace_id,
            {"title": "Pricing", "type": "csv", "content_text": csv_text},
        )
        source_id = source["id"]

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
                response = {
                    "subject": "Cotización",
                    "body_md": "Ver datos en [S99].",
                    "hard_facts_used": [],
                    "sources": [
                        {
                            "source_id": source_id,
                            "label": "S1",
                            "title": "Pricing",
                            "excerpt": "TEL-001 12.50",
                        }
                    ],
                    "warnings": [],
                    "requires_confirmation": False,
                }
                return CompletionResult(
                    content=json.dumps(response),
                    model=request.model or "fake-model",
                    provider_slug="fake",
                    input_tokens=20,
                    output_tokens=40,
                    cost_usd=0.0,
                    duration_ms=10,
                )

        make_fake_router = lambda user_id=None, tenant_id=None, **kwargs: Router(providers=[FakeProvider()])  # noqa: E731
        monkeypatch.setattr(api_module, "build_router", make_fake_router)
        monkeypatch.setattr(draft_engine_module, "build_router", make_fake_router)

        try:
            response = inner.post(
                f"/api/workspaces/{workspace_id}/drafts",
                json={"user_request": "price"},
            )
            assert response.status_code == 201, response.text
            draft = response.json()
            blockers = json.loads(draft["blockers_json"])
            assert any("S99" in b for b in blockers)
            assert draft["requires_confirmation"] is True
        finally:
            cost_module.MODEL_ALLOWLIST.clear()
            cost_module.MODEL_ALLOWLIST.update(original_allowlist)
            monkeypatch.setattr(api_module, "build_router", original_api_build_router)
            monkeypatch.setattr(draft_engine_module, "build_router", original_engine_build_router)


def test_missing_source_label_in_body_is_warning(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.src.main import create_app
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    import app.src.api as api_module
    import app.src.draft_engine as draft_engine_module

    original_api_build_router = api_module.build_router
    original_engine_build_router = draft_engine_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    cost_module.MODEL_ALLOWLIST["fake"] = {"fake-model"}

    with TestClient(create_app()) as inner:
        workspace_id = _demo_workspace_id(inner)
        csv_text = "sku,price\nTEL-001,12.50"
        source = _ingest_source(
            inner,
            workspace_id,
            {"title": "Pricing", "type": "csv", "content_text": csv_text},
        )
        source_id = source["id"]

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
                response = {
                    "subject": "Cotización",
                    "body_md": "El precio es USD 12.50.",
                    "hard_facts_used": [
                        {"field": "price", "value": "12.50", "source_id": source_id},
                    ],
                    "sources": [
                        {
                            "source_id": source_id,
                            "label": "S1",
                            "title": "Pricing",
                            "excerpt": "TEL-001 12.50",
                        }
                    ],
                    "warnings": [],
                    "requires_confirmation": False,
                }
                return CompletionResult(
                    content=json.dumps(response),
                    model=request.model or "fake-model",
                    provider_slug="fake",
                    input_tokens=20,
                    output_tokens=40,
                    cost_usd=0.0,
                    duration_ms=10,
                )

        make_fake_router = lambda user_id=None, tenant_id=None, **kwargs: Router(providers=[FakeProvider()])  # noqa: E731
        monkeypatch.setattr(api_module, "build_router", make_fake_router)
        monkeypatch.setattr(draft_engine_module, "build_router", make_fake_router)

        try:
            response = inner.post(
                f"/api/workspaces/{workspace_id}/drafts",
                json={"user_request": "price"},
            )
            assert response.status_code == 201, response.text
            draft = response.json()
            warnings = json.loads(draft["warnings_json"])
            assert any("[S1]" in w for w in warnings)
            assert json.loads(draft["blockers_json"]) == []
        finally:
            cost_module.MODEL_ALLOWLIST.clear()
            cost_module.MODEL_ALLOWLIST.update(original_allowlist)
            monkeypatch.setattr(api_module, "build_router", original_api_build_router)
            monkeypatch.setattr(draft_engine_module, "build_router", original_engine_build_router)
