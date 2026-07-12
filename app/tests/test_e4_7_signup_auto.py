"""E4-7 — Public signup with gated auto-approval."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.src.auth import create_access_token
from app.src.main import create_app


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Create an isolated app with a fresh Foundation DB in a temp directory."""

    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setenv("FABERLOOM_CONFIG_DIR", tmpdir)
        monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)
        # Keep auth enabled so JWT tokens resolve to Foundation users.
        monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-with-enough-bytes-32")
        monkeypatch.setenv("FABERLOOM_USERS", '{"admin@platform.test":"secret"}')
        monkeypatch.setenv("FABERLOOM_SIGNUP_APPROVAL", "auto")
        monkeypatch.setenv("FABERLOOM_SIGNUP_DAILY_LIMIT", "100")
        db_path = Path(tmpdir) / "foundation.sqlite3"
        monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(db_path))
        with TestClient(create_app()) as test_client:
            yield test_client


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _auth_headers(email: str, tenant_id: str, user_id: str, role: str = "owner") -> dict[str, str]:
    token = create_access_token(email, tenant_id=tenant_id, user_id=user_id, role=role)
    return {"Authorization": f"Bearer {token}"}


def _signup_payload(n: int) -> dict[str, Any]:
    return {
        "company_name": f"Auto Corp {n}",
        "slug": f"auto-corp-{n}",
        "owner_email": f"owner{n}@autocorp.test",
        "owner_password": "secure1234",
        "plan": "starter",
    }


def test_signup_manual_mode_unchanged(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """In manual mode verify leaves the user pending_approval."""

    monkeypatch.setenv("FABERLOOM_SIGNUP_APPROVAL", "manual")

    with patch("app.src.auth.secrets.token_urlsafe", return_value="manual-token-12345"):
        r = client.post("/api/public/signup", json=_signup_payload(0))
        assert r.status_code == 200, r.text

    r = client.get("/api/public/signup/verify?token=manual-token-12345")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["user_status"] == "pending_approval"
    assert data["tenant_status"] == "pending_approval"

    conn = _foundation_conn(client)
    try:
        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE slug = ?", ("auto-corp-0",)
        ).fetchone()
        assert tenant["status"] == "pending_approval"
    finally:
        conn.close()


def test_signup_auto_approves_tenant_and_bootstraps(client: TestClient) -> None:
    """Auto mode: verify activates tenant, creates workspaces and identity."""

    with patch("app.src.auth.secrets.token_urlsafe", return_value="auto-token-12345"):
        r = client.post("/api/public/signup", json=_signup_payload(1))
        assert r.status_code == 200, r.text
        signup = r.json()
        assert signup["status"] == "pending_verification"

    r = client.get("/api/public/signup/verify?token=auto-token-12345")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["verified"] is True
    assert data["tenant_status"] == "active"
    assert data["user_status"] == "active"
    assert "auto-approved" in data["message"].lower()

    tenant_id = signup["tenant_id"]

    conn = _foundation_conn(client)
    try:
        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE id = ?", (tenant_id,)
        ).fetchone()
        assert tenant["status"] == "active"
        assert tenant["approved_by"] == "auto"
        assert tenant["signup_mode"] == "auto"

        user = conn.execute(
            "SELECT * FROM fnd_users WHERE tenant_id = ? AND email = ?",
            (tenant_id, "owner1@autocorp.test"),
        ).fetchone()
        assert user is not None
        assert user["status"] == "active"
        owner_id = user["id"]
    finally:
        conn.close()

    headers = _auth_headers("owner1@autocorp.test", tenant_id, owner_id)

    r = client.get("/api/workspaces/general", headers=headers)
    assert r.status_code == 200, r.text
    general_ws = r.json()
    assert general_ws["kind"] == "tenant_general"
    assert general_ws["display_name"] == "Auto Corp 1"

    r = client.get(f"/api/tenants/{tenant_id}/identity", headers=headers)
    assert r.status_code == 200, r.text
    identity = r.json()
    assert identity["name"] == "Auto Corp 1"
    assert identity["slug"] == "auto-corp-1"


def test_signup_global_daily_limit(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """The global daily signup counter rejects signups beyond the limit."""

    monkeypatch.setenv("FABERLOOM_SIGNUP_DAILY_LIMIT", "2")

    for i in range(2):
        r = client.post("/api/public/signup", json=_signup_payload(100 + i))
        assert r.status_code == 200, r.text

    r = client.post("/api/public/signup", json=_signup_payload(102))
    assert r.status_code == 429, r.text


def test_signup_rejects_disposable_domain(client: TestClient) -> None:
    """Disposable email domains are rejected at signup time."""

    payload = _signup_payload(200)
    payload["owner_email"] = "owner@mailinator.com"
    r = client.post("/api/public/signup", json=payload)
    assert r.status_code == 422, r.text


def test_signup_auto_requires_captcha_config(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """Auto mode with captcha required but no provider configured returns 503."""

    monkeypatch.setenv("FABERLOOM_SIGNUP_CAPTCHA_REQUIRED", "true")

    payload = _signup_payload(300)
    r = client.post("/api/public/signup", json=payload)
    assert r.status_code == 503, r.text
    assert "captcha" in r.json()["detail"].lower()


def test_onboarding_first_message(client: TestClient) -> None:
    """The first message in ws-general for a fresh tenant returns onboarding."""

    with patch("app.src.auth.secrets.token_urlsafe", return_value="onboard-token-12345"):
        r = client.post("/api/public/signup", json=_signup_payload(400))
        assert r.status_code == 200, r.text
        signup = r.json()

    r = client.get("/api/public/signup/verify?token=onboard-token-12345")
    assert r.status_code == 200, r.text

    tenant_id = signup["tenant_id"]

    conn = _foundation_conn(client)
    try:
        user = conn.execute(
            "SELECT * FROM fnd_users WHERE tenant_id = ? AND email = ?",
            (tenant_id, "owner400@autocorp.test"),
        ).fetchone()
        owner_id = user["id"]
    finally:
        conn.close()

    headers = _auth_headers("owner400@autocorp.test", tenant_id, owner_id)

    r = client.get("/api/workspaces/general", headers=headers)
    assert r.status_code == 200, r.text
    general_ws = r.json()
    ws_id = general_ws["id"]

    r = client.post(
        f"/api/workspaces/{ws_id}/chats",
        json={"title": "Onboarding"},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    chat_id = r.json()["id"]

    r = client.post(
        f"/api/workspaces/{ws_id}/chats/{chat_id}/completions",
        json={"message": "qué hay", "mode": "manual"},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    content = r.json()["message"]["content"]
    assert "subir archivos a Knowledge" in content
