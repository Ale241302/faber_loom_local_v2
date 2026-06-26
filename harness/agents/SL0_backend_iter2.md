Resumen de lo que hice y por qué:

- **Endurecí la costura `Context`** separando contexto `system` para bootstrap/listado/creación de workspaces y contexto scoped para datos de workspace. Esto evita que las queries futuras se vuelvan ambiguas y prepara SL2a/SL3.5 para sellado real.
- **Subí el schema a `SCHEMA_VERSION = 2`** con migración versionada que agrega `routine` y `routine_run`, más la matriz completa de campos latentes exigidos por el plan.
- **Refactoricé DB + AuditWriter** para que creación de workspace y `audit_log` compartan transacción DB; el JSONL queda como espejo local best-effort después del commit.
- **Validé input de API con Pydantic v2**, incluyendo rechazo de nombres/slugs en blanco.
- **Ajusté `main.py`** para que `run_desktop(host, port)` use realmente el host/port recibidos o variables `SPACELOOM_HOST` / `SPACELOOM_PORT`.
- **Agregué tests versionados** para health, seed idempotente, schema contractual, audit, slug único y aislamiento básico por `tenant_id`.
- **Ejecuté verificación**: `pytest` pasó `6 passed`, `compileall` pasó, smoke API/static devolvió 200 y corrí `graphify update .`.

```python:app/src/context.py
"""Context layer for SpaceLoom SL0.

Every query that reads or writes application data receives a Context. In SL0 the
app is single-user/local-first, so tenant_id and user_id are latent fields; the
seam exists now to avoid rewriting repositories when Etapa 2-3 adds real access
enforcement.

Two scopes are intentionally explicit:

* ``system_context()``: bootstrap-only operations such as creating/listing
  workspaces. It is not a data-read escape hatch for workspace-owned rows.
* ``Context(workspace_id=...)``: scoped application access. Query helpers for
  workspace-owned tables must constrain by this ``workspace_id``.
"""

from __future__ import annotations

from dataclasses import dataclass


SYSTEM_WORKSPACE_ID = "__system__"
DEFAULT_LOCAL_USER_ID = "local"
DEFAULT_LOCAL_ACTOR_ROLE = "owner"


@dataclass(frozen=True, slots=True)
class Context:
    """Access scope and actor identity for a unit of work."""

    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None

    def require_workspace(self) -> str:
        """Return the scoped workspace id or raise for malformed context."""

        if not self.workspace_id:
            raise ValueError("Context.workspace_id is required")
        return self.workspace_id

    def require_scoped_workspace(self) -> str:
        """Return an application workspace id; reject bootstrap/system scope."""

        workspace_id = self.require_workspace()
        if workspace_id == SYSTEM_WORKSPACE_ID:
            raise ValueError("A concrete workspace Context is required for scoped data access")
        return workspace_id

    def require_system(self) -> None:
        """Assert that this context is explicitly bootstrap/system scoped."""

        if self.workspace_id != SYSTEM_WORKSPACE_ID:
            raise ValueError("A system Context is required for bootstrap workspace operations")

    @property
    def is_system(self) -> bool:
        return self.workspace_id == SYSTEM_WORKSPACE_ID

    def resolved_actor_id(self) -> str | None:
        return self.actor_id or self.user_id

    def with_workspace(self, workspace_id: str) -> "Context":
        return Context(
            workspace_id=workspace_id,
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            actor_id=self.actor_id,
            actor_role_at_decision=self.actor_role_at_decision,
        )


def system_context(
    *,
    tenant_id: str | None = None,
    user_id: str | None = DEFAULT_LOCAL_USER_ID,
    actor_id: str | None = DEFAULT_LOCAL_USER_ID,
    actor_role_at_decision: str | None = DEFAULT_LOCAL_ACTOR_ROLE,
) -> Context:
    """Bootstrap context for health, seed, and workspace listing/creation."""

    return Context(
        workspace_id=SYSTEM_WORKSPACE_ID,
        tenant_id=tenant_id,
        user_id=user_id,
        actor_id=actor_id,
        actor_role_at_decision=actor_role_at_decision,
    )
```

```python:app/src/models.py
"""SQLite schema migrations and Pydantic v2 API models for SpaceLoom SL0."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SCHEMA_VERSION = 2
CURRENT_SCHEMA_VERSION = SCHEMA_VERSION


# Migration policy for SL0:
# - v1 is the original skeleton contract.
# - v2 hardens the contract-first seams required before closing SL0:
#   routine/routine_run and a uniform latent-field surface.
MIGRATIONS: dict[int, str] = {
    1: """
    CREATE TABLE IF NOT EXISTS workspace (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        tenant_id TEXT,
        user_id TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS kb_source (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        content_text TEXT,
        content_blob BLOB,
        meta_json TEXT NOT NULL DEFAULT '{}',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT NOT NULL DEFAULT 'v1',
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS chat (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        title TEXT NOT NULL,
        model_preset TEXT NOT NULL DEFAULT 'default',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS message (
        id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        role TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
        content_json TEXT NOT NULL,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS draft (
        id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        status TEXT NOT NULL CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected', 'exported')),
        content_json TEXT NOT NULL,
        sources_json TEXT NOT NULL DEFAULT '[]',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        approved_by TEXT,
        approved_at TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        action TEXT NOT NULL,
        payload_json TEXT NOT NULL DEFAULT '{}',
        approved_by TEXT,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_kb_source_workspace_id ON kb_source(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_chat_workspace_id ON chat(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_message_chat_id ON message(chat_id);
    CREATE INDEX IF NOT EXISTS idx_draft_chat_id ON draft(chat_id);
    CREATE INDEX IF NOT EXISTS idx_audit_log_workspace_id ON audit_log(workspace_id);
    """,
    2: """
    ALTER TABLE workspace ADD COLUMN actor_id TEXT;
    ALTER TABLE workspace ADD COLUMN actor_role_at_decision TEXT;
    ALTER TABLE workspace ADD COLUMN routine_version TEXT;
    ALTER TABLE workspace ADD COLUMN skill_version TEXT;
    ALTER TABLE workspace ADD COLUMN source_version TEXT;
    ALTER TABLE workspace ADD COLUMN approved_by TEXT;

    ALTER TABLE kb_source ADD COLUMN actor_id TEXT;
    ALTER TABLE kb_source ADD COLUMN actor_role_at_decision TEXT;
    ALTER TABLE kb_source ADD COLUMN approved_by TEXT;

    ALTER TABLE chat ADD COLUMN actor_id TEXT;
    ALTER TABLE chat ADD COLUMN actor_role_at_decision TEXT;
    ALTER TABLE chat ADD COLUMN approved_by TEXT;

    ALTER TABLE message ADD COLUMN workspace_id TEXT;
    ALTER TABLE message ADD COLUMN approved_by TEXT;

    CREATE TABLE IF NOT EXISTS routine (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        name TEXT NOT NULL,
        skill_md TEXT NOT NULL DEFAULT '',
        tools_allowlist TEXT NOT NULL DEFAULT '[]',
        schema_output_json TEXT NOT NULL DEFAULT '{}',
        preset_id TEXT,
        trigger_json TEXT NOT NULL DEFAULT '{}',
        persona_md TEXT NOT NULL DEFAULT '',
        is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 2,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS routine_run (
        id TEXT PRIMARY KEY,
        routine_id TEXT NOT NULL,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        input_json TEXT NOT NULL DEFAULT '{}',
        output_json TEXT NOT NULL DEFAULT '{}',
        evidence_json TEXT NOT NULL DEFAULT '[]',
        status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'requires_hitl')),
        edit_pct REAL,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 2,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (routine_id) REFERENCES routine(id) ON DELETE CASCADE,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    UPDATE message
    SET workspace_id = (
        SELECT chat.workspace_id FROM chat WHERE chat.id = message.chat_id
    )
    WHERE workspace_id IS NULL;

    CREATE INDEX IF NOT EXISTS idx_message_workspace_id ON message(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_routine_workspace_id ON routine(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_routine_run_workspace_id ON routine_run(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_routine_run_routine_id ON routine_run(routine_id);
    """,
}


class HealthRead(BaseModel):
    status: Literal["ok"] = "ok"
    app: str = "SpaceLoom"
    schema_version: int
    database_path: str


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=140)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Workspace name cannot be blank")
        return stripped

    @field_validator("slug")
    @classmethod
    def slug_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("Workspace slug cannot be blank")
        return stripped


class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
    updated_at: str


class WorkspaceListRead(BaseModel):
    workspaces: list[WorkspaceRead]


class AuditEvent(BaseModel):
    id: str
    workspace_id: str
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str | None = None
    user_id: str | None = None
    approved_by: str | None = None
    schema_version: int = SCHEMA_VERSION
    routine_version: str | None = None
    skill_version: str | None = None
    source_version: str | None = None
    created_at: str


class RoutineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    name: str
    skill_md: str
    tools_allowlist: str
    schema_output_json: str
    preset_id: str | None = None
    trigger_json: str
    persona_md: str
    is_active: int
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
    updated_at: str


class RoutineRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    routine_id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    input_json: str
    output_json: str
    evidence_json: str
    status: str
    edit_pct: float | None = None
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
```

```python:app/src/db.py
"""SQLite initialization, migrations, and SL0 data access helpers.

Raw sqlite3 keeps SL0 small and local-first. Versioned migrations are tracked in
_schema_version. Every application data query takes a Context. Bootstrap queries
are explicitly named ``system_*``; workspace-owned reads must constrain by
``ctx.workspace_id``.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import unicodedata
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .context import Context
from .models import MIGRATIONS, SCHEMA_VERSION, WorkspaceCreate


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"
DEFAULT_DB_PATH = DATA_DIR / "spaceloom.sqlite3"

WORKSPACE_COLUMNS = """
    id,
    name,
    slug,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    created_at,
    updated_at
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()
    return slug or "workspace"


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def get_database_path() -> Path:
    configured = os.getenv("SPACELOOM_DB_PATH")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DB_PATH


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def get_db() -> Iterator[sqlite3.Connection]:
    """FastAPI dependency yielding a configured SQLite connection."""

    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[None]:
    """Commit/rollback a unit of work unless already inside a transaction."""

    outer_transaction = conn.in_transaction
    try:
        yield
    except Exception:
        if not outer_transaction:
            conn.rollback()
        raise
    else:
        if not outer_transaction:
            conn.commit()


def initialize_database(conn: sqlite3.Connection | None = None) -> None:
    owns_conn = conn is None
    conn = conn or connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS _schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )
        applied = {
            int(row["version"])
            for row in conn.execute("SELECT version FROM _schema_version").fetchall()
        }
        for version in sorted(MIGRATIONS):
            if version in applied:
                continue
            conn.executescript(MIGRATIONS[version])
            conn.execute(
                "INSERT INTO _schema_version(version, applied_at) VALUES (?, ?)",
                (version, utc_now()),
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if owns_conn:
            conn.close()


init_db = initialize_database


def current_schema_version(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT MAX(version) AS version FROM _schema_version").fetchone()
    if row is None or row["version"] is None:
        return 0
    return int(row["version"])


def get_schema_version() -> int:
    with db_session() as conn:
        try:
            return current_schema_version(conn)
        except sqlite3.OperationalError:
            return 0


def assert_schema_current() -> None:
    actual = get_schema_version()
    if actual != SCHEMA_VERSION:
        raise RuntimeError(
            f"Database schema version {actual} does not match expected {SCHEMA_VERSION}"
        )


def _workspace_slug_exists(ctx: Context, conn: sqlite3.Connection, slug: str) -> bool:
    ctx.require_system()
    row = conn.execute("SELECT 1 FROM workspace WHERE slug = ? LIMIT 1", (slug,)).fetchone()
    return row is not None


def unique_workspace_slug(ctx: Context, conn: sqlite3.Connection, requested_slug: str) -> str:
    ctx.require_system()
    base = slugify(requested_slug)
    if not _workspace_slug_exists(ctx, conn, base):
        return base
    suffix = 2
    while True:
        candidate = f"{base}-{suffix}"
        if not _workspace_slug_exists(ctx, conn, candidate):
            return candidate
        suffix += 1


def system_list_workspaces(ctx: Context, conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """List visible workspaces from the explicit bootstrap/system scope."""

    ctx.require_system()
    rows = conn.execute(
        f"""
        SELECT {WORKSPACE_COLUMNS}
        FROM workspace
        WHERE tenant_id IS ?
        ORDER BY created_at ASC, name ASC
        """,
        (ctx.tenant_id,),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


# Backwards-compatible public name for the SL0 API route.
def list_workspaces(ctx: Context, conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return system_list_workspaces(ctx, conn)


def get_workspace(ctx: Context, conn: sqlite3.Connection) -> dict[str, Any] | None:
    """Read the workspace in ``ctx``; never read an arbitrary workspace id."""

    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        f"""
        SELECT {WORKSPACE_COLUMNS}
        FROM workspace
        WHERE id = ? AND tenant_id IS ?
        """,
        (workspace_id, ctx.tenant_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def system_get_workspace(
    ctx: Context,
    conn: sqlite3.Connection,
    workspace_id: str,
) -> dict[str, Any] | None:
    """Bootstrap-only lookup used by seed/tests; not for workspace-owned data."""

    ctx.require_system()
    row = conn.execute(
        f"""
        SELECT {WORKSPACE_COLUMNS}
        FROM workspace
        WHERE id = ? AND tenant_id IS ?
        """,
        (workspace_id, ctx.tenant_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def system_get_workspace_by_slug(
    ctx: Context,
    conn: sqlite3.Connection,
    slug: str,
) -> dict[str, Any] | None:
    ctx.require_system()
    row = conn.execute(
        f"""
        SELECT {WORKSPACE_COLUMNS}
        FROM workspace
        WHERE slug = ? AND tenant_id IS ?
        """,
        (slug, ctx.tenant_id),
    ).fetchone()
    return row_to_dict(row) if row else None


# Backwards-compatible public name for seed.
def get_workspace_by_slug(
    ctx: Context,
    conn: sqlite3.Connection,
    slug: str,
) -> dict[str, Any] | None:
    return system_get_workspace_by_slug(ctx, conn, slug)


def create_workspace(
    ctx: Context,
    conn: sqlite3.Connection,
    payload: WorkspaceCreate,
) -> dict[str, Any]:
    """Insert a workspace in the system scope.

    The function does not commit. Route/seed call sites wrap it in ``transaction``
    so workspace creation and audit-log insertion share one DB transaction.
    """

    ctx.require_system()
    now = utc_now()
    workspace_id = new_id("ws")
    name = payload.name.strip()
    slug = unique_workspace_slug(ctx, conn, payload.slug or name)

    conn.execute(
        """
        INSERT INTO workspace(
            id,
            name,
            slug,
            tenant_id,
            user_id,
            actor_id,
            actor_role_at_decision,
            routine_version,
            skill_version,
            schema_version,
            source_version,
            approved_by,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            name,
            slug,
            ctx.tenant_id,
            ctx.user_id,
            ctx.resolved_actor_id(),
            ctx.actor_role_at_decision,
            None,
            None,
            SCHEMA_VERSION,
            None,
            None,
            now,
            now,
        ),
    )
    created = system_get_workspace(ctx, conn, workspace_id)
    if created is None:
        raise RuntimeError("Workspace was created but could not be read back")
    return created


def insert_audit_log(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    event_id: str,
    action: str,
    payload: dict[str, Any],
    approved_by: str | None = None,
    routine_version: str | None = None,
    skill_version: str | None = None,
    source_version: str | None = None,
    created_at: str | None = None,
) -> None:
    """Insert an audit event row.

    This helper intentionally does not commit; callers decide transaction scope.
    """

    ctx.require_scoped_workspace()
    conn.execute(
        """
        INSERT INTO audit_log(
            id,
            workspace_id,
            tenant_id,
            user_id,
            actor_id,
            actor_role_at_decision,
            action,
            payload_json,
            approved_by,
            routine_version,
            skill_version,
            schema_version,
            source_version,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            ctx.workspace_id,
            ctx.tenant_id,
            ctx.user_id,
            ctx.resolved_actor_id(),
            ctx.actor_role_at_decision,
            action,
            json.dumps(payload, ensure_ascii=False, sort_keys=True),
            approved_by,
            routine_version,
            skill_version,
            SCHEMA_VERSION,
            source_version,
            created_at or utc_now(),
        ),
    )
```

```python:app/src/audit.py
"""AuditWriter seam for SpaceLoom.

Today it appends JSONL to app/data/audit.jsonl and mirrors the same event into
the audit_log table. Tomorrow this interface can be backed by an outbox/table
without changing route call sites.

Durability rule in SL0: the database row is the source of truth. JSONL is a
best-effort local mirror for inspectability and handoff to a future outbox.
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any

from .context import Context
from .db import DATA_DIR, insert_audit_log, new_id, transaction, utc_now
from .models import AuditEvent


_audit_lock = threading.Lock()


class AuditWriter:
    def __init__(self, audit_path: Path | None = None) -> None:
        self.audit_path = audit_path or (DATA_DIR / "audit.jsonl")

    def write(
        self,
        ctx: Context,
        conn: sqlite3.Connection,
        *,
        action: str,
        payload: dict[str, Any] | None = None,
        approved_by: str | None = None,
        routine_version: str | None = None,
        skill_version: str | None = None,
        source_version: str | None = None,
        mirror_jsonl: bool = True,
    ) -> AuditEvent:
        """Write one audit event.

        ``audit_log`` insertion participates in the caller's transaction when
        one is active. If no transaction is active, this method commits its own
        DB unit of work and then appends the JSONL mirror. If a transaction is
        already active, call ``mirror(event)`` after the outer commit.
        """

        outer_transaction = conn.in_transaction
        created_at = utc_now()
        event = AuditEvent(
            id=new_id("audit"),
            workspace_id=ctx.require_scoped_workspace(),
            actor_id=ctx.resolved_actor_id(),
            actor_role_at_decision=ctx.actor_role_at_decision,
            action=action,
            payload=payload or {},
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id,
            approved_by=approved_by,
            routine_version=routine_version,
            skill_version=skill_version,
            source_version=source_version,
            created_at=created_at,
        )

        with transaction(conn):
            insert_audit_log(
                ctx,
                conn,
                event_id=event.id,
                action=action,
                payload=event.payload,
                approved_by=approved_by,
                routine_version=routine_version,
                skill_version=skill_version,
                source_version=source_version,
                created_at=created_at,
            )

        if mirror_jsonl and not outer_transaction:
            self.mirror(event)
        return event

    def mirror(self, event: AuditEvent) -> None:
        """Append an already-committed audit event to the JSONL mirror."""

        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with _audit_lock:
            with self.audit_path.open("a", encoding="utf-8") as handle:
                handle.write(event.model_dump_json() + "\n")


audit_writer = AuditWriter()
```

```python:app/src/seed.py
"""SL0 seed data.

The seed is intentionally tiny: one demo workspace so the app can open with
persistent local state. No business facts are invented here.
"""

from __future__ import annotations

import sqlite3

from .audit import audit_writer
from .context import Context, system_context
from .db import create_workspace, get_workspace_by_slug, transaction
from .models import AuditEvent, WorkspaceCreate


DEMO_WORKSPACE_NAME = "MWT Demo"
DEMO_WORKSPACE_SLUG = "mwt-demo"


def seed_demo_workspace(conn: sqlite3.Connection) -> dict:
    bootstrap_ctx = system_context()
    existing = get_workspace_by_slug(bootstrap_ctx, conn, DEMO_WORKSPACE_SLUG)
    if existing is not None:
        return existing

    event: AuditEvent | None = None
    with transaction(conn):
        created = create_workspace(
            bootstrap_ctx,
            conn,
            WorkspaceCreate(name=DEMO_WORKSPACE_NAME, slug=DEMO_WORKSPACE_SLUG),
        )
        workspace_ctx = Context(
            workspace_id=created["id"],
            tenant_id=created.get("tenant_id"),
            user_id=created.get("user_id") or "local",
            actor_id=created.get("actor_id") or "local",
            actor_role_at_decision=created.get("actor_role_at_decision") or "owner",
        )
        event = audit_writer.write(
            workspace_ctx,
            conn,
            action="workspace.seeded",
            payload={
                "workspace_id": created["id"],
                "name": created["name"],
                "slug": created["slug"],
            },
            mirror_jsonl=False,
        )

    if event is not None:
        audit_writer.mirror(event)
    return created
```

```python:app/src/api.py
from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Request, status

from .audit import audit_writer
from .context import Context, system_context
from .db import (
    create_workspace,
    get_database_path,
    get_db,
    get_schema_version,
    get_workspace,
    list_workspaces,
    transaction,
)
from .models import AuditEvent, HealthRead, WorkspaceCreate, WorkspaceListRead, WorkspaceRead


router = APIRouter(prefix="/api", tags=["api"])


def context_from_request(request: Request, workspace_id: str | None = None) -> Context:
    # SL0 is local single-user. These headers preserve the future contract seam;
    # they are not treated as security authority for multi-tenant access.
    tenant_id = request.headers.get("x-tenant-id") or None
    user_id = request.headers.get("x-user-id") or "local"
    actor_id = request.headers.get("x-actor-id") or user_id
    actor_role = request.headers.get("x-actor-role") or "owner"
    if workspace_id:
        return Context(
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            user_id=user_id,
            actor_id=actor_id,
            actor_role_at_decision=actor_role,
        )
    return system_context(
        tenant_id=tenant_id,
        user_id=user_id,
        actor_id=actor_id,
        actor_role_at_decision=actor_role,
    )


@router.get("/health", response_model=HealthRead)
def health() -> HealthRead:
    return HealthRead(
        status="ok",
        schema_version=get_schema_version(),
        database_path=str(get_database_path()),
    )


@router.get("/workspaces", response_model=WorkspaceListRead)
def api_list_workspaces(
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> WorkspaceListRead:
    ctx = context_from_request(request)
    return WorkspaceListRead(workspaces=[WorkspaceRead(**row) for row in list_workspaces(ctx, conn)])


@router.post("/workspaces", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def api_create_workspace(
    payload: WorkspaceCreate,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> WorkspaceRead:
    bootstrap_ctx = context_from_request(request)
    event: AuditEvent | None = None
    with transaction(conn):
        created = create_workspace(bootstrap_ctx, conn, payload)
        workspace_ctx = bootstrap_ctx.with_workspace(created["id"])
        event = audit_writer.write(
            workspace_ctx,
            conn,
            action="workspace.created",
            payload={
                "workspace_id": created["id"],
                "name": created["name"],
                "slug": created["slug"],
            },
            mirror_jsonl=False,
        )

    if event is not None:
        audit_writer.mirror(event)
    return WorkspaceRead(**created)


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceRead)
def api_get_workspace(
    workspace_id: str,
    request: Request,
    conn: sqlite3.Connection = Depends(get_db),
) -> WorkspaceRead:
    ctx = context_from_request(request, workspace_id=workspace_id)
    workspace = get_workspace(ctx, conn)
    if workspace is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
    return WorkspaceRead(**workspace)
```

```python:app/src/main.py
from __future__ import annotations

import os
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .api import router as api_router
from .db import db_session, initialize_database
from .seed import seed_demo_workspace


APP_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = APP_DIR / "static"

# Entry point de la ventana desktop (pywebview) y del servidor local.
HOST = os.getenv("SPACELOOM_HOST", "127.0.0.1")
PORT = int(os.getenv("SPACELOOM_PORT", "8000"))
APP_URL = f"http://{HOST}:{PORT}/static/index.html"
HEALTH_URL = f"http://{HOST}:{PORT}/api/health"


def app_url(host: str = HOST, port: int = PORT) -> str:
    return f"http://{host}:{port}/static/index.html"


def health_url(host: str = HOST, port: int = PORT) -> str:
    return f"http://{host}:{port}/api/health"


@asynccontextmanager
async def lifespan(app: FastAPI):
    with db_session() as conn:
        initialize_database(conn)
        seed_demo_workspace(conn)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="SpaceLoom", version="0.1.0-sl0", lifespan=lifespan)
    app.include_router(api_router)

    @app.get("/", include_in_schema=False)
    def index():
        index_path = STATIC_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return HTMLResponse(
            """
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>SpaceLoom SL0</title>
                <style>
                  body {
                    margin: 0;
                    min-height: 100vh;
                    display: grid;
                    place-items: center;
                    background: #F4F1ED;
                    color: #1F1E1C;
                    font-family: Geist, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                  }
                  main {
                    width: min(680px, calc(100vw - 48px));
                    border: 1px solid #D8D0C0;
                    border-radius: 12px;
                    background: #FFFFFF;
                    padding: 32px;
                    box-shadow: 0 18px 60px rgba(31, 30, 28, 0.08);
                  }
                  .eyebrow {
                    color: #C96442;
                    font: 12px/1.4 "Geist Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
                    letter-spacing: 0.18em;
                    text-transform: uppercase;
                  }
                  h1 {
                    margin: 10px 0 12px;
                    font-family: "EB Garamond", Georgia, serif;
                    font-style: italic;
                    font-size: 44px;
                    font-weight: 500;
                    letter-spacing: -0.01em;
                  }
                  p { color: #5A544C; line-height: 1.6; margin: 0; }
                  code {
                    font-family: "Geist Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
                    color: #5A6B7C;
                  }
                </style>
              </head>
              <body>
                <main>
                  <div class="eyebrow">FaberLoom &middot; SpaceLoom</div>
                  <h1>SL0 skeleton is running.</h1>
                  <p>Local state is backed by SQLite. Check <code>/api/health</code> and <code>/api/workspaces</code>.</p>
                </main>
              </body>
            </html>
            """
        )

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    return app


app = create_app()


def _run_server(host: str = HOST, port: int = PORT) -> None:
    """Corre uvicorn en este proceso (se usa en un hilo daemon para el desktop)."""
    import uvicorn

    uvicorn.run(app, host=host, port=port, log_level="warning")


def _wait_until_ready(url: str = HEALTH_URL, timeout: float = 20.0) -> bool:
    """Sondea /api/health hasta que el servidor responda o se agote el tiempo."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(url, timeout=1.0) as resp:  # noqa: S310 (URL local fija)
                if resp.status == 200:
                    return True
        except (URLError, OSError):
            time.sleep(0.2)
    return False


def run_desktop(host: str = HOST, port: int = PORT) -> None:
    """Levanta el backend en un hilo y abre la ventana pywebview de SpaceLoom."""
    import webview

    server = threading.Thread(target=_run_server, args=(host, port), daemon=True)
    server.start()

    resolved_health_url = health_url(host, port)
    resolved_app_url = app_url(host, port)
    _wait_until_ready(resolved_health_url)

    webview.create_window(
        "SpaceLoom — FaberLoom",
        resolved_app_url,
        width=1320,
        height=860,
        min_size=(1000, 640),
        background_color="#F4F1ED",
    )
    webview.start()


def main() -> None:
    run_desktop()


if __name__ == "__main__":
    main()
```

```python:app/tests/test_sl0_backend.py
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.src.models import SCHEMA_VERSION


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "spaceloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SPACELOOM_DB_PATH", str(db_path))

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client, db_path, audit_path


def _columns(db_path: Path, table: str) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row[1] for row in rows}


def test_health_and_seed_workspace(client):
    test_client, _, _ = client

    health = test_client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["schema_version"] == SCHEMA_VERSION

    workspaces = test_client.get("/api/workspaces")
    assert workspaces.status_code == 200
    payload = workspaces.json()
    assert [workspace["slug"] for workspace in payload["workspaces"]].count("mwt-demo") == 1
    assert payload["workspaces"][0]["name"] == "MWT Demo"


def test_schema_contains_contract_tables_and_latent_fields(client):
    _, db_path, _ = client
    required_tables = {
        "workspace",
        "kb_source",
        "chat",
        "message",
        "draft",
        "audit_log",
        "routine",
        "routine_run",
    }
    latent_fields = {
        "tenant_id",
        "user_id",
        "actor_id",
        "actor_role_at_decision",
        "routine_version",
        "skill_version",
        "schema_version",
        "source_version",
        "approved_by",
    }

    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
    tables = {row[0] for row in rows}
    assert required_tables.issubset(tables)

    for table in required_tables:
        assert latent_fields.issubset(_columns(db_path, table)), table


def test_seed_is_idempotent(client):
    _, db_path, _ = client
    from app.src.db import connect, initialize_database
    from app.src.seed import seed_demo_workspace

    conn = connect()
    try:
        initialize_database(conn)
        first = seed_demo_workspace(conn)
        second = seed_demo_workspace(conn)
        count = conn.execute("SELECT COUNT(*) FROM workspace WHERE slug = ?", ("mwt-demo",)).fetchone()[0]
    finally:
        conn.close()

    assert first["id"] == second["id"]
    assert count == 1


def test_create_workspace_unique_slug_and_audit(client):
    test_client, db_path, audit_path = client

    first = test_client.post("/api/workspaces", json={"name": "Acme Client", "slug": "acme"})
    second = test_client.post("/api/workspaces", json={"name": "Acme Client", "slug": "acme"})

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["slug"] == "acme"
    assert second.json()["slug"] == "acme-2"

    with sqlite3.connect(db_path) as conn:
        action_count = conn.execute(
            "SELECT COUNT(*) FROM audit_log WHERE action = ?", ("workspace.created",)
        ).fetchone()[0]
    assert action_count == 2

    lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
    created_events = [json.loads(line) for line in lines if json.loads(line)["action"] == "workspace.created"]
    assert len(created_events) == 2


def test_workspace_name_rejects_blank(client):
    test_client, _, _ = client
    response = test_client.post("/api/workspaces", json={"name": "   "})
    assert response.status_code == 422


def test_context_tenant_scope_is_applied_to_workspace_reads(client):
    test_client, _, _ = client

    created = test_client.post(
        "/api/workspaces",
        headers={"x-tenant-id": "tenant-a"},
        json={"name": "Tenant A", "slug": "tenant-a"},
    )
    assert created.status_code == 201
    workspace_id = created.json()["id"]

    assert test_client.get(f"/api/workspaces/{workspace_id}").status_code == 404
    assert (
        test_client.get(f"/api/workspaces/{workspace_id}", headers={"x-tenant-id": "tenant-b"}).status_code
        == 404
    )

    visible = test_client.get(
        f"/api/workspaces/{workspace_id}", headers={"x-tenant-id": "tenant-a"}
    )
    assert visible.status_code == 200
    assert visible.json()["slug"] == "tenant-a"
```

```markdown:docs/contracts/latent_fields_matrix.md
# Latent fields matrix — SpaceLoom SL0

This matrix makes the contract-first seam explicit for SL0. The app remains
single-user/local-first, but every durable application table exposes the latent
fields needed to move to managed keys, routines, stronger HITL, and future
multi-tenant storage without a model rewrite.

| Table | tenant_id | user_id | actor_id | actor_role_at_decision | routine_version | skill_version | schema_version | source_version | approved_by |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `workspace` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `kb_source` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `chat` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `message` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `draft` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `audit_log` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `routine` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `routine_run` | yes | yes | yes | yes | yes | yes | yes | yes | yes |

Notes:

- `tenant_id` is nullable in SL0. `NULL` means the default local single-user
  tenant; it is still always part of the schema and query seam.
- `actor_id` / `actor_role_at_decision` capture who made or approved a decision
  without requiring a real identity provider in SL0.
- `routine_version` and `skill_version` are nullable until SL3a introduces the
  Routine Hub and portable `SKILL.md` compiler.
- `schema_version` stores the application schema contract version that produced
  the row.
- `source_version` is nullable where a row is not derived from an external KB
  source yet; SL2 will make it required for hard facts.
- `approved_by` stays nullable until HITL approval flows exist; irreversible
  actions are not implemented in SL0.
```

```toml:app/pyproject.toml
[project]
name = "spaceloom"
version = "0.1.0"
description = "FaberLoom SpaceLoom local-first desktop app"
requires-python = ">=3.13"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.30.0",
  "pywebview>=5.0",
  "jinja2>=3.1.0",
  "aiofiles>=24.1.0",
  "pydantic>=2.8.0",
]

[project.optional-dependencies]
test = [
  "httpx>=0.27.0",
  "pytest>=8.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = [".."]

[tool.uvicorn]
factory = false
```