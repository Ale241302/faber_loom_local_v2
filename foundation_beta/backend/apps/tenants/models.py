"""Tenant models for Foundation Beta."""
from __future__ import annotations

import uuid

from django.db import models


class Tenant(models.Model):
    class Status(models.TextChoices):
        SETUP = "setup", "Setup"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    legal_name = models.CharField(max_length=255)
    commercial_name = models.CharField(max_length=255, blank=True)
    vertical_spec_object_id = models.CharField(max_length=255)
    plan_tier = models.CharField(max_length=64)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SETUP)
    config_json = models.JSONField(default=dict)
    dpa_state = models.CharField(
        max_length=16,
        choices=[
            ("missing", "Missing"),
            ("signed", "Signed"),
            ("blocked", "Blocked"),
        ],
        default="missing",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants"
        indexes = [
            models.Index(fields=["slug"], name="idx_tenants_slug"),
            models.Index(fields=["status"], name="idx_tenants_status"),
        ]


class TenantPlanFeatures(models.Model):
    class DataClass(models.TextChoices):
        N0 = "N0", "N0"
        N1 = "N1", "N1"
        N2 = "N2", "N2"
        N3 = "N3", "N3"
        N4 = "N4", "N4"

    tenant = models.OneToOneField(
        Tenant,
        primary_key=True,
        on_delete=models.CASCADE,
        db_column="tenant_id",
    )
    data_class_ceiling = models.CharField(max_length=2, choices=DataClass.choices, default=DataClass.N2)
    max_seats = models.PositiveIntegerField(default=2)
    allow_agent_composition = models.BooleanField(default=False)
    allow_tools_in_skills = models.BooleanField(default=False)
    allow_email_connector = models.BooleanField(default=False)
    allow_whatsapp_connector = models.BooleanField(default=False)

    class Meta:
        db_table = "tenant_plan_features"
        indexes = [
            models.Index(fields=["tenant"], name="idx_tpf_tenant_id"),
        ]
