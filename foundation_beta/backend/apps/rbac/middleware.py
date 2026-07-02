"""RBAC middleware: loads membership and resolves active_hat per request."""
from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest

from apps.users.models import Membership


class RBACMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        self._load_membership(request)
        response = self.get_response(request)
        return response

    def _load_membership(self, request: HttpRequest) -> None:
        request.membership = None
        request.active_hat = None

        if not request.user.is_authenticated:
            return

        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return

        try:
            membership = Membership.objects.get(
                user_id=request.user.id,
                tenant_id=tenant_id,
            )
        except Membership.DoesNotExist:
            return

        request.membership = membership
        request.active_hat = self._resolve_active_hat(request, membership)
        # Reflect the resolved hat back into the lightweight session user.
        request.user.active_hat = request.active_hat

    def _resolve_active_hat(
        self, request: HttpRequest, membership: Membership
    ) -> str | None:
        roles = membership.roles or []
        if not roles:
            return None

        header_name = getattr(settings, "ACTIVE_HAT_HEADER", "HTTP_X_ACTIVE_HAT")
        requested_hat = request.META.get(header_name)
        if requested_hat and requested_hat in roles:
            return requested_hat

        if membership.active_hat and membership.active_hat in roles:
            return membership.active_hat

        return roles[0]
