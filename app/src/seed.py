"""SL0 seed data.

The seed is intentionally tiny: one demo workspace so the app can open with
persistent local state. No business facts are invented here.
"""

from __future__ import annotations

import sqlite3

from .audit import audit_writer
from .context import Context, system_context
from .db import create_workspace, get_workspace_by_slug, transaction
from .kb import ingest_kb_source
from .models import AuditEvent, WorkspaceCreate


DEMO_WORKSPACE_NAME = "MWT Demo"
DEMO_WORKSPACE_SLUG = "mwt-demo"


def seed_demo_workspace(conn: sqlite3.Connection) -> dict:
    bootstrap_ctx = system_context()
    existing = get_workspace_by_slug(bootstrap_ctx, conn, DEMO_WORKSPACE_SLUG)
    if existing is not None:
        return existing

    event: AuditEvent | None = None
    with transaction(conn):
        created = create_workspace(
            bootstrap_ctx,
            conn,
            WorkspaceCreate(name=DEMO_WORKSPACE_NAME, slug=DEMO_WORKSPACE_SLUG),
        )
        from .context import DEFAULT_TENANT_ID
        workspace_ctx = Context(
            workspace_id=created["id"],
            tenant_id=created.get("tenant_id") or DEFAULT_TENANT_ID,
            user_id=created.get("user_id") or "local",
            actor_id=created.get("actor_id") or "local",
            actor_role_at_decision=created.get("actor_role_at_decision") or "owner",
        )
        event = audit_writer.write(
            workspace_ctx,
            conn,
            action="workspace.seeded",
            payload={
                "workspace_id": created["id"],
                "name": created["name"],
                "slug": created["slug"],
            },
            mirror_jsonl=False,
        )

    if event is not None:
        audit_writer.mirror(event)

    # SL1b: seed an explicit demo KB so users can dogfood drafts immediately.
    # These prices are synthetic fixtures, not real MWT data.
    demo_kb_md = """# Catálogo demo FaberLoom (FIXTURE)

Esta fuente es un fixture de demostración. Los precios no son reales.

## Telas básicas

- Oxford premium: USD 12.50 por metro. Stock demo: 240 m.
- Lino natural: USD 18.00 por metro. Stock demo: 120 m.
- Gabardina stretch: USD 15.75 por metro. Stock demo: 85 m.

## Condiciones demo

- MOQ (mínimo de pedido): 20 metros por artículo.
- Lead time demo: 3 a 5 días hábiles para stock.
- Vigencia demo: 2026-06-01 a 2026-09-30.
"""
    demo_kb_csv = """sku,nombre,precio_usd,moneda,stock_m,vigente_desde,vigente_hasta
TEL-DEMO-001,Oxford premium,12.50,USD,240,2026-06-01,2026-09-30
TEL-DEMO-002,Lino natural,18.00,USD,120,2026-06-01,2026-09-30
TEL-DEMO-003,Gabardina stretch,15.75,USD,85,2026-06-01,2026-09-30
"""
    with transaction(conn):
        ingest_kb_source(
            workspace_ctx,
            conn,
            title="Demo MWT - Catálogo de telas (fixture)",
            source_type="md",
            content_text=demo_kb_md,
            source_version="demo-v1",
            approved_by="seed",
        )
        ingest_kb_source(
            workspace_ctx,
            conn,
            title="Demo MWT - Tabla CSV de precios (fixture)",
            source_type="csv",
            content_text=demo_kb_csv,
            source_version="demo-v1",
            approved_by="seed",
        )

    return created
