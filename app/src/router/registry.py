"""Environment-based router registry for SpaceLoom SL1a.

Provider configuration is resolved in this order of precedence:

1. Environment variables (BYOK, no persistence).
2. Encrypted local store (`SPACELOOM_CONFIG_DIR`/providers.json).
3. Built-in defaults.

Supported environment variables:

- OpenAI:
  - SPACELOOM_OPENAI_API_KEY or OPENAI_API_KEY
  - optional SPACELOOM_OPENAI_BASE_URL or OPENAI_BASE_URL
  - optional SPACELOOM_OPENAI_MODEL or OPENAI_MODEL
  - optional SPACELOOM_OPENAI_PRIORITY (default 10)
  - optional SPACELOOM_OPENAI_ENABLED (default true)
- Anthropic:
  - SPACELOOM_ANTHROPIC_API_KEY or ANTHROPIC_API_KEY
  - optional SPACELOOM_ANTHROPIC_BASE_URL or ANTHROPIC_BASE_URL
  - optional SPACELOOM_ANTHROPIC_MODEL or ANTHROPIC_MODEL
  - optional SPACELOOM_ANTHROPIC_PRIORITY (default 20)
  - optional SPACELOOM_ANTHROPIC_ENABLED (default true)
- Google/Gemini through OpenAI-compatible SDK:
  - SPACELOOM_GOOGLE_API_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY
  - optional SPACELOOM_GOOGLE_BASE_URL, GEMINI_BASE_URL, or GOOGLE_BASE_URL
  - optional SPACELOOM_GOOGLE_MODEL, GEMINI_MODEL, or GOOGLE_MODEL
  - optional SPACELOOM_GOOGLE_PRIORITY (default 30)
  - optional SPACELOOM_GOOGLE_ENABLED (default true)
- Kimi/Moonshot through OpenAI-compatible SDK:
  - SPACELOOM_KIMI_API_KEY, KIMI_API_KEY, or MOONSHOT_API_KEY
  - optional SPACELOOM_KIMI_BASE_URL or KIMI_BASE_URL
  - optional SPACELOOM_KIMI_MODEL, KIMI_MODEL, or MOONSHOT_MODEL
  - optional SPACELOOM_KIMI_PRIORITY (default 25)
  - optional SPACELOOM_KIMI_ENABLED (default true)
- Ollama (local):
  - SPACELOOM_ENABLE_OLLAMA=true or SPACELOOM_OLLAMA_ENABLED=true
  - optional SPACELOOM_OLLAMA_BASE_URL or OLLAMA_BASE_URL
  - optional SPACELOOM_OLLAMA_MODEL or OLLAMA_MODEL
  - optional SPACELOOM_OLLAMA_PRIORITY (default 90)
"""

from __future__ import annotations

import os
from typing import Any

from .config_store import ProviderConfigStore
from .cost import get_default_model
from .engine import Router
from .models import ProviderConfig, RouterSettings
from .providers import AnthropicProvider, GoogleProvider, KimiProvider, OllamaProvider, OpenAIProvider, Provider


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


def _str_or(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value
    return fallback


def _int_or(value: Any, fallback: int) -> int:
    if value is None:
        return fallback
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _bool_or(value: Any, fallback: bool) -> bool:
    if value is None:
        return fallback
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _resolve_value(env_value: str | None, stored_value: Any) -> str | None:
    """Environment wins; then stored value; then None."""

    if env_value is not None:
        return env_value
    if isinstance(stored_value, str) and stored_value.strip():
        return stored_value
    return None


def build_router() -> Router:
    """Build the default SL1a "Balanceado" router from env vars and local store."""

    settings = RouterSettings(
        budget_cap_usd=_env_float("SPACELOOM_BUDGET_CAP_USD", 5.0),
        provider_allowlist=_env_csv("SPACELOOM_PROVIDER_ALLOWLIST"),
    )

    store = ProviderConfigStore()
    stored = store.all()
    providers: list[Provider] = []

    openai_stored = stored.get("openai", {})
    providers.append(
        OpenAIProvider(
            ProviderConfig(
                provider_slug="openai",
                api_key=_resolve_value(
                    _first_env("SPACELOOM_OPENAI_API_KEY", "OPENAI_API_KEY"),
                    openai_stored.get("api_key"),
                ),
                base_url=_resolve_value(
                    _first_env("SPACELOOM_OPENAI_BASE_URL", "OPENAI_BASE_URL"),
                    openai_stored.get("base_url"),
                ),
                model_default=_resolve_value(
                    _first_env("SPACELOOM_OPENAI_MODEL", "OPENAI_MODEL"),
                    openai_stored.get("model_default"),
                )
                or get_default_model("openai"),
                priority=_int_or(openai_stored.get("priority"), _env_int("SPACELOOM_OPENAI_PRIORITY", 10)),
                is_enabled=_bool_or(
                    openai_stored.get("is_enabled"),
                    _env_bool("SPACELOOM_OPENAI_ENABLED", True),
                ),
            )
        )
    )

    anthropic_stored = stored.get("anthropic", {})
    providers.append(
        AnthropicProvider(
            ProviderConfig(
                provider_slug="anthropic",
                api_key=_resolve_value(
                    _first_env("SPACELOOM_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"),
                    anthropic_stored.get("api_key"),
                ),
                base_url=_resolve_value(
                    _first_env("SPACELOOM_ANTHROPIC_BASE_URL", "ANTHROPIC_BASE_URL"),
                    anthropic_stored.get("base_url"),
                ),
                model_default=_resolve_value(
                    _first_env("SPACELOOM_ANTHROPIC_MODEL", "ANTHROPIC_MODEL"),
                    anthropic_stored.get("model_default"),
                )
                or get_default_model("anthropic"),
                priority=_int_or(anthropic_stored.get("priority"), _env_int("SPACELOOM_ANTHROPIC_PRIORITY", 20)),
                is_enabled=_bool_or(
                    anthropic_stored.get("is_enabled"),
                    _env_bool("SPACELOOM_ANTHROPIC_ENABLED", True),
                ),
            )
        )
    )

    google_stored = stored.get("google", {})
    providers.append(
        GoogleProvider(
            ProviderConfig(
                provider_slug="google",
                api_key=_resolve_value(
                    _first_env("SPACELOOM_GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"),
                    google_stored.get("api_key"),
                ),
                base_url=_resolve_value(
                    _first_env("SPACELOOM_GOOGLE_BASE_URL", "GEMINI_BASE_URL", "GOOGLE_BASE_URL"),
                    google_stored.get("base_url"),
                )
                or "https://generativelanguage.googleapis.com/v1beta/openai/",
                model_default=_resolve_value(
                    _first_env("SPACELOOM_GOOGLE_MODEL", "GEMINI_MODEL", "GOOGLE_MODEL"),
                    google_stored.get("model_default"),
                )
                or get_default_model("google"),
                priority=_int_or(google_stored.get("priority"), _env_int("SPACELOOM_GOOGLE_PRIORITY", 30)),
                is_enabled=_bool_or(
                    google_stored.get("is_enabled"),
                    _env_bool("SPACELOOM_GOOGLE_ENABLED", True),
                ),
            )
        )
    )

    kimi_stored = stored.get("kimi", {})
    providers.append(
        KimiProvider(
            ProviderConfig(
                provider_slug="kimi",
                api_key=_resolve_value(
                    _first_env("SPACELOOM_KIMI_API_KEY", "KIMI_API_KEY", "MOONSHOT_API_KEY"),
                    kimi_stored.get("api_key"),
                ),
                base_url=_resolve_value(
                    _first_env("SPACELOOM_KIMI_BASE_URL", "KIMI_BASE_URL"),
                    kimi_stored.get("base_url"),
                ),
                model_default=_resolve_value(
                    _first_env("SPACELOOM_KIMI_MODEL", "KIMI_MODEL", "MOONSHOT_MODEL"),
                    kimi_stored.get("model_default"),
                )
                or get_default_model("kimi"),
                priority=_int_or(kimi_stored.get("priority"), _env_int("SPACELOOM_KIMI_PRIORITY", 25)),
                is_enabled=_bool_or(
                    kimi_stored.get("is_enabled"),
                    _env_bool("SPACELOOM_KIMI_ENABLED", True),
                ),
            )
        )
    )

    ollama_enabled = _env_bool(
        "SPACELOOM_ENABLE_OLLAMA",
        _env_bool("SPACELOOM_OLLAMA_ENABLED", False),
    )
    ollama_stored = stored.get("ollama", {})
    providers.append(
        OllamaProvider(
            ProviderConfig(
                provider_slug="ollama",
                api_key=None,
                base_url=_resolve_value(
                    _first_env("SPACELOOM_OLLAMA_BASE_URL", "OLLAMA_BASE_URL"),
                    ollama_stored.get("base_url"),
                )
                or "http://localhost:11434/v1",
                model_default=_resolve_value(
                    _first_env("SPACELOOM_OLLAMA_MODEL", "OLLAMA_MODEL"),
                    ollama_stored.get("model_default"),
                )
                or get_default_model("ollama"),
                priority=_int_or(ollama_stored.get("priority"), _env_int("SPACELOOM_OLLAMA_PRIORITY", 90)),
                is_enabled=_bool_or(ollama_stored.get("is_enabled"), ollama_enabled),
            )
        )
    )

    return Router(settings=settings, providers=providers)
