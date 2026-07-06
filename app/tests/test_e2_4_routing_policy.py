"""E2-4 workspace routing policy endpoints and permissions."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("FABERLOOM_DEV_TRUST_HEADERS", "true")

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


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def test_get_default_routing_policy(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.get(f"/api/workspaces/{ws}/routing-policy", headers=_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == ws
    assert data["budget_cap_usd"] == 5.0
    assert data["auto_mode_enabled"] is False
    assert data["max_auto_steps"] == 3
    assert data["require_local_only"] is False
    assert data["provider_allowlist"] == []
    assert data["model_allowlist"] == {}


def test_update_routing_policy_as_owner(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={
            "budget_cap_usd": 1.5,
            "auto_mode_enabled": True,
            "max_auto_steps": 5,
            "require_local_only": True,
            "provider_allowlist": ["ollama"],
            "model_allowlist": {"ollama": ["llama3.1"]},
        },
        headers=_headers("owner"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["budget_cap_usd"] == 1.5
    assert data["auto_mode_enabled"] is True
    assert data["max_auto_steps"] == 5
    assert data["require_local_only"] is True
    assert data["provider_allowlist"] == ["ollama"]
    assert data["model_allowlist"] == {"ollama": ["llama3.1"]}


def test_update_routing_policy_forbidden_for_viewer(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"budget_cap_usd": 2.0},
        headers=_headers("viewer"),
    )
    assert response.status_code == 403


def test_update_routing_policy_forbidden_for_operator(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"budget_cap_usd": 2.0},
        headers=_headers("operator"),
    )
    assert response.status_code == 403


def test_update_routing_policy_admin_allowed(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"budget_cap_usd": 2.0},
        headers=_headers("admin"),
    )
    assert response.status_code == 200
    assert response.json()["budget_cap_usd"] == 2.0


def test_routing_policy_is_workspace_scoped(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"budget_cap_usd": 0.5},
        headers=_headers("owner"),
    )
    assert response.status_code == 200

    # A different workspace still has defaults.
    response = client.post("/api/workspaces", json={"name": "Other"}, headers=_headers("owner"))
    assert response.status_code == 201
    other_ws = response.json()["id"]
    response = client.get(f"/api/workspaces/{other_ws}/routing-policy", headers=_headers("owner"))
    assert response.status_code == 200
    assert response.json()["budget_cap_usd"] == 5.0


def test_provider_allowlist_blocks_manual_model(client: TestClient) -> None:
    ws = _workspace_id(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"provider_allowlist": ["ollama"]},
        headers=_headers("owner"),
    )
    response = client.post(
        f"/api/workspaces/{ws}/model-catalog",
        json={
            "provider_slug": "fake",
            "model": "fake-model",
            "capabilities": ["text"],
            "is_local": True,
        },
        headers=_headers("owner"),
    )
    assert response.status_code == 201

    response = client.post(
        f"/api/workspaces/{ws}/chats",
        json={"title": "Manual block"},
        headers=_headers("owner"),
    )
    chat_id = response.json()["id"]

    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat_id}/completions",
        json={"message": "Hi", "provider_slug": "fake", "model": "fake-model"},
        headers=_headers("owner"),
    )
    assert response.status_code == 422
    assert "not allowed" in response.json()["detail"]
