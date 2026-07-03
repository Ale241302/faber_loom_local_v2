"""Tenant context utilities backed by a ContextVar stack and PostgreSQL SET."""
from __future__ import annotations

from contextvars import ContextVar
from uuid import UUID

# Stack of tenant ids for the current execution context. The top of the stack
# is the active tenant id (or None when empty).
tenant_ctx: ContextVar[list[UUID]] = ContextVar("tenant_id", default=[])


def set_db_tenant(tenant_id: UUID) -> None:
    """Push tenant_id onto the stack and set it on the current DB connection."""
    from django.db import connection

    stack = tenant_ctx.get()[:]
    stack.append(tenant_id)
    tenant_ctx.set(stack)

    with connection.cursor() as cursor:
        cursor.execute("SET app.tenant_id = %s", [str(tenant_id)])


def clear_db_tenant() -> None:
    """Pop the active tenant id and restore the previous one (if any)."""
    from django.db import connection

    stack = tenant_ctx.get()[:]
    if stack:
        stack.pop()
    tenant_ctx.set(stack)

    with connection.cursor() as cursor:
        if stack:
            cursor.execute("SET app.tenant_id = %s", [str(stack[-1])])
        else:
            cursor.execute("RESET app.tenant_id")


def current_tenant_id() -> UUID | None:
    """Return the active tenant id from the current execution context."""
    stack = tenant_ctx.get()
    return stack[-1] if stack else None
