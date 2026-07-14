"""Environment-based router registry for FaberLoom SL1a.

Provider configuration is resolved in this order of precedence:

1. Environment variables (BYOK, no persistence).
2. Encrypted local store (`FABERLOOM_CONFIG_DIR`/providers.json).
3. Built-in defaults.

Supported environment variables:

- OpenAI:
  - FABERLOOM_OPENAI_API_KEY or OPENAI_API_KEY
  - optional FABERLOOM_OPENAI_BASE_URL or OPENAI_BASE_URL
  - optional FABERLOOM_OPENAI_MODEL or OPENAI_MODEL
  - optional FABERLOOM_OPENAI_PRIORITY (default 10)
  - optional FABERLOOM_OPENAI_ENABLED (default true)
- Anthropic:
  - FABERLOOM_ANTHROPIC_API_KEY or ANTHROPIC_API_KEY
  - optional FABERLOOM_ANTHROPIC_BASE_URL or ANTHROPIC_BASE_URL
  - optional FABERLOOM_ANTHROPIC_MODEL or ANTHROPIC_MODEL
  - optional FABERLOOM_ANTHROPIC_PRIORITY (default 20)
  - optional FABERLOOM_ANTHROPIC_ENABLED (default true)
- Google/Gemini through OpenAI-compatible SDK:
  - FABERLOOM_GOOGLE_API_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY
  - optional FABERLOOM_GOOGLE_BASE_URL, GEMINI_BASE_URL, or GOOGLE_BASE_URL
  - optional FABERLOOM_GOOGLE_MODEL, GEMINI_MODEL, or GOOGLE_MODEL
  - optional FABERLOOM_GOOGLE_PRIORITY (default 30)
  - optional FABERLOOM_GOOGLE_ENABLED (default true)
- Kimi/Moonshot through OpenAI-compatible SDK:
  - FABERLOOM_KIMI_API_KEY, KIMI_API_KEY, or MOONSHOT_API_KEY
  - optional FABERLOOM_KIMI_BASE_URL or KIMI_BASE_URL
  - optional FABERLOOM_KIMI_MODEL, KIMI_MODEL, or MOONSHOT_MODEL
  - optional FABERLOOM_KIMI_PRIORITY (default 25)
  - optional FABERLOOM_KIMI_ENABLED (default true)
- Ollama (local):
  - FABERLOOM_ENABLE_OLLAMA=true or FABERLOOM_OLLAMA_ENABLED=true
  - optional FABERLOOM_OLLAMA_BASE_URL or OLLAMA_BASE_URL
  - optional FABERLOOM_OLLAMA_MODEL or OLLAMA_MODEL
  - optional FABERLOOM_OLLAMA_PRIORITY (default 90)
"""

from __future__ import annotations

import os
from typing import Any

from .config_store import ProviderConfigStore
from .cost import get_default_model
from .engine import Router
from .models import ProviderConfig, RouterSettings
from .cost import KIMI_CODE_MODELS
from .providers import (
    AnthropicProvider,
    GoogleProvider,
    KIMI_CODE_BASE_URL,
    KimiProvider,
    OllamaProvider,
    OpenAIProvider,
    Provider,
)


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


def _is_env_placeholder(value: str) -> bool:
    """Return True for values that should defer to environment variables.

    Matches the BYOK server-side fallback logic: empty strings, magic placeholders,
    or suspiciously short keys are ignored so the daemon can inject a real key.
    """

    if not value:
        return True
    stripped = value.strip()
    if stripped in {"server-default", "use-env"}:
        return True
    if len(stripped) < 20:
        return True
    return False


def _resolve_value(env_value: str | None, stored_value: Any) -> str | None:
    """Environment wins; then stored value if it looks real; then None."""

    if env_value is not None:
        return env_value
    if isinstance(stored_value, str) and not _is_env_placeholder(stored_value):
        return stored_value
    return None


def _resolve_api_key(
    env_value: str | None,
    stored_value: Any,
    *,
    tenant_id: str | None,
    byo_mode: str | None,
) -> tuple[str | None, str]:
    """Resolve API key and return (key, origin) according to BYO mode.

    - Default tenant / non-strict mode: env wins, then stored real key.
      Origin is ``platform`` when env was used, ``tenant`` when a real stored
      tenant key was used.
    - Non-default tenant + ``estricto``: only stored tenant key is allowed.
      If none exists the provider is unavailable and origin is ``unavailable``.
    """

    from ..context import DEFAULT_TENANT_ID

    effective_mode = (byo_mode or "hibrido").lower().strip()
    is_strict = tenant_id != DEFAULT_TENANT_ID and effective_mode == "estricto"

    if is_strict:
        if isinstance(stored_value, str) and not _is_env_placeholder(stored_value):
            return stored_value, "tenant"
        return None, "unavailable"

    if env_value is not None:
        return env_value, "platform"
    if isinstance(stored_value, str) and not _is_env_placeholder(stored_value):
        return stored_value, "tenant"
    return None, "unavailable"


def build_router(
    user_id: str | None = None,
    *,
    tenant_id: str | None = None,
    budget_cap_usd: float | None = None,
    provider_allowlist: list[str] | None = None,
    provider_denylist: list[str] | None = None,
    jurisdiction_allowlist: list[str] | None = None,
    byo_mode: str | None = None,
) -> Router:
    """Build the default SL1a "Balanceado" router from env vars and local store.

    When ``user_id`` is provided (typically the JWT ``sub`` claim), provider
    configuration is resolved from that user's encrypted slice. Local/test mode
    passes ``None`` or ``"local"`` and uses the shared/global configuration.

    ``tenant_id`` scopes the provider configuration to the caller's tenant; when
    omitted it falls back to the default tenant for local/single-tenant mode.

    Optional ``budget_cap_usd`` and ``provider_allowlist`` override the
    environment defaults for workspace-aware routing.

    ``provider_denylist`` y ``jurisdiction_allowlist`` transportan las
    restricciones de compliance del envelope del tenant
    (``routing_preset.envelope_json``) hasta el guard del engine. Se resuelven
    con ``resolve_effective_routing_constraints``; sin ellas el router queda en
    allow-all, que es el agujero que cierra SPEC_FB_ENVELOPE_ENFORCEMENT_v1.
    """

    settings = RouterSettings(
        budget_cap_usd=budget_cap_usd
        if budget_cap_usd is not None
        else _env_float("FABERLOOM_BUDGET_CAP_USD", 5.0),
        provider_allowlist=provider_allowlist
        if provider_allowlist is not None
        else _env_csv("FABERLOOM_PROVIDER_ALLOWLIST"),
        provider_denylist=provider_denylist,
        jurisdiction_allowlist=jurisdiction_allowlist,
    )

    store = ProviderConfigStore()
    stored = store.all(user_id, tenant_id=tenant_id)
    providers: list[Provider] = []

    openai_stored = stored.get("openai", {})
    openai_api_key, openai_key_origin = _resolve_api_key(
        _first_env("FABERLOOM_OPENAI_API_KEY", "OPENAI_API_KEY"),
        openai_stored.get("api_key"),
        tenant_id=tenant_id,
        byo_mode=byo_mode,
    )
    providers.append(
        OpenAIProvider(
            ProviderConfig(
                provider_slug="openai",
                api_key=openai_api_key,
                key_origin=openai_key_origin,
                base_url=_resolve_value(
                    _first_env("FABERLOOM_OPENAI_BASE_URL", "OPENAI_BASE_URL"),
                    openai_stored.get("base_url"),
                ),
                model_default=_resolve_value(
                    _first_env("FABERLOOM_OPENAI_MODEL", "OPENAI_MODEL"),
                    openai_stored.get("model_default"),
                )
                or get_default_model("openai"),
                priority=_int_or(openai_stored.get("priority"), _env_int("FABERLOOM_OPENAI_PRIORITY", 10)),
                is_enabled=_bool_or(
                    openai_stored.get("is_enabled"),
                    _env_bool("FABERLOOM_OPENAI_ENABLED", True),
                ),
            )
        )
    )

    anthropic_stored = stored.get("anthropic", {})
    anthropic_api_key, anthropic_key_origin = _resolve_api_key(
        _first_env("FABERLOOM_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"),
        anthropic_stored.get("api_key"),
        tenant_id=tenant_id,
        byo_mode=byo_mode,
    )
    providers.append(
        AnthropicProvider(
            ProviderConfig(
                provider_slug="anthropic",
                api_key=anthropic_api_key,
                key_origin=anthropic_key_origin,
                base_url=_resolve_value(
                    _first_env("FABERLOOM_ANTHROPIC_BASE_URL", "ANTHROPIC_BASE_URL"),
                    anthropic_stored.get("base_url"),
                ),
                model_default=_resolve_value(
                    _first_env("FABERLOOM_ANTHROPIC_MODEL", "ANTHROPIC_MODEL"),
                    anthropic_stored.get("model_default"),
                )
                or get_default_model("anthropic"),
                priority=_int_or(anthropic_stored.get("priority"), _env_int("FABERLOOM_ANTHROPIC_PRIORITY", 20)),
                is_enabled=_bool_or(
                    anthropic_stored.get("is_enabled"),
                    _env_bool("FABERLOOM_ANTHROPIC_ENABLED", True),
                ),
            )
        )
    )

    google_stored = stored.get("google", {})
    google_api_key, google_key_origin = _resolve_api_key(
        _first_env("FABERLOOM_GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"),
        google_stored.get("api_key"),
        tenant_id=tenant_id,
        byo_mode=byo_mode,
    )
    providers.append(
        GoogleProvider(
            ProviderConfig(
                provider_slug="google",
                api_key=google_api_key,
                key_origin=google_key_origin,
                base_url=_resolve_value(
                    _first_env("FABERLOOM_GOOGLE_BASE_URL", "GEMINI_BASE_URL", "GOOGLE_BASE_URL"),
                    google_stored.get("base_url"),
                )
                or "https://generativelanguage.googleapis.com/v1beta/openai/",
                model_default=_resolve_value(
                    _first_env("FABERLOOM_GOOGLE_MODEL", "GEMINI_MODEL", "GOOGLE_MODEL"),
                    google_stored.get("model_default"),
                )
                or get_default_model("google"),
                priority=_int_or(google_stored.get("priority"), _env_int("FABERLOOM_GOOGLE_PRIORITY", 30)),
                is_enabled=_bool_or(
                    google_stored.get("is_enabled"),
                    _env_bool("FABERLOOM_GOOGLE_ENABLED", True),
                ),
            )
        )
    )

    kimi_stored = stored.get("kimi", {})
    kimi_api_key, kimi_key_origin = _resolve_api_key(
        _first_env("FABERLOOM_KIMI_API_KEY", "KIMI_API_KEY", "MOONSHOT_API_KEY"),
        kimi_stored.get("api_key"),
        tenant_id=tenant_id,
        byo_mode=byo_mode,
    )
    kimi_base_url = _resolve_value(
        _first_env("FABERLOOM_KIMI_BASE_URL", "KIMI_BASE_URL"),
        kimi_stored.get("base_url"),
    )
    kimi_model_default = _resolve_value(
        _first_env("FABERLOOM_KIMI_MODEL", "KIMI_MODEL", "MOONSHOT_MODEL"),
        kimi_stored.get("model_default"),
    )

    # Kimi Code / Coding Plan keys (sk-kimi-) need the dedicated coding endpoint
    # and a coding-capable default model. Respect explicit user overrides.
    if kimi_api_key and kimi_api_key.startswith("sk-kimi-"):
        if kimi_base_url in {None, "https://api.moonshot.ai/v1", "https://api.moonshot.cn/v1"}:
            kimi_base_url = KIMI_CODE_BASE_URL
        if not kimi_model_default or kimi_model_default not in KIMI_CODE_MODELS:
            kimi_model_default = "kimi-for-coding"
    else:
        if not kimi_base_url:
            kimi_base_url = "https://api.moonshot.ai/v1"
        if not kimi_model_default:
            kimi_model_default = get_default_model("kimi")

    providers.append(
        KimiProvider(
            ProviderConfig(
                provider_slug="kimi",
                api_key=kimi_api_key,
                key_origin=kimi_key_origin,
                base_url=kimi_base_url,
                model_default=kimi_model_default,
                priority=_int_or(kimi_stored.get("priority"), _env_int("FABERLOOM_KIMI_PRIORITY", 25)),
                is_enabled=_bool_or(
                    kimi_stored.get("is_enabled"),
                    _env_bool("FABERLOOM_KIMI_ENABLED", True),
                ),
            )
        )
    )

    ollama_enabled = _env_bool(
        "FABERLOOM_ENABLE_OLLAMA",
        _env_bool("FABERLOOM_OLLAMA_ENABLED", False),
    )
    ollama_stored = stored.get("ollama", {})
    providers.append(
        OllamaProvider(
            ProviderConfig(
                provider_slug="ollama",
                api_key=None,
                key_origin=None,
                base_url=_resolve_value(
                    _first_env("FABERLOOM_OLLAMA_BASE_URL", "OLLAMA_BASE_URL"),
                    ollama_stored.get("base_url"),
                )
                or "http://localhost:11434/v1",
                model_default=_resolve_value(
                    _first_env("FABERLOOM_OLLAMA_MODEL", "OLLAMA_MODEL"),
                    ollama_stored.get("model_default"),
                )
                or get_default_model("ollama"),
                priority=_int_or(ollama_stored.get("priority"), _env_int("FABERLOOM_OLLAMA_PRIORITY", 90)),
                is_enabled=_bool_or(ollama_stored.get("is_enabled"), ollama_enabled),
            )
        )
    )

    return Router(settings=settings, providers=providers)
