"""Human feedback loop for assistant messages (E4-3 readiness).

Records explicit accepted/rejected/regenerated feedback and translates it into
``model_track_record`` adjustments. This closes the learning loop that E4-2
opened: without real feedback the track record stays artificially at 100 %%
acceptance.
"""

from __future__ import annotations

from typing import Any

from ..context import Context
from ..db import new_id, utc_now
from ..db_adapter import transaction
from .planner import update_model_track_record
from .memory import VALID_FEEDBACK_REASONS, increment_unconsolidated_count


VALID_OUTCOMES = {"accepted", "rejected", "regenerated"}


def _extract_feedback_target(route: dict[str, Any] | None) -> dict[str, Any]:
    """Pick capability/provider/model/cost from a message route.

    Auto chains expose ``steps``; manual messages expose only provider/model.
    """

    route = route or {}
    is_auto = route.get("mode") == "auto"
    steps = route.get("steps") or []
    capability = "chat"
    if steps and isinstance(steps, list) and steps[0].get("capability"):
        capability = steps[0]["capability"]
    elif route.get("capability"):
        capability = route["capability"]

    return {
        "is_auto": is_auto,
        "capability": capability,
        "provider_slug": route.get("provider_slug") or "unknown",
        "model": route.get("model") or "unknown",
        "cost_usd": float(route.get("cost_usd") or 0.0),
        "duration_ms": int(route.get("duration_ms") or 0),
    }


def _latest_feedback_for_message(conn: Any, message_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT outcome, reason
        FROM message_feedback
        WHERE message_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT 1
        """,
        (message_id,),
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def _adjust_track_record_counts(
    conn: Any,
    ctx: Context,
    capability: str,
    provider_slug: str,
    model: str,
    accepted_delta: int = 0,
    rejected_delta: int = 0,
    regenerated_delta: int = 0,
) -> None:
    """Apply signed deltas to an existing track-record row.

    Averages (cost/latency) are intentionally left untouched: the adjustment
    only corrects the categorical counters when feedback changes.
    """

    tenant_id = ctx.require_tenant()
    row = conn.execute(
        """
        SELECT accepted_count, rejected_count, regenerated_count
        FROM model_track_record
        WHERE tenant_id = ? AND capability = ? AND provider_slug = ? AND model = ?
        """,
        (tenant_id, capability, provider_slug, model),
    ).fetchone()
    if row is None:
        return

    accepted = max(0, int(row["accepted_count"] or 0) + accepted_delta)
    rejected = max(0, int(row["rejected_count"] or 0) + rejected_delta)
    regenerated = max(0, int(row["regenerated_count"] or 0) + regenerated_delta)
    total = accepted + rejected + regenerated

    conn.execute(
        """
        UPDATE model_track_record
        SET accepted_count = ?,
            rejected_count = ?,
            regenerated_count = ?,
            total_decisions = ?,
            updated_at = ?
        WHERE tenant_id = ? AND capability = ? AND provider_slug = ? AND model = ?
        """,
        (
            accepted,
            rejected,
            regenerated,
            total,
            utc_now(),
            tenant_id,
            capability,
            provider_slug,
            model,
        ),
    )


def record_message_feedback(
    ctx: Context,
    conn: Any,
    message_id: str,
    outcome: str,
    reason: str | None = None,
) -> dict[str, Any]:
    """Store feedback and update the per-model track record.

    Rules:
      - First feedback on a non-auto message with ``accepted`` counts accepted.
      - First feedback on an auto message with ``accepted`` is a no-op because
        ``execute_plan`` already counted it as accepted.
      - ``rejected`` / ``regenerated`` compensate the auto-accepted provisional
        count when the message came from an auto chain.
      - Changing previous feedback reverts the old counters and applies the new.
    """

    outcome = str(outcome).strip().lower()
    if outcome not in VALID_OUTCOMES:
        raise ValueError(f"Invalid feedback outcome: {outcome}")
    if reason is not None:
        reason = str(reason).strip().lower()
        if reason not in VALID_FEEDBACK_REASONS:
            raise ValueError(
                f"Invalid feedback reason: {reason}. Allowed: {sorted(VALID_FEEDBACK_REASONS)}"
            )

    workspace_id = ctx.require_scoped_workspace()
    tenant_id = ctx.require_tenant()

    with transaction(conn, ctx=ctx):
        msg_row = conn.execute(
            """
            SELECT role, content_json
            FROM message
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (message_id, workspace_id, tenant_id),
        ).fetchone()
        if msg_row is None:
            raise ValueError("Message not found in current workspace")
        if msg_row["role"] != "assistant":
            raise ValueError("Feedback can only be recorded on assistant messages")

        previous = _latest_feedback_for_message(conn, message_id)
        previous_outcome = previous["outcome"] if previous else None
        previous_reason = previous.get("reason") if previous else None
        if previous_outcome == outcome and previous_reason == reason:
            # Idempotent: nothing changes in the track record or reason.
            return {
                "message_id": message_id,
                "outcome": outcome,
                "previous_outcome": previous_outcome,
                "reason": reason,
            }
        # E4-5: if the outcome is unchanged but the reason changed, we still
        # record a new feedback row so the typed reason reaches the detector.
        # The track-record counters stay the same.

        route = None
        try:
            import json

            payload = json.loads(msg_row["content_json"] or "{}")
            route = payload.get("route") if isinstance(payload, dict) else None
        except Exception:
            route = None

        target = _extract_feedback_target(route)
        capability = target["capability"]
        provider_slug = target["provider_slug"]
        model = target["model"]
        cost_usd = target["cost_usd"]
        duration_ms = target["duration_ms"]
        is_auto = target["is_auto"]

        feedback_id = new_id("mfb")
        now = utc_now()
        conn.execute(
            """
            INSERT INTO message_feedback (
                id, message_id, workspace_id, tenant_id, outcome,
                previous_outcome, reason, actor_id, actor_role_at_decision,
                schema_version, source_version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                feedback_id,
                message_id,
                workspace_id,
                tenant_id,
                outcome,
                previous_outcome,
                reason,
                ctx.actor_id,
                ctx.actor_role_at_decision,
                47,
                "v1",
                now,
            ),
        )

        # E4-5: every explicit feedback event feeds the personal learning thermometer.
        increment_unconsolidated_count(ctx, conn)

        if previous_outcome is None:
            if outcome == "accepted":
                if not is_auto:
                    update_model_track_record(
                        ctx,
                        conn,
                        capability=capability,
                        provider_slug=provider_slug,
                        model=model,
                        outcome="accepted",
                        cost_usd=cost_usd,
                        latency_ms=duration_ms,
                    )
            else:
                if is_auto:
                    _adjust_track_record_counts(
                        conn,
                        ctx,
                        capability,
                        provider_slug,
                        model,
                        accepted_delta=-1,
                    )
                update_model_track_record(
                    ctx,
                    conn,
                    capability=capability,
                    provider_slug=provider_slug,
                    model=model,
                    outcome=outcome,
                    cost_usd=cost_usd,
                    latency_ms=duration_ms,
                )
        else:
            deltas: dict[str, int] = {"accepted": 0, "rejected": 0, "regenerated": 0}
            deltas[outcome] += 1
            deltas[previous_outcome] -= 1
            _adjust_track_record_counts(
                conn,
                ctx,
                capability,
                provider_slug,
                model,
                accepted_delta=deltas["accepted"],
                rejected_delta=deltas["rejected"],
                regenerated_delta=deltas["regenerated"],
            )

    return {
        "id": feedback_id,
        "message_id": message_id,
        "outcome": outcome,
        "previous_outcome": previous_outcome,
        "reason": reason,
        "created_at": now,
    }
