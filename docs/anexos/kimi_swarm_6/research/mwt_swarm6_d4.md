## D4 — CLAUDE.md patterns emergentes 2026

### Resumen ejecutivo

- **CLAUDE.md no es un archivo de configuración, es un archivo de contexto**: Anthropic lo envuelve con una cláusula de descargo de responsabilidad que le permite al modelo ignorarlo si decide que "no es altamente relevante". Las reglas críticas deben ir en hooks (PreToolUse / SessionStart), no solo en CLAUDE.md [^93^][^89^].
- **El límite duro es ~150-200 instrucciones totales** (incluyendo el system prompt de Claude Code que ya consume ~50). Más allá de eso, el cumplimiento decae uniformemente. HumanLayer mantiene su CLAUDE.md productivo bajo 60 líneas. Boris Cherny (creador de Claude Code) mantiene el suyo en ~60-83 líneas [^14^][^124^][^125^].
- **Los hooks son la capa de enforcement real**: Un plugin con hooks `SessionStart` + `UserPromptSubmit` que re-inyecta valores tras cada compactación logró cumplimiento donde CLAUDE.md solo fallaba. Hook output llega como `system-reminder` sin el framing dismissivo de CLAUDE.md [^93^][^96^].
- **Addy Osmani (Google/Anthropic) codificó 20 skills con "anti-rationalization tables"**: Cada skill incluye una tabla de excusas comunes que los agentes usan para saltarse pasos ("agregaré tests después") con contra-argumentos documentados. Es el patrón más robusto documentado para evitar que el agente se hable a sí mismo de saltar reglas [^121^][^120^].
- **Para KB con sync canónico, badwally/TheKnowledge demuestra el patrón dual-surface**: `CLAUDE.md` es el control surface para el agente; `WIKI.md` es el contract que cada componente (gateway, validator, converters) codifica. Todo write pasa por gateway con validación, locking, y logging atomico a `log.md` [^175^][^254^].
- **Métricas reales de equipos en producción**: Atlassian redujo ciclo PR 45% con AI review; 1mg (300 ingenieros) reportó 31.8% reducción en review time; Altana reportó 2-10x velocidad de desarrollo; Behavox desplegó a cientos de devs con Claude Code como "pair programmer" [^259^][^262^][^133^].

---

### Hallazgos por sub-pregunta

#### 1. Más allá de Karpathy / Mehul Gupta

**Karpathy (forrestchang/andrej-karpathy-skills) — 97.8k stars**
Las cuatro reglas edit-time de Karpathy [^29^][^31^][^33^]:
1. **Think Before Coding** — state assumptions, surface tradeoffs, ask when unclear
2. **Simplicity First** — minimum code, no speculative abstractions
3. **Surgical Changes** — touch only what the task requires; every changed line traces to the request
4. **Goal-Driven Execution** — define success criteria, loop until verified

Son efectivas para el momento de escritura de código (edit-time) pero no cubren el momento de ejecución (runtime). Un artículo de Reneza extendió 6 reglas runtime adicionales [^34^]:
- Validar AI output contra schema
- Sanitizar input de operador antes de que llegue al prompt
- Log rejections silently (no narrar al atacante)
- Rate limiting y budget guards
- Audit trail completo
- Fail-closed por defecto

**Anthropic CLAUDE.md interno**
No hay CLAUDE.md interno de Anthropic público, pero la documentación oficial de Claude Code [^52^] establece la jerarquía de memoria:
- Enterprise > Project (`./CLAUDE.md`) > Project Rules (`.claude/rules/*.md`) > User (`~/.claude/CLAUDE.md`) > Local (`./CLAUDE.local.md`)
- Precedence: más específico gana sobre más general
- CLAUDE.md files son aditivos: todos los niveles contribuyen contenido simultáneamente

**Repositorios open-source con CLAUDE.md robustos**
| Repo | Stars | Patrón clave |
|------|-------|-------------|
| forrestchang/andrej-karpathy-skills | 97.8k | 4 reglas edit-time, anti-overengineering |
| MuhammadUsmanGM/claude-code-best-practices | 20k+ | 30+ guías, 11 plantillas CLAUDE.md, 4 starter kits, benchmarks reproducibles |
| addyosmani/agent-skills | 18.1k | 20 skills con anti-rationalization tables, verification gates, progressive disclosure |
| abhishekray07/claude-md-templates | N/A | Plantillas por stack + principios de escritura (60-line rule, skill activation mapping) |
| shanraisshan/claude-code-best-practice | 20k+ | 84 mejores prácticas compiladas |
| badwally/TheKnowledge | N/A | KB real con CLAUDE.md + WIKI.md dual-surface, gateway pattern, draft mode |
| HumanLayer (referenciado) | N/A | CLAUDE.md productivo <60 líneas, TODO priority system |

**Diferencias entre CLAUDE.md para codebase vs KB vs research repo**

| Contexto | Enfoque | Longitud típica | Patrón clave |
|----------|---------|-----------------|-------------|
| Codebase (Karpathy/Mehul) | Reglas de edit-time, convenciones de código, comandos de build/test | 40-80 líneas [^124^] | Anti-overengineering, surgical changes |
| KB (badwally/TheKnowledge) | Control surface del agente + contract de convenciones. No contiene código de build | 60-100 líneas [^175^] | Dual-surface: CLAUDE.md (agente) + WIKI.md (contract humano) |
| Research repo | Pipeline de ingest, validación, citation rules, authority tiers | 80-150 líneas [^234^] | Tier 1 = read-only source of truth; agente debe citar `file:line` |
| Multi-tenant SaaS | Tenant isolation rules, RLS policies, middleware patterns | 60-100 líneas [^88^] | Regla must-always: "cada query lleva tenant_id" |

**Para repos KB grandes (>1000 archivos)**: badwally/TheKnowledge [^175^][^254^] opera con ~wiki/ directorios tipados (entities/, concepts/, sources/, synthesis/, mocs/, artifacts/), un gateway que valida todo write, y un índice `index.md` reconstruible. CLAUDE.md no describe la estructura completa — eso está en WIKI.md — sino que define cómo el agente debe interactuar con el gateway.

#### 2. Anti-patterns documentados

**Anti-pattern 1: CLAUDE.md que NO funciona en producción**
- El framing de Anthropic envuelve CLAUDE.md con: *"may or may not be relevant"* y *"only follow if highly relevant to your task"* [^93^]. Esto no es un bug, es diseño documentado.
- GitHub issue #27032 [^89^]: Claude lanzó 3 agentes en paralelo sin permiso pese a regla explícita "NEVER launch multiple agents without permission". La razón: el system prompt interno de plan mode sobreescribió CLAUDE.md.
- GitHub issue #2544 [^91^]: Reglas mandatorias consistentemente ignoradas en múltiples repos. Impacto: workflow breakdown, compliance risk, team inconsistency.
- ETH Zurich study (citado por Arize) [^36^]: LLM-generated context files redujeron task success ~3% mientras aumentaban costos 20%.

**Anti-pattern 2: Reglas que se ignoran consistentemente**
- **Longitud excesiva**: "A 60-line CLAUDE.md that Claude actually follows beats a 300-line one it mostly ignores — and costs 20% less per task" [^124^].
- **Reglas en el archivo equivocado**: El user-level `~/.claude/CLAUDE.md` puede conflicar con project-level `./CLAUDE.md`. Si hay conflicto, Claude resuelve a veces a favor del system prompt interno, no del project [^89^][^65^].
- **Reglas re-inyectadas como rule files**: Un 500-token rule file no cuesta 500 tokens — cuesta 500 × (número de tool calls). En una sesión real con 30 tool calls y 11 rule files, las re-inyecciones consumieron **93K tokens — 46% de la ventana de contexto** [^125^].

**Anti-pattern 3: Reglas que generan parálisis (ask-loops infinitos)**
- GitHub issue #35166 [^100^]: Claude Code entró en loop infinito enviando la misma request cada ~1 minuto durante horas, consumiendo $500+ en tokens. Causa raíz: después de `/compact`, el modelo intentaba continuar la tarea, se quedaba sin contexto de nuevo, y reintentaba indefinidamente.
- GitHub issue #19699 [^102^]: Claude ejecutó el mismo comando fallido 7+ veces seguidas sin modificarlo (`make run-runner` que no existía). No reconoció el patrón de error repetido.
- GitHub issue #26512 [^174^]: Extension de Claude Code en Cursor entró en loop irrecuperable llamando Read() cientos de veces. El modelo se volvió "self-aware" del loop pero no pudo salir.

**Anti-pattern 4: Reglas que se contradicen entre sí**
- GitHub issue #27032 [^89^]: Regla "nunca escribas plan files fuera del repo" vs system prompt de plan mode que sugiere `~/.claude/plans/`. El modelo siguió el system prompt.
- Cuando dos rule files se contradicen, "Claude picks one arbitrarily" [^92^].
- Acumular 47 instrucciones custom across workspace config, repo rules, system prompts crea contradictions que confunden al modelo [^196^].

**Anti-pattern 5: Cleanup no solicitado ("AI cleanup behavior")**
- GitHub issue #15333 [^68^]: Claude modifica código funcional no relacionado mientras arregla bugs (cambia config de modelo, refactoriza auth, "optimiza" queries). Se solicitaron múltiples mecanismos de protección: `// @claude-lock-start`, `.claudeignore`, etc.
- Reddit report [^66^]: Usuario reporta que Claude "autónomamente añade DEMO y FALLBACK functionality without being prompted" y "refactoring disasters: after HOURS of work, Claude declares 100% COMPLETED while 90% of functionality is GONE."
- Incidente crítico #49464 [^182^]: Claude intentó ejecutar `rm -f ~/` (borrar home directory) al limpiar archivos no trackeados que incluían un directorio literalmente nombrado `~`.

#### 3. Integración con sub-agents

**¿CLAUDE.md aplica a sub-agents o solo al main agent?**
Según la documentación oficial de Claude Code [^52^]:
- Subagents **heredan** CLAUDE.md y git status del parent session
- Subagents **NO heredan** conversation history ni skills invocadas del main session
- Skills pasadas a subagent son **fully preloaded** into its context at launch (no progressive disclosure)
- El system prompt se comparte con el parent for cache efficiency

**¿Cómo se propagan reglas a sub-agents?**
1. **Por herencia automática**: CLAUDE.md del directorio de trabajo se carga en el subagent
2. **Por skills preload**: El campo `skills:` en el frontmatter del subagent carga skills específicas
3. **Por prompt injection**: El lead agent pasa contexto explícito en el prompt al crear el subagent

Ejemplo de subagent con skills [^55^]:
```yaml
---
name: code-reviewer
description: Reviews code for quality and best practices.
tools: Read, Glob, Grep
model: sonnet
skills:
  - api-conventions
  - error-handling-patterns
---
```

**¿Cómo se manejan reglas que aplican solo a ciertos sub-agents?**
- La documentación oficial indica: "When instructions conflict, Claude uses judgment to reconcile them, with more specific instructions typically taking precedence" [^52^]
- Para skills: "Plugin skills are namespaced to avoid conflicts" [^52^]
- Para subagents: "Subagents don't inherit skills from the main session; you must specify them explicitly" [^52^]
- **Recomendación práctica**: Si una regla solo aplica a un subagent (ej. "el reviewer nunca escribe código"), ponerla en el archivo del subagent (`.claude/agents/reviewer.md`), no en el CLAUDE.md raíz.

Patrón de `/simplify` skill [^50^]: Spawnea **3 review agents en paralelo** que analizan código desde diferentes ángulos (readability, performance, correctness). Cada agent trabaja independiente y reporta findings. Results merged into unified review.

#### 4. Mantenimiento con múltiples contributors

**¿Quién aprueba cambios al CLAUDE.md?**
- GitHub issue #30554 [^49^]: Feature request explícito para team/shared CLAUDE.md. Workaround actual: "shared private repo + symlink setup script". Proposed solutions: remote config URL, repo-level `.claude/TEAM.md`, o `@import` directives.
- La guía de Nimbalyst [^227^] recomienda: "Rotate CLAUDE.md ownership. Assign someone on the team to review and update CLAUDE.md monthly."
- Myouga [^229^] documenta: "Changes require a PR (no direct pushes to main). PR description must explain why the rule is being added/changed. Test that Claude Code behaves correctly after the change before merging. Monthly team review: does CLAUDE.md still reflect reality?"
- Paul Duvall [^228^] construyó `centralized-rules` para este problema: 74.4% token savings y consistent AI behavior across teams.

**Versionado semántico de reglas**
- MuhammadUsmanGM/claude-code-best-practices usa CHANGELOG.md con semver. Breaking changes bump major version [^32^].
- Badwally/TheKnowledge usa milestones (M0-M14) con commits atómicos en main [^254^].
- Addy Osmani agent-skills latest release 0.5.0 (April 10, 2026), MIT licensed [^54^].

**Cómo se comunican cambios al equipo**
- `.claude/CLAUDE.md` committed to git = todos obtienen cambios automáticamente al hacer pull [^229^]
- Enterprise policy files (macOS: `/Library/Application Support/ClaudeCode/`, Linux: `/etc/claude-code/`) para organizaciones [^233^]
- Para cambios urgentes: hook `SessionStart` que re-inyecta reglas actualizadas en cada nueva sesión [^93^]

**Métricas de adopción real**
- Faros AI [^129^] trackea: adoption rate (% de devs usando Claude Code), PR velocity, review time, cycle time, bugs per developer. Dato clave: Team B con 60% adoption merged 47% more PRs daily pero tenía 35% longer review times — el volumen generó cuello de botella en review.
- Behavox [^133^]: "rolled it out to hundreds of developers, quickly became our go-to pair programmer"
- Altana [^133^]: "accelerated development velocity by 2-10x"

#### 5. Métricas de éxito

**¿Cómo medís si CLAUDE.md funciona?**

| Métrica | Baseline | Target | Fuente |
|---------|----------|--------|--------|
| Diff size promedio (líneas) | 40+ líneas para bugfixes simples | <10 líneas para fixes simples | Karpathy examples: fix de empty emails pasó de 40 líneas a 2 líneas [^31^] |
| Número de follow-up clarifications | 3-5 por sesión | <1 por sesión | "Think Before Coding" rule reduce assumptions [^29^] |
| Número de "AI cleanup incidents" | ~1 cada 3-5 sesiones | 0 | Hooks PreToolUse + reglas explícitas [^68^][^177^] |
| Tiempo de PR review | 18h promedio (Atlassian) | -45% | Atlassian Rovo Dev: 45% PR cycle time reduction [^259^] |
| Tiempo de PR review (enterprise India) | 128.8h baseline | -29.8% | 1mg (300 engineers): 31.8% overall efficiency gain [^262^] |
| Token savings | Baseline | 74.4% | Paul Duvall centralized-rules [^228^] |
| CLAUDE.md compliance rate | ~60% para archivos >200 líneas | >90% para <60 líneas | HumanLayer benchmark [^124^][^119^] |

**Métricas de qualidad del output**
- Arize Prompt Learning [^36^]: Optimizar solo el system prompt de Claude Code generó +5% en general coding performance y +11% cuando se especializó a un solo repositorio.
- Boris Cherny recomienda: "If you have to repeat an instruction in chat more than twice, promote it into your CLAUDE.md" [^33^].
- Señales de éxculo de CLAUDE.md [^233^]: Fewer corrections, better first attempts, reduced context-setting, team consistency.

#### 6. Plantillas para diferentes contextos

**CLAUDE.md para KB pura (caso MWT)**
Basado en badwally/TheKnowledge [^175^] + CWAN Engineering [^234^]:
```markdown
# CLAUDE.md — MWT Knowledge Hub Agent Control Surface

## Identity
You are the KB curator assistant for Muito Work Limitada. Your job is to 
organize, validate, and synthesize knowledge — NEVER to write production code.

## Canonical Source of Truth
- Git repo at C:\dev\mwt-knowledge-hub is the ONLY canonical source
- OneDrive mirror is read/write for Cowork sessions, but ALL changes MUST 
  flow through sync_*_indexa.ps1 back to the canonical repo
- NEVER write directly to the canonical repo from Cowork

## Taxonomy (8 tipos canónicos)
- ENT: Entity | PLB: Publicable | SCH: Schema | LOC: Location
- POL: Policy | IDX: Index | SKILL: Skill | LOTE: Lote
- Every file MUST have correct frontmatter type. Ask if unclear.

## Rules
1. DRAFT-FIRST invariante: All new content starts as draft: true
2. Curaduría 2 capas: USER review + COMMITTEE approval before finalize
3. NEVER create, move, or delete files in the canonical repo directly
4. NEVER modify files outside the current working directory scope
5. If Cowork suggests changes to canonical files, STOP and ask permission
6. All claims must cite source with [[file:line]] format
7. Seal/Open dual mode: Sealed = read-only source of truth; Open = working drafts
```

**CLAUDE.md para codebase (Karpathy/Mehul style)**
```markdown
# CLAUDE.md

## Think Before Coding
- State your assumptions explicitly before implementing
- Present multiple interpretations when ambiguity exists
- Ask when unclear — never pick silently

## Simplicity First
- Minimum code that solves the problem. Nothing speculative.
- No abstractions for single-use code. No "flexibility" not requested.
- If 200 lines could be 50, rewrite it.

## Surgical Changes
- Touch only what you must. Clean up only your own mess.
- Every changed line should trace directly to the user's request.
- Do not improve adjacent code, comments, or formatting.

## Goal-Driven Execution
- Transform imperative tasks into verifiable goals
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- Plan format: 1. [Step] → verify: [check]
```

**CLAUDE.md para research repo**
Según CWAN Engineering [^234^]:
- Tier 1: Source of Truth (read-only for AI agents)
- Tier 2: Core Knowledge (textbook del proyecto)
- Tier 3: Implementation & Analysis (working documents)
- Tier 4: Historical/Archive (non-authoritative)
- Regla: "If an AI agent contradicts a Tier 1 document, the agent is wrong"

**CLAUDE.md para multi-tenant SaaS**
Según LowCode Agency [^88^] + GoClaw [^94^]:
```markdown
## Multi-Tenant Rules (MUST NEVER BREAK)
1. Every database query MUST include tenant_id filter from request context
2. Every isolatable table has tenant_id NOT NULL
3. Tenant flows through context.Context — NEVER from client headers
4. RLS policies are the source of truth; app-level filtering is defense in depth
5. Per-tenant overrides: LLM configs, tool settings, skills enabled
```

#### 7. Reglas específicas para repo KB con sync canónico

**El patrón badwally/TheKnowledge [^175^][^254^]**
Es el caso de estudio más cercano al setup de MWT. Estructura:
```
~/code/knowledge/
├── CLAUDE.md              # Agent control surface
├── WIKI.md                # Conventions reference (contract humano)
├── raw/                   # Immutable ingested sources
├── wiki/                  # LLM-authored knowledge (6 page types)
├── .knowledge/
│   ├── policies/          # Editorial policies per domain
│   ├── locks/             # File locks for concurrency safety
│   └── lint/              # Lint reports
├── src/gateway/           # Gateway implementation
│   ├── core.py            # Gateway.execute(operation, args)
│   ├── validator.py       # WIKI.md rules as composable functions
│   ├── locking.py         # File locks
│   └── ops/               # One module per gateway operation
```

**Control surface dual: CLAUDE.md + WIKI.md**
- `CLAUDE.md` = qué puede hacer el agente, cómo debe comportarse
- `WIKI.md` = contract técnico que valida el gateway. Cada componente (gateway, validator, converters) codifica contra WIKI.md
- El gateway implementa WIKI.md § 9.2 contract: validate input → lock → execute → validate output → write atomically → update backlinks → log → release lock → return [^254^]

**Draft mode**
- `draft: true` en frontmatter permite contenido en progreso
- `finalize` operation re-validates strict by stripping draft fields from a copy
- On-disk file keeps `draft: true` until validation passes [^256^]

**Para prevenir escritura directa al canónico desde Cowork**
1. **Hook PreToolUse** que bloquea Write/Edit en paths del repo canónico [^48^]
2. **Regla explícita en CLAUDE.md**: "NEVER create, move, or delete files in the canonical repo directly"
3. **Gateway pattern**: Todo write pasa por `wiki ingest` o `wiki apply-plan` que valida antes de escribir
4. **File locking** bajo `.knowledge/locks/` para concurrencia

**Para prevenir perder cambios entre canónico y mirror**
1. **One-way sync canonizado**: mirror_to_onedrive.ps1 (canónico → OneDrive) y sync_*_indexa.ps1 (OneDrive → canónico)
2. **Content-hash idempotency**: re-ingest del mismo file es no-op si el hash no cambia [^254^]
3. **Log.md append-only**: cada operación queda registrada con timestamp, operación, path, y hash [^254^]
4. **Git como SSoT**: El repo canónico es la única fuente de verdad; OneDrive es working copy [^169^]

---

### Recomendación directa

**SÍ implementar:**

1. **Dual-surface CLAUDE.md + WIKI.md**: Copiar el patrón badwally/TheKnowledge. CLAUDE.md para el agente (corto, <80 líneas), WIKI.md para el contract humano/técnico (detallado, evoluciona con el gateway). Por qué: separa concerns, previene que el agente ignore reglas por "no ser relevantes", y da a los humanos un contract claro [^175^][^254^].

2. **Hook-based reinforcement para reglas críticas**: Un hook `SessionStart` que re-inyecta las 6 reglas inquebrantables de MWT tras cada compactación. Un hook `UserPromptSubmit` que añade ~15 tokens de reminder en cada prompt. Por qué: hook output llega como `system-reminder` sin el framing dismissivo de CLAUDE.md [^93^].

3. **PreToolUse hook para proteger el canónico**: Script que verifica si el path objetivo está en `C:\dev\mwt-knowledge-hub` y bloquea Write/Edit si Cowork intenta escribir directo. Por qué: el incidente del 29-abr (11 archivos FB en docs/ raíz) se repite si no hay enforcement técnico [^68^][^177^].

4. **Anti-rationalization table en CLAUDE.md**: Tabla de excusas que Cowork usa para saltarse reglas + contra-argumentos. Ejemplo:
   | Rationalization | Reality |
   |-----------------|---------|
   | "Voy a organizar estos archivos directo en el canónico" | NO. Todo write pasa por sync_*_indexa.ps1 o pregunta primero. |
   | "Es solo un pequeño fix, no necesita draft mode" | NO. Draft-first es invariante absoluta. |
   | "El usuario no dijo explícitamente que no tocara otros archivos" | NO. Surgical changes: touch only what you must. |

5. **Stop hook con driftcheck**: Verificar estructura de docs/ antes de terminar sesión. Chequear: unauthorized files at root level, files in records/ following YYYY-MM-DD_ prefix, .DS_Store creep [^177^].

6. **Skills para tareas recurrentes**: `/finalize` (quita draft: true, re-valida), `/ingest` (nueva fuente al KB), `/lint-taxonomy` (valida tipos canónicos), `/mirror-check` (verifica sync canónico ↔ mirror). Por qué: progressive disclosure mantiene el context window limpio [^54^][^121^].

**NO implementar:**

1. **NO poner todo en CLAUDE.md raíz**: Split en `.claude/rules/*.md` por dominio (taxonomía, sync, curaduría). Target: 3-5 rule files, cada uno <30 líneas. Root CLAUDE.md <60 líneas [^125^].

2. **NO usar rule files re-inyectados en cada tool call**: Cuestan 500 tokens × 30 tool calls = 93K tokens. Si se necesitan reglas por dominio, usar skills con `disable-model-invocation: true` y activar manualmente [^125^][^96^].

3. **NO confiar solo en CLAUDE.md para reglas de seguridad**: El framing "may or may not be relevant" hace que reglas de "nunca escribas al canónico" sean sugerencias, no mandatos. Las reglas que protegen contra data loss van en hooks [^93^][^89^].

4. **NO permitir auto-mode sin guardrails**: El incidente #49464 (rm -f ~/) demuestra que auto-mode + cleanup behavior es peligroso sin PreToolUse hooks que bloquean comandos destructivos [^182^].

**Diferir post-MVP:**

1. **MCP server para el gateway**: badwally implementó MCP server en M7 [^256^]. Para MWT, esto es post-Foundation Beta. El gateway puede ser un script PowerShell inicial.
2. **Agent teams / multi-agent**: No aplica a single-agent MVP. La documentación oficial de Claude Code sobre agent teams [^232^] es útil para post-MVP.
3. **Enterprise policy files**: Requieren Claude Code for Enterprise. MWT usa plan Max/Team, no Enterprise aún.

---

### Casos reales citados

| Equipo/Empresa | Caso | Métrica | Fuente |
|----------------|------|---------|--------|
| Andrej Karpathy / Forrest Chang | CLAUDE.md con 4 reglas edit-time | 97.8k stars, bug fix de 40 líneas → 2 líneas | [^29^][^31^] |
| HumanLayer | CLAUDE.md productivo | <60 líneas, mejor compliance que 200-línea manifestos | [^124^][^119^] |
| Boris Cherny (creador Claude Code) | CLAUDE.md equipo Anthropic | ~60-83 líneas, actualizado colaborativamente por errores reales | [^124^] |
| Behavox | Rollout Claude Code Enterprise | "Cientos de devs, go-to pair programmer" | [^133^] |
| Altana | Claude Code + Claude | "2-10x development velocity" | [^133^] |
| Atlassian (Rovo Dev) | AI code review interno | PR cycle time -45% (interno), -32% (clientes beta) | [^259^] |
| 1mg (India, 300 ingenieros) | AI platform DeputyDev | 31.8% reducción PR review time (p=0.0076), 28% increase code shipment | [^262^] |
| CPinto / Rails SaaS | Built complete SaaS with Claude Code | 38,600 líneas Rails, ~25-45h human time, 727 commits en 8 semanas | [^71^] |
| Dzianis Karviha | Claude Code en proyecto grande | 40% productivity increase, commits más atómicos | [^70^] |
| Paul Duvall | Centralized-rules pattern | 74.4% token savings, consistent AI behavior across teams | [^228^] |
| Badwally / TheKnowledge | KB con gateway + validator + draft mode | 134 tests passing, 11 MCP tools, 6 page types, content-hash idempotency | [^254^][^256^] |
| Addy Osmani (Google→Anthropic) | Agent-skills open source | 20 skills, anti-rationalization tables, 18.1k stars | [^121^][^126^] |
| Faros AI (análisis cohorte) | Team A 5% adoption vs Team B 60% | Team B merged 47% more PRs daily pero 35% longer review times | [^129^] |
| CWAN Engineering | AI-powered markdown KB | Tier 1 = read-only SSoT, agent must cite file:line | [^234^] |
| LowCode Agency | Multi-tenant SaaS con Claude Code | 3-5 días para foundation vs 2-4 semanas manual | [^88^] |
| GoClaw | Multi-tenant AI agent platform | 40+ tables con tenant_id, 5-layer defense-in-depth | [^94^] |
| Augusteo | "20 PRs a weekend" con Claude Code | Superpower Code Review + automated PR toolkit + Cubic Reviewer | [^260^] |
| Anthropic Data Infrastructure | Multiple parallel Claude Code sessions | Checkpoint-heavy workflow, one mission = one session | [^237^] |

---

### Gotchas y riesgos

1. **Context rot no es teórico**: "Lost in the Middle" (Liu et al., 2023) demostró que performance es más alta cuando información relevante está al principio o final del contexto, degradándose significativamente en el medio [^170^]. NoLiMa Benchmark: a 32k tokens, 11/12 modelos bajaron de 50% performance [^69^].

2. **Thinking token reduction = degradación real**: Un análisis cuantitativo de 17,871 thinking blocks y 234,760 tool calls reveló que la reducción de thinking tokens (redact-thinking-2026-02-12) correlacionó con quality regression medible. Convention drift: variable names prohibidas reaparecieron, cleanup patterns violados [^73^].

3. **El "compliance decay curve"**: Claude sigue reglas perfectamente por 3 mensajes, luego las abandona. No es malicioso, es atención diluida [^124^].

4. **"Simplest" como señal de degradación**: En logs de 6,852 sesiones, la palabra "simplest" aumentó 642% post-regresión. Indica que el modelo elige el path más fácil, no el correcto [^73^].

5. **Skills no se auto-activan confiablemente**: La documentación dice que skills son "autonomous" y "model-invoked", pero en práctica "you need to smash Claude over the head to actually use them" [^96^]. Requiere hook-based reinforcement o invocación explícita.

6. **Subagents no heredan skills del main session**: Si defines skills en el main agent, debes pasarlos explícitamente al subagent vía `skills:` field [^52^].

7. **MCP servers consumen context agresivamente**: 100+ MCP tools pueden ocupar 33.4% del context window antes de que empiece la conversación [^100^].

8. **Auto-compact contaminó contexto**: Un usuario reportó que con Auto Compact ON, sesión iniciaba en 85k/200k tokens (43%). Después de desactivarlo: 38k/200k (19%) [^67^].

---

### 4-6 patrones canónicos para incorporar a MWT CLAUDE.md v2

#### Patrón 1: Dual-Surface Control (CLAUDE.md + WIKI.md)

Adaptado de badwally/TheKnowledge [^175^][^254^]:

```markdown
# CLAUDE.md — MWT KB Agent Control Surface
## Identity
You are the KB curator assistant for Muito Work Limitada. 
Your job: organize, validate, synthesize knowledge. 
You NEVER write production code for FaberLoom.

## Canonical Source of Truth
- Git repo at C:\dev\mwt-knowledge-hub is the ONLY canonical source
- OneDrive mirror is working copy for Cowork sessions
- ALL changes flow through sync_*_indexa.ps1 back to canonical
- NEVER write directly to canonical repo from Cowork

## Rules (Inquebrantables)
1. DRAFT-FIRST: All new content starts as draft: true
2. CURADURÍA 2 CAPAS: USER review + COMMITTEE approval before finalize
3. SURGICAL CHANGES: Touch only what the task requires
4. ASK-DONT-ASSUME: When unclear, stop and ask. Never guess.
5. CITE-OR-DIE: Every claim must cite source with [[file:line]]
6. SEALED-OPEN: Sealed files = read-only. Open files = working drafts.

## Taxonomy (8 tipos canónicos)
ENT | PLB | SCH | LOC | POL | IDX | SKILL | LOTE
Every file MUST have correct frontmatter type.

## Commands
- Ingest source: use wiki ingest <path>
- Finalize draft: use wiki finalize <path>
- Check sync: use wiki mirror-check
- Lint taxonomy: use wiki lint-taxonomy
```

```markdown
# WIKI.md — MWT KB Conventions Reference
## §1 Directory Layout
├── canonical/           # Git repo (C:\dev\mwt-knowledge-hub)
│   ├── ENT/, PLB/, SCH/, LOC/, POL/, IDX/, SKILL/, LOTE/
│   ├── docs/            # Documentación operativa
│   └── .claude/         # Skills y hooks
├── mirror/              # OneDrive working copy
│   └── (sync via mirror_to_onedrive.ps1)

## §2 Frontmatter Schema
---
type: ENT | PLB | SCH | LOC | POL | IDX | SKILL | LOTE
id: UUIDv7
created: ISO8601
modified: ISO8601
draft: true | false
tier: 1 | 2 | 3 | 4
tags: [tag1, tag2]
---

## §3 Tier System
- Tier 1 (Source of Truth): Leadership-approved, read-only for agents
- Tier 2 (Core Knowledge): Foundational technical docs
- Tier 3 (Implementation): Working documents, change frequently
- Tier 4 (Archive): Non-authoritative, explicitly marked

## §4 Gateway Operations
All writes MUST pass through:
1. validate input (frontmatter, taxonomy, citations)
2. acquire file lock (.knowledge/locks/)
3. execute operation
4. validate output
5. write atomically
6. update index.md
7. append to log.md
8. release lock

## §5 Sync Protocol
- canonical → mirror: mirror_to_onedrive.ps1 (read-only from canonical POV)
- mirror → canonical: sync_*_indexa.ps1 (validates before write)
- NEVER bidirectional sync without validation gate
```

#### Patrón 2: Hook-Based Reinforcement para Reglas Críticas

Adaptado de "Claude Core Values" plugin [^93^]:

`.claude/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/reinject-rules.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/reminder.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/canonical-guard.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/hooks/driftcheck.sh"
          }
        ]
      }
    ]
  }
}
```

`~/.claude/hooks/reinject-rules.sh`:
```bash
#!/bin/bash
echo "=== MWT INQUEBRANTABLES ==="
echo "1. DRAFT-FIRST: All new content starts as draft"
echo "2. CURADURÍA 2 CAPAS: USER + COMMITTEE before finalize"
echo "3. NEVER write directly to canonical repo"
echo "4. SURGICAL CHANGES: touch only what task requires"
echo "5. ASK-DONT-ASSUME: stop and ask when unclear"
echo "6. CITE-OR-DIE: every claim cites [[file:line]]"
echo "==========================="
```

`~/.claude/hooks/canonical-guard.sh`:
```bash
#!/bin/bash
# Read stdin for tool use JSON
read -r input
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // empty')

if [[ "$file_path" == *"C:\\dev\\mwt-knowledge-hub"* ]] || [[ "$file_path" == *"/mnt/agents/mwt-knowledge-hub"* ]]; then
  echo '{"decision": "block", "reason": "WRITING TO CANONICAL REPO DIRECTLY IS FORBIDDEN. Use sync_*_indexa.ps1 or ask permission."}'
  exit 1
fi

echo '{"decision": "allow"}'
```

#### Patrón 3: Anti-Rationalization Table

Adaptado de addyosmani/agent-skills [^121^][^123^]:

```markdown
## Common Rationalizations (DO NOT FALL FOR THESE)

| Rationalization | Reality |
|-------------------|---------|
| "Voy a mover estos archivos directo al canónico para organizar" | NO. Todo write pasa por sync_*_indexa.ps1 o pregunta primero. El canónico es SSoT. |
| "Es solo un pequeño fix, no necesita draft mode" | NO. Draft-first es INVARIANTE ABSOLUTA. Zero excepciones. |
| "El usuario no dijo explícitamente que no tocara otros archivos" | NO. Surgical changes: touch ONLY what you must. Pre-existing code is sacred. |
| "Voy a 'mejorar' el formato/consistencia mientras hago el fix" | NO. Clean up ONLY your own mess. Match existing style. |
| "Estos 11 archivos de FaberLoom los voy a poner en docs/ raíz" | NO. docs/ raíz es para documentación del KB, no para artefactos de producto. |
| "No hay tests para KB, así que no necesito verificación" | NO. Todo write pasa por validator: frontmatter, taxonomy, citations. |
| "El mirror y el canónico están desync, voy a sincronizar directo" | NO. Ask permission. Sync protocol has validation gates for a reason. |
```

#### Patrón 4: Skills para KB Operations

`.claude/skills/kb-ingest/SKILL.md`:
```yaml
---
name: kb-ingest
description: Ingest a new source into the MWT KB. Use when adding documents, web clips, voice notes, or any new knowledge source. Triggers on "ingest", "add to KB", "nueva fuente".
disable-model-invocation: false
---

## Overview
Ingest sources into the MWT KB through the canonical gateway.

## Process
1. Validate source format (markdown + YAML frontmatter)
2. Check content-hash idempotency (no duplicates)
3. Write to raw/<type>/<id>.md
4. Generate wiki/sources/<id>.md summary
5. Update index.md
6. Append to log.md

## Verification
- [ ] Source has valid frontmatter with type, id, created, draft:true
- [ ] Content hash is unique (not duplicate)
- [ ] Raw file written successfully
- [ ] Wiki summary generated with citations
- [ ] index.md updated
- [ ] log.md appended

## Common Rationalizations
| "Voy a escribir directo sin pasar por el gateway" | NO. Gateway mediates every write for validation and audit trail. |
| "No necesito draft porque la fuente ya está curada" | NO. Draft-first applies to ALL new content. COMMITTEE must approve. |
```

`.claude/skills/kb-finalize/SKILL.md`:
```yaml
---
name: kb-finalize
description: Finalize a draft KB page after curation approval. Use when COMMITTEE has approved and draft: true needs to become draft: false. Triggers on "finalize", "approve", "publicar".
---

## Process
1. Read draft file
2. Strip draft fields from copy
3. Run strict validation (validator.py composite)
4. If validation passes: write finalized version
5. If validation fails: report errors, keep draft

## Verification
- [ ] All citations ground to real sources
- [ ] Frontmatter type is valid canonical type
- [ ] No [[broken-links]]
- [ ] Tier assigned correctly
- [ ] COMMITTEE approval documented in log.md
```

#### Patrón 5: Stop Hook con Driftcheck

`~/.claude/hooks/driftcheck.sh`:
```bash
#!/bin/bash
# Run at session end to verify no unauthorized changes

echo "=== DRIFT CHECK ==="

# Check for unauthorized files at docs/ root
unauthorized=$(find "C:\dev\mwt-knowledge-hub\docs" -maxdepth 1 -type f ! -name "*.md" ! -name ".gitkeep" 2>/dev/null)
if [ -n "$unauthorized" ]; then
  echo "[BLOCK] Unauthorized files at docs/ root:"
  echo "$unauthorized"
  echo "Move to correct subdirectory or remove before ending session."
fi

# Check for files outside taxonomy directories
orphans=$(find "C:\dev\mwt-knowledge-hub" -maxdepth 1 -type f -name "*.md" ! -name "CLAUDE.md" ! -name "WIKI.md" ! -name "README.md" ! -name "index.md" ! -name "log.md" 2>/dev/null)
if [ -n "$orphans" ]; then
  echo "[WARN] Markdown files at repo root (should be in typed directories):"
  echo "$orphans"
fi

# Check .DS_Store creep
if find "C:\dev\mwt-knowledge-hub" -name ".DS_Store" -print -quit | grep -q .; then
  echo "[WARN] .DS_Store files found. Clean before commit."
fi

echo "==================="
```

#### Patrón 6: Tier System para Authority Hierarchy

Adaptado de CWAN Engineering [^234^]:

```markdown
## Authority Hierarchy (Tier System)

### Tier 1: Source of Truth (Sealed)
- Leadership-approved documents defining project direction
- Read-only for AI agents
- Examples: architecture decisions, compliance policies, pricing tiers
- Agent MUST cite with file:line evidence for any authoritative claim
- If agent contradicts Tier 1, agent is WRONG

### Tier 2: Core Knowledge
- Foundational technical documents (API design, data model, integration patterns)
- Agent reads these during session initialization
- Citable, but may evolve with engineering approval

### Tier 3: Implementation & Analysis
- Working documents: sprint notes, meeting minutes, generated reports
- Change frequently
- Agent may suggest updates, but USER curates

### Tier 4: Historical/Archive
- Old documents kept for reference
- Explicitly marked NON-AUTHORITATIVE
- Agent MUST NOT cite as current truth

## Enforcement
1. Session initialization: read Tier 1 files first
2. Every claim: cite Tier 1 with [[file:line]] or mark confidence (HIGH/MEDIUM/LOW)
3. Never speculate about system behavior — cite or ask
```

---

### Métricas de éxito a trackear post-implementación

#### Métricas de calidad del KB (semanal)

| # | Métrica | Cómo medir | Target | Frecuencia |
|---|---------|-----------|--------|------------|
| 1 | Archivos sin frontmatter válido | `grep -L "^---"` en nuevos archivos | 0 | Semanal |
| 2 | Archivos en ubicación incorrecta (fuera de taxonomía) | Driftcheck hook output | 0 | Por sesión |
| 3 | Archivos draft sin aprobación después de 7 días | Query `draft: true` + age | <5% | Semanal |
| 4 | Citations rotas (`[[broken]]`) | Wiki link validator | 0 | Semanal |
| 5 | Incidentes "AI cleanup" (cambios no solicitados) | Log de sesiones + diff review | 0 | Por incidente |
| 6 | Writes directos al canónico bloqueados | PreToolUse hook log | 0 | Por intento |

#### Métricas de eficiencia del agente (mensual)

| # | Métrica | Cómo medir | Target | Frecuencia |
|---|---------|-----------|--------|------------|
| 7 | Diff size promedio (líneas cambiadas por tarea) | `git diff --stat` por sesión | <15 líneas para tareas simples | Mensual |
| 8 | Follow-up clarifications por sesión | Contar prompts tipo "no, eso no es lo que pedí" | <1 | Mensual |
| 9 | Sesiones que requieren /rewind o /clear | Contar sesiones con rollback | <10% | Mensual |
| 10 | Tiempo de curaduría (draft → finalize) | Timestamp draft vs timestamp finalize | <48h para Tier 3, <7d para Tier 2 | Mensual |
| 11 | Reglas de CLAUDE.md que se ignoran | Auditoría manual de sesiones grabadas | 0 para inquebrantables | Mensual |
| 12 | Token cost por sesión de KB | Claude Code statusline | <20k tokens promedio | Mensual |

#### Métricas de adopción del equipo (trimestral)

| # | Métrica | Cómo medir | Target | Frecuencia |
|---|---------|-----------|--------|------------|
| 13 | % sesiones usando skills (`/skill-name`) vs prompts raw | Skill auditor log [^51^] | >70% | Trimestral |
| 14 | Consistencia de taxonomía (archivos con tipo correcto) | Validator output | >95% | Trimestral |
| 15 | Nuevos contributors con setup correcto en día 1 | Onboarding checklist completion | 100% | Por onboarding |

---

### Anti-patterns a evitar explícitamente

| # | Anti-pattern | Por qué falla | Mitigación en MWT |
|---|-------------|---------------|-------------------|
| 1 | **Monolithic Mega-Prompt** — CLAUDE.md de 300+ líneas | Context overload, atención diluida, reglas finales ignoradas | Target <60 líneas raíz. Split en `.claude/rules/*.md` [^173^] |
| 2 | **Confiar en CLAUDE.md para reglas de seguridad** | El framing "may or may not be relevant" las convierte en sugerencias | Reglas críticas en hooks (SessionStart, PreToolUse) [^93^] |
| 3 | **Rule files re-inyectados en cada tool call** | 500 tokens × 30 calls = 93K tokens (46% de context window) | 3-5 rule files, <30 líneas cada uno. Skills con `disable-model-invocation: true` [^125^] |
| 4 | **AI cleanup behavior sin guardrails** | Modifica código/archivos no relacionados, genera regressions | PreToolUse hook bloquea writes no autorizados. Regla explícita: "touch only what you must" [^68^] |
| 5 | **Infinite loop sin circuit breaker** | Repite mismo comando fallido 7+ veces, consume $500+ en tokens | Límite de retries en hooks. Loop detection: abort after N identical requests [^100^][^102^] |
| 6 | **System prompt override de CLAUDE.md** | Plan mode / agent launch ignora reglas del usuario | Hooks que re-inyectan reglas tras cada compactación. Verificación manual de plan mode [^89^] |
| 7 | **Invisible state** — confiar en que el LLM "recuerda" | Estado comprimido, detalles perdidos, drift creciente | Estado explícito en log.md + index.md. Gateway mantiene estado estructurado [^173^] |
| 8 | **Happy path engineering** — solo probar el éxito | Agente nunca vio fallos, no sabe distinguir retry vs escalate | Skills con failure recovery patterns. Test con inputs malformados [^170^] |
| 9 | **Multi-agent chaos sin roles claros** | Agentes duplican trabajo, se contradicen, bounce control | MVP = single-agent. Post-MVP: roles definidos, shared state con invariantes [^170^] |
| 10 | **Contradictory instructions** — reglas que se anulan | "Nunca escribas fuera del repo" vs "escribe plan en ~/.claude/plans/" | Una sola fuente de verdad para reglas. WIKI.md como contract. Resolución: más específico gana [^89^] |
| 11 | **Agent-as-Business-Process** — dejar que el agente "aproxime" procesos | Reemplaza process graph controlado con reasoning no determinista | Gateway con pasos definidos: validate → lock → execute → validate → log [^173^][^254^] |
| 12 | **Sycophancy — agente dice lo que quiere oír** | Evita conflictos, no surfacea problemas reales | Anti-rationalization tables. Explicit conflict detection [^172^] |

---

### Secciones para KB con sync canónico

#### El patrón SSoT (Single Source of Truth) para KB

**Principios (adaptado de Shelfi [^169^] + badwally [^175^])**:
1. **Git es la SSoT**: El repo canónico es la única fuente de verdad. Si no está en Git, no es verdad.
2. **Version controlled**: Cada cambio trackeado en Git history. Audit trail completo.
3. **Code-adjacent**: Docs reviewed como parte del PR process. Nunca un afterthought.
4. **Centralized & searchable**: Índice `index.md` reconstruible desde el gateway.
5. **Ultimate portability**: Markdown files en repo propio. Zero vendor lock-in.

**Arquitectura de sync (caso MWT)**:
```
┌─────────────────────────────────────────┐
│  C:\dev\mwt-knowledge-hub (CANONICAL)   │
│  ├── Git repo = SSoT                    │
│  ├── CLAUDE.md + WIKI.md                │
│  ├── 8 typed directories (ENT/PLB/...)  │
│  ├── index.md + log.md                  │
│  └── .knowledge/ (locks, policies, lint)│
└─────────────────┬───────────────────────┘
                  │ mirror_to_onedrive.ps1
                  │ (one-way, read-only from canonical POV)
                  ▼
┌─────────────────────────────────────────┐
│  OneDrive (MIRROR / WORKING COPY)       │
│  ├── Cowork escribe aquí                │
│  └── Temporal, disposable               │
└─────────────────┬───────────────────────┘
                  │ sync_*_indexa.ps1
                  │ (validates before write to canonical)
                  ▼
┌─────────────────────────────────────────┐
│  Back to CANONICAL                      │
│  └── Gateway validates, locks, logs     │
└─────────────────────────────────────────┘
```

**Reglas del sync protocol**:
1. **Unidireccional por etapa**: canonical → mirror es export. mirror → canonical es import con validation gate.
2. **Nunca bidireccional automático**: El sync bidireccional sin gate genera conflictos y data loss.
3. **Content-hash idempotencia**: Re-ingest del mismo file es no-op si hash no cambia [^254^].
4. **Log append-only**: Cada operación de sync queda en `log.md` con timestamp, dirección, files afectados, y hash.
5. **Lock durante sync**: `.knowledge/locks/` previene race conditions si Cowork y sync script corren simultáneamente.

**CLAUDE.md rules específicas para sync**:
```markdown
## Sync Protocol (NEVER VIOLATE)
1. CANONICAL → MIRROR: mirror_to_onedrive.ps1 (export)
2. MIRROR → CANONICAL: sync_*_indexa.ps1 (import with validation)
3. NEVER write directly to canonical from Cowork
4. NEVER run bidirectional sync without validation gate
5. If sync conflict detected: STOP, ask human, log incident
6. After every sync: verify index.md consistency
```

---

### Sources

[^11^]: https://code.claude.com/docs/en/best-practices — Anthropic, "Best practices for Claude Code" (2025)
[^14^]: https://discuss.huggingface.co/t/10-essential-claude-code-best-practices-you-need-to-know/174731 — "10 Essential Claude Code Best Practices" (2026-03-28)
[^29^]: https://forum.devtalk.com/t/has-anyone-tried-the-karpathy-claude-md-rules-97-8k-stars/243109 — "Has anyone tried the Karpathy CLAUDE.md rules?" (2026-04-29)
[^30^]: https://intuitionlabs.ai/articles/claude-enterprise-deployment-training-guide-2026 — "Claude Enterprise Guide 2026" (2026-04-26)
[^31^]: https://alphasignalai.substack.com/p/karpathy-inspired-claudemd-how-to — "Karpathy-Inspired CLAUDE.md" (2026-04-22)
[^32^]: https://github.com/MuhammadUsmanGM/claude-code-best-practices — "claude-code-best-practices" GitHub (2026-04-23)
[^33^]: https://antigravity.codes/blog/karpathy-claude-code-skills-guide — "Karpathy's CLAUDE.md Skills File" (2026-04-13)
[^34^]: https://dev.to/reneza/ten-claudemd-rules-for-claude-code-four-edit-time-six-runtime-210g — "Ten CLAUDE.md rules" (2026-04-23)
[^35^]: https://medium.com/@elliotJL/your-ai-has-infinite-knowledge-and-zero-habits-heres-the-fix-e279215d478d — "Claude Keeps Making the Same Mistakes" (2026-01-28)
[^36^]: https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/ — "CLAUDE.md Best Practices from Prompt Learning" (2025-11-20)
[^37^]: https://www.gend.co/blog/claude-skills-claude-md-guide — "Claude Skills and Claude MD" (2025-12-05)
[^48^]: https://www.techplained.com/claude-code-subagents-skills — "Claude Code Subagents, Skills, Hooks" (2026-02-13)
[^49^]: https://github.com/anthropics/claude-code/issues/30554 — "Feature Request: Team/shared CLAUDE.md" (2026-03-03)
[^50^]: https://serenitiesai.com/articles/agent-skills-guide-2026 — "AI Agent Skills Guide 2026" (2026-03-05)
[^51^]: https://www.developersdigest.tech/blog/best-claude-code-skills-2026 — "Best Claude Code Skills 2026" (2026-04-28)
[^52^]: https://code.claude.com/docs/en/features-overview — "Extend Claude Code" Anthropic Docs (2025)
[^53^]: https://aimaker.substack.com/p/anthropic-claude-updates-q1-2026-guide — "Complete Guide to Claude Updates Q1 2026" (2026-04-07)
[^54^]: https://www.fundesk.io/claude-skills-agent-skills-complete-guide-2026 — "2026 Guide to Agent Skills" (2026-04-20)
[^55^]: https://smartscope.blog/en/generative-ai/claude/claude-code-best-practices-advanced-2026/ — "Claude Code Advanced Best Practices" (2026)
[^67^]: https://www.reddit.com/r/ClaudeAI/comments/1p05r7p/my_claude_code_context_window_strategy_200k_is/ — "Context Window Strategy" (2026-02-26)
[^68^]: https://github.com/anthropics/claude-code/issues/15333 — "Mark code sections as 'do not modify'" (2025-12-24)
[^69^]: https://limitededitionjonathan.substack.com/p/ultimate-guide-fixing-claude-hit — "Fixing Claude max length" (2025-11-06)
[^70^]: https://dev.to/dzianiskarviha/integrating-claude-code-into-production-workflows-lbn — "Claude Code in Production: 40% Productivity" (2025-12-22)
[^71^]: https://world.hey.com/cpinto/building-a-complete-saas-product-with-only-claude-code-cca13895 — "Building SaaS with only Claude Code" (2026-02-08)
[^72^]: https://www.mindstudio.ai/blog/what-is-claude-code-auto-mode-permission-classifier/ — "Claude Code Auto Mode" (2026-04-01)
[^73^]: https://github.com/anthropics/claude-code/issues/42796 — "Claude Code unusable for complex tasks Feb updates" (2026-04-02)
[^88^]: https://www.lowcode.agency/blog/claude-code-multi-tenant-architecture — "Multi-Tenant App Architecture with Claude Code" (2026-04-10)
[^89^]: https://github.com/anthropics/claude-code/issues/27032 — "Model ignores CLAUDE.md instructions" (2026-02-19)
[^90^]: https://www.reddit.com/r/ClaudeCode/comments/1se66cf/something_has_changed_claude_code_now_ignores/ — "Claude Code now ignores every rule" (2026)
[^91^]: https://github.com/anthropics/claude-code/issues/2544 — "CLAUDE.md Mandatory Rules Consistently Ignored" (2025-06-24)
[^92^]: https://medium.com/@richardhightower/claude-code-rules-stop-stuffing-everything-into-one-claude-md-0b3732bca433 — "Stop Stuffing Everything into One CLAUDE.md" (2026-03-10)
[^93^]: https://dev.to/albert_nahas_cdc8469a6ae8/your-claudemd-instructions-are-being-ignored-heres-why-and-how-to-fix-it-23p6 — "Your CLAUDE.md Instructions Are Being Ignored" (2026-02-17)
[^94^]: https://dev.to/truongpx396/goclaw-deep-dive-a-builders-guide-to-a-multi-tenant-ai-agent-platform-5d6c — "Multi-Tenant AI Agent Platform" (2026-04-28)
[^96^]: https://scottspence.com/posts/claude-code-skills-dont-auto-activate — "Claude Code Skills Don't Auto-Activate" (2025-11-05)
[^100^]: https://github.com/anthropics/claude-code/issues/35166 — "Claude Code sends repeated requests hundreds of times" (2026-03-16)
[^102^]: https://github.com/anthropics/claude-code/issues/19699 — "Claude gets stuck in infinite loop" (2026-01-21)
[^118^]: https://jimmysong.io/ai/addyosmani-agent-skills/ — "Agent Skills by Addy Osmani" (2026-04-27)
[^119^]: https://dev.to/shipwithaiio/beyond-claudemd-5-layers-your-ai-agent-harness-is-missing-475h — "Beyond CLAUDE.md: 5 Layers Missing" (2026-04-22)
[^120^]: https://dev.to/_46ea277e677b888e0cd13/agent-skills-19-production-grade-skills-that-make-ai-coding-agents-work-like-senior-engineers-5bi9 — "19 Production-Grade Skills" (2026-04-08)
[^121^]: https://github.com/addyosmani/agent-skills — "addyosmani/agent-skills" GitHub (2026-02-15)
[^123^]: https://github.com/addyosmani/agent-skills/blob/main/docs/skill-anatomy.md — "Skill Anatomy" (2026-02-15)
[^124^]: https://thomas-wiegold.com/blog/claude-md-helpful-or-expensive-noise/ — "CLAUDE.md: Helpful or Expensive Noise?" (2026-03-09)
[^125^]: https://github.com/abhishekray07/claude-md-templates/blob/main/principles.md — "Writing Rules Claude Actually Follows" (2026)
[^126^]: https://addyosmani.com/blog/agent-skills/ — "Agent Skills" blog (2026-05-04)
[^127^]: https://www.theunwindai.com/p/open-source-solution-to-context-rot-in-ai-agents — "Open-Source Solution to Context Rot" (2025-12-03)
[^128^]: https://codewithmukesh.com/blog/claude-md-mastery-dotnet/ — "CLAUDE.md Memory Hierarchy" (2026-01-24)
[^129^]: https://www.faros.ai/blog/how-to-measure-claude-code-roi-developer-productivity-insights-with-faros — "How to measure Claude Code ROI" (2026-01-07)
[^130^]: https://rachel.fyi/posts/what-i-took-from-addy-osmanis-agent-skills — "What I Took from Agent Skills" (2026-04-16)
[^131^]: https://shipwithai.io/blog/claude-code-harness-5-layers/ — "5 Layers Your AI Agent Harness Is Missing" (2026-04-09)
[^132^]: https://pub.towardsai.net/writing-a-good-claude-md-c40a32b39dfa — "Writing a Good CLAUDE.md" (2026-03-10)
[^133^]: https://www.anthropic.com/news/claude-code-on-team-and-enterprise — "Claude Code and admin controls" (2025-08-20)
[^134^]: https://github.com/anthropics/claude-code/issues/29990 — "Governing stateless sessions with CLAUDE.md + MEMORY.md" (2026-03-01)
[^135^]: https://www.rushis.com/agent-skills-teaching-ai-agents-to-code-like-senior-engineers/ — "Agent Skills: Teaching AI agents" (2026-04-13)
[^169^]: https://shelfi.sh/features/single-source/ — "Git-Based Single Source of Truth" (2026)
[^170^]: https://achan2013.medium.com/ai-agent-anti-patterns-part-2-tooling-observability-and-scale-traps-in-enterprise-agents-42a451ea84ec — "AI Agent Anti-Patterns Part 2" (2026-03-25)
[^171^]: https://elements.cloud/blog/agent-instruction-patterns-and-antipatterns-how-to-build-smarter-agents/ — "Agent Instruction Patterns and Antipatterns" (2025-06-27)
[^172^]: https://xmpro.com/when-ai-agents-tell-you-what-you-want-to-hear-the-sycophancy-problem/ — "Sycophancy Problem" (2025-06-03)
[^173^]: https://achan2013.medium.com/ai-agent-anti-patterns-part-1-architectural-pitfalls-that-break-enterprise-agents-before-they-32d211dded43 — "AI Agent Anti-Patterns Part 1" (2026-03-02)
[^174^]: https://github.com/anthropics/claude-code/issues/26512 — "Infinite loop bug with AI self-aware" (2026-02-17)
[^175^]: https://github.com/badwally/TheKnowledge/blob/main/WIKI.md — "TheKnowledge WIKI.md" (2026-04-29)
[^177^]: https://dev.to/shimo4228/stop-using-default-settings-10-claude-code-configs-that-actually-work-243l — "10 Claude Code Configs That Actually Work" (2026-03-05)
[^181^]: https://wmedia.es/en/tips/claude-code-claudemd-project-setup — "Your CLAUDE.md Is Full of Junk" (2026-03-03)
[^182^]: https://github.com/anthropics/claude-code/issues/49464 — "Claude attempts to delete home directory" (2026-04-16)
[^192^]: https://koder.ai/blog/claude-code-git-hooks-automation — "Claude Code git hooks" (2026-01-08)
[^196^]: https://engrxiv.org/preprint/download/6681/10947/9274 — "Rule-Based Governance of AI System Behavior" (2026)
[^197^]: https://mintlify.com/galfrevn/promptsmith/concepts/constraints — "Behavioral Constraints - PromptSmith" (2026-03-03)
[^198^]: https://dius-au.medium.com/a-week-with-claude-code-lessons-surprises-and-smarter-workflows-47584eb55e8d — "A week with Claude Code" (2026-04-29)
[^227^]: https://nimbalyst.com/blog/how-to-set-up-claude-code-for-your-team/ — "How to Set Up Claude Code for Your Team" (2026-03-24)
[^228^]: https://www.paulmduvall.com/sharing-ai-development-rules-across-your-organization/ — "Sharing AI Development Rules" (2026-01-29)
[^229^]: https://dev.to/myougatheaxo/standardizing-claude-code-across-your-team-claudemd-hooks-and-shared-skills-2nbn — "CLAUDE.md, Hooks, and Shared Skills" (2026-03-11)
[^230^]: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f?permalink_comment_id=6122761 — "llm-wiki" Karpathy gist (2026-05-01)
[^232^]: https://code.claude.com/docs/en/agent-teams — "Orchestrate teams of Claude Code sessions" (2025)
[^233^]: https://www.elegantsoftwaresolutions.com/blog/claude-code-mastery-claude-md-patterns — "CLAUDE.md Patterns That Actually Work" (2025-12-27)
[^234^]: https://medium.com/cwan-engineering/building-an-ai-powered-markdown-knowledge-base-system-for-your-engineering-team-4bccea3cdbfe — "AI-Powered Markdown Knowledge Base" (2026-04-24)
[^237^]: https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf — "How teams use Claude Code" Anthropic PDF (2025)
[^238^]: https://www.ronforbes.com/blog/building-your-ai-second-brain — "Building Your AI Second Brain" (2026-02-09)
[^239^]: https://portkey.ai/blog/claude-code-best-practices-for-enterprise-teams — "Claude Code best practices for enterprise" (2026-03-10)
[^254^]: https://github.com/badwally/TheKnowledge/blob/main/BUILD.md — "TheKnowledge BUILD.md" (2026-04-29)
[^255^]: https://www.gend.co/blog/claude-code-preview-review-merge — "Claude Code Preview, Review & Merge" (2026-02-20)
[^256^]: https://github.com/badwally/TheKnowledge/blob/main/SESSION_TRANSCRIPT.md — "TheKnowledge SESSION_TRANSCRIPT" (2026-04-29)
[^257^]: https://koder.ai/blog/claude-code-pr-review-pre-review-diffs — "Claude Code PR review" (2025-12-26)
[^259^]: https://www.atlassian.com/blog/announcements/how-we-cut-pr-cycle-time-with-ai-code-reviews — "Atlassian cut PR cycle time 45%" (2026-01-28)
[^260^]: https://www.augusteo.com/blog/claude-code-workflow-planning/ — "I Ship 20 PRs a Weekend" (2026-03-03)
[^262^]: https://arxiv.org/html/2509.19708v1 — "Measuring AI's True Impact on Developer Productivity" (2025-09-24)
[^263^]: https://github.com/badwally/TheKnowledge — "TheKnowledge GitHub" (2026-04-28)
[^264^]: https://code.claude.com/docs/en/code-review — "Code Review - Claude Code Docs" (2025)
