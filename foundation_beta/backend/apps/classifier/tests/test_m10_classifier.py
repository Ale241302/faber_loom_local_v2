"""M10 L1 Classifier unit tests (Tier0 + ActionEngine + service helpers)."""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

import pytest

from apps.classifier.engine import ActionEngine
from apps.classifier.models import (
    ClassificationResult,
    ClassificationResultStatus,
    FeedItem,
    FeedItemStatus,
    Tier0Rule,
)
from apps.classifier.l1 import L1Classifier
from apps.classifier.schemas import ActionContext
from apps.classifier.services import ClassifierService
from apps.classifier.tier0 import Tier0Classifier
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.tasks.models import Task


pytestmark = pytest.mark.django_db


class TestTier0Classifier:
    def test_keyword_rule_matches(self, tenant, classifier_skill):
        Tier0Rule.objects.create(
            tenant=tenant,
            name="urgent-rule",
            pattern={"keywords": ["urgente"]},
            action_context={
                "task_type": "escalation",
                "data_class": "N2",
                "skill_id": "urgent-skill",
                "agent_id": "agent-urgent",
                "routing": "zone_1",
                "sla_minutes": 15,
                "payload_normalizado": {"priority": "high"},
            },
            priority=10,
        )
        item = FeedItem.objects.create(
            tenant=tenant,
            source_type="email",
            normalized_payload={"subject": "Requerimiento urgente"},
        )
        ctx = Tier0Classifier.match(item, str(tenant.id))
        assert ctx is not None
        assert ctx.task_type == "escalation"
        assert ctx.routing == "zone_1"

    def test_no_rule_returns_none(self, tenant):
        item = FeedItem.objects.create(
            tenant=tenant,
            source_type="email",
            normalized_payload={"subject": "Regular update"},
        )
        assert Tier0Classifier.match(item, str(tenant.id)) is None


class TestActionEngine:
    def test_tier0_rule_creates_task(self, tenant, classifier_skill, plan_features, dpa_signed):
        Tier0Rule.objects.create(
            tenant=tenant,
            name="auto-rule",
            pattern={"exact": {"type": "invoice"}},
            action_context={
                "task_type": "process_invoice",
                "data_class": "N1",
                "skill_id": "invoice-skill",
                "agent_id": "agent-invoice",
                "routing": "zone_3",
                "sla_minutes": 120,
                "payload_normalizado": {"type": "invoice"},
            },
            priority=5,
        )
        item = FeedItem.objects.create(
            tenant=tenant,
            source_type="webhook",
            normalized_payload={"type": "invoice", "amount": 1000},
        )

        set_db_tenant(tenant.id)
        try:
            result = ActionEngine.process(
                feed_item=item,
                actor_id="user-1",
                actor_role="admin",
            )

            item.refresh_from_db()
            assert item.status == FeedItemStatus.ROUTED_TO_TASK
            assert "task_id" in result
            task = Task.objects.get(id=result["task_id"])
            assert task.agent_id == "agent-invoice"
            assert task.priority == Task.Priority.NORMAL
        finally:
            clear_db_tenant()

    def test_d9_blocks_n3_without_dpa(self, tenant, classifier_skill):
        """If tier0 yields N3 and DPA is missing, the item is sent to manual review."""
        Tier0Rule.objects.create(
            tenant=tenant,
            name="pii-rule",
            pattern={"keywords": ["pasaporte"]},
            action_context={
                "task_type": "review_pii",
                "data_class": "N3",
                "skill_id": "pii-skill",
                "agent_id": "agent-pii",
                "routing": "zone_2",
                "sla_minutes": 30,
            },
            priority=10,
        )
        item = FeedItem.objects.create(
            tenant=tenant,
            source_type="email",
            normalized_payload={"body": "Mi pasaporte venció"},
        )

        result = ActionEngine.process(
            feed_item=item,
            actor_id="user-1",
            actor_role="admin",
        )

        item.refresh_from_db()
        assert item.status == FeedItemStatus.MANUAL_REVIEW
        assert "blocked_reason" in result

    def test_low_confidence_goes_to_pending_review(self, tenant, classifier_skill, plan_features, dpa_signed):
        item = FeedItem.objects.create(
            tenant=tenant,
            source_type="email",
            normalized_payload={"subject": "Hello"},
        )
        low_confidence_ctx = ActionContext(
            tenant_id=str(tenant.id),
            task_type="greet",
            data_class="N1",
            skill_id="greet-skill",
            agent_id="agent-greet",
            confidence=0.5,
            source="email",
            routing="zone_4",
            sla_minutes=60,
            payload_normalizado={"subject": "Hello"},
        )

        with patch("apps.classifier.engine.L1Classifier.classify", return_value=_make_result(item, classifier_skill, low_confidence_ctx)):
            result = ActionEngine.process(
                feed_item=item,
                actor_id="user-1",
                actor_role="admin",
            )

        item.refresh_from_db()
        assert item.status == FeedItemStatus.PENDING_HUMAN_REVIEW
        assert "classification_result_id" in result



def _make_result(item, skill, ctx: ActionContext) -> ClassificationResult:
    return ClassificationResult.objects.create(
        tenant=item.tenant,
        feed_item=item,
        classifier_skill=skill,
        action_context=ctx.to_dict(),
        features={},
        confidence=Decimal(str(ctx.confidence)),
        routing_zone=ctx.routing,
        status=ClassificationResultStatus.CLASSIFIED,
        model_id="mock",
    )


class TestL1Classifier:
    def test_parse_valid_json(self):
        schema = {"required": ["task_type", "confidence"]}
        ctx = L1Classifier._parse_and_validate(
            '{"task_type": "summarize", "confidence": 0.92, "routing": "zone_3"}',
            schema,
        )
        assert ctx.task_type == "summarize"
        assert ctx.confidence == pytest.approx(0.92)

    def test_parse_missing_required_raises(self):
        schema = {"required": ["task_type"]}
        with pytest.raises(ValueError):
            L1Classifier._parse_and_validate('{"confidence": 0.9}', schema)

    def test_extract_json_from_markdown(self):
        schema = {"required": ["task_type"]}
        text = "```json\n{\"task_type\": \"x\"}\n```"
        ctx = L1Classifier._parse_and_validate(text, schema)
        assert ctx.task_type == "x"


class TestClassifierService:
    def test_confirm_pending_creates_task(self, tenant, classifier_skill, plan_features, dpa_signed):
        item = FeedItem.objects.create(
            tenant=tenant,
            source_type="manual",
            normalized_payload={"type": "request"},
            status=FeedItemStatus.PENDING_HUMAN_REVIEW,
        )
        ClassificationResult.objects.create(
            tenant=tenant,
            feed_item=item,
            classifier_skill=classifier_skill,
            action_context={
                "tenant_id": str(tenant.id),
                "task_type": "process",
                "data_class": "N1",
                "skill_id": "s1",
                "agent_id": "a1",
                "confidence": 0.9,
                "source": "manual",
                "routing": "zone_3",
                "sla_minutes": 60,
                "payload_normalizado": {"type": "request"},
            },
            confidence=Decimal("0.9"),
            routing_zone="zone_3",
            status=ClassificationResultStatus.PENDING_HUMAN_REVIEW,
        )

        set_db_tenant(tenant.id)
        try:
            result = ClassifierService.confirm_pending(
                feed_item=item,
                actor_id="user-1",
                actor_role="admin",
            )

            item.refresh_from_db()
            assert item.status == FeedItemStatus.ROUTED_TO_TASK
            assert Task.objects.filter(id=result["task_id"]).exists()
        finally:
            clear_db_tenant()

    def test_reclassify_overrides_and_runs_engine(self, tenant, classifier_skill, plan_features, dpa_signed):
        item = FeedItem.objects.create(
            tenant=tenant,
            source_type="manual",
            normalized_payload={"type": "invoice"},
            status=FeedItemStatus.PENDING_HUMAN_REVIEW,
        )
        ClassificationResult.objects.create(
            tenant=tenant,
            feed_item=item,
            classifier_skill=classifier_skill,
            action_context={},
            confidence=Decimal("0.6"),
            routing_zone="zone_4",
            status=ClassificationResultStatus.CLASSIFIED,
        )

        l1_ctx = ActionContext(
            tenant_id=str(tenant.id),
            task_type="manual_review",
            data_class="N1",
            skill_id="manual",
            agent_id="agent-manual",
            confidence=1.0,
            source="manual",
            routing="zone_3",
            sla_minutes=60,
            payload_normalizado={"type": "invoice"},
        )

        with patch("apps.classifier.engine.L1Classifier.classify", return_value=_make_result(item, classifier_skill, l1_ctx)):
            result = ClassifierService.reclassify(
                feed_item=item,
                action_context={
                    "tenant_id": str(tenant.id),
                    "task_type": "manual_review",
                    "data_class": "N1",
                    "skill_id": "manual",
                    "agent_id": "agent-manual",
                    "confidence": 1.0,
                    "source": "manual",
                    "routing": "zone_3",
                    "sla_minutes": 60,
                    "payload_normalizado": {"type": "invoice"},
                },
                actor_id="user-1",
                actor_role="admin",
            )

        assert result["status"] == FeedItemStatus.ROUTED_TO_TASK
