"""M19 Offline Sync backend snapshot tests."""
from __future__ import annotations

import pytest
from django.utils import timezone

from apps.classifier.models import FeedItem, FeedItemStatus
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.drafts.models import Draft, DraftStatus
from apps.events.models import EventLog
from apps.sync.service import build_full_state
from apps.tasks.models import Task


pytestmark = pytest.mark.django_db


def _setup_tenant_state(tenant):
    set_db_tenant(tenant.id)
    try:
        EventLog.objects.create(
            tenant=tenant,
            event_id="evt_001",
            event_type="draft.generated",
            payload_json={"draft_id": "x"},
            seq_no=42,
        )

        task = Task.objects.create(
            tenant=tenant,
            agent_id="@cotizador",
            invocation_mode=Task.InvocationMode.INBOUND,
            priority=Task.Priority.NORMAL,
            payload={"subject": "RFQ"},
            status=Task.Status.RUNNING,
            expected_completion_by=timezone.now() + timezone.timedelta(hours=1),
        )

        Draft.objects.create(
            tenant=tenant,
            task=task,
            status=DraftStatus.PENDING,
            original_content={"subject": "Cotización"},
            channel=Draft.Channel.EMAIL,
            recipient="client@example.com",
            expires_at=timezone.now() + timezone.timedelta(hours=48),
        )

        FeedItem.objects.create(
            tenant=tenant,
            source_type="email",
            raw_payload={"subject": "Nueva RFQ"},
            normalized_payload={"subject": "Nueva RFQ"},
            status=FeedItemStatus.PENDING_HUMAN_REVIEW,
        )
    finally:
        clear_db_tenant()


def test_full_state_includes_last_event_and_entities(tenant):
    _setup_tenant_state(tenant)

    state = build_full_state(str(tenant.id))

    assert state["tenant_id"] == str(tenant.id)
    assert state["last_event_id"] == 42
    assert len(state["drafts"]) == 1
    assert len(state["tasks"]) == 1
    assert len(state["feed_items"]) == 1
    assert state["feed_items"][0]["status"] == FeedItemStatus.PENDING_HUMAN_REVIEW


def test_full_state_respects_tenant_isolation(tenant, other_tenant):
    _setup_tenant_state(tenant)

    state = build_full_state(str(other_tenant.id))

    assert state["last_event_id"] is None
    assert state["drafts"] == []
    assert state["tasks"] == []
    assert state["feed_items"] == []
