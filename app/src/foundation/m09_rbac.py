"""M09 RBAC — roles, permisos y gestión de usuarios del tenant.

Port de ``foundation_beta/backend/apps/rbac`` adaptado al modelo de
``fnd_roles`` / ``fnd_user_roles`` (permisos como lista plana en vez del
mapa surface→level de Django). Guardrails del plan M09:

- Siempre debe quedar al menos 1 owner activo en el tenant.
- Nadie puede quitarse a sí mismo el rol owner si es el último.
- Solo un owner puede otorgar o quitar el rol owner.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .core import (
    SYSTEM_ROLES,
    SessionContext,
    get_conn,
    get_user_permissions,
    hash_password,
    new_id,
    require_permission,
    require_session,
    user_role_names,
    utcnow,
)
from ..plans import PlanError, enforce_user_creation

router = APIRouter(prefix="/rbac", tags=["m09-rbac"])


# ---------------------------------------------------------------------------
# Bodies
# ---------------------------------------------------------------------------


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=40)
    description: str = ""
    permissions: list[str] = Field(default_factory=list)


class RolePatch(BaseModel):
    description: str | None = None
    permissions: list[str] | None = None


class UserCreate(BaseModel):
    email: str
    display_name: str = ""
    password: str = Field(min_length=8)
    roles: list[str] = Field(default_factory=list)


class UserPatch(BaseModel):
    display_name: str | None = None
    status: str | None = None  # active | disabled
    password: str | None = Field(default=None, min_length=8)


class UserRolesBody(BaseModel):
    roles: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def permission_catalog() -> list[str]:
    perms: set[str] = set()
    for spec in SYSTEM_ROLES.values():
        perms.update(p for p in spec["permissions"] if p != "*")
    return sorted(perms)


def _role_to_dict(row: sqlite3.Row, in_use: int | None = None) -> dict[str, Any]:
    out = {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "permissions": json.loads(row["permissions_json"] or "[]"),
        "is_system": bool(row["is_system"]),
        "created_at": row["created_at"],
    }
    if in_use is not None:
        out["assigned_users"] = in_use
    return out


def _user_to_dict(conn: sqlite3.Connection, tenant_id: str, row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "email": row["email"],
        "display_name": row["display_name"],
        "status": row["status"],
        "totp_enabled": bool(row["totp_enabled"]),
        "roles": user_role_names(conn, tenant_id, row["id"]),
        "permissions": sorted(get_user_permissions(conn, tenant_id, row["id"])),
        "created_at": row["created_at"],
    }


def _active_owner_ids(conn: sqlite3.Connection, tenant_id: str) -> set[str]:
    rows = conn.execute(
        """SELECT DISTINCT u.id FROM fnd_users u
           JOIN fnd_user_roles ur ON ur.user_id = u.id AND ur.tenant_id = u.tenant_id
           JOIN fnd_roles r ON r.id = ur.role_id
           WHERE u.tenant_id = ? AND u.status = 'active' AND r.name = 'owner'""",
        (tenant_id,),
    ).fetchall()
    return {r["id"] for r in rows}


def _get_role(conn: sqlite3.Connection, tenant_id: str, role_id: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM fnd_roles WHERE id = ? AND tenant_id = ?", (role_id, tenant_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rol no encontrado")
    return row


def _get_user(conn: sqlite3.Connection, tenant_id: str, user_id: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM fnd_users WHERE id = ? AND tenant_id = ?", (user_id, tenant_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return row


def _resolve_role_ids(
    conn: sqlite3.Connection, tenant_id: str, names: list[str]
) -> dict[str, str]:
    """name → role_id; 400 si algún rol no existe en el tenant."""
    out: dict[str, str] = {}
    for name in names:
        row = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?", (tenant_id, name)
        ).fetchone()
        if row is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Rol desconocido: {name}")
        out[name] = row["id"]
    return out


def _assign_roles(
    conn: sqlite3.Connection, ctx: SessionContext, user_id: str, role_names: list[str]
) -> None:
    """Reemplaza las asignaciones de roles del usuario (con guardrails)."""
    role_names = sorted(set(role_names))
    current = set(user_role_names(conn, ctx.tenant_id, user_id))
    new = set(role_names)

    owner_changed = ("owner" in current) != ("owner" in new)
    if owner_changed and "owner" not in ctx.roles:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Solo un owner puede otorgar o quitar el rol owner"
        )
    if "owner" in current and "owner" not in new:
        owners = _active_owner_ids(conn, ctx.tenant_id)
        if owners == {user_id}:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Debe quedar al menos 1 owner activo en el tenant",
            )

    ids = _resolve_role_ids(conn, ctx.tenant_id, role_names)
    conn.execute(
        "DELETE FROM fnd_user_roles WHERE tenant_id = ? AND user_id = ?",
        (ctx.tenant_id, user_id),
    )
    for name in role_names:
        conn.execute(
            """INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
               VALUES (?, ?, ?, ?, ?)""",
            (ctx.tenant_id, user_id, ids[name], ctx.user_id, utcnow()),
        )


# ---------------------------------------------------------------------------
# Catálogo y roles
# ---------------------------------------------------------------------------


@router.get("/permissions")
def list_permissions(
    ctx: SessionContext = Depends(require_session),
) -> dict[str, Any]:
    return {"permissions": permission_catalog(), "system_roles": sorted(SYSTEM_ROLES.keys())}


@router.get("/roles")
def list_roles(
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    rows = conn.execute(
        "SELECT * FROM fnd_roles WHERE tenant_id = ? ORDER BY is_system DESC, name",
        (ctx.tenant_id,),
    ).fetchall()
    roles = []
    for row in rows:
        in_use = conn.execute(
            "SELECT COUNT(*) AS c FROM fnd_user_roles WHERE tenant_id = ? AND role_id = ?",
            (ctx.tenant_id, row["id"]),
        ).fetchone()["c"]
        roles.append(_role_to_dict(row, in_use))
    return {"roles": roles}


@router.post("/roles", status_code=status.HTTP_201_CREATED)
def create_role(
    body: RoleCreate,
    ctx: SessionContext = Depends(require_permission("roles.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    name = body.name.strip().lower()
    if name in SYSTEM_ROLES:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nombre reservado para rol de sistema")
    exists = conn.execute(
        "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?", (ctx.tenant_id, name)
    ).fetchone()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un rol con ese nombre")
    catalog = set(permission_catalog())
    invalid = [p for p in body.permissions if p not in catalog]
    if invalid:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Permisos desconocidos: {invalid}")
    role_id = new_id("rol")
    conn.execute(
        """INSERT INTO fnd_roles (id, tenant_id, name, description, permissions_json, is_system, created_at)
           VALUES (?, ?, ?, ?, ?, 0, ?)""",
        (role_id, ctx.tenant_id, name, body.description,
         json.dumps(sorted(set(body.permissions))), utcnow()),
    )
    ctx.audit("rbac.role.created", resource_type="role", resource_id=role_id,
              payload={"name": name, "permissions": sorted(set(body.permissions))})
    ctx.emit("rbac", "role.created", {"role_id": role_id, "name": name})
    return _role_to_dict(_get_role(conn, ctx.tenant_id, role_id), 0)


@router.patch("/roles/{role_id}")
def patch_role(
    role_id: str,
    body: RolePatch,
    ctx: SessionContext = Depends(require_permission("roles.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    role = _get_role(conn, ctx.tenant_id, role_id)
    changes: dict[str, Any] = {}
    if body.permissions is not None:
        if role["is_system"]:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Los permisos de los roles de sistema no se pueden editar",
            )
        catalog = set(permission_catalog())
        invalid = [p for p in body.permissions if p not in catalog]
        if invalid:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Permisos desconocidos: {invalid}")
        conn.execute(
            "UPDATE fnd_roles SET permissions_json = ? WHERE id = ?",
            (json.dumps(sorted(set(body.permissions))), role_id),
        )
        changes["permissions"] = sorted(set(body.permissions))
    if body.description is not None:
        conn.execute(
            "UPDATE fnd_roles SET description = ? WHERE id = ?", (body.description, role_id)
        )
        changes["description"] = body.description
    if changes:
        ctx.audit("rbac.role.updated", resource_type="role", resource_id=role_id,
                  payload=changes)
        ctx.emit("rbac", "role.updated", {"role_id": role_id, "changes": sorted(changes)})
    return _role_to_dict(_get_role(conn, ctx.tenant_id, role_id))


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: str,
    ctx: SessionContext = Depends(require_permission("roles.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    role = _get_role(conn, ctx.tenant_id, role_id)
    if role["is_system"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se puede borrar un rol de sistema")
    in_use = conn.execute(
        "SELECT COUNT(*) AS c FROM fnd_user_roles WHERE tenant_id = ? AND role_id = ?",
        (ctx.tenant_id, role_id),
    ).fetchone()["c"]
    if in_use:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"El rol está asignado a {in_use} usuario(s)"
        )
    conn.execute(
        "DELETE FROM fnd_roles WHERE id = ? AND tenant_id = ?", (role_id, ctx.tenant_id)
    )
    ctx.audit("rbac.role.deleted", resource_type="role", resource_id=role_id,
              payload={"name": role["name"]})
    ctx.emit("rbac", "role.deleted", {"role_id": role_id, "name": role["name"]})
    return {"detail": "Rol eliminado"}


# ---------------------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------------------


@router.get("/users")
def list_users(
    ctx: SessionContext = Depends(require_permission("users.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    rows = conn.execute(
        "SELECT * FROM fnd_users WHERE tenant_id = ? ORDER BY created_at", (ctx.tenant_id,)
    ).fetchall()
    return {"users": [_user_to_dict(conn, ctx.tenant_id, r) for r in rows]}


@router.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    ctx: SessionContext = Depends(require_permission("users.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    email = body.email.strip().lower()
    if "@" not in email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email inválido")
    exists = conn.execute(
        "SELECT id FROM fnd_users WHERE tenant_id = ? AND email = ?", (ctx.tenant_id, email)
    ).fetchone()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe un usuario con ese email")
    if "owner" in body.roles and "owner" not in ctx.roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo un owner puede crear otro owner")

    try:
        enforce_user_creation(ctx.tenant_id)
    except PlanError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc

    user_id = new_id("usr")
    conn.execute(
        """INSERT INTO fnd_users (id, tenant_id, email, display_name, password_hash, status, created_at)
           VALUES (?, ?, ?, ?, ?, 'active', ?)""",
        (user_id, ctx.tenant_id, email, body.display_name or email.split("@")[0],
         hash_password(body.password), utcnow()),
    )
    if body.roles:
        _assign_roles(conn, ctx, user_id, body.roles)
    ctx.audit("rbac.user.created", resource_type="user", resource_id=user_id,
              payload={"email": email, "roles": sorted(set(body.roles))})
    ctx.emit("rbac", "user.created", {"user_id": user_id, "email": email})
    return _user_to_dict(conn, ctx.tenant_id, _get_user(conn, ctx.tenant_id, user_id))


@router.patch("/users/{user_id}")
def patch_user(
    user_id: str,
    body: UserPatch,
    ctx: SessionContext = Depends(require_permission("users.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    user = _get_user(conn, ctx.tenant_id, user_id)
    changes: dict[str, Any] = {}

    if body.status is not None:
        if body.status not in ("active", "disabled"):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "status debe ser active|disabled")
        if body.status != "active":
            owners = _active_owner_ids(conn, ctx.tenant_id)
            if user_id in owners and owners == {user_id}:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "No se puede desactivar al último owner activo",
                )
            if "owner" in user_role_names(conn, ctx.tenant_id, user_id) and "owner" not in ctx.roles:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, "Solo un owner puede desactivar a un owner"
                )
        conn.execute("UPDATE fnd_users SET status = ? WHERE id = ?", (body.status, user_id))
        if body.status != "active":
            # Revocar sesiones activas del usuario desactivado.
            conn.execute(
                """UPDATE fnd_sessions SET revoked_at = ?
                   WHERE tenant_id = ? AND user_id = ? AND revoked_at IS NULL""",
                (utcnow(), ctx.tenant_id, user_id),
            )
        changes["status"] = body.status

    if body.display_name is not None:
        conn.execute(
            "UPDATE fnd_users SET display_name = ? WHERE id = ?", (body.display_name, user_id)
        )
        changes["display_name"] = body.display_name

    if body.password is not None:
        conn.execute(
            "UPDATE fnd_users SET password_hash = ?, failed_attempts = 0, locked_until = NULL WHERE id = ?",
            (hash_password(body.password), user_id),
        )
        changes["password"] = "reset"

    if changes:
        ctx.audit("rbac.user.updated", resource_type="user", resource_id=user_id,
                  payload=changes)
        ctx.emit("rbac", "user.updated", {"user_id": user_id, "changes": sorted(changes)})
    return _user_to_dict(conn, ctx.tenant_id, _get_user(conn, ctx.tenant_id, user_id))


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    ctx: SessionContext = Depends(require_permission("users.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    user = _get_user(conn, ctx.tenant_id, user_id)

    if user_id == ctx.user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No podés eliminar tu propio usuario")

    is_owner = "owner" in user_role_names(conn, ctx.tenant_id, user_id)
    if is_owner and "owner" not in ctx.roles:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo un owner puede eliminar a un owner")

    owners = _active_owner_ids(conn, ctx.tenant_id)
    if user_id in owners and owners == {user_id}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Debe quedar al menos 1 owner activo en el tenant")

    email = user["email"]
    conn.execute("DELETE FROM fnd_user_roles WHERE tenant_id = ? AND user_id = ?",
                 (ctx.tenant_id, user_id))
    conn.execute("DELETE FROM fnd_sessions WHERE tenant_id = ? AND user_id = ?",
                 (ctx.tenant_id, user_id))
    conn.execute("DELETE FROM fnd_users WHERE id = ? AND tenant_id = ?",
                 (user_id, ctx.tenant_id))

    ctx.audit("rbac.user.deleted", resource_type="user", resource_id=user_id,
              payload={"email": email, "was_owner": is_owner})
    ctx.emit("rbac", "user.deleted", {"user_id": user_id, "email": email})
    return {"detail": "Usuario eliminado"}


@router.post("/users/{user_id}/roles")
def set_user_roles(
    user_id: str,
    body: UserRolesBody,
    ctx: SessionContext = Depends(require_permission("users.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    _get_user(conn, ctx.tenant_id, user_id)
    before = user_role_names(conn, ctx.tenant_id, user_id)
    _assign_roles(conn, ctx, user_id, body.roles)
    after = user_role_names(conn, ctx.tenant_id, user_id)
    ctx.audit("rbac.user.roles_changed", resource_type="user", resource_id=user_id,
              payload={"before": sorted(before), "after": sorted(after)})
    ctx.emit("rbac", "user.roles_changed", {"user_id": user_id, "roles": sorted(after)})
    return _user_to_dict(conn, ctx.tenant_id, _get_user(conn, ctx.tenant_id, user_id))
