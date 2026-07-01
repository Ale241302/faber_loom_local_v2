# SCH_EMPAQUE_BASE — v1.0 ACTIVO
id: SCH_EMPAQUE_BASE
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

requires:
  - ENT_PROD_{PROD}.A2 (nombre)
  - ENT_PROD_{PROD}.E13-E16 (sticker tallas+barcode)
  - ENT_MARCA_IP (footer legal + trademarks)
  - ENT_COMP_CONTENT_RULES.B (condicional — si PORON en producto)
  - ENT_MERCADO_{M} (línea origen según destino)
policies:
  - POL_ROGERS
  - POL_STAMP
  - POL_ANTI_CONFUSION
  - POL_ORIGEN_LOCAL
inherits: —

## Elementos comunes a todo empaque
- slot: [Logo]
- slot: [Nombre → entity.A2]
- slot: [Sticker tallas+barcode → entity.E13-E16]
- slot: [Footer legal → ensamblado desde ENT_MARCA_IP + entity trademarks + ENT_COMP_CONTENT_RULES.B(condicional)]
- slot: [Línea origen → ENT_MERCADO_{M} según destino]

---

## Golden Example
> Status: [PENDIENTE — requiere ensamblaje real]
> Candidato: Goliath USA (ENT_PROD_GOL.A2/E13-E16 + ENT_MARCA_IP + ENT_MERCADO_USA)
