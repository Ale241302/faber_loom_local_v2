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

from .context import Context
from .models import MIGRATIONS, SCHEMA_VERSION, RoutineCreate, WorkspaceCreate
from .router import cost as router_cost
from .seal import (
    assert_workspace_hmac_for_row,
    compute_workspace_hmac_for_row,
    verify_workspace_hmac_for_row,
)


APP_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = APP_DIR / "data"


def _default_user_data_dir() -> Path:
    """Return the OS-appropriate user data directory for SpaceLoom."""

    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path.home() / ".local" / "share"
    return base / "SpaceLoom"


DEFAULT_DB_PATH = _default_user_data_dir() / "spaceloom.sqlite3"

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


def workspace_seal_id(ctx: Context, conn: sqlite3.Connection) -> str:
    """Return the workspace seal_id for the current scoped context."""

    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        "SELECT seal_id FROM workspace WHERE id = ? AND tenant_id IS ?",
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
    seal_id = uuid.uuid4().hex

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
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            now,
            now,
        ),
    )
    created = system_get_workspace(ctx, conn, workspace_id)
    if created is None:
        raise RuntimeError("Workspace was created but could not be read back")
    return created


def get_workspace_field_aliases(
    ctx: Context,
    conn: sqlite3.Connection,
) -> dict[str, list[str]]:
    """Return the workspace field alias map (workspace-scoped)."""

    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        "SELECT field_aliases_json FROM workspace WHERE id = ? AND tenant_id IS ?",
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
    with transaction(conn):
        cursor = conn.execute(
            """
            UPDATE workspace
            SET field_aliases_json = ?, updated_at = ?
            WHERE id = ? AND tenant_id IS ?
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
    created_at
"""


def record_editorial_event(
    ctx: Context,
    conn: sqlite3.Connection,
    entity_type: str,
    entity_id: str,
    action: str,
    reason: str | None = None,
) -> dict[str, Any]:
    """Record an editorial decision (approve/reject/apply) for an entity."""

    workspace_id = ctx.require_scoped_workspace()
    event_id = new_id("ed")
    now = utc_now()
    conn.execute(
        """
        INSERT INTO editorial_history (
            id, workspace_id, entity_type, entity_id, action, actor_id, reason, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            workspace_id,
            entity_type,
            entity_id,
            action,
            ctx.resolved_actor_id(),
            reason,
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

    workspace_id = ctx.require_scoped_workspace()
    sql = f"""
        SELECT {EDITORIAL_HISTORY_COLUMNS}
        FROM editorial_history
        WHERE workspace_id = ?
    """
    params: list[Any] = [workspace_id]
    if entity_type is not None:
        sql += " AND entity_type = ?"
        params.append(entity_type)
    if entity_id is not None:
        sql += " AND entity_id = ?"
        params.append(entity_id)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(row) for row in rows]


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
    created_at
"""


def create_chat(
    ctx: Context,
    conn: sqlite3.Connection,
    title: str,
) -> dict[str, Any]:
    """Insert a chat scoped to the current workspace."""

    workspace_id = ctx.require_scoped_workspace()
    chat_id = new_id("chat")
    now = utc_now()

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
            ctx.user_id,
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
        f"SELECT {CHAT_COLUMNS} FROM chat WHERE id = ? AND workspace_id = ? AND tenant_id IS ?",
        (chat_id, workspace_id, ctx.tenant_id),
    ).fetchone()
    assert row is not None
    return row_to_dict(row)


def list_chats(ctx: Context, conn: sqlite3.Connection) -> list[dict[str, Any]]:
    workspace_id = ctx.require_scoped_workspace()
    rows = conn.execute(
        f"""
        SELECT {CHAT_COLUMNS}
        FROM chat
        WHERE workspace_id = ? AND tenant_id IS ?
        ORDER BY created_at DESC
        """,
        (workspace_id, ctx.tenant_id),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def get_chat(
    ctx: Context,
    conn: sqlite3.Connection,
    chat_id: str,
) -> dict[str, Any] | None:
    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        f"""
        SELECT {CHAT_COLUMNS}
        FROM chat
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
        """,
        (chat_id, workspace_id, ctx.tenant_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def insert_message(
    ctx: Context,
    conn: sqlite3.Connection,
    *,
    chat_id: str,
    role: str,
    content: str,
) -> dict[str, Any]:
    workspace_id = ctx.require_scoped_workspace()
    if get_chat(ctx, conn, chat_id) is None:
        raise ValueError("Chat not found in current Context")
    message_id = new_id("msg")
    now = utc_now()

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
            ctx.user_id,
            ctx.resolved_actor_id(),
            ctx.actor_role_at_decision,
            role,
            json.dumps({"content": content}, ensure_ascii=False),
            None,
            None,
            SCHEMA_VERSION,
            None,
            None,
            now,
        ),
    )
    row = conn.execute(
        f"""
        SELECT {MESSAGE_COLUMNS}
        FROM message
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
        """,
        (message_id, workspace_id, ctx.tenant_id),
    ).fetchone()
    assert row is not None
    return row_to_dict(row)


def get_messages(
    ctx: Context,
    conn: sqlite3.Connection,
    chat_id: str,
) -> list[dict[str, Any]]:
    workspace_id = ctx.require_scoped_workspace()
    rows = conn.execute(
        f"""
        SELECT {MESSAGE_COLUMNS}
        FROM message
        WHERE chat_id = ? AND workspace_id = ? AND tenant_id IS ?
        ORDER BY created_at ASC, id ASC
        """,
        (chat_id, workspace_id, ctx.tenant_id),
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
) -> dict[str, Any]:
    workspace_id = ctx.require_scoped_workspace()
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
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            now,
        ),
    )
    row = conn.execute(
        f"""
        SELECT {USAGE_RECORD_COLUMNS}
        FROM usage_record
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
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
    workspace_id = ctx.require_scoped_workspace()
    rows = conn.execute(
        f"""
        SELECT {USAGE_RECORD_COLUMNS}
        FROM usage_record
        WHERE workspace_id = ? AND tenant_id IS ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (workspace_id, ctx.tenant_id, limit),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def sum_workspace_usage_cost(
    ctx: Context,
    conn: sqlite3.Connection,
    since: str | None = None,
) -> float:
    """Return accumulated cost_usd for the current workspace."""

    workspace_id = ctx.require_scoped_workspace()
    params: list[Any] = [workspace_id]
    tenant_clause = "tenant_id IS NULL" if ctx.tenant_id is None else "tenant_id = ?"
    if ctx.tenant_id is not None:
        params.append(ctx.tenant_id)

    sql = f"""
        SELECT COALESCE(SUM(cost_usd), 0.0) AS total
        FROM usage_record
        WHERE workspace_id = ? AND {tenant_clause} AND status = 'succeeded'
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
    routine_version,
    skill_version,
    schema_version,
    source_version,
    approved_by,
    urgency,
    reason,
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
    routine_version: str | None = None,
    skill_version: str | None = None,
    source_version: str | None = None,
    approved_by: str | None = None,
) -> dict[str, Any]:
    """Insert a routine_run row sealed to the current workspace."""

    workspace_id = ctx.require_scoped_workspace()
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
            status, edit_pct, routine_version, skill_version, schema_version,
            source_version, approved_by, workspace_hmac, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        f"SELECT {ROUTINE_RUN_COLUMNS} FROM routine_run WHERE id = ? AND workspace_id = ?",
        (run_id, workspace_id),
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

    workspace_id = ctx.require_scoped_workspace()
    seal_id = workspace_seal_id(ctx, conn)
    existing = conn.execute(
        f"""
        SELECT {ROUTINE_RUN_COLUMNS}
        FROM routine_run
        WHERE id = ? AND workspace_id = ?
        """,
        (run_id, workspace_id),
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
        WHERE id = ? AND workspace_id = ?
        """,
        (
            output_json_str,
            json.dumps(evidence_json, ensure_ascii=False),
            status,
            edit_pct,
            hmac,
            run_id,
            workspace_id,
        ),
    )
    if cursor.rowcount == 0:
        return None
    return get_routine_run(ctx, conn, run_id)


def get_routine_run(
    ctx: Context, conn: sqlite3.Connection, run_id: str
) -> dict[str, Any] | None:
    """Read a routine_run row and verify its workspace HMAC seal."""

    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        f"""
        SELECT {ROUTINE_RUN_COLUMNS}
        FROM routine_run
        WHERE id = ? AND workspace_id = ?
        """,
        (run_id, workspace_id),
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

    workspace_id = ctx.require_scoped_workspace()
    sql = f"SELECT {ROUTINE_RUN_COLUMNS} FROM routine_run WHERE workspace_id = ?"
    params: list[Any] = [workspace_id]
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
    draft_id,
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
) -> dict[str, Any]:
    """Insert a mail_message row scoped to the current workspace.

    Uses an upsert so repeated IMAP syncs do not crash on the
    UNIQUE(workspace_id, account, mail_uid) constraint.
    """

    workspace_id = ctx.require_scoped_workspace()
    now = utc_now()

    existing = conn.execute(
        f"""
        SELECT {MAIL_MESSAGE_COLUMNS}
        FROM mail_message
        WHERE workspace_id = ? AND account = ? AND mail_uid = ? AND tenant_id IS ?
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
            draft_id,
            schema_version,
            source_version,
            approved_by,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            None,
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
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
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
    workspace_id = ctx.require_scoped_workspace()
    rows = conn.execute(
        f"""
        SELECT {MAIL_MESSAGE_COLUMNS}
        FROM mail_message
        WHERE workspace_id = ? AND tenant_id IS ?
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
    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        f"""
        SELECT {MAIL_MESSAGE_COLUMNS}
        FROM mail_message
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
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
    workspace_id = ctx.require_scoped_workspace()
    with transaction(conn):
        conn.execute(
            """
            UPDATE mail_message
            SET status = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
            """,
            (status, utc_now(), mail_id, workspace_id, ctx.tenant_id),
        )
    row = conn.execute(
        f"""
        SELECT {MAIL_MESSAGE_COLUMNS}
        FROM mail_message
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
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
    workspace_id = ctx.require_scoped_workspace()
    with transaction(conn):
        conn.execute(
            """
            UPDATE mail_message
            SET draft_id = ?, status = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
            """,
            (draft_id, status, utc_now(), mail_id, workspace_id, ctx.tenant_id),
        )
    row = conn.execute(
        f"""
        SELECT {MAIL_MESSAGE_COLUMNS}
        FROM mail_message
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
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
    routine_id,
    run_id,
    edit_pct,
    input_json,
    output_json,
    learned_output_json,
    approved,
    used,
    schema_version,
    source_version,
    approved_by,
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
) -> dict[str, Any]:
    """Insert a routine scoped to the current workspace."""

    workspace_id = ctx.require_scoped_workspace()
    routine_id = new_id("rtn")
    now = utc_now()

    conn.execute(
        f"""
        INSERT INTO routine (
            id, workspace_id, tenant_id, user_id, actor_id,
            actor_role_at_decision, name, skill_md, tools_allowlist,
            schema_output_json, preset_id, trigger_json, persona_md,
            is_active, routine_version, skill_version, schema_version,
            source_version, approved_by, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            None,
            None,
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
        WHERE id = ? AND workspace_id = ?
        """,
        (routine_id, workspace_id),
    ).fetchone()
    assert row is not None
    return row_to_dict(row)


def _upsert_gold_candidate_from_run(
    ctx: Context,
    conn: sqlite3.Connection,
    run: dict[str, Any],
) -> None:
    """Create a gold_candidate row when a run is approved with low edit_pct."""

    edit_pct = run.get("edit_pct")
    if edit_pct is None or edit_pct > 0.2:
        return

    candidate_id = new_id("gold")
    now = utc_now()
    conn.execute(
        """
        INSERT INTO gold_candidate (
            id, workspace_id, routine_id, run_id, edit_pct,
            input_json, output_json, learned_output_json, approved,
            schema_version, source_version, approved_by, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(run_id) DO UPDATE SET
            edit_pct = excluded.edit_pct,
            input_json = excluded.input_json,
            output_json = excluded.output_json,
            updated_at = excluded.updated_at
        """,
        (
            candidate_id,
            run["workspace_id"],
            run["routine_id"],
            run["id"],
            edit_pct,
            run["input_json"],
            run["output_json"],
            json.dumps({}, ensure_ascii=False),
            0,
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

    with transaction(conn):
        cursor = conn.execute(
            """
            UPDATE routine_run
            SET output_json = ?, edit_pct = ?, status = ?, approved_by = ?, source_version = ?, workspace_hmac = ?
            WHERE id = ? AND workspace_id = ?
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
        WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
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

    workspace_id = ctx.require_scoped_workspace()
    approved_by = approved_by or ctx.resolved_actor_id()
    source_version = "v1"

    existing = get_routine_run(ctx, conn, run_id)
    if existing is None:
        return None

    with transaction(conn):
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
            WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
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

    workspace_id = ctx.require_scoped_workspace()
    source_version = "v1"

    existing = get_routine_run(ctx, conn, run_id)
    if existing is None:
        return None

    with transaction(conn):
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
            WHERE id = ? AND workspace_id = ? AND tenant_id IS ?
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
        WHERE id = ? AND workspace_id = ? AND approved_by IS NULL
        """,
        (approved_by, utc_now(), routine_id, workspace_id),
    )
    if cursor.rowcount == 0:
        return None
    return get_routine(ctx, conn, routine_id)


def get_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    routine_id: str,
) -> dict[str, Any] | None:
    """Read a routine scoped to the current workspace."""

    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        f"""
        SELECT {ROUTINE_COLUMNS}
        FROM routine
        WHERE id = ? AND workspace_id = ?
        """,
        (routine_id, workspace_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def get_routine_by_name(
    ctx: Context,
    conn: sqlite3.Connection,
    name: str,
) -> dict[str, Any] | None:
    """Read a routine by name (case-insensitive) in the current workspace."""

    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        f"""
        SELECT {ROUTINE_COLUMNS}
        FROM routine
        WHERE workspace_id = ? AND lower(name) = lower(?)
        """,
        (workspace_id, name),
    ).fetchone()
    return row_to_dict(row) if row else None


def list_routines(
    ctx: Context,
    conn: sqlite3.Connection,
) -> list[dict[str, Any]]:
    """List routines scoped to the current workspace."""

    workspace_id = ctx.require_scoped_workspace()
    rows = conn.execute(
        f"""
        SELECT {ROUTINE_COLUMNS}
        FROM routine
        WHERE workspace_id = ?
        ORDER BY created_at DESC
        """,
        (workspace_id,),
    ).fetchall()
    return [row_to_dict(row) for row in rows]


def delete_routine(
    ctx: Context,
    conn: sqlite3.Connection,
    routine_id: str,
) -> bool:
    """Delete a routine scoped to the current workspace."""

    workspace_id = ctx.require_scoped_workspace()
    cursor = conn.execute(
        "DELETE FROM routine WHERE id = ? AND workspace_id = ?",
        (routine_id, workspace_id),
    )
    return cursor.rowcount > 0



def get_mail_outbox(
    ctx: Context,
    conn: sqlite3.Connection,
    mail_id: str,
) -> dict[str, Any] | None:
    """Return the outbox row for a mail message if one exists."""

    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        """
        SELECT id, workspace_id, mail_id, idempotency_key, status,
               smtp_message_id, created_at, updated_at
        FROM mail_outbox
        WHERE workspace_id = ? AND mail_id = ?
        """,
        (workspace_id, mail_id),
    ).fetchone()
    return row_to_dict(row) if row else None


def get_mail_outbox_by_key(
    ctx: Context,
    conn: sqlite3.Connection,
    idempotency_key: str,
) -> dict[str, Any] | None:
    """Return an outbox row by idempotency key."""

    workspace_id = ctx.require_scoped_workspace()
    row = conn.execute(
        """
        SELECT id, workspace_id, mail_id, idempotency_key, status,
               smtp_message_id, created_at, updated_at
        FROM mail_outbox
        WHERE workspace_id = ? AND idempotency_key = ?
        """,
        (workspace_id, idempotency_key),
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
            id, workspace_id, mail_id, idempotency_key, status,
            smtp_message_id, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (outbox_id, workspace_id, mail_id, idempotency_key, status, None, now, now),
    )
    row = conn.execute(
        """
        SELECT id, workspace_id, mail_id, idempotency_key, status,
               smtp_message_id, created_at, updated_at
        FROM mail_outbox
        WHERE id = ? AND workspace_id = ?
        """,
        (outbox_id, workspace_id),
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
) -> dict[str, Any] | None:
    """Update outbox status after SMTP attempt."""

    workspace_id = ctx.require_scoped_workspace()
    with transaction(conn):
        conn.execute(
            """
            UPDATE mail_outbox
            SET status = ?, smtp_message_id = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ?
            """,
            (status, smtp_message_id, utc_now(), outbox_id, workspace_id),
        )
    row = conn.execute(
        """
        SELECT id, workspace_id, mail_id, idempotency_key, status,
               smtp_message_id, created_at, updated_at
        FROM mail_outbox
        WHERE id = ? AND workspace_id = ?
        """,
        (outbox_id, workspace_id),
    ).fetchone()
    return row_to_dict(row) if row else None
