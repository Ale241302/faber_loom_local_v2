"""Outcome ledger models for Foundation Beta (M14 minimal hook for M13)."""
from __future__ import annotations

import uuid

from django.db import models

from apps.core.models import TenantScopedModel


class OutcomeEntry(TenantScopedModel):
    """Immutable record of a human/agent decision on a draft or task."""

    class Action(models.TextChoices):
        APPROVED = "approved", "Approved"
        EDITED = "edited", "Edited"
        REJECTED = "rejected", "Rejected"
        SENT = "sent", "Sent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    draft = models.ForeignKey(
        "drafts.Draft",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="draft_id",
    )
    task = models.ForeignKey(
        "tasks.Task",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="task_id",
    )
    action = models.CharField(max_length=16, choices=Action.choices)
    diff = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "outcome_entries"
        indexes = [
            models.Index(fields=["tenant", "created_at"], name="idx_outcome_tenant_created"),
        ]
