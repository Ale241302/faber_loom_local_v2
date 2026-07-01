# RW_ROOT — Root Index
## Rana Walk / MWT — Arquitectura de Conocimiento v4.8.26
### Ultima actualizacion: 2026-06-15 (AUDIT-ROUTING-2026-06-14 · fix refs rotas core + huérfanos + IDX faltantes · 12 dominios + FaberLoom sub-router · DASHBOARD v13.4->v13.5)
### Anterior: 2026-05-07c (A1.2 INDEXA SPEC_FB_DOCUMENT_STATE_MACHINE v1.0 · maquina de estados documentos KB FaberLoom · 10 estados · 18 transiciones DAG · versioning monotonic semver · audit chain D10 · RBAC per transicion · DASHBOARD v13.2->v13.3)
### Anterior: 2026-05-07b (A1.1 INDEXA POL_OUTAGE_CANONICAL_MIRROR v1.0 · proteger pipeline ante outage canonico · 3 estados HEALTHY/DEGRADED/OUTAGE · 7 reglas · CEO autoridad unica para declarar OUTAGE · DASHBOARD v13.1->v13.2)
### Anterior: 2026-05-07 (INDEXA Prompt Cache Discipline · DEC-009 reemplaza placeholder · SPEC_PROMPT_CACHE_DISCIPLINE v1.0 DRAFT · SPEC_ACTION_ENGINE v1.2->v1.3 +D11 · DASHBOARD v13.0->v13.1 · ahorro proyectado $5.6K/ano)
### Anterior: 2026-05-03 (PR-0..5 auditoría de reindexación 2026-05-03 · cierre leak SCANNER + 5 SCH_FB en SCHEMA_REGISTRY + 4 POLs bumpeados con Reglas 1-5 ejecutables + DASHBOARD v13.0 fuente unica de conteos)
### Anterior: 2026-05-02 (Indexa-j · 4 piezas transversales R6+R7+R8 · learning + DMS + UnitOfWork + VerticalCandidates)
### Anterior: 2026-05-01b (Indexa AI_GOV Dual Review · PLB + SCH del veredicto · SPEC_AI_GOV v1.0→v1.1 +Componente 6 Dual Review · regla familias distintas inquebrantable)
### Anterior: 2026-05-01 (Indexa AI_GOV · subfamilia governance IA · 3 POLs + 1 SCH + 1 SPEC madre + 2 ENTs + extensión SPEC_LLM_ROUTING v1.3 con campos governance en Token Ledger)

---

## META-REGLAS DEL SISTEMA

- Todo documento es UTF-8 (POL_UTF8)
- Todo entity tiene: id, version, domain, status, visibility. stamp obligatorio para status VIGENTE/ACTIVO/FROZEN
- Todo schema tiene: id, version, requires[], policies[], inherits
- Cambio se propaga hacia abajo, nunca hacia arriba
- Nuevo dominio → editar este Root Index
- Nueva estructura de output → Schema en SCHEMA_REGISTRY
- Nuevo dato → Entity en Domain Index correspondiente
- Nueva regla operativa → Playbook en Domain Index correspondiente
- Nueva regla del sistema → Policy en /policies/

## TAXONOMÍA (8 tipos)

| Tipo | Prefijo | Función |
|------|---------|---------|
| Index | IDX_ | Router. Sabe dónde vive cada cosa |
| Schema | SCH_ | Plantilla de ensamblaje con slots |
| Entity | ENT_ | Data pura inyectable |
| Loc | LOC_ | Data localizada por idioma |
| Policy | POL_ | Constraint transversal del sistema |
| Playbook | PLB_ | Instrucciones operativas de dominio/agente |
| Lote | LOTE_SM_SPRINT* | Paquete de ejecución por sprint — solo plataforma |
| Skill | SKILL_ | System prompt de agente IA con memoria sobre KB |

## REGLAS DE SCHEMAS

- Schema existe = yo puedo ensamblarlo
- Schema no existe = primero se crea, itera y aprueba
- No se crean schemas especulativos. Solo cuando hay uso real.
- Todo schema declara: requires, policies, inherits
- Antes de ensamblar: verificar que todas las entities del requires están disponibles
- Si falta entity → escalar. Nunca inventar.
- Output ensamblado = DRAFT hasta que pase validación de policies
- Schema aprobado en producción = snapshot inmutable (va a archivo, no aquí)

### Ciclo de vida de un Schema

1. Necesidad detectada
2. DRAFT — se define slots, requires, policies, herencia
3. PROTOTIPO — se ensambla con una entity real para validar
4. ITERACIÓN — CEO revisa, ajusta slots, corrige requires
5. APROBADO — se agrega al registry como disponible
6. ACTIVO — disponible para ensamblaje con cualquier entity
7. DEPRECATED — si se reemplaza por otro schema

## DOMINIOS (12)

| Dominio | Index | Ubicación |
|---------|-------|-----------|
| Producto | IDX_PRODUCTO | /producto/ |
| Marca | IDX_MARCA | /marca/ |
| Comercial | IDX_COMERCIAL | /comercial/ |
| Operaciones | IDX_OPS | /operaciones/ |
| Mercados | IDX_MERCADOS | /mercados/ |
| Marketplace | IDX_MARKETPLACE | /marketplace/ |
| Compliance | IDX_COMPLIANCE | /compliance/ |
| Gobernanza | IDX_GOBERNANZA | /gobernanza/ |
| Plataforma | IDX_PLATAFORMA | /plataforma/ |
| Distribución | IDX_DISTRIBUCION | /distribucion/ |
| Arquitectura Fundacional | IDX_ARQUITECTURA_FUNDACIONAL | /arquitectura-fundacional/ |
| Sprints | IDX_SPRINTS | /sprints/ |

## SUB-ROUTERS (freeze / referenciados)

| Sub-router | Index | Ubicación | Nota |
|------------|-------|-----------|------|
| FaberLoom | IDX_FB_FOUNDATION_BETA | /faberloom/ | Build pausado; referenciado como sub-router, NO dominio activo |

## SCHEMAS

Catálogo de estructuras de output → SCHEMA_REGISTRY (/schemas/)

### Regla de indexación por tipo
- ENT_, PLB_, LOC_, SKILL_ → se indexan en IDX_{DOMINIO}
- POL_ → se indexan en IDX_GOBERNANZA (o IDX_COMPLIANCE si son compliance-specific)
- SCH_ → se indexan en SCHEMA_REGISTRY (su registro dedicado)
- LOTE_ → no se indexan en IDX (son paquetes de ejecución temporal)

## POLICIES

Constraints transversales → indexadas en IDX_GOBERNANZA (sección Policies). Conteo vivo de POLs → ver `DASHBOARD_SNAPSHOT.md §Tipos` (fuente unica per POL_DETERMINISMO §1 Regla 3 v1.2).

## REGISTROS ESPECIALES

Archivos que no pertenecen a la taxonomía de 8 tipos pero son parte operativa del proyecto:

| Archivo | Tipo | Función |
|---------|------|---------|
| ARTIFACT_REGISTRY.md | Registry | Catálogo versionado de artefactos del sistema (ART-01 a ART-20+) |
| MANIFIESTO_CAMBIOS_v2.md | Manifest | Log de cambios activo — append-only vía MANIFIESTO_APPEND_*. (MANIFIESTO_CAMBIOS.md histórico fue retirado en v4.8.7; trazabilidad pre-2026 vive como referencia textual en el changelog de v2) |
| DEPENDENCY_GRAPH.md | Registro | Grafo de dependencias de ensamblaje + cadenas operativas críticas |
| DASHBOARD_SNAPSHOT.md | Snapshot | Estado actual KB: conteos, health, sprints activos |
| SCHEMA_REGISTRY.md | Registry | Catálogo de todos los SCH_ (funciona como su IDX) |
| MWT_ARCHITECTURE_PACKAGE.md | Paquete | Refs consolidadas arquitectura (referenciado por PLB_ORCHESTRATOR FROZEN) |
| COM07_COM08_nomenclatura_marluvas_v1.md | Entity | Nomenclatura tokens Marluvas (B2B) |
| COM07_COM08_nomenclatura_marluvas_v1.json | Data | JSON motor de descripciones Marluvas |
| git_push.sh | Script | Push workspace → GitHub. Leer token desde .kb_token |
| PF_0000-2026_GOLDEN_EXAMPLE.html | Artefacto | Golden example proforma MWT (ART-02) |
| rw_sticker_v7_8.html | Artefacto | Catálogo HTML stickers + barcodes SVG 66 SKUs (ART-19, SSOT tallas) |
| rw_insole_color_spec_v7.html | Artefacto | Especificación colores plantillas (ART-20) |
| rw_sticker_v7_3.html | Artefacto | Versión anterior sticker (referencia histórica) |
| docs/ENT_FABERLOOM_AGENT_BUILDER_v1.md | ENT (DRAFT) | Especificación Agent Builder FaberLoom — 168 agentes, taxonomía, YAML schema, MVP |
| SPEC_QUERY_PROCESSING_PIPELINE.md | SPEC | Pipeline 8 fases consulta→memoria — Cowork observable + mapeado FaberLoom |
| SPEC_LLM_ROUTING_ARCHITECTURE.md | SPEC | L1 Clasificador + L2 Dispatcher + L3 Prompt Compiler + Token Ledger (v1.3 +campos governance AI_GOV: data_classification, provider_allowed_by_policy, audit_id, pinned_output_id, outcome_entry_id, role, parent_request_id) |
| SPEC_AUTONOMY_CONTROL_ENGINE.md | SPEC | ImpactVector · OutcomeLedger · UserControlProfile · Oscillation Counter · HumanAlignmentScore |
| SPEC_AI_GOV_GOVERNANCE_AND_ROUTING.md | SPEC | Capa AI_GOV sobre routing técnico — gobierna data_class×provider, skill installation, final pass premium, output pinning, dual review decisiones técnicas, eval lab mensual. Ata 3 POLs + 2 SCHs + 2 ENTs + 1 PLB (dual review). VIGENTE v1.1 |
| SPEC_FABERLOOM_MVP.md | SPEC | Plan validación 60 días — stack, 4 fases, métricas, riesgos, roadmap 12 meses |
| SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md | SPEC | Blueprint canónico arquitectura FaberLoom v1 (16 secciones) — citado por 14+ docs (AUDIT, MANIFIESTO, SPECs derivados). DRAFT v1.0 |
| SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md | SPEC | Composición de agentes FaberLoom (canon AgentSpec runtime/memory) — DRAFT v1.0 |
| SPEC_FABERLOOM_SKILL_COMPOSITION_v1.md | SPEC | Composición de skills FaberLoom (3-layer manual_overlay + learned_overlay + sealed_base) — DRAFT v1.0 |
| SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md | SPEC | Workflow engine FaberLoom (pg-boss + Letta + scratchpads MinIO + anti-loop) — DRAFT v1.0 |
| FABERLOOM_MOCKUP_CHANGES_F1_v3.6.md | Changelog | Cambios v3.5→v3.6 mockup F1 (post-AC_V3_5). Referencia histórica pre-promoción docs/AUDIT_FABERLOOM_AC_V3_5_v1.md |
| ENT_FABERLOOM_INSIGHTS_KIMI.md | ENT | 11 insights estratégicos de investigación Kimi Swarm (10 dimensiones, 200+ búsquedas) |
| ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL.md | ENT | 10 insights Kimi Swarm (Email + Conectividad MCP). Resuelve conflicto n8n. |
| AUDIT_FABERLOOM_A1..A7 · B0 · B1 · AC_V2/V3/V3_5 · TRAZABILIDAD_V2/V3 · AXE_REPORT · DELIVERY_TIMELINE (16 archivos) | AUDIT | Serie pre-build FaberLoom mockup v1→v3.5 — reconciliación SPECs + service blueprint + acceptance criteria (94 PASS cumulative) + trazabilidad + accessibility audit + release timeline. Dominio Gobernanza. Ver IDX_GOBERNANZA §"Auditorías FaberLoom pre-build". A7 v1.1 incluye C17 agent lifecycle + 21 OQ. |
| PLB_FABERLOOM_KB_PROMOTION_v1.md | PLB | Playbook handoff Claude Code → Cowork — roadmap promoción AUDIT_FABERLOOM → canon KB (D1-D10 nuevos, U1-U8 edits, O1-O3 referencias, 6 brechas KB, 21 OQ priorizadas P0-P3). Dominio Gobernanza. |
| faberloom_mapa_tiers.html | Artefacto | Mapa interactivo 168 agentes × 4 tiers de confianza, filtrable por área funcional |
| ROADMAP_EXTENDIDO_POST_DIRECTRIZ.md | Roadmap | Roadmap post-directriz estratégica CEO |

**Nota:** Los efímeros de sesión (CHANGELOG_SESION_*, MANIFIESTO_APPEND_*, GUIA_ALE_ de sprints cerrados, PROMPT_ANTIGRAVITY_* de sprints cerrados, RESUMEN_SPRINT* de sprints cerrados, apply_batch_*.sh) NO se listan aquí — se eliminan según POL_EPHEMERAL_OUTPUT.

Changelog:
- Historial completo: ver `MANIFIESTO_CAMBIOS_v2.md`.
- Entradas históricas de `RW_ROOT.md` no duplicadas individualmente en `MANIFIESTO_CAMBIOS_v2.md`: ver `docs/RW_ROOT_CHANGELOG.md`.

---

## CÓMO NAVEGAR (cualquier LLM)

1. Usa `docs/ROUTING_MANIFEST.json` para resolver `id` → `path`. El manifest es **tabular**: la primera fila es el header `[id, path, type, domain, status, visibility, version]`; las filas siguientes son los registros.
2. Códigos cortos de `domain` en el manifest: `PROD`=Producto, `MAR`=Marca, `COM`=Comercial, `OPS`=Operaciones, `MERC`=Mercados, `MKT`=Marketplace, `CMP`=Compliance, `GOB`=Gobernanza, `PLAT`=Plataforma, `DIST`=Distribución, `ARQF`=Arquitectura Fundacional, `FB`=FaberLoom.
3. O sigue la tabla de dominios de esta página → `IDX_<DOMINIO>` → archivo. Para FaberLoom (freeze) usa el sub-router `IDX_FB_FOUNDATION_BETA`.
4. Si una referencia no está en el manifest, escala; no inventes el destino.

---

Stamp: BOOTSTRAP VIGENTE 2026-06-15
Vencimiento: 2026-09-15
Estado: VIGENTE
Aprobador final: CEO
- v4.6.10 (2026-