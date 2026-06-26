# Diseño Router SL1a

Crea los archivos base del router en `app/src/router/` para SpaceLoom SL1a.

## Archivos a crear

1. `app/src/router/models.py`:
   - `CompletionRequest`: `messages: list[dict]`, `model: str | None`, `provider_slug: str | None`, `temperature: float = 0.7`, `max_tokens: int | None`.
   - `CompletionResult`: `content: str`, `model: str`, `provider_slug: str`, `input_tokens: int`, `output_tokens: int`, `cost_usd: float`, `duration_ms: int`.
   - `ProviderConfig`: `provider_slug: str`, `api_key: str | None`, `base_url: str | None`, `model_default: str`, `priority: int`, `is_enabled: bool`.
   - `RouterSettings`: `budget_cap_usd: float = 5.0`, `provider_allowlist: list[str] | None = None`.
   - `UsageRecord`: Pydantic model para tabla usage_record.

2. `app/src/router/cost.py`:
   - Tabla pequeña de precios por modelo (USD por 1K tokens): gpt-4o, gpt-4o-mini, claude-3-5-sonnet, gemini-1.5-pro, llama3.1 (Ollama = 0).
   - `estimate_cost(model, input_tokens, output_tokens) -> float`.
   - `get_default_model(provider_slug) -> str`.

3. `app/src/router/providers.py`:
   - Clase abstracta `Provider` con `complete(request) -> CompletionResult`.
   - `OpenAIProvider`, `AnthropicProvider`, `GoogleProvider`, `OllamaProvider`.
   - Cada provider usa su SDK o HTTP; si falla, lanza `ProviderError`.
   - Lee API keys de env vars; si no hay key, `is_available() -> False`.

4. `app/src/router/engine.py`:
   - Clase `Router` con `__init__(settings, providers)`.
   - `complete(request) -> CompletionResult`: filtra allowlist, ordena por prioridad, intenta providers en orden, fallback.
   - `check_budget(estimated_cost) -> bool`.
   - `list_available_providers() -> list[str]`.

5. `app/src/router/__init__.py`: exporta `Router`, `Provider`, `CompletionRequest`, `CompletionResult`, `ProviderError`.

6. `app/src/router/registry.py`:
   - `build_router()` que lee env vars, crea providers disponibles y devuelve `Router`.

## Reglas

- Soportar `openai` y `anthropic` como dependencias; Google usar el SDK de OpenAI apuntando a Gemini.
- Ollama opcional: base URL `http://localhost:11434/v1`, model default `llama3.1`.
- Si un provider no está configurado, se salta silenciosamente.
- Preset default "Balanceado" = usa providers en orden de prioridad.
- No escribir API keys en archivos.

## Formato

Resumen + bloques de código con ruta exacta.
