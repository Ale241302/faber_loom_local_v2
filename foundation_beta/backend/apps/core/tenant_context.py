"""Tenant context utilities backed by a ContextVar and PostgreSQL SET LOCAL."""
from __future__ import annotations

from contextvars import ContextVar
from uuid import UUID

tenant_ctx: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)


def set_db_tenant(tenant_id: UUID) -> None:
    """Set the tenant id for the current DB connection.

    Use SET LOCAL when already inside a transaction so the value is rolled back
    with the transaction. Otherwise use a session-level SET so it survives
    subsequent autocommit transactions (e.g. Django views/service code that
    opens its own transaction.atomic blocks).
    """
    from django.db import connection

    sql = (
        "SET LOCAL app.tenant_id = %s"
        if connection.in_atomic_block
        else "SET app.tenant_id = %s"
    )
    with connection.cursor() as cursor:
        cursor.execute(sql, [str(tenant_id)])
    tenant_ctx.set(tenant_id)


def clear_db_tenant() -> None:
    """Clear tenant state for the current DB connection."""
    from django.db import connection

    with connection.cursor() as cursor:
        # RESET works inside or outside a transaction, unlike DISCARD ALL.
        cursor.execute("RESET app.tenant_id")
    tenant_ctx.set(None)


def current_tenant_id() -> UUID | None:
    """Return the tenant id from the current execution context."""
    return tenant_ctx.get()
