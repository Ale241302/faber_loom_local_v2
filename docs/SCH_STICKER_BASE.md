# SCH_STICKER_BASE — v1.1 ACTIVO
id: SCH_STICKER_BASE
version: 1.1
status: ACTIVO
stamp: ACTIVO — 2026-04-03
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

requires:
  - ENT_PROD_{PROD}.E13-E16 (colores sticker)
  - ENT_PROD_{PROD}.F4 (arch profile)
  - ENT_OPS_TALLAS (datos talla TRIM + EXACT FIT)
  - LOC_TALLAS_{LANG} (labels según mercado)
  - ENT_MERCADO_{M} (bloque regulatorio)
  - ENT_PROD_COLORES (colores plantilla PU + textil por modelo — Color Spec)
  - ENT_PROD_COMPARATIVA (rankings, ejes bipolares/unipolares — Comparison Table)
policies:
  - POL_NUNCA_TRADUCIR
  - POL_ANTI_CONFUSION
  - POL_ORIGEN_LOCAL
inherits: —

## Elementos comunes (sticker)
- slot: [Header → entity.E15 + "ARCH PROFILE: " + entity.F4]
- slot: [TRIM column → entity.E13 + datos talla desde ENT_OPS_TALLAS]
- slot: [EXACT FIT column → entity.E14 + datos talla desde ENT_OPS_TALLAS]
- slot: [Barcode → SVG por SKU]
- slot: [Bloque regulatorio → ENT_MERCADO_{M} (origen, unidades, importador)]

## Ficha de producto (integrada en sticker v7.8)
- slot: [Sensation Profile → ejes bipolares (thickness/firmness/rigidity) con dot position por modelo]
- slot: [Performance → ejes unipolares (impact/energy/moisture) con fill bar + % valor]
- slot: [Comparison Table → grid 9 col: left label + 7 modelos + right label. Datos desde ENT_PROD_COMPARATIVA + PROD_SPECS{}]
- slot: [Color Spec → 2 capas (PU BASE + TEXTIL) por lado L/R. Datos desde ENT_PROD_COLORES. Pantone ref Delta-E CIE Lab]

## CSS harmonización
- Custom properties --fc-main y --fc-accent por producto (derivados de entity.E1/E2)
- color-mix(in srgb, ...) para tinted backgrounds, borders, shadows
- Outline en todos los elementos de color para visibilidad de blancos (#FFFFFF)

## i18n
- 4 mercados: USA (EN), CR (ES), BRA (PT), WORLD (EN)
- ~30 keys por mercado incluyendo labels de ficha, ejes, performance, color spec
- Labels de talla: ref → LOC_TALLAS_{LANG}

## Labels
Desde LOC_TALLAS_{LANG} según mercado destino

---

## Golden Example
> Status: ACTIVE — ART-19 (rw_sticker_v7_8.html)
> Implementación: Goliath USA (ENT_PROD_GOL + ENT_OPS_TALLAS + LOC_TALLAS_EN + ENT_PROD_COLORES + ENT_PROD_COMPARATIVA)

Changelog:
- v1.0: Creación inicial. Slots básicos sticker. 2026-03-18.
- v1.1: +requires ENT_PROD_COLORES y ENT_PROD_COMPARATIVA. +slots ficha de producto (sensation, performance, comparison, color spec). +CSS harmonización. +i18n 4 mercados. Golden example → ART-19 ACTIVE. 2026-04-03.
