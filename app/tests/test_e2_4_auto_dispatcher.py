"""E2-4 auto dispatcher tests, including PDF -> summary -> image chain."""

from __future__ import annotations

import base64
import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.router.engine import Router
from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
from app.src.router.providers import Provider


class FakeTextProvider(Provider):
    """Text provider that returns planner JSON or a plain summary."""

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
        prompt = "\n".join(str(m.get("content", "")) for m in request.messages if m.get("role") == "user")
        if "routing planner" in prompt.lower():
            # Planner prompt: return a three-step plan (will be sliced by max_auto_steps).
            plan = {
                "steps": [
                    {"capability": "text", "task": "summarize", "prompt": "Summarize."},
                    {"capability": "text", "task": "expand", "prompt": "Expand."},
                    {"capability": "text", "task": "answer", "prompt": "Answer."},
                ]
            }
            content = json.dumps(plan)
        else:
            content = "Summary of the document: woven fabric loom."
        return CompletionResult(
            content=content,
            model=request.model or "fake-model",
            provider_slug="fake",
            input_tokens=10,
            output_tokens=10,
            cost_usd=0.001,
            duration_ms=3,
        )


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("FABERLOOM_DEV_TRUST_HEADERS", "true")
    monkeypatch.setenv("FABERLOOM_AUTO_MODE_ENABLED", "true")

    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
        "KIMI_API_KEY",
        "MOONSHOT_API_KEY",
        "FABERLOOM_KIMI_API_KEY",
        "FABERLOOM_ENABLE_OLLAMA",
        "FABERLOOM_OLLAMA_ENABLED",
        "FABERLOOM_PROVIDER_ALLOWLIST",
        "FABERLOOM_BUDGET_CAP_USD",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app
    import app.src.routing.auto_dispatcher as auto_dispatcher_module
    from app.src.router import cost as cost_module

    monkeypatch.setitem(cost_module.MODEL_ALLOWLIST, "fake", {"fake-model"})

    def fake_build_router(*, budget_cap_usd=None, provider_allowlist=None):
        return Router(providers=[FakeTextProvider()])

    monkeypatch.setattr(auto_dispatcher_module, "build_router", fake_build_router)

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def _make_pdf_bytes(text: str) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, text)
    return pdf.output(dest="S")


def _setup_workspace(client: TestClient) -> str:
    ws = _workspace_id(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"auto_mode_enabled": True, "budget_cap_usd": 1.0, "max_auto_steps": 3},
        headers=_headers("owner"),
    )
    client.post(
        f"/api/workspaces/{ws}/model-catalog",
        json={"provider_slug": "fake", "model": "fake-model", "capabilities": ["text", "cheap"], "is_local": True},
        headers=_headers("owner"),
    )
    client.post(
        f"/api/workspaces/{ws}/model-catalog",
        json={"provider_slug": "stub", "model": "fake-image-gen", "capabilities": ["image_gen"], "is_local": True},
        headers=_headers("owner"),
    )
    return ws


def test_auto_mode_disabled_globally(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FABERLOOM_AUTO_MODE_ENABLED", raising=False)
    ws = _workspace_id(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"auto_mode_enabled": True},
        headers=_headers("owner"),
    )
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Auto"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Hi", "mode": "auto"},
        headers=_headers("owner"),
    )
    assert response.status_code == 403


def test_auto_mode_disabled_in_workspace(client: TestClient) -> None:
    ws = _workspace_id(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Auto"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Hi", "mode": "auto"},
        headers=_headers("owner"),
    )
    assert response.status_code == 403


def test_auto_mode_runs_text_chain(client: TestClient) -> None:
    ws = _setup_workspace(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Auto text"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Tell me about looms", "mode": "auto"},
        headers=_headers("owner"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider_slug"] == "fake"
    assert data["chain_id"]
    assert len(data["steps"]) >= 1


def test_auto_mode_respects_max_steps(client: TestClient) -> None:
    ws = _setup_workspace(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"auto_mode_enabled": True, "budget_cap_usd": 1.0, "max_auto_steps": 2},
        headers=_headers("owner"),
    )
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Max steps"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Plan something", "mode": "auto"},
        headers=_headers("owner"),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["steps"]) <= 2


def test_auto_mode_respects_budget_cap(client: TestClient) -> None:
    ws = _setup_workspace(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"auto_mode_enabled": True, "budget_cap_usd": 0.0005, "max_auto_steps": 3},
        headers=_headers("owner"),
    )
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Budget"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Plan something", "mode": "auto"},
        headers=_headers("owner"),
    )
    assert response.status_code == 422


def test_auto_pdf_to_image_chain(client: TestClient) -> None:
    ws = _setup_workspace(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "PDF image"}, headers=_headers("owner")).json()
    pdf_bytes = _make_pdf_bytes("This PDF describes a traditional loom weaving colorful fabric.")
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/auto",
        json={
            "user_request": "Resumen e imagen",
            "attachments": [
                {"filename": "loom.pdf", "mime_type": "application/pdf", "data": base64.b64encode(pdf_bytes).decode("ascii")},
            ],
        },
        headers=_headers("owner"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["chain_id"]
    capabilities = [s["capability"] for s in data["steps"]]
    assert "text" in capabilities
    assert "image_gen" in capabilities
    assert "stub://image/" in data["content"]


def test_auto_pdf_image_fails_without_image_gen_model(client: TestClient) -> None:
    ws = _setup_workspace(client)
    # Find and disable/remove the stub image entry.
    catalog = client.get(f"/api/workspaces/{ws}/model-catalog", headers=_headers("owner")).json()
    stub_entry = next((e for e in catalog if e["provider_slug"] == "stub" and e["model"] == "fake-image-gen"), None)
    if stub_entry:
        client.delete(f"/api/workspaces/{ws}/model-catalog/{stub_entry['id']}", headers=_headers("owner"))

    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "PDF no image"}, headers=_headers("owner")).json()
    pdf_bytes = _make_pdf_bytes("A document about looms.")
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/auto",
        json={
            "user_request": "Resumen e imagen",
            "attachments": [
                {"filename": "loom.pdf", "mime_type": "application/pdf", "data": base64.b64encode(pdf_bytes).decode("ascii")},
            ],
        },
        headers=_headers("owner"),
    )
    assert response.status_code == 422
    assert "image_gen" in response.json()["detail"]


def test_auto_mode_records_step_ledger(client: TestClient) -> None:
    ws = _setup_workspace(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Auto ledger"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Hello", "mode": "auto"},
        headers=_headers("owner"),
    )
    assert response.status_code == 200
    chain_id = response.json()["chain_id"]

    usage = client.get(f"/api/workspaces/{ws}/usage", headers=_headers("owner")).json()
    chain_records = [u for u in usage if u.get("chain_id") == chain_id]
    assert len(chain_records) >= 1
    for record in chain_records:
        assert record["step_index"] is not None
        assert record["capability"]
