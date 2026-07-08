"""E3-2 platform_admin endpoints for tenant lifecycle and metrics.

All destructive tenant lifecycle actions require a deterministic confirmation
token echoed back by the caller (HITL gate).

These endpoints are intentionally separate from workspace-scoped API routes:
platform_admin manages Foundation tenants across workspaces and must never
access tenant content. All state changes are audited in Foundation's immutable
audit chain (fnd_audit_log), which is the correct seam for Foundation tenant
lifecycle events.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from .ambient import seed_ambient_config
from .auth import get_current_user
from .context import SYSTEM_WORKSPACE_ID, Context
from .db import create_workspace, db_session, get_db, transaction
from .models import WorkspaceCreate
from .foundation.core import (
    audit_log,
    connect as connect_foundation,
    get_foundation_db_path,
    new_id,
    seed_system_roles,
    to_dict,
    utcnow,
)

platform_admin_router = APIRouter(
    prefix="/admin",
    tags=["platform-admin"],
    dependencies=[Depends(get_current_user)],
)


class SuspendRequest(BaseModel):
    reason: str = Field(default="", max_length=500)
    confirmation_token: str | None = Field(default=None, max_length=64)


class ApproveRequest(BaseModel):
    reason: str = Field(default="", max_length=500)
    confirmation_token: str | None = Field(default=None, max_length=64)


class UpdatePlanRequest(BaseModel):
    plan: str = Field(min_length=1, max_length=50)


def _confirmation_token(resource_id: str) -> str:
    """Deterministic token the UI must echo before destructive lifecycle actions."""
    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def _require_confirmation(resource_id: str, confirmation_token: str | None) -> None:
    """Raise 409 if the caller has not echoed the required confirmation token."""

    expected = _confirmation_token(resource_id)
    if confirmation_token != expected:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Action requires explicit confirmation; provide confirmation_token={expected}",
        )


def _require_platform_admin(request: Request) -> dict[str, Any]:
    """Return the authenticated user only if it has the platform_admin role."""

    user = getattr(request.state, "user", None) or request.scope.get("user")
    if user is None:
        # get_current_user dependency already ran; this is defensive.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    roles = user.get("roles") or []
    if user.get("role") == "platform_admin" or "platform_admin" in roles:
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Requires platform_admin role",
    )


def _normalize_tenant_status(raw: str) -> str:
    """Map Foundation tenant statuses to the public lifecycle surface."""

    if raw in {"pending_approval", "provisioning"}:
        return "pending"
    if raw in {"active", "suspended"}:
        return raw
    return "pending"


def _tenant_owner_email(conn: sqlite3.Connection, tenant_id: str) -> str | None:
    """Return the email of the first active owner for display purposes."""

    row = conn.execute(
        """
        SELECT u.email FROM fnd_users u
        JOIN fnd_user_roles ur ON ur.user_id = u.id AND ur.tenant_id = u.tenant_id
        JOIN fnd_roles r ON r.id = ur.role_id
        WHERE u.tenant_id = ? AND u.status = 'active' AND r.name = 'owner'
        ORDER BY u.created_at ASC LIMIT 1
        """,
        (tenant_id,),
    ).fetchone()
    return row["email"] if row else None


def _tenant_payload(conn: sqlite3.Connection, tenant: sqlite3.Row) -> dict[str, Any]:
    """Serialize a tenant row for the admin list response."""

    return {
        "id": tenant["id"],
        "name": tenant["name"],
        "slug": tenant["slug"],
        "status": _normalize_tenant_status(tenant["status"]),
        "raw_status": tenant["status"],
        "plan": tenant["plan"],
        "owner_email": _tenant_owner_email(conn, tenant["id"]),
        "created_at": tenant["created_at"],
        "activated_at": tenant["activated_at"],
        "approved_by": tenant["approved_by"],
        "suspended_by": tenant["suspended_by"],
        "suspension_reason": tenant["suspension_reason"],
    }


def _open_foundation() -> sqlite3.Connection:
    """Open the Foundation database for direct inspection/manipulation.

    In the local-first stack Foundation is always SQLite; this helper keeps the
    admin module self-contained while the rest of the app uses the configured
    engine (sqlite or postgres) for application data.
    """

    db_path = get_foundation_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@platform_admin_router.get("/tenants")
def list_tenants(
    request: Request,
    user: dict[str, Any] = Depends(_require_platform_admin),
) -> list[dict[str, Any]]:
    """List all Foundation tenants with normalized lifecycle status."""

    conn = _open_foundation()
    try:
        rows = conn.execute(
            "SELECT * FROM fnd_tenants ORDER BY created_at DESC"
        ).fetchall()
        return [_tenant_payload(conn, row) for row in rows]
    finally:
        conn.close()


@platform_admin_router.post("/tenants/{tenant_id}/approve")
def approve_tenant(
    tenant_id: str,
    request: Request,
    body: ApproveRequest | None = None,
    user: dict[str, Any] = Depends(_require_platform_admin),
) -> dict[str, Any]:
    """Approve a pending tenant and activate it."""

    body = body or ApproveRequest()
    admin_id = user.get("user_id") or user.get("sub") or "unknown"
    admin_email = user.get("sub") or admin_id

    conn = _open_foundation()
    try:
        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE id = ?", (tenant_id,)
        ).fetchone()
        if tenant is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant not found")

        _require_confirmation(tenant_id, body.confirmation_token)

        if tenant["status"] not in {"pending_approval", "provisioning"}:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Tenant cannot be approved from status '{tenant['status']}'",
            )

        now = utcnow()
        conn.execute(
            """
            UPDATE fnd_tenants
            SET status = 'active',
                activated_at = ?,
                approved_by = ?,
                suspended_by = NULL,
                suspension_reason = NULL
            WHERE id = ?
            """,
            (now, admin_id, tenant_id),
        )

        audit_log(
            conn,
            tenant_id,
            "tenant.approved",
            actor_id=admin_id,
            actor_email=admin_email,
            resource_type="tenant",
            resource_id=tenant_id,
            payload={"reason": body.reason},
        )
        conn.commit()

        # Bootstrap the approved tenant with a workspace and default settings.
        _bootstrap_approved_tenant(
            tenant_id=tenant_id,
            tenant_name=tenant["name"],
            tenant_slug=tenant["slug"],
            plan_name=tenant["plan"],
        )

        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE id = ?", (tenant_id,)
        ).fetchone()
        return _tenant_payload(conn, tenant)
    finally:
        conn.close()


@platform_admin_router.post("/tenants/{tenant_id}/suspend")
def suspend_tenant(
    tenant_id: str,
    request: Request,
    body: SuspendRequest | None = None,
    user: dict[str, Any] = Depends(_require_platform_admin),
) -> dict[str, Any]:
    """Suspend an active tenant."""

    body = body or SuspendRequest()
    admin_id = user.get("user_id") or user.get("sub") or "unknown"
    admin_email = user.get("sub") or admin_id

    conn = _open_foundation()
    try:
        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE id = ?", (tenant_id,)
        ).fetchone()
        if tenant is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant not found")

        _require_confirmation(tenant_id, body.confirmation_token)

        if tenant["status"] != "active":
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Tenant cannot be suspended from status '{tenant['status']}'",
            )

        conn.execute(
            """
            UPDATE fnd_tenants
            SET status = 'suspended',
                suspended_by = ?,
                suspension_reason = ?
            WHERE id = ?
            """,
            (admin_id, body.reason, tenant_id),
        )

        audit_log(
            conn,
            tenant_id,
            "tenant.suspended",
            actor_id=admin_id,
            actor_email=admin_email,
            resource_type="tenant",
            resource_id=tenant_id,
            payload={"reason": body.reason},
        )
        conn.commit()

        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE id = ?", (tenant_id,)
        ).fetchone()
        return _tenant_payload(conn, tenant)
    finally:
        conn.close()


def _compute_metrics(
    fnd_conn: sqlite3.Connection,
    app_conn: Any,
) -> dict[str, Any]:
    """Aggregate platform-level metrics across Foundation and app DBs."""

    # Tenant counts by normalized status.
    rows = fnd_conn.execute(
        "SELECT status, COUNT(*) AS n FROM fnd_tenants GROUP BY status"
    ).fetchall()
    by_status: dict[str, int] = {"pending": 0, "active": 0, "suspended": 0}
    pending_approvals = 0
    for row in rows:
        normalized = _normalize_tenant_status(row["status"])
        by_status[normalized] = by_status.get(normalized, 0) + row["n"]
        if row["status"] == "pending_approval":
            pending_approvals += row["n"]

    total_tenants = sum(by_status.values())

    # Recent signups (last 30 days) from Foundation.
    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    row = fnd_conn.execute(
        "SELECT COUNT(*) AS n FROM fnd_tenants WHERE created_at > ?",
        (since,),
    ).fetchone()
    recent_signups = row["n"] if row else 0

    # Total users from Foundation (active or pending verification).
    row = fnd_conn.execute(
        "SELECT COUNT(*) AS n FROM fnd_users WHERE status IN ('active', 'pending_verification')"
    ).fetchone()
    total_users = row["n"] if row else 0

    # Total workspaces from the app DB.
    row = app_conn.execute("SELECT COUNT(*) AS n FROM workspace").fetchone()
    total_workspaces = row["n"] if row else 0

    # Total cost from the app DB usage records (cross-tenant platform view).
    try:
        row = app_conn.execute(
            "SELECT SUM(cost_usd) AS total FROM usage_record"
        ).fetchone()
        total_cost_usd = float(row["total"] or 0.0)
    except Exception:
        total_cost_usd = 0.0

    return {
        "total_tenants": total_tenants,
        "by_status": by_status,
        "pending_approvals": pending_approvals,
        "recent_signups_30d": recent_signups,
        "total_users": total_users,
        "total_workspaces": total_workspaces,
        "total_cost_usd": total_cost_usd,
        # Frontend compatibility aliases.
        "healthy_tenants": by_status["active"],
    }


@platform_admin_router.get("/metrics")
def get_metrics(
    request: Request,
    app_conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(_require_platform_admin),
) -> dict[str, Any]:
    """Return aggregated platform metrics."""

    fnd_conn = _open_foundation()
    try:
        return _compute_metrics(fnd_conn, app_conn)
    finally:
        fnd_conn.close()


@platform_admin_router.get("/tenants/metrics")
def get_tenants_metrics(
    request: Request,
    app_conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(_require_platform_admin),
) -> dict[str, Any]:
    """Frontend compatibility alias for /api/admin/metrics."""

    return get_metrics(request, app_conn, user)


@platform_admin_router.patch("/tenants/{tenant_id}/plan")
def update_tenant_plan(
    tenant_id: str,
    body: UpdatePlanRequest,
    request: Request,
    user: dict[str, Any] = Depends(_require_platform_admin),
) -> dict[str, Any]:
    """Change the plan assigned to a tenant."""

    from .plans import PLANS

    plan_name = body.plan.strip().lower()
    if plan_name not in PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown plan: {plan_name}",
        )

    admin_id = user.get("user_id") or user.get("sub") or "unknown"
    admin_email = user.get("sub") or admin_id

    conn = _open_foundation()
    try:
        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE id = ?", (tenant_id,)
        ).fetchone()
        if tenant is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Tenant not found")

        previous_plan = tenant["plan"]
        conn.execute(
            "UPDATE fnd_tenants SET plan = ? WHERE id = ?",
            (plan_name, tenant_id),
        )
        audit_log(
            conn,
            tenant_id,
            "tenant.plan_changed",
            actor_id=admin_id,
            actor_email=admin_email,
            resource_type="tenant",
            resource_id=tenant_id,
            payload={"previous_plan": previous_plan, "new_plan": plan_name},
        )
        conn.commit()

        tenant = conn.execute(
            "SELECT * FROM fnd_tenants WHERE id = ?", (tenant_id,)
        ).fetchone()
        return _tenant_payload(conn, tenant)
    finally:
        conn.close()


def _bootstrap_approved_tenant(
    tenant_id: str,
    tenant_name: str,
    tenant_slug: str,
    plan_name: str,
) -> dict[str, Any]:
    """Seed an approved tenant with its first workspace and default settings.

    This is the programatic equivalent of the MWT bootstrap seed
    (SPEC_FB_TENANT_BOOTSTRAP_SEED_v1). It runs inside the app DB, which may be
    SQLite or Postgres depending on the runtime engine.
    """

    from .plans import PLANS

    plan = PLANS.get(plan_name) or PLANS["enterprise"]
    monthly_budget = plan.max_monthly_budget_usd if plan.max_monthly_budget_usd is not None else 50.0

    with db_session() as app_conn:
        bootstrap_ctx = Context(
            workspace_id=SYSTEM_WORKSPACE_ID,
            tenant_id=tenant_id,
            user_id="system",
            actor_id="system",
            actor_role_at_decision="platform_admin",
        )
        with transaction(app_conn, ctx=bootstrap_ctx):
            workspace = create_workspace(
                bootstrap_ctx,
                app_conn,
                WorkspaceCreate(
                    name=f"{tenant_name} Workspace",
                    slug=tenant_slug,
                ),
            )
            workspace_id = workspace["id"]

            now = utcnow()
            tenant_defaults: list[tuple[str, Any]] = [
                ("ambient.enabled", False),
                ("routing.auto_dispatch", False),
                ("routing.max_budget_usd", 2.0),
                ("routing.max_steps", 4),
                ("tenant.plan.monthly_budget_usd", monthly_budget),
            ]
            for key, value in tenant_defaults:
                app_conn.execute(
                    """
                    INSERT INTO tenant_settings (tenant_id, key, value_json, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(tenant_id, key) DO UPDATE SET
                        value_json = excluded.value_json,
                        updated_at = excluded.updated_at
                    """,
                    (tenant_id, key, json.dumps(value, ensure_ascii=False, sort_keys=True), now),
                )

            app_conn.execute(
                """
                INSERT INTO workspace_routing_policy
                    (workspace_id, tenant_id, provider_allowlist_json, model_allowlist_json,
                     budget_cap_usd, auto_mode_enabled, max_auto_steps, require_local_only, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workspace_id) DO UPDATE SET
                    provider_allowlist_json = excluded.provider_allowlist_json,
                    model_allowlist_json = excluded.model_allowlist_json,
                    budget_cap_usd = excluded.budget_cap_usd,
                    auto_mode_enabled = excluded.auto_mode_enabled,
                    max_auto_steps = excluded.max_auto_steps,
                    require_local_only = excluded.require_local_only,
                    updated_at = excluded.updated_at
                """,
                (workspace_id, tenant_id, "[]", "{}", 2.0, 0, 4, 0, now),
            )

            seed_ambient_config(app_conn, tenant_id)

    return {"tenant_id": tenant_id, "workspace_id": workspace_id}
