#!/usr/bin/env python3
"""Check freshness of the latest backup/restore smoke report.

Looks for the most recent ``docs/audits/BACKUP_SMOKE_*.md`` report and warns
when it is older than the configured threshold.  Designed to be called from
cron or from a health monitoring probe.

Usage:
    python app/scripts/check_backup_smoke_freshness.py [--max-age-hours 48]
    python app/scripts/check_backup_smoke_freshness.py --run-smoke
    python app/scripts/check_backup_smoke_freshness.py --json

Exit codes:
    0  Backup smoke report is fresh.
    1  Report is stale (older than threshold).
    2  No report found.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Allow running from repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ambient_detectors import find_latest_backup_smoke_report  # noqa: E402


DEFAULT_MAX_AGE_HOURS = 48


def check_freshness(
    audits_dir: Path,
    max_age_hours: int = DEFAULT_MAX_AGE_HOURS,
) -> dict[str, Any]:
    """Return freshness metadata for the latest backup smoke report.

    Returns a dict with keys:
        - fresh (bool)
        - last_smoke_at (str ISO8601 or None)
        - age_hours (float or None)
        - max_age_hours (int)
        - latest_report (str or None)
        - ok (bool): True when fresh or when a stale/missing report was
          re-generated successfully via ``--run-smoke``.
    """

    result = find_latest_backup_smoke_report(audits_dir)
    if result is None:
        return {
            "fresh": False,
            "last_smoke_at": None,
            "age_hours": None,
            "max_age_hours": max_age_hours,
            "latest_report": None,
            "ok": False,
        }

    latest, mtime = result
    age_hours = (datetime.now(timezone.utc) - mtime).total_seconds() / 3600
    return {
        "fresh": age_hours <= max_age_hours,
        "last_smoke_at": mtime.isoformat(),
        "age_hours": round(age_hours, 2),
        "max_age_hours": max_age_hours,
        "latest_report": latest.name,
        "ok": age_hours <= max_age_hours,
    }


def _run_backup_restore_smoke() -> None:
    """Execute the backup/restore smoke test script."""

    script = Path(__file__).resolve().parent / "backup_restore_smoke.py"
    subprocess.run([sys.executable, str(script)], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check freshness of the latest backup smoke report"
    )
    parser.add_argument(
        "--max-age-hours",
        "--threshold-hours",
        type=int,
        default=DEFAULT_MAX_AGE_HOURS,
        dest="max_age_hours",
        help=f"Maximum accepted age in hours (default: {DEFAULT_MAX_AGE_HOURS})",
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
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output a JSON summary instead of human-readable text",
    )
    args = parser.parse_args()

    audits_dir = args.audits_dir or (
        Path(__file__).resolve().parents[2] / "docs" / "audits"
    )
    result = check_freshness(audits_dir, max_age_hours=args.max_age_hours)

    if result["latest_report"] is None:
        if not args.json:
            print(
                f"CRITICAL: no BACKUP_SMOKE_*.md report found in {audits_dir}",
                file=sys.stderr,
            )
        if args.run_smoke:
            if not args.json:
                print("Running backup_restore_smoke.py ...", file=sys.stderr)
            _run_backup_restore_smoke()
            result = check_freshness(audits_dir, max_age_hours=args.max_age_hours)
        if result["latest_report"] is None:
            if args.json:
                print(json.dumps(result))
            return 2

    if not result["fresh"]:
        if not args.json:
            print(
                f"WARNING: latest backup smoke report {result['latest_report']} is "
                f"{result['age_hours']:.1f}h old (threshold {args.max_age_hours}h)",
                file=sys.stderr,
            )
        if args.run_smoke:
            if not args.json:
                print("Running backup_restore_smoke.py ...", file=sys.stderr)
            _run_backup_restore_smoke()
            result = check_freshness(audits_dir, max_age_hours=args.max_age_hours)
        if not result["fresh"]:
            if args.json:
                print(json.dumps(result))
            return 1

    if args.json:
        print(json.dumps(result))
    else:
        print(
            f"OK: latest backup smoke report {result['latest_report']} is "
            f"{result['age_hours']:.1f}h old (threshold {args.max_age_hours}h)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
