# ENT_FB_DECISIONES_E1_v1 -- Decisiones de diseno Foundation Beta E1
id: ENT_FB_DECISIONES_E1_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: PLB_FB_FOUNDATION_BETA_v1.md · SCH_FB_FUNCTIONAL_SPEC_v1.md · ARCH_AGENT_PRINCIPLES.md

---

## Proposito

Resuelve contradicciones detectadas por Kimi Swarm 2026-06-24 (D1-D6 v1.0)
y por auditoria Fugu Ultra + Kimi 2.7 Round 5 (D5.1 + D6.1 v1.1).

---

## D1 -- Canales en E1: OMNICANAL

FaberLoom es omnicanal desde S1A.
Canales E1: Gmail OAuth + IMAP, WhatsApp BSP, Webhook generico, Workspace upload.
Cada canal es MCP connector dumb pipe (max 5 nodos, sin LLM).
Reemplaza enmienda E-5 -- ANULADA.

---

## D2 -- Roles en E1: SCHEMA 5 ROLES, 2 ACTIVOS EN S1A

Schema DB: role text CHECK IN (owner,admin,operator,supervisor,viewer)
S1A: Owner + Operator. S5: Admin. S6: Supervisor + Viewer.
Multi-rol: actor_role_at_decision registrado en cada accion.
Reemplaza enmienda E-4 -- ANULADA.

---

## D3 -- Layout WorkLoom: KANBAN 4 COLUMNAS

Columnas: Critico / Listo para revisar / En proceso / Error accionable
Cards ordenadas: SLA restante ASC, confidence LOW first, valor DESC.
Columna = tipo de criterio requerido, no etapa de procesamiento.

---

## D4 -- Toggles agentes: PANEL DERECHO WORKSPACE

4 tabs: Agentes (ON/OFF) / Skills / Aprendizaje / Contexto activo.
WorkLoom = solo trabajo. Sin controles de configuracion.

---

## D5 -- Estados skill: 4 ESTADOS + SHADOW THRESHOLD E1

### D5.0 Estados canonicos

status text NOT NULL DEFAULT shadow CHECK
  (status IN (shadow, active, paused, deprecated))

shadow:     existe, no ejecuta externamente, acumula evidencia
active:     operacion normal hasta autonomy_ceiling
paused:     suspendido, mantiene memoria
deprecated: fuera de uso, memoria archivada

Transiciones:
  shadow --> active:     Owner/Admin aprueba (ver D5.1)
  active --> paused:     Owner/Admin pausa o fallo detectado
  paused --> active:     Owner/Admin reactiva
  active --> deprecated: Owner/Admin retira

### D5.1 Shadow promotion policy Foundation Beta E1

Condiciones (TODAS deben cumplirse):
  1. reviewed_shadow_runs >= 10
  2. approval_rate >= 0.70
  3. Owner/Admin hace clic explicito en Promover a ACTIVE
  4. Sin incidente P0/P1 abierto del skill
  5. Skill paso sandbox smoke test en spec_json actual

Definiciones:
  shadow_run: ejecucion con input real, sin side-effect externo
  reviewed_shadow_run: shadow_run con revision humana explicita
  edit_light: edicion <= 20% del output = cuenta como approved
  approval_rate = (approved + edit_light) / reviewed_shadow_runs
  runs_source: produccion solamente -- replay/eval NO cuenta en E1

Downgrade trigger:
  Si rejection_rate de ultimas 5 ejecuciones > 0.30:
  skill vuelve a SHADOW automaticamente + AuditEntry inmutable.

Review deadline: a las 8 semanas CEO decide extender/refinar/archivar.

UX shadow_review:
  Location: Mesa de Control Zona 3 Sandbox
  Card: skill_name, badge SHADOW, contador X/10, approval_rate Z%,
    last_output_preview
  Acciones: [Aprobar evidencia] [Editar evidencia] [Rechazar]
  Boton [Promover a ACTIVE]: visible solo si runs>=10 y rate>=70%
  Sin accion Enviar ni accion externa en SHADOW.

ACTIVE en E1:
  active genera outputs hacia WorkLoom normalmente.
  active NO autoriza envio externo autonomo.
  external_communication y external_mutation siguen requiriendo
  human_approver_id obligatorio.

Override P4: ARCH_AGENT_PRINCIPLES P4 (>=3 runs) es piso global.
  FaberLoom E1 usa 10 runs reales >= 70% con gate Owner/Admin.

Tests:
  test_shadow_promotion_blocked_at_9_runs
  test_shadow_promotion_blocked_low_approval
  test_shadow_promotion_creates_audit_entry
  test_shadow_outputs_visible_in_zona3_not_workloom
  test_shadow_downgrade_trigger_on_high_rejection_rate
  test_active_skill_still_requires_hitl_for_external_action

---

## D6 -- Engine skills: SKILLSPEC DB PYDANTIC + ARQUETIPOS E1

### D6.0 Engine

Tabla skills: id, tenant_id, name, slug, archetype, spec_json (jsonb),
  status, version, created_by, approved_by, last_sandbox_test_at

Runtime:
  spec = SkillSpec.model_validate(skill.spec_json)
  executor.run(spec, task_context)

Failure path SkillSpec invalido:
  capturar pydantic.ValidationError
  task.status = failed (NO retry -- error deterministico de schema)
  error_code = SKILL_SPEC_VALIDATION_ERROR
  WorkLoom columna Error accionable
  AuditEntry D10 + evento task.failed

Limites TIER 1 (no configurables):
  sin tools externas / sin HTTP / sin code execution / sin subprocess
  timeout_s = min(spec.timeout_s, 60)
  cost_cap = min(spec.cost_cap, 2.00)
  LiteLLM solo via Action Engine / LiteLLM Proxy
  workers sin acceso directo a API keys de providers

### D6.1 Arquetipos runtime TIER 1 Foundation Beta E1

Whitelist E1 (5 arquetipos ejecutables):

  classifier:
    produce labels, routing decision, priority, task_type o data_class.
    No produce texto final customer-facing.

  validator:
    verifica contra reglas, schema, policy, checklist o KB vigente.
    Output: pass/fail + findings + required_fix.
    Deterministic-first segun P14.

  generator:
    produce draft o asset nuevo a partir de input y contexto.

  formatter:
    transforma estructura, tono o formato de output existente.
    No cambia intencion de negocio.

  triage:
    clasifica + ramifica + emite draft condicional en una ejecucion.
    Restriccion critica: exactamente UN output por ejecucion.
    Ramificacion via routing_decision (label).
    NO via outputs paralelos.
    Prohibido invocar otro skill, loop o retry autonomo.
    Si comportamiento de mini-orchestrator en beta: restriccion formal E2.

Bloqueados E1 (E2+):
  orchestrator: state machine multi-step + side effects
  swarm:        composicion jerarquica de sub-agentes
  reactive:     event-driven sin invocacion humana directa

skill_package:
  Meta-arquetipo reutilizable. NO es agente ejecutable.
  Importable por otros agentes via skills_imports[].
  Sin tools_mcp, channels ni triggers.

Mapeo Pack 1:
  SKILL_PROFORMA_BUILDER:   generator
  SKILL_COMPLIANCE_CHECKER: validator
  SKILL_CLIENT_SERVICE:     triage
  SKILL_HUMANIZE_COMMS:     skill_package
  SKILL_KB_AUDITOR:         validator

Validacion runtime:
  ALLOWED = {classifier, validator, generator, formatter, triage}
  RESERVED_E2 = {orchestrator, swarm, reactive}
  archetype in RESERVED_E2 --> E1_ARCHETYPE_BLOCKED
  archetype == skill_package y type == agent --> E1_SKILL_PACKAGE_NOT_AGENT
  archetype not in ALLOWED --> TIER1_ARCHETYPE_NOT_ALLOWED

UI rule E1:
  Agent Factory muestra solo 5 arquetipos + skill_package.
  orchestrator/swarm/reactive: Disponible E2, disabled con tooltip.

Tests:
  test_invalid_skillspec_marks_task_failed_not_running
  test_task_validation_error_is_not_retried
  test_tier1_accepts_only_5_allowed_archetypes
  test_orchestrator_rejected_with_e1_archetype_blocked
  test_pack_1_archetypes_all_compile_valid
  test_skill_package_rejected_as_agent_archetype
  test_tier1_timeout_clamped_to_60s
  test_tier1_cost_cap_clamped_to_2_usd

Reemplaza: D6 v1.0 con 3 arquetipos -- ACTUALIZADO a 5.

---

## Contradicciones resueltas

v1.0: D1/D2/D3/D4/D5.0/D6.0
v1.1: D5.1 shadow threshold 10 runs / D6.1 arquetipos 5 + skill_package

## Contradicciones pendientes

  Sprint Draft/HITL S3 vs S5 -- Alejandro decide
  estados task created vs queued -- PENDIENTE S1A
  DPA wizard vs offline -- PENDIENTE CEO antes S10

---
Changelog:
- v1.1 (2026-06-24): D5.1 shadow promotion 10 runs + UX Zona 3.
  D6.1 arquetipos TIER 1 E1: 5 arquetipos + skill_package.
  Auditoria Fugu Ultra + Kimi 2.7 Round 5.
- v1.0 (2026-06-24): Creacion D1-D6.
