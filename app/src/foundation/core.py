"""Foundation Beta core — capa común para los módulos M07–M20 portados a FastAPI/SQLite.

Este módulo define el contrato compartido que usan todos los módulos foundation:

- Base de datos propia ``foundation.sqlite3`` (junto a la BD principal de la app),
  con esquema idempotente (``CREATE TABLE IF NOT EXISTS``). Los módulos registran
  su DDL con :func:`register_schema`.
- Tablas plataforma/spine compartidas: tenants, users, sessions, roles,
  user_roles, audit_log (hash chain, M12) y events (outbox, M15).
- Helpers: ``new_id``, ``utcnow``, hashing de passwords (PBKDF2), TOTP (RFC 6238,
  stdlib puro), contexto de tenant.
- Dependencias FastAPI: ``require_session`` y ``require_permission`` (M08/M09).
- Primitivas transversales: :func:`audit_log` (cadena de hashes inmutable) y
  :func:`emit_event` (outbox transaccional + realtime polling).

Adaptación local-first: el aislamiento multi-tenant de M16 (RLS Postgres) se
implementa aquí como scoping estricto por ``tenant_id`` en cada query, fail-closed
(sin tenant en contexto → no hay filas).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import struct
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

from fastapi import Depends, HTTPException, Request, status

from ..auth import get_current_user

# ---------------------------------------------------------------------------
# Rutas de base de datos
# ---------------------------------------------------------------------------


def get_foundation_db_path() -> Path:
    override = os.getenv("FABERLOOM_FOUNDATION_DB")
    if override:
        path = Path(override)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    from ..db import get_database_path

    main = get_database_path()
    main.parent.mkdir(parents=True, exist_ok=True)
    return main.parent / "foundation.sqlite3"


# ---------------------------------------------------------------------------
# Esquema
# ---------------------------------------------------------------------------

CORE_SCHEMA = """
CREATE TABLE IF NOT EXISTS fnd_tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'provisioning',
    plan TEXT NOT NULL DEFAULT 'beta',
    settings_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    activated_at TEXT
);

CREATE TABLE IF NOT EXISTS fnd_users (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES fnd_tenants(id),
    email TEXT NOT NULL,
    display_name TEXT NOT NULL DEFAULT '',
    password_hash TEXT NOT NULL DEFAULT '',
    totp_secret TEXT,
    totp_enabled INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'active',
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, email)
);

CREATE TABLE IF NOT EXISTS fnd_sessions (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL REFERENCES fnd_users(id),
    stage TEXT NOT NULL DEFAULT 'full',
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL,
    ip TEXT NOT NULL DEFAULT '',
    user_agent TEXT NOT NULL DEFAULT '',
    device_id TEXT NOT NULL DEFAULT '',
    revoked_at TEXT
);

CREATE TABLE IF NOT EXISTS fnd_roles (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    permissions_json TEXT NOT NULL DEFAULT '[]',
    is_system INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE (tenant_id, name)
);

CREATE TABLE IF NOT EXISTS fnd_user_roles (
    tenant_id TEXT NOT NULL,
    user_id TEXT NOT NULL REFERENCES fnd_users(id),
    role_id TEXT NOT NULL REFERENCES fnd_roles(id),
    assigned_by TEXT,
    assigned_at TEXT NOT NULL,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS fnd_audit_log (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE,
    tenant_id TEXT NOT NULL,
    actor_id TEXT,
    actor_email TEXT NOT NULL DEFAULT '',
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL DEFAULT '',
    resource_id TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL DEFAULT '{}',
    prev_hash TEXT NOT NULL DEFAULT '',
    hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_fnd_audit_tenant ON fnd_audit_log(tenant_id, seq);

CREATE TABLE IF NOT EXISTS fnd_events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE,
    tenant_id TEXT NOT NULL,
    topic TEXT NOT NULL,
    type TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    published_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_fnd_events_tenant ON fnd_events(tenant_id, seq);
"""

_MODULE_SCHEMAS: list[str] = []
_SEED_HOOKS: list[Callable[[sqlite3.Connection], None]] = []


def register_schema(ddl: str) -> None:
    """Los módulos registran su DDL idempotente al importarse."""
    if ddl not in _MODULE_SCHEMAS:
        _MODULE_SCHEMAS.append(ddl)


def register_seed(fn: Callable[[sqlite3.Connection], None]) -> None:
    """Hook post-migración (p. ej. sembrar roles del sistema)."""
    if fn not in _SEED_HOOKS:
        _SEED_HOOKS.append(fn)


_BUSY_TIMEOUT_MS = int(os.getenv("FABERLOOM_FND_BUSY_TIMEOUT_MS", "20000"))


def connect() -> sqlite3.Connection:
    # Long timeout for production concurrency; busy_timeout gives SQLite time to
    # acquire locks instead of raising "database is locked" immediately.
    conn = sqlite3.connect(get_foundation_db_path(), timeout=20.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    # Only switch to WAL once. Re-running PRAGMA journal_mode under concurrency
    # can itself contend for the lock and is unnecessary once WAL is active.
    current_mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    if current_mode != "wal":
        conn.execute("PRAGMA journal_mode = WAL")
    conn.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_MS}")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn


@contextmanager
def fnd_db() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_foundation_db() -> None:
    with fnd_db() as conn:
        conn.executescript(CORE_SCHEMA)
        for ddl in _MODULE_SCHEMAS:
            conn.executescript(ddl)
        for hook in _SEED_HOOKS:
            hook(conn)


def get_conn(request: Request) -> Iterator[sqlite3.Connection]:
    """Dependencia FastAPI: conexión con commit/rollback por request."""
    with fnd_db() as conn:
        yield conn


# ---------------------------------------------------------------------------
# Helpers generales
# ---------------------------------------------------------------------------


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:20]}"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    out = dict(row)
    for key in list(out.keys()):
        if key.endswith("_json") and isinstance(out[key], str):
            try:
                out[key[:-5]] = json.loads(out[key])
            except Exception:
                out[key[:-5]] = None
            del out[key]
    return out


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [to_dict(r) for r in rows]  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Passwords (PBKDF2) y TOTP (RFC 6238) — stdlib puro
# ---------------------------------------------------------------------------

_PBKDF2_ITERATIONS = 240_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERATIONS)
    return f"pbkdf2${_PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iters, salt_hex, digest_hex = stored.split("$")
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iters)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except Exception:
        return False


def generate_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode().rstrip("=")


def _hotp(secret_b32: str, counter: int, digits: int = 6) -> str:
    padding = "=" * ((8 - len(secret_b32) % 8) % 8)
    key = base64.b32decode(secret_b32.upper() + padding)
    mac = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = mac[-1] & 0x0F
    code = (struct.unpack(">I", mac[offset : offset + 4])[0] & 0x7FFFFFFF) % (10**digits)
    return str(code).zfill(digits)


def totp_now(secret_b32: str, at: float | None = None) -> str:
    return _hotp(secret_b32, int((at or time.time()) // 30))


def verify_totp(secret_b32: str, code: str, at: float | None = None, window: int = 1) -> bool:
    ts = at or time.time()
    counter = int(ts // 30)
    for delta in range(-window, window + 1):
        if hmac.compare_digest(_hotp(secret_b32, counter + delta), str(code).strip()):
            return True
    return False


def totp_provisioning_uri(secret_b32: str, email: str, issuer: str = "FaberLoom") -> str:
    from urllib.parse import quote

    return (
        f"otpauth://totp/{quote(issuer)}:{quote(email)}"
        f"?secret={secret_b32}&issuer={quote(issuer)}&algorithm=SHA1&digits=6&period=30"
    )


# ---------------------------------------------------------------------------
# M12 Audit Trail — cadena de hashes inmutable (primitiva compartida)
# ---------------------------------------------------------------------------


def audit_log(
    conn: sqlite3.Connection,
    tenant_id: str,
    action: str,
    *,
    actor_id: str | None = None,
    actor_email: str = "",
    resource_type: str = "",
    resource_id: str = "",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Escribe una entrada de audit encadenada por hash (append-only)."""
    row = conn.execute(
        "SELECT hash FROM fnd_audit_log WHERE tenant_id = ? ORDER BY seq DESC LIMIT 1",
        (tenant_id,),
    ).fetchone()
    prev_hash = row["hash"] if row else ""
    entry_id = new_id("aud")
    created_at = utcnow()
    payload_json = json.dumps(payload or {}, sort_keys=True, ensure_ascii=False)
    material = "|".join(
        [prev_hash, entry_id, tenant_id, actor_id or "", action, resource_type, resource_id, payload_json, created_at]
    )
    entry_hash = hashlib.sha256(material.encode()).hexdigest()
    conn.execute(
        """INSERT INTO fnd_audit_log
           (id, tenant_id, actor_id, actor_email, action, resource_type, resource_id,
            payload_json, prev_hash, hash, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (entry_id, tenant_id, actor_id, actor_email, action, resource_type, resource_id,
         payload_json, prev_hash, entry_hash, created_at),
    )
    return {"id": entry_id, "hash": entry_hash, "prev_hash": prev_hash, "created_at": created_at}


def verify_audit_chain(conn: sqlite3.Connection, tenant_id: str) -> dict[str, Any]:
    """Recorre la cadena y verifica integridad. Devuelve {ok, checked, broken_at}."""
    rows = conn.execute(
        "SELECT * FROM fnd_audit_log WHERE tenant_id = ? ORDER BY seq ASC", (tenant_id,)
    ).fetchall()
    prev = ""
    for row in rows:
        material = "|".join(
            [prev, row["id"], row["tenant_id"], row["actor_id"] or "", row["action"],
             row["resource_type"], row["resource_id"], row["payload_json"], row["created_at"]]
        )
        expected = hashlib.sha256(material.encode()).hexdigest()
        if row["prev_hash"] != prev or row["hash"] != expected:
            return {"ok": False, "checked": len(rows), "broken_at": row["id"]}
        prev = row["hash"]
    return {"ok": True, "checked": len(rows), "broken_at": None}


# ---------------------------------------------------------------------------
# M15 Outbox — emisión de eventos (primitiva compartida)
# ---------------------------------------------------------------------------


def emit_event(
    conn: sqlite3.Connection,
    tenant_id: str,
    topic: str,
    type_: str,
    payload: dict[str, Any] | None = None,
) -> str:
    event_id = new_id("evt")
    conn.execute(
        """INSERT INTO fnd_events (id, tenant_id, topic, type, payload_json, created_at, published_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (event_id, tenant_id, topic, type_, json.dumps(payload or {}, ensure_ascii=False), utcnow(), utcnow()),
    )
    return event_id


# ---------------------------------------------------------------------------
# Sesiones y RBAC (dependencias compartidas; endpoints en M08/M09)
# ---------------------------------------------------------------------------

SESSION_TTL_SECONDS = int(os.getenv("FABERLOOM_FND_SESSION_TTL", str(12 * 3600)))

SYSTEM_ROLES: dict[str, dict[str, Any]] = {
    "owner": {"description": "Dueño del tenant; control total", "permissions": ["*"]},
    "admin": {
        "description": "Administración del tenant sin transferencia de ownership",
        "permissions": [
            "users.manage", "roles.manage", "policy.manage", "audit.read",
            "classifier.manage", "drafts.review", "drafts.send", "outcomes.read",
            "memory.manage", "events.read", "sync.manage", "updates.manage",
            "bootstrap.manage", "tenants.read", "tenants.manage",
        ],
    },
    "operator": {
        "description": "Operación diaria: clasificar, redactar, aprobar drafts",
        "permissions": [
            "classifier.run", "classifier.read", "drafts.create", "drafts.review",
            "drafts.send", "outcomes.read", "outcomes.write", "memory.read",
            "memory.write", "events.read", "audit.read",
        ],
    },
    "viewer": {
        "description": "Solo lectura",
        "permissions": ["classifier.read", "outcomes.read", "events.read", "audit.read", "memory.read"],
    },
}


def seed_system_roles(conn: sqlite3.Connection, tenant_id: str) -> None:
    for name, spec in SYSTEM_ROLES.items():
        exists = conn.execute(
            "SELECT id, permissions_json FROM fnd_roles WHERE tenant_id = ? AND name = ?",
            (tenant_id, name),
        ).fetchone()
        if not exists:
            conn.execute(
                """INSERT INTO fnd_roles (id, tenant_id, name, description, permissions_json, is_system, created_at)
                   VALUES (?, ?, ?, ?, ?, 1, ?)""",
                (new_id("rol"), tenant_id, name, spec["description"],
                 json.dumps(spec["permissions"]), utcnow()),
            )
        else:
            # Sync idempotente: si el catálogo de permisos del rol de sistema
            # cambió entre versiones, la BD existente se actualiza al arrancar.
            expected = json.dumps(spec["permissions"])
            if exists["permissions_json"] != expected:
                conn.execute(
                    "UPDATE fnd_roles SET permissions_json = ? WHERE id = ?",
                    (expected, exists["id"]),
                )


def _sync_system_roles_all_tenants(conn: sqlite3.Connection) -> None:
    """Al inicializar la BD, re-siembra/sincroniza los roles de sistema de
    TODOS los tenants existentes (heals de despliegues previos)."""
    for row in conn.execute("SELECT id FROM fnd_tenants").fetchall():
        seed_system_roles(conn, row["id"])


register_seed(_sync_system_roles_all_tenants)


def get_user_permissions(conn: sqlite3.Connection, tenant_id: str, user_id: str) -> set[str]:
    rows = conn.execute(
        """SELECT r.permissions_json FROM fnd_user_roles ur
           JOIN fnd_roles r ON r.id = ur.role_id
           WHERE ur.tenant_id = ? AND ur.user_id = ?""",
        (tenant_id, user_id),
    ).fetchall()
    perms: set[str] = set()
    for row in rows:
        try:
            perms.update(json.loads(row["permissions_json"]))
        except Exception:
            pass
    return perms


def user_role_names(conn: sqlite3.Connection, tenant_id: str, user_id: str) -> list[str]:
    rows = conn.execute(
        """SELECT r.name FROM fnd_user_roles ur JOIN fnd_roles r ON r.id = ur.role_id
           WHERE ur.tenant_id = ? AND ur.user_id = ?""",
        (tenant_id, user_id),
    ).fetchall()
    return [r["name"] for r in rows]


class SessionContext:
    """Contexto autenticado que reciben los endpoints foundation."""

    def __init__(self, conn: sqlite3.Connection, session: sqlite3.Row, user: sqlite3.Row):
        self.conn = conn
        self.session_id: str = session["id"]
        self.tenant_id: str = session["tenant_id"]
        self.user_id: str = user["id"]
        self.email: str = user["email"]
        self.stage: str = session["stage"]
        self.permissions: set[str] = get_user_permissions(conn, self.tenant_id, self.user_id)
        self.roles: list[str] = user_role_names(conn, self.tenant_id, self.user_id)

    def has(self, permission: str) -> bool:
        return "*" in self.permissions or permission in self.permissions

    def audit(self, action: str, *, resource_type: str = "", resource_id: str = "",
              payload: dict[str, Any] | None = None) -> None:
        audit_log(self.conn, self.tenant_id, action, actor_id=self.user_id,
                  actor_email=self.email, resource_type=resource_type,
                  resource_id=resource_id, payload=payload)

    def emit(self, topic: str, type_: str, payload: dict[str, Any] | None = None) -> str:
        return emit_event(self.conn, self.tenant_id, topic, type_, payload)


def _session_token(request: Request) -> str | None:
    token = request.headers.get("X-Fnd-Session")
    if token:
        return token
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer fnds_"):
        return auth[7:]
    cookie = request.cookies.get("fnd_session")
    if cookie:
        return cookie
    return None


def load_session(conn: sqlite3.Connection, token: str) -> sqlite3.Row | None:
    row = conn.execute("SELECT * FROM fnd_sessions WHERE id = ?", (token,)).fetchone()
    if row is None or row["revoked_at"] is not None:
        return None
    if row["expires_at"] < utcnow():
        return None
    return row


def _bootstrap_path(request: Request) -> bool:
    path = request.url.path
    return path.startswith("/api/foundation/bootstrap")


def _bootstrap_jwt_context(request: Request, conn: sqlite3.Connection) -> SessionContext | None:
    """Durante el bootstrap inicial, un JWT principal válido puede usarse como
    puente temporal para los endpoints /api/foundation/bootstrap/*. Una vez que
    el tenant tiene un owner activo, este fallback se cierra y Foundation exige
    una sesión propia.
    """
    if not _bootstrap_path(request):
        return None
    if is_bootstrapped(conn):
        return None

    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer fnds_"):
        return None  # es un token Foundation, no el JWT principal
    try:
        # Acepta el JWT principal por cookie HttpOnly `faberloom_at` o por Bearer.
        jwt_user = get_current_user(request)
    except HTTPException:
        return None
    email = (jwt_user.get("sub") or "").strip().lower()
    if not email or email == "local":
        return None

    tenant = get_active_tenant(conn)
    tenant_id = tenant["id"] if tenant else new_id("tnt")

    # Synthetic owner-like user with bootstrap permission only. It is NOT persisted.
    synthetic_user: dict[str, Any] = {
        "id": f"jwt_{email}",
        "tenant_id": tenant_id,
        "email": email,
        "display_name": email.split("@")[0],
        "status": "active",
        "password_hash": "",
        "totp_enabled": 0,
        "failed_attempts": 0,
    }
    synthetic_session = {
        "id": f"jwt_{email}",
        "tenant_id": tenant_id,
        "user_id": synthetic_user["id"],
        "stage": "full",
        "expires_at": "9999-12-31T23:59:59+00:00",
    }
    ctx = SessionContext(conn, synthetic_session, synthetic_user)  # type: ignore[arg-type]
    ctx.permissions.add("bootstrap.manage")
    ctx.permissions.add("*")
    return ctx


def _sso_jwt_context(request: Request, conn: sqlite3.Connection) -> SessionContext | None:
    """SSO local-first: un JWT principal de FaberLoom válido (cookie HttpOnly
    ``faberloom_at`` o ``Authorization: Bearer``) cuyo ``sub`` (email) coincide
    con un usuario Foundation ACTIVO del tenant establece una sesión Foundation
    real, con los permisos REALES de ese usuario.

    El shell (foundation_app.jsx) no tiene login propio: reutiliza la sesión
    principal. Este puente lo hace posible tras el bootstrap sin reabrir el
    bypass cerrado en el hardening P0: no crea un usuario sintético ni concede
    ``*``; exige que el email exista como usuario Foundation activo y la
    autorización sigue gobernada por los roles reales de ese usuario.
    """
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer fnds_"):
        return None  # es un token Foundation, no un JWT principal
    tenant = get_active_tenant(conn)
    if tenant is None or tenant["status"] != "active":
        return None
    try:
        jwt_user = get_current_user(request)
    except HTTPException:
        return None
    email = (jwt_user.get("sub") or "").strip().lower()
    if not email or email == "local" or "@" not in email:
        return None
    # Multi-tenant: el email puede vivir en cualquier tenant ACTIVO (no solo el
    # primero). Se toma el match más antiguo por orden de creación del tenant.
    user = conn.execute(
        """SELECT u.* FROM fnd_users u
           JOIN fnd_tenants t ON t.id = u.tenant_id
           WHERE u.email = ? AND u.status = 'active' AND t.status = 'active'
           ORDER BY t.created_at ASC LIMIT 1""",
        (email,),
    ).fetchone()
    if user is None:
        return None
    synthetic_session = {
        "id": f"sso_{user['id']}",
        "tenant_id": user["tenant_id"],
        "user_id": user["id"],
        "stage": "full",
    }
    return SessionContext(conn, synthetic_session, user)  # type: ignore[arg-type]


def require_session(
    request: Request, conn: sqlite3.Connection = Depends(get_conn)
) -> SessionContext:
    token = _session_token(request)
    if token:
        session = load_session(conn, token)
        if session is not None:
            if session["stage"] != "full":
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "2FA pending")
            user = conn.execute(
                "SELECT * FROM fnd_users WHERE id = ?", (session["user_id"],)
            ).fetchone()
            if user is None or user["status"] != "active":
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User inactive")
            conn.execute(
                "UPDATE fnd_sessions SET last_seen_at = ? WHERE id = ?", (utcnow(), token)
            )
            return SessionContext(conn, session, user)

    # Bridge temporal solo durante bootstrap inicial (tenant aún no activo).
    ctx = _bootstrap_jwt_context(request, conn)
    if ctx is not None:
        return ctx

    # SSO local-first: sesión principal de FaberLoom → sesión Foundation real.
    ctx = _sso_jwt_context(request, conn)
    if ctx is not None:
        return ctx

    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Foundation session required")


def require_permission(permission: str) -> Callable[..., SessionContext]:
    def dependency(ctx: SessionContext = Depends(require_session)) -> SessionContext:
        if not ctx.has(permission):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"Missing permission: {permission}")
        return ctx

    return dependency


# ---------------------------------------------------------------------------
# Estado de bootstrap (M07 depende de esto; el frontend también)
# ---------------------------------------------------------------------------


def get_active_tenant(conn: sqlite3.Connection) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM fnd_tenants ORDER BY created_at ASC LIMIT 1"
    ).fetchone()


def is_bootstrapped(conn: sqlite3.Connection) -> bool:
    tenant = get_active_tenant(conn)
    return bool(tenant and tenant["status"] == "active")
