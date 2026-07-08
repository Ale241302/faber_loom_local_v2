"""E3-5 — Routing presets: CRUD, isolation, default templates, routine resolution."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
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
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        '{"admin@platform.test":"admin-pass","owner@acme.test":"owner-pass","owner@other.test":"owner-pass"}',
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


def _bootstrap_tenant(client: TestClient, email: str, role: str, slug: str) -> str:
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
        _create_foundation_user(conn, tenant_id, email, role)
        conn.commit()
        return tenant_id
    finally:
        conn.close()


def _bootstrap_platform_admin_tenant(client: TestClient) -> str:
    return _bootstrap_tenant(client, "admin@platform.test", "platform_admin", "platform-admin")


def _bootstrap_owner_tenant(client: TestClient, slug: str, email: str) -> str:
    return _bootstrap_tenant(client, email, "owner", slug)


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


def _confirmation_token(resource_id: str) -> str:
    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def _approve_pending_tenant(client: TestClient, tenant_id: str) -> dict[str, Any]:
    _bootstrap_platform_admin_tenant(client)
    _login(client, "admin@platform.test", "admin-pass")
    resp = client.post(
        f"/api/admin/tenants/{tenant_id}/approve",
        json={"reason": "E3-5 test", "confirmation_token": _confirmation_token(tenant_id)},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def _first_workspace_id(client: TestClient) -> str:
    resp = client.get("/api/workspaces")
    assert resp.status_code == 200, resp.text
    workspaces = resp.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def test_create_and_list_preset(client: TestClient) -> None:
    tenant_id = _bootstrap_owner_tenant(client, "create-list", "owner@acme.test")
    _login(client, "owner@acme.test", "owner-pass")

    resp = client.post(
        f"/api/tenants/{tenant_id}/presets",
        json={
            "preset_id": "mi-preset",
            "name": "Mi preset",
            "description": "Preset de prueba",
            "envelope": {"jurisdictions": ["US"], "providers_allow": ["anthropic"]},
            "curve": {"mode": "eco", "borderline_policy": "cheap"},
            "task_overrides": {"cotizacion": {"default": "claude-3-5-sonnet"}},
            "caps": {"monthly_budget_usd": 25},
            "escalation": {"user_boost_button": False},
        },
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["tenant_id"] == tenant_id
    assert data["preset_id"] == "mi-preset"
    assert data["name"] == "Mi preset"
    assert data["version"] == 1
    assert data["curve"]["mode"] == "eco"

    resp = client.get(f"/api/tenants/{tenant_id}/presets")
    assert resp.status_code == 200, resp.text
    presets = resp.json()["presets"]
    assert any(p["preset_id"] == "mi-preset" for p in presets)


def test_get_and_update_preset(client: TestClient) -> None:
    tenant_id = _bootstrap_owner_tenant(client, "get-update", "owner@acme.test")
    _login(client, "owner@acme.test", "owner-pass")

    client.post(
        f"/api/tenants/{tenant_id}/presets",
        json={"preset_id": "editable", "name": "Editable"},
    )

    resp = client.get(f"/api/tenants/{tenant_id}/presets/editable")
    assert resp.status_code == 200, resp.text
    assert resp.json()["name"] == "Editable"

    resp = client.patch(
        f"/api/tenants/{tenant_id}/presets/editable",
        json={"name": "Renombrado", "curve": {"mode": "sport", "borderline_policy": "premium"}},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["name"] == "Renombrado"
    assert data["version"] == 2


def test_delete_preset(client: TestClient) -> None:
    tenant_id = _bootstrap_owner_tenant(client, "delete", "owner@acme.test")
    _login(client, "owner@acme.test", "owner-pass")

    client.post(
        f"/api/tenants/{tenant_id}/presets",
        json={"preset_id": "borrable", "name": "Borrable"},
    )
    resp = client.delete(f"/api/tenants/{tenant_id}/presets/borrable")
    assert resp.status_code == 204, resp.text

    resp = client.get(f"/api/tenants/{tenant_id}/presets/borrable")
    assert resp.status_code == 404, resp.text


def test_cross_tenant_isolation(client: TestClient) -> None:
    tenant_a = _bootstrap_owner_tenant(client, "tenant-a", "owner@acme.test")
    tenant_b = _bootstrap_owner_tenant(client, "tenant-b", "owner@other.test")

    _login(client, "owner@acme.test", "owner-pass")
    resp = client.post(
        f"/api/tenants/{tenant_a}/presets",
        json={"preset_id": "privado", "name": "Privado"},
    )
    assert resp.status_code == 201, resp.text

    _login(client, "owner@other.test", "owner-pass")
    resp = client.get(f"/api/tenants/{tenant_b}/presets")
    assert resp.status_code == 200, resp.text
    presets = resp.json()["presets"]
    assert not any(p["preset_id"] == "privado" for p in presets)

    resp = client.get(f"/api/tenants/{tenant_b}/presets/privado")
    assert resp.status_code == 404, resp.text


def _activate_foundation_user(email: str) -> None:
    conn = sqlite3.connect(os.environ["FABERLOOM_FOUNDATION_DB"])
    try:
        conn.execute(
            "UPDATE fnd_users SET status = 'active', email_verified = 1 WHERE email = ?",
            (email,),
        )
        conn.commit()
    finally:
        conn.close()


def test_default_templates_seeded_on_approval(client: TestClient) -> None:
    resp = client.post(
        "/api/public/signup",
        json={
            "company_name": "Templates Co",
            "slug": "templates",
            "owner_email": "owner@acme.test",
            "owner_password": "secure1234",
            "plan": "starter",
        },
    )
    assert resp.status_code == 200, resp.text
    pending_id = resp.json()["tenant_id"]
    _approve_pending_tenant(client, pending_id)

    _activate_foundation_user("owner@acme.test")
    _login(client, "owner@acme.test", "owner-pass")
    resp = client.get(f"/api/tenants/{pending_id}/presets")
    assert resp.status_code == 200, resp.text
    presets = resp.json()["presets"]
    ids = {p["preset_id"] for p in presets}
    assert ids >= {"conservador", "balanceado", "ahorro", "sport"}
    for p in presets:
        assert p["is_template"] is True


def test_routine_uses_preset_slug(client: TestClient) -> None:
    _bootstrap_owner_tenant(client, "routine-preset", "owner@acme.test")
    _login(client, "owner@acme.test", "owner-pass")

    # Seed a premium preset that resolves to claude-3-5-sonnet.
    resp = client.get("/api/me")
    assert resp.status_code == 200, resp.text
    tenant_id = resp.json()["tenant_id"]
    client.post(
        f"/api/tenants/{tenant_id}/presets",
        json={
            "preset_id": "premium",
            "name": "Premium",
            "envelope": {"providers_allow": ["anthropic"]},
            "curve": {"mode": "sport", "borderline_policy": "premium"},
        },
    )

    resp = client.post("/api/workspaces", json={"name": "Routine Preset Test"})
    assert resp.status_code == 201, resp.text
    workspace_id = resp.json()["id"]
    skill_md = "---\nname: cotizador-premium\npersona: Eres un asistente.\ntools: []\n---\nResponde."
    resp = client.post(
        f"/api/workspaces/{workspace_id}/routines",
        json={
            "name": "cotizador-premium",
            "skill_md": skill_md,
            "preset_id": "@preset/premium",
            "category": "skill",
            "is_active": 1,
        },
    )
    assert resp.status_code == 201, resp.text
    routine = resp.json()
    assert routine["preset_id"] == "@preset/premium"

    # Resolution endpoint should map the preset to a provider/model.
    resp = client.get(f"/api/tenants/{tenant_id}/presets/premium/resolve")
    assert resp.status_code == 200, resp.text
    resolved = resp.json()
    assert resolved["provider_slug"] == "anthropic"
    assert resolved["model"] == "claude-3-5-sonnet"


def test_routine_legacy_preset_still_works(client: TestClient) -> None:
    _bootstrap_owner_tenant(client, "legacy-preset", "owner@acme.test")
    _login(client, "owner@acme.test", "owner-pass")

    resp = client.post("/api/workspaces", json={"name": "Legacy Preset Test"})
    assert resp.status_code == 201, resp.text
    workspace_id = resp.json()["id"]
    skill_md = "---\nname: cotizador-legacy\npersona: Eres un asistente.\ntools: []\n---\nResponde."
    resp = client.post(
        f"/api/workspaces/{workspace_id}/routines",
        json={
            "name": "cotizador-legacy",
            "skill_md": skill_md,
            "preset_id": "anthropic:claude-3-5-sonnet",
            "category": "skill",
            "is_active": 1,
        },
    )
    assert resp.status_code == 201, resp.text
    routine = resp.json()
    assert routine["preset_id"] == "anthropic:claude-3-5-sonnet"
