"""E3-2 — Migración de objetos legacy a prefijo por tenant (`t-{tenant}/ws-{workspace}`)."""

from __future__ import annotations

import importlib.util
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


def _load_migration_module() -> Any:
    script = Path(__file__).resolve().parents[1] / "scripts" / "migrate_minio_objects_to_tenant_prefix.py"
    spec = importlib.util.spec_from_file_location("migrate_minio_prefix", script)
    module = importlib.util.module_from_spec(spec)
    sys.modules["migrate_minio_prefix"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv("FABERLOOM_USERS", '{"test@example.test":"password"}')
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)

    from app.src.main import create_app
    from app.src.storage import reset_object_store

    reset_object_store()
    with TestClient(create_app()) as test_client:
        yield test_client


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _app_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_DB_PATH"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _auth_headers(tenant_id: str, role: str = "owner", user_id: str = "usr_test") -> dict[str, str]:
    from app.src.auth import create_access_token

    token = create_access_token(
        "test@example.test",
        tenant_id=tenant_id,
        user_id=user_id,
        role=role,
    )
    return {"Authorization": f"Bearer {token}"}


def _bootstrap_tenant(client: TestClient, slug: str, owner_email: str) -> str:
    from app.src.foundation.core import new_id, seed_system_roles, utcnow

    conn = _foundation_conn(client)
    try:
        tenant_id = new_id("tnt")
        conn.execute(
            """
            INSERT INTO fnd_tenants
            (id, name, slug, status, plan, created_at, activated_at)
            VALUES (?, ?, ?, 'active', 'starter', ?, ?)
            """,
            (tenant_id, f"Tenant {slug}", slug, utcnow(), utcnow()),
        )
        seed_system_roles(conn, tenant_id)
        user_id = new_id("usr")
        conn.execute(
            """
            INSERT INTO fnd_users
            (id, tenant_id, email, display_name, password_hash, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?)
            """,
            (
                user_id,
                tenant_id,
                owner_email,
                owner_email.split("@")[0],
                "irrelevant",
                utcnow(),
            ),
        )
        role_row = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = 'owner'",
            (tenant_id,),
        ).fetchone()
        conn.execute(
            """
            INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (tenant_id, user_id, role_row["id"], user_id, utcnow()),
        )
        conn.commit()
        return tenant_id
    finally:
        conn.close()


def _create_workspace(client: TestClient, tenant_id: str) -> dict[str, Any]:
    resp = client.post(
        "/api/workspaces",
        json={"name": "Migration Test Workspace"},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _insert_legacy_object(
    client: TestClient,
    workspace_id: str,
    tenant_id: str | None,
    bucket: str,
    legacy_key: str,
    data: bytes,
) -> str:
    from app.src.storage import get_object_store

    store = get_object_store()
    store.put_object(bucket, legacy_key, data, "application/octet-stream")

    conn = _app_conn(client)
    try:
        object_id = f"obj_{os.urandom(8).hex()}"
        conn.execute(
            """
            INSERT INTO object (
                id, workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision,
                origin, bucket, object_key, file_name, mime_type, size_bytes, sha256,
                meta_json, ingest_status, source_type, source_version, workspace_hmac,
                schema_version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                object_id,
                workspace_id,
                tenant_id,
                "tester",
                "tester",
                "owner",
                "upload",
                bucket,
                legacy_key,
                "fixture.txt",
                "text/plain",
                len(data),
                "sha256-dummy",
                "{}",
                "pending",
                None,
                "v1",
                "legacy-hmac",
                41,
                "2026-01-01T00:00:00Z",
                "2026-01-01T00:00:00Z",
            ),
        )
        conn.commit()
        return object_id
    finally:
        conn.close()


def test_dry_run_lists_legacy_objects(client: TestClient) -> None:
    module = _load_migration_module()
    tenant_id = _bootstrap_tenant(client, "dryrun", "dryrun@example.test")
    ws = _create_workspace(client, tenant_id)
    legacy_key = f"ws-{ws['id']}/upload/obj_xxx/fixture.txt"
    data = b"legacy blob"
    _insert_legacy_object(client, ws["id"], tenant_id, "fl-uploads", legacy_key, data)

    rc = module.main(["--execute", "--yes"])  # real migration to set baseline
    assert rc == 0

    tenant_id2 = _bootstrap_tenant(client, "dryrun2", "dryrun2@example.test")
    ws2 = _create_workspace(client, tenant_id2)
    legacy_key2 = f"ws-{ws2['id']}/upload/obj_yyy/fixture.txt"
    _insert_legacy_object(client, ws2["id"], tenant_id2, "fl-uploads", legacy_key2, b"legacy blob 2")

    rc = module.main([])  # dry-run
    assert rc == 0

    conn = _app_conn(client)
    try:
        row = conn.execute(
            "SELECT object_key FROM object WHERE workspace_id = ?", (ws2["id"],)
        ).fetchone()
        assert row["object_key"] == legacy_key2
    finally:
        conn.close()


def test_migrate_legacy_objects_to_tenant_prefix(client: TestClient) -> None:
    module = _load_migration_module()
    tenant_id = _bootstrap_tenant(client, "migrate", "migrate@example.test")
    ws = _create_workspace(client, tenant_id)
    legacy_key = f"ws-{ws['id']}/upload/obj_zzz/fixture.txt"
    data = b"tenant prefixed migration"
    _insert_legacy_object(client, ws["id"], tenant_id, "fl-uploads", legacy_key, data)

    rc = module.main(["--execute", "--yes"])
    assert rc == 0

    conn = _app_conn(client)
    try:
        row = conn.execute(
            "SELECT object_key, tenant_id FROM object WHERE workspace_id = ?", (ws["id"],)
        ).fetchone()
        expected_prefix = f"t-{tenant_id}/ws-{ws['id']}"
        assert row["object_key"].startswith(expected_prefix)
        assert row["tenant_id"] == tenant_id
    finally:
        conn.close()

    from app.src.storage import get_object_store

    store = get_object_store()
    new_key = row["object_key"]
    assert store.get_object("fl-uploads", new_key) == data
    assert store.object_exists("fl-uploads", legacy_key)


def test_migrate_resolves_tenant_from_workspace(client: TestClient) -> None:
    module = _load_migration_module()
    tenant_id = _bootstrap_tenant(client, "resolve", "resolve@example.test")
    ws = _create_workspace(client, tenant_id)
    legacy_key = f"ws-{ws['id']}/generated/obj_aaa/fixture.txt"
    data = b"resolved tenant"
    # Insertar con tenant_id NULL para forzar la resolución desde workspace
    _insert_legacy_object(client, ws["id"], None, "fl-generated", legacy_key, data)

    rc = module.main(["--execute", "--yes"])
    assert rc == 0

    conn = _app_conn(client)
    try:
        row = conn.execute(
            "SELECT object_key, tenant_id FROM object WHERE workspace_id = ?", (ws["id"],)
        ).fetchone()
        assert row["tenant_id"] == tenant_id
        assert f"t-{tenant_id}/ws-{ws['id']}" in row["object_key"]
    finally:
        conn.close()


def test_migrate_skips_already_prefixed_objects(client: TestClient) -> None:
    module = _load_migration_module()
    tenant_id = _bootstrap_tenant(client, "skip", "skip@example.test")
    ws = _create_workspace(client, tenant_id)
    prefixed_key = f"t-{tenant_id}/ws-{ws['id']}/upload/obj_bbb/fixture.txt"
    _insert_legacy_object(client, ws["id"], tenant_id, "fl-uploads", prefixed_key, b"already prefixed")

    rc = module.main(["--execute", "--yes"])
    assert rc == 0

    conn = _app_conn(client)
    try:
        row = conn.execute(
            "SELECT object_key FROM object WHERE workspace_id = ?", (ws["id"],)
        ).fetchone()
        assert row["object_key"] == prefixed_key
    finally:
        conn.close()
