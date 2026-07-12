"""E4-5 — Memoria viva (CAPA 1 personal) integration tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.living_agent.memory import (
    apply_memory_proposal,
    build_memory_context,
    detect_personal_memory_patterns,
    get_learning_state,
    ignore_memory_proposal,
    list_memory_proposals,
    orchestrate_memory_proposals,
    recall_personal_blocks,
)
from app.src.living_agent.feedback import record_message_feedback


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

    from app.src.router import cost as cost_module

    monkeypatch.setitem(cost_module.MODEL_ALLOWLIST, "fake", {"fake-model"})
    monkeypatch.setattr(api_module, "build_router", lambda user_id=None, tenant_id=None, **kwargs: Router(providers=[FakeProvider()]))

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _workspace_id(client: TestClient) -> str:
    return client.get("/api/workspaces").json()["workspaces"][0]["id"]


def _headers(user: str = "test", role: str = "owner") -> dict[str, str]:
    return {"x-user-id": user, "x-actor-id": user, "x-actor-role": role}


def _assistant_message_id(client: TestClient, workspace_id: str, user: str = "test") -> str:
    chat = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "Memory"},
        headers=_headers(user),
    ).json()
    # Create a user message so the chat is not empty.
    res = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}/completions",
        json={"message": "hello", "mode": "manual", "provider_slug": "fake", "model": "fake-model"},
        headers=_headers(user),
    )
    assert res.status_code == 200, res.text
    messages = client.get(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}/messages",
        headers=_headers(user),
    ).json()
    assistant = [m for m in messages if m["role"] == "assistant"]
    assert assistant, "expected an assistant message"
    return chat["id"], assistant[0]["id"]


def test_feedback_reason_validation(client: TestClient) -> None:
    ws = _workspace_id(client)
    chat_id, message_id = _assistant_message_id(client, ws)
    res = client.post(
        f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
        json={"outcome": "rejected", "reason": "not_a_reason"},
        headers=_headers(),
    )
    assert res.status_code == 422
    assert "Invalid feedback reason" in res.json()["detail"]


def test_two_step_feedback_persists_reason(client: TestClient) -> None:
    """UI sends outcome first, then the same outcome with a reason."""

    ws = _workspace_id(client)
    chat_id, message_id = _assistant_message_id(client, ws)

    # Step 1: thumbs down, no reason.
    res1 = client.post(
        f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
        json={"outcome": "rejected"},
        headers=_headers(),
    )
    assert res1.status_code == 200

    # Step 2: same outcome with a typed reason.
    res2 = client.post(
        f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
        json={"outcome": "rejected", "reason": "too_long"},
        headers=_headers(),
    )
    assert res2.status_code == 200

    # Detector must see the reason and generate a proposal.
    for _ in range(2):
        chat_id2, message_id2 = _assistant_message_id(client, ws)
        client.post(
            f"/api/workspaces/{ws}/chats/{chat_id2}/messages/{message_id2}/feedback",
            json={"outcome": "rejected", "reason": "too_long"},
            headers=_headers(),
        )

    index = client.post(f"/api/workspaces/{ws}/memory/index", headers=_headers()).json()
    assert index["findings"] >= 1


def test_feedback_increments_unconsolidated_counter(client: TestClient) -> None:
    ws = _workspace_id(client)
    chat_id, message_id = _assistant_message_id(client, ws)

    res = client.post(
        f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
        json={"outcome": "rejected", "reason": "too_long"},
        headers=_headers(),
    )
    assert res.status_code == 200

    state = client.get(f"/api/workspaces/{ws}/memory/learning-state", headers=_headers()).json()
    assert state["unconsolidated_count"] == 1
    assert state["level"] == "cool"


def test_detector_creates_proposal_after_threshold(client: TestClient) -> None:
    ws = _workspace_id(client)
    for _ in range(3):
        chat_id, message_id = _assistant_message_id(client, ws)
        res = client.post(
            f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
            json={"outcome": "rejected", "reason": "too_long"},
            headers=_headers(),
        )
        assert res.status_code == 200

    proposals_before = client.get(
        f"/api/workspaces/{ws}/memory/proposals?state=pending", headers=_headers()
    ).json()
    assert len(proposals_before) == 0

    index = client.post(f"/api/workspaces/{ws}/memory/index", headers=_headers()).json()
    assert index["findings"] >= 1

    proposals_after = client.get(
        f"/api/workspaces/{ws}/memory/proposals?state=pending", headers=_headers()
    ).json()
    assert len(proposals_after) == 1
    assert "largas" in proposals_after[0]["summary"].lower() or "largo" in proposals_after[0]["summary"].lower()


def test_apply_writes_memory_block_and_decrements_counter(client: TestClient) -> None:
    ws = _workspace_id(client)
    for _ in range(3):
        chat_id, message_id = _assistant_message_id(client, ws)
        client.post(
            f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
            json={"outcome": "rejected", "reason": "too_short"},
            headers=_headers(),
        )

    index = client.post(f"/api/workspaces/{ws}/memory/index", headers=_headers()).json()
    assert index["created"]
    proposal_id = index["created"][0]

    apply = client.post(
        f"/api/workspaces/{ws}/memory/proposals/{proposal_id}/apply", headers=_headers()
    ).json()
    assert apply["state"] == "applied"
    assert apply["block"]["action"] in ("created", "updated")

    state = client.get(f"/api/workspaces/{ws}/memory/learning-state", headers=_headers()).json()
    assert state["unconsolidated_count"] == 0

    blocks = client.get(f"/api/workspaces/{ws}/memory/proposals?state=applied", headers=_headers()).json()
    assert len(blocks) == 1


def test_ignore_proposal_does_not_write_block(client: TestClient) -> None:
    ws = _workspace_id(client)
    for _ in range(3):
        chat_id, message_id = _assistant_message_id(client, ws)
        client.post(
            f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
            json={"outcome": "rejected", "reason": "off_topic"},
            headers=_headers(),
        )

    index = client.post(f"/api/workspaces/{ws}/memory/index", headers=_headers()).json()
    proposal_id = index["created"][0]
    ignore = client.post(
        f"/api/workspaces/{ws}/memory/proposals/{proposal_id}/ignore", headers=_headers()
    ).json()
    assert ignore["state"] == "ignored"

    pending = client.get(
        f"/api/workspaces/{ws}/memory/proposals?state=pending", headers=_headers()
    ).json()
    assert len(pending) == 0
    applied = client.get(
        f"/api/workspaces/{ws}/memory/proposals?state=applied", headers=_headers()
    ).json()
    assert len(applied) == 0


def test_memory_is_private_per_user(client: TestClient) -> None:
    ws = _workspace_id(client)
    # User A creates feedback and applies a proposal.
    for _ in range(3):
        chat_id, message_id = _assistant_message_id(client, ws, user="userA")
        client.post(
            f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
            json={"outcome": "rejected", "reason": "too_long"},
            headers=_headers("userA"),
        )
    index = client.post(f"/api/workspaces/{ws}/memory/index", headers=_headers("userA")).json()
    proposal_id = index["created"][0]
    client.post(
        f"/api/workspaces/{ws}/memory/proposals/{proposal_id}/apply", headers=_headers("userA")
    )

    # User B must not see A's pending/applied proposals.
    user_b_proposals = client.get(
        f"/api/workspaces/{ws}/memory/proposals", headers=_headers("userB")
    ).json()
    assert len(user_b_proposals) == 0

    # User B feedback should start from zero unconsolidated count.
    state = client.get(f"/api/workspaces/{ws}/memory/learning-state", headers=_headers("userB")).json()
    assert state["unconsolidated_count"] == 0


def test_detector_is_read_only_never_writes_blocks(client: TestClient) -> None:
    ws = _workspace_id(client)
    for _ in range(3):
        chat_id, message_id = _assistant_message_id(client, ws)
        client.post(
            f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
            json={"outcome": "rejected", "reason": "wrong"},
            headers=_headers(),
        )

    # Only index (detector + orchestrator) runs; no apply.
    client.post(f"/api/workspaces/{ws}/memory/index", headers=_headers()).json()
    applied = client.get(
        f"/api/workspaces/{ws}/memory/proposals?state=applied", headers=_headers()
    ).json()
    assert len(applied) == 0


def test_memory_injection_includes_approved_block(client: TestClient) -> None:
    ws = _workspace_id(client)
    for _ in range(3):
        chat_id, message_id = _assistant_message_id(client, ws)
        client.post(
            f"/api/workspaces/{ws}/chats/{chat_id}/messages/{message_id}/feedback",
            json={"outcome": "rejected", "reason": "too_long"},
            headers=_headers(),
        )
    index = client.post(f"/api/workspaces/{ws}/memory/index", headers=_headers()).json()
    proposal_id = index["created"][0]
    client.post(
        f"/api/workspaces/{ws}/memory/proposals/{proposal_id}/apply", headers=_headers()
    )

    # Use DB directly to verify recall is scoped and build_memory_context includes the block.
    from app.src.db import connect

    with connect() as conn:
        ctx = Context(workspace_id=ws, tenant_id="default", user_id="test")
        blocks = recall_personal_blocks(ctx, conn)
        assert len(blocks) == 1
        context = build_memory_context(ctx, conn, query="largas")
        assert "preferencias personales del usuario" in context
        assert "conciso" in context
