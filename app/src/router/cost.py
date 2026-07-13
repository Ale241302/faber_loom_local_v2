"""Small SL1a pricing table and token-cost helpers.

Prices are intentionally centralized and approximate. Before using them for
billing or production enforcement, verify current vendor pricing and update this
table/version.
"""

from __future__ import annotations


# USD per 1K tokens: (input, output).
# Ollama/local models are treated as $0 provider cost in SL1a.
MODEL_PRICING_USD_PER_1K: dict[str, tuple[float, float]] = {
    # OpenAI pricing per 1K tokens (current as of 2025-06).
    "gpt-4o": (0.0025, 0.01),
    "gpt-4o-mini": (0.00015, 0.0006),
    # Imagen: el costo real es por imagen (~$0.04/1024px), no por token; el
    # dispatcher usa OPENAI_IMAGE_FLAT_COST_USD para el ledger.
    "gpt-image-1": (0.0, 0.0),
    # Hidden providers remain in the allowlist but are not surfaced in SL1a beta.
    "claude-3-5-sonnet": (0.003, 0.015),
    "gemini-1.5-pro": (0.0035, 0.0105),
    # __E5FIX16__ Moonshot/Kimi: precios oficiales cache-miss verificados
    # 2026-07-13 (platform.kimi.ai/docs/pricing/*). USD por 1K tokens.
    "moonshot-v1-8k": (0.0002, 0.002),
    "moonshot-v1-32k": (0.001, 0.003),
    "moonshot-v1-128k": (0.002, 0.005),
    # kimi-for-coding: sin precio por token publicado (Coding Plan). Proxy
    # conservador = kimi-k2.7-code oficial (0.95/4.00 por 1M).
    "kimi-for-coding": (0.00095, 0.004),
    # kimi-latest: sin pagina oficial de precio; conservador = moonshot-v1-128k.
    "kimi-latest": (0.002, 0.005),
    "kimi-k2.5": (0.0006, 0.003),
    "kimi-k2-thinking": (0.0006, 0.0025),
    "kimi-k2-turbo-preview": (0.00115, 0.008),
    "kimi-k2-0905-preview": (0.0006, 0.0025),
    "kimi-k2.6": (0.00095, 0.004),
    # Local models treated as zero provider cost.
    "llama3.1": (0.0, 0.0),
}

DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet",
    "google": "gemini-1.5-pro",
    "kimi": "moonshot-v1-8k",
    "ollama": "llama3.1",
}

FALLBACK_PRICING_MODEL = "gpt-4o"

PRICING_VERSION = "cost:sl1a-2026-07-13"

# SL1a model allowlist per provider. Unknown models are rejected at the API layer
# to avoid surprise costs / DoS through the local Ollama provider.
MODEL_ALLOWLIST: dict[str, set[str]] = {
    "openai": {"gpt-4o-mini", "gpt-4o", "gpt-image-1"},
    "anthropic": {"claude-3-5-sonnet"},
    "google": {"gemini-1.5-pro"},
    "kimi": {
        "moonshot-v1-8k",
        "moonshot-v1-32k",
        "moonshot-v1-128k",
        # Kimi Code / Coding Plan models (sk-kimi-* keys).
        "kimi-for-coding",
        "kimi-latest",
        "kimi-k2.5",
        "kimi-k2-thinking",
        "kimi-k2-turbo-preview",
        "kimi-k2-0905-preview",
        "kimi-k2.6",
    },
    "ollama": {"llama3.1"},
}

# Models that are only available on the Kimi Code / Coding Plan endpoint
# (keys prefixed sk-kimi-). Kept in one place so registry and UI can stay aligned.
KIMI_CODE_MODELS: set[str] = {
    "kimi-for-coding",
    "kimi-latest",
    "kimi-k2.5",
    "kimi-k2-thinking",
    "kimi-k2-turbo-preview",
    "kimi-k2-0905-preview",
    "kimi-k2.6",
}


def _pricing_for_model(model: str) -> tuple[float, float]:
    normalized = (model or "").strip().lower()

    if normalized in MODEL_PRICING_USD_PER_1K:
        return MODEL_PRICING_USD_PER_1K[normalized]

    for known_model, pricing in MODEL_PRICING_USD_PER_1K.items():
        if normalized.startswith(known_model):
            return pricing

    if normalized.startswith(("llama", "ollama")):
        return MODEL_PRICING_USD_PER_1K["llama3.1"]

    # Conservative-ish fallback for unknown cloud models.
    return MODEL_PRICING_USD_PER_1K[FALLBACK_PRICING_MODEL]


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate USD cost for model usage.

    Args:
        model: Provider model name.
        input_tokens: Prompt/input tokens.
        output_tokens: Completion/output tokens.
    """

    input_price, output_price = _pricing_for_model(model)
    cost = ((max(input_tokens, 0) / 1000) * input_price) + (
        (max(output_tokens, 0) / 1000) * output_price
    )
    return round(cost, 8)


def get_default_model(provider_slug: str) -> str:
    """Return the default SL1a model for a provider slug."""

    return DEFAULT_MODELS.get(provider_slug, DEFAULT_MODELS["openai"])
