El entorno está en **solo lectura**, así que no puedo persistir los archivos directamente. Abajo tienes los **archivos base completos** para `app/src/router/` según SL1a: router multi-proveedor, fallback por prioridad, allowlist, cap de presupuesto, costos estimados y providers OpenAI/Anthropic/Google vía OpenAI-compatible/Ollama opcional.

> Nota: no incluye migración de `usage_record` ni endpoints API; solo los modelos y capa router base solicitados. Si los aplicas en el repo, después corre `graphify update .`.

---

## `app/src/router/models.py`

```python
"""Contracts for the SpaceLoom SL1a provider router.

The router keeps provider selection, cost estimation, and usage accounting behind
one seam so BYO-key in Etapa 1 can later become managed keys without changing
call sites.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..models import SCHEMA_VERSION


class CompletionRequest(BaseModel):
    """Provider-agnostic chat completion request."""

    messages: list[dict[str, Any]]
    model: str | None = None
    provider_slug: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=None, gt=0)

    @field_validator("messages")
    @classmethod
    def messages_must_not_be_empty(cls, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not value:
            raise ValueError("CompletionRequest.messages cannot be empty")
        return value


class CompletionResult(BaseModel):
    """Provider-agnostic chat completion result."""

    content: str
    model: str
    provider_slug: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0.0)
    duration_ms: int = Field(ge=0)


class ProviderConfig(BaseModel):
    """Runtime config for a provider. API keys must come from env vars only."""

    provider_slug: str
    api_key: str | None = None
    base_url: str | None = None
    model_default: str
    priority: int
    is_enabled: bool


class RouterSettings(BaseModel):
    """SL1a default preset: Balanceado = provider priority order + fallback."""

    budget_cap_usd: float = Field(default=5.0, ge=0.0)
    provider_allowlist: list[str] | None = None


class UsageRecord(BaseModel):
    """Pydantic shape for the future usage_record table.

    Mirrors the contract-first latent fields used elsewhere in SL0/SL1 so usage
    accounting can later move from local SQLite to a tenant-aware ledger.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None

    provider_slug: str
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0.0)
    duration_ms: int = Field(ge=0)
    status: str = "succeeded"
    error: str | None = None

    request_json: dict[str, Any] = Field(default_factory=dict)
    response_json: dict[str, Any] = Field(default_factory=dict)

    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int = SCHEMA_VERSION
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
```

---

## `app/src/router/cost.py`

```python
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
```

---

## `app/src/router/providers.py`

```python
"""Provider implementations for the SpaceLoom SL1a router."""

from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any

from .cost import estimate_cost
from .models import CompletionRequest, CompletionResult, ProviderConfig


DEFAULT_MAX_TOKENS = 1024


class ProviderError(RuntimeError):
    """Raised when one provider fails.

    The router catches this and falls back to the next provider when possible.
    """

    def __init__(self, provider_slug: str, message: str):
        self.provider_slug = provider_slug
        super().__init__(f"{provider_slug}: {message}")


class Provider(ABC):
    """Abstract provider interface used by Router."""

    requires_api_key: bool = True

    def __init__(self, config: ProviderConfig):
        self.config = config

    @property
    def provider_slug(self) -> str:
        return self.config.provider_slug

    def is_available(self) -> bool:
        if not self.config.is_enabled:
            return False
        if self.requires_api_key and not self.config.api_key:
            return False
        return True

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResult:
        """Run a chat completion or raise ProviderError."""


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    try:
        return json.dumps(content, ensure_ascii=False)
    except TypeError:
        return str(content)


def _normalize_openai_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for message in messages:
        role = str(message.get("role") or "user")
        content = _content_to_text(message.get("content", ""))
        normalized.append({"role": role, "content": content})
    return normalized


def _split_anthropic_messages(messages: list[dict[str, Any]]) -> tuple[str | None, list[dict[str, str]]]:
    system_parts: list[str] = []
    normalized: list[dict[str, str]] = []

    for message in messages:
        role = str(message.get("role") or "user")
        content = _content_to_text(message.get("content", ""))

        if role == "system":
            if content:
                system_parts.append(content)
            continue

        if role not in {"user", "assistant"}:
            role = "user"

        if normalized and normalized[-1]["role"] == role:
            normalized[-1]["content"] = f"{normalized[-1]['content']}\n\n{content}".strip()
        else:
            normalized.append({"role": role, "content": content})

    if not normalized:
        normalized.append({"role": "user", "content": ""})

    if normalized[0]["role"] == "assistant":
        normalized.insert(0, {"role": "user", "content": "Continue."})

    system = "\n\n".join(system_parts).strip() or None
    return system, normalized


def _estimate_tokens_from_text(text: str) -> int:
    # Cheap rough estimate for fallback when a provider does not return usage.
    return max(1, len(text) // 4)


def _estimate_input_tokens(messages: list[dict[str, Any]]) -> int:
    text = "\n".join(
        f"{message.get('role', 'user')}: {_content_to_text(message.get('content', ''))}"
        for message in messages
    )
    return _estimate_tokens_from_text(text)


def _usage_value(usage: Any, *names: str) -> int | None:
    if usage is None:
        return None

    for name in names:
        value = usage.get(name) if isinstance(usage, dict) else getattr(usage, name, None)
        if value is not None:
            return int(value)

    return None


def _duration_ms(start: float) -> int:
    return max(0, int((time.perf_counter() - start) * 1000))


def _extract_openai_content(response: Any) -> str:
    choices = getattr(response, "choices", None) or []
    if not choices:
        return ""

    first = choices[0]
    message = getattr(first, "message", None)
    content = getattr(message, "content", None)

    if isinstance(content, list):
        return "\n".join(_content_to_text(part) for part in content)

    return _content_to_text(content)


def _extract_anthropic_content(response: Any) -> str:
    blocks = getattr(response, "content", None) or []
    parts: list[str] = []

    for block in blocks:
        text = getattr(block, "text", None)
        if text is not None:
            parts.append(str(text))
            continue

        if isinstance(block, dict) and block.get("text") is not None:
            parts.append(str(block["text"]))

    return "\n".join(parts).strip()


class _OpenAICompatibleProvider(Provider):
    """Shared implementation for OpenAI-compatible chat.completions APIs."""

    default_base_url: str | None = None

    def _client_api_key(self) -> str:
        return self.config.api_key or "ollama"

    def _client_base_url(self) -> str | None:
        return self.config.base_url or self.default_base_url

    def complete(self, request: CompletionRequest) -> CompletionResult:
        if not self.is_available():
            raise ProviderError(self.provider_slug, "provider is not configured")

        start = time.perf_counter()
        model = request.model or self.config.model_default

        try:
            from openai import OpenAI

            client_kwargs: dict[str, Any] = {"api_key": self._client_api_key()}
            base_url = self._client_base_url()
            if base_url:
                client_kwargs["base_url"] = base_url

            client = OpenAI(**client_kwargs)

            completion_kwargs: dict[str, Any] = {
                "model": model,
                "messages": _normalize_openai_messages(request.messages),
                "temperature": request.temperature,
            }
            if request.max_tokens is not None:
                completion_kwargs["max_tokens"] = request.max_tokens

            response = client.chat.completions.create(**completion_kwargs)
            content = _extract_openai_content(response)
            usage = getattr(response, "usage", None)

            input_tokens = _usage_value(usage, "prompt_tokens", "input_tokens") or _estimate_input_tokens(
                request.messages
            )
            output_tokens = _usage_value(
                usage,
                "completion_tokens",
                "output_tokens",
            ) or _estimate_tokens_from_text(content)

            return CompletionResult(
                content=content,
                model=model,
                provider_slug=self.provider_slug,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=estimate_cost(model, input_tokens, output_tokens),
                duration_ms=_duration_ms(start),
            )
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(self.provider_slug, str(exc)) from exc


class OpenAIProvider(_OpenAICompatibleProvider):
    """OpenAI chat completions provider."""

    requires_api_key = True


class GoogleProvider(_OpenAICompatibleProvider):
    """Google Gemini through its OpenAI-compatible endpoint."""

    requires_api_key = True
    default_base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"


class OllamaProvider(_OpenAICompatibleProvider):
    """Local Ollama through its OpenAI-compatible endpoint."""

    requires_api_key = False
    default_base_url = "http://localhost:11434/v1"


class AnthropicProvider(Provider):
    """Anthropic Messages API provider."""

    requires_api_key = True

    def complete(self, request: CompletionRequest) -> CompletionResult:
        if not self.is_available():
            raise ProviderError(self.provider_slug, "provider is not configured")

        start = time.perf_counter()
        model = request.model or self.config.model_default
        system, messages = _split_anthropic_messages(request.messages)

        try:
            from anthropic import Anthropic

            client_kwargs: dict[str, Any] = {"api_key": self.config.api_key}
            if self.config.base_url:
                client_kwargs["base_url"] = self.config.base_url

            client = Anthropic(**client_kwargs)

            completion_kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "max_tokens": request.max_tokens or DEFAULT_MAX_TOKENS,
                "temperature": request.temperature,
            }
            if system:
                completion_kwargs["system"] = system

            response = client.messages.create(**completion_kwargs)
            content = _extract_anthropic_content(response)
            usage = getattr(response, "usage", None)

            input_tokens = _usage_value(usage, "input_tokens") or _estimate_input_tokens(
                request.messages
            )
            output_tokens = _usage_value(usage, "output_tokens") or _estimate_tokens_from_text(content)

            return CompletionResult(
                content=content,
                model=model,
                provider_slug=self.provider_slug,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=estimate_cost(model, input_tokens, output_tokens),
                duration_ms=_duration_ms(start),
            )
        except ProviderError:
            raise
        except Exception as exc:
            raise ProviderError(self.provider_slug, str(exc)) from exc
```

---

## `app/src/router/engine.py`

```python
"""Routing engine for SpaceLoom SL1a.

Default preset "Balanceado": filter by allowlist, sort providers by priority,
try in order, and fallback on ProviderError.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from typing import Any

from .cost import estimate_cost
from .models import CompletionRequest, CompletionResult, RouterSettings
from .providers import Provider, ProviderError


DEFAULT_ESTIMATED_OUTPUT_TOKENS = 1024


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

        if providers is None:
            return

        provider_iter = providers.values() if isinstance(providers, Mapping) else providers
        for provider in provider_iter:
            if provider.is_available():
                self.providers[provider.provider_slug] = provider

    def check_budget(self, estimated_cost: float) -> bool:
        return estimated_cost <= self.settings.budget_cap_usd

    def list_available_providers(self) -> list[str]:
        return [provider.provider_slug for provider in self._ordered_providers()]

    def complete(self, request: CompletionRequest) -> CompletionResult:
        candidates = self._ordered_providers(request)
        if not candidates:
            raise ProviderError("router", "no configured providers are available")

        failures: list[str] = []

        for provider in candidates:
            model = request.model or provider.config.model_default
            estimated_cost = estimate_cost(
                model,
                _estimate_input_tokens(request.messages),
                request.max_tokens or DEFAULT_ESTIMATED_OUTPUT_TOKENS,
            )

            if not self.check_budget(estimated_cost):
                failures.append(
                    f"{provider.provider_slug}: estimated cost ${estimated_cost:.6f} "
                    f"exceeds budget cap ${self.settings.budget_cap_usd:.2f}"
                )
                continue

            try:
                result = provider.complete(request)
            except ProviderError as exc:
                failures.append(str(exc))
                continue

            if not self.check_budget(result.cost_usd):
                failures.append(
                    f"{provider.provider_slug}: actual cost ${result.cost_usd:.6f} "
                    f"exceeds budget cap ${self.settings.budget_cap_usd:.2f}"
                )
                continue

            return result

        detail = "; ".join(failures) if failures else "all providers failed"
        raise ProviderError("router", detail)

    def _ordered_providers(self, request: CompletionRequest | None = None) -> list[Provider]:
        providers = [
            provider
            for provider in self.providers.values()
            if provider.is_available()
            and self._provider_allowed(provider)
            and self._provider_matches_request(provider, request)
        ]
        return sorted(providers, key=lambda provider: provider.config.priority)

    def _provider_allowed(self, provider: Provider) -> bool:
        allowlist = self.settings.provider_allowlist
        if allowlist is None:
            return True
        return provider.provider_slug in allowlist

    @staticmethod
    def _provider_matches_request(provider: Provider, request: CompletionRequest | None) -> bool:
        if request is None or request.provider_slug is None:
            return True
        return provider.provider_slug == request.provider_slug
```

---

## `app/src/router/registry.py`

```python
"""Environment-based router registry for SpaceLoom SL1a.

No API keys are stored in files. Configure providers with environment variables:

- OpenAI:
  - SPACELOOM_OPENAI_API_KEY or OPENAI_API_KEY
  - optional SPACELOOM_OPENAI_BASE_URL or OPENAI_BASE_URL
- Anthropic:
  - SPACELOOM_ANTHROPIC_API_KEY or ANTHROPIC_API_KEY
  - optional SPACELOOM_ANTHROPIC_BASE_URL
- Google/Gemini through OpenAI-compatible SDK:
  - SPACELOOM_GOOGLE_API_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY
  - optional SPACELOOM_GOOGLE_BASE_URL
- Ollama:
  - SPACELOOM_ENABLE_OLLAMA=true
  - optional SPACELOOM_OLLAMA_BASE_URL or OLLAMA_BASE_URL
"""

from __future__ import annotations

import os

from .cost import get_default_model
from .engine import Router
from .models import ProviderConfig, RouterSettings
from .providers import AnthropicProvider, GoogleProvider, OllamaProvider, OpenAIProvider, Provider


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _env_csv(name: str) -> list[str] | None:
    value = os.getenv(name)
    if not value:
        return None

    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def _append_if_available(providers: list[Provider], provider: Provider) -> None:
    if provider.is_available():
        providers.append(provider)


def build_router() -> Router:
    """Build the default SL1a "Balanceado" router from environment variables."""

    settings = RouterSettings(
        budget_cap_usd=_env_float("SPACELOOM_BUDGET_CAP_USD", 5.0),
        provider_allowlist=_env_csv("SPACELOOM_PROVIDER_ALLOWLIST"),
    )

    providers: list[Provider] = []

    openai_key = _first_env("SPACELOOM_OPENAI_API_KEY", "OPENAI_API_KEY")
    _append_if_available(
        providers,
        OpenAIProvider(
            ProviderConfig(
                provider_slug="openai",
                api_key=openai_key,
                base_url=_first_env("SPACELOOM_OPENAI_BASE_URL", "OPENAI_BASE_URL"),
                model_default=_first_env("SPACELOOM_OPENAI_MODEL", "OPENAI_MODEL")
                or get_default_model("openai"),
                priority=_env_int("SPACELOOM_OPENAI_PRIORITY", 10),
                is_enabled=_env_bool("SPACELOOM_OPENAI_ENABLED", True),
            )
        ),
    )

    anthropic_key = _first_env("SPACELOOM_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY")
    _append_if_available(
        providers,
        AnthropicProvider(
            ProviderConfig(
                provider_slug="anthropic",
                api_key=anthropic_key,
                base_url=_first_env("SPACELOOM_ANTHROPIC_BASE_URL", "ANTHROPIC_BASE_URL"),
                model_default=_first_env("SPACELOOM_ANTHROPIC_MODEL", "ANTHROPIC_MODEL")
                or get_default_model("anthropic"),
                priority=_env_int("SPACELOOM_ANTHROPIC_PRIORITY", 20),
                is_enabled=_env_bool("SPACELOOM_ANTHROPIC_ENABLED", True),
            )
        ),
    )

    google_key = _first_env("SPACELOOM_GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY")
    _append_if_available(
        providers,
        GoogleProvider(
            ProviderConfig(
                provider_slug="google",
                api_key=google_key,
                base_url=_first_env("SPACELOOM_GOOGLE_BASE_URL", "GEMINI_BASE_URL", "GOOGLE_BASE_URL")
                or "https://generativelanguage.googleapis.com/v1beta/openai/",
                model_default=_first_env("SPACELOOM_GOOGLE_MODEL", "GEMINI_MODEL", "GOOGLE_MODEL")
                or get_default_model("google"),
                priority=_env_int("SPACELOOM_GOOGLE_PRIORITY", 30),
                is_enabled=_env_bool("SPACELOOM_GOOGLE_ENABLED", True),
            )
        ),
    )

    ollama_enabled = _env_bool(
        "SPACELOOM_ENABLE_OLLAMA",
        _env_bool("SPACELOOM_OLLAMA_ENABLED", False),
    )
    _append_if_available(
        providers,
        OllamaProvider(
            ProviderConfig(
                provider_slug="ollama",
                api_key=None,
                base_url=_first_env("SPACELOOM_OLLAMA_BASE_URL", "OLLAMA_BASE_URL")
                or "http://localhost:11434/v1",
                model_default=_first_env("SPACELOOM_OLLAMA_MODEL", "OLLAMA_MODEL")
                or get_default_model("ollama"),
                priority=_env_int("SPACELOOM_OLLAMA_PRIORITY", 90),
                is_enabled=ollama_enabled,
            )
        ),
    )

    return Router(settings=settings, providers=providers)
```

---

## `app/src/router/__init__.py`

```python
"""SpaceLoom SL1a provider router."""

from .engine import Router
from .models import CompletionRequest, CompletionResult, ProviderConfig, RouterSettings, UsageRecord
from .providers import Provider, ProviderError
from .registry import build_router

__all__ = [
    "Router",
    "Provider",
    "CompletionRequest",
    "CompletionResult",
    "ProviderConfig",
    "RouterSettings",
    "UsageRecord",
    "ProviderError",
    "build_router",
]
```