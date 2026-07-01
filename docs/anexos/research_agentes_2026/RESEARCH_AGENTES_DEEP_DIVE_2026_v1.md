---
id: RESEARCH_AGENTES_DEEP_DIVE_2026_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: research-note
stamp: VIGENTE 2026-06-01
fecha: 2026-06-01
agente: Cowork (orquestador) + 4 sub-agentes Claude (research paralelo)
fuente: Repos GitHub, docs oficiales, papers arXiv, benchmarks (web general)
alcance: Deep dive de 4 ejes - memoria, context engineering, LangGraph, agente SDR B2B
metodo: Swarm de 4 sub-agentes en paralelo, fuentes primarias preferidas, datos no verificables marcados [NO VERIFICADO]
nota: Sintesis de fuentes externas. NO contiene datos operativos MWT. Material para decisiones de arquitectura.
relacionado_con:
  - RESEARCH_AGENTES_MEDIUM_ABR_MAY_2026_v1
  - ARCH_AGENT_PRINCIPLES
  - SPEC_FB_AGENT_RUNTIME_STACK_v1
  - ENT_FB_AGENT_DECOMPOSITION_PRINCIPLE_v1
---

# Deep Dive: Arquitectura de Agentes IA (2026)

Investigacion profunda sobre 4 ejes, ejecutada con un swarm de 4 sub-agentes en paralelo, priorizando fuentes primarias (repos GitHub, docs oficiales, papers). Continuacion de RESEARCH_AGENTES_MEDIUM_ABR_MAY_2026_v1, que se basaba solo en Medium.

## TL;DR - Decisiones de arquitectura

| Eje | Recomendacion directa | Confianza |
|-----|----------------------|-----------|
| Memoria | **Mem0** como capa primaria (aislamiento multi-tenant nativo user_id/org_id + MCP oficial + n8n). Graphiti/Zep si se necesita razonamiento temporal. | Alta |
| Context engineering | **Restatement en la cola del contexto** + system prompt estatico cacheado. Nunca tocar el system prompt entre turnos. | Alta (docs Anthropic + Chroma) |
| Orquestador | **LangGraph 1.0** (unico con GA, checkpointing, HITL nativo, sin model-lock). Multi-tenancy se implementa a mano (thread_id namespaced + RLS). | Alta |
| SDR B2B | Stack: Apollo + Clay + Instantly + **WhatsApp Business API** (LATAM es WhatsApp-first). RAG anclado a catalogo verificado es el activo critico. | Media-alta |

---

## Eje A - Memoria de agentes

### Patrones transversales
- **Memoria tiered:** working (context window) / episodic (historial raw) / semantic (hechos destilados, KG) / procedural (instrucciones auto-optimizadas, solo Letta/LangMem).
- **Salience-gated writing:** el write-time es una apuesta irreversible bajo incertidumbre - no sabes que queries futuras vendran cuando decides comprimir. Mem0 usa LLM extractor; Graphiti invalida hechos viejos por ventana temporal (valid_at/invalid_at) en vez de borrar; Letta deja al agente paginar con tools explicitas.
- **Write-read asymmetry:** comprimir agresivo gana latencia de lectura pero pierde recall en queries inesperadas; preservar provenance cruda da fidelidad con mas overhead.

### Comparativa (datos de repos, may 2026)

| Dimension | Mem0 | Graphiti/Zep | Letta (ex-MemGPT) | LangMem |
|-----------|------|--------------|-------------------|---------|
| Modelo | Vector + KG + KV | Temporal KG (Neo4j) | OS-paging (RAM/disco) | Vector + namespace |
| Extraccion | LLM pipeline auto | Incremental graph build | Agent tool calls | LLM manager (hot/bg) |
| Temporalidad | Basica | Nativa (valid_at/invalid_at) | No | No |
| Multi-tenant nativo | Si (user_id/org_id) | Zep Cloud si; OSS manual | Manual | Si (namespaces) |
| MCP | Si (oficial) | Si (Graphiti MCP v1.0) | No oficial | No |
| n8n | Si (community, SSE) | Parcial | No | No |
| LangGraph | Integrado | Integrado | Ecosistema propio | Nativo |
| Stars | 51.4k | 25.4k (Graphiti) | 23.1k | 1.3k |
| Madurez prod | Alta (v1.0.9, 277 releases) | Alta (Cloud) / Media (OSS) | Media-alta | Baja (sin releases) |
| Licencia | Apache 2.0 | Apache 2.0 | Apache 2.0 | MIT |

### Recomendacion
**Mem0** para orquestador multi-tenant: el modelo user_id+agent_id+org_id hace imposible que una query sin tenant cruce namespaces (filtro obligatorio por diseno de API), tiene MCP server oficial y thread n8n confirmado, y madurez de produccion (YC S24, paper en arXiv con benchmark LOCOMO).
**Graphiti/Zep** solo si el caso requiere razonar sobre como cambia el estado en el tiempo (preferencias de cliente enero vs ahora, contradicciones temporales). Gana en LongMemEval (63.8% vs Mem0 49.0%) pero exige Neo4j propio o pagar Zep Cloud para el aislamiento managed.
**Letta** descartable aca: foco rotando a coding agents, multi-tenant manual, sin MCP/n8n nativo.
*Nota: los benchmarks de accuracy de Mem0 (+26% sobre OpenAI Memory, 90% menos tokens) son auto-reportados [NO VERIFICADO independientemente].*

---

## Eje B - Context engineering / Restatement

### El principio (con evidencia)
Anthropic formalizo "context engineering" en sep 2025: encontrar el menor set de tokens de alta senal que maximice el output deseado. El fondo: atencion cuadratica del transformer - a mas contexto, el presupuesto de atencion se reparte mas fino. Chroma (jul 2025, 18 modelos frontier) confirmo empiricamente el **context rot**: TODOS los modelos degradan precision al llenarse el contexto. No es bug de un modelo, es propiedad del transformer. El patron **lost in the middle** (Stanford): mover el doc relevante del inicio al medio baja precision >30%.

### Las dos categorias (regla central)
- **Estatico** (system prompt, tool schemas, ejemplos canonicos): cachear con `cache_control`. NUNCA modificar entre turnos. La API cachea por hash del prefijo exacto (tools -> system -> messages). Un timestamp o valor dinamico dentro del prefijo destruye el cache (se pierde hasta 85% reduccion de latencia y 90% de costo).
- **Dinamico** (historial, tool outputs, estado de tarea): vive en la cola de `messages`. Aca aplica Restatement.

### Restatement - implementable
En cada vuelta del loop, antes del turno del assistant, inyectar en el ultimo user message un bloque que re-enuncia (no copia verbatim):
```
<task_restatement>
Objetivo actual: ...
Paso siguiente: ...
Constraints activos: [solo los relevantes a este paso]
Estado acumulado: [3-5 bullets de lo ya hecho/decidido]
</task_restatement>
```
En n8n: nodo "Build Restatement" antes del nodo Claude, que arma el bloque con variables de estado del workflow. No hardcodear en system prompt.

### Estructura recomendada del contexto
```
tools[]      <- ESTATICO, cache_control
system       <- ESTATICO, cache_control
  <background> <instructions> <tool_guidance> <output_schema>
messages[]   <- DINAMICO, no cachear
  historial compactado
  tool_results (sandboxeados, no dumps crudos)
  [ultimo user turn] -> <task_restatement>
```

### Errores comunes
1. Modificar el system prompt cada turno para "refrescar" -> invalida KV-cache. Usar Restatement en la cola.
2. Volcar tool outputs crudos (un snapshot Playwright = 56KB). Sandboxear: el agente computa via script/query, solo el resumen entra al contexto (hasta 99% menos overhead; Claude Code usa head/tail/grep).
3. Esperar al 100% para compactar. Chroma ve degradacion desde 50%. Compactar con directiva explicita a los 60-75%.
4. Restatement verbatim del system prompt (duplica tokens sin valor). Debe ser especifico al turno.
5. Muchos edge cases vs pocos ejemplos canonicos. Anthropic: 3 ejemplos que cubren el patron > 20 variaciones.

---

## Eje C - LangGraph como orquestador

### Estado verificado
LangGraph 1.0 GA: 22-oct-2025 (primer stable en durable agent frameworks). SDK reciente langgraph-sdk 0.3.11 (mar 2026). 26.2k stars, adoptado por Klarna, LinkedIn, Uber, Replit, Elastic.

### Capacidades core
- **Grafo:** StateGraph con schema tipado, nodos = funciones Python puras, conditional_edges para routing. Sin abstraccion de prompts - control total.
- **Checkpointing:** pluggable (MemorySaver dev, AsyncPostgresSaver prod). **Limitacion critica:** si crashea DENTRO de un nodo (no entre nodos), el checkpoint no captura progreso parcial - el nodo re-ejecuta entero (sobrecosto silencioso en nodos con LLM calls caros).
- **Time-travel/replay:** inspeccionar y re-ejecutar desde cualquier estado previo. Clave para auditoria.
- **HITL:** `interrupt()` pausa, serializa estado, congela hasta aprobacion humana. Soporta modificar estado antes de resumir.
- **MCP/A2A:** MCP como toolbox de nodos (patron establecido). A2A en lista oficial de frameworks compatibles, pero ecosistema aun chico (<200 agentes publicos) - no apostar arquitectura critica a A2A cross-framework hoy.
- **Observabilidad:** LangSmith nativo (pago en prod, ~$0.005/run -> evaluar Langfuse/Phoenix OSS antes de escalar).

### Comparativa

| Dimension | LangGraph 1.0 | OpenAI Agents SDK | Google ADK | Temporal |
|-----------|---------------|-------------------|------------|----------|
| Modelo | Grafo dirigido ciclico | Handoffs | Jerarquico | Workflow durable |
| Model-lock | Ninguno | OpenAI | Optimizado Gemini | N/A |
| Durabilidad | Checkpoint entre nodos | Efimero | Session state | Total (event sourcing) |
| HITL | Nativo (interrupt) | No nativo | Limitado | Via signals |
| A2A | Si | No | Nativo (creadores) | No |
| Multi-tenant | Manual | Manual | Manual | Manual |
| Madurez | v1.0 GA | Reciente | Nuevo/verde | Muy maduro |
| Boilerplate | Alto (low-level) | Bajo | Medio | Alto |

### Recomendacion
**Si, LangGraph** como orquestador. Es el unico con 1.0 GA, checkpointing probado, HITL de primera clase, MCP/A2A, sin model-lock (critico para Claude + n8n). Riesgos a mitigar:
1. **Multi-tenancy sin primitivas:** namespacing por thread_id = `{tenant_id}:{conversation_id}` + Postgres con RLS activo. El boilerplate de aislamiento lo carga la plataforma.
2. **Durabilidad intra-nodo:** disenar nodos atomicos (1 LLM call por nodo), o envolver LangGraph en Temporal para nodos criticos/caros. Patron emergente 2026: Temporal como shell externo + LangGraph para el reasoning loop.
3. **Costo LangSmith a escala:** evaluar OSS antes de 1M runs/dia.

---

## Eje D - Agente SDR B2B (Marluvas/Tecmater, LATAM)

### Arquitectura por capas
1. **Data/enrichment:** Apollo (lista por NAICS/SIC: manufactura, construccion, mineria, oil&gas; filtro pais LATAM; titulos Gerente HSE / Jefe de Compras / Seguridad Industrial) + Clay (waterfall enrichment, Claygent detecta si ya tienen proveedor EPP o mencionan normas NOM-113-STPS, ISO 20345).
2. **Intent (debil en LATAM industrial con 6sense/Demandbase):** mejores fuentes -> licitaciones publicas (COMPRANET Mexico, SECOP Colombia) con alertas "calzado de seguridad/EPP/bota dielectrica"; LinkedIn Sales Navigator (empresas contratando HSE Manager = escalan programa seguridad); noticias de inversion en planta.
3. **Outreach multicanal:** Instantly/Smartlead (email), Heyreach/Expandi (LinkedIn), **WhatsApp Business API (Meta Cloud) + Wati/Respond.io** - en LATAM WhatsApp ~95% lectura vs ~25% email. Multicanal convierte 2.3x sobre canal unico. Cadencia 3 dias mejora inbox placement (73% -> 91%).
4. **CRM:** HubSpot (SMB) o Salesforce. Auto-crear deal en respuesta positiva, registrar toques, disparar MQL->SQL en solicitud de cotizacion, asignar a humano con contexto. Campo `distribuidor_id` para no hacer outreach frio a cuentas calientes.
5. **Escalamiento (autonomia asistida):** handoff automatico en solicitud de cotizacion/volumen, pregunta tecnica bajo umbral RAG, segundo reply en hilo, ICP score alto (>=7/10). El humano recibe resumen + score + normas + historial.
6. **Guardrails anti-alucinacion (CRITICO):** un agente que inventa certificacion ATEX puede causar incidente laboral y responsabilidad legal. RAG anclado a `catalog.json` verificado (modelo, SKU, normas CON certificado real, tallas, lead time); umbral de confianza (retrieval < 0.75 -> "verifico con el equipo tecnico" + escala); lista blanca de certificaciones (mencion fuera de lista -> escala forzado); separar hechos de catalogo (RAG cerrado) de conversacion comercial (LLM libre).
7. **Metricas:** respuesta por canal/vertical, MQL->SQL, meeting booked (>1.5% hibrido), tiempo de respuesta WhatsApp (<5 min), tasa de escalamiento correcto, precision RAG (% claims verificables).

### Plan por fases
- **Sem 1-4:** construir `catalog.json` (activo mas critico) + lista Apollo del vertical prioritario (propuesta: mineria Mexico).
- **Sem 5-8:** outreach email+WhatsApp con aprobacion humana en cada mensaje. Calibrar tono LATAM. Medir.
- **Sem 9-16:** semi-autonomia toques 1-2 del funnel frio + handoff calibrado. Ajustar umbral RAG.
- **Mes 5+:** sumar LinkedIn, expandir Colombia, intent via alertas de licitacion.

### Recomendacion
Stack minimo viable: Apollo + Clay + Instantly + WhatsApp (Wati). Base de codigo real adaptable: el template open source `b2b-sdr-agent-template` (pipeline 10 etapas, memoria multicapa, WhatsApp+Email nativo, `product-kb/catalog.json`). NO automatizar hasta tener 3+ meses de datos: primer follow-up a distribuidores existentes (la relacion se puede romper), negociacion de precio/volumen, respuestas tecnicas de certificacion hasta que el RAG este auditado. El mayor riesgo no es tecnologico: es lanzar con catalogo mal estructurado. Invertir 1 semana en `catalog.json` antes de tocar outreach.
*Benchmarks de respuesta/meeting-rate citados de fuentes secundarias [verificacion parcial].*

---

## Sintesis cruzada

**Refuerzos entre ejes:**
- **Restatement (B) + decomposition principle (KB):** el patron de re-enunciar estado en la cola encaja con orquestador delgado + sub-agentes. Cada sub-agente arranca con contexto limpio y recibe un Restatement scoped, evitando el context rot que sufre un agente monolitico en loops largos.
- **Mem0 (A) + LangGraph (C):** ambos usan filtro por tenant como obligatorio. Mem0 user_id/org_id se mapea al namespacing thread_id de LangGraph. Coherente con la regla MWT multi-tenant (tenant_id NOT NULL, RLS source of truth).
- **MCP es el hilo comun:** Mem0, Graphiti y LangGraph lo soportan. Confirma la apuesta MCP del stack actual.
- **Guardrails SDR (D) + HITL LangGraph (C):** el `interrupt()` de LangGraph es el mecanismo natural para el handoff de autonomia asistida y para el escalamiento por umbral de confianza del RAG.

**Conflictos / tensiones a resolver:**
- **Durabilidad intra-nodo (C) vs sub-agentes atomicos:** si cada sub-agente hace varios LLM calls, el crash intra-nodo de LangGraph pierde progreso. Resolver con nodos de 1 LLM call o Temporal wrapping. Decision de infra pendiente.
- **Compresion de memoria (A) vs fidelidad temporal:** Mem0 comprime agresivo (gana costo/latencia) pero pierde recall en queries inesperadas; Graphiti preserva historia temporal con mas overhead. Para datos comerciales de cliente que cambian (precios, preferencias), Graphiti seria mejor, pero choca con la simplicidad de Mem0. Evaluar memoria hibrida por dominio.
- **LangSmith costo (C) vs observabilidad necesaria:** a escala el costo obliga a OSS, lo que agrega trabajo de integracion.

## Implicaciones para MWT / FaberLoom
(Lectura de Cowork - validar contra ARCH_AGENT_PRINCIPLES y SPEC_FB_AGENT_RUNTIME_STACK_v1 antes de adoptar)
- Adoptar **Restatement** como patron de runtime explicito (encaja con la distincion estatico/dinamico ya implicita).
- Evaluar **Mem0** como capa de memoria de la plataforma (aislamiento multi-tenant + MCP) en una prueba acotada.
- Confirmar **LangGraph** como orquestador, con spec de namespacing tenant + decision de durabilidad (atomico vs Temporal).
- El **agente SDR B2B** es el caso de uso con ROI mas claro y cercano; arrancar por el `catalog.json` de Marluvas/Tecmater.

---

## Fuentes primarias (verificadas por los sub-agentes)

### Memoria
- github.com/mem0ai/mem0 ; docs.mem0.ai/platform/features/mcp-integration ; mem0.ai/research
- github.com/getzep/graphiti ; arxiv.org/abs/2501.13956 ; help.getzep.com/graphiti/getting-started/mcp-server
- github.com/letta-ai/letta ; github.com/langchain-ai/langmem ; langchain-ai.github.io/langmem/concepts/conceptual_guide
- vectorize.io/articles/mem0-vs-zep ; community.n8n.io/t/mem0-integration

### Context engineering
- anthropic.com/engineering/effective-context-engineering-for-ai-agents
- docs.anthropic.com/en/docs/build-with-claude/prompt-caching ; anthropic.com/news/prompt-caching
- research.trychroma.com/context-rot (Context Rot, Chroma jul 2025)

### LangGraph
- github.com/langchain-ai/langgraph ; changelog.langchain.com/announcements/langgraph-1-0-is-now-generally-available
- docs.langchain.com/oss/python/langgraph/durable-execution ; google.github.io/adk-docs/a2a
- openai.github.io/openai-agents-python/handoffs ; langchain.com/pricing

### SDR B2B
- github.com/iPythoning/b2b-sdr-agent-template ; github.com/MatthewDailey/open-sdr
- salesmotion.io/blog/ai-sdr-tools-compared ; knowlee.ai/compare/clay-vs-apollo
- outreaches.ai/blog/cold-outreach-benchmarks ; jelou.ai (WhatsApp AI LATAM)
- meilisearch.com/blog/rag-guardrails ; altexsoft.com/blog/ai-guardrails

*Nota de verificacion: algunas URLs de arXiv 2026 reportadas por los sub-agentes (2601.06007, 2603.09619) no fueron confirmadas por Cowork de forma independiente - tratar como [NO VERIFICADO] hasta abrir el paper.*

## Changelog
- v1.0 (2026-06-01): Creacion. Deep dive con swarm de 4 sub-agentes (memoria, context engineering, LangGraph, SDR B2B). Autor: Cowork. Pendiente indexar a docs/ canonico via sync si el CEO lo aprueba.
