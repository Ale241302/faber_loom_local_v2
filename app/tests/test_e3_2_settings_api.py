"""Tests for E3-2 settings cascade REST endpoints."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
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


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def _keys(settings: list[dict[str, Any]]) -> set[str]:
    return {s["key"] for s in settings}


def test_get_tenant_settings_returns_defaults(client: TestClient) -> None:
    response = client.get("/api/tenant/settings")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "settings" in data
    keys = _keys(data["settings"])
    assert "routing.max_budget_usd" in keys
    assert "routing.auto_dispatch" in keys
    for setting in data["settings"]:
        assert setting["source"] == "default"


def test_put_tenant_settings_override(client: TestClient) -> None:
    response = client.put(
        "/api/tenant/settings",
        json={"overrides": {"routing.max_budget_usd": 10.5, "routing.auto_dispatch": True}},
    )
    assert response.status_code == 200, response.text
    settings = {s["key"]: s for s in response.json()["settings"]}
    assert settings["routing.max_budget_usd"]["value"] == 10.5
    assert settings["routing.max_budget_usd"]["source"] == "tenant"
    assert settings["routing.auto_dispatch"]["value"] is True

    # A fresh read must reflect the override.
    response = client.get("/api/tenant/settings")
    assert response.status_code == 200
    settings = {s["key"]: s for s in response.json()["settings"]}
    assert settings["routing.max_budget_usd"]["value"] == 10.5
    assert settings["routing.max_budget_usd"]["source"] == "tenant"


def test_get_workspace_settings_returns_defaults(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.get(f"/api/workspaces/{workspace_id}/settings")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "settings" in data
    for setting in data["settings"]:
        assert "key" in setting
        assert "value" in setting
        assert "source" in setting


def test_put_workspace_settings_override(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)

    response = client.put(
        f"/api/workspaces/{workspace_id}/settings",
        json={"overrides": {"routing.max_budget_usd": 7.0, "routing.max_steps": 10}},
    )
    assert response.status_code == 200, response.text
    settings = {s["key"]: s for s in response.json()["settings"]}
    assert settings["routing.max_budget_usd"]["value"] == 7.0
    assert settings["routing.max_budget_usd"]["source"] == "workspace"
    assert settings["routing.max_steps"]["value"] == 10
    assert settings["routing.max_steps"]["source"] == "workspace"


def test_get_user_settings_returns_defaults_when_no_foundation(client: TestClient) -> None:
    response = client.get("/api/users/me/settings")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "settings" in data
    for setting in data["settings"]:
        assert setting["source"] == "default"


def test_get_settings_resolved(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.get(f"/api/settings/resolved?workspace_id={workspace_id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert "settings" in data
    keys = _keys(data["settings"])
    assert "routing.max_budget_usd" in keys
