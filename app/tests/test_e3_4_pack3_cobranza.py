"""E3-4 Wave 0: Pack 3 cobranza materialization and promotion."""

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


def _catalog_item_id(client: TestClient, file_name: str) -> str:
    response = client.get("/api/faberloom/catalog")
    assert response.status_code == 200
    item = next((i for i in response.json() if i["file"] == file_name), None)
    assert item is not None, f"{file_name} not found in catalog"
    return item["id"]


def test_pack3_import_creates_factory_rows_and_promotes_after_gates(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session, utc_now
    from app.src.skill_primitives import promote_pack

    workspace_id = _demo_workspace_id(client)
    item_id = _catalog_item_id(client, "SKILL_CO_DUNNING_FE.md")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/import-faberloom",
        json={"imports": [item_id]},
    )
    assert response.status_code == 200, response.text

    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")
    with db_session() as conn:
        manifest = conn.execute(
            "SELECT * FROM skill_manifest WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ?",
            (workspace_id, "default", "SKILL_CO_DUNNING_FE"),
        ).fetchone()
        assert manifest is not None
        assert manifest["status"] == "shadow"

        golden = conn.execute(
            "SELECT * FROM golden_case WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ?",
            (workspace_id, "default", "SKILL_CO_DUNNING_FE"),
        ).fetchone()
        assert golden is not None

        now = utc_now()
        conn.execute(
            """
            UPDATE golden_case
            SET approved = 1, approved_by = 'tester', verified_by = 'verifier',
                approved_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (now, now, golden["id"]),
        )

        conn.execute(
            """
            UPDATE skill_track_record
            SET runs_total = 100, runs_success = 95, acceptance_rate = 0.95,
                autonomy_ceiling = 1, updated_at = ?
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ?
            """,
            (now, workspace_id, "default", "SKILL_CO_DUNNING_FE"),
        )

        result = promote_pack(ctx, conn, pack_id="wtp_cobranza", approved_by="tester")

    assert result["status"] == "active"
    assert result["pack_id"] == "wtp_cobranza"
