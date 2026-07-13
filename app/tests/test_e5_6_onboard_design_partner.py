"""E5-6 — onboarding de design partner."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.scripts.onboard_design_partner import main


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


def _app_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_DB_PATH"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _foundation_conn(client: TestClient) -> sqlite3.Connection:
    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def test_onboard_dry_run_does_not_mutate(client: TestClient, tmp_path: Path) -> None:
    out_dir = tmp_path / "audits"
    code = main(
        [
            "--partner-name",
            "Marluvas",
            "--partner-slug",
            "marluvas",
            "--owner-email",
            "admin@marluvas.com",
            "--owner-password",
            "Secret123",
            "--db-path",
            os.environ["FABERLOOM_DB_PATH"],
            "--out-dir",
            str(out_dir),
        ]
    )
    assert code == 0
    assert (out_dir / "ACUERDO_marluvas_v1.md").exists()
    assert len(list(out_dir.glob("EVIDENCIA_DESIGN_PARTNER_marluvas_*.md"))) == 1

    app = _app_conn(client)
    foundation = _foundation_conn(client)
    try:
        assert foundation.execute("SELECT COUNT(*) AS n FROM fnd_tenants WHERE slug = ?", ("marluvas",)).fetchone()["n"] == 0
        assert app.execute(
            "SELECT COUNT(*) AS n FROM workspace WHERE slug = ?", ("marluvas",)
        ).fetchone()["n"] == 0
    finally:
        app.close()
        foundation.close()


def test_onboard_execute_creates_tenant_workspace_and_user(client: TestClient, tmp_path: Path) -> None:
    out_dir = tmp_path / "audits"
    code = main(
        [
            "--partner-name",
            "Tecmater",
            "--partner-slug",
            "tecmater",
            "--owner-email",
            "admin@tecmater.com",
            "--owner-password",
            "Secret123",
            "--execute",
            "--approved-by",
            "usr_ceo",
            "--db-path",
            os.environ["FABERLOOM_DB_PATH"],
            "--out-dir",
            str(out_dir),
        ]
    )
    assert code == 0

    app = _app_conn(client)
    foundation = _foundation_conn(client)
    try:
        tenant = foundation.execute(
            "SELECT * FROM fnd_tenants WHERE slug = ?", ("tecmater",)
        ).fetchone()
        assert tenant is not None
        tenant_id = tenant["id"]

        user = foundation.execute(
            "SELECT * FROM fnd_users WHERE email = ?", ("admin@tecmater.com",)
        ).fetchone()
        assert user is not None
        assert user["tenant_id"] == tenant_id

        role = foundation.execute(
            """
            SELECT r.name FROM fnd_user_roles ur
            JOIN fnd_roles r ON r.id = ur.role_id
            WHERE ur.user_id = ?
            """,
            (user["id"],),
        ).fetchone()
        assert role["name"] == "owner"

        ws = app.execute(
            "SELECT * FROM workspace WHERE tenant_id = ?", (tenant_id,)
        ).fetchone()
        assert ws is not None
        assert ws["is_canary"] == 1
        assert ws["id"] == f"ws_{tenant_id}"

        audit = app.execute(
            "SELECT COUNT(*) AS n FROM audit_log WHERE action = 'design_partner.onboarded'"
        ).fetchone()["n"]
        assert audit == 1
    finally:
        app.close()
        foundation.close()


def test_onboard_rejects_duplicate_slug(client: TestClient, tmp_path: Path) -> None:
    out_dir = tmp_path / "audits"
    args = [
        "--partner-name",
        "Dup",
        "--partner-slug",
        "dup-slug",
        "--owner-email",
        "a@dup.com",
        "--owner-password",
        "Secret123",
        "--execute",
        "--approved-by",
        "usr_ceo",
        "--db-path",
        os.environ["FABERLOOM_DB_PATH"],
        "--out-dir",
        str(out_dir),
    ]
    assert main(args) == 0

    out_dir2 = tmp_path / "audits2"
    args2 = [
        "--partner-name",
        "Dup2",
        "--partner-slug",
        "dup-slug",
        "--owner-email",
        "b@dup.com",
        "--owner-password",
        "Secret123",
        "--execute",
        "--approved-by",
        "usr_ceo",
        "--db-path",
        os.environ["FABERLOOM_DB_PATH"],
        "--out-dir",
        str(out_dir2),
    ]
    assert main(args2) == 1


def test_onboard_rejects_invalid_email(client: TestClient, tmp_path: Path) -> None:
    out_dir = tmp_path / "audits"
    code = main(
        [
            "--partner-name",
            "Bad",
            "--partner-slug",
            "bad-email",
            "--owner-email",
            "not-an-email",
            "--owner-password",
            "Secret123",
            "--execute",
            "--approved-by",
            "usr_ceo",
            "--db-path",
            os.environ["FABERLOOM_DB_PATH"],
            "--out-dir",
            str(out_dir),
        ]
    )
    assert code == 1
