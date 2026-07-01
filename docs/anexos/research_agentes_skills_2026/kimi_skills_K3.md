# K3 - Runtimes y Superficies

Resumen: Las seis plataformas analizadas difieren radicalmente en su modelo de ejecucion. Claude Code (CLI) ofrece acceso total al OS con sandbox opcional (bubblewrap/seatbelt), mientras que Claude Cowork ejecuta en una VM sandboxed (Ubuntu 22.04, sin root) con lista blanca de dominios administrada por Anthropic. La API de Claude/Code Execution Container permite skills programaticas con retencion de datos configurable. Codex CLI (OpenAI) usa sandbox por defecto sin acceso a red, con modos de aprobacion configurables. Cursor IDE opera como editor con agent mode que puede ejecutar comandos de terminal y usar MCP servers. Goose CLI (open-source) ejecuta localmente con las herramientas del sistema operativo anfitrion y sin restricciones inherentes. Para MWT, esto significa que: SP-API/n8n solo pueden ser llamados desde plataformas con acceso a red (Claude Code sin sandbox, Claude API, Codex CLI con red habilitada, Cursor, Goose) pero NO desde Cowork (lista blanca restringida).

---

## Tabla Comparativa - Acceso a Red

| Plataforma | Acceso a Red | HTTP Outbound | Restricciones | Proxy |
|------------|-------------|---------------|---------------|-------|
| **Claude Code (CLI)** | Completo (misma red que host) | curl, fetch, etc. | Ninguno inherente; sandbox opcional con allowlist | Proxy local configurable via settings.json |
| **Claude API (programatico)** | Desde el codigo del usuario | Via HTTP client del usuario | Depende del entorno de ejecucion del usuario | N/A |
| **claude.ai / Cowork** | Proxy con lista blanca | Solo dominios aprobados por Anthropic | allowManagedDomainsOnly=true ignora configuracion del usuario; 403 para dominios no aprobados | socat en localhost:3128 (HTTP) y :1080 (SOCKS5) |
| **Codex CLI (OpenAI)** | Desactivado por defecto | Configurable via --sandbox | Modo "workspace-write" por defecto sin red; red requiere aprobacion | Proxy de red configurable |
| **Cursor (IDE)** | Via herramientas del IDE y MCP | Depende de la herramienta; terminal puede hacer requests | MCP limitado a 40 herramientas; Privacy Mode configurable | Configurable via settings.json |
| **Goose (CLI)** | Completo (misma red que host) | Via shell commands o tools | Sin restricciones inherentes; depende del entorno host | N/A |

## Tabla Comparativa - Sandbox

| Plataforma | Sandbox | Tipo | Filesystem | Network |
|------------|---------|------|------------|---------|
| **Claude Code (CLI)** | Opcional (/sandbox) | bubblewrap (Linux), seatbelt (macOS) | Solo directorio de proyecto por defecto | Proxy con allowlist de dominios |
| **Claude API (programatico)** | Container de ejecucion de codigo | Aislado, efimero | Limitado al container | No outbound por defecto |
| **claude.ai / Cowork** | Siempre activo | VM Ubuntu 22.04 ARM64 + bubblewrap | ~9.6 GB root; solo mnt/outputs persiste | Lista blanca gestionada por Anthropic |
| **Codex CLI (OpenAI)** | Siempre activo | seatbelt (macOS), bubblewrap+seccomp (Linux), sandbox users (Windows) | Escritura limitada al workspace | Bloqueado por defecto; configurable |
| **Cursor (IDE)** | No tiene sandbox propio | Depende del SO host | Acceso completo via IDE | Sin restriccion inherente |
| **Goose (CLI)** | No tiene sandbox | Autonomous mode por defecto (permisos de usuario) | Acceso a archivos del usuario | Completo via shell |

## Tabla Comparativa - Instalacion de Paquetes en Runtime

| Plataforma | npm | pip | apt/brew | Otros |
|------------|-----|-----|----------|-------|
| **Claude Code (CLI)** | Si (via Bash) | Si (via Bash) | Si (con sudo si disponible) | cargo, go, etc. |
| **Claude API (programatico)** | Solo en Code Execution Container | Solo en Code Execution Container | No | No |
| **claude.ai / Cowork** | pip + npm pre-instalados | pip + npm pre-instalados | No (sin sudo/root) | No |
| **Codex CLI (OpenAI)** | Si (via Bash, sandboxed) | Si (via Bash, sandboxed) | Depende del sandbox | Depende del sandbox |
| **Cursor (IDE)** | Si (via terminal integrada) | Si (via terminal integrada) | Si (via terminal) | Todos disponibles |
| **Goose (CLI)** | Si (via shell tool) | Si (via shell tool) | Si (via shell) | Todos disponibles |

## Tabla Comparativa - Permisos de Tools

| Plataforma | Herramientas Disponibles | Tool Principal | Custom Tools |
|------------|-------------------------|----------------|--------------|
| **Claude Code (CLI)** | Read, Write, Edit, Bash, Grep, Glob, WebFetch, MCP, Skill, Task/subagent | Bash (shell completo) | Via MCP servers, skills, hooks |
| **Claude API (programatico)** | Depende de la implementacion; Code Execution Container: bash, file ops | N/A (el usuario define tools) | Via function calling |
| **claude.ai / Cowork** | 132 skills pre-built, 27 tools de computer use, browser, connectors | Computer use + skills | Via plugins (agrupaciones de skills+MCP+hooks) |
| **Codex CLI (OpenAI)** | Read, Write, Edit, Bash, MCP, apply_patch, js_repl, web_search, view_image, request_permissions | Bash (sandboxed) | Via MCP, skills, plugins |
| **Cursor (IDE)** | Chat, Composer, Agent mode, Inline Edit, terminal bash, MCP (40 tools max) | Terminal + Composer/Agent | Via MCP servers |
| **Goose (CLI)** | shell, text_editor, analyze, screen_capture, image_processor (Developer ext); MCP extensions | shell (completo) | Via MCP servers, extensions |

## Tabla Comparativa - Distribucion Org-wide / Admin Centralizado

| Plataforma | Admin Centralizado | Skills Org-wide | Grupos/Equipos | Audit Log |
|------------|-------------------|-----------------|----------------|-----------|
| **Claude Code (CLI)** | Enterprise: policy hooks, managed-mcp.json, allowedMcpServers/deniedMcpServers | Via plugins git repo; habilitar/deshabilitar per org | Via plugins asignados a grupos | Audit log + Compliance API |
| **Claude API (programatico)** | Via API keys de org | Via /v1/skills endpoint | [PENDIENTE] | Via API console |
| **claude.ai / Cowork** | Organization settings > Skills; toggle Code execution + Skills | Upload ZIP de skills; disponible para todos | Plugins asignados a grupos (marketing, etc.) | Audit log de skill sharing events |
| **Codex CLI (OpenAI)** | ChatGPT Enterprise admin setup; Managed configuration, RBAC | Via /etc/codex/skills/ (admin level); config.toml managed | Workspace settings + role-based access | Compliance API (ChatGPT Enterprise) |
| **Cursor (IDE)** | Business/Enterprise: Admin Dashboard > Privacy; enforce Privacy Mode | [PENDIENTE - NO INVENTAR] | Business/Enterprise tier | [PENDIENTE] |
| **Goose (CLI)** | No hay admin centralizado (open source) | Manual por usuario | No | No |

## Tabla Comparativa - Paths de Discovery (Skills)

| Plataforma | Path Local | Path Proyecto | Path Global/Org | Comandos de Invocacion |
|------------|-----------|---------------|-----------------|----------------------|
| **Claude Code (CLI)** | ~/.claude/skills/ | .claude/skills/ (en repo) | Via plugins marketplace | /skill-name o auto-detect |
| **Claude API (programatico)** | N/A (filesystem) | .claude/skills/ (en container) | Via skills API | skill_id en container param |
| **claude.ai / Cowork** | N/A (cloud) | N/A (upload ZIP) | Organization settings > Skills | Auto-trigger via descripcion |
| **Codex CLI (OpenAI)** | ~/.codex/skills/ | .agents/skills/ (en repo) | /etc/codex/skills/ (admin) | $skill-name, /skills, implicit |
| **Cursor (IDE)** | ~/.cursor/ | .cursor/rules/*.mdc | No hay skills nativos | N/A (.cursorrules legacy) |
| **Goose (CLI)** | [PENDIENTE] | [PENDIENTE] | No | Via extensiones MCP |

## Tabla Comparativa - ZDR / Retencion de Datos

| Plataforma | Retencion Estandar | ZDR Disponible | Alcance ZDR | Requisito |
|------------|-------------------|----------------|-------------|-----------|
| **Claude Code (CLI)** | 30 dias (commercial) | Si (Claude for Enterprise) | Solo Claude Code inference; NO claude.ai chat, NO Cowork, NO third-party integrations | Enterprise plan; contactar account team |
| **Claude API (programatico)** | 30 dias (commercial) | Si (API org keys) | API requests | Enterprise/commercial API keys |
| **claude.ai / Cowork** | 30 dias (commercial) | NO para Cowork | [N/A - Cowork excluido de ZDR] | [N/A] |
| **Codex CLI (OpenAI)** | 30 dias (ChatGPT Enterprise) | Si (ChatGPT Enterprise) | App, CLI e IDE | ChatGPT Enterprise; codigo permanece en entorno del dev |
| **Cursor (IDE)** | 30 dias (partners pueden retener) | Privacy Mode (gratuito) | Zero data retention at model providers; embeddings sin codigo fuente | Toggle en settings; enforceable por admin en Business/Enterprise |
| **Goose (CLI)** | Depende del LLM provider | Depende del LLM provider | N/A (open source, datos van al provider del LLM) | Configurar en provider |

## Tabla Comparativa - Soporte para Skills (SKILL.md)

| Plataforma | Skill Format | Soporte Skills | Auto-trigger | Scripts Ejecutables |
|------------|-------------|----------------|--------------|-------------------|
| **Claude Code (CLI)** | SKILL.md + scripts/ + references/ + assets/ | Nativo completo | Si (via description) | Si (Python, Bash, etc.) |
| **Claude API (programatico)** | SKILL.md | Via container param + /v1/skills | Si | En Code Execution Container |
| **claude.ai / Cowork** | ZIP upload | 132 pre-built + upload custom | Si | En sandbox VM (pip+npm) |
| **Codex CLI (OpenAI)** | SKILL.md + scripts/ + references/ + assets/ | Nativo completo; ~/.codex/skills/ | Si (implicit + explicit) | Si |
| **Cursor (IDE)** | .cursorrules (legacy), .cursor/rules/*.mdc (v1.7+) | Parcial (rules, no skills propiamente) | Condicional (file-scoped) | No (solo via MCP) |
| **Goose (CLI)** | SKILL.md via MCP/extension | Via extensiones MCP (no nativo) | [PENDIENTE] | Via shell tool |

---

## Hallazgos Detallados

```
Claim: Claude Code usa sandbox opcional con bubblewrap (Linux) y Seatbelt (macOS) que reduce prompts de permiso en un 84%.
Source: Anthropic Engineering Blog / InventiveHQ
URL: https://inventivehq.com/knowledge-base/claude/how-to-manage-permissions-and-sandboxing
Date: 2026
Excerpt: "Sandboxing creates defined boundaries within which Claude can work more freely. According to Anthropic, sandboxing reduces permission prompts by 84% in internal usage while maintaining security."
Context: Para MWT, el sandbox de Claude Code ofrece un balance de seguridad y productividad. Pero el acceso a SP-API desde el sandbox requeriria anadir los dominios de Amazon a la allowlist.
Confidence: high
```

```
Claim: Claude Code en sandbox usa un proxy local que verifica una allowlist de dominios aprobados. Nuevos dominios requieren confirmacion del usuario.
Source: Claude Code Camp
URL: https://www.claudecodecamp.com/p/claude-code-sandboxing-how-sandbox-works-and-what-it-doesn-t-protect
Date: 2026-04-09
Excerpt: "Network isolation routes all traffic through a proxy: Only approved domains can be accessed. New domain requests prompt for user confirmation. Git operations use a separate proxy that verifies operations without exposing credentials."
Context: Critico para MWT: si se usa Claude Code con sandbox, cada dominio de SP-API/n8n debe ser aprobado manualmente o configurado en settings.json.
Confidence: high
```

```
Claim: Cowork ejecuta en una VM Ubuntu 22.04 ARM64 sandboxed con bubblewrap, sin acceso a root/sudo, y todas las conexiones salientes pasan por un proxy con lista blanca gestionada por Anthropic que no puede ser modificada por el usuario.
Source: GitHub Issue anthopics/claude-code #37970
URL: https://github.com/anthropics/claude-code/issues/37970
Date: 2026-03-23
Excerpt: "In Cowork mode, the sandbox proxy blocks all external API calls that are not on Anthropic's managed allowlist. Project-level sandbox.network.allowedDomains settings are completely ignored, making it impossible for users to add domains they need."
Context: IMPACTO CRITICO PARA MWT: Cowork NO puede llamar SP-API, n8n, ni ningun API externo no aprobado por Anthropic. Las configuraciones de allowedDomains del usuario son ignoradas por allowManagedDomainsOnly=true.
Confidence: high
```

```
Claim: Cowork tiene 132 skills pre-construidos y 131 conectores MCP pre-instalados, pero el sandbox impide acceso a dominios no aprobados.
Source: Gradually.ai
URL: https://www.gradually.ai/en/claude-code-vs-claude-cowork/
Date: 2026-04-27
Excerpt: "Claude Cowork: 132 pre-built skills, 131 pre-installed MCP connectors. Filesystem access: Sandbox (mnt/outputs). Root/sudo: No (blocked by sandbox). Package managers: pip + npm only."
Context: Cowork tiene muchos conectores pero el sandbox de red impide que skills personalizados llamen SP-API/n8n a menos que Anthropic haya aprobado esos dominios.
Confidence: high
```

```
Claim: ZDR para Claude Code esta disponible solo en Claude for Enterprise, cubre solo la inferencia de Claude Code (NO claude.ai chat, NO Cowork, NO integraciones de terceros). Cada organizacion requiere habilitacion separada.
Source: Claude Code Docs (oficial)
URL: https://code.claude.com/docs/en/zero-data-retention
Date: 2026-05-02
Excerpt: "ZDR covers Claude Code inference on Claude for Enterprise... ZDR does not extend to: Chat on claude.ai, Cowork, Third-party integrations. ZDR is enabled on a per-organization basis; each new organization must have ZDR enabled separately by your account team."
Context: Para MWT: Cowork NO esta cubierto por ZDR. Los datos procesados por MCP servers (como SP-API) tampoco. Si se requiere ZDR para workflows con SP-API, debe usarse Claude Code CLI (no Cowork) + Enterprise.
Confidence: high
```

```
Claim: Skills se pueden distribuir org-wide en Claude for Enterprise via Organization settings > Skills, y se pueden asignar a grupos especificos via plugins.
Source: Anthropic Support (oficial)
URL: https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization
Date: 2026-05-29
Excerpt: "When you upload a skill through organization settings, it becomes available to everyone in your organization in Customize > Skills. To give a skill to only some members, bundle your skills into a plugin and assign that plugin to a group."
Context: MWT puede centralizar la distribucion de skills para SP-API/n8n en su org de Claude Enterprise, asignando solo a equipos relevantes.
Confidence: high
```

```
Claim: Claude Code tiene 25+ eventos de hooks (PreToolUse, PostToolUse, SessionStart, Stop, etc.) que permiten automatizacion y gobernanza. PreToolUse puede bloquear acciones.
Source: Claude Code Docs (oficial)
URL: https://code.claude.com/docs/en/hooks
Date: 2025-09-01
Excerpt: "PreToolUse: Before a tool call executes. Can block it. PermissionRequest: When a permission dialog appears. PostToolUse: After a tool call succeeds."
Context: MWT puede usar hooks para bloquear accesos a datos sensibles, loggear llamadas a SP-API, y auto-aprobar operaciones seguras.
Confidence: high
```

```
Claim: La API de Claude (Messages API) soporta skills via el parametro "container" en Code Execution, con endpoint /v1/skills para gestion programatica.
Source: Verdent.ai / Claude API Docs
URL: https://www.verdent.ai/guides/claude-agent-skills
Date: 2025-12-15
Excerpt: "Claude API: Reference skills by skill_id in the container parameter. Manage via /v1/skills endpoint. Code execution container, programmatic versioning."
Context: MWT puede invocar skills programaticamente desde sus sistemas backend, integrando SP-API/n8n via la API sin necesidad de Claude Code CLI.
Confidence: high
```

```
Claim: Codex CLI (OpenAI) usa sandbox por defecto sin acceso a red. Las herramientas incluyen: Read, Write, Edit, Bash (sandboxed), MCP, apply_patch, js_repl, web_search.
Source: OpenAI Codex Docs (oficial)
URL: https://developers.openai.com/codex/skills
Date: 2026
Excerpt: "By default, the agent runs with network access turned off. Locally, Codex uses an OS-enforced sandbox that limits what it can touch (typically to the current workspace). Codex uses different sandbox modes depending on where you run it: Codex CLI / IDE extension: OS-level mechanisms enforce sandbox policies. Defaults include no network access and write permissions limited to the active workspace."
Context: Para MWT: Codex CLI requiere habilitar explicitamente el acceso a red (--sandbox con perfil que permita outbound) para poder llamar SP-API/n8n. Esto es mas restrictivo que Claude Code.
Confidence: high
```

```
Claim: Codex CLI soporta skills con el mismo formato SKILL.md, leyendo desde ~/.codex/skills/ (usuario) y .agents/skills/ (proyecto). Incluye invocacion implicita y explicita.
Source: OpenAI Codex Docs (oficial)
URL: https://developers.openai.com/codex/skills
Date: 2026
Excerpt: "A skill is a directory with a SKILL.md file plus optional scripts and references. Codex can activate skills in two ways: Explicit invocation: Include the skill directly in your prompt. Implicit invocation: Codex can choose a skill when your task matches the skill description."
Context: MWT puede portar skills de Claude Code a Codex CLI con minima modificacion (mismo formato SKILL.md).
Confidence: high
```

```
Claim: Cursor IDE no tiene skills nativos en formato SKILL.md. Usa .cursorrules (legacy) o .cursor/rules/*.mdc (actual) para reglas de comportamiento. Soporta MCP servers (max 40 tools) y tiene terminal integrada que puede ejecutar bash.
Source: DeployHQ / Cursor Docs
URL: https://www.deployhq.com/guides/cursor
Date: 2026-04-30
Excerpt: "Cursor exposes three AI surfaces: Inline Edit, Chat, and Agent mode... Cursor implements MCP... Configure servers in Settings > MCP or in ~/.cursor/mcp.json... The modern format for Cursor Rules: .cursor/rules/*.mdc - markdown files with YAML frontmatter."
Context: Cursor puede integrar SP-API/n8n via MCP servers, pero no usa el sistema de skills SKILL.md nativamente. Requiere MCP servers para integraciones externas.
Confidence: high
```

```
Claim: Cursor tiene Privacy Mode (gratuito) que habilita zero data retention en los proveedores de modelos. Los admins de Business/Enterprise pueden forzar Privacy Mode para todos los miembros.
Source: Cursor Data Use & Privacy
URL: https://cursor.com/data-use
Date: 2025-10-20
Excerpt: "If you enable 'Privacy Mode' in Cursor's settings: zero data retention will be enabled for our model providers. Cursor may store some code data to provide additional features. Your code is never used by us or any third party for training."
Context: Para MWT: Cursor tiene mejor postura de privacidad que la mayoria, pero los datos de SP-API pasarian por los servidores de Cursor (aunque con ZDR en el provider del modelo).
Confidence: high
```

```
Claim: Goose CLI (Block) es open-source, soporta 25+ LLM providers, usa MCP para extensiones, y tiene herramientas built-in: shell, text_editor, analyze, screen_capture, image_processor. Ejecuta con privilegios del usuario (Autonomous mode por defecto).
Source: Goose Docs (oficial)
URL: https://goose-docs.ai/docs/mcp/developer-mcp/
Date: 2026-04-07
Excerpt: "The Developer extension provides these tools: shell - Execute shell commands, text_editor - Read, write, and edit files, analyze - Analyze code structure, screen_capture - Take screenshots, image_processor - Process and resize images. By default, goose can run system commands with your user privileges and edit any accessible file without your approval."
Context: Goose tiene acceso total al sistema (sin sandbox inherente), lo que permite llamar SP-API/n8n sin restricciones, pero con mayor riesgo de seguridad. Ideal para entornos controlados.
Confidence: high
```

```
Claim: El estandar abierto Agent Skills (agentskills.io) es soportado por 16+ herramientas incluyendo Claude Code, Cursor, Codex CLI, Goose, Copilot, Gemini CLI. skills.sh es el hub de distribucion principal.
Source: inference.sh
URL: https://inference.sh/blog/skills/agent-skills-overview
Date: 2026-04-13
Excerpt: "The Agent Skills format was developed by Anthropic and released as an open standard in late 2025. At last count, skills.sh lists compatibility with Claude Code, Cursor, GitHub Copilot, Goose, Codex CLI, Windsurf, Gemini CLI, Roo Code, Trae, and many others."
Context: MWT puede construir skills portables que funcionen en multiples plataformas, reduciendo vendor lock-in.
Confidence: high
```

```
Claim: Existe un MCP server comercial (DataDoe) que expone Amazon SP-API y Amazon Ads API via MCP, compatible con Claude, Cursor, Codex CLI, Gemini, Copilot, ChatGPT, y n8n. No requiere aprobacion de SP-API developer.
Source: DataDoe / MCP Servers Registry
URL: https://mcpservers.org/servers/deltologic/datadoe-mcp
Date: 2026
Excerpt: "Hosted Amazon Seller Central & Vendor Central MCP server. Connect Claude, ChatGPT, Cursor, Codex, Gemini, and GitHub Copilot to live Amazon SP-API and Amazon Ads API data. DataDoe handles the SP-API developer approval, OAuth, and rate limits so your AI agent starts querying in under a minute."
Context: MWT puede usar DataDoe MCP para integrar SP-API en cualquier plataforma que soporte MCP (Claude Code, Cursor, Codex CLI, Goose) sin esperar aprobacion de Amazon.
Confidence: high
```

```
Claim: Existe un MCP server (mcp-n8n) que permite a Claude Desktop y Cursor gestionar workflows de n8n directamente via lenguaje natural. Soporta 41 tools para gestion completa de n8n.
Source: GitHub - leosepulveda/mcp-n8n
URL: https://github.com/leosepulveda/mcp-n8n
Date: 2025-10-29
Excerpt: "Complete n8n API integration for Claude Desktop and Cursor - Manage workflows, automate tasks, and control every aspect of n8n directly through AI conversations. 41 tools for complete n8n management."
Context: MWT puede usar mcp-n8n para que Claude Code/Cursor gestionen workflows de n8n via MCP, automatizando la integracion SP-API -> n8n -> Claude.
Confidence: high
```

```
Claim: Claude Code on the web ejecuta en VMs gestionadas por Anthropic en la nube, con acceso configurable a red. Se clona el repo de GitHub en una VM aislada.
Source: Claude Code Docs (oficial)
URL: https://code.claude.com/docs/en/web-quickstart
Date: 2025-09-01
Excerpt: "Claude Code on the web runs on Anthropic-managed cloud infrastructure instead of your machine. Your repository is cloned into an isolated virtual machine. Network access: internet access is set based on your environment's access level."
Context: Para MWT: si se usa Claude Code en la web, los datos de SP-API se procesarian en VMs de Anthropic (consideracion de gobernanza). El acceso a red es configurable.
Confidence: high
```

```
Claim: Claude Code Remote Control permite acceder a una sesion local desde el movil/navegador sin que el codigo se mueva a la nube. Todo corre en la maquina local.
Source: DevOps.com
URL: https://devops.com/claude-code-remote-control-keeps-your-agent-local-and-puts-it-in-your-pocket/
Date: 2026-02-26
Excerpt: "No code moves to the cloud. No environment gets replicated somewhere else. Your phone is just a window into the session still running on your computer, with full access to your filesystem, MCP servers, tools, and project configuration."
Context: Para MWT: Remote Control permite monitorizar ejecuciones de skills SP-API/n8n desde movil sin comprometer soberania de datos.
Confidence: high
```

```
Claim: La retencion de datos de Claude Code para usuarios comerciales es de 30 dias estandar, con ZDR disponible en Enterprise. Los datos locales se almacenan en ~/.claude/projects/ por 30 dias.
Source: Claude Code Docs (oficial)
URL: https://code.claude.com/docs/en/data-usage
Date: 2026-05-15
Excerpt: "Commercial users (Team, Enterprise, and API): Standard: 30-day retention period. Zero data retention: available for Claude Code on Claude for Enterprise. Local caching: Claude Code clients store session transcripts locally in plaintext under ~/.claude/projects/ for 30 days."
Context: Para MWT: considerar ZDR en Enterprise si los datos de SP-API son sensibles. Los datos locales en ~/.claude/ deben protegerse.
Confidence: high
```

```
Claim: OpenAI ofrece Zero Data Retention para clientes Enterprise de ChatGPT, incluyendo Codex CLI. Por defecto, la API de OpenAI retiene datos 30 dias para monitoreo de abuso.
Source: OpenAI Developers Docs (oficial)
URL: https://developers.openai.com/api/docs/guides/your-data
Date: 2026-04-23
Excerpt: "By default, abuse monitoring logs are generated for all API feature usage and retained for up to 30 days. Eligible customers may have their customer content excluded from these abuse monitoring logs by getting approved for Zero Data Retention or Modified Abuse Monitoring controls."
Context: Para MWT: si usa Codex CLI con ChatGPT Enterprise, puede habilitar ZDR. Pero requiere aprobacion previa por OpenAI.
Confidence: high
```

```
Claim: En Cowork, los skills provisionados a nivel de organizacion aparecen en chat, web, Chat tab de Claude Desktop, y Cowork. El targeting de grupos configurado para Cowork se aplica automaticamente.
Source: Anthropic Support (oficial)
URL: https://support.claude.com/en/articles/13119606-provision-and-manage-skills-for-your-organization
Date: 2026-05-29
Excerpt: "Skills provisioned this way appear in chat, on the web and the Chat tab in Claude Desktop, as well as in Cowork. Group targeting you've already set up for Cowork carries over to chat with no extra steps."
Context: Skills para SP-API/n8n distribuidos org-wide estaran disponibles en Cowork, aunque Cowork no pueda ejecutar llamadas de red a esos servicios por el sandbox.
Confidence: high
```

---

## Matriz de Compatibilidad para MWT: SP-API + n8n

| Plataforma | Puede llamar SP-API? | Puede llamar n8n? | Metodo | Restricciones |
|------------|---------------------|-------------------|--------|---------------|
| **Claude Code (CLI, sin sandbox)** | Si | Si | Bash: curl, Python requests, MCP server | Sin restricciones de red inherente |
| **Claude Code (CLI, con sandbox)** | Si (con allowlist) | Si (con allowlist) | Bash via proxy sandbox | Dominios deben estar en allowedDomains |
| **Claude Code (web/cloud)** | Si | Si | Bash en VM de Anthropic | Acceso a red configurable por environment |
| **Claude API (programatico)** | Si | Si | Desde el codigo del usuario | Depende del entorno del usuario |
| **claude.ai / Cowork** | **NO** | **NO** | N/A - proxy bloquea todo | Lista blanca de Anthropic; no configurable por usuario |
| **Codex CLI (OpenAI)** | Si (habilitar red) | Si (habilitar red) | Bash sandboxed con red habilitada | Red desactivada por defecto; requiere --sandbox con perfil de red |
| **Cursor (IDE)** | Si (via MCP) | Si (via MCP) | MCP server + terminal bash | Limite de 40 tools MCP; requiere MCP server |
| **Goose (CLI)** | Si | Si | shell tool (completo) | Sin sandbox inherente; riesgo de seguridad mayor |

---

## Recomendaciones para MWT

### Para SP-API (Amazon Selling Partner API)

1. **Mejor opcion: Claude Code (CLI)** con skills + MCP server de DataDoe para SP-API. Acceso completo a red, skills nativos SKILL.md, hooks para logging/seguridad, y ZDR disponible en Enterprise.

2. **Alternativa: Cursor IDE** con MCP server de DataDoe para SP-API. Buena para workflows mixtos de codigo + datos de Amazon.

3. **Para automatizacion programatica: Claude API** con Code Execution Container. Permite invocar skills via API sin terminal.

4. **Cowork NO es viable** para integracion directa con SP-API debido al sandbox de red que bloquea todos los dominios no aprobados por Anthropic.

### Para n8n

1. **Mejor opcion: Claude Code (CLI)** con MCP server mcp-n8n. Permite gestionar workflows de n8n via lenguaje natural desde la terminal.

2. **Alternativa: Cursor** con MCP server mcp-n8n. Terminal integrada + MCP.

3. **Codex CLI** tambien compatible via MCP.

4. **Goose CLI** puede ejecutar n8n CLI commands via shell tool.

### Para ZDR/Compliance

- Si se requiere Zero Data Retention: usar **Claude Code (CLI)** con Claude for Enterprise (ZDR disponible) o **Cursor** con Privacy Mode activado.
- **Evitar Cowork** para datos sensibles de SP-API: no tiene ZDR y los datos pasan por sandbox de Anthropic.
- Los datos procesados por MCP servers de terceros (DataDoe, n8n) NO estan cubiertos por ZDR de Anthropic.

### Distribucion Org-wide

- Usar **Claude for Enterprise** para provisionar skills SP-API/n8n a toda la org.
- Asignar skills solo a grupos relevantes via plugins (ej: equipo de Amazon Operations).
- Configurar managed-mcp.json para controlar que MCP servers estan permitidos.
- Usar hooks PreToolUse para bloquear accesos no autorizados y loggear llamadas a SP-API.

---

*Documento generado: Junio 2026*
*Fuentes: Documentacion oficial de Anthropic, OpenAI, Cursor, Goose; articulos tecnicos verificados; GitHub issues; blogs de la comunidad.*
