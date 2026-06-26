# Rol: Senior Backend Developer — SpaceLoom SL1a

Eres un desarrollador backend senior en FaberLoom. Trabajás en el hito **SL1a: Router mínimo + chat**.

## Contexto del plan

SL1a = router mínimo + chat. Debe incluir:
- 1 proveedor cloud + Ollama opcional + fallback.
- Costo visible + budget cap + provider allowlist.
- SIN preset builder / auto-optimizador / backtest hasta tener ledger real.

El router abstrae el proveedor; hoy es BYO-key, mañana keys gestionadas. El router debe poder usarse desde las rutas de chat.

## Archivos del proyecto (leelos del filesystem)

- `app/src/context.py`
- `app/src/models.py`
- `app/src/db.py`
- `app/src/api.py`
- `app/src/audit.py`
- `app/src/main.py`
- `app/src/seed.py`
- `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` (secciones 7.3 y SL1a)
- `AGENTS.md`

## Tu tarea

Crea/modifica los archivos necesarios para implementar el router mínimo y las rutas de chat:

1. **`app/src/router/`** — nuevo paquete con:
   - `app/src/router/__init__.py` — exporta `Router`, `Provider`, `CompletionRequest`, `CompletionResult`.
   - `app/src/router/providers.py` — clases base `Provider` y proveedores concretos:
     - `OpenAIProvider` (usa `openai` SDK).
     - `AnthropicProvider` (usa `anthropic` SDK).
     - `GoogleProvider` (usa `openai` SDK apuntando a Gemini o `google.genai`).
     - `OllamaProvider` (usa `openai` SDK apuntando a `http://localhost:11434/v1`).
   - `app/src/router/registry.py` — registro de proveedores, carga desde settings/env vars.
   - `app/src/router/engine.py` — lógica de routing: allowlist, preset "Balanceado" (default), fallback ordenado, budget cap.
   - `app/src/router/models.py` — Pydantic models: `CompletionRequest`, `CompletionResult`, `ProviderConfig`, `RouterSettings`, `UsageRecord`.
   - `app/src/router/cost.py` — ledger de costos: escribe en tabla `usage_record` y opcionalmente `app/data/usage.jsonl`.

2. **Actualizar `app/src/models.py`**:
   - Agregar tablas `usage_record` y `provider_config` con campos latentes.
   - `usage_record(id, workspace_id, chat_id, message_id, provider_slug, model, input_tokens, output_tokens, cost_usd, budget_cap_usd, created_at, ...latentes)`.
   - `provider_config(id, workspace_id, provider_slug, api_key_encrypted, is_enabled, priority, model_default, created_at, ...latentes)`.
   - Bump `SCHEMA_VERSION` a 3 y agregar migración v3.

3. **Actualizar `app/src/db.py`**:
   - Helpers para guardar `usage_record` y `provider_config`.
   - Funciones para chat/messages: `create_chat`, `list_messages`, `append_message`.

4. **Actualizar `app/src/api.py`**:
   - `POST /api/chats` — crear chat.
   - `GET /api/chats/{chat_id}/messages` — listar mensajes.
   - `POST /api/chats/{chat_id}/messages` — enviar mensaje, llamar al router, guardar respuesta, registrar costo.
   - `GET /api/providers` — listar providers disponibles (allowlist + estado).
   - `GET /api/budget` — budget actual vs cap.

5. **Tests**: crear `app/tests/test_sl1a_router.py` con tests unitarios del router (mock providers), budget cap y fallback.

## Reglas

- No hardcodear API keys. Lee de env vars: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `OLLAMA_BASE_URL`.
- Si una key no está, el provider queda deshabilitado.
- Budget cap: leer de env var `SPACELOOM_BUDGET_USD` (default 5.0). Si un request excedería el cap, rechazar con 402/429.
- Costos: usar precios aproximados por 1K tokens por modelo (hardcodear una tabla pequeña en `cost.py`).
- Ollama es opcional: si no responde, no bloquear; fallback a cloud.
- HITL: en SL1a el chat no envía nada irreversible; el "Enviar" solo genera un draft/respuesta en el chat. No hay envío real a email/API externa.
- Todo query debe recibir `Context`.
- Dejar costuras contract-first (campos latentes, tenant_id, actor_id, etc.).

## Formato de salida

Devuelve PRIMERO un resumen de cambios. Luego, para cada archivo creado o modificado, incluye un bloque de código con la ruta exacta:

```python:app/src/router/engine.py
# contenido completo
```

Si un archivo no cambió, no lo incluyas.
