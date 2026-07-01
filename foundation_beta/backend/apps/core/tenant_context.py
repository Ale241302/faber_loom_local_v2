"""Tenant context utilities backed by a ContextVar and PostgreSQL SET LOCAL."""
from __future__ import annotations

from contextvars import ContextVar
from uuid import UUID

tenant_ctx: ContextVar[UUID | None] = ContextVar("tenant_id", default=None)


def set_db_tenant(tenant_id: UUID) -> None:
    """Set the tenant id for the current DB connection using SET LOCAL."""
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL app.tenant_id = %s", [str(tenant_id)])
    tenant_ctx.set(tenant_id)


def clear_db_tenant() -> None:
    """Clear tenant state for the current DB connection."""
    from django.db import connection

    with connection.cursor() as cursor:
        cursor.execute("DISCARD ALL")
    tenant_ctx.set(None)


def current_tenant_id() -> UUID | None:
    """Return the tenant id from the current execution context."""
    return tenant_ctx.get()
