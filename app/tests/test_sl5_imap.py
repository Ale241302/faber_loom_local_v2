"""SL5: IMAP read-first connector with HITL-guarded SMTP send."""

from __future__ import annotations

import email.message
import imaplib
import smtplib
from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "spaceloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("SPACELOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("SPACELOOM_IMAP_SERVER", "imap.example.com")
    monkeypatch.setenv("SPACELOOM_IMAP_PORT", "993")
    monkeypatch.setenv("SPACELOOM_IMAP_USER", "loom@example.com")
    monkeypatch.setenv("SPACELOOM_IMAP_PASSWORD", "secret-not-logged")
    monkeypatch.setenv("SPACELOOM_SMTP_SERVER", "smtp.example.com")
    monkeypatch.setenv("SPACELOOM_SMTP_PORT", "465")

    for name in (
        "OPENAI_API_KEY",
        "SPACELOOM_OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "SPACELOOM_ANTHROPIC_API_KEY",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "SPACELOOM_GOOGLE_API_KEY",
        "SPACELOOM_ENABLE_OLLAMA",
        "SPACELOOM_OLLAMA_ENABLED",
        "SPACELOOM_PROVIDER_ALLOWLIST",
        "SPACELOOM_BUDGET_CAP_USD",
        "SPACELOOM_DEV_TRUST_HEADERS",
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


def _patch_router_available(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.src.api as api_module

    class FakeRouter:
        def has_available_provider(self) -> bool:
            return True

    monkeypatch.setattr(api_module, "build_router", lambda: FakeRouter())


def _patch_generate_draft(monkeypatch: pytest.MonkeyPatch, return_value: dict[str, Any]) -> None:
    import app.src.api as api_module
    import app.src.draft_engine as engine_module

    def fake_generate_draft(ctx: Any, conn: Any, **kwargs: Any) -> dict[str, Any]:
        return return_value

    monkeypatch.setattr(engine_module, "generate_draft", fake_generate_draft)
    monkeypatch.setattr(api_module, "generate_draft", fake_generate_draft)


def _sample_email_bytes() -> bytes:
    msg = email.message.EmailMessage()
    msg["Subject"] = "Cotización de telas"
    msg["From"] = "cliente@example.com"
    msg["To"] = "loom@example.com"
    msg.set_content("Necesito precio de Oxford y Lino.")
    return msg.as_bytes()


def _patch_imap(monkeypatch: pytest.MonkeyPatch, msg_bytes: bytes) -> None:
    import app.src.connectors.imap as imap_module

    class FakeIMAP:
        def __init__(self, server: str, port: int) -> None:
            self.server = server
            self.port = port

        def __enter__(self) -> "FakeIMAP":
            return self

        def __exit__(self, *args: Any) -> None:
            return None

        def login(self, username: str, password: str) -> None:
            # Password must flow through but never be exposed.
            assert password == "secret-not-logged"

        def select(self, mailbox: str) -> tuple[str, Any]:
            return "OK", None

        def uid(self, command: str, *args: Any) -> tuple[str, Any]:
            if command == "SEARCH":
                return "OK", [b"42"]
            if command == "FETCH":
                return "OK", [(b"42 (RFC822 {len})".replace(b"{len}", str(len(msg_bytes)).encode()), msg_bytes), b")"]
            return "NO", None

    monkeypatch.setattr(imap_module.imaplib, "IMAP4_SSL", FakeIMAP)


def _confirmation_token(resource_id: str) -> str:
    import hashlib

    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def _patch_smtp(monkeypatch: pytest.MonkeyPatch) -> type:
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

        def login(self, username: str, password: str) -> None:
            pass

        def send_message(self, msg: email.message.EmailMessage) -> None:
            self.calls.append(
                {
                    "server": self.server,
                    "port": self.port,
                    "from": msg["From"],
                    "to": msg["To"],
                    "subject": msg["Subject"],
                    "body": msg.get_payload(),
                }
            )

    FakeSMTP.calls = []
    monkeypatch.setattr(imap_module.smtplib, "SMTP_SSL", FakeSMTP)
    return FakeSMTP


def test_sync_creates_mail_message(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    msg_bytes = _sample_email_bytes()
    _patch_imap(monkeypatch, msg_bytes)

    workspace_id = _create_workspace(client, "Mail Workspace")
    response = client.post(f"/api/workspaces/{workspace_id}/mail/sync")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["created"] == 1

    response = client.get(f"/api/workspaces/{workspace_id}/mail")
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 1
    assert messages[0]["subject"] == "Cotización de telas"
    assert messages[0]["sender"] == "cliente@example.com"
    assert messages[0]["status"] == "unread"


def test_draft_generates_linked_draft(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    msg_bytes = _sample_email_bytes()
    _patch_imap(monkeypatch, msg_bytes)
    _patch_router_available(monkeypatch)
    _patch_generate_draft(
        monkeypatch,
        {
            "subject": "Re: Cotización",
            "body_md": "El precio de Oxford es USD 12.50 por metro.",
            "hard_facts": [],
            "sources": [],
            "blockers": [],
            "warnings": [],
            "requires_confirmation": False,
            "provider_slug": "fake",
            "model": "fake-model",
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.0,
            "duration_ms": 1,
        },
    )

    workspace_id = _create_workspace(client, "Draft Workspace")
    sync = client.post(f"/api/workspaces/{workspace_id}/mail/sync")
    mail_id = sync.json()["messages"][0]["id"]

    response = client.post(f"/api/workspaces/{workspace_id}/mail/{mail_id}/draft")
    assert response.status_code == 201, response.text
    draft = response.json()
    assert draft["status"] == "draft"
    assert draft["body_md"] == "El precio de Oxford es USD 12.50 por metro."

    response = client.get(f"/api/workspaces/{workspace_id}/mail")
    mail = response.json()[0]
    assert mail["draft_id"] == draft["id"]
    assert mail["status"] == "drafted"


def test_send_without_approval_returns_409(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    msg_bytes = _sample_email_bytes()
    _patch_imap(monkeypatch, msg_bytes)
    _patch_router_available(monkeypatch)
    _patch_generate_draft(
        monkeypatch,
        {
            "subject": "Re: Cotización",
            "body_md": "Precio base.",
            "hard_facts": [],
            "sources": [],
            "blockers": [],
            "warnings": [],
            "requires_confirmation": False,
            "provider_slug": "fake",
            "model": "fake-model",
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.0,
            "duration_ms": 1,
        },
    )

    workspace_id = _create_workspace(client, "Send Workspace")
    sync = client.post(f"/api/workspaces/{workspace_id}/mail/sync")
    mail_id = sync.json()["messages"][0]["id"]
    client.post(f"/api/workspaces/{workspace_id}/mail/{mail_id}/draft")

    response = client.post(
        f"/api/workspaces/{workspace_id}/mail/{mail_id}/send",
        params={
            "confirmation_token": _confirmation_token(mail_id),
            "idempotency_key": "send-key-1",
        },
    )
    assert response.status_code == 409
    assert "approved" in response.json()["detail"].lower()


def test_send_with_approval_calls_smtp(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    msg_bytes = _sample_email_bytes()
    _patch_imap(monkeypatch, msg_bytes)
    _patch_router_available(monkeypatch)
    FakeSMTP = _patch_smtp(monkeypatch)
    _patch_generate_draft(
        monkeypatch,
        {
            "subject": "Re: Cotización",
            "body_md": "El precio de Oxford es USD 12.50 por metro.",
            "hard_facts": [],
            "sources": [],
            "blockers": [],
            "warnings": [],
            "requires_confirmation": False,
            "provider_slug": "fake",
            "model": "fake-model",
            "input_tokens": 10,
            "output_tokens": 5,
            "cost_usd": 0.0,
            "duration_ms": 1,
        },
    )

    workspace_id = _create_workspace(client, "Approved Send Workspace")
    sync = client.post(f"/api/workspaces/{workspace_id}/mail/sync")
    mail_id = sync.json()["messages"][0]["id"]

    draft_response = client.post(f"/api/workspaces/{workspace_id}/mail/{mail_id}/draft")
    draft_id = draft_response.json()["id"]

    approve_response = client.post(
        f"/api/workspaces/{workspace_id}/drafts/{draft_id}/approve?confirmed=true"
    )
    assert approve_response.status_code == 200, approve_response.text

    send_response = client.post(
        f"/api/workspaces/{workspace_id}/mail/{mail_id}/send",
        params={
            "confirmation_token": _confirmation_token(mail_id),
            "idempotency_key": "send-key-1",
        },
    )
    assert send_response.status_code == 200, send_response.text
    mail = send_response.json()
    assert mail["status"] == "sent"

    assert len(FakeSMTP.calls) == 1
    assert FakeSMTP.calls[0]["to"] == "cliente@example.com"
    assert "USD 12.50" in FakeSMTP.calls[0]["body"]


def test_missing_credentials_returns_503(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "SPACELOOM_IMAP_SERVER",
        "SPACELOOM_IMAP_PORT",
        "SPACELOOM_IMAP_USER",
        "SPACELOOM_IMAP_PASSWORD",
    ):
        monkeypatch.delenv(name, raising=False)

    workspace_id = _create_workspace(client, "No Creds Workspace")
    response = client.post(f"/api/workspaces/{workspace_id}/mail/sync")
    assert response.status_code == 503
    assert "IMAP credentials" in response.json()["detail"]


def test_workspace_isolation(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    msg_bytes = _sample_email_bytes()
    _patch_imap(monkeypatch, msg_bytes)

    ws_a = _create_workspace(client, "Mail A")
    ws_b = _create_workspace(client, "Mail B")

    sync_a = client.post(f"/api/workspaces/{ws_a}/mail/sync")
    mail_id = sync_a.json()["messages"][0]["id"]

    response_b_list = client.get(f"/api/workspaces/{ws_b}/mail")
    assert response_b_list.status_code == 200
    assert response_b_list.json() == []

    response_b_draft = client.post(f"/api/workspaces/{ws_b}/mail/{mail_id}/draft")
    assert response_b_draft.status_code == 404

    response_b_send = client.post(
        f"/api/workspaces/{ws_b}/mail/{mail_id}/send",
        params={
            "confirmation_token": _confirmation_token(mail_id),
            "idempotency_key": "send-key-2",
        },
    )
    assert response_b_send.status_code == 404
