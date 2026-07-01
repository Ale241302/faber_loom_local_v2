"""Intermediate login token store (step 1 of login)."""
from __future__ import annotations

import json
import uuid
from typing import Any

from django.conf import settings

from apps.core.redis_client import get_redis_client, tenant_key
from apps.auth_session.totp import generate_login_token


def _key(tenant_id: str | uuid.UUID, token: str) -> str:
    return tenant_key(tenant_id, f"login_token:{token}")


def create_login_token(
    tenant_id: str | uuid.UUID,
    user_id: str | uuid.UUID,
    requires_2fa: bool,
) -> str:
    """Store an intermediate login token and return it."""
    token = generate_login_token()
    payload = {
        "user_id": str(user_id),
        "requires_2fa": requires_2fa,
    }
    redis = get_redis_client()
    key = _key(tenant_id, token)
    # Short-lived: 5 minutes is plenty for the 2FA step.
    redis.set(key, json.dumps(payload), ex=300)
    return token


def get_login_token(tenant_id: str | uuid.UUID, token: str) -> dict[str, Any] | None:
    redis = get_redis_client()
    raw = redis.get(_key(tenant_id, token))
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def delete_login_token(tenant_id: str | uuid.UUID, token: str) -> None:
    get_redis_client().delete(_key(tenant_id, token))
