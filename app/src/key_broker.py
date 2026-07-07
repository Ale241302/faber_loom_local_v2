"""Graduated key broker for E3-3.

Each logical space (workspace, memory domain, object class) can have a key at
one of three graduation levels:

- closed: no key is exposed; operations requiring decryption are rejected.
- index: a blinded/index key allows search/matching without revealing content.
- content: the full content key is available for decryption.

The broker mediates access: it never hands the raw key to an agent; it only
returns a capability (level) after checking the caller's role and an explicit
HITL approval when crossing to ``content``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class KeyLevel(str, Enum):
    CLOSED = "closed"
    INDEX = "index"
    CONTENT = "content"


class KeyBrokerError(Exception):
    """Raised when a key access request is denied."""


@dataclass(frozen=True, slots=True)
class KeyPolicy:
    tenant_id: str
    space_id: str
    level: KeyLevel
    approver_roles: frozenset[str]
    ceo_only: bool = False


DEFAULT_APPROVER_ROLES = frozenset({"owner", "ceo"})


def get_policy(conn: Any, tenant_id: str, space_id: str) -> KeyPolicy:
    """Return the active key policy for a space, defaulting to CLOSED/owner+ceo."""

    row = conn.execute(
        """SELECT level, approver_roles_json, ceo_only
           FROM key_policy
           WHERE tenant_id = ? AND space_id = ?""",
        (tenant_id, space_id),
    ).fetchone()
    if row is None:
        return KeyPolicy(
            tenant_id=tenant_id,
            space_id=space_id,
            level=KeyLevel.CLOSED,
            approver_roles=DEFAULT_APPROVER_ROLES,
        )

    import json

    roles = frozenset(json.loads(row["approver_roles_json"] or "[]"))
    return KeyPolicy(
        tenant_id=tenant_id,
        space_id=space_id,
        level=KeyLevel(row["level"]),
        approver_roles=roles or DEFAULT_APPROVER_ROLES,
        ceo_only=bool(row["ceo_only"]),
    )


def set_policy(
    conn: Any,
    tenant_id: str,
    space_id: str,
    level: KeyLevel,
    *,
    approver_roles: set[str] | None = None,
    ceo_only: bool = False,
) -> KeyPolicy:
    """Set a key policy. Existing policies are overwritten."""

    import json

    roles = frozenset(approver_roles) if approver_roles else DEFAULT_APPROVER_ROLES
    conn.execute(
        """INSERT INTO key_policy (tenant_id, space_id, level, approver_roles_json, ceo_only)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(tenant_id, space_id) DO UPDATE SET
               level = excluded.level,
               approver_roles_json = excluded.approver_roles_json,
               ceo_only = excluded.ceo_only""",
        (tenant_id, space_id, level.value, json.dumps(sorted(roles)), int(ceo_only)),
    )
    return KeyPolicy(
        tenant_id=tenant_id,
        space_id=space_id,
        level=level,
        approver_roles=roles,
        ceo_only=ceo_only,
    )


def request_access(
    conn: Any,
    tenant_id: str,
    space_id: str,
    requested_level: KeyLevel,
    user_id: str,
    user_roles: set[str],
    confirmation_token: str | None = None,
) -> KeyLevel:
    """Return the granted access level for a space.

    Access is never upgraded without an explicit confirmation token when crossing
    to ``content``. CEO-only policies require the ``ceo`` role regardless of token.
    """

    policy = get_policy(conn, tenant_id, space_id)

    if policy.ceo_only and "ceo" not in user_roles:
        raise KeyBrokerError("This space is CEO-only")

    if requested_level == KeyLevel.CONTENT:
        if "content" not in {l.value for l in _allowed_levels(policy, user_roles)}:
            raise KeyBrokerError("Content access not allowed for this user")
        if confirmation_token is None:
            raise KeyBrokerError("Content access requires explicit confirmation token")

    granted = _min_level(policy.level, requested_level)
    if granted.value < requested_level.value:
        raise KeyBrokerError(f"Access denied: space is {policy.level.value}, requested {requested_level.value}")

    return granted


def _allowed_levels(policy: KeyPolicy, user_roles: set[str]) -> set[KeyLevel]:
    if not user_roles & policy.approver_roles:
        return {KeyLevel.CLOSED}
    return {KeyLevel.CLOSED, KeyLevel.INDEX, KeyLevel.CONTENT}


def _min_level(a: KeyLevel, b: KeyLevel) -> KeyLevel:
    order = {KeyLevel.CLOSED: 0, KeyLevel.INDEX: 1, KeyLevel.CONTENT: 2}
    return a if order[a] <= order[b] else b
