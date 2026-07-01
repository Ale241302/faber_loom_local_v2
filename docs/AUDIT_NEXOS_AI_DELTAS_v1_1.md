---
id: AUDIT_NEXOS_AI_DELTAS_v1_1
version: 1.1
status: DRAFT
visibility: [INTERNAL]
domain: ARQUITECTURA_FUNDACIONAL
type: AUDIT
date: 2026-05-17
source: revision profunda KB FaberLoom (69 archivos docs/faberloom/) post AUDIT v1.0
extiende: AUDIT_NEXOS_AI_DELTAS_v1.md
related:
  - AUDIT_NEXOS_AI_DELTAS_v1
  - ARCH_NEXOS_SIMPLIFICATION_PRINCIPLES_v1
  - IDX_FB_FOUNDATION_BETA
  - SPEC_FB_AGENT_BUILDER_v1 (v2.0)
  - SCH_FB_FLOW_DAG (v2.0)
  - SCH_FB_SKILL_MANIFEST_v2
  - ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1 (P16)
  - ENT_FB_SUB_AGENTS_LIBRARY_v1
  - SPEC_FB_KNOWLEDGE_RIVER_v1 (v1.1)
  - POL_FABERLOOM_SURFACE_CONTRACT (v0.1 DRAFT)
  - SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1
---

# AUDIT_NEXOS_AI_DELTAS_v1.1 - Rectificacion post revision profunda KB FaberLoom

## 0. Proposito

Este doc rectifica AUDIT_NEXOS_AI_DELTAS_v1.0 (indexado 2026-05-17 commit d3575c7) tras revision profunda de la KB FaberLoom canonica (69 docs/faberloom/). El v1.0 fue redactado sin consultar el canon FB existente y propuso deltas que ahora se detectan **redundantes, contradictorios o invalidos** contra specs VIGENTES.

Politica MWT append-only respetada: el v1.0 NO se edita ni se borra. Este v1.1 documenta el reanalisis y propone status revisado para cada delta. La decision CEO final sobre que promover/descartar se documenta en futuro BATCH.

## 1. Hallazgos del reanalisis - que cambia en mi modelo mental

Cinco correcciones criticas al modelo que tenia el v1.0:

| Lo que el v1.0 decia | Lo que dice el canon FB |
|---|---|
| 3-boton = "Aprobar / Iterar / Rechazar" | **"Aprobar / Descartar / Iterar en Workspace"** (POL_FABERLOOM_SURFACE_CONTRACT seccion3.6 ActionFooter governance). La iteracion manda al user al Workspace, no es loop in-place. |
| Creacion de agente "chat-first" propuesto | **Agent Factory wizard 4 pasos** firmado en TIER1 #15 (plan v1.3.1-FIRMADO 2026-05-01) |
| Capabilities = Web search / Knowledge base como toggles user-facing | Los 15 tools del catalogo (`ENT_FB_TOOL_CATALOG_v1`) estan **BLOQUEADOS en runtime de skill E1**. Existen como MCP wrappers, solo invocables desde flow nodes especificos. Habilitables E2 con `feature_flag.allow_tools_in_skills` |
| Modelo selector user-facing | Backend SkillSpec con modelo declarado. v1 = Sonnet 4.6 + Haiku 4.5 via LiteLLM. NO hay user-facing selector |
| Sub-agentes "prohibidos" segun TIER1 | P16 (ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1) define 10 sub-agentes canonicos. En E1 son standalone individuales. Composicion jerarquica habilitable E2 con feature flag. Reconciliacion en SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 |

## 2. Status revisado de los 5 deltas D1-D5 del v1.0

### D1 - POL_GROUNDING_POLICY_v1

**Status original v1.0:** NEW - ADOPTAR
**Status revisado v1.1:** **SCOPE_ACOTADO - revisar antes de promover**

**Por que cambia:** la idea de 5 presets (Grounded/Guided/Balanced/Analytical/Creative) **choca con HITL absoluto + P3 draft-first + Voice Humanizer v2** ya VIGENTE. Los agentes operativos en FB v1 son siempre HITL + KB-grounded por arquitectura - no hay espectro de "creatividad" expuesto al usuario.

**Donde si podria aplicar:** dentro del **GlobalChatTrigger ("Ask F\*")** que abre el Workspace/SpaceLoom (= mecanica universal de iteracion libre, fuera del runtime de agentes productivos). Ahi el user **si** puede pedir explorar/iterar con la IA fuera del grounding estricto de un agente.

**Recomendacion:** acotar D1 a "preset de iteracion para el GlobalChatTrigger del Workspace cuando se invoca sin agent activo". Renombrar a `POL_FB_WORKSPACE_ITERATION_MODE_v1`. Validar contra `SPEC_FB_KNOWLEDGE_RIVER_v1` v1.1 modelo 2 capas para evitar que un preset Creative permita leak de L4 indexed.

### D2 - SPEC_AGENT_BUNDLE_v1

**Status original v1.0:** NEW - ADOPTAR
**Status revisado v1.1:** **REDUNDANTE - descartar**

**Por que cambia:** ya existe `SCH_FB_SKILL_MANIFEST_v2.md` con shape canonico + 19 decisiones consolidadas en `SPEC_FB_AGENT_BUILDER_v1.md` v2.0 VIGENTE (D1-D19). Mi propuesta de "model_primary per-agente" contradice D8 (modelo unico vIa LiteLLM) y D17 (procesos embebidos, configuracion en data). Los campos que propuse ya existen o estan deliberadamente diferidos.

**Recomendacion:** descartar D2. Si surge una pregunta sobre shape de agente, referenciar `SCH_FB_SKILL_MANIFEST_v2` y `SPEC_FB_AGENT_BUILDER_v1` v2.0.

### D3 - SPEC_AGENT_FLOW_v1

**Status original v1.0:** NEW - ADOPTAR
**Status revisado v1.1:** **REDUNDANTE - descartar**

**Por que cambia:** ya existe `SCH_FB_FLOW_DAG.md` v2.0 con **7 tipos de nodo canonicos** (skill_call, branch, parallel, terminal, notify, human_gate, config_resolver). Mi propuesta era inferior a lo que ya esta documentado: el SCH canon tiene branching declarativo (que yo proponia como innovacion), parallel fork-join, human_gate con timeout obligatorio, config_resolver para multi-tenant. Mi propuesta era subset estrictamente menor.

**Recomendacion:** descartar D3. Cualquier dud sobre flow se resuelve en `SCH_FB_FLOW_DAG.md` v2.0.

### D4 - SPEC_LLM_GATEWAY_FALLBACK_v1

**Status original v1.0:** NEW - ADOPTAR
**Status revisado v1.1:** **REDUNDANTE - descartar**

**Por que cambia:** LiteLLM provee fallback nativo segun D8 del SPEC_FB_AGENT_BUILDER (gateway 100+ LLMs en formato OpenAI con callbacks). TIER1 #10 (Anthropic-only) hace que el fallback sea intra-Anthropic (Sonnet -> Haiku como degradacion). No requiere nuevo SPEC.

**Recomendacion:** descartar D4.

### D5 - PLB_AGENT_AUTHORING_v1 (chat-first)

**Status original v1.0:** NEW - ADAPTAR
**Status revisado v1.1:** **INVALIDO - contradice TIER1 firmado**

**Por que cambia:** TIER1 #15 firmado dice **"Agent Factory wizard 4 pasos"**. Mi propuesta de "creacion chat-first" violaria el plan firmado. Adicionalmente, R4 del POL_FABERLOOM_SURFACE_CONTRACT prohibe inventar "asistente local" en cada surface - la mecanica de iteracion siempre es via GlobalChatTrigger, no chat embebido en Agent Factory.

**Recomendacion:** descartar D5 tal cual. **PERO** rescatable: las **suggestion chips contextuales** (que propuse como parte de D5) si aplican como refinamiento del wizard de 4 pasos. Se vuelve refinamiento R5 (ver seccion3).

## 3. Refinamientos R1-R5 - recalibrados con tesis FaberLoom

Los 4 refinamientos del mensaje previo + 1 nuevo rescatado de D5:

| ID | Refinamiento | Superficie | Status v1.1 | Prioridad |
|---|---|---|---|---|
| R1 | Chip "Sugerencia del sistema" arriba de los 3 botones del ActionFooter governance en cards de Mesa | Mesa de Control (WorkLoom UI) | VIABLE | **Top** |
| R2 | Pre-seleccion automatica del tipo de edit (del dropdown SCH_FB_RESUMEN_RULE) basado en diff | Modal "porque del edit" | VIABLE | Medio |
| R3 | "Sugerencias del dia" como chips clicables, no bullets texto | Workspace home (= SpaceLoom global, segun POL_SURFACE_CONTRACT) | VIABLE | Bajo |
| R4 | Chip "destino sugerido" en correos de baja confianza del Inbox, aprendido del historico del user (L2 Episodic privada) | Inbox | VIABLE | **Top** |
| R5 (nuevo) | Suggestion chips contextuales dentro del Agent Factory wizard 4 pasos ("definir trigger", "agregar skill voz", "probar con caso golden") | Agent Factory (al final de cada paso) | VIABLE | Medio |

Justificacion del orden:
- R1 + R4 son **top** porque tocan el flujo principal del dia a dia: Inbox (entrada) y Mesa (criterio). La tesis FaberLoom es optimizar para correo del dia a dia con multiples superficies, y estas dos son las superficies de mas trafico operativo.
- R2 + R5 son **medio** porque refinan flujos menos frecuentes pero importantes para learning HITL (R2) y autoring (R5).
- R3 es **bajo** porque el Workspace (SpaceLoom) ya tiene sugerencias del dia funcionales - el cambio es cosmetico, no estructural.

## 4. Drifts detectados en la KB FaberLoom

Cinco drifts/inconsistencias que afectan a un lector entrante. NO se proponen fixes en este AUDIT, solo se documentan:

| # | Drift | Documentos afectados | Riesgo |
|---|---|---|---|
| 1 | **L0-L4 labels reutilizados con semanticas distintas** | `SPEC_FB_KNOWLEDGE_RIVER_v1` v1.1 usa L0-L4 para memoria/persistencia (KB inicial, Working, Episodic privada, Pool colectivo, Indexed firmado). Shell consolidated v2 (mockups) usa L0-L4 para autoridad/curaduria (Mundo, Vertical, Tenant, Workspace, Usuario) | ALTO - confusion grande al cruzar docs. Recomendacion futura: renombrar uno de los dos sistemas (sugerencia: capas River pasan a `R0-R4`, capas autoridad mantienen `L0-L4`) |
| 2 | **"Workspace" vs "SpaceLoom"** | `POL_FABERLOOM_SURFACE_CONTRACT` v0.1 DRAFT (2026-05-04) usa "Workspace" como mecanica universal de chat. `faberloom_shell_consolidated_v2_2026-05-07.md` (3 dias despues) renombra a "SpaceLoom" como home cognitivo y "Workspace" pasa a ser contenedor de cliente/proyecto | MEDIO - drift entre POL DRAFT y mockup. Recomendacion: bumpear POL_SURFACE_CONTRACT a v0.2 alineando naming, o ratificar uno de los dos |
| 3 | **"No sub-agentes" del IDX vs P16** | `IDX_FB_FOUNDATION_BETA.md` lista "No sub-agentes" en restricciones inquebrantables. `ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1` (P16) define 10 sub-agentes canonicos. `SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1` reconcilia (E1 standalone, E2 jerarquico) pero el IDX no refleja la reconciliacion | MEDIO - lector entrante puede pensar que P16 esta cancelado. Recomendacion: bumpear IDX agregando nota aclaratoria con link a TIER1_CONSTRAINTS |
| 4 | **Namespace `metadata.mwt.*`** | D5 del `SPEC_FB_AGENT_BUILDER_v1` v2.0 reconoce como deuda tecnica. Alias futuro `metadata.fbl.*` pendiente. Manifests existentes usan el namespace viejo | BAJO - documentado y manejado. Migracion pendiente sin fecha |
| 5 | **CURATOR_OPERATING_MODEL DEPRECATED sin marca visible** | `SPEC_FB_KNOWLEDGE_RIVER_v1` v1.1 (2026-05-02) marca `ENT_FB_CURATOR_OPERATING_MODEL_v1.md` como DEPRECATED en su seccion1.1. Pero el archivo deprecated sigue en `docs/faberloom/` sin frontmatter `status: DEPRECATED` ni marca visible en titulo | BAJO - lector que llegue directo a CURATOR_OPERATING_MODEL no sabra que esta deprecated. Recomendacion: bumpear el archivo deprecated con frontmatter explicito |

## 5. Respuestas a las 5 preguntas que estaban abiertas

1. **Composicion `@router -> @cotizador`** = **sub-agentes individuales standalone** del catalogo `ENT_FB_SUB_AGENTS_LIBRARY_v1` (10 atomicos). En E1 cada uno invocable solo. La cadena lineal entre ellos es via nodos `skill_call` de un flow DAG (SCH_FB_FLOW_DAG.md v2.0). Composicion jerarquica orquestada = E2 via feature flag.

2. **Grounding policy vs L0-L4**: NO son lo mismo. Drift #1 documentado en seccion4. El "grounding" como concepto user-facing **no existe en el canon** porque HITL absoluto + P3 draft-first + Voice Humanizer v2 resuelven el problema desde otro angulo arquitectonico.

3. **Draft state al crear agente**: NO hay draft fluido. Es **Agent Factory wizard 4 pasos** que culmina en agent registrado en tabla `agents`. No hay estado intermedio editable libremente como en nexos.

4. **Creacion chat-first vs wizard**: Wizard. Chat-first violaria TIER1 firmado.

5. **Que crea Inbox al ensenarle routing**: **parcialmente respondido**. SPEC_FB_INBOX_ROUTING_v1 esta listado como pendiente en el shell consolidated v2 seccion19. Hasta que exista, la respuesta operativa es: el signal del user alimenta L2 Episodic privada (Knowledge River) del user que ensena, y con k-anon >=5 puede subir a L3 Pool colectivo del tenant para que otros se beneficien.

## 6. Recomendacion operativa post v1.1

Decisiones que requieren input CEO antes de cualquier nuevo BATCH:

1. **D1 POL_GROUNDING_POLICY acotado**: aprobar reformulacion como `POL_FB_WORKSPACE_ITERATION_MODE_v1` solo para GlobalChatTrigger, o descartar completo?
2. **R1-R5 refinamientos**: priorizar implementacion (recomendado R1 + R4 primero, ambos top), o discutir alguno antes?
3. **Drifts 1-5 detectados**: cuales se cierran ahora (bumpeando docs afectados) y cuales se difieren?

Sin esas 3 decisiones, este v1.1 se queda en `generated_staging/` indefinido. Recomendacion: hacer un mini-batch SOLO con (a) este AUDIT v1.1 indexado + (b) una nota corta en MANIFIESTO_CAMBIOS_v2 declarando los 5 drifts como "detectados, pendiente fix". Las decisiones de D1/R1-R5 se toman despues, con tiempo.

## 7. Que se mantiene del AUDIT v1.0 indexado (sin tocar, append-only)

El v1.0 sigue como esta en canonico (commit d3575c7) por POL append-only. Lectores futuros deben leer **ambos** v1.0 y v1.1 para tener el cuadro completo. El v1.1 es **complemento, no reemplazo**.

El `ARCH_NEXOS_SIMPLIFICATION_PRINCIPLES_v1.md` indexado tampoco se toca. Sus 8 principios destilados siguen validos como referencia general. Lo que el v1.1 hace es **aplicar esos principios al canon FB real**, no inventar nuevos.

## Changelog

- v1.1 (2026-05-17): rectificacion post revision profunda KB FaberLoom (12 docs canonicos leidos: IDX, P16, AGENT_BUILDER, SURFACE_CONTRACT, ARCHETYPES, KNOWLEDGE_RIVER, TIER1_CONSTRAINTS + 5 referenciados). 5 deltas D1-D5 del v1.0 reanalizados: D1 SCOPE_ACOTADO, D2/D3/D4 REDUNDANTE, D5 INVALIDO. 4 refinamientos R1-R4 + 1 nuevo R5 rescatado, priorizados. 5 drifts detectados en KB FB documentados (L0-L4 ambiguo, Workspace/SpaceLoom naming, IDX vs P16, namespace mwt/fbl, CURATOR deprecated sin marca). 5 preguntas previas resueltas (4 totalmente, 1 parcialmente). Recomendacion: decisiones CEO requeridas antes de promover algun delta.
