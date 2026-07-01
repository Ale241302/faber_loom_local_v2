# SCH_FB_FLOW_DAG — Schema Declarativo de Flujos (DAG) FaberLoom
id: SCH_FB_FLOW_DAG
version: 2.0.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SCH
stamp: VIGENTE — 2026-04-29f (re-scope FB)
aprobador: CEO (sesión Cowork 2026-04-29 + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SCH_FB_SKILL_MANIFEST_v2.md · SPEC_FB_AGENT_BUILDER_v1.md · SCH_FB_TASK_ENTITY.md · SCH_STATE_MACHINE_*.md

---

## Declaración

Este schema define el **plan declarativo** de un agente con `archetype: workflow`, `routine` o `supervisor`. El plan es un **DAG (grafo dirigido acíclico)** de nodos donde cada nodo es una invocación de SKILL_ o una operación interna (branch, terminal, notify), y los edges son transiciones determinísticas o condicionales.

**El plan es la columna vertebral de la ejecución.** El agente NO improvisa la secuencia — la lee del manifest y ejecuta nodo por nodo. Esto matchea el patrón observado en OpenAI Workspace Agents: cada step del agente referencia el plan declarativo, no decide on-the-fly.

---

## Por qué este schema existe

Hasta v1.0 del SCH_SKILL_MANIFEST_V2, el archetype `workflow` mencionaba "secuencia fija" y `supervisor` "orquesta sub-agents", pero sin formato concreto del DAG. Sin schema:
- Compiler no puede validar grafo (ciclos, nodos huérfanos, branches sin default)
- Runtime no puede ejecutar de forma reproducible
- Debugging post-mortem es opaco
- Replay determinístico imposible

SCH_FLOW_DAG resuelve esto declarando estructura mínima y validable.

---

## Estructura del flow

```yaml
# Va dentro de metadata.mwt cuando archetype in [workflow, routine, supervisor]
flow:
  # Política global del flow
  max_depth: 5                              # max nivel de anidamiento (sub-flows)
  timeout_total_min: 15                     # timeout global del flow
  on_timeout: human_escalation              # nodo destino si timeout global
  fail_policy: stop                         # stop | continue | rollback

  # Nodos del DAG
  nodes:
    - id: classify_severity                 # ID único dentro del flow
      kind: skill_call                      # skill_call | branch | parallel | terminal | notify
      skill_ref: internal_classifier        # ref a SKILL_ o módulo interno (cuando kind=skill_call)
      input_map:                            # cómo se construye el input desde flow context
        review_text: "{{flow.input.review_text}}"
      emits: severity_tag                   # qué output del SKILL llamado se asigna a flow context
      timeout_s: 30
      on_failure: branch_critical           # nodo destino si este nodo falla
      retries: 1

    - id: branch_severity                   # nodo branch (decisión)
      kind: branch
      depends_on: [classify_severity]       # debe completarse antes
      conditions:                           # primera que matchea gana
        - if: "{{flow.context.severity_tag.value}} == 'critical'"
          goto: emit_escalation
        - if: "{{flow.context.severity_tag.value}} == 'low'"
          goto: emit_thanks
        - default:
          goto: compliance_check

    - id: compliance_check
      kind: skill_call
      skill_ref: SKILL_COMPLIANCE_CHECKER
      depends_on: [branch_severity]
      input_map:
        text: "{{flow.input.review_text}}"
        policies: [POL_BRAND_VOICE, POL_AMAZON_TOS]
      emits: compliance_result
      on_failure: emit_escalation

    - id: branch_compliance
      kind: branch
      depends_on: [compliance_check]
      conditions:
        - if: "{{flow.context.compliance_result.passes}} == true"
          goto: draft_response
        - default:
          goto: emit_escalation

    - id: draft_response
      kind: skill_call
      skill_ref: SKILL_COPY
      depends_on: [branch_compliance]
      input_map:
        review_text: "{{flow.input.review_text}}"
        severity: "{{flow.context.severity_tag.value}}"
      emits: response_draft

    - id: emit_response
      kind: terminal                        # nodo terminal exitoso
      depends_on: [draft_response]
      outputs_emit:                         # qué outputs del manifest se materializan
        - response_draft                    # ref a contract.outputs[].id

    - id: emit_thanks
      kind: skill_call
      skill_ref: SKILL_HUMANIZE_COMMS
      input_map:
        sentiment: positive
        review_text: "{{flow.input.review_text}}"
      emits: thanks_draft

    - id: emit_thanks_terminal
      kind: terminal
      depends_on: [emit_thanks]
      outputs_emit: [thanks_draft]

    - id: emit_escalation
      kind: terminal
      outputs_emit: [escalation_ticket]
      side_effect:
        notify_channel: ceo_email
        priority: high

  # Entry point del flow
  entry: classify_severity                   # nodo inicial

  # Outputs map: cómo flow context → contract.outputs[] del manifest
  output_emission_map:
    response_draft: "{{flow.context.response_draft}}"
    severity_tag: "{{flow.context.severity_tag}}"
    escalation_ticket: "{{flow.context.severity_tag if severity == 'critical'}}"
```

---

## Tipos de nodo

| Kind | Función | Campos requeridos |
|------|---------|-------------------|
| `skill_call` | invoca un SKILL_ o módulo interno | `skill_ref`, `input_map`, `emits` |
| `branch` | decisión condicional, ramifica el grafo | `conditions[]` con if/default |
| `parallel` | ejecuta varios nodos en paralelo, espera todos | `branches[]` (lista de nodos hijos) |
| `terminal` | nodo final, materializa outputs y termina rama | `outputs_emit[]` |
| `notify` | side effect (email, slack, webhook) sin emitir output | `channel`, `payload` |
| `human_gate` | espera aprobación humana antes de continuar | `prompt_to_user`, `timeout_h` |
| `config_resolver` (NUEVO v1.1) | carga config externa al flow context (D17 multi-cliente) | `source`, `key_field`, `loads_into`, `cache_ttl_min` |

### Detalle: kind `config_resolver` (v1.1)

Operacionaliza D17 (procesos embebidos, configuración en data). Permite que el flow cargue config per-cliente al context al inicio de la ejecución, sin acoplar la lógica del agent al cliente específico.

Ejemplo de nodo:

```yaml
- id: resolve_client
  kind: config_resolver
  source: ENT_COMERCIAL_CLIENTES          # KB ref o tabla Postgres
  resolve_strategy: by_domain              # by_domain | by_explicit_id | by_email_pattern
  payload_extraction: payload.email.sender_domain
  loads_into: flow.context.client_profile
  cache_ttl_min: 60
  fallback: prospect_unknown               # client_id por defecto si no matchea
```

Una vez ejecutado, los siguientes nodos consumen `flow.context.client_profile.*` como parámetro al SKILL invocado, evitando ramificar el grafo por cliente.

## Sub-steps anidados (NUEVO v1.1)

Los nodos `kind: skill_call` cuando invocan skills complejos pueden emitir **sub-steps** al runtime para visibilidad granular en el dashboard. No es una nueva primitiva del DAG — es metadata de ejecución persistida en episodic_memory:

```yaml
# Cuando un nodo skill_call ejecuta:
nodes:
  - id: classify_intent
    kind: skill_call
    skill_ref: email_classifier
    sub_steps_visible: true    # default true para skill_call

# Runtime emite sub-steps en episodic_memory:
{
  "node_id": "classify_intent",
  "sub_steps": [
    {"label": "Reading classification policy", "duration_ms": 120, "status": "completed"},
    {"label": "Matching intent patterns", "duration_ms": 340, "status": "completed"},
    {"label": "Confidence scoring", "duration_ms": 80, "status": "completed"}
  ]
}
```

El dashboard CEO renderiza el flow viewer con jerarquía: nodo del flow + sub-steps anidados (observado en demos OpenAI Trove y Tally).

---

## Validaciones build-time

| # | Regla | Falla si |
|---|-------|----------|
| 1 | Acíclico | el grafo tiene ciclo (no se permiten loops directos; usar `archetype: autonomous` con max_iterations en su lugar) |
| 2 | Entry point existe | `entry` no apunta a un `node.id` válido |
| 3 | Edges válidos | `goto` apunta a `node.id` inexistente |
| 4 | Branch con default | `kind: branch` sin clausula `default:` → reject (cobertura exhaustiva obligatoria) |
| 5 | Terminal alcanzable | hay rama del DAG que no termina en nodo `kind: terminal` ni `human_gate` |
| 6 | Outputs declarados | `node.kind: terminal` con `outputs_emit[]` referencia a IDs no presentes en `contract.outputs[]` |
| 7 | Profundidad respetada | grafo excede `max_depth` |
| 8 | Sub-skills existen | `skill_ref` apunta a SKILL_ no presente en KB ni declarado en `inputs.depends_on_skills` |
| 9 | Input map completo | `input_map` deja campos requeridos del SKILL invocado sin mapear |
| 10 | Human gate con timeout | `kind: human_gate` sin `timeout_h` declarado → reject |
| 11 | IDs únicos | duplicados en `nodes[].id` → reject |
| 12 | Parallel sin races | `kind: parallel` con sub-nodos que escriben al mismo `emits` → warning |
| 13 (v1.1) | config_resolver al inicio | `kind: config_resolver` debe estar en `flow.entry` o ser primer nodo de cada rama si `multi_client_mode: true` |
| 14 (v1.1) | config_resolver coherente | `loads_into` debe declarar path en `flow.context.*` válido |

---

## Compatibilidad con state_machine

`flow` (DAG declarativo) **complementa**, no reemplaza, `state_machine` (P7 obligatorio).

| | flow | state_machine |
|---|------|---------------|
| Granularidad | nodo = step de ejecución | estado = situación lifecycle (drafting, awaiting_approval, etc.) |
| Determinismo | DAG sin ciclos | máquina con loops permitidos |
| Trigger transiciones | output del nodo previo | evento externo (CEO approve, timeout) |
| Visibilidad | qué hace el agente paso a paso | en qué estado lifecycle está |

Un flow puede atravesar varios estados de la state_machine. Ejemplo: nodo `human_gate` mantiene estado `awaiting_approval`; cuando CEO aprueba, transición a `approved` y el flow continúa al siguiente nodo.

---

## Ejecución runtime

El runtime (módulo Django nuevo `agents/flow_executor.py`) hace:

1. Lee `metadata.mwt.flow` del manifest
2. Inicializa `flow.context` con `flow.input` recibido (de tarea o trigger)
3. Empieza por `flow.entry`
4. Ejecuta nodo según su `kind`:
   - `skill_call`: invoca SKILL referenciado, espera completion, asigna `emits` a context
   - `branch`: evalúa conditions, salta a `goto`
   - `parallel`: spawna sub-tareas, espera join
   - `terminal`: materializa outputs según `outputs_emit`, termina rama
   - `notify`: dispara side effect, continúa
   - `human_gate`: emite tarea con `awaiting_approval`, pausa flow
5. Loggea cada step a episodic_memory con `state_machine_path[]`
6. Cuando todas las ramas terminan, materializa `contract.outputs[]` finales

Cost rollup: el costo del flow = suma de costos de todos los `skill_call` invocados.

---

## Limitaciones (por diseño v1)

- **No loops nativos.** Si necesitás iteración (procesar lista de items), usá `archetype: autonomous` con max_iterations o un loop explícito en código del SKILL invocado por un nodo.
- **No nested flows v1.** Un flow puede invocar SKILLs (que pueden ser archetype workflow), pero el runtime no aplana automáticamente sub-flows. Cada flow es atómico desde su perspectiva.
- **No paralelismo masivo.** `kind: parallel` soporta ≤4 ramas concurrentes en v1 (límite Celery worker pool).
- **Expressions limitadas.** En `conditions` y `input_map`, syntax estilo `{{flow.context.X.field}}` con operadores básicos (`==`, `!=`, `>`, `<`, `and`, `or`). No Jinja2 completo (KISS).

---

## Cuándo NO usar flow (usar otra primitiva)

| Caso | Primitiva correcta |
|------|--------------------|
| Tarea atómica sin steps | `archetype: skill` sin flow |
| Loop con max iteraciones | `archetype: autonomous` con `loop.max_iterations` |
| Pipeline ETL determinístico | mejor en Windmill, no flow |
| Workflow visual con gestión de instancias | n8n |
| Long-running con sleeps/waits | considerar Inngest (FB v2 futuro) |

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29b): creación con scope MWT-only erróneo. Schema declarativo de DAG con 6 tipos de nodo (skill_call, branch, parallel, terminal, notify, human_gate). 12 validaciones build-time. Compatibilidad con state_machine. Limitaciones documentadas (no loops, no nested, no Jinja completo).
- v1.1 (2026-04-29c): agregado kind `config_resolver` (carga config externa al context para D17 multi-cliente/multi-tenant). Documentado patrón **sub-steps anidados** en skill_call para visibilidad granular en dashboard. 2 validaciones nuevas (13, 14) sobre config_resolver.
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado SCH_FLOW_DAG → SCH_FB_FLOW_DAG. El schema fue conceptualizado como MWT-only por error de scoping; el scope correcto siempre fue FB platform. El nodo `config_resolver` (D17) es la primitiva del multi-tenant en FB v1: carga `tenant_profile` + `client_profile` desde data al inicio del flow. MWT pasa de "el usuario" a "primer tenant beta". Aprobador: CEO sesión re-scoping 2026-04-29f.**
- v2.0.1 (2026-06-23, FB-STD-CODEX-2026-06-23-01): fix mecánico de ref legacy `SCH_TASK_ENTITY.md` → `SCH_FB_TASK_ENTITY.md` en metadata relacionado.
