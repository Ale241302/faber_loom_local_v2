"""Tenant-scoped secret management for E3-0/E3-3.

Provides envelope encryption: a platform master key protects per-tenant data
keys, and each data key protects the tenant's sensitive records (provider keys,
SMTP passwords, object payloads). The agent never handles the master key
directly; it only asks this module to encrypt/decrypt blobs scoped to a tenant.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken


class SecretError(Exception):
    """Raised when a secret operation cannot be completed safely."""


# Lazily imported to avoid a circular import with router.config_store.
def _master_key() -> bytes:
    from ..router.config_store import get_master_key

    return get_master_key()


def _derive_key(master: bytes, tenant_id: str, key_id: str) -> bytes:
    """Deterministically derive a Fernet key from the master key and labels."""

    material = hashlib.sha256(master + tenant_id.encode("utf-8") + key_id.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(material)


def generate_data_key_id() -> str:
    """Return a new random data-key identifier."""

    return base64.urlsafe_b64encode(os.urandom(16)).decode("ascii").rstrip("=")


@dataclass(frozen=True, slots=True)
class TenantDataKey:
    """A tenant-specific data encryption key wrapped by the platform master key."""

    tenant_id: str
    key_id: str
    encrypted_key: str  # Fernet(master).encrypt(raw_data_key)

    @classmethod
    def create(cls, tenant_id: str, master_key: bytes | None = None) -> "TenantDataKey":
        """Generate a new data key for ``tenant_id`` and wrap it with the master key."""

        key_id = generate_data_key_id()
        raw_key = Fernet.generate_key()
        master = master_key or _master_key()
        encrypted = Fernet(master).encrypt(raw_key).decode("utf-8")
        return cls(tenant_id=tenant_id, key_id=key_id, encrypted_key=encrypted)

    def unwrap(self, master_key: bytes | None = None) -> bytes:
        """Return the raw data key after unwrapping it with the master key."""

        master = master_key or _master_key()
        try:
            return Fernet(master).decrypt(self.encrypted_key.encode("utf-8"))
        except InvalidToken as exc:
            raise SecretError("Data key unwrap failed; master key mismatch or tampering") from exc

    def encrypt_blob(self, plaintext: str | bytes, master_key: bytes | None = None) -> str:
        """Encrypt a plaintext blob with this tenant data key."""

        data_key = self.unwrap(master_key)
        payload = plaintext.encode("utf-8") if isinstance(plaintext, str) else plaintext
        return Fernet(data_key).encrypt(payload).decode("utf-8")

    def decrypt_blob(self, ciphertext: str, master_key: bytes | None = None) -> bytes:
        """Decrypt a ciphertext blob with this tenant data key."""

        data_key = self.unwrap(master_key)
        try:
            return Fernet(data_key).decrypt(ciphertext.encode("utf-8"))
        except InvalidToken as exc:
            raise SecretError("Tenant blob decryption failed; data key mismatch or tampering") from exc

    def rotate(self, master_key: bytes | None = None) -> "TenantDataKey":
        """Return a new data key for the same tenant, suitable for re-encryption."""

        return self.__class__.create(self.tenant_id, master_key=master_key or _master_key())


def encrypt_value_for_tenant(
    tenant_id: str,
    value: str | None,
    data_key: TenantDataKey | None = None,
) -> tuple[str | None, TenantDataKey]:
    """Encrypt ``value`` for ``tenant_id``.

    If ``data_key`` is not provided, a new one is created. Returns the ciphertext
    and the data key that must be persisted (the ciphertext alone is useless
    without the wrapped key).
    """

    if value is None:
        return None, data_key or TenantDataKey.create(tenant_id)
    key = data_key or TenantDataKey.create(tenant_id)
    return key.encrypt_blob(value), key


def decrypt_value_for_tenant(ciphertext: str, data_key: TenantDataKey) -> str:
    """Decrypt a ciphertext using the tenant data key."""

    return data_key.decrypt_blob(ciphertext).decode("utf-8")


def row_to_dict(row: Any) -> dict[str, Any]:
    """Normalise a sqlite3.Row / psycopg row to a plain dict."""

    if hasattr(row, "_asdict"):
        return row._asdict()
    if hasattr(row, "keys"):
        return {k: row[k] for k in row.keys()}
    return dict(row)


# ---------------------------------------------------------------------------
# TenantSecretStore: high-level Context-aware secret storage
# ---------------------------------------------------------------------------

_ENVELOPE_PREFIX = "enc:v1:"


def _default_key_path() -> Path:
    """Return the default path for the tenant data-key repository.

    Lazily imported so ``security.secrets`` can be loaded by ``router.config_store``
    without a circular import.
    """

    from ..router.config_store import get_config_dir

    return get_config_dir() / "tenant_keys.json"


class _TenantKeyRepository:
    """Simple JSON file repository for tenant data encryption keys.

    Each tenant may have multiple keys (currently active + rotated older keys)
    so existing ciphertext can still be decrypted after rotation.
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or _default_key_path()

    def _load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            # A corrupted key file is treated as empty. Existing encrypted values
            # will fail to decrypt, which surfaces the problem instead of hiding
            # it under a fallback.
            return {}

    def _save(self, data: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def _records_for(self, tenant_id: str) -> list[dict[str, Any]]:
        data = self._load()
        records = data.get(tenant_id)
        if not isinstance(records, list):
            return []
        return [r for r in records if isinstance(r, dict)]

    def _record_to_key(self, record: dict[str, Any]) -> TenantDataKey:
        return TenantDataKey(
            tenant_id=record["tenant_id"],
            key_id=record["key_id"],
            encrypted_key=record["encrypted_key"],
        )

    def get_or_create_data_key(self, tenant_id: str) -> TenantDataKey:
        """Return the active data key for ``tenant_id``, creating one if needed."""

        records = self._records_for(tenant_id)
        if records:
            return self._record_to_key(records[-1])

        key = TenantDataKey.create(tenant_id)
        record = {
            "tenant_id": key.tenant_id,
            "key_id": key.key_id,
            "encrypted_key": key.encrypted_key,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data = self._load()
        data.setdefault(tenant_id, []).append(record)
        self._save(data)
        return key

    def get_data_key(self, tenant_id: str, key_id: str) -> TenantDataKey | None:
        """Return a specific data key by id, or None if it is unknown."""

        for record in self._records_for(tenant_id):
            if record.get("key_id") == key_id:
                return self._record_to_key(record)
        return None

    def rotate_data_key(self, tenant_id: str) -> TenantDataKey:
        """Create and persist a new active data key for ``tenant_id``."""

        key = TenantDataKey.create(tenant_id)
        record = {
            "tenant_id": key.tenant_id,
            "key_id": key.key_id,
            "encrypted_key": key.encrypted_key,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        data = self._load()
        data.setdefault(tenant_id, []).append(record)
        self._save(data)
        return key


class TenantSecretStore:
    """High-level, Context-aware tenant-scoped secret store.

    Callers pass a :class:`~app.src.context.Context` and a plaintext value;
    persistence of the per-tenant data key is handled internally. Encrypted
    values carry their own key id so they can be decrypted even after key
    rotation, as long as the old key is still in the repository.
    """

    def __init__(self, key_repository: _TenantKeyRepository | None = None) -> None:
        self._repo = key_repository or _TenantKeyRepository()

    def _tenant_id(self, ctx: Any) -> str:
        from ..context import DEFAULT_TENANT_ID

        return getattr(ctx, "tenant_id", None) or DEFAULT_TENANT_ID

    def get_or_create_data_key(self, ctx: Any) -> TenantDataKey:
        """Return the active tenant data key for ``ctx``.

        This is exposed so storage-layer helpers can obtain a tenant key for
        client-side metadata or payload encryption.
        """

        return self._repo.get_or_create_data_key(self._tenant_id(ctx))

    def encrypt_for_tenant(self, ctx: Any, plaintext: str | None) -> str | None:
        """Encrypt ``plaintext`` scoped to the tenant in ``ctx``.

        Returns ``None`` for ``None`` input so nullable secrets stay null.
        The returned envelope includes the key id and a version prefix so
        :meth:`decrypt_for_tenant` can detect it and legacy plaintext can be
        read transparently.
        """

        if plaintext is None:
            return None
        tenant_id = self._tenant_id(ctx)
        key = self._repo.get_or_create_data_key(tenant_id)
        ciphertext = key.encrypt_blob(plaintext)
        return f"{_ENVELOPE_PREFIX}{key.key_id}:{ciphertext}"

    def decrypt_for_tenant(self, ctx: Any, envelope: str | None) -> str | None:
        """Decrypt an envelope created by :meth:`encrypt_for_tenant`.

        If ``envelope`` is ``None`` or does not carry the encrypted prefix, it
        is returned as-is. This provides a backward-compatible read path for
        legacy plaintext values; the next write will persist them encrypted.
        """

        if envelope is None:
            return None
        if not isinstance(envelope, str) or not envelope.startswith(_ENVELOPE_PREFIX):
            return envelope
        payload = envelope[len(_ENVELOPE_PREFIX) :]
        if ":" not in payload:
            return envelope
        key_id, ciphertext = payload.split(":", 1)
        key = self._repo.get_data_key(self._tenant_id(ctx), key_id)
        if key is None:
            return envelope
        try:
            return key.decrypt_blob(ciphertext).decode("utf-8")
        except SecretError:
            return envelope

    def rotate_tenant_key(self, ctx: Any) -> TenantDataKey:
        """Rotate the active data key for the tenant in ``ctx``."""

        return self._repo.rotate_data_key(self._tenant_id(ctx))
