"""E3-0: faster-whisper integration tests (mocked)."""

from __future__ import annotations

import sys
from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient


class _FakeSegment:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeWhisperModel:
    def __init__(self, model_name: str, device: str, compute_type: str) -> None:
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type

    def transcribe(self, audio: Any) -> tuple[list[_FakeSegment], dict[str, Any]]:
        return (
            [_FakeSegment("hola mundo"), _FakeSegment("desde audio")],
            {"language": "es", "probability": 0.99},
        )


def _install_fake_faster_whisper(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_module = MagicMock()
    fake_module.WhisperModel = _FakeWhisperModel
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_module)


class _MissingFasterWhisper:
    def __getattr__(self, _name: str) -> Any:
        raise ModuleNotFoundError("No module named 'faster_whisper'")


def _broken_faster_whisper_module() -> _MissingFasterWhisper:
    return _MissingFasterWhisper()


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


def _create_workspace(client: TestClient, name: str) -> dict[str, Any]:
    resp = client.post(
        "/api/workspaces",
        json={"name": name},
        headers={
            "x-tenant-id": "default",
            "x-user-id": "tester",
            "x-actor-id": "tester",
            "x-actor-role": "admin",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _upload_object(
    client: TestClient,
    workspace_id: str,
    file_name: str,
    mime_type: str,
    data: bytes,
) -> str:
    resp = client.post(
        f"/api/workspaces/{workspace_id}/objects/presigned-upload",
        json={"file_name": file_name, "mime_type": mime_type, "size_bytes": len(data)},
        headers={
            "x-tenant-id": "default",
            "x-user-id": "tester",
            "x-actor-id": "tester",
            "x-actor-role": "admin",
        },
    )
    assert resp.status_code == 201, resp.text
    payload = resp.json()
    from app.src.storage import get_object_store

    store = get_object_store()
    store.put_object(payload["bucket"], payload["object_key"], data, mime_type)
    confirm = client.post(
        f"/api/workspaces/{workspace_id}/objects/confirm",
        json={"object_id": payload["object_id"], "size_bytes": len(data)},
        headers={
            "x-tenant-id": "default",
            "x-user-id": "tester",
            "x-actor-id": "tester",
            "x-actor-role": "admin",
        },
    )
    assert confirm.status_code == 200, confirm.text
    return payload["object_id"]


def test_extract_audio_transcribes_with_mocked_whisper(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_faster_whisper(monkeypatch)
    from app.src.ingest import extract_text_from_blob

    text = extract_text_from_blob(blob=b"fake audio bytes", ingest_type="audio")
    assert "hola mundo" in text
    assert "desde audio" in text


def test_extract_video_uses_audio_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    _install_fake_faster_whisper(monkeypatch)
    from app.src.ingest import extract_text_from_blob

    text = extract_text_from_blob(blob=b"fake video bytes", ingest_type="video")
    assert "hola mundo" in text


def test_extract_audio_raises_when_whisper_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "faster_whisper", _broken_faster_whisper_module())
    from app.src.ingest import LocalOnlyEngineMissingError, extract_text_from_blob

    with pytest.raises(LocalOnlyEngineMissingError) as exc_info:
        extract_text_from_blob(blob=b"fake audio bytes", ingest_type="audio")
    assert "faster-whisper" in str(exc_info.value).lower()


def test_audio_kb_source_is_chunked_and_searchable(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_faster_whisper(monkeypatch)
    ws = _create_workspace(client, "Audio KB")
    obj_id = _upload_object(client, ws["id"], "meeting.mp3", "audio/mpeg", b"fake mp3 bytes")

    resp = client.post(
        f"/api/workspaces/{ws['id']}/kb/sources",
        json={"title": "Reunión", "type": "audio", "object_id": obj_id},
        headers={
            "x-tenant-id": "default",
            "x-user-id": "tester",
            "x-actor-id": "tester",
            "x-actor-role": "admin",
        },
    )
    assert resp.status_code == 201, resp.text
    source = resp.json()
    assert source["type"] == "audio"
    assert "hola mundo" in source["content_text"]

    search = client.get(
        f"/api/workspaces/{ws['id']}/kb/search?q=mundo",
        headers={
            "x-tenant-id": "default",
            "x-user-id": "tester",
            "x-actor-id": "tester",
            "x-actor-role": "admin",
        },
    )
    assert search.status_code == 200, search.text
    data = search.json()
    assert any("mundo" in chunk["content_text"] for chunk in data["chunks"])


def test_audio_upload_returns_422_when_whisper_missing(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "faster_whisper", _broken_faster_whisper_module())
    ws = _create_workspace(client, "Audio Missing")

    resp = client.post(
        f"/api/workspaces/{ws['id']}/kb/upload",
        data={"title": "Reunión"},
        files={"file": ("meeting.mp3", b"fake mp3 bytes", "audio/mpeg")},
    )
    assert resp.status_code == 422, resp.text
    assert "faster-whisper" in resp.text.lower()
