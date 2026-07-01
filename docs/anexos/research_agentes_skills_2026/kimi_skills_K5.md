# K5 - Skills + Orquestacion Operativa

Resumen: La integracion entre skills de Claude Code y stacks operativos (n8n, MCP, sub-agentes, hooks) sigue una arquitectura de tres capas: Skills para conocimiento, Subagentes para comportamiento especializado, y MCP servers para conexiones externas. La documentacion oficial de Claude Code (v2.1+) define 12 eventos de hook, 4 tipos de handler, y un campo `skills:` en subagentes para precarga. El ecosistema n8n-MCP (czlonkowski/n8n-mcp, 21.4k stars) provee el puente documentado entre Claude Code y n8n via MCP. Los limites clave incluyen: 10K tokens max por SKILL.md (Read tool), context window 200K-1M tokens segun plan, timeout Bash 2-10 minutos, y deduplicacion ausente de skills multi-cargados.

---

## 1. HOOKS DE CLAUDE CODE

### 1.1 Eventos de Hook (12 eventos documentados)

Claim: Claude Code soporta 12 eventos de hook que interceptan momentos clave del ciclo de vida de una sesion, no 25 como se mencionaba en el brief inicial.
Source: Claude Code Hooks Complete Guide (claudefa.st)
URL: https://claudefa.st/blog/tools/hooks/hooks-guide
Date: 2026-05-28
Excerpt: "The 12 Hook Lifecycle Events: SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure, SubagentStart, SubagentStop, Stop, PreCompact, Setup, SessionEnd, Notification"
Context: Los 12 eventos cubren todo el ciclo de vida: inicio de sesion, antes/despues de uso de tool, spawn/fin de subagente, fin de respuesta, compactacion, y notificaciones. Stack MWT puede usar PreToolUse para bloquear operaciones peligrosas y PostToolUse para logging.
Confidence: high

Claim: Solo 5 de los 12 eventos pueden bloquear ejecucion: UserPromptSubmit, PreToolUse, PermissionRequest, Stop, SubagentStop.
Source: Claude Code Hooks (prg.sh)
URL: https://prg.sh/notes/Claude-Code-Hooks
Date: 2026-01-18
Excerpt: "PreToolUse: Before tool execution → Yes [can block]. PostToolUse: After tool completes → Yes [can block via exit code 2]. PermissionRequest: Permission dialog shown → Yes. UserPromptSubmit: User submits prompt → Yes. Stop: Main agent finishes → Yes. SubagentStop: Subagent finishes → Yes."
Context: Para stack MWT, PreToolUse es el mas critico: puede bloquear ejecucion de tools MCP o Bash que toquen datos sensibles de Amazon SP-API.
Confidence: high

### 1.2 Tipos de Hook Handler (4 tipos)

Claim: Claude Code soporta 4 tipos de hook handler: Command, HTTP, Prompt, y Agent. Los HTTP hooks se anadieron en febrero 2026.
Source: Claude Code Hooks Complete Guide (claudefa.st)
URL: https://claudefa.st/blog/tools/hooks/hooks-guide
Date: 2026-05-28
Excerpt: "Command hooks run shell scripts. HTTP hooks POST to an endpoint and receive JSON back: New - Feb 2026. Prompt hooks use LLM evaluation. Agent hooks spawn a subagent with tool access (Read, Grep, Glob) for deeper verification."
Context: Para MWT, los HTTP hooks permiten integrar validaciones externas (ej. verificar que un SKU existe en SP-API antes de modificarlo). Los Agent hooks permiten verificaciones complejas antes de acciones destructivas.
Confidence: high

Claim: Los hooks HTTP tienen comportamiento de error no-bloqueante por defecto: respuestas non-2xx, fallos de conexion y timeouts producen errores no-bloqueantes. Para bloquear realmente, se debe retornar 2xx con `decision: "block"`.
Source: Claude Code Hooks Complete Guide (claudefa.st)
URL: https://claudefa.st/blog/tools/hooks/hooks-guide
Date: 2026-05-28
Excerpt: "Non-blocking errors: Non-2xx responses, connection failures, and timeouts produce non-blocking errors (execution continues). To actually block a tool call, return a 2xx response with decision: 'block' in the JSON body."
Context: Gotcha critico para MWT: un hook HTTP que falle silenciosamente no bloqueara la operacion. Debe implementarse logica de confirmacion explicita.
Confidence: high

### 1.3 Configuracion de Hooks

Claim: Los hooks se configuran en `settings.json` con tres scopes: global (`~/.claude/settings.json`), proyecto (`.claude/settings.json`), y local (`.claude/settings.local.json`).
Source: Claude Code Hooks (claudefa.st)
URL: https://claudefa.st/blog/tools/hooks/hooks-guide
Date: 2026-05-28
Excerpt: "Hooks live in settings files: ~/.claude/settings.json (user, applies everywhere), .claude/settings.json (project, shared via git), .claude/settings.local.json (local, gitignored)"
Context: Stack MWT debe usar `.claude/settings.json` a nivel de proyecto para compartir hooks de validacion entre el equipo.
Confidence: high

Claim: Los matchers usan regex para filtrar que tools disparan el hook. El patron `mcp__.*` matchea todos los tools MCP.
Source: Claude Code Hooks (morphllm.com)
URL: https://morphllm.com/claude-code-hooks
Date: 2026-02-15
Excerpt: "Use mcp__server__tool naming pattern. Use regex matchers like mcp__github__.* to match all tools from a specific server, or mcp__.*__write.* to match write operations across all servers."
Context: Para MWT, se puede usar `mcp__sp-api__.*` para auditar todas las llamadas al MCP server de Amazon SP-API.
Confidence: high

---

## 2. SLASH COMMANDS

### 2.1 Lista Completa de Comandos Built-in

Claim: Claude Code tiene ~40+ comandos slash commands built-in. Los skills se exponen automaticamente como slash commands (ej. `/review`, `/deploy`).
Source: Claude Code Slash Commands (prg.sh)
URL: https://prg.sh/notes/Claude-Code-Slash-Commands
Date: 2026-01-18
Excerpt: "Built-in Commands: /add-dir, /agents, /bashes, /bug, /clear, /compact, /config, /context, /cost, /doctor, /exit, /export, /help, /hooks, /ide, /init, /install-github-app, /login, /logout, /mcp, /memory, /model, /output-style, /permissions, /plan, /plugin, /pr-comments, /privacy-settings, /release-notes, /rename, /remote-env, /resume, /review, /rewind, /sandbox, /security-review, /stats, /status, /statusline, /teleport, /terminal-setup, /theme, /todos, /usage, /vim"
Context: Los skills creados en `.claude/skills/<name>/SKILL.md` se exponen automaticamente como `/<name>`. Para MWT, skills como `/sp-api-query` o `/helium10-report` serian invocables directamente.
Confidence: high

Claim: Los skills aparecen en el slash command menu por defecto desde Claude Code 2.1 (enero 2026). Se puede ocultar con `user-invocable: false`.
Source: Claude Code 2.1 Pain Points Addressed (paddo.dev)
URL: https://paddo.dev/blog/claude-code-21-pain-points-addressed/
Date: 2026-01-08
Excerpt: "Skills now appear in the slash command menu by default. If you have a skill in .claude/skills/, it's visible as a slash command. Explicit invocation exists now. Opt-out with user-invocable: false in frontmatter."
Context: Mejora significativa para MWT: los skills son descubribles sin memorizar nombres.
Confidence: high

---

## 3. SKILLS + SUB-AGENTES (campo skills:)

### 3.1 Precarga de Skills en Subagentes

Claim: El campo `skills:` en el frontmatter de un subagente precarga el contenido completo de las skills en el contexto del subagente al startup. El subagente no necesita descubrirlas; ya estan cargadas.
Source: Claude Code Official Docs - Subagents
URL: https://code.claude.com/docs/en/sub-agents
Date: 2025-09-01 (ongoing)
Excerpt: "skills: Skills to preload into the subagent's context at startup. The full skill content is injected, not just the description. Subagents can still invoke unlisted project, user, and plugin skills through the Skill tool"
Context: Este es el patron compuesto 2026 para MWT: subagente Haiku + skills precargadas (SP-API conventions, Helium 10 query patterns) + MCP server scoped.
Confidence: high

Claim: Los subagentes con `skills:` reciben: su propio system prompt, el contenido completo de las skills listadas, CLAUDE.md y git status (excepto Explore y Plan que omiten ambos para mantener contexto liviano).
Source: Claude Code Official Docs - Skills
URL: https://code.claude.com/docs/en/skills
Date: 2025-09-01
Excerpt: "Skill with context: fork: From agent type, SKILL.md content, CLAUDE.md [except when agent is Explore or Plan]. Subagent with skills field: Subagent's markdown body, Claude's delegation message, Preloaded skills + CLAUDE.md"
Context: Para tareas de exploracion de datos SP-API, usar `agent: Explore` mantiene el contexto minimo y barato.
Confidence: high

### 3.2 Context Fork en Skills

Claim: Una skill con `context: fork` en su frontmatter ejecuta en un subagente aislado con su propia ventana de contexto. La skill content se convierte en el prompt que dirige al subagente.
Source: Claude Code Official Docs - Skills
URL: https://code.claude.com/docs/en/skills
Date: 2025-09-01
Excerpt: "Add context: fork to your frontmatter when you want a skill to run in isolation. The skill content becomes the prompt that drives the subagent. It won't have access to your conversation history."
Context: `context: fork` difumina la frontera skill/sub-agente: una skill puede ejecutar como subagente aislado. Para MWT, skills de analisis complejo (ej. `/deep-analysis`) deberian usar fork para no contaminar el contexto principal.
Confidence: high

Claim: `context: fork` solo tiene sentido para skills con instrucciones explicitas de tarea. Si la skill es solo guias (como "usa estas convenciones de API"), forkearla produce un subagente que recibe guias sin nada que hacer.
Source: Claude Code Official Docs - Skills
URL: https://code.claude.com/docs/en/skills
Date: 2025-09-01
Excerpt: "context: fork only makes sense for skills with explicit instructions. If your skill contains guidelines like 'use these API conventions' without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output."
Context: Anti-patron documentado para MWT: no forkear skills que solo contienen convenciones.
Confidence: high

### 3.3 Frontmatter Completo de Subagentes

Claim: El frontmatter de subagentes soporta los siguientes campos documentados: name, description, tools, disallowedTools, model, permissionMode, maxTurns, skills, mcpServers, hooks, memory, background, effort, isolation, color, initialPrompt.
Source: Claude Code Official Docs - Subagents
URL: https://code.claude.com/docs/en/sub-agents
Date: 2025-09-01
Excerpt: "Supported frontmatter fields: name (required), description (required), tools, disallowedTools, model, permissionMode, maxTurns, skills, mcpServers, hooks, memory, background, effort, isolation, color, initialPrompt"
Context: Para MWT, los campos mas utiles son: `skills` (precargar conocimiento SP-API), `mcpServers` (scopear acceso a SP-API), `model: haiku` (tareas rutinarias baratas), `maxTurns` (prevenir loops infinitos), `disallowedTools: Write,Edit` (read-only para auditorias).
Confidence: high

---

## 4. SKILLS + n8n

### 4.1 n8n MCP Server Trigger Node

Claim: n8n tiene un nodo "MCP Server Trigger" que expone workflows n8n como tools MCP via SSE (Server-Sent Events). AI agents pueden descubrir e invocar estos tools.
Source: n8n MCP Step-by-Step Guide (generect.com)
URL: https://generect.com/blog/n8n-mcp/
Date: 2026-01-12
Excerpt: "MCP server trigger node (letting AI agents use your tools): Think of the MCP server trigger like opening the door for AI agents. You're exposing parts of your n8n workflows so AI systems can find and use them."
Context: Para MWT, un workflow n8n que consulta SP-API podria exponerse como tool MCP, que Claude Code descubre y usa a traves del MCP server de n8n.
Confidence: high

Claim: El nodo MCP Server Trigger genera endpoints URL (test y production), soporta autenticacion Bearer tokens, y se activa togglando el workflow a "Active".
Source: n8n MCP Documentation
URL: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/
Date: ongoing
Excerpt: "The MCP Client Tool node is a Model Context Protocol (MCP) client, allowing you to use the tools exposed by an external MCP server. n8n also has an MCP Server Trigger node that allows you to expose n8n tools to external AI Agents."
Context: El flujo bidireccional Claude-n8n via MCP es: Claude (MCP client) → n8n MCP Server Trigger → n8n workflow → respuesta SSE.
Confidence: high

### 4.2 n8n MCP Client Tool Node

Claim: El nodo "MCP Client Tool" en n8n permite que workflows n8n invoquen tools de servidores MCP externos. Soporta SSE endpoint, Bearer/Header/OAuth2 auth.
Source: n8n MCP Client Tool Documentation
URL: https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolmcp/
Date: ongoing
Excerpt: "SSE Endpoint: The SSE endpoint for the MCP server you want to connect to. Authentication: Bearer, generic header, and OAuth2 authentication methods. Tools to Include: All, Selected, or All Except."
Context: Para MWT, un workflow n8n podria usar el MCP Client Tool node para invocar un MCP server custom que consulta SP-API, procesar los resultados, y guardarlos en Google Drive.
Confidence: high

### 4.3 n8n-mcp: MCP Server para Claude Code

Claim: El proyecto `czlonkowski/n8n-mcp` (21.4k stars, MIT license) es un MCP server que da a Claude Code acceso a 1,851 nodos n8n, documentacion, templates, y la capacidad de crear/modificar workflows directamente.
Source: GitHub - czlonkowski/n8n-mcp
URL: https://github.com/czlonkowski/n8n-mcp
Date: 2026-05-23 (ultimo release v2.56.0)
Excerpt: "A Model Context Protocol (MCP) server that provides AI assistants with comprehensive access to n8n node documentation, properties, and operations. 1,851 n8n nodes - 822 core nodes + 1,029 community nodes."
Context: Para MWT, este MCP server permite a Claude Code construir workflows n8n que integran SP-API, Helium 10, y Google Drive, todo desde la terminal.
Confidence: high

Claim: n8n-mcp se puede instalar en Claude Code con: `npx n8n-mcp` o `claude mcp add-from-claude-desktop`. Sirve skills markdown via MCP Resources.
Source: GitHub - czlonkowski/n8n-mcp
URL: https://github.com/czlonkowski/n8n-mcp
Date: 2026-05-23
Excerpt: "feat(mcp): serve n8n-skills markdown via MCP Resources (#793). Quick Start: npx n8n-mcp. Claude Code: claude mcp add-from-claude-desktop"
Context: n8n-mcp no solo expone nodos sino que sirve skills como recursos MCP, permitiendo composicion skill + MCP.
Confidence: high

### 4.4 n8n Skills para Claude Code

Claim: El proyecto `czlonkowski/n8n-skills` provee 7 skills complementarios que ensenan a Claude Code como construir workflows n8n. Se instalan como plugin o manualmente en `~/.claude/skills/`.
Source: GitHub - czlonkowski/n8n-skills
URL: https://github.com/czlonkowski/n8n-skills
Date: 2025-10-20
Excerpt: "7 complementary skills that work together. Skills activate automatically when relevant queries are detected. When you ask: 'Build and validate a webhook to Slack workflow' - n8n Workflow Patterns identifies pattern, MCP Tools Expert searches nodes, Node Configuration guides setup, Validation Expert validates."
Context: Patron composicion real documentado: multiples skills se activan en secuencia para una tarea compleja. Para MWT, se podria replicar con skills SP-API + Helium 10.
Confidence: high

---

## 5. SKILLS + MCP SERVERS PROPIOS

### 5.1 Arquitectura MCP Client-Server

Claim: MCP usa arquitectura cliente-servidor con comunicacion via JSON-RPC. Define dos transportes: STDIO (local) y Streamable HTTP/SSE (remoto). Los servidores exponen tools, resources, y prompts.
Source: Model Context Protocol Specification
URL: https://modelcontextprotocol.io/specification/2025-06-18
Date: 2026-05-29
Excerpt: "MCP defines two main transport mechanisms: STDIO and Streamable HTTP. The STDIO transport uses standard input/output for local processes. Streamable HTTP uses HTTP POST/GET with Server Sent Events for remote connections."
Context: Para un MCP server propio de SP-API, MWT deberia usar STDIO para desarrollo local y HTTP/SSE para produccion (si Claude Code y el server corren en maquinas separadas).
Confidence: high

Claim: El ciclo de vida MCP tiene tres fases: Initialization (handshake de capabilities), Operation (tool calls, resources), Shutdown (graceful termination). Las sesiones son stateful.
Source: Model Context Protocol Explained (codilime.com)
URL: https://codilime.com/blog/model-context-protocol-explained/
Date: 2026-02-02
Excerpt: "MCP defines a rigorous three-phase lifecycle: Initialization (handshake), Operation (tool calls, resources), Shutdown. All communication travels via JSON-RPC, transformed into a stateful session protocol."
Context: Para MWT, el MCP server de SP-API debe implementar el handshake de capabilities listando las operaciones disponibles (getOrders, getInventory, etc.).
Confidence: high

### 5.2 Como una Skill Descubre y Usa un MCP Server

Claim: Las skills no tienen acceso directo a datos externos. Las skills definen *como* hacer el trabajo; los MCP servers dan *acceso* a datos. Para acceder a datos externos, una skill debe invocar tools del MCP server.
Source: Skills vs Subagents vs MCP (systemprompt.io)
URL: https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
Date: 2026-03-11
Excerpt: "Skills vs MCP servers: skills are static text injected into the prompt. MCP servers are running programs that bridge Claude to external data and side effects. If your use case contains the words 'query', 'fetch', or 'current state', you need an MCP server, not a skill."
Context: Para MWT, una skill SP-API definira *como* consultar inventario (pasos, validaciones), pero la consulta real la hara el MCP server de SP-API via el tool `mcp__sp-api__getInventory`.
Confidence: high

Claim: Las skills pueden invocar tools MCP usando el Skill tool. Los hooks pueden matcher patrones MCP con `mcp__<server>__<tool>`. Los subagentes pueden tener MCP servers scoped via `mcpServers:`.
Source: Multiple sources (systemprompt.io, morphllm.com, code.claude.com)
URL: https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
Date: 2026-03-11
Excerpt: "Subagents can use MCP servers. MCP servers cannot use subagents. Subagents vs MCP servers: not a real comparison. A subagent is who is doing the work. An MCP server is what tools they have."
Context: Stack de composicion MWT: Subagente (quien) + Skills (conocimiento) + MCP server SP-API (tools). El `mcpServers:` frontmatter scoppea que tools ve cada subagente.
Confidence: high

---

## 6. LIMITES Y GOTSCHAS

### 6.1 Tamanio Maximo de SKILL.md

Claim: Claude Code tiene un limite de 10,000 tokens para la herramienta Read. SKILL.md files que exceden este limite fallan completamente al cargar, haciendo las skills inutilizables.
Source: GitHub Issue - anthropics/claude-plugins-official #995
URL: https://github.com/anthropics/claude-plugins-official/issues/995
Date: 2026-03-25
Excerpt: "File content (n) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file. This makes the skills completely unusable."
Context: Para MWT, las skills SP-API deben mantenerse bajo 10K tokens. Contenido extenso (ej. ejemplos de respuestas SP-API) debe extraerse a archivos `references/` separados.
Confidence: high

Claim: El workaround recomendado es extraer contenido detallado (templates, ejemplos, tablas) a archivos `references/` dentro del directorio de la skill, manteniendo SKILL.md bajo ~10KB con punteros Read.
Source: GitHub Issue - anthropics/claude-plugins-official #995
URL: https://github.com/anthropics/claude-plugins-official/issues/995
Date: 2026-03-25
Excerpt: "Extract detailed content into references/ files within each skill directory, keeping SKILL.md under ~10KB with Read pointers to the extracted files."
Context: Patron de referencias para skills grandes: SKILL.md (~10KB) + references/templates.md + references/examples.md + references/schemas.md.
Confidence: high

### 6.2 Progressive Disclosure y Tokens por Skill

Claim: Claude Code usa carga progresiva (progressive disclosure): al inicio de sesion solo carga nombre y descripcion de cada skill (~30-50 tokens por skill). El contenido completo solo se carga cuando Claude decide que es relevante.
Source: Tyler Folkman - Claude Skills Guide
URL: https://tylerfolkman.substack.com/p/the-complete-guide-to-claude-skills
Date: 2025-10-26
Excerpt: "At session start, Claude scans all available Skills and loads just the name and description into its system prompt. Each Skill consumes roughly 30-50 tokens until Claude decides it's relevant."
Context: Con 100 skills disponibles, el overhead es solo ~3,500-5,000 tokens. Para MWT, se pueden tener decenas de skills sin impactar el contexto hasta que se necesiten.
Confidence: high

Claim: Las skills se cargan en tres fases: Discovery (metadata ~100-200 tokens), Invocation (full skill content), y References (archivos auxiliares solo si se necesitan).
Source: Claude Agent Skills Deep Dive (leehanchung.github.io)
URL: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
Date: 2025-10-26
Excerpt: "Skills load in stages: Phase 1 Discovery & Loading (skill descriptions), Phase 2 Invocation (full SKILL.md), Phase 3 References (supporting files on demand)."
Context: Fase 1 es ~100-200 tokens por skill (name + description). Fase 2 carga el SKILL.md completo. Fase 3 carga archivos referenciados solo si se usan.
Confidence: high

### 6.3 Deduplicacion de Skills

Claim: El Skill tool no deduplica: cada invocacion del mismo skill anade el contenido completo al contexto. Invocar la misma skill 10+ veces agota rapidamente la ventana de contexto.
Source: GitHub Issue - anthropics/claude-code #21891
URL: https://github.com/anthropics/claude-code/issues/21891
Date: 2026-01-30
Excerpt: "The Skill tool appends full skill content to the Messages context every time it's invoked, even for the same skill. There's no deduplication, causing rapid context exhaustion."
Context: Gotcha critico para MWT: si un hook o subagente invoca la misma skill repetidamente, el contexto se saturara. Compaction ayuda pero no es ideal.
Confidence: high

### 6.4 Conflictos entre Multiple Skills

Claim: No hay sistema de resolucion de conflictos entre skills. Si dos skills dan instrucciones contradictorias, Claude las aplica en el orden que aparecen en el contexto.
Source: Stop Adding New Claude Skills (buildtolaunch.substack.com)
URL: https://buildtolaunch.substack.com/p/claude-skills-not-working-fix
Date: 2026-04-06
Excerpt: "Duplicate looks like: two files both describing how to write an article, different instructions, neither one deferring to the other. This is the same single-source-of-truth problem that breaks any shared documentation system."
Context: Para MWT, evitar skills SP-API y Helium 10 con instrucciones contradictorias sobre como formatear reportes. Mantener una skill maestra de "report-format" que las demas referencien.
Confidence: medium

Claim: Existen tres patrones de organizacion de skills: 1) Skill orquestador con sub-steps internos, 2) Skills independientes invocables, 3) Patron hibrido. Cada uno tiene trade-offs.
Source: Stop Adding New Claude Skills (buildtolaunch.substack.com)
URL: https://buildtolaunch.substack.com/p/claude-skills-not-working-fix
Date: 2026-04-06
Excerpt: "Three patterns exist: 1) Top-level skill owns sub-steps as internal references, 2) Independently invocable skills, 3) Hybrid. What goes wrong with orchestrator: you need to fix one sub-step without running the whole workflow. You can't. So you duplicate the sub-step as a standalone skill."
Context: Recomendacion para MWT: usar patron hibrido - skills independientes para tareas comunes (query SP-API, query Helium 10, formatear reporte) + skill orquestador para flujos completos.
Confidence: medium

### 6.5 Timeouts

Claim: Claude Code tiene un timeout por defecto de 2 minutos (120 segundos) para comandos Bash. Se puede extender hasta 10 minutos (600 segundos) con `timeout 600000ms` o via env var `BASH_DEFAULT_TIMEOUT_MS`.
Source: Solving Long-Running Command Timeouts (zenn.dev)
URL: https://zenn.dev/khasegawa/articles/75b49e2cbb14c8
Date: 2025-06-23
Excerpt: "Claude Code has a default timeout of 2 minutes. It can be extended up to 10 minutes. Configuration methods: Individual specification (timeout 600000ms), Environment variables (BASH_DEFAULT_TIMEOUT_MS=300000), settings.json"
Context: Para MWT, queries largas a SP-API (ej. reportes de 90 dias) necesitan timeout extendido. El maximo es 10 minutos para procesos interactivos.
Confidence: high

Claim: Para tareas que exceden 10 minutos, existe una skill "Long Waits" que implementa polling secuencial con background sleeps para superar el timeout.
Source: MCP Market - Long Waits Skill
URL: https://mcpmarket.com/tools/skills/long-waits-task-scheduling
Date: ongoing
Excerpt: "The Long Waits skill allows Claude Code to overcome the standard 10-minute bash timeout by implementing an event-driven loop of sequential background sleep intervals."
Context: Para reportes SP-API que toman >10 minutos, usar patron de polling con background sleeps en lugar de un comando bloqueante.
Confidence: medium

### 6.6 Context Window

Claim: Claude Code soporta context windows de 200K (Sonnet 4.5, modelos antiguos) y 1M tokens (Opus 4.6, Sonnet 4.6 en planes pagos). La ventana usable real es ~830K tokens despues de reservas de compaction.
Source: Claude Code 1M Context Power (verdent.ai)
URL: https://verdent.ai/guides/claude-code-1m-context-window
Date: 2026-04-01
Excerpt: "The 1M window: you have roughly 830K usable tokens after Claude Code's auto-compaction buffer (~33K reserved) and the ~83.5% usage threshold before compaction triggers."
Context: Con 1M de contexto, MWT puede cargar multiples skills + datos de SP-API + documentacion sin preocuparse por el limite en sesiones largas.
Confidence: high

### 6.7 Rate Limits

Claim: Los rate limits de Claude Code (post-mayo 2026, despues del deal Colossus 1): 5-hour window duplicado, peak-hour reductions eliminadas para Pro/Max. API Tier 1: 500K input TPM (antes 30K).
Source: Claude Code Rate Limits Doubled (mindstudio.ai)
URL: https://mindstudio.ai/blog/claude-code-rate-limits-doubled-colossus-1-api-limits/
Date: 2026-05-09
Excerpt: "Claude Code's 5-hour rate limit just doubled. API Tier 1 input tokens per minute jumped from 30,000 to 500,000. Peak-hour limit reduction eliminated for Pro and Max accounts."
Context: Para MWT, los nuevos limites permiten sesiones agenticas largas (2+ horas) sin interrupciones, incluso en Tier 1.
Confidence: high

---

## 7. PATRONES DE COMPOSICION

### Patron 1: SP-API Query → Transform → Documento (Stack MWT)

**Flujo documentado:**

```
1. Usuario: "Generar reporte de inventario de los ultimos 30 dias"
2. Claude Code decide delegar a subagente "sp-analyst" (description match)
3. Subagente sp-analyst arranca con:
   - skills: ["sp-api-conventions", "report-format"]
   - mcpServers: ["sp-api"]
   - model: sonnet
   - maxTurns: 30
4. Subagente usa mcp__sp-api__getInventoryReport con parametros (days: 30)
5. MCP server SP-API (propio) ejecuta llamada a Amazon SP-API
6. Resultados se transforman segun skill "report-format"
7. Subagente retorna markdown formateado al agente principal
8. Agente principal usa Write para guardar en Google Drive (via MCP)
```

**Fuentes:** Documentacion oficial Claude Code (skills, subagents, MCP), systemprompt.io (composicion de los tres mecanismos)

### Patron 2: n8n Workflow Auto-Build con Claude Code + n8n-mcp

**Flujo documentado:**

```
1. Usuario: "Crear workflow n8n que reciba webhook de Amazon notifications,
    consulte SP-API, y guarde en Google Drive"
2. Claude Code activa skill "n8n-workflow-patterns" (auto-detected)
3. Claude usa MCP server n8n-mcp para:
   - Listar nodos disponibles (Webhook, HTTP Request, Google Drive)
   - Ver propiedades y documentacion de cada nodo
   - Validar la configuracion propuesta
4. Claude genera JSON del workflow via tool mcp__n8n-mcp__createWorkflow
5. Workflow se crea directamente en la instancia n8n via API
6. n8n-mcp valida el workflow antes de deploy
```

**Fuentes:** czlonkowski/n8n-mcp GitHub, n8n-skills repo, medium.com/@shivamshinde92722

### Patron 3: Multi-Subagent Paralelo para Analisis Competitivo

**Flujo documentado:**

```
1. Usuario: "Analisis competitivo de producto X: precios Amazon, keywords Helium 10,
    y posicionamiento SEO"
2. Agente principal delega 3 subagentes en paralelo:
   a) Subagente "amazon-researcher":
      - skills: ["sp-api-queries", "product-analysis"]
      - mcpServers: ["sp-api"]
      - model: haiku
      - → Devuelve precios, reviews, ranking de producto X
   b) Subagente "helium10-researcher":
      - skills: ["helium10-conventions"]
      - mcpServers: ["helium10-mcp"]
      - model: haiku
      - → Devuelve keywords, search volume, Cerebro data
   c) Subagente "seo-analyst":
      - skills: ["seo-reporting"]
      - model: sonnet
      - → Devuelve analisis SEO competitivo
3. Agente principal sintetiza resultados en reporte consolidado
4. Guarda en Google Drive via MCP
```

**Fuentes:** Claude Code Official Docs (subagents en paralelo), systemprompt.io (patron compuesto 2026)

---

## 8. INVENTARIO: DOCUMENTADO vs INGENIERIA IN-HOUSE

### Documentado (fuente oficial o comunidad verificada)

| Integracion | Documentacion | Fuente |
|---|---|---|
| Hooks (12 eventos, 4 tipos) | Oficial completa | code.claude.com, claudefa.st |
| Slash commands (~40+) | Oficial completa | prg.sh, code.claude.com |
| Skills frontmatter (todos campos) | Oficial completa | code.claude.com/docs/en/skills |
| Subagentes frontmatter (skills:, mcpServers:, etc.) | Oficial completa | code.claude.com/docs/en/sub-agents |
| context: fork (skill como subagente) | Oficial completa | code.claude.com/docs/en/skills |
| n8n MCP Server Trigger node | Oficial n8n | docs.n8n.io |
| n8n MCP Client Tool node | Oficial n8n | docs.n8n.io |
| n8n-mcp (MCP server para n8n) | Comunidad, 21.4k stars | github.com/czlonkowski/n8n-mcp |
| n8n-skills (skills para n8n) | Comunidad | github.com/czlonkowski/n8n-skills |
| MCP protocol spec (STDIO, HTTP/SSE) | Oficial | modelcontextprotocol.io |
| SKILL.md limite 10K tokens | Comunidad verificada | GitHub issues |
| Progressive disclosure de skills | Comunidad verificada | Multiple blogs |
| Timeout 2-10 min Bash | Comunidad verificada | zenn.dev, GitHub issues |
| Rate limits (post-Colossus 1) | Oficial | Anthropic docs, mindstudio.ai |
| Context window 200K-1M | Oficial | support.claude.com |
| AGENTS.md vs CLAUDE.md | Documentado | nextjs.org, aihero.dev |

### Requiere Ingenieria In-House

| Integracion | Por que | Recomendacion |
|---|---|---|
| MCP server custom para SP-API | No existe MCP server publico para SP-API. Debe implementarse con stdio o HTTP transport, exponer tools (getOrders, getInventory, etc.), y manejar auth OAuth de Amazon. | Implementar con `@modelcontextprotocol/sdk`. Usar stdio para dev, HTTP/SSE para produccion. |
| MCP server custom para Helium 10 | Helium 10 no tiene API oficial publica. Requiere scraping o integracion via herramientas existentes. | Evaluar si Helium 10 tiene API privada o usar integracion indirecta via n8n workflows. |
| Composicion skill + n8n + SP-API en un solo flujo | No hay documentacion que una los tres. Requiere orchestracion manual. | Usar patron: skill → subagente con mcpServers: [n8n-mcp, sp-api-mcp] → orquestacion en Claude Code. |
| Deduplicacion de skills | El Skill tool no deduplica. Issue #21891 abierto sin resolver. | Hooks PreToolUse para rastrear skills cargadas y evitar recarga. |
| Skill conflict resolution | No hay sistema nativo de resolucion de conflictos entre skills. | Convencion de equipo: una skill maestra por dominio, skills hijas que referencian. |
| Rate limiting/quotas de SP-API | Los rate limits de SP-API son independientes de Claude Code. | Implementar backoff en el MCP server, no en la skill. |
| Google Drive como MCP server | Existe pero requiere configuracion OAuth | Usar MCP server oficial de Google o n8n workflow con MCP Server Trigger |

---

## 9. REFERENCIAS CRUZADAS PARA STACK MWT

### Taxonomia SKILL_ aplicada

| Tipo SKILL_ | Mapeo a mecanismo Claude Code | Ejemplo MWT |
|---|---|---|
| SKILL_AGENTE | Subagente con `skills:` precargadas | `sp-analyst` (subagente con skills SP-API + report-format) |
| SKILL_MODULO | Skill standalone invocable via `/` | `/sp-api-query`, `/helium10-search` |
| SKILL_KB | Contenido de referencia en `references/` | `references/sp-api-error-codes.md`, `references/helium10-metrics.md` |
| SKILL_CONVENTION | Skill con `disable-model-invocation: true` | `/deploy-staging` (solo manual) |

### Ubicaciones de archivos en proyecto MWT

```
.claude/
  settings.json              # Hooks de validacion SP-API
  skills/
    sp-api-query/
      SKILL.md               # ~10KB max
      references/
        endpoints.md         # Documentacion de endpoints SP-API
        error-codes.md       # Catalogo de errores
        examples.md          # Ejemplos de requests/responses
    helium10-search/
      SKILL.md
      references/
        metrics-guide.md
    report-format/
      SKILL.md               # Convenciones de formato de reportes
    n8n-workflow-patterns/
      SKILL.md               # Patrones para construir workflows n8n
  agents/
    sp-analyst.md            # Subagente con skills: [sp-api-query, report-format]
    competitor-researcher.md # Subagente con mcpServers: [sp-api, helium10]
```

---

*Documento generado a partir de fuentes verificadas. Integraciones marcadas como [PENDIENTE - NO INVENTAR] requieren confirmacion en documentacion oficial.*
