"""SL2: end-to-end citation traceability from output field to source section."""

from __future__ import annotations

import io
import json
from typing import Any

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook


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


def _make_xlsx_bytes() -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Catalogo"
    sheet.append(["sku", "nombre", "precio_usd", "moneda", "stock", "vigente_desde", "vigente_hasta"])
    sheet.append(["TEL-001", "Oxford", "12.50", "USD", 240, "2026-01-01", "2026-12-31"])
    buf = io.BytesIO()
    workbook.save(buf)
    return buf.getvalue()


def _upload_xlsx(client: TestClient, workspace_id: str) -> dict[str, Any]:
    response = client.post(
        f"/api/workspaces/{workspace_id}/kb/upload",
        data={"title": "Catalogo", "source_version": "v1"},
        files={
            "file": (
                "catalogo.xlsx",
                io.BytesIO(_make_xlsx_bytes()),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_citation_traces_field_to_source_sheet_and_locator(
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
        source = _upload_xlsx(inner, workspace_id)
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
                        {"field": "precio_usd", "value": "12.50", "source_id": source_id},
                    ],
                    "sources": [
                        {
                            "source_id": source_id,
                            "label": "S1",
                            "title": "Catalogo",
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

        make_fake_router = lambda user_id=None: Router(providers=[FakeProvider()])  # noqa: E731
        monkeypatch.setattr(api_module, "build_router", make_fake_router)
        monkeypatch.setattr(draft_engine_module, "build_router", make_fake_router)

        try:
            response = inner.post(
                f"/api/workspaces/{workspace_id}/drafts",
                json={"user_request": "TEL-001"},
            )
            assert response.status_code == 201, response.text
            draft = response.json()
            assert draft["requires_confirmation"] is False
            assert json.loads(draft["blockers_json"]) == []

            hard_facts = json.loads(draft["hard_facts_json"])
            assert len(hard_facts) == 1
            fact = hard_facts[0]
            assert fact["field"] == "precio_usd"
            assert fact["value"] == "12.50"
            assert fact["source_id"] == source_id
            assert "Catalogo" in (fact.get("source_sheet") or "")
            assert fact.get("source_locator")
            assert "[S1]" in draft["body_md"]
        finally:
            cost_module.MODEL_ALLOWLIST.clear()
            cost_module.MODEL_ALLOWLIST.update(original_allowlist)
            monkeypatch.setattr(api_module, "build_router", original_api_build_router)
            monkeypatch.setattr(draft_engine_module, "build_router", original_engine_build_router)
