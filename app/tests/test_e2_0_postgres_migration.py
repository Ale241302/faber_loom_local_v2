"""E2-0 — SQLite → PostgreSQL migration script tests.

These tests exercise the migration helper in dry-run mode, which requires only
``sqlite3`` and does not need a running Postgres server. Live migration tests
are intentionally excluded here because the CI/local environment does not
provide a Postgres instance.
"""

from __future__ import annotations

import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sqlite_to_postgres.py"


@pytest.fixture()
def sample_sqlite(tmp_path: Path) -> Path:
    """Create a small SQLite database with the core FaberLoom tables."""

    db_path = tmp_path / "sample.sqlite3"
    conn = sqlite3.connect(db_path)
    conn.executescript(
        """
        CREATE TABLE workspace (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            tenant_id TEXT,
            user_id TEXT,
            schema_version INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE routine (
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            tenant_id TEXT,
            user_id TEXT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'custom',
            is_active INTEGER NOT NULL DEFAULT 1,
            approved_by TEXT,
            schema_version INTEGER NOT NULL DEFAULT 12,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
        );

        CREATE TABLE routine_run (
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            tenant_id TEXT,
            routine_id TEXT NOT NULL,
            status TEXT NOT NULL,
            task_type TEXT,
            schema_version INTEGER NOT NULL DEFAULT 16,
            created_at TEXT NOT NULL,
            FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE,
            FOREIGN KEY (routine_id) REFERENCES routine(id) ON DELETE CASCADE
        );

        CREATE TABLE audit_log (
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            tenant_id TEXT,
            actor_id TEXT,
            action TEXT NOT NULL,
            correlation_id TEXT,
            payload_json TEXT NOT NULL DEFAULT '{}',
            schema_version INTEGER NOT NULL DEFAULT 22,
            created_at TEXT NOT NULL
        );

        CREATE TABLE kb_source (
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            tenant_id TEXT,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content_text TEXT,
            content_blob BLOB,
            meta_json TEXT NOT NULL DEFAULT '{}',
            level INTEGER NOT NULL DEFAULT 0,
            schema_version INTEGER NOT NULL DEFAULT 1,
            source_version TEXT NOT NULL DEFAULT 'v1',
            created_at TEXT NOT NULL,
            FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
        );

        CREATE INDEX idx_routine_workspace_id ON routine(workspace_id);
        CREATE INDEX idx_routine_category ON routine(workspace_id, tenant_id, category, is_active, approved_by);

        INSERT INTO workspace (id, name, slug, tenant_id, created_at, updated_at)
        VALUES
            ('ws-1', 'Demo', 'demo', 'default', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z'),
            ('ws-2', 'Canary', 'canary', 'canary', '2024-01-02T00:00:00Z', '2024-01-02T00:00:00Z');

        INSERT INTO routine (id, workspace_id, tenant_id, name, category, created_at, updated_at)
        VALUES
            ('r-1', 'ws-1', 'default', 'Saludo', 'skill', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z'),
            ('r-2', 'ws-1', 'default', 'Despedida', 'skill', '2024-01-01T00:00:00Z', '2024-01-01T00:00:00Z'),
            ('r-3', 'ws-2', 'canary', 'Resumen', 'agent', '2024-01-02T00:00:00Z', '2024-01-02T00:00:00Z');

        INSERT INTO routine_run (id, workspace_id, tenant_id, routine_id, status, task_type, created_at)
        VALUES
            ('rr-1', 'ws-1', 'default', 'r-1', 'completed', 'chat', '2024-01-01T00:00:00Z');

        INSERT INTO audit_log (id, workspace_id, tenant_id, action, correlation_id, created_at)
        VALUES
            ('a-1', 'ws-1', 'default', 'routine_run', 'corr-1', '2024-01-01T00:00:00Z');

        INSERT INTO kb_source (id, workspace_id, tenant_id, type, title, content_text, created_at)
        VALUES
            ('kb-1', 'ws-1', 'default', 'md', 'Manual', 'Contenido', '2024-01-01T00:00:00Z');
        """
    )
    conn.commit()
    conn.close()
    return db_path


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


def test_dry_run_reports_expected_counts(sample_sqlite: Path) -> None:
    """Dry-run output must list each table with its exact SQLite row count."""

    result = _run_script(sample_sqlite)
    assert result.returncode == 0, result.stderr

    expected_counts = {
        "workspace": 2,
        "routine": 3,
        "routine_run": 1,
        "audit_log": 1,
        "kb_source": 1,
    }
    for table, count in expected_counts.items():
        assert f"Table: {table} ({count} rows)" in result.stdout, (
            f"Expected count for {table} not found in stdout:\n{result.stdout}"
        )

    assert "Total rows to migrate: 8" in result.stdout, result.stdout
    assert "No Postgres connection was attempted (dry-run)" in result.stdout


def test_dry_run_generates_ddl_for_core_tables(sample_sqlite: Path) -> None:
    """Generated DDL must contain CREATE TABLE statements for the core tables."""

    result = _run_script(sample_sqlite)
    assert result.returncode == 0, result.stderr

    for table in ("workspace", "routine", "routine_run", "audit_log", "kb_source"):
        assert f"CREATE TABLE \"public\".\"{table}\"" in result.stdout, (
            f"Missing CREATE TABLE for {table}:\n{result.stdout}"
        )

    # Type mapping sanity checks
    assert '"content_blob" BYTEA' in result.stdout, "BLOB should map to BYTEA"
    assert '"level" INTEGER' in result.stdout, "INTEGER should stay INTEGER"


def test_dry_run_does_not_require_psycopg2(sample_sqlite: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The dry-run path must work even when psycopg2 is not importable."""

    monkeypatch.setitem(sys.modules, "psycopg2", None)
    result = _run_script(sample_sqlite)
    assert result.returncode == 0, result.stderr
    assert "workspace" in result.stdout
