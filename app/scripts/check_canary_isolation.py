#!/usr/bin/env python3
"""M16-contra-canario: test de regresión de aislamiento por deploy.

Contrato: plan E2 Sec.7.3 — el canario es permanente y este check corre en
cada despliegue. Verifica en AMBAS direcciones que el scoping por tenant no
filtra filas: para cada tenant (incluido `canary`), el acceso scoped a cada
tabla fnd_* devuelve exactamente sus filas propias, y las filas del canario
jamás aparecen en el scope de otro tenant.

Uso:
    python3 app/scripts/check_canary_isolation.py [--db /ruta/faberloom.sqlite3]
Exit code 0 = aislamiento OK; 1 = fuga detectada (bloquea el deploy).
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

from app.src.foundation.m16_tenant_isolation import _tenant_tables, tenant_scoped  # noqa: E402

CANARY_TENANT_ID = "canary"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=os.getenv("FABERLOOM_DB_PATH", "/data/faberloom.sqlite3"))
    parser.add_argument("--foundation-db", default=None,
                        help="foundation.sqlite3 (default: junto a --db)")
    args = parser.parse_args()

    foundation_path = args.foundation_db or os.path.join(os.path.dirname(args.db), "foundation.sqlite3")
    conn = sqlite3.connect(foundation_path)
    conn.row_factory = sqlite3.Row

    # Presencia del canario en la BD principal de la app (seed permanente).
    app_conn = sqlite3.connect(args.db)
    app_conn.row_factory = sqlite3.Row
    canary_ws = app_conn.execute(
        "SELECT COUNT(*) AS c FROM workspace WHERE tenant_id = ? AND is_canary = 1",
        (CANARY_TENANT_ID,),
    ).fetchone()["c"]
    if canary_ws == 0:
        print("[FAIL] canary workspace no sembrado en la BD principal")
        return 1

    tenants = {r["id"] for r in conn.execute("SELECT id FROM fnd_tenants").fetchall()}
    tenants.add(CANARY_TENANT_ID)

    failures: list[str] = []
    checked = 0
    for tenant_id in sorted(tenants):
        for table in _tenant_tables(conn):
            own = conn.execute(
                f"SELECT COUNT(*) AS c FROM {table} WHERE tenant_id = ?", (tenant_id,)
            ).fetchone()["c"]
            scoped_rows = tenant_scoped(conn, table, tenant_id)
            scoped = len(scoped_rows)
            checked += 1
            if scoped != own:
                failures.append(
                    f"{table}: tenant={tenant_id} own={own} scoped={scoped} (FUGA)"
                )
            # Dirección inversa explícita: ninguna fila del canario en scope ajeno.
            if tenant_id != CANARY_TENANT_ID:
                canary_in_scope = sum(
                    1 for r in scoped_rows if dict(r).get("tenant_id") == CANARY_TENANT_ID
                )
                if canary_in_scope:
                    failures.append(
                        f"{table}: {canary_in_scope} filas CANARY visibles desde tenant={tenant_id}"
                    )

    if failures:
        print(f"[FAIL] M16-contra-canario: {len(failures)} fugas en {checked} checks")
        for f in failures:
            print("  -", f)
        return 1
    print(f"[OK] M16-contra-canario: 0 fugas ({checked} checks, tenants: {', '.join(sorted(tenants))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
