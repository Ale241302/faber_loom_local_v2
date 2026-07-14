"""E5-1 archetype REST endpoints (SPEC_FB_ARCHETYPE_FACTORY_v1).

Un arquetipo es la plantilla reutilizable de "como se hace un tipo de trabajo".
Es tenant-scoped y lo puebla el usuario: pueden ser N. Distinto del enum cerrado
de `architectural_archetype` en skills.py, que nombra otra cosa.

Solo owner/admin del tenant o platform_admin pueden crear, editar o borrar.
Todas las mutaciones se auditan.
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
    create_archetype,
    delete_archetype,
    get_archetype,
    get_db,
    list_archetypes,
    transaction,
    update_archetype,
)
from .models import (
    ArchetypeCreate,
    ArchetypeRead,
    ArchetypeUpdate,
)

archetypes_router = APIRouter(prefix="/tenants", tags=["archetypes"])


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
    is_tenant_admin = user_tenant == tenant_id and (
        role in {"owner", "admin"} or {"owner", "admin"} & roles
    )
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


@archetypes_router.get("/{tenant_id}/archetypes")
def list_tenant_archetypes(
    tenant_id: str,
    request: Request,
    active_only: bool = False,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, list[ArchetypeRead]]:
    """List the tenant's archetypes."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    rows = list_archetypes(ctx, conn, active_only=active_only)
    return {"archetypes": [ArchetypeRead(**row) for row in rows]}


@archetypes_router.post("/{tenant_id}/archetypes", status_code=status.HTTP_201_CREATED)
def create_tenant_archetype(
    tenant_id: str,
    body: ArchetypeCreate,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> ArchetypeRead:
    """Create a new archetype for the tenant."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    try:
        with transaction(conn, ctx=ctx):
            _ensure_system_workspace(conn)
            created = create_archetype(
                ctx,
                conn,
                archetype_id=body.archetype_id,
                name=body.name,
                description=body.description,
                category=body.category,
                routing_preset_id=body.routing_preset_id,
                persona_md=body.persona_md,
                skill_md=body.skill_md,
                tools_allowlist=body.tools_allowlist,
                schema_output_json=body.schema_output_json,
                trigger_json=body.trigger_json,
                is_active=body.is_active,
                is_template=body.is_template,
            )
            audit_writer.write(
                ctx,
                conn,
                action="archetype.created",
                payload={
                    "archetype_id": created["archetype_id"],
                    "name": created["name"],
                    "routing_preset_id": created["routing_preset_id"],
                },
                system_event=True,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return ArchetypeRead(**created)


@archetypes_router.get("/{tenant_id}/archetypes/{archetype_id}")
def get_tenant_archetype(
    tenant_id: str,
    archetype_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> ArchetypeRead:
    """Fetch one archetype."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    row = get_archetype(ctx, conn, archetype_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Archetype '{archetype_id}' not found",
        )
    return ArchetypeRead(**row)


@archetypes_router.patch("/{tenant_id}/archetypes/{archetype_id}")
def patch_tenant_archetype(
    tenant_id: str,
    archetype_id: str,
    body: ArchetypeUpdate,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> ArchetypeRead:
    """Update an archetype. No toca las routines ya creadas: la herencia es plana."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    try:
        with transaction(conn, ctx=ctx):
            _ensure_system_workspace(conn)
            updated = update_archetype(
                ctx,
                conn,
                archetype_id,
                name=body.name,
                description=body.description,
                category=body.category,
                routing_preset_id=body.routing_preset_id,
                persona_md=body.persona_md,
                skill_md=body.skill_md,
                tools_allowlist=body.tools_allowlist,
                schema_output_json=body.schema_output_json,
                trigger_json=body.trigger_json,
                is_active=body.is_active,
                is_template=body.is_template,
            )
            if updated is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Archetype '{archetype_id}' not found",
                )
            audit_writer.write(
                ctx,
                conn,
                action="archetype.updated",
                payload={
                    "archetype_id": archetype_id,
                    "version": updated["version"],
                },
                system_event=True,
            )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    return ArchetypeRead(**updated)


@archetypes_router.delete(
    "/{tenant_id}/archetypes/{archetype_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_tenant_archetype(
    tenant_id: str,
    archetype_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> None:
    """Delete an archetype.

    Las routines ya creadas conservan su archetype_id: es procedencia historica,
    no un link vivo.
    """

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)
    with transaction(conn, ctx=ctx):
        _ensure_system_workspace(conn)
        deleted = delete_archetype(ctx, conn, archetype_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Archetype '{archetype_id}' not found",
            )
        audit_writer.write(
            ctx,
            conn,
            action="archetype.deleted",
            payload={"archetype_id": archetype_id},
            system_event=True,
        )
