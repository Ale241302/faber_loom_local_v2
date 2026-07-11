"""E4-4 — Presencia responde desde briefs INDEX, auditado, sin tocar CONTENT."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect
from app.src.living_agent.briefs import refresh_workspace_brief


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
        "FABERLOOM_AUTO_MODE_ENABLED",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces", headers=_headers("owner")).json()["workspaces"][0]["id"]


def _general_id(client: TestClient) -> str:
    return client.get("/api/workspaces/general", headers=_headers("owner")).json()["id"]


def _context(ws_id: str, role: str = "owner", tenant_id: str = "default") -> Context:
    return Context(
        workspace_id=ws_id,
        tenant_id=tenant_id,
        user_id="test",
        actor_id="test",
        actor_role_at_decision=role,
    )


def _refresh_brief(ws_id: str) -> None:
    conn = connect()
    ctx = _context(ws_id)
    refresh_workspace_brief(ctx, conn, ws_id)


def _create_chat(client: TestClient, workspace_id: str) -> str:
    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Chat general"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_presence_answers_from_index_briefs(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    _refresh_brief(ws_id)
    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "qué hay en mis workspaces", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["provider_slug"] == "presence"
    assert "panorama" in data["message"]["content"].lower()


def test_presence_rejects_deepdive_without_access(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    _refresh_brief(ws_id)
    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "muéstrame el workspace no-existe", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "no detecté" in data["message"]["content"].lower()


def test_presence_chat_greeting(client: TestClient) -> None:
    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "hola", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200, resp.text
    assert "hola" in resp.json()["message"]["content"].lower()


def test_presence_rejects_mention_in_general(client: TestClient) -> None:
    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "@cotizador precio", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 409, resp.text


def test_presence_writes_living_agent_read_audit(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    _refresh_brief(ws_id)
    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "qué hay en mis workspaces", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200, resp.text

    conn = connect()
    rows = conn.execute(
        "SELECT action, payload_json FROM audit_log WHERE action = 'living_agent.read' ORDER BY created_at DESC LIMIT 1"
    ).fetchall()
    assert len(rows) >= 1
    assert rows[0]["action"] == "living_agent.read"
    payload = rows[0]["payload_json"]
    assert "workspaces" in payload
