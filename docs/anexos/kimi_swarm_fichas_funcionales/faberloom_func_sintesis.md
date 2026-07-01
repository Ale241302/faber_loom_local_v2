# Síntesis Funcional — FaberLoom Foundation Beta E1

> Generado por AGENTE_SINTETIZADOR a partir de las 6 fichas funcionales del swarm.
> Fecha de síntesis: 2026-06-24.

---

## 1. Resumen ejecutivo

Se especificaron 6 módulos transversales de FaberLoom Foundation Beta E1: inbound (Gmail/WhatsApp) + clasificación L1, task + draft HITL, Mesa de Control WorkLoom + card, skill + agente, rutinas + workspace, y tenant bootstrap + aislamiento multi-tenant.

El sistema modela un flujo RFQ B2B: un mensaje entra por un canal conectado, se normaliza en `feed_item`, pasa por reglas Tier 0 y un clasificador L1, genera una `task`, un agente ejecuta una cadena lineal de skills, y si el output es cliente-facing aparece en Zona 2 de WorkLoom para aprobación humana antes de envío. Paralelamente existen rutinas (agentes de Proceso) y un Workspace conversacional de 3 modos para trabajo exploratorio y creación de objetos en SANDBOX.

Estado general: las fichas cubren las 13 dimensiones canónicas y documentan flujos, estados, permisos, errores y aprendizaje. Sin embargo, **múltiples decisiones de diseño siguen pendientes** y hay **contradicciones entre documentos base** que bloquean o complican la implementación. Los documentos `ENT_FB_INBOUND_TAXONOMY_v1`, `ENT_FB_WORK_TYPE_PACK_v1`, `SPEC_FB_ROUTINES_v1` y `SPEC_FB_WORKSPACE_v1` están en STUB, por lo que varios detalles de clasificación, catálogo, rutinas y workspace no pueden cerrarse sin input del CEO o arquitecto. La enmienda E-5 del PLB (email-only en E1-E2, WhatsApp a E3) y la enmienda E-4 (2 roles en E1) generan fricción con los prompts y con `SCH_FB_FUNCTIONAL_SPEC_v1`, que asumen 5 roles y multi-canal.

---

## 2. PENDIENTEs cross-módulo que bloquean implementación

Items `[PENDIENTE]` que aparecen en **más de una ficha** y son críticos para continuar:

| # | Pendiente | Módulos afectados | Por qué es crítico |
|---|---|---|---|
| 1 | **`ENT_FB_INBOUND_TAXONOMY_v1` en STUB** — tipos 1-2 (Gmail/WhatsApp) y los 13 tipos de inbound no están definidos. | 01, 03, 05, 06 | Sin la taxonomía no se puede implementar el clasificador L1, los filtros de Zona 4, la lógica de rutinas por tipo de inbound ni el paso 8 del bootstrap. |
| 2 | **`ENT_FB_WORK_TYPE_PACK_v1` en STUB** — seed del work-type pack "safety footwear" para E1 no definido. | 01, 03, 05, 06 | Alimenta las labels de clasificación L1, la visualización de cards, las rutinas base y el paso 5 del bootstrap. Sin él el cotizador no tiene catálogo. |
| 3 | **`SPEC_FB_ROUTINES_v1` en STUB** — wizard, triggers, campos obligatorios, UI de Zona 5, cantidad mínima de runs sandbox, fórmula signal-to-noise. | 03, 04, 05, 06 | Bloquea Zona 5, la creación de agentes de Proceso, la decisión de si las rutinas base se seedean en bootstrap y los thresholds de autonomía. |
| 4 | **`SPEC_FB_WORKSPACE_v1` en STUB** — layout 3 columnas, 3 modos exactos, tipos/tamaño de archivo, contexto activo, SpaceLoom, persistencia de working memory. | 04, 05 | Bloquea el modo Construcción/Automatización, la creación conversacional de agentes/skills/rutinas y el panel derecho de Workspace. |
| 5 | **Canales en E1: ¿email-only o incluir WhatsApp/Telegram?** La enmienda E-5 del PLB dice email-only E1-E2; los prompts de agentes asumen WhatsApp BSP/Telegram. | 01, 02, 03, 04, 05, 06 | Afecta canales de inbound/outbound, UI de cards y filtros, wizard de bootstrap paso 4, canal binding de agentes y política de envío post-HITL. |
| 6 | **Roles en E1: ¿2 roles (Owner/Operator) o 5 roles canónicos?** Enmienda E-4 reduce a 2; `SCH_FB_FUNCTIONAL_SPEC_v1` y `SPEC_FB_AUTH_TENANT_RBAC` usan 5. | 01, 02, 03, 04, 05, 06 | Define quién puede crear/promover skills y agentes, quién ve qué zonas, quién aprueba HITL y quién invita usuarios en bootstrap. |
| 7 | **Ubicación de toggles on/off de agentes y panel de aprendizaje en curso** — ¿panel lateral de WorkLoom, hero de Workspace o panel derecho de Workspace? | 03, 04, 05 | Decide el layout principal del desktop y dónde vive la gobernanza operativa en E1. |
| 8 | **Estados de skill/schema** — `SHADOW / ACTIVE / PAUSED / DEPRECATED` vs `draft / active / deprecated`; ¿se permite `paused`? | 02 (contradicción), 04 (pendiente CEO) | Impacta directamente el schema de la tabla `skills`, el wizard de Skill Factory y las transiciones de Zona 3. |
| 9 | **¿Operator puede pausar/reactivar rutinas desde Zona 5?** | 03, 05 | Define permisos de escritura en WorkLoom y la matriz de control de automatizaciones. |
| 10 | **Curator / Learning thermometer / thresholds de promoción de autonomía** | 04, 05 | Afecta cuándo un skill/rutina/agente puede subir de autonomía y quién lo aprueba en E1. |

Otros `[PENDIENTE]` importantes pero **no cross-módulo** (aparecen en una sola ficha o no bloquean la base): threshold de margen y campos bloqueados en edición de draft (02), campos exactos del evidence bundle (02), definición de Quick pass / Batch / Oscillation Counter (02), evento canónico para expiración de draft (02), `ActionContext` exacto/schema mínimo (01), "13 features del classifier" (01), n8n obligatorio u opcional (01), estados técnicos de task `created` vs `queued` / `timeout` (02), criterio exacto de Zona 1 (03), deep link de WorkLoom (03), política de reconexión offline (03), DPA firma electrónica (06), email provider de invitaciones (06), `SPEC_FB_BUILD_SEQUENCE` (06).

---

## 3. Contradicciones detectadas entre módulos

Se listan discrepancias que aparecen en más de una ficha y requieren resolución antes de codificar.

### 3.1 Canales en E1: WhatsApp vs email-only
- **Versión A (multi-canal):** Módulo 01 describe inbound Gmail/WhatsApp/Telegram; Módulo 03 incluye filtros por WhatsApp; Módulo 04 permite canal binding WhatsApp; Módulo 06 incluye paso 4 "Conectar WhatsApp" en bootstrap. Fuente: prompts de agentes y contexto general.
- **Versión B (email-only E1-E2):** Módulo 01 §8.1 y Módulo 02 §7.3 aclaran que en E1-E2 el envío es email-only y WhatsApp va a E3; Módulo 06 marca el paso 4 como pendiente por enmienda E-5. Fuente: `PLB_FB_FOUNDATION_BETA_v1.md` enmienda E-5.
- **Impacto:** decide si S1A/S5 implementan solo Gmail/IMAP o también WhatsApp BSP/Telegram.

### 3.2 Roles en E1: 2 vs 5
- **Versión A (5 roles):** Módulo 03 lista Operator/Supervisor/Admin/Owner/Viewer; Módulo 04 y 05 mantienen Admin/Supervisor/Viewer en descripciones; Módulo 06 menciona Admin (E3+). Fuente: `SCH_FB_FUNCTIONAL_SPEC_v1`, `SPEC_FB_AUTH_TENANT_RBAC_v1`.
- **Versión B (2 roles):** Módulos 01 y 02 aplican enmienda E-4: solo Owner/Operator en E1; Admin/Supervisor/Viewer son E3+. Fuente: `PLB_FB_FOUNDATION_BETA_v1.md` enmienda E-4.
- **Impacto:** permisos de Skill/Agent Factory, quién promueve desde Zona 3, quién invita en bootstrap.

### 3.3 Ubicación de toggles de agentes y panel de aprendizaje
- **Versión A:** Panel lateral izquierdo de WorkLoom (Módulo 03 prompt original; Módulo 04 menciona panel lateral de Mesa). Fuente: `SCH_FB_FUNCTIONAL_SPEC_v1` §8.2, TIER1 CONSTRAINTS v1.1.
- **Versión B:** Hero de Workspace (Módulo 03 nota spec puente). Fuente: `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` §8.2 v1.1.
- **Versión C:** Panel derecho de Workspace con tabs Agentes/Skills/Aprendizaje (Módulo 05). Fuente: `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` v1.8-v1.9.
- **Impacto:** layout del desktop y separación Mesa/Workspace.

### 3.4 Estados de skill
- **Versión A:** `SHADOW / ACTIVE / PAUSED / DEPRECATED` con state machine completa (Módulo 04). Fuente: `SCH_FB_FUNCTIONAL_SPEC_v1` §Referencias canónicas.
- **Versión B:** Schema `skills.status` admite solo `('draft','active','deprecated')` sin `paused` ni `shadow` (Módulo 02 y 04). Fuente: `PLB_FB_FOUNDATION_BETA_v1.md` §2.3.
- **Impacto:** schema de DB y wizard de Skill Factory.

### 3.5 Estados de agente
- **Versión A:** `shadow / running / paused / error` (Módulo 04). Fuente: `SCH_FB_FUNCTIONAL_SPEC_v1`.
- **Versión B:** incluye `archived` (Módulo 04). Fuente: `SPEC_FABERLOOM_AGENT_COMPOSITION_v1`.
- **Impacto:** enum `agent_status` y flujo de deprecación.

### 3.6 Sprint del módulo Draft/HITL
- **Versión A:** S3 — "Aprobación de draft por output" (Módulo 02, fuente: ejemplo de ficha en `SCH_FB_FUNCTIONAL_SPEC_v1`).
- **Versión B:** S5 — Mesa de Control + HITL + canales (Módulo 02, 03; fuente: `PLB_FB_FOUNDATION_BETA_v1` §Plan por sprint).
- **Impacto:** scheduling de S1B/S5.

### 3.7 Modelo de persistencia del engine de skills
- **Versión A:** Engine ejecutor genérico lee `SkillSpec` de DB con Pydantic dinámico (Módulo 01, 02, 04). Fuente: `PLB_FB_FOUNDATION_BETA_v1.md` §2.2/§S3 plan original.
- **Versión B:** Skill = markdown versionado + tools allowlist + schema de salida, capa fina sobre SDK estándar (Módulo 01, 02, 04). Fuente: `PLB_FB_FOUNDATION_BETA_v1.md` enmienda E-3.
- **Impacto:** arquitectura de Skill Factory y executor.

### 3.8 Sub-agentes / multi-agente
- **Versión A:** "NO sub-agentes" en E1 (Módulo 01, 04, 05). Fuente: `PLB_FB_FOUNDATION_BETA_v1.md` TIER 1 #15.
- **Versión B:** Sub-agentes como agentes standalone permitidos E1; composición jerárquica bloqueada E1 (Módulo 01, 04, 05). Fuente: `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` §3.1.
- **Versión C:** Nivel 2 de composición multi-agente habilitado bajo condiciones (Módulo 04). Fuente: `ARCH_AGENT_PRINCIPLES` P17.
- **Impacto:** diseño de agentes Proceso y rutinas.

### 3.9 Autonomy ceiling vs ladder
- **Versión A:** `autonomy ceiling` 4 niveles: PROPONE / EJECUTA_INTERNO / AUTO_NOTIFICA / AUTO_EXCEPCIONES (Módulo 04, 05). Fuente: `SCH_FB_FUNCTIONAL_SPEC_v1`.
- **Versión B:** `autonomy ladder` L0-L4 (5 niveles): Shadow / Propone / Ejecuta interno / Auto + notif / Auto + excepciones (Módulo 04). Fuente: `ARCH_AGENT_PRINCIPLES` P4/P13.
- **Impacto:** modelo de autonomía y thresholds de promoción.

### 3.10 Estados técnicos de task
- **Versión A:** `created / running / awaiting_approval / completed / failed / cancelled` (Módulo 02). Fuente: `SCH_FB_FUNCTIONAL_SPEC_v1` §Referencias canónicas.
- **Versión B:** `queued / running / awaiting_approval / completed / failed / cancelled / timeout` (Módulo 02). Fuente: `SCH_FB_TASK_ENTITY.md`.
- **Impacto:** nomenclatura UI/DB y si `timeout` es estado separado o subclass de `failed`.

### 3.11 Mesa: 5 zonas plegables vs Kanban 4 columnas
- **Versión A:** 5 zonas plegables (Z1-Z5) (Módulo 03). Fuente: `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` §8.1.
- **Versión B:** Mesa Kanban con 4 columnas: Crítico · Listo para revisar · Delegado · Error accionable (Módulo 03). Fuente: `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` §8.4 v1.7.
- **Impacto:** diseño de UI de WorkLoom.

### 3.12 Workspace lateral panel: hero vs panel derecho
- **Versión A:** Hero de Workspace para toggles y aprendizaje (Módulo 03/05). Fuente: TIER1 CONSTRAINTS v1.1/v1.2.
- **Versión B:** Panel derecho con tabs Agentes/Skills/Aprendizaje + Contexto activo (Módulo 05). Fuente: TIER1 CONSTRAINTS v1.8-v1.9.
- **Impacto:** layout de Workspace.

### 3.13 Estados de rutina
- **Versión A:** `sandbox / active / paused / failed / deprecated` (Módulo 05). Fuente: `SCH_FB_FUNCTIONAL_SPEC_v1`.
- **Versión B:** El prompt del AGENTE_5 agrega `running` como estado posible de rutina (Módulo 05). La ficha resuelve que `running` es `automation_run.status`, no estado de rutina.
- **Impacto:** state machine de `automations`.

### 3.14 Skill Factory / tools externas
- **Versión A:** Prohibidas tools externas y HTTP calls en E1 (Módulo 04, 05). Fuente: `PLB_FB_FOUNDATION_BETA_v1.md` TIER 1 #16.
- **Versión B:** `SPEC_ACTION_ENGINE.md` describe bypass mode y `ActionRegistry` que podrían incluir tools (Módulo 04, 05). Fuente: `SPEC_ACTION_ENGINE.md`.
- **Versión C:** Wrappers existen pero bloqueados en runtime de skill E1 (Módulo 05). Fuente: `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1`.
- **Impacto:** capacidad de los skills en E1.

### 3.15 Orden de sprints
- **Versión A:** 13 sprints en orden original del PLB (implícito en asignaciones de módulos). Fuente: `PLB_FB_FOUNDATION_BETA_v1.md` plan original.
- **Versión B:** Enmienda E-1 supersedes por `SPEC_FB_BUILD_SEQUENCE v2.1` (Módulo 06). Fuente: `PLB_FB_FOUNDATION_BETA_v1.md` enmienda E-1.
- **Impacto:** planificación de S1A/S1B y dependencias.

---

## 4. Dependencias entre módulos y orden de implementación

### 4.1 Grafo de dependencias (texto)

```
M06 Tenant Bootstrap + Isolation
    │
    ├──► M01 Inbound + Clasificación L1
    │       │
    │       ├──► M02 Task + Draft HITL
    │       │       │
    │       │       ├──► M03 WorkLoom / Card
    │       │       │
    │       └──► M04 Skill + Agente
    │               │
    │               ├──► M02 Task + Draft HITL (los skills/agentes generan tareas y drafts)
    │               │
    │               ├──► M03 WorkLoom / Card (visualización de resultados)
    │               │
    │               └──► M05 Rutinas + Workspace
    │                       │
    │                       └──► M03 WorkLoom / Card (alertas, Zona 3, Zona 5)
    │
    └──► M04 Skill + Agente (seed system en bootstrap)
```

**Notas del grafo:**
- `M06` es base de todo (RLS, tenant, auth, canales, KB seed, Voice Profile).
- `M01` depende de `M06` para canales conectados y RLS; produce `feed_item` y `ActionContext`.
- `M02` depende de `M01` (inbound clasificado) y de `M04` (skills/agentes que ejecutan); es la unidad atómica de trabajo y HITL.
- `M03` depende de `M02` (tasks/drafts), `M04` (agentes en Zona 3/5) y `M05` (rutinas en Zona 5); es pura superficie desktop.
- `M04` depende de `M06` (tenant, KB, canales, positions) y alimenta a `M02`, `M03`, `M05`.
- `M05` depende de `M04` (agentes de Proceso, skills) y `M03` (visualización); el Workspace depende de agentes/skills/rutinas.

### 4.2 Orden sugerido de build para Sprint 1A / 1B

#### Sprint 1A — Fundamentos y recepción
Objetivo: tener un tenant activo que pueda recibir y persistir un email.

1. **M06 Tenant Bootstrap (mínimo viable)**
   - Schema `tenants` + `users` + `membership` + RLS policies.
   - Subdomain → `tenant_id` middleware.
   - Auth + 2FA obligatorio para Owner.
   - Wizard pasos 1-3 (datos tenant, Owner, mailbox Gmail OAuth/IMAP).
   - Seed mínimo de agentes system (`@router`, `@cotizador`) en SHADOW/draft.
   - 5 tests cross-tenant en CI.

2. **M01 Inbound — Recepción y normalización (sin L1 completo)**
   - Gmail OAuth watch / IMAP poll.
   - Normalización a `feed_item`.
   - Tier 0 determinístico básico (spam/logística).
   - Creación de `task` en modo `webhook`/`created`.

3. **M02 Task — Entity y state machine mínima**
   - Tabla `tasks` con `queued`/`running`/`awaiting_approval`/`completed`/`failed`/`cancelled`.
   - Worker Celery con `tenant_id` en headers/payload.
   - DLQ y retry básico.

#### Sprint 1B — Clasificación, draft y WorkLoom
Objetivo: que un RFQ se clasifique, genere draft y aparezca en WorkLoom para HITL.

1. **M01 L1 classifier**
   - Skill system `classify_rfq` seed.
   - `ActionContext` con `task_type`, `data_class`, `skill_id`, `agent_id`, `confidence`, `routing`, `SLA`.
   - Threshold default 0.85; `pending_human_review` si confidence bajo.

2. **M04 Skill + Agente (seed system mínimo)**
   - `@cotizador` system con skill de cotización/cálculo de precio básico.
   - No requiere Skill/Agent Factory custom en S1B; solo seed y ejecución.

3. **M02 Draft + HITL**
   - Tabla `drafts` / `draft_decisions`.
   - Estados `pending → awaiting_approval → approved/edited/rejected/sent`.
   - Envío por email post-aprobación (E1-E2).
   - Audit D10 con `human_approver_id` obligatorio.

4. **M03 WorkLoom / Card (mínimo viable)**
   - Desktop Electron con Zona 1, Zona 2, Zona 4.
   - WebSocket fanout tenant-scoped.
   - Card compacta con cliente, tipo, canal, confidence, SLA, acción primaria.
   - Aprobación/rechazo inline en Zona 2.

**Post-S1B (no en S1A/1B pero dependiente):**
- M04 Skill Factory + Agent Factory (S6).
- M05 Rutinas + Workspace (S5/S6/S7).
- M06 wizard completo con DPA, KB upload, Voice Profile, sandbox test (S10).

---

## 5. Lo que Fugu Ultra debe validar (módulos de runtime crítico)

Lista de validaciones técnicas críticas para runtime, RLS, HITL, eventing e isolation. Si alguna falla, E1 no puede salir.

### 5.1 Aislamiento multi-tenant (M06)
- [ ] RLS habilitado `FORCE ROW LEVEL SECURITY` en **todas** las tablas con `tenant_id`.
- [ ] Middleware extrae `tenant_slug` del subdominio y setea `SET app.tenant_id = '<uuid>'` en cada conexión DB.
- [ ] 5 tests cross-tenant en CI que intenten leer/escribir datos de otro tenant y fallen.
- [ ] Redis keys con prefix obligatorio `tenant:{tenant_id}:...`; auditoría de keys sin prefix.
- [ ] Celery jobs usan wrapper `with_tenant_session` + `DISCARD ALL` al inicio/fin para evitar `tenant_id` stale.
- [ ] MinIO paths estrictamente scoped `/tenants/{tenant_id}/...` con validación de path en cada request.
- [ ] pgvector retrieval con pre-filter `tenant_id` obligatorio.
- [ ] LiteLLM calls taggeadas con `tenant_id`; logs filtrados por tenant.
- [ ] Letta namespaces estrictos `mem:agent:{agent_id}:*` y validación de pertenencia al tenant.
- [ ] WebSocket/SSE fanout filtra por `tenant_id`; un usuario de tenant A no recibe eventos de tenant B.

### 5.2 HITL y envío externo (M02)
- [ ] Cualquier output cliente-facing requiere `requires_human_approval=true` y no se envía sin `human_approver_id`.
- [ ] Envío post-aprobación usa únicamente el canal configurado del tenant (email en E1-E2 si aplica enmienda E-5).
- [ ] Intento de bypass HITL dispara alerta P0 y audit inmutable.
- [ ] Draft editado preserva original; diff va a Outcome Ledger.

### 5.3 Data classification (M01/M02/M04/M06)
- [ ] N3/N4 hard-block en upload y en clasificación; Action Engine D9 retorna `PlanUpgradeRequired` si `data_class > tenant_plan_ceiling`.
- [ ] Data class heredada del inbound se propaga a task, draft y audit D10.
- [ ] Tokens OAuth cifrados en reposo.

### 5.4 Eventing / Outbox (M01/M02/M03)
- [ ] Eventos canónicos publicados en outbox transaccional (`feed.item.received`, `feed.item.dispatched`, `task.created`, `draft.generated`, `draft.approved`, `draft.sent`, etc.).
- [ ] Redis Streams retiene eventos ≤24h; reconexión con `last_event_id`; re-fetch full si gap >24h.
- [ ] Acciones offline de WorkLoom se encolan localmente y sincronizan con manejo de conflictos.

### 5.5 Skills / Agentes (M04)
- [ ] Sandbox obligatorio antes de promote (`skills.last_sandbox_test_at` no nulo).
- [ ] Límites duros TIER 1 #16 enforceados: tipo `classifier/generator/formatter`, sin tools externas, sin HTTP, timeout ≤60s, cost cap ≤USD 2.00.
- [ ] Skill falla aislada: `task.status=skill_failed`, agente NO se cae (TIER 1 #16.14).
- [ ] Circuit breaker: 3 fallos consecutivos abren circuito y usan fallback o pausan agente/rutina.

### 5.6 Resiliencia y observabilidad (M01/M02/M05/M06)
- [ ] Retry exponencial 3× con backoff 1s/5s/25s para fallos transitorios.
- [ ] DLQ para jobs/eventos fallidos; panel admin para reintentar.
- [ ] Toda acción sensible logueada en audit D10 con `sha_chain_prev`/`sha_chain_curr`.
- [ ] Alertas P0/P1/P2 a Owner/platform admin según tabla de severidad.

### 5.7 Auth y permisos (M06)
- [ ] 2FA obligatorio para Owner.
- [ ] Invitaciones en E1 solo por platform admin (no self-service signup).
- [ ] DPA firmado antes de procesar datos reales (S10).

---

## 6. Recomendaciones para CEO / Alejandro

Decisiones urgentes a tomar antes de continuar con implementación:

1. **Definir scope de canales en E1.** ¿Email-only (Gmail OAuth + IMAP) como dice enmienda E-5, o se incluye WhatsApp BSP/Telegram? Afecta S1A, bootstrap, UI y política de envío.
2. **Definir roles activos en E1.** ¿2 roles (Owner/Operator) o 5 (Owner/Admin/Operator/Supervisor/Viewer)? Si se mantienen 2, ¿quién asume las funciones de Admin en Skill/Agent Factory?
3. **Resolver ubicación de toggles de agentes y panel de aprendizaje.** ¿WorkLoom panel lateral, Workspace hero o Workspace panel derecho? Esto desbloquea el layout del desktop.
4. **Alinear estados canónicos de skill y agente con el schema de DB.** Decidir si se usa `SHADOW/ACTIVE/PAUSED/DEPRECATED` y si `paused`/`shadow` se agregan al schema PLB; y si `archived` existe para agentes.
5. **Confirmar work-type pack safety footwear y taxonomía inbound.** Sin `ENT_FB_WORK_TYPE_PACK_v1` y `ENT_FB_INBOUND_TAXONOMY_v1` no se puede entrenar/clasificar RFQs.
6. **Definir si n8n es obligatorio u opcional en E1.** Si es obligatorio, se necesita infraestructura extra; si es opcional, confirmar fallback exacto.
7. **Decidir modelo de engine de skills.** ¿`SkillSpec` en DB con Pydantic dinámico (PLB original) o markdown versionado + SDK estándar (enmienda E-3)?
8. **Definir autonomía para E1.** ¿Usar 4 niveles de ceiling o 5 niveles L0-L4? ¿Qué thresholds de approval rate/edit rate/rejection rate habilitan promoción?
9. **Definir política de HITL y pricing.** Threshold de margen, campos de pricing bloqueados en edición de draft, y campos exactos del evidence bundle.
10. **Decidir DPA y onboarding.** ¿DPA se firma electrónicamente dentro del wizard o fuera de línea antes de S10? ¿Self-service signup o invitación manual permanece en E1?
11. **Revisar orden de sprints.** Confirmar si se aplica `SPEC_FB_BUILD_SEQUENCE v2.1` (enmienda E-1) o el orden original de 13 sprints del PLB.
12. **Definir sub-agentes/multi-agente en E1.** ¿Prohibidos tajantemente, standalone permitidos, o composición jerárquica bajo condiciones? Impacta diseño de rutinas y agentes Proceso.

---

*Fin de la síntesis funcional.*
