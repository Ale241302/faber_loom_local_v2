"""E4-5 — Memoria viva (CAPA 1 personal).

CAPA 1 es personal, privada y siempre con gate humano:

- El detector de patrones es read-only: nunca escribe memoria.
- Los thumbs-up/down del usuario alimentan ``message_feedback``; sólo la
  aprobación explícita de una propuesta (apply) escribe un bloque en
  ``fnd_memory_blocks``.
- La memoria se inyecta en el system prompt de completions, invocaciones de
  rutinas y pasos del orquestador, acotada por un budget de tokens y filtrada
  por usuario/tenant.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any

import sqlite3

from ..context import Context
from ..db import new_id, utc_now
from ..db_adapter import transaction
from .constants import (
    MEMORY_INJECTION_MAX_TOKENS,
    MEMORY_INJECTION_TOP_K,
    MEMORY_MAX_CANDIDATES_PER_CYCLE,
    MEMORY_NOTIFICATION_CADENCE_DAYS,
    MEMORY_PATTERN_THRESHOLD_DEFAULT,
    MEMORY_UNCONSOLIDATED_HOT,
    MEMORY_UNCONSOLIDATED_WARM,
)


# Namespace raíz para memoria personal CAPA 1.
PERSONAL_NS = "personal"
AGENT_SLUG_DEFAULT = "default"

# Vocabulario cerrado de razones de feedback (debe coincidir con la UI).
VALID_FEEDBACK_REASONS = frozenset(
    {"helpful", "wrong", "too_long", "too_short", "off_topic", "unsafe", "other"}
)

# Mensaje accionable por razón tipificada.
_REASON_SUMMARY = {
    "helpful": "Prefiere respuestas directas y centradas en lo que preguntó.",
    "wrong": "Ha señalado respuestas incorrectas; priorizar precisión y fuentes.",
    "too_long": "Suele rechazar respuestas muy largas; ser más conciso.",
    "too_short": "Suele rechazar respuestas muy cortas; dar más contexto útil.",
    "off_topic": "Suele rechazar respuestas que se desvían; mantenerse en el tema.",
    "unsafe": "Ha marcado contenido inapropiado; extremar políticas de seguridad.",
    "other": "Ha dejado feedback negativo recurrente; pedir clarificación.",
}

_NS_RE = re.compile(r"^[A-Za-z0-9_\-.]+(/[A-Za-z0-9_\-.]+)*$")
_KEY_RE = re.compile(r"^[A-Za-z0-9_\-.]+$")


def _validate_ns_key(namespace: str, key: str) -> None:
    if not _NS_RE.match(namespace or ""):
        raise ValueError("Namespace inválido (segmentos a-z0-9_-. separados por '/')")
    if not _KEY_RE.match(key or ""):
        raise ValueError("Key inválida (a-z0-9_-. sin '/')")


def _safe_namespace(namespace: str) -> str:
    return re.sub(r"[^A-Za-z0-9_\-./]", "_", namespace).strip("/")


def _user_learning_state_pk(ctx: Context) -> tuple[str, str, str, str]:
    return (
        ctx.require_tenant(),
        ctx.require_scoped_workspace(),
        ctx.user_id or "local",
        AGENT_SLUG_DEFAULT,
    )


def _ensure_user_learning_state(ctx: Context, conn: sqlite3.Connection) -> dict[str, Any]:
    tenant_id, workspace_id, user_id, agent_slug = _user_learning_state_pk(ctx)
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT * FROM user_learning_state
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND agent_slug = ?
            """,
            (tenant_id, workspace_id, user_id, agent_slug),
        ).fetchone()
        if row is not None:
            return dict(row)
        now = utc_now()
        conn.execute(
            """
            INSERT INTO user_learning_state (
                tenant_id, workspace_id, user_id, agent_slug,
                detection_threshold, notification_cadence, auto_archive_ignored_after_days,
                unconsolidated_count, last_indexed_at,
                actor_id, actor_role_at_decision, schema_version, source_version,
                approved_by, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tenant_id,
                workspace_id,
                user_id,
                agent_slug,
                MEMORY_PATTERN_THRESHOLD_DEFAULT,
                "weekly",
                30,
                0,
                None,
                ctx.actor_id,
                ctx.actor_role_at_decision,
                47,
                "v1",
                None,
                now,
                now,
            ),
        )
        return {
            "tenant_id": tenant_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "agent_slug": agent_slug,
            "detection_threshold": MEMORY_PATTERN_THRESHOLD_DEFAULT,
            "notification_cadence": "weekly",
            "auto_archive_ignored_after_days": 30,
            "unconsolidated_count": 0,
            "last_indexed_at": None,
        }


def get_learning_state(ctx: Context, conn: sqlite3.Connection) -> dict[str, Any]:
    """Return the learning thermometer state for the current user."""

    state = _ensure_user_learning_state(ctx, conn)
    count = int(state.get("unconsolidated_count") or 0)
    if count >= MEMORY_UNCONSOLIDATED_HOT:
        level = "hot"
    elif count >= MEMORY_UNCONSOLIDATED_WARM:
        level = "warm"
    else:
        level = "cool"
    return {
        "user_id": state["user_id"],
        "unconsolidated_count": count,
        "detection_threshold": int(state.get("detection_threshold") or MEMORY_PATTERN_THRESHOLD_DEFAULT),
        "notification_cadence": state.get("notification_cadence") or "weekly",
        "level": level,
        "last_indexed_at": state.get("last_indexed_at"),
    }


def increment_unconsolidated_count(ctx: Context, conn: sqlite3.Connection) -> dict[str, Any]:
    """Bump the counter of feedback events not yet consolidated into memory."""

    tenant_id, workspace_id, user_id, agent_slug = _user_learning_state_pk(ctx)
    _ensure_user_learning_state(ctx, conn)
    now = utc_now()
    with transaction(conn, ctx=ctx):
        conn.execute(
            """
            UPDATE user_learning_state
            SET unconsolidated_count = unconsolidated_count + 1,
                updated_at = ?
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND agent_slug = ?
            """,
            (now, tenant_id, workspace_id, user_id, agent_slug),
        )
    return get_learning_state(ctx, conn)


def decrement_unconsolidated_count(
    ctx: Context,
    conn: sqlite3.Connection,
    delta: int,
) -> dict[str, Any]:
    """Reduce the counter when feedback is consolidated (applied/ignored)."""

    tenant_id, workspace_id, user_id, agent_slug = _user_learning_state_pk(ctx)
    _ensure_user_learning_state(ctx, conn)
    now = utc_now()
    with transaction(conn, ctx=ctx):
        conn.execute(
            """
            UPDATE user_learning_state
            SET unconsolidated_count = MAX(0, unconsolidated_count - ?),
                updated_at = ?
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND agent_slug = ?
            """,
            (delta, now, tenant_id, workspace_id, user_id, agent_slug),
        )
    return get_learning_state(ctx, conn)


def touch_learning_indexed(ctx: Context, conn: sqlite3.Connection) -> None:
    tenant_id, workspace_id, user_id, agent_slug = _user_learning_state_pk(ctx)
    now = utc_now()
    with transaction(conn, ctx=ctx):
        conn.execute(
            """
            UPDATE user_learning_state
            SET last_indexed_at = ?, updated_at = ?
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND agent_slug = ?
            """,
            (now, now, tenant_id, workspace_id, user_id, agent_slug),
        )


# ---------------------------------------------------------------------------
# Personal memory blocks (wrappers over fnd_memory_blocks)
# ---------------------------------------------------------------------------


def _personal_namespace(agent_slug: str = AGENT_SLUG_DEFAULT) -> str:
    return f"{PERSONAL_NS}/{agent_slug}"


def upsert_personal_block(
    ctx: Context,
    conn: sqlite3.Connection,
    key: str,
    value: str,
    kind: str = "instruction",
    importance: float = 0.8,
    source: str = "",
) -> dict[str, Any]:
    """Write an approved personal memory block scoped to user/workspace."""

    namespace = _personal_namespace()
    _validate_ns_key(namespace, key)
    tenant_id = ctx.require_tenant()
    workspace_id = ctx.require_scoped_workspace()
    user_id = ctx.user_id or "local"
    now = utc_now()
    with transaction(conn, ctx=ctx):
        existing = conn.execute(
            """
            SELECT id FROM memory_block
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND namespace = ? AND key = ? AND archived_at IS NULL
            """,
            (tenant_id, workspace_id, user_id, namespace, key),
        ).fetchone()
        if existing is not None:
            block_id = existing["id"]
            conn.execute(
                """
                INSERT INTO memory_revision
                    (id, tenant_id, workspace_id, block_id, namespace, key, value, kind, importance, edited_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (new_id("mrv"), tenant_id, workspace_id, block_id, namespace, key, value, kind, importance, user_id, now),
            )
            conn.execute(
                """
                UPDATE memory_block
                SET value = ?, kind = ?, importance = ?, source = ?, updated_at = ?, archived_at = NULL
                WHERE id = ?
                """,
                (value, kind, importance, source, now, block_id),
            )
            action = "updated"
        else:
            block_id = new_id("mem")
            conn.execute(
                """
                INSERT INTO memory_block
                    (id, tenant_id, workspace_id, user_id, namespace, key, value, kind, importance, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (block_id, tenant_id, workspace_id, user_id, namespace, key, value, kind, importance, source, now, now),
            )
            action = "created"
    return {"block_id": block_id, "namespace": namespace, "key": key, "action": action}


def archive_personal_block(
    ctx: Context,
    conn: sqlite3.Connection,
    key: str,
) -> dict[str, Any]:
    """Archive a personal memory block (rollback)."""

    namespace = _personal_namespace()
    _validate_ns_key(namespace, key)
    tenant_id = ctx.require_tenant()
    workspace_id = ctx.require_scoped_workspace()
    user_id = ctx.user_id or "local"
    now = utc_now()
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT id FROM memory_block
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND namespace = ? AND key = ? AND archived_at IS NULL
            """,
            (tenant_id, workspace_id, user_id, namespace, key),
        ).fetchone()
        if row is None:
            raise ValueError("Memory block not found")
        conn.execute(
            "UPDATE memory_block SET archived_at = ?, updated_at = ? WHERE id = ?",
            (now, now, row["id"]),
        )
    return {"archived": True, "block_id": row["id"], "namespace": namespace, "key": key}


def recall_personal_blocks(
    ctx: Context,
    conn: sqlite3.Connection,
    query: str = "",
    limit: int = MEMORY_INJECTION_TOP_K,
) -> list[dict[str, Any]]:
    """Deterministic recall over the current user's personal memory blocks.

    Ranking: term overlap (60%) + importance (25%) + recency (15%).
    """

    tenant_id = ctx.require_tenant()
    workspace_id = ctx.require_scoped_workspace()
    user_id = ctx.user_id or "local"
    namespace = _personal_namespace()
    with transaction(conn, ctx=ctx):
        rows = conn.execute(
            """
            SELECT * FROM memory_block
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND archived_at IS NULL
                  AND (namespace = ? OR namespace LIKE ?)
            """,
            (tenant_id, workspace_id, user_id, namespace, namespace + "/%"),
        ).fetchall()

    terms = [t for t in re.split(r"\W+", (query or "").lower()) if len(t) >= 2]
    now = datetime.now(timezone.utc)
    scored: list[dict[str, Any]] = []
    for block in rows:
        haystack = f"{block['namespace']} {block['key']} {block['value']}".lower()
        if terms:
            hits = sum(1 for t in terms if t in haystack)
            term_score = hits / len(terms)
        else:
            term_score = 0.0
        if terms and term_score == 0.0:
            continue
        try:
            updated = datetime.fromisoformat(block["updated_at"].replace("Z", "+00:00"))
            age_days = max((now - updated).total_seconds() / 86400.0, 0.0)
        except Exception:
            age_days = 365.0
        recency = 1.0 / (1.0 + age_days / 7.0)
        score = 0.6 * term_score + 0.25 * float(block["importance"] or 0.0) + 0.15 * recency
        block = dict(block)
        block["score"] = round(score, 4)
        block["matched_terms"] = [t for t in terms if t in haystack]
        scored.append(block)
    scored.sort(key=lambda b: b["score"], reverse=True)
    return scored[:limit]


# ---------------------------------------------------------------------------
# Memory injection into prompts
# ---------------------------------------------------------------------------


def _estimate_tokens(text: str) -> int:
    """Cheap byte/word heuristic (~4 chars/token for Latin text)."""

    return max(1, len(text) // 4)


def build_memory_context(
    ctx: Context,
    conn: sqlite3.Connection,
    query: str = "",
    max_tokens: int = MEMORY_INJECTION_MAX_TOKENS,
) -> str:
    """Return a delimited memory context string respecting a token budget.

    Returns an empty string when the user has no personal memory blocks.
    """

    if not ctx.user_id:
        return ""
    blocks = recall_personal_blocks(ctx, conn, query=query, limit=MEMORY_INJECTION_TOP_K)
    if not blocks:
        return ""
    pieces: list[str] = []
    used = 0
    header = "[preferencias personales del usuario]"
    used += _estimate_tokens(header)
    for block in blocks:
        line = f"- {block['value']}"
        tok = _estimate_tokens(line)
        if used + tok > max_tokens:
            break
        pieces.append(line)
        used += tok
    if not pieces:
        return ""
    return f"{header}\n" + "\n".join(pieces) + "\n[/preferencias personales del usuario]\n"


# ---------------------------------------------------------------------------
# Pattern detector (read-only)
# ---------------------------------------------------------------------------


def detect_personal_memory_patterns(
    ctx: Context,
    conn: sqlite3.Connection,
) -> list["AmbientFinding"]:
    """Detect recurring feedback patterns per user.

    Returns ``AmbientFinding`` objects; the ambient orchestrator routes these
    to ``orchestrate_memory_proposals`` instead of creating WorkLoom drafts.
    """

    from ..ambient_detectors import AmbientFinding

    workspace_id = ctx.require_scoped_workspace()
    tenant_id = ctx.require_tenant()
    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat().replace("+00:00", "Z")

    with transaction(conn, ctx=ctx):
        rows = conn.execute(
            """
            SELECT mf.reason, mf.outcome, m.user_id, COUNT(*) AS cnt,
                   GROUP_CONCAT(mf.message_id, ',') AS message_ids
            FROM message_feedback mf
            JOIN message m ON m.id = mf.message_id
            WHERE mf.workspace_id = ? AND mf.tenant_id = ?
                  AND mf.created_at > ?
                  AND mf.reason IS NOT NULL AND mf.reason != ''
            GROUP BY m.user_id, mf.reason, mf.outcome
            ORDER BY m.user_id, cnt DESC
            """,
            (workspace_id, tenant_id, since),
        ).fetchall()

    # Group by (user_id, reason) aggregating accepted/rejected/regenerated.
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        reason = row["reason"]
        if reason not in VALID_FEEDBACK_REASONS:
            continue
        user_id = row["user_id"] or "local"
        key = (user_id, reason)
        bucket = grouped.setdefault(key, {"count": 0, "outcomes": {}, "message_ids": set()})
        bucket["count"] += int(row["cnt"] or 0)
        bucket["outcomes"][row["outcome"]] = int(row["cnt"] or 0)
        for mid in (row["message_ids"] or "").split(","):
            if mid:
                bucket["message_ids"].add(mid)

    state = _ensure_user_learning_state(ctx, conn)
    threshold = int(state.get("detection_threshold") or MEMORY_PATTERN_THRESHOLD_DEFAULT)

    findings: list[AmbientFinding] = []
    for (user_id, reason), data in grouped.items():
        count = data["count"]
        if count < threshold:
            continue
        summary = _REASON_SUMMARY.get(reason, f"Patrón recurrente de feedback: {reason}")
        findings.append(
            AmbientFinding(
                detector_slug="personal_memory",
                target_type="user_learning_state",
                target_id=f"{tenant_id}:{workspace_id}:{user_id}:{reason}",
                severity="low",
                title=f"Patrón de feedback: {reason}",
                description=(
                    f"El usuario '{user_id}' acumuló {count} eventos de feedback "
                    f"con razón '{reason}'. Resumen sugerido: {summary}"
                ),
                suggested_action="Revisar la propuesta de memoria personal y aplicarla o ignorarla.",
                evidence_json={
                    "user_id": user_id,
                    "reason": reason,
                    "count": count,
                    "threshold": threshold,
                    "outcomes": data["outcomes"],
                    "sample_message_ids": sorted(data["message_ids"])[:10],
                    "summary": summary,
                },
            )
        )

    return findings[:MEMORY_MAX_CANDIDATES_PER_CYCLE]


# ---------------------------------------------------------------------------
# Proposal orchestration / curation
# ---------------------------------------------------------------------------


def _proposal_id_from_evidence(evidence: dict[str, Any]) -> str:
    """Stable proposal id for a (tenant, workspace, user, reason)."""

    raw = (
        f"{evidence['tenant_id']}:{evidence['workspace_id']}:"
        f"{evidence['user_id']}:{evidence['reason']}"
    )
    return "mmp-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def orchestrate_memory_proposals(
    ctx: Context,
    conn: sqlite3.Connection,
    findings: list[AmbientFinding],
) -> dict[str, Any]:
    """Convert detector findings into ``memory_proposal`` rows.

    Existing pending proposals for the same (user, reason) are merged by
    incrementing ``detected_count`` and refreshing the evidence.
    """

    tenant_id = ctx.require_tenant()
    workspace_id = ctx.require_scoped_workspace()
    now = utc_now()
    created_ids: list[str] = []
    merged_ids: list[str] = []

    with transaction(conn, ctx=ctx):
        for finding in findings:
            ev = finding.evidence_json
            ev["tenant_id"] = tenant_id
            ev["workspace_id"] = workspace_id
            reason = ev["reason"]
            user_id = ev["user_id"]
            proposal_id = _proposal_id_from_evidence(ev)

            existing = conn.execute(
                """
                SELECT id, state, detected_count FROM memory_proposal
                WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND id = ?
                """,
                (tenant_id, workspace_id, user_id, proposal_id),
            ).fetchone()

            if existing is not None and existing["state"] == "pending":
                # Refresh the aggregate count to the detector's current total
                # rather than accumulating, so re-indexing does not inflate it.
                conn.execute(
                    """
                    UPDATE memory_proposal
                    SET detected_count = ?,
                        last_detected = ?,
                        evidence_json = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        ev.get("count", existing["detected_count"]),
                        now,
                        json.dumps(ev, ensure_ascii=False),
                        now,
                        proposal_id,
                    ),
                )
                merged_ids.append(proposal_id)
                continue

            if existing is not None:
                # Already applied/ignored: do not resurrect automatically.
                continue

            summary = ev.get("summary") or _REASON_SUMMARY.get(reason, f"Patrón: {reason}")
            conn.execute(
                """
                INSERT INTO memory_proposal (
                    id, tenant_id, workspace_id, user_id, agent_slug, summary,
                    detected_count, first_detected, last_detected, evidence_json,
                    state, applied_at, applied_namespace, applied_key,
                    actor_id, actor_role_at_decision, schema_version, source_version,
                    approved_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    proposal_id,
                    tenant_id,
                    workspace_id,
                    user_id,
                    AGENT_SLUG_DEFAULT,
                    summary,
                    ev.get("count", 1),
                    now,
                    now,
                    json.dumps(ev, ensure_ascii=False),
                    "pending",
                    None,
                    None,
                    None,
                    ctx.actor_id,
                    ctx.actor_role_at_decision,
                    47,
                    "v1",
                    None,
                    now,
                    now,
                ),
            )
            created_ids.append(proposal_id)

    touch_learning_indexed(ctx, conn)
    return {"created": created_ids, "merged": merged_ids}


def list_memory_proposals(
    ctx: Context,
    conn: sqlite3.Connection,
    state: str | None = None,
) -> list[dict[str, Any]]:
    tenant_id = ctx.require_tenant()
    workspace_id = ctx.require_scoped_workspace()
    user_id = ctx.user_id or "local"
    params: list[Any] = [tenant_id, workspace_id, user_id]
    sql = """
        SELECT * FROM memory_proposal
        WHERE tenant_id = ? AND workspace_id = ? AND user_id = ?
    """
    if state:
        sql += " AND state = ?"
        params.append(state)
    sql += " ORDER BY last_detected DESC"
    with transaction(conn, ctx=ctx):
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def get_memory_proposal(
    ctx: Context,
    conn: sqlite3.Connection,
    proposal_id: str,
) -> dict[str, Any] | None:
    tenant_id = ctx.require_tenant()
    workspace_id = ctx.require_scoped_workspace()
    user_id = ctx.user_id or "local"
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT * FROM memory_proposal
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND id = ?
            """,
            (tenant_id, workspace_id, user_id, proposal_id),
        ).fetchone()
        return dict(row) if row else None


def apply_memory_proposal(
    ctx: Context,
    conn: sqlite3.Connection,
    proposal_id: str,
) -> dict[str, Any]:
    """Approve a proposal and write it to the user's personal memory."""

    tenant_id = ctx.require_tenant()
    workspace_id = ctx.require_scoped_workspace()
    user_id = ctx.user_id or "local"
    now = utc_now()

    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT * FROM memory_proposal
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND id = ? AND state = 'pending'
            """,
            (tenant_id, workspace_id, user_id, proposal_id),
        ).fetchone()
        if row is None:
            raise ValueError("Memory proposal not found or already processed")

        reason = json.loads(row["evidence_json"] or "{}").get("reason", "other")
        key = f"{reason}_{proposal_id[:8]}"
        key = re.sub(r"[^A-Za-z0-9_\-.]", "_", key)
        namespace = _personal_namespace()

        approved_by = ctx.resolved_actor_id() or ctx.user_id or "unknown"
        block = upsert_personal_block(
            ctx,
            conn,
            key=key,
            value=row["summary"],
            kind="instruction",
            importance=0.8,
            source=f"memory_proposal:{proposal_id}",
        )

        conn.execute(
            """
            UPDATE memory_proposal
            SET state = 'applied',
                applied_at = ?,
                applied_namespace = ?,
                applied_key = ?,
                approved_by = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (now, namespace, key, approved_by, now, proposal_id),
        )

    decrement_unconsolidated_count(ctx, conn, int(row["detected_count"] or 1))
    return {
        "proposal_id": proposal_id,
        "state": "applied",
        "block": block,
        "approved_by": approved_by,
    }


def ignore_memory_proposal(
    ctx: Context,
    conn: sqlite3.Connection,
    proposal_id: str,
) -> dict[str, Any]:
    """Mark a proposal as ignored (soft delete)."""

    tenant_id = ctx.require_tenant()
    workspace_id = ctx.require_scoped_workspace()
    user_id = ctx.user_id or "local"
    now = utc_now()

    with transaction(conn, ctx=ctx):
        row = conn.execute(
            """
            SELECT detected_count FROM memory_proposal
            WHERE tenant_id = ? AND workspace_id = ? AND user_id = ? AND id = ? AND state = 'pending'
            """,
            (tenant_id, workspace_id, user_id, proposal_id),
        ).fetchone()
        if row is None:
            raise ValueError("Memory proposal not found or already processed")

        approved_by = ctx.resolved_actor_id() or ctx.user_id or "unknown"
        conn.execute(
            """
            UPDATE memory_proposal
            SET state = 'ignored',
                approved_by = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (approved_by, now, proposal_id),
        )

    decrement_unconsolidated_count(ctx, conn, int(row["detected_count"] or 1))
    return {"proposal_id": proposal_id, "state": "ignored", "approved_by": approved_by}


# ---------------------------------------------------------------------------
# Hygiene: archive stale ignored proposals
# ---------------------------------------------------------------------------


def archive_stale_memory_proposals(
    ctx: Context,
    conn: sqlite3.Connection,
    max_age_days: int = 30,
) -> dict[str, Any]:
    """Soft-archive ignored proposals older than ``max_age_days``."""

    tenant_id = ctx.require_tenant()
    workspace_id = ctx.require_scoped_workspace()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).isoformat().replace("+00:00", "Z")
    with transaction(conn, ctx=ctx):
        cur = conn.execute(
            """
            UPDATE memory_proposal
            SET state = 'ignored',
                updated_at = ?
            WHERE tenant_id = ? AND workspace_id = ?
                  AND state = 'pending'
                  AND last_detected < ?
            """,
            (utc_now(), tenant_id, workspace_id, cutoff),
        )
        archived = cur.rowcount
    return {"archived": archived}
