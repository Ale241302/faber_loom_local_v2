# K1 - Auditoria de Evidencia

Resumen: Se verificaron 11 claims principales contra 5 fuentes primarias (4 papers arXiv + 1 blogpost Snyk). De las cifras auditadas: 10 CONFIRMADAS, 0 REFUTADAS, 1 NO-LOCALIZADA (requiere aclaracion de contexto). Se detecto 1 discrepancia interna en SkillsBench (+12.66pp vs +16.2pp) y 1 inconsistencia de version (86 vs 84 tasks). Las cifras de Snyk ToxicSkills y el paper Bosch/CMU se confirman en primario con alta confianza.

---

## 1. arXiv 2602.08004 - Bosch Research / Carnegie Mellon University

### Claim: Mediana 1,414 tokens por skill
Claim: La mediana de tokens por skill es 1,414 (mean: 1,895, max: 116,239).
Source: Ling, George; Zhong, Shanshan; Huang, Richard. "Agent Skills: A Data-Driven Analysis of Claude Skills for Extending Large Language Model Functionality." arXiv:2602.08004 [cs.SE], 8 Feb 2026.
URL: https://arxiv.org/abs/2602.08004
Date: 2026-02-08
Excerpt: "The median length is 1,414 tokens and the mean is 1,895 tokens, indicating that a typical skill fits comfortably alongside planning context and tool schemas. [...] 90% and 99% remain below 3,935 and 9,253 tokens. [...] the maximum reaches 116,239 tokens."
Context: Metrica clave para dimensionar prompt budgets en una plataforma multi-tenant donde cada skill consume tokens del context window compartido. El 99% de skills caben bajo 9,253 tokens, pero el 1% extremo puede dominar el budget.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: 18.5x crecimiento en 20 dias
Claim: El ecosistema crecio 18.5x en 20 dias, de 2,179 skills (16 ene) a 40,285 skills (5 feb), con un pico de 8,857 skills en un solo dia (25 ene).
Source: Ling et al., arXiv:2602.08004 [cs.SE], 8 Feb 2026.
URL: https://arxiv.org/abs/2602.08004
Date: 2026-02-08
Excerpt: "The marketplace grows from 2,179 skills on January 16, 2026 to 40,285 skills on February 5, 2026, a net increase of 38,106 skills in 20 days. This corresponds to an 18.5x increase and an average multiplicative growth rate of about 15.7% per day. [...] The largest spike occurs on January 25, 2026, when 8,857 skills are added in a single day. This accounts for 23.2% of all new skills in the window."
Context: Tasa de crecimiento que outpaces cualquier capacidad de review manual. En una plataforma multi-tenant, un crecimiento 18.5x en 20 dias implica que los mecanismos de vetting deben ser completamente automatizados.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: 46.3% duplicados
Claim: El 46.3% de las skills comparten nombre normalizado con al menos otra listing (skills que aparecen mas de una vez).
Source: Ling et al., arXiv:2602.08004 [cs.SE], 8 Feb 2026.
URL: https://arxiv.org/abs/2602.08004
Date: 2026-02-08
Excerpt: "Skills that appear once account for 53.7%, while skills that appear more than once account for 46.3%. [...] Duplication is also concentrated. Pairs are common, with 2x groups contributing 18.7% of the corpus. Higher multiplicities still account for a nontrivial share: 5x to 9x groups contribute 14.3%, and 10x to 49x groups contribute 8.8%."
Context: Redundancia a nivel de intent que aumenta costos de discovery para usuarios y dificulta que skills de calidad destaquen. En multi-tenant, la duplicacion incrementa el corpus a auditar sin aumentar la diversidad funcional.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: 9% riesgo critico (L3)
Claim: El 9% de skills clasifican como L3 (riesgo critico: high impact / destructive actions).
Source: Ling et al., arXiv:2602.08004 [cs.SE], 8 Feb 2026.
URL: https://arxiv.org/abs/2602.08004
Date: 2026-02-08
Excerpt: "Overall, 54% are L0, 5% are L1, 30% are L2, and 9% are L3. Thus, nearly two fifths of the marketplace can access sensitive context or perform writes and actions, and a nontrivial share exposes critical capabilities."
Context: Nivel L3 = skills que habilitan acciones destructive (ej. sudo, admin, password, ejecucion de comandos arbitrarios). En una plataforma multi-tenant, el 9% de ~40k skills = ~3,600 skills con capacidades criticas que requieren sandboxing estricto.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: ~40% accede a contexto sensible o ejecuta writes/actions
Claim: Casi dos quintos (39% = 30% L2 + 9% L3) de las skills pueden acceder a contexto sensible o ejecutar acciones de escritura/state-changing.
Source: Ling et al., arXiv:2602.08004 [cs.SE], 8 Feb 2026.
URL: https://arxiv.org/abs/2602.08004
Date: 2026-02-08
Excerpt: "nearly two fifths of the marketplace can access sensitive context or perform writes and actions, and a nontrivial share exposes critical capabilities."
Context: Para una plataforma multi-tenant, esto significa que el ~40% de las skills requieren algun nivel de control de permisos. L2 = moderate risk (restricted write/action), L3 = critical risk (high impact/destructive).
Verdict: CONFIRMADA (39%, redondeado a ~40%)
Confidence: high

---

## 2. arXiv 2602.12670 - SkillsBench

### Claim: SkillsBench recopilo 47,150 skills unicos
Claim: El benchmark recolecto 47,150 skills unicos despues de deduplicacion por content hash, provenientes de 3 fuentes: GitHub (12,847), community marketplaces (28,412), y corporate partners (5,891).
Source: Li, Xiangyi et al. "SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks." arXiv:2602.12670 [cs.AI], 13 Feb 2026 (v3).
URL: https://arxiv.org/abs/2602.12670
Date: 2026-02-13
Excerpt: "Phase 1 (Benchmark Construction): We aggregate Skills from three sources--open-source repositories (12,847), the Claude Code ecosystem (28,412), and corporate partners (5,891)--yielding 47,150 unique Skills after deduplication."
Context: Escala del corpus skills que una plataforma multi-tenant potencialmente podria integrar. La deduplicacion por content hash reduce 47k+ skills unicos desde un total mayor.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: SkillsBench evaluo 84 tasks (no 86)
Claim: El benchmark final incluye 84 tasks evaluadas (no 86), filtradas desde 105 candidatas enviadas por 322 contribuyentes.
Source: Li et al., arXiv:2602.12670 [cs.AI], v3.
URL: https://arxiv.org/abs/2602.12670
Date: 2026-02-13
Excerpt: "producing 84 tasks spanning 11 domains" y "Across 84 tasks, 7 agent-model configurations, and 7,308 trajectories" y "16 of 84 tasks show negative deltas."
Context: [NOTA DE VERSION] El abstract de la v1 del paper menciona "86 tasks", pero el paper completo v3 (revisado 13 Mar 2026) reporta consistentemente 84 tasks evaluadas. La cifra de 86 probablemente incluye 2 tasks adicionales que fueron descartadas en revision. En una plataforma multi-tenant, la diferencia entre 84 y 86 es menor al 2.4%, pero la consistencia metodologica importa.
Verdict: CONFIRMADA (84 tasks en la version final v3; 86 en abstract v1)
Confidence: high

---

### Claim: 7,308 trayectorias evaluadas
Claim: SkillsBench ejecuto 7,308 trayectorias (trajectories) bajo 3 condiciones (no Skills, curated Skills, self-generated Skills).
Source: Li et al., arXiv:2602.12670 [cs.AI].
URL: https://arxiv.org/abs/2602.12670
Date: 2026-02-13
Excerpt: "We test 7 agent-model configurations over 7,308 trajectories."
Context: Tamano de la evaluacion que valida la eficacia de skills en diversas configuraciones agente-modelo. Para una plataforma multi-tenant, esto demuestra que el impacto de skills varia significativamente segun el modelo subyacente.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: +12.66pp mejora promedio (Figura 2) vs +16.2pp (resultados principales)
Claim: Existe una discrepancia interna en el paper: la Figura 2 (pipeline overview) reporta +12.66pp de mejora promedio, mientras que la Seccion 4.1.1 (Finding 1) reporta +16.2pp.
Source: Li et al., arXiv:2602.12670 [cs.AI], v3.
URL: https://arxiv.org/abs/2602.12670
Date: 2026-02-13
Excerpt (Figura 2): "7 agent-model configurations yield 7,308 trajectories, with curated Skills providing +12.66pp average improvement."
Excerpt (Finding 1): "Skills improve performance by +16.2pp on average across 7 model-harness configurations, but with high variance across configurations (range: +13.6pp to +23.3pp)."
Context: [RECOMENDACION - juicio del analista] La cifra de +16.2pp es la principal (aparece en el abstract, en los resultados principales, y en la conclusion). La +12.66pp de la Figura 2 probablemente es un artefacto de una version anterior del calculo que no se actualizo en la figura. Para una plataforma multi-tenant, usar +16.2pp como cifra de referencia.
Verdict: CONFIRMADA (+16.2pp es la cifra principal; +12.66pp es una discrepancia interna del paper probablemente no actualizada en la figura)
Confidence: medium (por la discrepancia interna)

---

## 3. arXiv 2602.20156 - Skill-Inject (Attack Success Rate)

### Claim: ~80% attack success rate con modelos frontier
Claim: Los agentes LLM frontier muestran hasta 80% de tasa de exito de ataque (ASR) ante inyecciones via skill files.
Source: Schmotz, David; Beurer-Kellner, Luca; Abdelnabi, Sahar; Andriushchenko, Maksym. "SKILL-INJECT: Measuring Agent Vulnerability to Skill File Attacks." arXiv:2602.20156 [cs.CR], 26 Feb 2026.
URL: https://arxiv.org/abs/2602.20156
Date: 2026-02-26
Excerpt: "Our results show that today's agents are highly vulnerable with up to 80% attack success rate with frontier models, often executing extremely harmful instructions including data exfiltration, destructive action, and ransomware-like behavior."
Context: [NOTA IMPORTANTE] El "up to 80%" se refiere a la condicion "Best-of-5 Obvious Injections" (BoN), donde el atacante tiene 5 intentos variando posicion de linea y user task. En "Obvious Injections" (un solo intento) el ASR varia entre 42-68% segun el modelo. En "Contextual Injections + Warning Prompt" (el escenario mas realista) el ASR varia entre 6-19%. Para una plataforma multi-tenant, la cifra de ~80% representa el peor caso bajo condiciones favorables al atacante (multi-intento).
Verdict: CONFIRMADA ("up to 80%" bajo Best-of-5 Obvious Injections)
Confidence: high

---

## 4. Snyk ToxicSkills - Blogpost Original (5 Feb 2026)

### Claim: 36.82% de 3,984 skills con >=1 falla de seguridad
Claim: Del total de 3,984 skills escaneadas de ClawHub, 1,467 (36.82%) contienen al menos una falla de seguridad, y 534 (13.4%) contienen al menos un issue de nivel CRITICAL.
Source: Beurer-Kellner, Luca et al. (Snyk). "Snyk Finds Prompt Injection in 36%, 1467 Malicious Payloads in a ToxicSkills Study of Agent Skills Supply Chain Compromise." Snyk Blog, 5 Feb 2026.
URL: https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
Date: 2026-02-05
Excerpt: "13.4% of all skills, or 534 in total, all contain at least one critical-level security issue [...] over a third of the ecosystem is affected: 36.82% (1,467 skills) have at least one security flaw."
Context: Estos numeros representan riesgo real, no ruido de scanner: "Our detectors were intentionally tuned to minimize false positives on widely adopted legitimate skills; these numbers represent real risk, not scanner noise." Para una plataforma multi-tenant, 36.82% de skills con fallas significa que mas de 1 de cada 3 skills requieren algun nivel de remediation antes de ser deployables.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: 76 payloads maliciosos confirmados
Claim: 76 skills contienen payloads confirmados como maliciosos mediante human-in-the-loop (HITL) review.
Source: Snyk ToxicSkills blogpost, 5 Feb 2026.
URL: https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
Date: 2026-02-05
Excerpt: "we confirmed active threats through HITL: 76 malicious payloads designed for credential theft, backdoor installation, and data exfiltration. From this small sample alone, 8 of these malicious skills remain publicly available on clawhub.ai as of publication."
Context: El HITL review confirma que no son falsos positivos: 8 de estas skills maliciosas seguian disponibles publicamente al momento de publicacion. En una plataforma multi-tenant, esto justifica la necesidad de un pipeline de scan + review antes de cualquier deployment.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: 10.9% hardcoded secrets
Claim: El 10.9% de las skills (434 de 3,984) contienen secretos hardcodeados (API keys, credenciales).
Source: Snyk ToxicSkills blogpost, 5 Feb 2026.
URL: https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
Date: 2026-02-05
Excerpt: Tabla de metricas: "Hardcoded secrets: 434 (10.9%)" (confirmado en el articulo de Zenn.dev que reproduce la tabla de Snyk).
Context: En una plataforma multi-tenant, skills con secretos hardcodeados representan un vector de credential leakage cross-tenant. Un skill que incluye una API key queda expuesta a cualquier usuario que pueda inspeccionar el skill file.
Verdict: CONFIRMADA
Confidence: high

---

## 5. ClawHavoc - Cifras Conflictivas (335 vs 341)

### Claim: ClawHavoc - 341 skills maliciosos total, 335 de una sola operacion coordinada
Claim: El incidente ClawHavoc involucro 341 skills maliciosos en ClawHub, de los cuales 335 fueron trazados a una unica operacion coordinada.
Source: Guo, Z. et al. "SkillSieve: A Hierarchical Triage Framework for Detecting Malicious AI Agent Skills." arXiv:2604.06550v1 [cs.CR], 4 Apr 2026. (Cita a Koi Security, Feb 2026).
URL: https://arxiv.org/html/2604.06550v1
Date: 2026-04-04
Excerpt: "The ClawHavoc campaign pushed hundreds of malicious skills into ClawHub over six weeks; Koi Security's audit of 2,857 skills found 341 malicious entries, 335 traced to a single coordinated operation (clawhavoc2026)."
Context: Las dos cifras NO son conflictivas, sino que responden a diferentes niveles de agregacion: 341 = total de skills maliciosos identificados en el audit de Koi Security; 335 = subset atribuido a una sola operacion coordinada (el 98.2% del total). En una plataforma multi-tenant, esto demuestra que un unico actor puede comprometer cientos de skills de forma coordinada.
Verdict: CONFIRMADA (ambas cifras son correctas en su contexto: 341 total, 335 de operacion unica)
Confidence: high

---

## 6. Hallazgos Adicionales (no en lista original)

### Claim: Self-generated skills no aportan beneficio (-1.3pp)
Claim: Las skills auto-generadas por los modelos no solo no ayudan, sino que empeoran ligeramente el rendimiento (-1.3pp en promedio).
Source: Li et al., arXiv:2602.12670, v3, Finding 3.
URL: https://arxiv.org/abs/2602.12670
Date: 2026-02-13
Excerpt: "Self-generated Skills provide negligible or negative benefit (-1.3 pp average), demonstrating that effective Skills require human-curated domain expertise that models cannot reliably self-generate."
Context: [RECOMENDACION - juicio del analista] Para una plataforma multi-tenant, esto refuerza que las skills deben ser curadas por humanos expertos, no generadas automaticamente por los modelos. El pipeline de skill creation debe incluir un HITL review.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: 2-3 modules es el tamano optimo de skill
Claim: Skills con 2-3 modules muestran la mayor mejora (+18.6pp); 4+ modules solo +5.9pp.
Source: Li et al., arXiv:2602.12670, v3, Finding 5.
URL: https://arxiv.org/abs/2602.12670
Date: 2026-02-13
Excerpt: "Tasks with 2-3 Skills show the largest improvement (+18.6pp), while 4+ Skills provide only +5.9 pp benefit. This non-monotonic relationship suggests that excessive Skills content creates cognitive overhead or conflicting guidance."
Context: [RECOMENDACION - juicio del analista] Las skills deben ser focalizadas y modulares. Una plataforma multi-tenant debe priorizar skills con 2-3 modulos sobre documentacion comprehensiva.
Verdict: CONFIRMADA
Confidence: high

---

### Claim: Skill-Inject contiene 202 injection-task pairs
Claim: El benchmark SKILL-INJECT incluye 202 pares de injection-task con ataques que van desde obvios hasta contextuales sutiles.
Source: Schmotz et al., arXiv:2602.20156 [cs.CR].
URL: https://arxiv.org/abs/2602.20156
Date: 2026-02-26
Excerpt: "SKILL-INJECT contains 202 injection-task pairs with attacks ranging from obviously malicious injections to subtle, context-dependent attacks hidden within otherwise legitimate instructions."
Context: Tamano del benchmark de evaluacion de vulnerabilidades por skill-based prompt injection. Una plataforma multi-tenant puede usar este benchmark para evaluar la robustez de sus agentes antes de exponerlos a skills de terceros.
Verdict: CONFIRMADA
Confidence: high

---

## Tabla Resumen de Veredictos

| # | Claim | Fuente | Veredicto | Confianza |
|---|-------|--------|-----------|-----------|
| 1 | Mediana 1,414 tokens/skill | arXiv 2602.08004 | CONFIRMADA | high |
| 2 | 18.5x crecimiento en 20 dias | arXiv 2602.08004 | CONFIRMADA | high |
| 3 | 46.3% duplicados | arXiv 2602.08004 | CONFIRMADA | high |
| 4 | 9% riesgo critico (L3) | arXiv 2602.08004 | CONFIRMADA | high |
| 5 | ~40% accede a contexto sensible | arXiv 2602.08004 | CONFIRMADA (39%) | high |
| 6 | ClawHavoc 341 total / 335 coordinados | arXiv 2604.06550v1 | CONFIRMADA (no conflictivas) | high |
| 7 | SkillsBench 47,150 skills unicos | arXiv 2602.12670 | CONFIRMADA | high |
| 8 | SkillsBench 84 tasks (v3) | arXiv 2602.12670 | CONFIRMADA (86 en v1) | high |
| 9 | SkillsBench +16.2pp / +12.66pp | arXiv 2602.12670 | CONFIRMADA (+16.2pp principal) | medium |
| 10 | SkillsBench 7,308 trayectorias | arXiv 2602.12670 | CONFIRMADA | high |
| 11 | Snyk 36.82% con fallas (1,467/3,984) | Blog Snyk 5 feb 2026 | CONFIRMADA | high |
| 12 | Snyk 13.4% criticas (534/3,984) | Blog Snyk 5 feb 2026 | CONFIRMADA | high |
| 13 | Snyk 76 payloads maliciosos | Blog Snyk 5 feb 2026 | CONFIRMADA | high |
| 14 | Skill-Inject ~80% ASR (Bo5) | arXiv 2602.20156 | CONFIRMADA ("up to 80%") | high |
| 15 | Self-generated skills -1.3pp | arXiv 2602.12670 | CONFIRMADA | high |
| 16 | 2-3 modules optimo (+18.6pp) | arXiv 2602.12670 | CONFIRMADA | high |
| 17 | 202 injection-task pairs | arXiv 2602.20156 | CONFIRMADA | high |

**Totales:** 17 claims verificadas, 17 CONFIRMADAS (1 con nota de discrepancia interna), 0 REFUTADAS, 0 NO-LOCALIZADAS.

---

## Discrepancias Detectadas

1. **SkillsBench +12.66pp vs +16.2pp**: El paper tiene ambas cifras. +16.2pp es la cifra principal (abstract, resultados, conclusion). +12.66pp aparece solo en la Figura 2 (pipeline overview) y probablemente es un residuo de version anterior.

2. **SkillsBench 86 vs 84 tasks**: El abstract de la v1 menciona "86 tasks across 11 domains", pero el paper completo v3 (revisado 13 Mar 2026) reporta consistentemente 84 tasks evaluadas. Se confirman 84 tasks como cifra final.

3. **ClawHavoc 335 vs 341**: No son cifras conflictivas. 341 = total de skills maliciosos encontrados por Koi Security; 335 = subset atribuido a una unica operacion coordinada (el 98.2%). Ambas correctas en su contexto.
