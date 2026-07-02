"""D9 Policy Gate for M11."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from django.db import transaction

from apps.audit.writer import AuditContext, AuditWriter
from apps.events.emit import emit_event

from .models import DataClassificationDefault, DpaStatement, PolicyBlock

from apps.tenants.models import TenantPlanFeatures


DATA_CLASS_ORDER = {
    "N0": 0,
    "N1": 1,
    "N2": 2,
    "N3": 3,
    "N4": 4,
}


@dataclass
class RetrievedChunk:
    data_class: str = "N1"
    source_type: str = ""


@dataclass
class ActionContext:
    """Input context for the D9 gate."""

    task_type: str = ""
    data_class: str = "N1"
    skill_id: str = ""
    confidence: float = 0.0
    source: str = ""
    tenant_id: str = ""
    case_id: str | None = None
    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)


@dataclass
class PolicyDecision:
    allowed: bool
    blocked_reason: str | None
    effective_classification: str
    requires_human_gate: bool


class D9Gate:
    """Fail-closed D9 data policy gate."""

    # Simple heuristic patterns that bump classification to N3/N4 pre-egress.
    _SENSITIVE_PATTERNS = {
        "N4": re.compile(
            r"\b\d{3}-\d{2}-\d{4}\b|\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            re.IGNORECASE,
        ),
        "N3": re.compile(
            r"\bCONFIDENTIAL\b|\bRESTRICTED\b|\bPII\b|\bPASSPORT\b",
            re.IGNORECASE,
        ),
    }

    @classmethod
    def evaluate(cls, actor_id: str, actor_role: str, action: ActionContext) -> PolicyDecision:
        tenant_id = action.tenant_id
        ceiling = cls._ceiling(tenant_id)
        dpa = cls._dpa_status(tenant_id)

        declared = action.data_class
        source_default = cls._source_default(tenant_id, action.source)
        retrieved = [c.data_class for c in (action.retrieved_chunks or [])]
        effective = cls._max_class([declared, source_default] + retrieved)

        decision = cls._decide(effective, ceiling, dpa, mismatch=False)
        cls._record(
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            decision=decision,
            event_type="policy.gate.passed" if decision.allowed else "policy.gate.blocked",
        )
        return decision

    @classmethod
    def pre_egress(
        cls,
        actor_id: str,
        actor_role: str,
        action: ActionContext,
        output_text: str,
    ) -> PolicyDecision:
        detected = cls._scan_output(output_text)
        effective = cls._max_class([action.data_class, detected])

        if detected != action.data_class and effective in ("N3", "N4"):
            decision = PolicyDecision(
                allowed=False,
                blocked_reason="ClassificationMismatch",
                effective_classification=effective,
                requires_human_gate=True,
            )
            cls._record(
                actor_id=actor_id,
                actor_role=actor_role,
                action=action,
                decision=decision,
                event_type="policy.classification_mismatch",
            )
            return decision

        return cls.evaluate(actor_id, actor_role, action)

    @classmethod
    def _scan_output(cls, text: str) -> str:
        if not text:
            return "N0"
        for level, pattern in sorted(cls._SENSITIVE_PATTERNS.items(), key=lambda x: -DATA_CLASS_ORDER[x[0]]):
            if pattern.search(text):
                return level
        return "N0"

    @classmethod
    def _source_default(cls, tenant_id: str, source_type: str) -> str:
        try:
            default = DataClassificationDefault.objects.get(
                tenant_id=tenant_id, source_type=source_type or "unknown"
            )
            return default.default_class
        except DataClassificationDefault.DoesNotExist:
            return "N1"

    @classmethod
    def _ceiling(cls, tenant_id: str) -> str:
        try:
            return TenantPlanFeatures.objects.get(tenant_id=tenant_id).data_class_ceiling
        except TenantPlanFeatures.DoesNotExist:
            return "N1"

    @classmethod
    def _dpa_status(cls, tenant_id: str) -> str:
        try:
            return DpaStatement.objects.get(tenant_id=tenant_id).status
        except DpaStatement.DoesNotExist:
            return "missing"

    @classmethod
    def _max_class(cls, classes: list[str]) -> str:
        return max((c for c in classes if c in DATA_CLASS_ORDER), key=lambda x: DATA_CLASS_ORDER[x])

    @classmethod
    def _decide(cls, effective: str, ceiling: str, dpa: str, mismatch: bool) -> PolicyDecision:
        effective_rank = DATA_CLASS_ORDER[effective]
        ceiling_rank = DATA_CLASS_ORDER[ceiling]

        if effective in ("N3", "N4") and dpa != "signed":
            return PolicyDecision(
                allowed=False,
                blocked_reason="PlanUpgradeRequired: N3/N4 requiere DPA firmado",
                effective_classification=effective,
                requires_human_gate=True,
            )

        if effective_rank > ceiling_rank:
            return PolicyDecision(
                allowed=False,
                blocked_reason="PlanUpgradeRequired: excede ceiling del plan",
                effective_classification=effective,
                requires_human_gate=True,
            )

        return PolicyDecision(
            allowed=True,
            blocked_reason=None,
            effective_classification=effective,
            requires_human_gate=effective in ("N2", "N3", "N4"),
        )

    @classmethod
    def _record(
        cls,
        *,
        actor_id: str,
        actor_role: str,
        action: ActionContext,
        decision: PolicyDecision,
        event_type: str,
    ) -> None:
        tenant_id = action.tenant_id
        try:
            with transaction.atomic():
                from apps.core.tenant_context import clear_db_tenant, set_db_tenant

                set_db_tenant(tenant_id)
                try:
                    if not decision.allowed:
                        PolicyBlock.objects.create(
                            tenant_id=tenant_id,
                            case_id=action.case_id,
                            declared_class=action.data_class,
                            effective_class=decision.effective_classification,
                            reason=decision.blocked_reason or "blocked",
                        )

                    emit_event(
                        tenant_id=tenant_id,
                        event_type=event_type,
                        payload={
                            "case_id": action.case_id,
                            "declared_class": action.data_class,
                            "effective_class": decision.effective_classification,
                            "allowed": decision.allowed,
                            "reason": decision.blocked_reason,
                        },
                    )

                    AuditWriter.write(
                        AuditContext(
                            tenant_id=tenant_id,
                            actor_id=actor_id,
                            actor_role_at_decision=actor_role,
                        ),
                        action_id="policy.gate.decision",
                        data_class=decision.effective_classification,
                        payload={
                            "case_id": action.case_id,
                            "event_type": event_type,
                            "allowed": decision.allowed,
                            "blocked_reason": decision.blocked_reason,
                            "requires_human_gate": decision.requires_human_gate,
                        },
                        emit=False,
                    )
                finally:
                    clear_db_tenant()
        except Exception:
            # Audit/event emission must not break the gate decision itself.
            pass
