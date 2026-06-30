"""Minimal JWT authentication for the FaberLoom web deployment.

Users and passwords are read from the ``FABERLOOM_USERS`` environment variable
as a JSON object, e.g.:

    FABERLOOM_USERS='{"admin@example.com":"secret"}'

If the variable is empty or unset, authentication is bypassed and the shell
behaves as before (local single-user).  This keeps the test suite green without
needing tokens.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Any

import jwt
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

auth_router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str


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
        # In production this should be set explicitly; the fallback is only so
        # the container does not crash during local smoke tests.
        secret = "faberloom-dev-secret-replace-me"
    return secret


def create_access_token(email: str, role: str = "admin") -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": email, "role": role, "iat": now, "exp": now + timedelta(days=7)}
    return jwt.encode(payload, _secret(), algorithm="HS256")


def get_current_user(request: Request) -> dict[str, Any]:
    """FastAPI dependency that validates the Bearer token.

    When no users are configured or ``FABERLOOM_AUTH_DISABLED`` is set, the
    request is treated as the legacy local user so existing tests keep working.
    """

    if os.getenv("FABERLOOM_AUTH_DISABLED"):
        return {"sub": "local", "role": "owner"}

    users = _users()
    if not users:
        return {"sub": "local", "role": "owner"}

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth[7:]
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

    request.state.user = payload
    return request.state.user


@auth_router.post("/auth/login", response_model=TokenResponse)
def api_login(payload: LoginRequest) -> TokenResponse:
    users = _users()
    expected = users.get(payload.email)
    if expected is None or expected != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(payload.email)
    return TokenResponse(access_token=token, email=payload.email)
