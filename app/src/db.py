"""SQLite initialization, migrations, and SL0 data access helpers.

Raw sqlite3 keeps SL0 small and local-first. Versioned migrations are tracked in
_schema_version. Every application data query takes a Context. Bootstrap queries
are explicitly named ``system_*``; workspace-owned reads must constrain by
``ctx.workspace_id``.
"""

from __future__ import annotations

import difflib
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

from .context import SYSTEM_WORKSPACE_ID, Context, enforce_tenant_scoped
from .db_adapter import (
    connect as adapter_connect,
    db_session as adapter_db_session,
    is_postgres_connection,
    normalize_sql,
    row_to_dict as adapter_row_to_dict,
    transaction as adapter_transaction,
)
from .models import MIGRATIONS, SCHEMA_VERSION, RoutineCreate, WorkspaceCreate
from .plans import enforce_budget, enforce_workspace_creation
from .router import cost as router_cost
from .router.config_store import decrypt_value, encrypt_value

try:
    import sqlcipher3
except Exception:  # pragma: no cover - runtime environment may lack sqlcipher3
    sqlcipher3 = None  # type: ignore[assignment]
from .seal import (
    assert_workspace_hmac_for_row,
    compute_workspace_hmac_for_row,
    verify_workspace_hmac_for_row,
)


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"


def _user_data_base() -> Path:
    """Return the base user data directory, honoring explicit overrides first."""

    env = os.environ.get("FABERLOOM_DATA_DIR") or os.environ.get("LOCALAPPDATA")
    if env:
        return Path(env)
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return Path.home() / ".local" / "share"


def _migrate_legacy_data_dir() -> None:
    """One-time migration: SpaceLoom -> FaberLoom user data directory.

    If the old ``SpaceLoom`` directory exists and ``FaberLoom`` does not, rename
    the directory and the legacy ``spaceloom.sqlite3`` database file. This keeps
    existing dogfood user data intact after the rebrand.
    """

    base = _user_data_base()
    old = base / "SpaceLoom"
    new = base / "FaberLoom"
    if old.exists() and not new.exists():
        old.rename(new)
        old_db = new / "spaceloom.sqlite3"
        new_db = new / "faberloom.sqlite3"
        if old_db.exists() and not new_db.exists():
            old_db.rename(new_db)


def _default_user_data_dir() -> Path:
    """Return the OS-appropriate user data directory for FaberLoom."""

    _migrate_legacy_data_dir()
    return _user_data_base() / "FaberLoom"


DEFAULT_DB_PATH = _default_user_data_dir() / "faberloom.sqlite3"

WORKSPACE_COLUMNS = """
    id,
    name,
    slug,
    seal_id,
    field_aliases_json,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    parent_id,
    inherits_kb,
    confidential,
    email_signature,
    is_canary,
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


def row_to_dict(row: Any) -> dict[str, Any]:
    return adapter_row_to_dict(row)


def get_database_path() -> Path:
    configured = os.getenv("FABERLOOM_DB_PATH")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DB_PATH


def connect() -> Any:
    """Return a database connection for the configured engine (SQLite default)."""

    return adapter_connect()


def get_workspace_database_path(
    workspace_id: str,
    main_path: Path | None = None,
) -> Path:
    """Return the SQLCipher database path for a confidential workspace."""

    main_path = main_path or get_database_path()
    return main_path.with_name(f"{main_path.stem}-conf-{workspace_id}.sqlite3")


def connect_workspace_data_db(
    workspace_id: str,
    passphrase: str,
    main_path: Path | None = None,
) -> sqlite3.Connection:
    """Open the per-workspace SQLCipher database used for confidential workspaces.

    The database is created and migrated on first open. The *workspace* table is
    mirrored so that the same repository helpers work unchanged.
    """

    if sqlcipher3 is None:
        raise RuntimeError("sqlcipher3 is not available; cannot open confidential workspace")

    db_path = get_workspace_database_path(workspace_id, main_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    existed = db_path.exists()
    conn = sqlcipher3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlcipher3.Row
    # Set the encryption key BEFORE any other PRAGMA or SQL statement.
    escaped = passphrase.replace("'", "''")
    conn.execute(f"PRAGMA key = '{escaped}'")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")

    if not existed:
        initialize_database(conn)
    return conn


def _mirror_workspace_to_data_db(
    main_conn: sqlite3.Connection,
    data_conn: sqlite3.Connection,
    workspace_id: str,
) -> None:
    """Copy a workspace row from the main DB into its confidential data DB."""

    row = main_conn.execute(
        "SELECT * FROM workspace WHERE id = ?",
        (workspace_id,),
    ).fetchone()
    if row is None:
        raise RuntimeError("Workspace row missing during confidential mirror")
    # Do not mirror the parent_id foreign key (the parent lives in the main DB)
    # or the plaintext passphrase into the confidential data DB.
    columns = [k for k in row.keys() if k not in {"parent_id", "passphrase"}]
    data_conn.execute("DELETE FROM workspace WHERE id = ?", (workspace_id,))
    data_conn.execute(
        f"""
        INSERT INTO workspace ({','.join(columns)})
        VALUES ({','.join('?' for _ in columns)})
        """,
        tuple(row[c] for c in columns),
    )


def get_db() -> Iterator[Any]:
    """FastAPI dependency yielding a configured database connection."""

    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def db_session() -> Iterator[Any]:
    """Yield a configured database connection and close it at the end."""

    with adapter_db_session() as conn:
        yield conn


@contextmanager
def transaction(conn: Any, ctx: Context | None = None) -> Iterator[None]:
    """Commit/rollback a unit of work unless already inside a transaction.

    When *ctx* is provided and the engine is Postgres, the connection variables
    used by RLS policies are set via ``SET LOCAL`` at the start of the
    transaction. This is the only place where tenant/workspace flow into the
    database connection; they never come from headers.
    """

    with adapter_transaction(conn, ctx=ctx):
        yield


def recompute_all_workspace_hmacs(conn: sqlite3.Connection) -> None:
    """Recompute content-aware workspace HMACs for every sealed row.

    Called automatically after migrations so legacy row-id-only seals are
    upgraded to tamper-evident signatures that cover the protected columns.
    """

    seals = {
        row["id"]: row["seal_id"]
        for row in conn.execute("SELECT id, seal_id FROM workspace").fetchall()
    }
    sealed_tables = ("kb_source", "kb_fact", "draft", "routine_run")
    for table_name in sealed_tables:
        for row in conn.execute(f"SELECT * FROM {table_name}").fetchall():
            workspace_id = row["workspace_id"]
            seal_id = seals.get(workspace_id)
            if seal_id is None:
                continue
            new_hmac = compute_workspace_hmac_for_row(
                seal_id, row_to_dict(row), table_name
            )
            conn.execute(
                f"UPDATE {table_name} SET workspace_hmac = ? WHERE id = ?",
                (new_hmac, row["id"]),
            )


def _migrate_v22_correlation_id(conn: sqlite3.Connection) -> None:
    """Idempotently add correlation_id to audit_log for E2-0.

    The v1 schema base already includes the column for new databases; this
    hook ensures existing databases receive the column without failing on
    duplicate-column errors.
    """

    row = conn.execute(
        "SELECT 1 FROM pragma_table_info('audit_log') WHERE name = ?",
        ("correlation_id",),
    ).fetchone()
    if row is None:
        conn.execute("ALTER TABLE audit_log ADD COLUMN correlation_id TEXT;")


def _migrate_v19_data(conn: sqlite3.Connection) -> None:
    """Backfill per-user data for the v19 schema change.

    Reads FABERLOOM_USERS as JSON to determine the default owner for existing
    shared rows. Existing SMTP config rows and unowned chats/messages are
    assigned to the first configured user (or "local" in unauthenticated mode).
    Chats are then duplicated for every additional configured user so each one
    starts with an independent history. usage_record rows are intentionally left
    pointing at the original chats.
    """

    users: list[str] = []
    raw_users = os.getenv("FABERLOOM_USERS", "")
    if raw_users:
        try:
            parsed = json.loads(raw_users)
            if isinstance(parsed, dict):
                users = [str(k) for k in parsed.keys()]
        except Exception:
            pass
    first_user = users[0] if users else "local"

    # Migrate SMTP config: assign existing workspace configs to the first user.
    smtp_rows = conn.execute(
        "SELECT workspace_id, host, port, use_ssl, username, password, from_email, created_at, updated_at "
        "FROM _workspace_smtp_config_v18"
    ).fetchall()
    for row in smtp_rows:
        conn.execute(
            """
            INSERT INTO workspace_smtp_config (
                workspace_id, user_id, host, port, use_ssl, username, password, from_email,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["workspace_id"],
                first_user,
                row["host"],
                row["port"],
                row["use_ssl"],
                row["username"],
                row["password"],
                row["from_email"],
                row["created_at"],
                row["updated_at"],
            ),
        )
    conn.execute("DROP TABLE _workspace_smtp_config_v18")

    # Claim any unowned chats/messages for the first user.
    conn.execute(
        "UPDATE chat SET user_id = ? WHERE user_id IS NULL",
        (first_user,),
    )
    conn.execute(
        "UPDATE message SET user_id = ? WHERE user_id IS NULL",
        (first_user,),
    )

    # Duplicate shared chats (and their messages) for every additional user.
    for additional_user in users[1:]:
        chats = conn.execute(
            "SELECT * FROM chat WHERE user_id = ?", (first_user,)
        ).fetchall()
        for chat in chats:
            new_chat_id = new_id("chat")
            conn.execute(
                """
                INSERT INTO chat (
                    id, workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision,
                    title, model_preset, routine_version, skill_version, schema_version,
                    source_version, approved_by, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_chat_id,
                    chat["workspace_id"],
                    chat["tenant_id"],
                    additional_user,
                    additional_user,
                    chat["actor_role_at_decision"],
                    chat["title"],
                    chat["model_preset"],
                    chat["routine_version"],
                    chat["skill_version"],
                    chat["schema_version"],
                    chat["source_version"],
                    chat["approved_by"],
                    chat["created_at"],
                ),
            )
            messages = conn.execute(
                "SELECT * FROM message WHERE chat_id = ?", (chat["id"],)
            ).fetchall()
            for msg in messages:
                new_message_id = new_id("msg")
                conn.execute(
                    """
                    INSERT INTO message (
                        id, chat_id, workspace_id, tenant_id, user_id, actor_id,
                        actor_role_at_decision, role, content_json, routine_version,
                        skill_version, schema_version, source_version, approved_by, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        new_message_id,
                        new_chat_id,
                        msg["workspace_id"],
                        msg["tenant_id"],
                        additional_user,
                        additional_user,
                        msg["actor_role_at_decision"],
                        msg["role"],
                        msg["content_json"],
                        msg["routine_version"],
                        msg["skill_version"],
                        msg["schema_version"],
                        msg["source_version"],
                        msg["approved_by"],
                        msg["created_at"],
                    ),
                )


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
            if version == 22:
                _migrate_v22_correlation_id(conn)
            migration_sql = MIGRATIONS[version]
            if is_postgres_connection(conn):
                # SQLite trigger syntax (BEGIN...END) is not valid in Postgres.
                # RLS already enforces tenant isolation; skip trigger creation.
                migration_sql = re.sub(
                    r"CREATE\s+TRIGGER\s+IF\s+NOT\s+EXISTS\s+.*?(?=\nCREATE|\Z)",
                    "",
                    migration_sql,
                    flags=re.IGNORECASE | re.DOTALL,
                )
            conn.executescript(migration_sql)
            conn.execute(
                "INSERT INTO _schema_version(version, applied_at) VALUES (?, ?)",
                (version, utc_now()),
            )
            if version == 19:
                _migrate_v19_data(conn)
        recompute_all_workspace_hmacs(conn)
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
    with transaction(conn, ctx=ctx):
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
    with transaction(conn, ctx=ctx):
        rows = conn.execute(
            f"""
            SELECT {WORKSPACE_COLUMNS}
            FROM workspace
            WHERE tenant_id = ?
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
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            f"""
            SELECT {WORKSPACE_COLUMNS}
            FROM workspace
            WHERE id = ? AND tenant_id = ?
            """,
            (workspace_id, ctx.tenant_id),
        ).fetchone()
    return row_to_dict(row) if row else None


def workspace_seal_id(ctx: Context, conn: sqlite3.Connection) -> str:
    """Return the workspace seal_id for the current scoped context."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            "SELECT seal_id FROM workspace WHERE id = ? AND tenant_id = ?",
            (workspace_id, ctx.tenant_id),
        ).fetchone()
        if row is None or row["seal_id"] is None:
            raise PermissionError("Workspace seal not available")
        return row["seal_id"]


def system_get_workspace(
    ctx: Context,
    conn: sqlite3.Connection,
    workspace_id: str,
) -> dict[str, Any] | None:
    """Bootstrap-only lookup used by seed/tests; not for workspace-owned data."""

    ctx.require_system()
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            f"""
            SELECT {WORKSPACE_COLUMNS}
            FROM workspace
            WHERE id = ? AND tenant_id = ?
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
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            f"""
            SELECT {WORKSPACE_COLUMNS}
            FROM workspace
            WHERE slug = ? AND tenant_id = ?
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

    with transaction(conn, ctx=ctx):
        ctx.require_system()
        enforce_workspace_creation(ctx, conn)
        now = utc_now()
        workspace_id = new_id("ws")
        name = payload.name.strip()
        slug = unique_workspace_slug(ctx, conn, payload.slug or name)
        seal_id = uuid.uuid4().hex

        parent_id = payload.parent_id
        inherits_kb = payload.inherits_kb
        confidential = getattr(payload, "confidential", 0) or 0
        if parent_id:
            parent = conn.execute(
                "SELECT id, tenant_id FROM workspace WHERE id = ?",
                (parent_id,),
            ).fetchone()
            if parent is None:
                raise ValueError(f"Parent workspace {parent_id} not found")
            if parent["tenant_id"] != ctx.tenant_id:
                raise ValueError("Parent workspace belongs to a different tenant")

        conn.execute(
            """
            INSERT INTO workspace(
                id,
                name,
                slug,
                seal_id,
                field_aliases_json,
                tenant_id,
                user_id,
                actor_id,
                actor_role_at_decision,
                routine_version,
                skill_version,
                schema_version,
                source_version,
                approved_by,
                parent_id,
                inherits_kb,
                confidential,
                email_signature,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                workspace_id,
                name,
                slug,
                seal_id,
                '{}',
                ctx.tenant_id,
                ctx.user_id,
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                None,
                None,
                SCHEMA_VERSION,
                None,
                None,
                parent_id,
                inherits_kb,
                confidential,
                None,
                now,
                now,
            ),
        )
        created = system_get_workspace(ctx, conn, workspace_id)
        if created is None:
            raise RuntimeError("Workspace was created but could not be read back")
        return created


# -----------------------------------------------------------------------------
# E2-4: Workspace routing policy and model catalog
# -----------------------------------------------------------------------------


def get_routing_policy(
    ctx: Context,
    conn: sqlite3.Connection,
    workspace_id: str | None = None,
) -> dict[str, Any]:
    """Return the routing policy for a workspace, creating a default row if absent."""

    with transaction(conn, ctx=ctx):
        ws_id = workspace_id or ctx.require_scoped_workspace()
        row = conn.execute(
            f"""
            SELECT {WORKSPACE_ROUTING_POLICY_COLUMNS}
            FROM workspace_routing_policy
            WHERE workspace_id = ? AND tenant_id = ?
            """,
            (ws_id, ctx.require_tenant()),
        ).fetchone()
        if row is None:
            now = utc_now()
            conn.execute(
                f"""
                INSERT INTO workspace_routing_policy (
                    workspace_id, tenant_id, provider_allowlist_json, model_allowlist_json,
                    budget_cap_usd, auto_mode_enabled, max_auto_steps, require_local_only, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (ws_id, ctx.require_tenant(), "[]", "{}", 5.0, 0, 3, 0, now),
            )
            row = conn.execute(
                f"""
                SELECT {WORKSPACE_ROUTING_POLICY_COLUMNS}
                FROM workspace_routing_policy
                WHERE workspace_id = ? AND tenant_id = ?
                """,
                (ws_id, ctx.require_tenant()),
            ).fetchone()
        data = row_to_dict(row)
        data["provider_allowlist"] = json.loads(data.get("provider_allowlist_json") or "[]")
        data["model_allowlist"] = json.loads(data.get("model_allowlist_json") or "{}")
        return data


def update_routing_policy(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    provider_allowlist: list[str] | None = None,
    model_allowlist: dict[str, list[str]] | None = None,
    budget_cap_usd: float | None = None,
    user_budget_cap_usd: float | None = None,
    auto_mode_enabled: bool | None = None,
    max_auto_steps: int | None = None,
    require_local_only: bool | None = None,
) -> dict[str, Any]:
    """Update the routing policy for the current scoped workspace."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        policy = get_routing_policy(ctx, conn, workspace_id)
        updates: dict[str, Any] = {"updated_at": utc_now()}
        if provider_allowlist is not None:
            updates["provider_allowlist_json"] = json.dumps(provider_allowlist, ensure_ascii=False)
        if model_allowlist is not None:
            updates["model_allowlist_json"] = json.dumps(model_allowlist, ensure_ascii=False)
        if budget_cap_usd is not None:
            updates["budget_cap_usd"] = budget_cap_usd
        if user_budget_cap_usd is not None:
            updates["user_budget_cap_usd"] = user_budget_cap_usd
        if auto_mode_enabled is not None:
            updates["auto_mode_enabled"] = 1 if auto_mode_enabled else 0
        if max_auto_steps is not None:
            updates["max_auto_steps"] = max_auto_steps
        if require_local_only is not None:
            updates["require_local_only"] = 1 if require_local_only else 0

        if not updates:
            return policy

        cols = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"UPDATE workspace_routing_policy SET {cols} WHERE workspace_id = ? AND tenant_id = ?",
            (*updates.values(), workspace_id, ctx.require_tenant()),
        )
        return get_routing_policy(ctx, conn, workspace_id)


def list_model_catalog(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    capability: str | None = None,
    local_only: bool = False,
    enabled_only: bool = True,
) -> list[dict[str, Any]]:
    """List model catalog entries for the current scoped workspace."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        query = f"""
            SELECT {WORKSPACE_MODEL_CATALOG_COLUMNS}
            FROM workspace_model_catalog
            WHERE workspace_id = ? AND tenant_id = ?
        """
        params: list[Any] = [workspace_id, ctx.require_tenant()]
        if enabled_only:
            query += " AND is_enabled = 1"
        if local_only:
            query += " AND is_local = 1"
        if capability:
            query += " AND capabilities_json LIKE ?"
            params.append(f'%"{capability}"%')
        query += " ORDER BY priority ASC, provider_slug ASC, model ASC"
        rows = conn.execute(query, params).fetchall()
        return [_model_catalog_row_to_dict(row) for row in rows]


def get_model_catalog_entry(
    ctx: Context,
    conn: sqlite3.Connection,
    entry_id: str,
) -> dict[str, Any] | None:
    """Return a single catalog entry if it belongs to the current workspace/tenant."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            f"""
            SELECT {WORKSPACE_MODEL_CATALOG_COLUMNS}
            FROM workspace_model_catalog
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (entry_id, workspace_id, ctx.require_tenant()),
        ).fetchone()
        return _model_catalog_row_to_dict(row) if row else None


def create_model_catalog_entry(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    provider_slug: str,
    model: str,
    capabilities: list[str],
    priority: int = 100,
    cost_input_1k: float = 0.0,
    cost_output_1k: float = 0.0,
    is_local: bool = False,
    is_managed: bool = False,
    is_enabled: bool = True,
) -> dict[str, Any]:
    """Insert a model catalog entry for the current scoped workspace."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        entry_id = new_id("mce")
        now = utc_now()
        conn.execute(
            f"""
            INSERT INTO workspace_model_catalog (
                id, workspace_id, tenant_id, provider_slug, model, capabilities_json,
                is_enabled, priority, cost_input_1k, cost_output_1k, is_local, is_managed,
                source_version, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry_id,
                workspace_id,
                ctx.require_tenant(),
                provider_slug,
                model,
                json.dumps(capabilities, ensure_ascii=False),
                1 if is_enabled else 0,
                priority,
                cost_input_1k,
                cost_output_1k,
                1 if is_local else 0,
                1 if is_managed else 0,
                router_cost.PRICING_VERSION,
                now,
            ),
        )
        row = conn.execute(
            f"""
            SELECT {WORKSPACE_MODEL_CATALOG_COLUMNS}
            FROM workspace_model_catalog
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (entry_id, workspace_id, ctx.require_tenant()),
        ).fetchone()
        assert row is not None
        return _model_catalog_row_to_dict(row)


def update_model_catalog_entry(
    ctx: Context,
    conn: sqlite3.Connection,
    entry_id: str,
    *,
    capabilities: list[str] | None = None,
    priority: int | None = None,
    cost_input_1k: float | None = None,
    cost_output_1k: float | None = None,
    is_local: bool | None = None,
    is_managed: bool | None = None,
    is_enabled: bool | None = None,
) -> dict[str, Any] | None:
    """Update a model catalog entry. Returns None if not found or not owned."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        updates: dict[str, Any] = {}
        if capabilities is not None:
            updates["capabilities_json"] = json.dumps(capabilities, ensure_ascii=False)
        if priority is not None:
            updates["priority"] = priority
        if cost_input_1k is not None:
            updates["cost_input_1k"] = cost_input_1k
        if cost_output_1k is not None:
            updates["cost_output_1k"] = cost_output_1k
        if is_local is not None:
            updates["is_local"] = 1 if is_local else 0
        if is_managed is not None:
            updates["is_managed"] = 1 if is_managed else 0
        if is_enabled is not None:
            updates["is_enabled"] = 1 if is_enabled else 0

        if not updates:
            return get_model_catalog_entry(ctx, conn, entry_id)

        cols = ", ".join(f"{k} = ?" for k in updates)
        cursor = conn.execute(
            f"""
            UPDATE workspace_model_catalog
            SET {cols}
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (*updates.values(), entry_id, workspace_id, ctx.require_tenant()),
        )
        if cursor.rowcount == 0:
            return None
        return get_model_catalog_entry(ctx, conn, entry_id)


def delete_model_catalog_entry(
    ctx: Context,
    conn: sqlite3.Connection,
    entry_id: str,
) -> bool:
    """Delete a model catalog entry. Returns True if deleted."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        cursor = conn.execute(
            "DELETE FROM workspace_model_catalog WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (entry_id, workspace_id, ctx.require_tenant()),
        )
        return cursor.rowcount > 0


def _model_catalog_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    data = row_to_dict(row)
    caps = data.get("capabilities_json") or '["text"]'
    try:
        data["capabilities"] = json.loads(caps)
    except Exception:
        data["capabilities"] = ["text"]
    data.pop("capabilities_json", None)
    return data


def get_workspace_field_aliases(
    ctx: Context,
    conn: sqlite3.Connection,
) -> dict[str, list[str]]:
    """Return the workspace field alias map (workspace-scoped)."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            "SELECT field_aliases_json FROM workspace WHERE id = ? AND tenant_id = ?",
            (workspace_id, ctx.tenant_id),
        ).fetchone()
        if row is None or row["field_aliases_json"] is None:
            return {}
        try:
            data = json.loads(row["field_aliases_json"])
        except json.JSONDecodeError:
            return {}
        if not isinstance(data, dict):
            return {}
        return {k: v for k, v in data.items() if isinstance(v, list)}


def update_workspace_field_aliases(
    ctx: Context,
    conn: sqlite3.Connection,
    aliases: dict[str, list[str]],
) -> dict[str, Any] | None:
    """Replace the workspace field alias map (workspace-scoped)."""

    workspace_id = ctx.require_scoped_workspace()
    with transaction(conn, ctx=ctx):
        cursor = conn.execute(
            """
            UPDATE workspace
            SET field_aliases_json = ?, updated_at = ?
            WHERE id = ? AND tenant_id = ?
            """,
            (json.dumps(aliases, ensure_ascii=False, sort_keys=True), utc_now(), workspace_id, ctx.tenant_id),
        )
        if cursor.rowcount == 0:
            return None
    return get_workspace(ctx, conn)


EDITORIAL_HISTORY_COLUMNS = """
    id,
    workspace_id,
    entity_type,
    entity_id,
    action,
    actor_id,
    reason,
    payload_json,
    created_at
"""


def record_editorial_event(
    ctx: Context,
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: str,
    action: str,
    reason: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Record an editorial decision (approve/reject/apply) for an entity."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        event_id = new_id("ed")
        now = utc_now()
        payload_value = payload if payload is not None else {}
        conn.execute(
            """
            INSERT INTO editorial_history (
                id, workspace_id, tenant_id, entity_type, entity_id, action, actor_id, reason, payload_json, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                workspace_id,
                ctx.require_tenant(),
                entity_type,
                entity_id,
                action,
                ctx.resolved_actor_id(),
                reason,
                json.dumps(payload_value, ensure_ascii=False, sort_keys=True),
                now,
            ),
        )
        return {
            "id": event_id,
            "workspace_id": workspace_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "actor_id": ctx.resolved_actor_id(),
            "reason": reason,
            "payload": payload_value,
            "created_at": now,
        }


def list_editorial_history(
    ctx: Context,
    conn: sqlite3.Connection,
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List editorial history events scoped to the current workspace."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        sql = f"""
            SELECT {EDITORIAL_HISTORY_COLUMNS}
            FROM editorial_history
            WHERE workspace_id = ? AND tenant_id = ?
        """
        params: list[Any] = [workspace_id, ctx.require_tenant()]
        if entity_type is not None:
            sql += " AND entity_type = ?"
            params.append(entity_type)
        if entity_id is not None:
            sql += " AND entity_id = ?"
            params.append(entity_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(sql, params).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            item = row_to_dict(row)
            try:
                item["payload"] = json.loads(item.get("payload_json") or "{}")
            except json.JSONDecodeError:
                item["payload"] = {}
            item.pop("payload_json", None)
            results.append(item)
        return results


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
    correlation_id: str | None = None,
    created_at: str | None = None,
    system_event: bool = False,
) -> None:
    """Insert an audit event row.

    This helper intentionally does not commit; callers decide transaction scope.
    When ``system_event`` is True the workspace may be the system scope (used for
    tenant-level lifecycle events such as identity or key-policy mutations).
    """

    with transaction(conn, ctx=ctx):
        if not system_event:
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
                correlation_id,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                correlation_id,
                created_at or utc_now(),
            ),
        )


# -----------------------------------------------------------------------------
# SL1a: Chat data access helpers
# -----------------------------------------------------------------------------

CHAT_COLUMNS = """
    id,
    workspace_id,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    title,
    model_preset,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    created_at
"""

MESSAGE_COLUMNS = """
    id,
    chat_id,
    workspace_id,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    role,
    content_json,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    created_at
"""

USAGE_RECORD_COLUMNS = """
    id,
    workspace_id,
    chat_id,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    provider_slug,
    model,
    input_tokens,
    output_tokens,
    cost_usd,
    duration_ms,
    status,
    error,
    attempts_json,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    run_id,
    step_index,
    chain_id,
    capability,
    platform_key_used,
    platform_key_surcharge_usd,
    byo_mode_at_run,
    created_at
"""

WORKSPACE_ROUTING_POLICY_COLUMNS = """
    workspace_id,
    tenant_id,
    provider_allowlist_json,
    model_allowlist_json,
    budget_cap_usd,
    user_budget_cap_usd,
    auto_mode_enabled,
    max_auto_steps,
    require_local_only,
    updated_at
"""

WORKSPACE_MODEL_CATALOG_COLUMNS = """
    id,
    workspace_id,
    tenant_id,
    provider_slug,
    model,
    capabilities_json,
    is_enabled,
    priority,
    cost_input_1k,
    cost_output_1k,
    is_local,
    is_managed,
    source_version,
    created_at
"""

ROUTING_PRESET_COLUMNS = """
    tenant_id,
    preset_id,
    name,
    version,
    description,
    envelope_json,
    curve_json,
    task_overrides_json,
    caps_json,
    escalation_json,
    is_active,
    is_template,
    created_by,
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


def _routing_preset_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    data = row_to_dict(row)
    for key in (
        "envelope_json",
        "curve_json",
        "task_overrides_json",
        "caps_json",
        "escalation_json",
    ):
        try:
            data[key.replace("_json", "")] = json.loads(data.get(key) or "{}")
        except Exception:
            data[key.replace("_json", "")] = {}
        data.pop(key, None)
    data["is_active"] = bool(data.get("is_active", 1))
    data["is_template"] = bool(data.get("is_template", 0))
    return data


def _chat_user_id(ctx: Context) -> str:
    """Return the user_id value to use for chat/message filters.

    Local/test mode uses the sentinel ``"local"`` value so existing tests keep
    working without JWT tokens.
    """

    return ctx.user_id or "local"


def create_chat(
    ctx: Context,
    conn: sqlite3.Connection,
    title: str,
) -> dict[str, Any]:
    """Insert a chat scoped to the current workspace and user."""

    with transaction(conn, ctx=ctx):
        enforce_tenant_scoped(ctx)
        workspace_id = ctx.require_scoped_workspace()
        chat_id = new_id("chat")
        now = utc_now()
        user_id = _chat_user_id(ctx)

        conn.execute(
            f"""
            INSERT INTO chat (
                id,
                workspace_id,
                tenant_id,
                user_id,
                actor_id,
                actor_role_at_decision,
                title,
                model_preset,
                routine_version,
                skill_version,
                schema_version,
                source_version,
                approved_by,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chat_id,
                workspace_id,
                ctx.tenant_id,
                user_id,
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                title.strip(),
                "default",
                None,
                None,
                SCHEMA_VERSION,
                None,
                None,
                now,
            ),
        )
        row = conn.execute(
            f"SELECT {CHAT_COLUMNS} FROM chat WHERE id = ? AND workspace_id = ? AND tenant_id = ? AND user_id = ?",
            (chat_id, workspace_id, ctx.tenant_id, user_id),
        ).fetchone()
        assert row is not None
        return row_to_dict(row)


def list_chats(ctx: Context, conn: sqlite3.Connection) -> list[dict[str, Any]]:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        user_id = _chat_user_id(ctx)
        rows = conn.execute(
            f"""
            SELECT {CHAT_COLUMNS}
            FROM chat
            WHERE workspace_id = ? AND tenant_id = ? AND user_id = ?
            ORDER BY created_at DESC
            """,
            (workspace_id, ctx.tenant_id, user_id),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def get_chat(
    ctx: Context,
    conn: sqlite3.Connection,
    chat_id: str,
) -> dict[str, Any] | None:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        user_id = _chat_user_id(ctx)
        row = conn.execute(
            f"""
            SELECT {CHAT_COLUMNS}
            FROM chat
            WHERE id = ? AND workspace_id = ? AND tenant_id = ? AND user_id = ?
            """,
            (chat_id, workspace_id, ctx.tenant_id, user_id),
        ).fetchone()
        return row_to_dict(row) if row else None


def update_chat(
    ctx: Context,
    conn: sqlite3.Connection,
    chat_id: str,
    title: str,
) -> dict[str, Any] | None:
    """Rename a chat. Returns the updated row or None if not found/scoped."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        user_id = _chat_user_id(ctx)
        cursor = conn.execute(
            """
            UPDATE chat
            SET title = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ? AND user_id = ?
            """,
            (title.strip(), chat_id, workspace_id, ctx.tenant_id, user_id),
        )
        if cursor.rowcount == 0:
            return None
        return get_chat(ctx, conn, chat_id)


def delete_chat(
    ctx: Context,
    conn: sqlite3.Connection,
    chat_id: str,
) -> bool:
    """Delete a chat and its messages (cascade), scoped to workspace/tenant/user.

    Leaves usage records with a dangling chat_id; callers may clean them up.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        user_id = _chat_user_id(ctx)
        conn.execute(
            "UPDATE usage_record SET chat_id = NULL WHERE chat_id = ? AND workspace_id = ? AND tenant_id = ?",
            (chat_id, workspace_id, ctx.require_tenant()),
        )
        cursor = conn.execute(
            "DELETE FROM chat WHERE id = ? AND workspace_id = ? AND tenant_id = ? AND user_id = ?",
            (chat_id, workspace_id, ctx.tenant_id, user_id),
        )
        return cursor.rowcount > 0


def insert_message(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    chat_id: str,
    role: str,
    content: str,
    route: dict[str, Any] | None = None,
    routine_version: str | None = None,
    skill_version: str | None = None,
    source_version: str | None = None,
    approved_by: str | None = None,
) -> dict[str, Any]:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        if get_chat(ctx, conn, chat_id) is None:
            raise ValueError("Chat not found in current Context")
        message_id = new_id("msg")
        now = utc_now()
        user_id = _chat_user_id(ctx)

        content_json: dict[str, Any] = {"content": content}
        if route:
            content_json["route"] = route

        conn.execute(
            f"""
            INSERT INTO message (
                id,
                chat_id,
                workspace_id,
                tenant_id,
                user_id,
                actor_id,
                actor_role_at_decision,
                role,
                content_json,
                routine_version,
                skill_version,
                schema_version,
                source_version,
                approved_by,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                chat_id,
                workspace_id,
                ctx.tenant_id,
                user_id,
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                role,
                json.dumps(content_json, ensure_ascii=False),
                routine_version,
                skill_version,
                SCHEMA_VERSION,
                source_version,
                approved_by,
                now,
            ),
        )
        row = conn.execute(
            f"""
            SELECT {MESSAGE_COLUMNS}
            FROM message
            WHERE id = ? AND workspace_id = ? AND tenant_id = ? AND user_id = ?
            """,
            (message_id, workspace_id, ctx.tenant_id, user_id),
        ).fetchone()
        assert row is not None
        return row_to_dict(row)


def get_messages(
    ctx: Context,
    conn: sqlite3.Connection,
    chat_id: str,
) -> list[dict[str, Any]]:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        user_id = _chat_user_id(ctx)
        rows = conn.execute(
            f"""
            SELECT {MESSAGE_COLUMNS}
            FROM message
            WHERE chat_id = ? AND workspace_id = ? AND tenant_id = ? AND user_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (chat_id, workspace_id, ctx.tenant_id, user_id),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def _message_content(row: dict[str, Any]) -> str:
    try:
        payload = json.loads(row["content_json"] or "{}")
    except json.JSONDecodeError:
        payload = {}
    return payload.get("content", "") if isinstance(payload, dict) else ""


def get_message_history(
    ctx: Context,
    conn: sqlite3.Connection,
    chat_id: str,
) -> list[dict[str, str]]:
    """Return provider-compatible message history."""

    messages = get_messages(ctx, conn, chat_id)
    return [
        {"role": row["role"], "content": _message_content(row)}
        for row in messages
        if row["role"] in {"system", "user", "assistant"}
    ]


def insert_usage_record(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    chat_id: str | None,
    provider_slug: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float,
    duration_ms: int,
    status: str,
    error: str | None,
    attempts_json: list[dict[str, Any]],
    request_json: dict[str, Any],
    response_json: dict[str, Any],
    source_version: str | None = router_cost.PRICING_VERSION,
    run_id: str | None = None,
    step_index: int | None = None,
    chain_id: str | None = None,
    capability: str | None = None,
    key_origin: str | None = None,
) -> dict[str, Any]:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        enforce_budget(ctx, conn, cost_usd)

        from .config_cascade import resolve as cascade_resolve
        from .context import DEFAULT_TENANT_ID
        from .plans import get_plan_surcharge_pct

        byo_mode = cascade_resolve(conn, ctx, "routing.byo_mode", default="hibrido")
        platform_key_used = 1 if key_origin == "platform" else 0
        platform_key_surcharge_usd = 0.0
        if platform_key_used and ctx.tenant_id != DEFAULT_TENANT_ID and byo_mode == "hibrido":
            platform_key_surcharge_usd = cost_usd * get_plan_surcharge_pct(ctx.tenant_id)

        record_id = new_id("use")
        now = utc_now()

        conn.execute(
            f"""
            INSERT INTO usage_record (
                id,
                workspace_id,
                chat_id,
                tenant_id,
                user_id,
                actor_id,
                actor_role_at_decision,
                provider_slug,
                model,
                input_tokens,
                output_tokens,
                cost_usd,
                duration_ms,
                status,
                error,
                attempts_json,
                request_json,
                response_json,
                routine_version,
                skill_version,
                schema_version,
                source_version,
                approved_by,
                run_id,
                step_index,
                chain_id,
                capability,
                platform_key_used,
                platform_key_surcharge_usd,
                byo_mode_at_run,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record_id,
                workspace_id,
                chat_id,
                ctx.tenant_id,
                ctx.user_id,
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                provider_slug,
                model,
                input_tokens,
                output_tokens,
                cost_usd,
                duration_ms,
                status,
                error,
                json.dumps(attempts_json, ensure_ascii=False),
                json.dumps(request_json, ensure_ascii=False, sort_keys=True),
                json.dumps(response_json, ensure_ascii=False, sort_keys=True),
                None,
                None,
                SCHEMA_VERSION,
                source_version,
                None,
                run_id,
                step_index,
                chain_id,
                capability,
                platform_key_used,
                platform_key_surcharge_usd,
                byo_mode,
                now,
            ),
        )
        row = conn.execute(
            f"""
            SELECT {USAGE_RECORD_COLUMNS}
            FROM usage_record
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (record_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        assert row is not None
        return row_to_dict(row)


def list_usage_records(
    ctx: Context,
    conn: sqlite3.Connection,
    limit: int = 100,
) -> list[dict[str, Any]]:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        rows = conn.execute(
            f"""
            SELECT {USAGE_RECORD_COLUMNS}
            FROM usage_record
            WHERE workspace_id = ? AND tenant_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (workspace_id, ctx.tenant_id, limit),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def sum_user_usage_cost(
    ctx: Context,
    conn: sqlite3.Connection,
    since: str | None = None,
) -> float:
    """Return accumulated cost_usd for the current user across the tenant.

    E2-4: soporte de budget por usuario (plan Sec.1.1 — budget cap y cost
    ledger por usuario, no solo global).
    """

    with transaction(conn, ctx=ctx):
        if not ctx.user_id:
            return 0.0
        params: list[Any] = [ctx.require_tenant(), ctx.user_id]
        sql = """
            SELECT COALESCE(SUM(cost_usd), 0.0) AS total
            FROM usage_record
            WHERE tenant_id = ? AND user_id = ? AND status = 'succeeded'
        """
        if since:
            sql += " AND created_at >= ?"
            params.append(since)
        row = conn.execute(sql, params).fetchone()
        return float(row["total"] or 0.0)


def summarize_tenant_usage_cost(
    conn: sqlite3.Connection,
    tenant_id: str,
    since: str | None = None,
) -> dict[str, Any]:
    """Return aggregate and per-provider/model/month breakdown for a tenant.

    Breakdown rows are scoped to the tenant across all workspaces. Aggregates
    include only succeeded records; failed/budget_exceeded rows are excluded
    from cost totals but counted in ``total_rows``.
    """

    ctx = Context(workspace_id=SYSTEM_WORKSPACE_ID, tenant_id=tenant_id)
    with transaction(conn, ctx=ctx):
        params: list[Any] = [tenant_id]
        total_sql = """
            SELECT COALESCE(SUM(cost_usd), 0.0) AS total_cost,
                   COALESCE(SUM(platform_key_surcharge_usd), 0.0) AS total_surcharge,
                   COUNT(*) AS total_rows
            FROM usage_record
            WHERE tenant_id = ? AND status = 'succeeded'
        """
        breakdown_sql = """
            SELECT provider_slug,
                   model,
                   substr(created_at, 1, 7) AS month,
                   COALESCE(SUM(cost_usd), 0.0) AS total_cost_usd,
                   COALESCE(SUM(platform_key_surcharge_usd), 0.0) AS total_surcharge_usd,
                   COALESCE(SUM(input_tokens), 0) AS total_input_tokens,
                   COALESCE(SUM(output_tokens), 0) AS total_output_tokens,
                   COUNT(*) AS row_count
            FROM usage_record
            WHERE tenant_id = ? AND status = 'succeeded'
        """
        if since:
            total_sql += " AND created_at >= ?"
            breakdown_sql += " AND created_at >= ?"
            params.append(since)
        breakdown_sql += " GROUP BY provider_slug, model, month ORDER BY month DESC, provider_slug ASC, model ASC"

        total_row = conn.execute(total_sql, params).fetchone()
        breakdown_rows = conn.execute(breakdown_sql, params).fetchall()

    return {
        "total_cost_usd": float(total_row["total_cost"] or 0.0),
        "total_surcharge_usd": float(total_row["total_surcharge"] or 0.0),
        "total_rows": int(total_row["total_rows"] or 0),
        "breakdown": [row_to_dict(row) for row in breakdown_rows],
    }


def sum_workspace_usage_cost(
    ctx: Context,
    conn: sqlite3.Connection,
    since: str | None = None,
) -> float:
    """Return accumulated cost_usd for the current workspace."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        params: list[Any] = [workspace_id, ctx.require_tenant()]

        sql = """
            SELECT COALESCE(SUM(cost_usd), 0.0) AS total
            FROM usage_record
            WHERE workspace_id = ? AND tenant_id = ? AND status = 'succeeded'
        """
        if since:
            sql += " AND created_at >= ?"
            params.append(since)
        row = conn.execute(sql, params).fetchone()
        return float(row["total"]) if row and row["total"] is not None else 0.0


# -----------------------------------------------------------------------------
# SL3.5: Routine run helpers with workspace HMAC seal
# -----------------------------------------------------------------------------

ROUTINE_RUN_COLUMNS = """
    id,
    routine_id,
    workspace_id,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    input_json,
    output_json,
    evidence_json,
    status,
    edit_pct,
    task_type,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    urgency,
    reason,
    assigned_to,
    workspace_hmac,
    created_at
"""


def create_routine_run(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    routine_id: str,
    input_json: dict[str, Any],
    output_json: dict[str, Any],
    evidence_json: list[dict[str, Any]],
    status: str,
    edit_pct: float | None = None,
    task_type: str | None = None,
    routine_version: str | None = None,
    skill_version: str | None = None,
    source_version: str | None = None,
    approved_by: str | None = None,
) -> dict[str, Any]:
    """Insert a routine_run row sealed to the current workspace."""

    with transaction(conn, ctx=ctx):
        enforce_tenant_scoped(ctx)
        workspace_id = ctx.require_scoped_workspace()
        if task_type is None:
            routine = get_routine(ctx, conn, routine_id)
            task_type = routine.get("category") if routine else None
        run_id = new_id("run")
        now = utc_now()
        seal_id = workspace_seal_id(ctx, conn)
        input_json_str = json.dumps(input_json, ensure_ascii=False, sort_keys=True)
        output_json_str = json.dumps(output_json, ensure_ascii=False, sort_keys=True)
        hmac = compute_workspace_hmac_for_row(
            seal_id,
            {
                "id": run_id,
                "workspace_id": workspace_id,
                "routine_id": routine_id,
                "input_json": input_json_str,
                "output_json": output_json_str,
                "status": status,
                "source_version": source_version,
            },
            "routine_run",
        )

        conn.execute(
            f"""
            INSERT INTO routine_run (
                id, routine_id, workspace_id, tenant_id, user_id, actor_id,
                actor_role_at_decision, input_json, output_json, evidence_json,
                status, edit_pct, task_type, routine_version, skill_version, schema_version,
                source_version, approved_by, workspace_hmac, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                routine_id,
                workspace_id,
                ctx.tenant_id,
                ctx.user_id,
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                input_json_str,
                output_json_str,
                json.dumps(evidence_json, ensure_ascii=False),
                status,
                edit_pct,
                task_type,
                routine_version,
                skill_version,
                SCHEMA_VERSION,
                source_version,
                approved_by,
                hmac,
                now,
            ),
        )
        row = conn.execute(
            f"SELECT {ROUTINE_RUN_COLUMNS} FROM routine_run WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (run_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        assert row is not None
        return row_to_dict(row)


def set_routine_run_output(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    run_id: str,
    output_json: dict[str, Any],
    evidence_json: list[dict[str, Any]],
    status: str,
    edit_pct: float | None = None,
) -> dict[str, Any] | None:
    """Set the output/evidence/status of an existing routine run."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        seal_id = workspace_seal_id(ctx, conn)
        existing = conn.execute(
            f"""
            SELECT {ROUTINE_RUN_COLUMNS}
            FROM routine_run
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (run_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        if existing is None:
            return None

        output_json_str = json.dumps(output_json, ensure_ascii=False, sort_keys=True)
        hmac_row = row_to_dict(existing)
        hmac_row["output_json"] = output_json_str
        hmac_row["status"] = status
        hmac = compute_workspace_hmac_for_row(seal_id, hmac_row, "routine_run")

        cursor = conn.execute(
            """
            UPDATE routine_run
            SET output_json = ?, evidence_json = ?, status = ?, edit_pct = ?, workspace_hmac = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (
                output_json_str,
                json.dumps(evidence_json, ensure_ascii=False),
                status,
                edit_pct,
                hmac,
                run_id,
                workspace_id,
                ctx.tenant_id,
            ),
        )
        if cursor.rowcount == 0:
            return None
        return get_routine_run(ctx, conn, run_id)


def get_routine_run(
    ctx: Context, conn: sqlite3.Connection, run_id: str
) -> dict[str, Any] | None:
    """Read a routine_run row and verify its workspace HMAC seal."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            f"""
            SELECT {ROUTINE_RUN_COLUMNS}
            FROM routine_run
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (run_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        if row is None:
            return None
        seal_id = workspace_seal_id(ctx, conn)
        assert_workspace_hmac_for_row(seal_id, row_to_dict(row), "routine_run")
        return row_to_dict(row)


def list_routine_runs(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    routine_id: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List routine_run rows, discarding any with a broken workspace HMAC seal."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        sql = f"SELECT {ROUTINE_RUN_COLUMNS} FROM routine_run WHERE workspace_id = ? AND tenant_id = ?"
        params: list[Any] = [workspace_id, ctx.tenant_id]
        if routine_id is not None:
            sql += " AND routine_id = ?"
            params.append(routine_id)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        seal_id = workspace_seal_id(ctx, conn)
        results: list[dict[str, Any]] = []
        for row in conn.execute(sql, params).fetchall():
            if verify_workspace_hmac_for_row(seal_id, row_to_dict(row), "routine_run"):
                results.append(row_to_dict(row))
        return results


# -----------------------------------------------------------------------------
# SL5: Mail connector data access helpers
# -----------------------------------------------------------------------------

MAIL_MESSAGE_COLUMNS = """
    id,
    workspace_id,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    account,
    mail_uid,
    subject,
    sender,
    body_text,
    raw_payload,
    status,
    category,
    draft_id,
    account_id,
    schema_version,
    source_version,
    approved_by,
    created_at,
    updated_at
"""


def create_mail_message(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    account: str,
    mail_uid: str,
    subject: str | None,
    sender: str | None,
    body_text: str | None,
    raw_payload: bytes | None,
    status: str = "unread",
    category: str = "other",
    account_id: str | None = None,
) -> dict[str, Any]:
    """Insert a mail_message row scoped to the current workspace.

    Uses an upsert so repeated IMAP syncs do not crash on the
    UNIQUE(workspace_id, account, mail_uid) constraint.
    """

    with transaction(conn, ctx=ctx):
        enforce_tenant_scoped(ctx)
        workspace_id = ctx.require_scoped_workspace()
        now = utc_now()

        existing = conn.execute(
            f"""
            SELECT {MAIL_MESSAGE_COLUMNS}
            FROM mail_message
            WHERE workspace_id = ? AND account = ? AND mail_uid = ? AND tenant_id = ?
            """,
            (workspace_id, account, mail_uid, ctx.tenant_id),
        ).fetchone()
        if existing is not None:
            return row_to_dict(existing)

        mail_id = new_id("mail")
        conn.execute(
            f"""
            INSERT INTO mail_message (
                id,
                workspace_id,
                tenant_id,
                user_id,
                actor_id,
                actor_role_at_decision,
                account,
                mail_uid,
                subject,
                sender,
                body_text,
                raw_payload,
                status,
                category,
                draft_id,
                account_id,
                schema_version,
                source_version,
                approved_by,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mail_id,
                workspace_id,
                ctx.tenant_id,
                ctx.user_id,
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                account,
                mail_uid,
                subject,
                sender,
                body_text,
                raw_payload,
                status,
                category,
                None,
                account_id,
                SCHEMA_VERSION,
                None,
                None,
                now,
                now,
            ),
        )
        row = conn.execute(
            f"""
            SELECT {MAIL_MESSAGE_COLUMNS}
            FROM mail_message
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (mail_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        assert row is not None
        return row_to_dict(row)


def list_mail_messages(
    ctx: Context,
    conn: sqlite3.Connection,
    limit: int = 100,
) -> list[dict[str, Any]]:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        rows = conn.execute(
            f"""
            SELECT {MAIL_MESSAGE_COLUMNS}
            FROM mail_message
            WHERE workspace_id = ? AND tenant_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (workspace_id, ctx.tenant_id, limit),
        ).fetchall()
        return [row_to_dict(row) for row in rows]


def get_mail_message(
    ctx: Context,
    conn: sqlite3.Connection,
    mail_id: str,
) -> dict[str, Any] | None:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            f"""
            SELECT {MAIL_MESSAGE_COLUMNS}
            FROM mail_message
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (mail_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        return row_to_dict(row) if row else None


def update_mail_message_status(
    ctx: Context,
    conn: sqlite3.Connection,
    mail_id: str,
    status: str,
) -> dict[str, Any] | None:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        with transaction(conn, ctx=ctx):
            conn.execute(
                """
                UPDATE mail_message
                SET status = ?, updated_at = ?
                WHERE id = ? AND workspace_id = ? AND tenant_id = ?
                """,
                (status, utc_now(), mail_id, workspace_id, ctx.tenant_id),
            )
        row = conn.execute(
            f"""
            SELECT {MAIL_MESSAGE_COLUMNS}
            FROM mail_message
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (mail_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        return row_to_dict(row) if row else None


def link_mail_message_to_draft(
    ctx: Context,
    conn: sqlite3.Connection,
    mail_id: str,
    draft_id: str,
    status: str = "drafted",
) -> dict[str, Any] | None:
    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        with transaction(conn, ctx=ctx):
            conn.execute(
                """
                UPDATE mail_message
                SET draft_id = ?, status = ?, updated_at = ?
                WHERE id = ? AND workspace_id = ? AND tenant_id = ?
                """,
                (draft_id, status, utc_now(), mail_id, workspace_id, ctx.tenant_id),
            )
        row = conn.execute(
            f"""
            SELECT {MAIL_MESSAGE_COLUMNS}
            FROM mail_message
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (mail_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        return row_to_dict(row) if row else None


# -----------------------------------------------------------------------------
# SL3b: Routine authoring + WorkLoom HITL + gold loop helpers
# -----------------------------------------------------------------------------

ROUTINE_COLUMNS = """
    id,
    workspace_id,
    tenant_id,
    user_id,
    actor_id,
    actor_role_at_decision,
    name,
    skill_md,
    tools_allowlist,
    schema_output_json,
    preset_id,
    trigger_json,
    persona_md,
    is_active,
    category,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    created_at,
    updated_at
"""

GOLD_CANDIDATE_COLUMNS = """
    id,
    workspace_id,
    tenant_id,
    routine_id,
    run_id,
    edit_pct,
    input_json,
    output_json,
    learned_output_json,
    approved,
    used,
    use_count,
    schema_version,
    source_version,
    approved_by,
    verified_by,
    state,
    actor_role_at_decision,
    created_at,
    updated_at
"""


def _json_ratio(a: dict[str, Any], b: dict[str, Any]) -> float:
    """Return dissimilarity ratio (0..1) between two JSON serializations."""

    sa = json.dumps(a, ensure_ascii=False, sort_keys=True)
    sb = json.dumps(b, ensure_ascii=False, sort_keys=True)
    return round(1 - difflib.SequenceMatcher(None, sa, sb).ratio(), 6)


def create_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    name: str,
    skill_md: str = "",
    tools_allowlist: str = "[]",
    schema_output_json: str = "{}",
    preset_id: str | None = None,
    trigger_json: str = "{}",
    persona_md: str = "",
    is_active: int = 1,
    source_version: str = "v1",
    skill_version: str | None = None,
    category: str = "custom",
) -> dict[str, Any]:
    """Insert a routine scoped to the current workspace."""

    with transaction(conn, ctx=ctx):
        enforce_tenant_scoped(ctx)
        workspace_id = ctx.require_scoped_workspace()
        routine_id = new_id("rtn")
        now = utc_now()
        routine_version = utc_now()

        conn.execute(
            f"""
            INSERT INTO routine (
                id, workspace_id, tenant_id, user_id, actor_id,
                actor_role_at_decision, name, skill_md, tools_allowlist,
                schema_output_json, preset_id, trigger_json, persona_md,
                is_active, category, routine_version, skill_version, schema_version,
                source_version, approved_by, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                routine_id,
                workspace_id,
                ctx.tenant_id,
                ctx.user_id,
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                name.strip(),
                skill_md,
                tools_allowlist,
                schema_output_json,
                preset_id,
                trigger_json,
                persona_md,
                is_active,
                category,
                routine_version,
                skill_version,
                SCHEMA_VERSION,
                source_version,
                None,
                now,
                now,
            ),
        )
        row = conn.execute(
            f"""
            SELECT {ROUTINE_COLUMNS}
            FROM routine
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (routine_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        assert row is not None
        return row_to_dict(row)


def _upsert_gold_candidate_from_run(
    ctx: Context,
    conn: sqlite3.Connection,
    run: dict[str, Any],
) -> None:
    """Create a gold_candidate row when a run is approved with low edit_pct."""

    with transaction(conn, ctx=ctx):
        edit_pct = run.get("edit_pct")
        if edit_pct is None or edit_pct > 0.2:
            return

        candidate_id = new_id("gold")
        now = utc_now()
        tenant_id = ctx.require_tenant()
        conn.execute(
            """
            INSERT INTO gold_candidate (
                id, workspace_id, tenant_id, routine_id, run_id, edit_pct,
                input_json, output_json, learned_output_json, approved,
                state, actor_role_at_decision, schema_version, source_version,
                approved_by, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                edit_pct = excluded.edit_pct,
                input_json = excluded.input_json,
                output_json = excluded.output_json,
                tenant_id = excluded.tenant_id,
                updated_at = excluded.updated_at
            """,
            (
                candidate_id,
                run["workspace_id"],
                tenant_id,
                run["routine_id"],
                run["id"],
                edit_pct,
                run["input_json"],
                run["output_json"],
                json.dumps({}, ensure_ascii=False),
                0,
                "candidate",
                ctx.actor_role_at_decision,
                SCHEMA_VERSION,
                run.get("source_version") or "v1",
                run.get("approved_by"),
                now,
                now,
            ),
        )


def update_routine_run_output(
    ctx: Context,
    conn: sqlite3.Connection,
    run_id: str,
    output_json: dict[str, Any],
    edited_output_json: dict[str, Any],
    approved_by: str | None = None,
) -> dict[str, Any] | None:
    """Apply an edited output, compute edit_pct and optionally approve the run."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        edit_pct = _json_ratio(output_json, edited_output_json)
        status = "succeeded" if approved_by else "requires_hitl"
        source_version = "v1"

        existing = get_routine_run(ctx, conn, run_id)
        if existing is None:
            return None

        seal_id = workspace_seal_id(ctx, conn)
        output_json_str = json.dumps(edited_output_json, ensure_ascii=False, sort_keys=True)
        hmac = compute_workspace_hmac_for_row(
            seal_id,
            {
                "id": run_id,
                "workspace_id": workspace_id,
                "routine_id": existing["routine_id"],
                "input_json": existing["input_json"],
                "output_json": output_json_str,
                "status": status,
                "source_version": source_version,
            },
            "routine_run",
        )

        with transaction(conn, ctx=ctx):
            cursor = conn.execute(
                """
                UPDATE routine_run
                SET output_json = ?, edit_pct = ?, status = ?, approved_by = ?, source_version = ?, workspace_hmac = ?
                WHERE id = ? AND workspace_id = ? AND tenant_id = ?
                """,
                (
                    output_json_str,
                    edit_pct,
                    status,
                    approved_by,
                    source_version,
                    hmac,
                    run_id,
                    workspace_id,
                    ctx.require_tenant(),
                ),
            )
            if cursor.rowcount == 0:
                return None

            updated = get_routine_run(ctx, conn, run_id)
            if updated and status == "succeeded":
                _upsert_gold_candidate_from_run(ctx, conn, updated)
        return updated


def record_routine_run_edit(
    ctx: Context,
    conn: sqlite3.Connection,
    run_id: str,
    edited_output_json: dict[str, Any],
) -> dict[str, Any] | None:
    """Record an edit without changing the run's status."""

    with transaction(conn, ctx=ctx):
        existing = get_routine_run(ctx, conn, run_id)
        if existing is None:
            return None

        try:
            current_output = json.loads(existing.get("output_json") or "{}")
        except json.JSONDecodeError:
            current_output = {}

        edit_pct = _json_ratio(current_output, edited_output_json)
        workspace_id = ctx.require_scoped_workspace()
        source_version = "v1"
        seal_id = workspace_seal_id(ctx, conn)
        output_json_str = json.dumps(edited_output_json, ensure_ascii=False, sort_keys=True)
        hmac = compute_workspace_hmac_for_row(
            seal_id,
            {
                "id": run_id,
                "workspace_id": workspace_id,
                "routine_id": existing["routine_id"],
                "input_json": existing["input_json"],
                "output_json": output_json_str,
                "status": existing["status"],
                "source_version": source_version,
            },
            "routine_run",
        )

        cursor = conn.execute(
            """
            UPDATE routine_run
            SET output_json = ?, edit_pct = ?, source_version = ?, workspace_hmac = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (
                output_json_str,
                edit_pct,
                source_version,
                hmac,
                run_id,
                workspace_id,
                ctx.tenant_id,
            ),
        )
        if cursor.rowcount == 0:
            return None
        return get_routine_run(ctx, conn, run_id)


def approve_routine_run(
    ctx: Context,
    conn: sqlite3.Connection,
    run_id: str,
    approved_by: str | None = None,
    *,
    reason: str | None = None,
    urgency: int = 0,
) -> dict[str, Any] | None:
    """Approve a routine run and, if low edit, create a gold candidate."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        approved_by = approved_by or ctx.resolved_actor_id()
        source_version = "v1"

        existing = get_routine_run(ctx, conn, run_id)
        if existing is None:
            return None

        with transaction(conn, ctx=ctx):
            seal_id = workspace_seal_id(ctx, conn)
            hmac = compute_workspace_hmac_for_row(
                seal_id,
                {
                    "id": run_id,
                    "workspace_id": workspace_id,
                    "routine_id": existing["routine_id"],
                    "input_json": existing["input_json"],
                    "output_json": existing["output_json"],
                    "status": "succeeded",
                    "source_version": source_version,
                },
                "routine_run",
            )

            cursor = conn.execute(
                """
                UPDATE routine_run
                SET status = ?, approved_by = ?, source_version = ?, workspace_hmac = ?, urgency = ?, reason = ?
                WHERE id = ? AND workspace_id = ? AND tenant_id = ?
                """,
                ("succeeded", approved_by, source_version, hmac, urgency, reason, run_id, workspace_id, ctx.tenant_id),
            )
            if cursor.rowcount == 0:
                return None

            updated = get_routine_run(ctx, conn, run_id)
            if updated is None:
                return None
            _upsert_gold_candidate_from_run(ctx, conn, updated)
            record_editorial_event(ctx, conn, "routine_run", run_id, "approved", reason=reason)
        return updated


def reject_routine_run(
    ctx: Context,
    conn: sqlite3.Connection,
    run_id: str,
    *,
    reason: str | None = None,
) -> dict[str, Any] | None:
    """Reject a routine run."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        source_version = "v1"

        existing = get_routine_run(ctx, conn, run_id)
        if existing is None:
            return None

        with transaction(conn, ctx=ctx):
            seal_id = workspace_seal_id(ctx, conn)
            hmac = compute_workspace_hmac_for_row(
                seal_id,
                {
                    "id": run_id,
                    "workspace_id": workspace_id,
                    "routine_id": existing["routine_id"],
                    "input_json": existing["input_json"],
                    "output_json": existing["output_json"],
                    "status": "cancelled",
                    "source_version": source_version,
                },
                "routine_run",
            )

            cursor = conn.execute(
                """
                UPDATE routine_run
                SET status = ?, source_version = ?, workspace_hmac = ?, reason = ?
                WHERE id = ? AND workspace_id = ? AND tenant_id = ?
                """,
                ("cancelled", source_version, hmac, reason, run_id, workspace_id, ctx.tenant_id),
            )
            if cursor.rowcount == 0:
                return None
            updated = get_routine_run(ctx, conn, run_id)
            if updated is not None:
                record_editorial_event(ctx, conn, "routine_run", run_id, "rejected", reason=reason)
        return updated





def approve_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    routine_id: str,
    approved_by: str | None = None,
) -> dict[str, Any] | None:
    """Approve a routine by setting approved_by and updated_at.

    Only updates if the routine exists and is not already approved.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        approved_by = approved_by or ctx.resolved_actor_id()

        existing = get_routine(ctx, conn, routine_id)
        if existing is None:
            return None
        if existing.get("approved_by") is not None:
            return existing

        cursor = conn.execute(
            """
            UPDATE routine
            SET approved_by = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ? AND approved_by IS NULL
            """,
            (approved_by, utc_now(), routine_id, workspace_id, ctx.tenant_id),
        )
        if cursor.rowcount == 0:
            return None
        return get_routine(ctx, conn, routine_id)


def is_routine_name_taken(
    ctx: Context,
    conn: sqlite3.Connection,
    name: str,
    exclude_id: str | None = None,
) -> bool:
    """Return True if another routine in the workspace already uses the name."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        sql = f"""
            SELECT 1 FROM routine
            WHERE workspace_id = ? AND tenant_id = ? AND lower(name) = lower(?)
        """
        params: list[Any] = [workspace_id, ctx.tenant_id, name.strip()]
        if exclude_id:
            sql += " AND id != ?"
            params.append(exclude_id)
        sql += " LIMIT 1"
        return conn.execute(sql, params).fetchone() is not None


def get_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    routine_id: str,
) -> dict[str, Any] | None:
    """Read a routine scoped to the current workspace."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            f"""
            SELECT {ROUTINE_COLUMNS}
            FROM routine
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (routine_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        return row_to_dict(row) if row else None


def get_routine_by_name(
    ctx: Context,
    conn: sqlite3.Connection,
    name: str,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Read routines by name (case-insensitive) in the current workspace.

    Returns a list so callers can detect ambiguous names.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        sql = f"""
            SELECT {ROUTINE_COLUMNS}
            FROM routine
            WHERE workspace_id = ? AND tenant_id = ? AND lower(name) = lower(?)
        """
        params: list[Any] = [workspace_id, ctx.tenant_id, name]
        if category is not None:
            sql += " AND category = ?"
            params.append(category)
        sql += " ORDER BY created_at DESC"
        rows = conn.execute(sql, params).fetchall()
        return [row_to_dict(row) for row in rows]


def list_routines(
    ctx: Context,
    conn: sqlite3.Connection,
    category: str | None = None,
) -> list[dict[str, Any]]:
    """List routines scoped to the current workspace, optionally filtered by category."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        sql = f"""
            SELECT {ROUTINE_COLUMNS}
            FROM routine
            WHERE workspace_id = ? AND tenant_id = ?
        """
        params: list[Any] = [workspace_id, ctx.tenant_id]
        if category is not None:
            sql += " AND category = ?"
            params.append(category)
        sql += " ORDER BY created_at DESC"
        rows = conn.execute(sql, params).fetchall()
        return [row_to_dict(row) for row in rows]


def delete_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    routine_id: str,
) -> bool:
    """Delete a routine scoped to the current workspace."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        cursor = conn.execute(
            "DELETE FROM routine WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (routine_id, workspace_id, ctx.tenant_id),
        )
        return cursor.rowcount > 0


ALLOWED_ROUTINE_UPDATE_FIELDS = frozenset(
    {
        "name",
        "skill_md",
        "tools_allowlist",
        "schema_output_json",
        "preset_id",
        "trigger_json",
        "persona_md",
        "is_active",
        "source_version",
        "skill_version",
        "approved_by",
        "category",
        "routine_version",
    }
)


_ROUTINE_APPROVAL_SENSITIVE_FIELDS = frozenset(
    {
        "name",
        "skill_md",
        "tools_allowlist",
        "schema_output_json",
        "preset_id",
        "trigger_json",
        "persona_md",
        "category",
    }
)


def update_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    routine_id: str,
    **fields: Any,
) -> dict[str, Any] | None:
    """Update a routine scoped to the current workspace.

    Only keys explicitly present in ``fields`` are written, so callers can pass
    ``approved_by=None`` to clear approval without omitting the column.
    Changing executable content clears human approval (HITL bypass prevention).
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        updates = {k: v for k, v in fields.items() if k in ALLOWED_ROUTINE_UPDATE_FIELDS}
        if not updates:
            return get_routine(ctx, conn, routine_id)

        existing = get_routine(ctx, conn, routine_id)
        if existing is None:
            return None

        # Changing executable/persona/model/category clears approval.
        for field in _ROUTINE_APPROVAL_SENSITIVE_FIELDS:
            if field in updates and updates[field] != existing.get(field):
                updates["approved_by"] = None
                break

        # Bump routine_version on any content change.
        if any(field in updates for field in _ROUTINE_APPROVAL_SENSITIVE_FIELDS):
            updates["routine_version"] = utc_now()

        set_clause = ", ".join(f"{k} = ?" for k in updates)
        params = list(updates.values()) + [utc_now(), routine_id, workspace_id, ctx.tenant_id]
        cursor = conn.execute(
            f"UPDATE routine SET {set_clause}, updated_at = ? WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            params,
        )
        if cursor.rowcount == 0:
            return None
        return get_routine(ctx, conn, routine_id)



def get_mail_outbox(
    ctx: Context,
    conn: sqlite3.Connection,
    mail_id: str,
) -> dict[str, Any] | None:
    """Return the outbox row for a mail message if one exists."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            """
            SELECT id, workspace_id, mail_id, idempotency_key, status, retry_count,
                   failed_at, error_json, smtp_message_id, created_at, updated_at
            FROM mail_outbox
            WHERE workspace_id = ? AND tenant_id = ? AND mail_id = ?
            """,
            (workspace_id, ctx.require_tenant(), mail_id),
        ).fetchone()
        return row_to_dict(row) if row else None


def get_mail_outbox_by_key(
    ctx: Context,
    conn: sqlite3.Connection,
    idempotency_key: str,
) -> dict[str, Any] | None:
    """Return an outbox row by idempotency key."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            """
            SELECT id, workspace_id, mail_id, idempotency_key, status, retry_count,
                   failed_at, error_json, smtp_message_id, created_at, updated_at
            FROM mail_outbox
            WHERE workspace_id = ? AND tenant_id = ? AND idempotency_key = ?
            """,
            (workspace_id, ctx.require_tenant(), idempotency_key),
        ).fetchone()
        return row_to_dict(row) if row else None


def create_or_get_mail_outbox(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    mail_id: str,
    idempotency_key: str,
    status: str = "pending",
) -> dict[str, Any]:
    """Atomically create an outbox row or return the existing one.

    Used by the send endpoint to guarantee idempotency and avoid duplicate
    SMTP deliveries.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        existing = get_mail_outbox(ctx, conn, mail_id)
        if existing is not None:
            return existing

        existing_by_key = get_mail_outbox_by_key(ctx, conn, idempotency_key)
        if existing_by_key is not None:
            return existing_by_key

        outbox_id = new_id("outbox")
        now = utc_now()
        conn.execute(
            """
            INSERT INTO mail_outbox (
                id, workspace_id, tenant_id, mail_id, idempotency_key, status,
                smtp_message_id, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (outbox_id, workspace_id, ctx.require_tenant(), mail_id, idempotency_key, status, None, now, now),
        )
        row = conn.execute(
            """
            SELECT id, workspace_id, mail_id, idempotency_key, status,
                   smtp_message_id, created_at, updated_at
            FROM mail_outbox
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (outbox_id, workspace_id, ctx.require_tenant()),
        ).fetchone()
        assert row is not None
        return row_to_dict(row)


def update_mail_outbox_status(
    ctx: Context,
    conn: sqlite3.Connection,
    outbox_id: str,
    *,
    status: str,
    smtp_message_id: str | None = None,
    error_json: str | None = None,
    increment_retry: bool = False,
) -> dict[str, Any] | None:
    """Update outbox status after SMTP attempt."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        now = utc_now()
        failed_at = now if status == "failed" else None
        with transaction(conn, ctx=ctx):
            conn.execute(
                """
                UPDATE mail_outbox
                SET status = ?,
                    smtp_message_id = ?,
                    error_json = COALESCE(?, error_json),
                    retry_count = retry_count + ?,
                    failed_at = ?,
                    updated_at = ?
                WHERE id = ? AND workspace_id = ? AND tenant_id = ?
                """,
                (status, smtp_message_id, error_json, 1 if increment_retry else 0, failed_at, now, outbox_id, workspace_id, ctx.require_tenant()),
            )
        row = conn.execute(
            """
            SELECT id, workspace_id, mail_id, idempotency_key, status, retry_count,
                   failed_at, error_json, smtp_message_id, created_at, updated_at
            FROM mail_outbox
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (outbox_id, workspace_id, ctx.require_tenant()),
        ).fetchone()
        return row_to_dict(row) if row else None


SMTP_CONFIG_COLUMNS = """
    workspace_id,
    host,
    port,
    use_ssl,
    username,
    password,
    from_email,
    is_app_password,
    created_at,
    updated_at
"""


def get_workspace_smtp_config(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    include_password: bool = False,
) -> dict[str, Any] | None:
    """Return the workspace SMTP configuration row or None.

    By default the password is never returned in plain text; only a
    ``has_password`` flag. Pass ``include_password=True`` to receive the
    decrypted password for internal backend use.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        user_id = ctx.user_id or "local"
        row = conn.execute(
            f"""
            SELECT {SMTP_CONFIG_COLUMNS}
            FROM workspace_smtp_config
            WHERE workspace_id = ? AND user_id = ? AND tenant_id = ?
            """,
            (workspace_id, user_id, ctx.require_tenant()),
        ).fetchone()
        if row is None:
            return None
        data = row_to_dict(row)
        data["has_password"] = bool(data.get("password"))
        data["is_app_password"] = int(data.get("is_app_password") or 0)
        if include_password:
            data["password"] = decrypt_value(data.get("password")) or ""
        else:
            data["password"] = ""
        return data


def set_workspace_smtp_config(
    ctx: Context,
    conn: sqlite3.Connection,
    host: str,
    port: int,
    use_ssl: bool,
    username: str,
    password: str,
    from_email: str,
    is_app_password: int | None = None,
) -> dict[str, Any]:
    """Upsert the per-user workspace SMTP configuration.

    The password is encrypted with the master key before persistence.
    If ``password`` is empty, the existing encrypted password is kept.
    If ``is_app_password`` is None, the existing value is kept.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        user_id = ctx.user_id or "local"
        now = utc_now()

        with transaction(conn, ctx=ctx):
            existing_row = conn.execute(
                "SELECT password, is_app_password FROM workspace_smtp_config WHERE workspace_id = ? AND user_id = ? AND tenant_id = ?",
                (workspace_id, user_id, ctx.require_tenant()),
            ).fetchone()
            existing_encrypted = existing_row["password"] if existing_row else None
            existing_app_password = existing_row["is_app_password"] if existing_row else 0

            if password:
                encrypted_password = encrypt_value(password)
            else:
                encrypted_password = existing_encrypted

            final_app_password = is_app_password if is_app_password is not None else existing_app_password

            conn.execute(
                """
                INSERT INTO workspace_smtp_config (
                    workspace_id, tenant_id, user_id, host, port, use_ssl, username, password, from_email,
                    is_app_password, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(workspace_id, user_id) DO UPDATE SET
                    host = excluded.host,
                    port = excluded.port,
                    use_ssl = excluded.use_ssl,
                    username = excluded.username,
                    password = COALESCE(excluded.password, workspace_smtp_config.password),
                    from_email = excluded.from_email,
                    is_app_password = excluded.is_app_password,
                    updated_at = excluded.updated_at
                """,
                (workspace_id, ctx.require_tenant(), user_id, host, port, 1 if use_ssl else 0, username, encrypted_password, from_email, final_app_password, now, now),
            )
        return get_workspace_smtp_config(ctx, conn)


# -----------------------------------------------------------------------------
# SL5: per-workspace IMAP accounts + email signature
# -----------------------------------------------------------------------------

EMAIL_ACCOUNT_COLUMNS = """
    id,
    workspace_id,
    tenant_id,
    user_id,
    label,
    provider,
    host,
    port,
    username,
    password,
    folders_json,
    auth_type,
    read_only,
    is_default,
    is_app_password,
    rotated_at,
    schema_version,
    source_version,
    created_at,
    updated_at
"""


def create_email_account(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    label: str,
    provider: str,
    host: str,
    port: int,
    username: str,
    password: str,
    folders_json: str,
    auth_type: str,
    read_only: int,
    is_default: int,
    is_app_password: int = 1,
) -> dict[str, Any]:
    """Insert an email account scoped to the current workspace.

    The password is encrypted with the master key before persistence.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        now = utc_now()
        account_id = new_id("email")
        encrypted_password = encrypt_value(password)

        with transaction(conn, ctx=ctx):
            # A workspace can only have one default account at a time.
            if is_default:
                conn.execute(
                    "UPDATE email_account SET is_default = 0 WHERE workspace_id = ? AND tenant_id = ?",
                    (workspace_id, ctx.require_tenant()),
                )
            conn.execute(
                f"""
                INSERT INTO email_account (
                    id, workspace_id, tenant_id, user_id, label, provider, host, port,
                    username, password, folders_json, auth_type, read_only, is_default,
                    is_app_password, schema_version, source_version, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    account_id,
                    workspace_id,
                    ctx.tenant_id,
                    ctx.user_id,
                    label,
                    provider,
                    host,
                    port,
                    username,
                    encrypted_password,
                    folders_json,
                    auth_type,
                    read_only,
                    is_default,
                    is_app_password,
                    SCHEMA_VERSION,
                    "v1",
                    now,
                    now,
                ),
            )
        row = conn.execute(
            f"""
            SELECT {EMAIL_ACCOUNT_COLUMNS}
            FROM email_account
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (account_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        assert row is not None
        data = row_to_dict(row)
        data["password"] = decrypt_value(data.get("password"))
        data["has_password"] = bool(data.get("password"))
        data["is_app_password"] = int(data.get("is_app_password") or 0)
        return data


def _mask_email_account(row: Any) -> dict[str, Any]:
    data = row_to_dict(row)
    data["has_password"] = bool(data.get("password"))
    data["is_app_password"] = int(data.get("is_app_password") or 0)
    data["password"] = ""
    return data


def list_email_accounts(
    ctx: Context,
    conn: sqlite3.Connection,
) -> list[dict[str, Any]]:
    """Return all email accounts for the current workspace.

    The password is never returned in plain text; only a has_password flag.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        rows = conn.execute(
            f"""
            SELECT {EMAIL_ACCOUNT_COLUMNS}
            FROM email_account
            WHERE workspace_id = ? AND tenant_id = ?
            ORDER BY is_default DESC, created_at ASC
            """,
            (workspace_id, ctx.tenant_id),
        ).fetchall()
        return [_mask_email_account(row) for row in rows]


def get_email_account(
    ctx: Context,
    conn: sqlite3.Connection,
    account_id: str,
) -> dict[str, Any] | None:
    """Return a single email account if it belongs to the current workspace.

    The password is never returned in plain text; only a has_password flag.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            f"""
            SELECT {EMAIL_ACCOUNT_COLUMNS}
            FROM email_account
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (account_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        if row is None:
            return None
        return _mask_email_account(row)


def get_default_email_account(
    ctx: Context,
    conn: sqlite3.Connection,
    user_id: str | None = None,
) -> dict[str, Any] | None:
    """Return the default email account for the workspace, optionally scoped to a user."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        params: list[Any] = [workspace_id, ctx.tenant_id]
        user_filter = ""
        if user_id is not None:
            user_filter = "AND user_id = ?"
            params.append(user_id)
        row = conn.execute(
            f"""
            SELECT {EMAIL_ACCOUNT_COLUMNS}
            FROM email_account
            WHERE workspace_id = ? AND tenant_id = ? AND is_default = 1 {user_filter}
            ORDER BY created_at ASC
            LIMIT 1
            """,
            params,
        ).fetchone()
        if row is None:
            return None
        data = row_to_dict(row)
        data["password"] = decrypt_value(data.get("password"))
        data["has_password"] = bool(data.get("password"))
        data["is_app_password"] = int(data.get("is_app_password") or 0)
        return data


def update_email_account(
    ctx: Context,
    conn: sqlite3.Connection,
    account_id: str,
    *,
    label: str,
    provider: str,
    host: str,
    port: int,
    username: str,
    password: str,
    folders_json: str,
    auth_type: str,
    read_only: int,
    is_default: int,
    is_app_password: int | None = None,
) -> dict[str, Any] | None:
    """Update an existing email account. Password is encrypted on write.

    If ``password`` is empty, the existing encrypted password is kept.
    If ``is_app_password`` is None, the existing value is kept.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        now = utc_now()

        with transaction(conn, ctx=ctx):
            existing_row = conn.execute(
                "SELECT password, is_app_password FROM email_account WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
                (account_id, workspace_id, ctx.tenant_id),
            ).fetchone()
            if existing_row is None:
                return None
            existing_encrypted = existing_row["password"]
            existing_app_password = existing_row["is_app_password"]

            encrypted_password = encrypt_value(password) if password else existing_encrypted
            final_app_password = is_app_password if is_app_password is not None else existing_app_password

            if is_default:
                conn.execute(
                    "UPDATE email_account SET is_default = 0 WHERE workspace_id = ? AND tenant_id = ?",
                    (workspace_id, ctx.require_tenant()),
                )
            conn.execute(
                """
                UPDATE email_account
                SET label = ?, provider = ?, host = ?, port = ?, username = ?,
                    password = ?, folders_json = ?, auth_type = ?, read_only = ?,
                    is_default = ?, is_app_password = ?, updated_at = ?
                WHERE id = ? AND workspace_id = ? AND tenant_id = ?
                """,
                (
                    label,
                    provider,
                    host,
                    port,
                    username,
                    encrypted_password,
                    folders_json,
                    auth_type,
                    read_only,
                    is_default,
                    final_app_password,
                    now,
                    account_id,
                    workspace_id,
                    ctx.tenant_id,
                ),
            )
        return get_email_account(ctx, conn, account_id)


def rotate_email_account_credentials(
    ctx: Context,
    conn: sqlite3.Connection,
    account_id: str,
    password: str,
) -> dict[str, Any] | None:
    """Rotate the password of an email account and record the rotation time."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        now = utc_now()
        encrypted_password = encrypt_value(password)

        with transaction(conn, ctx=ctx):
            existing = conn.execute(
                "SELECT id FROM email_account WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
                (account_id, workspace_id, ctx.tenant_id),
            ).fetchone()
            if existing is None:
                return None
            conn.execute(
                """
                UPDATE email_account
                SET password = ?, rotated_at = ?, updated_at = ?
                WHERE id = ? AND workspace_id = ? AND tenant_id = ?
                """,
                (encrypted_password, now, now, account_id, workspace_id, ctx.tenant_id),
            )
        return get_email_account(ctx, conn, account_id)


def delete_email_account(
    ctx: Context,
    conn: sqlite3.Connection,
    account_id: str,
) -> bool:
    """Delete an email account. Returns True if a row was removed."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        with transaction(conn, ctx=ctx):
            cursor = conn.execute(
                "DELETE FROM email_account WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
                (account_id, workspace_id, ctx.tenant_id),
            )
        return cursor.rowcount > 0


def get_workspace_email_signature(
    ctx: Context,
    conn: sqlite3.Connection,
) -> str | None:
    """Return the workspace-level email signature, if configured."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            "SELECT email_signature FROM workspace WHERE id = ? AND tenant_id = ?",
            (workspace_id, ctx.tenant_id),
        ).fetchone()
        return row["email_signature"] if row else None


def set_workspace_email_signature(
    ctx: Context,
    conn: sqlite3.Connection,
    signature: str,
) -> dict[str, Any] | None:
    """Update the workspace-level email signature."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        with transaction(conn, ctx=ctx):
            conn.execute(
                "UPDATE workspace SET email_signature = ?, updated_at = ? WHERE id = ? AND tenant_id = ?",
                (signature, utc_now(), workspace_id, ctx.tenant_id),
            )
        return get_workspace(ctx, conn)

# -----------------------------------------------------------------------------
# E2-6: Object storage metadata CRUD
# -----------------------------------------------------------------------------


def create_object(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    origin: str,
    bucket: str,
    object_key: str,
    file_name: str,
    mime_type: str,
    size_bytes: int,
    sha256: str | None = None,
    source_type: str | None = None,
    source_version: str = "v1",
    meta: dict[str, Any] | None = None,
    object_id: str | None = None,
) -> dict[str, Any]:
    """Insert an object metadata row for a workspace-scoped MinIO object.

    The caller is responsible for committing the transaction.
    """

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        tenant_id = ctx.tenant_id
        object_id = object_id or new_id("obj")
        now = utc_now()
        seal_id = workspace_seal_id(ctx, conn)

        hmac_row = {
            "id": object_id,
            "workspace_id": workspace_id,
            "bucket": bucket,
            "object_key": object_key,
            "source_version": source_version,
        }
        hmac = compute_workspace_hmac_for_row(seal_id, hmac_row, "object")

        conn.execute(
            """
            INSERT INTO object (
                id, workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision,
                origin, bucket, object_key, file_name, mime_type, size_bytes, sha256,
                meta_json, ingest_status, source_type, source_version, workspace_hmac,
                schema_version, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                object_id,
                workspace_id,
                tenant_id,
                ctx.user_id,
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                origin,
                bucket,
                object_key,
                file_name,
                mime_type,
                size_bytes,
                sha256,
                json.dumps(meta or {}, ensure_ascii=False, sort_keys=True),
                "pending",
                source_type,
                source_version,
                hmac,
                SCHEMA_VERSION,
                now,
                now,
            ),
        )
        row = conn.execute(
            "SELECT * FROM object WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (object_id, workspace_id, tenant_id),
        ).fetchone()
        return row_to_dict(row)


def get_object(
    ctx: Context,
    conn: sqlite3.Connection,
    object_id: str,
) -> dict[str, Any] | None:
    """Return an object metadata row if it belongs to the scoped workspace."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            """
            SELECT * FROM object
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (object_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        if row is None:
            return None
        result = row_to_dict(row)
        seal_id = workspace_seal_id(ctx, conn)
        assert_workspace_hmac_for_row(seal_id, result, "object")
        return result


def list_objects(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    origin: str | None = None,
    ingest_status: str | None = None,
) -> list[dict[str, Any]]:
    """List object metadata rows for the scoped workspace."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        query = "SELECT * FROM object WHERE workspace_id = ? AND tenant_id = ?"
        params: list[Any] = [workspace_id, ctx.tenant_id]
        if origin:
            query += " AND origin = ?"
            params.append(origin)
        if ingest_status:
            query += " AND ingest_status = ?"
            params.append(ingest_status)
        query += " ORDER BY created_at DESC"
        rows = conn.execute(query, params).fetchall()
        seal_id = workspace_seal_id(ctx, conn)
        results = []
        for row in rows:
            result = row_to_dict(row)
            assert_workspace_hmac_for_row(seal_id, result, "object")
            results.append(result)
        return results


def update_object(
    ctx: Context,
    conn: sqlite3.Connection,
    object_id: str,
    *,
    ingest_status: str | None = None,
    ingest_error: str | None = None,
    sha256: str | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Update mutable fields of an object metadata row."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        row = conn.execute(
            """
            SELECT * FROM object
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (object_id, workspace_id, ctx.tenant_id),
        ).fetchone()
        if row is None:
            return None

        fields: list[str] = []
        params: list[Any] = []
        if ingest_status is not None:
            fields.append("ingest_status = ?")
            params.append(ingest_status)
        if ingest_error is not None:
            fields.append("ingest_error = ?")
            params.append(ingest_error)
        if sha256 is not None:
            fields.append("sha256 = ?")
            params.append(sha256)
        if meta is not None:
            fields.append("meta_json = ?")
            params.append(json.dumps(meta, ensure_ascii=False, sort_keys=True))
        if not fields:
            return row_to_dict(row)

        fields.append("updated_at = ?")
        params.append(utc_now())
        params.extend([object_id, workspace_id, ctx.tenant_id])

        with transaction(conn, ctx=ctx):
            conn.execute(
                f"UPDATE object SET {', '.join(fields)} WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
                params,
            )
        return get_object(ctx, conn, object_id)


def delete_object(
    ctx: Context,
    conn: sqlite3.Connection,
    object_id: str,
) -> bool:
    """Delete an object metadata row. The caller must delete the MinIO object."""

    with transaction(conn, ctx=ctx):
        workspace_id = ctx.require_scoped_workspace()
        with transaction(conn, ctx=ctx):
            cursor = conn.execute(
                "DELETE FROM object WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
                (object_id, workspace_id, ctx.tenant_id),
            )
        return cursor.rowcount > 0


def create_generated_object(
    ctx: Context,
    conn: sqlite3.Connection,
    data: bytes,
    file_name: str,
    mime_type: str,
    source_type: str = "generated",
    source_version: str = "v1",
) -> dict[str, Any]:
    """Persist AI-generated bytes as an object in MinIO and the object table.

    Returns the created object metadata row.
    """

    from .storage import GENERATED_BUCKET, get_object_store, object_key
    from .db import new_id  # local import to avoid circular reference at module load

    object_id = new_id("obj")
    key = object_key(ctx.require_scoped_workspace(), "generated", file_name, object_id, tenant_id=ctx.tenant_id)

    with transaction(conn, ctx=ctx):
        row = create_object(
            ctx,
            conn,
            origin="generated",
            bucket=GENERATED_BUCKET,
            object_key=key,
            file_name=file_name,
            mime_type=mime_type,
            size_bytes=len(data),
            source_type=source_type,
            source_version=source_version,
            object_id=object_id,
        )

    store = get_object_store()
    store.put_object(GENERATED_BUCKET, key, data, mime_type)

    return row



# ---------------------------------------------------------------------------
# E3-4: global skill catalog (context for chat, not workspace-scoped)
# ---------------------------------------------------------------------------


def get_global_skills(
    conn: sqlite3.Connection,
    *,
    tenant_id: str = "global",
    active_only: bool = True,
    pack_id: str | None = None,
    query: str | None = None,
) -> list[dict[str, Any]]:
    """Return global skills available for the skill picker."""

    sql = "SELECT * FROM global_skill_catalog WHERE tenant_id = ?"
    params: list[Any] = [tenant_id]
    if active_only:
        sql += " AND is_active = 1"
    if pack_id:
        sql += " AND pack_id = ?"
        params.append(pack_id)
    if query:
        sql += " AND (skill_id LIKE ? OR name LIKE ? OR description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
    sql += " ORDER BY pack_id, name"
    rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(r) for r in rows]


def get_global_skill_by_id(
    conn: sqlite3.Connection,
    skill_id: str,
    *,
    tenant_id: str = "global",
    active_only: bool = True,
) -> dict[str, Any] | None:
    """Return a single global skill by skill_id."""

    sql = "SELECT * FROM global_skill_catalog WHERE tenant_id = ? AND skill_id = ?"
    params: list[Any] = [tenant_id, skill_id]
    if active_only:
        sql += " AND is_active = 1"
    row = conn.execute(sql, params).fetchone()
    return row_to_dict(row) if row else None


def upsert_global_skill(
    conn: sqlite3.Connection,
    *,
    id: str,
    tenant_id: str = "global",
    pack_id: str,
    skill_id: str,
    name: str,
    description: str,
    skill_md: str,
    manifest_json: str,
    is_active: int = 1,
    approved_by: str | None = "system",
) -> dict[str, Any]:
    """Insert or replace a global skill catalog row."""

    now = utc_now()
    conn.execute(
        """
        INSERT INTO global_skill_catalog (
            id, tenant_id, pack_id, skill_id, name, description, skill_md, manifest_json,
            is_active, approved_by, schema_version, source_version, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(skill_id) DO UPDATE SET
            pack_id = excluded.pack_id,
            name = excluded.name,
            description = excluded.description,
            skill_md = excluded.skill_md,
            manifest_json = excluded.manifest_json,
            is_active = excluded.is_active,
            approved_by = excluded.approved_by,
            updated_at = excluded.updated_at
        """,
        (
            id, tenant_id, pack_id, skill_id, name, description, skill_md, manifest_json,
            is_active, approved_by, SCHEMA_VERSION, "v2", now, now,
        ),
    )
    return get_global_skill_by_id(conn, skill_id, tenant_id=tenant_id, active_only=False)


# ---------------------------------------------------------------------------
# E3-5: Routing presets
# ---------------------------------------------------------------------------


def _default_preset_envelope() -> dict[str, Any]:
    return {
        "jurisdictions": ["US", "EU"],
        "providers_allow": ["anthropic", "openai"],
        "providers_deny": [],
        "data_collection": "deny",
        "byo_keys": False,
    }


def _default_preset_curve(mode: str = "balanceado") -> dict[str, Any]:
    return {"mode": mode, "borderline_policy": "premium" if mode in {"sport", "sport_plus"} else "cheap" if mode == "eco" else "premium"}


def _default_preset_caps() -> dict[str, Any]:
    return {"monthly_budget_usd": 50.0, "max_cost_per_task_usd": 0.5, "max_latency_s": 12.0}


def _default_preset_escalation() -> dict[str, Any]:
    return {"user_boost_button": True, "boost_cap_per_day": 10}


DEFAULT_PRESET_TEMPLATES: list[dict[str, Any]] = [
    {
        "preset_id": "conservador",
        "name": "Conservador",
        "description": "US/EU only, ZDR on, default seguro para onboarding.",
        "envelope": {**_default_preset_envelope(), "providers_allow": ["anthropic", "openai"]},
        "curve": _default_preset_curve("sport"),
        "task_overrides": {},
        "caps": _default_preset_caps(),
        "escalation": _default_preset_escalation(),
    },
    {
        "preset_id": "balanceado",
        "name": "Balanceado",
        "description": "US/EU only, modo balanceado recomendado interactivo.",
        "envelope": _default_preset_envelope(),
        "curve": _default_preset_curve("balanceado"),
        "task_overrides": {},
        "caps": _default_preset_caps(),
        "escalation": _default_preset_escalation(),
    },
    {
        "preset_id": "ahorro",
        "name": "Ahorro",
        "description": "US/EU + cost-mode para tareas batch y back-office.",
        "envelope": {**_default_preset_envelope(), "providers_allow": ["anthropic", "openai", "kimi"]},
        "curve": _default_preset_curve("eco"),
        "task_overrides": {},
        "caps": {**_default_preset_caps(), "monthly_budget_usd": 30.0},
        "escalation": _default_preset_escalation(),
    },
    {
        "preset_id": "sport",
        "name": "Sport",
        "description": "Siempre el mejor modelo; demos y tareas críticas.",
        "envelope": _default_preset_envelope(),
        "curve": _default_preset_curve("sport_plus"),
        "task_overrides": {},
        "caps": {**_default_preset_caps(), "monthly_budget_usd": 200.0},
        "escalation": _default_preset_escalation(),
    },
]


def seed_routing_presets(
    ctx: Context,
    conn: sqlite3.Connection,
    created_by: str = "system",
) -> list[dict[str, Any]]:
    """Seed the four default FaberLoom preset templates for a tenant.

    Idempotent: skips existing (tenant_id, preset_id) pairs and bumps version
    only when the template content changed.
    """

    ctx.require_tenant()
    now = utc_now()
    created: list[dict[str, Any]] = []
    with transaction(conn, ctx=ctx):
        for template in DEFAULT_PRESET_TEMPLATES:
            existing = conn.execute(
                "SELECT preset_id FROM routing_preset WHERE tenant_id = ? AND preset_id = ?",
                (ctx.require_tenant(), template["preset_id"]),
            ).fetchone()
            if existing is not None:
                continue
            conn.execute(
                f"""
                INSERT INTO routing_preset (
                    tenant_id, preset_id, name, version, description,
                    envelope_json, curve_json, task_overrides_json, caps_json, escalation_json,
                    is_active, is_template, created_by, actor_id, actor_role_at_decision,
                    routine_version, skill_version, schema_version, source_version,
                    approved_by, created_at, updated_at
                )
                VALUES ({','.join('?' for _ in range(22))})
                """,
                (
                    ctx.require_tenant(),
                    template["preset_id"],
                    template["name"],
                    1,
                    template.get("description"),
                    json.dumps(template["envelope"], ensure_ascii=False),
                    json.dumps(template["curve"], ensure_ascii=False),
                    json.dumps(template["task_overrides"], ensure_ascii=False),
                    json.dumps(template["caps"], ensure_ascii=False),
                    json.dumps(template["escalation"], ensure_ascii=False),
                    1,
                    1,
                    created_by,
                    ctx.resolved_actor_id(),
                    ctx.actor_role_at_decision,
                    None,
                    None,
                    SCHEMA_VERSION,
                    "v1",
                    None,
                    now,
                    now,
                ),
            )
            created.append(template)
    return created


def list_routing_presets(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    active_only: bool = False,
    templates_only: bool = False,
) -> list[dict[str, Any]]:
    """Return routing presets for the current tenant."""

    ctx.require_tenant()
    query = f"SELECT {ROUTING_PRESET_COLUMNS} FROM routing_preset WHERE tenant_id = ?"
    params: list[Any] = [ctx.require_tenant()]
    if active_only:
        query += " AND is_active = 1"
    if templates_only:
        query += " AND is_template = 1"
    query += " ORDER BY is_template DESC, name ASC"
    rows = conn.execute(query, params).fetchall()
    return [_routing_preset_row_to_dict(row) for row in rows]


def get_routing_preset(
    ctx: Context,
    conn: sqlite3.Connection,
    preset_id: str,
) -> dict[str, Any] | None:
    """Return a single routing preset if it belongs to the current tenant."""

    ctx.require_tenant()
    row = conn.execute(
        f"SELECT {ROUTING_PRESET_COLUMNS} FROM routing_preset WHERE tenant_id = ? AND preset_id = ?",
        (ctx.require_tenant(), preset_id),
    ).fetchone()
    return _routing_preset_row_to_dict(row) if row else None


def create_routing_preset(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    preset_id: str,
    name: str,
    description: str | None = None,
    envelope: dict[str, Any] | None = None,
    curve: dict[str, Any] | None = None,
    task_overrides: dict[str, Any] | None = None,
    caps: dict[str, Any] | None = None,
    escalation: dict[str, Any] | None = None,
    is_active: bool = True,
    is_template: bool = False,
) -> dict[str, Any]:
    """Create a tenant-scoped routing preset."""

    ctx.require_tenant()
    now = utc_now()
    with transaction(conn, ctx=ctx):
        existing = conn.execute(
            "SELECT preset_id FROM routing_preset WHERE tenant_id = ? AND preset_id = ?",
            (ctx.require_tenant(), preset_id),
        ).fetchone()
        if existing is not None:
            raise ValueError(f"Preset '{preset_id}' already exists in this tenant")
        conn.execute(
            f"""
            INSERT INTO routing_preset (
                tenant_id, preset_id, name, version, description,
                envelope_json, curve_json, task_overrides_json, caps_json, escalation_json,
                is_active, is_template, created_by, actor_id, actor_role_at_decision,
                routine_version, skill_version, schema_version, source_version,
                approved_by, created_at, updated_at
            )
            VALUES ({','.join('?' for _ in range(22))})
            """,
            (
                ctx.require_tenant(),
                preset_id,
                name.strip(),
                1,
                description,
                json.dumps(envelope or _default_preset_envelope(), ensure_ascii=False),
                json.dumps(curve or _default_preset_curve(), ensure_ascii=False),
                json.dumps(task_overrides or {}, ensure_ascii=False),
                json.dumps(caps or _default_preset_caps(), ensure_ascii=False),
                json.dumps(escalation or _default_preset_escalation(), ensure_ascii=False),
                1 if is_active else 0,
                1 if is_template else 0,
                ctx.resolved_actor_id(),
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                None,
                None,
                SCHEMA_VERSION,
                "v1",
                None,
                now,
                now,
            ),
        )
        row = conn.execute(
            f"SELECT {ROUTING_PRESET_COLUMNS} FROM routing_preset WHERE tenant_id = ? AND preset_id = ?",
            (ctx.require_tenant(), preset_id),
        ).fetchone()
        assert row is not None
        return _routing_preset_row_to_dict(row)


def update_routing_preset(
    ctx: Context,
    conn: sqlite3.Connection,
    preset_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    envelope: dict[str, Any] | None = None,
    curve: dict[str, Any] | None = None,
    task_overrides: dict[str, Any] | None = None,
    caps: dict[str, Any] | None = None,
    escalation: dict[str, Any] | None = None,
    is_active: bool | None = None,
    is_template: bool | None = None,
) -> dict[str, Any] | None:
    """Update a routing preset, bumping version on content changes."""

    ctx.require_tenant()
    with transaction(conn, ctx=ctx):
        existing = get_routing_preset(ctx, conn, preset_id)
        if existing is None:
            return None
        updates: dict[str, Any] = {"updated_at": utc_now()}
        if name is not None:
            updates["name"] = name.strip()
        if description is not None:
            updates["description"] = description
        if envelope is not None:
            updates["envelope_json"] = json.dumps(envelope, ensure_ascii=False)
        if curve is not None:
            updates["curve_json"] = json.dumps(curve, ensure_ascii=False)
        if task_overrides is not None:
            updates["task_overrides_json"] = json.dumps(task_overrides, ensure_ascii=False)
        if caps is not None:
            updates["caps_json"] = json.dumps(caps, ensure_ascii=False)
        if escalation is not None:
            updates["escalation_json"] = json.dumps(escalation, ensure_ascii=False)
        if is_active is not None:
            updates["is_active"] = 1 if is_active else 0
        if is_template is not None:
            updates["is_template"] = 1 if is_template else 0
        if len(updates) > 1:
            updates["version"] = existing["version"] + 1
        cols = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"UPDATE routing_preset SET {cols} WHERE tenant_id = ? AND preset_id = ?",
            (*updates.values(), ctx.require_tenant(), preset_id),
        )
        return get_routing_preset(ctx, conn, preset_id)


def delete_routing_preset(
    ctx: Context,
    conn: sqlite3.Connection,
    preset_id: str,
) -> bool:
    """Delete a routing preset. Returns True if it existed and was deleted."""

    ctx.require_tenant()
    with transaction(conn, ctx=ctx):
        cursor = conn.execute(
            "DELETE FROM routing_preset WHERE tenant_id = ? AND preset_id = ?",
            (ctx.require_tenant(), preset_id),
        )
        return cursor.rowcount > 0


def resolve_routing_preset(
    ctx: Context,
    conn: sqlite3.Connection,
    preset_ref: str | None,
    *,
    task_class: str | None = None,
    complexity: str = "medium",
) -> dict[str, Any] | None:
    """Resolve a preset reference into provider/model/params.

    Accepts '@preset/<slug>', a plain slug, or legacy 'provider:model'.
    Returns None if the reference is empty or cannot be resolved.
    """

    if not preset_ref:
        return None
    ref = preset_ref.strip()
    if not ref:
        return None
    if ":" in ref:
        provider, model = ref.split(":", 1)
        return {
            "preset_id": ref,
            "provider_slug": provider,
            "model": model,
            "params": {},
            "reason": "legacy_provider_model",
        }
    slug = ref.split("@preset/", 1)[-1].strip()
    preset = get_routing_preset(ctx, conn, slug)
    if preset is None:
        return None
    envelope = preset.get("envelope") or {}
    curve = preset.get("curve") or {}
    task_overrides = preset.get("task_overrides") or {}
    providers_allow = envelope.get("providers_allow") or ["anthropic", "openai"]
    mode = curve.get("mode") or "balanceado"
    borderline_policy = curve.get("borderline_policy") or "premium"
    override = task_overrides.get(task_class) if task_class else None
    if override and override.get("default"):
        default_model = override["default"]
        provider_guess = next((p for p in providers_allow if default_model in router_cost.MODEL_ALLOWLIST.get(p, set())), providers_allow[0])
        return {
            "preset_id": slug,
            "provider_slug": provider_guess,
            "model": default_model,
            "params": {"mode": mode, "borderline_policy": borderline_policy},
            "reason": "task_override",
        }
    # Mode-based fallback using the catalog.
    if mode in {"eco", "cheap"}:
        preferred = "gpt-4o-mini"
        provider_guess = next((p for p in providers_allow if preferred in router_cost.MODEL_ALLOWLIST.get(p, set())), providers_allow[0])
        return {
            "preset_id": slug,
            "provider_slug": provider_guess,
            "model": preferred,
            "params": {"mode": mode, "borderline_policy": borderline_policy},
            "reason": "mode_fallback_cheap",
        }
    if mode in {"sport_plus", "sport"}:
        preferred = "claude-3-5-sonnet"
        provider_guess = next((p for p in providers_allow if preferred in router_cost.MODEL_ALLOWLIST.get(p, set())), providers_allow[0])
        return {
            "preset_id": slug,
            "provider_slug": provider_guess,
            "model": preferred,
            "params": {"mode": mode, "borderline_policy": borderline_policy},
            "reason": "mode_fallback_premium",
        }
    preferred = "gpt-4o"
    provider_guess = next((p for p in providers_allow if preferred in router_cost.MODEL_ALLOWLIST.get(p, set())), providers_allow[0])
    return {
        "preset_id": slug,
        "provider_slug": provider_guess,
        "model": preferred,
        "params": {"mode": mode, "borderline_policy": borderline_policy},
        "reason": "mode_fallback_balanced",
    }


# -----------------------------------------------------------------------------
# E3-6: manual billing (invoices + payment reconciliation)
# -----------------------------------------------------------------------------


MANUAL_INVOICE_COLUMNS = """
    tenant_id,
    invoice_id,
    customer_name,
    customer_tax_id,
    customer_email,
    issue_date,
    due_date,
    line_items_json,
    subtotal,
    tax_total,
    total,
    currency,
    status,
    paid_at,
    paid_amount,
    payment_reference,
    notes,
    created_by,
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


PAYMENT_RECONCILIATION_COLUMNS = """
    tenant_id,
    reconciliation_id,
    bank_reference,
    received_at,
    amount,
    currency,
    payer_name,
    payer_account,
    matched_invoice_id,
    status,
    notes,
    created_by,
    actor_id,
    actor_role_at_decision,
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    created_at
"""


def _invoice_line_items_totals(line_items: list[dict[str, Any]]) -> tuple[float, float, float]:
    """Return (subtotal, tax_total, total) for a list of line items."""

    subtotal = 0.0
    tax_total = 0.0
    for item in line_items:
        quantity = float(item.get("quantity", 1) or 1)
        unit_price = float(item.get("unit_price", 0) or 0)
        tax_pct = float(item.get("tax_pct", 0) or 0)
        line_subtotal = quantity * unit_price
        line_tax = line_subtotal * tax_pct / 100.0
        subtotal += line_subtotal
        tax_total += line_tax
    return round(subtotal, 4), round(tax_total, 4), round(subtotal + tax_total, 4)


def _manual_invoice_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    data = row_to_dict(row)
    try:
        data["line_items"] = json.loads(data.get("line_items_json") or "[]")
    except Exception:
        data["line_items"] = []
    data.pop("line_items_json", None)
    return data


def _payment_reconciliation_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return row_to_dict(row)


def list_manual_invoices(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Return manual invoices for the current tenant."""

    ctx.require_tenant()
    query = f"SELECT {MANUAL_INVOICE_COLUMNS} FROM manual_invoice WHERE tenant_id = ?"
    params: list[Any] = [ctx.require_tenant()]
    if status is not None:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY issue_date DESC, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    return [_manual_invoice_row_to_dict(row) for row in rows]


def get_manual_invoice(
    ctx: Context,
    conn: sqlite3.Connection,
    invoice_id: str,
) -> dict[str, Any] | None:
    """Return a single manual invoice if it belongs to the current tenant."""

    ctx.require_tenant()
    row = conn.execute(
        f"SELECT {MANUAL_INVOICE_COLUMNS} FROM manual_invoice WHERE tenant_id = ? AND invoice_id = ?",
        (ctx.require_tenant(), invoice_id),
    ).fetchone()
    return _manual_invoice_row_to_dict(row) if row else None


def create_manual_invoice(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    invoice_id: str,
    customer_name: str,
    customer_tax_id: str | None = None,
    customer_email: str | None = None,
    issue_date: str,
    due_date: str | None = None,
    line_items: list[dict[str, Any]] | None = None,
    currency: str = "USD",
    notes: str | None = None,
) -> dict[str, Any]:
    """Create a manual invoice for the current tenant."""

    ctx.require_tenant()
    line_items = line_items or []
    subtotal, tax_total, total = _invoice_line_items_totals(line_items)
    now = utc_now()
    with transaction(conn, ctx=ctx):
        existing = conn.execute(
            "SELECT invoice_id FROM manual_invoice WHERE tenant_id = ? AND invoice_id = ?",
            (ctx.require_tenant(), invoice_id),
        ).fetchone()
        if existing is not None:
            raise ValueError(f"Invoice '{invoice_id}' already exists in this tenant")
        conn.execute(
            f"""
            INSERT INTO manual_invoice (
                tenant_id, invoice_id, customer_name, customer_tax_id, customer_email,
                issue_date, due_date, line_items_json, subtotal, tax_total, total,
                currency, status, paid_at, paid_amount, payment_reference, notes,
                created_by, actor_id, actor_role_at_decision, routine_version, skill_version,
                schema_version, source_version, approved_by, created_at, updated_at
            )
            VALUES ({','.join('?' for _ in range(27))})
            """,
            (
                ctx.require_tenant(),
                invoice_id,
                customer_name.strip(),
                customer_tax_id,
                customer_email,
                issue_date,
                due_date,
                json.dumps(line_items, ensure_ascii=False),
                subtotal,
                tax_total,
                total,
                currency,
                "draft",
                None,
                None,
                None,
                notes,
                ctx.resolved_actor_id(),
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                None,
                None,
                SCHEMA_VERSION,
                "v1",
                None,
                now,
                now,
            ),
        )
        row = conn.execute(
            f"SELECT {MANUAL_INVOICE_COLUMNS} FROM manual_invoice WHERE tenant_id = ? AND invoice_id = ?",
            (ctx.require_tenant(), invoice_id),
        ).fetchone()
        assert row is not None
        return _manual_invoice_row_to_dict(row)


def update_manual_invoice(
    ctx: Context,
    conn: sqlite3.Connection,
    invoice_id: str,
    *,
    status: str | None = None,
    paid_at: str | None = None,
    paid_amount: float | None = None,
    payment_reference: str | None = None,
    notes: str | None = None,
) -> dict[str, Any] | None:
    """Update a manual invoice (status / payment fields)."""

    ctx.require_tenant()
    with transaction(conn, ctx=ctx):
        existing = get_manual_invoice(ctx, conn, invoice_id)
        if existing is None:
            return None
        updates: dict[str, Any] = {"updated_at": utc_now()}
        if status is not None:
            updates["status"] = status
        if paid_at is not None:
            updates["paid_at"] = paid_at
        if paid_amount is not None:
            updates["paid_amount"] = paid_amount
        if payment_reference is not None:
            updates["payment_reference"] = payment_reference
        if notes is not None:
            updates["notes"] = notes
        if not updates:
            return existing
        cols = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(
            f"UPDATE manual_invoice SET {cols} WHERE tenant_id = ? AND invoice_id = ?",
            (*updates.values(), ctx.require_tenant(), invoice_id),
        )
        return get_manual_invoice(ctx, conn, invoice_id)


def delete_manual_invoice(
    ctx: Context,
    conn: sqlite3.Connection,
    invoice_id: str,
) -> bool:
    """Delete a manual invoice. Returns True if it existed and was deleted."""

    ctx.require_tenant()
    with transaction(conn, ctx=ctx):
        cursor = conn.execute(
            "DELETE FROM manual_invoice WHERE tenant_id = ? AND invoice_id = ?",
            (ctx.require_tenant(), invoice_id),
        )
        return cursor.rowcount > 0


def list_reconciliations(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    status: str | None = None,
) -> list[dict[str, Any]]:
    """Return payment reconciliations for the current tenant."""

    ctx.require_tenant()
    query = f"SELECT {PAYMENT_RECONCILIATION_COLUMNS} FROM payment_reconciliation WHERE tenant_id = ?"
    params: list[Any] = [ctx.require_tenant()]
    if status is not None:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY received_at DESC, created_at DESC"
    rows = conn.execute(query, params).fetchall()
    return [_payment_reconciliation_row_to_dict(row) for row in rows]


def get_reconciliation(
    ctx: Context,
    conn: sqlite3.Connection,
    reconciliation_id: str,
) -> dict[str, Any] | None:
    """Return a single reconciliation if it belongs to the current tenant."""

    ctx.require_tenant()
    row = conn.execute(
        f"SELECT {PAYMENT_RECONCILIATION_COLUMNS} FROM payment_reconciliation WHERE tenant_id = ? AND reconciliation_id = ?",
        (ctx.require_tenant(), reconciliation_id),
    ).fetchone()
    return _payment_reconciliation_row_to_dict(row) if row else None


def create_reconciliation(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    reconciliation_id: str,
    bank_reference: str | None = None,
    received_at: str,
    amount: float,
    currency: str = "USD",
    payer_name: str | None = None,
    payer_account: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """Create a payment reconciliation entry for the current tenant."""

    ctx.require_tenant()
    now = utc_now()
    with transaction(conn, ctx=ctx):
        existing = conn.execute(
            "SELECT reconciliation_id FROM payment_reconciliation WHERE tenant_id = ? AND reconciliation_id = ?",
            (ctx.require_tenant(), reconciliation_id),
        ).fetchone()
        if existing is not None:
            raise ValueError(f"Reconciliation '{reconciliation_id}' already exists in this tenant")
        conn.execute(
            f"""
            INSERT INTO payment_reconciliation (
                tenant_id, reconciliation_id, bank_reference, received_at, amount,
                currency, payer_name, payer_account, matched_invoice_id, status, notes,
                created_by, actor_id, actor_role_at_decision, routine_version, skill_version,
                schema_version, source_version, approved_by, created_at
            )
            VALUES ({','.join('?' for _ in range(20))})
            """,
            (
                ctx.require_tenant(),
                reconciliation_id,
                bank_reference,
                received_at,
                amount,
                currency,
                payer_name,
                payer_account,
                None,
                "pending",
                notes,
                ctx.resolved_actor_id(),
                ctx.resolved_actor_id(),
                ctx.actor_role_at_decision,
                None,
                None,
                SCHEMA_VERSION,
                "v1",
                None,
                now,
            ),
        )
        row = conn.execute(
            f"SELECT {PAYMENT_RECONCILIATION_COLUMNS} FROM payment_reconciliation WHERE tenant_id = ? AND reconciliation_id = ?",
            (ctx.require_tenant(), reconciliation_id),
        ).fetchone()
        assert row is not None
        return _payment_reconciliation_row_to_dict(row)


def match_reconciliation(
    ctx: Context,
    conn: sqlite3.Connection,
    reconciliation_id: str,
    *,
    matched_invoice_id: str,
    notes: str | None = None,
) -> dict[str, Any] | None:
    """Match a pending reconciliation to an invoice and optionally mark it paid."""

    ctx.require_tenant()
    with transaction(conn, ctx=ctx):
        reconciliation = get_reconciliation(ctx, conn, reconciliation_id)
        if reconciliation is None:
            return None
        invoice = get_manual_invoice(ctx, conn, matched_invoice_id)
        if invoice is None:
            raise ValueError(f"Invoice '{matched_invoice_id}' not found in this tenant")
        updates_recon: dict[str, Any] = {
            "matched_invoice_id": matched_invoice_id,
            "status": "matched",
        }
        if notes is not None:
            updates_recon["notes"] = notes
        cols = ", ".join(f"{k} = ?" for k in updates_recon)
        conn.execute(
            f"UPDATE payment_reconciliation SET {cols} WHERE tenant_id = ? AND reconciliation_id = ?",
            (*updates_recon.values(), ctx.require_tenant(), reconciliation_id),
        )
        # Mirror the payment on the invoice when amounts match (best-effort hint).
        if invoice.get("total") is not None and abs(float(invoice["total"]) - float(reconciliation["amount"])) < 0.001:
            update_manual_invoice(
                ctx,
                conn,
                matched_invoice_id,
                status="paid",
                paid_at=reconciliation.get("received_at"),
                paid_amount=reconciliation["amount"],
                payment_reference=f"reconciliation:{reconciliation_id}",
            )
        return get_reconciliation(ctx, conn, reconciliation_id)
