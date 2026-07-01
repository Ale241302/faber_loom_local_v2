# SCH_LISTING_AMAZON — v1.0 ACTIVO
id: SCH_LISTING_AMAZON
version: 1.0
status: ACTIVO
stamp: ACTIVO — 2026-03-18
visibility: [INTERNAL]
domain: Producto (IDX_PRODUCTO)
aplica_a: [MWT]

## Estructura
- slot: [G1 título]
- slot: [G2 bullet 1 hook]
- slot: [G3 bullet 2 problema+solución]
- slot: [G4 bullet 3 evidencia]
- slot: [G5 bullet 4 lifestyle]
- slot: [G6 bullet 5 garantía+TtF]
- slot: [G7 search terms backend]
- slot: [G8 comparación]

## Policies
POL_ROGERS (si PORON en claim), POL_STAMP

requires:
  - LOC_{PROD}_{LANG}.G1-G8
  - ENT_PROD_{PROD}.C1 (specs técnicos)
  - ENT_MERCADO_{M} (contexto mercado)
policies:
  - POL_ROGERS (si PORON en claim)
  - POL_STAMP
  - POL_CLAIMS_SCANNER
inherits: —
---

## Golden Example — Goliath EN · USA

> Ensamblado con: LOC_GOL_EN.G1-G8 + ENT_PROD_GOL.C1 + ENT_MERCADO_USA
> Validado por: [PENDIENTE — CEO debe aprobar]
> Fecha: 2026-03-14
> Policies aplicadas: POL_ROGERS (PORON en G4 — verificado contra guía Rogers), POL_STAMP

**G1 — Título:**
"...Work Boot Insoles for Men 225+ lbs — Arch Support..."

**G2 — Bullet 1 (Hook):**
Peso y heavy duty (225+ lbs)

**G3 — Bullet 2 (Problema + Solución):**
Standing all day — solución biomecánica

**G4 — Bullet 3 (Evidencia):**
PORON XRD, LeapCore — datos técnicos
Specs inyectados desde ENT_PROD_GOL.C1: LeapCore + Arch System + PORON XRD + ThinBoom (antepié) + NanoSpread

**G5 — Bullet 4 (Lifestyle):**
Warehouse, construction, factory

**G6 — Bullet 5 (Garantía + TtF):**
Trim to Fit + confianza

**G7 — Search Terms Backend:**
[PENDIENTE — NO INVENTAR]

**G8 — Comparación:**
vs "Factory Boot Insole"

**Contexto mercado (ENT_MERCADO_USA):**
Idioma: EN · Moneda: USD · Unidades: imperial · Canal: Amazon FBA · Origen: "Engineered in the Costa Rica MedTech Hub"

---
Changelog:
- v1.0: schema original.
- v1.1 (2026-03-14): +Golden Example Goliath EN USA (Ola L).
