"""E5-3 — validación del carril de carga H3/golden para PACK 2 (comex)."""

from __future__ import annotations

import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.scripts.load_pack2_golden import SYNTHETIC_CASES, main
from app.src.context import Context


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated app with fresh Foundation and app DBs."""

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


def _context(tenant_id: str, workspace_id: str) -> Context:
    return Context(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
        user_id="tester",
        actor_id="tester",
        actor_role_at_decision="operator",
    )


def test_load_pack2_golden_dry_run_does_not_mutate(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-pack2")
    conn = _app_conn(client)
    try:
        workspace_id = _seed_workspace(conn, tenant_id)
    finally:
        conn.close()

    out = tmp_path / "EVIDENCIA_PACK2_CARRIL.md"
    code = main(
        [
            "--tenant-id",
            tenant_id,
            "--workspace-id",
            workspace_id,
            "--synthetic",
            "--db-path",
            os.environ["FABERLOOM_DB_PATH"],
            "--out",
            str(out),
        ]
    )
    assert code == 0
    assert out.exists()

    conn = _app_conn(client)
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM golden_case WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()["n"]
        assert count == 0, "dry-run no debe insertar casos"
    finally:
        conn.close()


def test_load_pack2_golden_synthetic_execute_creates_cases(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-pack2-exec")
    conn = _app_conn(client)
    try:
        workspace_id = _seed_workspace(conn, tenant_id)
    finally:
        conn.close()

    out = tmp_path / "EVIDENCIA_PACK2_CARRIL.md"
    code = main(
        [
            "--tenant-id",
            tenant_id,
            "--workspace-id",
            workspace_id,
            "--synthetic",
            "--execute",
            "--approved-by",
            "usr_tester",
            "--db-path",
            os.environ["FABERLOOM_DB_PATH"],
            "--out",
            str(out),
        ]
    )
    assert code == 0
    assert out.exists()

    conn = _app_conn(client)
    try:
        rows = conn.execute(
            """
            SELECT * FROM golden_case
            WHERE tenant_id = ? AND workspace_id = ?
            ORDER BY skill_id
            """,
            (tenant_id, workspace_id),
        ).fetchall()
        assert len(rows) == len(SYNTHETIC_CASES)

        for row in rows:
            assert row["approved"] == 0
            assert row["verified_by"] is None
            assert row["origin"] == "synthetic"
            assert "[SINTETICO]" in row["input_json"]
            assert "[SINTETICO]" in row["expected_output_json"]

        audit = conn.execute(
            """
            SELECT COUNT(*) AS n FROM audit_log
            WHERE tenant_id = ? AND workspace_id = ? AND action = 'golden_case.synthetic_loaded'
            """,
            (tenant_id, workspace_id),
        ).fetchone()["n"]
        assert audit == len(SYNTHETIC_CASES)

        evidence = conn.execute(
            """
            SELECT COUNT(*) AS n FROM external_evidence
            WHERE entity_type = 'golden_case' AND tenant_id = ?
            """,
            (tenant_id,),
        ).fetchone()["n"]
        assert evidence == len(SYNTHETIC_CASES)
    finally:
        conn.close()


def test_load_pack2_golden_requires_existing_workspace(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-pack2-ws")
    out = tmp_path / "EVIDENCIA_PACK2_CARRIL.md"
    code = main(
        [
            "--tenant-id",
            tenant_id,
            "--workspace-id",
            "ws_inexistente",
            "--synthetic",
            "--execute",
            "--approved-by",
            "usr_tester",
            "--db-path",
            os.environ["FABERLOOM_DB_PATH"],
            "--out",
            str(out),
        ]
    )
    assert code == 1
    assert not out.exists()


def test_load_pack2_golden_source_dir_dry_run(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-pack2-src")
    conn = _app_conn(client)
    try:
        workspace_id = _seed_workspace(conn, tenant_id)
    finally:
        conn.close()

    source_dir = tmp_path / "h3"
    source_dir.mkdir()
    (source_dir / "marluvas_catalogo.md").write_text("# Catálogo Marluvas [SINTETICO]", encoding="utf-8")
    (source_dir / "tecmater_tarifas.csv").write_text("sku,descripcion,precio\nA1,X,10", encoding="utf-8")

    out = tmp_path / "EVIDENCIA_PACK2_CARRIL.md"
    code = main(
        [
            "--tenant-id",
            tenant_id,
            "--workspace-id",
            workspace_id,
            "--source-dir",
            str(source_dir),
            "--db-path",
            os.environ["FABERLOOM_DB_PATH"],
            "--out",
            str(out),
        ]
    )
    assert code == 0
    assert out.exists()

    conn = _app_conn(client)
    try:
        kb_count = conn.execute(
            "SELECT COUNT(*) AS n FROM kb_source WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()["n"]
        assert kb_count == 0, "dry-run no debe ingest KB"
    finally:
        conn.close()


def test_load_pack2_golden_source_dir_and_synthetic_execute(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-pack2-full")
    conn = _app_conn(client)
    try:
        workspace_id = _seed_workspace(conn, tenant_id)
    finally:
        conn.close()

    source_dir = tmp_path / "h3"
    source_dir.mkdir()
    (source_dir / "marluvas_catalogo.md").write_text("# Catálogo Marluvas [SINTETICO]", encoding="utf-8")
    (source_dir / "tecmater_tarifas.csv").write_text("sku,descripcion,precio\nA1,X,10", encoding="utf-8")

    out = tmp_path / "EVIDENCIA_PACK2_CARRIL.md"
    code = main(
        [
            "--tenant-id",
            tenant_id,
            "--workspace-id",
            workspace_id,
            "--source-dir",
            str(source_dir),
            "--synthetic",
            "--execute",
            "--approved-by",
            "usr_operador",
            "--db-path",
            os.environ["FABERLOOM_DB_PATH"],
            "--out",
            str(out),
        ]
    )
    assert code == 0

    conn = _app_conn(client)
    try:
        kb_count = conn.execute(
            "SELECT COUNT(*) AS n FROM kb_source WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()["n"]
        assert kb_count == 2, "debe ingerir los dos archivos KB"

        golden_count = conn.execute(
            "SELECT COUNT(*) AS n FROM golden_case WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()["n"]
        assert golden_count == len(SYNTHETIC_CASES)
    finally:
        conn.close()
