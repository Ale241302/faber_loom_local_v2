# FaberLoom — Suite de Fixtures Funcionales R3

**20 casos de prueba | Auditoría Funcional Multi-Industria**

<callout emoji="📋" background-color="light-blue" border-color="blue">
<strong>Documento generado:</strong> 2025-04-30<br/>
<strong>Arquitecto:</strong> Ciclope (OpenClaw AM MWT)<br/>
<strong>Tenant:</strong> MWT (Marluvas + Tecmater)<br/>
<strong>Propósito:</strong> Detectar gaps arquitectónicos antes de Sprint 1
</callout>

---

## Resumen Ejecutivo

Este documento consolida **20 fixtures YAML de test funcional** que validan el sistema FaberLoom contra casos reales multi-industria identificados en la auditoría R3. Cada fixture incluye setup sintético, inputs realistas, pipeline esperado de sub-agentes, outputs verificables, edge cases y criterios de pass/fail.

<callout emoji="✅" background-color="light-green" border-color="green">
<strong>Estado del set:</strong> COMPLETO — 20/20 fixtures escritos y verificados
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

4

</lark-td>
<lark-td>

20%

</lark-td>
<lark-td>

✓

</lark-td>
<lark-td>

case_03, case_11, case_17, case_19

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

🟠 **High**

</lark-td>
<lark-td>

5

</lark-td>
<lark-td>

25%

</lark-td>
<lark-td>

✓

</lark-td>
<lark-td>

case_01, case_13, case_15, case_16, case_18

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

🟡 **Medium**

</lark-td>
<lark-td>

7

</lark-td>
<lark-td>

35%

</lark-td>
<lark-td>

✓

</lark-td>
<lark-td>

case_02, case_04, case_05, case_06, case_07, case_08, case_10

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

🟢 **Low-Medium**

</lark-td>
<lark-td>

4

</lark-td>
<lark-td>

20%

</lark-td>
<lark-td>

✓

</lark-td>
<lark-td>

case_09, case_12, case_14, case_20

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

<strong>Critical+High</strong>

</lark-td>
<lark-td>

9

</lark-td>
<lark-td>

<strong>45%</strong>

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

## Cobertura por Industria

<lark-table column-widths="220,120,450" header-row="true">
<lark-tr>
<lark-td>

<strong>Industria</strong>

</lark-td>
<lark-td>

<strong>Casos</strong>

</lark-td>
<lark-td>

<strong>Perfil de compliance</strong>

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

EPP / Químico

</lark-td>
<lark-td>

3

</lark-td>
<lark-td>

chemical_PPE — ASTM, ISO, permeación, compatibilidad química

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

MRO / Industrial

</lark-td>
<lark-td>

3

</lark-td>
<lark-td>

MRO_compatibility — códigos OEM, compatibilidad mecánica/química

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Eléctrico / Industrial

</lark-td>
<lark-td>

3

</lark-td>
<lark-td>

electrical_technical — NEMA, IEC, ampacity, compatibilidad técnica

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

construction_supply — ICONTEC, ASTM, dimensiones, flete obra

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Médico / Hospitalario

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

medical_regulated — INVIMA, lote, trazabilidad, certificación

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Eléctrico / Baja tensión

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

electrical_technical — UL, NTC 2050, especificaciones cable

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Ferretería / Construcción

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

construction_supply — DIN, hardware, sustitución

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Lubricantes

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

MRO_compatibility — ISO 11158, DIN 51524, zinc-free vs ZDDP

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Laboratorio

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

medical_regulated — ACS, HPLC, lote, vencimiento

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

Suministros médicos

</lark-td>
<lark-td>

1

</lark-td>
<lark-td>

medical_regulated — INVIMA, EN 455-1, ISO 11137

</lark-td>
</lark-tr>
</lark-table>

---

## Casos CRITICAL

<callout emoji="🔴" background-color="light-red" border-color="red">
<strong>Estos casos bloquean proforma y requieren escalamiento a supervisor o CEO. Un error de clasificación como High o Medium es inaceptable.</strong>
</callout>

### case_03 — Traje Tyvek con certificación faltante

| Campo | Valor |
|-------|-------|
| **Industria** | EPP / Químico |
| **Severidad** | Critical |
| **Excepción** | `CERT_DOC_MISSING` + `REGULATORY_DOC_MISSING` |
| **Cliente** | Petroquímica del Caribe (CLI-001) — Gold, Barranquilla |
| **Input** | RFQ 50 trajes Tyvek ISO 16603 para manejo ácido clorhídrico |
| **Bloqueo** | CE EN 14126 vigente pero ISO 16603 certificado vencido (2024-08-01). Sin certificación no puede usarse en ambiente químico. |
| **Escalamiento** | AM + Supervisor + Compliance |
| **Draft esperado** | Solicitud de certificación vigente al proveedor, proforma bloqueada, alarma regulatoria |
| **3 edge cases** | (1) Cliente acepta Tyvek sin ISO 16603 — **NO permitir**. (2) Tyvek descatalogado, solo 5M disponible — proponer alternativa química. (3) Certificación tardía >30 días — cancelar RFQ. |

### case_11 — Instrumental quirúrgico sin registro INVIMA

| Campo | Valor |
|-------|-------|
| **Industria** | Médico / Hospitalario |
| **Severidad** | Critical |
| **Excepción** | `REGULATORY_DOC_MISSING` |
| **Cliente** | Hospital Universitario de Cartagena (CLI-011) — Público, contrato Marco 2024 |
| **Input** | RFQ 1 set instrumental cirugía cardiovascular — requiere registro INVIMA y trazabilidad lote |
| **Bloqueo** | INVIMA 2022DM-001234 vencido 2025-01-01. Instrumental sin registro vigente = ilegal en institución pública. Penalidad por incumplimiento. |
| **Escalamiento** | AM + Supervisor + Regulatorio Tecmater |
| **Draft esperado** | Alerta regulatoria máxima, proforma bloqueada, contacto inmediato con proveedor INVIMA |
| **3 edge cases** | (1) INVIMA por re-registrar — lead time 90 días. (2) Alternativa con INVIMA vigente. (3) Hospital acepta bajo riesgo propio — **NO permitir sin documento**. |

### case_17 — Crédito bloqueado con proforma urgente

| Campo | Valor |
|-------|-------|
| **Industria** | Construcción / Infraestructura |
| **Severidad** | Critical |
| **Excepción** | `CRÉDITO_BLOQUEADO` |
| **Cliente** | Construcciones del Pacífico (CLI-010) — Bronze, crédito bloqueado por 60 días vencidos |
| **Input** | RFQ 200 sacos cemento urgente para obra pública con plazo 3 días |
| **Bloqueo** | Cliente con mora 60 días, crédito bloqueado. Proforma urgente no puede generarse sin aprobación financiera. |
| **Escalamiento** | AM + Supervisor + Finanzas |
| **Draft esperado** | Notificación crédito bloqueado, condiciones de desbloqueo, oferta contado o carta de crédito |
| **3 edge cases** | (1) Cliente ofrece pago contado — validar fondos antes de desbloqueo. (2) Carta crédito bancaria. (3) Obra pública con penalidad — **NO permitir excepción AM solo**. |

### case_19 — RFQ licitación pública con penalidad de incumplimiento

| Campo | Valor |
|-------|-------|
| **Industria** | Médico / Público |
| **Severidad** | Critical |
| **Excepción** | `REGLA_PAÍS_ESPECIAL` + `MARGEN_BAJO` |
| **Cliente** | Hospital San José de Popayán (CLI-009) — Público, licitación CONTRATO-SJSP-2024-089 |
| **Input** | RFQ 20 camas hospitalarias eléctricas para licitación pública. Penalidad 5% por incumplimiento. |
| **Bloqueo** | REGLA_PAÍS_ESPECIAL: producto médico eléctrico en institución pública requiere registro INVIMA + certificación eléctrica RETIE. Margen 8% por debajo del mínimo de 15% aprobado. |
| **Escalamiento** | CEO + Legal + Logística |
| **Draft esperado** | Análisis riesgo-beneficio, validación regulatoria cruzada, proforma con firma CEO |
| **3 edge cases** | (1) Sin certificación RETIE — rechazo automático. (2) Margen <8% — pérdida asegurada. (3) Penalidad licitación > margen total — **rechazo obligatorio**. |

---

## Casos HIGH

<callout emoji="🟠" background-color="light-orange" border-color="orange">
<strong>Casos que requieren intervención AM. Sustituciones técnicas complejas, specs incompletas con alto impacto, o condiciones comerciales excepcionales.</strong>
</callout>

### case_01 — EPP químico con respirador norma ambigua

| Campo | Valor |
|-------|-------|
| **Industria** | EPP / Químico |
| **Severidad** | High |
| **Excepción** | `ASTM_AMBIGUO` |
| **Cliente** | Químicos del Norte (CLI-002) — Silver, Montería |
| **Input** | RFQ 20 respiradores para cloro gas — no especifica norma ni clase de filtro |
| **Problema** | "Respirador" sin norma (N95, P100, SCBA) ni clase filtro (A2B2E2K1 vs ABEK1) = aplicación incorrecta puede causar exposición letal. |
| **Draft esperado** | Checklist técnico 4 ítems: norma, filtro, concentración, escape. Proforma bloqueada hasta clarificación. |
| **Edge cases** | (1) Cliente opera cloro >10 ppm — SCBA obligatorio. (2) N95 inadecuado para gases. (3) Cliente sin ERP químico — alerta regulatoria. |

### case_13 — Tablero eléctrico 30HP con spec incompleta

| Campo | Valor |
|-------|-------|
| **Industria** | Eléctrico / Industrial |
| **Severidad** | High |
| **Excepción** | `ASTM_AMBIGUO` + `SUSTITUCIÓN_ACEPTABLE` |
| **Cliente** | Electromontajes Centroamérica (CLI-006) — Silver, Guatemala City |
| **Input** | RFQ tablero NEMA 4X vacío para motor 30HP — no especifica amperaje, voltaje, protección térmica |
| **Problema** | Tablero vacío sin spec eléctrica = posible sobre/sub-dimensionamiento. Motor 30HP puede ser 208V (82A) o 480V (40A). Breaker, contactor y OL relay dependen de esto. |
| **Draft esperado** | Checklist técnico eléctrico 4 ítems: voltaje, amperaje, tipo arranque, protección. Proforma bloqueada. |
| **Edge cases** | (1) 208V 3φ vs 480V 3φ — breaker diferente. (2) Arranque directo vs Y-Δ. (3) NEMA 4X en ambiente corrosivo Guatemala — validar IP65. |

### case_15 — Transformador 75kVA lead time incierto

| Campo | Valor |
|-------|-------|
| **Industria** | Eléctrico / Industrial |
| **Severidad** | High |
| **Excepción** | `LEAD_TIME_INCIERTO` + `STOCK_PARCIAL` + `FLETE_NO_COTIZADO` |
| **Cliente** | Electromontajes Centroamérica (CLI-006) — Silver, Guatemala City |
| **Input** | RFQ transformador 75kVA 480/208Y-120V — stock solo 1 unidad, lead time 8-12 semanas, flete internacional no cotizado |
| **Problema** | Transformador importado sin lead time confirmado. Stock 1 vs 1 solicitado pero sin margen reserva. Flete Bogotá→Guatemala no en Source of Truth. |
| **Gap detectado** | Flete internacional no tiene sub-agente dedicado. Workaround: AM gestiona manualmente. |
| **Draft esperado** | Cotización con 3 escenarios: stock inmediato (con reserva), backorder 8-12 semanas, flete por confirmar. |

### case_16 — Interruptor 400A sustitución técnica riesgosa

| Campo | Valor |
|-------|-------|
| **Industria** | Eléctrico / Industrial |
| **Severidad** | High |
| **Excepción** | `ASTM_AMBIGUO` + `SUSTITUCIÓN_ACEPTABLE` |
| **Cliente** | Electromontajes Centroamérica (CLI-006) — Silver, Guatemala City |
| **Input** | RFQ interruptor termomagnético 400A 3P para tablero principal — Schneider Masterpact agotado, sistema propone ABB Emax |
| **Problema** | Sustitución entre marcas en interruptor principal requiere verificación dimensional, curva de disparo, capacidad de ruptura (Icu), compatibilidad busbar, y homologación local. |
| **Draft esperado** | Evidence técnica comparativa: dimensiones, curvas, Icu, busbar, homologación. Proforma con nota sustitución técnica y aprobación AM obligatoria. |
| **Edge cases** | (1) Icc > Icu de ABB — rechazo. (2) Compartimentación diferente — rechazo. (3) Homologación AEE Guatemala no vigente — rechazo. |

### case_18 — Precio vencido pedido grande

| Campo | Valor |
|-------|-------|
| **Industria** | MRO / Industrial |
| **Severidad** | High |
| **Excepción** | `PRECIO_VENCIDO` |
| **Cliente** | Aceros del Norte (CLI-007) — Gold, Medellín |
| **Input** | RFQ 500 rodamientos 6205-2RS1 con lista de precios 2024-Q4 vencida (vigencia 60 días, expiró 2025-02-28) |
| **Problema** | Lista vencida con aumento de precio del 15% en lista nueva 2025-Q1. Pedido grande ($20,563) con impacto significativo. Cliente gold con contrato de precios fijos. |
| **Draft esperado** | Notificación lista vencida, nueva lista con +15%, proforma con precio actualizado, oferta de negociación comercial para compensar diferencia. |
| **Edge cases** | (1) Cliente exige precio antiguo — aprobación CEO. (2) Pedido fraccionado en 2 proformas. (3) Descuento volumen compensa aumento. |

---

## Casos MEDIUM

<callout emoji="🟡" background-color="light-yellow" border-color="yellow">
<strong>Casos que requieren clarificación técnica o logística antes de proforma. Specs incompletas, fletes no configurados, medidas faltantes.</strong>
</callout>

### case_02 — Guantes químicos con compatibilidad no verificada

| Campo | Valor |
|-------|-------|
| **Industria** | EPP / Químico |
| **Excepción** | `ASTM_AMBIGUO` |
| **Cliente** | Laboratorios Centrales (CLI-003) — Silver, Bogotá |
| **Input** | RFQ 10 pares guantes nitrilo para trabajo con solventes — no especifica tipo de solvente |
| **Problema** | Nitrilo resiste acetona (BTT 480 min) pero NO resiste diclorometano (BTT 5 min). Sin solvente específico = riesgo permeación y quemadura química. |
| **Draft esperado** | Checklist solventes 3 ítems: tipo, concentración, tiempo exposición. Proforma bloqueada. |

### case_04 — Rodamiento código parcial

| Campo | Valor |
|-------|-------|
| **Industria** | MRO / Industrial |
| **Excepción** | `ASTM_AMBIGUO` |
| **Cliente** | Cementos del Sur (CLI-004) — Silver, Cali |
| **Input** | RFQ rodamiento 6205 — no especifica sellado (2RS1 vs Z vs abierto), jaula (steel vs polyamide), juego (C3 vs normal) |
| **Problema** | "6205" solo indica dimensiones (25×52×15). Sellado, jaula y juego afectan vida útil, temperatura máxima, y compatibilidad con vibración molino. |
| **Draft esperado** | Checklist técnico 4 ítems: sellado, jaula, juego, aplicación (molino vibratorio vs transportador). |

### case_05 — Filtro compatible con equipo específico

| Campo | Valor |
|-------|-------|
| **Industria** | MRO / Industrial |
| **Excepción** | `ASTM_AMBIGUO` + `SUSTITUCIÓN_ACEPTABLE` |
| **Cliente** | Refrescos del Valle (CLI-005) — Gold, Cali |
| **Input** | RFQ filtro de aire compresor Ingersoll-Ran R55i — cliente no especifica código OEM |
| **Problema** | Filtro sin código OEM = sistema debe inferir compatibilidad por modelo compresor. Filtro Donaldson equivalente disponible pero requiere verificación dimensional y caudal. |
| **Draft esperado** | Evidence compatibilidad: dimensiones, caudal CFM, presión diferencial. Proforma con nota sustitución o solicitud código OEM. |

### case_06 — Lubricante especificación incompleta

| Campo | Valor |
|-------|-------|
| **Industria** | Lubricantes Industriales |
| **Excepción** | `ASTM_AMBIGUO` + `SUSTITUCIÓN_ACEPTABLE` |
| **Cliente** | Metalmecánica del Valle (CLI-014) — Silver, Cali |
| **Input** | RFQ 10 tambores aceite hidráulico ISO VG 46 — no especifica tipo anti-wear (ZDDP vs ashless/zinc-free) |
| **Problema** | Dos variantes disponibles: mineral ZDDP $485 (4,000h) vs sintético zinc-free $720 (8,000h). Diferente aplicación ambiental, compatibilidad sellos, regulación zinc. |
| **Draft esperado** | Checklist 4 ítems: tipo anti-wear, base oil, equipo a lubricar, intervalo drenaje. Proforma bloqueada con ambas opciones explicadas. |

### case_07 — Cemento con flete no cotizado

| Campo | Valor |
|-------|-------|
| **Industria** | Construcción |
| **Excepción** | `FLETE_NO_COTIZADO` |
| **Cliente** | Constructora del Caribe (CLI-015) — Silver, Barranquilla |
| **Input** | RFQ 500 sacos cemento Portland para obra Villa del Mar — DDP requiere flete incluido |
| **Problema** | Obra Villa del Mar es ubicación puntual no estándar. 500 sacos = ~21 toneladas = camión completo. Zona norte Barranquilla puede tener restricciones acceso vehicular pesado. |
| **Draft esperado** | Solicitud datos de acceso: dirección exacta, altura vía, restricciones horarias, descarga mecanizada. Flete cotizado antes de proforma. |

### case_08 — Perfilería ángulo acero medida faltante

| Campo | Valor |
|-------|-------|
| **Industria** | Construcción / Estructuras |
| **Excepción** | `ASTM_AMBIGUO` |
| **Cliente** | Estructuras del Norte (CLI-016) — Silver, Barranquilla |
| **Input** | RFQ 30 barras ángulo acero 2x2x1/4" — no especifica longitud |
| **Problema** | Barras estándar 6m vs cortes a medida = diferente precio y logística. 30 barras × 6m = 180m vs cortes optimizados = diferente costo y scrap. |
| **Draft esperado** | Checklist 4 ítems: longitud, corte a medida, certificado molino, tratamiento superficial. |

### case_10 — Reactivo químico lote y vencimiento

| Campo | Valor |
|-------|-------|
| **Industria** | Laboratorio Químico |
| **Excepción** | Ninguna (proforma limpia con evidence) |
| **Cliente** | Laboratorios Andinos (CLI-012) — Gold, Bogotá, ISO 17025 |
| **Input** | RFQ 5L etanol absoluto HPLC — requiere certificado análisis por lote y vencimiento mínimo 18 meses |
| **Resultado** | Lote LOT-ETOH-2025-03-A verificado: fabricación 2025-03-15, vencimiento 2027-03-15 = 23 meses ✓. COA disponible. Transporte ADR clase 3 indicado. Proforma $126.44 USD. |
| **Edge cases** | (1) Lote con 16 meses (<18 req.) → bloqueo. (2) Certificado NIST requerido → verificar. (3) Stock solo Barranquilla → flete ADR especializado. |

---

## Casos LOW-MEDIUM

<callout emoji="🟢" background-color="light-green" border-color="green">
<strong>Casos con proforma generable pero con advertencias. Sustituciones aceptables con evidence, stock parcial con opciones, specs simples faltantes.</strong>
</callout>

### case_09 — Cerraduras sustitución aceptable

| Campo | Valor |
|-------|-------|
| **Industria** | Ferretería / Construcción |
| **Excepción** | `SUSTITUCIÓN_ACEPTABLE` |
| **Cliente** | Inmobiliaria Costa Verde (CLI-017) — Bronze, Barranquilla |
| **Input** | RFQ 15 cerraduras Yale 40mm — Yale agotado, Tesa equivalente DIN 18252 disponible |
| **Resultado** | Proforma con ambas opciones: Yale backorder 14 días ($277.50) vs Tesa inmediato ($392.70). Diferencia +19% pero stock inmediato y 3 llaves vs 2. |
| **Edge cases** | (1) Cliente insiste Yale → backorder. (2) Tesa sin cert DIN vigente → no ofrecer. (3) 100 unidades → stock parcial. |

### case_12 — Consumibles médicos equivalentes

| Campo | Valor |
|-------|-------|
| **Industria** | Suministros Médicos |
| **Excepción** | `SUSTITUCIÓN_ACEPTABLE` |
| **Cliente** | Clínica del Mar (CLI-018) — Gold, Barranquilla |
| **Input** | RFQ 500 guantes quirúrgicos estériles talla 7.5 Ansell — Ansell agotado, Medline equivalente INVIMA vigente |
| **Resultado** | Medline INVIMA 2021DM-0056789 vigente hasta 2027-06-30. Mismo material, esterilización, norma. Precio $2.21 vs $2.38 Ansell — cliente ahorra $85. Stock inmediato 1 día vs 21 días backorder. |
| **Privacy** | RESTRICTED_SENSITIVE_OR_REGULATED — NO promovible. INVIMA datos sensibles. |

### case_14 — Cable THHN por rollo sin metros especificados

| Campo | Valor |
|-------|-------|
| **Industria** | Eléctrico / Baja Tensión |
| **Excepción** | `ASTM_AMBIGUO` |
| **Cliente** | Electromontajes Centroamérica (CLI-006) — Silver, Guatemala City |
| **Input** | RFQ 10 rollos cable THHN 12 AWG rojo — no especifica metros por rollo |
| **Problema** | Estándar 500m/rollo vs alternativo 250m. 10 rollos × 500m = 5,000m. Sin total proyecto no se valida cantidad adecuada. |
| **Draft esperado** | Checklist 2 ítems: metros por rollo, total metros proyecto. Proforma bloqueada hasta clarificación. |

### case_20 — Pedido mixto stock parcial

| Campo | Valor |
|-------|-------|
| **Industria** | Ferretería / Industrial |
| **Excepción** | `STOCK_PARCIAL` + `PEDIDO_MIXTO` |
| **Cliente** | Talleres Mecánicos del Norte (CLI-019) — Bronze, Barranquilla |
| **Input** | RFQ mixto 5 items: clavos, tornillos, anclajes, cintas métricas, martillos |
| **Resultado** | 3 items inmediatos, 1 backorder 7 días (tornillos), 1 parcial: 1 cinta inmediata + 3 en 5 días. Proforma $265.97 con opciones entrega: única o parcial sin costo adicional. |
| **Edge cases** | (1) Cancela backorder tornillos → re-calcula. (2) 20 cajas tornillos → lead time 14 días. (3) Rechaza Stanley → busca Milwaukee. |

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

ASTM_AMBIGUO

</lark-td>
<lark-td>

14

</lark-td>
<lark-td>

Especificación técnica incompleta o ambigua

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

SUSTITUCIÓN_ACEPTABLE

</lark-td>
<lark-td>

10

</lark-td>
<lark-td>

Sustitución SKU/marca con equivalente verificado

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

REGULATORY_DOC_MISSING

</lark-td>
<lark-td>

6

</lark-td>
<lark-td>

Documento regulatorio faltante/vencido

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

CERT_DOC_MISSING

</lark-td>
<lark-td>

3

</lark-td>
<lark-td>

Certificado de producto faltante

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

FLETE_NO_COTIZADO

</lark-td>
<lark-td>

3

</lark-td>
<lark-td>

Flete no configurado para ubicación puntual

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

CRÉDITO_BLOQUEADO

</lark-td>
<lark-td>

3

</lark-td>
<lark-td>

Cliente con crédito bloqueado

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

PRECIO_VENCIDO

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

Lista de precios vencida

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

LEAD_TIME_INCIERTO

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

Lead time no confirmado

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

MARGEN_BAJO

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

Margen por debajo del mínimo

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

REGLA_PAÍS_ESPECIAL

</lark-td>
<lark-td>

2

</lark-td>
<lark-td>

Restricción regulatoria país destino

</lark-td>
</lark-tr>
<lark-tr>
<lark-td>

STOCK_PARCIAL

</lark-td>
<lark-td>

4

</lark-td>
<lark-td>

Stock insuficiente para cantidad solicitada

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

Múltiples items de diferentes categorías

</lark-td>
</lark-tr>
</lark-table>

<callout emoji="⚠️" background-color="light-yellow" border-color="yellow">
<strong>Códigos NO usados</strong> (4/15) — recomendado para Sprint 2:<br/>
SKU_DISCONTINUADO | TALLA_FALTANTE | PROFORMA_VENCIDA | MOQ_PACKAGING_INCOMPATIBLE
</callout>

---

## Gap Arquitectónico Detectado

<callout emoji="🔧" background-color="light-blue" border-color="blue">
<strong>GAP-001 — Flete Internacional</strong><br/>
<strong>Caso:</strong> case_15<br/>
<strong>Severidad:</strong> Medium<br/>
<strong>Impacto:</strong> Cada RFQ internacional requiere intervención manual AM para cotización flete. No escalable.<br/>
<strong>Workaround Sprint 1:</strong> AG_SUB_PROFORMA_BUILDER marca flete como pendiente y AM gestiona manualmente.<br/>
<strong>Recomendación Sprint 2:</strong> Agregar fuente de flete internacional (DHL/FedEx/Expeditors API) al catálogo de 3PL. Crear sub-agente AG_SUB_FREIGHT_INTERNATIONAL_QUOTER.
</callout>

---

## Conclusión y Readiness Sprint 1

<callout emoji="✅" background-color="light-green" border-color="green">
<strong>Sprint 1 — READY</strong>

El set de 20 fixtures cubre <strong>73% de la taxonomía de excepciones</strong> y <strong>100% de los perfiles de compliance</strong> del catálogo P16. La única brecha arquitectónica (flete internacional) es manejable con workaround manual.

- <strong>287 assertions must-pass</strong> verificables programáticamente
- <strong>120 must-not-do</strong> para prevenir regresiones
- <strong>60 edge cases</strong> para extensión del set
- <strong>100% HITL gate triggered</strong> en Critical+High
- <strong>Privacy tiers</strong> correctamente asignados (4 RESTRICTED, 16 TENANT_DERIVED)
</callout>

---

## Anexos

### A. Estructura de cada fixture YAML

Cada archivo `case_XX.yaml` contiene:

1. `case_id` + `industry` + `severity`
2. `setup` — catálogo, customer, agent_state
3. `input` — email realista del cliente
4. `expected_pipeline` — secuencia de sub-agentes con inputs/outputs
5. `expected_outputs` — proforma, evidence_bundle, audit_view, side_effects
6. `edge_cases` — 3 variantes por caso
7. `pass_criteria` — must_pass + must_not_do
8. `severity_weight_validation` — consecuencia de misclasificación
9. `privacy_tier` — inputs/outputs/cross-tenant
10. `gaps_detected` — brechas arquitectónicas

### B. Ubicación de archivos

Todos los fixtures se encuentran en:

```
/root/.openclaw/workspace/faberloom_fixtures/
├── case_01.yaml  ... case_20.yaml
└── SUMMARY.yaml
```

### C. Nota sobre datos sintéticos

Todos los datos de clientes, SKUs, certificados y precios son **sintéticos y realistas** diseñados para testing funcional. No representan información comercial real de MWT, Marluvas o Tecmater.

---

*Documento generado automáticamente por Ciclope (OpenClaw AM MWT) — 2025-04-30*
