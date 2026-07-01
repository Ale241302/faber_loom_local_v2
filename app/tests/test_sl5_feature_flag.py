"""SL5: email connector feature flag gates the mail surface."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("FABERLOOM_ENABLE_EMAIL_CONNECTOR", "false")

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
        "FABERLOOM_DEV_TRUST_HEADERS",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_features_endpoint_reports_disabled_email_connector(client: TestClient) -> None:
    response = client.get("/api/features")
    assert response.status_code == 200
    assert response.json()["email_connector_enabled"] is False


def test_mail_endpoints_return_404_when_feature_disabled(client: TestClient) -> None:
    workspace_id = _create_workspace(client, "No Mail")
    assert client.get(f"/api/workspaces/{workspace_id}/mail").status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/mail/sync").status_code == 404
    assert client.post(f"/api/workspaces/{workspace_id}/mail/msg_draft/draft").status_code == 404


def test_admin_email_config_is_editable_when_feature_disabled(client: TestClient) -> None:
    workspace_id = _create_workspace(client, "Mail Admin")
    # SMTP config may be missing, but the endpoint must not be gated by the feature flag.
    smtp_get = client.get(f"/api/workspaces/{workspace_id}/admin/smtp-config")
    assert smtp_get.status_code in (200, 404), smtp_get.text
    imap_get = client.get(f"/api/workspaces/{workspace_id}/admin/imap-config")
    assert imap_get.status_code == 200, imap_get.text
    assert imap_get.json() == []
    sig_get = client.get(f"/api/workspaces/{workspace_id}/email-signature")
    assert sig_get.status_code == 200, sig_get.text
    assert sig_get.json()["email_signature"] == ""

    # Updating the signature must succeed.
    sig_put = client.put(
        f"/api/workspaces/{workspace_id}/email-signature",
        json={"email_signature": "Saludos,\nEquipo"},
    )
    assert sig_put.status_code == 200, sig_put.text
    assert sig_put.json()["email_signature"] == "Saludos,\nEquipo"

    # Creating an IMAP account must succeed.
    imap_post = client.post(
        f"/api/workspaces/{workspace_id}/admin/imap-config",
        json={
            "label": "Principal",
            "provider": "imap",
            "host": "imap.ejemplo.com",
            "port": 993,
            "username": "user@example.com",
            "password": "secret",
            "folders_json": '["INBOX"]',
            "auth_type": "password",
            "read_only": 1,
            "is_default": 1,
        },
    )
    assert imap_post.status_code == 201, imap_post.text
    assert imap_post.json()["host"] == "imap.ejemplo.com"
