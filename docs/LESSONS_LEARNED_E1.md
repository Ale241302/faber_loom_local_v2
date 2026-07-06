# Lecciones aprendidas — Etapa 1 (SpaceLoom / FaberLoom)

**id:** LESSONS_LEARNED_E1  
**versión:** 1.0  
**fecha:** 2026-07-06  
**estado:** cerrado para E2  

---

## 1. Contexto

La Etapa 1 construyó un runtime local funcional (SpaceLoom → FaberLoom) con:

- Backend FastAPI + SQLite monolítica.
- Frontend React 18 transpilado en el navegador (Babel standalone, sin build step).
- Parser de `SKILL.md`, rutinas aprobadas con HITL, router de modelos, presupuesto, KB con citas, drafts de correo, sellado workspace y Foundation Beta.

Estas notas capturan lo que aprendimos y los mecanismos que llevamos a E2 para no repetir fricciones.

---

## 2. Lo que funcionó

### 2.1 Costuras contract-first desde el inicio

Definir campos latentes (`tenant_id`, `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `source_version`, `approved_by`) en las tablas principales permitió avanzar E1 sin romper el modelo cuando llegó el contexto multi-usuario. La migración a multi-tenant fue posible sin reescribir tablas.

### 2.2 HITL como gate central

Toda acción irreversible (enviar correo, borrar fuente de KB, promover a gold) pasó por un estado intermedio y una aprobación explícita. Esto evitó daños reales durante dogfooding interno.

### 2.3 Router abstraído del proveedor

El router de completions mantuvo la UI libre de detalles de API keys y modelos. Cambiar de proveedor fue cuestión de configuración, no de reescribir prompts.

### 2.4 Tests de regresión por milestone

La suite `app/tests/test_sl*.py` alineada a SL0–SL5 detectó rápidamente regresiones cuando se movieron piezas grandes (por ejemplo, el rediseño de shell y la unificación de auth en E2-0).

### 2.5 Foundation Beta como fuente de verdad de identidad

Aunque arrancó como spike, Foundation consolidó tenant, usuarios, roles y sesiones. Enriquecer el JWT legacy desde Foundation (Opción A) fue mínimamente intrusivo y mantuvo la cookie HttpOnly.

---

## 3. Lo que costó más de lo esperado

### 3.1 Auth híbrida legacy ↔ Foundation

Tener dos fuentes de identidad generó ambigüedad: el JWT legacy sabía `sub` (email) pero no `tenant_id` ni `user_id` reales. E2-0 tuvo que cerrar esto antes de cualquier feature multi-usuario.

**Llevado a E2:** `get_current_user` enriquece claims desde Foundation; si no hay Foundation, el actor queda como legacy `sub`. Toda query usa `Context.resolved_actor_id()`.

### 3.2 `approved_by` pasado por query param

Los endpoints de aprobación aceptaban `approved_by` desde el cliente. Era conveniente para tests, pero violaba la costura de auditoría (el actor debe venir del contexto autenticado).

**Llevado a E2:** se eliminó el parámetro query; `approved_by` se toma de `ctx.resolved_actor_id()`. Los tests legacy se ajustaron para esperar el actor local cuando no hay login.

### 3.3 SQLite como única base operativa

SQLite funcionó para un usuario local, pero no da concurrencia real, RLS ni rollback fácil. La migración a Postgres se convirtió en gate de E2-1, no en tarea menor.

**Llevado a E2:** se preparó `app/scripts/sqlite_to_postgres.py` con dry-run, verificación por conteos y runbook (`docs/MIGRACION_POSTGRES_E2.md`).

### 3.4 UI sin build step

Babel standalone permitió iterar rápido, pero el bundle no se minifica ni se tree-shakea. A medida que crece `app.jsx`, el arranque del frontend se vuelve más pesado.

**Llevado a E2:** se mantiene el stack actual para no perder velocidad, pero se acuerda revisar la decisión si el bundle supera un umbral de tamaño o tiempo de carga.

### 3.5 Nombres y categorías de rutinas

La categoría de una rutina se derivó temporalmente del campo `source_version` (por ejemplo, `faberloom-skill`). Eso creó lógica confusa y una dependencia oculta.

**Llevado a E2:** se añadió `category` como columna explícita con `CHECK` en `routine` y se migraron los valores existentes.

---

## 4. Decisiones arquitectónicas que se mantienen

- **Context is God:** todo helper de DB recibe `Context(workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision)`.
- **AuditWriter dual:** la fila en `audit_log` es fuente de verdad; `audit.jsonl` es espejo legible para debug.
- **No datos inventados en KB:** todo hecho duro requiere fuente con locator; el gold loop exige doble verificación.
- **Router presupuestado:** el router aplica `budget_cap_usd` y devuelve evidencia de costo por invocación.
- **Workspace seal:** los datos sensibles usan HMAC por workspace para detectar manipulación.

---

## 5. Checklist para cerrar E2-0

- [x] Unificar identidad runtime (JWT legacy + Foundation).
- [x] `approved_by` desde Context, no desde query param.
- [x] `correlation_id` en `audit_log` para correlacionar eventos de aprobación/ejecución.
- [x] Tenant canario sembrado, aislado y marcado (`workspace.is_canary`) como gate permanente desde E2-0/E2-1.
- [x] Script y runbook de migración SQLite → Postgres.
- [x] Licencia FSL-1.1-ALv2 aplicada.
- [x] `harness/prompts/sl1b_dogfood_prompts.json` versionado.
- [x] Suite de tests completa verde.

---

## 6. Referencias

- `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1.md`
- `Plan/PLAN_TRABAJO_E2_FUGU_v3.md`
- `AGENTS.md`
- `docs/MIGRACION_POSTGRES_E2.md`
