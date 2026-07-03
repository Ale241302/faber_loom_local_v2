"""Draft HITL models for Foundation Beta M13."""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TenantScopedModel


class DraftStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    AWAITING_APPROVAL = "awaiting_approval", "Awaiting approval"
    APPROVED = "approved", "Approved"
    EDITED = "edited", "Edited"
    REJECTED = "rejected", "Rejected"
    SENT = "sent", "Sent"
    EXPIRED = "expired", "Expired"
    APPROVED_PENDING_SEND = "approved_pending_send", "Approved pending send"


class EditClassification(models.TextChoices):
    TONE = "tone", "Tone"
    DATA = "data", "Data"
    STRUCTURE = "structure", "Structure"
    POLICY = "policy", "Policy"
    SCOPE = "scope", "Scope"
    CONTEXT = "context", "Context"


class Channel(models.TextChoices):
    EMAIL = "email", "Email"
    WHATSAPP = "whatsapp", "WhatsApp"


class Draft(TenantScopedModel):
    """A human-gated draft output waiting for approval."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        db_column="task_id",
        related_name="drafts",
    )
    status = models.CharField(
        max_length=32,
        choices=DraftStatus.choices,
        default=DraftStatus.PENDING,
    )
    original_content = models.JSONField(default=dict)
    edited_content = models.JSONField(null=True, blank=True)
    edit_reason = models.TextField(blank=True, default="")
    edit_classification = models.CharField(
        max_length=16,
        choices=EditClassification.choices,
        null=True,
        blank=True,
    )
    evidence_bundle = models.ForeignKey(
        "drafts.EvidenceBundle",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="evidence_bundle_id",
        related_name="drafts",
    )
    channel = models.CharField(
        max_length=16,
        choices=Channel.choices,
        default=Channel.EMAIL,
    )
    recipient = models.CharField(max_length=255, blank=True, default="")
    approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="approver_id",
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drafts"
        indexes = [
            models.Index(fields=["tenant", "status", "expires_at"], name="idx_drafts_tenant_status"),
            models.Index(fields=["task"], name="idx_drafts_task"),
        ]


class EvidenceBundle(TenantScopedModel):
    """Immutable evidence backing a draft (client/internal views + hash)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    draft = models.ForeignKey(
        Draft,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        db_column="draft_id",
        related_name="evidence_bundles",
    )
    task = models.ForeignKey(
        "tasks.Task",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="task_id",
        related_name="evidence_bundles",
    )
    bundle_json = models.JSONField(default=dict)
    bundle_hash = models.CharField(max_length=64)
    client_view = models.JSONField(default=dict)
    internal_view = models.JSONField(default=dict)
    privacy_classification = models.CharField(max_length=2, default="N2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "evidence_bundles"
        indexes = [
            models.Index(fields=["draft"], name="idx_evidence_bundles_draft"),
        ]


class OscillationCounter(TenantScopedModel):
    """Tracks consecutive clean approvals per user/agent to detect oscillation."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="user_id",
    )
    agent_id = models.CharField(max_length=255)
    consecutive_clean_approvals = models.IntegerField(default=0)
    last_reset_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "oscillation_counters"
        unique_together = [("tenant", "user", "agent_id")]
