"""E2-2: shared-instance mail connector hardening.

Covers:
- FABERLOOM_SHARED_INSTANCE flag exposed in /api/features
- No legacy/global env fallback for IMAP/SMTP in shared mode
- Per-user app-password enforcement
- IMAP credential rotation endpoint + audit
- Cross-user rotation forbidden
"""

from __future__ import annotations

import email.message
import hashlib
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
    monkeypatch.setenv("FABERLOOM_SHARED_INSTANCE", "true")

    # Legacy env credentials are present but must be ignored in shared mode.
    monkeypatch.setenv("FABERLOOM_IMAP_SERVER", "imap.example.com")
    monkeypatch.setenv("FABERLOOM_IMAP_PORT", "993")
    monkeypatch.setenv("FABERLOOM_IMAP_USER", "loom@example.com")
    monkeypatch.setenv("FABERLOOM_IMAP_PASSWORD", "legacy-secret")
    monkeypatch.setenv("FABERLOOM_SMTP_SERVER", "smtp.example.com")
    monkeypatch.setenv("FABERLOOM_SMTP_PORT", "465")

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

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _sample_email_bytes() -> bytes:
    msg = email.message.EmailMessage()
    msg["Subject"] = "Cotización de telas"
    msg["From"] = "cliente@example.com"
    msg["To"] = "loom@example.com"
    msg.set_content("Necesito precio de Oxford y Lino.")
    return msg.as_bytes()


def _patch_imap(monkeypatch: pytest.MonkeyPatch, expected_password: str, msg_bytes: bytes) -> None:
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
            assert password == expected_password, "Unexpected IMAP password"

        def select(self, mailbox: str) -> tuple[str, Any]:
            return "OK", None

        def uid(self, command: str, *args: Any) -> tuple[str, Any]:
            if command == "SEARCH":
                return "OK", [b"42"]
            if command == "FETCH":
                return "OK", [(b"42 (RFC822 {len})".replace(b"{len}", str(len(msg_bytes)).encode()), msg_bytes), b")"]
            return "NO", None

    monkeypatch.setattr(imap_module.imaplib, "IMAP4_SSL", FakeIMAP)


def _patch_router_available(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.src.api as api_module

    class FakeRouter:
        def has_available_provider(self) -> bool:
            return True

    monkeypatch.setattr(api_module, "build_router", lambda user_id=None: FakeRouter())


def _patch_generate_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    import app.src.api as api_module
    import app.src.draft_engine as engine_module

    def fake_generate_draft(ctx: Any, conn: Any, **kwargs: Any) -> dict[str, Any]:
        return {
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
        }

    monkeypatch.setattr(engine_module, "generate_draft", fake_generate_draft)
    monkeypatch.setattr(api_module, "generate_draft", fake_generate_draft)


def _confirmation_token(resource_id: str) -> str:
    return hashlib.sha256(resource_id.encode("utf-8")).hexdigest()[:16]


def _sample_smtp_config(is_app_password: int = 1) -> dict[str, Any]:
    return {
        "host": "mail.example.com",
        "port": 465,
        "use_ssl": True,
        "username": "info@example.com",
        "password": "example-app-password",
        "from_email": "info@example.com",
        "is_app_password": is_app_password,
    }


def _sample_imap_config(password: str = "app-password-123", is_app_password: int = 1) -> dict[str, Any]:
    return {
        "label": "Cuenta AM",
        "provider": "imap",
        "host": "imap.example.com",
        "port": 993,
        "username": "am@example.com",
        "password": password,
        "folders_json": '["INBOX"]',
        "auth_type": "password",
        "read_only": 1,
        "is_default": 1,
        "is_app_password": is_app_password,
    }


def test_features_endpoint_exposes_shared_instance(client: TestClient) -> None:
    response = client.get("/api/features")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["email_connector_enabled"] is True
    assert data["shared_instance"] is True


def test_shared_instance_sync_rejects_env_fallback(client: TestClient) -> None:
    workspace_id = _create_workspace(client, "Shared Sync No Config")
    response = client.post(f"/api/workspaces/{workspace_id}/mail/sync")
    assert response.status_code == 503
    assert "app-password" in response.json()["detail"].lower() or "configured" in response.json()["detail"].lower()


def test_shared_instance_requires_app_password_for_imap(client: TestClient) -> None:
    workspace_id = _create_workspace(client, "Shared IMAP App Password")
    payload = _sample_imap_config(is_app_password=0)
    response = client.post(f"/api/workspaces/{workspace_id}/admin/imap-config", json=payload)
    assert response.status_code == 422
    assert "app-password" in response.json()["detail"].lower()


def test_shared_instance_requires_app_password_for_smtp(client: TestClient) -> None:
    workspace_id = _create_workspace(client, "Shared SMTP App Password")
    payload = _sample_smtp_config(is_app_password=0)
    response = client.put(f"/api/workspaces/{workspace_id}/admin/smtp-config", json=payload)
    assert response.status_code == 422
    assert "app-password" in response.json()["detail"].lower()


def test_sync_uses_user_default_account_in_shared_instance(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    msg_bytes = _sample_email_bytes()
    _patch_imap(monkeypatch, "app-password-123", msg_bytes)

    workspace_id = _create_workspace(client, "Shared Sync With Account")
    create = client.post(f"/api/workspaces/{workspace_id}/admin/imap-config", json=_sample_imap_config())
    assert create.status_code == 201, create.text

    response = client.post(f"/api/workspaces/{workspace_id}/mail/sync")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["created"] == 1

    messages = client.get(f"/api/workspaces/{workspace_id}/mail").json()
    assert len(messages) == 1
    assert messages[0]["account_id"] == create.json()["id"]


def test_shared_instance_send_rejects_env_smtp_fallback(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    msg_bytes = _sample_email_bytes()
    _patch_imap(monkeypatch, "app-password-123", msg_bytes)
    _patch_router_available(monkeypatch)
    _patch_generate_draft(monkeypatch)

    workspace_id = _create_workspace(client, "Shared Send No SMTP")
    client.post(f"/api/workspaces/{workspace_id}/admin/imap-config", json=_sample_imap_config())

    sync = client.post(f"/api/workspaces/{workspace_id}/mail/sync")
    mail_id = sync.json()["messages"][0]["id"]

    draft_response = client.post(f"/api/workspaces/{workspace_id}/mail/{mail_id}/draft")
    draft_id = draft_response.json()["id"]

    approve = client.post(
        f"/api/workspaces/{workspace_id}/drafts/{draft_id}/approve?confirmed=true"
    )
    assert approve.status_code == 200, approve.text

    send = client.post(
        f"/api/workspaces/{workspace_id}/mail/{mail_id}/send",
        params={"confirmation_token": _confirmation_token(mail_id), "idempotency_key": "key-1"},
    )
    assert send.status_code == 503
    assert "smtp" in send.json()["detail"].lower()


def test_rotate_imap_credentials(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    msg_bytes = _sample_email_bytes()
    _patch_imap(monkeypatch, "new-password-456", msg_bytes)

    workspace_id = _create_workspace(client, "Rotate IMAP")
    create = client.post(f"/api/workspaces/{workspace_id}/admin/imap-config", json=_sample_imap_config())
    assert create.status_code == 201
    account_id = create.json()["id"]

    rotate = client.post(
        f"/api/workspaces/{workspace_id}/admin/imap-config/{account_id}/rotate",
        json={"password": "new-password-456"},
    )
    assert rotate.status_code == 200, rotate.text
    rotated = rotate.json()
    assert rotated["has_password"] is True
    assert rotated["rotated_at"] is not None

    # Verify the new password is actually used by sync.
    sync = client.post(f"/api/workspaces/{workspace_id}/mail/sync")
    assert sync.status_code == 200
    assert sync.json()["created"] == 1


def test_rotate_forbidden_for_other_user_account(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret")
    monkeypatch.setenv("FABERLOOM_USERS", '{"a@mwt.one":"secret","b@mwt.one":"secret"}')

    login_a = client.post("/api/auth/login", json={"email": "a@mwt.one", "password": "secret"})
    assert login_a.status_code == 200

    workspace_id = _create_workspace(client, "Rotate Cross User")

    create = client.post(f"/api/workspaces/{workspace_id}/admin/imap-config", json=_sample_imap_config())
    assert create.status_code == 201
    account_id = create.json()["id"]

    login_b = client.post("/api/auth/login", json={"email": "b@mwt.one", "password": "secret"})
    assert login_b.status_code == 200

    rotate = client.post(
        f"/api/workspaces/{workspace_id}/admin/imap-config/{account_id}/rotate",
        json={"password": "hijack"},
    )
    assert rotate.status_code == 403
