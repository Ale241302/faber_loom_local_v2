"""E3-2: tax authority connectors (ATV/SAT/DIAN) adapter layer."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-at-least-32-bytes-long-xyz")
    monkeypatch.setenv("FABERLOOM_USERS", '{"owner@example.test":"password"}')
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(config_dir))

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
    response = client.get(
        "/api/workspaces",
        headers=_auth_headers("owner@example.test", "default", "owner"),
    )
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def _set_tenant_setting(
    conn: Any,
    tenant_id: str,
    key: str,
    value: Any,
) -> None:
    from app.src.db import utc_now

    conn.execute(
        """
        INSERT INTO tenant_settings (tenant_id, key, value_json, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(tenant_id, key) DO UPDATE SET
            value_json = excluded.value_json,
            updated_at = excluded.updated_at
        """,
        (tenant_id, key, json.dumps(value, ensure_ascii=False), utc_now()),
    )


def _set_connector_secret(
    ctx: Any,
    authority: str,
    suffix: str,
    plaintext: str,
) -> None:
    from app.src.connectors.tax_authority import set_tax_connector_secret

    set_tax_connector_secret(ctx, authority, suffix, plaintext)


def test_mock_connector_returns_mock_evidence(client: TestClient) -> None:
    from app.src.config_cascade import resolve
    from app.src.connectors.tax_authority import get_tax_connector
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        # Default mode is mock when no config is present.
        connector = get_tax_connector(ctx, conn, "atv")
        result = connector.check_document_status("001-0001-0001")

    assert result["status"] == "succeeded"
    assert result["mode"] == "mock"
    assert len(result["evidence"]) == 1
    item = result["evidence"][0]
    assert item["source_type"] == "mock"
    assert "mock://atv/document-status/001-0001-0001" in item["source_locator"]
    assert item["content_hash"]


def test_live_without_credentials_fail_closed(client: TestClient) -> None:
    from app.src.connectors.tax_authority import TaxConnectorError, get_tax_connector
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        _set_tenant_setting(conn, "default", "connectors.tax.atv.mode", "live")
        conn.commit()
        connector = get_tax_connector(ctx, conn, "atv")

    with pytest.raises(TaxConnectorError, match="no configurado"):
        connector.check_document_status("001-0001-0001")


def test_live_without_certificate_fails_he2_9(client: TestClient) -> None:
    from app.src.connectors.tax_authority import TaxConnectorError, get_tax_connector
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        _set_tenant_setting(conn, "default", "connectors.tax.atv.mode", "live")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.base_url", "https://atv.example.test")
        conn.commit()
        _set_connector_secret(ctx, "atv", "api_key", "secret-key")
        connector = get_tax_connector(ctx, conn, "atv")

    with pytest.raises(TaxConnectorError, match="certificado no configurado \\(HE2-9\\)"):
        connector.check_document_status("001-0001-0001")


def test_tenant_isolation_for_connector_secrets(client: TestClient) -> None:
    from app.src.connectors.tax_authority import get_tax_connector_secret
    from app.src.context import Context

    workspace_id = _demo_workspace_id(client)
    ctx_a = Context(workspace_id=workspace_id, tenant_id="tenant_a", user_id="local", actor_id="local")
    ctx_b = Context(workspace_id=workspace_id, tenant_id="tenant_b", user_id="local", actor_id="local")

    _set_connector_secret(ctx_a, "sat", "api_key", "secret-a")

    assert get_tax_connector_secret(ctx_a, "sat", "api_key") == "secret-a"
    assert get_tax_connector_secret(ctx_b, "sat", "api_key") is None


def test_external_lookup_with_tax_fetcher_for_fe_skill(client: TestClient) -> None:
    from app.src.connectors.tax_authority import build_tax_fetcher
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import external_lookup

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        fetcher = build_tax_fetcher(ctx, conn, "SKILL_FE_STATUS_CHECK")
        assert fetcher is not None

        result = external_lookup(
            ctx,
            conn,
            skill_id="SKILL_FE_STATUS_CHECK",
            query="estado comprobante 001-0001-0001",
            required_sources=["atv", "sat"],
            fetcher=fetcher,
        )

    assert result["status"] == "succeeded"
    assert len(result["evidence"]) == 2  # one item per queried authority
    for item in result["evidence"]:
        assert item["source_type"] == "mock"
        assert item["source_locator"].startswith("mock://")


def test_external_lookup_fails_closed_without_fetcher(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import external_lookup

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        result = external_lookup(
            ctx,
            conn,
            skill_id="SKILL_FE_STATUS_CHECK",
            query="estado comprobante 001",
            required_sources=["atv"],
            fetcher=None,
        )

    assert result["status"] == "failed"
    assert result["error"] == "external_lookup_unavailable"
    assert result["evidence"] == []
