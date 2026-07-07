"""E3-3 — Immutable tenant entity identity."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from app.src.entity_identity import IdentityError, create_identity, get_identity, update_identity


@pytest.fixture(autouse=True)
def _master_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "FABERLOOM_MASTER_KEY",
        "DV5NGDoFt9FuQaR4zN-jTBhYd-3m4BNqLWKmtZPRtxo=",
    )


@pytest.fixture()
def conn():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.sqlite3"
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        conn.executescript(
            """
            CREATE TABLE entity_identity_version (
                tenant_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                name TEXT NOT NULL,
                slug TEXT NOT NULL,
                tax_id TEXT,
                jurisdiction TEXT,
                owner_user_id TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (tenant_id, version)
            );
            """
        )
        yield conn
        conn.close()


def test_create_identity_persists_version_1(conn: sqlite3.Connection) -> None:
    identity = create_identity(
        conn,
        tenant_id="tenant-a",
        name="Acme Corp",
        slug="acme-corp",
        owner_user_id="owner-1",
        tax_id="TAX-001",
        timestamp="2024-01-01T00:00:00+00:00",
    )
    assert identity.version == 1
    assert identity.name == "Acme Corp"


def test_cannot_create_identity_twice(conn: sqlite3.Connection) -> None:
    create_identity(conn, "tenant-a", "Acme", "acme", "owner-1")
    with pytest.raises(IdentityError, match="already exists"):
        create_identity(conn, "tenant-a", "Acme2", "acme2", "owner-1")


def test_owner_cannot_self_approve_update(conn: sqlite3.Connection) -> None:
    create_identity(conn, "tenant-a", "Acme", "acme", "owner-1")
    with pytest.raises(IdentityError, match="cannot self-approve"):
        update_identity(
            conn,
            tenant_id="tenant-a",
            actor_user_id="owner-1",
            actor_role="owner",
            confirmation_token="tok",
            expected_token="tok",
            name="Acme New",
        )


def test_update_requires_owner_role(conn: sqlite3.Connection) -> None:
    create_identity(conn, "tenant-a", "Acme", "acme", "owner-1")
    with pytest.raises(IdentityError, match="Only owner"):
        update_identity(
            conn,
            tenant_id="tenant-a",
            actor_user_id="owner-2",
            actor_role="admin",
            confirmation_token="tok",
            expected_token="tok",
            name="Acme New",
        )


def test_update_creates_new_version(conn: sqlite3.Connection) -> None:
    create_identity(conn, "tenant-a", "Acme", "acme", "owner-1")
    updated = update_identity(
        conn,
        tenant_id="tenant-a",
        actor_user_id="owner-2",
        actor_role="owner",
        confirmation_token="tok",
        expected_token="tok",
        name="Acme New",
        timestamp="2024-02-01T00:00:00+00:00",
    )
    assert updated.version == 2
    assert updated.name == "Acme New"
    assert updated.slug == "acme"
