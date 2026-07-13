#!/usr/bin/env python3
"""Corre los reportes semanales (soak + routing) para todos los tenants.

Uso:
    python app/scripts/run_weekly_reports.py \\
        --db-path /opt/faber_loom/app/data/faberloom.sqlite3 \\
        --foundation-db /opt/faber_loom/app/data/foundation.sqlite3 \\
        --out-dir /opt/faber_loom/docs/audits
"""

from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.src.context import Context
from app.src.db import connect


def _import_report_builders() -> tuple[Any, Any, Any, Any]:
    from app.scripts.soak_report import build_soak_report, render_markdown as render_soak
    from app.scripts.routing_evidence_report import (
        build_routing_report,
        render_markdown as render_routing,
    )

    return build_soak_report, render_soak, build_routing_report, render_routing


def _list_tenants(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    rows = conn.execute(
        """
        SELECT tenant_id, MIN(id) AS workspace_id
        FROM workspace
        WHERE tenant_id IS NOT NULL AND tenant_id != ''
        GROUP BY tenant_id
        ORDER BY tenant_id
        """
    ).fetchall()
    return [(row["tenant_id"], row["workspace_id"]) for row in rows]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reportes semanales soak + routing por tenant.")
    parser.add_argument(
        "--db-path",
        required=True,
        help="Path to the FaberLoom app SQLite database.",
    )
    parser.add_argument(
        "--foundation-db",
        default=os.getenv("FABERLOOM_FOUNDATION_DB"),
        help="Path to the Foundation SQLite database (default: FABERLOOM_FOUNDATION_DB env).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("docs/audits"),
    )
    parser.add_argument(
        "--week",
        type=int,
        default=datetime.now(timezone.utc).isocalendar().week,
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Routing report window in days.",
    )
    args = parser.parse_args(argv)

    os.environ["FABERLOOM_DB_PATH"] = args.db_path
    if args.foundation_db:
        os.environ["FABERLOOM_FOUNDATION_DB"] = args.foundation_db

    build_soak, render_soak, build_routing, render_routing = _import_report_builders()

    conn = connect()
    try:
        tenants = _list_tenants(conn)
    finally:
        conn.close()

    if not tenants:
        print("No tenants found; nothing to report.")
        return 0

    errors: list[str] = []
    generated: list[Path] = []
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for tenant_id, workspace_id in tenants:
        ctx = Context(
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            user_id="weekly_reports",
            actor_id="weekly_reports",
            actor_role_at_decision="system",
        )

        # Soak report
        try:
            conn = connect()
            try:
                soak = build_soak(
                    ctx,
                    conn,
                    week=args.week,
                    db_path=args.db_path,
                    foundation_db=args.foundation_db,
                )
            finally:
                conn.close()
            soak_path = args.out_dir / f"SOAK_{tenant_id}_S{args.week}.md"
            soak_path.write_text(render_soak(soak), encoding="utf-8")
            generated.append(soak_path)
            print(f"[soak] {tenant_id} -> {soak_path}")
        except Exception as exc:
            errors.append(f"soak:{tenant_id}:{exc}")
            print(f"[soak ERROR] {tenant_id}: {exc}")

        # Routing evidence report
        try:
            conn = connect()
            try:
                routing = build_routing(ctx, conn, days=args.days)
            finally:
                conn.close()
            today = datetime.now(timezone.utc).strftime("%Y%m%d")
            routing_path = args.out_dir / f"EVIDENCIA_ROUTING_{tenant_id}_{today}.md"
            routing_path.write_text(render_routing(routing), encoding="utf-8")
            generated.append(routing_path)
            print(f"[routing] {tenant_id} -> {routing_path}")
        except Exception as exc:
            errors.append(f"routing:{tenant_id}:{exc}")
            print(f"[routing ERROR] {tenant_id}: {exc}")

    print(f"\nGenerated {len(generated)} reports, {len(errors)} errors.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
