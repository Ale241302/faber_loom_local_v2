# PROMPT DE AUDITORÍA FUNCIONAL — FABERLOOM (para ChatGPT / revisor externo)

**Fecha:** 2026-04-18
**Objetivo:** Auditoría independiente de la priorización de 20 funcionalidades de FaberLoom contra el landscape competitivo verificado por Kimi Swarm (43 empresas analizadas).
**Pegar este prompt completo en ChatGPT (recomendado: GPT-5 Thinking, Claude Opus 4.6, o modelo con razonamiento extendido).**

---

## 0. ROL QUE ASUMES

Eres **auditor senior de producto y arquitectura de agentes IA**, con perfil híbrido:
- Ex-director de producto en plataforma B2B SaaS con 8+ años en AI/ML
- Auditor técnico que ha revisado roadmaps de Harvey, Sierra, Glean y Relevance AI
- Experto en Orchestrator-Worker patterns, HITL design, memory architectures, policy engines
- Enfoque analítico: identificas puntos ciegos, desafías supuestos, no eres complaciente

**Tu tarea no es validar. Es romper.** Si encuentras la priorización correcta, dímelo con evidencia. Si encuentras huecos, nómbralos con precisión y costo estimado de no atenderlos.

---

## 1. CONTEXTO DE FABERLOOM (el producto a auditar)

### 1.1 Qué es
FaberLoom es un SaaS B2B que construye **"AI employees"** — agentes IA que aprenden observando a humanos antes de actuar solos. Modelo progresivo de autonomía.

### 1.2 Pilares de producto (hipótesis actuales)
- **Shadow Mode (L0)**: el agente observa al humano ejecutar la tarea, genera gold samples, no actúa hasta que lo autoricen
- **Framework de autonomía L0–L5** (inspirado en Artisan Level 1-5): progresión de observador → ejecutor supervisado → ejecutor autónomo con auditoría
- **Arquitectura de 3 objetos**: AgentSpec (manifest YAML) / Runtime (state machine de ejecución) / Memory (5 capas: ephemeral → session → user → org → global)
- **2 superficies**:
  - **Chat** (cliente final) — UX simple, 1 input, orquestador decide todo
  - **Console** (operador/admin) — sidebar con lista de agentes, 3 estados (DISABLED/ENABLED/FORCE_INVOKE), telemetría, gold samples, feedback tipificado
- **Policy engine externo** al LLM — reglas de negocio duras (crédito, compliance, precios) viven fuera del modelo
- **Draft-first guardrail operativo** — todo output crítico nace como borrador revisable
- **Event-driven learning** — cada interacción con feedback tipificado mueve pesos en el pipeline Candidate → Active → Archived
- **Handoffs estructurados** entre agentes con payload formal (no prompt injection)
- **Autonomía por evidencia** — un agente solo sube de nivel L0→L5 cuando hay N gold samples + precision ≥ X

### 1.3 Stack y contexto operativo
- CEO: Álvaro, Costa Rica (UTC-6)
- Empresa: Muito Work Limitada (MWT), marca Rana Walk (Amazon FBA) + representación B2B Marluvas/Tecmater (calzado seguridad industrial, México-Colombia)
- Stack: Claude Code, n8n, Google Drive, Amazon SP-API, Helium 10, pgvector
- Prototipo HTML activo (~3,100 líneas): Agentes, Agent Console, Centro de Conexiones implementados

### 1.4 ICP tentativo
SMBs no-tech en construcción/logística/agricultura/retail físico (hueco identificado por Kimi: todos los winners pelean por enterprise tech). Ventaja: Álvaro ya vende a este ICP con calzado de seguridad — conoce el buyer, los procesos, el dolor.

---

## 2. RESUMEN DETALLADO DE OBSERVACIONES DE KIMI SWARM

Kimi desplegó 43 agentes en paralelo para investigar el landscape de agentes IA a 2026-Q1. Output: 43 fichas estructuradas (ICP, modelos, memoria, HITL, pricing, diferenciadores, debilidades, red flags, tracción) + análisis estratégico consolidado.

### 2.1 Siete clústeres emergentes (a 2026-Q1)

| # | Clúster | Ejemplos | Señal clave |
|---|---------|----------|------------|
| 1 | **Multi-Model Horizontal Enterprise** | Glean, Writer, Microsoft Copilot Studio | RAG + KG + ruteo multi-modelo; enterprise distribution |
| 2 | **Infrastructure/Router** | OpenRouter, Together AI, Martian, NotDiamond, Portkey | Capa de abstracción, no producto final |
| 3 | **Vertical B2B Domain-Specific** | Harvey (legal), Hippocratic (health), Abridge (health), EvenUp (injury law), Clay (sales), Parloa (CX) | Forward-deployed experts, vendido a sectores regulados |
| 4 | **Big Tech Platform** | Salesforce Agentforce, AWS Bedrock Agents, Google Agentspace | Distribución vía su stack existente |
| 5 | **Browser/Computer-Use** | OpenAI Operator, Browser Use, MultiOn, Orby AI | UI-level automation, reemplazo de RPA |
| 6 | **China AI Six Tigers** | Zhipu, MiniMax, DeepSeek, Moonshot (Kimi), 01.AI, StepFun | Muy fuerte técnicamente, mercado occidental bloqueado por geopolítica |
| 7 | **AI Employee Startups** | 11x, Lindy, Artisan, Relevance AI, Cognition (Devin), Ema, Sierra, Decagon | Alta variabilidad de calidad y tracción |

### 2.2 Top 5 ganadores verificados (evidencia de ARR + retención + moat)

1. **Harvey** — legal vertical. $100M+ ARR, forward-deployed ex-abogados, HITL default-on, moat distribución en Big Law
2. **Glean** — enterprise search + agents. $100M+ ARR, integra 100+ SaaS, KG+RAG, retención >95%
3. **Sierra** — CX. Bret Taylor, Agent Development Platform (ADP) pattern, outcome-based pricing pionero
4. **Abridge** — clinical notes. Médico-fundador, linked evidence (cada afirmación enlaza al timestamp del audio), certificado por hospitales
5. **Salesforce Agentforce** — plataforma. Distribución vía CRM installed base; ejecución irregular pero inevitable por peso del canal

### 2.3 Top 5 en riesgo / zombies

1. **11x** — SDR AI. Caídas de retención, claims de ARR cuestionables, churn visible
2. **Adept** — ACT-1. Absorbido por Amazon, producto muerto
3. **MultiOn** — browser agents. Sin tracción comercial, pivot constante
4. **Martian** — router. Sin señal de tracción, mercado comoditizado
5. **Google Agentspace** — adopción interna irregular incluso dentro de Google Cloud accounts

### 2.4 Seis huecos de mercado identificados (ORDEN DE RELEVANCIA PARA FABERLOOM)

1. **Shadow Mode end-to-end puro** — NADIE lo hace completo. Harvey tiene HITL fuerte pero no observación-antes-de-ejecutar como pilar. Sierra tiene approval loops pero no framework L0-L5. **Este es el moat candidato de FaberLoom.**
2. **SMBs no-tech verticales** (construcción/logística/agricultura/retail físico) — todos los winners cazan enterprise tech. Hueco estructural. **Alineado con el expertise de Álvaro en Marluvas/Tecmater.**
3. **Linked evidence como feature transversal** — solo Abridge lo hace bien (en health). Harvey lo hace parcial. Nadie lo hace como pattern reutilizable por vertical.
4. **Framework público de autonomía progresiva** — Artisan lo menciona (Level 1-5) pero no lo usa como product framework real. Espacio abierto para claim de categoría.
5. **Outcome-based pricing transparente para SMB** — Sierra lo hace bien en enterprise. Nadie en SMB. Estructura "pagás cuando resuelvo" + trial gratuito.
6. **Policy engine externo accesible** — todos lo tienen interno/opaco. Oportunidad de exponerlo como config visible al cliente (trust + compliance).

### 2.5 Seis patrones arquitectónicos dominantes (frecuencia ≥3 de 43)

| Pattern | Frecuencia | Hacer en FaberLoom? |
|---------|-----------|---------------------|
| Multi-Model Routing (rule → semantic → LLM fallback) | ≥8 | **SÍ** — ahorro de costo sustancial |
| Multi-Layer Memory (≥3 capas) | ≥6 | **SÍ** — ya planificado (5 capas) |
| Knowledge Graph + RAG híbrido | ≥3 | **TAL VEZ** — depende de ICP, KG para enterprise tech caro |
| HITL Configurable (3+ modos) | ≥5 | **SÍ** — core del Shadow Mode |
| Computer-Use / GUI automation | ≥4 | **NO AHORA** — alta inversión, bajo fit |
| Outcome-Based Pricing | ≥4 | **SÍ** — como pricing hybrid (platform + per-resolution) |

### 2.6 Cinco patrones de producto dominantes

1. **Visual Workforce Canvas** (Relevance AI) — arrastrar agentes en canvas visual
2. **Agent Development Platform** (Sierra) — meta-agent que construye agentes
3. **Forward-Deployed Experts** (Harvey, Sierra) — humanos reales en cliente, no solo CS
4. **Mixture-of-Agents (MoA)** productizado (Genspark, aunque con claims dudosos) — basado en paper Together AI 2024
5. **Progressive Disclosure UX** (Monica, Poe) — opt-in `@agent` para power users, default simple

### 2.7 Benchmarks específicos para FaberLoom

**Imitar:**
- Harvey: HITL default-on como postura de producto, no feature opcional
- Abridge: linked evidence como confianza por defecto
- Sierra: outcome-based pricing transparente
- Genspark Claw: 3 niveles de memoria explícitos al usuario

**NO copiar:**
- 11x: claims de autonomía L5 sin el foundation → retention se muere
- Adept: apuesta full computer-use antes de resolver orchestración
- Artisan: marketing "AI Employee" sin framework real detrás

### 2.8 Contradicciones detectadas por Kimi (señal de marketing vs realidad)

- Genspark: ARR declarado salta de $36M a $100M en 3 meses sin explicación de GTM
- Writer: claims de retention enterprise no conciliables con ratios de LinkedIn job postings
- Abridge: ronda Serie D con valoración inconsistente con ARR declarado
- Hippocratic: revenue claim vs número de hospitales activos no cuadra
- Sierra: headcount público vs LinkedIn inconsistente
- DeepSeek: costo de training reportado ($5.5M) cuestionado por varios labs
- 01.AI: claims de usuarios en China no verificables
- Salesforce: adoption gap real entre accounts que pagaron Agentforce y los que lo usan
- Monica: número de usuarios activos vs descargas

**Implicación:** Kimi recomienda tratar claims de ARR/users/retention de todo competidor con 40-60% descuento implícito.

---

## 3. PRIORIZACIÓN DE 20 FUNCIONALIDADES (mi análisis — a auditar)

Escala:
- **Impacto (1-10):** valor diferencial para FaberLoom en su ICP target
- **Esfuerzo:** S (≤2 semanas) / M (≤6 semanas) / L (≤3 meses) / XL (>3 meses)
- **MoSCoW:** MUST / SHOULD / COULD / WON'T-NOW

| # | Funcionalidad | Impacto | Esfuerzo | Clase | Justificación corta |
|---|---------------|---------|----------|-------|---------------------|
| 1 | Shadow Mode (L0) | 10 | L | MUST | Moat único verificado por Kimi; nadie lo hace puro |
| 2 | Orchestrator-Worker pattern | 10 | L | MUST | Base de toda arquitectura multi-agente seria |
| 3 | Linked Evidence | 10 | M | MUST | Confianza por defecto; Abridge demuestra que escala |
| 4 | HITL Configurable (3 modos) | 9 | S | MUST | Core del Shadow Mode; Harvey lo valida |
| 5 | Framework L0-L5 público | 9 | M | MUST | Claim de categoría; Artisan abrió espacio |
| 6 | Capability Registry (YAML manifests MCP) | 9 | M | MUST | Escalabilidad de agentes; MCP-compatible futuro |
| 7 | Policy Engine externo | 9 | M | MUST | Protege motor; trust B2B |
| 8 | Multi-Model Routing (rule→semantic→LLM) | 8 | M | SHOULD | Economía de costo 5-10x |
| 9 | 5-Layer Memory | 8 | L | MUST | Ya arquitectado; ejecución pendiente |
| 10 | Cascada de ejecución (5 layers) | 8 | M | SHOULD | 50-60% queries en capas 0-2 a ~$0.001 |
| 11 | Feedback tipificado + Candidate/Active/Archived | 8 | M | MUST | Event-driven learning funcional |
| 12 | Console operador (sidebar 3 estados) | 8 | M | MUST | Auditoría B2B no-negociable |
| 13 | Outcome-Based Pricing híbrido | 8 | S | SHOULD | Plataforma + per-resolution; Sierra valida |
| 14 | Draft-First Guardrail | 8 | S | MUST | Guardrail operativo sin infraestructura pesada |
| 15 | Progressive Disclosure UX (@agent opt-in) | 7 | S | SHOULD | Sin fricción client, poder para operator |
| 16 | Gold Samples (13 campos) | 7 | M | MUST | Sin esto no hay Shadow Mode funcional |
| 17 | Handoffs estructurados | 7 | M | SHOULD | Escala orchestrator sin prompt injection |
| 18 | Forward-Deployed Expert (Álvaro mismo al inicio) | 7 | S | MUST | Go-to-market; Harvey valida |
| 19 | Visual Workforce Canvas | 5 | L | COULD | Bonito pero no crítico en v1 |
| 20 | Computer-Use / Browser automation | 3 | XL | WON'T-NOW | Alto costo, bajo fit ICP |

---

## 4. LO QUE CREO QUE ME FALTA (auto-evaluación explícita)

Lista de puntos donde reconozco incertidumbre o posible blind spot. **Desafía estos primero.**

1. **¿El ICP "SMB no-tech" es realmente viable, o es un agujero porque nadie lo puede monetizar?** Kimi dice hueco estructural, pero quizás la razón es CAC/LTV inviable. No tengo data de ACV promedio ni ciclo de venta en este segmento.
2. **¿Orchestrator-Worker como CORE vs como OPCIÓN en v1?** Clasifiqué MUST pero añade complejidad enorme. Alternativa: v1 con un solo agente + Shadow Mode, orchestrator en v2. No estoy seguro qué elegir.
3. **Framework L0-L5 público:** ¿es honesto reclamarlo antes de tener ≥3 clientes en L3+? Artisan lo "abrió" pero nadie lo respeta. ¿FaberLoom puede sostener el claim sin casos?
4. **Linked Evidence transversal:** Abridge lo hace en health con audio como source. ¿Qué es el "source" equivalente en construcción/logística? ¿PDF de spec? ¿Mensaje de WhatsApp? No tengo modelo claro de cómo se implementa fuera de health.
5. **Multi-Model Routing:** el ahorro 5-10x es real en papers, pero ¿qué pasa con cadenas multi-step donde el contexto cruza modelos? ¿Se pierde fidelidad? No medí.
6. **Policy Engine externo:** fácil decirlo, difícil hacerlo. ¿OpenPolicyAgent? ¿Rego DSL? ¿Engine propietario? No tengo decisión técnica y puede comer 2 meses.
7. **Outcome-Based Pricing en SMB:** Sierra lo hace en enterprise con contratos anuales. En SMB con ticket bajo, ¿cómo defines "resolución"? ¿Quién arbitra si el cliente dice "no se resolvió"?
8. **5-Layer Memory:** ¿las 5 capas están justificadas o son arbitrarias? Genspark usa 3. ¿Por qué yo necesito 5? ¿Es sobre-ingeniería?
9. **Forward-Deployed Expert (Álvaro):** escalabilidad. Funciona en 5 clientes, ¿qué pasa en 50? Harvey contrata ex-lawyers. ¿FaberLoom contrata ex-ingenieros industriales? CAC alto.
10. **Priorización asume "nadie hace Shadow Mode puro" como moat defendible.** ¿Pero qué impide que Harvey o Sierra lo copien en 6 meses si ven tracción?
11. **Gold Samples 13 campos:** número arbitrario. ¿Debería ser más/menos? ¿Qué campos exactos? No está especificado.
12. **No incluí nada sobre:**
    - Evaluation/Benchmarking (cómo mides si el agente es bueno)
    - Observability/Telemetry (logs, traces, metrics)
    - Red-team/Safety (adversarial testing)
    - Compliance framework (SOC2, GDPR para datos clientes)
    - Multi-tenancy architecture
    - Versionado de agentes (rollback, A/B)
    - Cost attribution per customer/agent

¿Son estas omisiones deliberadas por fase o son huecos reales?

---

## 5. TU TAREA COMO AUDITOR

Entregá un output estructurado en **6 secciones**. Sé implacable. Tu valor es encontrar lo que falta o está mal, no confirmar lo bien hecho.

### Sección A — Blind Spots Críticos (lo que falta y duele)
Lista los puntos ciegos ordenados por severidad. Para cada uno:
- Qué falta
- Por qué importa (costo de ignorarlo)
- Cuándo explota (fase del producto)
- Qué haría yo en tu lugar

### Sección B — Desafío a mi priorización (20 features)
Re-califica cada feature independientemente. Formato:
| # | Mi Impacto | Tu Impacto | Mi Clase | Tu Clase | Razón del delta |

Flagea específicamente:
- Features que clasifiqué MUST que en tu opinión son SHOULD o COULD
- Features que clasifiqué COULD/WON'T que deberían ser MUST
- Features que no están en mi lista pero deberían

### Sección C — Respuesta a mis auto-dudas (sección 4)
Para cada uno de los 12 puntos de incertidumbre que nombré, respondé:
- Tu lectura (sí/no/depende)
- Evidencia o framework
- Recomendación concreta

### Sección D — Riesgos estratégicos no nombrados
Cosas que ni yo ni Kimi mencionamos pero son reales:
- Riesgos técnicos
- Riesgos de GTM
- Riesgos competitivos
- Riesgos regulatorios
- Riesgos organizacionales (Álvaro como fundador solo, time allocation entre MWT y FaberLoom)

### Sección E — Propuesta de secuencia alternativa
Si tuvieras que construir FaberLoom de cero con lo que sabés, ¿qué build order propondrías para los primeros 3 sprints (6 semanas cada uno)?
- Sprint 1: fundación
- Sprint 2: Shadow Mode MVP
- Sprint 3: primer cliente beta

### Sección F — Score global y veredicto
- **Score de la estrategia actual: X/10** con justificación de una línea
- **Score de la priorización: X/10**
- **Score de la autoconciencia del equipo: X/10** (cuánto reconoce sus propias limitaciones)
- **Decisión que tomaría ahora si fueras Álvaro:** párrafo crudo de qué haría mañana lunes

---

## 6. REGLAS DE LA AUDITORÍA

- **No seas condescendiente.** Álvaro tiene conocimiento técnico sólido; no le expliques básicos.
- **Cita evidencia.** Si decís "Harvey hace X", decí de dónde lo sabés (ronda, blog, post, etc.). Si no tenés evidencia, marcá `[SIN VERIFICAR]`.
- **Rechaza claims débiles.** Si algo del análisis parece marketing, decilo.
- **Contradecime donde corresponda.** Especialmente en la sección 4 (auto-dudas) — si 6 de 12 dudas las resolví mal, decímelo.
- **Formato Markdown.** Tablas donde aplique. Sin emojis. Prosa directa, no corporativa.
- **Longitud:** sin límite superior, pero no diluyas. Si tu respuesta tiene menos de 2,000 palabras y la auditoría es superficial, reempezá.

---

## 7. OUTPUT FINAL ESPERADO

Un documento con las 6 secciones (A-F) listo para que Álvaro lo pegue en su KB como:
`docs/AUDIT_FABERLOOM_EXTERNAL_2026-04-18.md`

Empezá ya. No hagas preguntas de clarificación — si algo no está claro, asumí lo más razonable y marcá tu asunción.
