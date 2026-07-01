---
id: ENT_FB_VERTICAL_SPEC_OBJECT_v1
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-05-01 (v1.1 post review R4 + Ciclope safety_footwear)
fecha: 2026-05-01
agente: Cowork (redaccion) + CEO (decisiones) + ChatGPT (auditoria R3+R4) + Ciclope (10 fixtures safety_footwear)
aplica_a: [FaberLoom]
origen: Auditoria R3 - hallazgo "MWT como adapter, no core"
relacionado_con:
  - ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1
  - ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1
  - ENT_FB_SUB_AGENTS_LIBRARY_v1
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1
---

# ENT_FB_VERTICAL_SPEC_OBJECT_v1
## Adapter pattern · parametrizacion del sistema FaberLoom por vertical industrial

## 1. Proposito

El sistema FaberLoom debe ejecutar cotizacion B2B en multiples verticales industriales (calzado seguridad · EPP quimico · MRO · ferreteria construccion · medico hospitalario · electrico industrial · etc) sin que la arquitectura quede overfit al primer tenant.

El **vertical_spec_object** es la abstraccion que separa **logica universal** (RFQ → spec match → stock → precio → proforma) de **dominio especifico** (norma tecnica · variante dimensional · documentacion regulatoria · compatibilidad).

Cada vertical declara su `vertical_spec_object`. El sistema usa el spec para parametrizar Source of Truth, Exception Taxonomy, Compliance Checker profiles, Evidence Bundle fields, etc.

> **Insight CEO+R3:** "MWT es adapter del sistema, no el core del sistema. El core es spec-to-quote discipline · cada industria tiene su forma de convertir especificacion en linea cotizable."

## 2. Estructura del vertical_spec_object

```yaml
vertical_spec_object:
  vertical_id: string  # ej. safety_footwear · chemical_PPE · MRO_industrial · etc
  vertical_name_human: string  # ej. "Calzado de seguridad industrial"
  parent_industry: string  # ej. industrial_supply · medical · electrical · construction

  technical_spec_rule:
    name: string  # ej. ASTM_F2413 · NIOSH · ISO_VG · IEC_60947 · registro_sanitario_INVIMA
    versions_supported: array<string>  # ej. ["ASTM_F2413-18", "ASTM_F2413-11"]
    governing_body: string  # ej. ASTM · NIOSH · IEC · ANVISA · COFEPRIS
    mandatory: boolean
    validation_method: enum  # certificate_match · numeric_range · enum_lookup · regex
    validation_examples: array<string>

  variant_dimension:
    primary: string  # ej. talla (footwear) · medida (cable) · viscosidad_ISO_VG (lubricante) · capacidad_kVA (transformador)
    primary_type: enum  # numeric · enum · string · range
    primary_examples: array<any>  # ej. [25, 26, 27, 28] o ["S", "M", "L"] o [22, 46, 100]
    secondary: array<{name, type, examples}>  # ej. ancho · color · material · clase

  certification_requirements:
    types: array<{cert_type, governing_body, validity_period_days, mandatory_for_sale}>
    examples:
      - cert_type: "registro_sanitario"
        governing_body: "INVIMA Colombia · COFEPRIS Mexico · ANVISA Brasil"
        validity_period_days: 1825
        mandatory_for_sale: true
      - cert_type: "ASTM_F2413_certificate"
        governing_body: "lab_acreditado"
        validity_period_days: 1095
        mandatory_for_sale: true

  compatibility_matrix:
    required: boolean  # true para MRO, electrico, EPP quimico
    matrix_type: enum  # equipo_modelo · sustancia_quimica · capacidad_electrica · medida_norma
    cross_reference_source: string  # ej. OEM_catalog · chemical_resistance_chart · IEC_lookup_table

  packaging_logistics:
    packaging_unit: string  # ej. par · caja · saco · pail · rollo · pieza
    moq_default: number
    cbm_per_unit: number
    weight_kg_per_unit: number
    special_handling: array<enum>  # ej. ["fragil", "peligroso_clase_3", "refrigerado", "sobredimensionado"]

  regulatory_overrides:
    requires_lot_tracking: boolean  # true en medico, quimico
    requires_expiry_tracking: boolean  # true en medico, reactivos
    requires_serial_tracking: boolean  # true en electrico industrial alto valor
    requires_country_origin_doc: boolean
    restricted_export: boolean

  pricing_overrides:
    currency_default: string  # ISO 4217
    fx_volatility_class: enum  # stable · medium · high
    margin_floor_default: float  # ej. 0.18
    discount_authority_override: string?  # referencia a authority matrix custom

  authority_overrides:
    decisions_with_custom_authority: array<{decision, default_level, override_level, reason}>

  hitl_intensity: enum  # low (commodity) · medium (B2B normal) · high (regulated medical/electrical)

  language_pref_default: string  # ISO 639-1 con region · ej. "es-MX" · "pt-BR"

  glossary_overrides:
    # Terminos del dominio que el sistema debe entender literal en RFQ
    vocabulary: array<{term, canonical_meaning, examples}>
```

## 3. Implementaciones canonicas v1

### 3.1 safety_footwear (MWT con Marluvas + Tecmater)

```yaml
vertical_spec_object:
  vertical_id: safety_footwear
  vertical_name_human: "Calzado de seguridad industrial"
  parent_industry: industrial_supply

  technical_spec_rule:
    name: ASTM_F2413
    versions_supported: ["ASTM_F2413-18", "ASTM_F2413-11"]
    governing_body: "ASTM International"
    mandatory: true
    validation_method: certificate_match

  variant_dimension:
    primary: talla
    primary_type: numeric
    primary_examples: [22, 23, 24, 25, 26, 27, 28, 29, 30]
    secondary:
      - name: ancho
        type: enum
        examples: ["normal", "ancho", "extra_ancho"]
      - name: puntera
        type: enum
        examples: ["acero", "composite", "aluminio"]
      - name: plantilla
        type: enum
        examples: ["acero", "kevlar", "estandar"]

  certification_requirements:
    types:
      - cert_type: ASTM_F2413_certificate
        governing_body: lab_acreditado
        validity_period_days: 1095
        mandatory_for_sale: true

  compatibility_matrix:
    required: false

  packaging_logistics:
    packaging_unit: par
    moq_default: 12
    cbm_per_unit: 0.012
    weight_kg_per_unit: 1.4
    special_handling: []

  regulatory_overrides:
    requires_lot_tracking: false
    requires_expiry_tracking: false
    requires_serial_tracking: false
    requires_country_origin_doc: true  # para algunos paises LATAM
    restricted_export: false

  pricing_overrides:
    currency_default: USD
    fx_volatility_class: medium  # MX/CO con USD intermedio
    margin_floor_default: 0.22

  authority_overrides:
    decisions_with_custom_authority: []  # usa defaults

  hitl_intensity: medium
  language_pref_default: "es-MX"

  glossary_overrides:
    vocabulary:
      - term: "punto"
        canonical_meaning: talla numerica regional MX
        examples: ["6 punto", "7 punto"]
      - term: "talla mexicana"
        canonical_meaning: variant_dimension.primary en escala MX (22-30)
```

### 3.2 chemical_PPE (vertical adyacente · stress-test R3)

```yaml
vertical_spec_object:
  vertical_id: chemical_PPE
  vertical_name_human: "Equipo de proteccion personal quimica"
  parent_industry: industrial_supply

  technical_spec_rule:
    name: NIOSH_or_EN
    versions_supported: ["NIOSH_42CFR84", "EN_140", "EN_143", "EN_374"]
    governing_body: "NIOSH USA · CEN Europa"
    mandatory: true
    validation_method: certificate_match

  variant_dimension:
    primary: nivel_proteccion
    primary_type: enum
    primary_examples: ["N95", "N99", "N100", "P100", "Half_face", "Full_face"]
    secondary:
      - name: cartucho_compatible
        type: enum
        examples: ["organic_vapor", "acid_gas", "particulate", "multi_gas"]
      - name: talla_arnes
        type: enum
        examples: ["S", "M", "L"]

  certification_requirements:
    types:
      - cert_type: NIOSH_approval_TC
        governing_body: NIOSH
        validity_period_days: 1825
        mandatory_for_sale: true

  compatibility_matrix:
    required: true
    matrix_type: sustancia_quimica
    cross_reference_source: chemical_resistance_chart_per_material

  packaging_logistics:
    packaging_unit: pieza
    moq_default: 50
    special_handling: ["fragil"]

  regulatory_overrides:
    requires_lot_tracking: true  # quimicos requieren lote
    requires_expiry_tracking: true  # filtros vencen
    requires_serial_tracking: false
    requires_country_origin_doc: true

  pricing_overrides:
    currency_default: USD
    fx_volatility_class: medium
    margin_floor_default: 0.25

  hitl_intensity: high  # mayor por compliance regulatorio
  language_pref_default: "es-MX"
```

### 3.3 medical_regulated (vertical R3 · TIER 4 frecuente)

```yaml
vertical_spec_object:
  vertical_id: medical_regulated
  vertical_name_human: "Equipo medico hospitalario"
  parent_industry: medical

  technical_spec_rule:
    name: registro_sanitario
    versions_supported: []  # gobernado por organismo per pais
    governing_body: "INVIMA CO · COFEPRIS MX · ANVISA BR · CECMED CU"
    mandatory: true
    validation_method: certificate_match

  variant_dimension:
    primary: presentacion
    primary_type: enum
    primary_examples: []  # depende del producto especifico

  certification_requirements:
    types:
      - cert_type: registro_sanitario
        governing_body: organismo_pais
        validity_period_days: 1825  # variable por pais y producto
        mandatory_for_sale: true
      - cert_type: COA  # certificate of analysis
        governing_body: fabricante
        validity_period_days: 365
        mandatory_for_sale: true

  compatibility_matrix:
    required: false

  packaging_logistics:
    packaging_unit: pieza_o_kit
    moq_default: 1
    special_handling: ["esteril", "refrigerado_si_aplica"]

  regulatory_overrides:
    requires_lot_tracking: true  # CRITICO
    requires_expiry_tracking: true  # CRITICO
    requires_serial_tracking: true  # instrumental
    requires_country_origin_doc: true
    restricted_export: true

  pricing_overrides:
    currency_default: USD
    fx_volatility_class: high  # licitaciones publicas con tipo cambio
    margin_floor_default: 0.30

  authority_overrides:
    decisions_with_custom_authority:
      - decision: envio_proforma_final
        default_level: AM
        override_level: AM_supervisor
        reason: "licitacion publica + penalidad contractual"
      - decision: sustitucion_SKU
        default_level: agente_AM
        override_level: AM_supervisor
        reason: "equivalencia regulatoria requiere validacion"

  hitl_intensity: high  # casi todo escalado
  language_pref_default: "es-MX"
```

(Implementaciones para `MRO_industrial · construction_supply · electrical_technical` se canonizan en indexa-e cuando aparezcan tenants reales · son referenciables ahora pero sin datos de produccion no canonizamos hardcoded.)

## 4. Como el sistema usa el vertical_spec_object

### 4.1 En Source of Truth
```
Source of Truth lee vertical_spec_object al cargar tenant config:
  ├─ technical_spec_rule → poblar fuente "norma tecnica"
  ├─ variant_dimension → poblar fuente "variantes" 
  ├─ certification_requirements → poblar fuente "certificaciones/docs"
  ├─ compatibility_matrix → activar fuente "cross-reference" si required=true
  └─ packaging_logistics → poblar fuente "MOQ/CBM/peso/empaque"
```

### 4.2 En Exception Taxonomy
```
Algunas excepciones se renombran/parametrizan:
  ASTM_AMBIGUO → TECHNICAL_SPEC_AMBIGUOUS (resuelve con vertical.technical_spec_rule.name)
  TALLA_FALTANTE → VARIANT_DIMENSION_MISSING (resuelve con vertical.variant_dimension)
  CERT_DOC_FALTANTE → CERTIFICATION_DOC_MISSING (resuelve con vertical.certification_requirements)
```

### 4.3 En Compliance Checker
```
AG_SUB_COMPLIANCE_CHECKER tiene 6 perfiles per vertical:
  · safety_footwear · chemical_PPE · MRO_compatibility 
  · construction_supply · medical_regulated · electrical_technical

El profile activo se determina por vertical_spec_object.vertical_id del tenant.
Cada profile tiene su propio rule_set y validation_method.
```

### 4.4 En Evidence Bundle
```
Campos del bundle se parametrizan:
  technical_spec_rule (era ASTM_rule literal)
  cert_doc_version (resuelve con vertical.certification_requirements)
  country_rule_applied (resuelve con tax_incoterm_country_rules y vertical.regulatory_overrides)
```

### 4.5 En Authority Matrix
```
Authority defaults aplican universalmente.
vertical_spec_object.authority_overrides puede sobrescribir decisiones especificas
con justificacion documentada (ej. medical_regulated escala envio_proforma_final).
```

## 5. Adapter pattern · ciclo de vida

```
1. Onboarding tenant nuevo
   ├─ CEO selecciona vertical_id de catalogo o crea nuevo
   ├─ Si nuevo · CEO + arquitectura FB definen vertical_spec_object
   ├─ Privacy review · Knowledge River layer config
   └─ Tenant activa en SHADOW

2. Configuracion vertical_spec_object
   ├─ Fill mandatory fields
   ├─ Authority overrides (si aplica)
   ├─ Glossary (vocabulario regional/sectorial)
   └─ Validation: dry-run con replay set

3. Activacion
   ├─ Vertical pasa a ACTIVE en allowlist FB
   ├─ Compliance Checker carga profile correspondiente
   └─ Source of Truth conecta fuentes per vertical

4. Mantenimiento (curador organizacional)
   ├─ Glossary se actualiza con vocabulario emergente
   ├─ Authority overrides se ajustan con datos uso real
   ├─ Certification requirements se actualizan con cambios regulatorios
   └─ Versioning del vertical_spec_object con changelog
```

## 6. Reglas inquebrantables

1. **Un tenant tiene exactamente UN vertical_spec_object activo.** Multi-vertical (tenant que vende calzado + EPP + ferreteria) requiere multi-tenant interno o vertical_spec_object compuesto v3+.

2. **Cambios al vertical_spec_object requieren versionado.** v1.0 → v1.1 con changelog · vertical activo NO se modifica en runtime sin pasar por SHADOW 30d.

3. **Glossary tiene precedencia sobre canonicos.** Si vocabulario regional dice "punto" en lugar de "talla", el sistema entiende "punto" en ese tenant.

4. **Compliance profiles son inmutables per vertical.** Modificar profile de safety_footwear afecta a TODOS los tenants safety_footwear · requiere proceso de gobernanza FB-side.

5. **vertical_spec_object es PRIVATE_RAW.** Configuracion del tenant no se promueve cross-tenant ni siquiera anonimizada · es operacional sensible.

## 7. Implicaciones para canonizaciones existentes

| Canonizado previo | Cambio por vertical_spec_object |
|---|---|
| ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1 | Las 14 fuentes referencian campos del vertical_spec_object · NO hardcoded "ASTM" |
| ENT_FB_RFQ_EXCEPTION_TAXONOMY_v1 | 4 excepciones renombradas (TECHNICAL_SPEC_AMBIGUOUS · VARIANT_DIMENSION_MISSING · COMPATIBILITY_INCOMPLETE · CERTIFICATION_DOC_MISSING) |
| ENT_FB_COMMERCIAL_AUTHORITY_MATRIX_v1 | Defaults universales · vertical_spec_object.authority_overrides parametriza |
| SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1 | Campos `technical_spec_rule` y `cert_doc_version` referencian vertical · no literales |
| ENT_FB_SUB_AGENTS_LIBRARY_v1 v1.1 | AG_SUB_COMPLIANCE_CHECKER con 6 profiles per vertical |

## 8. Glossary overrides v1.1 (post review R4 + Ciclope safety_footwear)

R4 ajuste critico: glossary interpreta lenguaje · NO certifica compliance/stock/precio/equivalencia normativa. Mappings deben ir a INTENT/USE_CASE · no directo a estandar tecnico.

### 8.1 Estructura `glossary_overrides` per vertical

```yaml
glossary_overrides:
  vocabulary:
    - term: string                              # palabra/frase regional
      canonical_meaning: string                 # intent o use_case · NO directo a estandar
      mappings: object?                         # solo para mapping discreto (ej. punto → talla)
      geographic_scope: array<string>           # ISO country codes obligatorio
      confidence: float                         # 0-1 · default 0.85
      examples: array<string>
      precedence_boundary: string               # que NO certifica
      sin_pais_action: enum                     # ALARMA · ASK · DEFAULT_TO_PRIMARY_SCOPE
  
  gaps:
    - term: string
      missing_scope: array<string>
      workaround_v1: string
      v2_action: string
```

### 8.2 Implementacion canonica safety_footwear v1.1

```yaml
safety_footwear:
  glossary_overrides:
    vocabulary:
      - term: "punto"
        canonical_meaning: variant_dimension.primary en escala numerica regional
        mappings:
          mx:
            "6 punto": 24
            "8 punto": 26
            "10 punto": 28
            "12 punto": 30
        geographic_scope: [MX]
        confidence: 0.95  # alto · vocabulario claro MX
        examples: ["6 punto", "talla 8 punto", "10 punto", "necesito 6 puntos"]
        precedence_boundary: "interpretacion lingüistica · NO certifica talla disponible · NO equivalencia EU/US"
        sin_pais_action: ALARMA  # R4: si pais desconocido NO inferir silenciosamente
      
      - term: "bota dielectrica"
        canonical_meaning: requires_electrical_hazard_protection  # INTENT · no certificacion directa (R4)
        geographic_scope: [MX, CO, PE]
        confidence: 0.90
        examples: ["bota dielectrica BC-7240", "necesito dielectricas", "calzado dielectrico"]
        precedence_boundary: "intent comercial · ASTM EH lo confirma luego en source of truth"
        sin_pais_action: DEFAULT_TO_PRIMARY_SCOPE
      
      - term: "calzado agro"
        canonical_meaning: agricultural_use_case  # USE_CASE · resistencia quimica condicional (R4)
        geographic_scope: [MX, CO]
        confidence: 0.85
        examples: ["calzado agro talla 25", "bota agro Tecmater"]
        precedence_boundary: "use_case · chemical_resistance solo si RFQ lo pide explicito · 'agro' puede ser lodo/humedad/cana/finca"
        sin_pais_action: DEFAULT_TO_PRIMARY_SCOPE
      
      - term: "calzado seguridad"
        canonical_meaning: zapato_trabajo_normado  # categoria general
        geographic_scope: [LATAM]
        confidence: 0.95
        examples: ["calzado seguridad basico"]
        precedence_boundary: "categoria · NO especifica norma · sub-categoria via spec"
        sin_pais_action: DEFAULT_TO_PRIMARY_SCOPE
      
      - term: "zapato seguridad"
        canonical_meaning: zapato_trabajo_normado  # sinonimo coloquial
        geographic_scope: [MX, CR]
        confidence: 0.95
        examples: ["zapato seguridad TC-5500"]
        precedence_boundary: "sinonimo · misma semantica que 'calzado seguridad'"
        sin_pais_action: DEFAULT_TO_PRIMARY_SCOPE
    
    gaps:
      - term: "punto"
        missing_scope: [CR, CO]
        workaround_v1: clientes CR/CO usan talla numerica explicita · documentar limitacion
        v2_action: agregar mappings_punto_cr / mappings_punto_co cuando volumen justifique
```

### 8.3 Reglas de matching · R4 ajustes

1. **Case-insensitive con normalizacion Unicode** (NFD + lowercase) · "Punto" = "punto" = "PUNTO"
2. **Regex tolerante CON BOUNDARIES** · `\b\d+\s*punto[s]?\b` (boundaries `\b` evitan falsos positivos)
3. **Exclusiones explicitas** para evitar capturar:
   - "punto de venta"
   - "punto de entrega"
   - "punto medio"
   - "punto de partida"
4. **Confidence threshold** · si `confidence < 0.7` despues del match → ALARMA · NO inferir
5. **Sin pais explicit** · si `sin_pais_action = ALARMA` y pais cliente unknown → bloquear · pedir clarificacion

### 8.4 Precedencia con limite (R4 critico)

```yaml
glossary_overrides_precedence:
  applies_to: 
    - intent_parsing               # interpretar que pide el cliente
    - variant_interpretation       # mapear vocabulario regional a variant
    - use_case_inference           # categoria de uso
  
  does_NOT_apply_to:
    - certification                # ASTM/NIOSH/ISO los confirma source of truth · NO glossary
    - compliance                   # POL_DATA_CLASSIFICATION · NO glossary
    - price                        # source of truth pricing master · NO glossary
    - stock                        # source of truth inventory · NO glossary
    - supplier_equivalence         # compatibility_matrix del vertical · NO glossary
```

R4 frase canonica: **"glossary interpreta lenguaje · no certifica compliance · stock · precio o equivalencia normativa."**

### 8.5 Implicaciones en otros componentes

| Componente | Como usa glossary_overrides |
|---|---|
| AG_SUB_EMAIL_CLASSIFIER | Aplica glossary al parsear RFQ · genera intent + entities |
| AG_SUB_COMPLIANCE_CHECKER | NUNCA confia glossary para compliance · siempre va a source of truth para certificacion |
| AG_SUB_PROFORMA_BUILDER | Usa intent del classifier (post-glossary) pero confirma con catalogo + pricing master |
| Authority Matrix | Glossary mapping ambiguo (confidence <0.7) escala automaticamente a AM |

## 9. Pendientes v1.2 / v2

1. Composicion de vertical_spec_objects (tenant multi-vertical)
2. Vertical_spec_object editor visual en builder (post-MVP UI)
3. Templates de vertical_spec_object publicos en marketplace FB v3+
4. Cross-vertical learning (insights agregados sin contaminar profiles)
5. AI-assisted creation de vertical nuevo (CEO + sistema sugiere campos basado en industria)
6. Glossary `punto_cr` y `punto_co` (cuando volumen justifique · v2 safety_footwear)
7. Glossary detection automatica desde corpus uso real (sugerir terminos nuevos al curador)
8. Sub-vertical glossaries dentro de safety_footwear (agro vs minero vs industrial · diferenciados)

## NO IMPLICA (R4 bonus 5%/50%)

`ENT_FB_VERTICAL_SPEC_OBJECT_v1` v1.1 glossary_overrides **NO implica certificacion tecnica**. Glossary solo INTERPRETA lenguaje regional · NO certifica que el producto cumpla la norma sugerida. Cualquier certificacion (ASTM EH · NIOSH · ISO · etc) debe confirmarse via source of truth · evidence bundle · y compliance checker. Glossary inicia hipotesis · NO emite certificado.

## Changelog
- 2026-05-01 v1.1 VIGENTE: Indexa-e backend post review R4 + integracion 10 fixtures Ciclope safety_footwear. Agregada seccion 8 glossary_overrides completa con estructura canonica + implementacion safety_footwear v1.1 (5 terminos: punto/bota dielectrica/calzado agro/calzado seguridad/zapato seguridad + 1 gap punto CR/CO). Reglas matching: case-insensitive Unicode + regex con boundaries + exclusiones explicitas (punto de venta/entrega/medio) + confidence threshold 0.7 + sin_pais_action ALARMA. Precedencia con limite explicito (R4 critico): glossary aplica a intent_parsing/variant/use_case · NO aplica a certification/compliance/price/stock/supplier_equivalence. R4 ajustes criticos: "bota dielectrica" → INTENT requires_electrical_hazard_protection (no directo ASTM EH) · "calzado agro" → USE_CASE agricultural (chemical_resistance condicional) · "punto" sin pais → ALARMA. Linea NO implica certificacion tecnica.
- 2026-04-30 v1.0 VIGENTE: Creacion inicial. Adapter pattern canonizado tras hallazgo R3 "MWT como adapter, no core". Estructura del vertical_spec_object con 9 campos canonicos. 3 implementaciones ejemplo (safety_footwear · chemical_PPE · medical_regulated). 4 puntos de uso por componentes del sistema. 5 reglas inquebrantables. Implicaciones documentadas para 5 piezas canonizadas previas.

## Stamp
VIGENTE 2026-05-01 v1.1 — Adapter pattern + glossary_overrides canonizados con limites estrictos. R4 critico: glossary inicia hipotesis · NO emite certificado. Mitiga riesgo "bota dielectrica = ASTM EH certificado por magia semantica" (R4 advertencia central).
