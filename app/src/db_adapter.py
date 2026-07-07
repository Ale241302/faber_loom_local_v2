"""Dual SQLite/Postgres adapter for FaberLoom E3-1.

The adapter exposes a single connection API so that the rest of the app can
keep using ``?`` placeholders, ``conn.execute()``, ``conn.executemany()`` and
``conn.executescript()`` while the runtime is switched via
``FABERLOOM_DB_ENGINE=sqlite|postgres`` (default ``sqlite``).

Design constraints from E3-1:
- No hard-coded single-engine placeholders at call sites.
- Postgres transactions set ``app.current_tenant`` / ``app.current_workspace``
  so RLS policies can filter by Context.
- SQLite behaviour is unchanged; existing tests keep passing.
"""

from __future__ import annotations

import contextlib
import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

from .context import Context


DB_ENGINE = os.environ.get("FABERLOOM_DB_ENGINE", "sqlite").lower()
_POSTGRES_URL = os.environ.get(
    "FABERLOOM_POSTGRES_URL",
    "postgresql://faberloom_app:faberloom_app@localhost:5432/faberloom",
)


if DB_ENGINE == "postgres":
    import psycopg
    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool


# -----------------------------------------------------------------------------
# SQL placeholder normalisation
# -----------------------------------------------------------------------------


def _translate_placeholders(sql: str) -> str:
    """Replace ``?`` positional placeholders with ``%s`` for psycopg3.

    The replacement is conservative: it ignores ``?`` inside string literals,
    double-quoted identifiers and SQL comments.
    """

    result: list[str] = []
    i = 0
    n = len(sql)
    state: str = "normal"  # normal | single_quote | double_quote | ident | line_comment | block_comment
    while i < n:
        ch = sql[i]
        next_ch = sql[i + 1] if i + 1 < n else ""

        if state == "normal":
            if ch == "'":
                state = "single_quote"
                result.append(ch)
            elif ch == '"':
                state = "double_quote"
                result.append(ch)
            elif ch == "-" and next_ch == "-":
                state = "line_comment"
                result.append(ch)
            elif ch == "/" and next_ch == "*":
                state = "block_comment"
                result.append(ch)
            elif ch == "?":
                result.append("%s")
            else:
                result.append(ch)
        elif state == "single_quote":
            result.append(ch)
            if ch == "'":
                if next_ch == "'":
                    result.append(next_ch)
                    i += 1
                else:
                    state = "normal"
        elif state == "double_quote":
            result.append(ch)
            if ch == '"':
                if next_ch == '"':
                    result.append(next_ch)
                    i += 1
                else:
                    state = "normal"
        elif state == "line_comment":
            result.append(ch)
            if ch == "\n":
                state = "normal"
        elif state == "block_comment":
            result.append(ch)
            if ch == "*" and next_ch == "/":
                result.append(next_ch)
                i += 1
                state = "normal"

        i += 1

    return "".join(result)


def normalize_sql(sql: str) -> str:
    """Return engine-appropriate SQL for the current adapter."""

    if DB_ENGINE == "sqlite":
        return sql
    return _translate_placeholders(sql)


# -----------------------------------------------------------------------------
# Connection wrappers
# -----------------------------------------------------------------------------


class _CursorWrapper:
    """Normalize cursor access for sqlite3/psycopg3."""

    def __init__(self, cursor: Any, engine: str):
        self._cursor = cursor
        self._engine = engine

    def __getattr__(self, name: str) -> Any:
        return getattr(self._cursor, name)

    def fetchone(self) -> Any:
        row = self._cursor.fetchone()
        if row is None:
            return None
        return _normalize_row(row, self._engine)

    def fetchall(self) -> list[Any]:
        rows = self._cursor.fetchall()
        return [_normalize_row(r, self._engine) for r in rows]

    def fetchmany(self, size: int = 0) -> list[Any]:
        rows = self._cursor.fetchmany(size)
        return [_normalize_row(r, self._engine) for r in rows]

    def __iter__(self):
        return (_normalize_row(r, self._engine) for r in self._cursor)


class _SQLiteConnectionWrapper:
    """Thin passthrough wrapper so callers see a uniform adapter interface."""

    engine = "sqlite"

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def __enter__(self):
        self._conn.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._conn.__exit__(exc_type, exc_val, exc_tb)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)

    def execute(self, sql: str, parameters: Any = ()) -> Any:
        return _CursorWrapper(self._conn.execute(sql, parameters), self.engine)

    def executemany(self, sql: str, seq: Any) -> Any:
        return _CursorWrapper(self._conn.executemany(sql, seq), self.engine)

    def executescript(self, sql: str) -> Any:
        return self._conn.executescript(sql)

    def cursor(self) -> Any:
        return _CursorWrapper(self._conn.cursor(), self.engine)

    @property
    def in_transaction(self) -> bool:
        return self._conn.in_transaction


class _PostgresConnectionWrapper:
    """psycopg3 connection wrapper exposing the same surface as sqlite3."""

    engine = "postgres"

    def __init__(self, conn: Any, pool: Any = None):
        self._conn = conn
        self._pool = pool

    def __enter__(self):
        self._conn.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._conn.__exit__(exc_type, exc_val, exc_tb)

    def _normalize_sql(self, sql: str) -> str:
        return _translate_placeholders(sql)

    def execute(self, sql: str, parameters: Any = ()) -> Any:
        cur = self._conn.cursor()
        sql = self._normalize_sql(sql)
        if parameters is None:
            parameters = ()
        cur.execute(sql, parameters)
        return _CursorWrapper(cur, self.engine)

    def executemany(self, sql: str, seq: Any) -> Any:
        cur = self._conn.cursor()
        sql = self._normalize_sql(sql)
        cur.executemany(sql, seq)
        return _CursorWrapper(cur, self.engine)

    def executescript(self, sql: str) -> Any:
        """Best-effort multi-statement execution for Postgres.

        Migrations are expected to be engine-specific; this is used for simple
        scripts only. Complex PL/pgSQL blocks should be executed through the
        dedicated migration path.
        """

        cur = self._conn.cursor()
        for statement in _split_sql_statements(sql):
            if statement.strip():
                cur.execute(statement)
        return _CursorWrapper(cur, self.engine)

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        if self._pool is not None:
            self._pool.putconn(self._conn)
        else:
            self._conn.close()

    def cursor(self) -> Any:
        return _CursorWrapper(self._conn.cursor(), self.engine)

    def _set_config_var(self, name: str, value: str) -> None:
        """Execute ``SET LOCAL name = value`` safely for RLS session variables.

        ``name`` is allow-listed because it is injected as raw SQL; ``value`` is
        escaped via psycopg3's literal encoder.
        """

        if name not in {"app.current_tenant", "app.current_workspace", "app.tenant_id"}:
            raise ValueError(f"Disallowed SET variable: {name}")
        from psycopg import sql

        query = sql.SQL("SET LOCAL {name} = {value}").format(
            name=sql.SQL(name), value=sql.Literal(value)
        )
        cur = self._conn.cursor()
        cur.execute(query)

    @property
    def in_transaction(self) -> bool:
        # psycopg3 TransactionStatus: IDLE = 0, INTRANS = 2, ACTIVE = 1
        status = self._conn.info.transaction_status
        return status not in (0,)


def _split_sql_statements(sql: str) -> list[str]:
    """Split SQL on semicolons that are not inside quotes or comments."""

    statements: list[str] = []
    buf: list[str] = []
    i = 0
    n = len(sql)
    state: str = "normal"
    while i < n:
        ch = sql[i]
        next_ch = sql[i + 1] if i + 1 < n else ""

        if state == "normal":
            if ch == "'":
                state = "single_quote"
            elif ch == '"':
                state = "double_quote"
            elif ch == "-" and next_ch == "-":
                state = "line_comment"
            elif ch == "/" and next_ch == "*":
                state = "block_comment"
            elif ch == ";":
                statements.append("".join(buf))
                buf = []
                i += 1
                continue
        elif state == "single_quote":
            if ch == "'":
                if next_ch == "'":
                    i += 1
                else:
                    state = "normal"
        elif state == "double_quote":
            if ch == '"':
                if next_ch == '"':
                    i += 1
                else:
                    state = "normal"
        elif state == "line_comment":
            if ch == "\n":
                state = "normal"
        elif state == "block_comment":
            if ch == "*" and next_ch == "/":
                i += 1
                state = "normal"

        buf.append(ch)
        i += 1

    tail = "".join(buf)
    if tail.strip():
        statements.append(tail)
    return statements


# -----------------------------------------------------------------------------
# Row normalisation
# -----------------------------------------------------------------------------


def _normalize_row(row: Any, engine: str) -> Any:
    """Return a sqlite3.Row-like object from sqlite3 or psycopg3 rows."""

    if engine == "sqlite":
        return row
    if isinstance(row, dict):
        return _DictRow(row)
    return row


class _DictRow:
    """dict-like row exposing ``row['col']`` and positional ``row[0]`` access."""

    def __init__(self, data: dict[str, Any]):
        self._data = data
        self._keys = list(data.keys())

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, int):
            return self._data[self._keys[key]]
        return self._data[key]

    def __getattr__(self, key: str) -> Any:
        try:
            return self._data[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def keys(self) -> list[str]:
        return list(self._data.keys())

    def __iter__(self):
        return iter(self._data)

    def __repr__(self) -> str:
        return f"<_DictRow {self._data!r}>"


# -----------------------------------------------------------------------------
# Connection factories
# -----------------------------------------------------------------------------


def _get_sqlite_db_path() -> str:
    from .db import get_database_path

    return str(get_database_path())


def _connect_sqlite() -> _SQLiteConnectionWrapper:
    from .db import get_database_path

    db_path = get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 5000")
    return _SQLiteConnectionWrapper(conn)


_pg_pool: Any = None


def _get_postgres_pool() -> ConnectionPool:
    global _pg_pool
    if _pg_pool is None:
        _pg_pool = ConnectionPool(
            _POSTGRES_URL,
            min_size=1,
            max_size=int(os.environ.get("FABERLOOM_POSTGRES_POOL_SIZE", "10")),
            kwargs={"row_factory": dict_row},
        )
        _pg_pool.wait()
    return _pg_pool


def _connect_postgres() -> _PostgresConnectionWrapper:
    if "psycopg" not in globals():
        raise RuntimeError(
            "FABERLOOM_DB_ENGINE=postgres requires psycopg[binary] and psycopg-pool"
        )
    pool = _get_postgres_pool()
    conn = pool.getconn()
    return _PostgresConnectionWrapper(conn, pool=pool)


def connect() -> Any:
    """Return a database connection for the configured engine."""

    if DB_ENGINE == "postgres":
        return _connect_postgres()
    return _connect_sqlite()


def is_postgres_connection(conn: Any) -> bool:
    return getattr(conn, "engine", None) == "postgres"


@contextmanager
def db_session() -> Iterator[Any]:
    """Yield a connection and close it at the end (sqlite semantics)."""

    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def transaction(conn: Any, ctx: Context | None = None) -> Iterator[None]:
    """Commit/rollback a unit of work unless already inside a transaction.

    For Postgres, the current tenant/workspace are pushed into session variables
    so that RLS policies filter correctly. ``SET LOCAL`` keeps the values scoped
    to the current transaction.
    """

    engine = getattr(conn, "engine", "sqlite")
    outer_transaction = conn.in_transaction
    try:
        if engine == "postgres" and ctx is not None:
            tenant_id = ctx.tenant_id or ""
            workspace_id = ctx.workspace_id or ""
            conn._set_config_var("app.current_tenant", tenant_id)
            conn._set_config_var("app.current_workspace", workspace_id)
            conn._set_config_var("app.tenant_id", tenant_id)
        yield
    except Exception:
        if not outer_transaction:
            conn.rollback()
        raise
    else:
        if not outer_transaction:
            conn.commit()


def row_to_dict(row: Any) -> dict[str, Any]:
    """Convert a row from either engine into a plain dict."""

    if row is None:
        return {}
    if isinstance(row, _DictRow):
        return dict(row._data)
    if isinstance(row, sqlite3.Row):
        return {key: row[key] for key in row.keys()}
    if isinstance(row, dict):
        return dict(row)
    # sqlcipher3 rows expose the same interface as sqlite3.Row but are not
    # instances of sqlite3.Row.
    if hasattr(row, "keys") and hasattr(row, "__getitem__"):
        try:
            return {key: row[key] for key in row.keys()}
        except Exception:
            pass
    return {key: getattr(row, key) for key in dir(row) if not key.startswith("_")}


# Backwards-compatible helper for callers that already receive a dict row.
Row = Any
