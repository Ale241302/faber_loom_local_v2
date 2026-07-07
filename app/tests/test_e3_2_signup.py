"""E3-2 — Public tenant signup and platform_admin lifecycle."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

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
    assert data["status"] == "pending_verification"
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
        assert user["status"] == "pending_verification"
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


def _signup_payload(n: int) -> dict[str, Any]:
    return {
        "company_name": f"Corp {n}",
        "slug": f"corp-{n}",
        "owner_email": f"owner{n}@corp.test",
        "owner_password": "secure1234",
        "plan": "starter",
    }


def test_public_signup_rate_limit(client: TestClient) -> None:
    """After 5 signups from the same IP the 6th is rejected with 429."""

    with patch("app.src.auth.secrets.token_urlsafe", return_value="dummy-token"):
        for i in range(5):
            r = client.post("/api/public/signup", json=_signup_payload(i))
            assert r.status_code == 200, r.text

        r = client.post("/api/public/signup", json=_signup_payload(5))
        assert r.status_code == 429, r.text


def test_email_verification_activates_user(client: TestClient) -> None:
    """A valid verification token marks the owner email as verified."""

    with patch("app.src.auth.secrets.token_urlsafe", return_value="known-token-12345"):
        r = client.post(
            "/api/public/signup",
            json={
                "company_name": "Verify Me",
                "slug": "verify-me",
                "owner_email": "owner@verify.test",
                "owner_password": "secure1234",
                "plan": "starter",
            },
        )
        assert r.status_code == 200, r.text

    r = client.get("/api/public/signup/verify?token=known-token-12345")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["verified"] is True

    conn = _foundation_conn(client)
    try:
        user = conn.execute(
            "SELECT * FROM fnd_users WHERE email = ?", ("owner@verify.test",)
        ).fetchone()
        assert user is not None
        assert user["email_verified"] == 1
        assert user["email_verified_at"] is not None
        assert user["status"] == "pending_approval"
    finally:
        conn.close()


def test_resend_verification_rate_limit(client: TestClient) -> None:
    """Resend endpoint is rate limited after 3 attempts per IP."""

    with patch("app.src.auth.secrets.token_urlsafe", return_value="dummy-token"):
        r = client.post(
            "/api/public/signup",
            json={
                "company_name": "Resend Corp",
                "slug": "resend-corp",
                "owner_email": "owner@resend.test",
                "owner_password": "secure1234",
                "plan": "starter",
            },
        )
        assert r.status_code == 200, r.text

    for _ in range(3):
        r = client.post(
            "/api/public/signup/resend-verification",
            json={"email": "owner@resend.test"},
        )
        assert r.status_code == 200, r.text

    r = client.post(
        "/api/public/signup/resend-verification",
        json={"email": "owner@resend.test"},
    )
    assert r.status_code == 429, r.text


def test_verify_rejects_unknown_token(client: TestClient) -> None:
    r = client.get("/api/public/signup/verify?token=not-a-real-token")
    assert r.status_code == 400, r.text
