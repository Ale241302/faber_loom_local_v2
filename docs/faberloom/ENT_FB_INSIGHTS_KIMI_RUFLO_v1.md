# ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO — Insights Kimi #3 (Ruflo / 4 gaps arquitectónicos)
id: ENT_FB_INSIGHTS_KIMI_RUFLO_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: ENT
stamp: VIGENTE — 2026-04-27
aprobador: CEO
fuente: Investigación Kimi Swarm — 12 dimensiones, 142 footnotes únicas, 436 refs inline, anti-alucinación cross-verificada
aplica_a: [FaberLoom]
relacionado: ENT_FABERLOOM_INSIGHTS_KIMI.md (Kimi #1) · ENT_FABERLOOM_INSIGHTS_KIMI_EMAIL.md (Kimi #2) · SPEC_FABERLOOM_MVP.md · SPEC_AUTONOMY_CONTROL_ENGINE.md · SPEC_LLM_ROUTING_ARCHITECTURE.md · ARCH_AGENT_PRINCIPLES.md (P14)
anexo: docs/anexos/kimi_ruflo/ (12 dim raw + cross_verification + insight)

---

## Declaración

Investigación Kimi #3 sobre 4 gaps arquitectónicos identificados al comparar Ruflo (ex Claude Flow, ~27k stars) contra la arquitectura FaberLoom. Brief original solicitó decisión sobre adoptar/diferir/descartar cada gap. Kimi expandió a 12 dimensiones (3 por gap), aplicó cross-verification interna, identificó 1 conflict zone y produjo 9 insights transversales.

**Veredicto:** 2 IMPLEMENTAR + 2 DIFERIR + 0 DESCARTAR. Una contradicción CZ-001 desmonta dato del brief original ("87% en 4h" no verificable). Patrón "Deterministic First → LLM Fallback → Human Gate" emerge como invariante arquitectónico → consagrado como P14 en ARCH_AGENT_PRINCIPLES.

Confidence: 85% HIGH, 10% MEDIUM, 1 conflict zone resuelta. La decisión de mantener single-agent en MVP sigue siendo correcta; la justificación se actualiza a evidencia verificable (MAST NeurIPS 2025).

---

## Matriz de decisión

| GAP | Dim | Decisión | Fase | Esfuerzo | Trigger |
|---|---|---|---|---|---|
| 1 — Tier 0 sub-LLM | 01,02,03 | ✅ IMPLEMENTAR | MVP día 1-3 | ~3 días | Siempre activo |
| 2 — Routing aprendido | 04,05,06 | ⏳ DIFERIR | Phase 2 | 2-3 días prep MVP | >3,000 req/día × 14 días |
| 3 — Spawning controlado | 07,08,09 | ⏳ DIFERIR | Fase 6 | 1-2 días approval gates | >3 tools con dependencias |
| 4 — pgvector + RLS | 10,11,12 | ✅ IMPLEMENTAR (stay) | MVP | ~2 días tuning | Siempre activo |

Costo MVP proyectado: $135-160/mes (Supabase Pro + Large + LiteLLM en infra existente).
Tipping point económico: ~450K vectores en Supabase Pro = $200/mes — ahí se decide upgrade XL ($235) o migración Qdrant Cloud ($30-60).

---

## I-RUFLO-01 — Tier 0 sub-LLM: regex pre-LLM es 20,000-220,000× más rápido

**Confidence:** High

Implementar pre-filtro determinístico antes del L1 Haiku reduce costos 40-95% y latencia de ~1,100ms a <100μs para el 60-80% de tasks simples. El stack recomendado es `stdlib re` + Pydantic validation + LiteLLM pre-call hooks. No requiere librería externa.

**Datos:** Regex Python compilado ~5-50μs vs Haiku ~750-1,100ms (TTFT + RTT desde LATAM). Benchmark BI-RADS: regex 18,404× más rápido (1.45s vs 26,686s) con accuracy comparable (89.2% vs 87.7%). Costo Haiku tasks simples: $0.00012-0.00038/req → $9-35/mes a 500 req/día. RouteLLM 47% accuracy en RouterArena ICLR 2026 — descarta routers comerciales como solución.

**Implicación de diseño:** Tier 0 se inserta antes del L1 existente sin re-arquitecturar. 14 reglas concretas para MVP cobranza identificadas (parsers XML por país, validación TIN, extracción email). Riesgo de fallo silencioso del regex se mitiga con Pydantic validation obligatoria + fallback a Haiku cuando `confidence < threshold`.

**Mantenimiento:** parsers XML LATAM requieren ~1 día/trimestre por cambios fiscales (DIAN, SII, SAT, AFIP, SEFAZ publican schemas con frecuencia variable). No es costo cero post-implementación.

---

## I-RUFLO-02 — E-invoicing LATAM como ventaja estructural ignorada

**Confidence:** High

>90% de PYMEs LATAM usan e-invoicing estructurado por mandato fiscal. UBL 2.1 en Colombia, DTE en Chile (97% desde 2019), CFDI 4.0 en México, NFe en Brasil, AFIP en Argentina. Faberloom no debe usar LLM para parsear facturas — debe construir parsers XML por país como core competency.

**Datos:** Colombia (DIAN), Chile (SII), México (SAT), Brasil (SEFAZ), Argentina (AFIP) tienen schemas XML publicados y obligatorios. Cada parser XML requiere 20-40 líneas de `xml.etree.ElementTree` con XPath conocido.

**Implicación de diseño:** Diferenciador competitivo vs SaaS extranjeros (EE.UU./Europa) que usan OCR + LLM para PDFs no estructurados. Latencia sub-milisegundo, costo $0, accuracy 100% cuando XML válido. La ventaja no es técnica — es estructural por mandato regulatorio LATAM.

---

## I-RUFLO-03 — LiteLLM como hilo invisible que conecta 3 de los 4 gaps

**Confidence:** Medium-High

LiteLLM no es solo un proxy de modelos — es capa de orquestación multi-propósito. Habilita Tier 0 (pre-call hooks), multi-tenant routing (Organizations/Teams/Keys), y abstracción de embeddings (migración pgvector → Qdrant sin cambiar código de embeddings).

**Datos:** Pre-call hooks ejecutan regex/AST antes del LLM call. Organizations/Teams/Keys exponen aislamiento por tenant sin reimplementar. Embeddings endpoint expone `POST /embeddings` con interfaz estable independiente del provider.

**Implicación de diseño:** Documentar explícitamente que LiteLLM es infraestructura compartida, no overhead. Justifica configuración detallada de Organizations/Teams/Keys desde MVP. Capa `VectorStore` (50-200 LOC) limita superficie de migración futura — el cambio de vector DB afecta solo el store, no embeddings ni routing.

---

## I-RUFLO-04 — pgvector tipping point es económico, no técnico

**Confidence:** High

pgvector + RLS aguanta hasta 1M vectores con latencia p50 ~5ms y overhead RLS HNSW ~20% (3-5ms → 5-6ms). El límite no es performance — es costo Supabase: ~450K vectores fuerzan 2XL ($410/mes), excediendo presupuesto MVP en 105%.

**Datos:** RLS overhead — Simple Select +0.1ms, Vector Search HNSW +20%, GROUP BY x2.4. Supabase tiers — Free ($0, 32MB maintenance_work_mem cap, ~20K vectores antes de fallar índices), Pro $25, Large $110, XL $210, 2XL $410. Punto de ruptura $200/mes ≈ 450K vectores con halfvec quantization. Alternativas a 1M vectores/100 tenants: Qdrant Cloud $25-75, Weaviate $45-100, Mem0 $99-299 (NO es vector DB, es capa sobre store externo).

**Implicación de diseño:** Configuración defensiva pgvector — HNSW default + halfvec quantization + RLS safety net + composite indexes con `tenant_id` como leading column. Habilitar `hnsw.iterative_scan = relaxed_order` (pgvector 0.8.0+). Capa abstracción `VectorStore` desde día 1 para limitar lock-in. Benchmark mínimo: ANN-Benchmarks dbpedia-openai-1000k-angular, targets p95<100ms, QPS>10, recall@10>0.90.

---

## I-RUFLO-05 — ModelFingerprint reframing: feature de routing, no solo gate de seguridad

**Confidence:** High

El brief original posiciona ModelFingerprint como gate de probation al cambiar modelo (P13). Investigación revela que el patrón estándar producción (Scope, DFPE, Behavioral Fingerprint) lo usa principalmente como **feature de routing inteligente**. Un mismo objeto sirve dos propósitos: seguridad (existente) + routing (futuro).

**Datos:** ModelFingerprint = vector embedding 384-dim de comportamiento ante queries ancla (DFPE ACL 2026). Cosine similarity >0.8 entre modelos → transferir histórico con descuento 0.5. <0.2 → cold start. Scope (arXiv 2601.22323): 250 anchors estratégicos predicen correctness/costo de modelos nunca vistos sin retraining.

**Implicación de diseño:** Exponer `GET /model/similarity` desde día 1. Hoy consume sistema de probation; mañana consume sistema de routing Phase 2. Evita duplicación de infraestructura cuando llegue el bandit adaptive. Documentar explícitamente que ModelFingerprint evolucionará de mecanismo de seguridad a feature de contexto del futuro router.

---

## I-RUFLO-06 — Routing aprendido: cold start es el deal-breaker para MVP

**Confidence:** High (implementación actual) · Medium (bandit adaptive)

Bandit algorithms (Thompson Sampling, LinUCB, ε-greedy) superan routing estático en costo-eficiencia, pero requieren ~5,000 pulls/brazo para convergencia confiable. Faberloom procesará ~100-300 req/día en MVP — un bandit puro tardaría ~90 días en estabilizar. Ningún router comercial (RouteLLM, Martian, NotDiamond, OpenPipe) ofrece multi-tenancy nativa con aislamiento por org.

**Datos:** GreenServ (16 LLMs): +22% accuracy, -31% energy, overhead <8ms; necesitó ~100 queries para estabilizar. Router propio L1+L2: overhead 2-8ms, multi-tenant vía LiteLLM Organizations, control total. Granularidad óptima: global por `task_type`, NO per-org (sparse). Epsilon-greedy decay (ε=0.3→0.05) más simple para MVP que Thompson.

**Implicación de diseño:** Mantener L1/L2 rule-based en MVP. Diseñar OutcomeLedger desde día 1 con schema completo `(request_id, task_type, model_used, prompt_hash, response_hash, latency_ms, cost_usd, user_feedback, llm_judge_score, timestamp, org_id)` con RLS por `org_id`. No activa bandit todavía — acumula data para calentar priors bayesianos cuando volumen justifique transición.

---

## I-RUFLO-07 — Multi-agente en MVP: argumento del brief original debe actualizarse

**Confidence:** High · CZ-001 resuelta

**CONFLICT ZONE CZ-001:** Brief original cita "87% hallucination cascade en 4h" como justificación contra multi-agente. Investigación exhaustiva no localizó paper que reporte esa métrica con ventana temporal. El 86.7% existe (MAST UC Berkeley NeurIPS 2025, 1,642 trazas, 14 modos de fallo, Cohen's Kappa=0.88) **sin temporalidad asociada**. La "4h" proviene de extrapolación de modelos de costo de Cycles (runcycles.io) — autor declara "todas las cifras son ilustrativas, no datos de producción medidos".

**Resolución:** Decisión NO multi-agente en MVP sigue siendo correcta, pero argumentación debe sustituirse por evidencia verificable.

**Argumentación actualizada (3 pilares):**
1. MAST: 41-86.7% tasa de fallo en multi-agente sobre 1,642 trazas (NeurIPS 2025 Spotlight).
2. Single-agent iguala multi-agent en razonamiento multi-hop bajo igual presupuesto de tokens (paper NeurIPS 2025, argumento information-theoretic vía Data Processing Inequality).
3. Confiabilidad compuesta degrada exponencialmente: 10 handoffs al 99% = 90.4%; 20 handoffs al 95% = 35.8%. Costo multi-agente 2-5× tokens.

**Implicación de diseño:** Mantener single-agent + L1/L2 routing en MVP. Diseñar approval gates por tool (no por cadena) usando Pydantic AI nativo (`requires_approval=True`, `ApprovalRequired`). Diferir skill-to-skill delegation a Fase 6. Activación condicional: >3 tools con dependencias complejas O paralelismo justificable. Frameworks descartados explícitamente: OpenAI Swarm (deprecado mar-2025), CrewAI (handoffs implícitos sin control de fingerprint), AutoGen Group Chat (mesh con propagación rápida de errores).

---

## I-RUFLO-08 — UX dual obligatoria: WhatsApp es cuello de botella para multi-step

**Confidence:** High

WhatsApp Business API limita severamente cualquier interacción multi-step: máximo 3 quick reply buttons, 20-25 caracteres por label, sesión de 24h desde último mensaje del usuario. Fuera de sesión, solo template messages pre-aprobados por Meta (latencia aprobación 15min-24h). No tiene workaround técnico — es regla de plataforma.

**Datos:** Pydantic AI implementa HITL nativo por tool — `DeferredToolRequests` / `DeferredToolResults` con preservación automática de `message_history`. Granularidad por tool call, no por workflow. Aprobación condicional vía `ApprovalRequired` desde dentro de la tool.

**Implicación de diseño:** Asimetría de canal por diseño, no degradación. Web console (Next.js) = canal primario para aprobación granular y multi-step. WhatsApp = canal primario para notificaciones binarias de bajo riesgo + deep-links a consola para decisiones complejas. Cualquier workflow que requiera más de 1 decisión consecutiva o más de 20 caracteres de explicación → web console. Si sesión 24h expira → template message con un único CTA "🔗 Revisar pendientes en consola".

Esta restricción es universal — aplica a Tier 0 fallback, HITL de cobranza, validación de proformas, y cualquier feature multi-step futura.

---

## I-RUFLO-09 — Granularidad per-org es anti-patrón en aprendizaje (correcta en seguridad)

**Confidence:** High

Tensión arquitectónica: seguridad y aislamiento requieren per-org (RLS, AgentMemory contenida — P13); aprendizaje de routing requiere agregación (datos por tenant son sparse). La solución no es elegir uno — es separar dos sistemas que coexisten:

1. **RLS per-org:** seguridad y compliance (siempre per-org).
2. **Routing global por task_type:** optimización (NO per-org, NO incluye `org_id` como feature directa del bandit).

**Datos:** GreenServ ablation: `task_type` es la feature más informativa para routing. `org_id` como feature directa fragmenta datos y degrada convergencia. RLS sin `org_id` sería inseguro. Los dos sistemas son ortogonales.

**Implicación de diseño:** Documentar explícitamente la separación para evitar que un developer futuro "optimice" agregando `org_id` al router. Features de routing Phase 2: `task_type` + `query_embedding` + `complexity_score` + `ModelFingerprint_similarity`. NO incluir `org_id`. RLS sigue siendo capa de seguridad independiente. ARCH_AGENT_PRINCIPLES P13 (Contención) y P14 (Deterministic First) se complementan, no compiten.

---

## Patrón transversal: P14 candidato

**"Deterministic First → LLM Fallback → Human Gate"**

3 de los 4 gaps convergen en el mismo patrón:
- GAP 1: regex Tier 0 → Haiku → operador humano
- GAP 2: rule-based L1/L2 → bandit adaptive (Phase 2) → revisión CEO
- GAP 3: single-agent → multi-agent (Fase 6) → gate por tool

Este patrón no es restricción de presupuesto MVP — es estrategia de producción robusta. Sistemas que saltan directamente a la capa inteligente (LLM puro, bandit puro, swarm puro) tienen tasas de fallo 2-5× mayores. Ruflo mismo lo usa (WASM pre-filter → tier routing → Claude full).

**Acción:** consagrado como Principio 14 en ARCH_AGENT_PRINCIPLES v1.3 (ver patch).

---

## Plan B — Mitigación riesgo Anthropic deprecando Haiku 3.5 durante MVP

Haiku 4.5 ya existe (oct 2025). Si Anthropic deprecia 3.5 durante los 60 días de MVP:

| Métrica | Haiku 3.5 | Haiku 4.5 | Impacto |
|---|---|---|---|
| TTFT | 480-610ms | ~597ms (p95: 612-843ms) | +5-15% latencia |
| Costo input/output | baseline | similar | neutro |
| Migración | — | Cambio de model_id en LiteLLM config | <1 hora |

ModelFingerprint (P13) gestiona la transición — probation automática + revalidación por bucket. Riesgo controlado.

---

## Próximos pasos inmediatos (semana 1-2 post-research)

| Acción | Esfuerzo | Bloqueador potencial |
|---|---|---|
| Tier 0 Deterministic Pre-filter (`tier0.py` + LiteLLM hooks + 14 reglas) | 2-3 días | Acceso a muestras XML reales por país |
| Documentar API interna `GET /model/similarity` | 0.5 días | — |
| Schema `outcome_ledger` en Supabase con RLS por org_id | 1-1.5 días | — |
| Configuración pgvector defensiva (HNSW + halfvec + composite indexes + iterative_scan) | 1.5-2 días | Validar pgvector ≥0.8.0 en Supabase actual |
| Approval gates por tool en Pydantic AI + UX dual web/WhatsApp | 1-2 días | Diseño UI consola |

Suma: ~6-8 días de un developer. Distribuible en paralelo con 2 devs. Compatible con MVP 60 días.

**Regla de priorización:** cualquier item de backlog que no reduzca costo, latencia o riesgo de fallo en las primeras 4 semanas se mueve a Phase 2.

---

## Limitaciones conocidas de este Kimi

| Limitación | Mitigación aplicada |
|---|---|
| `agent.final.md` original (673 líneas) sin sección References consolidada — 142 footnotes únicas viven solo en archivos `dim01-12` | Anexo `docs/anexos/kimi_ruflo/` consultable manualmente |
| Fechas anómalas en headers de algunos dim ("Junio 2026" cuando estamos abr-2026) | Probable scaffolding del runtime Kimi — no afecta validez de claims |
| Mantenimiento parsers XML LATAM no estaba en research original | Agregado en I-RUFLO-01 (~1 día/trimestre) |
| 60-80% docs LATAM parseables sin LLM no validado contra muestra real Marluvas/Tecmater | Spot-check pendiente con 20 docs reales antes de comprometer 14 parsers en sprint 1 |

---

## Anexo

`docs/anexos/kimi_ruflo/` contiene:
- `faberloom_dim01.md` ... `faberloom_dim12.md` — research raw por dimensión (~30K tokens cada)
- `faberloom_cross_verification.md` — método anti-alucinación, conflict zones identificadas
- `faberloom_insight.md` — 9 insights consolidados pre-síntesis

No indexable a pgvector. Consultable manualmente para auditoría de fuentes o profundización técnica.

---

Changelog:
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Renombrado desde docs/ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO.md a docs/faberloom/ENT_FB_INSIGHTS_KIMI_RUFLO_v1.md. id y domain actualizados. v1.0 se mantiene.
- v1.0 (2026-04-27): Creación. Kimi #3 (Ruflo / 4 gaps). Trigger: brief CEO 2026-04-27, ejecución Kimi swarm 2026-04-26, revisión Cowork 2026-04-27, indexa CEO 2026-04-27.
