"""E3-1 — RLS canary / tenant isolation tests on Postgres.

Verifies that ``SET LOCAL app.current_tenant`` and ``app.current_workspace``
force workspace-owned queries to see only their own rows, and that the canary
workspace is isolated from the default tenant.
"""

from __future__ import annotations

import importlib
import os
from contextlib import contextmanager
from typing import Any, Iterator

import pytest

from app.src.context import Context

from app.tests.e3_1_pg_helper import (
    enable_rls,
    ensure_core_tables,
    postgres_test_schema,
    skip_if_no_postgres,
)
from app.scripts.check_canary_isolation_postgres import (
    WORKSPACE_TABLES,
    TENANT_TABLES,
    OPTIONAL_WORKSPACE_TABLES,
)


@contextmanager
def _postgres_adapter() -> Iterator[Any]:
    """Temporarily switch the adapter to Postgres and reload it."""

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


def _insert_workspace(conn: Any, schema: str, ws_id: str, tenant_id: str, is_canary: int = 0) -> None:
    conn.execute(
        f'INSERT INTO "{schema}".workspace (id, name, slug, tenant_id, is_canary, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (ws_id, ws_id, ws_id, tenant_id, is_canary, "2024-01-01", "2024-01-01"),
    )
    conn.commit()


@skip_if_no_postgres
def test_rls_filters_workspace_rows_by_tenant() -> None:
    """A query scoped to tenant A must not see tenant B's workspace."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema() as (pg_conn, schema):
            ensure_core_tables(pg_conn, schema)
            enable_rls(pg_conn, schema)

            _insert_workspace(pg_conn, schema, "ws-a", "tenant-a")
            _insert_workspace(pg_conn, schema, "ws-b", "tenant-b")

            conn = adapter.connect()
            try:
                ctx = Context(workspace_id="ws-a", tenant_id="tenant-a", user_id="u1")
                with adapter.transaction(conn, ctx=ctx):
                    rows = conn.execute(
                        f'SELECT id FROM "{schema}".workspace ORDER BY id'
                    ).fetchall()
                    ids = {r["id"] for r in rows}
                    assert ids == {"ws-a"}
            finally:
                conn.close()


@skip_if_no_postgres
def test_rls_blocks_unscoped_reads() -> None:
    """Without setting app.current_tenant, RLS must return no rows."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema() as (pg_conn, schema):
            ensure_core_tables(pg_conn, schema)
            enable_rls(pg_conn, schema)

            _insert_workspace(pg_conn, schema, "ws-default", "default")

            conn = adapter.connect()
            try:
                # No transaction(ctx) -> RLS variables are unset -> no rows.
                rows = conn.execute(
                    f'SELECT id FROM "{schema}".workspace'
                ).fetchall()
                assert rows == []
            finally:
                conn.close()


@skip_if_no_postgres
def test_canary_isolation_bidirectional() -> None:
    """Canary tenant sees only canary workspace; default tenant does not see canary."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema() as (pg_conn, schema):
            ensure_core_tables(pg_conn, schema)
            enable_rls(pg_conn, schema)

            _insert_workspace(pg_conn, schema, "ws-default", "default")
            _insert_workspace(pg_conn, schema, "ws-canary", "canary", is_canary=1)

            conn = adapter.connect()
            try:
                # Canary context
                ctx_canary = Context(workspace_id="ws-canary", tenant_id="canary", user_id="u1")
                with adapter.transaction(conn, ctx=ctx_canary):
                    rows = conn.execute(f'SELECT id FROM "{schema}".workspace').fetchall()
                    assert [r["id"] for r in rows] == ["ws-canary"]

                # Default context
                ctx_default = Context(workspace_id="ws-default", tenant_id="default", user_id="u1")
                with adapter.transaction(conn, ctx=ctx_default):
                    rows = conn.execute(f'SELECT id FROM "{schema}".workspace').fetchall()
                    assert [r["id"] for r in rows] == ["ws-default"]
            finally:
                conn.close()


@skip_if_no_postgres
def test_rls_kb_scope_is_tenant_workspace_bound() -> None:
    """KB chunks from workspace A/tenant A are invisible to workspace B/tenant B."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema() as (pg_conn, schema):
            ensure_core_tables(pg_conn, schema)
            enable_rls(pg_conn, schema)

            _insert_workspace(pg_conn, schema, "ws-a", "tenant-a")
            _insert_workspace(pg_conn, schema, "ws-b", "tenant-b")

            conn = adapter.connect()
            try:
                conn.execute(
                    f'INSERT INTO "{schema}".kb_source (id, workspace_id, tenant_id, type, title, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                    ("kbs-a", "ws-a", "tenant-a", "md", "Source A", "2024-01-01"),
                )
                conn.execute(
                    f'INSERT INTO "{schema}".kb_chunk (id, workspace_id, source_id, chunk_index, content_text, tenant_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
                    ("chunk-a", "ws-a", "kbs-a", 0, "alpha bravo", "tenant-a", "2024-01-01"),
                )
                conn.commit()

                ctx_a = Context(workspace_id="ws-a", tenant_id="tenant-a", user_id="u1")
                with adapter.transaction(conn, ctx=ctx_a):
                    rows = conn.execute(
                        f'SELECT id FROM "{schema}".kb_chunk'
                    ).fetchall()
                    assert [r["id"] for r in rows] == ["chunk-a"]

                ctx_b = Context(workspace_id="ws-b", tenant_id="tenant-b", user_id="u1")
                with adapter.transaction(conn, ctx=ctx_b):
                    rows = conn.execute(
                        f'SELECT id FROM "{schema}".kb_chunk'
                    ).fetchall()
                    assert rows == []
            finally:
                conn.close()


def test_canary_postgres_script_covers_v29_tables() -> None:
    """The Postgres canary checker must cover all v29 workspace/tenant tables."""

    required_workspace_tables = {
        "kb_source",
        "kb_chunk",
        "kb_fact",
        "chat",
        "message",
        "draft",
        "routine",
        "routine_run",
        "gold_candidate",
        "usage_record",
        "mail_message",
        "mail_outbox",
        "email_account",
        "audit_log",
        "editorial_history",
        "workspace_smtp_config",
        "workspace_routing_policy",
        "workspace_model_catalog",
        "ambient_workspace_config",
        "ambient_proposal",
        "object",
    }
    required_tenant_tables = {
        "ambient_config",
        "ambient_detector",
    }
    required_optional_tables = {
        "ambient_cycle",
        "ambient_detector_run",
    }

    assert required_workspace_tables.issubset(set(WORKSPACE_TABLES))
    assert required_tenant_tables.issubset(set(TENANT_TABLES))
    assert required_optional_tables.issubset(set(OPTIONAL_WORKSPACE_TABLES))
