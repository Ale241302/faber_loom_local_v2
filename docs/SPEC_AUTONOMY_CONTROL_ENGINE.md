# SPEC_AUTONOMY_CONTROL_ENGINE — Motor de Control de Autonomía
id: SPEC_AUTONOMY_CONTROL_ENGINE
version: 1.2
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SPEC
stamp: VIGENTE — 2026-04-27
aprobador: CEO
aplica_a: [MWT, FaberLoom]
relacionado: ARCH_AGENT_PRINCIPLES.md (P4, P13, P14) · SPEC_LLM_ROUTING_ARCHITECTURE.md · docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md (I-RUFLO-05, I-RUFLO-06)

---

## Declaración

La autonomía de un agente no es un nivel único — es una función de tres variables:

```
autonomía efectiva = nivel × action_class × environment_fingerprint
```

El agente propone acciones. El control layer adjudica el impacto.
Esa separación es el principio más importante de este documento.

---

## Primitivos Core

### ImpactVector

Reemplaza la clasificación binaria interno/externo.
Cada acción tiene un vector de 8 dimensiones computado por el control layer,
no declarado por el agente.

```typescript
type ImpactVector = {
  customer_visible:        number;  // 0..1
  external_side_effect:    number;  // 0..1
  reversibility:           number;  // 0..1  (1 = irreversible)
  blast_radius:            number;  // 0..1
  financial_risk:          number;  // 0..1
  legal_risk:              number;  // 0..1
  data_sensitivity:        number;  // 0..1
  operational_criticality: number;  // 0..1
  downstream_unknown:      boolean;
};
```

### ActionSpec

Cada tipo de acción tiene su spec declarado en el sistema — no inferido en runtime.

```typescript
type ActionSpec = {
  action_type:       string;        // "crm.update_field" | "email.send" | ...
  target_resource:   string;        // "deal.stage" | "client.email" | ...
  direct_impact:     ImpactVector;
  downstream_edges:  string[];      // refs al trigger graph
  preconditions:     string[];
  postconditions:    string[];
  allowed_levels:    (1|2|3|4)[];
};
```

### TriggerEdge

Registro de efectos downstream. Si una acción dispara algo en otro sistema,
ese efecto es un TriggerEdge con su propio ImpactVector.

```typescript
type TriggerEdge = {
  edge_id:          string;
  from_action_type: string;
  condition_ref:    string;       // id del workflow/automation/rule
  to_effect:        ImpactVector;
  known:            boolean;      // false = tratar como downstream_unknown
};
```

### ModelFingerprint

La autonomía es válida solo para un fingerprint específico.
Cambio de cualquier componente → probation inmediata.

```typescript
type ModelFingerprint = {
  provider:                string;
  model_family:            string;
  model_version:           string;
  system_prompt_hash:      string;
  tools_manifest_hash:     string;
  policy_version:          string;
  retrieval_index_version: string;
};
```

---

## Cómputo de Impacto Efectivo

El impacto efectivo incluye el impacto directo de la acción MÁS todos los
efectos downstream alcanzables via trigger graph.

```
impact_efectivo = direct_impact
                + max(downstream_effects)
                + uncertainty_penalty si downstream_unknown = true
```

**Weights por dimensión:**

| Dimensión | Weight |
|-----------|--------|
| customer_visible | 0.20 |
| external_side_effect | 0.15 |
| reversibility | 0.15 |
| blast_radius | 0.15 |
| financial_risk | 0.10 |
| legal_risk | 0.10 |
| data_sensitivity | 0.10 |
| operational_criticality | 0.05 |

Si `downstream_unknown = true` → impact floor = 0.65 (conservador siempre).

**Gates por nivel:**

| Nivel | Impact máximo permitido | Condiciones adicionales |
|-------|------------------------|------------------------|
| 1 — PROPONE | 0.00 | Solo draft, nunca ejecuta |
| 2 — EJECUTA_INTERNO | 0.20 | downstream_unknown=false · customer_visible≤0.05 · reversibility≤0.20 |
| 3 — AUTO_NOTIFICA | 0.40 | downstream_unknown=false · customer_visible≤0.20 |
| 4 — AUTO_EXCEPCIONES | 0.60 | Solo flujos validados con revalidación activa |

**Regla absoluta para Nivel 2:**
```
downstream_unknown = false
customer_visible   ≤ 0.05
external_side_effect ≤ 0.05
reversibility      ≤ 0.20
financial_risk     = 0
legal_risk         = 0
impact             ≤ 0.20
```

Esto elimina el caso "actualicé un campo CRM que disparó un email al cliente."

---

## Lógica de Escalación

### Hard escalation (inmediata, sin score)

```
policy_conflict = true              → escalar
required_context_missing = true     → escalar
downstream_unknown = true           → escalar
postcondition_check_failed = true   → escalar
customer_visible > 0.20
  AND confidence < 0.97             → escalar
financial_risk > 0.20
  AND confidence < 0.97             → escalar
legal_risk > 0.10
  AND confidence < 0.97             → escalar
effective_impact ≥ 0.40
  AND confidence < 0.90             → escalar
```

### Soft escalation score

Para casos que no caen en hard rules:

```
soft_score =
  0.45 × effective_impact
+ 0.25 × (1 - calibrated_confidence)
+ 0.15 × novelty_score
+ 0.15 × retrieval_conflict

si soft_score ≥ 0.45 → escalar
```

### Degradación silenciosa

**Solo permitida cuando TODOS estos se cumplen:**
```
effective_impact   ≤ 0.10
customer_visible   ≤ 0.05
financial_risk     = 0
legal_risk         = 0
downstream_unknown = false
postcondition_check_failed = false
```

Ejemplos que califican: draft interno, clasificación reversible de bajo riesgo,
resumen, sugerencia de ranking. Para todo lo demás: escalar, no degradar silencioso.

---

## Lógica de Promoción

### El problema que resuelve

Approval rate solo no detecta sandbagging: un agente que escala todo lo difícil
y ejecuta solo lo fácil puede alcanzar 92% approval rate sin merecer subir de nivel.

### Solución: loguear el opportunity set

Registrar CADA oportunidad de actuar autónomamente, no solo las ejecuciones.
El denominador importa tanto como el numerador.

```typescript
type TaskOpportunity = {
  opportunity_id:     string;
  agent_id:           string;
  action_spec_id:     string;
  predicted_difficulty: number;  // 0..1 — asignado por control layer, no agente
  predicted_risk:       number;  // 0..1 — ídem
  eligible_level:       1|2|3|4;
  agent_choice:         "execute" | "escalate" | "propose";
  final_outcome?:       "approved" | "edited" | "rejected" | "incident";
  created_at:           string;
};
```

**Crítico:** difficulty y risk son asignados por el control layer o shadow evaluator.
Si el agente etiqueta sus propias tareas, el examen lo hace el estudiante.

### Métricas derivadas

```
quality_score =
  (approved + 0.5 × edited) / max(1, executed)

coverage_score =
  executed / max(1, eligible_seen)

difficulty_coverage =
  sum_difficulty_executed / max(0.001, sum_difficulty_seen)

low_risk_escape_rate =
  escalated_low_risk / max(1, eligible_low_risk)

suspicious_escalation =
  count(escalate where confidence ≥ 0.85 AND predicted_risk ≤ 0.25)
  / eligible_seen
```

### Criterios de promoción (ejemplo L2 → L3)

```
eligible_seen         ≥ 50
executed_count        ≥ 30
quality_score         ≥ 0.92
coverage_score        ≥ 0.70
difficulty_coverage   ≥ 0.65
low_risk_escape_rate  ≤ 0.15
suspicious_escalation ≤ 0.10
calibration_error     ≤ 0.08
severe_incidents      = 0
```

Por bucket mínimo (más robusto que thresholds globales):
```
≥ 20 ejecuciones low_risk  con quality ≥ 0.92
≥ 15 ejecuciones medium_risk con quality ≥ 0.90
```

Esto impide que el agente acumule oro en tareas fáciles y evite las difíciles.

### Oscillation Counter — Anti-complacencia

La confianza del usuario no debe crecer monotónicamente. Un usuario que aprueba
sin leer no está validando — está generando falsos positivos que inflan el quality_score.

```
oscillation_counter:  int   // se incrementa por cada auto-aprobación consecutiva
oscillation_threshold: int  // default: 20

Si oscillation_counter ≥ oscillation_threshold:
  → la próxima acción del mismo tipo requiere confirmación humana explícita
    aunque effective_impact ≤ ceiling y eligible_level lo permita
  → oscillation_counter = 0
  → log "oscillation_check" en DecisionLog
```

**Por qué importa:** la tasa de éxito de prompt injection en sistemas agenticos es 84%.
Un usuario complaciente que aprueba sin leer es el vector de ataque más fácil.
El oscilador mantiene vivo el loop de verificación sin generar fatiga de decisión.

### HumanAlignmentScore — Calibración Perceptual

Además de la calibración estadística (ECE/Brier), el Promotion Engine trackea
la calibración perceptual: la correlación entre el confidence que el agente reporta
y la probabilidad de que el usuario apruebe.

```
human_alignment_score =
  correlation(agent_confidence, user_approval_rate)
  medido sobre ventana de 30 días

Si agente reporta HIGH confidence pero usuario rechaza 30%+ → desajuste perceptual
Si human_alignment_score < 0.70 → bloquear promoción aunque ECE sea < 0.05
```

Un agente perfectamente calibrado estadísticamente pero que el usuario percibe
como poco confiable no puede escalar. La confianza se construye en ambas dimensiones.

---

## Manejo de Cambio de Modelo (ModelFingerprint)

### Al detectar cambio de fingerprint

```
nivel anterior  →  nivel anterior - 1  (cap inmediato)
estado          →  "probation"
validated_buckets: { low_risk: false, medium_risk: false, high_risk: false }
```

El cap inmediato es conservador pero correcto. Un modelo nuevo puede comportarse
diferente exactamente en los casos que justificaron la promoción anterior.

### Revalidación por bucket

Correr eval offline + shadow sobre set estratificado:

| Bucket | Pass rate requerido | Condición adicional |
|--------|-------------------|-------------------|
| low_risk | ≥ 0.97 | severe_error_rate = 0 |
| medium_risk | ≥ 0.94 | severe_error_rate = 0 |
| high_risk | ≥ 0.98 | severe_error_rate = 0 |

**Regla para Nivel 4:** nunca restaurar solo por historial.
Requiere revalidación completa + compatibility_score ≥ 0.96.

**Casos:**
```
Patch menor mismo modelo, mismo toolchain  → cap nivel-1 hasta revalidación
Nueva familia de modelo                    → reset a Nivel 1 o 2 máx
Cambio de policy que afecta action classes → invalidar solo buckets afectados
```

---

## Task Authorization Model

### El patrón de agente delegado

El usuario no supervisa cada paso. Autoriza una tarea con scope al inicio
y recibe el resultado cuando está listo.

```typescript
type TaskAuthorization = {
  task_id:          string;
  agent_id:         string;
  task_description: string;
  authorized_scope: string[];      // action_types permitidos
  impact_ceiling:   number;        // 0..1 — máximo impacto auto-ejecutable
  escalation_mode:  "async" | "blocking";
  deadline?:        string;
  created_by:       string;
  created_at:       string;
};
```

**Flujo:**
```
Usuario firma TaskAuthorization
        ↓
Agente recibe scope + impact_ceiling
        ↓
Trabaja independientemente
  ├── impact ≤ ceiling         → ejecuta solo
  ├── downstream_unknown       → encola escalación async
  └── impact > ceiling         → encola para aprobación
        ↓
Resultado → Consola de Comunicaciones
```

### Async Escalation Queue

El agente no bloquea al usuario durante la ejecución. Las escalaciones se
encolan con contexto completo. El usuario las resuelve cuando abre la consola.

```typescript
type EscalationPacket = {
  escalation_id:     string;
  task_id:           string;
  agent_id:          string;
  step_context:      string;    // dónde estaba el agente cuando escaló
  action_attempted:  ActionSpec;
  reason_codes:      string[];
  impact_computed:   number;
  options:           EscalationOption[];
  created_at:        string;
  resolved_at?:      string;
  resolution?:       "approved" | "rejected" | "modified";
};

type EscalationOption = {
  label:          string;
  action:         string;
  impact_if_taken: number;
  recommended:    boolean;
};
```

**Crítico:** cada EscalationPacket lleva contexto completo — no solo "necesito
aprobación para X" sino el estado exacto de la tarea, por qué escaló,
y las opciones con su impacto estimado. El usuario aprueba informado, no a ciegas.

### Delivery a Consola de Comunicaciones

El output final del agente llega como paquete estructurado:

```typescript
type TaskDelivery = {
  task_id:           string;
  agent_id:          string;
  status:            "completed" | "partial" | "blocked";
  output:            any;
  actions_taken:     DecisionLog[];   // todo lo que hizo solo
  escalations:       EscalationPacket[]; // las que esperan resolución
  pending_fields:    string[];        // campos marcados [PENDIENTE]
  audit_trail:       string;          // hash del log completo
  delivered_at:      string;
};
```

---

## OutcomeLedger — Tracking de Resultados por Gold Sample

Un gold sample perfectamente recuperado que produce una acción perjudicial en el
contexto actual es peor que no tenerlo. El OutcomeLedger evalúa gold samples por
outcome histórico, no por similitud semántica.

```typescript
type OutcomeEntry = {
  entry_id:        string;
  gold_sample_id:  string;
  agent_id:        string;
  org_id:          string;
  action_taken:    string;
  outcome:         "approved" | "edited" | "rejected";
  edit_distance?:  number;      // 0..1 — qué tan diferente fue la edición
  user_comment?:   string;
  context_hash:    string;      // fingerprint del contexto en que se usó
  created_at:      string;
};

type GoldSampleHealth = {
  gold_sample_id:    string;
  total_uses:        number;
  approval_rate:     number;   // approved / total_uses
  avg_edit_distance: number;
  last_used:         string;
  drift_score:       number;   // 0..1 — contexto actual vs cuando se creó el sample
  status:            "active" | "degrading" | "deprecated";
};
```

**Reglas de salud del gold sample:**

```
approval_rate < 0.60 en últimas 10 uses  → "degrading", notificar al usuario
approval_rate < 0.40 en últimas 5 uses   → "deprecated", retirar del retrieval
drift_score > 0.70                        → forzar re-validación humana antes de usar
avg_edit_distance > 0.40                  → el sample ya no es referencia válida
```

El OutcomeLedger retroalimenta al Promotion Engine: un agente que opera con gold samples
degradados debe ver reducido su quality_score aunque el approval_rate de acciones sea alto.

### Extensión v1.1 — OutcomeLedger como fuente para routing aprendido (Phase 2)

Post Kimi #3 Ruflo (ver `ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO §I-RUFLO-06`): el OutcomeLedger
acumula desde MVP las observaciones que más adelante alimentan el routing aprendido por
bandit. Schema extendido per-request (no per-gold-sample):

```typescript
type RequestOutcomeEntry = {
  request_id:       string;
  org_id:           string;          // RLS por org_id (siempre)
  task_type:        string;          // feature de routing — granularidad GLOBAL, no per-org
  complexity_score: number;          // 0..1 — derivado de L1 Haiku
  model_used:       string;          // ej. "claude-haiku-4-5", "claude-sonnet-4-6"
  prompt_hash:      string;
  response_hash:    string;
  latency_ms:       number;          // señal de recompensa #1
  cost_usd:         number;          // señal de recompensa #2 (vía LiteLLM spend logs)
  user_feedback?:   "approved" | "edited" | "rejected";  // señal #3
  llm_judge_score?: number;          // 0..1, opcional, señal #4
  fingerprint_used: string;          // ModelFingerprint hash usado
  timestamp:        string;
};
```

**Reglas de captura desde MVP día 1:**
- Una fila por cada request, sin agregaciones, máxima flexibilidad de query analítica.
- RLS policy `org_id = current_setting('app.current_org')` aplicada SIEMPRE — seguridad.
- `task_type` global (NO incluye `org_id` como feature) — aprendizaje cross-tenant.
- `fingerprint_used` permite invalidar histórico cuando un modelo cambia (cosine sim <0.2).

**Activación del bandit (Phase 2):** trigger >3,000 req/día × 14 días consecutivos. A
~5,000 pulls/brazo, Thompson Sampling estabiliza. Antes de eso, los datos solo alimentan
priors bayesianos; la decisión sigue siendo rule-based L1/L2.

**Integración con ModelFingerprint:** ver `SPEC_LLM_ROUTING_ARCHITECTURE.md` — el endpoint
`GET /model/similarity` consume RequestOutcomeEntry para decidir si el histórico de un modelo
A se transfiere al modelo B con descuento 0.5 (sim ≥0.8) o se hace cold start (sim <0.2).

---

## UserControlProfile — Calibración de Preferencia de Control

El punto óptimo entre "el agente pregunta demasiado" y "el agente actúa solo demasiado"
es personal por usuario y evoluciona con el tiempo. El UserControlProfile aprende las
preferencias de control de cada usuario como input adicional al ImpactVector.

```typescript
type UserControlProfile = {
  user_id:              string;
  org_id:               string;

  // Patrones observados
  avg_approval_time_ms: number;   // < 3000ms = probablemente no leyó
  fast_approve_rate:    number;   // % aprobaciones < 3 segundos
  edit_rate:            number;   // % veces que edita antes de aprobar
  rejection_rate:       number;

  // Preferencia aprendida por tipo de acción (mínimo 20 samples)
  preferred_autonomy: {
    [action_type: string]: {
      preferred_level: 1 | 2 | 3 | 4;
      confidence:      number;  // 0..1
      sample_size:     number;
    }
  };

  complacency_score: number;   // 0..1 — probabilidad de aprobar sin leer
  last_calibrated:   string;
};
```

**Cómo afecta al control layer:**

```
Si preferred_level confirmado para action_type X con sample_size ≥ 20:
  → ajustar autonomy threshold para ese action_type específico

Si complacency_score > 0.70:
  → activar Oscillation Counter (ver sección anterior)
  → incrementar visibilidad de acciones que normalmente serían silenciosas
  → añadir resumen post-acción obligatorio en Consola de Comunicaciones
```

---

## Shadow Audit Trail (Bootstrapping de Confianza)

Las primeras N ejecuciones de cualquier agente en modo autónomo deben ser
observables. El usuario necesita ver qué hizo el agente antes de confiarle
tareas sin supervisión.

```
Primeras 3 ejecuciones:  shadow completo — log visible de cada decisión
Ejecuciones 4-10:        log resumido disponible bajo demanda
Ejecuciones 10+:         log en audit trail, no visible por default
```

La confianza se construye con evidencia observable, no con promesas.

---

## Integración con ARCH_AGENT_PRINCIPLES

| Principio | Qué implementa este documento |
|-----------|-------------------------------|
| P4 — Autonomía por evidencia | ImpactVector + PromotionWindow + difficulty coverage + HumanAlignmentScore |
| P7 — State machine | CapabilityState con validation_status |
| P8 — Telemetría | TaskOpportunity + DecisionLog + PromotionWindow + OutcomeLedger |
| P9 — Gobernanza embebida | Hard escalation rules + policy gates + Oscillation Counter |
| P13 — Contención | ModelFingerprint binding + garantía multi-tenant |

---

## Secuencia de Implementación

| Etapa | Qué construir | Cuándo |
|-------|--------------|--------|
| MVP | ImpactVector básico + ActionSpec registry + hard escalation rules | Primero |
| v1.1 | TriggerGraph registry por integración | Mes 1 |
| v1.2 | TaskOpportunity logging + promotion engine con difficulty coverage | Mes 2 |
| v1.3 | ModelFingerprint + probation automática | Mes 2-3 |
| v2.0 | Task Authorization + Async Escalation Queue + Delivery a Consola | Mes 3-4 |
| v2.1 | Shadow Audit Trail + bootstrapping UX | Mes 4 |
| v2.2 | OutcomeLedger + GoldSampleHealth + decay automático | Mes 5 |
| v2.3 | UserControlProfile + Oscillation Counter + HumanAlignmentScore | Mes 5-6 |

---

Changelog:
- v1.2 (2026-04-27): +OutcomeLedger v1.1 extension (RequestOutcomeEntry per-request schema para routing aprendido Phase 2). Captura desde MVP día 1 con RLS por org_id, task_type global. Activación bandit con trigger >3,000 req/día × 14 días. Origen: Kimi #3 Ruflo (I-RUFLO-06). Ver docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md.
- v1.1 (2026-04-17): +OutcomeLedger (GoldSampleHealth + decay automático) · +UserControlProfile (preferencia de control por usuario y action_type) · +Oscillation Counter (anti-complacencia, threshold 20) · +HumanAlignmentScore (calibración perceptual junto a ECE/Brier) · Secuencia de implementación 7 etapas.
- v1.0 (creación inicial): ImpactVector + ActionSpec + TriggerEdge + ModelFingerprint + Promotion Engine.