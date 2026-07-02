"""M12 Audit Trail integration tests."""
from __future__ import annotations

import uuid

import pytest
from django.db import connection
from django.test import Client
from django.urls import reverse

from apps.audit.models import AuditLog
from apps.audit.tasks import validate_audit_chains, validate_chain
from apps.audit.writer import AuditContext, AuditWriter
from apps.auth_session import session as session_store
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.events.models import Outbox
from apps.users.models import Membership, MembershipStatus, User


class tenant_scope:
    """Context manager that sets the DB tenant for RLS-aware queries."""

    def __init__(self, tenant_id):
        self.tenant_id = tenant_id

    def __enter__(self):
        set_db_tenant(self.tenant_id)
        return self

    def __exit__(self, exc_type, exc, tb):
        clear_db_tenant()
        return False


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


def _set_tenant(tenant_id):
    set_db_tenant(tenant_id)


def _audit_count(tenant_id):
    _set_tenant(tenant_id)
    try:
        return AuditLog.objects.filter(tenant_id=tenant_id).count()
    finally:
        clear_db_tenant()


@pytest.mark.django_db
def test_audit_writer_append_only_tenant_scoped_chain(
    tenant_a, tenant_b, owner_user
):
    ctx_a = AuditContext(
        tenant_id=tenant_a.id,
        actor_id=owner_user.id,
        actor_role_at_decision="owner",
    )
    entry1 = AuditWriter.write(ctx_a, action_id="task.started", payload={"task_id": "t1"})
    entry2 = AuditWriter.write(ctx_a, action_id="task.finished", payload={"task_id": "t1"})

    assert entry1.seq_no > 0
    assert entry2.seq_no == entry1.seq_no + 1
    assert entry2.sha_chain_prev == entry1.sha_chain_curr
    assert entry1.sha_chain_curr != entry1.sha_chain_prev

    # Tenant B gets its own chain starting from genesis.
    ctx_b = AuditContext(
        tenant_id=tenant_b.id,
        actor_id=owner_user.id,
        actor_role_at_decision="owner",
    )
    entry_b = AuditWriter.write(ctx_b, action_id="task.started", payload={"task_id": "t2"})
    assert entry_b.chain_id == f"{tenant_b.id}:default"
    assert entry_b.sha_chain_prev == "0" * 64

    # Tenant-scoped isolation.
    assert _audit_count(tenant_a.id) == 2
    assert _audit_count(tenant_b.id) == 1


@pytest.mark.django_db
def test_audit_entry_emits_event(tenant_a, owner_user):
    AuditWriter.write(
        AuditContext(
            tenant_id=tenant_a.id,
            actor_id=owner_user.id,
            actor_role_at_decision="owner",
        ),
        action_id="task.started",
    )
    assert Outbox.objects.filter(event_type="audit.entry.created").exists()


@pytest.mark.django_db(transaction=True)
def test_update_audit_log_is_rejected(tenant_a, owner_user):
    entry = AuditWriter.write(
        AuditContext(
            tenant_id=tenant_a.id,
            actor_id=owner_user.id,
            actor_role_at_decision="owner",
        ),
        action_id="task.started",
    )

    with pytest.raises(Exception, match="append-only"):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE audit_log SET action_id = %s WHERE id = %s",
                ["tampered", str(entry.id)],
            )


@pytest.mark.django_db(transaction=True)
def test_delete_audit_log_is_rejected(tenant_a, owner_user):
    entry = AuditWriter.write(
        AuditContext(
            tenant_id=tenant_a.id,
            actor_id=owner_user.id,
            actor_role_at_decision="owner",
        ),
        action_id="task.started",
    )

    with pytest.raises(Exception, match="append-only"):
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM audit_log WHERE id = %s",
                [str(entry.id)],
            )


@pytest.mark.django_db
def test_validate_chain_detects_no_rupture(tenant_a, owner_user):
    AuditWriter.write(
        AuditContext(
            tenant_id=tenant_a.id,
            actor_id=owner_user.id,
            actor_role_at_decision="owner",
        ),
        action_id="task.started",
        payload={"task_id": "t1"},
    )
    report = validate_chain(str(tenant_a.id), f"{tenant_a.id}:default")
    assert report["valid"] is True
    assert report["checked"] == 1


@pytest.mark.django_db(transaction=True)
def test_validate_chain_detects_rupture(tenant_a, owner_user):
    AuditWriter.write(
        AuditContext(
            tenant_id=tenant_a.id,
            actor_id=owner_user.id,
            actor_role_at_decision="owner",
        ),
        action_id="task.started",
        payload={"task_id": "t1"},
    )

    # Inject a forged entry directly to simulate tampering.
    _set_tenant(tenant_a.id)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT nextval('audit_seq')")
            (seq_no,) = cursor.fetchone()
            cursor.execute(
                """
                INSERT INTO audit_log (
                    id, tenant_id, action_id, data_class, sha_chain_prev, sha_chain_curr,
                    seq_no, chain_id, actor_id, actor_role_at_decision, payload_json
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                [
                    str(uuid.uuid4()),
                    str(tenant_a.id),
                    "task.forged",
                    "N1",
                    "0" * 64,
                    "0" * 64,
                    seq_no,
                    f"{tenant_a.id}:default",
                    str(owner_user.id),
                    "owner",
                    "{}",
                ],
            )
    finally:
        clear_db_tenant()

    report = validate_chain(str(tenant_a.id), f"{tenant_a.id}:default")
    assert report["valid"] is False
    assert any(b["reason"] == "prev_hash_mismatch" for b in report["breaks"])


@pytest.mark.django_db
def test_validate_audit_chains_job(tenant_a, tenant_b, owner_user):
    AuditWriter.write(
        AuditContext(tenant_id=tenant_a.id, actor_id=owner_user.id, actor_role_at_decision="owner"),
        action_id="task.started",
    )
    AuditWriter.write(
        AuditContext(tenant_id=tenant_b.id, actor_id=owner_user.id, actor_role_at_decision="owner"),
        action_id="task.started",
    )

    report = validate_audit_chains()
    assert len(report["chains"]) >= 2
    assert all(c["valid"] for c in report["chains"])


@pytest.mark.django_db
def test_login_writes_audit_entry(
    client: Client, tenant_a, operator_user, operator_membership
):
    _login(client, operator_user, tenant_a)
    with tenant_scope(tenant_a.id):
        entry = AuditLog.objects.filter(
            tenant_id=tenant_a.id, action_id="auth.login.success"
        ).latest("seq_no")
    assert str(entry.actor_id) == str(operator_user.id)
    assert entry.actor_role_at_decision == "operator"


@pytest.mark.django_db
def test_invite_writes_audit_entry(
    client: Client, tenant_a, owner_user, owner_membership
):
    _login(client, owner_user, tenant_a)
    resp = client.post(
        reverse("rbac-memberships-invite"),
        {"email": "newoperator@example.com", "roles": ["operator"]},
        content_type="application/json",
    )
    assert resp.status_code == 201
    with tenant_scope(tenant_a.id):
        entry = AuditLog.objects.filter(
            tenant_id=tenant_a.id, action_id="users.invite"
        ).latest("seq_no")
    assert str(entry.actor_id) == str(owner_user.id)
    assert entry.actor_role_at_decision == "owner"


@pytest.mark.django_db
def test_audit_list_respects_read_self(
    client: Client, tenant_a, owner_user, owner_membership, operator_user, operator_membership
):
    AuditWriter.write(
        AuditContext(tenant_id=tenant_a.id, actor_id=owner_user.id, actor_role_at_decision="owner"),
        action_id="owner.action",
    )
    AuditWriter.write(
        AuditContext(
            tenant_id=tenant_a.id,
            actor_id=operator_user.id,
            actor_role_at_decision="operator",
        ),
        action_id="operator.action",
    )

    _login(client, operator_user, tenant_a)
    resp = client.get(reverse("audit-list"))
    assert resp.status_code == 200
    data = resp.json()
    assert all(str(e["actor_id"]) == str(operator_user.id) for e in data)

    _login(client, owner_user, tenant_a)
    resp = client.get(reverse("audit-list"))
    assert resp.status_code == 200
    data = resp.json()
    actions = {e["action_id"] for e in data}
    assert "owner.action" in actions
    assert "operator.action" in actions


@pytest.mark.django_db
def test_audit_export_requires_export_permission(
    client: Client, tenant_a, owner_user, owner_membership, operator_user, operator_membership
):
    _login(client, operator_user, tenant_a)
    resp = client.get(reverse("audit-export"))
    assert resp.status_code == 403

    _login(client, owner_user, tenant_a)
    resp = client.get(reverse("audit-export"))
    assert resp.status_code == 200
    assert resp.json()["validation_report"]["valid"] is True
