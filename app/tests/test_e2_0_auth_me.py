"""E2-0 — Tests for /api/me session identity convergence.

The frontend uses /api/me as the single source of truth for the current user.
These tests verify that the endpoint returns Foundation-resolved claims when
available and falls back gracefully to the legacy local user.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

OWNER = {"email": "owner@acme.test", "display_name": "Owner", "password": "s3cret-pass"}


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "fnd.sqlite3"))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        f'{{"{OWNER["email"]}":"{OWNER["password"]}"}}',
    )
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)

    from app.src.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


def _bootstrap(client: TestClient) -> dict:
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
    resp = client.post(
        "/api/auth/login", json={"email": OWNER["email"], "password": OWNER["password"]}
    )
    assert resp.status_code == 200, resp.text


def test_me_resolves_foundation_identity(client: TestClient) -> None:
    user = _bootstrap(client)
    _login_legacy(client)

    resp = client.get("/api/me")
    assert resp.status_code == 200, resp.text
    me = resp.json()
    assert me["email"] == OWNER["email"]
    assert me["tenant_id"] == user["tenant_id"]
    assert me["user_id"] == user["id"]
    assert me["role"] == "owner"
    assert me["foundation_resolved"] is True


def test_me_falls_back_to_local_user_without_foundation(client: TestClient) -> None:
    # No Foundation bootstrap; login with a legacy user resolves to local claims.
    resp = client.post(
        "/api/auth/login", json={"email": OWNER["email"], "password": OWNER["password"]}
    )
    assert resp.status_code == 200, resp.text

    resp = client.get("/api/me")
    assert resp.status_code == 200, resp.text
    me = resp.json()
    assert me["email"] == OWNER["email"]
    assert me["tenant_id"] == "default"
    assert me["user_id"] == OWNER["email"]
    assert me["role"] == "admin"
    assert me["foundation_resolved"] is False


def test_me_requires_authentication(client: TestClient) -> None:
    resp = client.get("/api/me")
    assert resp.status_code == 401, resp.text
