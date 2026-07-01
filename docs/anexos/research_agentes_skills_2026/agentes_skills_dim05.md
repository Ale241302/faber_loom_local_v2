# Agent Skills 2026 — Dim05: Ecosistema / Marketplaces

Investigacion sobre como se distribuyen, versionan e instalan las Agent Skills (patron SKILL.md) y los plugins que las empaquetan. SKILL.md paso de feature de Claude Code (dic 2025) a estandar abierto adoptado por 32+ herramientas en 90 dias, con marketplaces tipo skills.sh (90k+ skills) y ClawHub creciendo mas rapido que npm. El lado oscuro: un supply chain inseguro by-design donde Snyk midio 36.82% de skills con fallas y campanas de malware activas. Fuentes primarias Medium-tier + Snyk + Linux Foundation + docs GitHub para verificar cifras.

---

## 1. Que es un Agent Skill y como se empaqueta

**Claim:** Un skill es un directorio con un archivo SKILL.md (YAML frontmatter + Markdown); sin runtime, sin servidor, sin build step, versionable en git junto al codigo.
**Source:** Paperclipped (de) — "Agent Skills as an Open Standard"
**URL:** https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/
**Date:** 2026-03-23
**Excerpt:** "The entire specification defines one thing: a directory containing a `SKILL.md` file with YAML frontmatter. That is the mandatory surface area... No runtime. No server. No build step. No package manager required. Just directories and Markdown files that you can version-control alongside your code in git."
**Context:** El frontmatter solo exige `name` (max 64 chars) y `description` (max 1,024 chars). Campos opcionales: `license`, `compatibility`, `metadata`, `allowed-tools` (experimental). Modelo de progressive disclosure de 3 niveles (~100 tokens por skill al arranque).
**Confidence:** high

---

## 2. Plugins de Claude Code: que empaquetan (skills + MCP + slash commands + hooks)

**Claim:** Un plugin de Claude Code agrupa skills, MCP servers, slash commands y hooks bajo un solo paquete; el marketplace es un repo GitHub que distribuye muchos plugins.
**Source:** WebSearch (claudemarketplaces.com / cased/claude-code-plugins, sintetizado)
**URL:** https://github.com/cased/claude-code-plugins
**Date:** 2026 (consultado 2026-06-01)
**Excerpt:** "A skill is a single instruction set, a plugin bundles multiple skills, MCP servers, or commands, and a marketplace is a GitHub repo that distributes many plugins under one registry."
**Context:** Jerarquia clave: skill (unidad) < plugin (bundle) < marketplace (registry GitHub). Relevante para el modelo multi-tenant: un plugin puede ser el contenedor de overrides per-tenant (skills habilitadas + MCP + slash commands).
**Confidence:** medium

---

## 3. Slash commands fusionados al sistema de Skills

**Claim:** Los slash commands se fusionaron al sistema de Skills; un archivo `.claude/commands/review.md` crea `/review`. Commands = prompt templates invocados por usuario; skills = pueden auto-activarse por contexto.
**Source:** WebSearch (morphllm — Claude Code Skills vs MCP vs Plugins, sintetizado)
**URL:** https://www.morphllm.com/claude-code-skills-mcp-plugins
**Date:** 2026 (consultado 2026-06-01)
**Excerpt:** "Slash commands are templates for frequently-used prompts, and have been merged into the Skills system—a file at .claude/commands/review.md creates /review. Commands are simple prompt templates, always user-invoked, while skills can include scripts, resources, and auto-trigger based on context."
**Context:** Distincion operativa: para shortcuts simples usar commands; para logica compleja con scripts/recursos usar skills. Importante para diseno de superficie de agentes (configurar vs iterar).
**Confidence:** medium

---

## 4. Skills vs MCP: capas complementarias, no competidoras

**Claim:** MCP da acceso estructurado a APIs/datos externos ("que puede acceder el agente"); Skills empaquetan conocimiento procedural ("como debe trabajar el agente"). Son capas complementarias.
**Source:** Paperclipped (de)
**URL:** https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/
**Date:** 2026-03-23
**Excerpt:** "MCP provides structured API access to external tools and data sources. Agent Skills package procedural knowledge... MCP answers 'what can I access?' Skills answer 'how should I work?' They are complementary layers, and this meant Agent Skills did not compete with any vendor's existing protocol investments."
**Context:** Stack emergente: MCP (acceso a herramientas) + A2A (comunicacion agente-agente) + Agent Skills (conocimiento procedural) + AGENTS.md (config de proyecto). Solo Skills requiere cero infraestructura.
**Confidence:** high

---

## 5. SKILL.md como estandar abierto: publicado dic 2025, adoptado en 48h

**Claim:** Anthropic publico la spec Agent Skills el 18-dic-2025; en 48h Microsoft la integro en VS Code y OpenAI en ChatGPT y Codex CLI.
**Source:** Paperclipped (de)
**URL:** https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/
**Date:** 2026-03-23
**Excerpt:** "Anthropic published the Agent Skills specification on December 18, 2025. Within 48 hours, Microsoft integrated it into VS Code and OpenAI added it to both ChatGPT and Codex CLI."
**Context:** El repo anthropics/skills se creo el 22-sep-2025; OpenAI ya habia mergeado "feat: experimental support for skills.md" en Codex CLI antes del anuncio oficial. El repo cruzo 100K stars.
**Confidence:** high

---

## 6. Adopcion cross-plataforma: 32 herramientas en 90 dias

**Claim:** A marzo 2026, 32 herramientas soportan Agent Skills, incluyendo Google (Gemini CLI), JetBrains (Junie), AWS (Kiro), Block (Goose), Sourcegraph (Amp), Snowflake, Databricks, ByteDance, Mistral AI y Spring AI.
**Source:** Paperclipped (de)
**URL:** https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/
**Date:** 2026-03-23
**Excerpt:** "By March 2026, 32 tools from competing companies, including Google's Gemini CLI, JetBrains' Junie, AWS's Kiro, and Block's Goose, all read the same `SKILL.md` files from the same directory structure... This is the fastest cross-vendor standardization event in AI tooling."
**Context:** Un skill escrito para Codex corre sin modificacion en Claude Code, Cursor, Gemini CLI, GitHub Copilot. Block corre 100+ skills internas en Goose. Razon de adopcion: spec implementable en un dia + efecto de red.
**Confidence:** high

---

## 7. Discrepancia en paths de instalacion (la portabilidad no es total)

**Claim:** La spec define el formato del archivo pero NO el path de instalacion: Claude Code lee de `.claude/skills/`, OpenAI Codex de `.agents/skills/`, Google de `~/.gemini/antigravity/skills/`.
**Source:** Paperclipped (de) citando a Simon Willison
**URL:** https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/
**Date:** 2026-03-23
**Excerpt:** "Different tools implement discovery differently: Claude Code reads from `.claude/skills/`, OpenAI Codex from `.agents/skills/`, Google's tools from `~/.gemini/antigravity/skills/`. The spec defines the file format but not the installation path, which means skills work across tools but installation methods do not."
**Context:** Simon Willison llamo la spec "quite heavily under-specified" en metadata y `allowed-tools`. Implicacion multi-tenant: el path de skills es un punto de configuracion per-plataforma que la plataforma debe abstraer.
**Confidence:** high

---

## 8. Linux Foundation / Agentic AI Foundation (gobernanza neutral)

**Claim:** El 9-dic-2025 la Linux Foundation anuncio el Agentic AI Foundation (AAIF) con Anthropic, OpenAI y Block como founding members; MCP, AGENTS.md y Goose fueron proyectos iniciales. A feb-2026, 146 organizaciones miembro.
**Source:** Paperclipped (de), corroborado por Linux Foundation
**URL:** https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/
**Date:** 2026-03-23
**Excerpt:** "On December 9, nine days before the open standard release, the Linux Foundation announced the Agentic AI Foundation (AAIF) with Anthropic, OpenAI, and Block as founding members. MCP, AGENTS.md, and Goose were contributed as initial projects. By February 2026, AAIF had grown to 146 member organizations."
**Context:** [NO VERIFICADO que SKILL.md sea proyecto formal del AAIF] — los proyectos contribuidos confirmados son MCP, AGENTS.md y Goose; SKILL.md/Agent Skills NO aparece explicitamente como proyecto AAIF en las fuentes. La resolucion de seguridad del supply chain "probablemente vendra del AAIF" (verified publisher, provenance) pero a marzo 2026 sigue en fase "move fast".
**Confidence:** medium

---

## 9. skills.sh — directorio oficial de Vercel (lanzado 20-ene-2026)

**Claim:** Vercel lanzo skills.sh el 20-ene-2026 como directorio y leaderboard oficial; soporta 19 agentes IA y rastrea install counts reales. Lista 89,753 / 90,000+ skills.
**Source:** Virtual Uncle (Medium-tier) + Paperclipped
**URL:** https://virtualuncle.com/agent-skills-marketplace-skills-sh-2026/
**Date:** 2026-03-25 (pub) / actualizado 2026-04-14
**Excerpt:** "Vercel launched skills.sh on January 20, 2026 as the official directory and leaderboard for agent skill packages... Skills.sh supports 19 different AI agents including Claude Code, Cursor, Codex, GitHub Copilot, Windsurf, Gemini, and more. It tracks actual install counts."
**Context:** Top skills por installs (marzo 2026): find-skills (Vercel Labs, 579k+), vercel-react-best-practices (216k+), web-design-guidelines (171k+), frontend-design (Anthropic, 164k+), remotion-best-practices (150k+), azure-ai (Microsoft, 137k+). Modelo de distribucion estilo npm: el skill mete el producto en el "dependency tree" del dev.
**Confidence:** high

---

## 10. Marketplaces competidores y fragmentacion

**Claim:** El ecosistema se fragmento rapido: SkillsMP (500k+ skills, filtro minimo de 2 stars), SkillHub (~7k, AI-evaluadas S/A/B), agentskill.sh (44k+, scanning de 2 capas), LobeHub (100k+), SkillsDirectory (50+ reglas automatizadas), awesome-agent-skills (lista curada GitHub).
**Source:** Virtual Uncle
**URL:** https://virtualuncle.com/agent-skills-marketplace-skills-sh-2026/
**Date:** 2026-03-25
**Excerpt:** "SkillsMP is the biggest by raw numbers with over 500,000 skills aggregated from GitHub... agentskill.sh sits at 44,000+ skills and runs two-layer security scanning on everything... SkillsDirectory runs automated security analysis on every skill using 50+ rules covering prompt injection, credential theft, data exfiltration, and malware."
**Context:** Todos usan el mismo estandar SKILL.md, asi que un skill corre en todos; la diferencia es curacion y vetting de seguridad. ClawHub es el marketplace especifico de OpenClaw (distinto de skills.sh).
**Confidence:** medium

---

## 11. Claude plugin marketplace — lanzamiento oficial (feb 2026, no exactamente feb pero verificado)

**Claim:** Anthropic publico su marketplace oficial de plugins de Claude Code el 20-feb-2026; el directorio claude-plugins-official cataloga 55+ plugins curados.
**Source:** WebSearch (gHacks + claudemarketplaces.com, sintetizado)
**URL:** https://www.ghacks.net/2026/02/25/anthropic-expands-claude-with-enterprise-plugins-and-marketplace/
**Date:** 2026-02-25
**Excerpt:** "Anthropic launched its official Claude Code plugin directory in early 2026, with the marketplace published on February 20, 2026... The official claude-plugins-official marketplace catalogs 55+ curated plugins, while the broader community ecosystem adds 72+ more."
**Context:** NOTA DE VERIFICACION SOBRE FECHA: el usuario pidio verificar "plugin marketplace feb 2026". Confirmado: el directorio OFICIAL gestionado por Anthropic se publico ~20-feb-2026, "less than a month after Anthropic first introduced plugins". Los plugins como feature aparecieron antes (ene 2026). Anthropic open-source 11 plugins de produccion bajo anthropics/knowledge-work-plugins (17.3K stars).
**Confidence:** medium

---

## 12. Versionado y pinning de plugins (commit SHA)

**Claim:** El campo `version` en marketplace.json es opcional pero load-bearing: si se omite, el commit SHA es la version (cada push = release). Al instalar, Claude Code graba el commit hash y no vuelve a chequear; `/plugin marketplace update` solo refresca el catalogo, no los plugins instalados.
**Source:** WebSearch (Claude Code Docs + workingbruno.com, sintetizado)
**URL:** https://code.claude.com/docs/en/plugin-marketplaces
**Date:** 2026 (consultado 2026-06-01)
**Excerpt:** "When you install a plugin, Claude Code records the commit hash at that moment and never checks again. The `/plugin marketplace update` command refreshes the marketplace catalogue, not your installed plugins, which stay pinned to whatever commit they had when installed... Plugin source supports both ref (branch/tag) and sha (exact commit)."
**Context:** El campo `source` de cada plugin soporta `ref` (branch/tag) y `sha` (commit exacto). Skills dentro de un plugin se exponen con namespacing tipo `/quality-review-plugin:hello` para evitar colisiones. Existe issue abierto (#33653, #10571) pidiendo pin a SHA mas robusto via marketplace.json. Critico para reproducibilidad en produccion multi-tenant.
**Confidence:** medium

---

## 13. Instalacion de skills via CLI

**Claim:** Se instala un skill con `npx skills add owner/repo`; para Claude Code se clona en `.claude/skills` (proyecto) o `~/.claude/skills` (global). Carga automatica cuando el agente detecta relevancia, sin build ni config.
**Source:** Virtual Uncle
**URL:** https://virtualuncle.com/agent-skills-marketplace-skills-sh-2026/
**Date:** 2026-03-25
**Excerpt:** "Run npx skills add owner/repo in your terminal to install any skill from a supported marketplace. For project-specific installation, clone the repo into your .claude/skills directory. For global installation across all projects, clone into ~/.claude/skills. Skills load automatically when your agent detects they are relevant. No build steps or configuration files are needed."
**Context:** Recomendacion de seguridad: usar el campo `allowed-tools` cuando este disponible para limitar el blast radius; preferir skills con 1,000+ installs de autores conocidos.
**Confidence:** high

---

## 14. obra/superpowers — framework de skills + marketplace

**Claim:** Superpowers (obra) es un framework de skills componibles + metodologia de desarrollo; se instala con `/plugin install superpowers@claude-plugins-official` y aporta 20+ skills battle-tested (TDD, debugging, /brainstorm, /write-plan, /execute-plan).
**Source:** WebSearch (github.com/obra/superpowers, sintetizado)
**URL:** https://github.com/obra/superpowers
**Date:** 2026 (consultado 2026-06-01)
**Excerpt:** "Superpowers is available via the official Claude plugin marketplace and can be installed with: /plugin install superpowers@claude-plugins-official... providing 20+ battle-tested skills with /brainstorm, /write-plan, /execute-plan commands."
**Context:** Superpowers corre cross-plataforma (Claude Code, Codex CLI/App, Factory Droid, Gemini CLI, OpenCode, Cursor, GitHub Copilot CLI). Su marketplace (obra/superpowers-marketplace) agrupa plugins por categoria (Testing, Debugging, Collaboration, Meta). Ejemplo de como un autor independiente empaqueta y distribuye.
**Confidence:** medium

---

## 15. SEGURIDAD SUPPLY CHAIN — Snyk ToxicSkills (cifras concretas)

**Claim:** Snyk escaneo 3,984 skills de ClawHub y skills.sh (5-feb-2026): 13.4% (534) con al menos un issue CRITICAL; 36.82% (1,467) con al menos una falla de seguridad; 76 payloads maliciosos confirmados; 8 skills maliciosas seguian live en ClawHub a la publicacion.
**Source:** Snyk — ToxicSkills (oficial, complementa Medium)
**URL:** https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
**Date:** 2026-02-05
**Excerpt:** "13.4% of all skills, or 534 in total, all contain at least one critical-level security issue... over a third of the ecosystem is affected: 36.82% (1,467 skills) have at least one security flaw... we confirmed active threats through HITL: 76 malicious payloads designed for credential theft, backdoor installation, and data exfiltration."
**Context:** El titular "prompt injection in 36%" del articulo se refiere a "any security flaw" (36.82%), NO solo a prompt injection. 100% de skills maliciosas confirmadas contienen codigo malicioso; 91% combinan prompt injection con malware tradicional. Submissions diarias saltaron de <50 (mediados ene) a >500 (inicios feb) = 10x.
**Confidence:** high

---

## 16. SEGURIDAD — privilegios heredados y barrera de publicacion nula

**Claim:** Una skill hereda los permisos completos del agente: shell access, read/write al filesystem, credenciales en env vars/config, capacidad de enviar mensajes, memoria persistente. La barrera para publicar en ClawHub: un SKILL.md y una cuenta GitHub de una semana. Sin code signing, sin review, sin sandbox by default.
**Source:** Snyk — ToxicSkills
**URL:** https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
**Date:** 2026-02-05
**Excerpt:** "Unlike traditional packages that execute in isolated contexts, Agent Skills operate with the full permissions of the AI agent they extend... The barrier to publishing a new agent skill on ClawHub? A `SKILL.md` Markdown file and a GitHub account that's one week old. No code signing. No security review. No sandbox by default."
**Context:** Taxonomia de 8 politicas (prompt injection, malicious code, suspicious download, credential handling, secret detection, third-party content, unverifiable dependencies, direct money access). Detectores CRITICAL logran 90-100% recall en maliciosas con 0% falsos positivos en top-100 de skills.sh.
**Confidence:** high

---

## 17. SEGURIDAD — secretos hardcodeados y dependencias no verificables

**Claim:** Secretos hardcodeados en 10.9% de skills de ClawHub (32% en muestras maliciosas confirmadas). 2.9% de skills de ClawHub (21% de maliciosas) ejecutan dinamicamente contenido de endpoints externos en runtime (curl | bash). Third-party content exposure: 17.7% de ClawHub, 9% del top-100 de skills.sh.
**Source:** Snyk — ToxicSkills
**URL:** https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
**Date:** 2026-02-05
**Excerpt:** "Hardcoded secrets appear in 10.9% of all ClawHub skills and 32% of confirmed malicious samples... 2.9% of ClawHub skills and 21% of malicious samples dynamically fetch and execute content from external endpoints at runtime... The published skill appears benign during review. But attackers can modify behavior at any time by updating the fetched content."
**Context:** Indirect prompt injection via third-party content: el autor del skill no hizo nada malo, el usuario instalo un skill popular, pero el agente se compromete al traer contenido envenenado. Herramienta de defensa: `uvx mcp-scan@latest --skills` (open source, motor mcp-scan de Invariant Labs).
**Confidence:** high

---

## 18. SEGURIDAD — campana ClawHavoc y attack success rate

**Claim:** 341 skills hostiles trazadas a una sola campana coordinada "ClawHavoc" que entrego el infostealer Atomic Stealer (AMOS) para macOS. Research (arxiv feb-2026) encontro hasta 80% de attack success rate con modelos frontier ante skill-based attacks.
**Source:** Paperclipped (de) + Virtual Uncle
**URL:** https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/
**Date:** 2026-03-23
**Excerpt:** "Snyk's ToxicSkills study scanned 3,984 skills... 341 hostile skills were traced to a single coordinated campaign called 'ClawHavoc' that delivered the Atomic Stealer (AMOS) macOS infostealer... Akamai's threat analysis lists skill poisoning as a top-10 threat vector for agentic AI in 2026."
**Context:** Virtual Uncle reporta "over 335 malicious skills shared a single command-and-control IP" y "up to 80% attack success rate with frontier models" (arxiv 2602.20156). [NO VERIFICADO: la cifra exacta 341 vs 335 difiere entre fuentes — rango ~335-341]. Akamai cataloga skill poisoning como top-10 threat 2026.
**Confidence:** medium

---

## 19. Datos de calidad del ecosistema (no solo seguridad)

**Claim:** El Agent Skill Report analizo 673 skills: 22% fallan validacion estructural; 52% de tokens en repos de skills son archivos no-estandar (LICENSE, build artifacts) que desperdician context window. Analisis arxiv de 40,285 skills: skill mediano = 1,414 tokens, 90% bajo 3,935 tokens.
**Source:** Paperclipped (de)
**URL:** https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/
**Date:** 2026-03-23
**Excerpt:** "The Agent Skill Report analyzed 673 skills and found that 22% fail structural validation... 52% of all tokens in skill repositories are non-standard files... The arxiv analysis of 40,285 publicly listed skills found that the median skill is 1,414 tokens (mean: 1,895). 90% are under 3,935 tokens."
**Context:** Degradacion conductual medible: skills mal escritas degradan el rendimiento base via template propagation (-0.483), token budget competition (-0.384), architectural pattern bleed (-0.317). Instalar un skill malo no solo no ayuda, daña activamente tareas no relacionadas. Relevante para curacion de KB en plataforma multi-tenant.
**Confidence:** medium

---

## Notas de verificacion y banderas

- **Fecha plugin marketplace:** CONFIRMADA — directorio oficial Anthropic ~20-feb-2026 (no exactamente "feb 2026" como mes redondo, pero dentro de feb). Plugins como feature: ene 2026.
- **[NO VERIFICADO] SKILL.md como proyecto formal del AAIF:** las fuentes confirman MCP, AGENTS.md y Goose como proyectos contribuidos al Agentic AI Foundation; NO confirman que Agent Skills/SKILL.md sea proyecto formal bajo gobernanza AAIF. La gobernanza de SKILL.md sigue de facto en agentskills.io (Anthropic).
- **[NO VERIFICADO] cifra exacta ClawHavoc:** 335 (Virtual Uncle) vs 341 (Paperclipped) skills hostiles — discrepancia menor entre fuentes, usar rango ~335-341.
- **[NO VERIFICADO] conteos de skills por marketplace:** las cifras de SkillsMP (500k+), LobeHub (100k+), SkillHub (~7k) vienen de un solo articulo (Virtual Uncle) sin corroboracion cruzada; tratar como ordenes de magnitud, no exactas.
- **Medium spillwave/Skilz:** el fetch de medium.com/spillwave-solutions/skilz devolvio vacio (paywall/JS); NO se pudo verificar su contenido. Excluido de claims.
- **Titular Snyk "36%":** aclarado — se refiere a "any security flaw" (36.82%), no a prompt injection aislado.

## Fuentes principales
- Snyk ToxicSkills (oficial): https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/ (2026-02-05)
- Paperclipped — Open Standard (Medium-tier): https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/ (2026-03-23)
- Virtual Uncle — skills.sh (Medium-tier): https://virtualuncle.com/agent-skills-marketplace-skills-sh-2026/ (2026-03-25)
- Linux Foundation AAIF: https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation
- Claude Code Docs — plugin marketplaces: https://code.claude.com/docs/en/plugin-marketplaces
- GitHub: anthropics/skills, obra/superpowers, skillmatic-ai/awesome-agent-skills, cased/claude-code-plugins
- gHacks — Anthropic enterprise plugins: https://www.ghacks.net/2026/02/25/anthropic-expands-claude-with-enterprise-plugins-and-marketplace/
