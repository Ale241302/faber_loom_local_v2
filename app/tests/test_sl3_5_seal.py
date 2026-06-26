"""SL3.5: workspace HMAC seal and leak-detection tests."""

from __future__ import annotations

import sqlite3
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "spaceloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SPACELOOM_DB_PATH", str(db_path))

    for name in (
        "OPENAI_API_KEY",
        "SPACELOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "SPACELOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "SPACELOOM_GOOGLE_API_KEY",
        "SPACELOOM_ENABLE_OLLAMA",
        "SPACELOOM_OLLAMA_ENABLED",
        "SPACELOOM_PROVIDER_ALLOWLIST",
        "SPACELOOM_BUDGET_CAP_USD",
        "SPACELOOM_DEV_TRUST_HEADERS",
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


def _ingest_source(
    client: TestClient,
    workspace_id: str,
    title: str,
    text: str,
    source_type: str = "md",
) -> dict[str, Any]:
    response = client.post(
        f"/api/workspaces/{workspace_id}/kb/sources",
        json={"title": title, "type": source_type, "content_text": text},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _patch_router_and_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.src.api as api_module
    import app.src.draft_engine as engine_module

    class FakeRouter:
        def has_available_provider(self) -> bool:
            return True

    def fake_generate_draft(ctx: Any, conn: Any, **kwargs: Any) -> dict[str, Any]:
        return {
            "subject": "SL3.5 draft",
            "body_md": "Cuerpo de prueba.",
            "hard_facts": [],
            "sources": [],
            "blockers": [],
            "warnings": [],
            "requires_confirmation": False,
            "provider_slug": "fake",
            "model": "fake-model",
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.0,
            "duration_ms": 1,
        }

    monkeypatch.setattr(api_module, "build_router", FakeRouter)
    monkeypatch.setattr(engine_module, "generate_draft", fake_generate_draft)


def _create_draft(client: TestClient, monkeypatch: pytest.MonkeyPatch, workspace_id: str) -> dict[str, Any]:
    _patch_router_and_engine(monkeypatch)
    response = client.post(
        f"/api/workspaces/{workspace_id}/drafts",
        json={"user_request": "test SL3.5"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_each_workspace_has_unique_seal_id(client: TestClient) -> None:
    a = _create_workspace(client, "Seal A")
    b = _create_workspace(client, "Seal B")
    assert a["seal_id"]
    assert b["seal_id"]
    assert a["seal_id"] != b["seal_id"]
    assert len(a["seal_id"]) >= 16


def test_seal_check_endpoint_does_not_expose_seal_id(client: TestClient) -> None:
    workspace = _create_workspace(client, "Seal Check")
    response = client.get(f"/api/workspaces/{workspace['id']}/seal-check")
    assert response.status_code == 200
    data = response.json()
    assert "seal_id" not in data
    assert data["sample_hmac"]
    assert len(data["sample_hmac"]) == 64
    assert data["verified"] == "true"


def test_kb_source_hmac_blocks_simulated_leak(client: TestClient) -> None:
    from app.src.db import connect

    a = _create_workspace(client, "Source A")
    b = _create_workspace(client, "Source B")
    source = _ingest_source(client, a["id"], "Secret A", "Contenido confidencial de A.")
    source_id = source["id"]

    # Simulate an attacker moving the row from workspace A to workspace B.
    with connect() as conn:
        conn.execute(
            "UPDATE kb_source SET workspace_id = ? WHERE id = ?",
            (b["id"], source_id),
        )
        conn.commit()

    # Reading from the original workspace now misses the moved row.
    response_a = client.get(f"/api/workspaces/{a['id']}/kb/sources/{source_id}")
    assert response_a.status_code == 404

    # Reading from the target workspace must fail seal verification.
    response_b = client.get(f"/api/workspaces/{b['id']}/kb/sources/{source_id}")
    assert response_b.status_code in (403, 500)
    if response_b.status_code == 403:
        assert "seal" in response_b.json()["detail"].lower()


def test_kb_fact_hmac_blocks_simulated_leak(client: TestClient) -> None:
    from app.src.db import connect

    a = _create_workspace(client, "Fact A")
    b = _create_workspace(client, "Fact B")
    csv_text = "sku,nombre,precio\nTEL-001,Oxford,12.50"
    source = _ingest_source(client, a["id"], "Catalogo", csv_text, source_type="csv")

    with connect() as conn:
        row = conn.execute(
            "SELECT id FROM kb_fact WHERE workspace_id = ? LIMIT 1",
            (a["id"],),
        ).fetchone()
        assert row is not None
        fact_id = row["id"]
        conn.execute(
            "UPDATE kb_fact SET workspace_id = ? WHERE id = ?",
            (b["id"], fact_id),
        )
        conn.commit()

    response_b = client.get(f"/api/workspaces/{b['id']}/kb/search?q=Oxford")
    assert response_b.status_code == 200
    facts = response_b.json()["facts"]
    assert not any(fact["id"] == fact_id for fact in facts)


def test_draft_hmac_blocks_simulated_leak(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.src.db import connect

    a = _create_workspace(client, "Draft A")
    b = _create_workspace(client, "Draft B")
    draft = _create_draft(client, monkeypatch, a["id"])
    draft_id = draft["id"]

    with connect() as conn:
        conn.execute(
            "UPDATE draft SET workspace_id = ? WHERE id = ?",
            (b["id"], draft_id),
        )
        conn.commit()

    response_b = client.get(f"/api/workspaces/{b['id']}/drafts/{draft_id}")
    assert response_b.status_code in (403, 500)

    response_b_list = client.get(f"/api/workspaces/{b['id']}/drafts")
    assert response_b_list.status_code == 200
    assert draft_id not in {d["id"] for d in response_b_list.json()}


def test_kb_source_is_cross_workspace_isolated(client: TestClient) -> None:
    a = _create_workspace(client, "Iso A")
    b = _create_workspace(client, "Iso B")
    source = _ingest_source(client, a["id"], "Iso source", "Solo A")

    response_b = client.get(f"/api/workspaces/{b['id']}/kb/sources/{source['id']}")
    assert response_b.status_code == 404

    response_b_list = client.get(f"/api/workspaces/{b['id']}/kb/sources")
    assert response_b_list.status_code == 200
    assert source["id"] not in {s["id"] for s in response_b_list.json()}


def test_draft_is_cross_workspace_isolated(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    a = _create_workspace(client, "Draft Iso A")
    b = _create_workspace(client, "Draft Iso B")
    draft = _create_draft(client, monkeypatch, a["id"])

    response_b = client.get(f"/api/workspaces/{b['id']}/drafts/{draft['id']}")
    assert response_b.status_code == 404

    response_b_list = client.get(f"/api/workspaces/{b['id']}/drafts")
    assert response_b_list.status_code == 200
    assert draft["id"] not in {d["id"] for d in response_b_list.json()}


def test_hmac_helpers_are_consistent() -> None:
    from app.src.seal import assert_workspace_hmac, compute_workspace_hmac, verify_workspace_hmac

    seal_id = "aabbccdd"
    row_id = "row_123"
    workspace_id = "ws_abc"
    hmac = compute_workspace_hmac(seal_id, row_id, workspace_id)
    assert len(hmac) == 64
    assert verify_workspace_hmac(seal_id, row_id, workspace_id, hmac)
    assert not verify_workspace_hmac(seal_id, row_id, workspace_id, hmac[:-1] + "x")
    assert not verify_workspace_hmac("otroseal", row_id, workspace_id, hmac)
    assert_workspace_hmac(seal_id, row_id, workspace_id, hmac)

    with pytest.raises(PermissionError):
        assert_workspace_hmac(seal_id, row_id, workspace_id, "invalid")


def test_routine_run_is_sealed(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import connect, create_routine, create_routine_run, get_routine_run, list_routine_runs

    workspace = _create_workspace(client, "Routine Run Seal")
    other_workspace = _create_workspace(client, "Routine Run Other")

    with connect() as conn:
        ctx = Context(workspace_id=workspace["id"])
        routine = create_routine(ctx, conn, name="Test routine")
        routine_id = routine["id"]
        run = create_routine_run(
            ctx,
            conn,
            routine_id=routine_id,
            input_json={"query": "x"},
            output_json={"answer": "y"},
            evidence_json=[],
            status="succeeded",
        )
        assert run["workspace_hmac"]
        assert len(run["workspace_hmac"]) == 64

        fetched = get_routine_run(ctx, conn, run["id"])
        assert fetched is not None
        assert fetched["id"] == run["id"]

        runs = list_routine_runs(ctx, conn)
        assert any(r["id"] == run["id"] for r in runs)

        # Simulate leak by moving the row to a different workspace context.
        conn.execute(
            "UPDATE routine_run SET workspace_id = ? WHERE id = ?",
            (other_workspace["id"], run["id"]),
        )
        conn.commit()

        other_ctx = Context(workspace_id=other_workspace["id"])
        with pytest.raises(PermissionError):
            get_routine_run(other_ctx, conn, run["id"])

        sealed_runs = list_routine_runs(other_ctx, conn)
        assert run["id"] not in {r["id"] for r in sealed_runs}


def test_seal_id_column_is_backed_by_database(client: TestClient) -> None:
    from app.src.db import connect

    workspace = _create_workspace(client, "DB Seal")
    with connect() as conn:
        row = conn.execute(
            "SELECT seal_id FROM workspace WHERE id = ?",
            (workspace["id"],),
        ).fetchone()
    assert row is not None
    assert row["seal_id"] == workspace["seal_id"]
