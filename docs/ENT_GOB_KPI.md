# ENT_GOB_KPI — Indicadores de Desempeño
id: ENT_GOB_KPI
version: 1.0
domain: Gobernanza (IDX_GOBERNANZA)
status: DRAFT
visibility: [INTERNAL]
stamp: DRAFT — pendiente aprobación CEO
iso: 9001:2015 §9.1, 45001:2018 §9.1
aplica_a: [MWT]

---

## A. Propósito

KPIs medibles por proceso. Alimentan la revisión por la dirección (PLB_REVISION_DIRECCION) y demuestran mejora continua a un auditor ISO.

Principio: solo se mide lo que se puede actuar. KPI sin acción asociada = métrica de vanidad.

---

## B. KPIs por módulo

### B1. Expedientes (M1)

| KPI | Fórmula | Fuente | Umbral verde | Umbral rojo | Frecuencia |
|-----|---------|--------|-------------|-------------|-----------|
| Tiempo promedio por fase | Σ(días en fase) / n expedientes | ENT_OPS_STATE_MACHINE event log | ≤ histórico + 10% | > histórico + 30% | Mensual |
| % expedientes con corrección de costo | Expedientes con R1+ en costos / total | ART-11 versioning | < 10% | > 25% | Mensual |
| Reloj crédito: días promedio de cobro | Σ(días hasta pago) / n expedientes | Reloj crédito 90d | ≤ 60 días | > 80 días | Mensual |
| Expedientes bloqueados por crédito | Count(estado=BLOQUEADO por crédito) | State machine | 0 | > 2 simultáneos | Semanal |
| Proformas aprobadas sin revisión | Proformas R0 aprobadas / total | ART-02 versioning | > 80% | < 60% | Mensual |

### B2. Pricing (M2)

| KPI | Fórmula | Fuente | Umbral verde | Umbral rojo | Frecuencia |
|-----|---------|--------|-------------|-------------|-----------|
| Margen real vs proyectado | |margen_real - margen_proyectado| / margen_proyectado | ENT_OPS_EXPEDIENTE.C2 | < 5% desviación | > 15% desviación | Por expediente cerrado |

### B3. Marketplace / Amazon (M8)

| KPI | Fórmula | Fuente | Umbral verde | Umbral rojo | Frecuencia |
|-----|---------|--------|-------------|-------------|-----------|
| TACoS | Ad spend / total revenue | Amazon Advertising | < 12% | > 20% | Semanal |
| ACoS | Ad spend / ad revenue | Amazon Advertising | < 25% | > 40% | Semanal |
| Sessions/día | Daily page views | Amazon Business Reports | [CEO definir] | [CEO definir] | Diario |
| Conversion rate | Units ordered / sessions | Amazon Business Reports | > 15% | < 8% | Semanal |
| BSR (categoría) | Best Sellers Rank | Amazon product page | Top [CEO definir] | > [CEO definir] | Semanal |
| Reviews (count) | Total review count | Amazon product page | Tendencia ↑ | Estancado >30d | Mensual |
| Reviews (rating) | Average star rating | Amazon product page | ≥ 4.3 | < 4.0 | Mensual |
| Devoluciones por defecto de producto | Returns "defective" / units sold | Amazon reports | < 2% | > 5% | Mensual |


### B3b. Mapeo de fuentes KPI — Seller Central (ref: Perplexity Prompt 8)

| KPI | Fuente primaria | Reporte/Ubicación | Columna | Frecuencia |
|-----|----------------|-------------------|---------|------------|
| Revenue mensual | Seller Central | Business Reports → By ASIN | Ordered Product Sales | Mensual |
| Unidades vendidas | Seller Central | Business Reports → By ASIN | Units Ordered | Mensual |
| Conversion Rate | Seller Central | Business Reports → By ASIN | Unit Session Percentage | Mensual |
| Sessions | Seller Central | Business Reports → By ASIN | Sessions - Total | Mensual |
| Ad Spend | Advertising Console | Reports → Sponsored Products | Spend | Mensual |
| ACoS | Advertising Console | Reports → Sponsored Products | ACOS | Mensual |
| TACoS | Calculado | Ad Spend ÷ Total Revenue × 100 | — | Mensual |
| BSR subcategoría | Manual | Amazon.com → Product Information | Best Sellers Rank | Mensual |
| Reviews count | Manual | Amazon.com → Ratings section | Total reviews | Mensual |
| Rating promedio | Manual | Amazon.com → Ratings section | Estrellas | Mensual |
| Return rate | Seller Central | Reports → Fulfillment → FBA Returns | Quantity | Mensual |
| Inventory (FBA) | Seller Central | Inventory → Manage FBA Inventory | Fulfillable Quantity | Semanal |
| IPI | Seller Central | Inventory → Inventory Performance | Score visual | Mensual |

> Solo con Seller Central (costo $0) se obtienen 12 de 14 KPIs. BSR y Reviews requieren anotación manual. Helium 10 Platinum ($99/mes) agrega: P&L automatizado, BSR histórico, keyword tracking, market share. Guía completa: INVESTIGACIONES_PERPLEXITY_GAPS_CEO.pdf §4.

### B4. Scanner SaaS (futuro)

| KPI | Fórmula | Fuente | Umbral verde | Umbral rojo | Frecuencia |
|-----|---------|--------|-------------|-------------|-----------|
| Attach rate plantilla/scan | Ventas plantilla post-scan / total scans | Scanner SaaS DB | > 25% | < 15% | Semanal |
| Scans por distribuidor/mes | Count(scans) por tenant | Scanner SaaS DB | > 50 | < 20 | Mensual |
| Uptime del servicio | Horas disponible / horas totales | Monitoring | > 99.5% | < 99% | Mensual |
| Incidentes de seguridad | Count(incidentes) | PLB_INCIDENT_RESPONSE log | 0 | > 0 | Mensual |
| Tiempo de respuesta a incidente | Horas desde detección hasta contención | PLB_INCIDENT_RESPONSE log | < 4 horas | > 24 horas | Por incidente |

### B5. SSO (ISO 45001)

| KPI | Fórmula | Fuente | Umbral verde | Umbral rojo | Frecuencia |
|-----|---------|--------|-------------|-------------|-----------|
| Incidentes laborales | Count(incidentes) | ENT_GOB_SSO log | 0 | > 0 | Trimestral |
| Días sin incidente | Días consecutivos sin incidente | ENT_GOB_SSO log | > 90 | < 30 | Continuo |

---

## C. Dashboard de revisión

Para PLB_REVISION_DIRECCION, el SCH_ISO_AUDIT_PACK genera una vista consolidada de todos los KPIs con semáforo verde/amarillo/rojo y tendencia (mejorando/estable/empeorando).

Fuente de datos MVP: manual (CEO reporta). Post-MVP: automático desde PostgreSQL vía Grafana (ref → ENT_PLAT_OBSERVABILIDAD).

---

## F. Pipeline de datos por módulo

Principio: KPI sin fuente de datos = métrica de vanidad. KPI con fuente definida + canal previsto = métrica en standby.

### F1. Marketplace / Amazon (B3)

| KPI | Fuente primaria | Fuente secundaria | Canal actual | Canal objetivo | Status |
|-----|----------------|-------------------|-------------|----------------|--------|
| TACoS | Amazon Advertising Console | Helium 10 | Manual (export CSV) | API SP-API / Helium 10 API | MANUAL |
| ACoS | Amazon Advertising Console | Helium 10 | Manual (export CSV) | API SP-API / Helium 10 API | MANUAL |
| Sessions/día | Amazon Seller Central | AMZScout | Manual (Business Reports) | API SP-API | MANUAL |
| Conversion rate | Amazon Seller Central | AMZScout | Manual (Business Reports) | API SP-API | MANUAL |
| BSR | Amazon (product page) | Helium 10 / AMZScout | Manual (consulta directa) | Helium 10 API / AMZScout API | MANUAL |
| Reviews (count + rating) | Amazon (product page) | Helium 10 | Manual | Helium 10 API | MANUAL |
| Devoluciones por defecto | Amazon Seller Central | — | Manual (Returns report) | API SP-API | MANUAL |

### F2. Expedientes (B1)

| KPI | Fuente primaria | Canal actual | Canal objetivo | Status |
|-----|----------------|-------------|----------------|--------|
| Tiempo promedio por fase | ENT_OPS_STATE_MACHINE event log | Sistema (cuando esté activo) | Automático (event log → cálculo) | PENDIENTE PLATAFORMA |
| % corrección de costo | ART-11 versioning | Sistema | Automático | PENDIENTE PLATAFORMA |
| Reloj crédito: días cobro | State machine | Sistema | Automático (cron Sprint 2) | PENDIENTE PLATAFORMA |

### F3. Pricing (B2)

| KPI | Fuente primaria | Canal actual | Canal objetivo | Status |
|-----|----------------|-------------|----------------|--------|
| Margen real vs proyectado | ENT_OPS_EXPEDIENTE.C2 | Sistema | Automático (por expediente cerrado) | PENDIENTE PLATAFORMA |

### Leyenda de Status

| Status | Significado |
|--------|------------|
| MANUAL | Dato disponible, se carga manualmente desde la fuente |
| PENDIENTE PLATAFORMA | Dato depende de módulo de plataforma que aún no está activo |
| AUTOMÁTICO | Pipeline conectado, dato fluye sin intervención |

### Nota de evolución
Cuando se integre cada API (SP-API, Helium 10 API, AMZScout API), cambiar el status de MANUAL → AUTOMÁTICO y documentar en MANIFIESTO_CAMBIOS. No sabemos hoy qué se puede automatizar — se afina cuando el pipeline exista.

---

Stamp: DRAFT — Pendiente aprobación CEO
