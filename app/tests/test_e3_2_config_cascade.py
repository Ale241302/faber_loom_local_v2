"""E3-2 — Configuration cascade resolver."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from app.src.config_cascade import ConfigCascadeError, resolve
from app.src.context import Context


@pytest.fixture()
def conn():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.sqlite3"
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        conn.executescript(
            """
            CREATE TABLE workspace_smtp_config (
                workspace_id TEXT PRIMARY KEY,
                server TEXT,
                port INTEGER,
                use_ssl INTEGER,
                username TEXT
            );
            """
        )
        yield conn
        conn.close()


def test_default_returned_when_no_override(conn: sqlite3.Connection) -> None:
    ctx = Context(workspace_id="ws-1", tenant_id="tenant-a", user_id="u1")
    assert resolve(conn, ctx, "smtp.port") == 465


def test_workspace_override_wins_over_default(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT INTO workspace_smtp_config VALUES (?, ?, ?, ?, ?)",
        ("ws-1", "smtp.acme.test", 587, 0, "user"),
    )
    conn.commit()
    ctx = Context(workspace_id="ws-1", tenant_id="tenant-a", user_id="u1")
    assert resolve(conn, ctx, "smtp.port") == 587
    assert resolve(conn, ctx, "smtp.use_ssl") == 0


def test_explicit_default_used_when_no_value_and_no_default(conn: sqlite3.Connection) -> None:
    ctx = Context(workspace_id="ws-1", tenant_id="tenant-a", user_id="u1")
    assert resolve(conn, ctx, "smtp.missing", default="fallback") == "fallback"


def test_unknown_key_without_default_raises(conn: sqlite3.Connection) -> None:
    ctx = Context(workspace_id="ws-1", tenant_id="tenant-a", user_id="u1")
    with pytest.raises(ConfigCascadeError):
        resolve(conn, ctx, "not.a.setting")
