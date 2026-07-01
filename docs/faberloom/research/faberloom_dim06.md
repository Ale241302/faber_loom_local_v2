# DIMENSIÓN 6: Anthropic/Claude Design Philosophy — Chat-First y Tool-Use UI

> Fecha de investigación: Julio 2025
> Investigador: Agente de investigación
> Fuentes: 30+ búsquedas independientes, documentación oficial Anthropic, GitHub repos, blogs de ingeniería, podcasts, análisis de UI

---

## 1. CHAT-FIRST UI: ESTRUCTURA DEL LAYOUT

### 1.1 Layout General de claude.ai

```
Claim: Anthropic diseña claude.ai con un layout de tres columnas: sidebar izquierda para historial/navegación, área central para el chat, y panel derecho contextual (Artifacts, Project Knowledge, o Preview).
Source: Claude Help Center + Análisis de UI
URL: https://support.claude.com/en/articles/9517075-what-are-projects
Date: 2026-03-16
Excerpt: "Projects allow you to create self-contained workspaces with their own chat histories and knowledge bases. Within each project, you can upload documents, provide context, and have focused chats with Claude."
Context: En Projects, el knowledge base aparece en el panel derecho. En Artifacts, el panel derecho muestra el preview/code. En chat normal, el área central ocupa todo el espacio disponible.
Confidence: high
```

```
Claim: El diseño de claude.ai utiliza una paleta de colores "cream + coral" deliberadamente cálida, distintiva del gris frío de OpenAI y el azul corporativo de Microsoft. El canvas es #faf9f5 (tinted cream).
Source: DesignMD - Documentación de Design System
URL: https://www.designmd.co/d/claude
Date: 2025
Excerpt: "Claude.com is the warmest, most editorial interface in the AI-product category. The base atmosphere is a tinted cream canvas ({colors.canvas} — #faf9f5) — distinctly warm, deliberately not the cool gray-white that every other AI brand uses."
Context: Este es un diferenciador de marca intencional. El coral (#cc785c) se usa en CTAs y el wordmark. La tipografía es slab-serif display ("Copernicus" / Tiempos Headline) weight 400 con negative letter-spacing.
Confidence: high
```

### 1.2 Sidebar y Navegación

```
Claim: La sidebar izquierda de claude.ai muestra el historial de chats recientes, acceso a Projects, y funciones de organización. Los usuarios pueden renombrar chats para mejor organización.
Source: YouTube tutorial + Claude Help Center
URL: https://www.youtube.com/watch?v=h35HxkuhWkE
Date: 2026-03-10
Excerpt: "The first step is to look at the left-hand side of your screen. That vertical bar displays your recent chat history automatically... click on the button labeled 'Chats' located in that sidebar. Once you click this, the interface expands to show your complete conversation history."
Context: La sidebar es colapsable/expansible. Tiene search bar en la parte superior para filtrar conversaciones. Los usuarios pueden "star" projects para acceso rápido.
Confidence: high
```

```
Claim: Los chats se pueden mover entre projects usando un dropdown menu, lo que permite reorganizar conversaciones según evolucionan los proyectos.
Source: Claude Help Center
URL: https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects
Date: 2026-03-16
Excerpt: "You can move a standalone chat into a project by clicking on the dropdown arrow next to the chat name, then 'Add to project'"
Context: Esta funcionalidad de "organización fluida" es clave para workflows B2B donde una conversación puede migrar de contexto.
Confidence: high
```

### 1.3 Input Box y Composición

```
Claim: El input box de claude.ai está diseñado para ser generoso (~300px de altura) pero no intimidante, con bordes redondeados y sombra suave. Incluye un ícono "+" para adjuntar contexto (archivos, imágenes) que se muestran como chips removibles.
Source: AI UX Gallery + Dear Designer blog
URL: https://www.aiuxplayground.com/gallery/claude-context-chips
Date: 2025
Excerpt: "Claude allows users to attach files, images, and other context sources to conversations, displayed as removable chips. Plus (+) icon below input field opening context attachment menu."
Context: Los chips muestran el tipo de archivo con íconos apropiados. Se pueden remover individualmente. El input usa placeholder text en tono conversacional ("How can I help you today?"). En Claude 4, el input también tiene selector de modelo, effort mode, y permission mode.
Confidence: high
```

```
Claim: La homepage de claude.ai muestra un toggle Chat/Cowork que refleja la dualidad de la plataforma: conversación libre vs. workspace colaborativo para trabajo estructurado.
Source: Screenshot directo de claude.ai
URL: https://claude.ai
Date: 2025-07
Excerpt: (Visual) Toggle "Chat" / "Cowork" en la parte superior derecha del área de contenido.
Context: Cowork es el modo workspace donde Claude trabaja con archivos locales y tareas multi-paso. El toggle indica que Anthropic ve el chat como el modo "rápido/brainstorm" y Cowork como el modo "proyecto estructurado".
Confidence: high
```

---

## 2. TOOL-USE UI: RENDERIZADO DE TOOL CALLS

### 2.1 Patrón Expandible/Collapsible

```
Claim: Claude Code (terminal) renderiza tool calls con tres modos de visualización: Normal (resumen colapsado), Verbose (todos los detalles), y Summary (solo respuestas finales). El modo por defecto colapsa tool calls en líneas de resumen.
Source: Claude Code Docs
URL: https://code.claude.com/docs/en/desktop
Date: 2025-09-01
Excerpt: "Mode: Normal - Tool calls collapsed into summaries, with full text responses. Verbose - Every tool call, file read, and intermediate step Claude takes. Summary - Only Claude's final responses and the changes it made."
Context: Se cambia con Ctrl+O o desde un dropdown. En modo Normal, un tool call aparece como: "Edited 5 files +27 -23, committed bbbe19" — una línea que se puede expandir.
Confidence: high
```

```
Claim: En la VS Code extension, los tool calls se renderizan como bloques IN/OUT con monospaced font, pero los usuarios reportan que necesitan mejor jerarquía visual — mismos tamaño/peso que el texto de respuesta del asistente.
Source: GitHub issue - VS Code extension
URL: https://github.com/anthropics/claude-code/issues/26592
Date: 2026-02-18
Excerpt: "Tool call outputs (Bash, Grep, Read, Edit, etc.) are rendered with the same font size, weight, and visual prominence as the assistant's actual response text. This makes the chat very hard to read."
Context: El issue solicita: collapsed by default, smaller font size/muted color, compact single-line summary, y que el texto del asistente sea visualmente dominante. Anthropic ha iterado en esto — en versiones recientes los tool calls se colapsan agresivamente.
Confidence: high
```

### 2.2 Jerarquía Visual y Color-Coding

```
Claim: En herramientas de terceros que visualizan Claude Code (como Cogpit), los tool calls usan color-coding: Read=azul, Write=verde, Edit=amber, Bash=rojo. Cada uno es expandible con full input/output.
Source: Dev.to - Cogpit review
URL: https://dev.to/gentritbiba/claude-code-is-my-favorite-dev-tool-i-was-flying-blind-until-i-found-cogpit-1edn
Date: 2026-03-01
Excerpt: "Tool calls with color-coded badges — Read is blue, Write is green, Edit is amber, Bash is red. Each one expandable with full input/output. Edit diffs — actual line-by-line diffs with syntax highlighting, not raw JSON."
Context: Este color-coding es un patrón emergente en el ecosistema, no necesariamente oficial de Anthropic, pero refleja cómo los usuarios esperan visualizar tool calls.
Confidence: medium
```

### 2.3 Tool Call Approval / Human-in-the-Loop

```
Claim: Claude Code usa un sistema de permisos de tres niveles: Read-only (sin aprobación), File modification (aprobación requerida, "hasta fin de sesión"), y Bash commands (aprobación por proyecto y comando).
Source: Claude Code Docs - Permissions
URL: https://code.claude.com/docs/en/permissions
Date: 2025-09-01
Excerpt: "Read-only: File reads, Grep — Approval required: No. Bash commands: Shell execution — Approval required: Yes — 'Yes, don't ask again' behavior: Permanently per project directory and command. File modification: Edit/write files — Approval required: Yes — Until session end."
Context: Este diseño de "gradual trust" es fundamental: herramientas de solo lectura nunca piden permiso, las de escritura piden una vez por sesión, y los comandos de shell piden por directorio/comando específico.
Confidence: high
```

```
Claim: Claude Code introdujo "Auto Mode" (research preview, marzo 2026) — un permission classifier basado en un modelo separado que evalúa cada tool call en tiempo real y decide auto-aprobar, pedir confirmación, o bloquear, basado en tipo de acción, parámetros, reversibilidad, blast radius y contexto de conversación.
Source: MindStudio Blog + Digital Applied
URL: https://www.mindstudio.ai/blog/what-is-claude-code-auto-mode-permission-classifier/
Date: 2026-04-01
Excerpt: "The permission classifier is the core mechanism behind auto mode. It's a model-based system that evaluates each tool call Claude Code wants to make and assigns it a risk level before execution... Based on this evaluation, each action gets routed one of three ways: auto-approve, prompt for confirmation, or block entirely."
Context: Auto mode es una respuesta a la fatiga de aprobación. En lugar de todo-o-nada, usa un modelo separado para decidir. Esto es altamente trasladable a B2B operativo donde acciones de bajo riesgo deberían auto-ejecutarse.
Confidence: high
```

---

## 3. STREAMING RESPONSES

### 3.1 Texto en Tiempo Real

```
Claim: Anthropic implementa streaming token-by-token para reducir tiempos de espera y crear interacciones más naturales. Tool use con streaming está disponible en la Messages API.
Source: Anthropic Blog - Tool Use GA
URL: https://claude.com/blog/tool-use-ga
Date: 2024
Excerpt: "Tool use with streaming reduces wait times to create more engaging interactions: Streaming enables real-time responses in applications like customer support chatbots for smoother, more natural conversations."
Context: El streaming no solo aplica al texto final — también a tool results. Las aplicaciones pueden mostrar "Running bash command..." → "Result: Hello, World!" progresivamente.
Confidence: high
```

### 3.2 Thinking Blocks (Extended Thinking)

```
Claim: Los modelos de "extended thinking" de Claude muestran su razonamiento interno como bloques de texto en gris/cursiva, collapsible, por encima de la respuesta final. Se puede toggle con Ctrl+O (verbose mode).
Source: Wmedia - Show Thinking in Claude Code
URL: https://wmedia.es/en/tips/claude-code-verbose-output-see-thinking
Date: 2026-02-15
Excerpt: "As Claude streams its response, you'll see the thinking blocks rendered in gray italic text above the actual output. This is the model's internal reasoning — not a summary, the actual chain of thought."
Context: Este patrón de "transparencia del razonamiento" es distintivo. El usuario puede ver cómo el modelo está abordando el problema y abortar (Ctrl+C) si detecta una mala suposición antes de que se materialice en código/archivos.
Confidence: high
```

```
Claim: Existe un feature request activo para stream thinking output en tiempo real durante interactive mode, ya que actualmente el CLI no muestra feedback durante la fase de thinking — solo un spinner.
Source: GitHub issue - claude-code
URL: https://github.com/anthropics/claude-code/issues/30660
Date: 2026-03-04
Excerpt: "When Claude is thinking (extended thinking / reasoning), the CLI shows no feedback until the thinking phase completes and the response begins streaming. For longer reasoning chains this means staring at a spinner with no indication of progress."
Context: Esto muestra una tensión de diseño: ¿mostrar el proceso de pensamiento en tiempo real (más transparencia pero más ruido visual) o mantenerlo oculto hasta completar (más limpio pero menos feedback)?
Confidence: high
```

---

## 4. FILE UPLOADS

### 4.1 Drag & Drop y Paste

```
Claim: claude.ai soporta múltiples métodos de upload: drag & drop directo en la ventana de chat, botón de attachment (paperclip/+), y paste de imágenes desde clipboard.
Source: Claude Help Center
URL: https://support.claude.com/en/articles/8241126-upload-files-to-claude
Date: 2026-04-22
Excerpt: "Click 'Open' to attach the files, or drag and drop the files directly into the chat window. You can also copy images and paste them from your clipboard."
Context: Límites: 30MB por archivo, hasta 20 archivos simultáneamente en chat. Soporta PDF, DOCX, TXT, CSV, imágenes (JPEG, PNG, GIF, WebP). Los PDFs >100 páginas se procesan como texto solo.
Confidence: high
```

### 4.2 Context Chips

```
Claim: Los archivos adjuntos se muestran como "chips" removibles sobre el input box, con ícono del tipo de archivo, nombre truncado, y un botón X para remover individualmente.
Source: AI UX Gallery - Claude Context Chips
URL: https://www.aiuxplayground.com/gallery/claude-context-chips
Date: 2025
Excerpt: "Context sources displayed as removable chips with icons. Multiple context sources can be attached simultaneously. Chips show file type with appropriate icons. Individual removal provides granular control."
Context: Este patrón de chips es estándar en la industria pero la implementación de Claude es particularmente limpia — los chips no interfieren con el área de texto, se apilan horizontalmente debajo del input.
Confidence: high
```

### 4.3 Projects Knowledge Base

```
Claim: En Claude Projects, los archivos se suben a un "Project Knowledge" panel en el lado derecho. Son persistentes across todas las conversaciones del project. Se activa RAG automáticamente cuando se acerca al límite de contexto.
Source: Claude Help Center
URL: https://support.claude.com/en/articles/9517075-what-are-projects
Date: 2026-03-16
Excerpt: "You can upload relevant documents, text, code, or other files to a project's knowledge base, which Claude will use to better understand the context and background for your individual chats within that project."
Context: El knowledge base aparece en el panel derecho. Los archivos se referencian automáticamente — el usuario no necesita mencionarlos explícitamente en cada mensaje. Esto es equivalente a tener un "KB persistente" vinculado al workspace.
Confidence: high
```

---

## 5. ARTIFACTS: PANEL LATERAL Y RENDERIZADO

### 5.1 Arquitectura del Panel

```
Claim: Artifacts aparece como un panel deslizable desde la derecha que se abre cuando Claude detecta contenido sustancial (código, documentos, visualizaciones). La conversación principal se mantiene limpia — el contenido sustancial vive en su propio workspace.
Source: GitHub - claude-quickstarts
URL: https://github.com/anthropics/claude-quickstarts/blob/main/autonomous-coding/prompts/app_spec.txt
Date: 2025
Excerpt: "1. Assistant generates artifact in response · 2. Artifact panel slides in from right · 3. Content renders (code with highlighting or live preview) · 4. User can..."
Context: El panel tiene dos modos de visualización: Preview (renderizado visual) y Code (código fuente con syntax highlighting). Se puede toggle entre ellos.
Confidence: high
```

### 5.2 Preview vs Code

```
Claim: Los Artifacts soportan toggle Preview/Code en la parte superior del panel. En Preview se renderiza HTML/React/JS como interfaz funcional. En Code se muestra el código fuente. También soportan version history.
Source: Albato - How to use Claude Artifacts
URL: https://albato.com/blog/publications/how-to-use-claude-artifacts-guide
Date: 2026-04-29
Excerpt: "At the top of the Claude Artifact window, you'll find a toggle to switch between two viewing modes: Preview: Displays the result. Code: Shows the underlying source code."
Context: Actions disponibles: Download, Copy, Publish artifact, View version history. La versión history permite revertir a versiones anteriores. Los artifacts se pueden publicar y compartir vía link.
Confidence: high
```

### 5.3 Tipos de Artifacts

```
Claim: Claude Artifacts soporta múltiples tipos: código/scripts, SVG vector graphics, Mermaid diagrams, interactive web elements (HTML/React), documents/formatted content (Markdown), y PDF rendering.
Source: MindStudio - On-Demand Generative UI
URL: https://www.mindstudio.ai/blog/what-is-claude-interactive-visualization-generative-ui/
Date: 2026-03-14
Excerpt: "Claude's Artifacts feature changes this. Claude can generate self-contained, live interfaces that render directly in a preview panel alongside the conversation. You see a working thing, not instructions for building one."
Context: Los artifacts corren en un sandboxed environment — no pueden acceder a archivos locales ni hacer requests a APIs externas. Esto es una decisión de seguridad deliberada.
Confidence: high
```

### 5.4 Live Artifacts (2026)

```
Claim: Claude Live Artifacts (introducido abril 2026) son dashboards y trackers persistentes que se refrescan con datos actuales cada vez que se reabren. Se conectan a fuentes de datos vía MCP.
Source: Eigent - Claude Live Artifacts Guide
URL: https://www.eigent.ai/blog/claude-live-artifacts-guide
Date: 2026-04-21
Excerpt: "Claude Live Artifacts take this a step further by making those artifacts stateful and connected. They can pull from your apps and files, refresh when you open them, and behave less like static snapshots and more like live tools you return to repeatedly."
Context: Los Live Artifacts se conectan a Google Calendar, Gmail, Slack, y otros servicios vía MCP. Son útiles para KPI monitoring, pipeline tracking, y content calendars.
Confidence: high
```

---

## 6. MODEL CONTEXT PROTOCOL (MCP): INTEGRACIÓN DE TOOLS EXTERNAS

### 6.1 Hammer Icon y Tool Picker

```
Claim: En Claude Desktop, cuando MCP servers están configurados, aparece un ícono de martillo (🔨) en la esquina inferior derecha del input box. Al hacer click, muestra una lista de tools disponibles agrupadas por servidor.
Source: Taskade - MCP Servers Guide
URL: https://www.taskade.com/blog/mcp-servers
Date: 2026-04-09
Excerpt: "After relaunch, look for the small hammer icon in the chat input — that is the MCP tool indicator. Click the hammer icon. You should see a list of available tools grouped by server."
Context: Este patrón de "tool picker icon" es consistente: hammer = tools disponibles. Si la lista está vacía, el server falló al iniciar. Los tools se agrupan por servidor MCP (ej: Filesystem, Git, etc.).
Confidence: high
```

### 6.2 Arquitectura MCP en la UI

```
Claim: MCP sigue una arquitectura client-server donde el Host Process (Claude Desktop) maneja múltiples MCP Clients, cada uno conectado a un MCP Server. La seguridad es central: el host aprueba cada servidor y controla permisos.
Source: Medium - MCP Deep Dive
URL: https://medium.com/@amanatulla1606/anthropics-model-context-protocol-mcp-a-deep-dive-for-developers-1d3db39c9fdc
Date: 2025-03-21
Excerpt: "A significant aspect of the MCP architecture is the emphasis on security and controlled access. The host instantiates clients and approves servers, allowing users and organizations to strictly manage what an AI assistant is allowed to connect to."
Context: La comunicación usa JSON-RPC con transporte Stdio (procesos locales) o HTTP con SSE (servicios remotos). Los servidores operan independientemente con responsabilidades enfocadas.
Confidence: high
```

### 6.3 Tool Discovery y Deferred Loading

```
Claim: Anthropic introdujo "Tool Search Tool" que permite a Claude descubrir dinámicamente tools de una librería de miles sin consumir context window. Los tools marcados con defer_loading: true solo se cargan bajo demanda.
Source: Anthropic Engineering Blog
URL: https://www.anthropic.com/engineering/advanced-tool-use
Date: 2025-11-24
Excerpt: "The Tool Search Tool lets Claude dynamically discover tools instead of loading all definitions upfront. You provide all your tool definitions to the API, but mark tools with defer_loading: true to make them discoverable on-demand."
Context: Esto resuelve el problema de "tool library explosion" — un agent puede tener acceso a 1000+ tools pero solo cargar las relevantes para la tarea actual. El usuario no ve esto directamente pero mejora la latencia.
Confidence: high
```

---

## 7. PRINCIPIOS DE DISEÑO DE ANTHROPIC

### 7.1 Safety-First y User Control

```
Claim: Anthropic prioriza safety y alignment como "prerrequisitos de capability, no limitaciones post-hoc". En Claude Code, los humanos pueden detener a Claude en cualquier momento y redirigir su enfoque. Permisos read-only por defecto.
Source: Anthropic - Safe and Trustworthy Agents Framework
URL: https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents
Date: 2025-08-04
Excerpt: "In Claude Code, humans can stop Claude whenever they want and redirect its approach. It has read-only permissions by default, meaning it can analyze and review information... but must ask for human approval before taking any actions that modify code or systems."
Context: Este framework establece que "agents must be able to work autonomously... But humans should retain control over how their goals are pursued, particularly before high-stakes decisions."
Confidence: high
```

### 7.2 Diseñar con Datos Reales, No Mockups

```
Claim: Joel Lewenstein (Head of Product Design, Anthropic) afirma que diseñar con datos reales y ambientes de producción es "meaningfully better than designing with static Figma mockups" para productos de IA, donde la magia está en la imprevisibilidad de la respuesta del modelo.
Source: Academy UX Podcast - Joel Lewenstein Interview
URL: https://blog.academyux.com/learn-how-anthropic-designs-for-ai-joel-lewenstein-head-of-product-design-anthropic/
Date: 2024-02-12
Excerpt: "We can make seven Figma screens where you press some buttons and the model responds, but we've just typed out what it will say — that doesn't capture the failure modes, and it doesn't capture the peeking-behind-the-curtain moment when the response is really good."
Context: El equipo de diseño de Anthropic es pequeño (~3 designers). No usan roadmaps largos — usan un "football playbook" de features listas para deployar según las capacidades de los nuevos modelos.
Confidence: high
```

### 7.3 Chat como Apertura, GUI para Pasos Intermedios

```
Claim: Joel Lewenstein opina que el chat es "wonderful for the free-form, I'm going to brain-dump all the things I want to happen opening move, but much weaker for intermediate steps". 40 años de GUI craft siguen siendo relevantes.
Source: Academy UX Podcast + Fast Company
URL: https://blog.academyux.com/learn-how-anthropic-designs-for-ai-joel-lewenstein-head-of-product-design-anthropic/
Date: 2024-02-12
Excerpt: "Chat is wonderful for 'the free-form, I'm going to brain-dump all the things I want to happen' opening move, but much weaker for intermediate steps. 'We've spent 40 years making graphical user interfaces — I can't imagine none of that is relevant in the future.'"
Context: Anthropic está explorando "structured, parameterized prompts" como dirección — GUI layered back onto chat. Menciona a Respell como ejemplo que convierte prompts en "black boxes with typed inputs".
Confidence: high
```

```
Claim: Anthropic prefiere "four really awesome products for four different types of people" en lugar de un solo hero interface. Cada producto (claude.ai, Claude Code, Excel plugin, Chrome extension) comparte un design language pero es bespoke para su audience.
Source: Fast Company Interview
URL: https://fastcompany.com/91501353/ai-changed-design-forever-now-what
Date: 2026-05-04
Excerpt: "We would rather, at this point, have four really awesome products for four different types of people, and then figure out later what to do, because it just lets us learn faster, right?"
Context: Esta filosofía de "productos especializados vs. plataforma única" es relevante para FaberLoom: en lugar de forzar todo en chat, tener interfaces especializadas para diferentes tareas operativas.
Confidence: high
```

### 7.4 Simplicidad y Restricción Intencional

```
Claim: El post de ingeniería de Anthropic sobre harness design es explícito: "Find the simplest solution possible, and only increase complexity when needed." La empresa empuja por restricción intencional.
Source: Petronella Tech - Claude Design Principles
URL: https://petronellatech.com/blog/claude-design-principles/
Date: 2025
Excerpt: "Anthropic's engineering post on harness design is explicit: 'Find the simplest solution possible, and only increase complexity when needed.'"
Context: Esto se refleja en la UI de claude.ai: no hay features innecesarias, no hay configuraciones complejas por defecto. Cada feature debe justificar su complejidad.
Confidence: medium
```

### 7.5 Honestidad sobre Incertidumbre

```
Claim: Una decisión de diseño distintiva de Anthropic es que Claude sea explícitamente honesto sobre su incertidumbre — surface trade-offs en lugar de hacer elecciones silenciosas. Esto lo hace más valioso en contextos profesionales.
Source: Adventure PPC - Hidden Architecture of Claude Code
URL: https://adventureppc.com/blog/the-hidden-architecture-of-claude-code-how-anthropic-built-an-ai-that-actually-understands-instructions
Date: 2026-04-25
Excerpt: "This is why Claude Code's honesty about uncertainty is a feature, not a limitation. It's why its tendency to surface trade-offs rather than making silent choices makes it more valuable in professional contexts, not less."
Context: En contextos B2B operativos, esto es crítico: los usuarios necesitan entender los riesgos y trade-offs de las acciones del agente, no solo confiar en que "todo está bien".
Confidence: high
```

---

## 8. PATRONES ESPECÍFICOS DE CLAUDE CODE DESKTOP/WEB

### 8.1 Paneles Arrastrables y Workspace Flexible

```
Claim: Claude Code Desktop permite arrastrar paneles (chat, diff, preview, terminal, file, plan, tasks, subagent) en cualquier layout. Los usuarios pueden reorganizar su workspace según la tarea.
Source: Claude Code Docs
URL: https://code.claude.com/docs/en/desktop
Date: 2025-09-01
Excerpt: "The Code tab is built around panes you can arrange in any layout: chat, diff, preview, terminal, file, plan, tasks, and subagent. Drag a pane by its header to reposition it, or drag a pane edge to resize it."
Context: Esto es diferente de claude.ai web — Claude Code Desktop es más como un IDE con workspace flexible. Los paneles se pueden cerrar con Cmd+\ y abrir desde el menú Views.
Confidence: high
```

### 8.2 Diff-First Edits

```
Claim: Claude Code muestra ediciones como inline diffs con syntax highlighting antes de aplicarlas. El usuario puede aceptar, rechazar, o modificar el diff. Hay one-click revert.
Source: Claude Code GUI Extension
URL: https://marketplace.visualstudio.com/items?itemName=MaheshKok.claude-code-gui
Date: 2026-05-10
Excerpt: "Diff-first edits — inline diffs, open-in-VS Code diff, and one-click revert."
Context: Este patrón de "preview antes de aplicar" es fundamental para operaciones destructivas. En B2B operativo, cualquier acción que modifique datos debería mostrar un diff/confirm antes de ejecutar.
Confidence: high
```

---

## 9. EVALUACIÓN DE TRASLADABILIDAD A B2B OPERATIVO (FABERLOOM)

### 9.1 Patrones Altamente Trasladables

| Patrón | Trasladabilidad | Notas |
|--------|----------------|-------|
| **Tool calls collapsible** | ⭐⭐⭐⭐⭐ | Esencial para B2B: mostrar resumen + expandir para detalles. Reduce ruido visual. |
| **Permission tiers (read/edit/execute)** | ⭐⭐⭐⭐⭐ | Crítico para operaciones B2B: lectura auto, escritura con confirmación, ejecución con aprobación explícita. |
| **Context chips para uploads** | ⭐⭐⭐⭐⭐ | Los adjuntos deben ser visibles como chips removibles. Múltiples archivos simultáneos. |
| **Knowledge base persistente** | ⭐⭐⭐⭐⭐ | FaberLoom ya es KB-first; el panel derecho de Project Knowledge valida este enfoque. |
| **Artifacts panel lateral** | ⭐⭐⭐⭐ | Output sustancial (reportes, dashboards, código) debería renderizarse en panel separado, no en el chat stream. |
| **View modes (Normal/Verbose/Summary)** | ⭐⭐⭐⭐ | Diferentes roles necesitan diferentes niveles de detalle. Power users = verbose; managers = summary. |
| **Thinking blocks visibles** | ⭐⭐⭐⭐ | Transparencia del razonamiento = confianza en contextos operativos. |
| **Auto Mode / Permission classifier** | ⭐⭐⭐⭐ | Modelo separado que evalúa riesgo de cada acción. Aplicable a operaciones B2B de diferente criticidad. |

### 9.2 Patrones Moderadamente Trasladables

| Patrón | Trasladabilidad | Notas |
|--------|----------------|-------|
| **Cream/coral aesthetic** | ⭐⭐⭐ | La identidad visual de FaberLoom debería ser propia, pero el principio de "calidez deliberada" vs "corporativo frío" aplica. |
| **Chat-first como default** | ⭐⭐⭐ | El chat es bueno para "brain dump" inicial pero insuficiente para operaciones estructuradas. Necesita GUI para pasos intermedios. |
| **MCP tool picker (hammer icon)** | ⭐⭐⭐ | Aplicable si FaberLoom integra tools externas. El patrón de ícono de herramienta + lista agrupada es bueno. |
| **Diff-first para ediciones** | ⭐⭐⭐ | Aplica a modificaciones de datos/configuraciones, pero no a todas las operaciones. |
| **Streaming token-by-token** | ⭐⭐⭐ | Bueno para percepción de velocidad, pero en B2B muchas operaciones son batch y no necesitan streaming. |

### 9.3 Patrones con Adaptación Significativa Requerida

| Patrón | Trasladabilidad | Notas |
|--------|----------------|-------|
| **Claude Cowork workspace** | ⭐⭐ | Requiere reimaginar para operaciones específicas de FaberLoom (no coding). El principio de "tareas long-running con archivos" aplica. |
| **Live Artifacts** | ⭐⭐ | Los dashboards persistentes son relevantes, pero requieren conexión a datos operativos reales de FaberLoom. |
| **Computer Use API** | ⭐ | Demasiado experimental para B2B operativo. Requiere supervision constante. |

---

## 10. RECOMENDACIONES ESPECÍFICAS PARA FABERLOOM

### R1: Sistema de Permisos de Tres Niveles (Confidence: HIGH)
Implementar el patrón Claude Code de permission tiers:
- **Tier 1 (Auto)**: Consultas al KB, búsquedas, lectura de datos — sin aprobación
- **Tier 2 (Confirmar)**: Crear/editar registros, generar reportes, modificar configuraciones — aprobación con "no volver a preguntar esta sesión"
- **Tier 3 (Aprobación explícita)**: Operaciones destructivas, integraciones externas, acciones con blast radius amplio — siempre requiere aprobación

### R2: Tool Calls Collapsible con Color-Coding (Confidence: HIGH)
Renderizar las operaciones del agent como bloques colapsables:
- Estado: Ejecutando → Completo → Error
- Color: según tipo de operación (lectura=azul, escritura=verde, ejecución=amber, error=rojo)
- Default: colapsado a una línea de resumen
- Expandible: para ver full input/output (útil para debugging/auditoría)

### R3: Panel Lateral para Output Sustancial (Confidence: HIGH)
Cuando el agente genera: reportes, dashboards, código, documentos — mostrarlos en un panel derecho (modo Artifacts), no como texto en el chat stream. El chat se mantiene como "conversación de control", el panel lateral como "workspace de output".

### R4: Thinking Blocks / Razonamiento Visible (Confidence: MEDIUM-HIGH)
Mostrar el razonamiento del agente antes de ejecutar acciones (especialmente Tier 2/3). Esto aumenta la confianza del usuario operativo y permite abortar si el razonamiento es incorrecto. Usar estilo visual distintivo (gris, cursiva, collapsible).

### R5: Context Chips Persistentes para KB Attachments (Confidence: HIGH)
Los documentos/URLs referenciados del KB deberían aparecer como chips visibles sobre el input. Esto cumple el requisito de "upload visible siempre" de FaberLoom. Múltiples chips, cada uno removible individualmente.

### R6: View Mode Selector por Usuario/Rol (Confidence: MEDIUM)
Permitir que cada usuario elija su nivel de detalle:
- **Summary**: Solo respuestas finales y acciones tomadas (para managers)
- **Normal**: Resumen de tool calls + respuestas completas (default)
- **Verbose**: Todo el razonamiento, tool calls completos, thinking blocks (para power users/IT)

### R7: Auto-Approval Basado en Clasificador (Confidence: MEDIUM)
A largo plazo, implementar un clasificador de riesgo (similar a Claude Code Auto Mode) que auto-approve operaciones de bajo riesgo basándose en: tipo de acción, datos afectados, reversibilidad, y contexto histórico de aprobaciones del usuario.

---

## 11. SUMMARY EJECUTIVO

- **Anthropic diseña para "confianza incremental"**: Claude empieza con permisos read-only y pide aprobación antes de cualquier acción destructiva. El usuario puede conceder permisos persistentes para tareas de rutina. Este sistema de "gradual trust" es el patrón más trasladable a B2B operativo.

- **La UI de tool calls es un problema activo**: Anthropic está iterando agresivamente en cómo mostrar tool calls — de bloques IN/OUT expandidos a líneas de resumen colapsadas. La dirección es clara: menos ruido visual, más jerarquía, modos de visualización adaptables. FaberLoom debería saltar directamente a la solución más pulida (collapsible + color-coded).

- **Chat ≠ interfaz final**: Joel Lewenstein (Head of Design, Anthropic) es explícito: "Chat es excelente para el brain dump inicial pero débil para pasos intermedios." Los 40 años de GUI siguen siendo relevantes. FaberLoom no debería forzar todo al chat — debería usar chat como punto de entrada y GUI estructurada para operaciones complejas.

- **El diseño visual de Anthropic es intencionalmente cálido**: La paleta cream (#faf9f5) + coral (#cc785c) + slab serif es una decisión de diferenciación de marca deliberada. No es "genérico corporativo". FaberLoom debería invertir en una identidad visual propia con la misma intencionalidad.

- **Artifacts validan el patrón "panel lateral para output"**: Cuando el agente produce algo sustancial, Anthropic lo saca del chat stream y lo pone en su propio panel. Esto mantiene la conversación limpia y da al output el espacio que necesita. Es el patrón más aplicable para reportes, dashboards y documentos en FaberLoom.

---

## 12. GAPS IDENTIFICADOS

1. **Falta documentación oficial detallada sobre la UI de claude.ai web**: La mayoría de la información proviene de análisis de terceros, screenshots, y reverse engineering. Anthropic no publica una "UI kit" o design system público para la interfaz de producto (solo marketing site).

2. **Poca información sobre el sistema de diseño interno de Anthropic**: A pesar de tener un equipo de solo 3 designers, no hay publicaciones sobre su design system, component library, o proceso de diseño para la UI de producto.

3. **Streaming UI specifics**: No se encontró documentación sobre cómo Anthropic implementa técnicamente el streaming visual (skeleton loaders, token-by-token rendering, etc.). La información es a nivel de API, no de UI.

4. **Claude Cowork está en alpha muy temprano**: La información es limitada porque es alpha cerrada (solo macOS Desktop). No hay documentación pública detallada de su UI.

5. **No se encontró información sobre A/B testing o métricas de UX**: Anthropic no publica datos sobre cómo miden el éxito de sus decisiones de UI (engagement, task completion, satisfaction).

6. **Poca evidencia sobre patrones de error y recovery**: Cómo Anthropic maneja estados de error en la UI (tool call fallido, contexto excedido, rate limiting) no está bien documentado.

---

## FUENTES CONSULTADAS (30+ búsquedas)

1. [Claude Help Center - Projects](https://support.claude.com/en/articles/9517075-what-are-projects)
2. [Claude Help Center - File Uploads](https://support.claude.com/en/articles/8241126-upload-files-to-claude)
3. [Claude Help Center - Managing Projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)
4. [Anthropic - Safe Agents Framework](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents)
5. [Anthropic Engineering - Advanced Tool Use](https://www.anthropic.com/engineering/advanced-tool-use)
6. [Anthropic - Claude Design Announcement](https://www.anthropic.com/news/claude-design-anthropic-labs)
7. [Claude Code Docs - Permissions](https://code.claude.com/docs/en/permissions)
8. [Claude Code Docs - Permission Modes](https://code.claude.com/docs/en/permission-modes)
9. [Claude Code Docs - Desktop](https://code.claude.com/docs/en/desktop)
10. [Claude Code Docs - Interactive Mode](https://code.claude.com/docs/en/interactive-mode)
11. [Claude Blog - Tool Use GA](https://claude.com/blog/tool-use-ga)
12. [DesignMD - Claude Design System](https://www.designmd.co/d/claude)
13. [GitHub - claude-quickstarts/app_spec.txt](https://github.com/anthropics/claude-quickstarts/blob/main/autonomous-coding/prompts/app_spec.txt)
14. [GitHub - Anthropic Skills (Anti-Slop)](https://github.com/rohitg00/awesome-claude-design)
15. [AI UX Gallery - Context Chips](https://www.aiuxplayground.com/gallery/claude-context-chips)
16. [Medium - MCP Deep Dive](https://medium.com/@amanatulla1606/anthropics-model-context-protocol-mcp-a-deep-dive-for-developers-1d3db39c9fdc)
17. [Taskade - MCP Servers Guide](https://www.taskade.com/blog/mcp-servers)
18. [Academy UX Podcast - Joel Lewenstein](https://blog.academyux.com/learn-how-anthropic-designs-for-ai-joel-lewenstein-head-of-product-design-anthropic/)
19. [Fast Company - AI Changed Design Forever](https://www.fastcompany.com/91501353/ai-changed-design-forever-now-what)
20. [Dear Designer - Styrene Soul](https://deardesigner.substack.com/p/my-styrene-soul-a-short-affair-with)
21. [Wmedia - Show Thinking in Claude Code](https://wmedia.es/en/tips/claude-code-verbose-output-see-thinking)
22. [MindStudio - On-Demand Generative UI](https://www.mindstudio.ai/blog/what-is-claude-interactive-visualization-generative-ui/)
23. [Eigent - Live Artifacts Guide](https://www.eigent.ai/blog/claude-live-artifacts-guide)
24. [Albato - Claude Artifacts Guide](https://albato.com/blog/publications/how-to-use-claude-artifacts-guide)
25. [LogRocket - Implementing Artifacts](https://blog.logrocket.com/implementing-claudes-artifacts-feature-ui-visualization/)
26. [Claude History Crate](https://docs.rs/crate/claude-history/latest)
27. [GitHub - VS Code Tool Call Hierarchy Issue](https://github.com/anthropics/claude-code/issues/26592)
28. [GitHub - Configurable Tool Call Visibility](https://github.com/anthropics/claude-code/issues/37199)
29. [GitHub - Stream Thinking Issue](https://github.com/anthropics/claude-code/issues/30660)
30. [GitHub - VS Code Compact Display Mode](https://github.com/anthropics/claude-code/issues/55888)
31. [Kuse - Claude Cowork Guide](https://www.kuse.ai/kuse-cowork/claude-cowork)
32. [Adventure PPC - Hidden Architecture of Claude Code](https://www.adventureppc.com/blog/the-hidden-architecture-of-claude-code-how-anthropic-built-an-ai-that-actually-understands-instructions)
33. [Digital Applied - Computer Use API](https://www.digitalapplied.com/blog/anthropic-computer-use-api-guide)
34. [Addy Osmani - Agent Harness Engineering](https://addyosmani.com/blog/agent-harness-engineering/)
35. [P0stman - Claude Artifacts Limitations](https://p0stman.com/guides/claude-artifacts-limitations/)
36. [Nicholas Porter - Anti AI-Slop UI Design Skill](https://medium.com/@porter.nicholas/anthropic-skills-marketplace-the-anti-ai-slop-ui-design-skill-a572d0cfef4f)
37. [Fwdslash - What is a Claude Project](https://www.fwdslash.ai/blog/what-is-a-claude-project)
38. [Data Studios - File Upload Capabilities](https://www.datastudios.org/post/claude-ai-file-uploading-reading-capabilities-detailed-overview)
39. [MindStudio - Claude Design Explained](https://www.mindstudio.ai/blog/what-is-claude-design-anthropics-visual-prototyping/)
40. [Medium - Anthropic MCP Git Setup](https://medium.com/@richardhightower/anthropics-mcp-set-up-git-mcp-agentic-tooling-with-claude-desktop-beceb283a59c)
41. [Generect - Ultimate Guide to MCP](https://generect.com/blog/claude-mcp/)
42. [Snyk - Top Claude Skills for UI/UX Engineers](https://snyk.io/articles/top-claude-skills-ui-ux-engineers/)
43. [GitHub - Claude Code GUI VS Code Extension](https://marketplace.visualstudio.com/items?itemName=MaheshKok.claude-code-gui)
44. [Dev.to - Cogpit Claude Code Dashboard](https://dev.to/gentritbiba/claude-code-is-my-favorite-dev-tool-i-was-flying-blind-until-i-found-cogpit-1edn)
45. [Medium - Permission Classifier / Auto Mode](https://www.mindstudio.ai/blog/what-is-claude-code-auto-mode-permission-classifier/)
46. [Medium - Auto Mode Launch](https://medium.com/@joe.njenga/anthropic-adds-new-claude-code-auto-mode-no-more-permission-modes-52c8094ab742)
47. [Digital Applied - Auto Mode Guide](https://www.digitalapplied.com/blog/claude-code-auto-mode-autonomous-permission-decisions-guide)
48. [Human in the Loop - Tool Approvals](https://medium.com/@arvisionlab/human-in-the-loop-ai-agents-how-to-add-approvals-escalation-and-safe-autonomy-in-production-0a21e359781c)
49. [Open WebUI - Human In The Loop Discussion](https://github.com/open-webui/open-webui/discussions/16701)
50. [NicelyDone - Anthropic UI Components](https://nicelydone.club/apps/anthropic/components)
51. [YouTube - Claude Chat History Sidebar](https://www.youtube.com/watch?v=h35HxkuhWkE)
52. [Claude AI Homepage](https://claude.ai) (screenshot directo)
