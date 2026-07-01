# MANIFIESTO_APPEND — 2026-05-01 — Subfamilia AI_GOV (Governance de IA)

## Origen
Sesión arquitectónica AI_GOV 2026-05-01 (Cowork como arquitecto + ChatGPT como cross-validator). Punto de partida: iteración Kimi inventario 213 skills (skills.sh ecosystem) + intuición CEO sobre control de costos IA + pinning de outputs + sandbox de evals.

## Decisiones arquitectónicas tomadas

| # | Decisión | Resolución |
|---|----------|------------|
| D1 | Naming subsistema gobernanza | `AI_GOV` como subfamilia conceptual bajo Plataforma. Indexación por convención: POL → IDX_GOBERNANZA, ENT → IDX_PLATAFORMA, SCH → SCHEMA_REGISTRY, SPEC → registros especiales RW_ROOT. NO se abre dominio #11. |
| D2 | Token Ledger | YA existía canonizado en `SPEC_LLM_ROUTING_ARCHITECTURE` v1.2. Decisión: **extender a v1.3** con campos de governance, NO crear ENT separado. |
| D3 | OutcomeLedger | YA existía en `SPEC_AUTONOMY_CONTROL_ENGINE` v1.2 (`RequestOutcomeEntry`). Decisión: **referenciar via `outcome_entry_id`** en Token Ledger, NO duplicar. |
| D4 | Relación SPEC_LLM_ROUTING vs SPEC_AI_GOV | Paralelo, no fusionar. AI_GOV gobierna; LLM_ROUTING ejecuta. Ante conflicto, gana governance. |
| D5 | Scope | Cross-brand `[MWT, FaberLoom]`. Rechazada propuesta `_FB_` por miopía (duplicaría todo en 6 meses). |
| D6 | Tier compuesto | Regla canonizada: `output_tier = max(input_tiers de toda la cadena)`. Carpintero no puede bajar tier. |
| D7 | Asimetría orquestador | Kimi/Moonshot puede orquestar chains que tocan N3 si y solo si solo recibe metadata (N0/N1) y los carpinteros son DPA-FULL/SELF-HOST. Asimetría registrada en ledger. |

## Archivos creados (6 nuevos)

| Archivo | Tipo | Status | Indexa en |
|---------|------|--------|-----------|
| `POL_AI_GOV_DATA_CLASS_PROVIDER.md` | POL | VIGENTE v1.0 | IDX_GOBERNANZA |
| `POL_AI_GOV_SKILL_INSTALLATION.md` | POL | VIGENTE v1.0 | IDX_GOBERNANZA |
| `POL_AI_GOV_FINAL_OUTPUT_QUALITY.md` | POL | VIGENTE v1.0 | IDX_GOBERNANZA |
| `SCH_AI_GOV_HANDOFF_DRAFT.md` | SCH | VIGENTE v1.0 | IDX_GOBERNANZA + SCHEMA_REGISTRY |
| `SPEC_AI_GOV_GOVERNANCE_AND_ROUTING.md` | SPEC | VIGENTE v1.0 | IDX_GOBERNANZA Arq Fundacional + IDX_PLATAFORMA Arq Plataforma + RW_ROOT registros especiales |
| `ENT_AI_GOV_GOLDEN_CORPUS_MWT.md` | ENT | DRAFT v1.0 (esqueleto, corpus pendiente curación CEO) | IDX_PLATAFORMA |
| `ENT_AI_GOV_OUTPUT_PINS.md` | ENT | DRAFT v1.0 (registry vacío, poblamiento via ledger) | IDX_PLATAFORMA |

## Archivos extendidos (1)

| Archivo | Cambio | Versión |
|---------|--------|---------|
| `SPEC_LLM_ROUTING_ARCHITECTURE.md` | +campos governance en schema Token Ledger (data_classification, data_class_max_in_chain, provider_policy_version, provider_allowed_by_policy, audit_id, outcome_entry_id, pinned_output_id, pin_status, final_pass_required/executed/shortcut_reason, budget_caps_applied/status, role, parent_request_id, context_hash, output_hash, tokens_cached, brand_scope) +5 reglas de integridad +header `gobernado_por: SPEC_AI_GOV_GOVERNANCE_AND_ROUTING.md` | v1.2 → v1.3 |

## IDX actualizados (4)

| IDX | Cambios |
|-----|---------|
| `IDX_GOBERNANZA.md` | +3 POLs en Policies · +1 SCH en Schemas de Gobernanza · +1 SPEC en Arquitectura Fundacional · update header health (28→31 POLs, 2→3 SCHs, 7→8 arq fundacional) |
| `IDX_PLATAFORMA.md` | +2 ENTs (golden_corpus, output_pins) · +1 SPEC en Arquitectura de Plataforma · update SPEC_LLM_ROUTING v1.2→v1.3 · update header health (23→25 archivos contenido) |
| `SCHEMA_REGISTRY.md` | +sección AI GOVERNANCE con SCH_AI_GOV_HANDOFF_DRAFT · total 19→20 schemas |
| `RW_ROOT.md` | +SPEC_AI_GOV en registros especiales · update SPEC_LLM_ROUTING descriptor v1.3 · header v4.8.18 → v4.8.19 |

## Reglas inquebrantables canonizadas (8)

1. Ninguna llamada LLM sin entry en Token Ledger.
2. Ningún output cliente-visible sin `final_pass_required: true`.
3. AI_GOV gobierna; LLM_ROUTING ejecuta. Ante conflicto, gana governance.
4. Tier compuesto: output_tier = max(input_tiers).
5. Pin no es dogma: torneo mensual obligatorio.
6. Cap de tokens por skill SIEMPRE existe. Free tier sin cap prohibido.
7. Override de policy requiere audit_event con expiración (cost-mode opt-in máx 90 días renovables).
8. Skill externa sin contrato + scan + sandbox + owner = bloqueada.

## Lecciones aprendidas (indexadas)

1. **No asumir que algo existe o no existe sin grep.** Tanto Cowork (Claude) como ChatGPT recomendaron crear `ENT_PLAT_TOKEN_LEDGER` desde cero cuando ya estaba canonizado en `SPEC_LLM_ROUTING_ARCHITECTURE` v1.2 (sección propia con schema, queries, feedback loop). La regla #1 del CLAUDE.md (no inventar) aplica también a "no asumir ausencia". Lección: **antes de proponer crear un archivo, grep el repo**.

2. **Scope cross-brand desde día 1.** ChatGPT propuso prefijo `_FB_` (FaberLoom-only). Si se aceptaba, en 6 meses se duplicaba todo para MWT. Decisión cross-brand `[MWT, FaberLoom]` desde el inicio ahorra reescritura.

3. **Token Ledger ya conectado a OutcomeLedger sin duplicar.** Schema v1.3 referencia `outcome_entry_id` (RequestOutcomeEntry de SPEC_AUTONOMY_CONTROL_ENGINE) en vez de duplicar telemetría de outcome. Hermanos, no gemelos.

4. **Asimetría de orquestador es la palanca de costo crítica.** Kimi/Moonshot puede ser orquestador legal incluso para chains N3, si solo ve metadata. Sin esa asimetría documentada, alguien va a pasar raw N3 al orquestador "porque es más fácil" y romper privacy. Canonizado en POL_AI_GOV_DATA_CLASS_PROVIDER §E.

5. **Pinning + torneo mensual es la palanca de calidad+costo combinada.** "El rey conserva la corona, pero todos los meses hay torneo." Sin esta disciplina, los pins se vuelven dogma y perdemos ahorros que los modelos baratos van ganando con el tiempo.

## Pendientes inmediatos (no bloqueantes para canonización)

| # | Pendiente | Owner | Trigger |
|---|-----------|-------|---------|
| P1 | Poblar `ENT_AI_GOV_GOLDEN_CORPUS_MWT` con 50-100 cases curados | CEO + curador | Sprint dedicado de curación |
| P2 | Implementar enforcement de `provider_allowed_by_policy` en Action Engine | AG-01 / AG-02 | Sem 3+ roadmap Action Engine |
| P3 | Hookpoint en final pass dispatcher para `final_pass_required` | AG-02 | Sem 5-7 |
| P4 | Primer ciclo Eval Lab mensual con corpus mínimo 50 cases | CEO | Post P1 |
| P5 | Migración de skills externas existentes (obra/superpowers, anthropic-skills) a contratos formales según POL_AI_GOV_SKILL_INSTALLATION | CEO | Lazy: cuando se toque cada skill |
| P6 | Auditoría de pins propuestos automáticamente desde histórico de Token Ledger (outputs aprobados clean en últimos 30 días) | CEO | Post enforcement F1 |

## Diferido (intencional)

- Benchmark real Kimi K2 vs Qwen3 vs Sonnet vs Opus: bloqueado por golden corpus. Hasta P1 está poblado, todo benchmark es teatro.
- Instalación masiva de skills externas: bloqueado por POL_AI_GOV_SKILL_INSTALLATION lifecycle. Primero canonizar gobernanza, después instalar bajo régimen.
- Bandit adaptive routing: ya en roadmap SPEC_LLM_ROUTING etapa v2.1 (trigger >3,000 req/día × 14 días). No se acelera.
- Auto-update de skills: prohibido por regla #1 de POL_AI_GOV_SKILL_INSTALLATION.

## Por qué este lote y no más

Este lote cierra el **frame de governance de IA**. Todo lo que sigue (P1-P6) es ejecución, no arquitectura. Si abrimos más decisiones arquitectónicas en este sprint, atrasamos enforcement.

## Cross-validación con ChatGPT

ChatGPT validó las 4 decisiones arquitectónicas iniciales (naming AI_GOV, paralelo a v1.2, ledger primero, scope cross-brand) con 5 caveats de los cuales 4 quedaron incorporados:
- Naming `_PLAT_` para infra que produce datos vs `_AI_GOV_` para políticas que consumen → respetado (ENT_PLAT_TOKEN_LEDGER existe en SPEC; ENTs nuevos usan AI_GOV en IDX_PLATAFORMA por convención).
- TokenLedger no duplica OutcomeLedger → respetado (referenciado via outcome_entry_id).
- Campos governance al ledger (data_classification, audit_id, etc) → respetado (extensión v1.3).
- Precedencia AI_GOV gobierna, LLM_ROUTING ejecuta → respetado (header `gobernado_por`).

Caveat 5 (no abrir dominio #11) → respetado: AI_GOV es subfamilia conceptual, indexa por convención KB, no rompe los 10 dominios.

## Riesgo principal a vigilar

Lo más fácil al canonizar gobernanza es que se vuelva teatro: políticas escritas pero no enforced. Los **3 hookpoints críticos** que convierten esto de declarativo a ejecutable:

1. Action Engine consulta `POL_AI_GOV_DATA_CLASS_PROVIDER` antes de despachar → Sem 3+.
2. Token Ledger valida `provider_allowed_by_policy: true` antes de aceptar entry → Sem 3+.
3. Final pass dispatcher consulta `POL_AI_GOV_FINAL_OUTPUT_QUALITY` y respeta SCH_AI_GOV_HANDOFF_DRAFT → Sem 5-7.

Si los 3 no están en producción, AI_GOV es documentación. Que vivan en código es la métrica de éxito real.

---

Stamp: VIGENTE — 2026-05-01
