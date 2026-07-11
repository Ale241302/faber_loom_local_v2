#!/usr/bin/env python3
"""Migrar objetos legacy `ws-{id}/...` al prefijo por tenant `t-{tenant}/ws-{id}/...`.

Bloque 8 — E3 cierre parciales. Resuelve la deuda documentada en:
- Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md §E3-2 t.6
- docs/audits/AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md §2.3
- docs/audits/AUDIT_E3_PLAN_VS_CODE_20260708.md §E3-2 #6

El script:
1. Lee filas `object` cuyo `object_key` no empiece por `t-`.
2. Resuelve `tenant_id` (object.tenant_id o workspace.tenant_id).
3. Copia el blob al nuevo key dentro del mismo bucket.
4. Actualiza `object.object_key` y `workspace_hmac` en una transacción.
5. Verifica conteos: filas migradas vs objetos listados en MinIO bajo el prefijo.

Modo dry-run por defecto; usar --execute para aplicar.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from typing import Any

# Permitir importar desde app/src estando en app/scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.src.context import Context, SYSTEM_WORKSPACE_ID
from app.src.db import (
    connect,
    transaction,
    workspace_seal_id,
)
from app.src.seal import compute_workspace_hmac_for_row
from app.src.storage import (
    GENERATED_BUCKET,
    UPLOAD_BUCKET,
    get_object_store,
    object_key,
    workspace_object_prefix,
)


MIGRATION_ACTOR = "migration_minio_prefix"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_tenant_id(
    conn: Any,
    workspace_id: str,
    object_tenant_id: str | None,
) -> str:
    if object_tenant_id:
        return object_tenant_id
    row = conn.execute(
        "SELECT tenant_id FROM workspace WHERE id = ?",
        (workspace_id,),
    ).fetchone()
    if row is None or not row["tenant_id"]:
        raise ValueError(f"Cannot resolve tenant_id for workspace {workspace_id}")
    return row["tenant_id"]


def _new_key_for_legacy(
    legacy_key: str,
    workspace_id: str,
    tenant_id: str,
) -> str:
    """Return the tenant-prefixed key for a legacy workspace-prefixed key."""

    legacy_prefix = workspace_object_prefix(workspace_id, tenant_id=None)
    new_prefix = workspace_object_prefix(workspace_id, tenant_id=tenant_id)
    if not legacy_key.startswith(legacy_prefix + "/"):
        raise ValueError(
            f"Legacy key {legacy_key!r} does not start with {legacy_prefix!r}"
        )
    suffix = legacy_key[len(legacy_prefix) + 1 :]
    return f"{new_prefix}/{suffix}"


def _recompute_hmac(
    conn: Any,
    ctx: Context,
    row: dict[str, Any],
) -> str:
    seal_id = workspace_seal_id(ctx, conn)
    hmac_row = {
        "id": row["id"],
        "workspace_id": row["workspace_id"],
        "bucket": row["bucket"],
        "object_key": row["object_key"],
        "source_version": row.get("source_version", "v1"),
    }
    return compute_workspace_hmac_for_row(seal_id, hmac_row, "object")


def _migrate_bucket(
    conn: Any,
    store: Any,
    bucket: str,
    dry_run: bool,
    delete_old: bool,
) -> dict[str, Any]:
    rows = conn.execute(
        """
        SELECT id, workspace_id, tenant_id, bucket, object_key, file_name, source_version
        FROM object
        WHERE bucket = ? AND object_key NOT LIKE 't-%'
        ORDER BY id
        """,
        (bucket,),
    ).fetchall()

    migrated = 0
    skipped = 0
    errors: list[str] = []

    for row in rows:
        row_dict = dict(row)
        try:
            tenant_id = _resolve_tenant_id(
                conn, row["workspace_id"], row["tenant_id"]
            )
            new_key = _new_key_for_legacy(
                row["object_key"], row["workspace_id"], tenant_id
            )
        except ValueError as exc:
            errors.append(f"{row['id']}: {exc}")
            continue

        if store.object_exists(bucket, new_key):
            skipped += 1
            continue

        if dry_run:
            print(f"[dry-run] {bucket}/{row['object_key']} -> {new_key}")
            migrated += 1
            continue

        try:
            store.copy_object(bucket, row["object_key"], bucket, new_key)
        except Exception as exc:
            errors.append(f"{row['id']}: copy failed: {exc}")
            continue

        ctx = Context(
            workspace_id=row["workspace_id"],
            tenant_id=tenant_id,
            user_id=MIGRATION_ACTOR,
            actor_id=MIGRATION_ACTOR,
            actor_role_at_decision="system",
        )
        row_dict["object_key"] = new_key
        row_dict["tenant_id"] = tenant_id
        try:
            new_hmac = _recompute_hmac(conn, ctx, row_dict)
        except Exception as exc:
            errors.append(f"{row['id']}: HMAC recompute failed: {exc}")
            continue

        with transaction(conn, ctx=ctx):
            conn.execute(
                """
                UPDATE object
                SET object_key = ?, tenant_id = ?, workspace_hmac = ?, updated_at = ?
                WHERE id = ? AND bucket = ? AND object_key = ?
                """,
                (
                    new_key,
                    tenant_id,
                    new_hmac,
                    _now(),
                    row["id"],
                    row["bucket"],
                    row["object_key"],
                ),
            )

        if delete_old:
            try:
                store.delete_object(bucket, row["object_key"])
            except Exception as exc:
                errors.append(f"{row['id']}: failed to delete old key: {exc}")

        migrated += 1

    return {
        "bucket": bucket,
        "legacy_rows": len(rows),
        "migrated": migrated,
        "skipped": skipped,
        "errors": errors,
    }


def _verify_bucket(conn: Any, store: Any, bucket: str) -> dict[str, Any]:
    rows = conn.execute(
        "SELECT COUNT(*) AS n FROM object WHERE bucket = ? AND object_key LIKE 't-%'",
        (bucket,),
    ).fetchone()
    db_count = int(rows["n"])

    keys = store.list_object_keys(bucket, prefix="t-")
    store_count = len(keys)

    return {
        "bucket": bucket,
        "db_tenant_prefixed": db_count,
        "store_tenant_prefixed": store_count,
        "consistent": db_count == store_count,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Migrate legacy MinIO object keys to tenant-prefixed keys."
    )
    parser.add_argument(
        "--db-path",
        default=os.getenv("FABERLOOM_DB_PATH"),
        help="Path to the FaberLoom SQLite database (default: FABERLOOM_DB_PATH env).",
    )
    parser.add_argument(
        "--buckets",
        default=f"{UPLOAD_BUCKET},{GENERATED_BUCKET}",
        help="Comma-separated list of buckets to migrate.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Apply the migration (default is dry-run).",
    )
    parser.add_argument(
        "--delete-old",
        action="store_true",
        help="Delete legacy keys after successful copy (default keeps them).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip interactive confirmation when --execute is used.",
    )
    args = parser.parse_args(argv)

    if not args.db_path:
        print("Error: --db-path or FABERLOOM_DB_PATH is required", file=sys.stderr)
        return 2

    os.environ["FABERLOOM_DB_PATH"] = args.db_path

    buckets = [b.strip() for b in args.buckets.split(",") if b.strip()]
    dry_run = not args.execute

    if not dry_run and not args.yes:
        prompt = (
            f"This will migrate objects in buckets {buckets!r}. "
            "Type 'migrate' to continue: "
        )
        if input(prompt).strip().lower() != "migrate":
            print("Aborted.")
            return 1

    conn = connect()
    store = get_object_store()

    results: list[dict[str, Any]] = []
    for bucket in buckets:
        result = _migrate_bucket(conn, store, bucket, dry_run, args.delete_old)
        results.append(result)
        print(
            f"Bucket {bucket}: legacy={result['legacy_rows']} "
            f"migrated={result['migrated']} skipped={result['skipped']} "
            f"errors={len(result['errors'])}"
        )
        for error in result["errors"]:
            print(f"  ERROR: {error}", file=sys.stderr)

    if not dry_run:
        print("\nVerification:")
        for bucket in buckets:
            verify = _verify_bucket(conn, store, bucket)
            status = "OK" if verify["consistent"] else "MISMATCH"
            print(
                f"  {bucket}: DB={verify['db_tenant_prefixed']} "
                f"Store={verify['store_tenant_prefixed']} [{status}]"
            )

    total_errors = sum(len(r["errors"]) for r in results)
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
