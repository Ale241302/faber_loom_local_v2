from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.src.models import SCHEMA_VERSION


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
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



def test_v12_migration_maps_unknown_source_version_to_custom(client, tmp_path):
    from app.src.db import connect
    from app.src.models import MIGRATIONS, SCHEMA_VERSION

    test_client, db_path, _ = client
    # Reset DB: close current connection and re-apply migrations 1..11 manually.
    custom_path = tmp_path / "v12_migration.sqlite3"
    import shutil
    shutil.copy(db_path, custom_path)

    # For this test we create a fresh DB by applying migrations up to v11.
    fresh_path = tmp_path / "fresh_v11.sqlite3"
    with sqlite3.connect(fresh_path) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS _schema_version (version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL)")
        for version in sorted(MIGRATIONS):
            if version >= 12:
                break
            conn.executescript(MIGRATIONS[version])
            conn.execute(
                "INSERT INTO _schema_version(version, applied_at) VALUES (?, ?)",
                (version, "2024-01-01T00:00:00Z"),
            )
        # Insert routines with legacy source_version values.
        conn.execute(
            "INSERT INTO workspace (id, name, slug, schema_version, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("ws-test", "Test", "test", SCHEMA_VERSION, "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"),
        )
        conn.execute(
            "INSERT INTO routine (id, workspace_id, name, skill_md, is_active, source_version, schema_version, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("r1", "ws-test", "Unknown", "", 1, "acme-proprietary", SCHEMA_VERSION, "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"),
        )
        conn.execute(
            "INSERT INTO routine (id, workspace_id, name, skill_md, is_active, source_version, schema_version, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("r2", "ws-test", "Agent", "", 1, "faberloom-agent", SCHEMA_VERSION, "2024-01-01T00:00:00Z", "2024-01-01T00:00:00Z"),
        )
        conn.commit()

    # Now apply v12 migration using the real initializer.
    from app.src.db import initialize_database
    import os
    os.environ["FABERLOOM_DB_PATH"] = str(fresh_path)
    with sqlite3.connect(fresh_path) as conn:
        conn.row_factory = sqlite3.Row
        initialize_database(conn)
        rows = {row["id"]: row["category"] for row in conn.execute("SELECT id, category FROM routine").fetchall()}
    assert rows["r1"] == "custom"
    assert rows["r2"] == "agent"


def test_default_routing_preset_mi_preset_is_seeded(client):
    """The default tenant must receive the mi-preset routing preset on startup."""

    _, db_path, _ = client
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM routing_preset WHERE tenant_id = ? AND preset_id = ?",
            ("default", "mi-preset"),
        ).fetchone()

    assert row is not None
    assert row["name"] == "Mi preset"
    assert row["description"] == "Para qué sirve"
    envelope = json.loads(row["envelope_json"])
    assert envelope["jurisdictions"] == ["US", "EU"]
    assert envelope["providers_allow"] == ["anthropic", "openai"]
    assert envelope["data_collection"] == "deny"
    curve = json.loads(row["curve_json"])
    assert curve["mode"] == "balanceado"
    assert curve["borderline_policy"] == "premium"
    caps = json.loads(row["caps_json"])
    assert caps["monthly_budget_usd"] == 50
    escalation = json.loads(row["escalation_json"])
    assert escalation["user_boost_button"] is True


def test_default_archetypes_are_seeded_from_global_skills(client):
    """Each active global skill should have a matching archetype in the default tenant."""

    _, db_path, _ = client
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        skills = conn.execute(
            "SELECT skill_id, name FROM global_skill_catalog WHERE tenant_id = ? AND is_active = 1",
            ("global",),
        ).fetchall()
        archetypes = conn.execute(
            "SELECT archetype_id, routing_preset_id FROM archetype WHERE tenant_id = ?",
            ("default",),
        ).fetchall()

    skill_ids = {row["skill_id"] for row in skills}
    archetype_map = {row["archetype_id"]: row["routing_preset_id"] for row in archetypes}

    assert skill_ids
    assert archetype_map
    for skill_id in skill_ids:
        assert skill_id in archetype_map, f"missing archetype for skill {skill_id}"
        assert archetype_map[skill_id] == "mi-preset"


def test_default_preset_and_archetype_seed_is_idempotent(client):
    """Re-running default seeds must not duplicate presets or archetypes."""

    _, db_path, _ = client
    from app.src.context import Context, SYSTEM_WORKSPACE_ID
    from app.src.db import connect, seed_default_archetypes, seed_routing_presets

    conn = connect()
    try:
        ctx = Context(
            workspace_id=SYSTEM_WORKSPACE_ID,
            tenant_id="default",
            user_id="system",
            actor_id="system",
            actor_role_at_decision="platform_admin",
        )
        seed_routing_presets(ctx, conn)
        seed_default_archetypes(ctx, conn, preset_id="mi-preset")

        preset_count = conn.execute(
            "SELECT COUNT(*) FROM routing_preset WHERE tenant_id = ? AND preset_id = ?",
            ("default", "mi-preset"),
        ).fetchone()[0]
        archetype_count = conn.execute(
            "SELECT COUNT(*) FROM archetype WHERE tenant_id = ? AND routing_preset_id = ?",
            ("default", "mi-preset"),
        ).fetchone()[0]

        seed_routing_presets(ctx, conn)
        seed_default_archetypes(ctx, conn, preset_id="mi-preset")

        preset_count_after = conn.execute(
            "SELECT COUNT(*) FROM routing_preset WHERE tenant_id = ? AND preset_id = ?",
            ("default", "mi-preset"),
        ).fetchone()[0]
        archetype_count_after = conn.execute(
            "SELECT COUNT(*) FROM archetype WHERE tenant_id = ? AND routing_preset_id = ?",
            ("default", "mi-preset"),
        ).fetchone()[0]
    finally:
        conn.close()

    assert preset_count == preset_count_after == 1
    assert archetype_count == archetype_count_after
    assert archetype_count > 0
