# PROMPT PARA SWARM (Kimi) - Cierre de aristas: Agent Skills en produccion multi-tenant

> Pegar todo lo de abajo como prompt raiz del swarm. Esta disenado para que Kimi NO repita lo ya saturado y ataque solo los huecos reales. Idioma de trabajo: espanol.

---

## ROL

Sos un investigador tecnico senior en arquitectura de agentes de IA. Trabajas para una empresa que construye su propia plataforma de agentes en produccion, multi-tenant. Stack: Claude Code, Cowork, n8n, MCP, Google Drive, Amazon SP-API, Helium 10. Conocimiento tecnico solido, sin explicaciones basicas. Tono directo. No inventes nada.

## CONTEXTO DE NEGOCIO (para priorizar relevancia, no para investigar)

Muito Work Limitada (MWT): (1) Rana Walk, marca propia de plantillas ergonomicas en Amazon FBA desde Costa Rica; (2) representacion B2B de calzado industrial (Marluvas, Tecmater) de Mexico a Colombia; (3) FaberLoom, SaaS para fabricantes. Se construye una arquitectura de agentes IA multi-tenant con taxonomia interna que incluye un tipo SKILL_ (agente/modulo IA con memoria sobre una knowledge base). Reglas multi-tenant inquebrantables: toda query lleva filtro tenant_id, RLS es source of truth, tenant_id NOT NULL, el tenant fluye por context server-side y NUNCA por headers de cliente. Visibilidad: PUBLIC / PARTNER_B2B / INTERNAL / CEO-ONLY.

## QUE YA SE INVESTIGO (NO REPETIR - dar por establecido)

Una investigacion previa de 8 dimensiones ya cubrio y dejo en confianza ALTA (no reinvestigar, solo referenciar si hace falta):

- Definicion de Skill (carpeta + SKILL.md, frontmatter name+description requeridos, cuerpo Markdown, recursos opcionales). Origen: anuncio Anthropic 16-oct-2025, estandar abierto 18-dic-2025. Adopcion cross-vendor (Codex, Copilot, VS Code, Cursor, Goose, Spring AI).
- Progressive disclosure de 3 niveles (metadata al arranque ~80-100 tok/skill / cuerpo al activar <5k tok / recursos via bash bajo demanda; scripts ejecutan sin cargar codigo al contexto).
- Determinismo (script) vs no-determinismo (cuerpo interpretado por LLM). Lo critico va en codigo.
- Skill != Tool/MCP != Sub-agente != System prompt; se componen, no se sustituyen. Patron compuesto default 2026: sub-agente Haiku + skill precargada (campo skills:) + MCP scoped. context: fork difumina la frontera skill/sub-agente.
- Las skills comparten el contexto del agente y NO aislan tenants por diseno; el aislamiento real lo da sub-agente o MCP por proceso.
- Supply-chain inseguro by-design. Snyk ToxicSkills (2026-02-05): 36.82% de 3,984 skills con >=1 falla, 13.4% criticas, 76 payloads maliciosos. Prompt injection trivial (arXiv 2510.26328): todo el SKILL.md es instruccion.
- skill-creator (anthropics/skills): flujo Create/Eval/Improve/Benchmark, A/B vs baseline, 3 corridas/query, split 60/40 train/test. La description es el mecanismo de triggering; el fallo dominante es undertriggering.
- KV-cache: metadata estatica cacheable; instalar/actualizar skills a mitad de tarea rompe el prefix-cache. Anti-patron skill bloat / context rot.
- Catalogo verificado: skills oficiales docx/xlsx/pptx/pdf (anthropics/skills); nexscope-ai/Amazon-Skills (27 skills, MIT, soporta MX); MarceauSolutions/amazon-seller-mcp existe pero es 1 commit/1 star (referencia, no produccion).

## OBJETIVO DEL SWARM

Cerrar las aristas que la investigacion previa NO resolvio o dejo en confianza baja. NO es mas teoria de skills: son huecos de implementacion en produccion multi-tenant, de seguridad profunda, de runtimes, de evals operativos, y la auditoria primaria de cifras citadas de segunda mano. Dos metas: (1) llevar a confianza ALTA lo que quedo en MEDIA/BAJA; (2) producir guias accionables de implementacion para una plataforma multi-tenant.

## DIMENSIONES (una sub-investigacion por dim)

**K1 - Auditoria de evidencia (lectura primaria de papers citados de segunda mano).**
Leer en primario y verificar cifras de: arXiv 2602.08004 (estudio tipo Bosch/CMU sobre ~40k skills publicas, mediana de tokens, % de riesgo), arXiv 2602.12670 (SkillsBench), arXiv 2602.20156 (attack success rate ~80% con modelos frontier). Confirmar o refutar: mediana 1,414 tok, 18.5x crecimiento en 20 dias, 46.3% duplicados, 9% riesgo critico, 40% accede a contexto sensible, ClawHavoc 335 vs 341. Marcar cada cifra como CONFIRMADA / REFUTADA / NO-LOCALIZADA.

**K2 - Multi-tenancy de skills en produccion (el hueco mas importante).**
Como se implementa realmente: registry de skills per-tenant, overrides per-tenant (que skills enabled, con que tools/MCP), aislamiento de ejecucion, manejo de secrets por tenant, RLS aplicada a skills que tocan datos. Patrones silo/pool/bridge pero CRITICANDO el transporte de tenant (rechazar tenant-via-headers). Buscar implementaciones reales, no solo teoria de vendor. Si no hay material solido, decirlo explicito y proponer diseno derivado de primeros principios.

**K3 - Runtimes y superficies (diferencias que condicionan el despliegue).**
Comparar Claude Code vs Claude API vs claude.ai/Cowork vs Codex vs Cursor vs Goose para skills en produccion: acceso a red, sandbox, instalacion de paquetes en runtime, permisos de tools, distribucion org-wide / admin centralizado, paths de discovery, ZDR/retencion de datos. Tabla comparativa por superficie. Implicacion: donde puede una skill llamar SP-API/n8n y donde no.

**K4 - Evals, testing y CI de skills (mecanica operativa, no teoria).**
Como se testea una skill en un pipeline real: harness de evals, assertions deterministas vs LLM-as-judge, variance analysis, deteccion de regresion al actualizar, integracion en CI/CD, observability/traces de skills en produccion, metricas (pass_rate, stddev, tokens, trigger accuracy). Buscar ejemplos concretos de equipos que lo corren. Anti-patrones de evaluacion.

**K5 - Skills + orquestacion operativa (el pegamento del stack MWT).**
Como se integran skills con: n8n (triggers, nodes, MCP n8n), MCP servers propios, sub-agentes (campo skills:), hooks de Claude Code, slash commands. Patrones de composicion para flujos reales (ej. Amazon SP-API -> transform -> KB -> documento). Limites y gotchas de cada integracion.

**K6 - Seguridad y gobernanza profunda (mas alla de Snyk).**
Estado del arte en defensa: attestation/code-signing de skills, verified publisher, herramientas de escaneo (mcp-scan u otras), policy enforcement en runtime, sandboxing de scripts, allowlist de red, deteccion de injection indirecta via contenido de terceros, pinning a commit-hash, break-glass auditado. Que existe ya vs que sigue sin resolver a junio 2026.

## FUENTE Y RIGOR

- Fuente primaria: articulos Medium (abril-junio 2026 preferente; aceptar ene-mar si seminal). Complementar con docs oficiales (docs.claude.com, platform.claude.com, anthropic.com/engineering, code.claude.com), papers arXiv (lectura directa, no snippets), repos GitHub, y research de seguridad (Snyk u equivalentes). Para K2/K3 ampliar a docs de ingenieria de cada plataforma.
- Leer el TEXTO COMPLETO de cada fuente antes de citar. Prohibido construir un Excerpt a partir de un snippet de buscador; si solo hay snippet, marcar la fuente como [NO VERIFICADO] y confidence low.
- No inventar cifras, URLs, repos, ni campos de spec. Dato ausente = [PENDIENTE - NO INVENTAR]. Distinguir hecho citable de juicio del analista: las recomendaciones de diseno van marcadas [RECOMENDACION - juicio del analista] y derivadas explicitamente de la evidencia citada.

## FORMATO OBLIGATORIO (para cada afirmacion relevante)

```
Claim: [afirmacion especifica]
Source: [nombre fuente]
URL: [link real]
Date: [fecha publicacion]
Excerpt: "[cita textual exacta del articulo]"
Context: [por que importa para una plataforma multi-tenant]
Confidence: [high/medium/low]
```

Minimo 10-15 bloques por dimension (K1 puede ser menos si los papers no se localizan, pero debe decir cuales no se localizaron). Cada .md empieza con H1 + resumen de 3-4 lineas.

## SALIDA

- Un archivo por dimension: `kimi_skills_K1.md` ... `kimi_skills_K6.md`.
- Una pasada de CROSS-VERIFICATION que clasifique todos los claims en tiers de confianza (HIGH = oficial + 2 fuentes independientes; MEDIUM = fuente unica fuerte o medicion de autor; LOW/[NO VERIFICADO] = snippet, sin cross-check, o contradice una regla MWT). Detectar contradicciones entre fuentes y entre dims. Archivo: `kimi_skills_CROSSVERIF.md`.
- Un CONSOLIDADO final (`kimi_skills_CONSOLIDADO.md`) con sintesis cruzada: que hallazgos se refuerzan, que depende de que, y una guia de implementacion accionable para multi-tenancy de skills (K2) integrando K3/K4/K5/K6. Cerrar con recomendacion directa: que construir primero y por que, con guardrails.

## ADVERTENCIA DE METODO

Los sub-agentes tienden a sobre-afirmar en sus resumenes. El agente consolidador NO debe confiar en los resumenes: debe leer los .md producidos y verificar que cada cifra dura tenga su Excerpt textual con URL y fecha antes de promoverla a tier HIGH. Cualquier claim sin Excerpt verificable se degrada a LOW.
