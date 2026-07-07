"""Tenant-scoped secret management for E3-0/E3-3.

Provides envelope encryption: a platform master key protects per-tenant data
keys, and each data key protects the tenant's sensitive records (provider keys,
SMTP passwords, object payloads). The agent never handles the master key
directly; it only asks this module to encrypt/decrypt blobs scoped to a tenant.
"""

from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
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
