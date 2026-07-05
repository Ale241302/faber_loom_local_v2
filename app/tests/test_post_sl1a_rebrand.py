"""Post-SL1a v3: rebrand migration and packaging regression tests."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
APP_DIR = ROOT / "app"
BUILD_SCRIPT = APP_DIR / "build.py"
MAIN_FILE = APP_DIR / "src" / "main.py"
INDEX_HTML = APP_DIR / "static" / "index.html"


def test_build_script_targets_faberloom_artifacts() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    assert "FaberLoom.exe" in text
    assert "FaberLoom-Setup.exe" in text
    assert "SpaceLoom" not in text


def test_main_window_title_is_faberloom() -> None:
    text = MAIN_FILE.read_text(encoding="utf-8")
    assert 'webview.create_window(\n        "FaberLoom",' in text


def test_index_html_title_is_faberloom() -> None:
    text = INDEX_HTML.read_text(encoding="utf-8")
    assert "<title>FaberLoom" in text
    assert "SpaceLoom" not in text


def test_fastapi_title_is_faberloom() -> None:
    from app.src.main import create_app

    app = create_app()
    assert "FaberLoom" in app.title


def test_legacy_spaceloom_data_dir_is_migrated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(os, "name", "nt")

    old = tmp_path / "SpaceLoom"
    old_db = old / "spaceloom.sqlite3"
    old.mkdir(parents=True)
    old_db.write_text("legacy database", encoding="utf-8")

    from app.src import db as db_module

    db_module._migrate_legacy_data_dir()

    new = tmp_path / "FaberLoom"
    new_db = new / "faberloom.sqlite3"
    assert new.exists()
    assert not old.exists()
    assert new_db.exists()
    assert new_db.read_text(encoding="utf-8") == "legacy database"


def test_legacy_migration_skips_when_faberloom_already_exists(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(os, "name", "nt")

    new = tmp_path / "FaberLoom"
    new_db = new / "faberloom.sqlite3"
    new.mkdir(parents=True)
    new_db.write_text("faberloom database", encoding="utf-8")

    old = tmp_path / "SpaceLoom"
    old_db = old / "spaceloom.sqlite3"
    old.mkdir(parents=True)
    old_db.write_text("legacy database", encoding="utf-8")

    from app.src import db as db_module

    db_module._migrate_legacy_data_dir()

    assert old.exists()
    assert new_db.read_text(encoding="utf-8") == "faberloom database"


def test_migrated_sqlite_database_loads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(os, "name", "nt")

    old = tmp_path / "SpaceLoom"
    old_db = old / "spaceloom.sqlite3"
    old.mkdir(parents=True)
    conn = sqlite3.connect(str(old_db))
    conn.execute("CREATE TABLE workspaces (id TEXT PRIMARY KEY, name TEXT);")
    conn.execute("INSERT INTO workspaces (id, name) VALUES ('ws_1', 'Legacy');")
    conn.commit()
    conn.close()

    from app.src import db as db_module

    db_module._migrate_legacy_data_dir()

    new_db = tmp_path / "FaberLoom" / "faberloom.sqlite3"
    assert new_db.exists()

    migrated = sqlite3.connect(str(new_db))
    row = migrated.execute("SELECT id, name FROM workspaces").fetchone()
    migrated.close()
    assert row == ("ws_1", "Legacy")


def test_legacy_config_dir_is_migrated_via_config_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setattr(os, "name", "nt")

    old = tmp_path / "SpaceLoom"
    old.mkdir(parents=True)
    (old / "providers.json").write_text("legacy provider config", encoding="utf-8")

    from app.src.router.config_store import get_config_dir

    result = get_config_dir()
    assert result == tmp_path / "FaberLoom"
    assert (result / "providers.json").read_text(encoding="utf-8") == "legacy provider config"
