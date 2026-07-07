"""E3-0 — Tenant-scoped secret envelope encryption."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.src.context import Context
from app.src.security.secrets import (
    SecretError,
    TenantDataKey,
    TenantSecretStore,
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


def test_tenant_secret_store_roundtrip(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FABERLOOM_MASTER_KEY", "DV5NGDoFt9FuQaR4zN-jTBhYd-3m4BNqLWKmtZPRtxo=")
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))

    store = TenantSecretStore()
    ctx = Context(workspace_id="ws_1", tenant_id="tenant-a", user_id="user-a")
    envelope = store.encrypt_for_tenant(ctx, "sensitive-value")
    assert envelope is not None
    assert envelope.startswith("enc:v1:")
    assert store.decrypt_for_tenant(ctx, envelope) == "sensitive-value"


def test_tenant_secret_store_encrypts_none_as_none(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FABERLOOM_MASTER_KEY", "DV5NGDoFt9FuQaR4zN-jTBhYd-3m4BNqLWKmtZPRtxo=")
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))

    store = TenantSecretStore()
    ctx = Context(workspace_id="ws_1", tenant_id="tenant-a", user_id="user-a")
    assert store.encrypt_for_tenant(ctx, None) is None
    assert store.decrypt_for_tenant(ctx, None) is None


def test_tenant_secret_store_returns_plaintext_as_is(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FABERLOOM_MASTER_KEY", "DV5NGDoFt9FuQaR4zN-jTBhYd-3m4BNqLWKmtZPRtxo=")
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))

    store = TenantSecretStore()
    ctx = Context(workspace_id="ws_1", tenant_id="tenant-a", user_id="user-a")
    assert store.decrypt_for_tenant(ctx, "legacy-plaintext") == "legacy-plaintext"


def test_tenant_secret_store_isolates_tenants(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FABERLOOM_MASTER_KEY", "DV5NGDoFt9FuQaR4zN-jTBhYd-3m4BNqLWKmtZPRtxo=")
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))

    store = TenantSecretStore()
    ctx_a = Context(workspace_id="ws_1", tenant_id="tenant-a", user_id="user-a")
    ctx_b = Context(workspace_id="ws_1", tenant_id="tenant-b", user_id="user-a")
    envelope = store.encrypt_for_tenant(ctx_a, "secret-a")
    # Tenant b cannot decrypt tenant a's envelope.
    assert store.decrypt_for_tenant(ctx_b, envelope) == envelope


def test_tenant_secret_store_rotates_key(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FABERLOOM_MASTER_KEY", "DV5NGDoFt9FuQaR4zN-jTBhYd-3m4BNqLWKmtZPRtxo=")
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))

    store = TenantSecretStore()
    ctx = Context(workspace_id="ws_1", tenant_id="tenant-a", user_id="user-a")
    envelope1 = store.encrypt_for_tenant(ctx, "secret")
    key1 = store.get_or_create_data_key(ctx)

    key2 = store.rotate_tenant_key(ctx)
    assert key1.key_id != key2.key_id

    # Old ciphertext is still decryptable after rotation.
    assert store.decrypt_for_tenant(ctx, envelope1) == "secret"

    # New ciphertext uses the rotated key.
    envelope2 = store.encrypt_for_tenant(ctx, "secret")
    assert envelope2 != envelope1
    assert store.decrypt_for_tenant(ctx, envelope2) == "secret"
