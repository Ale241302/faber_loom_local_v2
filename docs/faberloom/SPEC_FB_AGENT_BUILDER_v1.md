# SPEC_FB_AGENT_BUILDER_v1 — Plan de Implementación Agent Builder FaberLoom v1
id: SPEC_FB_AGENT_BUILDER_v1
version: 2.0.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-04-29 (re-scopeado de MWT a FB)
aprobador: CEO (sesión Cowork 2026-04-29 + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SPEC_FABERLOOM_MVP.md · SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md · SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md · SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md · ARCH_AGENT_PRINCIPLES.md · SCH_FB_SKILL_MANIFEST_v2.md · POL_FB_OUTCOME_ACCOUNTABILITY.md · ENT_FB_AGENT_ARCHETYPES_v1.md · SCH_FB_FLOW_DAG.md · SCH_FB_TASK_ENTITY.md · ENT_FB_TEMPLATE_LIBRARY_v1.md · ENT_FB_TOOL_CATALOG_v1.md · gold_samples/

---

## Declaración

Este documento materializa el plan de construcción del **Agent Builder de FaberLoom v1**, derivado de sesión Cowork 2026-04-29 que cruzó: framework Mitjana de productividad, research externo (Hermes Agent NousResearch, Claude Code leak 2026-03, Kimi research FaberLoom multi-tenant, 5 repos blog mejba.me), demos OpenAI Workspace Agents (Spark/Trove/Tally/Scout/Software Review), principios fundacionales P0-P14 + P15 outcome accountability, y los 7 arquetipos arquitectónicos.

**Foco firme: FB v1 con un único tenant beta — Muito Work Limitada (MWT/Rana Walk).** Multi-tenant productivo (≥2 tenants pagantes) queda como roadmap FB v2 condicional a segundo prospect/LOI real. El research de Kimi sobre FaberLoom multi-tenant cripto queda archivado como insumo v2 (ver `ENT_RESEARCH_FABERLOOM_KIMI_2026-04`).

**Primer agente autónomo objetivo: SKILL_RW_REVIEW_TRIAGE del tenant MWT.** Por volumen real (Rana Walk Amazon FBA), bajo riesgo, métricas claras, y entrenamiento del patrón sobre data operacional concreta. Una vez validado en MWT, el patrón se documenta como template para nuevos tenants.

**Por qué scope FB y no MWT:** este builder NO es interno a MWT. Es la plataforma FaberLoom — producto SaaS para fabricantes y operaciones B2B/B2C — usando MWT como primer caso de uso real para validar arquitectura, gobernanza y graduación de autonomía. MWT consume FaberLoom; no es FaberLoom.

---

## Decisiones consolidadas (no se vuelven a discutir)

Cambiar cualquiera requiere bump major + aprobación CEO explícita. Cada decisión asume contexto FaberLoom platform.

### D1 — FB v1 single-tenant beta (MWT primer tenant)

FB v1 sirve a un único tenant: MWT/Rana Walk. No multi-tenant cripto, no A2A bridge entre tenants, no profile system multi-org, no capability marketplace, no anti-distillation patterns. Esos componentes se diseñan para FB v2 cuando aparezca segundo prospect concreto con LOI.

**Razón:** YAGNI. La complejidad multi-tenant antes de tener segundo tenant es deuda gratuita. Validar arquitectura con un tenant real (MWT) > teorizar con cero tenants. La separación lógica multi-tenant SÍ existe desde v1 vía D17 (config en data), pero sin la infra cripto que requiere v2.

### D2 — Hosting Hostinger KVM 8 (donde corre MWT)

12 containers existentes del tenant MWT + 3 nuevos compartidos por la plataforma FB (Dockge, Langfuse, LiteLLM) ⇒ 15 containers totales. Headroom RAM 22 GB → 18 GB tras adición. Sin migración de hosting en v1.

**Razón:** la infra del tenant MWT alcanza para FB v1 beta. Migrar a cloud multi-AZ antes de tener segundo tenant es overengineering. Cuando aparezca tenant 2, se evalúa migración con datos reales de costo y latencia.

### D3 — Containers nuevos a sumar (compartidos por la plataforma FB)

- **Dockge** (catálogo Hostinger, one-click) — UI gestión Docker Compose para todos los containers FB
- **LiteLLM** (catálogo Hostinger, one-click) — gateway 100+ LLMs en formato OpenAI, callback Langfuse nativo, multi-tenant ready vía API keys per-tenant
- **Langfuse** (manual, no en catálogo) — observabilidad de agentes FB, ClickHouse-backed, MIT, multi-tenant nativo (project per tenant)

No se suma en v1: Letta, Mem0, OPA, Cedar, Phoenix, Helicone, pg-boss, ARQ, Inngest, Prometheus, Grafana, Kong, Authentik. Ninguno aporta a FB v1 con un solo tenant beta; todos diferidos.

**Razón:** valor marginal nulo a volumen del primer tenant (MWT, ~200 invocaciones/día). Cada container añadido es deuda operacional para una plataforma que aún no tiene clientes pagantes.

### D4 — Memory simple tenant-aware

pgvector existente + tabla `episodic_memory` nueva en Postgres con clave compuesta `(tenant_id, skill_id, session_id)` desde día 1, aunque tenant_id sea constante en v1 ('mwt'). Three-layer architecture conceptual (índice + topics + transcripts) sin Letta/Mem0 framework standalone.

**Razón:** el contexto rot a volumen del primer tenant no justifica framework standalone. Mem0 reduce 90% tokens vs full-context — beneficio emerge a >5k invocaciones/día. La clave compuesta tenant_id desde v1 evita migración traumática cuando aparezca tenant 2.

### D5 — Manifest schema v2 extiende SKILL.md

No se inventa schema desde cero. Frontmatter base SKILL.md (estándar abierto, 26+ plataformas: Claude Skills, Hermes, Cursor, Cline, OpenCode, agentskills.io) + extensión namespaceada `metadata.mwt.*`. Hermes y Atmos hicieron el mismo patrón de extensión. Ver `SCH_FB_SKILL_MANIFEST_v2.md`.

**Razón:** portabilidad + compatibilidad ecosistema. Inventar schema propio es trabajo perdido.

**Deuda técnica conocida:** el namespace `metadata.mwt.*` quedó así porque la sesión original conceptualizó el builder como MWT-internal. El namespace correcto a futuro es `metadata.fbl.*` (FaberLoom). Migración del namespace queda como deuda — backward compat se mantiene con alias `mwt -> fbl` en el compiler hasta que todos los manifests del tenant MWT migren.

### D6 — Policy enforcement vía hooks Python en Django

3 hooks middleware en el runtime FB: `pre_tool_call` (P9 gate), `post_tool_call` (P5 episodic logger), `pre_llm_call` (P14 deterministic-first). No OPA/Cedar en v1.

**Razón:** las 6 reglas inquebrantables (P0-P14 + P15) se expresan en ~200 líneas de Python por hook. Engine declarativo (OPA/Cedar) se justifica cuando haya ≥5 SKILLs con reglas cross-domain en producción + ≥2 tenants con políticas distintas.

### D7 — Observability: Langfuse self-hosted + LiteLLM callback

Stack mínimo viable. Langfuse captura traces, costs, sessions, tool calls, evals. LiteLLM emite logs automáticos a Langfuse con tenant_id como project. No Phoenix/Braintrust/Helicone en v1.

**Razón:** Langfuse cubre tracing + eval básico + multi-tenant nativo (project per tenant) gratis (MIT, self-hosted). Stack secundario aumenta complejidad sin valor proporcional en v1.

### D8 — Modelo: Claude Sonnet 4.6 vía LiteLLM

Modelo único confirmado para v1. LiteLLM permite añadir Haiku 4.5 (model routing 40-60% ahorro) cuando el primer agente esté en producción y tenga datos reales de cost/quality trade-off.

**Razón:** un modelo simplifica autonomy graduation (no introducir variables múltiples antes de evidencia). Cuando entre tenant 2, model routing per-tenant (data residency, cost tier) se decide caso por caso.

### D9 — Tools como sub-procesos / módulos Python

MCP servers para integraciones externas (SP-API, ERPs, etc.) NO son containers separados. Viven como módulos Python invocados desde el runtime FB, o sub-procesos vía stdio. Cuando un tool justifique aislamiento (alta concurrencia, lenguaje no-Python, sandbox de seguridad), se contenedoriza.

**Razón:** overhead operacional minimizado. Container por tool = 30+ containers a 30 SKILLs distribuidos entre tenants.

### D10 — Techo de autonomía nivel 3-4 bounded

No nivel 5 abierto. No nivel 6 supervisor con sub-agents en runtime. Bounded autonomy con `max_iterations` + `budget_cap_usd` + `stop_on_consecutive_failures`. P3 draft-first absoluto, P4 autonomía por evidencia.

**Razón:** P3 + P4 son inquebrantables. Nivel 5+ sin caso de negocio explícito = riesgo material para clientes B2B regulados (target FaberLoom). El techo se mueve solo con evidencia operacional acumulada per-tenant.

### D11 — Flujos como DAG declarativo en YAML (no UI visual v1)

Archetype `workflow`, `routine` y `supervisor` declaran su plan en `metadata.mwt.flow` (o futuro `metadata.fbl.flow`) siguiendo `SCH_FLOW_DAG`. Plan = grafo dirigido acíclico de nodos (skill_call, branch, parallel, terminal, notify, human_gate, config_resolver) con edges determinísticos o condicionales.

**Razón:** plan declarativo permite validación build-time (ciclos, branches sin default, terminales alcanzables), replay determinístico, debugging post-mortem trazable. UI visual viene cuando lo justifique scale (FB v2 con ≥3 tenants y ≥10 flows en producción simultánea).

**No se permiten:** loops nativos en flow (usar archetype: autonomous), nested flows (cada flow es atómico), Jinja2 completo en expressions (KISS).

### D12 — Tareas como entidad de primera clase (Postgres + endpoints)

Tabla `tasks` separada de `episodic_memory` con tenant_id desde día 1. Cada invocación (ad-hoc desde dashboard, scheduled cron, webhook, flow_node) crea una task con state machine propia (queued → running → awaiting_approval → completed/failed/cancelled/timeout). Ver `SCH_TASK_ENTITY`.

**Razón:** sin tasks como entidad, no hay HITL granular, no hay invocación ad-hoc desde UI per tenant, no hay trazabilidad de flow nodes, no hay billing/cost tracking per-tenant. La distinción task / run / skill es operacional para FB SaaS, no académica.

### D13 — Template Factory y Agent Builder = mismo módulo en FB v1

Templates son manifests v2 con `is_template: true` y `placeholders` declarados. Builder en modo Fork lee template, pregunta placeholders al admin del tenant, genera instancia. Mismo schema, mismo compiler, mismo runtime. Separación de UI/governance Template-Factory-vs-Agent-Builder solo en FB v2 cuando haya múltiples tenants productivos consumiendo templates.

**Razón:** en FB v1 con un solo tenant beta (MWT), el CEO de MWT es curador y consumidor. Forzar separación es complejidad sin valor. Schema base soporta separación cuando v2 lo requiera sin breaking change.

### D14 — Outputs plural por agente (no un output_schema singular)

`contract.outputs[]` lista tipada. Cada output declara `id` + `schema` + `kind` (asset/decision/learning/side_effect) + `destination` + `required` + `condition` opcional. Reemplaza `output_schema` singular de v1.0.

**Razón:** la realidad operacional muestra que un agente emite múltiples artefactos: un draft + un tag de decisión + un side effect. Modelarlo como singular fuerza acoplamiento artificial. HITL granular por output exige el modelo plural.

### D15 — Golden samples obligatorios para outputs kind:asset

Validación 17 de `SCH_SKILL_MANIFEST_v2`: archetype `workflow`, `routine`, `autonomous` deben declarar al menos 1 golden sample por output `kind: asset`. Sample sirve como few-shot inyectado al LLM, reference de calidad para review humano, y regression test fixture post-graduación.

**Razón:** sin norte de calidad declarativo, evaluation es subjetiva y no escalable. Golden sample operacionaliza "este es el output ideal" — patrón observado en `SKILL_PROFORMA_BUILDER` del primer tenant ("Gold Sample Shortcut") y en demos Workspace Agents. Estándar para todos los SKILLs en FB v1.

### D16 — Conector dumb pipe + Agent smart router

El conector (n8n, webhook nativo, MCP server) hace solo detect + extract + dispatch. La lógica de dominio (clasificación, decisión, transformación de negocio) vive 100% en el agent vía manifest declarativo. Cualquier excepción (filtro spam pre-agent, rate limiting) debe declararse explícita en el manifest del agent como `triggers[].pre_dispatch_filters` con `max_logic_complexity: trivial`.

Reglas operacionales para el primer tenant (MWT) y aplicables a todos los tenants futuros:
- n8n workflows ≤ 5 nodes por trigger (si pasa, hay lógica que debería estar en el agent)
- n8n nunca toca LLM (sin nodes OpenAI/Claude/etc.)
- n8n no decide branches de negocio (switch nodes solo para tipos de evento, no lógica)
- Manifest declara `triggers[].connector_workflow_id` versionado

**Razón:** sin esta separación la lógica se reparte entre n8n + agent, perdiendo versionado git, replay determinístico y audit trail completo. Cambiar el agent obligaría a editar n8n también — acoplamiento oculto. Patrón validado en demos OpenAI Workspace Agents (Slack como dumb channel, agent como smart router) y en Hermes Agent (gateway dumb + agent smart).

### D17 — Procesos embebidos, configuración en data (BASE DEL MULTI-TENANT FB)

El proceso de negocio vive embebido en el manifest del agent **una sola vez**. Las variaciones por tenant, idioma, marketplace, canal o cliente del tenant se resuelven cargando config desde data (KB del tenant, tabla `tenant_profiles`, tabla `clients_profiles`), nunca creando agents o flows duplicados. Si una variación NO se puede expresar como config (cambio fundamental de lógica), entonces es un proceso distinto y merece un agent distinto.

Implementado vía:
- `metadata.mwt.multi_client_mode: true` flag (renombrar a `multi_tenant_mode` cuando entre tenant 2)
- `metadata.mwt.client_resolver` con `resolve_strategy`
- `flow.nodes[].kind: config_resolver` (carga `tenant_profile` + `client_profile` al context al inicio)
- Skills downstream consumen `flow.context.tenant_profile` + `flow.context.client_profile` como parámetros

Regla: distinto proceso = distinto agent. Mismo proceso, distinto cliente del tenant = mismo agent + config. Mismo proceso, distinto tenant = mismo agent + tenant_profile.

**Razón:** D17 ES la base del multi-tenant en FB v1. Sin D17, la tentación es crear flow custom por tenant o por cliente B2B (Marluvas, Tecmater del tenant MWT, etc.). A los 5 clientes del primer tenant la operación ya es ingobernable. Con D17, agregar nuevo cliente B2B = entry en `ENT_COMERCIAL_CLIENTES` del tenant + voice_profile si necesita uno. Cero cambio al agent. Cero cambio a n8n. Y cuando entre tenant 2, agregar tenant = entry en `tenant_profiles` + KB nueva. Cero cambio al agent.

### D18 — Type formal: skill_package vs agent

El field `metadata.mwt.type` distingue:
- `skill_package`: capacidad atómica reutilizable, importable por agents + invocable standalone vía CLI
- `agent`: composición que importa skills + tools + channels + outcome metric

Validaciones diferenciadas (ver `SCH_SKILL_MANIFEST_v2` sección "Validaciones diferenciadas por type"). Skills no tienen `tools_mcp`, `channels`, `triggers` ni `outcome` obligatorio. Agents sí.

**Razón:** sin la distinción, "voz CEO del tenant" se duplicaría en cada agent que escribe correos. Con la distinción, `SKILL_HUMANIZE_COMMS` es skill_package importado por N agents — single source of truth. Confirma observación CEO sobre la voz como skill, no como agent dedicado. Aplica per-tenant: cada tenant define su propio `SKILL_HUMANIZE_COMMS_<tenant>`.

### D19 — Architectural archetype obligatorio

El field `metadata.mwt.architectural_archetype` declara qué tipo de problema resuelve el agent: Generator | Triage | Validator | Orchestrator | Swarm | Reactive | Skill_package. Distinto del `archetype` (que indica cómo ejecuta).

Cada arquetipo suma 2-3 validaciones específicas al compiler. Ver `ENT_AGENT_ARCHETYPES_v1` para definiciones, casos y validaciones por arquetipo.

**Razón:** los 10 SHADOW del primer tenant (MWT) y los 5 demos OpenAI mostraron que NO hay un patrón único. Hay 6 arquetipos distintos con requisitos arquitectónicos distintos + 1 meta-arquetipo (skill_package). Forzar uno solo lleva a manifests sobre-cargados o validaciones laxas. Forzar declaración del arquetipo permite validación específica + budget heurístico + bootstrap guiado.

---

## Fases de implementación (12 semanas — primer tenant MWT)

### Fase 0 — Foundation (semana 1-2)

Objetivos: tener tracing y memoria episódica antes de tocar agentes.

| # | Entregable | Tiempo | Dependencia |
|---|------------|--------|-------------|
| 0.1 | Dockge instalado vía catálogo Hostinger | 10 min | ninguna |
| 0.2 | Langfuse + ClickHouse manual + Nginx vhost + SSL | 1-2 días | clickhouse separado |
| 0.3 | LiteLLM instalado vía catálogo + callback Langfuse + Anthropic key configurada | 30 min | 0.2 |
| 0.4 | Schema `episodic_memory` en Postgres con tenant_id desde día 1 + migración Django | 1 día | ninguna |
| 0.5 | 3 hooks middleware Django (pre_tool_call, post_tool_call, pre_llm_call) | 2-3 días | 0.4 |
| 0.6 | Test e2e con tenant MWT: invocación dummy → tool call → log Langfuse + episodic | 1 día | 0.1-0.5 |

**Entregable Fase 0:** infraestructura de tracing y memoria activa para FB platform, primer tenant MWT configurado, sin agentes todavía.

### Fase 1 — Manifest schema v2 (semana 3-4)

Objetivos: definir contrato canónico FB y migrar 1 SKILL real del tenant MWT como template canónico.

| # | Entregable | Tiempo |
|---|------------|--------|
| 1.1 | Lectura SKILL_RW_REVIEW_TRIAGE actual (tenant MWT) + ARCH_AGENT_PRINCIPLES + SKILL_RUNTIME | 1 día |
| 1.2 | Manifest schema v2 documentado (SKILL.md base + `metadata.mwt.*`, alias futuro `fbl.*`) | 2-3 días |
| 1.3 | Validador Python del schema (CLI + import en builder FB) | 2 días |
| 1.4 | Data operacional del primer tenant: volumen reviews/mes Rana Walk + status quo + outcome metric primaria | tu turno |
| 1.5 | Migración SKILL_RW_REVIEW_TRIAGE al manifest v2 con outcome real del tenant MWT | 2-3 días |
| 1.6 | Manifest commit + changelog + MANIFIESTO_APPEND | 30 min |

**Entregable Fase 1:** 1 manifest v2 del primer tenant listo, schema canónico para el resto de los SKILLs MWT y futuros tenants.

### Fase 2 — Runtime para 1 agente (semana 5-6)

Objetivos: hacer que el manifest v2 se ejecute realmente sobre datos reales del primer tenant.

| # | Entregable | Tiempo |
|---|------------|--------|
| 2.1 | Compiler Python: manifest YAML → ejecutor con hooks atados | 3-4 días |
| 2.2 | MCP wrapper para SP-API reviews endpoint (módulo Python o sub-proceso) | 2-3 días |
| 2.3 | n8n trigger del tenant MWT: webhook Amazon notifications → endpoint Django builder FB | 1 día |
| 2.4 | State machine implementada (mínimo 5 estados con transiciones) | 2 días |
| 2.5 | Smoke test: 1 review real del tenant MWT entra → agente la procesa SHADOW → log Langfuse + episodic | 1 día |

**Entregable Fase 2:** agente del primer tenant corre en SHADOW con data real.

### Fase 2.6 — Flujos y Tareas (semana 6, ~1 semana)

Objetivos: agregar las primitivas de flow y task antes de SHADOW para que REVIEW_TRIAGE corra como workflow real, no como SKILL atómico.

| # | Entregable | Tiempo |
|---|------------|--------|
| 2.6.1 | Schema tabla `tasks` Postgres con tenant_id + migración Django | 1 día |
| 2.6.2 | Endpoints Django `/api/tasks/*` (POST, GET queue, GET id, approve, reject, cancel) — multi-tenant aware | 2 días |
| 2.6.3 | Worker Celery `execute_agent_task` que invoca skill_executor o flow_executor según archetype | 1-2 días |
| 2.6.4 | Flow executor (`agents/flow_executor.py`) — interpreta `metadata.mwt.flow` y ejecuta nodes | 2-3 días |
| 2.6.5 | Dashboard del tenant MWT (`portal.<tenant>.fbl/agents/tasks` ó equivalente) con cola, pendientes review, flow viewer | 2-3 días |
| 2.6.6 | Conectar `TPL_REVIEW_TRIAGE` como flow declarativo (no SKILL atómico) | 1 día |

**Entregable Fase 2.6:** REVIEW_TRIAGE corriendo como workflow del primer tenant con flow DAG, tasks individuales por nodo, HITL granular por output. Dashboard funcional para admin del tenant MWT.

### Fase 3 — SHADOW 30 días (semana 7-10)

Objetivos: acumular evidencia real para autonomy graduation del primer agente del primer tenant.

| # | Entregable | Cadencia |
|---|------------|----------|
| 3.1 | Run en SHADOW × 30 días sobre data del tenant MWT | calendario |
| 3.2 | Dashboard Langfuse: acceptance, schema compliance, cost, latency, outcome trending | configurar día 1 |
| 3.3 | Revisión semanal del admin tenant: drafts marcados accept/edit/reject | 30 min/semana |
| 3.4 | Episodic memory acumula evidencia para promoción | automático |

**Entregable Fase 3:** dataset real del primer tenant para decidir graduación según `POL_OUTCOME_ACCOUNTABILITY`.

### Fase 4 — Graduación a nivel 3 (semana 11-12)

Objetivos: agente vivo en producción supervisada (P3 draft-first activo).

| # | Entregable | Tiempo |
|---|------------|--------|
| 4.1 | Reporte de evidencia vs thresholds (ver `POL_OUTCOME_ACCOUNTABILITY`) | 1 día |
| 4.2 | Si pasa: SHADOW → ACTIVE nivel 3, outputs van a producción del tenant MWT con admin approval | 1 día |
| 4.3 | Si NO pasa: identificar gap, ajustar manifest, otro ciclo SHADOW 30 días | bucle |
| 4.4 | Documentar autonomy graduation en SKILL_RUNTIME del tenant + changelog | 1 día |

**Entregable Fase 4:** primer agente autónomo bounded en producción real del primer tenant FB. Patrón documentado como template para nuevos tenants y para agentes adicionales del tenant MWT.

---

## Lo que se difiere explícitamente a FB v2 o más adelante

| Componente | Cuándo entra |
|------------|--------------|
| Letta / Mem0 (memory framework standalone) | cuando ≥3 SKILLs autónomos compitan por memoria en cualquier tenant |
| OPA / Cedar (policy engine declarativo) | cuando hooks Python escalen mal (≥5 agentes con reglas cross-domain o ≥2 tenants con políticas distintas) |
| KAIROS / NIGHTLY_REFLECTION (capa 3 aprendizaje) | cuando episodic memory de 60-90 días tenga señal estadística |
| ULTRAPLAN (planning largo desacoplado) | cuando un caso B2B grande de cualquier tenant lo justifique |
| Three-layer memory completo (índice + topics + transcripts) | cuando contexto se sature con KB grande del tenant |
| Routines (cron + webhook como archetype dedicado) | después del primer SKILL graduado, replicando patrón |
| Coordinator/Supervisor formal | después del 2do SKILL graduado |
| Knowledge graph dual-level (LightRAG style) | cuando pgvector flat genere precisión < 80% en algún tenant |
| **Multi-tenant cripto (isolation, A2A bridge, profile system, capability marketplace)** | **FB v2 con segundo tenant LOI/pagante** |
| UI visual del agent builder (drag-drop) | FB v2 con ≥3 tenants productivos |
| Marketplace de templates entre tenants | FB v2 |

---

## Lo que NO se hace nunca

| Anti-pattern | Por qué no |
|--------------|------------|
| Computer Use / Manus full delegation | rompe P3 draft-first absoluto |
| Auto-prompt-update sin firma humana (capa 4 aprendizaje) | rompe P5, opacidad, no auditable |
| Multi-tenant cripto / A2A / profile system en FB v1 | un solo tenant beta (MWT), complejidad inútil hasta tenant 2 |
| Self-host LLM | break-even >10M tokens/día, lejísimos de escala FB v1 con un solo tenant |
| Forkear hermes-agent / claude-mem (AGPL) | deuda técnica + riesgo legal |
| Inventar manifest schema desde cero | SKILL.md ya es standard, solo extender |
| Adoptar el código del Claude Code leak | riesgo IP/legal, conceptos sí, código no |
| Loops nativos dentro de flow DAG | romper grafo acíclico; usar archetype autonomous con max_iterations |
| Output singular en agentes nuevos (post v1.1) | un agente emite múltiples artefactos típicamente; outputs[] plural obligatorio |
| Templates sin placeholders ni golden samples | template sin placeholders es manifest plano (no template); template sin gold samples no compila si tiene archetype workflow/autonomous/routine |
| Crear flow custom por cliente B2B del tenant en lugar de usar D17 | viola D17, ingobernable a 5+ clientes |

---

## Sistema de métricas activo desde día 1

Sin esperar research adicional, las métricas que se trackean en Fase 0 (per-tenant desde día 1, aunque el tenant inicial sea uno):

| Nivel | Métricas | Origen |
|-------|----------|--------|
| L0 Activity | runs/día, tokens/run, cost/run | Langfuse + LiteLLM |
| L1 Execution | tool_success_rate, latency p50/p95, error_rate | Langfuse |
| L2 Compliance | schema_compliance_rate, policy_pass_rate | hooks Django |
| L3 Acceptance | human_accepted, edit_light, rejected | dashboard custom del admin tenant |
| L4 Decision Closure | decisions_closed_per_run, branches_taken | episodic_memory |
| L5 Outcome | métrica primaria del tenant (TTR, AHR, etc.) | manifest declarado |

L5 es la única métrica que justifica seguir gastando tokens. Las demás son higiene operacional. Ver `POL_OUTCOME_ACCOUNTABILITY` para la regla.

---

## Pre-requisitos para arrancar Fase 0

Solo dos cosas:

1. **Datos operacionales del primer tenant (MWT):**
   - Volumen reviews/mes Rana Walk Amazon (aprox)
   - Status quo: quién maneja hoy, time-to-response típico
   - Outcome metric primaria (AHR / recovery rating / repeat purchase / case log / conversion / otro)

2. **Lectura de la KB del tenant MWT**: `SKILL_RW_REVIEW_TRIAGE` actual + `ARCH_AGENT_PRINCIPLES` literal + `SPEC_ACTION_ENGINE` + `SPEC_MWT_AGENT_PLATFORM` + `SKILL_RUNTIME`. La KB del tenant funciona como ground truth operacional para el primer agente FB.

Sin estos dos no se construye la fundación con base sólida — quedaría sobre supuestos.

---

## Trigger de aborto/pivot

El plan se aborta o pivota si:

- Fase 0 no termina en 3 semanas (estimación 1-2 sem) — algo está mal en infra
- Fase 1 no termina manifest v2 + 1 SKILL migrado en 4 semanas (estimación 2 sem) — schema demasiado ambicioso
- Fase 3 SHADOW genera < 30% acceptance rate — el agente no funciona, replantear desde cero
- Costo Fase 0-2 > $200 sin entregables productivos — overruns no justifican continuar
- Outcome metric primaria del primer tenant no se mueve después de 90 días → SKILL vuelve a SHADOW (`POL_OUTCOME_ACCOUNTABILITY`)
- Aparece prospect/LOI segundo tenant antes de Fase 4: pausar Fase 4, replantear arquitectura para multi-tenant cripto (FB v2)

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29): creación con scope MWT-only erróneo. 10 decisiones consolidadas, 4 fases, lo diferido, lo que NO se hace, sistema métricas L0-L5, pre-requisitos, triggers aborto. Sesión Cowork derivada del cruce Mitjana + research externo + inventario MWT real.
- v1.1 (2026-04-29b): agregadas 5 decisiones nuevas (D11 flujos DAG declarativos, D12 tareas como entidad de primera clase, D13 templates=builder mismo módulo, D14 outputs plural, D15 golden samples obligatorios). Nueva Fase 2.6 (Flujos y Tareas) entre Runtime y SHADOW. 3 anti-patterns adicionales. Aún con scope MWT-only.
- v1.2 (2026-04-29c): agregadas 4 decisiones nuevas (D16 conector dumb / agent smart, D17 procesos embebidos config en data, D18 type skill_package vs agent, D19 architectural_archetype obligatorio). Aún con scope MWT-only.
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado SPEC_AGENT_BUILDER_MWT_V1 → SPEC_FB_AGENT_BUILDER_v1. Toda la sesión del 29-abr fue conceptualizada para FB pero etiquetada como MWT por error. MWT pasa de "el proyecto" a "primer tenant beta de FB". Las 19 decisiones D1-D19 se reformulan con FB como sujeto y MWT como objeto (primer tenant). Multi-tenant cripto/A2A/profile system → diferido a FB v2 con segundo tenant. Namespace `metadata.mwt.*` se conserva como deuda técnica con alias futuro a `metadata.fbl.*`. Aprobador: CEO sesión re-scoping 2026-04-29f.**
- v2.0.1 (2026-06-23, FB-STD-CODEX-2026-06-23-01): fix mecánico de refs legacy sin prefijo `FB_` hacia nombres canon en `docs/faberloom/`.
