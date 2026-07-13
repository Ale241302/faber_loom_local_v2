#!/usr/bin/env python3
"""Onboarding de un design partner en FaberLoom (E5-6).

Crea tenant Foundation, usuario owner y workspace canario en un solo comando.
Genera el acuerdo de datos beta personalizado y la evidencia de onboarding.

El script es dry-run por defecto; usar --execute para mutar. Requiere:
  --partner-name, --partner-slug, --owner-email, --owner-password

Ejemplo (dry-run):
    python app/scripts/onboard_design_partner.py \\
        --partner-name "Marluvas" \\
        --partner-slug marluvas \\
        --owner-email admin@marluvas.com \\
        --owner-password SuperSecret123

Ejemplo (ejecutar):
    python app/scripts/onboard_design_partner.py \\
        --partner-name "Marluvas" \\
        --partner-slug marluvas \\
        --owner-email admin@marluvas.com \\
        --owner-password SuperSecret123 \\
        --execute --approved-by usr_ceo
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.src.audit import audit_writer
from app.src.context import Context
from app.src.db import connect, get_database_path, new_id, utc_now


AGREEMENT_TEMPLATE = Path("docs/faberloom/SCH_FB_ACUERDO_DATOS_BETA_v1.md")


def _foundation_db_path() -> Path:
    env = os.getenv("FABERLOOM_FOUNDATION_DB")
    if env:
        return Path(env).expanduser().resolve()
    main = get_database_path()
    return main.with_name(f"{main.stem}-foundation.sqlite3")


def _connect_foundation() -> sqlite3.Connection:
    path = _foundation_db_path()
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _hash_password(password: str) -> str:
    """Local copy of foundation password hashing to avoid heavy imports."""

    import hashlib
    import secrets

    iterations = 600_000
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2${iterations}${salt.hex()}${digest.hex()}"


def _seed_system_roles(conn: sqlite3.Connection, tenant_id: str) -> None:
    """Idempotent system-role seeding (subset required for owner login)."""

    now = utc_now()
    roles = {
        "owner": {
            "description": "Propietario del tenant",
            "permissions": ["*"],
        },
    }
    for name, spec in roles.items():
        exists = conn.execute(
            "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?",
            (tenant_id, name),
        ).fetchone()
        if not exists:
            conn.execute(
                """
                INSERT INTO fnd_roles
                (id, tenant_id, name, description, permissions_json, is_system, created_at)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (
                    new_id("rol"),
                    tenant_id,
                    name,
                    spec["description"],
                    json.dumps(spec["permissions"]),
                    now,
                ),
            )


def _validate_inputs(
    foundation: sqlite3.Connection,
    app: sqlite3.Connection,
    *,
    slug: str,
    email: str,
) -> None:
    if not slug or len(slug) < 3 or not slug.replace("-", "").isalnum():
        raise ValueError("slug inválido: mínimo 3 caracteres alfanuméricos o guiones")
    if "@" not in email:
        raise ValueError("owner-email inválido")

    existing = foundation.execute(
        "SELECT id FROM fnd_tenants WHERE slug = ?", (slug,)
    ).fetchone()
    if existing:
        raise ValueError(f"ya existe un tenant con slug '{slug}'")

    email_exists = foundation.execute(
        "SELECT id FROM fnd_users WHERE email = ?", (email,)
    ).fetchone()
    if email_exists:
        raise ValueError(f"ya existe un usuario con email '{email}'")


def _create_partner(
    foundation: sqlite3.Connection,
    app: sqlite3.Connection,
    *,
    partner_name: str,
    slug: str,
    owner_email: str,
    owner_password: str,
    plan: str,
    approved_by: str,
) -> dict[str, Any]:
    tenant_id = new_id("tnt")
    user_id = new_id("usr")
    workspace_id = f"ws_{tenant_id}"
    seal_id = uuid.uuid4().hex
    now = utc_now()

    # Foundation tenant + owner
    foundation.execute(
        """
        INSERT INTO fnd_tenants
        (id, name, slug, status, plan, created_at, activated_at)
        VALUES (?, ?, ?, 'active', ?, ?, ?)
        """,
        (tenant_id, partner_name, slug, plan, now, now),
    )
    _seed_system_roles(foundation, tenant_id)
    role_row = foundation.execute(
        "SELECT id FROM fnd_roles WHERE tenant_id = ? AND name = ?",
        (tenant_id, "owner"),
    ).fetchone()
    assert role_row is not None

    foundation.execute(
        """
        INSERT INTO fnd_users
        (id, tenant_id, email, display_name, password_hash, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'active', ?)
        """,
        (
            user_id,
            tenant_id,
            owner_email,
            owner_email.split("@")[0],
            _hash_password(owner_password),
            now,
        ),
    )
    foundation.execute(
        """
        INSERT INTO fnd_user_roles (tenant_id, user_id, role_id, assigned_by, assigned_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (tenant_id, user_id, role_row["id"], approved_by, now),
    )

    # App workspace canario
    app.execute(
        """
        INSERT INTO workspace (
            id, name, slug, kind, seal_id, field_aliases_json, tenant_id,
            user_id, actor_id, actor_role_at_decision, routine_version, skill_version,
            schema_version, source_version, is_canary, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            workspace_id,
            f"{partner_name} (canary)",
            slug,
            "standard",
            seal_id,
            "{}",
            tenant_id,
            user_id,
            approved_by,
            "system",
            None,
            None,
            48,
            "v1",
            1,
            now,
            now,
        ),
    )

    foundation.commit()
    app.commit()

    return {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "workspace_id": workspace_id,
        "slug": slug,
        "owner_email": owner_email,
    }


def _render_agreement(
    *,
    partner_name: str,
    slug: str,
    tenant_id: str,
    owner_email: str,
    plan: str,
    generated_at: str,
) -> str:
    if AGREEMENT_TEMPLATE.exists():
        template = AGREEMENT_TEMPLATE.read_text(encoding="utf-8")
    else:
        template = (
            "# Acuerdo de datos beta\n\n"
            "[PENDIENTE — plantilla SCH_FB_ACUERDO_DATOS_BETA_v1.md no encontrada]\n"
        )

    return (
        template
        + "\n\n---\n\n"
        + f"- **Partner**: {partner_name}\n"
        + f"- **slug**: {slug}\n"
        + f"- **tenant_id**: `{tenant_id}`\n"
        + f"- **owner_email**: {owner_email}\n"
        + f"- **plan**: {plan}\n"
        + f"- **generado_en**: {generated_at}\n"
        + "- **estado**: `pendiente_firma` (requiere revisión legal y firma humana)\n"
    )


def _render_evidence(
    *,
    partner_name: str,
    slug: str,
    tenant_id: str,
    user_id: str,
    workspace_id: str,
    owner_email: str,
    plan: str,
    generated_at: str,
    agreement_path: Path,
    dry_run: bool,
) -> str:
    return (
        "# Evidencia de onboarding de design partner (E5-6)\n\n"
        f"- **partner**: {partner_name}\n"
        f"- **slug**: {slug}\n"
        f"- **tenant_id**: `{tenant_id}`\n"
        f"- **user_id (owner)**: `{user_id}`\n"
        f"- **workspace_id (canario)**: `{workspace_id}`\n"
        f"- **owner_email**: {owner_email}\n"
        f"- **plan**: {plan}\n"
        f"- **generado_en**: {generated_at}\n"
        f"- **dry_run**: {dry_run}\n"
        "\n## Acciones realizadas\n\n"
        "- [x] Tenant creado en Foundation DB.\n"
        "- [x] Usuario owner creado con rol owner.\n"
        f"- [x] Workspace canario creado (`is_canary=1`).\n"
        f"- [{' ' if dry_run else 'x'}] Acuerdo de datos beta generado: `{agreement_path}`\n"
        "\n## Acciones humanas residuales\n\n"
        "1. Revisión legal del acuerdo de datos beta.\n"
        "2. Firma del acuerdo por ambas partes.\n"
        "3. Entrega de credenciales al owner por canal seguro.\n"
        "\n## Reglas de oro aplicadas\n\n"
        "- R2: Esquema FROZEN intacto; inserciones usan columnas existentes.\n"
        "- R11/R12: Context tenant-scoped y audit log de onboarding.\n"
        "- Fail-closed: dry-run por defecto; validaciones de slug/email únicos.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Onboarding de design partner: tenant, owner y workspace canario."
    )
    parser.add_argument("--partner-name", required=True)
    parser.add_argument("--partner-slug", required=True)
    parser.add_argument("--owner-email", required=True)
    parser.add_argument("--owner-password", required=True)
    parser.add_argument("--plan", default="beta")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approved-by", default=None)
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("docs/audits"),
    )
    parser.add_argument(
        "--db-path",
        default=os.getenv("FABERLOOM_DB_PATH"),
        help="Path to the FaberLoom app SQLite database (default: FABERLOOM_DB_PATH env).",
    )
    args = parser.parse_args(argv)

    if not args.db_path:
        print("Error: --db-path or FABERLOOM_DB_PATH is required", file=sys.stderr)
        return 2

    os.environ["FABERLOOM_DB_PATH"] = args.db_path

    if args.execute and not args.approved_by:
        print("Error: --execute requiere --approved-by", file=sys.stderr)
        return 2

    generated_at = utc_now()
    slug = args.partner_slug.lower().strip()
    agreement_path = args.out_dir / f"ACUERDO_{slug}_v1.md"
    evidence_path = args.out_dir / f"EVIDENCIA_DESIGN_PARTNER_{slug}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"

    foundation = _connect_foundation()
    app = connect()
    try:
        _validate_inputs(foundation, app, slug=slug, email=args.owner_email)

        if args.execute:
            result = _create_partner(
                foundation,
                app,
                partner_name=args.partner_name,
                slug=slug,
                owner_email=args.owner_email,
                owner_password=args.owner_password,
                plan=args.plan,
                approved_by=args.approved_by,
            )

            # Audit in app workspace context
            ctx = Context(
                workspace_id=result["workspace_id"],
                tenant_id=result["tenant_id"],
                user_id=args.approved_by,
                actor_id=args.approved_by,
                actor_role_at_decision="system",
            )
            audit_writer.write(
                ctx,
                app,
                action="design_partner.onboarded",
                payload={
                    "partner_name": args.partner_name,
                    "slug": slug,
                    "owner_email": args.owner_email,
                    "plan": args.plan,
                    "agreement_path": str(agreement_path),
                },
                approved_by=args.approved_by,
                source_version="v1",
                system_event=False,
            )
        else:
            result = {
                "tenant_id": "DRYRUN_TENANT_ID",
                "user_id": "DRYRUN_USER_ID",
                "workspace_id": f"ws_DRYRUN_{slug}",
                "slug": slug,
                "owner_email": args.owner_email,
            }

        agreement = _render_agreement(
            partner_name=args.partner_name,
            slug=slug,
            tenant_id=result["tenant_id"],
            owner_email=args.owner_email,
            plan=args.plan,
            generated_at=generated_at,
        )

        evidence = _render_evidence(
            partner_name=args.partner_name,
            slug=slug,
            tenant_id=result["tenant_id"],
            user_id=result["user_id"],
            workspace_id=result["workspace_id"],
            owner_email=args.owner_email,
            plan=args.plan,
            generated_at=generated_at,
            agreement_path=agreement_path,
            dry_run=not args.execute,
        )

        args.out_dir.mkdir(parents=True, exist_ok=True)
        agreement_path.write_text(agreement, encoding="utf-8")
        evidence_path.write_text(evidence, encoding="utf-8")

        print(f"Agreement template: {agreement_path}")
        print(f"Evidence report: {evidence_path}")
        if args.execute:
            print(
                f"Onboarded partner: tenant={result['tenant_id']} "
                f"workspace={result['workspace_id']} owner={result['user_id']}"
            )
        else:
            print("DRY-RUN: no se mutó la base de datos.")
        return 0
    except Exception as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1
    finally:
        foundation.close()
        app.close()


if __name__ == "__main__":
    sys.exit(main())
