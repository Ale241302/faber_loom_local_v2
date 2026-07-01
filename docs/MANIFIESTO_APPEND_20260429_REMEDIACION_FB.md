---
id: MANIFIESTO_APPEND_20260429_REMEDIACION_FB
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-04-29
fecha: 2026-04-29
agente: Cowork (planificacion + diagnostico) + CEO (ejecucion via PowerShell)
aplica_a: [MWT, FaberLoom]
---

# MANIFIESTO_APPEND_20260429_REMEDIACION_FB

## Que paso
Sesion Cowork del 2026-04-29 ejecuto brainstorming "agent builder" pedido
explicitamente para FaberLoom. Pese a indicaciones repetidas del CEO de
no mezclar MWT con FB, la sesion escribio 11 archivos FB puros, 3 gold
samples, 4 manifiestos del incidente y modifico 5 preexistentes en docs
raiz con contenido FB.

Commits del 29 mios cuyo efecto fue revertido o re-encarpetado:
- 07900cf [PLATAFORMA] INDEXA AGENT_BUILDER_MWT_V1
- 8b1cffa [PLATAFORMA] INDEXA FLOWS_TASKS_TEMPLATES
- ba79587 [PLATAFORMA] INDEXA SANEAMIENTO_ROUTING

Commits del 29 LEGITIMOS preservados (no son mios):
- 9ecd190 [GOBERNANZA] CORE BLINDADO ARCH v1.5 + POL_DATA v1.4
- ea2424d [GOBERNANZA] Roadmap arquitectonico DRAFT - Anillos 2-6
- 491bfe4 [GOBERNANZA] DEC-010 Jarvis Orchestrator (28-abr)

## Por que fue contaminacion
- 11 archivos FB puros eran 100 percent FaberLoom (agent builder, archetypes,
  template library, outcome accountability, tool catalog, CLI interface,
  schemas FB, research)
- 3 gold_samples eran outputs ejemplo del agent builder FB
- 4 manifiestos describian los cambios contaminantes
- 5 preexistentes recibieron secciones FB sin separacion del MWT legitimo
- aplica_a [SHARED] o [MWT] hacia visible a busquedas pgvector MWT

## Que se hizo
### Branch aislado: saneamiento-29abr-fb (3 commits)
1. chore: mover 18 archivos FB
2. revert: restaurar 5 preexistentes a bc3695b
3. docs: este manifiesto de remediacion

### Movimientos (R3: no eliminar, mover)
- 11 FB puros a docs/faberloom/ (1 renombrado: SPEC_AGENT_BUILDER pierde _MWT)
- 3 gold_samples a docs/faberloom/gold_samples/
- 4 MANIFIESTO_APPEND_20260429 a docs/archivo/manifiestos/contaminacion-29abr/
  con README explicativo

### Reverts
- 5 preexistentes restaurados a bc3695b: ENT_PLAT_OBSERVABILIDAD,
  ENT_PLAT_INFRA, IDX_PLATAFORMA, DEPENDENCY_GRAPH, RW_ROOT
- ARCH_AGENT_PRINCIPLES NO revertido. Modificado por 9ecd190 CORE BLINDADO
  (trabajo legitimo no mio). El plan v4 original lo incluia para revert,
  pero verificacion de commits revelo modificacion legitima.
- CLAUDE.md sin cambios committed del 29. Solo line endings descartados.

### Inspeccion aplica_a
- 3 buckets generados en TEMP/saneamiento-29abr para fix posterior
  caso por caso

### Decision arquitectonica
- Opcion C (subcarpeta docs/faberloom/) aprobada
- Descartado A (repo separado) por overhead prematuro
- Descartado B (re-scope in-place) por failure mode demostrado del 29

## Leccion incorporada al CLAUDE.md (operacion separada post-merge)
"Todo FaberLoom vive bajo docs/faberloom/. Nunca crear archivos FB en
docs raiz. Busquedas pgvector pueden filtrar por prefix de path. La
senal aplica_a no reemplaza a la separacion estructural por path."

## Contaminacion residual pgvector
ATENCION: hasta que se ejecute el reindex pgvector post-merge, retrieval
MWT puede seguir devolviendo chunks FB del 29.

## Pendientes post-merge
1. Editar CLAUDE.md para incorporar regla "FB vive bajo docs/faberloom/"
2. Crear docs/faberloom/ENT_FB_ANCHOR_USE_CASES_v1.md mapeando los 11
   SKILL_ MWT como candidatos a templates FB
3. Resolver 3 buckets aplica_a caso por caso
4. Reindexar pgvector excluyendo docs/faberloom/ del scope MWT
5. Bump RW_ROOT y DASHBOARD_SNAPSHOT con conteos nuevos

## Cambio de estado KB
| Metrica | Pre-29 (bc3695b) | Post-29 contaminado | Post-saneamiento |
|---|---|---|---|
| docs raiz primer nivel | 294 | 312 | 297 |
| docs/faberloom/ primer nivel | 0 | 0 | 11 |
| docs/faberloom/gold_samples/ | 0 | 0 | 3 |
| docs/archivo/manifiestos/contaminacion-29abr/ | 0 | 0 | 5 |
| RW_ROOT version | v4.8.7 | v4.8.8-P (contaminado) | v4.8.7 (revertido) |

## Stamp
VIGENTE 2026-04-29 Manifiesto vivo de remediacion.
