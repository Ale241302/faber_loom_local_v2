"""E4-3 HITL pause/approve/reject API tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect
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
    import app.src.api as api_module
    import app.src.router.registry as router_registry_module
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
            return CompletionResult(
                content="OK",
                model=request.model or "fake-model",
                provider_slug="fake",
                input_tokens=1,
                output_tokens=1,
                cost_usd=0.0001,
                duration_ms=1,
            )

    def fake_build_router(*, budget_cap_usd=None, provider_allowlist=None, tenant_id=None, **kwargs):
        return Router(providers=[FakeTextProvider()])

    monkeypatch.setattr(auto_dispatcher_module, "build_router", fake_build_router)
    monkeypatch.setattr(api_module, "build_router", fake_build_router)
    monkeypatch.setattr(router_registry_module, "build_router", fake_build_router)

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


def _hitl_plan() -> DispatchPlan:
    return DispatchPlan(
        steps=[
            DispatchStep(
                step_id="step_0",
                capability="text",
                task="run",
                prompt="ok",
                complexity="medium",
                chosen={
                    "provider_slug": "fake",
                    "model": "fake-model",
                    "cost_input_1k": 0.001,
                    "cost_output_1k": 0.001,
                },
                requires_hitl=False,
            ),
            DispatchStep(
                step_id="step_1",
                capability="mail_send",
                task="send_email",
                prompt="enviar",
                complexity="medium",
                chosen={
                    "provider_slug": "fake",
                    "model": "fake-model",
                    "cost_input_1k": 0.001,
                    "cost_output_1k": 0.001,
                },
                requires_hitl=True,
            ),
        ],
        est_total_cost_usd=0.001,
        planner_cost_usd=0.0,
    )


def test_api_approve_hitl_step(client: TestClient) -> None:
    ws = _setup_catalog(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    task = TaskOrchestrator(ctx, conn).run_task_from_plan(
        chat_id=None,
        user_request="hitl api approve",
        plan=_hitl_plan(),
    )
    assert task["status"] == "paused_hitl"

    resp = client.post(
        f"/api/workspaces/{ws}/agent-tasks/{task['id']}/approve",
        json={"confirmation_token": task["hitl_token"]},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


def test_api_reject_hitl_step(client: TestClient) -> None:
    ws = _setup_catalog(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    task = TaskOrchestrator(ctx, conn).run_task_from_plan(
        chat_id=None,
        user_request="hitl api reject",
        plan=_hitl_plan(),
    )
    assert task["status"] == "paused_hitl"

    resp = client.post(
        f"/api/workspaces/{ws}/agent-tasks/{task['id']}/reject",
        json={"token": task["hitl_token"], "reason": "no enviar"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in {"killed", "failed"}


def test_api_wrong_hitl_token_is_rejected(client: TestClient) -> None:
    ws = _setup_catalog(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    task = TaskOrchestrator(ctx, conn).run_task_from_plan(
        chat_id=None,
        user_request="hitl token reject",
        plan=_hitl_plan(),
    )
    assert task["status"] == "paused_hitl"

    resp = client.post(
        f"/api/workspaces/{ws}/agent-tasks/{task['id']}/approve",
        json={"confirmation_token": "wrong-token"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 403
