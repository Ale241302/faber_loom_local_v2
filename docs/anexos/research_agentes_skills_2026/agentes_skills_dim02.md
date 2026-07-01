# Agentes Skills (dim02): Arquitectura de una Skill — estado junio 2026

Investigacion sobre el patron tecnico SKILL.md: estructura del directorio, frontmatter/manifest y sus campos, los tres tiers de progressive disclosure con costos por tier, versionado, carga lazy de recursos embebidos (scripts/references/assets/examples) y el tradeoff entre skills deterministas (scripts) vs interpretadas por LLM. Fuentes: 4 articulos Medium/blog (feb-may 2026) + 2 oficiales (Anthropic Engineering, spec agentskills.io). El estandar es estable y multi-plataforma; lo unico inestable/experimental son campos como `allowed-tools` y extensiones propietarias de Claude Code (`paths`, `effort`, `context: fork`).

---

## 1. Estructura del directorio skill

Claim: Una skill es un directorio que contiene como minimo un archivo SKILL.md; carpetas opcionales scripts/, references/, assets/.
Source: agentskills.io (spec oficial)
URL: https://agentskills.io/specification
Date: spec viva (consultada jun 2026)
Excerpt: "A skill is a directory containing, at minimum, a `SKILL.md` file: skill-name/ ├── SKILL.md # Required: metadata + instructions ├── scripts/ # Optional: executable code ├── references/ # Optional: documentation ├── assets/ # Optional: templates, resources"
Context: Define el contrato fisico minimo. Para una plataforma multi-tenant, el directorio es la unidad versionable y distribuible por tenant.
Confidence: high

Claim: La carpeta examples/ aparece como directorio opcional adicional en parte de la literatura, aunque NO esta en los tres directorios canonicos de la spec (scripts/references/assets).
Source: Loic Carrere, Medium
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "code-review/ SKILL.md # Required: instructions + metadata scripts/ # Optional: executable code references/ # Optional: documentation assets/ # Optional: templates, data files examples/ # Optional: sample inputs/outputs"
Context: examples/ es convencion de autor, no campo normativo. La spec solo enumera scripts/, references/, assets/ y "Any additional files or directories". Tratar examples/ como recurso lazy mas, no como estructura obligatoria.
Confidence: medium

Claim: La spec recomienda referencias de archivo a un solo nivel de profundidad desde SKILL.md, con rutas relativas desde la raiz del skill.
Source: agentskills.io
URL: https://agentskills.io/specification
Date: spec viva
Excerpt: "Keep file references one level deep from `SKILL.md`. Avoid deeply nested reference chains."
Context: Limita cadenas de referencias anidadas que romperian el control de cuanto contexto entra. Regla de diseno relevante para auditar skills de terceros.
Confidence: high

Claim: Las skills viven en ubicaciones predecibles por plataforma; el formato es identico aunque los paths difieran.
Source: SwirlAI Newsletter (Aurimas Griciunas)
URL: https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
Date: 2026-03-11
Excerpt: "On Claude Code, that's `~/.claude/skills/` for personal skills or `.claude/skills/` inside a project. Codex CLI uses `.agents/skills/`. Gemini CLI uses `.gemini/skills/`. The paths differ, but the format is identical across all of them."
Context: La portabilidad es real: misma SKILL.md, distinto directorio de descubrimiento. Para multi-tenant esto permite un repositorio canonico y deploy a distintos runtimes.
Confidence: high

---

## 2. Frontmatter / manifest: campos

Claim: El frontmatter YAML tiene solo dos campos requeridos (`name`, `description`) y cuatro opcionales (`license`, `compatibility`, `metadata`, `allowed-tools`).
Source: agentskills.io
URL: https://agentskills.io/specification
Date: spec viva
Excerpt: "`name` Yes Max 64 characters. Lowercase letters, numbers, and hyphens only. (...) `description` Yes Max 1024 characters. (...) `license` No (...) `compatibility` No Max 500 characters. (...) `metadata` No Arbitrary key-value mapping (...) `allowed-tools` No Space-separated string of pre-approved tools the skill may use. (Experimental)"
Context: Tabla canonica de campos. `allowed-tools` esta marcado Experimental: no apoyarse en el para enforcement de seguridad multi-tenant.
Confidence: high

Claim: `name` debe tener 1-64 chars, solo minusculas alfanumericas y guiones, sin guion inicial/final, sin guiones consecutivos, y debe coincidir con el nombre del directorio padre.
Source: agentskills.io
URL: https://agentskills.io/specification
Date: spec viva
Excerpt: "Must be 1-64 characters (...) May only contain unicode lowercase alphanumeric characters (`a-z`, `0-9`) and hyphens (`-`) (...) Must not contain consecutive hyphens (`--`) (...) Must match the parent directory name"
Context: Restriccion fuerte de naming. En Claude Code el name se vuelve slash-command, lo que refuerza la regla.
Confidence: high

Claim: `description` debe tener 1-1024 chars y describir tanto QUE hace la skill como CUANDO usarla, con keywords; es el campo que determina el routing.
Source: agentskills.io + Firecrawl
URL: https://agentskills.io/specification
Date: spec viva
Excerpt: "Should describe both what the skill does and when to use it (...) Should include specific keywords that help agents identify relevant tasks"
Context: La calidad de `description` decide si la skill se activa o no. Firecrawl: "the description field carries more weight than it appears (...) A vague description like 'helps with code' will miss most triggers." (https://www.firecrawl.dev/blog/agent-skills, 2026-05-26). Critico para precision de activacion.
Confidence: high

Claim: `compatibility` (max 500 chars) declara requisitos de entorno: producto destino, paquetes de sistema, acceso de red. La mayoria de skills no lo necesitan.
Source: agentskills.io
URL: https://agentskills.io/specification
Date: spec viva
Excerpt: "Can indicate intended product, required system packages, network access needs, etc. (...) Most skills do not need the `compatibility` field."
Context: Util para skills con dependencias (ej. "Requires git, docker, jq, and access to the internet"). Senala explicitamente necesidad de red, relevante para sandboxing.
Confidence: high

Claim: `allowed-tools` es un string separado por espacios de herramientas pre-aprobadas; soporta wildcards; es experimental y el soporte varia entre implementaciones.
Source: agentskills.io + Firecrawl
URL: https://agentskills.io/specification
Date: spec viva
Excerpt: "A space-separated string of tools that are pre-approved to run (...) Experimental. Support for this field may vary between agent implementations"
Context: Ejemplo: `allowed-tools: Bash(git:*) Bash(jq:*) Read`. Firecrawl documenta wildcards como `Bash(gh *)`. Por ser experimental y variable, NO es base confiable de control de permisos cross-platform.
Confidence: high

---

## 3. Versionado de skills

Claim: `version` NO es campo top-level de la spec; para versionar se usa el mapa `metadata`.
Source: Loic Carrere, Medium
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "**Note:** `version` is not a top-level spec field. Use the `metadata` map for maximum portability."
Context: Hallazgo clave de versionado. La spec confirma `metadata` como "Arbitrary key-value mapping" con ejemplo `version: \"1.0\"`. Para multi-tenant, versionar dentro de metadata es lo portable; no inventar un campo top-level `version`.
Confidence: high

Claim: El ejemplo oficial de la spec ubica version dentro de metadata como string.
Source: agentskills.io
URL: https://agentskills.io/specification
Date: spec viva
Excerpt: "metadata: author: example-org version: \"1.0\""
Context: Confirma el patron de Carrere desde la fuente normativa. version va como string (entre comillas) bajo metadata.
Confidence: high

Claim: Actualizar skills a mitad de sesion es problematico: las skills se cargan al inicio de sesion y los cambios no aplican hasta reiniciar la sesion.
Source: Firecrawl
URL: https://www.firecrawl.dev/blog/agent-skills
Date: 2026-05-26
Excerpt: "Skills load at session start. If you push changes to a SKILL.md while an agent session is already running, those changes won't take effect until the session restarts. (...) rolling out updates without disrupting active workflows is a real coordination problem that the tooling hasn't fully solved yet."
Context: Limitacion operativa de versionado en produccion. Para una plataforma multi-tenant con sesiones largas, desplegar version N+1 requiere estrategia de invalidacion/reinicio; el estandar no la resuelve.
Confidence: high

---

## 4. Progressive disclosure: los tres tiers y tokens por tier

Claim: Progressive disclosure es un sistema de carga de tres niveles que mantiene el costo de contexto proporcional a lo usado, no a lo instalado.
Source: Anthropic Engineering (fuente original del termino)
URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
Date: 2025-10-16
Excerpt: "This metadata is the **first level** of *progressive disclosure* (...) The actual body of this file is the **second level** of detail (...) These additional linked files are the **third level** (and beyond) of detail, which Claude can choose to navigate and discover only as needed."
Context: Definicion canonica de Anthropic. Es el principio de diseno nuclear del estandar.
Confidence: high

Claim: Tier 1 / Discovery: al inicio se cargan solo name + description de cada skill (~100 tokens por skill); permite instalar muchas skills sin penalizacion de contexto.
Source: Neelam Pawar (Google Cloud Community), Medium
URL: https://medium.com/google-cloud/agent-skills-dynamic-context-engineering-c1bebf028cf7
Date: 2026-04-07
Excerpt: "Level 1: Metadata (always loaded , ~100 tokens per skill) (...) The Skill's YAML frontmatter (name + description) from each SKILL.md gets injected into the system prompt (...) This lightweight approach means you can install many Skills without context penalty."
Context: Cuantifica el tier 1. La spec lo confirma: "Metadata (~100 tokens): The `name` and `description` fields are loaded at startup for all skills".
Confidence: high

Claim: Medicion empirica del tier 1 sobre las 17 skills oficiales de Anthropic: mediana ~80 tokens por skill (rango ~55 a ~235); las 17 juntas ~1,700 tokens.
Source: SwirlAI Newsletter
URL: https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
Date: 2026-03-11
Excerpt: "the median discovery cost is ~80 tokens per skill, ranging from ~55 (webapp-testing) to ~235 (xlsx). All 17 skills together cost ~1,700 tokens, meaning an agent can be aware of dozens of skills for less context than a single activated skill."
Context: Numeros medidos, no estimados. Mas precisos que el "~100 tokens" redondeado. Otras fuentes citan "30-50 tokens" (Firecrawl) — la dispersion depende de la longitud real de la description.
Confidence: high

Claim: Tier 2 / Activation: cuando la tarea coincide con la description, se carga el cuerpo completo de SKILL.md (recomendado < 5,000 tokens); medicion empirica: rango ~275 a ~8,000 tokens, mediana ~2,000.
Source: SwirlAI + agentskills.io
URL: https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
Date: 2026-03-11
Excerpt: "body size ranges from ~275 tokens (internal-comms) to ~8,000 tokens (skill-creator), with a median around 2,000."
Context: La spec recomienda < 5,000 tokens; el skill-creator (~8,000) lo excede, mostrando que el limite es recomendacion, no hard cap. Para multi-tenant, vigilar skills que rebasan el limite recomendado.
Confidence: high

Claim: El estudio Bosch/CMU sobre 40,285 skills publicas hallo cuerpo mediano de 1,414 tokens.
Source: Firecrawl (citando Ling et al., arXiv:2602.08004)
URL: https://www.firecrawl.dev/blog/agent-skills
Date: 2026-05-26
Excerpt: "the median skill body is 1,414 tokens — confirming that most skills fit comfortably alongside planning context and tool schemas without competing for space."
Context: Dato de poblacion grande (40k skills), no solo las 17 oficiales. Confirma que el ecosistema real respeta el principio de cuerpos compactos. [NOTA: el id arXiv 2602.08004 con prefijo "2602" implica feb-2026; no verificado contra arxiv.org directamente].
Confidence: medium

Claim: Tier 3 / Execution: recursos de soporte (scripts, references, assets) entran al contexto solo cuando el agente alcanza el paso que los requiere; los scripts se ejecutan via bash y solo su output entra al contexto, no el codigo.
Source: Neelam Pawar (Google Cloud), Medium
URL: https://medium.com/google-cloud/agent-skills-dynamic-context-engineering-c1bebf028cf7
Date: 2026-04-07
Excerpt: "Level 3: Resources and code (loaded as needed) (...) scripts (scripts/validate.py) load on-demand during execution. Scripts are executed via bash, and only the output enters context, not the script code itself."
Context: Distincion crucial: el codigo del script NO consume tokens; solo su salida. Esto hace efectivamente ilimitado el contexto bundleable. Anthropic: "Claude can run this script without loading either the script or the PDF into context."
Confidence: high

Claim: El contexto que puede bundlearse en una skill es efectivamente ilimitado porque el agente con filesystem + code execution no necesita leer la skill entera.
Source: Anthropic Engineering
URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
Date: 2025-10-16
Excerpt: "Agents with a filesystem and code execution tools don't need to read the entirety of a skill into their context window when working on a particular task. This means that the amount of context that can be bundled into a skill is effectively unbounded."
Context: Implicacion arquitectonica fuerte: el limite de 5,000 tokens aplica al SKILL.md, no a la skill total. Una skill puede llevar megabytes de references/ que nunca se cargan si no se necesitan.
Confidence: high

Claim: La promocion entre tiers la decide la PLATAFORMA mediante razonamiento LLM sobre las descriptions; Claude selecciona skills por razonamiento puro, y la calidad de description determina la precision de routing.
Source: SwirlAI
URL: https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
Date: 2026-03-11
Excerpt: "The platform makes this decision using LLM reasoning over the descriptions from the discovery layer. Research shows that Claude selects skills through pure reasoning, with description quality directly determining routing accuracy."
Context: No hay matching deterministico por keywords ni embeddings obligatorios: es razonamiento del modelo. Refuerza por que la description es el campo mas importante.
Confidence: high

Claim: Matiz semantico: el termino correcto seria "progressive discovery" porque el agente es el sujeto activo que descubre; la skill es un recurso pasivo (bytes en disco sin trigger propio).
Source: Phil Whittaker, dev.to
URL: https://dev.to/phil-whittaker/progressive-discovery-a-better-mental-model-for-agent-skills-51bd
Date: 2026-04-19
Excerpt: "Claude is the one doing something. The Skill is not. The Skill is bytes on disk. It has no mechanism, no trigger, no awareness of context. (...) Claude is the active party. The Skill is a passive resource."
Context: Modelo mental util para autores: una skill se disena para SER DESCUBIERTA en cada capa, no para "revelar" en una secuencia fija. Cambia la pregunta de diseno a "puede el agente encontrar lo que necesita aqui?".
Confidence: medium

---

## 5. Scripts y recursos embebidos (carga lazy, ejecucion via bash)

Claim: Los recursos opcionales se cargan lazy: el agente solo los lee cuando realmente los necesita, no al inicio; archivos nunca referenciados en una sesion nunca se cargan.
Source: Loic Carrere + Firecrawl
URL: https://www.firecrawl.dev/blog/agent-skills
Date: 2026-05-26
Excerpt: "If the instructions reference a script in scripts/ or a document in references/, those files load on demand during execution. Files that are never referenced in a session never load at all."
Context: Carga perezosa real a nivel archivo. Carrere lo refuerza: "These resources are loaded lazily: the agent only reads them when it actually needs them, not at startup."
Confidence: high

Claim: La secuencia real de operaciones: el contexto arranca con system prompt + metadata de skills; Claude dispara la skill invocando Bash para leer pdf/SKILL.md; luego lee forms.md; luego procede con la tarea.
Source: Anthropic Engineering
URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
Date: 2025-10-16
Excerpt: "Claude triggers the PDF skill by invoking a Bash tool to read the contents of `pdf/SKILL.md`; Claude chooses to read the `forms.md` file bundled with the skill; Finally, Claude proceeds with the user's task"
Context: Confirma que la activacion misma es una lectura de archivo via Bash, no un mecanismo magico. La skill se "carga" leyendo el archivo del filesystem.
Confidence: high

Claim: La spec soporta explicitamente Python, Bash y JavaScript en scripts/; los scripts deben ser autocontenidos o documentar dependencias y manejar edge cases.
Source: agentskills.io
URL: https://agentskills.io/specification
Date: spec viva
Excerpt: "Supported languages depend on the agent implementation. Common options include Python, Bash, and JavaScript. (...) Be self-contained or clearly document dependencies (...) Handle edge cases gracefully"
Context: Define lenguajes soportados y contrato de calidad para scripts. El soporte concreto depende de la implementacion del agente.
Confidence: high

Claim: references/ contiene docs cargadas on-demand (REFERENCE.md, FORMS.md, archivos por dominio); assets/ contiene recursos estaticos (templates, imagenes, data files, schemas).
Source: agentskills.io
URL: https://agentskills.io/specification
Date: spec viva
Excerpt: "`references/` Contains additional documentation that agents can read when needed (...) Keep individual reference files focused. Agents load these on demand, so smaller files mean less use of context. (...) `assets/` Contains static resources: Templates (...) Images (...) Data files (lookup tables, schemas)"
Context: Separar references (texto que el LLM lee) de assets (recursos que el codigo consume) es la distincion practica. Archivos pequenos y enfocados = menos tokens al cargarse.
Confidence: high

Claim: Ejemplo real (skill pdf de Anthropic): SKILL.md + reference.md + forms.md + 8 scripts Python; SKILL.md apunta a los archivos de ejecucion via pointers tipo "see REFERENCE.md" / "follow FORMS.md".
Source: SwirlAI
URL: https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure
Date: 2026-03-11
Excerpt: "The `scripts/` folder holds 8 Python utilities the agent can call during execution. (...) ## Next Steps - For advanced pypdfium2 usage, see REFERENCE.md (...) - If you need to fill out a PDF form, follow the instructions in FORMS.md"
Context: Caso concreto verificable que muestra los tres tipos de contenido en tier 3: conocimiento de dominio (REFERENCE.md), scripts ejecutables, y tool pointers (`python scripts/check_fillable_fields <file.pdf>`).
Confidence: high

Claim: Variables dinamicas en Claude Code: `${CLAUDE_SKILL_DIR}` referencia scripts bundleados sin importar el cwd; `$ARGUMENTS` / `$ARGUMENTS[0]` para argumentos del slash-command.
Source: Firecrawl
URL: https://www.firecrawl.dev/blog/agent-skills
Date: 2026-05-26
Excerpt: "Skills support runtime substitutions that most authors overlook: `$ARGUMENTS` (everything passed after the slash command), `$ARGUMENTS[0]` for positional access, and `${CLAUDE_SKILL_DIR}` to reference bundled scripts regardless of where the user's working directory is."
Context: Extension propietaria de Claude Code (no spec base). Util para invocar scripts de forma portable dentro de la skill. No asumir disponibilidad cross-platform.
Confidence: medium

---

## 6. Skills deterministas (scripts) vs interpretadas por LLM — el tradeoff

Claim: Ciertas operaciones convienen ejecutarse como codigo (deterministico, barato, repetible) en vez de generarse token a token por el LLM; ej. ordenar una lista o extraer campos de un PDF.
Source: Anthropic Engineering
URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
Date: 2025-10-16
Excerpt: "sorting a list via token generation is far more expensive than simply running a sorting algorithm. Beyond efficiency concerns, many applications require the deterministic reliability that only code can provide. (...) because code is deterministic, this workflow is consistent and repeatable."
Context: Tesis central del tradeoff. El codigo da fiabilidad deterministica que la generacion del LLM no garantiza. Para outputs que requieren estructura exacta, mover esa parte a script.
Confidence: high

Claim: Las skills NO son deterministas: como un LLM interpreta las instrucciones, hay no-determinismo inherente; si se requiere estructura garantizada hay que combinar con structured output o tool calls.
Source: Loic Carrere, Medium
URL: https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
Date: 2026-02-09
Excerpt: "**Skills are not deterministic.** Because an LLM interprets the instructions, there is inherent non-determinism. If you need guaranteed structure, combine a skill with structured output constraints or use tool calls for the critical parts."
Context: El otro lado del tradeoff. Una skill "interpretada" (solo markdown) es flexible pero no garantiza salida. El patron robusto es skill (juicio) + script (parte critica deterministica).
Confidence: high

Claim: La regla de decision: si la tarea es mayormente una secuencia de pasos deterministas, escribir un script/Makefile en vez de una skill; la skill maneja los juicios (cuando correr, como interpretar output, que hacer ante lo inesperado), el script la parte predecible.
Source: Firecrawl (citando a Ville, "Does Your Skill Earn Its Keep?")
URL: https://www.firecrawl.dev/blog/agent-skills
Date: 2026-05-26
Excerpt: "is this a skill or a script? (...) If someone could write a bash script or a Makefile target that does 80% of it — do that instead. (...) A skill can call a script. The skill handles the judgment calls (...) The script handles the predictable parts reliably and cheaply."
Context: Heuristica accionable de diseno. "The worst skills use 500 tokens of natural language to describe something that is really just `make test` with some flags." Implicacion: separar logica deterministica (script) de logica de decision (skill markdown).
Confidence: high

Claim: Skills (sabiduria interna / how-to / expertise) son distintas de MCP (alcance externo / acceso a datos) y de Tools (capacidades base que viven siempre en el contexto). Skills se cargan dinamicamente desde filesystem; los tools consumen contexto en cada turno.
Source: Neelam Pawar (Google Cloud), Medium
URL: https://medium.com/google-cloud/agent-skills-dynamic-context-engineering-c1bebf028cf7
Date: 2026-04-07
Excerpt: "Tools live in the context window. Every time you send a prompt, those tool definitions (...) are taking up precious real estate. (...) Skills are loaded dynamically. They stay tucked away in the filesystem until the agent actually needs them."
Context: Ubica skills en la capa de "expertise/procedimiento" frente a tools (capacidad bruta) y MCP (conectividad). Una skill puede orquestar multiples tool calls; un script bundleado es la version deterministica de un paso.
Confidence: high

---

## 7. Seguridad y riesgo (relevante para multi-tenant en produccion)

Claim: El estudio de 40k+ skills hallo que ~40% de skills publicadas acceden contexto sensible o hacen escrituras, y 9% caen en categoria de riesgo critico; la spec aun no impone modelos de permisos ni sandboxing a nivel plataforma.
Source: Firecrawl (citando Ling et al.)
URL: https://www.firecrawl.dev/blog/agent-skills
Date: 2026-05-26
Excerpt: "nearly 40% of published skills access sensitive context or perform writes, and 9% fall into the critical risk category. The spec doesn't yet enforce permission models or sandboxing at the platform level, so the burden of scoping skills safely falls on whoever writes them."
Context: Critico para CEO de plataforma multi-tenant: el aislamiento NO viene del estandar. Hay que construir el sandbox/permisos por encima. `allowed-tools` es experimental, no enforcement real.
Confidence: high

Claim: Recomendacion oficial: instalar skills solo de fuentes confiables; auditar (leer todos los archivos, dependencias, scripts) antes de usar las de fuentes menos confiables; vigilar instrucciones que conecten a fuentes de red no confiables.
Source: Anthropic Engineering
URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
Date: 2025-10-16
Excerpt: "We recommend installing skills only from trusted sources. (...) thoroughly audit it before use. Start by reading the contents of the files bundled in the skill (...) pay attention to instructions or code within the skill that instruct Claude to connect to potentially untrusted external network sources."
Context: La skill es codigo + instrucciones ejecutables; tratarla como codigo en review/PR. Relevante para gobernanza de skills por tenant.
Confidence: high

---

## Notas de verificacion

- [NO VERIFICADO] El id arXiv:2602.08004 (estudio Bosch/CMU, "Agent Skills: A Data-Driven Analysis", Ling et al.) se cita solo via Firecrawl; no se accedio a arxiv.org directamente. Las cifras derivadas (40,285 skills, mediana 1,414 tokens, 18.5x en 20 dias, 40%/9% de riesgo) heredan esa confianza media.
- [NO VERIFICADO] Conteos de adopcion (SkillsMP "over 400,000 skills", ClawHub "over 13,000 skills", "26+/20+ plataformas") provienen de blogs secundarios (SwirlAI, Firecrawl); no contrastados con fuente primaria de cada marketplace.
- [NO VERIFICADO] Campos propietarios de Claude Code mas alla de la spec (`disable-model-invocation`, `paths`, `effort`, `context: fork`, `argument-hint`) solo aparecen en Firecrawl; no estan en la spec agentskills.io ni se confirmaron en docs platform.claude.com en esta investigacion. Tratar como extensiones especificas de Claude Code, no estandar.
- Fechas de publicacion tomadas de meta-article:published_time de cada articulo (verificado en el HTML servido).
- El termino "progressive discovery" (Whittaker) es propuesta de un autor, no terminologia oficial; el termino canonico de Anthropic sigue siendo "progressive disclosure".
