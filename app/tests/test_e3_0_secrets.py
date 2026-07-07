"""E3-0 — Tenant-scoped secret envelope encryption."""

from __future__ import annotations

import os

import pytest

from app.src.security.secrets import (
    SecretError,
    TenantDataKey,
    decrypt_value_for_tenant,
    encrypt_value_for_tenant,
)


@pytest.fixture(autouse=True)
def _master_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide a deterministic master key for every test."""

    monkeypatch.setenv(
        "FABERLOOM_MASTER_KEY",
        "DV5NGDoFt9FuQaR4zN-jTBhYd-3m4BNqLWKmtZPRtxo=",
    )


def test_tenant_data_key_roundtrip() -> None:
    key = TenantDataKey.create("tenant-a")
    ciphertext = key.encrypt_blob("sensitive-value")
    assert key.decrypt_blob(ciphertext).decode("utf-8") == "sensitive-value"


def test_tenant_keys_are_isolated() -> None:
    key_a = TenantDataKey.create("tenant-a")
    key_b = TenantDataKey.create("tenant-b")
    ciphertext = key_a.encrypt_blob("secret-a")
    with pytest.raises(SecretError):
        key_b.decrypt_blob(ciphertext)


def test_wrapped_key_cannot_be_decrypted_with_wrong_master() -> None:
    key = TenantDataKey.create("tenant-a")
    with pytest.raises(SecretError):
        key.decrypt_blob("invalid-ciphertext")


def test_encrypt_decrypt_helpers() -> None:
    ciphertext, key = encrypt_value_for_tenant("tenant-a", "plain")
    assert ciphertext is not None
    assert decrypt_value_for_tenant(ciphertext, key) == "plain"


def test_encrypt_none_returns_none() -> None:
    ciphertext, key = encrypt_value_for_tenant("tenant-a", None)
    assert ciphertext is None
    assert key.tenant_id == "tenant-a"


def test_master_key_from_env() -> None:
    os.environ["FABERLOOM_MASTER_KEY"] = "DV5NGDoFt9FuQaR4zN-jTBhYd-3m4BNqLWKmtZPRtxo="
    key = TenantDataKey.create("tenant-c")
    assert key.encrypt_blob("x")
