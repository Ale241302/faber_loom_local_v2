# ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO — Outline

## Executive Summary
### Contexto y Alcance
#### Faberloom evalúa 4 gaps arquitectónicos identificados en Ruflo (ex Claude Flow) para decidir qué incorporar, descartar o diferir en su roadmap de 12 meses

### Resumen de Decisiones
#### Cuadro decisión final: IMPLEMENTAR (2 gaps), DIFERIR (2 gaps), DESCARTAR (0 gaps)

## 1. GAP 1 — Tier 0 sub-LLM: ¿Vale la pena un layer pre-LLM? (~2500 words, 2 tables, 1 decision matrix)
### 1.1 Hallazgo
#### 1.1.1 Regex/AST puro en Python es ~20,000-220,000× más rápido que Haiku y $0 por request
#### 1.1.2 60-80% de documentos de cobranza LATAM y 75-90% de proformas son parseables sin LLM gracias a e-invoicing estructurado
#### 1.1.3 El riesgo real no es precisión sino fallo silencioso: regex sin Pydantic validation es peor que LLM honesto que dice "no estoy seguro"
### 1.2 Datos y Evidencia
#### 1.2.1 Benchmark BI-RADS: regex 18,404× más rápido (1.45s vs 26,686s) con accuracy comparable (89.2% vs 87.7%)
#### 1.2.2 Costo Haiku para tasks simples: $0.00012-0.00038/request; a 500 req/día = $9-35/mes (5-17% de budget)
#### 1.2.3 Tabla comparativa: regex stdlib vs Haiku vs pyparsing vs Lark (latencia, costo, mantenibilidad, madurez)
### 1.3 Confidence Level
#### 1.3.1 HIGH: Múltiples fuentes independientes (ACM TOPLAS, BI-RADS, Arthur.ai, Datadog, autoridades fiscales LATAM)
### 1.4 Implicación de Diseño
#### 1.4.1 Implementar "Deterministic Pre-filter" como Tier 0 antes del L1 Haiku; stdlib `re` + Pydantic validation + LiteLLM pre-call hooks
#### 1.4.2 14 reglas concretas para MVP cobranza: parsers XML por país (DIAN, SII, SAT, AFIP, SEFAZ), validación TIN, extracción email
### 1.5 Decisión Recomendada
#### 1.5.1 ✅ IMPLEMENTAR en MVP (día 1-3 de desarrollo, ~3 días de esfuerzo, reduce costos 40-95%)

## 2. GAP 2 — Routing Aprendido por Evidencia (~2500 words, 2 tables, 1 algorithm comparison)
### 2.1 Hallazgo
#### 2.1.1 Routing por bandit algorithms (Thompson Sampling, LinUCB, ε-greedy) supera routing estático en costo-eficiencia, pero requiere ~5,000 requests/brazo para convergencia confiable
#### 2.1.2 Cold start es el deal-breaker para MVP: Faberloom procesará ~100-300 req/día, un bandit puro tardaría semanas en estabilizar
#### 2.1.3 Ningún router comercial (RouteLLM, Martian, NotDiamond, OpenPipe) ofrece multi-tenancy nativa con aislamiento por organización
### 2.2 Datos y Evidencia
#### 2.2.1 GreenServ (16 LLMs): +22% accuracy, -31% energy, routing overhead <8ms; pero necesitó ~100 queries para estabilizar
#### 2.2.2 RouteLLM reproducibilidad cuestionable: 47% accuracy en RouterArena (ICLR 2026), peor que baseline heurístico
#### 2.2.3 Router propio L1 Haiku + L2 dispatcher: overhead 2-8ms, multi-tenant vía LiteLLM Organizations, control total de datos
### 2.3 Confidence Level
#### 2.3.1 HIGH para implementación actual; MEDIUM para bandit adaptive (datos de convergencia varían por workload)
### 2.4 Implicación de Diseño
#### 2.4.1 Mantener L1/L2 rule-based en MVP; diseñar ModelFingerprint como feature de routing (no solo seguridad) para Phase 2
#### 2.4.2 Epsilon-greedy decay (ε=0.3→0.05) como algoritmo de transición cuando se alcancen >3000 req/día
#### 2.4.3 Granularidad global por task_type (NO per-org); RLS per-org se mantiene para seguridad
### 2.5 Decisión Recomendada
#### 2.5.1 ⏳ DIFERIR a Phase 2 (>3000 req/día); IMPLEMENTAR schema de OutcomeLedger y feedback loop como preparación

## 3. GAP 3 — Spawning Controlado de Sub-Skills bajo Gate Humano (~2500 words, 2 tables, 1 UX analysis)
### 3.1 Hallazgo
#### 3.1.1 Skill-to-skill delegation punto-a-punto es técnicamente viable en Pydantic AI ("agent como tool"), pero la evidencia académica y de producción favorece single-agent para workloads <5 tools
#### 3.1.2 MAST (UC Berkeley, NeurIPS 2025): 41-86.7% tasa de fallo en multi-agente; single-agent supera multi-agent en razonamiento multi-hop bajo igual presupuesto de tokens
#### 3.1.3 CONTRADICCIÓN CON BRIEF ORIGINAL: El dato "87% hallucination cascade en 4h" NO es verificable; "4h" es extrapolación, no dato empírico
### 3.2 Datos y Evidencia
#### 3.2.1 Pydantic AI soporta delegación nativa vía `@agent.tool` con `await delegate_agent.run()`; pydantic-graph funcional pero overkill para 2-3 pasos
#### 3.2.2 Human approval nativa: `requires_approval=True` y `ApprovalRequired()`; pero WhatsApp Business API limita a 3 botones/20 chars/sesión 24h
#### 3.2.3 10 handoffs al 99% cada uno = 90.4% confiabilidad total; costo multi-agente 2-5× tokens vs single-agent
### 3.3 Confidence Level
#### 3.3.1 HIGH: Papers NeurIPS 2025, documentación Pydantic AI, datos MAST verificables, Meta WhatsApp API docs
### 3.4 Implicación de Diseño
#### 3.4.1 Mantener single-agent + L1/L2 routing en MVP; diseñar approval gates por tool (no por cadena) usando Pydantic AI nativo
#### 3.4.2 UX dual: aprobación granular en web console, notificaciones binarias en WhatsApp con links a consola
### 3.5 Decisión Recomendada
#### 3.5.1 ⏳ DIFERIR a Fase 6 (condición: >3 tools con dependencias complejas o requerimiento de paralelismo); NO envolver en LangGraph para MVP

## 4. GAP 4 — pgvector + RLS a Escala: ¿Aguanta 100+ Tenants? (~2500 words, 3 tables, 1 cost projection)
### 4.1 Hallazgo
#### 4.1.1 El tipping point de pgvector + RLS es ECONÓMICO no técnico: performance p50 ~5ms con 20% overhead RLS es aceptable hasta >1M vectores, pero Supabase supera $200/mes a ~450K vectores
#### 4.1.2 Alternativas (Qdrant, Weaviate, pgvectorscale) son superiores técnicamente pero ninguna justifica migración en MVP dado presupuesto y timeline
#### 4.1.3 Mem0 NO es reemplazo de vector DB; es capa de memoria sobre store externo
### 4.2 Datos y Evidencia
#### 4.2.1 RLS overhead: Simple Select +0.1ms, JOIN +0.1ms, Vector Search (HNSW) ~20% (3-5ms→5-6ms), GROUP BY x2.4
#### 4.2.2 Supabase cost tiers: Free (32MB maintenance_work_mem, >20K vectores fallan), Pro $25, Large $110, XL $210, 2XL $410; punto de ruptura ~450K vectores
#### 4.2.3 Alternativas costo 1M vectores/100 tenants: Qdrant Cloud $25-75, Weaviate $45-100, Turbopuffer $64+, Mem0 $99-299
### 4.3 Confidence Level
#### 4.3.1 HIGH para benchmarks técnicos; MEDIUM para proyección de costos (depende de crecimiento real de tenants)
### 4.4 Implicación de Diseño
#### 4.4.1 IMPLEMENTAR pgvector en Supabase para MVP: HNSW default + halfvec quantization + RLS safety net + composite indexes (tenant_id, ...)
#### 4.4.2 Habilitar `hnsw.iterative_scan = relaxed_order` (requiere pgvector 0.8.0+ en Supabase)
#### 4.4.3 DISEÑAR schema con tenant_id column como safety adicional además de RLS
### 4.5 Decisión Recomendada
#### 4.5.1 ✅ IMPLEMENTAR (stay con pgvector) para MVP; DIFERIR evaluación de alternativas a >500K vectores o 6 meses

## 5. Insights Transversales (~2000 words, 1 synthesis table)
### 5.1 Patrón Arquitectónico Universal
#### 5.1.1 Los 4 gaps convergen en un mismo patrón: "Deterministic First → LLM Fallback → Human Gate" — empezar simple, escalar inteligente
### 5.2 LiteLLM como Hilo Conector
#### 5.2.1 LiteLLM conecta 3 gaps: pre-call hooks (Tier 0), Organizations/Teams/Keys (multi-tenant routing), embeddings abstraction (vector DB migration)
### 5.3 E-invoicing LATAM como Ventaja Competitiva
#### 5.3.1 >90% de PYMEs LATAM usan XML estructurado por mandato fiscal: parsers por país son core competency, no afterthought
### 5.4 UX Dual Web/WhatsApp
#### 5.4.1 WhatsApp Business API es cuello de botella para todo multi-step: web console para aprobación granular, WhatsApp para notificaciones binarias

## 6. Matriz de Decisiones y Roadmap (~1000 words, 1 decision matrix table)
### 6.1 Cuadro Resumen
#### 6.1.1 Tabla final: GAP × Decisión × Fase × Esfuerzo × Impacto
### 6.2 Próximos Pasos Inmediatos
#### 6.2.1 Acciones para semana 1-2 post-research: implementar Tier 0, correr benchmark pgvector, documentar ModelFingerprint API interna

# References
## faberloom.agent.outline.md
- **Type**: Report outline
- **Description**: This outline file
- **Path**: /mnt/agents/output/ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO.agent.outline.md

## Research Artifacts
- **Type**: Deep research outputs
- **Description**: 12 dimension files + cross-verification + insights
- **Path**: /mnt/agents/output/research/faberloom_dim01.md through dim12.md, faberloom_cross_verification.md, faberloom_insight.md
