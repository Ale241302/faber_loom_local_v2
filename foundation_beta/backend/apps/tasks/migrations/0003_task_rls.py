"""Enable RLS on the tasks table for tenant isolation (M13)."""
from __future__ import annotations

from django.db import migrations


def apply_rls_tasks(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('ALTER TABLE "tasks" ENABLE ROW LEVEL SECURITY;')
        cursor.execute('ALTER TABLE "tasks" FORCE ROW LEVEL SECURITY;')
        cursor.execute(
            """
            SELECT 1 FROM pg_policies
            WHERE policyname = 'tenant_isolation_tasks'
              AND tablename = 'tasks'
            """
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                CREATE POLICY "tenant_isolation_tasks"
                    ON "tasks"
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::UUID);
                """
            )


def revert_rls_tasks(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            'DROP POLICY IF EXISTS "tenant_isolation_tasks" ON "tasks";'
        )
        cursor.execute('ALTER TABLE "tasks" NO FORCE ROW LEVEL SECURITY;')
        cursor.execute('ALTER TABLE "tasks" DISABLE ROW LEVEL SECURITY;')


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0002_task_outputs_task_review_notes_task_review_status_and_more"),
    ]

    operations = [
        migrations.RunPython(apply_rls_tasks, revert_rls_tasks),
    ]
