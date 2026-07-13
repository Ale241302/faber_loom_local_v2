#!/usr/bin/env python3
"""E5-6: instrumented soak report for a design partner tenant.

Generates a weekly, read-only soak report with rolled-up metrics only:
health, runs, HITL decisions, cost, incidents, and contamination canary.
No workspace content (emails, KB chunks, PDF bodies, etc.) is ever included.

Usage:
    python app/scripts/soak_report.py \
        --tenant-id tnt_xxx \
        --week 1 \
        --db-path /data/faberloom.sqlite3 \
        --foundation-db /data/foundation.sqlite3 \
        --out docs/audits

Exit code: 0 = report generated, canary clean; 1 = canary failure or missing tenant.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from app.src.context import SYSTEM_WORKSPACE_ID, Context  # noqa: E402
from app.src.db import summarize_tenant_usage_cost, utc_now  # noqa: E402
from app.src.health_dashboard import _compute_tenant_health  # noqa: E402


CANARY_SCRIPT = Path(__file__).parent / "check_canary_isolation.py"


def _week_bounds(week: int, now: datetime) -> tuple[str, str]:
    """Return (since, until) ISO timestamps for soak week ``week`` (1..4)."""

    if week < 1 or week > 4:
        raise ValueError("week must be between 1 and 4")
    until = now - timedelta(days=(week - 1) * 7)
    since = now - timedelta(days=week * 7)
    return since.isoformat(), until.isoformat()


def _count_weekly_runs(conn: sqlite3.Connection, tenant_id: str, since: str, until: str) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT status, COUNT(*) AS n
        FROM routine_run
        WHERE tenant_id = ? AND created_at >= ? AND created_at < ?
        GROUP BY status
        """,
        (tenant_id, since, until),
    ).fetchall()
    counts = {"total": 0, "succeeded": 0, "failed": 0, "requires_hitl": 0}
    for row in rows:
        n = int(row["n"])
        counts["total"] += n
        status = str(row["status"])
        if status in counts:
            counts[status] += n
    return counts


def _count_hitl_decisions(conn: sqlite3.Connection, tenant_id: str, since: str, until: str) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT status, COUNT(*) AS n
        FROM draft
        WHERE tenant_id = ? AND status IN ('approved', 'rejected')
          AND updated_at >= ? AND updated_at < ?
        GROUP BY status
        """,
        (tenant_id, since, until),
    ).fetchall()
    return {
        "approved": sum(int(r["n"]) for r in rows if r["status"] == "approved"),
        "rejected": sum(int(r["n"]) for r in rows if r["status"] == "rejected"),
    }


def _count_incidents(conn: sqlite3.Connection, tenant_id: str, since: str, until: str) -> dict[str, int]:
    rows = conn.execute(
        """
        SELECT action, COUNT(*) AS n
        FROM audit_log
        WHERE tenant_id = ? AND created_at >= ? AND created_at < ?
          AND (
              action LIKE '%degrad%'
              OR action LIKE '%incident%'
              OR action LIKE '%P0%'
              OR action LIKE '%kill_switch%'
              OR action LIKE '%routing.degraded%'
          )
        GROUP BY action
        """,
        (tenant_id, since, until),
    ).fetchall()
    return {
        "total": sum(int(r["n"]) for r in rows),
        "by_action": {r["action"]: int(r["n"]) for r in rows},
    }


def _run_canary(db_path: str, foundation_db: str | None) -> dict[str, Any]:
    """Execute the M16 canary isolation check as a subprocess and report status."""

    cmd = [sys.executable, str(CANARY_SCRIPT), "--db", db_path]
    if foundation_db:
        cmd.extend(["--foundation-db", foundation_db])
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return {
            "status": "clean" if proc.returncode == 0 else "contamination_detected",
            "exit_code": proc.returncode,
            "summary": proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "",
        }
    except Exception as exc:  # pragma: no cover - subprocess failure
        return {
            "status": "error",
            "exit_code": -1,
            "summary": f"canary check failed: {exc}",
        }


def build_soak_report(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    week: int,
    db_path: str,
    foundation_db: str | None = None,
) -> dict[str, Any]:
    """Build a read-only soak report for ``ctx.tenant_id``.

    Raises ``ValueError`` if the tenant is missing from the scope (fail-closed).
    The report is intentionally tenant-scoped but does not require a concrete
    application workspace because it aggregates across all workspaces of the tenant.
    """

    tenant_id = ctx.require_tenant()

    # Verify the tenant actually exists in the app DB.
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM workspace WHERE tenant_id = ?",
        (tenant_id,),
    ).fetchone()
    if row["n"] == 0:
        raise ValueError(f"tenant not found in app database: {tenant_id}")

    now = datetime.now(timezone.utc)
    since, until = _week_bounds(week, now)

    health = _compute_tenant_health(conn, tenant_id)
    runs = _count_weekly_runs(conn, tenant_id, since, until)
    hitl = _count_hitl_decisions(conn, tenant_id, since, until)
    usage = summarize_tenant_usage_cost(conn, tenant_id, since=since)
    incidents = _count_incidents(conn, tenant_id, since, until)
    canary = _run_canary(db_path, foundation_db)

    return {
        "report_id": f"SOAK_{tenant_id}_S{week}",
        "tenant_id": tenant_id,
        "week": week,
        "period": {"since": since, "until": until, "generated_at": utc_now()},
        "health": {
            "runs_30d": health["runs_30d"],
            "successful_runs_30d": health["successful_runs_30d"],
            "failed_runs_30d": health["failed_runs_30d"],
            "error_rate_pct": health["error_rate_pct"],
            "cost_usd_30d": health["cost_usd_30d"],
            "invoices_open": health["invoices_open"],
            "invoices_paid": health["invoices_paid"],
            "invoices_overdue": health["invoices_overdue"],
            "workspaces": health["workspaces"],
            "users": health["users"],
            "drafts_pending_approval": health["flags"]["drafts_pending_approval"],
        },
        "week_metrics": {
            "runs_total": runs["total"],
            "runs_successful": runs["succeeded"],
            "runs_failed": runs["failed"],
            "runs_requires_hitl": runs["requires_hitl"],
            "hitl_approved": hitl["approved"],
            "hitl_rejected": hitl["rejected"],
            "cost_usd": usage["total_cost_usd"],
            "surcharge_usd": usage["total_surcharge_usd"],
        },
        "incidents": incidents,
        "canary": canary,
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render the soak report as a standard audit markdown document."""

    period = report["period"]
    health = report["health"]
    week = report["week_metrics"]
    incidents = report["incidents"]
    canary = report["canary"]

    lines = [
        f"# {report['report_id']}",
        "",
        f"**Tenant:** `{report['tenant_id']}`  ",
        f"**Semana:** S{report['week']}  ",
        f"**Periodo:** {period['since']} → {period['until']}  ",
        f"**Generado:** {period['generated_at']}  ",
        "",
        "## Salud del tenant (ventana 30 días)",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Runs 30d | {health['runs_30d']} |",
        f"| Exitosos 30d | {health['successful_runs_30d']} |",
        f"| Fallidos 30d | {health['failed_runs_30d']} |",
        f"| Error rate % | {health['error_rate_pct']}% |",
        f"| Costo USD 30d | {health['cost_usd_30d']:.6f} |",
        f"| Workspaces | {health['workspaces']} |",
        f"| Usuarios | {health['users']} |",
        f"| Facturas abiertas | {health['invoices_open']} |",
        f"| Facturas pagadas | {health['invoices_paid']} |",
        f"| Facturas vencidas | {health['invoices_overdue']} |",
        f"| Drafts pendientes HITL | {health['drafts_pending_approval']} |",
        "",
        f"## Métricas de la semana S{report['week']}",
        "",
        "| Métrica | Valor |",
        "|---|---|",
        f"| Runs semana | {week['runs_total']} |",
        f"| Runs exitosos | {week['runs_successful']} |",
        f"| Runs fallidos | {week['runs_failed']} |",
        f"| Runs requieren HITL | {week['runs_requires_hitl']} |",
        f"| HITL aprobados | {week['hitl_approved']} |",
        f"| HITL rechazados | {week['hitl_rejected']} |",
        f"| Costo USD semana | {week['cost_usd']:.6f} |",
        f"| Recargo USD semana | {week['surcharge_usd']:.6f} |",
        "",
        "## Incidentes",
        "",
        f"**Total incidentes:** {incidents['total']}",
        "",
    ]
    if incidents["by_action"]:
        lines.extend(["| Acción | Count |", "|---|---|"])
        for action, count in incidents["by_action"].items():
            lines.append(f"| {action} | {count} |")
    else:
        lines.append("_Sin incidentes registrados en la ventana._")
    lines.extend([
        "",
        "## Canario de contaminación",
        "",
        f"**Estado:** {canary['status']}",
        f"**Resumen:** {canary['summary']}",
        "",
        "---",
        "",
        "_Reporte generado automáticamente por `app/scripts/soak_report.py`. "
        "Solo contiene agregados; ningún contenido de caso individual._",
    ])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a weekly soak report for a design partner.")
    parser.add_argument("--tenant-id", required=True, help="Tenant identifier")
    parser.add_argument("--week", type=int, required=True, help="Soak week (1..4)")
    parser.add_argument("--db-path", default=os.getenv("FABERLOOM_DB_PATH", "/data/faberloom.sqlite3"))
    parser.add_argument("--foundation-db", default=os.getenv("FABERLOOM_FOUNDATION_DB"))
    parser.add_argument("--out", default="docs/audits", help="Output directory for markdown report")
    parser.add_argument("--json", action="store_true", help="Also print the raw report JSON to stdout")
    parser.add_argument("--user-id", default="soak-report", help="Actor user id for the report context")
    args = parser.parse_args(argv)

    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"[FAIL] app database not found: {db_path}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    ctx = Context(
        workspace_id=SYSTEM_WORKSPACE_ID,
        tenant_id=args.tenant_id,
        user_id=args.user_id,
        actor_id=args.user_id,
        actor_role_at_decision="platform_admin",
    )

    try:
        report = build_soak_report(
            ctx,
            conn,
            week=args.week,
            db_path=str(db_path),
            foundation_db=args.foundation_db,
        )
    except Exception as exc:
        print(f"[FAIL] could not build soak report: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"SOAK_{args.tenant_id}_S{args.week}.md"
    out_path = out_dir / filename
    out_path.write_text(render_markdown(report), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, default=str))

    print(f"[OK] wrote {out_path}")
    if report["canary"]["status"] != "clean":
        print("[WARN] contamination canary is not clean — soak should be restarted after remediation")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
