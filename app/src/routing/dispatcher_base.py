"""Base protocol and value objects for task dispatchers (E4-0).

Separates PLANNING from EXECUTION so that the same planner can be invoked in
``shadow`` mode (plan only, no side effects) and ``natural`` mode (plan + run).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from ..context import Context


@dataclass
class DispatchStep:
    """One step of a dispatch plan."""

    step_id: str
    capability: str
    task: str
    prompt: str
    complexity: str
    model_candidates: list[dict[str, Any]] = field(default_factory=list)
    chosen: dict[str, Any] | None = None
    reason: str = ""
    inputs_from: str | None = None
    requires_hitl: bool = False


@dataclass
class DispatchPlan:
    """A planner-produced plan with cost estimates."""

    steps: list[DispatchStep]
    est_total_cost_usd: float = 0.0
    planner_cost_usd: float = 0.0


class TaskDispatcher(Protocol):
    """Planner that turns a user request into a ``DispatchPlan`` without executing it."""

    def plan(
        self,
        ctx: Context,
        conn: Any,
        *,
        user_request: str,
        attachments: list[dict[str, Any]],
        policy: dict[str, Any],
    ) -> DispatchPlan: ...


def step_id_for_index(index: int) -> str:
    """Stable step identifier used for handoff references."""

    return f"step_{index}"
