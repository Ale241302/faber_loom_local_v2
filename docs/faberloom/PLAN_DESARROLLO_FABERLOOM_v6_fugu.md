---
id: PLAN_DESARROLLO_FABERLOOM_v6_fugu
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: DRAFT -- 2026-06-25 -- plan modular distribuido contract-first E0-E3
aprobador: CEO
aplica_a: [FaberLoom]
relacionado:
  - CLAUDE.md
  - WIKI.md
  - docs/faberloom/SCH_FB_FUNCTIONAL_SPEC_v1.md
  - docs/faberloom/SPEC_FB_BUILD_SEQUENCE_v3.md
  - docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v5.md
  - docs/faberloom/SPEC_FB_ROUTING_PRESETS_v1.md
  - docs/faberloom/PLB_FB_FOUNDATION_BETA_v1.md
  - docs/faberloom/SPEC_FB_EVENTING_AND_OUTBOX_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M08_AUTH_SESSION_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M09_RBAC_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M11_D9_POLICY_GATE_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M12_AUDIT_TRAIL_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M14_OUTCOME_LEDGER_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M17_MEMORY_LETTA_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1.md
  - docs/faberloom/SPEC_FB_FUNC_M20_AUTO_UPDATE_v1.md
  - docs/faberloom/PLB_PROMPTING_FUGU_KIMI_v1.md
  - docs/faberloom/PLB_AUDIT_PATTERN_v1.md
  - docs/anexos/kimi_swarm_audit_faberloom/a9_sintesis.md
supersede:
  - docs/faberloom/PLAN_DESARROLLO_FABERLOOM_v5.md
run_id: PLAN-MOD-2026-06-25
engine: fugu
---

# PLAN_DESARROLLO_FABERLOOM_v6_fugu -- Plan modular distribuido E0-E3

## PLAN DE ORQUESTACION

1. Tipo de problema: build MODULAR y DISTRIBUIDO (contract-first).
2. Descomposicion: por modulo (M07-M20) como unidad independiente con contrato.
3. Especialistas asignados por dominio de modulo.
4. Estrategia: parallel execution + bring-in-specialist + debate-and-aggregation SOLO para particionar tracks.
5. Puntos de verificacion: integridad de contratos entre modulos.

## SUPUESTOS Y ALCANCE

- [SUPUESTO: `{{ENGINE}}` no vino instanciado; se usa `fugu` en el nombre del archivo.]
- [SUPUESTO: `{{RUN_ID}}` no vino instanciado; se usa `PLAN-MOD-2026-06-25`.]
- Stack canonico para este plan: Django 4.2 + PostgreSQL 16 + pgvector + RLS + Redis 7 + Celery + Electron/React + Next.js + LiteLLM Proxy Anthropic-only + Letta self-hosted + Docker Compose en Hostinger KVM 8.
- Este plan supersede el orden operativo de `PLAN_DESARROLLO_FABERLOOM_v5`; no modifica los archivos FROZEN `ENT_OPS_STATE_MACHINE` ni `PLB_ORCHESTRATOR`.
- Tallas usadas: S/M/L/XL. No se inventan horas.
- Kill criteria E1: `>=1 incidente privacy cross-tenant o salida N3/N4 sin DPA = kill/replan inmediato`.

## PRINCIPIO RECTOR -- CONTRACT-FIRST

Cada modulo expone un contrato estable: inputs, outputs, eventos emitidos/consumidos, schemas, RLS, audit. Los builders distribuidos no comparten estado interno. Solo se acoplan por contratos versionados, eventos canonicos y tablas/schemas declarados. Un modulo puede comenzar cuando los contratos que consume estan congelados y hay tests de contrato, aunque la implementacion interna del productor no este completa.

## FASE 1 -- DEBATE-AND-AGGREGATION DE PARTICIONES

### Particion candidata A -- Por capa tecnica

- Spine: M16, M08, M09, M15, M12, M11.
- Tracks: backend AI (M10/M13), learning (M14/M17), desktop (M18/M19/M20), bootstrap (M07).
- Ventaja: maximiza paralelismo despues del spine.
- Riesgo: M07 queda tarde si se interpreta como onboarding de tenant real.

### Particion candidata B -- Por flujo usuario

- Track 1: Tenant setup (M07/M08/M09/M16).
- Track 2: Inbound a draft (M10/M11/M12/M13/M15).
- Track 3: Aprendizaje/memoria (M14/M17).
- Track 4: Desktop lifecycle (M18/M19/M20).
- Ventaja: cada track cuenta una historia de usuario.
- Riesgo: mezcla demasiado estado interno en Track 2; baja independencia.

### Particion candidata C -- Por riesgo de integracion

- Spine duro: aislamiento, sesion, permisos, eventos, audit, policy.
- Tracks paralelos solo despues de pasar tests cross-tenant de M16.
- Ventaja: reduce el riesgo P0 detectado por auditorias Kimi/Fugu.
- Riesgo: menos paralelismo durante la primera fase.

### Agregacion elegida

Se adopta la particion C con tracks de la A. Primero se construye un SPINE serial minimo que establece aislamiento, identidad, eventos, audit y policy. Despues se forkearan cuatro tracks paralelos por contrato: Tenant Activation, AI Work Pipeline, Learning/Memory y Desktop Runtime.

---

# 1. SPINE SERIAL -- ORDEN MINIMO OBLIGATORIO

El SPINE no busca completar todas las features. Busca congelar contratos transversales que todos los tracks consumen. Ningun track operativo arranca antes de pasar los 5 tests cross-tenant de M16.

| Orden | Modulo | Talla | Especialista | Contrato que debe quedar congelado | Can-start-when | Bloquea |
|---:|---|---|---|---|---|---|
| 1 | M16 Tenant Isolation | L | RLS/multi-tenant | `tenant_context`, RLS, Redis prefix, Celery tenant payload, MinIO path, pgvector partition, LiteLLM tenant context, Letta namespace | E0 firmado + DB local | Todos los tracks |
| 2 | M08 Auth Session | M | Auth/security | session Redis, cookie/httpOnly, tenant_id server-side, auth events | M16 contract v1 | M09, M18, M07 |
| 3 | M09 RBAC | M | RBAC/compliance | membership, active hat, permission check, actor_role_at_decision | M08 contract v1 | M07, M13, M12 |
| 4 | M15 Outbox Streams | M | Eventing | event envelope, outbox, Redis Stream per tenant, `last_event_id`, `sync_required` | M16 + M08 contracts | M13, M19, M12 consumers |
| 5 | M12 Audit Trail | M | Compliance/audit | audit entry, tenant-scoped hash chain, append-only API, audit event writer | M16 + M09 + M15 event envelope | M11, M13, M14, M17 |
| 6 | M11 D9 Policy Gate | M | Policy/compliance | `ActionContext`, `effective_classification`, hard block, pre-egress mismatch, DPA state | M10 input contract stub + M12 audit writer | M10 execution, M13 outbound, M07 activation |
| 7 | M07 Bootstrap Wizard | M | Tenant onboarding | tenant activated, Owner/Operator, DPA state, seed skills shadow, mailbox connected | M08/M09/M11/M12/M16 contracts | Beta tenant go-live |

## SPINE acceptance criteria

1. Un request autenticado porta `tenant_id` desde sesion server-side, no desde header editable por cliente.
2. Toda query aislable falla cerrada si falta `app.tenant_id`.
3. Todo evento de negocio se escribe en Postgres + outbox en la misma transaccion.
4. Todo audit entry tiene `tenant_id`, `actor_role_at_decision`, `sha_chain_prev`, `sha_chain_curr` y chain tenant-scoped.
5. D9 puede bloquear N3/N4 sin DPA antes de cualquier llamada LLM o salida externa.
6. M07 no activa tenant si M16/M08/M09/M11/M12 no pasan smoke tests.

---

# 2. TRACKS PARALELOS

## TRACK T0 -- Tenant Activation / Governance

**Modulos:** M07 Bootstrap Wizard.  
**Especialista:** Tenant onboarding + compliance ops.  
**Talla:** M.  
**Can-start-when:** M08/M09/M11/M12/M16 contracts congelados; no requiere UI desktop.  
**Contrato:** crea tenant operativo y seed minimo para beta.

### Contrato T0

**Consume:**
- M08: login Owner + 2FA + session Redis.
- M09: roles Owner/Operator y permission check.
- M11: DPA state y data ceiling inicial.
- M12: audit writer.
- M16: tenant isolation context.

**Expone:**
- `tenant.status in (setup, active, blocked)`.
- `tenant.config` con pasos completados.
- `membership` Owner/Operator.
- `dpa_state` (`missing`, `signed`, `blocked`).
- seed skills en `shadow`.
- eventos: `tenant.created`, `user.invited`, `user.2fa_enabled`, `mailbox.connected`, `document.uploaded`, `tenant.activated`.

### Aceptacion T0

- Un tenant MWT se crea completo sin datos cross-tenant.
- Owner puede invitar Operator.
- DPA missing bloquea N3/N4.
- Seed skills quedan `shadow`, no `active`.

### Tests T0

- `test_bootstrap_creates_owner_operator_only_in_e1`
- `test_bootstrap_blocks_activation_when_dpa_required_missing`
- `test_seed_skills_are_shadow_and_cannot_external_send`

---

## TRACK T1 -- AI Work Pipeline / Inbound -> Draft -> HITL

**Modulos:** M10 L1 Classifier, M11 D9 Policy Gate (implementacion completa), M13 Draft HITL.  
**Especialistas:** ML classifier + policy gate + HITL/UX.  
**Tallas:** M10=M, M11=M, M13=M.  
**Can-start-when:** SPINE M16/M08/M09/M15/M12 contracts congelados; M11 puede iniciar con stub de M10 schema.  
**Contrato:** convierte inbound en ActionContext, bloquea data riesgosa, produce draft revisable por output.

### Contrato T1

**Consume:**
- M15: `feed.item.received`, `task.created`, event writer.
- M16: tenant context y RLS.
- M12: audit writer.
- M09: permission para approve/edit/reject.
- M11: policy decision.

**Expone:**
- `ActionContext` con `task_type`, `data_class`, `skill_id`, `confidence`, `source`, `tenant_id`.
- `PolicyDecision` con `allowed`, `blocked_reason`, `effective_classification`, `requires_human_gate`.
- `DraftOutput` por output: `draft_id`, `output_id`, `schema_status`, `review_status`.
- eventos: `feed.item.dispatched`, `task.created`, `policy.gate.passed`, `policy.gate.blocked`, `policy.classification_mismatch`, `draft.generated`, `draft.approved`, `draft.edited`, `draft.rejected`, `draft.sent`.

### Aceptacion T1

- Un RFQ real MWT genera un draft en WorkLoom sin envio externo automatico.
- Si L1 clasifica N1 pero pre-egress detecta N3, D9 bloquea fail-closed.
- La aprobacion es por output, no por task.
- `human_approver_id` es obligatorio para cualquier `external_communication` o `external_mutation`.

### Tests T1

- `test_l1_classifier_outputs_action_context_schema`
- `test_d9_pre_egress_classification_mismatch_blocks_provider_call`
- `test_external_draft_requires_human_approver_id_before_send`

---

## TRACK T2 -- Learning / Outcome / Memory

**Modulos:** M14 Outcome Ledger, M17 Memory Letta.  
**Especialistas:** Learning pipeline + memory containment.  
**Tallas:** M14=M, M17=M.  
**Can-start-when:** M12 audit writer + M16 isolation + M13 review events contract congelados.  
**Contrato:** convierte feedback humano en outcome ledger y memoria gated sin contaminar KB ni tenants.

### Contrato T2

**Consume:**
- M13: `draft.approved`, `draft.edited`, `draft.rejected`.
- M12: audit writer.
- M16: Letta namespace isolation.
- KB VIGENTE validity status.

**Expone:**
- `OutcomeEntry` con `task_id`, `draft_id`, `review_status`, `edit_distance`, `reason_code`, `time_saved_estimate`, `skill_version`.
- `LearningCandidate` con `candidate_type in (context, skill_refinement, gold_sample)`.
- Letta namespaces: `mem:tenant:{tenant_id}:agent:{agent_id}:task:{task_id}:working`, `episodic`, `persistent`.
- estados memoria: `active`, `disputed`, `deprecated`.
- eventos: `outcome.recorded`, `learning.candidate.created`, `memory.persisted`, `memory.disputed`, `memory.deprecated`.

### Aceptacion T2

- Feedback de un draft aprobado crea `OutcomeEntry` y no crea persistent memory automaticamente.
- Working memory incluye `task_id` y se limpia al terminal state.
- Si memoria contradice KB VIGENTE, se marca `disputed` y no se inyecta al prompt.

### Tests T2

- `test_outcome_recorded_from_draft_review_event`
- `test_working_memory_namespace_includes_task_id_and_cleans_on_terminal_state`
- `test_disputed_memory_not_injected_into_prompt`

---

## TRACK T3 -- Desktop Runtime / Electron

**Modulos:** M18 Electron Auth, M19 Offline Sync, M20 Auto Update.  
**Especialistas:** Electron security + realtime/offline + release engineering.  
**Tallas:** M18=M, M19=M, M20=M.  
**Can-start-when:** M08/M15/M16 contracts congelados; M13 contract para pending mutations; M20 puede empezar con release feed stub.  
**Contrato:** desktop seguro, reconciliable y actualizable sin perder trabajo.

### Contrato T3

**Consume:**
- M08: session server-side and `/auth/me`.
- M16: tenant-scoped session and data.
- M15: WS `?since=last_event_id`, `sync_required`.
- M13: pending mutations/drafts saved state.

**Expone:**
- Electron partition: `persist:faberloom-{profile}`.
- local non-secret cursor state: `last_event_id`, `last_sync_at`, `tenant_id`, `client_version`.
- update status: `checking`, `downloaded`, `ready_to_install`, `blocked_min_supported`.
- UI states: `connected`, `disconnected_unexpected`, `syncing`, `sync_required`, `read_only_offline`.
- events/telemetry: `desktop.login`, `desktop.sync.started`, `desktop.sync.completed`, `desktop.update.ready`, `desktop.update.installed` (telemetry no PII).

### Aceptacion T3

- Renderer no puede leer token/sesion.
- Restart tras 2h offline recupera estado con full fetch + WS since.
- No hay aprobaciones offline en S1A.
- Update nunca reinicia mid-task; instala al cerrar o boton explicito.

### Tests T3

- `test_renderer_cannot_read_session_token`
- `test_last_event_id_persisted_across_app_restart_and_reconciles`
- `test_update_does_not_install_with_pending_mutations`

---

## TRACK T4 -- Eventing hardening / Realtime contracts

**Modulos:** M15 Outbox Streams hardening posterior al SPINE.  
**Especialista:** Eventing/realtime.  
**Talla:** M.  
**Can-start-when:** M15 envelope congelado y M16 tenant prefix contract.  
**Contrato:** entrega confiable at-least-once, dedupe e hidratacion de UI.

### Contrato T4

**Consume:**
- M12 audit event writer for critical events.
- M16 tenant prefix.

**Expone:**
- `event_log` append-only.
- `outbox` transactional.
- Redis Stream `events:{tenant_id}`.
- WS fanout by tenant and permission.
- reconnect protocol: `?since=<last_event_id>` and `sync_required`.

### Aceptacion T4

- DB commit + Redis publish no se separan sin outbox.
- Duplicados se ignoran por `event_id`.
- Tenant A nunca recibe stream tenant B.

### Tests T4

- `test_outbox_publishes_after_business_transaction_commit`
- `test_duplicate_event_id_processed_once`
- `test_ws_fanout_filters_by_tenant_and_permission`

---

# 3. REGISTRO DE CONTRATOS MODULO -> MODULO

| Modulo | Expone | Consume | Eventos emitidos | Eventos consumidos | RLS/Audit obligatorio |
|---|---|---|---|---|---|
| M07 Bootstrap Wizard | `tenant`, `membership`, `dpa_state`, seed skills shadow | M08, M09, M11, M12, M16 | `tenant.created`, `user.invited`, `mailbox.connected`, `tenant.activated` | n/a | tenant_id en todo; audit D10 para activacion |
| M08 Auth Session | `session_id`, `tenant_id`, `user_id`, `active_hat` | M16 tenant context | `auth.login.success`, `auth.login.failed`, `session.revoked` | n/a | audit auth; session Redis scoped |
| M09 RBAC | permission decision, `actor_role_at_decision` | M08 session | `user.role_changed`, `permission.denied` | auth events | audit cada cambio rol; RLS membership |
| M10 L1 Classifier | `ActionContext` | feed item, M11 schema, M15 event writer | `feed.item.dispatched`, `task.created` | `feed.item.received` | audit classification; no external side-effect |
| M11 D9 Policy Gate | `PolicyDecision`, `effective_classification` | M10, M07 DPA, M12 audit | `policy.gate.passed`, `policy.gate.blocked`, `policy.classification_mismatch` | `task.created` | fail-closed; audit every block |
| M12 Audit Trail | append-only `AuditEntry` and hash chain | M16, M09 actor, M15 envelope | `audit.entry.created`, `sha_chain.broken` | all sensitive events | tenant-scoped chain, no update/delete |
| M13 Draft HITL | `DraftOutput`, review state, external send gate | M09, M11, M12, M15 | `draft.generated`, `draft.approved`, `draft.edited`, `draft.rejected`, `draft.sent` | `task.created`, `policy.gate.passed` | `human_approver_id` for external actions |
| M14 Outcome Ledger | `OutcomeEntry`, `LearningCandidate` | M13 review events, M12 | `outcome.recorded`, `learning.candidate.created` | `draft.approved`, `draft.edited`, `draft.rejected` | audit gold/persistent promotions |
| M15 Outbox Streams | event log, outbox, Redis stream, WS protocol | M16, M12 for critical audit | all event fanout | all producer events | stream per tenant; dedupe by event_id |
| M16 Tenant Isolation | tenant context utilities and isolation rules | M08 session | `cross_tenant.access_attempted` | n/a | FORCE RLS, Redis prefix, Celery tenant payload, MinIO paths, pgvector partition, LiteLLM ctx, Letta namespace |
| M17 Memory Letta | episodic/working/persistent memory API | M14, M16, KB VIGENTE, M12 | `memory.persisted`, `memory.disputed`, `memory.deprecated` | `learning.candidate.created` | working by task_id; persistent human gate; episodic append-only |
| M18 Electron Auth | secure desktop session partition | M08, M16 | `desktop.login` | `session.revoked` | no localStorage tokens; keychain for secrets |
| M19 Offline Sync | persisted cursors and sync state | M15, M18, M13 | `desktop.sync.started`, `desktop.sync.completed` | WS events, `sync_required` | no approvals offline; revalidate tenant before sync |
| M20 Auto Update | signed update lifecycle | M18, M19, M13 | `desktop.update.ready`, `desktop.update.installed` | backend min version | no tenant data in update; no restart mid-task |

---

# 4. DAG DE DEPENDENCIAS

## DAG textual

```text
M16 Tenant Isolation
  -> M08 Auth Session
      -> M09 RBAC
      -> M18 Electron Auth
  -> M15 Outbox Streams
      -> M19 Offline Sync
  -> M12 Audit Trail
      -> M11 D9 Policy Gate
      -> M13 Draft HITL
      -> M14 Outcome Ledger
      -> M17 Memory Letta
  -> M07 Bootstrap Wizard

M10 L1 Classifier
  -> M11 D9 Policy Gate
  -> M13 Draft HITL

M13 Draft HITL
  -> M14 Outcome Ledger
  -> M19 Offline Sync
  -> M20 Auto Update pre-install checks

M18 Electron Auth
  -> M19 Offline Sync
  -> M20 Auto Update
```

## Bloqueos duros

- M16 bloquea todos los modulos que leen/escriben datos tenant-scoped.
- M08 bloquea M09, M18, M07.
- M09 bloquea cualquier aprobacion HITL y cualquier cambio de roles.
- M12 bloquea M11, M13, M14, M17 para acciones sensibles.
- M11 bloquea cualquier LLM/provider call con data N2+ y cualquier output externo.
- M15 bloquea M19 y cualquier realtime WorkLoom confiable.

## Paralelizable despues del SPINE

- T0 M07 puede avanzar en paralelo con T1/T2/T3 si solo consume contratos ya congelados.
- T1 M10/M13 puede avanzar en paralelo con T2 si M13 emite eventos fake/fixture para M14.
- T2 M14/M17 puede avanzar con fixtures de `draft.approved/rejected`.
- T3 M18/M19/M20 puede avanzar con WS mock de M15 y `/auth/me` mock de M08.
- T4 M15 hardening puede avanzar en paralelo mientras no cambie event envelope.

---

# 5. INTEGRATION POINTS + CONTRACT TESTS

## Tests cross-tenant M16 obligatorios ANTES de abrir cualquier track

1. `test_postgres_rls_same_worker_tenant_a_then_b_no_cross_read`  
   Mismo proceso Django/Celery ejecuta tenant A y luego tenant B; B no ve filas A.

2. `test_celery_with_tenant_session_clears_context_after_exception`  
   Job tenant A falla; job tenant B posterior no hereda `app.tenant_id` ni cache interno.

3. `test_redis_stream_and_cache_keys_require_tenant_prefix`  
   Cualquier key sin `tenant:{tenant_id}:` falla lint/runtime.

4. `test_pgvector_n2_plus_uses_tenant_partition_not_global_hnsw`  
   `EXPLAIN` prueba partition pruning antes del vector scan para N2+.

5. `test_letta_namespace_blocks_cross_tenant_profile_access`  
   Agent tenant A no puede listar, recuperar ni inyectar memoria tenant B.

## Integration points principales

| Punto | Productor | Consumidor | Contract test |
|---|---|---|---|
| Tenant context | M08/M16 | Todos | `test_request_without_server_tenant_context_fails_closed` |
| Permission decision | M09 | M13/M07/web/admin | `test_permission_check_required_for_sensitive_endpoint` |
| Event envelope | M15 | M19/T3/T4 | `test_event_envelope_schema_stable_for_ws_and_outbox` |
| Audit writer | M12 | M11/M13/M14/M17 | `test_audit_writer_append_only_tenant_scoped_chain` |
| ActionContext | M10 | M11/M13 | `test_action_context_schema_accepts_classifier_output` |
| PolicyDecision | M11 | M13/LLM adapter | `test_policy_decision_blocks_before_provider_call` |
| DraftOutput | M13 | M14/M19 | `test_draft_review_event_contains_output_id_and_review_status` |
| OutcomeEntry | M14 | M17 | `test_learning_candidate_created_only_from_reviewed_outcome` |
| Memory API | M17 | Prompt assembly | `test_disputed_memory_excluded_from_prompt` |
| Desktop cursor | M19 | M15 WS | `test_ws_since_cursor_replays_delta_or_sync_required` |
| Update pre-check | M20 | M13/M19 | `test_update_install_blocked_until_no_pending_mutations_and_synced` |

---

# 6. RIESGOS P0/P1 + KILL CRITERIA

## Riesgos P0

1. **Cross-tenant leak por Celery stale tenant_id.**  
   Mitigacion: M16 base task con transaction boundary, `set_config(..., true)`, assert, cleanup y test worker A->B.

2. **LLM egress bypass del D9 Policy Gate.**  
   Mitigacion: LiteLLM Proxy como unico egress; secrets fuera de Django/Celery; CI bloquea SDK directos.

3. **pgvector HNSW global para N2+.**  
   Mitigacion: particion por tenant o exact search para N2+; test `EXPLAIN`.

4. **Audit no append-only o chain global.**  
   Mitigacion: hash chain tenant-scoped; triggers NO UPDATE/DELETE; app role sin update/delete.

5. **Electron token leak por localStorage/preload inseguro.**  
   Mitigacion: session partition + httpOnly cookies + keychain; renderer sin token.

## Riesgos P1

1. Shadow/active sin UX de evidencia: skill no aprende o se promueve sin evidencia.
2. Offline desktop stale permite aprobar datos viejos.
3. Auto-update reinicia mid-task y pierde drafts.
4. Memory Letta contradice KB vigente sin `MemoryConflictGuard`.
5. Eventing duplica drafts si outbox/dedupe no esta cerrado.

## Kill criteria E0-E3

- `>=1` incidente privacy cross-tenant confirmado: kill/replan inmediato.
- N3/N4 sale a provider sin DPA: kill/replan inmediato.
- D9 no puede evaluar classification: fail-closed; si se cae abierto, kill.
- RLS test suite M16 falla en main: no abrir tracks.
- Edit rate E2 >=60% en 30 drafts reales: congelar y replantear skill/prompt/KB.
- E2.5 sin >=3 compromisos pagos/LOI: E3 multi-tenant externo no arranca.
- Electron update sin firma o con auto-restart mid-task: bloquear release.

---

# 7. PENDIENTES-CEO Y CONTRADICCIONES KB

## Pendientes CEO que bloquean tracks

| Pendiente | Bloquea | Fuente | Decision requerida |
|---|---|---|---|
| TTL exacto de sesion server-side y recordar dispositivo | M08/M18 | SPEC_FB_FUNC_M08_AUTH_SESSION_v1 | Valor TTL y politica remember-device |
| Email provider para invites/verificacion | M07/M08 | SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1 / SPEC_FB_AUTH_TENANT_RBAC | SendGrid/SES/otro |
| DPA in-wizard vs offline | M07/M11 | SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1 | Estado `signed` como prerequisito tecnico |
| Roles visibles E1: solo Owner/Operator vs 5 deshabilitados | M07/M09 | SPEC_FB_FUNC_M09_RBAC_v1 | UI bootstrap |
| Admin audit completo o limitado | M09/M12 | SPEC_FB_FUNC_M09_RBAC_v1 | Matriz permiso audit |
| Set completo de eventos E1 vs 28 canonicos | M15 | SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1 | Subset E1 congelado |
| 5 tests cross-tenant exactos CI | M16 | SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1 | Ratificar lista de este plan o reemplazar |
| Umbral N2+ para pgvector particionado | M16/M17 | SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1 | Confirmar particion para N2+ |
| MemoryConflictGuard exacto | M17 | SPEC_FB_FUNC_M17_MEMORY_LETTA_v1 | Exact match vs semantico |
| Acciones permitidas offline lectura/redaccion local | M19 | SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1 | Permitir o bloquear borrador local |
| Feed HTTPS auto-update | M20 | SPEC_FB_FUNC_M20_AUTO_UPDATE_v1 | Host/canal/cadencia |

## Contradicciones KB detectadas -- NO resolver en este plan

| ID/version | Contradiccion | Impacto | Tratamiento |
|---|---|---|---|
| SPEC_FB_BUILD_SEQUENCE v3.0 vs PLAN_DESARROLLO_FABERLOOM_v5 | v3 server/SaaS secuencial vs v5 desktop/web dual y FastAPI/SQLite | Fuente de verdad duplicada | Este v6 supersede v5 como plan modular; no edita v3 |
| PLB_FB_FOUNDATION_BETA_v1 vs ENT_FB_DECISIONES_E1_v1 | Email-only/WhatsApp diferido vs omnicanal desde S1A | Canales bootstrap y scope E1 | [PENDIENTE -- NO INVENTAR] decision CEO |
| SPEC_FB_AUTH_TENANT_RBAC_v1 vs stack actual | FastAPI/app-native mencionado vs Django 4.2 canon del prompt | Implementacion auth | Este plan usa Django; actualizar spec separado despues |
| ARCH_AGENT_PRINCIPLES P4 vs ENT_FB_DECISIONES_E1 D5 | Shadow threshold 3 vs 20 | Promotion skills | [PENDIENTE -- NO INVENTAR] aplicar decision arquitectonica separada si ratificada |
| ENT_FB_DECISIONES_E1 D6 vs SCH_FB_SKILL_MANIFEST_v2 | 3 archetypes vs 7 manifest archetypes | Runtime TIER 1 | [PENDIENTE -- NO INVENTAR] aplicar decision arquitectonica separada si ratificada |
| SPEC_FB_FUNC_M07/M09 | 5 roles schema vs 2 roles activos E1 | UI roles | Este plan asume schema 5, UI E1 Owner/Operator salvo decision CEO |
| PLAN_DESARROLLO_v5 | FastAPI/SQLite desktop single-user | Stack canon actual Django/Postgres multi-tenant | Este v6 usa stack canon del prompt |

---

# 8. SINTESIS CRUZADA

## Spine en una linea

M16 aislamiento -> M08 sesion -> M09 permisos -> M15 eventos -> M12 audit -> M11 policy -> M07 tenant active; despues se forkearan tracks.

## Tracks paralelos posibles

| Track | Modulos | Puede correr en paralelo con | Confianza |
|---|---|---|---|
| T0 Tenant Activation | M07 | T1/T2/T3 despues del SPINE | MEDIA |
| T1 AI Work Pipeline | M10/M11/M13 | T2/T3/T4 | ALTA |
| T2 Learning/Memory | M14/M17 | T1 con fixtures, T3 | MEDIA |
| T3 Desktop Runtime | M18/M19/M20 | T1/T2/T4 con mocks | ALTA |
| T4 Eventing hardening | M15 | T1/T3 si envelope congelado | ALTA |

## Top 5 integration risks

1. **M16 incompleto antes de forkear:** cualquier track puede introducir leak cross-tenant.
2. **M11 como library sin egress enforcement:** LLM calls pueden saltarse classification/audit.
3. **M15/M12 divergentes:** eventos operativos y audit trail pueden contar historias distintas.
4. **M13/M14 contrato pobre:** feedback humano no se convierte en outcome medible ni aprendizaje seguro.
5. **M18/M19/M20 no coordinados:** desktop puede operar stale, perder sesion o reiniciar mid-task.

## Confianza por track

- T0 Tenant Activation: MEDIA. Depende de decisiones CEO sobre DPA, roles visibles e invites.
- T1 AI Work Pipeline: ALTA. Contratos son claros si D9 fail-closed y HITL absoluto se mantienen.
- T2 Learning/Memory: MEDIA. MemoryConflictGuard y gate persistent requieren decisiones finas.
- T3 Desktop Runtime: ALTA. M18-M20 ya estan bien delimitados y no requieren tocar core AI.
- T4 Eventing hardening: ALTA. Outbox + Redis Streams es contrato estable y acotado.

---

## CHANGLELOG

- v1.0 (2026-06-25): Creacion de plan modular distribuido contract-first E0-E3. Supersede PLAN_DESARROLLO_FABERLOOM_v5 como plan operativo. Integra M07-M20 como contratos paralelizables con SPINE serial minimo, tests cross-tenant M16 obligatorios, DAG, riesgos P0/P1, kill criteria y pendientes CEO.
