# Agent Skills (patron SKILL.md) — dim08: Hallazgos, Tradeoffs, No Resuelto, Recomendacion

> Investigacion junio 2026. Audiencia: CEO plataforma de agentes IA multi-tenant en produccion.
> Fuente primaria solicitada: Medium (abr-jun 2026), complementada con docs oficiales Anthropic, paper arXiv de prompt injection y research de Snyk para seguridad.
> Cada afirmacion de hecho lleva bloque Claim/Source/URL/Date/Excerpt/Context/Confidence. La recomendacion final es juicio del analista, derivada de la evidencia citada.

**Resumen (3-4 lineas).** Agent Skills es un patron simple — una carpeta con un `SKILL.md` (frontmatter YAML + cuerpo Markdown) que el agente carga bajo demanda via progressive disclosure de tres niveles. En 8 meses paso de anuncio de Anthropic (oct 2025) a estandar abierto bajo Linux Foundation con adopcion cross-plataforma (OpenAI Codex, Copilot, VS Code, Cursor, Goose). Pero el mismo diseno que lo hace barato y portable lo vuelve un vector de supply-chain: cada linea es una instruccion ejecutable, sin firma ni sandbox por defecto, y la evidencia muestra explotacion activa en marketplaces. Para una plataforma multi-tenant en produccion, las skills son utiles si y solo si se tratan como codigo con governance, no como prompts.

---

## HALLAZGOS CLAVE

### Claim 1 — Un skill es una carpeta con SKILL.md; frontmatter (name+description) se precarga en el system prompt al arranque
- **Source:** Anthropic Engineering — "Equipping agents for the real world with Agent Skills"
- **URL:** https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- **Date:** 2025-10-16
- **Excerpt:** "At its simplest, a skill is a directory that contains a `SKILL.md file`. This file must start with YAML frontmatter that contains some required metadata: `name` and `description`. At startup, the agent pre-loads the `name` and `description` of every installed skill into its system prompt."
- **Context:** Define la unidad minima y el primer nivel de progressive disclosure. Base del modelo de costo de contexto.
- **Confidence:** Alta (fuente oficial).

### Claim 2 — Progressive disclosure de 3 niveles: metadata (arranque) -> cuerpo SKILL.md (al activarse) -> archivos referenciados (bajo demanda)
- **Source:** Anthropic Engineering
- **URL:** https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- **Date:** 2025-10-16
- **Excerpt:** "This metadata is the first level of progressive disclosure... The actual body of this file is the second level of detail... These additional linked files are the third level (and beyond) of detail, which Claude can choose to navigate and discover only as needed."
- **Context:** El mecanismo nuclear de eficiencia. Permite contexto "efectivamente ilimitado" sin pagar tokens por todo.
- **Confidence:** Alta (oficial).

### Claim 3 — El costo de contexto es proporcional a lo que el agente usa, no a lo instalado (~50-100 tokens/skill de metadata; ~500-5000 al activar)
- **Source:** Medium — Loic Carrere, "The Agent Skills Standard"
- **URL:** https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
- **Date:** 2026-02-09
- **Excerpt:** "With 20 skills, that is roughly 1,000 tokens of metadata at startup... Without skills, 10 workflows at 500 tokens each means 5,000 tokens of permanent overhead. With skills, it is ~500 tokens for the catalog plus ~500 for the active skill. A 10x reduction."
- **Context:** La cifra "10x" es modelado del autor, no medicion controlada; util como orden de magnitud.
- **Confidence:** Media (Medium, ejemplo ilustrativo; la dinamica es consistente con la fuente oficial).

### Claim 4 — Las skills pueden incluir codigo (scripts) que el agente ejecuta como herramientas; solo el output entra al contexto, no el codigo
- **Source:** Anthropic Engineering
- **URL:** https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- **Date:** 2025-10-16
- **Excerpt:** "In our example, the PDF skill includes a pre-written Python script that reads a PDF and extracts all form fields. Claude can run this script without loading either the script or the PDF into context. And because code is deterministic, this workflow is consistent and repeatable."
- **Context:** Aqui esta el eje determinismo: el script da repetibilidad que el LLM por si solo no garantiza. Tambien es la superficie de ataque (ver Snyk/arXiv).
- **Confidence:** Alta (oficial).

### Claim 5 — Skill != tool != prompt != subagente; capas distintas del mismo stack
- **Source:** Medium — Loic Carrere
- **URL:** https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
- **Date:** 2026-02-09
- **Excerpt:** "Skills describe how to do something. Tools do something... A skill is a knowledge module that any agent can load. Think of skills as 'apps' and agents as the 'operating system.'... Skills are not deterministic. Because an LLM interprets the instructions, there is inherent non-determinism."
- **Context:** Clarifica que skill = conocimiento procedimental interpretado por LLM (no determinista por defecto); MCP = conectividad/accion determinista. Clave para decidir cuando usar cual.
- **Confidence:** Alta (consenso entre Medium Carrere, Medium Google Cloud y docs Goose/Block referenciados).

### Claim 6 — Skills vs MCP: skills comparten el contexto del agente (latencia cero, lectura local); MCP es proceso separado por servidor (round-trip de red, stateful)
- **Source:** Medium — Loic Carrere (tabla comparativa)
- **URL:** https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
- **Date:** 2026-02-09
- **Excerpt:** "Isolation: Skills — Shares agent's context | MCP — Separate process per server. Latency: Skills — Zero (local file read) | MCP — Network round-trip. State: Skills — Stateless (text) | MCP — Stateful (running server)."
- **Context:** Implicacion de aislamiento directa para multi-tenant: skills NO estan aisladas por proceso; comparten el contexto del agente. MCP si aisla. Dato load-bearing para la recomendacion.
- **Confidence:** Media-alta (Medium, pero tecnicamente consistente con la arquitectura oficial).

### Claim 7 — Skills se publico como estandar abierto cross-plataforma (dic 2025); adoptado por OpenAI Codex, GitHub Copilot, VS Code, Cursor, Goose, Spring AI
- **Source:** Medium — Loic Carrere; confirmado por nota oficial Anthropic
- **URL:** https://medium.com/@loccarrre/the-agent-skills-standard-how-a-simple-skill-md-file-turns-ai-agents-into-on-demand-specialists-172af1d9737d
- **Date:** 2026-02-09
- **Excerpt:** "On December 18, 2025, the format was published as an open standard for cross-platform portability... OpenAI Codex — reads skills from `.agents/skills`... GitHub Copilot loads skills from `.github/skills/`... The broader agentic AI ecosystem is coordinated through the Agentic AI Foundation under the Linux Foundation, whose platinum members include AWS, Anthropic, Block, Google, Microsoft, and OpenAI."
- **Context:** La nota oficial de Anthropic confirma "We've published Agent Skills as an open standard for cross-platform portability (December 18, 2025)" y enlaza agentskills.io. Reduce lock-in pero fragmenta paths (`.agents/skills`, `.github/skills/`, `.claude/skills/`).
- **Confidence:** Alta (cruce Medium + oficial).

### Claim 8 — Snyk: 36.82% de skills auditadas (1,467 de 3,984) tienen al menos una falla de seguridad; 13.4% (534) con issue critico; 76 payloads maliciosos confirmados
- **Source:** Snyk — "ToxicSkills" (Beurer-Kellner, Kudrinskii, Milanta, et al.)
- **URL:** https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
- **Date:** 2026-02-05
- **Excerpt:** "13.4% of all skills, or 534 in total, all contain at least one critical-level security issue... over a third of the ecosystem is affected: 36.82% (1,467 skills) have at least one security flaw... we confirmed active threats through HITL: 76 malicious payloads designed for credential theft, backdoor installation, and data exfiltration."
- **Context:** Primer audit comprehensivo del ecosistema (corpus ClawHub + skills.sh). Cifras son del scanner mcp-scan de Snyk, calibrado a 0% falsos positivos sobre top-100 de skills.sh y 90-100% recall sobre maliciosas confirmadas.
- **Confidence:** Alta (research vendor con metodologia publicada; sesgo comercial declarado — Snyk vende la solucion).

### Claim 9 — Las skills heredan el permiso completo del agente: shell, FS read/write, credenciales en env, mensajeria, memoria persistente. Barrera de publicacion: un SKILL.md + cuenta GitHub de 1 semana. Sin code signing, sin review, sin sandbox por defecto
- **Source:** Snyk — ToxicSkills
- **URL:** https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
- **Date:** 2026-02-05
- **Excerpt:** "Unlike traditional packages that execute in isolated contexts, Agent Skills operate with the full permissions of the AI agent they extend... The barrier to publishing a new agent skill on ClawHub? A SKILL.md Markdown file and a GitHub account that's one week old. No code signing. No security review. No sandbox by default."
- **Context:** El nucleo del problema de supply-chain. "Higher privilege by default" + "prompt injection has no analog" + "persistence through memory" lo hacen peor que npm/PyPI segun Snyk.
- **Confidence:** Alta.

### Claim 10 — Las skills permiten prompt injections "trivialmente simples": cada linea se interpreta como instruccion, asi que las defensas que detectan "instrucciones en datos" no aplican (todo el skill ES instruccion)
- **Source:** arXiv 2510.26328 — Schmotz, Abdelnabi, Andriushchenko (ELLIS/MPI/Tubingen)
- **URL:** https://arxiv.org/html/2510.26328v1
- **Date:** 2025-10-24
- **Excerpt:** "every line of Agent Skills is typically interpreted as an instruction, so prompt injections are particularly easy to execute... prompt injection defenses that are based on simply detecting instructions in data are, by definition, not valid as Agent Skills are all instructions."
- **Context:** Diferencia estructural respecto a injection en emails/webs (que requiere optimizacion iterativa). Paper academico, peer-context, no vendor.
- **Confidence:** Alta (paper academico con experimentos reproducibles, codigo publicado).

### Claim 11 — Un approval "Don't ask again" benigno se transfiere a acciones cercanas pero daninas; el guardrail de aprobacion no aisla la accion maliciosa
- **Source:** arXiv 2510.26328
- **URL:** https://arxiv.org/html/2510.26328v1
- **Date:** 2025-10-24
- **Excerpt:** "a benign, task-specific approval with the 'Don't ask again' option can carry over to closely related but harmful actions... when the time comes around to uploading the updated presentation using our malicious script, the authorization is usually granted, and the upload happens without any further user interaction."
- **Context:** Demostrado en Claude Code editando un pptx: el skill malicioso llama un "backup script" que exfiltra a una API externa. En Claude Web el sandbox de red lo bloqueo (solo permitia trafico a package managers), pero adaptaron el ataque a un URL malicioso en el output. Relevante para diseno de aprobaciones en produccion.
- **Confidence:** Alta.

### Claim 12 — Convergencia de tecnicas: 100% de skills maliciosas confirmadas contienen codigo malicioso y 91% ademas usan prompt injection para que el agente acepte ejecutar lo que un revisor humano rechazaria
- **Source:** Snyk — ToxicSkills
- **URL:** https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
- **Date:** 2026-02-05
- **Excerpt:** "100% of confirmed malicious skills contain malicious code patterns, while 91% simultaneously employ prompt injection techniques... Prompt injections prime the agent to accept and execute malicious code that a human reviewer, or the agent's own safety mechanisms, would normally reject."
- **Context:** Confirma empiricamente la tesis del paper arXiv (injection trivial) a escala de ecosistema. Patrones observados: ZIP con password (evasion antivirus), base64/Unicode obfuscation, `curl|bash` desde infraestructura del atacante.
- **Confidence:** Alta.

### Claim 13 — Vectores indirectos: 17.7% de skills ClawHub hacen fetch de contenido de terceros (injection indirecta); 10.9% tienen secretos hardcodeados; 2.9% ejecutan dependencias remotas no verificables (`curl ... | source`) modificables por el atacante post-review
- **Source:** Snyk — ToxicSkills
- **URL:** https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
- **Date:** 2026-02-05
- **Excerpt:** "Skills that fetch untrusted third-party content represent 17.7% of ClawHub skills... Hardcoded secrets appear in 10.9% of all ClawHub skills... 2.9% of ClawHub skills... dynamically fetch and execute content from external endpoints at runtime... The published skill appears benign during review. But attackers can modify behavior at any time by updating the fetched content."
- **Context:** Critico para versionado/pinning: una skill puede pasar review y volverse maliciosa despues si depende de contenido remoto. El "skill author did nothing wrong" en injection indirecta — la skill legitima trae contenido envenenado.
- **Confidence:** Alta.

### Claim 14 — Observabilidad supera a evals en produccion: ~89% de equipos tienen observability vs 52% con evals implementados; no hay benchmark estandar de skills
- **Source:** LangChain — State of Agent Engineering (via WebSearch)
- **URL:** https://www.langchain.com/state-of-agent-engineering
- **Date:** 2026 (snapshot WebSearch jun 2026)
- **Excerpt:** "Nearly 89% of respondents have implemented observability for their agents, outpacing evals adoption at 52%... the practical unit of evaluation being 'which step failed, under which tool call, with which prompt version, retrieval context, latency, and cost?'"
- **Context:** El gap evals < observability indica que la industria aun no tiene como medir calidad de skills de forma estandar; se evalua por traces, no por score unico. [NO VERIFICADO] que exista un benchmark publico especifico para evaluar SKILL.md per se.
- **Confidence:** Media (encuesta de industria; cifra de adopcion, no especifica a skills).

### Claim 15 — Patrones multi-tenant para skills: silo (skill dedicada por tenant, max aislamiento, max mantenimiento), pool (skill compartida), bridge (infra comun invoca logica tenant-especifica en runtime)
- **Source:** AWS — "Building multi-tenant agents with Amazon Bedrock AgentCore" (via WebSearch)
- **URL:** https://aws.amazon.com/blogs/machine-learning/building-multi-tenant-agents-with-amazon-bedrock-agentcore/
- **Date:** 2026 (snapshot WebSearch jun 2026)
- **Excerpt (sintesis WebSearch):** "The silo pattern uses dedicated tenant-specific skills where each tenant's complete workflow... is embedded in isolated agent skills... The bridge pattern embeds common workflow steps such as authentication, logging, and error handling in shared agent skills that invoke tenant-specific skills at runtime for business-critical logic."
- **Context:** Util como taxonomia de aislamiento. AVISO: la misma fuente describe el tenant context fluyendo via custom HTTP headers — esto CONTRADICE la regla MWT "tenant NUNCA via headers de cliente". Tratar la guia AWS como referencia de patrones, no como prescripcion de transporte de tenant. [NO VERIFICADO via fuente primaria — resumen de WebSearch, no fetch directo del articulo AWS].
- **Confidence:** Media-baja (sintesis de buscador, no fetch verificado linea a linea).

---

## TRADEOFFS

### T1 — Skill vs Subagente (costo / aislamiento)
- **Evidencia:** Skills augmentan un agente existente sin crear contexto nuevo; subagentes son contexto aislado independiente con sus propios tools (Claim 5, 6). Carrere: "A subagent is a fully independent agent with its own model, tools, and conversation history. A skill is lighter: it augments an existing agent's behavior without creating a new execution context."
- **Lectura:** Skill = barato, comparte contexto -> NO aisla. Subagente = caro (contexto separado) pero aisla permisos y conversacion. **Para multi-tenant esto es decisivo:** una skill compartida que ejecuta logica de tenant A corre en el mismo contexto que datos de tenant B. El aislamiento real lo da el subagente o el sandbox de proceso (MCP), no la skill.

### T2 — Determinismo (script) vs Flexibilidad (LLM)
- **Evidencia:** "because code is deterministic, this workflow is consistent and repeatable" (Anthropic, Claim 4) vs "Skills are not deterministic. Because an LLM interprets the instructions, there is inherent non-determinism" (Carrere, Claim 5).
- **Lectura:** Lo critico/regulado va en script (deterministico, auditable, testeable); lo flexible/contextual va en el cuerpo Markdown. El error de produccion es poner reglas de compliance solo en prose Markdown — el LLM puede "interpretarlas" distinto cada vez. Multi-tenant: filtros `tenant_id`, RLS y validaciones de visibilidad NUNCA en prose; van en codigo determinista fuera del SKILL.md.

### T3 — Portabilidad open-standard vs Lock-in
- **Evidencia:** Estandar abierto bajo Linux Foundation, adoptado por OpenAI/Microsoft/Google/Cursor/Goose (Claim 7). Pero cada plataforma usa paths distintos (`.claude/skills`, `.agents/skills`, `.github/skills/`).
- **Lectura:** Ganas portabilidad de la skill (un SKILL.md corre en varios runtimes) a costa de fragmentacion operativa (discovery, packaging y permisos difieren por plataforma). El frontmatter portable minimo: `name`, `description`; `version` va en `metadata` (no top-level) para max portabilidad. Lock-in se mueve del formato al runtime/governance.

### T4 — Progressive disclosure (eficiencia de contexto) vs Latencia de carga
- **Evidencia:** Metadata ~100 tokens/skill al arranque; cuerpo solo al activarse; recursos via bash bajo demanda (Claim 2, 3). Carga del cuerpo y de archivos referenciados ocurre via lecturas de filesystem en runtime.
- **Lectura:** Ahorras tokens permanentes (10x segun Carrere) pero pagas saltos de I/O en runtime (leer SKILL.md, luego forms.md, luego correr script). Para modelos locales pequenos, la fuente Carrere lo llama "architectural necessity"; para cloud, es optimizacion. El costo no desaparece, se difiere y se vuelve latencia condicional a la tarea.

### T5 — Seguridad supply-chain vs Velocidad de adopcion
- **Evidencia:** Crecimiento 10x en semanas (Snyk: de <50 a >500 submissions/dia ene-feb 2026) con barrera de publicacion casi nula y sin sandbox (Claim 9); 36.82% con fallas (Claim 8); injection trivial (Claim 10). Anthropic mismo recomienda: "installing skills only from trusted sources... thoroughly audit it before use."
- **Lectura:** La velocidad de adopcion del ecosistema va por delante de su seguridad — exactamente el patron npm/PyPI 2015-2020 que cita Snyk, "except with unprecedented access to credentials." En produccion multi-tenant, adoptar skills de marketplace al ritmo del ecosistema = aceptar 1-en-8 probabilidad de issue critico. El tradeoff se resuelve a favor de seguridad: allowlist propia, no marketplace abierto.

---

## LO QUE ESTA SIN RESOLVER

1. **Governance/seguridad de skills de terceros.** No hay code signing, review obligatorio ni sandbox por defecto (Claim 9). Snyk y arXiv coinciden en que el escaneo con LLM "inherits the scanner's own jailbreak surface" (arXiv) — el escaneo automatico es paliativo, no solucion. Sin estandar de attestation/firma, confiar en una skill de tercero es un acto de fe auditado a mano.

2. **Evals estandarizados.** No existe benchmark publico para evaluar la calidad de un SKILL.md como artefacto. La industria evalua por traces y observability (89%), no por evals (52%) (Claim 14). [NO VERIFICADO] que haya un harness estandar de skills comparable a SWE-bench.

3. **Versionado / dependencias entre skills.** `version` ni siquiera es campo top-level del spec (va en `metadata`). No hay resolucion de dependencias entre skills ni lockfile. Peor: skills con dependencias remotas pueden mutar post-review (Claim 13). El pinning a commit-hash es recomendacion manual, no garantia del estandar.

4. **Multi-tenancy de skills.** Las skills comparten el contexto del agente (Claim 6) — no hay aislamiento nativo per-tenant. Los patrones silo/pool/bridge (Claim 15) son de AWS, no del estandar, y la fuente arrastra el antipatron de tenant-via-headers. Overrides per-tenant (que skill esta enabled, con que tools) no tienen mecanismo estandar; cada plataforma lo improvisa.

5. **Determinismo en produccion.** El cuerpo Markdown es interpretado por LLM -> no determinista (Claim 5). El unico determinismo viene de los scripts (Claim 4). No hay forma estandar de declarar "esta seccion DEBE ejecutarse como codigo, no interpretarse". El `allowed-tools` es experimental.

---

## RECOMENDACION

**[RECOMENDACION — juicio del analista]**

Derivada de la evidencia: las skills dan eficiencia de contexto real (Claims 2-3) y consistencia via scripts (Claim 4), pero NO dan aislamiento (Claim 6/T1) ni seguridad por defecto (Claims 8-13). Para una plataforma multi-tenant en produccion, la conclusion prescriptiva es: **adoptar el patron SKILL.md solo como capa de conocimiento interno gobernado, nunca como canal de instalacion abierto.** Orden concreto:

**Fase 0 — Guardrails ANTES de la primera skill (no negociable).**
Porque Claims 9-13 demuestran explotacion activa y barrera de entrada nula. Construir primero:
- **Registry interno allowlisted.** Cero instalacion desde ClawHub/skills.sh. Toda skill entra por PR con review humano + escaneo (mcp-scan u equivalente). Deriva de Claim 8/9 y de la propia recomendacion de Anthropic ("trusted sources... audit before use").
- **Pin obligatorio a commit-hash y prohibicion de fetch remoto en runtime** (`curl|bash`, `| source`, dependencias externas). Deriva directo de Claim 13 (mutacion post-review).
- **Hardening de aprobaciones:** prohibir "Don't ask again" para acciones de red/exfiltracion; aprobacion debe ser por-accion, no por-categoria. Deriva de Claim 11.
- **Sandbox de red allowlist por defecto** (como hizo Claude Web en el paper, que bloqueo el backup script). Deriva de Claim 11.

**Fase 1 — Primeras skills a construir (las que codifican TUS reglas, no las del mercado).**
Construir skills internas que conviertan vuestras reglas inquebrantables en procedimiento repetible:
1. **`tenant-guard` (skill + script determinista).** Todo lo de aislamiento — filtro `tenant_id`, validacion RLS, chequeo de visibilidad (PUBLIC/PARTNER_B2B/INTERNAL/CEO-ONLY) — va en SCRIPT, no en prose (deriva de T2: compliance nunca interpretado por LLM). Primero porque es vuestro riesgo #1 y porque el estandar no lo resuelve (No-Resuelto #4).
2. **`kb-curation` y `sync-indexa`.** Codifican el flujo Cowork->generated_staging->sync_*_indexa.ps1 que ya teneis como conocimiento procedimental — caso de uso canonico de skills ("if you explain the same thing repeatedly, write a skill", Medium Google Cloud). Bajo riesgo, alto retorno de consistencia.
3. **`skill-review` (meta-skill de seguridad).** Skill que checa SKILL.md entrantes contra el taxonomy de Snyk (injection, secrets, suspicious download, unverifiable deps). Deriva de Claim 8/12; es vuestro gate de supply-chain interno.

**Fase 2 — Skills de dominio operativo** (Helium 10, SP-API, n8n workflows) una vez que el gate de Fase 0 esta probado. Empaquetar la logica determinista (queries, transforms) en scripts; dejar solo lo contextual en Markdown.

**Multi-tenancy — decision arquitectonica prescriptiva:**
- Para logica critica de negocio por tenant, **usar subagente o MCP server por tenant (aislamiento de proceso), NO skill compartida** (deriva de T1/Claim 6: la skill comparte contexto, no aisla).
- Skills compartidas (pool) solo para conocimiento generico no sensible. Logica tenant-especifica via patron bridge, pero **el tenant_id fluye por context server-side, NUNCA por headers de cliente** — explicitamente rechazando el antipatron de la guia AWS (Claim 15) por contradecir vuestra regla multi-tenant.
- Overrides per-tenant (que skills enabled) en su propio scope, no filtrables a otros tenants (consistente con vuestras reglas existentes).

**Por que este orden y no "adoptar skills del marketplace ya":** porque la evidencia (Claims 8-13) muestra que el ecosistema esta bajo ataque activo con 1-en-8 probabilidad de issue critico, y porque las skills NO aislan tenants por diseno (Claim 6). Construir guardrails + skills internas primero convierte un vector de supply-chain en un activo de governance auditable. El valor de las skills para vosotros es interno (consistencia, eficiencia de contexto, auditabilidad en Git), no la libreria publica.

---

*Notas de verificacion:* Claims 1,2,4 = docs oficiales Anthropic (alta). Claims 8,9,12,13 = Snyk research (alta, sesgo vendor declarado). Claims 10,11 = paper arXiv academico (alta). Claims 3,5,6,7 = Medium (media-alta, cruzados con oficiales donde posible). Claim 14 = encuesta LangChain via WebSearch (media). Claim 15 = sintesis WebSearch de AWS, NO fetch directo (media-baja, marcado [NO VERIFICADO] en transporte de tenant). [NO VERIFICADO] adicional: inexistencia de benchmark estandar de skills (No-Resuelto #2) es ausencia de evidencia, no evidencia de ausencia.
