"""Celery tasks for M12 Audit Trail chain validation."""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from celery import shared_task
from django.db import transaction

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.tenants.models import Tenant

from .models import AuditLog

logger = logging.getLogger(__name__)


def _recompute_hash(entry: AuditLog) -> str:
    payload_blob = json.dumps(entry.payload_json or {}, sort_keys=True, ensure_ascii=False)
    hash_input = (
        f"{entry.tenant_id}|{entry.case_id}|{entry.action_id}|{entry.data_class}|{entry.task_type}|"
        f"{entry.model_provider}|{entry.model_id}|{entry.model_version}|{entry.orchestrator_policy_pool_hash}|"
        f"{entry.prompt_hash}|{entry.output_hash}|{entry.human_gate_required}|{entry.human_approver_id}|"
        f"{entry.seq_no}|{entry.chain_id}|{payload_blob}|{entry.sha_chain_prev}"
    )
    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


def validate_chain(tenant_id: str, chain_id: str) -> dict[str, Any]:
    """Validate the integrity of a single audit chain."""
    with transaction.atomic():
        set_db_tenant(tenant_id)
        entries = list(
            AuditLog.objects.filter(chain_id=chain_id).order_by("seq_no")
        )
    clear_db_tenant()

    breaks = []
    previous_hash = "0" * 64
    checked = 0

    for entry in entries:
        if entry.sha_chain_prev != previous_hash:
            breaks.append(
                {
                    "seq_no": entry.seq_no,
                    "reason": "prev_hash_mismatch",
                    "expected": previous_hash,
                    "found": entry.sha_chain_prev,
                }
            )
        expected = _recompute_hash(entry)
        if entry.sha_chain_curr != expected:
            breaks.append(
                {
                    "seq_no": entry.seq_no,
                    "reason": "curr_hash_mismatch",
                    "expected": expected,
                    "found": entry.sha_chain_curr,
                }
            )
        previous_hash = entry.sha_chain_curr
        checked += 1

    return {
        "tenant_id": tenant_id,
        "chain_id": chain_id,
        "checked": checked,
        "valid": len(breaks) == 0,
        "breaks": breaks,
    }


@shared_task
def validate_audit_chains() -> dict[str, Any]:
    """Daily job: validate every audit chain for every tenant."""
    report = {"chains": [], "broken_chains": []}
    for tenant in Tenant.objects.filter(status=Tenant.Status.ACTIVE):
        chain_id = f"{tenant.id}:default"
        result = validate_chain(str(tenant.id), chain_id)
        report["chains"].append(result)
        if not result["valid"]:
            report["broken_chains"].append(result)
            logger.error(
                "M12 P0 audit chain rupture tenant=%s chain=%s breaks=%s",
                tenant.id,
                chain_id,
                result["breaks"],
            )
    return report
