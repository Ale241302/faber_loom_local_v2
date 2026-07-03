"""Pytest fixtures and global patches for M10 classifier tests."""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any

import pytest

from apps.classifier.models import ClassifierSkill, ClassifierSkillStatus
from apps.policy.models import DpaStatement, DpaStatus
from apps.rbac.models import PermissionLevel, Role
from apps.tenants.models import Tenant, TenantPlanFeatures
from apps.users.models import Membership, MembershipStatus, User


@pytest.fixture(autouse=True)
def _patch_emit_and_audit(monkeypatch):
    """Disable outbox/audit DB sequences so tests run without M12/M15 migrations."""

    def _noop_emit(*args, **kwargs):
        return "evt_noop"

    def _noop_audit(*args, **kwargs):
        return None

    monkeypatch.setattr("apps.events.outbox.EventWriter.emit", _noop_emit)
    monkeypatch.setattr("apps.audit.writer.AuditWriter.write", _noop_audit)


@pytest.fixture
def tenant(db):
    return Tenant.objects.create(
        slug=f"tenant-{uuid.uuid4().hex[:8]}",
        legal_name="Test Tenant",
        vertical_spec_object_id="vertical:test",
        plan_tier="starter",
    )


@pytest.fixture
def user(db):
    return User.objects.create_user(email="test@example.com", password="password123")


@pytest.fixture
def role_admin(db):
    return Role.objects.create(
        id="admin",
        name="Admin",
        permissions={
            "workloom": PermissionLevel.FULL,
            "config": PermissionLevel.FULL,
        },
    )


@pytest.fixture
def membership(db, tenant, user, role_admin):
    membership = Membership.objects.create(
        user=user,
        tenant=tenant,
        roles=[role_admin.id],
        active_hat=role_admin.id,
        status=MembershipStatus.ACTIVE,
    )
    membership._role_cache = role_admin
    return membership


@pytest.fixture
def plan_features(db, tenant):
    return TenantPlanFeatures.objects.create(
        tenant=tenant,
        data_class_ceiling="N4",
    )


@pytest.fixture
def dpa_signed(db, tenant, user):
    return DpaStatement.objects.create(
        tenant=tenant,
        status=DpaStatus.SIGNED,
        signed_by=user,
    )


@pytest.fixture
def classifier_skill(db, tenant):
    return ClassifierSkill.objects.create(
        tenant=tenant,
        name="default-skill",
        origin="system",
        prompt_template=(
            "Classify the payload:\n{payload}\nfeatures: {features}\n"
            "Return JSON with task_type, data_class, skill_id, agent_id, "
            "confidence, source, routing, sla_minutes, payload_normalizado, requires_human_gate."
        ),
        output_schema={
            "required": [
                "task_type",
                "skill_id",
                "agent_id",
                "confidence",
                "routing",
            ],
        },
        threshold=Decimal("0.85"),
        model_id="tier0",
        status=ClassifierSkillStatus.ACTIVE,
    )
