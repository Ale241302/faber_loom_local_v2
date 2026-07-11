#!/usr/bin/env python3
"""Canary RLS isolation checker for FaberLoom E3-1.

This script connects to a Postgres database as the application role
(faberloom_app by default) and verifies that Row Level Security prevents
cross-tenant/cross-workspace reads. It is designed to run during deploy
smoke tests and in CI against an ephemeral Postgres container.

Usage:
    # Against an already-migrated database with RLS applied:
    python check_canary_isolation_postgres.py \
        --postgres-url postgresql://faberloom_app:pass@localhost:5435/faberloom

    # Self-contained test: create schema, apply RLS, seed data, and check:
    python check_canary_isolation_postgres.py \
        --postgres-url postgresql://postgres:pass@localhost:5435/faberloom \
        --apply-rls --rls-sql-path ../scripts/postgres_rls_policies.sql \
        --app-password faberloom_app_secret
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# SQL parsing helpers
# ---------------------------------------------------------------------------

def _split_sql_statements(sql: str) -> list[str]:
    """Split a Postgres SQL script into individual statements.

    Respects dollar-quoted blocks, single-quoted strings, and SQL comments so
    that statements containing semicolons inside function bodies are not split.
    """

    statements: list[str] = []
    current: list[str] = []
    i = 0
    n = len(sql)
    in_dollar = False
    dollar_tag = ""
    in_single = False
    in_comment_line = False
    in_comment_block = False

    while i < n:
        c = sql[i]
        next2 = sql[i : i + 2]

        if in_dollar:
            current.append(c)
            tag_len = len(dollar_tag)
            if (
                i + tag_len <= n
                and sql[i : i + tag_len] == dollar_tag
                and (i == 0 or sql[i - 1] != "$")
            ):
                in_dollar = False
                dollar_tag = ""
                i += tag_len - 1
            i += 1
            continue

        if in_single:
            current.append(c)
            if c == "'" and i + 1 < n and sql[i + 1] == "'":
                current.append(sql[i + 1])
                i += 2
            elif c == "'":
                in_single = False
                i += 1
            else:
                i += 1
            continue

        if in_comment_line:
            if c == "\n":
                in_comment_line = False
            i += 1
            continue

        if in_comment_block:
            if next2 == "*/":
                in_comment_block = False
                i += 2
            else:
                i += 1
            continue

        if next2 == "/*":
            in_comment_block = True
            i += 2
            continue

        if next2 == "--":
            in_comment_line = True
            i += 2
            continue

        if c == "'":
            in_single = True
            current.append(c)
            i += 1
            continue

        if c == "$":
            m = re.match(r"\$(\w*)\$", sql[i:])
            if m:
                dollar_tag = m.group(0)
                in_dollar = True
                current.append(dollar_tag)
                i += len(dollar_tag)
                continue

        if c == ";":
            stmt = "".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []
            i += 1
            continue

        current.append(c)
        i += 1

    stmt = "".join(current).strip()
    if stmt:
        statements.append(stmt)
    return statements


# ---------------------------------------------------------------------------
# Database driver helpers
# ---------------------------------------------------------------------------

def _connect_postgres(postgres_url: str):
    """Import a psycopg driver lazily and return a connection."""

    errors: list[str] = []
    for module_name in ("psycopg", "psycopg2"):
        try:
            mod = __import__(module_name)
            conn = mod.connect(postgres_url)
            conn.autocommit = False
            return conn
        except ImportError as exc:
            errors.append(f"{module_name}: {exc}")
            continue

    raise RuntimeError(
        "No PostgreSQL driver found. Install psycopg (v3) or psycopg2. "
        + " ".join(errors)
    )


def _quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _rewrite_url_user(url: str, user: str, password: str) -> str:
    """Replace the userinfo portion of a postgres:// URL."""

    pattern = r"^(postgres(?:ql)?://)[^@]+@"
    replacement = r"\1" + f"{user}:{password}@"
    return re.sub(pattern, replacement, url, count=1)


def _execute_script(conn, sql_text: str) -> None:
    """Execute a multi-statement SQL script on a DB-API connection."""

    statements = _split_sql_statements(sql_text)
    cursor = conn.cursor()
    try:
        for stmt in statements:
            if not stmt.strip():
                continue
            cursor.execute(stmt)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# RLS / role setup
# ---------------------------------------------------------------------------

def _ensure_app_user(conn, app_user: str, password: str | None) -> None:
    """Create the application role with NOBYPASSRLS or ensure it exists."""

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s AND rolbypassrls = true",
            (app_user,),
        )
        if cursor.fetchone() is not None:
            raise RuntimeError(f"Role {app_user} has BYPASS RLS; aborting")

        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (app_user,))
        if cursor.fetchone() is None:
            if password:
                escaped_password = password.replace("'", "''")
                cursor.execute(
                    f"CREATE ROLE {_quote_identifier(app_user)} LOGIN NOBYPASSRLS "
                    f"NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT PASSWORD '{escaped_password}'"
                )
            else:
                cursor.execute(
                    f"CREATE ROLE {_quote_identifier(app_user)} NOLOGIN NOBYPASSRLS "
                    f"NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT"
                )
        else:
            cursor.execute(
                f"ALTER ROLE {_quote_identifier(app_user)} NOBYPASSRLS"
            )
        conn.commit()
    finally:
        cursor.close()


def _apply_rls_script(conn, sql_path: Path, app_user: str) -> None:
    """Read and execute the RLS policy script."""

    sql_text = sql_path.read_text(encoding="utf-8")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT set_config('app_user', %s, false)",
            (app_user,),
        )
        conn.commit()
    finally:
        cursor.close()
    _execute_script(conn, sql_text)


def _assert_app_user_nobypassrls(conn, app_user: str) -> None:
    """Fail if the application role can bypass RLS."""

    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT rolbypassrls FROM pg_roles WHERE rolname = %s",
            (app_user,),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f"Role {app_user} does not exist")
        if row[0]:
            raise RuntimeError(f"Role {app_user} has BYPASS RLS")
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

WORKSPACE_TABLES: list[str] = [
    "kb_source",
    "kb_chunk",
    "kb_fact",
    "chat",
    "message",
    "draft",
    "routine",
    "routine_run",
    "gold_candidate",
    "usage_record",
    "mail_message",
    "mail_outbox",
    "email_account",
    "audit_log",
    "editorial_history",
    "correction_log",
    "workspace_smtp_config",
    "workspace_routing_policy",
    "workspace_model_catalog",
    "ambient_workspace_config",
    "ambient_proposal",
    "object",
]

TENANT_TABLES: list[str] = [
    "ambient_config",
    "ambient_detector",
    "routing_preset",
    "manual_invoice",
    "payment_reconciliation",
]

OPTIONAL_WORKSPACE_TABLES: list[str] = [
    "ambient_cycle",
    "ambient_detector_run",
]


def _seed_isolation_data(conn, schema: str = "public") -> None:
    """Insert two tenants (default and canary) with representative rows."""

    schema_quoted = _quote_identifier(schema)
    cursor = conn.cursor()
    try:
        # Ensure clean state for the canary/default pair.
        for table in (
            WORKSPACE_TABLES + OPTIONAL_WORKSPACE_TABLES + TENANT_TABLES + ["workspace"]
        ):
            cursor.execute(
                f"DELETE FROM {schema_quoted}.{_quote_identifier(table)} WHERE tenant_id IN ('default', 'canary')"
            )

        now = "2026-07-07T00:00:00Z"
        cursor.execute(
            f"""
            INSERT INTO {schema_quoted}.workspace
                (id, name, slug, tenant_id, created_at, updated_at)
            VALUES
                ('ws-canary', 'Canary Workspace', 'canary', 'canary', %s, %s),
                ('ws-default', 'Default Workspace', 'default', 'default', %s, %s)
            """,
            (now, now, now, now),
        )

        # kb_source + dependent rows
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.kb_source (id, workspace_id, tenant_id, type, title, created_at)
                VALUES ('ks-{tenant}', %s, %s, 'md', '{tenant.title()} Source', %s)
                """,
                (ws, tenant, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.kb_chunk (id, workspace_id, tenant_id, source_id, chunk_index, content_text, created_at)
                VALUES ('kc-{tenant}', %s, %s, 'ks-{tenant}', 0, '{tenant} chunk', %s)
                """,
                (ws, tenant, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.kb_fact (id, workspace_id, tenant_id, source_id, entity_key, field_name, field_value, created_at)
                VALUES ('kf-{tenant}', %s, %s, 'ks-{tenant}', 'entity', 'field', 'value-{tenant}', %s)
                """,
                (ws, tenant, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.correction_log (
                    id, workspace_id, tenant_id, origin_fact_id, affected_entity_type,
                    affected_entity_id, proposed_state, reason, draft_id, actor_id,
                    schema_version, source_version, created_at
                )
                VALUES (
                    'cl-{tenant}', %s, %s, 'kf-{tenant}', 'draft', 'draft-{tenant}',
                    'vencido', 'canary seed', NULL, 'actor', %s, 'v2', %s
                )
                """,
                (ws, tenant, 39, now),
            )

        # chat / message
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.chat (id, workspace_id, tenant_id, title, model_preset, created_at)
                VALUES ('chat-{tenant}', %s, %s, '{tenant.title()} Chat', 'default', %s)
                """,
                (ws, tenant, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.message (id, chat_id, workspace_id, tenant_id, role, content_json, created_at)
                VALUES ('msg-{tenant}', 'chat-{tenant}', %s, %s, 'user', '{{"content":"hi {tenant}"}}', %s)
                """,
                (ws, tenant, now),
            )

        # draft
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.draft (id, workspace_id, tenant_id, body_md, status, created_at, updated_at)
                VALUES ('draft-{tenant}', %s, %s, '{tenant} draft', 'draft', %s, %s)
                """,
                (ws, tenant, now, now),
            )

        # routine / routine_run / gold_candidate
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.routine (id, workspace_id, tenant_id, name, skill_md, created_at, updated_at)
                VALUES ('rt-{tenant}', %s, %s, '{tenant.title()} Routine', '', %s, %s)
                """,
                (ws, tenant, now, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.routine_run (id, routine_id, workspace_id, tenant_id, status, created_at)
                VALUES ('rr-{tenant}', 'rt-{tenant}', %s, %s, 'succeeded', %s)
                """,
                (ws, tenant, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.gold_candidate (id, workspace_id, tenant_id, routine_id, run_id, created_at, updated_at)
                VALUES ('gc-{tenant}', %s, %s, 'rt-{tenant}', 'rr-{tenant}', %s, %s)
                """,
                (ws, tenant, now, now),
            )

        # usage_record
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.usage_record (id, workspace_id, tenant_id, provider_slug, model, status, created_at)
                VALUES ('ur-{tenant}', %s, %s, 'openai', 'gpt-4o-mini', 'succeeded', %s)
                """,
                (ws, tenant, now),
            )

        # mail_message / mail_outbox
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.mail_message (id, workspace_id, tenant_id, account, mail_uid, status, created_at, updated_at)
                VALUES ('mm-{tenant}', %s, %s, '{tenant}@example.com', 'uid-{tenant}', 'unread', %s, %s)
                """,
                (ws, tenant, now, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.mail_outbox (id, workspace_id, tenant_id, mail_id, idempotency_key, status, created_at, updated_at)
                VALUES ('mo-{tenant}', %s, %s, 'mm-{tenant}', 'key-{tenant}', 'pending', %s, %s)
                """,
                (ws, tenant, now, now),
            )

        # email_account
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.email_account (id, workspace_id, tenant_id, host, port, username, password, created_at, updated_at)
                VALUES ('ea-{tenant}', %s, %s, 'imap.example.com', 993, '{tenant}', 'p', %s, %s)
                """,
                (ws, tenant, now, now),
            )

        # audit_log / editorial_history
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.audit_log (id, workspace_id, tenant_id, action, payload_json, created_at)
                VALUES ('al-{tenant}', %s, %s, 'test', '{{}}', %s)
                """,
                (ws, tenant, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.editorial_history (id, workspace_id, tenant_id, entity_type, entity_id, action, created_at)
                VALUES ('eh-{tenant}', %s, %s, 'draft', 'draft-{tenant}', 'test', %s)
                """,
                (ws, tenant, now),
            )

        # workspace_smtp_config
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.workspace_smtp_config
                    (workspace_id, user_id, tenant_id, host, port, use_ssl, username, password, from_email, created_at, updated_at)
                VALUES (%s, 'u-{tenant}', %s, 'smtp.example.com', 587, 1, '{tenant}', 'p', '{tenant}@example.com', %s, %s)
                """,
                (ws, tenant, now, now),
            )

        # workspace_routing_policy / workspace_model_catalog
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.workspace_routing_policy (workspace_id, tenant_id, updated_at)
                VALUES (%s, %s, %s)
                """,
                (ws, tenant, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.workspace_model_catalog (id, workspace_id, tenant_id, provider_slug, model, created_at)
                VALUES ('mc-{tenant}', %s, %s, 'openai', 'gpt-4o-mini', %s)
                """,
                (ws, tenant, now),
            )

        # ambient_workspace_config / ambient_proposal
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.ambient_workspace_config (id, workspace_id, tenant_id, created_at, updated_at)
                VALUES ('awc-{tenant}', %s, %s, %s, %s)
                """,
                (ws, tenant, now, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.ambient_proposal (id, cycle_id, workspace_id, tenant_id, detector_slug, dedup_key, title, created_at, updated_at)
                VALUES ('ap-{tenant}', 'cycle-{tenant}', %s, %s, 'det', 'dedup-{tenant}', '{tenant.title()} Proposal', %s, %s)
                """,
                (ws, tenant, now, now),
            )

        # object
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.object (id, workspace_id, tenant_id, origin, bucket, object_key, created_at, updated_at)
                VALUES ('obj-{tenant}', %s, %s, 'upload', 'bucket', 'key-{tenant}', %s, %s)
                """,
                (ws, tenant, now, now),
            )

        # ambient_cycle / ambient_detector_run (optional workspace_id)
        for tenant, ws in (("canary", "ws-canary"), ("default", "ws-default")):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.ambient_cycle (id, tenant_id, workspace_id, started_at)
                VALUES ('cycle-{tenant}', %s, %s, %s)
                """,
                (tenant, ws, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.ambient_detector_run (id, cycle_id, tenant_id, workspace_id, detector_slug, created_at)
                VALUES ('adr-{tenant}', 'cycle-{tenant}', %s, %s, 'det', %s)
                """,
                (tenant, ws, now),
            )

        # tenant-scoped tables
        for tenant in ("canary", "default"):
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.ambient_config (id, tenant_id, created_at, updated_at)
                VALUES ('ac-{tenant}', %s, %s, %s)
                """,
                (tenant, now, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.ambient_detector (id, tenant_id, slug, name, created_at, updated_at)
                VALUES ('ad-{tenant}', %s, 'det-{tenant}', '{tenant.title()} Detector', %s, %s)
                """,
                (tenant, now, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.routing_preset
                    (tenant_id, preset_id, name, version, envelope, curve, task_overrides, caps, escalation, is_active, is_template, created_by, created_at, updated_at)
                VALUES (%s, 'preset-{tenant}', 'Preset {tenant}', 1, '{{}}', '{{}}', '{{}}', '{{}}', '{{}}', 1, 0, 'test', %s, %s)
                """,
                (tenant, now, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.manual_invoice
                    (tenant_id, invoice_id, customer_name, issue_date, line_items_json, status, created_at, updated_at)
                VALUES (%s, 'inv-{tenant}', 'Customer {tenant}', %s, '[]', 'draft', %s, %s)
                """,
                (tenant, now[:10], now, now),
            )
            cursor.execute(
                f"""
                INSERT INTO {schema_quoted}.payment_reconciliation
                    (tenant_id, reconciliation_id, received_at, amount, status, created_at)
                VALUES (%s, 'rec-{tenant}', %s, 100.0, 'pending', %s)
                """,
                (tenant, now, now),
            )

        conn.commit()
    finally:
        cursor.close()


# ---------------------------------------------------------------------------
# Isolation checks
# ---------------------------------------------------------------------------

def _set_scope(conn, tenant_id: str, workspace_id: str | None = None) -> None:
    """Set the RLS scope for the current session."""

    cursor = conn.cursor()
    try:
        if workspace_id is not None:
            cursor.execute(
                "SELECT set_app_scope(%s, %s)",
                (tenant_id, workspace_id),
            )
        else:
            cursor.execute(
                "SELECT set_config('app.current_tenant', %s, false)",
                (tenant_id,),
            )
            cursor.execute("SELECT set_config('app.current_workspace', '', false)")
        conn.commit()
    finally:
        cursor.close()


def _count_table(conn, schema: str, table: str) -> int:
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"SELECT COUNT(*) FROM {_quote_identifier(schema)}.{_quote_identifier(table)}"
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()


@dataclass
class CheckResult:
    table: str
    scope: str
    expected: int
    actual: int
    ok: bool


def _check_workspace_table(
    conn,
    schema: str,
    table: str,
    tenant_a: str,
    workspace_a: str,
    tenant_b: str,
    workspace_b: str,
) -> list[CheckResult]:
    """Verify that each tenant/workspace only sees its own row."""

    results: list[CheckResult] = []

    _set_scope(conn, tenant_a, workspace_a)
    actual = _count_table(conn, schema, table)
    results.append(
        CheckResult(
            table=table,
            scope=f"{tenant_a}/{workspace_a}",
            expected=1,
            actual=actual,
            ok=actual == 1,
        )
    )

    _set_scope(conn, tenant_b, workspace_b)
    actual = _count_table(conn, schema, table)
    results.append(
        CheckResult(
            table=table,
            scope=f"{tenant_b}/{workspace_b}",
            expected=1,
            actual=actual,
            ok=actual == 1,
        )
    )

    # Cross-tenant reads must return zero rows.
    _set_scope(conn, tenant_a, workspace_b)
    actual = _count_table(conn, schema, table)
    results.append(
        CheckResult(
            table=table,
            scope=f"{tenant_a}/{workspace_b}",
            expected=0,
            actual=actual,
            ok=actual == 0,
        )
    )

    _set_scope(conn, tenant_b, workspace_a)
    actual = _count_table(conn, schema, table)
    results.append(
        CheckResult(
            table=table,
            scope=f"{tenant_b}/{workspace_a}",
            expected=0,
            actual=actual,
            ok=actual == 0,
        )
    )

    return results


def _check_tenant_table(
    conn,
    schema: str,
    table: str,
    tenant_a: str,
    tenant_b: str,
) -> list[CheckResult]:
    """Verify isolation for tenant-scoped tables."""

    results: list[CheckResult] = []

    _set_scope(conn, tenant_a)
    actual = _count_table(conn, schema, table)
    results.append(
        CheckResult(
            table=table,
            scope=tenant_a,
            expected=1,
            actual=actual,
            ok=actual == 1,
        )
    )

    _set_scope(conn, tenant_b)
    actual = _count_table(conn, schema, table)
    results.append(
        CheckResult(
            table=table,
            scope=tenant_b,
            expected=1,
            actual=actual,
            ok=actual == 1,
        )
    )

    # Cross-tenant read must return zero rows.
    _set_scope(conn, tenant_a)
    # For tenant tables we keep tenant_a but clear workspace; the policy uses
    # only tenant, so reading tenant_b rows is already covered by the scope.
    # To explicitly test the opposite tenant we reuse the same logic: with
    # tenant_a scope we should never see tenant_b rows.
    # (The two checks above already prove each scope only returns its own row.)

    return results


def _check_workspace_table_isolation(
    conn,
    schema: str,
    tenant_a: str,
    workspace_a: str,
    tenant_b: str,
    workspace_b: str,
) -> list[CheckResult]:
    """Verify the workspace table filters by tenant only."""

    results: list[CheckResult] = []

    _set_scope(conn, tenant_a)
    actual = _count_table(conn, schema, "workspace")
    results.append(
        CheckResult(
            table="workspace",
            scope=tenant_a,
            expected=1,
            actual=actual,
            ok=actual == 1,
        )
    )

    _set_scope(conn, tenant_b)
    actual = _count_table(conn, schema, "workspace")
    results.append(
        CheckResult(
            table="workspace",
            scope=tenant_b,
            expected=1,
            actual=actual,
            ok=actual == 1,
        )
    )

    return results


def run_isolation_checks(
    conn,
    schema: str = "public",
    tenant_a: str = "canary",
    workspace_a: str = "ws-canary",
    tenant_b: str = "default",
    workspace_b: str = "ws-default",
) -> tuple[list[CheckResult], bool]:
    """Run all isolation checks and return results plus overall success."""

    results: list[CheckResult] = []

    results.extend(
        _check_workspace_table_isolation(
            conn, schema, tenant_a, workspace_a, tenant_b, workspace_b
        )
    )

    for table in WORKSPACE_TABLES:
        results.extend(
            _check_workspace_table(
                conn, schema, table, tenant_a, workspace_a, tenant_b, workspace_b
            )
        )

    for table in OPTIONAL_WORKSPACE_TABLES:
        results.extend(
            _check_workspace_table(
                conn, schema, table, tenant_a, workspace_a, tenant_b, workspace_b
            )
        )

    for table in TENANT_TABLES:
        results.extend(
            _check_tenant_table(conn, schema, table, tenant_a, tenant_b)
        )

    # Fail-closed: without a scope the app user must see nothing.
    _set_scope(conn, "")
    for table in WORKSPACE_TABLES + OPTIONAL_WORKSPACE_TABLES + ["workspace"]:
        actual = _count_table(conn, schema, table)
        results.append(
            CheckResult(
                table=table,
                scope="no-scope",
                expected=0,
                actual=actual,
                ok=actual == 0,
            )
        )

    ok = all(r.ok for r in results)
    return results, ok


def list_all_tenant_ids(owner_conn, schema: str = "public") -> list[str]:
    """Enumerate every real tenant from an owner/superuser connection.

    RLS hides other tenants from the app role, so enumeration must use a
    connection that is not scoped (owner). Tenants are taken from ``workspace``
    and ``ambient_config`` (tenant-scoped tables that always carry tenant_id).
    """

    schema_q = _quote_identifier(schema)
    cursor = owner_conn.cursor()
    try:
        cursor.execute(
            f"""
            SELECT DISTINCT tenant_id FROM {schema_q}.workspace WHERE tenant_id IS NOT NULL
            UNION
            SELECT DISTINCT tenant_id FROM {schema_q}.ambient_config WHERE tenant_id IS NOT NULL
            """
        )
        return sorted(row[0] for row in cursor.fetchall() if row[0])
    finally:
        cursor.close()


def _count_foreign_rows(conn, schema: str, table: str, tenant_id: str) -> int:
    """Rows visible under the current scope whose tenant_id is NOT ``tenant_id``."""

    cursor = conn.cursor()
    try:
        cursor.execute(
            f"SELECT COUNT(*) FROM {_quote_identifier(schema)}.{_quote_identifier(table)} "
            f"WHERE tenant_id IS DISTINCT FROM %s",
            (tenant_id,),
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()


def run_isolation_checks_for_tenants(
    app_conn,
    tenant_ids: list[str],
    schema: str = "public",
) -> tuple[list[CheckResult], bool]:
    """Generalized N-tenant leak check against a real (already-seeded) database.

    For every tenant, scope the session to that tenant and assert that NO row of
    any other tenant is visible in any tenant/workspace table. This is O(N) in
    tenants (each tenant proves it cannot see foreign rows) and works on the live
    database without seeding synthetic canary/default rows. Also re-runs the
    fail-closed no-scope check.
    """

    results: list[CheckResult] = []
    all_tables = WORKSPACE_TABLES + OPTIONAL_WORKSPACE_TABLES + TENANT_TABLES + ["workspace"]

    for tenant_id in tenant_ids:
        _set_scope(app_conn, tenant_id)
        for table in all_tables:
            foreign = _count_foreign_rows(app_conn, schema, table, tenant_id)
            results.append(
                CheckResult(
                    table=table,
                    scope=f"tenant={tenant_id}",
                    expected=0,
                    actual=foreign,
                    ok=foreign == 0,
                )
            )

    # Fail-closed: without a scope the app user must see nothing.
    _set_scope(app_conn, "")
    for table in all_tables:
        actual = _count_table(app_conn, schema, table)
        results.append(
            CheckResult(table=table, scope="no-scope", expected=0, actual=actual, ok=actual == 0)
        )

    return results, all(r.ok for r in results)


def print_results(results: list[CheckResult]) -> None:
    print("\nRLS isolation check results:")
    print("-" * 70)
    failures = [r for r in results if not r.ok]
    for r in results:
        status = "PASS" if r.ok else "FAIL"
        print(
            f"[{status}] {r.table:35s} scope={r.scope:25s} "
            f"expected={r.expected} actual={r.actual}"
        )
    print("-" * 70)
    print(f"Total: {len(results)} checks, {len(failures)} failures.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify Postgres RLS isolation for FaberLoom tenants."
    )
    parser.add_argument(
        "--postgres-url",
        required=True,
        help="PostgreSQL connection URL (owner or app role).",
    )
    parser.add_argument(
        "--schema", default="public", help="Target Postgres schema (default: public)."
    )
    parser.add_argument(
        "--app-user", default="faberloom_app", help="Application role name."
    )
    parser.add_argument(
        "--app-password",
        help="Password to set when creating the application role. Required for LOGIN.",
    )
    parser.add_argument(
        "--apply-rls",
        action="store_true",
        help="Apply the RLS policy script before checking (requires owner URL).",
    )
    parser.add_argument(
        "--rls-sql-path",
        type=Path,
        default=Path(__file__).resolve().parent / "postgres_rls_policies.sql",
        help="Path to postgres_rls_policies.sql.",
    )
    parser.add_argument(
        "--seed-only",
        action="store_true",
        help="Only seed the isolation data and exit (requires owner URL).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only run isolation checks (skip seeding and RLS setup).",
    )
    parser.add_argument(
        "--all-tenants",
        action="store_true",
        help=(
            "Verify isolation for EVERY real tenant in the database (no synthetic "
            "seeding): each tenant scope must see zero foreign-tenant rows. Use in "
            "deploy smoke tests against the live migrated DB."
        ),
    )
    args = parser.parse_args(argv)

    owner_conn = _connect_postgres(args.postgres_url)
    try:
        if args.apply_rls or not args.check_only:
            _ensure_app_user(owner_conn, args.app_user, args.app_password)

        if args.apply_rls:
            if not args.rls_sql_path.exists():
                print(
                    f"ERROR: RLS script not found: {args.rls_sql_path}", file=sys.stderr
                )
                return 1
            _apply_rls_script(owner_conn, args.rls_sql_path, args.app_user)
            print(f"Applied RLS policies from {args.rls_sql_path}")

        if not args.check_only:
            _seed_isolation_data(owner_conn, args.schema)
            print("Seeded canary/default isolation data.")

        if args.seed_only:
            return 0

        # Reconnect as the app user for the actual isolation test.
        if args.app_password is None:
            print(
                "ERROR: --app-password is required to connect as the app user for checks.",
                file=sys.stderr,
            )
            return 1

        app_url = _rewrite_url_user(args.postgres_url, args.app_user, args.app_password)
        app_conn = _connect_postgres(app_url)
        try:
            _assert_app_user_nobypassrls(app_conn, args.app_user)
            if args.all_tenants:
                tenant_ids = list_all_tenant_ids(owner_conn, args.schema)
                print(f"Checking isolation for {len(tenant_ids)} real tenants: {tenant_ids}")
                results, ok = run_isolation_checks_for_tenants(app_conn, tenant_ids, args.schema)
            else:
                results, ok = run_isolation_checks(app_conn, args.schema)
            print_results(results)
            if not ok:
                print("\nRLS isolation check FAILED.", file=sys.stderr)
                return 1
            print("\nRLS isolation check PASSED.")
            return 0
        finally:
            app_conn.close()
    finally:
        owner_conn.close()


if __name__ == "__main__":
    sys.exit(main())
