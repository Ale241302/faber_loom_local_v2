"""Immutable audit log for M12 Audit Trail."""
from __future__ import annotations

import uuid

from django.db import models

from apps.tenants.models import Tenant
from apps.users.models import User


class AuditLog(models.Model):
    """Append-only, tenant-scoped audit entry with hash chain."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        Tenant,
        db_column="tenant_id",
        on_delete=models.CASCADE,
    )
    case_id = models.TextField(blank=True, null=True)
    action_id = models.TextField()
    data_class = models.TextField(default="N1")
    task_type = models.TextField(blank=True, null=True)
    model_provider = models.TextField(blank=True, null=True)
    model_id = models.TextField(blank=True, null=True)
    model_version = models.TextField(blank=True, null=True)
    orchestrator_policy_pool_hash = models.TextField(blank=True, null=True)
    prompt_hash = models.TextField(blank=True, null=True)
    output_hash = models.TextField(blank=True, null=True)
    human_gate_required = models.BooleanField(default=False)
    human_approver = models.ForeignKey(
        User,
        db_column="human_approver_id",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    sha_chain_prev = models.TextField()
    sha_chain_curr = models.TextField()
    seq_no = models.BigIntegerField()
    chain_id = models.TextField()
    actor_id = models.UUIDField()
    actor_role_at_decision = models.TextField()
    payload_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        indexes = [
            models.Index(fields=["tenant", "chain_id", "seq_no"], name="idx_audit_tenant_chain_seq"),
            models.Index(fields=["tenant", "case_id", "created_at"], name="idx_audit_tenant_case"),
            models.Index(fields=["tenant", "actor_id", "created_at"], name="idx_audit_tenant_actor"),
        ]
