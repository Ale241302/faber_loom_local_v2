# ENT_COMERCIAL_FINANZAS [CEO-ONLY]
id: ENT_COMERCIAL_FINANZAS
version: 0.1
status: DRAFT
visibility: [CEO-ONLY]
domain: Comercial (IDX_COMERCIAL)
aplica_a: [MWT]

- Fórmula BE-ACoS: (PV - CostoTotal - FBA) / PV
- Fórmula Cash: Mes1 = NR x 9/30. Mes2+ = NR[N] x 9/30 + NR[N-1] x 21/30
- Safety stock financiero: velocidad diaria x lead time x 1.35

---
Changelog:
- v0.1 (2026-03-14): version: field agregado (normalización Ola A).
- v0.1 (2026-03-14): visibility: CEO-ONLY + status: DRAFT agregados (Ola B).
