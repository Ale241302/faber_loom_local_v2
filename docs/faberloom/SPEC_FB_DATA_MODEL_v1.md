---
id: SPEC_FB_DATA_MODEL_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE 2026-05-02 (modelo de datos consolidado · base para backend MVP1)
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decision arquitectura)
aplica_a: [FaberLoom]
fuente_verdad: docs/anexos/mockups/mockup_e1_full_navigable.html (entidades mock IAK_*, KN2_*) + brief externo (referencia complementaria · refactorizado)
relacionado:
  - SPEC_FB_AI_CONTROL_PLANE_v1.md
  - SPEC_FB_KNOWLEDGE_ATLAS_v1.md
  - SPEC_FB_VOICE_HUMANIZER_v1.md
  - SPEC_ACTION_ENGINE.md
  - SPEC_AUDIT_MODULE.md
---

# SPEC_FB_DATA_MODEL_v1

## Modelo de datos canon · backend MVP1

## 1. Por que existe este documento

El brief externo propuso 19 entidades. Como arquitecto, las refactorizo a un modelo mas simple sin perder expresividad: `outputs` con discriminator `kind` en lugar de 4 tablas separadas, `candidates` unica con `type` enum en lugar de 9 tablas. Backend mas mantenible · queryable igual.

Este SPEC define el modelo canon que el mock representa con `IAK_*` y `KN2_*` y que el backend MVP1 debe implementar.

## 2. Principio de modelado

```
Una entidad por concepto operativo.
Discriminator (kind/type) en lugar de N tablas hermanas.
FK a parent_id para versioning.
Audit trail siempre via separate audit_events table.
```

## 3. Entidades core · 14 tablas

### 3.1 Identity & RBAC

```sql
tenants(tenant_id, name, plan, dpa_status, created_at)
users(user_id, tenant_id, email, role_id, status)
roles(role_id, name, permissions[])  -- Owner|Admin|AM|Curator|Operator|Auditor|FaberLoom Product Dev
```

### 3.2 Agents & Skills

```sql
agents(agent_id, tenant_id, handle, type, status, parent_id, version, owner_id, spec_jsonb)
  -- type: TEMPLATE|CUSTOM|SANDBOX|SYSTEM
  -- parent_id: jerarquia recursiva (max depth 5)
skills(skill_id, tenant_id, name, type, status, version, base_layer_jsonb, contract_jsonb)
  -- type: SEALED|OPEN|EXTERNAL
  -- contract: input/output schema + policies + fallbacks
skill_overlays(overlay_id, skill_id, layer, owner_role, content_jsonb, status)
  -- layer: manual|learned
agent_skill_bindings(binding_id, agent_id, skill_id, ai_profile_id, role)
  -- role: primary|fallback|specialty
```

### 3.3 AI Control Plane

```sql
provider_connections(provider_connection_id, tenant_id, provider, status,
                     secret_ref, dpa_category, allowed_data_classes[],
                     allowed_modalities[], rotation_due_at, vault_namespace)
  -- secret_ref apunta a Vault/KMS · NUNCA la key

ai_profiles(ai_profile_id, tenant_id, name, status, version,
            allowed_provider_connections[], allowed_data_classes[],
            allowed_modalities[], blocked_modalities[],
            prep_model_policy, prompt_pack_strategy, producer_model_policy,
            final_pass_policy, judge_model_policy, human_gate_policy,
            dispatch_modes[], budget_soft_cap, budget_hard_cap,
            fallback_strategy, routing_matrix_version, arena_ranking_version)

skill_ai_contracts(skill_contract_id, agent_id, skill_id,
                   default_ai_profile, allowed_input_modalities[],
                   allowed_output_modalities[], forbidden_modalities[],
                   data_class_max, client_visible, side_effects,
                   final_pass_required, human_gate_required,
                   allowed_overrides[], forbidden_overrides[])

prompt_profiles(prompt_profile_id, model_family, target_roles[],
                working_language, output_language, instruction_style,
                context_order[], tag_strategy, few_shot_count,
                reasoning_scaffold, schema_preferences,
                known_failure_modes[], best_task_roles[], current_version)

prompt_recipes(prompt_recipe_id, task_type, prep_model, prompt_pack_strategy,
               working_language, facts_locked, producer_model,
               producer_prompt_profile, final_pass_model, output_language,
               human_gate, data_class_allowed, policy_gates[], arena_score)
```

### 3.4 Knowledge

```sql
knowledge_nodes(node_id, tenant_id, type, status, label, root_path,
                privacy_tier, version, confidence, freshness, avg_tokens,
                consumers[], outputs[], unit_of_work, validity_jsonb, content_jsonb)
  -- type: SRC|ENT|SCH|POL|PLB|SKILL|AGENT|OUTPUT|MEM|CASE|VOICE_USER|VOICE_ORG|VOICE_DEPT|VOICE_CHANNEL|VOICE_RECIPIENT
  -- status: VIGENTE|SIGNED|CANDIDATE|STALE|CONFLICTED|BLOCKED|USABLE|FROZEN|DEPRECATED
  -- privacy_tier: PRIVATE_RAW|TENANT_DERIVED|GLOBAL_PROMOTABLE|RESTRICTED_SENSITIVE_OR_REGULATED

knowledge_edges(edge_id, from_node_id, to_node_id, verb, weight)
  -- verb: usa|alimenta|gobierna|produce|consumido_por|aprendio_de|estructura|invoca|aporta|humaniza
```

### 3.5 Outputs (1 tabla con kind discriminator · NO 4 tablas separadas)

```sql
outputs(output_id, tenant_id, kind, parent_output_id, agent_id, skill_id, task_id,
        content_jsonb, output_type, evidence_refs[], confidence, hash,
        provider_connection_id, model_id, prompt_version, skill_version,
        agent_version, context_snapshot_id, cost_usd, latency_ms,
        tokens_in, tokens_out, run_mode, status, edited_by, diff_summary, created_at)
  -- kind: artifact|version|golden_sample|gap_report|pinned
  -- parent_output_id permite tree de versiones sin tabla aparte
  -- versioning: nueva fila con kind=version + parent_output_id
  -- golden sample: nueva fila con kind=golden_sample (puede tener parent o ser standalone)
  -- output pin: nueva fila con kind=pinned + recipe metadata
```

### 3.6 Candidates (1 tabla con type · NO 9 tablas)

```sql
candidates(candidate_id, tenant_id, type, status, origin_view, origin_run_id,
           target, reason, risk, evidence_jsonb, proposed_change_jsonb,
           approval_required, approval_route, expiration, rollback_target,
           created_by, created_at, decided_by, decided_at, decision_reason)
  -- type: routing_ladder|ai_profile|prompt_recipe|output_pin|provider_policy_review|
  --       capability_request|policy_exception|rollback|budget_adjustment|voice|change_plan|
  --       skill_overlay|agent_overlay|kb_gap|rule_candidate
  -- status: DRAFT|TESTING|NEEDS_REVIEW|READY_TO_SIGN|APPROVED|REJECTED|EXPIRED
```

### 3.7 Ledgers & Audit

```sql
token_ledger(entry_id, run_id, parent_request_id, tenant_id, agent_id,
             skill_id, task_type, ai_profile_id, routing_matrix_version,
             arena_ranking_version, prompt_profile_version, prompt_recipe_id,
             provider_policy_version, data_classification, data_class_max_in_chain,
             input_modality, output_modality, side_effects, client_visible,
             provider_connection_id, model_chain_jsonb, prompt_hash, context_hash,
             output_hash, input_hash, cost_usd, latency_ms, tokens_in, tokens_out,
             final_pass_required, final_pass_executed, human_gate_required,
             human_gate_outcome, budget_status, policy_blocks, audit_id, created_at)

governance_ledger(governance_entry_id, candidate_id, decision_type,
                  approver_role, approval_status, reason, diff_summary,
                  previous_version, new_version, rollback_target,
                  hash_chain_status, policy_version_pinned, audit_id, created_at)

policy_blocks(block_id, tenant_id, run_id, attempted_action,
              blocked_by_policy, block_reason, data_class,
              provider_connection_id, modality, skill_id, ai_profile_id,
              safe_alternative, candidate_allowed, audit_id, created_at)

audit_events(audit_id, tenant_id, trace_id, action_id, actor_user_id,
             actor_role, event_type, payload_jsonb, previous_audit_hash,
             entry_hash, signature, created_at)
  -- INMUTABLE · solo INSERT · hash chain via previous_audit_hash
```

## 4. Reglas de integridad

```
1. Outputs nunca se UPDATE in-place · siempre INSERT nueva fila con kind=version + parent_output_id
2. Knowledge_nodes con status=SIGNED nunca se UPDATE · solo nueva version (nuevo node con parent ref)
3. Audit_events solo INSERT · nunca UPDATE/DELETE
4. Candidates pueden UPDATE mientras status in (DRAFT|TESTING|NEEDS_REVIEW)
5. Provider_connections nunca exponen secret_ref via API · solo masked_key
6. Token_ledger NUNCA almacena: keys · raw secrets · payload sensible sin policy
7. Knowledge_nodes con privacy_tier=PRIVATE_RAW no salen del tenant_id sin candidate aprobado
8. Promote L2->L3 (privacy_tier change) requiere candidate + signature
```

## 5. Discriminadores canon

| Tabla | Campo | Valores |
|---|---|---|
| agents | type | TEMPLATE \| CUSTOM \| SANDBOX \| SYSTEM |
| skills | type | SEALED \| OPEN \| EXTERNAL |
| skill_overlays | layer | manual \| learned |
| knowledge_nodes | type | SRC \| ENT \| SCH \| POL \| PLB \| SKILL \| AGENT \| OUTPUT \| MEM \| CASE \| VOICE_USER \| VOICE_ORG \| VOICE_DEPT \| VOICE_CHANNEL \| VOICE_RECIPIENT |
| knowledge_nodes | status | VIGENTE \| SIGNED \| CANDIDATE \| STALE \| CONFLICTED \| BLOCKED \| USABLE \| FROZEN \| DEPRECATED |
| knowledge_nodes | privacy_tier | PRIVATE_RAW \| TENANT_DERIVED \| GLOBAL_PROMOTABLE \| RESTRICTED_SENSITIVE_OR_REGULATED |
| outputs | kind | artifact \| version \| golden_sample \| gap_report \| pinned |
| candidates | type | (15 tipos · ver 3.6) |

## 6. Diferencia con el brief externo

| Brief externo proponia | Mi modelo |
|---|---|
| 4 tablas: output_artifacts + output_versions + learning_candidates + golden_samples | 1 tabla outputs con kind |
| 9 tablas de candidates por tipo | 1 tabla candidates con type |
| ProviderConnection separada de provider | Una sola tabla provider_connections |
| RoutingPolicy + WorkspacePolicy + TenantPolicy + AIProfile + Binding + SkillContract + RunContext (7 tablas) | 4 tablas (policies por nivel se computan en runtime · cascade declarada en mockup como IAK_INHERITANCE) |

Razon: queryability igual + menos joins + mantenibilidad backend MVP1.

## 7. Que NO esta en este SPEC (deferred)

- Indices y particionado · vive en SPEC_FB_BACKEND_PERSISTENCE_v1 (futuro)
- API contracts (REST/GraphQL) · vive en SPEC_FB_API_v1 (futuro)
- Migraciones · viven en repo backend cuando exista
- Realtime streams (WebSocket/SSE) · vive en SPEC_FB_REALTIME_v1 (futuro)

## 8. Prioridad MVP1 (por valor para Foundation Beta)

```
P0 · tenants · users · roles · agents · skills · skill_ai_contracts · agent_skill_bindings
P1 · provider_connections · ai_profiles · token_ledger · audit_events · policy_blocks
P2 · knowledge_nodes · knowledge_edges · outputs · candidates
P3 · prompt_profiles · prompt_recipes · governance_ledger · skill_overlays
P4 · resto (golden samples bulk · arena rounds · etc.)
```

## 9. Changelog

- v1.0 (2026-05-02) · Modelo canon consolidado del mock + brief externo refactorizado. Base para backend MVP1.
