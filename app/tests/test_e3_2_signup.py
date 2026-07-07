"""E3-2 — Public tenant signup and platform_admin lifecycle."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.main import create_app


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Create an isolated app with a fresh Foundation DB in a temp directory."""

    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("FABERLOOM_CONFIG_DIR", tmpdir)
        monkeypatch.setenv("FABERLOOM_AUTH_DISABLED", "1")
        monkeypatch.delenv("FABERLOOM_USERS", raising=False)
        # Foundation DB lives inside CONFIG_DIR.
        db_path = Path(tmpdir) / "foundation.sqlite3"
        monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(db_path))
        with TestClient(create_app()) as test_client:
            yield test_client


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    # The app stores the path in env; re-open for inspection.
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def test_public_signup_creates_pending_tenant(client: TestClient) -> None:
    response = client.post(
        "/api/public/signup",
        json={
            "company_name": "Acme Corp",
            "slug": "acme-corp",
            "owner_email": "owner@acme.test",
            "owner_password": "secure1234",
            "plan": "growth",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending_approval"
    assert "tenant_id" in data

    conn = _foundation_conn(client)
    try:
        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE slug = ?", ("acme-corp",)
        ).fetchone()
        assert tenant is not None
        assert tenant["status"] == "pending_approval"
        assert tenant["plan"] == "growth"

        user = conn.execute(
            "SELECT * FROM fnd_users WHERE tenant_id = ? AND email = ?",
            (tenant["id"], "owner@acme.test"),
        ).fetchone()
        assert user is not None
        assert user["password_hash"].startswith("pbkdf2$")

        role = conn.execute(
            """SELECT r.name FROM fnd_user_roles ur
               JOIN fnd_roles r ON r.id = ur.role_id
               WHERE ur.user_id = ?""",
            (user["id"],),
        ).fetchone()
        assert role is not None
        assert role["name"] == "owner"
    finally:
        conn.close()


def test_public_signup_rejects_duplicate_slug(client: TestClient) -> None:
    payload = {
        "company_name": "Acme Corp",
        "slug": "acme-corp",
        "owner_email": "owner@acme.test",
        "owner_password": "secure1234",
    }
    assert client.post("/api/public/signup", json=payload).status_code == 200
    response = client.post("/api/public/signup", json=payload)
    assert response.status_code == 409


def test_public_signup_rejects_invalid_email(client: TestClient) -> None:
    response = client.post(
        "/api/public/signup",
        json={
            "company_name": "Acme Corp",
            "slug": "acme-corp",
            "owner_email": "not-an-email",
            "owner_password": "secure1234",
        },
    )
    assert response.status_code == 400


def test_public_signup_rejects_invalid_plan(client: TestClient) -> None:
    response = client.post(
        "/api/public/signup",
        json={
            "company_name": "Acme Corp",
            "slug": "acme-corp",
            "owner_email": "owner@acme.test",
            "owner_password": "secure1234",
            "plan": "luxury",
        },
    )
    assert response.status_code == 400
