"""Object storage abstraction for FaberLoom E2-6.

Supports two backends:
- ``minio``: real MinIO/S3-compatible backend (production).
- ``memory``: in-memory dictionary backend (tests / local dev without MinIO).

All workspace objects are stored under a workspace-scoped prefix so that the
API is the only place that can map an object id to a key and issue presigned
URLs. Buckets are never public.
"""

from __future__ import annotations

import hashlib
import os
from io import BytesIO
from typing import Any

from .db import new_id


UPLOAD_BUCKET = "fl-uploads"
GENERATED_BUCKET = "fl-generated"
OBJECT_ORIGINS = {"upload", "generated"}


class ObjectStoreError(Exception):
    """Raised when an object storage operation fails."""


class ObjectNotFoundError(ObjectStoreError):
    """Raised when an object is not found."""


def workspace_object_prefix(workspace_id: str) -> str:
    return f"ws-{workspace_id}"


def object_key(workspace_id: str, origin: str, file_name: str, object_id: str) -> str:
    if origin not in OBJECT_ORIGINS:
        raise ValueError(f"Invalid object origin: {origin}")
    prefix = workspace_object_prefix(workspace_id)
    safe_name = os.path.basename(file_name or "object")
    return f"{prefix}/{origin}/{object_id}/{safe_name}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _MemoryStoreBackend:
    """In-memory backend used by the test suite and local dev."""

    def __init__(self) -> None:
        self._objects: dict[tuple[str, str], bytes] = {}

    def put_object(
        self,
        bucket: str,
        key: str,
        data: bytes,
        length: int,
        content_type: str,
    ) -> dict[str, Any]:
        if len(data) != length:
            raise ObjectStoreError("data length does not match declared length")
        self._objects[(bucket, key)] = data
        return {"etag": sha256_bytes(data), "size": length}

    def get_object(self, bucket: str, key: str) -> bytes:
        try:
            return self._objects[(bucket, key)]
        except KeyError as exc:
            raise ObjectNotFoundError(f"Object not found: {bucket}/{key}") from exc

    def delete_object(self, bucket: str, key: str) -> None:
        self._objects.pop((bucket, key), None)

    def object_exists(self, bucket: str, key: str) -> bool:
        return (bucket, key) in self._objects

    def presigned_put_url(
        self, bucket: str, key: str, content_type: str, expires: int = 3600
    ) -> str:
        return f"memory://{bucket}/{key}?expires={expires}"

    def presigned_get_url(self, bucket: str, key: str, expires: int = 3600) -> str:
        return f"memory://{bucket}/{key}?expires={expires}"


class _MinioStoreBackend:
    """MinIO-backed object store."""

    def __init__(self) -> None:
        from minio import Minio  # type: ignore[import-untyped]

        endpoint = os.getenv("FL_MINIO_ENDPOINT", "localhost:9000")
        access_key = os.getenv("FL_MINIO_ACCESS_KEY", "")
        secret_key = os.getenv("FL_MINIO_SECRET_KEY", "")
        secure = os.getenv("FL_MINIO_SECURE", "false").lower() in {"true", "1", "yes"}

        if not access_key or not secret_key:
            raise ObjectStoreError(
                "FL_MINIO_ACCESS_KEY and FL_MINIO_SECRET_KEY are required"
            )

        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
        )

    def _ensure_bucket(self, bucket: str) -> None:
        if not self._client.bucket_exists(bucket):
            self._client.make_bucket(bucket)

    def ensure_buckets(self) -> None:
        self._ensure_bucket(UPLOAD_BUCKET)
        self._ensure_bucket(GENERATED_BUCKET)

    def put_object(
        self,
        bucket: str,
        key: str,
        data: bytes,
        length: int,
        content_type: str,
    ) -> dict[str, Any]:
        self._ensure_bucket(bucket)
        result = self._client.put_object(
            bucket,
            key,
            BytesIO(data),
            length,
            content_type=content_type,
        )
        return {"etag": result.etag, "size": length}

    def get_object(self, bucket: str, key: str) -> bytes:
        try:
            response = self._client.get_object(bucket, key)
            return response.read()
        except Exception as exc:
            raise ObjectNotFoundError(f"Object not found: {bucket}/{key}") from exc

    def delete_object(self, bucket: str, key: str) -> None:
        try:
            self._client.remove_object(bucket, key)
        except Exception as exc:
            raise ObjectStoreError(f"Failed to delete {bucket}/{key}: {exc}") from exc

    def object_exists(self, bucket: str, key: str) -> bool:
        try:
            self._client.stat_object(bucket, key)
            return True
        except Exception:
            return False

    def presigned_put_url(
        self, bucket: str, key: str, content_type: str, expires: int = 3600
    ) -> str:
        self._ensure_bucket(bucket)
        return self._client.presigned_put_object(
            bucket, key, expires=expires,
        )

    def presigned_get_url(self, bucket: str, key: str, expires: int = 3600) -> str:
        return self._client.presigned_get_object(bucket, key, expires=expires)


class ObjectStore:
    """High-level object store with workspace-scoped keys."""

    def __init__(self, backend: str | None = None) -> None:
        backend_env = os.getenv("FL_STORAGE_BACKEND")
        backend = (backend or backend_env or "minio").lower()
        if backend == "memory":
            self._backend: _MinioStoreBackend | _MemoryStoreBackend = _MemoryStoreBackend()
        elif backend == "minio":
            try:
                self._backend = _MinioStoreBackend()
            except ObjectStoreError:
                # If the operator did not explicitly request MinIO and no
                # credentials are configured, fall back to an in-memory store so
                # local tests and dev runs keep working without a MinIO server.
                if backend_env is None:
                    import warnings

                    warnings.warn(
                        "MinIO credentials not configured; falling back to memory object store",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    self._backend = _MemoryStoreBackend()
                else:
                    raise
        else:
            raise ObjectStoreError(f"Unsupported storage backend: {backend}")

    def ensure_buckets(self) -> None:
        if hasattr(self._backend, "ensure_buckets"):
            self._backend.ensure_buckets()

    def put_object(
        self,
        bucket: str,
        key: str,
        data: bytes,
        content_type: str,
    ) -> dict[str, Any]:
        return self._backend.put_object(bucket, key, data, len(data), content_type)

    def get_object(self, bucket: str, key: str) -> bytes:
        return self._backend.get_object(bucket, key)

    def delete_object(self, bucket: str, key: str) -> None:
        self._backend.delete_object(bucket, key)

    def object_exists(self, bucket: str, key: str) -> bool:
        return self._backend.object_exists(bucket, key)

    def presigned_upload_url(
        self, bucket: str, key: str, content_type: str, expires: int = 3600
    ) -> str:
        return self._backend.presigned_put_url(bucket, key, content_type, expires=expires)

    def presigned_download_url(
        self, bucket: str, key: str, expires: int = 3600
    ) -> str:
        return self._backend.presigned_get_url(bucket, key, expires=expires)

    def workspace_prefix(self, workspace_id: str) -> str:
        return workspace_object_prefix(workspace_id)


# Global singleton ---------------------------------------------------------

_store: ObjectStore | None = None


def get_object_store() -> ObjectStore:
    """Return the global object store instance."""
    global _store
    if _store is None:
        _store = ObjectStore()
    return _store


def set_object_store(store: ObjectStore) -> None:
    """Override the global store (used by tests)."""
    global _store
    _store = store


def reset_object_store() -> None:
    """Reset the global store so the next call creates a fresh instance."""
    global _store
    _store = None
