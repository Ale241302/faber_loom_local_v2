# Dimensión 03 — GAP 1: Stacks Producción y Mantenibilidad Pre-LLM

**Research Brief:** Faberloom × Ruflo: 4 Gaps Arquitectónicos  
**Dimension:** Pre-LLM Validation Stacks — Production Readiness & Maintainability  
**Date:** 2025-07-24  
**Searches Conducted:** 34 independent queries across academic papers, official docs, GitHub, engineering blogs, and primary sources.

---

## Executive Summary

The pre-LLM validation layer (deterministic checks before sending to the LLM) is a **well-documented production pattern** with real adoption across enterprise AI deployments. The consensus architecture is a **three-layer defense**: (1) sub-10ms rule-based validators (regex, schema, keyword), (2) 50-200ms ML classifiers for nuanced patterns, and (3) 300ms+ LLM semantic validation for high-stakes outputs[^58^][^248^].

For Faberloom's MVP context (FastAPI + Pydantic AI + LiteLLM + 60-day timeline + ~$200/mo budget + 1-3 devs), the research yields a **clear recommendation**: use **Python stdlib `re` with `re.compile()`** for deterministic pre-LLM validation (PII scrubbing, keyword blocklists, format checks), **do NOT adopt GuardrailsAI** for MVP (lock-in risk, RAIL learning curve, heavier than needed), and **do NOT add Instructor** (redundant with PydanticAI's built-in `output_type` + validation retries). Descartar frameworks <6 meses sin casos reales (flpc/fastre, pydantic-ai-guardrails third-party). Diferir Outlines/Guidance para post-MVP cuando se tenga infra local de modelos.

---

## 1. ¿Quién en producción usa un patrón "pre-LLM" (regex/AST antes de enviar al LLM)?

### 1.1 Casos documentados en producción

**Arthur.ai — Aerolínea mayor (cliente no nombrado)**  
Claim: "A major airline we work with uses pre-LLM guardrails to redact PII from customer support conversations before they ever leave the corporate environment." El pre-LLM guardrail "was non-negotiable from a compliance standpoint. Every conversation passes through PII detection before anything is sent to the model."[^201^]
Source: Arthur.ai Blog — Best Practices for Building Agents | Part 5 - Guardrails  
URL: https://www.arthur.ai/blog/best-practices-for-building-agents-guardrails  
Date: 2026-04-06  
Excerpt: "A major airline we work with uses pre-LLM guardrails to redact PII from customer support conversations before they ever leave the corporate environment... Every conversation passes through PII detection before anything is sent to the model."  
Context: Enterprise customer support agent with compliance requirements  
Confidence: high

**NeuralStack — Input Screening en API gateway**  
Claim: "A two-stage pipeline – fast regex pre-filter, then LLM classifier for borderline cases – balances cost and coverage." La arquitectura documentada incluye 7 capas, siendo la #2 "Input Screen" con "Regex + LLM classifier for injection."[^63^]
Source: NeuralStack — Secure-by-Design Patterns for LLM-Backend APIs  
URL: https://neuralstackms.tech/secure-by-design-patterns-for-llm-backend-apis  
Date: 2026-04-09  
Excerpt: "A two-stage pipeline – fast regex pre-filter, then LLM classifier for borderline cases – balances cost and coverage."  
Context: Enterprise LLM API security architecture  
Confidence: high

**Datadog — Output regex scrubbing**  
Claim: "An output security guardrail can apply regex scrubbing to redact leaked secrets (e.g., API keys) before returning responses to the client."[^64^]
Source: Datadog Blog — LLM guardrails: Best practices for deploying LLM apps securely  
URL: https://www.datadoghq.com/blog/llm-guardrails-best-practices/  
Date: 2025-10-22  
Excerpt: "an output security guardrail can apply regex scrubbing to redact leaked secrets (e.g., API keys) before returning responses to the client."  
Context: Production LLM security best practices  
Confidence: high

**Authority Partners — Tres capas de defensa con latencias documentadas**  
Claim: "Layer 1: Rule-Based Validators (Sub-10ms Latency)" — incluye "Input validation: Format checking, allowed character sets, length limits" y "PII detection: Regex patterns and dictionary matching."[^248^]
Source: Authority Partners — AI Agent Guardrails: Production Guide for 2026  
URL: https://authoritypartners.com/insights/ai-agent-guardrails-production-guide-for-2026/  
Date: 2025-11-18  
Excerpt: "Rule-based validators operate in microseconds. They're perfect precision for defined patterns. If you can write an explicit rule for it, this layer catches it faster than anything else."  
Context: Production guide for 2026 with latency benchmarks  
Confidence: high

**Checkstep — 10,000x faster profile validation**  
Claim: "Checkstep case study: 90% automated moderation achieved 2.3x subscription increase and 10,000x faster profile validation" con content moderation que usa reglas + ML combinado.[^35^]
Source: Introl Blog — Deploying AI guardrails at production scale  
URL: https://introl.com/blog/ai-safety-infrastructure-guardrails-production-scale-2025  
Date: 2026-02-05 (December 2025 Update)  
Excerpt: "Checkstep case study: 90% automated moderation achieved 2.3x subscription increase and 10,000x faster profile validation"  
Context: AI content moderation at scale  
Confidence: medium

### 1.2 Patrón arquitectónico consensuado

Claim: La arquitectura de validación pre-LLM en producción sigue un patrón de **defensa en profundidad** con al menos dos capas determinísticas antes del LLM. Vellum AI documenta "unit test bank" con validación sintáctica previa al despliegue[^56^]; VentureBeat documenta "Layer 1: Deterministic assertions" como "the pipeline's first gate, using traditional code and regex to validate structural integrity" con principio "fail-fast"[^58^]; y n8n documenta "Deterministic Steps & AI Steps" donde los pasos determinísticos (regex, schema validation) corren antes de los pasos AI[^191^].
Source: Multiple (Vellum AI, VentureBeat, n8n)  
Confidence: high

---

## 2. GuardrailsAI: ¿Está maduro? ¿Hay casos de producción? ¿Mantenibilidad real?

### 2.1 Estado del proyecto

**GitHub & Adoption**  
Claim: ~5.9k GitHub stars, "over 10,000 monthly downloads" (PyPI core), y "across all validators we average around 70K installs a week over the past year" (Hub validators). Fundado por Shreya Rajpal (ex-Apple, Drive.ai) y Diego Oppenheimer (Algorithmia founder). $7.5M seed funding (Feb 2024).[^217^][^212^]
Source: WorkOS Blog / GitHub Discussion #1399  
URL: https://workos.com/blog/guardrails-ai-vs-workos-safety-validation-enterprise-authentication / https://github.com/guardrails-ai/guardrails/discussions/1399  
Date: 2025-11-04 / 2026-02-08  
Excerpt: "From our PyPI registry's stats, we can see that across all validators we average around 70K installs a week over the past year."  
Context: Direct from maintainer answering maintenance questions  
Confidence: high

**Cliente documentado: Robinhood**  
Claim: "Notable customers include Robinhood, which uses Guardrails AI to ensure reliable AI behavior in financial applications where accuracy is paramount."[^217^]
Source: WorkOS Blog  
Date: 2025-11-04  
Confidence: medium (single named customer, financial sector)

**Review Score**  
Claim: Nolist.ai le da 72/100. "Best for: Developers building production RAG pipelines who need to prevent application crashes caused by malformed LLM responses. Not ideal for: Low-latency applications like real-time voice where the 100ms overhead from multiple validators is a dealbreaker."[^187^]
Source: Nolist.ai Review  
URL: https://nolist.ai/item/guardrails-ai  
Date: 2026-03-08  
Confidence: medium

### 2.2 Problemas de mantenibilidad

**RAIL XML / Format lock-in**  
Claim: "The primary lock-in risk is the RAIL XML/JSON schema format; while powerful, migrating these complex validation rules to a competitor like NeMo Guardrails would require a total rewrite of your safety logic into Colang."[^187^]
Source: Nolist.ai Review  
Confidence: high

**Pydantic v2 compatibility issues**  
Claim: "version 0.5.18 users report occasional conflicts with the latest pydantic v2 updates." Además, un issue de guardrails-api-client menciona: "Most of the issues are the result of the library trying to do too much (ser/de, using restrictive pydantic types, etc.)."[^187^][^250^]
Source: Nolist.ai / GitHub Issue #21  
URL: https://nolist.ai/item/guardrails-ai / https://github.com/guardrails-ai/guardrails-api-client/issues/21  
Date: 2026-03-08 / 2024-06-24  
Confidence: high

**Developer experience criticism**  
Claim: Una comparativa de 2023 (pre-1.0) encontró: "Guardrails was the hardest library to get started... Their ambition of creating a language / DSL for wrapping LLM API calls is an ambitious vision... I found the library to be a little challenging to use and it took me, by far, the longest to figure out how to effectively use it. The examples are a little dated and I wasn't able to figure out how to configure the model."[^233^]
Source: learnbybuilding.ai — Uncovering the Best LLM Data Extraction Library  
URL: https://learnbybuilding.ai/comparison/marvin-ai-vs-guardrails-vs-instructor/  
Date: 2023 (pre-1.0)  
Context: Review temprana; la biblioteca ha evolucionado desde entonces  
Confidence: medium (outdated pero revela raíces de DX problemática)

### 2.3 Veredicto para Faberloom MVP

**NO recomendado para MVP.** Razones: (a) curva de aprendizaje RAIL/XML innecesaria para equipo 1-3 devs, (b) lock-in en formato propietario, (c) overhead de 100ms+ cuando Faberloom necesita latencia baja para WhatsApp, (d) conflicto con Pydantic v2 que ya usa en su stack, (e) para validación simple de esquemas Pydantic ya cubre el 90% del caso de uso. Considerar post-MVP si se necesitan 50+ validators pre-built.

---

## 3. Instructor: ¿Sirve como alternativa o es complementario?

### 3.1 Estado del proyecto

Claim: Instructor es la biblioteca Python más popular para extracción estructurada de LLMs: 3M+ descargas mensuales, 12.3k GitHub stars, 100+ contribuidores. Usada en producción por equipos en OpenAI, Google, Microsoft, AWS.[^30^][^40^]
Source: Instructor Official Docs / GitHub  
URL: https://python.useinstructor.com/ / https://github.com/567-labs/instructor  
Date: 2025 / 2023  
Confidence: high

### 3.2 Relación con PydanticAI

Claim: "Instructor for extraction, PydanticAI for agents. Instructor shines when you need fast, schema-first extraction without extra agents. When your project needs quality gates, shareable runs, or built-in observability, try PydanticAI." La relación es explícita: ambas son del ecosistema Pydantic y PydanticAI "adds typed tools, dataset replays, and production dashboards while keeping your existing Instructor models."[^30^]
Source: Instructor Official Docs  
URL: https://python.useinstructor.com/  
Date: 2025  
Confidence: high

### 3.3 Comparativa técnica

| Feature | Instructor | PydanticAI |
|---------|-----------|------------|
| Approach | Post-gen validation | Post-gen validation |
| Auto-retry | Yes (built-in) | Yes (built-in) |
| Agent/tool support | No | Yes |
| Multi-provider | Any (15+) | Any |
| Latencia overhead | ~1-2ms wrapping | ~1-2ms validation |
| Stars | 12.3k | 14.5k |
| Best for | Quick extraction | Python agents with tools |

Source: codecut.ai / dev.to[^239^][^240^]  
Confidence: high

### 3.4 Veredicto para Faberloom MVP

**NO agregar Instructor.** PydanticAI ya provee validación post-generation con retries automáticos vía `output_type` y `result_type`. El equipo de Faberloom ya eligió PydanticAI como stack. Agregar Instructor sería redundancia con overhead cognitivo y de dependencias. La documentación oficial de Instructor misma recomienda PydanticAI cuando se construyen agents.

---

## 4. LangChain guardrails: ¿Son efectivos o overhead?

### 4.1 Evidencia de overhead y abandono en producción

**Octomind — 12 meses en producción, luego removido**  
Claim: "We used LangChain in production for over 12 months, starting in early 2023 then removing it in 2024... As its inflexibility began to show, we soon found ourselves diving into LangChain internals... But because LangChain intentionally abstracts so many details from you, it often wasn't easy or possible to write the lower-level code we needed." El resultado: "replacing its rigid high-level abstractions with modular building blocks simplified our code base and made our team happier and more productive."[^173^]
Source: Octomind Blog — Why We No Longer Use LangChain  
URL: https://octomind.dev/blog/why-we-no-longer-use-langchain-for-building-our-ai-agents  
Date: 2024-06-12  
Confidence: high

**Estadísticas de adopción**  
Claim: "45% of developers who experiment with LangChain never use it in production environments. Even more surprising? 23% of developers who initially adopted LangChain for production projects eventually removed it entirely."[^169^]
Source: Medium — Why 45% of Developers Never Use LangChain in Production  
URL: https://medium.com/@greekofai/why-45-of-developers-never-use-langchain-in-production-the-shocking-reality-behind-ais-most-145265efe17b  
Date: 2025-09-05  
Confidence: medium (survey data, methodology unclear)

**LangChain exit 2026**  
Claim: "Stack traces from LangChain production errors routinely span 15 to 40 frames of internal framework code." "Teams typically see 40-60% code reduction and 70-90% reduction in monthly framework maintenance after migration" a raw SDKs.[^163^]
Source: Ravoid Blog — The LangChain Exit  
URL: https://ravoid.com/blog/langchain-exit-raw-sdk-migration-2026  
Date: 2026-04-18  
Confidence: medium (análisis con datos de múltiples fuentes)

### 4.2 Veredicto para Faberloom MVP

**NO usar LangChain para guardrails.** El stack actual de Faberloom (FastAPI + Pydantic AI + LiteLLM) ya evita LangChain intencionalmente. Los guardrails de LangChain añadirían las mismas abstracciones rígidas que Octomind y otros removieron. Para validación, usar Pydantic nativo + LiteLLM pre-call hooks es más simple y mantenible.

---

## 5. ¿Cuándo quiebra el modelo regex?

### 5.1 Casos documentados de fallo en producción

**Sistema quebrado antes de demo importante**  
Claim: "Our staging environment had been working fine with simple regex parsing of LLM responses, but when we deployed to production, everything fell apart. Our regex patterns failed to match slightly different response formats, data types were inconsistent, and downstream processes couldn't handle the unpredictable data, causing cascading failures. When demo day arrived, our system was completely unusable."[^192^]
Source: DecodingAI — LLM Structure Outputs: The Silent Hero of Production AI  
URL: https://www.decodingai.com/p/llm-structured-outputs-the-only-way  
Date: 2025-10-14  
Excerpt: "The problem was clear: we had been relying on fragile string parsing, hoping the LLM would always respond in the exact same format. But in production, especially with AI systems, users will always enter inputs you never expect."  
Confidence: high

**Routing failure por cambio de phrasing**  
Claim: "Day 1: Your customer support classifier works perfectly... Day 8: The same input now returns: 'This is a payment problem. The customer was double-billed and is demanding a refund.' Your parser fails. The ticket is misrouted. Your metrics tank." El root cause: "Unstructured text is designed for humans. Production applications need structured data."[^230^]
Source: Dev.to — Stop Parsing LLMs with Regex  
URL: https://dev.to/dthompsondev/llm-structured-json-building-production-ready-ai-features-with-schema-enforced-outputs-4j2j  
Date: 2025-10-15  
Confidence: high

### 5.2 Límites teóricos y prácticos de regex

Claim: "Regex is ~1.35x faster on this simple extraction workload, but it fails on quoted or nested fields."[^59^] Para lenguaje natural, regex no puede parsear JSON correctamente debido a escaping, quoted strings, nested structures[^229^]. HTML tampoco puede parsearse con regex de forma robusta[^231^].
Source: Medium / Notepad++ Community / Reddit  
Confidence: high

Claim: "The reason you should use a real HTML parser to parse HTML rather than a regular expression isn't because regexes are theoretically not up to the job (they are), but rather merely that regular expressions as a notation are crap at describing anything other than extremely simple tokenization problems (for which they are rather good)."[^232^]
Source: Neil Madden Blog  
URL: https://neilmadden.blog/2019/02/24/why-you-really-can-parse-html-and-anything-else-with-regular-expressions/  
Date: 2019-02-24  
Confidence: high

### 5.3 Cuándo regex es apropiado vs. inadecuado

| Caso de uso | ¿Regex apropiado? | Razón |
|-------------|-------------------|-------|
| Validar formato de email/RUT/teléfono | ✅ Sí | Patrones finitos, bien definidos |
| Detectar PII (SSN, tarjetas) | ✅ Sí | Patrones numéricos con checksums |
| Keyword blocklists | ✅ Sí | Matching literal simple |
| Validar JSON schema | ❌ No | Nesting, escaping, recursion |
| Extraer entidades de NL ambiguo | ❌ No | Contexto, disambigüedad |
| Validar semántica de respuesta | ❌ No | Requiere comprensión de significado |

### 5.4 Veredicto para Faberloom MVP

Usar regex **solo para** Layer 1 determinístico: PII scrubbing, format checks (email, teléfono, moneda), keyword blocklists, length limits. **Nunca para** parsear JSON o extraer estructura semántica compleja. Para eso, usar PydanticAI `output_type` con native structured outputs de los proveedores (OpenAI/Anthropic ya garantizan schema compliance a nivel de API).

---

## 6. Implementación Python viable: comparar alternativas

### 6.1 Resumen comparativo

| Librería | Tipo | Latencia típica | Madurez | Casos de uso para LLM validation | Veredicto MVP |
|----------|------|-----------------|---------|----------------------------------|---------------|
| **stdlib `re`** | Regex engine (C) | ~1-10µs compiled | Mature (25+ años) | PII, keywords, formatos | ✅ **USAR** |
| **`regex` (PyPI)** | Regex mejorado | ~1-10µs | Mature (10+ años) | Unicode avanzado, fuzzy | ⚪ Diferir |
| **PyPcre** | PCRE2 binding | ~1-10µs | Nuevo (2025) | JIT, atomic groups | ❌ Descartar |
| **flpc / fastre** | Rust regex wrapper | ~sub-µs | **Experimental** (<1 año) | Benchmarks 28-68x vs re[^226^] | ❌ **DESCARTAR** |
| **pyparsing** | Parser combinator | ~10-100x más lento que re[^54^] | Mature (20+ años) | Gramáticas complejas, DSLs | ⚪ Diferir |
| **Lark** | PEG parser | ~10-50x más lento que re[^59^] | Mature (7+ años) | DSLs, AST generation | ⚪ Diferir |
| **Outlines** | Structured generation | ~µs overhead (pre-gen) | Activo (3+ años) | Garantía 100% schema | ⚪ Post-MVP |

### 6.2 Análisis detallado

**stdlib `re` con `re.compile()`**  
Claim: "Use `re.compile()` to compile your regex patterns when they are used multiple times. This saves the overhead of parsing the pattern each time it's used, leading to significant efficiency gains."[^211^] El stdlib `re` ya está implementado en C y libera el GIL durante matching en strings inmutables[^212^].
Source: Python docs / Boardflare / AppSignal  
Confidence: high

**flpc / fastre / regex-rust**  
Claim: flpc es "experimental stage. The code structure and dependencies may change."[^254^] fastre (hugopendlebury) tiene último release Jul 14, 2025 — **<6 meses**[^216^]. regex-rust muestra benchmarks 28-68x más rápido que stdlib `re` en algunos casos, pero "In some cases, regexrs may be up to 2x slower than regex, especially when creation of Match objects is necessary."[^226^]
Source: PyPI / GitHub  
Confidence: high

**Veredicto flpc/fastre: DESCARTAR.** A pesar de los números impresionantes de benchmark, son proyectos experimentales de <1 año sin adopción documentada en producción. Para Faberloom, el riesgo de mantenimiento y breakage supera cualquier ganancia marginal de latencia. El stdlib `re` compiled ya corre en microsegundos — suficiente para validación pre-LLM.

**pyparsing vs Lark**  
Claim: pyparsing es "slower because it is running in pure Python. Python's regex engine is implemented in C, so is inherently faster." Una comparativa mostró ratio 1:15 a 1:18 en favor de regex para parsing de 400k líneas[^54^]. Lark es "~1.35x slower" que regex en workloads simples pero "fails on quoted or nested fields"[^59^].
Source: Stack Overflow / Medium  
Confidence: high

**Veredicto pyparsing/Lark: DIFERIR.** No son necesarios para validación pre-LLM típica. Se justificarían solo si Faberloom necesita parsear un DSL complejo (ej: lenguaje de proformas custom). Para validación de inputs de WhatsApp (texto libre), regex + Pydantic es suficiente.

---

## 7. Frameworks con <6 meses o sin casos reales: Descartar

### 7.1 Lista de frameworks descartados para MVP

| Framework | Motivo descarte | Evidencia |
|-----------|-----------------|-----------|
| **flpc** | Experimental, <1 año, API inestable | "Being in experimental stage. The code structure and dependencies may change."[^254^] |
| **fastre** | <6 meses, 0 casos producción | PyPI release Jul 14, 2025[^216^] |
| **PyPcre** | Nuevo (2025), no probado en LLM stacks | Primer release Oct 2025[^220^] |
| **pydantic-ai-guardrails** (jagreehal) | Third-party no oficial, <1 año | Repo creado Jan 2026[^244^] |
| **Rynko Flow** | Comercial, no biblioteca open-source | Comparativa comercial[^228^] |
| **Marvin** | Menos maduro que Instructor/PydanticAI | Review pre-2024[^233^] |

### 7.2 Frameworks a considerar post-MVP

| Framework | Cuándo considerar |
|-----------|-------------------|
| **Outlines** | Cuando se tenga infra local (vLLM/SGLang) y se necesite 100% schema guarantee sin retries |
| **GuardrailsAI** | Cuando se necesiten 50+ validators pre-built o compliance enterprise |
| **NeMo Guardrails** | Cuando se construya chatbot conversacional multi-turn complejo |

---

## 8. Recomendaciones arquitectónicas para Faberloom MVP

### 8.1 Stack recomendado (pre-LLM validation)

```
[WhatsApp Input]
    │
    ▼
┌─────────────────────────────┐
│ Layer 0: Prompt Engineering │ ← Instrucciones claras, few-shot examples
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Layer 1: Deterministic      │ ← stdlib `re` compiled patterns
│ Pre-LLM Validation          │    - PII scrubbing (regex simple)
│   (~10-100µs)               │    - Keyword blocklist (Trie/retrie)
│                             │    - Format checks (email, tel, monto)
│                             │    - Length limits
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Layer 2: LiteLLM Proxy      │ ← Rate limiting, token quotas, routing
│   (pre_call guardrails)     │    - Keyword blocking built-in
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Layer 3: LLM Inference      │ ← Haiku (L1) / Sonnet (L2) via LiteLLM
│   + Structured Outputs      │    - OpenAI/Anthropic native JSON schema
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Layer 4: PydanticAI         │ ← `output_type` validation + auto-retry
│ Post-LLM Validation         │    - max_retries=2 (default)
│   + ModelFingerprint        │    - Probation on model change
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Layer 5: Business Rules     │ ← Python puro, testeable
│   (pre-tool execution)      │    - BeforeToolCall validation
└─────────────────────────────┘
```

### 8.2 Justificación por capa

**Layer 1 (Deterministic):** stdlib `re` es suficiente. Python's regex engine está en C, libera GIL, y con `re.compile()` es sub-millisecond. No justifica agregar dependencias Rust experimental.[^211^][^212^]

**Layer 2 (LiteLLM):** LiteLLM ya provee "built-in features include keyword blocking and regex-based detection for sensitive data" y "pre-call validation" con "granular policy control per API key or project."[^183^] Aprovechar esto en vez de reinventar.

**Layer 4 (PydanticAI):** Ya en el stack. Post-response validation con retries automáticos. El issue #660 de pydantic-ai discute explícitamente la estrategia y menciona que native structured outputs de proveedores están en roadmap[^219^].

**Layer 5 (Business Rules):** Hooks tipo `BeforeToolCallEvent` ejecutan validación de negocio en Python puro, testeable, sin frameworks. Patrón documentado por AWS: "The hook runs outside the LLM. The decision is not the LLM's to make."[^210^]

### 8.3 Anti-patrones a evitar

1. **No parsear JSON con regex.** "Our regex patterns failed to match slightly different response formats... causing cascading failures."[^192^]
2. **No usar regex para semántica.** "Regex filters only catch known patterns — attackers routinely bypass them using character substitution, base64 encoding, or Unicode separators. They are also context-blind."[^168^]
3. **No agregar frameworks que dupliquen PydanticAI.** Instructor y GuardrailsAI son redundantes cuando ya se usa PydanticAI + LiteLLM.
4. **No adoptar bibliotecas <1 año en ruta crítica.** flpc, fastre, PyPcre carecen de track record.

---

## 9. Contra-argumentos documentados

| Contra-argumento | Fuerza | Respuesta |
|------------------|--------|-----------|
| "Pero regex-rust es 28x más rápido" | Débil | El stdlib `re` ya corre en <1ms para patterns simples. 28x de casi-cero es casi-cero. El riesgo de dependencia experimental no vale la pena. |
| "GuardrailsAI tiene 50+ validators pre-built" | Media | Sí, pero RAIL format es lock-in. Para MVP, Pydantic validators custom son 10 líneas cada uno. |
| "Instructor tiene más stars que PydanticAI" | Débil | PydanticAI es más nuevo pero del equipo oficial de Pydantic. Instructor mismo recomienda PydanticAI para agents. |
| "LangChain tiene más integraciones" | Media | Sí, pero 45% nunca llega a producción y 23% lo remueve. Las integraciones no valen el costo de mantenimiento. |
| "Necesitamos WASM como Ruflo" | Media | WASM sub-millisecond es viable pero requiere infra Rust/WASM. Diferir hasta que el volumen justifique el esfuerzo. |

---

## 10. Decisiones resumidas

| Decisión | Acción | Timeline |
|----------|--------|----------|
| **stdlib `re` + `re.compile()`** | Implementar | MVP (Semana 1-2) |
| **LiteLLM pre-call hooks** | Configurar keyword blocking | MVP (Semana 1-2) |
| **PydanticAI `output_type` + retries** | Ya en stack, usar `max_retries=2` | MVP (Semana 1) |
| **Before-tool Python validators** | Implementar para cobranza/proformas | MVP (Semana 3-4) |
| **flpc / fastre / PyPcre** | **Descartar** | N/A |
| **GuardrailsAI** | **Descartar** para MVP, reevaluar post-MVP | Post-MVP |
| **Instructor** | **Descartar** (redundante con PydanticAI) | N/A |
| **LangChain** | **Descartar** (ya fuera del stack) | N/A |
| **Outlines / Guidance** | **Diferir** hasta infra local | Post-MVP v2 |
| **pyparsing / Lark** | **Diferir** hasta necesidad de DSL | Post-MVP |

---

## Fuentes consultadas (orden de aparición)

1. [^35^] Introl Blog — Deploying AI guardrails at production scale (2026-02-05)
2. [^30^] Instructor Official Docs — python.useinstructor.com
3. [^40^] GitHub — 567-labs/instructor
4. [^37^] Ceaksan — Multi-Layer Defense for LLM Production Systems (2026-04-20)
5. [^63^] NeuralStack — Secure-by-Design Patterns for LLM-Backend APIs (2026-04-09)
6. [^64^] Datadog — LLM guardrails: Best practices (2025-10-22)
7. [^58^] VentureBeat — Monitoring LLM behavior: Drift, retries, refusal (2026-04-24)
8. [^60^] arXiv — A Pre-Execution Firewall and Audit Layer for AI Agents (2026-03-13)
9. [^201^] Arthur.ai — Best Practices for Building Agents | Part 5 (2026-04-06)
10. [^248^] Authority Partners — AI Agent Guardrails Production Guide (2025-11-18)
11. [^187^] Nolist.ai — Guardrails AI Review (2026-03-08)
12. [^217^] WorkOS — Guardrails AI Features, Pricing, Alternatives (2025-11-04)
13. [^212^] GitHub Discussion — guardrails-ai/guardrails #1399 (2026-02-08)
14. [^233^] learnbybuilding.ai — Uncovering the Best LLM Data Extraction Library
15. [^173^] Octomind — Why We No Longer Use LangChain (2024-06-12)
16. [^169^] Medium — Why 45% of Developers Never Use LangChain (2025-09-05)
17. [^163^] Ravoid — The LangChain Exit (2026-04-18)
18. [^192^] DecodingAI — LLM Structure Outputs (2025-10-14)
19. [^230^] Dev.to — Stop Parsing LLMs with Regex (2025-10-15)
20. [^229^] Notepad++ Community — Why you shouldn't parse JSON with regex
21. [^231^] Reddit — ELI5 Why can't regex parse HTML
22. [^232^] Neil Madden — Why you really can parse HTML with regex
23. [^59^] Medium — I Dropped Regex for These 3 Parsing Libraries
24. [^54^] Stack Overflow — Why is PyParsing taking so much longer to parse vs RegEx
25. [^211^] Boardflare — Python Regex vs Excel
26. [^212^] PyPI — regex package (alternative to stdlib)
27. [^254^] PyPI — flpc package
28. [^226^] PyPI — regex-rust package
29. [^216^] PyPI — fastre (hugopendlebury profile)
30. [^220^] PyPI — PyPcre
31. [^205^] W3Computing — Domain-Specific Language Parsers with PLY & Lark
32. [^203^] Outlines Docs — dottxt-ai.github.io
33. [^206^] GitHub — dottxt-ai/outlines
34. [^239^] Dev.to — Top 5 Structured Output Libraries for LLMs in 2026
35. [^240^] CodeCut — 5 Python Tools for Structured LLM Outputs
36. [^219^] GitHub — pydantic/pydantic-ai #660
37. [^210^] Dev.to AWS — AI Agent Guardrails: Rules That LLMs Cannot Bypass
38. [^183^] Dev.to — Top 5 AI Gateways (LiteLLM guardrails)
39. [^185^] GuardrailsAI Blog — Leverage LiteLLM in Guardrails
40. [^56^] Vellum AI — Experimentation before & after production
41. [^168^] Dev.to Precogs AI — Why Pre-LLM Sanitization Matters
42. [^182^] arXiv — PlanCompiler: Deterministic Compilation Architecture for LLM Pipelines (2026-04-08)
43. [^189^] Tetrate — LLM Output Parsing and Structured Generation Guide
44. [^191^] n8n — Production AI Playbook: Deterministic Steps & AI Steps
45. [^202^] Agility-at-Scale — AI Guardrails for Enterprise LLMs
46. [^223^] Render — Implementing guardrails against prompt injection
47. [^224^] Zuplo — Production AI Agent Endpoints Need an API Gateway
48. [^227^] Maxim AI — Top 5 AI Gateways for Production LLM Applications
49. [^228^] Rynko — Rynko Flow vs Pydantic vs Guardrails AI
50. [^243^] arXiv — Deterministic Guardrails for Agentic Financial Systems (WASM sub-millisecond)
51. [^246^] arXiv — Kernel-Level Tool Governance via WASM

---

*End of Research Report — Dimensión 03: GAP 1*
