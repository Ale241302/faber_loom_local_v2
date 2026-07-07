"""SL3b: WorkLoom HITL queue + gold loop tests."""

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
    get_routine_run,
    list_editorial_history,
    record_routine_run_edit,
    reject_routine_run,
    transaction,
    update_routine_run_output,
)
from app.src.gold import apply_gold_to_routine, list_gold_candidates, promote_gold_candidate
from app.src.kb import insert_draft
from app.src.models import SCHEMA_VERSION, WorkspaceCreate
from app.src.workloom import list_workloom_items


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
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


def _create_workspace(client: TestClient, name: str) -> dict[str, Any]:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 201
    return response.json()


def _routine_and_run(client: TestClient, workspace_id: str):
    """Create a routine and a routine_run directly through the repository layer."""

    ctx = Context(workspace_id=workspace_id, tenant_id="default")
    with db_session() as conn:
        with transaction(conn):
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
                output_json={"price": 100, "currency": "USD"},
                evidence_json=[],
                status="requires_hitl",
            )
    return routine, run


def test_schema_has_gold_candidate_table(client: TestClient) -> None:
    from app.src.db import connect

    conn = connect()
    try:
        tables = {
            row["name"]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
    finally:
        conn.close()
    assert "gold_candidate" in tables


def test_create_routine_run_and_compute_edit_pct(client: TestClient) -> None:
    workspace = _create_workspace(client, "Edit Pct")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Cotizador")
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"client": "Acme"},
                output_json={"price": 100, "currency": "USD"},
                evidence_json=[],
                status="requires_hitl",
            )
            updated = record_routine_run_edit(
                ctx,
                conn,
                run["id"],
                edited_output_json={"price": 105, "currency": "USD"},
            )

    assert updated is not None
    assert updated["status"] == "requires_hitl"
    assert updated["edit_pct"] is not None
    assert 0 < updated["edit_pct"] <= 1


def test_approve_low_edit_generates_gold_candidate(client: TestClient) -> None:
    workspace = _create_workspace(client, "Gold Gen")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Cotizador")
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"client": "Acme"},
                output_json={"price": 100, "currency": "USD"},
                evidence_json=[],
                status="requires_hitl",
            )
            # Tiny edit should keep edit_pct <= 0.2
            update_routine_run_output(
                ctx,
                conn,
                run["id"],
                output_json={"price": 100, "currency": "USD"},
                edited_output_json={"price": 100, "currency": "USD", "note": "ok"},
                approved_by="local",
            )

    with db_session() as conn:
        approved = get_routine_run(ctx, conn, run["id"])
        candidates = list_gold_candidates(ctx, conn)

    assert approved is not None
    assert approved["status"] == "succeeded"
    assert approved["edit_pct"] <= 0.2
    assert len(candidates) == 1
    assert candidates[0]["run_id"] == run["id"]
    assert candidates[0]["routine_id"] == routine["id"]


def test_approve_high_edit_does_not_generate_gold_candidate(client: TestClient) -> None:
    workspace = _create_workspace(client, "No Gold")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Cotizador")
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"client": "Acme"},
                output_json={"price": 100, "currency": "USD"},
                evidence_json=[],
                status="requires_hitl",
            )
            update_routine_run_output(
                ctx,
                conn,
                run["id"],
                output_json={"price": 100, "currency": "USD"},
                edited_output_json={"price": 999, "currency": "EUR", "note": "rewritten"},
                approved_by="local",
            )

    with db_session() as conn:
        candidates = list_gold_candidates(ctx, conn)

    assert len(candidates) == 0


def test_reject_routine_run(client: TestClient) -> None:
    workspace = _create_workspace(client, "Reject Run")
    routine, run = _routine_and_run(client, workspace["id"])
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            rejected = reject_routine_run(ctx, conn, run["id"])

    assert rejected is not None
    assert rejected["status"] == "cancelled"


def test_list_workloom_endpoint(client: TestClient) -> None:
    workspace = _create_workspace(client, "WorkLoom Endpoint")
    routine, run = _routine_and_run(client, workspace["id"])

    response = client.get(f"/api/workspaces/{workspace['id']}/workloom")
    assert response.status_code == 200
    payload = response.json()
    assert "routine_runs" in payload
    assert "drafts" in payload
    assert "gold_candidates" in payload
    assert any(r["id"] == run["id"] for r in payload["routine_runs"])


def test_list_workloom_helper_orders_and_filters(client: TestClient) -> None:
    workspace = _create_workspace(client, "WorkLoom Filter")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        routine = create_routine(ctx, conn, name="Cotizador")
        create_routine_run(
            ctx,
            conn,
            routine_id=routine["id"],
            input_json={},
            output_json={"a": 1},
            evidence_json=[],
            status="succeeded",
        )
        hitl = create_routine_run(
            ctx,
            conn,
            routine_id=routine["id"],
            input_json={},
            output_json={"a": 2},
            evidence_json=[],
            status="requires_hitl",
        )
        items = list_workloom_items(ctx, conn)

    assert len(items["routine_runs"]) == 1
    assert items["routine_runs"][0]["id"] == hitl["id"]


def test_gold_candidates_endpoint_and_promote(client: TestClient) -> None:
    workspace = _create_workspace(client, "Gold Endpoint")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Cotizador")
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"client": "Acme"},
                output_json={"price": 100, "currency": "USD", "client": "Acme"},
                evidence_json=[],
                status="requires_hitl",
            )
            update_routine_run_output(
                ctx,
                conn,
                run["id"],
                output_json={"price": 100, "currency": "USD", "client": "Acme"},
                edited_output_json={"price": 100, "currency": "USD", "client": "Acme", "note": "ok"},
                approved_by="local",
            )

    list_response = client.get(f"/api/workspaces/{workspace['id']}/gold-candidates")
    assert list_response.status_code == 200
    candidates = list_response.json()
    assert len(candidates) == 1
    candidate_id = candidates[0]["id"]
    assert candidates[0]["approved"] == 0

    # Hard fields require a second independent verification gate.
    promote_response = client.post(
        f"/api/workspaces/{workspace['id']}/gold-candidates/{candidate_id}/promote",
        json={
            "learned_output_json": {"price": 100, "currency": "USD"},
            "verified_by": "controller",
        },
    )
    assert promote_response.status_code == 200
    promoted = promote_response.json()
    assert promoted["approved"] == 1
    assert json.loads(promoted["learned_output_json"]) == {"price": 100, "currency": "USD"}


def test_workspace_isolation_for_workloom(client: TestClient) -> None:
    alpha = _create_workspace(client, "Alpha WorkLoom")
    beta = _create_workspace(client, "Beta WorkLoom")

    ctx_alpha = Context(workspace_id=alpha["id"], tenant_id="default")
    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx_alpha, conn, name="Cotizador")
            run = create_routine_run(
                ctx_alpha,
                conn,
                routine_id=routine["id"],
                input_json={},
                output_json={"a": 1},
                evidence_json=[],
                status="requires_hitl",
            )

    alpha_response = client.get(f"/api/workspaces/{alpha['id']}/workloom")
    beta_response = client.get(f"/api/workspaces/{beta['id']}/workloom")

    assert alpha_response.status_code == 200
    assert beta_response.status_code == 200
    assert any(r["id"] == run["id"] for r in alpha_response.json()["routine_runs"])
    assert not any(r["id"] == run["id"] for r in beta_response.json()["routine_runs"])


def test_gold_candidates_are_workspace_isolated(client: TestClient) -> None:
    alpha = _create_workspace(client, "Alpha Gold")
    beta = _create_workspace(client, "Beta Gold")

    ctx_alpha = Context(workspace_id=alpha["id"], tenant_id="default")
    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx_alpha, conn, name="Cotizador")
            run = create_routine_run(
                ctx_alpha,
                conn,
                routine_id=routine["id"],
                input_json={},
                output_json={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
                evidence_json=[],
                status="requires_hitl",
            )
            update_routine_run_output(
                ctx_alpha,
                conn,
                run["id"],
                output_json={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
                edited_output_json={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "note": "ok"},
                approved_by="local",
            )

    alpha_gold = client.get(f"/api/workspaces/{alpha['id']}/gold-candidates")
    beta_gold = client.get(f"/api/workspaces/{beta['id']}/gold-candidates")

    assert alpha_gold.status_code == 200
    assert beta_gold.status_code == 200
    assert len(alpha_gold.json()) == 1
    assert len(beta_gold.json()) == 0


def test_workloom_sorted_by_urgency(client: TestClient) -> None:
    workspace = _create_workspace(client, "WorkLoom Urgency")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Cotizador")
            # Create pending HITL runs and set urgency directly.
            run_low = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={},
                output_json={"a": 1},
                evidence_json=[],
                status="requires_hitl",
            )
            run_high = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={},
                output_json={"a": 2},
                evidence_json=[],
                status="requires_hitl",
            )
            run_medium = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={},
                output_json={"a": 3},
                evidence_json=[],
                status="requires_hitl",
            )
            conn.execute(
                "UPDATE routine_run SET urgency = ? WHERE id = ?",
                (1, run_low["id"]),
            )
            conn.execute(
                "UPDATE routine_run SET urgency = ? WHERE id = ?",
                (5, run_high["id"]),
            )
            conn.execute(
                "UPDATE routine_run SET urgency = ? WHERE id = ?",
                (3, run_medium["id"]),
            )
            items = list_workloom_items(ctx, conn)

    urgencies = [r["urgency"] for r in items["routine_runs"]]
    assert urgencies == [5, 3, 1]


def test_approval_reason_is_persisted(client: TestClient) -> None:
    workspace = _create_workspace(client, "Approval Reason")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Cotizador")
            run_approve = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={},
                output_json={"a": 1},
                evidence_json=[],
                status="requires_hitl",
            )
            approved = approve_routine_run(
                ctx, conn, run_approve["id"], reason="Looks good", urgency=3
            )

    assert approved is not None
    assert approved["reason"] == "Looks good"
    assert approved["urgency"] == 3

    with db_session() as conn:
        with transaction(conn):
            run_reject = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={},
                output_json={"a": 2},
                evidence_json=[],
                status="requires_hitl",
            )
    response = client.post(
        f"/api/workspaces/{workspace['id']}/routine-runs/{run_reject['id']}/reject",
        json={"reason": "Reconsidering"},
    )
    assert response.status_code == 200
    rejected = response.json()
    assert rejected["reason"] == "Reconsidering"


def test_editorial_history_recorded(client: TestClient) -> None:
    workspace = _create_workspace(client, "Editorial History")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Cotizador")
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={},
                output_json={"a": 1},
                evidence_json=[],
                status="requires_hitl",
            )
            approve_routine_run(ctx, conn, run["id"], reason="Approved by test")

    response = client.get(f"/api/workspaces/{workspace['id']}/editorial-history")
    assert response.status_code == 200
    events = response.json()["events"]
    assert any(
        e["entity_type"] == "routine_run" and e["entity_id"] == run["id"] and e["action"] == "approved"
        for e in events
    )

    with db_session() as conn:
        with transaction(conn):
            draft = insert_draft(
                ctx,
                conn,
                chat_id=None,
                task="draft_commercial_reply",
                subject="Hi",
                body_md="Body",
                hard_facts=[],
                sources=[],
                blockers=[],
                warnings=[],
                requires_confirmation=False,
            )
    reject_response = client.post(
        f"/api/workspaces/{workspace['id']}/drafts/{draft['id']}/reject",
        json={"reason": "No good"},
    )
    assert reject_response.status_code == 200

    response = client.get(f"/api/workspaces/{workspace['id']}/editorial-history")
    assert response.status_code == 200
    events = response.json()["events"]
    assert any(
        e["entity_type"] == "draft" and e["entity_id"] == draft["id"] and e["action"] == "rejected"
        for e in events
    )


def test_apply_gold_to_routine_updates_schema(client: TestClient) -> None:
    workspace = _create_workspace(client, "Apply Gold")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(
                ctx,
                conn,
                name="Cotizador",
                schema_output_json=json.dumps(
                    {"type": "object", "properties": {"price": {"type": "number"}}}
                ),
            )
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"client": "Acme"},
                output_json={"price": 100, "currency": "USD", "client": "Acme"},
                evidence_json=[],
                status="requires_hitl",
            )
            update_routine_run_output(
                ctx,
                conn,
                run["id"],
                output_json={"price": 100, "currency": "USD", "client": "Acme"},
                edited_output_json={"price": 100, "currency": "USD", "client": "Acme", "note": "ok"},
                approved_by="local",
            )

    with db_session() as conn:
        candidate = list_gold_candidates(ctx, conn)[0]
        promote_response = client.post(
            f"/api/workspaces/{workspace['id']}/gold-candidates/{candidate['id']}/promote",
            json={"learned_output_json": {"currency": {"type": "string"}, "client": {"type": "string"}}},
        )
        assert promote_response.status_code == 200

        apply_response = client.post(
            f"/api/workspaces/{workspace['id']}/gold-candidates/{candidate['id']}/apply-to-routine"
        )
        assert apply_response.status_code == 200
        result = apply_response.json()

    routine_after = result["routine"]
    schema = json.loads(routine_after["schema_output_json"])
    # Original schema properties are preserved; learned keys are merged shallowly at root.
    assert schema["properties"]["price"]["type"] == "number"
    assert schema["currency"]["type"] == "string"
    assert schema["client"]["type"] == "string"
    assert result["candidate"]["used"] == 1

    response = client.get(f"/api/workspaces/{workspace['id']}/editorial-history")
    assert response.status_code == 200
    events = response.json()["events"]
    assert any(
        e["entity_type"] == "gold_candidate"
        and e["entity_id"] == candidate["id"]
        and e["action"] == "applied_to_routine"
        for e in events
    )


# -----------------------------------------------------------------------------
# SL3b/c CLOSER extensions
# -----------------------------------------------------------------------------


def test_task_type_is_captured_on_routine_run(client: TestClient) -> None:
    """routine_run stores the routine category as task_type for per-task metrics."""

    workspace = _create_workspace(client, "Task Type Capture")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Greeter", category="skill")
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"name": "Ada"},
                output_json={"greeting": "Hello"},
                evidence_json=[],
                status="requires_hitl",
            )

    assert run["task_type"] == "skill"


def test_edit_pct_declines_with_repetitions_by_task_type(client: TestClient) -> None:
    """Seeded sessions for the same task_type show a declining edit_pct trend."""

    workspace = _create_workspace(client, "Edit Pct Decline")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    target = {"reply": "approved response", "lang": "es"}
    # Each successive model output is closer to the approved target.
    seeded_outputs = [
        {"reply": "approved response!!!!", "lang": "es"},
        {"reply": "approved response!!", "lang": "es"},
        {"reply": "approved response!", "lang": "es"},
        target,
        target,
    ]
    edit_pcts: list[float] = []

    with db_session() as conn:
        routine = create_routine(ctx, conn, name="Repeater", category="skill")
        for i, output in enumerate(seeded_outputs):
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"turn": i},
                output_json=output,
                evidence_json=[],
                status="requires_hitl",
                task_type="skill",
            )
            updated = update_routine_run_output(
                ctx,
                conn,
                run["id"],
                output_json=output,
                edited_output_json=target,
                approved_by="local",
            )
            assert updated is not None
            edit_pcts.append(updated["edit_pct"])

    assert all(isinstance(p, float) and 0 <= p <= 1 for p in edit_pcts)
    # The final repetitions are identical to the target (zero edit).
    assert edit_pcts[-1] == 0.0
    assert edit_pcts[-2] == 0.0
    # The trend is non-increasing across our seeded progression.
    assert edit_pcts[-1] <= edit_pcts[0]
    assert edit_pcts == sorted(edit_pcts, reverse=True)
    assert edit_pcts[0] > edit_pcts[-3] > 0


def test_hard_field_gold_requires_second_gate(client: TestClient) -> None:
    """Gold candidates containing prices/SKUs/stock require independent verification."""

    workspace = _create_workspace(client, "Hard Field Gate")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Pricer")
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"sku": "ABC-123"},
                output_json={"price": 100, "sku": "ABC-123", "stock": 50},
                evidence_json=[],
                status="requires_hitl",
            )
            update_routine_run_output(
                ctx,
                conn,
                run["id"],
                output_json={"price": 100, "sku": "ABC-123", "stock": 50},
                edited_output_json={"price": 100, "sku": "ABC-123", "stock": 50, "note": "ok"},
                approved_by="local",
            )

    with db_session() as conn:
        candidate = list_gold_candidates(ctx, conn)[0]

    # Without the second gate the promotion is rejected.
    reject_response = client.post(
        f"/api/workspaces/{workspace['id']}/gold-candidates/{candidate['id']}/promote",
        json={"learned_output_json": {"price": 100, "sku": "ABC-123"}},
    )
    assert reject_response.status_code == 422

    # With an independent verifier the promotion succeeds.
    promote_response = client.post(
        f"/api/workspaces/{workspace['id']}/gold-candidates/{candidate['id']}/promote",
        json={
            "learned_output_json": {"price": 100, "sku": "ABC-123"},
            "verified_by": "controller",
        },
    )
    assert promote_response.status_code == 200
    assert promote_response.json()["approved"] == 1


def test_gold_candidate_tenant_isolation(client: TestClient) -> None:
    """Gold candidates and their evidence are scoped by tenant_id."""

    workspace = client.post(
        "/api/workspaces",
        json={"name": "Tenant Gold"},
        headers={"x-tenant-id": "t1"},
    ).json()
    ctx_t1 = Context(workspace_id=workspace["id"], tenant_id="t1")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx_t1, conn, name="Pricer")
            run = create_routine_run(
                ctx_t1,
                conn,
                routine_id=routine["id"],
                input_json={},
                output_json={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
                evidence_json=[],
                status="requires_hitl",
            )
            update_routine_run_output(
                ctx_t1,
                conn,
                run["id"],
                output_json={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
                edited_output_json={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "note": "ok"},
                approved_by="local",
            )

    with db_session() as conn:
        assert len(list_gold_candidates(ctx_t1, conn)) == 1
        # Same workspace id but a different tenant cannot read the candidate.
        ctx_t2 = Context(workspace_id=workspace["id"], tenant_id="t2")
        assert list_gold_candidates(ctx_t2, conn) == []


def test_gold_refeed_appends_approved_examples_to_skill_prompt(client: TestClient) -> None:
    """Approved gold candidates are injected into the skill prompt at execution time."""

    workspace = _create_workspace(client, "Gold Refeed")
    ctx = Context(workspace_id=workspace["id"], tenant_id="default")

    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Greeter")
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"name": "Ada"},
                output_json={"greeting": "Hello Ada", "tone": "friendly"},
                evidence_json=[],
                status="requires_hitl",
            )
            update_routine_run_output(
                ctx,
                conn,
                run["id"],
                output_json={"greeting": "Hello Ada", "tone": "friendly"},
                edited_output_json={"greeting": "Hello Ada", "tone": "friendly", "note": "ok"},
                approved_by="local",
            )
            candidate = list_gold_candidates(ctx, conn)[0]
            promote_gold_candidate(
                ctx,
                conn,
                candidate["id"],
                learned_output_json={"greeting": "Hello Ada"},
            )

        skill = {
            "instructions": "Be helpful.",
            "persona": "",
            "schema_output": {},
            "tools": [],
        }
        from app.src.api import _inject_gold_examples_into_skill

        _inject_gold_examples_into_skill(ctx, conn, skill, routine["id"])

    instructions = skill["instructions"]
    assert "Approved gold examples" in instructions
    assert "Hello Ada" in instructions
    assert json.dumps({"name": "Ada"}) in instructions
