Autores:
- Eduardo David Solis Zamora
- Trabajo independiente
- Fecha de elaboración: 2026-01-06

## DIMENSIÓN 9 — Multi-Agent Orchestration y Handoff

### 1. Resumen Ejecutivo

Esta investigación analiza el ecosistema de habilidades (*skills*) disponibles para la orquestación de múltiples agentes de inteligencia artificial (IA), el enrutamiento de tareas (*routing*), la transferencia de contexto entre agentes (*handoff*) y la gobernanza de flujos de trabajo. El objetivo es identificar herramientas reales y verificables que puedan ser integradas en los proyectos MWT (Master Workflow Tracker) y FaberLoom, los cuales ya poseen sistemas propios de orquestación (`PLB_ORCHESTRATOR`, `ENT_OPS_STATE_MACHINE`) y composición multi-agente nativa, respectivamente.

El ecosistema de *skills* (principalmente en [skills.sh](https://skills.sh)) presenta un panorama mixto. Si bien existen habilidades maduras para patrones de orquestación de alto nivel (ej. Saga, Flujos de trabajo Temporales) y para la integración de frameworks específicos (ej. LangGraph, CrewAI), la oferta de habilidades puramente enfocadas en la lógica de *routing*, *handoff* con preservación de estado y patrones de "supervisor agent" es limitada y a menudo se encuentra dentro de frameworks más grandes o aplicaciones independientes no estandarizadas como *skills*. Se identificaron 10 *skills* relevantes, 11 *skills* o proyectos descartados por inaplicabilidad o redundancia, y 6 brechas críticas que los proyectos MWT y FaberLoom deberían considerar desarrollar internamente.

### 2. *Skills* Relevantes Encontrados

A continuación, se presentan las *skills* verificadas que presentan un valor potencial para los proyectos MWT y FaberLoom. La evaluación se basa en la relevancia de su funcionalidad para la orquestación, el *handoff* y la gobernanza de agentes.

#### 2.1. Tabla de *Skills* Relevantes

| *Skill* | Repositorio / URL Verificable | Comando de Instalación | Puntuación MWT | Puntuación FaberLoom | Justificación (1 línea) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `swarm-planner` | `am-will/swarms` <br> [GitHub](https://github.com/am-will/swarms) | `npx skills add am-will/swarms` | **ALTO** | **MEDIO** | Planificación con dependencias explícitas y ejecución en oleadas paralelas con un orquestador que mantiene el contexto. Ideal para descomponer tareas grandes en MWT. |
| `parallel-task` | `am-will/swarms` <br> [GitHub](https://github.com/am-will/swarms) | `npx skills add am-will/swarms` | **ALTO** | **MEDIO** | Ejecución de tareas en paralelo con transferencia de contexto (*handoff*) y verificación de trabajo. Complementa directamente a `swarm-planner`. |
| `workflow-orchestration-patterns` | `wshobson/agents` <br> [skills.sh](https://skills.sh/wshobson/agents/workflow-orchestration-patterns) | `npx skills add wshobson/agents --skill workflow-orchestration-patterns` | **MEDIO** | **MEDIO** | Patrones de orquestación distribuida con Temporal, incluyendo Saga, gestión de estado a largo plazo y ejecución paralela. Relevante para procesos empresariales. |
| `saga-orchestration` | `wshobson/agents` <br> [skills.sh](https://skills.sh/wshobson/agents/saga-orchestration) | `npx skills add wshobson/agents --skill saga-orchestration` | **MEDIO** | **BAJO** | Patrones Saga (orquestación y coreografía) para transacciones distribuidas con compensación automática. Útil para flujos de MWT que requieren atomicidad. |
| `on-call-handoff-patterns` | `wshobson/agents` <br> [skills.sh](https://skills.sh/wshobson/agents/on-call-handoff-patterns) | `npx skills add wshobson/agents --skill on-call-handoff-patterns` | **ALTO** | **ALTO** | Patrones de transferencia de guardia (*handoff*) para equipos de agentes, incluyendo preservación de contexto y documentación de incidentes. Altamente relevante para ambos proyectos. |
| `deep-agents-orchestration` | `langchain-ai/langchain-skills` <br> [skills.sh](https://skills.sh/langchain-ai/langchain-skills/deep-agents-orchestration) | `npx skills add langchain-ai/langchain-skills --skill deep-agents-orchestration` | **MEDIO** | **ALTO** | Orquesta subagentes, planifica tareas multi-paso y requiere aprobación humana (*HITL*) para operaciones sensibles. Se integra con el paradigma de LangGraph. |
| `langgraph-human-in-the-loop` | `langchain-ai/langchain-skills` <br> [skills.sh](https://skills.sh/langchain-ai/langchain-skills/langgraph-human-in-the-loop) | `npx skills add langchain-ai/langchain-skills --skill langgraph-human-in-the-loop` | **ALTO** | **ALTO** | Implementa interrupciones en grafos LangGraph para revisión, aprobación o validación humana, y luego reanuda la ejecución. Crítico para gobernanza. |
| `multi-agent-orchestration` | `qodex-ai/ai-agent-skills` <br> [skills.sh](https://skills.sh/qodex-ai/ai-agent-skills/multi-agent-orchestration) | `npx skills add qodex-ai/ai-agent-skills --skill multi-agent-orchestration` | **MEDIO** | **MEDIO** | Coordina agentes especializados con 4 patrones: secuencial, paralelo, jerárquico y consenso. Incluye plantillas para CrewAI, AutoGen, LangGraph y Swarm. |
| `orchestrating-swarms` | `everyinc/compound-engineering-plugin` <br> [skills.sh](https://skills.sh/everyinc/compound-engineering-plugin/orchestrating-swarms) | `npx skills add everyinc/compound-engineering-plugin --skill orchestrating-swarms` | **MEDIO** | **MEDIO** | Orquestación de enjambres (*swarms*) usando el sistema de equipos de Claude Code, con gestión de tareas, mensajes entre agentes y backends de ejecución. |
| `session-handoff` | `softaworks/agent-toolkit` <br> [skills.sh](https://skills.sh/softaworks/agent-toolkit/session-handoff) | `npx skills add softaworks/agent-toolkit --skill session-handoff` | **ALTO** | **ALTO** | Transferencia de sesiones de agente con preservación exhaustiva de contexto, validación de documentos de transferencia y verificación de estado. Soluciona el problema de la ventana de contexto. |
| `swarm` | `boshu2/agentops` <br> [skills.sh](https://skills.sh/boshu2/agentops/swarm) | `npx skills add boshu2/agentops --skill swarm` | **MEDIO** | **MEDIO** | Primitiva de orquestación de enjambres para ejecución paralela. Parte del ecosistema AgentOps que enfatiza la validación y el *bookkeeping*. |
| `handoff` | `boshu2/agentops` <br> [skills.sh](https://skills.sh/boshu2/agentops/handoff) | `npx skills add boshu2/agentops --skill handoff` | **ALTO** | **ALTO** | Patrón de transferencia de control y contexto entre sesiones de agente. Integrado con el ciclo de vida RPI (Research-Plan-Implement) de AgentOps. |
| `state-machine-design` | `melodic-software/claude-code-plugins` <br> [skills.sh](https://skills.sh/melodic-software/claude-code-plugins/state-machine-design) | `npx skills add melodic-software/claude-code-plugins --skill state-machine-design` | **MEDIO** | **BAJO** | Diseño de máquinas de estado finitas y statecharts para modelar ciclos de vida de entidades y flujos de trabajo. Relevante para formalizar la lógica de `ENT_OPS_STATE_MACHINE`. |
| `model-hierarchy` | `zscole/model-hierarchy-skill` <br> [skills.sh](https://skills.sh/zscole/model-hierarchy-skill/model-hierarchy) | `npx skills add zscole/model-hierarchy-skill --skill model-hierarchy` | **MEDIO** | **MEDIO** | Enrutamiento de tareas al modelo de IA más barato que pueda manejarlas. Útil para optimizar costos en flujos multi-agente de alto volumen. |
| `recursive-decomposition` | `massimodeluisa/recursive-decomposition-skill` <br> [skills.sh](https://skills.sh/massimodeluisa/recursive-decomposition-skill/recursive-decomposition) | `npx skills add massimodeluisa/recursive-decomposition-skill --skill recursive-decomposition` | **MEDIO** | **MEDIO** | Descompone tareas de contexto largo (>50k tokens) recursivamente. Útil para orquestar agentes en problemas complejos que exceden la ventana de contexto. |
| `crewai-multi-agent` | `davila7/claude-code-templates` <br> [skills.sh](https://skills.sh/davila7/claude-code-templates/crewai-multi-agent) | `npx skills add davila7/claude-code-templates --skill crewai-multi-agent` | **BAJO** | **MEDIO** | Framework CrewAI para orquestación de agentes autónomos con roles, memoria y herramientas. Menos relevante si ya se usa LangGraph u orquestadores propios. |

#### 2.2. Análisis Detallado de *Skills* Clave

##### 2.2.1. `am-will/swarms` (GitHub)
Esta *skill* es una de las más prometedoras para MWT. Aborda directamente el problema de la orquestación de agentes con un enfoque de "planificación consciente de dependencias".
*   **Funcionamiento**: Se divide en dos fases. Primero, `swarm-planner` investiga la base de código, genera un plan con dependencias explícitas entre tareas y lo revisa con un subagente. Segundo, `parallel-task` ejecuta las tareas en "oleadas" (*waves*), donde todas las tareas sin dependencias pendientes se ejecutan en paralelo. El orquestador mantiene el contexto global y verifica el trabajo de cada oleada antes de proceder.
*   **Instalación**: `npx skills add am-will/swarms`. Nota: El repositorio sugiere que también funciona con Codex, pero requiere habilitar `multi_agents = true` en `~/.codex/config.toml`.
*   **Relevancia para MWT**: La gestión de dependencias y la ejecución en oleadas es un patrón de orquestación robusto que podría complementar o inspirar mejoras en `PLB_ORCHESTRATOR`.

##### 2.2.2. `wshobson/agents` (skills.sh)
Este es un ecosistema masivo (34.6K estrellas en GitHub) con 150 *skills* y 16 orquestadores. Las *skills* individuales son altamente especializadas.
*   **`workflow-orchestration-patterns`**: Se centra en el framework **Temporal** para flujos de trabajo distribuidos y duraderos. Cubre patrones como Saga, entidades de larga duración y fan-out/fan-in. Es ideal para procesos de negocio que deben persistir durante horas o días y recuperarse de fallos.
*   **`saga-orchestration`**: Específicamente para transacciones distribuidas, ofreciendo tanto el patrón de orquestación (coordinador central) como coreografía (event-driven). Automatiza la lógica de compensación en caso de fallos.
*   **`on-call-handoff-patterns`**: Diseñado para equipos de agentes, se centra en la transferencia de responsabilidad. Preserva el estado del incidente, el contexto operativo y las acciones tomadas, lo cual es fundamental para la continuidad operativa.
*   **Instalación**: `npx skills add wshobson/agents --skill <skill-name>`.
*   **Relevancia**: La *skill* de `handoff` es directamente aplicable a FaberLoom, que ya tiene una arquitectura de agentes por rol.

##### 2.2.3. `langchain-ai/langchain-skills` (skills.sh)
Este conjunto de *skills* es la referencia para el ecosistema LangGraph.
*   **`deep-agents-orchestration`**: Implementa un agente profundo (`create_deep_agent()`) que combina tres capacidades: delegación a subagentes (herramienta `task`), planificación con `write_todos`, y aprobación humana (*HITL*). Es un patrón de "supervisor agent" completo.
*   **`langgraph-human-in-the-loop`**: Proporciona la primitiva `interrupt()` para pausar la ejecución de un grafo LangGraph y `Command(resume=...)` para reanudarla. Esto es fundamental para implementar puntos de control de gobernanza donde un humano debe aprobar una acción antes de que continúe el flujo autónomo.
*   **Instalación**: `npx skills add langchain-ai/langchain-skills --skill <skill-name>`.
*   **Relevancia**: Estas *skills* son de alta prioridad para FaberLoom si se busca implementar un orquestador basado en LangGraph con controles de gobernanza robustos.

##### 2.2.4. `softaworks/agent-toolkit/session-handoff` (skills.sh)
Esta *skill* aborda un problema muy específico y crítico: la pérdida de contexto cuando un agente termina una sesión o se agota su ventana de contexto.
*   **Funcionamiento**: Automatiza la creación de un documento de transferencia (*handoff document*) con metadatos del proyecto, historial de git, archivos modificados y un resumen del trabajo. Al reanudar, verifica la "frescura" del documento comparando commits y cambios de archivos.
*   **Instalación**: `npx skills add softaworks/agent-toolkit --skill session-handoff`.
*   **Relevancia**: Es una *skill* de alta utilidad para cualquier proyecto que use agentes de larga duración o multi-sesión, como es el caso de MWT y FaberLoom.

##### 2.2.5. `boshu2/agentops` (skills.sh)
AgentOps es un "sistema operativo" para agentes de código, no solo una *skill* aislada. Sus primitivas de orquestación están integradas en un ciclo de vida más amplio (RPI: Research-Plan-Implement).
*   **`swarm`**: Ejecución paralela de tareas dentro del flujo de trabajo `/crank` o `/rpi`.
*   **`handoff`**: Transferencia de contexto entre sesiones, integrada con el sistema de *bookkeeping* local (`.agents/`) que persiste aprendizajes entre sesiones.
*   **Instalación**: `npx skills add boshu2/agentops --skill <skill-name>`.
*   **Relevancia**: Su enfoque en la persistencia de conocimiento (`learnings.md`, `.agents/`) y la validación antes de envío (`/council`, `/vibe`) lo hace muy atractivo para entornos de producción.

##### 2.2.6. `zscole/model-hierarchy-skill` (skills.sh)
Una *skill* de nicho pero con un valor claro: optimización de costos.
*   **Funcionamiento**: Clasifica las tareas en 3 niveles (Barato, Medio, Premium) y enruta cada tarea al modelo más económico que sea capaz de resolverla. Estima que el 80% del trabajo de agentes es "de limpieza" y no requiere modelos premium.
*   **Instalación**: `npx skills add zscole/model-hierarchy-skill --skill model-hierarchy`.
*   **Relevancia**: En un sistema multi-agente de producción como FaberLoom, donde múltiples agentes pueden estar activos simultáneamente, esta *skill* podría reducir drásticamente los costos de API.

### 3. *Skills* y Proyectos Descartados

Se analizaron varios proyectos y *skills* que, aunque mencionados en la investigación, no son aplicables o están redundantes con respecto a los sistemas existentes en MWT y FaberLoom.

| *Skill* / Proyecto | Razón de Descarte |
| :--- | :--- |
| `obra/superpowers/dispatching-parallel-agents` | **Ya instalado.** Es parte del núcleo de Cowork y no debe ser reinstalado. |
| `anthropic-skills/*` (docx, pdf, pptx, xlsx, schedule, skill-creator) | **Ya instalados.** Son *skills* oficiales de Anthropic ya presentes en el entorno base. |
| `Idun-Group/idun-agent-platform` | **No es una *skill*.** Es una plataforma de gobernanza y despliegue completa (FastAPI + React + PostgreSQL) para agentes LangGraph/ADK. Requiere infraestructura Docker y no se instala como una *skill* de `skills.sh`. Su función es de *hosting* y gobernanza, no de orquestación de lógica de agente. |
| `Charlie85270/Dorothy` | **No es una *skill*.** Es una aplicación de escritorio (Electron/Tauri) para orquestar múltiples agentes CLI en paralelo. Funciona como un *dashboard* y un "Super Agente" externo, pero no es una *skill* que se pueda integrar directamente en el flujo de trabajo de MWT o FaberLoom. |
| `ShunsukeHayashi/agent-skill-bus` | **No está en *skills.sh*.** Es un framework de orquestación basado en npm (`npm install agent-skill-bus`) con un enfoque en la salud operativa y la mejora automática de *skills*. Aunque interesante, su modelo de instalación y arquitectura (DAGs locales, JSONL) no se alinea con el ecosistema estándar de `skills.sh` y requeriría una integración custom significativa. |
| `AnastasiyaW/mclaude` | **No está en *skills.sh*.** Es un proyecto de orquestación multi-sesión para Claude Code con énfasis en la memoria y el *handoff*. Aunque altamente relevante conceptualmente, no se distribuye como una *skill* instalable y su integración sería a nivel de protocolo, no de *skill*. |
| `sanjay3290/ai-skills/deep-research` | **Enfoque incorrecto.** Aunque incluye "agentes", es una *skill* para realizar investigación profunda usando la API de Gemini. No proporciona patrones de orquestación multi-agente, *routing* o *handoff* aplicables a los proyectos. |
| `massimodeluisa/recursive-decomposition-skill` | **Baja aplicabilidad directa.** Aunque útil para descomposición de tareas, su enfoque es puramente algorítmico (procesamiento recursivo de contexto largo) y no cubre la coordinación o el *handoff* entre múltiples agentes especializados. |
| `crewaiinc/skills/*` (getting-started, design-agent) | **Redundante/Framework.** Son *skills* introductorias para el framework CrewAI. Si MWT o FaberLoom ya han decidido no usar CrewAI como base, estas *skills* no aportan valor. La *skill* `crewai-multi-agent` ya cubre el caso de uso general. |
| `mindrally/skills/autogen-development` | **Framework específico.** Es una *skill* para el framework AutoGen de Microsoft. Su utilidad está condicionada a la adopción de AutoGen, lo cual no está indicado en los requerimientos de los proyectos. |

### 4. Brechas Detectadas (*Gaps*)

La investigación revela varias áreas donde el ecosistema de *skills* existente es insuficiente para las necesidades avanzadas de MWT y FaberLoom. Estas brechas representan oportunidades para el desarrollo de *skills* propietarias.

| Nombre Propuesto | Justificación | Para MWT o FaberLoom | Prioridad |
| :--- | :--- | :--- | :--- |
| `mwt-orchestrator-bridge` | **Integración con sistema congelado.** MWT tiene `PLB_ORCHESTRATOR` y `ENT_OPS_STATE_MACHINE` congelados. No existe una *skill* que actúe como puente entre un orquestador moderno (como los patrones de `am-will/swarms`) y un sistema de estado heredado. Se necesita una *skill* que pueda leer/escribir el estado del sistema congelado y traducirlo a primitivas de orquestación modernas. | MWT | **ALTA** |
| `faber-loom-role-router` | **Enrutamiento basado en KB y Tono.** FaberLoom tiene agentes por rol con KB, tono y canal. No existe una *skill* que implemente un *router* inteligente que, dado un *request*, seleccione el agente correcto basándose no solo en la intención, sino también en el alcance de la KB, la autoridad y el canal de comunicación. | FaberLoom | **ALTA** |
| `context-preservation-handoff` | **Handoff con estado de ejecución.** Aunque existen *skills* de *handoff* (ej. `session-handoff`), ninguna maneja la preservación del estado de ejecución de una máquina de estado (como `ENT_OPS_STATE_MACHINE`). Se necesita una *skill* que serialice el estado actual de un flujo de trabajo y lo rehidrate en otro agente, incluyendo variables, puntos de control y decisiones pendientes. | Ambos | **ALTA** |
| `escalation-supervisor` | **Patrón Supervisor con Escalamiento.** Ninguna *skill* implementa un patrón de "supervisor agent" que incluya lógica de escalamiento automático (ej. si un agente falla N veces, escalar a un agente de mayor jerarquía o a un humano). Esto es crítico para FaberLoom. | FaberLoom | **MEDIA** |
| `hito-governance-gate` | **HITL para decisiones de negocio.** Las *skills* de HITL existentes (ej. `langgraph-human-in-the-loop`) se centran en la aprobación técnica de acciones. Se necesita una *skill* específica para pausar flujos y requerir aprobación humana para decisiones de negocio críticas, con un formato de presentación de datos adaptado a FaberLoom. | FaberLoom | **MEDIA** |
| `cross-framework-orchestrator` | **Orquestación agnóstica.** Todas las *skills* de orquestación están atadas a un framework (LangGraph, CrewAI, Temporal). No existe una *skill* que proporcione patrones de orquestación y *handoff* que funcionen de manera agnóstica con múltiples backends o incluso con agentes escritos en diferentes frameworks. | Ambos | **BAJA** |

### 5. Advertencias Técnicas (*Caveats*)

- **Conflictos de Orquestador**: `PLB_ORCHESTRATOR` (MWT) y el sistema nativo de FaberLoom podrían entrar en conflicto con orquestadores externos como `am-will/swarms` o `wshobson/agents`. La adopción de una *skill* de orquestación debe ser estratégica: o se usa como inspiración para mejorar el sistema interno, o se implementa una capa de adaptación (*bridge*).
- **Dependencias de Framework**: *Skills* como `deep-agents-orchestration` y `langgraph-human-in-the-loop` requieren que el proyecto esté construido sobre LangGraph. Su uso en un entorno que no use LangGraph sería inviable o requeriría una reescritura masiva.
- **Instalación de `am-will/swarms`**: Aunque el repositorio de GitHub indica `npx skills add am-will/swarms`, esta *skill* no aparece en los resultados de búsqueda de `skills.sh` cuando se busca por nombre. Esto sugiere que podría estar instalable directamente desde GitHub, pero no estar indexada en el directorio de `skills.sh`, lo cual podría indicar un estado de desarrollo temprano o falta de mantenimiento.
- **Seguridad de `qodex-ai/ai-agent-skills`**: La *skill* `multi-agent-orchestration` tiene una auditoría de seguridad de **Gen Agent Trust Hub** con estado **"Fail"**. Esto debería ser una bandera roja para su uso en producción sin una revisión de seguridad previa.
- **Modelo de Instalación de AgentOps**: `boshu2/agentops` se instala como un *marketplace* de plugins (`claude plugin marketplace add boshu2/agentops`), no como una *skill* individual de `skills.sh`. Esto requiere un paso de instalación adicional y puede no ser compatible con todos los entornos de agente.
- **Soporte de Subagentes**: La ejecución de *swarms* y equipos de agentes (ej. `am-will/swarms`, `everyinc/compound-engineering-plugin`) depende de la capacidad del entorno de agente para generar subagentes. Esto es una característica experimental en algunos runtimes (como Codex) y podría no estar disponible o ser estable en el entorno de MWT/FaberLoom.
- **Persistencia de Estado**: La mayoría de las *skills* de *handoff* se basan en archivos locales (JSON, Markdown). En un entorno distribuido o con múltiples instancias de agentes, esto puede causar problemas de concurrencia o pérdida de datos si no se implementa un backend de estado compartido (como PostgreSQL o Redis).
- **Costos de Modelo Jerárquico**: La *skill* `model-hierarchy` requiere la integración con múltiples proveedores de LLM (DeepSeek, Gemini, Anthropic, etc.). La gestión de múltiples claves de API y la lógica de fallback entre proveedores añade complejidad operativa.

### 6. Conclusión y Recomendaciones

Para los proyectos MWT y FaberLoom, el ecosistema de *skills* ofrece herramientas valiosas, pero no una solución completa.

1.  **Adopción Inmediata (Alto Valor, Bajo Riesgo)**:
    *   **`softaworks/agent-toolkit/session-handoff`**: Es una *skill* madura y directamente aplicable para resolver el problema de la continuidad entre sesiones de agente.
    *   **`zscole/model-hierarchy-skill`**: Si los costos de API son una preocupación, esta *skill* ofrece un mecanismo de optimización rápido de implementar.

2.  **Evaluación Estratégica (Alto Valor, Riesgo/Complejidad Media)**:
    *   **`am-will/swarms`**: Ideal para mejorar la capacidad de descomposición y ejecución paralela de MWT. Se recomienda un *PoC* (Prueba de Concepto) para validar la compatibilidad con `PLB_ORCHESTRATOR`.
    *   **`langchain-ai/langchain-skills` (especialmente `deep-agents-orchestration` y `langgraph-human-in-the-loop`)**: Si FaberLoom decide adoptar LangGraph como base para su orquestador, estas *skills* son de alta prioridad.
    *   **`wshobson/agents/on-call-handoff-patterns`**: Relevante para formalizar la lógica de transferencia entre agentes por rol en FaberLoom.

3.  **Desarrollo Interno (Para Cubrir Brechas)**:
    *   La brecha más crítica es el **puente entre orquestadores modernos y el sistema congelado de MWT** (`mwt-orchestrator-bridge`). Esto no lo resolverá ninguna *skill* externa.
    *   FaberLoom debería priorizar el desarrollo de un **`faber-loom-role-router`** que encapsule su lógica de negocio única (KB scope, tono, autoridad) en una *skill* reutilizable.

En resumen, el ecosistema de *skills* está evolucionando rápidamente, pero aún carece de soluciones profundamente integradas para la orquestación de agentes con gobernanza empresarial compleja. La estrategia óptima para MWT y FaberLoom es una combinación de *skills* estándar para tareas genéricas (ej. *handoff*, HITL) y desarrollo propio para la lógica de orquestación y *routing* que es el núcleo de su ventaja competitiva.