"""FaberLoom SL3b/E2-3: gold loop helpers with L2/L3 state machine."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import sqlite3

from .context import Context
from .db import (
    GOLD_CANDIDATE_COLUMNS,
    get_routine,
    record_editorial_event,
    row_to_dict,
    transaction,
    utc_now,
)
from .draft_engine import _extract_hard_tokens


_GOLD_STATES = frozenset({"candidate", "active_l2", "l3_pending", "l3", "rejected"})

# Roles that may promote a candidate to workspace-trusted gold (L2).
_L2_ROLES = frozenset({"owner", "admin", "curator", "ceo", "operator", "am"})

# Roles that may move a candidate to L3 / org-shared knowledge.
_L3_ROLES = frozenset({"owner", "admin", "curator", "ceo"})

# Valid state transitions. ``None`` means "from any state" is not supported.
_VALID_TRANSITIONS: dict[str, set[str]] = {
    "candidate": {"active_l2", "rejected"},
    "active_l2": {"l3_pending", "rejected"},
    "l3_pending": {"l3", "rejected"},
}


def _normalize_role(role: str | None) -> str:
    return (role or "").strip().lower()


def _role_can_l2(role: str | None) -> bool:
    normalized = _normalize_role(role)
    # Empty role is treated as owner for backward compatibility with existing
    # repository-layer callers that do not set actor_role_at_decision.
    return normalized in _L2_ROLES or normalized == ""


def _role_can_l3(role: str | None) -> bool:
    normalized = _normalize_role(role)
    return normalized in _L3_ROLES or normalized == ""


def _contains_hard_fields(value: dict[str, Any]) -> bool:
    """Return True when *value* contains prices, SKUs, stock, margins, etc."""

    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    return bool(_extract_hard_tokens(text))


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _learned_hash(value: dict[str, Any]) -> str:
    """Stable hash of the learned/canonized output used for k-anon counts."""

    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def get_gold_candidate(
    ctx: Context,
    conn: sqlite3.Connection,
    candidate_id: str,
) -> dict[str, Any] | None:
    """Return a gold candidate row if it belongs to the current workspace/tenant."""

    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        f"""
        SELECT {GOLD_CANDIDATE_COLUMNS}
        FROM gold_candidate
        WHERE id = ? AND workspace_id = ? AND tenant_id = ?
        """,
        (candidate_id, workspace_id, ctx.tenant_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def _count_similar_learned(conn: sqlite3.Connection, candidate: dict[str, Any]) -> int:
    """SQLite-friendly k-anon count including the candidate itself.

    Counts non-rejected candidates in the same tenant with the same
    canonized learned_output_json. For promotion to L3 the result must be >= 5.
    """

    tenant_id = candidate.get("tenant_id")
    learned = candidate.get("learned_output_json") or "{}"
    try:
        learned_value = json.loads(learned)
    except json.JSONDecodeError:
        learned_value = {}
    if not isinstance(learned_value, dict):
        learned_value = {}
    target = _canonical_json(learned_value)

    rows = conn.execute(
        """
        SELECT learned_output_json
        FROM gold_candidate
        WHERE tenant_id = ? AND state != 'rejected'
        """,
        (tenant_id,),
    ).fetchall()
    count = 0
    for row in rows:
        other = row["learned_output_json"] or "{}"
        try:
            other_value = json.loads(other)
        except json.JSONDecodeError:
            continue
        if not isinstance(other_value, dict):
            other_value = {}
        if _canonical_json(other_value) == target:
            count += 1
    return count


def list_gold_candidates(
    ctx: Context,
    conn: sqlite3.Connection,
    routine_id: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return gold candidate rows for the current workspace/tenant."""

    workspace_id = ctx.require_scoped_workspace()
    params: list[Any] = [workspace_id, ctx.tenant_id]
    sql = f"""
        SELECT {GOLD_CANDIDATE_COLUMNS}
        FROM gold_candidate
        WHERE workspace_id = ? AND tenant_id = ?
    """
    if routine_id is not None:
        sql += " AND routine_id = ?"
        params.append(routine_id)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(row) for row in rows]


def list_approved_gold_candidates_for_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    routine_id: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Return promoted gold candidates safe to use as few-shot examples."""

    workspace_id = ctx.require_scoped_workspace()
    rows = conn.execute(
        f"""
        SELECT {GOLD_CANDIDATE_COLUMNS}
        FROM gold_candidate
        WHERE workspace_id = ? AND tenant_id = ? AND routine_id = ?
          AND state IN ('active_l2', 'l3')
        ORDER BY use_count ASC, created_at DESC
        LIMIT ?
        """,
        (workspace_id, ctx.tenant_id, routine_id, limit),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def promote_gold_candidate(
    ctx: Context,
    conn: sqlite3.Connection,
    candidate_id: str,
    learned_output_json: dict[str, Any],
    approved_by: str | None = None,
    verified_by: str | None = None,
    target_state: str = "active_l2",
    actor_role_at_decision: str | None = None,
) -> dict[str, Any] | None:
    """Promote a gold candidate through the L2/L3 state machine.

    States:
      - candidate: created automatically from a low-edit approved run.
      - active_l2: workspace-trusted gold (AM + second verifier if hard fields).
      - l3_pending: queued for org-wide promotion; requires k-anon >= 5.
      - l3: org-shared knowledge; requires a curator/CEO verifier.
      - rejected: discarded.
    """

    workspace_id = ctx.require_scoped_workspace()
    approved_by = approved_by or ctx.resolved_actor_id()
    actor_role = _normalize_role(actor_role_at_decision or ctx.actor_role_at_decision)
    now = utc_now()

    if target_state not in _GOLD_STATES:
        raise ValueError(f"Invalid target state: {target_state}")

    candidate = get_gold_candidate(ctx, conn, candidate_id)
    if candidate is None:
        return None

    current_state = candidate.get("state") or "candidate"
    allowed = _VALID_TRANSITIONS.get(current_state, set())
    if target_state not in allowed:
        raise ValueError(
            f"Invalid state transition from {current_state} to {target_state}"
        )

    has_hard_fields = _contains_hard_fields(learned_output_json)

    if target_state == "active_l2":
        if not _role_can_l2(actor_role):
            raise ValueError(
                "Insufficient role to promote gold candidate to L2"
            )
        if has_hard_fields and not verified_by:
            raise ValueError(
                "Hard fields require independent verification; provide verified_by"
            )
        if verified_by and approved_by == verified_by:
            raise ValueError(
                "Second gate gold: promoter and verifier must be different actors"
            )

        cursor = conn.execute(
            """
            UPDATE gold_candidate
            SET learned_output_json = ?, approved = 1, approved_by = ?, verified_by = ?,
                state = ?, actor_role_at_decision = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (
                _canonical_json(learned_output_json),
                approved_by,
                verified_by,
                target_state,
                actor_role,
                now,
                candidate_id,
                workspace_id,
                ctx.tenant_id,
            ),
        )
        if cursor.rowcount == 0:
            return None
        return get_gold_candidate(ctx, conn, candidate_id)

    if target_state == "l3_pending":
        if not _role_can_l3(actor_role):
            raise ValueError(
                "Insufficient role to queue gold candidate for L3"
            )
        # Update learned output before counting so k-anon reflects the intended canonized value.
        conn.execute(
            """
            UPDATE gold_candidate
            SET learned_output_json = ?, state = ?, actor_role_at_decision = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (
                _canonical_json(learned_output_json),
                target_state,
                actor_role,
                now,
                candidate_id,
                workspace_id,
                ctx.tenant_id,
            ),
        )
        candidate = get_gold_candidate(ctx, conn, candidate_id)
        if candidate is None:
            return None
        k = _count_similar_learned(conn, candidate)
        if k < 5:
            raise ValueError(
                f"L3 promotion requires k-anon >= 5 (found {k})"
            )
        return candidate

    if target_state == "l3":
        if not _role_can_l3(actor_role):
            raise ValueError(
                "Insufficient role to promote gold candidate to L3"
            )
        original_approved_by = candidate.get("approved_by") or approved_by
        if has_hard_fields and not verified_by:
            raise ValueError(
                "Hard fields require independent verification; provide verified_by"
            )
        if verified_by and original_approved_by == verified_by:
            raise ValueError(
                "Second gate gold: promoter and verifier must be different actors"
            )
        # Ensure k-anon still holds at final L3 promotion.
        k = _count_similar_learned(conn, candidate)
        if k < 5:
            raise ValueError(
                f"L3 promotion requires k-anon >= 5 (found {k})"
            )
        cursor = conn.execute(
            """
            UPDATE gold_candidate
            SET learned_output_json = ?, approved = 1, verified_by = ?,
                state = ?, actor_role_at_decision = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (
                _canonical_json(learned_output_json),
                verified_by,
                target_state,
                actor_role,
                now,
                candidate_id,
                workspace_id,
                ctx.tenant_id,
            ),
        )
        if cursor.rowcount == 0:
            return None
        return get_gold_candidate(ctx, conn, candidate_id)

    if target_state == "rejected":
        if not (_role_can_l2(actor_role) or _role_can_l3(actor_role)):
            raise ValueError("Insufficient role to reject gold candidate")
        cursor = conn.execute(
            """
            UPDATE gold_candidate
            SET state = ?, approved = 0, actor_role_at_decision = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (
                target_state,
                actor_role,
                now,
                candidate_id,
                workspace_id,
                ctx.tenant_id,
            ),
        )
        if cursor.rowcount == 0:
            return None
        return get_gold_candidate(ctx, conn, candidate_id)

    raise ValueError(f"Unhandled target state: {target_state}")


def apply_gold_to_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    candidate_id: str,
) -> dict[str, Any] | None:
    """Apply a promoted gold candidate's learned output to its parent routine."""

    workspace_id = ctx.require_scoped_workspace()

    with transaction(conn):
        candidate = get_gold_candidate(ctx, conn, candidate_id)
        if candidate is None:
            return None
        if candidate.get("state") not in {"active_l2", "l3"}:
            raise ValueError("Gold candidate must be promoted before applying to routine")
        if candidate.get("used") == 1:
            raise ValueError("Gold candidate has already been applied to routine")

        routine = get_routine(ctx, conn, candidate["routine_id"])
        if routine is None:
            return None

        try:
            current_schema = json.loads(routine.get("schema_output_json") or "{}")
        except json.JSONDecodeError:
            current_schema = {}
        if not isinstance(current_schema, dict):
            current_schema = {}

        try:
            learned = json.loads(candidate.get("learned_output_json") or "{}")
        except json.JSONDecodeError:
            learned = {}
        if not isinstance(learned, dict):
            learned = {}

        merged_schema = {**current_schema, **learned}
        merged_schema_json = json.dumps(merged_schema, ensure_ascii=False, sort_keys=True)

        now = utc_now()
        conn.execute(
            """
            UPDATE routine
            SET schema_output_json = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ?
            """,
            (merged_schema_json, now, routine["id"], workspace_id),
        )

        conn.execute(
            """
            UPDATE gold_candidate
            SET used = 1, use_count = use_count + 1, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (now, candidate_id, workspace_id, ctx.tenant_id),
        )

        updated_routine = get_routine(ctx, conn, routine["id"])
        if updated_routine is None:
            return None

        updated_candidate = get_gold_candidate(ctx, conn, candidate_id)
        if updated_candidate is None:
            updated_candidate = candidate

        record_editorial_event(
            ctx,
            conn,
            "gold_candidate",
            candidate_id,
            "applied_to_routine",
            reason=f"Applied learned output to routine {routine['id']}",
        )

        return {
            "candidate": updated_candidate,
            "routine": updated_routine,
        }
