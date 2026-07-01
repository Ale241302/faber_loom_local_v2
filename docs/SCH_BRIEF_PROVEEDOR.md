# SCH_BRIEF_PROVEEDOR — v1.0 ACTIVO
id: SCH_BRIEF_PROVEEDOR
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

## Estructura
- Paleta completa (E1-E7)
- Specs empaque (loc.C3, entity.C2)
- Copy aprobado (loc.B1-B3)
- Reglas visuales (ref ENT_COMP_CONTENT_RULES.C)
- Footer legal (entity.E10 ensamblado)
- Línea origen (ref ENT_MERCADO_{M})

requires:
  - ENT_PROD_{PROD} (paleta + specs)
  - LOC_{PROD}_{LANG} (copy aprobado)
  - ENT_COMP_CONTENT_RULES.C (reglas visuales)
  - ENT_MARCA_IP (footer legal)
  - ENT_MERCADO_{M} (línea origen)
policies:
  - POL_VISIBILIDAD
inherits: —
## Excludes
[CEO-ONLY], [INTERNAL]

---

## Golden Example
> Status: [PENDIENTE — requiere ensamblaje real]
> Candidato: Goliath (ENT_PROD_GOL + LOC_GOL_EN + ENT_COMP_CONTENT_RULES.C + ENT_MARCA_IP)
