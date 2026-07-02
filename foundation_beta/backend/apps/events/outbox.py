"""Transactional outbox writer for M15."""
from __future__ import annotations

import uuid
from typing import Any

from django.db import connection, transaction

from apps.events.models import EventLog, Outbox


class EventWriter:
    """Write an event atomically to outbox and event_log within the caller transaction."""

    @classmethod
    def emit(
        cls,
        tenant_id: str | uuid.UUID,
        event_type: str,
        payload: dict[str, Any],
        event_id: str | None = None,
    ) -> str:
        if event_id is None:
            event_id = f"evt_{uuid.uuid4().hex}"

        with connection.cursor() as cursor:
            cursor.execute("SELECT nextval('global_event_seq')")
            (seq_no,) = cursor.fetchone()

        tenant_id_str = str(tenant_id)
        Outbox.objects.create(
            tenant_id=tenant_id_str,
            event_id=event_id,
            event_type=event_type,
            payload_json=payload,
            seq_no=seq_no,
        )
        EventLog.objects.create(
            tenant_id=tenant_id_str,
            event_id=event_id,
            event_type=event_type,
            payload_json=payload,
            seq_no=seq_no,
        )
        return event_id


def emit_event(
    tenant_id: str | uuid.UUID,
    event_type: str,
    payload: dict[str, Any],
    correlation_id: str = "",
) -> str:
    """Convenience function used by M08/M09 to emit domain events."""
    if correlation_id:
        payload["correlation_id"] = correlation_id
    return EventWriter.emit(tenant_id, event_type, payload)
