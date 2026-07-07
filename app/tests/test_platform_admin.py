"""E3-2 — platform_admin tenant lifecycle endpoints."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated app with fresh Foundation and app DBs plus two legacy users."""

    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        '{"admin@platform.test":"admin-pass","owner@acme.test":"owner-pass"}',
    )
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)

    from app.src.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _create_foundation_user(
    conn: sqlite3.Connection,
    tenant_id: str,
    email: str,
    role: str,
) -> str:
    """Create a Foundation user and assign a system role; return user id."""

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


def _bootstrap_platform_admin_tenant(client: TestClient) -> str:
    """Create an active Foundation tenant with a platform_admin user."""

    from app.src.foundation.core import new_id, utcnow

    conn = _foundation_conn(client)
    try:
        tenant_id = new_id("tnt")
        conn.execute(
            """
            INSERT INTO fnd_tenants
            (id, name, slug, status, plan, created_at, activated_at)
            VALUES (?, ?, ?, 'active', 'enterprise', ?, ?)
            """,
            (tenant_id, "Platform Admin Tenant", "platform-admin", utcnow(), utcnow()),
        )
        _create_foundation_user(conn, tenant_id, "admin@platform.test", "platform_admin")
        conn.commit()
        return tenant_id
    finally:
        conn.close()


def _bootstrap_owner_tenant(client: TestClient) -> str:
    """Create an active Foundation tenant with a regular owner user."""

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
            (tenant_id, "ACME Tenant", "acme", utcnow(), utcnow()),
        )
        _create_foundation_user(conn, tenant_id, "owner@acme.test", "owner")
        conn.commit()
        return tenant_id
    finally:
        conn.close()


def _login(client: TestClient, email: str, password: str) -> None:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text


def _signup_pending_tenant(client: TestClient, slug: str) -> str:
    resp = client.post(
        "/api/public/signup",
        json={
            "company_name": f"Company {slug}",
            "slug": slug,
            "owner_email": f"owner@{slug}.test",
            "owner_password": "secure1234",
            "plan": "starter",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["tenant_id"]


def test_admin_can_list_tenants(client: TestClient) -> None:
    _bootstrap_platform_admin_tenant(client)
    pending_id = _signup_pending_tenant(client, "list-pending")
    _login(client, "admin@platform.test", "admin-pass")

    resp = client.get("/api/admin/tenants")
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert isinstance(data, list)
    by_id = {t["id"]: t for t in data}
    assert pending_id in by_id
    assert by_id[pending_id]["status"] == "pending"
    assert by_id[pending_id]["raw_status"] == "pending_approval"


def test_admin_can_approve_pending_tenant(client: TestClient) -> None:
    _bootstrap_platform_admin_tenant(client)
    pending_id = _signup_pending_tenant(client, "approve-me")
    _login(client, "admin@platform.test", "admin-pass")

    resp = client.post(f"/api/admin/tenants/{pending_id}/approve", json={"reason": "Looks legit"})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "active"
    assert data["raw_status"] == "active"
    assert data["approved_by"]

    conn = _foundation_conn(client)
    try:
        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE id = ?", (pending_id,)
        ).fetchone()
        assert tenant["status"] == "active"
        assert tenant["approved_by"]
        assert tenant["activated_at"]
        audit = conn.execute(
            "SELECT * FROM fnd_audit_log WHERE action = 'tenant.approved' AND resource_id = ?",
            (pending_id,),
        ).fetchone()
        assert audit is not None
        assert "Looks legit" in audit["payload_json"]
    finally:
        conn.close()


def test_admin_can_suspend_active_tenant(client: TestClient) -> None:
    _bootstrap_platform_admin_tenant(client)
    pending_id = _signup_pending_tenant(client, "suspend-me")
    _login(client, "admin@platform.test", "admin-pass")

    client.post(f"/api/admin/tenants/{pending_id}/approve")

    resp = client.post(
        f"/api/admin/tenants/{pending_id}/suspend",
        json={"reason": "Billing dispute"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "suspended"
    assert data["raw_status"] == "suspended"
    assert data["suspension_reason"] == "Billing dispute"

    conn = _foundation_conn(client)
    try:
        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE id = ?", (pending_id,)
        ).fetchone()
        assert tenant["status"] == "suspended"
        assert tenant["suspended_by"]
        audit = conn.execute(
            "SELECT * FROM fnd_audit_log WHERE action = 'tenant.suspended' AND resource_id = ?",
            (pending_id,),
        ).fetchone()
        assert audit is not None
    finally:
        conn.close()


def test_admin_metrics(client: TestClient) -> None:
    _bootstrap_platform_admin_tenant(client)
    _bootstrap_owner_tenant(client)
    _signup_pending_tenant(client, "metrics-pending")
    _login(client, "admin@platform.test", "admin-pass")

    for path in ("/api/admin/metrics", "/api/admin/tenants/metrics"):
        resp = client.get(path)
        assert resp.status_code == 200, f"{path}: {resp.text}"
        data = resp.json()
        assert data["total_tenants"] >= 3
        assert "by_status" in data
        assert data["by_status"]["pending"] >= 1
        assert data["by_status"]["active"] >= 2
        assert data["total_users"] >= 3
        assert data["total_workspaces"] >= 0
        assert "recent_signups_30d" in data
        assert "total_cost_usd" in data


def test_non_admin_is_forbidden(client: TestClient) -> None:
    _bootstrap_owner_tenant(client)
    _login(client, "owner@acme.test", "owner-pass")

    resp = client.get("/api/admin/tenants")
    assert resp.status_code == 403, resp.text

    resp = client.get("/api/admin/metrics")
    assert resp.status_code == 403, resp.text


def test_unauthenticated_is_rejected(client: TestClient) -> None:
    _bootstrap_platform_admin_tenant(client)

    resp = client.get("/api/admin/tenants")
    assert resp.status_code == 401, resp.text


def test_approve_non_pending_fails(client: TestClient) -> None:
    _bootstrap_platform_admin_tenant(client)
    pending_id = _signup_pending_tenant(client, "bad-approve")
    _login(client, "admin@platform.test", "admin-pass")

    client.post(f"/api/admin/tenants/{pending_id}/approve")

    resp = client.post(f"/api/admin/tenants/{pending_id}/approve")
    assert resp.status_code == 409, resp.text


def test_suspend_non_active_fails(client: TestClient) -> None:
    _bootstrap_platform_admin_tenant(client)
    pending_id = _signup_pending_tenant(client, "bad-suspend")
    _login(client, "admin@platform.test", "admin-pass")

    resp = client.post(f"/api/admin/tenants/{pending_id}/suspend")
    assert resp.status_code == 409, resp.text


def test_approve_unknown_tenant_404(client: TestClient) -> None:
    _bootstrap_platform_admin_tenant(client)
    _login(client, "admin@platform.test", "admin-pass")

    resp = client.post("/api/admin/tenants/tnt_does_not_exist/approve")
    assert resp.status_code == 404, resp.text
