# ENT_FB_TOOL_CATALOG_v1 — Catálogo de Tools y Conectores en FaberLoom
id: ENT_FB_TOOL_CATALOG_v1
version: 2.0.1
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: ENT
stamp: VIGENTE — 2026-04-29f (re-scope FB)
aprobador: CEO (sesión Cowork 2026-04-29c + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: SCH_FB_SKILL_MANIFEST_v2.md · SPEC_FB_AGENT_BUILDER_v1.md · ENT_FB_TEMPLATE_LIBRARY_v1.md

---

## Declaración

Catálogo inicial de **tools (capacidades externas)** disponibles para que los agents en la plataforma FaberLoom los importen vía `tools_mcp[]`. Distingue claramente las 3 categorías que un agent puede combinar:

- **Tools** (este documento) → capacidades externas tipo APIs (Gmail, SP-API, Drive, ERPs)
- **Skills** (ver `ENT_FB_TEMPLATE_LIBRARY_v1`) → paquetes de comportamiento reutilizable (humanize_comms, brand_voice)
- **Files/Memory** → estado persistente (memory, gold samples)

**No mezclar las 3 categorías.** OpenAI Workspace Agents las separa visualmente; FaberLoom las separa en el manifest v2.

**Origen del primer set:** los tools nativos del catálogo inicial fueron escogidos para cubrir las necesidades del primer tenant beta (MWT/Rana Walk) — Amazon SP-API, Helium 10, Gmail, Google Drive, n8n connectors. Tenants verticales nuevos (fabricantes industriales B2B) agregarán tools propios al catálogo: SAP B1, Bind ERP, Aspel, Siigo, Microsip, etc. El catálogo es **extensible per-tenant** vía registro central + permission scopes.

---

## Tools nativos (con MCP wrapper) en FB v1 (set del primer tenant MWT)

| Tool ID | Función | Categoría | Permission default |
|---------|---------|-----------|---------------------|
| `amazon_sp_api_reviews` | leer/markar reviews Amazon FBA | read + write | per-tool |
| `amazon_sp_api_inventory` | leer inventario, FBA shipments | read | per-tool |
| `amazon_sp_api_listings` | leer/escribir listings (titles, bullets, A+ Content) | read + write con approval | per-tool, write requires_approval |
| `helium10_keywords` | research keywords ASIN | read | per-tool |
| `helium10_tracker` | tracker rankings históricos | read | per-tool |
| `gmail_search` | buscar emails inbox B2B | read | per-tool |
| `gmail_send` | enviar emails (drafts only sin approval) | write | requires_approval |
| `gdrive_search` | buscar archivos en Drive | read | per-tool |
| `gdrive_write_doc` | crear/editar Google Doc | write | requires_approval para writes |
| `slack_post` | postear en canal Slack | write | per-channel permission |
| `slack_thread_reply` | responder en thread existente | write | per-channel permission |
| `crm_marluvas_portal` | leer/escribir CRM Marluvas | read + write con approval | per-account |
| `sap_b1_distribution` | leer datos SAP B1 distribución (Marluvas/Tecmater) | read | per-tool |
| `web_search` | búsqueda web genérica | read | unrestricted |
| `web_fetch` | fetch URL específica | read | unrestricted, content filtering |

Cada tool tiene MCP wrapper en `mwt-knowledge/tools/<tool_id>.py` o como sub-proceso stdio según complejidad.

---

## Custom MCP slot (NUEVO — D16 + observación CEO)

Inspirado en el catálogo Workspace Agents OpenAI ("Custom MCP" como entrada del tool picker). Permite registrar MCP servers custom a través del builder UI sin tocar código:

```yaml
# manifest del agent que usa custom MCP
tools_mcp:
  - id: my_custom_mcp_server
    kind: custom
    endpoint: https://mcp.miempresa.com/v1
    auth_method: bearer
    auth_token_ref: $MCP_CUSTOM_TOKEN     # variable de entorno
    schema_url: https://mcp.miempresa.com/v1/schema.json
    permission_model: per-call
    rate_limit_per_min: 60
```

Catálogo central de Custom MCPs registrados vive en `ENT_PLAT_ACTION_REGISTRY` (ya existe en repo MWT — extender con sección "Custom MCPs" cuando aplique).

---

## n8n como bridge entre conector y agent (D16)

n8n NO es un tool del agent — es un **conector** (capa antes del agent). Pero los workflows n8n se referencian desde el manifest del agent via `triggers[].connector_workflow_id`:

```yaml
triggers:
  - kind: webhook
    source: gmail
    connector: n8n
    connector_workflow_id: gmail_b2b_watcher_v1
    # n8n hace: detect + extract + POST
    # NO clasifica, NO decide, NO transforma de negocio
```

n8n workflows versionados en n8n con naming convención: `<source>_<purpose>_v<N>` (ej: `gmail_b2b_watcher_v1`, `slack_software_requests_v2`).

Reglas operacionales para workflows n8n (D16):

| Regla | Por qué |
|-------|---------|
| ≤ 5 nodes por workflow | si pasa, hay lógica que debería estar en el agent |
| Sin nodes OpenAI/Claude/LLM | LLM solo en agent vía LiteLLM |
| Switch nodes solo para tipos de evento | no para lógica de negocio |
| Output siempre a endpoint Django builder | no a APIs externas directamente |

---

## Distinción Tools vs Skills vs Files (D18)

| Categoría | Qué es | Ejemplos | Cuándo agregarlo al agent |
|-----------|--------|----------|----------------------------|
| **Tools** | capacidad externa con API estructurada | Gmail send, SP-API write, Drive search | el agent necesita interactuar con el mundo exterior |
| **Skills** | paquete de comportamiento reutilizable (frontmatter agentskills.io) | humanize_comms, brand_voice, claims_scanner | el agent necesita "cómo se hace X" — generación con voz, validación específica, etc. |
| **Files/Memory** | estado persistente leído/escrito en runtime | memory.json, gold_samples/, conversation_history | el agent necesita recordar entre invocaciones |

Regla: si una capacidad es **stateless funcional** y reutilizable → Skill. Si requiere **acceso a sistema externo** → Tool. Si requiere **persistir estado** → Files/Memory.

Ejemplo concreto del agent SKILL_RW_REVIEW_TRIAGE:
- **Tools**: `amazon_sp_api_reviews` (read), `gmail_send` (write con approval)
- **Skills**: `humanize_comms` (voz CEO), `brand_voice_rw` (voz Rana Walk)
- **Files/Memory**: `gold_samples/review_response_2026_03.md`, episodic_memory de runs anteriores

Tres categorías, cada una con su rol claro.

---

## Pricing y costo de tools

Algunos tools tienen costo monetario directo (Helium 10, Gmail Workspace, SAP) — el costo NO va al budget del agent (es licenciamiento separado en MWT). Otros son gratuitos (Web search via Brave/DuckDuckGo).

Lo que sí cuenta para el budget del agent:
- Tokens del LLM cuando interpreta resultados de tool calls
- Latencia (impacta budget de tiempo del agent)

---

## Tools que NO se agregan al catálogo en MWT v1

| Tool potencial | Por qué NO ahora |
|----------------|------------------|
| GitHub API | no aplica al caso de operación MWT (no son developers) |
| Image generation (DALL-E, Midjourney) | no hay caso de uso B2B/FBA que lo justifique |
| Voice synthesis | no hay caso de uso B2B audio |
| Linear / Jira | no usás esos sistemas |
| Calendly | si la operación lo necesita, agregar; hoy no |
| Stripe / Mercado Pago | facturación no pasa por agents v1 |

Cuando un caso de uso real lo justifique, se agrega al catálogo + MCP wrapper.

---

## Cómo agregar un tool nuevo

1. Identificar caso de uso real (un agent existente lo necesita)
2. Diseñar MCP wrapper en `mwt-knowledge/tools/<tool_id>.py`
3. Definir input/output schema con Pydantic v2
4. Declarar en `ENT_PLAT_ACTION_REGISTRY` (registry vivo de actions disponibles)
5. Agregar entry en este catálogo (`ENT_TOOL_CATALOG_V1`)
6. Hacer disponible en el builder UI (Custom MCP slot del catálogo)
7. Test e2e con un agent que lo importa
8. Commit + indexa pequeña

---

## Auditoría de tools por agent

El builder permite auditar qué agents usan cada tool:

```bash
mwt audit --type=tool_usage
# Output:
# amazon_sp_api_reviews: usado por 2 agents (REVIEW_TRIAGE, AMAZON_OPS)
# gmail_send: usado por 3 agents (REVIEW_TRIAGE, LEAD_QUALIFIER, CLIENT_SERVICE)
# helium10_keywords: usado por 1 agent (LISTING_OPT)
# ...
```

Útil para:
- Decisiones de licenciamiento (¿vale Helium 10 si solo 1 agent lo usa poco?)
- Patch broadcast (cuando un tool cambia versión o falla)
- Compliance (qué agents tocan datos sensibles)

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29c): creación con scope MWT-only erróneo. Catálogo inicial de tools nativos (15) con permission defaults. Custom MCP slot inspirado en demo Workspace Agents OpenAI Tally. Distinción Tools/Skills/Files explícita (D18). Reglas operacionales para n8n workflows (D16).
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado ENT_TOOL_CATALOG_V1 → ENT_FB_TOOL_CATALOG_v1. Los 15 tools del catálogo inicial son del primer tenant MWT; tenants verticales futuros agregarán tools propios (ERPs LATAM: SAP B1, Bind, Aspel, Siigo, Microsip, etc.). Catálogo extensible per-tenant vía registro central + permission scopes. Aprobador: CEO sesión re-scoping 2026-04-29f.**
- v2.0.1 (2026-06-23, FB-STD-CODEX-2026-06-23-01): fix mecánico de ref legacy `ENT_TEMPLATE_LIBRARY_v1.md` → `ENT_FB_TEMPLATE_LIBRARY_v1.md` en metadata relacionado.
