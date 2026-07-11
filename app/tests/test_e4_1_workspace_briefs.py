"""E4-1 Workspace Briefs tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src import key_broker
from app.src.context import Context
from app.src.db import connect
from app.src.key_broker import KeyLevel
from app.src.living_agent.briefs import (
    build_workspace_brief,
    get_workspace_brief,
    is_brief_stale,
    refresh_workspace_brief,
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
        "FABERLOOM_AUTO_MODE_ENABLED",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def _context(ws_id: str, role: str = "owner", tenant_id: str = "default") -> Context:
    return Context(
        workspace_id=ws_id,
        tenant_id=tenant_id,
        user_id="test",
        actor_id="test",
        actor_role_at_decision=role,
    )


def test_workspace_brief_table_exists(client: TestClient) -> None:
    conn = connect()
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='workspace_brief'"
    ).fetchone()
    assert row is not None


def test_build_brief_default_content(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    ctx = _context(ws_id, role="owner")
    brief = build_workspace_brief(ctx, conn, ws_id)

    assert brief["sealed"] is False
    assert brief["level"] == "content"
    assert "source_counts" in brief
    assert "recent_titles" in brief
    assert "open_invoices" in brief
    assert "items" not in brief["open_invoices"]
    assert "total_usd" in brief["open_invoices"]


def test_build_brief_open_invoices_are_aggregates_only(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    ctx = _context(ws_id, role="owner")
    brief = build_workspace_brief(ctx, conn, ws_id)

    invoices = brief.get("open_invoices", {})
    assert set(invoices.keys()) <= {"count", "total_usd"}
    assert "items" not in invoices


def test_build_brief_closed_space(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    key_broker.set_policy(
        conn,
        tenant_id="default",
        space_id=ws_id,
        level=KeyLevel.CLOSED,
        updated_by="test",
    )

    ctx = _context(ws_id, role="owner")
    brief = build_workspace_brief(ctx, conn, ws_id)

    assert brief["sealed"] is True
    assert brief["level"] == "closed"
    assert "object_count" in brief
    assert "open_invoices" not in brief


def test_build_brief_content_sealed_for_non_approver(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    key_broker.set_policy(
        conn,
        tenant_id="default",
        space_id=ws_id,
        level=KeyLevel.CONTENT,
        approver_roles={"owner"},
        updated_by="test",
    )

    ctx = _context(ws_id, role="editor")
    brief = build_workspace_brief(ctx, conn, ws_id)

    assert brief["sealed"] is True
    assert brief["level"] == "index"
    assert "open_invoices" not in brief
    assert "recent_titles" in brief


def test_refresh_persists_brief(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    ctx = _context(ws_id, role="owner")

    row = refresh_workspace_brief(ctx, conn, ws_id)
    assert row["workspace_id"] == ws_id
    assert row["version"] == 1
    assert row["schema_version"] == 42
    assert "brief_json" in row

    fetched = get_workspace_brief(conn, ctx, ws_id)
    assert fetched is not None
    assert fetched["workspace_id"] == ws_id
    assert fetched["brief"]["level"] == "content"


def test_is_brief_stale_missing(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    ctx = _context(ws_id, role="owner")

    stale, diagnostics = is_brief_stale(conn, ctx, ws_id)
    assert stale is True
    assert diagnostics["reason"] == "missing"


def test_get_brief_endpoint_returns_404_when_missing(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    resp = client.get(f"/api/workspaces/{ws_id}/brief", headers=_headers("owner"))
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Brief not found"


def test_get_brief_endpoint_returns_persisted_brief(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    ctx = _context(ws_id, role="owner")
    refresh_workspace_brief(ctx, conn, ws_id)

    resp = client.get(f"/api/workspaces/{ws_id}/brief", headers=_headers("owner"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["workspace_id"] == ws_id
    assert data["schema_version"] == 42
    assert data["brief"]["level"] == "content"
    assert "open_invoices" in data["brief"]
    assert "items" not in data["brief"]["open_invoices"]


def test_get_brief_endpoint_degrades_for_non_approver(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    key_broker.set_policy(
        conn,
        tenant_id="default",
        space_id=ws_id,
        level=KeyLevel.CONTENT,
        approver_roles={"owner"},
        updated_by="test",
    )
    refresh_workspace_brief(_context(ws_id, role="owner"), conn, ws_id)

    resp = client.get(f"/api/workspaces/{ws_id}/brief", headers=_headers("editor"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["brief"]["level"] == "index"
    assert "open_invoices" not in data["brief"]


def test_get_brief_endpoint_closed_space_is_sealed(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    key_broker.set_policy(
        conn,
        tenant_id="default",
        space_id=ws_id,
        level=KeyLevel.CLOSED,
        updated_by="test",
    )
    refresh_workspace_brief(_context(ws_id, role="owner"), conn, ws_id)

    resp = client.get(f"/api/workspaces/{ws_id}/brief", headers=_headers("owner"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["brief"]["level"] == "closed"
    assert data["brief"]["sealed"] is True
    assert "open_invoices" not in data["brief"]
    assert "recent_titles" not in data["brief"]


def test_get_brief_endpoint_ceo_only_excludes_non_ceo(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    conn = connect()
    key_broker.set_policy(
        conn,
        tenant_id="default",
        space_id=ws_id,
        level=KeyLevel.CONTENT,
        approver_roles={"owner"},
        ceo_only=True,
        updated_by="test",
    )
    refresh_workspace_brief(_context(ws_id, role="owner"), conn, ws_id)

    resp = client.get(f"/api/workspaces/{ws_id}/brief", headers=_headers("owner"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["brief"]["level"] == "closed"
    assert data["brief"]["sealed"] is True
    assert "recent_titles" not in data["brief"]


def test_ambient_cycle_refreshes_brief(client: TestClient) -> None:
    ws_id = _workspace_id(client)
    from app.src.ambient import (
        get_orchestrator,
        seed_ambient_config,
        update_ambient_config,
    )

    conn = connect()
    seed_ambient_config(conn, "default")
    update_ambient_config(
        conn,
        "default",
        {
            "global_enabled": 1,
            "budget_pct_of_router_daily": 5.0,
        },
    )

    ctx = _context(ws_id, role="owner")

    # Run cycle for this single workspace.
    orchestrator = get_orchestrator()
    closed = orchestrator.run_cycle(conn, "default", workspace_id=ws_id, trigger="manual")
    assert closed["status"] == "completed"

    brief_row = get_workspace_brief(conn, ctx, ws_id)
    assert brief_row is not None
    assert brief_row["workspace_id"] == ws_id
    assert brief_row["version"] >= 1
