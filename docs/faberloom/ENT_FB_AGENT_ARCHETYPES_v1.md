# ENT_FB_AGENT_ARCHETYPES_v1 — Arquetipos Arquitectónicos de Agentes FaberLoom
id: ENT_FB_AGENT_ARCHETYPES_v1
version: 2.0.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE — 2026-04-29f (re-scope FB)
aprobador: CEO (sesión Cowork 2026-04-29c + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SCH_FB_SKILL_MANIFEST_v2.md · SPEC_FB_AGENT_BUILDER_v1.md · ENT_FB_TEMPLATE_LIBRARY_v1.md · SCH_FB_FLOW_DAG.md

---

## Declaración

Este documento formaliza **6 arquetipos arquitectónicos** de agentes en la plataforma FaberLoom + 1 meta-arquetipo (skill_package). Cada arquetipo define un patrón distinto de problema-solución con sus propias validaciones, budget heurístico, outcome metric típico y arquitectura recomendada.

**El field `architectural_archetype` del `SCH_FB_SKILL_MANIFEST_v2` es obligatorio** y debe declarar uno de estos siete valores. Distinto del field `archetype` (que indica CÓMO ejecuta — skill/workflow/supervisor/etc.), el architectural_archetype indica QUÉ TIPO DE PROBLEMA resuelve.

**Origen del modelo**: emergió del cruce de los 10 SKILLs SHADOW del primer tenant FB (MWT/Rana Walk) con los 4 demos públicos OpenAI Workspace Agents (Spark/Trove/Tally/Scout) + Software Review demo, durante sesión Cowork 2026-04-29c. Los 7 arquetipos son universales para cualquier tenant futuro de la plataforma — los ejemplos en tablas referencian al tenant MWT como primer caso real validado.

---

## Tabla de los 7 arquetipos

| # | Arquetipo | Qué hace | Archetype manifest típico | Outcome metric típica |
|---|-----------|----------|---------------------------|------------------------|
| 0 | **Skill_package** | capacidad atómica reutilizable, importable + standalone (NO es agent) | skill | acceptance rate cuando se usa standalone |
| 1 | **Generator** | escribe contenido (drafts, copy, reportes) | skill | acceptance rate post-CEO review |
| 2 | **Triage** | clasifica entrada y ramifica camino | routine + workflow | branch accuracy + TTR |
| 3 | **Validator** | chequea contra policies, decide pass/fail | skill (P14-heavy) | drift detection rate |
| 4 | **Orchestrator** | ejecuta proceso multi-step con side effects | workflow + state machine extensa | completion rate sin intervención manual |
| 5 | **Swarm** | descompone problema, ejecuta sub-agents, agrega | supervisor | accuracy del reporte agregado |
| 6 | **Reactive** | event-driven (cron/webhook), sin invocación humana directa | routine | response rate + signal-to-noise |

---

## 0 · Skill_package — capacidad atómica reutilizable

### Definición

Paquete de comportamiento reutilizable que NO es un agent. Importable por agents vía `skills_imports[]`. Ejecutable standalone vía CLI con `mwt skill run <skill_id>`.

### Características

- Stateless funcional típicamente
- Sin tools_mcp propias
- Sin channels propios
- Sin triggers propios
- Tiene `default_prompt` para invocación standalone
- Single source of truth para una capacidad atómica

### Casos en MWT

| SKILL | Función | Importado por |
|-------|---------|---------------|
| SKILL_HUMANIZE_BRAND | voz Rana Walk + voz Marluvas/Tecmater | agents que escriben copy externo |
| SKILL_HUMANIZE_COMMS | voz CEO en correos/mensajes | review_triage, lead_qualifier, proforma_builder |
| (futuro) SKILL_DOMAIN_CLASSIFIER | clasifica intent en mensajes B2B | varios |

### Cuándo se promueve a Agent

Cuando aparece UNA de:
- Memoria episódica per destinatario/cliente
- Outcome metric propio que valga medir
- Tools dedicados (Gmail, contactos)
- Schedule/routine triggerable
- Sub-agents que orquesta

Hasta entonces: skill_package.

### Validaciones obligatorias

- `skill_package_metadata.default_prompt` no vacío
- NO declarar `tools_mcp[]`, `channels`, `triggers[]`
- `outcome.primary` opcional (skills pueden no tener)
- `multi_client_mode` no aplica

### Budget heurístico

$5-15/mes a 200 invocaciones/día (mayoría reusa el agent, sin costo adicional).

---

## 1 · Generator — escribe contenido

### Definición

Toma input + contexto + voz/estilo, genera contenido nuevo (texto, HTML, JSON estructurado).

### Características

- Single LLM call típicamente (a veces N para variantes)
- Schema-locked output
- Outputs: 1 asset principal + 1 decision opcional (rama/categoría)
- requires_human_approval: true en outputs externos
- Memory: golden_samples como reference + episodic para acceptance rate

### Casos en MWT

| SKILL futuro | Función | Importa |
|--------------|---------|---------|
| SKILL_RW_LISTING_OPT | optimiza listings Amazon | brand_voice, claims_scanner |
| SKILL_PROFORMA_BUILDER | genera HTML proforma | brand_voice |
| SKILL_COPY | drafts de copy | brand_voice, claims_scanner |
| SKILL_RW_REVIEW_RESPONSE | drafts respuesta a review | humanize_comms, brand_voice |

### Caso demo OpenAI

- Spark (lead outreach) — escribe outreach emails personalizados

### Validaciones específicas

- `golden_samples[]` ≥ 1 por output `kind: asset`
- `output.requires_human_approval: true` para outputs con destino externo
- `architectural_archetype: generator`

### Budget heurístico

$20-30/mes a 200 invocaciones/día. Tokens 3-8k/run, latencia 5-30s.

### Outcome metric típica

Acceptance rate post-CEO review (% drafts que CEO acepta sin edit, % con edit_light, % rechaza).

---

## 2 · Triage — clasifica y ramifica

### Definición

Recibe entrada (email, ticket, review), clasifica intent/severidad, ramifica camino según clasificación, emite múltiples outputs (decision + asset condicional + side_effect condicional).

### Características

- Multi-output típico: 1 decision (severidad/categoría) + 1-2 assets condicionales (drafts) + side_effects (tickets, escalations)
- Flow DAG con branches obligatorios
- archetype: routine + workflow (recibe trigger + tiene plan)
- HITL granular por output

### Casos en MWT

| SKILL/TPL | Función |
|-----------|---------|
| SKILL_RW_REVIEW_TRIAGE | triage de reviews Amazon FBA |
| TPL_LEAD_QUALIFIER_B2B | califica leads B2B entrantes Gmail |
| SKILL_CLIENT_SERVICE | router multi-idioma B2B |

### Caso demo OpenAI

- Scout (product feedback monitor) — Slack threads → clasifica → escala a Linear

### Validaciones específicas

- `flow.branches[]` con clausula `default:` exhaustiva
- `triggers[]` ≥ 1 declarado
- `outputs[]` ≥ 2 (una decision + al menos un asset o side_effect)
- `architectural_archetype: triage`

### Budget heurístico

$15-25/mes a 200 invocaciones/día. Tokens 5-15k/run, latencia 10-40s.

### Outcome metric típica

Branch accuracy (% clasificaciones correctas) + TTR (time to response/triage).

---

## 3 · Validator — chequea policies

### Definición

Aplica policies/reglas a un input y decide pass/fail/escalado. Deterministic-first heavy (P14): regex/parsers/lookups antes de invocar LLM.

### Características

- archetype: skill (atómico)
- Tokens 1-5k/run (mayoría deterministic)
- Output: 1 decision principal + reporte detallado (asset informativo)
- Auto-flow si pass, escalado a humano si fail
- Memory: policy refs

### Casos en MWT

| SKILL | Función |
|-------|---------|
| SKILL_COMPLIANCE_CHECKER | valida claims, brand voice, market rules |
| SKILL_KB_AUDITOR | audit diario KB con V1-V9 checks |

### Validaciones específicas

- `policies[]` ≥ 1 declarado
- Sección `deterministic_first` declarada en flow
- `architectural_archetype: validator`

### Budget heurístico

$5-15/mes a 200 invocaciones/día. Tokens 1-5k/run, latencia 2-15s.

### Outcome metric típica

Drift detection rate (cuántos drift reales detecta vs falsos positivos vs falsos negativos).

---

## 4 · Orchestrator — proceso multi-step con side effects

### Definición

Ejecuta un proceso operativo de varios pasos con side effects significativos (writes a APIs externas). State machine extensa (7+ estados). Gates humanos por step crítico.

### Características

- archetype: workflow con state machine compleja
- Tools: 5-15 (es un proceso completo)
- Tokens 20-80k/run, latencia 1-10min
- HITL por step (no solo al final)
- Memory: account history, decision history

### Casos en MWT

| SKILL | Función |
|-------|---------|
| SKILL_AMAZON_OPS | ops cuenta Amazon (account health, inventory, cases) |
| SKILL_EXPERIMENT_RUNNER | A/B testing MYE con monitoring |

### Caso demo OpenAI

- Tally (weekly metrics) — pull data + compute + chart + draft + review

### Validaciones específicas

- `state_machine.states ≥ 7`
- side_effects con `requires_human_approval: true` por defecto
- `architectural_archetype: orchestrator`

### Budget heurístico

$50-150/mes a 50-100 invocaciones/día. Tokens 20-80k/run, latencia 1-10min.

### Outcome metric típica

Completion rate sin intervención manual (% ejecuciones que llegan a estado completed sin necesitar humano más allá del approval declarado).

---

## 5 · Swarm — descompone y agrega

### Definición

Descompone un problema complejo en sub-problemas, ejecuta sub-agents (paralelo o pipeline), agrega los resultados en un reporte final.

### Características

- archetype: supervisor con sub_agents declarados
- Tokens 50-200k/run (acumulado de sub-agents)
- Latencia 4-30min
- Memory: shared workspace entre sub-agents

### Casos en MWT

| SKILL | Función | Sub-agents |
|-------|---------|------------|
| SKILL_DEMAND_FORECASTER | forecast distribución B2B LATAM | 7 sub-agents (0A→A→B→C→D→E→F) |

### Caso demo OpenAI

- Trove (third-party risk manager) — research + criteria mapping + doc generation

### Validaciones específicas

- `inputs.depends_on_skills[]` ≥ 2
- Budget rollup declarado (cost del padre = suma cost sub-agents)
- `architectural_archetype: swarm`

### Budget heurístico

$80-200/mes a 5-20 invocaciones/día (alto costo por run, baja frecuencia).

### Outcome metric típica

Accuracy del reporte agregado (validado por humano experto en el dominio).

---

## 6 · Reactive — event-driven sin invocación humana

### Definición

Disparado por eventos externos (cron, webhook, signal de sistema). Sin invocación humana directa. Procesa, decide si notificar/escalar, persiste evidencia.

### Características

- archetype: routine
- Tokens 5-15k/run
- Latencia 5-60s
- Output típico: log + notify_if_relevant
- Memory: signal history

### Casos en MWT

| SKILL | Función | Trigger |
|-------|---------|---------|
| SKILL_KB_AUDITOR | audit diario KB | cron 06:00 CR |
| (futuro) SKILL_INVENTORY_LOW_ALERT | alerta inventario bajo Amazon | cron 12h |
| (futuro) SKILL_REVIEW_INCOMING | webhook reviews nuevos | Amazon notification |

### Caso demo OpenAI

- (similar al pattern de KAIROS del Claude Code leak — sesiones background autónomas con notify-if-relevant)

### Validaciones específicas

- `triggers[]` ≥ 1 (cron o webhook)
- `idempotency_key_field` declarado
- `architectural_archetype: reactive`

### Budget heurístico

$10-25/mes a 100-300 invocaciones/día (alta frecuencia, bajo costo por run).

### Outcome metric típica

Signal-to-noise ratio (% de runs que producen alertas accionables vs ruido) + response rate (cuando hay alerta, el humano responde a tiempo).

---

## Mapa completo: SHADOW MWT actual + demos OpenAI

| Caso | Arquetipo | Notas |
|------|-----------|-------|
| SKILL_HUMANIZE_BRAND | 0 · Skill_package | importable por todos los agents que escriben |
| SKILL_HUMANIZE_COMMS | 0 · Skill_package | voz CEO en correos |
| SKILL_COPY | 1 · Generator | drafts copy con validación claims |
| SKILL_PROFORMA_BUILDER | 1 · Generator | golden sample shortcut |
| SKILL_RW_LISTING_OPT (futuro) | 1 · Generator | listings Amazon |
| SKILL_RW_REVIEW_TRIAGE | 2 · Triage | foco Fase 1 builder |
| SKILL_CLIENT_SERVICE | 2 · Triage | router multi-idioma |
| TPL_LEAD_QUALIFIER_B2B | 2 · Triage | Gmail webhook |
| SKILL_COMPLIANCE_CHECKER | 3 · Validator | gate obligatorio |
| SKILL_KB_AUDITOR | 3 · Validator (con cron) | AUTO_NOTIFICA |
| SKILL_AMAZON_OPS | 4 · Orchestrator | state machine 7 estados |
| SKILL_EXPERIMENT_RUNNER | 4 · Orchestrator | gates por step |
| SKILL_DEMAND_FORECASTER | 5 · Swarm | 7 sub-agents secuenciales |
| (futuro) NIGHTLY_REFLECTION | 6 · Reactive | KAIROS-style |
| Spark (demo OpenAI) | 1+2 hybrid | research + classify + draft |
| Trove (demo OpenAI) | 5 · Swarm | research + reporte Doc |
| Tally (demo OpenAI) | 4 · Orchestrator | weekly metrics pipeline |
| Scout (demo OpenAI) | 2 · Triage | Slack feedback → Linear |
| software-review-evaluator (demo OpenAI) | 0 · Skill_package | evalúa requests vs alternativas |

---

## Implicaciones para el builder

### Bootstrap discusivo guiado por arquetipo

Cuando vos describís intención al CEO ("necesito un agent que clasifique tickets entrantes"):
1. El builder identifica patrón → propone `architectural_archetype: triage`
2. Sugiere TPL_TRIAGE_BASE como punto de partida
3. Aplica validaciones específicas del arquetipo
4. Sugiere budget default según arquetipo
5. Sugiere outcome metric típica del arquetipo

Esto reduce decisiones que el CEO tiene que tomar de cero.

### Templates indexados por arquetipo (futuro v2)

Cuando la Template Library crezca a 10+ templates, indexar por arquetipo:

```
TEMPLATES
├── 1 · Generator
│   ├── TPL_LISTING_OPTIMIZER
│   ├── TPL_PROFORMA_GENERATOR_B2B
│   └── TPL_REVIEW_RESPONSE
├── 2 · Triage
│   ├── TPL_REVIEW_TRIAGE
│   ├── TPL_LEAD_QUALIFIER_B2B
│   └── TPL_INBOX_TRIAGE
├── 3 · Validator
│   ├── TPL_COMPLIANCE_GATE
│   └── TPL_KB_AUDITOR
└── ...
```

UI del builder muestra cards agrupadas por arquetipo, con icon distintivo.

---

## No hay que formalizarlo todo en v1

Esta tabla es **guía conceptual**. El compiler usa el field `architectural_archetype` para sumar validaciones específicas (validaciones 28 del `SCH_FB_SKILL_MANIFEST_v2`). Pero NO hay que crear archivos separados por arquetipo en FB v1.

Cuando la plataforma FB tenga 10+ agents en producción (entre el tenant MWT y futuros tenants), vale revisar si los arquetipos se sostienen empíricamente o si hay drift hacia patrones nuevos. Si emergen 2-3 patrones nuevos, se documentan en v3 de este archivo.

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29c): creación con scope MWT-only erróneo. 6 arquetipos + 1 meta (skill_package). Cada uno con definición, características, casos del tenant MWT, validaciones específicas, budget heurístico, outcome metric típica. Mapa completo de SHADOW MWT + 5 demos OpenAI.
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado ENT_AGENT_ARCHETYPES_V1 → ENT_FB_AGENT_ARCHETYPES_v1. Los 7 arquetipos son universales para cualquier tenant FB; los ejemplos referencian al primer tenant MWT como caso real validado. Aprobador: CEO sesión re-scoping 2026-04-29f.**
- v2.0.1 (2026-06-23, FB-STD-CODEX-2026-06-23-01): fix mecánico de ref legacy `ENT_TEMPLATE_LIBRARY_v1.md` → `ENT_FB_TEMPLATE_LIBRARY_v1.md` en metadata relacionado.
