"""Fail-closed auto dispatcher for E2-4.

Chains multiple model calls by capability, respecting workspace policy, budget,
max steps, and local-only constraints.
"""

from __future__ import annotations

import base64
import json
import re
from typing import Any

from ..context import Context
from ..db import sum_workspace_usage_cost
from ..ledger import (
    check_chain_budget,
    list_chain_steps,
    record_step,
    start_chain,
    sum_chain_cost,
)
from ..router.cost import estimate_cost
from ..router.engine import Router
from ..router.models import CompletionRequest
from ..router.providers import ProviderConfig, ProviderError, StubImageProvider
from ..router.registry import build_router
from .catalog import has_catalog_capability, resolve_model_for_capability
from .pdf_images import extract_pdf_text_and_images


class NoCapacityError(RuntimeError):
    """Raised when the dispatcher cannot satisfy a required capability."""


class AutoDispatcherError(RuntimeError):
    """Raised for policy or runtime errors in the auto dispatcher."""


def _attachment_bytes(data: Any) -> bytes:
    """Normalize attachment data to bytes, base64-decoding PDF payloads."""
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        try:
            decoded = base64.b64decode(data, validate=False)
            if decoded.startswith(b"%PDF"):
                return decoded
        except Exception:
            pass
        return data.encode("utf-8", errors="ignore")
    return b""


def run_auto_chain(
    ctx: Context,
    conn: Any,
    *,
    chat_id: str,
    user_request: str,
    attachments: list[dict[str, Any]] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run an auto-routed chain for a chat request.

    Returns a dict with:
        - content: final assistant content
        - provider_slug: provider of the final step
        - model: model of the final step
        - input_tokens, output_tokens, cost_usd, duration_ms: totals across steps
        - chain_id
        - steps: list of {provider_slug, model, cost_usd, capability}
    """

    from ..routing.policy import is_auto_mode_allowed

    if not is_auto_mode_allowed(ctx, conn):
        raise AutoDispatcherError("Auto mode is not enabled for this workspace")

    if policy is None:
        from ..db import get_routing_policy

        policy = get_routing_policy(ctx, conn)

    if not has_catalog_capability(ctx, conn, "text", local_only=policy.get("require_local_only", False)):
        raise NoCapacityError("No text model available in workspace catalog")

    max_steps = policy.get("max_auto_steps", 3)
    budget_cap = policy.get("budget_cap_usd", 5.0)

    attachments = attachments or []
    chain_id = start_chain(ctx, conn, chat_id=chat_id, kind="auto")

    # Extract PDF text/images when present.
    pdf_texts: list[str] = []
    pdf_image_count = 0
    for att in attachments:
        if att.get("mime_type") == "application/pdf" or att.get("filename", "").lower().endswith(".pdf"):
            data = _attachment_bytes(att.get("data", b""))
            extracted = extract_pdf_text_and_images(data)
            pdf_texts.append(extracted["text"])
            pdf_image_count += len(extracted.get("page_images", []))

    combined_context = "\n\n".join(pdf_texts).strip()
    plan = _build_plan(
        ctx,
        conn,
        user_request=user_request,
        pdf_context=combined_context,
        pdf_image_count=pdf_image_count,
        policy=policy,
        budget_cap=budget_cap,
    )

    if len(plan) > max_steps:
        plan = plan[:max_steps]

    accumulated: dict[str, Any] = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "duration_ms": 0,
        "steps": [],
    }
    last_result: dict[str, Any] | None = None

    for step_index, step in enumerate(plan):
        capability = step["capability"]
        complexity = step.get("complexity", _estimate_complexity(user_request))
        spent = sum_chain_cost(ctx, conn, chain_id)
        remaining = budget_cap - spent
        if remaining <= 0:
            raise NoCapacityError(f"Budget cap ${budget_cap:.2f} exceeded after {step_index} steps")

        entry = resolve_model_for_capability(
            ctx,
            conn,
            capability,
            budget_remaining=remaining,
            policy=policy,
            complexity=complexity,
        )

        step_input = _render_step_input(
            step=step,
            user_request=user_request,
            pdf_context=combined_context,
            previous_result=last_result,
        )

        result = _execute_step(
            ctx,
            conn,
            entry=entry,
            step_input=step_input,
            policy=policy,
        )

        # Enforce workspace budget against actual step cost.
        if sum_chain_cost(ctx, conn, chain_id) + result.get("cost_usd", 0.0) > budget_cap:
            raise NoCapacityError(
                f"Workspace budget cap ${budget_cap:.2f} would be exceeded by this step"
            )

        step_record = record_step(
            ctx,
            conn,
            chain_id=chain_id,
            step_index=step_index,
            result=result,
            chat_id=chat_id,
            capability=capability,
            request_json={"capability": capability, "input_preview": step_input[:500]},
            response_json={"content_preview": str(result.get("content", result.get("output", "")))[:500]},
        )

        accumulated["input_tokens"] += result.get("input_tokens", 0)
        accumulated["output_tokens"] += result.get("output_tokens", 0)
        accumulated["cost_usd"] += result.get("cost_usd", 0.0)
        accumulated["duration_ms"] += result.get("duration_ms", 0)
        accumulated["steps"].append(
            {
                "step_index": step_index,
                "provider_slug": result.get("provider_slug", entry["provider_slug"]),
                "model": result.get("model", entry["model"]),
                "capability": capability,
                "cost_usd": result.get("cost_usd", 0.0),
                "step_record_id": step_record.get("id"),
            }
        )
        last_result = result

    final_content = _build_final_content(
        user_request=user_request,
        plan=plan,
        last_result=last_result,
        pdf_context=combined_context,
    )

    return {
        "content": final_content,
        "provider_slug": last_result.get("provider_slug", "router") if last_result else "router",
        "model": last_result.get("model", "unknown") if last_result else "unknown",
        "input_tokens": accumulated["input_tokens"],
        "output_tokens": accumulated["output_tokens"],
        "cost_usd": round(accumulated["cost_usd"], 8),
        "duration_ms": accumulated["duration_ms"],
        "chain_id": chain_id,
        "steps": accumulated["steps"],
    }


def _build_plan(
    ctx: Context,
    conn: Any,
    *,
    user_request: str,
    pdf_context: str,
    pdf_image_count: int,
    policy: dict[str, Any],
    budget_cap: float,
) -> list[dict[str, str]]:
    """Decide which capabilities to invoke and in what order."""

    request_lower = user_request.lower()
    wants_image = any(k in request_lower for k in ("imagen", "image", "imágen", "genera una imagen", "dibuja"))

    # Canonical PDF -> summary -> image shortcut.
    if pdf_context and wants_image:
        plan: list[dict[str, str]] = [
            {"capability": "text", "task": "summarize_pdf", "prompt": "Summarize the PDF in one paragraph.", "complexity": "medium"},
        ]
        if has_catalog_capability(ctx, conn, "image_gen", local_only=policy.get("require_local_only", False)):
            plan.append({"capability": "image_gen", "task": "generate_image", "prompt": "Generate an image based on the summary.", "complexity": "medium"})
        else:
            raise NoCapacityError("No image_gen model available in workspace catalog")
        return plan

    # General planner using the cheapest available text model so the plan itself
    # does not consume the auto-routing budget.
    prompt = _planner_prompt(user_request, pdf_context, pdf_image_count)
    spent = sum_workspace_usage_cost(ctx, conn)
    remaining = budget_cap - spent
    try:
        planner_entry = resolve_model_for_capability(
            ctx,
            conn,
            "cheap",
            budget_remaining=remaining,
            policy=policy,
            local_only=policy.get("require_local_only", False),
        )
    except ValueError:
        planner_entry = resolve_model_for_capability(
            ctx,
            conn,
            "text",
            budget_remaining=remaining,
            policy=policy,
            complexity="low",
            local_only=policy.get("require_local_only", False),
        )

    router = build_router(budget_cap_usd=policy.get("budget_cap_usd"))
    planner_provider = router.providers.get(planner_entry["provider_slug"])
    if planner_provider is None:
        raise NoCapacityError(f"Planner provider {planner_entry['provider_slug']} is not available")

    completion_request = CompletionRequest(
        messages=[{"role": "user", "content": prompt}],
        model=planner_entry["model"],
        provider_slug=planner_entry["provider_slug"],
        temperature=0.2,
        max_tokens=1024,
        spent_usd=spent,
    )
    try:
        result = planner_provider.complete(completion_request)
    except ProviderError as exc:
        raise NoCapacityError(f"Planner failed: {exc}") from exc

    raw = result.content
    try:
        plan_data = json.loads(_extract_json(raw))
        steps = plan_data.get("steps", [])
        if not isinstance(steps, list):
            raise ValueError("plan steps not a list")
        validated = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            capability = str(step.get("capability", "text")).lower()
            complexity = str(step.get("complexity", _estimate_complexity(user_request))).lower()
            if complexity not in {"low", "medium", "high"}:
                complexity = _estimate_complexity(user_request)
            validated.append(
                {
                    "capability": capability,
                    "task": str(step.get("task", "answer")),
                    "prompt": str(step.get("prompt", user_request)),
                    "complexity": complexity,
                }
            )
        if validated:
            return validated
    except Exception:
        pass

    # Fallback: single text answer.
    return [{
        "capability": "text",
        "task": "answer",
        "prompt": user_request,
        "complexity": _estimate_complexity(user_request),
    }]


def _planner_prompt(user_request: str, pdf_context: str, pdf_image_count: int) -> str:
    parts = [
        (
            "You are a routing planner. Respond ONLY with a JSON object: "
            '{"steps": [{"capability": "text"|"image_gen", "task": "...", "prompt": "...", '
            '"complexity": "low"|"medium"|"high"}]}. '
            "Use capability 'image_gen' only if the user explicitly asks for an image. "
            "Set complexity to 'low' for greetings, short factual answers or simple chat. "
            "Set complexity to 'high' for analysis, comparison, reasoning, code, design or long documents. "
            "Use at most 3 steps. Do not include explanations outside the JSON."
        ),
        f"User request: {user_request}",
    ]
    if pdf_context:
        parts.append(f"PDF text context ({pdf_image_count} pages): {pdf_context[:4000]}")
    return "\n\n".join(parts)


def _extract_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    return text


# Simple, local heuristic for task complexity. Keeps auto-routing deterministic
# and independent of cloud calls. The planner can override this per-step.
_COMPLEXITY_MARKERS: dict[str, list[str]] = {
    "low": [
        "hola", "como estas", "que tal", "buenos dias", "buenas tardes",
        "si/no", "si o no", "una palabra", "definicion corta", "resumen corto",
    ],
    "high": [
        "analiza", "analisis", "compara", "comparacion", "comparativa",
        "razona", "razonamiento", "explica detalladamente", "en detalle",
        "codigo", "programa", "implementa", "diseña", "estrategia",
        "investiga", "investigacion", "sintesis", "resumen ejecutivo",
        "proyecto", "propuesta", "plan", "modelo de negocio", "caso de estudio",
    ],
}


def _estimate_complexity(text: str) -> str:
    lowered = text.lower()
    words = len(text.split())
    if words < 10 and any(marker in lowered for marker in _COMPLEXITY_MARKERS["low"]):
        return "low"
    if any(marker in lowered for marker in _COMPLEXITY_MARKERS["high"]) or words > 80:
        return "high"
    return "medium"


def _render_step_input(
    *,
    step: dict[str, str],
    user_request: str,
    pdf_context: str,
    previous_result: dict[str, Any] | None,
) -> str:
    if step["task"] == "summarize_pdf" and pdf_context:
        return f"Summarize the following PDF text in one paragraph:\n\n{pdf_context[:6000]}"
    if step["task"] == "generate_image" and previous_result:
        prior = str(previous_result.get("content", previous_result.get("output", "")))
        return f"Generate an image that illustrates this summary: {prior[:1000]}"
    if pdf_context:
        return f"Context from PDF:\n\n{pdf_context[:6000]}\n\nUser request: {user_request}\n\n{step['prompt']}"
    return f"User request: {user_request}\n\n{step['prompt']}"


def _execute_step(
    ctx: Context,
    conn: Any,
    *,
    entry: dict[str, Any],
    step_input: str,
    policy: dict[str, Any],
) -> dict[str, Any]:
    provider_slug = entry["provider_slug"]
    model = entry["model"]

    if provider_slug == "stub":
        provider = StubImageProvider(
            ProviderConfig(
                provider_slug="stub",
                api_key=None,
                model_default=model,
                priority=entry["priority"],
                is_enabled=True,
            )
        )
        request = CompletionRequest(
            messages=[{"role": "user", "content": step_input}],
            model=model,
            provider_slug=provider_slug,
            temperature=0.7,
            max_tokens=1024,
            spent_usd=sum_workspace_usage_cost(ctx, conn),
        )
        try:
            comp = provider.complete(request)
        except ProviderError as exc:
            raise NoCapacityError(f"Stub image provider failed: {exc}") from exc
        return {
            "status": "succeeded",
            "content": comp.content,
            "output": {"image_url": comp.content},
            "provider_slug": comp.provider_slug,
            "model": comp.model,
            "input_tokens": comp.input_tokens,
            "output_tokens": comp.output_tokens,
            "cost_usd": comp.cost_usd,
            "duration_ms": comp.duration_ms,
        }

    router = build_router(budget_cap_usd=policy.get("budget_cap_usd"))
    provider = router.providers.get(provider_slug)

    from ..router.engine import _estimate_input_tokens, DEFAULT_ESTIMATED_OUTPUT_TOKENS

    spent = sum_workspace_usage_cost(ctx, conn)
    budget_cap = policy.get("budget_cap_usd", 5.0)
    request = CompletionRequest(
        messages=[{"role": "user", "content": step_input}],
        model=model,
        provider_slug=provider_slug,
        temperature=0.7,
        max_tokens=1024,
        spent_usd=spent,
    )

    estimated_cost = estimate_cost(
        model,
        _estimate_input_tokens(request.messages),
        request.max_tokens or DEFAULT_ESTIMATED_OUTPUT_TOKENS,
    )
    if spent + estimated_cost > budget_cap:
        raise NoCapacityError(
            f"Step estimated cost exceeds workspace budget cap ${budget_cap:.2f}"
        )

    try:
        if provider is not None:
            # Honor the auto-routing decision: use the selected provider/model directly.
            comp = provider.complete(request)
        else:
            # If the selected provider is not currently configured (e.g. stale catalog
            # entry), fall back to the router's normal ordered path.
            comp = router.complete(request)
    except ProviderError as exc:
        raise NoCapacityError(f"Step failed for {provider_slug}/{model}: {exc}") from exc

    actual_total = spent + comp.cost_usd
    if actual_total > budget_cap:
        raise NoCapacityError(
            f"Step actual cost exceeds workspace budget cap ${budget_cap:.2f}"
        )

    return {
        "status": "succeeded",
        "content": comp.content,
        "output": {"text": comp.content},
        "provider_slug": comp.provider_slug,
        "model": comp.model,
        "input_tokens": comp.input_tokens,
        "output_tokens": comp.output_tokens,
        "cost_usd": comp.cost_usd,
        "duration_ms": comp.duration_ms,
    }


def _build_final_content(
    *,
    user_request: str,
    plan: list[dict[str, str]],
    last_result: dict[str, Any] | None,
    pdf_context: str,
) -> str:
    if last_result is None:
        return "No result produced."

    last_capability = plan[-1]["capability"] if plan else "text"
    content = str(last_result.get("content", ""))

    if last_capability == "image_gen":
        # Find the summary from the previous text step if available.
        summary = ""
        if len(plan) >= 2 and plan[-2]["capability"] == "text":
            summary = content
        return f"{summary}\n\nGenerated image: {content}".strip()

    return content
