"""E3-2 — Plan limits and admin plan management."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.auth import create_access_token
from app.src.foundation.core import new_id, seed_system_roles, utcnow
from app.src.main import create_app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated app with fresh Foundation and app DBs, auth disabled."""

    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_AUTH_DISABLED", "1")
    monkeypatch.delenv("FABERLOOM_USERS", raising=False)
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture()
def auth_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated app with JWT auth enabled for platform_admin tests."""

    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        '{"admin@platform.test":"admin-pass"}',
    )
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)
    with TestClient(create_app()) as test_client:
        yield test_client


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _create_tenant(client: TestClient, slug: str, plan: str) -> str:
    """Create a Foundation tenant and return its id."""

    conn = _foundation_conn(client)
    try:
        tenant_id = new_id("tnt")
        conn.execute(
            """
            INSERT INTO fnd_tenants
            (id, name, slug, status, plan, created_at)
            VALUES (?, ?, ?, 'active', ?, ?)
            """,
            (tenant_id, f"Tenant {slug}", slug, plan, utcnow()),
        )
        seed_system_roles(conn, tenant_id)
        user_id = new_id("usr")
        conn.execute(
            """
            INSERT INTO fnd_users
            (id, tenant_id, email, display_name, password_hash, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
            """,
            (user_id, tenant_id, f"owner@{slug}.test", "owner", "", utcnow()),
        )
        role_row = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = 'owner'",
            (tenant_id,),
        ).fetchone()
        conn.execute(
            """
            INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (tenant_id, user_id, role_row["id"], user_id, utcnow()),
        )
        conn.commit()
        return tenant_id
    finally:
        conn.close()


def test_starter_plan_workspace_limit(client: TestClient) -> None:
    tenant_id = _create_tenant(client, "starter-limit", "starter")
    headers = {"x-tenant-id": tenant_id, "x-actor-role": "owner"}

    for i in range(2):
        r = client.post(
            "/api/workspaces",
            json={"name": f"WS {i}"},
            headers=headers,
        )
        assert r.status_code == 201, r.text

    r = client.post(
        "/api/workspaces",
        json={"name": "WS over limit"},
        headers=headers,
    )
    assert r.status_code == 422, r.text


def test_admin_can_change_tenant_plan(auth_client: TestClient) -> None:
    """Platform admin PATCH /plan is reflected in Foundation."""

    admin_tenant = _create_tenant(auth_client, "platform-admin", "enterprise")
    conn = _foundation_conn(auth_client)
    try:
        admin_user_id = new_id("usr")
        conn.execute(
            """
            INSERT INTO fnd_users
            (id, tenant_id, email, display_name, password_hash, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
            """,
            (admin_user_id, admin_tenant, "admin@platform.test", "admin", "", utcnow()),
        )
        role_row = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = 'platform_admin'",
            (admin_tenant,),
        ).fetchone()
        assert role_row is not None
        conn.execute(
            """
            INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (admin_tenant, admin_user_id, role_row["id"], admin_user_id, utcnow()),
        )
        conn.commit()
    finally:
        conn.close()

    target_tenant = _create_tenant(auth_client, "target-plan", "starter")

    token = create_access_token(
        "admin@platform.test",
        tenant_id=admin_tenant,
        user_id=admin_user_id,
        role="platform_admin",
    )

    r = auth_client.patch(
        f"/api/admin/tenants/{target_tenant}/plan",
        json={"plan": "growth"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["plan"] == "growth"

    conn = _foundation_conn(auth_client)
    try:
        row = conn.execute(
            "SELECT plan FROM fnd_tenants WHERE id = ?", (target_tenant,)
        ).fetchone()
        assert row["plan"] == "growth"
    finally:
        conn.close()
