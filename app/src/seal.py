"""Workspace-level HMAC seal.

Every workspace owns a unique ``seal_id`` generated at creation time. Sensitive
rows (kb_source, kb_fact, draft, routine_run) carry a ``workspace_hmac`` computed
with that seal. The signed payload now includes a canonical JSON representation of
the protected columns, so the HMAC detects content tampering as well as
workspace-id drift.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


# Columns that participate in the content HMAC for each sealed table.
_PROTECTED_COLUMNS: dict[str, tuple[str, ...]] = {
    "kb_source": (
        "id",
        "workspace_id",
        "type",
        "title",
        "source_version",
    ),
    "kb_fact": (
        "id",
        "workspace_id",
        "source_id",
        "entity_key",
        "field_name",
        "field_value",
        "source_version",
    ),
    "draft": (
        "id",
        "workspace_id",
        "task",
        "subject",
        "body_md",
        "status",
        "source_version",
    ),
    "routine_run": (
        "id",
        "workspace_id",
        "routine_id",
        "input_json",
        "output_json",
        "status",
        "source_version",
    ),
}


def _canonical_json(payload: dict[str, Any]) -> str:
    """Return a stable, compact JSON representation for signing."""

    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def _row_payload(row: dict[str, Any], table_name: str) -> dict[str, Any]:
    """Build the canonical protected payload from a row dict."""

    columns = _PROTECTED_COLUMNS.get(table_name, ())
    return {col: row.get(col) for col in columns if col in row}


def compute_workspace_hmac(
    seal_id: str,
    row_id: str,
    workspace_id: str,
    payload: dict[str, Any] | None = None,
) -> str:
    """Return the HMAC-SHA256 hex signature for a workspace-owned row.

    If ``payload`` is provided, the canonical JSON of the payload is included in
    the signed message, making the seal tamper-evident for content changes.
    """

    parts = [workspace_id, row_id]
    if payload is not None:
        parts.append(_canonical_json(payload))
    msg = "|".join(parts).encode("utf-8")
    return hmac.new(
        key=seal_id.encode("utf-8"),
        msg=msg,
        digestmod=hashlib.sha256,
    ).hexdigest()


def compute_workspace_hmac_for_row(
    seal_id: str,
    row: dict[str, Any],
    table_name: str,
) -> str:
    """Compute the content-aware HMAC for a row from one of the sealed tables."""

    payload = _row_payload(row, table_name)
    return compute_workspace_hmac(seal_id, row["id"], row["workspace_id"], payload)


def verify_workspace_hmac(
    seal_id: str,
    row_id: str,
    workspace_id: str,
    hmac_value: str | None,
    payload: dict[str, Any] | None = None,
) -> bool:
    """Constant-time HMAC verification.

    Accepts the legacy row-id-only signature as a fallback so existing rows can
    be migrated to content-aware signatures without being rejected.
    """

    if not hmac_value:
        return False
    expected = compute_workspace_hmac(seal_id, row_id, workspace_id, payload)
    if hmac.compare_digest(expected, hmac_value):
        return True
    # Backwards-compatible fallback for rows sealed before v9.
    legacy_expected = compute_workspace_hmac(seal_id, row_id, workspace_id)
    return hmac.compare_digest(legacy_expected, hmac_value)


def verify_workspace_hmac_for_row(
    seal_id: str,
    row: dict[str, Any],
    table_name: str,
) -> bool:
    """Verify the HMAC of a row using its protected-column payload."""

    payload = _row_payload(row, table_name)
    return verify_workspace_hmac(
        seal_id,
        row["id"],
        row["workspace_id"],
        row.get("workspace_hmac"),
        payload,
    )


def assert_workspace_hmac(
    seal_id: str,
    row_id: str,
    workspace_id: str,
    hmac_value: str | None,
    payload: dict[str, Any] | None = None,
) -> None:
    """Raise ``PermissionError`` if the row's workspace HMAC does not match."""

    if not verify_workspace_hmac(seal_id, row_id, workspace_id, hmac_value, payload):
        raise PermissionError("Workspace HMAC verification failed")


def assert_workspace_hmac_for_row(
    seal_id: str,
    row: dict[str, Any],
    table_name: str,
) -> None:
    """Assert the HMAC of a row using its protected-column payload."""

    payload = _row_payload(row, table_name)
    assert_workspace_hmac(seal_id, row["id"], row["workspace_id"], row.get("workspace_hmac"), payload)
