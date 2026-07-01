"""LiteLLM metadata tagger."""
from __future__ import annotations

from uuid import UUID


def litellm_metadata(tenant_id: UUID, **extra) -> dict:
    """Return LiteLLM request metadata scoped to a tenant."""
    return {"tenant_id": str(tenant_id), **extra}
