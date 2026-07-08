-- Postgres RLS policies for FaberLoom E3-1.
-- Run as the migrator/owner user after creating tables and the app user.
-- The application user (faberloom_app by default) must NOT have BYPASS RLS.
--
-- Usage:
--   psql postgresql://migrator:pass@localhost:5432/faberloom \
--     -v app_user=faberloom_app \
--     -f app/scripts/postgres_rls_policies.sql
--
-- The script is idempotent: it drops and recreates policies so it can be
-- re-applied after schema changes.

-- ---------------------------------------------------------------------------
-- 1. Application role
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    v_app_user TEXT := COALESCE(current_setting('app_user', true), 'faberloom_app');
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = v_app_user) THEN
        EXECUTE format(
            'CREATE ROLE %I NOLOGIN NOBYPASSRLS NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT',
            v_app_user
        );
    ELSE
        -- Make sure an existing role is not accidentally set to bypass RLS.
        EXECUTE format('ALTER ROLE %I NOBYPASSRLS', v_app_user);
    END IF;
END
$$;

-- ---------------------------------------------------------------------------
-- 2. Scope helpers
-- ---------------------------------------------------------------------------
-- The application adapter must call set_app_scope(tenant_id, workspace_id)
-- at the beginning of every request/transaction. The values live for the
-- duration of the database session (use SET LOCAL in the app if you want
-- transaction-scoped values).
CREATE OR REPLACE FUNCTION set_app_scope(p_tenant TEXT, p_workspace TEXT)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_tenant', p_tenant, false);
    PERFORM set_config('app.current_workspace', p_workspace, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION set_app_tenant(p_tenant TEXT)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_tenant', p_tenant, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ---------------------------------------------------------------------------
-- 3. Enable RLS on workspace-owned and tenant-scoped tables
-- ---------------------------------------------------------------------------
ALTER TABLE workspace ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace FORCE ROW LEVEL SECURITY;
ALTER TABLE kb_source ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_source FORCE ROW LEVEL SECURITY;
ALTER TABLE kb_chunk ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_chunk FORCE ROW LEVEL SECURITY;
ALTER TABLE kb_fact ENABLE ROW LEVEL SECURITY;
ALTER TABLE kb_fact FORCE ROW LEVEL SECURITY;
ALTER TABLE chat ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat FORCE ROW LEVEL SECURITY;
ALTER TABLE message ENABLE ROW LEVEL SECURITY;
ALTER TABLE message FORCE ROW LEVEL SECURITY;
ALTER TABLE draft ENABLE ROW LEVEL SECURITY;
ALTER TABLE draft FORCE ROW LEVEL SECURITY;
ALTER TABLE routine ENABLE ROW LEVEL SECURITY;
ALTER TABLE routine FORCE ROW LEVEL SECURITY;
ALTER TABLE routine_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE routine_run FORCE ROW LEVEL SECURITY;
ALTER TABLE gold_candidate ENABLE ROW LEVEL SECURITY;
ALTER TABLE gold_candidate FORCE ROW LEVEL SECURITY;
ALTER TABLE usage_record ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_record FORCE ROW LEVEL SECURITY;
ALTER TABLE mail_message ENABLE ROW LEVEL SECURITY;
ALTER TABLE mail_message FORCE ROW LEVEL SECURITY;
ALTER TABLE mail_outbox ENABLE ROW LEVEL SECURITY;
ALTER TABLE mail_outbox FORCE ROW LEVEL SECURITY;
ALTER TABLE email_account ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_account FORCE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log FORCE ROW LEVEL SECURITY;
ALTER TABLE editorial_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE editorial_history FORCE ROW LEVEL SECURITY;
ALTER TABLE workspace_smtp_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_smtp_config FORCE ROW LEVEL SECURITY;
ALTER TABLE workspace_routing_policy ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_routing_policy FORCE ROW LEVEL SECURITY;
ALTER TABLE workspace_model_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE workspace_model_catalog FORCE ROW LEVEL SECURITY;
ALTER TABLE routing_preset ENABLE ROW LEVEL SECURITY;
ALTER TABLE routing_preset FORCE ROW LEVEL SECURITY;
ALTER TABLE manual_invoice ENABLE ROW LEVEL SECURITY;
ALTER TABLE manual_invoice FORCE ROW LEVEL SECURITY;
ALTER TABLE payment_reconciliation ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_reconciliation FORCE ROW LEVEL SECURITY;
ALTER TABLE ambient_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambient_config FORCE ROW LEVEL SECURITY;
ALTER TABLE ambient_workspace_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambient_workspace_config FORCE ROW LEVEL SECURITY;
ALTER TABLE ambient_detector ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambient_detector FORCE ROW LEVEL SECURITY;
ALTER TABLE ambient_cycle ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambient_cycle FORCE ROW LEVEL SECURITY;
ALTER TABLE ambient_detector_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambient_detector_run FORCE ROW LEVEL SECURITY;
ALTER TABLE ambient_proposal ENABLE ROW LEVEL SECURITY;
ALTER TABLE ambient_proposal FORCE ROW LEVEL SECURITY;
ALTER TABLE object ENABLE ROW LEVEL SECURITY;
ALTER TABLE object FORCE ROW LEVEL SECURITY;

-- refresh_tokens is intentionally left out of RLS in E3-1: it is globally
-- scoped by user_id today and will receive a tenant_id column in E3-2.

-- ---------------------------------------------------------------------------
-- 4. Drop existing policies so the script can be re-applied safely
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    rec RECORD;
BEGIN
    FOR rec IN
        SELECT schemaname, tablename, policyname
        FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename IN (
              'workspace', 'kb_source', 'kb_chunk', 'kb_fact', 'chat', 'message',
              'draft', 'routine', 'routine_run', 'gold_candidate', 'usage_record',
              'mail_message', 'mail_outbox', 'email_account', 'audit_log',
              'editorial_history', 'workspace_smtp_config', 'workspace_routing_policy',
              'workspace_model_catalog', 'routing_preset', 'manual_invoice', 'payment_reconciliation',
              'ambient_config', 'ambient_workspace_config',
              'ambient_detector', 'ambient_cycle', 'ambient_detector_run',
              'ambient_proposal', 'object'
          )
    LOOP
        EXECUTE format(
            'DROP POLICY IF EXISTS %I ON %I.%I',
            rec.policyname, rec.schemaname, rec.tablename
        );
    END LOOP;
END
$$;

-- ---------------------------------------------------------------------------
-- 5. Helper to create tenant+workspace policies
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION _create_tenant_workspace_policy(p_table TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format(
        'CREATE POLICY tenant_workspace_policy ON %I
         FOR ALL
         USING (
             tenant_id = current_setting(''app.current_tenant'', true)
             AND workspace_id = current_setting(''app.current_workspace'', true)
         )
         WITH CHECK (
             tenant_id = current_setting(''app.current_tenant'', true)
             AND workspace_id = current_setting(''app.current_workspace'', true)
         )',
        p_table
    );
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------------
-- 6. Workspace-owned tables: tenant + workspace
-- ---------------------------------------------------------------------------
SELECT _create_tenant_workspace_policy('kb_source');
SELECT _create_tenant_workspace_policy('kb_chunk');
SELECT _create_tenant_workspace_policy('kb_fact');
SELECT _create_tenant_workspace_policy('chat');
SELECT _create_tenant_workspace_policy('message');
SELECT _create_tenant_workspace_policy('draft');
SELECT _create_tenant_workspace_policy('routine');
SELECT _create_tenant_workspace_policy('routine_run');
SELECT _create_tenant_workspace_policy('gold_candidate');
SELECT _create_tenant_workspace_policy('usage_record');
SELECT _create_tenant_workspace_policy('mail_message');
SELECT _create_tenant_workspace_policy('mail_outbox');
SELECT _create_tenant_workspace_policy('email_account');
SELECT _create_tenant_workspace_policy('audit_log');
SELECT _create_tenant_workspace_policy('editorial_history');
SELECT _create_tenant_workspace_policy('workspace_smtp_config');
SELECT _create_tenant_workspace_policy('workspace_routing_policy');
SELECT _create_tenant_workspace_policy('workspace_model_catalog');
SELECT _create_tenant_workspace_policy('ambient_workspace_config');
SELECT _create_tenant_workspace_policy('ambient_proposal');
SELECT _create_tenant_workspace_policy('object');

-- ---------------------------------------------------------------------------
-- 7. Special workspace-owned tables with optional workspace_id
-- ---------------------------------------------------------------------------
-- ambient_cycle and ambient_detector_run may have a NULL workspace_id for
-- tenant-global cycles/detector runs. The policy still filters by tenant and,
-- when workspace_id is set, by workspace.
CREATE POLICY tenant_workspace_policy ON ambient_cycle
    FOR ALL
    USING (
        tenant_id = current_setting('app.current_tenant', true)
        AND (
            workspace_id IS NULL
            OR workspace_id = current_setting('app.current_workspace', true)
        )
    )
    WITH CHECK (
        tenant_id = current_setting('app.current_tenant', true)
        AND (
            workspace_id IS NULL
            OR workspace_id = current_setting('app.current_workspace', true)
        )
    );

CREATE POLICY tenant_workspace_policy ON ambient_detector_run
    FOR ALL
    USING (
        tenant_id = current_setting('app.current_tenant', true)
        AND (
            workspace_id IS NULL
            OR workspace_id = current_setting('app.current_workspace', true)
        )
    )
    WITH CHECK (
        tenant_id = current_setting('app.current_tenant', true)
        AND (
            workspace_id IS NULL
            OR workspace_id = current_setting('app.current_workspace', true)
        )
    );

-- ---------------------------------------------------------------------------
-- 8. Tenant-scoped tables (no workspace_id)
-- ---------------------------------------------------------------------------
CREATE POLICY tenant_policy ON routing_preset
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_policy ON manual_invoice
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_policy ON payment_reconciliation
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_policy ON ambient_config
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

CREATE POLICY tenant_policy ON ambient_detector
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

-- ---------------------------------------------------------------------------
-- 9. workspace table
-- ---------------------------------------------------------------------------
-- workspace is special: it is the table that defines workspaces, so the policy
-- filters by tenant only. System/bootstrap operations use the same helper with
-- the real tenant_id (no magic sentinel).
CREATE POLICY tenant_workspace_policy ON workspace
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

-- ---------------------------------------------------------------------------
-- 10. Grants to the app user
-- ---------------------------------------------------------------------------
-- The migrator owns the tables; the app user uses them via RLS.
DO $$
DECLARE
    v_app_user TEXT := COALESCE(current_setting('app_user', true), 'faberloom_app');
BEGIN
    EXECUTE format('GRANT USAGE ON SCHEMA public TO %I', v_app_user);
    EXECUTE format('GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO %I', v_app_user);
    EXECUTE format('GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO %I', v_app_user);
END
$$;

-- ---------------------------------------------------------------------------
-- 11. Safety assertion: the app user must not bypass RLS
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    v_app_user TEXT := COALESCE(current_setting('app_user', true), 'faberloom_app');
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = v_app_user AND rolbypassrls = true
    ) THEN
        RAISE EXCEPTION '% has BYPASS RLS; this is not allowed', v_app_user;
    END IF;
END
$$;
