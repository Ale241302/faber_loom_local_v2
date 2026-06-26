# Auditoría técnica — SpaceLoom SL0 / iteración 1

> Nota de alcance: los placeholders `[[PHASE]]`, `[[ITERATION]]`, `[[WRITTEN_FILES]]` y `[[AGENT_OUTPUTS]]` no llegaron expandidos. Inferí **SL0 / iteración 1** por los archivos `harness/agents/SL0_*_iter1.md` y `harness/reports/SL0_*_iter1.md`. Audité en modo solo lectura.

---

## 1. Archivos revisados

### Plan / grafo

- `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md`
- `graphify-out/GRAPH_REPORT.md`

### Backend

- `app/src/context.py`
- `app/src/models.py`
- `app/src/db.py`
- `app/src/api.py`
- `app/src/audit.py`
- `app/src/seed.py`
- `app/src/main.py`
- `app/pyproject.toml`

### Frontend / marca

- `app/static/index.html`
- `app/static/js/app.jsx`
- `app/static/css/main.css`
- `app/static/assets/isotipo.svg`
- `app/static/assets/wordmark.svg`

### Evidencia de agentes / harness

- `harness/agents/SL0_backend_iter1.md`
- `harness/agents/SL0_frontend_iter1.md`
- `harness/agents/SL0_brand_iter1.md`
- `harness/reports/SL0_eval_iter1.md`
- `harness/reports/SL0_audit_iter1.md`

---

## 2. Resumen ejecutivo

La entrega **cumple funcionalmente el espíritu de SL0**: hay app FastAPI + SQLite, seed local, shell React, entrada pywebview y persistencia en `app/data/spaceloom.sqlite3`.

No encontré un P0 activo: no hay envío, borrado, correo, ingestion externa ni generación de drafts con datos inventados.

Pero **no la marcaría `PASS` limpio** porque las costuras contract-first declaradas como no negociables todavía están incompletas o ambiguas:

1. Faltan tablas `routine` y `routine_run`, aunque el plan las define como costura central.
2. La matriz de campos latentes no está completa ni documentada tabla por tabla.
3. `Context` existe y se pasa a queries, pero no aísla realmente por workspace/tenant.
4. `AuditWriter` existe, pero su doble escritura JSONL + DB no es atómica.
5. La UI afirma o sugiere capacidades no implementadas: `Sellado local`, `BYO-key`, citar fuentes, invocar skills.
6. El frontend depende de CDNs externos sin SRI y transpila JSX con Babel en runtime.
7. No hay tests versionados en el repo que hagan reproducible el smoke test.

Veredicto preliminar: **`NEEDS_FIX`**.

---

## 3. Evaluación contra DoD de SL0

### 3.1 App vacía corre

**Estado:** cumple en estructura.

Evidencia:

- `app/src/main.py` define `create_app()`, monta `/api` y `/static`.
- `lifespan()` inicializa DB y ejecuta seed.
- `run_desktop()` levanta uvicorn en hilo daemon y abre pywebview.
- `app/static/index.html` monta React UMD + `app.jsx`.
- `app/static/js/app.jsx` implementa topbar, rail, canvas, composer visual y carga de workspaces.

**Hallazgo menor:** `run_desktop(host, port)` no respeta realmente `host/port` custom para las URLs, porque `APP_URL` y `HEALTH_URL` están definidos globalmente con `HOST=127.0.0.1` y `PORT=8000`.

Recomendación:

```python
def run_desktop(host: str = HOST, port: int = PORT) -> None:
    app_url = f"http://{host}:{port}/static/index.html"
    health_url = f"http://{host}:{port}/api/health"
    ...
    _wait_until_ready(health_url)
    webview.create_window(..., app_url, ...)
```

También conviene permitir `SPACELOOM_PORT` o detectar puerto libre antes de dogfood.

---

### 3.2 1 workspace de prueba

**Estado:** cumple.

- `seed.py` crea `MWT Demo` con slug `mwt-demo`.
- Usa `get_workspace_by_slug()` para idempotencia.
- No introduce facts de negocio, precios ni datos reales inventados.

Correcto para SL0.

---

### 3.3 Persistencia local

**Estado:** cumple.

- SQLite en `app/data/spaceloom.sqlite3`.
- Override por `SPACELOOM_DB_PATH`.
- `.gitignore` excluye `app/data/`, `*.db`, `*.sqlite3`.

Correcto para SL0 local-first.

---

## 4. Costuras contract-first

## 4.1 `Context(workspace_id, tenant_id=None, user_id=None)`

**Estado:** parcial.

`Context` existe y las funciones de `db.py` lo reciben. Esto cumple la forma mínima de la costura.

Problema: **se pasa `Context`, pero no se usa como frontera real de aislamiento**.

Ejemplos:

- `list_workspaces(ctx, conn)` lista todos los workspaces sin filtrar por tenant/user.
- `get_workspace(ctx, conn, workspace_id=None)` permite leer un workspace arbitrario si se pasa `workspace_id`.
- `api_get_workspace()` toma el `workspace_id` del path y construye un `Context` con ese mismo ID; no verifica autorización ni que pertenezca al usuario/tenant actual.

En SL0 single-user no es P0, pero como costura para SL2a/SL3.5 está incompleta.

**Recomendación concreta:**

Separar explícitamente:

- queries `system_*` para bootstrap/listado/creación;
- queries `scoped_*` que siempre filtran por `ctx.workspace_id`.

Ejemplo conceptual:

```sql
WHERE workspace_id = :ctx_workspace_id
```

Y evitar funciones genéricas que acepten `workspace_id` externo salvo que sean `system_*` y estén documentadas.

---

## 4.2 Campos latentes

**Estado:** parcial / ambiguo.

El plan y AGENTS.md piden campos latentes desde SL0:

- `tenant_id`
- `user_id` / `actor_id`
- `actor_role_at_decision`
- `routine_version`
- `skill_version`
- `schema_version`
- `source_version`
- `approved_by`

El schema actual incluye muchos, pero no de forma uniforme.

### Tabla por tabla

| Tabla | Observación |
|---|---|
| `workspace` | Tiene `tenant_id`, `user_id`, `schema_version`; no tiene `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `source_version`, `approved_by`. |
| `kb_source` | Tiene `tenant_id`, `user_id`, `routine_version`, `skill_version`, `schema_version`, `source_version`; no tiene `actor_id`, `actor_role_at_decision`, `approved_by`. |
| `chat` | Tiene `tenant_id`, `user_id`, `routine_version`, `skill_version`, `schema_version`, `source_version`; no tiene `actor_id`, `actor_role_at_decision`, `approved_by`. |
| `message` | Tiene actor, role y versiones; no tiene `approved_by`. |
| `draft` | Bien cubierto. |
| `audit_log` | Bien cubierto. |

No todos los campos tienen sentido en todas las tablas, pero entonces debe existir una **matriz contractual** que diga “aplica / no aplica / razón”.

**Recomendación concreta:**

Crear:

```text
docs/contracts/latent_fields_matrix.md
```

Con una matriz por tabla y justificar excepciones. Si la regla es estricta, ajustar migración para agregar los campos faltantes.

---

## 4.3 Tablas `routine` y `routine_run`

**Estado:** faltante.

El plan define explícitamente:

```text
routine(id, workspace_id, name, skill_md, tools_allowlist, schema_output_json, preset_id, trigger_json, persona_md, is_active, created_at)

routine_run(id, routine_id, workspace_id, input_json, output_json, evidence_json, status, edit_pct, created_at)
```

Pero `models.py` solo crea:

- `workspace`
- `kb_source`
- `chat`
- `message`
- `draft`
- `audit_log`

Faltan `routine` y `routine_run`.

Esto no rompe el skeleton, pero sí debilita la base para SL3a y contradice la costura “Routine supersede split agent/skill”.

**Recomendación:** agregarlas ya, aunque estén vacías, con los campos latentes correspondientes.

---

## 4.4 `AuditWriter`

**Estado:** existe, buena costura, pero no atómica.

`AuditWriter` escribe:

1. `app/data/audit.jsonl`
2. tabla `audit_log`

Eso cumple la intención “hoy JSONL, mañana outbox/tabla”.

Problema: escribe primero JSONL y luego DB. Si falla la inserción en DB, queda divergencia. Además, `create_workspace()` hace commit antes de auditar, así que puede quedar un workspace creado sin audit consistente.

**Recomendación:**

Para SL0 puede bastar con documentar “best effort”, pero antes de dogfood conviene:

- insertar `audit_log` en la misma transacción del cambio principal;
- luego exportar/apendear JSONL;
- o convertir JSONL en vista/export derivado de `audit_log`.

---

## 5. Riesgos P0

## 5.1 Envío/borrado sin HITL

**Estado:** sin P0 activo.

No hay endpoints de envío, borrado, correo ni acciones irreversibles.

El composer del frontend previene submit:

```javascript
const onSubmit = (e) => {
  e.preventDefault();
};
```

Riesgo UX: el botón `Enviar` se habilita con texto, pero no hace nada. Para SL0 es aceptable, pero debería ser más explícito.

**Recomendación:** cambiar temporalmente a “Próximo en SL1a” o mostrar un aviso claro: “SL0: composer visual, no envía”.

---

## 5.2 Injection por contenido externo

**Estado:** no aplica aún a KB/email/PDF/Excel/SKILL.md.

No hay ingestion externa. React escapa contenido renderizado por defecto, así que no vi vector directo por nombres de workspace.

Riesgo importante: **supply-chain injection** por CDNs runtime:

```html
https://unpkg.com/react@18/...
https://unpkg.com/react-dom@18/...
https://unpkg.com/@babel/standalone@7/...
https://fonts.googleapis.com/...
```

Sin SRI, sin bundle local y con Babel runtime, la app local-first depende de red externa y código remoto.

**Recomendación antes de dogfood real:**

- vendorear React/ReactDOM o introducir build step;
- eliminar Babel standalone;
- servir fuentes locales;
- fijar hashes;
- añadir CSP.

---

## 5.3 Fuga cross-workspace

**Estado:** no hay datos sensibles todavía, pero la costura no está lista.

Riesgos:

- `GET /api/workspaces` lista todo.
- `x-tenant-id`, `x-user-id`, `x-actor-role` vienen de headers arbitrarios.
- `Context` no impone aislamiento real.

No es P0 en SL0 porque no hay KB real ni multiworkspace sensible. Pero debe corregirse antes de SL2a, donde el plan exige sellado mínimo antes de cargar clientes distintos.

---

## 5.4 Dato inventado sin fuente

**Estado:** sin P0 activo.

No hay generación de drafts ni facts. El seed solo crea un espacio demo.

Riesgo de comunicación: la UI muestra sugerencias como “Citar un dato con su fuente” y pills como “Sellado local” / “BYO-key”, aunque esas capacidades no existen todavía.

**Recomendación:** marcar esas superficies como `SL1a`, `SL2a`, “placeholder” o retirarlas temporalmente.

---

## 6. Sistema de marca / UI

### 6.1 Paleta

**Estado:** cumple visualmente.

`main.css` define tokens coherentes con el canon:

- `#F4F1ED`
- `#1F1E1C`
- `#C96442`
- `#5A6B7C`
- `#FFFFFF`
- neutrales cálidos compatibles.

### 6.2 Tipografía

**Estado:** cumple visualmente.

- EB Garamond para voz/títulos.
- Geist para UI.
- Geist Mono para datos.

Riesgo: carga remota desde Google Fonts.

### 6.3 Iconografía

**Estado:** cumple mayormente.

- Iconos inline 24×24.
- Stroke `1.75`.
- `currentColor`.
- Isotipo 3×3 tejido con stroke `3.5`.

### 6.4 Claims visuales no implementados

**Estado:** necesita fix.

En `Canvas` aparecen:

- `Sellado local`
- `BYO-key`

Esto sugiere capacidades activas. Para una marca “auditable” y “no hype”, debe evitarse.

**Fix recomendado:**

- `Sellado: SL2a`
- `Router: SL1a`
- o esconder hasta implementación real.

---

## 7. Tests y evidencia reproducible

**Estado:** faltan tests versionados.

Los agentes reportan smoke tests exitosos, pero no hay `app/tests/` ni script estable en el repo.

Mínimo recomendado para cerrar SL0:

1. DB init crea tablas.
2. Seed idempotente.
3. `/api/health` responde 200.
4. `/api/workspaces` devuelve `MWT Demo`.
5. `POST /api/workspaces` genera slug único.
6. `AuditWriter` escribe evento en JSONL y DB.
7. Static smoke: `index.html`, `main.css`, `app.jsx` devuelven 200.

---

## 8. Hallazgos priorizados

### P0 / BLOCKERS

No encontré P0 activo en SL0.

---

### P1 — Corregir antes de cerrar SL0 como base contractual

1. **Agregar o justificar ausencia de `routine` y `routine_run`.**
2. **Completar/documentar matriz de campos latentes por tabla.**
3. **Separar queries system vs scoped; hacer que `Context` limite lecturas/escrituras.**
4. **Cambiar UI que afirma `Sellado local` / `BYO-key` como si estuvieran implementados.**
5. **Agregar tests versionados de smoke/backend/schema/audit.**
6. **Eliminar dependencia runtime de CDNs antes de dogfood serio.**

---

### P2 — Mejoras próximas

1. `run_desktop(host, port)` debe usar URLs derivadas de argumentos.
2. `AuditWriter` debe ser transaccional o declaradamente best-effort.
3. `WorkspaceCreate.name` acepta whitespace-only; validar `strip()`.
4. Headers `x-tenant-id` / `x-actor-role` no deben ser autoridad real.
5. Empaquetar fuentes localmente.
6. Quitar Babel standalone antes de distribución.
7. Considerar puerto configurable o auto-detección.

---

## 9. Recomendación de siguiente iteración

Orden recomendado:

1. **Schema contract-first**
   - `routine`
   - `routine_run`
   - matriz de campos latentes
   - migración v2 o ajuste v1 si aún se permite resetear SL0.

2. **Context hardening**
   - `system_*` vs `scoped_*`
   - tests de aislamiento básicos.

3. **Tests**
   - smoke API
   - seed idempotente
   - audit
   - static assets.

4. **UI honesty pass**
   - marcar placeholders como `SL1a` / `SL2a`
   - no prometer sellado/router/fuentes antes de existir.

5. **Frontend local-first**
   - eliminar CDN runtime o al menos fijar integridad mientras se prepara bundle local.

---

# Veredicto preliminar

## `NEEDS_FIX`

La entrega **sí cumple el DoD funcional mínimo de SL0**: app shell, seed, SQLite local y frontend de marca.

Pero no debe cerrarse como `PASS` porque las costuras contract-first no están suficientemente sólidas para construir SL1–SL3 encima sin deuda temprana: faltan `routine`/`routine_run`, la matriz de campos latentes es incompleta/ambigua, `Context` no aísla realmente, no hay tests versionados y la UI afirma capacidades no implementadas.

No amerita `BLOCK` porque no hay P0 activo ni acción irreversible insegura.