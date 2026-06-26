# Latent fields matrix — SpaceLoom SL0

This matrix makes the contract-first seam explicit for SL0. The app remains
single-user/local-first, but every durable application table exposes the latent
fields needed to move to managed keys, routines, stronger HITL, and future
multi-tenant storage without a model rewrite.

| Table | tenant_id | user_id | actor_id | actor_role_at_decision | routine_version | skill_version | schema_version | source_version | approved_by |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `workspace` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `kb_source` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `chat` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `message` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `draft` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `audit_log` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `routine` | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| `routine_run` | yes | yes | yes | yes | yes | yes | yes | yes | yes |

Notes:

- `tenant_id` is nullable in SL0. `NULL` means the default local single-user
  tenant; it is still always part of the schema and query seam.
- `actor_id` / `actor_role_at_decision` capture who made or approved a decision
  without requiring a real identity provider in SL0.
- `routine_version` and `skill_version` are nullable until SL3a introduces the
  Routine Hub and portable `SKILL.md` compiler.
- `schema_version` stores the application schema contract version that produced
  the row.
- `source_version` is nullable where a row is not derived from an external KB
  source yet; SL2 will make it required for hard facts.
- `approved_by` stays nullable until HITL approval flows exist; irreversible
  actions are not implemented in SL0.
