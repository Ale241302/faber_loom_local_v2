# Agent Skills (dim07): Como construir y evaluar Skills propias — junio 2026

Investigacion sobre el flujo skill-creator de Anthropic, autoria de SKILL.md, evals/benchmarking, metricas de triggering y anti-patrones. La fuente primaria mas fuerte es el propio `SKILL.md` de skill-creator (anthropics/skills, 485 lineas) que codifica el flujo canonico draft -> test -> review -> improve -> benchmark, con optimizacion de descripcion por loop train/test. Lo complementan articulos Medium (mar-abr 2026) sobre evals rigurosos, el patron SKILL.md y la actualizacion Skill Creator 2.0. Para un CEO de plataforma multi-tenant, el punto clave: una skill es infraestructura versionada que debe tener evals propias, descripcion optimizada para triggering, y un "impuesto de contexto" que justificar antes de cargar por defecto.

---

## 1. Que es y que hace skill-creator

**Claim:** skill-creator es una skill de Anthropic que crea skills nuevas, mejora existentes y mide su performance con evals y analisis de varianza.
**Source:** anthropics/skills — skill-creator SKILL.md (frontmatter)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026 (repo activo; archivo 485 lineas / 32.4 KB)
**Excerpt:** "Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy."
**Context:** Es la description oficial de la propia skill — define su alcance: creacion, edicion, evals y optimizacion de triggering.
**Confidence:** high

## 2. Flujo canonico de creacion (el loop)

**Claim:** El flujo es un loop iterativo: decidir intent -> draft -> test prompts -> evaluar (cualitativo + cuantitativo) -> reescribir -> repetir -> expandir el test set a mayor escala.
**Source:** anthropics/skills — skill-creator SKILL.md
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "Decide what you want the skill to do and roughly how it should do it / Write a draft of the skill / Create a few test prompts and run claude-with-access-to-the-skill on them / Help the user evaluate the results both qualitatively and quantitatively / Rewrite the skill based on feedback ... / Repeat until you're satisfied / Expand the test set and try again at larger scale"
**Context:** El loop es identico para crear desde cero o mejorar una skill existente (en ese caso se salta directo a eval/iterate).
**Confidence:** high

## 3. Captura de intent: 4 preguntas y la decision test-cases si/no

**Claim:** El arranque captura intent con 4 preguntas (que habilita, cuando dispara, formato de output, si conviene test cases). Skills con output verificable se benefician de test cases; los de output subjetivo (estilo, arte) a menudo no.
**Source:** anthropics/skills — skill-creator SKILL.md (Capture Intent)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them."
**Context:** Decision arquitectonica temprana: no toda skill necesita harness cuantitativo; el tipo de output lo determina.
**Confidence:** high

## 4. Progressive disclosure: tres niveles de carga

**Claim:** Las skills cargan en 3 niveles: metadata (name+description, ~100 palabras, siempre en contexto); cuerpo de SKILL.md (al disparar, ideal <500 lineas); recursos bundled (bajo demanda, ilimitado, scripts ejecutan sin cargar al contexto).
**Source:** anthropics/skills — skill-creator SKILL.md (Progressive Disclosure)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "Metadata (name + description) - Always in context (~100 words) / SKILL.md body - In context whenever skill triggers (<500 lines ideal) / Bundled resources - As needed (unlimited, scripts can execute without loading)"
**Context:** Base del modelo de costo de contexto. El cuerpo solo entra al disparar; los recursos pesados solo cuando se referencian.
**Confidence:** high

## 5. La description es el mecanismo de triggering — y conviene ser "pushy"

**Claim:** La description es el mecanismo primario que decide si Claude invoca la skill; toda la info de "cuando usar" va ahi, no en el cuerpo. Claude tiende a "subdisparar" (no usar skills cuando serian utiles), por lo que se recomienda descripciones algo "pushy".
**Source:** anthropics/skills — skill-creator SKILL.md (Write the SKILL.md)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "currently Claude has a tendency to 'undertrigger' skills -- to not use them when they'd be useful. To combat this, please make the skill descriptions a little bit 'pushy'. So for instance, instead of 'How to build a simple fast dashboard...', you might write '...Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics ... even if they don't explicitly ask for a \"dashboard.\"'"
**Context:** Contradice la intuicion de descripciones neutrales; la subactivacion es el fallo dominante y se compensa con cobertura de frases.
**Confidence:** high

## 6. Como funciona el triggering: skills solo para tareas no triviales

**Claim:** Claude solo consulta skills para tareas que no resuelve facilmente solo; queries simples de un paso ("read this PDF") pueden no disparar la skill aunque la description matchee perfecto.
**Source:** anthropics/skills — skill-creator SKILL.md (How skill triggering works)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "Claude only consults skills for tasks it can't easily handle on its own — simple, one-step queries like 'read this PDF' may not trigger a skill even if the description matches perfectly ... Complex, multi-step, or specialized queries reliably trigger skills when the description matches."
**Context:** Implicacion para evals: las queries de prueba deben ser sustanciales; queries triviales son malos test cases.
**Confidence:** high

## 7. Test cases: evals.json, prompts primero, assertions despues

**Claim:** Tras el draft se escriben 2-3 prompts realistas, se guardan en `evals/evals.json` SIN assertions todavia; las assertions se redactan en el siguiente paso mientras corren los runs.
**Source:** anthropics/skills — skill-creator SKILL.md (Test Cases)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. ... Save test cases to evals/evals.json. Don't write assertions yet — just the prompts. You'll draft assertions in the next step while the runs are in progress."
**Context:** Separa generacion de prompts de la definicion de criterios, aprovechando el tiempo de ejecucion en paralelo.
**Confidence:** high

## 8. Comparacion with-skill vs baseline en paralelo

**Claim:** Por cada test case se lanzan dos subagentes en el mismo turno: uno con la skill y uno baseline. Para skill nueva el baseline es sin skill; para mejora de skill existente el baseline es la version vieja (snapshot).
**Source:** anthropics/skills — skill-creator SKILL.md (Step 1: Spawn all runs)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "For each test case, spawn two subagents in the same turn — one with the skill, one without. ... Creating a new skill: no skill at all. ... Improving an existing skill: the old version. Before editing, snapshot the skill (cp -r <skill-path> <workspace>/skill-snapshot/), then point the baseline subagent at the snapshot."
**Context:** El A/B contra baseline es lo que convierte "vibe check" en medicion de uplift real de la skill.
**Confidence:** high

## 9. Benchmark cuantitativo: pass_rate, tiempo, tokens con mean +/- stddev

**Claim:** La agregacion produce `benchmark.json`/`benchmark.md` con pass_rate, tiempo y tokens por configuracion, con media +/- desviacion estandar y el delta. Un "analyst pass" busca assertions no discriminantes, evals de alta varianza (flaky) y tradeoffs tiempo/tokens.
**Source:** anthropics/skills — skill-creator SKILL.md (Step 4)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "This produces benchmark.json and benchmark.md with pass_rate, time, and tokens for each configuration, with mean +/- stddev and the delta. ... surface patterns the aggregate stats might hide ... things like assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), and time/token tradeoffs."
**Context:** Las tres metricas de calidad — precision (pass_rate), consistencia (stddev/varianza) y eficiencia (tokens) — son las mismas que pide la audiencia.
**Confidence:** high

## 10. Optimizacion de description: loop train/test 60/40 con 3 corridas por query

**Claim:** El optimizador de description genera 20 queries (mix should-trigger / should-not-trigger), divide 60% train / 40% held-out test, evalua cada query 3 veces para una tasa de trigger fiable, itera hasta 5 veces y selecciona la mejor por score de TEST (no train) para evitar overfitting.
**Source:** anthropics/skills — skill-creator SKILL.md (Description Optimization)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "It splits the eval set into 60% train and 40% held-out test, evaluates the current description (running each query 3 times to get a reliable trigger rate) ... iterating up to 5 times. When it's done ... returns JSON with best_description — selected by test score rather than train score to avoid overfitting."
**Context:** Metrica de calidad de triggering medida formalmente con split ML-style; las 3 corridas absorben la no-determinacion.
**Confidence:** high

## 11. Near-misses: los negativos deben ser dificiles, no obvios

**Claim:** Las queries should-not-trigger mas valiosas son los "near-misses" que comparten keywords con la skill pero necesitan otra cosa; las negativas obviamente irrelevantes no prueban nada.
**Source:** anthropics/skills — skill-creator SKILL.md (Step 1: Generate trigger eval queries)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "the most valuable ones are the near-misses — queries that share keywords or concepts with the skill but actually need something different. ... The key thing to avoid: don't make should-not-trigger queries obviously irrelevant. 'Write a fibonacci function' as a negative test for a PDF skill is too easy — it doesn't test anything."
**Context:** Calidad de la medicion de triggering depende de negativos adversariales; coincide con el consejo de "negative tests" del articulo de evals.
**Confidence:** high

## 12. Packaging: package_skill.py produce un .skill instalable

**Claim:** El empaquetado se hace con `python -m scripts.package_skill <path>`, funciona en cualquier entorno con Python y filesystem, y produce un archivo `.skill` que el usuario descarga/instala.
**Source:** anthropics/skills — skill-creator SKILL.md (Package and Present / Claude.ai)
**URL:** https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
**Date:** 2026
**Excerpt:** "python -m scripts.package_skill <path/to/skill-folder> ... After packaging, direct the user to the resulting .skill file path so they can install it." / "The package_skill.py script works anywhere with Python and a filesystem."
**Context:** Empaquetado es el ultimo paso del loop; portable a Claude.ai, Claude Code y Cowork.
**Confidence:** high

## 13. Skill Creator 2.0: cuatro modos Create/Eval/Improve/Benchmark

**Claim:** La actualizacion Skill Creator 2.0 anade un proceso de cuatro pasos — Create, Eval, Improve, Benchmark — convirtiendo la creacion de "adivinar" a ingenieria, con debugging asistido por IA que analiza logs de fallo y sugiere cambios.
**Source:** The Tool Nerd (Akhil) — "Anthropic Skill Creator 2.0 Update"
**URL:** https://www.thetoolnerd.com/p/anthropic-skill-creator-20-update
**Date:** 2026-03-17 (meta article:modified_time)
**Excerpt:** "there is a clear, four-step process to make sure your skills are solid: Create / Eval / Improve / Benchmark ... When a test fails, the Improve mode analyzes the failure logs and suggests changes to the skill's instructions."
**Context:** Articulo secundario que enmarca el flujo del SKILL.md oficial; util para narrativa CEO ("de guessing a engineering").
**Confidence:** medium

## 14. Capability skills vs Preference skills

**Claim:** Anthropic clasifica skills en dos tipos: capability skills (extienden lo que el modelo base puede hacer, ej. extraer de PDFs complejos) y preference skills (codifican como quieres el trabajo, ej. formato de notas en un estilo de empresa).
**Source:** The Tool Nerd (Akhil) — "Anthropic Skill Creator 2.0 Update"
**URL:** https://www.thetoolnerd.com/p/anthropic-skill-creator-20-update
**Date:** 2026-03-17
**Excerpt:** "Capability skills extend what the base model can do. For example, a skill that extracts information from complex PDFs or fills out forms. Preference skills encode how you want work done. For example, formatting meeting notes in a specific structure or writing documentation in your company's style."
**Context:** Distincion util para gobernanza multi-tenant: capability se puede deprecar si el modelo base mejora; preference es propio del tenant.
**Confidence:** medium

## 15. Mantenimiento: regla de obsolescencia (correr evals con la skill DESACTIVADA)

**Claim:** Para mantenimiento se debe correr el harness periodicamente con la skill completamente desactivada; si el modelo base ya pasa todos los tests nativamente, la skill solo agrega latencia y debe borrarse.
**Source:** Shuva Jyoti Kar (Google Cloud Community, Medium) — "Agent Skills Evals: Stop Vibe-Testing Your Skills"
**URL:** https://medium.com/google-cloud/agent-skills-evals-stop-vibe-testing-your-skills-edd9eaaa6a1a
**Date:** 2026-03-07
**Excerpt:** "Every few months, run your eval harness with your custom Agent Skill completely disabled. If the base model can suddenly pass all the tests natively without needing your custom instructions, your skill is just adding unnecessary latency. Delete the code and move on."
**Context:** Politica de deprecacion concreta y medible; alinea con la regla de Anthropic de baseline sin skill.
**Confidence:** medium

## 16. Nondeterminismo: 3-5 corridas por prompt, distribucion no un solo pase

**Claim:** Un solo run exitoso no significa nada; hay que correr cada prompt 3-5 veces y buscar una distribucion estadistica alta de exito, no un pase aislado.
**Source:** Shuva Jyoti Kar (Google Cloud Community, Medium) — "Agent Skills Evals"
**URL:** https://medium.com/google-cloud/agent-skills-evals-stop-vibe-testing-your-skills-edd9eaaa6a1a
**Date:** 2026-03-07
**Excerpt:** "A single successful test run means nothing. Run every prompt through your skill harness 3 to 5 trials. You aren't looking for a single pass; you are looking for a high statistical distribution of success for that specific skill."
**Context:** Variance analysis explicito; coincide con las 3 corridas del optimizador de description de Anthropic.
**Confidence:** medium

## 17. Tres pilares de exito: viabilidad funcional, cumplimiento de directivas, eficiencia operacional

**Claim:** Una skill se mide en tres pilares: Functional Viability (cumplio la tarea core), Directive Compliance (siguio las reglas/guardas especificas) y Operational Efficiency (cuantos tokens quemo). Hay que graduar el RESULTADO, no el camino de ejecucion.
**Source:** Shuva Jyoti Kar (Google Cloud Community, Medium) — "Agent Skills Evals"
**URL:** https://medium.com/google-cloud/agent-skills-evals-stop-vibe-testing-your-skills-edd9eaaa6a1a
**Date:** 2026-03-07
**Excerpt:** "grade the outcome of the skill, not the execution path. ... Functional Viability: Did the skill actually accomplish its core task? ... Directive Compliance: Did the execution ... follow your specific rules or guard? ... Operational Efficiency ... How many tokens did the skill burn to reach the right answer?"
**Context:** Mapea casi 1:1 a las metricas de calidad pedidas (precision, consistencia, eficiencia de tokens).
**Confidence:** medium

## 18. Checks deterministicos antes de LLM-as-judge

**Claim:** Hay que evaluar todo lo posible SIN otro LLM (regex, parsing AST: checks booleanos instantaneos, baratos e inmunes a alucinacion) y reservar el LLM-as-judge (con Structured Outputs / schema Pydantic estricto) solo para output cualitativo.
**Source:** Shuva Jyoti Kar (Google Cloud Community, Medium) — "Agent Skills Evals"
**URL:** https://medium.com/google-cloud/agent-skills-evals-stop-vibe-testing-your-skills-edd9eaaa6a1a
**Date:** 2026-03-07
**Excerpt:** "Evaluate the skill's output using everything you can without relying on another LLM. Deterministic checks are instantaneous, cheap, and immune to hallucinations. ... If your skill dictates that the agent must 'write a clear, empathetic incident disclosure email', you need qualitative grading. ... lock the judge's response into a strict JSON schema using Pydantic."
**Context:** Coincide con la guia de Anthropic ("for assertions that can be checked programmatically, write and run a script ... scripts are faster, more reliable"). Negative test: verificar que la skill NO dispare ante prompt fuera de dominio.
**Confidence:** medium

## 19. Anti-patron #1: el fallo casi siempre es la description, no las instrucciones

**Claim:** Cuando una skill no dispara, casi nunca es por las instrucciones del cuerpo: es por la description. El error mas comun es escribir la description para un lector humano ("This skill helps with README generation") en vez de para la logica de matching del agente (que busca frases que reflejan peticiones reales).
**Source:** Sathish Raju (Medium) — "The SKILL.md Pattern: How to Write AI Agent Skills That Actually Work"
**URL:** https://medium.com/@sathishkraju/the-skill-md-pattern-how-to-write-ai-agent-skills-that-actually-work-c4ab23400ed5
**Date:** 2026-04-01
**Excerpt:** "If your skill doesn't trigger, it is almost never the instructions. It is the description. ... Common mistake: Writing the description for a human reader — 'This skill helps with README generation' — instead of for the agent's matching logic. ... Write it like a trigger: 'Use when the user asks to write, update, or generate a README.'"
**Context:** El anti-patron mas citado. Patron que funciona: empezar con "Use when the user..." y listar frases reales, sinonimos y variantes.
**Confidence:** medium

## 20. allowed-tools: limitar tools por skill (seguridad / scripts inseguros)

**Claim:** El campo `allowed-tools` en frontmatter restringe que tools puede usar la skill durante su activacion (ej. una skill de analisis de logs limitada a Read/Grep/Glob no puede ejecutar shell ni escribir archivos), anadiendo garantias de seguridad a skills observacionales. Es experimental en el spec pero soportado en Claude Code.
**Source:** Sathish Raju (Medium) — "The SKILL.md Pattern"
**URL:** https://medium.com/@sathishkraju/the-skill-md-pattern-how-to-write-ai-agent-skills-that-actually-work-c4ab23400ed5
**Date:** 2026-04-01
**Excerpt:** "With this active, the agent cannot execute shell commands, write files, or make any external calls during this skill's execution — even if those tools would normally be available. ... The allowed-tools field is experimental in the current spec but is well-supported in Claude Code today."
**Context:** Mitigacion directa contra scripts inseguros. Para multi-tenant: scope per-skill de tools = control de blast radius. NOTA: el firecrawl/Ville menciona variantes `allowed-tools: Bash(gh *)` con wildcards [ver bloque 22].
**Confidence:** medium

## 21. Anti-patron de seguridad: las skills son codigo con procedencia — revisar antes de instalar

**Claim:** Las skills son codigo; antes de instalar una de un registry publico hay que leer todo el SKILL.md, revisar los scripts en scripts/ y buscar instrucciones que intenten leer config files, exfiltrar datos o modificar la config del agente. Confiar como en un paquete npm de terceros.
**Source:** Sathish Raju (Medium) — "The SKILL.md Pattern"
**URL:** https://medium.com/@sathishkraju/the-skill-md-pattern-how-to-write-ai-agent-skills-that-actually-work-c4ab23400ed5
**Date:** 2026-04-01
**Excerpt:** "Skills are code, and code has provenance. Before installing any skill from a public registry, read the full SKILL.md, review any scripts in the scripts/ folder, and check for instructions that attempt to read config files, exfiltrate data, or modify agent configuration. Trust skills the same way you'd trust a third-party npm package."
**Context:** Coincide con el "Principle of Lack of Surprise" de Anthropic (no malware, no exploit, intent no debe sorprender). Critico para gobernanza de skills de terceros en plataforma multi-tenant.
**Confidence:** medium

## 22. Anti-patrones de "context tax" y over-engineering (skill vs script)

**Claim:** Cada skill paga un "impuesto de contexto": su description carga en cada sesion dispare o no (100 tokens x miles de ingenieros x sesiones/dia = millones de tokens de overhead diario). Antes de escribir: probar la tarea SIN skill; preguntarse si es skill o script (si un bash/Makefile hace el 80%, hacer eso); escribir el eval ANTES de la skill; mantenerla minima (un "nudge", no un tutorial).
**Source:** Ville (efexen, Substack) citado en Firecrawl — "Does Your Skill Earn Its Keep?" / Firecrawl "Agent Skills Explained"
**URL:** https://www.firecrawl.dev/blog/agent-skills
**Date:** 2026-05-26 (articulo Firecrawl; post de Ville referenciado)
**Excerpt:** "100 tokens of description. 1,000 engineers. 10 sessions a day. That's 1 million tokens of daily overhead before the agent touches a single task. ... If someone could write a bash script or a Makefile target that does 80% of it — do that instead. The worst skills use 500 tokens of natural language to describe something that is really just make test with some flags."
**Context:** Marco de "earn its keep" — el anti-patron de skill bloat / over-engineering / skills demasiado genericas, con costo cuantificado. Recomendacion: skills broadly-applicable por defecto; team-specific opt-in. `disable-model-invocation: true` baja el tax a casi cero para skills con side effects (deploys, commits). [Detalle de frontmatter via Firecrawl; algunos campos NO VERIFICADOS contra spec oficial — ver nota.]
**Confidence:** medium

## 23. Anti-patron operacional: el "Code Execution Mirage" y el bar de calidad extremo

**Claim:** Muchos entornos cloud gestionados bloquean ejecucion de codigo arbitrario por seguridad, asi que no se puede asumir que el agente correra scripts Python bundled; las skills deben disenarse como reglas declarativas puras. Ademas, si las reglas de una skill son vagas, DEGRADA activamente el baseline del modelo.
**Source:** Shuva Jyoti Kar (Google Cloud Community, Medium) — "Agent Skills Evals"
**URL:** https://medium.com/google-cloud/agent-skills-evals-stop-vibe-testing-your-skills-edd9eaaa6a1a
**Date:** 2026-03-07
**Excerpt:** "Many managed AI cloud environments completely block arbitrary code execution for security reasons. Your skills must be designed as pure declarative rules ... If a skill's rules are vague, it actively degrades the agent's baseline performance. Your prompt engineering within the SKILL.md file must be flawless, deterministic, and highly optimized."
**Context:** Refuerza que una skill mediocre es peor que ninguna (negativo medible en el harness). Tension con la postura de Anthropic de bundlear scripts — depende del entorno de ejecucion del tenant.
**Confidence:** medium

---

## Notas de verificacion

- **[NO VERIFICADO]** Campos de frontmatter avanzados citados por Firecrawl (bloque 22): `disable-model-invocation`, `paths`, `effort` (low/medium/high), `context: fork`, `argument-hint`, variables `$ARGUMENTS` / `${CLAUDE_SKILL_DIR}`. No los confirme contra el spec oficial en agentskills.io/specification ni en docs platform.claude.com; provienen de un articulo de blog (Firecrawl, citando a Ville). El `allowed-tools` SI esta corroborado por dos fuentes (Firecrawl + Sathish Raju), aunque este ultimo lo marca "experimental in the current spec".
- **[NO VERIFICADO]** Cifra "billones al ano en valor economico" y tono motivacional dentro del SKILL.md de skill-creator son texto del propio archivo (retorica de Anthropic), no una metrica externa.
- **[NO VERIFICADO]** SkillsBench (arXiv:2602.12670) y el estudio Bosch/CMU (arXiv:2602.08004, 40,285 skills, mediana 1,414 tokens) aparecen en resultados de busqueda y en Firecrawl pero NO accedi a los papers directamente; las cifras (18.5x en 20 dias, 9% riesgo critico, 40% accede a contexto sensible) provienen de la sintesis de Firecrawl, no de lectura primaria del arXiv.
- Limite de tokens: dos cifras conviven — "<500 lineas" para el cuerpo (Anthropic skill-creator) y "<5,000 tokens" recomendado (Firecrawl/Sathish Raju citando el spec). Ambas son guias, no hard limits (skill-creator dice "feel free to go longer if needed").
- Instrucciones Cowork-especificas del skill-creator (usar `--static` para el eval viewer sin browser, feedback via descarga de `feedback.json`) estan en el SKILL.md oficial y son directamente relevantes para este entorno.
