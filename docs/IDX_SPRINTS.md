---
id: IDX_SPRINTS
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: PLATAFORMA
tipo: index
last_review: 2026-05-04
stamp: VIGENTE - 2026-05-04
aplica_a: [SHARED]
---

# IDX_SPRINTS - Domain Index (LOTE_SM_SPRINT*)

> Health: 28 sprints documentados (S0-S27 todos DONE) - 0 abiertos
> Ubicacion fisica: docs/archivo/ (todos los DONE consolidados)
> Origen: audit retrieval golden-set 10q 2026-05-04 detecto que el tipo LOTE no tenia router canonico - el dato vivia solo en CLAUDE.md y forzaba glob global.

## Sprints cerrados

| Sprint | Archivo | Stamp/cierre | Tema |
|---|---|---|---|
| S0 | docs/archivo/LOTE_SM_SPRINT0.md | 2026-02-28 | Bootstrap pre-KB |
| S1 | docs/archivo/LOTE_SM_SPRINT1.md | DONE 9/9 items | Core operativo inicial |
| S2 | docs/archivo/LOTE_SM_SPRINT2.md | aprobado CEO 2026-03-12 | Ejecutado AG-02 |
| S3 | docs/archivo/LOTE_SM_SPRINT3.md | DONE 8/8 items | [ver archivo] |
| S4 | docs/archivo/LOTE_SM_SPRINT4.md | DONE 12/12 items | [ver archivo] |
| S5 | docs/archivo/LOTE_SM_SPRINT5.md | DONE 9/9 items | [ver archivo] |
| S6 | docs/archivo/LOTE_SM_SPRINT6.md | aprobado CEO 2026-03-12 | Ejecutado AG-02 |
| S7 | docs/archivo/LOTE_SM_SPRINT7.md | DONE 13/13 items | [ver archivo] |
| S8 | docs/archivo/LOTE_SM_SPRINT8.md | 2026-03-16 | [ver archivo] |
| S9 | docs/archivo/LOTE_SM_SPRINT9.md | 2026-03-16 | [ver archivo] |
| S10 | docs/archivo/LOTE_SM_SPRINT10.md | DONE | Ejecutado AG-02 |
| S11 | docs/archivo/LOTE_SM_SPRINT11.md | DONE | Modelo datos CostLine + STATE_MACHINE H2/H3/H7/H8 |
| S12 | docs/archivo/LOTE_SM_SPRINT12.md | DONE | Ejecutado AG-02 |
| S13 | docs/archivo/LOTE_SM_SPRINT13.md | DONE | Ejecutado AG-02 |
| S14 | docs/archivo/LOTE_SM_SPRINT14.md | DONE | Ejecutado AG-02 |
| S15 | docs/archivo/LOTE_SM_SPRINT15.md | DONE | Ejecutado AG-02/AG-03 |
| S16 | docs/archivo/LOTE_SM_SPRINT16.md | DONE | Ejecutado AG-02 |
| S17 | docs/archivo/LOTE_SM_SPRINT17.md | DONE | Ejecutado AG-02 |
| S18 | docs/archivo/LOTE_SM_SPRINT18.md | DONE | Ejecutado AG-02 |
| S19 | docs/archivo/LOTE_SM_SPRINT19.md | DONE | Ejecutado AG-02/AG-03 |
| S20 | docs/archivo/LOTE_SM_SPRINT20.md | DONE | Ejecutado AG-02 |
| S20B | docs/archivo/LOTE_SM_SPRINT20B.md | 2026-04-06 | Commands canonicos post-auditoria |
| S21 | docs/archivo/LOTE_SM_SPRINT21.md | 2026-04-01 | Migraciones produccion |
| S22 | docs/archivo/LOTE_SM_SPRINT22.md | 2026-04-05 | Servidor operativo |
| S23 | docs/archivo/LOTE_SM_SPRINT23.md | 2026-04-06 | Servidor operativo |
| S24 | docs/archivo/LOTE_SM_SPRINT24.md | 2026-04-07 | Seguridad B2B base + knowledge pipeline |
| S25 | docs/archivo/LOTE_SM_SPRINT25.md | 2026-04-08 | Payment machine + deferred + parent/child |
| S26 | docs/archivo/LOTE_SM_SPRINT26.md | 2026-04-10 | Notifications app + cobranza + admin templates |
| S27 | docs/archivo/LOTE_SM_SPRINT27.md | 2026-04-10 | Seguridad residual + audit completo + backups + hardening |

## Reglas

1. Sprint nuevo se crea como archivo `LOTE_SM_SPRINT<N>` (con el número de sprint reemplazando el placeholder `<N>`) en `docs/` (no en `archivo/`).
2. Al cerrarse (status DONE) se mueve a `docs/archivo/` y se appendea a la tabla de arriba.
3. Refs cruzadas con IDX_PLATAFORMA (sprints de plataforma) e IDX_OPS (cuando aplica).
4. Sprints DONE comprimidos a <=50 lineas via POL_CONTEXT_BUDGET (lazy migration).

## Pendientes

- Q1 2026: completar columna "Tema" para S3-S20 leyendo headers individuales (campo [ver archivo] hoy).
- Verificar si S28+ esta en planificacion o si Sprints estan congelados post-S27.

---

Changelog:
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Fix patrón no concreto en regla de creación de sprints: se describe el nombre con placeholder sin token de archivo. v1.0 → v1.1.
- v1.0 (2026-05-04): Creacion. Origen: audit retrieval golden-set 10q detecto que LOTE_SM_SPRINT* no tenia IDX canonico; CLAUDE.md tenia solo resumen agregado. ASCII puro per memoria edit_tool_truncates_typographic_chars.
