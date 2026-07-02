"""M15 Outbox Streams tests."""
from __future__ import annotations

import json
import urllib.parse
import uuid

import pytest
from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.db import transaction
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.auth_session import session as session_store
from apps.core.redis_client import get_redis_client, tenant_key
from apps.events.models import EventLog, Outbox, OutboxStatus
from apps.events.outbox import EventWriter
from apps.events.tasks import relay_outbox
from apps.users.models import Membership, MembershipStatus, User
from faberloom.asgi import application


def _session_cookie(tenant, user, roles: list[str] = None, active_hat: str = "") -> str:
    roles = roles or ["owner"]
    return session_store.create_session(
        user.id, tenant.id, roles, active_hat or roles[0]
    )


@pytest.mark.django_db
def test_event_writer_creates_outbox_and_event_log(tenant_a):
    event_id = EventWriter.emit(tenant_a.id, "task.created", {"task_id": "t1"})
    assert Outbox.objects.filter(event_id=event_id).exists()
    assert EventLog.objects.filter(event_id=event_id).exists()
    outbox = Outbox.objects.get(event_id=event_id)
    assert outbox.status == OutboxStatus.PENDING
    assert outbox.seq_no > 0


@pytest.mark.django_db
def test_event_writer_is_atomic_with_business_transaction(tenant_a):
    try:
        with transaction.atomic():
            EventWriter.emit(tenant_a.id, "task.created", {"task_id": "t2"})
            raise RuntimeError("rollback")
    except RuntimeError:
        pass

    assert not Outbox.objects.filter(event_type="task.created", payload_json__task_id="t2").exists()


@pytest.mark.django_db
def test_relay_publishes_pending_events_to_redis_stream(tenant_a, owner_user, owner_membership):
    event_id = EventWriter.emit(tenant_a.id, "draft.generated", {"draft_id": "d1"})
    result = relay_outbox(_tenant_id=str(tenant_a.id))
    assert result["published"] == 1

    outbox = Outbox.objects.get(event_id=event_id)
    assert outbox.status == OutboxStatus.PUBLISHED

    redis = get_redis_client()
    entries = redis.xrange(tenant_key(tenant_a.id, "events"))
    assert len(entries) == 1
    _, fields = entries[0]
    data = {k.decode() if isinstance(k, bytes) else k: v for k, v in fields.items()}
    assert data["event_id"] == event_id


@pytest.mark.django_db
def test_duplicate_relay_does_not_duplicate_stream_entries(tenant_a, owner_user, owner_membership):
    EventWriter.emit(tenant_a.id, "draft.approved", {"draft_id": "d2"})
    relay_outbox(_tenant_id=str(tenant_a.id))
    relay_outbox(_tenant_id=str(tenant_a.id))
    redis = get_redis_client()
    entries = redis.xrange(tenant_key(tenant_a.id, "events"))
    assert len(entries) == 1


@pytest.mark.django_db
def test_polling_fallback_returns_events(tenant_a, owner_user, owner_membership):
    event_id = EventWriter.emit(tenant_a.id, "feed.item.received", {"item_id": "i1"})
    relay_outbox(_tenant_id=str(tenant_a.id))

    session_id = _session_cookie(tenant_a, owner_user, ["owner"])
    client = Client()
    client.cookies["session_id"] = session_id
    resp = client.get(reverse("events-polling"), {"since": "0"})
    assert resp.status_code == 200
    data = resp.json()
    assert any(e["event_id"] == event_id for e in data["events"])


@pytest.mark.django_db
def test_polling_fallback_is_isolated_by_tenant(
    tenant_a, tenant_b, owner_user, owner_membership
):
    EventWriter.emit(tenant_b.id, "feed.item.received", {"item_id": "i2"})
    relay_outbox(_tenant_id=str(tenant_b.id))

    session_id = _session_cookie(tenant_a, owner_user, ["owner"])
    client = Client()
    client.cookies["session_id"] = session_id
    resp = client.get(reverse("events-polling"), {"since": "0"})
    assert resp.status_code == 200
    assert all(e["tenant_id"] == str(tenant_a.id) for e in resp.json()["events"])


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_rejects_anonymous(tenant_a):
    communicator = WebsocketCommunicator(application, "ws/events/")
    connected, _ = await communicator.connect()
    assert not connected
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_receives_event_after_relay(tenant_a, owner_user, owner_membership):
    session_id = _session_cookie(tenant_a, owner_user, ["owner"])
    headers = [(b"cookie", f"session_id={session_id}".encode())]
    communicator = WebsocketCommunicator(application, "ws/events/", headers=headers)
    connected, _ = await communicator.connect()
    assert connected

    await sync_to_async(EventWriter.emit)(tenant_a.id, "draft.sent", {"draft_id": "d3"})
    await sync_to_async(relay_outbox, thread_sensitive=False)(_tenant_id=str(tenant_a.id))

    response = await communicator.receive_json_from(timeout=5)
    assert response["type"] == "draft.sent"
    assert response["payload"]["draft_id"] == "d3"
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_does_not_cross_tenant(
    tenant_a, tenant_b, owner_user, owner_membership
):
    # Owner belongs to tenant_a; connect with tenant_a session.
    session_id = _session_cookie(tenant_a, owner_user, ["owner"])
    headers = [(b"cookie", f"session_id={session_id}".encode())]
    communicator = WebsocketCommunicator(application, "ws/events/", headers=headers)
    connected, _ = await communicator.connect()
    assert connected

    # Publish an event in tenant_b.
    await sync_to_async(EventWriter.emit)(tenant_b.id, "draft.sent", {"draft_id": "d4"})
    await sync_to_async(relay_outbox, thread_sensitive=False)(_tenant_id=str(tenant_b.id))

    # No message should arrive; give it a short window.
    with pytest.raises(Exception):
        await communicator.receive_json_from(timeout=0.5)
    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_websocket_sync_required_for_old_cursor(tenant_a, owner_user, owner_membership):
    # No events published yet; any non-fresh cursor is considered stale.
    session_id = _session_cookie(tenant_a, owner_user, ["owner"])
    headers = [(b"cookie", f"session_id={session_id}".encode())]
    communicator = WebsocketCommunicator(
        application, "ws/events/?since=1", headers=headers
    )
    connected, _ = await communicator.connect()
    assert connected
    response = await communicator.receive_json_from(timeout=2)
    assert response["type"] == "sync_required"
    await communicator.disconnect()


@pytest.mark.django_db
def test_purge_outbox_command(tenant_a):
    from django.core.management import call_command

    event_id = EventWriter.emit(tenant_a.id, "task.created", {"task_id": "t3"})
    outbox = Outbox.objects.get(event_id=event_id)
    outbox.status = OutboxStatus.PUBLISHED
    outbox.created_at = timezone.now() - timezone.timedelta(days=10)
    outbox.save(update_fields=["status", "created_at"])

    call_command("purge_outbox")
    assert not Outbox.objects.filter(event_id=event_id).exists()
