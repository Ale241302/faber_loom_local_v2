# ENT_PLAT_LLM_ROUTING — Gestión de Modelos LLM y Routing
id: ENT_PLAT_LLM_ROUTING
version: 2.0.1
status: DRAFT
visibility: [INTERNAL]
ceo_only_sections: [D]
domain: Plataforma (IDX_PLATAFORMA)
stamp: DRAFT 2026-04-21
refs: ENT_PLAT_INFRA, ENT_PLAT_KNOWLEDGE, ENT_PLAT_SEGURIDAD, ENT_PLAT_MEMORY_STACK, PLB_PROMPTING, ENT_GOB_PENDIENTES.CEO-24, ENT_GOB_DECISIONES.DEC-006/DEC-007/DEC-008, docs/archivo/kimi_swarm_4_adaptive_routing.md, SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT, SPEC_FABERLOOM_WORKFLOW_ENGINE_v1
aplica_a: [SHARED]

---

## A. Propósito

SSOT de qué modelos LLM están disponibles para MWT y FaberLoom, su pricing, capacidades, y cómo el sistema elige cuál usar para cada tarea. Alimenta el módulo PLT-11 (pendiente CEO-24) y es consumido por PLB_PROMPTING para instrucciones operativas, por SPEC_FABERLOOM_ARCHITECTURE para el motor runtime, y por SPEC_FABERLOOM_WORKFLOW_ENGINE para contención.

**v2.0 canoniza el veredicto Kimi Swarm #4 (2026-04-21):** downgrade de adaptive routing a tiered hardcoded en F1; adaptive postpuesto F2 gated. Mantiene intacto el data de mercado (arena rankings, pricing, aliases).

---

## B. Rankings verificados (arena.ai — snapshot 18 marzo 2026)

> **Volatilidad:** Scores fluctúan 2-5 puntos cada 2-7 días. Modelos con < 10 puntos de diferencia son equivalentes. Posiciones exactas pueden invertirse entre actualizaciones.

### B1. Text (Overall)
| # | Modelo | Score | Fortaleza | Debilidad |
|---|--------|-------|-----------|-----------|
| 1 | Claude Opus 4.6-thinking | 1501 | Hard Prompts #1, Instruction Following #1 | — |
| 2 | Claude Opus 4.6 | 1501 | Expert #1, Code #2 | — |
| 3 | Gemini 3.1 Pro Preview | 1493 | Creative Writing #1 | Expert #4 |
| 4 | Grok 4.20-beta1 | 1492 | Creative #4 | Math #17 |
| 5 | Gemini 3 Pro | 1486 | Creative #3, Math #5 | Code #11 |
| 6 | GPT-5.4-high | 1485 | Expert #3, Math #2 | Creative #9 |

### B2. Code
| # | Modelo | Score |
|---|--------|-------|
| 1 | Claude Opus 4.6 | 1549 |
| 2 | Claude Opus 4.6-thinking | 1547 |
| 3 | Claude Sonnet 4.6 | 1518 |
| 6 | GPT-5.4-high (codex) | 1456 |
| 7 | Gemini 3.1 Pro Preview | 1451 |

### B3. Vision
| # | Modelo | Score |
|---|--------|-------|
| 1 | Gemini 3 Pro | 1288 |
| 2 | Gemini 3.1 Pro Preview | 1279 |
| 3 | GPT-5.2 | 1278 |

### B4. Document
| # | Modelo | Score |
|---|--------|-------|
| 1 | Claude Opus 4.6 | 1524 |
| 2 | Claude Sonnet 4.6 | 1491 |
| 3 | GPT-5.4 | 1483 |

### B5. Search
| # | Modelo | Score |
|---|--------|-------|
| 1 | Claude Opus 4.6-search | 1255 |
| 2 | Grok 4.20-beta1 | 1225 |
| 3 | GPT-5.2-search | 1219 |
| 4 | Gemini 3 Flash-grounding | 1218 |

### B6. Text-to-Image
| # | Modelo | Score |
|---|--------|-------|
| 1 | Gemini 3.1 Flash Image (nano-banana-2) | 1268 |
| 2 | GPT Image 1.5 high-fidelity | 1248 |
| 3 | Gemini 3 Pro Image (nano-banana-pro) | 1236 |
| 5 | Reve v1.5 | 1177 |

### B7. Creative Writing (subcategoría)
| # | Modelo |
|---|--------|
| 1 | Gemini 3.1 Pro Preview |
| 2 | Claude Opus 4.6-thinking |
| 3 | Gemini 3 Pro |

---

## C. Pricing verificado (marzo 2026, fuentes oficiales)

| Modelo | Input/1M | Output/1M | Context | Max Output | Fuente |
|--------|----------|-----------|---------|------------|--------|
| Claude Opus 4.6 | $5.00 | $25.00 | 1M | 128K | anthropic.com |
| Claude Sonnet 4.6 | $3.00 | $15.00 | 1M | 64K | anthropic.com |
| Claude Haiku 4.5 | $1.00 | $5.00 | 200K | — | anthropic.com |
| GPT-5.4 | $2.50 | $15.00 | 1.05M (272K estándar, 1M opt-in) | 128K | openai.com |
| GPT-5.4 mini | $0.75 | $4.50 | — | — | openai.com |
| GPT-5.4 nano | $0.20 | $1.25 | — | — | openai.com |
| Gemini 3 Pro | $2.00 | $12.00 | 1M (>200K = 2x) | 65K | ai.google.dev |
| Gemini 3 Flash | $0.50 | $3.00 | 1M | 64K | ai.google.dev |
| Gemini 3.1 Flash Lite | $0.25 | $1.50 | 1M | — | ai.google.dev |
| DeepSeek V3.2 | $0.28 | $0.42 | 128K | 8K chat / 64K reasoner | deepseek.com |
| DeepSeek V3.2 cache hit | $0.028 | $0.42 | 128K | — | deepseek.com |
| Kimi K2.5 | $0.60 | $3.00 | 256K | 32K | ⛔ NO VERIFICADO |

> **Long-context surcharges:** GPT-5.4 >272K = 2x input, 1.5x output. Gemini Pro >200K = 2x. Claude Opus/Sonnet 4.6 = flat pricing en todo el 1M.

### C1. Tabla de aliases (nombre comercial ↔ API ID ↔ Arena ↔ context real)

| Nombre comercial | Model ID (API) | Nombre en Arena | Context real |
|-----------------|----------------|-----------------|-------------|
| Claude Opus 4.6 | claude-opus-4-6 | claude-opus-4-6 | 1M |
| Claude Opus 4.6 thinking | claude-opus-4-6 + thinking:adaptive | claude-opus-4-6-thinking | 1M |
| Claude Sonnet 4.6 | claude-sonnet-4-6 | claude-sonnet-4-6 | 1M |
| GPT-5.4 | gpt-5.4 | gpt-5.4 | 1.05M (272K estándar) |
| GPT-5.2 | gpt-5.2 | gpt-5.2-chat-latest-20260210 | 400K |
| GPT-5.2 (alias chat) | gpt-5.2-chat-latest | gpt-5.2-chat-latest | 128K ≠ gpt-5.2 |
| DeepSeek V3.2 (chat) | deepseek-chat | deepseek-v3.2 | 128K |
| DeepSeek V3.2 (reasoner) | deepseek-reasoner | deepseek-v3.2-thinking | 128K |
| Gemini 3 Pro | gemini-3-pro-preview | gemini-3-pro | 1M |
| Gemini 3 Flash | gemini-3-flash-preview | gemini-3-flash | 1M |

---

## D. Task routing (tabla de cascade) [CEO-ONLY — contiene estrategia de costos]

| Task type | Tier 1 (primero) | Tier 2 (fallback) | Tier 3 (último recurso) | Estrategia |
|-----------|-----------------|-------------------|------------------------|------------|
| classification | deepseek-chat | gemini-3-flash | claude-sonnet-4-6 | CHEAPEST_FIRST |
| b2b_response | deepseek-chat | claude-sonnet-4-6 | — | CHEAPEST_FIRST |
| code_generation | claude-opus-4-6 | gpt-5.4 | deepseek-chat | BEST_FIRST |
| code_review | claude-opus-4-6 | gpt-5.4 | — | BEST_FIRST |
| document_analysis | claude-opus-4-6 | gemini-3-pro | gpt-5.4 | BEST_FIRST |
| creative_writing | gemini-3.1-pro | claude-opus-4-6 | deepseek-chat | BEST_FIRST |
| copy_marketing | gpt-5.4 | gemini-3-pro | gemini-3-flash | BEST_FIRST |
| search_research | claude-opus-4-6-search | grok-4.20 | gemini-3-flash-grounding | BEST_FIRST |
| factcheck_quick | gemini-3-flash-grounding | claude-opus-4-6-search | — | CHEAPEST_FIRST |
| image_product_main | gpt-image-1.5 | gemini-3-pro-image | — | BEST_FIRST |
| image_product_text | ideogram-3.0 | gpt-image-1.5 | — | SINGLE |
| image_lifestyle | midjourney-v7 | gemini-3-pro-image | — | BEST_FIRST |
| vision_ocr | gemini-3-pro | gemini-3-flash | — | CHEAPEST_FIRST |
| pipeline_batch | deepseek-chat | gemini-3-flash | — | CHEAPEST_FIRST |
| strategic_decision | claude-opus-4-6-thinking | gpt-5.4-high | — | BEST_FIRST |

> Esta tabla sigue siendo el contrato MWT (catálogo maestro de rutas). FaberLoom F1 consume un **subset tier-based** derivado, no toda la granularidad (ver §F).

---

## E. PLT-11 — Arquitectura del módulo (MWT — pendiente CEO-24)

### E1. Modelo de datos (6 tablas PostgreSQL, NUNCA pgvector)

> v2.0 agrega `tenant_model_allowlist` (residencia de datos) y hace `tenant_id` obligatorio en `llm_usage_log`. Alineado con Kimi A4 + SPEC_FABERLOOM_ARCHITECTURE.

**llm_providers:** id, name, api_key_encrypted (Fernet), status (ACTIVE/PAUSED/REVOKED), region (cloud region principal: us-east, eu-west, cn-north, local), budget_monthly_usd, budget_used_usd, created_at, updated_at, notes.

**llm_models:** id, model_id, provider (FK), display_name, input_cost_per_m, output_cost_per_m, context_window, max_output, capabilities (JSONField), status (ACTIVE/OBSERVACIÓN/DEPRECATED), semaphore (GREEN/YELLOW/RED), ficha_md (TextField), last_verified_at, verification_source, notes.

**llm_model_scores:** id, model (FK), category (str: text, code, vision, document, search, creative, image), arena_score (int), arena_rank (int), snapshot_date.

**llm_task_routing:** id, task_type (str unique), description, tier1_model (FK), tier2_model (FK), tier3_model (FK nullable), cascade_strategy (CHEAPEST_FIRST/BEST_FIRST/SINGLE), updated_at. (MWT-owned — FaberLoom F1 no lo usa; usa YAML en git — ver §F.)

**llm_usage_log:** id, timestamp, tenant_id (FK obligatoria — RLS enforced), model (FK), task_type, tokens_input, tokens_output, cost_usd, latency_ms, success, error_message, caller, request_id, attempt_no, http_status, metadata (JSONField). Index: `idx_usage_tenant_time (tenant_id, timestamp DESC)`.

**llm_weekly_snapshots:** id, snapshot_date, rankings_json, pricing_json, changes_detected (nullable), alert_sent.

**tenant_model_allowlist** (NUEVA v2.0 — data residency hard block): id, tenant_id (FK), data_classification (enum: PUBLIC/INTERNAL/CONFIDENTIAL/CEO_ONLY), allowed_providers (array FK llm_providers), blocked_regions (array str: cn, ru, …), reason_denied_default (str), updated_at, updated_by (FK users), approved_by (FK users). RLS por tenant_id. **Evaluada ANTES del tier check**: si el modelo candidato cae en `blocked_regions` o el provider no está en `allowed_providers` para esa clasificación → hard deny, log a audit trail, escalamiento a CEO. CEO_ONLY nunca rutea a CN/RU por default; requiere approval explícito del owner del tenant para relajar.

## Fugu Standard como provider externo (FG-02 — sesion Fugu 2026-06-24)

Fugu confirmo explicitamente la siguiente matriz para uso como provider externo:

| Data class | Fugu Standard | Fugu Ultra | Condicion |
|---|---|---|---|
| N0/N1 | PERMITIDO | REVISAR | Si tenant lo habilita en allowlist |
| N2 | CONDICIONAL | NO | Solo con masking + tenant policy explicita |
| N3/N4 | NO | NO | Solo DPA LATAM firmado o self-hosted |

Registro en tenant_model_allowlist: provider=fugu-standard, allowed_data_class=[N0,N1],
blocked_for=[N2_sin_masking, N3, N4], requires_tenant_approval=true.
Ref: ENT_FABERLOOM_INSIGHTS_FUGU_SESSION FG-02.

### E2. Execution layer — LiteLLM Proxy HA (v2.0)

Django = control plane (gobierno, fichas, budgets, semáforo, UI).
LiteLLM Proxy = execution plane (routing, retry, fallback, spend tracking, normalización API).

**v2.0 elimina SPOF (hallazgo Kimi A2):**

- 2 instancias LiteLLM en Hostinger KVM 8 (primary :4000, backup :4001).
- HAProxy o Caddy como reverse proxy con health check HTTP `/health` cada 10s.
- Política: retry en primary → si error persistente, flip a backup; si ambos caen >30s → pg-boss queue with timeout, CEO alerta.
- Keys Fernet compartidas vía shared secret mount (no duplicadas).
- Observabilidad: Langfuse + Prometheus exporter de LiteLLM.

### E3. Windmill cron (lunes 3am, ~30 seg)

Scrape arena.ai + pricing pages → compara vs snapshot anterior → si cambios: actualiza llm_models + notifica CEO vía n8n → si modelo nuevo en top 10: registra como OBSERVACIÓN (semáforo YELLOW).

**Trigger 1 — Detección temprana (semana del lanzamiento):**
Modelo nuevo en top 10 → status: OBSERVACIÓN, semaphore: YELLOW. NO entra en routing.

**Trigger 2 — Investigación profunda (3-4 semanas después):**
Modelo en OBSERVACIÓN con 21+ días + 5000+ votos + top 5 → alerta CEO para evaluación. CEO decide si promover a GREEN.

### E4. Consola mwt.one — Orquestador simplificado (FaberLoom + MWT)

| Sub-tab | Contenido | Fuente de verdad |
|---|---|---|
| Políticas tiered | Editor YAML del routing estático F1 (§F.1) | git (source-of-truth) |
| Data residency | Matriz tenant × classification → allowed_providers + blocked_regions | Tabla `tenant_model_allowlist` |
| Catálogo | Modelos active/shadow/deprecated + semáforo + health | Tablas `llm_models` + `llm_model_scores` |
| Circuit breakers | Estado tiempo real CB provider y modelo | Redis (estado efímero) |
| Budget | Gasto semanal vs cap (tenant + global) | `llm_usage_log` agregado |

**Fuera de scope F1** (diferido F2 junto con adaptive routing): heatmap de evidence, propuestas de routing pendientes, historia de policies (reemplazada por git history).

### E5. Seguridad

- API keys: CEO-ONLY, Fernet encryption, key en .env (LLM_ENCRYPTION_KEY)
- MultiFernet para rotación de keys de encriptación
- Keys NUNCA en: pgvector, MinIO, logs, Git, responses API, frontends
- Desencriptación: solo en memoria, solo al momento de la llamada, descartada inmediatamente
- Budget enforcement: con protección contra race conditions (SELECT FOR UPDATE)
- Break glass policy: si todos los GREEN caen, tareas clasificación/pipeline fallan cerrado. Tareas code/document usan fallback preaprobado.
- Data residency hard block: ver §E1 `tenant_model_allowlist`. CEO_ONLY nunca rutea a CN/RU por default.
- RLS obligatoria en `llm_usage_log` y `tenant_model_allowlist` (FORCE + SET app.tenant_id server-side + DISCARD ALL al checkout de pool). Ref → ENT_PLAT_SEGURIDAD.
- Ref → ENT_PLAT_SEGURIDAD para framework completo.

### E6. Timeline

Sprint 11-12 (post-consola base). AI (Antigravity/Claude Code) escribe ~90% del código. F1 FaberLoom corre en paralelo (Sprint 1-8 FaberLoom en ventana 2026-04-20 → 2026-06-14 — ref SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT).

### E7. Hallazgos auditoría incorporados

| Hallazgo | Auditor | Corrección aplicada |
|----------|---------|-------------------|
| arena_score plano (un score por modelo) | ChatGPT (mar 2026) | Tabla llm_model_scores con score por categoría |
| Router sin manejo de errores reales | ChatGPT | LiteLLM Proxy como execution layer |
| budget_used_usd con race conditions | ChatGPT | SELECT FOR UPDATE |
| usage_log insuficiente para debugging | ChatGPT | Campos: request_id, attempt_no, http_status |
| Fernet sin rotación | ChatGPT | MultiFernet |
| Sin break glass policy | ChatGPT | Fallback preaprobado documentado |
| Scraper frágil contra arena.ai | ChatGPT | Validación de datos + snapshot comparison |
| Cross-tenant evidence poisoning (tablas sin tenant_id) | Kimi A4 (abr 2026) | tenant_id obligatorio + RLS en `llm_usage_log`; tablas adaptive descartadas de F1 |
| SPOF LiteLLM proxy | Kimi A2 | HA 2 instancias + HAProxy health check 10s (§E2) |
| Data residency sin guardrails (CEO-ONLY → China) | Kimi A4 | Tabla `tenant_model_allowlist` con hard block (§E1) |
| N≥20 power 6.5% insuficiente; pesos heurísticos; decay 0.9/mes lento | Kimi A3 | Adaptive routing postpuesto F2 gated (§G); mejoras capitalizables archivadas para F2 |
| Break-even 9,524 drafts/mes >> beta 600 | Kimi A1 | Downgrade a tiered hardcoded F1 (§F) |
| Circuit breaker policy ausente | Kimi A2 | Especificación concreta provider + modelo (§F.3) |
| Cold start bootstrap gap | Kimi síntesis | Exploración manual 30 días + YAML default (§F.4) |

---

## F. FaberLoom F1 — Tiered Hardcoded Routing (canonizado 2026-04-21)

**DEC-006 canoniza:** F1 usa routing YAML estático en git, sin evidence ledger, sin weekly tuning, sin score compuesto, sin shadow testing, sin MAB.

**Justificación:** beta FaberLoom proyecta 200-600 drafts/mes. Kimi A1 calculó break-even a 9,524 drafts/mes. Sobreingeniería probada. Ver `docs/archivo/kimi_swarm_4_adaptive_routing.md`.

### F.1 YAML tiered routing (source-of-truth en repo)

```yaml
# faberloom/config/llm_tiers.yaml — v1.0 (F1)
tiers:
  simple:
    description: "Clasificación, extracción, rewrite mínimo. Baja cognición, alta frecuencia."
    primary: gemini_flash
    fallback: [gpt_4o_mini, kimi_k2]
    max_cost_per_call_usd: 0.01

  medium:
    description: "Drafts B2B, resúmenes, research synthesis simple, QualifyBot."
    primary: kimi_k2
    fallback: [deepseek_v3, gpt_4o_mini]
    max_cost_per_call_usd: 0.05

  complex:
    description: "Reducer / Critic / Synthesizer de swarms. Decisiones estratégicas. Code review."
    primary: sonnet_4_6
    fallback: [opus_4_6]
    max_cost_per_call_usd: 0.50

  local_only:
    description: "CEO-ONLY data que jamás debe salir del tenant. Sin fallback externo."
    primary: ollama_llama_3_2_3b
    fallback: []
    max_cost_per_call_usd: 0.00
```

**Cambios al YAML = commit + PR + deploy.** Cada cambio es auditable por git log (reemplaza `routing_policy_version` de adaptive spec).

### F.2 Flujo runtime por request

```
request(task_type, tenant_id, data_classification, payload)
  ↓
[1] CHECK tenant_model_allowlist(tenant_id, data_classification)
      → si provider candidato NO en allowed_providers OR region in blocked_regions
        → HARD DENY, audit log, escalate
  ↓
[2] RESOLVE tier(task_type) → {simple, medium, complex, local_only}
  ↓
[3] PICK primary model from YAML
  ↓
[4] CHECK circuit breaker (provider + model)
      → si OPEN → skip to next fallback
  ↓
[5] CALL LiteLLM proxy :4000 (primary instance)
      → on timeout/error → :4001 (backup)
      → on both down >30s → pg-boss requeue + CEO alert
  ↓
[6] LOG to llm_usage_log (tenant_id, model, tokens, cost, latency, success)
  ↓
[7] RETURN response
```

### F.3 Circuit Breakers (spec Kimi A2)

Dos niveles: **por provider** y **por modelo**. Estado efímero en Redis.

| Métrica | Cerrado → Abierto | Half-Open | Abierto → Cerrado |
|---|---|---|---|
| Error rate | ≥50% en últimos 20 req | 1 req de prueba tras 60s | <10% en 10 req |
| Latencia p99 | >15s en ventana 60s | 1 req | <5s en 5 req |
| Rate limit 429 | ≥3 consecutivos | 1 req tras 60s | 200 OK |

**Reglas:**
- CB provider abierto → bloquea todos los modelos de ese provider.
- CB modelo abierto → excluye ese modelo del tier hasta recovery.
- Si 3 modelos del mismo provider fallan → abre provider CB 60s.
- Ventana CB = 60s fija (tiempo real), no week.

### F.4 Cold start de nuevos tenants (Kimi gap fix)

- **30 días exploración manual** con YAML default.
- CEO review de samples (≥1 sample/día para primeros 30 días).
- Sin transfer learning inter-tenant (fricción legal + cross-tenant contamination risk).
- Pasados 30 días: tenant opera con mismo YAML que los existentes; si entra F2, empieza warm-up de evidence per-tenant.

### F.5 Límites F1

- No ajuste automático de rankings per-tenant.
- No A/B entre modelos dentro del mismo tier.
- No shadow testing.
- No aprendizaje vía approval feedback.
- Los tiers cambian por **decisión humana** con commit explícito.

---

## G. FaberLoom F2 — Adaptive Routing (POSTPUESTO · gated)

**DEC-008 canoniza:** adaptive routing se promueve de F2 cuando se cumple el gate.

### G.1 Gate de promoción F1 → F2

- **3 tenants × 5,000 drafts/mes sostenido × 3 meses consecutivos**.
- Volumen mínimo para N≥500 defendible (Kimi A3: power ≥50%).
- Budget humano aceptado por CEO (ops overhead ~$200/mes vs ahorro marginal).

### G.2 Mejoras Kimi capitalizables cuando F2 llegue

Archivadas aquí para no reinventar cuando llegue el momento. Ver `docs/archivo/kimi_swarm_4_adaptive_routing.md` §"Mejoras Kimi diferidas a F2" para el verbatim.

| Mejora | Reemplaza a | Autor |
|---|---|---|
| Decay semanal 0.85 (half-life 4.3 sem) | Decay mensual 0.9 (half-life 6.6 meses) | Kimi A3 |
| Concept drift detection (Page-Hinkley / ADWIN) | Decay fijo | Kimi A3 |
| MAB híbrido: Thompson top-3 + ε-greedy + batch semanal resto | Weekly batch puro | Kimi A3 |
| Pesos aprendidos vía regresión logística (approval como target) | Heurísticos 0.40/0.20/0.15/0.15/0.10 | Kimi A3 |
| Umbral N≥500 para decisión con confianza | N≥20 | Kimi A3 |
| 4-eyes workflow + firma digital para policy changes (SOC 2) | Append-only policy_version solo | Kimi A4 |
| Dataset sintético/redactado para shadow testing | Producción real | Kimi A4 |
| Evidence aislada per tenant_id (no global) | Tabla global evidence_log | Kimi A4 |

### G.3 Tablas descartadas de S1 (F1) — re-evaluar en F2

- `model_evidence_ledger` → reemplazada por git history del YAML tiered en F1.
- `routing_policy_proposal` → reemplazada por PRs en git.
- `routing_policy_version` → reemplazada por git tags.
- `workflow_step_routing` dinámico → reemplazado por YAML estático §F.1.

En F2, estas tablas **renacen con `tenant_id` obligatorio** para evitar cross-tenant poisoning (lección Kimi A4 absorbida).

### G.4 Arena Mode

**DEC-007 canoniza:** Arena Mode DESCARTADO de F1. Razón: volumen beta insuficiente para N≥20 estadístico, 2-3 sprints de build, no tensión real de modelos con tiered Sonnet reducer. Se re-evalúa como parte de F2 si el gate pasa.

---

## H. MWT vs FaberLoom — separación de concerns

| Ámbito | MWT (ENT_PLAT_LLM_ROUTING §A-E) | FaberLoom F1 (§F) |
|---|---|---|
| Fuente de ruteo | Tabla `llm_task_routing` (15 task_types) | YAML tiered (4 tiers en git) |
| Granularidad | Task-type | Tier |
| Scope | Operación Rana Walk / Marluvas / Tecmater | Multi-tenant B2B control-plane |
| Data residency | Hereda de `tenant_model_allowlist` | Consume `tenant_model_allowlist` (misma tabla) |
| HA LiteLLM | Sí (§E2) | Sí (comparte infraestructura) |
| Circuit breakers | Sí (§F.3 spec aplica a ambos) | Sí |
| Adaptive | Futuro (post F2 FaberLoom + beta MWT propia) | Futuro (§G) |

**Ambos sistemas comparten:** proxy LiteLLM HA, `tenant_model_allowlist`, `llm_usage_log` con `tenant_id`, circuit breakers, Fernet key vault.

---

## F.6 Routing modes — `routing.mode` (E4-0, 2026-07-11)

E4-0 introduce un flag tri-estado `routing.mode` que reemplaza la doble gate legacy del modo auto:

| Modo | Comportamiento |
| ---- | -------------- |
| `manual` | Humano selecciona proveedor/modelo para cada mensaje (default). |
| `shadow` | El planner corre en segundo plano, registra decisiones, produce output no visible para el usuario y no tiene side effects. |
| `natural` | Planner + ejecución automática; equivalente al antiguo modo "auto". |

La resolución sigue la cascada de configuración existente: preferencia de usuario > workspace > tenant > default. El valor explícito de `routing.mode` siempre gana.

**Backwards compatibility:** la doble gate legacy `FABERLOOM_AUTO_MODE_ENABLED` (env var) + `workspace_routing_policy.auto_mode_enabled` se mapea a `routing.mode = "natural"` cuando ambas son true. La variable de entorno está **DEPRECATED** y emite warning; las nuevas configuraciones deben usar `routing.mode` a través de la cascada de settings.

**Scope en E4:** `shadow` es solo observación (planner-level). `natural` puede ejecutar pasos internos, pero cualquier paso con efecto externo permanece draft-first y gateado por WorkLoom HITL (Regla Sagrada).

**Implementación:** `app/src/routing/policy.py` (`resolve_routing_mode`), `app/src/config_cascade.py`, `app/src/api.py` (settings registry), `app/tests/test_e4_0_mode_flag.py`.

---

Stamp: AS-BUILT v2.2 desde 2026-07-13 — consolidado en `main` post-E4.

Changelog:
- v1.0 (2026-03-18): Creación inicial. Rankings arena.ai verificados 18 mar 2026. Pricing verificado contra docs oficiales. PLT-11 arquitectura con correcciones auditoría ChatGPT (8.2/10).
- v2.0 (2026-04-21): Canoniza veredicto Kimi Swarm #4 (LOW confidence adaptive routing F1). Downgrade a tiered hardcoded F1 en YAML git (§F). Adaptive postpuesto F2 gated a 5K×3 meses (§G). +Tabla `tenant_model_allowlist` (data residency hard block). +HA LiteLLM 2 instancias (§E2). +tenant_id obligatorio en `llm_usage_log` + RLS. +Circuit breakers spec (§F.3). Cold start 30 días manual (§F.4). Arena Mode descartado F1 (DEC-007). Mejoras Kimi F2 archivadas (§G.2). Separación MWT vs FaberLoom (§H). Refs: docs/archivo/kimi_swarm_4_adaptive_routing.md, ENT_GOB_DECISIONES DEC-006/007/008, ENT_PLAT_MEMORY_STACK, SPEC_FABERLOOM_ARCHITECTURE, SPEC_FABERLOOM_WORKFLOW_ENGINE.
- v2.0.1 (2026-06-23, FB-STD-CODEX-2026-06-23-01): fix mecánico de ref colgante `archivo/kimi_swarm_4_adaptive_routing.md` → `docs/archivo/kimi_swarm_4_adaptive_routing.md`.
- v2.1 (2026-06-24): +Fugu Standard como provider externo en tenant_model_allowlist (FG-02 sesion Fugu). Matriz N0/N1/N2/N3/N4 documentada.
- v2.2 (2026-07-13): Integración formal del apéndice E4-0 como §F.6; documenta `routing.mode` manual/shadow/natural y deprecación de `FABERLOOM_AUTO_MODE_ENABLED`. Estado pasa a AS-BUILT tras cierre técnico de E4.
