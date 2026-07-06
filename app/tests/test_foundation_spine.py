"""Tests de los módulos SPINE de Foundation Beta (M07, M08, M09, M11, M12, M15, M16).

Cubre: bootstrap completo → login → me, lockout, 2FA (enroll/confirm/login),
guardrail del último owner, policy gate fail-closed + allowlist, verificación
de la cadena de audit y polling de eventos con after_seq.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

OWNER = {"email": "owner@acme.test", "display_name": "Owner", "password": "s3cret-pass"}


def _make_app():
    """App real si es importable; si no (p. ej. Python < 3.12 en CI), una app
    mínima que monta foundation_router con el mismo prefijo y lifespan."""
    try:
        from app.src.main import create_app

        return create_app()
    except Exception:
        from contextlib import asynccontextmanager

        from fastapi import FastAPI

        from app.src.foundation import foundation_router, init_foundation_db

        @asynccontextmanager
        async def lifespan(app):
            init_foundation_db()
            yield

        app = FastAPI(lifespan=lifespan)
        app.include_router(foundation_router, prefix="/api")
        return app


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "fnd.sqlite3"))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_AUTH_DISABLED", "1")
    with TestClient(_make_app()) as test_client:
        yield test_client


def _bootstrap(client: TestClient) -> tuple[str, dict]:
    """Wizard completo: tenant → owner → activate. Devuelve (session, user)."""
    resp = client.post(
        "/api/foundation/bootstrap/tenant", json={"name": "ACME S.A.", "slug": "acme"}
    )
    assert resp.status_code == 201, resp.text
    resp = client.post("/api/foundation/bootstrap/owner", json=OWNER)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    session, user = data["session"], data["user"]
    resp = client.post(
        "/api/foundation/bootstrap/activate", headers={"X-Fnd-Session": session}
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["tenant"]["status"] == "active"
    return session, user


def _h(session: str) -> dict[str, str]:
    return {"X-Fnd-Session": session}


# ---------------------------------------------------------------------------
# M07 Bootstrap + M08 login / me
# ---------------------------------------------------------------------------


def test_bootstrap_flow_login_and_me(client: TestClient):
    # Estado inicial: sin tenant.
    state = client.get("/api/foundation/bootstrap/state").json()
    assert state["step"] == "tenant"
    assert client.get("/api/foundation/status").json()["bootstrapped"] is False

    session, user = _bootstrap(client)
    assert session.startswith("fnds_")
    assert user["roles"] == ["owner"]
    assert "*" in user["permissions"]

    # Post-activación: los endpoints de bootstrap quedan cerrados (salvo state).
    assert client.get("/api/foundation/bootstrap/state").json()["step"] == "done"
    resp = client.post(
        "/api/foundation/bootstrap/tenant", json={"name": "Otro", "slug": "otro"}
    )
    assert resp.status_code == 409

    # Login normal.
    resp = client.post(
        "/api/foundation/auth/login",
        json={"email": OWNER["email"], "password": OWNER["password"]},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["requires_2fa"] is False
    token = data["session"]

    # /me con la forma que consume el shell.
    me = client.get("/api/foundation/auth/me", headers=_h(token)).json()
    for key in ("id", "email", "display_name", "roles", "permissions", "tenant_id"):
        assert key in me
    assert me["email"] == OWNER["email"]
    assert "*" in me["permissions"]

    # Logout revoca la sesión.
    assert client.post("/api/foundation/auth/logout", headers=_h(token)).status_code == 200
    assert client.get("/api/foundation/auth/me", headers=_h(token)).status_code == 401


def test_sso_bridge_main_jwt_to_foundation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """SSO local-first: con el tenant ya bootstrapeado, un JWT principal de
    FaberLoom válido cuyo ``sub`` (email) coincide con un usuario Foundation
    activo autentica los endpoints Foundation SIN sesión ``fnds_`` propia.

    Regresión cubierta: el hardening P0 restringió el puente JWT a las rutas
    ``/bootstrap/*``, dejando el shell (que reusa la sesión principal, sin login
    propio) colgado en 401 "Foundation session required" tras el bootstrap.
    """
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "fnd.sqlite3"))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_USERS", '{"owner@acme.test": "pw"}')
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-sso-at-least-32-bytes-long")
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)

    from app.src.auth import create_access_token

    with TestClient(_make_app()) as client:
        _bootstrap(client)  # crea owner@acme.test + activa el tenant

        # JWT principal del owner, SIN X-Fnd-Session: el shell solo tiene esto.
        jwt_token = create_access_token(OWNER["email"])
        resp = client.get(
            "/api/foundation/auth/me",
            headers={"Authorization": f"Bearer {jwt_token}"},
        )
        assert resp.status_code == 200, resp.text
        me = resp.json()
        assert me["email"] == OWNER["email"]
        assert me["roles"] == ["owner"]
        assert "*" in me["permissions"]

        # Guard de seguridad: un JWT válido de un email SIN usuario Foundation
        # NO obtiene sesión — no se reabre el bypass de permisos '*' sintéticos.
        intruder = create_access_token("intruder@acme.test")
        resp = client.get(
            "/api/foundation/auth/me",
            headers={"Authorization": f"Bearer {intruder}"},
        )
        assert resp.status_code == 401, resp.text


def test_login_lockout_after_five_failures(client: TestClient):
    _bootstrap(client)
    for i in range(4):
        resp = client.post(
            "/api/foundation/auth/login",
            json={"email": OWNER["email"], "password": "wrong-pass"},
        )
        assert resp.status_code == 401, f"intento {i}"
    # 5º fallo → lockout.
    resp = client.post(
        "/api/foundation/auth/login",
        json={"email": OWNER["email"], "password": "wrong-pass"},
    )
    assert resp.status_code == 401
    # Con la cuenta bloqueada, incluso la password correcta devuelve 423.
    resp = client.post(
        "/api/foundation/auth/login",
        json={"email": OWNER["email"], "password": OWNER["password"]},
    )
    assert resp.status_code == 423

    # El lockout queda en el audit trail.
    session, _ = _relogin_after_unlock(client)
    entries = client.get(
        "/api/foundation/audit?action=auth.login.lockout", headers=_h(session)
    ).json()["entries"]
    assert len(entries) == 1


def _relogin_after_unlock(client: TestClient) -> tuple[str, dict]:
    """Desbloquea al owner manualmente (simula expiración de los 15 min)."""
    import os
    import sqlite3

    conn = sqlite3.connect(os.environ["FABERLOOM_FOUNDATION_DB"])
    conn.execute("UPDATE fnd_users SET failed_attempts = 0, locked_until = NULL")
    conn.commit()
    conn.close()
    resp = client.post(
        "/api/foundation/auth/login",
        json={"email": OWNER["email"], "password": OWNER["password"]},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    return data["session"], data.get("user") or {}


# ---------------------------------------------------------------------------
# M08 2FA
# ---------------------------------------------------------------------------


def test_2fa_enroll_confirm_and_login(client: TestClient):
    from app.src.foundation import core

    session, _ = _bootstrap(client)

    resp = client.post("/api/foundation/auth/2fa/enroll", headers=_h(session))
    assert resp.status_code == 200, resp.text
    enroll = resp.json()
    assert enroll["otpauth_uri"].startswith("otpauth://totp/")
    secret = enroll["secret"]

    # Confirmar con código inválido falla; con código válido activa.
    resp = client.post(
        "/api/foundation/auth/2fa/confirm", json={"code": "000000"}, headers=_h(session)
    )
    assert resp.status_code == 400
    resp = client.post(
        "/api/foundation/auth/2fa/confirm",
        json={"code": core.totp_now(secret)},
        headers=_h(session),
    )
    assert resp.status_code == 200
    assert resp.json()["totp_enabled"] is True

    # Login ahora requiere 2FA (sesión stage=totp, no sirve para /me).
    resp = client.post(
        "/api/foundation/auth/login",
        json={"email": OWNER["email"], "password": OWNER["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["requires_2fa"] is True
    pending = data["session"]
    assert client.get("/api/foundation/auth/me", headers=_h(pending)).status_code == 401

    # Código inválido no promueve; el válido sí.
    resp = client.post(
        "/api/foundation/auth/2fa/verify", json={"session": pending, "code": "111111"}
    )
    assert resp.status_code == 401
    resp = client.post(
        "/api/foundation/auth/2fa/verify",
        json={"session": pending, "code": core.totp_now(secret)},
    )
    assert resp.status_code == 200, resp.text
    full = resp.json()["session"]
    me = client.get("/api/foundation/auth/me", headers=_h(full)).json()
    assert me["email"] == OWNER["email"]
    assert me["totp_enabled"] is True


def test_sessions_list_and_revoke(client: TestClient):
    session, _ = _bootstrap(client)
    resp = client.post(
        "/api/foundation/auth/login",
        json={"email": OWNER["email"], "password": OWNER["password"]},
    )
    other = resp.json()["session"]

    sessions = client.get("/api/foundation/auth/sessions", headers=_h(session)).json()["sessions"]
    assert len(sessions) == 2
    assert sum(1 for s in sessions if s["current"]) == 1

    resp = client.post(
        f"/api/foundation/auth/sessions/{other}/revoke", headers=_h(session)
    )
    assert resp.status_code == 200
    assert client.get("/api/foundation/auth/me", headers=_h(other)).status_code == 401


# ---------------------------------------------------------------------------
# M09 RBAC — guardrails de owner
# ---------------------------------------------------------------------------


def test_rbac_users_roles_and_last_owner_guardrail(client: TestClient):
    session, owner_user = _bootstrap(client)

    # Crear un operator.
    resp = client.post(
        "/api/foundation/rbac/users",
        json={"email": "ops@acme.test", "display_name": "Ops",
              "password": "otra-pass-123", "roles": ["operator"]},
        headers=_h(session),
    )
    assert resp.status_code == 201, resp.text
    ops = resp.json()
    assert ops["roles"] == ["operator"]

    # Guardrail: el último owner no puede quitarse el rol owner.
    resp = client.post(
        f"/api/foundation/rbac/users/{owner_user['id']}/roles",
        json={"roles": ["admin"]},
        headers=_h(session),
    )
    assert resp.status_code == 400
    # Tampoco puede desactivarse.
    resp = client.patch(
        f"/api/foundation/rbac/users/{owner_user['id']}",
        json={"status": "disabled"},
        headers=_h(session),
    )
    assert resp.status_code == 400

    # Un no-owner no puede otorgar owner (operator ni siquiera tiene users.manage).
    resp = client.post(
        "/api/foundation/auth/login",
        json={"email": "ops@acme.test", "password": "otra-pass-123"},
    )
    ops_session = resp.json()["session"]
    resp = client.post(
        f"/api/foundation/rbac/users/{ops['id']}/roles",
        json={"roles": ["owner"]},
        headers=_h(ops_session),
    )
    assert resp.status_code == 403

    # Con un segundo owner, el primero ya puede ceder su rol.
    resp = client.post(
        f"/api/foundation/rbac/users/{ops['id']}/roles",
        json={"roles": ["owner"]},
        headers=_h(session),
    )
    assert resp.status_code == 200
    resp = client.post(
        f"/api/foundation/rbac/users/{owner_user['id']}/roles",
        json={"roles": ["admin"]},
        headers=_h(session),
    )
    assert resp.status_code == 200
    assert resp.json()["roles"] == ["admin"]


def test_rbac_custom_roles(client: TestClient):
    session, _ = _bootstrap(client)
    catalog = client.get("/api/foundation/rbac/permissions", headers=_h(session)).json()
    assert "audit.read" in catalog["permissions"]
    assert "*" not in catalog["permissions"]

    resp = client.post(
        "/api/foundation/rbac/roles",
        json={"name": "auditor", "description": "Solo audit",
              "permissions": ["audit.read", "events.read"]},
        headers=_h(session),
    )
    assert resp.status_code == 201, resp.text
    role = resp.json()
    assert role["is_system"] is False

    # No se puede editar permisos de un rol system ni borrar uno en uso.
    roles = client.get("/api/foundation/rbac/roles", headers=_h(session)).json()["roles"]
    owner_role = next(r for r in roles if r["name"] == "owner")
    resp = client.patch(
        f"/api/foundation/rbac/roles/{owner_role['id']}",
        json={"permissions": ["audit.read"]},
        headers=_h(session),
    )
    assert resp.status_code == 400
    resp = client.delete(
        f"/api/foundation/rbac/roles/{owner_role['id']}", headers=_h(session)
    )
    assert resp.status_code == 400

    # El rol custom sin uso sí se puede borrar.
    resp = client.delete(
        f"/api/foundation/rbac/roles/{role['id']}", headers=_h(session)
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# M11 Policy Gate — fail-closed y allowlist
# ---------------------------------------------------------------------------


def test_policy_evaluate_fail_closed_and_allowlist(client: TestClient):
    session, _ = _bootstrap(client)

    # Sin policies: outbound → needs_approval (fail-closed); otras → allow.
    resp = client.post(
        "/api/foundation/policy/evaluate",
        json={"action": "draft.send", "context": {"recipients": ["a@x.com"]}},
        headers=_h(session),
    )
    assert resp.status_code == 200
    assert resp.json()["decision"] == "needs_approval"

    resp = client.post(
        "/api/foundation/policy/evaluate",
        json={"action": "memory.write", "context": {}},
        headers=_h(session),
    )
    assert resp.json()["decision"] == "allow"

    # Policy con allowlist de dominios.
    resp = client.post(
        "/api/foundation/policy/policies",
        json={"name": "outbound-allowlist", "kind": "outbound",
              "rules": {"actions": ["draft.send", "email.send"],
                        "allow_domains": ["cliente.com"],
                        "max_recipients": 2}},
        headers=_h(session),
    )
    assert resp.status_code == 201, resp.text
    policy_id = resp.json()["id"]

    ok = client.post(
        "/api/foundation/policy/evaluate",
        json={"action": "draft.send", "context": {"recipients": ["ana@cliente.com"]}},
        headers=_h(session),
    ).json()
    assert ok["decision"] == "allow"
    assert ok["policy_id"] == policy_id

    deny = client.post(
        "/api/foundation/policy/evaluate",
        json={"action": "draft.send", "context": {"recipients": ["eve@otra.com"]}},
        headers=_h(session),
    ).json()
    assert deny["decision"] == "deny"

    too_many = client.post(
        "/api/foundation/policy/evaluate",
        json={"action": "draft.send",
              "context": {"recipients": [f"u{i}@cliente.com" for i in range(3)]}},
        headers=_h(session),
    ).json()
    assert too_many["decision"] == "deny"

    # require_hitl fuerza needs_approval aunque el resto pase.
    resp = client.patch(
        f"/api/foundation/policy/policies/{policy_id}",
        json={"rules": {"actions": ["draft.send"], "allow_domains": ["cliente.com"],
                        "require_hitl": True}},
        headers=_h(session),
    )
    assert resp.status_code == 200
    hitl = client.post(
        "/api/foundation/policy/evaluate",
        json={"action": "draft.send", "context": {"recipients": ["ana@cliente.com"]}},
        headers=_h(session),
    ).json()
    assert hitl["decision"] == "needs_approval"

    # DELETE = disable (no borra) → vuelve el fail-closed.
    resp = client.delete(
        f"/api/foundation/policy/policies/{policy_id}", headers=_h(session)
    )
    assert resp.status_code == 200
    assert resp.json()["enabled"] == 0
    again = client.post(
        "/api/foundation/policy/evaluate",
        json={"action": "draft.send", "context": {"recipients": ["ana@cliente.com"]}},
        headers=_h(session),
    ).json()
    assert again["decision"] == "needs_approval"

    decisions = client.get(
        "/api/foundation/policy/decisions", headers=_h(session)
    ).json()["decisions"]
    assert len(decisions) >= 6


# ---------------------------------------------------------------------------
# M12 Audit Trail
# ---------------------------------------------------------------------------


def test_audit_chain_verify_filters_and_export(client: TestClient):
    session, _ = _bootstrap(client)

    verify = client.get("/api/foundation/audit/verify", headers=_h(session)).json()
    assert verify["ok"] is True
    assert verify["checked"] >= 3  # tenant.created, owner.created, activated…
    assert verify["broken_at"] is None

    entries = client.get(
        "/api/foundation/audit?action=tenant.activated", headers=_h(session)
    ).json()["entries"]
    assert len(entries) == 1
    assert entries[0]["action"] == "tenant.activated"

    export = client.get("/api/foundation/audit/export", headers=_h(session))
    assert export.status_code == 200
    assert export.headers["content-type"].startswith("application/x-ndjson")
    lines = [line for line in export.text.splitlines() if line.strip()]
    assert len(lines) == verify["checked"]  # las lecturas no escriben audit
    import json

    parsed = [json.loads(line) for line in lines]
    assert all(p["tenant_id"] == parsed[0]["tenant_id"] for p in parsed)


# ---------------------------------------------------------------------------
# M15 Outbox Streams — polling con after_seq y consumers
# ---------------------------------------------------------------------------


def test_events_poll_after_seq_and_consumers(client: TestClient):
    session, _ = _bootstrap(client)

    first = client.get("/api/foundation/events", headers=_h(session)).json()
    assert first["count"] >= 2  # tenant.created, owner.created, activated…
    last_seq = first["last_seq"]
    topics = {e["topic"] for e in first["events"]}
    assert "tenant" in topics

    # after_seq = last_seq → sin eventos nuevos.
    empty = client.get(
        f"/api/foundation/events?after_seq={last_seq}", headers=_h(session)
    ).json()
    assert empty["count"] == 0

    # Una mutación (settings) emite un evento nuevo visible tras after_seq.
    resp = client.patch(
        "/api/foundation/tenants/settings",
        json={"settings": {"tz": "America/Mexico_City"}},
        headers=_h(session),
    )
    assert resp.status_code == 200
    fresh = client.get(
        f"/api/foundation/events?after_seq={last_seq}", headers=_h(session)
    ).json()
    assert fresh["count"] == 1
    assert fresh["events"][0]["topic"] == "tenant"
    assert fresh["events"][0]["type"] == "settings.updated"

    # Filtro por topic.
    only_tenant = client.get(
        "/api/foundation/events?topic=tenant", headers=_h(session)
    ).json()
    assert all(e["topic"] == "tenant" for e in only_tenant["events"])

    # Consumer ack + lag.
    resp = client.post(
        "/api/foundation/events/consumers/ui/ack",
        json={"seq": last_seq},
        headers=_h(session),
    )
    assert resp.status_code == 200
    status_data = client.get(
        "/api/foundation/events/stream-status", headers=_h(session)
    ).json()
    ui = next(c for c in status_data["consumers"] if c["consumer"] == "ui")
    assert ui["lag"] == status_data["last_seq"] - last_seq

    aggregates = client.get("/api/foundation/events/topics", headers=_h(session)).json()
    assert any(t["topic"] == "tenant" for t in aggregates["topics"])


# ---------------------------------------------------------------------------
# M16 Tenant Isolation
# ---------------------------------------------------------------------------


def test_tenant_info_settings_and_isolation_check(client: TestClient):
    session, _ = _bootstrap(client)

    info = client.get("/api/foundation/tenants", headers=_h(session)).json()
    assert info["slug"] == "acme"
    assert info["status"] == "active"
    assert info["users_count"] == 1

    resp = client.patch(
        "/api/foundation/tenants/settings",
        json={"settings": {"idioma": "es"}},
        headers=_h(session),
    )
    assert resp.status_code == 200
    assert resp.json()["settings"]["idioma"] == "es"

    report = client.get(
        "/api/foundation/tenants/isolation-check", headers=_h(session)
    ).json()
    assert report["ok"] is True
    tables = {t["table"] for t in report["tables"]}
    assert {"fnd_users", "fnd_sessions", "fnd_audit_log", "fnd_events"} <= tables
    assert all(t["foreign_rows"] == 0 for t in report["tables"])

    # Sin sesión → fail-closed (401).
    assert client.get("/api/foundation/tenants").status_code == 401
    assert client.get("/api/foundation/events").status_code == 401
    assert client.get("/api/foundation/audit").status_code == 401
