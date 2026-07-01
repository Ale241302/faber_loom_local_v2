---
id: SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom
type: schema
stamp: VIGENTE 2026-05-03

# Nota PR-3 AUDIT_REINDEXA 2026-05-03: domain corregido `Plataforma`→`FaberLoom` para
# consistencia con scope (path docs/faberloom/) y con los otros 4 SCH_FB_*. Bumpeo
# patch v1.0→v1.1. Sin cambios de contenido.
fecha: 2026-04-30
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R2+R3)
aplica_a: [FaberLoom]
implementa: ENT_FB_VERTICAL_SPEC_OBJECT_v1 (campos parametrizables)
relacionado_con:
  - ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1
  - ENT_FB_COMMERCIAL_AUTHORITY_MATRIX_v1
  - ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1
  - SPEC_AUDIT_MODULE (SHA-chain integrity)
---

# SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1
## Schema obligatorio del bundle de evidencia por output de cotizacion

## 1. Proposito

Cada output de cotizacion (proforma, draft, alarma con propuesta) genera un **evidence bundle** que documenta:
- Que fuente se uso para cada dato critico
- Que reglas se aplicaron
- Que decisiones de autoridad pasaron
- Que excepciones aparecieron
- Hash de integridad para audit trail

Sin evidence bundle, una cotizacion incorrecta tiene **apariencia de autoridad** y puede generar promesa comercial falsa (R2 Riesgo 2).

> **Insight ChatGPT R2 Riesgo 2:** "El agente puede preparar una proforma convincente con stock viejo, precio vencido o equivalencia ASTM incorrecta. Ese error no parece bug · parece promesa comercial."

## 2. Granularidad obligatoria · per-line + per-quote

R2 corrigió esto explicitamente: una cotizacion mixta puede tener una linea solida, otra con stock parcial y otra con sustitucion. Bundle solo per-quote oculta heterogeneidad.

```yaml
quote_evidence_bundle:
  schema_version: 1.0
  bundle_id: <uuid>
  
  # Per-line: 1 entrada por SKU/linea cotizada
  lines:
    - line_id: <uuid>
      sku: string
      sku_version: string
      
      technical_spec_rule:  # ex ASTM_rule literal
        rule_name: string  # resuelve via vertical_spec_object.technical_spec_rule.name
        rule_version: string
        validation_status: enum  # passed · warning · failed
        evidence_doc_ref: string?  # link a doc tecnico
      
      pricing:
        unit_price: number
        currency: string
        list_version: string  # version del precio source
        list_freshness_seconds: int
        discount_applied_percent: number
        discount_reason: string?
        margin_calculated: number
        margin_floor_check: enum  # above · at_floor · below_floor
      
      stock:
        source_stock: enum  # ERP · 3PL · contradiction_resolved
        timestamp_stock: ISO8601
        stock_freshness_seconds: int
        fulfillable_qty: int
        reserved_for_this_quote: int
      
      lead_time:
        days: int
        source_lead_time: enum  # proveedor · 3PL · catalogo
        confidence: enum  # high · medium · low
        last_confirmed: ISO8601
      
      moq_packaging:
        moq_required: int
        moq_satisfied: boolean
        packaging_unit: string
        packaging_rule_applied: string
      
      freight_assignment:
        freight_quote_ref: string?
        applies_to_this_line: boolean
        weight_kg: number
        cbm: number
      
      sku_status: enum  # active · discontinued · phasing_out
      
      cert_doc_version:
        cert_type: string  # del vertical_spec_object.certification_requirements
        version: string
        validity_until: ISO8601
        document_url: string?
        validation_status: enum
      
      country_rule_applied:
        country: string
        rules_matched: array<string>
        special_doc_required: array<string>
      
      customer_terms_ref:
        terms_id: string
        payment_terms: string
        credit_check_passed: boolean
      
      currency_fx_rate:  # solo si moneda local distinta a USD
        pair: string
        rate: number
        source: string
        timestamp: ISO8601
      
      exception_codes: array<string>  # excepciones disparadas en esta linea
      
      approver: string  # quien aprobo esta linea (puede ser AM si bundle interno)
      approved_at: ISO8601
      
      fallback_used: object?  # si se uso fallback en algun paso
        layer: string  # ej. "stock falled to backup_3pl"
        reason: string

  # Per-quote: agregado de la cotizacion completa
  quote_summary:
    quote_id: <uuid>
    customer_id: string
    
    vigencia:
      valid_until: ISO8601
      vigencia_days: int
      extension_allowed: boolean
    
    moneda_total:
      currency: string
      total_subtotal: number
      total_discount: number
      total_tax: number
      grand_total: number
    
    incoterm_pais:
      incoterm: string
      country_origin: string
      country_destination: string
    
    margen_global: number  # weighted avg de margenes per-line
    
    credito_check:
      customer_credit_status: enum  # ok · warning · blocked
      credit_limit: number
      credit_used_after_quote: number
      credit_check_passed: boolean
    
    flete_total:
      total_freight: number
      currency: string
      includes_special_handling: array<string>
    
    aprobador_final: string
    approval_history:
      - level: string  # AM · AM_supervisor · CEO
        approver: string
        action: enum  # approved · edited · rejected
        timestamp: ISO8601
        notes: string?
    
    exceptions_total: array<string>  # union de exception_codes per-line + quote-level
    
    severity_max: enum  # max severity entre todas las excepciones
    severity_weight_sum: int  # suma ponderada
    
    hitl_gates_triggered:
      - gate_name: string
        triggered_at: ISO8601
        resolved_by: string
    
    hash_paquete: string  # SHA-256 del bundle completo · audit integrity
    
    chain_prev_hash: string?  # SHA del bundle previo en la chain (audit log)

  # Metadata
  generated_by:
    archetype: string  # ej. AG_AM_MWT
    sub_agents_invoked: array<{name, version, latency_ms, cost_usd}>
    total_cost_usd: number
    total_latency_ms: int
  
  generated_at: ISO8601
  trace_id: string
  
  privacy_classification:
    inputs_tier: enum  # PRIVATE_RAW · TENANT_DERIVED · GLOBAL_PROMOTABLE · RESTRICTED_SENSITIVE_OR_REGULATED
    outputs_tier: enum
    cross_tenant_eligibility: boolean
```

## 3. 3 vistas del bundle

### 3.1 Vista cliente final (resumen filtrado)

Lo que el cliente recibe junto con la proforma:

```yaml
client_visible_evidence:
  vigencia: <date>
  disponibilidad_per_line:
    - sku: string
      quantity_available: int
      lead_time_days: int
      condicion: enum  # full · partial · on_request
  condiciones_comerciales:
    payment_terms: string
    incoterm: string
  sustituciones_explicitas:
    - original_sku: string
      substituted_sku: string
      reason: string
      authority_approval: string
  notas_tecnicas_relevantes: array<string>  # solo si afectan al cliente
```

**NO incluye:** margen · fuentes internas · fallback interno · scoring agente · authority chain interna · sub-agentes invocados.

### 3.2 Vista interna (bundle completo + audit log)

Toda la estructura YAML de Seccion 2. Acceso: AM + supervisor + CEO + auditor del tenant.

### 3.3 Vista audit (full + SHA chain + provenance)

Vista interna + chain de hashes para integridad temporal:

```yaml
audit_view:
  bundle: <full bundle from section 2>
  chain:
    prev_bundle_hash: string
    this_bundle_hash: string
    next_bundle_hash: string?  # si ya hay siguiente
  signed_by: string  # quien firmo digitalmente
  signed_at: ISO8601
  signature_algorithm: string  # ej. ed25519
  signature: string
```

Acceso: solo auditor del tenant + CEO + compliance officer si aplica.

## 4. Comportamiento generacion

```
1. AG_SUB_PROFORMA_BUILDER (o AG_SUB_DRAFT_WRITER en F1) genera output
2. Sistema construye evidence bundle paralelo a output:
   ├─ Recolecta fuentes consultadas (audit del Source of Truth)
   ├─ Captura authority decisions del flow
   ├─ Suma exception_codes disparadas
   ├─ Calcula severity_weight_sum
   ├─ Genera hash SHA-256 del bundle
   └─ Persiste en audit log
3. Output cliente lleva referencia al evidence_bundle_id
4. AM al revisar tiene acceso a vista interna completa
5. Cliente al recibir solo ve vista cliente final
```

## 5. Reglas inquebrantables

1. **Cliente NUNCA ve bundle completo.** Vista cliente final es lo unico filtered apropiado.
2. **Hash es obligatorio.** Sin hash · bundle invalido · output bloqueado.
3. **Per-line obligatorio para cotizaciones >1 SKU.** Bundle solo per-quote = bug critical.
4. **Bundle es immutable post-firma.** Cualquier edit del output post-firma genera bundle nuevo (con prev_hash referenciando el anterior).
5. **Provenance obligatoria.** Cada dato del bundle debe trazar a su fuente · sin source = bundle incompleto.
6. **Severity_weight_sum se calcula SIEMPRE** · aunque sum=0 (sin excepciones).
7. **Privacy_classification obligatoria.** Tier de inputs y outputs declarado · sin clasificacion = no se persiste.

## 6. Validacion automatica del bundle

Antes de firma final, sistema valida:

```yaml
validations:
  - all_lines_have_pricing: boolean
  - all_lines_have_stock: boolean
  - all_lines_have_technical_spec_rule: boolean
  - all_critical_lines_have_cert_doc_version: boolean  # si vertical lo requiere
  - hash_matches_content: boolean
  - signature_valid: boolean
  - privacy_tier_coherent: boolean  # outputs_tier <= inputs_tier
  - authority_chain_complete: boolean  # cada decision tiene approver
```

Si CUALQUIER validacion falla → bundle rechazado · output bloqueado · log severity:critical.

## 7. Audit log integration

El bundle se persiste en `SPEC_AUDIT_MODULE` con SHA-chain. Cada bundle es nodo en la chain de audit del tenant. Ruptura de chain = alarma critica al curador.

## 8. Pendientes v1.1

1. Bundle compresion (algunos bundles seran grandes en cotizaciones de 50+ lineas)
2. Bundle versioning explicito (re-cotizaciones con cambios trazables)
3. Bundle visualization para cliente (PDF render con resumen filtrado)
4. Bundle search/query API (para AM revisando historico)
5. Bundle export para auditores externos (formato estandar)

## Changelog
- 2026-04-30 v1.0 VIGENTE: Creacion inicial post R2+R3. 18 campos canonicos divididos per-line (10 grupos) + per-quote (10 grupos). 10 campos agregados en R2 (source_stock · source_lead_time · sku_status · cert_doc_version · country_rule_applied · freight_quote_ref · MOQ_packaging_rule · currency_fx_rate · customer_terms_ref · exception_codes). 3 vistas (cliente filtered · interno completo · audit con SHA-chain). Validacion automatica pre-firma con 8 checks. Privacy_classification obligatoria. Hash SHA-256 obligatorio · bundle invalid si falta. Per-line obligatorio para multi-SKU (insight R2 explicit · cotizacion mixta tiene heterogeneidad).

## Stamp
VIGENTE 2026-04-30 — Schema fundacional para auditabilidad de cotizaciones B2B. Mitiga R2 Riesgo 2 (cotizacion incorrecta con apariencia de autoridad). 3 vistas separan necesidades cliente / interno / audit. SHA-chain integra con SPEC_AUDIT_MODULE.
