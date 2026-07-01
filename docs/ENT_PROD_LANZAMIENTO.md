# ENT_PROD_LANZAMIENTO — Orden de Lanzamiento
id: ENT_PROD_LANZAMIENTO
version: 0.1
status: DRAFT
visibility: [PUBLIC]
ceo_only_sections: [T3.4, T5.3]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

## Secuencia
1. Goliath (Fase 1) — ACTIVO
2. Orbis (Fase 2) — Toggle apagado
3. Velox (Fase 3) — Toggle apagado
4. Leopard (Fase 4) — Toggle apagado
5. Bison (post-Goliath >1,000 reviews) — Aprobado, Fase TBD

## Regla anti-canibalización
BIS NO se lanza antes de GOL >1,000 reviews.
Ambos comparten PORON XRD — riesgo de split de demanda.

---

## Triggers de activación por fase

Principio: un toggle se activa cuando TODAS las condiciones se cumplen. No hay activación parcial.
Para datos actuales de KPIs → ref ENT_GOB_KPI.B3 (Marketplace: TACoS, reviews, BSR, conversion), ENT_GOB_KPI.B1 (Expedientes), ENT_GOB_KPI.F1 (pipeline datos). No duplicar datos aquí (POL_DETERMINISMO).
Ref decisión de secuencia → DEC-002 en ENT_GOB_DECISIONES.

### Fase 2: Orbis
| # | Condición | KPI | Umbral | Fuente |
|---|-----------|-----|--------|--------|
| T2.1 | GOL reviews suficientes | Review count | ≥ 75 orgánicas (4.3+ estrellas) | Amazon |
| T2.2 | GOL rating estable | Rating promedio | ≥ 4.3 estrellas (promedio 30 días) | Amazon |
| T2.3 | GOL rentable | TACoS | ≤ 22% con tendencia decreciente | Advertising Console |
| T2.4 | Supply chain estable | Lead time proforma→entrega | ≤ 90 días (ocean freight estándar) | ENT_OPS_STATE_MACHINE |
| T2.5 | Capacidad operativa | Expedientes/mes sin error | ≥ 3 expedientes/mes sin error crítico | Sistema |

### Fase 3: Velox
| # | Condición | KPI | Umbral | Fuente |
|---|-----------|-----|--------|--------|
| T3.1 | ORB lanzado y estable | ORB review count | ≥ 25 reviews orgánicas | Amazon |
| T3.2 | GOL mantiene posición | GOL BSR | Top [PENDIENTE] en categoría | Amazon |
| T3.3 | Sin canibalización GOL-ORB | GOL sessions post-ORB launch | ≥ 90% del baseline pre-lanzamiento | Amazon |
| T3.4 | Margen combinado | Margen GOL + ORB ponderado | ≥ 25% margen neto ponderado | ENT_COMERCIAL_PRICING |

### Fase 4: Leopard
| # | Condición | KPI | Umbral | Fuente |
|---|-----------|-----|--------|--------|
| T4.1 | VEL lanzado y estable | VEL review count | ≥ 50 reviews orgánicas | Amazon |
| T4.2 | Portafolio 3 productos sano | Canibalización cruzada | < [PENDIENTE]% overlap sessions | Amazon |
| T4.3 | Operaciones escaladas | Sistema plataforma funcional | Sprint [PENDIENTE] completado | ENT_GOB_PENDIENTES |

### Fase 5: Bison (one-way door — ref DEC-002)
| # | Condición | KPI | Umbral | Fuente |
|---|-----------|-----|--------|--------|
| T5.1 | GOL reviews masivos | Review count GOL | ≥ 1,000 | Amazon (ya documentado) |
| T5.2 | GOL domina categoría | BSR GOL | Top 200 subcategoría (4 semanas) | Amazon |
| T5.3 | Margen GOL financia BIS launch | Margen neto GOL | ≥ 30% margen neto | ENT_COMERCIAL_PRICING |
| T5.4 | Sin riesgo de split PORON | Share of PORON claims | GOL > [PENDIENTE]% | Internal analysis |

### Notas
- Todos los umbrales [PENDIENTE] requieren definición del CEO.
- Datos actuales → ref ENT_GOB_KPI (no se duplican aquí).
- Cuando el CEO defina umbrales, se actualiza version + stamp.

---

## LOCs requeridos por fase

| Fase | Producto | LOCs a completar | Status actual | Ensamblaje posible | Prerequisito |
|------|----------|------------------|---------------|--------------------|-------------|
| 1 (ACTIVO) | Goliath | LOC_GOL_EN, LOC_GOL_ES, LOC_GOL_PT | ✅ Completo (28/37/37 lín) | SCH_LISTING_AMAZON + SCH_FICHA_TECNICA | — |
| 2 | Orbis | LOC_ORB_EN (expandir), LOC_ORB_ES, LOC_ORB_PT | ⚠️ EN parcial (17 lín), ES/PT vacíos | SCH_FICHA_TECNICA (parcial). Insuficiente para SCH_LISTING_AMAZON — faltan G1-G9 completos | Triggers T2.1-T2.5 definidos y cumplidos |
| 3 | Velox | LOC_VEL_EN (expandir), LOC_VEL_ES, LOC_VEL_PT | ⚠️ EN parcial (17 lín), ES/PT vacíos | SCH_FICHA_TECNICA (parcial). Insuficiente para SCH_LISTING_AMAZON — faltan G1-G9 completos | Triggers T3.1-T3.4 definidos y cumplidos |
| 4 | Leopard | LOC_LEO_EN (expandir), LOC_LEO_ES, LOC_LEO_PT | ⚠️ EN parcial (17 lín), ES/PT vacíos | SCH_FICHA_TECNICA (parcial). Insuficiente para SCH_LISTING_AMAZON — faltan G1-G9 completos | Triggers T4.1-T4.3 definidos y cumplidos |
| 5 | Bison | LOC_BIS_EN, LOC_BIS_ES, LOC_BIS_PT | ❌ Todos vacíos (2 lín) | Ninguno | Triggers T5.1-T5.4 definidos y cumplidos |
| — | Marca | LOC_MARCA_EN, LOC_MARCA_ES, LOC_MARCA_PT | ❌ Todos vacíos (2 lín) | Ninguno | Transversal — cuando se defina identidad de marca |
| — | Tallas | LOC_TALLAS_EN, LOC_TALLAS_ES, LOC_TALLAS_PT | ⚠️ Parcial (4 lín) | Ninguno | Transversal — cuando se expanda tabla de tallas |

> Nota: "parcial — suficiente para ficha técnica" = tiene B1-B3 y C3 presentes, que es lo que necesita SCH_FICHA_TECNICA. "Insuficiente para listing" = faltan campos G1-G9 completos que SCH_LISTING_AMAZON requiere. Completar un LOC = todos los campos G1-G9, B1-B6, C3, H5 con datos reales o [PENDIENTE — keyword research] específico. Ref → DEPENDENCY_GRAPH para pre-flight check de ensamblaje.

---
Changelog:
- v0.1 (2026-03-14): version: field agregado (normalización Ola A).
- v0.1 (2026-03-14): visibility: ALL + status: DRAFT agregados (Ola B).
- v0.2 (2026-03-14): +triggers cuantificados por fase con ref cruzada a ENT_GOB_KPI (E-3).
