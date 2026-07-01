# SCH_APLUS_CONTENT — v1.0 ACTIVO
id: SCH_APLUS_CONTENT
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

## 5 módulos
1. Hero visual (claim + subhead)
2. Explosión producto/tecnología
3. Tabla comparativa
4. Casos uso/lifestyle
5. Brand Story → ref ENT_MARCA_EEAT

requires:
  - ENT_PROD_{PROD} (specs + contexto)
  - LOC_{PROD}_{LANG} (copy localizado)
  - ENT_MARCA_EEAT (Brand Story módulo 5)
  - ENT_MERCADO_{M} (contexto mercado)
policies:
  - POL_ROGERS (si PORON en claim)
  - POL_STAMP
inherits: —
---

## Golden Example
> Status: [PENDIENTE — requiere ensamblaje real]
> Candidato: Goliath EN · USA (LOC_GOL_EN completo + ENT_MARCA_EEAT disponible)
