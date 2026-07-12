# SPEC_E2_5_ENTIDAD_VIVA.md — Ciclo Ambiental Acotado (Entidad Viva)

id: SPEC_E2_5_ENTIDAD_VIVA  
version: 1.1  
status: DRAFT  
visibility: [INTERNAL]  
domain: FaberLoom (docs/faberloom/)  
type: SPEC  
stamp: DRAFT -- 2026-07-06 -- especificacion tecnica del hito E2-5: entidad viva / ciclo ambiental propositivo con limites duros  
aprobador: CEO  
aplica_a: [FaberLoom, MWT]  
relacionado: PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1.md - PLAN_TRABAJO_E2_FUGU_v3.md - HITOS_E2_COMPARATIVA_FUGU.md - SPEC_AUTONOMY_CONTROL_ENGINE.md - SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md  

---

## 1. Resumen ejecutivo

La **entidad viva** es el ciclo ambiental propositivo de FaberLoom. En Etapa 2 la entidad deja de ser puramente reactiva (responde en el canvas) y pasa a ejecutar revisiones programadas sobre workspaces, inbox (WorkLoom) y KB. Su unico output permitido es **crear items de WorkLoom con evidencia**; nunca ejecuta acciones irreversibles (enviar, borrar, modificar datos de produccion, consumir budget de routing de forma autonoma).

Este documento es la especificacion tecnica de implementacion del hito E2-5. Cubre arquitectura, modelo de datos, detectores, limites, dark-launch, deduplicacion, backoff, metricas, auditoria, API, seguridad y tests.

## 2. Scope: que hace y que NO hace

**Hace (dentro del scope):**
- Recorrer workspaces activos del tenant en ciclos programados.
- Ejecutar detectores de solo lectura sobre workspace, chat, inbox, KB, rutinas y uso.
- Crear items en WorkLoom (`workloom_item`) con evidencia, severidad y sugerencia de accion.
- Respetar ventana de actividad, frecuencia, budget cap y kill switch.
- Auditar cada ciclo: costo, detectores ejecutados, propuestas, fallos, kill state.
- Proveer API de administracion, monitoreo y control (kill switch, metricas, configuracion).

**NO hace (fuera del scope explicito):**
- No envia correos, mensajes, borra datos ni modifica KB/rutinas sin aprobacion humana.
- No consume el router en modo auto ni ejecuta rutinas por su cuenta.
- No crea workspaces, usuarios, tenants ni cambia configuracion de seguridad.
- No reemplaza el scheduler del sistema operativo; es disparada por un scheduler interno.

## 3. Principios y contratos no negociables

1. **0 acciones irreversibles.** La entidad solo lee y crea items WorkLoom. Cualquier detector que requiera efecto colateral es rechazado en revision.
2. **Context is God.** Toda query del ciclo lleva `Context(workspace_id, tenant_id, user_id, actor_role)`. No hay query sin scope.
3. **AuditWriter obligatorio.** Cada ciclo, cada detector y cada propuesta generan evento de auditoria con `actor_id`, `actor_role_at_decision`, `correlation_id` y `evidence_json`.
4. **Campos latentes.** Todas las tablas nuevas incluyen `tenant_id`, `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by` (aunque sean `NULL` por defecto).
5. **Kill switch inmediato.** El ciclo verifica el kill switch global y por workspace antes de cada detector. Si se activa durante la ejecucion, el ciclo se detiene en el siguiente punto de control.
6. **Fail-silent / fail-audit.** Un detector que falla no detiene todo el ciclo; se registra, aplica backoff y continua con los siguientes.

## 4. Arquitectura de alto nivel

```
+----------------------------------+
|  Scheduler interno (APScheduler) |
|  - trigger por tenant / workspace|
+-------------+--------------------+
              |
              v
+----------------------------------+
|  Ambient Orchestrator            |
|  - carga config, kill switches   |
|  - abre ambient_cycle            |
|  - ejecuta detectores en fases   |
+-------------+--------------------+
              |
    +---------+---------+---------+
    v         v         v         v
 Detector  Detector  Detector  Detector
 (read-only, scoped, allowlisted)
    |         |         |         |
    +---------+---------+---------+
              |
              v
+----------------------------------+
|  Scoring + Deduplication         |
|  - score de severidad            |
|  - clave estable, ventana 24h    |
+-------------+--------------------+
              |
              v
+----------------------------------+
|  Proposal Writer                 |
|  - crea workloom_item (dark or   |
|    visible segun fase)           |
+-------------+--------------------+
              |
              v
+----------------------------------+
|  Audit + Metrics                 |
|  - cierra ambient_cycle          |
|  - escribe audit_log + usage     |
+----------------------------------+
```

## 5. Modelo de datos

### 5.1 Tablas

#### `ambient_config` (configuracion global del tenant)
Parametros operativos del ciclo ambiental. Una fila por tenant. Solo admin puede editar.

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | TEXT PK | `cfg_{uuid}` |
| `tenant_id` | TEXT NOT NULL | FK logico a `fnd_tenants` |
| `global_enabled` | BOOLEAN DEFAULT true | Kill switch global |
| `cycle_window_start` | TIME DEFAULT '06:00' | Inicio ventana activa (America/Bogota) |
| `cycle_window_end` | TIME DEFAULT '22:00' | Fin ventana activa |
| `cycle_window_tz` | TEXT DEFAULT 'America/Bogota' | Timezone |
| `global_frequency_min` | INT DEFAULT 30 | Minutos entre ciclos globales (min 15) |
| `per_workspace_frequency_min` | INT DEFAULT 60 | Minutos entre revisiones del mismo workspace (min 30) |
| `budget_pct_of_router_daily` | DECIMAL(5,2) DEFAULT 5.00 | % del budget diario del router (min 1.00) |
| `max_proposals_per_cycle` | INT DEFAULT 10 | Tope de propuestas por workspace y ciclo (min 3) |
| `dark_launch_days` | INT DEFAULT 14 | Dias de modo observacion inicial |
| `utility_threshold_pct` | INT DEFAULT 20 | Umbral de utilidad para circuit breaker |
| `cost_overrun_pct` | INT DEFAULT 150 | Umbral de cost overrun para circuit breaker |
| `actor_id` | TEXT | Usuario admin que edito |
| `actor_role_at_decision` | TEXT | Rol del actor |
| `schema_version` | INT NOT NULL | Version del schema |
| `source_version` | TEXT | Origen de la config |
| `approved_by` | TEXT | Aprobador del cambio |
| `created_at` | TIMESTAMP | ISO 8601 UTC |
| `updated_at` | TIMESTAMP | ISO 8601 UTC |

Indices:
```sql
CREATE UNIQUE INDEX ux_ambient_config_tenant ON ambient_config(tenant_id);
```

#### `ambient_workspace_config` (override por workspace)
Permite habilitar/deshabilitar el ciclo por workspace y ajustar parametros locales sin romper limites duros.

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | TEXT PK | `wcfg_{uuid}` |
| `workspace_id` | TEXT NOT NULL | FK a `workspace` |
| `tenant_id` | TEXT NOT NULL | FK logico |
| `enabled` | BOOLEAN DEFAULT true | Kill switch por workspace |
| `detector_allowlist` | JSON | Lista de slugs de detectores permitidos; `null` = todos |
| `excluded_detector_slugs` | JSON | Lista de detectores deshabilitados explicitamente |
| `actor_id` | TEXT | Actor |
| `actor_role_at_decision` | TEXT | Rol |
| `schema_version` | INT NOT NULL | |
| `created_at` | TIMESTAMP | |
| `updated_at` | TIMESTAMP | |

Indices:
```sql
CREATE UNIQUE INDEX ux_ambient_workspace_config_ws ON ambient_workspace_config(workspace_id, tenant_id);
CREATE INDEX ix_ambient_workspace_config_tenant ON ambient_workspace_config(tenant_id);
```

#### `ambient_detector` (registro de detectores)
Catalogo de detectores disponibles. Se seedea en migracion; el admin puede deshabilitar por workspace via `ambient_workspace_config`.

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | TEXT PK | `det_{uuid}` |
| `tenant_id` | TEXT NOT NULL | Tenant (puede ser `default` para detectores globales) |
| `slug` | TEXT NOT NULL | Identificador estable (`unanswered_email`, `stale_kb`, etc.) |
| `name` | TEXT NOT NULL | Nombre humano |
| `description` | TEXT | Que detecta |
| `input_scope` | JSON | Tablas/entidades que lee |
| `output_type` | TEXT | `workloom_item` |
| `severity_default` | TEXT | `low`, `medium`, `high`, `critical` |
| `cost_estimate_usd` | DECIMAL | Costo estimado por ejecucion |
| `max_frequency_min` | INT | Frecuencia minima permitida del detector |
| `is_active` | BOOLEAN DEFAULT true | |
| `schema_version` | INT NOT NULL | |
| `created_at` | TIMESTAMP | |
| `updated_at` | TIMESTAMP | |

Indices:
```sql
CREATE UNIQUE INDEX ux_ambient_detector_slug ON ambient_detector(tenant_id, slug);
```

#### `ambient_cycle` (una fila por ciclo global o por workspace)
Registro de cada ejecucion del ciclo ambiental.

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | TEXT PK | `cyc_{uuid}` |
| `tenant_id` | TEXT NOT NULL | |
| `workspace_id` | TEXT | `NULL` si es ciclo global; valor si es ciclo por workspace |
| `status` | TEXT | `running`, `completed`, `paused`, `killed`, `cost_overrun`, `utility_breaker` |
| `trigger` | TEXT | `scheduled`, `critical_event`, `manual`, `retry` |
| `started_at` | TIMESTAMP | |
| `ended_at` | TIMESTAMP | |
| `detectors_run` | INT DEFAULT 0 | |
| `detectors_failed` | INT DEFAULT 0 | |
| `proposals_created` | INT DEFAULT 0 | |
| `proposals_visible` | INT DEFAULT 0 | Items visibles en WorkLoom |
| `proposals_dark` | INT DEFAULT 0 | Items en modo observacion |
| `cost_usd` | DECIMAL(12,6) DEFAULT 0 | Costo LLM/API del ciclo |
| `budget_usd` | DECIMAL(12,6) | Budget asignado a este ciclo |
| `utility_score_pct` | INT | `aceptadas / creadas * 100` del ciclo anterior o acumulado |
| `kill_switch_state` | JSON | `{global: bool, workspace: bool}` |
| `evidence_json` | JSON | Metadatos de detectores y resultados |
| `actor_id` | TEXT | Sistema o admin manual |
| `actor_role_at_decision` | TEXT | |
| `schema_version` | INT NOT NULL | |
| `source_version` | TEXT | |
| `approved_by` | TEXT | |

Indices:
```sql
CREATE INDEX ix_ambient_cycle_tenant ON ambient_cycle(tenant_id);
CREATE INDEX ix_ambient_cycle_workspace ON ambient_cycle(workspace_id, tenant_id);
CREATE INDEX ix_ambient_cycle_status ON ambient_cycle(status);
CREATE INDEX ix_ambient_cycle_started ON ambient_cycle(started_at);
```

#### `ambient_proposal` (candidato a item de WorkLoom)
Cada propuesta generada por un detector. Puede convertirse en `workloom_item` visible o quedar en dark-launch.

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | TEXT PK | `prp_{uuid}` |
| `cycle_id` | TEXT NOT NULL | FK a `ambient_cycle` |
| `workspace_id` | TEXT NOT NULL | |
| `tenant_id` | TEXT NOT NULL | |
| `detector_slug` | TEXT NOT NULL | |
| `target_type` | TEXT | Tipo de entidad detectada (`email`, `kb_source`, `routine_run`, etc.) |
| `target_id` | TEXT | ID de la entidad |
| `dedup_key` | TEXT NOT NULL | `hash(detector_slug\|target_id\|bucket)` |
| `severity` | TEXT | `low`, `medium`, `high`, `critical` |
| `title` | TEXT NOT NULL | Titulo del item WorkLoom |
| `description` | TEXT | Cuerpo con evidencia |
| `suggested_action` | TEXT | Accion recomendada (texto, no comando) |
| `evidence_json` | JSON | Datos que respaldan la propuesta |
| `state` | TEXT | `dark`, `visible`, `merged`, `rejected`, `cancelled_by_kill` |
| `workloom_item_id` | TEXT | FK a `workloom_item` si fue publicada |
| `accepted_at` | TIMESTAMP | Cuando el usuario la acepto |
| `actor_id` | TEXT | Sistema |
| `actor_role_at_decision` | TEXT | `system` |
| `schema_version` | INT NOT NULL | |
| `source_version` | TEXT | Version del detector |
| `created_at` | TIMESTAMP | |
| `updated_at` | TIMESTAMP | |

Indices:
```sql
CREATE INDEX ix_ambient_proposal_cycle ON ambient_proposal(cycle_id);
CREATE INDEX ix_ambient_proposal_dedup ON ambient_proposal(dedup_key, workspace_id, tenant_id);
CREATE INDEX ix_ambient_proposal_state ON ambient_proposal(state);
CREATE INDEX ix_ambient_proposal_target ON ambient_proposal(target_type, target_id);
```

#### `ambient_detector_run` (ejecucion individual de un detector)
Una fila por detector por ciclo.

| Campo | Tipo | Descripcion |
|---|---|---|
| `id` | TEXT PK | `dtr_{uuid}` |
| `cycle_id` | TEXT NOT NULL | |
| `detector_slug` | TEXT NOT NULL | |
| `workspace_id` | TEXT | |
| `tenant_id` | TEXT NOT NULL | |
| `status` | TEXT | `ok`, `failed`, `skipped_kill`, `skipped_disabled`, `skipped_budget` |
| `proposals_count` | INT DEFAULT 0 | |
| `cost_usd` | DECIMAL(12,6) DEFAULT 0 | |
| `latency_ms` | INT | |
| `error_message` | TEXT | Si fallo |
| `backoff_until` | TIMESTAMP | Hasta cuando esta en backoff |
| `consecutive_failures` | INT DEFAULT 0 | |
| `evidence_json` | JSON | Resultados compactos |
| `actor_id` | TEXT | Sistema |
| `actor_role_at_decision` | TEXT | `system` |
| `schema_version` | INT NOT NULL | |
| `created_at` | TIMESTAMP | |

Indices:
```sql
CREATE INDEX ix_ambient_detector_run_cycle ON ambient_detector_run(cycle_id);
CREATE INDEX ix_ambient_detector_run_detector ON ambient_detector_run(detector_slug, tenant_id);
```

### 5.2 Campos latentes contract-first

Todas las tablas anteriores incluyen explicitamente los campos latentes del contrato:
- `tenant_id`
- `actor_id`
- `actor_role_at_decision`
- `routine_version` (en tablas que lo ameriten; aqui generalmente `NULL`)
- `skill_version` (idem)
- `schema_version`
- `source_version`
- `approved_by`

`schema_version` se inicializa con la version del schema de la migracion que crea la tabla.

## 6. Ciclo de vida del ciclo ambiental

 Estados y transiciones:

```
[ scheduled ] --(scheduler)--> [ running ]
      |
      v
[ running ] --(kill switch activado)--> [ killed ]
[ running ] --(budget excedido)--> [ cost_overrun ]
[ running ] --(utility breaker)--> [ utility_breaker ]
[ running ] --(finaliza normal)--> [ completed ]
[ running ] --(pausa manual)--> [ paused ]
```

Fases dentro de un ciclo `running`:

1. **collect**: se ejecutan los detectores allowlistados del workspace/tenant.
2. **score**: se asigna severidad a cada hallazgo.
3. **dedup**: se filtran duplicados por `dedup_key` y ventana temporal.
4. **propose**: se crean filas en `ambient_proposal`. Si estamos en dark-launch, `state=dark`; si no, `state=visible` y se crea el `workloom_item` correspondiente.
5. **audit**: se cierra `ambient_cycle`, se escribe `audit_log` y se actualizan metricas.

Puntos de control donde se verifica kill switch:
- Inicio del ciclo.
- Antes de cada detector.
- Antes de convertir `ambient_proposal` a `workloom_item` visible.

## 7. Scheduler

- Se utiliza **APScheduler** como scheduler interno del proceso `faberloom-api`.
- Job principal: `ambient_cycle_global(tenant_id)`.
- Frecuencia: configurable via `ambient_config.global_frequency_min` (default 30 min, min 15 min).
- El job global itera sobre workspaces activos (`workspace.is_active = true`) y dispara un sub-ciclo por workspace respetando `per_workspace_frequency_min`.
- Fuera de la ventana configurada (`cycle_window_start` a `cycle_window_end` en `cycle_window_tz`), el scheduler no dispara ciclos programados, salvo que exista un evento critico:
  - `routine_run` en estado `failed`.
  - Budget del workspace consumido al > 90%.
  - `kb_source` con `stale_data_block` marcado como bloqueante.
- Los ciclos manuales y de retry se registran con `trigger=manual` / `trigger=retry`.

## 8. Detectores iniciales

Cada detector es una funcion pura `detect(ctx: Context, conn: sqlite3.Connection) -> list[AmbientFinding]`. Sus queries son de solo lectura y siempre scopadas por `tenant_id` + `workspace_id`.

### 8.1 `unanswered_email`
- **Entrada**: `mail_message` con `direction=inbound`, `status=unprocessed`, `workspace_id`.
- **Condicion**: correos sin `draft` asociado creado en las ultimas 24 h.
- **Severidad**: `medium` (alta si `urgency=high`).
- **Evidencia**: `message_id`, `from_address`, `subject`, `received_at`.
- **Propuesta**: "Correo de {from} sin respuesta preliminar".

### 8.2 `stale_kb_source`
- **Entrada**: `kb_source` con `stale_data_block` o `next_review_at < now`.
- **Condicion**: fuentes con fecha de revision vencida o flag de bloqueo activo.
- **Severidad**: `high` si bloquea; `low` si solo advertencia.
- **Evidencia**: `source_id`, `title`, `last_reviewed_at`, `stale_reason`.
- **Propuesta**: "Fuente KB vencida: {title}".

### 8.3 `stuck_hitl`
- **Entrada**: `routine_run` con `status=requires_hitl` o `draft` con `status=pending_approval`.
- **Condicion**: item en estado HITL por mas de 4 h.
- **Severidad**: `medium`.
- **Evidencia**: `run_id`/`draft_id`, `created_at`, `assigned_to`.
- **Propuesta**: "Pendiente HITL estancado: {title} (hace {delta})".

### 8.4 `failed_routine`
- **Entrada**: `routine_run` con `status=failed`.
- **Condicion**: fallas en las ultimas 24 h no atendidas.
- **Severidad**: `high`.
- **Evidencia**: `run_id`, `routine_id`, `error_summary`, `failed_at`.
- **Propuesta**: "Rutina fallida: {routine_name} ({error_summary})".

### 8.5 `budget_exhaustion`
- **Entrada**: `usage_record` + `workspace_routing_policy`.
- **Condicion**: uso acumulado del dia > 90% del budget del workspace o del tenant.
- **Severidad**: `critical`.
- **Evidencia**: `spent_usd`, `budget_usd`, `pct_used`.
- **Propuesta**: "Budget de routing al {pct}% — riesgo de corte".

### 8.6 `gold_candidate_unchanged`
- **Entrada**: `gold_candidate` con `state=candidate`.
- **Condicion**: candidato sin revision en > 7 dias.
- **Severidad**: `low`.
- **Evidencia**: `candidate_id`, `routine_id`, `created_at`.
- **Propuesta**: "Candidato gold sin revisar: {candidate_id}".

## 9. Limites duros

| Limite | Valor default | Configurable | Nota |
|---|---|---|---|
| Acciones permitidas | read + create WorkLoom item | NO | Nunca update/delete/send |
| Max propuestas por ciclo/workspace | 10 | SI, min 3 | Evita spam |
| Frecuencia global minima | 30 min | SI, min 15 min | |
| Frecuencia por workspace | 60 min | SI, min 30 min | |
| Budget ciclo ambiental | 5% del budget diario del router | SI, min 1% | |
| Ventana activa | 06:00-22:00 America/Bogota | SI | Fuera: solo criticos |
| Kill switch | global + por workspace | SI | Verificado antes de cada detector |
| Tools allowlist | `read_workspace`, `read_kb`, `read_inbox`, `create_workloom_item` | NO | Cualquier otro tool = P0 |
| Escritura derivada | `write_workspace_brief` | NO | Dato regenerable (R12), sin efecto externo; el *brief writer* escribe solo `workspace_brief` como cache derivada INDEX-only |

## 10. Dark-launch

- Durante `dark_launch_days` (default 14) a partir del primer despliegue de E2-5, el ciclo corre con `dark_launch_mode=true`.
- En dark-launch:
  - Los detectores se ejecutan normalmente.
  - Se generan `ambient_proposal` con `state=dark`.
  - **NO** se crean items visibles en WorkLoom.
  - Se auditan ruido/utilidad y costo.
- Criterio de salida (decision del curador/CEO):
  - Al menos 5 ciclos completados.
  - Utilidad estimada >= 25% (propuestas que serian aceptadas en simulacion).
  - 0 detectores con 3 fallos consecutivos.
  - 0 cost overruns.
- Una vez aprobado, `dark_launch_mode=false` y las propuestas pasan a `state=visible`.

## 11. Deduplicacion

- Cada propuesta calcula una clave estable:
  ```
  dedup_key = sha256(detector_slug + "|" + target_type + "|" + target_id + "|" + temporal_bucket)
  ```
  donde `temporal_bucket` es la fecha UTC truncada a hora (p. ej. `2026-07-06-14`).
- Antes de crear una nueva `ambient_proposal`, se busca una propuesta existente en el mismo workspace/tenant con:
  - mismo `dedup_key`, y
  - `state IN ('dark', 'visible', 'merged')`, y
  - `created_at > now - interval '24 hours'`.
- Si existe:
  - Se anexa la nueva evidencia al campo `evidence_json` de la existente (append con timestamp).
  - Se incrementa un contador `occurrence_count`.
  - No se crea duplicado.
- Si no existe, se crea nueva.

## 12. Backoff y circuit breakers

### 12.1 Backoff por error
- Si un detector falla, se programa reintento con espera `min(2^n * 60 segundos, 4 horas)`.
- Despues de 3 fallos consecutivos, el detector se marca `disabled` en `ambient_detector_run` y no se ejecuta hasta revision manual.
- El resto del ciclo continua.

### 12.2 Circuit breaker de utilidad
- Se evalua al cerrar cada ciclo.
- Si `aceptadas / creadas < utility_threshold_pct` (default 20%) durante 3 ciclos consecutivos:
  - Se pausan los ciclos automaticos (`ambient_cycle.status=utility_breaker`).
  - Se alerta al admin.
  - Reanudacion manual o tras ajuste de detectores.

### 12.3 Circuit breaker de costo
- Si un ciclo consume mas del `cost_overrun_pct` (default 150%) de su budget asignado:
  - Se detienen los detectores restantes.
  - El ciclo termina con `status=cost_overrun`.
  - Se registra `cost_overrun` en auditoria.

## 13. Metricas de ruido y utilidad

### 13.1 Definiciones
- **Ruido**: propuestas creadas que no reciben accion del usuario dentro de 7 dias.
- **Utilidad**: propuestas aceptadas (movidas a `in_progress` o `done`) / propuestas creadas, en ventana de 7 dias.
- **Costo por propuesta util**: `cost_usd / propuestas_aceptadas`.

### 13.2 Umbrales de alarma

| Metrica | Verde | Amarillo | Rojo |
|---|---|---|---|
| Utilidad 7d | >= 25% | 10-24% | < 10% |
| Ruido 7d | <= 60% | 61-80% | > 80% |
| Costo/ciclo | <= budget | budget-150% | > 150% |
| Latencia ciclo | <= 5 min | 5-10 min | > 10 min |
| Detectores fallidos | 0 | 1-2 | >= 3 |

### 13.3 Dashboard minimo
- Serie temporal de utilidad y ruido (ultimas 4 semanas).
- Costo acumulado vs budget diario.
- Kill switches activos (global / workspace).
- Lista de detectores con fallos consecutivos.

## 14. Auditoria por ciclo

Cada ciclo cierra con un evento `audit_log`:

```json
{
  "action": "ambient_cycle.completed",
  "cycle_id": "cyc_...",
  "tenant_id": "tnt_...",
  "workspace_id": "ws_...",
  "status": "completed",
  "detectors_run": 5,
  "detectors_failed": 0,
  "proposals_created": 3,
  "proposals_visible": 0,
  "proposals_dark": 3,
  "cost_usd": 0.0042,
  "budget_usd": 0.25,
  "kill_switch_state": {"global": true, "workspace": true},
  "utility_score_pct": 33
}
```

Ademas, cada detector escribe `audit_log` con:
- `action`: `ambient_detector.run` / `ambient_detector.failed` / `ambient_detector.skipped`.
- `detector_slug`, `proposals_count`, `cost_usd`, `latency_ms`, `status`.
- `evidence_json` con resultados resumidos.

Cada `ambient_proposal` publicada genera:
- `action`: `ambient_proposal.created` / `ambient_proposal.merged` / `ambient_proposal.cancelled_by_kill`.
- `dedup_key`, `target_type`, `target_id`, `severity`, `workloom_item_id`.

## 15. API propuesta

### 15.1 Endpoints de administracion

#### GET `/api/admin/ambient/config`
Devuelve `ambient_config` del tenant actual.

#### PATCH `/api/admin/ambient/config`
Actualiza parametros operativos (respetando limites duros). Requiere rol `admin`.

```json
{
  "global_enabled": true,
  "cycle_window_start": "06:00",
  "cycle_window_end": "22:00",
  "global_frequency_min": 30,
  "budget_pct_of_router_daily": 5.0
}
```

#### GET `/api/admin/ambient/workspaces/{workspace_id}/config`
Devuelve `ambient_workspace_config`.

#### PATCH `/api/admin/ambient/workspaces/{workspace_id}/config`
Habilita/deshabilita detectores por workspace. No puede habilitar detectores no allowlistados.

#### POST `/api/admin/ambient/workspaces/{workspace_id}/kill`
Activa/desactiva kill switch por workspace.

```json
{"enabled": false}
```

#### POST `/api/admin/ambient/kill`
Kill switch global.

### 15.2 Endpoints de monitoreo

#### GET `/api/admin/ambient/cycles`
Lista ciclos con filtros (`workspace_id`, `status`, `started_after`).

#### GET `/api/admin/ambient/cycles/{cycle_id}`
Detalle del ciclo incluyendo `ambient_detector_run` y `ambient_proposal`.

#### GET `/api/admin/ambient/metrics`
Metricas agregadas: utilidad, ruido, costo, detectores fallidos.

### 15.3 Endpoint manual

#### POST `/api/admin/ambient/trigger`
Dispara un ciclo manual para un workspace o para todo el tenant. Requiere rol `admin`.

```json
{
  "workspace_id": "ws_...",
  "trigger": "manual"
}
```

### 15.4 Reglas de acceso
- `admin`: lectura/escritura completa.
- `curador`: lectura, puede activar kill switch workspace.
- `AM`: solo lectura de metricas de sus workspaces asignados.

## 16. Seguridad y controles

1. **Tool allowlist hardcoded**: solo `read_workspace`, `read_kb`, `read_inbox`, `create_workloom_item`. Cualquier intento de usar otro tool es un P0.
2. **No inyeccion via contenido**: los detectores leen datos ya saneados por los canaries de E1/E2; no ejecutan parsers nuevos sin canarios.
3. **Scope forzado**: toda query usa `Context`. Tests canario deben fallar si se omite `tenant_id` o `workspace_id`.
4. **Presupuesto fail-closed**: si no se puede calcular el budget, el ciclo no corre.
5. **Kill switch testable**: test que activa el kill a mitad del ciclo y verifica que no se creen mas propuestas.
6. **Dark-launch por tenant**: no se libera a visible sin decision humana.

## 17. Tests y canarios

### 17.1 Unitarios
- `test_ambient_cycle_lifecycle`: transiciones de estado.
- `test_detector_allowlist`: un detector que intente tool no permitido falla.
- `test_dedup_key`: duplicados dentro de 24h se mergean.
- `test_kill_switch_global`: con kill global no corre ningun detector.
- `test_kill_switch_workspace`: con kill por workspace no corre para ese workspace.

### 17.2 Integracion
- `test_ambient_end_to_end`: ciclo completo con 1 detector, 1 propuesta, auditoria.
- `test_dark_launch`: propuestas en dark no aparecen en WorkLoom.
- `test_circuit_breaker_utility`: 3 ciclos de baja utilidad pausan el scheduler.
- `test_circuit_breaker_cost`: cost overrun detiene el ciclo.

### 17.3 Canarios de no-irreversibilidad
- `test_cannot_send_email`: la entidad no puede invocar `send_message`.
- `test_cannot_delete_data`: la entidad no puede borrar workspace/chat/kb/source.
- `test_cannot_update_routine`: la entidad no puede modificar rutinas.
- `test_cannot_exfiltrate`: la entidad no puede leer workspaces de otro tenant.

### 17.4 Canarios de fuga cross-workspace
- `test_proposal_is_scoped`: una propuesta creada para `ws_A` no es visible desde `ws_B`.
- `test_detector_query_scoped`: query de detector sin `workspace_id` devuelve 0 filas.

## 18. Plan de implementacion y DoD

### 18.1 Orden sugerido
1. Migracion de tablas (`ambient_config`, `ambient_workspace_config`, `ambient_detector`, `ambient_cycle`, `ambient_proposal`, `ambient_detector_run`).
2. Seed de detectores iniciales.
3. Implementar `AmbientOrchestrator` y fases del ciclo.
4. Implementar 3 detectores criticos (`unanswered_email`, `stuck_hitl`, `failed_routine`).
5. Scheduler APScheduler con ventana y frecuencia.
6. Dark-launch y deduplicacion.
7. Backoff y circuit breakers.
8. API admin y dashboard.
9. Tests unitarios + integracion + canarios.
10. QA negativa de no-irreversibilidad.

### 18.2 Definition of Done
- [ ] Tablas creadas con campos latentes e indices.
- [ ] Detectores iniciales ejecutandose en dark-launch.
- [ ] Kill switch global y por workspace funcionando.
- [ ] Deduplicacion activa (< 5% de duplicados en 7 dias).
- [ ] Backoff y circuit breakers probados.
- [ ] Metricas de utilidad/ruido visibles.
- [ ] Auditoria por ciclo escrita.
- [ ] Canarios P0 de no-irreversibilidad pasan.
- [ ] Canarios de fuga cross-workspace pasan.
- [ ] Gate E2-5: 0 acciones irreversibles; >= 1 propuesta util aceptada por semana.

## 19. Changelog

- v1.1 (2026-07-11): E4-1 enmienda — se exceptúa explícitamente `write_workspace_brief` de la tool allowlist dura. Justificación: el brief es un dato derivado regenerable (R12), generado INDEX-only, sin efecto externo, sin modificar KB/rutinas/correo; su único output es la tabla `workspace_brief` bajo el ciclo ambiental con los mismos límites de ventana/budget/kill switch.
- v1.0 (2026-07-06): Creacion. Especificacion tecnica del ciclo ambiental E2-5 con modelo de datos, detectores, limites duros, dark-launch, deduplicacion, backoff, metricas, auditoria, API y tests.
