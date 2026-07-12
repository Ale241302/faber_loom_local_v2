"""Fail-closed auto dispatcher for E2-4 / E4-0.

Chains multiple model calls by capability, respecting workspace policy, budget,
max steps, and local-only constraints. In E4-0 the planning and execution phases
were separated so the same planner can run in ``shadow`` mode without side effects.
"""

from __future__ import annotations

import base64
import json
import logging
import re
import time
from typing import Any

from ..context import Context
from ..config_cascade import resolve as cascade_resolve
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
from .dispatcher_base import DispatchPlan, DispatchStep, TaskDispatcher, step_id_for_index
from .pdf_images import extract_pdf_text_and_images
from ..living_agent.memory import build_memory_context


logger = logging.getLogger(__name__)


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


class NaturalPlanner:
    """Planner that builds a ``DispatchPlan`` from a user request.

    This is the ``natural`` mode planner. It does **not** execute steps; it only
    decides which capabilities to invoke, in what order, and which model should
    run each step according to the F1 tiered routing contract.
    """

    def __init__(
        self,
        *,
        policy: dict[str, Any] | None = None,
        max_steps: int | None = None,
        budget_cap: float | None = None,
    ) -> None:
        self.policy = policy
        self.max_steps = max_steps
        self.budget_cap = budget_cap

    def plan(
        self,
        ctx: Context,
        conn: Any,
        *,
        user_request: str,
        attachments: list[dict[str, Any]],
        policy: dict[str, Any],
    ) -> DispatchPlan:
        """Return a ``DispatchPlan`` without executing any step."""

        max_steps = self.max_steps if self.max_steps is not None else policy.get("max_auto_steps", 3)
        budget_cap = self.budget_cap if self.budget_cap is not None else policy.get("budget_cap_usd", 5.0)

        pdf_texts: list[str] = []
        pdf_image_count = 0
        for att in attachments or []:
            if att.get("mime_type") == "application/pdf" or att.get("filename", "").lower().endswith(".pdf"):
                data = _attachment_bytes(att.get("data", b""))
                extracted = extract_pdf_text_and_images(data)
                pdf_texts.append(extracted["text"])
                pdf_image_count += len(extracted.get("page_images", []))

        combined_context = "\n\n".join(pdf_texts).strip()

        raw_steps = _build_plan(
            ctx,
            conn,
            user_request=user_request,
            pdf_context=combined_context,
            pdf_image_count=pdf_image_count,
            policy=policy,
            budget_cap=budget_cap,
        )

        if len(raw_steps) > max_steps:
            raw_steps = raw_steps[:max_steps]

        dispatch_steps: list[DispatchStep] = []
        est_total_cost = 0.0
        planner_cost = 0.0

        for index, raw in enumerate(raw_steps):
            capability = raw["capability"]
            complexity = raw.get("complexity", _estimate_complexity(user_request))
            step_input = _render_step_input(
                step=raw,
                user_request=user_request,
                pdf_context=combined_context,
                previous_result=None,  # candidates are estimated without execution
            )

            candidates = _list_candidates(
                ctx,
                conn,
                capability=capability,
                complexity=complexity,
                estimated_input_tokens=max(1, len(step_input) // 4),
                budget_remaining=budget_cap,
                policy=policy,
            )

            chosen = candidates[0] if candidates else None
            if chosen is not None:
                est_input = max(len(step_input) // 4, 1000)
                est_cost = (chosen["cost_input_1k"] / 1000) * est_input + (chosen["cost_output_1k"] / 1000) * 1024
                est_total_cost += est_cost

            dispatch_steps.append(
                DispatchStep(
                    step_id=step_id_for_index(index),
                    capability=capability,
                    task=raw["task"],
                    prompt=raw["prompt"],
                    complexity=complexity,
                    model_candidates=candidates,
                    chosen=chosen,
                    reason=f"{complexity} complexity -> " + ("CHEAPEST_FIRST" if complexity == "low" or capability == "cheap" else "BEST_FIRST" if complexity == "high" else "value"),
                    inputs_from=step_id_for_index(index - 1) if index > 0 else None,
                )
            )

        # The planner itself consumed a cheap model; account for that cost.
        planner_cost = policy.get("planner_cost_usd", 0.0)
        if planner_cost == 0.0:
            try:
                cheap = resolve_model_for_capability(
                    ctx,
                    conn,
                    "cheap",
                    budget_remaining=budget_cap,
                    policy=policy,
                    local_only=policy.get("require_local_only", False),
                )
                planner_cost = (cheap["cost_input_1k"] / 1000) * 1500 + (cheap["cost_output_1k"] / 1000) * 512
            except ValueError:
                planner_cost = 0.0

        return DispatchPlan(
            steps=dispatch_steps,
            est_total_cost_usd=round(est_total_cost, 8),
            planner_cost_usd=round(planner_cost, 8),
        )


def execute_plan(
    ctx: Context,
    conn: Any,
    *,
    chat_id: str,
    user_request: str,
    plan: DispatchPlan,
    attachments: list[dict[str, Any]] | None = None,
    policy: dict[str, Any] | None = None,
    image_attachment: dict[str, Any] | None = None,
    chain_id: str | None = None,
) -> dict[str, Any]:
    """Execute a pre-built dispatch plan and return the aggregated result."""

    if policy is None:
        from ..db import get_routing_policy

        policy = get_routing_policy(ctx, conn)

    attachments = attachments or []
    if chain_id is None:
        chain_id = start_chain(ctx, conn, chat_id=chat_id, kind="auto")

    pdf_texts: list[str] = []
    for att in attachments:
        if att.get("mime_type") == "application/pdf" or att.get("filename", "").lower().endswith(".pdf"):
            data = _attachment_bytes(att.get("data", b""))
            extracted = extract_pdf_text_and_images(data)
            pdf_texts.append(extracted["text"])
    combined_context = "\n\n".join(pdf_texts).strip()

    budget_cap = policy.get("budget_cap_usd", 5.0)
    accumulated: dict[str, Any] = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "duration_ms": 0,
        "steps": [],
    }
    last_result: dict[str, Any] | None = None

    for step_index, step in enumerate(plan.steps):
        capability = step.capability
        spent = sum_chain_cost(ctx, conn, chain_id)
        remaining = budget_cap - spent
        if remaining <= 0:
            raise NoCapacityError(f"Budget cap ${budget_cap:.2f} exceeded after {step_index} steps")

        step_input = _render_step_input(
            step={"task": step.task, "prompt": step.prompt, "capability": capability},
            user_request=user_request,
            pdf_context=combined_context,
            previous_result=last_result,
        )

        entry = step.chosen
        if entry is None:
            entry = resolve_model_for_capability(
                ctx,
                conn,
                capability,
                budget_remaining=remaining,
                policy=policy,
                complexity=step.complexity,
                estimated_input_tokens=max(1, len(step_input) // 4),
            )

        result = _execute_step(
            ctx,
            conn,
            entry=entry,
            step_input=step_input,
            policy=policy,
            image_part=image_attachment if capability == "vision" else None,
            capability=capability,
        )

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

        # E4-2: update per-model track record (baseline accepted outcome).
        try:
            from ..living_agent.planner import update_model_track_record

            update_model_track_record(
                ctx,
                conn,
                capability=capability,
                provider_slug=result.get("provider_slug", entry["provider_slug"]),
                model=result.get("model", entry["model"]),
                outcome="accepted",
                cost_usd=result.get("cost_usd", 0.0),
                latency_ms=result.get("duration_ms", 0),
            )
        except Exception:
            logger.exception("Failed to update model track record for step %s", step_index)

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
        plan=[{"capability": s.capability, "task": s.task, "prompt": s.prompt, "complexity": s.complexity} for s in plan.steps],
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


def run_auto_chain(
    ctx: Context,
    conn: Any,
    *,
    chat_id: str,
    user_request: str,
    attachments: list[dict[str, Any]] | None = None,
    policy: dict[str, Any] | None = None,
    image_attachment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run an auto-routed chain for a chat request.

    ``image_attachment`` is an optional multimodal part
    ``{"type": "image", "mime_type": ..., "data_b64": ..., "file_name": ...}``;
    when present the chain starts with a vision-capable step that actually
    sees the image.

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

    # Preserve legacy image-attachment deterministic plan for backwards compatibility.
    if image_attachment is not None:
        if not has_catalog_capability(ctx, conn, "vision", local_only=policy.get("require_local_only", False)):
            raise NoCapacityError("No vision model available in workspace catalog")
        raw_steps: list[dict[str, str]] = [
            {"capability": "vision", "task": "analyze_image", "prompt": user_request, "complexity": _estimate_complexity(user_request)},
        ]
        wants_image = any(
            k in user_request.lower() for k in ("genera una imagen", "generame una imagen", "dibuja", "crea una imagen")
        )
        if wants_image and has_catalog_capability(ctx, conn, "image_gen", local_only=policy.get("require_local_only", False)):
            raw_steps.append({
                "capability": "image_gen",
                "task": "generate_image",
                "prompt": "Generate an image based on the analysis.",
                "complexity": "medium",
            })
        else:
            if wants_image:
                raise NoCapacityError("No image_gen model available in workspace catalog")

        dispatch_steps = [
            DispatchStep(
                step_id=step_id_for_index(i),
                capability=s["capability"],
                task=s["task"],
                prompt=s["prompt"],
                complexity=s["complexity"],
            )
            for i, s in enumerate(raw_steps)
        ]
        plan = DispatchPlan(steps=dispatch_steps)
    else:
        planner = NaturalPlanner(policy=policy)
        plan = planner.plan(
            ctx,
            conn,
            user_request=user_request,
            attachments=attachments or [],
            policy=policy,
        )

    # E4-2 R11: log the natural planner decision with full plan and correlation.
    plan_id: str | None = None
    decision_chain_id: str | None = None
    try:
        from ..living_agent.planner import log_planner_decision

        decision_chain_id = start_chain(ctx, conn, chat_id=chat_id, kind="auto")
        log = log_planner_decision(
            ctx,
            conn,
            mode="natural",
            plan=plan,
            correlation_id=chat_id,
            chain_id=decision_chain_id,
            task_ref=chat_id,
            planner_cost_usd=plan.planner_cost_usd,
        )
        plan_id = log.get("id")
    except Exception:
        logger.exception("Failed to log natural planner decision for chat %s", chat_id)

    # E4-3: run the plan under the task orchestrator (HITL, kill, budget, artifacts).
    from ..living_agent.orchestrator import TaskOrchestrator

    task = TaskOrchestrator(ctx, conn, policy=policy).run_task_from_plan(
        chat_id=chat_id,
        user_request=user_request,
        plan=plan,
        plan_id=plan_id,
        attachments=attachments,
        image_attachment=image_attachment,
        chain_id=decision_chain_id,
    )
    if task.get("status") in {"failed", "killed", "degraded"}:
        raise NoCapacityError(task.get("output_text") or "Agent task did not complete")
    last_step = None
    for s in reversed(task.get("steps", [])):
        if s["status"] == "completed":
            last_step = s
            break

    return {
        "content": task.get("output_text") or "",
        "provider_slug": last_step["provider_slug"] if last_step else "router",
        "model": last_step["model"] if last_step else "unknown",
        "input_tokens": sum(s["input_tokens"] for s in task.get("steps", [])),
        "output_tokens": sum(s["output_tokens"] for s in task.get("steps", [])),
        "cost_usd": round(task.get("cost_total_usd", 0.0), 8),
        "duration_ms": sum(s["duration_ms"] for s in task.get("steps", [])),
        "chain_id": task.get("chain_id") or task.get("id"),
        "task_id": task.get("id"),
        "steps": [
            {
                "step_index": s["step_index"],
                "provider_slug": s["provider_slug"],
                "model": s["model"],
                "capability": s["capability"],
                "cost_usd": s["cost_usd"],
            }
            for s in task.get("steps", [])
        ],
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

    byo_mode = cascade_resolve(conn, ctx, "routing.byo_mode", default="hibrido")
    router = build_router(
        user_id=ctx.user_id,
        tenant_id=ctx.tenant_id,
        budget_cap_usd=policy.get("budget_cap_usd"),
        byo_mode=byo_mode,
    )
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


def _list_candidates(
    ctx: Context,
    conn: Any,
    *,
    capability: str,
    complexity: str,
    estimated_input_tokens: int,
    budget_remaining: float,
    policy: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return scored model candidates for a step without mutating state."""

    from .catalog import (
        DEFAULT_MODEL_CONTEXT_TOKENS,
        DEFAULT_MODEL_QUALITY,
        MODEL_CONTEXT_TOKENS,
        MODEL_QUALITY,
        list_model_catalog,
    )

    candidates = list_model_catalog(
        ctx,
        conn,
        capability=capability,
        local_only=policy.get("require_local_only", False),
        enabled_only=True,
    )

    complexity = (complexity or "medium").lower()
    if complexity not in {"low", "medium", "high"}:
        complexity = "medium"

    result: list[dict[str, Any]] = []
    for entry in candidates:
        est_input = max(estimated_input_tokens, 1000)
        est_output = 1024
        if estimated_input_tokens:
            context_limit = MODEL_CONTEXT_TOKENS.get(entry["model"], DEFAULT_MODEL_CONTEXT_TOKENS)
            if estimated_input_tokens * 1.2 + 1024 > context_limit:
                continue
        est_cost = (entry["cost_input_1k"] / 1000) * est_input + (entry["cost_output_1k"] / 1000) * est_output
        if est_cost > budget_remaining:
            continue
        quality = MODEL_QUALITY.get(entry["model"], DEFAULT_MODEL_QUALITY)
        result.append({
            "provider_slug": entry["provider_slug"],
            "model": entry["model"],
            "est_input_tokens": est_input,
            "est_cost_usd": round(est_cost, 8),
            "quality": quality,
            "cost_input_1k": entry["cost_input_1k"],
            "cost_output_1k": entry["cost_output_1k"],
            "priority": entry.get("priority", 100),
        })

    # Sort using the same scoring logic as resolve_model_for_capability.
    def _sort_key(info: dict[str, Any]) -> tuple[float, float]:
        cost_per_1k = next(
            (e["cost_input_1k"] + e["cost_output_1k"] for e in candidates
             if e["provider_slug"] == info["provider_slug"] and e["model"] == info["model"]),
            0.0,
        )
        quality = info["quality"]
        if complexity == "low":
            return (cost_per_1k, -quality)
        if complexity == "high":
            return (-quality, cost_per_1k)
        return (cost_per_1k / max(quality, 1), cost_per_1k)

    result.sort(key=_sort_key)
    return result


def _planner_prompt(user_request: str, pdf_context: str, pdf_image_count: int) -> str:
    parts = [
        (
            "You are a routing planner. Respond ONLY with a JSON object: "
            '{"steps": [{"capability": "text"|"image_gen", "task": "...", "prompt": "...", '
            '"complexity": "low"|"medium"|"high"}]}. '
            "Use capability 'image_gen' only if the user explicitly asks for an image. "
            "Set complexity to 'low' for greetings, short factual answers or simple chat. "
            "Set complexity to 'high' for analysis, comparison, reasoning, code, design or long documents. "
            "For multi-step plans, mark intermediate extraction/summarization steps as complexity 'low' "
            "(they run on cheaper models) and give the final synthesis/answer step the real task complexity "
            "(it runs on a more capable model and is the one that answers the user). "
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
    prior = ""
    if previous_result is not None:
        prior = str(previous_result.get("content", previous_result.get("output", ""))).strip()

    if step["task"] == "analyze_image":
        return f"User request: {user_request}\n\nResponde considerando la imagen adjunta."
    if step["task"] == "summarize_pdf" and pdf_context:
        return f"Summarize the following PDF text in one paragraph:\n\n{pdf_context[:6000]}"
    if step["task"] == "generate_image" and previous_result:
        return f"Generate an image that illustrates this summary: {prior[:1000]}"
    if pdf_context:
        base = f"Context from PDF:\n\n{pdf_context[:6000]}\n\nUser request: {user_request}\n\n{step['prompt']}"
        if prior:
            base += f"\n\nResultado del paso anterior:\n{prior[:4000]}"
        return base
    base = f"User request: {user_request}\n\n{step['prompt']}"
    if prior:
        base += f"\n\nResultado del paso anterior:\n{prior[:4000]}"
    return base


OPENAI_IMAGE_FLAT_COST_USD = 0.04


def _execute_openai_image_step(
    ctx: Context,
    conn: Any,
    *,
    entry: dict[str, Any],
    prompt: str,
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Generate a real image with the OpenAI Images API and persist it to MinIO.

    El objeto queda en fl-generated (sellado ws-{id}); el content del paso es
    una URL presignada de 1h. Cost ledger usa costo plano por imagen.
    """

    import base64 as _b64
    import time as _time

    start = _time.perf_counter()
    byo_mode = cascade_resolve(conn, ctx, "routing.byo_mode", default="hibrido")
    router = build_router(
        user_id=ctx.user_id,
        tenant_id=ctx.tenant_id,
        budget_cap_usd=policy.get("budget_cap_usd"),
        byo_mode=byo_mode,
    )
    provider = router.providers.get("openai")
    if provider is None or not provider.is_available():
        raise NoCapacityError("OpenAI image provider is not configured")

    spent = sum_workspace_usage_cost(ctx, conn)
    budget_cap = policy.get("budget_cap_usd", 5.0)
    if spent + OPENAI_IMAGE_FLAT_COST_USD > budget_cap:
        raise NoCapacityError(
            f"Image step cost would exceed workspace budget cap ${budget_cap:.2f}"
        )

    try:
        client = provider._build_client()
        response = client.images.generate(
            model=entry["model"],
            prompt=prompt[:3800],
            size="1024x1024",
            n=1,
        )
    except Exception as exc:
        raise NoCapacityError(f"Image generation failed: {exc}") from exc

    datum = response.data[0]
    b64_payload = getattr(datum, "b64_json", None)
    remote_url = getattr(datum, "url", None)

    content_url: str
    object_id: str | None = None
    if b64_payload:
        from ..db import create_generated_object
        from ..storage import get_object_store

        image_bytes = _b64.b64decode(b64_payload)
        file_name = f"imagen-generada-{int(_time.time())}.png"
        object_row = create_generated_object(
            ctx, conn, image_bytes, file_name=file_name, mime_type="image/png"
        )
        object_id = object_row["id"]
        content_url = get_object_store().presigned_download_url(
            object_row["bucket"], object_row["object_key"], expires=3600
        )
    elif remote_url:
        content_url = str(remote_url)
    else:
        raise NoCapacityError("Image generation returned no payload")

    return {
        "status": "succeeded",
        "content": content_url,
        "output": {"image_url": content_url, "object_id": object_id},
        "provider_slug": "openai",
        "model": entry["model"],
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": OPENAI_IMAGE_FLAT_COST_USD,
        "duration_ms": max(0, int((_time.perf_counter() - start) * 1000)),
    }


def _execute_step(
    ctx: Context,
    conn: Any,
    *,
    entry: dict[str, Any],
    step_input: str,
    policy: dict[str, Any],
    image_part: dict[str, Any] | None = None,
    capability: str = "text",
) -> dict[str, Any]:
    provider_slug = entry["provider_slug"]
    model = entry["model"]

    if capability == "image_gen" and provider_slug == "openai":
        return _execute_openai_image_step(ctx, conn, entry=entry, prompt=step_input, policy=policy)

    # Contenido multimodal cuando el paso lleva imagen (capability vision).
    step_content: Any = step_input
    if image_part is not None:
        step_content = [{"type": "text", "text": step_input}, image_part]

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
            messages=[{"role": "user", "content": step_content}],
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

    byo_mode = cascade_resolve(conn, ctx, "routing.byo_mode", default="hibrido")
    router = build_router(
        user_id=ctx.user_id,
        tenant_id=ctx.tenant_id,
        budget_cap_usd=policy.get("budget_cap_usd"),
        byo_mode=byo_mode,
    )
    provider = router.providers.get(provider_slug)

    from ..router.engine import _estimate_input_tokens, DEFAULT_ESTIMATED_OUTPUT_TOKENS

    spent = sum_workspace_usage_cost(ctx, conn)
    budget_cap = policy.get("budget_cap_usd", 5.0)
    messages: list[dict[str, Any]] = []
    if ctx.user_id:
        memory_context = build_memory_context(ctx, conn, query=step_input)
        if memory_context:
            messages.append({"role": "system", "content": memory_context})
    messages.append({"role": "user", "content": step_content})

    request = CompletionRequest(
        messages=messages,
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
