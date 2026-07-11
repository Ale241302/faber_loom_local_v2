"""E3-4: pack promotion readiness endpoint and promote gate."""

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


def _auth_headers(email: str, tenant_id: str, role: str = "owner") -> dict[str, str]:
    from app.src.auth import create_access_token

    token = create_access_token(
        email,
        tenant_id=tenant_id,
        user_id=f"usr_{email.split('@')[0]}",
        role=role,
    )
    return {"Authorization": f"Bearer {token}"}


def test_pack_readiness_not_imported_shows_blockers(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    res = client.get(
        f"/api/workspaces/{workspace_id}/packs/readiness",
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert res.status_code == 200
    data = res.json()
    assert data["workspace_id"] == workspace_id
    assert data["thresholds"]["runs_total"] == 100
    pack = next((p for p in data["packs"] if p["pack_id"] == "wtp_fiscalidad_electronica"), None)
    assert pack is not None
    assert pack["status"] == "not_imported"
    assert any("no importado" in b for b in pack["blockers"])
    assert not pack["can_promote"]


def test_pack_readiness_blocked_by_gates_after_import(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    item_id = _catalog_item_id(client, "SKILL_FE_STATUS_CHECK.md")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/import-faberloom",
        json={"imports": [item_id]},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert response.status_code == 200, response.text

    res = client.get(
        f"/api/workspaces/{workspace_id}/packs/readiness",
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert res.status_code == 200
    pack = next(
        (p for p in res.json()["packs"] if p["pack_id"] == "wtp_fiscalidad_electronica"), None
    )
    assert pack is not None
    assert pack["status"] == "shadow"
    assert pack["imported_count"] >= 1
    assert any("golden cases" in b for b in pack["blockers"])
    assert not pack["can_promote"]


def test_promote_pack_gated_and_then_succeeds(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session, transaction, utc_now

    workspace_id = _demo_workspace_id(client)
    item_id = _catalog_item_id(client, "SKILL_FE_STATUS_CHECK.md")

    response = client.post(
        f"/api/workspaces/{workspace_id}/routines/import-faberloom",
        json={"imports": [item_id]},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert response.status_code == 200, response.text

    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")
    with db_session() as conn:
        with transaction(conn, ctx=ctx):
            golden = conn.execute(
                "SELECT * FROM golden_case WHERE workspace_id = ? AND tenant_id = ? AND skill_id = ?",
                (workspace_id, "default", "SKILL_FE_STATUS_CHECK"),
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
                (now, workspace_id, "default", "SKILL_FE_STATUS_CHECK"),
            )

    # Wrong confirmation token is rejected.
    bad = client.post(
        f"/api/workspaces/{workspace_id}/packs/wtp_fiscalidad_electronica/promote",
        json={"confirmation_token": "wrong-token"},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert bad.status_code == 409

    # Readiness now shows can_promote.
    res = client.get(
        f"/api/workspaces/{workspace_id}/packs/readiness",
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    pack = next(
        (p for p in res.json()["packs"] if p["pack_id"] == "wtp_fiscalidad_electronica"), None
    )
    assert pack["can_promote"]

    import hashlib

    token = hashlib.sha256(b"wtp_fiscalidad_electronica").hexdigest()[:16]
    promoted = client.post(
        f"/api/workspaces/{workspace_id}/packs/wtp_fiscalidad_electronica/promote",
        json={"confirmation_token": token},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert promoted.status_code == 200, promoted.text
    assert promoted.json()["status"] == "active"

    # After promotion, readiness reflects active status.
    res = client.get(
        f"/api/workspaces/{workspace_id}/packs/readiness",
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    pack = next(
        (p for p in res.json()["packs"] if p["pack_id"] == "wtp_fiscalidad_electronica"), None
    )
    assert pack["status"] == "active"
    assert pack["can_promote"]
