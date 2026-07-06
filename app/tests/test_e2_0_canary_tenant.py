"""E2-0 — Tenant canary seeding and isolation regression tests.

The canary tenant/workspace is created at application startup and must remain
invisible to the default tenant while remaining reachable for canary-scoped
requests.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("FABERLOOM_DEV_TRUST_HEADERS", "true")

    # Avoid leaking external credentials or feature flags into the app under test.
    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
        "KIMI_API_KEY",
        "MOONSHOT_API_KEY",
        "FABERLOOM_KIMI_API_KEY",
        "FABERLOOM_ENABLE_OLLAMA",
        "FABERLOOM_OLLAMA_ENABLED",
        "FABERLOOM_PROVIDER_ALLOWLIST",
        "FABERLOOM_BUDGET_CAP_USD",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _headers(tenant_id: str, user_id: str = "tester") -> dict[str, str]:
    return {
        "x-tenant-id": tenant_id,
        "x-user-id": user_id,
        "x-actor-id": user_id,
    }


def test_canary_workspace_is_seeded(client: TestClient) -> None:
    """The canary workspace exists and is tagged with the canary tenant."""

    response = client.get("/api/workspaces", headers=_headers("canary"))
    assert response.status_code == 200, response.text
    workspaces = response.json()["workspaces"]
    canary = next((w for w in workspaces if w["slug"] == "canary"), None)
    assert canary is not None
    assert canary["tenant_id"] == "canary"
    assert canary["name"] == "Canary Tenant"


def test_default_tenant_cannot_see_canary_workspace(client: TestClient) -> None:
    """The default tenant listing must not expose the canary workspace."""

    response = client.get("/api/workspaces", headers=_headers("default"))
    assert response.status_code == 200, response.text
    workspaces = response.json()["workspaces"]
    assert all(w["tenant_id"] != "canary" for w in workspaces)
    assert not any(w["slug"] == "canary" for w in workspaces)


def test_canary_tenant_cannot_see_default_demo_workspace(client: TestClient) -> None:
    """The canary tenant listing must not expose the default demo workspace."""

    response = client.get("/api/workspaces", headers=_headers("canary"))
    assert response.status_code == 200, response.text
    workspaces = response.json()["workspaces"]
    assert all(w["tenant_id"] == "canary" for w in workspaces)
    assert not any(w["slug"] == "mwt-demo" for w in workspaces)


def test_canary_workspace_is_not_reachable_from_default_tenant(client: TestClient) -> None:
    """Direct access to the canary workspace using a default tenant scope fails."""

    canary_list = client.get("/api/workspaces", headers=_headers("canary")).json()["workspaces"]
    canary_id = next(w["id"] for w in canary_list if w["slug"] == "canary")

    response = client.get(f"/api/workspaces/{canary_id}", headers=_headers("default"))
    assert response.status_code == 404, response.text


def test_dev_trust_headers_disabled_ignores_canary_header(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Without trust headers the canary header is ignored and requests resolve to default."""

    monkeypatch.delenv("FABERLOOM_DEV_TRUST_HEADERS", raising=False)

    response = client.get("/api/workspaces", headers={"x-tenant-id": "canary"})
    assert response.status_code == 200, response.text
    workspaces = response.json()["workspaces"]
    assert not any(w["tenant_id"] == "canary" for w in workspaces)
