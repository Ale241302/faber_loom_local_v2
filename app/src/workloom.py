"""FaberLoom SL3b: WorkLoom HITL queue helpers."""

from __future__ import annotations

from typing import Any

import sqlite3

from .context import Context
from .db import GOLD_CANDIDATE_COLUMNS, ROUTINE_RUN_COLUMNS, row_to_dict
from .db_adapter import transaction


def assign_workloom_item(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    item_type: str,
    item_id: str,
    assigned_to: str | None,
    urgency: int | None = None,
) -> dict[str, Any]:
    """Assign or reassign a WorkLoom item (routine_run | draft) to a user.

    E2-2 cola compartida: la asignación vive en la fila del item; assigned_to
    en None des-asigna. Fail-closed si el item no pertenece al workspace/tenant.
    """

    if item_type not in {"routine_run", "draft"}:
        raise ValueError("item_type must be 'routine_run' or 'draft'")
    workspace_id = ctx.require_scoped_workspace()
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            f"SELECT id FROM {item_type} WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (item_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        if row is None:
            raise ValueError(f"{item_type} {item_id} not found in workspace")

        sets = ["assigned_to = ?"]
        values: list[Any] = [assigned_to]
        if urgency is not None:
            sets.append("urgency = ?")
            values.append(int(urgency))
        values.append(item_id)
        conn.execute(f"UPDATE {item_type} SET {', '.join(sets)} WHERE id = ?", values)
        result = row_to_dict(
            conn.execute(f"SELECT * FROM {item_type} WHERE id = ?", (item_id,)).fetchone()
        )
    return result


def list_workloom_items(
    ctx: Context,
    conn: sqlite3.Connection,
    gold_limit: int = 50,
) -> dict[str, list[dict[str, Any]]]:
    """Return pending HITL items for the current workspace/tenant.

    Includes:
    - routine_runs with status in (requires_hitl, running, failed)
    - drafts with status in (draft, pending_approval)
    - recent gold_candidates for visibility in the same surface
    """

    workspace_id = ctx.require_scoped_workspace()
    tenant_id = ctx.tenant_id

    with transaction(conn, ctx=ctx):
        run_rows = conn.execute(
            f"""
            SELECT {ROUTINE_RUN_COLUMNS}
            FROM routine_run
            WHERE workspace_id = ? AND tenant_id = ? AND status IN ('requires_hitl', 'running', 'failed')
            ORDER BY urgency DESC, created_at DESC
            """,
            (workspace_id, tenant_id),
        ).fetchall()

        draft_rows = conn.execute(
            """
            SELECT *
            FROM draft
            WHERE workspace_id = ? AND tenant_id = ? AND status IN ('draft', 'pending_approval')
            ORDER BY urgency DESC, created_at DESC
            """,
            (workspace_id, tenant_id),
        ).fetchall()

        gold_rows = conn.execute(
            f"""
            SELECT {GOLD_CANDIDATE_COLUMNS}
            FROM gold_candidate
            WHERE workspace_id = ? AND tenant_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (workspace_id, tenant_id, gold_limit),
        ).fetchall()

    return {
        "routine_runs": [row_to_dict(row) for row in run_rows],
        "drafts": [row_to_dict(row) for row in draft_rows],
        "gold_candidates": [row_to_dict(row) for row in gold_rows],
    }
