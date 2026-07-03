"""Task entity for FaberLoom Foundation Beta."""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TenantScopedModel


class Task(TenantScopedModel):
    """A unit of agent execution. Owned by the tasks app; consumed by classifier, drafts, etc."""

    class InvocationMode(models.TextChoices):
        AD_HOC = "ad_hoc", "Ad hoc"
        SCHEDULED = "scheduled", "Scheduled"
        WEBHOOK = "webhook", "Webhook"
        FLOW_NODE = "flow_node", "Flow node"
        INBOUND = "inbound", "Inbound"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        NORMAL = "normal", "Normal"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        AWAITING_APPROVAL = "awaiting_approval", "Awaiting approval"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        TIMEOUT = "timeout", "Timeout"

    class ReviewStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        EDIT_LIGHT = "edit_light", "Edit light"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=255)
    invocation_mode = models.CharField(
        max_length=16,
        choices=InvocationMode.choices,
        default=InvocationMode.INBOUND,
    )
    invoked_by = models.CharField(max_length=128, default="system")
    priority = models.CharField(
        max_length=8,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    payload = models.JSONField(default=dict)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.QUEUED,
    )
    expected_completion_by = models.DateTimeField(null=True, blank=True)
    classification_result = models.ForeignKey(
        "classifier.ClassificationResult",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="classification_result_id",
    )
    parent_task = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="parent_task_id",
    )

    # HITL review fields (M13 Draft HITL)
    review_status = models.CharField(
        max_length=16,
        choices=ReviewStatus.choices,
        null=True,
        blank=True,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="reviewed_by_id",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True, default="")
    outputs = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
        indexes = [
            models.Index(
                fields=["tenant", "status", "expected_completion_by"],
                name="idx_tasks_tenant_status",
            ),
        ]
