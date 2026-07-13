"""Ambient detectors for E2-5.

Each detector receives a scoped Context and a DB connection and returns a list of
AmbientFinding objects. Detectors are read-only: they must not modify data.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import sqlite3

from .context import Context
from .db_adapter import transaction


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


def find_latest_backup_artifact(
    audits_dir: Path,
    data_dir: Path | None = None,
) -> tuple[Path, datetime] | None:
    """Return the most recent backup artifact.

    Accepts any of the following as evidence of a recent backup:
      - ``docs/audits/BACKUP_SMOKE_*.md`` (SQLite smoke reports)
      - ``data/backups/faberloom_postgres_*.sql.gz`` (Postgres dumps)
      - ``data/*.faberloom`` (SQLite archives)

    Used by the ``stale_backup_smoke`` detector and the ops freshness script.
    """

    candidates: list[Path] = []
    candidates.extend(audits_dir.glob("BACKUP_SMOKE_*.md"))
    if data_dir is not None:
        candidates.extend(data_dir.glob("*.faberloom"))
        candidates.extend(data_dir.glob("backups/faberloom_postgres_*.sql.gz"))

    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return None
    latest = candidates[0]
    mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
    return latest, mtime


# Backwards-compatible alias used by earlier E5-2 commits.
find_latest_backup_smoke_report = find_latest_backup_artifact


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
    with transaction(conn, ctx=ctx):
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

    with transaction(conn, ctx=ctx):
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

    with transaction(conn, ctx=ctx):
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


def detect_mail_without_draft(ctx: Context, conn: sqlite3.Connection) -> list[AmbientFinding]:
    """Detect unread mail_message rows without a draft for more than 4 hours."""

    workspace_id = ctx.require_scoped_workspace()
    since = _hours_ago(4)
    with transaction(conn, ctx=ctx):
        rows = conn.execute(
            """
            SELECT id, subject, sender, created_at
            FROM mail_message
            WHERE workspace_id = ? AND tenant_id = ? AND status = 'unread'
                  AND draft_id IS NULL AND created_at < ?
            ORDER BY created_at ASC
            LIMIT 20
            """,
            (workspace_id, ctx.tenant_id, since),
        ).fetchall()

        findings: list[AmbientFinding] = []
        for row in rows:
            subject = row["subject"] or "(sin asunto)"
            findings.append(
                AmbientFinding(
                    detector_slug="mail_without_draft",
                    target_type="mail_message",
                    target_id=row["id"],
                    severity="medium",
                    title=f"Correo sin draft: {subject[:80]}",
                    description=(
                        f"El correo de {row['sender'] or 'remitente desconocido'} lleva "
                        f"{_fmt_delta(row['created_at'])} sin borrador de respuesta."
                    ),
                    suggested_action="Generar un draft de respuesta y enviarlo a aprobación HITL.",
                    evidence_json={
                        "subject": subject,
                        "sender": row["sender"],
                        "received_at": row["created_at"],
                    },
                )
            )
    return findings


def detect_stale_sources(ctx: Context, conn: sqlite3.Connection) -> list[AmbientFinding]:
    """Detect KB sources past their declared validity or older than 180 days."""

    workspace_id = ctx.require_scoped_workspace()
    now = datetime.now(timezone.utc)
    age_cutoff = (now - timedelta(days=180)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    with transaction(conn, ctx=ctx):
        rows = conn.execute(
            """
            SELECT id, title, type, meta_json, created_at
            FROM kb_source
            WHERE workspace_id = ? AND tenant_id = ?
            ORDER BY created_at ASC
            LIMIT 200
            """,
            (workspace_id, ctx.tenant_id),
        ).fetchall()

        findings: list[AmbientFinding] = []
        today = now.date().isoformat()
        for row in rows:
            reason = None
            try:
                meta = json.loads(row["meta_json"] or "{}")
            except Exception:
                meta = {}
            vigente_hasta = str(meta.get("vigente_hasta") or meta.get("valid_until") or "").strip()
            if vigente_hasta and vigente_hasta < today:
                reason = f"vigencia declarada venció el {vigente_hasta}"
            elif (row["created_at"] or "") < age_cutoff:
                reason = f"cargada hace más de 180 días ({_fmt_delta(row['created_at'])})"
            if reason is None:
                continue
            findings.append(
                AmbientFinding(
                    detector_slug="stale_source",
                    target_type="kb_source",
                    target_id=row["id"],
                    severity="medium",
                    title=f"Fuente KB vencida: {row['title'][:80]}",
                    description=f"La fuente '{row['title']}' ({row['type']}) está potencialmente desactualizada: {reason}.",
                    suggested_action="Revisar la fuente, recargar datos vigentes o marcarla como retirada.",
                    evidence_json={
                        "title": row["title"],
                        "type": row["type"],
                        "created_at": row["created_at"],
                        "vigente_hasta": vigente_hasta or None,
                        "reason": reason,
                    },
                )
            )
    return findings


def detect_unreviewed_gold(ctx: Context, conn: sqlite3.Connection) -> list[AmbientFinding]:
    """Detect gold_candidate rows waiting for review for more than 48 hours."""

    workspace_id = ctx.require_scoped_workspace()
    since = _hours_ago(48)
    with transaction(conn, ctx=ctx):
        rows = conn.execute(
            """
            SELECT gc.id, gc.routine_id, gc.edit_pct, gc.created_at, r.name AS routine_name
            FROM gold_candidate gc
            LEFT JOIN routine r ON r.id = gc.routine_id
            WHERE gc.workspace_id = ? AND gc.approved = 0 AND gc.created_at < ?
            ORDER BY gc.created_at ASC
            LIMIT 20
            """,
            (workspace_id, since),
        ).fetchall()

        findings: list[AmbientFinding] = []
        for row in rows:
            routine_name = row["routine_name"] or "rutina desconocida"
            findings.append(
                AmbientFinding(
                    detector_slug="unreviewed_gold",
                    target_type="gold_candidate",
                    target_id=row["id"],
                    severity="low",
                    title=f"Gold candidate sin revisar: {routine_name}",
                    description=(
                        f"Un gold candidate de '{routine_name}' lleva {_fmt_delta(row['created_at'])} "
                        f"esperando revisión (edit_pct: {row['edit_pct']})."
                    ),
                    suggested_action="Revisar el candidate y aprobarlo o descartarlo (segundo gate aplica).",
                    evidence_json={
                        "routine_id": row["routine_id"],
                        "routine_name": routine_name,
                        "edit_pct": row["edit_pct"],
                        "created_at": row["created_at"],
                    },
                )
            )
    return findings


def detect_stale_backup_smoke(
    ctx: Context, conn: sqlite3.Connection
) -> list[AmbientFinding]:
    """Detect if the latest backup artifact is older than 24 hours.

    Accepts ``BACKUP_SMOKE_*.md`` reports (SQLite), ``*.faberloom`` archives,
    or Postgres dumps ``faberloom_postgres_*.sql.gz`` as evidence of a recent
    backup.  No finding is emitted when an artifact exists and is within the
    freshness threshold.
    """

    repo_root = Path(__file__).resolve().parents[2]
    audits_dir = repo_root / "docs" / "audits"
    # In the VPS container data lives under FABERLOOM_CONFIG_DIR (/data);
    # in local dev it is repo_root/data.
    data_dir = Path(os.environ.get("FABERLOOM_CONFIG_DIR", repo_root / "data"))
    threshold_hours = 24

    result = find_latest_backup_artifact(audits_dir, data_dir)
    if result is None:
        return [
            AmbientFinding(
                detector_slug="stale_backup_smoke",
                target_type="system",
                target_id="backup_smoke",
                severity="critical",
                title="No existe evidencia de backup reciente",
                description=(
                    f"No se encontró ningún artifact de backup en {audits_dir} "
                    f"ni en {data_dir}. El backup debe ejecutarse al menos cada "
                    f"{threshold_hours} horas."
                ),
                suggested_action=(
                    "Para SQLite: ejecutar python app/scripts/backup_restore_smoke.py. "
                    "Para Postgres: ejecutar app/scripts/backup_postgres.sh."
                ),
                evidence_json={
                    "audits_dir": str(audits_dir),
                    "data_dir": str(data_dir),
                    "threshold_hours": threshold_hours,
                    "latest_artifact": None,
                    "latest_mtime": None,
                    "age_hours": None,
                },
            )
        ]

    latest, mtime = result
    age = datetime.now(timezone.utc) - mtime
    age_hours = age.total_seconds() / 3600

    if age_hours <= threshold_hours:
        return []

    return [
        AmbientFinding(
            detector_slug="stale_backup_smoke",
            target_type="system",
            target_id="backup_smoke",
            severity="high",
            title="Backup desactualizado",
            description=(
                f"El último artifact de backup ({latest.name}) tiene "
                f"{age_hours:.1f} horas (umbral: {threshold_hours}h)."
            ),
            suggested_action=(
                "Reejecutar el script de backup correspondiente y verificar "
                "integridad del artifact más reciente."
            ),
            evidence_json={
                "latest_artifact": latest.name,
                "latest_artifact_path": str(latest),
                "latest_mtime": mtime.isoformat(),
                "age_hours": round(age_hours, 2),
                "threshold_hours": threshold_hours,
            },
        )
    ]


DETECTOR_REGISTRY: dict[str, Any] = {
    "failed_routine": detect_failed_routine,
    "stuck_hitl": detect_stuck_hitl,
    "budget_exhaustion": detect_budget_exhaustion,
    "mail_without_draft": detect_mail_without_draft,
    "stale_source": detect_stale_sources,
    "unreviewed_gold": detect_unreviewed_gold,
    "stale_backup_smoke": detect_stale_backup_smoke,
}

# E4-5: personal-memory detector is registered lazily to avoid a circular import
# with the memory module, which needs AmbientFinding for its return type.
from .living_agent.memory import detect_personal_memory_patterns  # noqa: E402

DETECTOR_REGISTRY["personal_memory"] = detect_personal_memory_patterns
