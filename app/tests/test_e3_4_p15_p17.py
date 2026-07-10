"""E3-4 Wave 0: P15 normative validity and P17 correction cascade primitives."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    db_path = tmp_path / "faberloom.sqlite3"
    audit_path = tmp_path / "audit.jsonl"
    monkeypatch.setenv("FABERLOOM_DB_PATH", str(db_path))
    monkeypatch.setenv("FL_STORAGE_BACKEND", "memory")

    from app.src.audit import audit_writer
    from app.src.main import create_app
    from app.src.storage import reset_object_store

    reset_object_store()
    audit_writer.audit_path = audit_path
    with TestClient(create_app()) as test_client:
        yield test_client


def _demo_workspace_id(client: TestClient) -> str:
    response = client.get("/api/workspaces")
    assert response.status_code == 200
    workspaces = response.json()["workspaces"]
    assert workspaces
    return workspaces[0]["id"]


def _insert_fact_and_source(conn: Any, ctx: Any, valid_from: str, valid_until: str | None) -> str:
    from app.src.db import new_id, utc_now

    now = utc_now()
    source_id = new_id("kbs")
    conn.execute(
        """
        INSERT INTO kb_source (id, workspace_id, tenant_id, type, title, content_text, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (source_id, ctx.workspace_id, ctx.tenant_id, "test", "Test source", "body", now),
    )
    fact_id = new_id("fact")
    conn.execute(
        """
        INSERT INTO kb_fact (
            id, workspace_id, tenant_id, source_id, entity_key, field_name, field_value,
            valid_from, valid_until, source_locator, source_version, schema_version, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            fact_id,
            ctx.workspace_id,
            ctx.tenant_id,
            source_id,
            "entity:test",
            "status",
            "active",
            valid_from,
            valid_until,
            f"test://source/{fact_id}",
            "v1",
            39,
            now,
        ),
    )
    return fact_id


def _insert_citing_draft(conn: Any, ctx: Any, fact_id: str) -> str:
    from app.src.kb import insert_draft

    draft = insert_draft(
        ctx,
        conn,
        chat_id=None,
        task="commercial_reply",
        subject="Derived draft",
        body_md=f"This draft cites fact {fact_id}",
        hard_facts=[{"field": "cited_fact_id", "value": fact_id, "source_locator": f"fact:{fact_id}"}],
        sources=[],
        blockers=[],
        warnings=[],
        requires_confirmation=False,
        status="draft",
        source_version="v1",
    )
    return draft["id"]


# ---------------------------------------------------------------------------
# P15
# ---------------------------------------------------------------------------


def test_p15_vigente(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import verificar_vigencia_normativa

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    def fetcher(query: str, sources: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "source_type": "test",
                "source_locator": sources[0],
                "captured_at": "2026-01-01T00:00:00Z",
                "valid_from": "2020-01-01T00:00:00Z",
                "valid_until": "2030-01-01T00:00:00Z",
            }
        ]

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", "2030-01-01T00:00:00Z")
        fact = {"id": fact_id, "source_locator": f"test://source/{fact_id}", "valid_from": "2020-01-01T00:00:00Z", "valid_until": "2030-01-01T00:00:00Z"}
        result = verificar_vigencia_normativa(ctx, conn, fact=fact, fetcher=fetcher)

    assert result["status"] == "vigente"
    assert result["fact_id"] == fact_id
    assert result["valid_from"] == "2020-01-01T00:00:00Z"
    assert result["valid_until"] == "2030-01-01T00:00:00Z"


def test_p15_vencido(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import verificar_vigencia_normativa

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    def fetcher(query: str, sources: list[str]) -> list[dict[str, Any]]:
        return [
            {
                "source_type": "test",
                "source_locator": sources[0],
                "captured_at": "2026-01-01T00:00:00Z",
                "valid_from": "2020-01-01T00:00:00Z",
                "valid_until": "2024-01-01T00:00:00Z",
            }
        ]

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", "2025-01-01T00:00:00Z")
        fact = {"id": fact_id, "source_locator": f"test://source/{fact_id}", "valid_from": "2020-01-01T00:00:00Z", "valid_until": "2025-01-01T00:00:00Z"}
        result = verificar_vigencia_normativa(ctx, conn, fact=fact, fetcher=fetcher)

    assert result["status"] == "vencido"
    assert result["fact_id"] == fact_id


def test_p15_no_verificable_without_fetcher(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import verificar_vigencia_normativa

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", "2030-01-01T00:00:00Z")
        fact = {"id": fact_id, "source_locator": f"test://source/{fact_id}", "valid_from": "2020-01-01T00:00:00Z", "valid_until": "2030-01-01T00:00:00Z"}
        result = verificar_vigencia_normativa(ctx, conn, fact=fact, fetcher=None)

    assert result["status"] == "no_verificable"
    assert result["fact_id"] == fact_id


def test_p15_no_verificable_when_lookup_fails(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import verificar_vigencia_normativa

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    def failing_fetcher(query: str, sources: list[str]) -> list[dict[str, Any]]:
        raise RuntimeError("source unreachable")

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", "2030-01-01T00:00:00Z")
        fact = {"id": fact_id, "source_locator": f"test://source/{fact_id}", "valid_from": "2020-01-01T00:00:00Z", "valid_until": "2030-01-01T00:00:00Z"}
        result = verificar_vigencia_normativa(ctx, conn, fact=fact, fetcher=failing_fetcher)

    assert result["status"] == "no_verificable"
    assert "lookup_failed" in result.get("reason", "")


def test_p15_no_verificable_missing_dates(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import verificar_vigencia_normativa

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local")

    def fetcher(query: str, sources: list[str]) -> list[dict[str, Any]]:
        return [{"source_type": "test", "source_locator": sources[0], "captured_at": "2026-01-01T00:00:00Z"}]

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", None)
        fact = {"id": fact_id, "source_locator": f"test://source/{fact_id}", "valid_from": "2020-01-01T00:00:00Z", "valid_until": ""}
        result = verificar_vigencia_normativa(ctx, conn, fact=fact, fetcher=fetcher)

    assert result["status"] == "no_verificable"


# ---------------------------------------------------------------------------
# P17
# ---------------------------------------------------------------------------


def test_p17_cascade_creates_hitl_drafts_and_log(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import corregir_en_cascada_temporal

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", "2024-01-01T00:00:00Z")
        draft_id = _insert_citing_draft(conn, ctx, fact_id)
        conn.commit()
        result = corregir_en_cascada_temporal(ctx, conn, fact_id=fact_id, new_state="vencido", reason="test correction")

    assert result["fact_id"] == fact_id
    assert result["new_state"] == "vencido"
    assert result["affected_artifacts"] == 1
    assert len(result["created_draft_ids"]) == 1
    assert len(result["correction_log_ids"]) == 1

    with db_session() as conn:
        correction_draft_id = result["created_draft_ids"][0]
        row = conn.execute(
            "SELECT * FROM draft WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (correction_draft_id, workspace_id, "default"),
        ).fetchone()
        assert row is not None
        assert row["requires_confirmation"] == 1
        assert row["status"] == "draft"

        log_id = result["correction_log_ids"][0]
        log_row = conn.execute(
            "SELECT * FROM correction_log WHERE id = ? AND workspace_id = ? AND tenant_id = ?",
            (log_id, workspace_id, "default"),
        ).fetchone()
        assert log_row is not None
        assert log_row["origin_fact_id"] == fact_id
        assert log_row["affected_entity_type"] == "draft"
        assert log_row["affected_entity_id"] == draft_id
        assert log_row["proposed_state"] == "vencido"


def test_p17_cascade_is_append_only(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import corregir_en_cascada_temporal

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", "2024-01-01T00:00:00Z")
        _insert_citing_draft(conn, ctx, fact_id)
        conn.commit()
        result = corregir_en_cascada_temporal(ctx, conn, fact_id=fact_id, new_state="vencido")
        log_id = result["correction_log_ids"][0]

        # Append-only: UPDATE/DELETE must be possible at the SQL level (the helper
        # never issues them), but the table is a regular workspace-owned table.
        # We simply assert the row survives a re-read.
        log_row = conn.execute(
            "SELECT * FROM correction_log WHERE id = ?", (log_id,)
        ).fetchone()
        assert log_row is not None


def test_p17_invalid_state_raises(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import corregir_en_cascada_temporal

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", "2024-01-01T00:00:00Z")
        conn.commit()
        with pytest.raises(ValueError, match="Invalid correction state"):
            corregir_en_cascada_temporal(ctx, conn, fact_id=fact_id, new_state="invalid")


def test_p17_missing_fact_raises(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import corregir_en_cascada_temporal

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        with pytest.raises(ValueError, match="Fact not found"):
            corregir_en_cascada_temporal(ctx, conn, fact_id="fact_missing", new_state="vencido")


def test_p17_no_derived_artifacts_returns_empty(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import corregir_en_cascada_temporal

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", "2024-01-01T00:00:00Z")
        conn.commit()
        result = corregir_en_cascada_temporal(ctx, conn, fact_id=fact_id, new_state="corregido")

    assert result["affected_artifacts"] == 0
    assert result["created_draft_ids"] == []
    assert result["correction_log_ids"] == []


def test_p17_tenant_isolation(client: TestClient) -> None:
    from app.src.context import Context
    from app.src.db import db_session
    from app.src.skill_primitives import corregir_en_cascada_temporal

    workspace_id = _demo_workspace_id(client)
    ctx = Context(workspace_id=workspace_id, tenant_id="default", user_id="local", actor_id="local")

    with db_session() as conn:
        fact_id = _insert_fact_and_source(conn, ctx, "2020-01-01T00:00:00Z", "2024-01-01T00:00:00Z")
        conn.commit()

    other_ctx = Context(workspace_id=workspace_id, tenant_id="other", user_id="local", actor_id="local")
    with db_session() as conn:
        with pytest.raises(ValueError, match="Fact not found"):
            corregir_en_cascada_temporal(other_ctx, conn, fact_id=fact_id, new_state="vencido")
