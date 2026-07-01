# DASHBOARD_SNAPSHOT — Estado de la KB
id: DASHBOARD_SNAPSHOT
version: 14.6
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
stamp: VIGENTE -- 2026-06-15 -- AUDIT-ROUTING-2026-06-14 core fix + retención archivo
generado: 2026-06-15
generado_por: Claude (Cowork) — AUDIT-ROUTING-2026-06-14 (fuente unica de conteos, POL_DETERMINISMO §1 v1.2)
aplica_a: [MWT, FaberLoom]

---

## Conteos

> **Fuente unica:** este archivo es el unico que hard-codea conteos vivos (POL_DETERMINISMO §1 Regla 3 ejecutable v1.2). Todo otro archivo (CLAUDE.md, RW_ROOT.md, DEPENDENCY_GRAPH.md, IDX_*.md) referencia aqui en lugar de duplicar cifras.

| Metrica | Valor (2026-05-03 pre-PR1/PR2) | Notas |
|---------|--------------------------------|-------|
| Markdown totales (repo, mirror OneDrive) | 687 | sin .git/ - recontado 2026-06-15 manual (recount_kb.ps1 no disponible en este entorno) |
| Markdown totales (docs/ tree) | 655 | docs/ + subdirs |
| docs/ raiz (.md) | 336 | recontado 2026-06-15 |
| docs/faberloom/ (.md, primer nivel) | 81 | recontado 2026-06-15 |
| docs/anexos/ (.md totales) | 48 | mockups + ciclope + kimi_ruflo + kimi_team_swarm + kimi_skills |
| docs/archivo/ (.md totales) | 121 | sprints DONE + ephemerals histo + faberloom-mockup + manifiestos contaminacion + ARCHIVE_INDEX + SPEC_FB_BUILD_SEQUENCE_v2.1 A1 |
| audit/ (.md) | 8 | |
| reportes/ (.md) | 3 | |
| raiz repo (.md) | 3 | CLAUDE + README + COWORK_INSTRUCTIONS |
| docs/anexos/mockups/ (.html + README) | 4 (3 HTML + 1 README) |
| docs/anexos/ciclope_fixtures/r3_cross_industry/ | 22 (20 YAML + 1 SUMMARY YAML + 1 doc MD) |
| docs/anexos/ciclope_fixtures/safety_footwear/ | 13 (10 YAML + 1 SUMMARY YAML + 2 docs MD) |
| docs/faberloom/gold_samples/ (.md) | 3 |
| docs/archivo/ raíz (.md) | 57 |
| docs/archivo/2026-04-faberloom-prep/ (.md) | 22 |
| docs/archivo/faberloom-mockup/ (.md) | 26 |
| docs/archivo/manifiestos/contaminacion-29abr/ (.md) | 5 (4 manifiestos del 29 + README) |
| audit/ (.md) | 8 |
| reportes/ (.md) | 3 |
| raíz repo (.md) | 3 (CLAUDE, COWORK_INSTRUCTIONS, README) |
| ENT_ (docs/ raiz) | 105 |
| PLB_ (docs/ raiz) | 40 |
| POL_ (docs/ raiz) | 34 |
| SCH_ (docs/ raiz) | 20 |
| IDX_ (docs/ raiz) | 13 |
| LOC_ (docs/ raiz) | 32 |
| LOTE_ | 0 (29 en /archivo/) |
| SKILL_ (docs/ raiz) | 13 |
| SPEC_ (docs/ raiz) | 17 |
| ARCH_ (docs/ raiz) | 2 |
| FB scope en docs/faberloom/ | 23 (8 SPEC + 7 ENT/POL + 7 SCH/POL/CLI + Voice Humanizer batch g) -- +ENT_FB_INSIGHTS_KIMI_RUFLO_v1 + ENT_FB_PRICING_TIERS_v1 + SPEC_FB_ROUTING_PRESETS_v1 |

## Status

| Status | Cantidad |
|--------|----------|
| DRAFT | 115 |
| VIGENTE | 65 |
| STUB | 27 |
| DONE | 0 activos (29 LOTE_ DONE en /archivo/) |
| ACTIVO | 16 |
| SHADOW | 12 (11 SKILL_ Sprint Architecture 2026-04-16 + 1 SKILL_KB_GATEWAY A1.3 2026-05-07) |
| DEPRECATED | 1 (SCH_SKILL → reemplazado por nueva taxonomía skill architecture) |
| ARCHIVADO | 1 (SPEC_FB_BUILD_SEQUENCE_v2.1 A1 SUPERSEDED) |
| FROZEN | 2 (ENT_OPS_STATE_MACHINE + PLB_ORCHESTRATOR) |

## Tipos

| Tipo | Prefijo | Count |
|------|---------|-------|
| Entity | ENT_ | 99 |
| Playbook | PLB_ | 39 |
| Localization | LOC_ | 32 |
| Policy | POL_ | 34 |
| Lote/Sprint | LOTE_ | 0 activos (29 en /archivo/) |
| Schema | SCH_ | 18 |
| Index | IDX_ | 13 |
| Skill | SKILL_ | 12 (+SKILL_KB_GATEWAY A1.3) |
| Spec | SPEC_ | 14 |
| Arch | ARCH_ | 1 |

## Versiones principales

| Archivo | Version |
|---------|---------|
| RW_ROOT | v4.8.25 |
| DASHBOARD_SNAPSHOT | **v14.5** (este archivo) |
| SPEC_FB_VOICE_HUMANIZER | v2.0 (extiende v1, batch g 2026-05-07) |
| DEPENDENCY_GRAPH | v4.0 |
| MANIFIESTO_CAMBIOS_v2 | v1.0 (append-only) |
| SPEC_MWT_AGENT_PLATFORM | v1.2 |
| SPEC_ACTION_ENGINE | v1.3 (+D9 +D10 +D11) |
| SPEC_AUDIT_MODULE | v1.0 |
| SPEC_AUTONOMY_CONTROL_ENGINE | v1.2 |
| SPEC_LLM_ROUTING_ARCHITECTURE | v1.2 |
| SPEC_QUERY_PROCESSING_PIPELINE | v1.0 |
| ARCH_AGENT_PRINCIPLES | v1.5 (CORE BLINDADO 29-abr) |
| POL_DATA_CLASSIFICATION | v1.4 |
| IDX_PLATAFORMA | v1.0 (+6 SPECs/ENT_PLAT routed 29-abr indexa punto partida) |
| ENT_GOB_DECISIONES | v2.2 (+DEC-009 Prompt Cache Discipline) |
| SPEC_PROMPT_CACHE_DISCIPLINE | v1.0 (DRAFT) |
| POL_OUTAGE_CANONICAL_MIRROR | v1.0 (A1.1) |
| SPEC_FB_DOCUMENT_STATE_MACHINE | v1.0 (A1.2) |
| SKILL_KB_GATEWAY | v1.0 SHADOW (A1.3) |

## Health

| Check | Estado |
|-------|--------|
| Huerfanos (ENT/PLB/LOC no indexados) | 0 ✅ (3 resueltos en INDEXA 2026-04-17) |
| Patches pendientes | 0 |
| Refs rotas a archivos eliminados (literal .md) | 0 ✅ — alcance IDX+DEPENDENCY+SCHEMA_REGISTRY |
| DEPRECATED activos | 1 (SCH_SKILL — tracking KB_AUDIT) |
| Efimeros (APPEND/PATCH/CHECKPOINT) | **42 🔴** — violacion activa POL_EPHEMERAL (umbral >3) — purga via PR-1+PR-2 (delete destructivo, requiere reindex pgvector shadow) |
| MANIFIESTO_APPENDs pendientes | **42 🔴** — 8 ya consolidados en B1c-part1 (pendiente delete) + 34 a consolidar |
| Tipos en taxonomia | 8 ✅ |
| SKILL_ files creados | 12/12 (todos SHADOW, +SKILL_KB_GATEWAY A1.3) |
| GitHub sync | OK — commit e144f07 (B0 DONE_PUSHED 2026-04-18) |
| POL_CONTEXT_BUDGET | VIGENTE ✅ |
| POL_EPHEMERAL_OUTPUT | VIGENTE ✅ (violación pendiente B1c) |
| LINE_ENDINGS CRLF | 0 ✅ (B0 normalizado 2026-04-18 · 300 → 0) |
| UTF-8 decode / BOM / NFC | 0 / 0 / 0 ✅ (B0 verificado) |
| UNKNOWN domain | 0 ✅ (B0 reclasificado) |
| Schema assemblability | reportado — ver audit/schema_assemblability_report.md |
| CEO_ONLY leaks | **13 detectados** (14 - 1 cerrado por PR-0 ENT_PROD_SCANNER 2026-05-03) — follow-up CEO-32 (vence 2026-05-30) |
| FROZEN integrity | ENT_OPS_STATE_MACHINE + PLB_ORCHESTRATOR intactos ✅ (md5 estable, v1.2.2 FINAL stamp 2026-03-01) |
| Headers IDX | 10/10 ahora con stamp ✅ (2026-04-27 normalización post-v4.8.7) |
| SPEC sin visibility | 0 ✅ (SPEC_AGENT_ARCHITECTURE_ALE corregido 2026-04-27) |
| Higiene raíz | 3/3 ✅ (CLAUDE+README+COWORK_INSTRUCTIONS — 22 ephemerals movidos a docs/archivo/2026-04-faberloom-prep/) |

## Sprints

| Sprint | Status |
|--------|--------|
| Sprint 0-27 | DONE ✅ — S1-S27 cerrados 2026-04-10 |
| Sprint 25 | DONE — 2026-04-08 (AG-02, 59 tests) |
| Sprint 26 | DONE — 2026-04-10 (AG-02, 63 tests, notifications app + cobranza + admin templates) |
| Sprint 27 | DONE — 2026-04-10 (AG-02, DoD 13/13, hardening + backups + audit seguridad) |

## Deuda conocida

| Issue | Severidad | Tracking |
|-------|-----------|----------|
| LOTE_SM_SPRINT26 (1,243L > límite 500) | Baja | Candidato a compresión post-DONE |
| LOTEs DONE S20B/S22/S23/S25 inflados (>500L) | Media | Comprimir en sesión de mantenimiento |
| ENT_PLAT_NIGHTLY_AUDITOR (940L) | Media | Split: config + procedures |
| 18+ status no canónicos | Media | Pendiente normalización |
| ENT_PLAT_SEGURIDAD en KB aún es DRAFT v1.0 | Media | v2.1 verificada en servidor S27. Actualizar archivo KB y promover a VIGENTE. |
| ENT_PLAT_SSOT es STUB (incompleto) | Media | Registry maestro SSOTs pendiente |
| H10: 6 consolidaciones pendientes (ENT_COMP_CLAIMS→CONTENT_RULES, etc.) | Media | Próxima sesión mantenimiento |
| H14: ENT_OPS_INVENTARIO — único registro de inventario activo | Baja | ENT_PLAT_INVENTARIO_OPS eliminado (STUB vacío, KB Hygiene v4.7.0) |

## Auditoría más reciente

| Auditor | Fecha | Score | Umbral |
|---------|-------|-------|--------|
| Claude ECC (auditoría externa) | 2026-04-09 | 7.8/10 pre-remediación | 9.5 |
| Post-remediación (estimado) | 2026-04-09 | ~9.0/10 | — |
| KB_AUDIT_20260418 (Cowork) | 2026-04-18 | B0 DONE_PUSHED · B1a/B1b/B1c-PART1 DONE · B2-B11 PENDING | — |
| AUDIT_INTEGRAL_20260422 (Cowork) | 2026-04-22 | AMARILLO — 3 focos rojos (CEO pendings, 5 SPECs FaberLoom, 27 raíz) | — |
| AUDIT_4ALCANCE_20260427 (Cowork) | 2026-04-27 | Drift detectado (322→404), 22 ephemerals → archivo, 14 CEO leaks (no 10), 4 SPECs huérfanos indexados | — |

---

Changelog:
- v10.0 (2026-04-27): Sync post-AUDIT 4-alcance (RW_ROOT v4.8.7). Conteos reales: 404 .md (285 docs/activo + 105 archivo/ [57+22+26] + 11 audit+reportes + 3 raíz). +22 ephemerals raíz → docs/archivo/2026-04-faberloom-prep/. faberloom-mockup/ → docs/archivo/. Corrige DASHBOARD_MISMATCH P0 (322→404, +82 archivos sin sync). +1 SPEC indexado (6→11). Headers IDX +stamp (10/10 ✅). CEO_ONLY leaks 10→14. FROZEN íntegros. Health: AMARILLO mantenido (B2-B11 KB_AUDIT estancado + CEO-25/26/27/32 vencen 2026-05-30).
- v9.0 (2026-04-18): INDEXA B1a — sync SSOT/IDX post-B0. Conteos reales: 322 .md (254 docs/activo + 55 archivo/
  + 8 audit/ + 2 reportes/ + 3 raíz). Corrige DASHBOARD_MISMATCH P0 (254+65=319 declarado → 322 real). /archivo/ 65→55.
  Taxonomía 8 tipos confirmada. Flagged: 9 efímeros pendientes B1c, 1 DEPRECATED (SCH_SKILL), 10 CEO_ONLY leaks (CEO-32),
  CRLF normalizado 300→0 post-B0. IDX_GOBERNANZA: +POL_CONSENTIMIENTO +POL_RETENCION_ESCANEOS (26→28 POLs).
- v8.9 (2026-04-17): INDEXA — 3 huérfanos resueltos (ENT_COMP_CONTENT_RULES, ENT_MARCA_MW_IDENTIDAD,
  ENT_PLAT_AGENT_ORCHESTRATION). IDX_COMPLIANCE, IDX_MARCA, IDX_PLATAFORMA actualizados. Huérfanos: 0 ✅
- v8.8 (2026-04-17): INDEXA — conteos reales post git-merge. Activos 254 (LOTE_ 29→/archivo/).
  SPEC_MWT_AGENT_PLATFORM→v1.2 (3 componentes: Hub+mwt.one+FaberLoom). IDX_PLATAFORMA actualizado.
  ENT_ 93→95, PLB_ 37→38, SCH_ 15→18, SKILL_ 6→11. Huérfanos 0.
- v8.7 (2026-04-17): +ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL v1.0 (10 insights Email + Conectividad MCP).
  SPEC_MWT_AGENT_PLATFORM→v1.1 (conflicto n8n resuelto). Total 278→279. ENT_ 92→93. MD 252→253.
- v8.6 (2026-04-17): +SPEC_MWT_AGENT_PLATFORM v1.0 — MWT como plataforma de agentes,
  stack completo, 3 objetos, pgvector, WhatsApp, OutcomeLedger flat-file, roadmap autonomía.
  Total 277→278. IDX_PLATAFORMA actualizado.
- v8.5 (2026-04-17): Integración investigación Kimi Swarm. SPEC_AUTONOMY_CONTROL_ENGINE→v1.1
  (+OutcomeLedger +UserControlProfile +Oscillation Counter +HumanAlignmentScore).
  +SPEC_FABERLOOM_MVP v1.0 (plan 60 días, stack, fases, métricas). +ENT_FABERLOOM_INSIGHTS_KIMI
  v1.0 (11 insights estratégicos). Total 274→277. IDX_GOBERNANZA actualizado.
- v8.4 (2026-04-17): +SPEC_AUTONOMY_CONTROL_ENGINE v1.0 (ImpactVector, Task Authorization, Async Queue) +ARCH_AGENT_PRINCIPLES v1.2 (+P13 Contención + ModelFingerprint). Total 272→274.
- v8.3 (2026-04-17): +SPEC_LLM_ROUTING_ARCHITECTURE v1.0 — L1 Clasificador + L2 Dispatcher (Arena-aware, 3 modos) + L3 Prompt Compiler + Token Ledger. Total 271→272.
- v8.2 (2026-04-17): +SPEC_QUERY_PROCESSING_PIPELINE v1.0 — pipeline 8 fases consulta→memoria, observable en Cowork, mapeado a FaberLoom. Total 270→271. IDX_GOBERNANZA actualizado.
- v8.1 (2026-04-17): +ARCH_AGENT_PRINCIPLES v1.1 (12 principios, +P11 clasificador 3 destinos, +P12 propagación cross-skill) +SPEC_AGENT_ARCHITECTURE_ALE. Total 268→270. IDX_GOBERNANZA actualizado.
- v8.0 (2026-04-16): INDEXA gate — Skill Architecture Sprint. +4 archivos (SCH_SKI
- v14.6 (2026-06-15): AUDIT-ROUTING-2026-06-14 core fix. Conteos reajustados post-fix: totales 687, docs tree 655, docs/raiz 336, docs/faberloom 81, docs/archivo 121. ENT_ docs/raiz 105, POL_ 34, IDX_ 13. DRAFT 115, VIGENTE 65, ARCHIVADO 1. Se archiva SPEC_FB_BUILD_SEQUENCE_v2.1 A1 SUPERSEDED y se crea ARCHIVE_INDEX.md.
