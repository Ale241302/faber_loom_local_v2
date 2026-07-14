"""E3-6 manual billing REST endpoints.

Tenant-scoped invoice and payment-reconciliation management. Only tenant
owners/admins or platform_admin may create, update or delete records. All
mutations are audited.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response

from .api import context_from_request
from .audit import audit_writer
from .auth import get_current_user
from .connectors.tax_authority import get_tax_connector_secret
from .context import SYSTEM_WORKSPACE_ID, Context
from .db import (
    create_manual_invoice,
    create_reconciliation,
    delete_manual_invoice,
    ensure_system_workspace,
    get_db,
    get_manual_invoice,
    get_reconciliation,
    list_manual_invoices,
    list_reconciliations,
    mark_invoice_pdf_generated,
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
            ensure_system_workspace(conn, ctx.tenant_id)
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
                document_series=body.document_series,
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
        ensure_system_workspace(conn, ctx.tenant_id)
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
        ensure_system_workspace(conn, ctx.tenant_id)
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
            ensure_system_workspace(conn, ctx.tenant_id)
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
            ensure_system_workspace(conn, ctx.tenant_id)
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


# ---------------------------------------------------------------------------
# E3-6: manual invoice PDF generation (non-fiscal / beta)
# ---------------------------------------------------------------------------

from pathlib import Path

from fpdf import FPDF


def _tenant_has_tax_certificate(ctx: Context) -> bool:
    """Return True when the tenant has an ATV certificate configured (HE2-9 gate)."""

    return bool(get_tax_connector_secret(ctx, "atv", "certificate"))


def _render_invoice_pdf(invoice: dict[str, Any], *, has_tax_certificate: bool) -> bytes:
    """Render a manual invoice as a PDF.

    When ``has_tax_certificate`` is False the PDF carries the original non-fiscal
    beta disclaimer (no regression).  When True the disclaimer is removed and the
    fiscal authority data is printed instead.
    """

    pdf = FPDF(unit="pt", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=36)

    # Use the built-in Helvetica font. All text is limited to Latin-1 characters
    # so no external Unicode font files are required in the server image.
    def set_font(style: str = "", size: int = 10) -> None:
        pdf.set_font("Helvetica", style=style, size=size)

    set_font("B", 16)
    pdf.cell(0, 22, "FaberLoom", ln=True)
    set_font("", 9)
    if has_tax_certificate:
        pdf.cell(0, 12, "DOCUMENTO FISCAL ELECTRONICO", ln=True)
        set_font("", 8)
        authority = invoice.get("tax_authority") or "ATV (Costa Rica)"
        pdf.cell(0, 10, f"Autoridad tributaria: {authority}", ln=True)
        if invoice.get("tax_document_key"):
            pdf.cell(0, 10, f"Clave numerica: {invoice['tax_document_key']}", ln=True)
        if invoice.get("tax_authority_status"):
            pdf.cell(0, 10, f"Estado ante autoridad: {invoice['tax_authority_status']}", ln=True)
    else:
        pdf.cell(0, 12, "DOCUMENTO NO FISCAL - BETA", ln=True)
        set_font("", 8)
        pdf.cell(0, 10, "Este documento no tiene validez tributaria. Uso interno de Facturacion Beta.", ln=True)
    pdf.ln(8)

    set_font("B", 12)
    pdf.cell(0, 16, "Factura", ln=True)
    set_font("", 10)
    series = invoice.get("document_series") or "BETA"
    number = invoice.get("document_number")
    number_text = f"Serie {series} - Numero {number}" if number is not None else f"Serie {series}"
    pdf.cell(0, 14, number_text, ln=True)
    pdf.cell(0, 14, f"ID interno: {invoice['invoice_id']}", ln=True)
    pdf.ln(8)

    set_font("B", 10)
    pdf.cell(0, 14, "Cliente", ln=True)
    set_font("", 10)
    pdf.cell(0, 12, invoice["customer_name"], ln=True)
    if invoice.get("customer_tax_id"):
        pdf.cell(0, 12, f"Identificación tributaria: {invoice['customer_tax_id']}", ln=True)
    if invoice.get("customer_email"):
        pdf.cell(0, 12, f"Correo: {invoice['customer_email']}", ln=True)
    pdf.ln(8)

    set_font("", 10)
    pdf.cell(90, 12, f"Fecha de emisión: {invoice['issue_date']}", ln=False)
    if invoice.get("due_date"):
        pdf.cell(0, 12, f"Vencimiento: {invoice['due_date']}", ln=True)
    else:
        pdf.ln(12)
    pdf.ln(8)

    # Line items table.
    set_font("B", 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(250, 18, "Descripción", border=1, fill=True)
    pdf.cell(60, 18, "Cant.", border=1, align="C", fill=True)
    pdf.cell(90, 18, "Precio unit.", border=1, align="R", fill=True)
    pdf.cell(70, 18, "Impuesto", border=1, align="R", fill=True)
    pdf.cell(80, 18, "Total", border=1, align="R", fill=True)
    pdf.ln(18)

    set_font("", 9)
    for item in invoice.get("line_items") or []:
        description = item.get("description") or ""
        quantity = float(item.get("quantity", 1) or 1)
        unit_price = float(item.get("unit_price", 0) or 0)
        tax_pct = float(item.get("tax_pct", 0) or 0)
        line_total = quantity * unit_price * (1 + tax_pct / 100.0)
        pdf.cell(250, 16, str(description), border=1)
        pdf.cell(60, 16, str(int(quantity)), border=1, align="C")
        pdf.cell(90, 16, f"{unit_price:.2f}", border=1, align="R")
        pdf.cell(70, 16, f"{tax_pct:.2f}%", border=1, align="R")
        pdf.cell(80, 16, f"{line_total:.2f}", border=1, align="R")
        pdf.ln(16)

    pdf.ln(8)
    totals_x = 360
    set_font("", 10)
    pdf.set_x(totals_x)
    pdf.cell(120, 14, "Subtotal:", align="R")
    pdf.cell(80, 14, f"{invoice['subtotal']:.2f} {invoice['currency']}", align="R")
    pdf.ln(14)
    pdf.set_x(totals_x)
    pdf.cell(120, 14, "Impuesto:", align="R")
    pdf.cell(80, 14, f"{invoice['tax_total']:.2f} {invoice['currency']}", align="R")
    pdf.ln(14)
    set_font("B", 11)
    pdf.set_x(totals_x)
    pdf.cell(120, 16, "Total:", align="R")
    pdf.cell(80, 16, f"{invoice['total']:.2f} {invoice['currency']}", align="R")
    pdf.ln(16)

    if invoice.get("notes"):
        pdf.ln(10)
        set_font("B", 9)
        pdf.cell(0, 12, "Notas", ln=True)
        set_font("", 9)
        pdf.multi_cell(0, 12, str(invoice["notes"]))

    pdf.ln(16)
    set_font("", 8)
    pdf.set_text_color(100, 100, 100)
    if has_tax_certificate:
        pdf.multi_cell(
            0,
            10,
            "Documento fiscal electronico generado por FaberLoom. "
            "La validez tributaria esta sujeta a aceptacion por la autoridad correspondiente.",
        )
    else:
        pdf.multi_cell(0, 10, "DOCUMENTO NO FISCAL - BETA. No emitido ante autoridad tributaria. "
                               "Generado por FaberLoom para trazabilidad interna de facturacion manual.")

    return bytes(pdf.output())


@billing_router.get("/{tenant_id}/invoices/{invoice_id}/pdf")
def download_invoice_pdf(
    tenant_id: str,
    invoice_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> Response:
    """Download a manual invoice as a non-fiscal PDF."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    invoice = get_manual_invoice(ctx, conn, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")

    pdf_bytes = _render_invoice_pdf(invoice, has_tax_certificate=_tenant_has_tax_certificate(ctx))

    with transaction(conn, ctx=ctx):
        ensure_system_workspace(conn, ctx.tenant_id)
        if invoice.get("pdf_generated_at") is None:
            mark_invoice_pdf_generated(ctx, conn, invoice_id)
        audit_writer.write(
            ctx,
            conn,
            action="manual_invoice.pdf_generated",
            payload={"invoice_id": invoice_id, "document_number": invoice.get("document_number")},
            system_event=True,
        )

    filename = f"{invoice['invoice_id']}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )
