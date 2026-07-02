"""DRF views for M09 RBAC membership management."""
from __future__ import annotations

from datetime import timedelta
from uuid import UUID

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth_session.session import revoke_all_user_sessions
from apps.events.emit import emit_event
from apps.rbac.drf_permissions import HasPermission, IsActiveMember
from apps.rbac.permissions import set_active_hat
from apps.users.models import Membership, MembershipStatus

User = get_user_model()


def _membership_to_dict(m: Membership) -> dict:
    return {
        "id": str(m.id),
        "user_id": str(m.user_id),
        "tenant_id": str(m.tenant_id),
        "roles": m.roles or [],
        "active_hat": m.active_hat,
        "status": m.status,
        "invited_by": str(m.invited_by_id) if m.invited_by_id else None,
        "invited_at": m.invited_at.isoformat() if m.invited_at else None,
        "accepted_at": m.accepted_at.isoformat() if m.accepted_at else None,
    }


def _is_last_owner(tenant_id: str | UUID, exclude_user_id: str | UUID | None = None) -> bool:
    qs = Membership.objects.filter(
        tenant_id=tenant_id,
        status=MembershipStatus.ACTIVE,
        roles__contains=["owner"],
    )
    if exclude_user_id:
        qs = qs.exclude(user_id=exclude_user_id)
    return not qs.exists()


class MembershipListView(APIView):
    permission_classes = [HasPermission("users", "view")]

    def get(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        qs = Membership.objects.filter(tenant_id=tenant_id).select_related("user")
        results = []
        for m in qs:
            data = _membership_to_dict(m)
            data["email"] = m.user.email
            results.append(data)
        return Response(results)


class MembershipCreateView(APIView):
    permission_classes = [HasPermission("users", "invite")]

    def post(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        email = str(request.data.get("email", "")).strip().lower()
        roles = request.data.get("roles", [])
        if not email or not roles:
            return Response(
                {"detail": "email and roles are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # E1 guard: only owner/admin can invite; admin cannot create owner.
        actor_roles = getattr(request.user, "roles", [])
        if "owner" not in actor_roles and "owner" in roles:
            return Response(
                {"detail": "Only Owner can create another Owner."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"display_name": email.split("@")[0]},
        )

        if Membership.objects.filter(user=user, tenant_id=tenant_id).exists():
            return Response(
                {"detail": "User is already a member of this tenant."},
                status=status.HTTP_409_CONFLICT,
            )

        ttl_days = int(getattr(settings, "INVITATION_TTL_DAYS", 7))
        with transaction.atomic():
            membership = Membership.objects.create(
                user=user,
                tenant_id=tenant_id,
                roles=roles,
                active_hat=roles[0],
                status=MembershipStatus.INVITED,
                invited_by_id=request.user.id,
                invited_at=timezone.now(),
            )
            emit_event(
                tenant_id=tenant_id,
                event_type="user.invited",
                payload={
                    "user_id": str(user.id),
                    "roles": roles,
                    "invited_by": request.user.id,
                    "expires_at": (timezone.now() + timedelta(days=ttl_days)).isoformat(),
                },
            )

        return Response(_membership_to_dict(membership), status=status.HTTP_201_CREATED)


class MembershipDetailView(APIView):
    permission_classes = [HasPermission("users", "change_roles")]

    def patch(self, request: Request, membership_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            membership = Membership.objects.get(id=membership_id, tenant_id=tenant_id)
        except Membership.DoesNotExist:
            return Response({"detail": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)

        new_roles = request.data.get("roles")
        if not new_roles:
            return Response({"detail": "roles is required."}, status=status.HTTP_400_BAD_REQUEST)

        actor_roles = getattr(request.user, "roles", [])
        # Admin cannot modify Owner.
        if "owner" in (membership.roles or []) and "owner" not in actor_roles:
            return Response(
                {"detail": "Only Owner can modify an Owner."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Admin cannot promote to owner.
        if "owner" in new_roles and "owner" not in actor_roles:
            return Response(
                {"detail": "Only Owner can assign Owner role."},
                status=status.HTTP_403_FORBIDDEN,
            )

        previous_roles = membership.roles or []
        previous_hat = membership.active_hat
        with transaction.atomic():
            membership.roles = new_roles
            if membership.active_hat not in new_roles:
                membership.active_hat = new_roles[0]
            membership.save(update_fields=["roles", "active_hat", "updated_at"])
            emit_event(
                tenant_id=tenant_id,
                event_type="user.role_changed",
                payload={
                    "user_id": str(membership.user_id),
                    "previous_roles": previous_roles,
                    "new_roles": new_roles,
                    "previous_hat": previous_hat,
                    "new_hat": membership.active_hat,
                    "changed_by": request.user.id,
                },
            )

        return Response(_membership_to_dict(membership))


class RevokeMembershipView(APIView):
    permission_classes = [HasPermission("users", "revoke")]

    def post(self, request: Request, membership_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            membership = Membership.objects.get(id=membership_id, tenant_id=tenant_id)
        except Membership.DoesNotExist:
            return Response({"detail": "Membership not found."}, status=status.HTTP_404_NOT_FOUND)

        # Cannot revoke the last active owner.
        if (
            "owner" in (membership.roles or [])
            and membership.status == MembershipStatus.ACTIVE
            and _is_last_owner(tenant_id, exclude_user_id=membership.user_id)
        ):
            return Response(
                {"detail": "Cannot revoke the last Owner of the tenant."},
                status=status.HTTP_403_FORBIDDEN,
            )

        actor_roles = getattr(request.user, "roles", [])
        # Admin cannot revoke Owner.
        if "owner" in (membership.roles or []) and "owner" not in actor_roles:
            return Response(
                {"detail": "Only Owner can revoke an Owner."},
                status=status.HTTP_403_FORBIDDEN,
            )

        with transaction.atomic():
            membership.status = MembershipStatus.REVOKED
            membership.active_hat = ""
            membership.save(update_fields=["status", "active_hat", "updated_at"])
            revoke_all_user_sessions(membership.user_id, tenant_id)
            emit_event(
                tenant_id=tenant_id,
                event_type="user.revoked",
                payload={
                    "user_id": str(membership.user_id),
                    "revoked_by": request.user.id,
                },
            )

        return Response({"detail": "Membership revoked.", "id": str(membership.id)})


class SetActiveHatView(APIView):
    permission_classes = [IsActiveMember]

    def post(self, request: Request) -> Response:
        membership = getattr(request, "membership", None)
        if not membership:
            return Response({"detail": "No membership context."}, status=status.HTTP_400_BAD_REQUEST)

        hat = str(request.data.get("hat", "")).strip()
        if not hat:
            return Response({"detail": "hat is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not set_active_hat(membership, hat):
            return Response(
                {"detail": "Invalid hat for this membership."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update the current session's active_hat so permissions follow immediately.
        session_id = request.COOKIES.get("session_id")
        if session_id and request.tenant_id:
            from apps.auth_session.session import get_session, revoke_session

            payload = get_session(session_id, request.tenant_id)
            if payload:
                payload["active_hat"] = hat
                # We cannot easily update TTL atomically without rewriting; revoke and recreate
                # would change session_id, which is disruptive. For E1 we accept that the hat
                # change is reflected in the request via RBACMiddleware; the session refreshes
                # on next login.

        return Response({"active_hat": hat})
