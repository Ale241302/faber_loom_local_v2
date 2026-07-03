"""Action Engine: orchestrates Tier 0 / L1 classification, D9 gate and task creation."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.audit.writer import AuditContext, AuditWriter
from apps.classifier.l1 import L1Classifier
from apps.classifier.models import (
    ClassificationResult,
    ClassificationResultStatus,
    ClassifierSkill,
    FeedItemStatus,
)
from apps.classifier.schemas import ActionContext
from apps.classifier.tier0 import Tier0Classifier
from apps.events.emit import emit_event
from apps.policy.gate import D9Gate
from apps.tasks.models import Task


class ActionEngine:
    """Process a feed_item and produce a routing decision."""

    @classmethod
    def process(cls, feed_item, actor_id: str, actor_role: str) -> dict[str, Any]:
        with transaction.atomic():
            tenant_id = str(feed_item.tenant_id)
            skill = ClassifierSkill.objects.get_active(tenant_id)

            classification_result = cls._classify(feed_item, skill)

            if classification_result.status == ClassificationResultStatus.FAILED:
                feed_item.status = FeedItemStatus.MANUAL_REVIEW
                feed_item.save(update_fields=["status", "updated_at"])
                return {
                    "feed_item_id": str(feed_item.id),
                    "status": feed_item.status,
                    "blocked_reason": "classification_failed",
                }

            ctx = ActionContext.from_dict(classification_result.action_context)

            decision = D9Gate.evaluate(
                actor_id=actor_id,
                actor_role=actor_role,
                action=ctx.to_policy_action(),
            )

            if not decision.allowed:
                feed_item.status = FeedItemStatus.MANUAL_REVIEW
                feed_item.save(update_fields=["status", "updated_at"])
                return {
                    "feed_item_id": str(feed_item.id),
                    "status": feed_item.status,
                    "blocked_reason": decision.blocked_reason,
                    "effective_classification": decision.effective_classification,
                }

            if ctx.confidence < float(skill.threshold) or decision.requires_human_gate:
                feed_item.status = FeedItemStatus.PENDING_HUMAN_REVIEW
                classification_result.status = ClassificationResultStatus.PENDING_HUMAN_REVIEW
                feed_item.save(update_fields=["status", "updated_at"])
                classification_result.save(update_fields=["status"])
                emit_event(
                    tenant_id=tenant_id,
                    event_type="feed.item.dispatched",
                    payload={
                        "feed_item_id": str(feed_item.id),
                        "classification_result_id": str(classification_result.id),
                        "routing_zone": ctx.routing,
                        "confidence": str(ctx.confidence),
                    },
                )
                return {
                    "feed_item_id": str(feed_item.id),
                    "status": feed_item.status,
                    "classification_result_id": str(classification_result.id),
                }

            task = Task.objects.create(
                tenant=feed_item.tenant,
                agent_id=ctx.agent_id or ctx.skill_id,
                invocation_mode=Task.InvocationMode.INBOUND,
                invoked_by="system",
                priority=cls._priority_from_routing(ctx.routing),
                payload=ctx.payload_normalizado,
                status=Task.Status.QUEUED,
                expected_completion_by=timezone.now() + timezone.timedelta(minutes=ctx.sla_minutes),
                classification_result=classification_result,
            )

            feed_item.status = FeedItemStatus.ROUTED_TO_TASK
            classification_result.status = ClassificationResultStatus.ROUTED_TO_TASK
            feed_item.save(update_fields=["status", "updated_at"])
            classification_result.save(update_fields=["status"])

            emit_event(
                tenant_id=tenant_id,
                event_type="task.created",
                payload={
                    "task_id": str(task.id),
                    "feed_item_id": str(feed_item.id),
                    "agent_id": task.agent_id,
                    "routing_zone": ctx.routing,
                },
            )

            AuditWriter.write(
                AuditContext(
                    tenant_id=tenant_id,
                    actor_id=actor_id,
                    actor_role_at_decision=actor_role,
                ),
                action_id="feed.item.dispatched",
                data_class=ctx.data_class,
                task_type=ctx.task_type,
                model_id=classification_result.model_id,
                model_version=classification_result.model_version,
                payload={
                    "feed_item_id": str(feed_item.id),
                    "classification_result_id": str(classification_result.id),
                    "task_id": str(task.id),
                    "confidence": str(ctx.confidence),
                },
            )

            return {
                "feed_item_id": str(feed_item.id),
                "task_id": str(task.id),
                "status": feed_item.status,
                "classification_result_id": str(classification_result.id),
            }

    @classmethod
    def _classify(cls, feed_item, skill: ClassifierSkill) -> ClassificationResult:
        tenant_id = str(feed_item.tenant_id)
        ctx = Tier0Classifier.match(feed_item, tenant_id)
        if ctx:
            return ClassificationResult.objects.create(
                tenant=feed_item.tenant,
                feed_item=feed_item,
                classifier_skill=skill,
                action_context=ctx.to_dict(),
                features={},
                confidence=Decimal("1.000"),
                routing_zone=ctx.routing,
                status=ClassificationResultStatus.CLASSIFIED,
                model_id="tier0",
                model_version="1",
            )
        return L1Classifier.classify(feed_item, skill)

    @classmethod
    def _priority_from_routing(cls, routing: str) -> str:
        mapping = {
            "zone_1": Task.Priority.URGENT,
            "zone_2": Task.Priority.HIGH,
            "zone_3": Task.Priority.NORMAL,
            "zone_4": Task.Priority.NORMAL,
        }
        return mapping.get(routing, Task.Priority.NORMAL)
