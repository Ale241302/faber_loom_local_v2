"""Outcome ledger writer for M14."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apps.audit.writer import AuditContext
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.events.emit import emit_event
from apps.learning.models import GoldSample, OutcomeLedgerEntry

if TYPE_CHECKING:
    from apps.drafts.models import Draft


class LedgerWriter:
    """Record immutable human decisions and spawn gold samples."""

    GOLD_CONFIDENCE_THRESHOLD = 0.85

    @classmethod
    def record_decision(
        cls,
        ctx: AuditContext,
        draft: "Draft | None" = None,
        decision: OutcomeLedgerEntry.Decision = OutcomeLedgerEntry.Decision.APPROVED,
        *,
        diff: dict[str, Any] | None = None,
        reason: str = "",
        decision_time_ms: int | None = None,
        classification_result: Any = None,
    ) -> OutcomeLedgerEntry:
        tenant_id = str(ctx.tenant_id)
        set_db_tenant(ctx.tenant_id)
        try:
            confidence = None
            agent_id = ""
            task_payload = {}
            original_content = {}
            data_class = "N1"

            if draft and draft.task:
                task = draft.task
                agent_id = task.agent_id
                task_payload = task.payload
                original_content = draft.edited_content or draft.original_content
                if task.classification_result:
                    confidence = float(task.classification_result.confidence)
                    data_class = cls._extract_data_class(task.classification_result.action_context)
            elif classification_result:
                confidence = float(classification_result.confidence)
                data_class = cls._extract_data_class(classification_result.action_context)
                agent_id = (
                    classification_result.action_context.get("agent_id", "")
                    if isinstance(classification_result.action_context, dict)
                    else ""
                )

            entry = OutcomeLedgerEntry.objects.create(
                tenant_id=tenant_id,
                draft=draft,
                classification_result=classification_result,
                decision=decision,
                diff=diff or {},
                reason=reason,
                confidence=confidence,
                actor_id=str(ctx.actor_id),
                actor_role_at_decision=ctx.actor_role_at_decision or "system",
                decision_time_ms=decision_time_ms,
            )

            emit_event(
                tenant_id=tenant_id,
                event_type="ledger.entry.created",
                payload={
                    "entry_id": str(entry.id),
                    "decision": entry.decision,
                    "draft_id": str(draft.id) if draft else None,
                    "agent_id": agent_id,
                },
            )

            if (
                decision == OutcomeLedgerEntry.Decision.APPROVED
                and not diff
                and confidence is not None
                and confidence >= cls.GOLD_CONFIDENCE_THRESHOLD
            ):
                cls._create_candidate(
                    tenant_id=tenant_id,
                    agent_id=agent_id,
                    draft=draft,
                    input_json=task_payload,
                    output_json=original_content,
                    data_class=data_class,
                )

            return entry
        finally:
            clear_db_tenant()

    @staticmethod
    def _extract_data_class(action_context) -> str:
        if isinstance(action_context, dict):
            return action_context.get("data_class", "N1")
        return "N1"

    @classmethod
    def _create_candidate(
        cls,
        *,
        tenant_id: str,
        agent_id: str,
        draft: "Draft | None",
        input_json: dict[str, Any],
        output_json: dict[str, Any],
        data_class: str,
    ) -> None:
        skill_id = ""
        if draft and draft.task:
            skill_id = draft.task.agent_id

        GoldSample.objects.create(
            tenant_id=tenant_id,
            agent_id=agent_id,
            skill_id=skill_id,
            input_json=input_json,
            output_json=output_json,
            status=GoldSample.Status.CANDIDATE,
            validity_metadata={"data_class": data_class, "source": "hitl_approval"},
        )
        emit_event(
            tenant_id=tenant_id,
            event_type="gold.candidate.created",
            payload={"agent_id": agent_id, "draft_id": str(draft.id) if draft else None},
        )
