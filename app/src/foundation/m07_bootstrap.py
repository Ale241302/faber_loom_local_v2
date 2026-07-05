"""M07 Bootstrap Wizard — provisioning inicial del tenant local-first.

Port de ``foundation_beta/backend/apps/bootstrap``: el wizard Django tenía 8
pasos (tenant_data, owner_2fa, mailbox, kb_seed, voice_profile, dpa_signed,
seed_agents, sandbox_ok). Local-first se reduce al núcleo del spine:

    tenant → owner → security (2FA opcional, reportado) → activate

Los endpoints PRE-AUTH solo funcionan mientras el tenant no está activo
(``is_bootstrapped`` → 409, salvo GET /state). Al crear el owner se abre una
sesión full para que el wizard continúe autenticado, y /activate exige
permiso ``bootstrap.manage`` (u owner ``*``).
"""

from __future__ import annotations

import re
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from .core import (
    SessionContext,
    audit_log,
    emit_event,
    get_active_tenant,
    get_conn,
    hash_password,
    is_bootstrapped,
    new_id,
    require_session,
    seed_system_roles,
    to_dict,
    utcnow,
)
from .m08_auth_session import _user_payload, create_session

router = APIRouter(prefix="/bootstrap", tags=["m07-bootstrap"])

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$")


class TenantBody(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=40)


class OwnerBody(BaseModel):
    email: str
    display_name: str = ""
    password: str = Field(min_length=8)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _guard_not_bootstrapped(conn: sqlite3.Connection) -> None:
    if is_bootstrapped(conn):
        raise HTTPException(status.HTTP_409_CONFLICT, "El tenant ya está activo")


def _owner_users(conn: sqlite3.Connection, tenant_id: str) -> list[sqlite3.Row]:
    return conn.execute(
        """SELECT DISTINCT u.* FROM fnd_users u
           JOIN fnd_user_roles ur ON ur.user_id = u.id AND ur.tenant_id = u.tenant_id
           JOIN fnd_roles r ON r.id = ur.role_id
           WHERE u.tenant_id = ? AND r.name = 'owner'""",
        (tenant_id,),
    ).fetchall()


def _checklist(conn: sqlite3.Connection) -> dict[str, Any]:
    tenant = get_active_tenant(conn)
    owners = _owner_users(conn, tenant["id"]) if tenant else []
    active_owners = [o for o in owners if o["status"] == "active"]
    owner_2fa = any(o["totp_enabled"] for o in active_owners)
    return {
        "tenant_created": tenant is not None,
        "owner_exists": len(active_owners) > 0,
        "owner_2fa_enabled": owner_2fa,  # opcional, solo informativo
        "activated": bool(tenant and tenant["status"] == "active"),
    }


def _step(conn: sqlite3.Connection) -> str:
    tenant = get_active_tenant(conn)
    if tenant is None:
        return "tenant"
    if not any(o["status"] == "active" for o in _owner_users(conn, tenant["id"])):
        return "owner"
    if tenant["status"] != "active":
        return "security"  # 2FA opcional → luego activate
    return "done"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/state")
def get_state(conn: sqlite3.Connection = Depends(get_conn)) -> dict[str, Any]:
    tenant = get_active_tenant(conn)
    return {
        "step": _step(conn),
        "steps": ["tenant", "owner", "security", "activate"],
        "tenant": to_dict(tenant),
        "checklist": _checklist(conn),
        "bootstrapped": is_bootstrapped(conn),
    }


@router.post("/tenant", status_code=status.HTTP_201_CREATED)
def create_tenant(
    body: TenantBody, conn: sqlite3.Connection = Depends(get_conn)
) -> dict[str, Any]:
    _guard_not_bootstrapped(conn)
    if get_active_tenant(conn) is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un tenant en provisioning")
    slug = body.slug.strip().lower()
    if not _SLUG_RE.match(slug):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Slug inválido: usa minúsculas, dígitos y guiones (3-40 caracteres)",
        )
    tenant_id = new_id("tnt")
    conn.execute(
        """INSERT INTO fnd_tenants (id, name, slug, status, created_at)
           VALUES (?, ?, ?, 'provisioning', ?)""",
        (tenant_id, body.name.strip(), slug, utcnow()),
    )
    seed_system_roles(conn, tenant_id)
    audit_log(conn, tenant_id, "tenant.created", resource_type="tenant",
              resource_id=tenant_id, payload={"name": body.name.strip(), "slug": slug})
    emit_event(conn, tenant_id, "tenant", "created", {"tenant_id": tenant_id, "slug": slug})
    tenant = get_active_tenant(conn)
    return {"tenant": to_dict(tenant), "step": _step(conn)}


@router.post("/owner", status_code=status.HTTP_201_CREATED)
def create_owner(
    body: OwnerBody,
    request: Request,
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    _guard_not_bootstrapped(conn)
    tenant = get_active_tenant(conn)
    if tenant is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Primero crea el tenant")
    tenant_id = tenant["id"]
    if any(o["status"] == "active" for o in _owner_users(conn, tenant_id)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un owner activo")

    email = body.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email inválido")
    exists = conn.execute(
        "SELECT id FROM fnd_users WHERE tenant_id = ? AND email = ?", (tenant_id, email)
    ).fetchone()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un usuario con ese email")

    user_id = new_id("usr")
    conn.execute(
        """INSERT INTO fnd_users (id, tenant_id, email, display_name, password_hash, status, created_at)
           VALUES (?, ?, ?, ?, ?, 'active', ?)""",
        (user_id, tenant_id, email, body.display_name or email.split("@")[0],
         hash_password(body.password), utcnow()),
    )
    owner_role = conn.execute(
        "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = 'owner'", (tenant_id,)
    ).fetchone()
    if owner_role is None:  # defensivo: seed si faltara
        seed_system_roles(conn, tenant_id)
        owner_role = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = 'owner'", (tenant_id,)
        ).fetchone()
    conn.execute(
        """INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
           VALUES (?, ?, ?, NULL, ?)""",
        (tenant_id, user_id, owner_role["id"], utcnow()),
    )

    token = create_session(conn, tenant_id, user_id, stage="full", request=request)
    audit_log(conn, tenant_id, "bootstrap.owner.created", actor_id=user_id,
              actor_email=email, resource_type="user", resource_id=user_id,
              payload={"roles": ["owner"]})
    emit_event(conn, tenant_id, "tenant", "owner.created",
               {"user_id": user_id, "email": email})
    user = conn.execute("SELECT * FROM fnd_users WHERE id = ?", (user_id,)).fetchone()
    return {
        "session": token,
        "user": _user_payload(conn, tenant_id, user),
        "step": _step(conn),
    }


@router.get("/checklist")
def get_checklist(
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    return {"checklist": _checklist(conn), "step": _step(conn)}


@router.post("/activate")
def activate_tenant(
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    if not ctx.has("bootstrap.manage"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Requiere permiso bootstrap.manage")
    tenant = conn.execute(
        "SELECT * FROM fnd_tenants WHERE id = ?", (ctx.tenant_id,)
    ).fetchone()
    if tenant is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant no encontrado")
    if tenant["status"] == "active":
        raise HTTPException(status.HTTP_409_CONFLICT, "El tenant ya está activo")

    checklist = _checklist(conn)
    if not checklist["tenant_created"] or not checklist["owner_exists"]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Checklist incompleta: se requiere tenant y al menos 1 owner activo",
        )

    conn.execute(
        "UPDATE fnd_tenants SET status = 'active', activated_at = ? WHERE id = ?",
        (utcnow(), ctx.tenant_id),
    )
    ctx.audit("tenant.activated", resource_type="tenant", resource_id=ctx.tenant_id,
              payload={"checklist": checklist})
    ctx.emit("tenant", "activated", {"tenant_id": ctx.tenant_id, "activated_by": ctx.user_id})
    tenant = conn.execute(
        "SELECT * FROM fnd_tenants WHERE id = ?", (ctx.tenant_id,)
    ).fetchone()
    return {"tenant": to_dict(tenant), "checklist": _checklist(conn), "step": _step(conn)}
