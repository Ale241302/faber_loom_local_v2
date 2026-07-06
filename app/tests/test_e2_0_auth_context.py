"""E2-0 — Tests de unificación de identidad entre JWT legacy y Foundation.

Verifica que el API principal resuelva tenant_id, user_id y role reales desde
Foundation, y que Context/AuditWriter registren el actor autenticado.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

OWNER = {"email": "owner@acme.test", "display_name": "Owner", "password": "s3cret-pass"}


def _make_app():
    from app.src.main import create_app

    return create_app()


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "fnd.sqlite3"))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    # Legacy user that matches the Foundation owner email.
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        f'{{"{OWNER["email"]}":"{OWNER["password"]}"}}',
    )
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)
    with TestClient(_make_app()) as test_client:
        yield test_client


def _bootstrap(client: TestClient) -> dict:
    """Bootstrap Foundation tenant + owner and activate."""
    resp = client.post(
        "/api/foundation/bootstrap/tenant", json={"name": "ACME S.A.", "slug": "acme"}
    )
    assert resp.status_code == 201, resp.text
    resp = client.post("/api/foundation/bootstrap/owner", json=OWNER)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    session = data["session"]
    user = data["user"]
    resp = client.post("/api/foundation/bootstrap/activate", headers={"X-Fnd-Session": session})
    assert resp.status_code == 200, resp.text
    return user


def _login_legacy(client: TestClient) -> None:
    """Login via legacy /api/auth/login (matches FABERLOOM_USERS)."""
    resp = client.post(
        "/api/auth/login", json={"email": OWNER["email"], "password": OWNER["password"]}
    )
    assert resp.status_code == 200, resp.text


def test_login_creates_access_token_with_foundation_claims(client: TestClient):
    user = _bootstrap(client)
    _login_legacy(client)

    # Cookie should be set; decode it via a workspace-scoped endpoint.
    resp = client.get("/api/workspaces")
    assert resp.status_code == 200, resp.text

    # Inspect request state indirectly: the cookie was created at login.
    # We cannot read HttpOnly cookie from JS, but we can verify the token payload
    # by decoding the cookie manually if exposed. FastAPI TestClient exposes cookies.
    token = client.cookies.get("faberloom_at")
    assert token is not None

    import jwt

    payload = jwt.decode(token, "test-secret-key-at-least-32-bytes-long-xyz", algorithms=["HS256"])
    assert payload["sub"] == OWNER["email"]
    assert payload["tenant_id"] == user["tenant_id"]
    assert payload["user_id"] == user["id"]
    assert payload["role"] == "owner"


def test_context_resolves_foundation_identity(client: TestClient):
    user = _bootstrap(client)
    _login_legacy(client)

    # Create a workspace; it must be scoped to the Foundation tenant.
    resp = client.post("/api/workspaces", json={"name": "E2-0 Test", "seal_passphrase": ""})
    assert resp.status_code == 201, resp.text
    workspace = resp.json()
    assert workspace["tenant_id"] == user["tenant_id"]

    # Workspace is scoped to the Foundation tenant, proving Context resolved identity.
    assert workspace["tenant_id"] == user["tenant_id"]


def test_approved_by_taken_from_context(client: TestClient):
    user = _bootstrap(client)
    _login_legacy(client)

    # Create workspace and a routine.
    resp = client.post("/api/workspaces", json={"name": "E2-0 Routine", "seal_passphrase": ""})
    assert resp.status_code == 201, resp.text
    workspace = resp.json()

    routine_payload = {
        "name": "test-skill",
        "category": "skill",
        "skill_md": "---\nname: test-skill\n---\n",
        "is_active": True,
    }
    resp = client.post(f"/api/workspaces/{workspace['id']}/routines", json=routine_payload)
    assert resp.status_code == 201, resp.text
    routine = resp.json()
    assert routine["approved_by"] is None

    # Approve routine without sending approved_by query param.
    resp = client.post(f"/api/workspaces/{workspace['id']}/routines/{routine['id']}/approve")
    assert resp.status_code == 200, resp.text
    routine = resp.json()
    assert routine["approved_by"] == user["id"]

    # Audit log should reflect the Foundation actor.
    db_path = os.environ["FABERLOOM_DB_PATH"]
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT actor_id, user_id, tenant_id, actor_role_at_decision FROM audit_log WHERE action = 'routine.approved' ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        assert row is not None
        assert row["actor_id"] == user["id"]
        assert row["user_id"] == user["id"]
        assert row["tenant_id"] == user["tenant_id"]
        assert row["actor_role_at_decision"] == "owner"
    finally:
        conn.close()
