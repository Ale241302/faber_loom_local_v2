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

    def _table_exists(self, cursor, table):
        cursor.execute(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_name = %s
            """,
            [table],
        )
        return cursor.fetchone() is not None

    def handle(self, *args, **options):
        tables = options["tables"] or self.DEFAULT_TABLES
        drop_existing = options["drop_existing"]

        with connection.cursor() as cursor:
            for table in tables:
                if not self._table_exists(cursor, table):
                    self.stdout.write(
                        self.style.WARNING(f"Skipping {table}: table does not exist.")
                    )
                    continue

                if not self._has_tenant_id_column(cursor, table):
                    self.stdout.write(
                        self.style.WARNING(f"Skipping {table}: no tenant_id column.")
                    )
                    continue

                self.stdout.write(self.style.NOTICE(f"Applying RLS to {table}..."))

                policy_name = f"tenant_isolation_{table}"

                cursor.execute(
                    f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY;'
                )
                cursor.execute(
                    f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY;'
                )

                if drop_existing:
                    cursor.execute(
                        f'DROP POLICY IF EXISTS "{policy_name}" ON "{table}";'
                    )

                cursor.execute(
                    f"""
                    CREATE POLICY "{policy_name}" ON "{table}"
                        USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::UUID);
                    """
                )

        self.stdout.write(self.style.SUCCESS("RLS policies applied successfully."))
