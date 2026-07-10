"""E3-6: golden-case harvester from real routine runs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv("FABERLOOM_USERS", '{"owner@example.test":"password","curator@example.test":"password"}')
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.storage import reset_object_store

    reset_object_store()
    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _auth_headers(email: str, tenant_id: str, role: str = "owner") -> dict[str, str]:
    from app.src.auth import create_access_token

    token = create_access_token(
        email,
        tenant_id=tenant_id,
        user_id=f"usr_{email.split('@')[0]}",
        role=role,
    )
    return {"Authorization": f"Bearer {token}"}


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces", headers=_auth_headers("owner@example.test", "default", "owner"))
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def _insert_run(conn: Any, workspace_id: str, skill_id: str) -> str:
    from app.src.db import new_id, utc_now

    now = utc_now()
    routine_id = new_id("rt")
    conn.execute(
        """
        INSERT INTO routine (id, workspace_id, tenant_id, name, skill_md, tools_allowlist,
            schema_output_json, trigger_json, persona_md, is_active, category, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            routine_id,
            workspace_id,
            "default",
            skill_id,
            "---\nname: test\n---\n",
            "[]",
            "{}",
            "[]",
            "",
            0,
            "skill",
            now,
            now,
        ),
    )
    run_id = new_id("rr")
    conn.execute(
        """
        INSERT INTO routine_run (id, routine_id, workspace_id, tenant_id, input_json,
            output_json, evidence_json, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'succeeded', ?)
        """,
        (
            run_id,
            routine_id,
            workspace_id,
            "default",
            json.dumps({"request": "value"}),
            json.dumps({"result": "ok"}),
            json.dumps(
                [
                    {
                        "source_type": "test",
                        "source_locator": "test://evidence/1",
                        "captured_at": now,
                        "content_text": "evidence body",
                    }
                ]
            ),
            now,
        ),
    )
    return run_id


def _confirmation_token(resource_id: str) -> str:
    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def test_propose_golden_case_from_run(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.golden_harvester import propose_golden_case_from_run

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        run_id = _insert_run(conn, workspace_id, "SKILL_TEST")
        conn.commit()
        case = propose_golden_case_from_run(ctx, conn, run_id=run_id, skill_id="SKILL_TEST")

    assert case["skill_id"] == "SKILL_TEST"
    assert case["case_id"] == f"run-{run_id}"
    assert case["approved"] == 0
    assert case["origin"] == "dogfood"
    assert case["run_id"] == run_id
    assert case["frozen_at"] is not None

    with db_session() as conn:
        rows = conn.execute(
            "SELECT * FROM external_evidence WHERE entity_type = 'golden_case' AND entity_id = ?",
            (case["id"],),
        ).fetchall()
        assert len(rows) == 1


def test_list_golden_cases_by_state(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.golden_harvester import approve_golden_case, list_golden_cases, propose_golden_case_from_run

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        run_id = _insert_run(conn, workspace_id, "SKILL_TEST")
        conn.commit()
        case = propose_golden_case_from_run(ctx, conn, run_id=run_id, skill_id="SKILL_TEST")

    candidates = list_golden_cases(ctx, None, state="candidate")
    assert len(candidates) == 1

    with db_session() as conn:
        approve_golden_case(ctx, conn, case_id=case["id"], approved_by="curator_a")

    candidates = list_golden_cases(ctx, None, state="candidate")
    approved = list_golden_cases(ctx, None, state="approved")
    assert len(candidates) == 0
    assert len(approved) == 1


def test_candidate_does_not_count_for_promote(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.golden_harvester import propose_golden_case_from_run
    from app.src.skill_primitives import ensure_skill_factory_rows, promote_pack

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        ensure_skill_factory_rows(
            ctx,
            conn,
            skill_id="SKILL_FE_PROMOTE",
            manifest_json={
                "name": "Promote",
                "version": "1.0.0",
                "metadata": {
                    "fbl": {
                        "id": "SKILL_PROMOTE",
                        "type": "agent",
                        "architectural_archetype": "generator",
                        "archetype": "generator",
                    }
                },
            },
            golden_samples=[],
        )
        run_id = _insert_run(conn, workspace_id, "SKILL_FE_PROMOTE")
        conn.commit()
        propose_golden_case_from_run(ctx, conn, run_id=run_id, skill_id="SKILL_FE_PROMOTE")

        with pytest.raises(ValueError, match="unapproved golden cases"):
            promote_pack(ctx, conn, pack_id="wtp_fiscalidad_electronica", approved_by="admin")


def test_api_propose_and_list(client: TestClient) -> None:
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    with db_session() as conn:
        run_id = _insert_run(conn, workspace_id, "SKILL_API")
        conn.commit()

    resp = client.post(
        "/api/tenants/default/skills/SKILL_API/golden-cases/propose",
        json={"run_id": run_id},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert resp.status_code == 200, resp.text
    case_id = resp.json()["id"]

    resp = client.get(
        "/api/tenants/default/golden-cases?state=candidate",
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert resp.status_code == 200
    assert len(resp.json()["golden_cases"]) == 1


def test_api_approve_requires_confirmation_token(client: TestClient) -> None:
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    with db_session() as conn:
        run_id = _insert_run(conn, workspace_id, "SKILL_APPROVE")
        conn.commit()

    resp = client.post(
        "/api/tenants/default/skills/SKILL_APPROVE/golden-cases/propose",
        json={"run_id": run_id},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    case_id = resp.json()["id"]

    resp = client.post(
        f"/api/tenants/default/golden-cases/{case_id}/approve",
        json={"confirmation_token": "wrong"},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert resp.status_code == 409

    resp = client.post(
        f"/api/tenants/default/golden-cases/{case_id}/approve",
        json={"confirmation_token": _confirmation_token(case_id)},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["approved"] == 1
    assert resp.json()["approved_by"] == "usr_owner"


def test_api_verify_requires_different_user(client: TestClient) -> None:
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    with db_session() as conn:
        run_id = _insert_run(conn, workspace_id, "SKILL_VERIFY")
        conn.commit()

    resp = client.post(
        "/api/tenants/default/skills/SKILL_VERIFY/golden-cases/propose",
        json={"run_id": run_id},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    case_id = resp.json()["id"]

    client.post(
        f"/api/tenants/default/golden-cases/{case_id}/approve",
        json={"confirmation_token": _confirmation_token(case_id)},
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )

    resp = client.post(
        f"/api/tenants/default/golden-cases/{case_id}/verify",
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert resp.status_code == 422, resp.text
    assert "different from approver" in resp.text

    resp = client.post(
        f"/api/tenants/default/golden-cases/{case_id}/verify",
        headers=_auth_headers("curator@example.test", "default", "owner"),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["verified_by"] == "usr_curator"


def test_tenant_isolation(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.golden_harvester import propose_golden_case_from_run

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        run_id = _insert_run(conn, workspace_id, "SKILL_ISO")
        conn.commit()
        case = propose_golden_case_from_run(ctx, conn, run_id=run_id, skill_id="SKILL_ISO")

    other_ctx = Context(workspace_id=workspace_id, tenant_id="other", user_id="local", actor_id="local")
    with db_session() as conn:
        with pytest.raises(ValueError, match="Golden case not found"):
            from app.src.golden_harvester import approve_golden_case
            approve_golden_case(other_ctx, conn, case_id=case["id"], approved_by="x")


def test_api_non_admin_gets_403(client: TestClient) -> None:
    workspace_id = _demo_workspace_id(client)
    resp = client.get(
        "/api/tenants/default/golden-cases",
        headers=_auth_headers("owner@example.test", "default", "member"),
    )
    assert resp.status_code == 403
