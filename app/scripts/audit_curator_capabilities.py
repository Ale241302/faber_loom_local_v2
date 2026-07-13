#!/usr/bin/env python3
"""Auditoría ejecutable de capacidades del curador (vista Skills / catálogo v2).

El script puede correr contra producción (Postgres) o localmente (SQLite).
Requiere acceso al filesystem para leer los archivos SKILL_*.md y app.jsx.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


REPO_BLOB_URL = "https://github.com/Ale241302/faber_loom_local_v2/blob/main"
REPO_RAW_URL = "https://raw.githubusercontent.com/Ale241302/faber_loom_local_v2/main"

SKILL_DIR = Path(__file__).resolve().parents[1] / "faberloom"
APP_JSX = Path(__file__).resolve().parents[1] / "static" / "js" / "app.jsx"


@dataclass
class SkillAuditItem:
    file: str
    skill_id: str | None = None
    status: str | None = None
    ok: bool = True
    findings: list[str] = field(default_factory=list)
    github_url: str = ""


@dataclass
class CuratorAuditReport:
    started_at: str = field(default_factory=_now)
    ended_at: str | None = None
    schema_version: int | None = None
    db_engine: str | None = None
    total_skill_files: int = 0
    db_skill_manifests: dict[str, int] = field(default_factory=dict)
    permission_check: dict[str, Any] = field(default_factory=dict)
    all_ok: bool = True
    findings: list[dict[str, Any]] = field(default_factory=list)
    human_review_items: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _github_blob_url(relative_path: str) -> str:
    return f"{REPO_BLOB_URL}/{relative_path}"


def _open_db_connection(postgres_url: str | None = None) -> Any:
    engine = os.getenv("FABERLOOM_DB_ENGINE", "")
    if engine == "postgres" or postgres_url:
        import psycopg

        url = postgres_url or os.getenv("FABERLOOM_POSTGRES_URL") or os.getenv("DATABASE_URL")
        if not url:
            raise RuntimeError("FABERLOOM_POSTGRES_URL or --postgres-url required")
        conn = psycopg.connect(url, autocommit=False)
        conn.row_factory = psycopg.rows.dict_row
        return conn

    # Fallback SQLite para tests / local
    import sqlite3

    db_path = os.getenv("FABERLOOM_SQLITE_PATH", "data/faberloom.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _schema_version(conn: Any) -> int | None:
    try:
        row = conn.execute("SELECT MAX(version) AS v FROM _schema_version").fetchone()
        return row["v"] if row and row.get("v") is not None else None
    except Exception:
        return None


def _db_skill_counts(conn: Any) -> dict[str, int]:
    try:
        rows = conn.execute("SELECT status, COUNT(*) AS n FROM skill_manifest GROUP BY status").fetchall()
        return {row["status"]: row["n"] for row in rows}
    except Exception:
        return {}


def _active_without_goldens(conn: Any) -> list[dict[str, Any]]:
    try:
        rows = conn.execute(
            """
            SELECT sm.id, sm.skill_id, sm.workspace_id, sm.tenant_id, sm.status
            FROM skill_manifest sm
            WHERE sm.status = 'active'
              AND NOT EXISTS (
                  SELECT 1 FROM golden_case gc
                  WHERE gc.skill_id = sm.skill_id
                    AND gc.workspace_id = sm.workspace_id
                    AND gc.tenant_id = sm.tenant_id
                    AND gc.approved = 1
              )
            """
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def _extract_frontmatter(text: str) -> dict[str, Any] | None:
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1]) or {}
    except Exception:
        return None


def _check_skill_file(path: Path) -> SkillAuditItem:
    rel = path.relative_to(Path(__file__).resolve().parents[2]).as_posix()
    item = SkillAuditItem(
        file=rel,
        github_url=_github_blob_url(rel),
    )
    text = path.read_text(encoding="utf-8")
    fm = _extract_frontmatter(text)
    if fm is None:
        item.ok = False
        item.findings.append("No se pudo parsear el frontmatter YAML")
        return item

    meta = fm.get("metadata", {}).get("fbl", {}) or {}
    item.skill_id = meta.get("id") or fm.get("name")
    item.status = (meta.get("status") or "UNKNOWN").lower()

    if item.status not in {"shadow", "active", "deprecated", "archived"}:
        item.ok = False
        item.findings.append(f"status no permitido: {item.status}")

    budget = meta.get("budget", {}) or {}
    kill = budget.get("kill_switch", {}) or {}
    if kill.get("enabled") is not True:
        item.ok = False
        item.findings.append("kill_switch.enabled no es true")

    lc = meta.get("learning_consolidation", {}) or {}
    if lc.get("auto_apply") is not False:
        item.ok = False
        item.findings.append("learning_consolidation.auto_apply no es false")

    contract = meta.get("contract", {}) or {}
    outputs = contract.get("outputs", []) or []
    requires_hitl = any(o.get("requires_human_approval") for o in outputs)
    if not requires_hitl and item.status == "active":
        item.ok = False
        item.findings.append("skill active sin outputs que requieran aprobación humana")

    if "[PENDIENTE — NO INVENTAR]" in text:
        item.findings.append("contiene placeholders [PENDIENTE — NO INVENTAR]")

    return item


def _check_permissions() -> dict[str, Any]:
    result = {"file_exists": False, "can_manage_skills_includes_curator": False, "snippet": ""}
    if not APP_JSX.exists():
        return result
    result["file_exists"] = True
    text = APP_JSX.read_text(encoding="utf-8")
    # Buscar definición de canManageSkills y presencia de "curator"
    match = re.search(r"const\s+canManageSkills\s*=.*?(?:\n|$)", text, re.DOTALL)
    if match:
        snippet = match.group(0)
        result["snippet"] = snippet.strip()
        result["can_manage_skills_includes_curator"] = '"curator"' in snippet or "'curator'" in snippet
    return result


def run_audit(
    postgres_url: str | None = None,
    repo_url: str | None = None,
) -> CuratorAuditReport:
    report = CuratorAuditReport()
    if repo_url:
        report.github_base = repo_url  # type: ignore[attr-defined]

    conn = _open_db_connection(postgres_url)
    try:
        report.schema_version = _schema_version(conn)
        report.db_skill_manifests = _db_skill_counts(conn)
        active_without_goldens = _active_without_goldens(conn)
    finally:
        conn.close()

    skill_files = sorted(SKILL_DIR.glob("SKILL_*.md"))
    report.total_skill_files = len(skill_files)
    skill_items: list[SkillAuditItem] = []
    for path in skill_files:
        item = _check_skill_file(path)
        skill_items.append(item)
        if not item.ok:
            report.all_ok = False

    report.permission_check = _check_permissions()
    if not report.permission_check.get("can_manage_skills_includes_curator"):
        report.all_ok = False

    # Hallazgos ejecutables
    if active_without_goldens:
        report.all_ok = False
        for row in active_without_goldens:
            report.findings.append(
                {
                    "severity": "P0",
                    "category": "governance",
                    "message": f"Skill {row['skill_id']} está ACTIVE sin golden cases aprobados",
                    "skill_id": row["skill_id"],
                    "workspace_id": row["workspace_id"],
                }
            )

    for item in skill_items:
        for finding in item.findings:
            report.findings.append(
                {
                    "severity": "P2" if finding.startswith("contiene placeholders") else "P1",
                    "category": "skill_manifest",
                    "message": f"{item.file}: {finding}",
                    "skill_id": item.skill_id,
                    "file": item.file,
                    "url": item.github_url,
                }
            )

    if not report.permission_check.get("can_manage_skills_includes_curator"):
        report.findings.append(
            {
                "severity": "P0",
                "category": "permissions",
                "message": "El rol curator no aparece en canManageSkills de app.jsx",
                "file": "app/static/js/app.jsx",
                "url": _github_blob_url("app/static/js/app.jsx"),
            }
        )

    # Ítems que requieren ojo humano (máximo 5)
    human_candidates = [
        f for f in report.findings if f.get("severity") in ("P1", "P2") and f.get("url")
    ]
    for f in human_candidates[:5]:
        report.human_review_items.append(
            {
                "item": f"{f['category']} — {f['message']}",
                "url": f["url"],
                "note": "[REQUIERE OJO HUMANO]",
            }
        )

    report.ended_at = _now()
    return report


def _write_markdown(report: CuratorAuditReport, path: Path) -> None:
    lines = [
        "# Auditoría de capacidades del curador — Vista Skills (E5-0)",
        "",
        f"**Fecha de ejecución:** {report.started_at}",
        f"**DB engine:** {report.db_engine or 'inferred from env'}",
        f"**SCHEMA_VERSION:** {report.schema_version}",
        f"**Estado general:** {'✅ OK' if report.all_ok else '⚠️ HAY HALLAZGOS'}",
        "",
        "## Resumen ejecutivo",
        "",
        f"- Archivos `faberloom/SKILL_*.md` revisados: **{report.total_skill_files}**",
        f"- Skills en DB (`skill_manifest`) por estado: `{report.db_skill_manifests}`",
        f"- Permiso `canManageSkills` incluye `curator`: **{'SÍ' if report.permission_check.get('can_manage_skills_includes_curator') else 'NO'}**",
        "",
        "## Hallazgos automáticos",
        "",
    ]
    if not report.findings:
        lines.append("Sin hallazgos automáticos.")
    else:
        lines.append("| Severidad | Categoría | Hallazgo | URL |")
        lines.append("|-----------|-----------|----------|-----|")
        for f in report.findings:
            url = f.get("url", "")
            lines.append(f"| {f.get('severity','')} | {f.get('category','')} | {f.get('message','')} | {url} |")

    lines.extend(["", "## Requiere ojo humano (≤5 ítems)", ""])
    if not report.human_review_items:
        lines.append("Ningún ítem requiere revisión humana explícita.")
    else:
        for idx, item in enumerate(report.human_review_items, 1):
            lines.append(f"{idx}. {item['note']} {item['item']}")
            lines.append(f"   - URL: {item['url']}")

    lines.extend(["", "## Snippet de permisos", "", "```js", json.dumps(report.permission_check.get("snippet", ""), indent=2), "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Auditoría de capacidades del curador")
    parser.add_argument("--postgres-url", default=None, help="URL de Postgres (default: env)")
    parser.add_argument("--repo-url", default=None, help="URL base del repo para enlaces")
    parser.add_argument("--json", default=None, help="Ruta para reporte JSON")
    parser.add_argument("--md", default=None, help="Ruta para reporte Markdown")
    args = parser.parse_args(argv)

    report = run_audit(postgres_url=args.postgres_url, repo_url=args.repo_url)

    if args.json:
        Path(args.json).write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON report written to {args.json}")

    if args.md:
        _write_markdown(report, Path(args.md))
        print(f"Markdown report written to {args.md}")

    print(f"audit ok={report.all_ok} skill_files={report.total_skill_files} db_manifests={report.db_skill_manifests}")
    return 0 if report.all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
