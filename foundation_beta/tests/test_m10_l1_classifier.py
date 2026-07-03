"""M10 L1 Classifier integration tests."""
from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.audit.models import AuditLog
from apps.classifier.engine import ActionEngine
from apps.classifier.models import (
    ClassificationResult,
    ClassificationResultStatus,
    ClassifierSkill,
    ClassifierSkillStatus,
    FeedItem,
    FeedItemStatus,
    Tier0Rule,
)
from apps.classifier.schemas import ActionContext
from apps.classifier.services import ClassifierService
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.events.models import Outbox
from apps.policy.models import DpaStatement
from apps.tenants.models import TenantPlanFeatures
from apps.tasks.models import Task


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    import fakeredis
    from apps.core import redis_client
    from apps.auth_session import session as session_module
    from apps.auth_session import middleware as middleware_module

    fake = fakeredis.FakeStrictRedis()
    monkeypatch.setattr(redis_client, "get_redis_client", lambda: fake)
    monkeypatch.setattr(session_module, "get_redis_client", lambda: fake)
    monkeypatch.setattr(middleware_module, "get_redis_client", lambda: fake)


def _plan_features(tenant, ceiling: str = "N4") -> TenantPlanFeatures:
    return TenantPlanFeatures.objects.update_or_create(
        tenant=tenant,
        defaults={"data_class_ceiling": ceiling},
    )[0]


@pytest.fixture
def classifier_skill(db, tenant_a):
    set_db_tenant(tenant_a.id)
    try:
        skill, _ = ClassifierSkill.objects.update_or_create(
            tenant=tenant_a,
            name="classify_rfq",
            defaults={
                "origin": "system",
                "prompt_template": "Classify the payload: {payload}",
                "output_schema": {"required": ["task_type", "data_class", "skill_id", "confidence"]},
                "threshold": Decimal("0.85"),
                "model_id": "anthropic/claude-3-5-haiku-20241022",
                "status": ClassifierSkillStatus.ACTIVE,
            },
        )
    finally:
        clear_db_tenant()
    return skill


@pytest.fixture
def rfq_feed_item(tenant_a):
    set_db_tenant(tenant_a.id)
    try:
        return FeedItem.objects.create(
            tenant=tenant_a,
            source_type="email",
            raw_payload={"subject": "RFQ", "body": "Please quote 100 units"},
            normalized_payload={"subject": "RFQ", "body": "Please quote 100 units"},
            data_class="N1",
        )
    finally:
        clear_db_tenant()


def _make_classification_result(feed_item, skill, confidence: float, data_class: str = "N2"):
    if feed_item._state.adding:
        feed_item.source_type = feed_item.source_type or "email"
        feed_item.normalized_payload = feed_item.normalized_payload or {}
        feed_item.raw_payload = feed_item.raw_payload or {}
        feed_item.data_class = feed_item.data_class or "N1"
        feed_item.save(force_insert=True)
    ctx = ActionContext(
        tenant_id=str(feed_item.tenant_id),
        task_type="rfq",
        data_class=data_class,
        skill_id="@cotizador",
        agent_id="@cotizador",
        confidence=confidence,
        source="email_body",
        routing="zone_4",
        payload_normalizado={"subject": "RFQ"},
    )
    return ClassificationResult.objects.create(
        tenant=feed_item.tenant,
        feed_item=feed_item,
        classifier_skill=skill,
        action_context=ctx.to_dict(),
        confidence=Decimal(str(confidence)).quantize(Decimal("0.001")),
        routing_zone="zone_4",
        status=ClassificationResultStatus.CLASSIFIED,
        model_id=skill.model_id,
    )


@pytest.mark.django_db
def test_tier0_exact_match_creates_task(tenant_a, owner_user, classifier_skill, rfq_feed_item):
    _plan_features(tenant_a, "N4")
    set_db_tenant(tenant_a.id)
    try:
        Tier0Rule.objects.create(
            tenant=tenant_a,
            name="rfq_keyword",
            pattern={"keywords": ["rfq", "quote"]},
            priority=10,
            action_context={
                "task_type": "rfq",
                "data_class": "N1",
                "skill_id": "@cotizador",
                "agent_id": "@cotizador",
                "source": "email_body",
                "routing": "zone_4",
                "payload_normalizado": {"intent": "rfq"},
            },
        )
        result = ActionEngine.process(rfq_feed_item, str(owner_user.id), "owner")
    finally:
        clear_db_tenant()

    assert result["status"] == FeedItemStatus.ROUTED_TO_TASK
    assert Task.objects.filter(tenant_id=tenant_a.id).count() == 1
    assert Outbox.objects.filter(event_type="task.created").exists()


@pytest.mark.django_db
def test_l1_low_confidence_goes_to_human_review(tenant_a, owner_user, classifier_skill, rfq_feed_item):
    _plan_features(tenant_a, "N4")
    low_confidence_result = _make_classification_result(rfq_feed_item, classifier_skill, 0.4)

    with patch("apps.classifier.engine.L1Classifier.classify", return_value=low_confidence_result):
        set_db_tenant(tenant_a.id)
        try:
            result = ActionEngine.process(rfq_feed_item, str(owner_user.id), "owner")
        finally:
            clear_db_tenant()

    assert result["status"] == FeedItemStatus.PENDING_HUMAN_REVIEW
    assert Task.objects.filter(tenant_id=tenant_a.id).count() == 0
    assert Outbox.objects.filter(event_type="feed.item.dispatched").exists()


@pytest.mark.django_db
def test_l1_high_confidence_creates_task(tenant_a, owner_user, classifier_skill, rfq_feed_item):
    _plan_features(tenant_a, "N4")
    DpaStatement.objects.create(tenant=tenant_a, status=DpaStatement.Status.SIGNED, version="v1")
    high_confidence_result = _make_classification_result(rfq_feed_item, classifier_skill, 0.92)

    with patch("apps.classifier.engine.L1Classifier.classify", return_value=high_confidence_result):
        set_db_tenant(tenant_a.id)
        try:
            result = ActionEngine.process(rfq_feed_item, str(owner_user.id), "owner")
        finally:
            clear_db_tenant()

    assert result["status"] == FeedItemStatus.ROUTED_TO_TASK
    assert Task.objects.filter(tenant_id=tenant_a.id).count() == 1
    assert Outbox.objects.filter(event_type="task.created").exists()


@pytest.mark.django_db
def test_n3n4_without_dpa_blocked(tenant_a, owner_user, classifier_skill, rfq_feed_item):
    _plan_features(tenant_a, "N4")
    n3_result = _make_classification_result(rfq_feed_item, classifier_skill, 0.92, data_class="N3")

    with patch("apps.classifier.engine.L1Classifier.classify", return_value=n3_result):
        set_db_tenant(tenant_a.id)
        try:
            result = ActionEngine.process(rfq_feed_item, str(owner_user.id), "owner")
        finally:
            clear_db_tenant()

    assert result["status"] == FeedItemStatus.MANUAL_REVIEW
    assert "blocked_reason" in result
    assert Task.objects.filter(tenant_id=tenant_a.id).count() == 0


@pytest.mark.django_db
def test_l1_llm_error_retries_and_fallbacks(tenant_a, owner_user, classifier_skill, rfq_feed_item):
    _plan_features(tenant_a, "N4")

    with patch("apps.classifier.l1.litellm.completion", side_effect=RuntimeError("LLM down")):
        set_db_tenant(tenant_a.id)
        try:
            result = ActionEngine.process(rfq_feed_item, str(owner_user.id), "owner")
        finally:
            clear_db_tenant()

    assert result["status"] == FeedItemStatus.MANUAL_REVIEW
    assert ClassificationResult.objects.filter(
        tenant_id=tenant_a.id, status=ClassificationResultStatus.FAILED
    ).exists()


@pytest.mark.django_db
def test_cross_tenant_classifier_skill_isolation(tenant_a, tenant_b, classifier_skill):
    set_db_tenant(tenant_b.id)
    try:
        with pytest.raises(ClassifierSkill.DoesNotExist):
            ClassifierSkill.objects.get_active(tenant_b.id)
    finally:
        clear_db_tenant()


@pytest.mark.django_db
def test_manual_classify_endpoint_creates_feed_item(
    client, tenant_a, owner_user, owner_membership, classifier_skill
):
    _plan_features(tenant_a, "N4")
    DpaStatement.objects.create(tenant=tenant_a, status=DpaStatement.Status.SIGNED, version="v1")
    high_confidence_result = _make_classification_result(
        FeedItem(tenant=tenant_a), classifier_skill, 0.92
    )

    # Login via M08 to get session cookie.
    from django.urls import reverse
    from apps.auth_session import session as session_store

    session_id = session_store.create_session(
        user_id=owner_user.id,
        tenant_id=tenant_a.id,
        roles=owner_membership.roles,
        active_hat=owner_membership.active_hat,
    )
    client.cookies["session_id"] = session_id

    with patch("apps.classifier.engine.L1Classifier.classify", return_value=high_confidence_result):
        response = client.post(
            reverse("classifier-classify"),
            {
                "source_type": "email",
                "raw_payload": {"subject": "Quote request"},
                "data_class": "N1",
            },
            content_type="application/json",
            HTTP_X_TENANT_ID=str(tenant_a.id),
        )

    assert response.status_code == 201, response.json()
    assert response.json()["status"] == FeedItemStatus.ROUTED_TO_TASK
