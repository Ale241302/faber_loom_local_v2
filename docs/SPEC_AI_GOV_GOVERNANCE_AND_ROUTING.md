# SPEC_AI_GOV_GOVERNANCE_AND_ROUTING — Gobernanza de IA y Routing
id: SPEC_AI_GOV_GOVERNANCE_AND_ROUTING
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SPEC
subfamilia: AI_GOV (subdominio conceptual bajo Plataforma; spec madre del subsistema)
stamp: VIGENTE — 2026-05-01
aprobador: CEO
aplica_a: [MWT, FaberLoom]
gobierna_a: SPEC_LLM_ROUTING_ARCHITECTURE (capa tecnica) · ENT_PLAT_ACTION_REGISTRY (catalogo) · todas las skills externas e internas que invocan LLM
relacionado: SPEC_ACTION_ENGINE.md (D9 Data Classification, D10 Audit Module) · SPEC_AUTONOMY_CONTROL_ENGINE.md (OutcomeLedger) · SPEC_LLM_ROUTING_ARCHITECTURE.md v1.3 (Token Ledger) · SPEC_AUDIT_MODULE.md · POL_AI_GOV_DATA_CLASS_PROVIDER · POL_AI_GOV_SKILL_INSTALLATION · POL_AI_GOV_FINAL_OUTPUT_QUALITY · SCH_AI_GOV_HANDOFF_DRAFT · ENT_AI_GOV_GOLDEN_CORPUS_MWT · ENT_AI_GOV_OUTPUT_PINS · PLB_AI_GOV_DUAL_REVIEW · SCH_AI_GOV_DUAL_REVIEW_OUTPUT · POL_DATA_CLASSIFICATION · ARCH_AGENT_PRINCIPLES (P3, P9, P13, P14)

---

## Declaracion

Este SPEC es la capa de **gobernanza** sobre el routing tecnico de LLMs. SPEC_LLM_ROUTING_ARCHITECTURE define **como** se rutea (L1/L2/L3, dispatcher, compiler, ledger). Este SPEC define **que esta permitido**, **bajo que costo**, **con que riesgo**, y **con que pinning**.

> **Regla de precedencia:** AI_GOV gobierna; LLM_ROUTING ejecuta. Ante conflicto entre la decision tecnica del dispatcher y la policy de governance, **gana governance**. El motor tecnico no debe ganarle al freno.

Sin este SPEC, el routing tecnico es funcional pero ciego a:
- privacidad de datos por proveedor
- caps de costo por skill/agente/org
- pinning de outputs validados
- evaluacion mensual de modelos nuevos
- final pass premium para outputs cliente-visibles

---

## Arquitectura — vista de capas

```
+----------------------------------------------------------+
| CAPA AI_GOV — politicas y entidades de gobernanza        |
|                                                           |
|  POL_AI_GOV_DATA_CLASS_PROVIDER  (matriz autoritativa)   |
|  POL_AI_GOV_SKILL_INSTALLATION   (lifecycle skills)      |
|  POL_AI_GOV_FINAL_OUTPUT_QUALITY (final pass premium)    |
|  ENT_AI_GOV_OUTPUT_PINS          (recetas pineadas)      |
|  ENT_AI_GOV_GOLDEN_CORPUS_MWT    (corpus eval)           |
|  SCH_AI_GOV_HANDOFF_DRAFT        (contract handoff)      |
+----------------------------------------------------------+
                          |
                          v consulta antes de despachar
+----------------------------------------------------------+
| CAPA TECNICA — SPEC_LLM_ROUTING_ARCHITECTURE v1.3        |
|                                                           |
|  Tier 0 deterministic                                     |
|  L1 Clasificador                                          |
|  L2 Dispatcher (Arena Feed + Cost Oracle + Ledger)       |
|  L3 Prompt Compiler                                       |
|  Token Ledger (con campos AI_GOV: provider_allowed,      |
|    data_class, audit_id, pinned_output_id, etc)          |
+----------------------------------------------------------+
                          |
                          v invocacion via Action Engine
+----------------------------------------------------------+
| CAPA INFRAESTRUCTURA — SPEC_ACTION_ENGINE                |
|                                                           |
|  ENT_PLAT_ACTION_REGISTRY (catalogo proveedores)         |
|  SPEC_AUDIT_MODULE        (audit_event)                  |
|  SPEC_AUTONOMY_CONTROL_ENGINE (RequestOutcomeEntry)      |
+----------------------------------------------------------+
```

---

## Componentes que este SPEC ata

### 1. Skill Contract (referencia POL_AI_GOV_SKILL_INSTALLATION)

Toda skill (interna o externa) declara contrato con:
- runtime soportado
- agentes autorizados
- data classes que puede tocar
- capabilities (codigo, archivos, APIs)
- cost policy (cap por run, soft warn, owner)
- conflicts con skills instaladas
- security scan status

Skill sin contrato no se ejecuta. El Action Engine consulta el contrato antes de cada invocacion.

### 2. Data Class x Provider Matrix (referencia POL_AI_GOV_DATA_CLASS_PROVIDER)

Matriz autoritativa N0-N4 x DPA-FULL/DPA-COMERCIAL/NO-DPA-MANAGED/SELF-HOST-OPEN. Cada llamada LLM:
- consulta el `accepts_data_class` del proveedor en ENT_PLAT_ACTION_REGISTRY
- valida contra la matriz de POL_AI_GOV_DATA_CLASS_PROVIDER
- registra `provider_allowed_by_policy: bool` en Token Ledger
- si false, el Engine rechaza antes de despachar

**Asimetria de orquestador:** Kimi/Moonshot puede orquestar chains que tocan N3 si y solo si solo recibe metadata (N0/N1) y los carpinteros son DPA-FULL/SELF-HOST.

### 3. Cost Policy por Skill

Cada skill declara en su contrato:
```yaml
cost_policy:
  unit:           usd_per_run
  hard_cap:       0.50
  soft_warn:      0.30
  budget_owner:   <persona>
```

El Engine antes de despachar:
- estima `cost_total_usd` con Cost Oracle
- compara contra hard_cap del skill, del agente, del org, del run
- si excede hard_cap → rechazo o degradacion de modelo
- si excede soft_warn 3+ veces en 7 dias → alerta al owner

Caps activos se registran en `budget_caps_applied` y `budget_status` del ledger.

### 4. Final Output Quality Pass (referencia POL_AI_GOV_FINAL_OUTPUT_QUALITY)

Outputs cliente-visibles obligatoriamente pasan por finalizador (Sonnet 4.6 default, Opus 4.7 critico). Excepcion: short-circuit por gold sample con 5 condiciones AND.

Handoff carpintero -> finalizador via SCH_AI_GOV_HANDOFF_DRAFT.

### 5. Output Pinning (referencia ENT_AI_GOV_OUTPUT_PINS)

Outputs aprobados clean (edit_distance=0) son candidatos a pin. Pin vincula:
- task_type + skill_id + client_context_hash
- model + prompt_hash + context_hash

Pins activan short-circuit del dispatcher cuando hay match >= 0.90 similarity.

**Re-evaluacion mensual (torneo):** sandbox corre pin vs retadores; si retador alcanza calidad equivalente con costo >=40% menor, propuesta de re-pin a CEO.

> "El rey conserva la corona, pero todos los meses hay torneo."

### 6. Dual Review para decisiones técnicas (referencia PLB_AI_GOV_DUAL_REVIEW + SCH_AI_GOV_DUAL_REVIEW_OUTPUT)

Caso especial de cadena Token Ledger con 3 entries y mismo `parent_request_id`: proponente (`role: carpintero`) + auditor adversarial (`role: judge`) + sintetizador (`role: final_pass`). Modelos de **familias distintas obligatorio** (Anthropic vs OpenAI vs Google vs Moonshot vs DeepSeek). Aplica a decisiones técnicas P0/P1: SPECs, schemas, POLs, migraciones, PRs con side effects, prompts críticos.

Modo MVP: prescriptivo (decisor ejecuta los 3 pasos manual). Modo ejecutable: post Action Engine F1, vía `action_engine.execute(intent="dual_review", ...)`.

Caps: 3 invocaciones P1/semana por decisor, USD 2.50/run hard cap, USD 30/mes por decisor. Anti-loop: 1 sola ronda, sin re-runs automáticos.

### 7. Monthly Model Evaluation Lab (referencia ENT_AI_GOV_GOLDEN_CORPUS_MWT)

Cada mes, sandbox corre el golden_corpus contra:
- modelos pineados (defender de su pin)
- modelos nuevos del ecosistema (retadores)
- modelos existentes con nuevas versiones

Judge model + criterios objetivos del golden_case generan scorecard. CEO revisa propuestas de re-pinning.

Triggers de re-evaluacion:
- calendarico: mensual
- evento: release de modelo nuevo (Anthropic, OpenAI, Google, Moonshot, etc)
- evento: drift detectado (judge sample mensual da alerta)
- evento: change de pricing del proveedor pineado >=30%

---

## Cadena ejecutable (debe quedar explicita)

```
Skill -> Action Engine -> Routing tecnico (L1/L2/L3) -> Provider Policy check ->
LLM call -> Token Ledger entry -> RequestOutcomeEntry -> Final Pass policy ->
Handoff schema -> Final output -> Output Pinning candidate -> Eval Lab mensual
```

Esta cadena es la columna vertebral del subsistema AI_GOV. Cada salto:
- valida contra una policy
- registra en una entidad
- alimenta el feedback loop

---

## Interfaces (resumen)

| Componente | Lee de | Escribe a |
|------------|--------|-----------|
| Action Engine | POL_AI_GOV_DATA_CLASS_PROVIDER · ENT_PLAT_ACTION_REGISTRY · skill contracts | Token Ledger · audit_event · RequestOutcomeEntry |
| L1 Clasificador | request del usuario | classification → L2 |
| L2 Dispatcher | Arena Feed · Cost Oracle · Token Ledger · ENT_AI_GOV_OUTPUT_PINS · cost_policy del skill | dispatch_plan |
| L3 Compiler | dispatch_plan · ENT_AI_GOV_GOLDEN_CORPUS_MWT (gold samples para few-shot) | compiled_prompt |
| Token Ledger | TODAS las llamadas LLM | feedback al Dispatcher · audit · cost reporting |
| Final Pass policy | SCH_AI_GOV_HANDOFF_DRAFT · ENT_AI_GOV_OUTPUT_PINS · ENT_AI_GOV_GOLDEN_CORPUS_MWT | handoff_response · outcome |
| Eval Lab | ENT_AI_GOV_GOLDEN_CORPUS_MWT · ENT_AI_GOV_OUTPUT_PINS · Token Ledger histortico | propuestas de re-pin a CEO |

---

## Reglas inquebrantables

1. **Ninguna llamada LLM sin entry en Token Ledger.** Skill que llama proveedor bypaseando ledger es defectuosa por definicion. Lifecycle: deprecated automatico.
2. **Ningun output cliente-visible sin final_pass_required = true en ledger.** Sample mensual valida. Excepciones documentadas en POL_AI_GOV_FINAL_OUTPUT_QUALITY §J.
3. **AI_GOV gobierna, LLM_ROUTING ejecuta.** Si L2 selecciona modelo prohibido por POL_AI_GOV_DATA_CLASS_PROVIDER, gana governance.
4. **Tier compuesto:** output_tier = max(input_tiers de toda la cadena). Carpintero no puede bajar tier de un input.
5. **Pin no es dogma:** torneo mensual obligatorio. Pin que no se rete = pin estancado.
6. **Cap de tokens por skill SIEMPRE existe.** Free tier sin cap es prohibido.
7. **Override de policy requiere audit_event con expiracion.** Cost-mode opt-in maximo 90 dias renovables.
8. **Skill externa sin contrato + scan + sandbox + owner = bloqueada.** No hay excepciones.

---

## Estados de implementacion

| Componente | Estado actual | Trigger de activacion |
|------------|---------------|----------------------|
| Token Ledger v1.3 con campos governance | SPEC actualizado · implementacion sem 3+ Action Engine | inicio sem 3 roadmap Action Engine |
| POL_AI_GOV_DATA_CLASS_PROVIDER enforcement | DRAFT enforcement · catalogo vigente en ENT_PLAT_ACTION_REGISTRY | hookpoint en Action Engine.execute() sem 3+ |
| Skill contracts | DRAFT contract template · primer skill con contrato pendiente | primera skill externa instalada bajo este regimen |
| Final pass policy | DRAFT enforcement | hookpoint en final pass dispatcher post sem 3 |
| Output pins | esquema definido en ENT · poblamiento pendiente | primer output approved clean post implementacion |
| Golden corpus | esqueleto en ENT · poblamiento 50-100 cases pendiente | sprint dedicado de curacion CEO |
| Monthly Eval Lab | spec definido · ejecucion pendiente | primer ciclo mes 1 post poblamiento corpus |

---

## Riesgos arquitectonicos a vigilar

1. **Ledger sin enforcement:** implementacion del schema v1.3 sin que el Engine valide los campos = teatro de governance. Mitigacion: rule de integridad #1 en SPEC_LLM_ROUTING v1.3.
2. **Pin estancado sin torneo:** sin disciplina mensual, pins se vuelven dogma y perdemos ahorros. Mitigacion: trigger calendarico + automatizacion del Eval Lab.
3. **Golden corpus desactualizado:** golden_case con datos 2025 evaluando modelos 2027. Mitigacion: refresh trigger en ENT_AI_GOV_GOLDEN_CORPUS_MWT (ver ese archivo).
4. **Skill bloat:** instalar 30 skills externas sin contrato satura context y mata trigger precision. Mitigacion: POL_AI_GOV_SKILL_INSTALLATION lifecycle obligatorio.
5. **Cost-mode opt-in eterno:** override sin expiracion = privacy leak normalizado. Mitigacion: TTL 90 dias hardcoded en POL_AI_GOV_DATA_CLASS_PROVIDER §F.

---

## Lo que esto NO es

- No es un firewall LLM — es governance de routing.
- No es seleccion de proveedor — eso lo hace el Dispatcher tecnico.
- No reemplaza POL_DATA_CLASSIFICATION — la consume y aplica al routing.
- No es teorico: cada policy y entidad de AI_GOV es ejecutable via campos del Token Ledger v1.3.

---

## Implementacion por fases

| Fase | Que entrega | Cuando |
|------|-------------|--------|
| **F0 — Canonizacion** | 6 archivos AI_GOV + extension SPEC_LLM_ROUTING v1.3 | 2026-05-01 (este sprint) |
| **F1 — Enforcement basico** | Action Engine consulta POL_AI_GOV_DATA_CLASS_PROVIDER antes de despachar; Token Ledger captura campos governance | sem 3-5 roadmap Action Engine |
| **F2 — Final Pass policy en runtime** | Hookpoint en final pass dispatcher; SCH_AI_GOV_HANDOFF_DRAFT activo | sem 5-7 |
| **F3 — Output Pins** | Pin candidates capturados; short-circuit por gold sample activo | sem 7-9 |
| **F4 — Eval Lab mensual** | Primer ciclo de torneo con golden corpus poblado | mes 3 post F3 |
| **F5 — Cost dashboard** | Reportes mensuales por skill/agente/org desde Token Ledger | post F4 |

---

Changelog:
- v1.1 (2026-05-01): +Componente 6 Dual Review para decisiones técnicas (PLB_AI_GOV_DUAL_REVIEW + SCH_AI_GOV_DUAL_REVIEW_OUTPUT). Renumera Eval Lab a componente 7. Refs en header. Origen: sesión AI_GOV dual review 2026-05-01 (idea CEO).
- v1.0 (2026-05-01): Creacion. SPEC madre del subsistema AI_GOV. Atado de 3 POLs + 1 SCH + 2 ENTs sobre la capa tecnica de SPEC_LLM_ROUTING v1.3. Cadena ejecutable explicita. Reglas inquebrantables (8). Roadmap por fases F0-F5. Origen: sesion AI_GOV 2026-05-01 (Cowork + ChatGPT cross-validation).
