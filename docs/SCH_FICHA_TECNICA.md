# SCH_FICHA_TECNICA — v1.0 ACTIVO
id: SCH_FICHA_TECNICA
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

## Estructura
- Nombre + subtítulo (A2, A3)
- Tecnologías detalle (C1 + ref ENT_TECH)
- Rankings (C4)
- Sizing referencia

requires:
  - ENT_PROD_{PROD} (specs técnicos)
  - ENT_TECH (tecnologías)
  - ENT_OPS_TALLAS (sizing referencia)
policies:
  - POL_STAMP
inherits: —
---

## Golden Example
> Status: [PENDIENTE — requiere ensamblaje real]
> Candidato: Goliath (ENT_PROD_GOL.C1-C4 + ENT_TECH + ENT_OPS_TALLAS)
