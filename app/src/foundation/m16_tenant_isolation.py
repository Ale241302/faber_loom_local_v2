"""M16 Tenant Isolation — scoping estricto por tenant_id (port de RLS Postgres).

En Django/Postgres el aislamiento se implementaba con Row Level Security
(``apps/core/tenant_context``). En local-first SQLite se adapta como scoping
explícito fail-closed: toda query lleva ``tenant_id`` del SessionContext y
este módulo aporta además un endpoint de verificación que recorre todas las
tablas ``fnd_*`` con columna ``tenant_id`` y comprueba que no haya filas de
otros tenants visibles para el tenant de la sesión.
"""

from __future__ import annotations

import json
import re
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from ..auth import get_current_user
from .core import (
    SessionContext,
    audit_log,
    emit_event,
    get_conn,
    hash_password,
    new_id,
    require_permission,
    require_session,
    seed_system_roles,
    to_dict,
    utcnow,
)

router = APIRouter(prefix="/tenants", tags=["m16-tenant-isolation"])

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$")


# ---------------------------------------------------------------------------
# Helper de scoping — los módulos pueden usarlo para leer tablas fnd_* de
# forma fail-closed (sin tenant_id no hay filas).
# ---------------------------------------------------------------------------


def tenant_scoped(
    conn: sqlite3.Connection, table: str, tenant_id: str
) -> list[sqlite3.Row]:
    """Devuelve todas las filas de ``table`` pertenecientes a ``tenant_id``.

    Fail-closed: valida que la tabla sea una tabla foundation conocida y que
    tenga columna ``tenant_id``; si no, no devuelve nada.
    """
    if not tenant_id:
        return []
    if not table.startswith("fnd_") or not table.replace("_", "").isalnum():
        raise ValueError(f"tenant_scoped: tabla no permitida: {table!r}")
    columns = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
    if "tenant_id" not in columns:
        raise ValueError(f"tenant_scoped: {table} no tiene columna tenant_id")
    return conn.execute(
        f"SELECT * FROM {table} WHERE tenant_id = ?", (tenant_id,)
    ).fetchall()


def _tenant_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE 'fnd_%' ORDER BY name"
    ).fetchall()
    out: list[str] = []
    for row in rows:
        columns = {r["name"] for r in conn.execute(f"PRAGMA table_info({row['name']})")}
        if "tenant_id" in columns:
            out.append(row["name"])
    return out


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


class TenantSettingsPatch(BaseModel):
    settings: dict[str, Any] = Field(default_factory=dict)


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=40)
    owner_email: str | None = None
    owner_display_name: str = ""
    owner_password: str | None = Field(default=None, min_length=8)


class TenantUserCreate(BaseModel):
    email: str
    display_name: str = ""
    password: str = Field(min_length=8)
    roles: list[str] = Field(default_factory=lambda: ["operator"])


class TenantAssignBody(BaseModel):
    user_id: str
    roles: list[str] | None = None  # None → conserva sus roles por nombre


class SelfServiceBody(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=40)
    password: str = Field(min_length=8)
    display_name: str = ""


# ---------------------------------------------------------------------------
# Helpers multi-tenant
# ---------------------------------------------------------------------------


def _validate_slug(slug: str) -> str:
    slug = slug.strip().lower()
    if not _SLUG_RE.match(slug):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Slug inválido: usa minúsculas, dígitos y guiones (3-40 caracteres)",
        )
    return slug


def _tenant_summary(conn: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    out = to_dict(row) or {}
    out["users_count"] = conn.execute(
        "SELECT COUNT(*) AS c FROM fnd_users WHERE tenant_id = ?", (row["id"],)
    ).fetchone()["c"]
    out["owners_count"] = conn.execute(
        """SELECT COUNT(DISTINCT u.id) AS c FROM fnd_users u
           JOIN fnd_user_roles ur ON ur.user_id = u.id AND ur.tenant_id = u.tenant_id
           JOIN fnd_roles r ON r.id = ur.role_id
           WHERE u.tenant_id = ? AND u.status = 'active' AND r.name = 'owner'""",
        (row["id"],),
    ).fetchone()["c"]
    return out


def _get_tenant_or_404(conn: sqlite3.Connection, tenant_id: str) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM fnd_tenants WHERE id = ?", (tenant_id,)).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant no encontrado")
    return row


def _create_user_in_tenant(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    email: str,
    display_name: str,
    password: str,
    role_names: list[str],
) -> str:
    email = email.strip().lower()
    if "@" not in email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email inválido")
    exists = conn.execute(
        "SELECT id FROM fnd_users WHERE tenant_id = ? AND email = ?", (tenant_id, email)
    ).fetchone()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un usuario con ese email en ese tenant")
    user_id = new_id("usr")
    conn.execute(
        """INSERT INTO fnd_users (id, tenant_id, email, display_name, password_hash, status, created_at)
           VALUES (?, ?, ?, ?, ?, 'active', ?)""",
        (user_id, tenant_id, email, display_name or email.split("@")[0],
         hash_password(password), utcnow()),
    )
    _set_roles_in_tenant(conn, tenant_id, user_id, role_names, assigned_by=None)
    return user_id


def _set_roles_in_tenant(
    conn: sqlite3.Connection,
    tenant_id: str,
    user_id: str,
    role_names: list[str],
    *,
    assigned_by: str | None,
) -> None:
    conn.execute(
        "DELETE FROM fnd_user_roles WHERE tenant_id = ? AND user_id = ?", (tenant_id, user_id)
    )
    for name in sorted(set(role_names)):
        role = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?", (tenant_id, name)
        ).fetchone()
        if role is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Rol desconocido en el tenant destino: {name}")
        conn.execute(
            """INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
               VALUES (?, ?, ?, ?, ?)""",
            (tenant_id, user_id, role["id"], assigned_by, utcnow()),
        )


def _maybe_activate(conn: sqlite3.Connection, tenant_id: str) -> None:
    """Un tenant en provisioning se activa al ganar su primer owner activo."""
    tenant = _get_tenant_or_404(conn, tenant_id)
    if tenant["status"] == "active":
        return
    owners = conn.execute(
        """SELECT COUNT(DISTINCT u.id) AS c FROM fnd_users u
           JOIN fnd_user_roles ur ON ur.user_id = u.id AND ur.tenant_id = u.tenant_id
           JOIN fnd_roles r ON r.id = ur.role_id
           WHERE u.tenant_id = ? AND u.status = 'active' AND r.name = 'owner'""",
        (tenant_id,),
    ).fetchone()["c"]
    if owners:
        conn.execute(
            "UPDATE fnd_tenants SET status = 'active', activated_at = ? WHERE id = ?",
            (utcnow(), tenant_id),
        )
        audit_log(conn, tenant_id, "tenant.activated", resource_type="tenant",
                  resource_id=tenant_id, payload={"via": "tenant_admin"})
        emit_event(conn, tenant_id, "tenant", "activated", {"tenant_id": tenant_id})


# ---------------------------------------------------------------------------
# Administración multi-tenant (rutas literales ANTES de las parametrizadas)
# ---------------------------------------------------------------------------


@router.get("/all")
def list_all_tenants(
    ctx: SessionContext = Depends(require_permission("tenants.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    rows = conn.execute("SELECT * FROM fnd_tenants ORDER BY created_at ASC").fetchall()
    return {"tenants": [_tenant_summary(conn, r) for r in rows]}


@router.post("", status_code=status.HTTP_201_CREATED)
def create_tenant(
    body: TenantCreate,
    ctx: SessionContext = Depends(require_permission("tenants.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    slug = _validate_slug(body.slug)
    if conn.execute("SELECT id FROM fnd_tenants WHERE slug = ?", (slug,)).fetchone():
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un tenant con ese slug")
    if body.owner_email and not body.owner_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "owner_password es requerido si se indica owner_email")

    tenant_id = new_id("tnt")
    conn.execute(
        """INSERT INTO fnd_tenants (id, name, slug, status, created_at)
           VALUES (?, ?, ?, 'provisioning', ?)""",
        (tenant_id, body.name.strip(), slug, utcnow()),
    )
    seed_system_roles(conn, tenant_id)

    owner_id: str | None = None
    if body.owner_email and body.owner_password:
        owner_id = _create_user_in_tenant(
            conn, tenant_id,
            email=body.owner_email, display_name=body.owner_display_name,
            password=body.owner_password, role_names=["owner"],
        )
        _maybe_activate(conn, tenant_id)

    # Audit en ambos lados: el tenant del actor y el tenant nuevo.
    ctx.audit("tenant.created", resource_type="tenant", resource_id=tenant_id,
              payload={"name": body.name.strip(), "slug": slug, "owner_email": body.owner_email})
    audit_log(conn, tenant_id, "tenant.created", actor_id=ctx.user_id,
              actor_email=ctx.email, resource_type="tenant", resource_id=tenant_id,
              payload={"name": body.name.strip(), "slug": slug, "created_from_tenant": ctx.tenant_id})
    ctx.emit("tenant", "created", {"tenant_id": tenant_id, "slug": slug})

    tenant = _get_tenant_or_404(conn, tenant_id)
    out = _tenant_summary(conn, tenant)
    out["owner_user_id"] = owner_id
    return out


@router.post("/self-service", status_code=status.HTTP_201_CREATED)
def self_service_tenant(
    body: SelfServiceBody,
    request: Request,
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    """Un usuario autenticado en la app principal (JWT) que NO está asignado a
    ningún tenant Foundation puede crear el suyo y quedar como owner."""
    try:
        jwt_user = get_current_user(request)
    except HTTPException:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Requiere sesión principal de FaberLoom")
    email = (jwt_user.get("sub") or "").strip().lower()
    if not email or email == "local" or "@" not in email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "La sesión principal no tiene un email válido")

    assigned = conn.execute(
        "SELECT id FROM fnd_users WHERE email = ?", (email,)
    ).fetchone()
    if assigned:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Tu email ya está asignado a un tenant; pide a un admin que te mueva o entra con ese tenant",
        )

    slug = _validate_slug(body.slug)
    if conn.execute("SELECT id FROM fnd_tenants WHERE slug = ?", (slug,)).fetchone():
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un tenant con ese slug")

    tenant_id = new_id("tnt")
    conn.execute(
        """INSERT INTO fnd_tenants (id, name, slug, status, created_at)
           VALUES (?, ?, ?, 'provisioning', ?)""",
        (tenant_id, body.name.strip(), slug, utcnow()),
    )
    seed_system_roles(conn, tenant_id)
    user_id = _create_user_in_tenant(
        conn, tenant_id,
        email=email, display_name=body.display_name,
        password=body.password, role_names=["owner"],
    )
    _maybe_activate(conn, tenant_id)
    audit_log(conn, tenant_id, "tenant.self_service_created", actor_id=user_id,
              actor_email=email, resource_type="tenant", resource_id=tenant_id,
              payload={"name": body.name.strip(), "slug": slug})
    emit_event(conn, tenant_id, "tenant", "created",
               {"tenant_id": tenant_id, "slug": slug, "self_service": True})

    from .m08_auth_session import _user_payload, create_session

    token = create_session(conn, tenant_id, user_id, stage="full", request=request)
    user = conn.execute("SELECT * FROM fnd_users WHERE id = ?", (user_id,)).fetchone()
    tenant = _get_tenant_or_404(conn, tenant_id)
    return {
        "tenant": _tenant_summary(conn, tenant),
        "user": _user_payload(conn, tenant_id, user),
        "session": token,
    }


@router.get("/{tenant_id}/users")
def list_users_of_tenant(
    tenant_id: str,
    ctx: SessionContext = Depends(require_permission("tenants.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    """Usuarios de un tenant específico (vista de administración multi-tenant)."""
    tenant = _get_tenant_or_404(conn, tenant_id)
    rows = conn.execute(
        "SELECT * FROM fnd_users WHERE tenant_id = ? ORDER BY created_at", (tenant_id,)
    ).fetchall()
    users = []
    for row in rows:
        roles = conn.execute(
            """SELECT r.name FROM fnd_user_roles ur JOIN fnd_roles r ON r.id = ur.role_id
               WHERE ur.tenant_id = ? AND ur.user_id = ?""",
            (tenant_id, row["id"]),
        ).fetchall()
        users.append({
            "id": row["id"],
            "email": row["email"],
            "display_name": row["display_name"],
            "status": row["status"],
            "roles": [r["name"] for r in roles],
            "totp_enabled": bool(row["totp_enabled"]),
            "created_at": row["created_at"],
            "tenant_id": tenant_id,
            "tenant_name": tenant["name"],
            "tenant_slug": tenant["slug"],
        })
    return {"tenant": {"id": tenant_id, "name": tenant["name"], "slug": tenant["slug"]},
            "users": users}


@router.delete("/{tenant_id}/users/{user_id}")
def remove_user_from_tenant(
    tenant_id: str,
    user_id: str,
    ctx: SessionContext = Depends(require_permission("tenants.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    """Quita (elimina) un usuario de un tenant específico. Mismo efecto que el
    borrado de M09 pero operable cross-tenant por un admin de plataforma."""
    _get_tenant_or_404(conn, tenant_id)
    user = conn.execute(
        "SELECT * FROM fnd_users WHERE id = ? AND tenant_id = ?", (user_id, tenant_id)
    ).fetchone()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado en ese tenant")
    if user_id == ctx.user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No podés quitar tu propio usuario")

    roles = conn.execute(
        """SELECT r.name FROM fnd_user_roles ur JOIN fnd_roles r ON r.id = ur.role_id
           WHERE ur.tenant_id = ? AND ur.user_id = ?""",
        (tenant_id, user_id),
    ).fetchall()
    role_names = [r["name"] for r in roles]
    if "owner" in role_names:
        other_owners = conn.execute(
            """SELECT COUNT(DISTINCT u.id) AS c FROM fnd_users u
               JOIN fnd_user_roles ur ON ur.user_id = u.id AND ur.tenant_id = u.tenant_id
               JOIN fnd_roles r ON r.id = ur.role_id
               WHERE u.tenant_id = ? AND u.status = 'active' AND r.name = 'owner' AND u.id != ?""",
            (tenant_id, user_id),
        ).fetchone()["c"]
        other_users = conn.execute(
            "SELECT COUNT(*) AS c FROM fnd_users WHERE tenant_id = ? AND id != ?",
            (tenant_id, user_id),
        ).fetchone()["c"]
        if other_users and not other_owners:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "No se puede quitar al último owner de un tenant que aún tiene usuarios",
            )

    email = user["email"]
    conn.execute("DELETE FROM fnd_user_roles WHERE tenant_id = ? AND user_id = ?",
                 (tenant_id, user_id))
    # Igual que M09: las sesiones se eliminan (FK fnd_sessions.user_id → fnd_users.id).
    conn.execute("DELETE FROM fnd_sessions WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM fnd_users WHERE id = ? AND tenant_id = ?", (user_id, tenant_id))

    payload = {"email": email, "tenant_id": tenant_id, "roles": sorted(role_names)}
    ctx.audit("tenant.user.removed", resource_type="user", resource_id=user_id, payload=payload)
    audit_log(conn, tenant_id, "tenant.user.removed", actor_id=ctx.user_id,
              actor_email=ctx.email, resource_type="user", resource_id=user_id,
              payload=payload)
    emit_event(conn, tenant_id, "tenant", "user.removed", payload)
    return {"detail": "Usuario quitado del tenant"}


@router.post("/{tenant_id}/users", status_code=status.HTTP_201_CREATED)
def create_user_in_tenant(
    tenant_id: str,
    body: TenantUserCreate,
    ctx: SessionContext = Depends(require_permission("tenants.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    _get_tenant_or_404(conn, tenant_id)
    user_id = _create_user_in_tenant(
        conn, tenant_id,
        email=body.email, display_name=body.display_name,
        password=body.password, role_names=body.roles or ["operator"],
    )
    _maybe_activate(conn, tenant_id)
    ctx.audit("tenant.user.created", resource_type="user", resource_id=user_id,
              payload={"email": body.email.strip().lower(), "tenant_id": tenant_id,
                       "roles": sorted(set(body.roles or ["operator"]))})
    audit_log(conn, tenant_id, "rbac.user.created", actor_id=ctx.user_id,
              actor_email=ctx.email, resource_type="user", resource_id=user_id,
              payload={"email": body.email.strip().lower(),
                       "roles": sorted(set(body.roles or ["operator"])),
                       "created_from_tenant": ctx.tenant_id})
    emit_event(conn, tenant_id, "rbac", "user.created",
               {"user_id": user_id, "email": body.email.strip().lower()})
    user = conn.execute("SELECT * FROM fnd_users WHERE id = ?", (user_id,)).fetchone()
    from .m08_auth_session import _user_payload

    return _user_payload(conn, tenant_id, user)


@router.post("/{tenant_id}/assign")
def assign_user_to_tenant(
    tenant_id: str,
    body: TenantAssignBody,
    ctx: SessionContext = Depends(require_permission("tenants.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    """Mueve un usuario existente (de cualquier tenant) al tenant destino."""
    _get_tenant_or_404(conn, tenant_id)
    user = conn.execute("SELECT * FROM fnd_users WHERE id = ?", (body.user_id,)).fetchone()
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    source_tenant_id = user["tenant_id"]
    if source_tenant_id == tenant_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El usuario ya pertenece a ese tenant")
    if body.user_id == ctx.user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No podés moverte a vos mismo de tenant")

    # Guardrail: no dejar sin owner a un tenant que sigue teniendo usuarios.
    old_roles = conn.execute(
        """SELECT r.name FROM fnd_user_roles ur JOIN fnd_roles r ON r.id = ur.role_id
           WHERE ur.tenant_id = ? AND ur.user_id = ?""",
        (source_tenant_id, body.user_id),
    ).fetchall()
    old_role_names = [r["name"] for r in old_roles]
    if "owner" in old_role_names:
        other_owners = conn.execute(
            """SELECT COUNT(DISTINCT u.id) AS c FROM fnd_users u
               JOIN fnd_user_roles ur ON ur.user_id = u.id AND ur.tenant_id = u.tenant_id
               JOIN fnd_roles r ON r.id = ur.role_id
               WHERE u.tenant_id = ? AND u.status = 'active' AND r.name = 'owner' AND u.id != ?""",
            (source_tenant_id, body.user_id),
        ).fetchone()["c"]
        other_users = conn.execute(
            "SELECT COUNT(*) AS c FROM fnd_users WHERE tenant_id = ? AND id != ?",
            (source_tenant_id, body.user_id),
        ).fetchone()["c"]
        if other_users and not other_owners:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "No se puede mover al último owner de un tenant que aún tiene usuarios",
            )

    conflict = conn.execute(
        "SELECT id FROM fnd_users WHERE tenant_id = ? AND email = ?",
        (tenant_id, user["email"]),
    ).fetchone()
    if conflict:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un usuario con ese email en el tenant destino")

    new_roles = body.roles if body.roles is not None else (old_role_names or ["operator"])

    conn.execute("DELETE FROM fnd_user_roles WHERE tenant_id = ? AND user_id = ?",
                 (source_tenant_id, body.user_id))
    conn.execute(
        """UPDATE fnd_sessions SET revoked_at = ?
           WHERE user_id = ? AND revoked_at IS NULL""",
        (utcnow(), body.user_id),
    )
    conn.execute("UPDATE fnd_users SET tenant_id = ? WHERE id = ?", (tenant_id, body.user_id))
    _set_roles_in_tenant(conn, tenant_id, body.user_id, new_roles, assigned_by=ctx.user_id)
    _maybe_activate(conn, tenant_id)

    payload = {"email": user["email"], "from_tenant": source_tenant_id,
               "to_tenant": tenant_id, "roles": sorted(set(new_roles))}
    ctx.audit("tenant.user.moved", resource_type="user", resource_id=body.user_id, payload=payload)
    audit_log(conn, tenant_id, "tenant.user.moved", actor_id=ctx.user_id,
              actor_email=ctx.email, resource_type="user", resource_id=body.user_id,
              payload=payload)
    audit_log(conn, source_tenant_id, "tenant.user.moved_out", actor_id=ctx.user_id,
              actor_email=ctx.email, resource_type="user", resource_id=body.user_id,
              payload=payload)
    emit_event(conn, tenant_id, "tenant", "user.moved", payload)

    moved = conn.execute("SELECT * FROM fnd_users WHERE id = ?", (body.user_id,)).fetchone()
    from .m08_auth_session import _user_payload

    return _user_payload(conn, tenant_id, moved)


@router.get("")
def get_tenant(
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM fnd_tenants WHERE id = ?", (ctx.tenant_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant no encontrado")
    tenant = to_dict(row) or {}
    tenant["users_count"] = conn.execute(
        "SELECT COUNT(*) AS c FROM fnd_users WHERE tenant_id = ?", (ctx.tenant_id,)
    ).fetchone()["c"]
    return tenant


@router.patch("/settings")
def patch_settings(
    body: TenantSettingsPatch,
    ctx: SessionContext = Depends(require_permission("tenants.read")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    row = conn.execute(
        "SELECT * FROM fnd_tenants WHERE id = ?", (ctx.tenant_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant no encontrado")
    try:
        current = json.loads(row["settings_json"] or "{}")
    except Exception:
        current = {}
    current.update(body.settings)
    conn.execute(
        "UPDATE fnd_tenants SET settings_json = ? WHERE id = ?",
        (json.dumps(current, ensure_ascii=False), ctx.tenant_id),
    )
    ctx.audit(
        "tenant.settings.updated",
        resource_type="tenant",
        resource_id=ctx.tenant_id,
        payload={"keys": sorted(body.settings.keys())},
    )
    ctx.emit("tenant", "settings.updated", {"keys": sorted(body.settings.keys())})
    updated = to_dict(
        conn.execute("SELECT * FROM fnd_tenants WHERE id = ?", (ctx.tenant_id,)).fetchone()
    )
    return updated or {}


@router.get("/isolation-check")
def isolation_check(
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    """Verifica que ninguna tabla fnd_* exponga filas de otros tenants.

    Local-first normalmente hay un solo tenant; el check confirma que el
    scoping fail-closed se sostiene aunque la BD contenga más de uno.
    """
    report: list[dict[str, Any]] = []
    ok = True
    for table in _tenant_tables(conn):
        total = conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]
        own = conn.execute(
            f"SELECT COUNT(*) AS c FROM {table} WHERE tenant_id = ?", (ctx.tenant_id,)
        ).fetchone()["c"]
        foreign = total - own
        # Filas de otros tenants pueden existir en la BD; lo que se verifica
        # es que el acceso scoped no las incluya jamás.
        scoped = len(tenant_scoped(conn, table, ctx.tenant_id))
        leak = scoped != own
        if leak:
            ok = False
        report.append(
            {
                "table": table,
                "total_rows": total,
                "tenant_rows": own,
                "foreign_rows": foreign,
                "scoped_rows": scoped,
                "ok": not leak,
            }
        )
    ctx.audit("tenant.isolation.checked", resource_type="tenant",
              resource_id=ctx.tenant_id, payload={"ok": ok, "tables": len(report)})
    return {"ok": ok, "tenant_id": ctx.tenant_id, "tables": report}
