"""FaberLoom catalog importer for FaberLoom.

Reads Markdown specs/agents/templates from the ``faberloom/`` directory (or the
bundled ``static/faberloom/`` copy inside a PyInstaller build) and imports them
as workspace routines. Imported routines are intentionally created as inactive
and unapproved so a human must review/activate them before execution.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from .context import Context
from .db import create_routine, get_routine_by_name, update_routine
from .skills import _detect_dangerous, compile_skill_md


_PERSONA_MD_MAX_LEN = 20000


class FaberloomCatalogItem(BaseModel):
    id: str
    name: str
    description: str
    version: str
    category: str
    file: str
    skill_md: str
    persona_md: str
    tools_allowlist: str
    schema_output_json: str
    trigger_json: str
    source_version: str


class FaberloomImportRequest(BaseModel):
    imports: list[str] = Field(default_factory=list, min_length=1)


def _app_dir() -> Path:
    """Return the application directory (``app/``)."""

    if hasattr(sys, "_MEIPASS"):
        # PyInstaller unpacks everything under _MEIPASS; static/ lives there.
        return Path(sys._MEIPASS) / "static"
    return Path(__file__).resolve().parent.parent


def _catalog_dir() -> Path:
    """Locate the folder that contains the FaberLoom Markdown catalog.

    Prefers the bundled ``static/faberloom/`` copy when it exists (production
    executable) and falls back to the repository ``faberloom/`` folder during
    development.
    """

    app_dir = _app_dir()
    bundled = app_dir / "faberloom"
    if bundled.exists() and any(bundled.iterdir()):
        return bundled

    # Development layout: app/src/faberloom_catalog.py -> repo root/faberloom
    repo_faberloom = app_dir.parent / "faberloom"
    if repo_faberloom.exists():
        return repo_faberloom

    # Last resort: return bundled path even if empty so callers can report it.
    return bundled


def _safe_path(catalog_dir: Path, relative: str) -> Path | None:
    """Resolve a catalog-relative path, ensuring it stays inside ``catalog_dir``."""

    try:
        candidate = (catalog_dir / relative).resolve(strict=True)
    except (OSError, ValueError):
        return None
    if not str(candidate).startswith(str(catalog_dir.resolve())):
        return None
    return candidate


def _extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split Markdown text into YAML frontmatter and body."""

    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    frontmatter_text = parts[1].strip()
    body = parts[2].strip()
    try:
        metadata = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError:
        metadata = {}
    if not isinstance(metadata, dict):
        metadata = {}
    return metadata, body


def _derive_category(file_name: str, metadata: dict[str, Any]) -> str:
    """Classify a FaberLoom item."""

    declared = metadata.get("type") or metadata.get("kind")
    if declared in {"skill", "agent", "template", "reference"}:
        return str(declared)

    upper = file_name.upper()
    if file_name == "SKILL.md" or upper.startswith("SKILL_"):
        return "skill"
    if "AGENT" in upper or "ARCHETYPE" in upper or "SUB_AGENT" in upper:
        return "agent"
    if "TEMPLATE" in upper or "TPL_" in upper:
        return "template"
    return "reference"


def _slugify_id(value: str) -> str:
    """Return a lowercase, dash-separated slug."""

    text = re.sub(r"[^\w\s-]", "", value.lower().strip())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with an ellipsis marker when it exceeds ``max_len``."""

    if len(text) <= max_len:
        return text
    marker = "\n\n[truncado por longitud]"
    return text[: max_len - len(marker)] + marker


def _build_minimal_skill_md(name: str, version: str, description: str, triggers: list[str]) -> str:
    """Build a small, safe SKILL.md that passes the injection gate.

    The full FaberLoom document is kept in ``persona_md``; this minimal skill is
    only meant to be a placeholder until a human edits and approves the routine.
    """

    frontmatter = {
        "name": name,
        "version": version,
        "persona": description,
        "tools": [],
        "schema_output": {},
        "triggers": triggers,
    }
    yaml_lines = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False)
    body = (
        "Este skill fue importado desde la biblioteca FaberLoom. "
        "Revisa el documento fuente en persona_md, completa las instrucciones "
        "y actívalo antes de ejecutarlo."
    )
    return f"---\n{yaml_lines}---\n\n{body}\n"


def _catalog_item(file_path: Path, catalog_dir: Path) -> FaberloomCatalogItem | None:
    """Build a catalog item from a single Markdown file."""

    try:
        text = file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    metadata, body = _extract_frontmatter(text)
    name = metadata.get("name") or file_path.stem
    if not name:
        return None

    description = metadata.get("description") or metadata.get("summary") or ""
    if isinstance(description, list):
        description = " ".join(str(x) for x in description)
    description = str(description).strip()

    version = str(metadata.get("version") or "1.0.0").strip()
    category = _derive_category(file_path.name, metadata)
    item_id = _slugify_id(f"{category}:{file_path.stem}")
    triggers = metadata.get("triggers") or []
    if not isinstance(triggers, list):
        triggers = []
    triggers = [str(t) for t in triggers]

    source_text = _truncate(text, _PERSONA_MD_MAX_LEN)
    skill_md = _build_minimal_skill_md(name, version, description, triggers)

    return FaberloomCatalogItem(
        id=item_id,
        name=name,
        description=description,
        version=version,
        category=category,
        file=str(file_path.relative_to(catalog_dir)),
        skill_md=skill_md,
        persona_md=source_text,
        tools_allowlist="[]",
        schema_output_json="{}",
        trigger_json=json.dumps(triggers, ensure_ascii=False),
        source_version=f"faberloom-{category}",
    )


def list_catalog() -> list[FaberloomCatalogItem]:
    """Return all importable FaberLoom items."""

    catalog_dir = _catalog_dir()
    if not catalog_dir.exists():
        return []

    items: list[FaberloomCatalogItem] = []
    for path in sorted(catalog_dir.glob("*.md")):
        item = _catalog_item(path, catalog_dir)
        if item is not None:
            items.append(item)
    return items


def get_catalog_item(item_id: str) -> FaberloomCatalogItem | None:
    """Return a single catalog item by id."""

    for item in list_catalog():
        if item.id == item_id:
            return item
    return None


def import_catalog_items(
    ctx: Context,
    conn: Any,
    item_ids: list[str],
) -> list[dict[str, Any]]:
    """Import selected catalog items into the current workspace.

    Existing routines with the same name are updated (their content is replaced
    and approval is cleared). New routines are created inactive and unapproved.
    All imported content passes the same injection canaries used for SKILL.md.
    """

    items = [get_catalog_item(item_id) for item_id in item_ids]
    items = [item for item in items if item is not None]
    if not items:
        return []

    for item in items:
        for field, label in (
            (item.persona_md, "persona_md"),
            (item.skill_md, "skill_md"),
        ):
            dangers = _detect_dangerous(field)
            if dangers:
                raise ValueError(
                    f"Unsafe {label} content in catalog item '{item.id}': " + "; ".join(dangers)
                )
        # Ensure the minimal skill_md is syntactically valid and frontmatter is safe.
        try:
            compile_skill_md(item.skill_md)
        except ValueError as exc:
            raise ValueError(f"Invalid skill_md in catalog item '{item.id}': {exc}") from exc

    routines: list[dict[str, Any]] = []
    for item in items:
        existing_list = get_routine_by_name(ctx, conn, item.name)
        existing = existing_list[0] if existing_list else None
        if existing is not None:
            updated = update_routine(
                ctx,
                conn,
                existing["id"],
                name=item.name,
                skill_md=item.skill_md,
                tools_allowlist=item.tools_allowlist,
                schema_output_json=item.schema_output_json,
                trigger_json=item.trigger_json,
                persona_md=item.persona_md,
                is_active=0,
                category=item.category,
                source_version=item.source_version,
                approved_by=None,
            )
            if updated is not None:
                routines.append(updated)
        else:
            created = create_routine(
                ctx,
                conn,
                name=item.name,
                skill_md=item.skill_md,
                tools_allowlist=item.tools_allowlist,
                schema_output_json=item.schema_output_json,
                preset_id=None,
                trigger_json=item.trigger_json,
                persona_md=item.persona_md,
                is_active=0,
                category=item.category,
                source_version=item.source_version,
            )
            routines.append(created)
    return routines
