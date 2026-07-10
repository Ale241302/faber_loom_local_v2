"""Golden-case harvester for FaberLoom E3-6.

Captures real routine runs as candidate golden cases, then exposes a HITL
approval/verification workflow before they can be used for pack promotion.
"""

from __future__ import annotations

import json
from typing import Any

from .context import Context, enforce_tenant_scoped
from .db import db_session, new_id, row_to_dict, transaction, utc_now
from .models import SCHEMA_VERSION
from .skill_primitives import attach_evidence


def _state_clause(state: str | None) -> tuple[str, list[Any]]:
    """Return a SQL filter and params for the requested golden-case state."""

    if state == "candidate":
        return "approved = 0 AND (verified_by IS NULL OR verified_by = '')", []
    if state == "approved":
        return "approved = 1 AND (verified_by IS NULL OR verified_by = '')", []
    if state == "verified":
        return "approved = 1 AND verified_by IS NOT NULL AND verified_by != ''", []
    return "", []


def _scoped_context(ctx: Context, workspace_id: str) -> Context:
    return Context(
        workspace_id=workspace_id,
        tenant_id=ctx.tenant_id,
        user_id=ctx.user_id,
        actor_id=ctx.actor_id,
        actor_role_at_decision=ctx.actor_role_at_decision,
    )


def propose_golden_case_from_run(
    ctx: Context,
    conn: Any,
    *,
    run_id: str,
    skill_id: str,
) -> dict[str, Any]:
    """Freeze a real routine run as a candidate golden case.

    The run's input, output and evidence are copied into ``golden_case`` with
    ``approved=0`` and ``origin='dogfood'``. Existing evidence items are also
    attached to the golden case entity for auditability.
    """

    if not ctx.tenant_id:
        raise ValueError("A tenant context is required")

    with transaction(conn, ctx=ctx):
        run = conn.execute(
            """
            SELECT id, routine_id, workspace_id, input_json, output_json, evidence_json, status
            FROM routine_run
            WHERE id = ? AND tenant_id = ?
            """,
            (run_id, ctx.tenant_id),
        ).fetchone()
        if run is None:
            raise ValueError(f"Run not found: {run_id}")

        workspace_id = run["workspace_id"]
        scoped_ctx = _scoped_context(ctx, workspace_id)

        case_id = f"run-{run_id}"
        now = utc_now()

        # Upsert: a second proposal for the same run refreshes the frozen snapshot.
        conn.execute(
            """
            INSERT INTO golden_case (
                id, workspace_id, tenant_id, skill_id, case_id,
                input_json, expected_output_json, evidence_required,
                approved, approved_by, approved_at, verified_by,
                schema_version, source_version, origin, run_id, frozen_at,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, NULL, NULL, NULL, ?, 'v2', ?, ?, ?, ?, ?)
            ON CONFLICT(workspace_id, tenant_id, skill_id, case_id) DO UPDATE SET
                input_json = excluded.input_json,
                expected_output_json = excluded.expected_output_json,
                origin = excluded.origin,
                run_id = excluded.run_id,
                frozen_at = excluded.frozen_at,
                approved = 0,
                approved_by = NULL,
                approved_at = NULL,
                verified_by = NULL,
                updated_at = excluded.updated_at
            """,
            (
                new_id("gcs"),
                workspace_id,
                scoped_ctx.tenant_id,
                skill_id,
                case_id,
                run["input_json"],
                run["output_json"],
                SCHEMA_VERSION,
                "dogfood",
                run_id,
                now,
                now,
                now,
            ),
        )

        row = conn.execute(
            """
            SELECT * FROM golden_case
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ? AND case_id = ?
            """,
            (workspace_id, scoped_ctx.tenant_id, skill_id, case_id),
        ).fetchone()
        assert row is not None
        golden_case_id = row["id"]

        evidence_items = json.loads(run["evidence_json"] or "[]")
        if evidence_items:
            normalized = [_normalize_evidence(item) for item in evidence_items]
            normalized = [item for item in normalized if item]
            if normalized:
                attach_evidence(
                    scoped_ctx,
                    conn,
                    entity_type="golden_case",
                    entity_id=golden_case_id,
                    evidence_items=normalized,
                )

    return row_to_dict(row)


def list_golden_cases(
    ctx: Context,
    conn: Any = None,
    *,
    skill_id: str | None = None,
    state: str | None = None,
) -> list[dict[str, Any]]:
    """Return golden cases for the current tenant, optionally filtered."""

    if not ctx.tenant_id:
        raise ValueError("A tenant context is required")

    sql = """
        SELECT * FROM golden_case
        WHERE tenant_id = ?
    """
    params: list[Any] = [ctx.tenant_id]

    if skill_id:
        sql += " AND skill_id = ?"
        params.append(skill_id)

    state_filter, state_params = _state_clause(state)
    if state_filter:
        sql += f" AND {state_filter}"
        params.extend(state_params)

    sql += " ORDER BY created_at DESC"

    if conn is None:
        with db_session() as conn:
            rows = conn.execute(sql, params).fetchall()
    else:
        rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(row) for row in rows]


def approve_golden_case(
    ctx: Context,
    conn: Any,
    *,
    case_id: str,
    approved_by: str,
) -> dict[str, Any]:
    """Human curator approval (first gate). Sets approved=1."""

    if not ctx.tenant_id:
        raise ValueError("A tenant context is required")

    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT * FROM golden_case
            WHERE id = ? AND tenant_id = ?
            """,
            (case_id, ctx.tenant_id),
        ).fetchone()
        if row is None:
            raise ValueError(f"Golden case not found: {case_id}")

        workspace_id = row["workspace_id"]
        scoped_ctx = _scoped_context(ctx, workspace_id)

        now = utc_now()
        conn.execute(
            """
            UPDATE golden_case
            SET approved = 1, approved_by = ?, approved_at = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (approved_by, now, now, case_id, workspace_id, scoped_ctx.tenant_id),
        )

    updated = conn.execute(
        "SELECT * FROM golden_case WHERE id = ?", (case_id,)
    ).fetchone()
    return row_to_dict(updated)


def verify_golden_case(
    ctx: Context,
    conn: Any,
    *,
    case_id: str,
    verified_by: str,
) -> dict[str, Any]:
    """Independent verification (second gold gate). Sets verified_by.

    The verifier must be different from the approver (promote_pack enforces this
    as the second gate).
    """

    if not ctx.tenant_id:
        raise ValueError("A tenant context is required")

    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT * FROM golden_case
            WHERE id = ? AND tenant_id = ?
            """,
            (case_id, ctx.tenant_id),
        ).fetchone()
        if row is None:
            raise ValueError(f"Golden case not found: {case_id}")
        if not row["approved"]:
            raise ValueError("Golden case must be approved before verification")
        if row["approved_by"] == verified_by:
            raise ValueError("Verifier must be different from approver")

        workspace_id = row["workspace_id"]
        now = utc_now()
        conn.execute(
            """
            UPDATE golden_case
            SET verified_by = ?, updated_at = ?
            WHERE id = ? AND workspace_id = ? AND tenant_id = ?
            """,
            (verified_by, now, case_id, workspace_id, ctx.tenant_id),
        )

    updated = conn.execute(
        "SELECT * FROM golden_case WHERE id = ?", (case_id,)
    ).fetchone()
    return row_to_dict(updated)


def _normalize_evidence(item: Any) -> dict[str, Any] | None:
    if not isinstance(item, dict):
        return None
    source_type = str(item.get("source_type", "") or item.get("type", "")).strip()
    source_locator = str(item.get("source_locator", "") or item.get("locator", "")).strip()
    captured_at = str(item.get("captured_at", "") or item.get("timestamp", utc_now())).strip()
    if not source_type or not source_locator or not captured_at:
        return None
    return {
        "source_type": source_type,
        "source_locator": source_locator,
        "captured_at": captured_at,
        "content_text": item.get("content_text") or item.get("content"),
        "content_hash": item.get("content_hash"),
    }
