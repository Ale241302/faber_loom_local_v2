# DIMENSION 12: Observability, Cost Surfacing y Error Recovery en Agentic Systems

**Proyecto:** FaberLoom Design System  
**Fecha:** Julio 2025  
**Investigador:** AI Research Agent  
**Total búsquedas:** 25+ queries independientes  
**Fuentes primarias:** Documentación oficial (LangSmith, Langfuse, Arize, AG-UI), papers académicos (arXiv), blogs de ingeniería, GitHub repos  

---

## TABLA DE CONTENIDO

1. [Observability: Patrones de Visibilidad en Tiempo Real](#1-observability)
2. [Cost Surfacing: Transparencia de Costos](#2-cost-surfacing)
3. [Error Recovery: Resiliencia y Fallback](#3-error-recovery)
4. [Reasoning Visibility: Mostrar o No el Razonamiento](#4-reasoning-visibility)
5. [Execution Trace: Trazabilidad Paso a Paso](#5-execution-trace)
6. [Metrics Dashboard: Métricas y KPIs](#6-metrics-dashboard)
7. [Alertas y Notificaciones](#7-alertas)
8. [Transparency vs Overwhelm](#8-transparency-vs-overwhelm)
9. [Herramientas Evaluadas](#9-herramientas)
10. [Catálogo de Patrones para FaberLoom](#10-catalogo-patterns)
11. [Summary Ejecutivo](#11-summary)
12. [Gaps Identificados](#12-gaps)
13. [Recomendaciones](#13-recomendaciones)

---

## 1. OBSERVABILITY: Patrones de Visibilidad en Tiempo Real

### 1.1 Pattern: Agent Status Monitoring (Layered)

```
Claim: Los indicadores de carga tradicionales (spinners, progress bars) no funcionan para tareas agenticas que toman minutos u horas. Se requiere un sistema de estado en capas: ambient badge, progress panel, attention notification, y summary status. [^1^]
Source: AIUX Design Patterns - Agent Status Monitoring
URL: https://www.aiuxdesign.guide/patterns/agent-status-monitoring
Date: 2026-02-16
Excerpt: "Traditional loading indicators don't work for agentic tasks that may take minutes or hours, involve multiple parallel activities, or require occasional user attention. The design challenge is keeping users informed without demanding their attention. This pattern provides four status layers: ambient status, progress status, attention status, and summary status."
Context: Usado por ChatGPT y Devin. El sistema soporta múltiples tareas concurrentes con tiempos estimados.
Confidence: high
```

### 1.2 Pattern: AG-UI Event Streaming Protocol

```
Claim: AG-UI (Agent-User Interaction Protocol) estandariza la comunicación agente-UI mediante eventos en tiempo real (SSE/WebSockets), permitiendo mostrar progreso en tiempo real sin polling. Soporta eventos de razonamiento visibles al usuario. [^2^]
Source: AG-UI Documentation - Reasoning
URL: https://docs.ag-ui.com/concepts/reasoning
Date: 2025
Excerpt: "AG-UI provides first-class support for LLM reasoning, enabling chain-of-thought visibility while maintaining privacy and state continuity... Reasoning visibility: Surface reasoning signals (e.g., summaries) to users without exposing raw chain-of-thought"
Context: Protocolo open-source, framework-agnostic. Nacido de la partnership entre CopilotKit, LangGraph y CrewAI.
Confidence: high
```

### 1.3 Pattern: Real-Time Progress Indicator (AI-Specific)

```
Claim: Los indicadores de progreso AI deben aparecer 1 segundo después de activarse y permanecer visibles al menos 500ms para evitar flickering. Deben permitir al usuario detener el proceso. [^3^]
Source: Emarsys Design System - AI Progress Indicator
URL: https://designsystem.emarsys.net/patterns/ai-guidelines/ai-progress-indicator
Date: 2026-03-13
Excerpt: "Display the AI progress indicator on the screen one second after the generation process is triggered and ensure it remains visible for at least 500ms to avoid flickering."
Context: No usar para operaciones < 1 segundo. No usar cuando se puede dar una estimación precisa de tiempo.
Confidence: high
```

### 1.4 Pattern: Trace Tree Visualization

```
Claim: LangSmith muestra trazas como árboles jerárquicos donde cada nodo representa un paso del agente (LLM call, tool call, retrieval), con latencia, tokens y costo por nodo. Permite inspeccionar inputs/outputs de cada paso. [^4^]
Source: LangSmith Observability Documentation
URL: https://docs.langchain.com/langsmith/observability
Date: 2025
Excerpt: "Traces show the full execution tree: every LLM call, tool invocation, retrieval step, and the reasoning that connected them. It goes beyond simple inputs and outputs to reveal the internal monologue of the agent and the exact parameters passed to the model at every step."
Context: LangSmith es framework-agnostic. Funciona con OpenAI SDK, Anthropic, Vercel AI SDK, etc.
Confidence: high
```

### 1.5 Pattern: OpenTelemetry Distributed Tracing for Agents

```
Claim: OpenTelemetry es el estándar emergente para tracing distribuido de agentes AI. Cada paso del agente se convierte en un span con atributos estandarizados (agent.iteration, agent.decision, agent.tools_called, gen_ai.usage.*). [^5^]
Source: OneUptime Blog - Trace AI Agent Execution Flows with OpenTelemetry
URL: https://oneuptime.com/blog/post/2026-02-06-trace-ai-agent-execution-flows-opentelemetry/view
Date: 2026-02-06
Excerpt: "Each agent step becomes a span. The parent-child relationships between spans capture the execution hierarchy. And the trace as a whole tells you the full story of how the agent processed a request."
Context: Atributos clave: agent.iteration, agent.decision, agent.tool.name, agent.tool.arguments, gen_ai.usage.input_tokens, gen_ai.usage.output_tokens.
Confidence: high
```

### 1.6 Pattern: AI-Assisted Debugging (Natural Language Queries)

```
Claim: LangSmith Polly permite hacer preguntas en lenguaje natural sobre trazas del agente (ej: "Why did the agent enter this loop?"), analizando automáticamente los traces y sugiriendo fixes. [^6^]
Source: LangChain Blog - Introducing Polly
URL: https://www.langchain.com/blog/introducing-polly-your-ai-agent-engineer
Date: 2025-12-10
Excerpt: "Instead of manually scanning through endless traces or guessing which prompt change will fix an issue, you can simply ask Polly questions in natural language. It's like having an expert agent engineer on your team."
Context: Polly soporta Claude, OpenAI, Gemini, Bedrock, Groq, Mistral, xAI, DeepSeek, Fireworks AI.
Confidence: high
```

---

## 2. COST SURFACING: Transparencia de Costos

### 2.1 Pattern: Automatic Token & Cost Tracking (LangSmith)

```
Claim: LangSmith registra automáticamente uso de tokens y costos para proveedores principales (OpenAI, Anthropic, Gemini), con desglose en input/output/other tokens visible en el trace tree, project stats y dashboards. [^7^]
Source: LangSmith Cost Tracking Documentation
URL: https://docs.langchain.com/langsmith/cost-tracking
Date: 2025-12-01 (changelog)
Excerpt: "LangSmith now automatically records token usage and derived costs for major model providers. You can also submit custom cost data for any run type — including tools, retrieval steps or non-linear pricing models."
Context: Soporta cache reads, multimodal tokens, reasoning tokens. Permite custom pricing via model price map editor.
Confidence: high
```

### 2.2 Pattern: Cost Dashboard with Aggregation

```
Claim: Los dashboards pre-construidos de LangSmith muestran métricas agregadas: trace count, latency, error rates, cost & tokens desglosados por tipo, tool usage stats, run types, y feedback scores. Soportan agrupación por tags y metadata. [^8^]
Source: LangSmith Dashboards Documentation
URL: https://docs.langchain.com/langsmith/dashboards
Date: 2025
Excerpt: "Prebuilt dashboards are created automatically for each project and cover essential metrics: trace count, error rates, token usage, and more. Group by run tag or metadata can be used to split data over attributes important to your application."
Context: Dashboards personalizables con charts de cost trends over time.
Confidence: high
```

### 2.3 Pattern: Cost Per Successful Task (Business Metric)

```
Claim: La métrica de negocio más valiosa es "cost per successful task" (no cost per request). Incluye: token use, tool fees, infrastructure, y retries. Permite optimizar el ROI real del agente. [^9^]
Source: TestingXperts - AI Agent Evaluation Metrics
URL: https://www.testingxperts.com/blog/ai-agent-evaluation/
Date: 2026-02-02
Excerpt: "Cost for each successful activity (better than cost for each request). Token use, tool fees, and infrastructure. Cost goes up when you try again or when you have a big multi-turn loop."
Context: Scorecard recomendado: Task completion ≥92%, Wrong tool rate ≤2%, Cost per task ≤$0.04.
Confidence: high
```

### 2.4 Pattern: Per-Operation Cost Visibility (Langfuse)

```
Claim: Langfuse muestra el costo LLM de cada trace individualmente, con roll-up automático en dashboards para trackear gastos por environment (staging/production). [^10^]
Source: Kerno Blog - Improving Trace Visibility in Langfuse
URL: https://www.kerno.io/blog/improving-trace-visibility-and-reproducibility-in-langfuse
Date: 2025-11-11
Excerpt: "Each trace now includes its LLM cost, and these costs automatically roll up into a dashboard so you can track spend across staging and production environments."
Context: Langfuse también incluye version tags en cada trace para correlacionar costos con deployments.
Confidence: high
```

### 2.5 Pattern: Enriched Cost Attribution (CloudZero)

```
Claim: Para costos explicables, cada llamada OpenAI debe etiquetarse con: Feature, Team, Customer/Tenant ID, Environment, Prompt version, Model, Workflow type. Así el gasto LLM se vuelve "immediately explainable". [^11^]
Source: CloudZero - Track OpenAI Spend
URL: https://www.cloudzero.com/blog/track-openai-spend/
Date: 2026-01-30
Excerpt: "With these, your LLM spend becomes immediately explainable. Instead of a single line item labeled 'OpenAI,' you can see the exact people, processes, and products driving your costs."
Context: Enfoque de "Cloud Cost Intelligence" usado por Grammarly, New Relic, Skyscanner.
Confidence: medium
```

---

## 3. ERROR RECOVERY: Resiliencia y Fallback

### 3.1 Pattern: Exponential Backoff with Jitter

```
Claim: El retry con exponential backoff y jitter es el patrón base para errores transitorios (503, rate limits). Previene "thundering herd" cuando múltiples agentes hacen backoff simultáneamente. [^12^]
Source: PraisonAI - Agent Retry Strategies
URL: https://docs.praison.ai/docs/best-practices/agent-retry-strategies
Date: 2025
Excerpt: "Exponential delay: delay = min(initial_delay * (base ^ attempt), max_delay). Add jitter: delay = random.uniform(0, delay)."
Context: Config típica: max_attempts=3, initial_delay=1s, max_delay=60s, base=2.0.
Confidence: high
```

### 3.2 Pattern: Circuit Breaker

```
Claim: El circuit breaker previene "retry storms" donde un agente gasta $700 en una noche llamando repetidamente una API rota. Tiene 3 estados: Closed, Open, Half-open. Especialmente crítico para agentes que "re-plan" en lugar de reintentar. [^13^]
Source: BuildMVPfast - AI Agent Timeout & Circuit Breaker Patterns
URL: https://www.buildmvpfast.com/blog/agent-timeout-circuit-breaker-patterns-runaway-ai-workflows-2026
Date: 2026-04-02
Excerpt: "Failure mode 2: The reasoning loop. The agent calls a tool, gets a timeout, and instead of retrying the same call, it re-plans... Infrastructure-level circuit breakers can't see reasoning-layer retries. That's the fundamental challenge with agentic systems."
Context: Recomendación: step-count ceiling (max_steps=25), wall-clock timeout, error classification, kill switch, token budget.
Confidence: high
```

### 3.3 Pattern: Retry with Fallback

```
Claim: El patrón retry-with-fallback intenta la función primaria N veces, luego fallback a función alternativa, y finalmente cache. Reduces costos al no reintentar infinitamente. [^14^]
Source: PraisonAI - Agent Retry Strategies
URL: https://docs.praison.ai/docs/best-practices/agent-retry-strategies
Date: 2025
Excerpt: "Try primary function with retry → cache successful result → try fallback if available → return cached result if enabled → escalate if all exhausted."
Context: Config típica: primary_retry_attempts=3, fallback_retry_attempts=2, use_cache_on_failure=true.
Confidence: high
```

### 3.4 Pattern: Graceful Degradation (Hierarchy of Responses)

```
Claim: Los sistemas AI deben degradarse gracefulmente: Full AI Response → Simplified AI Response → Rule-Based Response → Human Handoff. Cada paso comunicado claramente al usuario. [^15^]
Source: Clearly.Design - Designing for AI Failures
URL: https://clearly.design/articles/ai-design-4-designing-for-ai-failures
Date: 2025-08-12
Excerpt: "Design fallback levels that maintain usefulness even when AI fails. Intercom's chatbots visibly degrade: first AI responses, then 'Here are some related help articles,' then 'Talk to a human' — each step clearly communicated."
Context: Voice assistants demuestran confidence cascades: alta confianza → acción inmediata; media → clarificación; baja → "Try saying it differently."
Confidence: high
```

### 3.5 Pattern: Error Classification & Routing

```
Claim: No todos los errores son iguales. Se necesitan 4 categorías: Transient (system retry), LLM-recoverable (el LLM reformula), User-fixable (human interrupt), Unexpected (developer bug). Cada uno necesita estrategia diferente. [^16^]
Source: Dev.to - 4 Fault Tolerance Patterns Every AI Agent Needs
URL: https://dev.to/klement_gunndu/4-fault-tolerance-patterns-every-ai-agent-needs-in-production-jih
Date: 2026-03-02
Excerpt: "The key insight: when a tool fails, you do not retry the same call. You send the error back to the LLM so it can reformulate. The LLM becomes the error handler."
Context: Resultados medidos: unrecoverable failures dropped from 23% to under 2%; cost per failure decreased by 85%.
Confidence: high
```

### 3.6 Pattern: Human-in-the-Loop (5 Core Patterns)

```
Claim: Existen 5 patrones HITL que cubren 90%+ de casos de uso: Approval Gate, Escalation Ladder, Confidence-Based Routing, Collaborative Drafting, y Audit Trail with Lazy Review. La tasa de error crítico bajó de 23% a 5.1% tras implementar HITL. [^17^]
Source: Dev.to - HITL for AI Agents: Patterns and Best Practices
URL: https://dev.to/taimoor__z/-human-in-the-loop-hitl-for-ai-agents-patterns-and-best-practices-5ep5
Date: 2026-04-19
Excerpt: "AI agents without human checkpoints fail catastrophically — our autonomous agent pipeline had a 23% critical error rate before HITL; after implementing structured human gates, that dropped to 5.1% (a 78% reduction)."
Context: Caso real: Coinbase usa 3 tiers — AI maneja 60% de queries rutinarias, Tier 1 review para info financiera, Tier 3 fraud team para >$10K.
Confidence: high
```

### 3.7 Pattern: Self-Healing (Checkpoint & Recovery)

```
Claim: Los agentes pueden auto-recuperarse mediante checkpointing periódico del estado. Si el agente crasha, se reanuda desde el último checkpoint sin perder progreso. Patrones: retry con exponential backoff, circuit breaker, graceful degradation. [^18^]
Source: Agentbase Docs - Self-Healing
URL: https://docs.agentbase.sh/primitives/essentials/self-healing
Date: 2025
Excerpt: "Automatic retry pattern: Attempt 1: Immediate, Attempt 2: Wait 1s, Attempt 3: Wait 2s, Attempt 4: Wait 4s, Attempt 5: Wait 8s. Total attempts: 5, then escalate to user."
Context: Circuit breaker: try → retry → detect pattern → open circuit → use fallback → periodically test recovery.
Confidence: medium
```

---

## 4. REASONING VISIBILITY: Mostrar o No el Razonamiento

### 4.1 Pattern: Visible Thinking (Summary vs Raw)

```
Claim: Mostrar el "pensamiento" del chatbot antes de la respuesta aumenta la confianza y el engagement. Dos framing: Emotionally-Supportive (más cálido, empático) y Expertise-Supportive (más lógico, profesional). Ambos superan la condición "None" en trust y engagement. [^19^]
Source: arXiv - User Perceptions of Visible Thinking in Chatbots
URL: https://arxiv.org/html/2601.16720v1
Date: 2026-01-23
Excerpt: "The Expertise-Supportive chatbot was rated as possessing greater levels of trust and understanding. Participants described the chatbot as 'logical', 'professional', and 'reliable'... The None condition was seen as lacking empathy or interest in the user."
Context: Estudio 3x2 mixed design (Thinking Content x Conversation Context). N=230+ participants. Visible thinking functiona como "self-presentation" del chatbot.
Confidence: high (paper académico peer-reviewed, ACM DIS 2026)
```

### 4.2 Pattern: AG-UI Reasoning Streaming

```
Claim: AG-UI separa el razonamiento interno de las respuestas finales mediante ReasoningMessage. El agente controla qué se muestra: full visibility, summary only, o hidden (encrypted). Soporta zero data retention. [^20^]
Source: AG-UI Documentation - Reasoning
URL: https://docs.ag-ui.com/concepts/reasoning
Date: 2025
Excerpt: "Agents control what reasoning is visible to users: Full visibility: Stream complete chain-of-thought; Summary only: Emit condensed summary while attaching detailed reasoning as encrypted values; Hidden: Use only encrypted events with no visible streaming."
Context: Encrypted reasoning values permiten GDPR right to erasure (descartar sin perder capability).
Confidence: high
```

### 4.3 Pattern: Chain of Thought Component (Collapsible)

```
Claim: Un componente UI collapsible que muestra pasos del razonamiento ("searching the web", "analyzing results", "forming response") con status visual (complete/active/pending) y nested content. [^21^]
Source: shadcn UI - React AI Chain of Thought
URL: https://www.shadcn.io/ai/chain-of-thought
Date: 2025
Excerpt: "A collapsible panel that breaks down the AI's reasoning into visible steps. Each step can have its own status (complete, active, pending), custom icons, and nested content. Built on Radix primitives."
Context: Componente reutilizable. Se colapsa a una línea cuando el usuario no quiere ver detalles.
Confidence: medium
```

### 4.4 Counter-argument: Expectancy Violations

```
Claim: El visible thinking puede crear "expectancy violations" negativas: si el thinking implica profundidad pero la respuesta final es superficial, los usuarios se frustran. El framing debe alinearse con el rol del chatbot y el contexto. [^22^]
Source: arXiv - User Perceptions of Visible Thinking in Chatbots (Discussion)
URL: https://arxiv.org/html/2601.16720v1
Date: 2026-01-23
Excerpt: "Both visible thinking conditions produced negative expectancy violations when the chatbot's final reply failed to meet the expectations established by its displayed thinking... some reported frustration when the depth implied by the chatbot's 'thinking' was not reflected in the substance of its eventual reply."
Context: Importante: el thinking display debe adaptarse al contexto conversacional.
Confidence: high
```

---

## 5. EXECUTION TRACE: Trazabilidad Paso a Paso

### 5.1 Pattern: Hierarchical Trace Tree

```
Claim: Las trazas de agentes se visualizan como árboles jerárquicos (trace tree) donde cada span tiene: inputs, outputs, latency, token usage, status, y parent-child relationships. Permite reconstruir el flujo completo de ejecución. [^23^]
Source: Langfuse - What does a good trace look like
URL: https://langfuse.com/faq/all/what-does-a-good-trace-look-like
Date: 2026-05-05
Excerpt: "A trace shows up in the Langfuse UI as a trace tree and an agent graph... You should see your LLM calls, tool calls, and other important steps represented in the tree. They should have the correct observation type."
Context: Niveles: observations (steps) → traces (via trace_id) → sessions (via session_id).
Confidence: high
```

### 5.2 Pattern: Trace Replay for Debugging

```
Claim: Las trazas deben incluir suficiente información para reproducir issues: input artifacts, intermediate outputs, configuration states, Docker Compose, SQL files, request payloads. El goal es hacer cada trace un "complete snapshot". [^24^]
Source: Kerno Blog - Improving Trace Visibility in Langfuse
URL: https://www.kerno.io/blog/improving-trace-visibility-and-reproducibility-in-langfuse
Date: 2025-11-11
Excerpt: "The goal is simple: make a trace a complete snapshot of what actually happened. This removes friction when debugging, evaluating, or comparing agent runs."
Context: Langfuse ahora incluye input/output data en cada trace para reproducibilidad.
Confidence: high
```

### 5.3 Pattern: Thread-Level Context Analysis

```
Claim: Para agentes multi-turn, las "threads" agrupan trazas relacionadas por session ID. Analizar threads individuales no es suficiente; hay que ver la conversación completa para detectar failure modes distribuidos. [^25^]
Source: LangChain - AI Agent Observability
URL: https://www.langchain.com/articles/agent-observability
Date: 2025
Excerpt: "Threads connect related traces across conversations and sessions. Analyzing any individual trace in isolation gives an incomplete picture. The failure mode only becomes visible when you see the full conversation trajectory."
Context: Métricas a nivel de thread: resolution rate, escalation frequency, goal completion.
Confidence: high
```

---

## 6. METRICS DASHBOARD: Métricas y KPIs

### 6.1 Pattern: Agent Scorecard (Minimum Viable)

```
Claim: Un scorecard mínimo debe incluir: Task completion ≥92% (30%), Wrong tool rate ≤2% (20%), Tool argument validity ≥98% (10%), P95 latency <2s (10%), Cost per task ≤$0.04 (10%), Safety violations 0 critical (20%). [^26^]
Source: TestingXperts - AI Agent Evaluation
URL: https://www.testingxperts.com/blog/ai-agent-evaluation/
Date: 2026-02-02
Excerpt: "A scorecard makes it easy to compare agents within and across teams over time. Scorecards also set release gates: if safety fails, the agent doesn't ship."
Context: Cada métrica mapeada a SLA con peso ponderado.
Confidence: high
```

### 6.2 Pattern: Four Core Dimensions of Agent Metrics

```
Claim: Las métricas de agentes se organizan en 4 dimensiones: User Experience (satisfaction, adoption, FCR), Cost/Efficiency (tokens, API calls, latency), Tool Execution (accuracy, success rate, efficiency), Error/Recovery (hard error rate, recovery rate, detection time). [^27^]
Source: MindStudio - Measuring AI Agent Success
URL: https://www.mindstudio.ai/blog/ai-agent-success-metrics/
Date: 2026-02-06
Excerpt: "Key experience indicators: User satisfaction scores, Adoption rate, First contact resolution (70-85% benchmark). Essential cost indicators: Token usage, API call volume, Response latency, Resource consumption."
Context: GPT-5.2 achieved 94.5% on tool calling benchmarks.
Confidence: high
```

### 6.3 Pattern: Dashboard Stakeholder-Specific Views

```
Claim: Diferentes stakeholders necesitan diferentes vistas del dashboard: Executives (ROI, cost trends), Product Managers (completion rates, user satisfaction), Technical teams (latency, error rates, tool accuracy). [^28^]
Source: MindStudio - AI Agent Success Metrics
URL: https://www.mindstudio.ai/blog/ai-agent-success-metrics/
Date: 2026-02-06
Excerpt: "Create role-specific dashboards for executives, product managers, and technical teams. Effective dashboards include: Real-time performance, Trend analysis, Comparison views, Drill-down capability."
Context: Revisión recomendada: Daily (operational), Weekly (trends), Monthly (business impact), Quarterly (strategy).
Confidence: high
```

---

## 7. ALERTAS Y NOTIFICACIONES

### 7.1 Pattern: Multi-Level Alert System

```
Claim: LangSmith soporta alertas configurables via webhooks o PagerDuty cuando métricas cruzan umbrales: latency spikes, error rate increases, cost thresholds, feedback score drops. [^29^]
Source: LangSmith Observability Platform
URL: https://www.langchain.com/langsmith/observability
Date: 2025
Excerpt: "Configure alerts via webhooks or PagerDuty when metrics cross thresholds."
Context: Integra con sistemas de alerting existentes. No es un sistema de alerting nativo completo.
Confidence: high
```

### 7.2 Pattern: Billing Alert (Runaway Agent Prevention)

```
Claim: Los "billing alerts" son la última línea de defensa contra agentes runaway. Un agente puede gastar $700 en una noche sin que nadie lo note hasta que el alert de billing dispara a las 6am. [^30^]
Source: BuildMVPfast - AI Agent Timeout & Circuit Breaker Patterns
URL: https://www.buildmvpfast.com/blog/agent-timeout-circuit-breaker-patterns-runaway-ai-workflows-2026
Date: 2026-04-02
Excerpt: "Every single call looked reasonable in isolation. The loop only became visible in aggregate, at 6am, when the billing alert finally fired. That's the thing about runaway AI agents. They don't crash or throw loud errors. They quietly drain your wallet while you sleep."
Context: Recomendación: 5 patterns en <1 hora: step-count ceiling, wall-clock timeout, error classification, kill switch, token budget.
Confidence: high
```

### 7.3 Pattern: ML-Based Anomaly Detection

```
Claim: Los sistemas modernos usan ML-based anomaly detection que aprende patrones únicos del comportamiento del agente, identificando planning breakdowns, prompt injections o runaway tool loops por desviaciones conductuales, no por umbrales estáticos. [^31^]
Source: Galileo - Enterprise Guide to AI Agent Observability
URL: https://galileo.ai/blog/ai-agent-observability
Date: 2026-02-25
Excerpt: "These intelligent detectors identify planning breakdowns, prompt injections, or runaway tool loops based on behavioral deviations rather than static thresholds."
Context: Galileo Luna-2 SLMs escanean cada interacción para intent drift.
Confidence: medium
```

---

## 8. TRANSPARENCY VS OVERWHELM

### 8.1 Pattern: Progressive Disclosure (Collapsible)

```
Claim: El componente Chain of Thought se colapsa a una línea cuando el usuario no quiere ver detalles. Esto evita sobrecarga cognitiva mientras mantiene la transparencia disponible on-demand. [^32^]
Source: shadcn UI - React AI Chain of Thought
URL: https://www.shadcn.io/ai/chain-of-thought
Date: 2025
Excerpt: "The whole thing collapses down to a single line when users don't care about the details."
Context: Patrón de "progressive disclosure": mostrar lo esencial, permitir expandir para detalles.
Confidence: high
```

### 8.2 Pattern: Concise XAI for Trust

```
Claim: Explainable AI debe ofrecer insights concisos, relevantes y accionables, alineados con "mixed-initiative" interface design. El reto es crear XAI usable bajo cognitive overload. [^33^]
Source: arXiv - Mitigating Societal Cognitive Overload in the Age of AI
URL: https://arxiv.org/html/2504.19990v1
Date: 2025-04-28
Excerpt: "Explainable AI for Trust and Calibration: XAI helps users understand AI recommendations and calibrate trust. However, creating usable XAI under cognitive overload remains a challenge. XAI should offer concise, relevant, actionable insights."
Context: Referencia: Miller (2019), Nielsen (1994), Horvitz (1999) sobre mixed-initiative interfaces.
Confidence: high
```

### 8.3 Pattern: Four Failure Modes with Specific UX

```
Claim: Las UX de error AI deben manejar 4 modos de fallo distintos: "I Don't Understand" → clarifying question; "I Can't Do That" → honest + alternative; "Something Went Wrong" → retry button con pre-filled message; "The Response Is Wrong" → regenerate + feedback buttons. [^34^]
Source: AIUX Design Patterns - Error Handling & Fallback Design
URL: https://aiuxdesign.guide/guides/conversational-ui-guide/error-handling-and-fallback-design
Date: 2026-04-02
Excerpt: "The key UX principle: errors should feel like a natural part of the conversation, not a system crash. Style them as messages, not modal dialogs. Never silently swallow errors."
Context: Pattern Honest Uncertainty: "I'm inferring this from..." vale más que 400 palabras confiadas pero incorrectas.
Confidence: high
```

---

## 9. HERRAMIENTAS EVALUADAS

### 9.1 LangSmith

| Capacidad | Detalle |
|---|---|
| Tracing | Full execution tree: LLM calls, tool invocations, reasoning steps |
| Cost tracking | Automático por proveedor; custom cost data; model price map editor |
| Dashboards | Prebuilt + custom; token usage, latency (P50/P99), error rates, cost breakdowns |
| Alerting | Webhooks, PagerDuty integration |
| AI-assisted | Polly (NL queries sobre traces) |
| Frameworks | LangChain, OpenAI SDK, Anthropic, Vercel AI SDK, LlamaIndex |
| Deployment | Cloud, BYOC, self-hosted |

### 9.2 Langfuse

| Capacidad | Detalle |
|---|---|
| Tracing | Trace tree + agent graph; sessions para multi-turn |
| Cost tracking | LLM cost por trace; cost dashboard con roll-up por environment |
| Reproducibility | Input/output data en cada trace; version tags |
| Custom dashboards | Widgets con queries personalizadas |
| Open source | Sí; self-hosted option |

### 9.3 Arize Phoenix

| Capacidad | Detalle |
|---|---|
| Tracing | OpenTelemetry-based; vendor/framework agnostic |
| Evaluation | LLM-as-judge; response y retrieval evals |
| Datasets | Versioned datasets para experimentation |
| Playground | Prompt optimization, model comparison, replay |
| Open source | Sí; 5M+ downloads/mes |

### 9.4 Galileo AI

| Capacidad | Detalle |
|---|---|
| Observability | Agent graph visualization; multi-agent session tracking |
| Evaluation | Luna-2 SLMs (97% cost reduction vs GPT-4; <200ms latency) |
| Runtime protection | Native guardrails; deterministic override/passthrough |
| Failure detection | Insights Engine: auto-clustering de failures; root cause analysis |
| Deployment | SaaS, private VPC, on-premises |

### 9.5 Weights & Biases (Weave)

| Capacidad | Detalle |
|---|---|
| Heritage | ML experiment tracking extended to LLMs via Weave |
| Tracing | Trace table y timeline; nested spans |
| Focus | Experiment tracking, hyperparameter sweeps, model registry |
| Limitation | Basic trace visualization sin dedicated agent analytics |

### 9.6 Evidently AI

| Capacidad | Detalle |
|---|---|
| Focus | ML model monitoring: drift detection, data quality |
| LLM support | Evaluación de token accuracy, output consistency, context adherence |
| Reports | Interactive visualizations; 20+ pre-built drift detection methods |
| Open source | 25M+ downloads |
| Limitation | Más orientado a ML tradicional que a agentes autónomos |

### 9.7 AG-UI Protocol

| Capacidad | Detalle |
|---|---|
| Purpose | Estandarizar agent-to-user communication |
| Events | TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END, TOOL_RESULT, STATE_SNAPSHOT, STATE_DELTA, INTERRUPT, REASONING_START, REASONING_CONTENT, REASONING_END |
| Features | Real-time streaming, tool orchestration with human approval, state sync, thinking steps visibility |
| Status | Open protocol; HTTP/SSE/WebSockets |

---

## 10. CATÁLOGO DE PATTERNS PARA FABERLOOM

### 10.1 Según Tipo de Superficie

#### **Panel de Operador (HMI en planta)**

| # | Pattern | Prioridad | Implementación |
|---|---|---|---|
| 1 | **Agent Status Monitoring** (4 capas: ambient badge, progress panel, attention notification, summary) | MUST | Badge persistente con color de estado; panel expandible con pasos detallados |
| 2 | **Real-Time Progress Indicator** con steps | MUST | Mostrar pasos del agente ("Analizando datos de sensor", "Consultando histórico", "Generando recomendación") |
| 3 | **Error Classification & Routing** (4 tipos) | MUST | Distinguir errores transitorios vs recoverable vs que requieren humano |
| 4 | **Graceful Degradation** (4 niveles) | MUST | AI full → Simplified → Rule-based → Human handoff |
| 5 | **Escalation Ladder** (HITL) | MUST | Tier 1: auto-approve rutina; Tier 2: supervisor; Tier 3: experto dominio |
| 6 | **Visible Thinking** (Expertise-Supportive) | SHOULD | Mostrar razonamiento conciso antes de la respuesta; framing técnico/profesional |
| 7 | **Cost Surfacing** (por operación) | COULD | Mostrar costo estimado de cada operación del agente (para contexto industrial) |

#### **Panel de Supervisor**

| # | Pattern | Prioridad | Implementación |
|---|---|---|---|
| 1 | **Trace Tree Visualization** | MUST | Árbol jerárquico de ejecución con latencia por nodo |
| 2 | **Metrics Dashboard** (4 dimensiones) | MUST | Task completion rate, tool accuracy, latency P95, error rate |
| 3 | **Cost Dashboard** (por environment, por agente) | MUST | Token usage, cost per successful task, trends |
| 4 | **Alert Configuration** (webhooks) | MUST | Umbrales configurables para latency, error rate, cost |
| 5 | **Thread-Level Analysis** (multi-turn) | SHOULD | Ver conversaciones completas del agente con operadores |
| 6 | **AI-Assisted Debugging** (NL queries) | COULD | "Why did the agent recommend this setpoint?" |
| 7 | **Audit Trail** con lazy review | MUST | Toda acción del agente loggeada; review bajo demanda |

#### **Panel de Administrador/IT**

| # | Pattern | Prioridad | Implementación |
|---|---|---|---|
| 1 | **OpenTelemetry Integration** | MUST | Traces exportables a sistemas existentes |
| 2 | **Circuit Breaker Status** | MUST | Visualización de estado de cada circuit breaker |
| 3 | **Retry Policy Configuration** | MUST | Configuración de max attempts, backoff, jitter por servicio |
| 4 | **Model Fallback Chain** | SHOULD | Primary → Fallback 1 → Fallback 2 con visualización de switches |
| 5 | **Anomaly Detection Dashboard** | COULD | ML-based detection de comportamiento anómalo |

### 10.2 Matriz de Implementación por Fase

| Fase | Patterns | Timeline |
|---|---|---|
| **MVP** | Agent Status Monitoring, Real-Time Progress, Error Classification (4 tipos), Graceful Degradation, Escalation Ladder (Tier 1-2) | Semana 1-2 |
| **V1.1** | Trace Tree, Metrics Dashboard, Cost Tracking, Alertas básicas | Semana 3-4 |
| **V1.2** | Visible Thinking (summary), Thread Analysis, Audit Trail completo | Semana 5-6 |
| **V2.0** | AI-Assisted Debugging, Anomaly Detection, Model Fallback visualization | Mes 3+ |

---

## 11. SUMMARY EJECUTIVO

- **Observability es foundational para la confianza en agentes industriales.** LangSmith, Langfuse y Arize Phoenix demuestran que el tracing distribuido (OpenTelemetry) es el estándar emergente. Para FaberLoom, la recomendación es implementar un **Agent Status Monitoring de 4 capas** (ambient badge → progress panel → attention notification → summary) que permita al operador entender qué está haciendo el agente sin monopolizar su atención.

- **El cost surfacing debe ser automático y contextual.** LangSmith demuestra que el tracking de tokens y costos por operación es técnicamente viable. En contexto industrial, el costo por sí solo importa menos que el **"cost per successful task"** — la métrica de negocio real. Mostrar costos en tiempo real al operador puede ser opcional (COULD), pero trackearlos para el supervisor/administrador es MUST.

- **La recuperación de errores requiere 4 capas de defensa.** Los datos de producción muestran que implementar Retry + Fallback + Error Classification + Checkpointing reduce failures de 23% a <2% y el costo por failure en 85%. La recomendación: empezar con **step-count ceiling** (max_steps=25), **wall-clock timeout**, y **error classification** en 4 categorías.

- **Mostrar el razonamiento aumenta la confianza pero requiere diseño cuidadoso.** El paper de ACM DIS 2026 demuestra que el visible thinking mejora trust y engagement significativamente, pero puede crear "expectancy violations" si el thinking promete más de lo que la respuesta entrega. Para FaberLoom (contexto industrial/técnico), el framing **Expertise-Supportive** (lógico, profesional) es más apropiado que el Emotionally-Supportive.

- **La transparencia vs overwhelm se resuelve con progressive disclosure.** Mostrar lo esencial por defecto, permitir expandir para detalles. El protocolo AG-UI demuestra que es factible separar reasoning signals (resúmenes) del raw chain-of-thought, dando al agente control sobre qué exponer.

---

## 12. GAPS IDENTIFICADOS

| # | Gap | Severidad |
|---|---|---|
| 1 | **No se encontraron papers específicos sobre cost surfacing UX en interfaces industriales.** La literatura de "show cost to user" es casi inexistente; hay mucho sobre tracking interno pero poco sobre cómo presentar costos al usuario final de forma útil sin crear ansiedad. | Medium |
| 2 | **Escasez de datos sobre reasoning visibility en contextos industriales/no-emocionales.** El paper de ACM DIS 2026 se enfoca en help-seeking emocional. No hay estudios sobre visible thinking en troubleshooting técnico, mantenimiento predictivo, o optimización de procesos. | Medium |
| 3 | **Integración OT/IT (SCADA/PLC) con observability de agentes.** Hay información sobre Agentic AI + SCADA pero no sobre cómo visualizar el estado del agente dentro de un HMI/SCADA existente. | High |
| 4 | **Latencia de HITL en sistemas industriales de tiempo real.** Los patrones HITL existentes asumen latencia aceptable de segundos/minutos. No hay guidance para HITL sub-100ms en control industrial. | Medium |
| 5 | **Estandarización de métricas de agente para industria manufacturera.** Las métricas existentes (task completion, tool accuracy) son genéricas. No hay un framework de KPIs específico para agentes de mantenimiento, calidad, o scheduling en manufactura. | High |
| 6 | **No se encontraron estudios sobre "carga cognitiva del operador industrial" al monitorear agentes AI.** La literatura de cognitive overload en AI es general; falta research específico para operadores de planta. | Medium |

---

## 13. RECOMENDACIONES

### Inmediatas (Implementar esta semana)

| # | Recomendación | Confidence |
|---|---|---|
| 1 | Implementar **Agent Status Monitoring de 4 capas** con colores de estado: thinking (amarillo pulso), completed (verde), waiting for input (rojo pulso), idle (gris). Usar como referencia AgentsRoom y Devin. [^35^] | High |
| 2 | Definir **max_steps=25** y wall-clock timeout para todos los agentes. Previene 90% de loops infinitos según datos de producción. [^36^] | High |
| 3 | Implementar **Graceful Degradation de 4 niveles**: AI full → Simplified → Rule-based → Human handoff. Comunicar cada transición al usuario. [^37^] | High |

### Corto plazo (2-4 semanas)

| # | Recomendación | Confidence |
|---|---|---|
| 4 | Integrar **OpenTelemetry tracing** con spans para: agent.iteration, agent.decision, agent.tool.name, gen_ai.usage.*. Exportable a LangSmith/Langfuse o sistema existente. [^38^] | High |
| 5 | Implementar **cost tracking automático** por operación (input/output tokens, model name). Visible en panel de supervisor; opcional en panel de operador. [^39^] | High |
| 6 | Crear **Escalation Ladder de 3 tiers**: Auto-approve (rutina, reversible) → Supervisor review (>umbral de riesgo) → Domain expert (irreversible, high-stakes). [^40^] | High |
| 7 | Mostrar **visible thinking con framing Expertise-Supportive**: resumen técnico conciso antes de la respuesta (ej: "Analizando datos de vibración del último mes para identificar anomalías..."). [^41^] | Medium |

### Medio plazo (1-3 meses)

| # | Recomendación | Confidence |
|---|---|---|
| 8 | Implementar **dashboard de métricas** con 4 dimensiones: UX (task completion, FCR), Cost (tokens, cost/task), Tool Execution (accuracy, latency), Error/Recovery (hard error rate, recovery rate). [^42^] | High |
| 9 | Configurar **alertas** para: latency P95 > threshold, error rate > 5%, cost per task > budget, step count > 25 (posible loop). [^43^] | High |
| 10 | Implementar **Audit Trail completo**: toda acción del agente loggeada con contexto (who, what, when, why), visible para compliance y debugging. [^44^] | Medium |
| 11 | Evaluar **circuit breaker pattern** para cada integración externa (APIs, bases de datos) con visualización de estado en dashboard de IT. [^45^] | Medium |

---

## REFERENCIAS

[^1^]: https://www.aiuxdesign.guide/patterns/agent-status-monitoring - Agent Status Monitoring Pattern, AIUX Design, 2026-02-16  
[^2^]: https://docs.ag-ui.com/concepts/reasoning - AG-UI Reasoning Documentation  
[^3^]: https://designsystem.emarsys.net/patterns/ai-guidelines/ai-progress-indicator - Emarsys AI Progress Indicator, 2026-03-13  
[^4^]: https://docs.langchain.com/langsmith/observability - LangSmith Observability Docs  
[^5^]: https://oneuptime.com/blog/post/2026-02-06-trace-ai-agent-execution-flows-opentelemetry/view - OneUptime, OpenTelemetry Tracing, 2026-02-06  
[^6^]: https://www.langchain.com/blog/introducing-polly-your-ai-agent-engineer - LangChain Polly Blog, 2025-12-10  
[^7^]: https://docs.langchain.com/langsmith/cost-tracking - LangSmith Cost Tracking  
[^8^]: https://docs.langchain.com/langsmith/dashboards - LangSmith Dashboards  
[^9^]: https://www.testingxperts.com/blog/ai-agent-evaluation/ - TestingXperts AI Agent Evaluation, 2026-02-02  
[^10^]: https://www.kerno.io/blog/improving-trace-visibility-and-reproducibility-in-langfuse - Kerno Blog, 2025-11-11  
[^11^]: https://www.cloudzero.com/blog/track-openai-spend/ - CloudZero OpenAI Spend, 2026-01-30  
[^12^]: https://docs.praison.ai/docs/best-practices/agent-retry-strategies - PraisonAI Retry Strategies  
[^13^]: https://www.buildmvpfast.com/blog/agent-timeout-circuit-breaker-patterns-runaway-ai-workflows-2026 - BuildMVPfast, 2026-04-02  
[^14^]: https://docs.praison.ai/docs/best-practices/agent-retry-strategies - PraisonAI Retry with Fallback  
[^15^]: https://clearly.design/articles/ai-design-4-designing-for-ai-failures - Clearly.Design, 2025-08-12  
[^16^]: https://dev.to/klement_gunndu/4-fault-tolerance-patterns-every-ai-agent-needs-in-production-jih - Dev.to, 2026-03-02  
[^17^]: https://dev.to/taimoor__z/-human-in-the-loop-hitl-for-ai-agents-patterns-and-best-practices-5ep5 - Dev.to HITL, 2026-04-19  
[^18^]: https://docs.agentbase.sh/primitives/essentials/self-healing - Agentbase Self-Healing  
[^19^]: https://arxiv.org/html/2601.16720v1 - User Perceptions of Visible Thinking in Chatbots, ACM DIS 2026  
[^20^]: https://docs.ag-ui.com/concepts/reasoning - AG-UI Reasoning  
[^21^]: https://www.shadcn.io/ai/chain-of-thought - shadcn Chain of Thought  
[^22^]: https://arxiv.org/html/2601.16720v1 - Visible Thinking Expectancy Violations  
[^23^]: https://langfuse.com/faq/all/what-does-a-good-trace-look-like - Langfuse Trace Structure  
[^24^]: https://www.kerno.io/blog/improving-trace-visibility-and-reproducibility-in-langfuse - Langfuse Reproducibility  
[^25^]: https://www.langchain.com/articles/agent-observability - LangChain Agent Observability  
[^26^]: https://www.testingxperts.com/blog/ai-agent-evaluation/ - TestingXperts Scorecard  
[^27^]: https://www.mindstudio.ai/blog/ai-agent-success-metrics/ - MindStudio Agent Metrics, 2026-02-06  
[^28^]: https://www.mindstudio.ai/blog/ai-agent-success-metrics/ - MindStudio Dashboard Views  
[^29^]: https://www.langchain.com/langsmith/observability - LangSmith Alerts  
[^30^]: https://www.buildmvpfast.com/blog/agent-timeout-circuit-breaker-patterns-runaway-ai-workflows-2026 - Runaway Agent Prevention  
[^31^]: https://galileo.ai/blog/ai-agent-observability - Galileo Anomaly Detection  
[^32^]: https://www.shadcn.io/ai/chain-of-thought - shadcn Collapsible CoT  
[^33^]: https://arxiv.org/html/2504.19990v1 - Mitigating Societal Cognitive Overload  
[^34^]: https://aiuxdesign.guide/guides/conversational-ui-guide/error-handling-and-fallback-design - AIUX Error Handling  
[^35^]: https://agentsroom.dev/features/agent-status-tracking - AgentsRoom Status Tracking  
[^36^]: https://www.buildmvpfast.com/blog/agent-timeout-circuit-breaker-patterns-runaway-ai-workflows-2026 - Step Count Ceiling  
[^37^]: https://clearly.design/articles/ai-design-4-designing-for-ai-failures - Graceful Degradation  
[^38^]: https://oneuptime.com/blog/post/2026-02-06-trace-ai-agent-execution-flows-opentelemetry/view - OpenTelemetry Agent Tracing  
[^39^]: https://docs.langchain.com/langsmith/cost-tracking - LangSmith Cost Tracking  
[^40^]: https://dev.to/taimoor__z/-human-in-the-loop-hitl-for-ai-agents-patterns-and-best-practices-5ep5 - HITL Escalation Ladder  
[^41^]: https://arxiv.org/html/2601.16720v1 - Expertise-Supportive Visible Thinking  
[^42^]: https://www.mindstudio.ai/blog/ai-agent-success-metrics/ - Agent Metrics Dashboard  
[^43^]: https://www.langchain.com/langsmith/observability - LangSmith Alert Configuration  
[^44^]: https://galileo.ai/blog/best-llm-monitoring-solutions-enterprise - Enterprise Audit Trail  
[^45^]: https://dev.to/klement_gunndu/4-fault-tolerance-patterns-every-ai-agent-needs-in-production-jih - Circuit Breaker Pattern  

---

*Documento generado a partir de 25+ búsquedas independientes. Última actualización: Julio 2025.*
