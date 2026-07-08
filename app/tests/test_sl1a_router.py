"""SL1a router + chat backend tests."""

from __future__ import annotations

import json
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

    # Ensure no provider keys or router config leak into tests.
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


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def test_schema_version_is_current(client: TestClient) -> None:
    from app.src.models import SCHEMA_VERSION

    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["schema_version"] == SCHEMA_VERSION


def test_schema_contains_usage_record_table(client: TestClient) -> None:
    from app.src.db import connect

    with connect() as conn:
        tables = {
            row["name"]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    assert "usage_record" in tables


def test_router_status_without_configured_providers(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.get(f"/api/workspaces/{workspace_id}/router/status")
    assert response.status_code == 200
    data = response.json()
    assert data["budget_cap_usd"] == 5.0
    assert data["spent_usd"] == 0.0
    assert data["provider_allowlist"] is None
    providers = {p["provider_slug"]: p for p in data["providers"]}
    assert "openai" in providers
    assert providers["openai"]["configured"] is False
    assert providers["openai"]["available"] is False
    assert providers["openai"]["reason"] == "missing_api_key"


def test_chat_crud(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)

    response = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Planning session"},
    )
    assert response.status_code == 201
    chat = response.json()
    assert chat["title"] == "Planning session"
    assert chat["workspace_id"] == workspace_id
    chat_id = chat["id"]

    response = client.get(f"/api/workspaces/{workspace_id}/chats")
    assert response.status_code == 200
    chats = response.json()
    assert any(c["id"] == chat_id for c in chats)

    response = client.get(f"/api/workspaces/{workspace_id}/chats/{chat_id}")
    assert response.status_code == 200
    assert response.json()["id"] == chat_id

    response = client.get(f"/api/workspaces/{workspace_id}/chats/{chat_id}/messages")
    assert response.status_code == 200
    assert response.json() == []


def test_chat_rejects_blank_title(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "   "},
    )
    assert response.status_code == 422


def test_chat_completion_returns_503_when_no_providers(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    response = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "No providers chat"},
    )
    assert response.status_code == 201
    chat_id = response.json()["id"]

    response = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
        json={"message": "Hello"},
    )
    assert response.status_code == 503


def test_chat_completion_rejects_disallowed_model(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace_id = _demo_workspace_id(client)
    chat_id = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Model test"},
    ).json()["id"]

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    response = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
        json={"message": "Hi", "provider_slug": "openai", "model": "gpt-4-turbo"},
    )
    assert response.status_code == 422
    assert "gpt-4-turbo" in response.json()["detail"]


def test_chat_completion_with_fake_provider(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    db_path = tmp_path / "faberloom.sqlite3"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    audit_writer.audit_path = tmp_path / "audit.jsonl"

    received_requests: list[CompletionRequest] = []

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
            received_requests.append(request)
            return CompletionResult(
                content="Fake assistant reply",
                model=request.model or "fake-model",
                provider_slug="fake",
                input_tokens=10,
                output_tokens=4,
                cost_usd=0.0,
                duration_ms=12,
            )

    import app.src.api as api_module

    original_build_router = api_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    cost_module.MODEL_ALLOWLIST["fake"] = {"fake-model"}

    def fake_build_router(user_id: str | None = None, *, tenant_id: str | None = None, **kwargs) -> Router:
        return Router(providers=[FakeProvider()])

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

    try:
        with TestClient(create_app()) as client:
            workspace_id = _demo_workspace_id(client)
            response = client.post(
                f"/api/workspaces/{workspace_id}/chats",
                json={"title": "Fake chat"},
            )
            assert response.status_code == 201
            chat_id = response.json()["id"]

            response = client.post(
                f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
                json={"message": "Hi"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["provider_slug"] == "fake"
            assert data["model"] == "fake-model"
            assert data["input_tokens"] == 10
            assert data["output_tokens"] == 4
            assert data["cost_usd"] == 0.0
            assert data["message"]["role"] == "assistant"
            assert data["message"]["content"] == "Fake assistant reply"

            messages = client.get(f"/api/workspaces/{workspace_id}/chats/{chat_id}/messages").json()
            assert len(messages) == 2
            assert messages[0]["role"] == "user"
            assert messages[0]["content"] == "Hi"
            assert messages[1]["role"] == "assistant"
            assert messages[1]["content"] == "Fake assistant reply"
            route = messages[1]["route"]
            assert route["provider_slug"] == "fake"
            assert route["model"] == "fake-model"
            assert route["input_tokens"] == 10
            assert route["output_tokens"] == 4
            assert route["cost_usd"] == 0.0
            assert route["duration_ms"] == 12
            assert "budget_usd" in route
            assert "budget_cap_usd" in route

            # The actual user message must reach the provider.
            assert len(received_requests) == 1
            last_message = received_requests[0].messages[-1]
            assert last_message["role"] == "user"
            assert last_message["content"] == "Hi"

            usage = client.get(f"/api/workspaces/{workspace_id}/usage").json()
            assert len(usage) == 1
            assert usage[0]["provider_slug"] == "fake"
            assert usage[0]["status"] == "succeeded"
            assert usage[0]["input_tokens"] == 10
            assert usage[0]["chat_id"] == chat_id
            assert usage[0]["source_version"] == cost_module.PRICING_VERSION
            assert json.loads(usage[0]["attempts_json"])[-1]["status"] == "succeeded"

            # Exactly one chat.completion audit line; no duplicates.
            lines = audit_writer.audit_path.read_text(encoding="utf-8").strip().splitlines()
            completion_actions = [json.loads(line)["action"] for line in lines if json.loads(line)["action"].startswith("chat.completion")]
            assert completion_actions.count("chat.completion") == 1
            assert "chat.completion_failed" not in completion_actions
    finally:
        cost_module.MODEL_ALLOWLIST.clear()
        cost_module.MODEL_ALLOWLIST.update(original_allowlist)
        monkeypatch.setattr(api_module, "build_router", original_build_router)


def test_fallback_uses_allowed_model_per_provider(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    db_path = tmp_path / "faberloom.sqlite3"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import ProviderError
    from app.src.router.providers import Provider

    audit_writer.audit_path = tmp_path / "audit.jsonl"

    received_models: dict[str, str] = {}

    class FailingProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="openai",
                    api_key=None,
                    model_default="gpt-4o-mini",
                    priority=1,
                    is_enabled=True,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            received_models["openai"] = request.model
            raise ProviderError("openai", "simulated failure")

    class BackupProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="anthropic",
                    api_key=None,
                    model_default="claude-3-5-sonnet",
                    priority=2,
                    is_enabled=True,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            received_models["anthropic"] = request.model
            return CompletionResult(
                content="Backup reply",
                model=request.model,
                provider_slug="anthropic",
                input_tokens=5,
                output_tokens=2,
                cost_usd=0.0,
                duration_ms=1,
            )

    import app.src.api as api_module

    original_build_router = api_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}

    def fake_build_router(user_id: str | None = None, *, tenant_id: str | None = None, **kwargs) -> Router:
        return Router(providers=[FailingProvider(), BackupProvider()])

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

    try:
        with TestClient(create_app()) as client:
            workspace_id = _demo_workspace_id(client)
            chat_id = client.post(
                f"/api/workspaces/{workspace_id}/chats",
                json={"title": "Fallback chat"},
            ).json()["id"]

            # Request a model allowed only for OpenAI; fallback must switch to
            # Anthropic's default allowed model, not reuse gpt-4o-mini.
            response = client.post(
                f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
                json={"message": "Hi", "provider_slug": "openai", "model": "gpt-4o-mini"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["provider_slug"] == "anthropic"
            assert data["model"] == "claude-3-5-sonnet"
            assert data["message"]["content"] == "Backup reply"
            assert received_models.get("openai") == "gpt-4o-mini"
            assert received_models.get("anthropic") == "claude-3-5-sonnet"
    finally:
        cost_module.MODEL_ALLOWLIST.clear()
        cost_module.MODEL_ALLOWLIST.update(original_allowlist)
        monkeypatch.setattr(api_module, "build_router", original_build_router)


def test_provider_allowlist_restricts_providers(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    db_path = tmp_path / "faberloom.sqlite3"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_PROVIDER_ALLOWLIST", "openai")

    from app.src.main import create_app

    with TestClient(create_app()) as client:
        workspace_id = _demo_workspace_id(client)
        data = client.get(f"/api/workspaces/{workspace_id}/router/status").json()
        slugs = {p["provider_slug"] for p in data["providers"] if p["allowed"]}
        assert slugs == {"openai"}


def test_accumulated_budget_cap_blocks_requests(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    db_path = tmp_path / "faberloom.sqlite3"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_BUDGET_CAP_USD", "0.05")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    audit_writer.audit_path = tmp_path / "audit.jsonl"

    class ExpensiveProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="expensive",
                    api_key=None,
                    model_default="expensive-model",
                    priority=1,
                    is_enabled=True,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            return CompletionResult(
                content="Reply",
                model="expensive-model",
                provider_slug="expensive",
                input_tokens=1000,
                output_tokens=1000,
                cost_usd=0.04,
                duration_ms=1,
            )

    import app.src.api as api_module

    original_build_router = api_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    cost_module.MODEL_ALLOWLIST["expensive"] = {"expensive-model"}

    real_router = api_module.build_router()

    def fake_build_router(user_id: str | None = None, *, tenant_id: str | None = None, **kwargs) -> Router:
        return Router(settings=real_router.settings, providers=[ExpensiveProvider()])

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

    try:
        with TestClient(create_app()) as client:
            workspace_id = _demo_workspace_id(client)
            chat_id = client.post(
                f"/api/workspaces/{workspace_id}/chats",
                json={"title": "Budget chat"},
            ).json()["id"]

            # First call spends $0.04, under the $0.05 cap.
            response = client.post(
                f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
                json={"message": "Hi"},
            )
            assert response.status_code == 200

            # Second call would exceed the cap.
            response = client.post(
                f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
                json={"message": "Hi again"},
            )
            assert response.status_code == 429
            assert "Budget cap exceeded" in response.json()["detail"]

            usage = client.get(f"/api/workspaces/{workspace_id}/usage").json()
            exceeded = [u for u in usage if u["status"] == "budget_exceeded"]
            assert len(exceeded) == 1

            # The 429 path must be audited exactly once (not duplicated in JSONL).
            lines = audit_writer.audit_path.read_text(encoding="utf-8").strip().splitlines()
            failed_events = [
                json.loads(line)
                for line in lines
                if json.loads(line)["action"] == "chat.completion_failed"
                and json.loads(line).get("payload", {}).get("reason") == "budget_exceeded"
            ]
            assert len(failed_events) == 1
    finally:
        cost_module.MODEL_ALLOWLIST.clear()
        cost_module.MODEL_ALLOWLIST.update(original_allowlist)
        monkeypatch.setattr(api_module, "build_router", original_build_router)


def test_cross_workspace_chat_isolation(client: TestClient) -> None:
    workspace_a = client.post("/api/workspaces", json={"name": "A", "slug": "a"}).json()
    workspace_b = client.post("/api/workspaces", json={"name": "B", "slug": "b"}).json()

    chat_a = client.post(
        f"/api/workspaces/{workspace_a['id']}/chats",
        json={"title": "Chat A"},
    ).json()

    # Workspace B should not see A's chat.
    response = client.get(f"/api/workspaces/{workspace_b['id']}/chats/{chat_a['id']}")
    assert response.status_code == 404

    response = client.get(f"/api/workspaces/{workspace_b['id']}/chats/{chat_a['id']}/messages")
    assert response.status_code == 404


def test_chat_events_are_mirrored_to_audit_jsonl(client: TestClient) -> None:
    from app.src.audit import audit_writer

    workspace_id = _demo_workspace_id(client)
    chat_id = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Audit chat"},
    ).json()["id"]

    lines = audit_writer.audit_path.read_text(encoding="utf-8").strip().splitlines()
    actions = [json.loads(line)["action"] for line in lines]
    assert "chat.created" in actions

    # Failed completion also audits.
    response = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
        json={"message": "Hi"},
    )
    assert response.status_code == 503

    lines = audit_writer.audit_path.read_text(encoding="utf-8").strip().splitlines()
    actions = [json.loads(line)["action"] for line in lines]
    assert "chat.completion_failed" in actions


def test_fallback_to_cheaper_provider_when_first_exceeds_budget(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    db_path = tmp_path / "faberloom.sqlite3"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_BUDGET_CAP_USD", "0.05")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    audit_writer.audit_path = tmp_path / "audit.jsonl"

    class ExpensiveProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="expensive",
                    api_key=None,
                    model_default="expensive-model",
                    priority=1,
                    is_enabled=True,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            return CompletionResult(
                content="Expensive reply",
                model="expensive-model",
                provider_slug="expensive",
                input_tokens=1000,
                output_tokens=1000,
                cost_usd=0.04,
                duration_ms=1,
            )

    class CheapProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="cheap",
                    api_key=None,
                    model_default="llama3.1",
                    priority=2,
                    is_enabled=True,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            return CompletionResult(
                content="Cheap reply",
                model="llama3.1",
                provider_slug="cheap",
                input_tokens=1,
                output_tokens=1,
                cost_usd=0.0,
                duration_ms=1,
            )

    import app.src.api as api_module

    original_build_router = api_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    cost_module.MODEL_ALLOWLIST["expensive"] = {"expensive-model"}
    cost_module.MODEL_ALLOWLIST["cheap"] = {"llama3.1"}

    real_router = api_module.build_router()

    def fake_build_router(user_id: str | None = None, *, tenant_id: str | None = None, **kwargs) -> Router:
        return Router(settings=real_router.settings, providers=[ExpensiveProvider(), CheapProvider()])

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

    try:
        with TestClient(create_app()) as client:
            workspace_id = _demo_workspace_id(client)
            chat_id = client.post(
                f"/api/workspaces/{workspace_id}/chats",
                json={"title": "Fallback budget chat"},
            ).json()["id"]

            # First call spends $0.04.
            response = client.post(
                f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
                json={"message": "Hi"},
            )
            assert response.status_code == 200
            assert response.json()["provider_slug"] == "expensive"

            # Second call: expensive would exceed cap, but cheap provider fits.
            response = client.post(
                f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
                json={"message": "Hi again"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["provider_slug"] == "cheap"
            assert data["message"]["content"] == "Cheap reply"
    finally:
        cost_module.MODEL_ALLOWLIST.clear()
        cost_module.MODEL_ALLOWLIST.update(original_allowlist)
        monkeypatch.setattr(api_module, "build_router", original_build_router)


def test_unknown_provider_slug_returns_422(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    workspace_id = _demo_workspace_id(client)
    chat_id = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Unknown provider chat"},
    ).json()["id"]

    response = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
        json={"message": "Hi", "provider_slug": "unknown-provider"},
    )
    assert response.status_code == 422
    assert "unknown-provider" in response.json()["detail"]


def test_no_providers_creates_failed_usage_record(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    chat_id = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "No provider usage chat"},
    ).json()["id"]

    response = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
        json={"message": "Hi"},
    )
    assert response.status_code == 503

    usage = client.get(f"/api/workspaces/{workspace_id}/usage").json()
    failed = [u for u in usage if u["status"] == "failed"]
    assert len(failed) == 1
    assert failed[0]["provider_slug"] == "router"
    assert "no_providers_configured" in failed[0]["error"]


def test_audit_mirror_failure_does_not_break_response(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    db_path = tmp_path / "faberloom.sqlite3"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    audit_writer.audit_path = tmp_path / "audit.jsonl"

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
                content="Reply despite mirror failure",
                model="fake-model",
                provider_slug="fake",
                input_tokens=1,
                output_tokens=1,
                cost_usd=0.0,
                duration_ms=1,
            )

    import app.src.api as api_module

    original_build_router = api_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    cost_module.MODEL_ALLOWLIST["fake"] = {"fake-model"}

    def fake_build_router(user_id: str | None = None, *, tenant_id: str | None = None, **kwargs) -> Router:
        return Router(providers=[FakeProvider()])

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

    def broken_mirror(event: Any) -> None:
        raise RuntimeError("mirror is down")

    try:
        with TestClient(create_app()) as client:
            # Break the mirror only after the app has finished its lifespan/seed.
            monkeypatch.setattr(audit_writer, "mirror", broken_mirror)
            workspace_id = _demo_workspace_id(client)
            chat_id = client.post(
                f"/api/workspaces/{workspace_id}/chats",
                json={"title": "Mirror failure chat"},
            ).json()["id"]

            response = client.post(
                f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
                json={"message": "Hi"},
            )
            assert response.status_code == 200
            assert response.json()["message"]["content"] == "Reply despite mirror failure"
    finally:
        cost_module.MODEL_ALLOWLIST.clear()
        cost_module.MODEL_ALLOWLIST.update(original_allowlist)
        monkeypatch.setattr(api_module, "build_router", original_build_router)


def test_no_allowed_model_records_usage_and_audit(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    db_path = tmp_path / "faberloom.sqlite3"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    from app.src.router.models import ProviderConfig
    from app.src.router.providers import Provider

    audit_writer.audit_path = tmp_path / "audit.jsonl"

    class MisconfiguredProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug="misconfigured",
                    api_key=None,
                    model_default="not-in-allowlist",
                    priority=1,
                    is_enabled=True,
                )
            )

        def complete(self, request):
            raise AssertionError("should not be called")

    import app.src.api as api_module

    original_build_router = api_module.build_router
    original_allowlist = {k: v.copy() for k, v in cost_module.MODEL_ALLOWLIST.items()}
    # Intentionally empty allowlist for this provider so no model is allowed.
    cost_module.MODEL_ALLOWLIST["misconfigured"] = set()

    def fake_build_router(user_id: str | None = None, *, tenant_id: str | None = None, **kwargs) -> Router:
        return Router(providers=[MisconfiguredProvider()])

    monkeypatch.setattr(api_module, "build_router", fake_build_router)

    try:
        with TestClient(create_app()) as client:
            workspace_id = _demo_workspace_id(client)
            chat_id = client.post(
                f"/api/workspaces/{workspace_id}/chats",
                json={"title": "No allowed model chat"},
            ).json()["id"]

            response = client.post(
                f"/api/workspaces/{workspace_id}/chats/{chat_id}/completions",
                json={"message": "Hi"},
            )
            assert response.status_code == 422

            usage = client.get(f"/api/workspaces/{workspace_id}/usage").json()
            failed = [u for u in usage if u["status"] == "failed"]
            assert len(failed) == 1
            assert failed[0]["provider_slug"] == "router"
            assert "no_allowed_model" in failed[0]["attempts_json"]

            lines = audit_writer.audit_path.read_text(encoding="utf-8").strip().splitlines()
            failed_events = [
                json.loads(line)
                for line in lines
                if json.loads(line)["action"] == "chat.completion_failed"
                and json.loads(line).get("payload", {}).get("reason") == "failed"
            ]
            assert len(failed_events) == 1
    finally:
        cost_module.MODEL_ALLOWLIST.clear()
        cost_module.MODEL_ALLOWLIST.update(original_allowlist)
        monkeypatch.setattr(api_module, "build_router", original_build_router)
