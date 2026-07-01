"""Event emission helper (writes to transactional outbox)."""
from __future__ import annotations

import uuid
from typing import Any

from apps.events.models import OutboxEvent


def emit_event(
    tenant_id: str | uuid.UUID,
    event_type: str,
    payload: dict[str, Any],
    correlation_id: str = "",
) -> OutboxEvent:
    """Persist an event to the outbox table within the current transaction."""
    return OutboxEvent.objects.create(
        tenant_id=str(tenant_id),
        event_type=event_type,
        payload=payload,
        correlation_id=correlation_id,
    )
