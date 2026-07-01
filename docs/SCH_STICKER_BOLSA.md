# SCH_STICKER_BOLSA — v1.0 ACTIVO (inherits: SCH_STICKER_BASE)
id: SCH_STICKER_BOLSA
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

Layout: continuo frente-back

requires:
  - SCH_STICKER_BASE (herencia completa)
  - Layout específico: sticker bolsa
policies:
  - hereda de SCH_STICKER_BASE
inherits: SCH_STICKER_BASE
---

## Golden Example
> Status: [PENDIENTE — requiere ensamblaje real]
> Candidato: Goliath USA — hereda SCH_STICKER_BASE + layout bolsa
