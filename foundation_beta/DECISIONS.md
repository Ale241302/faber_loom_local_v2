# Decisiones de arquitectura — M16 Tenant Isolation

## 1. Tablas de plataforma sin RLS
`tenants` y `tenant_plan_features` no tienen columna `tenant_id` y no aplican RLS. Son tablas de plataforma gestionadas por platform admin. El resto de tablas tenant-scoped (incluyendo `sample_items` y `kb_embedding`) sí aplican RLS.

## 2. Política RLS fail-closed
La policy usa:
```sql
USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::UUID)
```
Si `app.tenant_id` no está seteado, `NULLIF` devuelve `NULL`, el cast es seguro y la comparación devuelve `NULL` (no `TRUE`), por lo que RLS deniega. Esto evita el error de cast y mantiene el comportamiento fail-closed.

## 3. `TenantMiddleware` y testing header
En producción el tenant_id proviene de la sesión server-side (M08). Para tests de M16 se habilita un header `X-Tenant-Id` solo cuando `settings.TENANT_TESTING_HEADER_ALLOWED` es `True` (DEBUG o env `TESTING=True`).

## 4. `init_rls` verifica existencia de `tenant_id`
El management command no intenta crear policies en tablas que no tengan la columna `tenant_id`, evitando errores con tablas de plataforma o tablas aún no migradas.

## 5. Celery eager en tests
`conftest.py` configura `CELERY_TASK_ALWAYS_EAGER=True` para ejecutar tareas sincrónicamente durante tests, eliminando la necesidad de un worker corriendo.

## 6. Tabla `kb_embedding` particionada por `tenant_id`
Se crea como tabla particionada por lista (`PARTITION BY LIST (tenant_id)`). El helper `ensure_tenant_partition` crea una partición e índice HNSW por tenant. La clave primaria incluye `tenant_id` para cumplir con las restricciones de PostgreSQL en tablas particionadas.

## 7. Dependencias mínimas
`letta` y `litellm` se dejan como dependencias opcionales. Los helpers `llm.py` y `memory.py` solo generan strings/dicts; no requieren los SDK instalados para los tests de M16.

## 8. Nota sobre ejecución local
En el entorno de desarrollo actual no se encontró Docker Desktop ni PostgreSQL/Redis locales instalados. Por ello los tests cross-tenant que requieren base de datos no fueron ejecutados en esta sesión, pero el código está preparado para correr una vez levantados los servicios con `docker compose up`.
