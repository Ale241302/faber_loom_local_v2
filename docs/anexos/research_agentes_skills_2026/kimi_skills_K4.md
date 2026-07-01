# K4 - Evals, Testing y CI de Skills

Resumen: La evaluacion de skills en produccion multi-tenant se apoya en un ecosistema emergente de herramientas: SkillsBench para benchmarks deterministas, skill-eval/skillgrade para testing unitario de skills, y plataformas como Braintrust y Confident AI para observability y evals online. Las metricas clave son pass@k (capacidad) vs pass^k (consistencia), con deteccion de regresion via GitHub Actions y trigger accuracy via skill-creator v2. La varianza no-determinista es el problema central: τ-bench reporta 60% pass@1 vs 25% consistencia real. La integracion CI/CD es viable hoy via GitHub Actions (skill-bench/skill-eval-action, mgechev/skill-eval), aunque el monitoreo de tokens por skill en produccion requiere OpenTelemetry manual.

---

## 1. Harness de Evals

### Claim: SkillsBench es el benchmark academico mas completo para evaluar skills, con verificacion determinista (pytest) y evaluacion bajo tres condiciones (no Skills, curated Skills, self-generated Skills)
Source: SkillsBench paper (arXiv)
URL: https://arxiv.org/html/2602.12670v1
Date: 2026-02-13
Excerpt: "We present SkillsBench, a benchmark of 86 tasks across 11 domains paired with curated Skills and deterministic verifiers. Each task is evaluated under three conditions: no Skills, curated Skills, and self-generated Skills. We test 7 agent-model configurations over 7,308 trajectories. Curated Skills raise average pass rate by 16.2 percentage points(pp), but effects vary widely by domain (+4.5pp for Software Engineering to +51.9pp for Healthcare)."
Context: Proporciona una metodologia reproducible para medir el impacto de skills con verificacion determinista en contenedores Docker. El framework Harbor subyacente asegura aislamiento.
Confidence: high

### Claim: skill-eval de Minko Gechev es un framework TypeScript que ejecuta skills en contenedores Docker y combina graders deterministicos con LLM rubric graders
Source: Minko Gechev's blog
URL: https://blog.mgechev.com/2026/02/26/skill-eval/
Date: 2026-02-26
Excerpt: "Skill Eval is a TypeScript framework that benchmarks how well an agent follows your skills. You define a task, point it at your skill, and the framework runs the agent in a Docker container, then grades the result... You can use two types of graders. Deterministic graders run a shell script and check outcomes. LLM rubric graders evaluate qualitative aspects."
Context: Framework open-source que soporta multiples agentes (Gemini, Claude, Codex) y mantiene reportes con historial de scores. Genera tablas con pass rate, pass@k, pass^k, tokens por trial.
Confidence: high

### Claim: skillgrade (mgechev) proporciona presets predefinidos para diferentes niveles de confianza: --smoke (5 trials), --reliable (15 trials), --regression (30 trials)
Source: skillgrade GitHub
URL: https://github.com/mgechev/skillgrade
Date: 2026-02-26
Excerpt: "Presets: --smoke (5 trials, Quick capability check), --reliable (15 trials, Reliable pass rate estimate), --regression (30 trials, High-confidence regression detection)"
Context: La herramienta permite ajustar el numero de corridas segun el objetivo: verificar que funciona vs detectar regresiones con alta confianza. Incluye grader deterministico y LLM rubric con pesos configurables.
Confidence: high

### Claim: Skill Bench (skill-eval-action) es una GitHub Action que evalua skills de Claude Code contra casos YAML con grading automatizado y reporte en PR
Source: GitHub Marketplace
URL: https://github.com/marketplace/actions/skill-eval
Date: 2026 (actualizado continuamente)
Excerpt: "A GitHub Action that evaluates Claude Code skills against YAML test cases with automated grading and PR reporting... eval YAML -> claude -p (execute) -> claude -p (grade) -> summary.json -> PR comment + artifact"
Context: Soporta evaluacion de solo skills cambiadas (changed-only), ejecucion en matriz paralela, y umbral de pass configurable (default 80%). Cada caso hace 2 llamadas API (execute + grade).
Confidence: high

### Claim: skill-creator v2 opera en 4 modos (Create, Eval, Improve, Benchmark) usando 4 sub-agentes en paralelo: executor, grader, comparator, analyzer
Source: Tessl blog
URL: https://tessl.io/blog/anthropic-brings-evals-to-skill-creator-heres-why-thats-a-big-deal/
Date: 2026-03-04
Excerpt: "The updated skill-creator now operates in 4 modes: Create, Eval, Improve, and Benchmark. The interesting addition is the eval pipeline, which uses four composable sub-agents working in parallel: An executor runs skills against eval prompts. A grader evaluates outputs against defined expectations. A comparator performs blind A/B comparisons between skill versions. And an analyzer surfaces patterns that aggregate stats might hide."
Context: El sistema de evals esta integrado en el flujo de skill-creator. Los test cases son JSON con assertions verificables. El comparator hace A/B blind testing.
Confidence: high

---

## 2. Assertions Deterministas vs LLM-as-a-Judge

### Claim: Las evaluaciones hibridas combinan reglas deterministicas (formato, presencia de elementos) con LLM judges (tono, calidad, solucion del problema) y revision humana para casos de alta criticidad
Source: LangChain
URL: https://www.langchain.com/articles/llm-as-a-judge
Date: 2026 (actualizado)
Excerpt: "LLM-based judges: Use these for nuanced quality assessment where 'good' requires judgment. They measure helpfulness, accuracy, appropriate tone, and whether the AI agent actually solved the user's problem. Deterministic rules: Use these for obvious issues like format validation, length constraints, or the presence of required elements. Rules are fast, cheap, and perfectly reliable for what they measure. Use them as your first pass."
Context: Para CI/CD de skills multi-tenant, la recomendacion es: reglas deterministicas como primer filtro (rapido, barato), LLM judges para calidad cualitativa, y human review para calibracion periodica.
Confidence: high

### Claim: Braintrust recomienda una stack de evaluacion en capas: deterministic checks -> LLM-as-a-judge -> human review
Source: Braintrust
URL: https://www.braintrust.dev/articles/what-is-llm-as-a-judge
Date: 2026-02-26
Excerpt: "LLM-as-a-judge operates within a layered evaluation system that combines deterministic checks, model-based scoring, and human oversight. Code-based checks validate structural requirements such as format compliance, length limits, and schema rules, while LLM-as-a-judge evaluates qualitative dimensions that code cannot measure reliably."
Context: En produccion multi-tenant, esta stack en capas permite gatear deployments: primero verificacion estructural rapida, luego evaluacion cualitativa, luego muestreo humano.
Confidence: high

### Claim: skill-eval de mgechev combina deterministic graders (shell scripts) con LLM rubric graders con pesos configurables para balancear "funciona?" vs "lo hizo bien?"
Source: Minko Gechev's blog
URL: https://blog.mgechev.com/2026/02/26/skill-eval/
Date: 2026-02-26
Excerpt: "Each grader returns a score between 0.0 and 1.0 with configurable weights, so you can combine 'did it work?' with 'did it work the right way?'"
Context: En la practica, un grader deterministico verifica que el archivo se corrigio (weight 0.7) y un LLM rubric evalua si siguio el workflow correcto (weight 0.3).
Confidence: high

### Claim: DeepEval de Confident AI usa una arquitectura DAG (Direct Acyclic Graph) para lograr determinismo en evaluaciones con LLM judge
Source: Confident AI
URL: https://www.confident-ai.com/blog/why-llm-as-a-judge-is-the-best-llm-evaluation-method
Date: 2026-05-16
Excerpt: "You can achieve determinism with LLMs by structuring evaluations as a Directed Acyclic Graph (DAG). In this approach, each node represents an LLM judge handling a specific decision, while edges define the logical flow between decisions. By breaking down an LLM interaction into finer, atomic units, you reduce ambiguity and enforce alignment with your expectations."
Context: Para skills multi-tenant, DAG permite granularizar las evaluaciones de judge en decisiones atomicas, reduciendo la varianza del scoring.
Confidence: medium

---

## 3. Variance Analysis

### Claim: Research de τ-bench encontro que agentes con 60% pass@1 exhiben solo 25% consistencia entre multiples corridas
Source: The Context Lab
URL: https://www.thecontextlab.ai/blog/non-determinism-problem-evaluating-agents-reliably
Date: 2026-02-04
Excerpt: "Research from τ-bench found that agents achieving 60% pass@1 on benchmarks may exhibit only 25% consistency across multiple trials. An agent that succeeds more than half the time on a single run might fail three out of four times when you actually need it to work reliably."
Context: Este gap entre benchmark y confiabilidad real es central para skills multi-tenant: un skill que pasa 60% de las veces en eval no garantiza consistencia en produccion.
Confidence: high

### Claim: pass@k mide capacidad (al menos un exito en k intentos) mientras pass^k mide confiabilidad (todos los intentos exitosos). Ambas divergen a medida que k aumenta.
Source: Anthropic Engineering blog
URL: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
Date: 2026-01-08
Excerpt: "pass@k measures the likelihood that an agent gets at least one correct solution in k attempts... pass^k measures the probability that all k trials succeed... pass@k and pass^k diverge as trials increase. At k=1, they're identical. By k=10, they tell opposite stories: pass@k approaches 100% while pass^k falls to 0%."
Context: Para CI/CD de skills: usar pass@5 para verificar que el skill PUEDE resolver el problema; usar pass^5 para verificar que el skill es CONFIABLE en produccion.
Confidence: high

### Claim: Un skill con pass@5=100% pero pass^5=30% indica que el agente puede hacer la tarea pero es inestable -- requiere investigacion del transcript
Source: Minko Gechev's blog (citing Anthropic research)
URL: https://blog.mgechev.com/2026/02/26/skill-eval/
Date: 2026-02-26
Excerpt: "If your skill has pass@5 = 100% but pass^5 = 30%, the agent can do it but is flaky. Investigate the transcript."
Context: Esta heuristica es aplicable directamente a gates de CI/CD: si pass^5 cae por debajo del umbral, fallar el pipeline e investigar el transcript del agente.
Confidence: high

### Claim: Las distribuciones de reward por trial varian significativamente -- un mismo skill puede obtener rewards de 1.0, 0.91, 0.70, 0.70, 0.70 en 5 corridas identicas
Source: Minko Gechev's blog (skill-eval output)
URL: https://blog.mgechev.com/2026/02/26/skill-eval/
Date: 2026-02-26
Excerpt: "Trial 1/5 reward=1.00 (55.0s, 2 cmds, ~716 tokens) | Trial 2/5 reward=0.91 (33.1s, 2 cmds, ~798 tokens) | Trial 3/5 reward=0.70 (46.8s, 2 cmds, ~798 tokens) | Trial 4/5 reward=0.70 (40.5s, 2 cmds, ~648 tokens) | Trial 5/5 reward=0.70 (48.4s, 2 cmds, ~650 tokens) | Pass Rate 80.2%"
Context: La varianza en tokens y duration entre corridas identicas es inherente a LLMs no-deterministicos. Para produccion multi-tenant, se debe monitorear la distribucion completa, no solo la media.
Confidence: high

### Claim: SkillsBench reporto alta varianza en mejora por skill: +16.2pp promedio pero con rango de +13.6pp a +23.3pp segun configuracion agente-modelo
Source: SkillsBench paper
URL: https://arxiv.org/html/2602.12670v1
Date: 2026-02-13
Excerpt: "Skills improve performance by +16.2pp on average across 7 model-harness configurations, but with high variance across configurations (range: +13.6pp to +23.3pp). This variability suggests that Skills efficacy depends strongly on the specific agent-model combination."
Context: La varianza cross-model implica que un skill que funciona bien con Claude puede funcionar diferente con Gemini. En produccion multi-tenant con multiples modelos, se necesita eval por modelo.
Confidence: high

### Claim: Counterfactual Trace Auditing (CTA) revela que pass-rate es "casi silencioso": promedio +0.34pp, stddev 4.4pp, mientras identifica 696 divergencias comportamentales y 522 instancias SIP
Source: Counterfactual Trace Auditing of LLM Agent Skills (arXiv)
URL: https://arxiv.org/abs/2605.11946
Date: 2026-05-12
Excerpt: "Across all 49 tasks the mean pass-rate change is +0.34pp, median 0pp, standard deviation 4.4pp. Only 3 tasks have >=+4pp... the same 49 traces contain 696 behavioral divergences between the with- and without-skill agent (mean 14.2 per task) and 522 SIP instances (mean 10.7 per task)."
Context: El paper demuestra que pass-rate como metrica unica es insuficiente. Para CI/CD de skills multi-tenant, se necesita analisis de trazas (trace auditing), no solo verificacion de resultados.
Confidence: high

---

## 4. Deteccion de Regresion

### Claim: Skill Bench CI/CD puede correr solo skills modificadas en un PR usando git diff, evaluando solo las que tienen directorio evals/
Source: GitHub Marketplace / skill-bench.dev
URL: https://skill-bench.dev/docs/getting-started
Date: 2026
Excerpt: "Combine with dorny/paths-filter or git diff to only eval skills that were modified in the PR... skills=$(git diff --name-only origin/main...HEAD -- 'skills/' | cut -d/ -f2 | sort -u | while read s; do [ -d skills/$s/evals ] && echo $s; done)"
Context: Patron esencial para repos con muchos skills: no evaluar todo en cada PR, solo lo que cambio. Mantiene feedback loops rapidos.
Confidence: high

### Claim: MindStudio evaluation API puede ser llamada desde CI/CD pipelines para deteccion automatica de regresiones: si el score cae bajo umbral, el pipeline fallea antes del deploy
Source: MindStudio blog
URL: https://www.mindstudio.ai/blog/claude-code-skills-2-evaluation-ab-testing/
Date: 2026-03-13
Excerpt: "The MindStudio evaluation API can be called from CI/CD pipelines. When a workflow is updated and a deployment is triggered, an automated evaluation run kicks off using the skill's registered rubric and test dataset. If the score drops below threshold, the pipeline flags it before the change goes live. This catches regressions automatically rather than waiting for someone to notice a problem in production."
Context: Patron de regression gate aplicable a skills multi-tenant: eval automatica en deploy con threshold configurable.
Confidence: high

### Claim: skillgrade soporta modo --regression (30 trials) para deteccion de regresion de alta confianza y modo --ci que falla si el pass rate cae bajo el umbral
Source: skillgrade GitHub
URL: https://github.com/mgechev/skillgrade
Date: 2026-02-26
Excerpt: "--regression: 30 trials, High-confidence regression detection... Exits with code 1 if pass rate falls below --threshold (default: 0.8)... Use --provider=local in CI -- the runner is already an ephemeral sandbox."
Context: El modo regression con 30 trials proporciona la confianza estadistica necesaria para detectar regresiones sutiles. El exit code 1 permite integrar con cualquier CI system.
Confidence: high

### Claim: Confident AI soporta regression tests en CI via deepeval test run y monitoreo de calidad en produccion con alertas en Slack/PagerDuty
Source: Confident AI
URL: https://www.confident-ai.com/
Date: 2026
Excerpt: "Run regression tests on every pull request. If quality drops below thresholds you define, the build fails — no bad prompts make it to production... Automatic detection of AI app failures, quality drift, user sentiment shifts, performance regressions, and cost anomalies in production. Real-time alerts in Slack, PagerDuty, or Teams when quality degrades."
Context: Para skills multi-tenant, la deteccion de drift en produccion complementa los tests pre-deploy. La plataforma correlaciona cost anomalies con quality drift.
Confidence: high

---

## 5. Integracion en CI/CD

### Claim: Minko Gechev proporciona una GitHub Action completa que corre evals en cada PR que toca skills/** o tasks/**, con 5 trials y provider Docker
Source: Minko Gechev's blog
URL: https://blog.mgechev.com/2026/02/26/skill-eval/
Date: 2026-02-26
Excerpt: "name: Skill Eval
on:
  pull_request:
    paths: ['skills/**', 'tasks/**']
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install
      - run: npm run eval my_task -- --trials=5 --provider=docker
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}"
Context: Template funcional listo para usar. El trigger por paths evita correr evals en PRs que no modifican skills.
Confidence: high

### Claim: Skill Bench GitHub Action soporta auto-descubrimiento dinamico de skills con directorio evals/, evaluacion en matriz paralela, y comentarios de PR con tabla pass/fail
Source: GitHub Marketplace
URL: https://github.com/marketplace/actions/skill-eval
Date: 2026
Excerpt: "Auto-discover all skills (dynamic matrix): find skills -name '*.yaml' -path '*/evals/*'... The action posts (or updates) a PR comment with: Pass/fail table with per-case results, Collapsible failed criteria with evidence, Eval metadata (time, tokens, cost, threshold). Comments are upserted using an HTML marker."
Context: El upsert de comentarios evita spam en PRs re-ejecutados. El viewer HTML interactivo permite debugging visual del eval.
Confidence: high

### Claim: Skill Bench recomienda 80% como pass-threshold default (no 100%) porque "la flakiness ocasional es esperada" en evals de LLM
Source: GitHub Marketplace / skill-bench.dev
URL: https://skill-bench.dev/
Date: 2026
Excerpt: "The default pass-threshold is 80 not 100. The agentskills.io best practices say 'occasional flakiness is expected'. Options to reduce flakiness: Relax criteria, Run multiple times and average, Lower threshold -- accept that 70-80% is a realistic pass rate for LLM evals."
Context: Este umbral realista es critico para CI/CD: un 100% es inalcanzable con LLMs no-deterministicos. 70-80% es la zona operativa recomendada.
Confidence: high

### Claim: CircleCI recomienda estructur pipelines en gates: Gate 1 (unit tests, <3min) -> Gate 2 (integration, <10min) -> Gate 3 (full regression, solo en main)
Source: CircleCI blog
URL: https://circleci.com/blog/regression-testing-and-how-to-automate-it-with-ci/
Date: 2026-03-05
Excerpt: "Gate 1: Unit tests and linting. Runs on every commit. Should finish in under 3 minutes. Gate 2: Integration tests and selective regression. Runs on pull requests. Should finish in under 10 minutes. Gate 3: Full regression suite. Runs on merges to main. Parallelized to keep wall-clock time short."
Context: Aplicable a evals de skills: smoke tests rapidos en commit, evals de skills en PR, full benchmark suite en merge a main.
Confidence: high

### Claim: Tessl reporto que skill-creator v2 mejoro un skill existente de 81 a 97.5 (15.7% improvement) despues de iteracion con evals y A/B testing
Source: Dev.to (Debbie O'Brien)
URL: https://dev.to/debs_obrien/i-used-skill-creator-v2-to-improve-one-of-my-agent-skills-in-vs-code-fhd
Date: 2026-03-21
Excerpt: "The improved skill outperformed the baseline on two out of four evals and tied on the other two. The overall result improved from 81 to 97.5. That's a 15.7% improvement."
Context: Flujo real de Create -> Eval -> Improve -> Benchmark que produjo mejora medible. El eval viewer HTML permitio revision humana de los resultados.
Confidence: high

---

## 6. Observability / Traces de Skills en Produccion

### Claim: Claude Code exporta metricas OpenTelemetry incluyendo claude_code.token.usage segmentable por skill.name, plugin.name, y agent.name
Source: Claude Code Docs
URL: https://code.claude.com/docs/en/monitoring-usage
Date: 2025-09-01
Excerpt: "Claude Code exports metrics as time series data via the standard metrics protocol... claude_code.token.usage: Number of tokens used... Break down by type (input/output), user, team, model, skill.name, plugin.name, or agent.name."
Context: En produccion multi-tenant, la segmentacion por skill.name permite atribuir costos de tokens a cada skill individualmente. Requiere CLAUDE_CODE_ENABLE_TELEMETRY=1.
Confidence: high

### Claim: Braintrust captura traces exhaustivos incluyendo duracion, LLM duration, time to first token, prompt tokens, cached tokens, completion tokens, reasoning tokens, y costo estimado
Source: Braintrust
URL: https://www.braintrust.dev/articles/ai-agent-evaluation-framework
Date: 2026-02-02
Excerpt: "Braintrust captures exhaustive traces automatically for every request. Each trace includes duration, LLM duration, time to first token, all LLM calls and tool calls, errors separated by type, prompt tokens, cached tokens, completion tokens, reasoning tokens, and estimated cost."
Context: Para skills multi-tenant, esto permite correlacionar fallos de calidad con consumo de tokens especifico por skill, identificando skills cost-ineficientes.
Confidence: high

### Claim: Braintrust permite filtrar metricas por metadata (cost per feature, per user cohort) y alertar cuando token consumption excede historic averages
Source: Braintrust
URL: https://www.braintrust.dev/articles/ai-agent-evaluation-framework
Date: 2026-02-02
Excerpt: "Agent monitoring dashboards display token usage, latency, request volume, and error rates in real time. These metrics can be filtered by any metadata dimension to show cost per feature or per user cohort... Teams can configure notifications when relevancy scores drop below a threshold or when token consumption exceeds historical averages."
Context: Alertas proactivas cuando un skill consume mas tokens de lo normal pueden indicar degradacion o loops infinitos.
Confidence: high

### Claim: VS Code Copilot captura traces OpenTelemetry de ejecucion de skills incluyendo github.copilot.tool.parameters.skill_name como atributo del span
Source: VS Code Docs
URL: https://code.visualstudio.com/docs/copilot/guides/monitoring-agents
Date: 2026-05-13
Excerpt: "gen_ai.operation.name: execute_tool | github.copilot.tool.parameters.skill_name: For skill invocations | gen_ai.tool.name: Tool name"
Context: El estandar OpenTelemetry para agentes captura invocaciones de skills como spans con atributos especificos, permitiendo tracing distribuido de que skills se invocan en cada request.
Confidence: high

### Claim: Confident AI proporciona "online evaluations" que corren metricas sobre traces en tiempo real a medida que se ingieren
Source: Confident AI Docs
URL: https://www.confident-ai.com/docs/llm-tracing/online-evals
Date: 2026-05-01
Excerpt: "Online evaluations let you run metrics on traces and spans on-the-fly as they're ingested into Confident AI, giving you real-time production monitoring of your AI's quality."
Context: Evaluacion continua en produccion sin bloquear el agente. Las metricas corren asincronamente sobre los traces.
Confidence: high

### Claim: Agent observability requiere tracing del full execution flow: tool calls, memory reads, branching decisions, sub-agent handoffs -- no solo prompt/completion de una sola llamada
Source: Braintrust
URL: https://www.braintrust.dev/articles/agent-observability-tracing-tool-calls-memory
Date: 2026-02-26
Excerpt: "Standard LLM observability captures the prompt, the completion, token counts, and latency for a single model call. Agent observability captures the full execution flow across every step the agent takes, including tool calls, memory reads, branching decisions, and sub-agent handoffs."
Context: Para skills multi-tenant, observability parcial (solo LLM calls) es insuficiente. Se necesita tracing del flujo completo para debuggear por que un skill no se activo o produjo output incorrecto.
Confidence: high

---

## 7. Metricas

### Claim: Las metricas fundamentales de eval de skills son: Pass Rate, pass@k, pass^k, Avg Duration, Total Tokens, y Avg Commands
Source: skill-eval (mgechev) output format
URL: https://blog.mgechev.com/2026/02/26/skill-eval/
Date: 2026-02-26
Excerpt: "Pass Rate 80.2% | pass@5 100.0% | pass^5 100.0% | Avg Duration 44.8s | Avg Commands 2.0 | Total Tokens ~3610 (estimated)"
Context: Estas metricas proporcionan una foto completa: puede hacerlo? (pass@5), lo hace confiablemente? (pass^5), cuanto cuesta? (tokens), cuanto tarda? (duration).
Confidence: high

### Claim: MindStudio A/B testing reporta: averageScore, standardDeviation, breakdown por criterio, delta, confidence, y pValue
Source: MindStudio blog
URL: https://www.mindstudio.ai/blog/claude-code-skills-2-evaluation-ab-testing/
Date: 2026-03-13
Excerpt: "control: { averageScore: 3.8, standardDeviation: 0.5, breakdown: { accuracy: 3.9, completeness: 3.4 } }, treatment: { averageScore: 4.2, standardDeviation: 0.4 }, winner: 'treatment', delta: 0.4, confidence: 0.93, pValue: 0.03"
Context: La estadistica inferencial (pValue, confidence) permite decidir si una mejora es real o ruido. El standardDeviation captura la consistencia del skill.
Confidence: high

### Claim: skill-creator v2 mide trigger accuracy via un loop de optimizacion que evalua should-trigger y should-not-trigger queries, mejorando el recall del skill
Source: Tessl blog / Dev.to (Debbie O'Brien)
URL: https://dev.to/debs_obrien/i-used-skill-creator-v2-to-improve-one-of-my-agent-skills-in-vs-code-fhd
Date: 2026-03-21
Excerpt: "Skill Creator has an eval viewer... It also includes description optimization, which is really important for improving skill triggering accuracy by testing realistic trigger and non-trigger queries. That workflow lets you: review trigger queries, review non-trigger queries, edit them, export the eval set, run the optimization loop."
Context: Trigger accuracy es critica para produccion: un skill excelente que no se activa es inutil. El split train/validation evita overfitting a queries especificas.
Confidence: high

### Claim: agentskills.io recomienda evaluar descripciones en train y validation sets separados, usando solo train para guiar cambios y validation para medir generalizacion
Source: agentskills.io
URL: https://agentskills.io/skill-creation/optimizing-descriptions
Date: 2026-04-22
Excerpt: "Evaluate the current description on both train and validation sets. The train results guide your changes; the validation results tell you whether those changes are generalizing... Select the best iteration by its validation pass rate -- the best description may not be the last one you produced. Five iterations is usually enough."
Context: Metodologia de ML aplicada a descripciones de skills: evitar overfitting a queries de entrenamiento usando validacion separada.
Confidence: high

### Claim: EffectorHQ encontro que 67% de 13,729 skills fallan en practica, motivando la creacion de un framework de evaluacion estatica
Source: effectorHQ / skill-eval
URL: https://github.com/effectorHQ/skill-eval
Date: 2026-03-13
Excerpt: "ClawHub has 13,729 skills. 67% of them fail in practice. The ecosystem needs a way to answer: does this skill actually do what it claims?"
Context: La metrica de tasa de fallo en el ecosistema valida la necesidad de testing obligatorio antes de deploy. El analisis estatico es el primer filtro antes de ejecucion.
Confidence: medium

---

## Anti-patrones de Evaluacion

### Anti-patron 1: "One-shot eval" -- confiar en una sola corrida para decidir si un skill funciona
Source: Multiple sources
URL: https://blog.mgechev.com/2026/02/26/skill-eval/
Excerpt: "Run at least 5 trials. Agent behavior is non-deterministic. A single run means nothing."
Mitigacion: Usar --smoke (5 trials) minimo, --reliable (15) para estimados de pass rate, --regression (30) para deteccion de regresion.
Confidence: high

### Anti-patron 2: "Pass-rate tunnel vision" -- usar solo pass rate como metrica sin analizar el comportamiento subyacente
Source: Counterfactual Trace Auditing paper
URL: https://arxiv.org/abs/2605.11946
Excerpt: "A skill can simultaneously help an agent disambiguate the right file (constructive) and prompt it to write an extra, off-task configuration file (destructive); when both occur, delta-P may stay at zero even though the agent's trajectory has been reshaped along multiple measurable axes."
Mitigacion: Complementar pass rate con trace auditing (CTA), metricas de tokens por tarea, y analisis de divergencias comportamentales.
Confidence: high

### Anti-patron 3: "Threshold 100%" -- esperar que un skill pase 100% de las evaluaciones en CI
Source: skill-bench.dev
URL: https://skill-bench.dev/
Excerpt: "The default pass-threshold is 80 not 100. The agentskills.io best practices say 'occasional flakiness is expected'."
Mitigacion: Configurar threshold en 70-80% para evals de LLM. Monitorear tendencias a lo largo del tiempo, no solo pass/fail binario.
Confidence: high

### Anti-patron 4: "Description overfitting" -- ajustar la descripcion del skill para pasar queries especificas de eval sin generalizar
Source: agentskills.io
URL: https://agentskills.io/skill-creation/optimizing-descriptions
Excerpt: "Avoid adding specific keywords from failed queries -- that's overfitting. Instead, find the general category or concept those queries represent and address that."
Mitigacion: Usar split train/validation para descripciones. Seleccionar la iteracion por validation pass rate, no train pass rate.
Confidence: high

### Anti-patron 5: "Eval silos" -- mantener evals en una herramienta separada del pipeline de deploy
Source: Anthropic / MindStudio
URL: https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
Excerpt: "Automated evals are especially useful pre-launch and in CI/CD, running on each agent change and model upgrade as the first line of defense against quality problems."
Mitigacion: Integrar evals en CI/CD via GitHub Actions (skill-eval-action) o API calls desde el pipeline de deploy. Evaluar en cada cambio de skill, no solo periodicamente.
Confidence: high

---

## Estado de Herramientas: Maduras vs Aspiracionales

### MADURAS (usables hoy en produccion)

| Herramienta | Estado | Uso recomendado |
|---|---|---|
| skill-eval (mgechev) | Stable, open-source | Testing unitario de skills con Docker, deterministic + LLM graders |
| skillgrade (mgechev) | Stable, npm | CLI para eval rapido con presets smoke/reliable/regression |
| skill-eval-action (skill-bench) | GitHub Marketplace | CI/CD de skills con PR comments y viewer HTML |
| skill-creator v2 (Anthropic) | Producto oficial | Flujo Create/Eval/Improve/Benchmark con trigger optimization |
| DeepEval + Confident AI | Enterprise-ready | Framework pytest-style + plataforma de observabilidad y online evals |
| Braintrust | Enterprise-ready | Tracing, eval SDK, cost analytics, alertas |
| SkillsBench | Paper + dataset | Benchmark academico con verificacion determinista |
| ccusage / Claude-Code-Usage-Monitor | CLI tools open-source | Monitoreo de token consumption local/historico |
| Claude Code OpenTelemetry | Feature oficial | Export de metricas incluyendo token.usage por skill.name |

### ASPIRACIONALES (en desarrollo o con limitaciones significativas)

| Herramienta | Limitacion | Estado |
|---|---|---|
| Counterfactual Trace Auditing (CTA) | Paper academico; no hay herramienta productiva disponible. Requiere implementacion manual del pipeline. | Research |
| effectorHQ/skill-eval | Solo analisis estatico (v0.1.x). Execution sandbox y CI integration vienen en v0.2.0/v0.3.0 | Early alpha |
| MindStudio Eval API para CI/CD | Documentada pero requiere MINDSTUDIO_API_KEY y setup de cuenta. No es self-hosted. | Documentada, vendor-lock-in |
| Skill-creator trigger detection | Bug reportado: 0% recall para skills de usuario via claude -p (issue #1249 en GitHub). Solo funciona para skills donde Claude no puede proceder sin consultar el skill. | Bug conocido |
| Unified skill observability standard | Cada plataforma (Claude Code, Copilot, Cursor) usa atributos OTel diferentes. No hay estandar cross-platform para skill.name, skill.version, skill.trigger_accuracy. | Fragmentado |
| Variance analysis automatizado | No hay herramienta que automaticamente detecte skills con alta varianza y alerte. Se requiere analisis manual de distribuciones. | Gap identificado |
| Token consumption forecasting | Existe tracking historico (ccusage) pero no prediccion de costo por skill en tenant nuevos. | Gap identificado |

---

## Key Takeaways para MWT Multi-Tenant

1. **Evals en CI/CD son viables hoy**: skill-eval-action (GitHub Actions) + skillgrade (--regression 30 trials) proporcionan un pipeline funcional con PR comments y gating por threshold.

2. **pass^k > pass@k para produccion**: En multi-tenant, la consistencia importa mas que la capacidad. Un skill que funciona 30% de las veces (pass^5=30%) no es deployable aunque pass@5=100%.

3. **Trigger accuracy es critico y testeable**: skill-creator v2 y agentskills.io proporcionan metodologia para evaluar should-trigger/should-not-trigger con split train/validation.

4. **Observabilidad requiere OpenTelemetry**: Claude Code ya exporta skill.name en metricas OTel. Braintrust/Confident AI proveen las capas de analisis y alerta encima.

5. **La varianza es el enemigo principal**: τ-bench (60%->25%), SkillsBench (+13.6pp a +23.3pp rango), y CTA (stddev 4.4pp) demuestran que los numeros agregados esconden inconsistencias criticas.

6. **80% es el umbral operativo realista**: 100% es inalcanzable con LLMs no-deterministicos. La combinacion de threshold 80% + monitoreo de tendencias + alertas de drift es el patron productivo.
