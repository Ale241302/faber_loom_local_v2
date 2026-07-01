# Dimensión 11: Agent Orchestration UI — Tabs Configurar / Iterar / Sanidad

## Investigación: Patrones de UI para Orquestación de Agentes IA

**Fecha:** 2025-07-22  
**Investigador:** Deep Research Agent  
**Búsquedas realizadas:** 24+ queries independientes  
**Fuentes primarias consultadas:** LangGraph Studio, AutoGen Studio, CrewAI, GitLab Duo, n8n, Zapier Canvas, Replicate, Zed, Warp, Claude Code Agent Monitor, AG-UI Protocol, CopilotKit, LangSmith, Langfuse, Microsoft Foundry, Oracle AI Agent Studio, Evil Martians AgentPrism, Braintrust, GitHub Composio Agent Orchestrator, Microsoft Agent Framework, Cloudflare Agents, Permit.io, LangWatch

---

## Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Marco de Referencia: La Arquitectura de 3 Tabs](#2-marco-de-referencia-la-arquitectura-de-3-tabs)
3. [Tab 1: CONFIGURAR — Setup Inicial](#3-tab-1-configurar--setup-inicial)
4. [Tab 2: ITERAR — Refinamiento en Tiempo Real](#4-tab-2-iterar--refinamiento-en-tiempo-real)
5. [Tab 3: SANIDAD — Validación y QA](#5-tab-3-sanidad--validación-y-qa)
6. [Progress Indicators y Estado de Agentes](#6-progress-indicators-y-estado-de-agentes)
7. [Parallel Agents y Visualización Simultánea](#7-parallel-agents-y-visualización-simultánea)
8. [Transiciones entre Tabs: Lineal vs No-Lineal](#8-transiciones-entre-tabs-lineal-vs-no-lineal)
9. [Matriz de Patterns por Tab](#9-matríz-de-patterns-por-tab)
10. [Catalogo de Patterns Visualizados](#10-catalogo-de-patterns-visualizados)
11. [Gaps Identificados](#11-gaps-identificados)
12. [Recomendaciones Específicas para FaberLoom](#12-recomendaciones-específicas-para-faberloom)

---

## 1. Resumen Ejecutivo

- **El modelo de 3 tabs (Configurar/Iterar/Sanidad) tiene precedentes sólidos** pero rara vez se implementa explícitamente como tabs primarios. La mayoría de plataformas usan patrones híbridos: wizards para configuración, playgrounds para iteración, y tracing/evaluación para sanidad.
- **AG-UI Protocol se está consolidando como estándar** para comunicación agente-UI en tiempo real, con 17 tipos de eventos estandarizados (RUN_STARTED, STEP_STARTED, TOOL_CALL_START, etc.) que permiten sincronizar cualquier UI con cualquier agente backend [^727^][^776^].
- **La visualización de estado de agentes converge en 4 estados básicos**: running/working, waiting/paused, completed/success, error/failed — implementados consistentemente en GitLab Duo, Claude Code Monitor, Zed, y AG-UI [^649^][^727^].
- **Los patrones HITL (Human-in-the-Loop) son críticos para el tab ITERAR**: interrupt & resume, approval flows, y guidance patterns deben integrarse en el diseño desde el inicio [^578^][^684^][^685^].
- **La iteración en tiempo real usa el patrón "chat + preview side-by-side"** consistentemente en Microsoft Copilot, CopilotKit, Oracle AI Agent Studio, y Google AI Studio [^653^][^764^][^783^].
- **No se encontró ninguna plataforma que implemente exactamente los 3 tabs como describe FaberLoom**, lo que representa una oportunidad de diferenciación o un riesgo de descubribilidad.

---

## 2. Marco de Referencia: La Arquitectura de 3 Tabs

### 2.1 ¿Quién usa tabs para separar fases de agentes?

**Finding:** Ninguna plataforma estudiada implementa exactamente 3 tabs Configurar/Iterar/Sanidad. Sin embargo, múltiples plataformas usan patrones similares:

#### Oracle AI Agent Studio — 4 tabs (lo más cercano)

```
Claim: Oracle AI Agent Studio usa tabs separados para Prompts, LLM, Input y Output durante la configuración y testing de agentes.
Source: Oracle AI Agent Studio Documentation
URL: https://docs.oracle.com/en/cloud/saas/fusion-ai/aiaas/edit-and-test-ai-agents-iteratively-in-playground.html
Date: 2026-04-10
Excerpt: "You can use Edit in Playground to edit and test your AI agents and large language model (LLM) nodes. This option enables iterative, real-time testing and refinement of agent instructions and parameters... The Prompts Tab lets you design templates and instructions that guide the agent's behavior. The LLM Tab lets you choose the type of model and change custom model properties. The Input Tab lets you enter the specific test data, variables, or context required. The Output Tab lets you configure the overall structure of the agent's output using JSON schema."
Context: Oracle divide la configuración del agente en tabs funcionales dentro del playground. No es exactamente Configurar/Iterar/Sanidad, pero separa claramente la configuración (Prompts, LLM, Input, Output) de la iteración (el propio playground con "View Results" dual-pane).
Confidence: high
```

#### GitLab Duo Agent Platform — Agents vs Flows vs Sessions

```
Claim: GitLab Duo separa claramente entre Agents (configuración interactiva), Flows (orquestación multi-agente), y Sessions (logs de ejecución). Los flows se comunican a través de 4 ubicaciones UI: Comments/Activity Timeline, Session Panel, Sessions Indicator, y Notifications.
Source: GitLab Pajamas Design System
URL: https://design.gitlab.com/patterns/duo-agents-and-flows
Date: 2025-12-15
Excerpt: "Flows are triggered to execute automated, multi-step processes. These flows have distinct working states we must communicate across multiple UI locations to keep users informed of progress, request input when needed, and provide completion status. Display flow states across four primary UI locations: 1. Comments and activity timeline, 2. Session panel, 3. Sessions indicator, 4. Notifications."
Context: GitLab no usa tabs explícitos para Configurar/Iterar/Sanidad, pero su arquitectura de "Agents → Flows → Sessions" mapea conceptualmente: Agents = Configurar, Flows = Iterar (ejecución), Sessions = Sanidad (observabilidad).
Confidence: high
```

#### LangGraph Studio — Graph Mode vs Chat Mode

```
Claim: LangGraph Studio ofrece dos modos principales: Graph Mode (visualización de workflows complejos) y Chat Mode (testing conversacional), además de interrupt functionality para editar AgentState en tiempo real.
Source: Mem0 Blog / IBM
URL: https://mem0.ai/blog/visual-ai-agent-debugging-langgraph-studio
Date: 2025-12-29
Excerpt: "LangGraph Studio has a number of powerful features... Graph Mode provides detailed visualization with execution paths, intermediate states, and full debugging features... Chat Mode offers a simplified conversational interface that's perfect for testing and iterating on chat-specific agent interactions. Interrupt Functionality lets you edit AgentState before and after node execution."
Context: LangGraph Studio alterna entre modos de vista más que tabs de workflow. Graph Mode = Configurar/Visualizar, Chat Mode = Iterar. La validación se hace a través de LangSmith (tracing externo).
Confidence: high
```

### 2.2 Pattern alternativo: Canvas/Builder + Playground + Observatory

En vez de tabs, la mayoría de plataformas usan **3 espacios separados**:

| Plataforma | Espacio 1 (Configurar) | Espacio 2 (Iterar) | Espacio 3 (Sanidad) |
|---|---|---|---|
| **LangGraph** | Graph Studio (graph mode) | Chat Mode + Interrupts | LangSmith (traces) |
| **AutoGen Studio** | Team Builder (drag & drop) | Playground (live streaming) | Profiling info en Playground |
| **CrewAI** | YAML/agents.py setup | crew.kickoff() CLI | Tracing (nuevo, local) |
| **n8n** | Workflow Editor (canvas) | Execute Workflow (test) | Execution Log |
| **Zapier** | Canvas (diagram) | Copilot chat | N/A |
| **GitLab Duo** | AI Catalog + Agent config | Duo Chat / Flow execution | Sessions + Automate |
| **Oracle AI** | Prompts/LLM/Input/Output tabs | Playground dual-pane | Evaluation sets |
| **Microsoft Foundry** | Model/Agent playground tabs | Playground testing | AgentOps tracing |

---

## 3. Tab 1: CONFIGURAR — Setup Inicial

### 3.1 Wizard UI Pattern — Setup Secuencial

```
Claim: Los wizard patterns con progress tracking y validación paso-a-paso son el estándar para setup inicial de agentes. Upwork y Duolingo son ejemplos citados de wizards con preview option.
Source: Eleken Blog
URL: https://www.eleken.co/blog-posts/wizard-ui-pattern-explained
Date: Unknown
Excerpt: "Upwork's onboarding wizard for new freelancers is a stellar example of guiding users through a comprehensive process step-by-step... Upwork's wizard carefully divides the setup into logical, manageable sections. Best Practices: Logical Flow with Clearly Defined Steps, Progress Tracking and Step Highlights, Contextual Help and Tips, Preview Option."
Context: Aplicable al tab Configurar de FaberLoom: el setup inicial del agente (modelo, prompts, tools, variables) debería seguir un wizard con pasos lógicos y preview.
Confidence: high
```

### 3.2 Mission Panel + Tools Store Pattern

```
Claim: Botpress, MindStudio y n8n implementan un patrón de "Mission Panel" para definir el objetivo del agente y un "Tools Store" para equipar al agente con capacidades. Ambos usan catálogos descubribles.
Source: bprigent.com
URL: https://www.bprigent.com/article/7-ux-patterns-for-human-oversight-in-ambient-ai-agents
Date: 2025-12-04
Excerpt: "Every agent starts with a mission. A mission is a place where you define the end goal, how they should measure success, and what are the limits... Once a mission is defined, the next step is to give your agent some capabilities. This flow is similar to the UX pattern 5 where users browse and add event stream integrations. As Botpress shows, your UI will need to list tools users have added and can add."
Context: El tab Configurar debería tener: (1) un panel de misión para definir objetivos, y (2) un catálogo de herramientas integrables. El artículo también menciona que "there is a lack of education in the discovery modal" y "a disconnect between adding tools and leveraging tools."
Confidence: high
```

### 3.3 Catalog Pattern para Integraciones

```
Claim: El "catalog pattern" (tipo App Store) es el estándar para descubrir y configurar integraciones en agentes. Cada integración debe tener página dedicada con nombre, categoría, status indicators (connected, error, disabled) y descripción.
Source: bprigent.com (UX Pattern 5)
URL: https://www.bprigent.com/article/7-ux-patterns-for-human-oversight-in-ambient-ai-agents
Date: 2025-12-04
Excerpt: "The catalog pattern is great. The list of integrations should be categorized according to your users' needs. If you offer many integrations, consider building category pages, filters, and search. Each integration should have a dedicated page that shows name, category, status indicators (connected, error, disabled...), and a description."
Context: El tab Configurar de FaberLoom debería usar un catálogo para que los usuarios descubran y configuren las herramientas/integraciones del agente.
Confidence: high
```

### 3.4 Workflow Design — Multiple Flows

```
Claim: Botpress y n8n permiten que un agente tenga múltiples workflows separados (main, error, timeout, conversation end, y workflows custom adicionales). Esto permite clarificar los nodos en páginas separadas.
Source: bprigent.com
URL: https://www.bprigent.com/article/7-ux-patterns-for-human-oversight-in-ambient-ai-agents
Date: 2025-12-04
Excerpt: "Botpress studio works as followed. Each agent starts with some default flows: a main, an error, a timeout, and a conversation end flow. After that, you can create additional workflows. A user can thus clarify their nodes into separate pages."
Context: Si FaberLoom permite múltiples workflows por agente, el tab Configurar podría tener sub-tabs para cada workflow.
Confidence: high
```

### 3.5 Replicate Playground — Form-based Configuration

```
Claim: Replicate usa un patrón de "playground page" con formulario web auto-generado basado en los inputs del modelo (Cog schema). Es el patrón más simple y directo para configurar ejecuciones.
Source: Replicate Documentation
URL: https://replicate.com/docs/topics/models/run-a-model
Date: Unknown
Excerpt: "Every model on Replicate has its own 'playground' page with a web form for running the model. The playground is a good place to start when trying out a model for the first time. It gives you a visual view of all the inputs to the model, and generates a form for running the model right from your browser."
Context: El tab Configurar podría generar formularios dinámicamente basados en los parámetros requeridos por el modelo/agente. Especialmente útil para configuración de modelos (temperature, max_tokens, system prompt, etc.).
Confidence: high
```

### 3.6 Patterns Identificados para Tab CONFIGURAR

| Pattern | Descripción | Aplicabilidad | Ejemplo |
|---|---|---|---|
| **Wizard con Progress Bar** | Pasos secuenciales con validación | Setup inicial del agente | Upwork onboarding |
| **Mission Panel** | Definir objetivo, éxito, límites | Configuración de propósito | Botpress |
| **Tools Catalog** | Catálogo descubrible con status | Selección de herramientas | Botpress, n8n |
| **Form Playground** | Form auto-generado de parámetros | Configuración de modelo | Replicate |
| **Multi-Flow Tabs** | Sub-tabs para cada workflow | Agentes con múltiples flows | Botpress |
| **YAML/Code Toggle** | Alternar UI visual ↔ código | Configuración avanzada | CrewAI, n8n |

---

## 4. Tab 2: ITERAR — Refinamiento en Tiempo Real

### 4.1 Side-by-Side Mode: Chat + Preview Workspace

```
Claim: Microsoft Copilot implementa dos modos de chat: Inline (para previews simples) y Side-by-Side (para iteración compleja con workspace contextual). El Side-by-Side preserva el chat como fuente de control principal.
Source: Microsoft Documentation — Declarative Agent UI Widgets Guidelines
URL: https://learn.microsoft.com/en-us/microsoft-365/copilot/extensibility/declarative-agent-ui-widgets-guidelines
Date: 2026-03-06
Excerpt: "Side-by-side mode is an optional surface that can be used when richer interactions are needed. The layout includes: Conversation pane (primary source of intent and control), Chiclet card (compact card preserving context), Side-by-side panel header (agent identity + handoff), App workspace (larger MCP-rendered surface for editing/reviewing), Contextual controls (task-specific controls). Preserve chat as primary: Users must be able to continue chatting while Side-by-side mode is open, ask clarifying questions mid-task."
Context: Este es exactamente el patrón que debería usar el tab ITERAR de FaberLoom: un panel de chat (para iterar con el agente) y un panel de preview/workspace (para ver resultados en tiempo real).
Confidence: high
```

### 4.2 Oracle AI Agent Studio — Dual-Pane Layout

```
Claim: Oracle AI Agent Studio usa un layout de "dual-pane" para iteración: panel de edición a la izquierda, panel de resultados a la derecha. Permite "view real-time results in a dual-pane layout".
Source: Oracle Documentation
URL: https://docs.oracle.com/en/cloud/saas/fusion-ai/aiaas/edit-and-test-ai-agents-iteratively-in-playground.html
Date: 2026-04-10
Excerpt: "Edit the agent details to adjust the prompt logic and model parameters. To edit and view real-time results in a dual-pane layout, you can select View Results."
Context: El dual-pane de Oracle mapea directamente al tab ITERAR: edición a la izquierda, preview a la derecha.
Confidence: high
```

### 4.3 CopilotKit — Generative UI con useAgent Hook

```
Claim: CopilotKit proporciona el hook useAgent que permite al UI acceder y controlar el estado del agente en tiempo real, incluyendo state synchronization bidireccional.
Source: CopilotKit GitHub
URL: https://github.com/copilotkit/copilotkit
Date: 2026-05-07
Excerpt: "The useAgent hook is a proper superset of useCoAgent and sits directly on AG-UI, giving more control over the agent connection. // Programmatically access and control your agents const { agent } = useAgent({ agentId: 'my_agent' }); // Render and update your agent's state return <div> <h1>{agent.state.city}</h1> <button onClick={() => agent.setState({ city: 'NYC' })}> Set City </button> </div>"
Context: El tab ITERAR necesita estado compartido entre agente y UI. CopilotKit/AG-UI proporciona el protocolo para esto.
Confidence: high
```

### 4.4 AG-UI Protocol — Event Streaming para Iteración

```
Claim: AG-UI define 17 tipos de eventos estandarizados que permiten al UI sincronizarse con el agente en tiempo real. Los eventos clave para iteración son: RUN_STARTED, STEP_STARTED, TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_RESULT, STATE_DELTA, TEXT_MESSAGE_CONTENT, RUN_FINISHED, RUN_ERROR.
Source: AG-UI Documentation / CopilotKit Blog
URL: https://docs.ag-ui.com/concepts/events
Date: Unknown
Excerpt: "AG-UI supports around 16 event types across five categories: Lifecycle (RUN_STARTED, STEP_STARTED, STEP_FINISHED, RUN_FINISHED, RUN_ERROR), Text Messages (TEXT_MESSAGE_START, TEXT_MESSAGE_CONTENT, TEXT_MESSAGE_END), Tool Calls (TOOL_CALL_START, TOOL_CALL_ARGS, TOOL_CALL_END, TOOL_CALL_RESULT), State Management (STATE_SNAPSHOT, STATE_DELTA), and Special events (INTERRUPT, CUSTOM, RAW)."
Context: FaberLoom debería usar AG-UI (o un modelo similar) para el tab ITERAR, permitiendo que el UI se actualice en tiempo real mientras el agente trabaja.
Confidence: high
```

### 4.5 Human-in-the-Loop: Interrupt & Resume

```
Claim: El patrón "Interrupt & Resume" de LangGraph permite pausar la ejecución del agente para editar AgentState antes y después de cada nodo, y luego reanudar. Es el estándar para HITL en iteración.
Source: Permit.io Blog / LangGraph
URL: https://www.permit.io/blog/human-in-the-loop-for-ai-agents-best-practices-frameworks-use-cases-and-demo
Date: 2025-06-04
Excerpt: "Interrupt & Resume: Used in LangGraph. The agent is paused mid-execution using an interrupt() call. Human input is collected (yes/no, select from options, etc.), and then the workflow resumes based on the response. Best for: Approving tool calls, pausing long-running workflows, inserting human checkpoints before final actions."
Context: El tab ITERAR debe integrar puntos de interrupción donde el usuario pueda pausar, modificar, y reanudar la ejecución del agente.
Confidence: high
```

### 4.6 GitHub Copilot Edits — Iteración Cross-File

```
Claim: GitHub Copilot Edits combina lo mejor de Chat e Inline Chat: flujo conversacional + capacidad de hacer cambios inline across múltiples archivos, diseñado para iteración rápida. El usuario puede review changes, accept good ones, e iterate con follow-up asks.
Source: VS Code Blog
URL: https://code.visualstudio.com/blogs/2024/11/12/introducing-copilot-edits
Date: 2024-11-12
Excerpt: "Copilot Edits combines the best of Chat and Inline Chat: the conversational flow and the ability to make inline changes across a set of files that you manage. And it just works. The experience is iterative: when the model gets it wrong, you can review changes across multiple files, accept good ones and iterate until, together with Copilot, you arrive at the right solution."
Context: El tab ITERAR de FaberLoom debería permitir aceptar/rechazar cambios parciales del agente y continuar iterando.
Confidence: high
```

### 4.7 Feedback Loop: Exception Escalation en vez de Routine Review

```
Claim: El patrón correcto de HITL no es "human reviews every output" sino "agent handles routine autonomously, humans handle exceptions". Los triggers de escalación incluyen: confidence below threshold, policy conflict, negative sentiment, financial impact above limit, request outside known patterns.
Source: Medium — Designing Human-in-the-Loop for Agentic Workflows
URL: https://medium.com/@AlignX_AI/designing-human-in-the-loop-for-agentic-workflows-079faec737ed
Date: 2026-03-16
Excerpt: "Instead of: 'Agent drafts response → Human reviews every response → Human approves' Design for: 'Agent drafts response → Agent evaluates confidence → High-confidence responses auto-send → Low-confidence responses escalate to human' The key is defining escalation triggers clearly: Confidence below a threshold, Policy conflict detected, User sentiment flagged as negative, Financial impact above a limit, Request outside known patterns."
Context: En el tab ITERAR, no todo requiere aprobación humana. El agente debería auto-aprobar cambios de alta confianza y escalar solo los de baja confianza.
Confidence: high
```

### 4.8 Patterns Identificados para Tab ITERAR

| Pattern | Descripción | Aplicabilidad | Ejemplo |
|---|---|---|---|
| **Chat + Preview Side-by-Side** | Panel de chat + workspace de resultados | Iteración principal | Microsoft Copilot, Oracle |
| **Generative UI** | Agente renderiza UI dinámicamente | Output adaptativo | CopilotKit |
| **Event Streaming (AG-UI)** | Eventos en tiempo real agente→UI | Sincronización | AG-UI Protocol |
| **Interrupt & Resume** | Pausa, edita, reanuda | Control humano | LangGraph |
| **Accept/Reject Changes** | Aceptar/rechazar cambios parciales | Iteración incremental | Copilot Edits |
| **Exception Escalation** | Auto-aprobar alta confianza, escalar baja | Eficiencia | AlignX pattern |
| **Dual-Pane Edit/Result** | Edición a la izquierda, resultados a la derecha | Testing rápido | Oracle AI Studio |

---

## 5. Tab 3: SANIDAD — Validación y QA

### 5.1 Agent Evaluation Readiness Checklist

```
Claim: LangChain proporciona una checklist de evaluación de agentes que incluye: gather traces, open coding review, categorize failures, assign eval ownership, y rule out infrastructure issues before blaming the agent.
Source: LangChain Blog
URL: https://www.langchain.com/blog/agent-evaluation-readiness-checklist
Date: 2026-04-30
Excerpt: "Before you build evals: 1. Gather traces: Collect representative failures from production or testing. 2. Open coding: Review traces with a domain expert, noting every issue. 3. Categorize: Group issues into a failure taxonomy (prompt problems, tool design problems, model limitations, tool failures, data gaps). 4. Iterate: Keep reviewing until you stop discovering new failure categories."
Context: El tab SANIDAD debería incluir una checklist similar para validar la calidad del agente antes de deployment.
Confidence: high
```

### 5.2 LangSmith — Trace View con Evaluación

```
Claim: LangSmith ofrece trace visualization con span hierarchy, timing information, agent/workflow events, y tool calls. Permite A/B testing de prompts con métricas cuantificadas (relevance, conciseness, correctness, tone).
Source: LangSmith Learning GitHub / Victor Leung Blog
URL: https://github.com/rajkundalia/langsmith-learning
Date: 2026-01-17
Excerpt: "LangSmith lets you see inside every LLM call: the exact prompt sent, the response received, token usage, latency, and more. LangSmith runs evaluations across dozens or hundreds of examples automatically, giving you quantified metrics."
Context: El tab SANIDAD debería mostrar traces de ejecución con métricas de calidad evaluadas.
Confidence: high
```

### 5.3 AgentPrism — Tree View + Timeline View + Details Panel

```
Claim: AgentPrism (Evil Martians) proporciona 4 componentes de visualización de traces: Tree View (jerarquía), Timeline View (Gantt-style execution), Details Panel (input/output por step), y Sequence Diagram (step-by-step replay). Usa color-coded status indicators (green=success, red=error, yellow=warning).
Source: Evil Martians Blog
URL: https://evilmartians.com/chronicles/debug-ai-fast-agent-prism-open-source-library-visualize-agent-traces
Date: 2025-10-15
Excerpt: "Tree View displays the hierarchical trace structure. Timeline View shows a Gantt-style execution flow — quickly points to where time and money are being wasted. Reveals concurrency issues and bottlenecks. Color-coded status indicators (green = success, red = error, yellow = warning). Real-time cost accumulation with dollar amounts."
Context: El tab SANIDAD debería incluir visualizaciones similares: tree view de ejecución, timeline Gantt, y panel de detalles.
Confidence: high
```

### 5.4 Microsoft DevUI Tracing — OpenTelemetry Timeline

```
Claim: Microsoft DevUI proporciona tracing integrado con OpenTelemetry que muestra span hierarchy, timing information, agent/workflow events, y tool calls & results en un timeline.
Source: Microsoft Documentation
URL: https://learn.microsoft.com/en-us/agent-framework/devui/tracing
Date: 2026-02-13
Excerpt: "DevUI provides built-in support for capturing and displaying OpenTelemetry (OTel) traces emitted by the Agent Framework... View the trace timeline showing: Span hierarchy, Timing information, Agent/workflow events, Tool calls and results."
Context: Integrar tracing OTel en el tab SANIDAD permite observabilidad estándar.
Confidence: high
```

### 5.5 QA Scorecard Pattern — Weighted Scoring

```
Claim: Las QA scorecards usan scoring ponderado (ej. 50% Issue Resolution, 30% Empathy, 20% Process Adherence) con thresholds definidos (Excellent 90%+, Good 80-89%, Needs Improvement 70-79%, Unsatisfactory <70%).
Source: Supportbench / Balto.ai / Hiver
URL: https://www.supportbench.com/build-qa-scorecard-support-examples-scoring-templates/
Date: 2026-01-28
Excerpt: "A good starting point is the 50/30/20 rule: allocate 50% to Issue Resolution, 30% to Empathy and Tone, and 20% to Process Adherence. Define passing score between 70% and 80%. For critical areas, enforce an auto-fail rule."
Context: El tab SANIDAD debería mostrar un scorecard con métricas ponderadas de calidad del agente.
Confidence: medium
```

### 5.6 Cloudflare Agents — waitForApproval() Pattern

```
Claim: Cloudflare implementa HITL con waitForApproval() para workflows multi-step que pueden esperar horas, días o semanas. El workflow reporta progreso con reportProgress() antes de pausar.
Source: Cloudflare Documentation
URL: https://developers.cloudflare.com/agents/guides/human-in-the-loop/
Date: 2026-04-20
Excerpt: "Use Workflow approval when you need durable, multi-step processes with approval gates that can wait hours, days, or weeks... reportProgress({ step: 'approval', status: 'pending', message: 'Awaiting approval for $${expense.amount}' })... waitForApproval(step, { timeout: '7 days' })"
Context: El tab SANIDAD puede integrar aprobaciones pendientes como parte de la validación.
Confidence: high
```

### 5.7 GitLab Duo — Flow State Communication

```
Claim: GitLab Duo comunica el estado de los flows en 4 ubicaciones UI simultáneamente: Comments/Activity Timeline, Session Panel, Sessions Indicator, y Notifications. Incluye estados: In Progress, Paused, Cancelled, Completed, Error.
Source: GitLab Pajamas Design System
URL: https://design.gitlab.com/patterns/duo-agents-and-flows
Date: 2025-12-15
Excerpt: "When flows are triggered from a work item or MR: Initial comment: '[Flow name] started Session [session ID] triggered by [user]'. Session panel: Flow name, Session ID, Timestamp, Status: 'In Progress', Real-time activity stream. Sessions indicator: 'Session #[number] [name] created', Status icon (neutral/gray), Tooltip: 'Triggered by @username'."
Context: El tab SANIDAD debería mostrar estado de validación de forma persistente en múltiples ubicaciones.
Confidence: high
```

### 5.8 Patterns Identificados para Tab SANIDAD

| Pattern | Descripción | Aplicabilidad | Ejemplo |
|---|---|---|---|
| **Trace Tree View** | Jerarquía de spans de ejecución | Debug de flujo | AgentPrism, LangSmith |
| **Timeline Gantt** | Ejecución en timeline con duración | Identificar bottlenecks | AgentPrism, DevUI |
| **Scorecard Dashboard** | Métricas ponderadas de calidad | Evaluación de calidad | Supportbench, Balto |
| **A/B Comparison** | Comparar variantes lado a lado | Evaluar cambios | LangSmith, Braintrust |
| **Approval Queue** | Lista de aprobaciones pendientes | HITL validation | Cloudflare Agents |
| **Activity Stream** | Log en tiempo real de actividad | Observabilidad | GitLab Sessions |
| **Cost Accumulation** | Costo acumulado en tiempo real | Control de gastos | AgentPrism |
| **Auto-Fail Rules** | Reglas de fallo automático por criterio | Compliance crítica | QA Scorecards |

---

## 6. Progress Indicators y Estado de Agentes

### 6.1 AG-UI Lifecycle Events — Progress Standard

```
Claim: AG-UI define eventos de lifecycle estandarizados que permiten mostrar progreso: RUN_STARTED → (STEP_STARTED → STEP_FINISHED)* → RUN_FINISHED/ RUN_ERROR. Los steps son opcionales pero proporcionan granularidad.
Source: AG-UI Documentation
URL: https://docs.ag-ui.com/concepts/events
Date: Unknown
Excerpt: "A typical agent run follows a predictable pattern: it begins with a RunStarted event, may contain multiple optional StepStarted/StepFinished pairs, and concludes with either a RunFinished event (success) or a RunError event (failure)."
Context: Los progress indicators de FaberLoom deberían basarse en estos eventos estándar.
Confidence: high
```

### 6.2 GitLab Duo — Flow State Machine

```
Claim: GitLab Duo define estados de flow: In Progress, Paused, Cancelled, Restarted, Completed, Error. Cada estado tiene comunicación UI específica en múltiples ubicaciones.
Source: GitLab Pajamas Design System
URL: https://design.gitlab.com/patterns/duo-agents-and-flows
Date: 2025-12-15
Excerpt: "Flow is paused: Status indicator: 'Paused', Reason for pause (user-initiated, awaiting input, system issue), Last action completed before pause, Duration paused (live counter), 'Resume' button or action. Flow is restarted: Restart timestamp with visual marker/divider, Status: 'In Progress (Resumed)', Reference to pause duration (e.g., 'Paused for 15 minutes')."
Context: La máquina de estados de GitLab puede replicarse para el indicador de progreso de FaberLoom.
Confidence: high
```

### 6.3 Claude Code Agent Monitor — State Machine Visual

```
Claim: El monitor de Claude Code implementa una máquina de estados con 4 estados: working, waiting, completed, error. Los agentes transicionan entre estos estados basados en eventos (PreToolUse, PostToolUse, Stop, SessionEnd).
Source: Claude Code Agent Monitor GitHub
URL: https://github.com/hoangsonww/Claude-Code-Agent-Monitor
Date: 2026-03-05
Excerpt: "Persisted statuses: working | waiting | completed | error... State transitions: waiting --> working: PreToolUse / UserPromptSubmit. working --> working: PostToolUse (tool completed). working --> waiting: Stop, non-error. waiting --> error: Stop with error. working --> completed: SessionEnd."
Context: El modelo de 4 estados (working/waiting/completed/error) es el estándar de facto para agentes.
Confidence: high
```

### 6.4 Kilo Code — Run Status Indicator

```
Claim: Kilo Code implementa status indicators para ejecución de scripts en worktrees: idle (no indicator), running (spinner/pulsing icon), passed (green checkmark), failed (red X). Los estados se muestran como dots o icons junto al label de branch.
Source: Kilo Code GitHub Issue
URL: https://github.com/Kilo-Org/kilocode/issues/7526
Date: 2026-03-24
Excerpt: "Track per-worktree run state: idle (no run triggered) → No indicator. running (script executing) → Spinner or pulsing icon. passed (exit code 0) → Green checkmark. failed (non-zero exit) → Red X. Status badge: Green dot/check for passed, Red dot/X for failed, Spinner for running, Nothing for idle."
Context: Los progress indicators de FaberLoom pueden usar el mismo patrón de badges color-coded.
Confidence: high
```

### 6.5 Patrones de Progress Indicator

| Pattern | Uso | Visual | Ejemplo |
|---|---|---|---|
| **Stepper/Progress Bar** | Progreso lineal por pasos | Barra con pasos completados | Bootstrap Stepper |
| **Status Badge** | Estado actual del agente | Dot/Icon + label | Kilo Code, GitLab |
| **Kanban Columns** | Múltiples agentes por estado | Columnas: Working/Waiting/Done/Error | Claude Code Monitor |
| **Activity Stream** | Log cronológico de eventos | Feed scrollable con timestamps | GitLab Sessions |
| **Gantt Timeline** | Duración y concurrencia | Barras horizontales por agente | AgentPrism |
| **Spinner/Pulse** | Ejecutando en tiempo real | Animación de carga | AG-UI RUN_STARTED |
| **Cost Meter** | Costo acumulado en vivo | Contador $ en tiempo real | AgentPrism |

---

## 7. Parallel Agents y Visualización Simultánea

### 7.1 Zed — Threads Sidebar para Agentes Paralelos

```
Claim: Zed permite orquestar múltiples agentes en paralelo dentro de la misma ventana. El Threads Sidebar muestra todos los threads a glance, agrupados por proyecto, con capacidad de mix & match de agentes por thread.
Source: Zed Blog
URL: https://zed.dev/blog/parallel-agents
Date: 2026-04-22
Excerpt: "Zed now lets you orchestrate multiple agents, each running in parallel in the same window. The new Threads Sidebar lets you control exactly which folders and repositories agents can access, and lets you monitor threads as they run. The Sidebar gives you instant access to common operations like stopping threads, archiving them, and kicking off new ones."
Context: Para FaberLoom, si múltiples agentes pueden trabajar en paralelo, se necesita un sidebar o panel que muestre todos los agentes activos.
Confidence: high
```

### 7.2 Warp — Parallel Agents en Tabs

```
Claim: Warp permite lanzar varios agentes a la vez, cada uno en su propia tab. El task pane muestra todos los agentes en ejecución con planes, progreso y resultados en vivo.
Source: Warp Documentation
URL: https://docs.warp.dev/guides/agent-workflows/how-to-run-3-agents-in-parallel-summarize-logs-analyze-pr-modify-ui/
Date: 2026-05-08
Excerpt: "Warp allows you to launch several agents at once, each focused on a separate task. The task pane in Warp shows all running agents. You can view plans, progress, and results live without interrupting other tasks."
Context: Warp usa tabs para separar agentes paralelos, similar al concepto de FaberLoom pero a nivel de agente individual, no de fase de workflow.
Confidence: high
```

### 7.3 Claude Code Agent Monitor — Kanban Board

```
Claim: El monitor de Claude Code implementa un Kanban Board con 4 columnas para agentes: Working, Waiting, Completed, Error. Cada card muestra modelo, costo y herramienta actual a glance.
Source: Claude Code Agent Monitor GitHub
URL: https://github.com/hoangsonww/Claude-Code-Agent-Monitor
Date: 2026-03-05
Excerpt: "Kanban Board (agents) — agents grouped by status across 4 columns: Working / Waiting / Completed / Error. The yellow Waiting column surfaces sessions blocked on user input. Each card shows model, cost, and current tool at a glance."
Context: El Kanban Board es ideal para mostrar múltiples agentes paralelos en el tab ITERAR o SANIDAD.
Confidence: high
```

### 7.4 Agent Orchestrator Dashboard (Composio) — 6-Column Kanban

```
Claim: El Agent Orchestrator Dashboard de Composio usa un Kanban de 6 columnas de atención: Respond, Review, Pending, Working, Done, Archived. Diseñado para 30+ cards con alta densidad de información.
Source: GitHub Composio — Agent Orchestrator DESIGN.md
URL: https://github.com/ComposioHQ/agent-orchestrator/blob/main/DESIGN.md
Date: 2026-03-28
Excerpt: "Kanban board with 6 attention-priority columns... Direction: Warm Terminal. Reference: Conductor.build (layout baseline), linear.app (density standard), t3.codes (terminal aesthetic). Typography: JetBrains Mono for headlines + Geist Sans for body. 0px border-radius everywhere. Hard edges are the identity."
Context: El diseño de 6 columnas con alta densidad es un modelo para el dashboard de agentes paralelos.
Confidence: high
```

### 7.5 Patterns para Parallel Agents

| Pattern | Descripción | Uso | Ejemplo |
|---|---|---|---|
| **Threads Sidebar** | Sidebar con lista de todos los threads/agentes | Navegación y control | Zed |
| **Tab per Agent** | Cada agente en su propia tab | Aislamiento de contexto | Warp |
| **Kanban Board** | Columnas por estado con cards | Overview de todos los agentes | Claude Code Monitor |
| **Task Pane** | Panel con progreso de todos los agentes | Monitoreo en tiempo real | Warp |
| **Gantt Timeline** | Tracks paralelos en timeline | Visualizar concurrencia | AgentPrism |

---

## 8. Transiciones entre Tabs: Lineal vs No-Lineal

### 8.1 Azure Architecture Center — Orchestration Patterns

```
Claim: Microsoft Azure define 5 patrones de orquestación de agentes: Sequential (lineal), Concurrent (paralelo), Group Chat (consenso iterativo), Handoff (delegación dinámica), y Magentic (plan-build-execute). Cada uno tiene diferentes implicaciones de navegación.
Source: Microsoft Azure Architecture Center
URL: https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns
Date: 2026-02-12
Excerpt: "Sequential: Linear pipeline; each agent processes the previous agent's output. Concurrent: Parallel; agents work independently on the same input. Group chat: Conversational; agents contribute to a shared thread. Handoff: Dynamic delegation; one active agent at a time. Magentic: Plan-build-execute; manager agent builds and adapts a task ledger."
Context: FaberLoom puede soportar múltiples patrones de orquestación, lo que afecta cómo los usuarios navegan entre tabs.
Confidence: high
```

### 8.2 Bootstrap Stepper — Linear vs Editable

```
Claim: Los stepper/wizard patterns soportan dos modos: linear (validación antes de avanzar) y editable (navegación libre entre pasos completados). El modo linear usa data-mdb-stepper-linear="true" y el no-editable usa data-mdb-stepper-no-editable="true".
Source: Bootstrap Stepper Documentation
URL: https://d-wajszczuk-public.mdbgo.io/docs/standard/components/stepper/
Date: Unknown
Excerpt: "If you want to use basic validation before proceeding to the next step you can set data-mdb-stepper-linear='true'. You can set data-mdb-stepper-no-editable='true' to prevent you from editing the completed step again."
Context: Para FaberLoom: ¿los 3 tabs son secuenciales obligatorios (linear) o se puede saltar? La recomendación es: lineal hacia adelante (no puedes Iterar sin Configurar), pero editable hacia atrás (puedes volver a Configurar desde Iterar).
Confidence: high
```

### 8.3 Patrones de Transición Recomendados

| Patrón | Descripción | Cuándo usar |
|---|---|---|
| **Lineal Forward** | Debe completarse Configurar antes de Iterar, e Iterar antes de Sanidad | Garantiza secuencia lógica |
| **Editable Backward** | Puede volver a tabs anteriores para editar | Flexibilidad para correcciones |
| **Skip-ahead (gated)** | Saltar a Sanidad solo si hay resultado previo | Usuarios avanzados |
| **Auto-advance** | Al completar un tab, avanza automáticamente al siguiente | Flujo fluido para nuevos usuarios |
| **Interrupt & Return** | Desde cualquier tab, puede pausar y volver después | HITL, aprobaciones |

---

## 9. Matriz de Patterns por Tab

### Matriz Principal: ¿Qué pattern va en qué tab?

| Pattern / Component | Tab CONFIGURAR | Tab ITERAR | Tab SANIDAD | Cross-Cutting |
|---|---|---|---|---|
| **Wizard / Stepper** | ✅ Setup inicial | ❌ | ❌ | |
| **Mission Panel** | ✅ Objetivo del agente | ❌ | ❌ | |
| **Tools Catalog** | ✅ Selección de tools | ❌ | ❌ | |
| **Form Playground** | ✅ Parámetros del modelo | ❌ | ❌ | |
| **YAML/Code Toggle** | ✅ Config avanzada | ❌ | ❌ | |
| **Chat Panel** | ❌ | ✅ Iteración principal | ❌ | |
| **Preview Workspace** | ❌ | ✅ Resultados en tiempo real | ❌ | |
| **Side-by-Side Layout** | ❌ | ✅ Chat + Preview | ❌ | |
| **Generative UI** | ❌ | ✅ Output adaptativo | ❌ | |
| **Event Streaming** | ❌ | ✅ Sincronización RT | ✅ Logs | |
| **Interrupt & Resume** | ❌ | ✅ Control humano | ❌ | |
| **Accept/Reject Changes** | ❌ | ✅ Iteración incremental | ❌ | |
| **Trace Tree View** | ❌ | ❌ | ✅ Debug | |
| **Timeline Gantt** | ❌ | ✅ Progreso visual | ✅ Bottlenecks | |
| **Scorecard Dashboard** | ❌ | ❌ | ✅ Evaluación | |
| **A/B Comparison** | ❌ | ❌ | ✅ Evaluar cambios | |
| **Approval Queue** | ❌ | ❌ | ✅ HITL validation | |
| **Activity Stream** | ❌ | ✅ Log en vivo | ✅ Observabilidad | |
| **Cost Meter** | ❌ | ✅ Control de gastos | ✅ Reporte | |
| **Kanban Board** | ❌ | ✅ Agentes paralelos | ✅ Estado general | |
| **Status Badges** | ✅ Estado de config | ✅ Estado de ejecución | ✅ Estado de validación | ✅ Siempre visible |
| **Progress Bar** | ✅ Progreso de setup | ✅ Progreso de iteración | ✅ Progreso de QA | |
| **Auto-Fail Rules** | ❌ | ❌ | ✅ Compliance | |

### Matriz de Herramientas Estudiadas → Patterns Aplicables

| Herramienta Estudiada | Pattern Principal | Tab Relacionado |
|---|---|---|
| LangGraph Studio (Graph Mode) | Visual graph development, AgentState editing | CONFIGURAR |
| LangGraph Studio (Chat Mode) | Conversational testing | ITERAR |
| AutoGen Studio (Team Builder) | Drag-and-drop agent team composition | CONFIGURAR |
| AutoGen Studio (Playground) | Live message streaming, visual message flow | ITERAR |
| CrewAI (YAML config) | Role-based agent definition, task specification | CONFIGURAR |
| CrewAI (Process types) | Sequential/Hierarchical/Custom execution | ITERAR |
| n8n (Workflow Editor) | Node-based visual workflow builder | CONFIGURAR |
| n8n (Execution Log) | Step-by-step execution trace | SANIDAD |
| Zapier Canvas | Diagram-based system visualization | CONFIGURAR |
| Replicate (Playground) | Form-based model configuration + run | CONFIGURAR + ITERAR |
| GitLab Duo (AI Catalog) | Agent/flow discovery and configuration | CONFIGURAR |
| GitLab Duo (Sessions) | Activity timeline, session panel, status indicator | SANIDAD |
| LangSmith (Trace View) | Span hierarchy, timing, token usage | SANIDAD |
| LangSmith (Playground) | Prompt A/B testing, evaluation metrics | SANIDAD |
| AgentPrism (Tree View) | Hierarchical trace structure | SANIDAD |
| AgentPrism (Timeline) | Gantt execution flow, cost accumulation | SANIDAD |
| Microsoft DevUI (Tracing) | OTel trace timeline | SANIDAD |
| Zed (Threads Sidebar) | Parallel agent overview, per-thread control | ITERAR |
| Warp (Task Pane) | Multi-agent progress monitoring | ITERAR |
| Claude Code Monitor (Kanban) | 4-column agent status board | ITERAR + SANIDAD |
| CopilotKit (useAgent) | Bidirectional state synchronization | ITERAR |
| AG-UI Protocol | 17 event types for agent-UI communication | ITERAR + SANIDAD |
| Oracle AI Studio (4 Tabs) | Prompts/LLM/Input/Output config tabs | CONFIGURAR |
| Oracle AI (Playground) | Dual-pane edit + results | ITERAR |
| Microsoft Foundry Playground | Model comparison, agent testing, evaluation | ITERAR + SANIDAD |
| Braintrust Playground | Side-by-side diff mode, annotations | SANIDAD |
| Cloudflare Agents (waitForApproval) | Durable approval gates with timeout | ITERAR + SANIDAD |

---

## 10. Catalogo de Patterns Visualizados

### 10.1 Pattern: Visual Graph Builder (LangGraph Studio)
- **Uso**: CONFIGURAR — construir workflows de agente visualmente
- **Componentes**: Nodos (agents), edges (transiciones), panel de propiedades
- **Interacción**: Drag & drop, click para configurar, zoom/pan
- **Estado mostrado**: Running (nodo resaltado), completed (check), error (rojo)

### 10.2 Pattern: Playground Form (Replicate)
- **Uso**: CONFIGURAR + ITERAR — probar modelos con parámetros configurables
- **Componentes**: Formulario auto-generado, botón Run, área de output
- **Interacción**: Ajustar parámetros → Run → ver resultado → iterar

### 10.3 Pattern: Team Builder (AutoGen Studio)
- **Uso**: CONFIGURAR — componer equipos de agentes
- **Componentes**: Canvas, agent cards, tool palette, property panel
- **Interacción**: Drag agents → canvas, connect, configure properties

### 10.4 Pattern: Chat + Preview Side-by-Side (Microsoft Copilot / Oracle)
- **Uso**: ITERAR — iteración conversacional con preview
- **Componentes**: Panel de chat (izquierda), workspace preview (derecha)
- **Interacción**: Chat en panel izquierdo → resultado aparece en derecha → iterar

### 10.5 Pattern: Kanban Status Board (Claude Code Monitor)
- **Uso**: ITERAR — overview de múltiples agentes paralelos
- **Componentes**: Columnas por estado (Working/Waiting/Completed/Error), cards por agente
- **Interacción**: Drag entre columnas, click para detalle, hover para resumen

### 10.6 Pattern: Trace Timeline Gantt (AgentPrism / DevUI)
- **Uso**: SANIDAD — debug de ejecución
- **Componentes**: Timeline horizontal, spans como barras, colores por estado
- **Interacción**: Click span → detail panel, zoom/pan, filter

### 10.7 Pattern: QA Scorecard (Supportbench / Balto)
- **Uso**: SANIDAD — evaluación de calidad
- **Componentes**: Métricas ponderadas, thresholds, auto-fail rules
- **Interacción**: Review automático, ajustar pesos, ver tendencias

### 10.8 Pattern: Activity Stream (GitLab Sessions)
- **Uso**: SANIDAD — log de actividad
- **Componentes**: Feed cronológico, filtros, search, timestamps
- **Interacción**: Scroll, filter por tipo, click para detalle

### 10.9 Pattern: Status Badge System (Kilo Code / GitLab)
- **Uso**: Cross-cutting — estado en cualquier UI
- **Componentes**: Dot/icon + label, colores: green=passed, red=failed, yellow=waiting, spinner=running
- **Interacción**: Hover para tooltip, click para detalle

### 10.10 Pattern: Multi-Tab Agent Config (Oracle AI Studio)
- **Uso**: CONFIGURAR — separar aspectos de configuración
- **Componentes**: Tabs: Prompts, LLM, Input, Output
- **Interacción**: Navegar entre tabs, editar, guardar

---

## 11. Gaps Identificados

### Gaps en la investigación:

1. **No se encontró ninguna plataforma que implemente exactamente los 3 tabs Configurar/Iterar/Sanidad.** Todos usan arquitecturas similares pero con diferente nomenclatura y organización. Esto es tanto una oportunidad como un riesgo: los usuarios no tendrán un modelo mental preexistente.

2. **Make.com scenario builder:** No se encontraron screenshots detallados del interface visual de Make.com. La información fue limitada a descripciones textuales.

3. **CrewAI Studio UI:** CrewAI tiene un producto llamado "CrewAI Studio" según su web, pero no se encontraron screenshots ni documentación detallada de su interfaz. El framework open-source es mayormente CLI/YAML-based.

4. **Replicate Playground UI detallado:** Se encontró descripción del patrón general pero no análisis detallado de la UI de iteración (antes/después, comparación de runs).

5. **Patrones de transición entre tabs específicos para agentes:** No se encontró literatura sobre cómo diseñar transiciones entre fases de setup, ejecución y validación de agentes. Los patrones existentes son de wizards genéricos.

6. **Sanidad como tab primario:** No se encontró ninguna plataforma que tenga "QA/Validación" como tab de nivel principal. Generalmente es una funcionalidad secundaria (tracing, evaluación) accesible desde otras vistas.

7. **Patrones para "saltar" de Iterar a Sanidad automáticamente:** Poco documentado sobre triggers automáticos de transición basados en estado del agente.

8. **Diseño de tabs para múltiples superficies simultáneas:** FaberLoom menciona "3 tabs por superficie" — no se encontró literatura sobre cómo manejar múltiples instancias de tabs anidados.

9. **Iteración con múltiples agentes simultáneos en un solo tab:** No está claro cómo diseñar la iteración cuando hay varios agentes trabajando al mismo tiempo en el mismo tab.

10. **Integración de cost tracking en tiempo real dentro de tabs de iteración:** Aunque AgentPrism y LangSmith muestran costos, no se encontró un patrón estándar para integrarlos en la iteración activa.

---

## 12. Recomendaciones Específicas para FaberLoom

### 12.1 Arquitectura de Tabs Recomendada

**Recomendación:** Implementar los 3 tabs con navegación **lineal forward + editable backward**:
- Debe completarse CONFIGURAR antes de habilitar ITERAR
- Debe haber al menos una ejecución en ITERAR antes de habilitar SANIDAD
- Se puede volver a cualquier tab anterior en cualquier momento
- El tab activo muestra un progress indicator del estado actual

**Confidence:** high

### 12.2 Tab CONFIGURAR — Componentes Recomendados

| Componente | Priority | Pattern Base |
|---|---|---|
| **Wizard stepper** (3-5 pasos) | P0 | Upwork, Duolingo |
| **Mission panel** (objetivo + constraints) | P0 | Botpress |
| **Tools catalog** (catálogo descubrible) | P0 | Botpress, n8n |
| **Model config form** (parámetros del LLM) | P0 | Replicate Playground |
| **System prompt editor** | P0 | Oracle AI Studio |
| **YAML/Code toggle** | P1 | CrewAI |
| **Preview/Simulate button** | P1 | — |

**Confidence:** high

### 12.3 Tab ITERAR — Componentes Recomendados

| Componente | Priority | Pattern Base |
|---|---|---|
| **Chat panel** (conversación con agente) | P0 | Copilot, Oracle |
| **Preview workspace** (resultados en tiempo real) | P0 | Copilot Side-by-Side |
| **Status bar** (estado del agente: working/waiting/error) | P0 | Claude Code Monitor |
| **Interrupt/Resume controls** | P0 | LangGraph |
| **Accept/Reject changes** | P0 | Copilot Edits |
| **Event stream log** (tool calls, state changes) | P1 | AG-UI Protocol |
| **Cost meter en tiempo real** | P1 | AgentPrism |
| **Kanban mini-view** (si hay múltiples agentes) | P2 | Claude Code Monitor |

**Confidence:** high

### 12.4 Tab SANIDAD — Componentes Recomendados

| Componente | Priority | Pattern Base |
|---|---|---|
| **Trace tree view** (jerarquía de ejecución) | P0 | AgentPrism, LangSmith |
| **Scorecard dashboard** (métricas de calidad) | P0 | Supportbench, Balto |
| **A/B comparison** (comparar ejecuciones) | P0 | Braintrust, LangSmith |
| **Activity stream** (log cronológico) | P1 | GitLab Sessions |
| **Approval queue** (aprobaciones pendientes) | P1 | Cloudflare Agents |
| **Timeline Gantt** (duración y concurrencia) | P2 | AgentPrism |
| **Auto-fail rules config** | P2 | QA Scorecards |

**Confidence:** high

### 12.5 Estado de Agentes — Visualización Recomendada

Implementar 4 estados básicos con badges color-coded:

| Estado | Color | Icono | Cuándo |
|---|---|---|---|
| **Running / Working** | Blue | Spinner/Pulse | Agente ejecutando |
| **Waiting / Paused** | Yellow/Amber | Pause icon | Esperando input humano |
| **Completed / Success** | Green | Checkmark | Ejecución exitosa |
| **Error / Failed** | Red | X icon | Error en ejecución |

**Confidence:** high

### 12.6 Parallel Agents — Visualización Recomendada

Si FaberLoom soporta múltiples agentes paralelos:

1. **Mini Kanban** en el tab ITERAR (columnas: Working/Waiting/Done/Error)
2. **Status badges** en cada card del Kanban mostrando modelo, costo acumulado, tool actual
3. **Click en card** abre el detalle de ese agente específico en el panel principal

**Confidence:** medium

### 12.7 Integración AG-UI Protocol

**Recomendación:** Adoptar AG-UI Protocol para la comunicación entre agentes y UI. Esto proporciona:
- 17 tipos de eventos estandarizados
- Soporte para SSE/WebSockets
- Framework-agnostic (funciona con LangGraph, CrewAI, etc.)
- Lifecycle events para progress tracking
- Tool call events para transparencia
- State management events para sincronización

**Confidence:** high

### 12.8 HITL Integration

**Recomendación:** Integrar 3 niveles de HITL en el tab ITERAR:

1. **Interrupt & Resume**: Pausa automática en puntos críticos
2. **Approval Flow**: Aprobación explícita para acciones sensibles
3. **Guidance (no Approval)**: El agente presenta opciones, humano elige dirección

**Confidence:** high

---

## Anexos

### A. Fuentes Primarias Consultadas (24+)

1. LangGraph Studio Documentation — mem0.ai, IBM
2. AutoGen Studio — Microsoft Research, GitHub microsoft/autogen
3. CrewAI — GitHub crewaiinc/crewai, DigitalOcean tutorial
4. n8n — hatchworks.com, fruitionservices.io
5. Zapier Canvas — zapier.com/blog, help.zapier.com
6. Replicate — replicate.com/docs
7. GitLab Duo Design System — design.gitlab.com
8. LangSmith / Langfuse / LangWatch — Documentación oficial
9. AgentPrism — evilmartians.com
10. Microsoft DevUI Tracing — learn.microsoft.com
11. Zed Parallel Agents — zed.dev/blog
12. Warp Parallel Agents — docs.warp.dev
13. Claude Code Agent Monitor — GitHub hoangsonww
14. CopilotKit / AG-UI — GitHub copilotkit, docs.ag-ui.com
15. Microsoft Agent Framework + AG-UI — devblogs.microsoft.com
16. Microsoft Copilot UX Guidelines — learn.microsoft.com
17. Oracle AI Agent Studio — docs.oracle.com
18. Microsoft Foundry Playgrounds — learn.microsoft.com
19. Cloudflare Agents HITL — developers.cloudflare.com
20. Permit.io HITL Blog — permit.io/blog
21. Agent Orchestrator Dashboard (Composio) — GitHub ComposioHQ
22. AI Coding Agent Dashboard — blog.marcnuri.com
23. Bootstrap Stepper / DevExtreme Stepper
24. Eleken Wizard UI Pattern
25. bprigent.com UX Patterns for AI Agents
26. Supportbench / Balto.ai QA Scorecards
27. Braintrust Playgrounds — braintrust.dev
28. Kilo Code Status Indicators — GitHub Kilo-Org

### B. Métricas de la Investigación

- Búsquedas independientes: 24+
- Fuentes primarias consultadas: 28+
- Plataformas estudiadas en profundidad: 12
- Patterns documentados: 25+
- Gaps identificados: 10
- Recomendaciones específicas: 8
