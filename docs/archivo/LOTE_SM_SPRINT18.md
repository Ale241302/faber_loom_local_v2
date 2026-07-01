# LOTE_SM_SPRINT18 — Motor de Tallas Genérico + Endpoints Backend
id: LOTE_SM_SPRINT18
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
status: DONE — ejecutado AG-02
version: 3.5
sprint: 18
depends_on: LOTE_SM_SPRINT17

---

## Objetivo

Motor dimensional de plataforma (subsistema tallas/dimensiones genérico), endpoints backend PATCH por estado, CRUD FactoryOrder, pagos, merge expedientes.

## Fases ejecutadas

- **Fase 0 — Motor Dimensional**: 5 modelos + tabla puente + data migration. FK nullable brand_sku en EPL. Fix resolve_client_price(). Campos nullable adelantados. Hook post_command_hooks en dispatcher.
- **Fase 1 — Endpoints Backend**: Serializers actualizados, 5 endpoints PATCH por estado, CRUD FactoryOrder, POST pagos + PaymentLine, POST merge expedientes.

## Items: 10 ejecutados (S18-01 a S18-10)

---

Stamp: DONE — Ejecutado y desplegado en producción
