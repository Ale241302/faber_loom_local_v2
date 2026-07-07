"""E3-1 — KB full-text search parity: SQLite FTS5 vs Postgres tsvector/GIN.

Inserts the same corpus into both engines and asserts that the same queries
return the same top-k chunk content.
"""

from __future__ import annotations

import importlib
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import pytest

from app.src.context import Context
from app.src.kb import search_kb_chunks

from app.tests.e3_1_pg_helper import (
    ensure_core_tables,
    postgres_test_schema,
    skip_if_no_postgres,
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


@contextmanager
def _sqlite_corpus() -> Iterator[tuple[Any, Context]]:
    """Create a temporary SQLite DB with a KB corpus and yield (conn, ctx)."""

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "fts.sqlite3"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        # Minimal schema compatible with the FTS5 path.
        conn.executescript(
            """
            CREATE TABLE workspace (
                id TEXT PRIMARY KEY, name TEXT, slug TEXT, tenant_id TEXT,
                parent_id TEXT, inherits_kb INTEGER DEFAULT 0,
                is_canary INTEGER DEFAULT 0, created_at TEXT, updated_at TEXT
            );
            CREATE TABLE kb_source (
                id TEXT PRIMARY KEY, workspace_id TEXT, tenant_id TEXT,
                type TEXT, title TEXT, created_at TEXT
            );
            CREATE TABLE kb_chunk (
                id TEXT PRIMARY KEY, workspace_id TEXT, source_id TEXT,
                chunk_index INTEGER, content_text TEXT, source_locator TEXT,
                source_version TEXT, tenant_id TEXT, created_at TEXT
            );
            CREATE VIRTUAL TABLE kb_chunk_fts USING fts5(
                content_text, content='kb_chunk', content_rowid='rowid'
            );
            CREATE TRIGGER kb_chunk_fts_insert AFTER INSERT ON kb_chunk BEGIN
                INSERT INTO kb_chunk_fts(rowid, content_text) VALUES (new.rowid, new.content_text);
            END;
            """
        )
        ctx = Context(workspace_id="ws-1", tenant_id="tenant-1", user_id="u1")
        conn.execute(
            "INSERT INTO workspace (id, name, slug, tenant_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("ws-1", "WS", "ws-1", "tenant-1", "2024-01-01", "2024-01-01"),
        )
        conn.execute(
            "INSERT INTO kb_source (id, workspace_id, tenant_id, type, title, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("kbs-1", "ws-1", "tenant-1", "md", "Manual", "2024-01-01"),
        )
        chunks = [
            ("chunk-1", "El procedimiento de facturación electrónica requiere validación previa."),
            ("chunk-2", "La guía de compras internacionales incluye aranceles y logística."),
            ("chunk-3", "Para facturar se necesita el NIT del receptor y el CAI vigente."),
        ]
        for cid, text in chunks:
            conn.execute(
                "INSERT INTO kb_chunk (id, workspace_id, source_id, chunk_index, content_text, tenant_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (cid, "ws-1", "kbs-1", 0, text, "tenant-1", "2024-01-01"),
            )
        conn.commit()
        try:
            yield conn, ctx
        finally:
            conn.close()


def _seed_postgres_corpus(conn: Any, schema: str) -> Context:
    ctx = Context(workspace_id="ws-1", tenant_id="tenant-1", user_id="u1")
    conn.execute(
        f'INSERT INTO "{schema}".workspace (id, name, slug, tenant_id, is_canary, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        ("ws-1", "WS", "ws-1", "tenant-1", 0, "2024-01-01", "2024-01-01"),
    )
    conn.execute(
        f'INSERT INTO "{schema}".kb_source (id, workspace_id, tenant_id, type, title, created_at) VALUES (?, ?, ?, ?, ?, ?)',
        ("kbs-1", "ws-1", "tenant-1", "md", "Manual", "2024-01-01"),
    )
    chunks = [
        ("chunk-1", "El procedimiento de facturación electrónica requiere validación previa."),
        ("chunk-2", "La guía de compras internacionales incluye aranceles y logística."),
        ("chunk-3", "Para facturar se necesita el NIT del receptor y el CAI vigente."),
    ]
    for cid, text in chunks:
        conn.execute(
            f'INSERT INTO "{schema}".kb_chunk (id, workspace_id, source_id, chunk_index, content_text, tenant_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (cid, "ws-1", "kbs-1", 0, text, "tenant-1", "2024-01-01"),
        )
    conn.commit()
    return ctx


def _chunk_ids(results: list[dict[str, Any]]) -> list[str]:
    return [r["id"] for r in results]


def test_sqlite_fts_returns_expected_chunks() -> None:
    """Sanity check: SQLite FTS5 path returns the matching chunks."""

    with _sqlite_corpus() as (conn, ctx):
        results = search_kb_chunks(ctx, conn, "facturación", limit=5)
        ids = _chunk_ids(results)
        assert "chunk-1" in ids
        assert "chunk-2" not in ids

        results = search_kb_chunks(ctx, conn, "NIT", limit=5)
        ids = _chunk_ids(results)
        assert "chunk-3" in ids
        assert "chunk-1" not in ids
        assert "chunk-2" not in ids


@skip_if_no_postgres
def test_postgres_tsvector_returns_expected_chunks() -> None:
    """Postgres tsvector/GIN path returns the same matching chunks."""

    with _postgres_adapter() as adapter:
        with postgres_test_schema() as (pg_conn, schema):
            ensure_core_tables(pg_conn, schema)
            ctx = _seed_postgres_corpus(pg_conn, schema)

            conn = adapter.connect()
            try:
                with adapter.transaction(conn, ctx=ctx):
                    results = search_kb_chunks(ctx, conn, "facturación", limit=5)
                    ids = _chunk_ids(results)
                    assert "chunk-1" in ids
                    assert "chunk-2" not in ids

                    results = search_kb_chunks(ctx, conn, "NIT", limit=5)
                    ids = _chunk_ids(results)
                    assert "chunk-3" in ids
                    assert "chunk-1" not in ids
                    assert "chunk-2" not in ids
            finally:
                conn.close()


@skip_if_no_postgres
def test_fts_parity_across_engines() -> None:
    """Same queries on SQLite and Postgres return the same top-k chunk ids."""

    queries = ["facturación", "NIT", "compras internacionales"]

    with _sqlite_corpus() as (sqlite_conn, sqlite_ctx):
        sqlite_results = {
            q: _chunk_ids(search_kb_chunks(sqlite_ctx, sqlite_conn, q, limit=5))
            for q in queries
        }

    with _postgres_adapter() as adapter:
        with postgres_test_schema() as (pg_conn, schema):
            ensure_core_tables(pg_conn, schema)
            pg_ctx = _seed_postgres_corpus(pg_conn, schema)

            conn = adapter.connect()
            try:
                with adapter.transaction(conn, ctx=pg_ctx):
                    for q in queries:
                        pg_ids = _chunk_ids(search_kb_chunks(pg_ctx, conn, q, limit=5))
                        assert pg_ids == sqlite_results[q], (
                            f"Query '{q}' differs: sqlite={sqlite_results[q]} postgres={pg_ids}"
                        )
            finally:
                conn.close()
