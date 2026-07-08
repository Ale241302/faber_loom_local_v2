"""Leak tests for E2-6 object storage: cross-workspace and cross-tenant isolation."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.storage import reset_object_store

    reset_object_store()
    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _headers(tenant: str = "default", role: str = "admin") -> dict[str, str]:
    return {
        "x-tenant-id": tenant,
        "x-user-id": "tester",
        "x-actor-id": "tester",
        "x-actor-role": role,
    }


def _create_workspace(client: TestClient, name: str, tenant: str = "default") -> dict[str, Any]:
    resp = client.post("/api/workspaces", json={"name": name}, headers=_headers(tenant))
    assert resp.status_code == 201, resp.text
    return resp.json()


def _upload_placeholder(client: TestClient, workspace: dict[str, Any], tenant: str = "default") -> str:
    resp = client.post(
        f"/api/workspaces/{workspace['id']}/objects/presigned-upload",
        json={"file_name": "leak.pdf", "mime_type": "application/pdf", "size_bytes": 1024},
        headers=_headers(tenant),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["object_id"]


def test_object_not_leakable_across_workspaces_same_tenant(client: TestClient) -> None:
    ws_a = _create_workspace(client, "Leak A")
    ws_b = _create_workspace(client, "Leak B")
    obj_id = _upload_placeholder(client, ws_a)

    # Same tenant, different workspace: every operation must fail as not found.
    assert client.get(
        f"/api/workspaces/{ws_b['id']}/objects/{obj_id}",
        headers=_headers(),
    ).status_code == 404

    assert client.get(
        f"/api/workspaces/{ws_b['id']}/objects/{obj_id}/url",
        headers=_headers(),
    ).status_code == 404

    assert client.post(
        f"/api/workspaces/{ws_b['id']}/objects/confirm",
        json={"object_id": obj_id, "sha256": "abc"},
        headers=_headers(),
    ).status_code == 404

    assert client.delete(
        f"/api/workspaces/{ws_b['id']}/objects/{obj_id}?confirmation_token=abc",
        headers=_headers(),
    ).status_code == 404


def test_object_not_leakable_across_tenants(client: TestClient) -> None:
    ws_default = _create_workspace(client, "Leak Default", tenant="default")
    obj_id = _upload_placeholder(client, ws_default, tenant="default")

    # A different tenant cannot even resolve the workspace.
    assert client.get(
        f"/api/workspaces/{ws_default['id']}/objects/{obj_id}",
        headers=_headers(tenant="canary"),
    ).status_code == 404

    assert client.get(
        f"/api/workspaces/{ws_default['id']}/objects",
        headers=_headers(tenant="canary"),
    ).status_code == 404


def test_list_objects_does_not_expose_other_workspaces(client: TestClient) -> None:
    ws_a = _create_workspace(client, "List A")
    ws_b = _create_workspace(client, "List B")
    obj_a = _upload_placeholder(client, ws_a)
    obj_b = _upload_placeholder(client, ws_b)

    list_a = client.get(f"/api/workspaces/{ws_a['id']}/objects", headers=_headers()).json()
    list_b = client.get(f"/api/workspaces/{ws_b['id']}/objects", headers=_headers()).json()

    assert {o["id"] for o in list_a} == {obj_a}
    assert {o["id"] for o in list_b} == {obj_b}


def test_object_key_contains_workspace_id_as_seal_prefix(client: TestClient) -> None:
    ws = _create_workspace(client, "Seal Prefix")
    resp = client.post(
        f"/api/workspaces/{ws['id']}/objects/presigned-upload",
        json={"file_name": "seal.pdf", "mime_type": "application/pdf", "size_bytes": 1024},
        headers=_headers(),
    )
    assert resp.status_code == 201
    key = resp.json()["object_key"]
    assert key.startswith(f"t-default/ws-{ws['id']}/")
