"""M14 Outcome Ledger, Gold Samples and Learning Thermometer tests."""
from __future__ import annotations

import pytest
from django.utils import timezone

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.drafts.services import DraftService
from apps.learning.gold import GoldSampleService, PromotionRejected
from apps.learning.models import GoldSample, OutcomeLedgerEntry
from apps.learning.thermometer import update_thermometer
from apps.tasks.models import Task


pytestmark = pytest.mark.django_db


def _approve_draft(tenant, draft, user):
    set_db_tenant(tenant.id)
    try:
        DraftService.approve(draft, user, "operator")
    finally:
        clear_db_tenant()


def test_approved_high_confidence_creates_candidate(tenant, user, draft):
    _approve_draft(tenant, draft, user)

    set_db_tenant(tenant.id)
    try:
        assert OutcomeLedgerEntry.objects.filter(
            tenant_id=tenant.id,
            draft=draft,
            decision=OutcomeLedgerEntry.Decision.APPROVED,
        ).exists()
        assert GoldSample.objects.filter(
            tenant_id=tenant.id,
            agent_id="@cotizador",
            status=GoldSample.Status.CANDIDATE,
        ).exists()
    finally:
        clear_db_tenant()


def test_edited_decision_writes_diff(tenant, user, draft):
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

    set_db_tenant(tenant.id)
    try:
        entry = OutcomeLedgerEntry.objects.get(
            tenant_id=tenant.id,
            draft=draft,
            decision=OutcomeLedgerEntry.Decision.EDITED,
        )
        assert entry.diff.get("edit_classification") == "tone"
        assert entry.diff.get("edit_reason") == "ajuste de tono"
    finally:
        clear_db_tenant()


def test_promotion_requires_validations(tenant, curator):
    set_db_tenant(tenant.id)
    try:
        gold = GoldSample.objects.create(
            tenant=tenant,
            agent_id="@cotizador",
            input_json={},
            output_json={},
            status=GoldSample.Status.CANDIDATE,
        )

        with pytest.raises(PromotionRejected):
            GoldSampleService.promote(gold, curator, "curator")

        gold.refresh_from_db()
        assert gold.status == GoldSample.Status.CANDIDATE
    finally:
        clear_db_tenant()


def test_n2_plus_requires_second_approver(tenant, user, n2_task, curator, second_approver):
    set_db_tenant(tenant.id)
    try:
        n2_draft = DraftService.generate(n2_task)
        DraftService.approve(n2_draft, user, "operator")
    finally:
        clear_db_tenant()

    set_db_tenant(tenant.id)
    try:
        gold = GoldSample.objects.get(tenant_id=tenant.id, agent_id="@cotizador", status=GoldSample.Status.CANDIDATE)
        result = GoldSampleService.promote(gold, curator, "operator")
        assert result.requires_second_approver is True
        gold.refresh_from_db()
        assert gold.status == GoldSample.Status.BLOCKED_PENDING_SECOND_APPROVER

        GoldSampleService.approve_second(gold, second_approver, "Supervisor")
        gold.refresh_from_db()
        assert gold.status == GoldSample.Status.ACTIVE
        assert gold.second_approver == second_approver
    finally:
        clear_db_tenant()


def test_deprecated_gold_not_used(tenant, user, curator, draft):
    _approve_draft(tenant, draft, user)

    set_db_tenant(tenant.id)
    try:
        gold = GoldSample.objects.get(tenant_id=tenant.id, agent_id="@cotizador")
        GoldSampleService.promote(gold, curator, "Owner")
        gold.refresh_from_db()
        assert gold.status == GoldSample.Status.ACTIVE

        GoldSampleService.deprecate(gold, curator, "outdated")
        gold.refresh_from_db()
        assert gold.status == GoldSample.Status.DEPRECATED
        assert GoldSample.objects.filter(
            tenant_id=tenant.id,
            agent_id="@cotizador",
            status=GoldSample.Status.ACTIVE,
        ).count() == 0
    finally:
        clear_db_tenant()


def test_thermometer_buckets(tenant, user):
    # Three approvals should score 3 -> warm bucket.
    for _ in range(3):
        set_db_tenant(tenant.id)
        try:
            t = Task.objects.create(
                tenant=tenant,
                agent_id="@cotizador",
                invocation_mode=Task.InvocationMode.INBOUND,
                priority=Task.Priority.NORMAL,
                payload={"subject": "Cotización"},
                status=Task.Status.RUNNING,
                expected_completion_by=timezone.now() + timezone.timedelta(hours=1),
            )
            d = DraftService.generate(t)
            DraftService.approve(d, user, "operator")
        finally:
            clear_db_tenant()

    thermometer = update_thermometer(str(tenant.id), "@cotizador")
    assert thermometer.score == 3
    assert thermometer.bucket == "warm"
