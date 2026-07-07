"""Test-only request helpers.

This module is only imported inside pytest runs. It must never be loaded in
production, so it does not change any production behaviour.
"""

from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request


class TestTrustHeaderMiddleware(BaseHTTPMiddleware):
    """Inject ``request.state.user`` from trusted test headers.

    This middleware only runs while ``PYTEST_CURRENT_TEST`` is set, which means
    it is active exclusively during pytest sessions. It replaces the old
    ``FABERLOOM_DEV_TRUST_HEADERS`` production variable by moving the header
    parsing into pure test harness code.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if os.getenv("PYTEST_CURRENT_TEST"):
            tenant_id = request.headers.get("x-tenant-id")
            user_id = request.headers.get("x-user-id")
            actor_id = request.headers.get("x-actor-id")
            role = request.headers.get("x-actor-role")
            if any(v is not None for v in (tenant_id, user_id, actor_id, role)):
                effective_user_id = user_id or "local"
                request.state.user = {
                    "tenant_id": tenant_id or "default",
                    "user_id": effective_user_id,
                    "actor_id": actor_id or effective_user_id,
                    "role": role or "owner",
                    "sub": effective_user_id,
                }
        return await call_next(request)
