"""Outcome ledger service (M14 minimal hook for M13)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from apps.outcomes.models import OutcomeEntry

if TYPE_CHECKING:
    from apps.drafts.models import Draft
    from apps.tasks.models import Task


class OutcomeService:
    """Record an immutable outcome entry."""

    @classmethod
    def record(
        cls,
        tenant_id: str,
        action: OutcomeEntry.Action,
        draft: "Draft | None" = None,
        task: "Task | None" = None,
        diff: dict[str, Any] | None = None,
    ) -> OutcomeEntry:
        entry = OutcomeEntry.objects.create(
            tenant_id=tenant_id,
            draft=draft,
            task=task,
            action=action,
            diff=diff or {},
        )
        print(f"[OutcomeService] recorded {entry.id} action={entry.action} tenant={entry.tenant_id}")
        return entry
