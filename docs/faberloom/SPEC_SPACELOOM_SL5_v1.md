---
id: SPEC_SPACELOOM_SL5
version: 1.1
status: ACTIVE_SPIKE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: ACTIVE_SPIKE — 2026-06-30 — correo usable en servidor, keyring/OAuth reservados para desktop
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL5_v1.1 — Correo (spike usable, canonización parcial)

## Objetivo

Conectar una cuenta de correo IMAP por workspace en modo read-first, generar drafts desde emails entrantes y permitir envío SMTP solo tras aprobación HITL.

## Estado

**ACTIVE_SPIKE**. La funcionalidad base está implementada y desplegada en el VPS, protegida por feature flag (`FABERLOOM_ENABLE_EMAIL_CONNECTOR`).

## Alcance de la Fase 1 (spike usable)

- Feature flag `FABERLOOM_ENABLE_EMAIL_CONNECTOR` (default `false`).
- Configuración IMAP por workspace con password cifrado mediante `FABERLOOM_MASTER_KEY`.
- Configuración SMTP por `(workspace, user)` con password cifrado.
- Firma / footer de correo configurable por workspace.
- Envío HITL: draft aprobado + `confirmation_token` + `idempotency_key`.
- Retry/timeout en `mail_outbox` para envíos fallidos.
- Test P0 de prompt injection desde email.

## Límites explícitos del spike

| Funcionalidad | Estado | Nota |
|---|---|---|
| Multi-cuenta IMAP por workspace | 🟡 Una cuenta default | Multi-cuenta completa queda para Fase 2. |
| OAuth | ❌ No implementado | Requiere runtime desktop + browser. |
| Keyring del OS | ❌ No implementado | En servidor se usa almacén cifrado con master key. |
| Polling automático | ❌ No implementado | Sync manual; Fase 2 lo añade. |
| Enriquecimiento de KB | ❌ No implementado | Fase 2. |
| Adjuntos | ❌ No procesados | Se ignoran; Fase 2 añade parser sandboxeado. |
| HTML sanitizado | 🟡 Regex básico | Fase 2 usaría sanitizador real. |
| Borrar/mover/marcar emails | ❌ No implementado | Fase 2 con HITL. |

## Canonización completa

Para cumplir `SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md` al 100% se requiere:

1. Runtime desktop (SL4) con acceso a keyring OS y navegador para OAuth.
2. Migrar secretos IMAP/SMTP del almacén cifrado SQLite al keyring del OS.
3. Implementar OAuth read-only para Gmail/Microsoft 365.
4. En el VPS, mantener el conector deshabilitado por defecto o en modo relay seguro.

## Flag explícito

`FABERLOOM_ENABLE_EMAIL_CONNECTOR=false` por defecto. Activar solo en deploys donde se acepte la superficie de riesgo del correo.

## Documento de referencia

- `SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md`

## Changelog

- v1.0 (2026-06-30): Especificación diferida.
- v1.1 (2026-06-30): Fase 1 del spike usable cerrada en servidor; límites y ruta a canonización documentados.
