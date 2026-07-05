"""M15 Outbox Streams — event log transaccional + polling realtime.

Port de ``foundation_beta/backend/apps/events``: en Django el patrón era
outbox (Postgres) + Celery publisher + Channels/WebSocket. Local-first se
adapta a:

- ``fnd_events`` (core) escrito por :func:`core.emit_event` en la misma
  transacción del request → transactional outbox (published_at inmediato,
  no hay broker externo).
- Realtime → polling con ``after_seq`` (el frontend refresca cada 5s).
- Consumers → tabla ``fnd_event_consumers`` con ack de última secuencia y
  cálculo de lag (reemplaza los consumer groups de Redis Streams).
"""

from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from .core import (
    SessionContext,
    get_conn,
    register_schema,
    require_permission,
    rows_to_dicts,
    utcnow,
)

router = APIRouter(prefix="/events", tags=["m15-outbox-streams"])

register_schema(
    """
CREATE TABLE IF NOT EXISTS fnd_event_consumers (
    consumer TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    last_seq INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, consumer)
);
"""
)

MAX_LIMIT = 500


class AckBody(BaseModel):
    seq: int = Field(ge=0)


@router.get("")
def list_events(
    topic: str | None = Query(default=None),
    type: str | None = Query(default=None),
    after_seq: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=MAX_LIMIT),
    ctx: SessionContext = Depends(require_permission("events.read")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    """Polling realtime: eventos del tenant con seq > after_seq."""
    query = "SELECT * FROM fnd_events WHERE tenant_id = ? AND seq > ?"
    params: list[Any] = [ctx.tenant_id, after_seq]
    if topic:
        query += " AND topic = ?"
        params.append(topic)
    if type:
        query += " AND type = ?"
        params.append(type)
    query += " ORDER BY seq ASC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    events = rows_to_dicts(rows)
    last_seq = events[-1]["seq"] if events else after_seq
    return {"events": events, "last_seq": last_seq, "count": len(events)}


@router.get("/topics")
def list_topics(
    ctx: SessionContext = Depends(require_permission("events.read")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    rows = conn.execute(
        """SELECT topic, COUNT(*) AS count, MAX(seq) AS last_seq, MAX(created_at) AS last_at
           FROM fnd_events WHERE tenant_id = ? GROUP BY topic ORDER BY topic""",
        (ctx.tenant_id,),
    ).fetchall()
    return {"topics": [dict(r) for r in rows]}


@router.post("/consumers/{name}/ack")
def ack_consumer(
    name: str,
    body: AckBody,
    ctx: SessionContext = Depends(require_permission("events.read")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    if not name or len(name) > 80:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nombre de consumer inválido")
    max_seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) AS m FROM fnd_events WHERE tenant_id = ?",
        (ctx.tenant_id,),
    ).fetchone()["m"]
    if body.seq > max_seq:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"seq {body.seq} es mayor que la última secuencia del tenant ({max_seq})",
        )
    conn.execute(
        """INSERT INTO fnd_event_consumers (consumer, tenant_id, last_seq, updated_at)
           VALUES (?, ?, ?, ?)
           ON CONFLICT (tenant_id, consumer)
           DO UPDATE SET last_seq = excluded.last_seq, updated_at = excluded.updated_at""",
        (name, ctx.tenant_id, body.seq, utcnow()),
    )
    return {"consumer": name, "last_seq": body.seq, "lag": max_seq - body.seq}


@router.get("/stream-status")
def stream_status(
    ctx: SessionContext = Depends(require_permission("events.read")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    max_seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) AS m FROM fnd_events WHERE tenant_id = ?",
        (ctx.tenant_id,),
    ).fetchone()["m"]
    total = conn.execute(
        "SELECT COUNT(*) AS c FROM fnd_events WHERE tenant_id = ?", (ctx.tenant_id,)
    ).fetchone()["c"]
    rows = conn.execute(
        "SELECT * FROM fnd_event_consumers WHERE tenant_id = ? ORDER BY consumer",
        (ctx.tenant_id,),
    ).fetchall()
    consumers = [
        {
            "consumer": r["consumer"],
            "last_seq": r["last_seq"],
            "lag": max(0, max_seq - r["last_seq"]),
            "updated_at": r["updated_at"],
        }
        for r in rows
    ]
    return {"last_seq": max_seq, "total_events": total, "consumers": consumers}
