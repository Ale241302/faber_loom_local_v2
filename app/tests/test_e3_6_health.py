"""E3-6 — Tenant health dashboard (platform admin + owner mirror)."""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated app with fresh Foundation and app DBs."""

    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv("FABERLOOM_USERS", '{"test@example.test":"password"}')
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)

    from app.src.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


def _auth_headers(tenant_id: str, role: str = "owner", user_id: str = "usr_test") -> dict[str, str]:
    from app.src.auth import create_access_token

    token = create_access_token(
        "test@example.test",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
    )
    return {"Authorization": f"Bearer {token}"}


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _app_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_DB_PATH"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _create_foundation_user(
    conn: sqlite3.Connection,
    tenant_id: str,
    email: str,
    role: str,
) -> str:
    from app.src.foundation.core import hash_password, new_id, seed_system_roles, utcnow

    seed_system_roles(conn, tenant_id)
    user_id = new_id("usr")
    now = utcnow()
    conn.execute(
        """
        INSERT INTO fnd_users
        (id, tenant_id, email, display_name, password_hash, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'active', ?)
        """,
        (
            user_id,
            tenant_id,
            email,
            email.split("@")[0],
            hash_password("irrelevant-for-legacy-login"),
            now,
        ),
    )
    role_row = conn.execute(
        "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?",
        (tenant_id, role),
    ).fetchone()
    if role_row is None:
        raise RuntimeError(f"Role {role} missing for tenant {tenant_id}")
    conn.execute(
        """
        INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (tenant_id, user_id, role_row["id"], user_id, now),
    )
    return user_id


def _bootstrap_tenant(client: TestClient, slug: str, owner_email: str) -> str:
    from app.src.foundation.core import new_id, utcnow

    conn = _foundation_conn(client)
    try:
        tenant_id = new_id("tnt")
        conn.execute(
            """
            INSERT INTO fnd_tenants
            (id, name, slug, status, plan, created_at, activated_at)
            VALUES (?, ?, ?, 'active', 'starter', ?, ?)
            """,
            (tenant_id, f"Tenant {slug}", slug, utcnow(), utcnow()),
        )
        _create_foundation_user(conn, tenant_id, owner_email, "owner")
        conn.commit()
        return tenant_id
    finally:
        conn.close()


def _seed_health_data(client: TestClient, tenant_id: str) -> tuple[str, str]:
    """Create a workspace, routine, runs and usage records for the tenant."""

    headers = _auth_headers(tenant_id)
    resp = client.post(
        "/api/workspaces",
        json={"name": "Health Workspace", "slug": "health-ws"},
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    workspace_id = resp.json()["id"]

    app_conn = _app_conn(client)
    try:
        now = datetime.now(timezone.utc).isoformat()
        routine_id = f"rout_{tenant_id}"
        app_conn.execute(
            """
            INSERT INTO routine (id, workspace_id, tenant_id, name, skill_md, is_active, schema_version, source_version, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, 2, 'v1', ?, ?)
            """,
            (routine_id, workspace_id, tenant_id, "Health Routine", "", now, now),
        )
        for i, status in enumerate(["succeeded", "succeeded", "failed"]):
            app_conn.execute(
                """
                INSERT INTO routine_run (id, routine_id, workspace_id, tenant_id, input_json, output_json, evidence_json, status, schema_version, created_at)
                VALUES (?, ?, ?, ?, '{}', '{}', '[]', ?, 2, ?)
                """,
                (f"run_{tenant_id}_{i}", routine_id, workspace_id, tenant_id, status, now),
            )
        app_conn.execute(
            """
            INSERT INTO usage_record (id, workspace_id, tenant_id, provider_slug, model, input_tokens, output_tokens, cost_usd, status, request_json, response_json, created_at)
            VALUES (?, ?, ?, 'openai', 'gpt-4o-mini', 100, 50, 0.12, 'succeeded', '{}', '{}', ?)
            """,
            (f"usage_{tenant_id}", workspace_id, tenant_id, now),
        )
        app_conn.commit()
    finally:
        app_conn.close()

    fnd_conn = _foundation_conn(client)
    try:
        owner_id = fnd_conn.execute(
            "SELECT id FROM fnd_users WHERE tenant_id = ? AND email LIKE 'owner@%'",
            (tenant_id,),
        ).fetchone()["id"]
        session_id = f"fnds_{tenant_id}"
        now = datetime.now(timezone.utc).isoformat()
        fnd_conn.execute(
            """
            INSERT INTO fnd_sessions (id, tenant_id, user_id, stage, created_at, expires_at, last_seen_at)
            VALUES (?, ?, ?, 'full', ?, ?, ?)
            """,
            (session_id, tenant_id, owner_id, now, now, now),
        )
        fnd_conn.commit()
    finally:
        fnd_conn.close()

    return workspace_id, routine_id


def test_owner_mirror_health_dashboard(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "acme-health", "owner@acme-health.test")
    _seed_health_data(client, tenant_id)

    resp = client.get(f"/api/tenants/{tenant_id}/health", headers=_auth_headers(tenant_id, "owner"))
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["tenant_id"] == tenant_id
    assert data["plan"] == "starter"
    assert data["limits"]["max_monthly_budget_usd"] == 50.0
    assert data["runs_30d"] == 3
    assert data["successful_runs_30d"] == 2
    assert data["failed_runs_30d"] == 1
    assert data["error_rate_pct"] == 33.33
    assert data["runs_7d"] == 3
    assert data["cost_usd_30d"] == 0.12
    assert data["budget_remaining_usd"] == 49.88
    assert data["workspaces"] == 1
    assert data["users"] == 1
    assert data["last_owner_login"] is not None
    assert data["flags"]["drafts_pending_approval"] == 0
    assert data["invoices_open"] == 0


def test_platform_admin_health_dashboard(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "acme-admin-health", "owner@acme-admin-health.test")
    _seed_health_data(client, tenant_id)

    resp = client.get(
        f"/api/admin/tenants/{tenant_id}/health",
        headers=_auth_headers(tenant_id, "platform_admin", "platform_admin"),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["tenant_id"] == tenant_id
    assert data["runs_30d"] == 3
    assert data["cost_usd_30d"] == 0.12


def test_cross_tenant_health_isolation(client: TestClient) -> None:
    tenant_a = _bootstrap_tenant(client, "acme-health-a", "owner@a.test")
    tenant_b = _bootstrap_tenant(client, "acme-health-b", "owner@b.test")

    resp = client.get(
        f"/api/tenants/{tenant_a}/health",
        headers=_auth_headers(tenant_b, "owner"),
    )
    assert resp.status_code == 403, resp.text
