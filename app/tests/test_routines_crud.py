"""Tests for Routine Hub CRUD and FaberLoom catalog import."""

from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "spaceloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SPACELOOM_DB_PATH", str(db_path))

    for name in (
        "OPENAI_API_KEY",
        "SPACELOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "SPACELOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "SPACELOOM_GOOGLE_API_KEY",
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


def _create_routine(client: TestClient, workspace_id: str, approved: bool = False) -> dict[str, Any]:
    payload = {
        "name": "cotizador-crud",
        "skill_md": "---\nname: cotizador-crud\npersona: Eres un asistente.\ntools: [\"calculator\"]\n---\nResponde.",
        "persona_md": "Eres un asistente.",
        "tools_allowlist": json.dumps(["calculator"]),
        "schema_output_json": "{}",
        "trigger_json": "[]",
        "is_active": 1,
        "source_version": "v1",
    }
    response = client.post(f"/api/workspaces/{workspace_id}/routines", json=payload)
    assert response.status_code == 201, response.text
    routine = response.json()
    if approved:
        response = client.post(f"/api/workspaces/{workspace_id}/routines/{routine['id']}/approve?approved_by=local")
        assert response.status_code == 200
        routine = response.json()
    return routine


def _confirmation_token(resource_id: str) -> str:
    import hashlib

    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def test_patch_update_name(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id)

    response = client.patch(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}",
        json={"name": "cotizador-renombrado"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "cotizador-renombrado"
    assert data["category"] == "custom"


def test_patch_skill_md_clears_approval(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id, approved=True)
    assert routine["approved_by"] == "local"

    response = client.patch(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}",
        json={"skill_md": "---\nname: cotizador-crud\npersona: Nueva persona.\n---\nNueva instrucción."},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["approved_by"] is None
    assert "Nueva persona" in data["persona_md"]


def test_patch_toggle_is_active_keeps_approval(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id, approved=True)
    assert routine["is_active"] == 1
    assert routine["approved_by"] == "local"

    response = client.patch(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}",
        json={"is_active": 0},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["is_active"] == 0
    assert data["approved_by"] == "local"


def test_delete_requires_confirmation_token(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    routine = _create_routine(client, workspace_id)

    response = client.delete(f"/api/workspaces/{workspace_id}/routines/{routine['id']}")
    assert response.status_code == 409, response.text

    response = client.delete(
        f"/api/workspaces/{workspace_id}/routines/{routine['id']}?confirmation_token={_confirmation_token(routine['id'])}"
    )
    assert response.status_code == 204, response.text

    response = client.get(f"/api/workspaces/{workspace_id}/routines/{routine['id']}")
    assert response.status_code == 404


def test_faberloom_catalog_not_empty(client: TestClient) -> None:
    response = client.get("/api/faberloom/catalog")
    assert response.status_code == 200, response.text
    catalog = response.json()
    assert isinstance(catalog, list)
    assert len(catalog) > 0
    # SKILL.md must be classified as a skill.
    skill_item = next((item for item in catalog if item["file"] == "SKILL.md"), None)
    assert skill_item is not None
    assert skill_item["category"] == "skill"
    assert skill_item["source_version"] == "faberloom-skill"


def test_import_faberloom_creates_inactive_unapproved(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)

    catalog_response = client.get("/api/faberloom/catalog")
    catalog = catalog_response.json()
    skill_item = next(item for item in catalog if item["file"] == "SKILL.md")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/import-faberloom",
        json={"imports": [skill_item["id"]]},
    )
    assert response.status_code == 200, response.text
    imported = response.json()
    assert len(imported) == 1
    routine = imported[0]
    assert routine["name"] == skill_item["name"]
    assert routine["category"] == "skill"
    assert routine["is_active"] == 0
    assert routine["approved_by"] is None
    assert routine["source_version"] == "faberloom-skill"


def test_import_faberloom_upserts_by_name(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)

    catalog_response = client.get("/api/faberloom/catalog")
    catalog = catalog_response.json()
    skill_item = next(item for item in catalog if item["file"] == "SKILL.md")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/import-faberloom",
        json={"imports": [skill_item["id"]]},
    )
    assert response.status_code == 200
    first_id = response.json()[0]["id"]

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/import-faberloom",
        json={"imports": [skill_item["id"]]},
    )
    assert response.status_code == 200
    second_id = response.json()[0]["id"]
    assert first_id == second_id
