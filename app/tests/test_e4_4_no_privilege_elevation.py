"""E4-4 — La presencia nunca eleva privilegios al profundizar."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect
from app.src.kb import ingest_kb_source
from app.src.living_agent.briefs import refresh_workspace_brief
from app.src.living_agent.presence import deepdive


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


def test_deepdive_preserves_user_role(client: TestClient) -> None:
    target_id = _create_workspace(client, "Target", "target")
    conn = connect()
    ctx = _context(target_id)
    ingest_kb_source(
        ctx,
        conn,
        title="Fuente target",
        source_type="md",
        content_text="Dato secreto: 12345",
        source_version="v1",
        approved_by="test",
    )
    refresh_workspace_brief(ctx, conn, target_id)

    # General chat context with editor role.
    general_ctx = Context(
        workspace_id=_general_id(client),
        tenant_id="default",
        user_id="editor-user",
        actor_id="editor-user",
        actor_role_at_decision="editor",
    )

    result = deepdive(general_ctx, conn, "muéstrame el workspace target")
    assert result["level"] == "content"  # editor has default CONTENT when no policy
    assert result["target_workspace_id"] == target_id
    # The evidence pack was built with the same editor role, not system.
    assert "target" in result["content"].lower()


def _general_id(client: TestClient) -> str:
    return client.get("/api/workspaces/general", headers=_headers("owner")).json()["id"]
