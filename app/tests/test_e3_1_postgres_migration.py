"""E3-1 — SQLite → PostgreSQL migration tests.

Dry-run tests verify that the migration helper understands the current
FaberLoom schema without needing a running Postgres server. Live tests run
only when ``FABERLOOM_TEST_POSTGRES_URL`` is set (or an ephemeral container
is available) and validate row counts and constraints after migration.
"""

from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sqlite_to_postgres.py"


def _run_script(db_path: Path, *extra_args: str) -> subprocess.CompletedProcess:
    """Invoke the migration script and return the completed process."""

    cmd = [
        sys.executable,
        str(SCRIPT),
        "--sqlite-path",
        str(db_path),
        "--postgres-url",
        "postgresql://unused:unused@localhost:5435/unused",
        "--dry-run",
        *extra_args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


@pytest.fixture()
def sample_sqlite(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Create a real FaberLoom SQLite database using the current migrations."""

    db_path = tmp_path / "faberloom.sqlite3"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "config"))

    # Avoid importing optional providers that may not be configured in tests.
    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
        "KIMI_API_KEY",
        "MOONSHOT_API_KEY",
        "FABERLOOM_KIMI_API_KEY",
        "FABERLOOM_ENABLE_OLLAMA",
        "FABERLOOM_OLLAMA_ENABLED",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.db import initialize_database

    initialize_database()

    # Insert representative rows for two tenants so counts are non-trivial.
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    now = "2026-07-07T00:00:00Z"
    conn.execute(
        """
        INSERT INTO workspace (id, name, slug, tenant_id, created_at, updated_at)
        VALUES ('ws-canary', 'Canary', 'canary', 'canary', ?, ?),
               ('ws-default', 'Default', 'default', 'default', ?, ?)
        """,
        (now, now, now, now),
    )
    conn.execute(
        """
        INSERT INTO chat (id, workspace_id, tenant_id, title, model_preset, created_at)
        VALUES ('chat-canary', 'ws-canary', 'canary', 'Canary Chat', 'default', ?),
               ('chat-default', 'ws-default', 'default', 'Default Chat', 'default', ?)
        """,
        (now, now),
    )
    conn.execute(
        """
        INSERT INTO routine (id, workspace_id, tenant_id, name, skill_md, created_at, updated_at)
        VALUES ('rt-canary', 'ws-canary', 'canary', 'Canary Routine', '', ?, ?),
               ('rt-default', 'ws-default', 'default', 'Default Routine', '', ?, ?)
        """,
        (now, now, now, now),
    )
    conn.execute(
        """
        INSERT INTO object (id, workspace_id, tenant_id, origin, bucket, object_key, created_at, updated_at)
        VALUES ('obj-canary', 'ws-canary', 'canary', 'upload', 'bucket', 'key-canary', ?, ?),
               ('obj-default', 'ws-default', 'default', 'upload', 'bucket', 'key-default', ?, ?)
        """,
        (now, now, now, now),
    )
    conn.execute(
        """
        INSERT INTO ambient_config (id, tenant_id, created_at, updated_at)
        VALUES ('ac-canary', 'canary', ?, ?),
               ('ac-default', 'default', ?, ?)
        """,
        (now, now, now, now),
    )
    conn.commit()
    conn.close()
    return db_path


def test_dry_run_reports_expected_counts(sample_sqlite: Path) -> None:
    """Dry-run output must list each table with its exact SQLite row count."""

    result = _run_script(sample_sqlite)
    assert result.returncode == 0, result.stderr

    expected_counts = {
        "workspace": 2,
        "chat": 2,
        "routine": 2,
        "object": 2,
        "ambient_config": 2,
    }
    for table, count in expected_counts.items():
        assert f"Table: {table} ({count} rows)" in result.stdout, (
            f"Expected count for {table} not found in stdout:\n{result.stdout}"
        )

    # The virtual FTS5 table and its shadow tables must not be migrated.
    assert "Table: kb_chunk_fts" not in result.stdout, result.stdout
    assert "Total rows to migrate:" in result.stdout
    assert "No Postgres connection was attempted (dry-run)" in result.stdout


def test_dry_run_generates_ddl_for_current_tables(sample_sqlite: Path) -> None:
    """Generated DDL must contain CREATE TABLE statements for current tables."""

    result = _run_script(sample_sqlite)
    assert result.returncode == 0, result.stderr

    for table in (
        "workspace",
        "kb_source",
        "kb_chunk",
        "kb_fact",
        "chat",
        "message",
        "draft",
        "routine",
        "routine_run",
        "usage_record",
        "gold_candidate",
        "mail_message",
        "mail_outbox",
        "email_account",
        "audit_log",
        "editorial_history",
        "workspace_smtp_config",
        "workspace_routing_policy",
        "workspace_model_catalog",
        "ambient_config",
        "ambient_workspace_config",
        "ambient_detector",
        "ambient_cycle",
        "ambient_detector_run",
        "ambient_proposal",
        "object",
    ):
        assert f'CREATE TABLE "public"."{table}"' in result.stdout, (
            f"Missing CREATE TABLE for {table}:\n{result.stdout}"
        )

    # Type mapping sanity checks
    assert '"content_blob" BYTEA' in result.stdout, "BLOB should map to BYTEA"
    assert '"level" INTEGER' in result.stdout, "INTEGER should stay INTEGER"
    assert '"meta_json" JSONB' in result.stdout, "JSON meta_json should map to JSONB"


def test_dry_run_recreates_unique_constraints(sample_sqlite: Path) -> None:
    """Unique constraints from SQLite autoindexes must appear as unique indexes."""

    result = _run_script(sample_sqlite)
    assert result.returncode == 0, result.stderr

    # workspace.slug and object.id are primary keys; gold_candidate.run_id is a
    # unique constraint that must survive the migration.
    assert 'CREATE UNIQUE INDEX IF NOT EXISTS "sqlite_autoindex_gold_candidate_2" ON "public"."gold_candidate" ("run_id")' in result.stdout, (
        "Unique constraint on gold_candidate.run_id should be recreated as a unique index"
    )


# ---------------------------------------------------------------------------
# Live migration tests (require a Postgres server)
# ---------------------------------------------------------------------------


def _postgres_url() -> str | None:
    """Return the test Postgres URL or None if live tests should be skipped."""

    return os.environ.get("FABERLOOM_TEST_POSTGRES_URL")


@pytest.fixture(scope="session")
def postgres_url() -> str:
    """Provide a Postgres URL for live tests."""

    url = _postgres_url()
    if not url:
        pytest.skip(
            "FABERLOOM_TEST_POSTGRES_URL is not set; skipping live Postgres tests. "
            "See app/.tmp/e3_1_db_notes.md for instructions on starting an ephemeral server."
        )
    return url


def _run_live_migration(
    db_path: Path, postgres_url: str, schema: str = "public_e3_1_test"
) -> subprocess.CompletedProcess:
    """Run the migration script against a real Postgres server."""

    cmd = [
        sys.executable,
        str(SCRIPT),
        "--sqlite-path",
        str(db_path),
        "--postgres-url",
        postgres_url,
        "--schema",
        schema,
        "--drop-existing",
        "--log-path",
        str(db_path.with_suffix(".migration.jsonl")),
    ]
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


@pytest.mark.skipif(
    _postgres_url() is None,
    reason="FABERLOOM_TEST_POSTGRES_URL not set",
)
def test_live_migration_counts_match(
    sample_sqlite: Path, postgres_url: str
) -> None:
    """A live migration must copy every row and report zero mismatches."""

    result = _run_live_migration(sample_sqlite, postgres_url)
    assert result.returncode == 0, f"Migration failed:\n{result.stdout}\n{result.stderr}"

    # All tables should report OK.
    assert "[FAIL]" not in result.stdout, result.stdout
    assert "[MISMATCH]" not in result.stdout, result.stdout
    assert "Migration completed successfully." in result.stdout, result.stdout

    # Compare source and destination counts table by table.
    import sqlite3

    sqlite_conn = sqlite3.connect(sample_sqlite)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_counts = {
        row[0]: row[1]
        for row in sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        if row[0] not in {"kb_chunk_fts"}
    }
    for table in list(sqlite_counts):
        sqlite_counts[table] = sqlite_conn.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        ).fetchone()[0]
    sqlite_conn.close()

    psycopg = pytest.importorskip("psycopg")
    conn = psycopg.connect(postgres_url)
    try:
        with conn.cursor() as cur:
            for table, expected in sqlite_counts.items():
                cur.execute(f'SELECT COUNT(*) FROM "public_e3_1_test"."{table}"')
                actual = cur.fetchone()[0]
                assert actual == expected, f"{table}: expected {expected}, got {actual}"
    finally:
        conn.close()
