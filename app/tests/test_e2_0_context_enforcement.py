"""E2-0 — Context enforcement regression tests.

These tests verify that workspace-owned repository helpers fail closed when
they receive a Context without a real tenant or a real workspace. This is the
SQLite-side mirror of the Postgres RLS policies that will be applied in E2-1.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.src.context import Context, system_context
from app.src.db import connect, initialize_database
from app.src.db import (
    create_chat,
    create_mail_message,
    create_routine,
    create_routine_run,
)
from app.src.kb import ingest_kb_source


@pytest.fixture()
def conn(tmp_path: Path) -> sqlite3.Connection:
    """Yield an initialized SQLite connection for repository tests."""

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "test.sqlite3"))
    db_conn = connect()
    initialize_database(db_conn)
    try:
        yield db_conn
    finally:
        db_conn.close()
        monkeypatch.undo()


def test_system_context_rejects_scoped_data_access(conn: sqlite3.Connection) -> None:
    """A system Context cannot be used to create workspace-owned data."""

    ctx = system_context()
    with pytest.raises(ValueError, match="concrete workspace Context is required"):
        create_chat(ctx, conn, "Bad chat")


def test_missing_tenant_is_rejected(conn: sqlite3.Connection) -> None:
    """A scoped workspace without a tenant is rejected (fail-closed)."""

    ctx = Context(workspace_id="ws_123", tenant_id="")
    with pytest.raises(ValueError, match="tenant_id is required"):
        create_routine(ctx, conn, "Bad routine")


def test_missing_workspace_is_rejected(conn: sqlite3.Connection) -> None:
    """A missing workspace id is rejected."""

    ctx = Context(workspace_id="", tenant_id="default")
    with pytest.raises(ValueError, match="workspace_id is required"):
        create_chat(ctx, conn, "Bad chat")


def test_kb_ingest_requires_tenant_scoped_context(conn: sqlite3.Connection) -> None:
    """KB ingestion is workspace/tenant-scoped."""

    ctx = Context(workspace_id="ws_kb", tenant_id="")
    with pytest.raises(ValueError, match="tenant_id is required"):
        ingest_kb_source(
            ctx,
            conn,
            title="Bad source",
            source_type="md",
            content_text="content",
        )


def test_mail_message_requires_tenant_scoped_context(conn: sqlite3.Connection) -> None:
    """Mail message creation is workspace/tenant-scoped."""

    ctx = Context(workspace_id="ws_mail", tenant_id="")
    with pytest.raises(ValueError, match="tenant_id is required"):
        create_mail_message(
            ctx,
            conn,
            account="acc",
            mail_uid="1",
            subject="Subject",
            sender="s@test",
            body_text="body",
            raw_payload=None,
        )


def test_routine_run_requires_tenant_scoped_context(conn: sqlite3.Connection) -> None:
    """Routine run creation is workspace/tenant-scoped."""

    ctx = Context(workspace_id="ws_run", tenant_id="")
    with pytest.raises(ValueError, match="tenant_id is required"):
        create_routine_run(
            ctx,
            conn,
            routine_id="rt_123",
            input_json={},
            output_json={},
            evidence_json=[],
            status="succeeded",
        )
