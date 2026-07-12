"""E4-4 — Chat general del tenant (ws-general)."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.db import connect


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))

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
        "FABERLOOM_AUTO_MODE_ENABLED",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def test_general_workspace_created_by_seed(client: TestClient) -> None:
    resp = client.get("/api/workspaces/general", headers=_headers("owner"))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["kind"] == "tenant_general"
    assert data["slug"] == "general"
    assert data["display_name"] == "Faber"


def test_general_workspace_not_in_regular_list(client: TestClient) -> None:
    general = client.get("/api/workspaces/general", headers=_headers("owner")).json()
    resp = client.get("/api/workspaces", headers=_headers("owner"))
    assert resp.status_code == 200, resp.text
    ids = {ws["id"] for ws in resp.json()["workspaces"]}
    assert general["id"] not in ids


def test_general_workspace_rls_across_tenants(client: TestClient) -> None:
    # A user from another tenant should not see the default tenant's ws-general.
    resp = client.get("/api/workspaces/general", headers={"x-actor-role": "owner", "x-user-id": "other", "x-actor-id": "other", "x-tenant-id": "other-tenant"})
    assert resp.status_code == 404, resp.text


def test_cannot_create_tenant_general_workspace_as_editor(client: TestClient) -> None:
    resp = client.post(
        "/api/workspaces",
        json={"name": "Fake general", "slug": "fake-general", "kind": "tenant_general"},
        headers=_headers("editor"),
    )
    assert resp.status_code == 403, resp.text


def test_workspace_kind_column_exists(client: TestClient) -> None:
    conn = connect()
    row = conn.execute("PRAGMA table_info(workspace)").fetchall()
    columns = {r["name"] for r in row}
    assert "kind" in columns
