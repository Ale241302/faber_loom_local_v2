"""E3-1 — Dual SQLite/Postgres adapter tests.

Exercises placeholder translation, connection wrapping, transaction scoping,
and basic CRUD when ``FABERLOOM_DB_ENGINE=postgres``. SQLite is the default
engine and the existing suite already covers it; these tests focus on the
Postgres path and skip automatically when no server is available.
"""

from __future__ import annotations

import importlib
import os
from contextlib import contextmanager
from typing import Any, Iterator

import pytest

from app.src.context import Context

from app.tests.e3_1_pg_helper import (
    ensure_core_tables,
    postgres_test_schema,
    skip_if_no_postgres,
)


@contextmanager
def _postgres_adapter() -> Iterator[Any]:
    """Temporarily switch the adapter to Postgres and reload it.

    Yields the freshly imported adapter module so tests use the Postgres path.
    """

    import app.src.db_adapter as adapter_module

    old_engine = os.environ.get("FABERLOOM_DB_ENGINE")
    os.environ["FABERLOOM_DB_ENGINE"] = "postgres"
    try:
        importlib.reload(adapter_module)
        yield adapter_module
    finally:
        if old_engine is None:
            os.environ.pop("FABERLOOM_DB_ENGINE", None)
        else:
            os.environ["FABERLOOM_DB_ENGINE"] = old_engine
        importlib.reload(adapter_module)


@pytest.mark.parametrize(
    ("sql", "expected"),
    [
        ("SELECT * FROM t WHERE a = ?", "SELECT * FROM t WHERE a = %s"),
        ("INSERT INTO t VALUES (?, ?)", "INSERT INTO t VALUES (%s, %s)"),
        ("-- ? comment\nSELECT ?", "-- ? comment\nSELECT %s"),
        ("SELECT 'literal ?' FROM t WHERE x = ?", "SELECT 'literal ?' FROM t WHERE x = %s"),
        ("SELECT * FROM t WHERE a LIKE '%?%' AND b = ?", "SELECT * FROM t WHERE a LIKE '%?%' AND b = %s"),
    ],
)
def test_translate_placeholders(sql: str, expected: str) -> None:
    from app.src.db_adapter import _translate_placeholders

    assert _translate_placeholders(sql) == expected


def test_sqlite_mode_is_default() -> None:
    from app.src.db_adapter import DB_ENGINE

    assert DB_ENGINE in {"sqlite", "postgres"}
    if "FABERLOOM_DB_ENGINE" not in os.environ:
        assert DB_ENGINE == "sqlite"


@skip_if_no_postgres
def test_postgres_connect_returns_adapter_wrapper() -> None:
    """A Postgres connection must expose the wrapper interface."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema():
            conn = adapter.connect()
            assert adapter.is_postgres_connection(conn)
            assert hasattr(conn, "execute")
            assert hasattr(conn, "executemany")
            assert hasattr(conn, "executescript")
            assert hasattr(conn, "commit")
            assert hasattr(conn, "rollback")
            assert hasattr(conn, "close")
            conn.close()


@skip_if_no_postgres
def test_postgres_crud_with_question_placeholders() -> None:
    """Callers can keep using ``?`` placeholders on Postgres."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema() as (pg_conn, schema):
            ensure_core_tables(pg_conn, schema)
            conn = adapter.connect()
            try:
                conn.execute(
                    f'INSERT INTO "{schema}".workspace (id, name, slug, tenant_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
                    ("ws-1", "Demo", "demo", "default", "2024-01-01", "2024-01-01"),
                )
                conn.commit()
                row = conn.execute(
                    f'SELECT name FROM "{schema}".workspace WHERE id = ?',
                    ("ws-1",),
                ).fetchone()
                assert row is not None
                assert row["name"] == "Demo"
            finally:
                conn.close()


@skip_if_no_postgres
def test_postgres_transaction_sets_rls_session_variables() -> None:
    """transaction(conn, ctx) must SET LOCAL app.current_tenant/workspace."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema():
            conn = adapter.connect()
            try:
                ctx = Context(
                    workspace_id="ws-demo",
                    tenant_id="tenant-demo",
                    user_id="u1",
                    actor_id="u1",
                    actor_role_at_decision="owner",
                )
                with adapter.transaction(conn, ctx=ctx):
                    cur = conn.execute(
                        "SELECT current_setting('app.current_tenant') AS t, current_setting('app.current_workspace') AS w"
                    )
                    row = cur.fetchone()
                    assert row is not None
                    assert row["t"] == "tenant-demo"
                    assert row["w"] == "ws-demo"
            finally:
                conn.close()


@skip_if_no_postgres
def test_postgres_db_session_context_manager() -> None:
    """db_session() must work as a context manager with Postgres."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema():
            with adapter.db_session() as conn:
                assert adapter.is_postgres_connection(conn)
                cur = conn.execute("SELECT 1 AS n")
                assert cur.fetchone()["n"] == 1


@skip_if_no_postgres
def test_postgres_connection_rollback_on_error() -> None:
    """transaction must roll back on exception."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema() as (pg_conn, schema):
            ensure_core_tables(pg_conn, schema)
            conn = adapter.connect()
            try:
                with pytest.raises(RuntimeError):
                    with adapter.transaction(conn):
                        conn.execute(
                            f'INSERT INTO "{schema}".workspace (id, name, slug, tenant_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
                            ("ws-rollback", "Roll", "roll", "default", "2024-01-01", "2024-01-01"),
                        )
                        raise RuntimeError("boom")
                row = conn.execute(
                    f'SELECT 1 FROM "{schema}".workspace WHERE id = ?',
                    ("ws-rollback",),
                ).fetchone()
                assert row is None
            finally:
                conn.close()
