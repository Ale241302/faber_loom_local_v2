"""E3-6 manual billing REST endpoints.

Tenant-scoped invoice and payment-reconciliation management. Only tenant
owners/admins or platform_admin may create, update or delete records. All
mutations are audited.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from .api import context_from_request
from .audit import audit_writer
from .auth import get_current_user
from .context import SYSTEM_WORKSPACE_ID, Context
from .db import (
    create_manual_invoice,
    create_reconciliation,
    delete_manual_invoice,
    get_db,
    get_manual_invoice,
    get_reconciliation,
    list_manual_invoices,
    list_reconciliations,
    match_reconciliation,
    transaction,
    update_manual_invoice,
)
from .models import (
    InvoiceCreate,
    InvoiceListRead,
    InvoiceRead,
    InvoiceStatusUpdate,
    ReconciliationCreate,
    ReconciliationListRead,
    ReconciliationMatch,
    ReconciliationRead,
)

billing_router = APIRouter(prefix="/tenants", tags=["billing"])


def _ensure_system_workspace(conn: Any) -> None:
    """Guarantee the synthetic system workspace row exists for system-scoped audit."""

    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO workspace (id, name, slug, tenant_id, created_at, updated_at)
        VALUES (?, 'System', ?, ?, ?, ?)
        ON CONFLICT (id) DO NOTHING
        """,
        (SYSTEM_WORKSPACE_ID, SYSTEM_WORKSPACE_ID, SYSTEM_WORKSPACE_ID, now, now),
    )


def _require_tenant_admin(tenant_id: str, user: dict[str, Any]) -> None:
    """Fail unless the user is owner/admin of the tenant or platform_admin."""

    user_tenant = user.get("tenant_id")
    role = (user.get("role") or "").lower()
    roles = {r.lower() for r in (user.get("roles") or [])}
    is_platform_admin = role == "platform_admin" or "platform_admin" in roles
    is_tenant_admin = user_tenant == tenant_id and (role in {"owner", "admin"} or {"owner", "admin"} & roles)
    if not (is_platform_admin or is_tenant_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner/admin role required for this tenant",
        )


def _tenant_context(request: Request, tenant_id: str) -> Context:
    user = getattr(request.state, "user", None) or {}
    return Context(
        workspace_id=SYSTEM_WORKSPACE_ID,
        tenant_id=tenant_id,
        user_id=user.get("user_id") or user.get("sub") or "local",
        actor_id=user.get("actor_id") or user.get("user_id") or user.get("sub") or "local",
        actor_role_at_decision=(user.get("role") or "owner"),
    )


@billing_router.get("/{tenant_id}/invoices", response_model=InvoiceListRead)
def list_invoices(
    tenant_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> InvoiceListRead:
    """List manual invoices for the tenant."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    rows = list_manual_invoices(ctx, conn)
    return InvoiceListRead(invoices=[InvoiceRead(**row) for row in rows])


@billing_router.post("/{tenant_id}/invoices", status_code=status.HTTP_201_CREATED, response_model=InvoiceRead)
def create_invoice(
    tenant_id: str,
    body: InvoiceCreate,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> InvoiceRead:
    """Create a manual invoice for the tenant."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    try:
        with transaction(conn, ctx=ctx):
            _ensure_system_workspace(conn)
            created = create_manual_invoice(
                ctx,
                conn,
                invoice_id=body.invoice_id,
                customer_name=body.customer_name,
                customer_tax_id=body.customer_tax_id,
                customer_email=body.customer_email,
                issue_date=body.issue_date,
                due_date=body.due_date,
                line_items=[item.model_dump() for item in body.line_items],
                currency=body.currency,
                notes=body.notes,
            )
            audit_writer.write(
                ctx,
                conn,
                action="manual_invoice.created",
                payload={"invoice_id": created["invoice_id"], "total": created["total"]},
                system_event=True,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return InvoiceRead(**created)


@billing_router.get("/{tenant_id}/invoices/{invoice_id}", response_model=InvoiceRead)
def get_invoice(
    tenant_id: str,
    invoice_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> InvoiceRead:
    """Return a single manual invoice."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    row = get_manual_invoice(ctx, conn, invoice_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return InvoiceRead(**row)


@billing_router.patch("/{tenant_id}/invoices/{invoice_id}", response_model=InvoiceRead)
def patch_invoice(
    tenant_id: str,
    invoice_id: str,
    body: InvoiceStatusUpdate,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> InvoiceRead:
    """Update a manual invoice (status, payment info, notes)."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    with transaction(conn, ctx=ctx):
        _ensure_system_workspace(conn)
        updated = update_manual_invoice(
            ctx,
            conn,
            invoice_id,
            status=body.status,
            paid_at=body.paid_at,
            paid_amount=body.paid_amount,
            payment_reference=body.payment_reference,
            notes=body.notes,
        )
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        audit_writer.write(
            ctx,
            conn,
            action="manual_invoice.updated",
            payload={"invoice_id": invoice_id, "status": updated["status"]},
            system_event=True,
        )
    return InvoiceRead(**updated)


@billing_router.delete("/{tenant_id}/invoices/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    tenant_id: str,
    invoice_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> None:
    """Delete a manual invoice."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    with transaction(conn, ctx=ctx):
        _ensure_system_workspace(conn)
        if not delete_manual_invoice(ctx, conn, invoice_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
        audit_writer.write(
            ctx,
            conn,
            action="manual_invoice.deleted",
            payload={"invoice_id": invoice_id},
            system_event=True,
        )


@billing_router.get("/{tenant_id}/reconciliations", response_model=ReconciliationListRead)
def list_reconciliation_items(
    tenant_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> ReconciliationListRead:
    """List payment reconciliations for the tenant."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    rows = list_reconciliations(ctx, conn)
    return ReconciliationListRead(reconciliations=[ReconciliationRead(**row) for row in rows])


@billing_router.post("/{tenant_id}/reconciliations", status_code=status.HTTP_201_CREATED, response_model=ReconciliationRead)
def create_reconciliation_item(
    tenant_id: str,
    body: ReconciliationCreate,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> ReconciliationRead:
    """Create a payment reconciliation entry for the tenant."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    try:
        with transaction(conn, ctx=ctx):
            _ensure_system_workspace(conn)
            created = create_reconciliation(
                ctx,
                conn,
                reconciliation_id=body.reconciliation_id,
                bank_reference=body.bank_reference,
                received_at=body.received_at,
                amount=body.amount,
                currency=body.currency,
                payer_name=body.payer_name,
                payer_account=body.payer_account,
                notes=body.notes,
            )
            audit_writer.write(
                ctx,
                conn,
                action="payment_reconciliation.created",
                payload={"reconciliation_id": created["reconciliation_id"], "amount": created["amount"]},
                system_event=True,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return ReconciliationRead(**created)


@billing_router.patch("/{tenant_id}/reconciliations/{reconciliation_id}/match", response_model=ReconciliationRead)
def patch_reconciliation_match(
    tenant_id: str,
    reconciliation_id: str,
    body: ReconciliationMatch,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> ReconciliationRead:
    """Match a reconciliation to an invoice."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    try:
        with transaction(conn, ctx=ctx):
            _ensure_system_workspace(conn)
            updated = match_reconciliation(
                ctx,
                conn,
                reconciliation_id,
                matched_invoice_id=body.invoice_id,
                notes=body.notes,
            )
            if updated is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reconciliation not found")
            audit_writer.write(
                ctx,
                conn,
                action="payment_reconciliation.matched",
                payload={
                    "reconciliation_id": reconciliation_id,
                    "invoice_id": body.invoice_id,
                    "status": updated["status"],
                },
                system_event=True,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    return ReconciliationRead(**updated)
