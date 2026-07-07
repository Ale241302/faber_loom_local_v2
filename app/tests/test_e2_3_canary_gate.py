"""E2-3 gate — Permanent canary tenant/workspace.

The canary workspace is seeded from E2-0/E2-1 and must remain present and
marked for every E2-3 isolation gate. This test fails loudly if the canary
is missing or not distinguishable from production workspaces.
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


def test_canary_workspace_exists_and_is_marked(client: TestClient) -> None:
    """E2-3 gate: there must be exactly one workspace flagged as canary."""

    response = client.get("/api/workspaces", headers=_headers("canary"))
    assert response.status_code == 200, response.text
    workspaces = response.json()["workspaces"]
    canaries = [w for w in workspaces if w.get("is_canary")]
    assert len(canaries) == 1, f"Expected exactly one canary workspace, got {len(canaries)}"
    canary = canaries[0]
    assert canary["slug"] == "canary"
    assert canary["tenant_id"] == "canary"
    assert canary["name"] == "Canary Tenant"


def test_canary_is_invisible_to_default_tenant(client: TestClient) -> None:
    """MWT/default tenant must never list the canary workspace."""

    response = client.get("/api/workspaces", headers=_headers("default"))
    assert response.status_code == 200, response.text
    workspaces = response.json()["workspaces"]
    assert not any(w.get("is_canary") for w in workspaces)
    assert not any(w["tenant_id"] == "canary" for w in workspaces)


def test_canary_is_isolated_from_default_workspaces(client: TestClient) -> None:
    """Canary-scoped requests must not see MWT/demo workspaces."""

    response = client.get("/api/workspaces", headers=_headers("canary"))
    assert response.status_code == 200, response.text
    workspaces = response.json()["workspaces"]
    assert not any(w["tenant_id"] != "canary" for w in workspaces)
    assert not any(w["slug"] == "mwt-demo" for w in workspaces)


def test_canary_cannot_be_accessed_with_default_scope(client: TestClient) -> None:
    """Direct workspace access with the wrong tenant scope is rejected."""

    canary_list = client.get("/api/workspaces", headers=_headers("canary")).json()["workspaces"]
    canary_id = next(w["id"] for w in canary_list if w["slug"] == "canary")

    response = client.get(f"/api/workspaces/{canary_id}", headers=_headers("default"))
    assert response.status_code == 404, response.text
