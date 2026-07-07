"""JWT authentication with httpOnly cookies for the FaberLoom web deployment.

Users and passwords are read from the ``FABERLOOM_USERS`` environment variable
as a JSON object, e.g.:

    FABERLOOM_USERS='{"admin@example.com":"secret"}'

Access tokens are short-lived JWTs delivered as ``HttpOnly``, ``Secure`` (over
HTTPS) and ``SameSite=Strict`` cookies. A refresh token is stored in a separate
``HttpOnly`` cookie and rotated on every use.

If the variable is empty or unset and ``FABERLOOM_AUTH_DISABLED`` is set, the
request is treated as the legacy local user so existing tests keep working.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from .context import DEFAULT_TENANT_ID
from .db import get_db
from .rate_limit import rate_limit_dependency
from .connectors.smtp import SMTPConfig, send_email as smtp_send_email, SMTPError

auth_router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    token_type: str = "bearer"
    email: str


ACCESS_TOKEN_TTL_MINUTES = int(os.getenv("FABERLOOM_ACCESS_TOKEN_TTL_MINUTES", "60"))
REFRESH_TOKEN_TTL_DAYS = int(os.getenv("FABERLOOM_REFRESH_TOKEN_TTL_DAYS", "7"))


def _users() -> dict[str, str]:
    raw = os.getenv("FABERLOOM_USERS", "")
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


def _secret() -> str:
    secret = os.getenv("FABERLOOM_SECRET_KEY")
    if not secret:
        auth_disabled = os.getenv("FABERLOOM_AUTH_DISABLED")
        if not auth_disabled and _users():
            raise RuntimeError(
                "FABERLOOM_SECRET_KEY is required when FABERLOOM_USERS is configured"
            )
        # Local dev/test fallback only when auth is disabled or no users.
        secret = "faberloom-dev-secret-replace-me"
    return secret


def _cookie_settings(request: Request) -> dict[str, Any]:
    return {
        "httponly": True,
        "secure": request.url.scheme == "https",
        "samesite": "strict",
        "path": "/",
    }


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _create_refresh_token(
    conn: sqlite3.Connection, user_id: str
) -> tuple[str, datetime]:
    token = "rt_" + secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=REFRESH_TOKEN_TTL_DAYS)
    token_hash = _hash_token(token)
    conn.execute(
        """
        INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "rtid_" + secrets.token_urlsafe(16),
            user_id,
            token_hash,
            expires.isoformat(),
            now.isoformat(),
        ),
    )
    return token, expires


def _refresh_token_for_cookie(
    conn: sqlite3.Connection, cookie_token: str
) -> sqlite3.Row | None:
    row = conn.execute(
        """
        SELECT * FROM refresh_tokens
        WHERE token_hash = ? AND revoked_at IS NULL AND expires_at > ?
        """,
        (_hash_token(cookie_token), datetime.now(timezone.utc).isoformat()),
    ).fetchone()
    return row


def _revoke_refresh_token(conn: sqlite3.Connection, token_hash: str) -> None:
    conn.execute(
        "UPDATE refresh_tokens SET revoked_at = ? WHERE token_hash = ?",
        (datetime.now(timezone.utc).isoformat(), token_hash),
    )


def create_access_token(
    email: str,
    tenant_id: str | None = None,
    user_id: str | None = None,
    role: str | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "role": role or "admin",
        "tenant_id": tenant_id or DEFAULT_TENANT_ID,
        "user_id": user_id or email,
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
    }
    return jwt.encode(payload, _secret(), algorithm="HS256")


def _local_user() -> dict[str, Any]:
    return {"sub": "local", "role": "owner", "tenant_id": DEFAULT_TENANT_ID}


def _resolve_user_from_foundation(email: str) -> dict[str, Any] | None:
    """Resolve a Foundation user by email and return real identity claims.

    This is intentionally import-local to avoid a circular import: foundation/core
    already imports get_current_user from this module for the SSO bridge.
    """
    try:
        from .foundation.core import get_foundation_db_path
    except Exception:  # pragma: no cover - foundation may not be importable in tests
        return None

    db_path = get_foundation_db_path()
    if not db_path.exists():
        return None

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        user = conn.execute(
            """
            SELECT u.* FROM fnd_users u
            JOIN fnd_tenants t ON t.id = u.tenant_id
            WHERE LOWER(u.email) = LOWER(?) AND u.status = 'active' AND t.status = 'active'
            ORDER BY t.created_at ASC LIMIT 1
            """,
            (email,),
        ).fetchone()
        if user is None:
            return None

        role_rows = conn.execute(
            """
            SELECT r.name FROM fnd_user_roles ur
            JOIN fnd_roles r ON r.id = ur.role_id
            WHERE ur.user_id = ? AND ur.tenant_id = ?
            ORDER BY r.created_at ASC
            """,
            (user["id"], user["tenant_id"]),
        ).fetchall()
        role_names = [row["name"] for row in role_rows]
        primary_role = role_names[0] if role_names else "viewer"

        return {
            "user_id": user["id"],
            "tenant_id": user["tenant_id"],
            "role": primary_role,
            "roles": role_names,
        }
    finally:
        conn.close()


def get_current_user(request: Request) -> dict[str, Any]:
    """FastAPI dependency that validates the access token (cookie or header)."""

    if os.getenv("FABERLOOM_AUTH_DISABLED"):
        return _local_user()

    users = _users()
    if not users:
        return _local_user()

    token: str | None = None
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
    if token is None:
        token = request.cookies.get("faberloom_at")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, _secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    email = (payload.get("sub") or "").strip().lower()
    if email and email != "local" and "@" in email:
        foundation_user = _resolve_user_from_foundation(email)
        if foundation_user:
            payload["tenant_id"] = foundation_user["tenant_id"]
            payload["user_id"] = foundation_user["user_id"]
            payload["role"] = foundation_user["role"]
            payload["roles"] = foundation_user["roles"]
            payload["foundation_resolved"] = True
        else:
            payload["foundation_resolved"] = False

    if not payload.get("tenant_id"):
        payload["tenant_id"] = DEFAULT_TENANT_ID
    if not payload.get("user_id"):
        payload["user_id"] = payload.get("sub") or "local"
    request.state.user = payload
    return request.state.user


@auth_router.post("/auth/login", response_model=TokenResponse)
def api_login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    conn: sqlite3.Connection = Depends(get_db),
) -> TokenResponse:
    users = _users()
    expected = users.get(payload.email)
    if expected is None or expected != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    foundation_user = _resolve_user_from_foundation(payload.email)
    access_token = create_access_token(
        payload.email,
        tenant_id=foundation_user["tenant_id"] if foundation_user else None,
        user_id=foundation_user["user_id"] if foundation_user else None,
        role=foundation_user["role"] if foundation_user else None,
    )
    refresh_token, _expires = _create_refresh_token(conn, payload.email)

    cookie_opts = _cookie_settings(request)
    response.set_cookie(key="faberloom_at", value=access_token, **cookie_opts)
    response.set_cookie(key="faberloom_rt", value=refresh_token, **cookie_opts)

    return TokenResponse(email=payload.email)


@auth_router.post("/auth/refresh")
def api_refresh(
    request: Request,
    response: Response,
    conn: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    cookie_token = request.cookies.get("faberloom_rt")
    if not cookie_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token required")

    row = _refresh_token_for_cookie(conn, cookie_token)
    if row is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")

    _revoke_refresh_token(conn, row["token_hash"])

    email = row["user_id"]
    foundation_user = _resolve_user_from_foundation(email)
    access_token = create_access_token(
        email,
        tenant_id=foundation_user["tenant_id"] if foundation_user else None,
        user_id=foundation_user["user_id"] if foundation_user else None,
        role=foundation_user["role"] if foundation_user else None,
    )
    refresh_token, _expires = _create_refresh_token(conn, email)

    cookie_opts = _cookie_settings(request)
    response.set_cookie(key="faberloom_at", value=access_token, **cookie_opts)
    response.set_cookie(key="faberloom_rt", value=refresh_token, **cookie_opts)

    return {"email": email}


@auth_router.post("/auth/logout")
def api_logout(
    request: Request,
    response: Response,
    conn: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    cookie_token = request.cookies.get("faberloom_rt")
    if cookie_token:
        row = _refresh_token_for_cookie(conn, cookie_token)
        if row is not None:
            _revoke_refresh_token(conn, row["token_hash"])

    cookie_opts = _cookie_settings(request)
    response.delete_cookie(key="faberloom_at", **cookie_opts)
    response.delete_cookie(key="faberloom_rt", **cookie_opts)
    return {"detail": "Sesión cerrada"}


# ---------------------------------------------------------------------------
# E3-2 public signup with email verification
# ---------------------------------------------------------------------------


class PublicSignupRequest(BaseModel):
    company_name: str
    slug: str
    owner_email: str
    owner_password: str = Field(min_length=8)
    plan: str = "starter"


class PublicSignupResponse(BaseModel):
    tenant_id: str
    status: str
    message: str


class ResendVerificationRequest(BaseModel):
    email: str


_VERIFICATION_TOKEN_TTL_HOURS = 24
_SIGNUP_RATE_LIMIT_MAX = int(os.getenv("FABERLOOM_SIGNUP_RATE_LIMIT_MAX", "5"))
_SIGNUP_RATE_LIMIT_WINDOW = int(os.getenv("FABERLOOM_SIGNUP_RATE_LIMIT_WINDOW", "900"))
_RESEND_RATE_LIMIT_MAX = int(os.getenv("FABERLOOM_RESEND_RATE_LIMIT_MAX", "3"))
_RESEND_RATE_LIMIT_WINDOW = int(os.getenv("FABERLOOM_RESEND_RATE_LIMIT_WINDOW", "3600"))


def _generate_verification_token() -> str:
    return secrets.token_urlsafe(32)


def _hash_verification_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _public_host() -> str:
    return os.getenv("FABERLOOM_PUBLIC_HOST", "app.faberloom.ai")


def _verification_link(token: str) -> str:
    return f"https://{_public_host()}/api/public/signup/verify?token={token}"


def _store_verification_token(
    conn: sqlite3.Connection,
    tenant_id: str,
    user_id: str,
    token: str,
    purpose: str = "signup",
) -> str:
    from .foundation.core import new_id, utcnow

    token_hash = _hash_verification_token(token)
    expires_at = (
        datetime.now(timezone.utc) + timedelta(hours=_VERIFICATION_TOKEN_TTL_HOURS)
    ).isoformat()
    verification_id = new_id("evf")
    conn.execute(
        """
        INSERT INTO fnd_email_verifications
        (id, tenant_id, user_id, purpose, token_hash, expires_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (verification_id, tenant_id, user_id, purpose, token_hash, expires_at, utcnow()),
    )
    return verification_id


def _send_verification_email(
    conn: sqlite3.Connection,
    email: str,
    token: str,
    company_name: str,
) -> dict[str, Any]:
    """Send the verification email if platform SMTP is configured.

    Returns the SMTP result dict or a dry-run dict when no SMTP is configured.
    Never raises; failures are logged and returned as dry-run so signup always
    succeeds from the caller's perspective.
    """

    from .foundation.core import get_platform_smtp_config, utcnow

    config_data = get_platform_smtp_config(conn)
    if config_data is None:
        return {"sent": False, "dry_run": True, "reason": "no_smtp_config"}

    try:
        config = SMTPConfig(
            server=config_data["host"],
            port=int(config_data["port"]),
            username=config_data["username"],
            password=config_data["password"],
            use_ssl=bool(config_data.get("use_ssl", 1)),
            from_email=config_data.get("from_email") or config_data["username"],
        )
        link = _verification_link(token)
        subject = f"Verify your FaberLoom account — {company_name}"
        body = (
            f"Welcome to FaberLoom.\n\n"
            f"Please verify your email by opening the link below. "
            f"It expires in {_VERIFICATION_TOKEN_TTL_HOURS} hours.\n\n"
            f"{link}\n\n"
            f"If you did not request this account, you can safely ignore this message."
        )
        # The SMTP connector requires a confirmation_token to actually send.
        # For automated lifecycle emails we compute the deterministic token
        # internally and pass it directly; no UI preview step is involved.
        expected_token = smtp_send_email(
            config, email, subject, body, dry_run=True
        )["confirmation_token"]
        return smtp_send_email(
            config, email, subject, body, confirmation_token_value=expected_token
        )
    except SMTPError as exc:
        return {"sent": False, "dry_run": True, "reason": "smtp_error", "error": str(exc)}
    except Exception as exc:  # pragma: no cover - defensive
        return {"sent": False, "dry_run": True, "reason": "unexpected", "error": str(exc)}


@auth_router.post("/public/signup", response_model=PublicSignupResponse)
def public_signup(
    body: PublicSignupRequest,
    request: Request,
) -> PublicSignupResponse:
    """Create a new tenant pending platform_admin approval.

    The owner user is created in ``pending_verification`` status. A verification
    email is sent when platform SMTP is configured; otherwise the flow runs in
    dry-run mode. Per-IP rate limiting is enforced before any processing.
    """

    rate_limit_dependency(request, action="signup", max_attempts=_SIGNUP_RATE_LIMIT_MAX, window_seconds=_SIGNUP_RATE_LIMIT_WINDOW)

    import re

    from .foundation.core import (
        audit_log,
        get_foundation_db_path,
        hash_password,
        new_id,
        seed_system_roles,
        utcnow,
    )

    _SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$")

    email = body.owner_email.strip().lower()
    if "@" not in email:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid owner email")

    password = body.owner_password
    if len(password) < 8:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Password too short")

    slug = body.slug.strip().lower()
    if not _SLUG_RE.match(slug):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Slug must be 3-40 lowercase chars, digits or hyphens",
        )

    company = body.company_name.strip()
    if not company or len(company) > 120:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid company name")

    plan = body.plan.strip().lower()
    if plan not in {"starter", "growth", "enterprise"}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid plan")

    db_path = get_foundation_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        # Slug uniqueness across tenants.
        existing = conn.execute(
            "SELECT id FROM fnd_tenants WHERE slug = ?", (slug,)
        ).fetchone()
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Slug already taken")

        tenant_id = new_id("tnt")
        user_id = new_id("usr")
        now = utcnow()

        conn.execute(
            """INSERT INTO fnd_tenants (id, name, slug, status, plan, created_at)
               VALUES (?, ?, ?, 'pending_approval', ?, ?)""",
            (tenant_id, company, slug, plan, now),
        )
        seed_system_roles(conn, tenant_id)

        conn.execute(
            """INSERT INTO fnd_users
               (id, tenant_id, email, display_name, password_hash, status, created_at)
               VALUES (?, ?, ?, ?, ?, 'pending_verification', ?)""",
            (
                user_id,
                tenant_id,
                email,
                email.split("@")[0],
                hash_password(password),
                now,
            ),
        )

        owner_role = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = 'owner'",
            (tenant_id,),
        ).fetchone()
        if owner_role is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Owner role missing")

        conn.execute(
            """INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
               VALUES (?, ?, ?, ?, ?)""",
            (tenant_id, user_id, owner_role["id"], user_id, now),
        )

        token = _generate_verification_token()
        _store_verification_token(conn, tenant_id, user_id, token)
        smtp_result = _send_verification_email(conn, email, token, company)

        audit_log(
            conn,
            tenant_id,
            "tenant.signup",
            actor_id=user_id,
            actor_email=email,
            resource_type="tenant",
            resource_id=tenant_id,
            payload={"plan": plan, "slug": slug, "email_sent": smtp_result.get("sent"), "dry_run": smtp_result.get("dry_run")},
        )
        conn.commit()
    finally:
        conn.close()

    return PublicSignupResponse(
        tenant_id=tenant_id,
        status="pending_verification",
        message="Thanks for signing up. Please check your email to verify your account.",
    )


@auth_router.get("/public/signup/verify")
def verify_signup_token(
    token: str,
) -> dict[str, Any]:
    """Verify an owner email and activate the user if the tenant is approved."""

    import re

    from .foundation.core import audit_log, get_foundation_db_path, utcnow

    if not token or len(token) < 16:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid verification token")

    token_hash = _hash_verification_token(token)
    db_path = get_foundation_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        verification = conn.execute(
            """
            SELECT ev.*, u.tenant_id AS user_tenant_id, u.status AS user_status, t.status AS tenant_status
            FROM fnd_email_verifications ev
            JOIN fnd_users u ON u.id = ev.user_id
            JOIN fnd_tenants t ON t.id = ev.tenant_id
            WHERE ev.token_hash = ? AND ev.purpose = 'signup' AND ev.used_at IS NULL
            ORDER BY ev.created_at DESC LIMIT 1
            """,
            (token_hash,),
        ).fetchone()

        if verification is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired verification token")

        if verification["expires_at"] < utcnow():
            raise HTTPException(status.HTTP_410_GONE, "Verification token has expired")

        user_id = verification["user_id"]
        tenant_id = verification["tenant_id"]
        tenant_status = verification["tenant_status"]

        new_user_status = "active" if tenant_status == "active" else "pending_approval"
        now = utcnow()
        conn.execute(
            """
            UPDATE fnd_users
            SET email_verified = 1, email_verified_at = ?, status = ?
            WHERE id = ?
            """,
            (now, new_user_status, user_id),
        )
        conn.execute(
            "UPDATE fnd_email_verifications SET used_at = ? WHERE id = ?",
            (now, verification["id"]),
        )

        audit_log(
            conn,
            tenant_id,
            "user.email_verified",
            actor_id=user_id,
            actor_email="",
            resource_type="user",
            resource_id=user_id,
            payload={"new_status": new_user_status, "tenant_status": tenant_status},
        )
        conn.commit()

        return {
            "verified": True,
            "user_status": new_user_status,
            "tenant_status": tenant_status,
            "message": "Email verified. Your account is now active."
                if new_user_status == "active"
                else "Email verified. Your account will be activated once the tenant is approved.",
        }
    finally:
        conn.close()


@auth_router.post("/public/signup/resend-verification")
def resend_verification(
    body: ResendVerificationRequest,
    request: Request,
) -> dict[str, Any]:
    """Resend the verification email for a pending owner user.

    Always returns a generic success message to avoid email enumeration.
    """

    rate_limit_dependency(request, action="resend_verification", max_attempts=_RESEND_RATE_LIMIT_MAX, window_seconds=_RESEND_RATE_LIMIT_WINDOW)

    from .foundation.core import get_foundation_db_path, utcnow

    email = body.email.strip().lower()
    if "@" not in email:
        # Generic response even for malformed input to avoid enumeration.
        return {"message": "If an account exists, a verification email has been sent."}

    db_path = get_foundation_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        user = conn.execute(
            """
            SELECT u.*, t.name AS tenant_name FROM fnd_users u
            JOIN fnd_tenants t ON t.id = u.tenant_id
            WHERE LOWER(u.email) = ? AND u.status = 'pending_verification'
            ORDER BY u.created_at DESC LIMIT 1
            """,
            (email,),
        ).fetchone()

        if user is None:
            return {"message": "If an account exists, a verification email has been sent."}

        # Invalidate any previous unused tokens for this user.
        conn.execute(
            "UPDATE fnd_email_verifications SET used_at = ? WHERE user_id = ? AND used_at IS NULL",
            (utcnow(), user["id"]),
        )

        token = _generate_verification_token()
        _store_verification_token(conn, user["tenant_id"], user["id"], token)
        _send_verification_email(conn, email, token, user["tenant_name"])
        conn.commit()

        return {"message": "If an account exists, a verification email has been sent."}
    finally:
        conn.close()
