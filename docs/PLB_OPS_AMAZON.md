# PLB_OPS_AMAZON — Playbook Operaciones Amazon
id: PLB_OPS_AMAZON
status: DRAFT
visibility: [INTERNAL]
version: 1.1
domain: Operaciones (IDX_OPS) · Plataforma (IDX_PLATAFORMA)
classification: PLAYBOOK — Instrucciones operativas canal Amazon FBA
aplica_a: [MWT]

refs:
  - ENT_COMERCIAL_COSTOS (fees, storage)
  - ENT_COMP_AMAZON (compliance policies)
  - ENT_GOB_KPI.B3 (métricas marketplace)
  - PLB_EXPERIMENTACION (cambios de listing)
  - PLB_SUPPORT (post-venta)
  - PLB_ADS (publicidad)
  - ENT_PLAT_AUTOMATIONS (AUT-001 a AUT-004)

---

## Reglas Generales Ops (absorbido de PLB_OPS v0.1)

**Identidad:** RW-Ops — agente de operaciones

**Herramientas:** Inventario, logística, fulfillment

**Métricas core:** Stock days, lead time, fill rate

**Reglas operativas:**
- Fórmulas de safety stock (ref → ENT_OPS_DEMAND_PLANNING)
- Semáforos de nivel (ref → ENT_OPS_DEMAND_PLANNING)
- Escalamiento por stock bajo → CEO

**Comunicación inter-agente:**
- Stock check request ← Ads
- Feasibility check ← Growth
- Escalamiento → CEO

---

## A. Account Health Management

### A1. Métricas del Account Health Dashboard

| Métrica | Descripción | Umbral verde | Umbral amarillo | Umbral rojo | Fuente |
|---------|-------------|--------------|-----------------|-------------|--------|
| ODR (Order Defect Rate) | A-Z claims + chargebacks + negative feedback / pedidos | <1% | 0.8%-1% | ≥1% (riesgo suspensión) | Seller Central > Account Health |
| LSR (Late Shipment Rate) | Envíos confirmados después de expected ship date | <4% | 3%-4% | ≥4% | Seller Central > Account Health |
| VTR (Valid Tracking Rate) | Pedidos con tracking válido / pedidos enviados | >95% | 90%-95% | <90% | Seller Central > Account Health |
| Pre-fulfillment Cancel Rate | Cancelaciones antes de envío / pedidos | <2.5% | 2%-2.5% | ≥2.5% | Seller Central > Account Health |
| IP Score (Intellectual Property) | Score de salud de propiedad intelectual | Sin complaints | 1-2 complaints activos | ≥3 complaints o policy warning | Seller Central > Account Health |
| Policy Compliance | Violaciones de políticas de Amazon | 0 activas | 1 warning activo | Cualquier violation activa | Seller Central > Account Health |

**Nota FBA:** LSR, VTR y Pre-fulfillment Cancel Rate son gestionados por Amazon cuando se usa FBA. Se monitorean igualmente porque Amazon puede atribuir errores al seller en casos edge (commingled, multi-channel).

### A2. Protocolo de respuesta — métrica en amarillo

1. **Detectar:** revisión diaria del Account Health Dashboard (ref → sección F, cadencia diaria)
2. **Diagnosticar:** identificar los pedidos/casos específicos que causan degradación
3. **Actuar:**
   - ODR amarillo → revisar A-Z claims abiertos, responder en <24h, escalar a ref → sección C (Case Management)
   - LSR amarillo → verificar con FBA si hay delays de warehouse, abrir case si es error de Amazon
   - VTR amarillo → verificar tracking numbers en órdenes recientes, abrir case si FBA no subió tracking
4. **Documentar:** registrar incidente y acción tomada
5. **Monitorear:** seguimiento diario hasta retorno a verde

### A3. Protocolo de respuesta — métrica en rojo

1. Todo lo de A2 + escalamiento inmediato
2. Si ODR ≥1%: **ALERTA CRÍTICA** — riesgo de suspensión. Pausar campañas PPC (ref → PLB_ADS). Priorizar resolución de claims sobre cualquier otra tarea.
3. Si IP complaint activo: revisar ENT_COMP_AMAZON.E para framework de appeal
4. Documentar timeline de acciones para potencial Plan of Action (POA)

Ref → ENT_COMP_AMAZON para detalle completo de compliance policies.

---

## B. Inventory Management FBA

### B1. Reglas de restock

Automatizaciones planificadas (ref → ENT_PLAT_AUTOMATIONS):
- AUT-001: Inventory sync FBA-US (cada 4h, n8n)
- AUT-002: Low stock alert (diario, n8n)
- AUT-003: Stranded inventory alert (diario, n8n)
- AUT-004: Restock calculation (semanal, Windmill)

**Hasta que AUT-001..004 estén activos:** restock se calcula manualmente con fórmula:

```
Restock quantity = (daily_velocity × lead_time_days × safety_factor) - current_FBA_units
  donde:
    daily_velocity = units sold últimos 30 días / 30
    lead_time_days = [PENDIENTE — CEO definir según cadena actual FACTORY-CN → FBA-US]
    safety_factor = 1.5 (conservative) o 1.2 (lean)
```

### B2. IPI Score (Inventory Performance Index)

- Score 0-1000. Amazon evalúa trimestralmente.
- **Umbral mínimo:** 400 (debajo de 400 = límites de almacenamiento impuestos)
- **Target:** >500 (acceso a almacenamiento ilimitado cuando disponible)
- Factores: sell-through rate, excess inventory %, stranded inventory %, in-stock rate
- Acción si IPI <450: reducir aged inventory (ref → B5), crear removal orders, optimizar velocity con PPC

### B3. Regla de stock mínimo para PPC

**REGLA CARDINAL:** Nunca escalar PPC si stock FBA <21 días de inventario.
- Origen: PLB_ADS (migrada aquí como fuente operativa)
- Lógica: escalar PPC con stock bajo = stockout = pérdida de BSR + ranking orgánico + penalización Amazon
- Si stock <21d: mantener PPC en nivel actual o reducir. NO lanzar campañas nuevas.
- Si stock <7d: pausar campañas excepto branded keywords
- Ref → PLB_ADS para gestión completa de campañas

### B4. Estacionalidad de storage fees

Fuente: ENT_COMERCIAL_COSTOS (dato canónico — no duplicar aquí)

| Período | Storage fee (standard-size) | Nota |
|---------|---------------------------|------|
| Enero - Septiembre | $0.78/ft³/mes | Tarifa base |
| Octubre - Diciembre | $2.40/ft³/mes | ~3x tarifa base — peak season surcharge |

**Implicación operativa:**
- Enviar inventario Q4 lo más tarde posible sin arriesgar stockout
- No sobre-enviar en septiembre (paga tarifa alta 3 meses)
- Calcular costo de almacenamiento como % del COGS para decisiones de restock

### B5. Aged inventory surcharges y protocolo de liquidación

Amazon cobra surcharges por inventario con >181 días en FBA (aged inventory surcharge, anteriormente LTSF).

**Protocolo de liquidación:**
1. Identificar SKUs con >120 días en FBA (pre-alerta, antes de surcharge)
2. Evaluar opciones: a) descuento agresivo para mover, b) removal order → bodega propia, c) liquidation program de Amazon, d) disposal (último recurso)
3. Decisión: CEO aprueba acción por SKU
4. Ejecutar antes de día 181 para evitar surcharge
5. Documentar decisión y resultado

---

## C. Case Management

### C1. Tipos de cases y SLA de respuesta

| Tipo de case | Ejemplo | SLA de primera respuesta | Prioridad |
|-------------|---------|--------------------------|-----------|
| Policy violation | Listing suprimido por claim no permitido | <12h | CRÍTICA |
| Listing suppression | ASIN desactivado por error de categoría o imagen | <24h | ALTA |
| A-Z Guarantee claim | Buyer escala disputa a A-Z | <24h (antes de que Amazon decida) | ALTA |
| IP complaint (tercero) | Otra marca reclama infracción | <24h | CRÍTICA |
| IP complaint (recibido) | Hijacker en nuestro listing | <48h | MEDIA |
| Account health warning | Amazon envía warning por métrica | <24h | ALTA |
| FBA inventory issue | Unidades perdidas, dañadas, discrepancia | <72h | MEDIA |
| Reimbursement | Solicitud de reembolso por error FBA | <7 días | BAJA |

### C2. Escalamiento

```
Nivel 1: Seller Support (chat/email)
  ↓ si no resuelve en 48h o respuesta genérica
Nivel 2: Reopen case con detalle adicional + solicitar supervisor
  ↓ si no resuelve en 72h adicionales
Nivel 3: Captive team (si disponible vía Account Health Dashboard)
  ↓ si no resuelve
Nivel 4: Account Manager (solo si aplica — requiere programa específico o invitación)
  ↓ último recurso
Nivel 5: Jeff@ email escalation (bezos@amazon.com — executive escalation, usar con extrema prudencia)
```

### C3. Plantillas de respuesta por tipo de case

[PENDIENTE — NO INVENTAR texto exacto. Crear templates cuando se tenga experiencia real con cada tipo de case]

Estructura esperada por template:
- Saludo profesional
- Referencia al case ID / ASIN / Order ID
- Descripción del problema
- Evidencia adjunta (si aplica)
- Acción solicitada
- Cierre

### C4. Registro de cases

Todo case abierto se documenta con: fecha, tipo, ASIN/order, acción tomada, resultado, días hasta resolución. Esto alimenta métricas de Account Health (ref → ENT_GOB_KPI.B3).

---

## D. Listing Health

### D1. Monitoreo de supresión

- **Cadencia:** diaria (ref → sección F)
- **Dónde:** Seller Central > Inventory > Manage Inventory > Suppressed
- **Causas comunes:** imagen no cumple requisitos, claim prohibido, categoría incorrecta, missing required attributes
- **Acción:** identificar causa → corregir → reactivar. Si la causa es policy → ref → ENT_COMP_AMAZON.B

### D2. Cambios no autorizados

Amazon puede modificar títulos, bullets, imágenes o categorías sin notificación. Brand Registry reduce pero no elimina esto.

**Protocolo:**
1. Detectar: comparar listing actual vs versión aprobada (ref → SCH_LISTING_AMAZON golden example)
2. Si cambio no autorizado: abrir case en Seller Central con evidencia de versión correcta
3. Si Brand Registry activo: usar "Report a violation" tool
4. Documentar cada incidente para pattern tracking

### D3. Hijackers / Unauthorized sellers

- **Detección:** otro seller aparece en nuestro listing (Buy Box compartido)
- **Acción inmediata:** verificar si es counterfeit o authorized reseller
- **Si counterfeit:** Report violation via Brand Registry → IP complaint
- **Si unauthorized:** evaluar impacto en Buy Box y pricing antes de actuar
- Ref → ENT_COMP_AMAZON.A2 (product authenticity requirements)

### D4. Cambios de contenido

Todo cambio de contenido en listings sigue el protocolo de experimentación:
- Ref → PLB_EXPERIMENTACION para framework de testing
- Ref → SCH_LISTING_AMAZON para estructura de listing y campos
- Regla: no cambiar título Y bullets simultáneamente (aislar variable)

---

## E. Reviews & Ratings Management

### E1. Protocolo de monitoreo

- **Cadencia:** diaria para reviews nuevas, semanal para trends (ref → sección F)
- **Qué monitorear:** rating promedio, count de reviews, reviews recientes negativas (1-2 estrellas)
- **Dónde:** Seller Central + Brand Analytics (si disponible) + Helium 10 (si activo)
- Ref → PLB_SUPPORT para protocolo post-venta que alimenta reviews

### E2. Respuesta a reviews negativas

**Framework (no templates — adaptar a cada caso):**
1. **Leer y clasificar:** ¿es problema de producto, shipping, expectativa incorrecta, o abuso?
2. **Si problema de producto real:** documentar para mejora (ref → ENT_PROD_GOL o producto correspondiente). Responder vía "Comment on review" con empatía + acción concreta.
3. **Si error de shipping/FBA:** responder explicando que fue error logístico, ofrecer solución vía buyer-seller messaging.
4. **Si expectativa incorrecta:** evaluar si el listing creó expectativa falsa → corregir listing si aplica.
5. **Si viola guidelines de Amazon (abusivo, irrelevante):** reportar vía "Report abuse" button.
6. **Regla:** NUNCA ofrecer reembolso a cambio de eliminar review. Esto viola ToS de Amazon.

### E3. Vine Program

- **Qué es:** Amazon Vine permite enviar unidades gratis a reviewers verificados de Amazon.
- **Cuándo activar:** al lanzar nuevo ASIN o cuando review count <30
- **Cuántos units:** Amazon permite hasta 30 unidades por ASIN en Vine
- **Costo:** fee por unidad inscrita (varía, verificar tarifa actual en Seller Central)
- **Decisión:** CEO aprueba activación y cantidad
- **Timing:** activar DESPUÉS de que listing esté optimizado (ref → SCH_LISTING_AMAZON)

### E4. Reglas anti-manipulación (lo que Amazon prohíbe)

Amazon prohíbe explícitamente:
- Solicitar reviews positivas (solo se puede solicitar "un review", no "un review positivo")
- Ofrecer descuentos, productos gratis o compensación a cambio de reviews
- Usar servicios de review manipulation
- Pedir a familiares/empleados que dejen reviews
- Manipular el sistema de "helpful" votes
- Crear cuentas falsas para dejar reviews

**Consecuencia:** suspensión de cuenta. Tolerancia cero.

Ref → ENT_COMP_AMAZON.A1 (Seller Code of Conduct)

---

## F. Cadencia operativa

### F1. Tabla de cadencia

| Frecuencia | Qué revisar | Quién ejecuta | Ref |
|-----------|------------|---------------|-----|
| **Diario** | Account Health Dashboard (ODR, LSR, VTR) | CEO (hoy) → operador (futuro) | A1 |
| **Diario** | Listings suprimidos | CEO → operador | D1 |
| **Diario** | Reviews nuevas | CEO → operador | E1 |
| **Diario** | Cases abiertos — seguimiento | CEO → operador | C1 |
| **Diario** | Inventory levels FBA (stockout risk) | CEO → operador | B1 |
| **Semanal** | Sales velocity + restock calculation | CEO → operador / AUT-004 | B1 |
| **Semanal** | PPC performance (ACoS, TACoS, spend) | CEO → operador | PLB_ADS |
| **Semanal** | Review trends (rating promedio, velocity) | CEO → operador | E1 |
| **Semanal** | Competitor price + listing changes | CEO → operador | ENT_MKT_COMPETENCIA |
| **Mensual** | IPI Score review | CEO | B2 |
| **Mensual** | Aged inventory check (>120 días) | CEO | B5 |
| **Mensual** | Keyword ranking + search term report | CEO | ENT_MKT_KEYWORDS |
| **Mensual** | Account Health summary para ENT_GOB_KPI | CEO | ENT_GOB_KPI.B3 |
| **Trimestral** | Storage fee impact analysis (pre-Q4) | CEO | B4 |
| **Trimestral** | Vine program evaluation | CEO | E3 |
| **Trimestral** | Full listing audit vs golden example | CEO | SCH_LISTING_AMAZON |

### F2. Transición CEO → operador

Hoy el CEO ejecuta todos los checks. Cuando se contrate operador:
1. Operador asume checks diarios y semanales
2. CEO retiene checks mensuales y trimestrales + decisiones de escalamiento
3. Protocolo de handoff: [PENDIENTE — crear cuando haya operador identificado]

---

## Z. Pendientes

| ID | Pendiente | Tipo | Desbloquea |
|----|-----------|------|-----------|
| Z1 | Definir lead_time_days para fórmula restock (B1) | Dato CEO | Cálculo automático restock |
| Z2 | Templates de respuesta a cases (C3) | Contenido | Estandarización respuestas |
| Z3 | Activar AUT-001 a AUT-004 (B1) | Técnico | Automatización inventory |
| Z4 | Protocolo handoff CEO → operador (F2) | Proceso | Escalabilidad operativa |

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO

Changelog:
- v0.1 (2026-03-14): header normalizado + status: STUB (Ola A).
- v1.0 (2026-03-15): STUB → DRAFT. Framework completo: 6 secciones (Account Health, FBA Inventory, Case Mgmt, Listing Health, Reviews, Cadencia). Refs cruzadas a ENT_COMP_AMAZON, ENT_COMERCIAL_COSTOS, PLB_ADS, PLB_EXPERIMENTACION, PLB_SUPPORT, ENT_PLAT_AUTOMATIONS. Regla stock <21d migrada desde PLB_ADS.
- v1.1 (2026-04-01): Absorción PLB_OPS v0.1 (reglas generales ops, identidad RW-Ops, comunicación inter-agente). Depuración Q2-2026.
