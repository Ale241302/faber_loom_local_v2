"""Provider implementations for the SpaceLoom SL1a router."""

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


class ProviderError(RuntimeError):
    """Raised when one provider fails.

    The router catches this and falls back to the next provider when possible.
    The public message must be generic to avoid leaking provider internals.
    """

    def __init__(self, provider_slug: str, code: str):
        self.provider_slug = provider_slug
        self.code = code
        super().__init__(f"{provider_slug}: {code}")


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

            client = OpenAI(**client_kwargs, timeout=PROVIDER_TIMEOUT, max_retries=PROVIDER_MAX_RETRIES)

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
            raise ProviderError(self.provider_slug, "provider_request_failed") from exc


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
    """Moonshot Kimi through its OpenAI-compatible endpoint."""

    requires_api_key = True
    default_base_url = "https://api.moonshot.cn/v1"


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
            logger.exception("OpenAI-compatible provider failed", extra={"provider": self.provider_slug})
            raise ProviderError(self.provider_slug, "provider_request_failed") from exc
