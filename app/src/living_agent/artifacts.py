"""Encrypted handoff artifacts for E4-3 agent task steps.

Artefacts are stored in the generated object store under a workspace-scoped key
and encrypted at rest with the tenant data key. Only the output_ref (object id)
travel between steps.
"""

from __future__ import annotations

from typing import Any

from ..context import Context
from ..db import create_object
from ..db_adapter import transaction
from ..storage import (
    GENERATED_BUCKET,
    ObjectStore,
    encrypt_object_payload,
    decrypt_object_payload,
    get_object_store,
    object_key,
)


ARTIFACT_MIME_TYPE = "application/json"
ARTIFACT_FILE_NAME = "step-output.json"


def save_step_artifact(
    ctx: Context,
    conn: Any,
    payload: bytes | str,
    *,
    file_name: str = ARTIFACT_FILE_NAME,
    mime_type: str = ARTIFACT_MIME_TYPE,
) -> str:
    """Persist ``payload`` as an encrypted generated object and return its id."""

    workspace_id = ctx.require_scoped_workspace()
    tenant_id = ctx.require_tenant()

    if isinstance(payload, str):
        payload_bytes = payload.encode("utf-8")
    else:
        payload_bytes = payload

    encrypted = encrypt_object_payload(ctx, payload_bytes)
    object_id = create_object(
        ctx,
        conn,
        origin="generated",
        bucket=GENERATED_BUCKET,
        object_key="",
        file_name=file_name,
        mime_type=mime_type,
        size_bytes=len(encrypted),
        sha256=None,
        source_type="agent_task_step",
        source_version="v1",
        meta={"encrypted": True, "tenant_id": tenant_id},
        object_id=None,
    )["id"]

    key = object_key(
        workspace_id=workspace_id,
        origin="generated",
        file_name=file_name,
        object_id=object_id,
        tenant_id=tenant_id,
    )

    # Update the object row with the real key once we know the id.
    with transaction(conn, ctx=ctx):
        conn.execute(
            "UPDATE object SET object_key = ? WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (key, object_id, workspace_id, tenant_id),
        )

    store = get_object_store()
    store.put_object(
        bucket=GENERATED_BUCKET,
        key=key,
        data=encrypted,
        content_type=mime_type,
    )
    return object_id


def load_step_artifact(
    ctx: Context,
    conn: Any,
    output_ref: str,
) -> bytes:
    """Load and decrypt a step artifact by object id."""

    from ..db import get_object

    workspace_id = ctx.require_scoped_workspace()
    tenant_id = ctx.require_tenant()

    obj = get_object(ctx, conn, output_ref)
    if obj is None:
        raise ValueError(f"Artifact {output_ref} not found in workspace")

    store = get_object_store()
    key = object_key(
        workspace_id=workspace_id,
        origin="generated",
        file_name=obj.get("file_name") or ARTIFACT_FILE_NAME,
        object_id=output_ref,
        tenant_id=tenant_id,
    )
    encrypted = store.get_object(bucket=GENERATED_BUCKET, key=key)
    return decrypt_object_payload(ctx, encrypted)


def load_step_artifact_text(
    ctx: Context,
    conn: Any,
    output_ref: str,
) -> str:
    """Convenience helper returning the artifact as UTF-8 text."""

    return load_step_artifact(ctx, conn, output_ref).decode("utf-8", errors="replace")
