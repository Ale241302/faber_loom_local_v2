# SCH_EMPAQUE_BOLSA_2 — v1.0 ACTIVO (inherits: SCH_EMPAQUE_BASE)
id: SCH_EMPAQUE_BOLSA_2
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

## Caras: Frontal, Posterior

| Cara | Slots |
|------|-------|
| Frontal | [BASE.Logo] + [entity.A2] + [loc.B1] + [loc.B2] + [BASE.Sticker] |
| Posterior | [loc.C3] + [entity.C2] + [loc.B3] + [BASE.Footer] + [BASE.Línea origen] |

## Colores
entity.E1-E5 por cara + entity.E6-E7

## Sticker
Continuo frente-back (ref → SCH_STICKER_BOLSA)

requires:
  - SCH_EMPAQUE_BASE (herencia completa)
  - Layout específico: 2 pares por bolsa
policies:
  - hereda de SCH_EMPAQUE_BASE
inherits: SCH_EMPAQUE_BASE
---

## Golden Example
> Status: [PENDIENTE — requiere ensamblaje real]
> Candidato: Goliath USA — hereda SCH_EMPAQUE_BASE + layout 2 pares
