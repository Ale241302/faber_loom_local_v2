# MANIFIESTO_APPEND_20260428_ACTION_ENGINE
id: MANIFIESTO_APPEND_20260428_ACTION_ENGINE
type: TRANSITORIO
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE — 2026-04-28
expires: post-consolidación en MANIFIESTO_CAMBIOS_v2.md (próxima sesión de mantenimiento)
aplica_a: [SHARED]

---

## Contexto

Sesión Cowork 2026-04-28 derivó en decisión arquitectónica de fondo: introducir el **Action Engine** como módulo medular del sistema MWT/FaberLoom. La sesión cubrió:

1. Evaluación side-by-side DeepSeek V4-Pro vs Kimi K2.6 (test técnico Tier 0)
2. Test de orquestación Kimi K2.6 swarm (simulación 5 sub-agentes)
3. Propuesta MoAT (Mixture of Agents Tiered) con 3 tiers LIGHT/MEDIUM/EXTREME
4. Refinamiento "carpintería vs calidad" — separación explícita por tipo de trabajo
5. Decisión arquitectónica: Action Engine medular (no add-on)

CEO delegó decisión final al Arquitecto Cowork. Decisión tomada: **Opción D — contract-first, implementación incremental** (strangler fig pattern aplicado al diseño).

`indexa de una vez` autoriza la materialización en KB.

## Cambios ejecutados

### 1. SPEC_ACTION_ENGINE.md v1.0 (NUEVO — medular)

`docs/SPEC_ACTION_ENGINE.md` — el documento medular del sistema.

Cubre:
- Las 8 decisiones de diseño cementadas (D1-D8: async-first, bypass mode, schema strict, semver+deprecation, multi-tenant first-class, observability OpenTelemetry, library no service, circuit breaker + fallback)
- Contract API v1.0 (Python pseudo-code con ActionContext, ActionResult, ActionEngine)
- 3 escenarios de uso (LLM call, API externa, tool local con bypass)
- Mapeo a subsistemas: MoAT como Routing Policy, Carpintería/Calidad como tagging, P14 como ordering, P3 como side_effects gating, P13 como multi-tenant
- Failure modes con resiliencia obligatoria
- Observability schema OpenTelemetry-compatible
- Roadmap 9 semanas con triggers de aborto/pivot

### 2. SCH_ACTION_SPEC.yaml (NUEVO)

`docs/SCH_ACTION_SPEC.yaml` — schema de cada acción registrable.

Cubre:
- 12+ campos required (action_id, category, schemas I/O, capability map, performance profile, side_effects, multi_tenant, failure handling, versioning, observability)
- 6 campos opcionales (provider, region, data_residency, license, deployment_mode, notes)
- 5 reglas de validación adicionales (irreversible→human_gate, data_residency→compliance, tier_hint→cost, self_hosted→infra_cost, deprecation→sunset_in)
- Ejemplo completo con DeepSeek V4-Flash

### 3. ENT_PLAT_ACTION_REGISTRY.md (NUEVO)

`docs/ENT_PLAT_ACTION_REGISTRY.md` — catálogo inicial de 53 acciones del sistema.

Inventariadas:
- 12 LLM providers (Anthropic, OpenAI, Google, DeepSeek, Moonshot)
- 8 data APIs (Amazon SP-API, Helium 10, Supabase, autoridades fiscales LATAM)
- 5 communication APIs (Gmail, WhatsApp Business, Slack)
- 10 tools locales (regex, parsers XML, Pydantic validate, bash, python, file ops)
- 5 tools browser (computer-use, claude-in-chrome)
- 9 MCP servers
- 4 KB access methods

47 activo + 6 candidato. 5 pricing pendientes de WebSearch antes de Fase 2 (knowledge cutoff Cowork mayo 2025).

### 4. SPEC_LLM_ROUTING_ARCHITECTURE.md v1.1 → v1.2

Marcado como **subcomponente del Action Engine**. El L1/L2/L3 sigue válido pero ahora ejecuta dentro del Engine como Routing Policy para `action_category == llm_provider`. Cambio de framing, no de implementación.

## Por qué Opción D vs A/B/C

Tres opciones consideradas y descartadas:

| Opción | Por qué descartada |
|---|---|
| A. Action Engine medular pleno antes de FaberLoom MVP | Delay 9 semanas → 9-13% de ventana competitiva LATAM (18-24 meses). Riesgo time-to-market |
| B. Action Engine para FaberLoom desde diseño, MWT migra después | Genera divergencia arquitectónica MWT vs FaberLoom. Doble mantenimiento meses |
| C. MWT-first, FaberLoom hereda v2 | FaberLoom MVP usa arquitectura "vieja", refactor masivo después. Deuda técnica intencional desde día 1 |

**Opción D elegida:** contract-first (sem 1-2) + implementación trivial (sem 3) + crecimiento incremental detrás del contrato (sem 4-9). FaberLoom MVP arranca en sem 3 sobre contrato estable, no sobre arquitectura vieja. MWT migra a su ritmo. Cero refactor masivo después.

## Las 8 decisiones cementadas (no negociables sin major bump)

| # | Decisión | Resolución |
|---|---|---|
| D1 | Sync vs async | **Async-first**, wrapper sync para legacy |
| D2 | Bypass mode | **Obligatorio**, con razón loggeada para auditoría |
| D3 | Schema enforcement | **Estricto desde v1**, Pydantic v2 |
| D4 | Versionado | **Semver + deprecation cycle 2 versiones** |
| D5 | Multi-tenant | **First-class desde v1**, RLS a nivel Engine |
| D6 | Observability | **JSON estructurado + OpenTelemetry-compatible** |
| D7 | Library vs Service | **Library** (Python package), sin SPOF |
| D8 | Failure handling | **Circuit breaker + fallback to direct call** |

## Counts post-indexación

| Métrica | Antes (post Kimi #3 Ruflo) | Después | Delta |
|---|---|---|---|
| Total .md | 424 | 427 | +3 (SPEC_ACTION_ENGINE, ENT_PLAT_ACTION_REGISTRY, MANIFIESTO_APPEND) |
| Total .yaml | 0 | 1 | +1 (SCH_ACTION_SPEC.yaml) |
| docs/ activos (.md) | 288 | 291 | +3 |
| docs/anexos/ | 17 | 17 | 0 |
| docs/archivo/ | 105 | 105 | 0 |
| audit/reportes | 11 | 11 | 0 |
| raíz | 3 | 3 | 0 |

**Nota:** SCH_ACTION_SPEC se mantuvo como `.yaml` por preservar machine-readability del schema. Es el primer archivo no-`.md` en docs/ activos.

## Archivos modificados (resumen)

| Archivo | Versión | Tipo de cambio |
|---|---|---|
| `SPEC_ACTION_ENGINE.md` | v1.0 (NUEVO) | Documento medular |
| `SCH_ACTION_SPEC.yaml` | v1.0 (NUEVO) | Schema de acción registrable |
| `ENT_PLAT_ACTION_REGISTRY.md` | v1.0 (NUEVO) | Catálogo inicial 53 acciones |
| `SPEC_LLM_ROUTING_ARCHITECTURE.md` | v1.1 → v1.2 | Marcado como subcomponente del Action Engine |
| `MANIFIESTO_APPEND_20260428_ACTION_ENGINE.md` | v1.0 (NUEVO) | Este archivo |

## Riesgos asumidos por el Arquitecto

Documentados explícitamente en SPEC_ACTION_ENGINE §"Riesgo que estoy asumiendo":

1. Si el contrato sale mal en sem 1-2, todo lo que viene encima hereda el problema → mitigado por aprobación binaria al final de sem 2 con spike por consumer
2. FaberLoom MVP en sem 4-9 corre sobre Engine "trivial" sin features avanzados → aceptable, contrato cubre
3. Tentación de agregar features al contrato durante sem 4-9 → disciplina: contrato congelado hasta v2
4. MWT migra gradual = 2 caminos paralelos durante semanas → aceptable, mejor que big bang
5. Adaptive Tuner se posterga a sem 10+ → OK para MVP, no necesario inicial

## Triggers de aborto/pivot (de SPEC_ACTION_ENGINE)

| Trigger | Acción correctiva |
|---|---|
| Sem 2: Contract API no cierra tras review CEO | Volver a sem 1, redefinir |
| Sem 3: Implementación trivial >5 días | Algo del contrato mal definido |
| Sem 6: FaberLoom MVP bloqueado por gap del Engine | Relajar contrato congelado, abrir v1.1 |
| Sem 9: Sin Capability Map útil | Revisar prioridades del backlog |
| Performance overhead >10ms p99 | Stop ship hasta resolver |

## NO ejecutado (pendiente CEO o próxima sesión)

| Pendiente | Razón |
|---|---|
| WebSearch pre-Fase 2 para verificar pricing actual abril 2026 (Haiku 4.5, Sonnet 4.6, Kimi K2.6 API managed, GPT-5.5 mini) | Antes de cementar Routing Policy |
| Update DEPENDENCY_GRAPH.md con Action Engine como nodo central | Sesión de mantenimiento |
| Update RW_ROOT.md counts (424→428) | Sesión de mantenimiento |
| Update IDX_PLATAFORMA con refs a SPEC_ACTION_ENGINE + ENT_PLAT_ACTION_REGISTRY + SCH_ACTION_SPEC | Sesión de mantenimiento |
| Spike de 1 día por consumer principal (AG-01, AG-02, AG-06, AG-07, FaberLoom) — validar Contract API | Sem 2 del roadmap |
| POL_ACTION_OVERRIDE.md (override de side_effects irreversible) | Sem 3+ cuando se necesite |
| Implementación Python `mwt_action_engine` package | Sem 3 del roadmap |

## Próxima acción CEO recomendada

1. **Git sync inmediato** — esta sesión deja todo committable. Sugerencia commit:
   ```
   [PLATAFORMA] Action Engine medular — SPEC + Schema + Registry + LLM Routing como subcomponente

   - Nuevo SPEC_ACTION_ENGINE v1.0 (decisión D contract-first, 8 decisiones cementadas)
   - Nuevo SCH_ACTION_SPEC.yaml (schema de acción registrable)
   - Nuevo ENT_PLAT_ACTION_REGISTRY v1.0 (catálogo 53 acciones)
   - SPEC_LLM_ROUTING_ARCHITECTURE v1.1 → v1.2 (subcomponente del Engine)

   Origen: sesión Cowork 2026-04-28. Decisión arquitectónica delegada al Arquitecto.
   Roadmap 9 semanas. Triggers de aborto documentados.
   ```

2. **Spike de validación sem 2** — antes de cementar Contract API, validar con 5 consumers reales (AG-01..AG-07 + FaberLoom MVP) que la firma es viable.

3. **WebSearch pricing** — antes de Fase 2 (sem 3), verificar pricing actual abril 2026 de Haiku 4.5, Sonnet 4.6, Kimi K2.6 (API managed vs self-host), GPT-5.5 mini.

4. **Decisiones diferidas** — POL_ACTION_OVERRIDE, DEPENDENCY_GRAPH update, IDX_PLATAFORMA update — postponer a próxima sesión de mantenimiento.

---

Trigger: CEO `eres el arquitecto debes de decidir eso` → decisión D → `indexa de una vez` (sesión 2026-04-28, Cowork mode).
