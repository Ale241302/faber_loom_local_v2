"""E4-4 — platform_admin solo ve agregados, nunca contenido de tenant."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect
from app.src.kb import ingest_kb_source
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


def _general_id(client: TestClient) -> str:
    return client.get("/api/workspaces/general", headers=_headers("owner")).json()["id"]


def _create_workspace(client: TestClient, name: str, slug: str) -> str:
    resp = client.post(
        "/api/workspaces",
        json={"name": name, "slug": slug},
        headers=_headers("owner"),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _seed_kb(ws_id: str) -> None:
    conn = connect()
    ctx = Context(
        workspace_id=ws_id,
        tenant_id="default",
        user_id="test",
        actor_id="test",
        actor_role_at_decision="owner",
    )
    ingest_kb_source(
        ctx,
        conn,
        title="Secreto",
        source_type="md",
        content_text="Dato confidencial: ABC123",
        source_version="v1",
        approved_by="test",
    )
    refresh_workspace_brief(ctx, conn, ws_id)


def _create_chat(client: TestClient, workspace_id: str) -> str:
    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Admin"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_platform_admin_general_only_index(client: TestClient) -> None:
    ws_id = _create_workspace(client, "Operativo", "operativo")
    _seed_kb(ws_id)
    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "qué hay en mis workspaces", "mode": "manual"},
        headers=_headers("platform_admin"),
    )
    assert resp.status_code == 200, resp.text
    content = resp.json()["message"]["content"]
    assert "Operativo" in content
    assert "ABC123" not in content


def test_platform_admin_deepdive_blocked(client: TestClient) -> None:
    ws_id = _create_workspace(client, "Operativo", "operativo2")
    _seed_kb(ws_id)
    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "muéstrame el workspace operativo2", "mode": "manual"},
        headers=_headers("platform_admin"),
    )
    assert resp.status_code == 200, resp.text
    content = resp.json()["message"]["content"].lower()
    assert "abc123" not in content
