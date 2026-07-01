"""Redis helpers enforcing tenant-scoped keys."""
from __future__ import annotations

import re
from uuid import UUID

SAFE_SEGMENT_RE = re.compile(r"^[a-zA-Z0-9_\-\.:/]+$")


def tenant_key(tenant_id: UUID, suffix: str) -> str:
    """Build a tenant-prefixed Redis key."""
    if not SAFE_SEGMENT_RE.match(suffix):
        raise ValueError(f"Invalid Redis key suffix: {suffix}")
    return f"tenant:{tenant_id}:{suffix}"


def require_tenant_prefix(key: str, tenant_id: UUID) -> None:
    """Validate that a Redis key belongs to the given tenant."""
    prefix = f"tenant:{tenant_id}:"
    if not key.startswith(prefix):
        raise ValueError(f"Redis key must start with {prefix}")


def get_redis_client():
    """Return a Redis client from the default cache location."""
    from django.conf import settings
    from redis import Redis

    return Redis.from_url(settings.CACHES["default"]["LOCATION"], decode_responses=True)
