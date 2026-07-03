"""Classifier services for manual operations and re-classification."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from apps.audit.writer import AuditContext, AuditWriter
from apps.classifier.engine import ActionEngine
from apps.classifier.models import (
    ClassificationResult,
    ClassificationResultStatus,
    ClassifierSkill,
    FeedItem,
    FeedItemStatus,
    Tier0Rule,
)
from apps.classifier.schemas import ActionContext
from apps.events.emit import emit_event


class ClassifierService:
    """High-level operations exposed by the classifier API."""

    @classmethod
    def create_feed_item(
        cls,
        tenant_id: str,
        source_type: str,
        raw_payload: dict[str, Any],
        normalized_payload: dict[str, Any] | None = None,
        external_id: str = "",
        data_class: str = "N1",
    ) -> FeedItem:
        return FeedItem.objects.create(
            tenant_id=tenant_id,
            source_type=source_type,
            external_id=external_id,
            raw_payload=raw_payload,
            normalized_payload=normalized_payload or raw_payload,
            data_class=data_class,
            status=FeedItemStatus.RECEIVED,
        )

    @classmethod
    def manual_classify(
        cls,
        feed_item: FeedItem,
        actor_id: str,
        actor_role: str,
    ) -> dict[str, Any]:
        feed_item.status = FeedItemStatus.CLASSIFYING
        feed_item.save(update_fields=["status", "updated_at"])
        return ActionEngine.process(feed_item, actor_id, actor_role)

    @classmethod
    def confirm_pending(
        cls,
        feed_item: FeedItem,
        actor_id: str,
        actor_role: str,
    ) -> dict[str, Any]:
        """Operator confirms a pending_human_review item and creates its task."""
        if feed_item.status != FeedItemStatus.PENDING_HUMAN_REVIEW:
            raise ValueError("feed item is not pending human review")

        classification_result = feed_item.classification_results.latest("created_at")
        ctx = ActionContext.from_dict(classification_result.action_context)

        with transaction.atomic():
            from apps.tasks.models import Task

            task = Task.objects.create(
                tenant=feed_item.tenant,
                agent_id=ctx.agent_id or ctx.skill_id,
                invocation_mode=Task.InvocationMode.INBOUND,
                invoked_by=actor_id,
                priority=Task.Priority.NORMAL,
                payload=ctx.payload_normalizado,
                status=Task.Status.QUEUED,
                classification_result=classification_result,
            )
            feed_item.status = FeedItemStatus.ROUTED_TO_TASK
            classification_result.status = ClassificationResultStatus.ROUTED_TO_TASK
            feed_item.save(update_fields=["status", "updated_at"])
            classification_result.save(update_fields=["status"])

            emit_event(
                tenant_id=str(feed_item.tenant_id),
                event_type="task.created",
                payload={
                    "task_id": str(task.id),
                    "feed_item_id": str(feed_item.id),
                    "agent_id": task.agent_id,
                },
            )
            emit_event(
                tenant_id=str(feed_item.tenant_id),
                event_type="pattern.candidate.detected",
                payload={
                    "feed_item_id": str(feed_item.id),
                    "classification_result_id": str(classification_result.id),
                    "reason": "operator_confirmed",
                },
            )

            AuditWriter.write(
                AuditContext(
                    tenant_id=str(feed_item.tenant_id),
                    actor_id=actor_id,
                    actor_role_at_decision=actor_role,
                ),
                action_id="feed.item.confirmed",
                data_class=ctx.data_class,
                task_type=ctx.task_type,
                payload={
                    "feed_item_id": str(feed_item.id),
                    "task_id": str(task.id),
                    "classification_result_id": str(classification_result.id),
                },
            )

        return {
            "feed_item_id": str(feed_item.id),
            "task_id": str(task.id),
            "status": feed_item.status,
        }

    @classmethod
    def reclassify(
        cls,
        feed_item: FeedItem,
        action_context: dict[str, Any],
        actor_id: str,
        actor_role: str,
        reason: str = "operator_correction",
    ) -> dict[str, Any]:
        """Operator overrides the classification."""
        with transaction.atomic():
            skill = ClassifierSkill.objects.get_active(feed_item.tenant_id)
            classification_result = ClassificationResult.objects.create(
                tenant=feed_item.tenant,
                feed_item=feed_item,
                classifier_skill=skill,
                action_context=action_context,
                confidence=Decimal("1.000"),
                routing_zone=action_context.get("routing", "zone_4"),
                status=ClassificationResultStatus.CLASSIFIED,
                model_id="operator",
                model_version="1",
            )

            emit_event(
                tenant_id=str(feed_item.tenant_id),
                event_type="pattern.candidate.detected",
                payload={
                    "feed_item_id": str(feed_item.id),
                    "classification_result_id": str(classification_result.id),
                    "reason": reason,
                },
            )

            return ActionEngine.process(feed_item, actor_id, actor_role)

    @classmethod
    def clone_skill(
        cls,
        skill: ClassifierSkill,
        new_name: str,
        actor_id: str,
        actor_role: str,
    ) -> ClassifierSkill:
        with transaction.atomic():
            cloned = ClassifierSkill.objects.create(
                tenant=skill.tenant,
                name=new_name,
                origin="tenant",
                prompt_template=skill.prompt_template,
                output_schema=skill.output_schema,
                threshold=skill.threshold,
                model_id=skill.model_id,
                timeout_ms=skill.timeout_ms,
                cost_cap_usd=skill.cost_cap_usd,
                status=ClassifierSkill.Status.SHADOW,
                active_version="1",
            )
            AuditWriter.write(
                AuditContext(
                    tenant_id=str(skill.tenant_id),
                    actor_id=actor_id,
                    actor_role_at_decision=actor_role,
                ),
                action_id="classifier.skill.cloned",
                payload={
                    "source_skill_id": str(skill.id),
                    "cloned_skill_id": str(cloned.id),
                    "name": new_name,
                },
            )
            return cloned
