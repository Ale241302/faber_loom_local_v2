# SCH_FORECAST_OUTPUTS — Schema de Outputs del Demand Forecasting
id: SCH_FORECAST_OUTPUTS
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Schema Registry (SCHEMA_REGISTRY)
aplica_a: [SHARED]

---

## Propósito

Especificación exacta de cada formato de output que produce Agent_F del SKILL_DEMAND_FORECASTER. Define estructura, contenido por sección, y cuándo usar cada formato.

---

## requires

```yaml
requires:
  - SCH_DEMAND_FORECAST_REPORT    # datos del análisis ya procesados por Agents A-E
```

---

## OUTPUT 1 — Excel (.xlsx) — SIEMPRE generar

**Cuándo:** en todo engagement de forecasting, independiente de otros outputs.
**Herramienta Cowork:** skill xlsx

### Hoja 1: FORECAST

| Columna | Contenido |
|---------|-----------|
| SKU ID | sku_id |
| Descripción | sku_descripcion |
| Mes | YYYY-MM |
| Demanda Real | unidades históricas (vacío si es período futuro) |
| Forecast Estadístico | forecast_estadístico base de Agent_B |
| Forecast Ajustado | forecast final de Agent_C |
| IC80% Lower | intervalo_confianza_80.lower |
| IC80% Upper | intervalo_confianza_80.upper |
| Modelo Usado | nombre del modelo seleccionado |
| MAPE Backtest | % del modelo para ese SKU |

**Charts en Hoja 1:**
- Chart A: Línea — Demanda Real vs Forecast Ajustado + banda sombreada IC80% (por SKU, serie de tiempo completa)
- Chart B: Barras agrupadas — Forecast próximos N meses por SKU (comparativo entre SKUs)

### Hoja 2: AJUSTES CONTEXTUALES

| Columna | Contenido |
|---------|-----------|
| Señal | descripción de la señal |
| SKUs Afectados | lista |
| Mes Aplicado | YYYY-MM |
| Ajuste % | porcentaje aplicado |
| Unidades Delta | diferencia en unidades vs forecast estadístico |
| Confianza | ALTA / MEDIA / BAJA |
| Fuente | dato objetivo / estimación / supuesto |

**Chart en Hoja 2:**
- Chart C: Waterfall — Forecast estadístico base → ajustes por señal → forecast ajustado final (para el SKU principal o total)

### Hoja 3: REORDER POINTS

| Columna | Contenido |
|---------|-----------|
| SKU ID | sku_id |
| Descripción | sku_descripcion |
| Demanda Diaria Promedio | unidades/día calculadas del historial |
| Lead Time (días) | lead_time_dias del CONTEXT_PARAMS |
| Stock Seguridad | demanda_diaria × sqrt(lead_time) × 1.65 (Z=95%) |
| Reorder Point | (demanda_diaria × lead_time) + stock_seguridad |
| Stock Actual | del MMBE si disponible, sino [DATO_FALTANTE] |
| Urgencia Pedido | 🔴 bajo ROP / 🟡 dentro de 30 días / 🟢 OK |

### Hoja 4: DATA QUALITY (solo si hay advertencias)

Contenido: DATA_QUALITY_REPORT completo de Agent_A — gaps, stockouts sospechados, outliers.

---

## OUTPUT 2 — PowerPoint (.pptx) — para presentación a cliente

**Cuándo:** reunión de presentación de resultados al cliente, pitch de servicio de forecasting, demo vs Forecast Pro.
**Herramienta Cowork:** skill pptx
**Máximo:** 8 slides. Sin texto denso. Visual-first.

### Estructura de slides

| # | Slide | Contenido |
|---|-------|-----------|
| 1 | Portada | Cliente · Proveedor · Período analizado · Fecha |
| 2 | Resumen ejecutivo | 3 hallazgos clave (bullets cortos) + 1 alerta crítica destacada |
| 3 | Forecast por SKU | Tabla SKU × mes (forecast ajustado) + colores semáforo por MAPE |
| 4 | Gráfico principal | Chart A del Excel — línea demanda real vs forecast + IC80% |
| 5 | Ajustes contextuales | Chart C waterfall + tabla de señales aplicadas con confianza |
| 6 | Reorder Points | Tabla ROP por SKU con columna urgencia (🔴🟡🟢) |
| 7 | Nuestra metodología vs Forecast Pro | Tabla comparativa 10 capacidades |
| 8 | Próximos pasos | Dato faltante #1 · Frecuencia actualización · Acción inmediata |

**Paleta de colores recomendada:** fondos blancos, texto oscuro, azul para forecast, gris para histórico, naranja para ajustes contextuales, rojo para alertas.

---

## OUTPUT 3 — Word (.docx) — entregable técnico formal

**Cuándo:** cliente requiere documento formal con metodología, el análisis es para una auditoría, o hay múltiples stakeholders que necesitan leer el detalle.
**Herramienta Cowork:** skill docx

### Estructura del documento

| Sección | Contenido |
|---------|-----------|
| 1. Resumen Ejecutivo | Hallazgos clave, tabla forecast final, alertas críticas |
| 2. Datos Analizados | Cobertura, fuente SAP/CSV, DATA_QUALITY_REPORT de Agent_A |
| 3. Metodología Estadística | Modelo seleccionado por SKU con justificación, MAPE backtest |
| 4. Ajustes Contextuales | Tabla de señales, fuentes, confianza, impacto en unidades |
| 5. Accuracy vs Benchmark | ACCURACY_REPORT de Agent_D completo |
| 6. Forecast Detallado | Tabla SKU × mes con IC80% para todos los períodos |
| 7. Reorder Points | Tabla completa con fórmula aplicada |
| 8. Limitaciones | Datos faltantes, supuestos, advertencias de Agent_A |
| 9. Próximos Pasos | Frecuencia actualización, dato #1 a conseguir, SKU urgente |
| Anexo A | Tabla comparativa vs Forecast Pro |
| Anexo B | DATA_QUALITY_REPORT completo |

---

## OUTPUT 4 — PDF — entrega final

**Cuándo:** versión final para firma, envío por email al cliente, archivo.
**Herramienta Cowork:** skill pdf
**Fuente:** convertir el .pptx o .docx aprobado. No generar PDF directo desde datos crudos.

---

## Reglas de routing (para Agent_F)

```
SI output_requerido incluye "excel" o "datos"   → generar OUTPUT 1 (siempre)
SI output_requerido incluye "presentación"       → generar OUTPUT 2
SI output_requerido incluye "reporte" o "formal" → generar OUTPUT 3
SI output_requerido incluye "pdf" o "enviar"     → generar OUTPUT 4 (post-aprobación)
SI output_requerido = "completo"                 → generar OUTPUT 1 + 2 + 3
SI output_requerido no especificado              → generar OUTPUT 1 + preguntar si necesita PPT o Word
```

---

Changelog:
- v1.0 (2026-04-14): Creación. Specs para xlsx (4 hojas + 3 charts), pptx (8 slides), docx (9 secciones + 2 anexos), pdf. Routing rules para Agent_F.
