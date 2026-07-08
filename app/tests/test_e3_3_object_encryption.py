"""E3-3 — Object payloads are encrypted at rest with the tenant data key (P0-7)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

_HEADERS = {
    "x-tenant-id": "default",
    "x-user-id": "tester",
    "x-actor-id": "tester",
    "x-actor-role": "owner",
}


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.storage import reset_object_store

    reset_object_store()
    audit_writer.audit_path = tmp_path / "audit.jsonl"
    with TestClient(create_app()) as test_client:
        yield test_client


def _create_workspace(client: TestClient) -> str:
    resp = client.post("/api/workspaces", json={"name": "Docs"}, headers=_HEADERS)
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_encrypt_decrypt_roundtrip_and_legacy_passthrough(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.storage import decrypt_object_payload, encrypt_object_payload, is_encrypted_payload

    ctx = Context(workspace_id="ws1", tenant_id="default", user_id="u1")
    plaintext = b"binary \x00\x01 secret payload"

    blob = encrypt_object_payload(ctx, plaintext)
    assert is_encrypted_payload(blob)
    assert plaintext not in blob  # never at rest in the clear
    assert decrypt_object_payload(ctx, blob) == plaintext

    # Legacy objects stored before this feature (no prefix) pass through untouched.
    assert decrypt_object_payload(ctx, b"legacy plaintext") == b"legacy plaintext"


def test_upload_is_encrypted_at_rest_and_readable_via_api(client: TestClient) -> None:
    from app.src.storage import get_object_store

    workspace_id = _create_workspace(client)
    secret = b"El precio de Oxford es USD 12.50 por metro.\n"

    resp = client.post(
        f"/api/workspaces/{workspace_id}/kb/upload",
        data={"title": "Precios"},
        files={"file": ("precios.md", secret, "text/markdown")},
        headers=_HEADERS,
    )
    assert resp.status_code == 201, resp.text
    source = resp.json()

    # 1) At rest in MinIO the payload is ciphertext, never the plaintext.
    store = get_object_store()
    blobs = list(store._backend._objects.items())  # type: ignore[attr-defined]
    assert blobs, "object was not stored"
    assert all(blob.startswith(b"FLENC1:") for _, blob in blobs)
    assert all(secret not in blob for _, blob in blobs)

    # 2) Ingestion decrypted the payload (the KB source carries the real text).
    assert "12.50" in (source.get("content_text") or "")

    # 3) The API-proxied content endpoint returns the decrypted bytes.
    (bucket, object_key), _ = blobs[0]
    object_id = object_key.split("/upload/")[1].split("/")[0]

    content = client.get(
        f"/api/workspaces/{workspace_id}/objects/{object_id}/content", headers=_HEADERS
    )
    assert content.status_code == 200, content.text
    assert b"12.50" in content.content

    # 4) The download-URL endpoint routes encrypted uploads through the proxy.
    url_resp = client.get(
        f"/api/workspaces/{workspace_id}/objects/{object_id}/url", headers=_HEADERS
    )
    assert url_resp.status_code == 200, url_resp.text
    assert "/content" in url_resp.json()["download_url"]
