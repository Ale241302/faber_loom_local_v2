"""E4-0 bit-a-bit regression test for the auto dispatcher refactor."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect
from app.src.routing.auto_dispatcher import NaturalPlanner, execute_plan, run_auto_chain


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
                        {"capability": "text", "task": "expand", "prompt": "Expand."},
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


def test_run_auto_chain_matches_separated_plan_and_execute(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Regression"}, headers=_headers("owner")).json()

    # Full legacy path.
    legacy_result = run_auto_chain(
        ctx,
        conn,
        chat_id=chat["id"],
        user_request="Tell me about looms",
    )

    # Separated path: plan then execute.
    planner = NaturalPlanner()
    plan = planner.plan(
        ctx,
        conn,
        user_request="Tell me about looms",
        attachments=[],
        policy={"max_auto_steps": 3, "budget_cap_usd": 1.0, "require_local_only": False},
    )
    separated_result = execute_plan(
        ctx,
        conn,
        chat_id=chat["id"],
        user_request="Tell me about looms",
        plan=plan,
    )

    assert legacy_result["provider_slug"] == separated_result["provider_slug"] == "fake"
    assert legacy_result["model"] == separated_result["model"] == "fake-model"
    assert legacy_result["content"] == separated_result["content"]
    assert len(legacy_result["steps"]) == len(separated_result["steps"])
    assert legacy_result["cost_usd"] == separated_result["cost_usd"]


def test_run_auto_chain_records_usage_steps(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Ledger"}, headers=_headers("owner")).json()
    result = run_auto_chain(
        ctx,
        conn,
        chat_id=chat["id"],
        user_request="Tell me about looms",
    )

    assert result["chain_id"]
    assert len(result["steps"]) >= 1
    for step in result["steps"]:
        assert step["capability"]
        assert step["provider_slug"]
        assert step["model"]
