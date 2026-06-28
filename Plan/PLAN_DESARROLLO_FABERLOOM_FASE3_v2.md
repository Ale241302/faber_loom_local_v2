# Plan Fase 3 v2 — SpaceLoom Toolset (corregido tras auditoría fugu)

## Objetivo

Cerrar la funcionalidad del **rail derecho (Toolset)** y las **vistas de Capacidades** para que el usuario pueda:

1. Crear/editar **Skills** (`category=skill`).
2. Crear/editar **Agentes** (`category=agent`) con **modelo de IA + prompt/persona**.
3. Ver Skills/Agentes/Conocimiento/Gold en el right-rail.
4. Invocar Skills/Agentes **desde el chat** con un click o con `@mención`.

Este plan integra los **must-fix** de la auditoría `codex -p fugu`.

---

## Must-fix incorporados

| # | Hallazgo fugu | Corrección en este plan |
|---|---------------|--------------------------|
| 1 | Migración v12 insegura | `UPDATE` mapea solo valores del enum; cualquier otro valor → `custom`. Test con `source_version` desconocido. |
| 2 | `category` campo + computed_field incompatible | `RoutineRead.category` es un campo normal leído de DB. Se elimina el `@computed_field`; el fallback legacy se hace en la migración. |
| 3 | Queries `routine` sin `tenant_id` | Todas las queries de routine/routine_run incluyen `AND tenant_id IS ?` e índices actualizados. |
| 4 | `is_active` no se valida en ejecución | `_execute_skill_run`, `/invoke`, `/run` y `@mention` rechazan `is_active=0`. |
| 5 | `preset_id`/`category`/`name` cambios mantienen aprobación | Se añaden a `_ROUTINE_APPROVAL_SENSITIVE_FIELDS`; cualquier cambio limpia `approved_by`. |
| 6 | Budget cap no aplica a skills | `execute_skill` recibe `spent_usd` real; `router.complete` respeta el cap. |
| 7 | Validación incompleta de `preset_id` | Validador Pydantic y runtime: formato `provider:model`, provider conocido, modelo en `MODEL_ALLOWLIST`, provider disponible. |
| 8 | Override de provider/model como bypass | `/invoke` **no acepta** override; usa siempre el `preset_id` de la rutina. `@mention` mantiene override opcional ya existente, pero se audita explícitamente. |
| 9 | `@mention` ambiguo | Crear/actualizar rutina rechaza nombres duplicados (case-insensitive) dentro del workspace. `get_routine_by_name` devuelve `409` si hay múltiples coincidencias. |
| 10 | Categoría como permiso de ejecución | `/invoke` y `@mention` solo permiten `skill`, `agent` o `custom`. `template`/`reference` no ejecutables desde chat. |
| 11 | `persona_md` sin gate de inyección | Se valida `persona_md` con el mismo detector de patrones peligrosos que `skill_md` antes de aprobación/ejecución. |
| 12 | `tools_allowlist`/`trigger_json` sin validar JSON | Validadores Pydantic: deben ser arrays JSON de strings, con límites y política para `"*"`. |
| 13 | `onInvokeTool` no encaja con estado | Se usa evento global `spaceloom:invoke-routine` que `SpaceView` escucha, evitando elevar estado de chat a `App`. |
| 14 | Trazabilidad de `/invoke` | Se reutiliza el mismo flujo de `@mention`: mensaje user real, assistant, `run_id`, `routine_id`, versiones, `usage_record`, `audit_log`. |
| 15 | Versionado contract-first | Al crear/editar rutina se genera `routine_version` (timestamp ISO). Se copia a `routine_run`, `usage_record` y `audit_log`. |
| 16 | Tests críticos faltantes | Tests para inactivas, preset inválido, duplicados, JSON malformado, migración unknown, tenant isolation, budget cap en skill. |

---

## Backend

### Migración v12

```sql
ALTER TABLE routine ADD COLUMN category TEXT NOT NULL DEFAULT 'custom'
    CHECK (category IN ('skill', 'agent', 'template', 'reference', 'custom'));

UPDATE routine SET category = CASE
    WHEN source_version = 'faberloom-skill' THEN 'skill'
    WHEN source_version = 'faberloom-agent' THEN 'agent'
    WHEN source_version = 'faberloom-template' THEN 'template'
    WHEN source_version = 'faberloom-reference' THEN 'reference'
    ELSE 'custom'
END;

CREATE INDEX IF NOT EXISTS idx_routine_category
    ON routine(workspace_id, tenant_id, category, is_active, approved_by);
```

`SCHEMA_VERSION = 12`.

### Modelos Pydantic (`app/src/models.py`)

- `RoutineRead`: campo `category: str` (no computed). Eliminar `@computed_field category`.
- `RoutineCreate`:
  - `category: Literal["skill","agent","template","reference","custom"] = "custom"`.
  - Validadores: `tools_allowlist` y `trigger_json` deben parsear a `list[str]`.
  - Validador `preset_id`: si se provee, debe tener formato `provider:model` y modelo permitido.
  - Validador `persona_md`: detector de patrones peligrosos.
- `RoutineUpdate`: mismos validadores opcionales; `category`, `preset_id`, `name` incluidos.

### DB helpers (`app/src/db.py`)

- `ROUTINE_COLUMNS`: incluir `category`.
- Todas las queries de routine añaden `AND tenant_id IS ?`.
- `create_routine`: aceptar `category`, generar `routine_version = utc_now()`.
- `update_routine`: permitir `category`; al actualizar regenerar `routine_version = utc_now()`.
- `list_routines(ctx, conn, category=None)`: filtro opcional con tenant_id.
- `get_routine_by_name`: añadir tenant_id; devolver lista para detectar duplicados.
- Verificar nombre duplicado en create/update: helper `is_routine_name_taken(ctx, conn, name, exclude_id=None)`.

### Seguridad y ejecución (`app/src/api.py`, `app/src/skills.py`)

- `_ROUTINE_APPROVAL_SENSITIVE_FIELDS` incluye `skill_md`, `tools_allowlist`, `schema_output_json`, `persona_md`, `trigger_json`, `preset_id`, `category`, `name`.
- `_execute_skill_run`:
  - Rechaza `is_active=0`.
  - Rechaza `category` no ejecutable (`template`/`reference`).
  - Recibe `spent_usd` y lo pasa a `CompletionRequest`.
  - Crea run → **commit** → llama LLM → update run → audit (no dentro de la misma transacción).
  - Copia `routine_version` al run.
- Validar `preset_id` en runtime parseando con `split(":", 1)` y consultando `MODEL_ALLOWLIST`/providers.

### API endpoints

- `GET /api/workspaces/{id}/routines?category=...` con validación de enum.
- `POST /api/workspaces/{id}/routines` con validación de duplicado y categoría.
- `PATCH /api/workspaces/{id}/routines/{rid}` con duplicado, campos sensibles y limpieza de aprobación.
- `POST /api/workspaces/{id}/chats/{chat_id}/invoke`:
  - Body: `{ routine_id, user_request? }`.
  - No acepta `provider_slug`/`model` override.
  - Requiere rutina aprobada, activa y ejecutable.
  - Resuelve provider/model desde `preset_id`.
  - Persiste mensajes, run, usage, audit.
- `@mention` (completions):
  - Rechaza inactivas/no ejecutables.
  - Resuelve modelo: payload override (si viene) → preset de rutina → router default.
  - Si `get_routine_by_name` devuelve múltiples filas → `409 ambiguous`.

### Catalog import

- `import_catalog_items` pasa `category` explícito a `create_routine`.
- `persona_md` importado pasa validación de inyección.

---

## Frontend

### Helpers

- `parsePreset(presetId)` / `formatPreset(provider, model)`.
- `isExecutableCategory(category)` → true para skill/agent/custom.

### Componentes base de rutinas

- `RoutineForm({ mode, initial, providers, models, onSubmit, onCancel })`.
- `RoutineCard({ routine, onEdit, onApprove, onToggle, onDelete, onInvoke })`.
- `RoutineList({ routines, categoryLabel, onInvoke })`.

### `SkillsView`

- Carga `GET /routines?category=skill`.
- Lista con `RoutineCard`.
- Formulario: nombre, skill_md, tools_allowlist (JSON), schema_output_json (JSON), trigger_json (JSON), toggle activo.
- Crear/editar/aprobar/eliminar.

### `AgentsView`

- Carga `GET /routines?category=agent`.
- Formulario adicional:
  - `persona_md` (prompt).
  - Selector provider + model (de `/router/status`).
  - `preset_id` guardado como `provider:model`.

### `ToolsetPanel` / `RightRail`

```jsx
const TABS = [
  { id: "agents", label: "Agentes" },
  { id: "skills", label: "Skills" },
  { id: "kb", label: "Conocimiento" },
  { id: "gold", label: "Gold" },
];
```

- Tabs renderizan listas filtradas.
- Items ejecutables muestran botón "Invocar".
- Al invocar, emite `window.dispatchEvent(new CustomEvent("spaceloom:invoke-routine", { detail: { routine } }))`.

### `SpaceView`

- Escucha `spaceloom:invoke-routine`.
- Si no hay chat activo, crea uno nuevo.
- Llama `POST /chats/{id}/invoke` con `routine_id` y `user_request` (opcional).
- Refresca mensajes.
- `Composer`:
  - Botón "@" abre menú de routines ejecutables.
  - Selección inserta `@Nombre` o invoca directamente.
  - (Opcional) mostrar provider/model efectivo del chat/override.

### CSS

- `.toolset-tabs`, `.toolset-tab`, `.toolset-tab.is-active`.
- `.toolset-list`, `.toolset-item`, `.toolset-item-actions`.
- `.routine-form` grids.
- Ajustar `.rail3` para scroll vertical.

---

## Tests a añadir

1. Migración v12 con `source_version` desconocido → `custom`.
2. `GET /routines?category=agent` devuelve solo agentes.
3. Crear rutina con nombre duplicado → `409`.
4. Actualizar `preset_id` de rutina aprobada → limpia `approved_by`.
5. Ejecutar rutina inactiva → `409`.
6. Ejecutar `template` desde chat → `409` o `422`.
7. `preset_id` inválido → `422`.
8. `tools_allowlist` JSON malformado → `422`.
9. `persona_md` con `<script` → `422`.
10. Budget cap respeta skill con `spent_usd` (mockear router si es necesario).
11. `get_routine_by_name` con duplicados → `409 ambiguous`.
12. `/invoke` persiste mensaje assistant con `run_id` y `routine_version`.
13. Cross-tenant: rutina de otro tenant no es accesible.

---

## Archivos a modificar

- `app/src/models.py`
- `app/src/db.py`
- `app/src/api.py`
- `app/src/skills.py`
- `app/src/faberloom_catalog.py`
- `app/static/js/app.jsx`
- `app/static/js/foundation.jsx` (si se añaden selects/modales)
- `app/static/css/main.css`
- `app/tests/test_routines_crud.py`
- `app/tests/test_sl3a_skills.py`
- `app/tests/test_sl1a_router_endpoints.py` (opcional)

---

## Criterios de aceptación

- [ ] Admin → Skills y Admin → Agentes son vistas reales con CRUD completo.
- [ ] Los agentes permiten elegir provider/model y prompt; se guarda como `preset_id`.
- [ ] Right-rail Toolset muestra tabs Agentes/Skills/Conocimiento/Gold.
- [ ] Click en agente/skill invoca desde el chat vía `/invoke`.
- [ ] `@Nombre` sigue funcionando y respeta seguridad.
- [ ] Rutinas inactivas, templates/references no ejecutables desde chat.
- [ ] Cambio de preset/modelo/categoría/nombre limpia aprobación HITL.
- [ ] Todos los tests pasan (`uv run --extra test pytest -q`).
- [ ] Build genera `app/dist/SpaceLoom.exe`.

---

## Nota final

Este plan v2 corrige los 16 must-fix de fugu. El siguiente paso es la implementación directa; no se requiere re-auditoría previa salvo que el usuario lo solicite.
