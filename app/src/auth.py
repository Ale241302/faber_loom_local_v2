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
# E3-2 public signup
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


@auth_router.post("/public/signup", response_model=PublicSignupResponse)
def public_signup(body: PublicSignupRequest) -> PublicSignupResponse:
    """Create a new tenant pending platform_admin approval.

    This endpoint is intentionally public and unauthenticated, but rate-limiting
    should be added at the reverse-proxy / WAF layer before production use.
    """

    import re

    import sqlite3

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
               VALUES (?, ?, ?, ?, ?, 'active', ?)""",
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

        audit_log(
            conn,
            tenant_id,
            "tenant.signup",
            actor_id=user_id,
            actor_email=email,
            resource_type="tenant",
            resource_id=tenant_id,
            payload={"plan": plan, "slug": slug},
        )
        conn.commit()
    finally:
        conn.close()

    return PublicSignupResponse(
        tenant_id=tenant_id,
        status="pending_approval",
        message="Tenant registered and pending platform_admin approval.",
    )
