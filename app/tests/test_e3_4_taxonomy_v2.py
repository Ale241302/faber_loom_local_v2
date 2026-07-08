"""E3-4 Wave 0: taxonomy v2 primitives and dimensions."""

from __future__ import annotations

from app.src.skill_primitives import TAXONOMY_V2


def test_taxonomy_v2_declares_p15_p18() -> None:
    assert TAXONOMY_V2["primitives"] == ["P15", "P16", "P17", "P18"]
    assert TAXONOMY_V2["primitive_names"]["P18"] == "capturar_interaccion_informal"
    assert TAXONOMY_V2["primitive_names"]["P16"] == "rastrear_externo"


def test_taxonomy_v2_e1_archetypes() -> None:
    expected = {"classifier", "validator", "generator", "formatter", "triage", "skill_package"}
    assert TAXONOMY_V2["archetypes_e1"] == expected


def test_taxonomy_v2_scope_dimensions() -> None:
    dims = TAXONOMY_V2["unit_of_work_dimensions"]
    assert "tenant_id" in dims
    assert "workspace_id" in dims
    assert "unit_of_work_id" in dims
    assert "data_class" in dims
    assert "action" in dims
