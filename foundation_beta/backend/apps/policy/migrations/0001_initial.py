"""Initial migration for M11 D9 Policy Gate."""
from __future__ import annotations

import django.db.models.deletion
import uuid
from django.db import migrations, models


def apply_policy_rls(apps, schema_editor):
    """Enable RLS and tenant isolation policies for policy tables."""
    with schema_editor.connection.cursor() as cursor:
        for table in ("dpa_statements", "data_classification_defaults", "policy_blocks"):
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


def revert_policy_rls(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        for table in ("dpa_statements", "data_classification_defaults", "policy_blocks"):
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
            name="DpaStatement",
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
                (
                    "status",
                    models.CharField(
                        default="missing",
                        max_length=16,
                    ),
                ),
                ("signed_at", models.DateTimeField(blank=True, null=True)),
                ("version", models.TextField(default="v1")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "signed_by",
                    models.ForeignKey(
                        blank=True,
                        db_column="signed_by",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="signed_dpas",
                        to="users.user",
                    ),
                ),
                (
                    "tenant",
                    models.OneToOneField(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="dpa_statement",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "db_table": "dpa_statements",
            },
        ),
        migrations.CreateModel(
            name="DataClassificationDefault",
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
                ("source_type", models.TextField()),
                (
                    "default_class",
                    models.CharField(
                        default="N1",
                        max_length=2,
                    ),
                ),
                ("overrides", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="classification_defaults",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "db_table": "data_classification_defaults",
            },
        ),
        migrations.CreateModel(
            name="PolicyBlock",
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
                ("case_id", models.TextField(blank=True, null=True)),
                ("declared_class", models.CharField(max_length=2)),
                ("effective_class", models.CharField(max_length=2)),
                ("reason", models.TextField()),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "resolved_by",
                    models.ForeignKey(
                        blank=True,
                        db_column="resolved_by",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="resolved_blocks",
                        to="users.user",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="policy_blocks",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "db_table": "policy_blocks",
            },
        ),
        migrations.AlterUniqueTogether(
            name="dataclassificationdefault",
            unique_together={("tenant", "source_type")},
        ),
        migrations.RunPython(apply_policy_rls, revert_policy_rls),
    ]
