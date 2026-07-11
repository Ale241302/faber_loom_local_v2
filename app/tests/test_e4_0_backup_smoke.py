"""E4-0 backup/restore smoke test (E3-1 gap closure)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from app.src.backup import export_db
from app.src.db import get_database_path


def test_backup_restore_smoke(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    db_path = tmp_path / "faberloom.sqlite3"
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    from app.src.db import connect, initialize_database
    from app.src.models import SCHEMA_VERSION

    conn = connect()
    initialize_database(conn)

    # Seed minimal synthetic data.
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO workspace (id, name, slug, tenant_id, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("ws_test", "Test", "test", "default", "2026-01-01T00:00:00Z", "2026-01-01T00:00:00Z"),
        )
        conn.execute(
            "INSERT INTO kb_source (id, workspace_id, tenant_id, type, title, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("src_test", "ws_test", "default", "text", "Source", "2026-01-01T00:00:00Z"),
        )
        conn.execute(
            "INSERT INTO usage_record (id, workspace_id, tenant_id, provider_slug, model, cost_usd, status, step_index, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("usg_test", "ws_test", "default", "fake", "fake-model", 0.001, "succeeded", 0, "2026-01-01T00:00:00Z"),
        )
        conn.commit()

    archive = backup_dir / "latest.faberloom"
    export_db(db_path, archive)

    # Run the smoke script against the backup directory.
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "app/scripts/backup_restore_smoke.py", "--backup-dir", str(backup_dir)],
        cwd=str(Path(__file__).resolve().parents[2]),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "OK=True" in result.stdout

    # Find the generated report (script runs from repo root).
    repo_root = Path(__file__).resolve().parents[2]
    reports = sorted((repo_root / "docs/audits").glob("BACKUP_SMOKE_*.md"))
    assert reports, "No backup smoke report generated"
    report = reports[-1].read_text(encoding="utf-8")
    assert f"**Schema version:** {SCHEMA_VERSION}" in report
    assert "| workspace | 1 |" in report
    assert "| kb_source | 1 |" in report
    assert "| usage_record | 1 |" in report
    assert "**OK:** YES" in report
