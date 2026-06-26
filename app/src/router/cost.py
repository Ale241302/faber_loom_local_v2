"""Small SL1a pricing table and token-cost helpers.

Prices are intentionally centralized and approximate. Before using them for
billing or production enforcement, verify current vendor pricing and update this
table/version.
"""

from __future__ import annotations


# USD per 1K tokens: (input, output).
# Ollama/local models are treated as $0 provider cost in SL1a.
MODEL_PRICING_USD_PER_1K: dict[str, tuple[float, float]] = {
    "gpt-4o": (0.005, 0.015),
    "gpt-4o-mini": (0.00015, 0.0006),
    "claude-3-5-sonnet": (0.003, 0.015),
    "gemini-1.5-pro": (0.0035, 0.0105),
    "llama3.1": (0.0, 0.0),
}

DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-sonnet",
    "google": "gemini-1.5-pro",
    "ollama": "llama3.1",
}

FALLBACK_PRICING_MODEL = "gpt-4o"

PRICING_VERSION = "cost:sl1a-2026-06-25"

# SL1a model allowlist per provider. Unknown models are rejected at the API layer
# to avoid surprise costs / DoS through the local Ollama provider.
MODEL_ALLOWLIST: dict[str, set[str]] = {
    "openai": {"gpt-4o-mini", "gpt-4o"},
    "anthropic": {"claude-3-5-sonnet"},
    "google": {"gemini-1.5-pro"},
    "ollama": {"llama3.1"},
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
