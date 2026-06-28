"""SL2: workspace KB inheritance (parent/child) and cross-tenant isolation."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))

    for name in (
        "OPENAI_API_KEY",
        "FABERLOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "FABERLOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FABERLOOM_GOOGLE_API_KEY",
        "FABERLOOM_ENABLE_OLLAMA",
        "FABERLOOM_OLLAMA_ENABLED",
        "FABERLOOM_PROVIDER_ALLOWLIST",
        "FABERLOOM_BUDGET_CAP_USD",
    ):
        monkeypatch.delenv(name, raising=False)

    # Trust headers only for the cross-tenant test below.
    monkeypatch.setenv("FABERLOOM_DEV_TRUST_HEADERS", "true")

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _create_workspace(
    client: TestClient,
    name: str,
    *,
    parent_id: str | None = None,
    inherits_kb: int = 0,
    tenant_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"name": name, "inherits_kb": inherits_kb}
    if parent_id:
        payload["parent_id"] = parent_id
    headers = {"x-tenant-id": tenant_id} if tenant_id else {}
    response = client.post("/api/workspaces", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


def _upload_csv(
    client: TestClient,
    workspace_id: str,
    csv_text: bytes,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    import io

    response = client.post(
        f"/api/workspaces/{workspace_id}/kb/upload",
        data={"title": "Catalog", "source_version": "v1"},
        files={"file": ("catalog.csv", io.BytesIO(csv_text), "text/csv")},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_child_workspace_inherits_parent_kb(client: TestClient) -> None:
    parent = _create_workspace(client, "Parent")
    _upload_csv(
        client,
        parent["id"],
        b"sku,nombre,precio_usd,moneda,stock,vigente_desde,vigente_hasta\n"
        b"TEL-001,Oxford,12.50,USD,240,2026-01-01,2026-12-31",
    )

    child = _create_workspace(client, "Child", parent_id=parent["id"], inherits_kb=1)
    assert child["parent_id"] == parent["id"]
    assert child["inherits_kb"] is True or child["inherits_kb"] == 1

    search = client.get(f"/api/workspaces/{child['id']}/kb/search?q=TEL-001")
    assert search.status_code == 200
    data = search.json()
    assert any(fact["entity_key"] == "TEL-001" for fact in data["facts"])


def test_child_without_inheritance_is_isolated(client: TestClient) -> None:
    parent = _create_workspace(client, "Parent Isolated")
    _upload_csv(
        client,
        parent["id"],
        b"sku,price\nTEL-001,12.50",
    )

    child = _create_workspace(client, "Child Isolated", parent_id=parent["id"], inherits_kb=0)
    search = client.get(f"/api/workspaces/{child['id']}/kb/search?q=TEL-001")
    assert search.status_code == 200
    assert not any(fact["entity_key"] == "TEL-001" for fact in search.json()["facts"])


def test_inheritance_does_not_cross_tenants(client: TestClient) -> None:
    parent = _create_workspace(client, "Parent Tenant", tenant_id="tenant-a")
    response = client.post(
        "/api/workspaces",
        json={"name": "Child Tenant", "parent_id": parent["id"], "inherits_kb": 1},
        headers={"x-tenant-id": "tenant-b"},
    )
    assert response.status_code == 422
    assert "different tenant" in response.json()["detail"].lower()


def test_kb_sources_are_tenant_isolated(client: TestClient) -> None:
    ws_a = _create_workspace(client, "Tenant A", tenant_id="tenant-a")
    ws_b = _create_workspace(client, "Tenant B", tenant_id="tenant-b")

    _upload_csv(
        client, ws_a["id"], b"sku,price\nTEL-001,12.50", headers={"x-tenant-id": "tenant-a"}
    )

    list_a = client.get(
        f"/api/workspaces/{ws_a['id']}/kb/sources", headers={"x-tenant-id": "tenant-a"}
    )
    list_b = client.get(
        f"/api/workspaces/{ws_b['id']}/kb/sources", headers={"x-tenant-id": "tenant-b"}
    )
    assert list_a.status_code == 200
    assert list_b.status_code == 200
    a_ids = {s["id"] for s in list_a.json()}
    b_ids = {s["id"] for s in list_b.json()}
    assert a_ids
    assert not a_ids & b_ids
