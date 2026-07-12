# E4-1 — Workspace Briefs

## Propósito

Un **workspace brief** es una caché en frío, de solo-índice, que responde
"¿qué hay en este workspace?" sin escanear contenido en tiempo de request.
Sirve como memoria operativa del Agente Vivo: el planner puede leerlo para
enriquecer prompts sin incurrir en costo de embeddings ni exponer cuerpos de
fuentes.

## Diseño

- **Índice únicamente:** conteos por tipo de fuente, títulos recientes,
  entidades frecuentes (heurística barata sobre títulos), rutinas activas,
  última corrida de rutina y actividad reciente resumida.
- **Agregados de negocio:** facturas abiertas (totales y conteos únicamente;
  nunca ítems detallados).
- **Nunca genera en caliente:** los endpoints solo leen la caché persistida.
- **Regeneración:** ciclo ambiental (`ambient.AmbientOrchestrator._process_workspace`).
- **Política de stale:** por defecto `max_age_h=24` o `max_writes=50` desde el
  último `computed_at`.

## Esquema

`app/src/models.py` v42 añade `workspace_brief`:

| Campo | Notas |
|---|---|
| `tenant_id` + `workspace_id` | PK compuesta, tenant-scoped |
| `brief_json` | Payload entero devuelto por `build_workspace_brief` |
| `source_counts_json` | Snapshot de conteos por tipo de fuente |
| `staleness_policy_json` | Política aplicada al calcular el brief |
| `generation_cost_usd` | Costo de generación (hoy 0 porque no usa LLM) |
| `version` | Incremental, útil para invalidar caches |
| `computed_at` | Timestamp de cálculo |
| Campos latentes R13 | `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by` |

RLS en Postgres: política `tenant_workspace_isolation` aplicada en
`app/scripts/postgres_rls_policies.sql`.

## Key broker

`build_workspace_brief` consulta `key_broker.resolve_read_level` antes de leer
nada:

- `CLOSED` → brief sellado con conteo total y `level=closed`.
- `CONTENT` sin rol aprobador → `level=index`, sellado, sin agregados de facturas.
- `CONTENT` con rol aprobador → brief completo.
- `CEO-only` sin rol `ceo` → se comporta como `CLOSED`.

## API

- `GET /api/workspaces/{workspace_id}/brief`
  - Devuelve el brief persistido, re-mediado por los roles del solicitante.
  - **Nunca** lo genera inline; si no existe responde `404`.
  - `CLOSED` o `CEO-only` sin `ceo` devuelven el modelo `WorkspaceBriefRead` con
    `source_counts: {}` y el campo `brief` reducido a `sealed`, `level` y `object_count`.
  - `INDEX` devuelve el brief sin agregados de facturas.
  - Respuesta: `WorkspaceBriefRead`.

## UI

`app/static/js/app.jsx` incluye `WorkspaceBriefPanel` en el `RightRail`.
Muestra:

- Nivel de acceso y sello.
- Versión y fecha de cómputo.
- Conteo total de fuentes, rutinas activas y total de facturas abiertas.
- Hasta 5 títulos recientes.
- Mensaje informativo cuando el brief aún no existe.

## Tests

`app/tests/test_e4_1_workspace_briefs.py` cubre:

1. Existencia de tabla tras migración v42.
2. Brief por defecto a nivel `content`.
3. Brief sellado para espacio `CLOSED`.
4. Degradación a `index` para no-approver.
5. Persistencia tras `refresh_workspace_brief`.
6. Detección de stale.
7. Endpoint `GET /brief` 404 cuando no existe y 200 tras refresh.
8. El ciclo ambiental genera el brief para el workspace procesado.

## Riesgos mitigados

| Riesgo | Mitigación |
|---|---|
| Fuga cross-tenant | PK `(tenant_id, workspace_id)`, RLS, y `Context.require_tenant()` en toda query |
| CEO-only leak | `resolve_read_level` devuelve `CLOSED` para no-CEO |
| Contenido expuesto | Solo títulos y conteos; nunca cuerpos de fuentes |
| Generación inline costosa | Endpoints solo leen; refresh solo en ciclo ambiental |
| Dato derivado sin fuente | Los briefs son regenerables; se documentan como R12 en `SPEC_E2_5_ENTIDAD_VIVA.md` |
