"""E5-6 — soak report read-only aggregations and isolation."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.scripts.soak_report import build_soak_report, main, render_markdown
from app.src.context import Context, SYSTEM_WORKSPACE_ID


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated app with fresh Foundation and app DBs."""

    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        '{"admin@platform.test":"admin-pass","owner@acme.test":"owner-pass","owner@other.test":"owner-pass"}',
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
    if role_row is None:
        raise RuntimeError(f"Role {role} missing for tenant {tenant_id}")
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


def _seed_data(conn: sqlite3.Connection, tenant_id: str) -> None:
    from app.src.db import utc_now

    now = utc_now()
    # Workspace
    conn.execute(
        """
        INSERT INTO workspace (id, name, slug, tenant_id, created_at, updated_at)
        VALUES (?, 'WS', ?, ?, ?, ?)
        """,
        (f"ws_{tenant_id}", f"ws-{tenant_id}", tenant_id, now, now),
    )
    # Runs in the last 7 days
    for i, status in enumerate(["succeeded", "succeeded", "failed", "requires_hitl"]):
        conn.execute(
            """
            INSERT INTO routine_run
            (id, routine_id, workspace_id, tenant_id, status, created_at, input_json, output_json, evidence_json)
            VALUES (?, ?, ?, ?, ?, ?, '{}', '{}', '[]')
            """,
            (
                f"run_{tenant_id}_{i}",
                "routine_1",
                f"ws_{tenant_id}",
                tenant_id,
                status,
                now,
            ),
        )
    # Drafts approved / rejected
    for i, status in enumerate(["approved", "approved", "rejected"]):
        conn.execute(
            """
            INSERT INTO draft
            (id, workspace_id, tenant_id, body_md, hard_facts_json, status, updated_at, created_at)
            VALUES (?, ?, ?, 'body', '[]', ?, ?, ?)
            """,
            (f"draft_{tenant_id}_{i}", f"ws_{tenant_id}", tenant_id, status, now, now),
        )
    # Usage
    conn.execute(
        """
        INSERT INTO usage_record
        (id, workspace_id, tenant_id, provider_slug, model, cost_usd, status, created_at)
        VALUES (?, ?, ?, 'openai', 'gpt-4', 0.123, 'succeeded', ?)
        """,
        (f"usage_{tenant_id}", f"ws_{tenant_id}", tenant_id, now),
    )
    # Audit incident
    conn.execute(
        """
        INSERT INTO audit_log
        (id, workspace_id, tenant_id, action, payload_json, created_at)
        VALUES (?, ?, ?, 'living_agent.routing.degraded', '{}', ?)
        """,
        (f"audit_{tenant_id}", f"ws_{tenant_id}", tenant_id, now),
    )
    conn.commit()


def _context(tenant_id: str, workspace_id: str = SYSTEM_WORKSPACE_ID) -> Context:
    return Context(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
        user_id="soak-test",
        actor_id="soak-test",
        actor_role_at_decision="platform_admin",
    )


def test_soak_report_aggregations_are_correct(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-soak")
    conn = _app_conn(client)
    try:
        _seed_data(conn, tenant_id)
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "app.scripts.soak_report._run_canary",
            lambda db_path, foundation_db: {
                "status": "clean",
                "exit_code": 0,
                "summary": "OK",
            },
        )
        try:
            report = build_soak_report(
                _context(tenant_id, workspace_id=f"ws_{tenant_id}"),
                conn,
                week=1,
                db_path=os.environ["FABERLOOM_DB_PATH"],
                foundation_db=os.environ["FABERLOOM_FOUNDATION_DB"],
            )
        finally:
            monkeypatch.undo()
    finally:
        conn.close()

    assert report["tenant_id"] == tenant_id
    assert report["week"] == 1
    assert report["week_metrics"]["runs_total"] == 4
    assert report["week_metrics"]["runs_successful"] == 2
    assert report["week_metrics"]["runs_failed"] == 1
    assert report["week_metrics"]["runs_requires_hitl"] == 1
    assert report["week_metrics"]["hitl_approved"] == 2
    assert report["week_metrics"]["hitl_rejected"] == 1
    assert report["week_metrics"]["cost_usd"] == pytest.approx(0.123)
    assert report["incidents"]["total"] == 1
    assert report["canary"]["status"] == "clean"


def test_soak_report_has_no_sensitive_content(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-soak-no-content")
    conn = _app_conn(client)
    try:
        _seed_data(conn, tenant_id)
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "app.scripts.soak_report._run_canary",
            lambda db_path, foundation_db: {
                "status": "clean",
                "exit_code": 0,
                "summary": "OK",
            },
        )
        try:
            report = build_soak_report(
                _context(tenant_id, workspace_id=f"ws_{tenant_id}"),
                conn,
                week=1,
                db_path=os.environ["FABERLOOM_DB_PATH"],
                foundation_db=os.environ["FABERLOOM_FOUNDATION_DB"],
            )
        finally:
            monkeypatch.undo()
    finally:
        conn.close()

    markdown = render_markdown(report)
    assert "body_md" not in markdown
    assert "raw_payload" not in markdown
    assert "input_json" not in markdown
    assert "output_json" not in markdown
    # Sensitive content from seeded data should not appear in the report.
    assert "body" not in markdown


def test_soak_report_isolation_across_tenants(client: TestClient) -> None:
    tenant_a = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-soak-a")
    tenant_b = _bootstrap_tenant(client, "owner@other.test", "owner", "other-soak-b")
    conn = _app_conn(client)
    try:
        _seed_data(conn, tenant_a)
        _seed_data(conn, tenant_b)
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "app.scripts.soak_report._run_canary",
            lambda db_path, foundation_db: {
                "status": "clean",
                "exit_code": 0,
                "summary": "OK",
            },
        )
        try:
            report_a = build_soak_report(
                _context(tenant_a, workspace_id=f"ws_{tenant_a}"),
                conn,
                week=1,
                db_path=os.environ["FABERLOOM_DB_PATH"],
                foundation_db=os.environ["FABERLOOM_FOUNDATION_DB"],
            )
        finally:
            monkeypatch.undo()
    finally:
        conn.close()

    # Tenant A should only see its own 4 runs, not tenant B's.
    assert report_a["week_metrics"]["runs_total"] == 4


def test_soak_report_fail_closed_without_tenant(client: TestClient) -> None:
    conn = _app_conn(client)
    try:
        ctx = Context(
            workspace_id=SYSTEM_WORKSPACE_ID,
            tenant_id=None,
            user_id="soak-test",
            actor_id="soak-test",
        )
        with pytest.raises(Exception):
            build_soak_report(
                ctx,
                conn,
                week=1,
                db_path=os.environ["FABERLOOM_DB_PATH"],
                foundation_db=os.environ["FABERLOOM_FOUNDATION_DB"],
            )
    finally:
        conn.close()


def test_soak_report_canary_red_returns_non_zero(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-soak-red")
    conn = _app_conn(client)
    try:
        _seed_data(conn, tenant_id)
    finally:
        conn.close()

    out_dir = tmp_path / "audits"
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        "app.scripts.soak_report._run_canary",
        lambda db_path, foundation_db: {
            "status": "contamination_detected",
            "exit_code": 1,
            "summary": "FUGA",
        },
    )
    try:
        code = main(
            [
                "--tenant-id",
                tenant_id,
                "--week",
                "1",
                "--db-path",
                os.environ["FABERLOOM_DB_PATH"],
                "--foundation-db",
                os.environ["FABERLOOM_FOUNDATION_DB"],
                "--out",
                str(out_dir),
            ]
        )
    finally:
        monkeypatch.undo()

    assert code == 1
    assert (out_dir / f"SOAK_{tenant_id}_S1.md").exists()
