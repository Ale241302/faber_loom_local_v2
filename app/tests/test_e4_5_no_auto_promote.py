"""E4-5 — CAPA 1 must never auto-promote feedback into memory."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))
    for name in (
        "OPENAI_API_KEY", "FABERLOOM_OPENAI_API_KEY", "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY", "KIMI_API_KEY", "MOONSHOT_API_KEY",
        "FABERLOOM_KIMI_API_KEY", "FABERLOOM_ENABLE_OLLAMA", "FABERLOOM_OLLAMA_ENABLED",
        "FABERLOOM_PROVIDER_ALLOWLIST", "FABERLOOM_BUDGET_CAP_USD",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app
    import app.src.api as api_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider
    from app.src.router import cost as cost_module

    class FakeProvider(Provider):
        requires_api_key = False
        def __init__(self) -> None:
            super().__init__(ProviderConfig(provider_slug="fake", api_key=None, model_default="fake-model", priority=1, is_enabled=True))
        def complete(self, request: CompletionRequest) -> CompletionResult:
            return CompletionResult(content="Fake reply", model=request.model or "fake-model", provider_slug="fake", input_tokens=5, output_tokens=3, cost_usd=0.0, duration_ms=7)

    monkeypatch.setitem(cost_module.MODEL_ALLOWLIST, "fake", {"fake-model"})
    monkeypatch.setattr(api_module, "build_router", lambda user_id=None, tenant_id=None, **kwargs: Router(providers=[FakeProvider()]))

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(user: str = "test", role: str = "owner") -> dict[str, str]:
    return {"x-user-id": user, "x-actor-id": user, "x-actor-role": role}


def _assistant_message_id(client: TestClient, workspace_id: str, user: str = "test") -> tuple[str, str]:
    chat = client.post(f"/api/workspaces/{workspace_id}/chats", json={"title": "Memory"}, headers=_headers(user)).json()
    res = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}/completions",
        json={"message": "hello", "mode": "manual", "provider_slug": "fake", "model": "fake-model"},
        headers=_headers(user),
    )
    assert res.status_code == 200
    messages = client.get(f"/api/workspaces/{workspace_id}/chats/{chat['id']}/messages", headers=_headers(user)).json()
    assistant = [m for m in messages if m["role"] == "assistant"]
    assert assistant
    return chat["id"], assistant[0]["id"]


def test_feedback_never_creates_memory_block(client: TestClient) -> None:
    ws = _workspace_id(client)
    for _ in range(5):
        chat_id, message_id = _assistant_message_id(client, ws)
        client.post(
            f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
            json={"outcome": "rejected", "reason": "too_long"},
            headers=_headers(),
        )

    applied = client.get(f"/api/workspaces/{ws}/memory/proposals?state=applied", headers=_headers()).json()
    assert applied == []


def test_index_only_materializes_pending_proposals(client: TestClient) -> None:
    ws = _workspace_id(client)
    for _ in range(3):
        chat_id, message_id = _assistant_message_id(client, ws)
        client.post(
            f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
            json={"outcome": "rejected", "reason": "wrong"},
            headers=_headers(),
        )

    index = client.post(f"/api/workspaces/{ws}/memory/index", headers=_headers()).json()
    assert index["created"]

    proposals = client.get(f"/api/workspaces/{ws}/memory/proposals?state=pending", headers=_headers()).json()
    assert len(proposals) == 1
    assert proposals[0]["state"] == "pending"
