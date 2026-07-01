"""TOTP brute-force lockout helper backed by Redis."""
from __future__ import annotations

import uuid

from django.conf import settings

from apps.core.redis_client import get_redis_client, tenant_key


def _key(tenant_id: str | uuid.UUID, user_id: str | uuid.UUID) -> str:
    return tenant_key(tenant_id, f"totp_lock:{user_id}")


def record_failed_attempt(tenant_id: str | uuid.UUID, user_id: str | uuid.UUID) -> int:
    """Increment failed TOTP attempt counter and return current count."""
    redis = get_redis_client()
    key = _key(tenant_id, user_id)
    count = redis.incr(key)
    if count == 1:
        redis.expire(key, settings.TOTP_LOCKOUT_SECONDS)
    return int(count)


def is_locked(tenant_id: str | uuid.UUID, user_id: str | uuid.UUID) -> bool:
    redis = get_redis_client()
    count = redis.get(_key(tenant_id, user_id))
    if count is None:
        return False
    return int(count) >= settings.TOTP_ATTEMPTS_LIMIT


def clear_attempts(tenant_id: str | uuid.UUID, user_id: str | uuid.UUID) -> None:
    get_redis_client().delete(_key(tenant_id, user_id))


def remaining_seconds(tenant_id: str | uuid.UUID, user_id: str | uuid.UUID) -> int:
    redis = get_redis_client()
    return int(redis.ttl(_key(tenant_id, user_id)))
