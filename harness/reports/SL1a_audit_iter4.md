# Auditoría técnica preliminar — SpaceLoom `SL1a` asumido

## 0. Alcance

El prompt llegó con placeholders sin resolver: `[[PHASE]]`, `[[ITERATION]]`, `[[WRITTEN_FILES]]`, `[[AGENT_OUTPUTS]]`. Por el estado del repo, timestamps y archivos presentes, audité como fase:

> **SL1a — router mínimo + chat**

Revisé en modo solo lectura:

- `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md`
- `graphify-out/GRAPH_REPORT.md`
- `app/src/models.py`
- `app/src/db.py`
- `app/src/context.py`
- `app/src/audit.py`
- `app/src/api.py`
- `app/src/main.py`
- `app/src/router/*`
- `app/src/seed.py`
- `app/static/index.html`
- `app/static/js/app.jsx`
- `app/static/css/main.css`
- `app/tests/test_sl0_backend.py`
- `app/tests/test_sl1a_router.py`
- reportes previos en `harness/reports/`

**Limitación:** no ejecuté `pytest` ni `graphify update .` porque el entorno está en modo read-only y la política actual no permite aprobaciones. Esta auditoría es estática.

---

# 1. Resumen ejecutivo

La implementación actual de SL1a está bastante alineada con el DoD: hay chat funcional, router con proveedores cloud, Ollama opcional, fallback, provider allowlist, budget cap, ledger de uso, auditoría y UI conectada.

Los P1 señalados en auditorías previas parecen haber sido corregidos:

- `NoAllowedModel` ahora registra `usage_record` + audit.
- Fallos de mirror JSONL ya no rompen la respuesta API.
- El prompt base fue endurecido contra acciones irreversibles y hard facts sin fuente.
- El frontend ya muestra estado básico de router/costo acumulado.
- Hay tests nuevos para no-provider, no-allowed-model, budget, fallback, cross-workspace y audit mirror failure.

No encontré P0 activo. Quedan riesgos P2/P3 que conviene atender antes de SL1b/dogfood real.

---

# 2. Evaluación contra DoD SL1a

| Requisito SL1a | Estado | Comentario |
|---|---:|---|
| Router mínimo | **OK** | `app/src/router/` separa models, providers, registry, cost y engine. |
| 1 proveedor cloud | **OK** | Hay OpenAI, Anthropic y Google. Excede el mínimo sin caer en preset builder/backtest. |
| Ollama opcional | **OK** | Activable por env vars. |
| Fallback | **OK** | `Router.complete()` prueba candidatos por prioridad, salta modelos no permitidos y budget-exceeded estimado. |
| Costo visible | **OK parcial** | API devuelve costo; `/usage` existe; UI muestra provider/model/costo de última respuesta y spend/cap. Ver P2 sobre refresh. |
| Budget cap | **OK secuencial / P2 concurrente** | Funciona en flujo normal; queda riesgo de carrera si dos completions concurrentes pasan el cap. |
| Provider allowlist | **OK** | `SPACELOOM_PROVIDER_ALLOWLIST` + status endpoint. |
| Ledger de uso | **OK** | `usage_record` incluye `chat_id`, `attempts_json`, `source_version` y campos latentes. |
| Chat funcional | **OK** | CRUD de chats, mensajes y completions vía API + UI React UMD. |
| Sin overbuild | **OK** | No vi preset builder, backtest, optimizador o fábrica de niveles. |

---

# 3. Costuras contract-first

## 3.1 Campos latentes

**Estado: OK.**

`SCHEMA_VERSION = 4`. Las migraciones incluyen las costuras exigidas:

- `tenant_id`
- `user_id`
- `actor_id`
- `actor_role_at_decision`
- `routine_version`
- `skill_version`
- `schema_version`
- `source_version`
- `approved_by`

Tablas principales presentes:

- `workspace`
- `kb_source`
- `chat`
- `message`
- `draft`
- `audit_log`
- `routine`
- `routine_run`
- `usage_record`

`usage_record` está bien alineada con el futuro ledger tenant-aware.

## 3.2 Context layer

**Estado: OK.**

La capa `Context(workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision)` existe y se usa en helpers relevantes de DB.

Puntos positivos:

- `system_context()` está separado de contexto workspace.
- `require_scoped_workspace()` evita usar `__system__` para datos de app.
- Queries de `workspace`, `chat`, `message`, `usage_record` filtran por `workspace_id` y `tenant_id`.
- Por defecto no se confía en headers de cliente; solo se honran con `SPACELOOM_DEV_TRUST_HEADERS`.

## 3.3 AuditWriter

**Estado: OK.**

La costura `AuditWriter` cumple la intención:

- SQLite es fuente de verdad.
- `audit.jsonl` es mirror best-effort.
- `mirror()` captura excepciones.
- `_mirror_audit()` en API también evita romper la respuesta si falla el mirror.

Recomendación menor: hoy se tragan excepciones sin logging; conviene registrar warning para saber si el mirror local dejó de escribirse.

## 3.4 Router BYO-key → managed keys

**Estado: OK.**

- Keys vienen de env vars.
- No se persisten API keys en SQLite.
- Providers hacen lazy import de SDKs.
- Router abstrae provider/model/fallback/costo.
- Buena costura para mover luego a keys gestionadas.

---

# 4. Riesgos P0

## 4.1 HITL / irreversibles

**No hay P0 activo.**

No encontré endpoints de correo, borrado, scheduler, ejecución externa o acciones irreversibles. El botón “Enviar” envía mensaje al LLM, no correo ni acción externa.

**Recomendación SL1b:** cuando se habilite export/envío, mantener doble confirmación explícita y registrar `approved_by`.

## 4.2 Injection por contenido

**Sin P0 activo en SL1a.**

SL1a todavía no ingiere email/PDF/HTML/Excel/KB/SKILL.md. El prompt base fue endurecido:

- usuario como contenido no confiable;
- no irreversibles sin confirmación humana;
- no afirmar precios/SKU/stock/margen/lead time/equivalencias sin fuente autorizada vigente.

Eso es correcto para preparar SL1b, aunque los canaries reales quedan para SL2/SL3/SL5.

## 4.3 Fuga cross-workspace

**Estado: OK para SL1a.**

Las rutas de chat, mensajes y usage pasan por `Context` y helpers filtrados por workspace. Hay test explícito `test_cross_workspace_chat_isolation`.

No pude ejecutar tests, pero la implementación está alineada.

## 4.4 Dato inventado sin fuente

**No hay P0 activo, pero SL1a no debe confundirse con SL1b.**

SL1a no tiene KB ni citación, así que no puede garantizar “0 dato inventado” para drafts reales. El prompt reduce riesgo, pero la garantía contractual llega con mini-KB real + fuentes en SL1b/SL2.

---

# 5. Hallazgos y recomendaciones

## P2 — Corregir antes de SL1b o dogfood intensivo

### P2-01 — Budget cap no es completamente atómico ante concurrencia

En `api_create_completion()`, se reconsulta `current_spent` dentro del bloque final, pero SQLite no toma lock de escritura antes del `SELECT`. Dos completions concurrentes podrían leer el mismo gasto acumulado y ambas insertar luego.

**Impacto:** posible sobrepaso del cap en doble envío o concurrencia.

**Recomendación:**

- Usar `BEGIN IMMEDIATE` o helper transaccional específico para `recheck_spend + insert_usage`.
- Añadir test de concurrencia o simulación de carrera.
- Para SL1a single-user es aceptable; antes de uso real intensivo conviene cerrarlo.

---

### P2-02 — El chip de spend/cap en UI puede quedar stale después de enviar

`SpaceView` carga `/router/status` al cambiar workspace, pero tras una completion exitosa actualiza `lastMeta` y recarga mensajes, no necesariamente refresca `routerStatus`.

**Impacto:** la UI puede mostrar `spent_usd` viejo aunque el último costo sí aparezca.

**Recomendación:**

- Llamar `loadRouterStatus()` después de `sendMessage()` exitoso.
- También refrescar después de errores 429/budget.

---

### P2-03 — `router/status` puede marcar Ollama como disponible sin comprobar servidor local

`OllamaProvider.is_available()` solo valida enabled/config, no si `localhost:11434` responde. Si Ollama está enabled pero apagado, la UI puede sugerir disponibilidad y luego fallar/fallback.

**Recomendación:**

- Para SL1a puede bastar como “configured”.
- Para UX real, distinguir `configured` vs `reachable`.
- Hacer probe corto opcional en status o mostrar “Ollama habilitado, no verificado”.

---

### P2-04 — `attempts_json` no refleja todo el camino de fallback

En éxito con fallback, el ledger registra el intento exitoso, pero no necesariamente todos los proveedores saltados/fallidos desde el router.

**Impacto:** auditabilidad incompleta del routing decision.

**Recomendación:**

- Hacer que `Router.complete()` devuelva también `attempts`.
- Persistir razones: `not_available`, `not_allowed_model`, `estimated_budget_exceeded`, `provider_error`, `succeeded`.

---

### P2-05 — Falta warning claro de egreso a proveedor cloud

La UI dice que SL1a usa API key configurada y muestra proveedor, pero antes del primer envío convendría una señal explícita:

> “Este mensaje puede salir a OpenAI/Anthropic/Google según configuración.”

**Impacto:** local-first puede malinterpretarse como “todo queda local”.

**Recomendación:**

- Chip “Cloud” vs “Local”.
- Si provider activo no es Ollama, mostrar aviso discreto.
- Esto será importante antes de usar datos MWT reales.

---

### P2-06 — Hard-coded pricing/model tables deben tratarse como aproximadas

`cost.py` centraliza pricing y `PRICING_VERSION`, lo cual está bien. Pero los precios/model IDs de vendors cambian.

**Recomendación:**

- Mantener `PRICING_VERSION` visible en ledger.
- Antes de dogfood con costo real, validar model IDs y pricing vigente.
- Permitir override por env o config local para no tener que migrar código por cada cambio de vendor.

---

## P3 — Limpieza / no bloqueante

### P3-01 — `graphify` reporta ciclo `api.py -> main.py -> api.py`

Inspeccionando fuentes, `main.py` importa `api_router`, pero no vi import real de `main.py` desde `api.py`. Parece falso positivo/inferencia de graphify.

**Recomendación:** revisar con `graphify query` si interesa; no bloquea.

### P3-02 — Fallback HTML en `main.py` sigue diciendo “SL0”

La app principal es `SL1a`, pero el fallback HTML embebido todavía muestra “SL0 skeleton is running.”

**Recomendación:** actualizar texto fallback a SL1a o hacerlo genérico.

### P3-03 — Dependencia CDN para React/Babel

Para SL1a dev es aceptable. Para SL4 desktop instalable/offline, no.

**Recomendación:** vendorizar assets o introducir build local antes de empaque.

---

# 6. Marca / diseño

**Estado general: OK.**

Puntos positivos:

- Paleta centralizada en CSS vars.
- EB Garamond para voz/títulos.
- Geist para UI.
- Geist Mono para datos/estado.
- Iconos inline SVG con `currentColor`, `strokeWidth="1.75"`, round caps.
- Isotipo 3×3 tejido presente en boot/topbar/empty state.
- UI comunica “HITL absoluto” y evita apariencia de chatbot genérico.

Observaciones:

- Las sugerencias “Armar un draft contra el espacio” pueden sobreprometer si el usuario interpreta que ya hay KB/citas. Está mitigado parcialmente por chips “SL2a/SL3a”, pero convendría aclarar “SL1a: sin KB todavía”.
- Hex crudos en CSS tokens son correctos; hex en fallback HTML de `main.py` no bloquea, pero duplica marca.

---

# 7. Testing observado

`app/tests/test_sl1a_router.py` cubre bien:

- schema version 4;
- tabla `usage_record`;
- router status sin providers;
- CRUD de chats;
- modelo no permitido;
- completion con fake provider;
- fallback con modelo permitido por provider;
- allowlist de providers;
- budget cap acumulado;
- aislamiento cross-workspace;
- failed usage cuando no hay providers;
- audit mirror failure no rompe respuesta;
- `NoAllowedModel` registra usage + audit.

**Falta recomendado:**

1. Test concurrente/simulado de budget cap.
2. Test de refresh UI de `spent_usd` después de completion.
3. Test de attempts completos en fallback.
4. Test de provider cloud warning si se introduce en UI.

---

# 8. Veredicto preliminar

# `PASS`

PASS **preliminar estático** para SL1a: no encontré P0 activo ni P1 bloqueante en el estado actual del filesystem. Las costuras contract-first principales están presentes y el DoD técnico de router + chat está cubierto.

Condición práctica antes de cerrar formalmente el hito: ejecutar y archivar salida de:

```bash
cd app
python -m pytest -q
```

Y antes de SL1b/dogfood real: cerrar budget concurrency, warning cloud/local y mini-KB con fuentes.