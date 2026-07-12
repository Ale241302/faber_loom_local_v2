"""E3-6 tenant health dashboard.

Aggregated, read-only health metrics for platform administrators and tenant
owners/admins. The endpoint intentionally exposes only rolled-up counts and
costs; no workspace content is included.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from .auth import get_current_user
from .context import SYSTEM_WORKSPACE_ID, Context
from .db import get_db, summarize_tenant_usage_cost, transaction
from .foundation.core import connect as connect_foundation, get_foundation_db_path
from .models import TenantHealthFlagsRead, TenantHealthLimitRead, TenantHealthRead
from .plans import get_plan, get_tenant_plan_name

health_router = APIRouter(tags=["health"])


def _open_foundation() -> sqlite3.Connection:
    """Open the Foundation database for user/session metadata."""

    db_path = get_foundation_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _tenant_context(request: Request, tenant_id: str) -> Context:
    user = getattr(request.state, "user", None) or {}
    return Context(
        workspace_id=SYSTEM_WORKSPACE_ID,
        tenant_id=tenant_id,
        user_id=user.get("user_id") or user.get("sub") or "local",
        actor_id=user.get("actor_id") or user.get("user_id") or user.get("sub") or "local",
        actor_role_at_decision=user.get("role") or "owner",
    )


def _require_tenant_admin(tenant_id: str, user: dict[str, Any]) -> None:
    """Fail unless the user is owner/admin of the tenant or platform_admin."""

    user_tenant = user.get("tenant_id")
    role = (user.get("role") or "").lower()
    roles = {r.lower() for r in (user.get("roles") or [])}
    is_platform_admin = role == "platform_admin" or "platform_admin" in roles
    is_tenant_admin = user_tenant == tenant_id and (
        role in {"owner", "admin"} or {"owner", "admin"} & roles
    )
    if not (is_platform_admin or is_tenant_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner/admin role required for this tenant",
        )


def _require_platform_admin(user: dict[str, Any]) -> None:
    """Fail unless the user has the platform_admin role."""

    role = (user.get("role") or "").lower()
    roles = {r.lower() for r in (user.get("roles") or [])}
    if role != "platform_admin" and "platform_admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires platform_admin role",
        )


def _since_iso(days: int) -> str:
    """Return the ISO timestamp for ``days`` ago."""

    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def _tenant_plan_name(fnd_conn: sqlite3.Connection, tenant_id: str) -> str:
    row = fnd_conn.execute(
        "SELECT plan FROM fnd_tenants WHERE id = ?",
        (tenant_id,),
    ).fetchone()
    return row["plan"] if row else "enterprise"


def _count_tenant_users(fnd_conn: sqlite3.Connection, tenant_id: str) -> int:
    row = fnd_conn.execute(
        """
        SELECT COUNT(*) AS n FROM fnd_users
        WHERE tenant_id = ? AND status IN ('active', 'pending_verification')
        """,
        (tenant_id,),
    ).fetchone()
    return int(row["n"]) if row else 0


def _last_owner_login(fnd_conn: sqlite3.Connection, tenant_id: str) -> str | None:
    row = fnd_conn.execute(
        """
        SELECT MAX(s.last_seen_at) AS last_seen
        FROM fnd_sessions s
        JOIN fnd_user_roles ur ON ur.user_id = s.user_id AND ur.tenant_id = s.tenant_id
        JOIN fnd_roles r ON r.id = ur.role_id
        WHERE s.tenant_id = ?
          AND r.name = 'owner'
          AND s.revoked_at IS NULL
        """,
        (tenant_id,),
    ).fetchone()
    return row["last_seen"] if row and row["last_seen"] else None


def _count_runs(app_conn: Any, tenant_id: str, since: str) -> dict[str, int]:
    ctx = Context(workspace_id=SYSTEM_WORKSPACE_ID, tenant_id=tenant_id)
    with transaction(app_conn, ctx=ctx):
        rows = app_conn.execute(
            """
            SELECT status, COUNT(*) AS n
            FROM routine_run
            WHERE tenant_id = ? AND created_at >= ?
            GROUP BY status
            """,
            (tenant_id, since),
        ).fetchall()
    counts: dict[str, int] = {"total": 0, "successful": 0, "failed": 0}
    for row in rows:
        counts["total"] += int(row["n"])
        if row["status"] == "succeeded":
            counts["successful"] += int(row["n"])
        elif row["status"] == "failed":
            counts["failed"] += int(row["n"])
    return counts


def _count_invoices(app_conn: Any, tenant_id: str) -> dict[str, int]:
    ctx = Context(workspace_id=SYSTEM_WORKSPACE_ID, tenant_id=tenant_id)
    with transaction(app_conn, ctx=ctx):
        rows = app_conn.execute(
            """
            SELECT status, due_date, COUNT(*) AS n
            FROM manual_invoice
            WHERE tenant_id = ?
            GROUP BY status, due_date
            """,
            (tenant_id,),
        ).fetchall()
        open_count = 0
        paid_count = 0
        overdue_count = 0
        today = datetime.now(timezone.utc).date().isoformat()
        for row in rows:
            status = row["status"]
            n = int(row["n"])
            if status in {"draft", "sent"}:
                open_count += n
                due = row["due_date"]
                if due and due < today:
                    overdue_count += n
            elif status == "paid":
                paid_count += n
    return {"open": open_count, "paid": paid_count, "overdue": overdue_count}


def _count_pending_drafts(app_conn: Any, tenant_id: str) -> int:
    ctx = Context(workspace_id=SYSTEM_WORKSPACE_ID, tenant_id=tenant_id)
    with transaction(app_conn, ctx=ctx):
        row = app_conn.execute(
            """
            SELECT COUNT(*) AS n FROM draft
            WHERE tenant_id = ? AND status = 'pending_approval'
            """,
            (tenant_id,),
        ).fetchone()
    return int(row["n"]) if row else 0


def _count_workspaces(app_conn: Any, tenant_id: str) -> int:
    ctx = Context(workspace_id=SYSTEM_WORKSPACE_ID, tenant_id=tenant_id)
    with transaction(app_conn, ctx=ctx):
        row = app_conn.execute(
            "SELECT COUNT(*) AS n FROM workspace WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()
    return int(row["n"]) if row else 0


def _count_agent_metrics(app_conn: Any, tenant_id: str) -> dict[str, Any]:
    """Aggregate living-agent metrics for the tenant health dashboard."""

    ctx = Context(workspace_id=SYSTEM_WORKSPACE_ID, tenant_id=tenant_id)
    since_30d = _since_iso(30)

    with transaction(app_conn, ctx=ctx):
        # workspace_brief: total, fresh, stale (older than 24h or never computed).
        brief_rows = app_conn.execute(
            """
            SELECT computed_at FROM workspace_brief
            WHERE tenant_id = ?
            """,
            (tenant_id,),
        ).fetchall()
        stale_threshold = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
        briefs_total = len(brief_rows)
        briefs_fresh = sum(1 for row in brief_rows if row["computed_at"] and row["computed_at"] >= stale_threshold)
        briefs_stale = briefs_total - briefs_fresh

        # agent_task counts by status.
        task_rows = app_conn.execute(
            """
            SELECT status, COUNT(*) AS n
            FROM agent_task
            WHERE tenant_id = ?
            GROUP BY status
            """,
            (tenant_id,),
        ).fetchall()
        task_counts: dict[str, int] = {
            "planned": 0,
            "running": 0,
            "paused_hitl": 0,
            "completed": 0,
            "failed": 0,
        }
        for row in task_rows:
            status = row["status"]
            n = int(row["n"])
            if status in task_counts:
                task_counts[status] = n
            elif status in ("failed", "killed", "degraded"):
                task_counts["failed"] += n

        # memory_block counts.
        active_row = app_conn.execute(
            """
            SELECT COUNT(*) AS n FROM memory_block
            WHERE tenant_id = ? AND archived_at IS NULL
            """,
            (tenant_id,),
        ).fetchone()
        archived_row = app_conn.execute(
            """
            SELECT COUNT(*) AS n FROM memory_block
            WHERE tenant_id = ? AND archived_at IS NOT NULL
            """,
            (tenant_id,),
        ).fetchone()

        cost_row = app_conn.execute(
            """
            SELECT COALESCE(SUM(cost_usd), 0.0) AS total
            FROM usage_record
            WHERE tenant_id = ? AND provider_slug = 'living_agent' AND created_at >= ?
            """,
            (tenant_id, since_30d),
        ).fetchone()

    return {
        "briefs_total": briefs_total,
        "briefs_stale": briefs_stale,
        "briefs_fresh": briefs_fresh,
        "tasks_pending": task_counts["planned"],
        "tasks_running": task_counts["running"],
        "tasks_paused": task_counts["paused_hitl"],
        "tasks_completed": task_counts["completed"],
        "tasks_failed": task_counts["failed"],
        "memory_blocks_active": int(active_row["n"]) if active_row else 0,
        "memory_blocks_archived": int(archived_row["n"]) if archived_row else 0,
        "cost_living_agent_30d": float(cost_row["total"] if cost_row else 0.0),
    }


def _compute_tenant_health(app_conn: Any, tenant_id: str) -> dict[str, Any]:
    """Aggregate tenant health from the app and Foundation databases."""

    fnd_conn = _open_foundation()
    try:
        plan_name = _tenant_plan_name(fnd_conn, tenant_id)
        try:
            plan = get_plan(plan_name)
        except Exception:
            plan = get_plan("enterprise")

        users = _count_tenant_users(fnd_conn, tenant_id)
        last_owner_login = _last_owner_login(fnd_conn, tenant_id)
    finally:
        fnd_conn.close()

    since_30d = _since_iso(30)
    since_7d = _since_iso(7)

    runs_30d = _count_runs(app_conn, tenant_id, since_30d)
    runs_7d = _count_runs(app_conn, tenant_id, since_7d)

    usage = summarize_tenant_usage_cost(app_conn, tenant_id, since=since_30d)
    budget_remaining: float | None = None
    if plan.max_monthly_budget_usd is not None:
        budget_remaining = plan.max_monthly_budget_usd - usage["total_cost_usd"]

    invoices = _count_invoices(app_conn, tenant_id)
    pending_drafts = _count_pending_drafts(app_conn, tenant_id)
    workspaces = _count_workspaces(app_conn, tenant_id)

    error_rate_30d = 0.0
    if runs_30d["total"] > 0:
        error_rate_30d = round((runs_30d["failed"] / runs_30d["total"]) * 100, 2)

    agent_metrics = _count_agent_metrics(app_conn, tenant_id)

    return {
        "tenant_id": tenant_id,
        "plan": plan_name,
        "limits": {
            "max_users": plan.max_users,
            "max_workspaces": plan.max_workspaces,
            "max_monthly_budget_usd": plan.max_monthly_budget_usd,
        },
        "period_days": 30,
        "runs_30d": runs_30d["total"],
        "successful_runs_30d": runs_30d["successful"],
        "failed_runs_30d": runs_30d["failed"],
        "error_rate_pct": error_rate_30d,
        "runs_7d": runs_7d["total"],
        "successful_runs_7d": runs_7d["successful"],
        "failed_runs_7d": runs_7d["failed"],
        "cost_usd_30d": usage["total_cost_usd"],
        "surcharge_usd_30d": usage["total_surcharge_usd"],
        "budget_remaining_usd": budget_remaining,
        "invoices_open": invoices["open"],
        "invoices_paid": invoices["paid"],
        "invoices_overdue": invoices["overdue"],
        "workspaces": workspaces,
        "users": users,
        "last_owner_login": last_owner_login,
        "flags": {
            "drafts_pending_approval": pending_drafts,
            "invoices_overdue": invoices["overdue"],
        },
        "agent": agent_metrics,
    }


@health_router.get("/admin/tenants/{tenant_id}/health", response_model=TenantHealthRead)
def admin_tenant_health(
    tenant_id: str,
    request: Request,
    app_conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> TenantHealthRead:
    """Platform admin view of a tenant's health dashboard."""

    _require_platform_admin(user)
    return TenantHealthRead(**_compute_tenant_health(app_conn, tenant_id))


@health_router.get("/tenants/{tenant_id}/health", response_model=TenantHealthRead)
def tenant_health(
    tenant_id: str,
    request: Request,
    app_conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> TenantHealthRead:
    """Owner/admin mirror view of the tenant's health dashboard."""

    _require_tenant_admin(tenant_id, user)
    return TenantHealthRead(**_compute_tenant_health(app_conn, tenant_id))
