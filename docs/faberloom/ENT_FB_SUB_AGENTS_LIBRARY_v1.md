---
id: ENT_FB_SUB_AGENTS_LIBRARY_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-04-30 (v1.1 post-auditoria R3)
fecha: 2026-04-30
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R3)
aplica_a: [FaberLoom]
implementa: ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1 (P16 Atomic Agents Principle)
relacionado_con:
  - ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1
  - ENT_FB_AGENT_ARCHETYPES_v1
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1 (compliance profiles per vertical)
  - ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1 (severity_weight para kill_criteria)
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1 (v1.1)
  - SPEC_FB_AGENT_BUILDER_v1
  - SPEC_LLM_ROUTING_ARCHITECTURE
  - SPEC_ACTION_ENGINE
---

# ENT_FB_SUB_AGENTS_LIBRARY_v1
## Catalogo inicial de sub-agentes atomicos · scope vertical Account Management B2B

## 1. Proposito

Catalogo de sub-agentes atomicos especializados que componen el archetype principal **AG_AM (Account Manager B2B)**. Cada sub-agente ejecuta una capacidad cognitiva unitaria, es stateless dentro del request, tiene schema I/O contractual, modelo apropiado al task y pool L3 propio en Knowledge River.

Pickeo libre desde el agent builder: el usuario compone su archetype escogiendo del catalogo lo que necesite, sin pre-categorizacion core/vertical (eso emergera con datos cuando aparezca un segundo vertical).

## 2. Scope v1 · 10 sub-agentes para AM B2B

| ID | Modelo | Categoria cognitiva | Stateless | Pool L3 |
|---|---|---|---|---|
| AG_SUB_EMAIL_CLASSIFIER | Haiku 4.5 | Clasificacion N-way | si | si |
| AG_SUB_DRAFT_WRITER | Sonnet 4.6 | Generacion creativa | si | si |
| AG_SUB_PROFORMA_BUILDER | Sonnet 4.6 | Generacion estructurada | si | si |
| AG_SUB_SAP_QUERY | Haiku + tool | Lookup + format | si | no |
| AG_SUB_VOICE_TRANSCRIBER | Whisper | Transcripcion | si | no |
| AG_SUB_PRE_CALL_SUMMARIZER | Haiku 4.5 | Resumen extractivo | si | si |
| AG_SUB_COMPLIANCE_CHECKER | Haiku 4.5 | Reglas binarias | si | si |
| AG_SUB_ESCALATION_ROUTER | deterministic | If/then puro | si | no |
| AG_SUB_PRICING_CALCULATOR | Python puro | Calculo deterministic | si | no |
| AG_SUB_INVENTORY_FETCHER | tool only | API call | si | no |

Pool L3 = recibe destilacion de patterns cross-tenant. NO Pool L3 = sub-agente puramente deterministic o tool-wrapping (no hay nada que aprender via Knowledge River).

---

## 3. Detalle por sub-agente

### 3.1 AG_SUB_EMAIL_CLASSIFIER

**Proposito:** clasificar email inbound de cliente en categorias accionables del AM.

**Modelo:** Claude Haiku 4.5 (clasificacion N-way no requiere Sonnet).

**Trigger:** evento `EMAIL_RECEIVED` desde adapter Gmail/Outlook del tenant.

**Schema input:**
```yaml
email:
  from: string
  to: string
  subject: string
  body_text: string  # plain text, max 8000 chars (truncate front)
  body_html: string?  # opcional
  thread_id: string?
  timestamp: ISO8601
account_context:
  account_id: string
  industry: string  # metalmecanica, agro, construccion, etc
  language_pref: string  # es-MX, es-CO, pt-BR, etc
  recent_threads: array<{thread_id, last_intent, last_status}>  # max 5
```

**Schema output:**
```yaml
classification:
  primary_intent: enum  # quote_request, status_inquiry, complaint, payment_issue, sample_request, follow_up, off_topic, spam
  secondary_intents: array<enum>  # hasta 3
  urgency: enum  # critical, high, normal, low
  sentiment: enum  # positive, neutral, frustrated, angry
  requires_human: boolean
  human_reason: string?  # poblado si requires_human=true
  confidence: float  # 0-1
  language_detected: string
  entities_extracted:
    sku_mentions: array<string>
    quantity_mentions: array<{value, unit, sku_ref?}>
    date_mentions: array<{value, type}>  # delivery_date, payment_due, etc
    monetary_mentions: array<{value, currency}>
trace_id: string  # para audit log
```

**Latency target:** p95 < 1.2s
**Cost target:** < $0.0003 per call (Haiku 4.5 ~1k tokens)
**Pool L3:** si — destila patterns "cuando email tiene X, casi siempre primary_intent es Y" cross-tenant respetando k-anon >=5
**Threshold shadow → active:** 90d con accuracy >=0.85 vs muestreo humano + cero misclasifications criticas (complaint clasificado como off_topic)

**HITL gate:** automatico si `confidence < 0.7` o `requires_human = true` → marca para review manual.

---

### 3.2 AG_SUB_DRAFT_WRITER

**Proposito:** escribir draft de respuesta email basado en clasificacion + contexto de cuenta + politica del tenant.

**Modelo:** Claude Sonnet 4.6 (creatividad + tono justifica el costo).

**Trigger:** invocado por orquestador cuando `classification.primary_intent in {status_inquiry, complaint, follow_up, sample_request}` y `requires_human=false`.

**Schema input:**
```yaml
classification: {output completo de AG_SUB_EMAIL_CLASSIFIER}
account_context:
  account_id: string
  account_name: string
  contact_name: string
  contact_role: string?
  preferred_communication_style: enum  # formal, friendly, direct
  language: string
  open_items: array<{item_id, type, status, last_update}>
template_voice:
  tenant: string  # marluvas, tecmater
  tone_guide: string  # del template del tenant
  banned_phrases: array<string>
  required_signoff: string
recent_thread_summary: string?  # output de AG_SUB_PRE_CALL_SUMMARIZER si aplica
```

**Schema output:**
```yaml
draft:
  subject: string
  body: string  # markdown-ready, idioma de account_context.language
  attachments_suggested: array<{type, reason}>  # ej. catalogo PDF
  internal_note: string  # NO se envia, contexto para el AM humano
  tone_used: enum
  policies_applied: array<string>  # ej. "rana-walk-tone-v1.2", "marluvas-formality-mx"
confidence:
  overall: float
  high_risk_terms_detected: array<{term, reason}>?  # poblado si hay terminos que requieren review
trace_id: string
```

**Latency target:** p95 < 4s
**Cost target:** < $0.018 per draft (Sonnet 4.6 ~3k tokens in + ~1k tokens out)
**Pool L3:** SI — alimentado por TODOS los AM de TODOS los tenants (k-anon >=5). Destila patterns "como abrir respuesta a queja por delay en industria X, idioma Y". Mejora 1 sub-agente = mejora todos los archetypes que lo usan.
**Threshold shadow → active:** 90d con send-rate >=0.6 sin edicion humana sustantiva (>20% del texto cambiado) + cero violaciones de banned_phrases

**HITL gate:** P3 draft-first absoluto. NUNCA envia directo. Siempre va a inbox del AM humano para review.

---

### 3.3 AG_SUB_PROFORMA_BUILDER

**Proposito:** construir proforma estructurada lista para enviar al cliente, integrando line items, pricing, terminos, validez.

**Modelo:** Claude Sonnet 4.6 (estructura compleja + narrativa).

**Trigger:** invocado por orquestador cuando `classification.primary_intent = quote_request` y datos de SAP fueron fetched.

**Schema input:**
```yaml
quote_request:
  parsed_items: array<{sku, quantity, unit, special_terms?}>
  delivery_terms_requested: string?
  payment_terms_requested: string?
  validity_days_requested: int?
sap_data:
  items: array<{sku, description, list_price, currency, available_stock, lead_time_days, weight_kg}>
  account_credit_limit: number
  account_payment_terms_default: string
  applicable_discounts: array<{type, percent, condition}>
pricing_calc:
  output completo de AG_SUB_PRICING_CALCULATOR
template_voice: {ver AG_SUB_DRAFT_WRITER}
account_context: {ver AG_SUB_DRAFT_WRITER}
```

**Schema output:**
```yaml
proforma:
  proforma_number_provisional: string  # ej. "PF-MWT-2026-04-XXXX-DRAFT"
  account_block:
    company: string
    contact: string
    address: string
    tax_id: string
  items_table: array<{sku, description, quantity, unit_price, line_total, lead_time}>
  totals:
    subtotal: number
    discount_total: number
    iva: number?
    grand_total: number
    currency: string
  terms_block:
    payment_terms: string
    delivery_terms: string
    validity: string  # ej. "30 dias"
    incoterm: string?
    warranty: string?
  cover_letter: string  # narrativa que acompana la proforma
  attachments_required: array<{type, ref}>  # PDF tecnico, ficha SKU, etc
warnings: array<{level, code, message}>  # ej. "credito_limite_exceeded", "stock_insuficiente_lead_+30d"
trace_id: string
```

**Latency target:** p95 < 6s
**Cost target:** < $0.025 per proforma (Sonnet 4.6 ~5k tokens in + ~1.5k tokens out)
**Pool L3:** SI — destila patterns de cover_letter exitoso por industria/tenant
**Threshold shadow → active:** 90d con close-rate de proforma generada >= close-rate baseline humano + cero proformas con warnings.level=critical sin override humano

**HITL gate:** SIEMPRE. La proforma propuesta va a draft state — el AM humano ajusta y envia.

---

### 3.4 AG_SUB_SAP_QUERY

**Proposito:** wrapper estructurado sobre SAP Business One / SAP S/4HANA del tenant. Solo formatea params y parsea response.

**Modelo:** Claude Haiku 4.5 + SAP API tool (no necesita razonamiento, solo orquestar tool call).

**Trigger:** invocado por orquestador cuando se necesita data ERP (stock, pricing master, account credit, payment history).

**Schema input:**
```yaml
query_type: enum  # stock_by_sku, pricing_master, account_credit, payment_history, lead_time
params:
  skus: array<string>?
  account_id: string?
  date_range: {from, to}?
  warehouse: string?
tenant_sap_config:
  endpoint: string  # del config del tenant
  auth_token_ref: string  # referencia a vault, NO el token
  api_version: string
```

**Schema output:**
```yaml
sap_response:
  query_type: enum  # mismo que input
  data: object  # shape depende de query_type
  freshness_seconds: int  # antiguedad del cache si aplica
  source: enum  # live, cache_5min, cache_1h
errors: array<{code, message, retryable}>?
trace_id: string
```

**Latency target:** p95 < 2s (incluye round-trip SAP)
**Cost target:** < $0.0008 per call (Haiku ~500 tokens + tool overhead)
**Pool L3:** NO (puro lookup, no hay patterns que destilar)
**Threshold shadow → active:** 30d sin error rate >2%

**HITL gate:** ninguno (read-only). Si SAP devuelve error fatal, sube exception al orquestador.

---

### 3.5 AG_SUB_VOICE_TRANSCRIBER

**Proposito:** transcribir grabaciones de llamada cliente↔AM con timestamps y diarization.

**Modelo:** Whisper large-v3 (no LLM Anthropic, no requerido).

**Trigger:** evento `CALL_RECORDING_UPLOADED` desde adapter de telefonia (Twilio Voice, Aircall, etc).

**Schema input:**
```yaml
audio:
  url_signed: string  # URL firmada con expiracion 1h
  format: enum  # mp3, wav, opus
  duration_seconds: int
  language_hint: string?  # es-MX, pt-BR
diarization_required: boolean  # default true
participants_count_expected: int?  # default 2
```

**Schema output:**
```yaml
transcript:
  full_text: string
  segments: array<{speaker_id, start_ms, end_ms, text, confidence}>
  language_detected: string
  speakers_identified: int  # cuantos hablantes diferenciados
  total_duration_seconds: int
quality_metrics:
  avg_confidence: float
  silence_percent: float
  overlap_percent: float  # cuando 2 speakers hablaron al mismo tiempo
trace_id: string
```

**Latency target:** p95 < 30s para audio de 10min (asincrono — no bloquea orquestador)
**Cost target:** ~$0.006 per minuto de audio
**Pool L3:** NO (Whisper no es Anthropic, fine-tuning fuera de scope v1)
**Threshold shadow → active:** 30d con avg_confidence >=0.85 en muestreo

**HITL gate:** ninguno (transcripcion no es accion). Output pasa directo a AG_SUB_PRE_CALL_SUMMARIZER si aplica.

---

### 3.6 AG_SUB_PRE_CALL_SUMMARIZER

**Proposito:** generar 1-pager resumen de cuenta antes de una llamada agendada (24h antes), sintesis de ultimas interacciones + items abiertos + topicos sugeridos.

**Modelo:** Claude Haiku 4.5 (resumen extractivo, no requiere Sonnet).

**Trigger:** scheduled task — 24h antes de cada calendar event con tag `CLIENT_CALL`.

**Schema input:**
```yaml
account_id: string
call_metadata:
  scheduled_at: ISO8601
  duration_planned_minutes: int
  attendees: array<{email, name, role}>
  agenda_provided: string?
historical_data:
  emails_last_90d: array<{thread_id, date, intent_summary, status}>
  proformas_last_90d: array<{number, date, status, total, currency}>
  calls_last_90d: array<{date, summary, action_items, outcome}>
  open_items: array<{item_id, type, status, age_days}>
  payment_history_summary: object  # {on_time_rate, avg_days_late, last_overdue_amount}
```

**Schema output:**
```yaml
pre_call_summary:
  account_snapshot:  # 1 parrafo
    text: string
  recent_activity:  # bullets
    items: array<string>
  open_items_critical: array<{item_id, summary, days_open, recommended_action}>
  suggested_topics: array<{topic, rationale, priority}>
  risks_to_mention: array<{risk, severity, mitigation_idea}>
  positive_signals: array<string>  # algo bueno que reconocer
key_metrics_card:
  revenue_ytd: number
  revenue_last_year: number
  growth_yoy_percent: float
  payment_health: enum  # green, yellow, red
trace_id: string
```

**Latency target:** p95 < 3s (asincrono — pre-genera la noche anterior)
**Cost target:** < $0.002 per resumen (Haiku ~3k tokens in + ~500 tokens out)
**Pool L3:** SI — destila patterns "cuando cuenta tiene X firma Y, suggested_topics ganadores son Z"
**Threshold shadow → active:** 60d con accept-rate del AM >=0.7 (AM no descarta el summary)

**HITL gate:** ninguno (read-only para el AM). El AM lee y decide que hacer.

---

### 3.7 AG_SUB_COMPLIANCE_CHECKER

**Proposito:** validar draft outbound contra reglas de compliance (LFPDPPP MX, LGPD BR, ISO27001, politicas internas del tenant) antes de send.

**Modelo:** Claude Haiku 4.5 (reglas binarias, pattern matching estructurado).

**Trigger:** invocado por orquestador antes de cada `SEND_INTENT` (email, attachment, contract).

**Schema input:**
```yaml
content_to_check:
  type: enum  # email, attachment, contract, post
  subject: string?
  body: string
  attachments: array<{filename, hash, content_text?}>?
context:
  tenant: string
  jurisdictions_applicable: array<string>  # ej. [MX, CR, CO]
  recipient_type: enum  # client, prospect, internal, vendor
  data_classification_required: enum  # de POL_DATA_CLASSIFICATION (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED)
rules_to_apply:
  policies: array<string>  # refs a POL_DATA_CLASSIFICATION, POL_LFPDPPP_v1, etc
```

**Schema output:**
```yaml
check_result:
  pass: boolean
  warnings: array<{level, code, message, location}>  # level: info, low, medium
  blocking_issues: array<{level, code, message, location, fix_suggestion}>  # level: high, critical
  pii_detected: array<{type, location, redaction_suggested}>  # email, phone, RFC, CURP, CPF, address
  policies_violated: array<{policy_id, rule_id, severity}>
trace_id: string
```

**Latency target:** p95 < 1s
**Cost target:** < $0.0005 per check
**Pool L3:** SI — destila patterns "frases que casi siempre disparan blocking_issues" para flagging temprano en AG_SUB_DRAFT_WRITER
**Threshold shadow → active:** 90d con cero false negatives en muestreo (nunca aprobar algo que era blocking) — false positives tolerables hasta 10%

**HITL gate:** si `blocking_issues != []` el orquestador NO procede con el send. Marca el draft como BLOCKED y notifica al AM con razon + fix sugerido.

---

### 3.8 AG_SUB_ESCALATION_ROUTER

**Proposito:** decidir a quien escalar segun tipo de incidente. NO usa LLM — es decision tree explicito mantenido en YAML del tenant.

**Modelo:** deterministic (Python + YAML rules). Documentado aqui porque es invocable desde el orquestador igual que un sub-agente LLM.

**Trigger:** invocado cuando `requires_human=true` o cuando otro sub-agente devuelve `needs_escalation`.

**Schema input:**
```yaml
incident:
  type: enum  # complaint, payment_overdue, legal_threat, technical_issue, vip_request, compliance_block, billing_dispute
  severity: enum  # low, medium, high, critical
  account_tier: enum  # bronze, silver, gold, platinum, vip
  amount_at_risk: number?  # currency en account_context
  age_hours: float
context:
  tenant: string
  available_recipients: array<{role, email, on_call, timezone, language}>
  business_hours: {tz, start, end, days}
escalation_rules_yaml: string  # del config del tenant
```

**Schema output:**
```yaml
escalation_decision:
  route_to: enum  # auto_handle, supervisor, ceo, legal, finance, technical_lead
  recipients: array<{email, role, primary_or_cc}>
  channel: enum  # email, slack, sms, phone_call
  urgency_override: enum?  # si la regla escalo el urgency original
  rationale: string  # por que esta regla matcheo
  fallback_route: enum  # si recipient primary no responde en X horas
sla_target:
  ack_within_minutes: int
  resolve_within_hours: int
trace_id: string
```

**Latency target:** p95 < 100ms (no LLM)
**Cost target:** ~0 (compute puro)
**Pool L3:** NO (decision tree no aprende — se updeates manualmente cuando se cambia el YAML)
**Threshold shadow → active:** N/A — al ser deterministic se valida con test suite, no con shadow mode

**HITL gate:** ninguno (es la decision misma de routing).

---

### 3.9 AG_SUB_PRICING_CALCULATOR

**Proposito:** calcular pricing final de line items aplicando descuentos politica + tier de cliente + volumen + condiciones especiales. Sin LLM — Python puro sobre rules engine.

**Modelo:** Python (rules engine + matematica). Documentado aqui porque es invocable desde el orquestador.

**Trigger:** invocado por orquestador antes de AG_SUB_PROFORMA_BUILDER.

**Schema input:**
```yaml
items: array<{sku, quantity, unit, list_price, currency}>
account:
  account_id: string
  tier: enum
  custom_discount_percent: float?  # negociado historicamente
  payment_terms: string
  applicable_taxes: array<string>
context:
  rule_set_version: string  # ej. "marluvas-pricing-rules-v2.3"
  effective_date: date
  promotions_active: array<{code, condition, discount}>
```

**Schema output:**
```yaml
pricing_result:
  items_priced: array<{sku, quantity, unit_price_list, discount_applied, discount_reason, unit_price_final, line_total}>
  totals:
    subtotal: number
    discount_total: number
    tax_breakdown: array<{tax_code, percent, amount}>
    grand_total: number
    currency: string
  rules_applied: array<{rule_id, items_affected, impact}>
  warnings: array<{code, message}>  # ej. "discount_excede_politica_required_approval"
trace_id: string
```

**Latency target:** p95 < 200ms
**Cost target:** ~0
**Pool L3:** NO
**Threshold shadow → active:** N/A — test suite con casos canonicos

**HITL gate:** si `warnings.level=critical` el orquestador marca el draft para approval supervisor antes de send.

---

### 3.10 AG_SUB_INVENTORY_FETCHER

**Proposito:** wrapper sobre sistema de inventario del tenant (puede ser SAP MM, almacen propio, integracion con 3PL). Devuelve stock per SKU per warehouse con freshness.

**Modelo:** tool call only (HTTP REST a inventory API del tenant).

**Trigger:** invocado por orquestador cuando se necesita validar stock antes de proforma o respuesta a status_inquiry.

**Schema input:**
```yaml
skus: array<string>
warehouses: array<string>?  # si vacio, query a todos los warehouses default del tenant
freshness_required_seconds: int  # max staleness aceptable; default 300 (5 min)
```

**Schema output:**
```yaml
inventory:
  items: array<{sku, warehouse, available_quantity, reserved_quantity, in_transit_quantity, last_updated}>
  freshness_seconds: int
  source: enum  # live, cache_<seconds>
errors: array<{sku, warehouse, error_code}>?
trace_id: string
```

**Latency target:** p95 < 1.5s
**Cost target:** ~0 (tool call)
**Pool L3:** NO
**Threshold shadow → active:** 30d sin discrepancias >5% vs SAP MM auditoria

**HITL gate:** ninguno (read-only).

---

## 4. Pool L3 design — sub-agentes que aprenden vs los que no

| Sub-agente | Pool L3 | Razon |
|---|---|---|
| AG_SUB_EMAIL_CLASSIFIER | SI | Patterns de clasificacion mejoran con corpus |
| AG_SUB_DRAFT_WRITER | SI · ALTA PRIORIDAD | Tono, estructura, frases ganadoras destilables |
| AG_SUB_PROFORMA_BUILDER | SI | Cover letter patterns por industria/tenant |
| AG_SUB_PRE_CALL_SUMMARIZER | SI | Patterns de "que destacar" mejoran con uso |
| AG_SUB_COMPLIANCE_CHECKER | SI | Frases trampa nuevas se detectan via corpus |
| AG_SUB_SAP_QUERY | NO | Lookup deterministic, no hay nada que aprender |
| AG_SUB_VOICE_TRANSCRIBER | NO | Whisper externo a Anthropic, no fine-tunable v1 |
| AG_SUB_ESCALATION_ROUTER | NO | Decision tree YAML, se updeates manual |
| AG_SUB_PRICING_CALCULATOR | NO | Rules engine deterministic |
| AG_SUB_INVENTORY_FETCHER | NO | API wrapper |

5 de 10 con pool L3. Esto reduce footprint de gobernanza (curador solo revisa destilados de 5, no 10) sin perder beneficio (los 5 son los que mueven la aguja: clasificacion + draft + proforma + summary + compliance).

## 5. Composicion en archetype AG_AM_MARLUVAS

Ejemplo de archetype principal AG_AM_MARLUVAS componiendo 9 de 10 sub-agentes (no usa VOICE_TRANSCRIBER porque Marluvas no graba calls v1):

```yaml
archetype: AG_AM_MARLUVAS
type: orchestrator
state: stateful  # mantiene contexto cuenta + thread + pipeline
sub_agents:
  - AG_SUB_EMAIL_CLASSIFIER
  - AG_SUB_DRAFT_WRITER
  - AG_SUB_PROFORMA_BUILDER
  - AG_SUB_SAP_QUERY
  - AG_SUB_PRE_CALL_SUMMARIZER
  - AG_SUB_COMPLIANCE_CHECKER
  - AG_SUB_ESCALATION_ROUTER
  - AG_SUB_PRICING_CALCULATOR
  - AG_SUB_INVENTORY_FETCHER
flows: 3  # email_inbound, quote_request, escalation
hitl_gates:
  - draft_first_absolute  # P3
  - proforma_review_required
  - compliance_blocking_pause
knowledge_river_pool_id: pool_am_marluvas_v1
governance_mode: B  # comite (medio riesgo, B2B con pricing/contratos)
```

## 6. Decisiones aplicadas (de ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1)

1. **Profundidad orquestacion: max 2 niveles v1.** Orquestador AG_AM → sub-agentes. Ninguno de los 10 sub-agentes invoca a otro sub-agente. Si se necesita composicion compleja, el orquestador la coordina (paraleliza/serializa).
2. **Sharing cross-template: SI.** AG_SUB_DRAFT_WRITER y AG_SUB_EMAIL_CLASSIFIER reciben pool L3 cross-tenant. Knowledge River usa k-anon >=5 para privacy.
3. **Pricing per sub-agente: rolled-up al template padre.** Billing es por uso del template AM, no per-sub-agente. Metric interno granular para optimizacion.
4. **Versioning con shadow 30d.** Update de AG_SUB_DRAFT_WRITER v1.2 → v1.3 NO se aplica auto a archetypes que lo usan. Se promuewe a SHADOW 30d, datos comparativos, luego promote (P3 + P15).

## 7. CLI commands relacionados (futuros)

```
fbl subagent ls                              # lista catalogo
fbl subagent inspect <id>                    # ver schema I/O completo
fbl subagent test <id> --input <file.json>   # invocar aislado
fbl orchestrator inspect <archetype>         # ver composicion
fbl trace <request_id>                       # reconstruir grafo de sub-calls + cost + latency
fbl subagent promote <id> --from shadow      # promover de shadow a active tras 30d
```

(Implementacion en SCH_FB_CLI_INTERFACE pendiente · este ENT solo declara los commands esperados.)

## 8. Pendientes v2 (no entran en v1)

- Sub-agentes para vertical Code (AG_SUB_SPEC_PARSER, AG_SUB_TEST_GENERATOR, AG_SUB_PR_REVIEWER, etc) — cuando aparezca primer tenant software shop
- Sub-agentes para vertical Soporte (AG_SUB_TICKET_TRIAGE, AG_SUB_KB_SEARCHER, etc)
- Sub-agentes audio: AG_SUB_VOICE_SYNTHESIZER (text-to-speech) si appears caso de IVR automatizado
- Refactor "core vs vertical" cuando segundo vertical exponga reuso real de los 4 candidatos: EMAIL_CLASSIFIER, DRAFT_WRITER, COMPLIANCE_CHECKER, ESCALATION_ROUTER
- Sub-sub-agentes (composicion fractal nivel 3) — solo si datos de produccion >=90d justifican

## 9. Cambios v1.1 (post-auditoria R3)

### 9.1 Compliance Checker · 6 perfiles per vertical

R3 critico insight: "Un solo compliance checker no puede saber de todo. Compliance no es universal · solo el patron de validacion lo es."

`AG_SUB_COMPLIANCE_CHECKER` mantiene su definicion v1.0 (Haiku 4.5, schema I/O, latency, cost) pero agrega `profile` parametrizable per `vertical_spec_object.vertical_id`:

| Profile | Vertical | Reglas especificas |
|---|---|---|
| `safety_footwear` | safety_footwear (MWT) | ASTM F2413 validation · puntera/plantilla check · LFPDPPP MX/CO PII redaction |
| `chemical_PPE` | chemical_PPE | NIOSH/EN cert validation · chemical resistance matrix check · cartucho compatibility · LGPD BR si aplica |
| `MRO_compatibility` | MRO_industrial | OEM cross-reference validation · capacidad mechanical check · sustitucion technica policy |
| `construction_supply` | construction_supply | obra logistics check · descarga/entrega validation · weight/CBM compliance |
| `medical_regulated` | medical_regulated | registro sanitario per pais · COA validation · lote/vencimiento check · TIER 4 PII handling · DPO notification triggers |
| `electrical_technical` | electrical_technical | IEC/NEMA cert · capacidad electrica validation · curva kAIC check · safety regulations |

El profile activo se determina por `vertical_spec_object.vertical_id` del tenant. Cada profile tiene su propio `rule_set` declarativo + `validation_methods` per regla.

### 9.2 Kill criteria per sub-agente

R3 mitigacion riesgo R3: "demasiados sub-agentes antes de saber cual mueve el negocio · 10 sub-agentes para AM B2B puede volverse teatro de arquitectura si todos existen pero ninguno prueba impacto."

Cada sub-agente declara `kill_criteria` evaluables a 12 sem (wedge) y 90d (P15). Cuatro acciones posibles:

| Accion | Trigger |
|---|---|
| **STAY** | Reduce tiempo cycle · reduce error severo · aumenta reuse de outputs |
| **MERGE** | Solo reetiqueta trabajo de otro sub-agente · output redundante |
| **FREEZE** | Requiere mas curaduria que valor que aporta · pool L3 no destila |
| **BLOCK_AUTONOMY_PROMOTION** | Buen acceptance rate pero error severity criticos infrecuentes superan threshold |

#### Kill criteria per sub-agente catalogo

| Sub-agente | STAY si | MERGE si | FREEZE si | BLOCK promo if |
|---|---|---|---|---|
| AG_SUB_EMAIL_CLASSIFIER | accuracy >=85% en 90d · zero misclassifications criticas | duplicado por LLM upstream | accuracy <70% requiere correccion humana sostenida | severity_weight de errores >35 en 90d |
| AG_SUB_DRAFT_WRITER | send-rate sin edicion sustantiva >=0.6 · ALTA PRIORIDAD pool L3 destila | redactor genérico sin context-aware quality | edit-rate >40% sustained | error severity critical >2 en 90d |
| AG_SUB_PROFORMA_BUILDER | close-rate >= baseline humano · proforma calidad consistente | absorbido por DRAFT_WRITER si formato unifica | warnings.critical >5% requests | severity_weight errores >50 en 90d |
| AG_SUB_SAP_QUERY | error rate <2% en 30d | covered por orquestador wrapper | timeout rate >5% | data integrity errors detectados |
| AG_SUB_VOICE_TRANSCRIBER | confidence >=0.85 · NO usado en MWT v1 | obsolecido por mejor whisper externo | accuracy <80% sustained | cualquier error de transcripcion confidencial filtrada |
| AG_SUB_PRE_CALL_SUMMARIZER | accept-rate AM >=0.7 · pool L3 destila | redundante con DRAFT_WRITER | nadie usa el output (telemetria <10% calls) | ningun blocker |
| AG_SUB_COMPLIANCE_CHECKER (todas profiles) | zero false negatives en 90d (NUNCA aprobar lo blocking) | nunca · es critico per profile | nunca · es critico | si false negatives >0 en 30d |
| AG_SUB_ESCALATION_ROUTER | rules YAML cubre 95% casos · escalation SLA cumplido >=95% | nunca · es deterministic | si rules ratio cobertura <80% | nunca · es deterministic |
| AG_SUB_PRICING_CALCULATOR | calculo correcto en test suite · zero rounding errors | nunca · es Python deterministic | nunca · es Python | si rounding errors detectados |
| AG_SUB_INVENTORY_FETCHER | discrepancias <5% vs SAP MM auditoria | covered si SAP query absorbe | timeout rate >3% | data integrity errors detectados |

Evaluacion automatica continua · curador del tenant revisa kill_criteria triggered cada semana.

### 9.3 Severity weight integrado en threshold shadow → active

Adicional al criterio v1.0, ahora cada sub-agente declara:

```yaml
threshold_shadow_to_active:
  duration_days: 30  # mantenido
  acceptance_rate_min: 0.65  # mantenido
  severity_weight_max_errors: 30  # NUEVO · suma ponderada de errores en 30d
  zero_critical_errors: true  # NUEVO · ningun error severity=critical permitido
  human_review_required: true  # NUEVO · curador firma promote
```

Sub-agente NO promote si:
- `severity_weight_sum_errors > severity_weight_max_errors` aun con buen acceptance rate
- Cualquier error severity=critical en periodo

R3 insight: "agente con buen acceptance rate puede cometer errores no tolerables · severity > acceptance rate."

## 10. Pendientes v2 (no entran en v1.1)

- Sub-agentes para vertical Code (AG_SUB_SPEC_PARSER, AG_SUB_TEST_GENERATOR, AG_SUB_PR_REVIEWER, etc) — cuando aparezca primer tenant software shop
- Sub-agentes para vertical Soporte (AG_SUB_TICKET_TRIAGE, AG_SUB_KB_SEARCHER, etc)
- Sub-agentes audio: AG_SUB_VOICE_SYNTHESIZER (text-to-speech) si appears caso de IVR automatizado
- Refactor "core vs vertical" cuando segundo vertical exponga reuso real de los 4 candidatos: EMAIL_CLASSIFIER, DRAFT_WRITER, COMPLIANCE_CHECKER, ESCALATION_ROUTER
- Sub-sub-agentes (composicion fractal nivel 3) — solo si datos de produccion >=90d justifican
- Compliance Checker profiles para verticals adicionales que aparezcan
- Auto-MERGE detection (sistema sugiere consolidar sub-agentes redundantes)

## Changelog
- 2026-04-30 v1.1 VIGENTE: Indexa-d post-auditoria R3. Agregado: AG_SUB_COMPLIANCE_CHECKER con 6 perfiles per vertical (safety_footwear · chemical_PPE · MRO_compatibility · construction_supply · medical_regulated · electrical_technical) · profile activo determinado por vertical_spec_object.vertical_id. Kill criteria per sub-agente con 4 acciones posibles (STAY · MERGE · FREEZE · BLOCK_AUTONOMY_PROMOTION) evaluables a 12 sem y 90d. Severity weight integrado en threshold shadow→active (severity_weight_max_errors + zero_critical_errors + human_review_required). Mitiga R3 risks: compliance no universal · sub-agentes que no prueban impacto · agentes "comodos pero peligrosos".
- 2026-04-30 v1.0 VIGENTE: creacion inicial. Catalogo de 10 sub-agentes para vertical AM B2B con detalle completo schema I/O + modelo + latency target + cost target + pool L3 + threshold shadow→active + HITL gate. 5 con pool L3 (ALTA PRIORIDAD: DRAFT_WRITER), 5 sin pool. Composicion ejemplo AG_AM_MARLUVAS con 9 de 10. Decisiones de P16 aplicadas (profundidad max 2, sharing cross-tenant, pricing rolled-up, versioning shadow 30d). CLI commands declarados. Sub-agentes para verticals futuros (Code, Soporte, Audio) explicitamente en pendientes v2.

## Stamp
VIGENTE 2026-04-30 v1.1 — Catalogo enriquecido post-R3. Compliance profiles per vertical evita "compliance checker que finge saber de todo" (R3). Kill criteria evita teatro arquitectonico de sub-agentes sin impacto. Severity weight evita agentes "comodos pero peligrosos" (R3 critical insight). Refactor core/vertical sigue diferido hasta segundo vertical.
