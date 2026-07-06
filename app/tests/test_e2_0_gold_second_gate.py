"""E2-0/E2-2 — Second gate gold loop tests.

Promoting a gold candidate with hard fields requires an independent verifier
who is not the same actor that approved the originating routine run.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import (
    approve_routine_run,
    create_routine,
    create_routine_run,
    create_workspace,
    db_session,
    transaction,
)
from app.src.gold import list_gold_candidates, promote_gold_candidate
from app.src.models import WorkspaceCreate


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_DEV_TRUST_HEADERS", "true")

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


def _seed_run(client: TestClient) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Create a workspace, routine and a low-edit run that yields a gold candidate."""

    response = client.post("/api/workspaces", json={"name": "Gold Gate"})
    assert response.status_code == 201, response.text
    workspace = response.json()

    ctx = Context(workspace_id=workspace["id"], tenant_id="default", user_id="am_a", actor_id="am_a")
    with db_session() as conn:
        with transaction(conn):
            workspace_row = create_workspace(
                Context(workspace_id="__system__", tenant_id="default"),
                conn,
                WorkspaceCreate(name="Gold Gate", slug="gold-gate"),
            )
            # Use the API-created workspace id; create_workspace above is just to satisfy FK.
            routine = create_routine(
                ctx,
                conn,
                name="Cotizador",
                skill_md="# Cotizador\nGenera cotizaciones.",
                schema_output_json='{"type": "object"}',
            )
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"client": "Acme"},
                output_json={"price": "USD 12.50", "currency": "USD"},
                evidence_json=[],
                status="requires_hitl",
                edit_pct=0.05,
            )
            approved = approve_routine_run(ctx, conn, run["id"], approved_by="am_a")
            assert approved is not None

    # Reload candidate from DB via repository.
    with db_session() as conn:
        candidates = list_gold_candidates(ctx, conn, routine_id=routine["id"])
    assert len(candidates) == 1
    return workspace, routine, candidates[0]


def test_promote_gold_requires_independent_verifier_for_hard_fields(client: TestClient) -> None:
    """Hard-field gold promotion fails when verifier equals promoter."""

    workspace, routine, candidate = _seed_run(client)
    ctx = Context(workspace_id=workspace["id"], tenant_id="default", user_id="am_a", actor_id="am_a")

    with db_session() as conn:
        with pytest.raises(ValueError, match="promoter and verifier must be different actors"):
            promote_gold_candidate(
                ctx,
                conn,
                candidate["id"],
                learned_output_json={"price": "USD 12.50"},
                approved_by="am_a",
                verified_by="am_a",
            )


def test_promote_gold_succeeds_with_independent_verifier(client: TestClient) -> None:
    """Hard-field gold promotion succeeds with a different verifier."""

    workspace, routine, candidate = _seed_run(client)
    ctx = Context(workspace_id=workspace["id"], tenant_id="default", user_id="curator_b", actor_id="curator_b")

    with db_session() as conn:
        promoted = promote_gold_candidate(
            ctx,
            conn,
            candidate["id"],
            learned_output_json={"price": "USD 12.50"},
            approved_by="am_a",
            verified_by="curator_b",
        )
    assert promoted is not None
    assert promoted["approved"] == 1
    assert promoted["approved_by"] == "am_a"
    assert promoted["verified_by"] == "curator_b"
