"""E5-4: ATV sandbox/live HTTP contract tests."""

from __future__ import annotations

import json
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


def _cassette(name: str) -> dict[str, Any]:
    path = Path(__file__).parent / "fixtures" / "atv_cassettes" / name
    return json.loads(path.read_text(encoding="utf-8"))


def _monkeypatch_atv_cassette(monkeypatch: pytest.MonkeyPatch, cassette_name: str) -> None:
    """Patch the internal HTTP helper to replay a JSON cassette."""
    cassette = _cassette(cassette_name)
    body = json.dumps(cassette, ensure_ascii=False).encode("utf-8")

    def _fake_request(method: str, url: str, **kwargs: Any) -> tuple[int, bytes]:
        return 200, body

    monkeypatch.setattr(
        "app.src.connectors.tax_authority._http_request",
        _fake_request,
    )


def test_atv_document_status_parses_cassette(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.src.connectors.tax_authority import get_tax_connector
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    _monkeypatch_atv_cassette(monkeypatch, "document_status_accepted.json")

    with db_session() as conn:
        _set_tenant_setting(conn, "default", "connectors.tax.atv.mode", "sandbox")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.base_url", "https://atv-sandbox.example.test")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.document_status_endpoint", "documents/{document_key}")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.taxpayer_info_endpoint", "taxpayers/{taxpayer_id}")
        conn.commit()
        _set_connector_secret(ctx, "atv", "api_key", "sandbox-key")
        connector = get_tax_connector(ctx, conn, "atv")
        result = connector.check_document_status("50607072400012345678901234567890123456789")

    assert result["status"] == "succeeded"
    assert result["authority"] == "atv"
    assert result["mode"] == "sandbox"
    assert result["authority_status"] == "aceptado"
    assert len(result["evidence"]) == 1
    item = result["evidence"][0]
    assert item["source_type"] == "sandbox"
    assert item["content_hash"]
    assert "50607072400012345678901234567890123456789" in item["content_text"]


def test_atv_taxpayer_info_parses_cassette(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.src.connectors.tax_authority import get_tax_connector
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    _monkeypatch_atv_cassette(monkeypatch, "taxpayer_info_active.json")

    with db_session() as conn:
        _set_tenant_setting(conn, "default", "connectors.tax.atv.mode", "sandbox")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.base_url", "https://atv-sandbox.example.test")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.document_status_endpoint", "documents/{document_key}")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.taxpayer_info_endpoint", "taxpayers/{taxpayer_id}")
        conn.commit()
        _set_connector_secret(ctx, "atv", "api_key", "sandbox-key")
        connector = get_tax_connector(ctx, conn, "atv")
        result = connector.fetch_taxpayer_info("3-101-123456")

    assert result["status"] == "succeeded"
    assert result["authority"] == "atv"
    assert result["mode"] == "sandbox"
    assert result["authority_status"] == "activo"
    assert len(result["evidence"]) == 1
    item = result["evidence"][0]
    assert item["source_type"] == "sandbox"
    assert "3-101-123456" in item["content_text"]


def test_atv_missing_endpoint_fails_closed(client: TestClient) -> None:
    from app.src.connectors.tax_authority import TaxConnectorError, get_tax_connector
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        _set_tenant_setting(conn, "default", "connectors.tax.atv.mode", "sandbox")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.base_url", "https://atv-sandbox.example.test")
        conn.commit()
        _set_connector_secret(ctx, "atv", "api_key", "sandbox-key")
        connector = get_tax_connector(ctx, conn, "atv")

    with pytest.raises(TaxConnectorError, match="PENDIENTE"):
        connector.check_document_status("001-0001-0001")


def test_sat_dian_remain_pending(client: TestClient) -> None:
    from app.src.connectors.tax_authority import TaxConnectorError, get_tax_connector
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        _set_tenant_setting(conn, "default", "connectors.tax.sat.mode", "sandbox")
        _set_tenant_setting(conn, "default", "connectors.tax.sat.base_url", "https://sat.example.test")
        _set_tenant_setting(conn, "default", "connectors.tax.sat.document_status_endpoint", "documents/{document_key}")
        _set_tenant_setting(conn, "default", "connectors.tax.sat.taxpayer_info_endpoint", "taxpayers/{taxpayer_id}")
        conn.commit()
        _set_connector_secret(ctx, "sat", "api_key", "sandbox-key")
        connector = get_tax_connector(ctx, conn, "sat")

    with pytest.raises(TaxConnectorError, match="PENDIENTE"):
        connector.check_document_status("001-0001-0001")


def test_live_without_certificate_he2_9(client: TestClient) -> None:
    from app.src.connectors.tax_authority import TaxConnectorError, get_tax_connector
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        _set_tenant_setting(conn, "default", "connectors.tax.atv.mode", "live")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.base_url", "https://atv.example.test")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.document_status_endpoint", "documents/{document_key}")
        _set_tenant_setting(conn, "default", "connectors.tax.atv.taxpayer_info_endpoint", "taxpayers/{taxpayer_id}")
        conn.commit()
        _set_connector_secret(ctx, "atv", "api_key", "secret-key")
        connector = get_tax_connector(ctx, conn, "atv")

    with pytest.raises(TaxConnectorError, match="certificado no configurado \\(HE2-9\\)"):
        connector.check_document_status("001-0001-0001")
