---
id: SPEC_FB_ARCHETYPE_FACTORY_v1
title: Fabrica de arquetipos (Capa 1)
status: DRAFT
version: 1.0
domain: FaberLoom
etapa: E5
created: 2026-07-14
last_review: 2026-07-14
depends_on: SPEC_FB_ENVELOPE_ENFORCEMENT_v1
---

# Fabrica de arquetipos

## Resumen

Un **arquetipo** es la plantilla reutilizable de "como se hace un tipo de trabajo"
(`SPEC_FB_ARCHETYPE_v1.md:23`). Hoy no existe como entidad: es un string validado dentro
del blob `manifest_json` de `skill_manifest` mas un SPEC en DRAFT. Este spec lo hace real:
tabla tenant-scoped que el usuario puebla, panel de Admin, y copy-on-create hacia routines.

Va **despues** de `SPEC_FB_ENVELOPE_ENFORCEMENT_v1` a proposito: sin enforcement, un
arquetipo que declara "quien responde" seria una promesa que el runtime no cumple.

## Por que una tabla y no un enum

"Arquetipo" nombra cuatro cosas distintas en la KB. Dos son relevantes aca:

- **Sentido B** (`ENT_FB_AGENT_ARCHETYPES_v1`): los 7 arquetipos *arquitectonicos*
  (`generator`, `triage`, `validator`...). Es un **enum cerrado**, ya existe en
  `skills.py:55-92`, y su propio doc dice que NO hay que crear archivos por arquetipo.
- **Sentido A** (`SPEC_FB_ARCHETYPE_v1`): la *unidad de trabajo* reutilizable
  ("cotizacion B2B", "consulta operativa"). Es lo que el usuario puebla, y pueden ser N.

Este spec implementa el **Sentido A**. Son cosas ortogonales que comparten nombre; no se
unifican aca.

## Las facetas: solo una es una entidad

El SPEC declara 6 facetas. Verificado contra el codigo:

| # | Faceta | Estado real | Decision |
|---|---|---|---|
| 2 | Routing | **Entidad**: `routing_preset` | **Se referencia** (FK) |
| 5 | Schema de salida | Columna inline `routine.schema_output_json` | Se copia |
| 6 | Voz/formato | Columna inline `routine.persona_md` | Se copia |
| 1 | Tipo de informacion | No existe; lo mas cercano es `routine.category` (enum) | Se copia el enum |
| 3 | Working Profile | **No existe. Cero hits en todo el repo** | **Fuera** |
| 4 | Conocimiento L0 | Tablas KB existen, pero ninguna columna de `routine` apunta a una KB y el modelo L0-L4 no existe en codigo | **Fuera** |

Consecuencia: el arquetipo **referencia** la faceta 2 y **copia** el resto, porque el resto
no son entidades sino columnas de `routine`. Un arquetipo que "empaqueta seis entidades"
seria ficcion: cinco no estan.

## Diseño

### 1. Tabla `archetype` (migracion 49)

Tenant-scoped, espejando la forma de `routing_preset`. `SCHEMA_VERSION` pasa 48 -> 49.

```sql
CREATE TABLE IF NOT EXISTS archetype (
    tenant_id TEXT NOT NULL,
    archetype_id TEXT NOT NULL,
    name TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    description TEXT,
    category TEXT NOT NULL DEFAULT 'custom'
        CHECK (category IN ('skill', 'agent', 'template', 'reference', 'custom')),
    routing_preset_id TEXT,
    persona_md TEXT NOT NULL DEFAULT '',
    skill_md TEXT NOT NULL DEFAULT '',
    tools_allowlist TEXT NOT NULL DEFAULT '[]',
    schema_output_json TEXT NOT NULL DEFAULT '{}',
    trigger_json TEXT NOT NULL DEFAULT '{}',
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    is_template INTEGER NOT NULL DEFAULT 0 CHECK (is_template IN (0, 1)),
    created_by TEXT,
    actor_id TEXT,
    actor_role_at_decision TEXT,
    routine_version TEXT,
    skill_version TEXT,
    schema_version INTEGER NOT NULL DEFAULT 49,
    source_version TEXT NOT NULL DEFAULT 'v1',
    approved_by TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, archetype_id),
    FOREIGN KEY (tenant_id, routing_preset_id)
        REFERENCES routing_preset(tenant_id, preset_id)
);
```

`category` reusa el enum de `routine` (`_ROUTINE_CATEGORIES`, `models.py:16`) para que el
copy-on-create sea directo.

### 2. El FK compuesto

Es el **primer FK compuesto del schema** (verificado: 30 `FOREIGN KEY` en `models.py`,
todos de una columna). Se justifica porque:

- Hace **estructuralmente imposible** referenciar un preset de otro tenant: `tenant_id`
  participa del FK, asi que un arquetipo solo puede apuntar a presets de su propio tenant.
- `routing_preset_id` es nullable; un FK con NULL no se enforcea, asi que un arquetipo
  sin routing es legal.
- `PRAGMA foreign_keys = ON` ya esta activo en el path principal
  (`db_adapter.py:386`, `_connect_sqlite`).

**Cambio de contrato en `delete_routing_preset`** (`db.py:4193`): hoy borra sin chequear
nada y huerfaniza en silencio. Con el FK, borrar un preset referenciado por un arquetipo
falla. Se agrega un chequeo explicito que devuelve 409 con el conteo de arquetipos que lo
referencian, en vez de dejar salir un error crudo de integridad. Es la misma filosofia que
`SPEC_FB_ENVELOPE_ENFORCEMENT_v1`: fallar fuerte antes que degradar en silencio.

Nota Postgres: el chequeo de FK corre con RLS bypasseada, lo que en general permitiria
inferir existencia cross-tenant. Aca no aplica: como `tenant_id` esta en ambos lados del
FK, una referencia cross-tenant no es expresable.

### 3. Procedencia: `routine.archetype_id`

Migracion 49 tambien agrega:

```sql
ALTER TABLE routine ADD COLUMN archetype_id TEXT;
```

Nullable, **sin FK, y explicitamente no es un link vivo**: registra de que arquetipo se
copio la routine al crearse. Editar el arquetipo despues no toca la routine (herencia
plana, Dimension 2 del SPEC; la cascada esta DIFERIDA).

Sin esta columna la procedencia es irrecuperable a posteriori, y es lo que habilitan las
fases F3-F4 del SPEC (evolucion y clasificacion dinamica).

No lleva FK por dos razones: `routine.tenant_id` es **nullable** (un FK compuesto no se
enforcearia para filas con tenant NULL), y `routine` es workspace-scoped mientras
`archetype` es tenant-scoped.

### 4. Copy-on-create

```
POST /api/workspaces/{workspace_id}/routines/from-archetype/{archetype_id}
```

Materializa una routine con los campos del arquetipo, grabando `archetype_id` como
procedencia. El usuario despues especializa con el PATCH normal.

La copia va del grano tenant (arquetipo) al grano workspace (routine), que es justamente
lo que resuelve el mismatch: un arquetipo se comparte entre workspaces, sus instancias no.

`preset_id` se materializa con el prefijo `@preset/<slug>`, porque es lo que
`routine.preset_id` espera (`app.jsx:4059`) — asimetria existente: `routing_preset.preset_id`
guarda el slug pelado y `preset_id_must_be_slug` rechaza `/`.

### 5. API

`app/src/archetypes.py`, espejando `presets.py` exactamente:
`_require_tenant_admin` (owner/admin/platform_admin) -> `_tenant_context` ->
`transaction(conn, ctx=ctx)` -> `_ensure_system_workspace` -> fn de db -> `audit_writer`.

| Metodo | Path |
|---|---|
| GET | `/api/tenants/{tenant_id}/archetypes` |
| POST | `/api/tenants/{tenant_id}/archetypes` (201) |
| GET | `/api/tenants/{tenant_id}/archetypes/{archetype_id}` |
| PATCH | `/api/tenants/{tenant_id}/archetypes/{archetype_id}` |
| DELETE | `/api/tenants/{tenant_id}/archetypes/{archetype_id}` (204) |

Acciones de audit: `archetype.created` / `.updated` / `.deleted` / `routine.created_from_archetype`.

### 6. UI

`PresetsPanel` **no** es un panel de nav: vive anidado en `SettingsView` (`app.jsx:3191`),
colgado de "Router / Proveedores". Los paneles nuevos siguen otro patron —
`agent_tasks.jsx` con guard `window.AgentTasksPanel` y `<script>` en `index.html` **antes**
de `app.jsx`. Arquetipos sigue ese patron:

- `app/static/js/archetypes.jsx`, terminando en `window.ArchetypesPanel = ArchetypesPanel;`
- `<script type="text/babel" src="/static/js/archetypes.jsx?v=...">` en `index.html:42`,
  antes de `app.jsx`
- `RailItem label="Arquetipos"` en el accordion `tenant-acc` (`app.jsx:499-520`)
- Rama guardada en la cadena de dispatch (`app.jsx:3844-3865`)
- Bump del `?v=` de `app.jsx`

### 7. RLS (Postgres)

`archetype` es tenant-scoped, no workspace-scoped. En `postgres_rls_policies.sql`:
`ENABLE`/`FORCE` (~`:97`), entrada en la lista de tablas (~`:146-149`), y un
`tenant_policy` en la seccion 8 (~`:259+`) — **no** el helper
`_create_tenant_workspace_policy`, que exige workspace y romperia el acceso tenant-level.

## Alcance

**Dentro:** tabla + FK compuesto + procedencia + CRUD + copy-on-create + panel + RLS.

**Fuera:**
- **Semillas**: el catalogo nace vacio. Es lo que dice `SPEC_FB_ARCHETYPE_v1.md:96`
  ("el humano/curador define los arquetipos iniciales") y evita heredar el bug de
  `seed_routing_presets`, cuyo docstring afirma que bumpea version cuando cambia el
  template pero cuyo codigo hace `continue` sobre cualquier fila existente (`db.py:3994`).
- **Cascada / herencia viva**: DIFERIDA por el propio SPEC (senal de activacion:
  >=10 tenants).
- **Facetas 3 y 4** (Working Profile, L0): no existen entidades que referenciar.
- **Unificar con los 7 arquetipos arquitectonicos**: enum cerrado vs tabla poblada por el
  usuario. Ortogonales.

## Testing

Archivo nuevo: `app/tests/test_e5_archetypes.py`. Patron de `test_e3_5_presets.py`
(TestClient + bootstrap de tenant owner).

Mandatorios:

1. `test_cross_tenant_isolation` — el tenant B no ve ni toca los arquetipos del tenant A.
   Es el P0 de `AGENTS.md:38`.
2. `test_archetype_cannot_reference_foreign_tenant_preset` — el FK compuesto hace
   imposible apuntar a un preset de otro tenant.
3. `test_delete_preset_referenced_by_archetype_fails` — 409 con el conteo, no orfandad
   silenciosa.
4. `test_routine_from_archetype_copies_facets` — la routine nace con persona_md,
   schema_output_json, tools_allowlist, category y preset_id del arquetipo.
5. `test_routine_records_archetype_provenance` — `routine.archetype_id` queda grabado.
6. `test_editing_archetype_does_not_touch_existing_routines` — herencia plana: la copia
   es una foto, no un espejo.
7. `test_archetype_without_preset_is_legal` — `routing_preset_id` NULL no rompe el FK.

## Archivos afectados

| Concern | Archivo |
|---|---|
| Migracion 49 + SCHEMA_VERSION | `app/src/models.py:12`, `:137` |
| Schemas pydantic | `app/src/models.py` (junto a `RoutingPreset*`, `:3183+`) |
| Capa db | `app/src/db.py` (junto a `*_routing_preset`, `:4036+`) |
| Chequeo referencial | `app/src/db.py:4193` (`delete_routing_preset`) |
| Router | `app/src/archetypes.py` (nuevo) |
| Registro | `app/src/main.py` (junto a `presets_router`) |
| Copy-on-create | `app/src/api.py` (junto a las rutas de routines) |
| RLS | `app/scripts/postgres_rls_policies.sql` (3 lugares) |
| Panel | `app/static/js/archetypes.jsx` (nuevo) + `app/static/index.html` |
| Nav | `app/static/js/app.jsx` (RailItem + dispatch + bump `?v=`) |
| Tests | `app/tests/test_e5_archetypes.py` (nuevo) |

Post-implementacion: `graphify update .` (`AGENTS.md:43`).

## Decisiones registradas

| Decision | Eleccion | Razon |
|---|---|---|
| Entidad | Tabla poblada por el usuario, no enum | "Pueden ser N"; el enum cerrado ya existe y es otra cosa |
| FK a preset | Compuesto real `(tenant_id, routing_preset_id)` | Hace cross-tenant inexpresable; falla fuerte en vez de huerfanizar |
| Semillas | Ninguna, catalogo vacio | Lo dice el SPEC; evita heredar el bug de no-propagacion |
| Procedencia | `routine.archetype_id`, sin FK, no es link vivo | Irrecuperable a posteriori; habilita F3-F4 |
| Facetas 3 y 4 | Fuera | No existen entidades que referenciar |
| Herencia | Plana, copy-on-create | Dimension 2 del SPEC; cascada DIFERIDA |
