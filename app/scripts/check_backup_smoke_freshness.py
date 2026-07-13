#!/usr/bin/env python3
"""Check freshness of the latest backup/restore smoke report.

Looks for the most recent ``docs/audits/BACKUP_SMOKE_*.md`` report and warns
when it is older than the configured threshold.  Designed to be called from
cron or from a health monitoring probe.

Usage:
    python app/scripts/check_backup_smoke_freshness.py [--threshold-hours 24]
    python app/scripts/check_backup_smoke_freshness.py --run-smoke

Exit codes:
    0  Backup smoke report is fresh.
    1  Report is stale (older than threshold).
    2  No report found.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ambient_detectors import find_latest_backup_smoke_report  # noqa: E402


DEFAULT_THRESHOLD_HOURS = 24


def _run_backup_restore_smoke() -> None:
    """Execute the backup/restore smoke test script."""

    script = Path(__file__).resolve().parent / "backup_restore_smoke.py"
    subprocess.run([sys.executable, str(script)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check freshness of the latest backup smoke report"
    )
    parser.add_argument(
        "--threshold-hours",
        type=int,
        default=DEFAULT_THRESHOLD_HOURS,
        help=f"Maximum accepted age in hours (default: {DEFAULT_THRESHOLD_HOURS})",
    )
    parser.add_argument(
        "--run-smoke",
        action="store_true",
        help="Run backup_restore_smoke.py if the report is missing or stale",
    )
    parser.add_argument(
        "--audits-dir",
        type=Path,
        default=None,
        help="Directory containing BACKUP_SMOKE_*.md reports "
             "(default: docs/audits relative to repo root)",
    )
    args = parser.parse_args()

    audits_dir = args.audits_dir or (
        Path(__file__).resolve().parents[2] / "docs" / "audits"
    )
    result = find_latest_backup_smoke_report(audits_dir)
    now = datetime.now(timezone.utc)

    if result is None:
        print(
            f"CRITICAL: no BACKUP_SMOKE_*.md report found in {audits_dir}",
            file=sys.stderr,
        )
        if args.run_smoke:
            print("Running backup_restore_smoke.py ...", file=sys.stderr)
            _run_backup_restore_smoke()
            result = find_latest_backup_smoke_report(audits_dir)
        if result is None:
            return 2

    latest, mtime = result
    age_hours = (now - mtime).total_seconds() / 3600

    if age_hours > args.threshold_hours:
        print(
            f"WARNING: latest backup smoke report {latest.name} is "
            f"{age_hours:.1f}h old (threshold {args.threshold_hours}h)",
            file=sys.stderr,
        )
        if args.run_smoke:
            print("Running backup_restore_smoke.py ...", file=sys.stderr)
            _run_backup_restore_smoke()
            result = find_latest_backup_smoke_report(audits_dir)
            if result is not None:
                latest, mtime = result
                age_hours = (now - mtime).total_seconds() / 3600
        if age_hours > args.threshold_hours:
            return 1

    print(
        f"OK: latest backup smoke report {latest.name} is "
        f"{age_hours:.1f}h old (threshold {args.threshold_hours}h)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
