Nota: intenté cargar la skill `graphify`; su `SKILL.md` externo quedó bloqueado por sandbox, pero sí revisé `PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md`, `graphify-out/GRAPH_REPORT.md` y archivos clave (`models.py`, `db.py`, `api.py`, `skills.py`, `faberloom_catalog.py`, `app.jsx`).

**Veredicto: NO-GO hasta corregir los must-fix.**

## Must-fix antes de implementar

1. **Migración v12 insegura con `CHECK(category)`**  
   El `UPDATE` puede generar categorías fuera del enum (`source_version` arbitrario, `faberloom-*` no esperado) y romper la migración. Mapear solo valores permitidos; todo lo demás → `custom`. Añadir test con `source_version` desconocido.

2. **`RoutineRead.category` como campo + `@computed_field` es incompatible**  
   En Pydantic v2 no debes tener campo normal y `computed_field` con el mismo nombre. Quitar el computed field o usar un `model_validator(mode="before")` como fallback. Actualizar también `ROUTINE_COLUMNS`.

3. **Fuga futura por queries sin `tenant_id` en routines/runs**  
   `get_routine`, `list_routines`, `get_routine_by_name`, `delete_routine`, `update_routine`, `routine_run` usan mayormente solo `workspace_id`. Viola el contrato `Context(workspace_id, tenant_id)`. Corregir todas las queries e índices: `workspace_id AND tenant_id IS ?`.

4. **`is_active` no se valida en backend**  
   `_execute_skill_run` solo exige `approved_by`; una rutina aprobada pero inactiva puede ejecutarse vía `/run` o `@mention`. `/invoke`, `/run` y `@mention` deben rechazar `is_active=0` salvo endpoint admin explícito.

5. **Cambio de `preset_id` mantiene aprobación HITL**  
   El set sensible actual no incluye `preset_id`, `category`, posiblemente `name`. Cambiar modelo/proveedor de un agente aprobado es cambio ejecutable y debe limpiar `approved_by`.

6. **Budget cap se puede saltar en skills/agentes**  
   `execute_skill()` crea `CompletionRequest(spent_usd=0.0)`, a diferencia del chat normal que usa `sum_workspace_usage_cost`. Pasar gasto acumulado real para que skills/agentes respeten budget cap.

7. **Validación de `preset_id` incompleta**  
   No basta parsear `provider:model`. Validar en `RoutineCreate/Update` y runtime: provider conocido, modelo en `MODEL_ALLOWLIST`, provider permitido/habilitado. Usar `split(":", 1)`, no `split(":")`.

8. **Override provider/model puede ser bypass de política aprobada**  
   Si un agente fue aprobado para `ollama` pero el chat lo sobreescribe a `openai`, puede haber fuga de datos/costo. Definir política: override deshabilitado por defecto para routines aprobadas, o explícitamente permitido y auditado por rutina.

9. **`@mention` es ambiguo y limitado**  
   `get_routine_by_name` devuelve una fila no determinista si hay duplicados; además el regex no soporta espacios/acentos. Añadir slug único por workspace/tenant o responder `409 ambiguous`. `/invoke` por `routine_id` sí es necesario para el right-rail.

10. **Categoría no debe equivaler a permiso de ejecución**  
   El test propuesto “routine de otra categoría funciona igual” es riesgoso. `reference`/`template` no deberían ejecutarse desde chat salvo flag explícito `executable`. Limitar `/invoke` y `@mention` a `skill|agent|custom` o añadir `is_executable`.

11. **`persona_md` y catálogo no tienen gate de injection suficiente**  
   `skill_md` pasa por `compile_skill_md`, pero `persona_md` puede convertirse en system prompt vía fallback/import. Validar `persona_md`, catalog imports y frontmatter con canaries similares a SKILL.md antes de permitir aprobación.

12. **`tools_allowlist` y `trigger_json` no se validan como JSON en backend**  
   La UI planea textareas JSON, pero el modelo no valida esos campos. Añadir validadores: array JSON, strings no vacíos, límites, y política especial para `"*"`.

13. **Diseño frontend de `onInvokeTool` no encaja con estado actual**  
   `RightRail` es sibling de `SpaceView`, pero `activeChatId` vive dentro de `SpaceView`. App no puede invocar `/chats/{chat_id}/invoke` sin levantar `activeChatId/messages` a `App`, usar context/event bus, o mover Toolset dentro de `SpaceView`.

14. **`/invoke` debe persistir trazabilidad completa**  
   Verificar `chat_id` en contexto, persistir mensaje user real —no inventar `@Copywriter ...` si no lo escribió—, assistant message, `run_id`, `routine_id`, `routine_version/skill_version`, provider/model efectivo y audit event.

15. **Versionado contract-first no está cubierto**  
   Al editar rutina/skill/agente, incrementar o snapshotear `routine_version`/`skill_version`; al ejecutar, copiar esos valores a `routine_run`, usage/audit y, si posible, mensaje assistant. Si no, Gold/HITL queda sin trazabilidad reproducible.

16. **El plan de tests omite gates críticos**  
   Añadir tests para: inactive no ejecuta, preset/category edit limpia aprobación, budget cap en skill, duplicate @mention → 409, invalid preset → 422, malformed JSON fields → 422, category migration unknown → custom, cross-workspace/tenant isolation en routines.

## Recomendaciones

1. **Mantener `/invoke` separado, pero compartir núcleo**  
   Sí conviene `/chats/{chat_id}/invoke` por `routine_id` para right-rail. Implementarlo reutilizando una función común con `@mention` y `/routines/{id}/run`.

2. **Model selector: usar `/router/status`, no solo allowlist**  
   Mostrar solo providers `available=true`; si no, deshabilitar con `reason`. `model_allowlist` expuesto ya existe y es suficiente; no expone keys.

3. **No hacer llamadas LLM dentro de transacción SQLite**  
   Hoy `_execute_skill_run` ejecuta provider dentro de `transaction(conn)`. Para Fase 3, esto puede bloquear SQLite. Crear run → commit → llamada LLM → update run → audit.

4. **Índices sugeridos**  
   `idx_routine_category(workspace_id, tenant_id, category, is_active, approved_by)` y unique lógico para nombre/slug: `(workspace_id, tenant_id, lower(name))` o columna `slug`.

5. **Right-rail tabs con IDs estables**  
   No mezclar labels `"Agentes"` con checks `tab === "agents"`. Usar `{id,label}` para tabs.

6. **No insertar `@source:Título` sin backend**  
   Ese formato choca con el parser actual de `@mention`. O implementar referencias estructuradas a KB, o copiar texto/cita segura sin prefijo `@`.

7. **Factorizar UI de rutinas**  
   Extraer `RoutineForm`, `RoutineCard`, `RoutineList` para no duplicar lógica entre `RoutinesView`, `SkillsView`, `AgentsView` y Toolset.

8. **Actualizar knowledge graph al final**  
   El plan debe incluir `graphify update .` después de modificar código, según `AGENTS.md`.