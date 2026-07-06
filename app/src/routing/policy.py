"""Workspace routing policy helpers for E2-4."""

from __future__ import annotations

import os
from typing import Any

from ..context import Context
from ..db import get_routing_policy, update_routing_policy


def is_auto_mode_allowed(ctx: Context, conn: Any) -> bool:
    """Return True only when the global flag and workspace policy allow auto mode."""

    global_enabled = os.getenv("FABERLOOM_AUTO_MODE_ENABLED", "false").lower() in {
        "1",
        "true",
        "yes",
    }
    if not global_enabled:
        return False
    policy = get_routing_policy(ctx, conn)
    return bool(policy.get("auto_mode_enabled"))


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
