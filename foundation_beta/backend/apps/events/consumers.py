"""Django Channels consumer for M15 Outbox Streams."""
from __future__ import annotations

import json
import urllib.parse
from datetime import timedelta
from typing import Any

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.utils import timezone

from apps.auth_session.session import SESSION_INDEX_PREFIX, get_session
from apps.core.redis_client import get_redis_client, tenant_key
from apps.rbac.permissions import resolve_permission
from apps.users.models import Membership


class EventsConsumer(AsyncWebsocketConsumer):
    """WebSocket fanout for tenant-scoped events with permission filtering."""

    async def connect(self):
        session_id = self._cookie_session_id()
        if not session_id:
            await self.close(code=4001)
            return

        auth = await _authenticate_async(session_id)
        if auth is None:
            await self.close(code=4001)
            return

        self.tenant_id = auth["tenant_id"]
        self.user = auth["user"]
        self.membership = auth["membership"]
        self.active_hat = auth["active_hat"]
        self.stream_key = tenant_key(self.tenant_id, "events")

        since = self._since_seq()
        await self.channel_layer.group_add(self._group_name(), self.channel_name)
        await self.accept()

        # If the client is too far behind, ask for a full sync.
        cursor_valid = await _cursor_valid_async(self.stream_key, since)
        if not cursor_valid:
            await self.send(
                json.dumps({"type": "sync_required", "reason": "cursor_too_old"})
            )
            return

        missed = await _events_since_async(self.tenant_id, self.stream_key, since)
        for event in missed:
            if self._can_see(event):
                await self.send(json.dumps(event))

    async def disconnect(self, close_code):
        if getattr(self, "tenant_id", None):
            await self.channel_layer.group_discard(
                self._group_name(), self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        # Clients are read-only on this channel.
        pass

    async def event_message(self, event):
        """Handler for channel-layer messages."""
        payload = event["payload"]
        if self._can_see(payload):
            await self.send(json.dumps(payload))

    def _group_name(self) -> str:
        return f"tenant_events_{self.tenant_id}"

    def _cookie_session_id(self) -> str | None:
        headers = dict(self.scope.get("headers", []))
        cookie_header = headers.get(b"cookie", b"").decode()
        if not cookie_header:
            return None
        for cookie in cookie_header.split(";"):
            key, _, value = cookie.strip().partition("=")
            if key == settings.SESSION_COOKIE_NAME:
                return value
        return None

    def _since_seq(self) -> int | None:
        query = self.scope.get("query_string", b"").decode()
        params = urllib.parse.parse_qs(query)
        since = params.get("since", [None])[0]
        if since is None:
            return None
        try:
            return int(since)
        except ValueError:
            return None

    def _can_see(self, event: dict[str, Any]) -> bool:
        # E1: any active member of the tenant receives all tenant events.
        # Fine-grained permission filtering is enforced on REST endpoints by M09.
        return event.get("tenant_id") == self.tenant_id and self.membership is not None


class _SessionUser:
    def __init__(self, payload: dict):
        self.id = payload["user_id"]
        self.pk = self.id
        self.tenant_id = payload["tenant_id"]
        self.roles = payload.get("roles", [])
        self.active_hat = payload.get("active_hat", "")
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = True


def _resolve_active_hat(membership: Membership, requested: str | None) -> str | None:
    roles = membership.roles or []
    if not roles:
        return None
    if requested and requested in roles:
        return requested
    if membership.active_hat and membership.active_hat in roles:
        return membership.active_hat
    return roles[0]


def _authenticate_sync(session_id: str) -> dict[str, Any] | None:
    redis = get_redis_client()
    tenant_id_raw = redis.get(f"{SESSION_INDEX_PREFIX}{session_id}")
    if not tenant_id_raw:
        return None
    tenant_id = (
        tenant_id_raw.decode()
        if isinstance(tenant_id_raw, bytes)
        else tenant_id_raw
    )
    session_data = get_session(session_id, tenant_id)
    if not session_data:
        return None

    try:
        membership = Membership.objects.get(
            user_id=session_data["user_id"], tenant_id=tenant_id
        )
    except Membership.DoesNotExist:
        membership = None

    active_hat = None
    if membership:
        active_hat = _resolve_active_hat(membership, None)
        if active_hat:
            from apps.rbac.models import Role

            try:
                membership._role_cache = Role.objects.get(id=active_hat)
            except Role.DoesNotExist:
                membership._role_cache = None

    user = _SessionUser(session_data)
    user.active_hat = active_hat or ""
    return {
        "tenant_id": tenant_id,
        "user": user,
        "membership": membership,
        "active_hat": active_hat,
    }


def _cursor_valid_sync(stream_key: str, since: int | None) -> bool:
    if since is None:
        return True
    redis = get_redis_client()
    oldest = redis.xrange(stream_key, count=1)
    if not oldest:
        return False
    first_seq = int(oldest[0][1].get(b"seq_no", 0))
    return since >= first_seq


def _events_since_sync(
    tenant_id: str, stream_key: str, since: int | None
) -> list[dict[str, Any]]:
    if since is None:
        return []
    redis = get_redis_client()
    entries = redis.xrange(stream_key, min=f"({since}-0", max="+")
    events = []
    for _entry_id, fields in entries:
        data = {
            k.decode() if isinstance(k, bytes) else k: v
            for k, v in fields.items()
        }
        try:
            payload = json.loads(data.get("payload", "{}"))
        except json.JSONDecodeError:
            payload = {}
        events.append(
            {
                "event_id": data.get("event_id"),
                "type": data.get("type"),
                "tenant_id": tenant_id,
                "payload": payload,
                "seq_no": int(data.get("seq_no", 0)),
                "timestamp": timezone.now().isoformat(),
            }
        )
    return events


_authenticate_async = database_sync_to_async(_authenticate_sync)
_cursor_valid_async = database_sync_to_async(_cursor_valid_sync)
_events_since_async = database_sync_to_async(_events_since_sync)
