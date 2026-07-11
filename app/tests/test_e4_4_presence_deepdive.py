"""E4-4 — Profundización desde el chat general sin elevar privilegios."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src import key_broker
from app.src.context import Context
from app.src.db import connect
from app.src.key_broker import KeyLevel
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


def _context(ws_id: str, role: str = "owner", tenant_id: str = "default") -> Context:
    return Context(
        workspace_id=ws_id,
        tenant_id=tenant_id,
        user_id="test",
        actor_id="test",
        actor_role_at_decision=role,
    )


def _seed_kb_and_brief(ws_id: str) -> None:
    conn = connect()
    ctx = _context(ws_id)
    ingest_kb_source(
        ctx,
        conn,
        title="Catálogo Colombia",
        source_type="md",
        content_text="## Productos Colombia\n\n- Oxford: USD 12.50/m\n- Cliente: Colombia Textiles",
        source_version="v1",
        approved_by="test",
    )
    refresh_workspace_brief(ctx, conn, ws_id)


def _create_chat(client: TestClient, workspace_id: str) -> str:
    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Chat"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_deepdive_owner_reads_content(client: TestClient) -> None:
    target_id = _create_workspace(client, "Colombia", "colombia")
    _seed_kb_and_brief(target_id)
    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "muéstrame el workspace colombia", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200, resp.text
    content = resp.json()["message"]["content"].lower()
    assert "colombia" in content
    assert "oxford" in content


def test_deepdive_editor_downgraded_to_index(client: TestClient) -> None:
    target_id = _create_workspace(client, "Colombia Sellada", "colombia-sellada")
    _seed_kb_and_brief(target_id)
    conn = connect()
    key_broker.set_policy(
        conn,
        tenant_id="default",
        space_id=target_id,
        level=KeyLevel.CONTENT,
        approver_roles={"owner"},
        updated_by="test",
    )
    refresh_workspace_brief(_context(target_id), conn, target_id)

    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "muéstrame el workspace colombia-sellada", "mode": "manual"},
        headers=_headers("editor"),
    )
    assert resp.status_code == 200, resp.text
    content = resp.json()["message"]["content"].lower()
    assert "contenido detallado" in content or "títulos recientes" in content
    assert "oxford" not in content


def test_deepdive_closed_space_is_blocked(client: TestClient) -> None:
    target_id = _create_workspace(client, "Cerrado", "cerrado")
    _seed_kb_and_brief(target_id)
    conn = connect()
    key_broker.set_policy(
        conn,
        tenant_id="default",
        space_id=target_id,
        level=KeyLevel.CLOSED,
        updated_by="test",
    )
    refresh_workspace_brief(_context(target_id), conn, target_id)

    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "muéstrame el workspace cerrado", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200, resp.text
    content = resp.json()["message"]["content"].lower()
    assert "no tengo acceso" in content
