"""E2-3: KB inheritance, source/citation preservation, gold L2/L3 states,
k-anon >= 5, committee/curator gate and negative tests.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import (
    create_routine,
    create_routine_run,
    create_workspace,
    db_session,
    get_workspace,
    transaction,
    update_routine_run_output,
)
from app.src.gold import promote_gold_candidate
from app.src.models import WorkspaceCreate


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
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


def _create_workspace(client: TestClient, name: str) -> dict[str, Any]:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


def _set_inherits_kb(workspace_id: str, parent_id: str) -> None:
    with db_session() as conn:
        with transaction(conn):
            conn.execute(
                "UPDATE workspace SET parent_id = ?, inherits_kb = 1 WHERE id = ?",
                (parent_id, workspace_id),
            )


def _ingest_source(client: TestClient, workspace_id: str, title: str, content: str) -> dict[str, Any]:
    response = client.post(
        f"/api/workspaces/{workspace_id}/kb/sources",
        json={"title": title, "type": "md", "content_text": content, "source_version": "v1"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _search_kb(
    client: TestClient,
    workspace_id: str,
    q: str,
    role: str = "owner",
    tenant_id: str = "default",
) -> dict[str, Any]:
    response = client.get(
        f"/api/workspaces/{workspace_id}/kb/search",
        params={"q": q, "limit": 10},
        headers={"x-actor-role": role, "x-tenant-id": tenant_id},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _create_child_workspace(client: TestClient, parent_id: str, name: str) -> dict[str, Any]:
    response = client.post("/api/workspaces", json={"name": name, "parent_id": parent_id})
    assert response.status_code == 201, response.text
    ws = response.json()
    _set_inherits_kb(ws["id"], parent_id)
    return ws


def _seed_candidate(workspace_id: str, learned: dict[str, Any] | None = None) -> dict[str, Any]:
    ctx = Context(workspace_id=workspace_id, tenant_id="default")
    with db_session() as conn:
        with transaction(conn):
            routine = create_routine(ctx, conn, name="Greeter")
            run = create_routine_run(
                ctx,
                conn,
                routine_id=routine["id"],
                input_json={"name": "Ada"},
                output_json={"greeting": "Hello Ada"},
                evidence_json=[],
                status="requires_hitl",
            )
            update_routine_run_output(
                ctx,
                conn,
                run["id"],
                output_json={"greeting": "Hello Ada", "note": "ok"},
                edited_output_json={"greeting": "Hello Ada", "note": "ok"},
                approved_by="am_a",
            )
            candidates = conn.execute(
                "SELECT * FROM gold_candidate WHERE run_id = ?",
                (run["id"],),
            ).fetchall()
            candidate = dict(candidates[0])
            if learned is not None:
                conn.execute(
                    "UPDATE gold_candidate SET learned_output_json = ? WHERE id = ?",
                    (json.dumps(learned, ensure_ascii=False, sort_keys=True), candidate["id"]),
                )
                candidate["learned_output_json"] = json.dumps(learned, ensure_ascii=False, sort_keys=True)
            return candidate


def _promote(
    client: TestClient,
    workspace_id: str,
    candidate_id: str,
    learned_output_json: dict[str, Any],
    target_state: str = "active_l2",
    verified_by: str | None = None,
    role: str = "owner",
) -> Any:
    return client.post(
        f"/api/workspaces/{workspace_id}/gold-candidates/{candidate_id}/promote",
        json={
            "learned_output_json": learned_output_json,
            "target_state": target_state,
            "verified_by": verified_by,
        },
        headers={"x-actor-role": role},
    )


def test_kb_inheritance_preserves_source_citation(client: TestClient) -> None:
    parent = _create_workspace(client, "Parent KB")
    source = _ingest_source(
        client,
        parent["id"],
        "Lista de precios",
        "Precio de Oxford: USD 12.50 por metro. Fuente: lista julio 2026.",
    )

    child = _create_child_workspace(client, parent["id"], "Child KB")

    results = _search_kb(client, child["id"], "Oxford")
    chunks = results["chunks"]
    assert len(chunks) >= 1
    assert any(chunk["source_id"] == source["id"] for chunk in chunks)


def test_kb_inheritance_disabled_isolates_child(client: TestClient) -> None:
    parent = _create_workspace(client, "Parent Isolated")
    _ingest_source(client, parent["id"], "Lista de precios", "Oxford USD 12.50")

    # Child created with parent_id but inherits_kb explicitly left off via a separate workspace.
    orphan = _create_workspace(client, "Orphan KB")
    with db_session() as conn:
        conn.execute("UPDATE workspace SET parent_id = ? WHERE id = ?", (parent["id"], orphan["id"]))

    results = _search_kb(client, orphan["id"], "Oxford")
    assert len(results["chunks"]) == 0
    assert len(results["facts"]) == 0


def test_canary_workspace_isolated_from_default_kb(client: TestClient) -> None:
    default_ws = _create_workspace(client, "Default MWT")
    _ingest_source(client, default_ws["id"], "Confidencial", "Precio especial para MWT: USD 10.00")

    with db_session() as conn:
        canary = conn.execute(
            "SELECT id FROM workspace WHERE is_canary = 1 AND tenant_id = 'canary'"
        ).fetchone()
    assert canary is not None

    results = _search_kb(client, canary["id"], "MWT", tenant_id="canary")
    assert len(results["chunks"]) == 0
    assert len(results["facts"]) == 0


def test_gold_candidate_state_machine(client: TestClient) -> None:
    ws = _create_workspace(client, "Gold States")
    learned = {"greeting": "Hello Ada"}

    # Seed 5 candidates with identical learned output to satisfy k-anon.
    candidates: list[dict[str, Any]] = []
    for _ in range(5):
        candidates.append(_seed_candidate(ws["id"], learned))

    first_id = candidates[0]["id"]

    # candidate -> active_l2
    r = _promote(client, ws["id"], first_id, learned, target_state="active_l2", role="owner")
    assert r.status_code == 200, r.text
    assert r.json()["state"] == "active_l2"

    # active_l2 -> l3_pending (owner is also a curator-level role in this mapping)
    r = _promote(client, ws["id"], first_id, learned, target_state="l3_pending", role="owner")
    assert r.status_code == 200, r.text
    assert r.json()["state"] == "l3_pending"

    # l3_pending -> l3
    r = _promote(
        client,
        ws["id"],
        first_id,
        learned,
        target_state="l3",
        verified_by="curator_b",
        role="owner",
    )
    assert r.status_code == 200, r.text
    assert r.json()["state"] == "l3"


def test_l3_requires_k_anon(client: TestClient) -> None:
    ws = _create_workspace(client, "Gold K-Anon")
    candidate = _seed_candidate(ws["id"], {"greeting": "Hello Ada"})

    # Promote to active_l2 first.
    r = _promote(client, ws["id"], candidate["id"], {"greeting": "Hello Ada"}, role="owner")
    assert r.status_code == 200

    # Only one occurrence -> L3 must fail.
    r = _promote(
        client,
        ws["id"],
        candidate["id"],
        {"greeting": "Hello Ada"},
        target_state="l3_pending",
        role="owner",
    )
    assert r.status_code == 422
    assert "k-anon" in r.json()["detail"].lower()


def test_l3_requires_curator_role(client: TestClient) -> None:
    ws = _create_workspace(client, "Gold Role")
    learned = {"greeting": "Hello Ada"}
    candidates = [_seed_candidate(ws["id"], learned) for _ in range(5)]

    r = _promote(client, ws["id"], candidates[0]["id"], learned, target_state="active_l2", role="owner")
    assert r.status_code == 200

    # AM/operator cannot queue L3.
    r = _promote(
        client,
        ws["id"],
        candidates[0]["id"],
        learned,
        target_state="l3_pending",
        role="operator",
    )
    assert r.status_code == 422
    assert "role" in r.json()["detail"].lower()


def test_l3_hard_fields_require_independent_verifier(client: TestClient) -> None:
    ws = _create_workspace(client, "Gold L3 Verify")
    learned = {"price": "USD 12.50"}
    candidates = [_seed_candidate(ws["id"], learned) for _ in range(5)]

    first_id = candidates[0]["id"]
    r = _promote(client, ws["id"], first_id, learned, target_state="active_l2", verified_by="curator_b", role="owner")
    assert r.status_code == 200

    r = _promote(client, ws["id"], first_id, learned, target_state="l3_pending", role="owner")
    assert r.status_code == 200

    # Self verification must be rejected at L3 (approved_by was set by the owner promotion above).
    r = _promote(
        client,
        ws["id"],
        first_id,
        learned,
        target_state="l3",
        verified_by="local",
        role="owner",
    )
    assert r.status_code == 422
    assert "promoter and verifier" in r.json()["detail"].lower()


def test_viewer_cannot_promote_gold(client: TestClient) -> None:
    ws = _create_workspace(client, "Gold Viewer")
    candidate = _seed_candidate(ws["id"], {"greeting": "Hello Ada"})

    r = _promote(
        client,
        ws["id"],
        candidate["id"],
        {"greeting": "Hello Ada"},
        role="viewer",
    )
    assert r.status_code == 422
    assert "role" in r.json()["detail"].lower()


def test_apply_gold_requires_active_state(client: TestClient) -> None:
    ws = _create_workspace(client, "Gold Apply State")
    candidate = _seed_candidate(ws["id"], {"greeting": "Hello Ada"})

    r = client.post(
        f"/api/workspaces/{ws['id']}/gold-candidates/{candidate['id']}/apply-to-routine",
        headers={"x-actor-role": "owner"},
    )
    assert r.status_code == 409
    assert "promoted" in r.json()["detail"].lower()


def test_reject_gold_candidate(client: TestClient) -> None:
    ws = _create_workspace(client, "Gold Reject")
    candidate = _seed_candidate(ws["id"], {"greeting": "Hello Ada"})

    r = _promote(
        client,
        ws["id"],
        candidate["id"],
        {"greeting": "Hello Ada"},
        target_state="rejected",
        role="owner",
    )
    assert r.status_code == 200, r.text
    assert r.json()["state"] == "rejected"
    assert r.json()["approved"] == 0


def test_cross_tenant_curator_cannot_verify(client: TestClient) -> None:
    """A curator from another tenant cannot verify/promote gold in this tenant."""

    ws = _create_workspace(client, "Gold Cross Tenant")
    learned = {"greeting": "Hello Ada"}
    candidates = [_seed_candidate(ws["id"], learned) for _ in range(5)]

    first_id = candidates[0]["id"]
    _promote(client, ws["id"], first_id, learned, target_state="active_l2", role="owner")
    _promote(client, ws["id"], first_id, learned, target_state="l3_pending", role="owner")

    # The endpoint is scoped by workspace/tenant; a request with a different tenant
    # header cannot even see the workspace.
    r = client.get(f"/api/workspaces/{ws['id']}/gold-candidates", headers={"x-tenant-id": "other"})
    assert r.status_code == 404
