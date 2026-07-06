-- Postgres RLS policies for FaberLoom E2-1.
-- Run as the migrator/owner user after creating tables and the app user.
-- The application user (faberloom_app) must NOT have BYPASS RLS.

-- Enable RLS on workspace-owned tables.
ALTER TABLE workspace ENABLE ROW LEVEL FORCE;
ALTER TABLE kb_source ENABLE ROW LEVEL FORCE;
ALTER TABLE kb_chunk ENABLE ROW LEVEL FORCE;
ALTER TABLE kb_fact ENABLE ROW LEVEL FORCE;
ALTER TABLE chat ENABLE ROW LEVEL FORCE;
ALTER TABLE message ENABLE ROW LEVEL FORCE;
ALTER TABLE draft ENABLE ROW LEVEL FORCE;
ALTER TABLE routine ENABLE ROW LEVEL FORCE;
ALTER TABLE routine_run ENABLE ROW LEVEL FORCE;
ALTER TABLE gold_candidate ENABLE ROW LEVEL FORCE;
ALTER TABLE usage_record ENABLE ROW LEVEL FORCE;
ALTER TABLE mail_message ENABLE ROW LEVEL FORCE;
ALTER TABLE mail_outbox ENABLE ROW LEVEL FORCE;
ALTER TABLE email_account ENABLE ROW LEVEL FORCE;
ALTER TABLE audit_log ENABLE ROW LEVEL FORCE;
ALTER TABLE editorial_history ENABLE ROW LEVEL FORCE;
ALTER TABLE workspace_smtp_config ENABLE ROW LEVEL FORCE;

-- Helper function to set the current tenant/workspace for the connection.
-- The app must call SELECT set_app_scope('tenant-uuid', 'workspace-id') before
-- every request, or set the variables via SET LOCAL.
CREATE OR REPLACE FUNCTION set_app_scope(p_tenant TEXT, p_workspace TEXT)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_tenant', p_tenant, false);
    PERFORM set_config('app.current_workspace', p_workspace, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Policy generator for tenant+workspace scoped tables.
DO $$
DECLARE
    t TEXT;
    tables TEXT[] := ARRAY[
        'kb_source', 'kb_chunk', 'kb_fact',
        'chat', 'message', 'draft',
        'routine', 'routine_run', 'gold_candidate',
        'usage_record',
        'mail_message', 'mail_outbox', 'email_account',
        'audit_log', 'editorial_history', 'workspace_smtp_config'
    ];
BEGIN
    FOREACH t IN ARRAY tables
    LOOP
        EXECUTE format(
            'CREATE POLICY tenant_workspace_policy ON %I
             USING (tenant_id = current_setting(''app.current_tenant'')::TEXT
                    AND workspace_id = current_setting(''app.current_workspace'')::TEXT);',
            t
        );
    END LOOP;
END;
$$;

-- workspace is special: it is the table that defines workspaces, so the policy
-- filters by tenant only. System/bootstrap operations use tenant_id='__system__'.
CREATE POLICY tenant_workspace_policy ON workspace
    USING (tenant_id = current_setting('app.current_tenant')::TEXT);

-- Grant required privileges to the app user (replace 'faberloom_app' if needed).
-- The migrator owns the tables; the app user uses them via RLS.
GRANT USAGE ON SCHEMA public TO faberloom_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO faberloom_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO faberloom_app;

-- The app user must not bypass RLS. This is a safety assertion; the command
-- will fail if the user was accidentally granted BYPASS RLS.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'faberloom_app' AND rolbypassrls = true
    ) THEN
        RAISE EXCEPTION 'faberloom_app has BYPASS RLS; this is not allowed';
    END IF;
END;
$$;
