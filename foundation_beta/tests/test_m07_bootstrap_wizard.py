"""M07 Bootstrap Wizard integration tests."""
from __future__ import annotations

import pytest
from django.test import Client
from django.urls import reverse

from apps.auth_session import session as session_store
from apps.bootstrap.models import SystemAgent, TenantBootstrapProgress, VoiceProfile
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.events.models import Outbox
from apps.policy.models import DpaStatement
from apps.tenants.models import Tenant, TenantPlanFeatures
from apps.users.models import Membership, MembershipStatus, User


def _session(client: Client, user, tenant_id: str):
    session_id = session_store.create_session(
        user.id, tenant_id, ["owner"], "owner"
    )
    client.cookies["session_id"] = session_id


@pytest.fixture
def platform_admin(db):
    return User.objects.create_user(
        email="platform@example.com",
        password="FaberLoom1234!",
        display_name="Platform Admin",
    )


@pytest.fixture
def setup_tenant(db):
    tenant = Tenant.objects.create(
        slug="setup-tenant",
        legal_name="Setup Tenant Legal",
        commercial_name="Setup Tenant",
        vertical_spec_object_id="vertical-setup",
        plan_tier="starter",
        status=Tenant.Status.SETUP,
    )
    TenantPlanFeatures.objects.create(tenant=tenant, data_class_ceiling="N4")
    return tenant


@pytest.fixture
def setup_owner(db, setup_tenant):
    user = User.objects.create_user(
        email="owner-setup@example.com",
        password="FaberLoom1234!",
        display_name="Setup Owner",
    )
    Membership.objects.create(
        user=user,
        tenant=setup_tenant,
        roles=["owner"],
        active_hat="owner",
        status=MembershipStatus.ACTIVE,
    )
    return user


def _complete_step(client, tenant_id, step, payload=None):
    resp = client.post(
        reverse("bootstrap-step", kwargs={"tenant_id": tenant_id, "step": step}),
        payload or {},
        content_type="application/json",
    )
    assert resp.status_code == 200, f"step {step}: {resp.json()}"


@pytest.mark.django_db
def test_invite_owner_creates_invited_membership(
    client: Client, platform_admin, setup_tenant
):
    _session(client, platform_admin, str(setup_tenant.id))
    resp = client.post(
        reverse("bootstrap-invite-owner", kwargs={"tenant_id": setup_tenant.id}),
        {"email": "future-owner@example.com"},
        content_type="application/json",
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "invited"

    set_db_tenant(setup_tenant.id)
    try:
        membership = Membership.objects.get(id=data["membership_id"])
        assert membership.status == MembershipStatus.INVITED
        assert membership.roles == ["owner"]
        assert Outbox.objects.filter(event_type="user.invited").exists()
    finally:
        clear_db_tenant()


@pytest.mark.django_db
def test_invitation_expires_in_7_days(client: Client, platform_admin, setup_tenant):
    _session(client, platform_admin, str(setup_tenant.id))
    resp = client.post(
        reverse("bootstrap-invite-owner", kwargs={"tenant_id": setup_tenant.id}),
        {"email": "expiring-owner@example.com"},
        content_type="application/json",
    )
    assert resp.status_code == 201
    set_db_tenant(setup_tenant.id)
    try:
        membership = Membership.objects.get(id=resp.json()["membership_id"])
        from datetime import timedelta
        assert membership.invited_at is not None
        event = Outbox.objects.filter(event_type="user.invited").latest("created_at")
        expires = event.payload_json.get("expires_at")
        assert expires is not None
        assert expires.startswith((membership.invited_at + timedelta(days=6)).isoformat()[:10])
    finally:
        clear_db_tenant()


@pytest.mark.django_db
def test_bootstrap_persists_progress(
    client: Client, platform_admin, setup_tenant, setup_owner
):
    _session(client, setup_owner, str(setup_tenant.id))
    _complete_step(client, setup_tenant.id, "tenant_data", {"legal_name": "Acme"})

    resp = client.get(reverse("bootstrap-status", kwargs={"tenant_id": setup_tenant.id}))
    assert resp.status_code == 200
    data = resp.json()
    assert "tenant_data" in data["steps_completed"]


@pytest.mark.django_db
def test_seed_agents_are_shadow(
    client: Client, setup_tenant, setup_owner
):
    _session(client, setup_owner, str(setup_tenant.id))
    _complete_step(client, setup_tenant.id, "seed_agents")

    set_db_tenant(setup_tenant.id)
    try:
        agents = list(SystemAgent.objects.filter(tenant_id=setup_tenant.id))
        assert len(agents) == 2
        assert all(a.status == SystemAgent.Status.SHADOW for a in agents)
        assert any(a.name == "@router" for a in agents)
        assert any(a.name == "@cotizador" for a in agents)
    finally:
        clear_db_tenant()


@pytest.mark.django_db
def test_sandbox_generates_draft_no_external_egress(
    client: Client, setup_tenant, setup_owner
):
    _session(client, setup_owner, str(setup_tenant.id))
    _complete_step(client, setup_tenant.id, "dpa_signed")

    resp = client.post(
        reverse("bootstrap-sandbox", kwargs={"tenant_id": setup_tenant.id}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["passed"] is True
    assert "draft" in data


@pytest.mark.django_db
def test_activation_blocked_without_dpa(
    client: Client, setup_tenant, setup_owner
):
    _session(client, setup_owner, str(setup_tenant.id))
    steps = ["tenant_data", "owner_2fa", "mailbox", "kb_seed", "voice_profile", "seed_agents"]
    for step in steps:
        payload = None
        if step == "owner_2fa":
            payload = {}
        elif step == "mailbox":
            payload = {"provider": "imap_smtp", "account": "box@example.com", "credentials_encrypted": "enc"}
        elif step == "kb_seed":
            payload = {"count": 5}
        elif step == "voice_profile":
            payload = {
                "user_id": str(setup_owner.id),
                "persona": "professional",
                "tone": "warm",
                "glossary": ["RFQ"],
                "greeting": "Hello",
                "signature": "Best",
            }
        _complete_step(client, setup_tenant.id, step, payload)

    resp = client.post(
        reverse("bootstrap-activate", kwargs={"tenant_id": setup_tenant.id}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "DPA" in resp.json()["detail"]


@pytest.mark.django_db
def test_full_bootstrap_activates_tenant(
    client: Client, setup_tenant, setup_owner
):
    _session(client, setup_owner, str(setup_tenant.id))

    _complete_step(
        client,
        setup_tenant.id,
        "tenant_data",
        {"legal_name": "Acme Inc", "commercial_name": "Acme", "slug": "acme"},
    )
    _complete_step(client, setup_tenant.id, "owner_2fa")
    _complete_step(
        client,
        setup_tenant.id,
        "mailbox",
        {"provider": "imap_smtp", "account": "inbox@acme.com", "credentials_encrypted": "enc"},
    )
    _complete_step(client, setup_tenant.id, "kb_seed", {"count": 5})
    _complete_step(
        client,
        setup_tenant.id,
        "voice_profile",
        {
            "user_id": str(setup_owner.id),
            "persona": "professional",
            "tone": "warm",
            "glossary": ["RFQ"],
            "greeting": "Hello",
            "signature": "Best regards",
        },
    )
    _complete_step(client, setup_tenant.id, "dpa_signed")
    _complete_step(client, setup_tenant.id, "seed_agents")

    resp = client.post(
        reverse("bootstrap-sandbox", kwargs={"tenant_id": setup_tenant.id}),
        content_type="application/json",
    )
    assert resp.status_code == 200

    resp = client.post(
        reverse("bootstrap-activate", kwargs={"tenant_id": setup_tenant.id}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "active"

    setup_tenant.refresh_from_db()
    assert setup_tenant.status == Tenant.Status.ACTIVE
    assert Outbox.objects.filter(event_type="tenant.activated").exists()


@pytest.mark.django_db
def test_only_owner_and_operator_are_active_roles_after_go_live(
    client: Client, setup_tenant, setup_owner
):
    _session(client, setup_owner, str(setup_tenant.id))
    for step in ["tenant_data", "owner_2fa", "mailbox", "kb_seed", "voice_profile", "dpa_signed", "seed_agents"]:
        payload = {}
        if step == "mailbox":
            payload = {"provider": "imap_smtp", "account": "inbox@acme.com", "credentials_encrypted": "enc"}
        elif step == "kb_seed":
            payload = {"count": 5}
        elif step == "voice_profile":
            payload = {
                "user_id": str(setup_owner.id),
                "persona": "professional",
                "tone": "warm",
                "glossary": ["RFQ"],
                "greeting": "Hello",
                "signature": "Best",
            }
        _complete_step(client, setup_tenant.id, step, payload)
    client.post(reverse("bootstrap-sandbox", kwargs={"tenant_id": setup_tenant.id}), content_type="application/json")
    client.post(reverse("bootstrap-activate", kwargs={"tenant_id": setup_tenant.id}), content_type="application/json")

    # Post go-live: invite an operator.
    resp = client.post(
        reverse("rbac-memberships-invite"),
        {"email": "operator@acme.com", "roles": ["operator"]},
        content_type="application/json",
    )
    assert resp.status_code == 201
    set_db_tenant(setup_tenant.id)
    try:
        roles = set(
            Membership.objects.filter(
                tenant_id=setup_tenant.id, status__in=[MembershipStatus.ACTIVE, MembershipStatus.INVITED]
            ).values_list("roles", flat=True)
        )
        flat = {r for sub in roles for r in sub}
        assert flat == {"owner", "operator"}
    finally:
        clear_db_tenant()
