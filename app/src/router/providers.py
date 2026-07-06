"""Provider implementations for the FaberLoom SL1a router."""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any


logger = logging.getLogger(__name__)


# Default SDK timeout/retry policy for SL1a.
PROVIDER_TIMEOUT = 30.0
PROVIDER_MAX_RETRIES = 1

from .cost import estimate_cost
from .models import CompletionRequest, CompletionResult, ProviderConfig


DEFAULT_MAX_TOKENS = 1024

# Kimi Code / Coding Plan keys (prefix sk-kimi-) use a separate OpenAI-compatible
# endpoint and require a whitelisted User-Agent to avoid 403 access-denied errors.
KIMI_CODE_BASE_URL = "https://api.kimi.com/coding/v1"
KIMI_CODE_USER_AGENT = "KimiCLI/1.30.0"


class ProviderError(RuntimeError):
    """Raised when one provider fails.

    The router catches this and falls back to the next provider when possible.
    ``detail`` may contain provider-specific diagnostics and is surfaced in
    logs and the provider-test endpoint so operators can see the real cause.
    """

    def __init__(self, provider_slug: str, code: str, detail: str | None = None):
        self.provider_slug = provider_slug
        self.code = code
        self.detail = detail
        super().__init__(f"{provider_slug}: {code}" + (f" - {detail}" if detail else ""))


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


def _error_detail(exc: Exception) -> str:
    """Return a short diagnostic string from an OpenAI/Anthropic exception.

    Includes the provider's HTTP status, code and raw response body when available
    so the UI can surface the real cause (401 invalid_api_key, 404 model_not_found,
    connection error, etc.). Avoids duplicating the body when the SDK message already
    contains it.
    """

    # OpenAI SDK errors expose .message, .code / .status and .body.
    message = getattr(exc, "message", None)
    code = getattr(exc, "code", None) or getattr(exc, "status", None)
    body = getattr(exc, "body", None)

    if message:
        text = str(message)
        # The OpenAI SDK message already includes the status and the JSON body.
        if code and str(code) not in text:
            text = f"{code} - {text}"
        return text

    if body is not None:
        try:
            return json.dumps(body, ensure_ascii=False) if isinstance(body, dict) else str(body)
        except Exception:  # pragma: no cover - defensive
            return str(body)

    if code:
        return str(code)

    return str(exc)


class _OpenAICompatibleProvider(Provider):
    """Shared implementation for OpenAI-compatible chat.completions APIs."""

    default_base_url: str | None = None

    def _client_api_key(self) -> str:
        return self.config.api_key or "ollama"

    def _client_base_url(self) -> str | None:
        return self.config.base_url or self.default_base_url

    def _client_default_headers(self) -> dict[str, str]:
        """Optional default headers for the HTTP client (e.g. User-Agent)."""
        return {}

    def _build_client(self) -> Any:
        """Build and return an OpenAI SDK client configured for this provider."""

        from openai import OpenAI

        client_kwargs: dict[str, Any] = {"api_key": self._client_api_key()}
        base_url = self._client_base_url()
        if base_url:
            client_kwargs["base_url"] = base_url
        default_headers = self._client_default_headers()
        if default_headers:
            client_kwargs["default_headers"] = default_headers
        return OpenAI(**client_kwargs, timeout=PROVIDER_TIMEOUT, max_retries=PROVIDER_MAX_RETRIES)

    def list_models(self) -> list[str]:
        """List available model ids from the provider's /models endpoint."""

        if not self.is_available():
            raise ProviderError(self.provider_slug, "provider is not configured")
        try:
            client = self._build_client()
            return [m.id for m in client.models.list().data]
        except Exception as exc:
            logger.exception("Failed to list models", extra={"provider": self.provider_slug})
            raise ProviderError(self.provider_slug, "provider_request_failed", detail=_error_detail(exc)) from exc

    def complete(self, request: CompletionRequest) -> CompletionResult:
        if not self.is_available():
            raise ProviderError(self.provider_slug, "provider is not configured")

        start = time.perf_counter()
        model = request.model or self.config.model_default

        try:
            client = self._build_client()

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
            logger.exception("OpenAI-compatible provider failed", extra={"provider": self.provider_slug})
            raise ProviderError(self.provider_slug, "provider_request_failed", detail=_error_detail(exc)) from exc


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


class KimiProvider(_OpenAICompatibleProvider):
    """Moonshot Kimi through its OpenAI-compatible endpoint.

    Moonshot has two regional endpoints: the international ``.ai`` endpoint and the
    China ``.cn`` endpoint. Some API keys are only valid against one of them. When a
    request fails with a 401 authentication error we transparently try the alternate
    endpoint once, so users do not have to guess which region their key belongs to.

    Keys prefixed ``sk-kimi-`` are Kimi Code / Coding Plan keys; they authenticate
    against the dedicated ``https://api.kimi.com/coding/v1`` endpoint and require a
    whitelisted ``User-Agent`` header. Those keys are routed automatically.
    """

    requires_api_key = True
    default_base_url = "https://api.moonshot.ai/v1"

    def _is_kimi_code_key(self) -> bool:
        key = self.config.api_key or ""
        return key.startswith("sk-kimi-")

    def _client_base_url(self) -> str | None:
        # Kimi Code keys have their own endpoint unless the user explicitly overrides it.
        if self._is_kimi_code_key() and not self.config.base_url:
            return KIMI_CODE_BASE_URL
        return super()._client_base_url()

    def _client_default_headers(self) -> dict[str, str]:
        if self._is_kimi_code_key():
            return {"User-Agent": KIMI_CODE_USER_AGENT}
        return {}

    def _alternate_base_url(self) -> str | None:
        current = self._client_base_url()
        if current == "https://api.moonshot.ai/v1":
            return "https://api.moonshot.cn/v1"
        if current == "https://api.moonshot.cn/v1":
            return "https://api.moonshot.ai/v1"
        # No alternate for the Kimi Code endpoint; the key only works there.
        return None

    @staticmethod
    def _is_auth_error(detail: str | None) -> bool:
        if not detail:
            return False
        lowered = detail.lower()
        return "401" in lowered and ("invalid authentication" in lowered or "invalid_authentication" in lowered)

    def _run_with_alternate_base_url(self, operation: Any) -> Any:
        """Run ``operation`` using the alternate regional endpoint."""

        alternate = self._alternate_base_url()
        if alternate is None:
            raise ProviderError(self.provider_slug, "provider_request_failed", detail="no alternate endpoint available")

        original = self.config.base_url
        self.config.base_url = alternate
        try:
            return operation()
        finally:
            self.config.base_url = original

    def list_models(self) -> list[str]:
        try:
            return super().list_models()
        except ProviderError as exc:
            if not self._is_auth_error(exc.detail) or self._is_kimi_code_key():
                raise
            logger.info("Kimi auth failed on %s; trying alternate endpoint", self._client_base_url())
            return self._run_with_alternate_base_url(lambda: super(KimiProvider, self).list_models())

    def complete(self, request: CompletionRequest) -> CompletionResult:
        # The Kimi Code endpoint only accepts temperature == 1.0 for its models.
        if self._is_kimi_code_key() and request.temperature != 1.0:
            request = request.model_copy(update={"temperature": 1.0})
        try:
            return super().complete(request)
        except ProviderError as exc:
            if not self._is_auth_error(exc.detail) or self._is_kimi_code_key():
                raise
            logger.info("Kimi auth failed on %s; trying alternate endpoint", self._client_base_url())
            return self._run_with_alternate_base_url(lambda: super(KimiProvider, self).complete(request))


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

            client = Anthropic(**client_kwargs, timeout=PROVIDER_TIMEOUT, max_retries=PROVIDER_MAX_RETRIES)

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
            logger.exception("Anthropic provider failed", extra={"provider": self.provider_slug})
            raise ProviderError(self.provider_slug, "provider_request_failed", detail=_error_detail(exc)) from exc


class StubImageProvider(Provider):
    """Fake image-generation provider for E2-4 testing and demos.

    Requires no API key and always returns a deterministic placeholder URL.
    """

    requires_api_key = False

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._image_counter = 0

    def is_available(self) -> bool:
        return self.config.is_enabled

    def complete(self, request: CompletionRequest) -> CompletionResult:
        import uuid

        start = time.time()
        model = request.model or self.config.model_default or "fake-image-gen"
        prompt = "\n".join(
            str(m.get("content", "")) for m in request.messages if m.get("role") == "user"
        )[:200]
        self._image_counter += 1
        content = f"stub://image/{uuid.uuid4().hex}?prompt={prompt.replace(' ', '_')}"
        input_tokens = 0
        output_tokens = 0
        return CompletionResult(
            content=content,
            model=model,
            provider_slug=self.provider_slug,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=estimate_cost(model, input_tokens, output_tokens),
            duration_ms=_duration_ms(start),
        )
