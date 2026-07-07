"""E2-4 workspace model catalog endpoints."""

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


def test_catalog_seeded_from_configured_providers(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.get(f"/api/workspaces/{ws}/model-catalog", headers=_headers("owner"))
    assert response.status_code == 200
    entries = response.json()
    # No cloud keys configured; only the local Ollama entry is enabled by default.
    slugs = {e["provider_slug"] for e in entries}
    assert "ollama" in slugs
    enabled = {e["provider_slug"] for e in entries if e["is_enabled"]}
    assert enabled == {"ollama"}


def test_create_catalog_entry_requires_admin(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.post(
        f"/api/workspaces/{ws}/model-catalog",
        json={"provider_slug": "stub", "model": "fake-image-gen", "capabilities": ["image_gen"]},
        headers=_headers("operator"),
    )
    assert response.status_code == 403


def test_create_and_read_catalog_entry(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.post(
        f"/api/workspaces/{ws}/model-catalog",
        json={"provider_slug": "stub", "model": "fake-image-gen", "capabilities": ["image_gen"]},
        headers=_headers("owner"),
    )
    assert response.status_code == 201
    entry = response.json()
    assert entry["provider_slug"] == "stub"
    assert entry["model"] == "fake-image-gen"
    assert entry["capabilities"] == ["image_gen"]
    assert entry["is_enabled"] is True

    response = client.get(f"/api/workspaces/{ws}/model-catalog", headers=_headers("owner"))
    assert any(e["id"] == entry["id"] for e in response.json())


def test_update_catalog_entry(client: TestClient) -> None:
    ws = _workspace_id(client)
    entry = client.post(
        f"/api/workspaces/{ws}/model-catalog",
        json={"provider_slug": "stub", "model": "fake-image-gen", "capabilities": ["image_gen"]},
        headers=_headers("owner"),
    ).json()

    response = client.patch(
        f"/api/workspaces/{ws}/model-catalog/{entry['id']}",
        json={"capabilities": ["image_gen", "cheap"], "is_enabled": False},
        headers=_headers("owner"),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["capabilities"] == ["image_gen", "cheap"]
    assert data["is_enabled"] is False


def test_delete_catalog_entry(client: TestClient) -> None:
    ws = _workspace_id(client)
    entry = client.post(
        f"/api/workspaces/{ws}/model-catalog",
        json={"provider_slug": "stub", "model": "fake-image-gen", "capabilities": ["image_gen"]},
        headers=_headers("owner"),
    ).json()

    response = client.delete(
        f"/api/workspaces/{ws}/model-catalog/{entry['id']}",
        headers=_headers("owner"),
    )
    assert response.status_code == 204

    response = client.get(f"/api/workspaces/{ws}/model-catalog", headers=_headers("owner"))
    assert not any(e["id"] == entry["id"] for e in response.json())


def test_viewer_can_list_catalog(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.get(f"/api/workspaces/{ws}/model-catalog", headers=_headers("viewer"))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_catalog_entry_capabilities_validation(client: TestClient) -> None:
    ws = _workspace_id(client)
    response = client.post(
        f"/api/workspaces/{ws}/model-catalog",
        json={"provider_slug": "stub", "model": "x", "capabilities": []},
        headers=_headers("owner"),
    )
    assert response.status_code == 422
