# MANIFIESTO_APPEND_20260429b_FLOWS_TASKS_TEMPLATES
id: MANIFIESTO_APPEND_20260429b_FLOWS_TASKS_TEMPLATES
type: TRANSITORIO
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE — 2026-04-29
expires: post-consolidación en MANIFIESTO_CAMBIOS_v2.md (próxima sesión de mantenimiento)
aplica_a: [MWT]

---

## Contexto

Segunda indexa del día 2026-04-29 (la primera fue MANIFIESTO_APPEND_20260429_AGENT_BUILDER_MWT_V1, con plan de implementación + manifest schema v2 + regla P15 + research consolidado).

Esta segunda indexa fue derivada de:

1. Observación CEO del lanzamiento OpenAI Workspace Agents (22 abril 2026) — análisis comparativo con plan MWT
2. Identificación de gaps en plan v1.0:
   - "Crear flujos o tareas" como primitiva no formalizada
   - "Biblioteca de plantillas" mencionada pero sin catálogo
   - "Golden sample como norte" presente solo en SKILL_PROFORMA_BUILDER, no estándar
   - Output schema singular en SCH v1.0 vs realidad de múltiples outputs por agente
3. Decisión CEO de mantener foco MWT-only y no dejar que Workspace Agents desvíe el plan

`indexa, creo que no cambia mucho lo que hemos planeado, me hace sentir muy bien pq estamos con un buen norte` autoriza la materialización en KB.

## Cambios ejecutados

### 1. SCH_SKILL_MANIFEST_V2.md UPDATE v1.0 → v1.1

`docs/SCH_SKILL_MANIFEST_V2.md` — extensiones del schema canónico:

- `contract.outputs[]` plural reemplaza `contract.output_schema` singular. Cada output con id + schema + kind (asset/decision/learning/side_effect) + destination + required + condition opcional + requires_human_approval explícito por output (P3 granular).
- Nueva sección `metadata.mwt.golden_samples` con id, path, validates_outputs, evaluation_use, added_by, added_at, notes. Norte de calidad declarativo + few-shot + regression eval.
- Nueva sección `metadata.mwt.is_template + template_metadata + placeholders` para Template Library (mismo módulo en MWT v1, separable en FaberLoom).
- 8 validaciones build-time nuevas (13-20): outputs vacío, output kind válido, IDs únicos, approval externa, golden sample requerido por output:asset en archetype workflow/autonomous/routine, golden válido (path existe), template placeholders, flow DAG válido.
- Deliverable type ahora `computed_from_outputs: true` (calcula del kind de outputs, no se declara manual).

### 2. SCH_FLOW_DAG.md (NUEVO v1.0)

`docs/SCH_FLOW_DAG.md` — schema declarativo de plan ejecutable.

Cubre:
- DAG con 6 tipos de nodo: skill_call, branch, parallel, terminal, notify, human_gate
- Política global: max_depth, timeout_total, on_timeout, fail_policy
- Estructura nodos: id, kind, depends_on, conditions, goto, input_map, emits, on_failure, retries
- Entry point + output_emission_map
- 12 validaciones build-time (acíclico, entry válido, edges válidos, branch con default exhaustivo, terminal alcanzable, outputs declarados, profundidad respetada, sub-skills existen, input map completo, human gate con timeout, IDs únicos, parallel sin races)
- Compatibilidad con state_machine (P7) — flow complementa, no reemplaza
- Limitaciones v1: no loops nativos, no nested flows, no Jinja2 completo, paralelismo ≤4 ramas

### 3. SCH_TASK_ENTITY.md (NUEVO v1.0)

`docs/SCH_TASK_ENTITY.md` — tareas como entidad de primera clase.

Cubre:
- Schema tabla `tasks` Postgres con state machine 8 estados (queued, running, awaiting_approval, completed, failed, cancelled, timeout) + transiciones válidas
- 6 endpoints Django: POST tasks, GET queue, GET id, POST approve, POST reject, POST cancel + GET stats
- Dashboard CEO en portal.mwt.one/agents/tasks (cola, pendientes review, histórico, flow viewer, stats)
- Worker Celery `execute_agent_task` que invoca skill_executor o flow_executor según archetype
- Vinculación con flow: cada flow_node skill_call genera sub-task con parent_task_id
- HITL granular por output (no por task entera) — review por output_id individual
- Compatibilidad con todos los archetypes (skill, workflow, routine, autonomous, supervisor)
- Limitaciones v1: no retry inteligente, no prioridad dinámica, no quotas por tenant

### 4. ENT_TEMPLATE_LIBRARY_V1.md (NUEVO v1.0)

`docs/ENT_TEMPLATE_LIBRARY_V1.md` — catálogo de 5 templates iniciales:

- TPL_REVIEW_TRIAGE (routine + workflow, Amazon FBA reviews)
- TPL_LISTING_OPTIMIZER (skill, copy ASIN)
- TPL_LEAD_QUALIFIER_B2B (routine + workflow, Gmail webhook leads B2B)
- TPL_QUOTE_GENERATOR_B2B (skill, proforma Marluvas/Tecmater)
- TPL_KB_AUDITOR (routine, audit diaria KB)

Cada template documentado con: caso de uso, outputs declarados, placeholders al instanciar, golden samples requeridos, budget default. Lifecycle del template (draft → approved → deprecated → archived). Política de governance (CEO-only mantenimiento). Roadmap templates v2+. Manifests YAML reales pendientes para Fase 1 SPEC_AGENT_BUILDER_MWT_V1.

### 5. docs/gold_samples/ (NUEVO directorio)

`docs/gold_samples/README.md` + 2 placeholders (`review_response_2026_03.md`, `review_escalation_2026_02.md`).

Cubre:
- Convención de naming
- Estructura de cada gold sample (frontmatter + Input + Output ideal + Contexto + Métricas)
- Política: solo CEO popula, anonimización obligatoria, update gradual, versionado implícito
- Estado actual: PLACEHOLDER hasta CEO popule con casos reales
- Template esperados (6 placeholders mapeados a SKILLs futuros)

### 6. SPEC_AGENT_BUILDER_MWT_V1.md UPDATE v1.0 → v1.1

`docs/SPEC_AGENT_BUILDER_MWT_V1.md` — extensiones del plan:

- 5 decisiones nuevas (D11-D15):
  - D11 Flujos como DAG declarativo en YAML (no UI visual v1)
  - D12 Tareas como entidad de primera clase (Postgres + endpoints + dashboard)
  - D13 Template Factory y Agent Builder = mismo módulo en MWT v1 (separan en FB)
  - D14 Outputs plural por agente (contract.outputs[] reemplaza output_schema singular)
  - D15 Golden samples obligatorios para outputs kind:asset
- Nueva Fase 2.6 (Flujos y Tareas) entre Runtime (Fase 2) y SHADOW (Fase 3): ~1 semana, 6 entregables
- 3 anti-patterns adicionales: loops en DAG, output singular post v1.1, templates sin placeholders/gold

### 7. ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md UPDATE v1.0 → v1.1

`docs/ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md` — sección nueva "Lanzamientos competidores 2026-04":

- OpenAI Workspace Agents (22 abril 2026) descrito con características, adopters, quote testimonio Rippling
- Tabla validación de patterns propios (10 patterns convergen)
- Tabla diferenciales que sobreviven para FaberLoom (7 gaps de OpenAI = oportunidad FB)
- Implicaciones operacionales para MWT v1 (cero impacto)
- Decisiones que influenció (D11, D13, D14, D15)
- Diferencia conceptual Workspace Agents vs Manus vs OpenClaw vs Computer Use

## Decisiones cerradas en esta indexa

| Tipo | Decisión |
|------|----------|
| Schema | outputs plural (contract.outputs[]) reemplaza output_schema singular |
| Schema | golden_samples obligatorios para outputs kind:asset en archetype workflow/autonomous/routine |
| Schema | is_template + placeholders como ciudadanos de primera clase del manifest |
| Schema | flow DAG declarativo (SCH_FLOW_DAG) para archetype workflow/routine/supervisor |
| Schema | tasks como entidad de primera clase (SCH_TASK_ENTITY) con state machine 8 estados |
| Plan | Fase 2.6 (Flujos y Tareas) agregada entre Runtime y SHADOW |
| Producto | 5 templates iniciales catalogados, manifests YAML pendientes Fase 1 |
| Operación | gold_samples directorio creado con placeholders, CEO popula casos reales |
| Estratégico | OpenAI Workspace Agents NO afecta plan MWT v1, valida arquitectura |

## Total cambios KB

- **NUEVOS** (4 archivos): SCH_FLOW_DAG, SCH_TASK_ENTITY, ENT_TEMPLATE_LIBRARY_V1, gold_samples/README
- **NUEVOS placeholders** (2 archivos): gold_samples/review_response_2026_03, gold_samples/review_escalation_2026_02
- **UPDATES** (3 archivos): SCH_SKILL_MANIFEST_V2 v1.1, SPEC_AGENT_BUILDER_MWT_V1 v1.1, ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04 v1.1
- **MANIFIESTO** (1 archivo): este

**Total: 10 archivos tocados.**

## Pendientes nuevos (que esta indexa creó, no bloqueantes Fase 0)

| # | Pendiente | Owner | Cuándo |
|---|-----------|-------|--------|
| 1 | CEO popula gold_samples/review_response_2026_03.md con caso real | CEO | antes Fase 4 graduación REVIEW_TRIAGE |
| 2 | CEO popula gold_samples/review_escalation_2026_02.md con caso real | CEO | antes Fase 4 |
| 3 | Escribir manifests YAML reales de los 5 templates (TPL_*.yaml) | Cowork/Claude Code | Fase 1 SPEC_AGENT_BUILDER_MWT_V1 |
| 4 | Implementar flow_executor Django module | Claude Code | Fase 2.6 |
| 5 | Implementar schema tabla `tasks` + endpoints + worker Celery | Claude Code | Fase 2.6 |
| 6 | Build dashboard CEO portal.mwt.one/agents/tasks | Claude Code | Fase 2.6 |
| 7 | Migrar SKILL_RW_REVIEW_TRIAGE como fork de TPL_REVIEW_TRIAGE | Claude Code | Fase 1 + 2.6 |
| 8 | Opcional: evaluar OpenAI Workspace Agents como benchmark (free hasta 6 mayo) | CEO | nice-to-have, 30 min |

## Pendientes Fase 0 que se mantienen (no movidos)

Los 4 datos operacionales del CEO siguen siendo bloqueante de Fase 1:

1. CEO declara outcome metric primaria de SKILL_RW_REVIEW_TRIAGE (ahora SKILL fork de TPL_REVIEW_TRIAGE)
2. CEO declara baseline pre-agente
3. CEO declara volumen mensual reviews + status quo
4. Lectura SKILL_RW_REVIEW_TRIAGE actual + ARCH_AGENT_PRINCIPLES literal

## Referencias y trazabilidad

**Aprobador:** CEO (sesión Cowork 2026-04-29b).

**Sesión Cowork derivada de:**
- Análisis del lanzamiento OpenAI Workspace Agents (22 abril 2026)
- Observación CEO: "templates pre-hechas + sumar skills + memoria simple"
- Observación CEO: "no veo crear flujos o tareas, como lo vez"
- Observación CEO: "fábrica de plantillas y agent builder, son lo mismo o separados"
- Observación CEO: "step-by-step con plan como columna, golden sample como norte, varios resultados"
- Decisión CEO: mantener foco MWT-only, no rediseñar plan

**Sync al repo canónico:** vía `sync_indexa_20260429b.ps1` (raíz del workspace, generado en esta sesión, con bug fix del mirror identificado en sync anterior).

---

Stamp: VIGENTE — 2026-04-29

Changelog:
- v1.0 (2026-04-29b): creación. Documenta segunda indexa del día con flujos, tareas, templates, outputs plural, golden samples, registro Workspace Agents. 4 archivos nuevos (+2 placeholders), 3 actualizados, 10 archivos tocados total. 9 decisiones cerradas. 8 pendientes nuevos. Foco MWT-only mantenido. FaberLoom no se toca.
