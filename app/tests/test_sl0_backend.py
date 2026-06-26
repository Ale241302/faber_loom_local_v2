from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.src.models import SCHEMA_VERSION


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "spaceloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SPACELOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("SPACELOOM_DEV_TRUST_HEADERS", "true")

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client, db_path, audit_path


def _columns(db_path: Path, table: str) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def test_health_and_seed_workspace(client):
    test_client, _, _ = client

    health = test_client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["schema_version"] == SCHEMA_VERSION

    workspaces = test_client.get("/api/workspaces")
    assert workspaces.status_code == 200
    payload = workspaces.json()
    assert [workspace["slug"] for workspace in payload["workspaces"]].count("mwt-demo") == 1
    assert payload["workspaces"][0]["name"] == "MWT Demo"


def test_schema_contains_contract_tables_and_latent_fields(client):
    _, db_path, _ = client
    required_tables = {
        "workspace",
        "kb_source",
        "chat",
        "message",
        "draft",
        "audit_log",
        "routine",
        "routine_run",
    }
    latent_fields = {
        "tenant_id",
        "user_id",
        "actor_id",
        "actor_role_at_decision",
        "routine_version",
        "skill_version",
        "schema_version",
        "source_version",
        "approved_by",
    }

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    tables = {row[0] for row in rows}
    assert required_tables.issubset(tables)

    for table in required_tables:
        assert latent_fields.issubset(_columns(db_path, table)), table


def test_seed_is_idempotent(client):
    _, db_path, _ = client
    from app.src.db import connect, initialize_database
    from app.src.seed import seed_demo_workspace

    conn = connect()
    try:
        initialize_database(conn)
        first = seed_demo_workspace(conn)
        second = seed_demo_workspace(conn)
        count = conn.execute("SELECT COUNT(*) FROM workspace WHERE slug = ?", ("mwt-demo",)).fetchone()[0]
    finally:
        conn.close()

    assert first["id"] == second["id"]
    assert count == 1


def test_create_workspace_unique_slug_and_audit(client):
    test_client, db_path, audit_path = client

    first = test_client.post("/api/workspaces", json={"name": "Acme Client", "slug": "acme"})
    second = test_client.post("/api/workspaces", json={"name": "Acme Client", "slug": "acme"})

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["slug"] == "acme"
    assert second.json()["slug"] == "acme-2"

    with sqlite3.connect(db_path) as conn:
        action_count = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action = ?", ("workspace.created",)
        ).fetchone()[0]
    assert action_count == 2

    lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
    created_events = [json.loads(line) for line in lines if json.loads(line)["action"] == "workspace.created"]
    assert len(created_events) == 2


def test_workspace_name_rejects_blank(client):
    test_client, _, _ = client
    response = test_client.post("/api/workspaces", json={"name": "   "})
    assert response.status_code == 422


def test_context_tenant_scope_is_applied_to_workspace_reads(client):
    test_client, _, _ = client

    created = test_client.post(
        "/api/workspaces",
        headers={"x-tenant-id": "tenant-a"},
        json={"name": "Tenant A", "slug": "tenant-a"},
    )
    assert created.status_code == 201
    workspace_id = created.json()["id"]

    assert test_client.get(f"/api/workspaces/{workspace_id}").status_code == 404
    assert (
        test_client.get(f"/api/workspaces/{workspace_id}", headers={"x-tenant-id": "tenant-b"}).status_code
        == 404
    )

    visible = test_client.get(
        f"/api/workspaces/{workspace_id}", headers={"x-tenant-id": "tenant-a"}
    )
    assert visible.status_code == 200
    assert visible.json()["slug"] == "tenant-a"
