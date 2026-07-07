"""Shared helper for E3-1 Postgres tests.

Provides a fixture-like function that returns a psycopg3 connection to an
ephemeral Postgres database/schema. Tests skip automatically when no Postgres
server is reachable.
"""

from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

import pytest


DEFAULT_TEST_POSTGRES_URL = os.environ.get(
    "FABERLOOM_TEST_POSTGRES_URL",
    "postgresql://postgres:postgres@localhost:5432/faberloom_test",
)


def _get_postgres_url() -> str:
    return os.environ.get("FABERLOOM_POSTGRES_URL", DEFAULT_TEST_POSTGRES_URL)


def postgres_available() -> bool:
    """Return True if a Postgres server is reachable."""

    try:
        import psycopg
    except ImportError:
        return False

    try:
        with psycopg.connect(_get_postgres_url(), connect_timeout=2):
            return True
    except Exception:
        return False


@contextmanager
def postgres_test_schema() -> Iterator[tuple[Any, str]]:
    """Create a temporary schema, yield (conn, schema_name), then drop it."""

    import psycopg

    schema_name = f"e3_1_{uuid.uuid4().hex[:12]}"
    conn = psycopg.connect(_get_postgres_url())
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
    conn.autocommit = False
    try:
        yield conn, schema_name
    finally:
        # Close any open transaction before switching autocommit so cleanup can
        # run even if a test left the connection in INTRANS/INERROR.
        try:
            conn.rollback()
        except Exception:
            pass
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE')
        conn.close()


def ensure_core_tables(conn: Any, schema: str) -> None:
    """Create a minimal Postgres schema for E3-1 adapter/RLS/FTS tests."""

    sql = f"""
    CREATE TABLE IF NOT EXISTS "{schema}".workspace (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        seal_id TEXT,
        field_aliases_json TEXT DEFAULT '{{}}',
        tenant_id TEXT NOT NULL DEFAULT 'default',
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 29,
        source_version TEXT,
        approved_by TEXT,
        parent_id TEXT,
        inherits_kb INTEGER NOT NULL DEFAULT 0,
        confidential INTEGER NOT NULL DEFAULT 0,
        email_signature TEXT,
        is_canary INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "{schema}".kb_source (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL REFERENCES "{schema}".workspace(id) ON DELETE CASCADE,
        tenant_id TEXT NOT NULL DEFAULT 'default',
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        content_text TEXT,
        content_blob BYTEA,
        meta_json TEXT NOT NULL DEFAULT '{{}}',
        source_version TEXT NOT NULL DEFAULT 'v1',
        schema_version INTEGER NOT NULL DEFAULT 29,
        level INTEGER NOT NULL DEFAULT 0,
        file_name TEXT,
        mime_type TEXT,
        file_size INTEGER,
        parser_version TEXT,
        approved_by TEXT,
        workspace_hmac TEXT,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "{schema}".kb_chunk (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL REFERENCES "{schema}".workspace(id) ON DELETE CASCADE,
        source_id TEXT NOT NULL REFERENCES "{schema}".kb_source(id) ON DELETE CASCADE,
        chunk_index INTEGER NOT NULL,
        content_text TEXT NOT NULL,
        source_locator TEXT,
        source_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 29,
        tenant_id TEXT NOT NULL DEFAULT 'default',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS "{schema}".kb_fact (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL REFERENCES "{schema}".workspace(id) ON DELETE CASCADE,
        source_id TEXT NOT NULL REFERENCES "{schema}".kb_source(id) ON DELETE CASCADE,
        entity_key TEXT NOT NULL,
        field_name TEXT NOT NULL,
        field_value TEXT NOT NULL,
        unit TEXT,
        currency TEXT,
        valid_from TEXT,
        valid_until TEXT,
        source_locator TEXT,
        source_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 29,
        extraction_method TEXT,
        source_sheet TEXT,
        workspace_hmac TEXT,
        tenant_id TEXT NOT NULL DEFAULT 'default',
        created_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_kb_chunk_workspace
        ON "{schema}".kb_chunk(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_kb_chunk_source
        ON "{schema}".kb_chunk(source_id);
    CREATE INDEX IF NOT EXISTS idx_kb_fact_workspace
        ON "{schema}".kb_fact(workspace_id);

    -- Full-text search via tsvector/GIN for Postgres parity with SQLite FTS5.
    CREATE INDEX IF NOT EXISTS idx_kb_chunk_fts
        ON "{schema}".kb_chunk USING GIN (to_tsvector('simple', content_text));
    """
    conn.execute(sql)
    conn.commit()


def enable_rls(conn: Any, schema: str) -> None:
    """Enable RLS and create tenant/workspace policies for the test schema."""

    sql = f"""
    ALTER TABLE "{schema}".workspace ENABLE ROW LEVEL SECURITY;
    ALTER TABLE "{schema}".workspace FORCE ROW LEVEL SECURITY;
    ALTER TABLE "{schema}".kb_source ENABLE ROW LEVEL SECURITY;
    ALTER TABLE "{schema}".kb_source FORCE ROW LEVEL SECURITY;
    ALTER TABLE "{schema}".kb_chunk ENABLE ROW LEVEL SECURITY;
    ALTER TABLE "{schema}".kb_chunk FORCE ROW LEVEL SECURITY;
    ALTER TABLE "{schema}".kb_fact ENABLE ROW LEVEL SECURITY;
    ALTER TABLE "{schema}".kb_fact FORCE ROW LEVEL SECURITY;

    CREATE OR REPLACE FUNCTION "{schema}".set_app_scope(p_tenant TEXT, p_workspace TEXT)
    RETURNS VOID AS $$
    BEGIN
        PERFORM set_config('app.current_tenant', p_tenant, false);
        PERFORM set_config('app.current_workspace', p_workspace, false);
    END;
    $$ LANGUAGE plpgsql SECURITY DEFINER;

    CREATE POLICY tenant_workspace_policy ON "{schema}".workspace
        USING (tenant_id = current_setting('app.current_tenant', true)::TEXT);

    CREATE POLICY tenant_workspace_policy ON "{schema}".kb_source
        USING (tenant_id = current_setting('app.current_tenant', true)::TEXT
               AND workspace_id = current_setting('app.current_workspace', true)::TEXT);

    CREATE POLICY tenant_workspace_policy ON "{schema}".kb_chunk
        USING (tenant_id = current_setting('app.current_tenant', true)::TEXT
               AND workspace_id = current_setting('app.current_workspace', true)::TEXT);

    CREATE POLICY tenant_workspace_policy ON "{schema}".kb_fact
        USING (tenant_id = current_setting('app.current_tenant', true)::TEXT
               AND workspace_id = current_setting('app.current_workspace', true)::TEXT);
    """
    conn.execute(sql)
    conn.commit()


skip_if_no_postgres = pytest.mark.skipif(
    not postgres_available(),
    reason="Postgres server not reachable (set FABERLOOM_TEST_POSTGRES_URL)",
)
