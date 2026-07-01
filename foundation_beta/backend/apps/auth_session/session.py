"""Server-side Redis session store for M08 Auth Session."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from django.conf import settings

from apps.core.redis_client import get_redis_client, tenant_key


SESSION_INDEX_PREFIX = "session:"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_session(
    user_id: str | uuid.UUID,
    tenant_id: str | uuid.UUID,
    roles: list[str],
    active_hat: str,
    remember: bool = False,
) -> str:
    """Create a server-side session and return the opaque session id."""
    session_id = uuid.uuid4().hex
    ttl = settings.SESSION_REMEMBER_TTL_SECONDS if remember else settings.SESSION_TTL_SECONDS
    now = _now()
    payload = {
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "active_hat": active_hat,
        "issued_at": now.isoformat(),
        "expires_at": (now + timedelta(seconds=ttl)).isoformat(),
        "remember": remember,
    }
    redis = get_redis_client()
    # Global index to resolve tenant_id from session_id.
    redis.set(f"{SESSION_INDEX_PREFIX}{session_id}", str(tenant_id), ex=ttl)
    # Tenant-scoped payload key.
    key = tenant_key(tenant_id, f"session:{session_id}")
    redis.set(key, json.dumps(payload), ex=ttl)
    return session_id


def get_session(session_id: str, tenant_id: str | uuid.UUID) -> dict[str, Any] | None:
    """Fetch session payload if it exists and has not expired."""
    key = tenant_key(tenant_id, f"session:{session_id}")
    raw = get_redis_client().get(key)
    if not raw:
        return None
    try:
        payload = json.loads(raw)
        # Refresh TTL on active use for non-remember sessions.
        if not payload.get("remember"):
            get_redis_client().expire(key, settings.SESSION_TTL_SECONDS)
        return payload
    except json.JSONDecodeError:
        return None


def revoke_session(session_id: str, tenant_id: str | uuid.UUID) -> None:
    """Delete a single session."""
    redis = get_redis_client()
    redis.delete(f"{SESSION_INDEX_PREFIX}{session_id}")
    key = tenant_key(tenant_id, f"session:{session_id}")
    redis.delete(key)


def revoke_all_user_sessions(user_id: str | uuid.UUID, tenant_id: str | uuid.UUID) -> int:
    """Delete all sessions belonging to a user in a tenant."""
    redis = get_redis_client()
    pattern = f"tenant:{tenant_id}:session:*"
    removed = 0
    for key in redis.scan_iter(match=pattern):
        raw = redis.get(key)
        if not raw:
            continue
        try:
            payload = json.loads(raw)
            if payload.get("user_id") == str(user_id):
                session_id = key.decode().split(":")[-1]
                redis.delete(f"{SESSION_INDEX_PREFIX}{session_id}")
                redis.delete(key)
                removed += 1
        except json.JSONDecodeError:
            continue
    return removed


def list_user_sessions(user_id: str | uuid.UUID, tenant_id: str | uuid.UUID) -> list[dict[str, Any]]:
    """Return metadata for all active sessions of a user in a tenant."""
    redis = get_redis_client()
    pattern = f"tenant:{tenant_id}:session:*"
    sessions: list[dict[str, Any]] = []
    for key in redis.scan_iter(match=pattern):
        raw = redis.get(key)
        if not raw:
            continue
        try:
            payload = json.loads(raw)
            if payload.get("user_id") == str(user_id):
                # key format: tenant:<id>:session:<session_id>
                session_id = key.decode().split(":")[-1]
                sessions.append(
                    {
                        "session_id": session_id,
                        "issued_at": payload.get("issued_at"),
                        "expires_at": payload.get("expires_at"),
                        "active_hat": payload.get("active_hat"),
                        "remember": payload.get("remember"),
                    }
                )
        except json.JSONDecodeError:
            continue
    return sessions
