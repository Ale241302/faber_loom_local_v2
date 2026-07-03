"""Gold sample lifecycle for M14."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.audit.writer import AuditContext, AuditWriter
from apps.core.tenant_context import clear_db_tenant, set_db_tenant
from apps.events.emit import emit_event
from apps.learning.models import GoldSample
from apps.users.models import User


class PromotionRejected(Exception):
    """Raised when a gold sample fails one or more promotion validations."""

    def __init__(self, validations: dict[str, bool]):
        self.validations = validations
        super().__init__(f"Promotion rejected: {validations}")


@dataclass
class PromotionResult:
    status: str
    requires_second_approver: bool = False


class GoldSampleService:
    """Promote, discard or deprecate gold samples."""

    VALIDATIONS = ["schema", "policy", "replay", "scope", "human_approval"]

    @classmethod
    def promote(
        cls,
        gold: GoldSample,
        curator: User,
        curator_role: str,
    ) -> PromotionResult:
        tenant_id = str(gold.tenant_id)
        set_db_tenant(gold.tenant_id)
        try:
            validations = cls._run_validations(gold)
            if not all(validations.values()):
                raise PromotionRejected(validations)

            if cls._requires_second_approver(gold, curator_role):
                gold.status = GoldSample.Status.BLOCKED_PENDING_SECOND_APPROVER
                gold.validations_json = validations
                gold.save(update_fields=["status", "validations_json", "updated_at"])
                return PromotionResult(
                    status=gold.status,
                    requires_second_approver=True,
                )

            gold.status = GoldSample.Status.ACTIVE
            gold.promoter = curator
            gold.promoted_at = timezone.now()
            gold.validations_json = validations
            gold.save(
                update_fields=[
                    "status",
                    "promoter",
                    "promoted_at",
                    "validations_json",
                    "updated_at",
                ]
            )

            emit_event(
                tenant_id=tenant_id,
                event_type="gold.promoted",
                payload={
                    "gold_sample_id": str(gold.id),
                    "agent_id": gold.agent_id,
                    "promoter_id": str(curator.id),
                    "validations": validations,
                },
            )
            AuditWriter.write(
                AuditContext(
                    tenant_id=tenant_id,
                    actor_id=curator.id,
                    actor_role_at_decision=curator_role,
                ),
                action_id="gold.promoted",
                payload={
                    "gold_sample_id": str(gold.id),
                    "agent_id": gold.agent_id,
                    "validations": validations,
                },
                emit=False,
            )
            return PromotionResult(status=gold.status)
        finally:
            clear_db_tenant()

    @classmethod
    def approve_second(
        cls,
        gold: GoldSample,
        approver: User,
        approver_role: str,
    ) -> None:
        """Second approver unblocks a gold sample pending second approval."""
        if gold.status != GoldSample.Status.BLOCKED_PENDING_SECOND_APPROVER:
            raise ValueError("gold sample is not pending second approver")

        allowed = {r.strip() for r in getattr(settings, "GOLD_SECOND_APPROVER_ROLES", "Supervisor,Admin,Owner").split(",")}
        if approver_role not in allowed:
            raise PermissionError("role cannot second-approve gold samples")

        tenant_id = str(gold.tenant_id)
        set_db_tenant(gold.tenant_id)
        try:
            gold.status = GoldSample.Status.ACTIVE
            gold.second_approver = approver
            gold.promoted_at = timezone.now()
            gold.save(update_fields=["status", "second_approver", "promoted_at", "updated_at"])

            emit_event(
                tenant_id=tenant_id,
                event_type="gold.promoted",
                payload={
                    "gold_sample_id": str(gold.id),
                    "agent_id": gold.agent_id,
                    "second_approver_id": str(approver.id),
                },
            )
            AuditWriter.write(
                AuditContext(
                    tenant_id=tenant_id,
                    actor_id=approver.id,
                    actor_role_at_decision=approver_role,
                ),
                action_id="gold.second_approved",
                payload={
                    "gold_sample_id": str(gold.id),
                    "agent_id": gold.agent_id,
                },
                emit=False,
            )
        finally:
            clear_db_tenant()

    @classmethod
    def discard(cls, gold: GoldSample) -> None:
        tenant_id = str(gold.tenant_id)
        set_db_tenant(gold.tenant_id)
        try:
            gold.status = GoldSample.Status.DISCARDED
            gold.save(update_fields=["status", "updated_at"])
            emit_event(
                tenant_id=tenant_id,
                event_type="gold.discarded",
                payload={"gold_sample_id": str(gold.id), "agent_id": gold.agent_id},
            )
        finally:
            clear_db_tenant()

    @classmethod
    def deprecate(cls, gold: GoldSample, curator: User, reason: str) -> None:
        tenant_id = str(gold.tenant_id)
        set_db_tenant(gold.tenant_id)
        try:
            gold.status = GoldSample.Status.DEPRECATED
            gold.validity_metadata = {**(gold.validity_metadata or {}), "deprecation_reason": reason}
            gold.save(update_fields=["status", "validity_metadata", "updated_at"])
            emit_event(
                tenant_id=tenant_id,
                event_type="gold.deprecated",
                payload={
                    "gold_sample_id": str(gold.id),
                    "agent_id": gold.agent_id,
                    "reason": reason,
                },
            )
            AuditWriter.write(
                AuditContext(
                    tenant_id=tenant_id,
                    actor_id=curator.id,
                    actor_role_at_decision="curator",
                ),
                action_id="gold.deprecated",
                payload={
                    "gold_sample_id": str(gold.id),
                    "agent_id": gold.agent_id,
                    "reason": reason,
                },
                emit=False,
            )
        finally:
            clear_db_tenant()

    @classmethod
    def _run_validations(cls, gold: GoldSample) -> dict[str, bool]:
        """Run the five canonical validations. E1 uses conservative heuristics."""
        return {
            "schema": bool(gold.output_json),
            "policy": cls._policy_validation(gold),
            "replay": cls._replay_validation(gold),
            "scope": bool(gold.agent_id),
            "human_approval": True,
        }

    @classmethod
    def _policy_validation(cls, gold: GoldSample) -> bool:
        # E1: no sensitive patterns in output text.
        import re

        text = str(gold.output_json)
        ssn = re.search(r"\b\d{3}-\d{2}-\d{4}\b", text)
        cc = re.search(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", text)
        return not (ssn or cc)

    @classmethod
    def _replay_validation(cls, gold: GoldSample) -> bool:
        # E1 stub: assume replay would succeed for non-empty input/output.
        return bool(gold.input_json) and bool(gold.output_json)

    @classmethod
    def _requires_second_approver(cls, gold: GoldSample, curator_role: str) -> bool:
        allowed = {r.strip() for r in getattr(settings, "GOLD_SECOND_APPROVER_ROLES", "Supervisor,Admin,Owner").split(",")}
        if curator_role in allowed:
            return False
        data_class = (gold.validity_metadata or {}).get("data_class", "N1")
        return data_class in ("N2", "N3", "N4")
