# ENT_FB_RESEARCH_AGENT_ECOSYSTEM_2026-04 — Consolidado Research Ecosistema Agent Builders (FaberLoom)
id: ENT_FB_RESEARCH_AGENT_ECOSYSTEM_2026-04
version: 2.0
status: VIGENTE — REFERENCE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE — 2026-04-29f (re-scope FB)
aprobador: CEO (sesión Cowork 2026-04-29 + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SPEC_FB_AGENT_BUILDER_v1.md · SCH_FB_SKILL_MANIFEST_v2.md · POL_FB_OUTCOME_ACCOUNTABILITY.md · ENT_RESEARCH_FABERLOOM_KIMI_2026-04.md

---

## Propósito

Archivo consolidado de **research externo** sobre ecosistema de agent builders, recolectado durante sesión Cowork 2026-04-29 para informar el diseño de la plataforma FaberLoom v1. NO contiene decisiones operativas (esas viven en `SPEC_FB_AGENT_BUILDER_v1` y `POL_FB_OUTCOME_ACCOUNTABILITY`). NO contiene código de los repos analizados.

Este documento sirve como **memoria institucional** de qué se evaluó, qué se descartó, qué se difirió, y qué fuentes fueron consultadas durante el diseño FB. Útil para reconsulta en 6-12 meses cuando se evalúe FB v2 multi-tenant productivo o nuevos archetypes.

---

## Frameworks evaluados — taxonomía 2026

### Anthropic stack (model-as-agent + composición)

| Primitiva | Función | Fuente |
|-----------|---------|--------|
| Claude Agent SDK | runtime programmatic Python/TS, hooks, permissions | platform.claude.com/docs/en/agent-sdk |
| Subagents (Claude Code) | aislamiento de contexto vía Task tool | code.claude.com/docs/en/sub-agents |
| Skills (SKILL.md) | librerías reutilizables auto-disparadas por descripción | code.claude.com/docs/en/skills |
| MCP (Model Context Protocol) | bus para tools/data, estándar abierto adoptado cross-vendor | anthropic.com/news/model-context-protocol |

Modelo mental: composición vía descripción + aislamiento granular + tool search lazy.

### OpenAI stack (handoff + agent-as-tool)

| Primitiva | Función | Estado |
|-----------|---------|--------|
| Swarm (oct 2024) | routine + handoff, experimental | discontinuado, evolucionó a Agents SDK |
| OpenAI Agents SDK (mar 2025) | Agent + Handoff + Guardrails + Tracing | producción |
| Codex CLI (abr-may 2025) | coding agent local con sandbox | producción |
| Assistants API | server-stateful, mono-agente | deprecated mid-2026 |

Modelo mental: network of peers + parallel guardrails + tracing nativo.

### LangGraph (graph + state-typed)

Ganador silencioso enterprise 2025-2026. Pattern: grafo dirigido con TypedDict/Pydantic state, nodos = agentes/tools, edges condicionales. Templates: supervisor, swarm, hierarchical-teams. Más citado en papers arxiv 2025 sobre agentic systems. LangGraph Platform añadió persistencia, time-travel debugging, HITL.

### Hermes Agent (NousResearch)

Repo: github.com/NousResearch/hermes-agent (124k stars, Python, MIT, push activo abril 2026, sucesor de OpenClaw).

Características clave:
- Self-improving con loop cerrado de aprendizaje
- Model-agnostic (cualquier LLM via OpenRouter, Nous Portal, Claude, OpenAI, Kimi, etc.)
- Multi-platform delivery (Telegram, Discord, Slack, WhatsApp, Signal, CLI, Email, SMS)
- Skills compatible con agentskills.io standard (open)
- Cron scheduler + webhooks como Routines (precedente a Claude Code Routines)
- Subagents con isolation y parallelization
- 6 terminal backends (local, Docker, SSH, Daytona, Singularity, Modal serverless)
- MCP nativo + ACP adapter (IDE: VS Code/Zed/JetBrains)
- Plugin system con hooks lifecycle (pre/post tool, pre/post llm, session start/end)
- Profile system (multi-instance aislado, HERMES_HOME por instancia)
- Multiple memory providers pluggables (honcho, mem0, supermemory, byterover, hindsight, holographic, openviking, retaindb)
- 40+ tools, toolset distribution
- Slash command registry único (deriva CLI + gateway + Telegram + Slack + autocomplete)

10 primitivas que valen estudiar para builder MWT (sin copiar código):
1. agentskills.io standard format
2. Plugin hooks lifecycle (5 hooks)
3. Profile system (multi-tenant futuro FB)
4. Routines (cron + webhook + API triggers)
5. Script injection pre-agente (Python pre-procesa, agente razona)
6. MemoryProvider ABC pluggable
7. Tool registry auto-discovery
8. Toolsets agrupaciones
9. Slash command registry único multi-surface
10. Cache-safe deferred config (cambios deferred por default)

### Manus AI vs OpenClaw vs Computer Use

Tres formas de empaquetar Computer Use de Anthropic:

| Sistema | Modo | Riesgo B2B regulado |
|---------|------|---------------------|
| Manus AI | full delegation, agent decide todo en VM remota | alto — opacidad auditoría, viola P3 |
| OpenClaw / Hermes Agent local | screenshots + mouse/teclado en máquina local | medio — útil para CEO research, no producción |
| Claude Computer Use (primitiva) | screenshot → coords → action API | medio — controlable con permissions |
| Claude Agent SDK + MCP (recomendado) | tool calls vía API estructurada | bajo — auditable, schema-locked |

**Decisión MWT:** Computer Use NO es camino para producción. API-based tool use con MCP. Hermes Agent local sirve solo para research interno CEO.

### Otros frameworks (descartados o no aplicables)

| Framework | Por qué no aplica |
|-----------|-------------------|
| AutoGen v0.4 (Microsoft) | actor model distribuido, overhead injustificado a tu escala |
| CrewAI | role-based (PM, engineer, QA) — modelo MWT es funcional no role-based |
| MetaGPT | SOP-driven company-as-code, mismo problema que CrewAI |
| Kimi K2 model-as-agent | ya estás de facto sobre Claude, sin razón para migrar |

---

## Claude Code leak 2026-03-31 — insights arquitectónicos

Anthropic publicó accidentalmente 512k líneas de Claude Code el 31 de marzo de 2026 vía sourcemap mal configurado (`.npmignore` faltante + Bun bug + R2 bucket público). Material **no copiable** (riesgo IP/legal aunque MIT no aplique al leak), pero **conceptos arquitectónicos sí estudiables** vía análisis públicos (dev.to/varshithvhegde, alex000kim.com, blog Gabriel Anhaia).

### Subsistemas revelados que valen para MWT

**Three-layer memory architecture**
- Layer 1: MEMORY.md (índice de pointers ~150 chars/entry, siempre cargado, almacena LOCATIONS no datos)
- Layer 2: Topic Files (conocimiento real, fetched on-demand, nunca todos en contexto)
- Layer 3: Raw Transcripts (nunca re-leídos completos, solo grep'd)
- **Strict Write Discipline**: agente solo actualiza índice tras file write exitoso confirmado
- **Memory-as-hint, verify-against-actual**: agente lee archivo real antes de actuar, no confía ciego

**KAIROS — autonomous background daemon**
- Always-on, sesiones background mientras CEO idle
- `autoDream` nightly: merges observaciones, remueve contradicciones, valida facts
- Brief output mode + tools especiales

**ULTRAPLAN — long-running planning**
- Offload planning complejo (30 min) a Cloud Container Runtime con Opus
- Approve from phone/browser
- Sentinel `__ULTRAPLAN_TELEPORT_LOCAL__` para retornar resultado

**Coordinator Mode**
- Un Claude spawning + managing multiple worker Claudes en parallel
- Task distribution + result aggregation + conflict resolution
- Confirma archetype Supervisor

**Tool plugin architecture**
- ~40 tools en ~29k LOC base
- Cada tool: permission model propio + validation + output formatting
- Confirma capabilities + visibility per-tool del SP Page Builder pattern

**Anti-distillation**
- `ANTI_DISTILLATION_CC` flag → API request `anti_distillation: ['fake_tools']`
- Server inyecta decoy tool definitions + summarization de reasoning entre tool calls + firmas criptográficas
- Aplica a FaberLoom B2B futuro, no a MWT

**Frustration detection regex**
- Regex sobre user input ("wtf", "fucking broken", "useless") en vez de LLM call
- Concreta P14 deterministic-first

**MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3**
- Después de 3 fallos seguidos, simplemente para
- Costó 250k API calls/día pre-fix
- Regla operacional: todo loop necesita stop por consecutive failures

**Undercover Mode**
- Hardcode `NO force-OFF` posible — solo se puede forzar ON
- Dead-code-eliminated en external builds
- Patrón hardcode-only-direction para info que NUNCA debe filtrar

### Fuentes leak (referencias públicas, no código)

- dev.to/varshithvhegde/the-great-claude-code-leak-of-2026-...
- Análisis Gabriel Anhaia (architecture walkthrough)
- Análisis Alex Kim (alex000kim.com)
- VentureBeat, The Register, CNBC, Fortune, Axios, Decrypt
- Hacker News thread

---

## Repos open source analizados (blog mejba.me)

Post: "9 Repos de GitHub Que Hicieron Mi Claude Code 10 Veces Más Rápido" — mejba.me/es/blog/best-github-repos-claude-code

| Repo | Licencia | Patrón distintivo | Aplicabilidad MWT |
|------|----------|-------------------|---------------------|
| **claude-mem** (thedotmack) | AGPL-3.0 | 5 lifecycle hooks + 3-layer progressive disclosure + `<private>` tags | conceptos sí, código NO (AGPL contagioso) |
| **superpowers** (obra) | MIT | subagent-driven development + two-stage review (spec then quality) + skills auto-trigger | dos-stage review aplicable a COMPLIANCE_CHECKER |
| **GSD** (gsd-build) | MIT | wave execution + atomic commits per task + XML prompt format + workflow files canónicos + discuss mode + profile system de modelos | XML prompt format y workflow files son adopción directa |
| **n8n-MCP** (czlonkowski) | MIT | multi-level validation + templates first + diff-based partial updates + silent execution + never-trust-defaults | validación multi-nivel para tus state machines |
| **LightRAG** (HKUDS) | academic | dual-level retrieval (low entities + high themes) + KG extraction + reranker + WebUI graph viz | mejora pgvector cuando precisión <80%, diferido |

Patrones a robar (sin copiar código), priorizados:
1. 5 lifecycle hooks (claude-mem) — adoptado en SPEC_AGENT_BUILDER fase 0
2. XML prompt formatting (GSD) — adoptado en runtime
3. Workflow files canónicos (GSD: PROJECT/STATE/PLAN/SUMMARY) — base para expediente FaberLoom futuro
4. Wave execution (GSD) — futuro para DEMAND_FORECASTER swarm
5. Two-stage review (superpowers) — futuro para COMPLIANCE_CHECKER
6. Discuss mode (GSD) — futuro para Bootstrap del builder
7. Multi-level validation (n8n-MCP) — adoptado en hooks
8. Profile system de modelos (GSD) — implementado vía LiteLLM
9. Atomic commits per task (GSD) — adoptado en builder
10. KG dual-level retrieval (LightRAG) — diferido

---

## Kimi research FaberLoom — MOVIDO

El research Kimi K2 swarm sobre FaberLoom B2B regulado multi-tenant fue **extraído de este archivo** durante el saneamiento de KB del 2026-04-29d para evitar context bleed entre proyectos.

**Archivo nuevo:** `ENT_RESEARCH_FABERLOOM_KIMI_2026-04.md` (`aplica_a: [FaberLoom]`)

Razón del movimiento: este archivo aplica solo a MWT. El research Kimi FB no aporta a decisiones MWT v1 y mezclarlo aquí generaba decisiones contaminadas. Si necesitás el research Kimi FB, abrí el archivo separado.

De ese research, lo único que aplicó a MWT y se mantuvo aquí:

- Extensión SKILL.md con namespace propio (adoptado vía SCH_SKILL_MANIFEST_V2)
- Decisión API Anthropic hasta 5k invocaciones/día
- Stack Langfuse como observabilidad
- Atención a LFPDPPP México (porque MWT vende a Marluvas/Tecmater MX)

Todo lo demás del research (multi-tenant isolation, OPA Gateway, Mem0, A2A bridge, anti-distillation, capability marketplace, profile system criptográfico) **NO aplica MWT** y vive ahora en el archivo FB-specific.

---

## Inventario MWT actual (snapshot 2026-04-29)

**Hosting:** Hostinger KVM 8 (8 vCPU, 32 GB RAM, 400 GB NVMe), Ubuntu 24, ~$20-50/mes.

**12 containers activos:**
1. mwt-knowledge (Django + Gunicorn, :8000) — backend
2. PostgreSQL 16 + pgvector (:5432)
3. Redis 7 (:6379)
4. Celery + Celery Beat
5. Next.js mwt.one (:3000)
6. Next.js ranawalk.com (:3001)
7. Next.js portal.mwt.one (:3002)
8. n8n (:5678)
9. Windmill (:8080)
10. MinIO (:9000/:9001)
11. Nginx (:80/:443)

**3 containers nuevos para builder v1 (decisión SPEC_AGENT_BUILDER_MWT_V1):**
- Dockge (catálogo Hostinger)
- LiteLLM (catálogo Hostinger, gateway 100+ LLMs)
- Langfuse + ClickHouse (manual, MIT)

**Headroom**: ~10 GB RAM usados de 32, sobra para los 3 nuevos (+3.5 GB). Disco 307 GB libres.

**Hostinger Docker Catalog:** 200+ apps en 13 categorías. Útiles para MWT/FB futuro: LiteLLM, Authentik, Keycloak, Kong, Traefik (preinstalado VPS nuevos con auto-SSL), Grafana, Prometheus, Jaeger, Milvus, Weaviate.

---

## Framework Mitjana — productividad real vs falsa

Video Xavier Mitjana (youtu.be/T2OHlsqZmqU) sobre trampa de productividad con IA. Operacionalizado para agentes en POL_OUTCOME_ACCOUNTABILITY.

3 filtros de impacto (qué debe generar un día/run productivo):
1. **Activo** — output reutilizable
2. **Decisión** — loop cerrado
3. **Aprendizaje** — entrada de memoria validada

Pregunta filtro: **¿le pido HACER o PENSAR?**
- HACER (ejecutar tareas) — adelante, es trabajo de agente
- PENSAR (decidir, evaluar, juzgar) — detente, es trabajo del CEO

Pyramid de métricas L0-L5 derivada y adoptada en SPEC_AGENT_BUILDER_MWT_V1.

---

## Decisiones de IP/legal aplicables

1. **No descargar código del Claude Code leak.** Conceptos sí, código no.
2. **No copy-paste de hermes-agent (MIT) ni claude-mem (AGPL) ni superpowers/GSD/n8n-MCP/LightRAG.** Implementación desde cero.
3. **Adoptar standards abiertos:** SKILL.md (agentskills.io), MCP, A2A si aplica futuro.
4. **Naming MWT propio.** No "KAIROS", "ULTRAPLAN", "BUDDY", "Coordinator". Equivalentes: NIGHTLY_REFLECTION, ASYNC_PLANNER, AGENT_SUPERVISOR.
5. **Verificar dependencias transitivas** si alguna vez se forkeara algo (no es plan).
6. **Trade secret para SKILLs sensibles**: visibility CEO_ONLY o INTERNAL, no publicar.

---

## Lanzamientos competidores 2026-04

### OpenAI Workspace Agents (22 abril 2026)

URL: https://openai.com/es-419/index/introducing-workspace-agents-in-chatgpt/

OpenAI lanzó "Workspace Agents en ChatGPT" como evolución de los GPTs. Plataforma para que equipos en ChatGPT Business/Enterprise/Edu/Teachers creen agentes compartidos sin código. Powered by Codex en cloud.

**Características clave:**
- Crear agente describiendo el flujo en chat (low-code)
- Ejecutan en Codex cloud (no infra del cliente)
- Memoria persistente
- Multi-platform: ChatGPT + Slack (más por venir)
- Triggers programados + webhooks
- Aprobación humana antes de acciones sensibles
- Analytics + governance enterprise (API de cumplimiento, RBAC, suspensión)
- Templates pre-hechas para finance/sales/marketing
- Anti prompt injection built-in
- Gratis hasta 6 mayo 2026, después pricing créditos

**Adopters tempranos publicados:** Rippling, SoftBank Corp, Better Mortgage, BBVA, Hibob.

**Quote testimonio (Rippling):** "Lo difícil de crear un agente no es el modelo. Son las integraciones, la memoria y la experiencia del usuario."

### Validación que aporta a MWT/FaberLoom

| Pattern propio | Validado por OpenAI |
|----------------|---------------------|
| Composición declarativa "describe el flujo" (Bootstrap del builder) | sí, idéntico |
| Templates por dominio (Template Library) | sí, OpenAI con templates finance/sales/marketing |
| Multi-platform delivery | sí, ChatGPT + Slack (Hermes Agent ya lo tenía) |
| Routines (cron + webhook) | sí, OpenAI los expone igual |
| P3 draft-first absoluto (aprobación CEO) | sí, "approval before action" idéntico |
| Memoria persistente + analytics | sí |
| Anti prompt injection | sí, built-in |
| Step-by-step con plan como columna | sí, observación derivó D11 (flujos DAG declarativos) y D14 (outputs plural) |
| Golden sample como norte | sí, derivó D15 (golden samples obligatorios) |
| Outputs múltiples por run | sí, derivó D14 (contract.outputs[] plural en SCH v1.1) |

### Diferenciales que sobreviven para FaberLoom

| Gap OpenAI Workspace Agents | Diferencial FaberLoom |
|------------------------------|------------------------|
| Lock-in OpenAI Codex cloud | model-agnostic (Claude / Kimi / open via LiteLLM) |
| Compliance LFPDPPP México / data residency LATAM ausente | constraint LFPDPPP-first desde diseño (ver Frente 6 Kimi research FB) |
| Cliente fabricante industrial no es ChatGPT-native | UX vertical (wizards, no chat-first) |
| Sin integración ERP fabricantes (SAP B1, Bind, Aspel, Siigo) | capabilities verticales en catálogo |
| Pricing créditos volátil (post 6 mayo) | pricing predecible por outcome/tenant |
| Multi-tenant pool genérico | multi-tenant criptográfico B2B regulado (cuando FB exista) |
| Dependencia internet + cloud OpenAI | self-hosted opcional |

Los 5 diferenciales son reales y duros de copiar para OpenAI a corto plazo. La vara competitiva subió, pero MWT v1 (operación interna) no cambia.

### Implicaciones operacionales para MWT v1

- **Cero impacto.** El builder MWT no compite con esto — es operación interna con Claude API + tu KB + compliance específico. Sigue plan tal cual.
- **Validación**: el patrón general que diseñamos (manifest declarativo + templates + flujos + golden samples + outputs plural) está siendo validado simultáneamente por OpenAI con producto comercial. Estamos en buen norte.
- **Acción opcional**: 30 min para evaluar Workspace Agents como benchmark (free hasta 6 mayo). Útil para vara de calidad y UX a copiar (no para uso producción por lock-in + compliance).

### Decisiones que esto influenció en SPEC v1.1

- D11 — Flujos como DAG declarativo (matchea step-by-step pattern OpenAI)
- D13 — Template Factory y Builder = mismo módulo (OpenAI no separa, valida KISS para v1)
- D14 — Outputs plural (`contract.outputs[]` reemplaza `output_schema` singular)
- D15 — Golden samples obligatorios (operationaliza "norte de calidad")

### Diferencia conceptual: Workspace Agents vs Manus AI vs OpenClaw

| Sistema | Modelo | Nivel autonomía |
|---------|--------|-----------------|
| **OpenAI Workspace Agents** (abr 2026) | tool-based, plan declarativo, HITL granular | nivel 3-4 bounded |
| **Manus AI** | full delegation en VM remota | nivel 5-6 abierto |
| **OpenClaw / Hermes Agent local** | screenshots + mouse/teclado | nivel 4 con humano supervisado |
| **Claude Computer Use** (primitiva) | screenshot → coords → action | depende del integrador |

Workspace Agents y MWT-builder convergen en el mismo punto del espectro (tool-based + bounded). Manus y Computer Use ocupan otro nicho.

---

## Análisis profundo: 4 demos OpenAI Workspace Agents (NUEVO v1.2)

Sesión Cowork 2026-04-29c revisó 4 video-demos públicos de OpenAI sobre Workspace Agents (~70-156s cada uno). Detalles visuales extraídos.

### Demo 1: Lead Outreach (Spark, 110s)

Casos:
- Bootstrap UI: "What should your agent do?" + sugerencias inline (Chat Q&A, Morning planner, Bug triage) + cards templates abajo (Customer, Chief of Staff, Data Analyst, Knowledge)
- Prompt CEO: *"Build a sales agent that researches each new lead, grades the lead, drafts & sends the first outreach email, drafts the follow up email, and schedules a calendar reminder"*
- **Agent plan ANTES de Create**: Nombre Spark + descripción + Tools (Web Search, Gmail, Google Calendar) + Channels + Capabilities (Research new leads / Score lead quality / Draft outreach emails / Schedule follow-up reminders) + botones Edit plan / Start building
- Editor del agente con secciones SEPARADAS visualmente: **Tools** + **Skills** (+ Add skill) + **Files** (Memory + Add) + **Channels**. Botones top: Create / **Schedule** / Preview
- Instructions con estructura: **Role** + **Lead Intake And Assumptions**
- Invocación con structured input pegado (Name / Email / Phone / Company Size / Company / Request)
- Runtime: step "Review the OpenAI docs skill guidance" + sub-steps con search bubbles + sources visitadas (openai.com, help.openai.com)

### Demo 2: Third-Party Risk Manager (Trove, 126s)

Casos:
- Bootstrap con upload: CEO sube **tprm-risk-research.zip** (skill empaquetado como ZIP) + prompt: *"Build Trove... uses web search plus a TPRM risk research skill... references Google Drive risk criteria spreadsheet as source of truth, creates polished Google Doc report"*
- Editor del agente: Tools: Google Drive · Google Docs · Web search. **Skills: tprm-risk-research** (con icono propio, ZIP cargado). Files: Memory. Instructions con **Role** + **Skill Directory** ("Use tprm-risk-research for substantive third-party risk research")
- Summary of changes: ✓ Attached the TPRM risk research skill / ✓ Wrote Trove's vendor risk assessment instructions / ✓ Set the subtitle / ✓ Added 2 starter prompts / ✓ Updated icon
- Runtime: Step "Open the TPRM workflow and locate the risk criteria spreadsheet" con **sub-steps** Running command / Searching files (research-template.md) / Calling get_profile / Calling search / Calling search documents — visibilidad granular

### Demo 3: Weekly Metrics Reporting (Tally, 156s)

Casos:
- **Tools picker**: Modal con búsqueda + lista: Image generation · Web search · **Custom MCP** · Google Calendar · Google Drive · Gmail · SharePoint · Slack · Adobe Express · Adobe Photoshop · Agentforce Sales · Airtable. Panel derecho con icon + nombre + descripción + botón "Add"
- Editor Tally: Tools: Google Drive. **Skills: executive-update-drafter + weekly-visualization-workflow + metrics-standardization-workflow** (3 skills cargados). Files: Memory. Instructions con **Role** + **Data** (expected columns: snapshot_week_end, account_id, plan_type, arr_l7d_usd, wau_l7d, mau_l30d, etc.)
- **Sidebar post-build assistant**: "How should we improve this agent?" con 4 acciones: Test this agent · Add advanced logic · Configure when the agent runs · Optimize this agent
- Runtime: "Worked for 4m 30s" + "The weekly update is ready in Google Docs"

### Demo 4: Software Review Evaluator (92s)

Casos:
- **Skill detail view**: software-review-evaluator (Skill · 2 files). Tabla con **Name** / **Short description** / **Description** / **Default prompt** ("Use $software-review-evaluator to compare...") + **Skill instructions**
- Slack canal #software-requests con mensajes de empleados pidiendo herramientas (BigQuery, Calendly, Zendesk, Asana)
- Thread con agente respondiendo a Russell Kang sobre Screen Studio: "**3:34 IT action opened**" + "**License review created: SWR-17**" + "Approval needed to provision seats" + "Sent by **Slate**" (sistema IT externo)

### 7 detalles arquitectónicos clave extraídos

1. **"Custom MCP" como entrada del catálogo de Tools** — registrar MCP servers custom (URL endpoint + auth + schema) sin código → adoptado en ENT_TOOL_CATALOG_V1
2. **Skills múltiples por agente (3 skills en Tally)** — confirma `skills_imports[]` lista, no campo único → adoptado en SCH_SKILL_MANIFEST_V2 v1.2
3. **Skill metadata con default_prompt + sintaxis `$skill-name`** — adoptado en SCH_SKILL_MANIFEST_V2 v1.2 (skill_package_metadata)
4. **Post-build assistant con 4 acciones** — adoptado en ENT_PLAT_OBSERVABILIDAD v1.1 (dashboard CEO)
5. **"Worked for 4m 30s" visible al usuario** — adoptado en episodic_memory (worked_duration_s)
6. **Slack threads como delivery channel real + tickets externos** — confirma cross-platform delivery + outputs side_effect
7. **"Data" section en Instructions** — adoptado como `instructions.data_schema` opcional

### Decisiones que estos demos influenciaron en el plan v1.2

- D16 — Conector dumb / Agent smart (la lógica vive en el agent, no en n8n)
- D17 — Procesos embebidos, configuración en data (multi-cliente sin duplicar agents)
- D18 — Type formal: skill_package vs agent (Tools/Skills/Files separados)
- D19 — Architectural archetype obligatorio (6 arquetipos identificados)

---

## Estado de este documento

Este es un **archivo de referencia VIGENTE** pero estable. Se actualiza si:
- Aparecen nuevos frameworks que cambien la taxonomía
- El leak Claude Code revela nueva información relevante
- Kimi (u otra herramienta) emite research adicional sobre estos temas
- Se descubre breach o quiebre legal en algún framework adoptado
- Lanzamientos competidores relevantes para FaberLoom

Para decisiones operativas vivas: ver `SPEC_FB_AGENT_BUILDER_v1`, `SCH_FB_SKILL_MANIFEST_v2`, `POL_FB_OUTCOME_ACCOUNTABILITY`.

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29): creación con scope MWT-only erróneo. Consolidado de research externo sesión Cowork 2026-04-29. Cubre: stacks Anthropic/OpenAI/LangGraph/Hermes/Manus/Computer Use, Claude Code leak insights, 5 repos blog mejba.me, Kimi research FaberLoom (archivado), framework Mitjana, inventario operativo, decisiones IP/legal.
- v1.1 (2026-04-29b): agregada sección "Lanzamientos competidores 2026-04" con OpenAI Workspace Agents. Tabla de validación de patterns propios + diferenciales + decisiones D11-D15 influenciadas.
- v1.2 (2026-04-29c): agregada sección "Análisis profundo: 4 demos OpenAI Workspace Agents". 7 detalles arquitectónicos + 4 decisiones D16-D19.
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04 → ENT_FB_RESEARCH_AGENT_ECOSYSTEM_2026-04. El research siempre fue para informar el diseño de la plataforma FB; quedó etiquetado como MWT por error de scoping. Aprobador: CEO sesión re-scoping 2026-04-29f.**
