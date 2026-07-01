"""M08 Auth Session integration tests."""
from __future__ import annotations

import pyotp
import pytest
from django.test import Client
from django.urls import reverse

from apps.auth_session import session as session_store
from apps.auth_session import totp as totp_helpers
from apps.auth_session.lockout import is_locked
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.users.models import Membership, MembershipStatus, User


@pytest.mark.django_db
def test_login_step_one_requires_email_password_tenant(client: Client):
    resp = client.post(
        reverse("auth-login"),
        {"email": "owner@example.com", "password": "x"},
        content_type="application/json",
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_login_step_one_invalid_credentials_do_not_leak_existence(
    client: Client, tenant_a
):
    resp = client.post(
        reverse("auth-login"),
        {
            "email": "notfound@example.com",
            "password": "wrong",
            "tenant_id": str(tenant_a.id),
        },
        content_type="application/json",
    )
    assert resp.status_code == 401


@pytest.mark.django_db
def test_login_step_one_membership_required(
    client: Client, tenant_a, owner_user
):
    # User exists but has no membership in tenant_a.
    resp = client.post(
        reverse("auth-login"),
        {
            "email": owner_user.email,
            "password": "FaberLoom1234!",
            "tenant_id": str(tenant_a.id),
        },
        content_type="application/json",
    )
    assert resp.status_code == 401


@pytest.mark.django_db
def test_login_step_one_returns_login_token_when_2fa_enrolled(
    client: Client, tenant_a, owner_user, owner_membership
):
    owner_user.totp_secret_encrypted = totp_helpers.encrypt_secret(
        totp_helpers.generate_totp_secret()
    )
    owner_user.save(update_fields=["totp_secret_encrypted"])

    resp = client.post(
        reverse("auth-login"),
        {
            "email": owner_user.email,
            "password": "FaberLoom1234!",
            "tenant_id": str(tenant_a.id),
        },
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["requires_2fa"] is True
    assert data["login_token"]


@pytest.mark.django_db
def test_login_step_one_direct_session_without_2fa(
    client: Client, tenant_a, operator_user, operator_membership
):
    resp = client.post(
        reverse("auth-login"),
        {
            "email": operator_user.email,
            "password": "FaberLoom1234!",
            "tenant_id": str(tenant_a.id),
        },
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["requires_2fa"] is False
    assert data["session_id"]
    assert "session_id" in resp.cookies


@pytest.mark.django_db
def test_login_step_two_valid_totp_creates_session(
    client: Client, tenant_a, owner_user, owner_membership
):
    secret = totp_helpers.generate_totp_secret()
    owner_user.totp_secret_encrypted = totp_helpers.encrypt_secret(secret)
    owner_user.save(update_fields=["totp_secret_encrypted"])

    step1 = client.post(
        reverse("auth-login"),
        {
            "email": owner_user.email,
            "password": "FaberLoom1234!",
            "tenant_id": str(tenant_a.id),
        },
        content_type="application/json",
    )
    login_token = step1.json()["login_token"]
    valid_code = pyotp.TOTP(secret).now()
    resp = client.post(
        reverse("auth-2fa"),
        {
            "login_token": login_token,
            "totp": valid_code,
            "tenant_id": str(tenant_a.id),
        },
        content_type="application/json",
    )
    assert resp.status_code == 200, resp.json()
    data = resp.json()
    assert data["session_id"]
    assert data["tenant_id"] == str(tenant_a.id)
    assert "owner" in data["roles"]
    assert "session_id" in resp.cookies


@pytest.mark.django_db
def test_login_step_two_invalid_totp_increments_lockout(
    client: Client, tenant_a, owner_user, owner_membership
):
    secret = totp_helpers.generate_totp_secret()
    owner_user.totp_secret_encrypted = totp_helpers.encrypt_secret(secret)
    owner_user.save(update_fields=["totp_secret_encrypted"])

    step1 = client.post(
        reverse("auth-login"),
        {
            "email": owner_user.email,
            "password": "FaberLoom1234!",
            "tenant_id": str(tenant_a.id),
        },
        content_type="application/json",
    )
    login_token = step1.json()["login_token"]

    for i in range(3):
        resp = client.post(
            reverse("auth-2fa"),
            {
                "login_token": login_token,
                "totp": "000000",
                "tenant_id": str(tenant_a.id),
            },
            content_type="application/json",
        )
        if i < 2:
            assert resp.status_code == 401
        else:
            assert resp.status_code == 423
            assert "retry_after" in resp.json()

    assert is_locked(tenant_a.id, owner_user.id)


@pytest.mark.django_db
def test_me_requires_session(client: Client, tenant_a, owner_user, owner_membership):
    session_id = session_store.create_session(
        owner_user.id, tenant_a.id, ["owner"], "owner"
    )
    client.cookies["session_id"] = session_id
    resp = client.get(reverse("auth-me"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == str(owner_user.id)
    assert data["tenant_id"] == str(tenant_a.id)
    assert "owner" in data["roles"]


@pytest.mark.django_db
def test_me_rejects_anonymous(client: Client):
    resp = client.get(reverse("auth-me"))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_logout_revokes_session(
    client: Client, tenant_a, owner_user, owner_membership
):
    session_id = session_store.create_session(
        owner_user.id, tenant_a.id, ["owner"], "owner"
    )
    client.cookies["session_id"] = session_id

    resp = client.post(reverse("auth-logout"))
    assert resp.status_code == 200
    assert session_store.get_session(session_id, tenant_a.id) is None
    assert "session_id" not in resp.cookies or not resp.cookies["session_id"].value


@pytest.mark.django_db
def test_logout_all_revokes_user_sessions(
    client: Client, tenant_a, owner_user, owner_membership
):
    s1 = session_store.create_session(owner_user.id, tenant_a.id, ["owner"], "owner")
    s2 = session_store.create_session(owner_user.id, tenant_a.id, ["owner"], "owner")
    client.cookies["session_id"] = s1

    resp = client.post(reverse("auth-logout-all"))
    assert resp.status_code == 200
    assert session_store.get_session(s1, tenant_a.id) is None
    assert session_store.get_session(s2, tenant_a.id) is None


@pytest.mark.django_db
def test_owner_can_revoke_member_session(
    client: Client, tenant_a, owner_user, owner_membership, operator_user, operator_membership
):
    owner_session = session_store.create_session(
        owner_user.id, tenant_a.id, ["owner"], "owner"
    )
    operator_session = session_store.create_session(
        operator_user.id, tenant_a.id, ["operator"], "operator"
    )
    client.cookies["session_id"] = owner_session

    resp = client.post(
        reverse("auth-revoke-session", kwargs={"session_id": operator_session})
    )
    assert resp.status_code == 200
    assert session_store.get_session(operator_session, tenant_a.id) is None
    assert session_store.get_session(owner_session, tenant_a.id) is not None


@pytest.mark.django_db
def test_operator_cannot_revoke_sessions(
    client: Client, tenant_a, operator_user, operator_membership, owner_user
):
    operator_session = session_store.create_session(
        operator_user.id, tenant_a.id, ["operator"], "operator"
    )
    owner_session = session_store.create_session(
        owner_user.id, tenant_a.id, ["owner"], "owner"
    )
    client.cookies["session_id"] = operator_session

    resp = client.post(
        reverse("auth-revoke-session", kwargs={"session_id": owner_session})
    )
    assert resp.status_code == 403


@pytest.mark.django_db
def test_password_change_invalidates_sessions(
    client: Client, tenant_a, owner_user, owner_membership
):
    session_id = session_store.create_session(
        owner_user.id, tenant_a.id, ["owner"], "owner"
    )
    owner_user.set_password("NewPassword1234!")
    owner_user.save(update_fields=["password"])
    assert session_store.get_session(session_id, tenant_a.id) is None


@pytest.mark.django_db
def test_backup_code_can_be_used_once(
    client: Client, tenant_a, owner_user, owner_membership
):
    secret = totp_helpers.generate_totp_secret()
    plain_codes, hashed = totp_helpers.generate_backup_codes(10)
    owner_user.totp_secret_encrypted = totp_helpers.encrypt_secret(secret)
    owner_user.backup_codes_hashed = hashed
    owner_user.save(update_fields=["totp_secret_encrypted", "backup_codes_hashed"])

    step1 = client.post(
        reverse("auth-login"),
        {
            "email": owner_user.email,
            "password": "FaberLoom1234!",
            "tenant_id": str(tenant_a.id),
        },
        content_type="application/json",
    )
    login_token = step1.json()["login_token"]

    resp = client.post(
        reverse("auth-2fa"),
        {
            "login_token": login_token,
            "totp": plain_codes[0],
            "tenant_id": str(tenant_a.id),
        },
        content_type="application/json",
    )
    assert resp.status_code == 200

    # Refresh user to check backup code was consumed.
    owner_user.refresh_from_db()
    assert len(owner_user.backup_codes_hashed) == 9
