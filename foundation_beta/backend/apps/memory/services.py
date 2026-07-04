"""Memory lifecycle services for M17."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from django.db import models
from django.utils import timezone

from apps.audit.writer import AuditContext, AuditWriter
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.events.outbox import emit_event
from apps.memory.guard import ConflictCheckResult, MemoryConflictGuard
from apps.memory.models import MemoryConflict, MemoryItem
from apps.tenants.models import Tenant
from apps.users.models import User


class MemoryService:
    """High-level API for working, episodic and persistent memory."""

    WORKING_TTL_HOURS = 24

    @classmethod
    def record_working(
        cls,
        tenant_id,
        agent_id: str,
        task_id: str,
        context: dict[str, Any],
        *,
        client: Any,
    ) -> MemoryItem:
        set_db_tenant(tenant_id)
        try:
            result = client.create_working(tenant_id, agent_id, task_id, context)
            item, _ = MemoryItem.objects.update_or_create(
                tenant_id=str(tenant_id),
                agent_id=agent_id,
                task_id=task_id,
                layer=MemoryItem.Layer.WORKING,
                namespace=result["namespace"],
                defaults={
                    "content_hash": result["hash"],
                    "status": MemoryItem.Status.ACTIVE,
                    "validity_metadata": {"ttl_hours": cls.WORKING_TTL_HOURS},
                },
            )
            return item
        finally:
            clear_db_tenant()

    @classmethod
    def record_episodic(
        cls,
        tenant_id,
        agent_id: str,
        event: dict[str, Any],
        *,
        client: Any,
    ) -> MemoryItem:
        set_db_tenant(tenant_id)
        try:
            result = client.create_episodic(tenant_id, agent_id, event)
            item, _ = MemoryItem.objects.get_or_create(
                tenant_id=str(tenant_id),
                agent_id=agent_id,
                layer=MemoryItem.Layer.EPISODIC,
                namespace=result["namespace"],
                defaults={
                    "content_hash": client.content_hash(event),
                    "status": MemoryItem.Status.ACTIVE,
                    "validity_metadata": {"event_type": event.get("type")},
                },
            )
            return item
        finally:
            clear_db_tenant()

    @classmethod
    def propose_persistent(
        cls,
        tenant_id,
        agent_id: str,
        content: dict[str, Any],
        *,
        client: Any,
    ) -> MemoryItem:
        set_db_tenant(tenant_id)
        try:
            result = client.create_persistent(tenant_id, agent_id, content)
            return MemoryItem.objects.create(
                tenant_id=str(tenant_id),
                agent_id=agent_id,
                layer=MemoryItem.Layer.PERSISTENT,
                namespace=result["namespace"],
                content_hash=result["hash"],
                status=MemoryItem.Status.PROPOSED,
                validity_metadata={"source": "operator_proposal"},
            )
        finally:
            clear_db_tenant()

    @classmethod
    def approve_persistent(
        cls,
        item: MemoryItem,
        user: User,
        actor_role: str,
        *,
        client: Any,
        kb_chunks: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        tenant_id = item.tenant_id
        set_db_tenant(tenant_id)
        try:
            if item.layer != MemoryItem.Layer.PERSISTENT:
                raise ValueError("only persistent memories require human gate")
            if item.status != MemoryItem.Status.PROPOSED:
                raise ValueError("memory is not in proposed state")

            content = client.read_namespace(
                tenant_id, item.agent_id, kind="persistent"
            ) or {}
            check = MemoryConflictGuard.check(content, kb_chunks or [])

            if check.conflict:
                item.status = MemoryItem.Status.DISPUTED
                item.save(update_fields=["status", "updated_at"])
                conflict = MemoryConflict.objects.create(
                    tenant=item.tenant,
                    memory_item=item,
                    kb_source=check.kb_source,
                    kb_hash=check.kb_hash,
                    reason=check.reason,
                )
                emit_event(
                    str(tenant_id),
                    "memory.disputed",
                    {
                        "memory_id": str(item.id),
                        "conflict_id": str(conflict.id),
                        "reason": check.reason,
                    },
                )
                AuditWriter.write(
                    AuditContext(
                        tenant_id=tenant_id,
                        actor_id=user.id,
                        actor_role_at_decision=actor_role,
                    ),
                    action_id="memory.disputed",
                    payload={
                        "memory_id": str(item.id),
                        "conflict_id": str(conflict.id),
                        "reason": check.reason,
                    },
                )
                return {"status": item.status, "conflict": check.reason}

            item.status = MemoryItem.Status.ACTIVE
            item.promoted_by = user
            item.save(update_fields=["status", "promoted_by", "updated_at"])
            emit_event(
                str(tenant_id),
                "memory.promoted",
                {"memory_id": str(item.id), "agent_id": item.agent_id},
            )
            AuditWriter.write(
                AuditContext(
                    tenant_id=tenant_id,
                    actor_id=user.id,
                    actor_role_at_decision=actor_role,
                ),
                action_id="memory.promoted",
                payload={
                    "memory_id": str(item.id),
                    "agent_id": item.agent_id,
                    "namespace": item.namespace,
                },
            )
            return {"status": item.status}
        finally:
            clear_db_tenant()

    @classmethod
    def reject_persistent(
        cls,
        item: MemoryItem,
        user: User,
        actor_role: str,
    ) -> MemoryItem:
        tenant_id = item.tenant_id
        set_db_tenant(tenant_id)
        try:
            if item.status != MemoryItem.Status.PROPOSED:
                raise ValueError("memory is not in proposed state")
            item.status = MemoryItem.Status.DEPRECATED
            item.save(update_fields=["status", "updated_at"])
            emit_event(
                str(tenant_id),
                "memory.rejected",
                {"memory_id": str(item.id), "agent_id": item.agent_id},
            )
            AuditWriter.write(
                AuditContext(
                    tenant_id=tenant_id,
                    actor_id=user.id,
                    actor_role_at_decision=actor_role,
                ),
                action_id="memory.rejected",
                payload={"memory_id": str(item.id), "agent_id": item.agent_id},
            )
            return item
        finally:
            clear_db_tenant()

    @classmethod
    def deprecate(
        cls,
        item: MemoryItem,
        user: User,
        actor_role: str,
    ) -> MemoryItem:
        tenant_id = item.tenant_id
        set_db_tenant(tenant_id)
        try:
            item.status = MemoryItem.Status.DEPRECATED
            item.save(update_fields=["status", "updated_at"])
            emit_event(
                str(tenant_id),
                "memory.deprecated",
                {"memory_id": str(item.id), "agent_id": item.agent_id},
            )
            AuditWriter.write(
                AuditContext(
                    tenant_id=tenant_id,
                    actor_id=user.id,
                    actor_role_at_decision=actor_role,
                ),
                action_id="memory.deprecated",
                payload={"memory_id": str(item.id), "agent_id": item.agent_id},
            )
            return item
        finally:
            clear_db_tenant()

    @classmethod
    def sweep_expired_working(cls, tenant_id=None) -> int:
        cutoff = timezone.now() - timedelta(hours=cls.WORKING_TTL_HOURS)

        def _sweep(tid) -> int:
            set_db_tenant(tid)
            try:
                qs = MemoryItem.objects.filter(
                    tenant_id=str(tid),
                    layer=MemoryItem.Layer.WORKING,
                    status=MemoryItem.Status.ACTIVE,
                    created_at__lt=cutoff,
                )
                return qs.update(status=MemoryItem.Status.DEPRECATED)
            finally:
                clear_db_tenant()

        if tenant_id is not None:
            return _sweep(tenant_id)

        total = 0
        for tenant in Tenant.objects.filter(status=Tenant.Status.ACTIVE):
            total += _sweep(tenant.id)
        return total


class PromptAssembler:
    """Assemble the prompt context injected into an agent invocation."""

    INJECTABLE_STATUSES = {MemoryItem.Status.ACTIVE}

    @classmethod
    def for_agent(
        cls,
        tenant_id,
        agent_id: str,
        *,
        client: Any,
        kb_chunks: list[dict[str, Any]] | None = None,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        set_db_tenant(tenant_id)
        try:
            qs = MemoryItem.objects.filter(
                tenant_id=str(tenant_id),
                agent_id=agent_id,
                status__in=cls.INJECTABLE_STATUSES,
            )
            if task_id:
                # Task-scoped working memory plus agent-level episodic/persistent.
                items = qs.filter(
                    models.Q(task_id=task_id)
                    | models.Q(layer__in=(MemoryItem.Layer.EPISODIC, MemoryItem.Layer.PERSISTENT))
                )
            else:
                items = qs

            sections: dict[str, Any] = {
                "kb": kb_chunks or [],
                "working": [],
                "episodic": [],
                "persistent": [],
            }
            for item in items.select_related("tenant"):
                content = client.read_namespace(
                    tenant_id, agent_id, item.task_id or None, kind=item.layer
                )
                if content is None:
                    continue
                sections[item.layer].append(
                    {
                        "memory_id": str(item.id),
                        "namespace": item.namespace,
                        "content": content,
                    }
                )
            return sections
        finally:
            clear_db_tenant()

    @classmethod
    def to_prompt(cls, sections: dict[str, Any]) -> str:
        lines: list[str] = ["# Context"]
        if sections.get("kb"):
            lines.append("## Knowledge Base")
            for chunk in sections["kb"]:
                text = chunk.get("text") if isinstance(chunk, dict) else str(chunk)
                if text:
                    lines.append(f"- {text}")
        for layer in ("persistent", "working", "episodic"):
            entries = sections.get(layer, [])
            if not entries:
                continue
            lines.append(f"## {layer.capitalize()} memory")
            for entry in entries:
                lines.append(f"- {entry['namespace']}: {entry['content']}")
        return "\n".join(lines)
