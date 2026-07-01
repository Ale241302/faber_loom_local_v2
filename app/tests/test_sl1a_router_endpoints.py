"""Tests for provider configuration endpoints."""

from __future__ import annotations

import hashlib
from typing import Any

import pytest
from fastapi.testclient import TestClient


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
        "FABERLOOM_DEV_TRUST_HEADERS",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def test_list_providers_masks_keys(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.get(f"/api/workspaces/{workspace_id}/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert "model_allowlist" in data
    slugs = {p["provider_slug"] for p in data["providers"]}
    assert slugs == {"openai", "kimi"}
    openai = next(p for p in data["providers"] if p["provider_slug"] == "openai")
    assert openai["api_key_masked"] is None


def test_update_provider_config_and_status(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)

    response = client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        json={"api_key": "sk-test1234567890123456", "model_default": "gpt-4o", "priority": 5, "is_enabled": True},
    )
    assert response.status_code == 200
    updated = response.json()
    assert updated["api_key_masked"].startswith("sk-t")
    assert updated["api_key_masked"].endswith("3456")
    assert updated["model_default"] == "gpt-4o"
    assert updated["priority"] == 5

    response = client.get(f"/api/workspaces/{workspace_id}/router/status")
    assert response.status_code == 200
    openai_status = next(p for p in response.json()["providers"] if p["provider_slug"] == "openai")
    assert openai_status["configured"] is True
    assert openai_status["available"] is True


def _confirmation_token(resource_id: str) -> str:
    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def test_delete_provider_key_requires_confirmation(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        json={"api_key": "sk-test1234567890123456"},
    )

    response = client.delete(f"/api/workspaces/{workspace_id}/providers/openai/key")
    assert response.status_code == 409

    token = _confirmation_token("openai")
    response = client.delete(
        f"/api/workspaces/{workspace_id}/providers/openai/key",
        params={"confirmation_token": token},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "key_removed"

    response = client.get(f"/api/workspaces/{workspace_id}/providers")
    openai = next(p for p in response.json()["providers"] if p["provider_slug"] == "openai")
    assert openai["api_key_masked"] is None


def test_test_provider_without_key(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.post(f"/api/workspaces/{workspace_id}/providers/openai/test")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert "not configured" in (data["error"] or "").lower()


def test_update_unknown_provider_returns_422(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.patch(
        f"/api/workspaces/{workspace_id}/providers/unknown",
        json={"api_key": "sk-test1234567890123456"},
    )
    assert response.status_code == 422


def test_update_provider_with_invalid_model_returns_422(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        json={"model_default": "not-in-allowlist"},
    )
    assert response.status_code == 422, response.text


def test_provider_config_update_is_audited(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        json={"api_key": "sk-test1234567890123456", "model_default": "gpt-4o", "priority": 5, "is_enabled": True},
    )
    assert response.status_code == 200, response.text

    response = client.get(f"/api/workspaces/{workspace_id}/editorial-history")
    assert response.status_code == 200, response.text
    events = response.json().get("events", [])
    config_events = [e for e in events if e["action"] == "provider.config_updated"]
    assert config_events
    payload = config_events[0]["payload"]
    assert payload["provider_slug"] == "openai"
    assert "api_key" in payload["diff"]
    assert payload["diff"]["api_key"]["new"].startswith("sk-t")
    assert payload["diff"]["api_key"]["new"].endswith("3456")
    assert "test1234567890123456" not in payload["diff"]["api_key"]["new"]


def test_provider_key_delete_is_audited(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        json={"api_key": "sk-test1234567890123456"},
    )

    token = _confirmation_token("openai")
    response = client.delete(
        f"/api/workspaces/{workspace_id}/providers/openai/key",
        params={"confirmation_token": token},
    )
    assert response.status_code == 200, response.text

    response = client.get(f"/api/workspaces/{workspace_id}/editorial-history")
    assert response.status_code == 200, response.text
    events = response.json().get("events", [])
    assert any(e["action"] == "provider.key_deleted" for e in events)


def test_provider_config_exposes_requires_api_key(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.get(f"/api/workspaces/{workspace_id}/providers")
    assert response.status_code == 200, response.text
    providers = response.json()["providers"]
    by_slug = {p["provider_slug"]: p for p in providers}
    assert by_slug["openai"]["requires_api_key"] is True
    assert by_slug["kimi"]["requires_api_key"] is True


def test_ollama_can_be_enabled_without_key(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.patch(
        f"/api/workspaces/{workspace_id}/providers/ollama",
        json={"is_enabled": True, "model_default": "llama3.1"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["is_enabled"] is True
    assert data["requires_api_key"] is False


def test_provider_surface_visible_is_openai_and_kimi(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.get(f"/api/workspaces/{workspace_id}/providers")
    assert response.status_code == 200, response.text
    data = response.json()
    visible_slugs = {p["provider_slug"] for p in data["providers"]}
    assert visible_slugs == {"openai", "kimi"}
    assert set(data["model_allowlist"].keys()) == {"openai", "kimi"}

    status = client.get(f"/api/workspaces/{workspace_id}/router/status").json()
    status_slugs = {p["provider_slug"] for p in status["providers"]}
    assert status_slugs == {"openai", "kimi"}
    assert set(status["model_allowlist"].keys()) == {"openai", "kimi"}


def test_rename_conversation(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)

    chat = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Nueva conversación"},
    ).json()

    response = client.patch(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}",
        json={"title": "Renombrada"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["title"] == "Renombrada"

    response = client.get(f"/api/workspaces/{workspace_id}/chats/{chat['id']}")
    assert response.json()["title"] == "Renombrada"


def test_delete_conversation_requires_confirmation(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)

    chat = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Para borrar"},
    ).json()

    # Without confirmation token → 409.
    response = client.delete(f"/api/workspaces/{workspace_id}/chats/{chat['id']}")
    assert response.status_code == 409

    # With confirmation → 204.
    token = _confirmation_token(chat["id"])
    response = client.delete(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}",
        params={"confirmation_token": token},
    )
    assert response.status_code == 204

    # Chat is gone.
    response = client.get(f"/api/workspaces/{workspace_id}/chats/{chat['id']}")
    assert response.status_code == 404


def test_delete_conversation_tenant_isolation(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FABERLOOM_DEV_TRUST_HEADERS", "true")

    ws_a = client.post("/api/workspaces", json={"name": "Tenant A"}, headers={"x-tenant-id": "tenant-a"}).json()
    ws_b = client.post("/api/workspaces", json={"name": "Tenant B"}, headers={"x-tenant-id": "tenant-b"}).json()

    chat = client.post(
        f"/api/workspaces/{ws_a['id']}/chats",
        json={"title": "Chat A"},
        headers={"x-tenant-id": "tenant-a"},
    ).json()

    token = _confirmation_token(chat["id"])
    response = client.delete(
        f"/api/workspaces/{ws_b['id']}/chats/{chat['id']}",
        params={"confirmation_token": token},
        headers={"x-tenant-id": "tenant-b"},
    )
    # Workspace mismatch → 404 before tenant check.
    assert response.status_code == 404

    # Same tenant delete works.
    response = client.delete(
        f"/api/workspaces/{ws_a['id']}/chats/{chat['id']}",
        params={"confirmation_token": token},
        headers={"x-tenant-id": "tenant-a"},
    )
    assert response.status_code == 204


def test_ollama_remains_configurable_when_hidden(client: TestClient) -> None:
    """Providers hidden from the UI can still be configured via PATCH."""

    workspace_id = _demo_workspace_id(client)
    response = client.patch(
        f"/api/workspaces/{workspace_id}/providers/ollama",
        json={"is_enabled": True, "model_default": "llama3.1"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["is_enabled"] is True

    response = client.get(f"/api/workspaces/{workspace_id}/providers")
    slugs = {p["provider_slug"] for p in response.json()["providers"]}
    assert "ollama" not in slugs
    assert "openai" in slugs
    assert "kimi" in slugs


def test_fallback_uses_kimi_when_openai_has_no_key(client: TestClient) -> None:
    """With OpenAI unconfigured and Kimi configured, only Kimi is available for routing."""

    workspace_id = _demo_workspace_id(client)

    # Configure OpenAI without key and Kimi with key.
    client.patch(
        f"/api/workspaces/{workspace_id}/providers/openai",
        json={"is_enabled": True, "model_default": "gpt-4o-mini", "priority": 5},
    )
    client.patch(
        f"/api/workspaces/{workspace_id}/providers/kimi",
        json={"api_key": "sk-kimi1234567890123456", "model_default": "moonshot-v1-8k", "priority": 10, "is_enabled": True},
    )

    status = client.get(f"/api/workspaces/{workspace_id}/router/status").json()
    openai_status = next(p for p in status["providers"] if p["provider_slug"] == "openai")
    kimi_status = next(p for p in status["providers"] if p["provider_slug"] == "kimi")
    assert openai_status["available"] is False
    assert kimi_status["available"] is True

    # Only Kimi appears in the ordered available list.
    available = [p["provider_slug"] for p in status["providers"] if p["available"]]
    assert available == ["kimi"]


# -----------------------------------------------------------------------------
# Kimi/Moonshot provider fixes (Post-SL1a v3)
# -----------------------------------------------------------------------------


def test_kimi_defaults_base_url_moonshot() -> None:
    """KimiProvider must default to the live Moonshot endpoint, not the old .cn."""

    from app.src.router.models import ProviderConfig
    from app.src.router.providers import KimiProvider

    config = ProviderConfig(
        provider_slug="kimi",
        api_key="sk-test1234567890123456",
        base_url=None,
        model_default="moonshot-v1-8k",
        priority=10,
        is_enabled=True,
    )
    provider = KimiProvider(config)
    assert provider._client_base_url() == "https://api.moonshot.ai/v1"


def test_kimi_probar_surfaces_real_error(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """A provider failure must expose the underlying HTTP diagnostic, not a generic string."""

    from app.src import api
    from app.src.router import Router, RouterSettings
    from app.src.router.models import ProviderConfig
    from app.src.router.providers import Provider, ProviderError

    class FailingKimi(Provider):
        requires_api_key = True

        def __init__(self, config: ProviderConfig) -> None:
            self.config = config

        @property
        def provider_slug(self) -> str:
            return self.config.provider_slug

        def is_available(self) -> bool:
            return True

        def complete(self, request: Any) -> Any:
            raise ProviderError(
                "kimi",
                "provider_request_failed",
                detail="401 - Incorrect API key provided",
            )

    config = ProviderConfig(
        provider_slug="kimi",
        api_key="sk-test1234567890123456",
        model_default="moonshot-v1-8k",
        priority=10,
        is_enabled=True,
    )
    router = Router(settings=RouterSettings(), providers={"kimi": FailingKimi(config)})
    monkeypatch.setattr(api, "build_router", lambda user_id=None: router)

    workspace_id = _demo_workspace_id(client)
    response = client.post(f"/api/workspaces/{workspace_id}/providers/kimi/test")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ok"] is False
    assert "Incorrect API key" in data["error"]


def test_kimi_models_fetched_from_provider(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful provider test must return the live model list for the UI dropdown."""

    from app.src import api
    from app.src.router import CompletionResult, Router, RouterSettings
    from app.src.router.models import ProviderConfig
    from app.src.router.providers import Provider

    class WorkingKimi(Provider):
        requires_api_key = True

        def __init__(self, config: ProviderConfig) -> None:
            self.config = config

        @property
        def provider_slug(self) -> str:
            return self.config.provider_slug

        def is_available(self) -> bool:
            return True

        def complete(self, request: Any) -> CompletionResult:
            return CompletionResult(
                content="ok",
                model=request.model or self.config.model_default,
                provider_slug="kimi",
                input_tokens=1,
                output_tokens=1,
                cost_usd=0.0,
                duration_ms=1,
            )

        def list_models(self) -> list[str]:
            return ["moonshot-v1-8k", "moonshot-v1-32k"]

    config = ProviderConfig(
        provider_slug="kimi",
        api_key="sk-test1234567890123456",
        model_default="moonshot-v1-8k",
        priority=10,
        is_enabled=True,
    )
    router = Router(settings=RouterSettings(), providers={"kimi": WorkingKimi(config)})
    monkeypatch.setattr(api, "build_router", lambda user_id=None: router)

    workspace_id = _demo_workspace_id(client)
    response = client.post(f"/api/workspaces/{workspace_id}/providers/kimi/test")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ok"] is True
    assert data["models"] == ["moonshot-v1-8k", "moonshot-v1-32k"]


def test_kimi_routes_when_configured(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """When Kimi is the only available provider, chat completions route through it."""

    from app.src import api
    from app.src.router import CompletionResult, Router, RouterSettings
    from app.src.router.models import ProviderConfig
    from app.src.router.providers import Provider

    class WorkingKimi(Provider):
        requires_api_key = True

        def __init__(self, config: ProviderConfig) -> None:
            self.config = config

        @property
        def provider_slug(self) -> str:
            return self.config.provider_slug

        def is_available(self) -> bool:
            return True

        def complete(self, request: Any) -> CompletionResult:
            return CompletionResult(
                content="Respuesta de Kimi",
                model=request.model or self.config.model_default,
                provider_slug="kimi",
                input_tokens=2,
                output_tokens=3,
                cost_usd=0.00001,
                duration_ms=10,
            )

    config = ProviderConfig(
        provider_slug="kimi",
        api_key="sk-kimi1234567890123456",
        model_default="moonshot-v1-8k",
        priority=10,
        is_enabled=True,
    )
    router = Router(settings=RouterSettings(), providers={"kimi": WorkingKimi(config)})
    monkeypatch.setattr(api, "build_router", lambda user_id=None: router)

    workspace_id = _demo_workspace_id(client)
    chat = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Kimi routing"},
    ).json()

    response = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}/completions",
        json={"message": "hola", "provider_slug": "kimi", "model": "moonshot-v1-8k"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["provider_slug"] == "kimi"
    assert data["model"] == "moonshot-v1-8k"


class _FakeKimiModelResponse:
    data = [type("M", (), {"id": "moonshot-v1-cn"})()]


class _FakeKimiModels:
    def list(self):
        return _FakeKimiModelResponse()


class _FakeKimiCNClient:
    models = _FakeKimiModels()

    def chat_completions_create(self, **kwargs):
        from app.src.router.models import CompletionResult
        return CompletionResult(
            content="ok-cn",
            model=kwargs.get("model", "moonshot-v1-8k"),
            provider_slug="kimi",
            input_tokens=1,
            output_tokens=1,
            cost_usd=0.0,
            duration_ms=1,
        )


def _make_auth_exception() -> Exception:
    exc = Exception("auth failed")
    exc.message = "Error code: 401 - {'error': {'message': 'Invalid Authentication', 'type': 'invalid_authentication_error'}}"
    exc.body = {"message": "Invalid Authentication", "type": "invalid_authentication_error"}
    return exc


def test_kimi_falls_back_to_cn_endpoint_on_auth_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """If the .ai endpoint rejects the key with 401, Kimi should try .cn automatically."""

    from app.src.router.models import ProviderConfig
    from app.src.router.providers import KimiProvider

    config = ProviderConfig(
        provider_slug="kimi",
        api_key="sk-test1234567890123456",
        model_default="moonshot-v1-8k",
        priority=10,
        is_enabled=True,
    )
    provider = KimiProvider(config)

    def fake_build_client(self: Any) -> Any:
        if self.config.base_url == "https://api.moonshot.cn/v1":
            return _FakeKimiCNClient()
        raise _make_auth_exception()

    monkeypatch.setattr("app.src.router.providers._OpenAICompatibleProvider._build_client", fake_build_client)

    models = provider.list_models()
    assert models == ["moonshot-v1-cn"]


def test_kimi_does_not_fallback_on_non_auth_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A 404 or network error should not trigger the .cn fallback."""

    from app.src.router.models import ProviderConfig
    from app.src.router.providers import KimiProvider, ProviderError

    config = ProviderConfig(
        provider_slug="kimi",
        api_key="sk-test1234567890123456",
        model_default="moonshot-v1-8k",
        priority=10,
        is_enabled=True,
    )
    provider = KimiProvider(config)

    def fake_build_client(self: Any) -> Any:
        exc = Exception("not found")
        exc.message = "Error code: 404 - {'error': {'message': 'Not Found'}}"
        raise exc

    monkeypatch.setattr("app.src.router.providers._OpenAICompatibleProvider._build_client", fake_build_client)

    with pytest.raises(ProviderError):
        provider.list_models()



def test_kimi_code_key_routes_to_coding_endpoint() -> None:
    """Keys prefixed sk-kimi- must use the Kimi Code endpoint and User-Agent."""

    from app.src.router.models import ProviderConfig
    from app.src.router.providers import KIMI_CODE_BASE_URL, KimiProvider

    config = ProviderConfig(
        provider_slug="kimi",
        api_key="sk-kimi-1234567890123456",
        base_url=None,
        model_default="kimi-for-coding",
        priority=10,
        is_enabled=True,
    )
    provider = KimiProvider(config)
    assert provider._client_base_url() == KIMI_CODE_BASE_URL
    assert provider._client_default_headers() == {"User-Agent": "KimiCLI/1.30.0"}


def test_kimi_code_key_keeps_explicit_base_url() -> None:
    """A user-provided base URL must not be overwritten by the code-key heuristic."""

    from app.src.router.models import ProviderConfig
    from app.src.router.providers import KimiProvider

    config = ProviderConfig(
        provider_slug="kimi",
        api_key="sk-kimi-1234567890123456",
        base_url="https://api.moonshot.cn/v1",
        model_default="kimi-for-coding",
        priority=10,
        is_enabled=True,
    )
    provider = KimiProvider(config)
    assert provider._client_base_url() == "https://api.moonshot.cn/v1"


def test_registry_picks_kimi_code_model_for_code_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """build_router must select a coding-capable default model for sk-kimi- keys."""

    monkeypatch.setenv("KIMI_API_KEY", "sk-kimi-1234567890123456")
    from app.src.router.registry import build_router

    router = build_router()
    kimi = router.providers["kimi"]
    assert kimi.config.base_url == "https://api.kimi.com/coding/v1"
    assert kimi.config.model_default == "kimi-for-coding"


def test_provider_test_uses_draft_overrides(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """The test endpoint must use draft api_key/base_url without persisting them."""

    from app.src import api
    from app.src.router import CompletionResult, Router, RouterSettings
    from app.src.router.models import ProviderConfig
    from app.src.router.providers import Provider

    class CapturingKimi(Provider):
        requires_api_key = True

        def __init__(self, config: ProviderConfig) -> None:
            self.config = config

        @property
        def provider_slug(self) -> str:
            return self.config.provider_slug

        def is_available(self) -> bool:
            return True

        def complete(self, request: Any) -> CompletionResult:
            return CompletionResult(
                content="ok",
                model=request.model or self.config.model_default,
                provider_slug="kimi",
                input_tokens=1,
                output_tokens=1,
                cost_usd=0.0,
                duration_ms=1,
            )

        def list_models(self) -> list[str]:
            return [self.config.model_default or "unknown"]

    config = ProviderConfig(
        provider_slug="kimi",
        api_key="stored-key",
        base_url="https://api.moonshot.ai/v1",
        model_default="moonshot-v1-8k",
        priority=10,
        is_enabled=True,
    )
    router = Router(settings=RouterSettings(), providers={"kimi": CapturingKimi(config)})
    monkeypatch.setattr(api, "build_router", lambda user_id=None: router)

    workspace_id = _demo_workspace_id(client)
    response = client.post(
        f"/api/workspaces/{workspace_id}/providers/kimi/test",
        json={"api_key": "draft-key", "base_url": "https://api.kimi.com/coding/v1", "model_default": "kimi-for-coding"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["ok"] is True
    assert data["model"] == "kimi-for-coding"
    assert data["models"] == ["kimi-for-coding"]

    # Stored config must remain untouched.
    cfg_response = client.get(f"/api/workspaces/{workspace_id}/providers")
    stored = next(p for p in cfg_response.json()["providers"] if p["provider_slug"] == "kimi")
    assert stored["api_key_masked"] is None
    assert stored["base_url"] is None
    assert stored["model_default"] == "moonshot-v1-8k"
