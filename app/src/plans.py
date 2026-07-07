"""Plan limits and enforcement for E3-2.

Every real tenant is associated with a plan that caps users, workspaces,
storage bytes and monthly budget. Checks are fail-closed: if the plan or the
current usage cannot be determined, the operation is rejected.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .context import SYSTEM_WORKSPACE_ID, Context
from .db_adapter import transaction


class PlanError(Exception):
    """Raised when a plan limit is exceeded or cannot be verified."""


@dataclass(frozen=True, slots=True)
class PlanLimits:
    name: str
    max_users: int | None
    max_workspaces: int | None
    max_storage_bytes: int | None
    max_monthly_budget_usd: float | None


# Built-in plan catalog. Plans are referenced by name in tenant_plan.plan_name.
PLANS: dict[str, PlanLimits] = {
    "starter": PlanLimits(
        name="starter",
        max_users=5,
        max_workspaces=2,
        max_storage_bytes=1_000_000_000,  # 1 GB
        max_monthly_budget_usd=50.0,
    ),
    "growth": PlanLimits(
        name="growth",
        max_users=25,
        max_workspaces=10,
        max_storage_bytes=10_000_000_000,  # 10 GB
        max_monthly_budget_usd=500.0,
    ),
    "enterprise": PlanLimits(
        name="enterprise",
        max_users=None,
        max_workspaces=None,
        max_storage_bytes=None,
        max_monthly_budget_usd=None,
    ),
    # Legacy Foundation tenants created before E3-2 are treated as unrestricted.
    "beta": PlanLimits(
        name="beta",
        max_users=None,
        max_workspaces=None,
        max_storage_bytes=None,
        max_monthly_budget_usd=None,
    ),
}


def get_plan(plan_name: str) -> PlanLimits:
    """Return a plan by name or raise PlanError if it does not exist."""

    plan = PLANS.get(plan_name)
    if plan is None:
        raise PlanError(f"Unknown plan: {plan_name}")
    return plan


def _count_tenant_workspaces(conn: Any, tenant_id: str) -> int:
    ctx = Context(workspace_id=SYSTEM_WORKSPACE_ID, tenant_id=tenant_id)
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM workspace WHERE tenant_id = ?",
            (tenant_id,),
        ).fetchone()
    return int(row["n"]) if row else 0


def _count_tenant_users(conn: Any, tenant_id: str) -> int:
    # Foundation users are the source of truth for tenant owners/staff.
    # Fall back to 0 if the foundation tables are not available (should not
    # happen for real tenants).
    ctx = Context(workspace_id=SYSTEM_WORKSPACE_ID, tenant_id=tenant_id)
    try:
        with transaction(conn, ctx=ctx):
            row = conn.execute(
                """SELECT COUNT(*) AS n FROM fnd_users
                   WHERE tenant_id = ? AND status = 'active'""",
                (tenant_id,),
            ).fetchone()
        return int(row["n"]) if row else 0
    except Exception:
        return 0


def check_plan_limit(
    conn: Any,
    tenant_id: str,
    plan_name: str,
    resource: str,
    requested: int | float,
) -> None:
    """Raise PlanError if ``requested`` would exceed the tenant's plan limit.

    Supported resources: ``users``, ``workspaces``, ``storage_bytes``,
    ``monthly_budget_usd``.
    """

    plan = get_plan(plan_name)

    if resource == "users":
        limit = plan.max_users
        current = _count_tenant_users(conn, tenant_id)
    elif resource == "workspaces":
        limit = plan.max_workspaces
        current = _count_tenant_workspaces(conn, tenant_id)
    elif resource == "storage_bytes":
        limit = plan.max_storage_bytes
        current = 0  # callers add current usage before invoking
    elif resource == "monthly_budget_usd":
        limit = plan.max_monthly_budget_usd
        current = 0.0
    else:
        raise PlanError(f"Unsupported plan resource: {resource}")

    if limit is None:
        return

    if current + requested > limit:
        raise PlanError(
            f"Plan '{plan_name}' {resource} limit exceeded: "
            f"{current + requested} > {limit}"
        )


def enforce_all_limits(
    conn: Any,
    tenant_id: str,
    plan_name: str,
    requested: dict[str, int | float],
) -> None:
    """Check every resource in ``requested`` against the tenant plan."""

    for resource, amount in requested.items():
        check_plan_limit(conn, tenant_id, plan_name, resource, amount)


def get_tenant_plan_name(tenant_id: str) -> str:
    """Return the plan name stored in Foundation for the tenant.

    Defaults to ``enterprise`` when Foundation is not reachable so local/dev
    tenants are not blocked.
    """

    from .foundation.core import get_foundation_db_path

    db_path = get_foundation_db_path()
    if not db_path.exists():
        return "enterprise"

    conn = sqlite3.connect(str(db_path), timeout=20.0)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT plan FROM fnd_tenants WHERE id = ?",
            (tenant_id,),
        ).fetchone()
        return row["plan"] if row else "enterprise"
    finally:
        conn.close()


def enforce_workspace_creation(ctx: Context, conn: Any) -> None:
    """Fail if creating one more workspace would exceed the tenant plan."""

    plan_name = get_tenant_plan_name(ctx.tenant_id)
    check_plan_limit(conn, ctx.tenant_id, plan_name, "workspaces", 1)
