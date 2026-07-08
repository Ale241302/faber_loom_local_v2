"""E3-4 Wave 0: C0-1 informal interaction capture."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("FABERLOOM_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

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


def test_capture_informal_interaction_creates_hitl_draft(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import capture_informal_interaction

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    with db_session() as conn:
        result = capture_informal_interaction(
            ctx,
            conn,
            raw_text="El cliente dice que paga el viernes 10 de julio",
            source_type="whatsapp",
            source_locator="whatsapp:+1234567890:msg-001",
            unit_of_work_id="quote-123",
        )

    assert result["status"] == "pending_hitl"
    assert "draft_id" in result
    assert result["classification"]["label"] == "other"


def test_approve_informal_capture_materializes_citable_fact(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import approve_informal_capture, capture_informal_interaction

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    with db_session() as conn:
        captured = capture_informal_interaction(
            ctx,
            conn,
            raw_text="Acordamos envío parcial de 100 pares el lunes.",
            source_type="voice",
            source_locator="call:+50600000000:rec-002",
        )
        approved = approve_informal_capture(
            ctx,
            conn,
            draft_id=captured["draft_id"],
            confirmed=True,
            reason="Cliente confirmó por teléfono",
        )

    assert approved["status"] == "citable"
    assert approved["kb_fact_id"]
    assert approved["source_id"]

    # Verify the fact is queryable as a real KB row.
    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM kb_fact WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (approved["kb_fact_id"], workspace_id, "default"),
        ).fetchone()
        assert row is not None
        assert "Acordamos envío parcial" in row["field_value"]
