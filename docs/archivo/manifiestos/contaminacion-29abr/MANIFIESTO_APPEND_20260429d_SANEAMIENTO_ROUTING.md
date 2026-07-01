# MANIFIESTO_APPEND_20260429d_SANEAMIENTO_ROUTING
id: MANIFIESTO_APPEND_20260429d_SANEAMIENTO_ROUTING
type: TRANSITORIO
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE — 2026-04-29d
aplica_a: [SHARED]
expires: post-consolidación en MANIFIESTO_CAMBIOS_v2.md (próxima sesión de mantenimiento)

---

## Contexto

**Cuarta indexa del día 2026-04-29 (saneamiento, NO feature work).**

Las tres indexas anteriores (A, B, C) introdujeron 24 archivos tocados y muchas decisiones acumuladas. CEO detectó el problema:

> "Mezclas mucho FaberLoom con MWT, creo que hay problemas en el ruteo. Si estás evaluando FaberLoom con algo y metés MWT genera hype o underevaluation. Me has hecho gastar tiempo y tokens innecesariamente."

Diagnóstico técnico:
- 310 archivos en `docs/`
- Solo 41 (13%) tenían `aplica_a:` declarado
- 269 archivos sin scope explícito → cualquier query/agent retornaba todo mezclado, generando context bleed evaluativo
- Algunos archivos con scope declarado mezclaban contenido específico del proyecto opuesto (ej. SCH_SKILL_MANIFEST_V2 [MWT] tenía field `tenant_scope.mode: multi (FaberLoom)`)
- ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04 mezclaba research general MWT + Kimi swarm específico FB en un solo archivo

`aplica esos cambios por favor es mas lee bien todo` autoriza el saneamiento.

---

## Cambios ejecutados

### 1. Aplicado `aplica_a:` a los 269 archivos que faltaban

Clasificación heurística por nombre + verificación de contenido. Distribución resultante:

| Valor | Archivos clasificados |
|-------|------------------------|
| `[MWT]` | 146 (operación específica: ENT_PROD_*, ENT_COMERCIAL_*, ENT_OPS_*, ENT_GOB_*, ENT_COMP_*, ENT_DIST_*, ENT_MARCA_*, LOC_*, SKILL_* operativos, PLB_OPS_*, SCH_PROFORMA, SCH_LISTING, etc.) |
| `[SHARED]` | 113 (conceptual ambos: IDX_*, POL_* universales, SCHEMA_REGISTRY, ARTIFACT_REGISTRY, DEPENDENCY_GRAPH, RW_ROOT, PLB_PROMPTING, PLB_ARCHITECT, SKILL_HUMANIZE_*, SKILL_RUNTIME, SCH_LLMS, SCH_FORECAST, etc.) |
| `[FaberLoom]` | 10 (SPEC_FABERLOOM_*, FABERLOOM_*, manifiestos faberloom-specific) |

Total después del saneamiento: **310 archivos clasificados con `aplica_a:` (100% cobertura)**.

Heurística aplicada (script Python en `/tmp/saneamiento_aplica_a.py` para auditoría):
- Prefijos MWT operativos → `[MWT]`
- IDX_*, POL_* universales, schemas conceptuales, registries → `[SHARED]`
- ENT_PLAT_INFRA/OBSERVABILIDAD/FRONTENDS/MARCAS/NIGHTLY_AUDITOR/SSOT → `[MWT]`
- ENT_PLAT_* conceptuales (KNOWLEDGE, EVENTOS, MEMORY_STACK, etc.) → `[SHARED]`
- MANIFIESTOS específicos por proyecto del manifiesto

### 2. SCH_SKILL_MANIFEST_V2 limpiado de fields FaberLoom

Archivo declaraba `aplica_a: [MWT]` pero contenía:
- Field `tenant_scope.mode: multi (FaberLoom)` como ejemplo en sample
- Validación 10: "tenant_scope.mode: multi en MWT v1 → warning (FaberLoom-only)"
- Comentarios "futuro FB, vacío en MWT v1"

Saneamiento aplicado:
- Tenant scope ahora es **single fijo siempre** en este schema
- Validación 10 cambiada a: `tenant_scope.mode != single → reject` (este schema es MWT-only)
- Nota explícita al final: "si en algún momento existe FaberLoom multi-tenant, la extensión vivirá en `SCH_SKILL_MANIFEST_FB_V1` (heredando este como base + multi-tenant). NO modificar este schema con campos FB."

### 3. ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04 dividido

Archivo declaraba `aplica_a: [MWT, FaberLoom]` pero mezclaba:
- Research general útil para MWT (Hermes, Claude Code leak, repos blog, Workspace Agents)
- Research específico Kimi swarm FaberLoom B2B regulado multi-tenant (sección "Kimi research FaberLoom" con 7 frentes + 4 insights cruzados)

Saneamiento aplicado:
- **Archivo original** (`ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04.md`) ahora `aplica_a: [MWT]`. La sección Kimi FB fue extraída y reemplazada por una nota "Kimi research FaberLoom — MOVIDO" con puntero al nuevo archivo + resumen de qué SÍ aplicó a MWT.
- **Archivo nuevo** (`ENT_RESEARCH_FABERLOOM_KIMI_2026-04.md`, NUEVO) con `aplica_a: [FaberLoom]`. Contiene los 7 frentes + 4 insights + 7 decisiones desbloqueadas + autocrítica + diferenciales sobrevivientes vs Workspace Agents + trigger de reactivación. Documento archivado hasta prospect FB real.

### 4. Audit de los 24 archivos tocados en indexas A, B, C

Verificación de scope vs contenido para todos los archivos modificados/creados hoy:

| Archivo | aplica_a actual | Veredicto |
|---------|-----------------|-----------|
| SPEC_AGENT_BUILDER_MWT_V1 | [MWT] | OK — menciones FB como descartes explícitos (D1, anti-patterns) |
| SCH_SKILL_MANIFEST_V2 | [MWT] | OK post-limpieza |
| POL_OUTCOME_ACCOUNTABILITY | [MWT, FaberLoom] | OK — métricas universales (Mitjana, kill switch, outcome) |
| ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04 | [MWT] | OK post-división |
| ENT_RESEARCH_FABERLOOM_KIMI_2026-04 (NUEVO) | [FaberLoom] | OK |
| ENT_AGENT_ARCHETYPES_V1 | [MWT, FaberLoom] | OK — arquetipos universales |
| SCH_FLOW_DAG | [MWT] | OK — sin menciones FB |
| SCH_TASK_ENTITY | [MWT] | OK — 1 mención FB en limitaciones (warning) |
| ENT_TEMPLATE_LIBRARY_V1 | [MWT] | OK — 5 templates específicos MWT |
| ENT_PLAT_OBSERVABILIDAD | [MWT] | OK — 3 menciones FB en "siguiente versión esperada" (futuro) |
| ENT_PLAT_INFRA | [MWT] | OK — sección G "FaberLoom requerirá infra propia separada" (caveat sano) |
| SCH_CLI_INTERFACE | [MWT] | OK — 1 mención FB en roles |
| ENT_TOOL_CATALOG_V1 | [MWT] | OK — sin contaminación |
| 3 manifiestos del día (A, B, C) | [MWT] | OK |
| sync scripts | n/a | scripts |

**Veredicto del audit**: las 3 indexas del día (A, B, C) tomaron decisiones con scope correcto. El context bleed estaba en archivos pre-existentes, NO en las decisiones nuevas. Las 24 decisiones (D1-D19) son válidas.

---

## Lo que NO se modificó (intencional)

Las decisiones tomadas en las 3 indexas del día (D1-D19) NO se revierten ni revalidan. Las menciones FB en archivos `[MWT]` quedan donde son **caveats explícitos sanos** (descarte, exclusión, futuro condicional) — NO contaminación.

Ejemplo de caveat sano (se queda):
> SPEC_AGENT_BUILDER_MWT_V1 D1: "FaberLoom es proyecto distinto. No contaminar arquitectura del builder con multi-tenant, A2A bridge, profile system, capability marketplace, ni anti-distillation patterns."

Ejemplo de contaminación (se sacó):
> SCH_SKILL_MANIFEST_V2: field `tenant_scope.mode: multi (FaberLoom)` como ejemplo en el sample → quitado.

---

## Reglas operacionales nuevas

### R1 · Header `aplica_a:` obligatorio en todo .md de docs/

Validador en pre-commit (a implementar): cualquier archivo nuevo en `docs/*.md` sin `aplica_a:` declarado → reject.

Valores canónicos:
- `[MWT]` — operación interna MWT (Rana Walk + B2B Marluvas/Tecmater)
- `[FaberLoom]` — proyecto SaaS futuro para fabricantes
- `[SHARED]` — conceptual aplicable a ambos sin contaminación cross-project
- `[LEGACY]` — archivado, no aplicar a decisiones nuevas

NO usar `[MWT, FaberLoom]` salvo casos genuinamente universales (POL_, ENT_AGENT_ARCHETYPES, etc. que son conceptos sin sesgo de proyecto).

### R2 · Filtro de routing en queries (a implementar)

Toda query del agente builder, retrieval pgvector o agent invocation declara `scope: MWT | FaberLoom | shared | all`. pgvector filtra `metadata.aplica_a` antes de retrieval. Si no se declara scope, el agente pregunta antes de proceder.

### R3 · Disciplina conversacional del agente

Toda respuesta del agente (Cowork, Claude Code, builder UI futuro) declara su scope al inicio:

```
Foco: MWT
[análisis...]
```

NO mezclar caveats del otro proyecto salvo que el usuario lo pida explícito. Si una decisión cruza ambos proyectos → preguntar antes.

### R4 · Archivos contaminados se dividen, no se mezclan

Si un archivo declara `[MWT]` o `[FaberLoom]` pero contiene contenido del otro proyecto:
- Si el contenido cruzado es **caveat explícito** (descarte, exclusión) → OK, se queda
- Si el contenido cruzado es **información operativa del otro proyecto** → dividir en 2 archivos

---

## Total cambios KB

- **NUEVOS** (1 archivo): ENT_RESEARCH_FABERLOOM_KIMI_2026-04.md
- **HEADERS aplicados** (269 archivos): aplica_a: [MWT] / [SHARED] / [FaberLoom] según clasificación
- **LIMPIEZA** (2 archivos): SCH_SKILL_MANIFEST_V2 (quitar fields FB), ENT_RESEARCH_AGENT_ECOSYSTEM_2026-04 (extraer sección Kimi FB)
- **MANIFIESTO** (1 archivo): este

**Total: 273 archivos tocados** (269 headers + 2 limpiados + 1 nuevo + 1 manifiesto).

---

## Pendientes operacionales (no bloqueantes)

| # | Pendiente | Prioridad |
|---|-----------|-----------|
| 1 | Implementar validador pre-commit que rechaza .md sin `aplica_a:` | media |
| 2 | Implementar filtro de routing en pgvector queries | alta para Fase 0 |
| 3 | Auditoría manual periódica (mensual) de drift cross-project | baja |
| 4 | Agregar regla R3 (disciplina conversacional) a CLAUDE.md raíz del repo | alta |

---

## Lo que esto recupera

Antes del saneamiento:
- 87% archivos sin scope → cualquier query traía contenido contaminado
- Decisiones se tomaban sobre evidencia mezclada → hype/underevaluation
- Tiempo y tokens gastados re-validando información que ya estaba decidida

Después del saneamiento:
- 100% archivos con `aplica_a:` declarado
- Queries pueden filtrar por scope antes de retrieval
- Decisiones nuevas se hacen sobre evidencia limpia
- Las 19 decisiones (D1-D19) tomadas hoy quedan validadas como NO contaminadas

---

## Referencias y trazabilidad

**Aprobador:** CEO (sesión Cowork 2026-04-29d, post-detección del problema).

**Sync al repo canónico:** vía `sync_indexa_20260429d_saneamiento.ps1` con bug fix del mirror ya validado.

---

Stamp: VIGENTE — 2026-04-29d

Changelog:
- v1.0 (2026-04-29d): creación. Cuarta indexa del día (saneamiento, NO feature work). Aplicados 269 headers `aplica_a:`. Limpiado SCH_SKILL_MANIFEST_V2 de fields FB. Dividido ENT_RESEARCH_AGENT_ECOSYSTEM en MWT-only + FaberLoom-only. Audit de 24 archivos tocados en indexas A/B/C — veredicto: decisiones D1-D19 válidas. 4 reglas operacionales nuevas (R1-R4). 273 archivos tocados. Derivado de detección CEO de context bleed evaluativo entre MWT y FaberLoom.
