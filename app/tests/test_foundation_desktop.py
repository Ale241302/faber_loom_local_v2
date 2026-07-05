"""Foundation Desktop (M18/M19/M20) — device auth, offline sync y auto update.

Suite autocontenida: app FastAPI mínima que monta ``foundation_router`` con la
BD foundation apuntando a ``tmp_path`` y seed directo vía ``core`` (sin pasar
por M07/M08, que pertenecen a otro flujo).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.src.foundation import core, foundation_router, init_foundation_db
from app.src.foundation.core import (
    emit_event,
    fnd_db,
    new_id,
    seed_system_roles,
    utcnow,
)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _seed_user(conn, tenant_id: str, email: str, role_name: str) -> dict[str, str]:
    user_id = new_id("usr")
    conn.execute(
        """INSERT INTO fnd_users (id, tenant_id, email, display_name, password_hash, status, created_at)
           VALUES (?, ?, ?, ?, '', 'active', ?)""",
        (user_id, tenant_id, email, email.split("@")[0], utcnow()),
    )
    role = conn.execute(
        "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?", (tenant_id, role_name)
    ).fetchone()
    conn.execute(
        "INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_at) VALUES (?, ?, ?, ?)",
        (tenant_id, user_id, role["id"], utcnow()),
    )
    session_id = new_id("fnds")
    now = datetime.now(timezone.utc)
    conn.execute(
        """INSERT INTO fnd_sessions
           (id, tenant_id, user_id, stage, created_at, expires_at, last_seen_at, ip, user_agent, device_id)
           VALUES (?, ?, ?, 'full', ?, ?, ?, '', 'pytest', '')""",
        (session_id, tenant_id, user_id, _iso(now), _iso(now + timedelta(hours=4)), _iso(now)),
    )
    return {"user_id": user_id, "session": session_id}


@pytest.fixture()
def env(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    init_foundation_db()

    with fnd_db() as conn:
        tenant_id = new_id("tnt")
        conn.execute(
            """INSERT INTO fnd_tenants (id, name, slug, status, plan, created_at, activated_at)
               VALUES (?, 'Test Tenant', 'test-tenant', 'active', 'beta', ?, ?)""",
            (tenant_id, utcnow(), utcnow()),
        )
        seed_system_roles(conn, tenant_id)
        owner = _seed_user(conn, tenant_id, "owner@test.local", "owner")
        viewer = _seed_user(conn, tenant_id, "viewer@test.local", "viewer")

    app = FastAPI()
    app.include_router(foundation_router, prefix="/api")
    client = TestClient(app)
    return {"client": client, "tenant_id": tenant_id, "owner": owner, "viewer": viewer}


def _h(session: str) -> dict[str, str]:
    return {"X-Fnd-Session": session}


def _register_device(env: dict[str, Any], name: str = "Equipo pytest") -> dict[str, Any]:
    res = env["client"].post(
        "/api/foundation/desktop/auth/device/register",
        json={"name": name, "platform": "linux"},
        headers=_h(env["owner"]["session"]),
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["device_id"].startswith("dev_")
    assert data["device_secret"].startswith("devs_")
    return data


# ---------------------------------------------------------------------------
# M18 — device auth
# ---------------------------------------------------------------------------


def test_register_then_device_login_creates_new_session(env: dict[str, Any]) -> None:
    client: TestClient = env["client"]
    dev = _register_device(env)

    res = client.post(
        "/api/foundation/desktop/auth/device/login",
        json={"device_id": dev["device_id"], "device_secret": dev["device_secret"]},
    )
    assert res.status_code == 200, res.text
    login = res.json()
    assert login["session"] != env["owner"]["session"]
    assert login["device_id"] == dev["device_id"]
    assert login["user"]["email"] == "owner@test.local"

    # La nueva sesión sirve para llamadas autenticadas y viene ligada al device.
    res = client.get("/api/foundation/sync/status", headers=_h(login["session"]))
    assert res.status_code == 200, res.text
    assert res.json()["device_id"] == dev["device_id"]

    # Secret incorrecto → 401 genérico.
    res = client.post(
        "/api/foundation/desktop/auth/device/login",
        json={"device_id": dev["device_id"], "device_secret": "devs_wrong"},
    )
    assert res.status_code == 401


def test_revoke_blocks_device_login(env: dict[str, Any]) -> None:
    client: TestClient = env["client"]
    dev = _register_device(env)

    res = client.post(
        f"/api/foundation/desktop/auth/devices/{dev['device_id']}/revoke",
        headers=_h(env["owner"]["session"]),
    )
    assert res.status_code == 200, res.text
    assert res.json()["revoked_at"]

    res = client.post(
        "/api/foundation/desktop/auth/device/login",
        json={"device_id": dev["device_id"], "device_secret": dev["device_secret"]},
    )
    assert res.status_code == 401

    # Y las sesiones ligadas al device quedaron revocadas (register ligó la del owner).
    res = client.get("/api/foundation/sync/status", headers=_h(env["owner"]["session"]))
    assert res.status_code == 401


def test_viewer_cannot_revoke_foreign_device(env: dict[str, Any]) -> None:
    client: TestClient = env["client"]
    dev = _register_device(env)
    res = client.post(
        f"/api/foundation/desktop/auth/devices/{dev['device_id']}/revoke",
        headers=_h(env["viewer"]["session"]),
    )
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# M19 — offline sync
# ---------------------------------------------------------------------------


def test_pull_delta_with_new_events(env: dict[str, Any]) -> None:
    client: TestClient = env["client"]
    dev = _register_device(env)
    tenant_id = env["tenant_id"]

    # Cursor fresco en seq 0 → los eventos nuevos llegan por delta.
    with fnd_db() as conn:
        conn.execute(
            """INSERT INTO fnd_sync_state (device_id, tenant_id, last_event_seq, last_sync_at, mode, updated_at)
               VALUES (?, ?, 0, ?, 'delta', ?)""",
            (dev["device_id"], tenant_id, utcnow(), utcnow()),
        )
        emit_event(conn, tenant_id, "drafts", "draft.created", {"path": "/drafts/d1"})
        emit_event(conn, tenant_id, "drafts", "draft.updated", {"path": "/drafts/d1"})

    res = client.post(
        "/api/foundation/sync/pull",
        json={"device_id": dev["device_id"]},
        headers=_h(env["owner"]["session"]),
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["mode"] == "delta"
    types = [e["type"] for e in data["events"]]
    assert "draft.created" in types and "draft.updated" in types
    assert data["next_seq"] >= 2

    # Segundo pull inmediato: delta vacío, cursor estable.
    res = client.post(
        "/api/foundation/sync/pull",
        json={"device_id": dev["device_id"]},
        headers=_h(env["owner"]["session"]),
    )
    assert res.json()["mode"] == "delta"
    assert res.json()["events"] == []


def test_pull_full_refresh_when_gap_exceeds_24h(env: dict[str, Any]) -> None:
    client: TestClient = env["client"]
    dev = _register_device(env)
    old = _iso(datetime.now(timezone.utc) - timedelta(days=3))
    with fnd_db() as conn:
        conn.execute(
            """INSERT INTO fnd_sync_state (device_id, tenant_id, last_event_seq, last_sync_at, mode, updated_at)
               VALUES (?, ?, 5, ?, 'delta', ?)""",
            (dev["device_id"], env["tenant_id"], old, old),
        )

    res = client.post(
        "/api/foundation/sync/pull",
        json={"device_id": dev["device_id"]},
        headers=_h(env["owner"]["session"]),
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["mode"] == "full_refresh"
    assert "gap" in data["reason"]

    # Sin cursor previo también es full refresh.
    dev2 = _register_device(env, name="Segundo equipo")
    res = client.post(
        "/api/foundation/sync/pull",
        json={"device_id": dev2["device_id"]},
        headers=_h(env["owner"]["session"]),
    )
    assert res.json()["mode"] == "full_refresh"
    assert "cursor" in res.json()["reason"]


def test_push_queues_and_apply_processes(env: dict[str, Any]) -> None:
    client: TestClient = env["client"]
    dev = _register_device(env)
    headers = _h(env["owner"]["session"])

    res = client.post(
        "/api/foundation/sync/push",
        json={"device_id": dev["device_id"], "mutations": [
            {"method": "post", "path": "/drafts", "body": {"subject": "hola"}},
            {"method": "patch", "path": "/drafts/d9", "body": {"status": "approved"}},
        ]},
        headers=headers,
    )
    assert res.status_code == 200, res.text
    assert res.json()["queued"] == 2

    res = client.get("/api/foundation/sync/mutations?status=queued", headers=headers)
    assert len(res.json()["mutations"]) == 2

    res = client.post(
        "/api/foundation/sync/apply", json={"device_id": dev["device_id"]}, headers=headers
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["processed"] == 2 and data["applied"] == 2 and data["conflicts"] == 0
    assert data["pending_mutations"] == 0

    res = client.get("/api/foundation/sync/mutations?status=applied", headers=headers)
    assert len(res.json()["mutations"]) == 2


def test_apply_marks_conflict_when_resource_changed_after_queue(env: dict[str, Any]) -> None:
    client: TestClient = env["client"]
    dev = _register_device(env)
    headers = _h(env["owner"]["session"])

    res = client.post(
        "/api/foundation/sync/push",
        json={"device_id": dev["device_id"], "mutations": [
            {"method": "patch", "path": "/drafts/d42", "body": {"status": "approved"}},
        ]},
        headers=headers,
    )
    assert res.status_code == 200

    # Otro actor modifica el recurso después de encolar → conflicto (LWW con detección).
    import time

    time.sleep(0.01)
    with fnd_db() as conn:
        emit_event(conn, env["tenant_id"], "drafts", "draft.updated", {"path": "/drafts/d42"})

    res = client.post(
        "/api/foundation/sync/apply", json={"device_id": dev["device_id"]}, headers=headers
    )
    data = res.json()
    assert data["conflicts"] == 1 and data["applied"] == 0
    assert "conflicto" in data["results"][0]["error"]
    assert data["pending_mutations"] == 1  # conflict sigue bloqueando updates


# ---------------------------------------------------------------------------
# M20 — auto update
# ---------------------------------------------------------------------------

MANIFEST = {
    "version": "9.9.9",
    "min_supported_client_version": "0.1.0",
    "url": "https://updates.test/faberloom-9.9.9.bin",
    "sha256": "0" * 64,
    "notes": "test release",
}


def _put_manifest(env: dict[str, Any], manifest: dict[str, Any], channel: str = "stable"):
    return env["client"].put(
        "/api/foundation/updates/manifest",
        json={"channel": channel, "manifest": manifest},
        headers=_h(env["owner"]["session"]),
    )


def test_current_version_from_file(env: dict[str, Any]) -> None:
    res = env["client"].get(
        "/api/foundation/updates/current", headers=_h(env["owner"]["session"])
    )
    assert res.status_code == 200
    assert res.json()["version"]  # contenido de app/VERSION


def test_manifest_put_requires_permission(env: dict[str, Any]) -> None:
    res = env["client"].put(
        "/api/foundation/updates/manifest",
        json={"channel": "stable", "manifest": MANIFEST},
        headers=_h(env["viewer"]["session"]),
    )
    assert res.status_code == 403

    res = _put_manifest(env, MANIFEST)
    assert res.status_code == 200, res.text

    res = env["client"].get(
        "/api/foundation/updates/manifest?channel=stable", headers=_h(env["viewer"]["session"])
    )
    assert res.json()["manifest"]["version"] == "9.9.9"


def test_check_force_update_below_min_supported(env: dict[str, Any]) -> None:
    dev = _register_device(env)
    manifest = dict(MANIFEST, min_supported_client_version="2.0.0")
    assert _put_manifest(env, manifest).status_code == 200

    res = env["client"].post(
        "/api/foundation/updates/check",
        json={"device_id": dev["device_id"], "current_version": "1.0.0", "channel": "stable"},
        headers=_h(env["owner"]["session"]),
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["action"] == "force_update"
    assert data["min_supported_client_version"] == "2.0.0"

    # Versión al día → up_to_date.
    res = env["client"].post(
        "/api/foundation/updates/check",
        json={"device_id": dev["device_id"], "current_version": "9.9.9", "channel": "stable"},
        headers=_h(env["owner"]["session"]),
    )
    assert res.json()["action"] == "up_to_date"


def test_install_gated_by_pending_mutations_until_reconcile(env: dict[str, Any]) -> None:
    client: TestClient = env["client"]
    dev = _register_device(env)
    headers = _h(env["owner"]["session"])
    assert _put_manifest(env, MANIFEST).status_code == 200

    res = client.post(
        "/api/foundation/updates/check",
        json={"device_id": dev["device_id"], "current_version": "0.2.0", "channel": "stable"},
        headers=headers,
    )
    assert res.json()["action"] == "update_available"

    res = client.post(
        "/api/foundation/updates/stage",
        json={"device_id": dev["device_id"], "version": "9.9.9"},
        headers=headers,
    )
    assert res.status_code == 200 and res.json()["status"] == "staged"

    # Mutación offline pendiente → install bloqueado (regla M19/M20).
    res = client.post(
        "/api/foundation/sync/push",
        json={"device_id": dev["device_id"], "mutations": [
            {"method": "post", "path": "/outcomes", "body": {"kind": "won"}},
        ]},
        headers=headers,
    )
    assert res.status_code == 200

    res = client.post(
        "/api/foundation/updates/install", json={"device_id": dev["device_id"]}, headers=headers
    )
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "blocked"
    assert res.json()["blocked_reason"] == "pending mutations"

    state = client.get(
        f"/api/foundation/updates/state?device_id={dev['device_id']}", headers=headers
    ).json()
    assert state["status"] == "blocked"

    # Apply + reconcile desbloquean.
    res = client.post(
        "/api/foundation/sync/apply", json={"device_id": dev["device_id"]}, headers=headers
    )
    assert res.json()["pending_mutations"] == 0
    res = client.post(
        "/api/foundation/sync/reconcile", json={"device_id": dev["device_id"]}, headers=headers
    )
    assert res.status_code == 200 and res.json()["mode"] == "delta"

    res = client.post(
        "/api/foundation/updates/install", json={"device_id": dev["device_id"]}, headers=headers
    )
    assert res.status_code == 200, res.text
    assert res.json() == {"status": "installed", "version": "9.9.9"}

    state = client.get(
        f"/api/foundation/updates/state?device_id={dev['device_id']}", headers=headers
    ).json()
    assert state["status"] == "installed"
    assert state["current_version"] == "9.9.9"
    assert state["staged_version"] is None


def test_install_blocked_while_sync_mode_full(env: dict[str, Any]) -> None:
    client: TestClient = env["client"]
    dev = _register_device(env)
    headers = _h(env["owner"]["session"])
    assert _put_manifest(env, MANIFEST).status_code == 200

    client.post(
        "/api/foundation/updates/check",
        json={"device_id": dev["device_id"], "current_version": "0.2.0", "channel": "stable"},
        headers=headers,
    )
    client.post(
        "/api/foundation/updates/stage",
        json={"device_id": dev["device_id"], "version": "9.9.9"},
        headers=headers,
    )

    # Pull sin cursor → modo full sin reconciliar → install bloqueado.
    res = client.post(
        "/api/foundation/sync/pull", json={"device_id": dev["device_id"]}, headers=headers
    )
    assert res.json()["mode"] == "full_refresh"

    res = client.post(
        "/api/foundation/updates/install", json={"device_id": dev["device_id"]}, headers=headers
    )
    assert res.json()["status"] == "blocked"
    assert "full refresh" in res.json()["blocked_reason"]

    client.post(
        "/api/foundation/sync/reconcile", json={"device_id": dev["device_id"]}, headers=headers
    )
    res = client.post(
        "/api/foundation/updates/install", json={"device_id": dev["device_id"]}, headers=headers
    )
    assert res.json()["status"] == "installed"
