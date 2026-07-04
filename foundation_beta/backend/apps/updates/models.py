"""Models for M20 Auto Update."""
from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models

from apps.core.models import TenantScopedModel


class ClientRelease(models.Model):
    """Global release catalog per platform and update channel."""

    class Channel(models.TextChoices):
        STABLE = "stable", "Stable"
        BETA = "beta", "Beta"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.CharField(max_length=32)
    platform = models.CharField(max_length=16)
    channel = models.CharField(max_length=16, choices=Channel.choices)
    feed_url = models.URLField()
    published_at = models.DateTimeField(auto_now_add=True)
    retired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "client_releases"
        unique_together = [("version", "platform", "channel")]
        indexes = [
            models.Index(
                fields=["platform", "channel", "published_at"],
                name="idx_releases_platform_channel",
            ),
        ]


class SystemConfig(models.Model):
    """Singleton-style global configuration values."""

    key = models.CharField(primary_key=True, max_length=64)
    value = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "system_configs"


class TenantUpdateChannel(TenantScopedModel):
    """Update channel assigned to a tenant (default stable)."""

    class Channel(models.TextChoices):
        STABLE = "stable", "Stable"
        BETA = "beta", "Beta"

    channel = models.CharField(
        max_length=16,
        choices=Channel.choices,
        default=Channel.STABLE,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenant_update_channels"


class ClientVersionTelemetry(TenantScopedModel):
    """Reported client version per user/session."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="user_id",
    )
    client_version = models.CharField(max_length=32)
    platform = models.CharField(max_length=16)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "client_version_telemetry"
        indexes = [
            models.Index(
                fields=["tenant", "reported_at"],
                name="idx_telemetry_tenant_reported",
            ),
        ]
