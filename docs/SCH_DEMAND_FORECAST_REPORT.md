# SCH_DEMAND_FORECAST_REPORT — Schema: Reporte de Demand Forecasting B2B
id: SCH_DEMAND_FORECAST_REPORT
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Schema Registry (SCHEMA_REGISTRY)
aplica_a: [SHARED]

---

## Metadatos del schema

| Campo | Valor |
|-------|-------|
| Tipo output | Reporte de análisis de demanda + forecast por SKU |
| Uso principal | Entregable a cliente B2B industrial (Marluvas, Tecmater) |
| Agente ensamblador | SKILL_DEMAND_FORECASTER v2.0 (Swarm 7 agentes: 0A→A→B→C→D→E→F) |
| Playbook de ejecución | PLB_DEMAND_FORECASTING |

---

## requires

```yaml
requires:
  - ENT_DIST_FORECAST_SIGNALS     # señales de negocio LATAM B2B
  - ENT_DIST_SAP_SCHEMAS          # normalización de exports SAP
  - SCH_FORECAST_OUTPUTS          # spec de outputs xlsx/pptx/docx
  - dataset_historico_cliente      # CSV/Excel SAP o genérico — externo, no en KB
  - context_params_cliente         # lead time, SKUs activos, eventos — externo, provisto por CEO
```

## policies

```yaml
policies:
  - POL_DETERMINISMO               # sin datos inventados — dato faltante = [DATO_FALTANTE]
  - POL_VISIBILIDAD                # reporte cliente puede ser PUBLIC/PARTNER_B2B según decisión CEO
```

## inherits

```yaml
inherits: null
```

---

## Secciones del output ensamblado

### Sección 1 — DATA_QUALITY_REPORT (Agent_A)

```
cobertura_meses: [número]
veredicto: APTO_MODELAR | APTO_CON_RESERVAS | INSUFICIENTE
gaps_detectados: [{período, descripción}]
stockouts_detectados: [{sku, período, demanda_real, demanda_ajustada_sugerida}]
outliers: [{sku, fecha, valor, acción: incluir|excluir}]
advertencias: [lista libre]
```

### Sección 2 — SKU_FORECAST (Agent_B) — una entrada por SKU

```
sku_id: [string]
sku_descripcion: [string]
modelo_seleccionado: [nombre + justificación 1 línea]
mape_backtest: [%]
mae_backtest: [unidades]
forecast_unidades: [{mes, valor}]
intervalo_confianza_80: [{mes, lower, upper}]
alerta: ninguna | demanda_intermitente | datos_insuficientes
```

### Sección 3 — CONTEXT_ADJUSTMENTS (Agent_C) — una entrada por señal activa

```
señal_id: [S01..S07 de ENT_DIST_FORECAST_SIGNALS o nueva]
señal_descripcion: [string]
skus_afectados: [lista]
dirección: [+X% | -X% | adelanto_pedido]
confianza: ALTA | MEDIA | BAJA
fuente: [dato objetivo | estimación CEO | supuesto explícito]
forecast_ajustado: [{sku, mes, valor_original, valor_ajustado}]
```

### Sección 4 — ACCURACY_REPORT (Agent_D)

```
escenario: A (con FP export) | B (Seasonal Naive como proxy)
mape_modelo: [% ponderado por volumen]
mape_benchmark: [%]
mejora_relativa: [%]
ganancia_unidades_mes: [unidades]
skus_ganamos: [{sku, delta_mape}]
skus_perdemos: [{sku, delta_mape, causa_probable}]
valor_contexto: [texto — cuánto redujo el error Agent_C en unidades]
```

### Sección 5 — EXECUTIVE_SUMMARY (Agent_E)

```
puntos_clave: [máx 3 bullets]
tabla_forecast_final: [{sku × mes → unidades ajustadas}]
reorder_points: [{sku, rop_unidades, justificación}]
alertas_críticas: [{nivel: 🔴|🟡, sku, descripción, acción}]
dato_faltante_p1: [qué dato más mejoraría el forecast]
frecuencia_actualizacion: mensual | trimestral | event-driven
sku_atencion_inmediata: [{sku, razón, acción recomendada}]
```

---

## Reglas de ensamblaje

1. Output sin stamp VIGENTE = DRAFT. Declararlo explícitamente en el reporte entregado al cliente
2. Secciones 1 y 2 son obligatorias. Secciones 3-5 requieren context_params_cliente completos
3. Si dataset < 6 meses → emitir solo Sección 1 con veredicto INSUFICIENTE y no continuar
4. Cada `[DATO_FALTANTE]` debe describir qué es y qué desbloquea su presencia
5. Formato de unidades siempre explícito en el reporte (pares / cajas / unidades)
6. Separar siempre en el entregable: forecast estadístico puro vs forecast ajustado final

---

## Ciclo de vida

Estado actual: DRAFT
Criterio para promover a ACTIVO: ejecutado con éxito en ≥ 2 clientes reales con datos históricos reales y validación CEO del output.

---

Changelog:
- v1.0 (2026-04-14): Creación. Estructura extraída de Swarm Demo Marluvas. Requiere validación con cliente real antes de promover a ACTIVO.
