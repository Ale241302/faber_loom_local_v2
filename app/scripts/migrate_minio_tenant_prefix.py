#!/usr/bin/env python3
"""Migrar objetos MinIO al nuevo prefijo explícito por tenant.

Nuevo layout: ``tenant/<tenant_id>/ws-<workspace_id>/<origin>/<object_id>/<file_name>``.

Soporta paths antiguos:
- ``tenant/<tenant>/ws-<ws>/...``  -> ya migrado, se salta.
- ``t-<tenant>/ws-<ws>/...``       -> extrae tenant y workspace del path.
- ``ws-<ws>/...``                  -> extrae workspace y resuelve tenant desde DB.
- paths sin estructura             -> resuelve por file_name + bucket + size; si
  no se encuentra, se reporta como huérfano.

Modo dry-run por defecto; usar ``--execute`` para aplicar. Los objetos originales
nunca se borran: tras actualizar la DB se mueven a ``_quarantine/<old_key>``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field, replace as dataclass_replace
from datetime import datetime, timezone
from typing import Any

# Permitir importar app.* al ejecutar el script directamente desde app/scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from app.src.storage import (  # type: ignore[import-untyped]
    GENERATED_BUCKET,
    UPLOAD_BUCKET,
    ObjectStore,
)

MIGRATION_ACTOR = "migration_minio_tenant_prefix"


# ---------------------------------------------------------------------------
# Estructuras y helpers
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class MigrationItem:
    old_key: str
    new_key: str | None = None
    bucket: str = ""
    tenant_id: str | None = None
    workspace_id: str | None = None
    object_id: str | None = None
    origin: str | None = None
    file_name: str | None = None
    status: str = "planned"
    error: str | None = None


@dataclass
class MigrationReport:
    started_at: str = field(default_factory=_now)
    ended_at: str | None = None
    tenants: list[str] = field(default_factory=list)
    buckets: list[str] = field(default_factory=list)
    dry_run: bool = True
    total_objects: int = 0
    migrated: int = 0
    skipped_already_migrated: int = 0
    orphans: int = 0
    failed: int = 0
    objects: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "tenants": self.tenants,
            "buckets": self.buckets,
            "dry_run": self.dry_run,
            "total_objects": self.total_objects,
            "migrated": self.migrated,
            "skipped_already_migrated": self.skipped_already_migrated,
            "orphans": self.orphans,
            "failed": self.failed,
            "objects": self.objects,
        }


# ---------------------------------------------------------------------------
# Conexiones
# ---------------------------------------------------------------------------


def _configure_db_env(args: argparse.Namespace) -> None:
    """Configurar variables de entorno antes de importar db_adapter."""

    engine = os.getenv("FABERLOOM_DB_ENGINE", "sqlite").lower()
    use_postgres = (
        engine == "postgres"
        or args.postgres
        or args.postgres_url is not None
        or os.getenv("FABERLOOM_POSTGRES_URL")
        or os.getenv("DATABASE_URL")
    )
    if use_postgres:
        os.environ["FABERLOOM_DB_ENGINE"] = "postgres"
        url = (
            args.postgres_url
            or os.getenv("FABERLOOM_POSTGRES_URL")
            or os.getenv("DATABASE_URL")
        )
        if url:
            os.environ["FABERLOOM_POSTGRES_URL"] = url
    elif args.db_path:
        os.environ["FABERLOOM_DB_PATH"] = args.db_path


def _create_store(args: argparse.Namespace) -> ObjectStore:
    """Crear el ObjectStore respetando FL_STORAGE_BACKEND (memory/minio)."""

    backend = os.getenv("FL_STORAGE_BACKEND", "minio").lower()
    if backend == "minio":
        for name in ("FL_MINIO_ENDPOINT", "FL_MINIO_ACCESS_KEY", "FL_MINIO_SECRET_KEY"):
            if not os.getenv(name):
                raise RuntimeError(f"Missing MinIO environment variable: {name}")
    return ObjectStore(backend=backend)


def _stat_object(store: ObjectStore, bucket: str, key: str) -> dict[str, Any]:
    """Devolver {size, etag} para un objeto en MinIO/memory."""

    backend = getattr(store, "_backend", None)
    backend_name = type(backend).__name__ if backend else "unknown"

    if backend_name == "_MemoryStoreBackend":
        data = store.get_object(bucket, key)
        return {"size": len(data), "etag": _sha256_bytes(data)}

    client = getattr(backend, "_client", None)
    if client is None:
        raise RuntimeError("No MinIO client available for stat_object")

    stat = client.stat_object(bucket, key)
    return {"size": stat.size, "etag": stat.etag}


# ---------------------------------------------------------------------------
# Resolución de paths y DB
# ---------------------------------------------------------------------------


def _bucket_to_origin(bucket: str) -> str:
    if bucket == UPLOAD_BUCKET:
        return "upload"
    if bucket == GENERATED_BUCKET:
        return "generated"
    return "unknown"


def _resolve_tenant_for_workspace(conn: Any, workspace_id: str) -> str | None:
    """Resolver tenant_id más frecuente para un workspace; None si es ambiguo."""

    rows = conn.execute(
        """
        SELECT tenant_id, COUNT(*) AS n
        FROM object
        WHERE workspace_id = ? AND tenant_id IS NOT NULL
        GROUP BY tenant_id
        ORDER BY n DESC
        """,
        (workspace_id,),
    ).fetchall()

    if rows:
        top = rows[0]
        if len(rows) > 1 and rows[1]["n"] == top["n"]:
            return None
        return top["tenant_id"]

    # Fallback a tabla workspace
    row = conn.execute(
        "SELECT tenant_id FROM workspace WHERE id = ?",
        (workspace_id,),
    ).fetchone()
    if row and row["tenant_id"]:
        return row["tenant_id"]
    return None


def _find_object_row(
    conn: Any,
    old_key: str,
    object_id: str | None,
    file_name: str | None,
    bucket: str,
    size: int | None,
) -> dict[str, Any] | None:
    """Buscar fila object por object_key, id o file_name+bucket+size."""

    row = conn.execute(
        "SELECT * FROM object WHERE object_key = ? AND bucket = ?",
        (old_key, bucket),
    ).fetchone()
    if row:
        return dict(row)

    if object_id:
        row = conn.execute("SELECT * FROM object WHERE id = ?", (object_id,)).fetchone()
        if row:
            return dict(row)

    if file_name and size is not None:
        row = conn.execute(
            """
            SELECT * FROM object
            WHERE file_name = ? AND bucket = ? AND size_bytes = ?
            LIMIT 1
            """,
            (file_name, bucket, size),
        ).fetchone()
        if row:
            return dict(row)

    return None


def _parse_object_key(
    old_key: str,
    bucket: str,
    conn: Any,
    store: ObjectStore,
) -> MigrationItem:
    """Parsear key antigua y resolver tenant/workspace/object_id vía DB."""

    if not old_key or old_key.endswith("/"):
        return MigrationItem(
            old_key=old_key,
            bucket=bucket,
            status="failed",
            error="empty or directory-like key",
        )

    if old_key.startswith("_quarantine/"):
        return MigrationItem(
            old_key=old_key,
            bucket=bucket,
            status="skipped_already_migrated",
            error=None,
        )

    parts = old_key.split("/")

    # Ya migrado
    if parts[0] == "tenant":
        return MigrationItem(
            old_key=old_key,
            bucket=bucket,
            status="skipped_already_migrated",
            error=None,
        )

    tenant_id: str | None = None
    workspace_id: str | None = None
    origin: str | None = None
    object_id: str | None = None
    file_name = parts[-1]

    # t-<tenant>/ws-<workspace>/...
    if parts[0].startswith("t-") and len(parts) >= 2 and parts[1].startswith("ws-"):
        tenant_id = parts[0][2:]
        workspace_id = parts[1][3:]
        if len(parts) >= 3:
            origin = parts[2]
        if len(parts) >= 4:
            object_id = parts[3]

    # ws-<workspace>/...
    elif parts[0].startswith("ws-"):
        workspace_id = parts[0][3:]
        tenant_id = _resolve_tenant_for_workspace(conn, workspace_id)
        if tenant_id is None:
            return MigrationItem(
                old_key=old_key,
                bucket=bucket,
                workspace_id=workspace_id,
                status="failed",
                error=f"cannot resolve unambiguous tenant_id for workspace {workspace_id}",
            )
        if len(parts) >= 2:
            origin = parts[1]
        if len(parts) >= 3:
            object_id = parts[2]

    # Sin estructura reconocible: resolver por file_name + bucket + size
    else:
        try:
            stat = _stat_object(store, bucket, old_key)
        except Exception as exc:
            return MigrationItem(
                old_key=old_key,
                bucket=bucket,
                status="failed",
                error=f"cannot stat object: {exc}",
            )

        row = _find_object_row(conn, old_key, None, file_name, bucket, stat["size"])
        if row is None:
            return MigrationItem(
                old_key=old_key,
                bucket=bucket,
                file_name=file_name,
                status="orphan",
                error="no matching DB row by file_name/bucket/size",
            )
        workspace_id = row["workspace_id"]
        tenant_id = row.get("tenant_id") or _resolve_tenant_for_workspace(conn, workspace_id)
        origin = row.get("origin") or _bucket_to_origin(bucket)
        object_id = row["id"]

    if not origin:
        origin = _bucket_to_origin(bucket)

    if not workspace_id:
        return MigrationItem(
            old_key=old_key,
            bucket=bucket,
            status="failed",
            error="workspace_id could not be determined",
        )

    if not tenant_id:
        return MigrationItem(
            old_key=old_key,
            bucket=bucket,
            workspace_id=workspace_id,
            status="failed",
            error="tenant_id could not be determined",
        )

    if not object_id:
        return MigrationItem(
            old_key=old_key,
            bucket=bucket,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            status="failed",
            error="object_id could not be determined from path",
        )

    # Verificar/confirmar con fila DB para paths estructurados
    row = _find_object_row(conn, old_key, object_id, file_name, bucket, None)
    if row is not None:
        if row["workspace_id"] != workspace_id:
            return MigrationItem(
                old_key=old_key,
                bucket=bucket,
                status="failed",
                error=(
                    f"workspace mismatch: path={workspace_id} "
                    f"db={row['workspace_id']}"
                ),
            )
        db_tenant = row.get("tenant_id")
        if db_tenant and db_tenant != tenant_id:
            return MigrationItem(
                old_key=old_key,
                bucket=bucket,
                status="failed",
                error=(
                    f"tenant mismatch: path={tenant_id} db={db_tenant}"
                ),
            )
        # Si la DB tenía origen, preferirlo
        if row.get("origin"):
            origin = row["origin"]
    # Si no hay fila DB para path estructurado, fallamos fail-closed
    elif parts[0].startswith("t-") or parts[0].startswith("ws-"):
        return MigrationItem(
            old_key=old_key,
            bucket=bucket,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            object_id=object_id,
            status="failed",
            error="no matching DB row for structured path",
        )

    safe_name = os.path.basename(file_name or "object")
    new_key = f"tenant/{tenant_id}/ws-{workspace_id}/{origin}/{object_id}/{safe_name}"

    return MigrationItem(
        old_key=old_key,
        new_key=new_key,
        bucket=bucket,
        tenant_id=tenant_id,
        workspace_id=workspace_id,
        object_id=object_id,
        origin=origin,
        file_name=safe_name,
        status="planned",
        error=None,
    )


# ---------------------------------------------------------------------------
# Ejecución de la migración por objeto
# ---------------------------------------------------------------------------


def _execute_item(
    conn: Any,
    store: ObjectStore,
    item: MigrationItem,
) -> MigrationItem:
    """Copiar, verificar, actualizar DB y cuarentenar un objeto."""

    assert item.new_key is not None
    assert item.tenant_id is not None
    assert item.workspace_id is not None
    assert item.object_id is not None

    old_key = item.old_key
    new_key = item.new_key
    bucket = item.bucket

    # 1. Si el destino ya existe, no sobreescribimos; verificamos.
    if store.object_exists(bucket, new_key):
        try:
            src_stat = _stat_object(store, bucket, old_key)
            dst_stat = _stat_object(store, bucket, new_key)
            if src_stat["size"] != dst_stat["size"] or src_stat.get("etag") != dst_stat.get("etag"):
                return dataclass_replace(
                    item,
                    status="failed",
                    error="destination exists with different size/etag",
                )
        except Exception as exc:
            return dataclass_replace(
                item,
                status="failed",
                error=f"destination exists and verification failed: {exc}",
            )
    else:
        # copy -> verify
        try:
            store.copy_object(bucket, old_key, bucket, new_key)
            src_stat = _stat_object(store, bucket, old_key)
            dst_stat = _stat_object(store, bucket, new_key)
            if src_stat["size"] != dst_stat["size"]:
                raise RuntimeError(
                    f"size mismatch: src={src_stat['size']} dst={dst_stat['size']}"
                )
        except Exception as exc:
            # Limpiar copia parcial si quedó
            try:
                if store.object_exists(bucket, new_key):
                    store.delete_object(bucket, new_key)
            except Exception:
                pass
            return dataclass_replace(item, status="failed", error=f"copy/verify failed: {exc}")

    # 2. Actualizar DB con commit explícito y WHERE fail-closed
    from app.src.context import Context
    from app.src.db_adapter import transaction

    ctx = Context(
        workspace_id=item.workspace_id,
        tenant_id=item.tenant_id,
        user_id=MIGRATION_ACTOR,
        actor_id=MIGRATION_ACTOR,
        actor_role_at_decision="system",
    )
    try:
        with transaction(conn, ctx=ctx):
            cur = conn.execute(
                """
                UPDATE object
                SET object_key = ?, tenant_id = ?, updated_at = ?
                WHERE id = ?
                  AND workspace_id = ?
                  AND bucket = ?
                  AND object_key = ?
                  AND (tenant_id = ? OR tenant_id IS NULL)
                """,
                (
                    new_key,
                    item.tenant_id,
                    _now(),
                    item.object_id,
                    item.workspace_id,
                    bucket,
                    old_key,
                    item.tenant_id,
                ),
            )
            if cur.rowcount != 1:
                raise RuntimeError(f"expected 1 row updated, got {cur.rowcount}")
    except Exception as exc:
        # Limpiar copia nueva
        try:
            store.delete_object(bucket, new_key)
        except Exception:
            pass
        return dataclass_replace(item, status="failed", error=f"database update failed: {exc}")

    # 3. Mover original a _quarantine (copiar + borrar)
    quarantine_key = f"_quarantine/{old_key}"
    try:
        store.copy_object(bucket, old_key, bucket, quarantine_key)
        store.delete_object(bucket, old_key)
    except Exception as exc:
        return dataclass_replace(
            item,
            status="migrated",
            error=f"migrated but quarantine failed: {exc}",
        )

    return dataclass_replace(item, status="migrated", error=None)


# ---------------------------------------------------------------------------
# Orquestación principal
# ---------------------------------------------------------------------------


def run_migration(
    conn: Any,
    store: ObjectStore,
    *,
    tenant: str | None = None,
    buckets: list[str] | None = None,
    dry_run: bool = True,
    report_path: str | None = None,
) -> dict[str, Any]:
    """Correr la migración y devolver el reporte como dict."""

    buckets = buckets or [UPLOAD_BUCKET, GENERATED_BUCKET]
    report = MigrationReport(buckets=buckets, dry_run=dry_run)
    tenants_seen: set[str] = set()

    for bucket in buckets:
        keys = store.list_object_keys(bucket, prefix="")
        for old_key in keys:
            item = _parse_object_key(old_key, bucket, conn, store)
            report.total_objects += 1

            if tenant is not None and item.tenant_id != tenant:
                item = dataclass_replace(item, status="filtered")

            if item.status == "planned":
                if dry_run:
                    pass  # status stays planned
                else:
                    item = _execute_item(conn, store, item)

            if item.status == "migrated":
                report.migrated += 1
                if item.tenant_id:
                    tenants_seen.add(item.tenant_id)
            elif item.status == "skipped_already_migrated":
                report.skipped_already_migrated += 1
                if item.tenant_id:
                    tenants_seen.add(item.tenant_id)
            elif item.status == "orphan":
                report.orphans += 1
            elif item.status == "failed":
                report.failed += 1

            report.objects.append(
                {
                    "old_key": item.old_key,
                    "new_key": item.new_key,
                    "bucket": item.bucket,
                    "tenant_id": item.tenant_id,
                    "workspace_id": item.workspace_id,
                    "object_id": item.object_id,
                    "status": item.status,
                    "error": item.error,
                }
            )

    report.tenants = sorted(tenants_seen) if tenants_seen else ([tenant] if tenant else [])
    report.ended_at = _now()

    if dry_run:
        print(f"[dry-run] {report.total_objects} objects scanned")
        for obj in report.objects:
            print(
                f"  {obj['status']:30} {obj['old_key']!r} -> {obj['new_key']!r}"
            )
    else:
        print(
            f"[execute] total={report.total_objects} migrated={report.migrated} "
            f"skipped={report.skipped_already_migrated} orphans={report.orphans} "
            f"failed={report.failed}"
        )
        for obj in report.objects:
            if obj["status"] in ("failed", "orphan"):
                print(f"  {obj['status']:30} {obj['old_key']!r} {obj['error']}")

    if report_path:
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report.to_dict(), fh, indent=2, ensure_ascii=False)

    return report.to_dict()


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Migrate MinIO object keys to the explicit tenant/<tenant>/ws-<ws>/ layout."
    )
    parser.add_argument(
        "--tenant",
        default=None,
        help="Only migrate objects for this tenant_id (default: all tenants).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show migration plan without making changes (default).",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=False,
        help="Actually perform the migration.",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Path to write the JSON migration report.",
    )
    parser.add_argument(
        "--buckets",
        default=f"{UPLOAD_BUCKET},{GENERATED_BUCKET}",
        help="Comma-separated list of buckets to migrate.",
    )
    parser.add_argument(
        "--db-path",
        default=os.getenv("FABERLOOM_DB_PATH"),
        help="SQLite database path (default: FABERLOOM_DB_PATH env).",
    )
    parser.add_argument(
        "--postgres",
        action="store_true",
        help="Use Postgres via FABERLOOM_POSTGRES_URL or DATABASE_URL.",
    )
    parser.add_argument(
        "--postgres-url",
        default=None,
        help="Postgres connection URL (overrides env).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_argparser()
    args = parser.parse_args(argv)

    dry_run = args.dry_run and not args.execute

    _configure_db_env(args)

    # Importar db_adapter DESPUÉS de configurar env
    from app.src import db_adapter

    conn = db_adapter.connect()
    try:
        store = _create_store(args)
        buckets = [b.strip() for b in args.buckets.split(",") if b.strip()]
        report = run_migration(
            conn,
            store,
            tenant=args.tenant,
            buckets=buckets,
            dry_run=dry_run,
            report_path=args.report,
        )
    finally:
        conn.close()

    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
