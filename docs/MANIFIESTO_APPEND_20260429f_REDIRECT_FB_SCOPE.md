---
id: MANIFIESTO_APPEND_20260429f_REDIRECT_FB_SCOPE
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-04-29f
fecha: 2026-04-29
agente: Cowork (re-scope de los 11 archivos del dia) + CEO (autorizacion + ejecucion git)
aplica_a: [FaberLoom]
---

# MANIFIESTO_APPEND_20260429f_REDIRECT_FB_SCOPE

## Que paso
Cierre del incidente del 29-abr. Los 11 archivos que durante el dia se redactaron con scope MWT por error de scoping fueron re-escritos con scope FaberLoom nativo. El contenido conceptual del dia (las 19 decisiones D1-D19, los 7 arquetipos, manifest v2, flow DAG, tasks, templates, tool catalog, CLI, P15) era valido para FB; solo el lenguaje, los ejemplos y el sujeto/objeto estaban invertidos.

## Cambios concretos

### 1. Reescritura de los 11 archivos en docs/faberloom/
Cada archivo recibio:
- ID renombrado con prefijo FB: `SCH_FB_*`, `ENT_FB_*`, `POL_FB_*`, `SPEC_FB_*`
- `aplica_a:` -> `[FaberLoom]` (eliminado [MWT] y [MWT, FaberLoom] cross)
- `domain:` -> `FaberLoom (docs/faberloom/)`
- Declaracion: scope FB platform, MWT como primer tenant beta donde aplica
- Cuerpo: ejemplos del primer tenant MWT preservados como caso real validado
- Bump version a 2.0
- Changelog: entry v2.0 documentando el re-scope

### 2. Tabla de renames (filename fisico)

| Filename viejo | Filename nuevo |
|---|---|
| SPEC_AGENT_BUILDER_v1.md | SPEC_FB_AGENT_BUILDER_v1.md |
| SCH_SKILL_MANIFEST_v2.md | SCH_FB_SKILL_MANIFEST_v2.md |
| SCH_FLOW_DAG.md | SCH_FB_FLOW_DAG.md |
| SCH_TASK_ENTITY.md | SCH_FB_TASK_ENTITY.md |
| SCH_CLI_INTERFACE.md | SCH_FB_CLI_INTERFACE.md |
| ENT_AGENT_ARCHETYPES_v1.md | ENT_FB_AGENT_ARCHETYPES_v1.md |
| ENT_TEMPLATE_LIBRARY_v1.md | ENT_FB_TEMPLATE_LIBRARY_v1.md |
| ENT_TOOL_CATALOG_v1.md | ENT_FB_TOOL_CATALOG_v1.md |
| POL_OUTCOME_ACCOUNTABILITY.md | POL_FB_OUTCOME_ACCOUNTABILITY.md |
| ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md | ENT_FB_RESEARCH_AGENT_ECOSYSTEM_2026-04.md |
| ENT_RESEARCH_FABERLOOM_KIMI_2026-04.md | (sin cambio, ya FB-named) |

### 3. Cambios estructurales clave

- **Multi-tenant base desde dia 1**: tabla `tasks`, `episodic_memory`, dashboards Langfuse incluyen `tenant_id` aunque en FB v1 beta exista solo el tenant MWT. Evita migracion traumatica cuando entre tenant 2.
- **D17 (config en data) reposicionado** como BASE DEL MULTI-TENANT FB v1, no como feature multi-cliente del tenant MWT.
- **CLI cambia de `mwt` a `fbl`** con `--tenant=mwt` default en v1.
- **Multi-tenant cripto/A2A/profile system/marketplace** -> diferido explicitamente a FB v2 con segundo tenant LOI/pagante.
- **Deuda tecnica documentada**: namespace `metadata.mwt.*` queda con alias futuro a `metadata.fbl.*`.

## Por que se hizo asi

El usuario aclaro post-saneamiento: "todo lo del dia esta conceptualizado para FB; lo unico para MWT era que MWT se conecta a FB como tenant cuando exista". Cambiar solo `aplica_a:` (acta cosmetico) era insuficiente; el cuerpo de cada archivo seguia narrado como MWT-internal. Re-escritura sustantiva con FB como sujeto y MWT como primer tenant beta.

NO se reinvento contenido. Las 19 decisiones D1-D19, los 7 arquetipos, las validaciones, el plan 12 semanas, el sistema de metricas L0-L5, los anti-patterns: todo se preserva conceptualmente. Solo cambia la posicion del sujeto/objeto.

## Lo que NO se hizo

1. **NO se actualizo el contenido a multi-tenant cripto**. Eso es FB v2. El contenido v1 sigue siendo single-tenant beta con MWT, escalable a multi-tenant via D17 (config en data).
2. **NO se renombro `metadata.mwt.*` a `metadata.fbl.*`** en el namespace del manifest schema. Eso rompe SKILLs existentes del tenant MWT. Queda como deuda tecnica con backward-compat alias.
3. **NO se reescribieron los SPEC_FABERLOOM_* preexistentes** (MVP, ARCHITECTURE, AGENT_COMPOSITION, SKILL_COMPOSITION, WORKFLOW_ENGINE). Esos viven en docs/ raiz por lazy migration y son independientes de los re-scopeados hoy.
4. **NO se ajustaron los SKILL_ del tenant MWT en docs/ raiz**. Eso aplica cuando el tenant MWT migre sus 11 SKILLs al manifest v2 en Fase 1 del SPEC_FB_AGENT_BUILDER_v1.

## Archivos creados/modificados

| Archivo | Accion |
|---|---|
| docs/faberloom/SPEC_AGENT_BUILDER_v1.md | reescrito v1.2->v2.0 + (rename pendiente fisico) |
| docs/faberloom/SCH_SKILL_MANIFEST_v2.md | reescrito header + changelog (rename pendiente) |
| docs/faberloom/SCH_FLOW_DAG.md | reescrito header + changelog (rename pendiente) |
| docs/faberloom/SCH_TASK_ENTITY.md | reescrito header + changelog (rename pendiente) |
| docs/faberloom/SCH_CLI_INTERFACE.md | reescrito header + nota CLI fbl + changelog (rename pendiente) |
| docs/faberloom/ENT_AGENT_ARCHETYPES_v1.md | reescrito header + changelog (rename pendiente) |
| docs/faberloom/ENT_TEMPLATE_LIBRARY_v1.md | reescrito header + proposito + changelog (rename pendiente) |
| docs/faberloom/ENT_TOOL_CATALOG_v1.md | reescrito header + declaracion + changelog (rename pendiente) |
| docs/faberloom/POL_OUTCOME_ACCOUNTABILITY.md | reescrito header + changelog (rename pendiente) |
| docs/faberloom/ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md | reescrito header + changelog (rename pendiente) |
| docs/faberloom/ENT_RESEARCH_FABERLOOM_KIMI_2026-04.md | refs cruzadas actualizadas |
| docs/MANIFIESTO_APPEND_20260429f_REDIRECT_FB_SCOPE.md | nuevo (este archivo) |

## Pendientes post-merge

1. Renombrar archivos fisicos via `git mv` (script provisto en mismo branch).
2. Buscar refs externas a los nombres viejos en docs/ raiz (SPEC_FABERLOOM_*, etc.) y actualizar a nuevos.
3. Reindex pgvector con paths actualizados.
4. Bump RW_ROOT v4.8.8 -> v4.8.9 con entry de re-scope.
5. Bump DASHBOARD_SNAPSHOT v11.0 -> v11.1.

## Stamp
VIGENTE 2026-04-29f - Manifiesto de cierre del re-scope FB. Las 11 piezas del agent builder de FB ahora tienen identidad consistente.
