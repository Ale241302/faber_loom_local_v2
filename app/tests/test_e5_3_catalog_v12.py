"""E5-3 — Skill catalog v1.2 has no definition gaps."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest


CATALOG_PATH = Path(__file__).parent.parent.parent / "docs" / "faberloom" / "ENT_FB_SKILL_CATALOG_v1.2.md"


# Veredictos terminales válidos. "POSPUESTO" es un veredicto si lleva razón y fecha.
VALID_VERDICTS = {
    "MIGRADO-SHADOW",
    "DEFINIDO-SHADOW",
    "DEPRECATED",
    "DESCARTADO",
    "POSPUESTO",
}


def _parse_catalog_table(path: Path) -> list[dict[str, str]]:
    """Parse the skill tables from the catalog markdown."""

    text = path.read_text(encoding="utf-8")
    rows: list[dict[str, str]] = []

    # Match any markdown table row with 4 or 5 columns that contains a SKILL_ id.
    for line in text.splitlines():
        if "SKILL_" not in line or line.startswith("|") is False:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 4:
            continue
        if "ID" in cells[0] or "---" in cells[0]:
            continue
        skill_id = cells[0]
        if not skill_id.startswith("SKILL_"):
            continue
        entry: dict[str, str] = {
            "id": skill_id,
            "name": cells[1] if len(cells) > 1 else "",
            "verdict": cells[2] if len(cells) > 2 else "",
        }
        if len(cells) > 3:
            entry["reason_or_location"] = cells[3]
        if len(cells) > 4:
            entry["review_date"] = cells[4]
        rows.append(entry)

    return rows


def test_every_skill_has_a_verdict() -> None:
    rows = _parse_catalog_table(CATALOG_PATH)
    assert rows, "catalog table should contain skills"

    missing: list[str] = []
    for row in rows:
        verdict = row.get("verdict", "")
        if verdict not in VALID_VERDICTS:
            missing.append(f"{row['id']}: {verdict!r}")

    assert not missing, f"skills with invalid/missing verdicts: {missing}"


def test_no_definition_pending_gaps() -> None:
    rows = _parse_catalog_table(CATALOG_PATH)
    bad = [r["id"] for r in rows if r.get("verdict", "") == "DEFINITION_PENDING"]
    assert not bad, f"skills still in DEFINITION_PENDING: {bad}"


def test_postponed_skills_have_reason_and_review_date() -> None:
    rows = _parse_catalog_table(CATALOG_PATH)
    postponed = [r for r in rows if r.get("verdict") == "POSPUESTO"]
    assert postponed, "expected at least one POSPUESTO skill (PACK 2 until H3 arrives)"

    for row in postponed:
        reason = row.get("reason_or_location", "")
        review = row.get("review_date", "")
        assert reason, f"{row['id']} is POSPUESTO without reason"
        assert review, f"{row['id']} is POSPUESTO without review date"
        assert re.search(r"20\d{2}", reason) or re.search(r"20\d{2}", review), "review/reason must contain a year"


def test_no_active_or_auto_apply_skills_in_catalog() -> None:
    text = CATALOG_PATH.read_text(encoding="utf-8")
    # The catalog itself should not declare any skill as ACTIVE.
    assert "| ACTIVE |" not in text
    # auto_apply is prohibited in v2 manifests.
    assert "auto_apply = true" not in text
    assert "auto_apply: true" not in text


def test_catalog_references_no_invented_external_data() -> None:
    text = CATALOG_PATH.read_text(encoding="utf-8")
    # URLs of tax authorities / external portals must not be invented.
    # The catalog should not contain hardcoded URLs except internal repo paths.
    url_matches = re.findall(r"https?://[^\s|)]+", text)
    assert not url_matches, f"catalog should not contain invented URLs: {url_matches}"
