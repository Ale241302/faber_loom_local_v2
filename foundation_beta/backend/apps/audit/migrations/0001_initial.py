"""Initial migration for M12 Audit Trail."""
from __future__ import annotations

import django.db.models.deletion
import uuid
from django.db import migrations, models


def apply_audit_ddl(apps, schema_editor):
    """Create sequence, append-only triggers, RLS policy and app-role grants."""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("CREATE SEQUENCE IF NOT EXISTS audit_seq;")

        cursor.execute(
            """
            CREATE OR REPLACE FUNCTION reject_audit_mutation()
            RETURNS TRIGGER AS $$
            BEGIN
                RAISE EXCEPTION 'audit_log is append-only';
            END;
            $$ LANGUAGE plpgsql;
            """
        )

        cursor.execute(
            """
            DROP TRIGGER IF EXISTS audit_no_update ON audit_log;
            CREATE TRIGGER audit_no_update
                BEFORE UPDATE ON audit_log
                FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation();
            """
        )
        cursor.execute(
            """
            DROP TRIGGER IF EXISTS audit_no_delete ON audit_log;
            CREATE TRIGGER audit_no_delete
                BEFORE DELETE ON audit_log
                FOR EACH ROW EXECUTE FUNCTION reject_audit_mutation();
            """
        )

        cursor.execute('ALTER TABLE "audit_log" ENABLE ROW LEVEL SECURITY;')
        cursor.execute('ALTER TABLE "audit_log" FORCE ROW LEVEL SECURITY;')

        cursor.execute(
            """
            SELECT 1 FROM pg_policies
            WHERE policyname = 'tenant_isolation_audit_log'
              AND tablename = 'audit_log'
            """
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                CREATE POLICY "tenant_isolation_audit_log"
                    ON "audit_log"
                    USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::UUID);
                """
            )

        # App-role privilege hardening (defense in depth; triggers enforce append-only).
        cursor.execute(
            "SELECT rolname FROM pg_roles WHERE rolname IN ('faberloom_app', 'faberloom_backend')"
        )
        for (role_name,) in cursor.fetchall():
            cursor.execute(
                f"GRANT INSERT, SELECT ON audit_log TO {role_name};"
            )
            cursor.execute(
                f"REVOKE UPDATE, DELETE ON audit_log FROM {role_name};"
            )


def revert_audit_ddl(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "DROP TRIGGER IF EXISTS audit_no_update ON audit_log;"
        )
        cursor.execute(
            "DROP TRIGGER IF EXISTS audit_no_delete ON audit_log;"
        )
        cursor.execute('DROP POLICY IF EXISTS "tenant_isolation_audit_log" ON audit_log;')
        cursor.execute('ALTER TABLE "audit_log" NO FORCE ROW LEVEL SECURITY;')
        cursor.execute('ALTER TABLE "audit_log" DISABLE ROW LEVEL SECURITY;')


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
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
                ("action_id", models.TextField()),
                ("data_class", models.TextField(default="N1")),
                ("task_type", models.TextField(blank=True, null=True)),
                ("model_provider", models.TextField(blank=True, null=True)),
                ("model_id", models.TextField(blank=True, null=True)),
                ("model_version", models.TextField(blank=True, null=True)),
                ("orchestrator_policy_pool_hash", models.TextField(blank=True, null=True)),
                ("prompt_hash", models.TextField(blank=True, null=True)),
                ("output_hash", models.TextField(blank=True, null=True)),
                ("human_gate_required", models.BooleanField(default=False)),
                (
                    "sha_chain_prev",
                    models.TextField(),
                ),
                (
                    "sha_chain_curr",
                    models.TextField(),
                ),
                ("seq_no", models.BigIntegerField()),
                ("chain_id", models.TextField()),
                ("actor_id", models.UUIDField()),
                ("actor_role_at_decision", models.TextField()),
                ("payload_json", models.JSONField(default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "human_approver",
                    models.ForeignKey(
                        blank=True,
                        db_column="human_approver_id",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="users.user",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        db_column="tenant_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "db_table": "audit_log",
            },
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(
                fields=["tenant", "chain_id", "seq_no"],
                name="idx_audit_tenant_chain_seq",
            ),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(
                fields=["tenant", "case_id", "created_at"],
                name="idx_audit_tenant_case",
            ),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(
                fields=["tenant", "actor_id", "created_at"],
                name="idx_audit_tenant_actor",
            ),
        ),
        migrations.RunPython(apply_audit_ddl, revert_audit_ddl),
    ]
