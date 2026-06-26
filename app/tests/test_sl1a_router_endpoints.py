"""Tests for provider configuration endpoints."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "spaceloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("SPACELOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("SPACELOOM_CONFIG_DIR", str(config_dir))

    for name in (
        "OPENAI_API_KEY",
        "SPACELOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "SPACELOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "SPACELOOM_GOOGLE_API_KEY",
        "KIMI_API_KEY",
        "MOONSHOT_API_KEY",
        "SPACELOOM_KIMI_API_KEY",
        "SPACELOOM_ENABLE_OLLAMA",
        "SPACELOOM_OLLAMA_ENABLED",
        "SPACELOOM_PROVIDER_ALLOWLIST",
        "SPACELOOM_BUDGET_CAP_USD",
        "SPACELOOM_DEV_TRUST_HEADERS",
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


def test_list_providers_masks_keys(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.get(f"/api/workspaces/{workspace_id}/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "model_allowlist" in data
    slugs = {p["provider_slug"] for p in data["providers"]}
    assert "kimi" in slugs
    openai = next(p for p in data["providers"] if p["provider_slug"] == "openai")
    assert openai["api_key_masked"] is None


def test_update_provider_config_and_status(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)

    response = client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        json={"api_key": "sk-test1234", "model_default": "gpt-4o", "priority": 5, "is_enabled": True},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["api_key_masked"] == "sk-t•••1234"
    assert updated["model_default"] == "gpt-4o"
    assert updated["priority"] == 5

    response = client.get(f"/api/workspaces/{workspace_id}/router/status")
    assert response.status_code == 200
    openai_status = next(p for p in response.json()["providers"] if p["provider_slug"] == "openai")
    assert openai_status["configured"] is True
    assert openai_status["available"] is True


def test_delete_provider_key(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        json={"api_key": "sk-test1234"},
    )

    response = client.delete(f"/api/workspaces/{workspace_id}/providers/openai/key")
    assert response.status_code == 200
    assert response.json()["status"] == "key_removed"

    response = client.get(f"/api/workspaces/{workspace_id}/providers")
    openai = next(p for p in response.json()["providers"] if p["provider_slug"] == "openai")
    assert openai["api_key_masked"] is None


def test_test_provider_without_key(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.post(f"/api/workspaces/{workspace_id}/providers/openai/test")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert "not configured" in (data["error"] or "").lower()


def test_update_unknown_provider_returns_422(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.patch(
        f"/api/workspaces/{workspace_id}/providers/unknown",
        json={"api_key": "sk-test"},
    )
    assert response.status_code == 422
