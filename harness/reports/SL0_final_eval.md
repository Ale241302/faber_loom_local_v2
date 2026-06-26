He revisado todos los archivos y los resultados de tests. Veredicto:

## Evaluación SL0 — SpaceLoom

### 1. DoD SL0 ✓
- **App vacía corre:** `main.py` levanta FastAPI con `lifespan` que inicializa DB + seed, sirve el shell estático y abre la ventana pywebview (`run_desktop`). Hay fallback HTML si falta `index.html`.
- **1 workspace de prueba + datos semilla:** `seed.py` crea `MWT Demo` (`mwt-demo`) de forma **idempotente** (busca por slug antes de insertar). Confirmado por `test_seed_is_idempotent` y `test_health_and_seed_workspace`.
- **Modelo de datos base:** migraciones versionadas (`_schema_version`, `SCHEMA_VERSION=2`) con `workspace`, `kb_source`, `chat`, `message`, `draft`, `audit_log`, `routine`, `routine_run`.

### 2. Costuras contract-first ✓
- **Campos latentes:** `tenant_id`, `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by` presentes en **todas** las tablas requeridas (la migración v2 los uniforma y propaga `workspace_id` a `message`). Verificado por `test_schema_contains_contract_tables_and_latent_fields`.
- **Context:** `Context(workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision)` con separación explícita `system_context()` (bootstrap) vs. `require_scoped_workspace()` (datos). Toda lectura de `workspace` filtra por `ctx.tenant_id`.
- **AuditWriter:** escribe a `audit_log` (fuente de verdad, participa en la transacción del caller) y espeja a `audit.jsonl` tras el commit. Verificado por `test_create_workspace_unique_slug_and_audit`.
- **routine/routine_run:** ambas tablas existen con su contrato completo (allowlist de tools, evidence, estados incl. `requires_hitl`).

### 3. Claims de UI ✓
La UI es honesta: el composer hace `preventDefault` y declara "en SL0 el composer es solo de muestra"; vistas futuras usan `PlaceholderView`; pills marcadas "Disponible en SL1a/SL2a". No hay features falsamente anunciadas como funcionales.

### 4. Riesgos P0 ✓ (ninguno activo)
- **Envío/borrado sin HITL:** SL0 no ejecuta acciones irreversibles; sin endpoints de envío/borrado, composer inerte.
- **Injection por contenido:** SL0 no ingiere contenido externo (sin email/PDF/SKILL.md).
- **Fuga cross-workspace:** scoping aplicado y probado — `test_context_tenant_scope_is_applied_to_workspace_reads` confirma 404 cross-tenant.
- **Dato inventado sin fuente:** seed sin hechos de negocio; UI con estados vacíos.

### Observaciones menores (no bloqueantes)
- Mojibake aparente en títulos/comentarios (`SpaceLoom â€" FaberLoom`) es artefacto de visualización de PowerShell; el encoding de archivo es correcto (ya documentado).
- Avatar/usuario `"AL" / Álvaro` hardcodeado en el shell — cosmético, aceptable para SL0.
- Recomendado para SL1a: documentar/preparar la costura del **Router** de proveedores (mencionada en AGENTS.md pero aún no instanciada), aunque no es DoD de SL0.

Los 6 tests pasan y cubren health/seed, esquema/campos latentes, idempotencia, slug único + auditoría, validación de blanco y scoping por tenant.

[APROBADO]