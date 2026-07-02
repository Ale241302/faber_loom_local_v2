"""Policy / D9 gate models for M11."""
from __future__ import annotations

import uuid

from django.db import models

from apps.tenants.models import Tenant
from apps.users.models import User


class DpaStatus(models.TextChoices):
    MISSING = "missing", "Missing"
    SIGNED = "signed", "Signed"
    BLOCKED = "blocked", "Blocked"


class DataClass(models.TextChoices):
    N0 = "N0", "N0"
    N1 = "N1", "N1"
    N2 = "N2", "N2"
    N3 = "N3", "N3"
    N4 = "N4", "N4"


class DpaStatement(models.Model):
    """Data Processing Agreement state per tenant."""

    Status = DpaStatus

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.OneToOneField(
        Tenant,
        db_column="tenant_id",
        on_delete=models.CASCADE,
        related_name="dpa_statement",
    )
    status = models.CharField(
        max_length=16,
        choices=DpaStatus.choices,
        default=DpaStatus.MISSING,
    )
    signed_by = models.ForeignKey(
        User,
        db_column="signed_by",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="signed_dpas",
    )
    signed_at = models.DateTimeField(null=True, blank=True)
    version = models.TextField(default="v1")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "dpa_statements"


class DataClassificationDefault(models.Model):
    """Default data class for a source type within a tenant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        db_column="tenant_id",
        on_delete=models.CASCADE,
        related_name="classification_defaults",
    )
    source_type = models.TextField()
    default_class = models.CharField(
        max_length=2,
        choices=DataClass.choices,
        default=DataClass.N1,
    )
    overrides = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "data_classification_defaults"
        unique_together = [("tenant", "source_type")]


class PolicyBlock(models.Model):
    """Immutable record of a policy block decision."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        db_column="tenant_id",
        on_delete=models.CASCADE,
        related_name="policy_blocks",
    )
    case_id = models.TextField(blank=True, null=True)
    declared_class = models.CharField(max_length=2, choices=DataClass.choices)
    effective_class = models.CharField(max_length=2, choices=DataClass.choices)
    reason = models.TextField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        db_column="resolved_by",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_blocks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "policy_blocks"
