#!/usr/bin/env python3
"""Backup/restore smoke test for E4-0 (E3-1 gap closure).

Locates the most recent ``.faberloom`` backup archive for the configured
database, restores it to a temporary database, compares row counts for
critical tables, and writes a markdown report to ``docs/audits/``.

Usage:
    python app/scripts/backup_restore_smoke.py [--backup-dir DIR]
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Allow running from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backup import restore_db  # noqa: E402
from src.db import get_database_path  # noqa: E402


CRITICAL_TABLES = [
    "fnd_tenants",
    "workspace",
    "kb_source",
    "manual_invoice",
    "usage_record",
]

REQUIRED_TABLES = ["workspace", "kb_source", "usage_record"]


def _find_latest_backup(backup_dir: Path) -> Path | None:
    candidates = sorted(backup_dir.glob("*.faberloom"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _count_rows(conn: sqlite3.Connection, table: str) -> int | None:
    try:
        row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        return int(row[0]) if row else 0
    except sqlite3.Error:
        return None


def run_smoke(*, backup_dir: Path | None = None) -> dict[str, Any]:
    db_path = get_database_path()
    search_dir = backup_dir or db_path.parent
    archive = _find_latest_backup(search_dir)
    if archive is None:
        raise FileNotFoundError(f"No *.faberloom backup found in {search_dir}")

    with tempfile.TemporaryDirectory() as tmpdir:
        restored_path = Path(tmpdir) / "restored.sqlite3"
        restore_info = restore_db(archive, restored_path)

        conn = sqlite3.connect(restored_path)
        try:
            conn.row_factory = sqlite3.Row
            counts: dict[str, int | None] = {}
            for table in CRITICAL_TABLES:
                counts[table] = _count_rows(conn, table)

            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
        finally:
            conn.close()

    missing = [t for t in REQUIRED_TABLES if t not in tables]
    zero = [t for t in REQUIRED_TABLES if counts.get(t) == 0]

    return {
        "archive": str(archive),
        "restored_path": restore_info["restored_path"],
        "backup_path": restore_info.get("backup_path"),
        "schema_version": restore_info["meta"].get("schema_version"),
        "counts": counts,
        "missing_tables": missing,
        "zero_count_tables": zero,
        "ok": not missing and not zero,
    }


def write_report(result: dict[str, Any]) -> Path:
    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = Path("docs/audits") / f"BACKUP_SMOKE_{now}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Backup/Restore Smoke Test",
        "",
        f"**Timestamp:** {now}",
        f"**Archive:** `{result['archive']}`",
        f"**Schema version:** {result.get('schema_version')}",
        "",
        "## Row counts (critical tables)",
        "",
        "| Table | Rows |",
        "|-------|------|",
    ]
    for table, count in result["counts"].items():
        lines.append(f"| {table} | {count if count is not None else 'N/A'} |")

    lines.extend([
        "",
        "## Result",
        "",
        f"- Missing required tables: {result['missing_tables'] or 'None'}",
        f"- Required tables with zero rows: {result['zero_count_tables'] or 'None'}",
        f"- **OK:** {'YES' if result['ok'] else 'NO'}",
        "",
    ])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup/restore smoke test")
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Directory to search for *.faberloom backups (default: same dir as DB)",
    )
    args = parser.parse_args()

    result = run_smoke(backup_dir=args.backup_dir)
    report_path = write_report(result)
    print(f"Report written to {report_path}")
    print(f"OK={result['ok']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
