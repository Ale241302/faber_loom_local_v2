# SPEC_LLM_ROUTING_ARCHITECTURE — Arquitectura de Routing LLM
id: SPEC_LLM_ROUTING_ARCHITECTURE
version: 1.3
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SPEC
stamp: VIGENTE — 2026-05-01
aprobador: CEO
aplica_a: [MWT, FaberLoom]
subcomponente_de: SPEC_ACTION_ENGINE.md (post v1.2 — el L1/L2/L3 vive dentro del Action Engine como Routing Policy)
gobernado_por: SPEC_AI_GOV_GOVERNANCE_AND_ROUTING.md (la capa AI_GOV gobierna; este SPEC ejecuta)
relacionado: SPEC_ACTION_ENGINE.md · SPEC_QUERY_PROCESSING_PIPELINE.md (expande Fase 6) · SPEC_AUTONOMY_CONTROL_ENGINE.md (RequestOutcomeEntry) · SPEC_AUDIT_MODULE.md (audit_event) · ARCH_AGENT_PRINCIPLES.md (P13, P14) · docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md (I-RUFLO-05, I-RUFLO-06, I-RUFLO-09) · ENT_PLAT_ACTION_REGISTRY.md · POL_AI_GOV_DATA_CLASS_PROVIDER.md · ENT_AI_GOV_OUTPUT_PINS.md

---

## Declaración

**Post v1.2 (2026-04-28):** Este SPEC define el **subsistema L1/L2/L3** que vive **dentro del Action Engine** (ver `SPEC_ACTION_ENGINE.md`). Las capas L1-L3 ahora son la Routing Policy aplicada por el Engine cuando `action_category == llm_provider`. El contrato API público para invocar un LLM es `action_engine.execute(intent="llm_call", ...)`, no un cliente directo a LiteLLM.

Toda llamada a un LLM en MWT/FaberLoom pasa por tres capas en secuencia antes de
ejecutarse. Estas capas determinan qué información procesar, qué modelo(s) llamar,
y cómo empacar el prompt para ese modelo específico.

Sin estas capas el sistema es funcional pero ciego al costo y sordo al quality.

```
[Contexto ensamblado — Fase 5 del pipeline]
              ↓
   ┌──────────────────────┐
   │  L1 — CLASIFICADOR   │  qué tipo de tarea, qué complejidad
   └──────────────────────┘
              ↓
   ┌──────────────────────┐
   │  L2 — DISPATCHER     │  qué modelo/s, en qué modo
   └──────────────────────┘
              ↓
   ┌──────────────────────┐
   │  L3 — COMPILER       │  cómo empacar para ese modelo
   └──────────────────────┘
              ↓
   [Llamada(s) API — Fase 6 del pipeline]
              ↓
   ┌──────────────────────┐
   │  TOKEN LEDGER        │  contabilidad cruzada + feedback loop
   └──────────────────────┘
```

---

## L1 — Clasificador de Tarea

### Responsabilidad
Antes de cargar contexto caro o llamar modelo capaz, un modelo barato clasifica
la tarea entrante. Es el portero del sistema.

### Inputs
- Consulta cruda del usuario
- Trigger word detectado (si existe)
- Metadata de sesión (canal, org, historial reciente)

### Outputs
```
task_type:      [copy | forecast | research | qa | classification | code | creative | ...]
complexity:     [low | medium | high | critical]
required_caps:  [reasoning | multilingual | vision | code | long_context | ...]
confidence:     float 0-1
ambiguous:      bool  → si true, preguntar antes de continuar
estimated_tokens: int → estimación antes de ensamblar contexto completo
```

### Modelo usado
Haiku o Gemini Flash. El clasificador nunca usa un modelo caro — eso anularía
el propósito de la capa.

### Regla de escalación
Si `confidence < 0.6` → preguntar al usuario antes de proceder.
Si `ambiguous = true` → no continuar al Dispatcher hasta resolver.

---

## L2 — Dispatcher

### Responsabilidad
Con la clasificación de L1, decide qué modelo(s) llamar y en qué modo.
Combina tres fuentes de información: Arena Feed, Cost Oracle, y Token Ledger propio.

### Componentes internos

**Arena Feed**
Ranking de modelos por tipo de tarea, actualizado periódicamente.
Fuente externa: LMSys Chatbot Arena, Artificial Analysis.
Fuente interna (preferida con el tiempo): Token Ledger propio.
Cache recomendado: 7 días. No consultar en tiempo real por cada request.

```
arena_rankings = {
  reasoning:     [o3, claude-opus, gemini-pro, ...],
  multilingual:  [claude-sonnet, gpt-4o, gemini-flash, ...],
  code:          [claude-sonnet, gpt-4o, deepseek, ...],
  copy_latam:    [ranking propio basado en approval_rate por org]
}
```

**Cost Oracle**
Precio actual input/output por token por proveedor.
Actualizar semanalmente o al detectar cambio de pricing.

```
cost_oracle = {
  claude-haiku:   {input: 0.80, output: 4.00},    # USD/M tokens
  claude-sonnet:  {input: 3.00, output: 15.00},
  claude-opus:    {input: 15.00, output: 75.00},
  gpt-4o-mini:    {input: 0.15, output: 0.60},
  gpt-4o:         {input: 2.50, output: 10.00},
  gemini-flash:   {input: 0.075, output: 0.30},
  gemini-pro:     {input: 1.25, output: 5.00}
}
```

**Task→Model Mapper**
Combina Arena ranking + Cost Oracle + task_type + complexity para producir
candidatos ordenados por score = quality_rank × (1 / costo_estimado).

### Modos de dispatch

| Modo | Cuándo activar | Lógica |
|------|---------------|--------|
| **SINGLE** | complexity=low/medium, patrón conocido, gold sample disponible | El más barato que supera quality bar para ese task_type |
| **DUAL** | complexity=high, tarea fina, primera vez sin gold sample | 2 modelos en paralelo → judge model (barato) selecciona mejor output |
| **ENSEMBLE** | complexity=critical, decisión irreversible, alta ambigüedad | 3 modelos → consensus si ≥2 coinciden, judge si divergen, escala a humano si empate |

**Regla de gold sample shortcut:**
Si existe gold sample con similarity ≥ 0.85 para esta consulta → modo SINGLE
forzado con el modelo más barato. El gold sample actúa como guardia de calidad.

**Regla de presupuesto:**
Si `estimated_tokens × cost_oracle[modelo] > org_budget_per_query` →
degradar modo o degradar modelo antes de ejecutar.

### Salida del Dispatcher
```
dispatch_plan = {
  mode:    "single" | "dual" | "ensemble",
  models:  ["claude-sonnet-4-6"],  // lista de 1-3 modelos
  judge:   "claude-haiku",         // modelo de selección si mode != single
  estimated_cost_usd: float,
  reason:  string                  // para audit trail
}
```

---

## L3 — Prompt Compiler

### Responsabilidad
El mismo contexto ensamblado se empaca de forma diferente según el modelo destino.
El contenido no cambia. El formato, orden, y estructura sí.

### Por qué importa
Un prompt optimizado para Claude mandado a Gemini puede perder 20-30% de quality
no por el modelo sino por el formato. El Compiler elimina esa pérdida.

### Model Profiles

| Atributo | Claude | GPT-4o | Gemini |
|----------|--------|--------|--------|
| System prompt | Role separado vía API | System message | System instruction |
| Chain-of-thought | Implícito funciona | Explícito rinde más | Explícito obligatorio |
| Instrucciones | Prosa larga OK | Bullets más efectivos | Más corto = mejor |
| Orden de contexto | Datos primero, instrucción después | Instrucción primero | Mixto según tarea |
| Few-shot | 1-2 ejemplos óptimo | 3-5 ejemplos | 2-3 ejemplos |
| XML tags | Comprende y usa bien | Ignora parcialmente | Ignora |
| Idioma instrucción | Español nativo OK | Español OK | Mejor en inglés para instrucciones técnicas |
| Context window óptimo | Hasta 200k eficiente | Hasta 128k | Hasta 1M pero quality baja en extremos |

### Operación del Compiler

```
compile(context_assembled, target_model) → prompt_compiled

Pasos:
1. Cargar model_profile[target_model]
2. Restructurar secciones según context_order del profile
3. Convertir XML tags si el modelo no los procesa (Claude → otros)
4. Seleccionar few-shot: gold_samples filtrando por style_match[target_model]
5. Inyectar CoT scaffolding si model_profile.cot = "explicit"
6. Comprimir al token_budget[target_model] priorizando:
   constraints > skill_instructions > gold_samples > kb_context > history
7. Agregar output_format en el idioma/estructura que el modelo procesa mejor
8. Registrar prompt_version en Token Ledger
```

### Few-shot Selector
Los gold samples se etiquetan con `model_affinity[]` basado en histórico de
approval_rate por modelo. El Compiler prefiere gold samples que han funcionado
bien con el modelo destino.

```
gold_sample.model_affinity = {
  "claude-sonnet": 0.91,
  "gpt-4o":        0.78,
  "gemini-pro":    0.65
}
```

---

## Token Ledger

### Responsabilidad
Contabilidad cruzada de toda llamada LLM. Es la única fuente de verdad sobre
costo real, quality real, y eficiencia real del routing.

### Schema por registro (v1.3 — extendido con campos de governance)

```
ledger_entry = {
  entry_id:         uuid,
  org_id:           string,
  brand_scope:      "MWT" | "FaberLoom",
  agent_id:         string,
  skill_id:         string,
  task_type:        string,
  complexity:       string,
  role:             "orchestrator" | "carpintero" | "final_pass" | "judge",
  parent_request_id: uuid,           // null si es root; reconstruye cadena multi-modelo
  dispatch_mode:    "single" | "dual" | "ensemble",
  models_called:    [string],
  model_selected:   string,          // el que produjo el output final
  prompt_version:   string,          // hash del compiled prompt
  context_hash:     string,          // hash del contexto inyectado (para repro)
  output_hash:      string,          // hash del output producido
  tokens_input:     {model: int},
  tokens_output:    {model: int},
  tokens_cached:    {model: int},    // prompt caching Anthropic — bajón de costo
  cost_usd:         {model: float},
  cost_total_usd:   float,
  latency_ms:       int,
  outcome:          "approved" | "edited" | "rejected",
  edit_distance:    float,           // 0 = sin cambios, 1 = reescrito
  approval_rate_30d: float,
  arena_rank_used:  string,

  // === Campos de governance (v1.3, AI_GOV) ===
  data_classification:      "N0" | "N1" | "N2" | "N3" | "N4",  // ref POL_DATA_CLASSIFICATION
  data_class_max_in_chain:  "N0" | "N1" | "N2" | "N3" | "N4",  // tier máximo tocado en parent_chain
  provider_policy_version:  string,  // ref POL_AI_GOV_DATA_CLASS_PROVIDER vigente
  provider_allowed_by_policy: bool,  // false ⇒ violación; el Engine debe rechazar antes
  audit_id:                 uuid,    // ref audit_event en SPEC_AUDIT_MODULE
  outcome_entry_id:         uuid,    // ref RequestOutcomeEntry en SPEC_AUTONOMY_CONTROL_ENGINE
  pinned_output_id:         uuid,    // ref ENT_AI_GOV_OUTPUT_PINS si fue pin shortcut
  pin_status:               "none" | "matched" | "challenged" | "demoted",
  final_pass_required:      bool,    // del POL_AI_GOV_FINAL_OUTPUT_QUALITY
  final_pass_executed:      bool,
  final_pass_shortcut_reason: string, // si executed=false: "gold_similarity≥0.90" | "previous_clean" | etc
  budget_caps_applied:      [string], // ["per_skill", "per_org", "per_run"] — qué caps se chequearon
  budget_status:            "within" | "soft_warn" | "hard_cap_hit",

  timestamp:        datetime
}
```

**Reglas de integridad del schema v1.3:**

1. **`provider_allowed_by_policy` debe ser `true` para que el ledger acepte el entry.** Si el Engine intenta loguear un entry con `false`, el entry se rechaza y se emite alerta. No existen entries inválidos en el ledger; el Engine debe haber rechazado antes.

2. **`data_class_max_in_chain` se computa como `MAX(data_classification de todos los entries con mismo `parent_request_id` raíz)`.** Esta es la palanca crítica: un orquestador puede ser un proveedor sin DPA solo si su `data_classification` es N0/N1, y el `data_class_max_in_chain` de sus carpinteros queda registrado pero NO se filtra hacia el orquestador.

3. **`pinned_output_id` no nulo implica `pin_status = "matched"` y short-circuit del Dispatcher.** Si el pin existe pero `pin_status = "challenged"`, el sistema corrió el modelo pineado contra retador en sandbox; el entry registra cuál ganó.

4. **`outcome_entry_id` se materializa post-hoc** cuando el output llega al gate humano (Fase 7) o al Promotion Engine. Hasta ese momento queda null y se reconcilia.

5. **Chain reconstruction:** una query del usuario puede generar 1..N ledger entries. La cadena se reconstruye con `WHERE parent_request_id = root_id OR entry_id = root_id`. Costo total real del output final = `SUM(cost_total_usd)` de la cadena, no del último entry.

### Por qué estos campos en v1.3

Antes de v1.3 el ledger medía costo y quality, pero no permitía governance ejecutable: no se podía afirmar "esta llamada respetó la política de data class × provider", "este output salió del pin canónico", "este final pass se ejecutó por POL_AI_GOV_FINAL_OUTPUT_QUALITY". Los campos agregados cierran ese gap. Sin ellos, los SPECs y POLs de AI_GOV referencian un sistema de medición sin instrumentación.

### Queries operativas obligatorias

```sql
-- ¿Cuál es el modelo más eficiente para copy_latam este mes?
SELECT model_selected,
       AVG(outcome = 'approved') as approval_rate,
       AVG(cost_total_usd) as avg_cost,
       AVG(approval_rate) / AVG(cost_total_usd) as efficiency_score
WHERE task_type = 'copy_latam'
  AND timestamp > NOW() - INTERVAL 30 DAY
GROUP BY model_selected
ORDER BY efficiency_score DESC;

-- ¿Qué me cuesta realmente por org por mes?
SELECT org_id, SUM(cost_total_usd), COUNT(*), AVG(cost_total_usd)
WHERE timestamp > NOW() - INTERVAL 30 DAY
GROUP BY org_id;

-- ¿El Ensemble vale la pena vs Single en tareas críticas?
SELECT dispatch_mode,
       AVG(outcome = 'approved') as approval_rate,
       AVG(cost_total_usd) as avg_cost
WHERE complexity = 'critical'
GROUP BY dispatch_mode;
```

### Feedback loop al Dispatcher y Compiler

El Token Ledger alimenta dos sistemas con datos propios que superan al Arena Feed
externo con el tiempo:

```
Token Ledger
    ↓
[approval_rate × (1/cost)] por modelo por task_type por org
    ↓
Dispatcher.arena_feed_internal ← actualiza rankings propios
Compiler.gold_sample.model_affinity ← actualiza afinidad por modelo
```

Con 30-60 días de datos, el sistema ya ruteará mejor que cualquier benchmark
externo porque conoce el mix real de tareas y el estilo de aprobación real de
cada organización.

---

## Integración en el Pipeline

Este documento expande la **Fase 6 — Generación** de SPEC_QUERY_PROCESSING_PIPELINE:

```
Fase 5 (Ensamblaje) → L1 Clasificador → L2 Dispatcher → L3 Compiler → API call(s) → Token Ledger → Fase 7 (Gate humano)
```

Las capas L0-L7 de optimización de costo (SPEC_QUERY_PROCESSING_PIPELINE §costos)
y estas tres capas de routing son complementarias:

- L0-L7 reducen cuánto contexto entra al pipeline
- L1-L3 optimizan qué modelo procesa ese contexto y cómo

---

## Lo que esto NO es

- No es un A/B test de modelos — es routing determinístico por evidencia
- No es vendor lock-in en reversa — el sistema es agnóstico al proveedor por diseño
- No es complejidad gratuita — sin esto, el costo escala linealmente con el uso;
  con esto, escala sublinealmente

---

## Implementación por etapas

| Etapa | Qué implementar | Cuándo |
|-------|----------------|--------|
| MVP | L2 estático (router fijo por complexity) + Token Ledger básico + Tier 0 deterministic pre-filter (P14) | Desde día 1 |
| v1.1 | L1 clasificador con Haiku + L3 Compiler para Claude y GPT-4o | Primer mes |
| v1.2 | Arena Feed externo + Cost Oracle automatizado | Mes 2 |
| v2.0 | Modo DUAL/ENSEMBLE + Arena Feed interno desde Ledger | Mes 3-4 |
| v2.1 | Bandit adaptive (epsilon-greedy decay) + ModelFingerprint as routing feature | Mes 5-6 (trigger: >3,000 req/día × 14 días) |

---

## Tier 0 — Deterministic First (post Kimi #3 Ruflo, ARCH_AGENT_PRINCIPLES P14)

Antes del L1 Haiku, todo request pasa por un middleware determinístico que resuelve
60-80% de tasks simples sin invocar ningún LLM. Implementación: `tier0.py` middleware
FastAPI + LiteLLM pre-call hooks + Pydantic validation.

```
[Request entrante]
       ↓
┌──────────────────────┐
│  Tier 0              │  regex + parsers XML LATAM + Pydantic validation
│  (NUEVO desde v1.1)  │  latencia: 5-50 μs · costo: $0
└──────────────────────┘
       ↓ (si confidence < threshold o caso no cubierto)
┌──────────────────────┐
│  L1 — Clasificador   │  Haiku 4.5 — qué tipo de tarea, qué complejidad
└──────────────────────┘
       ↓
┌──────────────────────┐
│  L2 — Dispatcher     │  selecciona modelo por task_type + complexity + cost
└──────────────────────┘
       ↓
┌──────────────────────┐
│  L3 — Prompt Compiler│  empaca prompt para el modelo elegido
└──────────────────────┘
```

Ver detalle en `SPEC_FABERLOOM_MVP §Tier 0 obligatorio` y `ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO §I-RUFLO-01`.

---

## ModelFingerprint como feature de routing (extensión v2.1)

ModelFingerprint nació como gate de probation cross-modelo (P13). Post Kimi #3 Ruflo
(I-RUFLO-05), también es **feature de routing**. Un mismo objeto sirve dos propósitos
sin duplicación de infraestructura.

### Endpoint interno

```
GET /model/similarity?model_a={hash}&model_b={hash}
→ {
    cosine_similarity: 0.84,
    transfer_history: true,
    discount_factor: 0.5,    // similitud ≥0.8 → transferir con descuento
    cold_start: false        // similitud <0.2 → cold start obligatorio
  }
```

### Reglas de transferencia (basadas en research Scope, DFPE, Behavioral Fingerprint)

| Cosine similarity | Acción del routing | Acción de probation |
|---|---|---|
| ≥ 0.80 | Transferir histórico de modelo A → B con descuento 0.5 | Mantener nivel actual con probation 50% |
| 0.20-0.80 | Mezcla parcial — usar histórico solo como prior débil | Probation hasta revalidación por bucket |
| < 0.20 | Cold start obligatorio — el modelo es "nuevo" | Reset a Nivel 1 |

### Implementación

ModelFingerprint = vector embedding 384-dim del comportamiento del modelo ante un
conjunto de queries ancla validación (fuente: DFPE ACL 2026, Scope arXiv). Construido
con sentence embeddings promediados sobre N=250 anchors estratégicamente distribuidos.

**MVP:** ModelFingerprint solo se usa como gate de probation (P13). El endpoint
`/model/similarity` se expone pero el bandit no lo consume todavía.

**v2.1:** el bandit consume `cosine_similarity` como feature adicional para evitar
cold start cuando llega un modelo nuevo de la misma familia (ej. Sonnet 4.5 → 4.6).

---

## Granularidad de aprendizaje: global por task_type, NO per-org

Tensión arquitectónica entre seguridad (per-org RLS, P13) y aprendizaje (datos sparse
per-org). La solución es separar dos sistemas ortogonales (ver `ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO §I-RUFLO-09`):

| Sistema | Granularidad | Por qué |
|---|---|---|
| RLS de seguridad | per-org | Aislamiento, compliance, garantía multi-tenant (P13) |
| Routing aprendido | global por task_type | Datos per-org son sparse en MVP; task_type es feature más informativa (GreenServ ablation) |

**Anti-patrón prohibido:** agregar `org_id` como feature directa del bandit. Fragmenta
datos, degrada convergencia, y duplica el trabajo del RLS sin beneficio.

**Features de routing autorizadas (v2.1):**
- `task_type` (ej. "cobranza_extraccion_monto", "proforma_clasificacion")
- `complexity_score` (0..1, derivado de L1)
- `query_embedding` (384-dim, opcional, prior débil)
- `ModelFingerprint_similarity` (cuando llega modelo nuevo)

**Features prohibidas:** `org_id`, `user_id`, cualquier identificador per-tenant.

---

## L1 — Feature set candidato (FG-03 sesion Fugu 2026-06-24)

Features para clasificar cuando orquestar vs resolver directo (validados por Fugu):

task_type_confidence, schema_parse_success, num_documents, num_counterparties,
jurisdiction_count, data_class, tenant_risk_tier, estimated_tokens,
expected_latency, business_value, validator_failure_count,
prior_case_similarity, requires_human_gate

Heuristica single-model: confianza alta + schema parseable + pocos docs + SLA ajustado.
Heuristica orquestar: multi-doc + evidencia conflictiva + alto valor + validador fallo.
Ref: ENT_FABERLOOM_INSIGHTS_FUGU_SESSION FG-03.

---

Changelog:
- v1.4 (2026-06-24): +L1 feature set candidato 13 features (FG-03 sesion Fugu).
- - v1.3 (2026-05-01): +Token Ledger schema extendido con campos de governance AI_GOV (data_classification, data_class_max_in_chain, provider_policy_version, provider_allowed_by_policy, audit_id, outcome_entry_id, pinned_output_id, pin_status, final_pass_required, final_pass_executed, budget_caps_applied, budget_status, role, parent_request_id, context_hash, output_hash, tokens_cached, brand_scope). +5 reglas de integridad. +Header `gobernado_por: SPEC_AI_GOV_GOVERNANCE_AND_ROUTING.md`. Razón: governance ejecutable requiere instrumentación; sin estos campos los POLs y SPECs de AI_GOV referencian sistema sin telemetría. Origen: sesión arquitectónica AI_GOV 2026-05-01 (Cowork + ChatGPT cross-validation). Ver MANIFIESTO_APPEND_20260501_AI_GOV.md.
- v1.2 (2026-04-28): Marcado como **subcomponente del Action Engine** (ver SPEC_ACTION_ENGINE.md). El L1/L2/L3 sigue válido pero ahora ejecuta dentro del Engine como Routing Policy para `action_category == llm_provider`. Origen: decisión arquitectónica D (contract-first) sesión 2026-04-28.
- v1.1 (2026-04-27): +Tier 0 deterministic pre-filter (P14) en pipeline. +Sección "ModelFingerprint como feature de routing" (reframing dual-purpose: probation + routing). +Sección "Granularidad de aprendizaje: global por task_type". v2.1 etapa actualizada (bandit adaptive con trigger volumen). Origen: Kimi #3 Ruflo (I-RUFLO-05, I-RUFLO-06, I-RUFLO-09). Ver docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md.
- v1.0 (2026-04-17): Creación. L1 Clasificador + L2 Dispatcher + L3 Prompt Compiler + Token Ledger. Pipeline 3 capas + Arena Feed.
