---
id: PLAN_DESARROLLO_FABERLOOM_v6_KIMI
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: DRAFT -- 2026-06-25 -- v6 modular distribuido contract-first (RUN_ID: PLAN-MOD-2026-06-24)
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: PLAN_DESARROLLO_FABERLOOM_v5.md · SPEC_FB_BUILD_SEQUENCE_v3.md · PLB_FB_FOUNDATION_BETA_v1.md · SPEC_FB_ROUTING_PRESETS_v1.md · SPEC_FB_EVENTING_AND_OUTBOX_v1.md · SCH_FB_FUNCTIONAL_SPEC_v1.md · SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1.md · SPEC_FB_FUNC_M08_AUTH_SESSION_v1.md · SPEC_FB_FUNC_M09_RBAC_v1.md · SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1.md · SPEC_FB_FUNC_M11_D9_POLICY_GATE_v1.md · SPEC_FB_FUNC_M12_AUDIT_TRAIL_v1.md · SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md · SPEC_FB_FUNC_M14_OUTCOME_LEDGER_v1.md · SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1.md · SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1.md · SPEC_FB_FUNC_M17_MEMORY_LETTA_v1.md · SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1.md · SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1.md · SPEC_FB_FUNC_M20_AUTO_UPDATE_v1.md · PLB_PROMPTING_FUGU_KIMI_v1.md · PLB_AUDIT_PATTERN_v1.md · docs/anexos/kimi_swarm_audit_faberloom/a9_sintesis.md
---

# PLAN DE ORQUESTACION

1. **Tipo de problema:** build **MODULAR y DISTRIBUIDO** (contract-first) de los 14 modulos funcionales M07-M20 de FaberLoom Foundation Beta (E0-E3).
2. **Descomposicion:** cada modulo (M07-M20) es una unidad independiente que expone un **CONTRATO** estable: inputs, outputs, eventos emitidos/consumidos, schemas, politicas RLS y campos de audit trail D10.
3. **Especialistas asignados por dominio de modulo:** Platform Architect (SPINE), RLS/multi-tenant, ML classifier / Action Engine, HITL/UX, Electron/desktop, eventing/audit.
4. **Estrategia:** `parallel execution` sobre tracks desacoplados + `bring-in-specialist` en riesgos de integracion + `debate-and-aggregation` **unicamente** para decidir la particion de tracks y el orden del SPINE.
5. **Puntos de verificacion:** integridad de contratos entre modulos; los **5 tests cross-tenant de M16** deben fallar/pass correctamente antes de forkear cualquier track; todo evento que cruza Postgres/Redis pasa por el outbox; todo output cliente-facing pasa por HITL.

**[SUPUESTO: este plan supersedee explicitamente PLAN_DESARROLLO_FABERLOOM_v5.md en orden/timeline; el contenido tecnico reusable de v5, BUILD_SEQUENCE_v3 y PLB_FB_FOUNDATION_BETA_v1 se conserva como referencia. Se autoriza la escritura directa en `docs/faberloom/` para esta corrida autonoma; la indexacion formal via `sync_*_indexa.ps1` se ejecuta en el flujo de sync posterior.]**

---

# PRINCIPIO RECTOR: CONTRACT-FIRST

Cada modulo se construye independiente porque expone un **CONTRATO** estable. Los tracks distribuidos **NO comparten estado interno**; solo dependen de los contratos publicados en este documento. Un builder de un track puede avanzar en paralelo si respeta:

- **Inputs:** schemas JSON/Pydantic esperados.
- **Outputs:** filas en tablas, eventos canonicos, respuestas HTTP.
- **Eventos:** solo los 28 tipos canonico de `SPEC_FB_EVENTING_AND_OUTBOX_v1.md` (subconjunto E1 en M15).
- **RLS:** `tenant_id` NOT NULL en toda tabla aislable; politicas `FORCE ROW LEVEL SECURITY`; tenant via context, nunca via header.
- **Audit:** campos D10 minimos en cada accion auditable (ver M12).

Si un modulo necesita un dato que otro modulo aun no produce, se usa un **stub contract** (fixture/mocks) con version explicita; la integracion real se firma en el punto de verificacion del track.

---

# ACTO ADMINISTRATIVO

**Este documento, al aprobarse, supersede el ORDEN DE BUILD de `PLAN_DESARROLLO_FABERLOOM_v5.md` para la etapa E0-E3.** No supersede los kill criteria de privacidad, el principio HITL absoluto, ni las decisiones CEO firmadas que no contradigan este plan.

**[PENDIENTE -- NO INVENTAR] Ratificacion escrita del CEO de que v6 es la fuente unica de orden de build E0-E3 y que los 14 modulos M07-M20 se construyen bajo el principio contract-first aqui definido.**

---

# 1. SPINE SERIAL — ORDEN MINIMO OBLIGATORIO

El SPINE son los modulos transversales que deben existir antes de forkear tracks paralelos. Se construyen en orden porque cada paso habilita el contrato del siguiente.

| Paso | Modulo | Rol / Especialista | Entregable de contrato | Gate de salida | Talla |
|---|---|---|---|---|---|
| S0 | **E0 — Decisiones CEO + dataset de verdad** | CEO + Module Partitioner | Lista cerrada de alcance E1; 30 casos reales (o scope reducido firmado); 10 holdout congelados; baseline Claude-crudo; dedicacion de Alejandro confirmada | CEO firma go/no-go; Alejandro >= [PENDIENTE] h/sem confirmado | S |
| S1 | **M16 Tenant Isolation** + **M08 Auth Session** (co-build) | Platform Architect + RLS/multi-tenant | RLS en PostgreSQL; Redis/Celery/MinIO/pgvector/LiteLLM/Letta scoped; sesion server-side con `tenant_id`; cookie httpOnly / particion Electron | 5 tests cross-tenant de M16 pasan; login basico funciona; query sin `tenant_id` devuelve cero filas | L |
| S2 | **M09 RBAC** | Platform Architect + RLS/multi-tenant | Matriz 5 roles x superficie; `membership` con roles; hat selector; resolucion server-side de permisos | 5 roles seedeados; invitacion/aceptacion/suspension funciona; permission denied auditado | M |
| S3 | **M15 Outbox Streams** + **M12 Audit Trail** (co-build) | Platform Architect + eventing/audit | Tabla `outbox` transaccional; relay a Redis Streams; WebSocket fanout por tenant; tabla audit append-only con SHA-chain | Evento de prueba via outbox llega a WS; insercion en audit no editable (UPDATE/DELETE bloqueados); job de validacion de cadena OK | L |
| S4 | **M11 D9 Policy Gate** | Platform Architect + compliance | Ceiling de data class por tenant/plan; DPA status registry; pre-skill + pre-egress scanner; respuesta `PlanUpgradeRequired` | Hard-block N3/N4 sin DPA; fail-closed cuando no puede evaluar; eventos `policy.gate.blocked/passed` emitidos | L |

**[SUPUESTO: M16 y M08 se co-construyen porque M08 provee el `tenant_id` que M16 usa, y M16 provee el aislamiento que protege las tablas de sesion. Se tratan como un solo paso S1 para el orden, aunque internamente se particionen subtareas.]**

---

# 2. TRACKS PARALELOS

Una vez cerrado el SPINE (S0-S4), los siguientes tracks pueden avanzar en paralelo. Cada track lista sus modulos, especialista, contrato, condicion de inicio, aceptacion, tests y talla.

## TRACK 1 — Bootstrap Wizard & Tenant Lifecycle (M07)

- **Especialista:** Platform Onboarding / RBAC.
- **Modulos:** M07 Bootstrap Wizard.
- **Contrato:**
  - **Inputs:** invitacion platform-side, datos de tenant, credenciales Owner, mailbox OAuth/IMAP, KB docs, Voice Profile, estado DPA (de M11).
  - **Outputs:** tenant `active`, filas `tenants`/`users`/`memberships`, mailbox conectado, documentos/chunks KB, agentes system en `shadow`, estado de sandbox.
  - **Eventos emitidos:** `tenant.created`, `user.invited`, `user.2fa_enabled`, `mailbox.connected`, `document.uploaded`, `tenant.activated`.
  - **Schemas:** `tenant.config` JSON; wizard step state; invitation token.
  - **RLS:** todas las filas creadas con `tenant_id`; platform admin no accede a datos de cliente sin audit.
  - **Audit D10:** `tenant.created`, `tenant.activated`, `mailbox.connected`, `document.uploaded`.
- **Can start when:** SPINE S4 cerrado (M08, M09, M11, M16 listos). Puede usar stub de DPA hasta que CEO decida firma.
- **Aceptacion:** Owner puede activar un tenant de cero a `active` en < 1 hora; sandbox test clasifica 1 RFQ de prueba y genera draft en Zona 3; DPA gate bloquea datos reales N3 hasta firma.
- **Tests:** E2E wizard completo; invitacion expirada; suspension de tenant; reconnect de mailbox.
- **Talla:** M.

## TRACK 2 — AI Router / L1 Classifier (M10)

- **Especialista:** ML Classifier / Action Engine.
- **Modulos:** M10 L1 Classifier.
- **Contrato:**
  - **Inputs:** `feed_item` (texto/adjuntos), resultado Tier 0 deterministico, work-type pack del tenant, KB seed.
  - **Outputs:** `ActionContext` JSON: `task_type`, `data_class` (N0-N4), `skill_id`/`agent_id`, `confidence`, `routing`/`zona`, `SLA`.
  - **Eventos emitidos:** `feed.item.dispatched`, `task.created`, `pattern.candidate.detected`.
  - **Schemas:** schema `ActionContext`; skill spec markdown versionado (prompt + schema + threshold).
  - **RLS:** `skill_executions`, `llm_calls`, skills tenant-scoped.
  - **Audit D10:** `feed.item.dispatched`, `task.created`, modelo/provider/confidence.
- **Can start when:** SPINE S4 cerrado (M11, M15, M16 listos). Puede usar work-type pack stub hasta que M07 entregue el seed real.
- **Aceptacion:** Tier 0 cubre >= 40% sin LLM; P95 latencia clasificacion < 1.5s; confidence >= 0.85 rutea automaticamente; < 0.85 va a `pending_human_review`; N3/N4 siempre pasa por M11.
- **Tests:** 10 RFQs golden; 8 exception codes; mock de M11 que fuerza bloqueo N3; correccion humana genera `pattern.candidate.detected`.
- **Talla:** L.

## TRACK 3 — HITL + Learning Loop (M13 + M14)

- **Especialista:** HITL/UX (+ Curator para M14).
- **Modulos:** M13 Draft HITL + M14 Outcome Ledger.
- **Contrato:**
  - **Inputs (M13):** task, output del agente, evidence bundle, Voice Profile, decision humana (aprobar/editar/rechazar).
  - **Outputs (M13):** draft con estados `pending/awaiting_approval/approved/edited/rejected/sent/expired`; mensaje enviado al canal; diff al M14.
  - **Eventos (M13):** `draft.generated`, `draft.approved`, `draft.edited`, `draft.rejected`, `draft.sent`, `draft.expired`.
  - **Inputs (M14):** decision HITL de M13, correcciones de clasificacion de M10.
  - **Outputs (M14):** entrada en Outcome Ledger; gold sample `CANDIDATE/ACTIVE/discarded/deprecated`; Learning Thermometer Cold/Warm/Hot.
  - **Eventos (M14):** `gold.candidate.created`, `gold.promoted`, `gold.deprecated`.
  - **Schemas:** draft + evidence bundle; ledger entry; gold sample.
  - **RLS:** drafts/ledger/gold samples tenant-scoped; visibilidad por rol (M09).
  - **Audit D10:** aprobacion/edicion/rechazo con `human_gate_required=true`, `human_approver_id`, diff_hash; promocion de gold con aprobadores.
- **Can start when:** M09, M10, M12, M15 cerrados. M13 y M14 se co-construyen (M14 solo existe como reaccion a M13).
- **Aceptacion:** flujo login -> draft aprobado < 2 min (desktop); 0 auto-send; edit_distance y tiempo de decision registrados; gold sample candidato generado tras aprobacion sin edicion + confidence HIGH; segundo aprobador N2+ funciona.
- **Tests:** 3 botones HITL; envio falla con reintentos; rechazo con razon obligatoria; Oscillation Counter; promocion de gold con segundo aprobador.
- **Talla:** L.

## TRACK 4 — Agent Memory Stack (M17)

- **Especialista:** Memory / Letta.
- **Modulos:** M17 Memory Letta.
- **Contrato:**
  - **Inputs:** contexto de ejecucion del agente, `task_id`, KB VIGENTE.
  - **Outputs:** episodic (append-only), working (TTL 24h), persistent (gate humano), `disputed` marks.
  - **Eventos:** `memory.persisted`, `memory.disputed`, `memory.deprecated`.
  - **Schemas:** memory item JSON; namespaces `mem:agent:{agent_id}:task:{task_id}:working`.
  - **RLS:** namespace estricto por tenant y por agente; cross-profile bloqueado.
  - **Audit D10:** `memory.persisted`, `memory.disputed`, `memory.deprecated`.
- **Can start when:** SPINE S4 cerrado (M16 listo). M15 recomendado para eventos pero no bloqueante.
- **Aceptacion:** agente lee working + episodic + KB sin contradecir KB; persistent solo con gate humano; MemoryConflictGuard marca disputed y no inyecta; no leak cross-profile.
- **Tests:** memoria working se limpia post-task; persistent requiere aprobacion; conflicto KB gana; intento cross-profile = P0.
- **Talla:** M.

## TRACK 5 — Electron Desktop Runtime (M18 + M19 + M20)

- **Especialista:** Electron / Desktop.
- **Modulos:** M18 Electron Auth, M19 Offline Sync, M20 Auto Update.
- **Contrato:**
  - **Inputs (M18):** flujo M08, tenant profile.
  - **Outputs (M18):** `session.fromPartition('persist:faberloom-{profile}')`, secretos en keychain, config no secreta en `electron-store`.
  - **Inputs (M19):** `last_event_id`, `last_sync_at`, WS events (M15), endpoint full state.
  - **Outputs (M19):** estado reconciliado, cursores actualizados, badge offline/syncing.
  - **Inputs (M20):** feed HTTPS firmado, `min_supported_client_version`.
  - **Outputs (M20):** artefacto descargado/verificado, instalacion al cierre/boton, bloqueo si version obsoleta.
  - **Eventos:** reusa M08; M19/M20 emiten telemetria de sync/update.
  - **Schemas:** particion, cursor JSON, feed JSON.
  - **RLS/seguridad:** particion por tenant; localStorage prohibido para tokens; `contextIsolation=true`, `nodeIntegration=false`; no aprobaciones offline en S1A.
  - **Audit:** reusa M08/M12; M20 telemetria sin PII.
- **Can start when:** SPINE S1 (M08) y S3 (M15) cerrados. M19 necesita M18; M20 necesita M18+M19.
- **Aceptacion:** login desktop persistente; logout limpia particion + keychain; reconexion con delta <= 24h; full refresh si gap > 24h; update firmado no disruptivo; min_supported bloquea versiones viejas.
- **Tests:** keychain no disponible = fail-closed; reconexion con last_event_id; gap > 24h = full refresh; firma invalida = rechazo; no auto-restart mid-task.
- **Talla:** L.

---

# 3. REGISTRO DE CONTRATOS MODULO → MODULO

| Modulo | Expone (outputs / eventos / schemas) | Consume (inputs / eventos de otros modulos) |
|---|---|---|
| **M16 Tenant Isolation** | RLS policies; key prefixes `tenant:{id}:`; Celery tenant wrapper; MinIO paths; pgvector partitions; Letta namespaces; `cross_tenant.access_attempted` | `tenant_id` de M08; queries/jobs/events de todos los modulos |
| **M08 Auth Session** | Sesion server-side Redis; cookie httpOnly / particion Electron; eventos `auth.*` | Credenciales/TOTP; revocaciones de M09; M18 para desktop |
| **M09 RBAC** | Matriz de permisos; resolucion allow/deny; eventos `user.*`, `permission.denied` | Sesion/rol de M08; M07 crea memberships; M13/M18 consultan permisos |
| **M15 Outbox Streams** | Tabla `outbox`; relay a Redis Streams; WebSocket fanout por tenant; entrega con `last_event_id` | Cambios de negocio de M07-M14; M12 usa outbox para audit durable |
| **M12 Audit Trail** | Tabla audit append-only + SHA-chain; validacion diaria; export | Acciones auditables de todos los modulos; outbox M15 para no perder escrituras |
| **M11 D9 Policy Gate** | `PlanUpgradeRequired` / `ClassificationMismatch`; eventos `policy.gate.*` | `data_class` de M10; DPA status de M07; chunks/output para pre-egress |
| **M07 Bootstrap Wizard** | Tenant `active`; mailbox conectado; KB seed; agentes shadow; eventos `tenant.*`, `mailbox.*`, `document.*` | M08/M09 para auth/roles; M11 para DPA status; M16 para aislamiento |
| **M10 L1 Classifier** | `ActionContext` JSON; eventos `feed.item.dispatched`, `task.created` | `feed_item`; Tier 0; work-type pack/KB de M07; M11 para gate |
| **M13 Draft HITL** | Drafts con estados; envio al canal; eventos `draft.*`; diff a M14 | Task/output de M10; evidence bundle; permisos de M09; eventos M15; M12 audit |
| **M14 Outcome Ledger** | Ledger entry; gold samples; Learning Thermometer; eventos `gold.*` | Decisiones de M13; correcciones de M10; M12 audit de promociones |
| **M17 Memory Letta** | working/episodic/persistent/disputed; eventos `memory.*` | Contexto de ejecucion; KB VIGENTE; M16 aislamiento |
| **M18 Electron Auth** | Particion segura por tenant; secretos en keychain | Flujo M08; M16 aislamiento cliente; M19/M20 coordinan |
| **M19 Offline Sync** | Estado reconciliado; cursores; badge syncing/offline | M15 eventos/WS; M18 sesion; endpoints full state |
| **M20 Auto Update** | Artefacto firmado; instalacion controlada; bloqueo version obsoleta | Feed HTTPS; `min_supported_client_version`; M18/M19 pre-checks |

---

# 4. DAG DE DEPENDENCIAS

```
                         +---------+
                         |   E0    | CEO decisions + dataset
                         +----+----+
                              |
         +--------------------+--------------------+
         |                    |                    |
         v                    v                    v
    +---------+          +---------+         +---------+
    |  M16    |<-------->|  M08    |         |  M09    |
    |Tenant   |  co-dep  |Auth     |-------->|RBAC     |
    |Isolation|          |Session  |         |         |
    +----+----+          +---------+         +----+----+
         |                    ^                    |
         |                    |                    |
         +--------------------+--------------------+
                              |
                              v
    +---------+         +---------+         +---------+
    |  M15    |<------->|  M12    |         |  M11    |
    |Outbox   |  co-dep  |Audit    |         |D9 Gate  |
    |Streams  |          |Trail    |         |         |
    +----+----+          +---------+         +----+----+
         |                                       |
         |                                       v
         |                                  +---------+
         |                                  |  M10    | AI Router
         |                                  |L1 Class |
         |                                  +----+----+
         |                                       |
         |                                       v
         |                                  +---------+
         |                                  | M13+M14 | HITL + Learning
         |                                  |Draft +  |
         |                                  |Outcome  |
         |                                  +---------+
         |
         +----------------+----------------+----------------+
         |                |                |                |
         v                v                v                v
    +---------+      +---------+      +---------+      +---------+
    |  M07    |      |  M17    |      |  M18    |      |  M19    |
    |Bootstrap|      |Memory   |      |Electron |----->|Offline  |
    |Wizard   |      |Letta    |      |Auth     |      |Sync     |
    +---------+      +---------+      +---------+      +----|----+
                                                             |
                                                             v
                                                        +---------+
                                                        |  M20    |
                                                        |Auto Updt|
                                                        +---------+
```

**Notas de paralelismo:**
- M16/M08 y M09 pueden co-construirse dentro del SPINE.
- M15/M12 se co-construyen; M11 se construye sobre M15/M12.
- Track 2 (M10) y Track 1 (M07) pueden correr en paralelo usando stubs de work-type pack/DPA.
- Track 3 (M13+M14) **requiere** M09, M10, M12, M15.
- Track 4 (M17) solo requiere M16 (y M15 para eventos, no bloqueante).
- Track 5 (M18→M19→M20) requiere M08 y M15; M19/M20 son serial dentro del track.

---

# 5. INTEGRATION POINTS + CONTRACT TESTS

## 5.1 Tests cross-tenant de M16 (obligatorios antes de abrir cualquier track)

Antes de forkear tracks, los 5 tests deben ejecutarse en CI. **Un test que deberia fallar (sin aislamiento) y pasa con aislamiento = OK; si pasa sin aislamiento = leak.**

| # | Capa | Setup | Accion / Request | Assertion |
|---|---|---|---|---|
| CT-1 | **PostgreSQL RLS** | Tenant A tiene 5 `tasks`; Tenant B tiene 0. Sesion de B setea `app.tenant_id = B`. | `SELECT * FROM tasks` como B. | Devuelve 0 filas. Si devuelve > 0 = leak P0. |
| CT-2 | **Redis Streams fanout** | Tenant A recibe un `draft.generated`; Tenant B con WS abierto. | WS de B escucha `events:B`. | B no recibe el evento de A. |
| CT-3 | **Celery tenant context** | Job encolado con `tenant_id=A`; worker reutiliza conexion sin `DISCARD ALL`; siguiente job sin tenant seteado. | Ejecutar job que lee `current_setting('app.tenant_id')`. | Falla o devuelve NULL; nunca devuelve A. |
| CT-4 | **MinIO path scoping** | Tenant A sube archivo a `/tenants/A/doc.pdf`; request de B intenta `GET /tenants/A/doc.pdf`. | Validacion anti path-traversal + tenant scoping. | 403 / not found; B no lee archivo de A. |
| CT-5 | **Letta profile isolation** | Agente `agent-A` del tenant A escribe memoria working; agente de tenant B intenta leer namespace `mem:agent:agent-A:...`. | Read cross-profile. | Bloqueado; evento `cross_tenant.access_attempted`; P0. |

**[PENDIENTE -- NO INVENTAR] Confirmar los 5 escenarios exactos del CI con el CEO; estos son los propuestos por el rol Security Auditor a partir de las 7 capas de M16.**

## 5.2 Tests de contrato entre modulos

| Integration | Test | Setup | Assert |
|---|---|---|---|
| M08 → M16 | `tenant_id` fluye de sesion a RLS | Login de tenant A; request autenticado a tabla tenant-scoped | Query filtra por A sin que el cliente envie `tenant_id` en header |
| M09 → M13 | RBAC bloquea aprobacion | Operator intenta aprobar draft de otro Operador sin permiso | 403 + `permission.denied` + audit |
| M10 → M11 | Data class dispara gate | L1 clasifica item como N3 sin DPA firmado | M11 devuelve `PlanUpgradeRequired`; no se invoca skill |
| M11 → M13 | Solo `passed` genera draft | Gate bloquea item | No se crea draft; card de bloqueo en WorkLoom |
| M15 → M12 | Outbox no pierde audit | Transaccion crea draft + inserta outbox; simular crash del relay antes del publish | Al reiniciar relay, evento se publica y audit row existe |
| M13 → M14 | Decision genera senal | Operator aprueba draft sin edicion + confidence HIGH | Outcome Ledger crea entrada; gold candidate generado |
| M15 → M19 | Reconexion con cursor | Desktop pierde WS; backend emite 3 eventos; desktop reconecta con `last_event_id` | Recibe los 3 eventos en orden; UI actualizada |
| M18 → M19 | Sesion preservada en sync | Login en Electron; cerrar app; reabrir offline breve; reconectar | Reanuda sesion de la particion; no pide login |
| M07 → M11 | DPA status cambia ceiling | Owner firma DPA via wizard | M11 deja pasar items N3 para ese tenant; audit de firma |
| M07 → M10 | Work-type pack seed disponible | Wizard carga pack `safety_footwear` | Classifier puede listar tipos de tarea del pack |
| M20 → M18/M19 | Update no rompe sesion/cursores | Publicar update; instalar al cerrar | Sesion (M18) y cursores (M19) se preservan; app arranca y sincroniza |

---

# 6. RIESGOS P0/P1 + KILL CRITERIA

## 6.1 Riesgos P0 (bloquean o matan)

| Riesgo | Modulo afectado | Mitigacion | Umbral de kill |
|---|---|---|---|
| RLS incomplete o cross-tenant leak | M16 | 5 tests CI + `FORCE RLS` + `DISCARD ALL` + wrappers Celery | >=1 incidente privacy = kill |
| D9 Policy Gate fail-open | M11 | Hard-block N3/N4; fail-closed; sin override CEO; audit | Cualquier dato N3/N4 sale sin DPA = kill |
| Auto-send sin HITL | M13 | Estado machine; server-side enforcement; 0 boton de envio automatico | Envio cliente-facing sin aprobacion humana = kill |
| Token/session exposure en desktop | M18/M19 | keychain/safeStorage; localStorage prohibido; contextIsolation | XSS roba sesion = kill / replan mayor |
| Evento de negocio perdido (sin outbox) | M15 | Outbox transaccional; relay idempotente; DLQ | Perdida de evento que cause accion incorrecta = P0/kill |
| Stack/framework no resuelto | SPINE | CEO ratifica stack en E0; no mezclar FastAPI/Django/Celery/RabbitMQ | Kickoff sin stack unico = no iniciar S1 |

## 6.2 Riesgos P1 (importantes)

| Riesgo | Modulo afectado | Mitigacion |
|---|---|---|
| M07 DPA e-sign vs offline no resuelto | M07/M11 | Usar stub hasta decision; gate fail-closed |
| M10 threshold 0.85 vs routing presets 3 capas | M10/M11 | Definir interseccion ECU/preset/curva antes de S1B |
| M12 campos audit 12 vs 18 no canonizados | M12 | Elegir superset de 18; migrar sin tocar entradas pasadas |
| M17 MemoryConflictGuard con falsos positivos | M17 | KB VIGENTE gana; memoria disputed no se inyecta |
| M19 aprobaciones offline en modo lectura | M19 | Bloquear acciones sensibles hasta reconciliacion en S1A |
| M20 feed HTTPS / code signing sin infra | M20 | Plan B manual download mientras se habilita feed |
| Roles 5 vs 2 en E1 generan UI inconsistente | M09/M07 | UI muestra solo Owner/Operator en E1; Admin/Supervisor/Viewer deshabilitados |

## 6.3 Kill criteria

1. **>=1 incidente privacy o fuga cross-tenant** → kill inmediato E1.
2. **>=1 envio cliente-facing sin aprobacion HITL** → kill inmediato E1.
3. **M16 cross-tenant tests no pasan antes de forkear tracks** → no iniciar tracks paralelos.
4. **M11 falla-closed no funciona** → no procesar datos reales.
5. **Edit rate >= 60% en 30 drafts** (M13/M14) → replan/congelar.
6. **Stack/framework no ratificado en E0** → no iniciar SPINE.
7. **M15 pierde eventos en test de crash** → no abrir WorkLoom.
8. **M20 artefacto sin firma valida** → no distribuir.

---

# 7. PENDIENTES CEO QUE BLOQUEAN CADA TRACK

## SPINE

1. **[PENDIENTE -- M16]** Confirmar los 5 tests cross-tenant exactos del CI y el umbral N2+ para pgvector por particion.
2. **[PENDIENTE -- M08]** TTL de sesion server-side; politica "recordar dispositivo"; algoritmo hash (argon2id recomendado); cooldown lockout 2FA.
3. **[PENDIENTE -- M09]** E1 expone solo Owner/Operator en UI de invitacion o muestra 5 roles deshabilitados; si Admin ve audit completo o scope.
4. **[PENDIENTE -- M12]** Set canonico final de campos D10: 12 de `SCH_FB_FUNCTIONAL_SPEC_v1` vs 18 de `SPEC_FB_FUNC_M12_AUDIT_TRAIL_v1`; formato de export para auditores.
5. **[PENDIENTE -- M11]** Mapeo exacto N0-N4 -> ceiling por plan; provider de deletion-on-request; pre-egress scanner (heuristica vs modelo).
6. **[PENDIENTE -- gobernanza]** Ratificar que v6 es fuente unica de orden de build E0-E3 y resolver contradicciones de stack (ver seccion 8).

## TRACK 1 — Bootstrap (M07)

1. **[PENDIENTE -- M07]** WhatsApp BSP: paso visible-diferido u oculto en E1-E2 (enmienda E-5 PLB).
2. **[PENDIENTE -- M07/M11]** DPA: firma e-sign in-wizard u offline antes de S10.
3. **[PENDIENTE -- M07]** Email provider para invitaciones (SendGrid/SES).
4. **[PENDIENTE -- M07]** Contenido exacto del seed work-type pack `safety_footwear`.
5. **[PENDIENTE -- M07]** Rutinas base: seedear en bootstrap o despues en S5/S6.

## TRACK 2 — AI Router (M10)

1. **[PENDIENTE -- M10]** Pesos/normalizacion de los 13 features FG-03.
2. **[PENDIENTE -- M10]** Interaccion del threshold 0.85 con las 3 capas de routing (ECU/preset/curva) de `SPEC_FB_ROUTING_PRESETS_v1`.
3. **[PENDIENTE -- M10]** Versionado del modelo si deja de ser prompt-based.
4. **[PENDIENTE -- M10]** Skill system `classify_rfq` seed: modelo default Haiku vs Sonnet.

## TRACK 3 — HITL + Learning (M13 + M14)

1. **[PENDIENTE -- M13]** Valor N del Oscillation Counter.
2. **[PENDIENTE -- M13]** Timeout/vida del draft antes de `expired`.
3. **[PENDIENTE -- M13/M14]** Schema de evidence bundle para drafts no-cotizacion (follow-up, consulta) vs `SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1`.
4. **[PENDIENTE -- M14]** Umbrales exactos del Learning Thermometer (Cold/Warm/Hot) y segundo aprobador N2+.
5. **[PENDIENTE -- M14]** Criterio automatico para deprecar un gold sample malo.

## TRACK 4 — Memory (M17)

1. **[PENDIENTE -- M17]** MemoryConflictGuard: match exacto vs semantico para detectar conflicto con KB VIGENTE.
2. **[PENDIENTE -- M17]** TTL/criterio exacto del sweeper de working stale.
3. **[PENDIENTE -- M17]** Gate de persistent: Owner, Curator o ambos; segundo aprobador N2+ como en M14.

## TRACK 5 — Desktop Runtime (M18 + M19 + M20)

1. **[PENDIENTE -- M18]** TTL local de reanudacion de sesion desktop.
2. **[PENDIENTE -- M18]** Convencion exacta de naming del profile en la particion (`tenant_slug` vs `user+tenant`).
3. **[PENDIENTE -- M18]** Comportamiento si keychain del SO no esta disponible.
4. **[PENDIENTE -- M19]** Acciones permitidas en modo lectura offline.
5. **[PENDIENTE -- M19]** Numero de reintentos/backoff de reconexion.
6. **[PENDIENTE -- M20]** Host/infra del feed HTTPS propio por plataforma/canal.
7. **[PENDIENTE -- M20]** 5 tenants del canal beta y criterio de promocion beta -> stable.
8. **[PENDIENTE -- M20]** Cadencia de chequeo del feed y politica de gracia ante `min_supported`.

---

# 8. CONTRADICCIONES KB (id + version, NO RESUELTAS)

| # | Codigo | Documentos en conflicto (id + version) | Descripcion | Bloquea a |
|---|---|---|---|---|
| C1 | **STACK-01** | `PLB_FB_FOUNDATION_BETA_v1` (v1.3.2-ENMENDADO) vs `PLAN_DESARROLLO_FABERLOOM_v5.md` (v5.0) vs `ENT_PLAT_INFRA` (VIGENTE, citado en a9) | Foundation Beta asume FastAPI + Next.js + Postgres + Redis + Celery + LiteLLM Proxy + 12 contenedores; v5 asume FastAPI + LiteLLM lib + desktop/web dual + SQLite/Postgres; ENT_PLAT_INFRA asume Django + Celery + Redis. El prompt de este plan fija stack Django+Celery+PostgreSQL/RLS+Redis Streams+pgvector+MinIO+LiteLLM+Letta+Next.js+Electron. | SPINE S0: decision CEO/CTO obligatoria antes de S1A |
| C2 | **ROLES-01** | `SCH_FB_FUNCTIONAL_SPEC_v1` (v1.0) vs `PLB_FB_FOUNDATION_BETA_v1` enmienda E-4 | SCH define 5 roles canonicos activos; enmienda E-4 reduce E1 a Owner/Operator y difiere Admin/Supervisor/Viewer a E3+. | M07, M08, M09, M13 UI |
| C3 | **WHATSAPP-01** | `SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1` (v1.0) paso 4 vs `PLB_FB_FOUNDATION_BETA_v1` enmienda E-5 | M07 lista conexion de canales WhatsApp BSP en wizard; enmienda E-5 difiere WhatsApp Business a E3 (email-only E1-E2). | M07 paso 4 |
| C4 | **AUDIT-01** | `SCH_FB_FUNCTIONAL_SPEC_v1` (v1.0) D12.2 vs `SPEC_FB_FUNC_M12_AUDIT_TRAIL_v1` (v1.0) D12.2 | SCH lista 12 campos D10; M12 define 18 campos canonicos (superset). | M12 schema |
| C5 | **EVIDENCE-01** | `SPEC_FB_FUNC_M13_DRAFT_HITL_v1` (v1.0) vs `SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1` (v1.0) | M13 asume evidence bundle para todo draft; SCH_FB_QUOTE_EVIDENCE_BUNDLE esta disenado para cotizacion; no hay schema definido para drafts no-cotizacion. | M13 schema de bundle |
| C6 | **ROUTING-01** | `SPEC_FB_FUNC_M10_L1_CLASSIFIER_v1` (v1.0) vs `SPEC_FB_ROUTING_PRESETS_v1` (v1.0) | M10 usa threshold fijo 0.85 y 13 features FG-03; ROUTING_PRESETS define 3 capas (ECU/preset/curva) y fabrica niveles 0-4. | M10 integracion con presets |
| C7 | **DESKTOP-01** | `SPEC_FB_FUNC_M08_AUTH_SESSION_v1` (v1.0) vs `SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1` (v1.0) | M08 cubre auth web+Electron general; M18 profundiza Electron. Solapamiento que puede divergir en futuras ediciones si no se mantiene sincronizado. | M18/M08 mantenimiento |
| C8 | **BETA-01** | `SPEC_FB_FUNC_M20_AUTO_UPDATE_v1` (v1.0) vs `PLB_FB_FOUNDATION_BETA_v1` enmienda E-4 / `SPEC_FB_BUILD_SEQUENCE_v3` (v3.0) | M20 asume canal beta para 5 tenants; enmienda E-4 y BUILD_SEQUENCE v3 plantean E1 single-tenant interno / 2 roles, con multi-tenant externo condicional a E2.5/E4b. | M20 alcance de canal beta en E1 |
| C9 | **EVENTS-01** | `SPEC_FB_EVENTING_AND_OUTBOX_v1` (v1.0) vs `SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1` (v1.0) | EVENTING define 28 eventos canonicos; M15 implementa subconjunto E1 de 6 eventos. | M15 set E1 |

**[PENDIENTE -- NO INVENTAR] El CEO debe resolver C1-C9 o aceptarlas como supuestos documentados antes de iniciar cada track afectado. Este plan NO las resuelve.**

---

# 9. SINTESIS CRUZADA

## 9.1 SPINE en una linea

**E0 ratifica stack/scope → S1 construye M16+M08 (aislamiento + sesion con tenant_id) → S2 agrega M09 (RBAC) → S3 construye M15+M12 (eventos confiables + audit inmutable) → S4 cierra M11 (D9 fail-closed). Sin esto no hay tracks paralelos.**

## 9.2 Tracks paralelos posibles tras SPINE

- **Track 1 Bootstrap (M07):** paralelo, pero integra DPA de M11 al final.
- **Track 2 AI Router (M10):** paralelo, usa stub de work-type pack; necesita M11 para gate.
- **Track 3 HITL + Learning (M13+M14):** depende de M09+M10+M12+M15; no puede arrancar antes de que Track 2 y SPINE terminen.
- **Track 4 Memory (M17):** paralelo al SPINE desde S4, solo requiere M16.
- **Track 5 Desktop Runtime (M18→M19→M20):** paralelo, depende de M08 y M15; internamente serial.

## 9.3 Top 5 integration risks

| # | Riesgo | Track afectado | Mitigacion clave |
|---|---|---|---|
| 1 | **M16 RLS leak** | Todos | 5 tests CI; `FORCE RLS`; `DISCARD ALL`; wrappers Celery |
| 2 | **M11 fail-open** | Track 2, 3 | Hard-block N3/N4; sin override; audit |
| 3 | **M15 pierde eventos** | Track 3, 5 | Outbox transaccional; relay idempotente; DLQ |
| 4 | **M13 auto-send** | Track 3 | State machine server-side; HITL absoluto |
| 5 | **M18/M19 exposicion de tokens** | Track 5 | keychain; no localStorage; contextIsolation; particion por tenant |

## 9.4 Confianza por track (ALTA / MEDIA / BAJA)

| Track | Confianza | Razon |
|---|---|---|
| SPINE | **MEDIA** | El stack (C1) y los roles (C2) estan sin resolver; una vez resueltos, M16/M08/M15/M12 son tecnicamente estandar. |
| Track 1 Bootstrap | **MEDIA** | Depende de DPA y WhatsApp (C3, C5); el flujo wizard es predecible si se fijan esos dos pendientes. |
| Track 2 AI Router | **MEDIA** | Necesita decision de threshold vs presets (C6) y pesos de 13 features; tecnicamente viable con stubs. |
| Track 3 HITL + Learning | **ALTA** | Es el corazon del producto, bien especificado en M13/M14; el riesgo principal es no respetar HITL absoluto. |
| Track 4 Memory | **MEDIA** | Letta introduce complejidad; el MemoryConflictGuard y el aislamiento de namespace son los puntos de atencion. |
| Track 5 Desktop Runtime | **MEDIA** | Electron seguro es conocido; la incertidumbre esta en keychain cross-plataforma y feed de updates. |

---

# 10. CHECKLIST GO/NO-GO ANTES DE FORKEAR TRACKS

- [ ] E0 cerrado: stack ratificado, 30 casos (o scope reducido), holdout, baseline, dedicacion Alejandro.
- [ ] 5 tests cross-tenant de M16 pasan en CI.
- [ ] M08 sesion server-side funciona; M09 RBAC resuelve permisos.
- [ ] M15 outbox + M12 audit funcionan; evento de prueba llega a WS.
- [ ] M11 hard-block N3/N4 sin DPA demostrado.
- [ ] CEO resolvio o acepto documentar C1-C9 que bloquean el track a iniciar.
- [ ] Kill criteria comunicados al equipo.

---

Changelog:
- v1.0 (2026-06-25): Creacion. Plan de desarrollo modular distribuido E0-E3 contract-first; SPINE S0-S4; 5 tracks paralelos (M07, M10, M13+M14, M17, M18+M19+M20); registro de contratos modulo->modulo; DAG; 5 tests cross-tenant de M16; riesgos P0/P1 + kill criteria; pendientes CEO por track; 9 contradicciones KB sin resolver; sintesis cruzada. RUN_ID: PLAN-MOD-2026-06-24.
