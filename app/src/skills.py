"""SL3a: SKILL.md parser/validator and skill executor."""

from __future__ import annotations

import json
import re
from typing import Any

import jsonschema
import yaml

from .router.engine import BudgetExceeded, NoAllowedModel, Router
from .router.models import CompletionRequest
from .router.providers import ProviderError


def _detect_dangerous(skill_md: str) -> list[str]:
    """Return a list of dangerous patterns found in SKILL.md content."""

    dangers: list[str] = []
    lowered = skill_md.lower()

    if "<script" in lowered:
        dangers.append("HTML <script> tag")
    if re.search(r"javascript\s*:", lowered):
        dangers.append("javascript: scheme")
    # Detect Python import statements (e.g. "import os", "from os import").
    if re.search(r"(?:^|\s)import\s+", skill_md):
        dangers.append("Python import statement")
    if re.search(r"\beval\s*\(", skill_md):
        dangers.append("eval() call")
    # Excel formula injection: a line starting with = and containing '!'
    for line in skill_md.splitlines():
        stripped = line.strip()
        if stripped.startswith("=") and "!" in stripped:
            dangers.append("Excel formula injection")
            break

    return dangers


def _extract_frontmatter(skill_md: str) -> tuple[dict[str, Any], str]:
    """Split a SKILL.md into YAML frontmatter and body."""

    if not skill_md.startswith("---"):
        return {}, skill_md

    parts = skill_md.split("---", 2)
    if len(parts) < 3:
        return {}, skill_md

    frontmatter_text = parts[1].strip()
    body = parts[2].strip()

    try:
        frontmatter = yaml.safe_load(frontmatter_text) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid SKILL.md frontmatter: {exc}") from exc

    if not isinstance(frontmatter, dict):
        raise ValueError("Invalid SKILL.md frontmatter: must be a mapping")

    return frontmatter, body


def compile_skill_md(skill_md: str) -> dict[str, Any]:
    """Parse and validate a SKILL.md document into a normalized skill dict."""

    dangers = _detect_dangerous(skill_md)
    if dangers:
        raise ValueError("Unsafe SKILL.md content: " + "; ".join(dangers))

    frontmatter, body = _extract_frontmatter(skill_md)

    schema_output = frontmatter.get("schema_output", {})
    if isinstance(schema_output, str):
        try:
            schema_output = json.loads(schema_output)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid schema_output JSON: {exc}") from exc

    tools = frontmatter.get("tools", [])
    if isinstance(tools, str):
        try:
            tools = json.loads(tools)
        except json.JSONDecodeError:
            tools = []
    if not isinstance(tools, list):
        tools = []

    triggers = frontmatter.get("triggers", [])
    if isinstance(triggers, str):
        try:
            triggers = json.loads(triggers)
        except json.JSONDecodeError:
            triggers = []
    if not isinstance(triggers, list):
        triggers = []

    return {
        "name": str(frontmatter.get("name", "")).strip(),
        "persona": str(frontmatter.get("persona", "")).strip(),
        "tools": tools,
        "schema_output": schema_output if isinstance(schema_output, dict) else {},
        "triggers": triggers,
        "instructions": body,
        "skill_md": skill_md,
    }


def _tool_is_allowlisted(tool: str, allowlist: list[str]) -> bool:
    """Return True when ``tool`` is allowed by the workspace allowlist."""

    if not allowlist:
        return False
    if "*" in allowlist:
        return True
    return tool in allowlist


def skill_requires_hitl(skill: dict[str, Any], tools_allowlist: list[str]) -> bool:
    """Return True when the skill must stop for human confirmation.

    HITL is required when:
        - a requested tool is not in the routine allowlist, or
        - the output schema explicitly asks for confirmation.
    """

    for tool in skill.get("tools", []):
        if not _tool_is_allowlisted(tool, tools_allowlist):
            return True

    schema_output = skill.get("schema_output", {})
    if isinstance(schema_output, dict) and schema_output.get("requires_confirmation"):
        return True

    return False


def _strip_code_fences(text: str) -> str:
    """Remove Markdown JSON fences if the model wrapped the output."""

    text = text.strip()
    fence_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return text


def _build_skill_messages(
    skill: dict[str, Any],
    input_json: dict[str, Any],
) -> list[dict[str, str]]:
    """Build provider-compatible messages from the skill contract."""

    system_parts: list[str] = []
    if skill.get("persona"):
        system_parts.append(skill["persona"])
    system_parts.append(
        "You are a structured skill. Follow the instructions exactly and answer "
        "with a single JSON object that validates against the provided schema."
    )
    if skill.get("instructions"):
        system_parts.append(skill["instructions"])

    schema_output = skill.get("schema_output", {})
    if schema_output:
        system_parts.append(
            "Output schema:\n" + json.dumps(schema_output, ensure_ascii=False, indent=2)
        )

    return [
        {"role": "system", "content": "\n\n".join(system_parts)},
        {"role": "user", "content": json.dumps(input_json, ensure_ascii=False)},
    ]


def execute_skill(
    skill: dict[str, Any],
    input_json: dict[str, Any],
    router: Router,
    provider_slug: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Run a compiled skill through the provider router.

    Returns a dict with:
        - status: "succeeded" | "failed" | "requires_hitl"
        - output: dict | None
        - error: str | None
        - provider_slug, model, input_tokens, output_tokens, cost_usd, duration_ms
        - evidence: list[dict[str, Any]]
    """

    if not router.has_available_provider():
        return {
            "status": "failed",
            "output": None,
            "error": "no_providers_configured",
            "provider_slug": "router",
            "model": "none",
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "duration_ms": 0,
            "evidence": [{"reason": "no_providers_configured"}],
        }

    messages = _build_skill_messages(skill, input_json)
    request = CompletionRequest(
        messages=messages,
        provider_slug=provider_slug,
        model=model,
        temperature=0.2,
        max_tokens=1024,
        spent_usd=0.0,
    )

    try:
        result = router.complete(request)
    except (ProviderError, BudgetExceeded, NoAllowedModel) as exc:
        return {
            "status": "failed",
            "output": None,
            "error": str(exc),
            "provider_slug": getattr(exc, "provider_slug", "router"),
            "model": "unknown",
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "duration_ms": 0,
            "evidence": [{"error": str(exc)}],
        }
    except Exception as exc:
        return {
            "status": "failed",
            "output": None,
            "error": f"unexpected_error: {exc}",
            "provider_slug": "router",
            "model": "unknown",
            "input_tokens": 0,
            "output_tokens": 0,
            "cost_usd": 0.0,
            "duration_ms": 0,
            "evidence": [{"error": str(exc)}],
        }

    raw_content = _strip_code_fences(result.content)
    try:
        output = json.loads(raw_content)
        if not isinstance(output, dict):
            raise ValueError("Skill output is not a JSON object")
    except Exception as exc:
        return {
            "status": "failed",
            "output": None,
            "error": f"invalid_json_output: {exc}",
            "provider_slug": result.provider_slug,
            "model": result.model,
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "cost_usd": result.cost_usd,
            "duration_ms": result.duration_ms,
            "evidence": [{"raw_content": raw_content}],
        }

    # Validate output against schema when a non-trivial schema is present.
    schema_output = skill.get("schema_output", {})
    if isinstance(schema_output, dict) and schema_output and schema_output != {}:
        try:
            jsonschema.validate(output, schema_output)
        except jsonschema.ValidationError as exc:
            return {
                "status": "failed",
                "output": None,
                "error": f"schema_validation_failed: {exc.message}",
                "provider_slug": result.provider_slug,
                "model": result.model,
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "cost_usd": result.cost_usd,
                "duration_ms": result.duration_ms,
                "evidence": [{"raw_content": raw_content, "schema_error": exc.message}],
            }

    # Determine whether this run must stop for HITL.
    tools_allowlist = skill.get("tools_allowlist", [])
    status = "requires_hitl" if skill_requires_hitl(skill, tools_allowlist) else "succeeded"

    return {
        "status": status,
        "output": output,
        "error": None,
        "provider_slug": result.provider_slug,
        "model": result.model,
        "input_tokens": result.input_tokens,
        "output_tokens": result.output_tokens,
        "cost_usd": result.cost_usd,
        "duration_ms": result.duration_ms,
        "evidence": [
            {
                "provider_slug": result.provider_slug,
                "model": result.model,
                "raw_content": raw_content,
            }
        ],
    }


def routine_to_skill(routine: dict[str, Any]) -> dict[str, Any]:
    """Re-compile a stored routine row into the skill contract used at runtime.

    The normalized ``tools_allowlist`` column is authoritative for HITL decisions;
    the SKILL.md ``tools`` field only declares which tools the skill may request.
    """

    tools_allowlist: list[str] = []
    try:
        parsed = json.loads(routine.get("tools_allowlist", "[]") or "[]")
        if isinstance(parsed, list):
            tools_allowlist = parsed
    except json.JSONDecodeError:
        tools_allowlist = []

    skill_md = routine.get("skill_md", "")
    if skill_md:
        try:
            skill = compile_skill_md(skill_md)
            skill["tools_allowlist"] = tools_allowlist
            return skill
        except ValueError:
            pass

    # Fallback: reconstruct from the normalized columns.
    schema_output: dict[str, Any] = {}
    try:
        schema_output = json.loads(routine.get("schema_output_json", "{}") or "{}")
    except json.JSONDecodeError:
        schema_output = {}

    triggers: list[str] = []
    try:
        triggers = json.loads(routine.get("trigger_json", "[]") or "[]")
    except json.JSONDecodeError:
        triggers = []

    return {
        "name": routine.get("name", ""),
        "persona": routine.get("persona_md", ""),
        "tools": tools_allowlist,
        "tools_allowlist": tools_allowlist,
        "schema_output": schema_output,
        "triggers": triggers,
        "instructions": routine.get("skill_md", ""),
        "skill_md": routine.get("skill_md", ""),
    }


__all__ = [
    "compile_skill_md",
    "execute_skill",
    "routine_to_skill",
    "skill_requires_hitl",
]
