"""E5-1 — evidencia operacional de routing auto-generada."""

from __future__ import annotations

import os
import sqlite3
import uuid
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.scripts.routing_evidence_report import build_routing_report, main, render_markdown
from app.src.context import Context


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


def _seed_routing_data(conn: sqlite3.Connection, tenant_id: str, workspace_id: str) -> None:
    from app.src.db import new_id, utc_now

    now = utc_now()

    # Planner decisions: 2 shadow (one absurd), 1 natural.
    decisions = [
        ("shadow", '{"est_total_cost_usd": 0.5}', '{"cost_usd": 0.4}'),
        ("shadow", '{"est_total_cost_usd": 0.6}', '{"cost_usd": 0.2}'),
        ("natural", '{"est_total_cost_usd": 0.1}', '{"cost_usd": 0.1}'),
    ]
    for mode, plan, outcome in decisions:
        conn.execute(
            """
            INSERT INTO planner_decision_log (
                id, tenant_id, workspace_id, mode, plan_json, actual_outcome_json,
                schema_version, source_version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, 43, 'v1', ?, ?)
            """,
            (new_id("pdl"), tenant_id, workspace_id, mode, plan, outcome, now, now),
        )

    # Usage records.
    usage = [
        ("openai", "gpt-4o", "succeeded", 0.05),
        ("openai", "gpt-4o", "succeeded", 0.04),
        ("anthropic", "claude-3-5-sonnet", "failed", 0.01),
        ("openai", "gpt-4o", "budget_exceeded", 0.0),
    ]
    for provider, model, status, cost in usage:
        conn.execute(
            """
            INSERT INTO usage_record (
                id, workspace_id, tenant_id, provider_slug, model,
                input_tokens, output_tokens, cost_usd, status, created_at
            ) VALUES (?, ?, ?, ?, ?, 100, 50, ?, ?, ?)
            """,
            (new_id("usg"), workspace_id, tenant_id, provider, model, cost, status, now),
        )

    conn.commit()


def test_routing_report_read_only_tenant_scoped(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-routing")
    conn = _app_conn(client)
    try:
        workspace_id = _seed_workspace(conn, tenant_id)
        _seed_routing_data(conn, tenant_id, workspace_id)
    finally:
        conn.close()

    ctx = Context(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
        user_id="tester",
        actor_id="tester",
        actor_role_at_decision="system",
    )
    conn = _app_conn(client)
    try:
        report = build_routing_report(ctx, conn, days=7)
    finally:
        conn.close()

    assert report["tenant_id"] == tenant_id
    assert report["workspace_id"] == workspace_id
    assert report["planner"]["total_decisions"] == 3
    assert report["planner"]["shadow_decisions"] == 2
    assert report["planner"]["natural_decisions"] == 1
    assert report["planner"]["absurd_decisions"] == 1
    assert report["planner"]["projected_savings_usd"] == pytest.approx(-0.5, abs=1e-6)
    assert report["usage"]["total_calls"] == 4
    assert report["usage"]["succeeded"] == 2
    assert report["usage"]["failed"] == 1
    assert report["usage"]["budget_exceeded"] == 1
    assert report["usage"]["cost_usd"] == pytest.approx(0.10, abs=1e-6)
    assert report["policy"]["mode"] is None
    assert report["policy"]["degraded_count"] == 0


def test_routing_report_render_markdown(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-routing-md")
    conn = _app_conn(client)
    try:
        workspace_id = _seed_workspace(conn, tenant_id)
        _seed_routing_data(conn, tenant_id, workspace_id)
    finally:
        conn.close()

    ctx = Context(
        workspace_id=workspace_id,
        tenant_id=tenant_id,
        user_id="tester",
        actor_id="tester",
        actor_role_at_decision="system",
    )
    conn = _app_conn(client)
    try:
        report = build_routing_report(ctx, conn, days=7)
    finally:
        conn.close()

    markdown = render_markdown(report)
    assert "Evidencia operacional de routing" in markdown
    assert "openai/gpt-4o" in markdown
    assert "decisiones absurdas" in markdown
    assert "promoción" in markdown.lower()


def test_routing_report_cli_generates_file(client: TestClient, tmp_path: Path) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-routing-cli")
    conn = _app_conn(client)
    try:
        workspace_id = _seed_workspace(conn, tenant_id)
        _seed_routing_data(conn, tenant_id, workspace_id)
    finally:
        conn.close()

    out = tmp_path / "EVIDENCIA_ROUTING.md"
    code = main(
        [
            "--tenant-id",
            tenant_id,
            "--workspace-id",
            workspace_id,
            "--days",
            "7",
            "--db-path",
            os.environ["FABERLOOM_DB_PATH"],
            "--out",
            str(out),
        ]
    )
    assert code == 0
    assert out.exists()
    assert "openai/gpt-4o" in out.read_text(encoding="utf-8")


def test_routing_report_fail_closed_without_tenant(client: TestClient) -> None:
    conn = _app_conn(client)
    try:
        ctx = Context(
            workspace_id="ws_any",
            tenant_id=None,
            user_id="tester",
            actor_id="tester",
            actor_role_at_decision="system",
        )
        with pytest.raises(Exception):
            build_routing_report(ctx, conn, days=7)
    finally:
        conn.close()
