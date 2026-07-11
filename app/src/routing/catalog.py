"""Workspace model catalog for E2-4.

The catalog is the source of truth for capability-based routing. Each workspace
owns its catalog entries; seeding happens from the configured providers and the
hardcoded model allowlist/pricing table.
"""

from __future__ import annotations

import json
from typing import Any

from ..context import Context
from ..config_cascade import resolve as cascade_resolve
from ..db import (
    create_model_catalog_entry,
    get_routing_policy,
    list_model_catalog,
)
from ..db_adapter import transaction
from ..router import cost as router_cost
from ..router.registry import build_router


DEFAULT_MODEL_CAPABILITIES: dict[str, list[str]] = {
    "gpt-4o-mini": ["text", "cheap", "vision"],
    "gpt-4o": ["text", "vision"],
    "gpt-image-1": ["image_gen"],
    "claude-3-5-sonnet": ["text", "vision"],
    "gemini-1.5-pro": ["text", "vision"],
    "moonshot-v1-8k": ["text"],
    "moonshot-v1-32k": ["text"],
    "moonshot-v1-128k": ["text"],
    "kimi-for-coding": ["text", "code"],
    "kimi-latest": ["text", "code"],
    "kimi-k2.5": ["text", "code"],
    "kimi-k2-thinking": ["text", "code"],
    "kimi-k2-turbo-preview": ["text", "code"],
    "kimi-k2-0905-preview": ["text", "code"],
    "kimi-k2.6": ["text", "code"],
    "llama3.1": ["text", "local_only"],
}


# Nivel de capacidad aproximado por modelo (3 = frontier, 2 = medio, 1 = básico).
# Determinista y versionado en git — contrato F1 tiered (ENT_PLAT_LLM_ROUTING §F,
# DEC-006): los niveles cambian por decisión humana con commit explícito.
MODEL_QUALITY: dict[str, int] = {
    "gpt-4o": 3,
    "gpt-image-1": 3,
    "gpt-4o-mini": 1,
    "claude-3-5-sonnet": 3,
    "gemini-1.5-pro": 3,
    "moonshot-v1-8k": 1,
    "moonshot-v1-32k": 2,
    "moonshot-v1-128k": 2,
    "kimi-for-coding": 3,
    "kimi-latest": 2,
    "kimi-k2.5": 3,
    "kimi-k2-thinking": 3,
    "kimi-k2-turbo-preview": 2,
    "kimi-k2-0905-preview": 2,
    "kimi-k2.6": 3,
    "llama3.1": 1,
}
DEFAULT_MODEL_QUALITY = 2

# Ventana de contexto aproximada (tokens) por modelo, para descartar candidatos
# que no aguantan el input estimado de un paso (tareas largas / PDFs).
MODEL_CONTEXT_TOKENS: dict[str, int] = {
    "gpt-4o": 128_000,
    "gpt-4o-mini": 128_000,
    "claude-3-5-sonnet": 200_000,
    "gemini-1.5-pro": 1_000_000,
    "moonshot-v1-8k": 8_000,
    "moonshot-v1-32k": 32_000,
    "moonshot-v1-128k": 128_000,
    "kimi-for-coding": 256_000,
    "kimi-latest": 128_000,
    "kimi-k2.5": 256_000,
    "kimi-k2-thinking": 256_000,
    "kimi-k2-turbo-preview": 256_000,
    "kimi-k2-0905-preview": 256_000,
    "kimi-k2.6": 256_000,
    "llama3.1": 8_000,
}
DEFAULT_MODEL_CONTEXT_TOKENS = 32_000


def seed_workspace_catalog(
    ctx: Context,
    conn: Any,
    workspace_id: str,
    *,
    include_stub_image_gen: bool = False,
) -> list[dict[str, Any]]:
    """Create or refresh default catalog entries for a workspace from configured providers.

    Idempotent: only creates missing entries and refreshes seeded (non-managed)
    entries with current provider availability/pricing. Admin-managed entries are
    left untouched.
    """

    from ..db import new_id, utc_now

    # Ensure the policy row exists first.
    get_routing_policy(ctx, conn, workspace_id)

    byo_mode = cascade_resolve(conn, ctx, "routing.byo_mode", default="hibrido")
    router = build_router(
        user_id=ctx.user_id,
        tenant_id=ctx.tenant_id,
        byo_mode=byo_mode,
    )
    now = utc_now()

    with transaction(conn, ctx=ctx):
        for provider in router.all_providers():
            provider_slug = provider.provider_slug
            models = router_cost.MODEL_ALLOWLIST.get(provider_slug, set())
            is_local = provider_slug == "ollama"
            available = provider.is_available()
            for model in sorted(models):
                capabilities = list(DEFAULT_MODEL_CAPABILITIES.get(model, ["text"]))
                if is_local and "local_only" not in capabilities:
                    capabilities.append("local_only")
                input_price, output_price = router_cost._pricing_for_model(model)

                existing = conn.execute(
                    "SELECT id, is_managed FROM workspace_model_catalog "
                    "WHERE workspace_id = ? AND tenant_id = ? AND provider_slug = ? AND model = ?",
                    (workspace_id, ctx.require_tenant(), provider_slug, model),
                ).fetchone()

                if existing is None:
                    entry_id = new_id("mce")
                    conn.execute(
                        """
                        INSERT INTO workspace_model_catalog (
                            id, workspace_id, tenant_id, provider_slug, model, capabilities_json,
                            is_enabled, priority, cost_input_1k, cost_output_1k, is_local, is_managed,
                            source_version, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            entry_id,
                            workspace_id,
                            ctx.require_tenant(),
                            provider_slug,
                            model,
                            json.dumps(capabilities, ensure_ascii=False),
                            1 if available or is_local else 0,
                            provider.config.priority,
                            input_price,
                            output_price,
                            1 if is_local else 0,
                            0,
                            router_cost.PRICING_VERSION,
                            now,
                        ),
                    )
                elif existing["is_managed"] == 0:
                    conn.execute(
                        """
                        UPDATE workspace_model_catalog
                        SET is_enabled = ?, priority = ?, cost_input_1k = ?, cost_output_1k = ?,
                            capabilities_json = ?, source_version = ?
                        WHERE id = ?
                        """,
                        (
                            1 if available or is_local else 0,
                            provider.config.priority,
                            input_price,
                            output_price,
                            json.dumps(capabilities, ensure_ascii=False),
                            router_cost.PRICING_VERSION,
                            existing["id"],
                        ),
                    )

        if include_stub_image_gen:
            stub = conn.execute(
                "SELECT id FROM workspace_model_catalog "
                "WHERE workspace_id = ? AND tenant_id = ? AND provider_slug = ? AND model = ?",
                (workspace_id, ctx.require_tenant(), "stub", "fake-image-gen"),
            ).fetchone()
            if stub is None:
                stub_id = new_id("mce")
                conn.execute(
                    """
                    INSERT INTO workspace_model_catalog (
                        id, workspace_id, tenant_id, provider_slug, model, capabilities_json,
                        is_enabled, priority, cost_input_1k, cost_output_1k, is_local, is_managed,
                        source_version, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        stub_id,
                        workspace_id,
                        ctx.require_tenant(),
                        "stub",
                        "fake-image-gen",
                        json.dumps(["image_gen"], ensure_ascii=False),
                        1,
                        200,
                        0.0,
                        0.0,
                        1,
                        0,
                        router_cost.PRICING_VERSION,
                        now,
                    ),
                )

    return list_model_catalog(ctx, conn, enabled_only=False)


def resolve_model_for_capability(
    ctx: Context,
    conn: Any,
    capability: str,
    *,
    budget_remaining: float,
    policy: dict[str, Any] | None = None,
    local_only: bool = False,
    preferred_provider: str | None = None,
    complexity: str = "medium",
    estimated_input_tokens: int = 0,
) -> dict[str, Any]:
    """Pick the best catalog entry for a capability and task complexity.

    Contrato F1 tiered (ENT_PLAT_LLM_ROUTING §D/§F, DEC-006): en modo auto la
    prioridad manual del provider NO participa; la decisión es determinista por
    complejidad de la tarea, calidad del modelo, costo, tokens y budget:
      - low complexity  -> CHEAPEST_FIRST: el más barato que cumpla
      - high complexity -> BEST_FIRST: el de mayor calidad dentro del budget
      - medium          -> mejor valor (costo/calidad)
    Los modelos cuya ventana de contexto no aguanta ``estimated_input_tokens``
    se descartan (tareas largas van a modelos de contexto grande).

    Fail-closed: raises ValueError if no entry matches capability, allowlist,
    budget, context or isolation constraints.
    """

    if policy is None:
        policy = get_routing_policy(ctx, conn)

    if local_only or policy.get("require_local_only"):
        local_only = True

    provider_allowlist: set[str] = set(policy.get("provider_allowlist") or [])
    model_allowlist: dict[str, list[str]] = policy.get("model_allowlist") or {}

    candidates = list_model_catalog(
        ctx,
        conn,
        capability=capability,
        local_only=local_only,
        enabled_only=True,
    )

    complexity = (complexity or "medium").lower()
    if complexity not in {"low", "medium", "high"}:
        complexity = "medium"

    def _score(entry: dict[str, Any]) -> tuple[float, float]:
        """Lower tuple sorts first. La prioridad manual del admin NO participa:
        el modo auto decide por calidad del modelo y costo según complejidad."""
        cost_per_1k = entry["cost_input_1k"] + entry["cost_output_1k"]
        quality = MODEL_QUALITY.get(entry["model"], DEFAULT_MODEL_QUALITY)
        if capability == "cheap" or complexity == "low":
            # CHEAPEST_FIRST: el más barato; a igual costo, el de más calidad.
            return (cost_per_1k, -quality)
        if complexity == "high":
            # BEST_FIRST: el de más calidad; a igual calidad, el más barato.
            return (-quality, cost_per_1k)
        # medium: mejor valor — costo por unidad de calidad.
        return (cost_per_1k / max(quality, 1), cost_per_1k)

    for entry in sorted(candidates, key=_score):
        if provider_allowlist and entry["provider_slug"] not in provider_allowlist:
            continue
        allowed_models = model_allowlist.get(entry["provider_slug"])
        if allowed_models is not None and entry["model"] not in allowed_models:
            continue
        if preferred_provider and entry["provider_slug"] != preferred_provider:
            continue
        # Context-window check: descarta modelos que no aguantan el input estimado
        # (margen 20% + espacio para el output).
        if estimated_input_tokens:
            context_limit = MODEL_CONTEXT_TOKENS.get(entry["model"], DEFAULT_MODEL_CONTEXT_TOKENS)
            if estimated_input_tokens * 1.2 + 1024 > context_limit:
                continue
        # Budget check: estimación con los tokens reales del paso cuando se conocen.
        est_input = max(estimated_input_tokens, 1000)
        estimated_cost = (entry["cost_input_1k"] / 1000) * est_input + (entry["cost_output_1k"] / 1000) * 1024
        if estimated_cost > budget_remaining:
            continue
        return entry

    raise ValueError(f"No catalog model available for capability '{capability}' with current policy/budget")


def has_catalog_capability(
    ctx: Context,
    conn: Any,
    capability: str,
    *,
    local_only: bool = False,
) -> bool:
    """Return True if the workspace catalog has at least one enabled model for the capability."""

    try:
        resolve_model_for_capability(
            ctx,
            conn,
            capability,
            budget_remaining=float("inf"),
            local_only=local_only,
        )
        return True
    except ValueError:
        return False
