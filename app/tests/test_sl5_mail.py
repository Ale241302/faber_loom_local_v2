"""SL5: workspace-scoped SMTP administration endpoints."""

from __future__ import annotations

import email.message
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "cfg"))
    monkeypatch.setenv("FABERLOOM_ENABLE_EMAIL_CONNECTOR", "true")

    # Keep IMAP env vars present so other SL5 paths do not fail; SMTP-specific
    # tests will override/disable as needed.
    monkeypatch.setenv("FABERLOOM_IMAP_SERVER", "imap.example.com")
    monkeypatch.setenv("FABERLOOM_IMAP_PORT", "993")
    monkeypatch.setenv("FABERLOOM_IMAP_USER", "loom@example.com")
    monkeypatch.setenv("FABERLOOM_IMAP_PASSWORD", "secret-not-logged")

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
        "FABERLOOM_SMTP_SERVER",
        "FABERLOOM_SMTP_PORT",
        "FABERLOOM_SMTP_USER",
        "FABERLOOM_SMTP_PASSWORD",
        "FABERLOOM_SMTP_FROM",
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


def _sample_smtp_config() -> dict[str, Any]:
    return {
        "host": "mail.example.com",
        "port": 465,
        "use_ssl": True,
        "username": "info@example.com",
        "password": "example-app-password",
        "from_email": "info@example.com",
    }


def _patch_send_message(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    import app.src.api as api_module
    import app.src.connectors.imap as imap_module

    calls: list[dict[str, Any]] = []

    def fake_send_message(*args: Any, **kwargs: Any) -> None:
        calls.append({"args": args, "kwargs": kwargs})

    # api.py imports send_message into its own namespace, so patch both the
    # source module and the consumer module.
    monkeypatch.setattr(imap_module, "send_message", fake_send_message)
    monkeypatch.setattr(api_module, "send_message", fake_send_message)
    return calls


def test_get_smtp_config_returns_404_when_missing(client: TestClient) -> None:
    workspace_id = _create_workspace(client, "SMTP Missing")
    response = client.get(f"/api/workspaces/{workspace_id}/admin/smtp-config")
    assert response.status_code == 404
    assert "smtp" in response.json()["detail"].lower()


def test_put_and_get_smtp_config(client: TestClient) -> None:
    workspace_id = _create_workspace(client, "SMTP Config")
    config = _sample_smtp_config()

    response = client.put(f"/api/workspaces/{workspace_id}/admin/smtp-config", json=config)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["host"] == config["host"]
    assert data["port"] == config["port"]
    assert data["use_ssl"] is True
    assert data["username"] == config["username"]
    # The spike returns the password to the admin form; it must never be logged.
    assert data["password"] == config["password"]
    assert data["from_email"] == config["from_email"]

    response = client.get(f"/api/workspaces/{workspace_id}/admin/smtp-config")
    assert response.status_code == 200
    assert response.json() == data


def test_smtp_test_endpoint_sends_to_local_user(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace_id = _create_workspace(client, "SMTP Test Local")
    client.put(f"/api/workspaces/{workspace_id}/admin/smtp-config", json=_sample_smtp_config())
    calls = _patch_send_message(monkeypatch)

    response = client.post(f"/api/workspaces/{workspace_id}/admin/smtp-config/test")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["sent_to"] == "local"
    assert data["status"] == "sent"

    assert len(calls) == 1
    call = calls[0]
    assert call["args"][0] == "mail.example.com"
    assert call["args"][1] == 465
    assert call["args"][2] == "info@example.com"
    assert call["kwargs"]["to"] == "local"
    assert call["kwargs"]["subject"] == "FaberLoom: prueba SMTP"
    assert call["kwargs"]["body"] == "Este es un correo de prueba desde FaberLoom."
    assert call["kwargs"]["use_ssl"] is True
    assert call["kwargs"]["from_email"] == "info@example.com"


def test_smtp_test_endpoint_uses_jwt_sub(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    import app.src.auth as auth_module

    workspace_id = _create_workspace(client, "SMTP Test JWT")

    # Enable auth with a deterministic secret and user.
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret")
    monkeypatch.setenv("FABERLOOM_USERS", '{"admin@mwt.one":"secret"}')

    login = client.post("/api/auth/login", json={"email": "admin@mwt.one", "password": "secret"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Store the SMTP config as the authenticated user so the per-user lookup succeeds.
    client.put(f"/api/workspaces/{workspace_id}/admin/smtp-config", headers=headers, json=_sample_smtp_config())
    calls = _patch_send_message(monkeypatch)

    response = client.post(
        f"/api/workspaces/{workspace_id}/admin/smtp-config/test",
        headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json()["sent_to"] == "admin@mwt.one"

    assert len(calls) == 1
    assert calls[0]["kwargs"]["to"] == "admin@mwt.one"


def test_send_message_supports_use_ssl_false(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.src.connectors.imap as imap_module

    class FakeSMTP:
        calls: list[dict[str, Any]] = []

        def __init__(self, server: str, port: int) -> None:
            self.server = server
            self.port = port

        def __enter__(self) -> "FakeSMTP":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def starttls(self) -> None:
            pass

        def login(self, username: str, password: str) -> None:
            pass

        def send_message(self, msg: email.message.EmailMessage) -> None:
            self.calls.append({"server": self.server, "port": self.port, "from": msg["From"], "to": msg["To"]})

    FakeSMTP.calls = []
    monkeypatch.setattr(imap_module.smtplib, "SMTP_SSL", object)
    monkeypatch.setattr(imap_module.smtplib, "SMTP", FakeSMTP)

    imap_module.send_message(
        "smtp.example.com",
        587,
        "user@example.com",
        "secret",
        to="dest@example.com",
        subject="Hola",
        body="Mensaje",
        use_ssl=False,
        from_email="noreply@example.com",
    )

    assert len(FakeSMTP.calls) == 1
    assert FakeSMTP.calls[0]["server"] == "smtp.example.com"
    assert FakeSMTP.calls[0]["port"] == 587
    assert FakeSMTP.calls[0]["from"] == "noreply@example.com"
    assert FakeSMTP.calls[0]["to"] == "dest@example.com"


def test_smtp_config_is_workspace_isolated(client: TestClient) -> None:
    ws_a = _create_workspace(client, "SMTP A")
    ws_b = _create_workspace(client, "SMTP B")

    client.put(f"/api/workspaces/{ws_a}/admin/smtp-config", json=_sample_smtp_config())

    response_b = client.get(f"/api/workspaces/{ws_b}/admin/smtp-config")
    assert response_b.status_code == 404
