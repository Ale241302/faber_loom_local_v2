"""Tests for E5-2 backup smoke freshness detector and CLI script.

These tests complement the ambient-cycle integration tests in
``test_ambient.py`` by focusing on the read-only contract and the
``check_backup_smoke_freshness.py`` CLI.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture()
def audits_dir(tmp_path: Path) -> Path:
    d = tmp_path / "audits"
    d.mkdir()
    return d


def _write_report(audits_dir: Path, name: str, mtime: datetime) -> Path:
    path = audits_dir / name
    path.write_text("# Backup smoke\n", encoding="utf-8")
    ts = mtime.timestamp()
    path.touch(exist_ok=True)
    # Set both access and modification time to the requested timestamp.
    import os

    os.utime(path, (ts, ts))
    return path


def test_check_freshness_no_report(audits_dir: Path) -> None:
    from app.scripts.check_backup_smoke_freshness import check_freshness

    result = check_freshness(audits_dir, max_age_hours=24)
    assert result["fresh"] is False
    assert result["latest_report"] is None
    assert result["ok"] is False


def test_check_freshness_fresh(audits_dir: Path) -> None:
    from app.scripts.check_backup_smoke_freshness import check_freshness

    _write_report(
        audits_dir,
        "BACKUP_SMOKE_20260713T120000Z.md",
        datetime.now(timezone.utc) - timedelta(hours=1),
    )
    result = check_freshness(audits_dir, max_age_hours=24)
    assert result["fresh"] is True
    assert result["latest_report"] is not None
    assert result["age_hours"] <= 24
    assert result["ok"] is True


def test_check_freshness_stale(audits_dir: Path) -> None:
    from app.scripts.check_backup_smoke_freshness import check_freshness

    _write_report(
        audits_dir,
        "BACKUP_SMOKE_20260711T120000Z.md",
        datetime.now(timezone.utc) - timedelta(hours=48),
    )
    result = check_freshness(audits_dir, max_age_hours=24)
    assert result["fresh"] is False
    assert result["age_hours"] > 24
    assert result["ok"] is False


def test_detector_is_read_only(audits_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The detector must not write to the database."""

    from app.src.ambient_detectors import detect_stale_backup_smoke
    from app.src.context import Context

    fresh_mtime = datetime.now(timezone.utc) - timedelta(hours=1)
    from app.src import ambient_detectors as ad

    monkeypatch.setattr(
        ad,
        "find_latest_backup_smoke_report",
        lambda _path: (Path("BACKUP_SMOKE_20260713T120000Z.md"), fresh_mtime),
    )

    # Passing None as the DB connection proves the detector does not touch it
    # for a fresh report.
    ctx = Context(workspace_id="ws", tenant_id="default")
    findings = detect_stale_backup_smoke(ctx, None)
    assert findings == []


def test_cli_fresh_report(audits_dir: Path) -> None:
    _write_report(
        audits_dir,
        "BACKUP_SMOKE_20260713T120000Z.md",
        datetime.now(timezone.utc) - timedelta(hours=1),
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "check_backup_smoke_freshness.py"
    result = subprocess.run(
        [sys.executable, str(script), "--audits-dir", str(audits_dir), "--max-age-hours", "24"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "OK:" in result.stdout


def test_cli_stale_report(audits_dir: Path) -> None:
    _write_report(
        audits_dir,
        "BACKUP_SMOKE_20260711T120000Z.md",
        datetime.now(timezone.utc) - timedelta(hours=48),
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "check_backup_smoke_freshness.py"
    result = subprocess.run(
        [sys.executable, str(script), "--audits-dir", str(audits_dir), "--max-age-hours", "24"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "WARNING:" in result.stderr


def test_cli_missing_report(audits_dir: Path) -> None:
    script = Path(__file__).resolve().parents[1] / "scripts" / "check_backup_smoke_freshness.py"
    result = subprocess.run(
        [sys.executable, str(script), "--audits-dir", str(audits_dir), "--max-age-hours", "24"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "CRITICAL:" in result.stderr


def test_cli_json_output(audits_dir: Path) -> None:
    _write_report(
        audits_dir,
        "BACKUP_SMOKE_20260713T120000Z.md",
        datetime.now(timezone.utc) - timedelta(hours=1),
    )
    script = Path(__file__).resolve().parents[1] / "scripts" / "check_backup_smoke_freshness.py"
    result = subprocess.run(
        [sys.executable, str(script), "--audits-dir", str(audits_dir), "--json", "--max-age-hours", "24"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["fresh"] is True
    assert "age_hours" in data
    assert data["max_age_hours"] == 24
