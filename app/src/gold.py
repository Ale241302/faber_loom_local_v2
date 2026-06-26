"""SpaceLoom SL3b: gold loop helpers for low-edit routine runs."""

from __future__ import annotations

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


def list_gold_candidates(
    ctx: Context,
    conn: sqlite3.Connection,
    routine_id: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return gold candidate rows for the current workspace.

    By default returns all candidates (approved or not). Pass routine_id to
    filter by routine.
    """

    workspace_id = ctx.require_scoped_workspace()
    params: list[Any] = [workspace_id]
    sql = f"""
        SELECT {GOLD_CANDIDATE_COLUMNS}
        FROM gold_candidate
        WHERE workspace_id = ?
    """
    if routine_id is not None:
        sql += " AND routine_id = ?"
        params.append(routine_id)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(row) for row in rows]


def promote_gold_candidate(
    ctx: Context,
    conn: sqlite3.Connection,
    candidate_id: str,
    learned_output_json: dict[str, Any],
    approved_by: str | None = None,
) -> dict[str, Any] | None:
    """Promote a gold candidate with the learned/canonized output."""

    workspace_id = ctx.require_scoped_workspace()
    approved_by = approved_by or ctx.resolved_actor_id()
    now = utc_now()

    cursor = conn.execute(
        """
        UPDATE gold_candidate
        SET learned_output_json = ?, approved = 1, approved_by = ?, updated_at = ?
        WHERE id = ? AND workspace_id = ?
        """,
        (
            json.dumps(learned_output_json, ensure_ascii=False, sort_keys=True),
            approved_by,
            now,
            candidate_id,
            workspace_id,
        ),
    )
    if cursor.rowcount == 0:
        return None

    row = conn.execute(
        f"""
        SELECT {GOLD_CANDIDATE_COLUMNS}
        FROM gold_candidate
        WHERE id = ? AND workspace_id = ?
        """,
        (candidate_id, workspace_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def apply_gold_to_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    candidate_id: str,
) -> dict[str, Any] | None:
    """Apply a promoted gold candidate's learned output to its parent routine.

    Performs a shallow merge of learned_output_json into the routine's
    schema_output_json, marks the candidate as used, and records an editorial
    event so the gold loop is auditable.
    """

    workspace_id = ctx.require_scoped_workspace()

    with transaction(conn):
        row = conn.execute(
            f"""
            SELECT {GOLD_CANDIDATE_COLUMNS}
            FROM gold_candidate
            WHERE id = ? AND workspace_id = ?
            """,
            (candidate_id, workspace_id),
        ).fetchone()
        if row is None:
            return None

        candidate = row_to_dict(row)
        if candidate.get("approved") != 1:
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
            SET used = 1, updated_at = ?
            WHERE id = ? AND workspace_id = ?
            """,
            (now, candidate_id, workspace_id),
        )

        updated_routine = get_routine(ctx, conn, routine["id"])
        if updated_routine is None:
            return None

        candidate_row = conn.execute(
            f"""
            SELECT {GOLD_CANDIDATE_COLUMNS}
            FROM gold_candidate
            WHERE id = ? AND workspace_id = ?
            """,
            (candidate_id, workspace_id),
        ).fetchone()
        updated_candidate = row_to_dict(candidate_row) if candidate_row else candidate

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
