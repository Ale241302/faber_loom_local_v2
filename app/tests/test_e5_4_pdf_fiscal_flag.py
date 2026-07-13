"""E5-4: manual invoice PDF fiscal flag."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pdfplumber
import pytest
from fastapi.testclient import TestClient


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


def _foundation_conn(client: TestClient) -> Any:
    import os
    import sqlite3

    path = os.environ["FABERLOOM_FOUNDATION_DB"]
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _create_foundation_user(
    conn: Any,
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


def _login(client: TestClient, email: str, password: str) -> None:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text


def _create_invoice(client: TestClient, tenant_id: str, invoice_id: str) -> dict[str, Any]:
    resp = client.post(
        f"/api/tenants/{tenant_id}/invoices",
        json={
            "invoice_id": invoice_id,
            "customer_name": "Cliente S.A.",
            "customer_tax_id": "123456",
            "customer_email": "cliente@example.com",
            "issue_date": "2026-07-01",
            "due_date": "2026-07-31",
            "line_items": [
                {"description": "Servicio", "quantity": 1, "unit_price": 100.0, "tax_pct": 0}
            ],
            "currency": "USD",
            "notes": "Nota de prueba",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _set_connector_secret(tenant_id: str, authority: str, suffix: str, plaintext: str) -> None:
    from app.src.connectors.tax_authority import set_tax_connector_secret
    from app.src.context import Context

    ctx = Context(
        workspace_id="system",
        tenant_id=tenant_id,
        user_id="local",
        actor_id="local",
    )
    set_tax_connector_secret(ctx, authority, suffix, plaintext)


def test_pdf_without_certificate_contains_non_fiscal_disclaimer(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-pdf-no-cert")
    _login(client, "owner@acme.test", "owner-pass")

    _create_invoice(client, tenant_id, "FAC-NOFISCAL-001")
    resp = client.get(f"/api/tenants/{tenant_id}/invoices/FAC-NOFISCAL-001/pdf")
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/pdf"

    with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    assert "DOCUMENTO NO FISCAL" in text
    assert "DOCUMENTO FISCAL ELECTRONICO" not in text


def test_pdf_with_certificate_shows_fiscal_header(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-pdf-cert")
    _login(client, "owner@acme.test", "owner-pass")

    _set_connector_secret(tenant_id, "atv", "certificate", "-----BEGIN CERTIFICATE-----\nTEST\n-----END CERTIFICATE-----")

    _create_invoice(client, tenant_id, "FAC-FISCAL-001")
    resp = client.get(f"/api/tenants/{tenant_id}/invoices/FAC-FISCAL-001/pdf")
    assert resp.status_code == 200, resp.text

    with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    assert "DOCUMENTO NO FISCAL" not in text
    assert "DOCUMENTO FISCAL ELECTRONICO" in text
    assert "ATV (Costa Rica)" in text
