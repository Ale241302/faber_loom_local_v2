"""E4-2 Autonomy Control Engine (ACE) for routing-mode promotion/degradation.

This module implements the minimum governance surface required by
``docs/faberloom/PLB_FB_E4_ROUTING_NATURAL_v1.md``:

- Measurable promotion criteria from ``shadow`` to ``natural``.
- Deterministic confirmation tokens (owner/curator HITL).
- Automatic degradation back to ``shadow`` on cost overrun.
- Audit events for every promotion/rollback/degradation.

The agent never auto-promotes; it only measures and enables a human decision.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from ..audit import audit_writer
from ..context import Context
from ..db import get_routing_policy, update_routing_policy, utc_now
from ..db_adapter import transaction
from .constants import (
    ACE_ABSURD_COST_RATIO,
    ACE_COOLDOWN_DAYS_AFTER_DOUBLE_DEGRADATION,
    ACE_DEFAULT_REPORT_DAYS,
    ACE_DEGRADE_OVERRUN_RATIO,
    ACE_DEGRADE_WINDOW_HOURS,
    ACE_MIN_SHADOW_DECISIONS_FOR_PROMOTION,
)


_TOKEN_SALT = "faberloom-e4-2-shadow-promotion"


def generate_promotion_token(workspace_id: str, action: str) -> str:
    """Return a deterministic confirmation token for a workspace promotion action."""

    payload = f"{workspace_id}:{action}:{_TOKEN_SALT}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _fmt(dt: datetime) -> str:
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def evaluate_promotion_readiness(
    ctx: Context,
    conn: Any,
    workspace_id: str,
    *,
    days: int = ACE_DEFAULT_REPORT_DAYS,
    min_decisions: int = ACE_MIN_SHADOW_DECISIONS_FOR_PROMOTION,
) -> dict[str, Any]:
    """Return whether a workspace may be promoted from ``shadow`` to ``natural``.

    Criteria (all must pass):
      - At least ``min_decisions`` shadow decisions in the analysis window.
      - Projected savings >= 0 (actual cost of the real path >= planner estimate).
      - Zero "absurd" decisions (estimated cost > 150% of actual cost).
      - Not in a 30-day cooldown after two automatic degradations.
    """

    tenant_id = ctx.require_tenant()
    since = _fmt(_now() - timedelta(days=days))

    with transaction(conn, ctx=ctx):
        # Shadow decision volume.
        count_row = conn.execute(
            """
            SELECT COUNT(*) AS n
            FROM planner_decision_log
            WHERE tenant_id = ? AND workspace_id = ? AND mode = 'shadow' AND created_at > ?
            """,
            (tenant_id, workspace_id, since),
        ).fetchone()
        shadow_decisions = int(count_row["n"]) if count_row else 0

        # Estimated vs actual cost for shadow decisions in the window.
        cost_row = conn.execute(
            """
            SELECT
                COALESCE(SUM(json_extract(plan_json, '$.est_total_cost_usd')), 0.0) AS est,
                COALESCE(SUM(json_extract(actual_outcome_json, '$.cost_usd')), 0.0) AS actual
            FROM planner_decision_log
            WHERE tenant_id = ? AND workspace_id = ? AND mode = 'shadow' AND created_at > ?
            """,
            (tenant_id, workspace_id, since),
        ).fetchone()
        estimated_cost = float(cost_row["est"] or 0.0)
        actual_cost = float(cost_row["actual"] or 0.0)
        savings = actual_cost - estimated_cost

        # Absurd decisions: planner estimated > 150% of what the real path cost.
        absurd_row = conn.execute(
            """
            SELECT COUNT(*) AS n
            FROM planner_decision_log
            WHERE tenant_id = ? AND workspace_id = ? AND mode = 'shadow' AND created_at > ?
              AND json_extract(plan_json, '$.est_total_cost_usd') >
                  json_extract(actual_outcome_json, '$.cost_usd') * ?
            """,
            (tenant_id, workspace_id, since, ACE_ABSURD_COST_RATIO),
        ).fetchone()
        absurd_count = int(absurd_row["n"]) if absurd_row else 0

        policy = get_routing_policy(ctx, conn, workspace_id)
        degraded_count = int(policy.get("degraded_count") or 0)
        last_degraded_at = policy.get("last_degraded_at")

    in_cooldown = False
    if degraded_count >= 2 and last_degraded_at:
        try:
            last = datetime.fromisoformat(last_degraded_at.replace("Z", "+00:00"))
            if (_now() - last).days < ACE_COOLDOWN_DAYS_AFTER_DOUBLE_DEGRADATION:
                in_cooldown = True
        except Exception:
            pass

    ready = (
        shadow_decisions >= min_decisions
        and savings >= -1e-9
        and absurd_count == 0
        and not in_cooldown
    )

    return {
        "workspace_id": workspace_id,
        "ready": ready,
        "shadow_decisions": shadow_decisions,
        "min_decisions": min_decisions,
        "estimated_cost_usd": estimated_cost,
        "actual_cost_usd": actual_cost,
        "projected_savings_usd": savings,
        "absurd_decisions": absurd_count,
        "degraded_count": degraded_count,
        "in_cooldown": in_cooldown,
        "window_days": days,
    }


def promote_or_rollback_workspace(
    ctx: Context,
    conn: Any,
    workspace_id: str,
    *,
    requested_mode: str,
    confirmation_token: str,
) -> dict[str, Any]:
    """Promote ``shadow -> natural`` or rollback ``natural -> shadow``.

    Promotion requires the deterministic token and a passing readiness check.
    Rollback requires only the matching token.
    """

    requested_mode = str(requested_mode).strip().lower()
    if requested_mode not in {"natural", "shadow"}:
        raise ValueError(f"Invalid requested mode '{requested_mode}': must be natural or shadow")

    if requested_mode == "natural":
        expected_action = "promote-shadow"
        readiness = evaluate_promotion_readiness(ctx, conn, workspace_id)
        if not readiness["ready"]:
            raise ValueError(f"Workspace not ready for promotion: {json.dumps(readiness)}")
    else:
        expected_action = "rollback-natural"

    expected_token = generate_promotion_token(workspace_id, expected_action)
    if not isinstance(confirmation_token, str):
        raise ValueError("confirmation_token must be a string")
    # Constant-time comparison to avoid timing leaks.
    if not _constant_time_compare(confirmation_token, expected_token):
        raise ValueError("Invalid confirmation token")

    now = utc_now()
    with transaction(conn, ctx=ctx):
        updates: dict[str, Any] = {"mode": requested_mode}
        if requested_mode == "natural":
            updates["promoted_at"] = now
        else:
            updates["promoted_at"] = None
        update_routing_policy(ctx, conn, workspace_id=workspace_id, **updates)

        action = (
            "workspace.routing.promoted"
            if requested_mode == "natural"
            else "workspace.routing.rollback"
        )
        audit_event = audit_writer.write(
            ctx,
            conn,
            action=action,
            payload={
                "workspace_id": workspace_id,
                "requested_mode": requested_mode,
                "approved_by": ctx.actor_id,
            },
            mirror_jsonl=False,
        )

    return {
        "workspace_id": workspace_id,
        "mode": requested_mode,
        "action": action,
        "promoted_at": now if requested_mode == "natural" else None,
        "audit_event_id": audit_event.id if audit_event else None,
    }


def degrade_workspace_if_needed(
    ctx: Context,
    conn: Any,
    workspace_id: str,
    *,
    window_hours: int = ACE_DEGRADE_WINDOW_HOURS,
    overrun_ratio: float = ACE_DEGRADE_OVERRUN_RATIO,
) -> dict[str, Any]:
    """Automatically degrade a workspace to ``shadow`` if real cost overruns the estimate.

    Returns a dict with ``degraded`` boolean and the measured costs.
    """

    tenant_id = ctx.require_tenant()
    since = _fmt(_now() - timedelta(hours=window_hours))

    with transaction(conn, ctx=ctx):
        actual_row = conn.execute(
            """
            SELECT COALESCE(SUM(cost_usd), 0.0) AS total
            FROM usage_record
            WHERE tenant_id = ? AND workspace_id = ? AND created_at > ? AND status = 'succeeded'
            """,
            (tenant_id, workspace_id, since),
        ).fetchone()
        actual_cost = float(actual_row["total"] or 0.0)

        estimated_row = conn.execute(
            """
            SELECT COALESCE(SUM(json_extract(plan_json, '$.est_total_cost_usd')), 0.0) AS total
            FROM planner_decision_log
            WHERE tenant_id = ? AND workspace_id = ? AND mode = 'natural' AND created_at > ?
            """,
            (tenant_id, workspace_id, since),
        ).fetchone()
        estimated_cost = float(estimated_row["total"] or 0.0)

        policy = get_routing_policy(ctx, conn, workspace_id)
        degraded_count = int(policy.get("degraded_count") or 0)

        degraded = False
        reason = None
        # Degrade only if we have a non-zero estimate and the real cost exceeds it.
        if estimated_cost > 0 and actual_cost > estimated_cost * overrun_ratio:
            degraded = True
            reason = (
                f"actual cost ${actual_cost:.8f} exceeds estimated ${estimated_cost:.8f} "
                f"by more than {overrun_ratio:.0%} in the last {window_hours}h"
            )
            now = utc_now()
            update_routing_policy(
                ctx,
                conn,
                workspace_id=workspace_id,
                mode="shadow",
                degraded_count=degraded_count + 1,
                last_degraded_at=now,
            )
            audit_writer.write(
                ctx,
                conn,
                action="living_agent.routing.degraded",
                payload={
                    "workspace_id": workspace_id,
                    "reason": reason,
                    "actual_cost_usd": actual_cost,
                    "estimated_cost_usd": estimated_cost,
                    "overrun_ratio": overrun_ratio,
                    "degraded_count": degraded_count + 1,
                },
                mirror_jsonl=False,
            )

    return {
        "workspace_id": workspace_id,
        "degraded": degraded,
        "actual_cost_usd": actual_cost,
        "estimated_cost_usd": estimated_cost,
        "overrun_ratio": overrun_ratio,
        "window_hours": window_hours,
        "reason": reason,
        "degraded_count": degraded_count + 1 if degraded else degraded_count,
    }


def _constant_time_compare(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    return hashlib.sha256(a.encode("utf-8")).digest() == hashlib.sha256(b.encode("utf-8")).digest()
