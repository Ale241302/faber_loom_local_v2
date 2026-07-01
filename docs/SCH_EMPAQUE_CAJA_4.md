# SCH_EMPAQUE_CAJA_4 — v1.0 ACTIVO (inherits: SCH_EMPAQUE_BASE)
id: SCH_EMPAQUE_CAJA_4
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

## Caras: Frontal, Lateral izq, Lateral der, Posterior

| Cara | Slots |
|------|-------|
| Frontal | [BASE.Logo] + [entity.A2] + [loc.B1 claim] + [loc.B2 subhead] + [entity.B4 sello si != N/A] + [BASE.Sticker] |
| Lateral izq | [loc.C3 specs] + [entity.C2 íconos] + [BASE.Logo] |
| Lateral der | [pendiente definir por producto] |
| Posterior | [loc.B3 tagline] + [BASE.Footer] + [BASE.Línea origen] |

## Colores
entity.E1-E5 por cara + entity.E6-E7 slogan cromático

## Sticker
Continuo frente-lateral-back (ref → SCH_STICKER_CAJA)

requires:
  - SCH_EMPAQUE_BASE (herencia completa)
  - Layout específico: 4 pares por caja
policies:
  - hereda de SCH_EMPAQUE_BASE
inherits: SCH_EMPAQUE_BASE
---

## Golden Example
> Status: [PENDIENTE — requiere ensamblaje real]
> Candidato: Goliath USA — hereda SCH_EMPAQUE_BASE + layout 4 pares
