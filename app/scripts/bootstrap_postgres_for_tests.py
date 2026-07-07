#!/usr/bin/env python3
"""Bootstrap a Postgres database for the E3-1 test suite.

Usage:
    export FABERLOOM_TEST_POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/faberloom_test
    python scripts/bootstrap_postgres_for_tests.py

Steps:
1. Create a temporary SQLite database and run the SQLite migrations.
2. Migrate the empty schema to Postgres using sqlite_to_postgres.py.
3. Seed _schema_version so initialize_database() skips SQLite migrations on Postgres.
4. Apply RLS policies so test_e3_1_rls_canary.py can validate isolation.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import psycopg

# Make app/src importable when running from app/ or app/scripts/.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "app"))

from src.db import initialize_database
from src.models import SCHEMA_VERSION


def _postgres_url() -> str:
    return os.environ.get(
        "FABERLOOM_TEST_POSTGRES_URL",
        os.environ.get(
            "FABERLOOM_POSTGRES_URL",
            "postgresql://postgres:postgres@localhost:5432/faberloom_test",
        ),
    )


def _postgres_admin_url() -> str:
    """URL used to apply RLS policies (must be a superuser/owner)."""
    return os.environ.get(
        "FABERLOOM_TEST_POSTGRES_ADMIN_URL",
        os.environ.get(
            "FABERLOOM_POSTGRES_ADMIN_URL",
            _postgres_url(),
        ),
    )


def _sqlite_to_postgres_script() -> Path:
    return REPO_ROOT / "app" / "scripts" / "sqlite_to_postgres.py"


def _rls_policies_script() -> Path:
    return REPO_ROOT / "app" / "scripts" / "postgres_rls_policies.sql"


def main() -> int:
    pg_url = _postgres_url()
    pg_admin_url = _postgres_admin_url()

    # 1. Temporary SQLite with full schema.
    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tmp:
        sqlite_path = tmp.name
    try:
        import sqlite3

        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        initialize_database(conn)
        conn.close()

        # 2. Migrate schema to Postgres.
        cmd = [
            sys.executable,
            str(_sqlite_to_postgres_script()),
            "--sqlite-path",
            sqlite_path,
            "--postgres-url",
            pg_url,
            "--schema",
            "public",
            "--drop-existing",
            "--no-fts-gin",
        ]
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(cmd, check=False, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            print(result.stdout, file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            return result.returncode

        # 3. Seed _schema_version so initialize_database() is a no-op on Postgres.
        with psycopg.connect(pg_url) as pg_conn:
            with pg_conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS _schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL
                    )
                    """
                )
                for version in range(1, SCHEMA_VERSION + 1):
                    cur.execute(
                        """
                        INSERT INTO _schema_version(version, applied_at)
                        VALUES (%s, %s)
                        ON CONFLICT (version) DO NOTHING
                        """,
                        (version, "1970-01-01T00:00:00Z"),
                    )
            pg_conn.commit()

        # 4. Apply RLS policies as the database owner.
        rls_path = _rls_policies_script()
        if rls_path.exists():
            with psycopg.connect(pg_admin_url) as admin_conn:
                with admin_conn.cursor() as cur:
                    cur.execute(rls_path.read_text(encoding="utf-8"))
                admin_conn.commit()

        print(f"Postgres bootstrap complete: {pg_url}")
        return 0
    finally:
        try:
            os.unlink(sqlite_path)
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
