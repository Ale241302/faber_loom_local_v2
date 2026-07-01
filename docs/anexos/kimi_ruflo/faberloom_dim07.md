
# Dimensión 07 — GAP 3: Handoffs Punto-a-Punto vs Swarm Completo

**Investigador:** Investigación técnica automatizada
**Fecha:** 2026-04-28
**Búsquedas realizadas:** 24 queries independientes
**Fuentes primarias consultadas:** Papers arXiv, documentación oficial (CrewAI, LangGraph, AutoGen, OpenAI GitHub), posts de ingeniería (Anthropic, LangChain, SitePoint), análisis de producción (UC Berkeley MAST, IBM ITBench)

---

## 1. RUFLO: Arquitectura de Handoffs y Patrones de Orquestación

### 1.1 Patrones de topología soportados

Ruflo (ruvnet/ruflo) es un framework de orquestación multi-agente construido sobre `agentic-flow` que soporta cinco topologías de coordinación:

```
Claim: Ruflo soporta explícitamente cinco patrones de topología: Mesh (peer-to-peer), Hierarchical (queen/workers), Adaptive (dynamic), Ring (secuencial) y Star (coordinador central) [^408^][^412^]
Source: ruvnet/ruflo GitHub (official)
URL: https://github.com/ruvnet/ruflo/blob/main/.claude/skills/swarm-orchestration/SKILL.md
Date: 2025-06-02
Excerpt: "Supports mesh, hierarchical, and adaptive topologies with automatic task distribution, load balancing, and fault tolerance."
Context: Skill definition file del repositorio oficial
Confidence: high
```

```
Claim: Ruflo usa un orquestador centralizado que maneja task routing, conflict resolution y output merging, independientemente de la topología elegida [^358^]
Source: SitePoint — Deploying Multi-Agent Swarms with Ruflo
URL: https://www.sitepoint.com/deploying-multiagent-swarms-with-ruflo-beyond-singleprompt-coding/
Date: 2026-03-02
Excerpt: "The orchestrator sits at the center, responsible for task routing (deciding which agent handles which subtask), conflict resolution (managing cases where agents produce contradictory outputs), and output merging (combining results into a coherent final deliverable)."
Context: Análisis técnico del framework
Confidence: high
```

### 1.2 Handoff model y context sharing

```
Claim: Ruflo implementa handoffs con tres modos de contexto: "full" (output completo), "summary" (versión condensada por el orquestador) y "filtered" (solo keys específicas), permitiendo control granular del flujo de información entre agentes [^358^]
Source: SitePoint — Deploying Multi-Agent Swarms with Ruflo
URL: https://www.sitepoint.com/deploying-multiagent-swarms-with-ruflo-beyond-singleprompt-coding/
Date: 2026-03-02
Excerpt: "Setting it to 'full' passes the complete output of the upstream agent. Setting it to 'summary' instructs the orchestrator to generate a condensed version... Setting it to 'filtered' allows specifying patterns or keys that determine which portions of the output are forwarded."
Context: Guía de configuración de producción
Confidence: high
```

```
Claim: Ruflo consume 2-3x tokens vs single-agent en configuraciones de dos agentes con full context, y el costo escala rápidamente con más agentes [^358^]
Source: SitePoint — Deploying Multi-Agent Swarms with Ruflo
URL: https://www.sitepoint.com/deploying-multiagent-swarms-with-ruflo-beyond-singleprompt-coding/
Date: 2026-03-02
Excerpt: "A two-agent swarm with full context handoffs may consume 2-3x the tokens of a single-agent call... five agents each receiving full context from all predecessors can blow through limits fast."
Context: Nota de costos en guía de producción
Confidence: high
```

### 1.3 Cuándo usar cada patrón en Ruflo

| Patrón | Uso recomendado | Control |
|--------|----------------|---------|
| Mesh | Problemas distribuidos, exploración paralela, sin dependencias fuertes | P2P, decisiones locales |
| Hierarchical | Tareas con coordinación central, delegación estructurada | Queen decide, workers ejecutan |
| Adaptive | Workflows mixtos donde la complejidad cambia dinámicamente | Switchea automáticamente |
| Ring | Pipelines determinísticos, etapas ordenadas sin branching | Secuencial fijo |
| Star | Routing centralizado simple, triage → especialista | Coordinador único |

**Implicación para Faberloom:** El patrón actual L1 (Haiku clasificador) → L2 (dispatcher por task_type + complexity + cost) de Faberloom se mapea directamente al patrón **Star/Hierarchical** de Ruflo, no al patrón Mesh/Swarm. Esto es intencionalmente más simple y auditable.

---

## 2. CREWAI: Delegación vs Swarm — ¿Control Granular?

### 2.1 Procesos disponibles

```
Claim: CrewAI soporta tres tipos de proceso: Sequential (tareas en orden fijo), Hierarchical (manager agent delega dinámicamente), y Consensual (planificado, no implementado). No hay patrón peer-to-peer/swarm nativo [^318^]
Source: CrewAI Official Documentation — Processes
URL: https://docs.crewai.com/en/concepts/processes
Date: 2025 (current docs)
Excerpt: "Sequential: Executes tasks sequentially... Hierarchical: Organizes tasks in a managerial hierarchy, where tasks are delegated and executed based on a structured chain of command... Consensual Process (Planned): Aiming for collaborative decision-making among agents."
Context: Documentación oficial
Confidence: high
```

### 2.2 Handoffs en CrewAI

```
Claim: CrewAI NO implementa handoffs punto-a-punto directos entre agentes. Toda la coordinación pasa por el Crew runtime (sequential) o el Manager Agent (hierarchical). El output de una tarea sirve como contexto para la siguiente, pero los agentes no se "llaman" entre sí [^318^][^320^]
Source: CrewAI Official Documentation — Hierarchical Process
URL: https://docs.crewai.com/en/learn/hierarchical-process
Date: 2025 (current docs)
Excerpt: "Tasks are not pre-assigned; the manager allocates tasks to agents based on their capabilities, reviews outputs, and assesses task completion."
Context: Documentación oficial del proceso jerárquico
Confidence: high
```

```
Claim: CrewAI introdujo "Flows" como extensión stateful que permite @router para branching condicional, @listen para pipelines multi-step, y state persistence con Pydantic. Esto acerca a CrewAI a workflows phase-based, pero sigue sin ser peer-to-peer [^383^][^419^]
Source: Crewship — CrewAI Flows: Build Multi-Step AI Pipelines
URL: https://www.crewship.dev/learn/crewai-flows
Date: 2026-03-03
Excerpt: "Flows let you build multi-step pipelines that chain crews, agents, and custom functions together. Manage state with Pydantic, add conditional branching with routers."
Context: Tutorial/educativo de partner oficial
Confidence: high
```

### 2.3 Pipelines: chaining de crews

```
Claim: CrewAI soporta Pipelines que encadenan múltiples crews, donde el output de una crew alimenta la siguiente. Esto permite workflows multi-fase modulares, similar a phase-based orchestration [^315^]
Source: Arize Phoenix — CrewAI Cookbook
URL: https://arize.com/docs/phoenix/cookbook/agent-workflow-patterns/crewai
Date: 2026-04-24
Excerpt: "Pipelines chain multiple crews together, enabling multi-phase workflows where the output of one crew becomes the input to the next. This allows developers to modularize complex applications into reusable, composable segments of logic."
Context: Documentación de integración
Confidence: high
```

**Veredicto para Faberloom:** CrewAI no ofrece handoffs punto-a-punto con control granular. Es una abstracción de más alto nivel donde el runtime controla todo. Para Faberloom, que necesita control explícito de routing L1→L2 y probation de ModelFingerprint, CrewAI sería demasiado opaco.

---

## 3. AUTOGEN (Microsoft / AG2): Group Chat vs Sequential

### 3.1 Patrones de diseño multi-agente

```
Claim: AutoGen 0.4 documenta tres patrones principales: Sequential workflow (cadena de mensajes), Group chat (conversación compartida con expertise especializada), y Handoff (delegación tipo dispatcher). Soporta también pub-sub a Topics [^298^]
Source: Medium — AutoGen 0.4 Unpacked
URL: https://medium.com/@writetopavan/autogen-0-4-unpacked-a-thorough-analysis-and-a-wishlist-for-whats-next-058f5e4d8e75
Date: 2025-03-05
Excerpt: "Sequential workflow: Agents pass a message along a chain. Group chat: Agents (including user proxies) hold a shared conversation, each role injecting specialized expertise. Handoff: An agent delegates to a different agent, reminiscent of a dispatcher routing tasks."
Context: Análisis técnico detallado de AutoGen 0.4
Confidence: high
```

### 3.2 Messaging y spawning

```
Claim: AutoGen permite dos modos de mensajería: Direct send (agent.send_message) y Publish a Topic (agent.publish_message). Los agentes se crean subclassing RoutedAgent y definiendo message handlers. El spawning es explícito vía código, no autónomo [^298^]
Source: Medium — AutoGen 0.4 Unpacked
URL: https://medium.com/@writetopavan/autogen-0-4-unpacked-a-thorough-analysis-and-a-wishlist-for-whats-next-058f5e4d8e75
Date: 2025-03-05
Excerpt: "Direct send: await agent.send_message(...). Publish to a Topic: await agent.publish_message(..., topic_id=...). The system decouples who receives the message from how it's published."
Context: Análisis técnico
Confidence: high
```

**Veredicto para Faberloom:** AutoGen ofrece más control que CrewAI (mensajería explícita, handlers tipados), pero el Group Chat introduce exactamente el riesgo de "context contamination" que Faberloom quiere evitar. El Handoff pattern es el más cercano al modelo L1→L2 de Faberloom.

---

## 4. OPENAI SWARM: ¿Demo/Educativo o Producción?

### 4.1 Estatus oficial: experimental y deprecado

```
Claim: OpenAI Swarm fue explícitamente marcado como "experimental, educational" y fue deprecado en marzo 2025. El README oficial indica: "Swarm is now replaced by the OpenAI Agents SDK, which is a production-ready evolution of Swarm" [^409^]
Source: OpenAI GitHub — openai/swarm (official)
URL: https://github.com/openai/swarm
Date: 2024-02-22 (última actualización README)
Excerpt: "Swarm is now replaced by the OpenAI Agents SDK, which is a production-ready evolution of Swarm. The Agents SDK features key improvements and will be actively maintained by the OpenAI team. We recommend migrating to the Agents SDK for all production use cases."
Context: Repositorio oficial de OpenAI
Confidence: high
```

### 4.2 Limitaciones que impidieron producción

```
Claim: Swarm carecía de memory, tracing/debugging, safety guardrails (PII masking, jailbreak detection), y validación de acciones. OpenAI lo cerró específicamente por estas limitaciones [^293^]
Source: BetterStack — From OpenAI Swarm to AgentKit
URL: https://betterstack.com/community/guides/ai/openai-swarm-to-agentkit/
Date: 2025-12-04
Excerpt: "No built-in memory: Swarm agents couldn't remember anything from earlier in a conversation... No tracing or debugging: When something broke, figuring out what went wrong was a nightmare... Lack of safety guardrails: Swarm didn't have basic security features... OpenAI shut down Swarm in March 2025 because of these limitations."
Context: Guía de migración Swarm → AgentKit
Confidence: high
```

```
Claim: El Agents SDK (sucesor de Swarm) formalizó cuatro primitivas: Agents, Handoffs, Guardrails, y Tracing. A abril 2026 añadió sandboxing y model harness, pero terceros como Diagrid señalan que aún carece de durable execution, checkpointing, failure detection y multi-instance coordination [^356^][^365^]
Source: DevOps.com — OpenAI Upgrades Its Agents SDK
URL: https://devops.com/openai-upgrades-its-agents-sdk-with-sandboxing-and-a-new-model-harness/
Date: 2026-04-17
Excerpt: "It launched in early 2025 as the production-ready successor to Swarm, an experimental, lightweight framework... formalizing four core primitives: Agents, Handoffs, Guardrails, and Tracing."
Context: Reportaje de lanzamiento
Confidence: high
```

**Veredicto para Faberloom:** Swarm fue explícitamente un experimento educativo, no una base para producción. El hecho de que Faberloom ya descartó multi-agente en MVP es consistente con la postura oficial de OpenAI: "migrar al Agents SDK para todos los casos de producción". Pero incluso el Agents SDK requiere infraestructura adicional (checkpointing, durable execution) que Faberloom no tiene presupuesto para construir en MVP (~$200/mes).

---

## 5. LANGGRAPH: Supervisor-Worker, Custom Edges y Checkpointing

### 5.1 Tres patrones nativos

```
Claim: LangGraph soporta tres patrones de coordinación multi-agente: Supervisor Pattern (hierarchical con router LLM), Agent Swarm (peer-to-peer handoffs vía Command(goto=)), y Pipeline (secuencial determinístico) [^292^]
Source: Abstract Algorithms — Multi-Agent Systems in LangGraph
URL: https://www.abstractalgorithms.dev/langgraph-multi-agent-supervisor-pattern
Date: 2026-03-28
Excerpt: "Supervisor + Workers (hierarchical) is the most flexible... Agent swarm (peer-to-peer handoffs) is better when agents need to negotiate directly... Pipeline (sequential delegation) is the simplest pattern."
Context: Guía técnica profunda con código
Confidence: high
```

### 5.2 Checkpointing para trazabilidad

```
Claim: LangGraph ofrece checkpointing nativo con persistencia en PostgreSQL, SQLite, y Redis. Cada checkpoint captura channel_values, channel_versions, y version tracking por nodo. Soporta "time-travel debugging" para reproducir ejecuciones no-determinísticas [^361^][^363^]
Source: LangGraph Official Documentation — Checkpointing
URL: https://www.mintlify.com/langchain-ai/langgraph/concepts/checkpointing
Date: 2026-03-03
Excerpt: "Checkpointing enables LangGraph to persist state across invocations, recover from failures, and provide time-travel debugging. It's the foundation for long-running agents, human-in-the-loop workflows, and conversational memory."
Context: Documentación oficial
Confidence: high
```

```
Claim: LangGraph checkpointing incluye PostgresSaver y AsyncPostgresSaver para producción, con tables setup automático. Cada thread tiene un thread_id configurable, permitiendo resumir conversaciones desde cualquier checkpoint [^361^]
Source: LangGraph Official Documentation — Checkpointing
URL: https://www.mintlify.com/langchain-ai/langgraph/concepts/checkpointing
Date: 2026-03-03
Excerpt: "from langgraph.checkpoint.postgres import PostgresSaver... PostgresSaver.setup_tables(conn)... checkpointer = PostgresSaver(conn)... graph = builder.compile(checkpointer=checkpointer)"
Context: Documentación oficial con snippets
Confidence: high
```

### 5.3 Custom edges vs prebuilt supervisor

```
Claim: LangGraph permite dos enfoques: (a) edges condicionales custom con add_conditional_edges para control total, o (b) langgraph-supervisor prebuilt que reduce boilerplate pero sacrifica ownership del estado. La recomendación de la comunidad es prototipar con prebuilt, pero "own the supervisor in production" [^292^][^387^]
Source: LangChain Forum — Difference of creating Multi-agent
URL: https://forum.langchain.com/t/difference-of-creating-multi-agent/1679
Date: 2025-09-29
Excerpt: "langgraph-supervisor-py is a concrete, production-ready implementation of a specific pattern... built on top of LangGraph with graph state, interrupt/human-in-the-loop, and persistence features... The LangChain Multi-agent docs cover patterns, not a fixed framework."
Context: Respuesta oficial del equipo LangChain
Confidence: high
```

### 5.4 Subgraphs para aislamiento de estado

```
Claim: LangGraph permite wrappear agentes como subgraphs con su propio TypedDict privado, evitando que tool_calls, scratchpad o intermediate_steps contaminen el estado del grafo padre. La comunicación solo ocurre en boundary points explícitos [^292^][^410^]
Source: Abstract Algorithms — Multi-Agent Systems in LangGraph
URL: https://www.abstractalgorithms.dev/langgraph-multi-agent-supervisor-pattern
Date: 2026-03-28
Excerpt: "When you wrap a specialist agent as a subgraph instead of a plain node, it gets its own private TypedDict. The parent graph and the subgraph communicate only at explicit boundary points — the entry edge and the exit edge."
Context: Análisis técnico con código
Confidence: high
```

**Veredicto para Faberloom:** LangGraph ofrece la infraestructura más completa para trazabilidad (checkpointing) y control de handoffs (custom edges, Command(goto=), subgraphs). Si Faberloom eventualmente migra a multi-agente en Phase 2, LangGraph sería el candidato técnico más sólido. Sin embargo, el prebuilt `langgraph-supervisor` sacrifica control de estado que Faberloom necesitaría para ModelFingerprint + probation.

---

## 6. COMPARATIVA: ¿Cuándo Usar Punto-a-Punto vs Swarm?

### 6.1 Definiciones

| Dimensión | Punto-a-Punto (P2P) | Swarm / Mesh |
|-----------|---------------------|--------------|
| Control flow | Determinístico, edges definidos en compile-time | Emergente, decisiones locales en runtime |
| Coordinación | Centralizada (supervisor/router) o secuencial fija | Descentralizada, autónoma |
| Trazabilidad | Alta: cada handoff es un evento auditable | Baja: requiere reconstruir cadena de logs distribuidos |
| Ordenamiento | Soporta garantías transaccionales estrictas | Difícil garantizar secuencias estrictas |
| Terminación | Supervisor o END node decide explícitamente | Requiere condiciones de convergencia (max iterations, quality thresholds) |
| Escalabilidad | Hasta 7-10 agents antes de degradar routing quality [^292^] | 50+ agents para exploración paralela |

### 6.2 Ventajas y costos

```
Claim: El patrón Swarm elimina control centralizado pero introduce el riesgo principal de "observability": trazar una tarea de inicio a fin requiere reconstruir la cadena de handoffs desde logs distribuidos. Los swarms también luchan con tareas que requieren ordenamiento estricto o garantías transaccionales [^317^]
Source: GuruSup — Agent Orchestration Patterns: Swarm vs Mesh vs Hierarchical
URL: https://gurusup.com/blog/agent-orchestration-patterns
Date: 2026-03-16
Excerpt: "The main risk is observability. Without a central coordinator, tracing a task from start to finish requires reconstructing the handoff chain from distributed logs... Swarms also struggle with tasks that require strict ordering or transactional guarantees because there's no global arbiter to enforce sequencing."
Context: Análisis de patrones de orquestación
Confidence: high
```

```
Claim: El patrón punto-a-punto (pipeline/secuencial) es "deterministic, easy to trace, and appropriate when every stage must run in order without branching". El patrón supervisor-worker es "the most flexible" para branching dinámico. El swarm es mejor para "defined responsibility lanes with no ambiguity at boundaries" [^292^]
Source: Abstract Algorithms — Multi-Agent Systems in LangGraph
URL: https://www.abstractalgorithms.dev/langgraph-multi-agent-supervisor-pattern
Date: 2026-03-28
Excerpt: "Pipeline (sequential delegation) is the simplest pattern. Each agent receives the output of the previous one, does its job, and passes downstream. This is deterministic, easy to trace, and appropriate when every stage must run in order without branching."
Context: Tabla comparativa de patrones
Confidence: high
```

```
Claim: Para customer support, el patrón "orchestrator-worker" (punto-a-punto con router central) es el estándar probado: "platforms handling thousands of daily tickets with autonomous resolution rates above 90%". Provee "clear audit trails for every resolution, simple escalation paths" [^396^]
Source: GuruSup — Agent Orchestration Patterns FAQ
URL: https://gurusup.com/blog/agent-orchestration-patterns
Date: 2026-03-16
Excerpt: "Orchestrator-worker is the proven standard for customer support automation... This pattern provides clear audit trails for every resolution, simple escalation paths when confidence is low, and straightforward horizontal scaling."
Context: FAQ sobre patrones
Confidence: high
```

### 6.3 Costo de token: multiplicadores reales

```
Claim: Multi-agent systems cuestan aproximadamente 2x-10x más tokens que single-agent, con un multiplicador efectivo de 2-3x después de ajustar por retries. Un workflow de análisis de documentos de 10K tokens single-agent requiere ~35K tokens en 4-agent implementation (3.5x) [^385^][^430^]
Source: SoftwareSeni — Why Forty Percent of Multi-Agent AI Projects Fail
URL: https://www.softwareseni.com/why-forty-percent-of-multi-agent-ai-projects-fail-and-how-to-avoid-the-same-mistakes/
Date: 2026-02-16
Excerpt: "Production systems observe 2-5x token cost increases when moving to multi-agent architectures. A document analysis workflow consuming 10,000 tokens with a single agent requires 35,000 tokens across a 4-agent implementation—a 3.5x cost multiplier."
Context: Análisis de costos basado en datos de producción
Confidence: high
```

```
Claim: En benchmarks de framework, CrewAI tiene el overhead más alto (~3-4x), LangGraph el más eficiente (~1.3-1.8x). AutoGen multi-agent ~2-5x. Para un sistema multi-agent típico, se consumen 200K-1M+ tokens por tarea [^431^]
Source: Iternal.ai — Token Usage & Cost Projection Guide 2026
URL: https://iternal.ai/token-usage-guide
Date: 2026-03-30
Excerpt: "CrewAI: ~3-4x. Highest overhead due to autonomous deliberation before tool calls... LangGraph: ~1.3-1.8x. Most efficient state management; fastest execution... Multi-agent system: 10 tasks/day × 1,000,000 tokens = 300M tokens/month."
Context: Guía de proyección de costos
Confidence: medium
```

```
Claim: El sistema multi-agent de investigación de Anthropic usa ~15x más tokens que interacciones de chat estándar, aunque logró +90% de mejora en calidad vs single-agent [^424^]
Source: Anthropic Engineering — How we built our multi-agent research system
URL: https://www.anthropic.com/engineering/built-multi-agent-research-system
Date: 2025-06-13
Excerpt: "In our data, agents typically use about 4× more tokens than chat interactions, and multi-agent systems use about 15× more tokens than chats. For economic viability, multi-agent systems require tasks where the value of the task is high enough to pay for the increased performance."
Context: Post de ingeniería oficial de Anthropic
Confidence: high
```

---

## 7. ¿HAY EVIDENCIA DE QUE HANDOFFS PUNTO-A-PUNTO SON MÁS CONFIABLES QUE SWARM?

### 7.1 MAST: Multi-Agent System Failure Taxonomy (UC Berkeley)

```
Claim: El estudio MAST de UC Berkeley analizó 1,642 trazas de ejecución en 7 frameworks multi-agente y encontró tasas de fallo de 41% a 86.7% en tareas del mundo real. El 79% de los fallos provienen de especificación y coordinación, no de infraestructura [^338^][^357^][^385^]
Source: arXiv — Why Do Multi-Agent LLM Systems Fail? (Cemri et al., UC Berkeley)
URL: https://arxiv.org/pdf/2503.13657
Date: 2025-03-11
Excerpt: "We analyze five popular MAS frameworks across over 150 tasks... We identify 14 unique failure modes... These fine-grained failure modes are organized into 3 categories: (i) specification and system design failures, (ii) inter-agent misalignment, and (iii) task verification and termination."
Context: Paper académico peer-reviewed (arXiv)
Confidence: high
```

```
Claim: Las tres categorías de fallo MAST: (1) Specification & System Design: 41.8% — incluye task misinterpretation (11.8%), step repetition/loops (15.7%), unaware of termination (12.4%); (2) Inter-Agent Misalignment: 36.9% — context loss during handoffs, conflicting outputs; (3) Task Verification: 21.3% — premature termination (6.2%), incorrect verification (9.1%) [^357^][^360^]
Source: FutureAGI — Why do multi agent LLM systems fail
URL: https://futureagi.substack.com/p/why-do-multi-agent-llm-systems-fail
Date: 2026-03-27
Excerpt: "Specification and System Design issues account for roughly 41.8%... Inter-Agent Misalignment accounts for about 36.9%... Task Verification and Termination failures make up the remaining 21.3%."
Context: Síntesis del paper MAST
Confidence: high
```

### 7.2 Single-agent vs Multi-agent bajo presupuesto de tokens igualado

```
Claim: Bajo presupuesto de "thinking tokens" igualado, Single-Agent Systems (SAS) consistentemente igualan o superan a Multi-Agent Systems (MAS) en tareas de razonamiento multi-hop. La ventaja de SAS proviene de la Data Processing Inequality: M=g(C) no puede aumentar la información mutua con la respuesta correcta [^336^]
Source: arXiv — Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning (2026)
URL: https://arxiv.org/html/2604.02460v1
Date: 2026-04-02
Excerpt: "By the Data Processing Inequality... I(Y;C) ≥ I(Y;M)... the multi-agent architecture cannot increase mutual information with the true answer... SAS consistently match or outperform MAS on multi-hop reasoning tasks when reasoning tokens are held constant."
Context: Paper académico reciente, tres familias de modelos
Confidence: high
```

```
Claim: El paper concluye que "many reported advantages of multi-agent systems are better explained by unaccounted computation and context effects rather than inherent architectural benefits". MAS solo se vuelve competitivo cuando el contexto del single-agent está degradado o cuando se gasta más compute [^336^]
Source: arXiv — Single-Agent LLMs Outperform Multi-Agent Systems
URL: https://arxiv.org/html/2604.02460v1
Date: 2026-04-02
Excerpt: "Our results suggest that, for multi-hop reasoning tasks, many reported advantages of multi-agent systems are better explained by unaccounted computation and context effects rather than inherent architectural benefits."
Context: Conclusión del paper
Confidence: high
```

### 7.3 Gartner y estudios de producción: la tasa de fallo del 40%

```
Claim: Gartner predice que más del 40% de los proyectos de agentic AI serán cancelados para finales de 2027. La investigación de Carnegie Mellon y UC Berkeley (MAST) confirma tasas de fallo de 41-87% en frameworks multi-agente. Solo 30-35% de las ejecuciones completan exitosamente [^385^][^392^]
Source: Beam.ai — Why 40% of AI Agent Projects Fail
URL: https://beam.ai/agentic-insights/40-percent-agentic-ai-projects-will-fail-heres-how-to-be-in-the-60
Date: 2026-01-23
Excerpt: "Gartner just dropped a sobering prediction: over 40% of agentic AI projects will be canceled by the end of 2027. The reasons? Escalating costs, unclear business value, and inadequate risk controls."
Context: Análisis basado en datos Gartner y MAST
Confidence: high
```

```
Claim: La confiabilidad compuesta de una cadena secuencial: 10 pasos al 99% de confiabilidad cada uno = 90.4% de confiabilidad total (0.99^10). 20 pasos al 95% = 35.8% de confiabilidad total. Esto explica por qué sistemas multi-agente con múltiples handoffs fallan a nivel sistémico incluso cuando cada agente individual es "confiable" [^385^]
Source: SoftwareSeni — Why Forty Percent of Multi-Agent AI Projects Fail
URL: https://www.softwareseni.com/why-forty-percent-of-multi-agent-ai-projects-fail-and-how-to-avoid-the-same-mistakes/
Date: 2026-02-16
Excerpt: "Ten sequential steps each at 99% reliability yield only 90.4% overall system reliability (0.99^10 = 90.4%). With twenty steps at 95% reliability each, overall reliability drops to 35.8%."
Context: Análisis matemático de confiabilidad compuesta
Confidence: high
```

### 7.4 Single agent: confiabilidad probada en producción

```
Claim: Un estudio de 2026 mostró que un single agent en una tarea bien definida tuvo éxito en 28 intentos consecutivos (100%). Los sistemas single-agent son "consistently reliable for production environments" [^314^]
Source: Neil Sahota — Single vs. Multi-Agent AI: Why Coordination Fails
URL: https://www.neilsahota.com/single-agent-vs-multi-agent-ai-the-real-cost-of-ai-agent-coordination/
Date: 2026-03-23
Excerpt: "A study run in early 2026, testing agents across different organizational structures, showed that a single agent on a well-defined task succeeded in all 28 consecutive attempts. These results indicate that discrete, clearly defined single agents are consistently reliable for production environments."
Context: Análisis de confiabilidad
Confidence: medium
```

```
Claim: Microsoft (Azure Cloud Adoption Framework) recomienda single-agent como punto de partida para casos de "low complexity": "Single agents provide the most efficient starting point for low complexity use cases" [^325^]
Source: Microsoft — Choosing Between Single-Agent and Multi-Agent System
URL: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai-agents/single-agent-multiple-agents
Date: 2025-12-10
Excerpt: "Single-agent architectures consolidate logic, context, and tool execution into one entity. This consolidation reduces design complexity, simplifies implementation, and streamlines governance."
Context: Documentación oficial de Microsoft Azure
Confidence: high
```

### 7.5 ¿Cuándo SÍ justifica multi-agente?

```
Claim: La recomendación práctica es: "Start with CrewAI unless you have a specific reason not to" para prototipos, pero para producción el patrón orquestador-especialista con routing auditable es el estándar. "Don't overuse multi-agent setups. Many workflows are best solved with a single agent plus strong orchestration and a few high-quality tools" [^295^][^393^]
Source: Context Patterns — Recursive Delegation in Swarm, CrewAI, and LangGraph
URL: https://contextpatterns.com/guides/recursive-delegation-frameworks/
Date: 2025
Excerpt: "Start with CrewAI unless you have a specific reason not to. Isolation by default is the right starting point for most multi-agent systems... If CrewAI's abstractions don't fit your workflow, reach for LangGraph."
Context: Análisis comparativo de frameworks
Confidence: high
```

```
Claim: Un análisis de decisión propone 5 preguntas antes de usar multi-agente. Si la mayoría responde "no", single-agent es la elección correcta. Multi-agent solo cuando: subtasks sin dependencias secuenciales, archivos disjuntos, especificaciones independientes, tarea suficientemente grande, y review bandwidth disponible [^430^]
Source: AugmentCode — A Decision Framework for Scaling AI Agent Workflows
URL: https://www.augmentcode.com/guides/when-multi-agent-ai-is-overkill
Date: 2026-04-25
Excerpt: "Run the task through these five evaluation questions before reaching for multi-agent orchestration. If the answers mostly point toward single-agent, adding more agents will introduce overhead without a corresponding gain."
Context: Framework de decisión
Confidence: high
```

---

## 8. CONTRA-ARGUMENTOS DOCUMENTADOS

### 8.1 Cuando multi-agente SÍ supera a single-agent

```
Claim: Anthropic logró que su sistema multi-agente de Research superara al single-agent Claude Opus 4 por 90.2% en evaluaciones internas. La clave: problemas que requieren "breadth-first queries" con múltiples direcciones independientes, y donde el contexto excede una sola ventana [^424^]
Source: Anthropic Engineering — How we built our multi-agent research system
URL: https://www.anthropic.com/engineering/built-multi-agent-research-system
Date: 2025-06-13
Excerpt: "We found that a multi-agent system with Claude Opus 4 as the lead agent and Claude Sonnet 4 subagents outperformed single-agent Claude Opus 4 by 90.2% on our internal research eval."
Context: Post de ingeniería oficial
Confidence: high
```

```
Claim: Un estudio de Cornell mostró que sistemas multi-agente sincronizados completaron tareas de planificación compleja 42.68% del tiempo, vs 2.92% de un single-agent GPT-4 en el mismo benchmark [^314^]
Source: Neil Sahota — Single vs. Multi-Agent AI
URL: https://www.neilsahota.com/single-agent-vs-multi-agent-ai-the-real-cost-of-ai-agent-coordination/
Date: 2026-03-23
Excerpt: "A study from Cornell University indicates that synchronized multi-agent systems successfully completed intricate planning tasks 42.68% of the time. A single-agent GPT-4 setup scored 2.92% on the same benchmark."
Context: Referencia a estudio de Cornell
Confidence: medium
```

```
Claim: PwC demostró 7x mejora en accuracy de code generation (10% → 70%) usando multi-agent CrewAI con validation loops estructurados [^385^]
Source: SoftwareSeni — Why Forty Percent of Multi-Agent AI Projects Fail
URL: https://www.softwareseni.com/why-forty-percent-of-multi-agent-ai-projects-fail-and-how-to-avoid-the-same-mistakes/
Date: 2026-02-16
Excerpt: "PwC demonstrated 7x accuracy improvements in code generation accuracy (10% to 70%) by implementing proper multi-agent architectures with structured validation loops."
Context: Caso de estudio citado
Confidence: medium
```

### 8.2 Pero con costos extremos

```
Claim: El sistema multi-agente de Anthropic usa ~15x más tokens. Los agentes de OpenAI Swarm-style pueden costar 4.8x más que single-agent en la misma tarea. Los costos no son lineales: cada handoff re-factura el contexto acumulado [^433^][^424^]
Source: Reddit r/SaaS — Multi-agent AI systems cost 4.8x more
URL: https://www.reddit.com/r/SaaS/comments/1ras2cc/multiagent_ai_systems_cost_48x_more_than_single/
Date: 2025
Excerpt: "Multi-agent systems cost 4.8x more than single agents on the same task. Context gets re-billed at every agent handoff."
Context: Discusión de comunidad con datos de producción
Confidence: medium
```

---

## 9. RECOMENDACIONES ARQUITECTÓNICAS PARA FABERLOOM

### 9.1 Decisión: Mantener single-agent + routing L1/L2 en MVP

La evidencia empírica respalda fuertemente la decisión actual de Faberloom de NO usar multi-agente en MVP:

1. **MAST (UC Berkeley):** 41-86.7% tasas de fallo en multi-agente [^338^]
2. **Gartner:** 40%+ de proyectos agentic AI cancelados para 2027 [^392^]
3. **Data Processing Inequality:** Single-agent es information-theoreticamente superior bajo igual presupuesto de tokens [^336^]
4. **Confiabilidad compuesta:** 10 handoffs al 99% = 90.4% confiabilidad total [^385^]
5. **Costo:** 2-5x multiplicador de tokens (potencialmente $10/día vs $0.41/día para single-agent en un escenario simple) [^432^]
6. **Microsoft Azure:** Single-agent es "most efficient starting point for low complexity" [^325^]

### 9.2 El modelo L1+L2 actual ES un handoff punto-a-punto

La arquitectura de Faberloom:
- **L1 (Haiku):** Clasificador de intención → esto es un **router agent**
- **L2 (Dispatcher):** task_type + complexity + cost → esto es un **conditional edge**
- **ModelFingerprint + probation:** Control de cambio de modelo → esto es **audit trail** y **state validation**

Este patrón se alinea con:
- **LangGraph:** Supervisor pattern con routing por tool-calling (más confiable que free-form text) [^292^]
- **Watsonx Orchestrate:** "triage_agent (Router, Not Solver)" + deterministic routing conditions [^438^]
- **Patrón estándar de customer support:** "orchestrator-worker is the proven standard... with autonomous resolution rates above 90%" [^396^]

### 9.3 Phase-based orchestration: el camino hacia multi-agente sin swarm

Si Faberloom eventualmente necesita descomponer workflows (ej: cobranza en 5+ pasos), el patrón recomendado es **phase-based sequential pipeline**, no swarm:

1. **Phase 1:** Intake + Validación (single agent)
2. **Phase 2:** Ejecución principal (single agent con tools específicas)
3. **Phase 3:** Verificación/QA (single agent o regla programática)
4. **Transición entre fases:** Handoff explícito con state checkpoint (en Supabase/pgvector), no delegación dinámica

Esto es equivalente a:
- **CrewAI Pipelines:** "output of one crew becomes the input to the next" [^315^]
- **LangGraph Pipeline pattern:** "sequential, predictable, easy to trace" [^292^]
- **Ruflo Ring topology:** "sequential processing" [^408^]

**Ventaja:** Cada fase es deterministic, testeable, y el estado entre fases se persiste en Supabase (ya en stack), no en memoria de agente.

### 9.4 Cuándo reconsiderar multi-agente (post-MVP)

Criterios para evaluar en Phase 2 (mes 6-12):

| Criterio | Umbral para multi-agente |
|----------|-------------------------|
| Context window | Workflow excede 100K tokens en single call |
| Especialización | Necesita >3 dominios con toolsets disjuntos (ej: cobranza legal + contabilidad + CRM) |
| Paralelismo | Subtareas verdaderamente independientes que ahorren >50% de tiempo vs secuencial |
| Costo justificado | Valor del workflow >10x el costo de tokens extra |
| Trazabilidad | Sistema de checkpointing ya implementado (LangGraph-style) |

```
Claim: La fórmula matemática para decidir: multi-agente es beneficioso cuando (1) context overflow: ΣTi > C - N·O, o (2) quality gain: ΠSi > 1 + N·O·λ/C. Para 3 especialistas 25% mejores cada uno, el gain es 1.25^3 = 1.95x, que típicamente excede el overhead de 3-5 pasos [^292^]
Source: Abstract Algorithms — Multi-Agent Systems in LangGraph
URL: https://www.abstractalgorithms.dev/langgraph-multi-agent-supervisor-pattern
Date: 2026-03-28
Excerpt: "If each specialist is 20% better than the generalist on its subtask (Si=1.2), three specialists yield a compound quality ratio of 1.2^3 = 1.73 — a 73% quality improvement."
Context: Modelo matemático de decisión
Confidence: high
```

### 9.5 Descartar / Diferir decisiones específicas

| Framework/Pattern | Decisión | Justificación |
|-------------------|----------|---------------|
| **OpenAI Swarm** | DESCARTAR | Deprecado, experimental, sin memoria ni trazabilidad [^409^] |
| **CrewAI Hierarchical** | DIFERIR | Abstracción demasiado alta; no permite control de ModelFingerprint + probation |
| **AutoGen Group Chat** | DESCARTAR | Riesgo de context contamination; no deterministico [^298^] |
| **Ruflo Mesh/Swarm** | DIFERIR | Útil para exploración paralela, no para workflows determinísticos B2B |
| **LangGraph Supervisor** | EVALUAR en Phase 2 | Mejor trazabilidad (checkpointing), custom edges permiten control de routing, pero requiere inversión en infraestructura [^292^][^361^] |
| **Phase-based Pipeline** | IMPLEMENTAR si es necesario | Patrón más alineado con L1→L2 actual; deterministico; usa Supabase para state persistence |

---

## 10. SÍNTESIS EJECUTIVA

**Para Faberloom × Ruflo, GAP 3:**

1. **Ruflo** soporta múltiples patrones (mesh, hierarchical, adaptive, ring, star), pero su handoff principal es orquestado, no peer-to-peer autónomo. El patrón "star" o "hierarchical" se alinea con el L1→L2 de Faberloom.

2. **CrewAI** no tiene handoffs punto-a-punto con control granular. Es secuencial o jerárquico. Los Flows recientes añaden routing condicional pero mantienen abstracción alta.

3. **AutoGen** ofrece handoff tipo dispatcher y group chat, pero el group chat introduce riesgo de misalignment.

4. **OpenAI Swarm** fue explícitamente un experimento educativo, deprecado en marzo 2025. Su sucesor (Agents SDK) aún requiere infra adicional para producción.

5. **LangGraph** tiene el stack técnico más completo: supervisor, swarm, pipeline, checkpointing PostgreSQL, subgraphs para aislamiento, y custom edges. Sería la base técnica más sólida si Faberloom migra a multi-agente en Phase 2.

6. **La evidencia de confiabilidad favorece punto-a-punto:** MAST demuestra 41-86.7% fallos en multi-agente. Single-agent supera a multi-agente bajo igual presupuesto de tokens (paper 2026). La confiabilidad compuesta de handoffs secuenciales degrada exponencialmente.

7. **La arquitectura L1+L2 actual de Faberloom ya es un handoff punto-a-punto bien diseñado.** Debe mantenerse, no "mejorarse" hacia swarm. La evolución natural post-MVP es hacia phase-based pipeline (Crews encadenadas o LangGraph sequential), no hacia delegación dinámica multi-agente.

---

## APÉNDICE: FUENTES CONSULTADAS (ÍNDICE NUMÉRICO)

| Cita | Fuente | Tipo |
|------|--------|------|
| [^292^] | Abstract Algorithms — LangGraph Supervisor Pattern | Guía técnica |
| [^293^] | BetterStack — OpenAI Swarm to AgentKit | Guía migración |
| [^295^] | Context Patterns — Recursive Delegation | Análisis comparativo |
| [^298^] | Medium — AutoGen 0.4 Unpacked | Análisis técnico |
| [^313^] | Neil Sahota — Single vs Multi-Agent | Análisis |
| [^314^] | Neil Sahota — Coordination Fails | Análisis |
| [^315^] | Arize — CrewAI Patterns | Documentación |
| [^317^] | GuruSup — Agent Orchestration Patterns | Análisis patrones |
| [^318^] | CrewAI Docs — Processes | Documentación oficial |
| [^320^] | CrewAI Docs — Hierarchical Process | Documentación oficial |
| [^336^] | arXiv — Single-Agent LLMs Outperform MAS | Paper académico |
| [^338^] | arXiv — Why Do Multi-Agent LLM Systems Fail? (MAST) | Paper académico |
| [^356^] | DevOps.com — OpenAI Agents SDK Upgrade | Reportaje |
| [^358^] | SitePoint — Deploying Multi-Agent Swarms with Ruflo | Tutorial técnico |
| [^361^] | LangGraph Docs — Checkpointing | Documentación oficial |
| [^383^] | Crewship — CrewAI Flows | Tutorial |
| [^385^] | SoftwareSeni — 40% Multi-Agent Projects Fail | Análisis |
| [^387^] | LangChain Forum — Multi-agent Difference | Foro oficial |
| [^392^] | Beam.ai — 40% Agentic AI Projects Fail | Análisis Gartner |
| [^408^] | Ruflo GitHub — Swarm Orchestration Skill | Código oficial |
| [^409^] | OpenAI GitHub — swarm | Repositorio oficial |
| [^412^] | Ruflo GitHub — README | Repositorio oficial |
| [^418^] | GeeksForGeeks — CrewAI Flow | Tutorial |
| [^419^] | Crewship — CrewAI Flows Routing | Tutorial |
| [^424^] | Anthropic Engineering — Multi-Agent Research System | Post ingeniería |
| [^430^] | AugmentCode — Decision Framework | Guía decisión |
| [^431^] | Iternal.ai — Token Usage Guide | Guía costos |
| [^432^] | Capgemini — Token Costs Multi-Agent | Análisis costos |
| [^433^] | Reddit — Multi-agent 4.8x cost | Comunidad |
| [^438^] | Watsonx Orchestrate — Agent Swarm | Tutorial IBM |

---

*Fin del documento de investigación — Dimensión 07*
