"""E3-6 — Manual billing: invoices, payment reconciliation, isolation, state changes."""

from __future__ import annotations

import hashlib
import os
import sqlite3
from pathlib import Path
from typing import Any

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


def _login(client: TestClient, email: str, password: str) -> None:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text


def _create_invoice(client: TestClient, tenant_id: str, invoice_id: str, total: float = 100.0) -> dict[str, Any]:
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
                {"description": "Servicio", "quantity": 1, "unit_price": total, "tax_pct": 0}
            ],
            "currency": "USD",
            "notes": "Nota de prueba",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_reconciliation(client: TestClient, tenant_id: str, reconciliation_id: str, amount: float) -> dict[str, Any]:
    resp = client.post(
        f"/api/tenants/{tenant_id}/reconciliations",
        json={
            "reconciliation_id": reconciliation_id,
            "bank_reference": "REF-001",
            "received_at": "2026-07-05",
            "amount": amount,
            "currency": "USD",
            "payer_name": "Cliente S.A.",
            "payer_account": "****0001",
            "notes": "Transferencia",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_and_list_invoice(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-billing")
    _login(client, "owner@acme.test", "owner-pass")

    invoice = _create_invoice(client, tenant_id, "FAC-001", 150.0)
    assert invoice["tenant_id"] == tenant_id
    assert invoice["invoice_id"] == "FAC-001"
    assert invoice["customer_name"] == "Cliente S.A."
    assert invoice["subtotal"] == 150.0
    assert invoice["tax_total"] == 0.0
    assert invoice["total"] == 150.0
    assert invoice["status"] == "draft"

    resp = client.get(f"/api/tenants/{tenant_id}/invoices")
    assert resp.status_code == 200, resp.text
    invoices = resp.json()["invoices"]
    assert any(i["invoice_id"] == "FAC-001" for i in invoices)


def test_get_invoice(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-billing-get")
    _login(client, "owner@acme.test", "owner-pass")

    _create_invoice(client, tenant_id, "FAC-002")
    resp = client.get(f"/api/tenants/{tenant_id}/invoices/FAC-002")
    assert resp.status_code == 200, resp.text
    assert resp.json()["invoice_id"] == "FAC-002"

    resp = client.get(f"/api/tenants/{tenant_id}/invoices/NONEXISTENT")
    assert resp.status_code == 404, resp.text


def test_update_invoice_status(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-billing-status")
    _login(client, "owner@acme.test", "owner-pass")

    _create_invoice(client, tenant_id, "FAC-003")
    resp = client.patch(
        f"/api/tenants/{tenant_id}/invoices/FAC-003",
        json={"status": "sent"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "sent"

    resp = client.patch(
        f"/api/tenants/{tenant_id}/invoices/FAC-003",
        json={
            "status": "paid",
            "paid_at": "2026-07-10T12:00:00Z",
            "paid_amount": 100.0,
            "payment_reference": "wire-123",
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "paid"
    assert data["paid_amount"] == 100.0
    assert data["payment_reference"] == "wire-123"


def test_delete_invoice(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-billing-delete")
    _login(client, "owner@acme.test", "owner-pass")

    _create_invoice(client, tenant_id, "FAC-004")
    resp = client.delete(f"/api/tenants/{tenant_id}/invoices/FAC-004")
    assert resp.status_code == 204, resp.text

    resp = client.get(f"/api/tenants/{tenant_id}/invoices/FAC-004")
    assert resp.status_code == 404, resp.text


def test_cross_tenant_invoice_isolation(client: TestClient) -> None:
    tenant_a = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-a")
    tenant_b = _bootstrap_tenant(client, "owner@other.test", "owner", "other-b")

    _login(client, "owner@acme.test", "owner-pass")
    _create_invoice(client, tenant_a, "PRIV-001")

    _login(client, "owner@other.test", "owner-pass")
    resp = client.get(f"/api/tenants/{tenant_b}/invoices")
    assert resp.status_code == 200, resp.text
    invoices = resp.json()["invoices"]
    assert not any(i["invoice_id"] == "PRIV-001" for i in invoices)

    resp = client.get(f"/api/tenants/{tenant_b}/invoices/PRIV-001")
    assert resp.status_code == 404, resp.text


def test_create_and_match_reconciliation(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-recon")
    _login(client, "owner@acme.test", "owner-pass")

    _create_invoice(client, tenant_id, "FAC-005", 200.0)
    recon = _create_reconciliation(client, tenant_id, "REC-001", 200.0)
    assert recon["status"] == "pending"
    assert recon["matched_invoice_id"] is None

    resp = client.patch(
        f"/api/tenants/{tenant_id}/reconciliations/REC-001/match",
        json={"invoice_id": "FAC-005"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "matched"
    assert data["matched_invoice_id"] == "FAC-005"

    # When amounts match exactly, the invoice should be marked paid automatically.
    resp = client.get(f"/api/tenants/{tenant_id}/invoices/FAC-005")
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "paid"


def test_reconciliation_amount_mismatch_does_not_mark_paid(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-recon-mismatch")
    _login(client, "owner@acme.test", "owner-pass")

    _create_invoice(client, tenant_id, "FAC-006", 200.0)
    _create_reconciliation(client, tenant_id, "REC-002", 199.0)

    resp = client.patch(
        f"/api/tenants/{tenant_id}/reconciliations/REC-002/match",
        json={"invoice_id": "FAC-006"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "matched"

    resp = client.get(f"/api/tenants/{tenant_id}/invoices/FAC-006")
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] != "paid"


def test_duplicate_invoice_id_rejected(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "owner", "acme-dup")
    _login(client, "owner@acme.test", "owner-pass")

    _create_invoice(client, tenant_id, "FAC-007")
    resp = client.post(
        f"/api/tenants/{tenant_id}/invoices",
        json={
            "invoice_id": "FAC-007",
            "customer_name": "Otro",
            "issue_date": "2026-07-01",
            "line_items": [{"description": "x", "quantity": 1, "unit_price": 1, "tax_pct": 0}],
        },
    )
    assert resp.status_code == 409, resp.text


def test_non_admin_cannot_create_invoice(client: TestClient) -> None:
    tenant_id = _bootstrap_tenant(client, "owner@acme.test", "viewer", "acme-viewer")
    _login(client, "owner@acme.test", "owner-pass")

    resp = client.post(
        f"/api/tenants/{tenant_id}/invoices",
        json={
            "invoice_id": "FAC-008",
            "customer_name": "Cliente",
            "issue_date": "2026-07-01",
            "line_items": [{"description": "x", "quantity": 1, "unit_price": 1, "tax_pct": 0}],
        },
    )
    assert resp.status_code == 403, resp.text
