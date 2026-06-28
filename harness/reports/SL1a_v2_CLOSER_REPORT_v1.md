# Reporte de cierre SL1a v2 — ajustes de superficie (§8)

**Fecha:** 2026-06-27  
**Agente:** Kimi Code CLI  
**Loop CLOSER:** §5 AUDIT → PLAN → IMPLEMENT → TEST → GATE → REPORTE

## Estado

Ajustes post-SL1a v2 **CERRADOS**. No se reabrió el gate de SL1a; son cambios quirúrgicos de superficie + features.

## 1. Superficie de providers: OpenAI + Kimi

- `_VISIBLE_PROVIDER_SLUGS` en `app/src/api.py` cambió de `{openai, ollama}` a `{openai, kimi}`.
- Backend sigue soportando todos los providers (`openai`, `anthropic`, `google`, `kimi`, `ollama`); solo cambia qué se muestra en la UI.
- `PATCH /providers/{slug}` sigue aceptando providers ocultos (test `test_ollama_remains_configurable_when_hidden`).
- Kimi aparece en Settings con los mismos campos que OpenAI: API key, modelo default, prioridad, habilitado, base URL.

## 2. Router mínimo intacto

- No se agregó clasificador de complejidad, auto-optimizador ni memoria cross-conversación.
- El router sigue eligendo por prioridad + allowlist + budget cap + fallback.
- Mensaje de "sin proveedores" actualizado a español:
  > "Ningún proveedor disponible: configura OpenAI o Kimi (API key)."
- **Fallback probado:** `test_fallback_uses_kimi_when_openai_has_no_key` verifica que, si OpenAI no tiene key y Kimi sí, el router solo presenta a Kimi como disponible.

## 3. Fix UI: cards de provider y API keys

- Se eliminó el overflow horizontal de las cards:
  - `.provider-key-row` usa `display: flex; min-width: 0`.
  - El input de API key tiene `flex: 1 1 auto; min-width: 0; box-sizing: border-box`.
  - La key guardada se muestra con `word-break: break-all` y fuente monoespaciada.
- Placeholder del input cambia a "Key guardada · actualizar" cuando ya hay key, evitando texto largo.

## 4. Gestión de conversaciones

### Renombrar

- Doble clic en el título de un chat o botón de editar → input inline.
- `PATCH /workspaces/{id}/chats/{chat_id}` con `ChatUpdate`.
- Scoped por `(workspace_id, tenant_id)`.
- Auto-titulado opcional: al enviar el primer mensaje en un chat llamado "Nueva conversación", se renombra con las primeras 6 palabras del mensaje.

### Borrar

- Botón de papelera en cada tarjeta de chat.
- `DELETE /workspaces/{id}/chats/{chat_id}` requiere `confirmation_token` (HITL absoluto, doble confirmación).
- Modal `DeleteConfirmModal` reutilizado; el usuario debe copiar el token.
- Borra solo el chat y sus mensajes (cascade en DB); no toca otros chats ni workspaces.
- Multi-tenant: filtra por `tenant_id`.

## 5. Tests

Nuevos tests en `app/tests/test_sl1a_router_endpoints.py`:

- `test_provider_surface_visible_is_openai_and_kimi`
- `test_ollama_remains_configurable_when_hidden`
- `test_fallback_uses_kimi_when_openai_has_no_key`
- `test_rename_conversation`
- `test_delete_conversation_requires_confirmation`
- `test_delete_conversation_tenant_isolation`

Tests actualizados:

- `test_list_providers_masks_keys`
- `test_provider_config_exposes_requires_api_key`

## Resultados de test

```text
pytest app/tests/test_sl1a_router.py app/tests/test_sl1a_router_endpoints.py -q
34 passed, 1 warning

pytest app/tests -q
202 passed, 1 warning
```

Baseline SL4: `197 passed`.  
Incremento neto: **+5 tests**.

## Archivos modificados

- `app/src/api.py` — `_VISIBLE_PROVIDER_SLUGS`, endpoints `PATCH/DELETE /chats/{id}`.
- `app/src/db.py` — `update_chat`, `delete_chat`.
- `app/src/models.py` — `ChatUpdate`.
- `app/src/router/engine.py` — mensaje de fallback en español.
- `app/static/js/app.jsx` — provider cards, selector filtrado, ChatList con rename/delete, SpaceView con handlers.
- `app/static/js/icons.jsx` — icono `edit`.
- `app/static/css/main.css` — estilos anti-overflow para provider cards y chat actions.
- `app/tests/test_sl1a_router_endpoints.py` — tests de superficie, fallback, rename/delete.
- `harness/reports/SL1a_v2_CLOSER_REPORT_v1.md` — este reporte.

## Restricciones respetadas

- `ENT_OPS_STATE_MACHINE` y `PLB_ORCHESTRATOR` no modificados.
- No se inventaron datos MWT reales.
- Ollama y demás providers no se eliminaron; solo se ocultaron de la UI.
