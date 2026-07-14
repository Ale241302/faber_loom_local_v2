"""E3-4: legacy SKILL_*.md migration to manifest v2.

Verifica el lado v2 de la migracion: que cada id legacy tenga su
faberloom/SKILL_*.md compilable, sin auto-apply y con aprobacion para salidas
externas. El inventario de los originales v1 vive en mwt-knowledge-hub junto al
resto del conocimiento, asi que no se chequea desde aca.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from fastapi.testclient import TestClient


# Set of legacy skill IDs that are expected to be migrated to faberloom/ v2.
MIGRABLE_LEGACY_IDS: set[str] = {
    "SKILL_AMAZON_OPS",
    "SKILL_CLIENT_SERVICE",
    "SKILL_COMPLIANCE_CHECKER",
    "SKILL_COPY",
    "SKILL_DEMAND_FORECASTER",
    "SKILL_EXPERIMENT_RUNNER",
    "SKILL_HUMANIZE_BRAND",
    "SKILL_HUMANIZE_COMMS",
    "SKILL_KB_AUDITOR",
    "SKILL_KB_GATEWAY",
    "SKILL_PROFORMA_BUILDER",
}

# Reference-only documents that must NOT be ported as executable skills.
DEPRECATED_LEGACY_IDS: set[str] = {
    "SKILL_FRONTEND_PRINCIPLES_MWT",
    "SKILL_RUNTIME",
}


def _faberloom_v2_files(project_root: Path) -> dict[str, Path]:
    return {p.stem: p for p in (project_root / "faberloom").glob("SKILL_*.md")}


def _extract_fbl(skill_md: str) -> dict[str, Any]:
    from app.src.skills import compile_skill_md_v2

    manifest = compile_skill_md_v2(skill_md)
    return dict(manifest.get("metadata", {}).get("fbl", {}))


def _external_outputs_require_approval(fbl: dict[str, Any]) -> bool:
    contract = fbl.get("contract", {}) or {}
    for output in contract.get("outputs", []):
        if not isinstance(output, dict):
            continue
        destination = str(output.get("destination", "")).strip()
        if destination and not destination.startswith(("drafts/", "logs/", "internal/")):
            if not output.get("requires_human_approval"):
                return False
    return True


@pytest.fixture()
def project_root() -> Path:
    """Return the repository root (parent of app/)."""

    return Path(__file__).resolve().parents[2]


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.storage import reset_object_store

    reset_object_store()
    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _admin_headers() -> dict[str, str]:
    return {
        "x-tenant-id": "default",
        "x-user-id": "tester",
        "x-actor-id": "tester",
        "x-actor-role": "admin",
    }


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces", headers=_admin_headers())
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def test_migrable_v2_files_exist(project_root: Path) -> None:
    v2_files = _faberloom_v2_files(project_root)
    for skill_id in MIGRABLE_LEGACY_IDS:
        assert skill_id in v2_files, f"Missing v2 file for {skill_id}"


def test_deprecated_skills_have_no_v2_file(project_root: Path) -> None:
    v2_files = _faberloom_v2_files(project_root)
    for skill_id in DEPRECATED_LEGACY_IDS:
        assert skill_id not in v2_files, f"Deprecated {skill_id} should not have a v2 file"


def test_migrable_v2_files_compile(project_root: Path) -> None:
    from app.src.skills import compile_skill_md_v2

    v2_files = _faberloom_v2_files(project_root)
    for skill_id in sorted(MIGRABLE_LEGACY_IDS):
        text = v2_files[skill_id].read_text(encoding="utf-8")
        manifest = compile_skill_md_v2(text)
        fbl = manifest["metadata"]["fbl"]
        assert fbl["id"] == skill_id
        assert fbl["status"] == "SHADOW"
        assert fbl["type"] in {"agent", "skill_package"}
        assert fbl["architectural_archetype"] in {
            "classifier",
            "validator",
            "generator",
            "formatter",
            "triage",
            "skill_package",
        }


def test_migrable_v2_no_auto_apply(project_root: Path) -> None:
    v2_files = _faberloom_v2_files(project_root)
    for skill_id in sorted(MIGRABLE_LEGACY_IDS):
        text = v2_files[skill_id].read_text(encoding="utf-8")
        fbl = _extract_fbl(text)
        memory = fbl.get("memory", {}) or {}
        learning = memory.get("learning_consolidation", {}) or {}
        assert learning.get("auto_apply") is not True, f"{skill_id} must not auto_apply"


def test_migrable_v2_external_outputs_require_approval(project_root: Path) -> None:
    v2_files = _faberloom_v2_files(project_root)
    for skill_id in sorted(MIGRABLE_LEGACY_IDS):
        text = v2_files[skill_id].read_text(encoding="utf-8")
        fbl = _extract_fbl(text)
        assert _external_outputs_require_approval(fbl), f"{skill_id} has unapproved external output"


def test_imported_routines_are_shadow_and_unapproved(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    catalog = client.get("/api/faberloom/catalog").json()
    legacy_items = [item for item in catalog if item["file"].startswith("SKILL_") and item["file"].removesuffix(".md") in MIGRABLE_LEGACY_IDS]
    assert len(legacy_items) == len(MIGRABLE_LEGACY_IDS), "All migrable legacy skills must appear in catalog"

    item_ids = [item["id"] for item in legacy_items]
    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/import-faberloom",
        json={"imports": item_ids},
        headers=_admin_headers(),
    )
    assert response.status_code == 200, response.text
    imported = response.json()
    assert len(imported) == len(MIGRABLE_LEGACY_IDS)

    for routine in imported:
        assert routine["is_active"] == 0
        assert routine["approved_by"] is None
        assert routine["category"] == "skill"
        fbl = _extract_fbl(routine["skill_md"])
        assert fbl["status"] == "SHADOW"
        assert _external_outputs_require_approval(fbl)


def test_deprecated_skills_not_in_catalog_as_executable(client: TestClient, project_root: Path) -> None:
    catalog = client.get("/api/faberloom/catalog").json()
    catalog_files = {item["file"] for item in catalog}
    for skill_id in DEPRECATED_LEGACY_IDS:
        assert f"{skill_id}.md" not in catalog_files, f"Deprecated {skill_id} should not be importable"
