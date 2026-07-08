"""E3-4: global skill catalog and '/' chat context."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

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
            content="Fake reply",
            model=request.model or "fake-model",
            provider_slug="fake",
            input_tokens=5,
            output_tokens=3,
            cost_usd=0.0,
            duration_ms=7,
        )


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
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

    from app.src import audit
    from app.src.main import create_app
    import app.src.api as api_module
    from app.src.router import cost as cost_module

    monkeypatch.setitem(cost_module.MODEL_ALLOWLIST, "fake", {"fake-model"})
    monkeypatch.setattr(
        api_module,
        "build_router",
        lambda user_id=None, tenant_id=None, **kwargs: Router(providers=[FakeProvider()]),
    )

    audit.audit_writer.audit_path = tmp_path / "audit.jsonl"
    with TestClient(create_app()) as test_client:
        yield test_client


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def test_global_skill_catalog_seeded(client: TestClient) -> None:
    res = client.get("/api/skills")
    assert res.status_code == 200
    data = res.json()
    assert len(data["skills"]) >= 14
    skill_ids = {s["skill_id"] for s in data["skills"]}
    assert "SKILL_FE_STATUS_CHECK" in skill_ids
    assert "SKILL_CO_DUNNING_FE" in skill_ids


def test_global_skill_catalog_filter_by_pack(client: TestClient) -> None:
    res = client.get("/api/skills?pack_id=wtp_cobranza")
    assert res.status_code == 200
    data = res.json()
    assert len(data["skills"]) >= 6
    assert all(s["pack_id"] == "wtp_cobranza" for s in data["skills"])


def test_global_skill_catalog_query(client: TestClient) -> None:
    res = client.get("/api/skills?query=retencion")
    assert res.status_code == 200
    data = res.json()
    assert any("retencion" in s["name"].lower() for s in data["skills"])


def test_chat_completion_with_skill_context(client: TestClient) -> None:
    ws = client.get("/api/workspaces").json()["workspaces"][0]["id"]
    chat = client.post(
        f"/api/workspaces/{ws}/chats",
        json={"title": "Skills"},
        headers=_headers("owner"),
    ).json()
    skills = client.get("/api/skills").json()["skills"]
    skill_ids = [s["skill_id"] for s in skills[:2]]

    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "Revisa estas facturas", "skill_ids": skill_ids},
        headers=_headers("owner"),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["message"]["content"] == "Fake reply"


def test_chat_completion_rejects_unknown_skill(client: TestClient) -> None:
    ws = client.get("/api/workspaces").json()["workspaces"][0]["id"]
    chat = client.post(
        f"/api/workspaces/{ws}/chats",
        json={"title": "Bad skill"},
        headers=_headers("owner"),
    ).json()

    response = client.post(
        f"/api/workspaces/{ws}/chats/{chat['id']}/completions",
        json={"message": "hola", "skill_ids": ["SKILL_DOES_NOT_EXIST"]},
        headers=_headers("owner"),
    )
    assert response.status_code == 422
