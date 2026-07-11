"""E4-2 planner instrumentation: decision logging, shadow planning and track record.

This module wraps the E4-0 NaturalPlanner with persistence and governance:
- every plan (shadow or natural) is logged with full candidates, chosen model and reason (R11);
- shadow plans only plan, never execute;
- per-model track record feeds back into model selection for non-manual modes.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any

from ..context import Context
from ..db import insert_usage_record, new_id, utc_now
from ..db_adapter import transaction
from ..routing.auto_dispatcher import NaturalPlanner

logger = logging.getLogger(__name__)


SHADOW_CAPABILITY = "shadow_plan"
SHADOW_PROVIDER = "living_agent"
SHADOW_MODEL = "shadow_plan"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _fmt(dt: datetime) -> str:
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _serialize_plan(plan: Any) -> dict[str, Any]:
    """Serialize a DispatchPlan (or any dataclass) to a plain dict."""

    if hasattr(plan, "__dataclass_fields__"):
        return asdict(plan)  # type: ignore[arg-type]
    if isinstance(plan, dict):
        return plan
    return {"repr": repr(plan)}


def log_planner_decision(
    ctx: Context,
    conn: Any,
    *,
    mode: str,
    plan: Any,
    actual_outcome: dict[str, Any] | None = None,
    correlation_id: str | None = None,
    chain_id: str | None = None,
    task_ref: str | None = None,
    planner_cost_usd: float = 0.0,
) -> dict[str, Any]:
    """Persist a planner decision. Returns the inserted row."""

    decision_id = new_id("pdl")
    now = utc_now()
    actor_id = ctx.actor_id or ctx.user_id or "system"
    actor_role = ctx.actor_role_at_decision or "system"

    with transaction(conn, ctx=ctx):
        conn.execute(
            """
            INSERT INTO planner_decision_log (
                id, tenant_id, workspace_id, chain_id, task_ref, mode,
                plan_json, actual_outcome_json, correlation_id,
                actor_id, actor_role_at_decision, routine_version, skill_version,
                schema_version, source_version, approved_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision_id,
                ctx.require_tenant(),
                ctx.workspace_id,
                chain_id,
                task_ref,
                mode,
                json.dumps(_serialize_plan(plan), ensure_ascii=False),
                json.dumps(actual_outcome or {}, ensure_ascii=False),
                correlation_id,
                actor_id,
                actor_role,
                None,
                None,
                43,
                "v1",
                None,
                now,
                now,
            ),
        )
        row = conn.execute(
            "SELECT * FROM planner_decision_log WHERE id = ?",
            (decision_id,),
        ).fetchone()

    return dict(row)


def record_shadow_plan_cost(
    ctx: Context,
    conn: Any,
    *,
    chat_id: str | None,
    chain_id: str | None,
    cost_usd: float,
    duration_ms: int = 0,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    """Record the estimated cost of a shadow plan as a usage_record."""

    return insert_usage_record(
        ctx,
        conn,
        chat_id=chat_id,
        provider_slug=SHADOW_PROVIDER,
        model=SHADOW_MODEL,
        input_tokens=0,
        output_tokens=0,
        cost_usd=cost_usd,
        duration_ms=duration_ms,
        status="ok",
        error=None,
        attempts_json=[],
        request_json={"correlation_id": correlation_id, "mode": "shadow"},
        response_json={},
        chain_id=chain_id,
        capability=SHADOW_CAPABILITY,
    )


def run_shadow_plan(
    ctx: Context,
    conn: Any,
    *,
    chat_id: str,
    user_request: str,
    attachments: list[dict[str, Any]] | None = None,
    policy: dict[str, Any] | None = None,
    actual_outcome: dict[str, Any] | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any] | None:
    """Run a shadow plan for a request and log the decision.

    This function only plans; it never executes steps. The cost recorded is the
    planner's own estimated cost.
    """

    chain_id = new_id("chn")
    started_at = _now()
    try:
        planner = NaturalPlanner()
        plan = planner.plan(
            ctx,
            conn,
            user_request=user_request,
            attachments=attachments,
            policy=policy,
        )
        duration_ms = int((_now() - started_at).total_seconds() * 1000)

        log = log_planner_decision(
            ctx,
            conn,
            mode="shadow",
            plan=plan,
            actual_outcome=actual_outcome,
            correlation_id=correlation_id,
            chain_id=chain_id,
            task_ref=chat_id,
            planner_cost_usd=plan.planner_cost_usd,
        )
        record_shadow_plan_cost(
            ctx,
            conn,
            chat_id=chat_id,
            chain_id=chain_id,
            cost_usd=plan.planner_cost_usd,
            duration_ms=duration_ms,
            correlation_id=correlation_id,
        )
        return log
    except Exception:
        logger.exception("Shadow plan failed for chat %s", chat_id)
        return None


def update_model_track_record(
    ctx: Context,
    conn: Any,
    *,
    capability: str,
    provider_slug: str,
    model: str,
    outcome: str,
    cost_usd: float = 0.0,
    latency_ms: float = 0.0,
) -> dict[str, Any]:
    """Update acceptance/cost statistics for a (tenant, capability, provider, model).

    outcome must be one of: accepted, regenerated, rejected.
    """

    if outcome not in {"accepted", "regenerated", "rejected"}:
        raise ValueError(f"Invalid outcome '{outcome}'")

    tenant_id = ctx.require_tenant()
    now = utc_now()
    actor_id = ctx.actor_id or ctx.user_id or "system"
    actor_role = ctx.actor_role_at_decision or "system"

    with transaction(conn, ctx=ctx):
        existing = conn.execute(
            """
            SELECT total_decisions, accepted_count, regenerated_count, rejected_count,
                   avg_cost_usd, avg_latency_ms
            FROM model_track_record
            WHERE tenant_id = ? AND capability = ? AND provider_slug = ? AND model = ?
            """,
            (tenant_id, capability, provider_slug, model),
        ).fetchone()

        if existing is None:
            total = 1
            accepted = 1 if outcome == "accepted" else 0
            regenerated = 1 if outcome == "regenerated" else 0
            rejected = 1 if outcome == "rejected" else 0
            avg_cost = cost_usd
            avg_latency = latency_ms
        else:
            total = int(existing["total_decisions"]) + 1
            accepted = int(existing["accepted_count"]) + (1 if outcome == "accepted" else 0)
            regenerated = int(existing["regenerated_count"]) + (1 if outcome == "regenerated" else 0)
            rejected = int(existing["rejected_count"]) + (1 if outcome == "rejected" else 0)
            prev_avg_cost = float(existing["avg_cost_usd"] or 0.0)
            prev_avg_latency = float(existing["avg_latency_ms"] or 0.0)
            avg_cost = (prev_avg_cost * (total - 1) + cost_usd) / total
            avg_latency = (prev_avg_latency * (total - 1) + latency_ms) / total

        conn.execute(
            """
            INSERT INTO model_track_record (
                tenant_id, capability, provider_slug, model,
                total_decisions, accepted_count, regenerated_count, rejected_count,
                avg_cost_usd, avg_latency_ms, last_used_at,
                actor_id, actor_role_at_decision, routine_version, skill_version,
                schema_version, source_version, approved_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tenant_id, capability, provider_slug, model) DO UPDATE SET
                total_decisions = excluded.total_decisions,
                accepted_count = excluded.accepted_count,
                regenerated_count = excluded.regenerated_count,
                rejected_count = excluded.rejected_count,
                avg_cost_usd = excluded.avg_cost_usd,
                avg_latency_ms = excluded.avg_latency_ms,
                last_used_at = excluded.last_used_at,
                actor_id = excluded.actor_id,
                actor_role_at_decision = excluded.actor_role_at_decision,
                schema_version = excluded.schema_version,
                source_version = excluded.source_version,
                approved_by = excluded.approved_by,
                updated_at = excluded.updated_at
            """,
            (
                tenant_id, capability, provider_slug, model,
                total, accepted, regenerated, rejected,
                round(avg_cost, 8), round(avg_latency, 4), now,
                actor_id, actor_role, None, None,
                43, "v1", None, now, now,
            ),
        )
        row = conn.execute(
            """
            SELECT * FROM model_track_record
            WHERE tenant_id = ? AND capability = ? AND provider_slug = ? AND model = ?
            """,
            (tenant_id, capability, provider_slug, model),
        ).fetchone()

    return dict(row)


def get_model_track_record(
    conn: Any,
    ctx: Context,
    capability: str,
    provider_slug: str,
    model: str,
) -> dict[str, Any] | None:
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT * FROM model_track_record
            WHERE tenant_id = ? AND capability = ? AND provider_slug = ? AND model = ?
            """,
            (ctx.require_tenant(), capability, provider_slug, model),
        ).fetchone()
    return dict(row) if row else None


def run_shadow_plan_background(
    tenant_id: str,
    workspace_id: str,
    chat_id: str,
    user_request: str,
    *,
    actor_role: str | None = None,
    actual_outcome: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
    attachments: list[dict[str, Any]] | None = None,
) -> None:
    """Entry point for FastAPI BackgroundTasks: opens a fresh DB connection."""

    from ..db import connect

    conn = connect()
    try:
        ctx = Context(
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            user_id="shadow",
            actor_id="shadow",
            actor_role_at_decision=actor_role or "system",
        )
        run_shadow_plan(
            ctx,
            conn,
            chat_id=chat_id,
            user_request=user_request,
            attachments=attachments,
            policy=policy,
            actual_outcome=actual_outcome,
            correlation_id=chat_id,
        )
    except Exception:
        logger.exception("Background shadow plan failed for chat %s", chat_id)
    finally:
        conn.close()


def get_shadow_report(
    conn: Any,
    ctx: Context,
    *,
    days: int = 14,
) -> dict[str, Any]:
    """Return aggregated shadow vs natural metrics for the tenant."""

    tenant_id = ctx.require_tenant()
    since = (_now() - timedelta(days=days)).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    with transaction(conn, ctx=ctx):
        total_rows = conn.execute(
            """
            SELECT mode, COUNT(*) AS n
            FROM planner_decision_log
            WHERE tenant_id = ? AND created_at > ?
            GROUP BY mode
            """,
            (tenant_id, since),
        ).fetchall()

        model_rows = conn.execute(
            """
            SELECT capability, provider_slug, model,
                   total_decisions, accepted_count, regenerated_count, rejected_count,
                   avg_cost_usd, avg_latency_ms
            FROM model_track_record
            WHERE tenant_id = ?
            ORDER BY capability, accepted_count DESC
            """,
            (tenant_id,),
        ).fetchall()

        cost_rows = conn.execute(
            """
            SELECT mode,
                   COALESCE(SUM(json_extract(plan_json, '$.est_total_cost_usd')), 0) AS est_cost,
                   COALESCE(SUM(json_extract(actual_outcome_json, '$.cost_usd')), 0) AS actual_cost
            FROM planner_decision_log
            WHERE tenant_id = ? AND created_at > ?
            GROUP BY mode
            """,
            (tenant_id, since),
        ).fetchall()

    total_by_mode = {row["mode"]: int(row["n"]) for row in total_rows}
    cost_by_mode = {}
    for row in cost_rows:
        cost_by_mode[row["mode"]] = {
            "estimated_cost_usd": float(row["est_cost"] or 0.0),
            "actual_cost_usd": float(row["actual_cost"] or 0.0),
        }

    return {
        "tenant_id": tenant_id,
        "days": days,
        "since": since,
        "decisions_count": total_by_mode,
        "cost_by_mode": cost_by_mode,
        "model_records": [dict(row) for row in model_rows],
    }
