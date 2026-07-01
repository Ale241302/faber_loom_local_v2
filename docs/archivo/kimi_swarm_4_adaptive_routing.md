# kimi_swarm_4_adaptive_routing
id: AUDIT_KIMI_SWARM_4_ADAPTIVE_ROUTING
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
stamp: DRAFT 2026-04-21
classification: AUDIT — Síntesis verbatim validación multi-agente Kimi Swarm #4 sobre §9 Adaptive Routing FaberLoom
fuente_origen: /kimi_swarm_unzip/FABERLOOM_EVALUACION_COMPLETA.md (workspace upload CEO)
plan_origen: /kimi_swarm_unzip/plan.md (orquestador 4 sub-agentes paralelos A1/A2/A3/A4)

---

## Contexto

Cuarta iteración de validación externa vía Kimi 2.6 swarm. Target: spec §9 Adaptive Routing FaberLoom (runtime router + evidence ledger + weekly tuning ritual + model discovery + 4 tablas nuevas + score compuesto + guardrails N≥20). 4 sub-agentes especializados en paralelo (Cost/Econ, Reliability, DataSci, Security) + síntesis final.

**Veredicto global:** `LOW confidence` en adaptive routing F1.

**Consecuencia canonizada:** downgrade a tiered hardcoded routing F1. Adaptive postpuesto F2 gated a 3 tenants × 5K drafts/mes sostenido × 3 meses. Ref: DEC-006 a DEC-008 en `ENT_GOB_DECISIONES.md`.

---

## A1_COST — Cost/Econ Analyst (verbatim)

### ¿El 75% de ahorro vs Sonnet-everywhere aguanta?
**No. El 75% es optimista; con distribución 40/40/20 el ahorro real es ~59%, post-costos-ocultos ~46%.**

| Escenario @ 600 drafts/mes | Costo/mes | Ahorro |
|---|---|---|
| Sonnet-everywhere | $20.88 | — |
| Routing óptimo (Flash/DeepSeek/Sonnet) | $8.61 | 58.8% |
| + Ollama local simples | $8.52 | 59.2% |

- Supuesto: tokens/draft = simple 2K/800, medio 4K/1.5K, complejo 8K/3K.
- El 75% sólo se alcanza con Ollama local + <10% complejos.
- Ahorro real post-ocultos: ~46% ($20.88 → $11.27).

### Costos ocultos no trackeados

| Concepto | $/mes |
|---|---|
| Shadow testing (10% requests, modelo secundario) | $0.93 |
| Fallbacks (5% → dispara Sonnet) | $1.47 |
| Re-runs errores (3% retry) | $0.26 |
| Total ocultos | ~$2.67 |

Faltan: costo operativo humano (debugging multi-modelo) ≈ $200/mes mínimo.

### Fórmula Break-Even

```
           C_fixed + C_ops
    N ≥ ─────────────────────
        c_sonnet − c_route − h

    Plug-in FaberLoom:
    N ≥ $200 / ($0.035 − $0.014 − $0.004) = 9,524 drafts/mes
```

**Conclusión:** a 600 drafts/mes el ahorro marginal (~$9/mes) no amortiza el costo operativo. Adaptive routing es over-engineering en beta. Recomendación: hardcoded routing (simple→Flash, complejo→Sonnet) sin evidence ledger hasta ≥5K drafts/mes.

---

## A2_RELIABILITY — Reliability Engineer (verbatim)

### ¿El fallback chain genera cascade failures?
**Sí. Tres escenarios de tormenta:**

1. Rate-limit provider compartido: Sonnet + Haiku comparten Anthropic. Fallback a Haiku golpea mismo rate-limit. Blast radius: 2 modelos.
2. Timeout regional: problema en US-East afecta Anthropic, OpenAI, Google. Blast radius: 4 modelos.
3. Cadena secuencial: 7 modelos × retry × 3 tenants = hasta 21 requests amplificados por draft fallido si no hay `max_fallbacks`.

Mitigación obligatoria: limitar a max 2 saltos. Retry exponencial (1s, 2s). No fallback dentro del mismo provider/region.

### ¿SPOF LiteLLM proxy?
**Sí. SPOF crítico.** Todo tráfico pasa por un único proxy. Si cae: 0% requests atendidos. pg-boss acumula jobs con timeout. Mitigación: 2 instancias (activo/pasivo), health check HTTP cada 10s, backoff exponencial si proxy down >30s.

### Circuit Breaker Policy recomendada — dos niveles: por provider + por modelo

| Métrica | Cerrado→Abierto | Half-Open | Abierto→Cerrado |
|---|---|---|---|
| Error rate | ≥50% en últimos 20 req | 1 req de prueba | <10% en 10 req |
| Latencia p99 | >15s en ventana 60s | 1 req | <5s en 5 req |
| Rate limit 429 | ≥3 consecutivos | 1 req tras 60s | 200 OK |

- CB provider abierto → bloquea todos los modelos de ese provider (evita fallback inútil).
- CB modelo abierto → excluye del ranking. Fuerza `error_rate = 1.0` en score compuesto.
- Ventana CB: 60s fija (tiempo real), independiente del weekly tuning.

---

## A3_DATASCI — Data Scientist (verbatim)

### ¿N≥20/semana detecta delta 5pp en approval rate?
**No. Insuficiente por orden de magnitud.**

- Test de proporciones: H0: p1=p2, H1: |p1-p2|≥0.05, α=0.05, p_base≈0.70.
- Cohen h ≈ 0.112. Con n=20: power ≈ 6.5% (prácticamente α).

| N/semana | Power aprox. |
|---|---|
| 20 | 6.5% |
| 50 | 8.7% |
| 100 | 12.5% |
| 200 | 20.2% |
| 500 | ~50% |
| 1,250 | ≥80% |

Mínimo recomendado: N≥100 (exploratory); para decisión con confianza: N≥500.

### ¿Pesos 0.40/0.20/0.15/0.15/0.10 defensibles?
**Heurísticos sin fundamento teórico.** Sensibilidad (Kendall τ vs pesos base):
- approval ±0.10 → τ varía 0.43–1.00
- latency ±0.10 → τ varía 0.43–0.91
- Top-2 robusto, posiciones 3–7 volátiles.

Recomendación: aprender pesos vía regresión logística (approval como target) o Pareto optimization.

### Decay 0.9/mes
**Demasiado lento.** Half-life ≈ 6.6 meses.

| Edad muestra | Peso restante |
|---|---|
| 3 meses | 72.9% |
| 6 meses | 53.1% |

Recomendación: decay por semana con factor 0.85 (half-life ≈ 4.3 semanas) o concept drift detection (Page-Hinkley, ADWIN).

### MAB (Thompson Sampling) vs Weekly Batch

| Criterio | Weekly Batch | Thompson Sampling |
|---|---|---|
| Latencia adaptación | 1 semana | Online (per-request) |
| Overhead | O(1) | O(K) ≈ 7 muestras Beta |
| Regret | O(K·T) sublinear lento | O(√(KT log T)) |

- MAB supera batch cuando: concept drift, K≤10, costo subóptimo alto.
- MAB NO vale la pena cuando: tráfico < 100 req/día.
- Umbral FaberLoom: con ~20 drafts/día, datos escasos. Recomendar MAB híbrido: Thompson para top-3 con ε-greedy, batch semanal para resto.

---

## A4_SECURITY — Security/Compliance (verbatim)

### CEO-ONLY data → Kimi/DeepSeek (China): ¿bloqueo duro?
**No existe data-classification-based routing en el spec. Gap crítico.**
- Router rutea por score compuesto, ignorando jurisdicción.
- Datos estratégicos PyMEs LATAM pueden aterrizar en servidores chinos.
- Incumplimiento: Ley 25.326 (AR), LGPD (BR), Ley 1581 (CO) — requieren consentimiento para transferencia internacional de datos sensibles.
- Mitigación: hard block por clasificación + `allowed_providers` por tenant.

### ¿Shadow testing filtra datos reales?
**Sí. El spec no menciona anonimización, datos sintéticos, ni consentimiento.**
- Modelo candidato procesa requests reales de producción en paralelo.
- Datos de cotización (PII potencial de trabajadores) filtran a providers no aprobados.
- Riesgo: viola principio de finalidad (art. 9 LGPD, art. 6 Ley 1581).
- Mitigación mínima: dataset sintético/redactado; consentimiento explícito por tenant.

### Policy_version append-only: ¿suficiente auditoría?
**Insuficiente para ISO 27001 / SOC 2 Type II.**
- Falta: actor/identidad del modificador, workflow 4-eyes, rationale del cambio, firma digital/non-repudiation.
- Gap crítico: admin comprometido altera routing sin accountability trazable.

### Cross-tenant: ¿influencia via evidence global?
**Sí. Las 4 tablas no declaran `tenant_id`. Supuesto: tablas globales.**
- Tenant A inyecta datos adversariales → contamina `evidence_log` → sesga score compuesto → altera routing de Tenant B.
- Mitigación: sandboxing per-tenant en scoring + evidence aislada por `tenant_id`.

---

## Síntesis Final Kimi (verbatim)

### Overall Confidence: **LOW**

El spec §9 Adaptive Routing tiene una arquitectura conceptualmente sólida pero no es lanzable en F1 sin resolver gaps críticos en seguridad multi-tenant, resiliencia de infraestructura, y fundamentación estadística. El ahorro económico está sobreestimado para la escala actual, lo que sugiere que el adaptive routing es prematuro para 600 drafts/mes.

### Top 3 Blockers antes de F1 Launch

| # | Blocker | Riesgo | Agente |
|---|---|---|---|
| 1 | Cross-tenant evidence poisoning: `evidence_log` y `model_scores` sin `tenant_id` permiten que Tenant A contamine el routing de Tenant B | Data leakage, SLA breach, regulador | A4 |
| 2 | SPOF LiteLLM proxy: caída total del servicio con único proxy, sin replicación ni health checks | 0% availability, acumulación jobs pg-boss | A2 |
| 3 | Data residency sin guardrails: CEO-ONLY / datos sensibles pueden rutearse a Kimi/DeepSeek (China) violando Ley 25.326, LGPD, Ley 1581 | Multas regulatorias, pérdida clientes enterprise | A4 |

### Top 3 Mejoras 10× (no bloquean pero reducen riesgo/complejidad)

| # | Mejora | Impacto | Agente |
|---|---|---|---|
| 1 | Reemplazar adaptive routing por hardcoded tiered routing (simple→Flash/GPT-4o-mini, complejo→Sonnet) hasta ≥5K drafts/mes. Elimina evidence ledger, weekly tuning, y N≥20. Reduce complejidad operativa 10× | TTM rápido, sin deuda técnica prematura | A1, A3 |
| 2 | Circuit breaker por provider + por modelo con thresholds concretos (50% error/20 req, half-open 1 req, recovery <10%/10 req) | Resiliencia profesional, sin cascade failures | A2 |
| 3 | Concept drift detection (Page-Hinkley o ADWIN) en vez de decay fijo 0.9/mes. Recalibra sólo cuando hay evidencia de drift, no en ciclo fijo | Adaptación real, menos varianza en rankings | A3 |

### 1 cosa que el spec NO considera y debería

**Cold start de nuevos tenants (bootstrap problem).**

Cada nuevo tenant empieza con N=0 muestras en `evidence_log` para todos los modelos. El guardrail N≥20 lo excluye de routing informado durante semanas. El spec no define:
- Default routing para tenants sin evidence (¿Sonnet everywhere temporal? ¿tiered heuristic?)
- Transfer learning entre tenants (¿puede un nuevo tenant heredar el ranking de un tenant similar?)
- Warm-up period con exploración forzada antes de activar N≥20

Este problema es crítico en beta: con solo 3 tenants, cada onboarding nuevo reduce el tráfico agregado disponible para mantener N≥20 en todos los modelos, degradando la calidad del routing para todos.

---

## Mejoras Kimi capitalizables hoy (destino en ENT_PLAT_LLM_ROUTING v2.0)

- Tiered hardcoded routing F1 en YAML (source-of-truth en git).
- HA LiteLLM: 2 instancias (primary:4000, backup:4001) + HAProxy/Caddy health check 10s.
- Nueva tabla `tenant_model_allowlist` (tenant × data_classification → allowed_providers + blocked_regions). Hard block pre-tier-check.
- `tenant_id` + RLS en `llm_usage_log` obligatorios.
- Circuit breakers por provider + por modelo, estado Redis, thresholds definidos.
- Cold start explícito: 30 días exploración manual con YAML default + CEO review de samples. Sin transfer learning inter-tenant en F1 (fricción legal).

## Mejoras Kimi diferidas a F2 (postergar junto con adaptive routing)

- Decay semanal 0.85 (half-life 4.3 semanas) vs mensual 0.9.
- Concept drift detection (Page-Hinkley o ADWIN) reemplaza decay fijo.
- MAB híbrido: Thompson para top-3 + ε-greedy + batch semanal para resto.
- Pesos aprendidos vía regresión logística con approval como target (no 0.40/0.20/0.15/0.15/0.10 heurísticos).
- Umbral mínimo N≥500 para decisión con confianza (no N≥20).
- 4-eyes workflow + firma digital policy changes para SOC 2.
- Dataset sintético/redactado para shadow testing (no producción real).

---

## Orquestación del swarm (referencia para Research Swarm F1)

Plan.md original del swarm:

- Stage 1 — 4 sub-agentes en paralelo sin dependencias:
  - A1_COST (Cost/Econ Analyst)
  - A2_RELIABILITY (Reliability Engineer)
  - A3_DATASCI (Data Scientist)
  - A4_SECURITY (Security/Compliance)
- Stage 2 — Síntesis final con Overall confidence + Top 3 blockers + Top 3 mejoras 10× + 1 cosa que el spec NO considera.

Reglas observadas:
- Máx 300 palabras por sección.
- Formato estricto, sin prosa de relleno.
- Señalar supuestos inline.
- Output único en markdown (sin archivos intermedios) — la síntesis integra los 4 resultados.

Esto valida empíricamente el patrón fan_out_reduce propuesto en el SPEC Research Swarm F1.

---

## Refs activos

- `ENT_PLAT_LLM_ROUTING.md` v1.0 → v2.0 (target de promoción de insights)
- `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` (schema S1 pendiente de bump)
- `SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md` (SPOF mitigation relevante al runtime)
- `ENT_GOB_DECISIONES.md` v1.0 → v2.0 (DEC-006/007/008 canonizan veredicto)
- `ENT_GOB_PENDIENTES.md` (Q1-Q18 batch nuevo)
- `/kimi_swarm_unzip/FABERLOOM_EVALUACION_COMPLETA.md` (fuente — upload CEO 2026-04-21)

## Stamp

AUDIT DRAFT desde 2026-04-21. Verbatim preservado de Kimi 2.6 swarm validation run. No es canon per se — canon vive en `ENT_PLAT_LLM_ROUTING.md` v2.0 y DECs asociadas. Este archivo sirve como trail de evidencia para auditoría posterior.

Changelog:
- v1.0 (2026-04-21): indexación inicial verbatim Kimi Swarm #4. Trigger CEO "indexa".
