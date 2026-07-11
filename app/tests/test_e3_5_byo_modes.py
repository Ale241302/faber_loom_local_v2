"""E3-5 — BYO key strict/hybrid modes and platform-key surcharge."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


def _auth_headers(tenant_id: str, role: str = "owner") -> dict[str, str]:
    """Return Authorization header with a JWT for the given tenant/role."""

    from app.src.auth import create_access_token

    token = create_access_token(
        "testuser@example.test",
        tenant_id=tenant_id,
        user_id="usr_test",
        role=role,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """Isolated app with fresh app DB and no provider env keys."""

    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv("FABERLOOM_USERS", '{"testuser@example.test":"password"}')
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "config"))

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

    audit_writer.audit_path = tmp_path / "audit.jsonl"
    with TestClient(create_app()) as test_client:
        yield test_client


def _first_workspace_id(client: TestClient, tenant_id: str = "default") -> str:
    resp = client.get("/api/workspaces", headers=_auth_headers(tenant_id))
    assert resp.status_code == 200, resp.text
    workspaces = resp.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def _create_workspace(client: TestClient, tenant_id: str, name: str) -> str:
    resp = client.post(
        "/api/workspaces",
        json={"name": name},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _set_tenant_byo_mode(client: TestClient, tenant_id: str, mode: str) -> None:
    resp = client.put(
        "/api/tenant/settings",
        json={"overrides": {"routing.byo_mode": mode}},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 200, resp.text
    settings = {s["key"]: s for s in resp.json()["settings"]}
    assert settings["routing.byo_mode"]["value"] == mode


def _store_tenant_key(client: TestClient, tenant_id: str, workspace_id: str, key: str) -> None:
    resp = client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        json={"api_key": key},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 200, resp.text


def _patch_completion(monkeypatch: pytest.MonkeyPatch, key_origin: str) -> None:
    """Patch the OpenAI-compatible provider so completions never hit the network."""

    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    class FakeProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="openai",
                    api_key=None,
                    model_default="gpt-4o-mini",
                    priority=1,
                    is_enabled=True,
                    key_origin=key_origin,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            return CompletionResult(
                content="Fake reply",
                model=request.model or "gpt-4o-mini",
                provider_slug="openai",
                input_tokens=10,
                output_tokens=4,
                cost_usd=0.0012,
                duration_ms=12,
            )

    import app.src.api as api_module

    def fake_build_router(*, byo_mode: str | None = None, **kwargs) -> Router:
        return Router(providers=[FakeProvider()])

    monkeypatch.setattr(api_module, "build_router", fake_build_router)


def _usage_record_for_chat(tenant_id: str) -> dict[str, Any] | None:
    from app.src.db import connect

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM usage_record WHERE tenant_id = ? ORDER BY created_at DESC LIMIT 1",
            (tenant_id,),
        ).fetchone()
    return dict(row) if row else None


def test_default_tenant_no_surcharge_when_platform_key_used(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    workspace_id = _first_workspace_id(client, "default")
    chat_id = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Default tenant"},
        headers=_auth_headers("default"),
    ).json()["id"]

    _patch_completion(monkeypatch, key_origin="platform")

    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
        json={"message": "Hi"},
        headers=_auth_headers("default"),
    )
    assert resp.status_code == 200, resp.text

    row = _usage_record_for_chat("default")
    assert row is not None
    assert row is not None
    assert row["platform_key_used"] == 1
    assert row["platform_key_surcharge_usd"] == 0.0


def test_non_default_tenant_with_own_key_no_surcharge(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = "tenant_with_key"
    workspace_id = _create_workspace(client, tenant_id, "Own key")

    _set_tenant_byo_mode(client, tenant_id, "hibrido")
    _store_tenant_key(client, tenant_id, workspace_id, "sk-tenant-own-key-1234567890")

    chat_id = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Own key"},
        headers=_auth_headers(tenant_id),
    ).json()["id"]

    _patch_completion(monkeypatch, key_origin="tenant")

    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
        json={"message": "Hi"},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 200, resp.text

    row = _usage_record_for_chat(tenant_id)
    assert row is not None
    assert row["platform_key_used"] == 0
    assert row["platform_key_surcharge_usd"] == 0.0
    assert row["byo_mode_at_run"] == "hibrido"


def test_non_default_tenant_hibrido_platform_key_records_surcharge(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant_id = "tenant_hibrido"
    workspace_id = _create_workspace(client, tenant_id, "Hibrido fallback")

    _set_tenant_byo_mode(client, tenant_id, "hibrido")

    chat_id = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Hibrido fallback"},
        headers=_auth_headers(tenant_id),
    ).json()["id"]

    _patch_completion(monkeypatch, key_origin="platform")

    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
        json={"message": "Hi"},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 200, resp.text

    row = _usage_record_for_chat(tenant_id)
    assert row is not None
    assert row["platform_key_used"] == 1
    from app.src.plans import get_plan_surcharge_pct

    pct = get_plan_surcharge_pct(tenant_id)
    assert abs(row["platform_key_surcharge_usd"] - row["cost_usd"] * pct) < 1e-9
    assert row["byo_mode_at_run"] == "hibrido"


def test_non_default_tenant_estricto_fail_closed_without_own_key(
    client: TestClient,
) -> None:
    tenant_id = "tenant_estricto"
    workspace_id = _create_workspace(client, tenant_id, "Estricto")

    _set_tenant_byo_mode(client, tenant_id, "estricto")

    chat_id = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Estricto"},
        headers=_auth_headers(tenant_id),
    ).json()["id"]

    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
        json={"message": "Hi"},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 422, resp.text
    assert "BYO estricto" in resp.json()["detail"]


def test_build_router_key_origin_resolution(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Direct unit test for BYO key resolution without hitting the network."""

    from app.src.router.registry import build_router

    tenant_id = "tenant_resolution"

    # No env key, no stored key -> unavailable.
    router = build_router(tenant_id=tenant_id, byo_mode="estricto")
    assert router.key_origin("openai") == "unavailable"
    assert not router.has_available_provider()

    # Hybrid with env key -> platform origin and provider available.
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-key-12345678901234567890")
    router = build_router(tenant_id=tenant_id, byo_mode="hibrido")
    assert router.key_origin("openai") == "platform"
    assert router.has_available_provider()

    # Default tenant always uses env key even in estricto.
    router = build_router(tenant_id="default", byo_mode="estricto")
    assert router.key_origin("openai") == "platform"


def test_usage_summary_endpoint_authorization(client: TestClient) -> None:
    tenant_a = "tenant_summary_a"
    tenant_b = "tenant_summary_b"
    _create_workspace(client, tenant_a, "Summary A")
    _create_workspace(client, tenant_b, "Summary B")

    # Owner of tenant A can read breakdown.
    resp = client.get(
        f"/api/tenants/{tenant_a}/usage/summary",
        headers=_auth_headers(tenant_a, role="owner"),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["tenant_id"] == tenant_a
    assert "breakdown" in data

    # Platform admin sees aggregates only.
    resp = client.get(
        f"/api/tenants/{tenant_a}/usage/summary",
        headers=_auth_headers(tenant_a, role="platform_admin"),
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["tenant_id"] == tenant_a
    assert data["breakdown"] == []

    # Cross-tenant owner is denied.
    resp = client.get(
        f"/api/tenants/{tenant_a}/usage/summary",
        headers=_auth_headers(tenant_b, role="owner"),
    )
    assert resp.status_code == 403, resp.text


def test_settings_byo_mode_update_and_read_back(client: TestClient) -> None:
    tenant_id = "tenant_settings_byo"
    _create_workspace(client, tenant_id, "Settings BYO")

    resp = client.put(
        "/api/tenant/settings",
        json={"overrides": {"routing.byo_mode": "estricto"}},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 200, resp.text
    settings = {s["key"]: s for s in resp.json()["settings"]}
    assert settings["routing.byo_mode"]["value"] == "estricto"
    assert settings["routing.byo_mode"]["source"] == "tenant"

    resp = client.get(
        "/api/tenant/settings",
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 200, resp.text
    settings = {s["key"]: s for s in resp.json()["settings"]}
    assert settings["routing.byo_mode"]["value"] == "estricto"


def test_settings_byo_mode_rejects_invalid_value(client: TestClient) -> None:
    tenant_id = "tenant_settings_invalid"
    _create_workspace(client, tenant_id, "Settings invalid")

    resp = client.put(
        "/api/tenant/settings",
        json={"overrides": {"routing.byo_mode": "invalid"}},
        headers=_auth_headers(tenant_id),
    )
    assert resp.status_code == 422, resp.text
