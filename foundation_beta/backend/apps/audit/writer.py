"""Audit writer for M12 Audit Trail."""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from typing import Any

from django.db import connection, transaction

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.events.emit import emit_event

from .models import AuditLog


@dataclass
class AuditContext:
    """Actor context captured at the decision point."""

    tenant_id: str | uuid.UUID
    actor_id: str | uuid.UUID
    actor_role_at_decision: str


class AuditWriter:
    """Write immutable, chained audit entries for a tenant."""

    @classmethod
    def write(
        cls,
        ctx: AuditContext,
        action_id: str,
        *,
        case_id: str | None = None,
        data_class: str = "N1",
        task_type: str | None = None,
        model_provider: str | None = None,
        model_id: str | None = None,
        model_version: str | None = None,
        policy_pool_hash: str | None = None,
        prompt_hash: str | None = None,
        output_hash: str | None = None,
        human_gate_required: bool = False,
        human_approver_id: str | uuid.UUID | None = None,
        payload: dict[str, Any] | None = None,
        emit: bool = True,
    ) -> AuditLog:
        tenant_id = str(ctx.tenant_id)
        chain_id = f"{tenant_id}:default"
        payload = payload or {}

        with transaction.atomic():
            set_db_tenant(tenant_id)
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT nextval('audit_seq')")
                    (seq_no,) = cursor.fetchone()

                    cursor.execute(
                        """
                        SELECT sha_chain_curr FROM audit_log
                        WHERE chain_id = %s
                        ORDER BY seq_no DESC
                        LIMIT 1
                        """,
                        [chain_id],
                    )
                    row = cursor.fetchone()
                    sha_chain_prev = row[0] if row else "0" * 64

                payload_blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
                hash_input = (
                    f"{tenant_id}|{case_id}|{action_id}|{data_class}|{task_type}|"
                    f"{model_provider}|{model_id}|{model_version}|{policy_pool_hash}|"
                    f"{prompt_hash}|{output_hash}|{human_gate_required}|{human_approver_id}|"
                    f"{seq_no}|{chain_id}|{payload_blob}|{sha_chain_prev}"
                )
                sha_chain_curr = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

                log = AuditLog.objects.create(
                    tenant_id=tenant_id,
                    case_id=case_id,
                    action_id=action_id,
                    data_class=data_class,
                    task_type=task_type,
                    model_provider=model_provider,
                    model_id=model_id,
                    model_version=model_version,
                    orchestrator_policy_pool_hash=policy_pool_hash,
                    prompt_hash=prompt_hash,
                    output_hash=output_hash,
                    human_gate_required=human_gate_required,
                    human_approver_id=str(human_approver_id) if human_approver_id else None,
                    sha_chain_prev=sha_chain_prev,
                    sha_chain_curr=sha_chain_curr,
                    seq_no=seq_no,
                    chain_id=chain_id,
                    actor_id=str(ctx.actor_id),
                    actor_role_at_decision=ctx.actor_role_at_decision,
                    payload_json=payload,
                )

                if emit:
                    emit_event(
                        tenant_id=tenant_id,
                        event_type="audit.entry.created",
                        payload={
                            "audit_id": str(log.id),
                            "action_id": action_id,
                            "actor_id": str(ctx.actor_id),
                            "actor_role_at_decision": ctx.actor_role_at_decision,
                            "seq_no": seq_no,
                            "chain_id": chain_id,
                        },
                    )

                return log
            finally:
                clear_db_tenant()
