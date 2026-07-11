"""Contracts for the FaberLoom SL1a provider router.

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
    spent_usd: float = Field(default=0.0, ge=0.0)

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
    key_origin: str | None = None


class ProviderConfig(BaseModel):
    """Runtime config for a provider. API keys may come from env or tenant store."""

    provider_slug: str
    api_key: str | None = None
    base_url: str | None = None
    model_default: str
    priority: int
    is_enabled: bool
    key_origin: str | None = "platform"


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
