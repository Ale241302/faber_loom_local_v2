#!/usr/bin/env python3
"""Carga masiva de fuentes KB H3 (Marluvas/Tecmater) en un workspace.

Bloque 8 — E3 cierre parciales. Resuelve la deuda documentada en:
- Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md §E3-0 t.5
- docs/audits/AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md §2.1

El script espera un directorio con archivos de texto/tablas/PDF soportados por
`app/src/kb.py:ingest_kb_source()`. No transforma ni inventa datos: lee lo que
exista y lo ingiere con `source_version` y `approved_by` del operador.

Ejemplo (dry-run):
    python app/scripts/ingest_kb_h3.py \\
        --tenant-id tnt_xxx \\
        --workspace-id ws_yyy \\
        --source-dir ~/KB_H3_Marluvas_Tecmater

Ejemplo (ejecutar):
    python app/scripts/ingest_kb_h3.py \\
        --tenant-id tnt_xxx \\
        --workspace-id ws_yyy \\
        --source-dir ~/KB_H3_Marluvas_Tecmater \\
        --execute --approved-by usr_operador
"""

from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.src.context import Context
from app.src.db import connect
from app.src.kb import ingest_kb_source


SOURCE_TYPES = {
    ".md": "md",
    ".txt": "txt",
    ".csv": "csv",
    ".xlsx": "xlsx",
    ".pdf": "pdf",
    ".docx": "docx",
    ".json": "json",
}


def _resolve_source_type(path: Path) -> str | None:
    ext = path.suffix.lower()
    return SOURCE_TYPES.get(ext)


def _ingest_file(
    conn: Any,
    ctx: Context,
    path: Path,
    *,
    dry_run: bool,
    approved_by: str | None,
) -> dict[str, Any]:
    source_type = _resolve_source_type(path)
    if source_type is None:
        return {"status": "skipped", "reason": "unsupported extension"}

    data = path.read_bytes()
    mime_type, _ = mimetypes.guess_type(str(path))
    mime_type = mime_type or "application/octet-stream"

    if dry_run:
        return {
            "status": "dry-run",
            "title": path.stem,
            "source_type": source_type,
            "size": len(data),
        }

    result = ingest_kb_source(
        ctx,
        conn,
        title=path.stem,
        source_type=source_type,
        content_blob=data,
        file_name=path.name,
        mime_type=mime_type,
        file_size=len(data),
        approved_by=approved_by,
    )
    return {"status": "ingested", "source_id": result.get("id"), "title": result.get("title")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ingest KB H3 sources into a FaberLoom workspace."
    )
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approved-by", default="kb_h3_ingest")
    parser.add_argument(
        "--db-path",
        default=os.getenv("FABERLOOM_DB_PATH"),
        help="Path to the FaberLoom SQLite database (default: FABERLOOM_DB_PATH env).",
    )
    args = parser.parse_args(argv)

    if not args.db_path:
        print("Error: --db-path or FABERLOOM_DB_PATH is required", file=sys.stderr)
        return 2

    os.environ["FABERLOOM_DB_PATH"] = args.db_path

    if not args.source_dir.is_dir():
        print(f"Error: {args.source_dir} is not a directory", file=sys.stderr)
        return 2

    ctx = Context(
        workspace_id=args.workspace_id,
        tenant_id=args.tenant_id,
        user_id="kb_h3_ingest",
        actor_id="kb_h3_ingest",
        actor_role_at_decision="system",
    )

    conn = connect()
    try:
        results: list[dict[str, Any]] = []
        for path in sorted(args.source_dir.iterdir()):
            if not path.is_file():
                continue
            result = _ingest_file(
                conn,
                ctx,
                path,
                dry_run=not args.execute,
                approved_by=args.approved_by,
            )
            result["path"] = str(path)
            results.append(result)
            status = result["status"]
            if status == "skipped":
                print(f"[skip] {path.name}: {result['reason']}")
            elif status == "dry-run":
                print(
                    f"[dry-run] {path.name}: {result['source_type']} "
                    f"({result['size']} bytes) -> '{result['title']}'"
                )
            else:
                print(f"[ingested] {path.name}: {result['source_id']} '{result['title']}'")

        ingested = sum(1 for r in results if r["status"] == "ingested")
        dry = sum(1 for r in results if r["status"] == "dry-run")
        skipped = sum(1 for r in results if r["status"] == "skipped")
        print(f"\nSummary: ingested={ingested} dry-run={dry} skipped={skipped}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
