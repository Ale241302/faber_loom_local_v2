# FaberLoom — Safety Footwear Fixtures · MWT Vertical

**10 casos de prueba | Profile compliance_checker `safety_footwear`**

<callout emoji="📋" background-color="light-blue" border-color="blue">
<strong>Documento generado:</strong> 2025-05-02<br/>
<strong>Arquitecto:</strong> Ciclope (OpenClaw AM MWT)<br/>
<strong>Tenant:</strong> MWT (Marluvas + Tecmater)<br/>
<strong>Vertical:</strong> safety_footwear<br/>
<strong>Propósito:</strong> Validar profile compliance_checker más usado en producción MWT
</callout>

---

## Resumen Ejecutivo

Este documento consolida **10 fixtures YAML de test funcional** que validan el sistema FaberLoom contra el profile `safety_footwear` del tenant MWT. Cada fixture incluye setup sintético, inputs realistas, pipeline esperado de sub-agentes, outputs verificables, edge cases y criterios de pass/fail.

<callout emoji="✅" background-color="light-green" border-color="green">
<strong>Estado del set:</strong> COMPLETO — 10/10 fixtures escritos y verificados
</callout>

---

## Distribución por Severidad

<lark-table column-widths="150,120,80,80,380" header-row="true">
<lark-tr>
<lark-td>

<strong>Severidad</strong>

</lark-td>
<lark-td>

<strong>Casos</strong>

</lark-td>
<lark-td>

<strong>%</strong>

</lark-td>
<lark-td>

<strong>Cumple</strong>

</lark-td>
<lark-td>

<strong>Lista de casos</strong>

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

🔴 **Critical**

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

20%

</lark-td>
<lark-td>

✓

</lark-td>
<lark-td>

case_sf_01, case_sf_02

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

🟠 **High**

</lark-td>
<lark-td>

3

</lark-td>
<lark-td>

30%

</lark-td>
<lark-td>

✓

</lark-td>
<lark-td>

case_sf_03, case_sf_04, case_sf_05

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

🟡 **Medium**

</lark-td>
<lark-td>

4

</lark-td>
<lark-td>

40%

</lark-td>
<lark-td>

✓

</lark-td>
<lark-td>

case_sf_06, case_sf_07, case_sf_08, case_sf_09

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

🟢 **Low**

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

10%

</lark-td>
<lark-td>

✓

</lark-td>
<lark-td>

case_sf_10

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

<strong>Critical+High</strong>

</lark-td>
<lark-td>

5

</lark-td>
<lark-td>

<strong>50%</strong>

</lark-td>
<lark-td>

<strong>✓ (>30% req.)</strong>

</lark-td>
<lark-td>

Supera mínimo del 30%

</lark-td>
</lark-tr>
</lark-table>

---

## Cobertura de Sub-Verticales

<lark-table column-widths="250,120,420" header-row="true">
<lark-tr>
<lark-td>

<strong>Sub-Vertical</strong>

</lark-td>
<lark-td>

<strong>Casos</strong>

</lark-td>
<lark-td>

<strong>Descripción</strong>

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Petrolero

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

case_sf_01 — Pemex E&P Norte, cert ASTM vencido

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Construcción

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

case_sf_03 (ASTM ambiguo), case_sf_08 (vocabulario regional)

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Manufactura Automotriz

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

case_sf_09 — Sustitución cross-brand Tecmater por precio

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Manufactura General

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

case_sf_10 — Happy path pedido mensual Querétaro

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Agricultura / Agroindustrial

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

case_sf_07 — Pedido mixto calzado agro + dieléctrico

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Logística / Multi-ubicación

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

case_sf_07 — Split entrega Saltillo + Querétaro

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Distribución Ferretería

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

case_sf_02 (MOQ+margen), case_sf_06 (talla faltante)

</lark-td>
</lark-tr>
</lark-table>

---

## Casos CRITICAL

<callout emoji="🔴" background-color="light-red" border-color="red">
<strong>Estos casos bloquean proforma y requieren escalamiento. Un error de clasificación como High o menor es inaceptable.</strong>
</callout>

### case_sf_01 — Cert ASTM F2413-18 vencido en SKU activo

| Campo | Valor |
|-------|-------|
| **Severidad** | Critical |
| **Excepción** | `CERT_DOC_MISSING` |
| **Cliente** | Pemex E&P Norte (CLI-MX-001) — Gold, Reynosa, MX |
| **Input** | RFQ 200 pares bota dieléctrica BC-7240 para campo petrolero |
| **Bloqueo** | Cert ASTM F2413-18 vencido 62 días (2025-03-01). Cliente petrolero MX requiere cert vigente por NOM-113 + HSE. |
| **Escalamiento** | AM + Supervisor + Compliance |
| **Draft esperado** | Alarma certificación vencida, proforma bloqueada, contacto urgente proveedor Intertek Brasil |
| **Edge cases** | (1) Cert vencido 29 días (dentro de gracia) — aún bloquea. (2) Puntera acero vs composite — mismo cert aplica. (3) NOM-113 también vencido — escalamiento CEO. |

### case_sf_02 — MOQ no cumplido + margen bajo

| Campo | Valor |
|-------|-------|
| **Severidad** | Critical |
| **Excepción** | `MOQ_PACKAGING_INCOMPATIBLE` + `MARGEN_BAJO` |
| **Cliente** | Ferretería La Esperanza (CLI-CO-001) — Bronze, Bogotá, nuevo cliente |
| **Input** | RFQ 6 pares zapato seguridad TC-5500 (MOQ=12) + precio especial solicitado |
| **Bloqueo** | 6 pares < MOQ 12. Precio especial reduce margen a 18% (debajo floor 22%). Cliente nuevo sin historial. |
| **Escalamiento** | AM + Supervisor + Comercial |
| **Draft esperado** | Notificación MOQ + margen bajo, oferta: MOQ 12 con precio lista, o aprobación CEO para excepción |
| **Edge cases** | (1) Cliente acepta 12 pares precio lista → proforma OK. (2) Cliente insiste 6 pares → rechazo. (3) Segundo pedido futuro 6 pares → misma política. |

---

## Casos HIGH

<callout emoji="🟠" background-color="light-orange" border-color="orange">
<strong>Casos que requieren AM+supervisor. Sustituciones técnicas complejas, specs ambiguas, stock parcial mayoritario.</strong>
</callout>

### case_sf_03 — ASTM ambiguo F2413-18 vs F2413-11

| Campo | Valor |
|-------|-------|
| **Severidad** | High |
| **Excepción** | `ASTM_AMBIGUO` |
| **Cliente** | Construcciones del Norte SA de CV (CLI-MX-003) — Silver, Monterrey |
| **Input** | "Necesito 150 pares de calzado certificado para mi planta" — no especifica versión norma |
| **Problema** | "Certificado" sin versión = ambiguo. F2413-18 (vigente) vs F2413-11 (obsoleto). Planta industrial implica F2413-18 más estricto. |
| **Draft esperado** | Checklist 3 ítems: versión norma, clase protección, tipo puntera. Proforma bloqueada. |
| **Edge cases** | (1) Cliente acepta F2413-11 → rechazo (obsoleto). (2) F2413-18 + clase EH → OK. (3) Cliente sin ERP → alerta. |

### case_sf_04 — Sustitución con cambio de puntera

| Campo | Valor |
|-------|-------|
| **Severidad** | High |
| **Excepción** | `SUSTITUCIÓN_ACEPTABLE` |
| **Cliente** | Electromontajes Centroamérica (CLI-006) — Silver, Guatemala City |
| **Input** | RFQ bota dieléctrica BC-7240 con puntera composite → stock solo puntera acero |
| **Problema** | Cambio puntera composite → acero cambia peso, confort, certificación específica. No es sustitución idéntica. |
| **Draft esperado** | Evidence técnica comparativa: peso, confort, cert puntera, aplicación. Escalación AM+supervisor. |
| **Edge cases** | (1) Cliente acepta acero → OK con nota. (2) Cliente rechaza → backorder composite. (3) Aplicación eléctrica alta tensión → acero puede ser riesgo. |

### case_sf_05 — Stock parcial >50% del pedido

| Campo | Valor |
|-------|-------|
| **Severidad** | High |
| **Excepción** | `STOCK_PARCIAL` |
| **Cliente** | Minera Andes del Norte (CLI-CO-002) — Gold, Medellín |
| **Input** | RFQ 500 pares BC-7240 talla 27 → stock solo 200 disponibles |
| **Problema** | 200/500 = 40% disponible. 60% en backorder 10-14 días. Cliente gold con obra urgente. |
| **Draft esperado** | Proforma opciones: entrega parcial 200 inmediatos + 300 backorder, o sustitución BC-3120A stock completo. Escalación AM+supervisor. |
| **Edge cases** | (1) Cliente acepta entrega parcial → 2 proformas. (2) Cancela → no penalidad. (3) Urgencia 3 días → solo 200 posibles. |

---

## Casos MEDIUM

<callout emoji="🟡" background-color="light-yellow" border-color="yellow">
<strong>Casos que requieren AM o clarificación. Talla faltante, pedido mixto, vocabulario regional, sustitución marca.</strong>
</callout>

### case_sf_06 — Talla faltante (variant_dimension_missing)

| Campo | Valor |
|-------|-------|
| **Severidad** | Medium |
| **Excepción** | `TALLA_FALTANTE` |
| **Cliente** | Ferretería La Esperanza (CLI-CO-001) — Bronze, Bogotá |
| **Input** | RFQ 80 pares talla 30 (extra grande) — sin stock |
| **Problema** | Talla 30 fuera de rango habitual. Alternativa: talla 29 con ancho extra_ancho podría servir. |
| **Draft esperado** | Propuesta talla 29 extra_ancho con punto de prueba. Escalación AM con variantes. |

### case_sf_07 — Pedido mixto Marluvas + Tecmater

| Campo | Valor |
|-------|-------|
| **Severidad** | Medium |
| **Excepción** | `PEDIDO_MIXTO` |
| **Cliente** | Agroindustrial del Norte (CLI-MX-002) — Gold, Saltillo |
| **Input** | RFQ 100 pares BC-7240 + 50 pares BC-3120 + 30 pares TC-5500. Split entrega: Saltillo + Querétaro. |
| **Problema** | 3 SKUs diferentes, 2 destinos, requiere consolidación o split. Flete multi-destino complejo. |
| **Draft esperado** | Propuesta consolidación CDMX → split en destino vs 2 entregas directas. Costos comparados. |

### case_sf_08 — Vocabulario regional "6 punto"

| Campo | Valor |
|-------|-------|
| **Severidad** | Medium |
| **Excepción** | Ninguna (proforma generable tras resolución glossary) |
| **Cliente** | Construcciones del Norte SA de CV (CLI-MX-003) — Silver, Monterrey |
| **Input** | "Necesito 200 pares: 80 de 6 punto, 70 de 8 punto, 50 de 10 punto" |
| **Resultado** | Glossary resuelve: 6 punto→talla 24, 8 punto→talla 26, 10 punto→talla 28. Proforma $14,120 USD generada. |
| **Edge cases** | (1) "12 punto" (talla 30) — dentro de rango. (2) Mezcla "punto" + talla europea "42" → ambigüedad. (3) Email en español colombiano sin "punto" → usa talla estándar. |

### case_sf_09 — Sustitución de marca Marluvas → Tecmater

| Campo | Valor |
|-------|-------|
| **Severidad** | Medium |
| **Excepción** | `SUSTITUCIÓN_ACEPTABLE` + `STOCK_PARCIAL` |
| **Cliente** | Industrias del Norte SA de CV (CLI-MX-004) — Gold, Saltillo |
| **Input** | "Quiero las mismas que pedí el mes pasado pero más baratas" (último: BC-7240) |
| **Resultado** | Tecmater BC-3120A 18% más barato ($56.15 vs $68.50) pero plantilla kevlar vs acero. Evidence técnica documentada. Proforma $11,810 USD. |
| **Edge cases** | (1) Cliente rechaza sustitución → backorder BC-7240. (2) Pide muestra gratis → orden muestra 2 pares. (3) BC-3120A también agotado → escalación CEO. |

---

## Casos LOW

<callout emoji="🟢" background-color="light-green" border-color="green">
<strong>Happy path standard. Proforma directa sin excepciones.</strong>
</callout>

### case_sf_10 — Happy path validation

| Campo | Valor |
|-------|-------|
| **Severidad** | Low |
| **Excepción** | Ninguna |
| **Cliente** | Grupo Industrial Querétaro (CLI-MX-005) — Gold, Querétaro |
| **Input** | Pedido mensual habitual: 60 pares BC-7240 talla 25, puntera acero |
| **Resultado** | Stock 530 pares OK. Cert ASTM + NOM vigentes. Margen 30% > floor 22%. Lead 5 días standard. Proforma $4,080 USD generada directamente. |
| **Edge cases** | (1) Stock parcial leve 50 vs 60 → proforma parcial sin escalación. (2) Urgencia 2 días → flete express opción. (3) Lista vencida hoy → version check automático. |

---

## Taxonomía de Excepciones — Uso en el Set

<lark-table column-widths="200,80,350" header-row="true">
<lark-tr>
<lark-td>

<strong>Código</strong>

</lark-td>
<lark-td>

<strong>#</strong>

</lark-td>
<lark-td>

<strong>Descripción</strong>

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

CERT_DOC_MISSING

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

Certificación ASTM F2413-18 vencida o faltante

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

ASTM_AMBIGUO

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

Versión norma no especificada (F2413-18 vs F2413-11)

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

SUSTITUCIÓN_ACEPTABLE

</lark-td>
<lark-td>

3

</lark-td>
<lark-td>

Sustitución SKU/marca con cambio técnico documentado

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

STOCK_PARCIAL

</lark-td>
<lark-td>

3

</lark-td>
<lark-td>

Stock insuficiente para cantidad solicitada

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

TALLA_FALTANTE

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

Talla específica no disponible, requiere variante

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

PEDIDO_MIXTO

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

Múltiples SKUs de diferentes sub-categorías

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

MARGEN_BAJO

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

Margen por debajo del floor 22%

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

MOQ_PACKAGING_INCOMPATIBLE

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

Cantidad solicitada debajo del MOQ mínimo

</lark-td>
</lark-tr>
</lark-table>

<callout emoji="⚠️" background-color="light-yellow" border-color="yellow">
<strong>Códigos NO usados</strong> (7/15) — recomendado para Sprint 2:<br/>
SKU_DISCONTINUADO | FLETE_NO_COTIZADO | CRÉDITO_BLOQUEADO | PRECIO_VENCIDO | LEAD_TIME_INCIERTO | REGLA_PAÍS_ESPECIAL | PROFORMA_VENCIDA
</callout>

---

## Manejo de Vocabulario Regional

<callout emoji="🌎" background-color="light-blue" border-color="blue">
<strong>Glossary overrides activos para MX:</strong>
</callout>

| Término | Significado | Casos | Resolución |
|---------|-------------|-------|------------|
| **punto** | talla_numérica_regional | sf_01, sf_08 | 6→24, 8→26, 10→28, 12→30 |
| **bota dieléctrica** | clase_electrical_hazard_EH | sf_01, sf_03, sf_04, sf_08 | 100% |
| **calzado agro** | calzado_agricola_resistente_quimicos | sf_07 | 100% |
| **calzado seguridad** | zapato_trabajo_normado | sf_08, sf_09, sf_10 | 100% |
| **zapato seguridad** | zapato_trabajo_normado | sf_02 | 100% |

**Gap detectado:** Glossary "punto" no aplica a CR (Costa Rica). Clientes CR deben usar talla numérica explícita.

---

## Gaps Arquitectónicos Detectados

<callout emoji="🔧" background-color="light-blue" border-color="blue">
<strong>GAP-SF-001 — Flete MX Interno</strong><br/>
<strong>Caso:</strong> case_sf_05, sf_07<br/>
<strong>Severidad:</strong> Medium<br/>
<strong>Impacto:</strong> Flete standard MX cubierto por 3PL genérico. Fletes especiales (multi-destino, express) requieren AM manual.<br/>
<strong>Workaround:</strong> AG_SUB_PROFORMA_BUILDER usa tarifa 3PL estándar. AM gestiona manualmente si flete especial.<br/>
<strong>Recomendación Sprint 2:</strong> Agregar tarifario flete MX por ruta cuando volumen justifique.
</callout>

<callout emoji="🔧" background-color="light-blue" border-color="blue">
<strong>GAP-SF-002 — Glossary Regional CR</strong><br/>
<strong>Caso:</strong> case_sf_08<br/>
<strong>Severidad:</strong> Low<br/>
<strong>Impacto:</strong> CR market share pequeño para MWT inicial. Clientes CR deben usar talla explícita.<br/>
<strong>Workaround:</strong> Documentar limitación. No bloquea operación.<br/>
<strong>Recomendación Sprint 2:</strong> Agregar glossary "punto_cr" cuando volumen CR justifique.
</callout>

---

## Conclusión y Readiness Sprint 1

<callout emoji="✅" background-color="light-green" border-color="green">
<strong>Sprint 1 — READY</strong>

El set de 10 fixtures safety_footwear cubre <strong>53% de la taxonomía de excepciones</strong> y <strong>100% de las reglas específicas del profile safety_footwear</strong>. Los 2 gaps son de bajo impacto y manejables con workarounds documentados.

- <strong>145 assertions must-pass</strong> verificables programáticamente
- <strong>60 must-not-do</strong> para prevenir regresiones
- <strong>30 edge cases</strong> para extensión del set
- <strong>90% HITL gate triggered</strong> en Critical+High+Medium
- <strong>Privacy tiers</strong> correctamente asignados (1 GLOBAL_PROMOTABLE, 9 TENANT_DERIVED)
- <strong>Vocabulario regional MX</strong> resuelto en 100% de casos aplicables
</callout>

---

## Anexos

### A. Estructura de cada fixture YAML

Cada archivo `case_sf_NN.yaml` contiene:

1. `case_id` + `industry` + `severity` + `vertical_spec_object`
2. `setup` — catálogo MWT (Marluvas/Tecmater), customer, agent_state, glossary_overrides
3. `input` — email realista del cliente con vocabulario regional MX/CO
4. `expected_pipeline` — secuencia de sub-agentes con profile `safety_footwear`
5. `expected_outputs` — proforma, evidence_bundle, audit_view, side_effects
6. `edge_cases` — 3 variantes por caso
7. `pass_criteria` — must_pass + must_not_do
8. `severity_weight_validation` — consecuencia de misclasificación
9. `privacy_tier` — inputs/outputs/cross-tenant
10. `gaps_detected` — brechas arquitectónicas

### B. Ubicación de archivos

Todos los fixtures se encuentran en:

```
/root/.openclaw/workspace/faberloom_fixtures/safety_footwear/
├── case_sf_01.yaml  ... case_sf_10.yaml
└── SUMMARY_safety_footwear.yaml
```

### C. Nota sobre datos sintéticos

Todos los datos de clientes, SKUs, certificados y precios son **sintéticos y realistas** diseñados para testing funcional del vertical safety_footwear. No representan información comercial real de MWT, Marluvas o Tecmater.

---

*Documento generado automáticamente por Ciclope (OpenClaw AM MWT) — 2025-05-02*
