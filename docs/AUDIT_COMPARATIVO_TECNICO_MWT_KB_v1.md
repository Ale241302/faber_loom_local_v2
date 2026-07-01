---
id: AUDIT_COMPARATIVO_TECNICO_MWT_KB
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma / FaberLoom
stamp: DRAFT -- 2026-06-24 -- comparativa de especificaciones vs. estado real de la KB
agente: Kimi Code CLI (auditor técnico)
---

# AUDIT COMPARATIVO TÉCNICO — KB MWT / FaberLoom

## 1. Resumen ejecutivo

Se compararon 7 bloques técnicos críticos contra los documentos canónicos de la KB. Solo **2 de 7** están cubiertos de forma sólida (RLS+pgvector y, con matices, el aislamiento multi-tenant). Los demás presentan duplicidad, vacíos o especificaciones contradictorias que bloquearían la implementación del Sprint 1 si no se cierran antes.

| Componente | Alineación | Riesgo |
|---|---|---|
| 1. User / Admin / Knowledge Flow | **Parcial** | Medio-Alto |
| 2. Schema Knowledge Base (entidades base) | **Parcial** | Medio |
| 3. Multi-tenant isolation | **Parcial** | Medio-Alto |
| 4. Automations + automation_runs | **No** | Alto |
| 5. Integración Letta self-hosted | **No** | Medio-Alto |
| 6. RLS + pgvector | **Sí / Parcial** | Medio |
| 7. Matriz RBAC | **Parcial** | Medio-Alto |

**Top 3 prioridades:**
1. Unificar modelo de identidad, membresía y RBAC (componentes 1 y 7) — hay dos vocabularios y dos esquemas en paralelo.
2. Especificar el componente de automaciones (`automations` + `automation_runs`) — hoy solo existen piezas aisladas (`scheduled_jobs`, `job_execution`, `workflow_runs`).
3. Resolver el estado de Letta self-hosted (CEO-34 vence 2026-06-30): adoptar con spec propia o descartar formalmente.

---

## 2. Alcance y metodología

### Documentos inspeccionados

| Documento | Rol en esta auditoría |
|---|---|
| `docs/SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` v1.0 DRAFT | Especificación de identidad, directory sync, flujo de conocimiento, leakage tests |
| `docs/SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` v1.0 DRAFT | Blueprint técnico: 20 tablas FROZEN, RLS, pgvector, migraciones, dev/staging |
| `docs/faberloom/SCH_FB_CORE_TABLES_v1.md` v1.0 VIGENTE | DDL de 7 tablas core del Sprint 1 |
| `docs/ENT_PLAT_MULTITENANT.md` v1.0 VIGENTE | Invariantes de aislamiento multi-tenant |
| `docs/SPEC_TENANT_CONTAMINATION_TESTS_v1.md` v1.0 DRAFT | Suite anti-cross-tenant |
| `docs/faberloom/SPEC_FB_AUTH_TENANT_RBAC_v1.md` v1.0 VIGENTE | Auth, subdomain routing, RBAC ejecutable |
| `docs/SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` v1.0 DRAFT | Motor de workflows (pg-boss / Inngest) |
| `docs/ARCH_AGENT_PRINCIPLES.md` v1.0 VIGENTE | Principios y 3 objetos base: AgentSpec, AgentRuntime, AgentMemory |
| `docs/ENT_GOB_PENDIENTES.md` v16.0 VIGENTE | Pendientes CEO, incluye CEO-34 Letta |
| `docs/ENT_PLAT_MEMORY_STACK.md` (referenciado) | Decisión de memoria / pgvector / Letta v1.5 |

### Reglas aplicadas

- R1: no inventar datos que no estén en la KB.
- R2: no tocar documentos FROZEN; si hay conflicto, reportar gap.
- R5: toda discrepancia se cita con fuente y ubicación aproximada.

---

## 3. Matriz comparativa detallada

| Componente | Especificaciones que lo cubren | Estado actual en KB | ¿Alineado? | Gaps encontrados | Riesgo de no cerrar el gap | Recomendación inmediata |
|---|---|---|---|---|---|---|
| **1. User / Admin / Knowledge Flow** | `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` (v1.0 DRAFT) | Modelo identity descrito; ERD mínimo; state machine; leakage tests definidos; directory sync v1.5. | **Parcial** | a) ERD de este doc (`org_id`, `membership`, `role_in_faberloom`) no coincide con el blueprint (`tenant_id`, `department`, `user_department`, `role` ∈ {owner,admin,operator}). b) Roles difieren de los 4 roles canónicos de `SPEC_FB_AUTH_TENANT_RBAC_v1.md`. c) Directory sync es read-only en v1 pero no hay cron ni schema de sincronización concreto. | Medio-Alto | Crear un **SPEC_FB_IDENTITY_UNIFIED_v1.md** que integre `user_account`, `department`, `user_department`, `membership`/`workspace_members` y alinee roles con RBAC. |
| **2. Schema Knowledge Base (entidades base)** | `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §4 + §2; `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §2.4 | Blueprint define `memory_source`, `memory_chunk`, `memory_chunk_vector`, `overlay_policy`, `agent_spec`, `agent_binding`, `agent_run`. `SPEC_USER_ADMIN_KNOWLEDGE_FLOW` lista `agent_spec_base`, `agent_spec_overlay_manual/learned`, `memory_document`, `memory_example`, `user_control_profile`. `SCH_FB_CORE_TABLES` define `gold_samples`, `conversations`, `conversation_messages`. | **Parcial** | Duplicidad semántica: `agent_spec` vs `agent_spec_base`; `memory_source` vs `memory_document`; `memory_example`/`gold_samples`; `overlay_policy` vs `agent_spec_overlay_*`. No hay un mapa de equivalencia. | Medio | Publicar un **mapping table** que relacione las entidades de los 3 specs y decida nombres canónicos; actualizar `SPEC_USER_ADMIN_KNOWLEDGE_FLOW` o marcarlo SUPERSEDED por el blueprint. |
| **3. Multi-tenant isolation** | `ENT_PLAT_MULTITENANT.md` v1.0 VIGENTE; `SPEC_TENANT_CONTAMINATION_TESTS_v1.md` v1.0 DRAFT | Invariantes consolidados (5 reglas + workspace lens). RLS pattern genérico. Tests definen 7 superficies y estructura YAML. | **Parcial** | a) `SPEC_TENANT_CONTAMINATION_TESTS` sigue llamando a `ENT_PLAT_MULTITENANT` “STUB” (desactualizado). b) No hay seed de 2 tenants ni casos YAML concretos. c) RLS detallada solo existe para `memory_chunk`; el resto de tablas solo tienen policy genérica. | Medio-Alto | Actualizar `SPEC_TENANT_CONTAMINATION_TESTS` a VIGENTE, poblar ENT_PLAT_MULTITENANT como fuente bajo prueba y añadir políticas RLS por tabla en el blueprint. |
| **4. Automations + automation_runs** | No se encontró spec dedicado. | Existen `scheduled_jobs` (`SCH_FB_CORE_TABLES`), `job_execution` (blueprint §11) y `workflow_runs`/`workflow_step_runs` (`SPEC_FABERLOOM_WORKFLOW_ENGINE`). Ninguno cubre el concepto genérico de `automations` + `automation_runs` con FK, RLS e idempotencia. | **No** | No existe tabla `automations` ni `automation_runs`. No hay un modelo unificado de triggers (cron, evento, webhook) ni de histórico/reattempt. | Alto | Crear `SPEC_FB_AUTOMATIONS_v1.md` con DDL de `automations` + `automation_runs`, FK a `scheduled_jobs`/`workflow_runs`, RLS, retry policy e idempotencia; o renombrar/integrar `scheduled_jobs` como implementación. |
| **5. Integración Letta self-hosted** | Referencias en `ENT_GOB_PENDIENTES.md` CEO-34, anexos de research, `SPEC_FABERLOOM_WORKFLOW_ENGINE.md` §2. | No hay spec canónico de integración Letta en docs principales. Memory stack canónica es pgvector (`ENT_PLAT_MEMORY_STACK`, blueprint §16). Letta queda como “v1.5 opcional” o piloto pendiente de decisión. | **No** | Sin schema de memoria Letta, sin endpoints, sin mapeo a `agent_run`/`memory_chunk`, sin decisión de Go/No-Go formal. | Medio-Alto | Resolver CEO-34 antes del 2026-06-30: si se adopta, crear `SPEC_FB_LETTA_INTEGRATION_v1.md`; si no, actualizar `ENT_GOB_DECISIONES.md` y `ENT_PLAT_MEMORY_STACK` declarando descarte formal. |
| **6. RLS + pgvector** | `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §1-§4, §6, §7; `SCH_FB_CORE_TABLES_v1.md`; `SPEC_FB_RAG_SECURITY_FIREWALL_v1.md` | RLS settings unificados (`app.tenant_id`, `app.user_id`, `app.role`, `app.dept_ids`, `app.break_glass`). DDL completo de `memory_chunk` con 4 policies. `CREATE EXTENSION vector` en init. Retrieval query canónica. | **Sí / Parcial** | a) No se muestra DDL de `memory_chunk_vector` ni índice HNSW. b) RLS detallada solo para `memory_chunk`; otras tablas usan policy genérica. c) `FORCE ROW LEVEL SECURITY` no se menciona para tablas que no sean `memory_chunk`. | Medio | Completar DDL de `memory_chunk_vector` con índice HNSW (`vector_cosine_ops`); extender policies RLS a las 20 tablas FROZEN en el blueprint. |
| **7. Matriz RBAC** | `SPEC_FB_AUTH_TENANT_RBAC_v1.md` v1.0 VIGENTE; `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §6 | Dos matrices en paralelo: 4 roles AM/CURATOR/AUDITOR/CEO con 25+ recursos en el primer doc; 3 roles Tenant Owner/Admin/Operator en el segundo. | **Parcial** | No hay mapping entre los dos modelos de roles. El blueprint usa roles {owner,admin,operator} que no se alinean ni con AM/CURATOR/AUDITOR/CEO ni con Tenant Owner/Admin/Operator/Auditor. | Medio-Alto | Definir vocabulario único de roles y unificar matrices; publicar `rbac_matrix_v1.yaml` referenciado en `SPEC_FB_AUTH_TENANT_RBAC_v1.md` §5.2. |

---

## 4. Evidencia por componente

### 4.1 User / Admin / Knowledge Flow

- `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §1.8 propone tablas:
  ```text
  user_account (id PK, org_id, email, status, created_at)
  membership (id PK, user_id FK, org_id, team_key, role_in_faberloom)
  ```
  El blueprint (`SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §3) usa:
  ```text
  user_account (id PK, tenant_id uuid, email, role ∈ {owner,admin,operator})
  department (id PK, tenant_id, name, slug)
  user_department (user_id, department_id, tenant_id, role_in_dept)
  ```
  La duplicidad `org_id` vs `tenant_id` y `membership` vs `user_department` + `workspace_members` (`SCH_FB_CORE_TABLES`) generará migraciones incompatibles si ambos specs se usan como fuente.

- `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §6 define roles **Tenant Owner / Admin / Operator**; `SPEC_FB_AUTH_TENANT_RBAC_v1.md` §2.2 define **AM / CURATOR / AUDITOR / CEO**. No se encontró mapa entre ambos.

### 4.2 Schema Knowledge Base

- Blueprint §2 lista 20 tablas FROZEN: `memory_source`, `memory_chunk`, `memory_chunk_vector`, `overlay_policy`, `agent_spec`, `agent_binding`, `agent_run`.
- `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §2.4 lista: `agent_spec_base`, `agent_spec_overlay_manual`, `agent_spec_overlay_learned`, `memory_document`, `memory_chunk`, `memory_example`, `user_control_profile`.
- `SCH_FB_CORE_TABLES_v1.md` añade `gold_samples`, `conversations`, `conversation_messages`.
- `ARCH_AGENT_PRINCIPLES.md` define los 3 objetos base: `AgentSpec`, `AgentRuntime`, `AgentMemory`. El blueprint los materializa en `agent_spec`, `agent_binding`+`agent_run`, `memory_chunk`. El spec de knowledge flow no se ha actualizado para reflejar esa materialización.

### 4.3 Multi-tenant isolation

- `ENT_PLAT_MULTITENANT.md` v1.0 (2026-06-12) dejó de ser STUB y consolidó 5 invariantes, el workspace lens y punteros canónicos.
- `SPEC_TENANT_CONTAMINATION_TESTS_v1.md` §G aún dice: “Extiende el modelo multi-tenant declarado en CLAUDE.md (3 reglas) y `ENT_PLAT_MULTITENANT` (STUB)”. Esto ya no es cierto.
- §H de `SPEC_TENANT_CONTAMINATION_TESTS` marca como pendientes:
  - L1: poblar `ENT_PLAT_MULTITENANT` (resuelto).
  - L2: definir seed mínimo de 2 tenants sintéticos para CI (aún pendiente).
  - L3: cobertura S5 según prompt cache (aún pendiente).

### 4.4 Automations + automation_runs

- No se encontró ningún documento cuyo título o ID sea `SPEC_FB_AUTOMATIONS*`, ni tablas `automations` / `automation_runs` en DDL.
- `SCH_FB_CORE_TABLES_v1.md` define `scheduled_jobs`:
  ```sql
  CREATE TABLE scheduled_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    job_type text NOT NULL,            -- digest | validity_check | promotion_batch
    cron_expr text NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}',
    enabled boolean NOT NULL DEFAULT true,
    last_run_at timestamptz,
    last_status text,
    created_at timestamptz NOT NULL DEFAULT now()
  );
  ```
  Esta tabla no tiene FK a histórico de ejecuciones; el histórico vive en `job_execution` del blueprint, que a su vez **no tiene `tenant_id`**.
- `SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` §4.1 define `workflow_runs`, `workflow_step_runs`, `workflow_approvals` y `workflow_templates`. Es un motor de workflows, no un sistema genérico de automations.
- Resultado: falta el componente unificado que relacione automations → runs → jobs/workflow_runs.

### 4.5 Integración Letta self-hosted

- `ENT_GOB_PENDIENTES.md` CEO-34: “**VENCE 2026-06-30** Decidir piloto Letta self-hosted en profile `mwt-sprint-active` (4 semanas, esfuerzo 4-6h Ale). Stack memoria operativa agentes.”
- `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §16: “`ENT_PLAT_MEMORY_STACK.md` — pgvector queda como KB canónica; Letta **[v1.5]** como capa memoria operativa opcional.”
- `SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` §2 lista “Agent framework: Letta (memoria) + LangGraph (checkpointing) + Claude Agent SDK”, pero no hay DDL, endpoints ni protocolo de integración.
- No se encontró `SPEC_FB_LETTA_INTEGRATION*`, ni schema de memoria Letta, ni mapeo a tablas FaberLoom.

### 4.6 RLS + pgvector

- Blueprint §4.1-4.3 define `memory_chunk` con:
  - 4 scopes (`global`, `org`, `dept`, `user`).
  - CHECK de consistencia scope↔owner.
  - 7 índices.
  - 4 policies RLS (read, insert, update, delete).
  - Retrieval query canónica que hace JOIN con `memory_chunk_vector`.
- Blueprint §6 init: `CREATE EXTENSION vector; CREATE EXTENSION pgcrypto; CREATE EXTENSION btree_gin;`.
- Falta:
  - DDL de `memory_chunk_vector` (columnas, FK, índice HNSW).
  - Políticas RLS detalladas para las otras 19 tablas.
  - Mención explícita de `FORCE ROW LEVEL SECURITY` más allá de `memory_chunk`.

### 4.7 Matriz RBAC

- `SPEC_FB_AUTH_TENANT_RBAC_v1.md` §5.2 presenta matriz de 25+ recursos × acciones para roles AM/CURATOR/AUDITOR/CEO. Dice: “(Matriz completa en YAML reference · `docs/anexos/rbac_matrix_v1.yaml` cuando se implemente.)”.
- `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` §6 presenta matriz para Tenant Owner/Admin/Operator.
- El blueprint (`SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` §3) usa `role ∈ {owner,admin,operator}` en `user_account`.
- No se encontró `docs/anexos/rbac_matrix_v1.yaml` ni documento de mapping de roles.

---

## 5. Top 3 prioridades

### P1 — Unificar identidad, membresía y RBAC (componentes 1 y 7)
**Por qué primero:** los developers del Sprint 1 necesitan un único schema de usuarios y un único vocabulario de roles. Hoy hay tres vocabularios en tres documentos.
**Criterio de cierre:** un solo SPEC vigente con DDL unificado, matriz RBAC ejecutable en YAML y mapa de roles aceptado por CEO.

### P2 — Especificar Automations (`automations` + `automation_runs`)
**Por qué segundo:** M1 (digest), M4 (vigencias) y M8 (batch promoción) asumen un scheduler, pero no existe un modelo común. Sin esto cada módulo improvisará su propio cron.
**Criterio de cierre:** SPEC con DDL, RLS, FK a `scheduled_jobs`/`workflow_runs`/`job_execution`, retry policy e idempotencia.

### P3 — Decidir Letta self-hosted
**Por qué tercero:** CEO-34 vence el 2026-06-30. Si se adopta, bloquea la arquitectura de memoria operativa; si no, hay que eliminar ambigüedad de varios specs que mencionan Letta como opcional.
**Criterio de cierre:** decisión formal en `ENT_GOB_DECISIONES.md` + spec de integración o nota de descarte en `ENT_PLAT_MEMORY_STACK.md` y `SPEC_FABERLOOM_WORKFLOW_ENGINE.md`.

---

## 6. Próximos pasos concretos

| # | Acción | Owner sugerido | Entregable | Deadline sugerido |
|---|---|---|---|---|
| 1 | Crear `SPEC_FB_IDENTITY_UNIFIED_v1.md` que integre `user_account`, `department`, `user_department`, `workspace_members`, directory sync y roles. | Arquitecto + CEO | SPEC VIGENTE | 2026-06-28 |
| 2 | Actualizar `SPEC_TENANT_CONTAMINATION_TESTS_v1.md`: corregir referencia a ENT_PLAT_MULTITENANT (ya no es STUB), añadir seed de 2 tenants y casos YAML concretos. | Backend lead | SPEC VIGENTE + tests pytest | 2026-07-03 |
| 3 | Extender RLS en blueprint: DDL de `memory_chunk_vector` con HNSW y policies RLS para las 20 tablas FROZEN. | Backend lead | PR contra blueprint | 2026-07-03 |
| 4 | Crear `SPEC_FB_AUTOMATIONS_v1.md` con `automations` + `automation_runs`; decidir relación con `scheduled_jobs`, `job_execution` y `workflow_runs`. | Arquitecto | SPEC DRAFT → VIGENTE | 2026-07-05 |
| 5 | Resolver CEO-34: decisión Letta Go/No-Go. Si Go, crear `SPEC_FB_LETTA_INTEGRATION_v1.md`. | CEO + Arquitecto | Decisión en `ENT_GOB_DECISIONES.md` | 2026-06-30 |
| 6 | Publicar `docs/anexos/rbac_matrix_v1.yaml` y unificar vocabulario de roles (AM/CURATOR/AUDITOR/CEO vs Owner/Admin/Operator). | Product + Arquitecto | YAML + nota de alineación | 2026-07-01 |
| 7 | Actualizar `SPEC_USER_ADMIN_KNOWLEDGE_FLOW.md` o marcarlo SUPERSEDED por el SPEC unificado de identidad + blueprint. | Arquitecto | Nota en header + changelog | 2026-06-29 |

---

## 7. Notas finales

- Esta auditoría **no evalúa calidad de código**; solo compara especificaciones contra el estado documentado de la KB.
- Los documentos `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` y `SCH_FB_CORE_TABLES_v1.md` son los más cercanos a una fuente de verdad técnica, pero aún tienen vacíos en RLS generalizada y en el componente de automaciones.
- La duplicidad de vocabularios (tenant/org, AM/operator, owner/CEO) es el riesgo más costoso de corregir en implementación; debería resolverse antes de escribir la primera migración del Sprint 1.

---

Changelog:
- v1.0 (2026-06-24): Creación. Comparativa de 7 componentes técnicos con evidencia citada, top 3 prioridades y próximos pasos.
