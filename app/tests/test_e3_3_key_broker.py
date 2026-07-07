"""E3-3 — Graduated key broker."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from app.src.key_broker import (
    DEFAULT_APPROVER_ROLES,
    KeyBrokerError,
    KeyLevel,
    get_policy,
    request_access,
    set_policy,
)


@pytest.fixture()
def conn():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.sqlite3"
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        conn.executescript(
            """
            CREATE TABLE key_policy (
                tenant_id TEXT NOT NULL,
                space_id TEXT NOT NULL,
                level TEXT NOT NULL,
                approver_roles_json TEXT NOT NULL DEFAULT '[]',
                ceo_only INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT '',
                updated_by TEXT,
                PRIMARY KEY (tenant_id, space_id)
            );
            """
        )
        yield conn
        conn.close()


def test_default_policy_is_closed(conn: sqlite3.Connection) -> None:
    policy = get_policy(conn, "tenant-a", "space-1")
    assert policy.level == KeyLevel.CLOSED
    assert policy.approver_roles == DEFAULT_APPROVER_ROLES


def test_set_and_get_policy(conn: sqlite3.Connection) -> None:
    set_policy(conn, "tenant-a", "space-1", KeyLevel.INDEX)
    policy = get_policy(conn, "tenant-a", "space-1")
    assert policy.level == KeyLevel.INDEX


def test_content_access_requires_confirmation(conn: sqlite3.Connection) -> None:
    set_policy(conn, "tenant-a", "space-1", KeyLevel.CONTENT)
    with pytest.raises(KeyBrokerError, match="confirmation token"):
        request_access(
            conn,
            "tenant-a",
            "space-1",
            KeyLevel.CONTENT,
            user_id="u1",
            user_roles={"owner"},
        )


def test_content_access_granted_with_token(conn: sqlite3.Connection) -> None:
    set_policy(conn, "tenant-a", "space-1", KeyLevel.CONTENT)
    level = request_access(
        conn,
        "tenant-a",
        "space-1",
        KeyLevel.CONTENT,
        user_id="u1",
        user_roles={"owner"},
        confirmation_token="yes",
    )
    assert level == KeyLevel.CONTENT


def test_ceo_only_blocks_non_ceo(conn: sqlite3.Connection) -> None:
    set_policy(conn, "tenant-a", "space-1", KeyLevel.CONTENT, ceo_only=True)
    with pytest.raises(KeyBrokerError, match="CEO-only"):
        request_access(
            conn,
            "tenant-a",
            "space-1",
            KeyLevel.CONTENT,
            user_id="u1",
            user_roles={"owner"},
            confirmation_token="yes",
        )
