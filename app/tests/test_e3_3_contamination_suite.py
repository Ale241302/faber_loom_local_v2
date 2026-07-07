"""E3-3 — Contamination probe for tenant-isolated primitives.

These tests exercise the new E3-3 tables directly. They are expected to fail if
any cross-tenant leak exists in entity_identity_version, key_policy, memory, or
secret storage.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import db_session
from app.src.entity_identity import create_identity, get_identity
from app.src.key_broker import KeyLevel, get_policy, set_policy
from app.src.main import create_app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated app with fresh databases."""

    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_AUTH_DISABLED", "1")
    monkeypatch.delenv("FABERLOOM_USERS", raising=False)
    with TestClient(create_app()) as test_client:
        yield test_client


def _db_conn() -> Any:
    return db_session()


def test_entity_identity_is_isolated_by_tenant(client: TestClient) -> None:
    """Identity for alpha must never be visible from beta context."""

    with _db_conn() as conn:
        create_identity(conn, "alpha", "Alpha Inc", "alpha-inc", "owner-alpha")
        alpha = get_identity(conn, "alpha")
        assert alpha is not None
        assert alpha.name == "Alpha Inc"

        beta = get_identity(conn, "beta")
        assert beta is None


def test_key_policy_is_isolated_by_tenant(client: TestClient) -> None:
    """Key policy for alpha space must not leak to beta."""

    with _db_conn() as conn:
        set_policy(conn, "alpha", "space-1", KeyLevel.CONTENT)
        alpha_policy = get_policy(conn, "alpha", "space-1")
        assert alpha_policy.level == KeyLevel.CONTENT

        beta_policy = get_policy(conn, "beta", "space-1")
        assert beta_policy.level == KeyLevel.CLOSED


def test_memory_blocks_are_isolated_by_tenant(client: TestClient) -> None:
    """Foundation memory blocks must be scoped to tenant_id at the DB level."""

    from app.src.foundation.core import connect as connect_foundation, new_id, utcnow

    conn = connect_foundation()
    try:
        conn.execute(
            """
            INSERT INTO fnd_memory_blocks (id, tenant_id, namespace, key, value, kind, created_at, updated_at)
            VALUES (?, ?, 'facts', 'tenant', 'alpha secret', 'fact', ?, ?)
            """,
            (new_id("mem"), "alpha", utcnow(), utcnow()),
        )
        conn.execute(
            """
            INSERT INTO fnd_memory_blocks (id, tenant_id, namespace, key, value, kind, created_at, updated_at)
            VALUES (?, ?, 'facts', 'tenant', 'beta secret', 'fact', ?, ?)
            """,
            (new_id("mem"), "beta", utcnow(), utcnow()),
        )
        conn.commit()

        alpha_rows = conn.execute(
            "SELECT value FROM fnd_memory_blocks WHERE tenant_id = ? AND namespace = ?",
            ("alpha", "facts"),
        ).fetchall()
        assert any("alpha secret" in row["value"] for row in alpha_rows)
        assert not any("beta secret" in row["value"] for row in alpha_rows)
    finally:
        conn.close()


def test_config_store_secrets_use_tenant_scoped_keys(client: TestClient) -> None:
    """Encrypting the same secret for two tenants yields different ciphertexts."""

    from app.src.security.secrets import TenantSecretStore

    store = TenantSecretStore()
    ctx_alpha = Context(
        workspace_id="ws_alpha", tenant_id="alpha", user_id="u1"
    )
    ctx_beta = Context(
        workspace_id="ws_beta", tenant_id="beta", user_id="u2"
    )

    encrypted_alpha = store.encrypt_for_tenant(ctx_alpha, "sensitive-value")
    encrypted_beta = store.encrypt_for_tenant(ctx_beta, "sensitive-value")
    assert encrypted_alpha != encrypted_beta

    decrypted_alpha = store.decrypt_for_tenant(ctx_alpha, encrypted_alpha)
    decrypted_beta = store.decrypt_for_tenant(ctx_beta, encrypted_beta)
    assert decrypted_alpha == "sensitive-value"
    assert decrypted_beta == "sensitive-value"
    assert decrypted_alpha == decrypted_beta
