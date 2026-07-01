# AGENT SKILLS dim04 — Skills + Memoria + Context Engineering (junio 2026)

Investigacion sobre como el patron SKILL.md interactua con la memoria persistente del agente, el budget de contexto y la KV-cache. Hallazgo central: las skills son una implementacion de "progressive disclosure" que mantiene la metadata estatica y cacheable mientras carga el body on-demand; mal gestionadas (skill bloat, inyeccion dinamica en el prefijo) destruyen el prefix-cache y degradan rendimiento hasta un orden de magnitud. Audiencia: CEO plataforma agentes multi-tenant en produccion. Fuente primaria Medium + complemento oficial Anthropic.

---

## A. Skills, budget de contexto y carga progresiva

### Claim 1 — Las skills mueven la disciplina de "prompt engineering" estatico a "dynamic context engineering"
- Source: Medium (Google Cloud Community) — Neelam Pawar, "Agent Skills-Dynamic Context Engineering"
- URL: https://medium.com/google-cloud/agent-skills-dynamic-context-engineering-c1bebf028cf7
- Date: 2026-04-07 (meta-article:published_time 2026-04-07T02:18:07Z)
- Excerpt: "The biggest hidden tax in AI development isn't just the API subscription - it's 'Context Inflation.' ... By treating capabilities as a lightweight, open-format filesystem, we move away from static prompt engineering and toward dynamic context engineering. Instead of paying for a 32k token window full of 'just in case' instructions, an agent can now 'discover' the specific skill folder ... only when required."
- Context: Framing economico de la disciplina. Util como narrativa para un CEO: el coste no es la suscripcion, es el contexto inflado.
- Confidence: high

### Claim 2 — Sistema de carga en tres niveles: la metadata siempre cargada cuesta ~100 tokens por skill
- Source: Medium (Google Cloud Community) — Neelam Pawar
- URL: https://medium.com/google-cloud/agent-skills-dynamic-context-engineering-c1bebf028cf7
- Date: 2026-04-07
- Excerpt: "Agents use a three-tier loading system for skills that keeps context costs proportional to what the agent uses, not what it has installed. ... Level 1: Metadata (always loaded, ~100 tokens per skill) ... Agent loads this metadata at startup and includes it in the system prompt. ... Level 2: Instructions (loaded when triggered, under 5,000 tokens) ... Level 3: Resources and code (loaded as needed)."
- Context: Define el modelo de costes por nivel. La cifra ~100 tokens es del autor (estimacion redonda); ver Claim 4 para una medicion mas granular.
- Confidence: high

### Claim 3 — Medicion empirica: la metadata (Layer 1) tiene mediana ~80 tokens/skill; 17 skills oficiales caben en ~1,700 tokens
- Source: Medium/Substack (SwirlAI Newsletter) — Aurimas Griciunas, "Agent Skills: Progressive Disclosure as a System Design Pattern"
- URL: https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
- Date: 2026-03-11 (meta-article:modified_time 2026-03-11T10:39:36Z)
- Excerpt: "I measured this across Anthropic's 17 official skills: the median discovery cost is ~80 tokens per skill, ranging from ~55 (webapp-testing) to ~235 (xlsx). All 17 skills together cost ~1,700 tokens, meaning an agent can be aware of dozens of skills for less context than a single activated skill."
- Context: Medicion del autor (no auditada por terceros) pero concreta y consistente con la cifra redonda de Pawar. El punto clave para multi-tenant: el catalogo de discovery es barato; lo caro es la activacion.
- Confidence: medium

### Claim 4 — El body activado (Layer 2) va de ~275 a ~8,000 tokens, mediana ~2,000; la decision de activar es puro razonamiento del LLM sobre las descripciones
- Source: Medium/Substack (SwirlAI Newsletter) — Aurimas Griciunas
- URL: https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
- Date: 2026-03-11
- Excerpt: "body size ranges from ~275 tokens (internal-comms) to ~8,000 tokens (skill-creator), with a median around 2,000. The platform makes this decision using LLM reasoning over the descriptions from the discovery layer. Research shows that Claude selects skills through pure reasoning, with description quality directly determining routing accuracy."
- Context: Implicacion de gobernanza: la calidad de la `description` determina el routing. En multi-tenant, descripciones mal escritas activan skills equivocadas y queman budget.
- Confidence: medium

### Claim 5 — La metadata (name + description) se pre-carga en el system prompt al arranque; el body se lee solo si la skill es relevante (definicion oficial de progressive disclosure)
- Source: Oficial — Anthropic Engineering, "Equipping agents for the real world with Agent Skills"
- URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Date: 2025-10-16 (Published Oct 16, 2025; seminal, anterior al estandar abierto del 18-dic-2025)
- Excerpt: "At startup, the agent pre-loads the name and description of every installed skill into its system prompt. This metadata is the first level of progressive disclosure ... If Claude thinks the skill is relevant to the current task, it will load the skill by reading its full SKILL.md into context."
- Context: Fuente canonica del mecanismo. Confirma que la metadata vive en el system prompt (zona estatica, cacheable) y el body entra via lectura on-demand.
- Confidence: high

---

## B. Orden de inyeccion y KV-cache (lo que rompe o preserva el cache)

### Claim 6 — Jerarquia de invalidacion de cache: tools -> system -> CLAUDE.md/skills -> messages; lo mas a la izquierda debe ser lo mas estable
- Source: Medium-style blog (KnightLi) — "Claude Code Token-Saving Guide: How Models, MCP, CLAUDE.md, and Skills Affect Cache"
- URL: https://knightli.com/en/2026/05/18/claude-code-prompt-cache-token-optimization/
- Date: 2026-05-18 (meta-article:published_time 2026-05-18)
- Excerpt: "tools -> system -> CLAUDE.md / skills -> messages ... The farther left something sits, the more stable it should be and the larger the cache benefit. If a left-side section changes, everything after it may need to be recalculated. ... Anthropic's documentation summarizes the invalidation hierarchy as tools -> system -> messages."
- Context: Mapa operativo directo. Las skills se sientan entre system y messages; cambiarlas a mitad de tarea invalida los messages posteriores.
- Confidence: high

### Claim 7 — Instalar o actualizar skills a mitad de tarea es "cache killer": rompe el prefix y obliga a recomputar
- Source: Medium-style blog (KnightLi)
- URL: https://knightli.com/en/2026/05/18/claude-code-prompt-cache-token-optimization/
- Date: 2026-05-18
- Excerpt: "Cache killer 4: installing or updating Skills mid-task. Skills are also part of the context. Installing a new Skill, updating a Skill, or changing the Skill list changes what gets injected into the session. These changes often do not fully take effect until reload, resume, or a new session. Once messages are rebuilt, old cache entries may no longer match. ... Keep the Skill set stable for the same kind of task."
- Context: Regla de oro para produccion: configurar el set de skills ANTES de empezar la tarea; tratar cualquier instalacion nueva como inicio de una fase nueva. Para multi-tenant: cambios de skills per-tenant deben anclarse al inicio de sesion.
- Confidence: high

### Claim 8 — La metadata de skills es contenido estatico cacheable; el body cargado on-demand SE APPENDEA (no reescribe el prefijo), por lo que no invalida el cache del system prompt
- Source: Oficial — Anthropic Engineering (mecanismo) + KnightLi (jerarquia)
- URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Date: 2025-10-16
- Excerpt: "1. To start, the context window has the core system prompt and the metadata for each of the installed skills ... 2. Claude triggers the PDF skill by invoking a Bash tool to read the contents of pdf/SKILL.md; 3. Claude chooses to read the forms.md file ... 4. Finally, Claude proceeds with the user's task now that it has loaded relevant instructions."
- Context: [INFERENCIA RAZONADA, NO AFIRMACION LITERAL DE LA FUENTE] La secuencia oficial muestra que el body entra como resultado de un tool-call Bash anhadido al final de la conversacion (zona messages), NO modificando el system prompt. Por tanto la activacion de una skill consume tokens nuevos pero NO invalida el prefijo estable. Combinado con Claim 6, esto explica por que la metadata es cacheable y la activacion es "barata en cache" aunque cueste tokens. La fuente no lo afirma textualmente con estas palabras.
- Confidence: medium

### Claim 9 — Mantener prefijo estable puede dar >10x de mejora; NO poner timestamps cambiantes al inicio del system prompt o se invalida todo el cache
- Source: Medium — Baixin Guo (Max), "Agent Skills for Context Engineering Are Here" (analizando el repo Agent-Skills-for-Context-Engineering)
- URL: https://medium.com/@gbx1220max/agent-skills-for-context-engineering-are-here-ready-for-claude-code-codex-garnering-2-3k-00d720ec55bd
- Date: 2025-12-29 (Dec 29, 2025)
- Excerpt: "KV-Cache Hit Rate Optimization ... optimizing KV-Cache hit rate can bring more than 10x performance improvement: Maintain Prefix Stability: System prompts and tool definitions should be placed at the front and remain unchanged. Avoid Dynamic Interference: Do not place constantly changing 'current timestamps' at the beginning of system prompts - this will invalidate all caches instantly."
- Context: Regla concreta que aplica directamente al diseno de skills/system prompts multi-tenant. La cifra >10x es del autor.
- Confidence: medium

### Claim 10 — El prefix-cache se empareja por secuencia desde el token 0; un solo caracter distinto en un system prompt de 5,000 tokens fuerza recomputar los 5,000
- Source: Research blog (ThinkSmart.Life) — "KV Cache in Local AI: Why Your Agentic Setup is 90% Slower Than It Should Be"
- URL: https://thinksmart.life/research/posts/kv-cache-local-inference/
- Date: 2026-03-12 (March 12, 2026)
- Excerpt: "Any change to the beginning of the context invalidates the entire prefix cache from that point forward. A single character difference in a 5,000-token system prompt means the model recomputes all 5,000 tokens, even if only one token changed."
- Context: Fundamento tecnico que justifica por que el orden de inyeccion de skills importa. Aplica a cualquier backend con prefix caching.
- Confidence: high

---

## C. Context windows pequenos / modelos locales

### Claim 11 — Los sistemas agenticos son los que MAS se benefician del KV-cache (prefijo estable largo) y por tanto los que MAS sufren al invalidarlo; en sesiones largas el slowdown es de orden de magnitud (~50x en el ejemplo)
- Source: Research blog (ThinkSmart.Life)
- URL: https://thinksmart.life/research/posts/kv-cache-local-inference/
- Date: 2026-03-12
- Excerpt: "agentic AI is the use case most suited to benefit from KV cache reuse - and therefore the use case that suffers most when that cache is invalidated. ... With working KV cache ~200 tokens recomputed/turn ~2.2s; Cache invalidated every turn ~10,000 tokens ~111 seconds; Slowdown factor ~50x."
- Context: El ejemplo usa Qwen3.5-35B-A3B en RTX 3090, 10k tokens, turno 50. Relevante para despliegues locales/edge con context windows pequenos donde el coste de recomputar es prohibitivo. Cita el bug de Claude Code (header de atribucion cambiante) reportado por Unsloth como caso real de 90% slowdown.
- Confidence: high

### Claim 12 — Mejor practica <20 tools (precision cae despues de 10); el mismo principio aplica a las skills/instrucciones cargadas a la vez
- Source: Medium/Substack (SwirlAI Newsletter) — Aurimas Griciunas
- URL: https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
- Date: 2026-03-11
- Excerpt: "Best practice recommends fewer than 20 tools available to an agent at once, with accuracy degrading past 10. The same principle applies to instructions. ... Connect a few MCP servers without managing what loads, and you quickly reach 90+ tool definitions, over 50,000 tokens of JSON schemas before the model even starts reasoning."
- Context: Limite practico para multi-tenant: el catalogo per-tenant de skills/tools activas debe podarse. Conecta con el anti-patron de la seccion D.
- Confidence: medium

### Claim 13 — "Lost-in-the-middle": un context window mas grande NO elimina la dilucion de atencion; la recall en el medio es 10-40% menor que en los extremos
- Source: Medium — Baixin Guo (Max) [cifra 10-40%]; corroborado por MindStudio
- URL: https://medium.com/@gbx1220max/agent-skills-for-context-engineering-are-here-ready-for-claude-code-codex-garnering-2-3k-00d720ec55bd
- Date: 2025-12-29
- Excerpt: "Lost-in-the-Middle ... Data Support: Research shows that when information is placed in the middle, recall accuracy can be 10-40% lower than when placed at both ends. ... Always place the most important constraints at the beginning and the most urgent current task objectives at the end."
- Context: Justifica que skills lean importan incluso con ventanas de 200K. MindStudio lo confirma: "Larger context windows ... don't eliminate the attention dilution problem ... A bloated skill file still degrades performance even when it's well within the token limit" (https://www.mindstudio.ai/blog/context-rot-claude-code-skills-bloated-files, 2026-03-24).
- Confidence: medium

---

## D. Anti-patron: skill bloat / inflado del catalogo de metadata

### Claim 14 — "Context tax": skill media ~1,900 tokens pero distribucion de cola pesada; el top 1% supera 100,000 tokens y una sola skill no optimizada puede consumir todo el budget
- Source: HuggingFace blog (Shanshan Zhong) sobre el paper "Agent Skills: A Data-Driven Analysis of Claude Skills" (40,000 skills auditadas de skills.sh)
- URL: https://huggingface.co/blog/zhongshsh/agent-skills-analysis
- Date: 2026-02-16 (Published February 16, 2026)
- Excerpt: "While the average skill is a manageable 1,900 tokens, the distribution is heavy-tailed. The top 1% of skills exceed 100,000 tokens. Because agents often load these skill definitions into their context window before execution, installing a single unoptimized skill can consume a model's entire memory budget, leaving no room for the actual task."
- Context: Dato cuantitativo fuerte para gobernanza multi-tenant: imponer limite de tokens por skill antes de admitirla al catalogo. Basado en auditoria de 40,000 skills.
- Confidence: high

### Claim 15 — Mercado inundado: 46.3% de skills son duplicados/casi-duplicados; crecimiento 18.5x en 20 dias (ene-feb 2026) ligado al hype; crea una "discovery tax"
- Source: HuggingFace blog (Shanshan Zhong) sobre el mismo paper
- URL: https://huggingface.co/blog/zhongshsh/agent-skills-analysis
- Date: 2026-02-16
- Excerpt: "The researchers tracked the marketplace's growth ... observing a staggering 18.5x increase in listed skills in just 20 days. ... The study found that 46.3% of all skills are duplicates or near-duplicates. ... This redundancy creates a 'discovery tax' for users."
- Context: El bloat no es solo por archivo grande, tambien por catalogo redundante que infla la metadata de discovery y degrada el routing. Implicacion: curacion de "canonical skills" per-tenant.
- Confidence: high

### Claim 16 — "Context rot": archivos de skill que solo crecen producen dilucion de atencion, conflictos de instrucciones y compresion del budget; el conteo total de tokens es lo que importa, no el numero de archivos
- Source: Medium-style blog (MindStudio Team) — "What Is Context Rot in Claude Code Skills?"
- URL: https://www.mindstudio.ai/blog/context-rot-claude-code-skills-bloated-files
- Date: 2026-03-24 (March 24, 2026)
- Excerpt: "Context rot ... a gradual degradation in agent performance caused by skill files that have grown too large ... A 500-token CLAUDE.md costs you 500 tokens on every single inference. A 12,000-token skill file costs 12,000 tokens - every time. ... The solution to context rot isn't to split one large file into many smaller files that all get loaded at startup - the total token count is what matters, not the file count."
- Context: Matiz importante: dividir un archivo grande en muchos que igual se cargan al arranque NO ayuda. Recomienda limite ~2,000 tokens/archivo, "write the delta not the manual", scoping por subdirectorio.
- Confidence: high

---

## E. Skills + memoria persistente cross-session

### Claim 17 — La ventana de contexto es memoria de trabajo activa; usarla para hechos a largo plazo o constraints duros produce modos de fallo. Consenso 2025-2026: jerarquia de tres niveles
- Source: WebSearch (sintesis de Medium y mem0.ai) — multiples articulos abril 2026
- URL: https://mem0.ai/blog/context-window-is-ram-not-storage-why-most-agent-failures-happen-how-to-fix-them-in-2026
- Date: 2026 (articulos abril 2026; fecha exacta no verificada por fetch directo)
- Excerpt: "The context window is good at holding the active working state of the current task, but using it for long-term facts, cross-session preferences, or hard constraints produces failure modes. ... The production consensus in 2025-2026 is a three-tier hierarchy: in-context working memory for the current session, session-scoped compressed memory with summarized facts, and long-term persistent store with cross-session knowledge in vector+graph storage." [NO VERIFICADO — extracto via snippet de WebSearch, no via fetch directo del articulo completo]
- Context: Distingue skills (procedural knowledge cargado on-demand) de memoria (estado/hechos persistentes cross-session). Las skills NO son el mecanismo de memoria; coexisten. Confidence baja porque no se hizo fetch directo de cada articulo.
- Confidence: low

### Claim 18 — Las skills pueden complementar a la memoria via "anchored iterative summarization": un bloque de estado estructurado que el agente relee tras un reset de contexto
- Source: Medium — Baixin Guo (Max)
- URL: https://medium.com/@gbx1220max/agent-skills-for-context-engineering-are-here-ready-for-claude-code-codex-garnering-2-3k-00d720ec55bd
- Date: 2025-12-29
- Excerpt: "Anchored Iterative Summarization ... maintain a structured state block: Session Intent ... Files Modified ... Decisions Made ... Current State ... Next Steps ... When the context resets, the Agent reads this snapshot instead of vague memories. ... the file system as state machine ... the program can be interrupted at any time and automatically resume after restarting, without wasting any tokens."
- Context: Patron clave: usar el filesystem (donde viven las skills) como memoria/checkpoint persistente. Conecta skills con continuidad cross-session sin inflar el contexto. Tambien describe "observation masking" (reemplazar tool outputs verbosos por referencias, -90% volumen de contexto).
- Confidence: medium

### Claim 19 — Anthropic anticipa que los agentes podran crear/editar/evaluar sus propias skills, codificando sus patrones en capacidades reutilizables (memoria procedimental auto-generada)
- Source: Oficial — Anthropic Engineering
- URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Date: 2025-10-16
- Excerpt: "Looking further ahead, we hope to enable agents to create, edit, and evaluate Skills on their own, letting them codify their own patterns of behavior into reusable capabilities."
- Context: Vision oficial de skills como memoria procedimental persistente y auto-evolutiva. Relevante para el roadmap de una plataforma multi-tenant que quiera que los agentes aprendan workflows per-tenant.
- Confidence: high

---

## Notas de verificacion
- Claims 1-2, 5-16, 18-19: extractos verificados por fetch directo de la pagina (texto citado presente en el HTML recuperado).
- Claim 3-4: medicion del autor SwirlAI (no auditada por terceros) — confidence medium.
- Claim 8: INFERENCIA razonada combinando dos fuentes; la fuente oficial no lo afirma con estas palabras literales — confidence medium, marcado explicitamente.
- Claim 13: cifra 10-40% atribuida a "research" por el autor de Medium, no a un paper nombrado — confidence medium.
- Claim 17: [NO VERIFICADO] — unico bloque cuyo extracto viene de snippet de WebSearch sin fetch directo del articulo completo — confidence low.
- La fuente oficial Anthropic (Claim 5, 8, 19) esta fechada 2025-10-16, anterior al estandar abierto Agent Skills (18-dic-2025); se incluye por ser el documento seminal del mecanismo.
- NO se inventaron URLs, cifras ni citas. Todas las cifras (80/1,700/1,900/100,000 tokens, 46.3%, 18.5x, 50x, 90%, 10-40%) provienen literalmente de los extractos citados.
