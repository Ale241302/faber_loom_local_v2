"""E3-3 — Envelope encryption by tenant."""

from __future__ import annotations

import pytest

from app.src.crypto.envelope import (
    SecretError,
    TenantDataKey,
    envelope_decrypt,
    envelope_encrypt,
    rotate_data_key,
)


@pytest.fixture(autouse=True)
def _master_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "FABERLOOM_MASTER_KEY",
        "DV5NGDoFt9FuQaR4zN-jTBhYd-3m4BNqLWKmtZPRtxo=",
    )


def test_envelope_roundtrip() -> None:
    ciphertext, key = envelope_encrypt("tenant-a", "plain text")
    assert envelope_decrypt(ciphertext, key) == "plain text"


def test_keys_are_tenant_isolated() -> None:
    _, key_a = envelope_encrypt("tenant-a", "secret")
    ciphertext_b, _ = envelope_encrypt("tenant-b", "other")
    with pytest.raises(SecretError):
        envelope_decrypt(ciphertext_b, key_a)


def test_rotate_data_key() -> None:
    _, key1 = envelope_encrypt("tenant-a", "x")
    key2 = rotate_data_key(key1)
    assert key1.key_id != key2.key_id
    assert key2.tenant_id == "tenant-a"
