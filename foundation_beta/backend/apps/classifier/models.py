"""L1 Classifier models for FaberLoom Foundation Beta M10."""
from __future__ import annotations

import uuid

from django.db import models

from apps.core.models import TenantScopedModel


class DataClass(models.TextChoices):
    N0 = "N0", "N0"
    N1 = "N1", "N1"
    N2 = "N2", "N2"
    N3 = "N3", "N3"
    N4 = "N4", "N4"


class FeedItemStatus(models.TextChoices):
    RECEIVED = "received", "Received"
    CLASSIFYING = "classifying", "Classifying"
    CLASSIFIED = "classified", "Classified"
    PENDING_HUMAN_REVIEW = "pending_human_review", "Pending human review"
    ROUTED_TO_TASK = "routed_to_task", "Routed to task"
    ARCHIVED = "archived", "Archived"
    FAILED = "failed", "Failed"
    MANUAL_REVIEW = "manual_review", "Manual review"


class FeedItem(TenantScopedModel):
    """Inbound item waiting for classification."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_type = models.CharField(max_length=16)
    external_id = models.CharField(max_length=255, blank=True, null=True)
    raw_payload = models.JSONField(default=dict)
    normalized_payload = models.JSONField(default=dict)
    data_class = models.CharField(
        max_length=2,
        choices=DataClass.choices,
        default=DataClass.N1,
    )
    status = models.CharField(
        max_length=32,
        choices=FeedItemStatus.choices,
        default=FeedItemStatus.RECEIVED,
    )
    received_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "feed_items"
        indexes = [
            models.Index(
                fields=["tenant", "status", "received_at"],
                name="idx_feed_items_tenant_status",
            ),
        ]


class ClassifierSkillStatus(models.TextChoices):
    SHADOW = "shadow", "Shadow"
    ACTIVE = "active", "Active"
    DEPRECATED = "deprecated", "Deprecated"


class ClassifierSkillManager(models.Manager):
    def get_active(self, tenant_id: str | uuid.UUID) -> "ClassifierSkill":
        return self.get(tenant_id=tenant_id, status=ClassifierSkillStatus.ACTIVE)


class ClassifierSkill(TenantScopedModel):
    """Prompt+schema+threshold configuration for the L1 classifier."""

    Status = ClassifierSkillStatus

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    origin = models.CharField(max_length=16, default="system")
    prompt_template = models.TextField()
    output_schema = models.JSONField(default=dict)
    threshold = models.DecimalField(max_digits=4, decimal_places=3, default=0.85)
    model_id = models.CharField(
        max_length=128,
        default="anthropic/claude-3-5-haiku-20241022",
    )
    timeout_ms = models.IntegerField(default=10000)
    cost_cap_usd = models.DecimalField(max_digits=8, decimal_places=4, default=0.05)
    status = models.CharField(
        max_length=16,
        choices=ClassifierSkillStatus.choices,
        default=ClassifierSkillStatus.ACTIVE,
    )
    active_version = models.CharField(max_length=32, default="1")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ClassifierSkillManager()

    class Meta:
        db_table = "classifier_skills"


class ClassificationResultStatus(models.TextChoices):
    CLASSIFIED = "classified", "Classified"
    PENDING_HUMAN_REVIEW = "pending_human_review", "Pending human review"
    ROUTED_TO_TASK = "routed_to_task", "Routed to task"
    FAILED = "failed", "Failed"


class ClassificationResult(TenantScopedModel):
    """Result of classifying a feed item."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feed_item = models.ForeignKey(
        FeedItem,
        on_delete=models.CASCADE,
        db_column="feed_item_id",
        related_name="classification_results",
    )
    classifier_skill = models.ForeignKey(
        ClassifierSkill,
        on_delete=models.RESTRICT,
        db_column="classifier_skill_id",
    )
    action_context = models.JSONField(default=dict)
    features = models.JSONField(default=dict)
    confidence = models.DecimalField(max_digits=4, decimal_places=3)
    routing_zone = models.CharField(max_length=16, default="zone_4")
    status = models.CharField(
        max_length=32,
        choices=ClassificationResultStatus.choices,
        default=ClassificationResultStatus.CLASSIFIED,
    )
    model_id = models.CharField(max_length=128, blank=True, null=True)
    model_version = models.CharField(max_length=32, blank=True, null=True)
    latency_ms = models.IntegerField(null=True, blank=True)
    cost_usd = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "classification_results"
        indexes = [
            models.Index(
                fields=["feed_item"],
                name="idx_clsresult_feed_item",
            ),
        ]


class Tier0Rule(TenantScopedModel):
    """Deterministic classification rule."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    pattern = models.JSONField(default=dict)
    priority = models.IntegerField(default=0)
    action_context = models.JSONField(default=dict)
    origin = models.CharField(max_length=16, default="system")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tier0_rules"
        indexes = [
            models.Index(
                fields=["tenant", "priority"],
                name="idx_t0_rules_tenant_priority",
            ),
        ]
