"""M19 Offline Sync — cursores, delta vs full refresh y cola de mutaciones.

Port de ``foundation_beta/desktop/src/main/sync.js`` (Electron):

- Los cursores que Electron guardaba en ``electron-store``
  (``last_event_id``/``last_sync_at``) viven en el servidor por device
  (``fnd_sync_state``), con ``fnd_events.seq`` como cursor monotónico.
- WS ``/ws/events?since=`` → polling HTTP: ``POST /pull`` devuelve el delta de
  ``fnd_events`` o pide ``full_refresh`` (regla del plan M19: gap > 24h o
  cursor perdido → full refresh).
- Cola de mutaciones offline (``fnd_sync_mutations``): ``POST /push`` encola,
  ``POST /apply`` procesa en orden con estrategia last-write-wins + detección
  de conflicto simple (si el recurso tiene un evento posterior a queued_at →
  conflict).
- ``pending_mutations()`` es el gate que consume M20: mientras haya
  mutaciones queued|conflict el update no debe instalarse.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .core import (
    SessionContext,
    new_id,
    register_schema,
    require_session,
    rows_to_dicts,
    to_dict,
    utcnow,
)
from .m18_desktop_auth import get_tenant_device

router = APIRouter(prefix="/sync", tags=["foundation-m19"])

DELTA_WINDOW_HOURS = 24  # regla del plan M19: gap > 24h → full refresh

SCHEMA = """
CREATE TABLE IF NOT EXISTS fnd_sync_state (
    device_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    last_event_seq INTEGER,
    last_sync_at TEXT,
    mode TEXT NOT NULL DEFAULT 'delta',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fnd_sync_mutations (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    device_id TEXT NOT NULL,
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    body_json TEXT NOT NULL DEFAULT '{}',
    queued_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    applied_at TEXT,
    error TEXT
);
CREATE INDEX IF NOT EXISTS idx_fnd_sync_mut_tenant
    ON fnd_sync_mutations(tenant_id, device_id, status);
"""
register_schema(SCHEMA)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def pending_mutations(conn, tenant_id: str, device_id: str) -> int:
    """Mutaciones que impiden instalar un update (gate M19→M20)."""
    row = conn.execute(
        """SELECT COUNT(*) AS c FROM fnd_sync_mutations
           WHERE tenant_id = ? AND device_id = ? AND status IN ('queued', 'conflict')""",
        (tenant_id, device_id),
    ).fetchone()
    return int(row["c"]) if row else 0


def _get_state(conn, tenant_id: str, device_id: str):
    return conn.execute(
        "SELECT * FROM fnd_sync_state WHERE device_id = ? AND tenant_id = ?",
        (device_id, tenant_id),
    ).fetchone()


def _upsert_state(conn, tenant_id: str, device_id: str, *, last_event_seq=None,
                  last_sync_at=None, mode: str | None = None) -> None:
    existing = _get_state(conn, tenant_id, device_id)
    now = utcnow()
    if existing is None:
        conn.execute(
            """INSERT INTO fnd_sync_state
               (device_id, tenant_id, last_event_seq, last_sync_at, mode, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (device_id, tenant_id, last_event_seq, last_sync_at, mode or "delta", now),
        )
        return
    conn.execute(
        """UPDATE fnd_sync_state SET
             last_event_seq = COALESCE(?, last_event_seq),
             last_sync_at = COALESCE(?, last_sync_at),
             mode = COALESCE(?, mode),
             updated_at = ?
           WHERE device_id = ? AND tenant_id = ?""",
        (last_event_seq, last_sync_at, mode, now, device_id, tenant_id),
    )


def _hours_since(iso: str | None) -> float:
    """Port de ``hoursSince`` de sync.js (sin fecha → Infinity)."""
    if not iso:
        return float("inf")
    try:
        then = datetime.fromisoformat(iso)
        if then.tzinfo is None:
            then = then.replace(tzinfo=timezone.utc)
    except ValueError:
        return float("inf")
    return (datetime.now(timezone.utc) - then).total_seconds() / 3600.0


def _max_event_seq(conn, tenant_id: str) -> int:
    row = conn.execute(
        "SELECT MAX(seq) AS m FROM fnd_events WHERE tenant_id = ?", (tenant_id,)
    ).fetchone()
    return int(row["m"]) if row and row["m"] is not None else 0


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------


class DeviceRef(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)


class MutationIn(BaseModel):
    method: str = Field(min_length=1, max_length=10)
    path: str = Field(min_length=1, max_length=500)
    body: dict[str, Any] = Field(default_factory=dict)


class PushIn(DeviceRef):
    mutations: list[MutationIn] = Field(default_factory=list, max_length=200)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/status")
def sync_status(ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Estado de sync del device ligado a la sesión actual."""
    session = ctx.conn.execute(
        "SELECT device_id FROM fnd_sessions WHERE id = ?", (ctx.session_id,)
    ).fetchone()
    device_id = session["device_id"] if session else ""
    if not device_id:
        return {"state": "unbound", "device_id": None,
                "hint": "Registra este dispositivo en M18 para habilitar sync."}
    state = _get_state(ctx.conn, ctx.tenant_id, device_id)
    return {
        "state": "bound",
        "device_id": device_id,
        "sync": to_dict(state) if state else None,
        "pending_mutations": pending_mutations(ctx.conn, ctx.tenant_id, device_id),
        "server_max_seq": _max_event_seq(ctx.conn, ctx.tenant_id),
    }


@router.post("/pull")
def sync_pull(body: DeviceRef, ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Cold start / reconexión: delta si el gap ≤ 24h, si no full refresh."""
    device = get_tenant_device(ctx.conn, ctx.tenant_id, body.device_id)
    state = _get_state(ctx.conn, ctx.tenant_id, device["id"])

    has_cursor = state is not None and state["last_event_seq"] is not None
    gap_hours = _hours_since(state["last_sync_at"]) if state is not None else float("inf")

    if has_cursor and gap_hours <= DELTA_WINDOW_HOURS:
        rows = ctx.conn.execute(
            "SELECT * FROM fnd_events WHERE tenant_id = ? AND seq > ? ORDER BY seq ASC LIMIT 500",
            (ctx.tenant_id, state["last_event_seq"]),
        ).fetchall()
        events = []
        for r in rows:
            item = to_dict(r) or {}
            item["seq"] = r["seq"]
            events.append(item)
        next_seq = rows[-1]["seq"] if rows else int(state["last_event_seq"])
        _upsert_state(ctx.conn, ctx.tenant_id, device["id"],
                      last_event_seq=next_seq, last_sync_at=utcnow(), mode="delta")
        ctx.audit("sync.pull", resource_type="device", resource_id=device["id"],
                  payload={"mode": "delta", "events": len(events), "next_seq": next_seq})
        return {"mode": "delta", "events": events, "next_seq": next_seq}

    reason = ("cursor de eventos ausente" if not has_cursor
              else f"gap de {gap_hours:.1f}h > {DELTA_WINDOW_HOURS}h desde el último sync")
    # No se avanza el cursor: el cliente debe re-descargar estado y reconciliar.
    _upsert_state(ctx.conn, ctx.tenant_id, device["id"], mode="full")
    ctx.audit("sync.pull", resource_type="device", resource_id=device["id"],
              payload={"mode": "full_refresh", "reason": reason})
    ctx.emit("sync", "sync.full_refresh_required", {"device_id": device["id"], "reason": reason})
    return {"mode": "full_refresh", "reason": reason,
            "server_max_seq": _max_event_seq(ctx.conn, ctx.tenant_id)}


@router.post("/push")
def sync_push(body: PushIn, ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Encola mutaciones capturadas offline (no las aplica todavía)."""
    device = get_tenant_device(ctx.conn, ctx.tenant_id, body.device_id)
    if not body.mutations:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Sin mutaciones que encolar")
    ids: list[str] = []
    now = utcnow()
    for m in body.mutations:
        mut_id = new_id("mut")
        ctx.conn.execute(
            """INSERT INTO fnd_sync_mutations
               (id, tenant_id, device_id, method, path, body_json, queued_at, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, 'queued')""",
            (mut_id, ctx.tenant_id, device["id"], m.method.upper(), m.path,
             json.dumps(m.body, ensure_ascii=False), now),
        )
        ids.append(mut_id)
    ctx.audit("sync.push", resource_type="device", resource_id=device["id"],
              payload={"queued": len(ids)})
    ctx.emit("sync", "sync.mutations_queued", {"device_id": device["id"], "count": len(ids)})
    return {"queued": len(ids), "mutation_ids": ids}


@router.post("/apply")
def sync_apply(body: DeviceRef, ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Procesa la cola en orden (last-write-wins con detección de conflicto).

    Conflicto simple del plan M19: si el recurso (path) tiene un evento de
    dominio posterior a ``queued_at``, alguien más lo modificó mientras el
    device estaba offline → se marca ``conflict`` con detalle, no se pisa.
    Los eventos con topic ``sync`` se excluyen (son meta-eventos propios).
    """
    device = get_tenant_device(ctx.conn, ctx.tenant_id, body.device_id)
    queued = ctx.conn.execute(
        """SELECT * FROM fnd_sync_mutations
           WHERE tenant_id = ? AND device_id = ? AND status = 'queued'
           ORDER BY queued_at ASC, rowid ASC""",
        (ctx.tenant_id, device["id"]),
    ).fetchall()

    applied, conflicts = 0, 0
    results: list[dict[str, Any]] = []
    for m in queued:
        newer = ctx.conn.execute(
            """SELECT id, type, created_at FROM fnd_events
               WHERE tenant_id = ? AND topic != 'sync' AND created_at > ?
                 AND instr(payload_json, ?) > 0
               ORDER BY seq DESC LIMIT 1""",
            (ctx.tenant_id, m["queued_at"], m["path"]),
        ).fetchone()
        now = utcnow()
        if newer is not None:
            error = (f"conflicto: el recurso {m['path']} fue modificado después de encolar "
                     f"(evento {newer['id']} · {newer['type']} · {newer['created_at']})")
            ctx.conn.execute(
                "UPDATE fnd_sync_mutations SET status = 'conflict', error = ? WHERE id = ?",
                (error, m["id"]),
            )
            conflicts += 1
            results.append({"id": m["id"], "status": "conflict", "error": error})
        else:
            ctx.conn.execute(
                "UPDATE fnd_sync_mutations SET status = 'applied', applied_at = ?, error = NULL "
                "WHERE id = ?",
                (now, m["id"]),
            )
            applied += 1
            results.append({"id": m["id"], "status": "applied", "applied_at": now})
            ctx.emit("sync", "sync.mutation_applied",
                     {"mutation_id": m["id"], "method": m["method"], "mutation_path": m["path"],
                      "device_id": device["id"]})

    ctx.audit("sync.apply", resource_type="device", resource_id=device["id"],
              payload={"applied": applied, "conflicts": conflicts})
    return {"processed": len(queued), "applied": applied, "conflicts": conflicts,
            "results": results,
            "pending_mutations": pending_mutations(ctx.conn, ctx.tenant_id, device["id"])}


@router.get("/mutations")
def list_mutations(
    status: str | None = None,  # noqa: A002 - nombre de query param del contrato
    device_id: str | None = None,
    ctx: SessionContext = Depends(require_session),
) -> dict[str, Any]:
    """Cola de mutaciones del tenant (filtro opcional ?status= y ?device_id=)."""
    sql = "SELECT * FROM fnd_sync_mutations WHERE tenant_id = ?"
    args: list[Any] = [ctx.tenant_id]
    if status:
        sql += " AND status = ?"
        args.append(status)
    if device_id:
        sql += " AND device_id = ?"
        args.append(device_id)
    sql += " ORDER BY queued_at DESC, rowid DESC LIMIT 200"
    rows = ctx.conn.execute(sql, args).fetchall()
    return {"mutations": rows_to_dicts(rows)}


@router.post("/reconcile")
def sync_reconcile(body: DeviceRef, ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Tras un full refresh (o apply), fija el cursor al máximo actual."""
    device = get_tenant_device(ctx.conn, ctx.tenant_id, body.device_id)
    max_seq = _max_event_seq(ctx.conn, ctx.tenant_id)
    now = utcnow()
    _upsert_state(ctx.conn, ctx.tenant_id, device["id"],
                  last_event_seq=max_seq, last_sync_at=now, mode="delta")
    pending = pending_mutations(ctx.conn, ctx.tenant_id, device["id"])
    ctx.audit("sync.reconcile", resource_type="device", resource_id=device["id"],
              payload={"last_event_seq": max_seq})
    ctx.emit("sync", "sync.reconciled", {"device_id": device["id"], "last_event_seq": max_seq})
    return {"device_id": device["id"], "last_event_seq": max_seq, "last_sync_at": now,
            "mode": "delta", "pending_mutations": pending}
