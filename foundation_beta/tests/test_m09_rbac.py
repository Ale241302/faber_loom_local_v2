"""M09 RBAC integration tests."""
from __future__ import annotations

import pytest
from django.test import Client
from django.urls import reverse

from apps.auth_session import session as session_store
from apps.events.models import OutboxEvent
from apps.rbac.models import Role
from apps.users.models import Membership, MembershipStatus, User


def _login(client: Client, user, tenant, password: str = "FaberLoom1234!") -> str:
    """Helper to authenticate a user and return session id."""
    resp = client.post(
        reverse("auth-login"),
        {"email": user.email, "password": password, "tenant_id": str(tenant.id)},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    if data.get("requires_2fa"):
        from apps.auth_session import totp as totp_helpers

        secret = totp_helpers.decrypt_secret(user.totp_secret_encrypted)
        import pyotp

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


@pytest.mark.django_db
def test_rbac_middleware_loads_membership(client: Client, tenant_a, owner_user, owner_membership):
    session_id = _login(client, owner_user, tenant_a)
    resp = client.get(reverse("auth-me"))
    assert resp.status_code == 200
    assert resp.json()["active_hat"] == "owner"


@pytest.mark.django_db
def test_owner_can_list_memberships(client: Client, tenant_a, owner_user, owner_membership):
    _login(client, owner_user, tenant_a)
    resp = client.get(reverse("rbac-memberships-list"))
    assert resp.status_code == 200
    data = resp.json()
    assert any(m["user_id"] == str(owner_user.id) for m in data)


@pytest.mark.django_db
def test_operator_cannot_list_memberships(
    client: Client, tenant_a, operator_user, operator_membership
):
    _login(client, operator_user, tenant_a)
    resp = client.get(reverse("rbac-memberships-list"))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_owner_can_invite_operator(client: Client, tenant_a, owner_user, owner_membership):
    _login(client, owner_user, tenant_a)
    resp = client.post(
        reverse("rbac-memberships-invite"),
        {"email": "newoperator@example.com", "roles": ["operator"]},
        content_type="application/json",
    )
    assert resp.status_code == 201, resp.json()
    data = resp.json()
    assert data["roles"] == ["operator"]
    assert data["status"] == "invited"
    assert OutboxEvent.objects.filter(event_type="user.invited").exists()


@pytest.mark.django_db
def test_admin_cannot_create_owner(
    client: Client, tenant_a, owner_user, owner_membership
):
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
    _login(client, admin_user, tenant_a)
    resp = client.post(
        reverse("rbac-memberships-invite"),
        {"email": "wannabeowner@example.com", "roles": ["owner"]},
        content_type="application/json",
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_last_owner_cannot_self_revoke(
    client: Client, tenant_a, owner_user, owner_membership
):
    _login(client, owner_user, tenant_a)
    resp = client.post(
        reverse("rbac-memberships-revoke", kwargs={"membership_id": str(owner_membership.id)})
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_revoke_membership_closes_sessions(
    client: Client, tenant_a, owner_user, owner_membership, operator_user, operator_membership
):
    operator_session = session_store.create_session(
        operator_user.id, tenant_a.id, ["operator"], "operator"
    )
    _login(client, owner_user, tenant_a)

    resp = client.post(
        reverse("rbac-memberships-revoke", kwargs={"membership_id": str(operator_membership.id)})
    )
    assert resp.status_code == 200
    assert session_store.get_session(operator_session, tenant_a.id) is None
    assert OutboxEvent.objects.filter(event_type="user.revoked").exists()


@pytest.mark.django_db
def test_role_change_emits_event(
    client: Client, tenant_a, owner_user, owner_membership, operator_user, operator_membership
):
    _login(client, owner_user, tenant_a)
    resp = client.patch(
        reverse("rbac-memberships-detail", kwargs={"membership_id": str(operator_membership.id)}),
        {"roles": ["viewer"]},
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.json()
    operator_membership.refresh_from_db()
    assert operator_membership.roles == ["viewer"]
    assert OutboxEvent.objects.filter(event_type="user.role_changed").exists()


@pytest.mark.django_db
def test_active_hat_header_is_validated(
    client: Client, tenant_a, owner_user
):
    Membership.objects.create(
        user=owner_user,
        tenant=tenant_a,
        roles=["owner", "operator"],
        active_hat="owner",
        status=MembershipStatus.ACTIVE,
    )
    session_id = _login(client, owner_user, tenant_a)

    resp = client.post(
        reverse("rbac-set-hat"),
        {"hat": "operator"},
        content_type="application/json",
        HTTP_X_ACTIVE_HAT="operator",
    )
    assert resp.status_code == 200
    assert resp.json()["active_hat"] == "operator"


@pytest.mark.django_db
def test_invalid_active_hat_is_rejected(
    client: Client, tenant_a, owner_user, owner_membership
):
    _login(client, owner_user, tenant_a)
    resp = client.post(
        reverse("rbac-set-hat"),
        {"hat": "admin"},
        content_type="application/json",
    )
    assert resp.status_code == 400
