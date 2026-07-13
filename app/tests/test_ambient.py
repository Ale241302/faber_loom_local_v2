"""Tests for E2-5 ambient cycle."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _auth_headers(role: str = "admin") -> dict[str, str]:
    return {
        "x-tenant-id": "default",
        "x-user-id": "tester",
        "x-actor-id": "tester",
        "x-actor-role": role,
    }


def _create_workspace(client: TestClient, name: str) -> dict[str, Any]:
    resp = client.post(
        "/api/workspaces",
        json={"name": name},
        headers=_auth_headers(),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_routine_run(
    client: TestClient,
    workspace_id: str,
    status: str = "failed",
    hours_ago: int = 1,
) -> dict[str, Any]:
    from app.src.db import connect, create_routine, create_routine_run
    from app.src.context import Context
    from app.src.models import RoutineCreate

    conn = connect()
    try:
        ctx = Context(
            workspace_id=workspace_id,
            tenant_id="default",
            user_id="tester",
            actor_id="tester",
            actor_role_at_decision="admin",
        )
        created_at_offset = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        routine = create_routine(
            ctx,
            conn,
            name=f"Test Routine {os.urandom(2).hex()}",
            skill_md="# SKILL\nname: Test\n",
        )
        run = create_routine_run(
            ctx,
            conn,
            routine_id=routine["id"],
            input_json={},
            output_json={"error": "Something went wrong"} if status == "failed" else {"result": "ok"},
            evidence_json=[],
            status=status,
            task_type="test",
        )
        # Adjust created_at to simulate age
        conn.execute(
            "UPDATE routine_run SET created_at = ? WHERE id = ?",
            (created_at_offset.isoformat(timespec="milliseconds").replace("+00:00", "Z"), run["id"]),
        )
        conn.commit()
        return {"routine_id": routine["id"], "run_id": run["id"]}
    finally:
        conn.close()


def _enable_ambient(client: TestClient) -> None:
    """El ciclo ambiental arranca OFF por contrato (plan E2 Sec.7.1);
    los tests que disparan ciclos lo encienden explícitamente."""
    resp = client.patch(
        "/api/admin/ambient/config",
        json={"global_enabled": True},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200, resp.text


def test_ambient_config_is_seeded(client: TestClient) -> None:
    resp = client.get("/api/admin/ambient/config", headers=_auth_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["tenant_id"] == "default"
    assert data["global_frequency_min"] == 30


def test_failed_routine_detector_creates_proposal(client: TestClient) -> None:
    ws = _create_workspace(client, "Ambient Test Failed")
    _enable_ambient(client)
    _create_routine_run(client, ws["id"], status="failed", hours_ago=1)

    resp = client.post(
        "/api/admin/ambient/trigger",
        json={"workspace_id": ws["id"]},
        headers=_auth_headers(),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["proposals_created"] >= 1

    # Dark-launch: proposals should be dark, not visible drafts
    resp2 = client.get(
        f"/api/workspaces/{ws['id']}/drafts",
        headers=_auth_headers(),
    )
    assert resp2.status_code == 200
    drafts = resp2.json()
    ambient_drafts = [d for d in drafts if d.get("task") == "ambient_proposal"]
    assert len(ambient_drafts) == 0


def test_kill_switch_workspace_blocks_cycle(client: TestClient) -> None:
    ws = _create_workspace(client, "Ambient Kill Switch")
    _enable_ambient(client)
    _create_routine_run(client, ws["id"], status="failed", hours_ago=1)

    # Disable workspace kill switch
    resp = client.post(
        f"/api/admin/ambient/workspaces/{ws['id']}/kill",
        json={"enabled": False},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200

    resp2 = client.post(
        "/api/admin/ambient/trigger",
        json={"workspace_id": ws["id"]},
        headers=_auth_headers(),
    )
    assert resp2.status_code == 201
    assert resp2.json()["proposals_created"] == 0


def test_ambient_metrics_endpoint(client: TestClient) -> None:
    ws = _create_workspace(client, "Ambient Metrics")
    _enable_ambient(client)
    _create_routine_run(client, ws["id"], status="failed", hours_ago=1)

    client.post(
        "/api/admin/ambient/trigger",
        json={"workspace_id": ws["id"]},
        headers=_auth_headers(),
    )

    resp = client.get(
        "/api/admin/ambient/metrics",
        params={"workspace_id": ws["id"], "days": 7},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["proposals_created"] >= 1


def test_cannot_send_email_from_ambient() -> None:
    from app.src.ambient import DETECTOR_REGISTRY
    from app.src.connectors import imap

    # Ambient must not import or expose send_message
    assert "send_message" not in DETECTOR_REGISTRY
    # The connector module has send_message, but ambient does not call it.
    import app.src.ambient as ambient_module
    assert not hasattr(ambient_module, "send_message")


def test_deduplication_merges_same_finding(client: TestClient) -> None:
    ws = _create_workspace(client, "Ambient Dedup")
    _enable_ambient(client)
    run = _create_routine_run(client, ws["id"], status="failed", hours_ago=1)

    # First cycle
    resp = client.post(
        "/api/admin/ambient/trigger",
        json={"workspace_id": ws["id"]},
        headers=_auth_headers(),
    )
    assert resp.status_code == 201
    first_count = resp.json()["proposals_created"]
    assert first_count >= 1

    # Second cycle within 24h should merge, not create new proposals for same run
    resp2 = client.post(
        "/api/admin/ambient/trigger",
        json={"workspace_id": ws["id"]},
        headers=_auth_headers(),
    )
    assert resp2.status_code == 201
    second_count = resp2.json()["proposals_created"]
    assert second_count == 0


def test_scheduler_runs_a_cycle_per_tenant(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """The scheduler is no longer hardcoded to the default tenant: each enabled
    tenant gets its own cycle, scoped to itself."""

    import app.src.ambient as ambient
    from app.src.db import connect

    ran: list[str] = []

    class _FakeOrch:
        def run_cycle(self, conn: Any, tenant_id: str, workspace_id: str | None = None, trigger: str = "manual") -> dict[str, Any]:
            ran.append(tenant_id)
            return {"tenant_id": tenant_id, "trigger": trigger}

    monkeypatch.setattr(ambient, "get_orchestrator", lambda: _FakeOrch())
    monkeypatch.setattr(ambient, "is_within_window", lambda config: True)

    conn = connect()
    try:
        for tenant_id in ("default", "tnt_second"):
            ambient.seed_ambient_config(conn, tenant_id)
            ambient.update_ambient_config(conn, tenant_id, {"global_enabled": 1})
        # A disabled tenant must be skipped.
        ambient.seed_ambient_config(conn, "tnt_disabled")

        ambient._run_tenant_schedule(conn, "default")
        ambient._run_tenant_schedule(conn, "tnt_second")
        ambient._run_tenant_schedule(conn, "tnt_disabled")
    finally:
        conn.close()

    assert "default" in ran
    assert "tnt_second" in ran
    assert "tnt_disabled" not in ran


# ---------------------------------------------------------------------------
# E5-2: stale_backup_smoke detector
# ---------------------------------------------------------------------------


def test_stale_backup_smoke_detector_is_registered() -> None:
    from app.src.ambient import DETECTOR_REGISTRY

    assert "stale_backup_smoke" in DETECTOR_REGISTRY


def test_stale_backup_smoke_finding_when_report_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.src import ambient_detectors as ad
    from app.src.ambient_detectors import detect_stale_backup_smoke
    from app.src.context import Context

    monkeypatch.setattr(ad, "find_latest_backup_smoke_report", lambda _path: None)

    ctx = Context(workspace_id="ws", tenant_id="default")
    findings = detect_stale_backup_smoke(ctx, None)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.detector_slug == "stale_backup_smoke"
    assert finding.severity == "critical"
    assert "No existe reporte" in finding.title


def test_stale_backup_smoke_finding_when_report_stale(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.src import ambient_detectors as ad
    from app.src.ambient_detectors import detect_stale_backup_smoke
    from app.src.context import Context

    stale_mtime = datetime.now(timezone.utc) - timedelta(hours=48)
    monkeypatch.setattr(
        ad,
        "find_latest_backup_smoke_report",
        lambda _path: (Path("BACKUP_SMOKE_20260712T000000Z.md"), stale_mtime),
    )

    ctx = Context(workspace_id="ws", tenant_id="default")
    findings = detect_stale_backup_smoke(ctx, None)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.detector_slug == "stale_backup_smoke"
    assert finding.severity == "high"
    assert "desactualizado" in finding.title


def test_stale_backup_smoke_no_finding_when_report_fresh(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.src import ambient_detectors as ad
    from app.src.ambient_detectors import detect_stale_backup_smoke
    from app.src.context import Context

    fresh_mtime = datetime.now(timezone.utc) - timedelta(hours=1)
    monkeypatch.setattr(
        ad,
        "find_latest_backup_smoke_report",
        lambda _path: (Path("BACKUP_SMOKE_20260713T000000Z.md"), fresh_mtime),
    )

    ctx = Context(workspace_id="ws", tenant_id="default")
    findings = detect_stale_backup_smoke(ctx, None)

    assert findings == []


def test_stale_backup_smoke_creates_proposal_when_missing(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    ws = _create_workspace(client, "Ambient Backup Smoke")
    _enable_ambient(client)

    from app.src import ambient_detectors as ad

    monkeypatch.setattr(ad, "find_latest_backup_smoke_report", lambda _path: None)

    resp = client.post(
        "/api/admin/ambient/trigger",
        json={"workspace_id": ws["id"]},
        headers=_auth_headers(),
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["proposals_created"] >= 1
