"""E4-3 agent task orchestrator: multi-step natural execution with HITL, kill and budget."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from ..context import Context
from ..db_adapter import transaction
from ..ledger import record_step, start_chain
from ..routing.auto_dispatcher import (
    NoCapacityError,
    _execute_step,
    _render_step_input,
)
from ..routing.dispatcher_base import DispatchPlan, DispatchStep
from .artifacts import load_step_artifact_text, save_step_artifact
from .autonomy import degrade_workspace_if_needed
from .constants import ACE_DEGRADE_OVERRUN_RATIO
from .planner import update_model_track_record
from .tasks import (
    create_task,
    create_task_step,
    get_task,
    is_task_killed,
    refresh_task_cost,
    transition_step,
    transition_task,
)


logger = logging.getLogger(__name__)


# Capabilities that always require human approval before execution (Regla Sagrada).
HITL_CAPABILITIES = {
    "mail_send",
    "smtp_send",
    "invoice_create",
    "payment",
    "whatsapp_send",
    "external_write",
}


def _is_hitl_required(step: DispatchStep) -> bool:
    return step.requires_hitl or step.capability in HITL_CAPABILITIES


def _hitl_token(task_id: str, step_id: str) -> str:
    payload = f"{task_id}:{step_id}:hitl"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _create_hitl_draft(
    ctx: Context,
    conn: Any,
    task_id: str,
    step_row: dict[str, Any],
) -> str:
    """Create a WorkLoom draft representing the proposed external action.

    Returns the draft id.
    """

    from ..kb import insert_draft

    body = (
        f"**Acción pendiente de aprobación**\n\n"
        f"- Tarea: `{task_id}`\n"
        f"- Paso {step_row['step_index']}: `{step_row['step_id']}`\n"
        f"- Capability: `{step_row['capability']}`\n"
        f"- Prompt: {step_row['prompt'] or '(none)'}\n\n"
        f"Aprobá esta acción para continuar la ejecución del agente."
    )
    draft = insert_draft(
        ctx,
        conn,
        chat_id=None,
        task=f"agent_task:{task_id}:step:{step_row['id']}",
        subject=f"Aprobación requerida: paso {step_row['step_id']}",
        body_md=body,
        hard_facts=[],
        sources=[],
        blockers=[],
        warnings=[],
        requires_confirmation=True,
        status="pending_approval",
        source_version="v1",
    )
    return draft["id"]


def _build_dispatch_step_from_row(row: dict[str, Any]) -> DispatchStep:
    """Reconstruct a minimal DispatchStep from an agent_task_step row."""

    return DispatchStep(
        step_id=row["step_id"],
        capability=row["capability"],
        task=row["task"] or "",
        prompt=row["prompt"] or "",
        complexity="medium",
        model_candidates=[],
        chosen=None,
        reason="reconstructed_from_task",
        inputs_from=None,
        requires_hitl=False,
    )


class TaskOrchestrator:
    """Executes a DispatchPlan as a resumable, auditable agent task."""

    def __init__(
        self,
        ctx: Context,
        conn: Any,
        policy: dict[str, Any] | None = None,
    ) -> None:
        self.ctx = ctx
        self.conn = conn
        self.policy = policy
        self._chain_id: str | None = None

    def _policy(self) -> dict[str, Any]:
        if self.policy is None:
            from ..db import get_routing_policy

            self.policy = get_routing_policy(self.ctx, self.conn)
        return self.policy

    def run_task_from_plan(
        self,
        *,
        chat_id: str | None,
        user_request: str,
        plan: DispatchPlan,
        plan_id: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
        image_attachment: dict[str, Any] | None = None,
        chain_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a task from an existing plan and run it to completion or HITL pause."""

        policy = self._policy()
        budget_cap = policy.get("budget_cap_usd", 5.0)

        task = create_task(
            self.ctx,
            self.conn,
            workspace_id=self.ctx.require_scoped_workspace(),
            chat_id=chat_id,
            plan_id=plan_id,
            user_request=user_request,
            budget_cap_usd=budget_cap,
            est_cost_usd=plan.est_total_cost_usd,
            status="planned",
        )
        task_id = task["id"]

        step_rows: list[dict[str, Any]] = []
        for index, step in enumerate(plan.steps):
            step_row = create_task_step(
                self.ctx,
                self.conn,
                task_id=task_id,
                step_index=index,
                step_id=step.step_id,
                capability=step.capability,
                task=step.task,
                prompt=step.prompt,
                provider_slug=step.chosen["provider_slug"] if step.chosen else None,
                model=step.chosen["model"] if step.chosen else None,
                status="pending",
            )
            step_rows.append(step_row)

        transition_task(self.ctx, self.conn, task_id, "running")
        result = self._run_steps(
            task_id=task_id,
            chat_id=chat_id,
            user_request=user_request,
            plan=plan,
            step_rows=step_rows,
            attachments=attachments,
            image_attachment=image_attachment,
            start_from=0,
            chain_id=chain_id,
        )
        result["chain_id"] = self._chain_id
        return result

    def _run_steps(
        self,
        *,
        task_id: str,
        chat_id: str | None,
        user_request: str,
        plan: DispatchPlan,
        step_rows: list[dict[str, Any]],
        attachments: list[dict[str, Any]] | None,
        image_attachment: dict[str, Any] | None,
        start_from: int,
        chain_id: str | None = None,
    ) -> dict[str, Any]:
        policy = self._policy()
        budget_cap = policy.get("budget_cap_usd", 5.0)
        est_cost = plan.est_total_cost_usd

        if chain_id is None:
            chain_id = start_chain(self.ctx, self.conn, chat_id=chat_id, kind="auto")
        self._chain_id = chain_id

        # PDF context is processed fresh for each resume to keep inputs deterministic.
        pdf_texts: list[str] = []
        for att in attachments or []:
            if att.get("mime_type") == "application/pdf" or att.get("filename", "").lower().endswith(".pdf"):
                from ..routing.auto_dispatcher import _attachment_bytes, extract_pdf_text_and_images

                data = _attachment_bytes(att.get("data", b""))
                extracted = extract_pdf_text_and_images(data)
                pdf_texts.append(extracted["text"])
        pdf_context = "\n\n".join(pdf_texts).strip()

        last_output_ref: str | None = None
        last_result: dict[str, Any] | None = None

        for index in range(start_from, len(plan.steps)):
            step = plan.steps[index]
            step_row = step_rows[index]

            # Kill switch checks.
            if is_task_killed(self.ctx, self.conn, task_id):
                transition_step(
                    self.ctx,
                    self.conn,
                    step_row["id"],
                    "skipped",
                    updates={"status_reason": "task_killed"},
                )
                continue

            # Budget pre-check.
            cost_total = refresh_task_cost(self.ctx, self.conn, task_id)
            est_step = step.chosen.get("est_cost_usd", 0.0) if step.chosen else 0.0
            if cost_total + est_step > budget_cap:
                transition_task(
                    self.ctx,
                    self.conn,
                    task_id,
                    "degraded",
                    updates={"output_text": f"Budget cap ${budget_cap:.2f} would be exceeded"},
                )
                transition_step(
                    self.ctx,
                    self.conn,
                    step_row["id"],
                    "failed",
                    updates={"status_reason": "budget_cap_exceeded"},
                )
                _degrade_if_overrun(self.ctx, self.conn, cost_total, est_cost)
                return get_task(self.ctx, self.conn, task_id) or {}

            # HITL pause for external-effect steps.
            if _is_hitl_required(step):
                transition_step(
                    self.ctx,
                    self.conn,
                    step_row["id"],
                    "paused_hitl",
                )
                draft_id = _create_hitl_draft(self.ctx, self.conn, task_id, step_row)
                token = _hitl_token(task_id, step_row["id"])
                transition_task(
                    self.ctx,
                    self.conn,
                    task_id,
                    "paused_hitl",
                    updates={
                        "hitl_step_id": step_row["id"],
                        "hitl_token": token,
                        "output_text": f"Waiting for HITL approval (draft {draft_id})",
                    },
                )
                return get_task(self.ctx, self.conn, task_id) or {}

            # Execute step.
            transition_step(self.ctx, self.conn, step_row["id"], "running")
            try:
                result = self._execute_single_step(
                    step=step,
                    step_row=step_row,
                    user_request=user_request,
                    pdf_context=pdf_context,
                    previous_output_ref=last_output_ref,
                    image_attachment=image_attachment,
                    chain_id=chain_id,
                    task_id=task_id,
                )
            except NoCapacityError as exc:
                reason = str(exc)
                is_budget = "budget" in reason.lower()
                transition_step(
                    self.ctx,
                    self.conn,
                    step_row["id"],
                    "failed",
                    updates={"status_reason": reason},
                )
                transition_task(
                    self.ctx,
                    self.conn,
                    task_id,
                    "degraded" if is_budget else "failed",
                    updates={"output_text": reason},
                )
                if is_budget:
                    _degrade_if_overrun(self.ctx, self.conn, refresh_task_cost(self.ctx, self.conn, task_id), est_cost)
                return get_task(self.ctx, self.conn, task_id) or {}
            except Exception as exc:
                logger.exception("Step %s failed for task %s", step.step_id, task_id)
                transition_step(
                    self.ctx,
                    self.conn,
                    step_row["id"],
                    "failed",
                    updates={"status_reason": str(exc)},
                )
                transition_task(
                    self.ctx,
                    self.conn,
                    task_id,
                    "failed",
                    updates={"output_text": str(exc)},
                )
                return get_task(self.ctx, self.conn, task_id) or {}

            last_result = result
            # Store textual output as artifact for next step.
            content_text = str(result.get("content", result.get("output", "")))
            output_ref = save_step_artifact(self.ctx, self.conn, content_text)
            last_output_ref = output_ref
            transition_step(
                self.ctx,
                self.conn,
                step_row["id"],
                "completed",
                updates={
                    "output_ref": output_ref,
                    "cost_usd": result.get("cost_usd", 0.0),
                    "input_tokens": result.get("input_tokens", 0),
                    "output_tokens": result.get("output_tokens", 0),
                    "duration_ms": result.get("duration_ms", 0),
                    "provider_slug": result.get("provider_slug"),
                    "model": result.get("model"),
                },
            )
            refresh_task_cost(self.ctx, self.conn, task_id)

        # If the task was killed/degraded by a concurrent request, do not finalize as completed.
        if is_task_killed(self.ctx, self.conn, task_id):
            return get_task(self.ctx, self.conn, task_id) or {}

        # Finalize task.
        final_content = self._build_final_content(
            user_request=user_request,
            plan=plan,
            last_result=last_result,
            pdf_context=pdf_context,
        )
        transition_task(
            self.ctx,
            self.conn,
            task_id,
            "completed",
            updates={
                "output_text": final_content,
                "output_ref": last_output_ref,
            },
        )
        cost_total = refresh_task_cost(self.ctx, self.conn, task_id)
        _degrade_if_overrun(self.ctx, self.conn, cost_total, est_cost)
        result = get_task(self.ctx, self.conn, task_id) or {}
        result["chain_id"] = self._chain_id
        return result

    def _execute_single_step(
        self,
        *,
        step: DispatchStep,
        step_row: dict[str, Any],
        user_request: str,
        pdf_context: str,
        previous_output_ref: str | None,
        image_attachment: dict[str, Any] | None,
        chain_id: str,
        task_id: str,
    ) -> dict[str, Any]:
        policy = self._policy()

        previous_result: dict[str, Any] | None = None
        if previous_output_ref is not None:
            prior_text = load_step_artifact_text(self.ctx, self.conn, previous_output_ref)
            previous_result = {"content": prior_text}

        step_input = _render_step_input(
            step={"task": step.task, "prompt": step.prompt, "capability": step.capability},
            user_request=user_request,
            pdf_context=pdf_context,
            previous_result=previous_result,
        )

        entry = step.chosen
        if entry is None:
            from ..routing.catalog import resolve_model_for_capability

            entry = resolve_model_for_capability(
                self.ctx,
                self.conn,
                step.capability,
                budget_remaining=policy.get("budget_cap_usd", 5.0),
                policy=policy,
                complexity=step.complexity,
                estimated_input_tokens=max(1, len(step_input) // 4),
            )

        image_part = image_attachment if step.capability == "vision" else None
        result = _execute_step(
            self.ctx,
            self.conn,
            entry=entry,
            step_input=step_input,
            policy=policy,
            image_part=image_part,
            capability=step.capability,
        )

        record_step(
            self.ctx,
            self.conn,
            chain_id=chain_id,
            step_index=step_row["step_index"],
            result=result,
            chat_id=None,
            capability=step.capability,
            task_id=task_id,
            request_json={"capability": step.capability, "input_preview": step_input[:500]},
            response_json={"content_preview": str(result.get("content", ""))[:500]},
        )

        try:
            update_model_track_record(
                self.ctx,
                self.conn,
                capability=step.capability,
                provider_slug=result.get("provider_slug", entry["provider_slug"]),
                model=result.get("model", entry["model"]),
                outcome="accepted",
                cost_usd=result.get("cost_usd", 0.0),
                latency_ms=result.get("duration_ms", 0),
            )
        except Exception:
            logger.exception("Failed to update track record for task %s step %s", task_id, step.step_id)

        return result

    def _build_final_content(
        self,
        *,
        user_request: str,
        plan: DispatchPlan,
        last_result: dict[str, Any] | None,
        pdf_context: str,
    ) -> str:
        from ..routing.auto_dispatcher import _build_final_content

        return _build_final_content(
            user_request=user_request,
            plan=[{"capability": s.capability, "task": s.task, "prompt": s.prompt, "complexity": s.complexity} for s in plan.steps],
            last_result=last_result,
            pdf_context=pdf_context,
        )

    def approve_hitl_step(
        self,
        task_id: str,
        confirmation_token: str,
    ) -> dict[str, Any]:
        """Approve a paused HITL step and continue execution."""

        task = get_task(self.ctx, self.conn, task_id, include_steps=True)
        if task is None:
            raise ValueError("Task not found")
        if task["status"] != "paused_hitl":
            raise ValueError(f"Task is not paused for HITL (status={task['status']})")
        if task["hitl_token"] != confirmation_token:
            raise PermissionError("Invalid confirmation token")

        hitl_step_id = task["hitl_step_id"]
        step_rows = task["steps"]
        hitl_index = next((i for i, s in enumerate(step_rows) if s["id"] == hitl_step_id), -1)
        if hitl_index < 0:
            raise ValueError("HITL step not found")

        # Mark the HITL step as completed (the external action was approved via draft).
        transition_step(
            self.ctx,
            self.conn,
            hitl_step_id,
            "completed",
            updates={
                "status_reason": "hitl_approved",
                "output_text": "Approved via HITL",
            },
        )

        # Reconstruct remaining steps and continue.
        remaining_steps = [_build_dispatch_step_from_row(r) for r in step_rows[hitl_index + 1 :]]
        if not remaining_steps:
            transition_task(
                self.ctx,
                self.conn,
                task_id,
                "completed",
                updates={"output_text": "Task completed after HITL approval"},
            )
            return get_task(self.ctx, self.conn, task_id) or {}

        transition_task(
            self.ctx,
            self.conn,
            task_id,
            "running",
            updates={
                "hitl_step_id": None,
                "hitl_token": None,
            },
        )

        # Build a plan for remaining steps only.
        remaining_plan = DispatchPlan(
            steps=remaining_steps,
            est_total_cost_usd=0.0,
            planner_cost_usd=0.0,
        )
        return self._run_steps(
            task_id=task_id,
            chat_id=task["chat_id"],
            user_request=task["user_request"],
            plan=remaining_plan,
            step_rows=step_rows[hitl_index + 1 :],
            attachments=None,
            image_attachment=None,
            start_from=0,
        )

    def reject_hitl_step(
        self,
        task_id: str,
        confirmation_token: str,
        *,
        reason: str | None = None,
        rejected_by: str | None = None,
    ) -> dict[str, Any]:
        """Reject a paused HITL step and terminate the task."""

        task = get_task(self.ctx, self.conn, task_id, include_steps=True)
        if task is None:
            raise ValueError("Task not found")
        if task["status"] != "paused_hitl":
            raise ValueError(f"Task is not paused for HITL (status={task['status']})")
        if task["hitl_token"] != confirmation_token:
            raise PermissionError("Invalid confirmation token")

        hitl_step_id = task["hitl_step_id"]
        transition_step(
            self.ctx,
            self.conn,
            hitl_step_id,
            "failed",
            updates={
                "status_reason": f"hitl_rejected: {reason or 'no reason'}",
                "approved_by": rejected_by,
            },
        )
        transition_task(
            self.ctx,
            self.conn,
            task_id,
            "killed",
            updates={
                "output_text": reason or "Rejected via HITL",
                "kill_requested_by": rejected_by,
            },
        )
        refresh_task_cost(self.ctx, self.conn, task_id)
        return get_task(self.ctx, self.conn, task_id) or {}

    def kill_task(
        self,
        task_id: str,
        *,
        reason: str | None = None,
        requested_by: str | None = None,
    ) -> dict[str, Any]:
        """Kill a running or paused task."""

        task = get_task(self.ctx, self.conn, task_id, include_steps=True)
        if task is None:
            raise ValueError("Task not found")
        if task["status"] in {"completed", "killed", "failed", "degraded"}:
            return task

        from ..db import utc_now as db_utc_now

        now = db_utc_now()
        transition_task(
            self.ctx,
            self.conn,
            task_id,
            "killed",
            updates={
                "kill_requested_at": now,
                "kill_requested_by": requested_by,
                "output_text": reason or "Killed by user",
            },
        )
        for step in task["steps"]:
            if step["status"] in {"pending", "running", "paused_hitl"}:
                transition_step(
                    self.ctx,
                    self.conn,
                    step["id"],
                    "failed",
                    updates={"status_reason": "task_killed"},
                )
        refresh_task_cost(self.ctx, self.conn, task_id)
        return get_task(self.ctx, self.conn, task_id) or {}


def _degrade_if_overrun(
    ctx: Context,
    conn: Any,
    actual_cost: float,
    estimated_cost: float,
) -> None:
    """Run ACE degradation check if the task overran its estimate."""

    if estimated_cost and estimated_cost > 0 and actual_cost > estimated_cost * ACE_DEGRADE_OVERRUN_RATIO:
        try:
            degrade_workspace_if_needed(ctx, conn, ctx.require_scoped_workspace())
        except Exception:
            logger.exception("Degradation check failed after task overrun")
