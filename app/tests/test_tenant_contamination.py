"""Adversarial tenant contamination tests for the SQLite monolith.

These tests verify that two tenants sharing the same user email cannot read or
mutate each other's workspaces, SMTP config, mail outbox, or editorial history.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.src.context import Context
from app.src.db import (
    connect,
    create_mail_message,
    create_or_get_mail_outbox,
    get_mail_outbox,
    get_workspace_smtp_config,
    list_editorial_history,
    record_editorial_event,
    set_workspace_smtp_config,
)

USER_EMAIL = "shared@example.com"


@pytest.fixture()
def client(tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FABERLOOM_CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("FABERLOOM_SECRET_KEY", "test-secret")
    monkeypatch.setenv("FABERLOOM_DEV_TRUST_HEADERS", "true")

    # Avoid leaking external credentials or feature flags into the app under test.
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


def _headers(tenant_id: str, user_id: str = USER_EMAIL) -> dict[str, str]:
    return {
        "x-tenant-id": tenant_id,
        "x-user-id": user_id,
        "x-actor-id": user_id,
    }


def _create_workspace(client: TestClient, tenant_id: str, name: str, slug: str) -> dict:
    response = client.post(
        "/api/workspaces",
        headers=_headers(tenant_id),
        json={"name": name, "slug": slug},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_workspace_listing_is_isolated_by_tenant(client: TestClient) -> None:
    alpha = _create_workspace(client, "alpha", "Alpha", "alpha")
    beta = _create_workspace(client, "beta", "Beta", "beta")

    alpha_list = client.get("/api/workspaces", headers=_headers("alpha")).json()["workspaces"]
    alpha_ids = {w["id"] for w in alpha_list}
    assert alpha["id"] in alpha_ids
    assert beta["id"] not in alpha_ids

    # Direct workspace access is also tenant-scoped.
    assert client.get(f"/api/workspaces/{beta['id']}", headers=_headers("alpha")).status_code == 404


def test_smtp_config_is_isolated_by_tenant(client: TestClient) -> None:
    alpha = _create_workspace(client, "alpha", "Alpha", "alpha")
    config = {
        "host": "mail.alpha.test",
        "port": 465,
        "use_ssl": True,
        "username": "a@alpha.test",
        "password": "secret",
        "from_email": "a@alpha.test",
    }

    put_resp = client.put(
        f"/api/workspaces/{alpha['id']}/admin/smtp-config",
        headers=_headers("alpha"),
        json=config,
    )
    assert put_resp.status_code == 200, put_resp.text

    # Beta cannot reach alpha's workspace at all.
    assert (
        client.get(
            f"/api/workspaces/{alpha['id']}/admin/smtp-config",
            headers=_headers("beta"),
        ).status_code
        == 404
    )

    # Direct repository check: the same workspace_id with a beta tenant
    # cannot see the SMTP row.
    with connect() as conn:
        alpha_ctx = Context(workspace_id=alpha["id"], tenant_id="alpha", user_id=USER_EMAIL)
        beta_ctx = Context(workspace_id=alpha["id"], tenant_id="beta", user_id=USER_EMAIL)
        alpha_cfg = get_workspace_smtp_config(alpha_ctx, conn)
        assert alpha_cfg is not None
        assert alpha_cfg["host"] == config["host"]
        assert get_workspace_smtp_config(beta_ctx, conn) is None


def test_mail_outbox_is_isolated_by_tenant(client: TestClient) -> None:
    alpha = _create_workspace(client, "alpha", "Alpha", "alpha")

    with connect() as conn:
        alpha_ctx = Context(workspace_id=alpha["id"], tenant_id="alpha", user_id=USER_EMAIL)
        beta_ctx = Context(workspace_id=alpha["id"], tenant_id="beta", user_id=USER_EMAIL)

        mail = create_mail_message(
            alpha_ctx,
            conn,
            account="acc",
            mail_uid="1",
            subject="Subject",
            sender="s@alpha.test",
            body_text="body",
            raw_payload=None,
        )
        outbox = create_or_get_mail_outbox(
            alpha_ctx,
            conn,
            mail_id=mail["id"],
            idempotency_key="key1",
        )
        assert outbox is not None
        assert get_mail_outbox(beta_ctx, conn, mail["id"]) is None


def test_editorial_history_is_isolated_by_tenant(client: TestClient) -> None:
    alpha = _create_workspace(client, "alpha", "Alpha", "alpha")

    with connect() as conn:
        alpha_ctx = Context(workspace_id=alpha["id"], tenant_id="alpha", user_id=USER_EMAIL)
        beta_ctx = Context(workspace_id=alpha["id"], tenant_id="beta", user_id=USER_EMAIL)

        record_editorial_event(alpha_ctx, conn, "draft", "d1", "approved")
        assert list_editorial_history(beta_ctx, conn) == []
        assert len(list_editorial_history(alpha_ctx, conn)) == 1


def test_x_tenant_id_header_is_ignored_without_trust_headers(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("FABERLOOM_DEV_TRUST_HEADERS", raising=False)

    created = client.post(
        "/api/workspaces",
        headers={"x-tenant-id": "alpha"},
        json={"name": "Ignored", "slug": "ignored"},
    ).json()

    # Without FABERLOOM_DEV_TRUST_HEADERS the header is ignored, so both
    # requests resolve to the default tenant.
    default_list = client.get("/api/workspaces").json()["workspaces"]
    alpha_list = client.get("/api/workspaces", headers={"x-tenant-id": "alpha"}).json()["workspaces"]
    assert any(w["id"] == created["id"] for w in default_list)
    assert any(w["id"] == created["id"] for w in alpha_list)
