"""E3-3 — REST endpoints for tenant identity and key broker."""

from __future__ import annotations

import hashlib
import os
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.auth import create_access_token
from app.src.foundation.core import hash_password, new_id, seed_system_roles, utcnow
from app.src.main import create_app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated app with JWT auth and fresh Foundation/app DBs."""

    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        '{"owner@tenant.test":"pass","viewer@tenant.test":"pass"}',
    )
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)
    with TestClient(create_app()) as test_client:
        yield test_client


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _create_tenant_with_owner(client: TestClient, slug: str) -> tuple[str, str]:
    conn = _foundation_conn(client)
    try:
        tenant_id = new_id("tnt")
        user_id = new_id("usr")
        conn.execute(
            """
            INSERT INTO fnd_tenants (id, name, slug, status, plan, created_at)
            VALUES (?, ?, ?, 'active', 'starter', ?)
            """,
            (tenant_id, f"Tenant {slug}", slug, utcnow()),
        )
        seed_system_roles(conn, tenant_id)
        conn.execute(
            """
            INSERT INTO fnd_users (id, tenant_id, email, display_name, password_hash, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
            """,
            (user_id, tenant_id, "owner@tenant.test", "owner", hash_password("pass"), utcnow()),
        )
        owner_role = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = 'owner'",
            (tenant_id,),
        ).fetchone()
        conn.execute(
            """
            INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (tenant_id, user_id, owner_role["id"], user_id, utcnow()),
        )
        conn.commit()
        return tenant_id, user_id
    finally:
        conn.close()


def _token(email: str, tenant_id: str, user_id: str, role: str) -> str:
    return create_access_token(email, tenant_id=tenant_id, user_id=user_id, role=role)


def _confirmation_token(resource_id: str) -> str:
    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def _add_owner(tenant_id: str, email: str) -> str:
    conn = sqlite3.connect(os.environ["FABERLOOM_FOUNDATION_DB"])
    conn.row_factory = sqlite3.Row
    try:
        user_id = new_id("usr")
        conn.execute(
            """
            INSERT INTO fnd_users (id, tenant_id, email, display_name, password_hash, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
            """,
            (user_id, tenant_id, email, email.split("@")[0], hash_password("pass"), utcnow()),
        )
        owner_role = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = 'owner'",
            (tenant_id,),
        ).fetchone()
        conn.execute(
            """
            INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (tenant_id, user_id, owner_role["id"], user_id, utcnow()),
        )
        conn.commit()
        return user_id
    finally:
        conn.close()


def test_identity_crud(client: TestClient) -> None:
    tenant_id, owner_a = _create_tenant_with_owner(client, "identity-crud")
    owner_b = _add_owner(tenant_id, "owner-b@tenant.test")

    headers_a = {"Authorization": f"Bearer {_token('owner@tenant.test', tenant_id, owner_a, 'owner')}"}
    headers_b = {"Authorization": f"Bearer {_token('owner-b@tenant.test', tenant_id, owner_b, 'owner')}"}

    r = client.post(
        f"/api/tenants/{tenant_id}/identity",
        json={"name": "Acme Inc", "slug": "acme-inc", "tax_id": "123", "jurisdiction": "US"},
        headers=headers_a,
    )
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Acme Inc"
    assert data["version"] == 1

    r = client.get(f"/api/tenants/{tenant_id}/identity", headers=headers_a)
    assert r.status_code == 200, r.text
    assert r.json()["name"] == "Acme Inc"

    r = client.post(
        f"/api/tenants/{tenant_id}/identity/update",
        json={
            "name": "Acme Corp",
            "confirmation_token": _confirmation_token(tenant_id),
        },
        headers=headers_b,
    )
    assert r.status_code == 200, r.text
    assert r.json()["version"] == 2
    assert r.json()["name"] == "Acme Corp"


def test_key_policy_crud(client: TestClient) -> None:
    tenant_id, user_id = _create_tenant_with_owner(client, "key-policy-crud")
    headers = {"Authorization": f"Bearer {_token('owner@tenant.test', tenant_id, user_id, 'owner')}"}

    r = client.get(f"/api/tenants/{tenant_id}/key-policy/space-1", headers=headers)
    assert r.status_code == 200, r.text
    assert r.json()["level"] == "closed"

    r = client.put(
        f"/api/tenants/{tenant_id}/key-policy/space-1",
        json={
            "level": "content",
            "confirmation_token": _confirmation_token(f"{tenant_id}:space-1"),
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["level"] == "content"

    r = client.post(
        f"/api/tenants/{tenant_id}/key-policy/space-1/access",
        json={
            "requested_level": "content",
            "confirmation_token": "dummy-token",
        },
        headers=headers,
    )
    assert r.status_code == 200, r.text
    assert r.json()["granted_level"] == "content"


def test_identity_endpoints_are_isolated(client: TestClient) -> None:
    tenant_a, user_a = _create_tenant_with_owner(client, "identity-a")
    tenant_b, user_b = _create_tenant_with_owner(client, "identity-b")

    headers_a = {"Authorization": f"Bearer {_token('owner@tenant.test', tenant_a, user_a, 'owner')}"}
    headers_b = {"Authorization": f"Bearer {_token('owner@tenant.test', tenant_b, user_b, 'owner')}"}

    client.post(
        f"/api/tenants/{tenant_a}/identity",
        json={"name": "Tenant A", "slug": "tenant-a"},
        headers=headers_a,
    )

    r = client.get(f"/api/tenants/{tenant_b}/identity", headers=headers_b)
    assert r.status_code == 404, r.text
