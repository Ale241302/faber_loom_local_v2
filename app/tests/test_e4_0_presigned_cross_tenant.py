"""E4-0 cross-tenant object-store contamination test (E3-3 gap closure)."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
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


def _headers(tenant_id: str = "default", role: str = "owner") -> dict[str, str]:
    return {
        "x-tenant-id": tenant_id,
        "x-user-id": "tester",
        "x-actor-id": "tester",
        "x-actor-role": role,
    }


def _create_workspace(client: TestClient, name: str, tenant_id: str = "default") -> dict[str, Any]:
    resp = client.post("/api/workspaces", json={"name": name}, headers=_headers(tenant_id))
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_presigned_url_isolated_by_tenant(client: TestClient) -> None:
    ws_a = _create_workspace(client, "WS A", tenant_id="tenant-a")
    ws_b = _create_workspace(client, "WS B", tenant_id="tenant-b")

    # Create and confirm an object in tenant-a / ws-a.
    resp = client.post(
        f"/api/workspaces/{ws_a['id']}/objects/presigned-upload",
        json={"file_name": "a.pdf", "mime_type": "application/pdf", "size_bytes": 1024},
        headers=_headers("tenant-a"),
    )
    assert resp.status_code == 201, resp.text
    obj = resp.json()

    from app.src.storage import get_object_store

    store = get_object_store()
    store.put_object(obj["bucket"], obj["object_key"], b"secret-tenant-a", "application/pdf")

    confirm = client.post(
        f"/api/workspaces/{ws_a['id']}/objects/confirm",
        json={"object_id": obj["object_id"], "sha256": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"},
        headers=_headers("tenant-a"),
    )
    assert confirm.status_code == 200, confirm.text

    # Tenant-b must not be able to read the object metadata.
    leak_meta = client.get(
        f"/api/workspaces/{ws_b['id']}/objects/{obj['object_id']}",
        headers=_headers("tenant-b"),
    )
    assert leak_meta.status_code == 404

    # Tenant-b must not be able to request a download URL for the object.
    leak_url = client.get(
        f"/api/workspaces/{ws_b['id']}/objects/{obj['object_id']}/url",
        headers=_headers("tenant-b"),
    )
    assert leak_url.status_code == 404

    # Object key prefix must include tenant-a.
    assert f"t-tenant-a/ws-{ws_a['id']}" in obj["object_key"]

    # Tenant-a can still retrieve it.
    own_url = client.get(
        f"/api/workspaces/{ws_a['id']}/objects/{obj['object_id']}/url",
        headers=_headers("tenant-a"),
    )
    assert own_url.status_code == 200
    assert "download_url" in own_url.json()
