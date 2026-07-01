# LOTE_SM_SPRINT20 — Modelo Proformas + ArtifactPolicy Backend
id: LOTE_SM_SPRINT20
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
status: DONE — ejecutado AG-02
version: 1.6
sprint: 20
depends_on: LOTE_SM_SPRINT19

---

## Objetivo

Cambio de paradigma: expediente como contenedor de Proformas (ART-02). Multi-proforma con modos independientes (Broker/Trader). ArtifactPolicy engine backend-driven. C1 flexible.

## Fases ejecutadas

- **Fase 0 — Modelo de datos**: FK proforma nullable en EPL, FK parent_proforma en ArtifactInstance, ART-05 multi-proforma via payload, validación mode en ART-02 payload
- **Fase 1 — ArtifactPolicy engine**: ARTIFACT_POLICY constante + resolve_artifact_policy() servicio. Bundle retorna artifact_policy calculada (required/optional/gate_for_advance)
- **Fase 2 — C1 flexible + C5**: handle_c1 actualizado (mínimo client_id + brand_id), validate_c5_gate actualizado

## Sprint 20B (Frontend policy-driven)

Ejecutado como extensión. Incluye:
- AddArtifactModal (selección centralizada reemplaza dropdown inline)
- Admin overrides (eliminar cualquier artefacto incluso required)
- ProformaSection (badge modo, operated_by)
- ArtifactSection genérico por fase
- Legacy fallback para expedientes pre-S20
- Gates: artefactos gate_for_advance, líneas huérfanas, modos definidos

---

Stamp: DONE — S20 + S20B ejecutados y desplegados en producción
