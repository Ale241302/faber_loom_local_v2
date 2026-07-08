"""E3-3 — The key broker mediates the agent's KB content read (P0-5).

The draft engine's evidence pack is the single seam where the agent reads
sealed content. These tests prove the broker gates it: CONTENT (default) exposes
excerpts and facts, INDEX exposes only source titles/pointers, CLOSED exposes
nothing — and the agent never holds the key.
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from typing import Any

import pytest

import app.src.draft_engine as draft_engine
from app.src.context import Context
from app.src.key_broker import KeyLevel, set_policy


@pytest.fixture()
def conn():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.sqlite3"
        c = sqlite3.connect(str(path))
        c.row_factory = sqlite3.Row
        c.executescript(
            """
            CREATE TABLE key_policy (
                tenant_id TEXT NOT NULL,
                space_id TEXT NOT NULL,
                level TEXT NOT NULL,
                approver_roles_json TEXT NOT NULL DEFAULT '[]',
                ceo_only INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT '',
                updated_by TEXT,
                PRIMARY KEY (tenant_id, space_id)
            );
            """
        )
        yield c
        c.close()


@pytest.fixture()
def canned_kb(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the KB reads so _build_evidence_pack has deterministic content."""

    monkeypatch.setattr(
        draft_engine,
        "search_kb_chunks",
        lambda ctx, conn, q, limit=5: [
            {
                "source_id": "s1",
                "content_text": "El precio de Oxford es USD 12.50 por metro.",
                "source_locator": "row-1",
                "source_version": "v1",
            }
        ],
    )
    monkeypatch.setattr(draft_engine, "search_kb_facts", lambda ctx, conn, term, limit=10: [])
    monkeypatch.setattr(
        draft_engine,
        "get_kb_source",
        lambda ctx, conn, source_id: {
            "title": "Lista de Precios",
            "type": "md",
            "source_version": "v1",
            "created_at": "2026-07-07T00:00:00Z",
        },
    )
    monkeypatch.setattr(draft_engine, "get_kb_facts_by_source", lambda ctx, conn, source_id: [])


def _ctx() -> Context:
    return Context(workspace_id="ws1", tenant_id="tenant-a", user_id="u1", actor_role_at_decision="am")


def test_default_open_exposes_content(conn: sqlite3.Connection, canned_kb: None) -> None:
    pack = draft_engine._build_evidence_pack(_ctx(), conn, "precio oxford")
    assert len(pack) == 1
    assert "USD 12.50" in pack[0]["excerpt"]


def test_closed_space_yields_no_evidence(conn: sqlite3.Connection, canned_kb: None) -> None:
    set_policy(conn, "tenant-a", "ws1", KeyLevel.CLOSED)
    pack = draft_engine._build_evidence_pack(_ctx(), conn, "precio oxford")
    assert pack == []


def test_index_space_exposes_titles_not_content(conn: sqlite3.Connection, canned_kb: None) -> None:
    set_policy(conn, "tenant-a", "ws1", KeyLevel.INDEX)
    pack = draft_engine._build_evidence_pack(_ctx(), conn, "precio oxford")
    assert len(pack) == 1
    # Knows WHERE (the source exists) but not the sealed content.
    assert pack[0]["title"] == "Lista de Precios"
    assert pack[0]["excerpt"] == ""
    assert pack[0]["facts"] == []
