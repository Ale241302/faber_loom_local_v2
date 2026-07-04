"""M17 Memory Letta: episodic, working TTL and persistent gate tests."""
from __future__ import annotations

import uuid

import pytest
from django.utils import timezone

from apps.core.memory import letta_namespace
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.memory.guard import MemoryConflictGuard
from apps.memory.models import MemoryConflict, MemoryItem
from apps.memory.services import MemoryService, PromptAssembler


pytestmark = pytest.mark.django_db


def test_namespace_includes_tenant_and_validates(tenant):
    ns = letta_namespace(tenant.id, "agent_1", "task_42", "working")
    assert f"tenant:{tenant.id}" in ns
    assert "agent:agent_1" in ns
    assert "task:task_42" in ns
    assert ns.endswith(":working")

    with pytest.raises(ValueError):
        letta_namespace(tenant.id, "bad agent", kind="working")


def test_working_memory_ttl_sweep(tenant, user, letta_client):
    set_db_tenant(tenant.id)
    try:
        fresh = MemoryService.record_working(
            tenant.id, "@cotizador", "task_fresh",
            {"subject": "fresh"}, client=letta_client,
        )
        stale = MemoryService.record_working(
            tenant.id, "@cotizador", "task_stale",
            {"subject": "stale"}, client=letta_client,
        )
        # Force the stale record to look older than 24h.
        stale.created_at = timezone.now() - timezone.timedelta(hours=25)
        stale.save(update_fields=["created_at"])
    finally:
        clear_db_tenant()

    swept = MemoryService.sweep_expired_working(tenant_id=tenant.id)
    assert swept == 1

    set_db_tenant(tenant.id)
    try:
        fresh.refresh_from_db()
        stale.refresh_from_db()
        assert fresh.status == MemoryItem.Status.ACTIVE
        assert stale.status == MemoryItem.Status.DEPRECATED
    finally:
        clear_db_tenant()


def test_persistent_requires_human_gate(tenant, user, letta_client):
    set_db_tenant(tenant.id)
    try:
        proposed = MemoryService.propose_persistent(
            tenant.id, "@cotizador",
            {"rule": "always greet formally"}, client=letta_client,
        )
        assert proposed.status == MemoryItem.Status.PROPOSED

        result = MemoryService.approve_persistent(
            proposed, user, "curator", client=letta_client, kb_chunks=[],
        )
        assert result["status"] == MemoryItem.Status.ACTIVE
        proposed.refresh_from_db()
        assert proposed.promoted_by == user
    finally:
        clear_db_tenant()


def test_kb_wins_conflict_guard(tenant, user, letta_client):
    set_db_tenant(tenant.id)
    try:
        proposed = MemoryService.propose_persistent(
            tenant.id, "@cotizador",
            {"rule": "Payment terms are net 30 days"}, client=letta_client,
        )
        kb_chunks = [
            {
                "text": "The official payment terms are net 30 days for all invoices.",
                "source": "kb/pricing",
            }
        ]
        result = MemoryService.approve_persistent(
            proposed, user, "curator", client=letta_client, kb_chunks=kb_chunks,
        )
        assert result["status"] == MemoryItem.Status.DISPUTED
        assert MemoryConflict.objects.filter(memory_item=proposed).exists()
        proposed.refresh_from_db()
        assert proposed.status == MemoryItem.Status.DISPUTED
    finally:
        clear_db_tenant()


def test_conflict_guard_no_false_positive(tenant):
    proposed = {"rule": "Use emojis sparingly"}
    kb_chunks = [
        {"text": "Quarterly revenue grew 12% year over year", "source": "kb/finance"}
    ]
    result = MemoryConflictGuard.check(proposed, kb_chunks)
    assert result.conflict is False


def test_disputed_and_proposed_not_injected(tenant, user, letta_client):
    set_db_tenant(tenant.id)
    try:
        active_persistent = MemoryService.propose_persistent(
            tenant.id, "@cotizador",
            {"rule": "active rule"}, client=letta_client,
        )
        MemoryService.approve_persistent(
            active_persistent, user, "curator", client=letta_client, kb_chunks=[],
        )

        disputed = MemoryService.propose_persistent(
            tenant.id, "@cotizador",
            {"rule": "disputed rule"}, client=letta_client,
        )
        MemoryService.approve_persistent(
            disputed, user, "curator", client=letta_client,
            kb_chunks=[{"text": "disputed rule", "source": "kb"}],
        )

        proposed = MemoryService.propose_persistent(
            tenant.id, "@cotizador",
            {"rule": "proposed rule"}, client=letta_client,
        )

        # Working + episodic active should still appear.
        MemoryService.record_working(
            tenant.id, "@cotizador", "task_1",
            {"subject": "working context"}, client=letta_client,
        )
        MemoryService.record_episodic(
            tenant.id, "@cotizador",
            {"type": "outcome", "value": "approved"}, client=letta_client,
        )
    finally:
        clear_db_tenant()

    sections = PromptAssembler.for_agent(
        tenant.id, "@cotizador", client=letta_client
    )
    persistent_ids = {e["memory_id"] for e in sections["persistent"]}
    assert str(active_persistent.id) in persistent_ids
    assert str(disputed.id) not in persistent_ids
    assert str(proposed.id) not in persistent_ids
    assert len(sections["working"]) == 1
    assert len(sections["episodic"]) == 1


def test_cross_tenant_read_blocked_by_rls(tenant, other_tenant, user, letta_client):
    set_db_tenant(tenant.id)
    try:
        item = MemoryService.record_working(
            tenant.id, "@cotizador", "task_x",
            {"secret": "tenant A"}, client=letta_client,
        )
    finally:
        clear_db_tenant()

    set_db_tenant(other_tenant.id)
    try:
        # The RLS policy should hide tenant A rows from tenant B queries.
        found = MemoryItem.objects.filter(id=item.id).first()
        assert found is None
    finally:
        clear_db_tenant()


def test_prompt_assembler_respects_task_scope(tenant, user, letta_client):
    set_db_tenant(tenant.id)
    try:
        MemoryService.record_working(
            tenant.id, "@cotizador", "task_scope",
            {"subject": "scoped"}, client=letta_client,
        )
        MemoryService.record_working(
            tenant.id, "@cotizador", "task_other",
            {"subject": "other"}, client=letta_client,
        )
    finally:
        clear_db_tenant()

    sections = PromptAssembler.for_agent(
        tenant.id, "@cotizador", client=letta_client, task_id="task_scope"
    )
    assert len(sections["working"]) == 1
    assert sections["working"][0]["content"]["subject"] == "scoped"


def test_reject_persistent_deprecates_item(tenant, user, letta_client):
    set_db_tenant(tenant.id)
    try:
        proposed = MemoryService.propose_persistent(
            tenant.id, "@cotizador",
            {"rule": "rejected"}, client=letta_client,
        )
        MemoryService.reject_persistent(proposed, user, "curator")
        proposed.refresh_from_db()
        assert proposed.status == MemoryItem.Status.DEPRECATED
    finally:
        clear_db_tenant()
