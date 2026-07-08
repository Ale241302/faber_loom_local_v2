"""E2-4 step-aware cost ledger tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect, get_db, list_usage_records
from app.src.ledger import record_step, start_chain, sum_chain_cost
from app.src.router.engine import Router
from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
from app.src.router.providers import Provider


class FakeProvider(Provider):
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
            content="reply",
            model=request.model or "fake-model",
            provider_slug="fake",
            input_tokens=4,
            output_tokens=2,
            cost_usd=0.001,
            duration_ms=5,
        )


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))
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
    import app.src.api as api_module
    from app.src.router import cost as cost_module

    monkeypatch.setitem(cost_module.MODEL_ALLOWLIST, "fake", {"fake-model"})
    monkeypatch.setattr(api_module, "build_router", lambda user_id=None, tenant_id=None, **kwargs: Router(providers=[FakeProvider()]))

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def test_usage_record_has_step_columns_after_manual_completion(client: TestClient) -> None:
    ws = _workspace_id(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Ledger"}, headers=_headers("owner")).json()
    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Hi", "provider_slug": "fake", "model": "fake-model"},
        headers=_headers("owner"),
    )
    assert response.status_code == 200

    usage = client.get(f"/api/workspaces/{ws}/usage", headers=_headers("owner")).json()
    assert len(usage) == 1
    record = usage[0]
    assert "run_id" in record
    assert "step_index" in record
    assert "chain_id" in record
    assert "capability" in record


def test_ledger_helpers_record_chain_steps(client: TestClient) -> None:
    ws = _workspace_id(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Ledger direct"}, headers=_headers("owner")).json()

    # Use the same connection the app would use so we can call helpers directly.
    from app.src.api import context_from_request
    from fastapi import Request

    request = Request(scope={"type": "http", "headers": []})
    ctx = context_from_request(request, workspace_id=ws)

    conn = connect()
    chain_id = start_chain(ctx, conn, chat_id=chat["id"], kind="test")
    step = record_step(
        ctx,
        conn,
        chain_id=chain_id,
        step_index=0,
        result={
            "status": "succeeded",
            "provider_slug": "fake",
            "model": "fake-model",
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.002,
            "duration_ms": 8,
        },
        chat_id=chat["id"],
        capability="text",
    )
    assert step["chain_id"] == chain_id
    assert step["step_index"] == 0
    assert step["capability"] == "text"
    assert round(sum_chain_cost(ctx, conn, chain_id), 6) == 0.002
    conn.close()


def test_chain_cost_only_sums_succeeded_steps(client: TestClient) -> None:
    ws = _workspace_id(client)
    chat = client.post(f"/api/workspaces/{ws}/chats", json={"title": "Ledger sum"}, headers=_headers("owner")).json()

    from app.src.api import context_from_request
    from fastapi import Request

    request = Request(scope={"type": "http", "headers": []})
    ctx = context_from_request(request, workspace_id=ws)
    conn = connect()
    chain_id = start_chain(ctx, conn, chat_id=chat["id"], kind="test")
    record_step(ctx, conn, chain_id=chain_id, step_index=0, result={"status": "succeeded", "provider_slug": "fake", "model": "fake-model", "input_tokens": 1, "output_tokens": 1, "cost_usd": 0.01, "duration_ms": 1}, chat_id=chat["id"], capability="text")
    record_step(ctx, conn, chain_id=chain_id, step_index=1, result={"status": "failed", "provider_slug": "fake", "model": "fake-model", "input_tokens": 1, "output_tokens": 1, "cost_usd": 0.02, "duration_ms": 1, "error": "fail"}, chat_id=chat["id"], capability="text")
    assert round(sum_chain_cost(ctx, conn, chain_id), 6) == 0.01
    conn.close()
