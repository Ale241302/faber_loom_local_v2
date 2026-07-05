"""M14 — Outcome Ledger portado de Django (apps/outcomes + apps/learning).

Adaptaciones local-first:

- ``OutcomeEntry`` + ``OutcomeLedgerEntry`` se fusionan en una sola tabla
  append-only ``fnd_outcomes`` (kind: draft|classification|task) — sin UPDATE
  ni DELETE expuestos (ledger inmutable, igual que en Django donde sólo hay
  ``objects.create``).
- Gold samples y su flujo de promoción (Curator + segundo aprobador) quedan
  fuera del alcance operativo Beta; las señales de aprendizaje se derivan en
  ``/insights`` (top motivos de rechazo + tendencia semanal, en el espíritu del
  Learning Thermometer que contaba aprobaciones por agente).
- Métricas de ``/stats``: tasas de aceptación/edición/rechazo de drafts y
  avg score, equivalentes a lo que alimentaba el thermometer.
"""

from __future__ import annotations

import json
from collections import Counter
from typing import Any, Literal

from fastapi import APIRouter, Depends, Query
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

router = APIRouter(prefix="/outcomes", tags=["foundation-m14-outcomes"])

register_schema(
    """
CREATE TABLE IF NOT EXISTS fnd_outcomes (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('draft','classification','task')),
    ref_id TEXT NOT NULL DEFAULT '',
    outcome TEXT NOT NULL CHECK (outcome IN (
        'accepted','edited','rejected','won','lost','neutral'
    )),
    score REAL,
    feedback TEXT NOT NULL DEFAULT '',
    meta_json TEXT NOT NULL DEFAULT '{}',
    actor_id TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fnd_outcomes_tenant
    ON fnd_outcomes(tenant_id, kind, outcome, created_at);
"""
)

KINDS = ("draft", "classification", "task")
OUTCOMES = ("accepted", "edited", "rejected", "won", "lost", "neutral")


class OutcomeIn(BaseModel):
    kind: Literal["draft", "classification", "task"]
    ref_id: str = Field(default="", max_length=64)
    outcome: Literal["accepted", "edited", "rejected", "won", "lost", "neutral"]
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    feedback: str = Field(default="", max_length=4000)
    meta: dict[str, Any] = Field(default_factory=dict)


@router.post("", status_code=201)
def record_outcome(
    payload: OutcomeIn,
    ctx: SessionContext = Depends(require_permission("outcomes.write")),
) -> dict[str, Any]:
    outcome_id = new_id("out")
    ctx.conn.execute(
        """INSERT INTO fnd_outcomes
           (id, tenant_id, kind, ref_id, outcome, score, feedback, meta_json, actor_id, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (outcome_id, ctx.tenant_id, payload.kind, payload.ref_id, payload.outcome,
         payload.score, payload.feedback, json.dumps(payload.meta, ensure_ascii=False),
         ctx.user_id, utcnow()),
    )
    ctx.audit("outcomes.recorded", resource_type="outcome", resource_id=outcome_id,
              payload={"kind": payload.kind, "ref_id": payload.ref_id,
                       "outcome": payload.outcome, "score": payload.score})
    ctx.emit("outcomes", "recorded", {
        "outcome_id": outcome_id, "kind": payload.kind,
        "ref_id": payload.ref_id, "outcome": payload.outcome,
    })
    row = ctx.conn.execute(
        "SELECT * FROM fnd_outcomes WHERE tenant_id = ? AND id = ?",
        (ctx.tenant_id, outcome_id),
    ).fetchone()
    return to_dict(row)  # type: ignore[return-value]


@router.get("")
def list_outcomes(
    kind: str | None = Query(default=None),
    outcome: str | None = Query(default=None),
    ref_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    ctx: SessionContext = Depends(require_permission("outcomes.read")),
) -> dict[str, Any]:
    query = "SELECT * FROM fnd_outcomes WHERE tenant_id = ?"
    params: list[Any] = [ctx.tenant_id]
    if kind:
        query += " AND kind = ?"
        params.append(kind)
    if outcome:
        query += " AND outcome = ?"
        params.append(outcome)
    if ref_id:
        query += " AND ref_id = ?"
        params.append(ref_id)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    return {"outcomes": rows_to_dicts(ctx.conn.execute(query, params).fetchall())}


@router.get("/stats")
def outcome_stats(
    ctx: SessionContext = Depends(require_permission("outcomes.read")),
) -> dict[str, Any]:
    rows = ctx.conn.execute(
        """SELECT kind, outcome, COUNT(*) AS n, AVG(score) AS avg_score
           FROM fnd_outcomes WHERE tenant_id = ? GROUP BY kind, outcome""",
        (ctx.tenant_id,),
    ).fetchall()
    by_kind: dict[str, dict[str, int]] = {}
    total = 0
    for row in rows:
        by_kind.setdefault(row["kind"], {})[row["outcome"]] = row["n"]
        total += row["n"]

    def _rate(kind: str, numerator_keys: tuple[str, ...],
              denominator_keys: tuple[str, ...]) -> float | None:
        counts = by_kind.get(kind, {})
        num = sum(counts.get(k, 0) for k in numerator_keys)
        den = sum(counts.get(k, 0) for k in denominator_keys)
        return round(num / den, 4) if den else None

    avg_row = ctx.conn.execute(
        "SELECT AVG(score) AS avg_score, COUNT(score) AS scored FROM fnd_outcomes WHERE tenant_id = ?",
        (ctx.tenant_id,),
    ).fetchone()

    decision_keys = ("accepted", "edited", "rejected")
    return {
        "total": total,
        "by_kind": by_kind,
        "rates": {
            "draft_acceptance_rate": _rate("draft", ("accepted",), decision_keys),
            "draft_edit_rate": _rate("draft", ("edited",), decision_keys),
            "draft_rejection_rate": _rate("draft", ("rejected",), decision_keys),
            "classification_acceptance_rate": _rate("classification", ("accepted",), decision_keys),
            "win_rate": _rate("draft", ("won",), ("won", "lost")),
        },
        "avg_score": round(avg_row["avg_score"], 4) if avg_row["avg_score"] is not None else None,
        "scored_count": avg_row["scored"],
    }


@router.get("/insights")
def outcome_insights(
    ctx: SessionContext = Depends(require_permission("outcomes.read")),
) -> dict[str, Any]:
    # Top motivos de rechazo (feedback textual normalizado).
    rejected = ctx.conn.execute(
        """SELECT feedback FROM fnd_outcomes
           WHERE tenant_id = ? AND outcome = 'rejected' AND feedback != ''""",
        (ctx.tenant_id,),
    ).fetchall()
    reasons = Counter(row["feedback"].strip().lower() for row in rejected)
    top_rejection_reasons = [
        {"reason": reason, "count": count} for reason, count in reasons.most_common(5)
    ]

    # Tendencia semanal (ISO year-week) de las últimas 12 semanas con datos.
    weekly_rows = ctx.conn.execute(
        """SELECT strftime('%Y-W%W', created_at) AS week, outcome, COUNT(*) AS n
           FROM fnd_outcomes WHERE tenant_id = ?
           GROUP BY week, outcome ORDER BY week DESC LIMIT 200""",
        (ctx.tenant_id,),
    ).fetchall()
    weekly: dict[str, dict[str, int]] = {}
    for row in weekly_rows:
        weekly.setdefault(row["week"], {})[row["outcome"]] = row["n"]
    weeks_sorted = sorted(weekly.keys(), reverse=True)[:12]
    weekly_trend = []
    for week in sorted(weeks_sorted):
        counts = weekly[week]
        decided = sum(counts.get(k, 0) for k in ("accepted", "edited", "rejected"))
        weekly_trend.append({
            "week": week,
            "counts": counts,
            "total": sum(counts.values()),
            "acceptance_rate": round(counts.get("accepted", 0) / decided, 4) if decided else None,
        })

    signals: list[str] = []
    if top_rejection_reasons:
        signals.append(
            f"Motivo de rechazo más frecuente: “{top_rejection_reasons[0]['reason']}” "
            f"({top_rejection_reasons[0]['count']}x)"
        )
    if len(weekly_trend) >= 2:
        prev, last = weekly_trend[-2], weekly_trend[-1]
        if prev["acceptance_rate"] is not None and last["acceptance_rate"] is not None:
            delta = round(last["acceptance_rate"] - prev["acceptance_rate"], 4)
            direction = "mejoró" if delta > 0 else ("empeoró" if delta < 0 else "se mantuvo")
            signals.append(
                f"La tasa de aceptación {direction} vs. la semana anterior ({delta:+.2%})"
            )

    return {
        "top_rejection_reasons": top_rejection_reasons,
        "weekly_trend": weekly_trend,
        "signals": signals,
    }
