"""E3-2 — Generalized N-tenant RLS canary (no Postgres server required).

Exercises the pure logic of the all-tenants isolation checker against a fake
DB-API connection, so the generalization beyond the canary/default pair is
covered even when no Postgres is available locally.
"""

from __future__ import annotations

from typing import Any

from app.scripts.check_canary_isolation_postgres import (
    list_all_tenant_ids,
    run_isolation_checks_for_tenants,
)


class _FakeCursor:
    def __init__(self, conn: "_FakeConn") -> None:
        self.conn = conn
        self._one: tuple[Any, ...] | None = None
        self._rows: list[tuple[Any, ...]] | None = None

    def execute(self, sql: str, params: Any = None) -> None:
        s = " ".join(sql.lower().split())
        if "set_config('app.current_tenant'" in s:
            self.conn.scope = params[0] if params else ""
        elif "set_config('app.current_workspace'" in s:
            pass
        elif "union" in s and "tenant_id" in s:
            # Simulate the UNION's de-duplication.
            self._rows = [(t,) for t in sorted(set(self.conn.all_tenants))]
        elif "is distinct from" in s:
            tenant = params[0]
            self._one = (self.conn.leaks.get(tenant, 0),)
        elif "count(*)" in s:
            # No-scope table count: a correctly fail-closed DB returns 0.
            self._one = (0,)
        else:
            self._one = (0,)

    def fetchone(self) -> tuple[Any, ...] | None:
        return self._one

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._rows or []

    def close(self) -> None:
        pass


class _FakeConn:
    def __init__(self, all_tenants: tuple[str, ...] = (), leaks: dict[str, int] | None = None) -> None:
        self.all_tenants = list(all_tenants)
        self.leaks = leaks or {}
        self.scope = ""

    def cursor(self) -> _FakeCursor:
        return _FakeCursor(self)

    def commit(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_list_all_tenant_ids_dedupes_and_sorts() -> None:
    conn = _FakeConn(all_tenants=("beta", "alpha", "alpha"))
    assert list_all_tenant_ids(conn) == ["alpha", "beta"]


def test_all_tenants_isolation_passes_when_no_leak() -> None:
    conn = _FakeConn(leaks={})
    results, ok = run_isolation_checks_for_tenants(conn, ["t1", "t2", "t3"])
    assert ok is True
    assert all(r.ok for r in results)
    # Every tenant was actually scoped and checked.
    assert {r.scope for r in results if r.scope.startswith("tenant=")} == {
        "tenant=t1",
        "tenant=t2",
        "tenant=t3",
    }


def test_all_tenants_isolation_detects_a_leak() -> None:
    conn = _FakeConn(leaks={"t2": 1})
    results, ok = run_isolation_checks_for_tenants(conn, ["t1", "t2"])
    assert ok is False
    leaked = [r for r in results if not r.ok]
    assert leaked
    assert all(r.scope == "tenant=t2" for r in leaked)
