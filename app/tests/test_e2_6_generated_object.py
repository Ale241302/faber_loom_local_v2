"""Tests for E2-6 generated object persistence."""

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
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.storage import reset_object_store

    reset_object_store()
    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def test_presigned_upload_origin_generated(client: TestClient) -> None:
    ws = _create_workspace(client, "Generated Object")
    resp = client.post(
        f"/api/workspaces/{ws['id']}/objects/presigned-upload",
        json={"file_name": "image.png", "mime_type": "image/png", "size_bytes": 1024, "origin": "generated"},
        headers={"x-tenant-id": "default", "x-user-id": "tester", "x-actor-id": "tester", "x-actor-role": "admin"},
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["bucket"] == "fl-generated"
    assert f"ws-{ws['id']}/generated/" in data["object_key"]
