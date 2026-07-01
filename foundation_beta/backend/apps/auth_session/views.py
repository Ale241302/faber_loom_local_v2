"""DRF views for M08 Auth Session."""
from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auth_session import session as session_store
from apps.auth_session import totp as totp_helpers
from apps.auth_session.lockout import (
    clear_attempts,
    is_locked,
    record_failed_attempt,
    remaining_seconds,
)
from apps.auth_session.login_token import (
    create_login_token,
    delete_login_token,
    get_login_token,
)
from apps.events.emit import emit_event
from apps.users.models import Membership, MembershipStatus

User = get_user_model()


def _tenant_id_from_request(request: Request) -> str:
    """Extract tenant_id from the request body."""
    return str(request.data.get("tenant_id", "")).strip()


class AllowAny(permissions.AllowAny):
    pass


class IsAuthenticated(permissions.IsAuthenticated):
    pass


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and any(r in request.user.roles for r in ("owner", "admin"))
        )


class LoginStepOneView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        email = str(request.data.get("email", "")).strip().lower()
        password = request.data.get("password", "")
        tenant_id = _tenant_id_from_request(request)

        if not email or not password or not tenant_id:
            return Response(
                {"detail": "email, password and tenant_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.check_password(password):
            with transaction.atomic():
                emit_event(
                    tenant_id=tenant_id,
                    event_type="auth.login.failed",
                    payload={"reason": "bad_password", "email": email},
                )
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            membership = Membership.objects.get(
                user=user,
                tenant_id=tenant_id,
                status=MembershipStatus.ACTIVE,
            )
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        active_hat = membership.active_hat or (membership.roles[0] if membership.roles else "")

        # If the user has not enrolled TOTP, fall back to a direct session (E1 convenience).
        requires_2fa = bool(user.totp_secret_encrypted)
        if not requires_2fa:
            session_id = session_store.create_session(
                user.id,
                tenant_id,
                membership.roles,
                active_hat,
                remember=False,
            )
            with transaction.atomic():
                emit_event(
                    tenant_id=tenant_id,
                    event_type="auth.login.success",
                    payload={"user_id": str(user.id), "method": "password"},
                )
            response = Response({"requires_2fa": False, "session_id": session_id})
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                secure=True,
                samesite="Strict",
                max_age=8 * 3600,
            )
            return response

        login_token = create_login_token(tenant_id, user.id, requires_2fa=True)
        return Response({"requires_2fa": True, "login_token": login_token})


class LoginStepTwoView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        login_token = request.data.get("login_token", "")
        code = str(request.data.get("totp", "")).strip()
        remember = bool(request.data.get("remember", False))
        tenant_id = _tenant_id_from_request(request)

        if not login_token or not code or not tenant_id:
            return Response(
                {"detail": "login_token, totp and tenant_id are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token_data = get_login_token(tenant_id, login_token)
        if not token_data:
            return Response(
                {"detail": "Invalid or expired login token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user_id = token_data["user_id"]
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if is_locked(tenant_id, user.id):
            return Response(
                {
                    "detail": "Too many failed attempts.",
                    "retry_after": remaining_seconds(tenant_id, user.id),
                },
                status=status.HTTP_423_LOCKED,
            )

        try:
            membership = Membership.objects.get(
                user=user,
                tenant_id=tenant_id,
                status=MembershipStatus.ACTIVE,
            )
        except Membership.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        secret = totp_helpers.decrypt_secret(user.totp_secret_encrypted)
        matched = totp_helpers.verify_totp(secret, code)
        if not matched:
            matched, remaining = totp_helpers.verify_backup_code(
                code, user.backup_codes_hashed
            )
            if matched:
                user.backup_codes_hashed = remaining
                user.save(update_fields=["backup_codes_hashed"])

        if not matched:
            attempts = record_failed_attempt(tenant_id, user.id)
            with transaction.atomic():
                emit_event(
                    tenant_id=tenant_id,
                    event_type="auth.2fa.failed",
                    payload={"user_id": str(user.id), "attempt": attempts},
                )
            if attempts >= 3:
                emit_event(
                    tenant_id=tenant_id,
                    event_type="auth.2fa.locked",
                    payload={"user_id": str(user.id), "lockout_seconds": 900},
                )
                return Response(
                    {"detail": "Too many failed attempts.", "retry_after": 900},
                    status=status.HTTP_423_LOCKED,
                )
            return Response(
                {"detail": "Invalid code."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        clear_attempts(tenant_id, user.id)
        delete_login_token(tenant_id, login_token)

        active_hat = membership.active_hat or (membership.roles[0] if membership.roles else "")
        session_id = session_store.create_session(
            user.id,
            tenant_id,
            membership.roles,
            active_hat,
            remember=remember,
        )

        with transaction.atomic():
            emit_event(
                tenant_id=tenant_id,
                event_type="auth.login.success",
                payload={"user_id": str(user.id), "method": "totp"},
            )

        response = Response(
            {
                "session_id": session_id,
                "user_id": str(user.id),
                "tenant_id": tenant_id,
                "roles": membership.roles,
                "active_hat": active_hat,
            }
        )
        ttl = (
            30 * 86400
            if remember
            else 8 * 3600
        )
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=ttl,
        )
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        data = request.session_data or {}
        return Response(
            {
                "user_id": data.get("user_id"),
                "tenant_id": data.get("tenant_id"),
                "roles": data.get("roles", []),
                "active_hat": data.get("active_hat", ""),
            }
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        session_id = request.COOKIES.get("session_id")
        tenant_id = getattr(request, "tenant_id", None)
        if session_id and tenant_id:
            session_store.revoke_session(session_id, tenant_id)
            if tenant_id and request.user.is_authenticated:
                emit_event(
                    tenant_id=tenant_id,
                    event_type="session.revoked",
                    payload={"user_id": request.user.id, "session_id": session_id},
                )
        response = Response({"detail": "Logged out."})
        response.delete_cookie("session_id")
        return response


class LogoutAllView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        removed = session_store.revoke_all_user_sessions(request.user.id, tenant_id)
        emit_event(
            tenant_id=tenant_id,
            event_type="session.revoked",
            payload={"user_id": request.user.id, "scope": "all", "removed": removed},
        )
        response = Response({"detail": "All sessions revoked.", "removed": removed})
        response.delete_cookie("session_id")
        return response


class RevokeSessionView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def post(self, request: Request, session_id: str) -> Response:
        tenant_id = getattr(request, "tenant_id", None)
        if not tenant_id:
            return Response({"detail": "No tenant context."}, status=status.HTTP_400_BAD_REQUEST)

        session_store.revoke_session(session_id, tenant_id)
        emit_event(
            tenant_id=tenant_id,
            event_type="session.revoked",
            payload={"revoked_by": request.user.id, "session_id": session_id},
        )
        return Response({"detail": "Session revoked."})
