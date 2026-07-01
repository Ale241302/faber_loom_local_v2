# dim01 — Qué son las Agent Skills (estado a junio 2026)

Las Agent Skills son un estándar abierto, originado por Anthropic (anuncio público 16-oct-2025, estándar abierto 18-dic-2025), para empaquetar conocimiento procedimental reutilizable como carpetas con un archivo `SKILL.md` (YAML frontmatter + cuerpo Markdown + recursos opcionales). El mecanismo central es la *progressive disclosure*: tres niveles de carga (metadata siempre cargada, instrucciones al activarse, recursos/scripts bajo demanda) que mantienen el contexto proporcional a lo que el agente usa, no a lo que tiene instalado. Esta dim cubre la definición técnica, el origen/fechas, y la diferenciación Skill vs Tool/MCP vs Sub-agente vs Plugin vs System prompt, con tabla comparativa y criterio de decisión.

---

## 1. Definición técnica

Claim: Una Agent Skill es un directorio que contiene como mínimo un archivo `SKILL.md` con frontmatter YAML (metadata) y cuerpo Markdown (instrucciones); puede incluir scripts, referencias y assets opcionales cargados de forma diferida.
Source: Loic Carrere (Medium)
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "At its core, a skill is a folder containing one required file ... The `SKILL.md` file has two parts: **YAML frontmatter** with metadata (name, description, version) and a **Markdown body** with the actual instructions ... These resources are loaded lazily: the agent only reads them when it actually needs them, not at startup."
Context: Define la unidad mínima que la plataforma MWT/FaberLoom tendría que versionar y promover via sync. El frontmatter es la superficie de gobernanza (equivalente a los headers obligatorios ENT/PLB/POL).
Confidence: high

Claim: Los campos requeridos del frontmatter son `name` (max 64 chars, minúsculas/números/guiones, sin tags XML, sin palabras reservadas "anthropic"/"claude") y `description` (no vacío, max 1024 chars, sin tags XML), donde la description debe explicar qué hace y cuándo usar la skill.
Source: Anthropic / Claude Platform Docs (oficial)
URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
Date: 2026 (docs vivas)
Excerpt: "`name`: Maximum 64 characters, Must contain only lowercase letters, numbers, and hyphens, Cannot contain XML tags, Cannot contain reserved words: \"anthropic\", \"claude\". `description`: Must be non-empty, Maximum 1024 characters, Cannot contain XML tags ... The `description` should include both what the Skill does and when Claude should use it."
Context: Estos constraints son enforcement-relevantes: el `name` debe coincidir con el directorio, y `description` es load-bearing para el discovery. Para multi-tenant, la calidad de la description determina si la skill se dispara o no.
Confidence: high

Claim: `version` no es un campo top-level del spec; debe ir dentro del mapa `metadata` para máxima portabilidad. Campos opcionales incluyen `license`, `compatibility` (max 500 chars) y `allowed-tools` (experimental).
Source: Loic Carrere (Medium)
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "license (optional) License name or reference to a bundled license file. compatibility (optional) Max 500 chars. Environment requirements. metadata (optional) Key-value map for version, author, tags, etc. allowed-tools (optional) Space-delimited list of pre-approved tools. (Experimental.) ... **Note:** `version` is not a top-level spec field. Use the `metadata` map for maximum portability."
Context: Importa para la convención de headers de MWT: si se modela `version`/`status`/`visibility` en skills, deben ir en `metadata` para no romper portabilidad con el estándar agentskills.io.
Confidence: high

## 2. Progressive disclosure (mecanismo central)

Claim: La progressive disclosure opera en tres niveles: (1) Metadata siempre cargada (~100 tokens/skill, name+description inyectados al system prompt); (2) Instrucciones cargadas al activarse (cuerpo SKILL.md, <5k tokens); (3) Recursos/código bajo demanda (efectivamente ilimitado, ejecutado via bash sin cargar contenido al contexto).
Source: Anthropic / Claude Platform Docs (oficial)
URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
Date: 2026 (docs vivas)
Excerpt: "Level 1: Metadata — Always (at startup) — ~100 tokens per Skill — name and description from YAML frontmatter. Level 2: Instructions — When Skill is triggered — Under 5k tokens — SKILL.md body with instructions and guidance. Level 3+: Resources — As needed — Effectively unlimited — Bundled files executed via bash without loading contents into context."
Context: Este es el argumento de costo central para una plataforma multi-tenant: puedes instalar decenas de skills por tenant sin penalización de contexto permanente; sólo pagas tokens del catálogo (~100/skill) hasta que se activa la relevante.
Confidence: high

Claim: Los scripts bundleados se ejecutan via bash y sólo su salida entra al contexto; el código del script nunca se carga. Esto da operaciones deterministas y repetibles sin costo de tokens del código.
Source: Anthropic Engineering (oficial)
URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
Date: 2025-10-16
Excerpt: "In our example, the PDF skill includes a pre-written Python script that reads a PDF and extracts all form fields. Claude can run this script without loading either the script or the PDF into context. And because code is deterministic, this workflow is consistent and repeatable."
Context: Clave para FaberLoom: tareas frágiles (validaciones, migraciones, parsing SP-API) deben ir como scripts deterministas dentro de la skill, no como generación on-the-fly del LLM. Reduce alucinación y da reproducibilidad auditable.
Confidence: high

Claim: Como los archivos no consumen contexto hasta accederse, el contenido bundleado de una skill es "efectivamente ilimitado" / "unbounded": puede incluir documentación API extensa, datasets grandes o ejemplos sin penalización de contexto si no se usan.
Source: Anthropic Engineering (oficial)
URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
Date: 2025-10-16
Excerpt: "Agents with a filesystem and code execution tools don't need to read the entirety of a skill into their context window when working on a particular task. This means that the amount of context that can be bundled into a skill is effectively unbounded."
Context: Permite que un tenant cargue KB-domain completos (schemas, catálogos de producto SP-API, guías de marca) como referencias bajo demanda sin inflar cada turno. Es el patrón opuesto al system prompt monolítico.
Confidence: high

## 3. Origen y fechas clave

Claim: Anthropic introdujo públicamente Agent Skills el 16 de octubre de 2025; el formato se publicó como estándar abierto el 18 de diciembre de 2025 para portabilidad cross-platform.
Source: Anthropic Engineering (oficial)
URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
Date: 2025-10-16
Excerpt: "Published Oct 16, 2025 ... *Update: We've published* [*Agent Skills*](https://agentskills.io/) *as an open standard for cross-platform portability. (December 18, 2025)*"
Context: Establece la línea temporal canónica. La fecha del open standard (18-dic-2025) es la que habilita la portabilidad fuera de Claude (Cursor, Copilot, etc.), relevante si MWT/FaberLoom quiere skills no atadas a un solo vendor.
Confidence: high

Claim: El estándar fue desarrollado por Anthropic y publicado open source; el ecosistema agéntico más amplio se coordina vía la Agentic AI Foundation bajo la Linux Foundation, cuyos miembros platinum incluyen AWS, Anthropic, Block, Google, Microsoft y OpenAI.
Source: Loic Carrere (Medium)
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "The standard was developed by Anthropic and published as open source. The broader agentic AI ecosystem is coordinated through the [Agentic AI Foundation](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation) under the Linux Foundation, whose platinum members include AWS, Anthropic, Block, Google, Microsoft, and OpenAI."
Context: Señala que Skills no es lock-in de Anthropic. La adopción cross-vendor reduce riesgo estratégico para una plataforma en producción que quiera evitar atarse a un único proveedor de modelos.
Confidence: high

Claim: La adopción se extendió a OpenAI Codex (lee de `.agents/skills`), GitHub Copilot (`.github/skills/`), VS Code, Cursor (SKILL.md a nivel workspace), Block/Goose y Spring AI (implementación Java/Spring).
Source: Loic Carrere (Medium)
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "**OpenAI Codex** — reads skills from `.agents/skills` directories ... **GitHub Copilot** -- loads skills from `.github/skills/` in repositories **VS Code** -- native agent skills support in Copilot ... **Cursor** -- supports SKILL.md for workspace-level agent customization **Block (Goose)** -- open-source agent with full skills support **Spring AI** -- Java/Spring implementation"
Context: Confirma que el formato SKILL.md es interoperable a nivel directorio. Una skill autorizada por MWT podría funcionar en Cursor/Copilot del equipo de dev sin reescritura.
Confidence: medium

## 4. Skill vs Tool (MCP) vs Sub-agente vs Plugin vs System prompt

Claim: Skills NO son tools: un tool es una acción determinista (input -> output estructurado); una skill es un conjunto de instrucciones interpretadas por el LLM. Las skills describen *cómo* hacer algo; los tools *hacen* algo. (Goose/Block: "skills describe the workflow, while MCP provides the runner".)
Source: Loic Carrere (Medium)
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "**Skills are not tools.** A tool is a deterministic action: call it with inputs, get a structured output. A skill is a set of instructions interpreted by an LLM. Skills describe *how* to do something. Tools *do* something. As the Goose team at Block put it: skills describe the workflow, while MCP provides the runner."
Context: Distinción núcleo para el stack MWT (MCP + n8n + SP-API). MCP da acceso/acción; la skill da el procedimiento de cómo usar ese acceso bien. No son sustitutos, son capas.
Confidence: high

Claim: Skills NO reemplazan MCP: MCP es un protocolo de comunicación (JSON-RPC 2.0) que da conectividad/acción a sistemas externos; las skills dan conocimiento procedimental para *usar* esos sistemas. Diferentes capas del mismo stack. ("MCP gives agents abilities; skills teach agents how to use those abilities well.")
Source: Loic Carrere (Medium)
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "MCP provides secure connectivity to external systems. Skills provide procedural knowledge for *using* those systems. Different layers, same stack ... an MCP server connects to your PostgreSQL database and exposes a `run_query` tool. But the agent still needs to know *how* to write safe, efficient SQL for your specific schema. That is what a `database-query` skill provides."
Context: Aplicable directamente: el MCP SP-API expone tools; una skill `sp-api-listings` enseña al agente las reglas/edge-cases del schema multi-tenant. El ejemplo PostgreSQL es casi 1:1 con el caso MWT.
Confidence: high

Claim: Una formulación complementaria: MCP es "External Reach" (acceso, dónde vive el dato); Skills son "Internal Wisdom" (expertise, cómo procesar el dato). MCP dice *dónde* está la tabla; la skill dice *cómo* procesarla.
Source: Neelam Pawar (Medium / Google Cloud Community)
URL: https://medium.com/google-cloud/agent-skills-dynamic-context-engineering-c1bebf028cf7
Date: 2026-04-07
Excerpt: "\"Internal Wisdom\" (Skills) from \"External Reach\" (MCP). MCP provides access, Skills provide expertise ... While a Skill tells the agent how to process a table, MCP tells the agent where that table actually lives. MCP connects your agent to external systems and data."
Context: Refuerzo independiente del mismo claim desde una segunda fuente (Google Cloud Community), lo que sube la confianza en la frontera Skill/MCP.
Confidence: high

Claim: Skills NO son sub-agentes: un sub-agente es un agente independiente con su propio modelo, tools, memoria y loop de decisión (contexto aislado); una skill es más ligera, aumenta el comportamiento de un agente *existente* sin crear nuevo contexto de ejecución. ("subagentes = contratar a un especialista; skills = leer el playbook del especialista tú mismo".) Ambos —agentes y sub-agentes— pueden usar skills.
Source: Loic Carrere (Medium) / Neelam Pawar (Medium)
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "A subagent is a fully independent agent with its own model, tools, and conversation history. A skill is lighter: it augments an *existing* agent's behavior without creating a new execution context. Think of subagents as \"hiring a specialist contractor\" and skills as \"reading the specialist's playbook yourself.\""
Context: Decisión de arquitectura FaberLoom: usar sub-agentes para dividir trabajo (paralelizar, aislar permisos); usar skills para que cada worker —incluido el sub-agente— sea la versión más experta de sí mismo. No compiten.
Confidence: high

Claim: Skills NO son system prompts: un system prompt está siempre presente, consume tokens siempre y suele estar hardcodeado; una skill se carga sólo cuando se necesita y se descarga al terminar, viviendo fuera del código como artefacto portable/versionable.
Source: Loic Carrere (Medium)
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "A system prompt is always present, always consuming tokens, and typically hardcoded. A skill is loaded only when needed and unloaded when done. Skills are **portable artifacts** that live outside your code, so you can share, version, review, and swap them without changing a line of code."
Context: Argumento para mover guardrails de dominio del system prompt monolítico (que sufre "instruction drift") a skills. Coincide con el diagnóstico de Shafat sobre los rule-files que se vuelven "instruction blackholes".
Confidence: high

Claim: En la práctica los agentes de producción combinan los cinco: system prompt para comportamiento base, skills para expertise de tarea, MCP para datos externos, function calling para acciones, sub-agentes para orquestación compleja.
Source: Loic Carrere (Medium)
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "**In practice, production agents combine all of these.** System prompt for baseline behavior, skills for task-specific expertise, MCP for external data, function calling for actions, and subagents for complex orchestration."
Context: Confirma que la pregunta correcta para MWT no es "Skills O MCP" sino "qué capa para qué responsabilidad". Es la base de la tabla de decisión de abajo.
Confidence: high

### Tabla comparativa (síntesis de fuentes; columnas de Carrere)

| Dimensión | Agent Skills | MCP / Tools | Function Calling | System Prompt | Sub-agentes |
|---|---|---|---|---|---|
| Qué es | Módulo de conocimiento (workflow/expertise) | Conectividad / acción a sistemas externos | Acción estructurada única | Texto estático base | Contexto de ejecución independiente |
| Formato | Markdown + YAML (folder) | JSON-RPC 2.0 (protocolo) | Schema de función | String en código | Agente con modelo/tools/memoria propios |
| Ejecución | LLM interpreta instrucciones | Llamada API determinista | Invocación de función | Siempre en contexto | Loop de decisión propio |
| Carga | On-demand (3 niveles) | Siempre conectado | Schema siempre presente | Siempre presente | On-demand |
| Costo de tokens | Sólo cuando activa (~100/skill catálogo) | Schema presente cada turno | Schema presente | Siempre | Contexto separado |
| Portabilidad | Cross-platform (open standard) | Cross-platform | Específica del proveedor | Específica del vendor | Específica del framework |
| Mejor para | Workflows, expertise procedimental | Acceso a datos/acciones externas | Acciones individuales | Comportamiento baseline | Trabajo autónomo / divide-y-vencerás |

Fuente de la tabla: Carrere, "The Full Comparison" (texto literal: *"Agent Skills / MCP Tools / Function Calling / System Prompts / Subagents — What it is / Loading / Token cost / Portability / Best for"*). URL arriba. Date 2026-02-09. Confidence: high.

Nota sobre "Plugin": el pedido pide diferenciar también Plugin. **[NO VERIFICADO en las fuentes Medium leídas]** — ninguna de las seis fuentes consultadas define formalmente "Plugin" como categoría comparable a Skill/Tool/Sub-agente. Las docs oficiales mencionan que en Claude Code las Custom Skills "can also be shared via Claude Code Plugins", lo que sugiere que un Plugin es un **mecanismo de distribución/empaquetado** (puede contener skills), no un peer conceptual de la skill. Verificar contra docs de Claude Code Plugins antes de afirmar la frontera Plugin vs Skill.

## 5. Cuándo usar cada uno (criterio de decisión)

Claim: Regla de oro para escribir una skill: si te encuentras explicando lo mismo a un agente repetidamente, escribe una skill (manteniendo SKILL.md bajo ~500 líneas / <5k tokens).
Source: Neelam Pawar (Medium / Google Cloud) + Anthropic Docs
URL: https://medium.com/google-cloud/agent-skills-dynamic-context-engineering-c1bebf028cf7
Date: 2026-04-07
Excerpt: "The rule of thumb is simple: if you find yourself explaining the same thing to an Agent repeatedly, then you need to write a skill but keep keep SKILL.md under 500 lines. Below are some example: Code review standards your team follows ... Brand guidelines for your organization ... Debugging checklists for particular frameworks"
Context: Criterio operacional para MWT: estándares de code review, formatos de commit, guías de marca, plantillas de docs (pdf/ppt/docx), checklists de debugging por framework -> candidatos directos a skill.
Confidence: high

Claim: Marco de decisión por verbo: si necesitas *encontrar* algo usa RAG; si necesitas *resolverlo* usa Agentic RAG; si necesitas *hacerlo* construye una Skill. Skills son "tus manos" (acción imperativa, secuencia de movimientos / SOP + scripts).
Source: Muhammad Abdullah Shafat Mulkana (Medium)
URL: https://medium.com/@muhammad.shafat/stop-engineering-prompts-start-engineering-context-a-guide-to-the-agent-skills-standard-bc8e2056f40a
Date: 2026-03-19
Excerpt: "The Rule of Thumb: If you need to find it, use RAG. If you need to figure it out, use Agentic RAG. If you need to do it, build a Skill ... Agent Skills are your Hands: Use this when the goal is Action ... It mounts a specialized folder containing the Standard Operating Procedure (SOP) and the scripts needed to provision that node or trigger that API. It is imperative; it defines a sequence of moves."
Context: Añade una tercera dimensión que el stack MWT ya tiene (KB/RAG). Posiciona Skills como la capa de *acción/SOP* sobre la capa de *recuperación de conocimiento* del KB, no como reemplazo del KB.
Confidence: high

Claim: Cuándo NO usar Skills (tradeoffs honestos): (1) overhead de filesystem —para un script one-off la estructura de carpetas es pura ceremonia; paga a escala de equipo o múltiples proyectos largos; (2) la description es load-bearing —vaga = nunca dispara, demasiado amplia = dispara cuando no debe; (3) over-engineering para agentes simples —si el agente hace una sola cosa, un buen rule-file puede servir mejor. Skills valen la complejidad sólo cuando hay múltiples workflows distintos que no coexisten en un solo contexto sin causar drift.
Source: Muhammad Abdullah Shafat Mulkana (Medium)
URL: https://medium.com/@muhammad.shafat/stop-engineering-prompts-start-engineering-context-a-guide-to-the-agent-skills-standard-bc8e2056f40a
Date: 2026-03-19
Excerpt: "First, filesystem overhead ... The pattern pays off at team scale or across multiple long-lived projects; not for weekend experiments. Second, the description is load-bearing ... A vague description means the agent never fires the skill ... Third, this is over-engineering for simple agents ... The Agent Skills pattern is worth the complexity only when you have multiple distinct workflows that cannot coexist in a single context window without causing drift."
Context: Contrapeso crítico para MWT: no toda capacidad debe ser skill. El criterio de adopción es "múltiples workflows distintos + drift" — exactamente el caso multi-tenant con dominios separados, pero no para agentes de propósito único.
Confidence: high

## 6. Restricciones de runtime (relevante para producción multi-tenant)

Claim: Las Custom Skills NO sincronizan entre superficies y los entornos de runtime difieren: en Claude API las skills NO tienen acceso a red ni instalación de paquetes en runtime (sólo paquetes pre-instalados); en Claude Code tienen acceso completo a red; en claude.ai el acceso a red varía según settings de usuario/admin. claude.ai no soporta gestión admin centralizada ni distribución org-wide de custom skills.
Source: Anthropic / Claude Platform Docs (oficial)
URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
Date: 2026 (docs vivas)
Excerpt: "Custom Skills do not sync across surfaces ... Claude API: No network access: Skills cannot make external API calls or access the internet. No runtime package installation ... Claude Code: Full network access ... claude.ai does not support centralized admin management or org-wide distribution of custom Skills."
Context: Crítico para MWT. Si las skills deben llamar SP-API o n8n, NO funcionarán en la sandbox de la Claude API (sin red). El runtime con red completa es Claude Code. La falta de gestión org-wide en claude.ai impacta el modelo de distribución por tenant — habría que orquestar uploads por superficie. Sharing scope: API = workspace-wide; claude.ai = individual por usuario; Claude Code = personal o por proyecto.
Confidence: high

Claim: Anthropic publica skills pre-construidas (pptx, xlsx, docx, pdf) y open-source en github.com/anthropics/skills; las Skills no son elegibles para Zero Data Retention (ZDR).
Source: Anthropic / Claude Platform Docs (oficial)
URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
Date: 2026 (docs vivas)
Excerpt: "This feature is not eligible for Zero Data Retention (ZDR) ... Pre-built Agent Skills: PowerPoint (pptx) ... Excel (xlsx) ... Word (docx) ... PDF (pdf) ... Agent Skills is not covered by ZDR arrangements. Skill definitions and execution data are retained according to Anthropic's standard data retention policy."
Context: Implicación de compliance/visibilidad para MWT: si hay datos CEO-ONLY o sensibles de tenant, la no-elegibilidad ZDR de Skills debe entrar en la POL de visibilidad antes de meter datos sensibles en SKILL.md o en su ejecución.
Confidence: high

## 7. Seguridad (frontera de confianza)

Claim: El modelo de amenaza se desplaza del prompt a la carpeta: una skill maliciosa puede dirigir al agente a exfiltrar datos o invocar tools de forma que no coincide con su propósito declarado. Mitigaciones: auditar todos los archivos bundleados, tratar como instalar software (sólo fuentes confiables), strict tool scoping, read-only por defecto, y tratar `npx skills add` con la misma cautela que `npm install`.
Source: Anthropic Docs (oficial) + Shafat (Medium)
URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
Date: 2026 (docs vivas)
Excerpt: "a malicious Skill can direct Claude to invoke tools or execute code in ways that don't match the Skill's stated purpose ... Audit thoroughly: Review all files bundled in the Skill: SKILL.md, scripts, images, and other resources ... Treat like installing software: Only use Skills from trusted sources."
Context: Directamente relevante para gobernanza MWT: las skills entran por el mismo pipeline de review/PR que el código (control_surface). El claim de Shafat sobre auditar `/scripts` de skills de terceros antes de activar mapea al principio de "no escribir KB canónico directo" y al enforcement fail-closed de hooks.
Confidence: high

---

## Síntesis para la plataforma (no-claim, derivado)

Para MWT/FaberLoom las Skills no compiten con el stack actual (Claude Code, Cowork, n8n, MCP, SP-API) sino que se insertan como **capa de SOP/procedimiento** entre el KB (RAG, recuperación de verdad) y los MCP/tools (acción externa). Decisión por capa: KB para *encontrar*, MCP/SP-API para *acceder/actuar*, Skill para *cómo ejecutar el workflow correctamente y de forma consistente*, sub-agente para *aislar y paralelizar*, system prompt sólo para baseline. La restricción de runtime sin-red en Claude API y la no-elegibilidad ZDR son los dos hechos que más condicionan dónde y con qué datos desplegar skills en producción multi-tenant.
