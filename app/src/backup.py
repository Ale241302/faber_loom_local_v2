"""FaberLoom backup/export/restore helpers.

Exports the whole SQLite database to a single archive file.  When a passphrase is
provided the payload is encrypted with Fernet (AES-128-CBC + HMAC) using a key
derived from the passphrase via PBKDF2-HMAC-SHA256.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .models import SCHEMA_VERSION

try:
    import sqlcipher3
except Exception:  # pragma: no cover - runtime environment may lack sqlcipher3
    sqlcipher3 = None  # type: ignore[assignment]


SALT_LEN = 16
ITERATIONS = 480_000


def _derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a Fernet key from passphrase + salt."""

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase.encode("utf-8")))


def _encrypt(plaintext: bytes, passphrase: str) -> bytes:
    salt = os.urandom(SALT_LEN)
    f = Fernet(_derive_key(passphrase, salt))
    return salt + f.encrypt(plaintext)


def _decrypt(ciphertext: bytes, passphrase: str) -> bytes:
    if len(ciphertext) < SALT_LEN:
        raise ValueError("Archive is too short to contain salt")
    salt = ciphertext[:SALT_LEN]
    f = Fernet(_derive_key(passphrase, salt))
    return f.decrypt(ciphertext[SALT_LEN:])


def _read_schema_version(raw_db: bytes) -> int | None:
    """Return the schema version stored inside a SQLite database file."""

    tmpdir = tempfile.mkdtemp()
    try:
        temp_path = Path(tmpdir) / "check.sqlite3"
        temp_path.write_bytes(raw_db)
        try:
            with sqlite3.connect(temp_path) as conn:
                row = conn.execute(
                    "SELECT MAX(version) FROM _schema_version"
                ).fetchone()
                return row[0] if row and row[0] is not None else None
        except sqlite3.Error:
            return None
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def export_db(
    db_path: Path | str,
    output_path: Path | str,
    *,
    passphrase: str | None = None,
    db_key: str | None = None,
) -> dict[str, Any]:
    """Export the SQLite database to a `.faberloom` archive.

    Archive layout (zip):
      meta.json  -> {"version": 1, "encrypted": bool, "original_name": str, "schema_version": int}
      db.sqlite3 -> (optional) encrypted bytes of the original SQLite file

    ``db_key`` is the SQLCipher passphrase for encrypted workspace databases.
    ``passphrase`` encrypts the archive itself with Fernet.
    """

    db_path = Path(db_path)
    output_path = Path(output_path)

    # Ensure the database file is fully checkpointed so the exported file is
    # self-contained.  For SQLCipher databases we need the workspace key.
    if db_key is not None:
        if sqlcipher3 is None:
            raise RuntimeError("sqlcipher3 is not available; cannot export encrypted database")
        conn = sqlcipher3.connect(str(db_path), check_same_thread=False)
        escaped = db_key.replace("'", "''")
        conn.execute(f"PRAGMA key = '{escaped}'")
    else:
        conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()

    raw = db_path.read_bytes()
    encrypted = passphrase is not None

    if encrypted:
        payload = _encrypt(raw, passphrase)
    else:
        payload = raw

    meta = {
        "version": 1,
        "encrypted": encrypted,
        "original_name": db_path.name,
        "schema_version": SCHEMA_VERSION,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("meta.json", json.dumps(meta, ensure_ascii=False))
        zf.writestr("db.sqlite3", payload)

    return {
        "archive_path": str(output_path),
        "encrypted": encrypted,
        "size_bytes": len(payload),
    }


def restore_db(
    archive_path: Path | str,
    db_path: Path | str,
    *,
    passphrase: str | None = None,
) -> dict[str, Any]:
    """Restore the database from a `.faberloom` archive.

    The existing db_path is backed up to db_path.backup.<timestamp> before
    overwriting.  Returns the path to the backup.
    """

    archive_path = Path(archive_path)
    db_path = Path(db_path)

    with zipfile.ZipFile(archive_path, "r") as zf:
        meta = json.loads(zf.read("meta.json"))
        payload = zf.read("db.sqlite3")

    if meta.get("encrypted") and passphrase is None:
        raise ValueError("Archive is encrypted; passphrase required")
    if not meta.get("encrypted") and passphrase is not None:
        raise ValueError("Archive is not encrypted; do not pass passphrase")

    if meta.get("encrypted"):
        try:
            raw = _decrypt(payload, passphrase)
        except InvalidToken as exc:
            raise ValueError("Incorrect passphrase or corrupted archive") from exc
    else:
        raw = payload

    archive_schema = _read_schema_version(raw)
    if archive_schema is not None and archive_schema != SCHEMA_VERSION:
        raise ValueError(
            f"Backup schema version {archive_schema} does not match "
            f"current schema version {SCHEMA_VERSION}"
        )

    backup_path = db_path.with_suffix(f"{db_path.suffix}.backup.{_ts()}")
    if db_path.exists():
        shutil.copy2(db_path, backup_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.write_bytes(raw)

    return {
        "restored_path": str(db_path),
        "backup_path": str(backup_path) if backup_path.exists() else None,
        "meta": meta,
    }


def _ts() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def smoke_test_export_restore(
    db_path: Path | str,
    passphrase: str | None = "smoke-test-passphrase",
) -> dict[str, Any]:
    """End-to-end smoke test: export, corrupt original, restore, verify data."""

    db_path = Path(db_path)
    with tempfile.TemporaryDirectory() as tmpdir:
        archive = Path(tmpdir) / "backup.faberloom"
        export_info = export_db(db_path, archive, passphrase=passphrase)

        # Corrupt the live database (simulate loss).
        original_size = db_path.stat().st_size
        db_path.write_text("corrupted")

        restore_info = restore_db(archive, db_path, passphrase=passphrase)

        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            version = conn.execute(
                "SELECT MAX(version) FROM _schema_version"
            ).fetchone()[0]
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            workspace_count = conn.execute(
                "SELECT COUNT(*) FROM workspace"
            ).fetchone()[0]
            source_count = conn.execute(
                "SELECT COUNT(*) FROM kb_source"
            ).fetchone()[0]
            draft_count = conn.execute(
                "SELECT COUNT(*) FROM draft"
            ).fetchone()[0]

        assert db_path.stat().st_size >= original_size * 0.9, "Restored DB too small"
        assert "workspace" in tables
        assert "kb_source" in tables
        assert "draft" in tables
        assert workspace_count >= 1, "No workspace restored"
        assert source_count >= 1, "No kb_source restored"

        return {
            "export": export_info,
            "restore": restore_info,
            "schema_version": version,
            "tables": sorted(tables),
            "workspace_count": workspace_count,
            "source_count": source_count,
            "draft_count": draft_count,
        }
