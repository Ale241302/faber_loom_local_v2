"""Tests for E2-6 object storage: presigned URLs, workspace sealing, lifecycle."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_DEV_TRUST_HEADERS", "true")
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.storage import reset_object_store

    reset_object_store()
    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _auth_headers(role: str = "admin") -> dict[str, str]:
    return {
        "x-tenant-id": "default",
        "x-user-id": "tester",
        "x-actor-id": "tester",
        "x-actor-role": role,
    }


def _create_workspace(client: TestClient, name: str) -> dict[str, Any]:
    resp = client.post("/api/workspaces", json={"name": name}, headers=_auth_headers())
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_presigned_upload_requires_workspace(client: TestClient) -> None:
    resp = client.post(
        "/api/workspaces/ws_missing/objects/presigned-upload",
        json={"file_name": "doc.pdf", "mime_type": "application/pdf", "size_bytes": 1024},
        headers=_auth_headers(),
    )
    assert resp.status_code == 404


def test_presigned_upload_blocks_executable(client: TestClient) -> None:
    ws = _create_workspace(client, "Upload Blocks")
    resp = client.post(
        f"/api/workspaces/{ws['id']}/objects/presigned-upload",
        json={"file_name": "evil.exe", "mime_type": "application/x-dosexec", "size_bytes": 1024},
        headers=_auth_headers(),
    )
    assert resp.status_code == 415


def test_presigned_upload_blocks_oversized(client: TestClient) -> None:
    ws = _create_workspace(client, "Upload Size")
    resp = client.post(
        f"/api/workspaces/{ws['id']}/objects/presigned-upload",
        json={"file_name": "big.pdf", "mime_type": "application/pdf", "size_bytes": 10_000_000_000},
        headers=_auth_headers(),
    )
    assert resp.status_code == 413


def test_presigned_upload_returns_valid_url(client: TestClient) -> None:
    ws = _create_workspace(client, "Upload OK")
    resp = client.post(
        f"/api/workspaces/{ws['id']}/objects/presigned-upload",
        json={"file_name": "doc.pdf", "mime_type": "application/pdf", "size_bytes": 1024},
        headers=_auth_headers(),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["object_id"].startswith("obj_")
    assert data["bucket"] == "fl-uploads"
    assert f"ws-{ws['id']}/upload/" in data["object_key"]
    assert data["upload_url"].startswith("memory://fl-uploads/")


def test_cannot_confirm_missing_object(client: TestClient) -> None:
    ws = _create_workspace(client, "Confirm Missing")
    resp = client.post(
        f"/api/workspaces/{ws['id']}/objects/confirm",
        json={"object_id": "obj_doesnotexist", "sha256": "abc"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 404


def test_confirm_and_read_object(client: TestClient) -> None:
    ws = _create_workspace(client, "Confirm Read")
    resp = client.post(
        f"/api/workspaces/{ws['id']}/objects/presigned-upload",
        json={"file_name": "doc.pdf", "mime_type": "application/pdf", "size_bytes": 1024},
        headers=_auth_headers(),
    )
    obj_id = resp.json()["object_id"]

    # Simulate browser upload by putting bytes into memory store.
    from app.src.storage import get_object_store

    store = get_object_store()
    row = resp.json()
    store.put_object(row["bucket"], row["object_key"], b"hello", "application/pdf")

    confirm = client.post(
        f"/api/workspaces/{ws['id']}/objects/confirm",
        json={"object_id": obj_id, "sha256": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"},
        headers=_auth_headers(),
    )
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["ingest_status"] == "validating"

    read = client.get(
        f"/api/workspaces/{ws['id']}/objects/{obj_id}",
        headers=_auth_headers(),
    )
    assert read.status_code == 200
    assert read.json()["id"] == obj_id

    url_resp = client.get(
        f"/api/workspaces/{ws['id']}/objects/{obj_id}/url",
        headers=_auth_headers(),
    )
    assert url_resp.status_code == 200
    assert "download_url" in url_resp.json()


def test_object_is_workspace_sealed(client: TestClient) -> None:
    ws_a = _create_workspace(client, "WS A")
    ws_b = _create_workspace(client, "WS B")

    resp = client.post(
        f"/api/workspaces/{ws_a['id']}/objects/presigned-upload",
        json={"file_name": "a.pdf", "mime_type": "application/pdf", "size_bytes": 1024},
        headers=_auth_headers(),
    )
    obj_id = resp.json()["object_id"]

    leak = client.get(
        f"/api/workspaces/{ws_b['id']}/objects/{obj_id}",
        headers=_auth_headers(),
    )
    assert leak.status_code == 404

    leak_url = client.get(
        f"/api/workspaces/{ws_b['id']}/objects/{obj_id}/url",
        headers=_auth_headers(),
    )
    assert leak_url.status_code == 404


def test_delete_object_requires_confirmation(client: TestClient) -> None:
    ws = _create_workspace(client, "Delete Object")
    resp = client.post(
        f"/api/workspaces/{ws['id']}/objects/presigned-upload",
        json={"file_name": "del.pdf", "mime_type": "application/pdf", "size_bytes": 1024},
        headers=_auth_headers(),
    )
    obj_id = resp.json()["object_id"]

    no_token = client.delete(
        f"/api/workspaces/{ws['id']}/objects/{obj_id}",
        headers=_auth_headers(),
    )
    assert no_token.status_code == 409

    import hashlib

    token = hashlib.sha256(obj_id.encode("utf-8")).hexdigest()[:16]
    deleted = client.delete(
        f"/api/workspaces/{ws['id']}/objects/{obj_id}?confirmation_token={token}",
        headers=_auth_headers(),
    )
    assert deleted.status_code == 204

    gone = client.get(
        f"/api/workspaces/{ws['id']}/objects/{obj_id}",
        headers=_auth_headers(),
    )
    assert gone.status_code == 404


def test_minio_backend_uses_public_endpoint_for_presigned(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FL_MINIO_ACCESS_KEY", "test-access")
    monkeypatch.setenv("FL_MINIO_SECRET_KEY", "test-secret")
    monkeypatch.setenv("FL_MINIO_ENDPOINT", "faberloom-minio:9000")
    monkeypatch.setenv("FL_MINIO_PUBLIC_URL", "https://minio.faberloom.ai")

    from app.src.storage import _MinioStoreBackend

    backend = _MinioStoreBackend()
    # Internal client stays on the docker network.
    assert backend._client._base_url.host == "faberloom-minio:9000"
    assert not backend._client._base_url.is_https
    # Presigned client must sign against the TLS front door.
    assert backend._presigned_client._base_url.host == "minio.faberloom.ai"
    assert backend._presigned_client._base_url.is_https
