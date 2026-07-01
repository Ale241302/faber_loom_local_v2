---
id: AUDIT_NEXOS_AI_DELTAS_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: ARQUITECTURA_FUNDACIONAL
type: AUDIT
date: 2026-05-17
source: workspace.nexos.ai (trial), inspeccion directa via Chrome MCP
---

# AUDIT_NEXOS_AI_DELTAS_v1 - Investigacion nexos.ai vs arquitectura MWT/FaberLoom

## 0. Contexto y alcance

Plataforma analizada: **nexos.ai** (lituana, "AI Workspace" + "AI Gateway"), tenant TitanPoint7515 trial. SOC 2 Type 1 + ISO 27001 + GDPR. Modelos hosted Vertex EU.

4 areas exploradas: orquestacion, KB/RAG, UI agente, multi-tenancy/governance. Fuentes: navegacion directa /chat, /agents, /agents/new, /agents/templates, /projects, /management, /management/teams, /management/models. Cross-check con docs publicas (nexos.ai/features/, /ai-gateway/, /ai-for-developers/).

Aclaracion previa: nexos.ai no es competencia directa de MWT KB ni de FaberLoom. nexos = horizontal enterprise AI workspace para corporaciones; MWT KB = repo curado bilingue de una sola empresa; FaberLoom = SaaS vertical para fabricantes. Pero nexos resuelve **el problema de UX y configuracion de agentes** que FaberLoom tendra que resolver tambien, y resuelve **un AI gateway con fallback** que MWT no tiene. Ahi estan los aprendizajes.

---

## 1. Hallazgos crudos por area

### 1.1 Orquestacion

- **Agent = bundle declarativo**: Name + Description + Model + Creativity preset + Execution trigger (Prompt | Schedule) + Instructions (system prompt hasta 32K chars) + Capabilities toggles + Integrations [] + Conversation starters [].
- **Flow tab** = state machine narrativa visual, lineal, con un Goal raiz y N nodos secuenciales. Cada nodo tiene un mini-prompt narrativo. Ejemplo Content Writer: Goal -> Acknowledge Role -> Await Brief -> Produce or Improve. No vi conditionals/branching explicito; el routing dentro de cada step lo hace el LLM internamente segun el prompt del nodo. Es state machine como **convencion narrativa**, no como grafo conmutado tipo n8n.
- **Studio** (panel lateral) tabs: Try agent (sandbox chat) | Flow (workflow) | Settings (gear).
- **Composicion entre agentes**: via `@agent-name` en chat libre. Memoria del agent persiste; project comparte context entre agents invocados.
- **Schedule trigger nativo per-agent** (cron-like) sin requerir n8n externo.
- **Suggestion chips contextuales** generadas por LLM: "Add brand voice customization", "Tighten response instructions", "Switch to creative mode" - iteracion guiada.
- **"Generate with AI"** boton sobre el campo Instructions: el LLM autocompleta el system prompt desde la descripcion.

### 1.2 KB / RAG / memoria

- **Projects = colecciones de chats + files con RAG persistente**. Estructura: nombre, files (upload), creativity policy, instructions a nivel project. Files = bag plano, sin tags, sin taxonomia, sin versioning visible, **sin permisos per-file**.
- **Project creativity policy** (5 niveles enumerados, semanticos y mutuamente excluyentes):
  - Grounded: "Uses only the provided context. Zero outside knowledge."
  - Guided: "Stays close to the context, but carefully supplements with outside knowledge when needed."
  - Balanced: "Mixes context and outside knowledge with no strong preference."
  - Analytical: "Works only within the provided context, but surfaces deeper patterns and less obvious connections."
  - Creative: "Combines context with outside knowledge to create novel ideas and new directions."
- **Agent KB capability** = toggle binario "Knowledge base" (enable/disable acceso a internal docs). No vi granularidad.
- Memoria de agent persiste cross-thread (declarado en feature page, no validado en sandbox por timeout de trial).

### 1.3 UI crear/editar agente

- **Chat-first creation**: pantalla principal es un chat "Describe the task you want this agent to handle" + templates (~106) como atajo. El LLM construye el agente conversacionalmente.
- **Studio panel** lateral aparece desde el primer mensaje:
  - **Try agent** = sandbox conversacional inmediato, con Clear chat.
  - **Flow** = vista state machine narrativa (descrita arriba).
  - **Settings (gear)** = editor estructurado de TODOS los campos del agente (todo lo del bundle declarativo).
- **No tiene tab "Sanidad" dedicado**. La sanidad se fusiona dentro de Try agent (el usuario prueba a mano).
- **Aprobacion** = solo Save / Discard draft. No tiene el patron 3-boton (aprobar/descartar/iterar) que define el contract FaberLoom de Alvaro.
- **Conversation starters** = sugerencias de prompts iniciales que el agent muestra al usuario final, declaradas por el creador del agent.
- **Templates** organizados por categoria: Marketing 16, Sales 21, Productivity 32, People & HR 13, Customer Support 4, Legal 4, Data 7, Finances 2, Product 7. Cada template viene con Model + Creativity + Conversation starters + Flow pre-rellenados.

### 1.4 Multi-tenancy + governance

- **Workspace = tenant raiz** (ej. TitanPoint7515). Subdivision interna **Teams**.
- **Per-team override**:
  - subset de Models habilitados (toggle por modelo).
  - **Fallback chain** por modelo: primario + N fallbacks ordenados. Si el primario falla, gateway cae al fallback. Esto es **AI Gateway capability** y MWT no la tiene.
  - Default model por team.
- **Org-level Models registry**: admin agrega modelos con custom name + provider id (anthropic.claude-X@version) + fallback chain. 17 modelos en trial (Claude Haiku/Sonnet/Opus 4.5-4.7, Gemini 2.5/3/3.1, GPT 5.3-5.5, GPT-OSS 120b, Imagen 4, Whisper 1, TTS 1).
- **Users**: seats utilization (1/10 en trial). Invite members.
- **Audit logs**: declarado en marketing page "every interaction recorded in detailed audit logs". No validado en UI de trial (probable que sea feature enterprise).
- **No vi equivalente a control_surface inmutable / hooks fail-closed**. La frontera de gobernanza es role admin del workspace. Modelo de proteccion = RBAC, no append-only audited.

### 1.5 Catalogo de integrations relevantes (40+)

Cubre: comms (Slack, Teams, Outlook), docs (Google Workspace, MS 365, Notion), CRM (Salesforce, HubSpot), PM (Asana, Monday, Trello, Linear, Atlassian-via-MCP), Marketing (LinkedIn, Meta Ads, Google Ads, Ahrefs, Similarweb), Finanzas (Stripe, QuickBooks), Dev (GitHub-via-MCP, BigQuery-via-MCP), Analytics (Google Analytics), Design (Figma, Canva). Adopta MCP standard para algunos (Atlassian, GitHub, BigQuery). **Gap critico para MWT**: NO Amazon SP-API, NO Helium 10, NO ERPs LATAM. Si MWT quisiera operar via nexos, tendria que esperar conectores o construir un MCP server propio.

---

## 2. OUTPUT 1 - Propuesta de deltas sobre KB MWT

Cinco deltas, ordenados por valor de adopcion para MWT/FaberLoom.

### Delta D1 - POL_GROUNDING_POLICY_v1 (NEW)

- **Archivo**: `docs/POL_GROUNDING_POLICY_v1.md`
- **Accion**: NEW
- **Razon**: nexos formaliza "creatividad" como policy de grounding en 5 niveles semanticos. MWT hoy lo deja implicito por archivo o por prompt. Necesario codificarlo como POL porque la decision "cuanto el agente puede salir de la KB" es regulatoria, no estetica.
- **Headers**:
  ```yaml
  id: POL_GROUNDING_POLICY_v1
  version: 1.0
  status: DRAFT
  visibility: INTERNAL
  domain: ARQUITECTURA_FUNDACIONAL
  type: POL
  ```
- **Contenido propuesto**:
  - 5 niveles enumerados (Grounded / Guided / Balanced / Analytical / Creative) con definicion operativa MWT.
  - Mapeo por dominio: POL/SPEC/ARCH/FROZEN -> Grounded obligatorio; SCH/LOC -> Guided; brainstorming -> Balanced/Creative; analitica de patrones -> Analytical.
  - Constraint cross-cutting: cualquier SKILL_ o PLB_ debe declarar `grounding_policy: <nivel>` en su frontmatter. Default = Guided. CEO-ONLY = Grounded forzado.
  - Excepcion: SCH_ y LOC_ pueden subir a Balanced si el agent explicita necesidad de localizacion regional fuera de la KB.

### Delta D2 - SPEC_AGENT_BUNDLE_v1 (NEW)

- **Archivo**: `docs/SPEC_AGENT_BUNDLE_v1.md`
- **Accion**: NEW
- **Razon**: nexos expone un bundle declarativo de agente claro y completo. MWT/FaberLoom tienen partes dispersas (instrucciones en PLB_, modelo en SKILL_, tools en otro lado). Conviene canonizar el shape antes de construir mas SKILL_.
- **Headers**:
  ```yaml
  id: SPEC_AGENT_BUNDLE_v1
  version: 1.0
  status: DRAFT
  visibility: INTERNAL
  domain: ARQUITECTURA_FUNDACIONAL
  type: SPEC
  ```
- **Bundle propuesto** (10 campos):
  ```
  - id (slug, kebab-case)
  - version (semver)
  - description (resumen 1-2 lineas)
  - model_primary (provider.model@version, fallback chain explicita)
  - grounding_policy (referencia a POL_GROUNDING_POLICY_v1)
  - execution_trigger (prompt | schedule:<cron> | event:<topic>)
  - instructions (system prompt, max 32K, ASCII puro)
  - capabilities (toggles: web_search, kb_access, code_exec)
  - tools (lista de tools_ids habilitados; cada tool con scope per-tenant)
  - flow (opcional: lista ordenada de steps narrativos con goal global)
  - conversation_starters (opcional, max 4)
  - visibility (PUBLIC | PARTNER_B2B | INTERNAL | CEO-ONLY)
  - tenant_scope (global | tenant:<id> | team:<id>)
  ```
- Snippet: incluir ejemplo concreto con SKILL_AMAZON_PRICING como referencia.

### Delta D3 - SPEC_AGENT_FLOW_v1 (NEW)

- **Archivo**: `docs/SPEC_AGENT_FLOW_v1.md`
- **Accion**: NEW
- **Razon**: nexos demuestra que una state machine **narrativa lineal** (Goal + Steps con prompt embebido en cada estado) es suficiente para 90% de agentes y mucho mas digerible que ENT_OPS_STATE_MACHINE actual. Sin invadir el FROZEN, definir un sub-tipo "Flow" para SKILL_ que se renderice tipo nexos pero exprese transiciones MWT.
- **Headers**:
  ```yaml
  id: SPEC_AGENT_FLOW_v1
  version: 1.0
  status: DRAFT
  visibility: INTERNAL
  domain: ARQUITECTURA_FUNDACIONAL
  type: SPEC
  ```
- **Modelo propuesto**:
  - Goal (1 frase declarativa).
  - Steps[] ordenados; cada step: id, label, prompt_block (ASCII), success_signal, on_failure (next_step | retry | escalate).
  - Soporte opcional para branching declarado (no implicito): step puede declarar `next_step_when: <condicion>`.
  - Renderizado: misma logica que nexos (cards expandibles).
  - Restriccion: Flow es **declarativo**, no ejecutivo. El runtime traduce a una secuencia de prompts contra el modelo; no reemplaza n8n para automatizacion programatica.
- Anti-rationalization: no convertir ENT_OPS_STATE_MACHINE en Flow. Son cosas distintas; el state machine global de operacion **no se toca**.

### Delta D4 - SPEC_LLM_GATEWAY_FALLBACK_v1 (NEW)

- **Archivo**: `docs/SPEC_LLM_GATEWAY_FALLBACK_v1.md`
- **Accion**: NEW
- **Razon**: nexos Gateway expone primitiva "fallback chain por modelo" per-team. MWT hoy no la tiene declarada y los SKILL_ asumen un modelo sin redundancia. Si Anthropic cae mid-sprint, no hay policy. Para B2B (Marluvas/Tecmater) esto matara confianza.
- **Headers**:
  ```yaml
  id: SPEC_LLM_GATEWAY_FALLBACK_v1
  version: 1.0
  status: DRAFT
  visibility: INTERNAL
  domain: PLATAFORMA
  type: SPEC
  ```
- **Contenido**:
  - Tabla de modelos canonicos MWT (~8 modelos) con: provider id, fallback chain, latency budget, cost/1Mtok, region (LATAM-allowed).
  - Policy: todo SKILL_ debe declarar `model_primary` + obtener fallback de esta tabla, no del propio archivo.
  - Reglas de fallback: tier match obligatorio (Sonnet -> Sonnet, Opus -> Sonnet+Opus). Fallback nunca downgradea capability (vision, function calling).
  - Per-tenant override: tenant puede restringir lista (ej. cliente compliance solo OpenAI EU) sin filtrar a otros tenants.

### Delta D5 - PLB_AGENT_AUTHORING_v1 (NEW) + EXTEND PLB_ORCHESTRATOR-refs

- **Archivo nuevo**: `docs/PLB_AGENT_AUTHORING_v1.md` (NEW)
- **Archivo extendido**: `docs/IDX_PLATAFORMA.md` (EXTEND, agregar entrada y crossref)
- **Razon**: nexos materializa el patron "chat-first agent authoring con Studio lateral (Try + Flow + Settings)" mas suggestion chips contextuales. FaberLoom va a necesitar este flujo. Codificarlo como PLB antes de implementarlo previene fragmentacion entre SKILLs.
- **Headers PLB nuevo**:
  ```yaml
  id: PLB_AGENT_AUTHORING_v1
  version: 1.0
  status: DRAFT
  visibility: INTERNAL
  domain: PLATAFORMA
  type: PLB
  ```
- **Contenido**:
  - Layout obligatorio: chat principal izquierda + Studio panel derecho con tabs Configurar / Iterar / Sanidad (mantener taxonomia FaberLoom de Alvaro; NO copiar literal Try/Flow/Settings de nexos).
  - Suggestion chips: generadas por el LLM tras cada turno; max 4 visibles; texto corto imperativo.
  - "Generate with AI" para campo Instructions (autocompletar system prompt). Permitido bajo POL_GROUNDING_POLICY = Guided minimo.
  - Aprobacion final: respeta el contract FaberLoom 3-boton (aprobar / descartar / iterar). **No adoptar el Save/Discard binario de nexos** - la regla Alvaro existe por una razon explicita en memoria.
  - Upload visible en cada superficie (regla FaberLoom universal).

### NO adoptables tal cual (anti-deltas)

- **Files sin permisos per-archivo**: nexos KB es bag plano sin visibility. Rompe POL visibilidad MWT (PUBLIC/PARTNER_B2B/INTERNAL/CEO-ONLY). No adoptar; mantener taxonomia + headers.
- **Save/Discard binario**: rompe el contract 3-boton FaberLoom. No adoptar.
- **Bag of files sin taxonomia**: la KB MWT depende de los 8 tipos + headers + visibility para enforcement por hooks. nexos no tiene equivalente. No adoptar.
- **Audit como feature de plataforma (sin manifest selectivo)**: MWT audit = git + sync_*_indexa.ps1 + MANIFIESTO. Es mas estricto que nexos. Mantener.

---

## 3. OUTPUT 2 - Casos de uso: como nexos resuelve X que nosotros hacemos Y

### Caso 1: "Cuanto se le permite al LLM salir de la KB"

- **Problema (MWT)**: cada PLB_ y SKILL_ resuelve esto via convencion textual en el prompt. No es enforceable, no es legible para auditoria, no escala para B2B con compliance diferente por cliente.
- **Como MWT lo resuelve hoy**: instruccion embebida en system prompt tipo "no inventes" + revision humana ad-hoc.
- **Como nexos lo resuelve**: Project Creativity como primitiva de UI con 5 niveles semanticos. Cada nivel modifica system prompt y temperatura subyacentes; el usuario solo elige semantica.
- **Por que es mejor para nuestro contexto**: codificar grounding como POL explicito hace auditable la decision (Marluvas exige B2B partner; Rana Walk acepta Creative para copy marketing). Auditor puede leer el frontmatter del SKILL_ sin parsear instrucciones libres.
- **Veredicto**: **ADOPTAR** via Delta D1 (POL_GROUNDING_POLICY_v1). Mantener nomenclatura nexos (Grounded/Guided/Balanced/Analytical/Creative) porque ya es buena.

### Caso 2: "Definir un agente nuevo end-to-end"

- **Problema (MWT)**: crear un SKILL_AMAZON_X requiere editar 3-4 archivos (PLB para flow, SCH para output, SKILL para metadata, integration en otro lado).
- **Como MWT lo resuelve hoy**: changelog manual + sync_*_indexa.ps1.
- **Como nexos lo resuelve**: chat "describe what you want" -> bundle declarativo unico (Settings) + Flow narrativo opcional. Save y listo. El LLM genera system prompt, sugiere starters, sugiere flow steps.
- **Por que es mejor**: reduce friction de autoring. Para FaberLoom-clientes (que no son devs) este flujo es vital. Para MWT interno tambien acelera la iteracion.
- **Por que NO es mejor en todo**: nexos no obliga a declarar visibility ni grounding ni tenant_scope, lo cual rompe MWT. La adopcion debe **agregar restricciones MWT al patron nexos**, no replicarlo crudo.
- **Veredicto**: **ADAPTAR** via Delta D2 (SPEC_AGENT_BUNDLE) + Delta D5 (PLB_AGENT_AUTHORING). El bundle es bueno; el flow es bueno; las primitivas MWT se mantienen.

### Caso 3: "Que pasa si Anthropic cae a la mitad de una sesion B2B"

- **Problema (MWT)**: hoy, nada formalizado. Cada SKILL_ asume su modelo. Si Anthropic responde 529, el agent peta. Para Marluvas presentando en Bogota: catastrofe.
- **Como MWT lo resuelve hoy**: no lo resuelve. Retry manual.
- **Como nexos lo resuelve**: cada modelo en el registry tiene fallback chain ordenada. Gateway detecta failure y enruta al siguiente. Transparente al agent.
- **Por que es mejor**: simple, ya implementado, declarativo. No requiere LangGraph.
- **Por que es delicado**: fallback Anthropic -> OpenAI cambia tonalidad y puede romper SCH_ rigidos. Hay que validar que la fallback chain preserve capability (function calling, vision).
- **Veredicto**: **ADOPTAR** via Delta D4 (SPEC_LLM_GATEWAY_FALLBACK). Restringir fallbacks a modelos del mismo tier y misma capability. Documentar en SCH_ cuales son rigidos respecto al provider.

### Caso 4: "Memoria de KB con visibility per-archivo y permisos PARTNER_B2B"

- **Problema (MWT)**: necesidad real - distribuidores Marluvas en Colombia ven catalogo, no margenes; Tecmater en Mexico ve precios, no costo.
- **Como MWT lo resuelve hoy**: visibility por archivo en frontmatter + hooks fail-closed validan que CEO-ONLY no aparezca en archivos INTERNAL sin declaracion explicita. Granularidad de archivo.
- **Como nexos lo resuelve**: Project tiene files como bag plano. Permisos = "Shared with you" / "Created by you" a nivel agent. Sin granularidad de archivo. Sin clases de visibility como las MWT.
- **Por que MWT es mejor aqui**: visibility per-archivo + taxonomia + hooks fail-closed es mas estricto y necesario para B2B partner channel. nexos no podria, sin custom dev, separar lo que un distribuidor ve del CEO-ONLY.
- **Veredicto**: **DESCARTAR** el modelo nexos para KB de fondo. **Mantener MWT**. Posible uso: nexos como front-end "viewer" para socios que solo necesitan chat contra documentos PUBLIC/PARTNER_B2B - pero la KB canonica sigue siendo MWT.

### Caso 5: "Workflow agente con state machine"

- **Problema (MWT)**: ENT_OPS_STATE_MACHINE es FROZEN, global, complejo. Cada agent tiene su mini-state-machine implicita en su PLB_ via texto. No es visible al CEO en glance.
- **Como MWT lo resuelve hoy**: PLB_ con narrativa textual; ENT_OPS_STATE_MACHINE referenciado.
- **Como nexos lo resuelve**: Flow tab = Goal + Steps lineales con prompt narrativo embebido en cada step. Visual, expandible, editable por chat.
- **Por que es mejor**: legibilidad. Un agent tiene 3-5 steps visuales. CEO entiende en 30 segundos.
- **Por que NO es mejor del todo**: nexos Flow es lineal, sin conditionals visibles. Para agentes B2B con ramas (Marluvas: si stock < 30 dias entonces escalar a Brasil; sino procesar) hace falta extender el modelo.
- **Veredicto**: **ADAPTAR** via Delta D3 (SPEC_AGENT_FLOW). Agregar branching declarativo (`next_step_when`). Mantener ENT_OPS_STATE_MACHINE separado y FROZEN.

### Caso 6: "Integrar Amazon SP-API + Helium 10 a la arquitectura agentica"

- **Problema (MWT)**: stack Rana Walk depende de SP-API + Helium 10. Estos son nucleo, no opcion.
- **Como MWT lo resuelve hoy**: n8n + custom code, integrado en SKILL_ via tool wrappers.
- **Como nexos lo resuelve**: **NO los tiene**. 40+ integrations cubren Slack, Google, Microsoft, CRMs, PMs, Stripe, QB, dev tools - pero no Amazon SP-API ni Helium 10 ni ningun ERP LATAM.
- **Por que es peor**: para Rana Walk, nexos seria irrelevante sin custom MCP server propio. Para Marluvas/Tecmater igual: no hay integration con ERPs de calzado industrial.
- **Veredicto**: **DESCARTAR para nucleo MWT**. Si en algun momento Alvaro quiere usar nexos como cliente de chat enterprise para tareas horizontales (Google Workspace, Slack, CRM), bien. Pero no es plataforma operativa MWT.

---

## 4. OUTPUT 3 - Tabla comparativa MWT vs nexos

| Area | MWT actual | nexos.ai | Gap / oportunidad | Recomendacion |
|---|---|---|---|---|
| **Orquestacion** | PLB_ORCHESTRATOR (FROZEN) + ENT_OPS_STATE_MACHINE global; despacho por PLBs textuales; state machine implicita per-skill en prompt | Bundle declarativo per-agent + Flow narrativo (Goal + N Steps con prompt embebido) + Schedule trigger nativo | MWT no tiene shape canonico para agent; flow per-agent vive en texto; no hay scheduler declarativo | **Adoptar SPEC_AGENT_BUNDLE_v1 (D2) + SPEC_AGENT_FLOW_v1 (D3)**. Mantener ENT_OPS_STATE_MACHINE FROZEN intocado. Schedule declarativo per-skill en bundle |
| **KB / RAG / memoria** | Taxonomia estricta 8+ tipos, headers obligatorios, visibility per-archivo (PUBLIC/PARTNER_B2B/INTERNAL/CEO-ONLY), versioning git, hooks fail-closed | Projects = bag de files sin tags ni versioning; permisos a nivel project; Project Creativity 5-niveles como policy de grounding; memoria agent cross-thread | MWT no tiene primitiva de grounding policy explicita; nexos no tiene taxonomia ni visibility per-archivo | **Adoptar POL_GROUNDING_POLICY_v1 (D1)** con nomenclatura nexos. **Descartar** modelo bag-of-files; mantener taxonomia MWT |
| **UI agente** | No existe UI estandar de authoring; archivos .md editados a mano + Cowork/Claude Code | Chat-first creation + Studio panel (Try agent / Flow / Settings) + suggestion chips contextuales + Generate-with-AI para system prompt + Save/Discard binario | MWT no tiene patron de UI; FaberLoom va a necesitar uno. nexos da el patron base pero rompe contract 3-boton de Alvaro y no incluye "Sanidad" tab | **Adaptar via PLB_AGENT_AUTHORING_v1 (D5)**: chat-first + Studio con tabs Configurar/Iterar/Sanidad (mantener nomenclatura FaberLoom), suggestion chips, Generate-with-AI; conservar contract 3-boton (aprobar/descartar/iterar) |
| **Multi-tenancy + governance** | tenant_id NOT NULL via RLS source-of-truth; visibilidad granular; hooks fail-closed como control_surface; sync_*_indexa.ps1 con manifest selectivo; FROZEN protection; break-glass auditado | Workspace = tenant; Teams = sub-grupo; per-team model registry con fallback chain; audit logs platform-side; SOC 2/ISO/GDPR; no control_surface inmutable visible | MWT no tiene fallback chain declarativa por modelo. nexos no tiene control_surface protegido equivalente a hooks fail-closed | **Adoptar SPEC_LLM_GATEWAY_FALLBACK_v1 (D4)** para tabla de modelos con fallback chain. **Mantener** hooks fail-closed, RLS, manifest selectivo - son mas estrictos que nexos. **No adoptar** modelo Teams + RBAC simple |

---

## 5. Siguiente paso operativo (no es parte de los 3 outputs - separado)

Para promover esta auditoria a `docs/`:

1. Validar deltas D1-D5 con Alvaro. Probable feedback: priorizar D1 (POL_GROUNDING) + D4 (FALLBACK) primero - son los que mas valor inmediato dan sin tocar arquitectura existente.
2. Generar `sync_nexos_audit_indexa.ps1` con manifest de archivos seleccionados.
3. Append a `MANIFIESTO_CAMBIOS_v2` con BATCH `[ARQUITECTURA] auditoria nexos.ai + deltas D1-D5 propuestos`.
4. Crear stubs de los 5 SPEC/POL/PLB en `generated_staging/` antes de validar, no escribir directo a `docs/`.

## 6. Cosas que NO pude validar (PENDIENTE - NO INVENTAR)

- **Audit logs UI**: declarado en marketing, no visible en trial. [PENDIENTE - validar en sesion enterprise].
- **Memoria de agent cross-thread**: declarado, no probado por trial timeout. [PENDIENTE].
- **Branching real en Flow**: no vi conditionals en template Content Writer. Posible que en flows complejos (Process Visualizer, Investment Watcher) existan. [PENDIENTE - explorar 2-3 templates mas].
- **Permisos per-team granulares (mas alla de subset de Models)**: no vi roles per-team ni ACL sobre agents/projects. [PENDIENTE].
- **API/SDK shape**: AI Gateway declara unified API; no probe el SDK. Si MWT considera nexos como gateway al usar otros LLMs centralmente, hace falta ver el SDK. [PENDIENTE].
- **Pricing**: trial 7 dias sin pricing publico claro en UI. [PENDIENTE - consultar sales si la decision avanza].

## Changelog

- v1.0 (2026-05-17): documento inicial. Investigacion via Chrome MCP en workspace.nexos.ai (trial), tenant TitanPoint7515. 4 areas mapeadas. 5 deltas propuestos. 6 casos de uso analizados.
