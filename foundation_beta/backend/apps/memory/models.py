"""Models for M17 Memory Letta layer."""
from __future__ import annotations

import uuid

from django.db import models

from apps.core.models import TenantScopedModel
from apps.users.models import User


class MemoryItem(TenantScopedModel):
    """Metadata of a memory entry stored in the external Letta namespace.

    The actual content lives in the Letta-backed namespace; this table keeps
    Postgres-indexed metadata, status and gate provenance for RLS and queries.
    """

    class Layer(models.TextChoices):
        WORKING = "working", "Working"
        EPISODIC = "episodic", "Episodic"
        PERSISTENT = "persistent", "Persistent"

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PROPOSED = "proposed", "Proposed"
        DEPRECATED = "deprecated", "Deprecated"
        DISPUTED = "disputed", "Disputed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=128)
    task_id = models.CharField(max_length=128, blank=True)
    layer = models.CharField(max_length=16, choices=Layer.choices)
    namespace = models.CharField(max_length=255, db_index=True)
    content_hash = models.CharField(max_length=64, blank=True)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.ACTIVE
    )
    promoted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    validity_metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "memory_items"
        indexes = [
            models.Index(
                fields=["tenant", "agent_id", "layer", "status"],
                name="idx_memory_agent_layer_status",
            ),
            models.Index(
                fields=["namespace", "status"],
                name="idx_memory_namespace_status",
            ),
        ]


class MemoryConflict(TenantScopedModel):
    """Record of a Letta memory proposal that collided with a KB source.

    KB always wins: a conflict deprecates the proposed memory and forces a
    curator decision before the memory can ever be injected into a prompt.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    memory_item = models.ForeignKey(
        MemoryItem,
        on_delete=models.CASCADE,
        related_name="conflicts",
    )
    kb_source = models.CharField(max_length=255)
    kb_hash = models.CharField(max_length=64)
    reason = models.TextField()
    resolved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "memory_conflicts"
        indexes = [
            models.Index(
                fields=["tenant", "memory_item"],
                name="idx_conflict_tenant_memory",
            ),
        ]
