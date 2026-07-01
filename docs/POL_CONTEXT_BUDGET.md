# POL_CONTEXT_BUDGET — Presupuesto de Context Window
id: POL_CONTEXT_BUDGET
version: 1.0
status: VIGENTE
stamp: VIGENTE — 2026-04-09
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
aplica_a: [SHARED]

---

## Objetivo

Prevenir que la KB supere la capacidad del context window del Arquitecto (Claude Sonnet/Opus 4.6, ventana 200K tokens), garantizando que las sesiones de trabajo siempre tengan capacidad para operar.

## Estado actual KB

- KB total: ~265 archivos productivos, ~312K tokens (~156% de la ventana de 200K)
- pgvector: MANDATORIO — la KB no puede cargarse completa. Retrieval selectivo obligatorio.
- La KB NUNCA se carga completa en una sesión.

## Presupuesto por sesión

| Categoría | Tokens | % ventana |
|-----------|--------|-----------|
| System prompt + instrucciones | ~100K | 50% |
| KB (budget máximo) | ~100K | 50% |
| **Total disponible** | **~200K** | **100%** |

- **kb_budget:** 100,000 tokens máximo por sesión
- **compact_threshold:** 80,000 tokens → trigger de compactación proactiva
- El Arquitecto detiene la carga si se acerca a compact_threshold

## Tiers de carga

| Tier | Archivos | Tokens (~) | Cuándo cargar |
|------|----------|-----------|---------------|
| Always | IDX_*, POL_*, ENT_GOB_*, SKILL_*, RW_ROOT, DASHBOARD_SNAPSHOT, ENT_PLAT_KNOWLEDGE, ENT_PLAT_SKILLS_CATALOG | ~60K | Cada sesión |
| On-Demand | ENT_ (resto), PLB_, SCH_, LOC_ | ~30K | Cuando el dominio se menciona |
| Archive | LOTE_ DONE, MANIFIESTO_ histórico, CHANGELOG_SESION_* | — | Nunca — solo pgvector |

**Prioridad dentro de cada tier:** VIGENTE > FROZEN > DRAFT > STUB

## Regla de micro-compactación

Ningún archivo KB debe superar **500 líneas (~6,500 tokens)**. Excepciones:
- Archivos FROZEN (R2 — no se pueden modificar)
- Sprint activo LOTE_ con status DRAFT (exception documentada en DASHBOARD_SNAPSHOT)

Si un archivo nuevo o modificado supera 500 líneas:
1. Evaluar split en archivos más pequeños
2. Si no aplica split, comprimir (changelogs, redundancia)
3. Documentar excepción si persiste

## Reglas de carga selectiva

- **LOTE_ DONE:** NUNCA cargar — solo si CEO pide explícitamente
- **Efímeros:** NUNCA cargar — ref → POL_EPHEMERAL_OUTPUT
- **Archivos pesados:** Leer sección específica con Read (offset + limit), no el archivo completo
- **Los 5 más pesados:** LOTE_SM_SPRINT26 (~15K), ENT_PLAT_NIGHTLY_AUDITOR (~12K), ENT_OPS_STATE_MACHINE (~7K FROZEN), PLB_ORCHESTRATOR (~6.6K FROZEN), DEPENDENCY_GRAPH (~5.6K). No cargar todos simultáneamente.

## Enforcement

- **Detección:** Sesión supera 80K tokens de KB cargada
- **Acción:** Compactación inmediata — descargar archivos no referenciados en los últimos 5 turnos
- **Severidad:** HIGH — ventana saturada = outputs truncados o errores de coherencia

---

Changelog:
- v1.0 (2026-04-09): Creada. Extrae reglas de context window de CLAUDE.md a política formal (H8 auditoría ECC).
