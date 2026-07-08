"""E2-4 manual mode provider/model selection and policy enforcement."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.router.engine import Router
from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
from app.src.router.providers import Provider


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
            content="Fake reply",
            model=request.model or "fake-model",
            provider_slug="fake",
            input_tokens=5,
            output_tokens=3,
            cost_usd=0.0,
            duration_ms=7,
        )


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))
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
    import app.src.api as api_module
    from app.src.router import cost as cost_module

    monkeypatch.setitem(cost_module.MODEL_ALLOWLIST, "fake", {"fake-model"})
    monkeypatch.setattr(api_module, "build_router", lambda user_id=None, tenant_id=None, **kwargs: Router(providers=[FakeProvider()]))

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def test_manual_mode_with_selected_model(client: TestClient) -> None:
    ws = _workspace_id(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Manual"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Hi", "provider_slug": "fake", "model": "fake-model", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["provider_slug"] == "fake"
    assert data["model"] == "fake-model"


def test_manual_mode_rejects_unknown_model(client: TestClient) -> None:
    ws = _workspace_id(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Manual"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Hi", "provider_slug": "fake", "model": "unknown-model", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert response.status_code == 422


def test_manual_mode_default_is_manual(client: TestClient) -> None:
    ws = _workspace_id(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Manual"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Hi", "provider_slug": "fake", "model": "fake-model"},
        headers=_headers("owner"),
    )
    assert response.status_code == 200


def test_manual_mode_local_only_blocks_cloud(client: TestClient) -> None:
    ws = _workspace_id(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"require_local_only": True},
        headers=_headers("owner"),
    )
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Local only"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Hi", "provider_slug": "fake", "model": "fake-model"},
        headers=_headers("owner"),
    )
    assert response.status_code == 422
    assert "local-only" in response.json()["detail"]


def test_manual_mode_policy_model_allowlist(client: TestClient) -> None:
    ws = _workspace_id(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"model_allowlist": {"fake": ["other-model"]}},
        headers=_headers("owner"),
    )
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Allowlist"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Hi", "provider_slug": "fake", "model": "fake-model"},
        headers=_headers("owner"),
    )
    assert response.status_code == 422
    assert "not allowed" in response.json()["detail"]
