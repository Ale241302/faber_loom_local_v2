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


def build_router() -> Router:
    """Build the default SL1a "Balanceado" router from environment variables."""

    settings = RouterSettings(
        budget_cap_usd=_env_float("SPACELOOM_BUDGET_CAP_USD", 5.0),
        provider_allowlist=_env_csv("SPACELOOM_PROVIDER_ALLOWLIST"),
    )

    providers: list[Provider] = []

    openai_key = _first_env("SPACELOOM_OPENAI_API_KEY", "OPENAI_API_KEY")
    providers.append(
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
        )
    )

    anthropic_key = _first_env("SPACELOOM_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY")
    providers.append(
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
        )
    )

    google_key = _first_env("SPACELOOM_GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY")
    providers.append(
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
        )
    )

    ollama_enabled = _env_bool(
        "SPACELOOM_ENABLE_OLLAMA",
        _env_bool("SPACELOOM_OLLAMA_ENABLED", False),
    )
    providers.append(
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
        )
    )

    return Router(settings=settings, providers=providers)
