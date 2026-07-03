"""Enable RLS on outcome_entries for tenant isolation."""
from __future__ import annotations

from django.db import migrations


def apply_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('ALTER TABLE "outcome_entries" ENABLE ROW LEVEL SECURITY;')
        cursor.execute('ALTER TABLE "outcome_entries" FORCE ROW LEVEL SECURITY;')
        cursor.execute(
            """
            SELECT 1 FROM pg_policies
            WHERE policyname = 'tenant_isolation_outcome_entries'
              AND tablename = 'outcome_entries'
            """
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                CREATE POLICY "tenant_isolation_outcome_entries"
                    ON "outcome_entries"
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::UUID);
                """
            )


def revert_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            'DROP POLICY IF EXISTS "tenant_isolation_outcome_entries" ON "outcome_entries";'
        )
        cursor.execute('ALTER TABLE "outcome_entries" NO FORCE ROW LEVEL SECURITY;')
        cursor.execute('ALTER TABLE "outcome_entries" DISABLE ROW LEVEL SECURITY;')


class Migration(migrations.Migration):
    dependencies = [
        ("outcomes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(apply_rls, revert_rls),
    ]
