"""Enable RLS on the sample_items test table used by M16 cross-tenant tests."""
from django.db import migrations


def apply_rls_sample_items(apps, schema_editor):
    """Enable and force RLS, creating the tenant isolation policy."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('ALTER TABLE "sample_items" ENABLE ROW LEVEL SECURITY;')
        cursor.execute('ALTER TABLE "sample_items" FORCE ROW LEVEL SECURITY;')

        cursor.execute(
            """
            SELECT 1 FROM pg_policies
            WHERE policyname = 'tenant_isolation_sample_items'
              AND tablename = 'sample_items'
            """
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                CREATE POLICY "tenant_isolation_sample_items"
                    ON "sample_items"
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::UUID);
                """
            )


def revert_rls_sample_items(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            'DROP POLICY IF EXISTS "tenant_isolation_sample_items" ON "sample_items";'
        )
        cursor.execute('ALTER TABLE "sample_items" NO FORCE ROW LEVEL SECURITY;')
        cursor.execute('ALTER TABLE "sample_items" DISABLE ROW LEVEL SECURITY;')


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_kb_embedding"),
    ]

    operations = [
        migrations.RunPython(apply_rls_sample_items, revert_rls_sample_items),
    ]
