"""Initial migration for M07 Bootstrap Wizard."""
from __future__ import annotations

import django.db.models.deletion
import uuid
from django.db import migrations, models


def apply_bootstrap_rls(apps, schema_editor):
    """Enable RLS and tenant isolation policies for bootstrap tables."""
    with schema_editor.connection.cursor() as cursor:
        for table in (
            "tenant_bootstrap_progress",
            "email_bindings",
            "voice_profiles",
            "system_agents",
        ):
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

            cursor.execute(
                f"SELECT rolname FROM pg_roles WHERE rolname IN ('faberloom_app', 'faberloom_backend')"
            )
            for (role_name,) in cursor.fetchall():
                cursor.execute(f"GRANT INSERT, SELECT, UPDATE, DELETE ON {table} TO {role_name};")


def revert_bootstrap_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in (
            "tenant_bootstrap_progress",
            "email_bindings",
            "voice_profiles",
            "system_agents",
        ):
            cursor.execute(f'DROP POLICY IF EXISTS "tenant_isolation_{table}" ON "{table}";')
            cursor.execute(f'ALTER TABLE "{table}" NO FORCE ROW LEVEL SECURITY;')
            cursor.execute(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY;')


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TenantBootstrapProgress",
            fields=[
                (
                    "tenant",
                    models.OneToOneField(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to="tenants.tenant",
                    ),
                ),
                ("steps_completed", models.JSONField(default=list)),
                ("steps_blocked", models.JSONField(default=list)),
                ("sandbox_result", models.JSONField(blank=True, default=dict)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "tenant_bootstrap_progress",
            },
        ),
        migrations.CreateModel(
            name="EmailBinding",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("provider", models.CharField(max_length=16)),
                ("account", models.TextField()),
                ("credentials_encrypted", models.TextField()),
                ("is_default", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="email_bindings",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "db_table": "email_bindings",
            },
        ),
        migrations.CreateModel(
            name="VoiceProfile",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("persona", models.TextField()),
                ("tone", models.TextField()),
                ("glossary", models.JSONField(default=list)),
                ("greeting", models.TextField(blank=True)),
                ("signature", models.TextField(blank=True)),
                ("is_default", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="voice_profiles",
                        to="tenants.tenant",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_column="user_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="voice_profiles",
                        to="users.user",
                    ),
                ),
            ],
            options={
                "db_table": "voice_profiles",
            },
        ),
        migrations.CreateModel(
            name="SystemAgent",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("name", models.TextField()),
                ("origin", models.TextField(default="system")),
                ("skill_md", models.TextField()),
                ("status", models.CharField(default="shadow", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="system_agents",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "db_table": "system_agents",
            },
        ),
        migrations.RunPython(apply_bootstrap_rls, revert_bootstrap_rls),
    ]
