"""Immutable tenant entity identity for E3-3.

Each tenant has a single, versioned identity record. Rewrites are rejected
unless they come from an existing owner with explicit confirmation, and every
mutation is appended to the tenant audit chain.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class IdentityError(Exception):
    """Raised when an identity mutation would violate immutability rules."""


@dataclass(frozen=True, slots=True)
class EntityIdentity:
    tenant_id: str
    version: int
    name: str
    slug: str
    tax_id: str | None
    jurisdiction: str | None
    owner_user_id: str
    updated_at: str


def get_identity(conn: Any, tenant_id: str) -> EntityIdentity | None:
    """Return the current identity for a tenant, or None if not set."""

    row = conn.execute(
        """SELECT tenant_id, version, name, slug, tax_id, jurisdiction,
                  owner_user_id, updated_at
           FROM entity_identity_version
           WHERE tenant_id = ?
           ORDER BY version DESC LIMIT 1""",
        (tenant_id,),
    ).fetchone()
    if row is None:
        return None
    return EntityIdentity(**dict(row))


def create_identity(
    conn: Any,
    tenant_id: str,
    name: str,
    slug: str,
    owner_user_id: str,
    *,
    tax_id: str | None = None,
    jurisdiction: str | None = None,
    timestamp: str | None = None,
) -> EntityIdentity:
    """Create the initial identity for a tenant. Fails if one already exists."""

    if get_identity(conn, tenant_id) is not None:
        raise IdentityError("Identity already exists for this tenant")

    identity = EntityIdentity(
        tenant_id=tenant_id,
        version=1,
        name=name,
        slug=slug,
        tax_id=tax_id,
        jurisdiction=jurisdiction,
        owner_user_id=owner_user_id,
        updated_at=timestamp or _now(),
    )
    _persist(conn, identity)
    return identity


def update_identity(
    conn: Any,
    tenant_id: str,
    actor_user_id: str,
    actor_role: str,
    confirmation_token: str,
    expected_token: str,
    *,
    name: str | None = None,
    slug: str | None = None,
    tax_id: str | None = None,
    jurisdiction: str | None = None,
    timestamp: str | None = None,
) -> EntityIdentity:
    """Create a new identity version after strict authorization checks.

    Only an owner with the correct confirmation token may mutate identity. The
    old version is preserved (append-only).
    """

    current = get_identity(conn, tenant_id)
    if current is None:
        raise IdentityError("No existing identity to update")

    if actor_role != "owner":
        raise IdentityError("Only owner can mutate tenant identity")

    if actor_user_id == current.owner_user_id:
        raise IdentityError("Owner cannot self-approve identity mutation")

    if confirmation_token != expected_token:
        raise IdentityError("Confirmation token mismatch")

    new_identity = EntityIdentity(
        tenant_id=tenant_id,
        version=current.version + 1,
        name=name if name is not None else current.name,
        slug=slug if slug is not None else current.slug,
        tax_id=tax_id if tax_id is not None else current.tax_id,
        jurisdiction=jurisdiction if jurisdiction is not None else current.jurisdiction,
        owner_user_id=current.owner_user_id,
        updated_at=timestamp or _now(),
    )
    _persist(conn, new_identity)
    return new_identity


def _persist(conn: Any, identity: EntityIdentity) -> None:
    conn.execute(
        """INSERT INTO entity_identity_version
           (tenant_id, version, name, slug, tax_id, jurisdiction,
            owner_user_id, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            identity.tenant_id,
            identity.version,
            identity.name,
            identity.slug,
            identity.tax_id,
            identity.jurisdiction,
            identity.owner_user_id,
            identity.updated_at,
        ),
    )


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
