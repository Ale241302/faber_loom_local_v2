"""E4-0 routing.mode resolution and legacy compatibility tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect
from app.src.routing.policy import resolve_routing_mode


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))
    # Start without the legacy env var.
    monkeypatch.delenv("FABERLOOM_AUTO_MODE_ENABLED", raising=False)

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

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def _context(ws_id: str, tenant_id: str = "default") -> Context:
    return Context(workspace_id=ws_id, tenant_id=tenant_id, user_id="test", actor_id="test")


def test_default_mode_is_manual(client: TestClient) -> None:
    ws = _workspace_id(client)
    conn = connect()
    ctx = _context(ws)
    assert resolve_routing_mode(ctx, conn) == "manual"


def test_legacy_env_and_auto_enabled_maps_to_natural(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FABERLOOM_AUTO_MODE_ENABLED", "true")
    ws = _workspace_id(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"auto_mode_enabled": True},
        headers=_headers("owner"),
    )
    conn = connect()
    ctx = _context(ws)
    assert resolve_routing_mode(ctx, conn) == "natural"


def test_legacy_env_without_workspace_flag_is_manual(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FABERLOOM_AUTO_MODE_ENABLED", "true")
    ws = _workspace_id(client)
    conn = connect()
    ctx = _context(ws)
    assert resolve_routing_mode(ctx, conn) == "manual"


def test_explicit_tenant_mode_wins_over_legacy(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FABERLOOM_AUTO_MODE_ENABLED", "true")
    ws = _workspace_id(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"auto_mode_enabled": True},
        headers=_headers("owner"),
    )
    # Set tenant-level routing.mode to shadow.
    client.put(
        "/api/tenant/settings",
        json={"overrides": {"routing.mode": "shadow"}},
        headers=_headers("owner"),
    )
    conn = connect()
    ctx = _context(ws)
    assert resolve_routing_mode(ctx, conn) == "shadow"


def test_explicit_user_mode_wins_over_tenant(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FABERLOOM_AUTO_MODE_ENABLED", "true")
    ws = _workspace_id(client)
    client.put(
        f"/api/workspaces/{ws}/routing-policy",
        json={"auto_mode_enabled": True},
        headers=_headers("owner"),
    )
    client.put(
        "/api/tenant/settings",
        json={"overrides": {"routing.mode": "natural"}},
        headers=_headers("owner"),
    )
    # Simulate a user preference that overrides the tenant setting.
    from app.src import config_cascade

    original_user_config = config_cascade._user_config

    def _mock_user_config(conn: Any, ctx: Context, key: str) -> Any:
        if key == "routing.mode":
            return "manual"
        return original_user_config(conn, ctx, key)

    monkeypatch.setattr(config_cascade, "_user_config", _mock_user_config)

    conn = connect()
    ctx = _context(ws)
    assert resolve_routing_mode(ctx, conn) == "manual"
