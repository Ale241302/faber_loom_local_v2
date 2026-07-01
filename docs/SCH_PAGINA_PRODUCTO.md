# SCH_PAGINA_PRODUCTO — v1.0 ACTIVO
id: SCH_PAGINA_PRODUCTO
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [SHARED]

## Estructura
- Headline → loc.B1
- Body → derivado de A9 contexto + C1 tecnologías
- CTA
- Galería
- Size Guide → ref ENT_OPS_TALLAS
- Specs → loc.C3, entity.C4

## Colores
entity.E1-E5

requires:
  - ENT_PROD_{PROD} (specs + contexto)
  - LOC_{PROD}_{LANG} (copy localizado)
  - ENT_OPS_TALLAS (size guide)
  - ENT_MERCADO_{M} (contexto mercado)
policies:
  - POL_STAMP
inherits: —
---

## Golden Example
> Status: [PENDIENTE — requiere ensamblaje real]
> Candidato: Goliath EN · USA (LOC_GOL_EN.H5 + ENT_PROD_GOL + ENT_OPS_TALLAS)
