# POL_CONSENTIMIENTO — Consentimiento para Captura de Datos Biométricos
id: POL_CONSENTIMIENTO
version: 0.1
status: DRAFT
stamp: DRAFT — pendiente aprobación CEO (activación Fase 2 ISO)
visibility: [INTERNAL]
domain: Compliance (IDX_COMPLIANCE)
aplica_a: [SHARED]


---

## Propósito

Definir las reglas de consentimiento explícito del usuario antes de captura de datos biomecánicos con el pressure scanner MWT.

## Alcance

Aplica a todo escaneo de pie que genere datos clasificados como N4 [BIOMETRIC] (ref → POL_DATA_CLASSIFICATION.C5).

## Marco normativo

- ISO 27001 A.5.34 — Privacy and protection of personal information
- LGPD Brasil Art. 5 y 11 (datos sensibles biométricos)
- BIPA Illinois (si aplica canal USA)
- CCPA California (si aplica canal USA)

## Contenido pendiente

[PENDIENTE — NO INVENTAR]

Los siguientes elementos deben definirse cuando se active Fase 2 ISO:

- Formato y contenido del consent receipt
- Mecanismo de captura (UI, firma digital, checkbox)
- Almacenamiento del consent receipt (separado del escaneo — ref → POL_DATA_CLASSIFICATION)
- Inmutabilidad del consent receipt (ref → POL_INMUTABILIDAD)
- Procedimiento de revocación (nuevo registro, no edición)
- Retención del consent receipt post-anonimización del escaneo
- Reglas por jurisdicción (USA, CR, BR)

## Trigger de activación

Este policy se activa cuando el scanner entre en producción con captura de datos de usuarios finales. Mientras el scanner esté en fase de desarrollo/testing interno, no es bloqueante.

## Refs entrantes

- POL_DATA_CLASSIFICATION.C5 (N4 biometric)
- ENT_COMP_ISO_ROADMAP F2-01
- REPORTE_SESION_ISO_20260301

---

Changelog:
- v0.1 (2026-03-13): Stub creado con scope y marco normativo. Contenido [PENDIENTE].
- v0.1.1 (2026-04-18): KB_AUDIT B1b — agregado stamp DRAFT en header + foot block (header_complete fix). Contenido semántico sin cambios.

## Enforcement
- **Detección:** Dato de tercero usado sin consentimiento documentado
- **Acción:** Escalar a Compliance, bloquear publicación
- **Severidad:** HARD — riesgo legal

---
Stamp: DRAFT 2026-03-13 — pendiente aprobación CEO
Vencimiento: N/A (DRAFT — stamp-less hasta activación Fase 2 ISO)
Estado: DRAFT
Aprobador final: CEO (pendiente)
