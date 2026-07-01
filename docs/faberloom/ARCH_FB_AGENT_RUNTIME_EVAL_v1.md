---
id: ARCH_FB_AGENT_RUNTIME_EVAL
version: 1.0.0
status: draft
visibility: [INTERNAL]
domain: faberloom
type: arch
stamp: DRAFT 2026-06-17 - integrado de HANDOFF_AGENT_RUNTIME_EVAL - bajo PAUSAR-Y-VALIDAR
fecha: 2026-06-17
agente: Claude (Cowork) - Arquitecto Ejecutor
fuente: HANDOFF_AGENT_RUNTIME_EVAL.md + swarm AOSS-2026-06-17 (F1) + AOSS-F2-2026-06-17 (F2)
relacionado_con:
  - SPEC_FB_BUILD_SEQUENCE_v3 (gate E2; pausa)
  - SPEC_SPACELOOM_SELFHOSTED_v1.1 (lo unico adoptable ahora cruza aca)
  - ENT_RESEARCH_FABERLOOM_KIMI_2026-04
  - IDX_FB_FOUNDATION_BETA
---

# ARCH_FB_AGENT_RUNTIME_EVAL
## Evaluacion de runtimes de agentes open-source + modelo de agente por tenant

> **PISO DE GOBERNANZA:** este documento es CONOCIMIENTO/DECISION, no adopcion de infra. FaberLoom
> sigue en PAUSAR-Y-VALIDAR (eval 2026-06-09): SaaS multi-tenant en pausa, SPEC freeze hasta cierre E2,
> portfolio b>a>c. Nada aca levanta la pausa. Decisiones = propuestas a ratificar por el CEO.

## 1. Modelo arquitectonico (agente por tenant, memoria sellada)

Patron objetivo (para el FaberLoom multi-tenant, cuando salga de pausa): un agente-entidad por tenant,
personalidad estable, que opera en espacios encapsulados sin contaminarse entre contextos.

1. **Identidad transversal e INMUTABLE.** La personalidad viaja entre espacios pero es read-only en sesion. Si el agente reescribe su identidad con lo aprendido en un espacio, se vuelve canal de fuga al siguiente.
2. **Indice global vs contenido sellado.** El agente sabe QUE existe y DONDE (punteros/metadata, equivalente a un router IDX_), pero el CONTENIDO queda sellado al espacio. Saber-que vs saber-que.
3. **Memoria sellada por contexto.** Aislamiento CRIPTOGRAFICO/de plataforma, no por instruccion. Dos ejes: espacial (workspace) y temporal (memoria entre corridas; un agente vivo persistente se enajena si la memoria no esta namespaced por tenant y por dominio/visibilidad).
4. **Llave graduada por politica.** Tres posiciones: cerrada / indice abierto (default sano: responde "donde", no "que") / contenido abierto (alto riesgo). La controla el owner del tenant, versionada y auditada; el agente nunca tiene la llave. Apertura = consulta MEDIADA por broker, no acceso directo. PISO: CEO-ONLY y FROZEN no cruzan a menor visibilidad aunque se abra la llave.
5. **Loop de vida.** La "sensacion de vida" es efecto del harness (persistencia + identidad + memoria episodica + reactividad + PROACTIVIDAD), no del modelo. La proactividad cruza el umbral herramienta->vivo. Para seguridad se trata como software determinista. Tradeoff: mas vida = menos control; dosificar por visibilidad (max en comercial repetitivo, efimero en CEO-ONLY/FROZEN).
6. **Meta-agente curador.** Puede crear agentes/rutinas y afinar skills DENTRO del plano de ejecucion (sandbox: proponer, iterar, evals), pero la PROMOCION a canonico y todo toque a control_surface exige gate humano / break-glass auditado. Propone, no dispone. Riesgos: deriva acumulativa (sanidad+changelog+rollback) y herencia del sello (no puede crear hijos exentos).
7. **Particion embebido vs gobierno** (regla de decision): la linea es "invocable vs inviolable".
   - Procesos deterministas que el agente invoca cuando razona que toca -> EMBEBER como skill/tool.
   - Gate de acciones irreversibles (NEVER), disparadores que deben correr aunque el agente falle, y log inmutable -> FUERA del agente, en un plano que no alcanza (n8n u otro).
   El no-determinismo no esta en el proceso embebido (una funcion no alucina) sino en la INVOCACION (el LLM decide si/cuando/como llamarla, y puede ser inducido a saltarsela).

## 2. Veredicto del swarm (frameworks open-source)

Frameworks: Hermes Agent, OpenClaw, LangGraph, CrewAI, OpenHands, Letta, Agno. Fuente: swarm_output/.

1. **NINGUN framework da aislamiento multi-tenant hostil de fabrica.** El paper SMTA: 92% de defensa cross-tenant requiere Container/VM isolation + RBAC+ABAC + namespace isolation. Ninguno cumple por defecto. Confirma: el sello es capa propia, no del framework.
2. **SKILL.md (YAML frontmatter) es el estandar portable.** OpenHands, Hermes, OpenClaw lo usan (formato AgentSkills abierto). Las SKILL_ de la KB mapean directo; MWT ya esta parado ahi (Claude Code/Cowork).
3. **n8n no se elimina, se reduce.** Ninguno tiene integracion n8n nativa; su orquestacion (cron/standing orders) corre DENTRO del agente, justo donde no debe vivir el gate. n8n queda para la franja inviolable/auditable.
4. **Marketplaces = veneno.** 36.82% de skills con flaws, 13.4% criticas, 76 con payloads maliciosos. No instalar skills de comunidad sin auditar.
5. **Kimi Work/Claw parcialmente replicable.** Replicable: SKILL.md, ClawHub (API abierta), MCP, SDK thin. NO: K2.5/2.6, app Kimi Work, swarm de 300, Kimi Business multi-tenant ($599/seat/ano), infra Alibaba MicroVM. Control plane unico Work+Claw = [NO-VERIFICADO].

### Tabla de candidatos (interpretacion MWT)

| Framework | Veredicto MWT | Razon corta |
|---|---|---|
| OpenHands | A vigilar (top realista) | Building blocks mas completos (Docker per-conversation, SecretRegistry, sub-agentes, REST API, SDK Python). Core MIT, nube Polyform (no-OSS). Multi-tenant se construye encima. Self-host 4/5 |
| Agno | Descartar multi-tenant | RBAC JWT opt-in, facil deploy (3/5) pero 3 IDORs cross-tenant + unsafe exec() + FAIL 73/100 |
| OpenClaw | Referencia de diseno, no SDK | Mejor aislamiento declarativo (allowlist JSON5, workspace per-agente, Kustomize) pero Markdown-driven, no SDK. 25+ CVEs (una CVSS 9.9) |
| Hermes | No aplica | App standalone, no framework. Issue #34352: memoria bypassa hooks; aislamiento imposible sin forkear core |
| LangGraph / CrewAI / Letta | Fuera | LangGraph aisla solo por thread; CrewAI y Letta sin aislamiento robusto |

## 3. Decisiones propuestas (PENDIENTES de ratificacion CEO)

1. **No adoptar ningun harness como infraestructura ahora.** Respeta la pausa.
2. **Estandarizar skills del slice F1-F2 en SKILL.md.** Unica accion adoptable ya, bajo riesgo, sin dependencia nueva. Portable entre runtimes. **Cruza al build self-embedded:** SpaceLoom debe usar SKILL.md (YAML frontmatter), no un markdown propio (ver SPEC_SPACELOOM_SELFHOSTED_v1.1 sec 5).
3. **n8n (o equivalente) reducido al plano de gobierno:** gate NEVER, disparadores criticos, log inmutable. Resto de deterministas embebidos como skills.
4. **OpenHands en lista "re-evaluar al cierre de E2"** como candidato self-host, con aislamiento multi-tenant como capa propia (Container/VM + RBAC+ABAC + namespace), no del framework.
5. El modelo de seccion 1 es el blueprint del FaberLoom multi-tenant cuando salga de pausa; no se construye antes.

## 4. Ruta a infraestructura (fases + gates)

| Fase | Que | Gate |
|---|---|---|
| Investigar | swarm OSS (HECHO, este doc) | veredicto + candidatos documentados |
| Destilar | este ARCH_ + ratificacion CEO | CEO ratifica decisiones sec 3 |
| Construir slice | skills F1-F2 en SKILL.md (Claude Code), plano de gobierno minimo | slice corre con skills portables + gate NEVER fuera del agente |
| Desplegar | infra propia self-host (candidato OpenHands) **solo al cierre de E2** | aislamiento multi-tenant verificado (>=92% SMTA) ANTES de cualquier tenant externo |

Cada salto requiere cierre del gate anterior. El multi-tenant no se despliega sin el umbral de aislamiento.

## 5. [NO-VERIFICADO] (validar antes de usar como hecho)

- Control plane unico que unifique Kimi Work + Kimi Claw (Moonshot no lo documenta).
- Cifras de mercado/CVE citadas por el swarm (verificacion independiente pendiente).
- Umbral SMTA 92% como aplicable 1:1 a la arquitectura MWT (paper externo, contexto distinto).

## 6. Accion de seguridad URGENTE (operativa, no parte del ARCH_)

Credenciales IMAP entregadas a Kimi Work (2026-06-17): **rotar/revocar de inmediato**; asumir que Moonshot las tiene. Para acceso de agentes a correo: OAuth scoped read-only sobre carpeta especifica, NO IMAP full-mailbox. Nada CEO-ONLY accesible por esa cuenta. **Confirmar con Alvaro si ya se ejecuto.**

## 7. Abierto / a decidir

- Ratificacion CEO de las decisiones sec 3.
- Si el slice F1-F2 adopta SKILL.md ya o espera.
- Mecanismo del plano de gobierno (n8n vs cron+validador) - depende del cierre de E2.
- Self-host de OpenHands en detalle - diferido a cierre de E2.
- Si los prompts de research (PROMPT_RESEARCH_AGENTS_OSS) se indexan junto a los PROMPT_KIMI_SWARM_*.

## 8. Relacion con SpaceLoom self-embedded (NUEVO - reconciliacion)

Este ARCH_ es del mundo **FaberLoom multi-tenant (PAUSADO)**. SpaceLoom self-embedded (SPEC_SPACELOOM_SELFHOSTED_v1.1) es **single-user, local-first, sin multi-tenant**. La mayoria de este modelo (sello criptografico, llave graduada, meta-agente, aislamiento cross-tenant) NO aplica al build self-embedded actual y NO debe re-inflarlo. Lo unico que cruza ahora:
- **SKILL.md como formato de skills** (refuerza SPEC_SPACELOOM sec 5).
- **Sandbox de skills / marketplaces = veneno** (refuerza SPEC_SPACELOOM sec 7: skills nunca como codigo, allowlist, no community sin auditar).
- **OpenHands** = candidato de runtime SOLO si SpaceLoom alguna vez necesita ejecucion de tools sandboxed (hoy PROHIBIDA). No ahora.

## 9. Changelog

- v1.0.0 (2026-06-17): integrado de HANDOFF_AGENT_RUNTIME_EVAL. Modelo de agente por tenant + veredicto swarm OSS (7 frameworks) + tabla candidatos + decisiones propuestas + ruta a infra + NO-VERIFICADO + accion de seguridad IMAP + reconciliacion con SpaceLoom self-embedded. Bajo PAUSAR-Y-VALIDAR; decisiones a ratificar por CEO. No toca FROZEN ni control_surface.
