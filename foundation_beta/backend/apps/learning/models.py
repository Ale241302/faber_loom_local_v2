"""M14 Outcome Ledger, Gold Samples and Learning Thermometer models."""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TenantScopedModel


class OutcomeLedgerEntry(TenantScopedModel):
    """Immutable record of a human decision on a draft or classification."""

    class Decision(models.TextChoices):
        APPROVED = "approved", "Approved"
        EDITED = "edited", "Edited"
        REJECTED = "rejected", "Rejected"
        RECLASSIFIED = "reclassified", "Reclassified"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    draft = models.ForeignKey(
        "drafts.Draft",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="draft_id",
    )
    classification_result = models.ForeignKey(
        "classifier.ClassificationResult",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="classification_result_id",
    )
    decision = models.CharField(max_length=16, choices=Decision.choices)
    diff = models.JSONField(default=dict, blank=True)
    reason = models.TextField(blank=True)
    confidence = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=True,
        blank=True,
    )
    actor_id = models.CharField(max_length=64)
    actor_role_at_decision = models.CharField(max_length=32)
    decision_time_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "outcome_ledger_entries"
        indexes = [
            models.Index(fields=["tenant", "decision", "created_at"], name="idx_ledger_tenant_decision"),
        ]


class GoldSample(TenantScopedModel):
    """Human-validated input/output pair that can be promoted to train skills."""

    class Status(models.TextChoices):
        CANDIDATE = "candidate", "Candidate"
        ACTIVE = "active", "Active"
        DISCARDED = "discarded", "Discarded"
        DEPRECATED = "deprecated", "Deprecated"
        BLOCKED_PENDING_SECOND_APPROVER = (
            "blocked_pending_second_approver",
            "Blocked pending second approver",
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_id = models.CharField(max_length=255)
    skill_id = models.CharField(max_length=255, blank=True)
    input_json = models.JSONField(default=dict)
    output_json = models.JSONField(default=dict)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.CANDIDATE,
    )
    validations_json = models.JSONField(default=dict, blank=True)
    promoter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="promoted_gold_samples",
        db_column="promoter_id",
    )
    second_approver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="second_approved_gold_samples",
        db_column="second_approver_id",
    )
    promoted_at = models.DateTimeField(null=True, blank=True)
    validity_metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "gold_samples"
        indexes = [
            models.Index(fields=["tenant", "status", "created_at"], name="idx_gold_tenant_status"),
        ]


class LearningThermometer(models.Model):
    """Per-agent learning score used by the Learning Thermometer."""

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        db_column="tenant_id",
    )
    agent_id = models.CharField(max_length=255)
    score = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_thermometers"
        constraints = [
            models.UniqueConstraint(fields=["tenant", "agent_id"], name="unique_thermometer_tenant_agent"),
        ]

    @property
    def bucket(self) -> str:
        cold_max = int(getattr(settings, "THERMOMETER_COLD_MAX", 2))
        warm_max = int(getattr(settings, "THERMOMETER_WARM_MAX", 5))
        if self.score <= cold_max:
            return "cold"
        if self.score <= warm_max:
            return "warm"
        return "hot"
