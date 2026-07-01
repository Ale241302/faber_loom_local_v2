# SCH_LLMS_TXT — v1.0 ACTIVO
id: SCH_LLMS_TXT
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [SHARED]

## Estructura
- Overview marca
- Tecnologías propietarias (desde ENT_TECH)
- Tecnología licenciada (desde ENT_COMP_CONTENT_RULES.B)
- Product lines (desde cada entity producto + loc EN)
- Sizing (desde ENT_OPS_TALLAS)
- Origin (desde ENT_MARCA_ORIGEN)
- About (desde ENT_MARCA_EEAT)

requires:
  - ENT_PROD_* (todos los productos)
  - ENT_TECH (tecnologías propietarias)
  - ENT_COMP_CONTENT_RULES.B (tecnología licenciada)
  - ENT_MARCA_* (origen, EEAT)
  - ENT_OPS_TALLAS (sizing)
policies:
  - POL_NUNCA_TRADUCIR
inherits: —
---

## Golden Example
> Status: [PENDIENTE — requiere ensamblaje real]
> Candidato: línea completa EN (todos ENT_PROD_* + ENT_TECH + ENT_MARCA_*)
