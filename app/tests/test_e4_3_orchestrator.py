"""E4-3 agent task orchestrator tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect
from app.src.living_agent.artifacts import load_step_artifact_text
from app.src.living_agent.orchestrator import TaskOrchestrator
from app.src.living_agent.tasks import get_task
from app.src.routing.dispatcher_base import DispatchPlan, DispatchStep


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("FABERLOOM_AUTO_MODE_ENABLED", "true")

    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
        "KIMI_API_KEY",
        "MOONSHOT_API_KEY",
        "FABERLOOM_KIMI_API_KEY",
        "FABERLOOM_ENABLE_OLLAMA",
        "FABERLOOM_OLLAMA_ENABLED",
        "FABERLOOM_PROVIDER_ALLOWLIST",
        "FABERLOOM_BUDGET_CAP_USD",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app
    import app.src.routing.auto_dispatcher as auto_dispatcher_module
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    monkeypatch.setitem(cost_module.MODEL_ALLOWLIST, "fake", {"fake-model"})

    class FakeTextProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="fake",
                    api_key=None,
                    model_default="fake-model",
                    priority=1,
                    is_enabled=True,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            prompt = "".join(
                str(m.get("content", "")) for m in request.messages if m.get("role") == "user"
            )
            if "paso 0" in prompt.lower():
                content = "OUTPUT_STEP_0"
            elif "paso 1" in prompt.lower():
                content = f"OUTPUT_STEP_1_RECEIVED_{prompt}"
            else:
                content = "Generic response"
            return CompletionResult(
                content=content,
                model=request.model or "fake-model",
                provider_slug="fake",
                input_tokens=5,
                output_tokens=5,
                cost_usd=0.001,
                duration_ms=2,
            )

    def fake_build_router(*, budget_cap_usd=None, provider_allowlist=None, tenant_id=None, **kwargs):
        return Router(providers=[FakeTextProvider()])

    monkeypatch.setattr(auto_dispatcher_module, "build_router", fake_build_router)

    import app.src.router.registry as router_registry_module

    monkeypatch.setattr(router_registry_module, "build_router", fake_build_router)

    import app.src.api as api_module

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def _setup_catalog(client: TestClient) -> str:
    ws = _workspace_id(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"auto_mode_enabled": True, "budget_cap_usd": 1.0, "max_auto_steps": 3},
        headers=_headers("owner"),
    )
    client.post(
        f"/api/workspaces/{ws}/model-catalog",
        json={"provider_slug": "fake", "model": "fake-model", "capabilities": ["text", "cheap"], "is_local": True},
        headers=_headers("owner"),
    )
    return ws


def _fake_step(step_id: str, capability: str, prompt: str, chosen: dict[str, Any] | None = None) -> DispatchStep:
    return DispatchStep(
        step_id=step_id,
        capability=capability,
        task="run",
        prompt=prompt,
        complexity="medium",
        model_candidates=[],
        chosen=chosen or {
            "provider_slug": "fake",
            "model": "fake-model",
            "cost_input_1k": 0.001,
            "cost_output_1k": 0.001,
        },
        reason="test",
        inputs_from=None,
        requires_hitl=False,
    )


def test_orchestrator_runs_two_step_pipeline_with_artifact_handoff(client: TestClient) -> None:
    ws = _setup_catalog(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    plan = DispatchPlan(
        steps=[
            _fake_step("step_0", "text", "Ejecuta paso 0"),
            _fake_step("step_1", "text", "Continúa con paso 1"),
        ],
        est_total_cost_usd=0.002,
        planner_cost_usd=0.0,
    )

    task = TaskOrchestrator(ctx, conn).run_task_from_plan(
        chat_id=None,
        user_request="pipeline test",
        plan=plan,
    )

    assert task["status"] == "completed"
    assert len(task["steps"]) == 2
    assert task["cost_total_usd"] > 0

    step0 = task["steps"][0]
    step1 = task["steps"][1]
    assert step0["status"] == "completed"
    assert step0["output_ref"] is not None
    assert step1["status"] == "completed"

    # Artifact handoff: step 1 received step 0 output.
    artifact_text = load_step_artifact_text(ctx, conn, step0["output_ref"])
    assert artifact_text == "OUTPUT_STEP_0"
    assert "OUTPUT_STEP_0" in (task["output_text"] or "")


def test_orchestrator_pauses_on_hitl_step_and_continues_with_token(client: TestClient) -> None:
    ws = _setup_catalog(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    plan = DispatchPlan(
        steps=[
            _fake_step("step_0", "text", "Ejecuta paso 0"),
            DispatchStep(
                step_id="step_1",
                capability="mail_send",
                task="send_email",
                prompt="Enviar correo",
                complexity="medium",
                chosen={
                    "provider_slug": "fake",
                    "model": "fake-model",
                    "cost_input_1k": 0.001,
                    "cost_output_1k": 0.001,
                },
                requires_hitl=True,
            ),
            _fake_step("step_2", "text", "Continúa con paso 2"),
        ],
        est_total_cost_usd=0.003,
        planner_cost_usd=0.0,
    )

    orch = TaskOrchestrator(ctx, conn)
    task = orch.run_task_from_plan(
        chat_id=None,
        user_request="hitl pipeline",
        plan=plan,
    )

    assert task["status"] == "paused_hitl"
    assert task["hitl_step_id"] is not None
    assert task["hitl_token"] is not None

    # A WorkLoom draft should exist for the HITL pause.
    draft = conn.execute(
        "SELECT id, status FROM draft WHERE workspace_id = ? AND status = 'pending_approval'",
        (ws,),
    ).fetchone()
    assert draft is not None

    task = orch.approve_hitl_step(task["id"], task["hitl_token"])
    assert task["status"] == "completed"
    assert len(task["steps"]) == 3
    assert task["steps"][1]["status"] == "completed"
    assert task["steps"][2]["status"] == "completed"


def test_orchestrator_degrades_task_on_budget_overrun(client: TestClient) -> None:
    ws = _setup_catalog(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    # Set a tiny budget cap.
    from app.src.db import update_routing_policy

    update_routing_policy(ctx, conn, budget_cap_usd=0.0001)

    plan = DispatchPlan(
        steps=[_fake_step("step_0", "text", "Paso caro")],
        est_total_cost_usd=0.001,
        planner_cost_usd=0.0,
    )

    task = TaskOrchestrator(ctx, conn).run_task_from_plan(
        chat_id=None,
        user_request="budget test",
        plan=plan,
    )

    assert task["status"] == "degraded"


def test_orchestrator_kill_task(client: TestClient) -> None:
    ws = _setup_catalog(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    plan = DispatchPlan(
        steps=[
            _fake_step("step_0", "text", "Ejecuta paso 0"),
            _fake_step("step_1", "text", "Continúa"),
        ],
        est_total_cost_usd=0.002,
        planner_cost_usd=0.0,
    )

    orch = TaskOrchestrator(ctx, conn)
    task = orch.run_task_from_plan(
        chat_id=None,
        user_request="kill test",
        plan=plan,
    )

    # Kill an already completed task is a no-op.
    task = orch.kill_task(task["id"], reason="user request", requested_by="test")
    assert task["status"] == "completed"


def test_agent_task_api_endpoints(client: TestClient) -> None:
    ws = _setup_catalog(client)

    resp = client.post(
        f"/api/workspaces/{ws}/agent-tasks",
        json={"user_request": "resumí el PDF y generá una imagen"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200
    task = resp.json()
    assert task["workspace_id"] == ws
    assert task["status"] in {"completed", "paused_hitl", "degraded"}

    resp = client.get(f"/api/workspaces/{ws}/agent-tasks", headers=_headers("owner"))
    assert resp.status_code == 200
    assert any(t["id"] == task["id"] for t in resp.json())

    resp = client.get(f"/api/workspaces/{ws}/agent-tasks/{task['id']}", headers=_headers("owner"))
    assert resp.status_code == 200
    assert resp.json()["id"] == task["id"]


def test_agent_task_isolation(client: TestClient) -> None:
    ws = _setup_catalog(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    plan = DispatchPlan(
        steps=[_fake_step("step_0", "text", "Ejecuta paso 0")],
        est_total_cost_usd=0.001,
        planner_cost_usd=0.0,
    )
    task = TaskOrchestrator(ctx, conn).run_task_from_plan(
        chat_id=None,
        user_request="isolation test",
        plan=plan,
    )

    other_ctx = Context(workspace_id=ws, tenant_id="other", user_id="test", actor_id="test")
    assert get_task(other_ctx, conn, task["id"], include_steps=False) is None
