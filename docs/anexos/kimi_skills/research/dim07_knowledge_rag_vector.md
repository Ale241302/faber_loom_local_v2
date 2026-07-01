# DIMENSIÓN 7 — Knowledge Management, RAG, Vector DBs

**Fecha de investigación:** 2026-05-14
**Investigador:** Agente de investigación de skills
**Fuentes:** skills.sh, GitHub (topics: claude-code-skill, agent-skills, skill.md), awesome-agent-skills, búsquedas web

---

## Contexto de los proyectos

**MWT:** Knowledge base canónica en markdown (430 archivos, 10 dominios, 8 tipos de taxonomía). Necesita mantenimiento de calidad, validación de links, frontmatter, y eventualmente RAG sobre su propio contenido.

**FaberLoom:** KB-as-a-product con multi-tenant pgvector, 4 capas de visibilidad (personal/rol/organización/público). Necesita skills para RLS, chunking, embedding strategies, hybrid search, y evaluación de retrieval.

---

## Skills relevantes encontrados

### Tabla 1: Skills verificadas con alta relevancia

| Skill | Repo / URL | Instalación | Score MWT | Score FB | Por qué (1 línea) |
|---|---|---|---|---|---|
| **rag-architect** | [github.com/alirezarezvani/claude-skills/tree/main/engineering/rag-architect](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/rag-architect) | `/plugin install engineering-advanced-skills@claude-code-skills` o copiar carpeta | **ALTO** | **ALTO** | RAG pipeline builder, chunking optimizer, retrieval evaluator, vector DB selection, hybrid retrieval (dense+sparse), reranking strategies |
| **llm-wiki** | [github.com/alirezarezvani/claude-skills/tree/main/engineering/llm-wiki](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/llm-wiki) | Bundle `engineering-advanced-skills` o copiar carpeta | **ALTO** | **MEDIO** | Second brain para Obsidian/Claude Code: KB markdown persistente, wiki-link checking, BM25 fallback search, ingestion de fuentes, auto-síntesis |
| **Vault Health (broken-links, orphan-finder, link-checker, frontmatter-validator)** | [github.com/DavidROliverBA/Daves-Claude-Code-Skills](https://github.com/DavidROliverBA/Daves-Claude-Code-Skills) | `cp skills/vault-health/*.md .claude/skills/` | **ALTO** | **MEDIO** | 9 skills para KB markdown: broken wiki-links, orphans, frontmatter YAML validation, auto-tagging, quality reports, auto-summary |
| **supabase-postgres-best-practices** | [skills.sh/supabase/agent-skills/supabase-postgres-best-practices](https://skills.sh/supabase/agent-skills/supabase-postgres-best-practices) | `npx skills add supabase/agent-skills` | **MEDIO** | **ALTO** | RLS policies, query performance, schema design, SQL debugging — cubre Postgres/Supabase general (incluye RLS) pero no pgvector específico |
| **postgres-semantic-search** | [github.com/laguagu/claude-code-nextjs-skills](https://github.com/laguagu/claude-code-nextjs-skills) | Copiar carpeta `postgres-semantic-search` a `.claude/skills/` | **MEDIO** | **ALTO** | pgvector semantic + hybrid search con SQLAlchemy/SQL templates, HNSW index tuning, RRF (Reciprocal Rank Fusion) |
| **database-schema-designer** | [github.com/alirezarezvani/claude-skills/tree/main/engineering/database-schema-designer](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/database-schema-designer) | Bundle `engineering-advanced-skills` o copiar carpeta | **BAJO** | **ALTO** | Requisitos → migraciones, types, seed data, **RLS policies** — útil para diseñar esquema multi-tenant en FaberLoom |
| **evaluate-rag** | [github.com/hamelsmu/evals-skills](https://github.com/hamelsmu/evals-skills) (dentro del bundle, skill `evaluate-rag`) | `npx skills add https://github.com/hamelsmu/evals-skills` | **MEDIO** | **ALTO** | Evalúa RAG retrieval y generation quality, LLM-as-a-judge, synthetic data generation, calibración de evaluadores |
| **qdrant/skills** | [github.com/qdrant/skills](https://github.com/qdrant/skills) | `npx skills add qdrant/skills` o `/plugin marketplace add qdrant/skills` | **BAJO** | **ALTO** | Vector search patterns: scaling, hybrid search, tenant isolation, quantization, sharding, monitoring, model migration |
| **claude-memory-skill** | [github.com/hanfang/claude-memory-skill](https://github.com/hanfang/claude-memory-skill) | `git clone https://github.com/hanfang/claude-memory-skill.git` o copiar carpeta | **MEDIO** | **MEDIO** | Memoria episódica + semántica jerárquica, auto-creación de docs de memoria, filesystem persistence, background agents |
| **context-engineering-advisor** | [github.com/deanpeters/Product-Manager-Skills/tree/main/context-engineering-advisor](https://github.com/deanpeters/Product-Manager-Skills/tree/main/context-engineering-advisor) | Copiar carpeta a `.claude/skills/` | **MEDIO** | **ALTO** | Context engineering, token management, chunking strategies, context window analysis — crítico para KB multi-tenant con límites de tokens |
| **memory-systems** | [github.com/muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering) | Copiar carpeta a skills dir | **MEDIO** | **MEDIO** | Diseño de arquitecturas de memoria (short-term, graph-based), context degradation, compression, optimization |
| **skill-validator** | [github.com/agent-ecosystem/skill-validator](https://github.com/agent-ecosystem/skill-validator) | `brew install agent-ecosystem/tap/skill-validator` o `go install` | **BAJO** | **BAJO** | Valida estructura, links rotos, frontmatter, token counts de skills (no KB markdown, pero útil para validar skills propias de MWT/FB) |

### Tabla 2: Skills con relevancia media/baja pero verificables

| Skill | Repo / URL | Instalación | Score MWT | Score FB | Por qué (1 línea) |
|---|---|---|---|---|---|
| **ai-skills / postgres** | [github.com/sanjay3290/ai-skills](https://github.com/sanjay3290/ai-skills) | `/plugin marketplace add sanjay3290/ai-skills` + `/plugin install postgres@ai-skills` | **BAJO** | **MEDIO** | Safe read-only SQL queries contra PostgreSQL; no es pgvector/RAG específico pero permite explorar schemas |
| **markdown-linter-fixer-skill** | [github.com/s2005/markdown-linter-fixer-skill](https://github.com/s2005/markdown-linter-fixer-skill) | Copiar carpeta a `.claude/skills/` | **MEDIO** | **BAJO** | Linting de formato markdown (MD029, etc.) con markdownlint-cli2; NO valida frontmatter de notas ni links internos de KB |
| **skill-md-validator** | [github.com/louloulin/skill-md-validator](https://github.com/louloulin/skill-md-validator) | Desconocida | **BAJO** | **BAJO** | SKILL.md validator tool — mencionado en awesome-agent-skills pero sin documentación clara de instalación |

---

## Skills descartados (mencionados en fuentes pero no aplican o no verificables)

| Skill | Razón descarte |
|---|---|
| **frmoretto/clarity-gate** | Listado en awesome-agent-skills como "epistemic quality verification for RAG", pero no se encontró repo verificable con SKILL.md claro para Claude Code. Parece más un proyecto de MCP/tooling que un skill de agente instalable. |
| **scarletkc/vexor** | Skill genérica de "self-discovery" y mejora de prompts. No tiene componentes específicos de RAG, vector DB, o knowledge management. Es un wrapper de "better prompting". |
| **bobmatnyc/mcp-skillset** | Es un MCP server con RAG híbrido (ChromaDB + Knowledge Graph), no un skill de agente en formato SKILL.md instalable vía skills.sh o copia de carpeta. |
| **SynaLinks/synalinks-memory-skills** | Framework propio (SynaLinks) con su propio ecosistema de memory skills. No compatible con skills.sh ni con Claude Code estándar. |
| **pgvector-hybrid-search** (mcpmarket.com) | Aparece en MCP Market pero sin repo de GitHub verificable identificado. Probablemente es una entrada curada sin skill real detrás. |
| **melodic-software/markdown-linting** | Skill de linting de formato markdown con markdownlint-cli2. No valida frontmatter YAML de una KB, ni verifica links internos entre archivos markdown. Es puramente estilístico. |

---

## Gaps detectados (skills que MWT/FB debería escribir)

| Nombre propuesto | Justificación | Para MWT o FB | Prioridad |
|---|---|---|---|
| **mwt-kb-librarian** | MWT tiene 430 archivos markdown con 8 taxonomías. Necesita un skill que entienda su esquema de frontmatter (dominio, tipo, tags, relaciones) y pueda responder preguntas sobre la KB usando el índice. Similar a `llm-wiki` pero adaptado a la taxonomía MWT. | MWT | **ALTA** |
| **faberloom-pgvector-tenant-isolation** | FaberLoom usa pgvector multi-tenant con 4 capas de visibilidad. Necesita un skill que codifique el patrón de RLS + row-level embedding ownership + query filtering por `organization_id` / `role` / `user_id`. `supabase-postgres-best-practices` cubre RLS general pero no este patrón híbrido. | FB | **ALTA** |
| **faberloom-hybrid-search-pgvector** | Skill específica para implementar hybrid search (BM25 via `tsvector` + pgvector embeddings + RRF) en Supabase/pgvector con SQLAlchemy/Prisma. `postgres-semantic-search` lo toca superficialmente. Necesita ser un skill de agente con slash commands. | FB | **ALTA** |
| **markdown-kb-validator** | Validador de KB markdown: frontmatter schema por tipo de nota, links internos (`[[wiki-links]]` y paths relativos), orphans, circular dependencies, freshness/stale detection. `Vault Health` de DavidROliverBA cubre mucho pero es genérico; MWT necesita uno adaptado a sus 8 taxonomías. | MWT | **ALTA** |
| **rag-retrieval-evaluator** | Skill para evaluar automáticamente retrieval: recall@k, MRR, NDCG, precision@k contra un golden dataset. `evaluate-rag` de hamelsmu existe pero es más general (generation quality). Necesita uno específico para evaluar solo el retrieval layer de FaberLoom. | FB | **MEDIA** |
| **embedding-chunking-strategist** | Skill que guíe la selección de estrategias de chunking (fixed-size, semantic, hierarchical, agentic) y embedding models (OpenAI, Cohere, local) según el tipo de documento. `rag-architect` lo menciona pero no profundiza en pgvector. | FB | **MEDIA** |
| **kb-dependency-graph** | Generar dependency graphs entre archivos markdown de la KB (relaciones de frontmatter, links, taxonomía). `Vault Health` tiene `/dependency-graph` para arquitectura de software, no para KB markdown. | MWT | **MEDIA** |
| **memory-tenant-isolation** | Skill para diseñar memoria aislada por tenant/agente en FaberLoom (memoria personal vs rol vs organización vs pública). `claude-memory-skill` es para un solo usuario. | FB | **MEDIA** |
| **mwt-kb-onboarding** | Skill para que nuevos colaboradores exploren la KB de MWT: tours guiados por dominio, búsqueda semántica local (sin vector DB), discovery de decisiones ADR/RFC. | MWT | **BAJA** |

---

## Caveats técnicos

- **Instalación de bundles vs skills individuales:** `alirezarezvani/claude-skills` se instala como marketplace bundle (`engineering-advanced-skills@claude-code-skills`) que incluye ~25 skills. No se pueden instalar individualmente vía `npx skills add` a menos que se copien las carpetas manualmente. Esto puede saturar el context window si se cargan todos los skills del bundle.

- **Frontmatter validation en Vault Health:** El `frontmatter-validator.py` de DavidROliverBA valida YAML frontmatter contra schemas configurables por tipo de nota. Es un hook de `PostToolUse`, no un skill slash command. Requiere configuración previa de `NOTE_SCHEMAS` en el script.

- **`hanfang/claude-memory-skill` no está en skills.sh:** Se instala vía `git clone` manual. No tiene marketplace ni `npx skills` support. El repo tiene 2.1K stars y está activamente mantenido.

- **`hamelsmu/evals-skills` no está en skills.sh:** Se instala vía `npx skills add https://github.com/hamelsmu/evals-skills`. Es un bundle de evaluación con múltiples skills (`evaluate-rag`, `eval-audit`, `error-analysis`, `generate-synthetic-data`, `write-judge-prompt`, `validate-evaluator`, `build-review-interface`).

- **`qdrant/skills` es Qdrant-specific:** Aunque cubre hybrid search, tenant isolation y sharding, está orientado a Qdrant (vector DB Rust) no a pgvector/Supabase. Los conceptos son transferibles pero las implementaciones de código no.

- **`supabase-postgres-best-practices` no menciona pgvector:** Cubre RLS, performance, schema design, pero no tiene sección específica de pgvector, embeddings, o vector similarity search. Es Postgres general.

- **Conflictos potenciales:** `llm-wiki` (alirezarezvani) y `Vault Health` (DavidROliverBA) ambos operan sobre vaults markdown. Podrían tener triggers superpuestos si ambos están activos. Recomendación: usar `llm-wiki` para ingestion/síntesis y `Vault Health` para validación/mantenimiento, con descripciones YAML cuidadosamente diferenciadas.

- **Dependencias externas:** `postgres-semantic-search` requiere `pgvector` extension instalada en Postgres. `skill-validator` requiere Go o Homebrew. `markdown-linter-fixer-skill` requiere `markdownlint-cli2` (npm).

- **Paths de instalación por agente:**
  - Claude Code: `.claude/skills/` (proyecto) o `~/.claude/skills/` (global)
  - Codex: `.agents/skills/` o `~/.agents/skills/`
  - Cursor: `.cursor/skills/`
  - Los skills bundles de `alirezarezvani` usan el formato de plugin de Claude Code (`/plugin marketplace add` / `/plugin install`).

---

## Resumen ejecutivo

**Para MWT (KB markdown canónica):**
- **Más valiosos:** `Vault Health` de DavidROliverBA (broken-links, frontmatter-validator, orphan-finder) + `llm-wiki` de alirezarezvani (second brain, ingestion, BM25 search).
- **Gap crítico:** No existe un skill específico que entienda las 8 taxonomías de MWT y genere dependency graphs entre archivos. Se recomienda escribir `mwt-kb-librarian` y `markdown-kb-validator`.

**Para FaberLoom (KB-as-a-product con pgvector multi-tenant):**
- **Más valiosos:** `rag-architect` (chunking, retrieval eval, hybrid search) + `database-schema-designer` (RLS policies, migrations) + `postgres-semantic-search` (pgvector híbrido) + `evaluate-rag` (evaluación) + `qdrant/skills` (patrones de vector DB transferibles).
- **Gap crítico:** Falta un skill que codifique el patrón exacto de RLS multi-tenant + pgvector + hybrid search en Supabase. Se recomienda escribir `faberloom-pgvector-tenant-isolation` y `faberloom-hybrid-search-pgvector`.

**Skills ya instaladas (no recomendadas en este informe):**
- `anthropic-skills/*`: docx, pdf, pptx, xlsx, schedule, skill-creator
- `obra/superpowers`: writing-plans, executing-plans, verification-before-completion, writing-skills
- Cowork plugins core
