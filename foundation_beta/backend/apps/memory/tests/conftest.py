"""Fixtures for M17 Memory Letta tests."""
from __future__ import annotations

import pytest

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.memory.letta_client import LettaMemoryClient, _InMemoryStore
from apps.tenants.models import Tenant
from apps.users.models import Membership, MembershipStatus, User


@pytest.fixture(autouse=True)
def _patch_audit_and_emit(monkeypatch):
    monkeypatch.setattr("apps.audit.writer.AuditWriter.write", lambda *a, **k: None)
    monkeypatch.setattr("apps.events.outbox.EventWriter.emit", lambda *a, **k: None)


@pytest.fixture
def letta_client():
    client = LettaMemoryClient(backend="memory")
    _InMemoryStore.clear()
    return client


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(
        slug="memory-tenant",
        legal_name="Memory Tenant Legal",
        commercial_name="Memory Tenant",
        vertical_spec_object_id="vertical-001",
        plan_tier="starter",
        status=Tenant.Status.ACTIVE,
    )


@pytest.fixture
def other_tenant(db):
    return Tenant.objects.create(
        slug="other-tenant",
        legal_name="Other Tenant Legal",
        commercial_name="Other Tenant",
        vertical_spec_object_id="vertical-002",
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
