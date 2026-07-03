"""Oscillation counter for M13 Draft HITL."""
from __future__ import annotations

from django.conf import settings

from apps.drafts.models import OscillationCounter
from apps.events.emit import emit_event


def record_approval(tenant_id: str, user_id: str, agent_id: str, edited: bool) -> None:
    """Record an approval decision and fire review-cycle event if needed."""
    counter, _ = OscillationCounter.objects.get_or_create(
        tenant_id=tenant_id,
        user_id=user_id,
        agent_id=agent_id,
        defaults={"consecutive_clean_approvals": 0},
    )

    if edited:
        counter.consecutive_clean_approvals = 0
    else:
        counter.consecutive_clean_approvals += 1

    limit = getattr(settings, "OSCILLATION_LIMIT", 10)
    if counter.consecutive_clean_approvals >= limit:
        emit_event(
            tenant_id=tenant_id,
            event_type="draft.review_cycle_required",
            payload={
                "user_id": str(user_id),
                "agent_id": agent_id,
                "consecutive_clean_approvals": counter.consecutive_clean_approvals,
            },
        )
        counter.consecutive_clean_approvals = 0

    counter.save()
