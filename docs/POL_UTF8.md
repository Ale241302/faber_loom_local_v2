# POL_UTF8 — Encoding Obligatorio
id: POL_UTF8
version: 1.0
status: VIGENTE
stamp: VIGENTE — 2026-03-01
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]

Todo documento, entity, schema y output es UTF-8 puro. Sin excepciones.
Caracteres corruptos (mojibake) = error crítico → corregir antes de usar.

---

## Enforcement
- **Detección:** Archivo con encoding no-UTF8 detectado
- **Acción:** Convertir a UTF-8, notificar
- **Severidad:** SOFT — corrección automática posible

---
Stamp: BOOTSTRAP VIGENTE 2026-03-01
Vencimiento: 2026-05-30
Estado: VIGENTE
Aprobador final: CEO
