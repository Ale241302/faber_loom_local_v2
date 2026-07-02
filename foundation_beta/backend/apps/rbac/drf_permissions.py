"""DRF permission classes for M09 RBAC."""
from __future__ import annotations

from rest_framework import permissions

from apps.rbac.permissions import emit_permission_denied, resolve_permission
from apps.users.models import MembershipStatus


class HasPermission(permissions.BasePermission):
    """DRF permission class that checks the RBAC matrix."""

    def __init__(self, surface: str, action: str):
        self.surface = surface
        self.action = action

    def __call__(self, *args, **kwargs):
        return self

    def has_permission(self, request, view):
        allowed = resolve_permission(getattr(request, "membership", None), self.surface, self.action)
        if not allowed:
            emit_permission_denied(request, self.surface, self.action)
        return allowed


class IsActiveMember(permissions.BasePermission):
    """Allow any active member of the current tenant."""

    def has_permission(self, request, view):
        membership = getattr(request, "membership", None)
        return bool(membership and membership.status == MembershipStatus.ACTIVE)
