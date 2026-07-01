# MANIFIESTO_APPEND — 2026-05-01b — AI_GOV Dual Review

## Origen
Idea CEO 2026-05-01 sobre revisión cruzada controlada por dos IAs de familias distintas + síntesis. Propuesta evaluada por Cowork como arquitecto: SI canonizar, formato PLB + SCH (no agente, no skill, no POL nueva).

Contexto: lote AI_GOV canonizado horas antes (commit 860eaa2) provee la infraestructura sobre la cual este flujo opera (Token Ledger v1.3 con campo `role`, POL_AI_GOV_DATA_CLASS_PROVIDER, POL_AI_GOV_FINAL_OUTPUT_QUALITY, SPEC_AI_GOV_GOVERNANCE_AND_ROUTING).

## Decisiones arquitectónicas tomadas

| # | Decisión | Resolución |
|---|----------|------------|
| D1 | Tipo de artefacto | **PLB + SCH**, NO agente, NO skill, NO POL nueva. Razón: la dualidad obliga a 2 modelos distintos invocados por flujo, no es un agente único. |
| D2 | Naming | **`PLB_AI_GOV_DUAL_REVIEW`** + **`SCH_AI_GOV_DUAL_REVIEW_OUTPUT`**. Subfamilia AI_GOV. "DUAL" marca conceptual clave (vs "ADVERSARIAL" que es consecuencia). |
| D3 | Modo de operación | **MVP prescriptivo** (decisor ejecuta los 4 pasos manual). Ejecutable post Action Engine F1. Razón: hookpoints de governance no existen aún en runtime. |
| D4 | Regla inquebrantable de familias distintas | Proponente y auditor DEBEN ser de familias distintas (Anthropic/OpenAI/Google/Moonshot/DeepSeek). Tabla de pares válidos canonizada. Razón: misma familia = sycophancy de training compartido. |
| D5 | Sintetizador | Tercer modelo, típicamente el de máxima calidad disponible (Opus 4.7). Aplica POL_AI_GOV_FINAL_OUTPUT_QUALITY como final pass premium. NO puede ser el mismo proponente. |
| D6 | Anti-loop | 1 sola ronda completa por invocación. NO re-runs automáticos. P0 sin resolución → "RECHAZAR" o "APROBAR CON CAMBIOS". Razón: loops vacían budget. |
| D7 | Caps anti-teatro | 3 P1/semana por decisor, USD 2.50/run, USD 30/mes por decisor, fail_open=false. Razón: sin cap, el flujo se invoca para todo y se vuelve teatro. |

## Archivos creados (3)

| Archivo | Tipo | Status | Indexa en |
|---------|------|--------|-----------|
| `PLB_AI_GOV_DUAL_REVIEW.md` | PLB | VIGENTE v1.0 | IDX_GOBERNANZA Playbooks |
| `SCH_AI_GOV_DUAL_REVIEW_OUTPUT.md` | SCH | VIGENTE v1.0 | IDX_GOBERNANZA Schemas + SCHEMA_REGISTRY AI GOVERNANCE |
| `MANIFIESTO_APPEND_20260501b_AI_GOV_DUAL_REVIEW.md` | Manifest | VIGENTE | (manifiesto append-only) |

## Archivos extendidos (1)

| Archivo | Cambio | Versión |
|---------|--------|---------|
| `SPEC_AI_GOV_GOVERNANCE_AND_ROUTING.md` | +Componente 6 Dual Review (caso especial cadena Token Ledger con 3 entries role=carpintero+judge+final_pass) +refs en header. Renumera Eval Lab a Componente 7. | v1.0 → v1.1 |

## IDX actualizados (3)

| IDX | Cambios |
|-----|---------|
| `IDX_GOBERNANZA.md` | +1 PLB en Playbooks · +1 SCH en Schemas de Gobernanza · update SPEC_AI_GOV v1.0→v1.1 · update header health (11→12 PLBs, 3→4 SCHs) |
| `SCHEMA_REGISTRY.md` | +1 SCH en sección AI GOVERNANCE · total 20→21 schemas |
| `RW_ROOT.md` | update SPEC_AI_GOV descriptor v1.1 · header v4.8.19→v4.8.20 |

## Reglas inquebrantables agregadas

1. **Modelos de familias distintas obligatorio** en Proponente vs Auditor del Dual Review. Pares prohibidos documentados (Opus+Sonnet, GPT-5.5+GPT-5.5 Pro, etc.).
2. **Sintetizador no puede ser el Proponente.** Es tercer modelo (idealmente máxima calidad disponible).
3. **Veredicto APROBAR no compatible con P0 sin resolución.** Validación automática del schema.
4. **1 sola ronda completa por invocación.** Anti-loop hardcoded.
5. **Caps de invocación + costo no configurables al alza** sin justificación CEO documentada.

## Conexión con AI_GOV existente

| Componente AI_GOV | Cómo lo usa el Dual Review |
|---|---|
| Token Ledger v1.3 (SPEC_LLM_ROUTING_ARCHITECTURE) | 3 entries por invocación con mismo `parent_request_id`, distintos `role` (carpintero, judge, final_pass) |
| POL_AI_GOV_DATA_CLASS_PROVIDER | Filtra los 3 modelos según `data_classification` de la decisión técnica |
| POL_AI_GOV_FINAL_OUTPUT_QUALITY | El Sintetizador es final pass premium (campo `final_pass_executed: true`) |
| ENT_PLAT_ACTION_REGISTRY | Catálogo del cual se seleccionan los 3 modelos respetando familias distintas |
| SCH_AI_GOV_DUAL_REVIEW_OUTPUT (nuevo) | Schema obligatorio del veredicto final |
| ENT_AI_GOV_GOLDEN_CORPUS_MWT | Veredictos clean son candidatos a golden_case del task_type "dual_review_synthesis" |
| ENT_AI_GOV_OUTPUT_PINS | Combinación modelo proponente+auditor+sintetizador con score consistente alto puede pinearse |

## Lecciones aprendidas (indexadas)

1. **Familias distintas no es opcional.** Sin esa regla, el adversarialismo es teatro: modelos de la misma casa coinciden por sesgos compartidos. Mejor "Opus vs GPT-5.5" o "Sonnet vs Kimi" que "Opus vs Sonnet".

2. **El sintetizador es la pieza más cara y más importante.** Es donde se aplica final pass premium. Si lo escatimás (carpintero hace síntesis), el flujo pierde 60% de su valor.

3. **Anti-loop hardcoded > caps blandos.** Loops infinitos son la falla más cara. Mejor 1 ronda fija con escalación humana que caps que se "ajustan" en producción.

4. **Caps anti-teatro hay que ponerlos antes de invocarlo, no después.** Sin caps, el flujo se invoca para todo en semana 2, teatro en semana 4, abandonado en semana 8.

5. **Modo prescriptivo MVP es válido.** No esperar runtime ejecutable para canonizar el flujo. Bibliotecas humanas con disciplina superan a runtimes mal hechos.

## Pendientes inmediatos

| # | Pendiente | Owner | Trigger |
|---|-----------|-------|---------|
| P1 | Crear carpeta `docs/dual_reviews/` para preservar veredictos importantes | CEO | Próxima invocación P0 |
| P2 | Bitácora de invocaciones del flujo (manual MVP) — registrar problem_id, modelos usados, costo, veredicto | Decisor (Alejandro u otro) | Cada invocación |
| P3 | Primera invocación piloto del flujo sobre una decisión P1 real para calibrar prompts y caps | CEO | Cuando surja decisión P1 candidata |
| P4 | Revisión trimestral de telemetría (cuántas invocaciones, distribución de veredictos, pares de familias dominantes) | CEO | 2026-08-01 |
| P5 | Migración a modo ejecutable post Action Engine F1 (sem 3+ del roadmap) — bumping a v2.0 | AG-01/AG-02 | Post hookpoints AI_GOV en runtime |

## Diferido (intencional)

- **Modo ejecutable hoy:** bloqueado por Action Engine sem 3+. No se acelera.
- **Multi-rounds (más de 1 ronda):** prohibido por anti-loop. No se reabre sin evidencia de que el cap actual es insuficiente.
- **Auto-pin del sintetizador:** primero hay que invocar el flujo varias veces y observar consistencia. No pre-optimizar.
- **Skill ejecutable que orqueste el flujo:** rechazado en sesión arquitectónica — sería multi-agente libre, viola restricción operativa.

## Riesgo principal a vigilar

**Teatro de arquitectura.** Si el flujo se invoca para todo (incluso casos triviales), o si los modelos seleccionados son siempre los mismos (Opus vs Sonnet, violando familias distintas), pierde su valor en 8 semanas y se convierte en costo operativo sin retorno.

Mitigaciones canonizadas:
- Caps duros (3 P1/semana, USD 2.50/run, fail_open: false).
- Regla familias distintas hardcoded en validación del schema.
- Revisión trimestral CEO con métrica clara: si >70% veredictos son "APROBAR" sin cambios, el flujo se está sub-utilizando o aplicando a casos triviales — ajustar caps a la baja.

---

Stamp: VIGENTE — 2026-05-01b
