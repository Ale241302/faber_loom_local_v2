"""E3-4 Wave 0: skill compiler v2 fail-closed validation."""

from __future__ import annotations

import pytest

from app.src.skills import compile_skill_md, compile_skill_md_v2


VALID_V2 = """---
name: SKILL_TEST_VALID
description: A valid v2 skill
version: 1.0.0
metadata:
  fbl:
    id: SKILL_TEST_VALID
    type: agent
    architectural_archetype: generator
    domain: TEST
    archetype: routine
    visibility: INTERNAL
    status: SHADOW
    contract:
      outputs:
        - id: output_1
          schema: SCH_TEST
          kind: asset
          destination: drafts/queue
          required: true
          requires_human_approval: true
      schema_lock: strict
    state_machine:
      ref: SCH_STATE_MACHINE_BASIC
    golden_samples:
      - id: GS_001
        validates_outputs: [output_1]
        evaluation_use: reference
    outcome:
      primary: test_metric
      baseline_value: 0
      target_at_60d: "> 0"
    budget:
      usd_monthly: 1
      hard_cap_usd: 5
      kill_switch:
        enabled: true
        trigger_on:
          - consecutive_failures: 3
    autonomy:
      current_level: 0
      target_level: 1
    tenant_scope:
      mode: single
      tenants: [default]
---
Test body.
"""


def test_compile_skill_md_v2_accepts_valid_manifest() -> None:
    manifest = compile_skill_md_v2(VALID_V2)
    assert manifest["name"] == "SKILL_TEST_VALID"
    assert manifest["metadata"]["fbl"]["id"] == "SKILL_TEST_VALID"


def test_compile_skill_md_backwards_compatible_returns_mwt() -> None:
    manifest = compile_skill_md(VALID_V2)
    assert "mwt" in manifest["metadata"]
    assert manifest["metadata"]["mwt"]["id"] == "SKILL_TEST_VALID"


def test_compile_skill_md_v2_rejects_missing_outcome_for_agent() -> None:
    bad = VALID_V2.replace("    outcome:", "    _outcome_ignored:")
    bad = bad.replace("      primary: test_metric", "      _primary_ignored: x")
    with pytest.raises(ValueError, match="MANIFEST_V2_MISSING_OUTCOME"):
        compile_skill_md_v2(bad)


def test_compile_skill_md_v2_rejects_missing_kill_switch() -> None:
    bad = VALID_V2.replace("      kill_switch:", "      _kill_switch_ignored:")
    with pytest.raises(ValueError, match="MANIFEST_V2_MISSING_KILL_SWITCH"):
        compile_skill_md_v2(bad)


def test_compile_skill_md_v2_rejects_missing_golden_samples() -> None:
    bad = VALID_V2.replace("    golden_samples:", "    _golden_samples_ignored:")
    with pytest.raises(ValueError, match="MANIFEST_V2_MISSING_GOLDEN_SAMPLES"):
        compile_skill_md_v2(bad)


def test_compile_skill_md_v2_rejects_auto_apply_true() -> None:
    modified = VALID_V2.replace(
        "    tenant_scope:",
        """    memory:
      learning_consolidation:
        target: SKILL_REFINEMENT
        requires_human_gate: true
        auto_apply: true
    tenant_scope:""",
    )
    with pytest.raises(ValueError, match="MANIFEST_V2_AUTO_APPLY"):
        compile_skill_md_v2(modified)


def test_compile_skill_md_v2_rejects_e1_blocked_archetype() -> None:
    bad = VALID_V2.replace("architectural_archetype: generator", "architectural_archetype: orchestrator")
    with pytest.raises(ValueError, match="E1_ARCHETYPE_BLOCKED"):
        compile_skill_md_v2(bad)


def test_compile_skill_md_v2_rejects_tools_on_skill_package() -> None:
    modified = VALID_V2.replace("type: agent", "type: skill_package")
    modified = modified.replace("architectural_archetype: generator", "architectural_archetype: skill_package")
    modified = modified.replace("archetype: routine", "archetype: skill_package")
    # Add a tools_mcp section to trigger the rule.
    modified = modified.replace(
        "    contract:",
        "    tools_mcp:\n      - id: some_tool\n    contract:",
    )
    with pytest.raises(ValueError, match="MANIFEST_V2_TOOLS_ON_SKILL_PACKAGE"):
        compile_skill_md_v2(modified)


def test_compile_skill_md_v2_rejects_external_asset_without_approval() -> None:
    bad = VALID_V2.replace("destination: drafts/queue", "destination: public/web")
    bad = bad.replace("requires_human_approval: true", "requires_human_approval: false")
    with pytest.raises(ValueError, match="MANIFEST_V2_ASSET_APPROVAL_REQUIRED"):
        compile_skill_md_v2(bad)


def test_compile_skill_md_v2_legacy_v1_still_works() -> None:
    v1 = """---
name: legacy_skill
persona: Legacy assistant.
tools: []
schema_output: {}
triggers: ["@legacy"]
---
Legacy body.
"""
    manifest = compile_skill_md_v2(v1)
    assert manifest["name"] == "legacy_skill"
    assert manifest["metadata"]["fbl"]["type"] == "skill"
