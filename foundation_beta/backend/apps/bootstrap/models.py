"""Bootstrap Wizard models for M07."""
from __future__ import annotations

import uuid

from django.db import models

from apps.tenants.models import Tenant
from apps.users.models import User


class TenantBootstrapProgress(models.Model):
    """Mutable wizard progress for a tenant."""

    tenant = models.OneToOneField(
        Tenant,
        db_column="tenant_id",
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="bootstrap_progress",
    )
    steps_completed = models.JSONField(default=list)
    steps_blocked = models.JSONField(default=list)
    sandbox_result = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenant_bootstrap_progress"


class EmailBinding(models.Model):
    """Inbound/outbound mailbox connected to a tenant."""

    class Provider(models.TextChoices):
        GMAIL_OAUTH = "gmail_oauth", "Gmail OAuth"
        IMAP_SMTP = "imap_smtp", "IMAP/SMTP"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        db_column="tenant_id",
        on_delete=models.CASCADE,
        related_name="email_bindings",
    )
    provider = models.CharField(max_length=16, choices=Provider.choices)
    account = models.TextField()
    credentials_encrypted = models.TextField()
    is_default = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "email_bindings"


class VoiceProfile(models.Model):
    """Voice/persona profile for outbound communication."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        db_column="tenant_id",
        on_delete=models.CASCADE,
        related_name="voice_profiles",
    )
    user = models.ForeignKey(
        User,
        db_column="user_id",
        on_delete=models.CASCADE,
        related_name="voice_profiles",
    )
    persona = models.TextField()
    tone = models.TextField()
    glossary = models.JSONField(default=list)
    greeting = models.TextField(blank=True)
    signature = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "voice_profiles"


class SystemAgent(models.Model):
    """System-owned agents seeded during bootstrap."""

    class Status(models.TextChoices):
        SHADOW = "shadow", "Shadow"
        ACTIVE = "active", "Active"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        db_column="tenant_id",
        on_delete=models.CASCADE,
        related_name="system_agents",
    )
    name = models.TextField()
    origin = models.TextField(default="system")
    skill_md = models.TextField()
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.SHADOW,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "system_agents"
