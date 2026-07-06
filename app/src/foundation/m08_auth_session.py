"""M08 Auth Session — login con password + TOTP opcional, sesiones en SQLite.

Port de ``foundation_beta/backend/apps/auth_session``:

- Sesiones Redis → tabla ``fnd_sessions`` (token opaco ``fnds_...``).
- Login en dos pasos: si el usuario tiene 2FA activo, ``/login`` crea una
  sesión ``stage="totp"`` (no autenticada) y ``/2fa/verify`` la promueve a
  ``stage="full"``.
- Lockout Redis → campos ``failed_attempts`` / ``locked_until`` en
  ``fnd_users``: 5 intentos fallidos → bloqueo 15 minutos.
- Audit + eventos en login ok/fail/lockout/logout/2fa (M12/M15).
"""

from __future__ import annotations

import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from .core import (
    SESSION_TTL_SECONDS,
    SessionContext,
    audit_log,
    emit_event,
    generate_totp_secret,
    get_active_tenant,
    get_conn,
    get_user_permissions,
    load_session,
    require_session,
    totp_provisioning_uri,
    user_role_names,
    utcnow,
    verify_password,
    verify_totp,
)

router = APIRouter(prefix="/auth", tags=["m08-auth-session"])

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


# ---------------------------------------------------------------------------
# Bodies
# ---------------------------------------------------------------------------


class LoginBody(BaseModel):
    email: str
    password: str


class TotpVerifyBody(BaseModel):
    session: str
    code: str


class CodeBody(BaseModel):
    code: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_dt() -> datetime:
    return datetime.now(timezone.utc)


def _fnd_cookie_settings(request: Request) -> dict[str, Any]:
    return {
        "httponly": True,
        "secure": request.url.scheme == "https",
        "samesite": "strict",
        "path": "/api/foundation",
    }


def create_session(
    conn: sqlite3.Connection,
    tenant_id: str,
    user_id: str,
    *,
    stage: str = "full",
    request: Request | None = None,
) -> str:
    token = "fnds_" + secrets.token_urlsafe(32)
    now = _now_dt()
    ip = ""
    user_agent = ""
    if request is not None:
        ip = request.client.host if request.client else ""
        user_agent = request.headers.get("user-agent", "")[:300]
    conn.execute(
        """INSERT INTO fnd_sessions
           (id, tenant_id, user_id, stage, created_at, expires_at, last_seen_at, ip, user_agent)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            token,
            tenant_id,
            user_id,
            stage,
            now.isoformat(),
            (now + timedelta(seconds=SESSION_TTL_SECONDS)).isoformat(),
            now.isoformat(),
            ip,
            user_agent,
        ),
    )
    return token


def _user_payload(conn: sqlite3.Connection, tenant_id: str, user: sqlite3.Row) -> dict[str, Any]:
    perms = get_user_permissions(conn, tenant_id, user["id"])
    return {
        "id": user["id"],
        "email": user["email"],
        "display_name": user["display_name"],
        "roles": user_role_names(conn, tenant_id, user["id"]),
        "permissions": sorted(perms),
        "tenant_id": tenant_id,
        "totp_enabled": bool(user["totp_enabled"]),
    }


def _is_locked(user: sqlite3.Row) -> bool:
    return bool(user["locked_until"] and user["locked_until"] > utcnow())


def _register_failure(
    conn: sqlite3.Connection, tenant_id: str, user: sqlite3.Row, *, kind: str
) -> None:
    """Incrementa el contador de fallos y bloquea al llegar al límite."""
    attempts = int(user["failed_attempts"] or 0) + 1
    locked_until: str | None = None
    if attempts >= MAX_FAILED_ATTEMPTS:
        locked_until = (_now_dt() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
    conn.execute(
        "UPDATE fnd_users SET failed_attempts = ?, locked_until = ? WHERE id = ?",
        (attempts, locked_until, user["id"]),
    )
    audit_log(
        conn, tenant_id, f"auth.{kind}.failed",
        actor_email=user["email"], resource_type="user", resource_id=user["id"],
        payload={"attempt": attempts},
    )
    if locked_until:
        audit_log(
            conn, tenant_id, "auth.login.lockout",
            actor_email=user["email"], resource_type="user", resource_id=user["id"],
            payload={"locked_until": locked_until, "attempts": attempts},
        )
        emit_event(conn, tenant_id, "auth", "login.lockout",
                   {"user_id": user["id"], "locked_until": locked_until})


def _clear_failures(conn: sqlite3.Connection, user_id: str) -> None:
    conn.execute(
        "UPDATE fnd_users SET failed_attempts = 0, locked_until = NULL WHERE id = ?",
        (user_id,),
    )


def _locked_response(user: sqlite3.Row) -> HTTPException:
    return HTTPException(
        status.HTTP_423_LOCKED,
        f"Cuenta bloqueada por intentos fallidos hasta {user['locked_until']}",
    )


def _raise_committed(conn: sqlite3.Connection, exc: HTTPException) -> None:
    """Commit + raise: los fallos de login escriben audit/lockout y deben
    persistir aunque el request termine en error (get_conn hace rollback
    cuando el endpoint lanza una excepción)."""
    conn.commit()
    raise exc


# ---------------------------------------------------------------------------
# PRE-AUTH: login y verificación 2FA
# ---------------------------------------------------------------------------


@router.post("/login")
def login(
    body: LoginBody,
    request: Request,
    response: Response,
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    tenant = get_active_tenant(conn)
    if tenant is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Tenant no inicializado (bootstrap pendiente)")
    tenant_id = tenant["id"]
    email = body.email.strip().lower()

    user = conn.execute(
        "SELECT * FROM fnd_users WHERE tenant_id = ? AND email = ?", (tenant_id, email)
    ).fetchone()
    if user is None:
        audit_log(conn, tenant_id, "auth.login.failed", actor_email=email,
                  payload={"reason": "unknown_user"})
        _raise_committed(conn, HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas"))

    if user["status"] != "active":
        audit_log(conn, tenant_id, "auth.login.failed", actor_email=email,
                  resource_type="user", resource_id=user["id"],
                  payload={"reason": "user_inactive"})
        _raise_committed(conn, HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas"))

    if _is_locked(user):
        audit_log(conn, tenant_id, "auth.login.failed", actor_email=email,
                  resource_type="user", resource_id=user["id"],
                  payload={"reason": "locked"})
        _raise_committed(conn, _locked_response(user))

    if not verify_password(body.password, user["password_hash"]):
        _register_failure(conn, tenant_id, user, kind="login")
        _raise_committed(conn, HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales inválidas"))

    _clear_failures(conn, user["id"])

    if user["totp_enabled"]:
        token = create_session(conn, tenant_id, user["id"], stage="totp", request=request)
        response.set_cookie(key="fnd_session", value=token, **_fnd_cookie_settings(request))
        audit_log(conn, tenant_id, "auth.login.2fa_pending", actor_id=user["id"],
                  actor_email=email, resource_type="session", resource_id=token[:16],
                  payload={"method": "password"})
        return {"requires_2fa": True, "session": token}

    token = create_session(conn, tenant_id, user["id"], stage="full", request=request)
    response.set_cookie(key="fnd_session", value=token, **_fnd_cookie_settings(request))
    audit_log(conn, tenant_id, "auth.login.success", actor_id=user["id"],
              actor_email=email, resource_type="session", resource_id=token[:16],
              payload={"method": "password"})
    emit_event(conn, tenant_id, "auth", "login.success",
               {"user_id": user["id"], "method": "password"})
    return {"requires_2fa": False, "session": token,
            "user": _user_payload(conn, tenant_id, user)}


@router.post("/2fa/verify")
def totp_verify(
    body: TotpVerifyBody,
    request: Request,
    response: Response,
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    session = load_session(conn, body.session)
    if session is None or session["stage"] != "totp":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión 2FA inválida o expirada")
    tenant_id = session["tenant_id"]
    user = conn.execute(
        "SELECT * FROM fnd_users WHERE id = ? AND tenant_id = ?",
        (session["user_id"], tenant_id),
    ).fetchone()
    if user is None or user["status"] != "active" or not user["totp_secret"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión 2FA inválida")

    if _is_locked(user):
        raise _locked_response(user)

    if not verify_totp(user["totp_secret"], body.code):
        _register_failure(conn, tenant_id, user, kind="2fa")
        _raise_committed(conn, HTTPException(status.HTTP_401_UNAUTHORIZED, "Código 2FA inválido"))

    _clear_failures(conn, user["id"])
    conn.execute("UPDATE fnd_sessions SET stage = 'full' WHERE id = ?", (session["id"],))
    response.set_cookie(key="fnd_session", value=session["id"], **_fnd_cookie_settings(request))
    audit_log(conn, tenant_id, "auth.login.success", actor_id=user["id"],
              actor_email=user["email"], resource_type="session",
              resource_id=session["id"][:16], payload={"method": "totp"})
    emit_event(conn, tenant_id, "auth", "login.success",
               {"user_id": user["id"], "method": "totp"})
    return {"session": session["id"], "user": _user_payload(conn, tenant_id, user)}


# ---------------------------------------------------------------------------
# AUTENTICADOS
# ---------------------------------------------------------------------------


@router.get("/me")
def me(
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    user = conn.execute(
        "SELECT * FROM fnd_users WHERE id = ? AND tenant_id = ?",
        (ctx.user_id, ctx.tenant_id),
    ).fetchone()
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no encontrado")
    return _user_payload(conn, ctx.tenant_id, user)


@router.post("/logout")
def logout(
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    conn.execute(
        "UPDATE fnd_sessions SET revoked_at = ? WHERE id = ? AND tenant_id = ?",
        (utcnow(), ctx.session_id, ctx.tenant_id),
    )
    ctx.audit("auth.logout", resource_type="session", resource_id=ctx.session_id[:16])
    ctx.emit("auth", "session.revoked", {"user_id": ctx.user_id, "scope": "self"})
    return {"detail": "Sesión cerrada"}


@router.get("/sessions")
def list_sessions(
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    rows = conn.execute(
        """SELECT * FROM fnd_sessions
           WHERE tenant_id = ? AND user_id = ? AND revoked_at IS NULL AND expires_at > ?
           ORDER BY created_at DESC""",
        (ctx.tenant_id, ctx.user_id, utcnow()),
    ).fetchall()
    return {
        "sessions": [
            {
                "id": r["id"],
                "stage": r["stage"],
                "created_at": r["created_at"],
                "last_seen_at": r["last_seen_at"],
                "expires_at": r["expires_at"],
                "ip": r["ip"],
                "user_agent": r["user_agent"],
                "current": r["id"] == ctx.session_id,
            }
            for r in rows
        ]
    }


@router.post("/sessions/{session_id}/revoke")
def revoke_session(
    session_id: str,
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    row = conn.execute(
        """SELECT * FROM fnd_sessions
           WHERE id = ? AND tenant_id = ? AND user_id = ? AND revoked_at IS NULL""",
        (session_id, ctx.tenant_id, ctx.user_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sesión no encontrada")
    conn.execute(
        "UPDATE fnd_sessions SET revoked_at = ? WHERE id = ?", (utcnow(), session_id)
    )
    ctx.audit("auth.session.revoked", resource_type="session",
              resource_id=session_id[:16])
    ctx.emit("auth", "session.revoked",
             {"user_id": ctx.user_id, "session_id": session_id[:16]})
    return {"detail": "Sesión revocada"}


# ---------------------------------------------------------------------------
# 2FA (TOTP)
# ---------------------------------------------------------------------------


@router.post("/2fa/enroll")
def totp_enroll(
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    user = conn.execute(
        "SELECT * FROM fnd_users WHERE id = ?", (ctx.user_id,)
    ).fetchone()
    if user["totp_enabled"]:
        raise HTTPException(status.HTTP_409_CONFLICT, "2FA ya está activo")
    secret = generate_totp_secret()
    conn.execute(
        "UPDATE fnd_users SET totp_secret = ?, totp_enabled = 0 WHERE id = ?",
        (secret, ctx.user_id),
    )
    ctx.audit("auth.2fa.enroll_started", resource_type="user", resource_id=ctx.user_id)
    return {"secret": secret, "otpauth_uri": totp_provisioning_uri(secret, ctx.email)}


@router.post("/2fa/confirm")
def totp_confirm(
    body: CodeBody,
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    user = conn.execute("SELECT * FROM fnd_users WHERE id = ?", (ctx.user_id,)).fetchone()
    if not user["totp_secret"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No hay enrolamiento 2FA pendiente")
    if not verify_totp(user["totp_secret"], body.code):
        ctx.audit("auth.2fa.confirm_failed", resource_type="user", resource_id=ctx.user_id)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Código 2FA inválido")
    conn.execute("UPDATE fnd_users SET totp_enabled = 1 WHERE id = ?", (ctx.user_id,))
    ctx.audit("auth.2fa.enabled", resource_type="user", resource_id=ctx.user_id)
    ctx.emit("auth", "2fa.enabled", {"user_id": ctx.user_id})
    return {"totp_enabled": True}


@router.post("/2fa/disable")
def totp_disable(
    body: CodeBody,
    ctx: SessionContext = Depends(require_session),
    conn: sqlite3.Connection = Depends(get_conn),
) -> dict[str, Any]:
    user = conn.execute("SELECT * FROM fnd_users WHERE id = ?", (ctx.user_id,)).fetchone()
    if not user["totp_enabled"] or not user["totp_secret"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "2FA no está activo")
    if not verify_totp(user["totp_secret"], body.code):
        ctx.audit("auth.2fa.disable_failed", resource_type="user", resource_id=ctx.user_id)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Código 2FA inválido")
    conn.execute(
        "UPDATE fnd_users SET totp_enabled = 0, totp_secret = NULL WHERE id = ?",
        (ctx.user_id,),
    )
    ctx.audit("auth.2fa.disabled", resource_type="user", resource_id=ctx.user_id)
    ctx.emit("auth", "2fa.disabled", {"user_id": ctx.user_id})
    return {"totp_enabled": False}
