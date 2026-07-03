"""Draft HITL service for M13."""
from __future__ import annotations

import json
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.audit.writer import AuditContext, AuditWriter
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.drafts.channel_sender import ChannelSender
from apps.drafts.generators import DraftGenerator
from apps.drafts.models import Channel, Draft, DraftStatus, EditClassification
from apps.drafts.oscillation import record_approval
from apps.events.emit import emit_event
from apps.outcomes.models import OutcomeEntry
from apps.outcomes.service import OutcomeService
from apps.policy.gate import ActionContext as PolicyActionContext
from apps.policy.gate import D9Gate
from apps.tasks.models import Task
from apps.users.models import User


class DraftService:
    """State-machine service for draft human-in-the-loop review."""

    @classmethod
    def generate(cls, task: Task) -> Draft:
        """Create a pending draft from a running task."""
        return DraftGenerator.generate(task)

    @classmethod
    def approve(cls, draft: Draft, user: User, actor_role: str) -> Draft:
        tenant_id = str(draft.tenant_id)
        set_db_tenant(tenant_id)
        try:
            draft.status = DraftStatus.APPROVED
            draft.approver = user
            draft.save(update_fields=["status", "approver", "updated_at"])
            cls._update_task_review(draft.task, Task.ReviewStatus.ACCEPTED, user)
            record_approval(tenant_id, str(user.id), draft.task.agent_id, edited=False)
            cls._emit_and_audit(draft, "draft.approved", user, actor_role)
            cls._maybe_send(draft, actor_role)
            return draft
        finally:
            clear_db_tenant()

    @classmethod
    def edit_and_approve(
        cls,
        draft: Draft,
        edited: dict[str, Any],
        reason: str,
        classification: str,
        user: User,
        actor_role: str,
    ) -> Draft:
        tenant_id = str(draft.tenant_id)
        set_db_tenant(tenant_id)
        try:
            draft.edited_content = edited
            draft.edit_reason = reason
            draft.edit_classification = classification
            draft.status = DraftStatus.EDITED
            draft.approver = user
            draft.save(
                update_fields=[
                    "edited_content",
                    "edit_reason",
                    "edit_classification",
                    "status",
                    "approver",
                    "updated_at",
                ]
            )
            cls._update_task_review(draft.task, Task.ReviewStatus.EDIT_LIGHT, user)
            record_approval(tenant_id, str(user.id), draft.task.agent_id, edited=True)
            OutcomeService.record(
                tenant_id=tenant_id,
                action=OutcomeEntry.Action.EDITED,
                draft=draft,
                task=draft.task,
                diff={"edit_classification": classification, "edit_reason": reason},
            )
            cls._emit_and_audit(draft, "draft.edited", user, actor_role)
            cls._maybe_send(draft, actor_role)
            return draft
        finally:
            clear_db_tenant()

    @classmethod
    def reject(cls, draft: Draft, reason: str, user: User, actor_role: str) -> Draft:
        tenant_id = str(draft.tenant_id)
        set_db_tenant(tenant_id)
        try:
            draft.status = DraftStatus.REJECTED
            draft.edit_reason = reason
            draft.approver = user
            draft.save(update_fields=["status", "edit_reason", "approver", "updated_at"])
            cls._update_task_review(draft.task, Task.ReviewStatus.REJECTED, user)
            OutcomeService.record(
                tenant_id=tenant_id,
                action=OutcomeEntry.Action.REJECTED,
                draft=draft,
                task=draft.task,
            )
            cls._emit_and_audit(draft, "draft.rejected", user, actor_role)
            return draft
        finally:
            clear_db_tenant()

    @classmethod
    def cancel(cls, draft: Draft, user: User, actor_role: str) -> Draft:
        """Cancel a pending draft (treated as rejected in E1)."""
        return cls.reject(draft, "cancelled_by_user", user, actor_role)

    @classmethod
    def expire(cls, draft: Draft) -> Draft:
        """Mark a draft as expired (e.g. TTL cron)."""
        tenant_id = str(draft.tenant_id)
        set_db_tenant(tenant_id)
        try:
            draft.status = DraftStatus.EXPIRED
            draft.save(update_fields=["status", "updated_at"])
            emit_event(
                tenant_id=tenant_id,
                event_type="draft.expired",
                payload={"draft_id": str(draft.id), "task_id": str(draft.task_id)},
            )
            return draft
        finally:
            clear_db_tenant()

    @classmethod
    def _maybe_send(cls, draft: Draft, actor_role: str) -> None:
        if draft.status not in (DraftStatus.APPROVED, DraftStatus.EDITED):
            return

        tenant_id = str(draft.tenant_id)
        content = draft.edited_content or draft.original_content
        output_text = json.dumps(content)

        action = PolicyActionContext(
            task_type=draft.task.agent_id,
            data_class=draft.evidence_bundle.privacy_classification if draft.evidence_bundle else "N2",
            skill_id=draft.task.agent_id,
            confidence=1.0,
            source=draft.task.payload.get("source_type", "unknown"),
            tenant_id=tenant_id,
            case_id=draft.task.payload.get("case_id"),
            retrieved_chunks=[],
        )

        decision = D9Gate.pre_egress(
            actor_id=str(draft.approver_id) if draft.approver else "system",
            actor_role=actor_role,
            action=action,
            output_text=output_text,
        )
        if not decision.allowed:
            draft.status = DraftStatus.APPROVED_PENDING_SEND
            draft.save(update_fields=["status", "updated_at"])
            OutcomeService.record(
                tenant_id=tenant_id,
                action=OutcomeEntry.Action.APPROVED,
                draft=draft,
                task=draft.task,
                diff={"blocked_reason": decision.blocked_reason},
            )
            emit_event(
                tenant_id=tenant_id,
                event_type="draft.blocked",
                payload={
                    "draft_id": str(draft.id),
                    "reason": decision.blocked_reason,
                },
            )
            return

        if ChannelSender.send(draft):
            draft.status = DraftStatus.SENT
            draft.sent_at = timezone.now()
            draft.save(update_fields=["status", "sent_at", "updated_at"])
            OutcomeService.record(
                tenant_id=tenant_id,
                action=OutcomeEntry.Action.SENT,
                draft=draft,
                task=draft.task,
                diff={"channel": draft.channel, "recipient": draft.recipient},
            )
            emit_event(
                tenant_id=tenant_id,
                event_type="draft.sent",
                payload={
                    "draft_id": str(draft.id),
                    "channel": draft.channel,
                    "recipient": draft.recipient,
                },
            )
        else:
            draft.status = DraftStatus.APPROVED_PENDING_SEND
            draft.save(update_fields=["status", "updated_at"])
            OutcomeService.record(
                tenant_id=tenant_id,
                action=OutcomeEntry.Action.APPROVED,
                draft=draft,
                task=draft.task,
                diff={"channel_failure": True},
            )

    @classmethod
    def _update_task_review(cls, task: Task, review_status: Task.ReviewStatus, user: User) -> None:
        task.review_status = review_status
        task.reviewed_by = user
        task.reviewed_at = timezone.now()
        task.save(update_fields=["review_status", "reviewed_by", "reviewed_at", "updated_at"])

    @classmethod
    def _emit_and_audit(
        cls,
        draft: Draft,
        event_type: str,
        user: User,
        actor_role: str,
    ) -> None:
        tenant_id = str(draft.tenant_id)
        emit_event(
            tenant_id=tenant_id,
            event_type=event_type,
            payload={
                "draft_id": str(draft.id),
                "task_id": str(draft.task_id),
                "approver_id": str(user.id),
                "status": draft.status,
            },
        )
        AuditWriter.write(
            AuditContext(
                tenant_id=tenant_id,
                actor_id=user.id,
                actor_role_at_decision=actor_role,
            ),
            action_id=event_type,
            payload={
                "draft_id": str(draft.id),
                "task_id": str(draft.task_id),
                "status": draft.status,
                "edit_reason": draft.edit_reason,
            },
        )
