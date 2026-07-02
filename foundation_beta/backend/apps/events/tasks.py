"""Celery tasks for M15 Outbox Streams."""
from __future__ import annotations

import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

from apps.core.redis_client import get_redis_client, tenant_key
from apps.events.models import Outbox, OutboxStatus
from faberloom.celery import TenantTask, app


def _fanout_event(tenant_id: str, row: Outbox) -> None:
    """Send the published event to the tenant channel-layer group."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f"tenant_events_{tenant_id}",
        {
            "type": "event_message",
            "payload": {
                "event_id": row.event_id,
                "type": row.event_type,
                "tenant_id": tenant_id,
                "payload": row.payload_json,
                "seq_no": row.seq_no,
                "timestamp": row.created_at.isoformat(),
            },
        },
    )


@app.task(base=TenantTask, bind=True, max_retries=3)
def relay_outbox(self, _tenant_id: str):
    """Publish pending outbox rows to the tenant Redis stream."""
    redis = get_redis_client()
    stream_key = tenant_key(_tenant_id, "events")
    ttl = int(getattr(settings, "EVENT_STREAM_TTL_SECONDS", 86400))

    pending = Outbox.objects.filter(
        tenant_id=_tenant_id, status=OutboxStatus.PENDING
    ).order_by("seq_no")

    published = 0
    for row in pending:
        try:
            redis.xadd(
                stream_key,
                {
                    "event_id": row.event_id,
                    "type": row.event_type,
                    "payload": json.dumps(row.payload_json),
                    "seq_no": str(row.seq_no),
                },
                id=f"{row.seq_no}-0",
                approximate=True,
            )
            redis.expire(stream_key, ttl)
            row.status = OutboxStatus.PUBLISHED
            row.save(update_fields=["status", "updated_at", "retry_count"])
            _fanout_event(_tenant_id, row)
            published += 1
        except Exception as exc:
            row.retry_count += 1
            if row.retry_count >= 3:
                row.status = OutboxStatus.FAILED
            row.save(update_fields=["retry_count", "status", "updated_at"])
            raise self.retry(exc=exc, countdown=2**row.retry_count)

    return {"published": published}
