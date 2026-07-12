"""Step-aware cost ledger for E2-4 auto chains.

Links usage_record rows via chain_id/step_index so a multi-step dispatcher can
be audited end-to-end.
"""

from __future__ import annotations

from typing import Any

from .context import Context
from .db import insert_usage_record, new_id, utc_now
from .db_adapter import transaction


def start_chain(
    ctx: Context,
    conn: Any,
    *,
    chat_id: str | None = None,
    kind: str = "auto",
) -> str:
    """Return a new chain_id without writing a row."""

    return new_id("chn")


def record_step(
    ctx: Context,
    conn: Any,
    *,
    chain_id: str,
    step_index: int,
    result: dict[str, Any],
    chat_id: str | None = None,
    run_id: str | None = None,
    capability: str = "text",
    task_id: str | None = None,
    request_json: dict[str, Any] | None = None,
    response_json: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist one step of a chain as a usage_record."""

    return insert_usage_record(
        ctx,
        conn,
        chat_id=chat_id,
        provider_slug=result.get("provider_slug", "router"),
        model=result.get("model", "unknown"),
        input_tokens=result.get("input_tokens", 0),
        output_tokens=result.get("output_tokens", 0),
        cost_usd=result.get("cost_usd", 0.0),
        duration_ms=result.get("duration_ms", 0),
        status="succeeded" if result.get("status") == "succeeded" else "failed",
        error=result.get("error") if result.get("status") != "succeeded" else None,
        attempts_json=[{"provider": result.get("provider_slug", "router"), "status": result.get("status")}],
        request_json=request_json or {},
        response_json=response_json or {"finish_status": result.get("status")},
        run_id=run_id,
        step_index=step_index,
        chain_id=chain_id,
        capability=capability,
        task_id=task_id,
    )


def sum_chain_cost(
    ctx: Context,
    conn: Any,
    chain_id: str,
) -> float:
    """Sum succeeded step costs for a chain."""

    workspace_id = ctx.require_scoped_workspace()
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT COALESCE(SUM(cost_usd), 0.0) AS total
            FROM usage_record
            WHERE workspace_id = ? AND tenant_id = ? AND chain_id = ? AND status = 'succeeded'
            """,
            (workspace_id, ctx.require_tenant(), chain_id),
        ).fetchone()
    return float(row["total"]) if row and row["total"] is not None else 0.0


def check_chain_budget(
    ctx: Context,
    conn: Any,
    chain_id: str,
    cap: float,
) -> bool:
    """Return True if the chain is still within budget."""

    return sum_chain_cost(ctx, conn, chain_id) < cap


def list_chain_steps(
    ctx: Context,
    conn: Any,
    chain_id: str,
) -> list[dict[str, Any]]:
    """Return all usage records for a chain ordered by step_index."""

    workspace_id = ctx.require_scoped_workspace()
    with transaction(conn, ctx=ctx):
        rows = conn.execute(
            """
            SELECT provider_slug, model, input_tokens, output_tokens, cost_usd,
                   duration_ms, status, step_index, capability, created_at
            FROM usage_record
            WHERE workspace_id = ? AND tenant_id = ? AND chain_id = ?
            ORDER BY step_index ASC, created_at ASC
            """,
            (workspace_id, ctx.require_tenant(), chain_id),
        ).fetchall()
    return [dict(row) for row in rows]
