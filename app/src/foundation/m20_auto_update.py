"""M20 Auto Update — canales, min_supported_client_version y gating por sync.

Port de ``foundation_beta/desktop/src/main/updater.js`` (Electron):

- electron-updater + feed → manifiesto por canal (stable|beta) en
  ``fnd_update_channels`` con {version, min_supported_client_version, url,
  sha256, signature?, notes}. La verificación reutiliza los helpers Ed25519 de
  ``app/src/update.py`` cuando el manifiesto trae firma.
- ``semver.lt(current, min_supported)`` → ``force_update`` (pantalla de
  bloqueo del plan M20).
- ``canInstallSafely()`` → gate contra M19: mientras haya mutaciones
  queued|conflict, o el sync esté en modo ``full`` sin reconciliar, el update
  no se instala (fail-closed si M19 no está disponible).
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .core import (
    SessionContext,
    register_schema,
    require_permission,
    require_session,
    to_dict,
    utcnow,
)
from .m18_desktop_auth import get_tenant_device

router = APIRouter(prefix="/updates", tags=["foundation-m20"])

CHANNELS = ("stable", "beta")
MANIFEST_REQUIRED = ("version", "min_supported_client_version", "url", "sha256")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+.].*)?$")

SCHEMA = """
CREATE TABLE IF NOT EXISTS fnd_update_channels (
    channel TEXT PRIMARY KEY CHECK (channel IN ('stable', 'beta')),
    manifest_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fnd_update_state (
    device_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    current_version TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL DEFAULT 'stable',
    available_version TEXT,
    staged_version TEXT,
    status TEXT NOT NULL DEFAULT 'idle',
    blocked_reason TEXT,
    updated_at TEXT NOT NULL
);
"""
register_schema(SCHEMA)


# ---------------------------------------------------------------------------
# Versionado (comparación de tuplas simple, sin dependencia externa)
# ---------------------------------------------------------------------------


def _ver_tuple(version: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", str(version or ""))
    if not parts:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Versión inválida: {version!r}")
    return tuple(int(p) for p in parts[:4])


def _validate_semver(version: str, field: str) -> None:
    if not isinstance(version, str) or not _SEMVER_RE.match(version):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"{field} debe ser semver (X.Y.Z), recibido: {version!r}",
        )


def _app_version() -> str:
    version_file = Path(__file__).resolve().parents[2] / "VERSION"
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except OSError:
        return "0.0.0"


def _get_manifest(conn, channel: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT manifest_json FROM fnd_update_channels WHERE channel = ?", (channel,)
    ).fetchone()
    if row is None:
        return None
    try:
        manifest = json.loads(row["manifest_json"])
    except json.JSONDecodeError:
        return None
    return manifest or None


def _get_state(conn, tenant_id: str, device_id: str):
    return conn.execute(
        "SELECT * FROM fnd_update_state WHERE device_id = ? AND tenant_id = ?",
        (device_id, tenant_id),
    ).fetchone()


def _upsert_state(conn, tenant_id: str, device_id: str, **fields: Any) -> None:
    existing = _get_state(conn, tenant_id, device_id)
    fields["updated_at"] = utcnow()
    if existing is None:
        cols = ["device_id", "tenant_id"] + list(fields.keys())
        conn.execute(
            f"INSERT INTO fnd_update_state ({', '.join(cols)}) "
            f"VALUES ({', '.join('?' for _ in cols)})",
            [device_id, tenant_id] + list(fields.values()),
        )
        return
    sets = ", ".join(f"{k} = ?" for k in fields)
    conn.execute(
        f"UPDATE fnd_update_state SET {sets} WHERE device_id = ? AND tenant_id = ?",
        list(fields.values()) + [device_id, tenant_id],
    )


def _channel_or_400(channel: str) -> str:
    if channel not in CHANNELS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Canal inválido: {channel!r} (stable|beta)")
    return channel


# ---------------------------------------------------------------------------
# Modelos
# ---------------------------------------------------------------------------


class ManifestPutIn(BaseModel):
    channel: str = Field(min_length=1, max_length=16)
    manifest: dict[str, Any]


class CheckIn(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    current_version: str = Field(min_length=1, max_length=40)
    channel: str = Field(default="stable", max_length=16)


class StageIn(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    version: str = Field(min_length=1, max_length=40)
    file_path: str | None = Field(default=None, max_length=1000)


class InstallIn(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/current")
def current_version(ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Versión actual de la app (app/VERSION)."""
    return {"version": _app_version()}


@router.get("/manifest")
def get_manifest(
    channel: str = "stable", ctx: SessionContext = Depends(require_session)
) -> dict[str, Any]:
    _channel_or_400(channel)
    return {"channel": channel, "manifest": _get_manifest(ctx.conn, channel)}


@router.put("/manifest")
def put_manifest(
    body: ManifestPutIn, ctx: SessionContext = Depends(require_permission("updates.manage"))
) -> dict[str, Any]:
    channel = _channel_or_400(body.channel)
    manifest = body.manifest
    missing = [k for k in MANIFEST_REQUIRED if not manifest.get(k)]
    if missing:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, f"Manifiesto incompleto, faltan: {', '.join(missing)}"
        )
    _validate_semver(manifest["version"], "version")
    _validate_semver(manifest["min_supported_client_version"], "min_supported_client_version")
    now = utcnow()
    ctx.conn.execute(
        """INSERT INTO fnd_update_channels (channel, manifest_json, updated_at)
           VALUES (?, ?, ?)
           ON CONFLICT(channel) DO UPDATE SET manifest_json = excluded.manifest_json,
                                              updated_at = excluded.updated_at""",
        (channel, json.dumps(manifest, ensure_ascii=False), now),
    )
    ctx.audit("updates.manifest_updated", resource_type="update_channel", resource_id=channel,
              payload={"version": manifest["version"],
                       "min_supported_client_version": manifest["min_supported_client_version"]})
    ctx.emit("updates", "client.update.published",
             {"channel": channel, "version": manifest["version"]})
    return {"channel": channel, "manifest": manifest, "updated_at": now}


@router.post("/check")
def check_update(body: CheckIn, ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Port de UpdateManager.check(): min_supported → force_update; si no, compara."""
    device = get_tenant_device(ctx.conn, ctx.tenant_id, body.device_id)
    channel = _channel_or_400(body.channel)
    current = _ver_tuple(body.current_version)
    manifest = _get_manifest(ctx.conn, channel)

    if manifest is None:
        _upsert_state(ctx.conn, ctx.tenant_id, device["id"],
                      current_version=body.current_version, channel=channel,
                      available_version=None, status="idle", blocked_reason=None)
        return {"action": "up_to_date", "reason": "sin manifiesto publicado en el canal"}

    min_supported = _ver_tuple(manifest.get("min_supported_client_version", "0.0.0"))
    available = _ver_tuple(manifest.get("version", "0.0.0"))

    if current < min_supported:
        action = "force_update"
        state_status = "available"
    elif available > current:
        action = "update_available"
        state_status = "available"
    else:
        action = "up_to_date"
        state_status = "idle"

    _upsert_state(
        ctx.conn, ctx.tenant_id, device["id"],
        current_version=body.current_version, channel=channel,
        available_version=manifest["version"] if state_status == "available" else None,
        status=state_status, blocked_reason=None,
    )
    ctx.audit("updates.check", resource_type="device", resource_id=device["id"],
              payload={"action": action, "current_version": body.current_version,
                       "channel": channel, "available": manifest.get("version")})
    out: dict[str, Any] = {"action": action}
    if action != "up_to_date":
        out["manifest"] = manifest
        if action == "force_update":
            out["min_supported_client_version"] = manifest["min_supported_client_version"]
            ctx.emit("updates", "client.update.blocked",
                     {"device_id": device["id"], "current_version": body.current_version,
                      "min_supported_client_version": manifest["min_supported_client_version"]})
        else:
            ctx.emit("updates", "client.update.available",
                     {"device_id": device["id"], "version": manifest["version"]})
    return out


@router.post("/stage")
def stage_update(body: StageIn, ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Simula la descarga (autoDownload de electron-updater) y la verifica.

    Si se aporta ``file_path`` local se verifica sha256 contra el manifiesto y,
    si el manifiesto trae firma Ed25519 (signature + public_key), se verifica
    con los helpers de app/src/update.py (fail-closed si no están disponibles).
    """
    device = get_tenant_device(ctx.conn, ctx.tenant_id, body.device_id)
    state = _get_state(ctx.conn, ctx.tenant_id, device["id"])
    channel = state["channel"] if state else "stable"
    manifest = _get_manifest(ctx.conn, channel)
    if manifest is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No hay manifiesto publicado en el canal")
    if body.version != manifest.get("version"):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"La versión {body.version} no coincide con el manifiesto ({manifest.get('version')})",
        )

    if body.file_path:
        payload_path = Path(body.file_path)
        if not payload_path.is_file():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "file_path no existe")
        payload = payload_path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != manifest.get("sha256"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "sha256 del artefacto no coincide con el manifiesto",
            )
        if manifest.get("signature") and manifest.get("public_key"):
            try:
                import base64 as _b64

                from ..update import verify_payload
            except Exception:  # fail-closed: firma presente pero sin verificador
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    "No se pudo verificar la firma Ed25519 (verificador no disponible)",
                )
            ok = verify_payload(
                payload,
                _b64.b64decode(manifest["signature"]),
                _b64.b64decode(manifest["public_key"]),
            )
            if not ok:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "Firma Ed25519 inválida")

    _upsert_state(ctx.conn, ctx.tenant_id, device["id"],
                  channel=channel, staged_version=body.version, status="staged",
                  blocked_reason=None)
    ctx.audit("updates.staged", resource_type="device", resource_id=device["id"],
              payload={"version": body.version, "verified_file": bool(body.file_path)})
    ctx.emit("updates", "client.update.downloaded",
             {"device_id": device["id"], "version": body.version})
    return {"status": "staged", "version": body.version}


@router.post("/install")
def install_update(body: InstallIn, ctx: SessionContext = Depends(require_session)) -> dict[str, Any]:
    """Port de canInstallSafely() + quitAndInstall(): gate M19 antes de instalar."""
    device = get_tenant_device(ctx.conn, ctx.tenant_id, body.device_id)
    state = _get_state(ctx.conn, ctx.tenant_id, device["id"])
    if state is None or not state["staged_version"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No hay versión staged para instalar")

    blocked_reason: str | None = None
    try:
        from .m19_offline_sync import pending_mutations
    except Exception:
        # Fail-closed: sin M19 no podemos garantizar que no haya mutaciones.
        blocked_reason = "módulo de sync no disponible (fail-closed)"
    else:
        pending = pending_mutations(ctx.conn, ctx.tenant_id, device["id"])
        if pending > 0:
            blocked_reason = "pending mutations"

    if blocked_reason is None:
        sync_state = ctx.conn.execute(
            "SELECT mode FROM fnd_sync_state WHERE device_id = ? AND tenant_id = ?",
            (device["id"], ctx.tenant_id),
        ).fetchone()
        if sync_state is not None and sync_state["mode"] == "full":
            blocked_reason = "full refresh sin reconciliar"

    if blocked_reason is not None:
        _upsert_state(ctx.conn, ctx.tenant_id, device["id"],
                      status="blocked", blocked_reason=blocked_reason)
        ctx.audit("updates.install_blocked", resource_type="device", resource_id=device["id"],
                  payload={"blocked_reason": blocked_reason,
                           "staged_version": state["staged_version"]})
        return {"status": "blocked", "blocked_reason": blocked_reason,
                "staged_version": state["staged_version"]}

    version = state["staged_version"]
    _upsert_state(ctx.conn, ctx.tenant_id, device["id"],
                  status="installed", current_version=version, staged_version=None,
                  available_version=None, blocked_reason=None)
    ctx.audit("updates.installed", resource_type="device", resource_id=device["id"],
              payload={"version": version})
    ctx.emit("updates", "client.update.installed",
             {"device_id": device["id"], "version": version})
    return {"status": "installed", "version": version}


@router.get("/state")
def update_state(
    device_id: str, ctx: SessionContext = Depends(require_session)
) -> dict[str, Any]:
    device = get_tenant_device(ctx.conn, ctx.tenant_id, device_id)
    state = _get_state(ctx.conn, ctx.tenant_id, device["id"])
    if state is None:
        return {"device_id": device["id"], "status": "idle", "current_version": None,
                "staged_version": None, "blocked_reason": None}
    return to_dict(state) or {}
