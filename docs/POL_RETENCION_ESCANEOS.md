# POL_RETENCION_ESCANEOS — Retención y Eliminación de Datos de Escaneo
id: POL_RETENCION_ESCANEOS
version: 0.1
status: DRAFT
stamp: DRAFT — pendiente aprobación CEO (activación Fase 2 ISO)
visibility: [INTERNAL]
domain: Compliance (IDX_COMPLIANCE)
aplica_a: [SHARED]


---

## Propósito

Definir los períodos de retención, reglas de eliminación y procedimiento de anonimización para datos de escaneo biomecánico capturados por el pressure scanner MWT.

## Alcance

Aplica a todos los datos clasificados como N4 [BIOMETRIC] y N3 [SCAN-RAW] (ref → POL_DATA_CLASSIFICATION).

## Marco normativo

- ISO 27001 A.5.33 — Protection of records
- LGPD Brasil Art. 15-16 (terminación del tratamiento y eliminación)
- BIPA Illinois (si aplica canal USA)
- CCPA California (si aplica canal USA)

## Contenido pendiente

[PENDIENTE — NO INVENTAR]

Los siguientes elementos deben definirse cuando se active Fase 2 ISO:

- Período de retención por tipo de dato (raw scan, perfil procesado, consent receipt)
- Procedimiento de anonimización (desvincular perfil de persona)
- Eliminación obligatoria al terminar contrato con distribuidor (ref → POL_DATA_CLASSIFICATION)
- Eliminación por revocación de consentimiento (ref → POL_CONSENTIMIENTO)
- Evidencia de eliminación (log inmutable)
- Reglas de retención diferenciadas por jurisdicción (USA, CR, BR)
- DPA (Data Processing Agreement) como prerequisito de captura

## Trigger de activación

Este policy se activa junto con POL_CONSENTIMIENTO cuando el scanner entre en producción con datos de usuarios finales.

## Refs entrantes

- POL_DATA_CLASSIFICATION (eliminación por terminación de contrato, tabla de operaciones permitidas)
- ENT_COMP_ISO_ROADMAP F2-02
- REPORTE_SESION_ISO_20260301

---

Changelog:
- v0.1 (2026-03-13): Stub creado con scope y marco normativo. Contenido [PENDIENTE].
- v0.1.1 (2026-04-18): KB_AUDIT B1b — agregado stamp DRAFT en header + foot block (header_complete fix). Contenido semántico sin cambios.

## Enforcement
- **Detección:** Escaneo/análisis sin fecha de retención declarada
- **Acción:** Agregar fecha de retención, notificar
- **Severidad:** SOFT — compliance de datos

---
Stamp: DRAFT 2026-03-13 — pendiente aprobación CEO
Vencimiento: N/A (DRAFT — stamp-less hasta activación Fase 2 ISO)
Estado: DRAFT
Aprobador final: CEO (pendiente)
