"""AuditWriter seam for FaberLoom.

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
        correlation_id: str | None = None,
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
        event_payload = payload or {}
        if correlation_id is not None:
            event_payload = {**event_payload, "correlation_id": correlation_id}
        event = AuditEvent(
            id=new_id("audit"),
            workspace_id=ctx.require_scoped_workspace(),
            actor_id=ctx.resolved_actor_id(),
            actor_role_at_decision=ctx.actor_role_at_decision,
            action=action,
            payload=event_payload,
            tenant_id=ctx.tenant_id,
            user_id=ctx.user_id,
            approved_by=approved_by,
            routine_version=routine_version,
            skill_version=skill_version,
            source_version=source_version,
            correlation_id=correlation_id,
            created_at=created_at,
        )

        with transaction(conn, ctx=ctx):
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
                correlation_id=correlation_id,
                created_at=created_at,
            )

        if mirror_jsonl and not outer_transaction:
            self.mirror(event)
        return event

    def mirror(self, event: AuditEvent) -> None:
        """Append an already-committed audit event to the JSONL mirror.

        The mirror is best-effort: failures are logged but not raised, so the
        database remains the source of truth.
        """

        try:
            self.audit_path.parent.mkdir(parents=True, exist_ok=True)
            with _audit_lock:
                with self.audit_path.open("a", encoding="utf-8") as handle:
                    handle.write(event.model_dump_json() + "\n")
        except Exception:
            # Best-effort mirror; do not break the API response.
            pass


audit_writer = AuditWriter()
