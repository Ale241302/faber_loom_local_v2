"""Tenant middleware: extracts tenant_id from session and sets it in DB + context."""
from __future__ import annotations

from uuid import UUID

from django.conf import settings
from django.db import connection, transaction

from apps.core.tenant_context import clear_db_tenant, set_db_tenant


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant_id = self._extract_tenant_id(request)

        if tenant_id is not None:
            with transaction.atomic():
                set_db_tenant(tenant_id)
                response = self.get_response(request)
                return response
        else:
            # No tenant context; RLS will deny access to tenant-scoped tables.
            clear_db_tenant()
            return self.get_response(request)

    def _extract_tenant_id(self, request):
        """Resolve tenant_id server-side only."""
        # M08 custom Redis session already resolved tenant_id.
        if getattr(request, "tenant_id", None):
            return UUID(request.tenant_id)

        # Legacy Django session (kept for admin compatibility).
        session_value = request.session.get("tenant_id")
        if session_value:
            return UUID(session_value)

        # Test-only header for M16 tests, guarded by settings.
        if getattr(settings, "TENANT_TESTING_HEADER_ALLOWED", False):
            header = request.META.get(settings.TENANT_ID_HEADER)
            if header:
                return UUID(header)

        return None

    def process_exception(self, request, exception):
        clear_db_tenant()
        return None
