"""M12 Audit Trail — lectura, verificación y export de la cadena de auditoría.

Port de ``foundation_beta/backend/apps/audit``. La escritura vive en
``core.audit_log`` (hash chain append-only por tenant, misma transacción del
request). Este módulo solo expone lectura: el trail es inmutable, no hay
endpoints de mutación ni borrado.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from .core import (
    SessionContext,
    get_conn,
    require_permission,
    rows_to_dicts,
    verify_audit_chain,
)

router = APIRouter(prefix="/audit", tags=["m12-audit-trail"])

MAX_LIMIT = 1000


def _query_entries(
    conn: sqlite3.Connection,
    tenant_id: str,
    *,
    action: str | None,
    actor: str | None,
    resource_type: str | None,
    after_seq: int,
    limit: int | None,
) -> list[sqlite3.Row]:
    query = "SELECT * FROM fnd_audit_log WHERE tenant_id = ? AND seq > ?"
    params: list[Any] = [tenant_id, after_seq]
    if action:
        query += " AND action LIKE ?"
        params.append(f"%{action}%")
    if actor:
        query += " AND (actor_email LIKE ? OR actor_id = ?)"
        params.extend([f"%{actor}%", actor])
    if resource_type:
        query += " AND resource_type = ?"
        params.append(resource_type)
    query += " ORDER BY seq ASC"
    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)
    return conn.execute(query, params).fetchall()


@router.get("")
def list_audit(
    action: str | None = Query(default=None),
    actor: str | None = Query(default=None),
    resource_type: str | None = Query(default=None),
    after_seq: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=MAX_LIMIT),
    ctx: SessionContext = Depends(require_permission("audit.read")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    rows = _query_entries(
        conn, ctx.tenant_id, action=action, actor=actor,
        resource_type=resource_type, after_seq=after_seq, limit=limit,
    )
    entries = rows_to_dicts(rows)
    return {
        "entries": entries,
        "count": len(entries),
        "last_seq": entries[-1]["seq"] if entries else after_seq,
    }


@router.get("/verify")
def verify_chain(
    ctx: SessionContext = Depends(require_permission("audit.read")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    result = verify_audit_chain(conn, ctx.tenant_id)
    result["tenant_id"] = ctx.tenant_id
    return result


@router.get("/export")
def export_audit(
    ctx: SessionContext = Depends(require_permission("audit.read")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> Response:
    """Export completo del trail del tenant en JSONL (application/x-ndjson)."""
    rows = _query_entries(
        conn, ctx.tenant_id, action=None, actor=None,
        resource_type=None, after_seq=0, limit=None,
    )
    lines = [json.dumps(dict(r), ensure_ascii=False, sort_keys=True) for r in rows]
    body = "\n".join(lines) + ("\n" if lines else "")
    return Response(
        content=body,
        media_type="application/x-ndjson",
        headers={
            "Content-Disposition": f'attachment; filename="audit_{ctx.tenant_id}.jsonl"'
        },
    )
