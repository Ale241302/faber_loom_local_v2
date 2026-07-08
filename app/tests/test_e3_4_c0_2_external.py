"""E3-4 Wave 0: C0-2 live external lookup, fail-closed."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    from app.src.audit import audit_writer
    from app.src.main import create_app

    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def test_external_lookup_fails_closed_without_fetcher(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import external_lookup

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    with db_session() as conn:
        result = external_lookup(
            ctx,
            conn,
            skill_id="SKILL_FE_STATUS_CHECK",
            query="estado comprobante 001",
            required_sources=["atv"],
            fetcher=None,
        )

    assert result["status"] == "failed"
    assert result["error"] == "external_lookup_unavailable"
    assert result["evidence"] == []


def test_external_lookup_stores_evidence_and_attaches(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import attach_evidence, external_lookup

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    def fake_fetcher(query: str, sources: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "source_type": "web_fetch",
                "source_locator": "https://atv.hacienda.go.cr/estado?clave=001",
                "captured_at": "2026-07-07T12:00:00Z",
                "content_text": "Estado: aceptado",
            }
        ]

    with db_session() as conn:
        result = external_lookup(
            ctx,
            conn,
            skill_id="SKILL_FE_STATUS_CHECK",
            query="estado comprobante 001",
            required_sources=["atv"],
            fetcher=fake_fetcher,
        )
        assert result["status"] == "succeeded"
        assert len(result["evidence"]) == 1

        evidence_ids = attach_evidence(
            ctx,
            conn,
            entity_type="routine_run",
            entity_id="run_test_001",
            evidence_items=result["evidence"],
        )

    assert len(evidence_ids) == 1

    with db_session() as conn:
        row = conn.execute(
            "SELECT * FROM external_evidence WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (evidence_ids[0], workspace_id, "default"),
        ).fetchone()
        assert row is not None
        assert row["entity_type"] == "routine_run"
        assert row["source_type"] == "web_fetch"


class _FakeResp:
    status = 200

    def __init__(self, body: bytes) -> None:
        self._body = body

    def __enter__(self) -> "_FakeResp":
        return self

    def __exit__(self, *args: Any) -> bool:
        return False

    def read(self, n: int | None = None) -> bytes:
        return self._body

    def getcode(self) -> int:
        return 200


def test_http_evidence_fetcher_builds_evidence_bundle(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.request

    from app.src.skill_primitives import http_evidence_fetcher

    monkeypatch.setattr(
        urllib.request, "urlopen", lambda req, timeout=10.0: _FakeResp(b"Estado: aceptado")
    )

    evidence = http_evidence_fetcher(
        "estado comprobante 001",
        ["https://atv.hacienda.go.cr/estado?clave=001"],
    )

    assert len(evidence) == 1
    item = evidence[0]
    assert item["source_type"] == "web"
    assert item["source_locator"].startswith("https://")
    assert item["captured_at"]
    assert item["content_hash"]
    assert "aceptado" in item["content_text"]


def test_http_evidence_fetcher_rejects_non_http_scheme() -> None:
    from app.src.skill_primitives import http_evidence_fetcher

    with pytest.raises(RuntimeError, match="unsupported_source_scheme"):
        http_evidence_fetcher("q", ["file:///etc/passwd"])


def test_http_evidence_fetcher_fails_closed_when_source_unreachable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import urllib.error
    import urllib.request

    from app.src.skill_primitives import http_evidence_fetcher

    def _boom(req: Any, timeout: float = 10.0) -> None:
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", _boom)

    with pytest.raises(RuntimeError, match="source_unreachable"):
        http_evidence_fetcher("q", ["https://atv.example/estado"])


def test_external_lookup_uses_real_http_fetcher(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """external_lookup wired to the real HTTP fetcher yields a stored evidence bundle."""
    import urllib.request

    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import external_lookup, http_evidence_fetcher

    monkeypatch.setattr(
        urllib.request, "urlopen", lambda req, timeout=10.0: _FakeResp(b"Estado: aceptado")
    )
    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    with db_session() as conn:
        result = external_lookup(
            ctx,
            conn,
            skill_id="SKILL_FE_STATUS_CHECK",
            query="estado comprobante 001",
            required_sources=["https://atv.hacienda.go.cr/estado?clave=001"],
            fetcher=http_evidence_fetcher,
        )

    assert result["status"] == "succeeded"
    assert result["evidence"][0]["source_type"] == "web"
    assert result["content_hash"]
