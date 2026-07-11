"""E4-2 Shadow Planner / Plan Audit tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect, new_id, utc_now
from app.src.living_agent.autonomy import (
    degrade_workspace_if_needed,
    evaluate_promotion_readiness,
    generate_promotion_token,
)
from app.src.living_agent.planner import (
    get_shadow_report,
    update_model_track_record,
)


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

    import app.src.router.registry as router_registry_module

    monkeypatch.setattr(router_registry_module, "build_router", fake_build_router)

    # The manual completion path in api.py imports build_router directly from
    # .router, so we must also patch the reference held by the api module.
    import app.src.api as api_module

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

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


def test_planner_decision_log_written_on_auto(client: TestClient) -> None:
    ws = _setup_workspace(client)
    # Set routing.mode to natural.
    client.put(
        "/api/tenant/settings",
        json={"overrides": {"routing.mode": "natural"}},
        headers=_headers("owner"),
    )

    resp = client.post(
        f"/api/workspaces/{ws}/chats",
        json={"title": "Test"},
        headers=_headers("owner"),
    )
    chat_id = resp.json()["id"]

    resp = client.post(
        f"/api/workspaces/{ws}/chats/{chat_id}/completions",
        json={"message": "Tell me about looms", "mode": "auto"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200

    conn = connect()
    rows = conn.execute(
        "SELECT * FROM planner_decision_log WHERE workspace_id = ? AND mode = 'natural'",
        (ws,),
    ).fetchall()
    assert len(rows) >= 1
    decision = dict(rows[0])
    assert decision["tenant_id"] == "default"
    assert decision["correlation_id"] == chat_id
    plan = __import__("json").loads(decision["plan_json"])
    assert "steps" in plan
    assert len(plan["steps"]) >= 1
    assert "est_total_cost_usd" in plan
    assert "planner_cost_usd" in plan


def test_shadow_plan_written_on_manual(client: TestClient) -> None:
    ws = _setup_workspace(client)
    # Set routing.mode to shadow.
    client.put(
        "/api/tenant/settings",
        json={"overrides": {"routing.mode": "shadow"}},
        headers=_headers("owner"),
    )

    resp = client.post(
        f"/api/workspaces/{ws}/chats",
        json={"title": "Test"},
        headers=_headers("owner"),
    )
    chat_id = resp.json()["id"]

    resp = client.post(
        f"/api/workspaces/{ws}/chats/{chat_id}/completions",
        json={"message": "Tell me about looms", "mode": "manual", "provider_slug": "fake", "model": "fake-model"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200

    conn = connect()
    rows = conn.execute(
        "SELECT * FROM planner_decision_log WHERE workspace_id = ? AND mode = 'shadow'",
        (ws,),
    ).fetchall()
    assert len(rows) >= 1
    decision = dict(rows[0])
    assert decision["mode"] == "shadow"
    assert decision["correlation_id"] == chat_id
    plan = __import__("json").loads(decision["plan_json"])
    assert "steps" in plan
    assert "est_total_cost_usd" in plan
    assert "planner_cost_usd" in plan


def test_track_record_accumulates(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    for _ in range(3):
        update_model_track_record(
            ctx,
            conn,
            capability="text",
            provider_slug="fake",
            model="fake-model",
            outcome="accepted",
            cost_usd=0.001,
            latency_ms=5.0,
        )

    row = conn.execute(
        """
        SELECT total_decisions, accepted_count FROM model_track_record
        WHERE tenant_id = ? AND capability = ? AND provider_slug = ? AND model = ?
        """,
        ("default", "text", "fake", "fake-model"),
    ).fetchone()
    assert row is not None
    assert row["total_decisions"] == 3
    assert row["accepted_count"] == 3


def test_shadow_report_endpoint(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    update_model_track_record(
        ctx,
        conn,
        capability="text",
        provider_slug="fake",
        model="fake-model",
        outcome="accepted",
        cost_usd=0.001,
        latency_ms=5.0,
    )

    resp = client.get("/api/tenants/default/routing/shadow-report?days=14", headers=_headers("owner"))
    assert resp.status_code == 200
    data = resp.json()
    assert data["tenant_id"] == "default"
    assert data["days"] == 14
    assert any(
        r["capability"] == "text" and r["provider_slug"] == "fake" and r["model"] == "fake-model"
        for r in data["model_records"]
    )


def test_poor_track_record_filters_model(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    # Seed 20 rejected samples for fake-model so it gets filtered.
    for _ in range(20):
        update_model_track_record(
            ctx,
            conn,
            capability="text",
            provider_slug="fake",
            model="fake-model",
            outcome="rejected",
            cost_usd=0.001,
            latency_ms=5.0,
        )

    from app.src.routing.catalog import resolve_model_for_capability

    # Should raise because the only model is now filtered out.
    with pytest.raises(ValueError):
        resolve_model_for_capability(
            ctx,
            conn,
            "text",
            budget_remaining=1.0,
            complexity="medium",
            estimated_input_tokens=100,
        )


def _insert_decision(
    conn: Any,
    ctx: Context,
    workspace_id: str,
    *,
    mode: str,
    est_cost: float = 0.01,
    actual_cost: float = 0.01,
    created_at: str | None = None,
) -> None:
    now = created_at or utc_now()
    conn.execute(
        """
        INSERT INTO planner_decision_log (
            id, tenant_id, workspace_id, mode, plan_json, actual_outcome_json,
            correlation_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id("pdl"),
            ctx.require_tenant(),
            workspace_id,
            mode,
            __import__("json").dumps({"est_total_cost_usd": est_cost, "planner_cost_usd": est_cost}),
            __import__("json").dumps({"cost_usd": actual_cost}),
            new_id("cor"),
            now,
            now,
        ),
    )


def test_promotion_readiness_not_ready_without_decisions(client: TestClient) -> None:
    ws = _setup_workspace(client)
    resp = client.get(
        f"/api/workspaces/{ws}/routing/promotion-readiness",
        headers=_headers("owner"),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["workspace_id"] == ws
    assert data["ready"] is False
    assert data["shadow_decisions"] == 0


def test_promotion_readiness_ready_after_threshold(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")
    for _ in range(50):
        _insert_decision(conn, ctx, ws, mode="shadow", est_cost=0.01, actual_cost=0.02)
    conn.commit()

    resp = client.get(
        f"/api/workspaces/{ws}/routing/promotion-readiness",
        headers=_headers("owner"),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["ready"] is True
    assert data["shadow_decisions"] == 50
    assert data["projected_savings_usd"] >= 0


def test_promotion_token_verifies_and_promotes(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")
    for _ in range(50):
        _insert_decision(conn, ctx, ws, mode="shadow", est_cost=0.01, actual_cost=0.02)
    conn.commit()

    token = generate_promotion_token(ws, "promote-shadow")
    resp = client.post(
        f"/api/workspaces/{ws}/routing/promote",
        json={"mode": "natural", "confirmation_token": token},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "natural"
    assert data["action"] == "workspace.routing.promoted"

    # Effective mode resolves to natural.
    resp = client.get(f"/api/workspaces/{ws}/settings", headers=_headers("owner"))
    assert resp.status_code == 200
    setting = next((s for s in resp.json()["settings"] if s["key"] == "routing.mode"), None)
    assert setting is not None
    assert setting["value"] == "natural"


def test_degradation_overrun_returns_to_shadow(client: TestClient) -> None:
    ws = _setup_workspace(client)
    conn = connect()
    ctx = Context(workspace_id=ws, tenant_id="default", user_id="test", actor_id="test")

    # Force workspace into natural mode.
    from app.src.db import update_routing_policy

    update_routing_policy(ctx.with_workspace(ws), conn, mode="natural")

    # Planner estimated $0.01, real usage cost $1.00 -> overrun.
    _insert_decision(conn, ctx, ws, mode="natural", est_cost=0.01, actual_cost=0.01)
    conn.execute(
        """
        INSERT INTO usage_record (
            id, tenant_id, workspace_id, chat_id, provider_slug, model,
            input_tokens, output_tokens, cost_usd, duration_ms, status,
            attempts_json, request_json, response_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            new_id("usg"),
            ctx.require_tenant(),
            ws,
            new_id("cht"),
            "fake",
            "fake-model",
            10,
            10,
            1.0,
            1,
            "succeeded",
            "[]",
            "{}",
            "{}",
            utc_now(),
        ),
    )

    result = degrade_workspace_if_needed(ctx, conn, ws)
    assert result["degraded"] is True
    policy = conn.execute(
        "SELECT mode, degraded_count FROM workspace_routing_policy WHERE workspace_id = ?",
        (ws,),
    ).fetchone()
    assert policy["mode"] == "shadow"
    assert policy["degraded_count"] == 1
