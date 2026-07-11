"""E3-3: WhatsApp Business Cloud API inbound webhook (C0-1)."""

from __future__ import annotations

import hashlib
import hmac
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


def _demo_workspace_id(client: TestClient, tenant_id: str = "default") -> str:
    response = client.get(
        "/api/workspaces",
        headers=_auth_headers("owner@example.test", tenant_id, "owner"),
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


def _register_number(
    ctx: Any,
    conn: Any,
    phone_number_id: str,
    workspace_id: str,
) -> None:
    from app.src.connectors.whatsapp_inbound import register_whatsapp_number

    register_whatsapp_number(ctx, conn, phone_number_id, workspace_id)


def _set_secrets(
    ctx: Any,
    phone_number_id: str,
    app_secret: str,
    verify_token: str,
) -> None:
    from app.src.connectors.whatsapp_inbound import set_whatsapp_secret

    set_whatsapp_secret(ctx, phone_number_id, "app_secret", app_secret)
    set_whatsapp_secret(ctx, phone_number_id, "verify_token", verify_token)


def _payload(phone_number_id: str, msg_type: str = "text", content: str = "hola") -> dict[str, Any]:
    msg: dict[str, Any] = {
        "from": "1234567890",
        "id": "wamid.testmsg",
        "timestamp": "1234567890",
        "type": msg_type,
    }
    if msg_type == "text":
        msg["text"] = {"body": content}
    elif msg_type == "audio":
        msg["audio"] = {"id": "mediaid", "mime_type": "audio/ogg", "url": "https://example.test/media"}

    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "business_account_id",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "1234567890",
                                "phone_number_id": phone_number_id,
                            },
                            "contacts": [{"profile": {"name": "Test"}, "wa_id": "1234567890"}],
                            "messages": [msg],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }


def _sign(body: bytes, app_secret: str) -> str:
    return "sha256=" + hmac.new(
        app_secret.encode("utf-8"), body, hashlib.sha256
    ).hexdigest()


def _setup_enabled(
    client: TestClient,
    tenant_id: str = "default",
) -> tuple[str, str, str]:
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id=tenant_id, user_id="local", actor_id="local")
    phone_number_id = f"phone_{tenant_id}"
    app_secret = f"app_secret_{tenant_id}"
    verify_token = f"verify_token_{tenant_id}"

    with db_session() as conn:
        _register_number(ctx, conn, phone_number_id, workspace_id)
        _set_tenant_setting(conn, tenant_id, "whatsapp_inbound.enabled", True)
        conn.commit()
        _set_secrets(ctx, phone_number_id, app_secret, verify_token)

    return workspace_id, phone_number_id, app_secret


def test_challenge_ok(client: TestClient) -> None:
    _, phone_number_id, _ = _setup_enabled(client)
    verify_token = "verify_token_default"

    response = client.get(
        "/api/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "CHALLENGE_CODE",
            "hub.verify_token": verify_token,
        },
    )
    assert response.status_code == 200, response.text
    assert response.text == "CHALLENGE_CODE"


def test_challenge_invalid_mode(client: TestClient) -> None:
    response = client.get(
        "/api/webhooks/whatsapp",
        params={
            "hub.mode": "invalid",
            "hub.challenge": "CHALLENGE_CODE",
            "hub.verify_token": "token",
        },
    )
    assert response.status_code == 400


def test_challenge_unknown_token(client: TestClient) -> None:
    response = client.get(
        "/api/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.challenge": "CHALLENGE_CODE",
            "hub.verify_token": "unknown-token",
        },
    )
    assert response.status_code == 404


def test_invalid_signature_rejected(client: TestClient) -> None:
    _, phone_number_id, _ = _setup_enabled(client)
    payload = _payload(phone_number_id)
    body = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/api/webhooks/whatsapp",
        content=body,
        headers={"X-Hub-Signature-256": "sha256=invalid"},
    )
    assert response.status_code == 401, response.text


def test_missing_signature_rejected(client: TestClient) -> None:
    _, phone_number_id, _ = _setup_enabled(client)
    payload = _payload(phone_number_id)
    body = json.dumps(payload).encode("utf-8")

    response = client.post("/api/webhooks/whatsapp", content=body)
    assert response.status_code == 401


def test_flag_off_returns_404(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")
    phone_number_id = "phone_off"
    app_secret = "app_secret_off"

    with db_session() as conn:
        _register_number(ctx, conn, phone_number_id, workspace_id)
        # leave whatsapp_inbound.enabled = False (default)
        conn.commit()
        _set_secrets(ctx, phone_number_id, app_secret, "verify_token_off")

    payload = _payload(phone_number_id)
    body = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/api/webhooks/whatsapp",
        content=body,
        headers={"X-Hub-Signature-256": _sign(body, app_secret)},
    )
    assert response.status_code == 404, response.text


def test_text_message_creates_pending_capture(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session

    workspace_id, phone_number_id, app_secret = _setup_enabled(client)
    payload = _payload(phone_number_id, msg_type="text", content="consulta de stock")
    body = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/api/webhooks/whatsapp",
        content=body,
        headers={"X-Hub-Signature-256": _sign(body, app_secret)},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "ok"
    assert data["processed"] == 1
    draft_id = data["results"][0]["draft_id"]

    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM draft WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (draft_id, workspace_id, "default"),
        ).fetchone()
        assert row is not None
        assert row["requires_confirmation"] == 1
        assert row["status"] == "draft"


def test_tenant_isolation(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session

    # Tenant A: registered and enabled (uses default workspace for the test)
    workspace_a, phone_a, secret_a = _setup_enabled(client, tenant_id="tenant_a")

    # Tenant B: tries to send a message using phone_a with its own secret.
    # The registered number resolves to tenant_a's app_secret (secret_a), so a
    # signature computed with tenant_b's secret must be rejected.
    ctx_b = Context(workspace_id=workspace_a, tenant_id="default", user_id="local", actor_id="local")
    secret_b = "app_secret_b"
    set_secret = pytest.importorskip("app.src.connectors.whatsapp_inbound").set_whatsapp_secret
    set_secret(ctx_b, phone_a, "app_secret", secret_b)

    payload = _payload(phone_a, msg_type="text", content="hello")
    body = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/api/webhooks/whatsapp",
        content=body,
        headers={"X-Hub-Signature-256": _sign(body, secret_b)},
    )
    assert response.status_code == 401, response.text
