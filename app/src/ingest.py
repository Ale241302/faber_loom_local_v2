"""Universal ingestion pipelines for E2-6.

Extractors turn supported binary/text formats into plain text that can be
chunked and fed to the router.  Heavy engines (OCR, speech-to-text) are
optional; if they are missing and the workspace requires local-only processing,
the pipeline returns an honest error instead of leaking content to a cloud model.
"""

from __future__ import annotations

import io
import json
import sqlite3
from typing import Any

from .context import Context
from .db import get_object, get_routing_policy
from .storage import get_object_store


class IngestError(Exception):
    """Raised when an object cannot be ingested."""


class LocalOnlyEngineMissingError(IngestError):
    """Raised when a local engine is required but not installed."""


_INGEST_MIME_MAP = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/msword": "docx",
    "application/json": "json",
    "application/sql": "sql",
    "text/x-sql": "sql",
    "application/x-sql": "sql",
    "image/png": "image",
    "image/jpeg": "image",
    "image/gif": "image",
    "image/webp": "image",
    "image/bmp": "image",
    "image/tiff": "image",
    "audio/mpeg": "audio",
    "audio/mp4": "audio",
    "audio/wav": "audio",
    "audio/x-wav": "audio",
    "audio/ogg": "audio",
    "audio/webm": "audio",
    "video/mp4": "video",
    "video/webm": "video",
    "video/ogg": "video",
    "video/quicktime": "video",
    "video/x-matroska": "video",
}


def _workspace_requires_local_only(ctx: Context, conn: sqlite3.Connection) -> bool:
    policy = get_routing_policy(ctx, conn)
    return bool(policy.get("require_local_only", 0))


def _read_object_blob(ctx: Context, conn: sqlite3.Connection, object_id: str) -> bytes:
    obj = get_object(ctx, conn, object_id)
    if obj is None:
        raise IngestError(f"Object {object_id} not found")
    store = get_object_store()
    try:
        return store.get_object(obj["bucket"], obj["object_key"])
    except Exception as exc:
        raise IngestError(f"Failed to read object {object_id} from storage: {exc}") from exc


def _detect_ingest_type(mime_type: str | None, file_name: str | None) -> str:
    lowered = (mime_type or "").lower()
    if lowered in _INGEST_MIME_MAP:
        return _INGEST_MIME_MAP[lowered]
    # Fallback by extension.
    ext = (file_name or "").rsplit(".", 1)[-1].lower()
    ext_map = {
        "docx": "docx",
        "json": "json",
        "sql": "sql",
        "png": "image",
        "jpg": "image",
        "jpeg": "image",
        "gif": "image",
        "webp": "image",
        "bmp": "image",
        "tiff": "image",
        "mp3": "audio",
        "m4a": "audio",
        "wav": "audio",
        "ogg": "audio",
        "weba": "audio",
        "mp4": "video",
        "webm": "video",
        "ogv": "video",
        "mov": "video",
        "mkv": "video",
    }
    return ext_map.get(ext, lowered.split("/")[-1].split("+")[0])


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------


def _extract_docx(blob: bytes) -> str:
    try:
        import docx  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover - optional dependency
        raise LocalOnlyEngineMissingError("python-docx no está instalado") from exc

    document = docx.Document(io.BytesIO(blob))
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    tables_text = []
    for table in document.tables:
        rows = []
        for row in table.rows:
            rows.append(" | ".join(cell.text for cell in row.cells))
        if rows:
            tables_text.append("\n".join(rows))
    parts = paragraphs
    if tables_text:
        parts.append("---TABLAS---")
        parts.extend(tables_text)
    return "\n\n".join(parts)


def _extract_json(blob: bytes) -> str:
    try:
        text = blob.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IngestError("JSON file is not valid UTF-8") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise IngestError(f"Invalid JSON: {exc}") from exc
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)


def _extract_sql(blob: bytes) -> str:
    try:
        return blob.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise IngestError("SQL file is not valid UTF-8") from exc


def _extract_image(blob: bytes, require_local: bool) -> str:
    try:
        from PIL import Image  # type: ignore[import-untyped]
        import pytesseract  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover - optional dependency
        if require_local:
            raise LocalOnlyEngineMissingError(
                "OCR local no disponible (instalar pytesseract + Pillow)"
            ) from exc
        raise LocalOnlyEngineMissingError("OCR local no disponible") from exc

    try:
        image = Image.open(io.BytesIO(blob))
        return pytesseract.image_to_string(image).strip()
    except Exception as exc:
        raise IngestError(f"OCR failed: {exc}") from exc


def _extract_audio(blob: bytes, require_local: bool) -> str:
    try:
        import whisper  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover - optional dependency
        if require_local:
            raise LocalOnlyEngineMissingError(
                "Transcripción local no disponible (instalar openai-whisper)"
            ) from exc
        raise LocalOnlyEngineMissingError("Transcripción local no disponible") from exc

    try:
        with io.BytesIO(blob) as src:
            # whisper expects a file path or numpy array; passing a file-like works with the API.
            model = whisper.load_model("base")
            result = model.transcribe(src)
        return result.get("text", "").strip()
    except Exception as exc:
        raise IngestError(f"Transcription failed: {exc}") from exc


def _extract_video(blob: bytes, require_local: bool) -> str:
    # Naive first pass: treat as audio extraction via whisper.
    # A production pipeline would separate audio with ffmpeg first.
    return _extract_audio(blob, require_local)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_text_from_blob(
    *,
    blob: bytes,
    ingest_type: str,
    require_local: bool = False,
) -> str:
    """Return extracted text from a binary blob.

    Raises ``LocalOnlyEngineMissingError`` when a local engine is required but
    not installed; raises ``IngestError`` for malformed or unsupported content.
    """

    if ingest_type == "docx":
        return _extract_docx(blob)
    if ingest_type == "json":
        return _extract_json(blob)
    if ingest_type == "sql":
        return _extract_sql(blob)
    if ingest_type == "image":
        return _extract_image(blob, require_local)
    if ingest_type == "audio":
        return _extract_audio(blob, require_local)
    if ingest_type == "video":
        return _extract_video(blob, require_local)
    raise IngestError(f"Unsupported ingest type: {ingest_type}")


def extract_text_from_object(
    ctx: Context,
    conn: sqlite3.Connection,
    object_id: str,
) -> dict[str, Any]:
    """Read an object from MinIO and extract ingestible text.

    Returns a dict with ``object_id``, ``file_name``, ``mime_type``,
    ``ingest_type``, ``text`` and ``error`` (None on success).
    """

    obj = get_object(ctx, conn, object_id)
    if obj is None:
        return {"object_id": object_id, "error": "Object not found"}

    blob = _read_object_blob(ctx, conn, object_id)
    ingest_type = _detect_ingest_type(obj.get("mime_type"), obj.get("file_name"))
    require_local = _workspace_requires_local_only(ctx, conn)

    try:
        text = extract_text_from_blob(
            blob=blob,
            ingest_type=ingest_type,
            require_local=require_local,
        )
        return {
            "object_id": object_id,
            "file_name": obj.get("file_name"),
            "mime_type": obj.get("mime_type"),
            "ingest_type": ingest_type,
            "text": text,
            "error": None,
        }
    except LocalOnlyEngineMissingError as exc:
        return {
            "object_id": object_id,
            "file_name": obj.get("file_name"),
            "mime_type": obj.get("mime_type"),
            "ingest_type": ingest_type,
            "text": "",
            "error": f"LOCAL_ENGINE_MISSING: {exc}",
        }
    except IngestError as exc:
        return {
            "object_id": object_id,
            "file_name": obj.get("file_name"),
            "mime_type": obj.get("mime_type"),
            "ingest_type": ingest_type,
            "text": "",
            "error": f"INGEST_ERROR: {exc}",
        }
