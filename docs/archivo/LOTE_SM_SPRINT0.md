# LOTE_SM_SPRINT0 — Bootstrap Infraestructura
id: LOTE_SM_SPRINT0
status: DONE — ejecutado pre-KB (enero-febrero 2026)
visibility: [INTERNAL]
stamp: DONE — 2026-02-28
domain: Plataforma (IDX_PLATAFORMA)
version: 1.0
sprint: 0
priority: P0
depends_on: ninguno
ejecutado_por: AG-02 (Alejandro)

---

## Objetivo

Setup inicial de infraestructura antes de la formalización de la KB. Este sprint no fue documentado en tiempo real — se reconstruye como registro histórico para cerrar la trazabilidad referenciada por PLB_ORCHESTRATOR (FROZEN) y LOTE_SM_SPRINT1.

## Alcance ejecutado

- Servidor Hostinger KVM 8 provisionado
- Docker Compose base: Django + PostgreSQL + Redis + Celery + MinIO
- Dominio mwt.one configurado
- Consola administrativa inicial
- Modelo Expediente v1

## Retrospectiva

### Lecciones aprendidas
- La infraestructura se montó antes de tener KB formal — toda la documentación fue retroactiva
- Docker Compose como base fue decisión correcta para el volumen actual

### Deuda técnica generada
- Sin CI/CD formal (persiste a Sprint 10)
- Sin Git repo hasta Sprint 8
- Puerto 8001 expuesto (detectado en Sprint 8)

---

Stamp: DONE v1.0 — Registro histórico. Reconstruido 2026-03-18 para cerrar ref rota en PLB_ORCHESTRATOR (FROZEN) y LOTE_SM_SPRINT1.

Changelog:
- v1.0 (2026-03-18): Creación como registro histórico. Trigger: auditoría ChatGPT 9.0/10 — ref rota a LOTE_SM_SPRINT0.
