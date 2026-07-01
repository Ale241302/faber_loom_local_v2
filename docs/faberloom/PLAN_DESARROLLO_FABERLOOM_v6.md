# PLAN_DESARROLLO_FABERLOOM_v6 -- Plan de Desarrollo Modular Distribuido E0-E3 (sintesis Fugu + Kimi)
id: PLAN_DESARROLLO_FABERLOOM_v6
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: DRAFT -- 2026-06-25 -- sintesis cruzada Fugu+Kimi; supersede v5 pendiente ratificacion CEO
aprobador: CEO
aplica_a: [FaberLoom]
supersede: PLAN_DESARROLLO_FABERLOOM_v5.md (orden operativo de build E0-E3; pendiente ratificacion CEO)
relacionado: PLAN_DESARROLLO_FABERLOOM_v6_fugu.md - PLAN_DESARROLLO_FABERLOOM_v6_KIMI.md - SPEC_FB_BUILD_SEQUENCE_v3.md - PLB_FB_FOUNDATION_BETA_v1.md - SPEC_FB_ROUTING_PRESETS_v1.md - SPEC_FB_EVENTING_AND_OUTBOX_v1.md - SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_FUNC_M07..M20 - PLB_PROMPTING_FUGU_KIMI_v1.md - PLB_AUDIT_PATTERN_v1.md - docs/anexos/kimi_swarm_audit_faberloom/a9_sintesis.md

---

## 0. Metodo de sintesis (patron dual)

Este v6 es la sintesis cruzada de dos corridas autonomas del mismo prompt
(PROMPT_PLAN_MODULAR_DISTRIBUIDO_v1) sobre PLAN-MOD-2026-06-24/25:
- PLAN_DESARROLLO_FABERLOOM_v6_fugu.md (Fugu Ultra).
- PLAN_DESARROLLO_FABERLOOM_v6_KIMI.md (Kimi Agent).
Regla de arbitraje (PLB_PROMPTING_FUGU_KIMI_v1 Sec.5): coinciden -> nucleo de alta
confianza; divergen -> decision CEO; uno vio y el otro no -> blind spot incorporado.
Decisiones CEO aplicadas (2026-06-25):
- Corte de tracks: HIBRIDO (flujo de Fugu + Bootstrap como track propio + M14/M17
  separables).
- Stack: v6 STACK-AGNOSTIC. STACK-01 se trata como decision #1 de E0; no se hornea
  ningun stack ni infra. Se descarta el detalle de infra inventado por Fugu
  (versiones exactas, proveedor de hosting): NO es canonico.

## 1. Plan de orquestacion

1. Tipo de problema: build MODULAR y DISTRIBUIDO (contract-first) de M07-M20, E0-E3.
2. Descomposicion: cada modulo es unidad independiente que expone un CONTRATO estable.
3. Especialistas por dominio: RLS/multi-tenant, auth/security, eventing/audit,
   policy/compliance, ML classifier, HITL/UX, learning/curator, memory/Letta,
   Electron/desktop, release engineering.
4. Estrategia: parallel execution + bring-in-specialist; debate-and-aggregation solo
   para particionar tracks.
5. Verificacion: integridad de contratos; los 5 tests cross-tenant de M16 deben pasar
   antes de forkear cualquier track.

## 2. Principio rector -- CONTRACT-FIRST

Cada modulo se construye independiente porque expone un contrato estable: inputs,
outputs, eventos emitidos/consumidos, schemas, RLS y campos de audit D10. Los tracks
distribuidos NO comparten estado interno; solo se acoplan por contratos versionados,
eventos canonicos y tablas/schemas declarados. Un modulo puede empezar cuando los
contratos que CONSUME estan congelados y existen contract tests, aunque la
implementacion interna del productor no este completa (se usan stubs/fixtures con
version explicita; la integracion real se firma en el punto de verificacion del track).

## 3. STACK-01 -- decision #1 de E0 (BLOQUEANTE, NO RESUELTA)

El stack NO esta ratificado y este plan NO lo fija. Hay contradiccion entre fuentes:
- PLB_FB_FOUNDATION_BETA_v1: FastAPI + Next.js + Postgres + Redis + Celery + LiteLLM
  Proxy + contenedores.
- PLAN_DESARROLLO_FABERLOOM_v5: FastAPI + LiteLLM lib + desktop/web dual + SQLite/Postgres.
- ENT_PLAT_INFRA (citado en a9_sintesis): Django + Celery + Redis.
[PENDIENTE -- NO INVENTAR] El CEO ratifica en E0 (S0) cual es el stack canonico unico
antes de iniciar S1. Hasta entonces los modulos se especifican por contrato (agnostico
de framework). Nota: ambos motores asumieron Django de facto; Fugu ademas invento
versiones y hosting (Django 4.2 / Postgres 16 / "Hostinger KVM 8") que se descartan por
no ser canonicos.

---

# 4. SPINE SERIAL -- orden minimo obligatorio

El SPINE congela los contratos transversales que todos los tracks consumen. Ningun
track operativo arranca antes de pasar los 5 tests cross-tenant de M16 (Sec.8.1).

| Paso | Modulo(s) | Talla | Especialista | Contrato a congelar | Gate de salida |
|---|---|---|---|---|---|
| S0 | E0 -- decisiones CEO + dataset + STACK-01 | S | CEO + Partitioner | Alcance E1 cerrado; 30 casos reales (o scope reducido firmado) + 10 holdout; baseline Claude-crudo; dedicacion Alejandro; STACK ratificado | CEO firma go; stack unico definido |
| S1 | M16 + M08 (co-build) | L | RLS/multi-tenant + auth | tenant_context, RLS, prefijos Redis/Celery/MinIO/pgvector/LiteLLM/Letta; sesion server-side con tenant_id; cookie httpOnly / particion Electron | 5 tests cross-tenant M16 pasan; login basico; query sin tenant_id = 0 filas |
| S2 | M09 | M | RBAC/compliance | membership, hat activo, permission check, actor_role_at_decision | 5 roles seedeados; invitar/suspender; permission.denied auditado |
| S3 | M15 + M12 (co-build) | L | eventing + audit | event envelope, outbox transaccional, Redis Stream por tenant, last_event_id, sync_required; audit append-only + SHA-chain tenant-scoped | evento de prueba via outbox llega a WS; audit no editable; job de validacion de cadena OK |
| S4 | M11 | M | policy/compliance | ActionContext, effective_classification, hard-block N3/N4, pre-egress mismatch, DPA state, PlanUpgradeRequired | hard-block N3/N4 sin DPA; fail-closed; eventos policy.gate.* |

Razon co-builds: M16+M08 (M08 provee tenant_id que M16 usa; M16 protege las tablas de
sesion). M15+M12 (el audit durable usa el outbox para no perder escrituras).
M07 NO esta en el spine: es un track propio (T0) que consume los contratos del spine.

## SPINE -- criterios de aceptacion

1. Request autenticado porta tenant_id desde sesion server-side, nunca desde header de cliente.
2. Toda query aislable falla cerrada si falta app.tenant_id.
3. Todo evento de negocio se escribe en Postgres + outbox en la misma transaccion.
4. Todo audit entry tiene tenant_id, actor_role_at_decision, sha_chain_prev/curr, chain tenant-scoped.
5. D9 bloquea N3/N4 sin DPA antes de cualquier llamada LLM o salida externa.

---

# 5. TRACKS PARALELOS (corte hibrido)

Tras cerrar el SPINE (S0-S4), forkean en paralelo. Cada track avanza si los contratos
que consume estan congelados; puede usar stubs/fixtures versionados mientras tanto.

## T0 -- Bootstrap / Tenant Activation (M07)
- Especialista: tenant onboarding + compliance ops. Talla: M.
- Can-start-when: M08/M09/M11/M12/M16 congelados. No requiere UI desktop.
- Consume: M08 (login Owner+2FA), M09 (roles/permiso), M11 (DPA state + ceiling),
  M12 (audit writer), M16 (aislamiento).
- Expone: tenant.status (setup/active/blocked), tenant.config, membership Owner/Operator,
  dpa_state (missing/signed/blocked), seed skills en shadow; eventos tenant.created,
  user.invited, user.2fa_enabled, mailbox.connected, document.uploaded, tenant.activated.
- Aceptacion: tenant MWT de cero a active < 1h sin datos cross-tenant; Owner invita
  Operator; DPA missing bloquea N3/N4; seed skills quedan shadow (no pueden enviar externo).
- Tests: test_bootstrap_creates_owner_operator_only_in_e1;
  test_bootstrap_blocks_activation_when_dpa_required_missing;
  test_seed_skills_are_shadow_and_cannot_external_send.

## T1 -- AI Work Pipeline / Inbound -> Draft -> HITL (M10 + M13)
- Especialistas: ML classifier + HITL/UX (M11 ya congelado en spine; aqui se ejerce su enforcement). Tallas: M10=L, M13=L.
- Can-start-when: spine M16/M08/M09/M15/M12/M11 congelados; M13 puede iniciar con fixtures de output del agente.
- Consume: M15 (feed.item.received, task.created, event writer), M16 (RLS), M12 (audit),
  M09 (permiso approve/edit/reject), M11 (PolicyDecision).
- Expone: ActionContext (task_type, data_class, skill_id, confidence, routing, tenant_id);
  DraftOutput por output (draft_id, output_id, review_status); eventos feed.item.dispatched,
  task.created, draft.generated/approved/edited/rejected/sent.
- Aceptacion: un RFQ real MWT genera draft en WorkLoom sin envio externo automatico; si L1
  clasifica N1 pero pre-egress detecta N3, D9 bloquea fail-closed; aprobacion por output;
  human_approver_id obligatorio antes de cualquier external_communication/mutation.
- Tests: test_l1_classifier_outputs_action_context_schema;
  test_d9_pre_egress_classification_mismatch_blocks_provider_call;
  test_external_draft_requires_human_approver_id_before_send.

## T2 -- Outcome Ledger / Learning (M14)
- Especialista: learning pipeline + Curator. Talla: M.
- Can-start-when: M12 audit + M16 + contrato de review events de M13 (draft.approved/edited/rejected). Puede usar fixtures de eventos de M13.
- Consume: M13 (decisiones HITL), M10 (correcciones de clasificacion), M12.
- Expone: OutcomeEntry (review_status, edit_distance, reason_code, skill_version);
  LearningCandidate; gold sample CANDIDATE/ACTIVE/discarded/deprecated; Learning Thermometer
  Cold/Warm/Hot; eventos outcome.recorded, gold.candidate.created, gold.promoted, gold.deprecated.
- Aceptacion: feedback de draft aprobado crea OutcomeEntry y NO promueve gold automaticamente;
  candidato gold solo de aprobado-sin-edicion + confidence HIGH; segundo aprobador N2+ funciona.
- Tests: test_outcome_recorded_from_draft_review_event;
  test_learning_candidate_created_only_from_reviewed_outcome;
  test_gold_promotion_requires_second_approver_for_n2_plus.

## T3 -- Agent Memory (M17)
- Especialista: memory containment / Letta. Talla: M.
- Can-start-when: M16 congelado (M15 recomendado para eventos, no bloqueante). Separable de T2.
- Consume: contexto de ejecucion, KB VIGENTE, M16 (namespace), M12.
- Expone: episodic (append-only), working (TTL 24h, namespace mem:tenant:{tid}:agent:{aid}:task:{tid}:working),
  persistent (gate humano), estados active/disputed/deprecated; eventos memory.persisted/disputed/deprecated.
- Aceptacion: agente lee working+episodic+KB sin contradecir KB; persistent solo con gate;
  MemoryConflictGuard marca disputed y NO inyecta; sin leak cross-profile.
- Tests: test_working_memory_namespace_includes_task_id_and_cleans_on_terminal_state;
  test_disputed_memory_not_injected_into_prompt;
  test_letta_namespace_blocks_cross_tenant_profile_access.

## T4 -- Desktop Runtime / Electron (M18 -> M19 -> M20)
- Especialistas: Electron security + realtime/offline + release engineering. Tallas: M c/u.
- Can-start-when: M08/M15/M16 congelados; M13 contract para pending mutations. Internamente serial (M19 necesita M18; M20 necesita M18+M19). Puede arrancar con WS mock de M15 y /auth/me mock de M08.
- Consume: M08 (/auth/me), M16 (sesion tenant-scoped), M15 (WS ?since=last_event_id, sync_required), M13 (pending mutations).
- Expone: particion persist:faberloom-{profile}; cursores no-secretos (last_event_id, last_sync_at, tenant_id, client_version); update lifecycle (checking/downloaded/ready_to_install/blocked_min_supported); UI states (connected/disconnected/syncing/sync_required/read_only_offline).
- Aceptacion: renderer no lee token/sesion; restart tras 2h offline recupera con full fetch + WS since; sin aprobaciones offline en S1A; update nunca reinicia mid-task.
- Tests: test_renderer_cannot_read_session_token;
  test_last_event_id_persisted_across_app_restart_and_reconciles;
  test_update_does_not_install_with_pending_mutations.

## T5 -- Eventing hardening (M15 post-spine)
- Especialista: eventing/realtime. Talla: M. (Blind spot aportado por Fugu.)
- Can-start-when: envelope de M15 congelado + prefijo tenant de M16. Avanza en paralelo mientras no cambie el event envelope.
- Expone: entrega at-least-once con dedupe por event_id; hidratacion de UI; reconnect ?since + sync_required.
- Aceptacion: DB commit + Redis publish nunca se separan sin outbox; duplicados ignorados por event_id; tenant A nunca recibe stream de B.
- Tests: test_outbox_publishes_after_business_transaction_commit;
  test_duplicate_event_id_processed_once;
  test_ws_fanout_filters_by_tenant_and_permission.

---

# 6. REGISTRO DE CONTRATOS MODULO -> MODULO

| Modulo | Expone | Consume | RLS/Audit obligatorio |
|---|---|---|---|
| M16 Tenant Isolation | tenant_context + reglas de aislamiento (RLS, prefijos Redis/Celery/MinIO, pgvector partition, LiteLLM ctx, Letta namespace); evento cross_tenant.access_attempted | M08 (tenant_id) | FORCE RLS; base de todo |
| M08 Auth Session | session_id, tenant_id, user_id, active_hat; eventos auth.* | M16 | audit auth; sesion Redis scoped |
| M09 RBAC | permission decision, actor_role_at_decision; eventos user.role_changed, permission.denied | M08 | audit cada cambio de rol; RLS membership |
| M15 Outbox Streams | event log, outbox, Redis Stream por tenant, WS protocol (?since/sync_required) | M16, M12 (audit critico) | stream por tenant; dedupe por event_id |
| M12 Audit Trail | AuditEntry append-only + SHA-chain; export | M16, M09 (actor), M15 (envelope) | chain tenant-scoped; sin UPDATE/DELETE |
| M11 D9 Policy Gate | PolicyDecision, effective_classification, PlanUpgradeRequired/ClassificationMismatch; eventos policy.gate.* | M10 (schema), M07 (DPA), M12 | fail-closed; audit cada bloqueo |
| M07 Bootstrap Wizard | tenant, membership, dpa_state, seed skills shadow; eventos tenant.*, mailbox.*, document.* | M08, M09, M11, M12, M16 | tenant_id en todo; audit D10 de activacion |
| M10 L1 Classifier | ActionContext | feed_item, Tier 0, work-type pack/KB de M07, M11 | audit classification; sin side-effect externo |
| M13 Draft HITL | DraftOutput, review state, gate de envio externo; eventos draft.* | M09, M11, M12, M15 | human_approver_id para acciones externas |
| M14 Outcome Ledger | OutcomeEntry, LearningCandidate, gold samples, Thermometer; eventos outcome.*, gold.* | M13 (review events), M10, M12 | audit promociones gold/persistent |
| M17 Memory Letta | episodic/working/persistent API, disputed marks; eventos memory.* | M14, M16, KB VIGENTE, M12 | working por task_id; persistent gate humano; episodic append-only |
| M18 Electron Auth | particion segura por tenant; secretos en keychain; evento desktop.login | M08, M16 | sin localStorage para tokens |
| M19 Offline Sync | cursores persistidos + estado de sync | M15, M18, M13 | sin aprobaciones offline; revalida tenant antes de sync |
| M20 Auto Update | ciclo de update firmado | M18, M19, M13 | sin datos de tenant en el update; sin restart mid-task |

---

# 7. DAG DE DEPENDENCIAS

```text
M16 Tenant Isolation
  -> M08 Auth Session
      -> M09 RBAC
      -> M18 Electron Auth -> M19 Offline Sync -> M20 Auto Update
  -> M15 Outbox Streams
      -> M19 Offline Sync
      -> M15 hardening (T5)
  -> M12 Audit Trail
      -> M11 D9 Policy Gate
      -> M13 Draft HITL
      -> M14 Outcome Ledger
      -> M17 Memory Letta
  -> M07 Bootstrap Wizard (T0)

M10 L1 Classifier -> M11 -> M13 -> M14
M13 -> M19 (pending mutations) / M20 (pre-install checks)
```

Bloqueos duros: M16 bloquea todo lo tenant-scoped; M08 bloquea M09/M18/M07; M09 bloquea
toda aprobacion HITL y cambios de rol; M12 bloquea M11/M13/M14/M17 (acciones sensibles);
M11 bloquea toda LLM/provider call con N2+ y todo output externo; M15 bloquea M19 y todo
realtime WorkLoom confiable.
Paralelizable tras spine: T0 (stubs DPA), T1 (M13 con fixtures), T2 (fixtures de review),
T3 (solo M16), T4 (mocks WS/auth), T5 (envelope congelado).

---

# 8. INTEGRATION POINTS + CONTRACT TESTS

## 8.1 Tests cross-tenant M16 (obligatorios ANTES de abrir cualquier track)
Convergentes en los 2 motores; [PENDIENTE -- NO INVENTAR] ratificar la lista exacta en CI.
1. test_postgres_rls_same_worker_tenant_a_then_b_no_cross_read -- mismo proceso ejecuta A y luego B; B no ve filas de A.
2. test_celery_with_tenant_session_clears_context_after_exception -- job A falla; job B no hereda app.tenant_id ni cache.
3. test_redis_stream_and_cache_keys_require_tenant_prefix -- key sin tenant:{id}: falla lint/runtime; WS de B no recibe evento de A.
4. test_pgvector_n2_plus_uses_tenant_partition_not_global_hnsw -- EXPLAIN prueba partition pruning para N2+.
5. test_letta_namespace_blocks_cross_tenant_profile_access -- agente A no lee/inyecta memoria de B; emite cross_tenant.access_attempted (P0).

## 8.2 Contract tests entre modulos
| Punto | Productor | Consumidor | Test |
|---|---|---|---|
| Tenant context | M08/M16 | Todos | test_request_without_server_tenant_context_fails_closed |
| Permission | M09 | M13/M07/admin | test_permission_check_required_for_sensitive_endpoint |
| Event envelope | M15 | M19/T4/T5 | test_event_envelope_schema_stable_for_ws_and_outbox |
| Audit writer | M12 | M11/M13/M14/M17 | test_audit_writer_append_only_tenant_scoped_chain |
| ActionContext | M10 | M11/M13 | test_action_context_schema_accepts_classifier_output |
| PolicyDecision | M11 | M13/LLM adapter | test_policy_decision_blocks_before_provider_call |
| DraftOutput | M13 | M14/M19 | test_draft_review_event_contains_output_id_and_review_status |
| OutcomeEntry | M14 | M17 | test_learning_candidate_created_only_from_reviewed_outcome |
| Memory API | M17 | Prompt assembly | test_disputed_memory_excluded_from_prompt |
| Desktop cursor | M19 | M15 WS | test_ws_since_cursor_replays_delta_or_sync_required |
| Update pre-check | M20 | M13/M19 | test_update_install_blocked_until_no_pending_mutations_and_synced |
| DPA -> ceiling | M07 | M11 | test_dpa_signed_raises_ceiling_for_tenant |

---

# 9. RIESGOS P0/P1 + KILL CRITERIA

## 9.1 P0 (bloquean o matan)
1. Cross-tenant leak por Celery stale tenant_id -- M16 base task con boundary + set_config + assert + cleanup + test A->B.
2. LLM egress bypass del D9 [blind spot Fugu] -- LiteLLM Proxy como UNICO egress; secrets fuera de Django/Celery; CI bloquea SDK directos.
3. pgvector HNSW global para N2+ [blind spot Fugu] -- particion por tenant o exact search N2+; test EXPLAIN.
4. Audit no append-only o chain global -- hash chain tenant-scoped; triggers sin UPDATE/DELETE; app role sin update/delete.
5. Auto-send sin HITL -- state machine server-side; 0 boton de envio automatico.
6. Token/session leak en Electron -- particion + httpOnly + keychain; renderer sin token.
7. Evento de negocio perdido sin outbox -- outbox transaccional; relay idempotente; DLQ.

## 9.2 P1
1. Shadow/active sin UX de evidencia. 2. Offline desktop stale permite aprobar datos viejos.
3. Auto-update reinicia mid-task. 4. Memory contradice KB sin MemoryConflictGuard.
5. Eventing duplica drafts si dedupe no cerrado. 6. M10 threshold 0.85 vs routing 3 capas
(ECU/preset/curva). 7. M12 campos audit 12 vs 18 sin canonizar. 8. Roles 5 vs 2 en E1 (UI).

## 9.3 Kill criteria
1. >=1 incidente privacy cross-tenant = kill/replan inmediato.
2. N3/N4 sale a provider sin DPA = kill/replan inmediato.
3. D9 no puede evaluar y se cae abierto = kill.
4. Tests cross-tenant M16 fallan en main = no abrir tracks.
5. Edit rate >= 60% en 30 drafts reales (E2) = congelar/replantear.
6. STACK-01 no ratificado en E0 = no iniciar SPINE.
7. M15 pierde eventos en test de crash = no abrir WorkLoom.
8. E2.5 sin >=3 compromisos pagos/LOI [blind spot Fugu] = E3 multi-tenant externo no arranca.
9. Electron update sin firma o con auto-restart mid-task = bloquear release.

---

# 10. PENDIENTES-CEO QUE BLOQUEAN TRACKS

SPINE / E0:
1. [STACK-01] Ratificar stack canonico unico (Sec.3) -- bloquea S1.
2. [M16] Confirmar los 5 tests cross-tenant exactos del CI; umbral N2+ para pgvector particionado.
3. [M08] TTL de sesion server-side; politica remember-device; hash (argon2id); cooldown lockout 2FA.
4. [M09] E1 expone solo Owner/Operator o 5 roles deshabilitados; Admin ve audit completo o scope.
5. [M12] Set canonico final de campos D10 (12 del SCH vs 18 de M12); formato de export auditores.
6. [M15] Subset E1 de eventos (6) vs 28 canonicos congelado.
7. [gobernanza] Ratificar que v6 supersede v5 como orden de build E0-E3.

T0 Bootstrap: WhatsApp BSP visible-diferido u oculto (E-5); DPA e-sign in-wizard u offline;
  email provider invites (SendGrid/SES); seed work-type pack safety_footwear; rutinas base seed.
T1 AI Pipeline: pesos/normalizacion de los 13 features FG-03; interaccion threshold 0.85 con
  routing 3 capas; versionado del modelo; default Haiku vs Sonnet de classify_rfq;
  Oscillation Counter N; timeout/vida del draft; evidence bundle para drafts no-cotizacion.
T2 Outcome: umbrales Learning Thermometer; segundo aprobador N2+; criterio para deprecar gold malo.
T3 Memory: MemoryConflictGuard exact vs semantico; TTL sweeper stale; gate persistent (Owner/Curator).
T4 Desktop: TTL reanudacion; naming de profile; keychain no disponible; acciones offline-lectura;
  reintentos/backoff; feed HTTPS host/canal; 5 tenants beta + promocion; cadencia min_supported.

---

# 11. CONTRADICCIONES KB (id+version, NO RESUELTAS)

| # | Codigo | Documentos | Impacto | Bloquea |
|---|---|---|---|---|
| C1 | STACK-01 | PLB_FB_FOUNDATION_BETA_v1 vs PLAN_v5 vs ENT_PLAT_INFRA | Stack no ratificado (FastAPI vs Django vs dual) | S0/S1 -- decision #1 |
| C2 | ROLES-01 | SCH_FB_FUNCTIONAL_SPEC_v1 vs PLB_FB_FOUNDATION_BETA E-4 | 5 roles vs 2 (Owner/Operator) en E1 | M07/M08/M09/M13 UI |
| C3 | WHATSAPP-01 | SPEC_FB_FUNC_M07_v1 paso 4 vs PLB E-5 | WhatsApp en wizard vs email-only E1-E2 | M07 paso 4 |
| C4 | AUDIT-01 | SCH_FB_FUNCTIONAL_SPEC_v1 D12.2 vs SPEC_FB_FUNC_M12_v1 | 12 vs 18 campos D10 | M12 schema |
| C5 | EVIDENCE-01 | SPEC_FB_FUNC_M13_v1 vs SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1 | bundle generico vs solo-cotizacion | M13 schema bundle |
| C6 | ROUTING-01 | SPEC_FB_FUNC_M10_v1 vs SPEC_FB_ROUTING_PRESETS_v1 | threshold 0.85 vs 3 capas ECU/preset/curva | M10 integracion presets |
| C7 | EVENTS-01 | SPEC_FB_EVENTING_AND_OUTBOX_v1 vs SPEC_FB_FUNC_M15_v1 | 28 eventos vs subset E1 de 6 | M15 set E1 |
| C8 | BETA-01 | SPEC_FB_FUNC_M20_v1 vs PLB E-4 / SPEC_FB_BUILD_SEQUENCE_v3 | beta 5-tenants vs E1 single-tenant interno | M20 alcance beta |
| C9 | SHADOW-THRESH | ARCH_AGENT_PRINCIPLES P4 vs ENT_FB_DECISIONES_E1 D5 | shadow threshold 3 vs 20 | promocion skills |
| C10 | ARCHETYPES | ENT_FB_DECISIONES_E1 D6 vs SCH_FB_SKILL_MANIFEST_v2 | 3 vs 7 archetypes | runtime TIER 1 |
| C11 | DESKTOP-OVERLAP | SPEC_FB_FUNC_M08_v1 vs SPEC_FB_FUNC_M18_v1 | solapamiento auth web/Electron | mantenimiento M08/M18 |

[PENDIENTE -- NO INVENTAR] El CEO resuelve o acepta documentar C1-C11 antes de iniciar
cada track afectado. Este plan NO las resuelve. C9 y C10 fueron detectadas solo por Fugu
(blind spot); C8 solo por Kimi.

---

# 12. SINTESIS CRUZADA

## 12.1 Spine en una linea
M16 aislamiento -> M08 sesion -> M09 permisos -> M15 eventos -> M12 audit -> M11 policy;
luego forkean T0-T5. Sin esto no hay tracks paralelos.

## 12.2 Procedencia (auditabilidad de la sintesis)
- Convergente (ambos): contract-first; spine y su orden; 5 tests cross-tenant como gate;
  HITL absoluto; D9 fail-closed; audit append-only; kill criteria de privacy/N3-N4/edit-rate.
- Solo Fugu (incorporado): T5 eventing hardening; P0 de LLM egress bypass; P0 de pgvector
  N2+; tests de contrato nombrados; kill criterion E2.5 >=3 LOI.
- Solo Kimi (incorporado): tabla de contradicciones con id+version; pendientes-CEO granulares;
  C8 beta vs single-tenant.
- Divergencia resuelta por CEO: corte de tracks = hibrido; stack = agnostico (STACK-01 a E0).

## 12.3 Top 5 integration risks
1. M16 incompleto antes de forkear -> leak. 2. M11 como library sin egress enforcement
-> LLM se salta classification/audit. 3. M15/M12 divergentes -> eventos y audit cuentan
historias distintas. 4. M13/M14 contrato pobre -> feedback no se vuelve outcome medible.
5. M18/M19/M20 no coordinados -> desktop stale, pierde sesion o reinicia mid-task.

## 12.4 Confianza por track
| Track | Confianza | Razon |
|---|---|---|
| SPINE | MEDIA | STACK-01 (C1) y roles (C2) sin resolver; resueltos, M16/M08/M15/M12 son estandar |
| T0 Bootstrap | MEDIA | depende de DPA, WhatsApp, roles visibles |
| T1 AI Pipeline | ALTA | bien especificado; riesgo = mantener D9 fail-closed y HITL absoluto |
| T2 Outcome | MEDIA | umbrales Thermometer y segundo aprobador requieren decision |
| T3 Memory | MEDIA | Letta + MemoryConflictGuard + aislamiento namespace son los puntos finos |
| T4 Desktop | ALTA | M18-M20 bien delimitados; incertidumbre = keychain cross-plataforma y feed |
| T5 Eventing | ALTA | outbox + Redis Streams es contrato estable y acotado |

---

# 13. CHECKLIST GO/NO-GO antes de forkear tracks
- [ ] E0 cerrado: STACK-01 ratificado, 30 casos (o scope reducido), holdout, baseline, dedicacion Alejandro.
- [ ] 5 tests cross-tenant de M16 pasan en CI.
- [ ] M08 sesion server-side OK; M09 RBAC resuelve permisos.
- [ ] M15 outbox + M12 audit OK; evento de prueba llega a WS.
- [ ] M11 hard-block N3/N4 sin DPA demostrado.
- [ ] CEO resolvio o acepto documentar C1-C11 que bloquean el track a iniciar.
- [ ] Kill criteria comunicados al equipo.

---

Changelog:
- v1.0 (2026-06-25): Creacion. Sintesis cruzada de PLAN_DESARROLLO_FABERLOOM_v6_fugu +
  _KIMI (patron dual PLB_PROMPTING_FUGU_KIMI_v1 Sec.5). Corte de tracks hibrido (decision
  CEO); v6 stack-agnostic con STACK-01 como decision #1 de E0 (decision CEO). SPINE S0-S4 +
  6 tracks (T0-T5); registro de contratos; DAG; 5 tests cross-tenant M16; contract tests
  nombrados; P0/P1 + kill criteria; pendientes-CEO por track; 11 contradicciones KB sin
  resolver. Supersede v5 pendiente ratificacion CEO. Status DRAFT hasta ratificar STACK-01.

---

# 14. ENMIENDA v1.0-a (2026-06-25) -- Gate E0.5 de validacion de valor

Esta enmienda NO modifica la arquitectura, el spine, los tracks ni las 14 fichas.
Antepone un gate y reordena el gate de valor. Se documenta como append (no reescribe
secciones previas).

## 14.1 Cambio
- Se inserta un nuevo gate **E0.5 -- Validacion de valor**, ANTES de S1, definido en
  `SPEC_FB_E0_5_VALIDATION_SLICE_v1.md`: un slice single-tenant descartable del loop
  RFQ -> draft -> HITL contra 10-15 RFQs reales de MWT, que mide tiempo_ahorrado,
  edit_rate, send_rate y fallo_critico.
- **S1 del SPINE no arranca sin PASA de E0.5.** Si E0.5 FALLA: kill/replan antes de
  escribir una linea de spine.
- El kill criterion comercial/valor sube de E2.5 (>=3 LOI, Sec.9.3 #8) a **E0.5**: el
  valor se prueba al inicio, no despues de construir la plataforma. El gate de E2.5
  (>=3 LOI antes de E3 multi-tenant externo) se mantiene como gate posterior, no como
  el unico de valor.

## 14.2 Razon
Asimetria de costo: construir el SPINE son meses; probar valor son dias. El v6 era
correcto en COMO construir pero front-loadeaba la plomeria y diferia la prueba del
supuesto que puede matar el proyecto. E0.5 lo corrige sin tocar el diseno.

## 14.3 Bonus
E0.5 con casos reales de-riskea T1: aporta datos para resolver C5 (evidence bundle
no-cotizacion), C6 (threshold vs routing 3 capas) y los pesos de los 13 features FG-03,
hoy marcados [PENDIENTE].

## 14.4 Checklist actualizado (precede a la Sec.13)
- [ ] **E0.5 PASA** (SPEC_FB_E0_5_VALIDATION_SLICE_v1): valor probado en casos reales.
- (luego sigue el checklist Go/No-Go de la Sec.13).

---

Changelog (cont.):
- v1.0-a (2026-06-25): Enmienda. Inserta gate E0.5 de validacion de valor pre-S1
  (SPEC_FB_E0_5_VALIDATION_SLICE_v1) y eleva el gate de valor de E2.5 a E0.5. No cambia
  arquitectura/spine/tracks/fichas. Sigue DRAFT hasta ratificar STACK-01 + supersede v5
  + umbrales E0.5.

---

# 15. ENMIENDA v1.0-b (2026-06-25) -- Decision interno-primero; spine DIFERIDO

Decision CEO (2026-06-25): FaberLoom se construye PRIMERO como herramienta interna de
MWT; se externaliza ("sacarlo") solo tras probar funcionalidad con valor real.

Efecto sobre este v6:
- Este v6 (build modular distribuido multi-tenant) pasa a ser el **plano de la fase de
  EXTERNALIZACION**, NO el proximo build. El SPINE (M16/M08/M09/M15/M12/M11) y los tracks
  multi-tenant NO se construyen ahora.
- El proximo build es un slice single-tenant INTERNO del loop RFQ -> draft -> HITL,
  gateado por la secuencia de SPEC_FB_E0_5_VALIDATION_SLICE_v1 (v1.1): E0.1 data-readiness
  + E0.5 valor interno (shadow-replay) + E0.6 safety/catch-rate.
- El gate comercial EXTERNO (E0.25: LOI/pago de PYME ajena) se reposiciona como gate de
  EXTERNALIZACION (pre-spine v6), no pre-S1.
- E0.25 >=3 LOI (Sec.9.3 #8) sigue siendo gate de E3/multi-tenant externo.

Origen: red-team Kimi + Fugu (EVAL_E0_5_VALIDATION_*), ambos MATIZADO -- el valor interno
(tiempo ahorrado) nunca justifico por si solo el spine multi-tenant; eso lo justifica la
demanda externa, que se prueba al sacarlo.

No se modifica la arquitectura, el spine, los tracks ni las 14 fichas: cambia CUANDO se
construye el spine (en externalizacion, no ahora).

Changelog (cont.):
- v1.0-b (2026-06-25): Decision interno-primero. v6 = plano de externalizacion; spine
  diferido. Build inmediato = slice interno gateado por SPEC_FB_E0_5 v1.1.
