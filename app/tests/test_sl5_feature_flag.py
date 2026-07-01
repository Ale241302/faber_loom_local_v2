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
    assert client.get(f"/api/workspaces/{workspace_id}/admin/smtp-config").status_code == 404
    assert client.get(f"/api/workspaces/{workspace_id}/admin/imap-config").status_code == 404
    assert client.get(f"/api/workspaces/{workspace_id}/email-signature").status_code == 404
