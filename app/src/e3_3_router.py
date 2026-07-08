"""E3-3 REST endpoints for immutable tenant identity, key broker and config cascade.

These endpoints are mounted under ``/api`` and protected by the main JWT
middleware.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from .api import context_from_request
from .auth import get_current_user
from .config_cascade import ConfigCascadeError, resolve
from .context import Context
from .db import get_db, transaction
from .entity_identity import IdentityError, create_identity, get_identity, update_identity
from .foundation.core import connect as connect_foundation
from .key_broker import KeyBrokerError, KeyLevel, get_policy, request_access, set_policy


e3_3_router = APIRouter(prefix="/tenants", tags=["e3-3-identity-key-broker"])


def _confirmation_token(resource_id: str) -> str:
    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def _require_confirmation(resource_id: str, confirmation_token: str | None) -> None:
    expected = _confirmation_token(resource_id)
    if confirmation_token != expected:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Action requires explicit confirmation; provide confirmation_token={expected}",
        )


def _require_owner(request: Request) -> dict[str, Any]:
    user = getattr(request.state, "user", None) or {}
    role = (user.get("role") or "").lower()
    roles = {r.lower() for r in (user.get("roles") or [])}
    if role != "owner" and "owner" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required",
        )
    return user


def _user_tenant_id(user: dict[str, Any]) -> str | None:
    return user.get("tenant_id")


def _require_tenant_member(tenant_id: str, user: dict[str, Any]) -> None:
    """Fail unless the authenticated user belongs to the requested tenant.

    platform_admin is intentionally NOT granted access here: these endpoints
    expose tenant-scoped identity/key metadata and must remain tenant-bound.
    """

    user_tenant = _user_tenant_id(user)
    if user_tenant != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant mismatch",
        )


def _require_tenant_owner(tenant_id: str, user: dict[str, Any]) -> None:
    _require_tenant_member(tenant_id, user)
    role = (user.get("role") or "").lower()
    roles = {r.lower() for r in (user.get("roles") or [])}
    if role != "owner" and "owner" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner role required",
        )


def _tenant_context(request: Request, tenant_id: str) -> Context:
    user = getattr(request.state, "user", None) or {}
    return Context(
        workspace_id="system",
        tenant_id=tenant_id,
        user_id=user.get("user_id") or user.get("sub") or "local",
        actor_id=user.get("actor_id") or user.get("user_id") or user.get("sub") or "local",
        actor_role_at_decision=(user.get("role") or "owner"),
    )


# ---------------------------------------------------------------------------
# Entity identity
# ---------------------------------------------------------------------------


class IdentityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=120)
    tax_id: str | None = Field(default=None, max_length=40)
    jurisdiction: str | None = Field(default=None, max_length=80)


class IdentityUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    slug: str | None = Field(default=None, max_length=120)
    tax_id: str | None = Field(default=None, max_length=40)
    jurisdiction: str | None = Field(default=None, max_length=80)
    confirmation_token: str = Field(min_length=1, max_length=64)


@e3_3_router.get("/{tenant_id}/identity")
def read_identity(
    tenant_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Return the current immutable identity for the tenant."""

    _require_tenant_member(tenant_id, user)
    identity = get_identity(conn, tenant_id)
    if identity is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Identity not found")
    return {
        "tenant_id": identity.tenant_id,
        "version": identity.version,
        "name": identity.name,
        "slug": identity.slug,
        "tax_id": identity.tax_id,
        "jurisdiction": identity.jurisdiction,
        "owner_user_id": identity.owner_user_id,
        "updated_at": identity.updated_at,
    }


@e3_3_router.post("/{tenant_id}/identity", status_code=status.HTTP_201_CREATED)
def create_tenant_identity(
    tenant_id: str,
    body: IdentityCreate,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Create the initial immutable identity for the tenant."""

    _require_tenant_owner(tenant_id, user)
    try:
        identity = create_identity(
            conn,
            tenant_id,
            body.name,
            body.slug,
            user.get("user_id") or user.get("sub") or "local",
            tax_id=body.tax_id,
            jurisdiction=body.jurisdiction,
            actor_role=(user.get("role") or "owner").lower(),
        )
    except IdentityError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc

    return {
        "tenant_id": identity.tenant_id,
        "version": identity.version,
        "name": identity.name,
        "slug": identity.slug,
        "tax_id": identity.tax_id,
        "jurisdiction": identity.jurisdiction,
        "owner_user_id": identity.owner_user_id,
        "updated_at": identity.updated_at,
    }


@e3_3_router.post("/{tenant_id}/identity/update")
def update_tenant_identity(
    tenant_id: str,
    body: IdentityUpdate,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Append a new immutable identity version (requires confirmation token)."""

    _require_tenant_owner(tenant_id, user)
    _require_confirmation(tenant_id, body.confirmation_token)
    try:
        identity = update_identity(
            conn,
            tenant_id,
            user.get("user_id") or user.get("sub") or "local",
            (user.get("role") or "owner").lower(),
            body.confirmation_token,
            _confirmation_token(tenant_id),
            name=body.name,
            slug=body.slug,
            tax_id=body.tax_id,
            jurisdiction=body.jurisdiction,
        )
    except IdentityError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(exc)) from exc

    return {
        "tenant_id": identity.tenant_id,
        "version": identity.version,
        "name": identity.name,
        "slug": identity.slug,
        "tax_id": identity.tax_id,
        "jurisdiction": identity.jurisdiction,
        "owner_user_id": identity.owner_user_id,
        "updated_at": identity.updated_at,
    }


# ---------------------------------------------------------------------------
# Key broker
# ---------------------------------------------------------------------------


class KeyPolicyWrite(BaseModel):
    level: str = Field(min_length=1, max_length=20)
    approver_roles: list[str] | None = None
    ceo_only: bool = False
    confirmation_token: str = Field(min_length=1, max_length=64)


class KeyPolicyRead(BaseModel):
    tenant_id: str
    space_id: str
    level: str
    approver_roles: list[str]
    ceo_only: bool


class KeyAccessRequest(BaseModel):
    requested_level: str = Field(min_length=1, max_length=20)
    confirmation_token: str | None = None


@e3_3_router.get("/{tenant_id}/key-policy/{space_id}")
def read_key_policy(
    tenant_id: str,
    space_id: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> KeyPolicyRead:
    """Return the active key policy for a space."""

    _require_tenant_member(tenant_id, user)
    policy = get_policy(conn, tenant_id, space_id)
    return KeyPolicyRead(
        tenant_id=policy.tenant_id,
        space_id=policy.space_id,
        level=policy.level.value,
        approver_roles=sorted(policy.approver_roles),
        ceo_only=policy.ceo_only,
    )


@e3_3_router.put("/{tenant_id}/key-policy/{space_id}")
def write_key_policy(
    tenant_id: str,
    space_id: str,
    body: KeyPolicyWrite,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> KeyPolicyRead:
    """Set the key policy for a space (owner only, HITL confirmation)."""

    _require_tenant_owner(tenant_id, user)
    _require_confirmation(f"{tenant_id}:{space_id}", body.confirmation_token)
    try:
        level = KeyLevel(body.level.lower())
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid level: {body.level}") from exc

    policy = set_policy(
        conn,
        tenant_id,
        space_id,
        level,
        approver_roles=set(body.approver_roles) if body.approver_roles else None,
        ceo_only=body.ceo_only,
        updated_by=user.get("user_id") or user.get("sub") or "local",
    )
    return KeyPolicyRead(
        tenant_id=policy.tenant_id,
        space_id=policy.space_id,
        level=policy.level.value,
        approver_roles=sorted(policy.approver_roles),
        ceo_only=policy.ceo_only,
    )


@e3_3_router.post("/{tenant_id}/key-policy/{space_id}/access")
def request_key_access(
    tenant_id: str,
    space_id: str,
    body: KeyAccessRequest,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Request access to a key at a given level."""

    _require_tenant_member(tenant_id, user)
    try:
        level = KeyLevel(body.requested_level.lower())
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Invalid level: {body.requested_level}") from exc

    roles = {r.lower() for r in (user.get("roles") or [])}
    role = (user.get("role") or "").lower()
    if role:
        roles.add(role)

    try:
        granted = request_access(
            conn,
            tenant_id,
            space_id,
            level,
            user.get("user_id") or user.get("sub") or "local",
            roles,
            confirmation_token=body.confirmation_token,
        )
    except KeyBrokerError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, str(exc)) from exc

    return {"granted_level": granted.value}


me_router = APIRouter(prefix="/me", tags=["e3-3-config-cascade"])


class TenantSettingWrite(BaseModel):
    value: Any


class UserPreferencesWrite(BaseModel):
    preferences: dict[str, Any]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@e3_3_router.get("/{tenant_id}/settings/resolve/{key}")
def resolve_tenant_setting(
    tenant_id: str,
    key: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Resolve a setting through the user > workspace > tenant > default cascade."""

    if user.get("tenant_id") != tenant_id and user.get("role") != "platform_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tenant mismatch")
    ctx = context_from_request(request, workspace_id=None)
    try:
        value = resolve(conn, ctx, key)
    except ConfigCascadeError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return {"tenant_id": tenant_id, "key": key, "value": value}


@e3_3_router.get("/{tenant_id}/settings/{key}")
def get_tenant_setting(
    tenant_id: str,
    key: str,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Read a tenant-scoped setting from the tenant_settings table."""

    if user.get("tenant_id") != tenant_id and user.get("role") != "platform_admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tenant mismatch")
    ctx = context_from_request(request, workspace_id=None)
    with transaction(conn, ctx=ctx):
        row = conn.execute(
            "SELECT value_json FROM tenant_settings WHERE tenant_id = ? AND key = ?",
            (tenant_id, key),
        ).fetchone()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Setting {key} not found")
    return {"tenant_id": tenant_id, "key": key, "value": json.loads(row[0])}


@e3_3_router.put("/{tenant_id}/settings/{key}")
def put_tenant_setting(
    tenant_id: str,
    key: str,
    body: TenantSettingWrite,
    request: Request,
    conn: Any = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Write a tenant-scoped setting. Only the tenant owner may mutate settings."""

    if user.get("tenant_id") != tenant_id or user.get("role") != "owner":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only tenant owner can update settings")
    ctx = context_from_request(request, workspace_id=None)
    value_json = json.dumps(body.value, ensure_ascii=False, sort_keys=True)
    with transaction(conn, ctx=ctx):
        conn.execute(
            """
            INSERT INTO tenant_settings (tenant_id, key, value_json, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(tenant_id, key) DO UPDATE SET
                value_json = excluded.value_json,
                updated_at = excluded.updated_at
            """,
            (tenant_id, key, value_json, _utc_now()),
        )
    return {"tenant_id": tenant_id, "key": key, "value": body.value}


@me_router.get("/preferences")
def get_user_preferences(
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Read the authenticated user's preferences from Foundation."""

    user_id = user.get("user_id") or user.get("sub") or "local"
    with connect_foundation() as conn:
        row = conn.execute(
            "SELECT preferences_json FROM fnd_users WHERE id = ?",
            (user_id,),
        ).fetchone()
    if not row or row[0] is None:
        return {"user_id": user_id, "preferences": {}}
    return {"user_id": user_id, "preferences": json.loads(row[0])}


@me_router.put("/preferences")
def put_user_preferences(
    body: UserPreferencesWrite,
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """Write the authenticated user's preferences to Foundation."""

    user_id = user.get("user_id") or user.get("sub") or "local"
    prefs_json = json.dumps(body.preferences, ensure_ascii=False, sort_keys=True)
    with connect_foundation() as conn:
        conn.execute(
            "UPDATE fnd_users SET preferences_json = ? WHERE id = ?",
            (prefs_json, user_id),
        )
        conn.commit()
    return {"user_id": user_id, "preferences": body.preferences}
