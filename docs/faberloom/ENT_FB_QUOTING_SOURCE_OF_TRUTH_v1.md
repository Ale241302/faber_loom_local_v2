---
id: ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-05-01 (v1.1 post review R4)
fecha: 2026-05-01
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R1+R2+R3+R4)
aplica_a: [FaberLoom]
implementa: ENT_FB_VERTICAL_SPEC_OBJECT_v1 (parametrizacion per vertical)
relacionado_con:
  - ENT_FB_VERTICAL_SPEC_OBJECT_v1
  - ENT_FB_COMMERCIAL_AUTHORITY_MATRIX_v1
  - ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1
  - SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1
---

# ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1
## Fuentes canonicas de verdad operacional para cotizacion B2B

## 1. Proposito

Define las **14 fuentes de verdad** que el sistema FaberLoom consulta para construir una cotizacion B2B. Cada fuente tiene:
- Identificador canonico
- Tipo de dato
- Regla de freshness (SLA maximo de antiguedad)
- Fuente origen (ERP · 3PL · catalogo · proveedor · finance · etc)
- Regla de prelacion cuando dos fuentes contradicen
- Estado parametrizable por `vertical_spec_object`

> **Insight ChatGPT R2:** "El punto debil no es falta de IA · es control de verdad operacional. ASTM, stock disponible, precio aprobado, lead time y version de proforma. Si eso queda liquido, los sub-agentes solo automatizan ambiguedad con traje nuevo."

## 2. Las 14 fuentes canonicas

### 2.1 Catalogo de productos
- **Tipo:** lista de SKU con metadatos (`description, category, manufacturer, vertical_spec_fields`)
- **Origen:** SAP material master · sistema interno tenant
- **Freshness SLA:** `max_age = 30d` · STALE_WARNING si >30d · FAIL_AM_REVIEW si >90d
- **Parametrizable:** los campos `vertical_spec_fields` se determinan por `vertical_spec_object.variant_dimension` y `technical_spec_rule`

### 2.2 Vertical spec object (parametrizacion universal)
- **Tipo:** `vertical_spec_object` per tenant
- **Origen:** config tenant onboarding
- **Freshness SLA:** versionado · cambios requieren SHADOW 30d
- **Reemplaza el campo "ASTM" hardcoded** del modelo R1+R2 · ahora es `technical_spec_rule` resoluble per vertical

### 2.3 Stock disponible (ATP · available-to-promise)
- **Tipo:** `{sku, warehouse, available_qty, reserved_qty, in_transit_qty}`
- **Origen:** ERP (SAP MM) + 3PL si aplica
- **Freshness SLA:** 
  - `≤5min` ideal
  - `STALE_WARNING` si entre 5-15min
  - `FAIL_AM_REVIEW` si >60min
- **Regla prelacion:** fuente fisica ejecutora (3PL) GANA sobre ERP en despacho inmediato · ERP gana en planning
- **Regla contradiccion 2 fuentes:** `fulfillable_qty = min(ERP_allocatable, 3PL_available)` · disparar excepcion si `delta >5%` o `delta >25 unidades`

### 2.4 Precio vigente (lista comercial)
- **Tipo:** `{sku, list_price, currency, version, effective_date, expiry_date}`
- **Origen:** SAP price list · sistema pricing tenant
- **Freshness SLA:** `≤24h` · disparar `PRICE_STALE` si >24h · `FAIL` si >72h
- **Regla prelacion:** lista comercial aprobada vigente GANA sobre precio historico · GANA sobre precio negociado expirado

### 2.5 Descuentos autorizados
- **Tipo:** `{discount_type, percent, condition, account_tier_applicable, sku_filter}`
- **Origen:** sistema pricing · finance approval matrix
- **Freshness SLA:** `≤24h`
- **Vinculado:** Authority Matrix decide si requiere aprobacion supervisor

### 2.6 Margen minimo vigente
- **Tipo:** `{sku_or_category, margin_floor_percent, applicable_segment}`
- **Origen:** finance · CEO override possible
- **Freshness SLA:** `≤24h`
- **Vinculado:** disparar `MARGEN_BAJO` excepcion si calculo final < floor

### 2.7 FX / moneda de cotizacion
- **Tipo:** `{currency_pair, rate, source, timestamp}`
- **Origen:** banco central pais · proveedor FX corporativo
- **Freshness SLA:** `≤1h` para cotizaciones en moneda local · `≤24h` para USD-pegged
- **Critico LATAM:** monedas con volatilidad alta (`vertical_spec_object.pricing_overrides.fx_volatility_class`) requieren freshness mas estricto

### 2.8 Flete
- **Tipo:** `{origin, destination, weight_kg, cbm, mode, rate, valid_until}`
- **Origen:** carrier API · contrato 3PL
- **Freshness SLA:**
  - flete spot: `≤48h`
  - flete contractual: `≤30d`
- **Regla:** disparar `FREIGHT_NOT_QUOTED` si destino no en cobertura · escalar AM

### 2.9 MOQ y packaging
- **Tipo:** `{sku, moq, packaging_unit, units_per_packaging, mixed_pallet_allowed}`
- **Origen:** catalogo + reglas comerciales tenant
- **Freshness SLA:** `≤30d`
- **Vinculado:** disparar `MOQ_PACKAGING_INCOMPATIBLE` si pedido < MOQ o requiere mixto no permitido

### 2.10 Lead time
- **Tipo:** `{sku, lead_time_days, source, confidence, last_confirmed}`
- **Origen:** proveedor (mas autoritativo) · 3PL · catalogo (default)
- **Freshness SLA:** `≤24h` para SKU activos · `≤7d` para SKU stock
- **Regla prelacion:** proveedor GANA sobre 3PL GANA sobre AM-promesa GANA sobre default catalogo
- **Vinculado:** disparar `LEAD_TIME_INCIERTO` si confidence baja o source >SLA

### 2.11 Vigencia de oferta
- **Tipo:** `{quote_id, valid_until, extension_allowed, extension_authority}`
- **Origen:** politica comercial tenant
- **Default:** 30 dias salvo configuracion contraria
- **Vinculado:** disparar `PROFORMA_VENCIDA` cuando intent=update_quote y vigencia expiro

### 2.12 Customer terms · credit status
- **Tipo:** `{customer_id, payment_terms, credit_limit, credit_used, credit_status, special_terms}`
- **Origen:** finance / ERP customer master
- **Freshness SLA:** `≤4h` para credit_status · `≤24h` para terms estaticos
- **Vinculado:** disparar `CREDITO_BLOQUEADO` si status=blocked · FAIL absoluto + escalar AM/supervisor

### 2.13 Tax · incoterm · country rules
- **Tipo:** `{country, tax_codes, incoterm_options, restrictions, special_docs_required}`
- **Origen:** sistema fiscal tenant · DB regulatoria
- **Freshness SLA:** `≤30d` para tax · `≤90d` para incoterm · `≤7d` para restrictions
- **Vinculado:** disparar `REGLA_PAÍS_ESPECIAL` si destino requiere doc adicional

### 2.14 Certificaciones · documentos tecnicos
- **Tipo:** `{sku, cert_type, version, issuer, validity_until, document_url}`
- **Origen:** catalogo + proveedor + lab acreditado
- **Freshness SLA:** `≤180d` o antes si proveedor emite version nueva
- **Parametrizable:** los `cert_type` exigidos vienen de `vertical_spec_object.certification_requirements`
- **Vinculado:** disparar `CERT_DOC_FALTANTE` (Critical · FAIL) si mandatory_for_sale=true y vencido

### 2.15 Dimensiones · peso · CBM por SKU
- **Tipo:** `{sku, weight_kg, length_mm, width_mm, height_mm, cbm}`
- **Origen:** catalogo
- **Freshness SLA:** `≤30d`
- **Vinculado:** input para flete (#2.8) y MOQ (#2.9) y packaging logistico

## 3. Reglas de prelacion universales

Cuando dos fuentes contradicen sobre el mismo dato, aplicar regla canonica:

| Dominio | Regla prelacion |
|---|---|
| Stock | Fuente fisica ejecutora (3PL fulfilment) GANA sobre ERP si despacho inmediato. ERP GANA en planning >7d. |
| Precio | Lista comercial aprobada vigente GANA sobre precio historico GANA sobre precio negociado expirado. |
| Lead time | Proveedor GANA sobre 3PL GANA sobre promesa AM GANA sobre default catalogo. |
| Credito | Finance/ERP GANA sobre AM. AM nunca puede sobrescribir credit_status. |
| Cert/docs | Lab acreditado GANA sobre proveedor self-issued GANA sobre catalogo. |
| FX | Banco central GANA sobre proveedor FX corporativo en cotizaciones >$X. |

## 4. Comportamiento ante freshness violations

```
SLA OK  → operacion continua normal
STALE_WARNING → continua + flag en evidence_bundle + log
FAIL_AM_REVIEW → bloquea uso fuente · disparar excepcion · escalar AM
```

Ejemplo stock:
```
freshness 3min → ok
freshness 12min → STALE_WARNING · sigue · evidence bundle marca "stock checked 12 min ago"
freshness 75min → FAIL · no usa stock · disparar excepcion · AM revisa manualmente
```

## 5. Estructura YAML del config per tenant

```yaml
sources_of_truth_config:
  tenant_id: mwt
  vertical_spec_object: safety_footwear  # ref ENT_FB_VERTICAL_SPEC_OBJECT
  
  catalog:
    source_system: sap_mm
    refresh_interval_minutes: 360
    
  stock:
    primary_source: sap_mm
    secondary_sources: [3pl_dhl, 3pl_estafeta]
    sla_max_minutes: 5
    stale_threshold_minutes: 15
    fail_threshold_minutes: 60
    contradiction_rule: min_with_alert
    contradiction_threshold_percent: 5
    contradiction_threshold_units: 25
    
  pricing:
    primary_source: sap_pricing_master
    sla_max_hours: 24
    stale_action: warn
    fail_threshold_hours: 72
    
  fx:
    primary_source: banco_central_mx
    secondary_source: corporate_fx_provider
    sla_max_hours: 1
    
  # ...resto de fuentes
```

## 6. Logging y audit

Cada acceso a fuente genera audit event:
```yaml
event: source_accessed
source_id: stock
sku: BC-7240
freshness_seconds: 187
result: ok
caller: AG_SUB_INVENTORY_FETCHER
trace_id: <id>
timestamp: <ISO8601>
```

Eventos `STALE_WARNING` y `FAIL` agregan campos:
- `severity`
- `excepcion_disparada` (si aplica)
- `escalation_required` (boolean)

## 7. Fuentes agregadas v1.1 (post review R4 · gaps Ciclope)

### 7.1 Fuente #15 · freight_international (gap GAP-001 R3 · case_15)

```yaml
fuente_15_freight_international:
  tipo: lista de carrier APIs (DHL · FedEx · Expeditors · Maersk LCL)
  origen: integracion carrier APIs
  freshness_SLA: 24h spot · 30d contractual
  estado_v1: workaround manual AM (no integrado · evidence_gap automatico)
  v1_priority: medium
  v2_accion: integrar 1+ carrier API
  vertical_applicable: todos
```

Comportamiento v1: si RFQ requiere flete internacional (origen ≠ destino pais) y no hay flete cotizado · disparar excepcion `FREIGHT_NOT_QUOTED` · escalar AM · documentar en evidence bundle como evidence_gap.

### 7.2 Fuente #16 · freight_MX_routes (gap GAP-SF-001 safety_footwear · case_sf_05)

```yaml
fuente_16_freight_MX_routes:
  tipo: tarifario flete MX por ruta
  rutas_canonicas: [CDMX→Saltillo, CDMX→Queretaro, CDMX→Monterrey, CDMX→Guadalajara, CDMX→Tijuana]
  origen: 3PL Mexico (DHL Supply Chain · Estafeta Industrial · Castores)
  freshness_SLA: 30d standard · 24h promociones spot
  estado_v1: 3PL generico cubre · AM gestiona casos especiales
  v1_priority: low (clasificacion R4: commercial_margin_sensitive)
  v2_accion: tarifario diferenciado por ruta cuando volumen justifique
  vertical_applicable: safety_footwear primer caso · escalable
```

R4 ajuste: aunque priority es `low` para integracion v1.1 · clasificar impacto como `commercial_margin_sensitive` · sistema NO trata flete MX como detalle cosmetico · siempre va a evidence bundle.

## 8. Reglas prelacion ampliadas (incluye flete · v1.1)

```
flete:
  carrier API (live) > 3PL contractual > 3PL spot > AM-promesa
  
AM-promesa: fuente MANUAL de baja autoridad y freshness explicita.
Si AM promete flete sin respaldo carrier/3PL → genera `evidence_gap`
en el bundle · NO pasa como verdad operacional.

(R4 microaclaracion: AM-promesa NO es equivalente a otras fuentes ·
es manual con autoridad limitada · debe quedar etiquetada explicitamente.)
```

## 9. Pendientes v1.2

1. Sources adicionales para verticals especificos (ej. lote/vencimiento para medico/quimico)
2. Health monitoring dashboard de cada fuente · alertas si SLA breach >X% requests
3. Auto-failover entre fuentes (3PL primario down → 3PL backup automatico)
4. Versioning explicito de catalogo con diff per change
5. Integracion carrier API real (freight_international v2)
6. Tarifario MX diferenciado por ruta (freight_MX_routes v2)

## NO IMPLICA (R4 bonus 5%/50%)

`ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1` v1.1 fuentes flete **NO implican integracion carrier en v1**. Las fuentes 15 y 16 estan declaradas como capability del sistema · pero el estado v1 es workaround manual AM con `evidence_gap` documentado. Integracion carrier API real queda a v2 cuando volumen justifique.

## Changelog
- 2026-05-01 v1.1 VIGENTE: Indexa-e backend post review R4. Agregadas 2 fuentes nuevas (15 freight_international gap GAP-001 R3 · 16 freight_MX_routes gap GAP-SF-001 safety_footwear). Microaclaracion sobre AM-promesa como fuente manual de baja autoridad (R4) · genera evidence_gap si sin respaldo. Reglas prelacion ampliadas para flete. Total fuentes 14 → 16. NO implica integracion carrier en v1 · workaround manual + evidence_gap documentado. Estado v1 ambas en workaround AM · v2 integracion real cuando volumen justifique.
- 2026-04-30 v1.0 VIGENTE: Creacion inicial post-auditorias R1+R2+R3. 14 fuentes canonicas con freshness SLA per dominio · reglas prelacion universales · 5 agregadas en R2 (customer_terms · tax_incoterm · certs · CBM · FX) · vertical_spec_object integrado para parametrizacion per industria (no hardcoded calzado/ASTM) · regla contradiccion stock canonizada (`min(ERP, 3PL)` con threshold 5%/25 unidades) · estructura YAML config tenant + audit event schema.

## Stamp
VIGENTE 2026-05-01 v1.1 — Pieza foundational del wedge cotizacion B2B. v1.1 amplia con 2 fuentes flete + microaclaracion AM-promesa de baja autoridad. Sin source of truth bien parametrizada · sub-agentes "automatizan ambiguedad con traje nuevo" (R2).
