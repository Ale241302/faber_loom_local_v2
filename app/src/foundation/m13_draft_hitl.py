"""M13 — Draft HITL portado de Django (apps/drafts) a FastAPI/SQLite.

Adaptaciones local-first:

- Máquina de estados estricta y simplificada del plan:
  ``draft → pending_review → approved → sent`` (rechazo sólo desde
  pending_review; edición permitida en draft|pending_review y genera revisión).
  Los estados Django ``edited/expired/approved_pending_send`` se colapsan:
  la edición es una revisión (fnd_draft_revisions) y el bloqueo de policy se
  refleja como 409/422 en ``/send`` (no como estado intermedio persistente).
- Regla four-eyes del plan: el aprobador NO puede ser el creador del draft.
- ``D9Gate.pre_egress`` (M11) → ``policy_evaluate`` con import tolerante y
  comportamiento fail-closed (needs_approval) si M11 no está disponible.
- ``ChannelSender`` (envío real email/WhatsApp) queda fuera de alcance: al
  pasar el policy gate se marca ``sent`` + ``sent_at`` y se emite el evento
  ``drafts/sent`` para que un conector externo lo procese.
- ``EvidenceBundle`` se reduce a ``evidence_json`` embebido en el draft.
"""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .core import (
    SessionContext,
    new_id,
    register_schema,
    require_permission,
    require_session,
    rows_to_dicts,
    to_dict,
    utcnow,
)

try:  # M11 lo implementa otro módulo; fail-closed si no está.
    from .m11_policy_gate import evaluate as policy_evaluate
except Exception:  # pragma: no cover - depende del despliegue de M11
    def policy_evaluate(conn, tenant_id, action, context):
        return {
            "decision": "needs_approval",
            "reasons": ["policy gate unavailable (fail-closed)"],
            "policy_id": None,
        }

router = APIRouter(prefix="/drafts", tags=["foundation-m13-drafts"])

register_schema(
    """
CREATE TABLE IF NOT EXISTS fnd_hitl_drafts (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    source_item_id TEXT,
    channel TEXT NOT NULL DEFAULT 'email',
    recipient TEXT NOT NULL DEFAULT '',
    subject TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    evidence_json TEXT NOT NULL DEFAULT '{}',
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN (
        'draft','pending_review','approved','rejected','sent','failed'
    )),
    created_by TEXT NOT NULL,
    reviewed_by TEXT,
    review_note TEXT NOT NULL DEFAULT '',
    policy_decision_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    sent_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_fnd_hitl_drafts_tenant_status
    ON fnd_hitl_drafts(tenant_id, status, updated_at);

CREATE TABLE IF NOT EXISTS fnd_draft_revisions (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    draft_id TEXT NOT NULL REFERENCES fnd_hitl_drafts(id),
    body TEXT NOT NULL DEFAULT '',
    subject TEXT NOT NULL DEFAULT '',
    edited_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fnd_draft_revisions_draft
    ON fnd_draft_revisions(tenant_id, draft_id, created_at);
"""
)

EDITABLE_STATUSES = {"draft", "pending_review"}


def _require_any_drafts_permission(
    ctx: SessionContext = Depends(require_session),
) -> SessionContext:
    if not (ctx.has("drafts.create") or ctx.has("drafts.review") or ctx.has("drafts.send")):
        raise HTTPException(403, "Missing permission: drafts.*")
    return ctx


def _get_draft(conn, tenant_id: str, draft_id: str):
    row = conn.execute(
        "SELECT * FROM fnd_hitl_drafts WHERE tenant_id = ? AND id = ?",
        (tenant_id, draft_id),
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Draft not found")
    return row


def _revisions(conn, tenant_id: str, draft_id: str) -> list[dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            """SELECT * FROM fnd_draft_revisions
               WHERE tenant_id = ? AND draft_id = ? ORDER BY created_at ASC, id ASC""",
            (tenant_id, draft_id),
        ).fetchall()
    )


def _save_revision(ctx: SessionContext, draft) -> str:
    """Guarda el contenido *anterior* del draft como revisión (historial)."""
    rev_id = new_id("rev")
    ctx.conn.execute(
        """INSERT INTO fnd_draft_revisions (id, tenant_id, draft_id, body, subject, edited_by, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (rev_id, ctx.tenant_id, draft["id"], draft["body"], draft["subject"],
         ctx.user_id, utcnow()),
    )
    return rev_id


def _transition(ctx: SessionContext, draft, allowed_from: set[str], new_status: str,
                *, extra_sql: str = "", extra_params: tuple = ()) -> None:
    if draft["status"] not in allowed_from:
        raise HTTPException(
            409,
            f"Transición inválida: {draft['status']} → {new_status} "
            f"(permitido desde: {', '.join(sorted(allowed_from))})",
        )
    ctx.conn.execute(
        f"UPDATE fnd_hitl_drafts SET status = ?, updated_at = ?{extra_sql} "
        "WHERE tenant_id = ? AND id = ?",
        (new_status, utcnow(), *extra_params, ctx.tenant_id, draft["id"]),
    )


def _emit_transition(ctx: SessionContext, draft_id: str, event_type: str,
                     payload: dict[str, Any] | None = None) -> None:
    data = {"draft_id": draft_id, "actor_id": ctx.user_id}
    data.update(payload or {})
    ctx.audit(f"drafts.{event_type}", resource_type="draft", resource_id=draft_id,
              payload=payload or {})
    ctx.emit("drafts", event_type, data)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class DraftIn(BaseModel):
    channel: str = Field(default="email", max_length=32)
    recipient: str = Field(default="", max_length=255)
    subject: str = Field(default="", max_length=500)
    body: str = Field(default="", max_length=50000)
    evidence: dict[str, Any] = Field(default_factory=dict)
    source_item_id: str | None = None


class DraftPatch(BaseModel):
    subject: str | None = Field(default=None, max_length=500)
    body: str | None = Field(default=None, max_length=50000)
    recipient: str | None = Field(default=None, max_length=255)


class RejectIn(BaseModel):
    note: str = Field(default="", max_length=2000)


class SendIn(BaseModel):
    override_ack: bool = False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("", status_code=201)
def create_draft(
    payload: DraftIn,
    ctx: SessionContext = Depends(require_permission("drafts.create")),
) -> dict[str, Any]:
    draft_id = new_id("drf")
    now = utcnow()
    ctx.conn.execute(
        """INSERT INTO fnd_hitl_drafts
           (id, tenant_id, source_item_id, channel, recipient, subject, body,
            evidence_json, status, created_by, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?, ?, ?)""",
        (draft_id, ctx.tenant_id, payload.source_item_id, payload.channel,
         payload.recipient, payload.subject, payload.body,
         json.dumps(payload.evidence, ensure_ascii=False), ctx.user_id, now, now),
    )
    _emit_transition(ctx, draft_id, "created",
                     {"channel": payload.channel, "recipient": payload.recipient})
    return to_dict(_get_draft(ctx.conn, ctx.tenant_id, draft_id))  # type: ignore[return-value]


@router.get("")
def list_drafts(
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=100, ge=1, le=500),
    ctx: SessionContext = Depends(_require_any_drafts_permission),
) -> dict[str, Any]:
    query = "SELECT * FROM fnd_hitl_drafts WHERE tenant_id = ?"
    params: list[Any] = [ctx.tenant_id]
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    query += " ORDER BY updated_at DESC LIMIT ?"
    params.append(limit)
    return {"drafts": rows_to_dicts(ctx.conn.execute(query, params).fetchall())}


@router.get("/{draft_id}")
def get_draft(
    draft_id: str,
    ctx: SessionContext = Depends(_require_any_drafts_permission),
) -> dict[str, Any]:
    draft = to_dict(_get_draft(ctx.conn, ctx.tenant_id, draft_id))
    draft["revisions"] = _revisions(ctx.conn, ctx.tenant_id, draft_id)  # type: ignore[index]
    return draft  # type: ignore[return-value]


@router.patch("/{draft_id}")
def edit_draft(
    draft_id: str,
    payload: DraftPatch,
    ctx: SessionContext = Depends(_require_any_drafts_permission),
) -> dict[str, Any]:
    if not (ctx.has("drafts.create") or ctx.has("drafts.review")):
        raise HTTPException(403, "Missing permission: drafts.create or drafts.review")
    draft = _get_draft(ctx.conn, ctx.tenant_id, draft_id)
    if draft["status"] not in EDITABLE_STATUSES:
        raise HTTPException(409, f"Sólo se edita en draft|pending_review (actual: {draft['status']})")
    if payload.subject is None and payload.body is None and payload.recipient is None:
        raise HTTPException(422, "Nada que actualizar")
    rev_id = _save_revision(ctx, draft)
    ctx.conn.execute(
        """UPDATE fnd_hitl_drafts SET
             subject = COALESCE(?, subject),
             body = COALESCE(?, body),
             recipient = COALESCE(?, recipient),
             updated_at = ?
           WHERE tenant_id = ? AND id = ?""",
        (payload.subject, payload.body, payload.recipient, utcnow(), ctx.tenant_id, draft_id),
    )
    _emit_transition(ctx, draft_id, "edited", {"revision_id": rev_id})
    out = to_dict(_get_draft(ctx.conn, ctx.tenant_id, draft_id))
    out["revisions"] = _revisions(ctx.conn, ctx.tenant_id, draft_id)  # type: ignore[index]
    return out  # type: ignore[return-value]


@router.post("/{draft_id}/submit")
def submit_draft(
    draft_id: str,
    ctx: SessionContext = Depends(require_permission("drafts.create")),
) -> dict[str, Any]:
    draft = _get_draft(ctx.conn, ctx.tenant_id, draft_id)
    _transition(ctx, draft, {"draft"}, "pending_review")
    _emit_transition(ctx, draft_id, "submitted", {})
    return to_dict(_get_draft(ctx.conn, ctx.tenant_id, draft_id))  # type: ignore[return-value]


@router.post("/{draft_id}/approve")
def approve_draft(
    draft_id: str,
    ctx: SessionContext = Depends(require_permission("drafts.review")),
) -> dict[str, Any]:
    draft = _get_draft(ctx.conn, ctx.tenant_id, draft_id)
    if draft["created_by"] == ctx.user_id:
        raise HTTPException(
            403, "Regla four-eyes: el creador del draft no puede aprobarlo"
        )
    _transition(ctx, draft, {"pending_review"}, "approved",
                extra_sql=", reviewed_by = ?", extra_params=(ctx.user_id,))
    _emit_transition(ctx, draft_id, "approved", {"reviewed_by": ctx.user_id})
    return to_dict(_get_draft(ctx.conn, ctx.tenant_id, draft_id))  # type: ignore[return-value]


@router.post("/{draft_id}/reject")
def reject_draft(
    draft_id: str,
    payload: RejectIn,
    ctx: SessionContext = Depends(require_permission("drafts.review")),
) -> dict[str, Any]:
    draft = _get_draft(ctx.conn, ctx.tenant_id, draft_id)
    _transition(ctx, draft, {"pending_review"}, "rejected",
                extra_sql=", reviewed_by = ?, review_note = ?",
                extra_params=(ctx.user_id, payload.note))
    _emit_transition(ctx, draft_id, "rejected", {"note": payload.note})
    return to_dict(_get_draft(ctx.conn, ctx.tenant_id, draft_id))  # type: ignore[return-value]


@router.post("/{draft_id}/send")
def send_draft(
    draft_id: str,
    payload: SendIn | None = None,
    ctx: SessionContext = Depends(require_permission("drafts.send")),
) -> dict[str, Any]:
    payload = payload or SendIn()
    draft = _get_draft(ctx.conn, ctx.tenant_id, draft_id)
    if draft["status"] != "approved":
        raise HTTPException(409, f"Sólo se envía desde approved (actual: {draft['status']})")

    decision = policy_evaluate(
        ctx.conn, ctx.tenant_id, "draft.send",
        {
            "recipient": draft["recipient"],
            "subject": draft["subject"],
            "body": draft["body"],
            "channel": draft["channel"],
        },
    ) or {"decision": "needs_approval", "reasons": ["empty policy decision"], "policy_id": None}
    verdict = decision.get("decision", "needs_approval")
    decision_json = json.dumps(decision, ensure_ascii=False, default=str)

    if verdict == "deny":
        ctx.conn.execute(
            "UPDATE fnd_hitl_drafts SET policy_decision_json = ?, updated_at = ? "
            "WHERE tenant_id = ? AND id = ?",
            (decision_json, utcnow(), ctx.tenant_id, draft_id),
        )
        _emit_transition(ctx, draft_id, "send_denied",
                         {"reasons": decision.get("reasons"), "policy_id": decision.get("policy_id")})
        raise HTTPException(422, {
            "message": "Policy gate denegó el envío",
            "decision": "deny",
            "reasons": decision.get("reasons", []),
            "policy_id": decision.get("policy_id"),
        })

    if verdict == "needs_approval" and not payload.override_ack:
        ctx.conn.execute(
            "UPDATE fnd_hitl_drafts SET policy_decision_json = ?, updated_at = ? "
            "WHERE tenant_id = ? AND id = ?",
            (decision_json, utcnow(), ctx.tenant_id, draft_id),
        )
        _emit_transition(ctx, draft_id, "send_blocked",
                         {"reasons": decision.get("reasons"), "policy_id": decision.get("policy_id")})
        raise HTTPException(409, {
            "message": "Policy gate requiere aprobación explícita; reintenta con override_ack",
            "decision": "needs_approval",
            "reasons": decision.get("reasons", []),
            "policy_id": decision.get("policy_id"),
        })

    overridden = verdict == "needs_approval" and payload.override_ack
    now = utcnow()
    _transition(ctx, draft, {"approved"}, "sent",
                extra_sql=", sent_at = ?, policy_decision_json = ?",
                extra_params=(now, decision_json))
    if overridden:
        ctx.audit("drafts.send.override_ack", resource_type="draft", resource_id=draft_id,
                  payload={"reasons": decision.get("reasons"),
                           "policy_id": decision.get("policy_id")})
    # Envío real fuera de alcance: el evento queda en el outbox para conectores.
    _emit_transition(ctx, draft_id, "sent", {
        "channel": draft["channel"], "recipient": draft["recipient"],
        "policy_decision": verdict, "overridden": overridden,
    })
    return to_dict(_get_draft(ctx.conn, ctx.tenant_id, draft_id))  # type: ignore[return-value]
