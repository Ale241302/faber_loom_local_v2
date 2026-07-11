"""Workspace routing policy helpers for E2-4 / E4-0.

E4-0 introduces ``routing.mode`` with three states:

- ``manual``   : human chooses model/preset per message (default).
- ``shadow``   : planner runs in the background, no side effects, no user-visible changes.
- ``natural``  : planner + execution, the former ``auto`` behaviour.

The legacy double gate (env ``FABERLOOM_AUTO_MODE_ENABLED`` +
``workspace_routing_policy.auto_mode_enabled``) maps to ``natural`` for backwards
compatibility. The explicit ``routing.mode`` setting wins over the legacy mapping.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from ..config_cascade import resolve as cascade_resolve
from ..context import Context
from ..db import get_routing_policy


logger = logging.getLogger(__name__)


def resolve_routing_mode(ctx: Context, conn: Any) -> str:
    """Return the effective routing mode for the current context.

    Resolution order (user > workspace > tenant > default):
      1. User preference ``routing.mode``.
      2. Workspace explicit ``routing.mode`` when supported, otherwise the
         legacy mapping ``FABERLOOM_AUTO_MODE_ENABLED`` env var plus
         ``workspace_routing_policy.auto_mode_enabled`` -> ``natural``.
      3. Tenant setting ``routing.mode``.
      4. Default ``manual``.

    The env var is DEPRECATED; callers should set ``routing.mode`` through the
    settings cascade instead.
    """

    from ..config_cascade import _user_config, _workspace_config, _tenant_config

    # 1. User preference wins.
    user_mode = _user_config(conn, ctx, "routing.mode")
    if user_mode in ("manual", "shadow", "natural"):
        return user_mode

    # 2. Workspace: explicit mode (future column) or legacy double gate.
    workspace_mode = _workspace_config(conn, ctx, "routing.mode")
    if workspace_mode in ("manual", "shadow", "natural"):
        return workspace_mode

    global_enabled = os.getenv("FABERLOOM_AUTO_MODE_ENABLED", "false").lower() in {
        "1",
        "true",
        "yes",
    }
    if global_enabled:
        policy = get_routing_policy(ctx, conn)
        if bool(policy.get("auto_mode_enabled")):
            logger.warning(
                "FABERLOOM_AUTO_MODE_ENABLED is deprecated; set routing.mode='natural' "
                "via the settings cascade instead"
            )
            return "natural"

    # 3. Tenant setting.
    tenant_mode = _tenant_config(conn, ctx, "routing.mode")
    if tenant_mode in ("manual", "shadow", "natural"):
        return tenant_mode

    # 4. Default.
    return "manual"


def is_auto_mode_allowed(ctx: Context, conn: Any) -> bool:
    """Return True when the effective mode is not ``manual``.

    Kept for backwards compatibility with callers that expect a boolean gate.
    """

    return resolve_routing_mode(ctx, conn) != "manual"


def get_effective_allowlists(
    ctx: Context,
    conn: Any,
    policy: dict[str, Any] | None = None,
) -> tuple[set[str] | None, dict[str, list[str]]]:
    """Return effective provider and model allowlists for a workspace.

    Workspace policy overrides the global env var. A workspace-level empty list
    is treated as "all allowed" only when the env var is also empty; otherwise
    it is the intersection.
    """

    if policy is None:
        policy = get_routing_policy(ctx, conn)

    env_provider_csv = os.getenv("FABERLOOM_PROVIDER_ALLOWLIST")
    env_providers: set[str] = set(env_provider_csv.split(",")) if env_provider_csv else set()
    workspace_providers: list[str] = policy.get("provider_allowlist") or []

    if workspace_providers:
        provider_allowlist = set(workspace_providers)
        if env_providers:
            provider_allowlist &= env_providers
    elif env_providers:
        provider_allowlist = env_providers
    else:
        provider_allowlist = None

    model_allowlist: dict[str, list[str]] = policy.get("model_allowlist") or {}

    return provider_allowlist, model_allowlist
