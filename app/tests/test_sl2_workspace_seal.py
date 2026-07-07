"""SL2: workspace seal and cross-workspace isolation tests."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
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


def test_workspace_has_unique_seal_id(client: TestClient) -> None:
    from app.src.db import connect

    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    with connect() as conn:
        for workspace in workspaces:
            row = conn.execute(
                "SELECT seal_id FROM workspace WHERE id = ?", (workspace["id"],)
            ).fetchone()
            assert row and row["seal_id"]
            assert len(row["seal_id"]) >= 16
    with connect() as conn:
        seals = {
            row["seal_id"]
            for row in conn.execute("SELECT seal_id FROM workspace").fetchall()
        }
        workspace_count = conn.execute("SELECT COUNT(*) FROM workspace").fetchone()[0]
    assert len(seals) == workspace_count


def test_seal_is_distinct_per_workspace(client: TestClient) -> None:
    from app.src.db import connect

    a = client.post("/api/workspaces", json={"name": "Alpha"})
    b = client.post("/api/workspaces", json={"name": "Beta"})
    assert a.status_code == 201
    assert b.status_code == 201
    with connect() as conn:
        a_seal = conn.execute(
            "SELECT seal_id FROM workspace WHERE id = ?", (a.json()["id"],)
        ).fetchone()["seal_id"]
        b_seal = conn.execute(
            "SELECT seal_id FROM workspace WHERE id = ?", (b.json()["id"],)
        ).fetchone()["seal_id"]
    assert a_seal != b_seal


def test_kb_source_is_cross_workspace_isolated(client: TestClient) -> None:
    a = client.post("/api/workspaces", json={"name": "Alpha"}).json()
    b = client.post("/api/workspaces", json={"name": "Beta"}).json()

    source = client.post(
        f"/api/workspaces/{a['id']}/kb/sources",
        json={"title": "Alpha data", "type": "md", "content_text": "Alpha only"},
    )
    assert source.status_code == 201
    source_id = source.json()["id"]

    # Workspace B cannot see the source.
    response_b = client.get(f"/api/workspaces/{b['id']}/kb/sources/{source_id}")
    assert response_b.status_code == 404

    # Workspace A can.
    response_a = client.get(f"/api/workspaces/{a['id']}/kb/sources/{source_id}")
    assert response_a.status_code == 200


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def test_draft_is_cross_workspace_isolated(client: TestClient) -> None:
    a = client.post("/api/workspaces", json={"name": "Alpha Draft"}).json()
    b = client.post("/api/workspaces", json={"name": "Beta Draft"}).json()

    chat_a = client.post(f"/api/workspaces/{a['id']}/chats", json={"title": "Chat A"})
    assert chat_a.status_code == 201
    chat_id = chat_a.json()["id"]

    draft = client.post(
        f"/api/workspaces/{a['id']}/drafts",
        json={"chat_id": chat_id, "user_request": "test"},
    )
    assert draft.status_code in (201, 503)
    if draft.status_code == 201:
        draft_id = draft.json()["id"]
        response_b = client.get(f"/api/workspaces/{b['id']}/drafts/{draft_id}")
        assert response_b.status_code == 404
