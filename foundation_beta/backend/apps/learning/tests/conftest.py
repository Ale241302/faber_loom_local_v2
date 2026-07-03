"""Fixtures for M14 Outcome Ledger tests."""
from __future__ import annotations

from decimal import Decimal

import pytest
from django.utils import timezone

from apps.classifier.models import ClassificationResult, ClassificationResultStatus, ClassifierSkill, FeedItem
from apps.classifier.schemas import ActionContext
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.drafts.models import Draft
from apps.drafts.services import DraftService
from apps.tasks.models import Task
from apps.tenants.models import Tenant
from apps.users.models import Membership, MembershipStatus, User


@pytest.fixture(autouse=True)
def _patch_audit_and_emit(monkeypatch):
    """Disable audit/event DB writes during unit tests."""
    monkeypatch.setattr("apps.audit.writer.AuditWriter.write", lambda *a, **k: None)
    monkeypatch.setattr("apps.events.outbox.EventWriter.emit", lambda *a, **k: None)


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(
        slug="learning-tenant",
        legal_name="Learning Tenant Legal",
        commercial_name="Learning Tenant",
        vertical_spec_object_id="vertical-001",
        plan_tier="starter",
        status=Tenant.Status.ACTIVE,
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="operator@example.com",
        password="FaberLoom1234!",
        display_name="Operator User",
        is_active=True,
    )


@pytest.fixture
def curator(db):
    return User.objects.create_user(
        email="curator@example.com",
        password="FaberLoom1234!",
        display_name="Curator User",
        is_active=True,
    )


@pytest.fixture
def second_approver(db):
    return User.objects.create_user(
        email="supervisor@example.com",
        password="FaberLoom1234!",
        display_name="Supervisor User",
        is_active=True,
    )


@pytest.fixture
def membership(db, tenant, user):
    return Membership.objects.create(
        user=user,
        tenant=tenant,
        roles=["operator"],
        active_hat="operator",
        status=MembershipStatus.ACTIVE,
    )


@pytest.fixture
def plan_features(db, tenant):
    from apps.tenants.models import TenantPlanFeatures

    return TenantPlanFeatures.objects.create(
        tenant=tenant,
        data_class_ceiling="N4",
    )


@pytest.fixture
def classifier_skill(db, tenant):
    skill, _ = ClassifierSkill.objects.update_or_create(
        tenant=tenant,
        name="rfq_skill",
        defaults={
            "origin": "system",
            "prompt_template": "Classify: {payload}",
            "output_schema": {"required": ["task_type"]},
            "threshold": Decimal("0.85"),
            "model_id": "mock",
            "status": ClassifierSkill.Status.ACTIVE,
        },
    )
    return skill


def _make_classification_result(tenant, skill, confidence: float, data_class: str = "N1"):
    feed_item = FeedItem.objects.create(
        tenant=tenant,
        source_type="email",
        raw_payload={"subject": "RFQ"},
        normalized_payload={"subject": "RFQ"},
        data_class=data_class,
    )
    ctx = ActionContext(
        tenant_id=str(tenant.id),
        task_type="rfq",
        data_class=data_class,
        skill_id="@cotizador",
        agent_id="@cotizador",
        confidence=confidence,
        source="email",
        routing="zone_4",
        payload_normalizado={"subject": "RFQ"},
    )
    return ClassificationResult.objects.create(
        tenant=tenant,
        feed_item=feed_item,
        classifier_skill=skill,
        action_context=ctx.to_dict(),
        confidence=Decimal(str(confidence)).quantize(Decimal("0.001")),
        routing_zone="zone_4",
        status=ClassificationResultStatus.CLASSIFIED,
        model_id="mock",
    )


@pytest.fixture
def task(db, tenant, plan_features, classifier_skill):
    set_db_tenant(tenant.id)
    try:
        classification_result = _make_classification_result(tenant, classifier_skill, 0.90)
        return Task.objects.create(
            tenant=tenant,
            agent_id="@cotizador",
            invocation_mode=Task.InvocationMode.INBOUND,
            invoked_by="system",
            priority=Task.Priority.NORMAL,
            payload={
                "subject": "Cotización",
                "lines": [{"description": "Producto A", "quantity": 10, "unit_price": 5.0}],
                "recipient": "client@example.com",
                "source_type": "email",
            },
            status=Task.Status.RUNNING,
            expected_completion_by=timezone.now() + timezone.timedelta(hours=1),
            classification_result=classification_result,
        )
    finally:
        clear_db_tenant()


@pytest.fixture
def draft(db, tenant, task):
    set_db_tenant(tenant.id)
    try:
        return DraftService.generate(task)
    finally:
        clear_db_tenant()


@pytest.fixture
def n2_task(db, tenant, plan_features, classifier_skill):
    set_db_tenant(tenant.id)
    try:
        classification_result = _make_classification_result(tenant, classifier_skill, 0.90, data_class="N2")
        return Task.objects.create(
            tenant=tenant,
            agent_id="@cotizador",
            invocation_mode=Task.InvocationMode.INBOUND,
            invoked_by="system",
            priority=Task.Priority.NORMAL,
            payload={"subject": "Cotización N2"},
            status=Task.Status.RUNNING,
            expected_completion_by=timezone.now() + timezone.timedelta(hours=1),
            classification_result=classification_result,
        )
    finally:
        clear_db_tenant()
