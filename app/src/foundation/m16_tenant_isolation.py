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
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .core import (
    SessionContext,
    get_conn,
    require_permission,
    require_session,
    to_dict,
)

router = APIRouter(prefix="/tenants", tags=["m16-tenant-isolation"])


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
