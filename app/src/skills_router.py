"""E3-6 golden-case harvester REST endpoints."""

from __future__ import annotations

import hashlib
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from .api import context_from_request
from .auth import get_current_user
from .context import SYSTEM_WORKSPACE_ID, Context
from .db import ensure_system_workspace, get_db, transaction


def _raise_golden_error(exc: ValueError) -> None:
    message = str(exc)
    if "not found" in message.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=message
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=message
    ) from exc
from .golden_harvester import (
    approve_golden_case,
    list_golden_cases,
    propose_golden_case_from_run,
    verify_golden_case,
)
from .models import GoldenCaseRead


skills_router = APIRouter(prefix="/tenants", tags=["skills"])


def _confirmation_token(resource_id: str) -> str:
    """Deterministic token the UI must echo for destructive actions."""
    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def _require_confirmation(resource_id: str, confirmation_token: str | None) -> None:
    expected = _confirmation_token(resource_id)
    if confirmation_token != expected:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Action requires explicit confirmation; provide confirmation_token={expected}",
        )


def _require_tenant_admin(tenant_id: str, user: dict[str, Any]) -> None:
    """Fail unless the user is owner/admin of the tenant or platform_admin."""

    user_tenant = user.get("tenant_id")
    role = (user.get("role") or "").lower()
    roles = {r.lower() for r in (user.get("roles") or [])}
    is_platform_admin = role == "platform_admin" or "platform_admin" in roles
    is_tenant_admin = user_tenant == tenant_id and (
        role in {"owner", "admin"} or {"owner", "admin"} & roles
    )
    if not (is_platform_admin or is_tenant_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner/admin role required for this tenant",
        )


def _tenant_context(request: Request, tenant_id: str) -> Context:
    user = getattr(request.state, "user", None) or {}
    return Context(
        workspace_id=SYSTEM_WORKSPACE_ID,
        tenant_id=tenant_id,
        user_id=user.get("user_id") or user.get("sub") or "local",
        actor_id=user.get("actor_id") or user.get("user_id") or user.get("sub") or "local",
        actor_role_at_decision=(user.get("role") or "owner"),
    )


class ProposeGoldenCaseRequest(BaseModel):
    run_id: str = Field(..., min_length=1)


class ApproveGoldenCaseRequest(BaseModel):
    confirmation_token: str = Field(..., min_length=1)


@skills_router.post("/{tenant_id}/skills/{skill_id}/golden-cases/propose")
def propose_golden_case_endpoint(
    tenant_id: str,
    skill_id: str,
    request: Request,
    body: ProposeGoldenCaseRequest,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> GoldenCaseRead:
    """Freeze a real routine run as a candidate golden case."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)

    with transaction(conn, ctx=ctx):
        ensure_system_workspace(conn, ctx.tenant_id)
        case = propose_golden_case_from_run(
            ctx,
            conn,
            run_id=body.run_id,
            skill_id=skill_id,
        )

    return GoldenCaseRead(**case)


@skills_router.get("/{tenant_id}/golden-cases")
def list_golden_cases_endpoint(
    tenant_id: str,
    request: Request,
    skill_id: str | None = None,
    state: str | None = Query(None, pattern="^(candidate|approved|verified|all)$"),
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, list[GoldenCaseRead]]:
    """List golden cases for the tenant, optionally filtered by skill or state."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)

    with transaction(conn, ctx=ctx):
        ensure_system_workspace(conn, ctx.tenant_id)
        cases = list_golden_cases(
            ctx,
            conn,
            skill_id=skill_id,
            state=state if state != "all" else None,
        )
    return {"golden_cases": [GoldenCaseRead(**case) for case in cases]}


@skills_router.post("/{tenant_id}/golden-cases/{case_id}/approve")
def approve_golden_case_endpoint(
    tenant_id: str,
    case_id: str,
    request: Request,
    body: ApproveGoldenCaseRequest,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> GoldenCaseRead:
    """Curator approval (first gate). Requires explicit confirmation token."""

    _require_tenant_admin(tenant_id, user)
    _require_confirmation(case_id, body.confirmation_token)
    ctx = _tenant_context(request, tenant_id)

    user_id = user.get("user_id") or user.get("sub") or "local"
    with transaction(conn, ctx=ctx):
        ensure_system_workspace(conn, ctx.tenant_id)
        try:
            case = approve_golden_case(ctx, conn, case_id=case_id, approved_by=user_id)
        except ValueError as exc:
            _raise_golden_error(exc)

    return GoldenCaseRead(**case)


@skills_router.post("/{tenant_id}/golden-cases/{case_id}/verify")
def verify_golden_case_endpoint(
    tenant_id: str,
    case_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> GoldenCaseRead:
    """Independent verification (second gate). Verifier must differ from approver."""

    _require_tenant_admin(tenant_id, user)
    ctx = _tenant_context(request, tenant_id)

    user_id = user.get("user_id") or user.get("sub") or "local"
    with transaction(conn, ctx=ctx):
        ensure_system_workspace(conn, ctx.tenant_id)
        try:
            case = verify_golden_case(ctx, conn, case_id=case_id, verified_by=user_id)
        except ValueError as exc:
            _raise_golden_error(exc)

    return GoldenCaseRead(**case)
