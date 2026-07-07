"""Smoke test for E2-6 MinIO backup/restore with mc mirror."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


def _create_workspace(client: TestClient, name: str) -> dict[str, Any]:
    resp = client.post(
        "/api/workspaces",
        json={"name": name},
        headers={"x-tenant-id": "default", "x-user-id": "tester", "x-actor-id": "tester", "x-actor-role": "admin"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture()
def client(tmp_path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_DEV_TRUST_HEADERS", "true")
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.storage import get_object_store, reset_object_store

    reset_object_store()
    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def test_backup_restore_mirror(client: TestClient, tmp_path) -> None:
    ws = _create_workspace(client, "Backup Restore")
    resp = client.post(
        f"/api/workspaces/{ws['id']}/objects/presigned-upload",
        json={"file_name": "doc.pdf", "mime_type": "application/pdf", "size_bytes": 12},
        headers={"x-tenant-id": "default", "x-user-id": "tester", "x-actor-id": "tester", "x-actor-role": "admin"},
    )
    payload = resp.json()
    from app.src.storage import get_object_store

    store = get_object_store()
    store.put_object(payload["bucket"], payload["object_key"], b"hello world", "application/pdf")

    # Simulate mc mirror: copy bucket contents to a backup path.
    backup_root = tmp_path / "backup"
    backup_root.mkdir()

    # Memory backend exposes _objects dict for inspection.
    for (bucket, key), data in store._backend._objects.items():
        if bucket == payload["bucket"]:
            path = backup_root / bucket / key
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)

    # Simulate restore: create a fresh memory store and copy data back.
    from app.src.storage import ObjectStore

    restored_store = ObjectStore("memory")
    for bucket_dir in backup_root.iterdir():
        bucket = bucket_dir.name
        for key_file in bucket_dir.rglob("*"):
            if key_file.is_file():
                key = str(key_file.relative_to(bucket_dir)).replace("\\", "/")
                restored_store._backend._objects[(bucket, key)] = key_file.read_bytes()

    assert restored_store.object_exists(payload["bucket"], payload["object_key"])
    assert restored_store.get_object(payload["bucket"], payload["object_key"]) == b"hello world"
