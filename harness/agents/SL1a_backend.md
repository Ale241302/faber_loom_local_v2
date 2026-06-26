## Resumen de cambios

> Nota: el entorno actual está en **sandbox read-only**, así que no pude escribir físicamente los archivos ni ejecutar `graphify update .`. Abajo dejo el contenido completo listo para aplicar.

Implementación SL1a propuesta:

- Nuevo paquete `app/src/router/` con:
  - proveedores OpenAI / Anthropic / Google / Ollama con imports SDK lazy.
  - registry desde env vars + `provider_config`.
  - engine con allowlist, preset default `Balanceado`, fallback ordenado y budget cap.
  - ledger de costos con tabla `usage_record` + mirror opcional `app/data/usage.jsonl`.
- `SCHEMA_VERSION = 3` y migración v3:
  - `usage_record`
  - `provider_config`
- Nuevos helpers DB:
  - `create_chat`, `get_chat`, `list_messages`, `append_message`
  - `insert_usage_record`, `get_workspace_usage_total`
  - `list_provider_configs`, `save_provider_config`
- Nuevas rutas API:
  - `POST /api/chats`
  - `GET /api/chats/{chat_id}/messages`
  - `POST /api/chats/{chat_id}/messages`
  - `GET /api/providers`
  - `GET /api/budget`
- Tests unitarios router:
  - fallback
  - budget cap
  - allowlist

```python:app/src/router/__init__.py
"""Provider router for SpaceLoom SL1a."""

from .engine import BudgetExceededError, NoAvailableProviderError, Router, RouterError
from .models import CompletionRequest, CompletionResult, ProviderConfig, RouterSettings, UsageRecord
from .providers import Provider, ProviderError, ProviderUnavailableError

__all__ = [
    "BudgetExceededError",
    "CompletionRequest",
    "CompletionResult",
    "NoAvailableProviderError",
    "Provider",
    "ProviderConfig",
    "ProviderError",
    "ProviderUnavailableError",
    "Router",
    "RouterError",
    "RouterSettings",
    "UsageRecord",
]
```

```python:app/src/router/models.py
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


MessageRole = Literal["system", "user", "assistant", "tool"]


class CompletionMessage(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1)


class CompletionRequest(BaseModel):
    """Provider-neutral completion request.

    `chat_id` and `message_id` are optional at the router layer so tests and
    future non-chat invocations can use the same interface. API routes fill them
    when routing chat messages.
    """

    model_config = ConfigDict(extra="forbid")

    messages: list[CompletionMessage] = Field(min_length=1)
    workspace_id: str | None = None
    chat_id: str | None = None
    message_id: str | None = None
    model_preset: str = "Balanceado"
    provider_allowlist: list[str] | None = None
    model: str | None = None
    max_tokens: int = Field(default=800, ge=1, le=8000)
    temperature: float = Field(default=0.4, ge=0.0, le=2.0)
    budget_cap_usd: float | None = Field(default=None, gt=0)
    current_spend_usd: float = Field(default=0.0, ge=0.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    routine_version: str | None = None
    skill_version: str | None = None
    source_version: str | None = None

    @field_validator("provider_allowlist")
    @classmethod
    def provider_allowlist_must_not_be_empty(
        cls, value: list[str] | None
    ) -> list[str] | None:
        if value is not None and not value:
            raise ValueError("provider_allowlist cannot be empty when provided")
        return value


class CompletionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider_slug: str
    model: str
    content: str
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0.0, ge=0.0)
    finish_reason: str | None = None
    fallback_from: list[str] = Field(default_factory=list)
    latency_ms: int | None = Field(default=None, ge=0)
    message_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ProviderConfig(BaseModel):
    """Runtime provider config.

    `api_key` is intentionally excluded from serialization. Today BYO keys come
    from env vars; tomorrow managed keys can decrypt `api_key_encrypted` behind
    this same seam.
    """

    model_config = ConfigDict(extra="forbid")

    id: str | None = None
    workspace_id: str | None = None
    provider_slug: str
    display_name: str
    api_key: str | None = Field(default=None, exclude=True)
    api_key_encrypted: str | None = None
    base_url: str | None = None
    is_enabled: bool = False
    priority: int = 100
    model_default: str
    status: str = "disabled"
    status_reason: str | None = None
    source: Literal["env", "db", "default"] = "default"


class RouterSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_preset: str = "Balanceado"
    provider_allowlist: list[str] = Field(
        default_factory=lambda: ["openai", "anthropic", "google", "ollama"]
    )
    fallback_order: list[str] = Field(
        default_factory=lambda: ["openai", "anthropic", "google", "ollama"]
    )
    budget_cap_usd: float = Field(default=5.0, gt=0)
    mirror_usage_jsonl: bool = True


class UsageRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    workspace_id: str
    chat_id: str | None = None
    message_id: str | None = None
    provider_slug: str
    model: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    cost_usd: float = Field(ge=0.0)
    budget_cap_usd: float = Field(gt=0)
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
```

```python:app/src/router/cost.py
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

from ..context import Context
from ..db import DATA_DIR, insert_usage_record, new_id, transaction, utc_now
from ..models import SCHEMA_VERSION
from .models import CompletionMessage, CompletionRequest, CompletionResult, UsageRecord


# Approximate USD prices per 1K tokens. This is intentionally small for SL1a;
# exact provider billing reconciliation can replace it once the ledger has real
# usage data.
PRICE_TABLE_USD_PER_1K: dict[str, tuple[float, float]] = {
    "gpt-4o-mini": (0.00015, 0.00060),
    "gpt-4o": (0.00500, 0.01500),
    "claude-3-5-haiku-latest": (0.00080, 0.00400),
    "claude-3-5-sonnet-latest": (0.00300, 0.01500),
    "gemini-1.5-flash": (0.000075, 0.00030),
    "gemini-1.5-pro": (0.00350, 0.01050),
    "llama3.1": (0.0, 0.0),
}

DEFAULT_PRICE_USD_PER_1K = (0.00100, 0.00300)

_usage_lock = threading.Lock()


def approximate_token_count(text: str) -> int:
    """Tiny local estimator for preflight budget checks.

    It intentionally overestimates short content by returning at least one token.
    """

    stripped = text.strip()
    if not stripped:
        return 0
    return max(1, len(stripped) // 4)


def estimate_input_tokens(messages: list[CompletionMessage]) -> int:
    return sum(approximate_token_count(message.content) for message in messages)


def price_for_model(model: str) -> tuple[float, float]:
    return PRICE_TABLE_USD_PER_1K.get(model, DEFAULT_PRICE_USD_PER_1K)


def calculate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    input_price, output_price = price_for_model(model)
    cost = ((input_tokens / 1000.0) * input_price) + ((output_tokens / 1000.0) * output_price)
    return round(cost, 8)


def estimate_request_cost_usd(request: CompletionRequest, model: str) -> float:
    input_tokens = estimate_input_tokens(request.messages)
    output_tokens = request.max_tokens
    return calculate_cost_usd(model, input_tokens, output_tokens)


class CostLedger:
    """Cost ledger seam.

    SQLite is the source of truth. JSONL is an optional inspectable local mirror,
    matching the AuditWriter pattern.
    """

    def __init__(self, usage_path: Path | None = None) -> None:
        self.usage_path = usage_path or (DATA_DIR / "usage.jsonl")

    def get_workspace_spend_usd(self, ctx: Context, conn: sqlite3.Connection) -> float:
        from ..db import get_workspace_usage_total

        return get_workspace_usage_total(ctx, conn)

    def record_usage(
        self,
        ctx: Context,
        conn: sqlite3.Connection,
        request: CompletionRequest,
        result: CompletionResult,
        *,
        message_id: str | None = None,
        budget_cap_usd: float,
        mirror_jsonl: bool = True,
    ) -> UsageRecord:
        outer_transaction = conn.in_transaction
        created_at = utc_now()
        record = UsageRecord(
            id=new_id("usage"),
            workspace_id=ctx.require_scoped_workspace(),
            chat_id=request.chat_id,
            message_id=message_id or result.message_id or request.message_id,
            provider_slug=result.provider_slug,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=result.cost_usd,
            budget_cap_usd=budget_cap_usd,
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id,
            actor_id=ctx.resolved_actor_id(),
            actor_role_at_decision=ctx.actor_role_at_decision,
            routine_version=request.routine_version,
            skill_version=request.skill_version,
            schema_version=SCHEMA_VERSION,
            source_version=request.source_version,
            approved_by=None,
            created_at=created_at,
        )

        with transaction(conn):
            insert_usage_record(ctx, conn, record.model_dump())

        if mirror_jsonl and not outer_transaction:
            self.mirror(record)
        return record

    def mirror(self, record: UsageRecord) -> None:
        self.usage_path.parent.mkdir(parents=True, exist_ok=True)
        with _usage_lock:
            with self.usage_path.open("a", encoding="utf-8") as handle:
                handle.write(record.model_dump_json() + "\n")
```

```python:app/src/router/providers.py
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any

from .cost import calculate_cost_usd, estimate_input_tokens
from .models import CompletionRequest, CompletionResult, ProviderConfig


class ProviderError(RuntimeError):
    """Base provider failure."""


class ProviderUnavailableError(ProviderError):
    """Provider cannot be used because config, SDK, or local service is unavailable."""


class Provider(ABC):
    slug: str
    display_name: str

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self.slug = config.provider_slug
        self.display_name = config.display_name

    @property
    def is_enabled(self) -> bool:
        return self.config.is_enabled

    @property
    def model_default(self) -> str:
        return self.config.model_default

    def resolve_model(self, request: CompletionRequest) -> str:
        return request.model or self.config.model_default

    @abstractmethod
    def complete(self, request: CompletionRequest) -> CompletionResult:
        raise NotImplementedError

    def _disabled_error(self) -> None:
        if not self.config.is_enabled:
            raise ProviderUnavailableError(
                f"Provider '{self.slug}' is disabled: {self.config.status_reason or 'not configured'}"
            )


def _openai_messages(request: CompletionRequest) -> list[dict[str, str]]:
    return [{"role": message.role, "content": message.content} for message in request.messages]


class OpenAIProvider(Provider):
    def complete(self, request: CompletionRequest) -> CompletionResult:
        self._disabled_error()
        if not self.config.api_key:
            raise ProviderUnavailableError("OPENAI_API_KEY is not configured")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderUnavailableError("openai SDK is not installed") from exc

        model = self.resolve_model(request)
        client = OpenAI(api_key=self.config.api_key, timeout=30.0)
        started = time.monotonic()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=_openai_messages(request),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        except Exception as exc:  # provider SDK exception hierarchy varies by version
            raise ProviderError(f"OpenAI completion failed: {exc}") from exc

        latency_ms = int((time.monotonic() - started) * 1000)
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        input_tokens = int(getattr(usage, "prompt_tokens", 0) or estimate_input_tokens(request.messages))
        output_tokens = int(getattr(usage, "completion_tokens", 0) or estimate_input_tokens([]))
        finish_reason = getattr(response.choices[0], "finish_reason", None)

        return CompletionResult(
            provider_slug=self.slug,
            model=model,
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=calculate_cost_usd(model, input_tokens, output_tokens),
            finish_reason=finish_reason,
            latency_ms=latency_ms,
        )


class AnthropicProvider(Provider):
    def complete(self, request: CompletionRequest) -> CompletionResult:
        self._disabled_error()
        if not self.config.api_key:
            raise ProviderUnavailableError("ANTHROPIC_API_KEY is not configured")

        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ProviderUnavailableError("anthropic SDK is not installed") from exc

        model = self.resolve_model(request)
        system_parts = [message.content for message in request.messages if message.role == "system"]
        messages = [
            {"role": message.role, "content": message.content}
            for message in request.messages
            if message.role in {"user", "assistant"}
        ]

        client = Anthropic(api_key=self.config.api_key, timeout=30.0)
        started = time.monotonic()

        try:
            response = client.messages.create(
                model=model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system="\n\n".join(system_parts) if system_parts else None,
                messages=messages,
            )
        except Exception as exc:
            raise ProviderError(f"Anthropic completion failed: {exc}") from exc

        latency_ms = int((time.monotonic() - started) * 1000)
        content = "".join(
            block.text for block in getattr(response, "content", []) if getattr(block, "type", "") == "text"
        )
        usage = getattr(response, "usage", None)
        input_tokens = int(getattr(usage, "input_tokens", 0) or estimate_input_tokens(request.messages))
        output_tokens = int(getattr(usage, "output_tokens", 0) or 0)
        stop_reason = getattr(response, "stop_reason", None)

        return CompletionResult(
            provider_slug=self.slug,
            model=model,
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=calculate_cost_usd(model, input_tokens, output_tokens),
            finish_reason=stop_reason,
            latency_ms=latency_ms,
        )


class GoogleProvider(Provider):
    """Gemini through the OpenAI-compatible endpoint.

    This keeps the provider interface identical to OpenAIProvider while retaining
    the BYO GOOGLE_API_KEY seam.
    """

    def complete(self, request: CompletionRequest) -> CompletionResult:
        self._disabled_error()
        if not self.config.api_key:
            raise ProviderUnavailableError("GOOGLE_API_KEY is not configured")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderUnavailableError("openai SDK is not installed") from exc

        model = self.resolve_model(request)
        base_url = self.config.base_url or "https://generativelanguage.googleapis.com/v1beta/openai/"
        client = OpenAI(api_key=self.config.api_key, base_url=base_url, timeout=30.0)
        started = time.monotonic()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=_openai_messages(request),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        except Exception as exc:
            raise ProviderError(f"Google Gemini completion failed: {exc}") from exc

        latency_ms = int((time.monotonic() - started) * 1000)
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        input_tokens = int(getattr(usage, "prompt_tokens", 0) or estimate_input_tokens(request.messages))
        output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        finish_reason = getattr(response.choices[0], "finish_reason", None)

        return CompletionResult(
            provider_slug=self.slug,
            model=model,
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=calculate_cost_usd(model, input_tokens, output_tokens),
            finish_reason=finish_reason,
            latency_ms=latency_ms,
        )


class OllamaProvider(Provider):
    """Local Ollama via OpenAI-compatible API.

    Ollama is optional. If localhost is not running, the router catches the
    provider failure and falls back to the next allowed provider.
    """

    def complete(self, request: CompletionRequest) -> CompletionResult:
        self._disabled_error()

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderUnavailableError("openai SDK is not installed") from exc

        model = self.resolve_model(request)
        base_url = self.config.base_url or "http://localhost:11434/v1"
        client = OpenAI(api_key="ollama", base_url=base_url, timeout=15.0)
        started = time.monotonic()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=_openai_messages(request),
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
        except Exception as exc:
            raise ProviderError(f"Ollama completion failed: {exc}") from exc

        latency_ms = int((time.monotonic() - started) * 1000)
        content = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        input_tokens = int(getattr(usage, "prompt_tokens", 0) or estimate_input_tokens(request.messages))
        output_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
        finish_reason = getattr(response.choices[0], "finish_reason", None)

        return CompletionResult(
            provider_slug=self.slug,
            model=model,
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=calculate_cost_usd(model, input_tokens, output_tokens),
            finish_reason=finish_reason,
            latency_ms=latency_ms,
        )
```

```python:app/src/router/registry.py
from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass

from ..context import Context
from .models import ProviderConfig, RouterSettings
from .providers import AnthropicProvider, GoogleProvider, OllamaProvider, OpenAIProvider, Provider


PROVIDER_CLASSES: dict[str, type[Provider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "ollama": OllamaProvider,
}


@dataclass(slots=True)
class ProviderRegistry:
    providers: list[Provider]
    settings: RouterSettings

    def by_slug(self) -> dict[str, Provider]:
        return {provider.slug: provider for provider in self.providers}

    def status_snapshot(self) -> list[dict]:
        return [
            {
                "provider_slug": provider.slug,
                "display_name": provider.display_name,
                "is_enabled": provider.config.is_enabled,
                "status": provider.config.status,
                "status_reason": provider.config.status_reason,
                "priority": provider.config.priority,
                "model_default": provider.config.model_default,
                "source": provider.config.source,
            }
            for provider in sorted(self.providers, key=lambda item: item.config.priority)
        ]


def _csv_env(name: str, default: list[str]) -> list[str]:
    raw = os.getenv(name)
    if not raw:
        return default
    values = [part.strip() for part in raw.split(",") if part.strip()]
    return values or default


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def load_router_settings() -> RouterSettings:
    return RouterSettings(
        provider_allowlist=_csv_env(
            "SPACELOOM_PROVIDER_ALLOWLIST",
            ["openai", "anthropic", "google", "ollama"],
        ),
        fallback_order=_csv_env(
            "SPACELOOM_FALLBACK_ORDER",
            ["openai", "anthropic", "google", "ollama"],
        ),
        budget_cap_usd=_float_env("SPACELOOM_BUDGET_USD", 5.0),
        mirror_usage_jsonl=os.getenv("SPACELOOM_USAGE_JSONL", "1").strip().lower()
        not in {"0", "false", "no"},
    )


def _default_provider_configs() -> dict[str, ProviderConfig]:
    openai_key = os.getenv("OPENAI_API_KEY") or None
    anthropic_key = os.getenv("ANTHROPIC_API_KEY") or None
    google_key = os.getenv("GOOGLE_API_KEY") or None
    ollama_base_url = os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434/v1"

    return {
        "openai": ProviderConfig(
            provider_slug="openai",
            display_name="OpenAI",
            api_key=openai_key,
            is_enabled=bool(openai_key),
            priority=10,
            model_default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            status="available" if openai_key else "disabled",
            status_reason=None if openai_key else "OPENAI_API_KEY missing",
            source="env",
        ),
        "anthropic": ProviderConfig(
            provider_slug="anthropic",
            display_name="Anthropic",
            api_key=anthropic_key,
            is_enabled=bool(anthropic_key),
            priority=20,
            model_default=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
            status="available" if anthropic_key else "disabled",
            status_reason=None if anthropic_key else "ANTHROPIC_API_KEY missing",
            source="env",
        ),
        "google": ProviderConfig(
            provider_slug="google",
            display_name="Google Gemini",
            api_key=google_key,
            base_url=os.getenv(
                "GOOGLE_OPENAI_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai/",
            ),
            is_enabled=bool(google_key),
            priority=30,
            model_default=os.getenv("GOOGLE_MODEL", "gemini-1.5-flash"),
            status="available" if google_key else "disabled",
            status_reason=None if google_key else "GOOGLE_API_KEY missing",
            source="env",
        ),
        "ollama": ProviderConfig(
            provider_slug="ollama",
            display_name="Ollama",
            api_key=None,
            base_url=ollama_base_url,
            is_enabled=os.getenv("SPACELOOM_DISABLE_OLLAMA", "").strip().lower()
            not in {"1", "true", "yes"},
            priority=40,
            model_default=os.getenv("OLLAMA_MODEL", "llama3.1"),
            status="available",
            status_reason="Optional local provider; runtime health checked on use",
            source="env",
        ),
    }


def _apply_db_overrides(
    configs: dict[str, ProviderConfig],
    ctx: Context | None,
    conn: sqlite3.Connection | None,
) -> dict[str, ProviderConfig]:
    if ctx is None or conn is None:
        return configs

    try:
        from ..db import list_provider_configs

        rows = list_provider_configs(ctx, conn)
    except Exception:
        return configs

    for row in rows:
        slug = row["provider_slug"]
        existing = configs.get(slug)
        if existing is None:
            continue

        enabled_by_env = bool(existing.api_key) or slug == "ollama"
        db_enabled = bool(row["is_enabled"])
        configs[slug] = existing.model_copy(
            update={
                "id": row["id"],
                "workspace_id": row["workspace_id"],
                "api_key_encrypted": row.get("api_key_encrypted"),
                "is_enabled": db_enabled and enabled_by_env,
                "priority": row["priority"],
                "model_default": row["model_default"] or existing.model_default,
                "status": "available" if db_enabled and enabled_by_env else "disabled",
                "status_reason": None
                if db_enabled and enabled_by_env
                else existing.status_reason or "Disabled in workspace provider_config",
                "source": "db",
            }
        )

    return configs


def build_provider_registry(
    ctx: Context | None = None,
    conn: sqlite3.Connection | None = None,
) -> ProviderRegistry:
    settings = load_router_settings()
    configs = _apply_db_overrides(_default_provider_configs(), ctx, conn)

    providers: list[Provider] = []
    for slug, config in configs.items():
        provider_class = PROVIDER_CLASSES.get(slug)
        if provider_class is None:
            continue
        providers.append(provider_class(config))

    return ProviderRegistry(providers=providers, settings=settings)
```

```python:app/src/router/engine.py
from __future__ import annotations

import sqlite3

from ..context import Context
from .cost import CostLedger, calculate_cost_usd, estimate_request_cost_usd
from .models import CompletionRequest, CompletionResult, RouterSettings
from .providers import Provider, ProviderError


class RouterError(RuntimeError):
    pass


class BudgetExceededError(RouterError):
    pass


class NoAvailableProviderError(RouterError):
    pass


class Router:
    """Minimal SL1a router.

    Supports:
    - provider allowlist
    - preset "Balanceado" as the default routing policy
    - ordered fallback
    - preflight budget cap checks
    """

    def __init__(
        self,
        providers: list[Provider],
        *,
        settings: RouterSettings | None = None,
        cost_ledger: CostLedger | None = None,
    ) -> None:
        self.providers = providers
        self.settings = settings or RouterSettings()
        self.cost_ledger = cost_ledger

    def complete(
        self,
        request: CompletionRequest,
        *,
        ctx: Context | None = None,
        conn: sqlite3.Connection | None = None,
    ) -> CompletionResult:
        candidates = self._candidate_providers(request)
        if not candidates:
            raise NoAvailableProviderError("No enabled provider matches the allowlist")

        budget_cap = request.budget_cap_usd or self.settings.budget_cap_usd
        spent = self._current_spend_usd(request, ctx=ctx, conn=conn)

        if spent >= budget_cap:
            raise BudgetExceededError(
                f"Budget cap reached: spent ${spent:.4f} of ${budget_cap:.4f}"
            )

        failures: list[str] = []
        budget_blocked: list[str] = []

        for provider in candidates:
            model = request.model or provider.model_default
            estimated_cost = estimate_request_cost_usd(request, model)
            if spent + estimated_cost > budget_cap:
                budget_blocked.append(provider.slug)
                continue

            try:
                result = provider.complete(request)
            except ProviderError as exc:
                failures.append(f"{provider.slug}: {exc}")
                continue
            except Exception as exc:
                failures.append(f"{provider.slug}: {exc}")
                continue

            if result.cost_usd == 0 and (result.input_tokens or result.output_tokens):
                result.cost_usd = calculate_cost_usd(
                    result.model,
                    result.input_tokens,
                    result.output_tokens,
                )

            if spent + result.cost_usd > budget_cap:
                raise BudgetExceededError(
                    f"Completion would exceed budget cap: "
                    f"${spent + result.cost_usd:.4f} > ${budget_cap:.4f}"
                )

            result.fallback_from = [failure.split(":", 1)[0] for failure in failures]
            return result

        if budget_blocked and len(budget_blocked) == len(candidates):
            raise BudgetExceededError(
                f"Request would exceed budget cap ${budget_cap:.4f}; "
                f"blocked providers: {', '.join(budget_blocked)}"
            )

        detail = "; ".join(failures) if failures else "No provider could complete the request"
        raise NoAvailableProviderError(detail)

    def _current_spend_usd(
        self,
        request: CompletionRequest,
        *,
        ctx: Context | None,
        conn: sqlite3.Connection | None,
    ) -> float:
        if self.cost_ledger is not None and ctx is not None and conn is not None:
            return self.cost_ledger.get_workspace_spend_usd(ctx, conn)
        return request.current_spend_usd

    def _candidate_providers(self, request: CompletionRequest) -> list[Provider]:
        settings_allowlist = set(self.settings.provider_allowlist)
        request_allowlist = set(request.provider_allowlist) if request.provider_allowlist else None

        allowed = settings_allowlist
        if request_allowlist is not None:
            allowed = allowed.intersection(request_allowlist)

        enabled = [
            provider
            for provider in self.providers
            if provider.slug in allowed and provider.is_enabled
        ]

        order_index = {
            slug: index for index, slug in enumerate(self.settings.fallback_order)
        }

        return sorted(
            enabled,
            key=lambda provider: (
                order_index.get(provider.slug, 999),
                provider.config.priority,
                provider.slug,
            ),
        )
```

```python:app/src/models.py
"""SQLite schema migrations and Pydantic v2 API models for SpaceLoom."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SCHEMA_VERSION = 3
CURRENT_SCHEMA_VERSION = SCHEMA_VERSION


# Migration policy:
# - v1 is the original skeleton contract.
# - v2 hardens the contract-first seams required before closing SL0:
#   routine/routine_run and a uniform latent-field surface.
# - v3 (SL1a) adds the router cost ledger and per-workspace provider config.
MIGRATIONS: dict[int, str] = {
    1: """
    CREATE TABLE IF NOT EXISTS workspace (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        tenant_id TEXT,
        user_id TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS kb_source (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        content_text TEXT,
        content_blob BLOB,
        meta_json TEXT NOT NULL DEFAULT '{}',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT NOT NULL DEFAULT 'v1',
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS chat (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        title TEXT NOT NULL,
        model_preset TEXT NOT NULL DEFAULT 'default',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS message (
        id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        role TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
        content_json TEXT NOT NULL,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS draft (
        id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        status TEXT NOT NULL CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected', 'exported')),
        content_json TEXT NOT NULL,
        sources_json TEXT NOT NULL DEFAULT '[]',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        approved_by TEXT,
        approved_at TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        action TEXT NOT NULL,
        payload_json TEXT NOT NULL DEFAULT '{}',
        approved_by TEXT,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_kb_source_workspace_id ON kb_source(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_chat_workspace_id ON chat(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_message_chat_id ON message(chat_id);
    CREATE INDEX IF NOT EXISTS idx_draft_chat_id ON draft(chat_id);
    CREATE INDEX IF NOT EXISTS idx_audit_log_workspace_id ON audit_log(workspace_id);
    """,
    2: """
    ALTER TABLE workspace ADD COLUMN actor_id TEXT;
    ALTER TABLE workspace ADD COLUMN actor_role_at_decision TEXT;
    ALTER TABLE workspace ADD COLUMN routine_version TEXT;
    ALTER TABLE workspace ADD COLUMN skill_version TEXT;
    ALTER TABLE workspace ADD COLUMN source_version TEXT;
    ALTER TABLE workspace ADD COLUMN approved_by TEXT;

    ALTER TABLE kb_source ADD COLUMN actor_id TEXT;
    ALTER TABLE kb_source ADD COLUMN actor_role_at_decision TEXT;
    ALTER TABLE kb_source ADD COLUMN approved_by TEXT;

    ALTER TABLE chat ADD COLUMN actor_id TEXT;
    ALTER TABLE chat ADD COLUMN actor_role_at_decision TEXT;
    ALTER TABLE chat ADD COLUMN approved_by TEXT;

    ALTER TABLE message ADD COLUMN workspace_id TEXT;
    ALTER TABLE message ADD COLUMN approved_by TEXT;

    CREATE TABLE IF NOT EXISTS routine (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        name TEXT NOT NULL,
        skill_md TEXT NOT NULL DEFAULT '',
        tools_allowlist TEXT NOT NULL DEFAULT '[]',
        schema_output_json TEXT NOT NULL DEFAULT '{}',
        preset_id TEXT,
        trigger_json TEXT NOT NULL DEFAULT '{}',
        persona_md TEXT NOT NULL DEFAULT '',
        is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 2,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS routine_run (
        id TEXT PRIMARY KEY,
        routine_id TEXT NOT NULL,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        input_json TEXT NOT NULL DEFAULT '{}',
        output_json TEXT NOT NULL DEFAULT '{}',
        evidence_json TEXT NOT NULL DEFAULT '[]',
        status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'requires_hitl')),
        edit_pct REAL,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 2,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (routine_id) REFERENCES routine(id) ON DELETE CASCADE,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    UPDATE message
    SET workspace_id = (
        SELECT chat.workspace_id FROM chat WHERE chat.id = message.chat_id
    )
    WHERE workspace_id IS NULL;

    CREATE INDEX IF NOT EXISTS idx_message_workspace_id ON message(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_routine_workspace_id ON routine(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_routine_run_workspace_id ON routine_run(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_routine_run_routine_id ON routine_run(routine_id);
    """,
    3: """
    CREATE TABLE IF NOT EXISTS usage_record (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        chat_id TEXT,
        message_id TEXT,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        provider_slug TEXT NOT NULL,
        model TEXT NOT NULL,
        input_tokens INTEGER NOT NULL DEFAULT 0,
        output_tokens INTEGER NOT NULL DEFAULT 0,
        cost_usd REAL NOT NULL DEFAULT 0,
        budget_cap_usd REAL NOT NULL,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 3,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE,
        FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE SET NULL,
        FOREIGN KEY (message_id) REFERENCES message(id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS provider_config (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        provider_slug TEXT NOT NULL,
        api_key_encrypted TEXT,
        is_enabled INTEGER NOT NULL DEFAULT 1 CHECK (is_enabled IN (0, 1)),
        priority INTEGER NOT NULL DEFAULT 100,
        model_default TEXT,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 3,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE,
        UNIQUE(workspace_id, provider_slug)
    );

    CREATE INDEX IF NOT EXISTS idx_usage_record_workspace_id ON usage_record(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_usage_record_chat_id ON usage_record(chat_id);
    CREATE INDEX IF NOT EXISTS idx_usage_record_created_at ON usage_record(created_at);
    CREATE INDEX IF NOT EXISTS idx_provider_config_workspace_id ON provider_config(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_provider_config_provider_slug ON provider_config(provider_slug);
    """,
}


class HealthRead(BaseModel):
    status: Literal["ok"] = "ok"
    app: str = "SpaceLoom"
    schema_version: int
    database_path: str


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=140)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Workspace name cannot be blank")
        return stripped

    @field_validator("slug")
    @classmethod
    def slug_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("Workspace slug cannot be blank")
        return stripped


class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
    updated_at: str


class WorkspaceListRead(BaseModel):
    workspaces: list[WorkspaceRead]


class AuditEvent(BaseModel):
    id: str
    workspace_id: str
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str | None = None
    user_id: str | None = None
    approved_by: str | None = None
    schema_version: int = SCHEMA_VERSION
    routine_version: str | None = None
    skill_version: str | None = None
    source_version: str | None = None
    created_at: str


class ChatCreate(BaseModel):
    workspace_id: str = Field(min_length=1)
    title: str = Field(default="New chat", min_length=1, max_length=160)
    model_preset: str = Field(default="Balanceado", min_length=1, max_length=80)

    @field_validator("title", "model_preset")
    @classmethod
    def value_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Value cannot be blank")
        return stripped


class ChatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    title: str
    model_preset: str
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str


class MessageCreate(BaseModel):
    workspace_id: str | None = Field(default=None, min_length=1)
    content: str = Field(min_length=1, max_length=24000)
    provider_allowlist: list[str] | None = None
    model_preset: str | None = Field(default=None, max_length=80)
    max_tokens: int = Field(default=800, ge=1, le=8000)
    temperature: float = Field(default=0.4, ge=0.0, le=2.0)

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Message content cannot be blank")
        return stripped


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    role: Literal["system", "user", "assistant", "tool"]
    content: dict[str, Any]
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str


class MessageListRead(BaseModel):
    messages: list[MessageRead]


class ChatSendRead(BaseModel):
    user_message: MessageRead
    assistant_message: MessageRead
    completion: dict[str, Any]
    usage: dict[str, Any] | None = None


class ProviderRead(BaseModel):
    provider_slug: str
    display_name: str
    is_enabled: bool
    status: str
    status_reason: str | None = None
    priority: int
    model_default: str
    source: str


class ProviderListRead(BaseModel):
    providers: list[ProviderRead]
    allowlist: list[str]


class BudgetRead(BaseModel):
    workspace_id: str
    spent_usd: float
    budget_cap_usd: float
    remaining_usd: float
    currency: Literal["USD"] = "USD"


class RoutineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    name: str
    skill_md: str
    tools_allowlist: str
    schema_output_json: str
    preset_id: str | None = None
    trigger_json: str
    persona_md: str
    is_active: int
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
    updated_at: str


class RoutineRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    routine_id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    input_json: str
    output_json: str
    evidence_json: str
    status: str
    edit_pct: float | None = None
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
```

```python:app/src/db.py
"""SQLite initialization, migrations, and data access helpers.

Raw sqlite3 keeps SpaceLoom small and local-first. Versioned migrations are
tracked in _schema_version. Every application data query takes a Context.
Bootstrap queries are explicitly named ``system_*``; workspace-owned reads must
constrain by ``ctx.workspace_id``.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import unicodedata
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .context import Context
from .models import MIGRATIONS, SCHEMA_VERSION, WorkspaceCreate


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "spaceloom.sqlite3"

WORKSPACE_COLUMNS = """
    id,
    name,
    slug,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    created_at,
    updated_at
"""

CHAT_COLUMNS = """
    id,
    workspace_id,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    title,
    model_preset,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    created_at
"""

MESSAGE_COLUMNS = """
    id,
    chat_id,
    workspace_id,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    role,
    content_json,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    created_at
"""

PROVIDER_CONFIG_COLUMNS = """
    id,
    workspace_id,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    provider_slug,
    api_key_encrypted,
    is_enabled,
    priority,
    model_default,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    created_at,
    updated_at
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return slug or "workspace"


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def message_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    payload = row_to_dict(row)
    content_json = payload.pop("content_json", "{}")
    try:
        payload["content"] = json.loads(content_json)
    except json.JSONDecodeError:
        payload["content"] = {"type": "text", "text": content_json}
    return payload


def get_database_path() -> Path:
    configured = os.getenv("SPACELOOM_DB_PATH")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DB_PATH


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def get_db() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[None]:
    outer_transaction = conn.in_transaction
    try:
        yield
    except Exception:
        if not outer_transaction:
            conn.rollback()
        raise
    else:
        if not outer_transaction:
            conn.commit()


def initialize_database(conn: sqlite3.Connection | None = None) -> None:
    owns_conn = conn is None
    conn = conn or connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS _schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )
        applied = {
            int(row["version"])
            for row in conn.execute("SELECT version FROM _schema_version").fetchall()
        }
        for version in sorted(MIGRATIONS):
            if version in applied:
                continue
            conn.executescript(MIGRATIONS[version])
            conn.execute(
                "INSERT INTO _schema_version(version, applied_at) VALUES (?, ?)",
                (version, utc_now()),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if owns_conn:
            conn.close()


init_db = initialize_database


def current_schema_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT MAX(version) AS version FROM _schema_version").fetchone()
    if row is None or row["version"] is None:
        return 0
    return int(row["version"])


def get_schema_version() -> int:
    with db_session() as conn:
        try:
            return current_schema_version(conn)
        except sqlite3.OperationalError:
            return 0


def assert_schema_current() -> None:
    actual = get_schema_version()
    if actual != SCHEMA_VERSION:
        raise RuntimeError(
            f"Database schema version {actual} does not match expected {SCHEMA_VERSION}"
        )


def _workspace_slug_exists(ctx: Context, conn: sqlite3.Connection, slug: str) -> bool:
    ctx.require_system()
    row = conn.execute("SELECT 1 FROM workspace WHERE slug = ? LIMIT 1", (slug,)).fetchone()
    return row is not None


def unique_workspace_slug(ctx: Context, conn: sqlite3.Connection, requested_slug: str) -> str:
    ctx.require_system()
    base = slugify(requested_slug)
    if not _workspace_slug_exists(ctx, conn, base):
        return base
    suffix = 2
    while True:
        candidate = f"{base}-{suffix}"
        if not _workspace_slug_exists(ctx, conn, candidate):
            return candidate
        suffix += 1


def system_list_workspaces(ctx: Context, conn: sqlite3.Connection) -> list[dict[str, Any]]:
    ctx.require_system()
    rows = conn.execute(
        f"""
        SELECT {WORKSPACE_COLUMNS}
        FROM workspace
        WHERE tenant_id IS ?
        ORDER BY created_at ASC, name ASC
        """,
        (ctx.tenant_id,),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def list_workspaces(ctx: Context, conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return system_list_workspaces(ctx, conn)


def get_workspace(ctx: Context, conn: sqlite3.Connection) -> dict[str, Any] | None:
    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        f"""
        SELECT {WORKSPACE_COLUMNS}
        FROM workspace
        WHERE id = ? AND tenant_id IS ?
        """,
        (workspace_id, ctx.tenant_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def system_get_workspace(
    ctx: Context,
    conn: sqlite3.Connection,
    workspace_id: str,
) -> dict[str, Any] | None:
    ctx.require_system()
    row = conn.execute(
        f"""
        SELECT {WORKSPACE_COLUMNS}
        FROM workspace
        WHERE id = ? AND tenant_id IS ?
        """,
        (workspace_id, ctx.tenant_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def system_get_workspace_by_slug(
    ctx: Context,
    conn: sqlite3.Connection,
    slug: str,
) -> dict[str, Any] | None:
    ctx.require_system()
    row = conn.execute(
        f"""
        SELECT {WORKSPACE_COLUMNS}
        FROM workspace
        WHERE slug = ? AND tenant_id IS ?
        """,
        (slug, ctx.tenant_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def get_workspace_by_slug(
    ctx: Context,
    conn: sqlite3.Connection,
    slug: str,
) -> dict[str, Any] | None:
    return system_get_workspace_by_slug(ctx, conn, slug)


def create_workspace(
    ctx: Context,
    conn: sqlite3.Connection,
    payload: WorkspaceCreate,
) -> dict[str, Any]:
    ctx.require_system()
    now = utc_now()
    workspace_id = new_id("ws")
    name = payload.name.strip()
    slug = unique_workspace_slug(ctx, conn, payload.slug or name)

    conn.execute(
        """
        INSERT INTO workspace(
            id,
            name,
            slug,
            tenant_id,
            user_id,
            actor_id,
            actor_role_at_decision,
            routine_version,
            skill_version,
            schema_version,
            source_version,
            approved_by,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            name,
            slug,
            ctx.tenant_id,
            ctx.user_id,
            ctx.resolved_actor_id(),
            ctx.actor_role_at_decision,
            None,
            None,
            SCHEMA_VERSION,
            None,
            None,
            now,
            now,
        ),
    )
    created = system_get_workspace(ctx, conn, workspace_id)
    if created is None:
        raise RuntimeError("Workspace was created but could not be read back")
    return created


def create_chat(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    title: str,
    model_preset: str = "Balanceado",
    routine_version: str | None = None,
    skill_version: str | None = None,
    source_version: str | None = None,
) -> dict[str, Any]:
    workspace_id = ctx.require_scoped_workspace()
    now = utc_now()
    chat_id = new_id("chat")

    conn.execute(
        """
        INSERT INTO chat(
            id,
            workspace_id,
            tenant_id,
            user_id,
            actor_id,
            actor_role_at_decision,
            title,
            model_preset,
            routine_version,
            skill_version,
            schema_version,
            source_version,
            approved_by,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chat_id,
            workspace_id,
            ctx.tenant_id,
            ctx.user_id,
            ctx.resolved_actor_id(),
            ctx.actor_role_at_decision,
            title.strip(),
            model_preset.strip(),
            routine_version,
            skill_version,
            SCHEMA_VERSION,
            source_version,
            None,
            now,
        ),
    )

    created = get_chat(ctx, conn, chat_id)
    if created is None:
        raise RuntimeError("Chat was created but could not be read back")
    return created


def get_chat(ctx: Context, conn: sqlite3.Connection, chat_id: str) -> dict[str, Any] | None:
    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        f"""
        SELECT {CHAT_COLUMNS}
        FROM chat
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
        """,
        (chat_id, workspace_id, ctx.tenant_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def append_message(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    chat_id: str,
    role: str,
    content: dict[str, Any],
    routine_version: str | None = None,
    skill_version: str | None = None,
    source_version: str | None = None,
) -> dict[str, Any]:
    workspace_id = ctx.require_scoped_workspace()
    if get_chat(ctx, conn, chat_id) is None:
        raise ValueError("Chat not found in current workspace context")

    now = utc_now()
    message_id = new_id("msg")
    conn.execute(
        """
        INSERT INTO message(
            id,
            chat_id,
            workspace_id,
            tenant_id,
            user_id,
            actor_id,
            actor_role_at_decision,
            role,
            content_json,
            routine_version,
            skill_version,
            schema_version,
            source_version,
            approved_by,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            message_id,
            chat_id,
            workspace_id,
            ctx.tenant_id,
            ctx.user_id,
            ctx.resolved_actor_id(),
            ctx.actor_role_at_decision,
            role,
            json.dumps(content, ensure_ascii=False, sort_keys=True),
            routine_version,
            skill_version,
            SCHEMA_VERSION,
            source_version,
            None,
            now,
        ),
    )

    row = conn.execute(
        f"""
        SELECT {MESSAGE_COLUMNS}
        FROM message
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
        """,
        (message_id, workspace_id, ctx.tenant_id),
    ).fetchone()
    if row is None:
        raise RuntimeError("Message was created but could not be read back")
    return message_row_to_dict(row)


def list_messages(
    ctx: Context,
    conn: sqlite3.Connection,
    chat_id: str,
) -> list[dict[str, Any]]:
    workspace_id = ctx.require_scoped_workspace()
    if get_chat(ctx, conn, chat_id) is None:
        return []

    rows = conn.execute(
        f"""
        SELECT {MESSAGE_COLUMNS}
        FROM message
        WHERE chat_id = ? AND workspace_id = ? AND tenant_id IS ?
        ORDER BY created_at ASC, id ASC
        """,
        (chat_id, workspace_id, ctx.tenant_id),
    ).fetchall()
    return [message_row_to_dict(row) for row in rows]


def insert_usage_record(
    ctx: Context,
    conn: sqlite3.Connection,
    payload: dict[str, Any],
) -> None:
    workspace_id = ctx.require_scoped_workspace()
    if payload["workspace_id"] != workspace_id:
        raise ValueError("usage_record workspace_id does not match Context")

    conn.execute(
        """
        INSERT INTO usage_record(
            id,
            workspace_id,
            chat_id,
            message_id,
            tenant_id,
            user_id,
            actor_id,
            actor_role_at_decision,
            provider_slug,
            model,
            input_tokens,
            output_tokens,
            cost_usd,
            budget_cap_usd,
            routine_version,
            skill_version,
            schema_version,
            source_version,
            approved_by,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            payload["id"],
            payload["workspace_id"],
            payload.get("chat_id"),
            payload.get("message_id"),
            payload.get("tenant_id"),
            payload.get("user_id"),
            payload.get("actor_id"),
            payload.get("actor_role_at_decision"),
            payload["provider_slug"],
            payload["model"],
            payload["input_tokens"],
            payload["output_tokens"],
            payload["cost_usd"],
            payload["budget_cap_usd"],
            payload.get("routine_version"),
            payload.get("skill_version"),
            payload["schema_version"],
            payload.get("source_version"),
            payload.get("approved_by"),
            payload["created_at"],
        ),
    )


def get_workspace_usage_total(ctx: Context, conn: sqlite3.Connection) -> float:
    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        """
        SELECT COALESCE(SUM(cost_usd), 0) AS total
        FROM usage_record
        WHERE workspace_id = ? AND tenant_id IS ?
        """,
        (workspace_id, ctx.tenant_id),
    ).fetchone()
    return float(row["total"] or 0.0)


def list_provider_configs(ctx: Context, conn: sqlite3.Connection) -> list[dict[str, Any]]:
    workspace_id = ctx.require_scoped_workspace()
    rows = conn.execute(
        f"""
        SELECT {PROVIDER_CONFIG_COLUMNS}
        FROM provider_config
        WHERE workspace_id = ? AND tenant_id IS ?
        ORDER BY priority ASC, provider_slug ASC
        """,
        (workspace_id, ctx.tenant_id),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def save_provider_config(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    provider_slug: str,
    api_key_encrypted: str | None = None,
    is_enabled: bool = True,
    priority: int = 100,
    model_default: str | None = None,
    routine_version: str | None = None,
    skill_version: str | None = None,
    source_version: str | None = None,
) -> dict[str, Any]:
    workspace_id = ctx.require_scoped_workspace()
    now = utc_now()
    config_id = new_id("prov")

    conn.execute(
        """
        INSERT INTO provider_config(
            id,
            workspace_id,
            tenant_id,
            user_id,
            actor_id,
            actor_role_at_decision,
            provider_slug,
            api_key_encrypted,
            is_enabled,
            priority,
            model_default,
            routine_version,
            skill_version,
            schema_version,
            source_version,
            approved_by,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(workspace_id, provider_slug) DO UPDATE SET
            api_key_encrypted = excluded.api_key_encrypted,
            is_enabled = excluded.is_enabled,
            priority = excluded.priority,
            model_default = excluded.model_default,
            routine_version = excluded.routine_version,
            skill_version = excluded.skill_version,
            schema_version = excluded.schema_version,
            source_version = excluded.source_version,
            actor_id = excluded.actor_id,
            actor_role_at_decision = excluded.actor_role_at_decision,
            updated_at = excluded.updated_at
        """,
        (
            config_id,
            workspace_id,
            ctx.tenant_id,
            ctx.user_id,
            ctx.resolved_actor_id(),
            ctx.actor_role_at_decision,
            provider_slug,
            api_key_encrypted,
            1 if is_enabled else 0,
            priority,
            model_default,
            routine_version,
            skill_version,
            SCHEMA_VERSION,
            source_version,
            None,
            now,
            now,
        ),
    )

    row = conn.execute(
        f"""
        SELECT {PROVIDER_CONFIG_COLUMNS}
        FROM provider_config
        WHERE workspace_id = ? AND provider_slug = ? AND tenant_id IS ?
        """,
        (workspace_id, provider_slug, ctx.tenant_id),
    ).fetchone()
    if row is None:
        raise RuntimeError("Provider config was saved but could not be read back")
    return row_to_dict(row)


def insert_audit_log(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    event_id: str,
    action: str,
    payload: dict[str, Any],
    approved_by: str | None = None,
    routine_version: str | None = None,
    skill_version: str | None = None,
    source_version: str | None = None,
    created_at: str | None = None,
) -> None:
    ctx.require_scoped_workspace()
    conn.execute(
        """
        INSERT INTO audit_log(
            id,
            workspace_id,
            tenant_id,
            user_id,
            actor_id,
            actor_role_at_decision,
            action,
            payload_json,
            approved_by,
            routine_version,
            skill_version,
            schema_version,
            source_version,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            ctx.workspace_id,
            ctx.tenant_id,
            ctx.user_id,
            ctx.resolved_actor_id(),
            ctx.actor_role_at_decision,
            action,
            json.dumps(payload, ensure_ascii=False, sort_keys=True),
            approved_by,
            routine_version,
            skill_version,
            SCHEMA_VERSION,
            source_version,
            created_at or utc_now(),
        ),
    )
```

```python:app/src/api.py
from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from .audit import audit_writer
from .context import Context, system_context
from .db import (
    append_message,
    create_chat,
    create_workspace,
    get_chat,
    get_database_path,
    get_db,
    get_schema_version,
    get_workspace,
    get_workspace_usage_total,
    list_messages,
    list_workspaces,
    transaction,
)
from .models import (
    AuditEvent,
    BudgetRead,
    ChatCreate,
    ChatRead,
    ChatSendRead,
    HealthRead,
    MessageCreate,
    MessageListRead,
    MessageRead,
    ProviderListRead,
    ProviderRead,
    WorkspaceCreate,
    WorkspaceListRead,
    WorkspaceRead,
)
from .router.cost import CostLedger
from .router.engine import BudgetExceededError, NoAvailableProviderError, Router as CompletionRouter
from .router.models import CompletionMessage, CompletionRequest
from .router.registry import build_provider_registry


router = APIRouter(prefix="/api", tags=["api"])


def context_from_request(request: Request, workspace_id: str | None = None) -> Context:
    # SL1a is still local single-user. These headers preserve the future contract
    # seam; they are not treated as security authority for multi-tenant access.
    tenant_id = request.headers.get("x-tenant-id") or None
    user_id = request.headers.get("x-user-id") or "local"
    actor_id = request.headers.get("x-actor-id") or user_id
    actor_role = request.headers.get("x-actor-role") or "owner"
    if workspace_id:
        return Context(
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            user_id=user_id,
            actor_id=actor_id,
            actor_role_at_decision=actor_role,
        )
    return system_context(
        tenant_id=tenant_id,
        user_id=user_id,
        actor_id=actor_id,
        actor_role_at_decision=actor_role,
    )


def workspace_id_from_request(request: Request, body_workspace_id: str | None = None) -> str:
    workspace_id = (
        body_workspace_id
        or request.headers.get("x-workspace-id")
        or request.query_params.get("workspace_id")
    )
    if not workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="workspace_id is required via body, x-workspace-id header, or query param",
        )
    return workspace_id


def _message_text(message: dict[str, Any]) -> str:
    content = message.get("content") or {}
    if isinstance(content, dict):
        text = content.get("text")
        if isinstance(text, str):
            return text
    return str(content)


def _completion_messages(existing_messages: list[dict[str, Any]], new_user_content: str) -> list[CompletionMessage]:
    messages = [
        CompletionMessage(role=message["role"], content=_message_text(message))
        for message in existing_messages
        if message["role"] in {"system", "user", "assistant", "tool"} and _message_text(message).strip()
    ]
    messages.append(CompletionMessage(role="user", content=new_user_content))
    return messages


@router.get("/health", response_model=HealthRead)
def health() -> HealthRead:
    return HealthRead(
        status="ok",
        schema_version=get_schema_version(),
        database_path=str(get_database_path()),
    )


@router.get("/workspaces", response_model=WorkspaceListRead)
def api_list_workspaces(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> WorkspaceListRead:
    ctx = context_from_request(request)
    return WorkspaceListRead(workspaces=[WorkspaceRead(**row) for row in list_workspaces(ctx, conn)])


@router.post("/workspaces", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def api_create_workspace(
    payload: WorkspaceCreate,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> WorkspaceRead:
    bootstrap_ctx = context_from_request(request)
    event: AuditEvent | None = None
    with transaction(conn):
        created = create_workspace(bootstrap_ctx, conn, payload)
        workspace_ctx = bootstrap_ctx.with_workspace(created["id"])
        event = audit_writer.write(
            workspace_ctx,
            conn,
            action="workspace.created",
            payload={
                "workspace_id": created["id"],
                "name": created["name"],
                "slug": created["slug"],
            },
            mirror_jsonl=False,
        )

    if event is not None:
        audit_writer.mirror(event)
    return WorkspaceRead(**created)


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceRead)
def api_get_workspace(
    workspace_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> WorkspaceRead:
    ctx = context_from_request(request, workspace_id=workspace_id)
    workspace = get_workspace(ctx, conn)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return WorkspaceRead(**workspace)


@router.post("/chats", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
def api_create_chat(
    payload: ChatCreate,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> ChatRead:
    ctx = context_from_request(request, workspace_id=payload.workspace_id)
    if get_workspace(ctx, conn) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    event: AuditEvent | None = None
    with transaction(conn):
        chat = create_chat(
            ctx,
            conn,
            title=payload.title,
            model_preset=payload.model_preset,
        )
        event = audit_writer.write(
            ctx,
            conn,
            action="chat.created",
            payload={"chat_id": chat["id"], "title": chat["title"]},
            mirror_jsonl=False,
        )

    if event is not None:
        audit_writer.mirror(event)
    return ChatRead(**chat)


@router.get("/chats/{chat_id}/messages", response_model=MessageListRead)
def api_list_chat_messages(
    chat_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> MessageListRead:
    workspace_id = workspace_id_from_request(request)
    ctx = context_from_request(request, workspace_id=workspace_id)
    if get_chat(ctx, conn, chat_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    return MessageListRead(
        messages=[MessageRead(**message) for message in list_messages(ctx, conn, chat_id)]
    )


@router.post("/chats/{chat_id}/messages", response_model=ChatSendRead)
def api_send_chat_message(
    chat_id: str,
    payload: MessageCreate,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> ChatSendRead:
    workspace_id = workspace_id_from_request(request, payload.workspace_id)
    ctx = context_from_request(request, workspace_id=workspace_id)
    chat = get_chat(ctx, conn, chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    existing = list_messages(ctx, conn, chat_id)
    registry = build_provider_registry(ctx, conn)
    ledger = CostLedger()
    completion_request = CompletionRequest(
        workspace_id=workspace_id,
        chat_id=chat_id,
        messages=_completion_messages(existing, payload.content),
        model_preset=payload.model_preset or chat["model_preset"] or "Balanceado",
        provider_allowlist=payload.provider_allowlist,
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
        budget_cap_usd=registry.settings.budget_cap_usd,
    )

    completion_router = CompletionRouter(
        registry.providers,
        settings=registry.settings,
        cost_ledger=ledger,
    )

    try:
        completion = completion_router.complete(completion_request, ctx=ctx, conn=conn)
    except BudgetExceededError as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc
    except NoAvailableProviderError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    event: AuditEvent | None = None
    usage = None
    with transaction(conn):
        user_message = append_message(
            ctx,
            conn,
            chat_id=chat_id,
            role="user",
            content={"type": "text", "text": payload.content},
        )
        assistant_message = append_message(
            ctx,
            conn,
            chat_id=chat_id,
            role="assistant",
            content={
                "type": "text",
                "text": completion.content,
                "provider_slug": completion.provider_slug,
                "model": completion.model,
                "finish_reason": completion.finish_reason,
            },
        )
        completion.message_id = assistant_message["id"]
        usage = ledger.record_usage(
            ctx,
            conn,
            completion_request,
            completion,
            message_id=assistant_message["id"],
            budget_cap_usd=registry.settings.budget_cap_usd,
            mirror_jsonl=False,
        )
        event = audit_writer.write(
            ctx,
            conn,
            action="chat.message.completed",
            payload={
                "chat_id": chat_id,
                "user_message_id": user_message["id"],
                "assistant_message_id": assistant_message["id"],
                "provider_slug": completion.provider_slug,
                "model": completion.model,
                "cost_usd": completion.cost_usd,
            },
            mirror_jsonl=False,
        )

    if usage is not None and registry.settings.mirror_usage_jsonl:
        ledger.mirror(usage)
    if event is not None:
        audit_writer.mirror(event)

    return ChatSendRead(
        user_message=MessageRead(**user_message),
        assistant_message=MessageRead(**assistant_message),
        completion=completion.model_dump(exclude={"raw"}),
        usage=usage.model_dump() if usage is not None else None,
    )


@router.get("/providers", response_model=ProviderListRead)
def api_list_providers(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> ProviderListRead:
    workspace_id = request.headers.get("x-workspace-id") or request.query_params.get("workspace_id")
    ctx = context_from_request(request, workspace_id=workspace_id) if workspace_id else None
    registry = build_provider_registry(ctx, conn if ctx else None)
    return ProviderListRead(
        providers=[ProviderRead(**item) for item in registry.status_snapshot()],
        allowlist=registry.settings.provider_allowlist,
    )


@router.get("/budget", response_model=BudgetRead)
def api_get_budget(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> BudgetRead:
    workspace_id = workspace_id_from_request(request)
    ctx = context_from_request(request, workspace_id=workspace_id)
    if get_workspace(ctx, conn) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")

    registry = build_provider_registry(ctx, conn)
    spent = get_workspace_usage_total(ctx, conn)
    cap = registry.settings.budget_cap_usd
    return BudgetRead(
        workspace_id=workspace_id,
        spent_usd=round(spent, 8),
        budget_cap_usd=cap,
        remaining_usd=round(max(0.0, cap - spent), 8),
    )
```

```python:app/tests/test_sl1a_router.py
from __future__ import annotations

import pytest

from app.src.router.engine import BudgetExceededError, NoAvailableProviderError, Router
from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig, RouterSettings
from app.src.router.providers import Provider, ProviderError


class MockProvider(Provider):
    def __init__(
        self,
        slug: str,
        *,
        enabled: bool = True,
        should_fail: bool = False,
        content: str = "ok",
        priority: int = 10,
        model: str = "gpt-4o-mini",
        cost_usd: float = 0.001,
    ) -> None:
        super().__init__(
            ProviderConfig(
                provider_slug=slug,
                display_name=slug.title(),
                is_enabled=enabled,
                priority=priority,
                model_default=model,
                status="available" if enabled else "disabled",
                source="default",
            )
        )
        self.should_fail = should_fail
        self.content = content
        self.cost_usd = cost_usd
        self.calls = 0

    def complete(self, request: CompletionRequest) -> CompletionResult:
        self.calls += 1
        if self.should_fail:
            raise ProviderError(f"{self.slug} failed")
        return CompletionResult(
            provider_slug=self.slug,
            model=self.model_default,
            content=self.content,
            input_tokens=10,
            output_tokens=10,
            cost_usd=self.cost_usd,
            finish_reason="stop",
        )


def _request(**overrides) -> CompletionRequest:
    payload = {
        "messages": [{"role": "user", "content": "Hola, crea un draft corto."}],
        "max_tokens": 100,
        "temperature": 0.2,
    }
    payload.update(overrides)
    return CompletionRequest(**payload)


def test_router_falls_back_when_first_provider_fails():
    primary = MockProvider("openai", should_fail=True, priority=10)
    fallback = MockProvider("anthropic", content="fallback response", priority=20)
    router = Router(
        [primary, fallback],
        settings=RouterSettings(
            provider_allowlist=["openai", "anthropic"],
            fallback_order=["openai", "anthropic"],
            budget_cap_usd=5.0,
        ),
    )

    result = router.complete(_request())

    assert result.provider_slug == "anthropic"
    assert result.content == "fallback response"
    assert result.fallback_from == ["openai"]
    assert primary.calls == 1
    assert fallback.calls == 1


def test_router_rejects_request_that_would_exceed_budget_cap():
    provider = MockProvider("openai", priority=10)
    router = Router(
        [provider],
        settings=RouterSettings(
            provider_allowlist=["openai"],
            fallback_order=["openai"],
            budget_cap_usd=0.000001,
        ),
    )

    with pytest.raises(BudgetExceededError):
        router.complete(_request(budget_cap_usd=0.000001))

    assert provider.calls == 0


def test_router_respects_request_provider_allowlist():
    openai = MockProvider("openai", content="openai", priority=10)
    anthropic = MockProvider("anthropic", content="anthropic", priority=20)
    router = Router(
        [openai, anthropic],
        settings=RouterSettings(
            provider_allowlist=["openai", "anthropic"],
            fallback_order=["openai", "anthropic"],
            budget_cap_usd=5.0,
        ),
    )

    result = router.complete(_request(provider_allowlist=["anthropic"]))

    assert result.provider_slug == "anthropic"
    assert openai.calls == 0
    assert anthropic.calls == 1


def test_router_raises_when_allowlist_has_no_enabled_provider():
    disabled = MockProvider("openai", enabled=False)
    router = Router(
        [disabled],
        settings=RouterSettings(
            provider_allowlist=["openai"],
            fallback_order=["openai"],
            budget_cap_usd=5.0,
        ),
    )

    with pytest.raises(NoAvailableProviderError):
        router.complete(_request())
```