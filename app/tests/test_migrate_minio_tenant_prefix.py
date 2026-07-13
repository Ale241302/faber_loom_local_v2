"""Tests para migrate_minio_tenant_prefix.py.

Usa un backend en memoria (dict) y SQLite local; no requiere MinIO/Postgres reales.
"""

from __future__ import annotations

import importlib.util
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest


def _load_module() -> Any:
    script = Path(__file__).resolve().parents[1] / "scripts" / "migrate_minio_tenant_prefix.py"
    spec = importlib.util.spec_from_file_location("migrate_minio_tenant_prefix", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["migrate_minio_tenant_prefix"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def module() -> Any:
    return _load_module()


@pytest.fixture()
def db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE workspace (
            id TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL
        );
        CREATE TABLE object (
            id TEXT PRIMARY KEY,
            workspace_id TEXT NOT NULL,
            tenant_id TEXT,
            origin TEXT NOT NULL,
            bucket TEXT NOT NULL,
            object_key TEXT NOT NULL,
            file_name TEXT,
            size_bytes INTEGER,
            sha256 TEXT,
            updated_at TEXT
        );
        """
    )
    return conn


@pytest.fixture()
def memory_store(module: Any, monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")
    from app.src.storage import ObjectStore

    return ObjectStore(backend="memory")


def _insert_object(
    conn: sqlite3.Connection,
    object_id: str,
    workspace_id: str,
    tenant_id: str | None,
    bucket: str,
    object_key: str,
    file_name: str,
    size: int,
    origin: str = "upload",
) -> None:
    conn.execute(
        """
        INSERT INTO object (id, workspace_id, tenant_id, origin, bucket, object_key, file_name, size_bytes, sha256)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (object_id, workspace_id, tenant_id, origin, bucket, object_key, file_name, size, "sha256-dummy"),
    )
    conn.execute(
        "INSERT OR IGNORE INTO workspace (id, tenant_id) VALUES (?, ?)",
        (workspace_id, tenant_id or "t_default"),
    )
    conn.commit()


def test_dry_run_does_not_modify(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any
) -> None:
    old_key = "ws-ws1/upload/obj_1/file.txt"
    data = b"legacy blob"
    memory_store.put_object("fl-uploads", old_key, data, "text/plain")
    _insert_object(db_conn, "obj_1", "ws1", "t1", "fl-uploads", old_key, "file.txt", len(data))

    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-uploads"],
        dry_run=True,
    )

    assert report["total_objects"] == 1
    assert report["migrated"] == 0
    assert report["failed"] == 0
    assert report["objects"][0]["status"] == "planned"

    row = db_conn.execute("SELECT object_key, tenant_id FROM object WHERE id = ?", ("obj_1",)).fetchone()
    assert row["object_key"] == old_key
    assert row["tenant_id"] == "t1"

    assert memory_store.object_exists("fl-uploads", old_key)
    assert not memory_store.object_exists("fl-uploads", "tenant/t1/ws-ws1/upload/obj_1/file.txt")


def test_execute_migrates_object_key(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any
) -> None:
    old_key = "ws-ws1/upload/obj_1/file.txt"
    data = b"legacy blob"
    memory_store.put_object("fl-uploads", old_key, data, "text/plain")
    _insert_object(db_conn, "obj_1", "ws1", "t1", "fl-uploads", old_key, "file.txt", len(data))

    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-uploads"],
        dry_run=False,
    )

    assert report["total_objects"] == 1
    assert report["migrated"] == 1
    assert report["failed"] == 0

    row = db_conn.execute("SELECT object_key, tenant_id FROM object WHERE id = ?", ("obj_1",)).fetchone()
    expected = "tenant/t1/ws-ws1/upload/obj_1/file.txt"
    assert row["object_key"] == expected
    assert row["tenant_id"] == "t1"

    assert memory_store.object_exists("fl-uploads", expected)
    assert not memory_store.object_exists("fl-uploads", old_key)
    assert memory_store.object_exists("fl-uploads", "_quarantine/" + old_key)
    assert memory_store.get_object("fl-uploads", expected) == data


def test_execute_migrates_from_old_tenant_prefix(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any
) -> None:
    old_key = "t-t1/ws-ws1/generated/obj_2/file.pdf"
    data = b"generated pdf"
    memory_store.put_object("fl-generated", old_key, data, "application/pdf")
    _insert_object(
        db_conn, "obj_2", "ws1", "t1", "fl-generated", old_key, "file.pdf", len(data), origin="generated"
    )

    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-generated"],
        dry_run=False,
    )

    assert report["migrated"] == 1
    expected = "tenant/t1/ws-ws1/generated/obj_2/file.pdf"
    row = db_conn.execute("SELECT object_key FROM object WHERE id = ?", ("obj_2",)).fetchone()
    assert row["object_key"] == expected
    assert memory_store.get_object("fl-generated", expected) == data


def test_resolves_tenant_from_workspace(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any
) -> None:
    old_key = "ws-ws1/upload/obj_3/file.txt"
    data = b"resolved tenant"
    memory_store.put_object("fl-uploads", old_key, data, "text/plain")
    _insert_object(
        db_conn, "obj_3", "ws1", None, "fl-uploads", old_key, "file.txt", len(data)
    )

    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-uploads"],
        dry_run=False,
    )

    assert report["migrated"] == 1
    row = db_conn.execute("SELECT object_key, tenant_id FROM object WHERE id = ?", ("obj_3",)).fetchone()
    expected = "tenant/t_default/ws-ws1/upload/obj_3/file.txt"
    assert row["object_key"] == expected
    assert row["tenant_id"] == "t_default"


def test_skips_already_tenant_prefixed_objects(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any
) -> None:
    key = "tenant/t1/ws-ws1/upload/obj_4/file.txt"
    data = b"already migrated"
    memory_store.put_object("fl-uploads", key, data, "text/plain")
    _insert_object(db_conn, "obj_4", "ws1", "t1", "fl-uploads", key, "file.txt", len(data))

    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-uploads"],
        dry_run=False,
    )

    assert report["total_objects"] == 1
    assert report["skipped_already_migrated"] == 1
    assert report["migrated"] == 0
    row = db_conn.execute("SELECT object_key FROM object WHERE id = ?", ("obj_4",)).fetchone()
    assert row["object_key"] == key


def test_reports_orphan_objects(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any
) -> None:
    key = "random.png"
    data = b"orphan image"
    memory_store.put_object("fl-uploads", key, data, "image/png")

    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-uploads"],
        dry_run=False,
    )

    assert report["total_objects"] == 1
    assert report["orphans"] == 1
    assert report["migrated"] == 0
    assert report["objects"][0]["status"] == "orphan"
    # El objeto huérfano no debe tocarse
    assert memory_store.object_exists("fl-uploads", key)
    assert not memory_store.object_exists("fl-uploads", "_quarantine/" + key)


def test_tenant_filter_only_processes_matching_objects(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any
) -> None:
    # obj_t1 pertenece a t1, obj_t2 a t2
    memory_store.put_object("fl-uploads", "ws-ws_t1/upload/obj_t1/a.txt", b"a", "text/plain")
    memory_store.put_object("fl-uploads", "ws-ws_t2/upload/obj_t2/b.txt", b"b", "text/plain")
    _insert_object(db_conn, "obj_t1", "ws_t1", "t1", "fl-uploads", "ws-ws_t1/upload/obj_t1/a.txt", "a.txt", 1)
    _insert_object(db_conn, "obj_t2", "ws_t2", "t2", "fl-uploads", "ws-ws_t2/upload/obj_t2/b.txt", "b.txt", 1)

    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-uploads"],
        dry_run=False,
        tenant="t1",
    )

    assert report["migrated"] == 1
    assert report["total_objects"] == 2
    statuses = {o["object_id"]: o["status"] for o in report["objects"]}
    assert statuses["obj_t1"] == "migrated"
    assert statuses["obj_t2"] == "filtered"


def test_unstructured_object_resolved_by_db(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any
) -> None:
    key = "fl-uploads/testobj3.png"
    data = b"\x89PNG\r\n\x1a\n"
    memory_store.put_object("fl-uploads", key, data, "image/png")
    _insert_object(
        db_conn, "obj_x", "ws1", "t1", "fl-uploads", key, "testobj3.png", len(data), origin="upload"
    )

    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-uploads"],
        dry_run=False,
    )

    assert report["migrated"] == 1
    expected = "tenant/t1/ws-ws1/upload/obj_x/testobj3.png"
    row = db_conn.execute("SELECT object_key FROM object WHERE id = ?", ("obj_x",)).fetchone()
    assert row["object_key"] == expected
    assert memory_store.object_exists("fl-uploads", expected)
    assert memory_store.object_exists("fl-uploads", "_quarantine/" + key)


def test_structured_path_missing_object_id_is_orphan(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any
) -> None:
    """Un path estructurado cuyo object_id no existe en DB es huérfano, no failed."""
    old_key = "t-t1/ws-ws1/upload/obj_missing/step-output.json"
    data = b'{}'
    memory_store.put_object("fl-generated", old_key, data, "application/json")

    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-generated"],
        dry_run=True,
    )

    assert report["total_objects"] == 1
    assert report["orphans"] == 1
    assert report["failed"] == 0
    obj = report["objects"][0]
    assert obj["status"] == "orphan"
    assert "object_id not found" in obj["error"]


def test_report_json_written_to_disk(
    module: Any, db_conn: sqlite3.Connection, memory_store: Any, tmp_path: Path
) -> None:
    key = "ws-ws1/upload/obj_5/file.txt"
    memory_store.put_object("fl-uploads", key, b"x", "text/plain")
    _insert_object(db_conn, "obj_5", "ws1", "t1", "fl-uploads", key, "file.txt", 1)

    report_path = tmp_path / "report.json"
    report = module.run_migration(
        db_conn,
        memory_store,
        buckets=["fl-uploads"],
        dry_run=True,
        report_path=str(report_path),
    )

    assert report_path.exists()
    import json

    with open(report_path, "r", encoding="utf-8") as fh:
        saved = json.load(fh)
    assert saved["dry_run"] is True
    assert saved["total_objects"] == 1
    assert saved["objects"][0]["old_key"] == key
