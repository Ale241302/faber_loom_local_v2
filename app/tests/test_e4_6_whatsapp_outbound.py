"""E4-6 — WhatsApp Cloud API outbound connector (draft-first / HITL)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.src.auth import create_access_token


USER_EMAIL = "owner@whatsapp.test"


@pytest.fixture()
def client(tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret-key-with-enough-bytes-32")
    monkeypatch.setenv("FABERLOOM_USERS", '{"admin@platform.test":"secret"}')
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
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _headers(tenant_id: str, role: str = "owner") -> dict[str, str]:
    token = create_access_token(USER_EMAIL, tenant_id=tenant_id, user_id=USER_EMAIL, role=role)
    return {"Authorization": f"Bearer {token}"}


def _configure(client: TestClient, tenant_id: str, phone: str) -> None:
    r = client.put(
        f"/api/tenants/{tenant_id}/connectors/whatsapp/{phone}",
        headers=_headers(tenant_id),
        json={"access_token": "test-token", "business_account_id": "biz-123"},
    )
    assert r.status_code == 200, r.text


def test_no_send_without_confirmation_token(client: TestClient) -> None:
    """A message send without token returns the required HITL token."""

    _configure(client, "alpha", "123456789")
    r = client.post(
        "/api/tenants/alpha/whatsapp/123456789/send",
        headers=_headers("alpha"),
        json={"to": "5491112345678", "body": "Hola", "last_customer_message_at": "2026-07-11T08:00:00+00:00"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["dry_run"] is True
    assert "confirmation_token" in data


def test_fail_closed_without_secrets(client: TestClient) -> None:
    """Sending without configured secrets returns 503."""

    r = client.post(
        "/api/tenants/beta/whatsapp/987654321/send",
        headers=_headers("beta"),
        json={"to": "5491112345678", "body": "Hola"},
    )
    assert r.status_code == 503, r.text


def test_outside_24h_requires_template(client: TestClient) -> None:
    """Free-form text outside the 24h window is rejected."""

    _configure(client, "gamma", "111222333")
    r = client.post(
        "/api/tenants/gamma/whatsapp/111222333/send",
        headers=_headers("gamma"),
        json={
            "to": "5491112345678",
            "body": "Hola",
            "last_customer_message_at": "2026-01-01T00:00:00+00:00",
        },
    )
    assert r.status_code == 409, r.text
    assert "24h" in r.json()["detail"]


def test_template_returns_confirmation_token(client: TestClient) -> None:
    """Template send without token returns a HITL token."""

    _configure(client, "delta", "444555666")
    r = client.post(
        "/api/tenants/delta/whatsapp/444555666/send-template",
        headers=_headers("delta"),
        json={"to": "5491112345678", "template_name": "hello_world", "language_code": "en_US"},
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["dry_run"] is True
    assert "confirmation_token" in data


def test_secrets_are_isolated_between_tenants(client: TestClient) -> None:
    """Tenant A secrets are not usable by tenant B."""

    _configure(client, "alpha", "123456789")
    r = client.post(
        "/api/tenants/beta/whatsapp/123456789/send",
        headers=_headers("beta"),
        json={"to": "5491112345678", "body": "Hola"},
    )
    assert r.status_code == 503, r.text
