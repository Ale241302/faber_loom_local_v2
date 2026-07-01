# MANIFIESTO_APPEND_20260427_KIMI_RUFLO
id: MANIFIESTO_APPEND_20260427_KIMI_RUFLO
type: TRANSITORIO
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
stamp: VIGENTE — 2026-04-27
expires: post-consolidación en MANIFIESTO_CAMBIOS_v2.md (próxima sesión de mantenimiento)
aplica_a: [MWT]

---

## Contexto

CEO solicitó revisión Cowork de Kimi #3 (Ruflo / 4 gaps arquitectónicos) — investigación Kimi K2.5 Swarm de 12 dimensiones paralelas con cross-verification interna, ejecutada 2026-04-26 (~437KB, 27 archivos en zip).

Cowork validó calidad: 85% claims HIGH confidence, 1 conflict zone resuelta (CZ-001), 9 insights transversales accionables, anti-alucinación funcional. CEO autorizó indexación.

Esta sesión ejecuta la indexación a la KB con 4 ediciones correctivas sobre el output original.

## Cambios ejecutados

### 1. Entity principal nueva

`docs/ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO.md` (v1.0, ~250 líneas) — síntesis del Kimi #3:
- 9 insights I-RUFLO-01..09 con confidence levels
- Matriz de decisión 4 GAPs (2 IMPLEMENTAR + 2 DIFERIR)
- Conflict zone CZ-001 resuelta explícitamente
- Patrón "Deterministic First → LLM Fallback → Human Gate"
- Plan B Anthropic deprecando Haiku 3.5
- Próximos pasos semana 1-2 (~6-8 días dev)
- Limitaciones conocidas del Kimi (sección dedicada)

### 2. ARCH_AGENT_PRINCIPLES — nuevo Principio 14

v1.1 → **v1.3** (la entrada v1.2 estaba truncada en el original — recuperada en este append)

Agregado: **P14 — Deterministic First → LLM Fallback → Human Gate**.
- 3 niveles en orden estricto (regex → LLM → humano)
- Tabla de aplicación obligatoria por capa (parsing, routing, composición, vector retrieval)
- Anti-patrón explícito: usar LLM cuando regex resuelve
- Relación con P3, P4, P9, P13

### 3. SPEC_FABERLOOM_MVP — argumentación actualizada + Tier 0

v1.0 → **v1.1**

Cambios:
- Argumento contra multi-agente actualizado: 3 pilares verificables (MAST 41-86.7%, single-agent vs multi-agent NeurIPS 2025, confiabilidad compuesta exponencial)
- Riesgo "Hallucination cascades" actualizado: "87% en 4h" → "MAST 41-86.7%, NeurIPS 2025, 1,642 trazas"
- Riesgo "Technical debt" actualizado: Gartner 2027 prediction como contexto, no evidencia técnica
- +Sección "Tier 0 obligatorio" con tabla de capas, 14 reglas concretas para sprint 1, mantenimiento ~1 día/trimestre, spot-check pendiente con 20 docs Marluvas/Tecmater
- +P14 en énfasis de principios

### 4. SPEC_AUTONOMY_CONTROL_ENGINE — extensión OutcomeLedger

v1.1 → **v1.2**

Cambios:
- +Sección "Extensión v1.1 — OutcomeLedger como fuente para routing aprendido"
- Schema `RequestOutcomeEntry` per-request (no per-gold-sample) con 11 columnas
- RLS por `org_id` siempre, `task_type` global (NO per-org como feature)
- Reglas de captura desde MVP día 1
- Trigger activación bandit: >3,000 req/día × 14 días consecutivos

### 5. SPEC_LLM_ROUTING_ARCHITECTURE — Tier 0 + ModelFingerprint reframing

v1.0 → **v1.1**

Cambios:
- +Sección "Tier 0 — Deterministic First (P14)" con diagrama del pipeline actualizado
- +Sección "ModelFingerprint como feature de routing" — endpoint `GET /model/similarity`, reglas de transferencia por cosine similarity (≥0.8 transfer descuento 0.5 / 0.2-0.8 prior débil / <0.2 cold start)
- +Sección "Granularidad de aprendizaje: global por task_type, NO per-org" — features autorizadas vs prohibidas
- v2.1 en etapas actualizada: bandit adaptive con trigger volumen

### 6. Anexo de research raw (16 archivos)

Nuevo: `docs/anexos/kimi_ruflo/`
- `faberloom_dim01.md` ... `faberloom_dim12.md` — research raw por dimensión
- `faberloom_cross_verification.md` — anti-alucinación, CZ-001
- `faberloom_insight.md` — 9 insights consolidados pre-síntesis
- `_outline.md` — outline original
- `_full_report.md` — documento final 673 líneas (referencia)
- `README.md` — mapa de archivos + limitaciones conocidas

**No indexable a pgvector** — material de auditoría manual.

## Counts post-indexación

| Métrica | Antes (post AUDIT 2026-04-27) | Después | Delta |
|---|---|---|---|
| Total .md | 404 | 424 | +20 |
| docs/ activos | 285 | 288 | +3 (ENT_RUFLO + MANIFIESTO_APPEND_KIMI + ¿ya existía 1 más?) |
| docs/anexos/ | 0 | 17 | +17 (nueva carpeta: 16 research + README) |
| docs/archivo/ | 105 | 105 | 0 |
| audit/reportes | 11 | 11 | 0 |
| raíz | 3 | 3 | 0 |

Nota: el +3 en `docs/ activos` (no +2 como esperado) sugiere que el AUDIT 2026-04-27 dejó docs/ en 286 (no 285) pre-indexa. Verificar en próximo SSOT sync de RW_ROOT.md.

Nota: `docs/anexos/kimi_ruflo/` es estructura nueva. CLAUDE.md y RW_ROOT.md deben actualizarse para reflejar la categoría "anexos" como ubicación canónica de research raw no-indexable.

## Archivos modificados (resumen)

| Archivo | v.antes | v.después | Tipo de cambio |
|---|---|---|---|
| `ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO.md` | (nuevo) | v1.0 | Creación |
| `ARCH_AGENT_PRINCIPLES.md` | v1.1 (changelog truncado) | v1.3 | +P14, changelog reparado |
| `SPEC_FABERLOOM_MVP.md` | v1.0 | v1.1 | Argumentación verificable + Tier 0 |
| `SPEC_AUTONOMY_CONTROL_ENGINE.md` | v1.1 | v1.2 | +RequestOutcomeEntry schema |
| `SPEC_LLM_ROUTING_ARCHITECTURE.md` | v1.0 | v1.1 | +Tier 0 + ModelFingerprint dual-purpose |
| `docs/anexos/kimi_ruflo/*` | (nuevos) | — | 16 archivos research raw + README |
| `MANIFIESTO_APPEND_20260427_KIMI_RUFLO.md` | (nuevo) | v1.0 | Este archivo |

## NO ejecutado (pendiente CEO o próxima sesión)

| Pendiente | Razón de diferir |
|---|---|
| Update CLAUDE.md count 404→421 + entrada anexos | Requiere edición SSOT — esperar consolidación de esta sesión |
| Update RW_ROOT counts + nueva sección "Anexos" | Idem |
| Update IDX_GOBERNANZA con ref a ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO | Idem |
| Spot-check 20 docs Marluvas/Tecmater para validar 60-80% Tier 0 | Bloqueador potencial sprint 1 — coordinar con CEO |
| Validar pgvector ≥0.8.0 en Supabase actual | Operativo — verificar antes de configuración defensiva |
| Decisión CEO sobre SCH_RESEARCH_BRIEF.yaml + SKILL_RESEARCH_VALIDATOR.md | Mejoras al patrón cascada propuestas en revisión Cowork |

## Decisión CEO recomendada

1. **Verificar** que los 5 archivos modificados pasan revisión final (lectura rápida — Cowork ya validó contenido).
2. **Git sync** sugerencia commit:
   ```
   [GOBERNANZA] Indexa Kimi #3 Ruflo — ENT + P14 + 3 SPECs + anexo

   - Nuevo ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO v1.0 (9 insights, matriz 4 GAPs)
   - ARCH_AGENT_PRINCIPLES v1.3 (+P14 Deterministic First)
   - SPEC_FABERLOOM_MVP v1.1 (CZ-001 resuelta, +Tier 0 obligatorio)
   - SPEC_AUTONOMY_CONTROL_ENGINE v1.2 (+RequestOutcomeEntry schema)
   - SPEC_LLM_ROUTING_ARCHITECTURE v1.1 (+Tier 0, ModelFingerprint dual-purpose)
   - docs/anexos/kimi_ruflo/ con 16 archivos research raw + README

   Origen: Kimi K2.5 Swarm 12 dim, ejec 2026-04-26, validado Cowork 2026-04-27
   ```
3. **Decidir** sobre próxima cascada Kimi (#4) y si adoptar SCH_RESEARCH_BRIEF antes.

---

Trigger: CEO `indexa` (sesión 2026-04-27, Cowork mode) tras revisión Kimi #3 Ruflo.
