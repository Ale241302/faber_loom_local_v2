# SCH_FB_SKILL_MANIFEST_v2 — Schema Canónico Manifest Skill v2 FaberLoom
id: SCH_FB_SKILL_MANIFEST_v2
version: 2.0.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SCH
stamp: VIGENTE — 2026-04-29 (re-scopeado de MWT a FB)
aprobador: CEO (sesión Cowork 2026-04-29 + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SPEC_FB_AGENT_BUILDER_v1.md · ARCH_AGENT_PRINCIPLES.md · POL_FB_OUTCOME_ACCOUNTABILITY.md · ENT_FB_AGENT_ARCHETYPES_v1.md · SCH_FB_FLOW_DAG.md · SCH_FB_TASK_ENTITY.md · ENT_FB_TEMPLATE_LIBRARY_v1.md · ENT_FB_TOOL_CATALOG_v1.md

---

## Declaración

Este schema define el **manifest canónico v2 para todo SKILL en la plataforma FaberLoom**. Extiende el frontmatter SKILL.md (estándar abierto Anthropic, soportado por 26+ plataformas y agentskills.io) con extensión namespaceada `metadata.mwt.*` que captura los campos específicos requeridos por ARCH_AGENT_PRINCIPLES.

**Estrategia: extender, no inventar.** El frontmatter base mantiene compatibilidad con el ecosistema (Claude Skills, Hermes, Cursor, Cline, OpenCode). La extensión captura los principios fundacionales (P0-P15) como campos auditables.

**Deuda técnica conocida:** el namespace `metadata.mwt.*` quedó así porque la sesión original conceptualizó el schema como MWT-internal antes de re-scopearlo a FB. El namespace correcto a futuro es `metadata.fbl.*` (FaberLoom). Migración del namespace queda como deuda — backward compat se mantiene con alias `mwt -> fbl` en el compiler hasta que todos los manifests del primer tenant (MWT) migren.

**Migración obligatoria:** todos los SKILLs en SHADOW del primer tenant beta (MWT/Rana Walk) se migran a v2 progresivamente, empezando por SKILL_RW_REVIEW_TRIAGE (primer agente autónomo objetivo de FB v1). Hasta migración, los SKILLs legacy del tenant MWT siguen siendo válidos. Tenants futuros entran directamente con manifest v2.

---

## Por qué este schema existe

Los frontmatters actuales de los 10 SKILLs en SHADOW del primer tenant (MWT) son heterogéneos. Ninguno declara archetype formal, ningún tools_mcp explícito, ningún sub_agents formalizado (DEMAND_FORECASTER es swarm de facto sin declarar), ningún outcome metric, ningún kill switch, ningún learning_consolidation target. El estado del primer tenant es representativo del problema que la plataforma FB resuelve para tenants en general.

Sin schema canónico:
- Validación automática imposible
- Audit cross-SKILL no formalizable
- Patch broadcast (cambio en POL/ENT aguas arriba) no detecta dependencias
- Autonomy graduation sin criterios uniformes
- ARCH_AGENT_PRINCIPLES P0-P14 quedan declarativos no ejecutables

---

## Schema base SKILL.md (estándar Anthropic, no se toca)

```yaml
name: SKILL_RW_REVIEW_TRIAGE
description: |
  Skill que clasifica reviews entrantes de Amazon FBA Rana Walk y genera
  draft de respuesta según POL_BRAND_VOICE + POL_AMAZON_TOS.
version: 2.0.0
metadata:
  # extensiones libres, namespaceadas
  mwt:
    # ver sección "Extensión metadata.mwt.*" abajo
    ...
```

Campos `name`, `description`, `version` son obligatorios y siguen estándar agentskills.io.

---

## Extensión metadata.mwt.* (canónica MWT)

```yaml
metadata:
  mwt:
    # === Identidad y dominio ===
    id: SKILL_RW_REVIEW_TRIAGE              # canonical ID, formato SKILL_* o TPL_*
    type: agent                              # skill_package | agent (NUEVO v1.2)
    architectural_archetype: triage          # generator | triage | validator | orchestrator | swarm | reactive | skill_package (NUEVO v1.2 — ver ENT_AGENT_ARCHETYPES_V1)
    domain: PRODUCTO                         # IDX_DOMINIO al que pertenece
    archetype: routine                       # skill | workflow | reactive | autonomous | supervisor | routine (cómo ejecuta)
    visibility: INTERNAL                     # PUBLIC | PARTNER_B2B | INTERNAL | CEO_ONLY
    status: SHADOW                           # SHADOW | ACTIVE | DEPRECATED | ARCHIVED

    # === Inputs y dependencias KB ===
    inputs:
      kb_refs:                               # archivos de la KB requeridos
        - PLB_REVIEW_TRIAGE
        - ENT_RW_BRAND_VOICE
        - LOC_ES_MX
        - POL_BRAND_VOICE
        - POL_AMAZON_TOS
        - POL_CLAIMS_SCANNER
      data_sources:
        - SP-API/reviews
      depends_on_skills: []                  # otros SKILL_ invocados (sub-agents)

    # === Skills imports (NUEVO v1.2 — separado de tools_mcp) ===
    # Skills son paquetes de comportamiento reutilizables (type: skill_package).
    # Distintos de tools_mcp (que son capacidades externas tipo APIs).
    skills_imports:
      - skill_id: SKILL_HUMANIZE_COMMS
        version: ">=0.2"
        invocation_alias: humanize_comms     # cómo el agent lo referencia internamente
      - skill_id: SKILL_BRAND_VOICE_RW
        version: ">=0.3"
        invocation_alias: brand_voice

    # === Multi-cliente lógico (NUEVO v1.2 — D17) ===
    multi_client_mode: true                  # default false; true exige client_resolver
    client_resolver:
      kind: config_lookup                    # config_lookup | explicit_id | email_pattern
      source: ENT_COMERCIAL_CLIENTES         # KB ref o tabla
      key_field: client_id
      resolve_strategy: by_domain            # by_domain | by_explicit_id | by_email_pattern
      payload_extraction: payload.email.sender_domain
      fallback: prospect_unknown             # client_id por defecto si no matchea
      cache_ttl_min: 60

    # === Contract: outputs plural y policies ===
    contract:
      outputs:                               # lista tipada — un agente puede emitir varios artefactos
        - id: response_draft
          schema: SCH_REVIEW_RESPONSE
          kind: asset                        # asset | decision | learning | side_effect
          destination: drafts/queue
          required: true
          requires_human_approval: true      # P3 draft-first explícito por output
        - id: severity_tag
          schema: SCH_SEVERITY_DECISION
          kind: decision
          destination: episodic_memory
          required: true
        - id: escalation_ticket
          schema: SCH_ESCALATION_TICKET
          kind: side_effect
          destination: case_log/
          required: false
          condition: severity == "critical"  # solo si rama crítica
      policies:                              # POL_ obligatorios pre-ejecución
        - POL_BRAND_VOICE
        - POL_AMAZON_TOS
        - POL_CLAIMS_SCANNER
        - POL_DATA_CLASSIFICATION
      schema_lock: strict                    # strict | flexible (no se acepta flexible en archetype routine/autonomous)

    # === State machine (P7 obligatorio) ===
    state_machine:
      ref: SCH_STATE_MACHINE_REVIEW_TRIAGE   # estado y transiciones declaradas
      states_minimum: [drafting, awaiting_approval, approved, executing, completed, rejected, escalated]
      timeout_default_h: 24

    # === Golden samples (norte de calidad + few-shot + regression eval) ===
    golden_samples:
      - id: GS_REVIEW_RESPONSE_2026_03
        path: docs/faberloom/gold_samples/review_response_2026_03.md
        validates_outputs: [response_draft]  # qué outputs valida este sample
        evaluation_use: reference            # reference | regression_test | few_shot
        added_by: ceo
        added_at: 2026-03-15
        notes: "Caso 4-star queja tamaño, recovery rating post respuesta"
      - id: GS_REVIEW_ESCALATION_2026_02
        path: docs/faberloom/gold_samples/review_escalation_2026_02.md
        validates_outputs: [escalation_ticket]
        evaluation_use: regression_test
        added_by: ceo
        added_at: 2026-02-10

    # === Skill package metadata (cuando type: skill_package) — NUEVO v1.2 ===
    # Solo para type: skill_package. Skills son ejecutables standalone via CLI.
    skill_package_metadata:
      default_prompt: "Use $humanize_comms para redactar mensajes con voz CEO en tono directo, sin saludos, al punto."
      invocation_alias: humanize_comms       # CLI: mwt skill run humanize_comms
      stateless: true                        # skill packages típicamente stateless
      reusable_by_agents: true               # importable por agents

    # === Template metadata (cuando is_template: true) ===
    is_template: false                       # default false
    template_metadata:                        # solo si is_template: true
      template_id: TPL_REVIEW_TRIAGE         # ID del template
      template_version: 1.0
      icon: triage                           # NUEVO v1.2: icon ID del catálogo (triage | generator | validator | orchestrator | swarm | reactive | custom_path)
      maintained_by: ceo
      template_status: approved              # approved | draft | deprecated
      forks_count: 0                         # auto-incrementa en cada Fork
      placeholders:                          # campos que el Fork pide al CEO
        - path: outcome.baseline_value
          type: number
          help: "TTR review actual sin agente, en horas"
          required: true
        - path: outcome.target_at_60d
          type: expression
          help: "Objetivo a 60 días (ej: '< 8')"
          required: true
        - path: budget.usd_monthly
          type: number
          default: 25
          help: "Budget mensual aprox"
          required: false

    # === Triggers (NUEVO v1.2 — D16 conector dumb / agent smart) ===
    # El conector solo detecta evento + extrae payload + POST al endpoint.
    # CERO clasificación, branching o transformación de negocio en n8n.
    # Toda la lógica vive embebida en el agent vía flow.
    triggers:
      - kind: webhook                         # webhook | cron | api | manual
        source: gmail                         # gmail | slack | sp-api | sap | ...
        endpoint: /api/triggers/gmail
        connector: n8n                        # n8n | native | mcp_server
        connector_workflow_id: gmail_b2b_watcher_v1   # ref versionada al workflow n8n
        idempotency_key_field: payload.email.message_id
        rate_limit_per_min: 30
        deduplication_window_h: 24
        pre_dispatch_filters:                 # opcional, lógica trivial pre-agent
          - kind: spam_domains_blocklist
            max_logic_complexity: trivial    # solo regex/lookup, NO LLM
        auth_method: hmac

    # === Tools MCP (capacidades externas tipo APIs) ===
    tools_mcp:
      - id: amazon_sp_api_reviews
        kind: read_only
        scope: list_reviews | get_review | mark_actioned
        permission_model: per-tool            # cada tool con su permission
      - id: gmail_send                        # tool de SALIDA, distinto de trigger Gmail de ENTRADA
        kind: write
        scope: draft_only                     # nunca send sin approval

    # === Memory binding (three-layer) ===
    memory:
      pgvector_filter:
        domain: PRODUCTO
        visibility: [PUBLIC, INTERNAL]
        exclude: [FROZEN, CEO_ONLY]
      episodic_logger:
        enabled: true
        retention_days: 365
        pii_scrubbing: true
      learning_consolidation:                  # P5: target de aprendizaje
        target: GOLD_SAMPLES                   # CONTEXTO | SKILL_REFINEMENT | GOLD_SAMPLES | none
        requires_human_gate: true              # SIEMPRE true
        auto_apply: false                      # SIEMPRE false (regla inquebrantable)

    # === Deliverable type (Mitjana) — derivado de contract.outputs[] ===
    # NOTA: con outputs plural (v1.1) el deliverable.type se computa automáticamente del kind
    # de cada output. Si todos los outputs son kind:asset → deliverable.type=asset.
    # Si mezcla → deliverable.type=hybrid. No declarar manualmente.
    deliverable:
      computed_from_outputs: true              # builder calcula tipo desde contract.outputs[]
      decision_branches:                       # solo si algún output kind:decision
        - approve_response
        - escalate_to_human
        - ignore
      must_close_decisions: true               # no se acepta "tal vez" como output decision

    # === Outcome metric (P15 — POL_OUTCOME_ACCOUNTABILITY) ===
    outcome:
      primary: time_to_response_p50_hours      # métrica de negocio
      baseline_value: 28                       # valor pre-agente (PENDIENTE — CEO declara)
      target_at_60d: < 8                       # objetivo a 60 días
      secondary:
        - cited_complaints_resolved_rate
        - account_health_rating_delta
      measurement_cadence: weekly

    # === Budget y kill switch ===
    budget:
      usd_monthly: 25
      hard_cap_usd: 50
      tokens_monthly: 500000
      time_per_run_s: 60
      kill_switch:
        enabled: true
        trigger_on:
          - acceptance_rate_drop_pp: 10        # baja 10pp en 7 días
          - cost_overrun_count: 3              # 3 overruns en 7 días
          - human_intervention_count: 1        # 1 intervención manual
          - outcome_no_progress_days: 90       # sin moverse en 90 días → SHADOW

    # === Autonomy graduation (P4 — autonomía por evidencia) ===
    autonomy:
      current_level: 1                          # 0-6, ver SPEC_AUTONOMY_CONTROL_ENGINE
      target_level: 3                           # objetivo
      promotion_policy: standard                # standard | conservative | aggressive
      promotion_criteria:
        runs_minimum: 100
        acceptance_rate_min: 0.90
        schema_compliance_min: 0.99
        decision_closure_rate_min: 0.70
        diversity_coverage_min: 0.80
        cost_within_budget_rate_min: 0.95
      shadow_mode_runs: 50                      # paralelo SHADOW antes de promoción
      demotion_triggers:                        # democión automática
        acceptance_rate_drop_pp: 10
        consecutive_failures: 3                 # MAX_CONSECUTIVE_FAILURES (Claude Code leak)
        rejection_rate_max: 0.30

    # === Tenant scoping (MWT-only — single tenant siempre) ===
    # Para MWT v1 este campo es fijo y solo declarativo.
    # Si en el futuro se requiere multi-tenant, NO modificar este schema —
    # crear SCH_SKILL_MANIFEST_FB_V1 que extiende este con multi_tenant.
    tenant_scope:
      mode: single
      tenants: [mwt_internal]

    # === Consumers y observabilidad ===
    consumed_by:                                # quién invoca este skill
      - n8n://review-triage-flow
      - django://api/skills/review-triage
    observability:
      langfuse_session: review_triage
      audit_level: standard                     # standard | high | maximum
      trace_sample_rate: 1.0                    # 1.0 = todos los runs (SHADOW)
```

---

## Validaciones diferenciadas por type (NUEVO v1.2)

| Validación | Aplica a `type: skill_package` | Aplica a `type: agent` |
|------------|--------------------------------|------------------------|
| `tools_mcp[]` | NO permitido (skills no tienen tools propias) | sí |
| `channels` | NO permitido | sí |
| `triggers[]` | NO permitido | sí (si archetype: routine) |
| `skill_package_metadata` | obligatorio | NO permitido |
| `default_prompt` | obligatorio | NO aplica |
| `outcome.primary` | opcional | obligatorio |
| `budget.kill_switch` | opcional | obligatorio |
| `state_machine.ref` | opcional (skills suelen ser atómicos) | obligatorio |
| `multi_client_mode` | NO aplica | opcional |
| `architectural_archetype` | obligatorio = `skill_package` | obligatorio (Generator/Triage/Validator/Orchestrator/Swarm/Reactive) |

## Validaciones diferenciadas por architectural_archetype (NUEVO v1.2)

Cada arquetipo arquitectónico (ver ENT_AGENT_ARCHETYPES_V1) suma 2-3 validaciones específicas:

| Arquetipo | Validación adicional |
|-----------|----------------------|
| **Generator** | `golden_samples[]` ≥ 1 por output `kind: asset` |
| **Triage** | `flow.branches[]` con clausula `default:` exhaustiva en cada branch node |
| **Validator** | `policies[]` ≥ 1 + sección `deterministic_first` declarada en flow |
| **Orchestrator** | `state_machine.states ≥ 7` + side_effects con `requires_human_approval` por defecto |
| **Swarm** | `inputs.depends_on_skills[]` ≥ 2 + budget rollup declarado |
| **Reactive** | `triggers[]` ≥ 1 (cron o webhook) + `idempotency_key_field` declarado |
| **Skill_package** | `skill_package_metadata.default_prompt` no vacío |

## Validaciones build-time obligatorias

El compiler del builder valida estas reglas. Falla la compilación si alguna se rompe:

| # | Regla | Falla si |
|---|-------|----------|
| 1 | Visibility coherente | `mwt.visibility < max(inputs.kb_refs.visibility)` |
| 2 | Tipos no mezclados | `kb_refs` declara `ENT_X` pero apunta a archivo `PLB_X` |
| 3 | FROZEN seguro | input FROZEN no marcado `reference_only` |
| 4 | Dependency graph íntegro | manifest rompe cadena en DEPENDENCY_GRAPH.md |
| 5 | Schema lock activo | hay `tools_mcp.kind: write` sin `outputs[].schema` declarado |
| 6 | Outcome declarado | `outcome.primary` ausente y `archetype != skill_informational` |
| 7 | Kill switch activo | `archetype` en `[autonomous, routine, supervisor, workflow]` sin `budget.kill_switch.enabled: true` |
| 8 | Learning gate humano | `learning_consolidation.target != none` y `requires_human_gate != true` → reject |
| 9 | Auto-apply prohibido | `learning_consolidation.auto_apply: true` → reject (regla inquebrantable) |
| 10 | Tenant single | `tenant_scope.mode != single` → reject (este schema es MWT-only) |
| 11 | Sub-agents declarados | `archetype: supervisor` o `swarm` y `depends_on_skills: []` → reject |
| 12 | Promotion criteria coherentes | `autonomy.promotion_criteria` valores fuera de [0, 1] o thresholds inconsistentes → reject |
| 13 | Outputs plural | `contract.outputs[]` vacío → reject (al menos un output requerido) |
| 14 | Output kind válido | `contract.outputs[].kind` no en {asset, decision, learning, side_effect} → reject |
| 15 | Output IDs únicos | duplicados en `contract.outputs[].id` → reject |
| 16 | Approval requerida en assets externos | `kind: asset` con `destination` externa (publica) sin `requires_human_approval: true` → reject (P3 absoluto) |
| 17 | Golden sample requerido | `archetype` en `[workflow, autonomous, routine]` y `golden_samples: []` vacío → reject (al menos uno por output kind:asset) |
| 18 | Golden sample válido | `golden_samples[].path` no existe en filesystem → reject |
| 19 | Template placeholders válidos | `is_template: true` y `template_metadata.placeholders[]` vacío → warning (template sin placeholders es manifest plano) |
| 20 | Flow DAG válido | `archetype: workflow` y falta `flow.nodes[]` → reject (ver SCH_FLOW_DAG) |
| 21 | Type vs archetype coherente | `type: skill_package` con `archetype: workflow/supervisor/autonomous` → reject |
| 22 | Skills imports válidos | `skills_imports[]` referencia skill_id no presente en KB → reject |
| 23 | Triggers solo en agent | `type: skill_package` con `triggers[]` declarado → reject |
| 24 | Tools solo en agent | `type: skill_package` con `tools_mcp[]` declarado → reject |
| 25 | Multi-cliente coherente | `multi_client_mode: true` sin `client_resolver` declarado → reject |
| 26 | Trigger pre_dispatch_filters disciplinado | `pre_dispatch_filters[].max_logic_complexity != trivial` → warning (riesgo violar D16) |
| 27 | Connector workflow versionado | `triggers[].connector: n8n` sin `connector_workflow_id` → reject |
| 28 | Architectural archetype declarado | falta `architectural_archetype` → reject |

---

## Migración de SKILLs legacy

Los 10 SKILLs actuales (SKILL_AMAZON_OPS, SKILL_CLIENT_SERVICE, SKILL_COMPLIANCE_CHECKER, SKILL_COPY, SKILL_DEMAND_FORECASTER, SKILL_HUMANIZE_BRAND, SKILL_HUMANIZE_COMMS, SKILL_KB_AUDITOR, SKILL_PROFORMA_BUILDER, SKILL_RW_REVIEW_TRIAGE) se migran progresivamente en orden de prioridad operacional.

Orden recomendado:
1. **SKILL_RW_REVIEW_TRIAGE** (Fase 1 SPEC_AGENT_BUILDER_MWT_V1) — primer agente autónomo
2. **SKILL_RW_LISTING_OPT** o equivalente — segundo agente
3. **SKILL_DEMAND_FORECASTER** — único swarm, requiere sub_agents declarados
4. **SKILL_COMPLIANCE_CHECKER** — validator, two-stage review
5. Resto en orden CEO-priorizado

**Hasta migración**: SKILLs legacy mantienen su frontmatter actual y son válidos. Coexisten con v2 sin conflicto. La validación schema v2 solo aplica a SKILLs que declaran `metadata.mwt.id` con esta version.

---

## Compatibilidad cross-vendor

El frontmatter base SKILL.md es legible por:
- Claude Code (subagents y skills, Anthropic)
- Hermes Agent (NousResearch)
- Cursor (.cursorrules)
- OpenCode
- Cline
- Gemini CLI extensions
- agentskills.io hub

La extensión `metadata.mwt.*` es invisible para estos vendors (campo libre del estándar). Esto preserva portabilidad: un SKILL puede ejecutarse en runtime MWT con todas las reglas, o ejecutarse en Claude Code stand-alone para testing rápido.

---

## Ejemplo mínimo (para testing rápido)

```yaml
name: SKILL_TEST_HELLO
description: Skill mínimo para testing del compiler
version: 0.1.0
metadata:
  mwt:
    id: SKILL_TEST_HELLO
    domain: PLATAFORMA
    archetype: skill
    visibility: INTERNAL
    status: SHADOW
    inputs:
      kb_refs: []
    contract:
      outputs:
        - id: hello_text
          schema: SCH_HELLO_OUTPUT
          kind: asset
          destination: logs/hello/
          required: true
      schema_lock: strict
    state_machine:
      ref: SCH_STATE_MACHINE_BASIC
    golden_samples:
      - id: GS_HELLO_BASIC
        path: docs/gold_samples/hello_basic.md
        validates_outputs: [hello_text]
        evaluation_use: reference
    deliverable:
      computed_from_outputs: true
    outcome:
      primary: hello_count
      baseline_value: 0
      target_at_60d: > 0
    budget:
      usd_monthly: 1
      hard_cap_usd: 5
      kill_switch:
        enabled: true
        trigger_on:
          consecutive_failures: 3
    autonomy:
      current_level: 0
      target_level: 1
    tenant_scope:
      mode: single
      tenants: [mwt_internal]
```

Este manifest pasa todas las validaciones build-time. Sirve como smoke test del compiler.

---

## Nota de scope

Este schema aplica a **FaberLoom v1 (single-tenant beta con MWT como primer tenant)**. La sección `tenant_scope` y los campos relacionados con `multi_client_mode` están desde día 1 aunque el tenant inicial sea uno solo, evitando migración traumática cuando entre tenant 2. La infra cripto multi-tenant (isolation key per tenant, A2A bridge, profile system multi-org) se diseña para FB v2 cuando exista segundo prospect/LOI — heredando este schema como base.

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29): creación con scope MWT-only erróneo. Schema base SKILL.md + extensión `metadata.mwt.*` con 12 secciones (identidad, inputs, contract, state_machine, tools_mcp, memory, deliverable, outcome, budget, autonomy, tenant_scope, consumed_by/observability). 12 validaciones build-time. Plan de migración de 10 SKILLs legacy. Compatibilidad cross-vendor preservada.
- v1.1 (2026-04-29b): outputs plural en `contract.outputs[]` (reemplaza `output_schema` singular) — cada output con id, schema, kind (asset/decision/learning/side_effect), destination, required, condition opcional. Nueva sección `golden_samples` (norte de calidad + few-shot + regression eval). Nueva sección `is_template + template_metadata + placeholders` para Template Library (mismo módulo en MWT v1, separable en FaberLoom). 8 validaciones nuevas (13-20): outputs vacío, output kind, IDs únicos, approval externa, golden requerido, golden válido, template placeholders, flow DAG. Deliverable type ahora computed_from_outputs. Derivado de observación CEO sobre Workspace Agents OpenAI 2026-04-22 (templates pre-hechas + step-by-step plan + golden sample + outputs múltiples).
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado SCH_SKILL_MANIFEST_V2 → SCH_FB_SKILL_MANIFEST_v2. El schema fue conceptualizado durante sesión Cowork 2026-04-29 como MWT-only por error de scoping. El scope correcto siempre fue FB platform — MWT pasa de "el sistema" a "primer tenant beta". Sección `tenant_scope` desde día 1 con valor único `[mwt_internal]` en v1, extensible a multi-tenant en v2. Multi-client mode (D17) renombrado conceptualmente a multi-tenant base (sin cambio de nombre del campo por backward compat). Namespace `metadata.mwt.*` se conserva como deuda técnica con alias futuro a `metadata.fbl.*`. Aprobador: CEO sesión re-scoping 2026-04-29f.**
- v1.2 (2026-04-29c): distinción formal **type: skill_package | agent** con validaciones diferenciadas por type. Nueva sección **architectural_archetype** (Generator/Triage/Validator/Orchestrator/Swarm/Reactive/Skill_package) con validaciones específicas por arquetipo. Nueva sección **skills_imports[]** separada de tools_mcp[] (skills son paquetes reutilizables, tools son capacidades externas). Nueva sección **triggers[]** formal con D16 (conector dumb / agent smart): connector_workflow_id, idempotency_key_field, pre_dispatch_filters trivial-only, rate_limit. Nueva sección **multi_client_mode + client_resolver** para D17 (procesos embebidos, config en data — NO N flujos por cliente). Nueva sección **skill_package_metadata** con default_prompt + invocation_alias para skills ejecutables standalone vía CLI. Field **icon** opcional en template_metadata. 8 validaciones nuevas (21-28). Derivado de sesión Cowork 2026-04-29c (4 demos OpenAI Workspace Agents + observación CEO sobre voz como skill + sub-agentes + procesos embebidos multi-cliente).
- v2.0.1 (2026-06-23, FB-STD-CODEX-2026-06-23-01): fix mecánico de refs legacy FB-prefijo y paths `docs/gold_samples/*` → `docs/faberloom/gold_samples/*`.


---

## SECCION E1 -- Whitelist arquetipos ejecutables Foundation Beta E1

Esta seccion complementa el schema general del manifest.
En Foundation Beta E1, el executor TIER 1 aplica whitelist estricta.

Arquetipos ejecutables E1:
  classifier:   etiqueta/routing, output decision
  validator:    verifica reglas/policy, output decision + reporte
  generator:    crea contenido nuevo, output asset
  formatter:    transforma formato de asset existente
  triage:       clasifica + ramifica + draft condicional (1 output max)
  skill_package: meta-arquetipo reutilizable, NO agente ejecutable

Arquetipos reservados E2+:
  orchestrator: state machine multi-step (E2+)
  swarm:        composicion jerarquica (E2+)
  reactive:     event-driven (E2+)

Mapeo Pack 1:
  SKILL_PROFORMA_BUILDER:   generator
  SKILL_COMPLIANCE_CHECKER: validator
  SKILL_CLIENT_SERVICE:     triage
  SKILL_HUMANIZE_COMMS:     skill_package
  SKILL_KB_AUDITOR:         validator

Regla compiler E1:
  type == agent y archetype not in whitelist --> E1_ARCHETYPE_BLOCKED
  type == skill_package y archetype != skill_package --> E1_SKILL_PACKAGE_BAD_ARCHETYPE

Ver especificacion ejecutable completa:
  ENT_FB_DECISIONES_E1_v1.md seccion D6.1

Registrado: 2026-06-24 -- auditoria Fugu Ultra + Kimi 2.7 Round 5.
