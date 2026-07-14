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

from pydantic import BaseModel

from ..config_cascade import resolve as cascade_resolve
from ..context import Context
from ..db import get_routing_policy


logger = logging.getLogger(__name__)


class RoutingConstraints(BaseModel):
    """Restricciones efectivas de routing para una llamada.

    ``None`` significa "sin restriccion". Una lista vacia en
    ``provider_allowlist`` significa lo contrario: ningun proveedor es legal.
    """

    provider_allowlist: list[str] | None = None
    provider_denylist: list[str] | None = None
    jurisdiction_allowlist: list[str] | None = None


def resolve_routing_mode(ctx: Context, conn: Any) -> str:
    """Return the effective routing mode for the current context.

    Resolution order (user > workspace > tenant > legacy fallback > default):
      1. User preference ``routing.mode``.
      2. Workspace explicit ``routing.mode`` when supported.
      3. Tenant setting ``routing.mode``.
      4. Legacy mapping ``FABERLOOM_AUTO_MODE_ENABLED`` env var plus
         ``workspace_routing_policy.auto_mode_enabled`` -> ``natural``.
      5. Default ``manual``.

    The explicit ``routing.mode`` flag wins over the legacy env var mapping.
    The env var is DEPRECATED; callers should set ``routing.mode`` through the
    settings cascade instead.
    """

    from ..config_cascade import _user_config, _workspace_config, _tenant_config
    from ..db_adapter import transaction

    with transaction(conn, ctx=ctx):
        # 1. User preference wins.
        user_mode = _user_config(conn, ctx, "routing.mode")
        if user_mode in ("manual", "shadow", "natural"):
            return user_mode

        # 2. Workspace: explicit mode.
        workspace_mode = _workspace_config(conn, ctx, "routing.mode")
        if workspace_mode in ("manual", "shadow", "natural"):
            return workspace_mode

        # 3. Tenant setting.
        tenant_mode = _tenant_config(conn, ctx, "routing.mode")
        if tenant_mode in ("manual", "shadow", "natural"):
            return tenant_mode

    # 4. Legacy double gate as fallback only when no explicit mode is set.
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

    # 5. Default.
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


def compose_routing_constraints(
    env_providers: list[str] | None,
    policy_providers: list[str] | None,
    envelope: dict[str, Any],
) -> RoutingConstraints:
    """Componer las restricciones de las tres fuentes de gobierno.

    Antes habia tres fuentes de verdad para "puedo usar este proveedor?" y solo
    dos tenian dientes: la env var global y ``workspace_routing_policy``. El
    envelope de ``routing_preset`` --el unico que dice "compliance"-- no se
    enforceaba. Esta funcion las colapsa en una sola respuesta.

    Una fuente que no restringe (``None`` o lista vacia) se saltea. El deny no
    se resta del allowlist: viaja aparte para que el guard lo aplique al final
    y gane incluso sobre un ``provider_slug`` pedido por el caller.
    """

    sources = [
        source
        for source in (env_providers, policy_providers, envelope.get("providers_allow"))
        if source
    ]

    provider_allowlist: list[str] | None
    if not sources:
        provider_allowlist = None
    else:
        # Interseccion preservando el orden de la primera fuente que restringe.
        # Una interseccion vacia es [] y no None: ningun proveedor es legal.
        provider_allowlist = list(sources[0])
        for source in sources[1:]:
            allowed = set(source)
            provider_allowlist = [slug for slug in provider_allowlist if slug in allowed]

    return RoutingConstraints(
        provider_allowlist=provider_allowlist,
        provider_denylist=list(envelope.get("providers_deny") or []) or None,
        jurisdiction_allowlist=list(envelope.get("jurisdictions") or []) or None,
    )


def resolve_effective_routing_constraints(
    ctx: Context,
    conn: Any,
    preset_ref: str | None = None,
    policy: dict[str, Any] | None = None,
) -> RoutingConstraints:
    """Resolver las restricciones efectivas para el preset de esta llamada.

    Lee las tres fuentes y delega la composicion. ``preset_ref`` acepta lo mismo
    que ``resolve_routing_preset``: '@preset/<slug>', un slug pelado, o el
    legacy 'provider:model' (que no tiene envelope).
    """

    from ..db import get_routing_preset

    if policy is None:
        policy = get_routing_policy(ctx, conn)

    env_provider_csv = os.getenv("FABERLOOM_PROVIDER_ALLOWLIST")
    env_providers = (
        [item.strip() for item in env_provider_csv.split(",") if item.strip()]
        if env_provider_csv
        else None
    )

    envelope: dict[str, Any] = {}
    ref = (preset_ref or "").strip()
    if ref and ":" not in ref:
        slug = ref.split("@preset/", 1)[-1].strip()
        preset = get_routing_preset(ctx, conn, slug)
        if preset is not None:
            envelope = preset.get("envelope") or {}

    return compose_routing_constraints(
        env_providers,
        policy.get("provider_allowlist") or None,
        envelope,
    )
