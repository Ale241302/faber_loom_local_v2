"""E4-4 — Flujo canónico: CEO pregunta por facturas y profundiza."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import connect
from app.src.kb import ingest_kb_source
from app.src.living_agent.briefs import refresh_workspace_brief


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))

    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
        "KIMI_API_KEY",
        "MOONSHOT_API_KEY",
        "FABERLOOM_KIMI_API_KEY",
        "FABERLOOM_ENABLE_OLLAMA",
        "FABERLOOM_OLLAMA_ENABLED",
        "FABERLOOM_PROVIDER_ALLOWLIST",
        "FABERLOOM_BUDGET_CAP_USD",
        "FABERLOOM_AUTO_MODE_ENABLED",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _headers(role: str = "owner") -> dict[str, str]:
    return {"x-actor-role": role, "x-user-id": "test", "x-actor-id": "test"}


def _general_id(client: TestClient) -> str:
    return client.get("/api/workspaces/general", headers=_headers("owner")).json()["id"]


def _create_workspace(client: TestClient, name: str, slug: str) -> str:
    resp = client.post(
        "/api/workspaces",
        json={"name": name, "slug": slug},
        headers=_headers("owner"),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _context(ws_id: str, role: str = "owner", tenant_id: str = "default") -> Context:
    return Context(
        workspace_id=ws_id,
        tenant_id=tenant_id,
        user_id="test",
        actor_id="test",
        actor_role_at_decision=role,
    )


def _create_invoice(client: TestClient, invoice_id: str, total: float) -> None:
    resp = client.post(
        "/api/tenants/default/invoices",
        json={
            "invoice_id": invoice_id,
            "customer_name": "Colombia Textiles S.A.",
            "customer_tax_id": "123456",
            "customer_email": "colombia@example.com",
            "issue_date": "2026-07-01",
            "due_date": "2026-07-31",
            "line_items": [{"description": "Tela", "quantity": 1, "unit_price": total, "tax_pct": 0}],
            "currency": "USD",
            "notes": "",
        },
        headers=_headers("owner"),
    )
    assert resp.status_code == 201, resp.text


def _seed_kb(ws_id: str) -> None:
    conn = connect()
    ctx = _context(ws_id)
    ingest_kb_source(
        ctx,
        conn,
        title="Cuenta Colombia Textiles",
        source_type="md",
        content_text="## Cliente Colombia Textiles\n\nFactura FAC-COL-001 por USD 5000. Contacto: Ana López.",
        source_version="v1",
        approved_by="test",
    )
    refresh_workspace_brief(ctx, conn, ws_id)


def _create_chat(client: TestClient, workspace_id: str) -> str:
    resp = client.post(
        f"/api/workspaces/{workspace_id}/chats",
        json={"title": "CEO"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_canonical_invoice_flow(client: TestClient) -> None:
    colombia_id = _create_workspace(client, "Colombia", "colombia")
    _seed_kb(colombia_id)

    # Set CONTENT policy so invoice aggregates are cached in the brief.
    conn = connect()
    from app.src import key_broker
    from app.src.key_broker import KeyLevel
    key_broker.set_policy(
        conn,
        tenant_id="default",
        space_id=colombia_id,
        level=KeyLevel.CONTENT,
        approver_roles={"owner"},
        updated_by="test",
    )

    _create_invoice(client, "FAC-COL-001", 5000.0)
    # Refresh brief after invoice so open_invoices aggregate is included.
    refresh_workspace_brief(_context(colombia_id), conn, colombia_id)

    general_id = _general_id(client)
    chat_id = _create_chat(client, general_id)

    # 1. General question: what invoices do I have from Colombia?
    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "qué facturas tengo del cliente Colombia", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200, resp.text
    content = resp.json()["message"]["content"]
    assert "5000" in content or "facturas" in content.lower()

    # 2. Deep-dive: show me the Colombia one.
    resp = client.post(
        f"/api/workspaces/{general_id}/chats/{chat_id}/completions",
        json={"message": "muéstrame la de Colombia", "mode": "manual"},
        headers=_headers("owner"),
    )
    assert resp.status_code == 200, resp.text
    content = resp.json()["message"]["content"].lower()
    assert "colombia" in content
    assert "ana" in content or "5000" in content
