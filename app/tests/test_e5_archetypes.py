"""E5 — Fabrica de arquetipos (SPEC_FB_ARCHETYPE_FACTORY_v1).

Un arquetipo es la plantilla reutilizable de "como se hace un tipo de trabajo".
Es tenant-scoped, referencia un routing_preset (la unica faceta que es una
entidad real) y copia el resto hacia la routine al materializarse.

Mandatorio: test_cross_tenant_isolation (P0 de AGENTS.md:38).
"""

from __future__ import annotations

import hashlib
import os
import sqlite3
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """App aislada con Foundation y app DB frescas."""

    monkeypatch.setenv("FABERLOOM_DB_PATH", str(tmp_path / "faberloom.sqlite3"))
    monkeypatch.setenv("FABERLOOM_FOUNDATION_DB", str(tmp_path / "foundation.sqlite3"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv(
        "FABERLOOM_USERS",
        '{"admin@platform.test":"admin-pass","owner@acme.test":"owner-pass","owner@other.test":"owner-pass"}',
    )
    monkeypatch.delenv("FABERLOOM_AUTH_DISABLED", raising=False)

    from app.src.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


def _foundation_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(os.environ["FABERLOOM_FOUNDATION_DB"])
    conn.row_factory = sqlite3.Row
    return conn


def _create_foundation_user(
    conn: sqlite3.Connection, tenant_id: str, email: str, role: str
) -> str:
    from app.src.foundation.core import hash_password, new_id, seed_system_roles, utcnow

    seed_system_roles(conn, tenant_id)
    user_id = new_id("usr")
    now = utcnow()
    conn.execute(
        """
        INSERT INTO fnd_users
        (id, tenant_id, email, display_name, password_hash, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'active', ?)
        """,
        (user_id, tenant_id, email, email.split("@")[0], hash_password("irrelevant"), now),
    )
    role_row = conn.execute(
        "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?", (tenant_id, role)
    ).fetchone()
    if role_row is None:
        raise RuntimeError(f"Role {role} missing for tenant {tenant_id}")
    conn.execute(
        """
        INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (tenant_id, user_id, role_row["id"], user_id, now),
    )
    return user_id


def _bootstrap_owner_tenant(slug: str, email: str) -> str:
    from app.src.foundation.core import new_id, utcnow

    conn = _foundation_conn()
    try:
        tenant_id = new_id("tnt")
        conn.execute(
            """
            INSERT INTO fnd_tenants (id, name, slug, status, plan, created_at, activated_at)
            VALUES (?, ?, ?, 'active', 'starter', ?, ?)
            """,
            (tenant_id, f"Tenant {slug}", slug, utcnow(), utcnow()),
        )
        _create_foundation_user(conn, tenant_id, email, "owner")
        conn.commit()
        return tenant_id
    finally:
        conn.close()


def _login(client: TestClient, email: str, password: str) -> None:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text


def _tenant_id(client: TestClient) -> str:
    return client.get("/api/me").json()["tenant_id"]


def _create_preset(client: TestClient, tenant_id: str, preset_id: str) -> None:
    resp = client.post(
        f"/api/tenants/{tenant_id}/presets",
        json={
            "preset_id": preset_id,
            "name": preset_id.title(),
            "envelope": {"providers_allow": ["anthropic", "openai"]},
            "curve": {"mode": "balanceado"},
        },
    )
    assert resp.status_code == 201, resp.text


_SKILL_MD = (
    "---\n"
    "name: cotizacion-b2b\n"
    "persona: Sos un cotizador formal.\n"
    "tools: []\n"
    "---\n"
    "Responde con precio y plazo."
)


def _archetype_body(**overrides: Any) -> dict[str, Any]:
    body = {
        "archetype_id": "cotizacion-b2b",
        "name": "Cotizacion B2B",
        "description": "Como se hace una cotizacion B2B.",
        "category": "skill",
        "routing_preset_id": None,
        "persona_md": "Sos un cotizador formal.",
        "skill_md": _SKILL_MD,
        "tools_allowlist": '["search"]',
        "schema_output_json": '{"type": "object", "properties": {"precio": {"type": "number"}}}',
        "trigger_json": "{}",
        "is_active": True,
    }
    body.update(overrides)
    return body


def _setup_owner(client: TestClient) -> str:
    _bootstrap_owner_tenant("acme", "owner@acme.test")
    _login(client, "owner@acme.test", "owner-pass")
    return _tenant_id(client)


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


def test_create_and_list_archetype(client: TestClient) -> None:
    tenant_id = _setup_owner(client)
    _create_preset(client, tenant_id, "balanceado")

    resp = client.post(
        f"/api/tenants/{tenant_id}/archetypes",
        json=_archetype_body(routing_preset_id="balanceado"),
    )
    assert resp.status_code == 201, resp.text
    created = resp.json()
    assert created["archetype_id"] == "cotizacion-b2b"
    assert created["routing_preset_id"] == "balanceado"
    assert created["category"] == "skill"
    assert created["version"] == 1

    resp = client.get(f"/api/tenants/{tenant_id}/archetypes")
    assert resp.status_code == 200, resp.text
    assert [a["archetype_id"] for a in resp.json()["archetypes"]] == ["cotizacion-b2b"]

    # El system workspace se crea con el tenant real, no con el sentinel
    # SYSTEM_WORKSPACE_ID. En Postgres con RLS, usar el sentinel como tenant_id
    # viola la politica de workspace y produce HTTP 500.
    app_conn = sqlite3.connect(os.environ["FABERLOOM_DB_PATH"])
    app_conn.row_factory = sqlite3.Row
    row = app_conn.execute(
        "SELECT tenant_id FROM workspace WHERE id = ?", ("__system__",)
    ).fetchone()
    app_conn.close()
    assert row is not None, "system workspace no fue creado"
    assert row["tenant_id"] == tenant_id, (
        f"system workspace pertenece a {row['tenant_id']!r}, no al tenant activo {tenant_id!r}"
    )


def test_archetype_without_preset_is_legal(client: TestClient) -> None:
    """routing_preset_id NULL no rompe el FK compuesto."""
    tenant_id = _setup_owner(client)

    resp = client.post(
        f"/api/tenants/{tenant_id}/archetypes",
        json=_archetype_body(routing_preset_id=None),
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["routing_preset_id"] is None


def test_archetype_id_must_be_slug(client: TestClient) -> None:
    tenant_id = _setup_owner(client)

    resp = client.post(
        f"/api/tenants/{tenant_id}/archetypes",
        json=_archetype_body(archetype_id="con/barra"),
    )
    assert resp.status_code == 422, resp.text


def test_archetype_rejects_unknown_preset(client: TestClient) -> None:
    """Un preset inexistente en el tenant no se puede referenciar."""
    tenant_id = _setup_owner(client)

    resp = client.post(
        f"/api/tenants/{tenant_id}/archetypes",
        json=_archetype_body(routing_preset_id="no-existe"),
    )
    assert resp.status_code == 409, resp.text


# ---------------------------------------------------------------------------
# Aislamiento (P0)
# ---------------------------------------------------------------------------


def test_cross_tenant_isolation(client: TestClient) -> None:
    """MANDATORIO: el tenant B no ve ni toca los arquetipos del tenant A."""
    tenant_a = _setup_owner(client)
    resp = client.post(
        f"/api/tenants/{tenant_a}/archetypes", json=_archetype_body()
    )
    assert resp.status_code == 201, resp.text

    _bootstrap_owner_tenant("other", "owner@other.test")
    _login(client, "owner@other.test", "owner-pass")
    tenant_b = _tenant_id(client)
    assert tenant_b != tenant_a

    # B no ve los de A en su propio listado.
    resp = client.get(f"/api/tenants/{tenant_b}/archetypes")
    assert resp.status_code == 200, resp.text
    assert resp.json()["archetypes"] == []

    # B no puede leer el tenant de A.
    resp = client.get(f"/api/tenants/{tenant_a}/archetypes")
    assert resp.status_code == 403, resp.text

    # B no puede leer un arquetipo puntual de A.
    resp = client.get(f"/api/tenants/{tenant_a}/archetypes/cotizacion-b2b")
    assert resp.status_code == 403, resp.text

    # B no puede borrarlo.
    resp = client.delete(f"/api/tenants/{tenant_a}/archetypes/cotizacion-b2b")
    assert resp.status_code == 403, resp.text


def test_archetype_cannot_reference_foreign_tenant_preset(client: TestClient) -> None:
    """El FK compuesto hace inexpresable apuntar al preset de otro tenant."""
    tenant_a = _setup_owner(client)
    _create_preset(client, tenant_a, "solo-de-acme")

    _bootstrap_owner_tenant("other", "owner@other.test")
    _login(client, "owner@other.test", "owner-pass")
    tenant_b = _tenant_id(client)

    resp = client.post(
        f"/api/tenants/{tenant_b}/archetypes",
        json=_archetype_body(routing_preset_id="solo-de-acme"),
    )
    assert resp.status_code == 409, resp.text


# ---------------------------------------------------------------------------
# Integridad referencial
# ---------------------------------------------------------------------------


def test_delete_preset_referenced_by_archetype_fails(client: TestClient) -> None:
    """Borrar un preset referenciado falla con 409, no huerfaniza en silencio.

    delete_routing_preset hoy borra sin chequear nada.
    """
    tenant_id = _setup_owner(client)
    _create_preset(client, tenant_id, "balanceado")
    resp = client.post(
        f"/api/tenants/{tenant_id}/archetypes",
        json=_archetype_body(routing_preset_id="balanceado"),
    )
    assert resp.status_code == 201, resp.text

    resp = client.delete(f"/api/tenants/{tenant_id}/presets/balanceado")
    assert resp.status_code == 409, resp.text
    assert "cotizacion-b2b" in resp.text or "arquetipo" in resp.text.lower()

    # El preset sigue vivo.
    resp = client.get(f"/api/tenants/{tenant_id}/presets/balanceado")
    assert resp.status_code == 200, resp.text


def test_delete_unreferenced_preset_still_works(client: TestClient) -> None:
    """El chequeo referencial no debe romper el borrado normal."""
    tenant_id = _setup_owner(client)
    _create_preset(client, tenant_id, "descartable")

    resp = client.delete(f"/api/tenants/{tenant_id}/presets/descartable")
    assert resp.status_code == 204, resp.text


# ---------------------------------------------------------------------------
# Copy-on-create
# ---------------------------------------------------------------------------


def _workspace_id(client: TestClient) -> str:
    resp = client.post("/api/workspaces", json={"name": "Archetype Test"})
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_routine_from_archetype_copies_facets(client: TestClient) -> None:
    """La routine nace con las facetas del arquetipo."""
    tenant_id = _setup_owner(client)
    _create_preset(client, tenant_id, "balanceado")
    client.post(
        f"/api/tenants/{tenant_id}/archetypes",
        json=_archetype_body(routing_preset_id="balanceado"),
    )
    workspace_id = _workspace_id(client)

    resp = client.post(
        f"/api/workspaces/{workspace_id}/routines/from-archetype/cotizacion-b2b",
        json={"name": "Cotizador Acme"},
    )
    assert resp.status_code == 201, resp.text
    routine = resp.json()

    assert routine["name"] == "Cotizador Acme"
    assert routine["persona_md"] == "Sos un cotizador formal."
    assert routine["tools_allowlist"] == '["search"]'
    assert routine["category"] == "skill"
    # El cuerpo del SKILL.md se copia; el frontmatter se renombra a la instancia.
    assert "Responde con precio y plazo." in routine["skill_md"]
    assert "name: Cotizador Acme" in routine["skill_md"]
    # preset_id se materializa con prefijo: es lo que routine.preset_id espera.
    assert routine["preset_id"] == "@preset/balanceado"


def test_two_routines_from_one_archetype(client: TestClient) -> None:
    """Un arquetipo es una plantilla: debe poder instanciarse N veces.

    Por eso el frontmatter se renombra al materializar; si no, el invariante
    name == frontmatter.name limitaria a una routine por arquetipo.
    """
    tenant_id = _setup_owner(client)
    client.post(f"/api/tenants/{tenant_id}/archetypes", json=_archetype_body())
    workspace_id = _workspace_id(client)

    for name in ("Cotizador Acme", "Cotizador Beta"):
        resp = client.post(
            f"/api/workspaces/{workspace_id}/routines/from-archetype/cotizacion-b2b",
            json={"name": name},
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["name"] == name


def test_routine_records_archetype_provenance(client: TestClient) -> None:
    """routine.archetype_id guarda de donde salio."""
    tenant_id = _setup_owner(client)
    client.post(f"/api/tenants/{tenant_id}/archetypes", json=_archetype_body())
    workspace_id = _workspace_id(client)

    resp = client.post(
        f"/api/workspaces/{workspace_id}/routines/from-archetype/cotizacion-b2b",
        json={"name": "Con procedencia"},
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["archetype_id"] == "cotizacion-b2b"


def test_routine_from_unknown_archetype_is_404(client: TestClient) -> None:
    _setup_owner(client)
    workspace_id = _workspace_id(client)

    resp = client.post(
        f"/api/workspaces/{workspace_id}/routines/from-archetype/no-existe",
        json={"name": "Fantasma"},
    )
    assert resp.status_code == 404, resp.text


def test_editing_archetype_does_not_touch_existing_routines(client: TestClient) -> None:
    """Herencia plana: la copia es una foto, no un espejo.

    La cascada esta DIFERIDA por SPEC_FB_ARCHETYPE_v1 (senal: >=10 tenants).
    """
    tenant_id = _setup_owner(client)
    client.post(f"/api/tenants/{tenant_id}/archetypes", json=_archetype_body())
    workspace_id = _workspace_id(client)

    resp = client.post(
        f"/api/workspaces/{workspace_id}/routines/from-archetype/cotizacion-b2b",
        json={"name": "Foto"},
    )
    assert resp.status_code == 201, resp.text
    routine_id = resp.json()["id"]

    resp = client.patch(
        f"/api/tenants/{tenant_id}/archetypes/cotizacion-b2b",
        json={"persona_md": "PERSONA CAMBIADA"},
    )
    assert resp.status_code == 200, resp.text

    resp = client.get(f"/api/workspaces/{workspace_id}/routines/{routine_id}")
    assert resp.status_code == 200, resp.text
    assert resp.json()["persona_md"] == "Sos un cotizador formal."


def test_update_archetype_bumps_version(client: TestClient) -> None:
    tenant_id = _setup_owner(client)
    client.post(f"/api/tenants/{tenant_id}/archetypes", json=_archetype_body())

    resp = client.patch(
        f"/api/tenants/{tenant_id}/archetypes/cotizacion-b2b",
        json={"name": "Cotizacion B2B v2"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["version"] == 2


# ---------------------------------------------------------------------------
# @mention de arquetipos en chat
# ---------------------------------------------------------------------------

import json


def _capturing_provider(slug: str, model: str) -> tuple[dict[str, Any], Any]:
    from app.src.router.models import CompletionRequest, CompletionResult, ProviderConfig
    from app.src.router.providers import Provider

    captured: dict[str, Any] = {}

    class CapturingProvider(Provider):
        requires_api_key = False

        def __init__(self) -> None:
            super().__init__(
                ProviderConfig(
                    provider_slug=slug,
                    api_key=None,
                    model_default=model,
                    priority=1,
                    is_enabled=True,
                )
            )

        def complete(self, request: CompletionRequest) -> CompletionResult:
            captured["messages"] = list(request.messages)
            return CompletionResult(
                content="CAPTURED",
                model=request.model or model,
                provider_slug=slug,
                input_tokens=10,
                output_tokens=5,
                cost_usd=0.0001,
                duration_ms=5,
            )

    return captured, CapturingProvider


def _patch_workspace_router(monkeypatch: pytest.MonkeyPatch, slug: str = "fake") -> dict[str, Any]:
    from app.src.router import cost as cost_module
    from app.src.router.engine import Router
    import app.src.api as api_module

    captured, ProviderCls = _capturing_provider(slug, f"{slug}-model")
    cost_module.MODEL_ALLOWLIST[slug] = {f"{slug}-model"}
    monkeypatch.setattr(
        api_module, "build_router", lambda *a, **kw: Router(providers=[ProviderCls()])
    )
    return captured


def _patch_presence_router(monkeypatch: pytest.MonkeyPatch, slug: str = "ollama") -> dict[str, Any]:
    from app.src.router.engine import Router
    import app.src.router.registry as registry_module

    captured, ProviderCls = _capturing_provider(slug, f"{slug}-model")
    monkeypatch.setattr(
        registry_module, "build_router", lambda *a, **kw: Router(providers=[ProviderCls()])
    )
    return captured


def test_workspace_chat_with_archetype_adopts_persona(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Seleccionar un arquetipo en un workspace normal inyecta persona_md + skill_md."""
    tenant_id = _setup_owner(client)
    _create_preset(client, tenant_id, "balanceado")
    client.post(
        f"/api/tenants/{tenant_id}/archetypes",
        json=_archetype_body(routing_preset_id="balanceado"),
    )

    workspace_id = _workspace_id(client)
    chat = client.post(
        f"/api/workspaces/{workspace_id}/chats", json={"title": "Archetype mention"}
    ).json()

    captured = _patch_workspace_router(monkeypatch, "fake")
    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}/completions",
        json={"message": "hola", "mode": "manual", "archetype_id": "cotizacion-b2b"},
    )
    assert resp.status_code == 200, resp.text
    assert "messages" in captured, "el modelo nunca fue llamado"
    system = captured["messages"][0]["content"]
    assert "cotizacion-b2b" in system
    assert "Sos un cotizador formal" in system
    assert "Responde con precio y plazo" in system


def _general_workspace(client: TestClient, tenant_id: str) -> dict[str, Any]:
    resp = client.get("/api/workspaces")
    assert resp.status_code == 200, resp.text
    for ws in resp.json()["workspaces"]:
        if ws.get("kind") == "tenant_general":
            return ws
    # Con Foundation auth el seed no crea automáticamente el ws-general para
    # tenants distintos de DEFAULT_TENANT_ID; lo creamos bajo demanda.
    resp = client.post(
        "/api/workspaces",
        json={"name": "Chat general", "slug": f"general-{tenant_id}", "kind": "tenant_general"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_general_chat_with_archetype_adopts_persona(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Seleccionar un arquetipo en SpaceLoom/general chat no devuelve 409 y adopta persona."""
    tenant_id = _setup_owner(client)
    _create_preset(client, tenant_id, "balanceado")
    client.post(
        f"/api/tenants/{tenant_id}/archetypes",
        json=_archetype_body(routing_preset_id="balanceado"),
    )

    general = _general_workspace(client, tenant_id)
    chat = client.post(
        f"/api/workspaces/{general['id']}/chats", json={"title": "General archetype"}
    ).json()

    # Seedea el catálogo con el router real (ollama local está siempre disponible).
    client.post(
        f"/api/workspaces/{general['id']}/chats/{chat['id']}/completions",
        json={"message": "hola", "mode": "manual"},
    )

    captured = _patch_presence_router(monkeypatch, "ollama")
    resp = client.post(
        f"/api/workspaces/{general['id']}/chats/{chat['id']}/completions",
        json={"message": "hola", "mode": "manual", "archetype_id": "cotizacion-b2b"},
    )
    assert resp.status_code == 200, resp.text
    assert "messages" in captured, "el modelo nunca fue llamado"
    system = captured["messages"][0]["content"]
    assert "cotizacion-b2b" in system
    assert "Sos un cotizador formal" in system


def test_general_chat_at_routine_still_rejected(client: TestClient) -> None:
    """Las @routine mentions sin arquetipo siguen rechazadas en el chat general."""
    tenant_id = _setup_owner(client)
    general = _general_workspace(client, tenant_id)
    chat = client.post(
        f"/api/workspaces/{general['id']}/chats", json={"title": "Reject mention"}
    ).json()

    resp = client.post(
        f"/api/workspaces/{general['id']}/chats/{chat['id']}/completions",
        json={"message": "@cotizador hola", "mode": "manual"},
    )
    assert resp.status_code == 409, resp.text
    assert "@routine mentions are not supported in the general chat" in resp.json()["detail"]


def test_workspace_chat_unknown_archetype_returns_404(client: TestClient) -> None:
    _setup_owner(client)
    workspace_id = _workspace_id(client)
    chat = client.post(
        f"/api/workspaces/{workspace_id}/chats", json={"title": "Invalid archetype"}
    ).json()

    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}/completions",
        json={"message": "hola", "mode": "manual", "archetype_id": "no-existe"},
    )
    assert resp.status_code == 404, resp.text
    assert "no-existe" in resp.json()["detail"]


def test_general_chat_unknown_archetype_returns_404(client: TestClient) -> None:
    tenant_id = _setup_owner(client)
    general = _general_workspace(client, tenant_id)
    chat = client.post(
        f"/api/workspaces/{general['id']}/chats", json={"title": "Invalid archetype"}
    ).json()

    resp = client.post(
        f"/api/workspaces/{general['id']}/chats/{chat['id']}/completions",
        json={"message": "hola", "mode": "manual", "archetype_id": "no-existe"},
    )
    assert resp.status_code == 404, resp.text
    assert "no-existe" in resp.json()["detail"]


def test_at_routine_mention_still_works(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Las @routine mentions existentes en workspace siguen funcionando (backwards compat)."""
    from app.src.skills import compile_skill_md, _extract_runtime

    tenant_id = _setup_owner(client)
    workspace_id = _workspace_id(client)

    skill_md = """---
name: cotizador
persona: Eres un asistente de cotizaciones.
tools: ["calculator"]
schema_output: {"type": "object", "properties": {"precio": {"type": "number"}}, "required": ["precio"]}
triggers: ["@cotizador"]
---
Genera una cotización en JSON con el precio.
"""
    compiled = compile_skill_md(skill_md)
    runtime = _extract_runtime(skill_md)
    payload = {
        "name": compiled["name"],
        "skill_md": skill_md,
        "persona_md": runtime.get("persona", ""),
        "tools_allowlist": json.dumps(runtime.get("tools", [])),
        "schema_output_json": json.dumps(runtime.get("schema_output", {})),
        "trigger_json": json.dumps(runtime.get("triggers", [])),
        "is_active": 1,
        "source_version": "v1",
    }
    routine = client.post(f"/api/workspaces/{workspace_id}/routines", json=payload).json()
    client.post(f"/api/workspaces/{workspace_id}/routines/{routine['id']}/approve")

    _patch_workspace_router(monkeypatch, "fake")
    chat = client.post(
        f"/api/workspaces/{workspace_id}/chats", json={"title": "Mention"}
    ).json()
    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats/{chat['id']}/completions",
        json={"message": "@cotizador cuánto sale Oxford"},
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["message"]["role"] == "assistant"
