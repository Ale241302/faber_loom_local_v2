# MANIFIESTO_APPEND_20260429_AGENT_BUILDER_MWT_V1
id: MANIFIESTO_APPEND_20260429_AGENT_BUILDER_MWT_V1
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

Sesión Cowork 2026-04-29 derivó en plan de implementación del **Agent Builder MWT v1**, derivado del cruce de:

1. Framework Mitjana (video Xavier Mitjana sobre trampa de productividad con IA): 3 filtros Activo/Decisión/Aprendizaje, pregunta filtro HACER vs PENSAR
2. Research externo aprendido en sesión:
   - Hermes Agent (NousResearch) — repo verificado github.com/NousResearch/hermes-agent
   - Claude Code leak 2026-03-31 (insights arquitectónicos: three-layer memory, KAIROS, ULTRAPLAN, Coordinator, anti-distillation, frustration regex, MAX_CONSECUTIVE_FAILURES=3)
   - 5 repos del blog mejba.me: claude-mem (AGPL), superpowers (MIT), GSD (MIT), n8n-MCP (MIT), LightRAG (academic)
   - Kimi research FaberLoom (7 frentes, archivado para FB futuro, no aplica MWT v1)
3. Inventario MWT real: 12 containers Hostinger KVM 8, 10 SKILLs en SHADOW, ARCH_AGENT_PRINCIPLES P0-P14
4. Decisión scope MWT-only por 6 meses (FaberLoom diferido a prospect/LOI real)
5. Catálogo Hostinger Docker (200+ apps, 13 categorías) — selección de 3 nuevos containers

`indexa` autoriza la materialización en KB.

---

## Cambios ejecutados

### 1. SPEC_AGENT_BUILDER_MWT_V1.md v1.0 (NUEVO — plan medular del builder)

`docs/SPEC_AGENT_BUILDER_MWT_V1.md` — el plan completo de implementación.

Cubre:
- 10 decisiones consolidadas (D1-D10): scope MWT-only, Hostinger se queda, 3 containers nuevos, memory simple, manifest extiende SKILL.md, hooks Python sobre OPA, observability Langfuse + LiteLLM, modelo único Sonnet 4.6, tools como sub-procesos, techo autonomía nivel 3-4
- 4 fases de implementación 12 semanas: Foundation, Manifest schema, Runtime, SHADOW, Graduación
- Lo que se difiere explícitamente (Letta/Mem0, OPA/Cedar, KAIROS, ULTRAPLAN, three-layer completo, knowledge graph, FB)
- Lo que NO se hace nunca (Computer Use, auto-prompt-update, multi-tenant en v1, self-host LLM, fork código, inventar manifest, código del leak)
- Sistema métricas L0-L5 activo desde día 1
- Pre-requisitos para arrancar: 3 datos operacionales del CEO + lectura del repo
- Triggers de aborto/pivot

### 2. SCH_SKILL_MANIFEST_V2.md v1.0 (NUEVO — schema canónico)

`docs/SCH_SKILL_MANIFEST_V2.md` — schema del manifest v2 para todo SKILL_ MWT.

Cubre:
- Frontmatter base SKILL.md (estándar Anthropic, 26+ plataformas, agentskills.io)
- Extensión namespaceada `metadata.mwt.*` con 12 secciones (identidad, inputs, contract, state_machine, tools_mcp, memory, deliverable, outcome, budget, autonomy, tenant_scope, consumed_by/observability)
- 12 validaciones build-time obligatorias del compiler
- Plan de migración de los 10 SKILLs SHADOW (orden: REVIEW_TRIAGE primero, después LISTING_OPT, DEMAND_FORECASTER, COMPLIANCE_CHECKER, resto)
- Compatibilidad cross-vendor preservada (Claude Code, Hermes, Cursor, Cline, OpenCode, Gemini CLI, agentskills.io hub)
- Ejemplo mínimo `SKILL_TEST_HELLO` para smoke test del compiler

### 3. POL_OUTCOME_ACCOUNTABILITY.md v1.0 (NUEVO — regla inquebrantable P15)

`docs/POL_OUTCOME_ACCOUNTABILITY.md` — formaliza P15 como extensión de ARCH_AGENT_PRINCIPLES.

Cubre:
- Declaración: todo agente vivo declara y mide outcome metric primaria; sin outcome trending observable a 90 días, vuelve a SHADOW
- Contexto Mitjana: actividad ≠ impacto, métricas L0-L1 son higiene no evidencia
- Aplicación operacional: declaración obligatoria en manifest (validación 6 SCH_SKILL_MANIFEST_V2), 4 condiciones para outcome legítimo, cadencia revisión
- 4 triggers kill switch automático
- Validación cruzada con P3, P4, P5, P9, P14 (no redefine, agrega dimensión)
- 7 anti-patterns prohibidos (vanity metrics)
- 5 heurísticas para CEO al elegir outcome
- Aplicación retrospectiva: 10 SKILLs SHADOW deben declarar outcome al migrar a v2
- Métricas de salud de la propia regla (evitar burocracia)

### 4. ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md v1.0 (NUEVO — referencia archivada)

`docs/ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md` — consolidado del research externo de la sesión.

Cubre:
- Frameworks evaluados: Anthropic stack, OpenAI stack, LangGraph, Hermes Agent, Manus AI, Computer Use, AutoGen v0.4, CrewAI, MetaGPT
- 10 primitivas Hermes Agent que valen estudiar (sin copiar código)
- Claude Code leak insights arquitectónicos (three-layer memory, KAIROS, ULTRAPLAN, Coordinator, tool plugin architecture, anti-distillation, frustration regex, MAX_CONSECUTIVE_FAILURES, Undercover Mode)
- 5 repos blog mejba.me con licencia y patrón distintivo
- Kimi research FaberLoom: 7 frentes + 4 insights cruzados + 7 decisiones desbloqueadas (archivado para FB, autocrítica documentada)
- Inventario MWT actual snapshot
- Hostinger Docker Catalog útiles para futuro
- Framework Mitjana operacionalizado
- Decisiones IP/legal aplicables (no copiar código, adoptar standards abiertos, naming MWT propio)

### 5. ENT_PLAT_OBSERVABILIDAD.md (UPDATE — de STUB v0.1 a VIGENTE v1.0)

`docs/ENT_PLAT_OBSERVABILIDAD.md` — stack de observabilidad MWT pasa de "[PENDIENTE — contenido por crear]" a contenido real.

Cubre:
- Stack confirmado: Langfuse + LiteLLM + Dockge + Postgres episodic_memory + dashboard CEO custom (todos $0 licencia)
- Stack descartado con razón (LangSmith, Phoenix, Helicone, Braintrust, W&B Weave, Logfire, Prometheus, Jaeger)
- Pyramid métricas L0-L5 con métricas concretas, origen, frecuencia
- Schema episodic_memory canónico (SQL completo)
- 4 lifecycle hooks Django ubicación (pre_llm_call, pre_tool_call, post_tool_call, on_session_end)
- Dashboards: Langfuse out-of-box, custom CEO a construir, reportes mensuales semi-automatizados
- Plan de instalación operacional (referencia SPEC_AGENT_BUILDER_MWT_V1 Fase 0)
- Compatibilidad ARCH_AGENT_PRINCIPLES (P3, P4, P5, P7, P9, P13, P14, P15)

### 6. ENT_PLAT_INFRA.md (UPDATE — v1.0 → v1.1)

`docs/ENT_PLAT_INFRA.md` — agregadas secciones B3 (containers planeados Fase 0), B4 (capacity post-Fase 0), G (foco MWT-only).

Cubre cambios:
- B3: tabla con Dockge, LiteLLM, Langfuse, ClickHouse (RAM, CPU, disco, función, método install)
- B4: capacity proyectada post-instalación (RAM 13.75 GB / 32 GB; nota sobre desbordamiento CPU teórico y mitigación)
- D: subdominios planeados (langfuse.mwt.one, litellm.mwt.one, dockge.mwt.one)
- G: declaración explícita de foco MWT-only, FaberLoom requerirá infra propia separada
- Status: DRAFT → VIGENTE
- Changelog v1.1 con derivación SPEC_AGENT_BUILDER_MWT_V1

---

## Decisiones cerradas en esta indexa

| Tipo | Decisión |
|------|----------|
| Scope | MWT-only por 6 meses, FaberLoom condicional |
| Hosting | Hostinger KVM 8 actual, sin migrar |
| Containers nuevos | Dockge + LiteLLM (catálogo) + Langfuse (manual) |
| Memory v1 | pgvector + tabla episodic, sin Letta/Mem0 |
| Manifest schema | extender SKILL.md con `metadata.mwt.*` |
| Policy enforcement | hooks Python Django, sin OPA/Cedar |
| Observability | Langfuse + LiteLLM + Dockge + custom dashboard CEO |
| Modelo LLM | Sonnet 4.6 vía LiteLLM |
| Tools | sub-procesos / módulos Python, no containers |
| Autonomía | techo nivel 3-4 bounded |
| Primer agente | SKILL_RW_REVIEW_TRIAGE |
| Regla nueva | P15 Outcome Accountability formalizada |

---

## Pendientes que quedan (no bloqueantes para arranque Fase 0)

| # | Pendiente | Owner | Prioridad |
|---|-----------|-------|-----------|
| 1 | CEO declara outcome metric primaria de SKILL_RW_REVIEW_TRIAGE (AHR / TTR / repeat purchase / case log / conversion / otra) | CEO | alta — bloqueante Fase 1 |
| 2 | CEO declara baseline_value pre-agente del outcome metric | CEO | alta — bloqueante Fase 1 |
| 3 | CEO declara volumen mensual aproximado de reviews Rana Walk Amazon | CEO | media — informa budget |
| 4 | CEO declara status quo: quién maneja reviews hoy + time-to-response actual | CEO | media — informa target_at_60d |
| 5 | Lectura completa SKILL_RW_REVIEW_TRIAGE actual + ARCH_AGENT_PRINCIPLES literal + SPEC_ACTION_ENGINE | Cowork/Claude Code | media — bloqueante Fase 1.1 |
| 6 | Migración progresiva de los 9 SKILLs restantes a manifest v2 | post-Fase 1 | baja — backlog |
| 7 | Replantear Kimi research si se reactiva FaberLoom (prospect/LOI) | condicional | baja — futuro |
| 8 | Investigación de métricas/productividad (Kimi 2 prompt armado, no lanzado) | opcional | baja — nice to have |

---

## Referencias y trazabilidad

**Aprobador:** CEO (sesión Cowork 2026-04-29).

**Sesión Cowork derivada de:**
- Brainstorming arquitectónico Agent Builder (parte 1 conversación 2026-04-29)
- Mockups visuales del builder (manifest editor, registry, audit, patch broadcast)
- Discusión arquetipos de agente (skill, workflow, autonomous, supervisor, swarm) y niveles autonomía 0-6
- Discusión aprendizaje y memoria (capas 0-5, KAIROS-style, capa 4 prohibida)
- Discusión MWT vs FaberLoom (separación clara aplicada en parte 2)
- Análisis Mitjana sobre productividad real
- Research externo (Hermes Agent, repos blog, Claude Code leak)
- Análisis Kimi research FaberLoom con autocrítica documentada
- Catálogo Hostinger Docker
- Mapeo a infra real MWT (12 containers existentes)

**Archivos creados (4):**
- docs/SPEC_AGENT_BUILDER_MWT_V1.md
- docs/SCH_SKILL_MANIFEST_V2.md
- docs/POL_OUTCOME_ACCOUNTABILITY.md
- docs/ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md

**Archivos actualizados (2):**
- docs/ENT_PLAT_OBSERVABILIDAD.md (STUB v0.1 → VIGENTE v1.0)
- docs/ENT_PLAT_INFRA.md (v1.0 → v1.1)

**Total cambios KB:** +4 archivos nuevos, +2 actualizados, +1 manifiesto = 7 archivos tocados.

**Sync al repo canónico:** vía `sync_indexa_builder_mwt_v1.ps1` (raíz del workspace, generado en esta sesión).

---

Stamp: VIGENTE — 2026-04-29

Changelog:
- v1.0 (2026-04-29): creación. Documenta indexa de la sesión Cowork 2026-04-29 con plan de implementación Agent Builder MWT v1. 4 archivos nuevos, 2 actualizados. 12 decisiones consolidadas. Regla P15 nueva. Foco MWT-only declarado. FaberLoom diferido. 8 pendientes documentados.
