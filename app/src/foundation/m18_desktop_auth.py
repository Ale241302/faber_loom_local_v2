"""M18 Desktop Auth — registro de dispositivo + persistencia segura de sesión.

Port de ``foundation_beta/desktop/src/main/session.js`` (Electron) al runtime
pywebview + FastAPI:

- keytar / keychain del SO → almacén local cifrado: los ``device_secret`` se
  guardan en ``fnd_device_secrets`` cifrados con Fernet, cuya clave se deriva
  (PBKDF2) de un secreto local en archivo junto a la BD foundation (0600,
  se genera si no existe).
- La cookie httpOnly por partición → sesiones foundation (``fnd_sessions``)
  ligadas al device vía la columna ``device_id``.
- El "remember me" desktop del plan M18 es ``POST /device/login``: con
  ``device_id`` + ``device_secret`` se crea una sesión full sin password.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field

from .core import (
    SESSION_TTL_SECONDS,
    SessionContext,
    audit_log,
    get_conn,
    get_foundation_db_path,
    new_id,
    register_schema,
    require_session,
    rows_to_dicts,
    to_dict,
    utcnow,
)

router = APIRouter(prefix="/desktop/auth", tags=["foundation-m18"])

SCHEMA = """
CREATE TABLE IF NOT EXISTS fnd_devices (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT '',
    fingerprint TEXT NOT NULL,
    created_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    revoked_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_fnd_devices_tenant ON fnd_devices(tenant_id, user_id);

CREATE TABLE IF NOT EXISTS fnd_device_secrets (
    device_id TEXT PRIMARY KEY REFERENCES fnd_devices(id),
    secret_encrypted TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""
register_schema(SCHEMA)

_KEY_FILE_NAME = "foundation_device.key"
_KDF_SALT = b"faberloom-fnd-device-secrets"
_KDF_ITERATIONS = 100_000


# ---------------------------------------------------------------------------
# Almacén local de credenciales (equivalente a keytar en Electron)
# ---------------------------------------------------------------------------


def _local_secret_path() -> Path:
    return get_foundation_db_path().parent / _KEY_FILE_NAME


def _get_fernet() -> Fernet:
    """Fernet con clave derivada de un secreto local en disco (0600)."""
    path = _local_secret_path()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = secrets.token_bytes(32)
        path.write_bytes(base64.b64encode(raw))
        try:
            os.chmod(path, 0o600)
        except OSError:  # pragma: no cover - p.ej. FS sin permisos POSIX
            pass
    raw = base64.b64decode(path.read_bytes())
    derived = hashlib.pbkdf2_hmac("sha256", raw, _KDF_SALT, _KDF_ITERATIONS)
    return Fernet(base64.urlsafe_b64encode(derived))


def _encrypt_secret(secret: str) -> str:
    return _get_fernet().encrypt(secret.encode()).decode()


def _decrypt_secret(token: str) -> str | None:
    try:
        return _get_fernet().decrypt(token.encode()).decode()
    except (InvalidToken, Exception):
        return None


def _fingerprint(secret: str) -> str:
    return hashlib.sha256(secret.encode()).hexdigest()


def _device_public(row) -> dict[str, Any]:
    out = to_dict(row) or {}
    out.pop("fingerprint", None)
    return out


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------


class DeviceRegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    platform: str = Field(default="", max_length=80)


class DeviceLoginIn(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    device_secret: str | None = Field(default=None, max_length=256)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/device/register")
def register_device(
    body: DeviceRegisterIn,
    request: Request,
    response: Response,
    ctx: SessionContext = Depends(require_session),
) -> dict[str, Any]:
    """Registra este dispositivo y liga la sesión actual a él.

    Devuelve el ``device_secret`` UNA sola vez; el servidor lo guarda cifrado
    (almacén tipo keytar) y solo lo re-verifica, nunca lo re-expone.
    """
    conn = ctx.conn
    device_id = new_id("dev")
    device_secret = "devs_" + secrets.token_urlsafe(32)
    now = utcnow()
    conn.execute(
        """INSERT INTO fnd_devices
           (id, tenant_id, user_id, name, platform, fingerprint, created_at, last_seen_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (device_id, ctx.tenant_id, ctx.user_id, body.name.strip(), body.platform.strip(),
         _fingerprint(device_secret), now, now),
    )
    conn.execute(
        "INSERT INTO fnd_device_secrets (device_id, secret_encrypted, created_at) VALUES (?, ?, ?)",
        (device_id, _encrypt_secret(device_secret), now),
    )
    conn.execute(
        "UPDATE fnd_sessions SET device_id = ? WHERE id = ?", (device_id, ctx.session_id)
    )
    ctx.audit(
        "device.registered",
        resource_type="device",
        resource_id=device_id,
        payload={"name": body.name.strip(), "platform": body.platform.strip()},
    )
    ctx.emit("desktop", "device.registered", {"device_id": device_id, "user_id": ctx.user_id})
    response.set_cookie(
        key="faberloom_fnd_device",
        value=device_secret,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        path="/api/foundation/desktop/auth",
    )
    return {
        "device_id": device_id,
        "device_secret": device_secret,
        "note": "Guarda el device_secret ahora; no se volverá a mostrar. También quedó en una cookie segura del navegador.",
    }


@router.post("/device/login")
def device_login(
    body: DeviceLoginIn,
    request: Request,
    response: Response,
    conn=Depends(get_conn),
) -> dict[str, Any]:
    """PRE-AUTH: crea una sesión full a partir de device_id + device_secret.

    Es el "remember me" desktop del plan M18: el cliente guarda el secret en
    su almacén local y re-abre sesión sin password mientras el device no esté
    revocado y el usuario siga activo.
    """
    invalid = HTTPException(status.HTTP_401_UNAUTHORIZED, "Credenciales de dispositivo inválidas")
    device_secret = body.device_secret or request.cookies.get("faberloom_fnd_device")
    if not device_secret:
        raise invalid

    device = conn.execute("SELECT * FROM fnd_devices WHERE id = ?", (body.device_id,)).fetchone()
    if device is None or device["revoked_at"] is not None:
        raise invalid

    # Verificación doble: fingerprint (hash) + secreto cifrado en el almacén local.
    if not hmac.compare_digest(_fingerprint(device_secret), device["fingerprint"]):
        raise invalid
    stored = conn.execute(
        "SELECT secret_encrypted FROM fnd_device_secrets WHERE device_id = ?", (body.device_id,)
    ).fetchone()
    plain = _decrypt_secret(stored["secret_encrypted"]) if stored else None
    if plain is None or not hmac.compare_digest(plain, device_secret):
        raise invalid

    user = conn.execute("SELECT * FROM fnd_users WHERE id = ?", (device["user_id"],)).fetchone()
    if user is None or user["status"] != "active":
        raise invalid

    now = datetime.now(timezone.utc)
    session_id = new_id("fnds")
    conn.execute(
        """INSERT INTO fnd_sessions
           (id, tenant_id, user_id, stage, created_at, expires_at, last_seen_at, ip, user_agent, device_id)
           VALUES (?, ?, ?, 'full', ?, ?, ?, '', 'desktop-device-login', ?)""",
        (session_id, device["tenant_id"], user["id"], now.isoformat(),
         (now + timedelta(seconds=SESSION_TTL_SECONDS)).isoformat(), now.isoformat(),
         device["id"]),
    )
    conn.execute("UPDATE fnd_devices SET last_seen_at = ? WHERE id = ?", (utcnow(), device["id"]))
    audit_log(
        conn, device["tenant_id"], "device.login",
        actor_id=user["id"], actor_email=user["email"],
        resource_type="device", resource_id=device["id"],
        payload={"session_id": session_id},
    )
    response.set_cookie(
        key="fnd_session",
        value=session_id,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="strict",
        path="/api/foundation",
    )
    return {
        "session": session_id,
        "expires_at": (now + timedelta(seconds=SESSION_TTL_SECONDS)).isoformat(),
        "device_id": device["id"],
        "user": {"id": user["id"], "email": user["email"], "display_name": user["display_name"]},
    }


@router.get("/devices")
def list_devices(ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Dispositivos propios; con ``users.manage`` se ven todos los del tenant."""
    if ctx.has("users.manage"):
        rows = ctx.conn.execute(
            "SELECT * FROM fnd_devices WHERE tenant_id = ? ORDER BY created_at DESC",
            (ctx.tenant_id,),
        ).fetchall()
    else:
        rows = ctx.conn.execute(
            "SELECT * FROM fnd_devices WHERE tenant_id = ? AND user_id = ? ORDER BY created_at DESC",
            (ctx.tenant_id, ctx.user_id),
        ).fetchall()
    return {"devices": [_device_public(r) for r in rows]}


@router.post("/devices/{device_id}/revoke")
def revoke_device(device_id: str, ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    device = ctx.conn.execute(
        "SELECT * FROM fnd_devices WHERE id = ? AND tenant_id = ?", (device_id, ctx.tenant_id)
    ).fetchone()
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dispositivo no encontrado")
    if device["user_id"] != ctx.user_id and not ctx.has("users.manage"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo el dueño o users.manage puede revocar")
    if device["revoked_at"] is not None:
        return {"device_id": device_id, "revoked_at": device["revoked_at"], "already_revoked": True}

    now = utcnow()
    ctx.conn.execute("UPDATE fnd_devices SET revoked_at = ? WHERE id = ?", (now, device_id))
    sessions = ctx.conn.execute(
        "UPDATE fnd_sessions SET revoked_at = ? WHERE device_id = ? AND revoked_at IS NULL",
        (now, device_id),
    ).rowcount
    ctx.audit(
        "device.revoked",
        resource_type="device",
        resource_id=device_id,
        payload={"sessions_revoked": sessions},
    )
    ctx.emit("desktop", "device.revoked", {"device_id": device_id})
    return {"device_id": device_id, "revoked_at": now, "sessions_revoked": sessions}


# ---------------------------------------------------------------------------
# Helper compartido (M19/M20): device del tenant, verificado y activo
# ---------------------------------------------------------------------------


def get_tenant_device(conn, tenant_id: str, device_id: str):
    """Device perteneciente al tenant, no revocado. 404/409 si no aplica."""
    device = conn.execute(
        "SELECT * FROM fnd_devices WHERE id = ? AND tenant_id = ?", (device_id, tenant_id)
    ).fetchone()
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dispositivo no encontrado")
    if device["revoked_at"] is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Dispositivo revocado")
    return device
