# MANIFIESTO_APPEND_20260429c_ARCHETYPES_TOOLS_SKILLS
id: MANIFIESTO_APPEND_20260429c_ARCHETYPES_TOOLS_SKILLS
type: TRANSITORIO
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE — 2026-04-29c
expires: post-consolidación en MANIFIESTO_CAMBIOS_v2.md (próxima sesión de mantenimiento)
aplica_a: [MWT]

---

## Contexto

**Tercera indexa del día 2026-04-29.** Las dos anteriores cerraron:
- Indexa A (mañana): MANIFIESTO_APPEND_20260429_AGENT_BUILDER_MWT_V1 — plan implementación + manifest schema v2 + regla P15 + research consolidado
- Indexa B (tarde): MANIFIESTO_APPEND_20260429b_FLOWS_TASKS_TEMPLATES — flujos DAG + tasks entidad + templates + outputs plural + golden samples + Workspace Agents

Esta tercera indexa (C) consolida 17 ítems acumulados durante la sesión de la tarde-noche, derivados de:

1. **4 demos OpenAI Workspace Agents** revisados visualmente (Spark/Trove/Tally/Software Review)
2. **Observaciones del CEO sobre arquitectura**:
   - "La voz del CEO debería ser un skill o agente que se invoca"
   - "Hay 3 elementos: plantillas, agent builder, skill builder"
   - "Capa de aprendizaje y mejora de instrucciones"
   - "Para cada cosa pueda haber un agente que se invoque desde la consola"
   - "Si un revisor de email agente, el motor está en el conector no en el agente — cómo establecemos el flujo"
   - "Los procesos deben estar embebidos, no podemos hacer flujos para cada cliente"
   - "Hay arquitecturas distintas según tipo de problema"

`recopila todo e indexa` autoriza la materialización en KB.

## Cambios ejecutados

### 1. SCH_SKILL_MANIFEST_V2.md UPDATE v1.1 → v1.2

`docs/SCH_SKILL_MANIFEST_V2.md` — extensiones del schema canónico:

- Field **`type: skill_package | agent`** (D18) con validaciones diferenciadas por type
- Field **`architectural_archetype`** (D19) obligatorio: Generator/Triage/Validator/Orchestrator/Swarm/Reactive/Skill_package
- Sección **`skills_imports[]`** separada de tools_mcp[] (skills son paquetes reutilizables, tools son APIs externas)
- Sección **`triggers[]`** formal con D16: `connector_workflow_id`, `idempotency_key_field`, `pre_dispatch_filters` con `max_logic_complexity: trivial`, `rate_limit_per_min`, `auth_method`
- Sección **`multi_client_mode + client_resolver`** (D17) para procesos embebidos con config en data
- Sección **`skill_package_metadata`** con `default_prompt` + `invocation_alias` para skills ejecutables standalone vía CLI
- Field **`icon`** opcional en template_metadata
- 8 validaciones build-time nuevas (21-28): type vs archetype, skills imports válidos, triggers solo en agent, tools solo en agent, multi-cliente coherente, pre_dispatch_filters disciplinado, connector workflow versionado, architectural archetype declarado
- Validaciones diferenciadas por type (skill_package vs agent) y por architectural_archetype

### 2. ENT_AGENT_ARCHETYPES_V1.md v1.0 (NUEVO)

`docs/ENT_AGENT_ARCHETYPES_V1.md` — formaliza los 7 arquetipos arquitectónicos.

Cubre:
- Tabla de los 7 arquetipos: 0 Skill_package, 1 Generator, 2 Triage, 3 Validator, 4 Orchestrator, 5 Swarm, 6 Reactive
- Por cada uno: definición, características, casos MWT (mapeo a SHADOW), validaciones específicas, budget heurístico, outcome metric típica
- Mapa completo de los 10 SHADOW MWT + 5 demos OpenAI a los 7 arquetipos
- Implicaciones para bootstrap discusivo del builder (sugerencia de arquetipo + template + budget según intención CEO)
- Roadmap templates futuros indexados por arquetipo

### 3. SCH_FLOW_DAG.md UPDATE v1.0 → v1.1

`docs/SCH_FLOW_DAG.md` — extensiones del schema de flow:

- Nuevo node kind **`config_resolver`** (carga config externa al flow context para D17 multi-cliente)
- Documentado patrón **sub-steps anidados** en `kind: skill_call` con metadata persistida en episodic_memory para visibilidad granular en dashboard
- 2 validaciones nuevas (13, 14) sobre config_resolver

### 4. SPEC_AGENT_BUILDER_MWT_V1.md UPDATE v1.1 → v1.2

`docs/SPEC_AGENT_BUILDER_MWT_V1.md` — 4 decisiones nuevas (D16-D19):

- **D16 — Conector dumb pipe + Agent smart router**: lógica de dominio 100% en agent, n8n solo detect+extract+dispatch. Reglas operacionales (≤5 nodes, sin LLM, sin branches de negocio)
- **D17 — Procesos embebidos, configuración en data**: 1 agent multi-cliente + N configs, NO N agents/flows duplicados. Implementado vía multi_client_mode + client_resolver + node config_resolver
- **D18 — Type formal: skill_package vs agent**: skill_package importable + standalone, agent compone skills+tools+channels+outcome. Validaciones diferenciadas
- **D19 — Architectural archetype obligatorio**: 7 arquetipos del ENT_AGENT_ARCHETYPES_V1, suma validaciones específicas por arquetipo

### 5. SCH_CLI_INTERFACE.md v1.0 (NUEVO)

`docs/SCH_CLI_INTERFACE.md` — interfaz CLI del builder.

Cubre:
- 6 grupos de comandos: agent, skill, template, task, trigger, stats, builder
- Comandos clave detallados (`mwt agent run`, `mwt skill run`, `mwt template fork`, `mwt task approve/reject`, `mwt builder new` interactivo)
- Auth + roles (ceo/curator/consumer)
- Output formats (json/table/summary/tail)
- Integración con scripts y CI
- Diferencia complementaria con dashboard portal.mwt.one
- Roadmap de implementación por fase

### 6. ENT_TOOL_CATALOG_V1.md v1.0 (NUEVO)

`docs/ENT_TOOL_CATALOG_V1.md` — catálogo de tools.

Cubre:
- 15 tools nativos con MCP wrapper (SP-API, Helium 10, Gmail, Drive, Slack, CRM Marluvas, SAP B1, etc.)
- Custom MCP slot inspirado en demo Tally
- n8n como bridge entre conector y agent (D16 reglas operacionales)
- Distinción Tools vs Skills vs Files (D18) con ejemplos
- Heurística para agregar tool nuevo
- Comando audit por tool

### 7. ENT_PLAT_OBSERVABILIDAD.md UPDATE v1.0 → v1.1

`docs/ENT_PLAT_OBSERVABILIDAD.md` — refinamientos del dashboard CEO:

- Columnas nuevas en schema episodic_memory: `worked_duration_s`, `sub_steps JSONB`
- Vistas nuevas en dashboard: flow viewer con sub-steps anidados, worked duration display, post-build assistant 4 acciones, templates con cards e icon
- Sección "Métricas de UX del dashboard" con 6 métricas visibles derivadas de demos OpenAI

### 8. ENT_TEMPLATE_LIBRARY_V1.md UPDATE v1.0 → v1.1

`docs/ENT_TEMPLATE_LIBRARY_V1.md` — refinamiento del catálogo:

- Cada template ahora declara `architectural_archetype` (Generator/Triage/Validator/Orchestrator/Swarm/Reactive)
- Field `icon` agregado a cada template
- UI futura agrupa templates por arquetipo arquitectónico con cards visuales

### 9. ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md UPDATE v1.1 → v1.2

`docs/ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md` — análisis profundo de demos:

- Sección "Análisis profundo: 4 demos OpenAI Workspace Agents" con detalle visual extraído de Spark, Trove, Tally, Software Review
- 7 detalles arquitectónicos clave extraídos
- 4 decisiones (D16-D19) que estos demos influenciaron en el plan v1.2

## Decisiones cerradas en esta indexa

| Tipo | Decisión |
|------|----------|
| Schema | type: skill_package vs agent (D18) |
| Schema | architectural_archetype obligatorio con 7 valores (D19) |
| Schema | skills_imports[] separado de tools_mcp[] |
| Schema | triggers[] formal con connector_workflow_id + pre_dispatch_filters |
| Schema | multi_client_mode + client_resolver |
| Schema | skill_package_metadata con default_prompt + invocation_alias |
| Plan | D16 conector dumb / agent smart |
| Plan | D17 procesos embebidos config en data |
| Plan | 7 arquetipos arquitectónicos formalizados |
| Producto | Custom MCP slot en catálogo |
| UX | Templates con icon agrupados por arquetipo |
| UX | Sub-steps anidados visibles en dashboard |
| UX | Worked duration display |
| UX | Post-build assistant 4 acciones |
| Surface | CLI surface completa documentada |
| Compliance | n8n workflows ≤ 5 nodes (regla operacional D16) |

## Total cambios KB

- **NUEVOS** (3 archivos): ENT_AGENT_ARCHETYPES_V1, SCH_CLI_INTERFACE, ENT_TOOL_CATALOG_V1
- **UPDATES** (6 archivos): SCH_SKILL_MANIFEST_V2 v1.2, SCH_FLOW_DAG v1.1, SPEC_AGENT_BUILDER_MWT_V1 v1.2, ENT_PLAT_OBSERVABILIDAD v1.1, ENT_TEMPLATE_LIBRARY_V1 v1.1, ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04 v1.2
- **MANIFIESTO** (1 archivo): este

**Total: 10 archivos tocados.**

## Pendientes nuevos (no bloqueantes Fase 0)

| # | Pendiente | Owner | Cuándo |
|---|-----------|-------|--------|
| 1 | Extender ENT_PLAT_ACTION_REGISTRY con sección "Custom MCPs" cuando se registre el primero | Cowork/Claude Code | cuando aparezca primer Custom MCP real |
| 2 | Implementar `mwt` CLI con comandos básicos (auth/agent run/task show/approve) | Claude Code | Fase 0 |
| 3 | Migrar SKILL_HUMANIZE_BRAND y SKILL_HUMANIZE_COMMS a `type: skill_package` con default_prompt declarado | Cowork | Fase 1 |
| 4 | Migrar SKILL_DEMAND_FORECASTER declarando explícitamente sub_agents[] (es swarm de 7) | Cowork | Fase 1 post REVIEW_TRIAGE |
| 5 | Diseñar/escribir n8n workflow `gmail_b2b_watcher_v1` cumpliendo D16 (≤5 nodes) | Claude Code | Fase 2.6 |
| 6 | Escribir manifests YAML reales de los 5 templates con `architectural_archetype` y `icon` declarados | Cowork | Fase 1 |

## Pendientes Fase 0 que se mantienen (no movidos)

Los 4 datos operacionales del CEO siguen siendo bloqueante de Fase 1:

1. CEO declara outcome metric primaria de SKILL_RW_REVIEW_TRIAGE
2. CEO declara baseline pre-agente del outcome
3. CEO declara volumen mensual reviews + status quo actual
4. Lectura SKILL_RW_REVIEW_TRIAGE actual + ARCH_AGENT_PRINCIPLES literal

## Referencias y trazabilidad

**Aprobador:** CEO (sesión Cowork 2026-04-29c — tarde-noche del mismo día).

**Sesión Cowork derivada de:**
- Análisis visual de 4 demos OpenAI Workspace Agents (Spark, Trove, Tally, Software Review evaluator)
- Observaciones CEO sobre arquitectura (voz como skill, sub-agents, procesos embebidos, conector vs agent, arquitecturas distintas por tipo)
- Cruce con inventario MWT actual (10 SKILLs SHADOW del Explore agent previo)
- Decisión CEO de mantener foco MWT-only y consolidar en una sola indexa todos los hallazgos del día

**Sync al repo canónico:** vía `sync_indexa_20260429c.ps1` (raíz del workspace, generado en esta sesión, con bug fix del mirror ya validado en sync 20260429b).

---

Stamp: VIGENTE — 2026-04-29c

Changelog:
- v1.0 (2026-04-29c): creación. Documenta tercera indexa del día con 17 ítems consolidados. 4 decisiones nuevas (D16-D19): conector dumb/agent smart, procesos embebidos config en data, type skill_package vs agent, architectural_archetype obligatorio. 3 archivos nuevos (ENT_AGENT_ARCHETYPES_V1, SCH_CLI_INTERFACE, ENT_TOOL_CATALOG_V1) + 6 updates. Análisis profundo de 4 demos OpenAI Workspace Agents. Catálogo de 15 tools nativos + Custom MCP slot. CLI surface completa. Foco MWT-only mantenido.
