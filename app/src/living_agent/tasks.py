"""Persistence layer for E4-3 agent tasks and steps."""

from __future__ import annotations

from typing import Any

from ..context import Context
from ..db import new_id, utc_now
from ..db_adapter import transaction


VALID_TASK_STATUSES = {
    "planned",
    "running",
    "paused_hitl",
    "completed",
    "killed",
    "failed",
    "degraded",
}
VALID_STEP_STATUSES = {
    "pending",
    "running",
    "paused_hitl",
    "completed",
    "failed",
    "skipped",
}


def _task_columns() -> str:
    return """
        id, tenant_id, workspace_id, chat_id, plan_id, user_request, status,
        cost_total_usd, budget_cap_usd, est_cost_usd, kill_requested_at,
        kill_requested_by, hitl_step_id, hitl_token, output_text, output_ref,
        actor_id, actor_role_at_decision, routine_version, skill_version,
        schema_version, source_version, approved_by, created_at, updated_at
    """


def _step_columns() -> str:
    return """
        id, tenant_id, workspace_id, task_id, step_index, step_id, capability, task, prompt, provider_slug,
        model, input_ref, output_ref, evidence_id, cost_usd, input_tokens,
        output_tokens, duration_ms, status, status_reason, actor_id,
        actor_role_at_decision, routine_version, skill_version, schema_version,
        source_version, approved_by, created_at, updated_at
    """


def _row_to_task(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "tenant_id": row["tenant_id"],
        "workspace_id": row["workspace_id"],
        "chat_id": row["chat_id"],
        "plan_id": row["plan_id"],
        "user_request": row["user_request"],
        "status": row["status"],
        "cost_total_usd": float(row["cost_total_usd"] or 0.0),
        "budget_cap_usd": row["budget_cap_usd"],
        "est_cost_usd": row["est_cost_usd"],
        "kill_requested_at": row["kill_requested_at"],
        "kill_requested_by": row["kill_requested_by"],
        "hitl_step_id": row["hitl_step_id"],
        "hitl_token": row["hitl_token"],
        "output_text": row["output_text"],
        "output_ref": row["output_ref"],
        "actor_id": row["actor_id"],
        "actor_role_at_decision": row["actor_role_at_decision"],
        "routine_version": row["routine_version"],
        "skill_version": row["skill_version"],
        "schema_version": row["schema_version"],
        "source_version": row["source_version"],
        "approved_by": row["approved_by"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_step(row: Any) -> dict[str, Any]:
    return {
        "id": row["id"],
        "tenant_id": row["tenant_id"],
        "workspace_id": row["workspace_id"],
        "task_id": row["task_id"],
        "step_index": row["step_index"],
        "step_id": row["step_id"],
        "capability": row["capability"],
        "task": row["task"],
        "prompt": row["prompt"],
        "provider_slug": row["provider_slug"],
        "model": row["model"],
        "input_ref": row["input_ref"],
        "output_ref": row["output_ref"],
        "evidence_id": row["evidence_id"],
        "cost_usd": float(row["cost_usd"] or 0.0),
        "input_tokens": row["input_tokens"] or 0,
        "output_tokens": row["output_tokens"] or 0,
        "duration_ms": row["duration_ms"] or 0,
        "status": row["status"],
        "status_reason": row["status_reason"],
        "actor_id": row["actor_id"],
        "actor_role_at_decision": row["actor_role_at_decision"],
        "routine_version": row["routine_version"],
        "skill_version": row["skill_version"],
        "schema_version": row["schema_version"],
        "source_version": row["source_version"],
        "approved_by": row["approved_by"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def create_task(
    ctx: Context,
    conn: Any,
    *,
    workspace_id: str,
    chat_id: str | None,
    plan_id: str | None,
    user_request: str,
    budget_cap_usd: float | None,
    est_cost_usd: float | None,
    status: str = "planned",
) -> dict[str, Any]:
    if status not in VALID_TASK_STATUSES:
        raise ValueError(f"Invalid task status: {status}")

    task_id = new_id("atask")
    now = utc_now()
    with transaction(conn, ctx=ctx):
        conn.execute(
            f"""
            INSERT INTO agent_task (
                id, tenant_id, workspace_id, chat_id, plan_id, user_request, status,
                cost_total_usd, budget_cap_usd, est_cost_usd, kill_requested_at,
                kill_requested_by, hitl_step_id, hitl_token, output_text, output_ref,
                actor_id, actor_role_at_decision, routine_version, skill_version,
                schema_version, source_version, approved_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                ctx.require_tenant(),
                workspace_id,
                chat_id,
                plan_id,
                user_request,
                status,
                0.0,
                budget_cap_usd,
                est_cost_usd,
                None,
                None,
                None,
                None,
                None,
                None,
                ctx.actor_id,
                ctx.actor_role_at_decision,
                None,
                None,
                46,
                "v1",
                None,
                now,
                now,
            ),
        )
        row = conn.execute(
            f"SELECT {_task_columns()} FROM agent_task WHERE id = ?",
            (task_id,),
        ).fetchone()
        assert row is not None
        return _row_to_task(row)


def create_task_step(
    ctx: Context,
    conn: Any,
    *,
    task_id: str,
    step_index: int,
    step_id: str,
    capability: str,
    task: str | None,
    prompt: str | None,
    provider_slug: str | None,
    model: str | None,
    input_ref: str | None = None,
    status: str = "pending",
) -> dict[str, Any]:
    if status not in VALID_STEP_STATUSES:
        raise ValueError(f"Invalid step status: {status}")

    step_db_id = new_id("astep")
    now = utc_now()
    workspace_id = ctx.require_scoped_workspace()
    tenant_id = ctx.require_tenant()
    with transaction(conn, ctx=ctx):
        conn.execute(
            f"""
            INSERT INTO agent_task_step (
                id, tenant_id, workspace_id, task_id, step_index, step_id, capability, task, prompt, provider_slug,
                model, input_ref, output_ref, evidence_id, cost_usd, input_tokens,
                output_tokens, duration_ms, status, status_reason, actor_id,
                actor_role_at_decision, routine_version, skill_version, schema_version,
                source_version, approved_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                step_db_id,
                tenant_id,
                workspace_id,
                task_id,
                step_index,
                step_id,
                capability,
                task,
                prompt,
                provider_slug,
                model,
                input_ref,
                None,
                None,
                0.0,
                0,
                0,
                0,
                status,
                None,
                ctx.actor_id,
                ctx.actor_role_at_decision,
                None,
                None,
                46,
                "v1",
                None,
                now,
                now,
            ),
        )
        row = conn.execute(
            f"SELECT {_step_columns()} FROM agent_task_step WHERE id = ?",
            (step_db_id,),
        ).fetchone()
        assert row is not None
        return _row_to_step(row)


def transition_task(
    ctx: Context,
    conn: Any,
    task_id: str,
    new_status: str,
    *,
    updates: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if new_status not in VALID_TASK_STATUSES:
        raise ValueError(f"Invalid task status: {new_status}")

    allowed: dict[str, set[str]] = {
        "planned": {"running", "killed", "failed"},
        "running": {"paused_hitl", "completed", "killed", "failed", "degraded"},
        "paused_hitl": {"running", "killed", "failed", "completed"},
        "completed": set(),
        "killed": set(),
        "failed": set(),
        "degraded": set(),
    }
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            "SELECT status FROM agent_task WHERE id = ? AND tenant_id = ? AND workspace_id = ?",
            (task_id, ctx.require_tenant(), ctx.require_scoped_workspace()),
        ).fetchone()
        if row is None:
            raise ValueError("Task not found in current workspace")
        current = row["status"]
        if new_status not in allowed.get(current, set()):
            # Allow idempotent same-status updates for metadata fixes.
            if new_status != current:
                raise ValueError(f"Invalid task transition: {current} -> {new_status}")

        set_clauses = ["status = ?", "updated_at = ?"]
        params: list[Any] = [new_status, utc_now()]
        for key, value in (updates or {}).items():
            if key in {
                "cost_total_usd",
                "budget_cap_usd",
                "est_cost_usd",
                "kill_requested_at",
                "kill_requested_by",
                "hitl_step_id",
                "hitl_token",
                "output_text",
                "output_ref",
                "approved_by",
            }:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        params.append(task_id)
        conn.execute(
            f"UPDATE agent_task SET {', '.join(set_clauses)} WHERE id = ?",
            params,
        )
        row = conn.execute(
            f"SELECT {_task_columns()} FROM agent_task WHERE id = ?",
            (task_id,),
        ).fetchone()
        assert row is not None
        return _row_to_task(row)


def transition_step(
    ctx: Context,
    conn: Any,
    step_id: str,
    new_status: str,
    *,
    updates: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if new_status not in VALID_STEP_STATUSES:
        raise ValueError(f"Invalid step status: {new_status}")

    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT s.status
            FROM agent_task_step s
            JOIN agent_task t ON t.id = s.task_id
            WHERE s.id = ? AND t.tenant_id = ? AND t.workspace_id = ?
            """,
            (step_id, ctx.require_tenant(), ctx.require_scoped_workspace()),
        ).fetchone()
        if row is None:
            raise ValueError("Step not found in current workspace")

        set_clauses = ["status = ?", "updated_at = ?"]
        params: list[Any] = [new_status, utc_now()]
        for key, value in (updates or {}).items():
            if key in {
                "provider_slug",
                "model",
                "input_ref",
                "output_ref",
                "evidence_id",
                "cost_usd",
                "input_tokens",
                "output_tokens",
                "duration_ms",
                "status_reason",
                "approved_by",
            }:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        params.append(step_id)
        conn.execute(
            f"UPDATE agent_task_step SET {', '.join(set_clauses)} WHERE id = ?",
            params,
        )
        row = conn.execute(
            f"SELECT {_step_columns()} FROM agent_task_step WHERE id = ?",
            (step_id,),
        ).fetchone()
        assert row is not None
        return _row_to_step(row)


def get_task(
    ctx: Context,
    conn: Any,
    task_id: str,
    *,
    include_steps: bool = True,
) -> dict[str, Any] | None:
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            f"""
            SELECT {_task_columns()}
            FROM agent_task
            WHERE id = ? AND tenant_id = ? AND workspace_id = ?
            """,
            (task_id, ctx.require_tenant(), ctx.require_scoped_workspace()),
        ).fetchone()
        if row is None:
            return None
        task = _row_to_task(row)
        if include_steps:
            step_rows = conn.execute(
                f"""
                SELECT {_step_columns()}
                FROM agent_task_step
                WHERE task_id = ?
                ORDER BY step_index ASC, created_at ASC
                """,
                (task_id,),
            ).fetchall()
            task["steps"] = [_row_to_step(r) for r in step_rows]
        return task


def list_tasks(
    ctx: Context,
    conn: Any,
    *,
    workspace_id: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    workspace_id = workspace_id or ctx.require_scoped_workspace()
    params: list[Any] = [ctx.require_tenant(), workspace_id]
    where = "tenant_id = ? AND workspace_id = ?"
    if status is not None:
        where += " AND status = ?"
        params.append(status)
    with transaction(conn, ctx=ctx):
        rows = conn.execute(
            f"""
            SELECT {_task_columns()}
            FROM agent_task
            WHERE {where}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()
        return [_row_to_task(r) for r in rows]


def is_task_killed(
    ctx: Context,
    conn: Any,
    task_id: str,
) -> bool:
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            "SELECT status FROM agent_task WHERE id = ? AND tenant_id = ? AND workspace_id = ?",
            (task_id, ctx.require_tenant(), ctx.require_scoped_workspace()),
        ).fetchone()
        if row is None:
            raise ValueError("Task not found")
        return row["status"] in {"killed", "failed", "completed", "degraded"}


def refresh_task_cost(
    ctx: Context,
    conn: Any,
    task_id: str,
) -> float:
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT COALESCE(SUM(cost_usd), 0.0) AS total
            FROM usage_record
            WHERE tenant_id = ? AND workspace_id = ? AND task_id = ? AND status = 'succeeded'
            """,
            (ctx.require_tenant(), ctx.require_scoped_workspace(), task_id),
        ).fetchone()
        total = float(row["total"] if row and row["total"] is not None else 0.0)
        conn.execute(
            "UPDATE agent_task SET cost_total_usd = ?, updated_at = ? WHERE id = ?",
            (total, utc_now(), task_id),
        )
        return total
