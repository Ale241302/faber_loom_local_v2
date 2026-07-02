"""Permission resolver and decorator for M09 RBAC."""
from __future__ import annotations

from functools import wraps
from typing import Callable

from django.conf import settings
from rest_framework.exceptions import PermissionDenied

from apps.events.emit import emit_event
from apps.rbac.models import PermissionLevel
from apps.users.models import Membership, MembershipStatus


SURFACE_MAP = {
    "workloom": ["view", "approve", "edit", "create"],
    "workspace": ["view", "edit"],
    "agent_factory": ["view", "create", "edit"],
    "skill_factory": ["view", "create", "edit"],
    "audit": ["view", "export"],
    "config": ["view", "edit"],
    "users": ["view", "invite", "change_roles", "revoke"],
}


ACTION_LEVEL = {
    "view": PermissionLevel.READ,
    "export": PermissionLevel.READ,
    "approve": PermissionLevel.WRITE,
    "edit": PermissionLevel.WRITE,
    "create": PermissionLevel.WRITE,
    "invite": PermissionLevel.WRITE,
    "change_roles": PermissionLevel.FULL,
    "revoke": PermissionLevel.FULL,
}


def _required_level(surface: str, action: str) -> str:
    if surface == "audit" and action == "view":
        return PermissionLevel.READ_SELF
    return ACTION_LEVEL.get(action, PermissionLevel.FULL)


def resolve_permission(membership: Membership | None, surface: str, action: str) -> bool:
    """Return True if membership's active role grants surface:action."""
    if not membership or membership.status != MembershipStatus.ACTIVE:
        return False

    active_hat = _validated_active_hat(membership)
    if not active_hat:
        return False

    role = getattr(membership, "_role_cache", None)
    if role is None:
        from apps.rbac.models import Role

        try:
            role = Role.objects.get(id=active_hat)
            membership._role_cache = role
        except Role.DoesNotExist:
            return False

    permissions = role.permissions or {}
    role_level = permissions.get(surface, PermissionLevel.NONE)
    if role_level == PermissionLevel.FULL:
        return True
    required = _required_level(surface, action)
    return PermissionLevel.rank(role_level) >= PermissionLevel.rank(required)


def _validated_active_hat(membership: Membership) -> str | None:
    """Return the active hat, falling back to the first role; validate it belongs to the user."""
    roles = membership.roles or []
    if not roles:
        return None
    if membership.active_hat and membership.active_hat in roles:
        return membership.active_hat
    return roles[0]


def set_active_hat(membership: Membership, hat: str) -> bool:
    """Persist a new active hat if it belongs to the user's roles."""
    if hat not in (membership.roles or []):
        return False
    membership.active_hat = hat
    membership.save(update_fields=["active_hat", "updated_at"])
    return True


def emit_permission_denied(request, surface: str, action: str) -> None:
    """Emit a throttled permission.denied event to the outbox."""
    tenant_id = getattr(request, "tenant_id", None)
    user_id = getattr(request.user, "id", None) if request.user.is_authenticated else None
    if not tenant_id:
        return
    # Simple in-process throttle: one denied event per request is enough.
    emit_event(
        tenant_id=tenant_id,
        event_type="permission.denied",
        payload={
            "user_id": user_id,
            "surface": surface,
            "action": action,
            "active_hat": getattr(request.user, "active_hat", None),
        },
    )


def require_permission(surface: str, action: str) -> Callable:
    """DRF-compatible decorator for function-based views (APIView methods use permission classes)."""

    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            membership = getattr(request, "membership", None)
            if not resolve_permission(membership, surface, action):
                emit_permission_denied(request, surface, action)
                raise PermissionDenied(f"Requires {surface}:{action}")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
