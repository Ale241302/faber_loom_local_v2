"""Global skill catalog (E3-4).

Loads SKILL.md files from the FaberLoom catalog into the
``global_skill_catalog`` table so every user can pick them as context in chat.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

import yaml

from .db import get_global_skill_by_id, upsert_global_skill
from .faberloom_catalog import _catalog_dir
from .skills import _extract_frontmatter, compile_skill_md_v2


def _read_frontmatter(skill_md: str) -> dict[str, Any]:
    """Return the YAML frontmatter as a plain dict."""

    frontmatter, _ = _extract_frontmatter(skill_md)
    return frontmatter if isinstance(frontmatter, dict) else {}


def _pack_id_from_frontmatter(frontmatter: dict[str, Any]) -> str | None:
    """Resolve pack_id from metadata.fbl.pack_id or legacy top-level pack_id."""

    metadata = frontmatter.get("metadata") or {}
    if isinstance(metadata, dict):
        fbl = metadata.get("fbl") or metadata.get("mwt") or {}
        if isinstance(fbl, dict) and fbl.get("pack_id"):
            return str(fbl["pack_id"]).strip()
    return str(frontmatter.get("pack_id", "")).strip() or None


def _skill_id_from_manifest(manifest: dict[str, Any]) -> str:
    """Return the canonical skill id from a compiled manifest."""

    fbl = manifest.get("metadata", {}).get("fbl", {})
    return str(fbl.get("id", manifest.get("name", ""))).strip() or manifest["name"]


def _serialize_for_json(value: Any) -> Any:
    """Recursively convert YAML date/datetime objects to ISO strings."""

    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _serialize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize_for_json(v) for v in value]
    return value


def seed_global_skill_catalog(conn: Any) -> tuple[int, list[str]]:
    """Read SKILL_*.md files from the FaberLoom catalog and upsert them.

    Returns (count upserted, list of warnings).
    """

    catalog_dir = _catalog_dir()
    warnings: list[str] = []
    upserted = 0

    if not catalog_dir.exists():
        warnings.append(f"Catalog directory not found: {catalog_dir}")
        return upserted, warnings

    for path in sorted(catalog_dir.glob("SKILL_*.md")):
        skill_md = path.read_text(encoding="utf-8")
        try:
            manifest = compile_skill_md_v2(skill_md)
        except ValueError as exc:
            warnings.append(f"Skipping {path.name}: {exc}")
            continue

        frontmatter = _read_frontmatter(skill_md)
        pack_id = _pack_id_from_frontmatter(frontmatter)
        if not pack_id:
            warnings.append(f"Skipping {path.name}: missing pack_id in metadata.fbl.pack_id")
            continue

        skill_id = _skill_id_from_manifest(manifest)
        if not skill_id:
            warnings.append(f"Skipping {path.name}: could not resolve skill_id")
            continue

        from .db import new_id

        skill_row = get_global_skill_by_id(conn, skill_id, tenant_id="global", active_only=False)
        skill_uuid = skill_row["id"] if skill_row else new_id("gskill")

        upsert_global_skill(
            conn,
            id=skill_uuid,
            tenant_id="global",
            pack_id=pack_id,
            skill_id=skill_id,
            name=manifest["name"],
            description=manifest.get("description", ""),
            skill_md=skill_md,
            manifest_json=json.dumps(_serialize_for_json(manifest), ensure_ascii=False, sort_keys=True),
            is_active=1,
            approved_by="system",
        )
        upserted += 1

    return upserted, warnings
