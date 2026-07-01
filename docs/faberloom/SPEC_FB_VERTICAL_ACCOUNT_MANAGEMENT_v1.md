---
id: SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: spec
stamp: VIGENTE 2026-04-30 (v1.1 post-auditoria R2+R3)
fecha: 2026-04-30
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R1+R2+R3)
aplica_a: [FaberLoom]
implementa:
  - ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1 (P16 Atomic Agents Principle)
  - SPEC_FB_KNOWLEDGE_RIVER_v1 (modelo conocimiento)
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1 (adapter pattern · MWT como primer adapter)
  - ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1 (14 fuentes con freshness)
  - ENT_FB_COMMERCIAL_AUTHORITY_MATRIX_v1 (5 niveles + 7 decisiones + 8 NEVER)
  - ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1 (15 excepciones + severity_weight)
  - SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1 (per-line + per-quote + 3 vistas)
  - POL_FB_KR_PRIVACY_TIERS_v1 (4 tiers Knowledge River)
  - ARCH_AGENT_PRINCIPLES (P1-P15 core sealed v1.5)
relacionado_con:
  - ENT_FB_SUB_AGENTS_LIBRARY_v1 (v1.1 con compliance profiles + kill_criteria)
  - ENT_FB_AGENT_ARCHETYPES_v1
  - SPEC_FB_AGENT_BUILDER_v1
  - SPEC_ACTION_ENGINE
  - POL_DATA_CLASSIFICATION (sealed v1.4)
  - ENT_FB_PRICING_TIERS
scope: minimo + 3 flows criticos · MWT como adapter (no core) · timeline 12 sem operativo
---

# SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1
## Vertical Account Management B2B · primer SPEC end-to-end FB v1

## 1. Proposito

SPEC del primer vertical productivo de FaberLoom: archetype **AG_AM (Account Manager)** modelado con orquestador delgado + sub-agentes atomicos desde dia 1, gestionando inbound de cliente B2B (emails, llamadas, proformas, escalaciones).

**Adapter pattern (v1.1 post-R3):** MWT NO es el core del sistema · es el primer adapter del vertical `safety_footwear` (definido en `ENT_FB_VERTICAL_SPEC_OBJECT_v1`). El core es spec-to-quote discipline parametrizable per industria. Esto evita overfit MWT al canonizar y protege expansion cross-industria.

Tenant beta: **MWT** con representaciones Marluvas + Tecmater (calzado de trabajo · clientes B2B Mexico-Colombia). MWT es el TENANT · Marluvas/Tecmater son catalogos/proveedores que MWT distribuye (NO son tenants paralelos).

Primer SPEC end-to-end que aplica P16 (sub-agentes atomicos) + Knowledge River (templates como activos organizacionales) + adapter pattern (vertical_spec_object).

## 2. Scope v1 — minimo + 3 flows criticos

**IN scope v1.1:**
- 1 archetype principal: AG_AM_MWT (UN solo archetype del tenant MWT que cubre catalogos Marluvas + Tecmater · NO archetypes paralelos)
- 9 sub-agentes del catalogo `ENT_FB_SUB_AGENTS_LIBRARY_v1` v1.1 (todos menos VOICE_TRANSCRIBER) · cada uno con `kill_criteria` declarado
- AG_SUB_COMPLIANCE_CHECKER con profile `safety_footwear` activo (de los 6 perfiles canonizados)
- 3 flows en detalle: **F1 email entrante**, **F2 proforma request**, **F3 escalacion**
- vertical_spec_object: `safety_footwear` (config completa MWT)
- 14 fuentes Source of Truth con freshness SLA
- Authority Matrix con defaults canonicos + overrides MWT
- 15 excepciones canonicas con severity_weight (Low=1 / Medium=3 / High=7 / Critical=15)
- Evidence bundle obligatorio per-line + per-quote · 3 vistas
- Privacy tiers Knowledge River (PRIVATE_RAW + TENANT_DERIVED · NO Layer 1 cross-tenant sin DPA · NO TIER 4 en MWT v1)
- HITL gates P3 absoluto en send + proforma + compliance block
- Metricas observables 90d ponderadas por severidad para validar P16
- Calendario operativo 12 semanas explicito (ver §15bis)
- Out of scope explicito (con razon)

**OUT of scope v1 (referenciado a v1.1):**
- Flow call recording + transcript (requiere VOICE_TRANSCRIBER + integracion telefonia)
- Flow mass outreach (campaigns, newsletters)
- Flow follow-up automation (cadencias time-based)
- Multi-language beyond es-MX, es-CO, pt-BR
- Integracion CRM externa (Salesforce, HubSpot) — v1 usa CRM-lite interno
- Voice synthesis (text-to-speech) para IVR

## 3. Modelo de datos

### 3.1 Cuenta (Account)

```yaml
account:
  account_id: string  # UUID
  tenant: string  # marluvas, tecmater
  company_name: string
  legal_id: string  # RFC MX, NIT CO, CC para personas
  industry: enum  # metalmecanica, agro, construccion, mineria, otro
  country: string
  language_pref: string  # es-MX, es-CO, pt-BR
  tier: enum  # bronze, silver, gold, platinum, vip
  custom_discount_percent: float?
  payment_terms: string
  credit_limit: number
  contacts: array<contact>
  primary_contact_id: string
  am_assigned: string  # email del AM humano
  status: enum  # prospect, active, inactive, churned
  created_at: ISO8601
  last_activity_at: ISO8601
```

### 3.2 Contact

```yaml
contact:
  contact_id: string
  account_id: string
  name: string
  role: string?
  email: string
  phone: string?
  preferred_communication_style: enum  # formal, friendly, direct
  is_primary: boolean
```

### 3.3 Conversation (thread)

```yaml
conversation:
  thread_id: string
  account_id: string
  contact_id: string
  channel: enum  # email, phone, whatsapp_b2b
  subject: string
  status: enum  # open, in_progress, awaiting_client, awaiting_internal, resolved, closed
  first_message_at: ISO8601
  last_message_at: ISO8601
  classification_history: array<classification_snapshot>
  drafts_history: array<draft_snapshot>  # P3 audit trail
  proformas_referenced: array<proforma_id>
  escalations_triggered: array<escalation_event>
```

### 3.4 Pipeline / open_items

```yaml
open_item:
  item_id: string
  account_id: string
  type: enum  # quote_pending, payment_overdue, sample_pending, complaint_unresolved, follow_up_scheduled
  status: enum  # new, in_progress, blocked, resolved
  age_days: int
  amount_at_risk: number?
  related_thread_id: string?
  due_date: ISO8601?
  owner: string  # email AM o sub-agente que lo creo
```

## 4. Archetype AG_AM (orquestador delgado)

```yaml
archetype: AG_AM
version: 1.0
type: orchestrator  # P16
state: stateful
context_held:
  - account snapshot (cuenta + ultimos 5 threads + pipeline)
  - tenant config (marluvas o tecmater)
  - template_voice (tono, banned phrases, signoff)
sub_agents:  # 9 de 10 del catalogo
  - AG_SUB_EMAIL_CLASSIFIER
  - AG_SUB_DRAFT_WRITER
  - AG_SUB_PROFORMA_BUILDER
  - AG_SUB_SAP_QUERY
  - AG_SUB_PRE_CALL_SUMMARIZER
  - AG_SUB_COMPLIANCE_CHECKER
  - AG_SUB_ESCALATION_ROUTER
  - AG_SUB_PRICING_CALCULATOR
  - AG_SUB_INVENTORY_FETCHER
flows_implemented:
  - F1: email_inbound
  - F2: quote_request
  - F3: escalation
hitl_gates:
  - P3_draft_first_absolute  # nunca envia directo
  - proforma_review_required
  - compliance_blocking_pause
knowledge_river:
  pool_id: pool_am_marluvas_v1  # o pool_am_tecmater_v1
  layers_used: [L0_kb, L1_working, L2_episodic_per_user, L3_pool_collective, L4_indexed]
  governance_mode: B  # comite (medio riesgo)
  curator_role: gerente_comercial_marluvas
  reviewers: [analista_pricing, analista_compliance]
  k_anon_min: 5
audit:
  trace_id_per_request: required
  sha_chain: enabled
  visibility_default: INTERNAL
  ceo_only_sections: []
```

El orquestador NO ejecuta tareas cognitivas. Su responsabilidad es:
1. Recibir trigger event (email, calendar, escalation_request, manual)
2. Mantener contexto de cuenta + thread + pipeline
3. Decidir que sub-agente invocar y en que orden
4. Paralellizar llamadas independientes
5. Agregar resultados
6. Aplicar HITL gates antes de send
7. Persistir audit log granular

## 5. Flow F1 — Email entrante

### 5.1 Diagrama

```
EMAIL_RECEIVED
  └─ AG_AM (orquestador)
      ├─ AG_SUB_EMAIL_CLASSIFIER  [Haiku · 1.2s p95]
      ├─ if classification.requires_human → marca thread + notify AM → END
      ├─ if primary_intent = quote_request → fork to F2
      ├─ if primary_intent in {complaint, payment_overdue, legal_threat} → fork to F3
      ├─ else (status_inquiry, follow_up, sample_request):
      │   ├─ AG_SUB_INVENTORY_FETCHER (parallel)  [tool · 1.5s p95]
      │   ├─ AG_SUB_SAP_QUERY (parallel, if needed)  [Haiku+tool · 2s p95]
      │   ├─ AG_SUB_DRAFT_WRITER  [Sonnet · 4s p95]
      │   ├─ AG_SUB_COMPLIANCE_CHECKER  [Haiku · 1s p95]
      │   ├─ if compliance.blocking_issues != [] → mark BLOCKED + notify AM → END
      │   ├─ persist draft as DRAFT_PENDING_REVIEW
      │   └─ notify AM: "draft listo para revisar"
```

Total latency p95 path principal (parallel): max(1.5s, 2s) + 1.2s + 4s + 1s = ~8s.

### 5.2 HITL gate · P3 absoluto

Draft NUNCA se envia automatic. Va a inbox virtual del AM con:
- Email original
- Clasificacion (intent + urgency + sentiment + confidence)
- Draft propuesto
- Diff vs templates anteriores (si existieron)
- Internal note (contexto)
- Boton: send · edit · discard · escalate
- Si AM edita >20%, evento `DRAFT_HEAVY_EDIT` se envia a Knowledge River pool L3 como negative signal (drafter podria mejorar)

### 5.3 Outcome accountability (P15)

Metric a 90d: **send-rate sin edicion sustantiva**. Target: >=0.6.
Si <0.6 → AG_SUB_DRAFT_WRITER vuelve a SHADOW. Investigar root cause antes de reactivar.

## 6. Flow F2 — Proforma request (quote_request)

### 6.1 Diagrama

```
F1 fork → primary_intent = quote_request
  └─ AG_AM
      ├─ extract parsed_items from email body via classifier output
      ├─ AG_SUB_SAP_QUERY (pricing master + account credit)  [Haiku+tool · 2s]
      ├─ AG_SUB_INVENTORY_FETCHER (stock per SKU)  [tool · 1.5s]
      ├─ AG_SUB_PRICING_CALCULATOR (apply discounts politica)  [Python · 200ms]
      ├─ if pricing.warnings has critical → mark APPROVAL_REQUIRED + notify supervisor
      ├─ AG_SUB_PROFORMA_BUILDER  [Sonnet · 6s]
      ├─ AG_SUB_DRAFT_WRITER (cover email)  [Sonnet · 4s]
      ├─ AG_SUB_COMPLIANCE_CHECKER (proforma + email)  [Haiku · 1s]
      ├─ if compliance.blocking_issues != [] → BLOCKED + notify AM → END
      ├─ persist proforma as PROFORMA_DRAFT
      └─ notify AM: "proforma + cover email listos para revisar"
```

Total latency p95 path principal (con parallels): max(2s, 1.5s) + 200ms + 6s + 4s + 1s = ~13s.

### 6.2 HITL gate · proforma review required

Proforma SIEMPRE va a draft state. AM revisa:
- Items priced (puede ajustar quantity, agregar items, cambiar SKU)
- Discounts applied (puede aprobar/rechazar discount excepcional)
- Cover email (puede ajustar tono, agregar contexto)
- Validity period (puede cambiar 30d → 45d casos especiales)

Boton: send · edit · save_for_later · escalate_for_approval (cuando supervisor needed)

### 6.3 Outcome accountability (P15)

Metric a 90d:
- **proforma close-rate** AM con AG_AM enabled vs baseline AM humano sin AG_AM
- Target: >= baseline (no peor)
- Stretch: +10% vs baseline (Knowledge River destila patterns ganadores)

## 7. Flow F3 — Escalacion

### 7.1 Diagrama

```
F1 fork → primary_intent in {complaint, payment_overdue, legal_threat, vip_request}
OR sub-agente devuelve needs_escalation
  └─ AG_AM
      ├─ AG_SUB_ESCALATION_ROUTER (deterministic)  [<100ms]
      ├─ extract route_to + recipients + urgency_override + sla_target
      ├─ AG_SUB_DRAFT_WRITER (internal alert message)  [Sonnet · 4s]
      ├─ AG_SUB_COMPLIANCE_CHECKER (que el alert no tenga PII innecesaria)  [Haiku · 1s]
      ├─ persist escalation_event in conversation
      ├─ send alert via channel (email, slack, sms)
      ├─ create open_item type=complaint_unresolved (or matching)
      └─ if route_to = ceo → also create CEO inbox priority entry
```

Total latency p95: <100ms + 4s + 1s = ~5s. Critical path porque escalations son time-sensitive.

### 7.2 HITL gate

NO HITL en F3. Escalation es notificacion, no accion irreversible. El recipient decide que hacer.

Excepcion: si `route_to = legal` y `severity = critical` → tambien snapshot del thread completo se exporta a archivo legal con SHA hash + audit trail (para preservar evidencia).

### 7.3 SLA enforcement

Cada escalation tiene `ack_within_minutes` y `resolve_within_hours` del output del router. Si recipient no acknowleges en ack window → AG_AM dispara fallback_route automatic.

## 8. Knowledge River pool config

### 8.1 Pool per tenant

```yaml
pool_am_marluvas_v1:
  parent_template: AG_AM_MARLUVAS
  layers:
    L0_kb:
      curator_seeded: true
      seeded_by: gerente_comercial_marluvas
      contents: [tone_guide, banned_phrases, signoff_templates, fix_phrases_industry]
    L1_working:
      ttl_hours: 24
      scope: per_request
    L2_episodic_per_user:
      retention_days: 90
      visibility: AM_user_only
    L3_pool_collective:
      k_anon_min: 5
      retention_days: 365
      sub_agents_contributing: [EMAIL_CLASSIFIER, DRAFT_WRITER, PROFORMA_BUILDER, PRE_CALL_SUMMARIZER, COMPLIANCE_CHECKER]
      curator: gerente_comercial_marluvas
      reviewers: [analista_pricing, analista_compliance]
    L4_indexed:
      signed_by: curator
      promotion_threshold: 50_uses_with_positive_outcome
```

### 8.2 Cross-tenant pool

`AG_SUB_DRAFT_WRITER` y `AG_SUB_EMAIL_CLASSIFIER` ALSO contribute a pool cross-tenant (`pool_global_drafter_v1`, `pool_global_classifier_v1`) respetando k-anon >=5. Esto permite que tenant Marluvas se beneficie de patterns aprendidos en Tecmater (y futuros).

PII redaction obligatoria antes de entrar a pool L3 cross-tenant (manejado por `POL_DATA_CLASSIFICATION` + `AG_SUB_COMPLIANCE_CHECKER` en redaction mode).

## 9. Metricas observables 90d (validacion P16)

### 9.1 Token cost reduction

Hipotesis P16: -65% vs monolitico.
Medicion: comparar cost real AG_AM (orquestador + 9 sub-agentes) vs cost simulado con archetype monolitico Sonnet hipotetico.
Target: -65% +-10pp.
Si fuera de tolerancia → revisitar threshold sub-agente vs skill_package.

### 9.2 Latency p95 user-perceived

F1 target: <8s
F2 target: <13s
F3 target: <5s

Si latency excede target en >20% requests → reevaluar paralellizacion del orquestador.

### 9.3 Audit log searchability

Tiempo medio para reconstruir trace completo de 1 request: <30s.
Mide eficacia del sha-chain + indexado por trace_id.

### 9.4 Curador overhead

Tiempo gastado por curador del pool revisando patterns destilados.
Target: <2h/semana per tenant. Si crece linealmente con # sub-agentes → escalation a comite (governance mode B).

### 9.5 Send-rate sin edicion sustantiva (P15 sub-agente DRAFT_WRITER)

Target: >=0.6 a 90d. Si <0.6 → DRAFT_WRITER vuelve a SHADOW.

### 9.6 Proforma close-rate (P15 sub-agente PROFORMA_BUILDER)

Target: >= baseline humano. Si < baseline → PROFORMA_BUILDER vuelve a SHADOW.

### 9.7 Escalation SLA compliance

Target: >=95% escalations acknowledged dentro de ack_within_minutes.

## 10. Visibility y data classification

| Dato | Classification | Pool L3 elegible | Notas |
|---|---|---|---|
| Email body raw | CONFIDENTIAL | NO sin redaction | PII redaction obligatoria |
| Classification output | INTERNAL | SI (sin email body) | Solo intent + sentiment + confidence |
| Draft body | CONFIDENTIAL | SI con redaction | Patterns extraibles cross-tenant |
| Proforma | CONFIDENTIAL | NO | Pricing sensitive |
| SAP data | RESTRICTED | NO | Nunca cross-tenant |
| Escalation alert | INTERNAL | NO | Recipient-specific |
| Audit log | RESTRICTED | NO | Solo CEO-ONLY queries |

`POL_DATA_CLASSIFICATION` v1.4 sealed governs estas decisiones.

## 11. Roles humanos involucrados

| Rol | Acciones |
|---|---|
| AM humano | Revisar drafts, editar, send. Es el "piloto" — AG_AM es copiloto |
| Supervisor comercial | Aprobar discounts excepcionales, intervenir escalations medium |
| Gerente comercial (curador del pool) | Sembrar L0, validar patterns destilados, gobernar L4 indexado |
| Analista pricing (reviewer) | Co-validar patterns relacionados con pricing en gobernanza B |
| Analista compliance (reviewer) | Co-validar patterns relacionados con compliance |
| Auditor (opcional) | Acceso read-only a audit log para revisiones periodicas |
| CEO MWT | Recipient de escalations level=ceo, owner de POL_DATA_CLASSIFICATION |

## 12. Pricing model (referencia)

Per `ENT_FB_PRICING_TIERS`: AG_AM como template billable.

Pricing AG_AM v1:
- Setup fee per tenant: $XXX [PENDIENTE — definir antes GA]
- Subscription mensual base: $XXX [PENDIENTE]
- Per-request usage cap incluido: 5000 emails/mes + 500 proformas/mes
- Overage: $XXX per 1000 emails extra, $XXX per 100 proformas extra [PENDIENTE]

Pricing rolled-up: usuario paga por template AM, no per-sub-agente. Metric interno granular para optimizacion.

## 13. Out of scope explicito v1 (con razon)

| Capacidad | Razon de exclusion v1 | Target version |
|---|---|---|
| Voice transcription + summary post-call | Requiere integracion telefonia (Aircall/Twilio) + AG_SUB_VOICE_TRANSCRIBER en active | v1.1 |
| Mass outreach (campaigns) | Risk profile distinto (compliance LFPDPPP requires opt-in tracking) | v1.2 |
| Follow-up automation cadencias | Riesgo de spam si no se calibra + requires scheduled_tasks beyond cron | v1.1 |
| Multi-language EN, FR | Sin demand inmediato, agrega complejidad | v2.0 |
| Integracion Salesforce/HubSpot | Tenants v1 (MWT) usan CRM-lite interno | v1.2 |
| Voice synthesis (TTS) | Sin caso de uso identificado v1 | TBD |
| Predictive analytics (churn, upsell signals) | Requiere >=12mo de data historica | v2.0 |

## 14. Decisiones pendientes para v1.1

1. SLA targets per industry (metalmecanica vs agro vs construccion pueden tener SLAs diferentes)
2. Proforma approval matrix (quien aprueba que descuento — actualmente solo distincion supervisor vs no)
3. Escalation YAML schema completo + UI para que tenant edite sus propias rules
4. Audit log retention period per tier (gold vs platinum pueden requerir retencion mas larga)
5. Rate limiting per tenant (DDoS protection · cap requests/min para evitar abuse)
6. Pricing $XXX [PENDIENTE — CEO + finance]
7. CRM-lite interno data model completo (este SPEC asume existe pero no especifica)

## 15. Roadmap implementacion (referencia · NO en este SPEC)

Implementacion code es responsabilidad de PLB_ORCHESTRATOR + agentes AG-01 a AG-07 segun scopes definidos en CLAUDE.md. Este SPEC es contract-first: define que debe existir, NO como implementarlo.

Fases sugeridas (referenciables · no normativas):
1. Action Engine + Knowledge River infra (SPEC_ACTION_ENGINE + SPEC_FB_KNOWLEDGE_RIVER ya existen)
2. Sub-agentes individuales en SHADOW mode (1 sprint per sub-agente)
3. Orquestador AG_AM componiendo sub-agentes
4. Pool L3 destilacion con curador human-in-loop
5. F1, F2, F3 end-to-end con tenant beta MWT/Marluvas
6. Outcome accountability validation 90d
7. Si validation pass → promote sub-agentes shadow → active uno por uno
8. GA tras 4-6 weeks active sin regressions

## 16. FROZEN references

Este SPEC NO modifica ningun FROZEN. Referencia:
- `ENT_OPS_STATE_MACHINE` (FROZEN) — state machine generic, AG_AM no necesita extender
- `PLB_ORCHESTRATOR` (FROZEN) — scopes de agentes implementadores aplica tal cual

## 15bis. Calendario operativo 12 semanas (canonizado v1.1 post-R3)

Resuelve tension P15 (90d) vs wedge (12 sem). Calendario explicito con instrumentos distintos:

```
SEM 0  · BASELINE MANUAL
  - AM extrae 60-120 RFQs historicos (AI-assisted via script Gmail/Outlook+SAP)
  - CEO marca outcome: ganadas/perdidas/ambiguas/edge
  - Sub-split per pais · proveedor · SKU family · volumen · stock · cliente · simple/mixta
  - Sistema captura: tiempo actual cotizacion · errores · retrabajo · tasa cierre
  - Replay set inicial poblado en TENANT_DERIVED tier
  - Authority Matrix MWT calibrada (~30 min CEO ajusta defaults)
  - vertical_spec_object safety_footwear configurado completo

SEM 1-2 · SHADOW MODE
  - AG_AM_MWT recibe inputs reales · genera drafts internos
  - Drafts NO salen al cliente · solo se comparan con respuesta humana
  - Captura diff humano vs agente per output
  - Severity weight tracking activo

SEM 3-6 · DRAFT-FIRST ABSOLUTO
  - HITL P3 cumple · todos los outputs van a draft_pending_review
  - AM revisa · firma · edita · rechaza con razon tipificada
  - Edits >20% disparan negative signal a Knowledge River
  - Compliance Checker profile safety_footwear activo · bloquea criticos

SEM 7-10 · OPERACION CONTROLADA CON METRICAS
  - Metricas wedge en vivo:
    * Tiempo RFQ → borrador
    * Tiempo RFQ → cotizacion aprobada
    * % cotizaciones sin retrabajo mayor
    * Precision SKU/technical_spec_rule
    * Precision stock/lead time
    * Margen preservado
    * Conversion asistida o avance comercial
  - Algunos sub-agentes pueden promote a higher autonomy si severity_weight P15 lo justifica

SEM 11-12 · DECISION WEDGE
  - Comparacion baseline Sem 0 vs operacion Sem 7-10
  - Decision: SEGUIR (resultados validan) · RECORTAR (focus en lo que funciona) · REDISENAR (no validan)
  - Si SEGUIR: prepar GA + segundo tenant adapter

DIA 90 · EVALUACION P15 PER SUB-AGENTE
  - Metricas P15 ponderadas por severidad:
    * Acceptance rate
    * Error severity (critical=15, high=7, medium=3, low=1)
    * Manual correction time
    * Escalation quality
    * Reuse rate de outputs
    * Contribution to quote cycle time
  - Promote sub-agente a higher autonomy si supera umbrales
  - Demote/SHADOW sub-agente si severity_weight de errores supera threshold
```

Reconciliacion P15 vs wedge: wedge mide si el SISTEMA sirve como producto · P15 mide si cada sub-agente merece mas autonomia. NO compiten · operan en escalas distintas.

## 15ter. Metricas observables 90d (v1.1 ponderadas por severidad)

Las 7 metricas del v1.0 se mantienen pero **todas se ponderan por severity_weight** (R3 critical insight):

| Metrica | Calculo v1.0 | Calculo v1.1 |
|---|---|---|
| Token cost reduction | -65% promedio | -65% promedio (sin cambio) |
| Latency p95 per flow | F1<8s · F2<13s · F3<5s | (sin cambio) |
| Audit log searchability | <30s para reconstruir trace | (sin cambio) |
| Curador overhead | <2h/sem per tenant | (sin cambio) |
| Send-rate sin edicion sustantiva | >=0.6 a 90d | **>=0.6 ponderado por severity** · si error severity=critical pesa 15× error severity=low |
| Proforma close-rate | >= baseline humano | **>= baseline ponderado** · close de proforma con errores critical no cuenta |
| Escalation SLA compliance | >=95% acknowledged en SLA | **>=95% ponderado** · breach de escalation severity=critical pesa 15× breach low |

Esto evita que un sub-agente con buen acceptance rate pero errores criticos infrecuentes se promueva (R3 insight).

## 15. Roadmap implementacion (referencia · NO en este SPEC)

Implementacion code es responsabilidad de PLB_ORCHESTRATOR + agentes AG-01 a AG-07 segun scopes definidos en CLAUDE.md. Este SPEC es contract-first: define que debe existir, NO como implementarlo.

Fases sugeridas (referenciables · no normativas):
1. Action Engine + Knowledge River infra (SPEC_ACTION_ENGINE + SPEC_FB_KNOWLEDGE_RIVER ya existen)
2. Sub-agentes individuales en SHADOW mode (1 sprint per sub-agente)
3. Orquestador AG_AM_MWT componiendo sub-agentes
4. Knowledge River layers L0+L1+L2 con curador human-in-loop (NO L3 cross-tenant en MWT v1)
5. F1, F2, F3 end-to-end con MWT (catalogos Marluvas + Tecmater)
6. Outcome accountability validation 90d ponderada por severity
7. Si validation pass → promote sub-agentes shadow → active uno por uno
8. GA tras 4-6 weeks active sin regressions

## 17. Cambios canonizados en v1.1 (post-auditoria R2+R3)

| Cambio | Motivo |
|---|---|
| MWT pasa de "tenant beta" a "primer adapter del vertical safety_footwear" | R3: evita overfit MWT al canonizar |
| AG_AM_MARLUVAS + AG_AM_TECMATER → AG_AM_MWT (UN solo archetype) | Correccion modelo: MWT es tenant · Marluvas/Tecmater son catalogos |
| Sumar referencia a 6 piezas nuevas canonizadas (Source of Truth · Authority Matrix · Exception Taxonomy · Evidence Bundle · Privacy Tiers · Vertical Spec Object) | Implementacion concreta del scope que en v1.0 quedaba como "modelo de datos generico" |
| Calendario operativo 12 sem explicito (§15bis) | Reconciliacion P15 (90d) vs wedge (12 sem) post-R2 |
| Severity_weight ponderada en TODAS las metricas (§15ter) | R3: "severity > acceptance rate" · evita agentes "comodos pero peligrosos" |
| Compliance Checker profile safety_footwear declarado | Sub-Agents Library v1.1 con 6 perfiles per vertical |
| Knowledge River en MWT v1 = solo L0+L1+L2 (NO Layer 1 cross-tenant sin DPA) | Privacy tiers POL_FB_KR_PRIVACY_TIERS_v1 + decision DPA-required para Layer 1 |
| Replay set como pool canonical · 60-120 RFQs · split 40/25/25/10 | R2 + R3 detalle del bench Arena Layer 1+2 |
| 14 fuentes Source of Truth con freshness SLA per dominio | R2 detalle |
| Authority Matrix con 5 niveles + 7 decisiones + 8 NEVER lista | R2 detalle |
| 15 excepciones canonicas con severity_weight | R2 detalle |
| Evidence Bundle obligatorio per-line + per-quote · 3 vistas | R2 detalle |

## Changelog
- 2026-04-30 v1.1 VIGENTE: Indexa-d post-auditoria R2+R3. MWT canonizado como primer adapter del vertical safety_footwear (NO core). UN solo archetype AG_AM_MWT (corrige modelo Marluvas/Tecmater como tenants paralelos). Implementa 6 piezas nuevas canonizadas (vertical_spec_object · source of truth · authority matrix · exception taxonomy · evidence bundle · privacy tiers). Calendario operativo 12 sem explicito reconciliando P15 vs wedge. Severity_weight ponderada en TODAS las metricas observables. Compliance Checker profile safety_footwear declarado (de los 6 perfiles canonizados en Sub-Agents Library v1.1). Knowledge River v1 limita a L0+L1+L2 (NO Layer 1 cross-tenant sin DPA). Replay set spec con 60-120 RFQs canonical. 17 secciones (sumando 15bis · 15ter · 17 nuevas). FROZENs intactos. ARCH sealed v1.5 NO modificado.
- 2026-04-30 v1.0 VIGENTE: SPEC inicial. Primer vertical productivo FB v1 aplicando P16 + Knowledge River end-to-end. Scope: archetype AG_AM + 9 sub-agentes + 3 flows criticos (email entrante, proforma request, escalacion) + Knowledge River pool config + metricas observables 90d. Out of scope explicito documentado. Pricing $XXX [PENDIENTE]. Aplica HITL P3 absoluto + P15 outcome accountability con thresholds concretos per sub-agente. Tenant beta: MWT con Marluvas + Tecmater.

## Stamp
VIGENTE 2026-04-30 — Primer SPEC vertical FB v1. Habilita validacion P16 con caso real B2B. Define contracts I/O completos para los 3 flows criticos. Listo para consumir por implementacion (PLB_ORCHESTRATOR + AG-01 a AG-07). Decisiones de pricing y rate limiting [PENDIENTE — NO INVENTAR] hasta input CEO.
