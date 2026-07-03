"""ActionContext schema shared between classifier and D9 gate."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from apps.policy.gate import ActionContext as PolicyActionContext
from apps.policy.gate import RetrievedChunk


@dataclass
class ActionContext:
    """Internal classification decision context.

    Maps to the D9 ``PolicyActionContext`` used by M11.
    """

    tenant_id: str = ""
    case_id: str | None = None
    task_type: str = ""
    data_class: str = "N1"
    skill_id: str = ""
    agent_id: str = ""
    confidence: float = 0.0
    source: str = ""
    routing: str = "zone_4"
    sla_minutes: int = 60
    payload_normalizado: dict[str, Any] = field(default_factory=dict)
    requires_human_gate: bool = False
    retrieved_chunks: list[RetrievedChunk] = field(default_factory=list)

    def to_policy_action(self) -> PolicyActionContext:
        return PolicyActionContext(
            task_type=self.task_type,
            data_class=self.data_class,
            skill_id=self.skill_id,
            confidence=self.confidence,
            source=self.source,
            tenant_id=self.tenant_id,
            case_id=self.case_id,
            retrieved_chunks=self.retrieved_chunks,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActionContext":
        chunks = data.pop("retrieved_chunks", [])
        return cls(
            **data,
            retrieved_chunks=[RetrievedChunk(**c) for c in chunks],
        )
