"""Learning Thermometer scoring for M14."""
from __future__ import annotations

from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.learning.models import LearningThermometer, OutcomeLedgerEntry


def update_thermometer(tenant_id: str, agent_id: str) -> LearningThermometer:
    """Update the learning thermometer score for an agent based on approved decisions."""
    set_db_tenant(tenant_id)
    try:
        score = OutcomeLedgerEntry.objects.filter(
            tenant_id=tenant_id,
            draft__task__agent_id=agent_id,
            decision=OutcomeLedgerEntry.Decision.APPROVED,
        ).count()
        # Cap the score so the thermometer does not grow unbounded in E1.
        score = min(score, 9)
        thermometer, _ = LearningThermometer.objects.update_or_create(
            tenant_id=tenant_id,
            agent_id=agent_id,
            defaults={"score": score},
        )
        return thermometer
    finally:
        clear_db_tenant()
