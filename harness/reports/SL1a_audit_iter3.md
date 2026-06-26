# Auditoría técnica preliminar — SpaceLoom SL1a

## 0. Alcance y advertencias

El prompt llegó con placeholders sin resolver: `[[PHASE]]`, `[[ITERATION]]`, `[[WRITTEN_FILES]]`, `[[AGENT_OUTPUTS]]`. Por el estado del repo, los archivos recientes y el contenido del graph report, audité como fase:

> **SL1a — router mínimo + chat**

Leí en modo solo lectura:

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
- `app/static/js/app.jsx`
- `app/static/css/main.css`
- `app/static/index.html`
- `app/tests/test_sl0_backend.py`
- `app/tests/test_sl1a_router.py`
- `harness/reports/SL1a_audit_iter2.md`

**No pude ejecutar pytest**: la política actual bloqueó la invocación de `python -m pytest`. Por tanto esta auditoría es de lectura estática + revisión de tests existentes, no verificación runtime.

---

## 1. Evaluación contra DoD SL1a

Según la enmienda v1.1, SL1a debe entregar:

> **router mínimo + chat:** 1 proveedor cloud + Ollama opcional + fallback + costo visible + budget cap + provider allowlist. Sin preset builder / auto-optimizador / backtest.

| Requisito | Estado | Comentario |
|---|---:|---|
| Chat funcional | **Implementado** | CRUD de chats, mensajes y completions en API; UI conectada al backend. |
| Proveedor cloud | **Implementado** | OpenAI, Anthropic y Google. Excede el mínimo, pero no veo overbuild tipo preset-builder/backtest. |
| Ollama opcional | **Implementado** | `SPACELOOM_ENABLE_OLLAMA` / `SPACELOOM_OLLAMA_ENABLED`. |
| Fallback | **Implementado** | El router intenta providers por prioridad y cambia modelo por provider según allowlist. |
| Costo visible | **Parcial / suficiente para SL1a** | API devuelve costo, `/usage` existe, UI muestra costo de última respuesta. Falta previsualizar proveedor/costo antes de enviar. |
| Budget cap | **Implementado con reservas** | Hay cap estimado y post-respuesta; se reconsulta gasto antes de persistir. Queda riesgo de concurrencia. |
| Provider allowlist | **Implementado** | `SPACELOOM_PROVIDER_ALLOWLIST` + status endpoint. |
| Ledger de uso | **Implementado** | `usage_record` con `chat_id`, `attempts_json`, `source_version`. |
| Tests | **Presentes** | Cobertura amplia; no ejecutable en esta sesión por política. |

**Conclusión DoD:** SL1a está sustancialmente implementado. No veo P0 activo, pero no doy `PASS` porque hay bugs/riesgos P1/P2 y no pude verificar tests.

---

## 2. Costuras contract-first

## 2.1 Campos latentes

**Estado: OK.**

`SCHEMA_VERSION = 4`. Las migraciones cubren tablas base y SL1a con campos contract-first:

- `tenant_id`
- `user_id`
- `actor_id`
- `actor_role_at_decision`
- `routine_version`
- `skill_version`
- `schema_version`
- `source_version`
- `approved_by`

Tablas relevantes presentes:

- `workspace`
- `kb_source`
- `chat`
- `message`
- `draft`
- `audit_log`
- `routine`
- `routine_run`
- `usage_record`

`usage_record` también incluye la superficie latente, más `chat_id` y `attempts_json`, lo cual es correcto para un ledger futuro.

## 2.2 Context layer

**Estado: OK con una observación.**

La capa `Context(workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision)` existe y los helpers de DB relevantes reciben `ctx`.

Puntos positivos:

- `system_context()` está separado de contexto de workspace.
- `require_scoped_workspace()` bloquea uso accidental de `__system__` para datos de aplicación.
- Las queries de `workspace`, `chat`, `message`, `usage_record` filtran por `workspace_id` y `tenant_id`.
- Por defecto no se confía en headers de cliente; solo se honran con `SPACELOOM_DEV_TRUST_HEADERS`.

Observación menor:

- El endpoint de status del router usa detalles internos/estado de providers directamente. No es grave, pero convendría centralizar status en una API pública del router para no acoplar `api.py` a internals.

## 2.3 AuditWriter

**Estado: mejorado / mayormente OK.**

La costura `AuditWriter` existe y declara correctamente:

- SQLite como fuente de verdad.
- JSONL como mirror best-effort.
- Inserción del audit row dentro de la transacción de llamada.

Se corrigió el problema visto en auditoría previa: ahora `_mirror_audit()` envuelve `audit_writer.mirror(event)` en `try/except`, y `mirror()` también captura errores. Bien.

Riesgo restante:

- Al tragar excepciones sin logging, se puede perder visibilidad de que el mirror JSONL falló. Para dogfood local está aceptable; para siguientes hitos conviene loguearlo.

## 2.4 Router BYO-key → managed keys

**Estado: OK.**

- API keys vienen de env vars.
- No se persisten keys en SQLite.
- Providers importan SDKs lazy.
- Router abstrae provider/model/costo/fallback.
- El diseño deja una costura razonable para mover BYO-key a keys gestionadas después.

---

## 3. Riesgos P0

## 3.1 HITL / acciones irreversibles

**No hay P0 activo confirmado.**

No encontré endpoints de correo, borrar, ejecutar acciones externas, scheduler o side effects irreversibles. El botón “Enviar” en la UI envía un mensaje al LLM, no correo.

Recomendación:

- Antes de SL1b/dogfood real, aclarar en UI si el mensaje saldrá a proveedor cloud. “Local-first” no debe confundirse con “no sale de la máquina” si se usa OpenAI/Anthropic/Google.

## 3.2 Injection por contenido

**No aplica plenamente a SL1a, pero el prompt base es débil para SL1b.**

SL1a no ingiere email/PDF/HTML/Excel/KB/SKILL.md. El contenido externo aún no existe, así que no hay P0 activo de injection por documentos.

Pero `_SYSTEM_PROMPT` es:

```text
You are SpaceLoom, a helpful operations assistant.
```

Eso es insuficiente para el salto a SL1b/SL2. Debe endurecerse antes de drafts reales.

Recomendación mínima:

- Declarar que contenido de usuario/KB/email/PDF/Excel/SKILL.md es dato no confiable, no instrucciones.
- Prohibir acciones irreversibles sin HITL.
- Prohibir afirmar precio/SKU/stock/margen/lead time/equivalencia sin fuente autorizada y vigente.
- Si falta fuente o vigencia, pedir confirmación.

## 3.3 Fuga cross-workspace

**Estado: OK para SL1a.**

La implementación filtra por `ctx.workspace_id` en chats, mensajes y usage. Hay test explícito `test_cross_workspace_chat_isolation`.

No pude ejecutar el test, pero la implementación está alineada con el riesgo P0.

## 3.4 Dato inventado sin fuente

**No aplica completamente a SL1a, pero hay riesgo de sobrepromesa UX.**

SL1a no tiene KB/citaciones; por tanto no puede cumplir “cero dato inventado” para drafts con datos duros. La UI ya habla de draft y de “espacio”, pero todavía no hay fuentes reales.

Recomendación:

- Mantener SL1a claramente etiquetado como “chat/router sin KB”.
- No considerar dogfood real hasta SL1b: mini-KB real + HITL mínimo + export/envío aprobado.

---

## 4. Hallazgos concretos

## P1 — Corregir antes de `PASS`

### P1-01 — `NoAllowedModel` puede salir sin usage/audit

En `api_create_completion()`, si `router.complete()` lanza `NoAllowedModel`, el código hace:

```python
except NoAllowedModel as exc:
    error = exc.detail
    attempts.append(...)
    raise HTTPException(...)
```

Esto ocurre **después** de persistir el mensaje de usuario, pero **antes** de insertar `usage_record` o audit event.

Impacto:

- Queda un mensaje de usuario persistido sin rastro de fallo en ledger/audit.
- Rompe auditabilidad del router.
- Puede confundir al usuario: el prompt queda en el chat, pero el fallo no aparece como `chat.completion_failed`.

Recomendación:

- Registrar `usage_record(status='failed', provider_slug='router', model='unknown'/'none', error='no_allowed_model')`.
- Registrar `audit_log` / JSONL `chat.completion_failed`.
- Luego devolver 422.

---

### P1-02 — Prompt base insuficiente para transición a SL1b

Para SL1a puro no bloquea, pero el hito siguiente depende de draft real con datos no inventados. Con el prompt actual, si el usuario pide un precio o SKU, el modelo puede inventar.

Impacto:

- Riesgo de falsa confianza en dogfood.
- Se acerca al P0 “dato inventado sin fuente” tan pronto se use con drafts reales.

Recomendación:

- Endurecer `_SYSTEM_PROMPT` ya en SL1a, aunque aún no haya KB.
- Incluir política de “hard facts require source”.
- La UI debe indicar “sin KB/citas todavía” o “no uses para datos duros sin fuente”.

---

### P1-03 — No se verificaron tests en esta auditoría

Los tests existen y parecen cubrir los fixes recientes, pero no se pudieron ejecutar por política.

Impacto:

- No puedo confirmar `PASS` real.
- `.pytest_cache/lastfailed` aún contiene nombres antiguos fallidos (`test_schema_version_is_3`, `test_chat_completion_persists_messages_and_usage`), aunque puede ser caché obsoleta.

Recomendación:

- Ejecutar en entorno permitido:

```bash
cd app
python -m pytest -q
```

- Actualizar o limpiar cache si los fallos ya no existen.
- Guardar output en `harness/reports/`.

---

## P2 — Recomendados

### P2-01 — Budget cap acumulado aún tiene riesgo de carrera

Hay una mejora importante: se reconsulta `current_spent = sum_workspace_usage_cost(ctx, conn)` dentro de una transacción antes de insertar el resultado. Aun así, SQLite no necesariamente serializa dos requests concurrentes durante todo el tramo provider-call → insert.

Impacto:

- Dos completions concurrentes podrían pasar el cap si ambas completan cerca en tiempo y no hay lock de escritura antes del chequeo final.

Recomendación:

- Para SL1a dogfood puede aceptarse.
- Para robustez: usar transacción de escritura tipo `BEGIN IMMEDIATE` en el tramo final `recheck_spend + insert_usage`.
- Agregar test concurrente o simulación de race.

### P2-02 — `BudgetExceeded` catch deja variable muerta

En `api_create_completion()`:

```python
except BudgetExceeded as exc:
    error = exc.detail
    attempts.append(...)
    user_message = "Budget cap exceeded for this workspace"
```

`user_message` no se usa.

Impacto: menor, deuda de limpieza.

Recomendación: eliminar variable o usarla para `detail`.

### P2-03 — `has_available_provider()` con provider preferido no disponible

`Router._ordered_providers(request)` incluye el provider preferido aunque no esté disponible:

```python
preferred = [p for p in ordered if p.provider_slug == request.provider_slug]
rest = [...]
return preferred + rest
```

Luego `complete()` intentará ese provider y el provider lanzará error si no está configurado.

Impacto:

- Funciona como fallback, pero genera un intento fallido esperable.
- Si el usuario selecciona explícitamente un provider no configurado, quizá debería devolver 422/503 más claro o tratarlo como preferencia laxa de forma explícita en UI.

Recomendación:

- Decidir contrato: `provider_slug` como preferencia laxa vs lock estricto.
- Si es laxo, documentarlo en API y UI.
- Si es estricto, no fallback cuando el usuario fija provider.

### P2-04 — El status/costo no se muestra antes del envío

La UI muestra `provider · model · cost · duration` después de una respuesta, pero antes de enviar el usuario no ve:

- proveedor probable,
- si saldrá a cloud,
- gasto acumulado,
- budget cap.

Recomendación:

- Consumir `/router/status` al cargar workspace.
- Mostrar chip: “Cloud: OpenAI / Anthropic / Google” o “Local: Ollama”.
- Mostrar `spent_usd / budget_cap_usd`.

### P2-05 — Frontend: headers `x-user-id` no tienen efecto por defecto

`app.jsx` manda:

```js
const apiHeaders = { "x-user-id": "local" };
```

Pero backend ignora headers salvo `SPACELOOM_DEV_TRUST_HEADERS`.

Impacto: menor; puede confundir a futuros devs.

Recomendación: remover header en frontend o comentar que es noop salvo modo dev.

### P2-06 — Dependencia de CDN en app desktop

`index.html` carga React/Babel desde `unpkg.com`. Para SL0/SL1a dev está bien, pero “desktop instalable sin terminal” y uso offline necesitarán assets locales.

Recomendación:

- Antes de SL4, vendorizar React/Babel o introducir build local.
- Para dogfood interno, documentar que necesita red para primer render si no está cacheado.

### P2-07 — Graph report muestra ciclo `api.py -> main.py -> api.py`

`graphify-out/GRAPH_REPORT.md` reporta ciclo import:

- `app/src/api.py -> app/src/main.py -> app/src/api.py`

No vi un ciclo obvio en los fuentes leídos, así que puede ser inferido/falso positivo por graphify. Pero conviene revisar.

Recomendación:

- Ejecutar query/inspección graphify.
- Si hay import real en tests o modules, romper dependencia.

---

## 5. Consistencia con sistema de marca

**Estado general: OK.**

Puntos positivos:

- Paleta centralizada en `:root` CSS vars.
- EB Garamond para títulos/voz.
- Geist para UI.
- Geist Mono para datos/estado.
- Iconos inline SVG con `currentColor`, `strokeWidth="1.75"`, round caps.
- Isotipo 3×3 tejido presente en UI y boot.
- Wordmark Faber/Loom respeta coral + ink.

Observaciones:

- El fallback HTML en `main.py` usa hex directos. No bloquea si `static/index.html` existe, pero sería mejor alinear o reducir duplicación.
- La UI comunica HITL (“nada irreversible…”), bien para P0.
- Riesgo UX: sugerencias como “Armar un draft contra el espacio” pueden sobreprometer antes de SL1b/SL2.

---

## 6. Testing observado

`app/tests/test_sl1a_router.py` cubre áreas importantes:

- schema version 4;
- tabla `usage_record`;
- router status sin providers;
- CRUD chat;
- blank title;
- no providers → 503;
- modelo no permitido → 422;
- fake provider completion;
- fallback modelo por provider;
- provider allowlist;
- budget cap acumulado;
- aislamiento cross-workspace;
- audit mirror JSONL;
- fallback a provider barato cuando el caro excede presupuesto;
- unknown provider → 422;
- no providers crea usage failed;
- fallo mirror no rompe respuesta.

Tests faltantes recomendados:

1. `NoAllowedModel` registra `usage_record` + audit.
2. Concurrencia de budget cap o simulación con dos completions solapadas.
3. UI status: provider/cap/spend visible antes de enviar.
4. Prompt/base guardrail para hard facts sin fuente.
5. Si `provider_slug` se define como lock estricto, test de no fallback.

---

## 7. Recomendaciones concretas de cierre SL1a

Antes de pedir `PASS`:

1. **Registrar audit/usage en `NoAllowedModel`.**
2. **Endurecer `_SYSTEM_PROMPT` con reglas anti-invención y anti-injection preparatorias.**
3. **Ejecutar y archivar `pytest -q`.**
4. **Mostrar en UI al menos estado básico de proveedor/costo o aclaración “SL1a sin KB/citas”.**
5. **Crear issue/tarea para serialización del budget cap antes de uso intensivo/concurrente.**

---

# Veredicto preliminar: `NEEDS_FIX`

No encontré P0 activo: no hay irreversibles sin HITL, la separación por workspace está bien encaminada, no hay ingesta externa vulnerable aún, y las costuras contract-first principales existen.

Pero no doy `PASS` por:

- falta de audit/usage en el camino `NoAllowedModel`;
- prompt base demasiado laxo para el salto inmediato a SL1b;
- tests no ejecutados en esta auditoría;
- riesgo residual de concurrencia en budget cap;
- UX aún puede sobreprometer “draft contra espacio” sin KB/citas.

Con esos ajustes y pytest pasando, SL1a debería estar cerca de `PASS` técnico como hito de router + chat.