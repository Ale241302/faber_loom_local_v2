# PLB_DEMAND_FORECASTING — Playbook de Demand Forecasting B2B
id: PLB_DEMAND_FORECASTING
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Distribucion (IDX_DISTRIBUCION)
aplica_a: [SHARED]

---

## A. Propósito

Procedimiento estándar para ejecutar un análisis de demanda y forecast para clientes B2B industriales. Aplica principalmente a Marluvas (calzado seguridad industrial, fabricante Brasil). Extensible a Tecmater.

Diferencial clave vs Forecast Pro: estadística pura + contexto de negocio inyectable (señales de contrato, auditorías, normativa, lead time). Ver ENT_DIST_FORECAST_SIGNALS para catálogo de señales.

---

## B. Cuándo usar este playbook

- Cliente solicita proyección de compras para próximo trimestre/semestre
- Preparación de pitch de servicio de forecasting vs competencia
- Auditoría interna de reorder points por SKU
- Detección de stockouts históricos que distorsionan demanda real

**No usar cuando:** historial < 3 meses. Con < 3 meses entregar solo benchmark Naive con advertencia explícita.

---

## C. Requerimientos de datos

### Mínimo para modelar

| Dato | Formato | Umbral mínimo | Impacto si falta |
|------|---------|---------------|-----------------|
| Historial de compras por SKU | CSV/Excel fecha + SKU + unidades | 6 meses | Modelo degradado a Naive |
| Lead time documentado | Días (número) | Obligatorio | Reorder point incalculable |
| SKUs activos | Lista | Obligatorio | No se puede delimitar análisis |

### Ideal para máxima precisión

| Dato | Por qué importa |
|------|----------------|
| 12+ meses de historia | Detectar estacionalidad anual |
| 24+ meses de historia | Habilita SARIMA, mejor detección ciclos |
| Stockouts documentados con fechas | Evita subestimar demanda real |
| Calendario de eventos cliente | Input para Agent_C Context Injector |
| Export Forecast Pro (si cliente lo tiene) | Comparación directa MAPE en Agent_D |

---

## D. Lógica de selección de modelo (Agent_B)

| Condición | Modelo asignado | Razón |
|-----------|----------------|-------|
| Zeros > 40% de períodos | Croston | Demanda intermitente — ETS/ARIMA distorsionan |
| Historia < 12 meses | Holt-Winters o ETS auto | Insuficiente para detectar estacionalidad anual |
| Historia ≥ 12 meses | ETS auto + SARIMA, elegir por AIC | Evaluar ambos, quedarse con menor AIC |
| Cualquier caso | Seasonal Naive como baseline | Benchmark obligatorio para Agent_D |

Validación siempre con backtest rolling hold-out últimos 3 meses.
Métrica principal: MAPE. Secundaria: MAE en unidades absolutas.

---

## E. Proceso de ejecución — Arquitectura Swarm 5 agentes

Ejecutar A → B → C → D → E en secuencia. Cada agente recibe output del anterior.

```
ORCHESTRATOR
├── Agent_A: Data Profiler
│   Output: DATA_QUALITY_REPORT (gaps, stockouts, outliers, veredicto)
├── Agent_B: Statistical Engine
│   Output: SKU_FORECAST (modelo, MAPE, unidades × mes, IC80%)
├── Agent_C: Context Injector
│   Output: CONTEXT_ADJUSTMENT × señal (ref: ENT_DIST_FORECAST_SIGNALS)
│           forecast_ajustado = estadístico + ajustes contextuales
├── Agent_D: Accuracy Arbiter
│   Output: ACCURACY_REPORT (MAPE nuestro vs benchmark, ganancia en unidades)
└── Agent_E: Output Synthesizer
    Output: EXECUTIVE_SUMMARY + METHODOLOGY_NOTE + NEXT_STEPS
```

Schema de output completo: SCH_DEMAND_FORECAST_REPORT

**Modelo recomendado para ejecutar el swarm:** Kimi 2.5 (long-context, procesa dataset completo en un solo pass). Alternativa: Claude Sonnet 4.6 con dataset < 500 filas.

---

## F. Reglas de entrega al cliente

1. **Separar siempre:** forecast estadístico puro vs forecast ajustado final
2. **Declarar fuente de cada ajuste contextual:** dato objetivo / estimación CEO / supuesto explícito
3. **Confianza explícita por ajuste:** ALTA / MEDIA / BAJA
4. **Dato faltante = marcado, no inventado:** `[DATO_FALTANTE: descripción]`
5. **Reorder point siempre incluido** con fórmula: `(demanda_diaria_promedio × lead_time_días) + stock_seguridad`
6. **SKU con MAPE > 40%** → alertar explícitamente como alta variabilidad

---

## G. Consideraciones específicas Marluvas

- Lead time estándar Brasil → LATAM: 60-90 días (incluye fabricación + transporte + aduana)
- Demanda atada a ciclos de obra, renovaciones de plantilla, auditorías de seguridad
- BRL/USD impacta costo de producto → posible ajuste de precio → efecto en demanda
- Normativa aplicable: NOM-017-STPS (México), regulaciones EPP por país
- Ver ENT_DIST_FORECAST_SIGNALS para señales documentadas con ajustes históricos

---

Changelog:
- v1.0 (2026-04-14): Creación. Conocimiento extraído de Swarm Demo Marluvas — Distribuidor Industrial del Centro S.A. Metodología validada en sesión CEO.
