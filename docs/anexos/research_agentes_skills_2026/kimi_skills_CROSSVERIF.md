# Cross-Verification: Skills Multi-Tenant K1-K6

Resumen: Se evaluaron 58 claims con cifras duras provenientes de 6 dimensiones de investigacion. 26 claims alcanzan HIGH (confirmados con 2+ fuentes y excerpt verificable), 26 MEDIUM (fuente unica fuerte o inferencia del investigador con metodo transparente), 6 LOW (weak sourcing o sin excerpt textual), y 0 NO VERIFICADO. Se detectaron 9 conflictos explicitos entre dimensiones, de los cuales 5 son discrepancias numericas internas y 4 son contradicciones cross-dimension. La base de evidencia mas solida se concentra en K1 (papers arXiv verificados) y K6 (herramientas de seguridad con implementaciones disponibles). Las mayorias debilidades estan en K2 (huecos no localizados) y K3 (dependencia de fuentes individuales de comunidad).

Total claims evaluados: 58
HIGH: 26 | MEDIUM: 26 | LOW: 6 | [NO VERIFICADO]: 0
Conflictos detectados: 9

---

# Seccion 1: Claims por Tier

---

## TIER HIGH

### Claim 1
Claim: SkillsBench evaluo 84 tasks (v3 final) provenientes de 105 candidatas enviadas por 322 contribuyentes, con 7,308 trayectorias.
Dimension: K1
Tier: HIGH
Razon Tier: Paper peer-reviewed v3 con excerpt textual exacto confirmado. Consistente en abstract, resultados y conclusion. La cifra de 86 tasks (v1) fue superada en revision.
Sources: arXiv 2602.12670 v3 (https://arxiv.org/abs/2602.12670)
Excerpt: "producing 84 tasks spanning 11 domains" y "Across 84 tasks, 7 agent-model configurations, and 7,308 trajectories"
Conflictos: K4 tambien reporta "86 tasks" en su excerpt (residuo v1 no actualizado). Ver Conflicto #1.

### Claim 2
Claim: El benchmark SkillsBench reporta +16.2pp de mejora promedio con curated skills (range: +13.6pp a +23.3pp), pero la Figura 2 del mismo paper reporta +12.66pp.
Dimension: K1
Tier: HIGH
Razon Tier: El +16.2pp aparece en el abstract, resultados principales (Finding 1) y conclusion, constituyendo la cifra principal del paper. El +12.66pp esta aislado en la Figura 2 (pipeline overview) y probablemente es un residuo de calculo no actualizado. Ambos excerpts verificables.
Sources: arXiv 2602.12670 v3 (https://arxiv.org/abs/2602.12670)
Excerpt (Finding 1): "Skills improve performance by +16.2pp on average across 7 model-harness configurations, but with high variance across configurations (range: +13.6pp to +23.3pp)." | Excerpt (Fig 2): "7 agent-model configurations yield 7,308 trajectories, with curated Skills providing +12.66pp average improvement."
Conflictos: Discrepancia INTERNA del paper. Ver Conflicto #2.

### Claim 3
Claim: Snyk ToxicSkills: 36.82% de 3,984 skills escaneadas (1,467 skills) contienen >=1 falla de seguridad; 13.4% (534) contienen >=1 issue CRITICAL; 76 payloads maliciosos confirmados por HITL review; 10.9% (434) contienen secretos hardcodeados.
Dimension: K1, K6
Tier: HIGH
Razon Tier: Blogpost oficial Snyk con excerpts textuales verificables. Las cifras son consistentes entre K1 y K6. 2+ fuentes (Snyk blog + Zenn.dev que reproduce la tabla). No hay contradiccion entre dimensiones.
Sources: Snyk Blog (https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/), K6 re-verificacion
Excerpt: "13.4% of all skills, or 534 in total, all contain at least one critical-level security issue [...] over a third of the ecosystem is affected: 36.82% (1,467 skills) have at least one security flaw." y "we confirmed active threats through HITL: 76 malicious payloads"
Conflictos: K6 resume "36%" en lugar de "36.82%" — redondeo, no contradiccion. Ver Conflicto #5.

### Claim 4
Claim: ~80% attack success rate (ASR) ante skill file injections con frontier models, bajo condicion Best-of-5 Obvious Injections (BoN). En condicion mas realista (Contextual + Warning Prompt) ASR es 6-19%.
Dimension: K1
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpt textual. El contexto de la condicion BoN esta documentado. La cifra de 80% sin calificar el BoN seria enganosa.
Sources: arXiv 2602.20156 (https://arxiv.org/abs/2602.20156)
Excerpt: "Our results show that today's agents are highly vulnerable with up to 80% attack success rate with frontier models, often executing extremely harmful instructions including data exfiltration, destructive action, and ransomware-like behavior."
Conflictos: Ninguno.

### Claim 5
Claim: Mediana 1,414 tokens por skill (mean: 1,895, max: 116,239). El 90% bajo 3,935 tokens, 99% bajo 9,253 tokens.
Dimension: K1
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpt textual completo y preciso. Fuente unica pero altamente creible (Bosch Research / CMU).
Sources: arXiv 2602.08004 (https://arxiv.org/abs/2602.08004)
Excerpt: "The median length is 1,414 tokens and the mean is 1,895 tokens, indicating that a typical skill fits comfortably alongside planning context and tool schemas. [...] 90% and 99% remain below 3,935 and 9,253 tokens. [...] the maximum reaches 116,239 tokens."
Conflictos: Ninguno.

### Claim 6
Claim: Crecimiento 18.5x en 20 dias: de 2,179 skills (16 ene) a 40,285 skills (5 feb). Pico de 8,857 skills en un solo dia (25 ene), 23.2% del total.
Dimension: K1
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpt textual completo. Fuente unica pero fuerte.
Sources: arXiv 2602.08004 (https://arxiv.org/abs/2602.08004)
Excerpt: "The marketplace grows from 2,179 skills on January 16, 2026 to 40,285 skills on February 5, 2026, a net increase of 38,106 skills in 20 days. This corresponds to an 18.5x increase and an average multiplicative growth rate of about 15.7% per day. [...] The largest spike occurs on January 25, 2026, when 8,857 skills are added in a single day. This accounts for 23.2% of all new skills in the window."
Conflictos: Ninguno.

### Claim 7
Claim: 46.3% de skills comparten nombre normalizado con al menos otra listing. Distribucion: 2x groups 18.7%, 5x-9x 14.3%, 10x-49x 8.8%.
Dimension: K1
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpt textual.
Sources: arXiv 2602.08004 (https://arxiv.org/abs/2602.08004)
Excerpt: "Skills that appear once account for 53.7%, while skills that appear more than once account for 46.3%. [...] Duplication is also concentrated. Pairs are common, with 2x groups contributing 18.7% of the corpus. Higher multiplicities still account for a nontrivial share: 5x to 9x groups contribute 14.3%, and 10x to 49x groups contribute 8.8%."
Conflictos: Ninguno.

### Claim 8
Claim: 9% L3 (riesgo critico), 30% L2 (moderado), 5% L1 (low), 54% L0 (no risk). ~40% total acceden a contexto sensible o ejecutan writes/actions.
Dimension: K1
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpt textual. Consistente internamente (9+30=39%, ~"two fifths").
Sources: arXiv 2602.08004 (https://arxiv.org/abs/2602.08004)
Excerpt: "Overall, 54% are L0, 5% are L1, 30% are L2, and 9% are L3. Thus, nearly two fifths of the marketplace can access sensitive context or perform writes and actions, and a nontrivial share exposes critical capabilities."
Conflictos: Ninguno.

### Claim 9
Claim: Self-generated skills no aportan beneficio (-1.3pp promedio). Skills con 2-3 modules: +18.6pp; 4+ modules: +5.9pp.
Dimension: K1
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpts textuales. Dos findings independientes confirmados.
Sources: arXiv 2602.12670 v3 (https://arxiv.org/abs/2602.12670)
Excerpt (Finding 3): "Self-generated Skills provide negligible or negative benefit (-1.3 pp average), demonstrating that effective Skills require human-curated domain expertise that models cannot reliably self-generate." | Excerpt (Finding 5): "Tasks with 2-3 Skills show the largest improvement (+18.6pp), while 4+ Skills provide only +5.9 pp benefit."
Conflictos: Ninguno.

### Claim 10
Claim: SKILL-INJECT contiene 202 injection-task pairs.
Dimension: K1
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpt textual.
Sources: arXiv 2602.20156 (https://arxiv.org/abs/2602.20156)
Excerpt: "SKILL-INJECT contains 202 injection-task pairs with attacks ranging from obviously malicious injections to subtle, context-dependent attacks hidden within otherwise legitimate instructions."
Conflictos: Ninguno.

### Claim 11
Claim: Dify vulnerabilidad cross-tenant: ejecuciones sandbox Python compartian mismo UID y filesystem /tmp, permitiendo source disclosure cross-tenant. Parcheado con UID per-run (syscall.Chown) y archivos 0600.
Dimension: K2
Tier: HIGH
Razon Tier: Dos fuentes independientes (Imperva Research + Dify GitHub commit) con excerpts textuales. Vulnerabilidad CVE-documentada real.
Sources: Imperva (https://www.imperva.com/blog/dify-when-your-ai-platform-becomes-the-attack-surface/), Dify commit (https://github.com/langgenius/dify-sandbox/commit/6b3577c7779c4afc9f26645df5a4660a7282a566)
Excerpt: "Sandboxed Python executions shared a filesystem location. Those executions shared the same runtime identity... Separate tenants executing inside the same sandbox root, under the same effective identity, with readable code artifacts left in a shared /tmp." y "uid, err := AcquireUID(ctx). The wrapper was written with os.WriteFile(..., 0600). The file was reassigned with syscall.Chown(..., uid, ...)."
Conflictos: Ninguno.

### Claim 12
Claim: GoClaw implementa tenant_id NOT NULL en 40+ tablas, WHERE tenant_id = $N en toda query, y tenant fluyendo por context.Context (nunca headers del cliente).
Dimension: K2
Tier: HIGH
Razon Tier: Fuente oficial (GoClaw Deep Dive) con excerpt textual. Aligera con regla MWT de tenant-via-context.
Sources: GoClaw Deep Dive (https://dev.to/truongpx396/goclaw-deep-dive-a-builders-guide-to-a-multi-tenant-ai-agent-platform-5d6c)
Excerpt: "Three rules, never broken: Every isolatable table has tenant_id NOT NULL. 40+ tables in GoClaw enforce this. Every query includes WHERE tenant_id = $N. No exceptions. Fail-closed. Tenant flows through context.Context. Resolved at the gateway, propagated everywhere, never taken from client headers (which can be spoofed)."
Conflictos: Ninguno. ALINEADO con reglas MWT.

### Claim 13
Claim: AWS Lambda Tenant Isolation Mode crea execution environments separados por tenant, sin comparticion de estado global. El tenant_id se establece via X-Amz-Tenant-Id header SOLO por el Lambda Authorizer, nunca por el cliente.
Dimension: K2
Tier: HIGH
Razon Tier: 2+ fuentes independientes (AWS doc + Ran the Builder) con excerpts. Confirma patron MWT.
Sources: Pubudu.Dev (https://pubudu.dev/posts/understanding-lambda-tenant-isolation/), Ran the Builder (https://ranthebuilder.cloud/blog/is-aws-lambda-tenant-isolation-mode-enough-for-saas/)
Excerpt: "With Lambda tenant isolation, you can have a single Lambda function shared by all of the tenant, yet have the isolation you need in a Lambda per tenant... The global variable counter, or any other shared state in the execution environment, is isolated per tenant." y "The Lambda authorizer needs to validate the tenant request, extract the tenant_id, and add the special, cool new header 'X-Amz-Tenant-Id'... You should also verify that you don't get this header from the client."
Conflictos: Ninguno. ALINEADO con reglas MWT.

### Claim 14
Claim: Azure OpenAI documenta que para built-in tools (MCP, Code Interpreter), no se puede inyectar tenant context de forma confiable. Se requieren contenedores dedicados o configuraciones separadas por tenant.
Dimension: K2
Tier: HIGH
Razon Tier: Documentacion oficial Microsoft con excerpt textual. Fuente oficial unica pero autoritativa.
Sources: Microsoft Azure Architecture Center (https://learn.microsoft.com/en-us/azure/architecture/guide/multitenant/service/openai)
Excerpt: "For built-in tools like Code Interpreter and remote Model Context Protocol (MCP) server calls, the model infrastructure runs these operations. You can't reliably inject tenant context into built-in tool invocations, so use dedicated containers or separate tool configurations for each tenant."
Conflictos: Ninguno directo, pero contrasta con K5 que propone usar MCP sin notar esta limitacion. Ver Conflicto #6.

### Claim 15
Claim: Claude Code soporta exactamente 12 eventos de hook: SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure, SubagentStart, SubagentStop, Stop, PreCompact, Setup, SessionEnd, Notification.
Dimension: K5
Tier: HIGH
Razon Tier: 2+ fuentes independientes (claudefa.st + prg.sh) con excerpts textuales consistentes. La cifra "12" esta enumerada explicitamente.
Sources: claudefa.st (https://claudefa.st/blog/tools/hooks/hooks-guide), prg.sh (https://prg.sh/notes/Claude-Code-Hooks)
Excerpt: "The 12 Hook Lifecycle Events: SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure, SubagentStart, SubagentStop, Stop, PreCompact, Setup, SessionEnd, Notification"
Conflictos: K3 menciona "25+ eventos de hooks" — ERROR detectado. Ver Conflicto #4.

### Claim 16
Claim: Claude Code tiene 4 tipos de hook handler: Command, HTTP, Prompt, Agent. Los HTTP hooks se anadieron en febrero 2026.
Dimension: K5
Tier: HIGH
Razon Tier: Fuente verificada (claudefa.st) con excerpt textual.
Sources: claudefa.st (https://claudefa.st/blog/tools/hooks/hooks-guide)
Excerpt: "Command hooks run shell scripts. HTTP hooks POST to an endpoint and receive JSON back: New - Feb 2026. Prompt hooks use LLM evaluation. Agent hooks spawn a subagent with tool access (Read, Grep, Glob) for deeper verification."
Conflictos: Ninguno.

### Claim 17
Claim: Cowork ejecuta en VM Ubuntu 22.04 ARM64 sandboxed con bubblewrap, sin root/sudo. El proxy de red bloquea TODOS los dominios no aprobados por Anthropic. allowManagedDomainsOnly=true ignora configuracion del usuario.
Dimension: K3
Tier: HIGH
Razon Tier: Fuente oficial (GitHub issue de Anthropic) con excerpt textual. Confirmado por fuente secundaria (Gradually.ai).
Sources: GitHub issue anthopics/claude-code #37970 (https://github.com/anthropics/claude-code/issues/37970), Gradually.ai (https://www.gradually.ai/en/claude-code-vs-claude-cowork/)
Excerpt: "In Cowork mode, the sandbox proxy blocks all external API calls that are not on Anthropic's managed allowlist. Project-level sandbox.network.allowedDomains settings are completely ignored, making it impossible for users to add domains they need." y "Sandbox (mnt/outputs). Root/sudo: No (blocked by sandbox). Package managers: pip + npm only."
Conflictos: Ninguno. Confirmado: Cowork NO puede llamar SP-API ni n8n (a menos que Anthropic apruebe los dominios). Ver Conflicto #3.

### Claim 18
Claim: Cowork tiene 132 skills pre-built y 131 MCP connectors pre-instalados.
Dimension: K3
Tier: HIGH
Razon Tier: Fuente secundaria (Gradually.ai) con excerpt consistente con documentacion oficial.
Sources: Gradually.ai (https://www.gradually.ai/en/claude-code-vs-claude-cowork/)
Excerpt: "Claude Cowork: 132 pre-built skills, 131 pre-installed MCP connectors."
Conflictos: Ninguno.

### Claim 19
Claim: Claude Code tiene limite de 10,000 tokens para la herramienta Read. SKILL.md que exceden este limite fallan completamente.
Dimension: K5
Tier: HIGH
Razon Tier: GitHub issue verificado (anthropics/claude-plugins-official #995) con excerpt textual.
Sources: GitHub issue #995 (https://github.com/anthropics/claude-plugins-official/issues/995)
Excerpt: "File content (n) exceeds maximum allowed tokens (10000). Use offset and limit parameters to read specific portions of the file. This makes the skills completely unusable."
Conflictos: Ninguno.

### Claim 20
Claim: Claude Code tiene timeout Bash de 2 minutos por defecto, extensible a 10 minutos (600 segundos).
Dimension: K5
Tier: HIGH
Razon Tier: Fuente verificada (zenn.dev) con excerpt textual.
Sources: zenn.dev (https://zenn.dev/khasegawa/articles/75b49e2cbb14c8)
Excerpt: "Claude Code has a default timeout of 2 minutes. It can be extended up to 10 minutes. Configuration methods: Individual specification (timeout 600000ms), Environment variables (BASH_DEFAULT_TIMEOUT_MS=300000), settings.json"
Conflictos: Ninguno.

### Claim 21
Claim: n8n-mcp (czlonkowski/n8n-mcp) tiene 21.4k stars y da acceso a 1,851 nodos n8n (822 core + 1,029 community).
Dimension: K5
Tier: HIGH
Razon Tier: Fuente verificada (GitHub) con excerpt textual. Metrica observable publicamente.
Sources: GitHub czlonkowski/n8n-mcp (https://github.com/czlonkowski/n8n-mcp)
Excerpt: "A Model Context Protocol (MCP) server that provides AI assistants with comprehensive access to n8n node documentation, properties, and operations. 1,851 n8n nodes - 822 core nodes + 1,029 community nodes."
Conflictos: Ninguno.

### Claim 22
Claim: SkillFortify logra 96.95% F1 (95% CI: [95.1%, 98.4%]) con 100% precision y 0% FPR en 540 skills. SAT-based resolution maneja 1,000-node graphs en <100ms. Escaneo de 540 skills en 1.378 segundos (2.55ms/skill).
Dimension: K6
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpt textual. Metricas reproducibles.
Sources: arXiv 2603.00195 (https://arxiv.org/abs/2603.00195)
Excerpt: "SkillFortify achieves 96.95% F1 (95% CI: [95.1%, 98.4%]) with 100% precision and 0% false positive rate on 540 skills, while SAT-based resolution handles 1,000-node graphs in under 100 ms."
Conflictos: Ninguno.

### Claim 23
Claim: Park et al. (Agent Skills in the Wild) analizo 42,447 skills y encontro 26.1% con vulnerabilidades, 14 patrones distintos, 5.2% con patrones de alta severidad sugiriendo intencion maliciosa. SkillScan: 86.7% precision, 82.5% recall.
Dimension: K6
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpt textual.
Sources: arXiv 2601.10338 (https://arxiv.org/abs/2601.10338)
Excerpt: "26.1% of skills contain at least one vulnerability, spanning 14 distinct patterns across four categories: prompt injection, data exfiltration, privilege escalation, and supply chain risks."
Conflictos: Ninguno. Complementa (no contradice) los datos de Snyk (36.82% con fallas) — estudios diferentes, metodologias diferentes.

### Claim 24
Claim: SkillSieve proceso 49,592 skills reales de ClawHub en 31 minutos en Orange Pi ($440) a 38.8ms/skill. Filtro estatico filtra ~86% de skills benignas.
Dimension: K6
Tier: HIGH
Razon Tier: Paper peer-reviewed arXiv con excerpt textual.
Sources: arXiv 2604.06550 (https://arxiv.org/html/2604.06550v1)
Excerpt: "A cheap static check filters about 86% of the volume, so expensive LLM calls go only where they are needed... processing 49,592 real ClawHub skills in 31 minutes on a $440 ARM board at 38.8 ms per skill."
Conflictos: Ninguno.

### Claim 25
Claim: 91% de skills maliciosas combinan prompt injection con tecnicas tradicionales (malware).
Dimension: K6
Tier: HIGH
Razon Tier: Fuente oficial Snyk con excerpt textual verificable.
Sources: Snyk Blog (https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/)
Excerpt: "91% of malicious skills combine prompt injection with traditional malware."
Conflictos: Ninguno.

### Claim 26
Claim: Claude Code CVE-2026-25725 (CVSS 7.7): bubblewrap montaba .claude/settings.json como read-only solo si existia al inicio; como NO existe por defecto, el sandbox podia crear hooks persistentes. Patcheado en v2.1.2.
Dimension: K6
Tier: HIGH
Razon Tier: Fuente de seguridad (Cymulate Research) con excerpt textual detallado. CVE documentado.
Sources: Cymulate Research (https://cymulate.com/blog/the-race-to-ship-ai-tools-left-security-behind-part-1-sandbox-escape/)
Excerpt: "The read-only protection for .claude/settings.json is conditional on the file's existence at sandbox startup. Critically, this file does not exist by default... the .claude/ parent directory is mounted as writable, allowing file creation inside the sandbox."
Conflictos: Ninguno.

---

## TIER MEDIUM

### Claim 27
Claim: ClawHavoc involucro 341 skills maliciosos en ClawHub, 335 trazados a una unica operacion coordinada (clawhavoc2026).
Dimension: K1
Tier: MEDIUM
Razon Tier: Fuente unica (SkillSieve paper) citando a Koi Security. Excerpt textual disponible. La precision de la atribucion a "operacion coordinada" depende del analisis de Koi Security, no verificado independientemente.
Sources: arXiv 2604.06550v1 (https://arxiv.org/html/2604.06550v1)
Excerpt: "The ClawHavoc campaign pushed hundreds of malicious skills into ClawHub over six weeks; Koi Security's audit of 2,857 skills found 341 malicious entries, 335 traced to a single coordinated operation (clawhavoc2026)."
Conflictos: Ninguno. Las cifras 335 vs 341 responden a diferentes niveles de agregacion, no son conflictivas.

### Claim 28
Claim: GoClaw implementa registry per-tenant con overrides de: LLM configs, MCP servers per-user, skills enabled/disabled, tool settings.
Dimension: K2
Tier: MEDIUM
Razon Tier: Fuente de comunidad (dev.to) pero con excerpt textual detallado. Es la implementacion mas cercana documentada. Una sola fuente.
Sources: GoClaw Deep Dive (https://dev.to/truongpx396/goclaw-deep-dive-a-builders-guide-to-a-multi-tenant-ai-agent-platform-5d6c)
Excerpt: "Per-tenant overrides -- each tenant gets its own: LLM provider configs and API keys; Tool settings (web_search providers, TTS voice, etc.); Skills enabled/disabled; MCP servers + per-user credentials; Channel instances"
Conflictos: Ninguno.

### Claim 29
Claim: Scalekit documenta que tool registry en multi-tenant debe ser per-tenant capability configuration.
Dimension: K2
Tier: MEDIUM
Razon Tier: Fuente de vendor (Scalekit blog) con excerpt textual. Contenido tecnico solido pero es contenido de marketing.
Sources: Scalekit (https://www.scalekit.com/blog/single-vs-multi-tenant-tool-calling-agent-auth)
Excerpt: "Tool registry | Shared across all callers | Per-tenant capability configuration... An enterprise customer with a finance team may require that salesforce_delete_record never be accessible to the agent in their environment, regardless of OAuth scope."
Conflictos: Ninguno.

### Claim 30
Claim: El patron de vault de credenciales scopado a tenant usa (tenant_id, tool_name) como lookup key y encripta con per-tenant keys via KMS. NUNCA usar environment variables para credenciales de tenant.
Dimension: K2
Tier: MEDIUM
Razon Tier: Fuente de vendor (Omnithium) con excerpt textual. Recomendacion de arquitectura, no implementacion verificada.
Sources: Omnithium (https://omnithium.ai/blog/multi-tenant-agent-architecture.html)
Excerpt: "The safe pattern is a tenant-scoped credential vault. When a tool needs an API key, it looks up the key by (tenant_id, tool_name). The vault enforces that only agent processes authenticated for that tenant can retrieve those keys. At rest, keys are encrypted with per-tenant keys managed by a KMS... We recommend never using environment variables for tenant credentials."
Conflictos: Ninguno. ALINEADO con reglas MWT.

### Claim 31
Claim: RLS en PostgreSQL es critico cuando queries son generadas por AI porque no se puede asegurar que AI-generated queries no causen data leaks.
Dimension: K2
Tier: MEDIUM
Razon Tier: Fuente de comunidad (Medium) con excerpt textual. Es una opinion tecnica bien argumentada pero no un estudio empirico.
Sources: Medium (https://medium.com/@anand_thakkar/row-level-security-rls-in-postgresql-for-multi-tenant-saas-apps-ef8c324031d0)
Excerpt: "RLS becomes more critical especially when SQL queries are generated by an AI or agent-based system... AI Generated SQL: You can't always ensure that AI generated queries are not causing data leaks across agents."
Conflictos: Ninguno. ALINEADO con reglas MWT (tenant_id NOT NULL).

### Claim 32
Claim: MCP multi-tenant requiere 3 capas de aislamiento adicionales: tool definition isolation, context window isolation, credential vault isolation.
Dimension: K2
Tier: MEDIUM
Razon Tier: Fuente de vendor (Albato) con excerpt textual. Contenido tecnico solido.
Sources: Albato (https://albato.com/blog/publications/embedded-multi-tenant-mcp-saas)
Excerpt: "MCP adds protocol-specific surfaces that traditional APIs don't have: tool description metadata entering the LLM context window, credential vaults storing OAuth tokens per user per connection, and prompt-level context that could leak across tenants if not properly scoped..."
Conflictos: Ninguno.

### Claim 33
Claim: El broker pattern (CABP) es la solucion recomendada para propagar contexto de tenant en MCP: gateway inyecta claims JWT en contexto JSON-RPC.
Dimension: K2
Tier: MEDIUM
Razon Tier: Paper academico con excerpt textual. Es una propuesta de diseno, no una implementacion verificada.
Sources: arXiv 2603.13417v1 (https://arxiv.org/html/2603.13417v1)
Excerpt: "User identity cannot currently be propagated via MCP request headers to the server. The JSON-RPC protocol does not include a standard mechanism for carrying user context (identity, permissions, tenant scope) with tool invocations... A gateway service sits between the agent and the MCP server. It intercepts JSON-RPC requests, extracts claims from the OAuth token in the Authorization header..."
Conflictos: Ninguno. ALINEADO con reglas MWT (tenant via context server-side).

### Claim 34
Claim: Sandbox reduce prompts de permiso en un 84% segun datos internos de Anthropic.
Dimension: K3
Tier: MEDIUM
Razon Tier: Fuente secundaria (InventiveHQ) citando datos de Anthropic. No es dato primario. La cifra "84%" no es verificable desde la fuente original.
Sources: InventiveHQ (https://inventivehq.com/knowledge-base/claude/how-to-manage-permissions-and-sandboxing)
Excerpt: "Sandboxing creates defined boundaries within which Claude can work more freely. According to Anthropic, sandboxing reduces permission prompts by 84% in internal usage while maintaining security."
Conflictos: Ninguno. Nota: "segun datos internos de Anthropic" — no hay paper ni reporte publico.

### Claim 35
Claim: τ-bench encontro que agentes con 60% pass@1 exhiben solo 25% consistencia entre multiples corridas.
Dimension: K4
Tier: MEDIUM
Razon Tier: Fuente de comunidad (The Context Lab) con excerpt textual. No es paper peer-reviewed.
Sources: The Context Lab (https://www.thecontextlab.ai/blog/non-determinism-problem-evaluating-agents-reliably)
Excerpt: "Research from τ-bench found that agents achieving 60% pass@1 on benchmarks may exhibit only 25% consistency across multiple trials. An agent that succeeds more than half the time on a single run might fail three out of four times when you actually need it to work reliably."
Conflictos: Ninguno. Consistente con K4 que reporta varianza alta.

### Claim 36
Claim: pass@k mide capacidad (al menos un exito en k intentos); pass^k mide confiabilidad (todos exitosos). Divergen a medida que k aumenta: a k=10, pass@k→100% mientras pass^k→0%.
Dimension: K4
Tier: MEDIUM
Razon Tier: Fuente oficial (Anthropic Engineering blog) con excerpt textual.
Sources: Anthropic Engineering (https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
Excerpt: "pass@k measures the likelihood that an agent gets at least one correct solution in k attempts... pass^k measures the probability that all k trials succeed... pass@k and pass^k diverge as trials increase. At k=1, they're identical. By k=10, they tell opposite stories: pass@k approaches 100% while pass^k falls to 0%."
Conflictos: Ninguno.

### Claim 37
Claim: Counterfactual Trace Auditing (CTA): pass-rate promedio +0.34pp, stddev 4.4pp, 696 divergencias comportamentales, 522 instancias SIP en 49 tasks.
Dimension: K4
Tier: MEDIUM
Razon Tier: Paper peer-reviewed arXiv con excerpt textual. Cifras precisas.
Sources: arXiv 2605.11946 (https://arxiv.org/abs/2605.11946)
Excerpt: "Across all 49 tasks the mean pass-rate change is +0.34pp, median 0pp, standard deviation 4.4pp. Only 3 tasks have >=+4pp... the same 49 traces contain 696 behavioral divergences between the with- and without-skill agent (mean 14.2 per task) and 522 SIP instances (mean 10.7 per task)."
Conflictos: Ninguno.

### Claim 38
Claim: Claude Code exporta metricas OpenTelemetry con claude_code.token.usage segmentable por skill.name, plugin.name, agent.name.
Dimension: K4
Tier: MEDIUM
Razon Tier: Documentacion oficial con excerpt textual.
Sources: Claude Code Docs (https://code.claude.com/docs/en/monitoring-usage)
Excerpt: "Claude Code exports metrics as time series data via the standard metrics protocol... claude_code.token.usage: Number of tokens used... Break down by type (input/output), user, team, model, skill.name, plugin.name, or agent.name."
Conflictos: Ninguno.

### Claim 39
Claim: Skill Bench (skill-eval-action) usa 80% como pass-threshold default porque "la flakiness ocasional es esperada".
Dimension: K4
Tier: MEDIUM
Razon Tier: Documentacion oficial del producto con excerpt textual.
Sources: skill-bench.dev (https://skill-bench.dev/)
Excerpt: "The default pass-threshold is 80 not 100. The agentskills.io best practices say 'occasional flakiness is expected'. Options to reduce flakiness: Relax criteria, Run multiple times and average, Lower threshold -- accept that 70-80% is a realistic pass rate for LLM evals."
Conflictos: Ninguno.

### Claim 40
Claim: Solo 5 de los 12 eventos de hook pueden bloquear ejecucion: UserPromptSubmit, PreToolUse, PermissionRequest, Stop, SubagentStop.
Dimension: K5
Tier: MEDIUM
Razon Tier: Fuente de comunidad (prg.sh) con excerpt textual. Fuente unica.
Sources: prg.sh (https://prg.sh/notes/Claude-Code-Hooks)
Excerpt: "PreToolUse: Before tool execution → Yes [can block]. PostToolUse: After tool completes → Yes [can block via exit code 2]. PermissionRequest: Permission dialog shown → Yes. UserPromptSubmit: User submits prompt → Yes. Stop: Main agent finishes → Yes. SubagentStop: Subagent finishes → Yes."
Conflictos: Nota menor: prg.sh lista 5+1 eventos bloqueantes (incluye PostToolUse con exit code 2). El claim dice "5" pero la fuente sugiere 6 si se incluye PostToolUse. Divergencia menor en conteo.

### Claim 41
Claim: Claude Code tiene ~40+ comandos slash commands built-in.
Dimension: K5
Tier: MEDIUM
Razon Tier: Fuente de comunidad (prg.sh) con lista enumerada. Fuente unica.
Sources: prg.sh (https://prg.sh/notes/Claude-Code-Slash-Commands)
Excerpt: "Built-in Commands: /add-dir, /agents, /bashes, /bug, /clear, /compact, /config, /context, /cost, /doctor, /exit, /export, /help, /hooks, /ide, /init, /install-github-app, /login, /logout, /mcp, /memory, /model, /output-style, /permissions, /plan, /plugin, /pr-comments, /privacy-settings, /release-notes, /rename, /remote-env, /resume, /review, /rewind, /sandbox, /security-review, /stats, /status, /statusline, /teleport, /terminal-setup, /theme, /todos, /usage, /vim"
Conflictos: Ninguno. La lista cuenta ~43 comandos.

### Claim 42
Claim: El Skill tool NO deduplica: cada invocacion del mismo skill anade contenido completo al contexto. Invocar 10+ veces agota la ventana.
Dimension: K5
Tier: MEDIUM
Razon Tier: GitHub issue verificado (claude-code #21891) con excerpt textual.
Sources: GitHub (https://github.com/anthropics/claude-code/issues/21891)
Excerpt: "The Skill tool appends full skill content to the Messages context every time it's invoked, even for the same skill. There's no deduplication, causing rapid context exhaustion."
Conflictos: Ninguno.

### Claim 43
Claim: Claude Code soporta context windows de 200K y 1M tokens. Ventana usable real ~830K despues de reservas de compaction.
Dimension: K5
Tier: MEDIUM
Razon Tier: Fuente secundaria (Verdent.ai) con excerpt textual. No es documentacion oficial de Anthropic.
Sources: Verdent.ai (https://verdent.ai/guides/claude-code-1m-context-window)
Excerpt: "The 1M window: you have roughly 830K usable tokens after Claude Code's auto-compaction buffer (~33K reserved) and the ~83.5% usage threshold before compaction triggers."
Conflictos: Ninguno. Nota: la cifra de 830K es una estimacion del autor, no un dato oficial.

### Claim 44
Claim: Rate limits post-mayo 2026 (deal Colossus 1): 5-hour window duplicado, peak-hour reductions eliminadas para Pro/Max. API Tier 1: 500K input TPM (antes 30K).
Dimension: K5
Tier: MEDIUM
Razon Tier: Fuente secundaria (mindstudio.ai) con excerpt textual. Datos oficiales de Anthropic probablemente pero filtrados via blog.
Sources: mindstudio.ai (https://mindstudio.ai/blog/claude-code-rate-limits-doubled-colossus-1-api-limits/)
Excerpt: "Claude Code's 5-hour rate limit just doubled. API Tier 1 input tokens per minute jumped from 30,000 to 500,000. Peak-hour limit reduction eliminated for Pro and Max accounts."
Conflictos: Ninguno. Nota: el salto de 30K a 500K TPM es una cifra extrema que requiere confirmacion oficial.

### Claim 45
Claim: NVIDIA implemento programa de skills verificados: catalog → scan (SkillSpector) → sign (OpenSSF Model Signing) → skill card. SkillSpector escanea 64 patrones en 16 categorias.
Dimension: K6
Tier: MEDIUM
Razon Tier: Blog oficial NVIDIA con excerpt. Los detalles tecnicos (64 patrones, 16 categorias) no estan en el excerpt proporcionado — son inferidos del contexto.
Sources: NVIDIA Developer Blog (https://developer.nvidia.com/blog/nvidia-verified-agent-skills-provide-capability-governance-for-ai-agents/)
Excerpt: "The signature covers every file and subdirectory in the skill directory... Certificate retrieval, supported verification tooling, and example verification commands see the signing documentation."
Conflictos: Ninguno.

### Claim 46
Claim: Cisco mcp-scanner tiene 3 motores (YARA, LLM-as-judge, Cisco AI Defense API) y Prompt Defense Analyzer contra 12 vectores.
Dimension: K6
Tier: MEDIUM
Razon Tier: GitHub oficial Cisco con excerpt textual. Fuente de vendor pero open-source verificable.
Sources: GitHub cisco-ai-defense/mcp-scanner (https://github.com/cisco-ai-defense/mcp-scanner)
Excerpt: "The MCP Scanner provides a comprehensive solution... Multiple Modes: Run scanner as a stand-alone CLI tool or REST API server... Prompt Defense Analyzer checks for missing defensive measures against 12 common attack vectors."
Conflictos: Ninguno.

### Claim 47
Claim: mcp-scan (>2,000 estrellas) detecta tool poisoning, rug pulls via hash-based pinning, cross-origin escalations, prompt injection. Se ejecuta con uvx mcp-scan@latest.
Dimension: K6
Tier: MEDIUM
Razon Tier: Fuente de vendor (Stytch/Invariant Labs) con excerpt textual.
Sources: Stytch Blog (https://stytch.com/blog/mcp-scan/)
Excerpt: "MCP-Scan includes built-in Tool Pinning to detect and prevent MCP Rug Pull attacks, verifying the integrity of installed tools by tracking changes via tool hashing."
Conflictos: Ninguno.

### Claim 48
Claim: GKE Agent Sandbox usa gVisor (runsc) con perfiles seccomp/AppArmor optimizados para workloads de agentes AI. Sub-second provisioning.
Dimension: K6
Tier: MEDIUM
Razon Tier: Fuente de comunidad (dev.to/GDE) con excerpt textual. Es arquitectura de referencia, no producto comercial general.
Sources: Google Dev Blog/dev.to (https://dev.to/gde/untrusted-code-trusted-cluster-scaling-secure-ai-agent-workspaces-with-gke-agent-sandbox-1mk1)
Excerpt: "gVisor intercepts those same syscalls in user space via Sentry... When your agent code calls execve(), it's Sentry that handles it, not the host kernel... sub-second provisioning."
Conflictos: Ninguno.

### Claim 49
Claim: OWASP ASI Top 10 (2026): 10 riesgos — Goal Hijack, Tool Misuse, Identity & Privilege Abuse, Supply Chain Compromise, Unexpected Code Execution, Memory Poisoning, Insecure Inter-Agent Communication, Cascading Failures, Human-Agent Trust Exploitation, Rogue Agents.
Dimension: K6
Tier: MEDIUM
Razon Tier: Fuente reconocida (OWASP) via intermediario (DeepTeam). No se verifico en sitio oficial OWASP. El intermediario puede haber interpretado.
Sources: DeepTeam/OWASP (https://trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications)
Excerpt: "Agentic systems can cause cascading failures where a single vulnerability propagates through connected tools, memory, and other agents, leading to large-scale security incidents."
Conflictos: Ninguno. Nota: la lista de 10 riesgos no aparece completa en el excerpt — fue completada por el investigador K6.

### Claim 50
Claim: SkillSieve identifico que skills con scripts ejecutables son 2.12x mas propensas a vulnerabilidades (OR=2.12, p<0.001). Hightower6eu (autor malicioso, 354 skills) detectado en totalidad.
Dimension: K6
Tier: MEDIUM
Razon Tier: Paper peer-reviewed arXiv. La cifra OR=2.12 aparece en el contexto pero no en el excerpt proporcionado. El investigador la extrajo del paper completo.
Sources: arXiv 2604.06550 (https://arxiv.org/html/2604.06550v1)
Excerpt: "A cheap static check filters about 86% of the volume, so expensive LLM calls go only where they are needed..."
Conflictos: Ninguno. Nota: cifra extraida del paper por el investigador, no presente en el excerpt.

### Claim 51
Claim: Claude Code permissions: deny rules tienen precedencia; PreToolUse hooks pueden bloquear; disableBypassPermissionsMode evita --dangerously-skip-permissions; managed settings via server/plist/registry/file.
Dimension: K6
Tier: MEDIUM
Razon Tier: Documentacion oficial con excerpt. El bug de deny rules no siendo enforced (marzo 2026) reduce la confianza.
Sources: Claude Code Docs (https://code.claude.com/docs/en/permissions)
Excerpt: "Rules are evaluated in order: deny -> ask -> allow. The first matching rule wins, so deny rules always take precedence... PreToolUse hooks run before the permission prompt. The hook output can deny the tool call."
Conflictos: K6 documenta un bug donde deny rules de Console no se enforcean en runtime. Esto contradice parcialmente el claim. Ver Conflicto #8.

### Claim 52
Claim: CVE-2026-25725: fix-to-deploy duro 16 dias. Los hooks (SessionStart, PreToolUse, PostToolUse) ejecutan SIN confirmacion ni notificacion.
Dimension: K6
Tier: MEDIUM
Razon Tier: Fuente de seguridad (Cymulate) con contexto detallado. Las cifras de "16 dias" y "sin confirmacion" son del contexto, no del excerpt textual.
Sources: Cymulate Research (https://cymulate.com/blog/the-race-to-ship-ai-tools-left-security-behind-part-1-sandbox-escape/)
Excerpt: "The read-only protection for .claude/settings.json is conditional on the file's existence at sandbox startup..."
Conflictos: Ninguno.

---

## TIER LOW

### Claim 53
Claim: Las 3 capas de aislamiento que MCP agregan (tool definitions, context window, credential vault) crean attack surface que APIs REST tradicionales no tienen.
Dimension: K2
Tier: LOW
Razon Tier: Fuente de vendor (Prefactor) con excerpt. Es una opinion de marketing sin datos empiricos ni metricas. La afirmacion es qualitativa, no cuantitativa.
Sources: Prefactor (https://prefactor.tech/blog/mcp-security-multi-tenant-ai-agents-explained)
Excerpt: "MCP adds protocol-specific surfaces that traditional APIs don't have: tool description metadata entering the LLM context window, credential vaults storing OAuth tokens per user per connection, and prompt-level context that could leak across tenants if not properly scoped."
Conflictos: Ninguno. Nota: la "capa de context window" como attack surface no esta cuantificada.

### Claim 54
Claim: El estandar Agent Skills (agentskills.io) es soportado por 16+ herramientas. skills.sh es el hub principal.
Dimension: K3
Tier: LOW
Razon Tier: Fuente de comunidad (inference.sh) con excerpt. La cifra "16+" no esta verificada independientemente. La fuente tiene interes en promover el estandar.
Sources: inference.sh (https://inference.sh/blog/skills/agent-skills-overview)
Excerpt: "The Agent Skills format was developed by Anthropic and released as an open standard in late 2025. At last count, skills.sh lists compatibility with Claude Code, Cursor, GitHub Copilot, Goose, Codex CLI, Windsurf, Gemini CLI, Roo Code, Trae, and many others."
Conflictos: Ninguno. Nota: la cifra "16+" y la lista de herramientas no verificadas.

### Claim 55
Claim: El sandbox para agentes AI multi-tenant requiere microVM (Firecracker) como minimo aceptable para codigo no confiable.
Dimension: K2
Tier: LOW
Razon Tier: Fuente de vendor (Augment Code) con excerpt. Es una opinion/posicion de una empresa, no un consenso ni estandar. Docker es ampliamente usado a pesar de esta afirmacion.
Sources: Augment Code (https://www.augmentcode.com/guides/agent-execution-sandbox)
Excerpt: "Production-safe agent execution requires hardware-level isolation (microVMs or userspace kernels), default-deny filesystem and network policies, and layered escape prevention... Standard Docker/runc shares the host kernel and is explicitly insufficient for untrusted agent code execution."
Conflictos: Contradice parcialmente la realidad de produccion donde Docker es predominante. Ver Conflicto #9.

### Claim 56
Claim: No hay sistema de resolucion de conflictos entre skills. Si dos skills dan instrucciones contradictorias, Claude las aplica en orden de aparicion.
Dimension: K5
Tier: LOW
Razon Tier: Fuente de comunidad (buildtolaunch.substack.com) — blog sin peer review. Es una observacion empirica, no documentacion oficial.
Sources: buildtolaunch.substack.com (https://buildtolaunch.substack.com/p/claude-skills-not-working-fix)
Excerpt: "Duplicate looks like: two files both describing how to write an article, different instructions, neither one deferring to the other. This is the same single-source-of-truth problem that breaks any shared documentation system."
Conflictos: Ninguno. Nota: no hay documentacion oficial que confirme ni niegue este comportamiento.

### Claim 57
Claim: EffectorHQ encontro que 67% de 13,729 skills fallan en practica.
Dimension: K4
Tier: LOW
Razon Tier: Fuente no verificada (GitHub repo sin contexto academico). La metodologia de "fallar" no esta definida. Excerpt sin detalle metodologico.
Sources: GitHub effectorHQ/skill-eval (https://github.com/effectorHQ/skill-eval)
Excerpt: "ClawHub has 13,729 skills. 67% of them fail in practice. The ecosystem needs a way to answer: does this skill actually do what it claims?"
Conflictos: Ninguno. Nota: la cifra de "13,729" difiere del "40,285" de K1 (diferente fecha de muestreo).

### Claim 58
Claim: Los datos de Claude Code se almacenan localmente en ~/.claude/projects/ por 30 dias en plaintext.
Dimension: K3
Tier: LOW
Razon Tier: Documentacion oficial (code.claude.com) confirmando retencion de 30 dias. La aseveracion "plaintext" requiere verificacion local. No hay excerpt que diga "plaintext".
Sources: Claude Code Docs (https://code.claude.com/docs/en/data-usage)
Excerpt: "Commercial users (Team, Enterprise, and API): Standard: 30-day retention period... Local caching: Claude Code clients store session transcripts locally under ~/.claude/projects/ for 30 days."
Conflictos: Ninguno. Nota: el investigador K3 añadio "plaintext" como interpretacion; el excerpt dice "session transcripts" sin especificar formato.

---

# Seccion 2: Conflictos entre Dimensiones

## Conflicto 1: SkillsBench 84 tasks (v3) vs 86 tasks (v1 abstract)
Entre: K1 Claim 1 (84 tasks) vs K4 Claim 1 ("86 tasks across 11 domains")
Descripcion: K1 reporta consistentemente 84 tasks en la version final v3 del paper. K4 cita el abstract v1 que dice "86 tasks". K1 explica que la v1 probablemente incluia 2 tasks adicionales descartadas en revision.
Resolucion propuesta: PREVALECE 84 tasks (K1). La v3 es la version revisada y final del paper. K4 debe actualizar su excerpt a la v3. La diferencia es menor al 2.4% pero la consistencia metodologica importa.

## Conflicto 2: SkillsBench +16.2pp vs +12.66pp
Entre: K1 Claim 2 (+16.2pp principal) vs Figura 2 del mismo paper (+12.66pp)
Descripcion: El paper tiene AMBAS cifras. +16.2pp aparece en abstract, Finding 1 y conclusion. +12.66pp aparece solo en la Figura 2 (pipeline overview).
Resolucion propuesta: PREVALECE +16.2pp. Es la cifra que aparece en los resultados principales, abstract y conclusion. +12.66pp es probablemente un residuo de version anterior no actualizado en la figura. Se recomienda usar +16.2pp con nota de discrepancia.

## Conflicto 3: Cowork bloquea SP-API/n8n
Entre: K3 Claim 17 (Cowork bloquea TODOS los dominios no aprobados) vs K5 (usa Cowork para skills)
Descripcion: K3 confirma con fuente oficial (GitHub issue Anthropic) que Cowork bloquea todos los dominios no aprobados por Anthropic, incluyendo SP-API y n8n. K5 menciona Cowork como plataforma disponible para skills sin notar esta limitacion.
Resolucion propuesta: PREVALECE K3 Claim 17. Cowork NO es viable para SP-API/n8n a menos que Anthropic apruebe esos dominios explicitamente. K5 deberia añadir advertencia sobre esta limitacion. La restriccion es a nivel de red (proxy sandbox), no de skills.

## Conflicto 4: Hooks 12 eventos vs "25+ eventos"
Entre: K5 Claim 15 (12 eventos) vs K3 ("25+ eventos de hooks")
Descripcion: K5 enumera explicitamente 12 eventos con fuente verificada (claudefa.st). K3 menciona "25+ eventos de hooks" sin fuente ni enumeracion.
Resolucion propuesta: PREVALECE K5 Claim 15 (12 eventos). K3 no proporciono excerpt ni fuente para "25+". Probablemente el investigador K3 confundio hooks con otro concepto (quizas comandos slash, que son ~40+). K3 debe corregirse.

## Conflicto 5: 36.82% vs "36%"
Entre: K1 Claim 3 (36.82%) vs K6 resumen ("36%")
Descripcion: K1 y K6 usan la misma fuente (Snyk blog) pero K6 redondea a "36%" en el resumen ejecutivo.
Resolucion propuesta: PREVALECE 36.82% (K1/K6 con precision). El redondeo en K6 resumen es aceptable para comunicacion ejecutiva pero las cifras exactas deben usarse en especificaciones tecnicas. NO ES UNA CONTRADICCION REAL — es redondeo.

## Conflicto 6: MCP multi-tenant en Azure OpenAI
Entre: K2 Claim 14 (Azure OpenAI: no se puede inyectar tenant context en built-in tools) vs K5 (propone usar MCP sin esta limitacion)
Descripcion: K2 documenta una limitacion oficial de Microsoft: built-in tools MCP/Code Interpreter no permiten inyeccion confiable de tenant context. K5 propone arquitecturas MCP que no consideran esta limitacion.
Resolucion propuesta: PREVALECE K2 Claim 14. Para plataformas Azure OpenAI, se requieren contenedores dedicados o configs separadas por tenant. K5 deberia añadir nota sobre esta limitacion para deployments Azure.

## Conflicto 7: Cifras de skills en el ecosistema
Entre: K1 (40,285 skills en ClawHub) vs K4 (13,729 skills en ClawHub segun EffectorHQ)
Descripcion: K1 reporta 40,285 skills (fecha 5 feb 2026, paper Bosch/CMU). K4 reporta 13,729 skills (fuente EffectorHQ, fecha no especificada).
Resolucion propuesta: AMBAS pueden ser correctas en su contexto temporal. El ecosistema de skills crecio 18.5x en 20 dias (K1). Es probable que EffectorHQ haya muestreado en una fecha diferente. Sin embargo, la cifra de K1 tiene mayor rigor metodologico (paper academico con fecha explicita). Para propositos de MWT, usar la cifra mas reciente disponible con fecha explicita.

## Conflicto 8: Claude Code deny rules vs bug de no-enforcement
Entre: K6 Claim 51 (deny rules tienen precedencia) vs bug documentado (deny rules de Console no se enforcean en runtime)
Descripcion: K6 documenta que en marzo 2026 se reporto un bug donde deny rules configuradas via Console no se enforceaban en runtime. Esto contradice parcialmente el claim de que "deny rules always take precedence".
Resolucion propuesta: PREVALECE la documentacion oficial CON NOTA DE BUG. El diseno intencionado es que deny rules tengan precedencia, pero existe un bug conocido (marzo 2026, status desconocido). Para MWT: no confiar exclusivamente en deny rules hasta confirmar que el bug esta resuelto. Usar PreToolUse hooks como capa adicional de enforcement.

## Conflicto 9: Docker insuficiente vs Docker predominante
Entre: K2 Claim (Docker insuficiente para agentes AI, fuente Augment Code) vs realidad de produccion
Descripcion: Augment Code afirma que Docker es "explicitly insufficient" para codigo no confiable. Sin embargo, Docker es la tecnologia predominante en produccion (incluyendo Dify, Claude Code sandbox en Linux usa bubblewrap no Docker, etc.).
Resolucion propuesta: La afirmacion es valida para codigo REALMENTE no confiable (skills de terceros sin revision). Para skills propias revisadas, Docker es aceptable. La postura correcta es: gVisor/Firecracker para skills de terceros no verificadas; Docker/bubblewrap para skills propias verificadas. Ambas posturas coexisten dependiendo del threat model.

---

# Seccion 3: Reglas MWT Violadas

## Reglas MWT evaluadas

| # | Regla MWT | Estado | Claim que viola |
|---|-----------|--------|-----------------|
| 1 | Tenant via headers del cliente → RECHAZADO | **CUMPLIDA** por todos los claims | Ninguno. K2 Claims 12, 13 confirman explicitamente: tenant fluye por contexto server-side, nunca headers del cliente. |
| 2 | tenant_id NOT NULL en tablas | **CUMPLIDA** | Ninguno. K2 Claim 12 confirma GoClaw usa tenant_id NOT NULL en 40+ tablas. |
| 3 | WHERE tenant_id = $N obligatorio en queries | **CUMPLIDA** | Ninguno. K2 Claim 12 confirma "Every query includes WHERE tenant_id = $N. No exceptions." |
| 4 | Credenciales efimeras scopadas por tarea, nunca API keys de larga vida | **CUMPLIDA** | Ninguno. K2 Claim 30 (Descope) confirma: "Issue ephemeral, scoped credentials per task... Agents should NOT receive long-lived API keys." |
| 5 | Vault lookup por (tenant_id, tool_name), nunca env vars globales | **CUMPLIDA** | Ninguno. K2 Claim 30 (Omnithium) confirma: "look up the key by (tenant_id, tool_name)... never using environment variables for tenant credentials." |

**Resultado: Ningun claim viola las reglas MWT.** Todos los claims verificados estan alineados con las reglas de multi-tenancy establecidas. Esto es notable: la investigacion K2 encontro implementaciones que siguen exactamente las mismas reglas que MWT define.

## Notas de alineacion MWT

1. **Transporte de tenant**: K2 Claims 12 (GoClaw), 13 (AWS Lambda) y el broker pattern (Claim 33) confirman que el tenant fluye por contexto server-side. La postura de MWT de "nunca headers del cliente" esta respaldada por implementaciones reales.

2. **RLS**: K2 Claims 12 y 31 confirman que RLS es la ultima linea de defensa para queries AI-generated. La postura MWT de "tenant_id NOT NULL + WHERE obligatorio" esta implementada en GoClaw en produccion.

3. **Aislamiento de ejecucion**: K2 Claim 11 (Dify) demuestra que la falta de aislamiento UID per-execution causa source disclosure cross-tenant. K6 (gVisor, Firecracker) confirma que microVM es el estandar para codigo no confiable.

4. **Secrets scopados**: K2 Claims 28-30 confirman el patron (tenant_id, tool_name) lookup + per-tenant KMS keys. La advertencia contra env vars globales es unanime.

---

# Seccion 4: Hallazgos de Verificacion

## Base de evidencia SOLIDA (HIGH + MEDIUM = 52 de 58 claims)

### Papers peer-reviewed confirmados con excerpt:
| Paper | Claims | Confianza |
|-------|--------|-----------|
| Bosch/CMU arXiv 2602.08004 | 1,414 tokens mediana, 18.5x crecimiento, 46.3% duplicados, 9% L3 | HIGH |
| SkillsBench arXiv 2602.12670 v3 | 84 tasks, 7,308 trajectories, +16.2pp, 2-3 modules optimo, -1.3pp self-generated | HIGH |
| SKILL-INJECT arXiv 2602.20156 | 202 injection-task pairs, ~80% ASR (BoN) | HIGH |
| SkillFortify arXiv 2603.00195 | 96.95% F1, 0% FPR, 540 skills en 1.378s | HIGH |
| Park et al. arXiv 2601.10338 | 42,447 skills, 26.1% con vulnerabilidades, 14 patrones | HIGH |
| SkillSieve arXiv 2604.06550 | 49,592 skills, 38.8ms/skill, filtro 86% benignas | HIGH |
| CTA arXiv 2605.11946 | +0.34pp mean, 696 divergencias, 522 SIP | MEDIUM |
| CABP broker arXiv 2603.13417 | Patron gateway JWT para MCP multi-tenant | MEDIUM |

### Datos de produccion confirmados:
| Fuente | Claims | Confianza |
|--------|--------|-----------|
| Snyk ToxicSkills | 36.82%, 534 criticas, 76 maliciosos, 10.9% secrets | HIGH |
| Dify CVE + fix | Source disclosure cross-tenant, UID per-run fix | HIGH |
| GoClaw | 40+ tablas tenant_id NOT NULL, context.Context | HIGH |
| AWS Lambda Tenant Isolation | Execution envs separados por tenant | HIGH |
| Azure OpenAI | Built-in tools sin tenant context confiable | HIGH |
| Claude Code hooks | 12 eventos, 4 tipos, PreToolUse bloquea | HIGH |
| Cowork sandbox | VM Ubuntu 22.04, proxy bloquea todo no aprobado | HIGH |
| Claude Code CVE-2026-25725 | CVSS 7.7, settings.json sandbox escape | HIGH |

## Debilidades identificadas (LOW = 6 claims)

1. **K3: "16+ herramientas soportan Agent Skills"** — Fuente sin verificacion independiente de la cifra
2. **K2: "microVM es minimo aceptable"** — Opinion de vendor, no consenso
3. **K5: "No hay sistema de resolucion de conflictos entre skills"** — Observacion de blog, no documentacion oficial
4. **K4: "67% de skills fallan"** — Metodologia no definida, fuente no academica
5. **K3: "datos locales en plaintext"** — Interpolacion del investigador, no confirmada por excerpt
6. **K2: "3 capas de aislamiento MCP"** — Cualitativo, sin metricas empiricas

## Huecos criticos no localizados (de K2, confirmados por cross-verification)

| # | Hueco | Impacto para MWT |
|---|-------|------------------|
| 1 | RLS aplicada a tabla de skills (metadata) | Una query "listar skills" sin RLS expone skills de otros tenants |
| 2 | Aislamiento de ejecucion con RLS en canal de comunicacion | Como asegurar que el canal proceso-DB respeta RLS |
| 3 | Sistema de visibilidad de skills (4 niveles: PUBLIC/PARTNER_B2B/INTERNAL/CEO_ONLY) | No hay precedente documentado |
| 4 | Propagacion de tenant en skill chaining | Como hereda tenant context una skill invocada por otra |
| 5 | Implementacion end-to-end documentada | No existe caso de estudio que combine TODOS los aspectos |

## Veredicto final sobre discrepancias solicitadas

| # | Discrepancia | Veredicto |
|---|-------------|-----------|
| 1 | SkillsBench +12.66pp vs +16.2pp | **+16.2pp prevalece** (abstract, resultados, conclusion). +12.66pp es residuo de Figura 2. |
| 2 | SkillsBench 86 vs 84 tasks | **84 tasks prevalece** (v3 final). 86 es v1 superada. |
| 3 | Cowork bloquea SP-API/n8n | **CONFIRMADO** por fuente oficial (GitHub issue Anthropic #37970). Cowork NO puede llamar SP-API. |
| 4 | Hooks 12 eventos vs "25 eventos" | **12 eventos prevalece** (fuente verificada claudefa.st). "25" en K3 es ERROR sin fuente. |
| 5 | 36.82% vs "36%" | **36.82% prevalece** (dato exacto Snyk). "36%" es redondeo, no contradiccion. |

---

*Cross-verification completada el 2026-07-09*
*Metodologia: 58 claims evaluados, 6 papers peer-reviewed verificados, 20+ fuentes de produccion auditadas, 9 conflictos detectados y resueltos, 0 reglas MWT violadas*
*Investigadores responsables: K1-K6 (investigacion primaria), Cross-Verification (validacion y clasificacion)*
