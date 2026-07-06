"""Tests multi-tenant (M16 extendido): crear tenants, crear usuarios en un
tenant específico, mover usuarios entre tenants, self-service de tenant vía
JWT principal, login multi-tenant y aislamiento.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

OWNER = {"email": "owner@acme.test", "display_name": "Owner", "password": "s3cret-pass"}


def _make_app():
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
    return session, user


def _h(session: str) -> dict[str, str]:
    return {"X-Fnd-Session": session}


def _login(client: TestClient, email: str, password: str, tenant: str | None = None) -> dict:
    body = {"email": email, "password": password}
    if tenant:
        body["tenant"] = tenant
    resp = client.post("/api/foundation/auth/login", json=body)
    assert resp.status_code == 200, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Crear tenant + usuarios en tenant específico
# ---------------------------------------------------------------------------


def test_create_tenant_with_owner_and_login(client: TestClient):
    session, _ = _bootstrap(client)

    resp = client.post(
        "/api/foundation/tenants",
        json={
            "name": "Beta Corp",
            "slug": "beta",
            "owner_email": "boss@beta.test",
            "owner_display_name": "Boss",
            "owner_password": "beta-pass-123",
        },
        headers=_h(session),
    )
    assert resp.status_code == 201, resp.text
    tenant = resp.json()
    assert tenant["slug"] == "beta"
    assert tenant["status"] == "active"  # con owner se activa solo
    assert tenant["users_count"] == 1
    assert tenant["owners_count"] == 1

    # Aparece en el listado global.
    resp = client.get("/api/foundation/tenants/all", headers=_h(session))
    assert resp.status_code == 200, resp.text
    slugs = [t["slug"] for t in resp.json()["tenants"]]
    assert slugs == ["acme", "beta"]

    # El owner del tenant nuevo puede loguearse directo (multi-tenant login).
    data = _login(client, "boss@beta.test", "beta-pass-123")
    assert data["user"]["tenant_slug"] == "beta"
    assert data["user"]["roles"] == ["owner"]

    # Y su vista de usuarios NO incluye a los de acme (aislamiento).
    me_users = client.get(
        "/api/foundation/rbac/users", headers=_h(data["session"])
    ).json()["users"]
    assert [u["email"] for u in me_users] == ["boss@beta.test"]


def test_create_tenant_without_owner_stays_provisioning(client: TestClient):
    session, _ = _bootstrap(client)
    resp = client.post(
        "/api/foundation/tenants",
        json={"name": "Gamma", "slug": "gamma"},
        headers=_h(session),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["status"] == "provisioning"

    # Slug duplicado → 409.
    resp = client.post(
        "/api/foundation/tenants",
        json={"name": "Gamma 2", "slug": "gamma"},
        headers=_h(session),
    )
    assert resp.status_code == 409

    # owner_email sin owner_password → 400.
    resp = client.post(
        "/api/foundation/tenants",
        json={"name": "Delta", "slug": "delta", "owner_email": "x@d.test"},
        headers=_h(session),
    )
    assert resp.status_code == 400


def test_create_user_in_specific_tenant_activates_with_owner(client: TestClient):
    session, _ = _bootstrap(client)
    tenant = client.post(
        "/api/foundation/tenants",
        json={"name": "Gamma", "slug": "gamma"},
        headers=_h(session),
    ).json()
    assert tenant["status"] == "provisioning"

    # Crear un operator no activa el tenant.
    resp = client.post(
        f"/api/foundation/tenants/{tenant['id']}/users",
        json={"email": "op@gamma.test", "password": "gamma-pass-1", "roles": ["operator"]},
        headers=_h(session),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["tenant_slug"] == "gamma"

    all_tenants = client.get("/api/foundation/tenants/all", headers=_h(session)).json()["tenants"]
    gamma = next(t for t in all_tenants if t["slug"] == "gamma")
    assert gamma["status"] == "provisioning"

    # Crear un owner sí lo activa.
    resp = client.post(
        f"/api/foundation/tenants/{tenant['id']}/users",
        json={"email": "boss@gamma.test", "password": "gamma-pass-2", "roles": ["owner"]},
        headers=_h(session),
    )
    assert resp.status_code == 201, resp.text
    all_tenants = client.get("/api/foundation/tenants/all", headers=_h(session)).json()["tenants"]
    gamma = next(t for t in all_tenants if t["slug"] == "gamma")
    assert gamma["status"] == "active"

    # El operator del tenant activo ya puede loguearse.
    data = _login(client, "op@gamma.test", "gamma-pass-1")
    assert data["user"]["tenant_slug"] == "gamma"


def test_tenants_manage_requires_permission(client: TestClient):
    session, _ = _bootstrap(client)
    # Crear un viewer en acme: no tiene tenants.manage.
    resp = client.post(
        "/api/foundation/rbac/users",
        json={"email": "viewer@acme.test", "password": "viewer-pass-1", "roles": ["viewer"]},
        headers=_h(session),
    )
    assert resp.status_code == 201, resp.text
    data = _login(client, "viewer@acme.test", "viewer-pass-1")
    v = data["session"]
    assert client.get("/api/foundation/tenants/all", headers=_h(v)).status_code == 403
    assert client.post(
        "/api/foundation/tenants", json={"name": "Nope", "slug": "nope"}, headers=_h(v)
    ).status_code == 403


# ---------------------------------------------------------------------------
# Mover usuarios entre tenants
# ---------------------------------------------------------------------------


def test_assign_user_to_other_tenant(client: TestClient):
    session, _ = _bootstrap(client)
    # Usuario operador en acme.
    user = client.post(
        "/api/foundation/rbac/users",
        json={"email": "op@acme.test", "password": "acme-pass-1", "roles": ["operator"]},
        headers=_h(session),
    ).json()
    # Tenant destino con owner propio.
    tenant = client.post(
        "/api/foundation/tenants",
        json={
            "name": "Beta", "slug": "beta",
            "owner_email": "boss@beta.test", "owner_password": "beta-pass-123",
        },
        headers=_h(session),
    ).json()

    resp = client.post(
        f"/api/foundation/tenants/{tenant['id']}/assign",
        json={"user_id": user["id"]},
        headers=_h(session),
    )
    assert resp.status_code == 200, resp.text
    moved = resp.json()
    assert moved["tenant_slug"] == "beta"
    assert moved["roles"] == ["operator"]  # conserva sus roles por nombre

    # Ya no está en acme.
    users = client.get("/api/foundation/rbac/users", headers=_h(session)).json()["users"]
    assert "op@acme.test" not in [u["email"] for u in users]

    # Login del movido entra a beta.
    data = _login(client, "op@acme.test", "acme-pass-1")
    assert data["user"]["tenant_slug"] == "beta"

    # Aislamiento sin fugas tras el movimiento.
    report = client.get(
        "/api/foundation/tenants/isolation-check", headers=_h(session)
    ).json()
    assert report["ok"] is True


def test_assign_guardrails(client: TestClient):
    session, me = _bootstrap(client)
    tenant = client.post(
        "/api/foundation/tenants",
        json={
            "name": "Beta", "slug": "beta",
            "owner_email": "boss@beta.test", "owner_password": "beta-pass-123",
        },
        headers=_h(session),
    ).json()

    # No moverse a sí mismo.
    resp = client.post(
        f"/api/foundation/tenants/{tenant['id']}/assign",
        json={"user_id": me["id"]},
        headers=_h(session),
    )
    assert resp.status_code == 400

    # No mover al último owner de un tenant que aún tiene usuarios.
    client.post(
        "/api/foundation/rbac/users",
        json={"email": "op@acme.test", "password": "acme-pass-1", "roles": ["operator"]},
        headers=_h(session),
    )
    boss = _login(client, "boss@beta.test", "beta-pass-123")
    # boss intenta mover al owner de acme (que tiene otro usuario) → 400.
    resp = client.post(
        f"/api/foundation/tenants/{tenant['id']}/assign",
        json={"user_id": me["id"]},
        headers=_h(boss["session"]),
    )
    assert resp.status_code == 400

    # Conflicto de email en destino → 409.
    dup = client.post(
        f"/api/foundation/tenants/{tenant['id']}/users",
        json={"email": "op@acme.test", "password": "beta-pass-999"},
        headers=_h(session),
    )
    assert dup.status_code == 201
    op_acme = next(
        u for u in client.get("/api/foundation/rbac/users", headers=_h(session)).json()["users"]
        if u["email"] == "op@acme.test"
    )
    resp = client.post(
        f"/api/foundation/tenants/{tenant['id']}/assign",
        json={"user_id": op_acme["id"]},
        headers=_h(session),
    )
    assert resp.status_code == 409


# ---------------------------------------------------------------------------
# Ver y quitar usuarios de un tenant específico
# ---------------------------------------------------------------------------


def test_list_and_remove_user_from_tenant(client: TestClient):
    session, me = _bootstrap(client)
    tenant = client.post(
        "/api/foundation/tenants",
        json={
            "name": "Beta", "slug": "beta",
            "owner_email": "boss@beta.test", "owner_password": "beta-pass-123",
        },
        headers=_h(session),
    ).json()
    client.post(
        f"/api/foundation/tenants/{tenant['id']}/users",
        json={"email": "op@beta.test", "password": "beta-pass-456", "roles": ["operator"]},
        headers=_h(session),
    )

    # Listar usuarios del tenant beta desde acme (cross-tenant admin).
    resp = client.get(f"/api/foundation/tenants/{tenant['id']}/users", headers=_h(session))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["tenant"]["slug"] == "beta"
    emails = {u["email"]: u for u in data["users"]}
    assert set(emails) == {"boss@beta.test", "op@beta.test"}
    assert emails["boss@beta.test"]["roles"] == ["owner"]
    assert all(u["tenant_slug"] == "beta" for u in data["users"])

    # Guardrail: quitar al último owner con otros usuarios presentes → 400.
    resp = client.delete(
        f"/api/foundation/tenants/{tenant['id']}/users/{emails['boss@beta.test']['id']}",
        headers=_h(session),
    )
    assert resp.status_code == 400

    # Quitar al operator sí funciona y revoca sus sesiones.
    op_login = _login(client, "op@beta.test", "beta-pass-456")
    resp = client.delete(
        f"/api/foundation/tenants/{tenant['id']}/users/{emails['op@beta.test']['id']}",
        headers=_h(session),
    )
    assert resp.status_code == 200, resp.text
    assert client.get(
        "/api/foundation/auth/me", headers=_h(op_login["session"])
    ).status_code == 401

    # Ahora el owner (único usuario restante) sí puede quitarse → tenant queda vacío.
    resp = client.delete(
        f"/api/foundation/tenants/{tenant['id']}/users/{emails['boss@beta.test']['id']}",
        headers=_h(session),
    )
    assert resp.status_code == 200, resp.text
    data = client.get(
        f"/api/foundation/tenants/{tenant['id']}/users", headers=_h(session)
    ).json()
    assert data["users"] == []

    # No podés quitarte a vos mismo.
    resp = client.delete(
        f"/api/foundation/tenants/{_my_tenant_id(client, session)}/users/{me['id']}",
        headers=_h(session),
    )
    assert resp.status_code == 400


def _my_tenant_id(client: TestClient, session: str) -> str:
    return client.get("/api/foundation/auth/me", headers=_h(session)).json()["tenant_id"]


# ---------------------------------------------------------------------------
# Login multi-tenant con email duplicado
# ---------------------------------------------------------------------------


def test_login_same_email_in_two_tenants_requires_slug(client: TestClient):
    session, _ = _bootstrap(client)
    client.post(
        "/api/foundation/tenants",
        json={
            "name": "Beta", "slug": "beta",
            "owner_email": OWNER["email"], "owner_password": "beta-pass-123",
        },
        headers=_h(session),
    )
    # Sin slug → 409 con la lista de tenants.
    resp = client.post(
        "/api/foundation/auth/login",
        json={"email": OWNER["email"], "password": OWNER["password"]},
    )
    assert resp.status_code == 409
    assert "acme" in resp.json()["detail"] and "beta" in resp.json()["detail"]

    # Con slug entra al tenant correcto (cada uno con su password).
    data = _login(client, OWNER["email"], OWNER["password"], tenant="acme")
    assert data["user"]["tenant_slug"] == "acme"
    data = _login(client, OWNER["email"], "beta-pass-123", tenant="beta")
    assert data["user"]["tenant_slug"] == "beta"


# ---------------------------------------------------------------------------
# Self-service: usuario JWT sin tenant crea el suyo
# ---------------------------------------------------------------------------


def test_self_service_tenant_via_jwt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "fnd.sqlite3"))
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        '{"owner@acme.test": "pw", "nuevo@solo.test": "pw2"}',
    )
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-sso-at-least-32-bytes-long")
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)

    from app.src.auth import create_access_token

    with TestClient(_make_app()) as client:
        _bootstrap(client)

        # JWT de un email SIN usuario Foundation → puede crear su tenant.
        jwt_token = create_access_token("nuevo@solo.test")
        headers = {"Authorization": f"Bearer {jwt_token}"}
        resp = client.post(
            "/api/foundation/tenants/self-service",
            json={"name": "Solo Ventures", "slug": "solo", "password": "solo-pass-123"},
            headers=headers,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["tenant"]["slug"] == "solo"
        assert data["tenant"]["status"] == "active"
        assert data["user"]["email"] == "nuevo@solo.test"
        assert data["user"]["roles"] == ["owner"]
        assert data["session"].startswith("fnds_")

        # Con la sesión devuelta opera su tenant.
        me = client.get(
            "/api/foundation/auth/me", headers={"X-Fnd-Session": data["session"]}
        ).json()
        assert me["tenant_slug"] == "solo"

        # El SSO por JWT ahora también resuelve a su tenant.
        me = client.get("/api/foundation/auth/me", headers=headers).json()
        assert me["tenant_slug"] == "solo"

        # Repetir → 409 (ya está asignado).
        resp = client.post(
            "/api/foundation/tenants/self-service",
            json={"name": "Otra", "slug": "otra", "password": "solo-pass-123"},
            headers=headers,
        )
        assert resp.status_code == 409

        # Un email que YA tiene usuario Foundation → 409.
        jwt_owner = create_access_token(OWNER["email"])
        resp = client.post(
            "/api/foundation/tenants/self-service",
            json={"name": "Dup", "slug": "dup", "password": "dup-pass-1234"},
            headers={"Authorization": f"Bearer {jwt_owner}"},
        )
        assert resp.status_code == 409

        # Sin JWT → 401.
        resp = client.post(
            "/api/foundation/tenants/self-service",
            json={"name": "Anon", "slug": "anon", "password": "anon-pass-123"},
        )
        assert resp.status_code == 401
