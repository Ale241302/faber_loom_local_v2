# ENT_OPS_TALLAS
id: ENT_OPS_TALLAS
version: 0.2
status: DRAFT
visibility: [INTERNAL]
domain: Ops (IDX_OPS)
aplica_a: [MWT]

- SSOT: rw_sticker_v7_8.html
- 15 sistemas x 6 tallas x 4 mercados
- Curva demanda: S1:5%, S2:10%, S3:20%, S4:25%, S5:30%, S6:10%
- Config por mercado: ref → ENT_MERCADO_{M}
- Regla: Costa Rica = EU (35-47)
- Labels que nunca se traducen: US Men, US Women, Big Kid, UK Men, UK Women, AU Men, AU Women
- Nomenclatura: RW-[LÍNEA]-[ARCO]-[TALLA]. MED = MEDIO no médico.
- Total SKUs: 66 (GOL 6 + ORB 6 + VEL 6 + LEO 18 + BIS 18 + MAN 6 + ORC 6)

## Sticker v7.8 — Funcionalidades integradas

El artefacto rw_sticker_v7_8.html incluye:
- Sticker de talla con barcodes SVG por SKU
- Ficha de producto por modelo: Sensation Profile (ejes bipolares), Performance (ejes unipolares), Comparison Table (7 modelos), Color Spec (colores plantilla 2 capas)
- i18n completo: 4 mercados (USA=EN, CR=ES, BRA=PT, WORLD=EN)
- CSS harmonizado por producto via custom properties (--fc-main, --fc-accent)
- Ref colores plantilla → ENT_PROD_COLORES

---
Changelog:
- v0.1 (2026-03-14): version: field agregado (normalización Ola A).
- v0.1 (2026-03-14): visibility: INTERNAL + status: DRAFT agregados (Ola B).
- v0.2 (2026-04-03): SSOT actualizado rw_sticker_v7.html → rw_sticker_v7_8.html. Total SKUs 54 → 66 (incluye MAN 6 + ORC 6). Documentada funcionalidad sticker v7.8 (ficha producto, i18n, color spec, comparison table).
