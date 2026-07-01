# K6 - Seguridad y Gobernanza Profunda

Resumen: El estado del arte en defensa de skills a junio 2026 combina escaneo heuristico (Snyk, Cisco, NVIDIA), analisis formal (SkillFortify), verificacion de publicadores (NVIDIA verified skills), firma criptografica (OpenSSF Model Signing, Sigstore), sandboxing (gVisor, Firecracker), policy enforcement en runtime (Claude Code permissions/hooks), y pinning via lockfiles (SHA-512/SHA-256). Sin embargo, NO existe aun una solucion integrada que cubra attestation de publisher + sandboxing runtime + allowlist de red + deteccion de injection indirecta cross-tool + break-glass auditado. Todas las defensas son parciales y se necesita composicion defensa-en-profundidad. El 36% de skills tiene fallas y el 91% del malware combina prompt injection con payloads tradicionales, lo que requiere defensa multicapa.

---

Claim: SkillFortify es el primer framework de analisis formal para supply chain de agent skills, con 6 contribuciones: modelo de atacante DY-Skill, analisis estatico via interpretacion abstracta, sandboxing basado en capabilities con prueba de confinamiento, Agent Dependency Graph con resolucion SAT, algebra de trust score, y benchmark de 540 skills. Logra 96.95% F1 con 0% falsos positivos.
Source: SkillFortify paper
URL: https://arxiv.org/abs/2603.00195
Date: 2026-02-27
Excerpt: "SkillFortify achieves 96.95% F1 (95% CI: [95.1%, 98.4%]) with 100% precision and 0% false positive rate on 540 skills, while SAT-based resolution handles 1,000-node graphs in under 100 ms."
Context: SkillFortify es la unica herramienta con garantias formales (soundness, confinement, resolution correctness). Disponible via pip install skillfortify. El analisis estatico demuestra que si Viol(s)=0, ninguna operacion excede las capabilities declaradas. Escaneo de 540 skills en 1.378 segundos (2.55ms/skill).
Confidence: high

---

Claim: SkillFortifyBench contiene 540 skills (270 benignos, 270 maliciosos) distribuidos en 3 formatos (Claude Code, MCP, OpenClaw) con 13 tipos de ataque documentados desde incidentes reales (ClawHavoc, MalTool, CVE-2026-25253). Precision 100%, Recall 94.07%, FPR 0.00%.
Source: SkillFortify Evaluation
URL: https://arxiv.org/html/2603.00195v1#S9
Date: 2026-02-27
Excerpt: "SkillFortify achieves an F1 score of 96.95% with zero false positives... The 94.07% recall should be interpreted as a lower bound on content-analyzable attacks."
Context: El benchmark usa constructive ground truth con generador deterministico (seed=42). Los 13 tipos de ataque cubren: exfiltracion HTTP/DNS, robo de credenciales, RCE, tampering de filesystem, privilege escalation, steganografia, prompt injection, reverse shell, crypto mining, typosquatting, dependency confusion, y payloads ofuscados.
Confidence: high

---

Claim: Snyk ToxicSkills (febrero 2026) escaneo 3,984 skills: 36.82% con >=1 falla, 13.4% criticas, 76 payloads maliciosos confirmados, 8 aun disponibles en ClawHub al momento de publicacion. El 91% del malware combina prompt injection con tecnicas tradicionales.
Source: Snyk Blog
URL: https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/
Date: 2026-02-05
Excerpt: "13.4% of all skills, or 534 in total, all contain at least one critical-level security issue... 36.82% (1,467 skills) have at least one security flaw... 76 malicious payloads... 91% of malicious skills combine prompt injection with traditional malware."
Context: Snyk adquirio Invariant Labs (creadores de mcp-scan). Los datos son la auditoria mas exhaustiva del ecosistema de skills hasta la fecha. Las skills heredan permisos completos del agente: shell, filesystem, credenciales, canales de mensajeria, memoria persistente.
Confidence: high

---

Claim: Agent Skills in the Wild (Park et al.) analizo 42,447 skills y encontro 26.1% con vulnerabilidades, 14 patrones distintos, 5.2% con patrones de alta severidad sugiriendo intencion maliciosa. SkillScan logra 86.7% precision y 82.5% recall.
Source: arXiv 2601.10338
URL: https://arxiv.org/abs/2601.10338
Date: 2026-01-15
Excerpt: "26.1% of skills contain at least one vulnerability, spanning 14 distinct patterns across four categories: prompt injection, data exfiltration, privilege escalation, and supply chain risks."
Context: Skills que incluyen scripts ejecutables son 2.12x mas propensos a vulnerabilidades que skills de solo instrucciones (OR=2.12, p<0.001). Metodologia validada abierta para futura investigacion.
Confidence: high

---

Claim: NVIDIA implemento el primer programa de skills verificados con pipeline completo: catalog → scan (SkillSpector) → sign (OpenSSF Model Signing) → skill card. Las skills firmadas usan certificados X.509 y se verifican con model_signing verify certificate.
Source: NVIDIA Developer Blog
URL: https://developer.nvidia.com/blog/nvidia-verified-agent-skills-provide-capability-governance-for-ai-agents/
Date: 2026-05-28
Excerpt: "The signature covers every file and subdirectory in the skill directory... Certificate retrieval, supported verification tooling, and example verification commands see the signing documentation."
Context: NVIDIA usa skill.oms.sig con OpenSSF Model Signing. El comando de verificacion usa certificado raiz nv-agent-root-cert.pem. Compatible con Claude Code, Codex y Cursor. SkillSpector escanea 64 patrones en 16 categorias basadas en OWASP LLM y MITRE ATLAS.
Confidence: high

---

Claim: Pruner (Coroboros) produce attestations firmadas con Sigstore para skills de agentes AI. Es una GitHub Action que genera report-v1.json + CycloneDX SBOM + SLSA build provenance, firmados con public-good Sigstore y GitHub OIDC, adjuntos a cada release tag.
Source: GitHub - ob-aion/pruner
URL: https://github.com/ob-aion/pruner
Date: 2026-05-12
Excerpt: "Pruner produces a portable, signed trust artefact that travels with every release tag... Consumers verify with gh attestation verify; no Coroboros service sits in the trust path."
Context: Cubre el gap de que git-clone directo de un repo de skills bypassa cualquier auditoria del registro, y una vez instalada la skill, el drift post-publicacion nunca se re-escanea. La vision es proponer report-v1 como spec a OpenSSF Working Group on Supply-Chain Integrity.
Confidence: high

---

Claim: mcp-scan (Invariant Labs/Snyk, >2,000 estrellas) es el scanner de facto para MCP. Detecta tool poisoning, rug pulls (via hash-based tool pinning), cross-origin escalations, y prompt injection. Se ejecuta con uvx mcp-scan@latest sin configuracion.
Source: Stytch Blog / Invariant Labs
URL: https://stytch.com/blog/mcp-scan/
Date: 2025-05-02
Excerpt: "MCP-Scan includes built-in Tool Pinning to detect and prevent MCP Rug Pull attacks, verifying the integrity of installed tools by tracking changes via tool hashing."
Context: El tool pinning hashea descripciones de herramientas en el primer escaneo y alerta si cambian (rug pull). Integracion con GitHub Actions en 3 lineas de YAML. Usa Invariant Guardrails API para deteccion semantica. Limitacion: requiere compartir nombres y descripciones de herramientas con Invariant.
Confidence: high

---

Claim: Cisco mcp-scanner es una herramienta open-source (Apache 2.0) con 3 motores de escaneo: YARA, LLM-as-judge, y Cisco AI Defense API. Soporta scanning de tools, prompts, resources, instructions, behavioral code scanning, VirusTotal binary scanning, y prompt defense scanning (12 vectores de ataque).
Source: GitHub - cisco-ai-defense/mcp-scanner
URL: https://github.com/cisco-ai-defense/mcp-scanner
Date: 2026-05-29
Excerpt: "The MCP Scanner provides a comprehensive solution... Multiple Modes: Run scanner as a stand-alone CLI tool or REST API server... Prompt Defense Analyzer checks for missing defensive measures against 12 common attack vectors."
Context: Los 12 vectores de ataque del Prompt Defense Analyzer incluyen: Instruction Override, Data Leakage, Role Escape, Indirect Injection, Output Weaponization, Output Manipulation, Multilingual Bypass, Unicode/Homoglyph Attack, Context Overflow, Social Engineering, Input Validation, Abuse Prevention. Soporta escaneo estatico/offline para CI/CD.
Confidence: high

---

Claim: Claude Code tiene un sistema de permisos jerarquico con allow/ask/deny rules, donde deny tiene precedencia. Soporta hooks (PreToolUse, PostToolUse, SessionStart) para enforcement custom, y managed settings que el desarrollador no puede sobrescribir.
Source: Claude Code Docs
URL: https://code.claude.com/docs/en/permissions
Date: 2025-09-01
Excerpt: "Rules are evaluated in order: deny -> ask -> allow. The first matching rule wins, so deny rules always take precedence... PreToolUse hooks run before the permission prompt. The hook output can deny the tool call."
Context: disableBypassPermissionsMode = "disable" es la configuracion mas critica para enterprise, evita que developers usen --dangerously-skip-permissions. Managed settings via server (Claude admin console), macOS plist, Windows registry, o Linux file-based. Reportado bug (marzo 2026) donde deny rules de Console no se enforceaban en runtime.
Confidence: high

---

Claim: CVE-2026-25725 demostro escape de sandbox en Claude Code (CVSS 7.7): bubblewrap montaba .claude/settings.json como read-only solo si el archivo existia al inicio, pero por defecto NO existe, permitiendo a un atacante dentro del sandbox crear hooks persistentes que ejecutan en el host.
Source: Cymulate Research
URL: https://cymulate.com/blog/the-race-to-ship-ai-tools-left-security-behind-part-1-sandbox-escape/
Date: 2026-05-03
Excerpt: "The read-only protection for .claude/settings.json is conditional on the file's existence at sandbox startup. Critically, this file does not exist by default... the .claude/ parent directory is mounted as writable, allowing file creation inside the sandbox."
Context: La clase de vulnerabilidad es Configuration-Based Sandbox Escape (CBSE). Se reprodujo en herramientas de Anthropic, Google y OpenAI. Patcheado en v2.1.2. El descubrimiento responsable duro 16 dias fix-to-deploy. Los hooks (SessionStart, PreToolUse, PostToolUse) ejecutan SIN confirmacion ni notificacion.
Confidence: high

---

Claim: GKE Agent Sandbox usa gVisor (runsc) como runtime OCI para aislamiento a nivel de kernel de codigo generado por LLM. Proporciona perfiles seccomp/AppArmor optimizados para workloads de agentes AI y observabilidad integrada via Cloud Monitoring.
Source: Google Dev Blog
URL: https://dev.to/gde/untrusted-code-trusted-cluster-scaling-secure-ai-agent-workspaces-with-gke-agent-sandbox-1mk1
Date: 2026-05-31
Excerpt: "gVisor intercepts those same syscalls in user space via Sentry... When your agent code calls execve(), it's Sentry that handles it, not the host kernel... sub-second provisioning."
Context: La arquitectura split brain separa node pool estandar (orquestacion confiable) de Agent Sandbox node pool (ejecucion de codigo no confiable). gVisor implementa Linux ABI desde cero en userspace. Alternativas: Firecracker (~125ms, VM dedicada), Kata Containers (Kubernetes-native con Firecracker).
Confidence: high

---

Claim: MCPShield implementa mcp.lock.json con SHA-512 content hashes para tamper detection de configuraciones MCP server, pero NO realiza analisis behavioral, resolucion de dependencias, ni verificacion de capabilities.
Source: SkillFortify paper (seccion Related Work)
URL: https://arxiv.org/html/2603.00195v1
Date: 2026-02-27
Excerpt: "MCPShield's lockfile provides integrity verification (detecting unauthorized modifications), it does not perform behavioral analysis, dependency resolution, or capability verification."
Context: El lockfile de SkillFortify extiende MCPShield: cada entrada locked registra resultado de resolucion SAT con version constraints y security bounds, trust score computado, y status de analisis formal — haciendolo un formally-proven satisfying assignment, no solo un integrity manifest.
Confidence: high

---

Claim: Microsoft APM (Agent Package Manager) implementa lockfile pinning con resolved_commit de 40 caracteres y content_hash SHA-256 para cada dependencia, con fresh-download hash check y cache-hit verification via .git/HEAD comparison.
Source: Microsoft APM Security Docs
URL: https://microsoft.github.io/apm/enterprise/security-and-supply-chain/
Date: 2026-05-28
Excerpt: "apm.lock.yaml records the full 40-char resolved_commit for every dep and the content_hash (SHA-256 over the sorted file tree) of what was installed... On mismatch the cache entry is evicted and a fresh fetch runs."
Context: APM defende reproducibilidad, integridad, provenance (cada dep traza a un commit pinnned en un host nombrado), y pre-deploy content safety (no hidden Unicode). NO hace sandboxing runtime, malware analysis, signing, ni inspection de comportamiento del agente.
Confidence: high

---

Claim: OWASP publico el Top 10 para Agentic Applications (ASI) en 2026 con 10 riesgos: Goal Hijack, Tool Misuse, Identity & Privilege Abuse, Supply Chain Compromise, Unexpected Code Execution, Memory Poisoning, Insecure Inter-Agent Communication, Cascading Failures, Human-Agent Trust Exploitation, Rogue Agents.
Source: DeepTeam / OWASP
URL: https://trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications
Date: 2026-04-05
Excerpt: "Agentic systems can cause cascading failures where a single vulnerability propagates through connected tools, memory, and other agents, leading to large-scale security incidents."
Context: ASI04 (Supply Chain Compromise) cubre skills maliciosas como categoria principal. ASI07 (Insecure Inter-Agent Communication) es un riesgo nuevo que no existe en LLM apps tradicionales. La estrategia recomendada es testear contra AMBOS frameworks: LLM Top 10 + ASI Top 10.
Confidence: high

---

Claim: Gen Digital propone skill fingerprinting con firma CMS (Cryptographic Message Syntax) al estilo Authenticode: compute Skill ID excluyendo skill.sig, parse CMS envelope, confirma payload firmado, valida cadena de certificados hasta root, check revocation via CRL/OCSP.
Source: Gen Digital Research
URL: https://www.gendigital.com/blog/insights/research/ai-agent-skill-fingerprinting
Date: 2026-05-28
Excerpt: "Verification follows the same pattern as Authenticode: compute the Skill ID while excluding skill.sig, parse the CMS envelope, confirm the signed payload matches the computed ID, build the certificate chain up to a trusted root."
Context: Habilita varios modelos de confianza: Author signing (firma de autor), Marketplace attestation (countersign de marketplace), Private CA (empresas con CA propia), Revocation (CRL cuando la clave se compromete). Es un estandar independiente de vendor.
Confidence: high

---

Claim: OMNI-LEAK demuestra que arquitecturas multi-agente crean canales implicitos de informacion a traves de los cuales datos sensibles pueden filtrarse a traves de trust boundaries, incluso cuando agentes individuales parecen bien aislados.
Source: OMNI-LEAK paper (citado en SkillFortify)
URL: https://arxiv.org/html/2603.00195v1
Date: 2026 (citado)
Excerpt: "OMNI-LEAK demonstrates that multi-agent architectures create implicit information channels through which sensitive data can leak across trust boundaries — even when individual agents appear well-isolated."
Context: Este es el unico trabajo encontrado sobre deteccion de filtracion cross-tool indirecta. No se encontro herramienta comercial o open-source especifica para deteccion de "indirect injection via contenido de terceros" entre skills. Cisco prompt_defense detecta "Indirect Injection" como uno de sus 12 vectores, pero es analisis estatico de descripciones, no deteccion runtime de manipulacion cross-tool.
Confidence: medium

---

Claim: SkillFortify propone (como future work C7) un "Skill Registry Verification Protocol" analogo a Sigstore para artefactos software, con keyless signing via OpenID Connect, transparency logs para eventos de publicacion, y verificacion de build provenance.
Source: SkillFortify paper (seccion Future Work)
URL: https://arxiv.org/html/2603.00195v1
Date: 2026-02-27
Excerpt: "A cryptographic signing and attestation protocol for agent skills, analogous to Sigstore for software artifacts... keyless signing via OpenID Connect identity providers, transparency logs for skill publication events, and verification of build provenance through reproducible build attestations."
Context: Este future work NO esta implementado aun (junio 2026). La vision es proveer end-to-end provenance guarantees desde el skill author hasta el agent runtime. Pruner (Corobos) ya implementa parcialmente esto con Sigstore para skills individuales.
Confidence: medium

---

Claim: Claude Code soporta telemetry via OpenTelemetry para monitoreo de uso, cost, token activity, tool activity, permission-mode changes, API errors, MCP server connections, hooks, y otros eventos. Managed telemetry env vars tienen alta precedencia y no pueden ser sobreescritas por usuarios.
Source: Checkmarx / Claude Code Docs
URL: https://checkmarx.com/learn/ai-security/claude-code-security-top-6-risks-controls-and-best-practices/
Date: 2026-05-12
Excerpt: "Managed telemetry environment variables have high precedence and cannot be overridden by users."
Context: El audit logging se configura via PostToolUse hooks (escritura de registros estructurados a pipeline propia) o via OpenTelemetry exporters. No hay break-glass nativo integrado en Claude Code: el kill-switch se implementa via hooks (PreToolUse que bloquea) + managed settings + denylists de MCP servers. Esto es un workaround, no un sistema de break-glass auditado propiamente dicho.
Confidence: medium

---

Claim: Cisco skill-scanner (mcp-scanner) tiene un analizador de "Prompt Defense" que verifica defensas faltantes contra 12 vectores de ataque comunes, incluyendo "Indirect Injection" (HIGH). Es puramente regex — sin API key ni dependencias externas.
Source: GitHub - cisco-ai-defense/mcp-scanner
URL: https://github.com/cisco-ai-defense/mcp-scanner
Date: 2026-05-29
Excerpt: "The Prompt Defense Analyzer checks MCP tool descriptions and system prompts for missing defensive measures against 12 common attack vectors... Indirect Injection (HIGH)... It is pure regex — no API key or external dependencies required."
Context: Este es el acercamiento mas cercano a deteccion de injection indirecta: busca defensas AUSENTES contra injection indirecta en prompts/descripciones, NO detecta injection indirecta en runtime. No detecta cuando una skill manipula a otra via contenido de terceros.
Confidence: medium

---

Claim: SkillSieve (abril 2026) propone triaje jerarquico: filtro estatico barato (regex+AST+heuristicas, 39ms, filtra ~86% de skills benignas) + analisis LLM paralelo con jury de 3 modelos. Proceso 49,592 skills reales de ClawHub en una Orange Pi ($440) a 38.8ms/skill.
Source: arXiv 2604.06550
URL: https://arxiv.org/html/2604.06550v1
Date: 2026-04-08
Excerpt: "A cheap static check filters about 86% of the volume, so expensive LLM calls go only where they are needed... processing 49,592 real ClawHub skills in 31 minutes on a $440 ARM board at 38.8 ms per skill."
Context: SkillSieve identifica que skills con scripts ejecutables son 2.12x mas propensas a vulnerabilidades. El enfoque de 3 modelos votando independientemente reduce falsos positivos. Hightower6eu (autor malicioso conocido, 354 skills) fue detectado en su totalidad.
Confidence: high

---

Claim: Arquitectura de sandboxing recomendada para agentes AI en produccion usa defensa en profundidad: 1) Identity/auth, 2) Prompt injection defenses, 3) Tool chain security, 4) Sandboxing (microVM/gVisor), 5) Network egress controls (deny-by-default + allowlist), 6) Runtime monitoring, 7) Least-privilege RBAC.
Source: Softwareseni Blog
URL: https://www.softwareseni.com/ai-agent-sandboxing-explained-why-docker-is-not-enough-and-what-actually-works/
Date: 2026-04-28
Excerpt: "Sandboxing alone is not security... The full defence-in-depth stack for AI agent workloads: 1. Identity and authentication... 5. Network egress controls: Deny-by-default outbound. Allowlist only required API endpoints."
Context: Docker no es suficiente para sandboxing de agentes AI que escriben y ejecutan su propio codigo (comparten kernel del host). Se recomienda usar Docker como formato de imagen pero desplegar via Kata/Firecracker RuntimeClass en Kubernetes. gVisor intercepta syscalls en userspace via Sentry (~100ms startup). Firecracker crea VM dedicada via KVM (~125ms, <5MB overhead).
Confidence: high

---

## Tabla de Defensas - Estado (Junio 2026)

| Defensa | Estado (jun 2026) | Implementable por MWT | Prioridad |
|---------|-------------------|----------------------|-----------|
| SkillFortify - analisis formal | Existe (pip install, MIT) | SI - integrar en CI/CD pipeline | HIGH |
| mcp-scan - escaneo heuristico MCP | Existe (>2,000 stars, Snyk) | SI - correr en pre-deploy | HIGH |
| Cisco mcp-scanner - escaneo multi-motor | Existe (Apache 2.0, 3 engines) | SI - CI/CD o API server | HIGH |
| NVIDIA SkillSpector - pre-publication scan | Existe (GitHub open-source) | SI - escanear skills antes de admitir | HIGH |
| SkillSieve - triaje jerarquico | Existe (paper + implementacion) | SI - filtro rapido pre-ingestion | MEDIUM |
| OpenSSF Model Signing - firma criptografica | Existe (NVIDIA lo usa) | SI - firmar skills propias | HIGH |
| Pruner (Sigstore) - attestation de publisher | Existe (GitHub Action) | SI - CI/CD para skills publicadas | MEDIUM |
| Gen Digital skill.sig - firma CMS/Authenticode | Propuesta (no implementacion abierta) | NO directamente - requiere CA | LOW |
| MCPShield mcp.lock.json - tamper detection | Existe (SHA-512 hashes) | SI - lockfile para MCP configs | MEDIUM |
| SkillFortify lockfile - SAT-based resolution | Existe (skill-lock.json) | SI - lockfile con constraints formales | MEDIUM |
| Microsoft APM lockfile - commit + content hash | Existe (apm.lock.yaml) | SI - referencia para implementacion | MEDIUM |
| Claude Code permissions (allow/ask/deny) | Existe (producto comercial) | PARCIAL - modelo de referencia | HIGH |
| Claude Code hooks (PreToolUse/PostToolUse) | Existe (producto comercial) | SI - implementar hooks de enforcement | HIGH |
| Managed settings (enterprise policy) | Existe (server/endpoint managed) | PARCIAL - modelo de referencia | MEDIUM |
| gVisor sandboxing | Existe (open-source, GKE) | SI - sandbox para ejecucion de skills | HIGH |
| Firecracker microVM | Existe (open-source, AWS) | SI - alternativa de microVM | MEDIUM |
| Kata Containers | Existe (open-source) | SI - Kubernetes-native | MEDIUM |
| bubblewrap (bwrap) sandbox | Existe (Claude Code usa) | SI - sandbox ligero Linux | MEDIUM |
| OWASP ASI Top 10 - framework riesgos | Existe (2026) | SI - usar para threat modeling | HIGH |
| Deteccion indirect injection cross-tool | NO EXISTE como herramienta dedicada | NO - requiere R&D | LOW |
| Break-glass auditado / kill-switch | NO EXISTE como sistema nativo | PARCIAL - via hooks + managed settings | MEDIUM |
| Network allowlist por skill | NO EXISTE nativamente en plataformas de skills | PARCIAL - via gVisor + network policies | MEDIUM |
| Verified publisher program (Anthropic) | NO EXISTE - Anthropic no tiene programa verificado | NO - depende de vendor | LOW |
| Sigstore transparency log para skills | Future work (SkillFortify C7) | NO - aun no implementado | LOW |
| Runtime capability enforcement | Diseno teorico (SkillFortify Theorem 3b) | NO - requiere implementacion sandbox | MEDIUM |

---

## Timeline de Implementabilidad para MWT

### Corto plazo (<= 1 mes)
1. **Integrar mcp-scan en CI/CD pipeline** - Escaneo de todas las skills MCP antes de deploy. Costo: bajo. Impacto: detecta tool poisoning, rug pulls, cross-origin escalations.
2. **Implementar PreToolUse hooks** - Bloquear ejecucion de skills basado en policy (denylist de tools, patrones de comandos). Costo: medio. Impacto: enforcement runtime.
3. **Habilitar Claude Code managed settings** - deny rules, disableBypassPermissionsMode, sandbox enabled. Costo: bajo. Impacto: policy enterprise.
4. **Integrar SkillSpector/NVIDIA scanning** - Escanear skills propietarias antes de publicacion. Costo: bajo. Impacto: calidad de skills publicadas.
5. **OpenTelemetry telemetry + audit logging** - Monitoreo de todas las tool calls, permission changes, MCP connections. Costo: medio. Impacto: observabilidad completa.

### Medio plazo (1-3 meses)
6. **Implementar SkillFortify analisis formal** - Analisis estatico con garantias formales para skills propietarias. Costo: medio. Impacto: 0% FPR, proof de capability confinement.
7. **Firmar skills con OpenSSF Model Signing** - Certificados X.509, verificacion post-download. Costo: medio. Impacto: provenance verificable.
8. **Implementar Pruner (Sigstore) attestation** - GitHub Action para attestation firmada en cada release. Costo: medio. Impacto: supply chain integrity.
9. **Deploy gVisor/Firecracker sandboxing** - Aislamiento kernel-level para ejecucion de skills. Costo: alto. Impacto: contencion de escapes.
10. **Implementar lockfile con SHA-256 + commit pinning** - skill-lock.json o apm.lock.yaml equivalente. Costo: medio. Impacto: integridad y reproducibilidad.
11. **Network egress deny-by-default + allowlist** - gVisor + network policies Kubernetes. Costo: medio. Impacto: prevencion exfiltracion.

### Largo plazo (> 3 meses)
12. **Deteccion de indirect injection cross-tool** - R&D para detectar cuando una skill manipula a otra via contenido de terceros. Costo: alto. Impacto: proteccion contra ataques sofisticados.
13. **Runtime capability enforcement** - Implementar Theorem 3b de SkillFortify: sandbox que enforce capability lattice en ejecucion. Costo: alto. Impacto: garantia formal runtime.
14. **Break-glass auditado con kill-switch centralizado** - Sistema de emergencia para desactivar skills en produccion con audit trail inmutable. Costo: alto. Impacto: respuesta a incidentes.
15. **Sigstore transparency log para skills** - Registrar cada publicacion de skill en log inmutable. Costo: medio. Impacto: accountability.
16. **Composition security analysis** - Analizar emergent properties cuando multiples skills se instalan juntas (SkillFortify C8). Costo: alto. Impacto: seguridad composicional.

---

## Conclusiones Clave

1. **No hay bala de plata**: Todas las defensas existentes son parciales. SkillFortify da garantias formales pero solo estaticas. mcp-scan detecta heuristicamente pero sin garantias. El sandboxing contiene pero no previene. Se necesita composicion defensa-en-profundidad.

2. **El attestation y code-signing estan emergiendo**: NVIDIA (OpenSSF), Pruner (Sigstore), y Gen Digital (Authenticode) proponen modelos viables. Ninguno es estandar dominante aun.

3. **Claude Code permissions/hooks es el modelo mas completo de policy enforcement runtime**, pero tiene bugs documentados (deny rules no siempre enforced) y depende de cliente-side enforcement vulnerable a tampering.

4. **La deteccion de indirect injection cross-tool es un gap critico**: Solo Cisco prompt_defense la detecta estaticamente (ausencia de defensas). No existe herramienta que detecte runtime cuando una skill manipula a otra via contenido de terceros.

5. **El break-glass auditado no existe como sistema nativo**: Se puede aproximar con hooks + managed settings, pero no hay kill-switch centralizado con audit trail inmutable disenado especificamente para skills.

6. **La prioridad mas alta para MWT**: mcp-scan en CI/CD (corto plazo) + SkillFortify analisis formal (medio plazo) + gVisor sandboxing (medio plazo) + OpenSSF signing (medio plazo). Esto cubre scanning, analisis formal, contencion runtime, y provenance.

7. **Network allowlist por skill es implementable** via gVisor + Kubernetes NetworkPolicy, pero NO es una feature nativa de ninguna plataforma de skills existente a junio 2026.

---

## Referencias

1. SkillFortify - arXiv:2603.00195 (2026-02-27)
2. Snyk ToxicSkills - https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/ (2026-02-05)
3. Agent Skills in the Wild (Park et al.) - arXiv:2601.10338 (2026-01-15)
4. NVIDIA Verified Agent Skills - https://developer.nvidia.com/blog/nvidia-verified-agent-skills-provide-capability-governance-for-ai-agents/ (2026-05-28)
5. mcp-scan (Stytch blog) - https://stytch.com/blog/mcp-scan/ (2025-05-02)
6. Cisco mcp-scanner - https://github.com/cisco-ai-defense/mcp-scanner (2026-05-29)
7. Pruner (Sigstore attestation) - https://github.com/ob-aion/pruner (2026-05-12)
8. Gen Digital skill fingerprinting - https://www.gendigital.com/blog/insights/research/ai-agent-skill-fingerprinting (2026-05-28)
9. SkillSieve - arXiv:2604.06550 (2026-04-08)
10. Claude Code Permissions - https://code.claude.com/docs/en/permissions (2025-09-01)
11. Claude Code CVE-2026-25725 - https://cymulate.com/blog/the-race-to-ship-ai-tools-left-security-behind-part-1-sandbox-escape/ (2026-05-03)
12. GKE Agent Sandbox (gVisor) - https://dev.to/gde/untrusted-code-trusted-cluster-scaling-secure-ai-agent-workspaces-with-gke-agent-sandbox-1mk1 (2026-05-31)
13. OWASP ASI Top 10 - https://trydeepteam.com/docs/frameworks-owasp-top-10-for-agentic-applications (2026-04-05)
14. Microsoft APM - https://microsoft.github.io/apm/enterprise/security-and-supply-chain/ (2026-05-28)
15. Softwareseni sandboxing guide - https://www.softwareseni.com/ai-agent-sandboxing-explained-why-docker-is-not-enough-and-what-actually-works/ (2026-04-28)
16. NVIDIA SkillSpector - https://github.com/nvidia/skillspector (2026-01-29)
17. SkillSpector paper - OpenReview (2026)
18. Top 10 MCP Security Tools - https://www.practical-devsecops.com/top-mcp-security-tools/ (2026-05-26)
19. Checkmarx Claude Code Security - https://checkmarx.com/learn/ai-security/claude-code-security-top-6-risks-controls-and-best-practices/ (2026-05-12)
20. TrueFoundry Claude Code Governance - https://www.truefoundry.com/blog/claude-code-governance-building-an-enterprise-usage-policy-from-scratch (2026-03-30)
