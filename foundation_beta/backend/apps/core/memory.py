"""Letta namespace builder enforcing tenant-scoped memory."""
from __future__ import annotations

import re
from uuid import UUID

SAFE_KIND_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


def letta_namespace(
    tenant_id: UUID,
    agent_id: str,
    task_id: str | None = None,
    kind: str = "working",
) -> str:
    """Build a tenant-scoped Letta memory namespace."""
    if not SAFE_KIND_RE.match(agent_id):
        raise ValueError(f"Invalid agent_id: {agent_id}")
    if task_id is not None and not SAFE_KIND_RE.match(task_id):
        raise ValueError(f"Invalid task_id: {task_id}")
    if not SAFE_KIND_RE.match(kind):
        raise ValueError(f"Invalid kind: {kind}")

    parts = ["mem", "tenant", str(tenant_id), "agent", agent_id]
    if task_id:
        parts += ["task", task_id]
    parts += [kind]
    return ":".join(parts)
