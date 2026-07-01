"""Outbox event model for M15 (stub used by M08 auth events)."""
from __future__ import annotations

import uuid

from django.db import models

from apps.tenants.models import Tenant


class OutboxEvent(models.Model):
    """Transactional outbox row used to emit domain events."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_column="tenant_id")
    event_type = models.CharField(max_length=128)
    payload = models.JSONField(default=dict)
    correlation_id = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "outbox_events"
        indexes = [
            models.Index(fields=["tenant", "event_type"], name="idx_outbox_tenant_type"),
            models.Index(fields=["created_at"], name="idx_outbox_created_at"),
        ]
