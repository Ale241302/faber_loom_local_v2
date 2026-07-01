---
id: ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-04-30
fecha: 2026-04-30
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R2+R3)
aplica_a: [FaberLoom]
implementa: ENT_FB_VERTICAL_SPEC_OBJECT_v1 (parametrizacion per vertical)
relacionado_con:
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1
  - ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1
  - ENT_FB_COMMERCIAL_AUTHORITY_MATRIX_v1
  - SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1
  - ENT_FB_SUB_AGENTS_LIBRARY_v1 (handlers per excepcion)
---

# ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1
## 15 excepciones canonicas con severity_weight y handler

## 1. Proposito

Define el set canonico de excepciones que el sistema FaberLoom debe identificar y manejar durante el flow de cotizacion. Sin taxonomia cerrada, los sub-agentes "improvisan con confianza" (R2).

15 excepciones · cada una con:
- Codigo canonico (estable cross-version)
- Severity weight (Low / Medium / High / Critical)
- Handler obligatorio (FAIL+notif AM vs propuesta+escalacion)
- Required approver
- Vertical applicability (universal o vertical-specific)

> **Insight ChatGPT R3:** "Severity > acceptance rate. Un agente puede tener buen acceptance rate y aun asi cometer errores no tolerables en cumplimiento, credito o especificacion."

## 2. Las 15 excepciones canonicas

### 2.1 TECHNICAL_SPEC_AMBIGUOUS (era ASTM_AMBIGUO)
- **Severity:** High
- **Trigger:** spec tecnica solicitada no resuelve a una norma especifica del `vertical_spec_object.technical_spec_rule`
- **Handler:** propuesta + escalacion AM
- **Required approver:** AM
- **Vertical:** universal · resuelve via `vertical_spec_object`
- **Ejemplo wedge MWT:** "necesito calzado certificado" (no especifica ASTM F2413-18 vs F2413-11)
- **Ejemplo cross-vertical EPP:** "respiradores N95 para vapores organicos" (mismatch · N95 no es organic vapor)

### 2.2 SKU_DISCONTINUADO
- **Severity:** Medium
- **Trigger:** SKU solicitado tiene status=discontinued en catalogo
- **Handler:** propuesta + escalacion AM (con sustituto si existe)
- **Required approver:** AM
- **Vertical:** universal

### 2.3 STOCK_PARCIAL
- **Severity:** Medium (Low si <10% pedido · High si >50% pedido)
- **Trigger:** `fulfillable_qty < requested_qty`
- **Handler:** propuesta + escalacion AM
- **Required approver:** AM (auto-escalar a supervisor si >50% del pedido)
- **Vertical:** universal

### 2.4 VARIANT_DIMENSION_MISSING (era TALLA_FALTANTE)
- **Severity:** Medium
- **Trigger:** variante solicitada (`variant_dimension.primary` o `secondary`) sin stock
- **Handler:** propuesta + escalacion AM (con alternativas variant)
- **Required approver:** AM
- **Vertical:** universal · resuelve via `vertical_spec_object.variant_dimension`
- **Ejemplo wedge MWT:** "talla 25 sin stock"
- **Ejemplo cross-vertical eléctrico:** "cable AWG #4 sin stock"

### 2.5 SUSTITUCION_ACEPTABLE
- **Severity:** Medium-High
- **Trigger:** cliente pide "X o similar" o sistema detecta equivalencia tecnica certificada
- **Handler:** propuesta + escalacion AM
- **Required approver:** AM (supervisor si cambia certificacion · ver Authority Matrix)
- **Vertical:** universal · validado contra `vertical_spec_object.compatibility_matrix`

### 2.6 CREDITO_BLOQUEADO
- **Severity:** **Critical**
- **Trigger:** `customer.credit_status = blocked` o credit excedido
- **Handler:** **FAIL + notif AM** (NO propuesta · bloqueo absoluto)
- **Required approver:** AM + supervisor
- **Vertical:** universal
- **Audit:** evento severity:critical · NUNCA generar proforma final

### 2.7 PROFORMA_VENCIDA
- **Severity:** Medium
- **Trigger:** referencia a proforma con `valid_until < now`
- **Handler:** propuesta + escalacion AM (regenerar con precios actuales)
- **Required approver:** AM
- **Vertical:** universal

### 2.8 PEDIDO_MIXTO
- **Severity:** Low-Medium
- **Trigger:** RFQ contiene SKU de multiples proveedores/familias
- **Handler:** propuesta + escalacion AM (split o consolidado segun politica)
- **Required approver:** AM
- **Vertical:** universal · mas comun en MRO/ferreteria

### 2.9 FLETE_NO_COTIZADO
- **Severity:** Medium
- **Trigger:** destino fuera de cobertura · weight/CBM excede categoria · servicios especiales (descarga · grua)
- **Handler:** propuesta + escalacion AM (con flete pendiente o quote externo)
- **Required approver:** AM
- **Vertical:** universal

### 2.10 MARGEN_BAJO
- **Severity:** **Critical**
- **Trigger:** margen calculado < `vertical_spec_object.pricing_overrides.margin_floor_default`
- **Handler:** **FAIL + notif AM**
- **Required approver:** AM + supervisor (CEO si bajo umbral hard)
- **Vertical:** universal

### 2.11 REGLA_PAÍS_ESPECIAL
- **Severity:** High-Critical (depende del pais y restriccion)
- **Trigger:** destino requiere doc adicional · permiso especial · restriccion exportacion
- **Handler:** FAIL + notif AM si critica · propuesta + escalacion si moderada
- **Required approver:** AM + supervisor (siempre que sea critica)
- **Vertical:** universal · alta intensidad en medico/electrico/quimico

### 2.12 PRECIO_VENCIDO
- **Severity:** **High**
- **Trigger:** lista precios vigente >`24h` (FAIL si >`72h`)
- **Handler:** **FAIL + notif AM** (NO cotizar con precio stale)
- **Required approver:** AM
- **Vertical:** universal
- **Critico:** R2 marco esto como excepcion separada porque "stock fresco no arrastra precio vencido"

### 2.13 LEAD_TIME_INCIERTO
- **Severity:** Medium
- **Trigger:** lead_time source confidence baja · o source >SLA
- **Handler:** propuesta + escalacion AM (con plazo condicionado · "sujeto a confirmacion")
- **Required approver:** AM
- **Vertical:** universal · alta intensidad en electrico industrial

### 2.14 CERT_DOC_FALTANTE (era CERTIFICACION_FALTANTE)
- **Severity:** **Critical**
- **Trigger:** SKU requiere cert (`vertical_spec_object.certification_requirements[mandatory_for_sale=true]`) y doc faltante o vencido
- **Handler:** **FAIL + notif AM** (no cotizar producto sin documentacion regulatoria)
- **Required approver:** AM (supervisor + compliance officer si vertical regulado)
- **Vertical:** universal · CRITICO en medico (registro sanitario) · quimico (NIOSH/EN) · electrico (IEC/NEMA)

### 2.15 MOQ_PACKAGING_INCOMPATIBLE
- **Severity:** Medium
- **Trigger:** pedido < MOQ · o requiere mixto no permitido en pallet
- **Handler:** propuesta + escalacion AM (sugerir aumentar cantidad · split · alternativa)
- **Required approver:** AM
- **Vertical:** universal

## 3. Severity weight transversal (R3 critical insight)

```
Low      = 1   # cosmetico, redaccion, follow-up
Medium   = 3   # stock parcial, flete, lead time
High     = 7   # precio, margen, sustitucion tecnica
Critical = 15  # compliance, seguridad, registro, promesa contractual
```

Severity weight se usa transversalmente en:
- **Replay Set** · sub-split obligatorio Critical/High no menos del 30% del pool
- **P15 outcome accountability** · evaluacion ponderada por severidad (1 error critical pesa 15× un error low)
- **Optimizer Telar** · ranking modelos pondera por severidad de errores cometidos
- **Audit log** · queries priorizadas por severity_sum

## 4. Regla handler universal

```
Si la excepcion compromete dinero, legalidad, seguridad tecnica
o promesa comercial → FAIL + notif AM

Si puede generar alternativa verificable sin comprometer estos
→ propuesta + escalacion AM
```

| Compromete... | Handler |
|---|---|
| Dinero (credito · margen · precio stale · monto) | FAIL |
| Legalidad (cert faltante · regla pais critica · contrato penalidad) | FAIL |
| Seguridad tecnica (sustitucion no identica · spec ambigua que afecta proteccion) | FAIL |
| Promesa comercial (entrega contractual · stock parcial >50%) | FAIL |
| Operacional manejable (talla faltante · flete pendiente · MOQ · pedido mixto) | propuesta+escalacion |

## 5. Output schema obligatorio per excepcion

Cada excepcion disparada genera estructura:

```yaml
exception:
  exception_code: enum  # uno de los 15
  severity: enum  # low | medium | high | critical
  severity_weight: int  # 1 | 3 | 7 | 15
  blocking: boolean  # true si handler=FAIL
  recommended_action:
    type: enum  # request_clarification | propose_alternative | escalate | block_with_reason
    target: enum  # AM | supervisor | CEO | finance | compliance_officer
    payload: object  # detalle especifico
  required_approver: array<enum>  # ej. ["AM", "supervisor"]
  evidence_refs:
    sources_consulted: array<string>  # ref a Source of Truth ids
    timestamps: object
    contradictions_found: array<object>  # si aplica
  trace_id: string
  raised_by: string  # sub-agente que detecto
  raised_at: ISO8601
```

## 6. Vertical-specific exceptions (extension v1.1)

Algunas verticals tienen excepciones que no caben en las 15 universales. Se agregan via `vertical_spec_object` extensions:

| Vertical | Excepciones adicionales |
|---|---|
| medical_regulated | LOTE_VENCIMIENTO_INSUFICIENTE · COA_FALTANTE · LICITACION_PENALIDAD |
| chemical_PPE | INCOMPATIBILIDAD_QUIMICA · CARTUCHO_INCORRECTO_PARA_AGENTE |
| MRO_industrial | OEM_CROSSREF_NO_DISPONIBLE · COMPATIBILITY_INCOMPLETE |
| electrical_technical | TENSION_FASE_INCOMPLETA · CAPACIDAD_INSUFICIENTE · CURVA_KAIC_NO_ESPECIFICADA |
| construction_supply | OBRA_LOGISTICA_NO_COTIZADA · DESCARGA_NO_INCLUIDA |

Estas extensiones se canonizan cuando el vertical entra a produccion. NO entran en v1.

## 7. Logging de excepciones

```yaml
event: exception_raised
exception_code: CERT_DOC_FALTANTE
severity: critical
severity_weight: 15
blocking: true
trace_id: <id>
raised_by: AG_SUB_COMPLIANCE_CHECKER (profile: medical_regulated)
sub_agent_confidence: 0.92
caller_archetype: AG_AM_MWT
raised_at: <ISO8601>
escalation_triggered: true
escalated_to: ["alvaro@mwt.cr", "compliance@mwt.cr"]
```

Audit log con SHA-chain.

## 8. Reglas inquebrantables

1. **15 excepciones es lista cerrada en v1.** Excepciones nuevas requieren bump v1.1 · NO se agregan en runtime.
2. **Handler FAIL es absoluto.** Si dispara FAIL · NO se cotiza · sin importar lo que diga el sub-agente.
3. **Severity weight es inmutable.** No se ajusta per tenant (consistencia P15).
4. **Critical exceptions SIEMPRE escalan a humano.** Ningun bypass · ningun timeout auto-aprueba.
5. **Vertical-specific exceptions se canonizan separado** · no contaminan las 15 universales.
6. **Excepciones no detectadas son bug · no excepcion.** Si AM detecta caso que no matcheo a las 15 · revisar coverage en next version.

## 9. Pendientes v1.1

1. Vertical-specific exceptions per vertical activado
2. Composicion de excepciones (cuando 2+ disparan simultaneo · prioridad y handler combinado)
3. Auto-suggestion de alternativas con LLM cuando handler=propuesta
4. Dashboard analitico de excepciones mas frecuentes per vertical
5. Replay set sub-split obligatorio por excepcion mayoritaria

## Changelog
- 2026-04-30 v1.0 VIGENTE: Creacion inicial post R2+R3. 15 excepciones canonicas con severity_weight (Low=1 · Medium=3 · High=7 · Critical=15) · 4 agregadas en R2 (precio_vencido · lead_time_incierto · cert_doc_faltante · moq_packaging_incompatible) · 4 renombradas para vertical_spec_object (TECHNICAL_SPEC_AMBIGUOUS · VARIANT_DIMENSION_MISSING · CERT_DOC_FALTANTE · COMPATIBILITY_INCOMPLETE en vertical-specific) · regla handler universal canonizada (compromete dinero/legalidad/seguridad/promesa = FAIL · operacional manejable = propuesta+escalacion) · output schema obligatorio · lista de extensions vertical-specific para v1.1 · 6 reglas inquebrantables · severity weight integrada con Replay Set + P15 + Optimizer.

## Stamp
VIGENTE 2026-04-30 — Lista cerrada de excepciones para v1. Severity weight transversal protege wedge contra agentes "comodos pero peligrosos" (R3). Vertical-specific extensions diferidas a v1.1 cuando aparezca tenant del vertical correspondiente.
