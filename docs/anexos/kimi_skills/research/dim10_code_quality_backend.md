## DIMENSIÓN 10 — Code Quality, Backend, Testing

### Skills relevantes encontrados

| Skill | Repo | Instalación | Score MWT | Score FB | Por qué (1 línea) |
|---|---|---|---|---|---|
| `supabase-postgres-best-practices` | `github.com/supabase/agent-skills` | `npx skills add supabase/agent-skills --skill supabase-postgres-best-practices` | MEDIO | **ALTO** | 30 reglas de Supabase para query performance, RLS, schema design, migrations — crítico para FaberLoom con pgvector. |
| `fastapi-python` | `mindrally/skills` | `npx skills add https://github.com/mindrally/skills --skill fastapi-python` | MEDIO | **ALTO** | FastAPI + Pydantic v2 + async patterns + RORO + guard clauses — cubre el stack backend de FaberLoom. |
| `fastapi` (jezweb) | `jezweb/claude-skills` | `npx skills add https://github.com/jezweb/claude-skills --skill fastapi` | MEDIO | **ALTO** | FastAPI con Pydantic v2, SQLAlchemy 2.0 async, JWT auth, estructura domain-based — más completo que mindrally. |
| `python-type-safety` | `wshobson/agents` | `npx skills add https://github.com/wshobson/agents --skill python-type-safety` | BAJO | **ALTO** | mypy strict mode, pyright, generics, Protocols, type narrowing — type-safety para Python/Pydantic AI. |
| `python-testing-patterns` | `wshobson/agents` | `npx skills add https://github.com/wshobson/agents --skill python-testing-patterns` | BAJO | **ALTO** | pytest fixtures, markers, parametrization, mocking, async testing — cobertura completa de testing Python. |
| `pytest-coverage` | `github/awesome-copilot` | `npx skills add https://github.com/github/awesome-copilot --skill pytest-coverage` | BAJO | **MEDIO** | pytest + coverage annotate 100% — útil para forzar cobertura total en módulos críticos. |
| `pgvector-semantic-search` | `timescale/pg-aiguide` | `npx skills add https://github.com/timescale/pg-aiguide --skill pgvector-semantic-search` | MEDIO | **ALTO** | HNSW indexing, hybrid search RRF, SQLAlchemy patterns para pgvector — directamente aplicable a FaberLoom. |
| `pydantic-ai-agent-creation` | `existential-birds/beagle` | `npx skills add https://github.com/existential-birds/beagle --skill pydantic-ai-agent-creation` | MEDIO | **ALTO** | Agent setup, model selection, structured outputs, streaming, deps injection para Pydantic AI. |
| `sdd` (Spec-Driven Development) | `NeoLabHQ/context-engineering-kit/plugins/sdd` | `/plugin install sdd@NeoLabHQ/context-engineering-kit` o `npx skills add NeoLabHQ/context-engineering-kit` | **ALTO** | **ALTO** | Arc42-based spec-driven workflow: /add-task → /plan-task → /implement-task con LLM-as-a-Judge quality gates. |
| `tdd` (Test-Driven Development) | `NeoLabHQ/context-engineering-kit/plugins/tdd` | `/plugin install tdd@NeoLabHQ/context-engineering-kit` | **ALTO** | **ALTO** | /write-tests + /fix-tests con anti-pattern detection y subagents para testing. |
| `reflexion` | `NeoLabHQ/context-engineering-kit/plugins/reflexion` | `/plugin install reflexion@NeoLabHQ/context-engineering-kit` | **ALTO** | **MEDIO** | Self-refinement loop con /reflect, /memorize, /critique — mejora calidad de output del agente. |
| `review` | `NeoLabHQ/context-engineering-kit/plugins/review` | `/plugin install review@NeoLabHQ/context-engineering-kit` | **ALTO** | **ALTO** | PR review con 6 agentes especializados: bug-hunter, security-auditor, test-coverage-reviewer, etc. |
| `eval-audit` | `hamelsmu/evals-skills` | `npx skills add https://github.com/hamelsmu/evals-skills --skill eval-audit` | **ALTO** | **ALTO** | Audita pipelines de evaluación LLM y prioriza problemas — skill ancla para eval frameworks. |
| `error-analysis` | `hamelsmu/evals-skills` | `npx skills add https://github.com/hamelsmu/evals-skills --skill error-analysis` | **ALTO** | **ALTO** | Categoriza failure modes en pipelines LLM — crítico para debug de Pydantic AI agents. |
| `evaluate-rag` | `hamelsmu/evals-skills` | `npx skills add https://github.com/hamelsmu/evals-skills --skill evaluate-rag` | **ALTO** | **ALTO** | Evalúa retrieval + generation quality en RAG — FaberLoom usa pgvector para RAG. |
| `write-judge-prompt` | `hamelsmu/evals-skills` | `npx skills add https://github.com/hamelsmu/evals-skills --skill write-judge-prompt` | **ALTO** | **ALTO** | Diseña LLM-as-Judge evaluators para criterios subjetivos — necesario para evaluar Action Engine. |
| `generate-synthetic-data` | `hamelsmu/evals-skills` | `npx skills add https://github.com/hamelsmu/evals-skills --skill generate-synthetic-data` | MEDIO | **MEDIO** | Genera inputs de test sintéticos para evals cuando datos reales son escasos. |
| `validate-evaluator` | `hamelsmu/evals-skills` | `npx skills add https://github.com/hamelsmu/evals-skills --skill validate-evaluator` | MEDIO | **MEDIO** | Calibra LLM judges contra labels humanos con TPR/TNR — para evaluadores confiables. |
| `promptfoo-evals` | `promptfoo/promptfoo` | `/plugin install promptfoo-evals@promptfoo` o copiar a `.claude/skills/` | **ALTO** | **ALTO** | Skill oficial Promptfoo para crear eval suites con assertions deterministas y llm-rubric. |
| `tdd` | `mattpocock/skills` | `npx skills@latest add mattpocock/skills/tdd` | MEDIO | **MEDIO** | Red-green-refactor stricto para TypeScript-first — parcial para Python, útil como referencia. |
| `diagnose` | `mattpocock/skills` | `npx skills@latest add mattpocock/skills/diagnose` | MEDIO | **MEDIO** | 6-phase diagnosis loop: reproduce → minimise → hypothesise → instrument → fix → regression-test. |
| `python-observability` | `wshobson/agents` | `npx skills add https://github.com/wshobson/agents --skill python-observability` | BAJO | **MEDIO** | Logging, monitoring, tracing, metrics, OpenTelemetry para Python backends. |
| `python-error-handling` | `wshobson/agents` | `npx skills add https://github.com/wshobson/agents --skill python-error-handling` | BAJO | **MEDIO** | Exception hierarchy, custom exceptions, error context, recovery patterns en Python. |

### Skills descartados (mencionados pero no aplica)

| Skill | Razón descarte |
|---|---|
| `obra/superpowers` (y skills internas: `test-driven-development`, `systematic-debugging`, `root-cause-tracing`, `verification-before-completion`) | **Ya instalado.** El prompt de misión prohíbe recomendar skills ya instaladas. |
| `obra/test-driven-development` | Ya incluido en `obra/superpowers`. |
| `obra/systematic-debugging` | Ya incluido en `obra/superpowers`. |
| `obra/root-cause-tracing` | Ya incluido en `obra/superpowers` (como referencia de systematic-debugging). |
| `NeoLabHQ/sadd` (Subagent-Driven Development) | Superposición funcional con `obra/superpowers` (subagent-driven ya cubierto). |
| `NeoLabHQ/ddd` (Domain-Driven Development) | Relevante pero más general de arquitectura; FaberLoom ya tiene contract-first definido. |
| `NeoLabHQ/kaizen` | Complementario para mejora continua pero no específico de backend/testing. |
| `NeoLabHQ/git` | Skill de git workflows; útil pero no central para code quality/backend. |
| `NeoLabHQ/docs` | Documentación; desviado del foco de backend/testing. |
| `mattpocock/skills` — `git-guardrails-claude-code` | TypeScript-first, guardrails de git no crítico para FaberLoom backend. |
| `mattpocock/skills` — `setup-pre-commit` | Configura Husky + lint-staged + Prettier — stack Node/TypeScript, no aplica a Python. |
| `alinaqi/claude-bootstrap` (bundle 59 skills) | Framework masivo con superposición alta; skills individuales menos granulares que alternativas dedicadas. |
| `coderabbitai/skills` | Requiere instalación previa del CLI de CodeRabbit (`curl -fsSL cli.coderabbit.ai/install.sh`) + autenticación; dependencia externa no trivial. |
| `deepeval` (skills.rest) | Skill comercial con muy poca información verificable (solo 1 skill encontrado, sin repo GitHub claro). |
| `braintrust` (mcpmarket) | Skill con solo 3 GitHub stars, información limitada, requiere cuenta Braintrust. |
| `testdino-hq/playwright-skill` | Playwright es E2E frontend testing; FaberLoom es backend Python. |
| `DougTrajano/pydantic-ai-skills` | Es un **framework Python** para implementar Agent Skills en Pydantic AI (`pip install pydantic-ai-skills`), no es una skill de agente para instalar en Claude Code. |
| `genius-cai/finance-ai/pgvector` | Skill genérica de pgvector sin el depth de `timescale/pg-aiguide`. |
| `constructive-io/constructive-skills/pgvector-rag` | RAG-focused pero con menos installs y menos documentación que timescale. |

### Gaps detectados (skills que MWT/FB debería escribir)

| Nombre propuesto | Justificación | Para MWT o FB | Prioridad |
|---|---|---|---|
| `pydantic-ai-debugging-tracing` | Ninguna skill cubre debugging de agents Pydantic AI (tool calls, result validation, retries, deps injection). La skill existente solo cubre creación básica. | FB | **ALTA** |
| `fastapi-pydantic-ai-integration` | Skill que una FastAPI + Pydantic AI: endpoints que orquestan agents, streaming SSE, gestión de dependencias compartidas. | FB | **ALTA** |
| `supabase-py-sdk` | La skill `supabase-postgres-best-practices` cubre SQL/Postgres pero no el SDK Python (`supabase-py`) para operaciones client-side, auth, storage. | FB | **ALTA** |
| `rls-testing-automation` | No existe skill específica para testear políticas RLS de Supabase/Postgres con datos sintéticos y casos edge (bypass, privilege escalation). | FB | **ALTA** |
| `pgvector-pydantic-ai` | Skill que una pgvector con Pydantic AI: embeddings, similarity search, hybrid RRF dentro de agents Pydantic AI. | FB | **ALTA** |
| `json-schema-contract-testing` | FaberLoom es contract-first con Action Engine + JSON Schema. Ninguna skill cubre testing automatizado de contratos API contra schemas. | FB | **MEDIA** |
| `action-engine-eval` | Skill para evaluar el Action Engine de FaberLoom: schema compliance, tool calling correctness, intent-action mapping. | FB | **MEDIA** |
| `mypy-strict-config` | `python-type-safety` menciona mypy pero no tiene una skill dedicada a configurar `mypy --strict` en un proyecto nuevo con Pydantic AI. | FB | **MEDIA** |
| `pyright-ci-integration` | Skill para integrar pyright/mypy en CI con GitHub Actions, reportes de errores, baseline establishment. | FB | **MEDIA** |
| `braintrust-deepeval-bridge` | Skill que permita evaluar pipelines Pydantic AI con Braintrust o DeepEval: logging traces, scoring, drift detection. | FB | **BAJA** |

### Caveats técnicos

- **`obra/superpowers` ya cubre TDD, debugging, verification**: No instalar `NeoLabHQ/tdd` ni `mattpocock/tdd` si el objetivo es evitar conflicto de metodologías. Sin embargo, `NeoLabHQ/tdd` añade `/write-tests` y `/fix-tests` como **comandos slash** con subagents, mientras que obra/superpowers usa skills contextuales automáticas. Son complementarios pero pueden generar conflicto de "quién manda" en el workflow.
- **NeoLabHQ skills usan plugin marketplace de Claude Code**: Requieren `/plugin marketplace add NeoLabHQ/context-engineering-kit` y luego `/plugin install <plugin>@NeoLabHQ/context-engineering-kit`. En otros agentes (Cursor, Codex) usar `npx skills add NeoLabHQ/context-engineering-kit`. No todas las skills están indexadas en skills.sh directamente.
- **`hamelsmu/evals-skills` no está en skills.sh**: Se instala directamente desde GitHub: `npx skills add https://github.com/hamelsmu/evals-skills`. Las skills internas se invocan como `/evals-skills:<skill-name>` en Claude Code.
- **`promptfoo-evals` skill**: La skill oficial de Promptfoo se instala desde su repo (`promptfoo/promptfoo`) o se copia manualmente a `.claude/skills/`. Requiere que el proyecto tenga `promptfoo` CLI instalado (`npm install -g promptfoo`).
- **`supabase-postgres-best-practices` complementa MCP server**: Supabase tiene un MCP server para operaciones directas. Esta skill da las **reglas** para que el agente las use correctamente. Funcionan mejor juntos.
- **`mattpocock/skills` son TypeScript-first**: `tdd`, `diagnose`, `git-guardrails` asumen convenciones de Node/TypeScript. Aplicable a Python solo parcialmente; considerar fork/adaptación si se instalan.
- **`pgvector-semantic-search` de timescale**: Solo 293 installs. Skill relativamente nueva (bajo volumen de uso probado) pero con contenido técnico profundo sobre HNSW y RRF.
- **Skills de `wshobson/agents`**: Bundle masivo de ~20 skills Python. Se instalan individualmente con `--skill <name>`. El repo tiene 34.6K stars. Cada skill es independiente y bien enfocada.
- **Sin skills de DeepEval o Braintrust como agent skills maduras**: DeepEval y Braintrust son **plataformas de evaluación**, no skills de agente instalables. No existen skills.sh oficiales o verificables para integrarlos con Claude Code. Recomendaría usar `hamelsmu/evals-skills` + `promptfoo-evals` como alternativa open-source verificable.
- **`pydantic-ai-agent-creation` skill**: Solo 194 installs, 55 stars. Skill muy nueva (2 días desde skills.sh). Cubre conceptos básicos pero no patterns avanzados de producción. Requiere validación práctica antes de confiar para código crítico.
- **Conflictos potenciales TDD**: Si se instalan múltiples skills de TDD (`obra/superpowers`, `NeoLabHQ/tdd`, `mattpocock/tdd`), el agente puede recibir instrucciones contradictorias. Recomendación: quedarse con una (obra para contexto automático, o NeoLabHQ para comandos explícitos).
