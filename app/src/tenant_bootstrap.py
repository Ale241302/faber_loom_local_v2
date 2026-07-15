"""Programmatic bootstrap of an approved tenant.

This module isolates the seeding logic so both platform_admin manual approval
and signup auto-approval can reuse the same bootstrap without creating a
module-level circular import with auth.py.
"""

from __future__ import annotations

import json
from typing import Any

from .ambient import seed_ambient_config
from .context import SYSTEM_WORKSPACE_ID, Context
from .db import create_workspace, db_session, seed_default_archetypes, seed_routing_presets
from .db_adapter import transaction
from .entity_identity import create_identity
from .models import WorkspaceCreate
from .plans import PLANS


def _first_owner_id(fnd_conn: Any, tenant_id: str) -> str | None:
    """Return the first owner user_id for a tenant, regardless of status."""

    row = fnd_conn.execute(
        """
        SELECT u.id FROM fnd_users u
        JOIN fnd_user_roles ur ON ur.user_id = u.id AND ur.tenant_id = u.tenant_id
        JOIN fnd_roles r ON r.id = ur.role_id
        WHERE u.tenant_id = ? AND r.name = 'owner'
        ORDER BY u.created_at ASC LIMIT 1
        """,
        (tenant_id,),
    ).fetchone()
    return row["id"] if row else None


def bootstrap_approved_tenant(
    tenant_id: str,
    tenant_name: str,
    tenant_slug: str,
    plan_name: str,
    *,
    owner_user_id: str | None = None,
    foundation_conn: Any | None = None,
    approved_by: str = "system",
) -> dict[str, Any]:
    """Seed an approved tenant with its first workspace, default settings and identity.

    This is the programmatic equivalent of the MWT bootstrap seed
    (SPEC_FB_TENANT_BOOTSTRAP_SEED_v1). It runs inside the app DB, which may be
    SQLite or Postgres depending on the runtime engine.
    """

    from .foundation.core import audit_log, connect as connect_foundation, new_id, utcnow

    plan = PLANS.get(plan_name) or PLANS["enterprise"]
    monthly_budget = (
        plan.max_monthly_budget_usd if plan.max_monthly_budget_usd is not None else 50.0
    )

    owner_id = owner_user_id
    close_fnd = False
    if owner_id is None:
        if foundation_conn is None:
            foundation_conn = connect_foundation()
            close_fnd = True
        owner_id = _first_owner_id(foundation_conn, tenant_id)

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

            # E4-4: chat general del tenant as a system workspace.
            general_ws = create_workspace(
                bootstrap_ctx,
                app_conn,
                WorkspaceCreate(
                    name="Chat general",
                    slug="general",
                    kind="tenant_general",
                ),
            )
            general_workspace_id = general_ws["id"]

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

            seed_ctx = Context(
                workspace_id=SYSTEM_WORKSPACE_ID,
                tenant_id=tenant_id,
                user_id="system",
                actor_id="system",
                actor_role_at_decision="platform_admin",
            )
            seed_routing_presets(seed_ctx, app_conn, created_by="system")
            seed_default_archetypes(seed_ctx, app_conn, preset_id="mi-preset", created_by="system")

            # E4-7: create a default entity identity for the tenant.
            if owner_id is not None:
                create_identity(
                    app_conn,
                    tenant_id,
                    name=tenant_name,
                    slug=tenant_slug,
                    owner_user_id=owner_id,
                    timestamp=now,
                    actor_role="system",
                )

    if close_fnd:
        foundation_conn.close()

    if approved_by != "system":
        # Audit bootstrap when triggered by an explicit admin action.
        from .foundation.core import connect as connect_foundation

        fnd_conn = foundation_conn if foundation_conn is not None and not close_fnd else connect_foundation()
        try:
            audit_log(
                fnd_conn,
                tenant_id,
                "tenant.bootstrapped",
                actor_id=approved_by,
                actor_email="",
                resource_type="tenant",
                resource_id=tenant_id,
                payload={"workspace_id": workspace_id, "general_workspace_id": general_workspace_id},
            )
            fnd_conn.commit()
        finally:
            if close_fnd or foundation_conn is None:
                fnd_conn.close()

    return {
        "tenant_id": tenant_id,
        "workspace_id": workspace_id,
        "general_workspace_id": general_workspace_id,
    }
