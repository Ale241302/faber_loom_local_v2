---
id: SPEC_FB_ENVELOPE_ENFORCEMENT_v1
title: Enforcement del envelope de routing (compliance con dientes)
status: DRAFT
version: 1.0
domain: FaberLoom
etapa: E5
created: 2026-07-14
last_review: 2026-07-14
---

# Enforcement del envelope de routing

## Resumen

`routing_preset.envelope_json` declara restricciones de compliance (jurisdicciones,
proveedores permitidos y denegados, política de retención). Hoy se guarda, se valida
y se muestra — pero **no se enforcea**. Un tenant que declara `providers_deny: ["kimi"]`
puede terminar servido por Kimi sin error ni warning.

Este spec cierra ese agujero. No construye la fábrica de arquetipos: eso va en un spec
propio, encima de este piso.

## El problema, con evidencia

### El envelope es decorativo

Grep completo sobre `app/src`: `providers_deny`, `jurisdictions`, `data_collection` y
`byo_keys` son leídos por **cero** líneas de runtime. `providers_allow` se lee en 4
líneas, todas dentro de `resolve_routing_preset` (`db.py:4244,4250,4261,4271,4280`), y
no como filtro sino como fuente de un `next(...)` con fallback incondicional a
`providers_allow[0]` — una pista para adivinar una etiqueta, no un gate.

### La causa raíz: el cable suelto

`build_router` (`registry.py:190-218`) **ya acepta** `provider_allowlist`:

```python
settings = RouterSettings(
    provider_allowlist=provider_allowlist
    if provider_allowlist is not None
    else _env_csv("FABERLOOM_PROVIDER_ALLOWLIST"),
)
```

Los tres call sites del path de routines (`api.py:2295`, `api.py:2869`, `api.py:5987`)
lo llaman **sin ese argumento**. Cae a la env var global. Si la env var no está seteada,
`_env_csv` devuelve `None`, y entonces:

```python
def _provider_allowed(self, provider: Provider) -> bool:   # engine.py:205
    allowlist = self.settings.provider_allowlist
    if allowlist is None:
        return True                                        # engine.py:208 — allow-all
    return provider.provider_slug in allowlist
```

**El guard existe y está en el lugar correcto.** `_ordered_providers` (`engine.py:190-203`)
ya filtra por `_provider_allowed` antes de armar la lista de candidatos, así que el
`continue` ante `ProviderError` (`engine.py:164`) solo puede recorrer proveedores
permitidos. El motor está bien. Lo que falta es que alguien le pase el envelope del tenant.

### El exploit concreto

Tenant con `providers_allow: ["anthropic","openai"]`, `providers_deny: ["kimi"]`, modo
`balanceado`. `resolve_routing_preset` devuelve `openai/gpt-4o`.
`_validate_completion_choice` pasa. `Router.complete` (`engine.py:137`) itera candidatos;
como `provider_allowlist is None`, los candidatos son **todos** los proveedores con key
configurada. OpenAI lanza `ProviderError` (rate limit, 500, key vencida) o revienta el
budget check (`engine.py:154`) → `continue` → Kimi. `_resolve_model_for_provider`
(`engine.py:211`) ve que `gpt-4o` no está en el allowlist de Kimi y cae a su
`model_default` → la llamada se dispara contra Moonshot, en China, con el prompt del
tenant. El run figura como exitoso.

Esto no es un edge case: es el comportamiento de fallback diseñado ante cualquier fallo
transitorio de OpenAI.

### Estado en producción (VPS 187.77.218.102, verificado 2026-07-14)

- `FABERLOOM_PROVIDER_ALLOWLIST` **vacía** en el contenedor `faberloom-api` → allow-all activo.
- `routing_preset` tiene **0 filas** → nadie declaró un envelope todavía.
- Kimi (CN) y OpenAI (US) ambos configurados y habilitados.

Conclusión: la exposición es **latente, no activa**. No hay promesa de compliance siendo
violada porque nadie la hizo aún. El primer tenant que escriba `providers_deny: ["kimi"]`
y confíe en eso queda violado desde el minuto uno. Llegamos antes de la promesa.

### Tres fuentes de verdad para la misma pregunta

| Fuente | Grano | ¿Tiene dientes? |
|---|---|---|
| `FABERLOOM_PROVIDER_ALLOWLIST` (env) | global | Sí |
| `workspace_routing_policy.provider_allowlist_json` (`models.py:903`) | workspace | Sí (`_validate_manual_choice`, `api.py:1377`) |
| `routing_preset.envelope_json` (`models.py:1438`) | tenant | **No** |

El único que se llama "compliance" es el único sin enforcement. Esa duplicación es la
causa raíz, y el diseño la colapsa en una sola función de resolución.

## Alcance

**Dentro:**
- Capa 0: el envelope del tenant enforceado en el engine, fail-closed.
- Capa 0.5: jurisdicción como metadata estática del proveedor.
- Fix del par incoherente en `resolve_routing_preset`.

**Fuera (spec propio):**
- La fábrica de arquetipos (tabla `archetype`, panel, copy-on-create hacia routine).
- `task_overrides` muerto: el resolver acepta `task_class` pero el runtime nunca lo pasa
  (`api.py:3082`), así que la rama en `db.py:4247` es inalcanzable y los 4 presets semilla
  traen `task_overrides: {}`. Es una feature inerte, no una fuga. Se documenta aquí y se
  arregla aparte.
- `_VISIBLE_PROVIDER_SLUGS = {"openai","kimi"}` (`api.py:3339`) oculta anthropic, google y
  ollama de la UI aunque `build_router` los registra. Hoy inocuo (sin key,
  `is_available()` es falso), pero es un riesgo latente: una key por env var haría aparecer
  un proveedor sirviendo tráfico que el admin no ve ni puede apagar. Se documenta; el fix
  va aparte.

**Sin migración.** Los proveedores se registran en Python (`registry.py:224-389`) y las
keys viven en `providers.json` cifrado con Fernet (`config_store.py:143`), no en SQL. No
hay fila de proveedor a la cual agregarle columna. `SCHEMA_VERSION` se queda en 48
(`models.py:12`).

## Diseño

### 1. Jurisdicción como constante

En `app/src/router/cost.py`, junto a `DEFAULT_MODELS` (`cost.py:42`) y `MODEL_ALLOWLIST`
(`cost.py:56`), que ya son tablas por slug:

```python
PROVIDER_JURISDICTION: dict[str, str] = {
    "openai": "US",
    "anthropic": "US",
    "google": "US",
    "kimi": "CN",
    "ollama": "local",
}
```

Los cinco proveedores que `build_router` registra. Un slug ausente del dict se trata como
jurisdicción desconocida y **se deniega** cuando hay `jurisdiction_allowlist` activo —
fail-closed también acá: un proveedor nuevo no se cuela por olvido.

Va en código y no en DB porque la jurisdicción es una propiedad del vendor, no una
preferencia del tenant: Moonshot está en China para todos. El precedente en el codebase es
`requires_api_key: bool = True` (`providers.py:49`), otra propiedad estática por vendor.

### 2. `RouterSettings` gana dos campos

`app/src/router/models.py:60-64`, hoy dos campos:

```python
class RouterSettings(BaseModel):
    budget_cap_usd: float = Field(default=5.0, ge=0.0)
    provider_allowlist: list[str] | None = None
    provider_denylist: list[str] | None = None        # nuevo
    jurisdiction_allowlist: list[str] | None = None   # nuevo
```

`None` significa "sin restricción" en allowlist/jurisdicción (compatible con el
comportamiento actual), y "sin denegados" en denylist.

### 3. Una sola función de resolución

Nueva función en `app/src/routing/policy.py`, junto a `get_effective_allowlists`
(`policy.py:106`):

```python
class RoutingConstraints(BaseModel):
    provider_allowlist: list[str] | None = None
    provider_denylist: list[str] | None = None
    jurisdiction_allowlist: list[str] | None = None

def resolve_effective_routing_constraints(ctx, conn, preset_id) -> RoutingConstraints
```

Compone, en este orden:

```
provider_allowlist = env global
                   ∩ workspace_routing_policy.provider_allowlist
                   ∩ envelope.providers_allow
provider_denylist  = envelope.providers_deny
jurisdiction_allowlist = envelope.jurisdictions
```

Intersección: `None` en cualquier fuente significa "esa fuente no restringe" y se saltea.
Si todas son `None`, el resultado es `None` y no hay restricción — idéntico a hoy.

El deny **no** se resta acá: se pasa aparte y se aplica en el guard, para que gane sobre
todo siempre, incluso sobre un `provider_slug` pedido explícitamente por el caller. Esto
cumple `SPEC_FB_ROUTING_PRESETS_v1.md:45` ("el blocklist gana sobre allow"), que hoy no
existe en código.

Los tres call sites (`api.py:2295`, `2869`, `5987`) pasan a llamar:

```python
constraints = resolve_effective_routing_constraints(ctx, conn, routine.get("preset_id"))
router = build_router(
    user_id=ctx.user_id, tenant_id=ctx.tenant_id, byo_mode=byo_mode,
    provider_allowlist=constraints.provider_allowlist,
    provider_denylist=constraints.provider_denylist,
    jurisdiction_allowlist=constraints.jurisdiction_allowlist,
)
```

### 4. El guard

`engine.py:205`, único punto de estrangulamiento — todos los paths (`complete`, `estimate`,
`has_available_provider`, `list_available_providers`, y el endpoint de status vía
`router.provider_allowed`) pasan por acá:

```python
def _provider_allowed(self, provider: Provider) -> bool:
    slug = provider.provider_slug

    # deny gana sobre todo, siempre
    if self.settings.provider_denylist and slug in self.settings.provider_denylist:
        return False

    if self.settings.jurisdiction_allowlist is not None:
        jurisdiction = router_cost.PROVIDER_JURISDICTION.get(slug)
        if jurisdiction not in self.settings.jurisdiction_allowlist:
            return False   # desconocido => denegado

    allowlist = self.settings.provider_allowlist
    if allowlist is None:
        return True
    return slug in allowlist
```

No hace falta tocar `_ordered_providers` ni el loop de `complete`: ya filtran por este
guard antes de iterar.

### 5. Fail-closed

Con el guard alimentado, si el filtro deja la lista de candidatos vacía, `complete` ya
levanta el error de "no hay proveedor disponible" (`engine.py:131`) en vez de devolver una
respuesta. El fail-closed cae solo — no requiere código nuevo, solo que el guard reciba los
datos.

Cambio de contrato explícito: **un tenant con envelope restrictivo verá errores donde antes
veía respuestas.** Es intencional. Una respuesta que violó compliance es peor que ninguna
respuesta. Rollout directo (sin fase shadow): `routing_preset` tiene 0 filas en el VPS y
los defaults de `_default_preset_envelope` (`db.py:3908`) son permisivos, así que el impacto
inmediato es nulo. Los 4 presets semilla sí traen `providers_allow` restrictivo, así que el
primer tenant aprobado ya queda gobernado — que es el punto.

El mensaje de error debe nombrar la restricción que disparó el bloqueo (deny / jurisdicción
/ allowlist) y el proveedor afectado, para que un admin pueda diagnosticar sin leer logs.

### 6. Fix del par incoherente

`resolve_routing_preset` (`db.py:4250,4261,4271,4280`) usa `providers_allow` como fuente de
un `next(...)` con fallback a `providers_allow[0]`. Con `providers_allow: ["kimi"]` y modo
`balanceado`, `preferred="gpt-4o"` no matchea ningún proveedor permitido y devuelve el par
inválido `kimi/gpt-4o` — un modelo que ese proveedor no puede servir.

Invertir el orden: elegir modelo **dentro** de los proveedores permitidos, en vez de elegir
modelo y después inventarle proveedor. Si ningún proveedor permitido sirve un modelo para
esa curva, devolver `None` y dejar que el router falle cerrado, en vez de fabricar un par
inválido.

### 7. Auditoría

`db.py:1680` ya registra `byo_mode_at_run` / `platform_key_used` — el sistema loguea el hecho
relevante para compliance después de ocurrido, pero nunca gatea sobre él. Con este spec el
gate existe; el bloqueo se escribe al audit con `AuditWriter` (patrón obligatorio de
`AGENTS.md:22-33`) como `routing.provider_blocked`, con la restricción que lo causó.

## Testing

Patrón de `app/tests/test_e3_5_presets.py` (pytest + `TestClient`, fixture con DBs por test
en `tmp_path`). Archivo nuevo: `app/tests/test_e5_envelope_enforcement.py`.

El test mandatorio — el que hoy falla y prueba que el agujero se cerró:

1. **`test_denied_provider_never_serves_on_fallback`**: tenant con
   `providers_deny: ["kimi"]`, OpenAI mockeado para lanzar `ProviderError`. Debe recibir un
   error explícito, **no** una respuesta de Kimi. Es el inverso del
   `test_cross_tenant_isolation` que ya existe (`test_e3_5_presets.py:225`).

Complementarios:

2. `test_jurisdiction_filter_blocks_cn`: envelope `jurisdictions: ["US","EU"]` → Kimi (CN)
   excluido de candidatos aunque tenga key y esté habilitado.
3. `test_deny_beats_allow`: `providers_allow: ["kimi"]` + `providers_deny: ["kimi"]` → Kimi
   denegado.
4. `test_deny_beats_explicit_caller_override`: caller pide `provider_slug="kimi"` con
   `providers_deny: ["kimi"]` → denegado.
5. `test_unknown_provider_denied_under_jurisdiction_allowlist`: slug ausente de
   `PROVIDER_JURISDICTION` con jurisdicción activa → denegado.
6. `test_empty_envelope_preserves_current_behavior`: sin preset y sin env var → allow-all,
   idéntico a hoy. Protege contra romper a los tenants sin envelope.
7. `test_no_incoherent_pair`: `providers_allow: ["kimi"]` + modo `balanceado` → nunca
   devuelve `kimi/gpt-4o`.

## Archivos afectados

| Concern | Archivo | Ancla |
|---|---|---|
| Constante de jurisdicción | `app/src/router/cost.py` | junto a `MODEL_ALLOWLIST` (`:56`) |
| `RouterSettings` | `app/src/router/models.py` | `:60-64` |
| `build_router` (2 params nuevos) | `app/src/router/registry.py` | `:190-218` |
| Guard | `app/src/router/engine.py` | `_provider_allowed` `:205` |
| Resolución compuesta | `app/src/routing/policy.py` | junto a `get_effective_allowlists` `:106` |
| Call sites | `app/src/api.py` | `:2295`, `:2869`, `:5987` |
| Fix par incoherente | `app/src/db.py` | `resolve_routing_preset` `:4209-4287` |
| Tests | `app/tests/test_e5_envelope_enforcement.py` | nuevo |

Sin migración. Sin cambios de UI. Sin cambios en `postgres_rls_policies.sql`.

Post-implementación: `graphify update .` (`AGENTS.md:43`).

## Hallazgos colaterales (no se arreglan acá)

1. **`task_overrides` inerte** — `resolve_routing_preset` acepta `task_class` pero
   `api.py:3082` nunca lo pasa; la rama de `db.py:4247` es inalcanzable. Irónicamente
   `routine.category` sí está disponible en ese call site: se escribe como `task_type` en el
   run tres líneas después (`api.py:3198`).
2. **`seed_routing_presets` miente** — el docstring (`db.py:3981`) dice que bumpea versión
   cuando cambia el template; el código hace `continue` sobre cualquier fila existente
   (`db.py:3994`). Los updates de template nunca llegan a tenants existentes.
3. **Preset `conservador` con curva `sport`** (`db.py:3936`) — contradice su propia
   descripción ("default seguro para onboarding"). Parece copy-paste.
4. **`envelope.byo_keys` muerto** — BYO se resuelve desde el config cascade
   (`routing.byo_mode`, `api.py:1327`), no desde el envelope. Setear `byo_keys: true` no
   cambia nada.
5. **`_VISIBLE_PROVIDER_SLUGS`** (`api.py:3339`) oculta 3 de los 5 proveedores registrados
   de la UI de Admin.
6. **El audit E3 verificó lo incorrecto** — `AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md:405`
   afirma que un preset con `providers_allow=["anthropic"]` devuelve `anthropic/claude-3-5-sonnet`.
   Es cierto, y es el problema: verificó el valor de retorno de un resolver, no que la
   llamada esté vedada.

## Decisiones registradas

| Decisión | Elección | Razón |
|---|---|---|
| Rollout | Fail-closed directo, sin fase shadow | 0 filas en `routing_preset` en prod; impacto inmediato nulo |
| `task_overrides` | Fuera de alcance | Feature inerte, no fuga; ortogonal a compliance |
| Jurisdicción | Constante en código | Propiedad del vendor, no del tenant; evita migración |
| Deny | Aplicado en el guard, no en la composición | Debe ganar sobre el override explícito del caller |
| Proveedor sin jurisdicción conocida | Denegado | Fail-closed: un proveedor nuevo no se cuela por olvido |
