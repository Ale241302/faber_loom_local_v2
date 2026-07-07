"""Envelope encryption layer for tenant data (E3-3).

Each tenant has its own data encryption key (DEK). The DEK itself is encrypted
by the platform master key and stored alongside the tenant metadata. Sensitive
records are encrypted with the DEK, so a compromised single DEK only exposes one
tenant.
"""

from __future__ import annotations

from typing import Any

from ..security.secrets import SecretError, TenantDataKey


__all__ = ["TenantDataKey", "SecretError", "envelope_encrypt", "envelope_decrypt", "rotate_data_key"]


def envelope_encrypt(
    tenant_id: str,
    plaintext: str,
    data_key: TenantDataKey | None = None,
) -> tuple[str, TenantDataKey]:
    """Encrypt ``plaintext`` for ``tenant_id`` and return (ciphertext, data_key)."""

    key = data_key or TenantDataKey.create(tenant_id)
    return key.encrypt_blob(plaintext), key


def envelope_decrypt(ciphertext: str, data_key: TenantDataKey) -> str:
    """Decrypt ``ciphertext`` using the tenant data key."""

    return data_key.decrypt_blob(ciphertext).decode("utf-8")


def rotate_data_key(data_key: TenantDataKey) -> TenantDataKey:
    """Return a fresh data key for the same tenant.

    After rotation, existing ciphertexts must be re-encrypted with the new key
    and the old key record marked as superseded.
    """

    return data_key.rotate()


def row_to_data_key(row: Any) -> TenantDataKey:
    """Reconstruct a TenantDataKey from a database row."""

    return TenantDataKey(
        tenant_id=row["tenant_id"],
        key_id=row["key_id"],
        encrypted_key=row["encrypted_key"],
    )
