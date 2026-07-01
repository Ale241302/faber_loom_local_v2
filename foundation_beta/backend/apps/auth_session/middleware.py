"""Session middleware: reads the opaque session_id cookie and loads Redis session."""
from __future__ import annotations

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest

from apps.auth_session.session import SESSION_INDEX_PREFIX, get_session
from apps.core.redis_client import get_redis_client


class SessionMiddleware:
    """Custom server-side session middleware backed by Redis."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        self._load_session(request)
        response = self.get_response(request)
        return response

    def _load_session(self, request: HttpRequest) -> None:
        request.session_data = None
        request.tenant_id = None
        request.user = AnonymousUser()

        session_id = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
        if not session_id:
            return

        redis = get_redis_client()
        tenant_id_raw = redis.get(f"{SESSION_INDEX_PREFIX}{session_id}")
        if not tenant_id_raw:
            return

        tenant_id = (
            tenant_id_raw.decode()
            if isinstance(tenant_id_raw, bytes)
            else tenant_id_raw
        )
        payload = get_session(session_id, tenant_id)
        if not payload:
            return

        request.session_data = payload
        request.tenant_id = tenant_id
        # Build a lightweight user-like object without hitting the DB on every request.
        request.user = _SessionUser(payload)


class _SessionUser:
    """Lightweight wrapper exposing the minimal user/session API."""

    def __init__(self, payload: dict):
        self.id = payload["user_id"]
        self.pk = self.id
        self.tenant_id = payload["tenant_id"]
        self.roles = payload.get("roles", [])
        self.active_hat = payload.get("active_hat", "")
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = True

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def get_username(self) -> str:
        return self.id
