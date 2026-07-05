"""M11 Policy Gate D9 — gate fail-closed para acciones outbound.

Port de ``foundation_beta/backend/apps/policy`` (D9Gate) adaptado al modelo
local-first: en lugar de ceilings N0–N4 + DPA de Postgres, las políticas
viven en ``fnd_policies`` con reglas declarativas JSON y cada evaluación se
registra en ``fnd_policy_decisions``.

Reglas soportadas en ``rules_json`` (plan M11):

- ``actions``: lista de acciones a las que aplica la policy (vacío → todas).
- ``allow_domains`` / ``block_domains``: allowlist/blocklist de dominios de
  los destinatarios (``context.recipients``).
- ``max_recipients``: límite de destinatarios.
- ``blocked_patterns``: regex que bloquean el contenido (``context.content``).
- ``blocked_data_categories``: categorías de datos prohibidas
  (``context.data_categories``).
- ``require_hitl``: fuerza ``needs_approval`` (human in the loop).

Fail-closed: sin policies enabled aplicables, las acciones outbound
(``draft.send``, ``email.send``) devuelven ``needs_approval``; el resto
``allow``. Los módulos ops importan :func:`evaluate` para el gate de envío.
"""

from __future__ import annotations

import json
import re
import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from .core import (
    SessionContext,
    audit_log,
    get_conn,
    new_id,
    register_schema,
    require_permission,
    rows_to_dicts,
    to_dict,
    utcnow,
)

router = APIRouter(prefix="/policy", tags=["m11-policy-gate"])

register_schema(
    """
CREATE TABLE IF NOT EXISTS fnd_policies (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL DEFAULT 'outbound',
    rules_json TEXT NOT NULL DEFAULT '{}',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE (tenant_id, name)
);

CREATE TABLE IF NOT EXISTS fnd_policy_decisions (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    policy_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL DEFAULT '',
    resource_id TEXT NOT NULL DEFAULT '',
    decision TEXT NOT NULL,
    reasons_json TEXT NOT NULL DEFAULT '[]',
    context_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fnd_policy_dec_tenant ON fnd_policy_decisions(tenant_id, created_at);
"""
)

OUTBOUND_ACTIONS = {"draft.send", "email.send"}
DECISION_RANK = {"allow": 0, "needs_approval": 1, "deny": 2}


# ---------------------------------------------------------------------------
# Motor de evaluación (API pública para otros módulos)
# ---------------------------------------------------------------------------


def _domain(address: str) -> str:
    return address.rsplit("@", 1)[-1].strip().lower() if "@" in address else address.strip().lower()


def _eval_rules(rules: dict[str, Any], action: str, context: dict[str, Any]) -> tuple[str, list[str]]:
    """Evalúa las reglas de una policy → (decision, reasons)."""
    reasons: list[str] = []
    decision = "allow"

    recipients = [str(r) for r in context.get("recipients") or []]
    content = str(context.get("content") or "")
    categories = {str(c).lower() for c in context.get("data_categories") or []}

    block_domains = {str(d).lower() for d in rules.get("block_domains") or []}
    if block_domains:
        hit = sorted({_domain(r) for r in recipients} & block_domains)
        if hit:
            decision = "deny"
            reasons.append(f"dominio bloqueado: {', '.join(hit)}")

    allow_domains = {str(d).lower() for d in rules.get("allow_domains") or []}
    if allow_domains and recipients:
        outside = sorted({_domain(r) for r in recipients} - allow_domains)
        if outside:
            decision = "deny"
            reasons.append(f"dominio fuera de la allowlist: {', '.join(outside)}")

    max_recipients = rules.get("max_recipients")
    if isinstance(max_recipients, int) and len(recipients) > max_recipients:
        decision = "deny"
        reasons.append(f"destinatarios ({len(recipients)}) > max_recipients ({max_recipients})")

    for pattern in rules.get("blocked_patterns") or []:
        try:
            if content and re.search(str(pattern), content, re.IGNORECASE):
                decision = "deny"
                reasons.append(f"contenido coincide con patrón bloqueado: {pattern}")
        except re.error:
            # Regex inválida → fail-closed sobre esta regla.
            decision = "deny"
            reasons.append(f"patrón bloqueado inválido (fail-closed): {pattern}")

    blocked_categories = {str(c).lower() for c in rules.get("blocked_data_categories") or []}
    hit_categories = sorted(blocked_categories & categories)
    if hit_categories:
        decision = "deny"
        reasons.append(f"categoría de datos bloqueada: {', '.join(hit_categories)}")

    if decision == "allow" and rules.get("require_hitl"):
        decision = "needs_approval"
        reasons.append("require_hitl: aprobación humana requerida")

    return decision, reasons


def evaluate(
    conn: sqlite3.Connection,
    tenant_id: str,
    action: str,
    context: dict[str, Any] | None = None,
    *,
    actor_id: str | None = None,
    actor_email: str = "",
    record: bool = True,
) -> dict[str, Any]:
    """Evalúa ``action`` contra las policies enabled del tenant (fail-closed).

    Devuelve ``{"decision": allow|deny|needs_approval, "reasons": [...],
    "policy_id": str|None}``. Los módulos ops la usan como gate de envío
    outbound antes de cualquier egreso.
    """
    context = context or {}
    rows = conn.execute(
        "SELECT * FROM fnd_policies WHERE tenant_id = ? AND enabled = 1 ORDER BY created_at",
        (tenant_id,),
    ).fetchall()

    applicable: list[tuple[sqlite3.Row, dict[str, Any]]] = []
    for row in rows:
        try:
            rules = json.loads(row["rules_json"] or "{}")
        except Exception:
            rules = None
        if rules is None:
            # Rules corruptas → fail-closed: la policy aplica y deniega.
            applicable.append((row, {"blocked_patterns": ["(?s)."]}))
            continue
        actions = [str(a) for a in rules.get("actions") or []]
        if not actions or action in actions:
            applicable.append((row, rules))

    if not applicable:
        if action in OUTBOUND_ACTIONS:
            decision, reasons, policy_id = (
                "needs_approval",
                ["fail-closed: sin policies aplicables para acción outbound"],
                None,
            )
        else:
            decision, reasons, policy_id = (
                "allow",
                ["sin policies aplicables (acción no outbound)"],
                None,
            )
    else:
        decision, reasons, policy_id = "allow", [], None
        for row, rules in applicable:
            p_decision, p_reasons = _eval_rules(rules, action, context)
            if DECISION_RANK[p_decision] > DECISION_RANK[decision]:
                decision, policy_id = p_decision, row["id"]
            if p_reasons:
                reasons.extend(f"[{row['name']}] {r}" for r in p_reasons)
        if decision == "allow":
            policy_id = applicable[0][0]["id"]
            reasons.append("permitido por las policies aplicables")

    result = {"decision": decision, "reasons": reasons, "policy_id": policy_id}

    if record:
        conn.execute(
            """INSERT INTO fnd_policy_decisions
               (id, tenant_id, policy_id, action, resource_type, resource_id,
                decision, reasons_json, context_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                new_id("pdc"),
                tenant_id,
                policy_id,
                action,
                str(context.get("resource_type") or ""),
                str(context.get("resource_id") or ""),
                decision,
                json.dumps(reasons, ensure_ascii=False),
                json.dumps(context, ensure_ascii=False, default=str),
                utcnow(),
            ),
        )
        if decision in ("deny", "needs_approval"):
            audit_log(
                conn, tenant_id, "policy.gate.decision",
                actor_id=actor_id, actor_email=actor_email,
                resource_type="policy", resource_id=policy_id or "",
                payload={"action": action, "decision": decision, "reasons": reasons},
            )
    return result


# ---------------------------------------------------------------------------
# Bodies
# ---------------------------------------------------------------------------


class PolicyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    kind: str = "outbound"
    rules: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class PolicyPatch(BaseModel):
    name: str | None = None
    kind: str | None = None
    rules: dict[str, Any] | None = None
    enabled: bool | None = None


class EvaluateBody(BaseModel):
    action: str
    context: dict[str, Any] = Field(default_factory=dict)


def _validate_rules(rules: dict[str, Any]) -> None:
    for pattern in rules.get("blocked_patterns") or []:
        try:
            re.compile(str(pattern))
        except re.error as exc:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, f"Regex inválida en blocked_patterns: {pattern} ({exc})"
            )
    if "max_recipients" in rules and rules["max_recipients"] is not None:
        if not isinstance(rules["max_recipients"], int) or rules["max_recipients"] < 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "max_recipients debe ser entero >= 0")


def _get_policy(conn: sqlite3.Connection, tenant_id: str, policy_id: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM fnd_policies WHERE id = ? AND tenant_id = ?", (policy_id, tenant_id)
    ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Policy no encontrada")
    return row


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/policies")
def list_policies(
    ctx: SessionContext = Depends(require_permission("policy.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    rows = conn.execute(
        "SELECT * FROM fnd_policies WHERE tenant_id = ? ORDER BY created_at", (ctx.tenant_id,)
    ).fetchall()
    return {"policies": rows_to_dicts(rows)}


@router.post("/policies", status_code=status.HTTP_201_CREATED)
def create_policy(
    body: PolicyCreate,
    ctx: SessionContext = Depends(require_permission("policy.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    _validate_rules(body.rules)
    exists = conn.execute(
        "SELECT id FROM fnd_policies WHERE tenant_id = ? AND name = ?",
        (ctx.tenant_id, body.name),
    ).fetchone()
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una policy con ese nombre")
    policy_id = new_id("pol")
    now = utcnow()
    conn.execute(
        """INSERT INTO fnd_policies (id, tenant_id, name, kind, rules_json, enabled, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (policy_id, ctx.tenant_id, body.name, body.kind,
         json.dumps(body.rules, ensure_ascii=False), int(body.enabled), now, now),
    )
    ctx.audit("policy.created", resource_type="policy", resource_id=policy_id,
              payload={"name": body.name, "kind": body.kind, "enabled": body.enabled})
    ctx.emit("policy", "created", {"policy_id": policy_id, "name": body.name})
    return to_dict(_get_policy(conn, ctx.tenant_id, policy_id)) or {}


@router.patch("/policies/{policy_id}")
def patch_policy(
    policy_id: str,
    body: PolicyPatch,
    ctx: SessionContext = Depends(require_permission("policy.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    _get_policy(conn, ctx.tenant_id, policy_id)
    changes: dict[str, Any] = {}
    if body.rules is not None:
        _validate_rules(body.rules)
        conn.execute(
            "UPDATE fnd_policies SET rules_json = ? WHERE id = ?",
            (json.dumps(body.rules, ensure_ascii=False), policy_id),
        )
        changes["rules"] = body.rules
    if body.name is not None:
        conn.execute("UPDATE fnd_policies SET name = ? WHERE id = ?", (body.name, policy_id))
        changes["name"] = body.name
    if body.kind is not None:
        conn.execute("UPDATE fnd_policies SET kind = ? WHERE id = ?", (body.kind, policy_id))
        changes["kind"] = body.kind
    if body.enabled is not None:
        conn.execute(
            "UPDATE fnd_policies SET enabled = ? WHERE id = ?", (int(body.enabled), policy_id)
        )
        changes["enabled"] = body.enabled
    if changes:
        conn.execute("UPDATE fnd_policies SET updated_at = ? WHERE id = ?", (utcnow(), policy_id))
        ctx.audit("policy.updated", resource_type="policy", resource_id=policy_id,
                  payload={"changes": sorted(changes)})
        ctx.emit("policy", "updated", {"policy_id": policy_id, "changes": sorted(changes)})
    return to_dict(_get_policy(conn, ctx.tenant_id, policy_id)) or {}


@router.delete("/policies/{policy_id}")
def delete_policy(
    policy_id: str,
    ctx: SessionContext = Depends(require_permission("policy.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    """Las policies no se borran (trazabilidad): DELETE = disable."""
    policy = _get_policy(conn, ctx.tenant_id, policy_id)
    conn.execute(
        "UPDATE fnd_policies SET enabled = 0, updated_at = ? WHERE id = ?",
        (utcnow(), policy_id),
    )
    ctx.audit("policy.disabled", resource_type="policy", resource_id=policy_id,
              payload={"name": policy["name"]})
    ctx.emit("policy", "disabled", {"policy_id": policy_id, "name": policy["name"]})
    return to_dict(_get_policy(conn, ctx.tenant_id, policy_id)) or {}


@router.post("/evaluate")
def evaluate_endpoint(
    body: EvaluateBody,
    ctx: SessionContext = Depends(require_permission("policy.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    """Dry-run del gate: evalúa y registra la decisión sin ejecutar nada."""
    return evaluate(
        conn, ctx.tenant_id, body.action, body.context,
        actor_id=ctx.user_id, actor_email=ctx.email,
    )


@router.get("/decisions")
def list_decisions(
    action: str | None = Query(default=None),
    decision: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    ctx: SessionContext = Depends(require_permission("policy.manage")),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    query = "SELECT * FROM fnd_policy_decisions WHERE tenant_id = ?"
    params: list[Any] = [ctx.tenant_id]
    if action:
        query += " AND action = ?"
        params.append(action)
    if decision:
        query += " AND decision = ?"
        params.append(decision)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()
    return {"decisions": rows_to_dicts(rows)}
