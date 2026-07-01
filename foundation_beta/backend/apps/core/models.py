"""Core models for tenant isolation testing and reference."""
from __future__ import annotations

import uuid

from django.db import models

from apps.tenants.models import Tenant


class TenantScopedModel(models.Model):
    """Abstract base for all tenant-scoped models."""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        db_column="tenant_id",
    )

    class Meta:
        abstract = True


class SampleItem(TenantScopedModel):
    """Minimal tenant-scoped model used by M16 cross-tenant tests."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sample_items"
        indexes = [
            models.Index(fields=["tenant"], name="idx_sample_items_tenant_id"),
        ]
