"""Backend service for M19 full-state snapshots."""
from __future__ import annotations

from django.db.models import Max
from django.utils import timezone

from apps.classifier.models import FeedItem, FeedItemStatus
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.drafts.models import Draft
from apps.events.models import EventLog
from apps.tasks.models import Task


def build_full_state(tenant_id: str) -> dict:
    """Return a tenant-scoped operative snapshot for desktop offline sync."""
    set_db_tenant(tenant_id)
    try:
        last_event = (
            EventLog.objects.filter(tenant_id=tenant_id)
            .aggregate(max_seq=Max("seq_no"))
            .get("max_seq")
        )

        drafts = Draft.objects.filter(tenant_id=tenant_id).order_by("-updated_at")[:100]
        tasks = Task.objects.filter(tenant_id=tenant_id).order_by("-updated_at")[:100]
        feed_items = FeedItem.objects.filter(
            tenant_id=tenant_id,
            status__in=(
                FeedItemStatus.RECEIVED,
                FeedItemStatus.CLASSIFYING,
                FeedItemStatus.PENDING_HUMAN_REVIEW,
                FeedItemStatus.MANUAL_REVIEW,
            ),
        ).order_by("-received_at")[:100]

        return {
            "tenant_id": str(tenant_id),
            "last_event_id": last_event,
            "generated_at": timezone.now().isoformat(),
            "drafts": [
                {
                    "id": str(d.id),
                    "task_id": str(d.task_id) if d.task_id else None,
                    "status": d.status,
                    "channel": d.channel,
                    "recipient": d.recipient,
                    "expires_at": d.expires_at.isoformat(),
                    "created_at": d.created_at.isoformat(),
                }
                for d in drafts
            ],
            "tasks": [
                {
                    "id": str(t.id),
                    "agent_id": t.agent_id,
                    "status": t.status,
                    "priority": t.priority,
                    "payload": t.payload,
                    "review_status": t.review_status,
                    "created_at": t.created_at.isoformat(),
                    "updated_at": t.updated_at.isoformat(),
                }
                for t in tasks
            ],
            "feed_items": [
                {
                    "id": str(f.id),
                    "source_type": f.source_type,
                    "external_id": f.external_id,
                    "status": f.status,
                    "data_class": f.data_class,
                    "received_at": f.received_at.isoformat(),
                }
                for f in feed_items
            ],
        }
    finally:
        clear_db_tenant()
