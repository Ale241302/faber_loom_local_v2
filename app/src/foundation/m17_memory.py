"""M17 — Memory (Letta) portado a tabla local SQLite.

Adaptaciones local-first:

- Letta guardaba el contenido en un servicio externo y Django sólo la metadata
  (``MemoryItem``). Aquí el contenido vive en ``fnd_memory_blocks`` (key/value
  por namespace jerárquico ``tenant/agent/task``, como los namespaces Letta).
- Los layers working/episodic/persistent se mapean a ``kind``
  (fact|preference|instruction|episode) + ``importance``.
- Borrado = archivado (``archived_at``), nunca DELETE físico — conserva el
  espíritu de la memoria auditable con gate humano.
- Cada upsert preserva la versión anterior en ``fnd_memory_revisions``.
- ``/recall`` reemplaza el retrieval semántico de Letta con un ranking simple
  y determinista: solape de términos + importance + recencia (sin embeddings).
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .core import (
    SessionContext,
    new_id,
    register_schema,
    require_permission,
    rows_to_dicts,
    to_dict,
    utcnow,
)

router = APIRouter(prefix="/memory", tags=["foundation-m17-memory"])

register_schema(
    """
CREATE TABLE IF NOT EXISTS fnd_memory_blocks (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    user_id TEXT,
    namespace TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'fact' CHECK (kind IN ('fact','preference','instruction','episode')),
    importance REAL NOT NULL DEFAULT 0.5,
    source TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    archived_at TEXT,
    UNIQUE (tenant_id, namespace, key)
);
CREATE INDEX IF NOT EXISTS idx_fnd_memory_ns
    ON fnd_memory_blocks(tenant_id, namespace, archived_at);
CREATE INDEX IF NOT EXISTS idx_fnd_memory_user
    ON fnd_memory_blocks(tenant_id, user_id, archived_at);

CREATE TABLE IF NOT EXISTS fnd_memory_revisions (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    block_id TEXT NOT NULL REFERENCES fnd_memory_blocks(id),
    namespace TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'fact',
    importance REAL NOT NULL DEFAULT 0.5,
    edited_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fnd_memory_rev_block
    ON fnd_memory_revisions(tenant_id, block_id, created_at);
"""
)

KINDS = ("fact", "preference", "instruction", "episode")
_NS_RE = re.compile(r"^[A-Za-z0-9_\-.]+(/[A-Za-z0-9_\-.]+)*$")
_KEY_RE = re.compile(r"^[A-Za-z0-9_\-.]+$")


def _validate_ns_key(namespace: str, key: str) -> None:
    if not _NS_RE.match(namespace or ""):
        raise HTTPException(422, "Namespace inválido (usa segmentos a-z0-9_-. separados por '/')")
    if not _KEY_RE.match(key or ""):
        raise HTTPException(422, "Key inválida (a-z0-9_-. sin '/')")


class UpsertIn(BaseModel):
    value: str = Field(max_length=50000)
    kind: Literal["fact", "preference", "instruction", "episode"] = "fact"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    source: str = Field(default="", max_length=255)


class RecallIn(BaseModel):
    namespace: str = ""
    query: str = Field(default="", max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)


def _ns_filter(namespace: str | None) -> tuple[str, list[Any]]:
    """Filtro jerárquico: el namespace exacto o cualquier descendiente."""
    if not namespace:
        return "", []
    return " AND (namespace = ? OR namespace LIKE ?)", [namespace, namespace + "/%"]


@router.get("")
def list_blocks(
    namespace: str | None = Query(default=None),
    kind: str | None = Query(default=None),
    q: str | None = Query(default=None),
    include_archived: bool = Query(default=False),
    limit: int = Query(default=200, ge=1, le=1000),
    ctx: SessionContext = Depends(require_permission("memory.read")),
) -> dict[str, Any]:
    query = "SELECT * FROM fnd_memory_blocks WHERE tenant_id = ?"
    params: list[Any] = [ctx.tenant_id]
    if not include_archived:
        query += " AND archived_at IS NULL"
    ns_sql, ns_params = _ns_filter(namespace)
    query += ns_sql
    params.extend(ns_params)
    if kind:
        query += " AND kind = ?"
        params.append(kind)
    if q:
        query += " AND (key LIKE ? OR value LIKE ?)"
        like = f"%{q}%"
        params.extend([like, like])
    query += " ORDER BY namespace ASC, key ASC LIMIT ?"
    params.append(limit)
    return {"blocks": rows_to_dicts(ctx.conn.execute(query, params).fetchall())}


@router.get("/namespaces")
def list_namespaces(
    ctx: SessionContext = Depends(require_permission("memory.read")),
) -> dict[str, Any]:
    rows = ctx.conn.execute(
        """SELECT namespace, COUNT(*) AS n FROM fnd_memory_blocks
           WHERE tenant_id = ? AND archived_at IS NULL
           GROUP BY namespace ORDER BY namespace ASC""",
        (ctx.tenant_id,),
    ).fetchall()
    flat = [{"namespace": r["namespace"], "count": r["n"]} for r in rows]
    # Árbol con counts agregados por prefijo.
    tree: dict[str, dict[str, Any]] = {}
    for entry in flat:
        parts = entry["namespace"].split("/")
        for depth in range(1, len(parts) + 1):
            prefix = "/".join(parts[:depth])
            node = tree.setdefault(prefix, {"namespace": prefix, "depth": depth,
                                            "direct": 0, "total": 0})
            node["total"] += entry["count"]
            if depth == len(parts):
                node["direct"] += entry["count"]
    return {"namespaces": flat, "tree": sorted(tree.values(), key=lambda n: n["namespace"])}


@router.post("/recall")
def recall(
    payload: RecallIn,
    ctx: SessionContext = Depends(require_permission("memory.read")),
) -> dict[str, Any]:
    query = "SELECT * FROM fnd_memory_blocks WHERE tenant_id = ? AND archived_at IS NULL"
    params: list[Any] = [ctx.tenant_id]
    ns_sql, ns_params = _ns_filter(payload.namespace or None)
    query += ns_sql
    params.extend(ns_params)
    rows = rows_to_dicts(ctx.conn.execute(query, params).fetchall())

    terms = [t for t in re.split(r"\W+", payload.query.lower()) if len(t) >= 2]
    now = datetime.now()
    scored: list[dict[str, Any]] = []
    for block in rows:
        haystack = f"{block['namespace']} {block['key']} {block['value']}".lower()
        if terms:
            hits = sum(1 for t in terms if t in haystack)
            term_score = hits / len(terms)
        else:
            term_score = 0.0
        if terms and term_score == 0.0:
            continue  # con query, sólo devolvemos coincidencias
        try:
            updated = datetime.fromisoformat(block["updated_at"]).replace(tzinfo=None)
            age_days = max((now - updated).total_seconds() / 86400.0, 0.0)
        except Exception:
            age_days = 365.0
        recency = 1.0 / (1.0 + age_days / 7.0)  # 1.0 hoy → ~0.5 a la semana
        score = 0.6 * term_score + 0.25 * float(block.get("importance") or 0.0) + 0.15 * recency
        block["score"] = round(score, 4)
        block["matched_terms"] = [t for t in terms if t in haystack]
        scored.append(block)
    scored.sort(key=lambda b: b["score"], reverse=True)
    return {"results": scored[: payload.limit], "query": payload.query,
            "namespace": payload.namespace}


@router.put("/{namespace:path}/{key}")
def upsert_block(
    namespace: str,
    key: str,
    payload: UpsertIn,
    ctx: SessionContext = Depends(require_permission("memory.write")),
) -> dict[str, Any]:
    _validate_ns_key(namespace, key)
    now = utcnow()
    existing = ctx.conn.execute(
        "SELECT * FROM fnd_memory_blocks WHERE tenant_id = ? AND namespace = ? AND key = ?",
        (ctx.tenant_id, namespace, key),
    ).fetchone()
    if existing is not None:
        # Versión anterior → revisión.
        ctx.conn.execute(
            """INSERT INTO fnd_memory_revisions
               (id, tenant_id, block_id, namespace, key, value, kind, importance, edited_by, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (new_id("mrv"), ctx.tenant_id, existing["id"], namespace, key,
             existing["value"], existing["kind"], existing["importance"], ctx.user_id, now),
        )
        ctx.conn.execute(
            """UPDATE fnd_memory_blocks SET value = ?, kind = ?, importance = ?, source = ?,
               updated_at = ?, archived_at = NULL WHERE id = ?""",
            (payload.value, payload.kind, payload.importance, payload.source, now,
             existing["id"]),
        )
        block_id = existing["id"]
        action = "memory.block.updated"
    else:
        block_id = new_id("mem")
        ctx.conn.execute(
            """INSERT INTO fnd_memory_blocks
               (id, tenant_id, namespace, key, value, kind, importance, source, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (block_id, ctx.tenant_id, namespace, key, payload.value, payload.kind,
             payload.importance, payload.source, now, now),
        )
        action = "memory.block.created"
    ctx.audit(action, resource_type="memory_block", resource_id=block_id,
              payload={"namespace": namespace, "key": key, "kind": payload.kind})
    ctx.emit("memory", "upserted", {"block_id": block_id, "namespace": namespace,
                                    "key": key, "kind": payload.kind})
    row = ctx.conn.execute(
        "SELECT * FROM fnd_memory_blocks WHERE id = ?", (block_id,)
    ).fetchone()
    return to_dict(row)  # type: ignore[return-value]


@router.delete("/{namespace:path}/{key}")
def archive_block(
    namespace: str,
    key: str,
    ctx: SessionContext = Depends(require_permission("memory.manage")),
) -> dict[str, Any]:
    existing = ctx.conn.execute(
        """SELECT * FROM fnd_memory_blocks
           WHERE tenant_id = ? AND namespace = ? AND key = ? AND archived_at IS NULL""",
        (ctx.tenant_id, namespace, key),
    ).fetchone()
    if existing is None:
        raise HTTPException(404, "Memory block not found")
    ctx.conn.execute(
        "UPDATE fnd_memory_blocks SET archived_at = ?, updated_at = ? WHERE id = ?",
        (utcnow(), utcnow(), existing["id"]),
    )
    ctx.audit("memory.block.archived", resource_type="memory_block",
              resource_id=existing["id"], payload={"namespace": namespace, "key": key})
    ctx.emit("memory", "archived", {"block_id": existing["id"], "namespace": namespace,
                                    "key": key})
    return {"archived": True, "block_id": existing["id"]}
