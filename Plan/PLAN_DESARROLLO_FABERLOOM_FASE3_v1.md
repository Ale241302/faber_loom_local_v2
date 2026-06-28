# Plan Fase 3 — SpaceLoom Toolset (Agentes, Skills, Conocimiento, Gold)

## Objetivo de la fase

Cerrar la funcionalidad del **rail derecho (Toolset)** y las **vistas de Capacidades** para que el usuario pueda:

1. Crear y editar **Skills** (rutinas `category=skill`).
2. Crear y editar **Agentes** (rutinas `category=agent`) y asignarles **modelo de IA + prompt/persona**.
3. Ver Skills/Agentes/Conocimiento/Gold en el **right-rail Toolset**.
4. Invocar Skills/Agentes **desde el chat** con un click o con `@mención`.

El backend ya tiene casi todo (routines, router, chat completions, @mention). El trabajo principal es: (a) persistir una `category` real de routine, (b) activar `preset_id` como `provider:model`, y (c) construir la UI de gestión e invocación.

---

## Estado de partida

- **Backend:**
  - Tabla `routine` con `source_version` usado como proxy de categoría (`faberloom-skill`, `faberloom-agent`, `v1` → custom).
  - `RoutineRead.category` es un `@computed_field` que deriva de `source_version`.
  - `preset_id` existe pero no se usa para nada en ejecución.
  - `GET /api/workspaces/{id}/routines` no filtra por categoría server-side.
  - `POST /workspaces/{id}/chats/{chat_id}/completions` ya soporta `@Mención` y `provider_slug`/`model`.
  - `SkillInvokeRequest` y `_execute_skill_run` aceptan `provider_slug`/`model`, pero no leen el preset de la rutina.

- **Frontend:**
  - `SkillsView` y `AgentsView` son placeholders SL0.
  - `RightRail` es un placeholder "Toolset (Fase 3)".
  - `SpaceView` chat envía solo `{ message }` y no muestra modelos ni selector de skills.
  - `RoutinesView` ya hace CRUD completo de routines (se reutilizará lógica).

---

## Cambios de backend

### 1. Migración v12 — columna `category` en `routine`

```sql
ALTER TABLE routine ADD COLUMN category TEXT NOT NULL DEFAULT 'custom'
    CHECK (category IN ('skill', 'agent', 'template', 'reference', 'custom'));
CREATE INDEX IF NOT EXISTS idx_routine_category ON routine(workspace_id, category);
```

Migración de datos:

```sql
UPDATE routine SET category = CASE
    WHEN source_version LIKE 'faberloom-%' THEN substr(source_version, 11)
    WHEN source_version IS NULL OR source_version = 'v1' THEN 'custom'
    ELSE source_version
END;
```

Actualizar `SCHEMA_VERSION = 12`.

### 2. Modelos Pydantic (`app/src/models.py`)

- `RoutineRead`:
  - Añadir `category: str` como campo normal (leído de DB).
  - Mantener el `@computed_field` legacy solo como fallback interno por si una fila antigua llega sin la columna; en producción leerá el valor real.
- `RoutineCreate`:
  - Añadir `category: Literal["skill","agent","template","reference","custom"] = "custom"`.
  - `source_version` sigue existiendo para catalog-import; no es el mecanismo principal de categoría.
- `RoutineUpdate`:
  - Añadir `category` opcional.
  - Añadir `preset_id` opcional.

### 3. DB helpers (`app/src/db.py`)

- `create_routine`: aceptar `category: str = "custom"`, escribirlo en INSERT.
- `update_routine`: incluir `category` en `ALLOWED_ROUTINE_UPDATE_FIELDS`.
- `list_routines(ctx, conn, category=None)`:
  - Si se pasa `category`, filtrar por `WHERE workspace_id = ? AND category = ?`.
  - Si no, devolver todas.
- `get_routine_by_name(ctx, conn, name, category=None)`: opcionalmente restringir por categoría para resolver @mention sin ambigüedades.

### 4. API endpoints (`app/src/api.py`)

- `GET /api/workspaces/{workspace_id}/routines?category=skill|agent|...`
  - Parámetro query opcional, validado contra el enum.
  - Llama a `list_routines(ctx, conn, category=category)`.
- `POST /api/workspaces/{workspace_id}/routines` pasa `category` a `create_routine`.
- `PATCH /api/workspaces/{workspace_id}/routines/{routine_id}` permite `category` y `preset_id`.
- Nuevo endpoint:
  ```
  POST /api/workspaces/{workspace_id}/chats/{chat_id}/invoke
  Body: { routine_id: string, user_request?: string, provider_slug?: string, model?: string }
  ```
  - Resuelve la rutina por ID, requiere `approved_by`.
  - Usa `preset_id` de la rutina como `provider_slug:model` por defecto.
  - Ejecuta `_execute_skill_run` con `{ user_request }`.
  - Persiste mensajes user/assistant en el chat.
  - Devuelve `ChatCompletionResponse`.

### 5. Resolución de modelo/preset

- Nuevo helper `_preset_to_provider_model(preset_id: str | None) -> tuple[str|None, str|None]`:
  - Parsea `"openai:gpt-4o-mini"` → `("openai", "gpt-4o-mini")`.
  - Si no tiene `:` o está vacío → `(None, None)`.
- En `api_create_completion` (@mention path):
  - Si payload no trae `provider_slug`/`model`, usar el preset de la rutina.
  - Si payload los trae, payload gana.
- En `api_run_routine` (`/routines/{id}/run`):
  - Igual lógica: preset de rutina por defecto, payload override.
- Validar que el modelo esté en `MODEL_ALLOWLIST` del provider (ya existe `_validate_completion_choice`).

### 6. Catalog import (`app/src/faberloom_catalog.py`)

- Al importar items del catalog, usar el campo `category` del item (skill/agent/template/reference) en lugar de depender solo de `source_version`.
- Mantener `source_version = f"faberloom-{category}"` para trazabilidad.

---

## Cambios de frontend

### 1. Helpers reutilizables en `app/static/js/app.jsx`

Nuevos helpers pequeños:

```jsx
function parsePreset(presetId) {
  if (!presetId || !presetId.includes(":")) return { provider_slug: null, model: null };
  const [provider_slug, model] = presetId.split(":");
  return { provider_slug, model };
}

function formatPreset(provider_slug, model) {
  if (!provider_slug || !model) return "";
  return `${provider_slug}:${model}`;
}
```

### 2. `SkillsView` real

Reemplazar placeholder. Características:

- Cargar `GET /api/workspaces/{id}/routines?category=skill`.
- Listado tipo tarjeta con:
  - Nombre, badge `skill`, estado `Activo/Inactivo`, estado `Aprobado/Borrador`.
  - Toggle para activar/desactivar.
  - Botones Editar, Aprobar, Eliminar (con `DeleteConfirmModal`).
- Formulario de crección:
  - Nombre.
  - `skill_md` (textarea con hint de frontmatter YAML).
  - `tools_allowlist` (textarea JSON).
  - `schema_output_json` (textarea JSON).
  - Toggle activo.
- Modal de edición con los mismos campos.
- Al guardar/crear/eliminar: disparar `spaceloom-refresh`.

### 3. `AgentsView` real

Similar a `SkillsView` pero:

- Cargar `GET /api/workspaces/{id}/routines?category=agent`.
- Campos del formulario:
  - Nombre.
  - `persona_md` (prompt del agente).
  - `skill_md` (instrucciones/Skill opcional).
  - Selector de **Provider** (openai, anthropic, google, kimi, ollama).
  - Selector de **Model** según provider (poblar desde `/api/workspaces/{id}/router/status` → `model_allowlist`).
  - `preset_id` se guarda como `provider:model`.
  - `tools_allowlist` JSON.
  - Toggle activo.
- Estado y acciones idénticas a Skills.

### 4. `ToolsetPanel` y `RightRail`

Reemplazar `RightRail` por un componente con tabs:

```jsx
function ToolsetPanel({ open, activeWorkspace, activeTab = "agents", onInvoke }) {
  const [tab, setTab] = useState(activeTab);
  return (
    <aside className={cx("rail3", !open && "hidden")} aria-label="Toolset">
      <div className="toolset-tabs">
        {["Agentes", "Skills", "Conocimiento", "Gold"].map(t => ...)}
      </div>
      <div className="toolset-body">
        {tab === "agents" && <ToolsetRoutinesList category="agent" ... />}
        {tab === "skills" && <ToolsetRoutinesList category="skill" ... />}
        {tab === "kb" && <ToolsetKBList ... />}
        {tab === "gold" && <ToolsetGoldList ... />}
      </div>
    </aside>
  );
}
```

- `ToolsetRoutinesList`:
  - Carga routines filtradas.
  - Muestra solo activas y aprobadas primero.
  - Cada item con icono, nombre, chip de categoría.
  - Click invoca `onInvoke({ type: "routine", routine })`.
- `ToolsetKBList`:
  - Carga KB sources.
  - Click copia una referencia tipo `@source:Título` al composer (o simplemente notifica).
- `ToolsetGoldList`:
  - Carga gold candidates.
  - Click muestra resumen.

### 5. Integración con chat (`SpaceView`)

- Elevar un callback `onInvokeTool(item)` desde `App` hacia `ToolsetPanel`.
- En `SpaceView`, recibir `onInvokeTool` y, si hay chat activo, llamar a `POST .../invoke` con `routine_id`.
- `Composer`:
  - Añadir botón "+" o "@" que abre menú de skills/agentes disponibles.
  - Al seleccionar, insertar `@NombreDelAgente` en el textarea o invocar directamente.
  - Añadir selector opcional de provider/model para override del chat.
- `sendMessage`:
  - Si detecta @mention, envía `{ message, provider_slug, model }` (los del override si existen).
  - Si se hace click en Toolset, usa el endpoint `/invoke`.

### 6. CSS (`app/static/css/main.css`)

Añadir clases:

- `.toolset-tabs` (row de tabs).
- `.toolset-tab` / `.toolset-tab.is-active`.
- `.toolset-list` (columna scrollable).
- `.toolset-item` (fila clickable).
- `.toolset-item-meta` (chips).
- `.model-select` (selects de provider/model).
- Ajustar `.rail3` para que el contenido sea scrollable sin romper el layout.

### 7. CommandPalette

- Añadir sección "Skills y Agentes" con las routines activas del workspace.
- Al seleccionar una, navegar a `space` e invocar/insertar @mention.

---

## Flujos de usuario

### Crear un agente

1. Admin → Agentes.
2. Click "Nuevo agente".
3. Nombre: "Copywriter", Provider: openai, Model: gpt-4o-mini.
4. Prompt/persona: "Eres un copywriter experto en productos textiles..."
5. Guardar.
6. Aprobar el agente (HITL).

### Invocar desde chat

1. SpaceLoom → chat activo.
2. En right-rail, tab Agentes, click en "Copywriter".
3. El mensaje `@Copywriter redacta un email de seguimiento` se envía vía `/invoke`.
4. SpaceLoom responde ejecutando el agente con el modelo configurado.

### Crear una skill

1. Admin → Skills.
2. Nombre, SKILL.md con frontmatter (schema_output, tools), allowlist.
3. Guardar y aprobar.
4. Usar en chat escribiendo `@SkillName`.

---

## Tests a añadir/modificar

1. **Migración v12:**
   - Verificar que routines existentes mantienen categoría derivada correcta.
2. **CRUD por categoría:**
   - `POST /routines` con `category=agent` devuelve `category=agent`.
   - `GET /routines?category=skill` filtra correctamente.
3. **Preset resolution:**
   - Crear routine con `preset_id="openai:gpt-4o-mini"`.
   - Ejecutar vía `/run` sin provider/model → usa openai/gpt-4o-mini.
   - Ejecutar con override → usa override.
4. **Chat invoke endpoint:**
   - `POST /chats/{id}/invoke` con routine_id aprobado devuelve assistant message.
   - Routine no aprobado → 409.
   - Routine de otra categoría → funciona igual.
5. **@mention con override:**
   - Enviar `@Copywriter hola` con `provider_slug=anthropic` respeta override.
6. **Frontend placeholders desaparecen:**
   - `/skills` y `/agents` renderizan listas reales (smoke test con Playwright si es posible, o manual).

---

## Archivos a modificar

| Archivo | Cambio |
|---------|--------|
| `app/src/models.py` | Migración v12, modelos `RoutineCreate/Update/Read`. |
| `app/src/db.py` | `create_routine`, `update_routine`, `list_routines`, `get_routine_by_name`, `ROUTINE_COLUMNS`. |
| `app/src/api.py` | Filtro `category`, endpoint `/invoke`, preset resolution. |
| `app/src/skills.py` | Opcional: no cambia, sigue recibiendo provider/model. |
| `app/src/faberloom_catalog.py` | Usar `category` del item al importar. |
| `app/static/js/app.jsx` | SkillsView, AgentsView, ToolsetPanel, RightRail, Composer, SpaceView. |
| `app/static/js/foundation.jsx` | Posibles ajustes a modales/selects. |
| `app/static/css/main.css` | Estilos de toolset, tabs, items. |
| `app/tests/test_routines_crud.py` | Tests de categoría. |
| `app/tests/test_sl3a_skills.py` | Tests de preset y `/invoke`. |
| `app/tests/test_sl1a_router_endpoints.py` | Verificar model_allowlist expuesto. |

---

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|-----------|
| Añadir columna `category` rompe `RoutineRead.category` legacy | Dejar computed_field como fallback; Pydantic prioriza el campo real si existe en la row. |
| `preset_id` libre permite valores malformados | Validar formato `provider:model` en `RoutineCreate/Update`. |
| Cambios en DB invalidan HMACs de `routine_run` | `routine` no tiene HMAC, así que no afecta. Recomputar HMACs no es necesario. |
| UI de model selector requiere conocer allowlist | Cargar `/router/status` al abrir AgentsView/Toolset. |
| Tests de @mention actuales usan nombres | Mantener compatibilidad de `@mention` mientras se añade `/invoke`. |
| Build PyInstaller lento | No modificar `build.py`; el build final se hará al terminar. |

---

## Criterios de aceptación

- [ ] En Admin → Skills se pueden crear, editar, activar, aprobar y eliminar skills.
- [ ] En Admin → Agentes se pueden crear agentes con provider/model/prompt asignados.
- [ ] El right-rail muestra tabs Agentes/Skills/Conocimiento/Gold con datos reales.
- [ ] Desde el chat se puede invocar una skill/agente haciendo click en el right-rail.
- [ ] Desde el chat funciona `@Nombre` y respeta el modelo configurado o un override.
- [ ] Todos los tests pasan (`uv run --extra test pytest -q`).
- [ ] Build `uv run python app/build.py` genera `app/dist/SpaceLoom.exe`.

---

## Nota para auditoría fugu

Este plan debe ser auditado por `codex -p fugu` antes de la implementación. Se busca feedback sobre:

1. Omisiones de seguridad (HITL, aprobación, validación de preset_id).
2. Compatibilidad con el diseño contract-first existente.
3. Riesgos en la migración de datos.
4. Si es necesario un endpoint `/invoke` separado o basta con mejorar @mention.
5. Mejor forma de exponer modelos permitidos al frontend.
