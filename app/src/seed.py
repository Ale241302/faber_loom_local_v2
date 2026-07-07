"""SL0 seed data.

The seed is intentionally tiny: one demo workspace so the app can open with
persistent local state. No business facts are invented here.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from .ambient import seed_ambient_config
from .audit import audit_writer
from .context import Context, system_context
from .db import create_workspace, get_workspace_by_slug, transaction
from .kb import ingest_kb_source
from .models import AuditEvent, WorkspaceCreate


DEMO_WORKSPACE_NAME = "MWT Demo"
DEMO_WORKSPACE_SLUG = "mwt-demo"

CANARY_WORKSPACE_NAME = "Canary Tenant"
CANARY_WORKSPACE_SLUG = "canary"
CANARY_TENANT_ID = "canary"


def seed_demo_workspace(conn: sqlite3.Connection) -> dict:
    bootstrap_ctx = system_context()
    with transaction(conn, ctx=bootstrap_ctx):
        existing = get_workspace_by_slug(bootstrap_ctx, conn, DEMO_WORKSPACE_SLUG)
    if existing is not None:
        return existing

    event: AuditEvent | None = None
    with transaction(conn, ctx=bootstrap_ctx):
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
    # E2-5: seed ambient config and detectors
    with transaction(conn, ctx=workspace_ctx):
        seed_ambient_config(conn, workspace_ctx.tenant_id)

    with transaction(conn, ctx=workspace_ctx):
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


def seed_ambient_for_all_tenants(conn: sqlite3.Connection) -> None:
    """Ensure every tenant with a workspace has ambient config and detectors.

    This is idempotent: seed_ambient_config skips tenants that are already
    configured. It runs after workspace seeding so new tenants created during
    bootstrap get ambient coverage immediately.
    """

    from .db_adapter import transaction

    bootstrap_ctx = system_context()
    with transaction(conn, ctx=bootstrap_ctx):
        tenant_ids = {
            row[0]
            for row in conn.execute("SELECT DISTINCT tenant_id FROM workspace")
        }
    for tenant_id in tenant_ids:
        seed_ambient_config(conn, tenant_id)


def seed_canary_workspace(conn: sqlite3.Connection) -> dict[str, Any] | None:
    """Seed a recognizable canary tenant/workspace for isolation regression tests.

    The canary workspace is intentionally kept outside the default tenant so that
    E2 isolation tests have a persistent, distinguishable row to probe. It does
    not carry real business data.
    """

    from .context import DEFAULT_TENANT_ID

    canary_ctx = system_context(tenant_id=CANARY_TENANT_ID)
    with transaction(conn, ctx=canary_ctx):
        existing = get_workspace_by_slug(canary_ctx, conn, CANARY_WORKSPACE_SLUG)
    if existing is not None:
        return existing

    event: AuditEvent | None = None
    with transaction(conn, ctx=canary_ctx):
        created = create_workspace(
            canary_ctx,
            conn,
            WorkspaceCreate(name=CANARY_WORKSPACE_NAME, slug=CANARY_WORKSPACE_SLUG),
        )
        conn.execute(
            "UPDATE workspace SET is_canary = 1 WHERE id = ?",
            (created["id"],),
        )
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
                "tenant_id": CANARY_TENANT_ID,
                "is_canary": True,
            },
            mirror_jsonl=False,
        )

    if event is not None:
        audit_writer.mirror(event)

    return created
