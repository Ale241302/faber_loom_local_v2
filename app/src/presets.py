"""E3-5 routing presets REST endpoints.

Tenant-scoped preset management. Only tenant owners/admins or platform_admin
may create, update or delete presets. All mutations are audited.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from .api import context_from_request
from .audit import audit_writer
from .auth import get_current_user
from .context import SYSTEM_WORKSPACE_ID, Context
from .db import (
    create_routing_preset,
    delete_routing_preset,
    ensure_system_workspace,
    get_db,
    get_routing_preset,
    list_routing_presets,
    resolve_routing_preset,
    summarize_tenant_usage_cost,
    transaction,
    update_routing_preset,
)
from .models import (
    RoutingPresetCreate,
    RoutingPresetRead,
    RoutingPresetResolveRead,
    RoutingPresetUpdate,
    UsageSummaryRead,
)

presets_router = APIRouter(prefix="/tenants", tags=["routing-presets"])


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


@presets_router.get("/{tenant_id}/presets")
def list_presets(
    tenant_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, list[RoutingPresetRead]]:
    """List routing presets for the tenant (read access for any tenant member)."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    with transaction(conn, ctx=ctx):
        rows = list_routing_presets(ctx, conn)
    return {"presets": [RoutingPresetRead(**row) for row in rows]}


@presets_router.post("/{tenant_id}/presets", status_code=status.HTTP_201_CREATED)
def create_preset(
    tenant_id: str,
    body: RoutingPresetCreate,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> RoutingPresetRead:
    """Create a new routing preset for the tenant."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    try:
        with transaction(conn, ctx=ctx):
            ensure_system_workspace(conn, ctx.tenant_id)
            created = create_routing_preset(
                ctx,
                conn,
                preset_id=body.preset_id,
                name=body.name,
                description=body.description,
                envelope=body.envelope.model_dump(),
                curve=body.curve.model_dump(),
                task_overrides=body.task_overrides,
                caps=body.caps.model_dump(),
                escalation=body.escalation.model_dump(),
                is_active=body.is_active,
                is_template=body.is_template,
            )
            audit_writer.write(
                ctx,
                conn,
                action="routing_preset.created",
                payload={"preset_id": created["preset_id"], "name": created["name"]},
                system_event=True,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return RoutingPresetRead(**created)


@presets_router.get("/{tenant_id}/presets/{preset_id}")
def get_preset(
    tenant_id: str,
    preset_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> RoutingPresetRead:
    """Return a single routing preset."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    with transaction(conn, ctx=ctx):
        row = get_routing_preset(ctx, conn, preset_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    return RoutingPresetRead(**row)


@presets_router.patch("/{tenant_id}/presets/{preset_id}")
def patch_preset(
    tenant_id: str,
    preset_id: str,
    body: RoutingPresetUpdate,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> RoutingPresetRead:
    """Update a routing preset."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    with transaction(conn, ctx=ctx):
        ensure_system_workspace(conn, ctx.tenant_id)
        updated = update_routing_preset(
            ctx,
            conn,
            preset_id,
            name=body.name,
            description=body.description,
            envelope=body.envelope.model_dump() if body.envelope else None,
            curve=body.curve.model_dump() if body.curve else None,
            task_overrides=body.task_overrides,
            caps=body.caps.model_dump() if body.caps else None,
            escalation=body.escalation.model_dump() if body.escalation else None,
            is_active=body.is_active,
            is_template=body.is_template,
        )
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
        audit_writer.write(
            ctx,
            conn,
            action="routing_preset.updated",
            payload={"preset_id": preset_id, "version": updated["version"]},
            system_event=True,
        )
    return RoutingPresetRead(**updated)


@presets_router.delete("/{tenant_id}/presets/{preset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_preset(
    tenant_id: str,
    preset_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> None:
    """Delete a routing preset.

    Falla con 409 si algun arquetipo lo referencia, nombrando cuales, en vez de
    huerfanizarlos en silencio (SPEC_FB_ARCHETYPE_FACTORY_v1).
    """

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    try:
        with transaction(conn, ctx=ctx):
            ensure_system_workspace(conn, ctx.tenant_id)
            if not delete_routing_preset(ctx, conn, preset_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found"
                )
            audit_writer.write(
                ctx,
                conn,
                action="routing_preset.deleted",
                payload={"preset_id": preset_id},
                system_event=True,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@presets_router.get("/{tenant_id}/usage/summary")
def tenant_usage_summary(
    tenant_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> UsageSummaryRead:
    """Return tenant usage totals and, for tenant admins, a detailed breakdown."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    role = (user.get("role") or "").lower()
    roles = {r.lower() for r in (user.get("roles") or [])}
    is_platform_admin = role == "platform_admin" or "platform_admin" in roles

    summary = summarize_tenant_usage_cost(conn, ctx.tenant_id)
    breakdown = summary["breakdown"]
    if is_platform_admin:
        breakdown = []

    return UsageSummaryRead(
        tenant_id=ctx.tenant_id,
        total_cost_usd=summary["total_cost_usd"],
        total_surcharge_usd=summary["total_surcharge_usd"],
        total_rows=summary["total_rows"],
        breakdown=[
            {
                "provider_slug": row["provider_slug"],
                "model": row["model"],
                "month": row["month"],
                "total_cost_usd": row["total_cost_usd"],
                "total_surcharge_usd": row["total_surcharge_usd"],
                "total_input_tokens": row["total_input_tokens"],
                "total_output_tokens": row["total_output_tokens"],
                "row_count": row["row_count"],
            }
            for row in breakdown
        ],
    )


@presets_router.get("/{tenant_id}/presets/{preset_id}/resolve")
def resolve_preset(
    tenant_id: str,
    preset_id: str,
    request: Request,
    task_class: str | None = None,
    complexity: str = "medium",
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> RoutingPresetResolveRead:
    """Resolve a preset reference to provider/model/params (read-only)."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    with transaction(conn, ctx=ctx):
        resolved = resolve_routing_preset(ctx, conn, preset_id, task_class=task_class, complexity=complexity)
    if resolved is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preset not found")
    return RoutingPresetResolveRead(**resolved)
