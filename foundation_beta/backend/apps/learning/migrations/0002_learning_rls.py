"""Enable RLS on learning tables for tenant isolation (M14)."""
from __future__ import annotations

from django.db import migrations


TABLES = ["outcome_ledger_entries", "gold_samples", "learning_thermometers"]


def apply_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in TABLES:
            cursor.execute(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY;')
            cursor.execute(f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY;')
            cursor.execute(
                f"""
                SELECT 1 FROM pg_policies
                WHERE policyname = 'tenant_isolation_{table}'
                  AND tablename = '{table}'
                """
            )
            if not cursor.fetchone():
                cursor.execute(
                    f"""
                    CREATE POLICY "tenant_isolation_{table}"
                        ON "{table}"
                        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::UUID);
                    """
                )


def revert_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in TABLES:
            cursor.execute(f'DROP POLICY IF EXISTS "tenant_isolation_{table}" ON "{table}";')
            cursor.execute(f'ALTER TABLE "{table}" NO FORCE ROW LEVEL SECURITY;')
            cursor.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY;')


class Migration(migrations.Migration):
    dependencies = [
        ("learning", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(apply_rls, revert_rls),
    ]
