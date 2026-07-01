# ENT_DIST_FORECAST_SIGNALS — Señales de Negocio para Demand Forecasting B2B
id: ENT_DIST_FORECAST_SIGNALS
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Distribucion (IDX_DISTRIBUCION)
aplica_a: [MWT]

---

## A. Propósito

Catálogo de señales de negocio que modifican la demanda estadística base en análisis de forecast B2B industrial LATAM. Estas señales son el diferencial vs Forecast Pro: estadística pura no puede incorporarlas.

Referenciado por: PLB_DEMAND_FORECASTING (Agent_C Context Injector), SKILL_DEMAND_FORECASTER.

---

## B. Contexto del proveedor: Marluvas

| Parámetro | Valor | Fuente |
|-----------|-------|--------|
| Origen fabricación | Brasil | Dato objetivo |
| Lead time estándar | 60-90 días | Dato objetivo documentado |
| Moneda de compra | USD (negociado) o BRL | Dato objetivo |
| Categoría producto | Calzado seguridad industrial (EPP) | Dato objetivo |
| Mercados activos | México, Guatemala, Costa Rica, Colombia | Dato objetivo |
| Normativa principal | NOM-017-STPS (MX), regulaciones EPP por país | Dato objetivo |

---

## C. Catálogo de señales — 5 validadas en demo

### S01 — Renovación de contrato cliente

| Campo | Valor |
|-------|-------|
| Descripción | Cliente renueva contrato de obra o servicio — implica reposición masiva EPP |
| SKUs típicamente afectados | Botín punta acero, zapato ejecutivo antiestático |
| Ajuste sugerido | +15% a +25% en mes de inicio contrato |
| Confianza típica | ALTA si contrato confirmado / MEDIA si en negociación |
| Ventana de efecto | 1-2 meses desde inicio contrato |
| Fuente requerida | Dato objetivo (contrato firmado) o estimación CEO |

### S02 — Auditoría de seguridad programada

| Campo | Valor |
|-------|-------|
| Descripción | Cliente recibe auditoría de seguridad laboral → compra preventiva EPP para cumplir |
| SKUs típicamente afectados | Bota industrial caña alta, botín punta acero |
| Ajuste sugerido | +40% a +60% en mes previo a auditoría |
| Confianza típica | MEDIA (estimación basada en histórico) |
| Ventana de efecto | 1 mes previo a auditoría |
| Fuente requerida | Fecha de auditoría confirmada o estimada |

### S03 — Cambio normativo EPP (NOM-017-STPS o equivalente)

| Campo | Valor |
|-------|-------|
| Descripción | Nueva normativa obliga reposición o actualización de calzado en toda la plantilla |
| SKUs típicamente afectados | Todos los SKUs activos del cliente |
| Ajuste sugerido | +10% a +20% en mes de entrada en vigor |
| Confianza típica | MEDIA (impacto estimado — adopción varía por empresa) |
| Ventana de efecto | 1-3 meses desde entrada en vigor |
| Normativa conocida | NOM-017-STPS-2025 (México), vigencia prevista 2025 |
| Fuente requerida | Publicación oficial o comunicado gremial |

### S04 — Lead time largo (reorder point adelantado)

| Campo | Valor |
|-------|-------|
| Descripción | Lead time ≥ 75 días exige emitir pedido antes de lo que indicaría la demanda mensual |
| SKUs típicamente afectados | Todos |
| Ajuste | No es ajuste de demanda — es ajuste de timing de pedido |
| Cálculo | `ROP = demanda_diaria_prom × lead_time_días + stock_seguridad` |
| Confianza típica | ALTA si lead time documentado |
| Fuente requerida | Lead time confirmado con proveedor (Marluvas: 60-90 días) |

### S05 — Depreciación BRL/USD

| Campo | Valor |
|-------|-------|
| Descripción | Depreciación BRL reduce costo de importación → posible ajuste de precio → efecto en demanda |
| SKUs típicamente afectados | Todos |
| Ajuste sugerido | +5% a +15% en mes de impacto si se traslada reducción al cliente |
| Confianza típica | BAJA (depende de política comercial CEO) |
| Ventana de efecto | 1-2 meses después del movimiento cambiario |
| Fuente requerida | Tipo de cambio BRL/USD + decisión CEO de traslado |

---

## D. Señales adicionales — slots para nuevos clientes

Agregar una fila por señal nueva identificada en análisis de cuenta:

| ID | Señal | SKUs afectados | Ajuste típico | Confianza | Fuente |
|----|-------|----------------|--------------|-----------|--------|
| S06 | [completar] | — | — | — | — |
| S07 | [completar] | — | — | — | — |

---

## E. Regla de aplicación

1. Cada ajuste declara fuente y confianza explícita en el reporte final
2. Ajustes de confianza BAJA → incluir en forecast ajustado con nota, NO omitir
3. Señales contradictorias (ej: S01 + S05 en el mismo mes) → sumar ajustes, declarar ambos
4. Si señal no tiene fecha confirmada → no aplicar. Documentar como `[SEÑAL_PENDIENTE_CONFIRMAR]`

---

Changelog:
- v1.0 (2026-04-14): Creación. 5 señales extraídas de Swarm Demo Marluvas — Distribuidor Industrial del Centro S.A. Validadas en sesión CEO.
