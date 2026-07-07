# DEC_FB_SPIKE_PROMOTION — Promoción del spike E1 a base física de E2-1
id: DEC_FB_SPIKE_PROMOTION
version: 1.0
status: ACTIVE
stamp: 2026-07-07
decisor: mandato H7 (PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1 Sec.8, arquitecto 2026-07-06)
relacionado: PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1 - MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1

---

## Decisión

El deploy del spike E1 en el VPS (187.77.218.102, `/opt/faber_loom`, app.faberloom.ai,
Docker + mwt-nginx + JWT multi-user) **se promueve** a base física de la instancia
compartida de E2-1. Esta decisión **supersede** la instrucción de renombre del
manifiesto 2026-06-30. El runtime único es `app/` FastAPI (H6); el SPINE
Django/Postgres queda como contrato de referencia, archivado con tag.

## Estado de la promoción (2026-07-07)

- Deploy activo: compose `faber_loom` (api :8200, faberloom-postgres :5435, faberloom-minio :9100/9101) detrás de mwt-nginx, dominios Cloudflare.
- Auth: JWT cookies HttpOnly + refresh rotativo (access 60 min, refresh 7 días).
- Canario permanente: tenant `canary` sembrado al arranque (`seed_canary_workspace`); regresión por deploy: `python app/scripts/check_canary_isolation.py` (M16 bidireccional, corre dentro de la imagen).

## Staging Postgres + RLS (preparación del switch E2-0/E2-1)

Ejecutado 2026-07-07 contra `faberloom-postgres` (la app sigue en SQLite):

1. `sqlite_to_postgres.py` corregido (shadow tables FTS5 excluidas, PKs compuestas, IDENTITY BY DEFAULT, orden de FKs multi-pass, setval de secuencias, audit_log sin FKs por ser append-only con huérfanos legítimos) → migración **completa sin issues**, conteos por tabla verificados (616 filas).
2. `postgres_rls_policies.sql` corregido (ENABLE + FORCE ROW LEVEL SECURITY) y aplicado; rol `faberloom_app` NOBYPASSRLS creado.
3. **Gate del canario contra RLS: verde en ambas direcciones** — desde scope MWT 0 filas canary; desde scope canary 0 filas MWT (validación a nivel de policy, no solo capa app).

## Lo que FALTA para el switch de runtime (no incluido en esta DEC)

- `app/src/db.py` y foundation usan `sqlite3` directo (placeholders `?`, `sqlite_master`, PRAGMA). El switch requiere capa de conexión dual (psycopg + placeholders `%s`) o adaptador — talla L, hito propio.
- FTS: `kb_chunk_fts` (FTS5) debe reconstruirse con tsvector/GIN en Postgres.
- `foundation.sqlite3` (fnd_*) migra por el mismo script en el corte final.
- Corte final: congelar escrituras → migrar snapshot → `set_app_scope` en el pool → smoke suite → cambiar `FABERLOOM_DB_URL`.
