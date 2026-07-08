"""E3-4 Wave 0: Pack 1 fiscalidad electronica materialization and promotion."""

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


def test_pack1_import_creates_factory_rows_and_promotion_gated(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session, utc_now
    from app.src.skill_primitives import promote_pack

    workspace_id = _demo_workspace_id(client)
    item_id = _catalog_item_id(client, "SKILL_FE_STATUS_CHECK.md")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/import-faberloom",
        json={"imports": [item_id]},
    )
    assert response.status_code == 200, response.text

    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")
    with db_session() as conn:
        # Catalog import materialized the skill factory rows.
        manifest = conn.execute(
            "SELECT * FROM skill_manifest WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ?",
            (workspace_id, "default", "SKILL_FE_STATUS_CHECK"),
        ).fetchone()
        assert manifest is not None
        assert manifest["status"] == "shadow"

        golden = conn.execute(
            "SELECT * FROM golden_case WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ?",
            (workspace_id, "default", "SKILL_FE_STATUS_CHECK"),
        ).fetchone()
        assert golden is not None
        assert golden["approved"] == 0

        pack = conn.execute(
            "SELECT * FROM pack_status WHERE workspace_id = ? AND tenant_id = ? AND pack_id = ?",
            (workspace_id, "default", "wtp_fiscalidad_electronica"),
        ).fetchone()
        assert pack is not None
        assert pack["status"] == "shadow"
        assert pack["required_golden_cases"] >= 1

        # Promotion is blocked until gates are met.
        with pytest.raises(ValueError, match="unapproved golden cases"):
            promote_pack(ctx, conn, pack_id="wtp_fiscalidad_electronica", approved_by="tester")

        # Approve and verify the golden case.
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

        # Still blocked by track-record thresholds.
        with pytest.raises(ValueError, match="track-record thresholds"):
            promote_pack(ctx, conn, pack_id="wtp_fiscalidad_electronica", approved_by="tester")

        # Meet the conservative track-record threshold.
        conn.execute(
            """
            UPDATE skill_track_record
            SET runs_total = 100, runs_success = 95, acceptance_rate = 0.95,
                autonomy_ceiling = 1, updated_at = ?
            WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ?
            """,
            (now, workspace_id, "default", "SKILL_FE_STATUS_CHECK"),
        )

        result = promote_pack(ctx, conn, pack_id="wtp_fiscalidad_electronica", approved_by="tester")

    assert result["status"] == "active"
    assert result["pack_id"] == "wtp_fiscalidad_electronica"
