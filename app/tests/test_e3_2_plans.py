"""E3-2 — Plan limit enforcement."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest

from app.src.context import Context
from app.src.plans import PlanError, check_plan_limit, enforce_all_limits, get_plan


@pytest.fixture()
def conn():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.sqlite3"
        conn = sqlite3.connect(str(path))
        conn.row_factory = sqlite3.Row
        conn.executescript(
            """
            CREATE TABLE workspace (
                id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL
            );
            CREATE TABLE fnd_users (
                id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, status TEXT
            );
            """
        )
        yield conn
        conn.close()


def test_get_plan_known() -> None:
    plan = get_plan("starter")
    assert plan.max_users == 5


def test_get_plan_unknown_raises() -> None:
    with pytest.raises(PlanError):
        get_plan("nonexistent")


def test_check_within_limit(conn: sqlite3.Connection) -> None:
    check_plan_limit(conn, "tenant-a", "starter", "users", 1)


def test_check_exceeds_limit(conn: sqlite3.Connection) -> None:
    # starter allows 5 users; requesting 6 should fail.
    with pytest.raises(PlanError, match="limit exceeded"):
        check_plan_limit(conn, "tenant-a", "starter", "users", 6)


def test_unlimited_plan_allows_anything(conn: sqlite3.Connection) -> None:
    check_plan_limit(conn, "tenant-a", "enterprise", "users", 1_000_000)


def test_enforce_all_limits_passes(conn: sqlite3.Connection) -> None:
    enforce_all_limits(conn, "tenant-a", "starter", {"users": 1, "workspaces": 1})


def test_enforce_all_limits_fails_on_first_violation(conn: sqlite3.Connection) -> None:
    with pytest.raises(PlanError):
        enforce_all_limits(conn, "tenant-a", "starter", {"users": 10, "workspaces": 1})


def test_workspace_count_is_considered(conn: sqlite3.Connection) -> None:
    conn.execute("INSERT INTO workspace VALUES ('ws-1', 'tenant-b')")
    conn.commit()
    with pytest.raises(PlanError):
        # starter allows 2 workspaces; 1 used + 2 requested = 3.
        check_plan_limit(conn, "tenant-b", "starter", "workspaces", 2)
