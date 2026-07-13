"""E5-1/E5-6 — weekly reports runner integrates soak + routing per tenant."""

from __future__ import annotations

import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.scripts.run_weekly_reports import main


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        '{"admin@platform.test":"admin-pass","owner@acme.test":"owner-pass"}',
    )
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)

    from app.src.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _create_foundation_user(
    conn: sqlite3.Connection,
    tenant_id: str,
    email: str,
    role: str,
) -> str:
    from app.src.foundation.core import hash_password, new_id, seed_system_roles, utcnow

    seed_system_roles(conn, tenant_id)
    user_id = new_id("usr")
    now = utcnow()
    conn.execute(
        """
        INSERT INTO fnd_users
        (id, tenant_id, email, display_name, password_hash, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'active', ?)
        """,
        (
            user_id,
            tenant_id,
            email,
            email.split("@")[0],
            hash_password("irrelevant-for-legacy-login"),
            now,
        ),
    )
    role_row = conn.execute(
        "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?",
        (tenant_id, role),
    ).fetchone()
    assert role_row is not None
    conn.execute(
        """
        INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (tenant_id, user_id, role_row["id"], user_id, now),
    )
    return user_id


def _bootstrap_tenant(client: TestClient, email: str, role: str, slug: str) -> str:
    from app.src.foundation.core import new_id, utcnow

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
        _create_foundation_user(conn, tenant_id, email, role)
        conn.commit()
        return tenant_id
    finally:
        conn.close()


def _app_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_DB_PATH"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _seed_workspace(conn: sqlite3.Connection, tenant_id: str) -> str:
    from app.src.db import utc_now

    workspace_id = f"ws_{tenant_id}"
    seal_id = uuid.uuid4().hex
    now = utc_now()
    conn.execute(
        """
        INSERT INTO workspace (
            id, name, slug, tenant_id, seal_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (workspace_id, f"WS {tenant_id}", f"ws-{tenant_id}", tenant_id, seal_id, now, now),
    )
    conn.commit()
    return workspace_id


def test_weekly_reports_generates_files(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-weekly")
    conn = _app_conn(client)
    try:
        _seed_workspace(conn, tenant_id)
    finally:
        conn.close()

    out_dir = tmp_path / "weekly"

    # Canary returns clean without running real isolation logic.
    import app.scripts.soak_report as soak_module

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        soak_module,
        "_run_canary",
        lambda db_path, foundation_db: {
            "status": "clean",
            "exit_code": 0,
            "summary": "OK",
        },
    )
    try:
        code = main(
            [
                "--db-path",
                os.environ["FABERLOOM_DB_PATH"],
                "--foundation-db",
                os.environ["FABERLOOM_FOUNDATION_DB"],
                "--out-dir",
                str(out_dir),
                "--week",
                "1",
                "--days",
                "7",
            ]
        )
    finally:
        monkeypatch.undo()

    assert code == 0
    assert (out_dir / f"SOAK_{tenant_id}_S1.md").exists()
    assert len(list(out_dir.glob(f"EVIDENCIA_ROUTING_{tenant_id}_*.md"))) == 1
