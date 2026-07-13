"""E5-fix: tests de administración de workspaces (rename/delete) y guardas."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
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
        "FABERLOOM_AUTO_MODE_ENABLED",
    ):
        monkeypatch.delenv(name, raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def test_create_rename_delete_empty_workspace(client: TestClient) -> None:
    created = client.post("/api/workspaces", json={"name": "Temp E5FIX"})
    assert created.status_code == 201, created.text
    ws = created.json()

    renamed = client.patch(f"/api/workspaces/{ws['id']}", json={"name": "Temp E5FIX renombrado"})
    assert renamed.status_code == 200, renamed.text
    assert renamed.json()["name"] == "Temp E5FIX renombrado"
    assert renamed.json()["slug"] == ws["slug"]  # el slug es estable

    wrong = client.delete(f"/api/workspaces/{ws['id']}", params={"confirm_slug": "no-es"})
    assert wrong.status_code == 422

    deleted = client.delete(f"/api/workspaces/{ws['id']}", params={"confirm_slug": ws["slug"]})
    assert deleted.status_code == 204

    listing = client.get("/api/workspaces").json()["workspaces"]
    assert all(item["id"] != ws["id"] for item in listing)


def test_rename_rejects_empty_name(client: TestClient) -> None:
    created = client.post("/api/workspaces", json={"name": "Temp E5FIX 2"}).json()
    bad = client.patch(f"/api/workspaces/{created['id']}", json={"name": "   "})
    assert bad.status_code == 422


def test_general_workspace_cannot_be_deleted(client: TestClient) -> None:
    general = client.get("/api/workspaces/general")
    assert general.status_code == 200, general.text
    ws = general.json()
    resp = client.delete(f"/api/workspaces/{ws['id']}", params={"confirm_slug": ws["slug"]})
    assert resp.status_code == 409


def test_non_empty_workspace_delete_conflict(client: TestClient) -> None:
    # El demo workspace trae KB seedeada: debe rechazarse con 409.
    listing = client.get("/api/workspaces").json()["workspaces"]
    demo = next((w for w in listing if w["slug"] == "mwt-demo"), None)
    assert demo is not None
    resp = client.delete(f"/api/workspaces/{demo['id']}", params={"confirm_slug": demo["slug"]})
    assert resp.status_code == 409


def test_general_chat_auto_no_longer_unsupported(client: TestClient) -> None:
    general = client.get("/api/workspaces/general").json()
    chat = client.post(f"/api/workspaces/{general['id']}/chats", json={"title": "auto test"})
    assert chat.status_code == 201, chat.text
    chat_id = chat.json()["id"]
    resp = client.post(
        f"/api/workspaces/{general['id']}/chats/{chat_id}/completions",
        json={"message": "hola", "mode": "auto"},
    )
    # Puede fallar por falta de providers/modo manual (4xx), pero NUNCA con el
    # viejo "Auto mode is not supported in the general chat".
    if resp.status_code != 200:
        assert "not supported in the general chat" not in (resp.json().get("detail") or "")
