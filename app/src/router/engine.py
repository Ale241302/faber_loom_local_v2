"""Routing engine for FaberLoom SL1a.

Default preset "Balanceado": filter by allowlist, sort providers by priority,
try in order, and fallback on ProviderError. A requested provider_slug is treated
as a preference, not a strict lock; if it fails, the router still falls back.

Model selection is per-provider: each candidate uses the requested model only if
it appears in that provider's allowlist; otherwise it falls back to the
provider's configured default (also validated). Providers without an allowed
model are skipped.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from typing import Any

from . import cost as router_cost
from .cost import estimate_cost
from .models import CompletionRequest, CompletionResult, RouterSettings
from .providers import Provider, ProviderError


DEFAULT_ESTIMATED_OUTPUT_TOKENS = 1024


class BudgetExceeded(ProviderError):
    """Raised when the request cannot be satisfied within the configured budget."""

    def __init__(self, detail: str):
        super().__init__("router", "budget_exceeded")
        self.detail = detail


class NoAllowedModel(ProviderError):
    """Raised when no candidate provider has an allowed model for the request."""

    def __init__(self, detail: str):
        super().__init__("router", "no_allowed_model")
        self.detail = detail


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    try:
        return json.dumps(content, ensure_ascii=False)
    except TypeError:
        return str(content)


def _estimate_input_tokens(messages: list[dict[str, Any]]) -> int:
    text = "\n".join(
        f"{message.get('role', 'user')}: {_content_to_text(message.get('content', ''))}"
        for message in messages
    )
    return max(1, len(text) // 4)


class Router:
    """Provider router with allowlist, priority ordering, budget cap and fallback."""

    def __init__(
        self,
        settings: RouterSettings | None = None,
        providers: Iterable[Provider] | Mapping[str, Provider] | None = None,
    ):
        self.settings = settings or RouterSettings()
        self.providers: dict[str, Provider] = {}
        self._key_origins: dict[str, str] = {}

        if providers is None:
            return

        provider_iter = providers.values() if isinstance(providers, Mapping) else providers
        for provider in provider_iter:
            self.providers[provider.provider_slug] = provider
            self._key_origins[provider.provider_slug] = provider.config.key_origin

    def check_budget(self, cost: float) -> bool:
        return cost <= self.settings.budget_cap_usd

    def has_available_provider(self) -> bool:
        """Return True if at least one configured provider can serve requests."""
        return bool(self._ordered_providers())

    def list_available_providers(self) -> list[str]:
        return [provider.provider_slug for provider in self._ordered_providers()]

    def all_providers(self) -> list[Provider]:
        """Return all registered providers (including unavailable/disabled)."""
        return sorted(self.providers.values(), key=lambda provider: provider.config.priority)

    def provider_allowed(self, provider: Provider) -> bool:
        """Public check: is this provider permitted by the provider allowlist?"""
        return self._provider_allowed(provider)

    def key_origin(self, provider_slug: str) -> str | None:
        """Return how the provider's API key was resolved ('platform', 'tenant', etc.)."""
        return self._key_origins.get(provider_slug)

    def estimate(self, request: CompletionRequest) -> tuple[float, str, str]:
        """Return (estimated_cost_usd, provider_slug, model) for the first viable candidate.

        Raises ProviderError if no candidate has an allowed model.
        """
        candidates = self._ordered_providers(request)
        for provider in candidates:
            model = self._resolve_model_for_provider(provider, request)
            if model is None:
                continue
            estimated_cost = estimate_cost(
                model,
                _estimate_input_tokens(request.messages),
                request.max_tokens or DEFAULT_ESTIMATED_OUTPUT_TOKENS,
            )
            total_cost = request.spent_usd + estimated_cost
            if not self.check_budget(total_cost):
                continue
            return estimated_cost, provider.provider_slug, model
        raise NoAllowedModel("no configured provider has an allowed model for this request")

    def complete(self, request: CompletionRequest) -> CompletionResult:
        candidates = self._ordered_providers(request)
        if not candidates:
            raise ProviderError(
                "router",
                "Ningún proveedor disponible: configura OpenAI o Kimi (API key).",
            )

        failures: list[str] = []
        budget_failures: list[str] = []

        for provider in candidates:
            model = self._resolve_model_for_provider(provider, request)
            if model is None:
                failures.append(
                    f"{provider.provider_slug}: no allowed model available "
                    f"(requested={request.model}, default={provider.config.model_default})"
                )
                continue

            adjusted_request = request.model_copy(update={"model": model})
            estimated_cost = estimate_cost(
                model,
                _estimate_input_tokens(adjusted_request.messages),
                request.max_tokens or DEFAULT_ESTIMATED_OUTPUT_TOKENS,
            )
            estimated_total = request.spent_usd + estimated_cost

            if not self.check_budget(estimated_total):
                budget_failures.append(
                    f"{provider.provider_slug}: estimated total ${estimated_total:.6f} "
                    f"exceeds cap ${self.settings.budget_cap_usd:.2f}"
                )
                continue

            try:
                result = provider.complete(adjusted_request)
                result.key_origin = self._key_origins.get(provider.provider_slug)
            except ProviderError as exc:
                failures.append(f"{exc.provider_slug}: {exc.code}")
                continue

            actual_total = request.spent_usd + result.cost_usd
            if not self.check_budget(actual_total):
                budget_failures.append(
                    f"{provider.provider_slug}: actual total ${actual_total:.6f} "
                    f"exceeds cap ${self.settings.budget_cap_usd:.2f}"
                )
                continue

            return result

        if budget_failures and not failures:
            raise BudgetExceeded("; ".join(budget_failures))

        if failures and not budget_failures and all(
            failure.split(":", 1)[-1].strip().startswith("no allowed model available")
            for failure in failures
        ):
            raise NoAllowedModel("; ".join(failures))

        detail = "; ".join(failures + budget_failures) if (failures or budget_failures) else "all providers failed"
        raise ProviderError("router", detail)

    def _ordered_providers(self, request: CompletionRequest | None = None) -> list[Provider]:
        allowed = [
            provider
            for provider in self.providers.values()
            if self._provider_allowed(provider)
        ]
        ordered = sorted(allowed, key=lambda provider: provider.config.priority)

        if request is None or request.provider_slug is None:
            return [p for p in ordered if p.is_available()]

        preferred = [p for p in ordered if p.provider_slug == request.provider_slug]
        rest = [p for p in ordered if p.provider_slug != request.provider_slug and p.is_available()]
        return preferred + rest

    def _provider_allowed(self, provider: Provider) -> bool:
        slug = provider.provider_slug

        # El blocklist gana sobre todo, incluso sobre un provider_slug pedido
        # explicitamente por el caller (SPEC_FB_ROUTING_PRESETS_v1).
        if self.settings.provider_denylist and slug in self.settings.provider_denylist:
            return False

        if self.settings.jurisdiction_allowlist is not None:
            jurisdiction = router_cost.PROVIDER_JURISDICTION.get(slug)
            if jurisdiction not in self.settings.jurisdiction_allowlist:
                return False

        allowlist = self.settings.provider_allowlist
        if allowlist is None:
            return True
        return slug in allowlist

    def _resolve_model_for_provider(
        self, provider: Provider, request: CompletionRequest
    ) -> str | None:
        allowed = router_cost.MODEL_ALLOWLIST.get(provider.provider_slug, set())
        if request.model and request.model in allowed:
            return request.model
        default = provider.config.model_default
        if default in allowed:
            return default
        return None
