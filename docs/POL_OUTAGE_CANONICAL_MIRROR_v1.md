# POL_OUTAGE_CANONICAL_MIRROR -- Continuidad operativa ante outage del repo canonico

---
id: POL_OUTAGE_CANONICAL_MIRROR
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: POL
stamp: VIGENTE -- 2026-05-07
aprobador: CEO
aplica_a: [MWT, FaberLoom]
relacionado: POL_BRANCH_PR_v1.md · POL_ROOT_FILE_CLASSIFICATION_v1.md · SPEC_HOOKS_FAIL_CLOSED_v1.md · CLAUDE.md (source of truth canonico)
data_classification: N1
---

## Declaracion

Define comportamiento del pipeline KB cuando el repo canonico (`C:\dev\mwt-knowledge-hub`) esta inaccesible, corrompido o desincronizado del mirror OneDrive. Cubre deteccion, modo degradado, buffer staging, recuperacion y autoridad para declarar/levantar outage.

**Source of truth** sigue siendo el repo canonico. Mirror OneDrive es **read/write transitorio**, no autoridad. Esta POL no cambia esa regla -- la blinda contra escenarios de continuidad.

---

## Por que este documento existe

Pipeline canonico actual (post Sprint 0):

```
Cowork (AG-07) --escribe--> mirror OneDrive (generated_staging)
                                |
                                v
                          sync_*_indexa.ps1
                                |
                                v
                       repo canonico C:\dev\mwt-knowledge-hub
                                |
                                v
                           git push origin main
                                |
                                v
                          mirror_to_onedrive.ps1
                                |
                                v
                          mirror OneDrive (sync de vuelta)
```

Single point of failure: si el canonico cae (disco, corrupcion git, OneDrive bloqueando lock, hooks fail-closed por config invalida), TODO el flujo se bloquea. Sin politica explicita, Cowork puede acumular cambios huerfanos en mirror sin trazabilidad y al recuperar canonico se pierden o sobrescriben.

R3#11 hallazgo: hooks fail-closed activos amplifican el riesgo -- una config corrupta deja todo bloqueado sin canal de recuperacion declarado.

---

## Las 7 reglas cementadas

### R1 -- Estados canonicos del pipeline

Solo 3 estados validos:

| Estado | Significado | Quien escribe a canonico | Cowork puede escribir mirror |
|---|---|---|---|
| `HEALTHY` | Canonico accesible, working tree clean o branch activa esperada, hooks OK | sync_*_indexa.ps1 (actor unico) | SI -- generated_staging |
| `DEGRADED` | Canonico accesible pero un sync fallo (hash mismatch, push reject, mirror exit >=8). Recuperable sin intervencion CEO | NADIE hasta resolver. Bloqueado | SI -- generated_staging con flag pendiente |
| `OUTAGE` | Canonico inaccesible, corrupto, o desync >24h con remote. Requiere intervencion CEO | NADIE | SI -- buffer staging con SLA 7 dias max |

Transiciones: `HEALTHY -> DEGRADED -> HEALTHY` automatico (re-sync corrige); `DEGRADED -> OUTAGE` por SLA o por declaracion CEO; `OUTAGE -> HEALTHY` requiere reconciliacion manual + CEO declara.

### R2 -- Detectores de outage

Cualquiera de estas condiciones detectadas dispara escalacion (DEGRADED minimo, OUTAGE si persiste):

| Detector | Umbral | Accion |
|---|---|---|
| `git status` falla en canonico | 1 fallo | DEGRADED + reintentar 3x con backoff |
| `git fetch origin` falla | 3 fallos consecutivos | DEGRADED |
| `git push` rechazado por hash divergence | 1 vez | DEGRADED -- requiere rebase/merge manual |
| `mirror_to_onedrive.ps1` exit code >=8 | 1 vez | DEGRADED |
| `hooks/config.json` hash mismatch | 1 vez | OUTAGE -- hooks fail-closed bloquearan todo |
| Working tree dirty con archivos no listados en manifest activo | 1 vez | DEGRADED -- sync abort |
| Drift mirror vs canonico >100 archivos | check semanal | DEGRADED |
| Drift mirror vs canonico >24h sin sync | timestamp ultimo commit | OUTAGE |

Detector run-time: cada `sync_*_indexa.ps1` ejecuta R2 antes de Fase 1. Detector continuo: scheduled task semanal `kb_health_check.ps1` (futuro -- no parte de este POL).

### R3 -- Modo degradado

Cuando estado = DEGRADED:

1. **Cowork sigue escribiendo a mirror** bajo categoria `generated_staging` (per POL_ROOT_FILE_CLASSIFICATION_v1).
2. **Sync scripts NO ejecutan** -- abortan en Fase 0 con mensaje "DEGRADED: ver POL_OUTAGE_CANONICAL_MIRROR R2".
3. **Cowork agrega flag** `degraded_pending: true` en frontmatter de archivos nuevos.
4. **CEO o ejecutor recupera** corriendo `recover_canonical.ps1` (futuro) o secuencia manual:
   - `git fetch origin && git reset --hard origin/main` si divergence en local
   - `mirror_to_onedrive.ps1` con verbose para identificar archivos con conflict
   - Re-correr sync_*_indexa.ps1 fallido
5. **Estado vuelve a HEALTHY** cuando un sync subsecuente completa sin error.

### R4 -- Modo outage (CEO-only declarable)

Cuando estado = OUTAGE:

1. **Cowork NO escribe a mirror para promocion futura**. Sigue escribiendo a `outputs/` temporales o a `generated_staging` con flag `outage_buffer: true`.
2. **SLA buffer: 7 dias max**. Pasados 7 dias sin recuperar canonico, escalar a contingencia (re-clone desde GitHub remote a nueva ruta canonica).
3. **CEO declara OUTAGE** explicitamente con archivo `OUTAGE_DECLARED_<timestamp>.md` en raiz mirror. Contenido minimo: causa, archivos huerfanos en buffer, ETA recuperacion.
4. **CEO declara recovery** explicitamente removiendo el archivo y ejecutando `reconcile_outage.ps1` (futuro -- secuencia manual hoy).
5. **Reconciliacion** lista archivos en buffer, los promueve uno por uno con manifest selectivo, hash verifica cada uno contra estado pre-outage, escala conflictos a CEO.

### R5 -- Cowork autonomy en outage

Durante OUTAGE, Cowork PUEDE:

- Leer mirror (sin escritura promovible)
- Escribir `generated_staging` con flag `outage_buffer: true`
- Operar workspace folder y outputs temporales sin restriccion
- Generar reportes, drafts, exploraciones sin tocar `canonical_docs`

Cowork NO PUEDE:

- Ejecutar sync_*_indexa.ps1 (sin canonico no hay destino)
- Modificar archivos `control_surface` (hooks/config.json siempre bloqueado, agravado en outage)
- Declarar fin de outage (solo CEO)
- Generar manifests con archivos `canonical_docs` para sync futuro mientras outage activo (acumular es OK, promover NO)

### R6 -- Trazabilidad obligatoria

Toda transicion de estado registra:

| Evento | Registro |
|---|---|
| DEGRADED -> dispara | Append a `audit/canonical_health.log` con timestamp, detector, archivos afectados |
| OUTAGE -> declarado | Archivo `OUTAGE_DECLARED_<ts>.md` en raiz mirror + append a CAMBIOS_v2 con BATCH "OUTAGE_DECLARATION" |
| OUTAGE -> recovered | Append a CAMBIOS_v2 con BATCH "OUTAGE_RECOVERED" listando archivos reconciliados |
| HEALTHY restaurado | Implicito en proximo sync exitoso, no requiere doc separado |

### R7 -- Backups recurrentes (precondicion implicita)

Esta POL asume:

- `git push origin main` es backup remoto (GitHub) -- valida si remote esta accesible
- Mirror OneDrive es backup read-only del estado pre-outage
- Snapshot semanal del canonico a disco externo o cloud (CEO operativo, no automatizado en v1)

Si remote GitHub tambien cae simultaneo con canonico local: declarar OUTAGE y operar 100% desde mirror hasta recuperar uno de los dos.

---

## Implementacion por agente

| Agente | Implementacion concreta |
|---|---|
| Cowork (AG-07) | Lee `OUTAGE_DECLARED_*.md` al inicio de cada sesion. Si existe, opera modo R5. Si no, asume HEALTHY hasta detector R2 indique lo contrario. |
| Claude Code (AG-02) | Idem Cowork. Adicionalmente respeta hooks/config.json hash check (R2 detector). |
| sync_*_indexa.ps1 | Fase 0 nueva: ejecutar R2 detectores antes de Fase 1. Abortar si DEGRADED u OUTAGE. |
| CEO | Autoridad unica para declarar OUTAGE y RECOVERED. |

---

## Anti-patrones explicitos

| Anti-patron | Por que falla |
|---|---|
| Cowork escribe directo a canonico via WSL/Bash sin sync script | Bypass del actor `sync_indexa_script` -- viola POL_ROOT_FILE_CLASSIFICATION_v1 |
| Promover archivos `outage_buffer: true` sin reconciliacion | Mezcla estado pre/post outage sin verificar conflictos |
| Declarar OUTAGE sin documento explicito | Sin trazabilidad, recovery posterior pierde causa raiz |
| Operar >7 dias en buffer sin escalar | SLA roto, riesgo perdida progresiva de cambios |
| Editar `OUTAGE_DECLARED_*.md` retroactivamente | Viola POL_INMUTABILIDAD -- el archivo es snapshot |

---

## Riesgos asumidos

- **Detector continuo no automatizado en v1.** Dependemos de cada sync script ejecutar R2 al inicio. Mitigacion futura: scheduled task `kb_health_check.ps1` cada 6h.
- **CEO single point para declarar.** Si CEO indispuesto >7 dias, no hay backup de autoridad. Mitigacion futura: delegacion explicita en POL bump.
- **Buffer 7 dias arbitrario.** Sin medicion historica de outages reales. Revisable en v2 con datos.
- **Reconciliacion manual.** Script `reconcile_outage.ps1` no existe en v1. Recovery hoy es secuencia manual con riesgo de error humano.

---

## Changelog

```
v1.0 (2026-05-07): Creacion. Origen: PLAN_INTEGRACION_v4_POST_ROUND3.md A1.1.
                   Hallazgo R3#11: hooks fail-closed amplifican riesgo de outage
                   sin canal de recuperacion declarado. Define 3 estados, 7 reglas,
                   autoridad CEO para outage formal, SLA buffer 7 dias.
```

---

Ultima actualizacion: 2026-05-07 v1.0
Generado por: Cowork (AG-07) -- Arquitecto Ejecutor
