"""Context layer for SpaceLoom SL0.

Every query that reads or writes application data receives a Context. In SL0 the
app is single-user/local-first, so tenant_id and user_id are latent fields; the
seam exists now to avoid rewriting repositories when Etapa 2-3 adds real access
enforcement.

Two scopes are intentionally explicit:

* ``system_context()``: bootstrap-only operations such as creating/listing
  workspaces. It is not a data-read escape hatch for workspace-owned rows.
* ``Context(workspace_id=...)``: scoped application access. Query helpers for
  workspace-owned tables must constrain by this ``workspace_id``.
"""

from __future__ import annotations

from dataclasses import dataclass


SYSTEM_WORKSPACE_ID = "__system__"
DEFAULT_LOCAL_USER_ID = "local"
DEFAULT_LOCAL_ACTOR_ROLE = "owner"


@dataclass(frozen=True, slots=True)
class Context:
    """Access scope and actor identity for a unit of work."""

    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None

    def require_workspace(self) -> str:
        """Return the scoped workspace id or raise for malformed context."""

        if not self.workspace_id:
            raise ValueError("Context.workspace_id is required")
        return self.workspace_id

    def require_scoped_workspace(self) -> str:
        """Return an application workspace id; reject bootstrap/system scope."""

        workspace_id = self.require_workspace()
        if workspace_id == SYSTEM_WORKSPACE_ID:
            raise ValueError("A concrete workspace Context is required for scoped data access")
        return workspace_id

    def require_system(self) -> None:
        """Assert that this context is explicitly bootstrap/system scoped."""

        if self.workspace_id != SYSTEM_WORKSPACE_ID:
            raise ValueError("A system Context is required for bootstrap workspace operations")

    @property
    def is_system(self) -> bool:
        return self.workspace_id == SYSTEM_WORKSPACE_ID

    def resolved_actor_id(self) -> str | None:
        return self.actor_id or self.user_id

    def with_workspace(self, workspace_id: str) -> "Context":
        return Context(
            workspace_id=workspace_id,
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            actor_id=self.actor_id,
            actor_role_at_decision=self.actor_role_at_decision,
        )


def system_context(
    *,
    tenant_id: str | None = None,
    user_id: str | None = DEFAULT_LOCAL_USER_ID,
    actor_id: str | None = DEFAULT_LOCAL_USER_ID,
    actor_role_at_decision: str | None = DEFAULT_LOCAL_ACTOR_ROLE,
) -> Context:
    """Bootstrap context for health, seed, and workspace listing/creation."""

    return Context(
        workspace_id=SYSTEM_WORKSPACE_ID,
        tenant_id=tenant_id,
        user_id=user_id,
        actor_id=actor_id,
        actor_role_at_decision=actor_role_at_decision,
    )
