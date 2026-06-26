"""SpaceLoom SL3b: WorkLoom HITL queue helpers."""

from __future__ import annotations

from typing import Any

import sqlite3

from .context import Context
from .db import GOLD_CANDIDATE_COLUMNS, ROUTINE_RUN_COLUMNS, row_to_dict


def list_workloom_items(
    ctx: Context,
    conn: sqlite3.Connection,
    gold_limit: int = 50,
) -> dict[str, list[dict[str, Any]]]:
    """Return pending HITL items for the current workspace.

    Includes:
    - routine_runs with status in (requires_hitl, running, failed)
    - drafts with status in (draft, pending_approval)
    - recent gold_candidates for visibility in the same surface
    """

    workspace_id = ctx.require_scoped_workspace()

    run_rows = conn.execute(
        f"""
        SELECT {ROUTINE_RUN_COLUMNS}
        FROM routine_run
        WHERE workspace_id = ? AND status IN ('requires_hitl', 'running', 'failed')
        ORDER BY urgency DESC, created_at DESC
        """,
        (workspace_id,),
    ).fetchall()

    draft_rows = conn.execute(
        """
        SELECT *
        FROM draft
        WHERE workspace_id = ? AND status IN ('draft', 'pending_approval')
        ORDER BY urgency DESC, created_at DESC
        """,
        (workspace_id,),
    ).fetchall()

    gold_rows = conn.execute(
        f"""
        SELECT {GOLD_CANDIDATE_COLUMNS}
        FROM gold_candidate
        WHERE workspace_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (workspace_id, gold_limit),
    ).fetchall()

    return {
        "routine_runs": [row_to_dict(row) for row in run_rows],
        "drafts": [row_to_dict(row) for row in draft_rows],
        "gold_candidates": [row_to_dict(row) for row in gold_rows],
    }
