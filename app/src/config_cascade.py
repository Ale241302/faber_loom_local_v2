"""Configuration cascade resolver for E3-2.

Resolution order: user setting > workspace setting > tenant setting > default.
Tenant-level settings are stored in ``tenant_settings`` (created in E3-2 DB
migrations). Workspace-level settings reuse the existing
``workspace_smtp_config`` / ``workspace_routing_policy`` / ``workspace_model_catalog``
tables. User-level settings are resolved from the Foundation user profile when
available.
"""

from __future__ import annotations

from typing import Any

from .db_adapter import transaction
from .context import Context


class ConfigCascadeError(Exception):
    """Raised when a requested setting cannot be resolved."""


DEFAULTS: dict[str, Any] = {
    "smtp.use_ssl": True,
    "smtp.port": 465,
    "routing.auto_dispatch": False,
    "routing.max_budget_usd": 2.0,
    "routing.max_steps": 4,
    "routing.byo_mode": "hibrido",
    "model.default": "openai/gpt-4o-mini",
    "whatsapp_inbound.enabled": False,
}


def _workspace_config(conn: Any, ctx: Context, key: str) -> Any:
    """Look up a workspace-scoped setting in the existing config tables."""

    if key.startswith("smtp."):
        row = conn.execute(
            "SELECT * FROM workspace_smtp_config WHERE workspace_id = ?",
            (ctx.workspace_id,),
        ).fetchone()
        if row is None:
            return None
        mapping = {
            "smtp.host": row["host"],
            "smtp.port": row["port"],
            "smtp.use_ssl": row["use_ssl"],
            "smtp.username": row["username"],
        }
        return mapping.get(key)

    if key.startswith("routing."):
        row = conn.execute(
            "SELECT * FROM workspace_routing_policy WHERE workspace_id = ?",
            (ctx.workspace_id,),
        ).fetchone()
        if row is None:
            return None
        mapping = {
            "routing.auto_dispatch": row["auto_mode_enabled"],
            "routing.max_budget_usd": row["budget_cap_usd"],
            "routing.max_steps": row["max_auto_steps"],
        }
        return mapping.get(key)

    if key == "model.default":
        row = conn.execute(
            """
            SELECT model FROM workspace_model_catalog
            WHERE workspace_id = ? AND tenant_id = ? AND is_enabled = 1
            ORDER BY priority ASC, provider_slug ASC, model ASC LIMIT 1
            """,
            (ctx.workspace_id, ctx.tenant_id),
        ).fetchone()
        if row is not None:
            return row["model"]

    return None


def _tenant_config(conn: Any, ctx: Context, key: str) -> Any:
    """Look up a tenant-scoped setting. Returns None until tenant_settings exists."""

    try:
        row = conn.execute(
            "SELECT value_json FROM tenant_settings WHERE tenant_id = ? AND key = ?",
            (ctx.tenant_id, key),
        ).fetchone()
        if row is not None:
            import json

            return json.loads(row["value_json"])
    except Exception:
        # tenant_settings table may not exist yet in early E3-2 migrations.
        return None
    return None


def _user_config(conn: Any, ctx: Context, key: str) -> Any:
    """Look up a user-scoped setting from the Foundation profile if available."""

    if not ctx.user_id:
        return None
    try:
        row = conn.execute(
            "SELECT preferences_json FROM fnd_users WHERE id = ?",
            (ctx.user_id,),
        ).fetchone()
        if row is not None and row.get("preferences_json"):
            import json

            prefs = json.loads(row["preferences_json"])
            return prefs.get(key)
    except Exception:
        return None
    return None


def resolve(
    conn: Any,
    ctx: Context,
    key: str,
    default: Any = None,
) -> Any:
    """Resolve ``key`` following the user > workspace > tenant > default cascade."""

    with transaction(conn, ctx=ctx):
        for value in (
            _user_config(conn, ctx, key),
            _workspace_config(conn, ctx, key),
            _tenant_config(conn, ctx, key),
            DEFAULTS.get(key),
            default,
        ):
            if value is not None:
                return value
    raise ConfigCascadeError(f"No value found for setting '{key}'")
