# LOTE_SM_SPRINT1 — Command Handlers + Tests
id: LOTE_SM_SPRINT1
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
status: DONE — CERRADO · 9/9 items · 0 pendientes
version: 1.0
sprint: 1
depends_on: LOTE_SM_SPRINT0

---

## Objetivo

Commands C1–C14 (happy path REGISTRO→CERRADO) + C15 (CostLine) + C16–C18 (cancelación/bloqueo) + C21 (pagos). 18 commands totales. Patrón: APIView por command, no ViewSet.

## Items ejecutados

| Item | Tarea | Estado |
|------|-------|--------|
| S1-01 | Models (Expediente, ArtifactInstance, CostLine, etc.) + migrations | ✅ Done |
| S1-02 | Commands C1-C5 (REGISTRO) | ✅ Done |
| S1-03 | Commands C6 (PRODUCCION) | ✅ Done |
| S1-04 | Commands C7-C10 (PREPARACION) | ✅ Done |
| S1-05 | Commands C11-C12 (DESPACHO/TRANSITO) | ✅ Done |
| S1-06 | Commands C13-C14 (DESTINO/CERRADO) | ✅ Done |
| S1-07 | C15 RegisterCost + C16-C18 Cancel/Block | ✅ Done |
| S1-08 | C21 RegisterPayment | ✅ Done |
| S1-09 | Tests (pytest unit + integration) | ✅ Done |

---

Stamp: DONE — CERRADO · 9/9 items · Confirmado auditoría 2026-03-12
