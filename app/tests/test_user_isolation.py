"""Per-user isolation tests for the FaberLoom spike.

These tests verify that ``alejandro@muitowork.com`` and ``alvaro@muitowork.com``
have independent provider configuration, chats, and SMTP settings.
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


USER_A = "alejandro@muitowork.com"
USER_B = "alvaro@muitowork.com"
PASSWORD = "secret"


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret")
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        f'{{"{USER_A}":"{PASSWORD}","{USER_B}":"{PASSWORD}"}}',
    )

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
        "FABERLOOM_DEV_TRUST_HEADERS",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _token(client: TestClient, email: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(email: str, token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _demo_workspace_id(client: TestClient, token: str) -> str:
    response = client.get("/api/workspaces", headers=_auth(USER_A, token))
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def test_provider_config_is_per_user(client: TestClient) -> None:
    token_a = _token(client, USER_A)
    token_b = _token(client, USER_B)
    workspace_id = _demo_workspace_id(client, token_a)

    # User A configures OpenAI.
    response = client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        headers=_auth(USER_A, token_a),
        json={"api_key": "sk-user-a-1234567890123456", "model_default": "gpt-4o", "priority": 5},
    )
    assert response.status_code == 200, response.text
    assert response.json()["api_key_masked"].endswith("3456")

    # User B still sees the default unconfigured state.
    response = client.get(
        f"/api/workspaces/{workspace_id}/providers",
        headers=_auth(USER_B, token_b),
    )
    assert response.status_code == 200
    openai_b = next(p for p in response.json()["providers"] if p["provider_slug"] == "openai")
    assert openai_b["api_key_masked"] is None
    assert openai_b["priority"] != 5

    # User A still sees their own config.
    response = client.get(
        f"/api/workspaces/{workspace_id}/providers",
        headers=_auth(USER_A, token_a),
    )
    openai_a = next(p for p in response.json()["providers"] if p["provider_slug"] == "openai")
    assert openai_a["api_key_masked"].endswith("3456")
    assert openai_a["priority"] == 5


def test_chat_is_per_user(client: TestClient) -> None:
    token_a = _token(client, USER_A)
    token_b = _token(client, USER_B)
    workspace_id = _demo_workspace_id(client, token_a)

    response = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        headers=_auth(USER_A, token_a),
        json={"title": "User A chat"},
    )
    assert response.status_code == 201
    chat_id = response.json()["id"]

    # User A sees the chat.
    response = client.get(
        f"/api/workspaces/{workspace_id}/chats",
        headers=_auth(USER_A, token_a),
    )
    assert response.status_code == 200
    assert any(c["id"] == chat_id for c in response.json())

    # User B does not see it.
    response = client.get(
        f"/api/workspaces/{workspace_id}/chats",
        headers=_auth(USER_B, token_b),
    )
    assert response.status_code == 200
    assert not any(c["id"] == chat_id for c in response.json())

    # User B cannot access the chat directly or its messages.
    assert (
        client.get(
            f"/api/workspaces/{workspace_id}/chats/{chat_id}",
            headers=_auth(USER_B, token_b),
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"/api/workspaces/{workspace_id}/chats/{chat_id}/messages",
            headers=_auth(USER_B, token_b),
        ).status_code
        == 404
    )


def test_smtp_config_is_per_user(client: TestClient) -> None:
    token_a = _token(client, USER_A)
    token_b = _token(client, USER_B)
    workspace_id = _demo_workspace_id(client, token_a)

    config = {
        "host": "mail.a.example.com",
        "port": 465,
        "use_ssl": True,
        "username": "a@example.com",
        "password": "secret-a",
        "from_email": "a@example.com",
    }

    response = client.put(
        f"/api/workspaces/{workspace_id}/admin/smtp-config",
        headers=_auth(USER_A, token_a),
        json=config,
    )
    assert response.status_code == 200, response.text

    # User A sees the config.
    response = client.get(
        f"/api/workspaces/{workspace_id}/admin/smtp-config",
        headers=_auth(USER_A, token_a),
    )
    assert response.status_code == 200
    assert response.json()["host"] == "mail.a.example.com"

    # User B does not see User A's config.
    response = client.get(
        f"/api/workspaces/{workspace_id}/admin/smtp-config",
        headers=_auth(USER_B, token_b),
    )
    assert response.status_code == 404
