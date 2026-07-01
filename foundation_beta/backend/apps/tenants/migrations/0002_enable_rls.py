# Generated manually for Foundation Beta M16
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0001_initial"),
        ("core", "0002_kb_embedding"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                DO $$
                DECLARE
                    tbl text;
                    policy_name text;
                BEGIN
                    FOR tbl IN
                        SELECT table_name
                        FROM information_schema.columns
                        WHERE column_name = 'tenant_id'
                          AND table_schema = 'public'
                          AND table_name IN (
                              'sample_items', 'kb_embedding', 'workspaces',
                              'chats', 'messages', 'drafts', 'routines',
                              'routine_runs', 'usage_records', 'kb_sources',
                              'kb_chunks', 'kb_facts', 'mail_messages',
                              'mail_outbox', 'email_accounts', 'gold_candidates',
                              'audit_logs', 'editorial_histories', 'outboxes',
                              'event_logs'
                          )
                    LOOP
                        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
                        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', tbl);
                        policy_name := 'tenant_isolation_' || tbl;
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_policies
                            WHERE policyname = policy_name AND tablename = tbl
                        ) THEN
                            EXECUTE format(
                                'CREATE POLICY %I ON %I USING (tenant_id = NULLIF(current_setting(''app.tenant_id'', true), '''')::UUID)',
                                policy_name, tbl
                            );
                        END IF;
                    END LOOP;
                END $$;
            """,
            reverse_sql="""
                DO $$
                DECLARE
                    tbl text;
                    policy_name text;
                BEGIN
                    FOR tbl IN
                        SELECT table_name
                        FROM information_schema.columns
                        WHERE column_name = 'tenant_id'
                          AND table_schema = 'public'
                    LOOP
                        policy_name := 'tenant_isolation_' || tbl;
                        IF EXISTS (
                            SELECT 1 FROM pg_policies
                            WHERE policyname = policy_name AND tablename = tbl
                        ) THEN
                            EXECUTE format('DROP POLICY %I ON %I', policy_name, tbl);
                        END IF;
                        EXECUTE format('ALTER TABLE %I NO FORCE ROW LEVEL SECURITY', tbl);
                        EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY', tbl);
                    END LOOP;
                END $$;
            """,
        ),
    ]
