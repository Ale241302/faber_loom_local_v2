"""M11 D9 Policy Gate integration tests."""
from __future__ import annotations

import pytest
from django.test import Client
from django.urls import reverse

from apps.auth_session import session as session_store
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.events.models import Outbox
from apps.policy.gate import ActionContext, D9Gate, RetrievedChunk
from apps.policy.models import DpaStatement, PolicyBlock
from apps.tenants.models import TenantPlanFeatures
from apps.users.models import Membership, MembershipStatus, User


def _login(client: Client, user, tenant, password: str = "FaberLoom1234!") -> str:
    resp = client.post(
        reverse("auth-login"),
        {"email": user.email, "password": password, "tenant_id": str(tenant.id)},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    if data.get("requires_2fa"):
        from apps.auth_session import totp as totp_helpers
        import pyotp

        secret = totp_helpers.decrypt_secret(user.totp_secret_encrypted)
        resp2 = client.post(
            reverse("auth-2fa"),
            {
                "login_token": data["login_token"],
                "totp": pyotp.TOTP(secret).now(),
                "tenant_id": str(tenant.id),
            },
            content_type="application/json",
        )
        assert resp2.status_code == 200, resp2.json()
        return resp2.json()["session_id"]
    return data["session_id"]


def _plan_features(tenant, ceiling: str = "N4"):
    return TenantPlanFeatures.objects.update_or_create(
        tenant=tenant,
        defaults={"data_class_ceiling": ceiling},
    )[0]


@pytest.mark.django_db
def test_n3_without_dpa_blocks(tenant_a, owner_user):
    _plan_features(tenant_a, "N4")
    set_db_tenant(tenant_a.id)
    try:
        action = ActionContext(
            tenant_id=str(tenant_a.id),
            data_class="N3",
            source="email_body",
        )
        decision = D9Gate.evaluate(
            actor_id=str(owner_user.id), actor_role="owner", action=action
        )
    finally:
        clear_db_tenant()

    assert decision.allowed is False
    assert "DPA" in decision.blocked_reason


@pytest.mark.django_db
def test_n3_with_signed_dpa_passes(tenant_a, owner_user):
    _plan_features(tenant_a, "N4")
    set_db_tenant(tenant_a.id)
    try:
        DpaStatement.objects.create(
            tenant_id=tenant_a.id, status=DpaStatement.Status.SIGNED, version="v1"
        )
        action = ActionContext(
            tenant_id=str(tenant_a.id),
            data_class="N3",
            source="email_body",
        )
        decision = D9Gate.evaluate(
            actor_id=str(owner_user.id), actor_role="owner", action=action
        )
    finally:
        clear_db_tenant()

    assert decision.allowed is True
    assert decision.effective_classification == "N3"
    assert decision.requires_human_gate is True


@pytest.mark.django_db
def test_ceiling_exceeded_blocks(tenant_a, owner_user):
    _plan_features(tenant_a, "N1")
    set_db_tenant(tenant_a.id)
    try:
        DpaStatement.objects.create(
            tenant_id=tenant_a.id, status=DpaStatement.Status.SIGNED, version="v1"
        )
        action = ActionContext(
            tenant_id=str(tenant_a.id),
            data_class="N2",
            source="email_body",
        )
        decision = D9Gate.evaluate(
            actor_id=str(owner_user.id), actor_role="owner", action=action
        )
    finally:
        clear_db_tenant()

    assert decision.allowed is False
    assert "ceiling" in decision.blocked_reason


@pytest.mark.django_db
def test_block_is_recorded_and_event_emitted(tenant_a, owner_user):
    _plan_features(tenant_a, "N4")
    set_db_tenant(tenant_a.id)
    try:
        action = ActionContext(
            tenant_id=str(tenant_a.id),
            data_class="N4",
            source="email_body",
            case_id="case-123",
        )
        D9Gate.evaluate(
            actor_id=str(owner_user.id), actor_role="owner", action=action
        )
    finally:
        clear_db_tenant()

    set_db_tenant(tenant_a.id)
    try:
        assert PolicyBlock.objects.filter(tenant_id=tenant_a.id, case_id="case-123").exists()
        assert Outbox.objects.filter(event_type="policy.gate.blocked").exists()
    finally:
        clear_db_tenant()


@pytest.mark.django_db
def test_pre_egress_classification_mismatch_blocks(tenant_a, owner_user):
    _plan_features(tenant_a, "N4")
    set_db_tenant(tenant_a.id)
    try:
        DpaStatement.objects.create(
            tenant_id=tenant_a.id, status=DpaStatement.Status.SIGNED, version="v1"
        )
        action = ActionContext(
            tenant_id=str(tenant_a.id),
            data_class="N1",
            source="email_body",
            case_id="case-mismatch",
        )
        decision = D9Gate.pre_egress(
            actor_id=str(owner_user.id),
            actor_role="owner",
            action=action,
            output_text="This output contains a SSN 123-45-6789",
        )
    finally:
        clear_db_tenant()

    assert decision.allowed is False
    assert decision.blocked_reason == "ClassificationMismatch"
    assert decision.effective_classification == "N4"

    set_db_tenant(tenant_a.id)
    try:
        assert Outbox.objects.filter(event_type="policy.classification_mismatch").exists()
    finally:
        clear_db_tenant()


@pytest.mark.django_db
def test_owner_can_sign_dpa(client: Client, tenant_a, owner_user, owner_membership):
    _plan_features(tenant_a, "N4")
    session_id = _login(client, owner_user, tenant_a)
    client.cookies["session_id"] = session_id

    resp = client.post(reverse("policy-dpa-sign"), content_type="application/json")
    assert resp.status_code == 200, resp.json()
    assert resp.json()["status"] == "signed"


@pytest.mark.django_db
def test_admin_cannot_sign_dpa(client: Client, tenant_a, owner_user):
    _plan_features(tenant_a, "N4")
    admin_user = User.objects.create_user(
        email="admin@example.com", password="FaberLoom1234!"
    )
    Membership.objects.create(
        user=admin_user,
        tenant=tenant_a,
        roles=["admin"],
        active_hat="admin",
        status=MembershipStatus.ACTIVE,
    )
    session_id = _login(client, admin_user, tenant_a)
    client.cookies["session_id"] = session_id

    resp = client.post(reverse("policy-dpa-sign"), content_type="application/json")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_evaluate_endpoint_blocks_n3_without_dpa(
    client: Client, tenant_a, owner_user, owner_membership
):
    _plan_features(tenant_a, "N4")
    session_id = _login(client, owner_user, tenant_a)
    client.cookies["session_id"] = session_id

    resp = client.post(
        reverse("policy-evaluate"),
        {"data_class": "N3", "source": "email_body"},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    assert data["allowed"] is False
    assert "DPA" in data["blocked_reason"]


@pytest.mark.django_db
def test_blocks_list_requires_audit_permission(
    client: Client, tenant_a, owner_user, owner_membership
):
    _plan_features(tenant_a, "N4")
    session_id = _login(client, owner_user, tenant_a)
    client.cookies["session_id"] = session_id

    resp = client.get(reverse("policy-blocks"))
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
