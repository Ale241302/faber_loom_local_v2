"""Fixtures for M13 Draft HITL tests."""
from __future__ import annotations

import pytest
from django.utils import timezone

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.drafts.models import Channel, Draft
from apps.drafts.services import DraftService
from apps.tasks.models import Task
from apps.tenants.models import Tenant
from apps.users.models import Membership, MembershipStatus, User


@pytest.fixture(autouse=True)
def _patch_audit(monkeypatch):
    """Disable audit/event DB writes during unit tests."""
    monkeypatch.setattr("apps.audit.writer.AuditWriter.write", lambda *a, **k: None)


@pytest.fixture
def captured_events(monkeypatch):
    """Capture emitted event types."""
    events: list[str] = []
    original = __import__("apps.events.outbox", fromlist=["EventWriter"]).EventWriter.emit

    def fake_emit(tenant_id, event_type, payload, event_id=None):
        events.append(event_type)
        return None

    monkeypatch.setattr("apps.events.outbox.EventWriter.emit", fake_emit)
    return events


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(
        slug="draft-tenant",
        legal_name="Draft Tenant Legal",
        commercial_name="Draft Tenant",
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
def task(db, tenant, plan_features):
    set_db_tenant(tenant.id)
    try:
        return Task.objects.create(
            tenant=tenant,
            agent_id="@cotizador",
            invocation_mode=Task.InvocationMode.INBOUND,
            invoked_by="system",
            priority=Task.Priority.NORMAL,
            payload={
                "subject": "Cotización",
                "lines": [
                    {"description": "Producto A", "quantity": 10, "unit_price": 5.0},
                    {"description": "Producto B", "quantity": 2, "unit_price": 20.0},
                ],
                "recipient": "client@example.com",
                "source_type": "email",
            },
            status=Task.Status.RUNNING,
            expected_completion_by=timezone.now() + timezone.timedelta(hours=1),
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
