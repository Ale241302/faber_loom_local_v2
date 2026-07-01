# Dimension 7: Anthropic/Claude — Projects, Cowork, Console y Patterns Avanzados

**Fecha de investigacion:** 2026-05-15
**Investigador:** Agente de investigacion tecnica especializado
**Fuentes consultadas:** 25+ busquedas independientes, documentacion oficial de Anthropic, blogs de ingenieria, papers academicos, analisis de producto
**Contexto:** FaberLoom tiene tabs Configurar / Iterar / Sanidad con aprobaciones humanas (aprobar/descartar/iterar). Este documento analiza patterns avanzados de Anthropic/Claude para evaluar trasladabilidad.

---

## Tabla de Contenidos

1. [Claude Projects: Organizacion por Proyecto](#1-claude-projects)
2. [Claude Cowork: Colaboracion Multi-Usuario](#2-claude-cowork)
3. [Claude Console: Developer Experience](#3-claude-console)
4. [Approval Flows en Anthropic](#4-approval-flows)
5. [Iteration Loops en Artifacts](#5-iteration-loops)
6. [Error Handling y Retry Patterns](#6-error-handling)
7. [Context Management](#7-context-management)
8. [Patterns Transversales](#8-patterns-transversales)
9. [Skills y Open Standard](#9-skills)
10. [Resumen Ejecutivo y Recomendaciones](#10-resumen-ejecutivo)

---

## 1. Claude Projects

### 1.1 Vision General

```
Claim: Claude Projects permite crear workspaces auto-contenidos con historial de chat propio, knowledge base de documentos, instrucciones personalizadas y capacidades de colaboracion en equipo.
Source: Anthropic Official - Collaborate with Claude on Projects
URL: https://www.anthropic.com/news/projects
Date: 2024-06-25
Excerpt: "Projects allow you to ground Claude's outputs in your internal knowledge—be it style guides, codebases, interview transcripts, or past work. This added context enables Claude to provide expert assistance across tasks, from writing emails like your marketing team to writing SQL queries like a data analyst."
Context: Lanzado originalmente en junio 2024 para usuarios Pro y Team. Es una de las funcionalidades centrales de la estrategia de producto de Anthropic.
Confidence: high
```

```
Claim: Cada proyecto incluye una ventana de contexto de 200K tokens (equivalente a un libro de 500 paginas) y permite anadir documentos, codigo e insights para mejorar la efectividad de Claude.
Source: Anthropic Official Blog
URL: https://www.anthropic.com/news/projects
Date: 2024-06-25
Excerpt: "Each project includes a 200K context window, the equivalent of a 500-page book, so users can add all of the relevant documents, code, and insights to enhance Claude's effectiveness."
Context: La ventana de 200K es para planes pagados. Enterprise ofrece hasta 500K-1M tokens.
Confidence: high
```

### 1.2 Project Knowledge y KB Integration

```
Claim: Los proyectos permiten subir documentos (PDFs, DOCX, codigo, CSVs, HTML) que Claude referencia automaticamente sin necesidad de re-input. Los documentos se procesan mediante RAG (Retrieval Augmented Generation) cuando se acercan a los limites de contexto.
Source: Claude Help Center - What are projects?
URL: https://support.claude.com/en/articles/9517075-what-are-projects
Date: 2026-03-16
Excerpt: "You can upload relevant documents, text, code, or other files to a project's knowledge base, which Claude will use to better understand the context and background for your individual chats within that project."
Context: Existe tambien "Enhanced project knowledge with RAG" que se activa automaticamente.
Confidence: high
```

```
Claim: Cuando el conocimiento del proyecto se acerca a los limites de la ventana de contexto, Claude activa automaticamente el modo RAG que expande la capacidad hasta 10x manteniendo la calidad de respuesta. No requiere configuracion del usuario.
Source: Claude Help Center - RAG for projects
URL: https://support.claude.com/en/articles/11473015-retrieval-augmented-generation-rag-for-projects
Date: 2026-03-16
Excerpt: "When your project knowledge approaches context limits, Claude seamlessly enables RAG mode to expand capacity by up to 10x while maintaining response quality... RAG activates automatically when needed. No setup or configuration is required."
Context: El usuario ve un indicador visual cuando RAG esta activo. Si el conocimiento baja del umbral, Claude vuelve a procesamiento basado en contexto.
Confidence: high
```

```
Claim: El RAG de Claude usa "Contextual Retrieval" propio en lugar de RAG tradicional. En lugar de simplemente anexar contenido recuperado como tokens de contexto, el sistema busca en la Knowledge Base, enriquece la informacion con detalles contextuales, y combina este contexto enriquecido con el prompt del usuario.
Source: Learn Claude ReadTheDocs - Knowledge Base Quick Start
URL: https://learn-claude.readthedocs.io/en/latest/02-Claude-Project/41-Claude-Project-Knowledge-Base-Quick-Start/
Date: 2024-09-25
Excerpt: "Claude's implementation of RAG is augmented with its Contextual Retriever. Instead of simply appending retrieved content as context tokens in the chat, the retriever: 1. Searches the Knowledge Base for relevant content. 2. Enhances the retrieved information by adding contextual details. 3. Combines this enriched context with the user's prompt to generate the final response."
Context: Este enfoque mejora la precision comparado con RAG tradicional, especialmente cuando el usuario menciona referencias especificas como "seccion 1234".
Confidence: medium
```

### 1.3 Custom Instructions

```
Claim: Cada proyecto permite definir instrucciones personalizadas (project instructions) que adaptan las respuestas de Claude: tono, perspectiva de rol/industria, formato de salida, etc. Estas instrucciones se aplican a todos los chats dentro del proyecto.
Source: Claude Help Center
URL: https://support.claude.com/en/articles/9517075-what-are-projects
Date: 2026-03-16
Excerpt: "You can define project instructions for each project to further tailor Claude's responses. For example, instructing Claude to use a more formal tone or answer questions from the perspective of a specific role or industry."
Context: Esto es equivalente a "system prompts" a nivel de proyecto. Reduce la necesidad de repetir instrucciones en cada conversacion.
Confidence: high
```

### 1.4 Colaboracion y Sharing

```
Claim: En planes Team y Enterprise, los proyectos pueden compartirse con otros miembros de la organizacion con diferentes niveles de permiso. Incluye un "activity feed" donde los miembros del equipo pueden ver snapshots de las mejores conversaciones compartidas.
Source: Anthropic Blog
URL: https://www.anthropic.com/news/projects
Date: 2024-06-25
Excerpt: "Claude Team users can also share snapshots of their best conversations with Claude into your team's shared project activity feed. Activity feeds help each teammate get inspired around different ways to work with Claude, and helps the entire team uplevel their skills working with AI."
Context: La colaboracion incluye: multiple members pueden contribuir documentos, crear chats, y trabajar juntos dentro del mismo entorno de proyecto.
Confidence: high
```

```
Claim: Cada proyecto en Cowork tiene su propio espacio de memoria y resumen de proyecto dedicado, separado de otros proyectos y chats no asociados a proyectos.
Source: Claude Help Center - Chat search and memory
URL: https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context
Date: 2026-03-16
Excerpt: "Each project has its own separate memory space and dedicated project summary, so the context within each of your projects is focused, relevant, and separate from other projects or non-project chats."
Context: La memoria de proyecto se actualiza cada 24 horas con una sintesis de insights clave.
Confidence: high
```

### 1.5 Evaluacion de Trasladabilidad a FaberLoom

**Alto valor:**
- **KB integration con RAG automatico**: El pattern de RAG que se activa automaticamente cuando se excede el contexto es directamente trasladable a FaberLoom para el tab "Configurar" donde los usuarios cargan documentos de diseno.
- **Instrucciones por proyecto**: Equivalente a las instrucciones de generacion de codigo por proyecto en FaberLoom.
- **Separacion de memoria por proyecto**: Cada proyecto Cowork tiene memoria aislada; FaberLoom deberia aislar el contexto por proyecto de forma similar.

**Medio valor:**
- **Activity feed colaborativo**: Podria adaptarse para mostrar iteraciones recientes y decisiones de diseno en equipo.

---

## 2. Claude Cowork

### 2.1 Vision General

```
Claim: Claude Cowork es una extension de los principios de Claude Code al trabajo de conocimiento general. Permite a Claude actuar dentro de un entorno de escritorio controlado y completar tareas en nombre del usuario, con mayor autonomia que un chat estandar.
Source: Amplifi Labs - Claude Cowork Explained
URL: https://www.amplifilabs.com/post/claude-cowork-explained-how-anthropic-is-building-agentic-productivity
Date: 2026-03-30
Excerpt: "With Cowork enabled, Claude can: Read and modify files inside approved folders; Create, rename, and organize documents; Compile information across multiple sources; Generate structured outputs such as reports or spreadsheets; Execute sequences of actions based on a single natural-language instruction"
Context: Cowork esta disponible como "research preview" para suscriptores de Claude Max via la app de escritorio macOS.
Confidence: high
```

```
Claim: Cowork opera con un modelo de permisos basado en carpetas: el usuario otorga acceso explicito a carpetas locales especificas, lo que limita el alcance de lo que el modelo puede ver o modificar. Claude solicita confirmacion para acciones destructivas.
Source: MIT Sloan Management Review
URL: https://www.mitsloanme.com/article/anthropic-tests-cowork-an-ai-tool-that-can-act-on-files-and-folders/
Date: 2026-01-13
Excerpt: "Cowork allows users to grant Claude access to a specific folder on their device. Within those boundaries, the AI can read, edit, rename, delete, or create files... Anthropic emphasizes that user control remains central to the design. Claude can only access folders and connectors that are explicitly approved by the user and will request confirmation before taking any significant actions."
Context: Cowork integra conectores (Asana, Notion) e incluye "Skills" para mejorar la creacion de documentos y presentaciones.
Confidence: high
```

### 2.2 Workflow Tipico de Cowork

```
Claim: El workflow de Cowork sigue tres pasos: (1) el usuario define una tarea en lenguaje natural, (2) Claude planifica los pasos necesarios, (3) Claude ejecuta esos pasos dentro del entorno permitido, actualizando al usuario a lo largo del proceso.
Source: Amplifi Labs
URL: https://www.amplifilabs.com/post/claude-cowork-explained-how-anthropic-is-building-agentic-productivity
Date: 2026-03-30
Excerpt: "A typical workflow follows three steps: 1. The user defines a task in natural language; 2. Claude plans the steps required to complete it; 3. Claude executes those steps within the permitted environment"
Context: El usuario no necesita copiar manualmente outputs ni guiar cada paso intermedio. El sistema opera con mayor autonomia pero sigue requiriendo confirmacion para acciones sensibles.
Confidence: high
```

### 2.3 Cowork Projects

```
Claim: Cowork permite crear proyectos que agrupan tareas relacionadas en workspaces dedicados con sus propios archivos, contexto, instrucciones y memoria. Estos proyectos pueden crearse desde cero, importarse desde un proyecto de Claude, o usar una carpeta existente en el ordenador.
Source: Claude Help Center - Organize your tasks with projects in Claude Cowork
URL: https://support.claude.com/en/articles/14116274-organize-your-tasks-with-projects-in-claude-cowork
Date: 2026-04-09
Excerpt: "Projects in Claude Cowork let you group related tasks into dedicated workspaces with their own files, context, instructions, and memory. If you use projects on Claude, Cowork projects work similarly, but they live locally on your desktop and are built around the tasks you run through Cowork."
Context: La memoria esta habilitada para proyectos Cowork, lo que significa que Claude puede recordar contexto de tareas anteriores y aplicarlo a tareas futuras en el mismo proyecto.
Confidence: high
```

### 2.4 Diferencia Cowork vs Claude Code

```
Claim: Cowork esta empaquetado para tareas de escritorio no relacionadas con codificacion, con configuracion mas facil (sin linea de comando). Claude Code es para desarrolladores y opera via terminal. Ambos comparten los mismos fundamentos de ejecucion agentica.
Source: Gend.co - Claude Co-Work Explained
URL: https://www.gend.co/blog/anthropic-claude-cowork
Date: 2026-01-13
Excerpt: "Cowork also integrates with connectors (e.g., Asana, Notion) and introduces an initial set of Skills to improve document and presentation creation. When paired with Claude in Chrome, Claude can also complete tasks requiring browser access... Same foundations and agentic execution, but packaged for non-coding, desktop tasks and easier setup—no command line required."
Context: Cowork esta disponible solo para macOS por ahora. Windows esta planificado.
Confidence: high
```

### 2.5 Evaluacion de Trasladabilidad a FaberLoom

**Alto valor:**
- **Delegacion de tareas agenticas**: El pattern de "describir resultado deseado + Claude planifica + ejecuta con actualizaciones" es directamente aplicable al tab "Iterar" de FaberLoom.
- **Scope control via permisos de carpeta**: El modelo de permisos basado en carpetas aprobadas es analogo a la sandbox de generacion de FaberLoom.
- **Memoria por proyecto**: Cada proyecto Cowork mantiene memoria separada; FaberLoom deberia aislar memoria por proyecto de diseno.

**Medio valor:**
- **Integracion con conectores**: El pattern de conectar con herramientas externas (Notion, Asana) podria adaptarse para integracion con herramientas de diseno (Figma, etc.).

---

## 3. Claude Console y Developer Experience

### 3.1 Vision General del Console

```
Claim: El Anthropic Console es la interfaz web oficial para gestionar el acceso a la API de Claude. Incluye el Workbench (playground interactivo de prompts), monitoreo de uso, gestion de API keys, y documentacion.
Source: GetOpenClaw - Anthropic Console Guide
URL: https://www.getopenclaw.ai/tools/anthropic-console
Date: 2026-02-04
Excerpt: "The Anthropic Console is your command center for building with Claude. From the Workbench for testing prompts to usage dashboards and API key management, it's where serious Claude developers spend their time."
Context: Esencial para cualquier desarrollador construyendo aplicaciones con Claude.
Confidence: high
```

### 3.2 Workbench

```
Claim: El Workbench permite crear y testear prompts dentro de la cuenta de Console. Soporta configuracion de modelo, temperatura, max tokens, y genera codigo de ejemplo para los SDKs de Python y TypeScript.
Source: Claude Help Center - How do I use the Workbench?
URL: https://support.claude.com/en/articles/8606378-how-do-i-use-the-workbench
Date: 2026-03-16
Excerpt: "The Workbench allows you to create and test prompts within your Claude Console account. You can enter your prompt into the 'Human' dialogue box and click 'Run' to test Claude's output... The Workbench also allows you to configure several settings when prompting Claude."
Context: El Workbench guarda historial de prompts testeados y permite buscar prompts anteriores.
Confidence: high
```

```
Claim: El Workbench incluye herramientas de evaluacion (Evals) que permiten versionar prompts, correr multiples escenarios, y calificar outputs. Cambiar la temperatura se trata como una nueva version del prompt.
Source: LLMindset - Role Prompting Claude Workbench
URL: https://llmindset.co.uk/posts/2024/07/role-prompting-claude-workbench/
Date: 2024-07-15
Excerpt: "The Console has applied a version number to our prompt. Next to 'v1' is an average of the ratings we had given the outputs. It's also stored the result of our 'previous Without role' test run... A very nice touch in the Anthropic Workbench is that it treats changing the temperature setting as a new version of the prompt."
Context: Las evaluaciones incluyen tablas de resultados con ratings promedio por version.
Confidence: medium
```

### 3.3 Colaboracion en Console

```
Claim: Anthropic actualizo el Console para permitir compartir prompts y colaborar con companeros de equipo directamente. Anteriormente los desarrolladores tenian que copiar y pegar prompts entre documentos, causando problemas de version control y silos de conocimiento.
Source: InfoWorld - Anthropic's upgraded Console
URL: https://www.infoworld.com/article/3841405/anthropics-upgraded-console-targets-more-collaboration-among-developers.html
Date: 2025-03-07
Excerpt: "Developers can now share prompts to collaborate with teammates directly in the Anthropic Console... previously they had to resort to copying and pasting prompts between documents or chat applications, leading to version control issues and knowledge silos."
Context: La colaboracion incluye un "running library of prompts" para que nada se pierda con el tiempo.
Confidence: high
```

### 3.4 Extended Thinking y Budgeting

```
Claim: El Console incluye una capacidad de "budgeting" para extended thinking, que permite establecer un limite maximo de tokens de "thinking" que se generan. Esto permite controlar costos mientras se aprovecha el razonamiento profundo.
Source: InfoWorld - Anthropic's upgraded Console
URL: https://www.infoworld.com/article/3841405/anthropics-upgraded-console-targets-more-collaboration-among-developers.html
Date: 2025-03-07
Excerpt: "Anthropic is also offering a budgeting capability for extended thinking inside the Console, which can be used to set a limit to the maximum amount of 'thinking' tokens being generated."
Context: Extended thinking muestra los pasos que el modelo toma para llegar a una respuesta, similar a chain-of-thought visible.
Confidence: high
```

```
Claim: Extended thinking tokens se facturan como tokens de salida (no como una tarifa separada). El presupuesto minimo es 1,024 tokens. El modelo puede detenerse antes si termina el razonamiento, por lo que el presupuesto es un cap, no un target.
Source: René Zander Blog - Claude Extended Thinking
URL: https://renezander.com/blog/claude-extended-thinking/
Date: 2026-03-27
Excerpt: "The model can stop early. If it finishes reasoning in 2,400 tokens, you pay for 2,400, not 10,000. The budget is a cap, not a target. In practice Opus uses between 40 and 90 percent of the budget on tasks that actually need it, and almost none on tasks that don't."
Context: Este pattern de "budget-as-cap" es util para controlar costos en sistemas agenticos.
Confidence: high
```

### 3.5 Prompt Caching

```
Claim: El prompt caching de Anthropic almacena el estado computado (KV cache) de prompts ya procesados, reduciendo latencia y costos en conversaciones largas. Los tokens de cache read cuestan aproximadamente 10% del precio de tokens de input estandar.
Source: MindStudio - Anthropic Prompt Caching
URL: https://www.mindstudio.ai/blog/anthropic-prompt-caching-claude-subscription-limits/
Date: 2026-04-05
Excerpt: "Prompt caching lets Anthropic store that computed state so it doesn't have to be recalculated on the next request... Anthropic's pricing for Claude models shows cache read tokens at roughly 10% of the standard input token price for most Claude models — a significant discount."
Context: El cache funciona por prefijos: el contenido cacheado debe aparecer al inicio del contexto, antes de las partes dinamicas.
Confidence: high
```

### 3.6 Evaluacion de Trasladabilidad a FaberLoom

**Alto valor:**
- **Workbench como playground**: El pattern de playground de prompts es analogo a un "test environment" para instrucciones de generacion de codigo en FaberLoom.
- **Versionado de prompts con evaluacion**: La capacidad de versionar prompts y evaluar outputs es directamente aplicable al tab "Sanidad" de FaberLoom.
- **Budgeting de thinking tokens**: El control de presupuesto de razonamiento es util para limitar costos en iteraciones de diseno.
- **Prompt caching**: Optimizacion tecnica trasladable para mejorar rendimiento en conversaciones largas de iteracion.

---

## 4. Approval Flows en Anthropic

### 4.1 Sistema de Permisos de Claude Code (Permission Modes)

```
Claim: Claude Code ofrece cinco modos de permiso que representan diferentes equilibrios entre conveniencia y supervision: default (solo lecturas sin preguntar), acceptEdits (lecturas + ediciones + filesystem), plan (solo lectura, modo planificacion), auto (todo con safety checks en background), y dontAsk (solo herramientas pre-aprobadas).
Source: Claude Code Docs - Choose a permission mode
URL: https://code.claude.com/docs/en/permission-modes
Date: 2025-09-01
Excerpt: "Each mode makes a different tradeoff between convenience and oversight. The table below shows what Claude can do without a permission prompt in each mode."
Context: Los modos se pueden cambiar durante la sesion, al inicio, o como default persistente.
Confidence: high
```

| Modo | Que ejecuta sin preguntar | Mejor para |
|------|--------------------------|------------|
| `default` | Solo lecturas | Empezar, trabajo sensible |
| `acceptEdits` | Lecturas, ediciones de archivo, comandos filesystem comunes | Iterar en codigo que revisas |
| `plan` | Solo lecturas | Explorar codebase antes de cambiar |
| `auto` | Todo, con safety checks en background | Tareas largas, reducir fatiga de prompts |
| `dontAsk` | Solo herramientas pre-aprobadas | CI/scripts bloqueados |
| `bypassPermissions` | Todo | Solo contenedores/VMs aislados |

### 4.2 Plan Mode

```
Claim: Plan Mode es un modo de solo lectura donde Claude puede analizar el codebase, hacer preguntas de clarificacion, y crear planes detallados de implementacion sin modificar archivos ni ejecutar comandos. Separa el pensamiento de la ejecucion.
Source: Code With Mukesh - Plan Mode in Claude Code
URL: https://codewithmukesh.com/blog/plan-mode-claude-code/
Date: 2026-02-25
Excerpt: "Plan Mode is a read-only operating mode in Claude Code where Claude can analyze your codebase, ask clarifying questions, and create detailed implementation plans without modifying any files or running any commands. It separates thinking from execution, letting you review and approve an approach before Claude writes any code."
Context: Se activa con Shift+Tab dos veces, el comando /plan, o el flag --permission-mode plan.
Confidence: high
```

```
Claim: Cuando el plan esta listo, Claude lo presenta y pregunta como proceder. Las opciones incluyen: aprobar y empezar en modo auto, aprobar y accept edits, aprobar y revisar cada edicion manualmente, seguir planificando con feedback, o refinar con Ultraplan. El usuario puede editar el plan con Ctrl+G antes de aprobarlo.
Source: Claude Code Docs
URL: https://code.claude.com/docs/en/permission-modes
Date: 2025-09-01
Excerpt: "When the plan is ready, Claude presents it and asks how to proceed. From that prompt you can: Approve and start in auto mode; Approve and accept edits; Approve and review each edit manually; Keep planning with feedback; Refine with Ultraplan for browser-based review"
Context: Aprobar un plan tambien nombra la sesion automaticamente a partir del contenido del plan.
Confidence: high
```

### 4.3 Auto Mode y el Permission Classifier

```
Claim: Auto Mode usa un modelo clasificador AI separado (Claude Sonnet 4.6) que revisa cada accion antes de ejecutarla, bloqueando acciones que escalen mas alla de lo solicitado, apunten a infraestructura no reconocida, o parezcan impulsadas por contenido hostil.
Source: Claude Code Docs
URL: https://code.claude.com/docs/en/permission-modes
Date: 2025-09-01
Excerpt: "Auto mode lets Claude execute without permission prompts. A separate classifier model reviews actions before they run, blocking anything that escalates beyond your request, targets unrecognized infrastructure, or appears driven by hostile content Claude read."
Context: Auto mode requiere: plan Max/Team/Enterprise, admin habilita en Team/Enterprise, modelo Sonnet 4.6/Opus 4.6, y provider Anthropic API.
Confidence: high
```

```
Claim: El clasificador de permisos funciona en dos etapas: un filtro rapido de un solo token (decidiendo 'si' para bloquear o 'no' para permitir), seguido de razonamiento chain-of-thought solo si el primer filtro marca la accion. La mayoria de acciones pasan la primera etapa sin gastar tokens de razonamiento.
Source: MBGSec - Claude Code Auto Mode
URL: https://www.mbgsec.com/archive/2026-03-29-claude-code-auto-mode-a-safer-way-to-skip-permissions/
Date: 2026-03-29
Excerpt: "The classifier runs in two stages: a fast single-token filter (deciding 'yes' to block or 'no' to allow), followed by chain-of-thought reasoning only if the first filter flags the transcript. Because most actions clear the first stage, reasoning tokens are spent only where needed."
Context: El FPR (false positive rate) del pipeline completo es 0.4% en trafico real. El FNR (false negative rate) en acciones sobre-entusiastas reales es 17%.
Confidence: high
```

### 4.4 El Problema del Consent Fatigue

```
Claim: Los datos de Anthropic muestran que los desarrolladores aprueban el 93% de los prompts de permiso en Claude Code. En tareas complejas, Claude pide clarificacion en el 16.4% de los turnos. A cientos de acciones por sesion, la aprobacion por accion individual genera "consent fatigue".
Source: Anthropic - Measuring AI agent autonomy in practice
URL: https://www.anthropic.com/news/measuring-agent-autonomy
Date: 2026-02-18
Excerpt: "Newer users (<50 sessions) employ full auto-approve roughly 20% of the time; by 750 sessions, this increases to over 40% of sessions... New users interrupt Claude in 5% of turns, while more experienced users interrupt in around 9% of turns."
Context: Ambas cosas (auto-approvals E interrupciones) aumentan con la experiencia. Los usuarios experimentados dejan que Claude trabaje autonomamente e interrumpen cuando algo sale mal. Esto es "incident response, not oversight."
Confidence: high
```

```
Claim: Anthropic propone un modelo de seguridad de responsabilidad compartida de cuatro capas: Modelo (proveedor), Arnes/Arnés (instrucciones y politicas), Herramientas (MCP servers, APIs), y Entorno (donde corre el agente). Recomiendan "Plan Mode" como alternativa a la aprobacion por accion.
Source: Backslash Security - Anthropic's Shared Responsibility Security Model
URL: https://www.backslash.security/blog/anthropics-shared-responsibility-security-model-for-ai-agents
Date: 2026-04-29
Excerpt: "Anthropic's framework divides AI agent security into four layers - Model, Harness, Tools, and Environment... The paper reports that on complex tasks, Claude asks for clarification on 16.4% of turns... Anthropic's data from the Claude Code auto mode launch showed that developers already approve 93% of permission prompts."
Context: El modelo reconoce que el human-in-the-loop ya fallo a escala de produccion.
Confidence: high
```

### 4.5 Deny-and-Continue

```
Claim: Cuando el clasificador bloquea una accion, Claude no se detiene y espera input humano; en su lugar recupera e intenta un enfoque mas seguro donde exista. Si acumula 3 denegaciones consecutivas o 20 totales, el sistema escala y pide aprobacion humana.
Source: MBGSec - Claude Code Auto Mode
URL: https://www.mbgsec.com/archive/2026-03-29-claude-code-auto-mode-a-safer-way-to-skip-permissions/
Date: 2026-03-29
Excerpt: "When the transcript classifier flags an action as dangerous, that denial comes back as a tool result along with an instruction to treat the boundary in good faith: find a safer path, don't try to route around the block. If a session accumulates 3 consecutive denials or 20 total, we stop the model and escalate to the human."
Context: Este pattern hace que los falsos positivos sean "survivibles" - un 0.4% FPR no mata la sesion.
Confidence: high
```

### 4.6 Evaluacion de Trasladabilidad a FaberLoom

**Alto valor:**
- **Plan Mode**: El pattern de "planificar primero, ejecutar despues" es directamente aplicable al tab "Configurar" de FaberLoom. El usuario revisa y aprueba el plan antes de la generacion.
- **Escalacion tras N bloqueos**: El pattern de "3 denegaciones consecutivas o 20 totales -> escalar a humano" es trasladable al flujo de "Sanidad" donde despues de N intentos fallidos se requiere revision humana.
- **Clasificador de 2 etapas**: El enfoque de filtro rapido + razonamiento profundo solo cuando es necesario optimiza costos y latencia.
- **Consent fatigue awareness**: Reconocer que la aprobacion por cada accion no escala justifica el diseno de FaberLoom de aprobacion por lote (aprobar/descartar/iterar) en lugar de por cada micro-accion.

**Medio valor:**
- **Modos de permiso graduales**: La idea de diferentes niveles de autonomia segun confianza y contexto.

---

## 5. Iteration Loops en Artifacts

### 5.1 Vision General de Artifacts

```
Claim: Claude Artifacts convierten las conversaciones en un workspace vivo donde se puede construir, previsualizar y compartir aplicaciones interactivas, documentos y visualizaciones sin salir del chat. Soportan almacenamiento persistente (hasta 20MB por artifact), llamadas API directas, integraciones MCP, y Live Artifacts que se actualizan con datos actuales.
Source: Albato - Claude Artifacts Guide
URL: https://albato.com/blog/publications/how-to-use-claude-artifacts-guide
Date: 2026-04-29
Excerpt: "Claude Artifacts turn conversations into a live workspace where you can build, preview, and share interactive applications, documents, and visualizations without leaving the chat. Available on all Claude plans (Free, Pro, Max, Team, Enterprise), Artifacts now support persistent storage (up to 20MB per artifact), direct API calls, MCP integrations with external services, and Live Artifacts..."
Context: Artifacts evolucionaron de un simple panel de preview a un entorno completo de desarrollo de micro-apps.
Confidence: high
```

### 5.2 El Loop de Iteracion

```
Claim: La iteracion en Artifacts ocurre a traves de conversacion. En lugar de editar documentos manualmente, el usuario los refina hablando con Claude, creando un proceso creativo mas natural. Se puede pedir un cambio como "haz el boton azul" y ver la actualizacion en tiempo real en la ventana de Artifact.
Source: Learn Prompting - Are Claude Artifacts Worth Using?
URL: https://newsletter.learnprompting.org/p/are-claude-artifacts-worth-using
Date: 2025-09-12
Excerpt: "Iteration happens through conversation. Instead of manually editing documents, you refine them by talking to Claude, creating a more natural creative process... You can ask for a change in the chat – like 'make the button blue' and watch it update in the Artifact window in real-time. It completely changes the speed of UI/UX iteration."
Context: Este es el "conversation-driven iteration" que diferencia a Artifacts de otros editores.
Confidence: high
```

### 5.3 Version History

```
Claim: Artifacts mantienen un historial de versiones completo. Los usuarios pueden ver versiones anteriores a traves de un menu desplegable en el panel derecho del artifact, y cambiar entre versiones segun sea necesario.
Source: Guideflow - How to view version history of an artifact in Claude.ai
URL: https://www.guideflow.com/tutorial/how-to-view-version-history-of-an-artifact-in-claudeai
Date: 2026-03-04
Excerpt: "In the artifact's right-side panel, locate the version option. Then hover and click on the version dropdown menu to see a list of all previous versions. Finally click on a version from the dropdown menu to switch it if needed."
Context: Cada cambio genera una nueva version, permitiendo volver a estados anteriores facilmente.
Confidence: medium
```

### 5.4 Publicacion y Sharing

```
Claim: Cualquier artifact puede publicarse y compartirse via enlace, incluso con personas que no tienen cuenta de Claude. Existe un Artifact Catalog comunitario donde se pueden explorar creaciones de otros usuarios. Los artifacts publicados pueden ser "remixed" y personalizados por otros.
Source: Amit Koth - Claude Artifacts Guide
URL: https://amitkoth.com/claude-artifacts-guide/
Date: 2025-11-04
Excerpt: "Built for collaboration and sharing. Publish artifacts with a link, let others remix and customize, browse community creations in the Artifact Catalog, or keep them private within your team"
Context: El modelo de "remix" es similar a forks en GitHub.
Confidence: medium
```

### 5.5 Limitaciones

```
Claim: Las principales limitaciones de Artifacts son: no es un IDE completo (no permite escribir codigo manualmente directamente en el artifact), no tiene conexiones a APIs externas (salvo via MCP), y en algunos casos no se pueden editar artifacts despues de la creacion inicial.
Source: Learn Prompting / Robert Hu Blog
URL: https://newsletter.learnprompting.org/p/are-claude-artifacts-worth-using / https://theroberthu.com/blog/chatgpt-canvas-vs-claude-artifacts
Date: 2025-09-12 / 2025-07-19
Excerpt: "Not a Full IDE: Unlike other tools (Google's Build Mode), Artifacts don't allow users to manually write code... No External API Connections: While you are able to create Artifacts that use Claude features, you can't connect to other APIs."
Context: Comparado con ChatGPT Canvas, Artifacts es mejor para analisis/visualizacion de negocios pero carece de edicion colaborativa en tiempo real.
Confidence: medium
```

### 5.6 Evaluacion de Trasladabilidad a FaberLoom

**Alto valor:**
- **Iteracion conversacional**: El pattern de "pedir cambios en lenguaje natural y ver actualizacion en tiempo real" es el core del tab "Iterar" de FaberLoom.
- **Historial de versiones**: El versionado de artifacts es directamente aplicable al historial de iteraciones de diseno.
- **Preview en vivo**: El panel lateral con preview inmediato es analogo al canvas de preview de FaberLoom.

**Medio valor:**
- **Publicacion y sharing**: Compartir versiones especificas del diseno con stakeholders.
- **Remix**: La capacidad de que otros usuarios partan de un diseno existente.

---

## 6. Error Handling y Retry Patterns

### 6.1 Taxonomia de Errores del API

```
Claim: Anthropic expone una taxonomia completa de errores con excepciones tipadas: RateLimitError, APIStatusError, APITimeoutError, APIConnectionError. El SDK tiene retry logic integrado para errores 429 y 5xx.
Source: ClaudeReadiness - Claude Error Handling Patterns
URL: https://claudereadiness.com/blog/claude-error-handling-patterns/
Date: 2025-12-01
Excerpt: "The Anthropic Python SDK exposes these as typed exceptions: anthropic.RateLimitError, anthropic.APIStatusError, anthropic.APITimeoutError, and anthropic.APIConnectionError. Catch specifically rather than with a blanket except Exception — you need to distinguish between retryable and permanent errors."
Context: Tabla completa de errores: 400 (permanente), 401 (permanente), 403 (permanente), 404 (permanente), 413 (permanente), 429 (retryable con backoff), 500 (retryable), 529 (retryable con delays mas largos), Timeout (retryable).
Confidence: high
```

### 6.2 Estrategias de Retry

```
Claim: Para errores 429 (rate limit), siempre usar el header Retry-When presente. Si esta ausente, usar exponential backoff: wait = base_delay * 2^attempt + jitter (base_delay=1.0s, jitter=random(0,0.5), max_delay=60s). Despues de 5 retries, agregar a una cola de retry prioritario.
Source: ClaudeReadiness
URL: https://claudereadiness.com/blog/claude-error-handling-patterns/
Date: 2025-12-01
Excerpt: "Always use the Retry-After response header when present — this tells you exactly how long to wait, which is more accurate than a calculated backoff. If the header is absent, use exponential backoff: wait = base_delay x 2^attempt + jitter"
Context: Para errores de servidor (500, 529), usar exponential backoff con delays iniciales ligeramente mas largos (2-3 segundos base).
Confidence: high
```

### 6.3 User-Facing Error Handling

```
Claim: Los errores tecnicos nunca deben mostrarse directamente al usuario. Se debe mapear cada tipo de error a un mensaje claro y accionable que establezca expectativas sin exponer detalles de implementacion. Para tiempos de espera largos: mostrar indicador de progreso, actualizaciones de estado, opcion de cancelar, y notificacion de completitud.
Source: ClaudeReadiness
URL: https://claudereadiness.com/blog/claude-error-handling-patterns/
Date: 2025-12-01
Excerpt: "'429 Too Many Requests from Anthropic API' is not a user message. 'We're experiencing high demand right now — your request is being processed and will complete in approximately 2 minutes' is... For requests that will take a long time due to retry cycles: show a progress indicator immediately, provide status updates."
Context: Pattern de "progressive disclosure" para tiempos de espera largos.
Confidence: high
```

### 6.4 Graceful Degradation

```
Claim: Cuando Claude esta no disponible y se sirve desde fallback, mostrar un mensaje explicativo: "Our AI assistant is temporarily unavailable — we're showing a simplified version of this feature. Full capability will be restored shortly."
Source: ClaudeReadiness
URL: https://claudereadiness.com/blog/claude-error-handling-patterns/
Date: 2025-12-01
Excerpt: "When Claude is unavailable and you're serving from fallback: 'Our AI assistant is temporarily unavailable — we're showing a simplified version of this feature. Full capability will be restored shortly.' This is far better than a broken state or a confusing error."
Context: Este pattern de degradacion graceful es aplicable a sistemas donde el AI es una capa de valor agregado pero no el core.
Confidence: high
```

### 6.5 Circuit Breaker

```
Claim: Se recomienda implementar un circuit breaker para cualquier integracion donde la indisponibilidad del API podria causar fallos en cascada. El circuit breaker monitorea fallos y, cuando exceden un umbral, cortocircuita temporalmente las llamadas al API.
Source: ClaudeReadiness
URL: https://claudereadiness.com/blog/claude-error-handling-patterns/
Date: 2025-12-01
Excerpt: "A circuit breaker monitors failures and, when they exceed a threshold, temporarily short-circuits calls to the API — preventing cascading failures. After a cooldown period, it allows a test request through. If successful, normal operation resumes."
Context: Especialmente importante para funcionalidades orientadas al usuario.
Confidence: high
```

### 6.6 Evaluacion de Trasladabilidad a FaberLoom

**Alto valor:**
- **Taxonomia de errores tipada**: Distinguir errores retryable vs permanentes es fundamental para el tab "Sanidad" donde los errores de generacion deben clasificarse.
- **Exponential backoff con jitter**: Pattern estandar para reintentos de generacion fallida.
- **User-facing error messages**: Nunca mostrar errores tecnicos crudos al usuario; mapear a mensajes accionables.
- **Circuit breaker**: Evitar que fallos de LLM cascaden a toda la aplicacion.
- **Progressive disclosure**: Indicadores de progreso para iteraciones largas de diseno.

---

## 7. Context Management

### 7.1 Context Window y Memory Drift

```
Claim: Claude ofrece ventanas de contexto de 200K tokens en planes pagados estandar, hasta 500K en Enterprise Sonnet 4.5, y hasta 1M en variantes extended context beta. Sin embargo, a medida que las conversaciones crecen, el contenido mas antiguo se empuja fuera de la memoria activa, causando "memory drift".
Source: DataStudios - Does Claude Keep Context in Long Conversations?
URL: https://www.datastudios.org/post/does-claude-keep-context-in-long-conversations-memory-depth-and-stability
Date: 2026-02-09
Excerpt: "As conversations grow and the context window becomes saturated, the oldest content is gradually pushed out of active memory. At that point, Claude loses direct access to those earlier turns, resulting in a shift from perfect recall to a gradual 'drift' in which instructions or constraints may weaken or be forgotten altogether."
Context: Los sintomas de memory drift incluyen: reglas de formato olvidadas, parametros perdidos, respuestas contradictorias, y prompts de clarificacion repetidos.
Confidence: high
```

### 7.2 Compaction Automatica

```
Claim: Para usuarios con code execution habilitado, Claude gestiona automaticamente conversaciones largas. Cuando una conversacion se acerca al limite de la ventana de contexto, Claude resume mensajes anteriores para continuar seamless. El historial completo se preserva para referencia.
Source: Claude Help Center - How do usage and length limits work?
URL: https://support.claude.com/en/articles/11647753-how-do-usage-and-length-limits-work
Date: 2026-05-06
Excerpt: "When your conversation approaches the context window limit, Claude summarizes earlier messages to continue the conversation seamlessly. This means you can have longer, more natural conversations with fewer interruptions. Your full chat history is preserved so Claude can reference it even after summarization."
Context: Las conversaciones que activan la gestion automatica de contexto consumen mas del limite de uso.
Confidence: high
```

```
Claim: El sistema de compaction de Claude Code reserva hasta 20,000 tokens para el summary, calcula umbrales de advertencia y error, y aplica multiples estrategias: auto-compact (resumen proactivo), context collapse (archivar mensajes viejos), snip compaction (remover rangos especificos), y micro-compaction (editar entradas de prompt cache).
Source: Claude Code Pattern 6: Context Management at Scale
URL: https://kenhuangus.substack.com/p/claude-code-pattern-6-context-management
Date: 2026-04-07
Excerpt: "The harness addresses this challenge through multiple complementary strategies. Token counting and estimation tell the system when it is approaching limits. Automatic compaction summarizes old conversation history proactively. Context collapse archives old messages..."
Context: Estas estrategias se aplican en orden: operaciones locales baratas primero, llamadas API caras solo cuando es necesario.
Confidence: medium
```

### 7.3 Memory Tool (Cross-Conversation)

```
Claim: Claude 4 introduce el Memory Tool (memory_20250818) que permite el aprendizaje cross-conversation. Claude puede escribir lo que aprende para referencia futura en un sistema basado en archivos bajo el directorio /memories. Es implementacion client-side que da control total al usuario.
Source: Anthropic Cookbook - Memory & context management
URL: https://platform.claude.com/cookbook/tool-use-memory-cookbook
Date: 2025-05-22
Excerpt: "Claude 4 models introduce powerful context management capabilities: 1. Memory Tool (memory_20250818): Enables cross-conversation learning - Claude can write down what it learns for future reference - File-based system under /memories directory - Client-side implementation gives you full control"
Context: Soportado en: Claude Opus 4.1, Claude Opus 4, Claude Sonnet 4.6, Claude Sonnet 4, Claude Haiku 4.5.
Confidence: high
```

### 7.4 Chat Search y Memory

```
Claim: Claude puede buscar a traves de conversaciones anteriores para encontrar informacion relevante cross-session usando RAG. Tambien puede recordar contexto de chats previos, creando continuidad. La sintesis de memoria se actualiza cada 24 horas.
Source: Claude Help Center - Chat search and memory
URL: https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context
Date: 2026-03-16
Excerpt: "You can now prompt Claude to search through your previous conversations to find and reference relevant information in new chats. Additionally, Claude can remember context from previous chats, creating continuity across your conversations."
Context: El usuario puede ver y editar su memory summary en Settings > Capabilities. Las incognito chats no se guardan ni se incluyen en la memoria.
Confidence: high
```

### 7.5 Context Editing

```
Claim: Claude 4 incluye capacidades de "context editing" que gestionan el contexto automaticamente: tool use clearing (limpiar resultados de herramientas viejas cuando el contexto crece) y thinking management (gestionar bloques de extended thinking).
Source: Anthropic Cookbook - Memory & context management
URL: https://platform.claude.com/cookbook/tool-use-memory-cookbook
Date: 2025-05-22
Excerpt: "Context Editing: Automatically manages context with two strategies: - Tool use clearing (clear_tool_uses_20250919): Clears old tool results when context grows large - Thinking management (clear_thinking_20251015): Manages extended thinking blocks"
Context: Esto permite mantener sesiones largas manejables sin perder informacion critica.
Confidence: high
```

### 7.6 Evaluacion de Trasladabilidad a FaberLoom

**Alto valor:**
- **Compaction automatica**: Resumir conversaciones largas de iteracion para mantenerlas manejables es critico para el tab "Iterar".
- **Memory tool file-based**: El pattern de escribir aprendizajes a archivos para referencia futura es aplicable para mantener preferencias de diseno entre sesiones.
- **Context editing**: Limpiar resultados de herramientas viejas para liberar espacio de contexto.

**Medio valor:**
- **Chat search RAG**: Buscar en historial de iteraciones previas del mismo proyecto.
- **User-editable memory**: Permitir al usuario ver y editar lo que el sistema "recuerda" sobre sus preferencias de diseno.

---

## 8. Patterns Transversales

### 8.1 Conversation Branching / Forking

```
Claim: Claude Code soporta session forking via /branch y --fork-session. Permite crear sesiones independientes desde un punto compartido del historial para explorar tareas en paralelo sin degradar la ventana de contexto principal. Combinado con /btw y /rewind, ayuda a gestionar la "contaminacion de contexto".
Source: AskSurf - Claude Code's Session Forking
URL: https://asksurf.ai/pulse/en/claude-code-session-forking-how-it-works
Date: 2026-03-29
Excerpt: "Session forking builds on Claude Code's architecture... The idea: create independent branches for experimentation or collaboration while keeping your original context intact. Combined with commands like /btw and /rewind, it helps manage what you might call 'context pollution'."
Context: Boris Cherny, creador de Claude Code, revelo dos metodos: /branch dentro de una sesion, o el comando CLI 'claude --resume --fork-session'.
Confidence: high
```

```
Claim: En la interfaz web de Claude, el branching funciona mediante edicion de mensajes anteriores: al editar un mensaje previo, se crea una nueva rama desde ese punto mientras la version original permanece disponible. Es un modelo tipo "version control" para conversaciones.
Source: Jonathan's Substack - Fixing Claude hit the maximum length
URL: https://limitededitionjonathan.substack.com/p/ultimate-guide-fixing-claude-hit
Date: 2025-11-06
Excerpt: "You spot something you want to clarify. Ask your question in a new message. Claude answers. Now go back and edit the message right before that question. Rewrite it... You've just created a branch. The main thread continues from your edited prompt."
Context: Diferentes ramas no comparten contexto antes del punto de division.
Confidence: medium
```

### 8.2 System Prompts y Personalizacion

```
Claim: Claude Code construye el system prompt dinamicamente a partir de multiples capas: instrucciones base del modelo, estilos de output configurados, informacion del entorno (working directory, plataforma, shell), preferencias de idioma, y configuraciones de MCP servers. Se pueden personalizar via output styles, systemPrompt con append, o system prompts completamente custom.
Source: Claude Code Docs - Modifying system prompts
URL: https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts
Date: 2025-09-01
Excerpt: "System prompts define Claude's behavior, capabilities, and response style... Claude Code's system prompt includes: Tool usage instructions and available tools; Code style and formatting guidelines; Response tone and verbosity settings; Security and safety instructions; Context about the current working directory and environment"
Context: Tres metodos de modificacion: output styles (configuraciones persistentes), systemPrompt con append, o custom system prompts completos.
Confidence: high
```

### 8.3 Progressive Disclosure

```
Claim: El sistema de Skills de Claude usa "progressive disclosure": solo ~30-50 tokens por skill se cargan al inicio (nombre + descripcion), con las instrucciones completas cargandose solo cuando una tarea coincide. Un agente con 50 skills usa aproximadamente 1,500-2,500 tokens al inicio.
Source: Firecrawl - How SKILL.md Files Work
URL: https://www.firecrawl.dev/blog/agent-skills
Date: 2026-04-27
Excerpt: "Skills use progressive disclosure: only ~30-50 tokens per skill load at startup, with full instructions loading only when a task matches... Before skills, the standard approach was to stuff all your preferences, conventions, and tool documentation into a system prompt. That prompt loaded every session whether you needed it or not."
Context: La descripcion del skill (no las instrucciones) es lo que determina si se activa o no.
Confidence: high
```

### 8.4 Evaluacion de Trasladabilidad a FaberLoom

**Alto valor:**
- **Conversation branching**: El forking de sesiones permite explorar multiples direcciones de diseno sin perder el hilo principal. Aplicable al tab "Iterar".
- **Progressive disclosure**: Cargar solo lo necesario al inicio y el resto on-demand optimiza el uso del contexto.

---

## 9. Skills y Open Standard (Agent Skills)

### 9.1 Vision General

```
Claim: Las Skills son documentos de proceso reutilizables almacenados como archivos SKILL.md. Fueron creadas por Anthropic y publicadas como estandar abierto en agentskills.io en diciembre 2025. El mismo skill funciona en Claude Code, OpenAI Codex CLI, Gemini CLI, GitHub Copilot, Cursor, VS Code y 20+ plataformas.
Source: Firecrawl - How SKILL.md Files Work
URL: https://www.firecrawl.dev/blog/agent-skills
Date: 2026-04-27
Excerpt: "Originally created by Anthropic and released as an open standard on December 18, 2025, the spec now lives at agentskills.io... The same skill file works across Claude Code, OpenAI Codex CLI, Gemini CLI, GitHub Copilot, Cursor, VS Code, and 20+ other platforms without modification."
Context: El formato es un directorio con SKILL.md (requerido) + scripts/, references/, assets/ (opcionales).
Confidence: high
```

### 9.2 Estructura de Skills

```
Claim: Cada skill sigue la estructura del Agent Skills Specification: YAML frontmatter (name, description) + cuerpo markdown con instrucciones. La descripcion es el trigger condition que el agente usa para decidir si activar el skill.
Source: MindStudio - What Are Claude Code Skills
URL: https://www.mindstudio.ai/blog/what-are-claude-code-skills/
Date: 2026-04-16
Excerpt: "The core design principle: skill.md holds only process steps. Reference context lives in separate files and loads when needed... A good skill.md file is short, clear, and procedural. Each step should describe a discrete action."
Context: skill.md = solo pasos de proceso. brand.md, examples.md, format.md, learnings.md = archivos de referencia cargados on-demand.
Confidence: high
```

### 9.3 Learnings Loop

```
Claim: Un skill bien disenado captura lo que aprende en un archivo learnings.md que se acumula observaciones de cada ejecucion. En la siguiente ejecucion, el skill carga learnings.md como parte de su contexto de referencia, mejorando la calidad de salida con el tiempo sin actualizaciones manuales al proceso central.
Source: MindStudio - What Are Claude Code Skills
URL: https://www.mindstudio.ai/blog/what-are-claude-code-skills/
Date: 2026-04-16
Excerpt: "The mechanism for this is learnings.md — a file that lives inside the skill directory and accumulates observations from each run. After completing a task, Claude can write a short note about what worked, what didn't, and any edge cases it encountered."
Context: Esto se llama "learnings loop" — un mecanismo de feedback ligero que hace que los skills sean auto-mejorables.
Confidence: medium
```

### 9.4 Evaluacion de Trasladabilidad a FaberLoom

**Alto valor:**
- **Skills como SOPs para AI**: Empaquetar conocimiento de dominio (diseno de componentes, guias de estilo) en skills reutilizables es directamente aplicable a FaberLoom.
- **Learnings loop**: El pattern de capturar aprendizajes de cada iteracion para mejorar futuras ejecuciones es aplicable al sistema de "memoria de diseno" de FaberLoom.

---

## 10. Resumen Ejecutivo y Recomendaciones

### Summary Ejecutivo (5 bullets)

1. **Anthropic opera con un modelo de autonomia gradual**: desde el modo "default" (aprobar cada accion) hasta "auto" (clasificador AI aprueba automaticamente acciones seguras), pasando por "plan" (revisar plan antes de ejecutar). Este espectro de control es trasladable directamente a FaberLoom: Configurar = Plan Mode, Iterar = Accept Edits Mode, Sanidad = Default Mode con validaciones.

2. **El "consent fatigue" es un fenomeno documentado**: Anthropic reporta que usuarios aprueban el 93% de prompts de permiso. Esto justifica el diseno de FaberLoom de aprobacion por lote (aprobar/descartar/iterar una iteracion completa) en lugar de por cada micro-accion del agente.

3. **La gestion de contexto es multicapa**: Claude usa compaction automatica, memory tool file-based, context editing, y RAG para manejar conversaciones largas. FaberLoom deberia implementar compaction/resumen automatico en sesiones de iteracion largas y mantener un "design memory" persistente por proyecto.

4. **Los Skills como estandar abierto demuestran que empaquetar conocimiento de dominio en documentos de proceso reutilizables funciona**: El pattern de SKILL.md con progressive disclosure, learnings loop, y activation por descripcion es aplicable para encapsular patrones de diseno, guias de estilo, y reglas de componentes.

5. **El clasificador de 2 etapas (filtro rapido + razonamiento profundo condicional) con deny-and-continue es un pattern de seguridad eficiente**: El 0.4% FPR y el manejo de bloqueos sin detener la sesion son patterns aplicables al sistema de validacion de "Sanidad" de FaberLoom.

### Gaps Identificados

| Gap | Descripcion | Prioridad |
|-----|-------------|-----------|
| **No hay evidencia de "approval flow visual"** | No se encontro documentacion sobre un sistema visual de aprobacion tipo "tarjetas por revisar" como el que FaberLoom necesita | Alta |
| **No hay "iteracion con checkpoints" documentado** | Aunque existe version history en Artifacts, no se encontro un sistema de checkpoints con aprobacion explicita entre pasos | Media |
| **Cowork sigue en research preview** | La funcionalidad mas agentica de Anthropic esta en preview limitado a macOS/Max, lo que limita la evidencia de uso a escala | Media |
| **No hay comparativa directa con flujos de design systems** | La mayoria de la documentacion se enfoca en coding, no en generacion de componentes de diseno | Baja |
| **Compliance API no cubre Cowork** | Para workloads regulados, Cowork no tiene auditoria centralizada | Baja (para FaberLoom actual) |

### Recomendaciones Especificas con Confidence

#### Alta Confianza

1. **Implementar el espectro de modos de permiso en FaberLoom** [Confidence: high]
   - Tab "Configurar" = modo "plan" (Claude propone configuracion, usuario revisa y aprueba antes de generar)
   - Tab "Iterar" = modo "acceptEdits" (generacion automatica con preview, usuario aprueba/descarta/itera)
   - Tab "Sanidad" = modo "default" (cada cambio requiere aprobacion explicita, con validaciones automaticas)

2. **Usar aprobacion por lote, no por accion** [Confidence: high]
   - Basado en el consent fatigue documentado (93% approval rate), diseñar el flujo para que el usuario revise una iteracion completa (componente generado) en lugar de aprobar cada micro-paso.

3. **Implementar RAG automatico para KB de diseno** [Confidence: high]
   - Cuando el sistema de diseno del usuario excede la ventana de contexto, activar automaticamente RAG para buscar en documentacion, guias de estilo, y componentes existentes.

4. **Taxonomia de errores con retry selective** [Confidence: high]
   - Errores de LLM (rate limit, timeout) -> retry con exponential backoff
   - Errores de validacion de componente -> no retry, reportar a usuario con detalle
   - Errores de sintaxis generada -> retry automatico con instruccion de correccion (max 3 intentos)

#### Media Confianza

5. **Memory tool file-based para preferencias de diseno** [Confidence: medium]
   - Escribir aprendizajes de cada sesion de iteracion a archivos de memoria por proyecto, que se cargan en sesiones futuras del mismo proyecto.

6. **Progressive disclosure para instrucciones de diseno** [Confidence: medium]
   - Cargar solo guias de estilo relevantes al componente actual, no todo el design system completo.

7. **Plan Mode con checkpointing visual** [Confidence: medium]
   - Antes de generar, Claude presenta un plan estructurado de lo que va a crear (archivos, estructura, dependencias). El usuario puede editar, aprobar, o solicitar cambios.

8. **Context compaction automatico en iteraciones largas** [Confidence: medium]
   - Despues de N iteraciones, resumir el historial manteniendo solo las decisiones clave y el estado actual del componente.

#### Baja Confianza / Requiere Validacion

9. **Clasificador de 2 etapas para validacion de componentes** [Confidence: low-medium]
   - Un filtro rapido para componentes "obviamente correctos" + revision profunda solo para casos borderline. Requiere validacion con datos reales de calidad de componentes.

10. **Integration con version control para design iterations** [Confidence: low-medium]
    - Cada iteracion genera una "rama" que puede compararse con otras antes de mergear. Mas complejo de implementar, valor incierto.

---

## Anexo: Fuentes Adicionales

### Documentacion Oficial Anthropic
- Claude Help Center: https://support.claude.com
- Claude Code Docs: https://code.claude.com/docs
- Anthropic Console: https://console.anthropic.com
- Agent Skills Spec: https://agentskills.io

### Papers y Publicaciones Tecnicas
- "Trustworthy Agents in Practice" (Anthropic, April 2026) — NIST filing
- "Our Framework for Developing Safe and Trustworthy Agents" (Anthropic, August 2025)
- "Measuring AI agent autonomy in practice" (Anthropic, February 2026)

### Repositorios Relevantes
- `anthropics/skills` — Skills oficiales de referencia
- `anthropics/claude-code` — Issue tracker con feature requests

---

*Documento generado el 2026-05-15. Las URLs y fechas reflejan el estado del conocimiento disponible en la fecha de investigacion.*
