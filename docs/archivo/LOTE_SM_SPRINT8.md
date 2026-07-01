# LOTE_SM_SPRINT8 — Auth + Knowledge Container
id: LOTE_SM_SPRINT8
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
status: DONE — ejecutado y cerrado 2026-03-16
version: 4.0
sprint: 8
depends_on: LOTE_SM_SPRINT7

---

## Objetivo

Autenticación multi-tenant (JWT, roles, LegalEntity FK directa), Knowledge container (pgvector, mwt-knowledge con Nginx proxy), ingestion de KB a chunks.

## Decisiones arquitectónicas (D-01 a D-13)

- D-01: Sin LegalEntityRef — FK directa a LegalEntity
- D-06: PostgreSQL 16 + pgvector confirmado
- D-08: CEO = is_api_user=True
- D-13: visibility=CEO-ONLY excluida del agente knowledge

## Resultado

- Auth funcional con JWT + roles (CEO, AGENT_*, CLIENT_*)
- mwt-knowledge container activo, /health OK
- pgvector ingestion de KB chunks operativo
- 13 decisiones arquitectónicas documentadas

---

Stamp: DONE — Ejecutado y cerrado 2026-03-16
