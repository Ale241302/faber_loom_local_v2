"""Letta-backed memory client with an in-memory fallback for tests."""
from __future__ import annotations

import hashlib
import json
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.core.memory import letta_namespace


class _InMemoryStore:
    """Thread-local-ish key/value fallback used when Letta is not reachable."""

    _data: dict[str, Any] = {}

    @classmethod
    def _key(cls, namespace: str) -> str:
        return namespace

    @classmethod
    def store(cls, namespace: str, content: dict[str, Any], ttl: int | None = None) -> None:
        cls._data[cls._key(namespace)] = {
            "content": content,
            "expires_at": (timezone.now() + timedelta(seconds=ttl)).isoformat()
            if ttl
            else None,
        }

    @classmethod
    def append(cls, namespace: str, event: dict[str, Any]) -> None:
        key = cls._key(namespace)
        entry = cls._data.get(key, {"content": {"events": []}})
        if "content" not in entry:
            entry["content"] = {"events": []}
        if "events" not in entry["content"]:
            entry["content"]["events"] = []
        entry["content"]["events"].append(event)
        cls._data[key] = entry

    @classmethod
    def read(cls, namespace: str) -> dict[str, Any] | None:
        entry = cls._data.get(cls._key(namespace))
        if not entry:
            return None
        if entry.get("expires_at") and timezone.now().isoformat() > entry["expires_at"]:
            cls._data.pop(cls._key(namespace), None)
            return None
        return entry.get("content")

    @classmethod
    def clear(cls) -> None:
        cls._data.clear()


class LettaMemoryClient:
    """Thin wrapper around the Letta memory store.

    Namespaces are built by ``apps.core.memory.letta_namespace`` and isolate
    memory by tenant, agent, task (optional) and memory kind.
    """

    WORKING_TTL_SECONDS = 24 * 60 * 60

    def __init__(self, base_url: str | None = None, backend: str | None = None) -> None:
        self.base_url = (base_url or settings.LETTA_URL).rstrip("/")
        self.backend = backend or getattr(settings, "MEMORY_BACKEND", "letta")

    def _hash(self, content: dict[str, Any]) -> str:
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()

    def _store(
        self,
        namespace: str,
        content: dict[str, Any],
        ttl: int | None = None,
    ) -> dict[str, Any]:
        if self.backend == "memory":
            _InMemoryStore.store(namespace, content, ttl=ttl)
            return {"namespace": namespace, "hash": self._hash(content)}
        # Letta HTTP placeholder: in E1 the store is faked. When Letta is wired,
        # this becomes a PUT against a memory block keyed by ``namespace``.
        _InMemoryStore.store(namespace, content, ttl=ttl)
        return {"namespace": namespace, "hash": self._hash(content)}

    def _append(self, namespace: str, event: dict[str, Any]) -> dict[str, Any]:
        if self.backend == "memory":
            _InMemoryStore.append(namespace, event)
            return {"namespace": namespace, "event": event}
        _InMemoryStore.append(namespace, event)
        return {"namespace": namespace, "event": event}

    def _read(self, namespace: str) -> dict[str, Any] | None:
        if self.backend == "memory":
            return _InMemoryStore.read(namespace)
        return _InMemoryStore.read(namespace)

    def create_working(
        self,
        tenant_id,
        agent_id: str,
        task_id: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        namespace = letta_namespace(tenant_id, agent_id, task_id, kind="working")
        return self._store(namespace, context, ttl=self.WORKING_TTL_SECONDS)

    def create_episodic(
        self,
        tenant_id,
        agent_id: str,
        event: dict[str, Any],
    ) -> dict[str, Any]:
        namespace = letta_namespace(tenant_id, agent_id, kind="episodic")
        return self._append(namespace, event)

    def create_persistent(
        self,
        tenant_id,
        agent_id: str,
        content: dict[str, Any],
    ) -> dict[str, Any]:
        namespace = letta_namespace(tenant_id, agent_id, kind="persistent")
        return self._store(namespace, content, ttl=None)

    def read_namespace(
        self,
        tenant_id,
        agent_id: str,
        task_id: str | None = None,
        kind: str = "working",
    ) -> dict[str, Any] | None:
        namespace = letta_namespace(tenant_id, agent_id, task_id, kind=kind)
        return self._read(namespace)

    def read_agent(
        self,
        tenant_id,
        agent_id: str,
        kinds: list[str] | None = None,
    ) -> dict[str, dict[str, Any] | None]:
        kinds = kinds or ["working", "episodic", "persistent"]
        result: dict[str, dict[str, Any] | None] = {}
        for kind in kinds:
            namespace = letta_namespace(tenant_id, agent_id, kind=kind)
            result[kind] = self._read(namespace)
        return result

    def content_hash(self, content: dict[str, Any]) -> str:
        return self._hash(content)
