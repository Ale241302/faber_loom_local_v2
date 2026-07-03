"""M13 Draft HITL unit tests."""
from __future__ import annotations

import pytest
from django.conf import settings
from django.utils import timezone

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.drafts.models import Draft, DraftStatus
from apps.drafts.services import DraftService
from apps.outcomes.models import OutcomeEntry
from apps.tasks.models import Task


@pytest.mark.django_db
def test_draft_requires_approval_no_auto_send(tenant, task, draft):
    assert draft.status == DraftStatus.PENDING
    assert draft.original_content["body"]
    assert draft.evidence_bundle is not None
    assert draft.sent_at is None


@pytest.mark.django_db
def test_draft_edit_creates_diff_and_ledger_entry(tenant, user, draft):
    edited = {"subject": "Cotización actualizada", "body": "Contenido editado"}
    set_db_tenant(tenant.id)
    try:
        DraftService.edit_and_approve(
            draft=draft,
            edited=edited,
            reason="ajuste de tono",
            classification="tone",
            user=user,
            actor_role="operator",
        )
    finally:
        clear_db_tenant()

    assert draft.status == DraftStatus.SENT
    assert draft.edited_content == edited
    assert OutcomeEntry.objects.filter(
        tenant_id=tenant.id, draft=draft, action=OutcomeEntry.Action.EDITED
    ).exists()
    assert OutcomeEntry.objects.filter(
        tenant_id=tenant.id, draft=draft, action=OutcomeEntry.Action.SENT
    ).exists()


@pytest.mark.django_db
def test_draft_reject_with_reason(tenant, user, draft):
    set_db_tenant(tenant.id)
    try:
        DraftService.reject(draft, "incomplete_data", user, "operator")
    finally:
        clear_db_tenant()

    assert draft.status == DraftStatus.REJECTED
    assert draft.edit_reason == "incomplete_data"
    assert OutcomeEntry.objects.filter(
        tenant_id=tenant.id, draft=draft, action=OutcomeEntry.Action.REJECTED
    ).exists()


@pytest.mark.django_db
def test_draft_expires_without_action(tenant, draft):
    set_db_tenant(tenant.id)
    try:
        DraftService.expire(draft)
    finally:
        clear_db_tenant()

    assert draft.status == DraftStatus.EXPIRED


@pytest.mark.django_db
def test_d9_pre_egress_blocks_before_send(tenant, task, user):
    # Sensitive data (SSN pattern) triggers N4 classification mismatch in D9 pre-egress.
    task.payload["subject"] = "Cotización 123-45-6789"
    task.save(update_fields=["payload"])
    set_db_tenant(tenant.id)
    try:
        draft = DraftService.generate(task)
        DraftService.approve(draft, user, "operator")
    finally:
        clear_db_tenant()

    assert draft.status == DraftStatus.APPROVED_PENDING_SEND


@pytest.mark.django_db
def test_oscillation_counter_fires_after_n_clean_approvals(tenant, task, user, captured_events, monkeypatch):
    limit = 3
    monkeypatch.setattr(settings, "OSCILLATION_LIMIT", limit)

    set_db_tenant(tenant.id)
    try:
        for _ in range(limit):
            t = Task.objects.create(
                tenant=tenant,
                agent_id="@cotizador",
                invocation_mode=Task.InvocationMode.INBOUND,
                priority=Task.Priority.NORMAL,
                payload={"subject": "Cotización", "recipient": "a@b.com", "source_type": "email"},
                status=Task.Status.RUNNING,
            )
            d = DraftService.generate(t)
            DraftService.approve(d, user, "operator")
    finally:
        clear_db_tenant()

    assert "draft.review_cycle_required" in captured_events


@pytest.mark.django_db
def test_channel_failure_goes_to_approved_pending_send(tenant, task, user, monkeypatch):
    set_db_tenant(tenant.id)
    try:
        draft = DraftService.generate(task)
        monkeypatch.setattr("apps.drafts.channel_sender.send_mail", lambda *a, **k: (_ for _ in ()).throw(Exception("SMTP down")))
        DraftService.approve(draft, user, "operator")
    finally:
        clear_db_tenant()

    assert draft.status == DraftStatus.APPROVED_PENDING_SEND
