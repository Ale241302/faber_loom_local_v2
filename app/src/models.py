"""SQLite schema migrations and Pydantic v2 API models for FaberLoom SL0."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SCHEMA_VERSION = 27
CURRENT_SCHEMA_VERSION = SCHEMA_VERSION


_ROUTINE_CATEGORIES = frozenset({"skill", "agent", "template", "reference", "custom"})
_PROVIDER_SLUGS_FOR_PRESET = frozenset({"openai", "anthropic", "google", "kimi", "ollama"})


def _detect_dangerous(content: str) -> list[str]:
    """Return dangerous patterns found in user-authored prompt content."""

    dangers: list[str] = []
    lowered = content.lower()
    if "<script" in lowered:
        dangers.append("HTML <script> tag")
    if re.search(r"javascript\s*:", lowered):
        dangers.append("javascript: scheme")
    if re.search(r"(?:^|\s)import\s+", content):
        dangers.append("Python import statement")
    if re.search(r"\beval\s*\(", content):
        dangers.append("eval() call")
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("=") and "!" in stripped:
            dangers.append("Excel formula injection")
            break
    return dangers


def _must_be_json_array_of_strings(value: str, field_name: str) -> str:
    """Validate that a string field holds a JSON array of non-empty strings."""

    stripped = value.strip()
    if not stripped:
        return "[]"
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field_name} must be valid JSON: {exc}") from exc
    if not isinstance(parsed, list):
        raise ValueError(f"{field_name} must be a JSON array")
    if len(parsed) > 100:
        raise ValueError(f"{field_name} may not contain more than 100 entries")
    if not all(isinstance(item, str) and item.strip() for item in parsed):
        raise ValueError(f"{field_name} must contain only non-empty strings")
    # Wildcard '*' must be the only entry to keep the allowlist unambiguous.
    if "*" in parsed and len(parsed) > 1:
        raise ValueError(f"{field_name}: wildcard '*' must be the only entry")
    return stripped


def _validate_preset_id(value: str | None) -> str | None:
    """Validate that a preset_id is in 'provider:model' format with a known provider
    and a model that appears in the allowlist for that provider.
    """

    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    if ":" not in stripped:
        raise ValueError("preset_id must be in 'provider:model' format")
    provider, model = stripped.split(":", 1)
    if not provider or not model:
        raise ValueError("preset_id must have non-empty provider and model")
    if provider not in _PROVIDER_SLUGS_FOR_PRESET:
        raise ValueError(f"Unknown provider '{provider}' in preset_id")

    # Avoid a circular import: router.cost is a leaf module.
    from .router import cost as router_cost

    allowed = router_cost.MODEL_ALLOWLIST.get(provider, set())
    if model not in allowed:
        raise ValueError(
            f"Model '{model}' is not allowed for provider '{provider}'. Allowed: {sorted(allowed)}"
        )
    return stripped


# Migration policy:
# - v1 is the original skeleton contract.
# - v11 adds UI-facing metadata for the FaberLoom Shell redesign:
#   mail_message.category, kb_source.level, gold_candidate.use_count.
# - v12 adds routine.category and hardens the routine contract for the Fase 3
#   Toolset (Agents, Skills, Context, Gold).
# - v13 enriches editorial_history with payload_json and 'provider' entity_type,
#   enabling auditable provider config changes and key removal for SL1a.
# - v14 closes SL1b HITL metrics: draft.original_body_md and draft.edit_pct
#   so the CLOSER loop can report edit_pct (approved vs original).
# - v15 closes SL2a/b/c: workspace parent_id/inherits_kb, tenant_id on
#   kb_chunk/kb_fact, enabling multi-tenant isolation and KB inheritance.
# - v16 closes SL3b/c: tenant_id on gold_candidate, task_type on routine_run,
#   enabling per-task HITL metrics and tenant-scoped gold evidence.
# - v17 closes SL3.5: workspace.confidential flag enabling SQLCipher-backed
#   per-workspace confidential databases and hardened seal exposure.
# - v22 adds correlation_id to audit_log for E2-0 audit event correlation.
# - v2 hardens the contract-first seams required before closing SL0:
#   routine/routine_run and a uniform latent-field surface.
# - v3 adds SL1a chat router support: usage_record table with latent fields.
# - v4 hardens SL1a audit/cost seams: usage_record.chat_id, attempts_json,
#   model allowlist, accumulated budget cap, and pricing version.
# - v5 adds SL1b KB + draft support: kb_chunk, kb_fact, kb_chunk_fts, and a
#   workspace-scoped draft table with HITL fields (blockers, warnings, approved_by).
# - v6 adds SL2 robust ingestion: pdf/xlsx source types, workspace seal_id, and
#   source file metadata.
# - v7 adds SL2 field aliases, parser_version/source_sheet tracking, and
#   workspace-level synonym maps.
# - v8 adds SL3/SL3.5/SL5/SL4 seams: workspace HMAC seal, mail_message and
#   gold_candidate tables; enables skill runs, IMAP connector and desktop
#   packaging contracts.
# - v9 closes fugu P0 HITL gaps for destructive actions and mail send:
#   mail_outbox idempotency, confirmation tokens, and explicit approval gating.
# - v10 enriches WorkLoom + gold loop: urgency/reason on draft and routine_run,
#   editorial_history audit seam, and gold candidate apply-to-routine feedback.
MIGRATIONS: dict[int, str] = {
    1: """
    CREATE TABLE IF NOT EXISTS workspace (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        slug TEXT NOT NULL UNIQUE,
        tenant_id TEXT,
        user_id TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS kb_source (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        content_text TEXT,
        content_blob BLOB,
        meta_json TEXT NOT NULL DEFAULT '{}',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT NOT NULL DEFAULT 'v1',
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS chat (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        title TEXT NOT NULL,
        model_preset TEXT NOT NULL DEFAULT 'default',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS message (
        id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        role TEXT NOT NULL CHECK (role IN ('system', 'user', 'assistant', 'tool')),
        content_json TEXT NOT NULL,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS draft (
        id TEXT PRIMARY KEY,
        chat_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        status TEXT NOT NULL CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected', 'exported')),
        content_json TEXT NOT NULL,
        sources_json TEXT NOT NULL DEFAULT '[]',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        approved_by TEXT,
        approved_at TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        action TEXT NOT NULL,
        payload_json TEXT NOT NULL DEFAULT '{}',
        approved_by TEXT,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 1,
        source_version TEXT,
        correlation_id TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_kb_source_workspace_id ON kb_source(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_chat_workspace_id ON chat(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_message_chat_id ON message(chat_id);
    CREATE INDEX IF NOT EXISTS idx_draft_chat_id ON draft(chat_id);
    CREATE INDEX IF NOT EXISTS idx_audit_log_workspace_id ON audit_log(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_audit_log_correlation ON audit_log(workspace_id, correlation_id);
    """,
    22: """
    -- E2-0: correlation of audit events for routines, runs, and gold candidates.
    -- Column addition is performed by _migrate_v22_correlation_id in db.py so the
    -- migration stays idempotent when the schema-base (v1) already created it.
    CREATE INDEX IF NOT EXISTS idx_audit_log_correlation ON audit_log(workspace_id, correlation_id);
    """,
    2: """
    ALTER TABLE workspace ADD COLUMN actor_id TEXT;
    ALTER TABLE workspace ADD COLUMN actor_role_at_decision TEXT;
    ALTER TABLE workspace ADD COLUMN routine_version TEXT;
    ALTER TABLE workspace ADD COLUMN skill_version TEXT;
    ALTER TABLE workspace ADD COLUMN source_version TEXT;
    ALTER TABLE workspace ADD COLUMN approved_by TEXT;

    ALTER TABLE kb_source ADD COLUMN actor_id TEXT;
    ALTER TABLE kb_source ADD COLUMN actor_role_at_decision TEXT;
    ALTER TABLE kb_source ADD COLUMN approved_by TEXT;

    ALTER TABLE chat ADD COLUMN actor_id TEXT;
    ALTER TABLE chat ADD COLUMN actor_role_at_decision TEXT;
    ALTER TABLE chat ADD COLUMN approved_by TEXT;

    ALTER TABLE message ADD COLUMN workspace_id TEXT;
    ALTER TABLE message ADD COLUMN approved_by TEXT;

    CREATE TABLE IF NOT EXISTS routine (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        name TEXT NOT NULL,
        skill_md TEXT NOT NULL DEFAULT '',
        tools_allowlist TEXT NOT NULL DEFAULT '[]',
        schema_output_json TEXT NOT NULL DEFAULT '{}',
        preset_id TEXT,
        trigger_json TEXT NOT NULL DEFAULT '{}',
        persona_md TEXT NOT NULL DEFAULT '',
        is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 2,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS routine_run (
        id TEXT PRIMARY KEY,
        routine_id TEXT NOT NULL,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        input_json TEXT NOT NULL DEFAULT '{}',
        output_json TEXT NOT NULL DEFAULT '{}',
        evidence_json TEXT NOT NULL DEFAULT '[]',
        status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'succeeded', 'failed', 'cancelled', 'requires_hitl')),
        edit_pct REAL,
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 2,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (routine_id) REFERENCES routine(id) ON DELETE CASCADE,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    UPDATE message
    SET workspace_id = (
        SELECT chat.workspace_id FROM chat WHERE chat.id = message.chat_id
    )
    WHERE workspace_id IS NULL;

    CREATE INDEX IF NOT EXISTS idx_message_workspace_id ON message(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_routine_workspace_id ON routine(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_routine_run_workspace_id ON routine_run(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_routine_run_routine_id ON routine_run(routine_id);
    """,
    3: """
    CREATE TABLE IF NOT EXISTS usage_record (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        provider_slug TEXT NOT NULL,
        model TEXT NOT NULL,
        input_tokens INTEGER NOT NULL DEFAULT 0,
        output_tokens INTEGER NOT NULL DEFAULT 0,
        cost_usd REAL NOT NULL DEFAULT 0.0,
        duration_ms INTEGER NOT NULL DEFAULT 0,
        status TEXT NOT NULL CHECK (status IN ('succeeded', 'failed', 'budget_exceeded')),
        error TEXT,
        request_json TEXT NOT NULL DEFAULT '{}',
        response_json TEXT NOT NULL DEFAULT '{}',
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 3,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_usage_record_workspace_id ON usage_record(workspace_id);
    """,
    4: """
    ALTER TABLE usage_record ADD COLUMN chat_id TEXT;
    ALTER TABLE usage_record ADD COLUMN attempts_json TEXT NOT NULL DEFAULT '[]';

    CREATE INDEX IF NOT EXISTS idx_usage_record_chat_id ON usage_record(chat_id);
    """,
    5: """
    CREATE TABLE IF NOT EXISTS kb_chunk (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        source_id TEXT NOT NULL,
        chunk_index INTEGER NOT NULL,
        content_text TEXT NOT NULL,
        source_locator TEXT,
        source_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 5,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE,
        FOREIGN KEY (source_id) REFERENCES kb_source(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_kb_chunk_workspace_id ON kb_chunk(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_kb_chunk_source_id ON kb_chunk(source_id);

    CREATE TABLE IF NOT EXISTS kb_fact (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        source_id TEXT NOT NULL,
        entity_key TEXT NOT NULL,
        field_name TEXT NOT NULL,
        field_value TEXT NOT NULL,
        unit TEXT,
        currency TEXT,
        valid_from TEXT,
        valid_until TEXT,
        source_locator TEXT,
        source_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 5,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE,
        FOREIGN KEY (source_id) REFERENCES kb_source(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_kb_fact_workspace_id ON kb_fact(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_kb_fact_entity_key ON kb_fact(workspace_id, entity_key);

    CREATE VIRTUAL TABLE IF NOT EXISTS kb_chunk_fts USING fts5(
        content_text,
        content='kb_chunk',
        content_rowid='rowid'
    );

    CREATE TRIGGER IF NOT EXISTS kb_chunk_fts_insert AFTER INSERT ON kb_chunk BEGIN
        INSERT INTO kb_chunk_fts(rowid, content_text) VALUES (new.rowid, new.content_text);
    END;

    CREATE TRIGGER IF NOT EXISTS kb_chunk_fts_delete AFTER DELETE ON kb_chunk BEGIN
        INSERT INTO kb_chunk_fts(kb_chunk_fts, rowid, content_text) VALUES ('delete', old.rowid, old.content_text);
    END;

    DROP TABLE IF EXISTS draft;

    CREATE TABLE draft (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        chat_id TEXT,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        task TEXT NOT NULL DEFAULT 'draft_commercial_reply',
        subject TEXT,
        body_md TEXT NOT NULL,
        hard_facts_json TEXT NOT NULL DEFAULT '[]',
        sources_json TEXT NOT NULL DEFAULT '[]',
        blockers_json TEXT NOT NULL DEFAULT '[]',
        warnings_json TEXT NOT NULL DEFAULT '[]',
        requires_confirmation INTEGER NOT NULL DEFAULT 0 CHECK (requires_confirmation IN (0, 1)),
        status TEXT NOT NULL CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected', 'exported')),
        routine_version TEXT,
        skill_version TEXT,
        schema_version INTEGER NOT NULL DEFAULT 5,
        source_version TEXT,
        approved_by TEXT,
        approved_at TEXT,
        exported_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE,
        FOREIGN KEY (chat_id) REFERENCES chat(id) ON DELETE SET NULL
    );

    CREATE INDEX IF NOT EXISTS idx_draft_workspace_id ON draft(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_draft_chat_id ON draft(chat_id);
    CREATE INDEX IF NOT EXISTS idx_draft_status ON draft(workspace_id, status);
    """,
    6: """
    ALTER TABLE workspace ADD COLUMN seal_id TEXT;

    UPDATE workspace SET seal_id = lower(hex(randomblob(16)))
    WHERE seal_id IS NULL;

    CREATE TABLE IF NOT EXISTS _workspace_seal_backup (
        workspace_id TEXT PRIMARY KEY,
        seal_id TEXT NOT NULL
    );

    ALTER TABLE kb_source ADD COLUMN file_name TEXT;
    ALTER TABLE kb_source ADD COLUMN mime_type TEXT;
    ALTER TABLE kb_source ADD COLUMN file_size INTEGER;
    ALTER TABLE kb_fact ADD COLUMN extraction_method TEXT;

    CREATE INDEX IF NOT EXISTS idx_kb_fact_source_id ON kb_fact(source_id);
    """,
    7: """
    ALTER TABLE workspace ADD COLUMN field_aliases_json TEXT DEFAULT '{}';

    ALTER TABLE kb_source ADD COLUMN parser_version TEXT;
    ALTER TABLE kb_fact ADD COLUMN source_sheet TEXT;
    """,
    8: """
    ALTER TABLE kb_source ADD COLUMN workspace_hmac TEXT;
    ALTER TABLE kb_fact ADD COLUMN workspace_hmac TEXT;
    ALTER TABLE draft ADD COLUMN workspace_hmac TEXT;
    ALTER TABLE routine_run ADD COLUMN workspace_hmac TEXT;

    CREATE TABLE IF NOT EXISTS mail_message (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        actor_id TEXT,
        actor_role_at_decision TEXT,
        account TEXT NOT NULL,
        mail_uid TEXT NOT NULL,
        subject TEXT,
        sender TEXT,
        body_text TEXT,
        raw_payload BLOB,
        status TEXT NOT NULL CHECK (status IN ('unread','drafted','approved','sent','rejected')),
        draft_id TEXT,
        schema_version INTEGER NOT NULL DEFAULT 8,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE,
        FOREIGN KEY (draft_id) REFERENCES draft(id) ON DELETE SET NULL,
        UNIQUE(workspace_id, account, mail_uid)
    );

    CREATE INDEX IF NOT EXISTS idx_mail_message_workspace_id ON mail_message(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_mail_message_status ON mail_message(workspace_id, status);

    CREATE TABLE IF NOT EXISTS gold_candidate (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        routine_id TEXT NOT NULL,
        run_id TEXT NOT NULL UNIQUE,
        edit_pct REAL,
        input_json TEXT NOT NULL DEFAULT '{}',
        output_json TEXT NOT NULL DEFAULT '{}',
        learned_output_json TEXT NOT NULL DEFAULT '{}',
        approved INTEGER NOT NULL DEFAULT 0 CHECK (approved IN (0, 1)),
        schema_version INTEGER NOT NULL DEFAULT 8,
        source_version TEXT,
        approved_by TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE,
        FOREIGN KEY (routine_id) REFERENCES routine(id) ON DELETE CASCADE,
        FOREIGN KEY (run_id) REFERENCES routine_run(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_gold_candidate_workspace_id ON gold_candidate(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_gold_candidate_routine_id ON gold_candidate(routine_id);
    """,
    9: """
    CREATE TABLE IF NOT EXISTS mail_outbox (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        mail_id TEXT NOT NULL,
        idempotency_key TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('pending','sending','sent','failed')),
        smtp_message_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE,
        FOREIGN KEY (mail_id) REFERENCES mail_message(id) ON DELETE CASCADE,
        UNIQUE(workspace_id, mail_id),
        UNIQUE(workspace_id, idempotency_key)
    );

    CREATE INDEX IF NOT EXISTS idx_mail_outbox_workspace_id ON mail_outbox(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_mail_outbox_mail_id ON mail_outbox(mail_id);
    """,
    10: """
    ALTER TABLE routine_run ADD COLUMN urgency INTEGER DEFAULT 0;
    ALTER TABLE routine_run ADD COLUMN reason TEXT;

    ALTER TABLE draft ADD COLUMN urgency INTEGER DEFAULT 0;
    ALTER TABLE draft ADD COLUMN reason TEXT;

    ALTER TABLE gold_candidate ADD COLUMN used INTEGER DEFAULT 0 CHECK (used IN (0, 1));

    CREATE TABLE IF NOT EXISTS editorial_history (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        entity_type TEXT NOT NULL CHECK(entity_type IN ('draft','routine_run','gold_candidate')),
        entity_id TEXT NOT NULL,
        action TEXT NOT NULL,
        actor_id TEXT,
        reason TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_editorial_history_entity ON editorial_history(workspace_id, entity_type, entity_id);
    """,
    11: """
    ALTER TABLE mail_message ADD COLUMN category TEXT NOT NULL DEFAULT 'other' CHECK (category IN ('rfq','seguimiento','cobranza','soporte','spam','other'));
    ALTER TABLE kb_source ADD COLUMN level INTEGER NOT NULL DEFAULT 0 CHECK (level IN (0, 1, 2, 3, 4));
    ALTER TABLE gold_candidate ADD COLUMN use_count INTEGER NOT NULL DEFAULT 0;

    UPDATE gold_candidate SET use_count = CASE WHEN used = 1 THEN 1 ELSE 0 END;

    CREATE INDEX IF NOT EXISTS idx_mail_message_category ON mail_message(workspace_id, category);
    CREATE INDEX IF NOT EXISTS idx_kb_source_level ON kb_source(workspace_id, level);
    """,
    12: """
    ALTER TABLE routine ADD COLUMN category TEXT NOT NULL DEFAULT 'custom'
        CHECK (category IN ('skill', 'agent', 'template', 'reference', 'custom'));

    UPDATE routine SET category = CASE
        WHEN source_version = 'faberloom-skill' THEN 'skill'
        WHEN source_version = 'faberloom-agent' THEN 'agent'
        WHEN source_version = 'faberloom-template' THEN 'template'
        WHEN source_version = 'faberloom-reference' THEN 'reference'
        ELSE 'custom'
    END;

    CREATE INDEX IF NOT EXISTS idx_routine_category
        ON routine(workspace_id, tenant_id, category, is_active, approved_by);
    """,
    14: """
    ALTER TABLE draft ADD COLUMN original_body_md TEXT;
    ALTER TABLE draft ADD COLUMN edit_pct REAL;
    """,
    15: """
    ALTER TABLE workspace ADD COLUMN parent_id TEXT REFERENCES workspace(id) ON DELETE SET NULL;
    ALTER TABLE workspace ADD COLUMN inherits_kb INTEGER NOT NULL DEFAULT 0 CHECK (inherits_kb IN (0, 1));

    ALTER TABLE kb_chunk ADD COLUMN tenant_id TEXT;
    ALTER TABLE kb_fact ADD COLUMN tenant_id TEXT;

    UPDATE kb_chunk
    SET tenant_id = (SELECT tenant_id FROM kb_source WHERE kb_source.id = kb_chunk.source_id)
    WHERE tenant_id IS NULL;

    UPDATE kb_fact
    SET tenant_id = (SELECT tenant_id FROM kb_source WHERE kb_source.id = kb_fact.source_id)
    WHERE tenant_id IS NULL;

    CREATE INDEX IF NOT EXISTS idx_kb_chunk_workspace_tenant ON kb_chunk(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_kb_fact_workspace_tenant ON kb_fact(workspace_id, tenant_id);
    """,
    13: """
    CREATE TABLE IF NOT EXISTS _editorial_history_v13 (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        entity_type TEXT NOT NULL CHECK(entity_type IN ('draft','routine_run','gold_candidate','provider')),
        entity_id TEXT NOT NULL,
        action TEXT NOT NULL,
        actor_id TEXT,
        reason TEXT,
        payload_json TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    INSERT INTO _editorial_history_v13
        (id, workspace_id, entity_type, entity_id, action, actor_id, reason, payload_json, created_at)
    SELECT id, workspace_id, entity_type, entity_id, action, actor_id, reason, '{}', created_at
    FROM editorial_history;

    DROP TABLE editorial_history;
    ALTER TABLE _editorial_history_v13 RENAME TO editorial_history;

    CREATE INDEX IF NOT EXISTS idx_editorial_history_entity
        ON editorial_history(workspace_id, entity_type, entity_id);
    """,
    16: """
    ALTER TABLE gold_candidate ADD COLUMN tenant_id TEXT;
    ALTER TABLE routine_run ADD COLUMN task_type TEXT;

    UPDATE gold_candidate
    SET tenant_id = (
        SELECT routine.tenant_id FROM routine WHERE routine.id = gold_candidate.routine_id
    )
    WHERE tenant_id IS NULL;

    CREATE INDEX IF NOT EXISTS idx_gold_candidate_workspace_tenant
        ON gold_candidate(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_routine_run_task_type
        ON routine_run(workspace_id, tenant_id, task_type);
    """,
    17: """
    ALTER TABLE workspace ADD COLUMN confidential INTEGER NOT NULL DEFAULT 0
        CHECK (confidential IN (0, 1));
    """,
    18: """
    CREATE TABLE IF NOT EXISTS workspace_smtp_config (
        workspace_id TEXT PRIMARY KEY REFERENCES workspace(id) ON DELETE CASCADE,
        host TEXT NOT NULL,
        port INTEGER NOT NULL,
        use_ssl INTEGER NOT NULL DEFAULT 1,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        from_email TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """,
    19: """
    -- Migrate workspace_smtp_config from workspace-scoped to (workspace, user).
    ALTER TABLE workspace_smtp_config RENAME TO _workspace_smtp_config_v18;

    CREATE TABLE workspace_smtp_config (
        workspace_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        host TEXT NOT NULL,
        port INTEGER NOT NULL,
        use_ssl INTEGER NOT NULL DEFAULT 1,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        from_email TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (workspace_id, user_id),
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    -- Data backfill is performed by _migrate_v19_data in db.py because the
    -- target user_id must be read from the FABERLOOM_USERS environment variable.
    """,
    20: """
    -- SL5 Phase 1: per-workspace IMAP accounts, encrypted credentials,
    -- outbox retry tracking, and workspace email signature.

    CREATE TABLE IF NOT EXISTS email_account (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL,
        tenant_id TEXT,
        user_id TEXT,
        label TEXT,
        provider TEXT NOT NULL DEFAULT 'imap',
        host TEXT NOT NULL,
        port INTEGER NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        folders_json TEXT NOT NULL DEFAULT '["INBOX"]',
        auth_type TEXT NOT NULL DEFAULT 'password' CHECK (auth_type IN ('password', 'oauth')),
        read_only INTEGER NOT NULL DEFAULT 1,
        is_default INTEGER NOT NULL DEFAULT 0,
        schema_version INTEGER NOT NULL DEFAULT 20,
        source_version TEXT NOT NULL DEFAULT 'v1',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (workspace_id) REFERENCES workspace(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_email_account_workspace_id ON email_account(workspace_id);
    CREATE INDEX IF NOT EXISTS idx_email_account_default ON email_account(workspace_id, is_default);

    ALTER TABLE mail_message ADD COLUMN account_id TEXT REFERENCES email_account(id) ON DELETE SET NULL;
    CREATE INDEX IF NOT EXISTS idx_mail_message_account_id ON mail_message(account_id);

    ALTER TABLE mail_outbox ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE mail_outbox ADD COLUMN failed_at TEXT;
    ALTER TABLE mail_outbox ADD COLUMN error_json TEXT NOT NULL DEFAULT '{}';

    ALTER TABLE workspace ADD COLUMN email_signature TEXT;
    """,
    21: """
    -- P0 fugu hardening: refresh tokens, fail-closed tenant_id, and missing
    -- tenant columns on workspace-owned tables.

    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        token_hash TEXT NOT NULL UNIQUE,
        expires_at TEXT NOT NULL,
        revoked_at TEXT,
        created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user ON refresh_tokens(user_id, revoked_at, expires_at);

    -- Add tenant_id to tables that did not have it.
    ALTER TABLE workspace_smtp_config ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'default';
    ALTER TABLE mail_outbox ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'default';
    ALTER TABLE editorial_history ADD COLUMN tenant_id TEXT NOT NULL DEFAULT 'default';

    -- Backfill existing rows and enforce NOT NULL behavior via triggers.
    UPDATE workspace SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE kb_source SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE chat SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE message SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE draft SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE routine SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE routine_run SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE usage_record SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE mail_message SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE email_account SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE kb_chunk SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE kb_fact SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE gold_candidate SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE audit_log SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE workspace_smtp_config SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE mail_outbox SET tenant_id = 'default' WHERE tenant_id IS NULL;
    UPDATE editorial_history SET tenant_id = 'default' WHERE tenant_id IS NULL;

    CREATE TRIGGER IF NOT EXISTS trg_workspace_tenant_nn BEFORE INSERT ON workspace
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_workspace_tenant_nn_upd BEFORE UPDATE ON workspace
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_kb_source_tenant_nn BEFORE INSERT ON kb_source
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_kb_source_tenant_nn_upd BEFORE UPDATE ON kb_source
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_chat_tenant_nn BEFORE INSERT ON chat
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_chat_tenant_nn_upd BEFORE UPDATE ON chat
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_message_tenant_nn BEFORE INSERT ON message
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_message_tenant_nn_upd BEFORE UPDATE ON message
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_draft_tenant_nn BEFORE INSERT ON draft
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_draft_tenant_nn_upd BEFORE UPDATE ON draft
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_routine_tenant_nn BEFORE INSERT ON routine
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_routine_tenant_nn_upd BEFORE UPDATE ON routine
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_routine_run_tenant_nn BEFORE INSERT ON routine_run
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_routine_run_tenant_nn_upd BEFORE UPDATE ON routine_run
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_usage_record_tenant_nn BEFORE INSERT ON usage_record
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_usage_record_tenant_nn_upd BEFORE UPDATE ON usage_record
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_mail_message_tenant_nn BEFORE INSERT ON mail_message
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_mail_message_tenant_nn_upd BEFORE UPDATE ON mail_message
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_email_account_tenant_nn BEFORE INSERT ON email_account
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_email_account_tenant_nn_upd BEFORE UPDATE ON email_account
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_kb_chunk_tenant_nn BEFORE INSERT ON kb_chunk
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_kb_chunk_tenant_nn_upd BEFORE UPDATE ON kb_chunk
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_kb_fact_tenant_nn BEFORE INSERT ON kb_fact
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_kb_fact_tenant_nn_upd BEFORE UPDATE ON kb_fact
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_gold_candidate_tenant_nn BEFORE INSERT ON gold_candidate
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_gold_candidate_tenant_nn_upd BEFORE UPDATE ON gold_candidate
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_audit_log_tenant_nn BEFORE INSERT ON audit_log
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_audit_log_tenant_nn_upd BEFORE UPDATE ON audit_log
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_workspace_smtp_config_tenant_nn BEFORE INSERT ON workspace_smtp_config
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_workspace_smtp_config_tenant_nn_upd BEFORE UPDATE ON workspace_smtp_config
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_mail_outbox_tenant_nn BEFORE INSERT ON mail_outbox
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_mail_outbox_tenant_nn_upd BEFORE UPDATE ON mail_outbox
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_editorial_history_tenant_nn BEFORE INSERT ON editorial_history
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;
    CREATE TRIGGER IF NOT EXISTS trg_editorial_history_tenant_nn_upd BEFORE UPDATE ON editorial_history
        BEGIN SELECT CASE WHEN NEW.tenant_id IS NULL THEN RAISE(ABORT, 'tenant_id is required') END; END;

    CREATE INDEX IF NOT EXISTS idx_workspace_tenant ON workspace(tenant_id);
    CREATE INDEX IF NOT EXISTS idx_kb_source_tenant ON kb_source(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_chat_tenant ON chat(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_message_tenant ON message(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_draft_tenant ON draft(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_routine_tenant ON routine(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_routine_run_tenant ON routine_run(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_usage_record_tenant ON usage_record(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_mail_message_tenant ON mail_message(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_email_account_tenant ON email_account(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_kb_chunk_tenant ON kb_chunk(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_kb_fact_tenant ON kb_fact(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_gold_candidate_tenant ON gold_candidate(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_audit_log_tenant ON audit_log(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_workspace_smtp_config_tenant ON workspace_smtp_config(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_mail_outbox_tenant ON mail_outbox(workspace_id, tenant_id);
    CREATE INDEX IF NOT EXISTS idx_editorial_history_tenant ON editorial_history(workspace_id, tenant_id);
    """,
    23: """
    -- E2-0/E2-3: permanent canary tenant gate.
    -- Mark one workspace as the canary so isolation tests have a persistent,
    -- recognizable row that survives reseeds and cannot be confused with
    -- production tenants.
    ALTER TABLE workspace ADD COLUMN is_canary INTEGER NOT NULL DEFAULT 0
        CHECK (is_canary IN (0, 1));

    UPDATE workspace SET is_canary = 1 WHERE slug = 'canary';

    CREATE INDEX IF NOT EXISTS idx_workspace_is_canary ON workspace(tenant_id, is_canary);
    """,
    24: """
    -- E2-0/E2-2: second gate gold — record the independent verifier.
    ALTER TABLE gold_candidate ADD COLUMN verified_by TEXT;
    """,
    25: """
    -- E2-2: formal closure of SL5 mail connector for shared instance.
    -- Mark credentials as app-passwords and track IMAP credential rotation.
    ALTER TABLE email_account ADD COLUMN is_app_password INTEGER NOT NULL DEFAULT 0
        CHECK (is_app_password IN (0, 1));
    ALTER TABLE email_account ADD COLUMN rotated_at TEXT;
    ALTER TABLE workspace_smtp_config ADD COLUMN is_app_password INTEGER NOT NULL DEFAULT 0
        CHECK (is_app_password IN (0, 1));
    """,
    26: """
    -- E2-3: explicit gold candidate states and role tracking.
    ALTER TABLE gold_candidate ADD COLUMN state TEXT NOT NULL DEFAULT 'candidate'
        CHECK (state IN ('candidate', 'active_l2', 'l3_pending', 'l3', 'rejected'));
    ALTER TABLE gold_candidate ADD COLUMN actor_role_at_decision TEXT;

    -- Existing promoted candidates become active_l2; the rest stay candidate.
    UPDATE gold_candidate SET state = CASE WHEN approved = 1 THEN 'active_l2' ELSE 'candidate' END;
    """,
    27: """
    -- E2-4: routing policy, model catalog, and step-aware cost ledger.
    CREATE TABLE IF NOT EXISTS workspace_routing_policy (
        workspace_id TEXT PRIMARY KEY REFERENCES workspace(id) ON DELETE CASCADE,
        tenant_id TEXT NOT NULL,
        provider_allowlist_json TEXT NOT NULL DEFAULT '[]',
        model_allowlist_json TEXT NOT NULL DEFAULT '{}',
        budget_cap_usd REAL NOT NULL DEFAULT 5.0 CHECK (budget_cap_usd >= 0),
        auto_mode_enabled INTEGER NOT NULL DEFAULT 0 CHECK (auto_mode_enabled IN (0, 1)),
        max_auto_steps INTEGER NOT NULL DEFAULT 3 CHECK (max_auto_steps BETWEEN 1 AND 10),
        require_local_only INTEGER NOT NULL DEFAULT 0 CHECK (require_local_only IN (0, 1)),
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS workspace_model_catalog (
        id TEXT PRIMARY KEY,
        workspace_id TEXT NOT NULL REFERENCES workspace(id) ON DELETE CASCADE,
        tenant_id TEXT NOT NULL,
        provider_slug TEXT NOT NULL,
        model TEXT NOT NULL,
        capabilities_json TEXT NOT NULL DEFAULT '["text"]',
        is_enabled INTEGER NOT NULL DEFAULT 1 CHECK (is_enabled IN (0, 1)),
        priority INTEGER NOT NULL DEFAULT 100,
        cost_input_1k REAL NOT NULL DEFAULT 0.0,
        cost_output_1k REAL NOT NULL DEFAULT 0.0,
        is_local INTEGER NOT NULL DEFAULT 0 CHECK (is_local IN (0, 1)),
        is_managed INTEGER NOT NULL DEFAULT 0 CHECK (is_managed IN (0, 1)),
        source_version TEXT NOT NULL DEFAULT 'v1',
        created_at TEXT NOT NULL,
        UNIQUE(workspace_id, provider_slug, model)
    );
    CREATE INDEX IF NOT EXISTS idx_workspace_model_catalog_ws
        ON workspace_model_catalog(workspace_id, is_enabled, is_local);

    ALTER TABLE usage_record ADD COLUMN run_id TEXT;
    ALTER TABLE usage_record ADD COLUMN step_index INTEGER;
    ALTER TABLE usage_record ADD COLUMN chain_id TEXT;
    ALTER TABLE usage_record ADD COLUMN capability TEXT;
    CREATE INDEX IF NOT EXISTS idx_usage_record_chain
        ON usage_record(workspace_id, tenant_id, chain_id, step_index);
    """,
}


class HealthRead(BaseModel):
    status: Literal["ok"] = "ok"
    app: str = "FaberLoom"
    schema_version: int
    database_path: str


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=140)
    parent_id: str | None = Field(default=None, max_length=120)
    inherits_kb: int = Field(default=0, ge=0, le=1)
    confidential: int = Field(default=0, ge=0, le=1)
    passphrase: str | None = Field(default=None, max_length=200)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Workspace name cannot be blank")
        return stripped

    @field_validator("slug")
    @classmethod
    def slug_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("Workspace slug cannot be blank")
        return stripped


class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    field_aliases_json: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    parent_id: str | None = None
    inherits_kb: int = 0
    confidential: int = 0
    email_signature: str | None = None
    is_canary: int = 0
    created_at: str
    updated_at: str


class UserRead(BaseModel):
    email: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    role: str | None = None
    roles: list[str] = Field(default_factory=list)
    foundation_resolved: bool = False


class WorkspaceFieldAliasesUpdate(BaseModel):
    aliases: dict[str, list[str]] = Field(default_factory=dict)

    @field_validator("aliases")
    @classmethod
    def aliases_must_be_simple_strings(cls, value: dict[str, list[str]]) -> dict[str, list[str]]:
        for key, targets in value.items():
            if not key.strip():
                raise ValueError("Alias key cannot be blank")
            if not isinstance(targets, list) or not all(isinstance(t, str) and t.strip() for t in targets):
                raise ValueError(f"Alias '{key}' must map to a list of non-empty strings")
        return value


class WorkspaceListRead(BaseModel):
    workspaces: list[WorkspaceRead]


class AuditEvent(BaseModel):
    id: str
    workspace_id: str
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    action: str
    payload: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str | None = None
    user_id: str | None = None
    approved_by: str | None = None
    schema_version: int = SCHEMA_VERSION
    routine_version: str | None = None
    skill_version: str | None = None
    source_version: str | None = None
    correlation_id: str | None = None
    created_at: str


class RoutineRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    name: str
    skill_md: str
    tools_allowlist: str
    schema_output_json: str
    preset_id: str | None = None
    trigger_json: str
    persona_md: str
    is_active: int
    category: str
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
    updated_at: str


class RoutineRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    routine_id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    input_json: str
    output_json: str
    evidence_json: str
    status: str
    edit_pct: float | None = None
    task_type: str | None = None
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    urgency: int = 0
    reason: str | None = None
    created_at: str


class RoutineCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    skill_md: str = Field(default="", max_length=50000)
    tools_allowlist: str = Field(default="[]", max_length=2000)
    schema_output_json: str = Field(default="{}", max_length=10000)
    preset_id: str | None = Field(default=None, max_length=120)
    trigger_json: str = Field(default="{}", max_length=10000)
    persona_md: str = Field(default="", max_length=20000)
    is_active: int = Field(default=1, ge=0, le=1)
    source_version: str = Field(default="v1", min_length=1, max_length=120)
    skill_version: str | None = Field(default=None, max_length=120)
    category: str = Field(default="custom", max_length=20)

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, value: str) -> str:
        if value not in _ROUTINE_CATEGORIES:
            raise ValueError(f"Invalid routine category '{value}'")
        return value

    @field_validator("tools_allowlist")
    @classmethod
    def tools_allowlist_must_be_valid(cls, value: str) -> str:
        return _must_be_json_array_of_strings(value, "tools_allowlist")

    @field_validator("trigger_json")
    @classmethod
    def trigger_json_must_be_valid(cls, value: str) -> str:
        return _must_be_json_array_of_strings(value, "trigger_json")

    @field_validator("preset_id")
    @classmethod
    def preset_id_must_be_valid(cls, value: str | None) -> str | None:
        return _validate_preset_id(value)

    @field_validator("persona_md")
    @classmethod
    def persona_md_must_be_safe(cls, value: str) -> str:
        dangers = _detect_dangerous(value)
        if dangers:
            raise ValueError("Unsafe persona_md content: " + "; ".join(dangers))
        return value

    @field_validator("schema_output_json")
    @classmethod
    def schema_output_json_must_be_valid_schema(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            return "{}"
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"schema_output_json must be valid JSON: {exc}") from exc

        # Trivial/empty schema is allowed as a no-op.
        if parsed == {}:
            return stripped

        if not isinstance(parsed, dict):
            raise ValueError("schema_output_json must be a JSON object")
        if parsed.get("type") != "object":
            raise ValueError("schema_output_json must have type='object'")
        if not isinstance(parsed.get("properties"), dict):
            raise ValueError("schema_output_json must have a 'properties' object")
        return stripped


class RoutineUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    skill_md: str | None = Field(default=None, max_length=50000)
    tools_allowlist: str | None = Field(default=None, max_length=2000)
    schema_output_json: str | None = Field(default=None, max_length=10000)
    preset_id: str | None = Field(default=None, max_length=120)
    trigger_json: str | None = Field(default=None, max_length=10000)
    persona_md: str | None = Field(default=None, max_length=20000)
    is_active: int | None = Field(default=None, ge=0, le=1)
    source_version: str | None = Field(default=None, min_length=1, max_length=120)
    skill_version: str | None = Field(default=None, max_length=120)
    category: str | None = Field(default=None, max_length=20)

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value not in _ROUTINE_CATEGORIES:
            raise ValueError(f"Invalid routine category '{value}'")
        return value

    @field_validator("tools_allowlist")
    @classmethod
    def tools_allowlist_must_be_valid(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _must_be_json_array_of_strings(value, "tools_allowlist")

    @field_validator("trigger_json")
    @classmethod
    def trigger_json_must_be_valid(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _must_be_json_array_of_strings(value, "trigger_json")

    @field_validator("preset_id")
    @classmethod
    def preset_id_must_be_valid(cls, value: str | None) -> str | None:
        return _validate_preset_id(value)

    @field_validator("persona_md")
    @classmethod
    def persona_md_must_be_safe(cls, value: str | None) -> str | None:
        if value is None:
            return None
        dangers = _detect_dangerous(value)
        if dangers:
            raise ValueError("Unsafe persona_md content: " + "; ".join(dangers))
        return value

    @field_validator("schema_output_json")
    @classmethod
    def schema_output_json_must_be_valid_schema(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            return "{}"
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"schema_output_json must be valid JSON: {exc}") from exc

        if parsed == {}:
            return stripped

        if not isinstance(parsed, dict):
            raise ValueError("schema_output_json must be a JSON object")
        if parsed.get("type") != "object":
            raise ValueError("schema_output_json must have type='object'")
        if not isinstance(parsed.get("properties"), dict):
            raise ValueError("schema_output_json must have a 'properties' object")
        return stripped


class SkillInvokeRequest(BaseModel):
    input_json: dict[str, Any] = Field(default_factory=dict)
    provider_slug: str | None = None
    model: str | None = None


class ChatInvokeRequest(BaseModel):
    routine_id: str = Field(min_length=1, max_length=120)
    user_request: str = Field(default="", max_length=20000)
    mode: Literal["manual", "auto"] = "manual"


class AtMentionInvokeRequest(BaseModel):
    routine_name: str = Field(min_length=1, max_length=120)
    user_request: str = Field(min_length=1, max_length=20000)
    provider_slug: str | None = None
    model: str | None = None


class MailMessageCreate(BaseModel):
    account: str = Field(min_length=1, max_length=300)
    mail_uid: str = Field(min_length=1, max_length=300)
    subject: str | None = Field(default=None, max_length=1000)
    sender: str | None = Field(default=None, max_length=500)
    body_text: str | None = Field(default=None, max_length=100000)
    raw_payload: bytes | None = None


class MailMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    account: str
    mail_uid: str
    subject: str | None = None
    sender: str | None = None
    body_text: str | None = None
    status: str
    category: str = "other"
    draft_id: str | None = None
    account_id: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str
    updated_at: str


class GoldCandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    routine_id: str
    run_id: str
    tenant_id: str | None = None
    edit_pct: float | None = None
    input_json: str
    output_json: str
    learned_output_json: str
    approved: int
    used: int = 0
    use_count: int = 0
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    verified_by: str | None = None
    state: str = "candidate"
    actor_role_at_decision: str | None = None
    created_at: str
    updated_at: str


class WorkLoomRead(BaseModel):
    routine_runs: list[RoutineRunRead]
    drafts: list[DraftRead]
    gold_candidates: list[GoldCandidateRead]


# -----------------------------------------------------------------------------
# SL1a: Chat + Router API models
# -----------------------------------------------------------------------------

class ChatCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Chat title cannot be blank")
        return stripped


class ChatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    title: str
    model_preset: str
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str


class ChatUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=200)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Chat title cannot be blank")
        return stripped


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    role: str
    content: str
    route: dict[str, Any] | None = None
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    created_at: str


class ChatCompletionRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    provider_slug: str | None = None
    model: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=1024, gt=0, le=4096)
    mode: Literal["manual", "auto"] = "manual"


class ChatCompletionResponse(BaseModel):
    message: MessageRead
    provider_slug: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
    chain_id: str | None = None
    steps: list[dict[str, Any]] | None = None
    mode: str | None = None


class UsageRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    chat_id: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    provider_slug: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
    status: str
    error: str | None = None
    attempts_json: str
    routine_version: str | None = None
    skill_version: str | None = None
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    run_id: str | None = None
    step_index: int | None = None
    chain_id: str | None = None
    capability: str | None = None
    created_at: str


class RouterProviderRead(BaseModel):
    provider_slug: str
    model_default: str
    configured: bool
    enabled: bool
    allowed: bool
    available: bool
    reason: str | None = None


class RouterStatusRead(BaseModel):
    providers: list[RouterProviderRead]
    budget_cap_usd: float
    spent_usd: float
    provider_allowlist: list[str] | None = None
    model_allowlist: dict[str, list[str]] | None = None
    auto_mode_enabled: bool = False
    max_auto_steps: int = 3
    require_local_only: bool = False


class WorkspaceRoutingPolicyUpdate(BaseModel):
    provider_allowlist: list[str] | None = None
    model_allowlist: dict[str, list[str]] | None = None
    budget_cap_usd: float | None = Field(default=None, ge=0.0)
    auto_mode_enabled: bool | None = None
    max_auto_steps: int | None = Field(default=None, ge=1, le=10)
    require_local_only: bool | None = None


class WorkspaceRoutingPolicyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workspace_id: str
    tenant_id: str
    provider_allowlist: list[str]
    model_allowlist: dict[str, list[str]]
    budget_cap_usd: float
    auto_mode_enabled: bool
    max_auto_steps: int
    require_local_only: bool
    updated_at: str


class ModelCatalogEntryCreate(BaseModel):
    provider_slug: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=120)
    capabilities: list[str] = Field(default_factory=lambda: ["text"])
    priority: int = Field(default=100, ge=1, le=1000)
    cost_input_1k: float = Field(default=0.0, ge=0.0)
    cost_output_1k: float = Field(default=0.0, ge=0.0)
    is_local: bool = False
    is_managed: bool = False
    is_enabled: bool = True

    @field_validator("capabilities")
    @classmethod
    def capabilities_must_be_non_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("capabilities must not be empty")
        return [v.strip().lower() for v in value if v.strip()]


class ModelCatalogEntryUpdate(BaseModel):
    capabilities: list[str] | None = None
    priority: int | None = Field(default=None, ge=1, le=1000)
    cost_input_1k: float | None = Field(default=None, ge=0.0)
    cost_output_1k: float | None = Field(default=None, ge=0.0)
    is_local: bool | None = None
    is_managed: bool | None = None
    is_enabled: bool | None = None

    @field_validator("capabilities")
    @classmethod
    def capabilities_must_be_non_empty(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        stripped = [v.strip().lower() for v in value if v.strip()]
        if not stripped:
            raise ValueError("capabilities must not be empty")
        return stripped


class ModelCatalogEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str
    provider_slug: str
    model: str
    capabilities: list[str]
    priority: int
    cost_input_1k: float
    cost_output_1k: float
    is_local: bool
    is_managed: bool
    is_enabled: bool
    source_version: str
    created_at: str


class ProviderConfigWrite(BaseModel):
    api_key: str | None = Field(default=None, max_length=2000)
    base_url: str | None = Field(default=None, max_length=500)
    model_default: str | None = Field(default=None, max_length=120)
    priority: int | None = Field(default=None, ge=0, le=1000)
    is_enabled: bool | None = Field(default=None)


class ProviderConfigRead(BaseModel):
    provider_slug: str
    api_key_masked: str | None = None
    base_url: str | None = None
    model_default: str
    priority: int
    is_enabled: bool
    requires_api_key: bool = True


class ProviderConfigListRead(BaseModel):
    providers: list[ProviderConfigRead]
    model_allowlist: dict[str, list[str]]


class ProviderTestRequest(BaseModel):
    """Optional overrides for a provider connectivity test.

    Lets the UI test a key/base-url/model before saving it. When a field is
    omitted, the persisted/env value is used.
    """

    api_key: str | None = Field(default=None, max_length=2000)
    base_url: str | None = Field(default=None, max_length=500)
    model_default: str | None = Field(default=None, max_length=120)


class ProviderTestResult(BaseModel):
    ok: bool
    provider_slug: str
    model: str | None = None
    latency_ms: int | None = None
    error: str | None = None
    models: list[str] | None = None


class SMTPConfigRead(BaseModel):
    host: str
    port: int
    use_ssl: bool
    username: str
    has_password: bool
    from_email: str
    is_app_password: bool


class SMTPConfigWrite(BaseModel):
    host: str = Field(min_length=1, max_length=500)
    port: int = Field(ge=1, le=65535)
    use_ssl: bool
    username: str = Field(min_length=1, max_length=500)
    password: str = Field(default="", max_length=2000)  # empty = keep existing
    from_email: str = Field(min_length=1, max_length=500)
    is_app_password: int | None = Field(default=None, ge=0, le=1)


class SMTPTestResponse(BaseModel):
    sent_to: str
    status: str


class EmailAccountCreate(BaseModel):
    label: str = Field(default="", max_length=200)
    provider: str = Field(default="imap", max_length=50)
    host: str = Field(min_length=1, max_length=500)
    port: int = Field(ge=1, le=65535)
    username: str = Field(min_length=1, max_length=500)
    password: str = Field(min_length=1, max_length=2000)
    folders_json: str = Field(default='["INBOX"]', max_length=2000)
    auth_type: str = Field(default="password", max_length=20)
    read_only: int = Field(default=1, ge=0, le=1)
    is_default: int = Field(default=0, ge=0, le=1)
    is_app_password: int = Field(default=1, ge=0, le=1)

    @field_validator("auth_type")
    @classmethod
    def auth_type_must_be_supported(cls, value: str) -> str:
        if value not in {"password", "oauth"}:
            raise ValueError("auth_type must be 'password' or 'oauth'")
        return value

    @field_validator("folders_json")
    @classmethod
    def folders_json_must_be_array(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            return "[]"
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"folders_json must be valid JSON: {exc}") from exc
        if not isinstance(parsed, list):
            raise ValueError("folders_json must be a JSON array")
        if not all(isinstance(item, str) and item.strip() for item in parsed):
            raise ValueError("folders_json must contain only non-empty strings")
        return stripped


class EmailAccountWrite(BaseModel):
    label: str = Field(default="", max_length=200)
    provider: str = Field(default="imap", max_length=50)
    host: str = Field(default="", max_length=500)
    port: int = Field(default=993, ge=1, le=65535)
    username: str = Field(default="", max_length=500)
    password: str = Field(default="", max_length=2000)  # empty = keep existing
    folders_json: str = Field(default='["INBOX"]', max_length=2000)
    auth_type: str = Field(default="password", max_length=20)
    read_only: int = Field(default=1, ge=0, le=1)
    is_default: int = Field(default=0, ge=0, le=1)
    is_app_password: int | None = Field(default=None, ge=0, le=1)

    @field_validator("auth_type")
    @classmethod
    def auth_type_must_be_supported(cls, value: str) -> str:
        if value not in {"password", "oauth"}:
            raise ValueError("auth_type must be 'password' or 'oauth'")
        return value

    @field_validator("folders_json")
    @classmethod
    def folders_json_must_be_array(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            return "[]"
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"folders_json must be valid JSON: {exc}") from exc
        if not isinstance(parsed, list):
            raise ValueError("folders_json must be a JSON array")
        if not all(isinstance(item, str) and item.strip() for item in parsed):
            raise ValueError("folders_json must contain only non-empty strings")
        return stripped


class EmailAccountRotateRequest(BaseModel):
    password: str = Field(min_length=1, max_length=2000)


class EmailAccountRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    label: str | None = None
    provider: str
    host: str
    port: int
    username: str
    has_password: bool
    folders_json: str
    auth_type: str
    read_only: int
    is_default: int
    is_app_password: int
    rotated_at: str | None = None
    schema_version: int
    source_version: str | None = None
    created_at: str
    updated_at: str


class WorkspaceEmailSignatureUpdate(BaseModel):
    email_signature: str = Field(default="", max_length=2000)


class FeaturesRead(BaseModel):
    email_connector_enabled: bool
    shared_instance: bool


# -----------------------------------------------------------------------------
# SL1b: Knowledge Base + Draft API models
# -----------------------------------------------------------------------------


class KBSourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    type: Literal["md", "txt", "csv", "xlsx", "pdf"] = "md"
    content_text: str = Field(default="", min_length=0, max_length=500000)
    source_version: str = Field(default="v1", min_length=1, max_length=120)
    level: int = Field(default=0, ge=0, le=4)
    file_name: str | None = Field(default=None, max_length=500)
    mime_type: str | None = Field(default=None, max_length=200)
    file_size: int | None = Field(default=None, ge=0)


class KBSourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    type: str
    title: str
    content_text: str | None = None
    meta_json: str
    source_version: str | None = None
    schema_version: int
    file_name: str | None = None
    mime_type: str | None = None
    file_size: int | None = None
    parser_version: str | None = None
    level: int = 0
    approved_by: str | None = None
    created_at: str


class KBFactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    source_id: str
    entity_key: str
    field_name: str
    field_value: str
    unit: str | None = None
    currency: str | None = None
    valid_from: str | None = None
    valid_until: str | None = None
    source_locator: str | None = None
    source_version: str | None = None
    source_sheet: str | None = None
    created_at: str


class KBChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    source_id: str
    chunk_index: int
    content_text: str
    source_locator: str | None = None
    source_version: str | None = None
    created_at: str


class DraftSource(BaseModel):
    source_id: str
    label: str
    title: str
    locator: str | None = None
    source_version: str | None = None
    excerpt: str


class DraftHardFact(BaseModel):
    field: str
    value: str
    source_id: str
    source_locator: str | None = None
    source_version: str | None = None


class DraftContent(BaseModel):
    subject: str | None = None
    body_md: str
    hard_facts_used: list[DraftHardFact] = Field(default_factory=list)
    sources: list[DraftSource] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    requires_confirmation: bool = False


class DraftGenerateRequest(BaseModel):
    chat_id: str | None = None
    task: Literal["draft_commercial_reply"] = "draft_commercial_reply"
    user_request: str = Field(min_length=1, max_length=20000)
    provider_slug: str | None = None
    model: str | None = None
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int | None = Field(default=2048, gt=0, le=4096)


class DraftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    chat_id: str | None = None
    tenant_id: str | None = None
    user_id: str | None = None
    actor_id: str | None = None
    actor_role_at_decision: str | None = None
    task: str
    subject: str | None = None
    body_md: str
    hard_facts_json: str
    sources_json: str
    blockers_json: str
    warnings_json: str
    requires_confirmation: bool
    status: str
    schema_version: int
    source_version: str | None = None
    approved_by: str | None = None
    approved_at: str | None = None
    exported_at: str | None = None
    original_body_md: str | None = None
    edit_pct: float | None = None
    urgency: int = 0
    reason: str | None = None
    created_at: str
    updated_at: str


class DraftUpdateRequest(BaseModel):
    subject: str | None = Field(default=None, max_length=500)
    body_md: str | None = Field(default=None, max_length=50000)


class DraftApproveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)
    urgency: int = Field(default=0, ge=0)


class DraftRejectRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)


class RoutineRunApproveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)
    urgency: int = Field(default=0, ge=0)


class RoutineRunRejectRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)


class DraftExportRead(BaseModel):
    markdown: str
    subject: str | None = None
    exported_at: str
