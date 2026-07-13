#!/usr/bin/env python3
"""Carga golden cases de PACK 2 (comex) para validar el carril H3/golden.

Bloque E5-3 — reduce el desbloqueo a una acción humana:
  1. CEO entrega documentación real Marluvas/Tecmater.
  2. Operador corre este script con --source-dir <dir> --execute.
  3. El script genera evidencia auto-recolectada del carril validado.

Mientras no haya H3 real, --synthetic crea 3 casos marcados [SINTETICO]
que prueban que el pipeline de golden cases funciona de extremo a extremo.

Ejemplo (dry-run con docs reales):
    python app/scripts/load_pack2_golden.py \\
        --tenant-id tnt_xxx --workspace-id ws_yyy \\
        --source-dir ~/KB_H3_Marluvas_Tecmater

Ejemplo (cargar sintéticos para validar carril):
    python app/scripts/load_pack2_golden.py \\
        --tenant-id tnt_xxx --workspace-id ws_yyy \\
        --synthetic --execute --approved-by usr_tester

Ejemplo (docs reales + sintéticos en un solo comando):
    python app/scripts/load_pack2_golden.py \\
        --tenant-id tnt_xxx --workspace-id ws_yyy \\
        --source-dir ~/KB_H3_Marluvas_Tecmater \\
        --synthetic --execute --approved-by usr_operador
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.src.audit import audit_writer
from app.src.context import Context, enforce_tenant_scoped
from app.src.db import connect, new_id, transaction, utc_now
from app.src.kb import ingest_kb_source
from app.src.models import SCHEMA_VERSION
from app.src.skill_primitives import attach_evidence


SOURCE_TYPES = {
    ".md": "md",
    ".txt": "txt",
    ".csv": "csv",
    ".xlsx": "xlsx",
    ".pdf": "pdf",
    ".docx": "docx",
    ".json": "json",
}

# Skills de PACK 2 (comex) según ENT_FB_SKILL_CATALOG_v1.2.md.
# Se usan para crear golden cases sintéticos de validación de carril.
SYNTHETIC_SKILLS = [
    "SKILL_CX_PEDIMENTO_CROSSCHECK",
    "SKILL_CX_HS_CLASSIFY",
    "SKILL_CX_DUTY_CALC",
]

SYNTHETIC_CASES: list[dict[str, Any]] = [
    {
        "skill_id": "SKILL_CX_PEDIMENTO_CROSSCHECK",
        "case_id": "synthetic-pedimento-001",
        "input_json": {
            "pedimento": "1234567",
            "factura": "FAC-001",
            "guia": "GUIA-001",
            "nota": "[SINTETICO] Datos de prueba para validar carril de pedimentos.",
        },
        "expected_output_json": {
            "discrepancias": [],
            "estado": "OK",
            "nota": "[SINTETICO] Resultado simulado; requiere validación con pedimento real.",
        },
    },
    {
        "skill_id": "SKILL_CX_HS_CLASSIFY",
        "case_id": "synthetic-hs-001",
        "input_json": {
            "producto": "Zapatos deportivos de cuero sintético",
            "pais_origen": "CN",
            "nota": "[SINTETICO] Descripción de prueba para clasificación arancelaria.",
        },
        "expected_output_json": {
            "partida_hs": "6403.99.90",
            "confianza": "media",
            "nota": "[SINTETICO] Partida sugerida por simulación; requiere revisión aduanera real.",
        },
    },
    {
        "skill_id": "SKILL_CX_DUTY_CALC",
        "case_id": "synthetic-duty-001",
        "input_json": {
            "cif_usd": 10000.0,
            "arancel_pct": 15.0,
            "iva_pct": 13.0,
            "nota": "[SINTETICO] Valores de prueba para cálculo de derechos.",
        },
        "expected_output_json": {
            "derechos_arancelarios": 1500.0,
            "iva": 1495.0,
            "total_impuestos": 2995.0,
            "moneda": "USD",
            "nota": "[SINTETICO] Cálculo ilustrativo; requiere tasas vigentes reales.",
        },
    },
]


def _resolve_source_type(path: Path) -> str | None:
    return SOURCE_TYPES.get(path.suffix.lower())


def _validate_tenant_workspace(conn: Any, ctx: Context) -> None:
    enforce_tenant_scoped(ctx)
    ws = conn.execute(
        "SELECT 1 FROM workspace WHERE id = ? AND tenant_id = ?",
        (ctx.require_scoped_workspace(), ctx.require_tenant()),
    ).fetchone()
    if ws is None:
        raise ValueError(
            f"workspace {ctx.workspace_id} no existe o no pertenece al tenant {ctx.tenant_id}"
        )


def _ingest_source_dir(
    conn: Any,
    ctx: Context,
    source_dir: Path,
    *,
    dry_run: bool,
    approved_by: str | None,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in sorted(source_dir.iterdir()):
        if not path.is_file():
            continue
        source_type = _resolve_source_type(path)
        if source_type is None:
            results.append({"path": str(path), "status": "skipped", "reason": "unsupported extension"})
            continue

        data = path.read_bytes()
        mime_type, _ = mimetypes.guess_type(str(path))
        mime_type = mime_type or "application/octet-stream"

        if dry_run:
            results.append(
                {
                    "path": str(path),
                    "status": "dry-run",
                    "title": path.stem,
                    "source_type": source_type,
                    "size": len(data),
                }
            )
            continue

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
        results.append(
            {
                "path": str(path),
                "status": "ingested",
                "source_id": result.get("id"),
                "title": result.get("title"),
            }
        )
    return results


def _attach_synthetic_evidence(
    conn: Any,
    ctx: Context,
    golden_case_id: str,
) -> None:
    now = utc_now()
    attach_evidence(
        ctx,
        conn,
        entity_type="golden_case",
        entity_id=golden_case_id,
        evidence_items=[
            {
                "source_type": "synthetic_note",
                "source_locator": "app/scripts/load_pack2_golden.py",
                "captured_at": now,
                "content_text": (
                    "[SINTETICO] Caso generado para validar el carril de golden cases de PACK 2. "
                    "No constituye evidencia real de producción. "
                    "Reemplazar por caso con fuente H3 real antes de promover el pack."
                ),
            }
        ],
    )


def _upsert_synthetic_cases(
    conn: Any,
    ctx: Context,
    *,
    approved_by: str | None,
) -> list[dict[str, Any]]:
    now = utc_now()
    created: list[dict[str, Any]] = []
    for case in SYNTHETIC_CASES:
        case_id = case["case_id"]
        skill_id = case["skill_id"]
        input_json = json.dumps(case["input_json"], ensure_ascii=False)
        expected_output_json = json.dumps(case["expected_output_json"], ensure_ascii=False)

        with transaction(conn, ctx=ctx):
            conn.execute(
                """
                INSERT INTO golden_case (
                    id, workspace_id, tenant_id, skill_id, case_id,
                    input_json, expected_output_json, evidence_required,
                    approved, approved_by, approved_at, verified_by,
                    schema_version, source_version, origin, run_id, frozen_at,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 1, 0, NULL, NULL, NULL, ?, 'v2', ?, NULL, ?, ?, ?)
                ON CONFLICT(workspace_id, tenant_id, skill_id, case_id) DO UPDATE SET
                    input_json = excluded.input_json,
                    expected_output_json = excluded.expected_output_json,
                    origin = excluded.origin,
                    run_id = NULL,
                    frozen_at = excluded.frozen_at,
                    approved = 0,
                    approved_by = NULL,
                    approved_at = NULL,
                    verified_by = NULL,
                    updated_at = excluded.updated_at
                """,
                (
                    new_id("gcs"),
                    ctx.require_scoped_workspace(),
                    ctx.require_tenant(),
                    skill_id,
                    case_id,
                    input_json,
                    expected_output_json,
                    SCHEMA_VERSION,
                    "synthetic",
                    now,
                    now,
                    now,
                ),
            )

            row = conn.execute(
                """
                SELECT id FROM golden_case
                WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ? AND case_id = ?
                """,
                (ctx.require_scoped_workspace(), ctx.require_tenant(), skill_id, case_id),
            ).fetchone()
            assert row is not None
            _attach_synthetic_evidence(conn, ctx, row["id"])

            audit_writer.write(
                ctx,
                conn,
                action="golden_case.synthetic_loaded",
                payload={
                    "skill_id": skill_id,
                    "case_id": case_id,
                    "origin": "synthetic",
                    "note": "[SINTETICO] Validacion de carril PACK 2",
                },
                approved_by=approved_by,
                source_version="v2",
                skill_version=skill_id,
                system_event=False,
            )

        created.append({"skill_id": skill_id, "case_id": case_id})
    return created


def _render_report(
    *,
    tenant_id: str,
    workspace_id: str,
    source_dir: Path | None,
    source_results: list[dict[str, Any]],
    synthetic_created: list[dict[str, Any]],
    dry_run: bool,
    generated_at: str,
) -> str:
    lines: list[str] = [
        "# Evidencia de validación del carril PACK 2 (comex)",
        "",
        f"- **tenant_id**: `{tenant_id}`",
        f"- **workspace_id**: `{workspace_id}`",
        f"- **generado_en**: `{generated_at}`",
        f"- **dry_run**: `{dry_run}`",
        "",
        "## Resumen",
        "",
        f"- Archivos KB procesados: {len(source_results)}",
        f"- Casos sintéticos creados/actualizados: {len(synthetic_created)}",
        "",
        "## Origen de datos",
        "",
    ]
    if source_dir:
        lines.append(f"- Directorio de fuentes H3: `{source_dir}`")
    else:
        lines.append("- No se proporcionó directorio de fuentes H3 reales.")
    lines.append(
        "- Los casos sintéticos se marcan explícitamente como `[SINTETICO]` "
        "y no son evidencia real de producción."
    )
    lines.append("")

    if source_results:
        lines.extend(["## Procesamiento de fuentes KB", "", "| archivo | estado | detalle |", "|---|---|---|"])
        for r in source_results:
            detail = r.get("source_id") or r.get("reason") or f"{r.get('size', 0)} bytes"
            lines.append(f"| `{Path(r['path']).name}` | {r['status']} | {detail} |")
        lines.append("")

    if synthetic_created:
        lines.extend(["## Casos sintéticos de validación", "", "| skill_id | case_id |", "|---|---|"])
        for c in synthetic_created:
            lines.append(f"| `{c['skill_id']}` | `{c['case_id']}` |")
        lines.append("")

    lines.extend(
        [
            "## Próximos pasos humanos",
            "",
            "1. CEO entrega documentación H3 real de Marluvas/Tecmater.",
            "2. Operador corre el script con `--source-dir <dir> --execute --approved-by <usr>`.",
            "3. Curador aprueba y verifica los golden cases reales (approved_by != verified_by).",
            "4. Pack 2 puede salir de `POSPUESTO` a `SHADOW` cuando se cumplan los gates.",
            "",
            "## Reglas de oro aplicadas",
            "",
            "- R1: Nada sintético se presenta como evidencia real; todos los casos llevan `[SINTETICO]`.",
            "- R2: Esquema FROZEN intacto; inserciones usan columnas existentes.",
            "- R11/R12: Context tenant-scoped y audit log por cada caso cargado.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Carga golden cases de PACK 2 (comex) y valida el carril H3."
    )
    parser.add_argument("--tenant-id", required=True)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--source-dir", type=Path, default=None)
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approved-by", default=None)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/audits") / f"EVIDENCIA_PACK2_CARRIL_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md",
    )
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

    if not args.source_dir and not args.synthetic:
        print(
            "Error: debe especificar --source-dir con documentos H3 reales, "
            "--synthetic para validar el carril, o ambos.",
            file=sys.stderr,
        )
        return 2

    if args.source_dir and not args.source_dir.is_dir():
        print(f"Error: {args.source_dir} no es un directorio", file=sys.stderr)
        return 2

    if args.execute and not args.approved_by:
        print("Error: --execute requiere --approved-by", file=sys.stderr)
        return 2

    ctx = Context(
        workspace_id=args.workspace_id,
        tenant_id=args.tenant_id,
        user_id=args.approved_by or "load_pack2_golden",
        actor_id=args.approved_by or "load_pack2_golden",
        actor_role_at_decision="system",
    )

    conn = connect()
    try:
        _validate_tenant_workspace(conn, ctx)

        source_results: list[dict[str, Any]] = []
        if args.source_dir:
            source_results = _ingest_source_dir(
                conn,
                ctx,
                args.source_dir,
                dry_run=not args.execute,
                approved_by=args.approved_by,
            )

        synthetic_created: list[dict[str, Any]] = []
        if args.synthetic:
            if args.execute:
                synthetic_created = _upsert_synthetic_cases(conn, ctx, approved_by=args.approved_by)
            else:
                synthetic_created = [
                    {"skill_id": c["skill_id"], "case_id": c["case_id"]} for c in SYNTHETIC_CASES
                ]

        generated_at = utc_now()
        report = _render_report(
            tenant_id=args.tenant_id,
            workspace_id=args.workspace_id,
            source_dir=args.source_dir,
            source_results=source_results,
            synthetic_created=synthetic_created,
            dry_run=not args.execute,
            generated_at=generated_at,
        )

        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")

        if source_results:
            ingested = sum(1 for r in source_results if r["status"] == "ingested")
            skipped = sum(1 for r in source_results if r["status"] == "skipped")
            dry = sum(1 for r in source_results if r["status"] == "dry-run")
            print(f"KB sources: ingested={ingested} dry-run={dry} skipped={skipped}")
        if args.synthetic:
            print(f"Synthetic golden cases: {len(synthetic_created)}")
        print(f"Report written to: {args.out}")
        return 0
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
