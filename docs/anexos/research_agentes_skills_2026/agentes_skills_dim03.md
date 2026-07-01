# DIM03 — SKILLS vs SUB-AGENTES (Agent Skills, patron SKILL.md) — Junio 2026

Investigacion para CEO de plataforma de agentes IA multi-tenant. El patron 2026 no es "skill reemplaza sub-agente" sino una arquitectura por capas: skills = modulos de conocimiento que aumentan al agente existente (texto inyectado, mismo contexto); sub-agentes = runtime/contexto aislado con su propio modelo y tools. La novedad de 2026 (`context: fork`) difumina la frontera: una skill puede ejecutarse en un sub-agente aislado. El default economico recomendado es COMPONER: sub-agente Haiku + skill precargada + MCP scoped. La evidencia de costo es consistente (Haiku ~15x mas barato que Opus; routing a Haiku reduce ~60% del gasto Opus en tareas rutinarias) pero las cifras finas (9K vs 15K tokens) vienen de un solo benchmark de tercero.

Fuentes recuperadas en full-text: 6 (awesomeskill, morphllm, alexop.dev, systemprompt.io, theaiarchitects, callsphere, mehdi.cz). Medium devolvio cuerpo vacio en cada fetch (bloqueo server-side); las afirmaciones que solo provienen de snippets de busqueda van marcadas [NO VERIFICADO].

---

## 1. Definicion tecnica: skill = conocimiento inyectado; sub-agente = sesion aislada

**Claim:** Una skill es texto markdown inyectado en el prompt de la sesion actual; un sub-agente es una sesion Claude separada con su propio modelo, restriccion de tools y contexto.
**Source:** systemprompt.io (Ed Burton)
**URL:** https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
**Date:** 2026-03-11 (mod. 2026-05-15)
**Excerpt:** "skills are reusable markdown instructions that run inside the current session. Subagents are separate AI sessions with their own model, tool restrictions, and context. Use a skill when you want Claude to follow the same instructions every time. Use a subagent when you want Claude to behave differently (cheaper model, read-only tools, isolated context) for a delegated task."
**Context:** Verdict-first del articulo. Guia construida sobre 8 plugins de produccion, 34+ skills. Es la distincion canonica que pedia dim03.
**Confidence:** high

**Claim:** Formulacion equivalente: "las skills extienden al agente principal; los sub-agentes lo reemplazan para una tarea".
**Source:** AI Architects (Tom Crawshaw)
**URL:** https://theaiarchitects.com/blog/claude-code-subagents-vs-skills
**Date:** 2026-05-12
**Excerpt:** "skills extend what the main agent can do. Subagents replace the main agent for one task. A skill teaches the parent new tricks. A subagent forks off a specialist who does the work and reports back."
**Context:** Esta es exactamente la tesis "skill aumenta al agente existente vs sub-agente como runtime aislado". Util como cita directa para el CEO.
**Confidence:** high

---

## 2. Las cuatro dimensiones de diferencia (contexto, modelo, tools, invocacion)

**Claim:** Skill y sub-agente difieren en cuatro ejes: ventana de contexto, seleccion de modelo, permisos de tools e invocacion.
**Source:** AI Architects (Tom Crawshaw)
**URL:** https://theaiarchitects.com/blog/claude-code-subagents-vs-skills
**Date:** 2026-05-12
**Excerpt:** "Context window | Skill: Loads into the parent context, eats parent tokens | Subagent: Own context window, only the final summary returns to parent. Model selection | Skill: Runs on whatever model the parent is running | Subagent: Can run on a cheaper model (e.g. Haiku). Tool permissions | Skill: Inherits parent agent's tool permissions | Subagent: Can declare a restricted tool list in YAML (real safety control). Invocation | Skill: Auto-loads when description matches the task | Subagent: Called explicitly or via routing logic."
**Context:** Tabla operativa. Para multi-tenant, el eje "tool permissions" es el critico: solo el sub-agente da control de seguridad real via lista restringida en YAML.
**Confidence:** high

**Claim:** Tabla de 13 filas confirma: skill NO accede a data externa, NO restringe tools (hereda los de la sesion), NO elige modelo barato, NO aisla contexto; el sub-agente SI en los cuatro.
**Source:** systemprompt.io
**URL:** https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
**Date:** 2026-03-11
**Excerpt:** "Can restrict tools? | Skills: No. Inherits the calling session's tools | Subagents: Yes. tools: and disallowedTools: fields. Can pick a cheaper model? | Skills: No | Subagents: Yes. model: haiku, sonnet, or opus. Isolated context? | Skills: No. Adds to the current conversation | Subagents: Yes. Fresh context window per invocation."
**Context:** Fuente sintetiza docs oficiales (code.claude.com, snapshot 2026-04). Refuerza claim 1 con granularidad.
**Confidence:** high

---

## 3. CUANDO una skill basta y CUANDO se necesita un sub-agente (arbol de decision)

**Claim:** Usar sub-agente solo si se cumplen los tres: tarea larga, contexto que se ensuciaria, y contrato input/output claro. Si no, escribir skill.
**Source:** AI Architects (Tom Crawshaw)
**URL:** https://theaiarchitects.com/blog/claude-code-subagents-vs-skills
**Date:** 2026-05-12
**Excerpt:** "Reach for a subagent only when you have all three: long-running work, dirty context, and a clear input/output contract. Code review, security audits, schema validation, repo-wide refactors, second-opinion bug rescues. Those are the jobs subagents earn their keep on."
**Context:** Regla practica. Tres senales -> sub-agente: (1) necesita su propia ventana de contexto, (2) podria correr en modelo mas barato, (3) necesita permisos de tools propios. La primera que da "si" gana.
**Confidence:** high

**Claim:** Una skill PUEDE reemplazar a un sub-agente para code review, pero pierdes el aislamiento de contexto; en diffs grandes la skill se come el contexto del padre.
**Source:** AI Architects (Tom Crawshaw)
**URL:** https://theaiarchitects.com/blog/claude-code-subagents-vs-skills
**Date:** 2026-05-12
**Excerpt:** "Can a skill replace a subagent for code review? It can, but you lose context isolation. A review skill loaded into the main agent will work for small diffs. On a large diff, it will eat the parent context and crowd out the conversation you started. Use a subagent for any review that touches more than a handful of files."
**Context:** Respuesta directa al "cuando reemplaza y cuando no" de dim03. Volumen de I/O es el umbral.
**Confidence:** high

**Claim:** Framework de decision por costo: pregunta primero si necesita data/efectos externos (-> MCP), luego comportamiento distinto (-> sub-agente), luego instrucciones reusables (-> skill); empieza por la opcion mas barata.
**Source:** systemprompt.io
**URL:** https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
**Date:** 2026-03-11
**Excerpt:** "The questions are ordered by cost. Skills cost minutes to create. Subagents cost a markdown file with frontmatter. MCP servers cost real engineering time. Start at the cheapest option and only escalate when necessary."
**Context:** Arbol completo en el articulo. Util para gobernanza: define orden de escalamiento.
**Confidence:** high

---

## 4. Paralelismo: el caso donde el sub-agente NO se puede reemplazar por skill

**Claim:** Claude Code lanza multiples sub-agentes en paralelo para tareas independientes; los sub-agentes paralelos no se ven entre si y hay que mergear sus reportes en el padre.
**Source:** AI Architects (Tom Crawshaw)
**URL:** https://theaiarchitects.com/blog/claude-code-subagents-vs-skills
**Date:** 2026-05-12
**Excerpt:** "Claude Code spawns multiple subagents in parallel for independent tasks. Fan out a review subagent across each package of a monorepo, each running in its own context, then aggregate. The constraint is that parallel subagents do not see each other, so you have to merge their reports in the parent agent."
**Context:** El paralelismo verdadero (fan-out con contextos aislados) es propio de sub-agentes. Una skill inline no paraleliza. Excepcion: skill con `context: fork` (ver seccion 6).
**Confidence:** high

**Claim:** Matriz de capacidades: skill es paralelizable SOLO via `context: fork`; el sub-agente lo es nativamente.
**Source:** alexop.dev (Alexander Opalic) — tabla adaptada de IndyDevDan
**URL:** https://alexop.dev/posts/understanding-claude-code-full-stack/
**Date:** 2025-11-09 (act. abril 2026)
**Excerpt:** "Parallelizable | Skill: Yes (context: fork) | MCP: No | Subagent: Yes | Trigger: Yes. Tool Permissions | Skill: Yes | MCP: No | Subagent: Yes."
**Context:** Nota: esta fila contradice levemente a systemprompt/AI Architects que dicen que la skill hereda tools; la diferencia es que con `context: fork` la skill corre en sub-agente y ahi si aplican permisos. La capacidad de tool-permissions de skill aplica solo cuando forkea.
**Confidence:** medium

---

## 5. Costo y overhead: tokens de skill vs MCP, y routing de modelo

**Claim:** Una skill cuesta ~30-50 tokens en metadata (scan) hasta que se activa; carga progresiva permite 100+ skills sin impacto de contexto. MCP carga todas las definiciones de tools al inicio (puede ser 50k+).
**Source:** Morph (Morph Team)
**URL:** https://www.morphllm.com/claude-code-skills-mcp-plugins
**Date:** 2026-01-23
**Excerpt:** "Skills use progressive disclosure to stay efficient: Metadata scan: Claude loads only names and descriptions (~30-50 tokens per skill)... This means you can have 100+ skills installed without impacting context." / "A five-server setup with 58 tools can use 55,000+ tokens before any conversation starts."
**Context:** Cuantifica el overhead base. Tabla del articulo: Skill base 30-50 tokens / loaded <5k; MCP 1-50k. Tool Search reduce overhead MCP ~85% (testing interno: accuracy 49%->74% en Opus 4).
**Confidence:** high

**Claim:** Routing a sub-agentes Haiku para tareas rutinarias puede reducir el costo de tokens hasta ~60% vs correr todo en Opus.
**Source:** systemprompt.io
**URL:** https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
**Date:** 2026-03-11
**Excerpt:** "We tracked our token usage over a month and found that 60% of Opus tokens were spent on tasks that Haiku could handle identically. That is money set on fire." / "Teams that route routine tasks like code review and documentation to Haiku subagents can reduce token costs by up to 60% compared to running everything on Opus."
**Context:** Cifra de un equipo de produccion (no benchmark formal). El mecanismo del ahorro es model routing, no la skill en si.
**Confidence:** high

**Claim:** El sub-agente NO ahorra tokens per se; cuesta lo mismo por token. Ahorra o gasta segun (a) modelo mas barato o (b) trabajo paralelo. Ambos casos ocurren.
**Source:** AI Architects (Tom Crawshaw)
**URL:** https://theaiarchitects.com/blog/claude-code-subagents-vs-skills
**Date:** 2026-05-12
**Excerpt:** "Subagents cost the same per token as any other Claude Code call... The reason people ask is that subagents can either burn more tokens (parallel work) or save tokens (cheaper models on mechanical work). Both happen."
**Context:** Matiz importante para el CEO: el ahorro NO es automatico al introducir sub-agentes; viene de pinear modelo barato y restringir tools para evitar spidering recursivo del repo.
**Confidence:** high

**Claim:** [NO VERIFICADO] Benchmark de arquitectura multi-agente: sub-agentes aislados usaron ~9K tokens totales para una query multi-dominio vs ~15K de un patron basado en skills que acumula contexto.
**Source:** Augment Code (via snippet de busqueda; pagina no recuperada en full-text)
**URL:** https://www.augmentcode.com/guides/ai-agent-loop-token-cost-context-constraints
**Date:** abril 2026 (segun snippet)
**Excerpt:** "isolated subagents used approximately 9K total tokens for a multi-domain query, compared to 15K tokens for a skills-based pattern that accumulates context."
**Context:** Cifra que matiza la intuicion: para queries MULTI-DOMINIO el aislamiento de sub-agentes gana en tokens vs skills que acumulan. Pero el mismo snippet advierte: el sub-agente da CERO amortizacion en queries repetidas similares (cada llamada resetea). No pude abrir la pagina para verificar contexto/metodologia. Tratar como indicativo.
**Confidence:** low

**Claim:** [NO VERIFICADO] Skills cortan uso de tokens 25-40% vs prompts monoliticos en tareas de code-gen.
**Source:** Newline.co (Dipen) — articulo no recuperable en full-text (devolvio cuerpo vacio)
**URL:** https://www.newline.co/@Dipen/claude-skills-and-subagents-reduce-prompt-bloat--f2920804
**Date:** 2026-03-09 (segun snippet)
**Excerpt:** "Skills cut token usage by 25-40% compared to monolithic prompts."
**Context:** Cifra de un solo articulo, no verificada en el cuerpo. Direccionalmente coherente con morphllm (progressive disclosure) pero la magnitud exacta no esta confirmada.
**Confidence:** low

---

## 6. context: fork — la skill que corre como sub-agente (frontera difuminada 2026)

**Claim:** Anadir `context: fork` a una skill la ejecuta en un sub-agente aislado en vez de inline; el cuerpo de la skill se vuelve la tarea del sub-agente, que NO recibe el historial de la conversacion principal.
**Source:** mehdi.cz (Mehdi Akiki)
**URL:** https://www.mehdi.cz/blog/claude-code-context-fork
**Date:** 2026-03-09
**Excerpt:** "When you add context: fork to a skill, the skill runs in an isolated subagent context instead of directly inside the current conversation. The skill content becomes the prompt for that subagent, and the subagent does not get your main conversation history."
**Context:** Este es el mecanismo 2026 que convierte el dilema "skill O sub-agente" en un continuo. Una skill con `context: fork` es operacionalmente un sub-agente definido en formato skill.
**Confidence:** high

**Claim:** El frontmatter de skill soporta `context: fork`, `agent` (tipo de sub-agente: Explore/Plan/general-purpose) y `model` (haiku/sonnet/opus) — combinando knowledge module con runtime aislado y modelo barato.
**Source:** alexop.dev (Alexander Opalic)
**URL:** https://alexop.dev/posts/understanding-claude-code-full-stack/
**Date:** 2025-11-09 (act. abril 2026)
**Excerpt:** "context | Set to fork to run in an isolated subagent context. agent | Subagent type when context: fork is set (Explore, Plan, general-purpose). model | Model override (haiku, sonnet, opus)." / "When invoked, this spawns a separate context window. Your main conversation stays clean."
**Context:** Confirma que skills y sub-agentes son el "modelo unificado de extensibilidad" en 2026 (commands+skills ya fusionados). El campo `context: fork` es la bisagra.
**Confidence:** high

**Claim:** `context: fork` solo tiene sentido en skills con instrucciones explicitas; si la skill es solo guidelines, el sub-agente recibe lineamientos sin tarea accionable y puede volver sin output util.
**Source:** mehdi.cz (Mehdi Akiki)
**URL:** https://www.mehdi.cz/blog/claude-code-context-fork
**Date:** 2026-03-09
**Excerpt:** "Anthropic warns about this directly: context: fork only makes sense for skills with explicit instructions. If the skill is just general guidance, the subagent gets guidelines but no actionable task and may return without meaningful output."
**Context:** Anti-patron clave. Tambien: no forkear trabajo pequeno ("the isolation overhead is not worth it"); no esperar que el fork vea la conversacion completa.
**Confidence:** high

---

## 7. Patron compuesto: sub-agente Haiku + skill precargada + MCP scoped (el default 2026)

**Claim:** El default 2026 es componer las tres capas: un sub-agente en Haiku, con una skill precargada para convenciones y un MCP scoped para data en vivo, es el patron que se paga solo.
**Source:** systemprompt.io
**URL:** https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
**Date:** 2026-03-11
**Excerpt:** "In 2026, the default answer is compose all three. A subagent on Haiku, with a preloaded skill for conventions and a scoped MCP server for live data, is the pattern that actually pays for itself."
**Context:** Coincide EXACTAMENTE con el "patron compuesto" pedido en dim03. Es la recomendacion central para el CEO.
**Confidence:** high

**Claim:** Ejemplo concreto de composicion: un sub-agente que precarga skill via campo `skills:` y restringe tools/modelo/MCP en YAML.
**Source:** systemprompt.io
**URL:** https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
**Date:** 2026-03-11
**Excerpt:** "model: haiku / tools: Read, Grep, Glob, Bash / disallowedTools: Write, Edit / mcpServers: - github / skills: - review ... The skills: - review field loads the review skill into the subagent's context, so it follows your team's exact review conventions. Isolated context. The subagent runs in its own context window."
**Context:** El campo `skills:` en el frontmatter del sub-agente es el mecanismo de precarga. La skill se inyecta en el system prompt del sub-agente, no del padre. Frontmatter completo del sub-agente incluye: model, tools, disallowedTools, mcpServers, skills, permissionMode, maxTurns, background, isolation (worktree), hooks, memory.
**Confidence:** high

**Claim:** Un sub-agente puede llamar a una skill; la skill carga DENTRO del contexto del sub-agente, no del padre. "Sub-agente para aislamiento de contexto, skill para las instrucciones reusables adentro."
**Source:** AI Architects (Tom Crawshaw)
**URL:** https://theaiarchitects.com/blog/claude-code-subagents-vs-skills
**Date:** 2026-05-12
**Excerpt:** "A subagent runs on the same Claude Code runtime as the parent, so it can see and load skills from the same folders... The skill loads inside the subagent's context window, not the parent's. That is the most useful pattern in this whole post: subagent for context isolation, skill for the reusable instructions inside it."
**Context:** Segunda fuente independiente confirmando el patron compuesto. Convergencia fuerte entre systemprompt y AI Architects.
**Confidence:** high

---

## 8. Modelo: Haiku como worker, planner Opus/Sonnet (fan-out)

**Claim:** El patron de produccion dominante es el sub-agente como worker: decenas/cientos de workers Haiku abanican desde un planner Opus o Sonnet; el planner descompone, dispara en paralelo y recompone. Da calidad de razonamiento clase-Opus a costo/latencia casi clase-Haiku.
**Source:** CallSphere
**URL:** https://callsphere.ai/blog/td30-anth-haiku45-subagent
**Date:** 2026-04-09 (mod. 2026-06-01)
**Excerpt:** "The most powerful production pattern with Haiku 4.5 is the sub-agent: dozens or hundreds of Haiku workers fan out from a single Opus or Sonnet planner. The planner decomposes the task, dispatches it to Haiku workers in parallel, and recomposes the results. This pattern delivers Opus-class reasoning quality at near-Haiku-class cost and latency."
**Context:** Para una plataforma multi-tenant en produccion, este es el patron de escalamiento. Latencia: Haiku cabe en presupuesto de voz (~200-400ms para el LLM dentro de ~800ms end-to-end); Sonnet/Opus no. Sub-agente es el primitivo correcto aqui, no skill.
**Confidence:** medium

**Claim:** Pinear modelo en frontmatter: haiku para trabajo mecanico, sonnet para juicio, opus rara vez al nivel de sub-agente porque el costo se apila rapido.
**Source:** AI Architects (Tom Crawshaw)
**URL:** https://theaiarchitects.com/blog/claude-code-subagents-vs-skills
**Date:** 2026-05-12
**Excerpt:** "model. Either sonnet, haiku, opus, or inherit. Default is inherit. Pin to haiku for mechanical work. Pin to sonnet for anything requiring judgment. Opus rarely makes sense at the subagent level because the cost stacks fast."
**Context:** Guia practica de routing por modelo. Refuerza que la skill NO puede elegir modelo (hereda el del padre); solo el sub-agente.
**Confidence:** high

---

## 9. Aislamiento de tools y seguridad (relevante multi-tenant)

**Claim:** El valor del sub-agente viene de las RESTRICCIONES: `disallowedTools: Write, Edit` significa que el sub-agente fisicamente no puede modificar archivos, read-only por diseno no por convencion. `mcpServers: - github` lo limita a UN servidor; el resto es invisible.
**Source:** systemprompt.io
**URL:** https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
**Date:** 2026-03-11
**Excerpt:** "The disallowedTools: Write, Edit field means this subagent literally cannot modify files. It reads, analyses, and reports. Read-only by design, not by convention. The mcpServers: - github field gives the subagent access to the GitHub MCP server but nothing else. Your database, your deployment pipeline, your internal APIs are all invisible to this subagent."
**Context:** CRITICO para multi-tenant: el scoping de tools/MCP por sub-agente es el mecanismo de aislamiento de permisos. Una skill NO puede hacer esto (hereda tools del padre). Anti-patron: dar al sub-agente Opus y todos los tools -> es solo otra sesion main.
**Confidence:** high

**Claim:** [NO VERIFICADO] Las Agent Skills pueden forkear sub-agentes GOBERNADOS (gobernanza/aprobaciones) en Claude Code 2.1, pasando de "approval hell" a ejecucion autonoma controlada.
**Source:** Rick Hightower / Spillwave (Medium) — articulo no recuperable en full-text (cuerpo vacio)
**URL:** https://medium.com/@richardhightower/from-approval-hell-to-just-do-it-how-agent-skills-fork-governed-sub-agents-in-claude-code-2-1-c0438416433a
**Date:** feb. 2026 (segun listado de busqueda)
**Excerpt:** [no recuperable — solo titulo: "From Approval Hell to Just Do It: How Agent Skills Fork Governed Sub-Agents in Claude Code 2.1"]
**Context:** El angulo de gobernanza (skills que forkean sub-agentes con permisos pre-aprobados) es directamente relevante a una plataforma multi-tenant con RLS/scoping. NO pude verificar el cuerpo; solo el titulo confirma que el patron "skill forkea sub-agente gobernado" existe como tema en Medium feb-2026. Verificar antes de citar cifras.
**Confidence:** low

---

## 10. Anti-patrones de migracion (skill <-> sub-agente)

**Claim:** Empieza con skills (son gratis), luego sub-agentes (baratos), luego MCP (necesarios). No construir las tres a la vez; cada capa prueba su valor antes de anadir la siguiente.
**Source:** systemprompt.io
**URL:** https://systemprompt.io/guides/claude-skills-vs-agents-vs-mcp
**Date:** 2026-03-11
**Excerpt:** "The key principle is to start with skills because they are free. Then add subagents because they are cheap. Then add MCP servers because they are necessary. Do not build all three at once. Each layer should prove its value before you add the next."
**Context:** Path de migracion de 4 semanas. Anti-patron inverso: construir un MCP server de 400 lineas TypeScript que debio ser una skill de 15 lineas markdown.
**Confidence:** high

**Claim:** La mayoria de slash commands viejos mapean a skills, NO a sub-agentes. Promover a sub-agente solo si pega uno de los tres triggers (long-running, dirty context, restricted tools).
**Source:** AI Architects (Tom Crawshaw)
**URL:** https://theaiarchitects.com/blog/claude-code-subagents-vs-skills
**Date:** 2026-05-12
**Excerpt:** "Most slash commands map cleanly to skills, not subagents. The /commands folder was Anthropic's first version of reusable workflows. Skills are the second generation, with better triggering and packaging. Migrate to skills first. Promote to a subagent only if you hit one of the three subagent triggers."
**Context:** Guia de migracion. Convergente con systemprompt: skill es el default, sub-agente es la excepcion justificada.
**Confidence:** high

---

## Sintesis para el CEO (multi-tenant)

1. **No es "reemplazo", es capas.** Skill = conocimiento inyectado (mismo contexto, mismo modelo, mismos tools). Sub-agente = runtime aislado (su contexto, su modelo, sus tools). En multi-tenant el eje decisivo es **permisos de tools/MCP scoped** — solo el sub-agente lo da; la skill hereda todo del padre. (systemprompt, AI Architects — high)

2. **Skill basta cuando:** trabajo corto, mismo modelo, necesita contexto del padre, instrucciones reusables/convenciones. **Sub-agente cuando:** los tres juntos (largo + ensuciaria contexto + contrato I/O claro), o paralelismo real, o modelo mas barato, o tools restringidos por seguridad. (AI Architects — high)

3. **`context: fork` difumina la frontera** (2026): una skill con `context: fork` + `agent` + `model` ES operacionalmente un sub-agente escrito como skill. La eleccion ya no es binaria. (mehdi.cz, alexop.dev — high)

4. **Patron compuesto = default 2026:** sub-agente Haiku + skill precargada (campo `skills:`) + MCP scoped. Da scope de acceso, scope de costo y scope de proposito. Dos fuentes independientes convergen. (systemprompt, AI Architects — high)

5. **Costo:** el ahorro NO es automatico. Viene de routing a Haiku (~60% del gasto Opus es rutinario) y de restringir tools. Skills bajan overhead base por progressive disclosure (~30-50 tokens/skill latente). Las cifras finas (9K vs 15K; 25-40%) son de fuentes unicas no verificadas en cuerpo — usar como indicativas. (morphllm, systemprompt — high; Augment, Newline — low)

**Cobertura de fuentes:** 12 bloques con cita verbatim de paginas recuperadas en full-text (systemprompt, AI Architects, morphllm, alexop.dev, mehdi.cz, callsphere) + 3 bloques [NO VERIFICADO] de snippets (Augment Code, Newline/Dipen, Rick Hightower/Medium). Medium bloqueo todos los fetches server-side; las 3 afirmaciones Medium/Newline/Augment estan marcadas low y requieren verificacion manual antes de citar cifras.
