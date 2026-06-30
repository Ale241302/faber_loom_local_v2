---
id: SPEC_SPACELOOM_SL5
version: 1.0
status: DIFERIDO
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: DIFERIDO — 2026-06-30 — correo multi-cuenta read-first
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL5_v1 — Correo (diferido)

## Objetivo

Conectar una o varias cuentas de correo (OAuth/IMAP) en modo read-first, generar drafts desde emails entrantes y permitir envío solo tras aprobación HITL.

## Estado

**DIFERIDO** en Etapa 1.

## Razón

- El correo es lo único recortable sin romper el núcleo del telar single-user.
- Requiere credenciales IMAP de Kimi Work rotadas y un connector multi-cuenta robusto.
- Para el dogfood interno actual se puede copiar/pegar contenido a mano.
- El riesgo P0 de injection por contenido de email obliga a tests específicos antes de liberar.

## Decisiones pendientes

| # | Decisión | Quién |
|---|---|---|
| 1 | ¿SL5 entra en Etapa 1 o se difiere a Etapa 2? | CEO |
| 2 | Rotar credenciales IMAP de Kimi Work | CEO/IT |
| 3 | ¿Gmail OAuth + IMAP/SMTP custom, o solo IMAP/SMTP directo? | CEO/Arquitecto |

## Flag explícito

`email_connector_enabled=false` hasta que SL5 se reactive.

## Documento de referencia

- `SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md`

## Changelog

- v1.0 (2026-06-30): Especificación diferida. Registro del spike en `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md`.
