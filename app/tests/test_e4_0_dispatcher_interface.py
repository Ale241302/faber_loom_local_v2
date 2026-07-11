"""E4-0 TaskDispatcher / NaturalPlanner interface tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect
from app.src.routing.auto_dispatcher import NaturalPlanner
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
            prompt = "".join(str(m.get("content", "")) for m in request.messages if m.get("role") == "user")
            if "routing planner" in prompt.lower():
                plan = {
                    "steps": [
                        {"capability": "text", "task": "summarize", "prompt": "Summarize."},
                        {"capability": "text", "task": "answer", "prompt": "Answer."},
                    ]
                }
                content = __import__("json").dumps(plan)
            else:
                content = "Summary of the document: woven fabric loom."
            return CompletionResult(
                content=content,
                model=request.model or "fake-model",
                provider_slug="fake",
                input_tokens=10,
                output_tokens=10,
                cost_usd=0.001,
                duration_ms=3,
            )

    def fake_build_router(*, budget_cap_usd=None, provider_allowlist=None, tenant_id=None, **kwargs):
        return Router(providers=[FakeTextProvider()])

    monkeypatch.setattr(auto_dispatcher_module, "build_router", fake_build_router)

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def _setup_workspace(client: TestClient) -> str:
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


def test_natural_planner_returns_dispatch_plan(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")
    policy = {"max_auto_steps": 3, "budget_cap_usd": 1.0, "require_local_only": False}

    planner = NaturalPlanner(policy=policy)
    plan = planner.plan(
        ctx,
        conn,
        user_request="Tell me about looms",
        attachments=[],
        policy=policy,
    )

    assert isinstance(plan, DispatchPlan)
    assert len(plan.steps) >= 1
    for step in plan.steps:
        assert isinstance(step, DispatchStep)
        assert step.step_id
        assert step.capability
        assert step.chosen is not None
        assert step.chosen["provider_slug"]
        assert step.chosen["model"]
        assert step.chosen["est_cost_usd"] >= 0


def test_dispatch_steps_chain_inputs_from(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")
    policy = {"max_auto_steps": 3, "budget_cap_usd": 1.0, "require_local_only": False}

    planner = NaturalPlanner(policy=policy)
    plan = planner.plan(
        ctx,
        conn,
        user_request="Plan something",
        attachments=[],
        policy=policy,
    )

    assert len(plan.steps) >= 1
    for index, step in enumerate(plan.steps):
        if index == 0:
            assert step.inputs_from is None
        else:
            assert step.inputs_from == f"step_{index - 1}"


def test_planner_respects_max_steps(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")
    policy = {"max_auto_steps": 1, "budget_cap_usd": 1.0, "require_local_only": False}

    planner = NaturalPlanner(policy=policy)
    plan = planner.plan(
        ctx,
        conn,
        user_request="Plan something",
        attachments=[],
        policy=policy,
    )

    assert len(plan.steps) <= 1
