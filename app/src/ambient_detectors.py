"""Ambient detectors for E2-5.

Each detector receives a scoped Context and a DB connection and returns a list of
AmbientFinding objects. Detectors are read-only: they must not modify data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import sqlite3

from .context import Context


SEVERITIES = ("low", "medium", "high", "critical")


@dataclass(frozen=True, slots=True)
class AmbientFinding:
    detector_slug: str
    target_type: str
    target_id: str
    severity: str
    title: str
    description: str
    suggested_action: str
    evidence_json: dict[str, Any]

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"Invalid severity: {self.severity}")


def _hours_ago(hours: int) -> str:
    dt = datetime.now(timezone.utc) - timedelta(hours=hours)
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _fmt_delta(iso_dt: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - dt
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    except Exception:  # pragma: no cover
        return "?"


def detect_failed_routine(ctx: Context, conn: sqlite3.Connection) -> list[AmbientFinding]:
    """Detect routine_run rows with status=failed in the last 24 hours."""

    workspace_id = ctx.require_scoped_workspace()
    since = _hours_ago(24)
    rows = conn.execute(
        """
        SELECT id, routine_id, task_type, status, output_json, evidence_json, created_at
        FROM routine_run
        WHERE workspace_id = ? AND tenant_id = ? AND status = 'failed'
              AND created_at > ?
        ORDER BY created_at DESC
        """,
        (workspace_id, ctx.tenant_id, since),
    ).fetchall()

    findings: list[AmbientFinding] = []
    for row in rows:
        routine_name = "unknown"
        routine_row = conn.execute(
            "SELECT name FROM routine WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (row["routine_id"], workspace_id, ctx.tenant_id),
        ).fetchone()
        if routine_row is not None:
            routine_name = routine_row["name"]

        output = row["output_json"] or "{}"
        try:
            output_data = json.loads(output)
        except Exception:
            output_data = {}
        error_detail = output_data.get("error") or "sin detalle"

        findings.append(
            AmbientFinding(
                detector_slug="failed_routine",
                target_type="routine_run",
                target_id=row["id"],
                severity="high",
                title=f"Rutina fallida: {routine_name}",
                description=(
                    f"La rutina '{routine_name}' falló hace {_fmt_delta(row['created_at'])}. "
                    f"Error: {error_detail}."
                ),
                suggested_action="Revisar el error en la rutina y reintentar o corregir el input.",
                evidence_json={
                    "routine_id": row["routine_id"],
                    "routine_name": routine_name,
                    "task_type": row["task_type"],
                    "status": row["status"],
                    "output_json": output_data,
                    "failed_at": row["created_at"],
                },
            )
        )
    return findings


def detect_stuck_hitl(ctx: Context, conn: sqlite3.Connection) -> list[AmbientFinding]:
    """Detect routine_run/draft items waiting for HITL for more than 4 hours."""

    workspace_id = ctx.require_scoped_workspace()
    since = _hours_ago(4)
    findings: list[AmbientFinding] = []

    # routine_run stuck
    run_rows = conn.execute(
        """
        SELECT id, task_type, urgency, reason, created_at
        FROM routine_run
        WHERE workspace_id = ? AND tenant_id = ?
              AND status = 'requires_hitl'
              AND created_at < ?
        ORDER BY created_at ASC
        """,
        (workspace_id, ctx.tenant_id, since),
    ).fetchall()
    for row in run_rows:
        findings.append(
            AmbientFinding(
                detector_slug="stuck_hitl",
                target_type="routine_run",
                target_id=row["id"],
                severity="medium",
                title="Pendiente HITL estancado",
                description=(
                    f"Un run requiere aprobación HITL hace {_fmt_delta(row['created_at'])}. "
                    f"Razón: {row['reason'] or 'no especificada'}."
                ),
                suggested_action="Revisar y aprobar/rechazar el run en WorkLoom.",
                evidence_json={
                    "entity": "routine_run",
                    "urgency": row["urgency"],
                    "reason": row["reason"],
                    "created_at": row["created_at"],
                },
            )
        )

    # draft stuck
    draft_rows = conn.execute(
        """
        SELECT id, subject, status, created_at
        FROM draft
        WHERE workspace_id = ? AND tenant_id = ?
              AND status IN ('draft', 'pending_approval')
              AND created_at < ?
        ORDER BY created_at ASC
        """,
        (workspace_id, ctx.tenant_id, since),
    ).fetchall()
    for row in draft_rows:
        title = row["subject"] or "Draft sin asunto"
        findings.append(
            AmbientFinding(
                detector_slug="stuck_hitl",
                target_type="draft",
                target_id=row["id"],
                severity="medium",
                title=f"Draft estancado: {title}",
                description=(
                    f"Un draft lleva {_fmt_delta(row['created_at'])} sin aprobación."
                ),
                suggested_action="Revisar, editar o aprobar el draft.",
                evidence_json={
                    "entity": "draft",
                    "subject": title,
                    "status": row["status"],
                    "created_at": row["created_at"],
                },
            )
        )

    return findings


def detect_budget_exhaustion(ctx: Context, conn: sqlite3.Connection) -> list[AmbientFinding]:
    """Detect workspace or tenant daily budget close to exhaustion."""

    workspace_id = ctx.require_scoped_workspace()
    findings: list[AmbientFinding] = []

    # Workspace budget
    policy_row = conn.execute(
        """
        SELECT budget_cap_usd FROM workspace_routing_policy
        WHERE workspace_id = ? AND tenant_id = ?
        """,
        (workspace_id, ctx.tenant_id),
    ).fetchone()

    if policy_row is not None:
        budget = float(policy_row["budget_cap_usd"] or 0.0)
        if budget > 0:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            spent_row = conn.execute(
                """
                SELECT COALESCE(SUM(cost_total_usd), 0) AS spent
                FROM usage_record
                WHERE workspace_id = ? AND tenant_id = ? AND date(created_at) = ?
                """,
                (workspace_id, ctx.tenant_id, today),
            ).fetchone()
            spent = float(spent_row["spent"] or 0.0)
            pct = (spent / budget) * 100 if budget else 0.0
            if pct >= 90.0:
                severity = "critical" if pct >= 100.0 else "high"
                findings.append(
                    AmbientFinding(
                        detector_slug="budget_exhaustion",
                        target_type="workspace_routing_policy",
                        target_id=workspace_id,
                        severity=severity,
                        title=f"Budget de routing al {pct:.0f}%",
                        description=(
                            f"El workspace ha consumido ${spent:.4f} de ${budget:.4f} "
                            f"({pct:.1f}%) del budget diario."
                        ),
                        suggested_action="Pausar uso de modelos cloud o aumentar el budget.",
                        evidence_json={
                            "scope": "workspace",
                            "budget_usd": budget,
                            "spent_usd": spent,
                            "pct_used": round(pct, 2),
                            "date": today,
                        },
                    )
                )

    # Tenant-level budget (ambient config budget_pct_of_router_daily is separate;
    # here we warn when total tenant usage exceeds 90% of sum of workspace budgets).
    tenant_budget_row = conn.execute(
        """
        SELECT COALESCE(SUM(budget_cap_usd), 0) AS total_budget
        FROM workspace_routing_policy
        WHERE tenant_id = ?
        """,
        (ctx.tenant_id,),
    ).fetchone()
    total_budget = float(tenant_budget_row["total_budget"] or 0.0)
    if total_budget > 0:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        tenant_spent_row = conn.execute(
            """
            SELECT COALESCE(SUM(cost_total_usd), 0) AS spent
            FROM usage_record
            WHERE tenant_id = ? AND date(created_at) = ?
            """,
            (ctx.tenant_id, today),
        ).fetchone()
        tenant_spent = float(tenant_spent_row["spent"] or 0.0)
        tenant_pct = (tenant_spent / total_budget) * 100
        if tenant_pct >= 90.0:
            severity = "critical" if tenant_pct >= 100.0 else "high"
            findings.append(
                AmbientFinding(
                    detector_slug="budget_exhaustion",
                    target_type="tenant",
                    target_id=ctx.tenant_id,
                    severity=severity,
                    title=f"Budget del tenant al {tenant_pct:.0f}%",
                    description=(
                        f"El tenant ha consumido ${tenant_spent:.4f} de ${total_budget:.4f} "
                        f"({tenant_pct:.1f}%) del budget agregado diario."
                    ),
                    suggested_action="Revisar consumo por workspace y ajustar presupuestos.",
                    evidence_json={
                        "scope": "tenant",
                        "budget_usd": total_budget,
                        "spent_usd": tenant_spent,
                        "pct_used": round(tenant_pct, 2),
                        "date": today,
                    },
                )
            )

    return findings


DETECTOR_REGISTRY: dict[str, Any] = {
    "failed_routine": detect_failed_routine,
    "stuck_hitl": detect_stuck_hitl,
    "budget_exhaustion": detect_budget_exhaustion,
}
