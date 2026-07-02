"""Outbox and event log models for M15 Outbox Streams."""
from __future__ import annotations

import uuid

from django.db import models

from apps.tenants.models import Tenant


class OutboxStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PUBLISHED = "published", "Published"
    FAILED = "failed", "Failed"


class Outbox(models.Model):
    """Transactional outbox row written in the same transaction as the business change."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_column="tenant_id")
    event_id = models.CharField(max_length=64, unique=True)
    event_type = models.CharField(max_length=128)
    payload_json = models.JSONField(default=dict)
    seq_no = models.BigIntegerField()
    status = models.CharField(
        max_length=16, choices=OutboxStatus.choices, default=OutboxStatus.PENDING
    )
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "outbox"
        indexes = [
            models.Index(fields=["status", "created_at"], name="idx_outbox_status"),
            models.Index(fields=["tenant", "status"], name="idx_outbox_tenant"),
        ]


class EventLog(models.Model):
    """Immutable published event log used for replay and audit."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_column="tenant_id")
    event_id = models.CharField(max_length=64, unique=True)
    event_type = models.CharField(max_length=128)
    payload_json = models.JSONField(default=dict)
    seq_no = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "event_log"
        indexes = [
            models.Index(
                fields=["tenant", "seq_no"], name="idx_event_log_tenant_seq"
            ),
        ]
