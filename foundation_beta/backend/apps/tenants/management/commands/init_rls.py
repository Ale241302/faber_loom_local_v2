"""Management command to enable RLS and create tenant isolation policies."""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Enable FORCE ROW LEVEL SECURITY and create tenant isolation policies."

    DEFAULT_TABLES = [
        "workspaces",
        "chats",
        "messages",
        "drafts",
        "routines",
        "routine_runs",
        "usage_records",
        "kb_sources",
        "kb_chunks",
        "kb_facts",
        "kb_embedding",
        "mail_messages",
        "mail_outbox",
        "email_accounts",
        "gold_candidates",
        "audit_logs",
        "editorial_histories",
        "outboxes",
        "event_logs",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--tables",
            nargs="+",
            help="List of tables to scope. Defaults to the Foundation Beta tenant-scoped list.",
        )
        parser.add_argument(
            "--drop-existing",
            action="store_true",
            help="Drop existing policies before creating them.",
        )

    def _has_tenant_id_column(self, cursor, table):
        cursor.execute(
            """
            SELECT 1 FROM information_schema.columns
            WHERE table_name = %s AND column_name = 'tenant_id'
            """,
            [table],
        )
        return cursor.fetchone() is not None

    def handle(self, *args, **options):
        tables = options["tables"] or self.DEFAULT_TABLES
        drop_existing = options["drop_existing"]

        with connection.cursor() as cursor:
            for table in tables:
                if not self._has_tenant_id_column(cursor, table):
                    self.stdout.write(
                        self.style.WARNING(f"Skipping {table}: no tenant_id column.")
                    )
                    continue

                self.stdout.write(self.style.NOTICE(f"Applying RLS to {table}..."))

                cursor.execute(
                    """
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1 FROM information_schema.tables
                            WHERE table_name = %s
                        ) THEN
                            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', %s);
                            EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', %s);
                        END IF;
                    END $$;
                    """,
                    [table, table, table, table],
                )

                policy_name = f"tenant_isolation_{table}"

                if drop_existing:
                    cursor.execute(
                        """
                        DO $$
                        BEGIN
                            IF EXISTS (
                                SELECT 1 FROM pg_policies
                                WHERE policyname = %s AND tablename = %s
                            ) THEN
                                EXECUTE format('DROP POLICY %I ON %I', %s, %s);
                            END IF;
                        END $$;
                        """,
                        [policy_name, table, policy_name, table],
                    )

                cursor.execute(
                    """
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1 FROM information_schema.tables
                            WHERE table_name = %s
                        ) AND NOT EXISTS (
                            SELECT 1 FROM pg_policies
                            WHERE policyname = %s AND tablename = %s
                        ) THEN
                            EXECUTE format(
                                'CREATE POLICY %I ON %I USING (tenant_id = NULLIF(current_setting(''app.tenant_id'', true), '''')::UUID)',
                                %s, %s
                            );
                        END IF;
                    END $$;
                    """,
                    [table, policy_name, table, policy_name, table],
                )

        self.stdout.write(self.style.SUCCESS("RLS policies applied successfully."))
