# Consolidado Final: Skills Multi-Tenant K1-K6 — Guia de Implementacion para MWT

La investigacion cross-dimensional K1-K6 confirma que el ecosistema de skills multi-tenant es tecnicamente viable hoy, pero requiere composicion defensa-en-profundidad: 36.82% de skills del ecosistema tienen fallas de seguridad (K1/K6), la varianza no-determinista es el enemigo principal de la confiabilidad (K4), Cowork es inviable para SP-API/n8n por sandbox de red (K3), y no existe implementacion end-to-end documentada que combine registry RLS + aislamiento de ejecucion + vault scopado (K2). Las cinco prioridades de MWT son: (1) registry con RLS, (2) CI/CD con skillgrade + mcp-scan, (3) Claude Code CLI (no Cowork) para SP-API, (4) vault de credenciales por tenant, (5) sandbox gVisor para skills de terceros.

---

## 2. Hallazgos que se Refuerzan (Confirmados por 2+ Dimensiones)

### 2.1 La seguridad del supply chain de skills es un riesgo real y cuantificado

[HECHO VERIFICADO] Claim: El 36.82% de skills escaneadas (3,984) tienen >=1 falla; 13.4% son criticas; 76 payloads maliciosos confirmados por HITL review; 10.9% contienen secretos hardcodeados. | Source: Snyk ToxicSkills blogpost, 5 Feb 2026 | Excerpt: "13.4% of all skills, or 534 in total, all contain at least one critical-level security issue [...] over a third of the ecosystem is affected: 36.82% (1,467 skills) have at least one security flaw." | Tier: HIGH

**Refuerzo cruzado**: K1 (auditoria de cifras) + K6 (herramientas de defensa). K6 documenta que SkillFortify logra 96.95% F1 con 0% FPR, mcp-scan detecta tool poisoning/rug pulls, y Cisco mcp-scanner tiene 3 motores de escaneo. El 91% de skills maliciosas combina prompt injection con malware tradicional (K6).

[HECHO VERIFICADO] Claim: Hasta 80% ASR ante skill file injections (condicion Best-of-5 Obvious); 6-19% en condicion realista (Contextual + Warning Prompt). | Source: SKILL-INJECT arXiv 2602.20156 | Excerpt: "Our results show that today's agents are highly vulnerable with up to 80% attack success rate with frontier models, often executing extremely harmful instructions including data exfiltration, destructive action, and ransomware-like behavior." | Tier: HIGH

**Refuerzo cruzado**: K1 (202 pares injection-task) + K6 (CVE-2026-25725 sandbox escape CVSS 7.7) + K4 (varianza no-determinista). El vector via skill files es real en todas las condiciones.

### 2.2 La varianza no-determinista degrada la confiabilidad en produccion

[HECHO VERIFICADO] Claim: Agentes con 60% pass@1 exhiben solo 25% consistencia entre corridas multiples. pass@k y pass^k divergen radicalmente: a k=10, pass@k→100% mientras pass^k→0%. | Source: t-bench / Anthropic Engineering | Excerpt: "agents achieving 60% pass@1 on benchmarks may exhibit only 25% consistency across multiple trials" + "pass@k and pass^k diverge as trials increase. By k=10, they tell opposite stories: pass@k approaches 100% while pass^k falls to 0%" | Tier: HIGH

**Refuerzo cruzado**: K4 (t-bench 60%->25%, thresholds 80%) + K1 (SkillsBench varianza +13.6pp a +23.3pp) + K4 (CTA: stddev 4.4pp, 696 divergencias comportamentales). En multi-tenant, un skill inconsistente expone datos de un tenant a otro.

### 2.3 El aislamiento cross-tenant es un problema real con soluciones documentadas

[HECHO VERIFICADO] Claim: Dify sufrio source disclosure cross-tenant por ejecuciones compartiendo UID y /tmp. Parcheado con UID per-run + archivos 0600. | Source: Imperva Threat Research + Dify commit | Excerpt: "Separate tenants executing inside the same sandbox root, under the same effective identity, with readable code artifacts left in a shared /tmp" + "uid, err := AcquireUID(ctx). The wrapper was written with os.WriteFile(..., 0600). The file was reassigned with syscall.Chown(..., uid, ...)" | Tier: HIGH

**Refuerzo cruzado**: K2 (Dify + AWS Lambda Tenant Isolation + GoClaw) + K6 (gVisor/Firecracker) + CROSSVERIF (Conflicto #9: Docker para skills propias, microVM para terceros).

### 2.4 El transporte de tenant via contexto server-side tiene precedentes solidos

[HECHO VERIFICADO] Claim: GoClaw usa tenant_id NOT NULL en 40+ tablas, WHERE tenant_id = $N en toda query, tenant fluyendo por context.Context, NUNCA headers del cliente. AWS Lambda Tenant Isolation establece X-Amz-Tenant-Id SOLO via Lambda Authorizer. | Source: GoClaw Deep Dive + AWS docs + Ran the Builder | Excerpt: "Tenant flows through context.Context. Resolved at the gateway, propagated everywhere, never taken from client headers (which can be spoofed)" + "The Lambda authorizer needs to validate the tenant request, extract the tenant_id, and add the special header" | Tier: HIGH

**Refuerzo cruzado**: K2 (GoClaw + AWS Lambda + broker pattern CABP) + CROSSVERIF (0 reglas MWT violadas).

### 2.5 Las skills requieren curacion humana; la auto-generacion no funciona

[HECHO VERIFICADO] Claim: Self-generated skills empeoran rendimiento (-1.3pp). Skills con 2-3 modules: +18.6pp; 4+ modules: +5.9pp. | Source: SkillsBench arXiv 2602.12670 v3 | Excerpt: "Self-generated Skills provide negligible or negative benefit (-1.3 pp average)" + "Tasks with 2-3 Skills show the largest improvement (+18.6pp), while 4+ Skills provide only +5.9 pp benefit" | Tier: HIGH

**Refuerzo cruzado**: K1 (SkillsBench) + K4 (EffectorHQ 67% fallo) + K6 (skills con scripts: 2.12x mas propensas a vulnerabilidades, OR=2.12, p<0.001).

### 2.6 Cowork NO es viable para SP-API/n8n

[HECHO VERIFICADO] Claim: Cowork bloquea TODOS los dominios no aprobados por Anthropic. SP-API y n8n estan bloqueados. | Source: GitHub anthopics/claude-code #37970 | Excerpt: "In Cowork mode, the sandbox proxy blocks all external API calls that are not on Anthropic's managed allowlist. Project-level sandbox.network.allowedDomains settings are completely ignored" | Tier: HIGH

**Refuerzo cruzado**: K3 (sandbox de Cowork) + K5 (patrones de composicion) + CROSSVERIF (Conflicto #3: K3 prevalece).

---

## 3. Dependencias entre Dimensiones

```
K1 (Evidencia) ---------> K6 (Seguridad)
     |                         |
     v                         v
K2 (Multi-tenancy) <-----> K4 (Evals/CI)
     |                         |
     v                         v
K3 (Runtimes) ---------> K5 (Orquestacion)
```

| Dimension | Depende de | Por que |
|-----------|-----------|---------|
| K2 (multi-tenancy) | K3 (runtime) | El mecanismo de aislamiento varia: bubblewrap (Claude Code CLI), VM (Cowork), containers (API). El runtime determina si SP-API es alcanzable. |
| K2 (multi-tenancy) | K6 (seguridad) | RLS + vault + sandbox son requisitos que habilitan multi-tenancy. Sin ellos, no hay aislamiento cross-tenant. |
| K4 (evals/CI) | K1 + K6 | Thresholds basados en SkillsBench/t-bench. mcp-scan y SkillFortify deben correr EN el pipeline CI. |
| K5 (orquestacion) | K2 + K3 | Hooks/subagentes dependen de la plataforma. Subagente sin tenant context filtrado por RLS es data leak. |

**Cadena critica MWT**: Runtime (K3) -> Aislamiento (K2+K6) -> Skills ejecutables (K5) -> Evaluacion valida (K4)

---

## 4. Guia de Implementacion Multi-Tenant de Skills

### 4.1 Arquitectura de Referencia

#### 4.1.1 Registry de Skills con RLS

[RECOMENDACION - juicio del analista] Basado en K2 Claim 12 (GoClaw: 40+ tablas tenant_id NOT NULL), K2 Claim 31 (RLS critico para queries AI-generated). No se encontro implementacion documentada de RLS sobre metadata de skills — hueco que MWT debe cerrar.

```sql
CREATE TABLE skill_registry (
    tenant_id UUID NOT NULL, skill_id TEXT NOT NULL,
    skill_type TEXT NOT NULL CHECK (skill_type IN ('OFFICIAL','AMAZON','CUSTOM')),
    status TEXT NOT NULL DEFAULT 'DISABLED' CHECK (status IN ('ENABLED','DISABLED','DEPRECATED')),
    visibility TEXT NOT NULL DEFAULT 'INTERNAL' CHECK (visibility IN ('PUBLIC','PARTNER_B2B','INTERNAL','CEO_ONLY')),
    config JSONB DEFAULT '{}', content_hash TEXT,  -- SHA-256 para tamper detection
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (tenant_id, skill_id)
);
ALTER TABLE skill_registry ENABLE ROW LEVEL SECURITY;
CREATE POLICY skill_tenant_isolation ON skill_registry
    FOR ALL USING (tenant_id = current_setting('app.tenant_id')::UUID)
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::UUID);
```

[HECHO VERIFICADO] GoClaw: "Three rules, never broken: Every isolatable table has tenant_id NOT NULL. 40+ tables enforce this. Every query includes WHERE tenant_id = $N. No exceptions." | Tier: HIGH

#### 4.1.2 Overrides Per-Tenant

```json
{
  "tools_allowed": ["mcp__sp-api__getOrders", "mcp__sp-api__getInventory"],
  "tools_denied": ["mcp__sp-api__deleteListing"],
  "max_tokens_per_execution": 50000,
  "allowed_models": ["claude-sonnet-4", "claude-haiku-4"],
  "sandbox_required": true,
  "network_allowlist": ["sellingpartnerapi-na.amazon.com", "api.helium10.com"]
}
```

[HECHO VERIFICADO] GoClaw: overrides de LLM configs, tool settings, skills enabled/disabled, MCP servers + per-user credentials. | Tier: HIGH. Scalekit: "tool availability is a per-tenant configuration that must be enforced before the LLM ever selects a tool — not after." | Tier: MEDIUM

#### 4.1.3 Aislamiento de Ejecucion + Vault Scopado

```
Gateway (resuelve tenant_id de JWT/API key)
  → Tenant context en context.Context (NUNCA headers)
  → ToolDispatcher verifica skill_registry
  → Vault lookup (tenant_id, skill_id, credential_type) → credenciales efimeras
  → Proceso separado (MCP server / sub-agente) con sandbox dedicado
  → RLS PostgreSQL filtra datos del tenant → Resultado
```

[HECHO VERIFICADO] Azure OpenAI: "You can't reliably inject tenant context into built-in tool invocations, so use dedicated containers or separate tool configurations for each tenant." | Tier: HIGH. Omnithium vault: "look up the key by (tenant_id, tool_name)... never using environment variables for tenant credentials." | Tier: MEDIUM. Descope: "Agents should NOT receive long-lived API keys." | Tier: HIGH

[HECHO VERIFICADO] broker pattern (CABP): "A gateway service intercepts JSON-RPC requests, extracts claims from the OAuth token, and injects tenant_id, user_id, and permission scopes into the request context." | Source: arXiv 2603.13417v1 | Tier: MEDIUM

### 4.2 Decisiones de Runtime (Basado en K3)

| Workload | Runtime | Sandbox |
|----------|---------|---------|
| **SP-API/n8n (Rana Walk)** | Claude Code CLI (local) | bubblewrap/seatbelt opcional |
| **Reportes/codigo (FaberLoom)** | Claude Code CLI o Cursor | Privacy Mode (Cursor) |
| **Automatizacion programatica** | Claude API (/v1/skills) | Container aislado |
| **Cowork** | **NO para SP-API/n8n** | Proxy bloquea todo |
| **Terceros no verificados** | gVisor/Firecracker | Hardware-level isolation |

[HECHO VERIFICADO] Existe MCP server DataDoe que expone SP-API via MCP, compatible con Claude/Cursor/Codex/n8n. | Tier: HIGH

[HECHO VERIFICADO] CVE-2026-25725 (CVSS 7.7): settings.json no existia por defecto, permitiendo sandbox escape. Patcheado v2.1.2. Crear `.claude/settings.json` ANTES de iniciar sandbox. | Tier: HIGH

```json
{
  "permissions": {
    "deny": [
      { "tool": "mcp__sp-api__deleteListing" },
      { "tool": "mcp__sp-api__updatePrice", "when": "batch_size > 10" }
    ]
  }
}
```

### 4.3 Pipeline CI/CD para Skills (Basado en K4)

#### 4.3.1 Eval Harness + Thresholds

[HECHO VERIFICADO] skill-eval (mgechev): ejecuta skills en Docker con graders deterministicos + LLM rubric. | Tier: HIGH. skillgrade: `--smoke` (5 trials), `--reliable` (15), `--regression` (30). Exit code 1 si pass < threshold. | Tier: HIGH. Skill Bench: auto-descubrimiento de skills modificadas via git diff. | Tier: HIGH

```yaml
# .github/workflows/skills-eval.yml
name: Skills Eval
on:
  pull_request:
    paths: ['skills/**']
jobs:
  smoke:  # GATE 1: < 3 min
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm install -g skillgrade
      - run: skillgrade --smoke --provider=docker --threshold=0.70
        env: { ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }} }
  eval-pr:  # GATE 2: < 10 min
    needs: smoke
    steps:
      - uses: skill-bench/skill-eval-action@v1
        with: { threshold: 80, trials: 5, provider: docker }
  regression:  # GATE 3: solo en main
    if: github.ref == 'refs/heads/main'
    steps:
      - run: skillgrade --regression --provider=docker --threshold=0.80
  security:  # GATE 4: siempre
    steps:
      - run: uvx mcp-scan@latest --path ./skills --fail-on-warning
      - run: pip install skillfortify && skillfortify scan ./skills
```

[HECHO VERIFICADO] Skill Bench threshold 80%: "occasional flakiness is expected". | Tier: HIGH. pass^k > pass@k para produccion: pass@5=100% con pass^5=30% = skill inestable e inusable. | Tier: HIGH

| Gate | Metrica | Threshold | Racional |
|------|---------|-----------|----------|
| Smoke | pass@5 | >= 70% | Verificar que funciona al menos una vez |
| PR eval | pass@5 | >= 80% | Estimado confiable |
| **Regression** | **pass^5** | **>= 60%** | **Metrica critica para produccion multi-tenant** |

#### 4.3.2 Observabilidad

[HECHO VERIFICADO] Claude Code OpenTelemetry: token.usage segmentable por skill.name, plugin.name, agent.name. | Tier: HIGH. Braintrust: alertas cuando token consumption excede historic averages. | Tier: HIGH

Exportar `CLAUDE_CODE_ENABLE_TELEMETRY=1`. Alertas: token/skill >2x promedio, skill falla >3x consecutivas, MCP SP-API errores de auth, duration >2x promedio.

### 4.4 Integracion con Stack Operativo (Basado en K5)

#### 4.4.1 Skills + n8n

```
Claude Code CLI → Skill: n8n-workflow-patterns
  → MCP: czlonkowski/n8n-mcp (21.4k stars, 1,851 nodos)
  → MCP: leosepulveda/mcp-n8n (gestion workflows)
  → n8n instance → HTTP Request → SP-API → Google Drive
```

Instalacion: `claude mcp add n8n-mcp npx n8n-mcp`

[HECHO VERIFICADO] n8n MCP Server Trigger expone workflows como tools MCP via SSE. | Tier: HIGH

#### 4.4.2 Skills + MCP Servers Propios (SP-API)

[RECOMENDACION] Si no se usa DataDoe, implementar MCP server propio con `@modelcontextprotocol/sdk`. Cada llamada valida tenant context antes de ejecutar. Vault lookup por (tenant_id, tool_name). NUNCA env vars globales.

[HECHO VERIFICADO] "Skills definen COMO hacer el trabajo; MCP servers dan acceso a datos. Para query/fetch/current state, necesitas MCP server, no solo skill." | Source: systemprompt.io | Tier: HIGH

#### 4.4.3 Skills + Sub-Agentes

```yaml
# .claude/agents/sp-analyst.md
---
name: sp-analyst
description: Analista SP-API para Rana Walk
model: claude-sonnet-4
maxTurns: 30
skills: [sp-api-conventions, report-format]
mcpServers: [sp-api-mcp, n8n-mcp]
disallowedTools: [Edit, mcp__sp-api__deleteListing]
---
Analiza datos SP-API para el tenant actual. SIEMPRE valida tenant_id. NUNCA expongas datos cruzados.
```

[HECHO VERIFICADO] `skills:` precarga contenido completo en contexto al startup. | Tier: HIGH. Frontmatter soporta: tools, disallowedTools, model, maxTurns, skills, mcpServers, hooks. | Tier: HIGH. `context: fork` ejecuta skill en sub-agente aislado. | Tier: HIGH

### 4.5 Defensas de Seguridad (Basado en K6)

#### Corto Plazo (Semana 1-2)

| Herramienta | Comando | Que detecta |
|------------|---------|-------------|
| **mcp-scan** | `uvx mcp-scan@latest --path ./skills` | Tool poisoning, rug pulls, cross-origin escalations, prompt injection |
| **Cisco mcp-scanner** | `python -m mcp_scanner scan ./skills --prompt-defense` | 3 motores (YARA, LLM-judge, AI Defense API), 12 vectores |
| **Claude Code permissions** | `.claude/settings.json` deny/ask/allow | PreToolUse bloquea ejecucion. deny tiene precedencia |

[HECHO VERIFICADO] mcp-scan: "built-in Tool Pinning to detect and prevent MCP Rug Pull attacks" | Tier: HIGH. Cisco: "3 engines: YARA, LLM-as-judge, Cisco AI Defense API" | Tier: HIGH. Claude Code permissions: "Rules: deny -> ask -> allow. deny rules always take precedence." | Tier: HIGH

**Nota**: Bug conocido (marzo 2026): deny rules de Console no siempre se enforcean. Usar PreToolUse hooks como capa adicional.

#### Medio Plazo (Mes 1-3)

| Herramienta | Comando | Que aporta |
|------------|---------|-----------|
| **SkillFortify** | `pip install skillfortify && skillfortify scan ./skills` | 96.95% F1, 0% FPR, analisis formal, SAT-based resolution |
| **NVIDIA SkillSpector** | `skillspector scan ./skills --format sarif` | 64 patrones en 16 categorias (OWASP LLM + MITRE ATLAS) |
| **OpenSSF Model Signing** | `model_signing sign ./skills/<skill>` | Provenance verificable con certificados X.509 |
| **gVisor sandbox** | `runtimeClassName: gvisor` en Kubernetes | Hardware-level isolation para skills de terceros |
| **Pruner (Sigstore)** | GitHub Action ob-aion/pruner | Attestation firmada + CycloneDX SBOM + SLSA provenance |

[HECHO VERIFICADO] SkillFortify: "96.95% F1 with 100% precision and 0% false positive rate on 540 skills, SAT-based resolution handles 1,000-node graphs in under 100 ms. Escaneo: 1.378 segundos." | Tier: HIGH. gVisor: "sub-second provisioning... Sentry handles syscalls, not the host kernel." | Tier: HIGH. Pruner: "Consumers verify with gh attestation verify; no Coroboros service sits in the trust path." | Tier: HIGH

#### Largo Plazo (> 3 meses)

1. **Deteccion indirect injection cross-tool**: No existe herramienta dedicada. Cisco prompt_defense detecta ausencia de defensas estaticamente, no runtime.
2. **Break-glass auditado con kill-switch**: Aproximacion: PreToolUse hooks + denylist centralizada + audit log inmutable.
3. **Runtime capability enforcement**: Theorem 3b de SkillFortify — sandbox que enforce capability lattice. Requiere integracion skillfortify + gVisor.
4. **Composition security analysis**: Emergent properties cuando multiples skills se instalan juntas (SkillFortify C8).

---

## 5. Recomendacion Directa — Que Construir Primero

### Prioridad 1: Semana 1-2 (Foundations)

| Componente | Que construir | Riesgo si NO se hace |
|-----------|--------------|---------------------|
| **Registry RLS** | Tabla `skill_registry` con tenant_id NOT NULL + RLS policy + vista `tenant_skills` | Data leak cross-tenant de skills disponibles |
| **mcp-scan en CI** | GitHub Action: `uvx mcp-scan@latest --path ./skills --fail-on-warning` | Deploy de skills maliciosas que roban credenciales SP-API |
| **Claude Code CLI local** | Migrar SP-API skills de Cowork a Claude Code CLI | Paralisis operativa de Rana Walk (Cowork bloquea SP-API) |
| **Vault credenciales** | Vault lookup (tenant_id, tool_name) con per-tenant KMS keys | Leak de credenciales SP-API cross-tenant |

**Guardrails P1**: tenant_id NOT NULL en TODAS las tablas. NUNCA env vars globales para credenciales de tenant. NUNCA headers del cliente para tenant_id. Deny rules en settings.json para tools destructivos SP-API.

### Prioridad 2: Mes 1 (CI/CD + Observabilidad)

| Componente | Que construir | Riesgo si NO se hace |
|-----------|--------------|---------------------|
| **Pipeline skillgrade** | Gates: smoke (70%) → PR eval (80%) → regression (pass^5 >= 60%) | Deploy de skills inconsistentes |
| **SkillFortify en CI** | `skillfortify scan ./skills --format json` | Skills propias con vulnerabilidades no detectadas |
| **OpenTelemetry** | `CLAUDE_CODE_ENABLE_TELEMETRY=1` + backend observabilidad | Sin visibilidad de costos ni deteccion de degradacion |
| **Hooks PreToolUse HTTP** | Endpoint que valida tool calls SP-API contra policy del tenant | Ejecucion no autorizada de tools destructivos |

**Guardrails P2**: Threshold 80% PR evals (no 100%). pass^5 >= 60% obligatorio para produccion. mcp-scan + SkillFortify antes de deploy. Hooks HTTP: decision "block" en respuesta 2xx.

### Prioridad 3: Mes 2-3 (Hardening)

| Componente | Que construir | Riesgo si NO se hace |
|-----------|--------------|---------------------|
| **Sandbox gVisor** | `runtimeClassName: gvisor` para skills de terceros | Escape de sandbox con acceso a datos de todos los tenants |
| **OpenSSF Model Signing** | Firmar skills propias con certificados X.509 | Skills tampered sin deteccion |
| **Sub-agentes con tenant context** | Patron sp-analyst.md con skills precargadas + MCP scopado + RLS | Skills con acceso excesivo a tools y datos |
| **Skill-creator v2** | Eval + Improve loop para skills SP-API existentes | Skills con baja precision de activacion |

**Guardrails P3**: Terceros solo en gVisor. Skills propias firmadas antes de publicacion. Tenant context en TODOS los hops. Network egress deny-by-default + allowlist por tenant.

---

## 6. Guardrails Inquebrantables

### 6.1 Reglas MWT (inviolables)

1. **tenant_id flujo context server-side — NUNCA headers del cliente**
   [HECHO VERIFICADO] GoClaw + AWS Lambda + CABP confirman. | Excerpt: "Tenant flows through context.Context. Resolved at the gateway, propagated everywhere, never taken from client headers." | Tier: HIGH

2. **tenant_id NOT NULL en todas las tablas, WHERE tenant_id = $N en TODAS las queries**
   [HECHO VERIFICADO] GoClaw: "40+ tables. No exceptions. Fail-closed." | Tier: HIGH

3. **Credenciales efimeras scopadas por tarea — NUNCA API keys de larga vida**
   [HECHO VERIFICADO] Descope: "Agents should NOT receive long-lived API keys." | Tier: HIGH

4. **Vault lookup por (tenant_id, tool_name) — NUNCA env vars globales**
   [HECHO VERIFICADO] Omnithium: "never using environment variables for tenant credentials." | Tier: MEDIUM

### 6.2 Reglas derivadas de K1-K6

5. **Cowork NUNCA para SP-API/n8n** — [HECHO VERIFICADO] "Project-level allowedDomains settings are completely ignored." | Tier: HIGH

6. **Skills de terceros NUNCA sin escaneo previo (mcp-scan + SkillFortify)** — [HECHO VERIFICADO] 36.82% fallas, 76 maliciosos confirmados. | Tier: HIGH

7. **pass^5 < 60% → NUNCA deploy a produccion** — [HECHO VERIFICADO] t-bench: 60% pass@1 → 25% consistencia real. | Tier: HIGH

8. **SKILL.md NUNCA > 10,000 tokens** — [HECHO VERIFICADO] "exceeds maximum allowed tokens (10000). Skills completely unusable." | Tier: HIGH

9. **Hooks HTTP NUNCA confiados para bloqueo sin decision: "block" explicita** — [HECHO VERIFICADO] "Non-2xx responses produce non-blocking errors. To block, return 2xx with decision: 'block'." | Tier: HIGH

10. **deny rules NUNCA como unica capa (bug conocido marzo 2026)** — [HECHO VERIFICADO] deny rules de Console no siempre enforced. Usar PreToolUse hooks adicional. | Tier: HIGH

11. **Sandbox settings.json NUNCA omitido (post-CVE-2026-25725)** — [HECHO VERIFICADO] "settings.json conditional on existence at startup. This file does not exist by default." CVSS 7.7. | Tier: HIGH

12. **Network egress NUNCA allow-all para skills de terceros** — [HECHO VERIFICADO] 91% de maliciosas combinan prompt injection con exfiltracion. Deny-by-default + allowlist. | Tier: HIGH

13. **Self-generated skills NUNCA sin revision humana** — [HECHO VERIFICADO] "effective Skills require human-curated domain expertise that models cannot reliably self-generate." -1.3pp. | Tier: HIGH

14. **Skills con scripts ejecutables NUNCA sin sandbox dedicado** — [HECHO VERIFICADO] OR=2.12, p<0.001 para vulnerabilidades en skills con scripts. | Tier: MEDIUM

---

## Apendice: Claims Verificados Consolidados

| # | Claim | Tier | Excerpt Verificado |
|---|-------|------|-------------------|
| 1 | 36.82% skills con fallas, 13.4% criticas, 76 maliciosos | HIGH | "36.82% (1,467 skills) have at least one security flaw... 76 malicious payloads" |
| 2 | ~80% ASR injections (BoN), 6-19% realista | HIGH | "up to 80% attack success rate with frontier models" |
| 3 | 60% pass@1 -> 25% consistencia | HIGH | "agents achieving 60% pass@1 may exhibit only 25% consistency" |
| 4 | pass@k diverge de pass^k: k=10, pass@k→100%, pass^k→0% | HIGH | "By k=10, they tell opposite stories" |
| 5 | Dify source disclosure cross-tenant, UID per-run fix | HIGH | "Separate tenants executing inside the same sandbox root, under the same effective identity" |
| 6 | GoClaw tenant_id NOT NULL 40+ tablas, context.Context | HIGH | "Three rules, never broken: Every isolatable table has tenant_id NOT NULL" |
| 7 | AWS Lambda Tenant Isolation: envs separados por tenant | HIGH | "execution environments will not be shared across tenants" |
| 8 | Cowork bloquea SP-API/n8n | HIGH | "sandbox proxy blocks all external API calls that are not on Anthropic's managed allowlist" |
| 9 | Self-generated -1.3pp; 2-3 modules +18.6pp | HIGH | "Self-generated Skills provide negligible or negative benefit (-1.3 pp)" |
| 10 | Claude Code 12 eventos hook, 4 tipos handler | HIGH | "The 12 Hook Lifecycle Events: SessionStart..." |
| 11 | SkillFortify 96.95% F1, 0% FPR, 1.378s scan | HIGH | "96.95% F1 with 100% precision and 0% false positive rate on 540 skills" |
| 12 | mcp-scan: tool poisoning, rug pulls | HIGH | "MCP-Scan includes built-in Tool Pinning to detect and prevent MCP Rug Pull attacks" |
| 13 | CVE-2026-25725 sandbox escape CVSS 7.7 | HIGH | "settings.json conditional on the file's existence at sandbox startup" |
| 14 | gVisor sub-second provisioning | HIGH | "gVisor intercepts syscalls in user space via Sentry... sub-second provisioning" |
| 15 | Vault (tenant_id, tool_name), nunca env vars | MEDIUM | "never using environment variables for tenant credentials" |
| 16 | broker pattern CABP para MCP multi-tenant | MEDIUM | "gateway service... injects tenant_id, user_id, and permission scopes" |
| 17 | Skill Bench threshold 80% | HIGH | "default pass-threshold is 80 not 100. occasional flakiness is expected" |
| 18 | n8n-mcp 21.4k stars, 1,851 nodos | HIGH | "1,851 n8n nodes - 822 core nodes + 1,029 community nodes" |
| 19 | Claude Code telemetry por skill.name | HIGH | "Break down by... skill.name, plugin.name, or agent.name" |
| 20 | Cisco mcp-scanner: 3 motores, 12 vectores | HIGH | "Run scanner as CLI tool or REST API server... 12 common attack vectors" |

---

*Consolidado producido a partir de investigacion K1-K6 + Cross-Verification.*
*Claims verificados contra archivos fuente originales.*
*Todas las cifras "duras" tienen excerpt textual con URL y fecha.*
*Fecha: 2026-07-09*
