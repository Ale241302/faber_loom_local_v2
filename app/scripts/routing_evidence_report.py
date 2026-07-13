#!/usr/bin/env python3
"""Genera evidencia operacional semanal del modo de routing (E5-1).

El reporte es read-only y tenant-scoped. Agrega decisiones del planner
(`planner_decision_log`) y consumo real (`usage_record`) para documentar:
- Volumen de decisiones shadow vs natural.
- Estimación vs costo real, ahorro proyectado y decisiones "absurdas".
- Estado actual de la política de routing (modo, degradaciones, cooldown).
- Uso por modelo/proveedor y tasa de éxito.

Ejemplo (semanal, un tenant):
    python app/scripts/routing_evidence_report.py \\
        --tenant-id tnt_xxx \\
        --db-path $FABERLOOM_DB_PATH \\
        --out docs/audits/EVIDENCIA_ROUTING_$(date +%Y%m%d).md
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.src.context import Context, enforce_tenant_scoped
from app.src.db import connect, get_routing_policy, row_to_dict, utc_now


_DEFAULT_DAYS = 7


def _json_extract_expr(conn: Any, column: str, key: str) -> str:
    """Return an engine-specific JSON numeric extraction expression."""

    engine = getattr(conn, "engine", "sqlite")
    if engine == "postgres":
        return f"((NULLIF({column}, ''))::jsonb ->> '{key}')::float8"
    return f"json_extract({column}, '$.{key}')"


def _week_bounds(days: int) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    return (
        since.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        now.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
    )


def _validate_tenant(conn: Any, tenant_id: str) -> None:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM workspace WHERE tenant_id = ?",
        (tenant_id,),
    ).fetchone()
    if row is None or row["n"] == 0:
        raise ValueError(f"tenant not found: {tenant_id}")


def _planner_metrics(conn: Any, tenant_id: str, since: str) -> dict[str, Any]:
    total_row = conn.execute(
        """
        SELECT COUNT(*) AS n,
               SUM(CASE WHEN mode = 'shadow' THEN 1 ELSE 0 END) AS shadow_n,
               SUM(CASE WHEN mode = 'natural' THEN 1 ELSE 0 END) AS natural_n
        FROM planner_decision_log
        WHERE tenant_id = ? AND created_at >= ?
        """,
        (tenant_id, since),
    ).fetchone()

    est_expr = _json_extract_expr(conn, "plan_json", "est_total_cost_usd")
    act_expr = _json_extract_expr(conn, "actual_outcome_json", "cost_usd")
    cost_row = conn.execute(
        f"""
        SELECT
            COALESCE(SUM(CASE WHEN mode = 'shadow' THEN {est_expr} ELSE 0 END), 0.0) AS est,
            COALESCE(SUM(CASE WHEN mode = 'shadow' THEN {act_expr} ELSE 0 END), 0.0) AS actual
        FROM planner_decision_log
        WHERE tenant_id = ? AND created_at >= ?
        """,
        (tenant_id, since),
    ).fetchone()

    absurd_row = conn.execute(
        f"""
        SELECT COUNT(*) AS n
        FROM planner_decision_log
        WHERE tenant_id = ? AND created_at >= ? AND mode = 'shadow'
          AND {est_expr} > {act_expr} * 1.5
        """,
        (tenant_id, since),
    ).fetchone()

    estimated = float(cost_row["est"] or 0.0)
    actual = float(cost_row["actual"] or 0.0)
    return {
        "total_decisions": int(total_row["n"] or 0),
        "shadow_decisions": int(total_row["shadow_n"] or 0),
        "natural_decisions": int(total_row["natural_n"] or 0),
        "estimated_cost_usd": estimated,
        "actual_cost_usd": actual,
        "projected_savings_usd": actual - estimated,
        "absurd_decisions": int(absurd_row["n"] or 0),
    }


def _usage_metrics(conn: Any, tenant_id: str, since: str) -> dict[str, Any]:
    total_row = conn.execute(
        """
        SELECT
            COUNT(*) AS n,
            SUM(CASE WHEN status = 'succeeded' THEN 1 ELSE 0 END) AS succeeded,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed,
            SUM(CASE WHEN status = 'budget_exceeded' THEN 1 ELSE 0 END) AS budget_exceeded,
            COALESCE(SUM(cost_usd), 0.0) AS cost_usd,
            COALESCE(SUM(input_tokens + output_tokens), 0) AS tokens
        FROM usage_record
        WHERE tenant_id = ? AND created_at >= ?
        """,
        (tenant_id, since),
    ).fetchone()

    rows = conn.execute(
        """
        SELECT provider_slug, model, status, COUNT(*) AS n
        FROM usage_record
        WHERE tenant_id = ? AND created_at >= ?
        GROUP BY provider_slug, model, status
        ORDER BY n DESC
        """,
        (tenant_id, since),
    ).fetchall()

    provider_counter: Counter[str] = Counter()
    model_counter: Counter[str] = Counter()
    for row in rows:
        provider_counter[row["provider_slug"]] += row["n"]
        model_counter[f"{row['provider_slug']}/{row['model']}"] += row["n"]

    total = int(total_row["n"] or 0)
    return {
        "total_calls": total,
        "succeeded": int(total_row["succeeded"] or 0),
        "failed": int(total_row["failed"] or 0),
        "budget_exceeded": int(total_row["budget_exceeded"] or 0),
        "success_rate": round(int(total_row["succeeded"] or 0) / total, 4) if total else 0.0,
        "cost_usd": float(total_row["cost_usd"] or 0.0),
        "tokens": int(total_row["tokens"] or 0),
        "top_providers": provider_counter.most_common(5),
        "top_models": model_counter.most_common(5),
    }


def _policy_status(conn: Any, ctx: Context) -> dict[str, Any]:
    policy = get_routing_policy(ctx, conn)
    return {
        "workspace_id": policy.get("workspace_id"),
        "mode": policy.get("mode"),
        "promoted_at": policy.get("promoted_at"),
        "degraded_count": int(policy.get("degraded_count") or 0),
        "last_degraded_at": policy.get("last_degraded_at"),
        "auto_mode_enabled": bool(policy.get("auto_mode_enabled")),
        "budget_cap_usd": float(policy.get("budget_cap_usd") or 0.0),
    }


def build_routing_report(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    days: int = _DEFAULT_DAYS,
) -> dict[str, Any]:
    """Build the routing evidence report for the given tenant context."""

    enforce_tenant_scoped(ctx)
    tenant_id = ctx.require_tenant()
    _validate_tenant(conn, tenant_id)

    since, until = _week_bounds(days)
    return {
        "report_id": f"ROUTING_{tenant_id}_{since[:10]}",
        "tenant_id": tenant_id,
        "workspace_id": ctx.workspace_id,
        "period": {"since": since, "until": until, "generated_at": utc_now(), "days": days},
        "planner": _planner_metrics(conn, tenant_id, since),
        "usage": _usage_metrics(conn, tenant_id, since),
        "policy": _policy_status(conn, ctx),
    }


def render_markdown(report: dict[str, Any]) -> str:
    p = report["planner"]
    u = report["usage"]
    pol = report["policy"]
    period = report["period"]

    lines: list[str] = [
        "# Evidencia operacional de routing (E5-1)",
        "",
        f"- **report_id**: `{report['report_id']}`",
        f"- **tenant_id**: `{report['tenant_id']}`",
        f"- **workspace_id**: `{report['workspace_id']}`",
        f"- **período**: `{period['since']}` → `{period['until']}` ({period['days']} días)",
        f"- **generado_en**: `{period['generated_at']}`",
        "",
        "## Estado de la política de routing",
        "",
        f"- **modo actual**: `{pol['mode']}`",
        f"- **promoted_at**: `{pol['promoted_at']}`",
        f"- **degraded_count**: `{pol['degraded_count']}`",
        f"- **last_degraded_at**: `{pol['last_degraded_at']}`",
        f"- **auto_mode_enabled**: `{pol['auto_mode_enabled']}`",
        f"- **budget_cap_usd**: `{pol['budget_cap_usd']}`",
        "",
        "> Nota: la promoción de `shadow` a `natural` requiere aprobación humana explícita; "
        "este reporte solo recopila evidencia.",
        "",
        "## Métricas del planner",
        "",
        f"- **decisiones totales**: {p['total_decisions']}",
        f"- **decisiones shadow**: {p['shadow_decisions']}",
        f"- **decisiones natural**: {p['natural_decisions']}",
        f"- **costo estimado (shadow)**: ${p['estimated_cost_usd']:.6f}",
        f"- **costo actual (shadow)**: ${p['actual_cost_usd']:.6f}",
        f"- **ahorro proyectado**: ${p['projected_savings_usd']:.6f}",
        f"- **decisiones absurdas** (estimado > 150% real): {p['absurd_decisions']}",
        "",
        "## Uso real de modelos",
        "",
        f"- **llamadas totales**: {u['total_calls']}",
        f"- **exitosas**: {u['succeeded']}",
        f"- **fallidas**: {u['failed']}",
        f"- **budget_exceeded**: {u['budget_exceeded']}",
        f"- **tasa de éxito**: {u['success_rate']:.2%}",
        f"- **costo total USD**: ${u['cost_usd']:.6f}",
        f"- **tokens totales**: {u['tokens']}",
        "",
    ]

    lines.extend(["### Top proveedores", "", "| proveedor | llamadas |", "|---|---|"])
    for provider, n in u["top_providers"]:
        lines.append(f"| {provider} | {n} |")
    lines.append("")

    lines.extend(["### Top modelos", "", "| modelo | llamadas |", "|---|---|"])
    for model, n in u["top_models"]:
        lines.append(f"| {model} | {n} |")
    lines.append("")

    lines.extend(
        [
            "## Criterios de promoción (shadow → natural)",
            "",
            "- Mínimo de decisiones shadow en la ventana (configurable).",
            "- Ahorro proyectado >= 0 (costo real <= estimado).",
            "- Cero decisiones absurdas.",
            "- Fuera del cooldown de 30 días tras dos degradaciones automáticas.",
            "- Aprobación humana explícita antes de cambiar `mode`.",
            "",
            "---",
            "Reporte generado automáticamente por `app/scripts/routing_evidence_report.py`.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Genera evidencia operacional de routing para un tenant."
    )
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--workspace-id", default=None)
    parser.add_argument("--days", type=int, default=_DEFAULT_DAYS)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/audits") / f"EVIDENCIA_ROUTING_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md",
    )
    parser.add_argument(
        "--db-path",
        default=os.getenv("FABERLOOM_DB_PATH"),
        help="Path to the FaberLoom SQLite database (default: FABERLOOM_DB_PATH env).",
    )
    args = parser.parse_args(argv)

    if not args.db_path:
        print("Error: --db-path or FABERLOOM_DB_PATH is required", file=sys.stderr)
        return 2

    os.environ["FABERLOOM_DB_PATH"] = args.db_path

    ctx = Context(
        workspace_id=args.workspace_id,
        tenant_id=args.tenant_id,
        user_id="routing_report",
        actor_id="routing_report",
        actor_role_at_decision="system",
    )

    conn = connect()
    try:
        report = build_routing_report(ctx, conn, days=args.days)
        markdown = render_markdown(report)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(markdown, encoding="utf-8")
        print(f"Report written to: {args.out}")
        print(
            f"Planner: {report['planner']['total_decisions']} decisions, "
            f"usage: {report['usage']['total_calls']} calls, "
            f"cost: ${report['usage']['cost_usd']:.6f}"
        )
        return 0
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
