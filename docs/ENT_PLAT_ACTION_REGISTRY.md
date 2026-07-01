# ENT_PLAT_ACTION_REGISTRY — Catálogo de Acciones del Sistema
id: ENT_PLAT_ACTION_REGISTRY
version: 1.1
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: ENT
stamp: VIGENTE — 2026-04-28
aprobador: CEO (delegado al Arquitecto Cowork)
aplica_a: [MWT, FaberLoom]
relacionado: SPEC_ACTION_ENGINE.md (D9) · SCH_ACTION_SPEC.yaml (v1.1) · SPEC_LLM_ROUTING_ARCHITECTURE.md · POL_DATA_CLASSIFICATION.md

---

## Declaración

Catálogo vivo de todas las acciones registrables en el Action Engine. Cada entrada cumple `SCH_ACTION_SPEC.yaml`. Este archivo es la **vista humana** del Capability Map; la implementación machine-readable vive en `mwt_action_engine/registry/*.yaml` (sem 3+).

**Estado actual: catálogo inicial (sem 1-2 del roadmap).** Las acciones listadas son las que el sistema USA HOY, aunque la implementación del Engine que las consuma está en sem 3.

---

## Inventario por categoría

### llm_provider — Modelos de lenguaje

DPA disponible = puede procesar N2-N4. Sin DPA = solo N0/N1 con cost-mode opt-in (D9).

| action_id | Provider | Tier hint | $ in/out per 1M | DPA LATAM | accepts_data_class | Estado |
|---|---|---|---|---|---|---|
| `llm.claude_opus_47` | Anthropic | calidad | $5 / $25 (⚠️ tokenizer +35% efectivo) | ✅ | N0-N4 | activo |
| `llm.claude_sonnet_46` | Anthropic | calidad | confirmar pricing actual | ✅ | N0-N4 | activo |
| `llm.haiku_45` | Anthropic | carpenteria | confirmar pricing actual | ✅ | N0-N4 | activo |
| `llm.gpt_55` | OpenAI | calidad | $5 / $30 | ✅ | N0-N4 | activo |
| `llm.gpt_55_pro` | OpenAI | calidad | $30 / $180 | ✅ | N0-N4 | activo |
| `llm.gpt_55_mini` | OpenAI | carpenteria | [PENDIENTE — verificar variante "mini"] | ✅ | N0-N4 | candidato |
| `llm.gemini_31_pro` | Google | calidad | $2 / $12 | ✅ | N0-N4 | activo |
| `llm.gemini_25_flash` | Google | carpenteria | $0.075 / $0.30 (con grounding nativo) | ✅ | N0-N4 | activo |
| `llm.deepseek_v4_pro` | DeepSeek | calidad | $1.74 / $3.48 (75% off hasta 2026-05-05) | ❌ | N0-N1 (cost-mode) | activo |
| `llm.deepseek_v4_flash` | DeepSeek | carpenteria | $0.14 / $0.28 | ❌ | N0-N1 (cost-mode) | activo |
| `llm.kimi_k2_6` | Moonshot AI managed | carpenteria/calidad | API managed [PENDIENTE pricing] | ❌ | N0-N1 (cost-mode) | activo |
| `llm.kimi_k2_6_self` | Self-host MIT | carpenteria/calidad | self-host $1500/mes 2×H100 estimado | ✅ (DPA propio) | N0-N4 | candidato |
| `llm.kimi_k2_6_swarm` | Moonshot AI managed | calidad | swarm 300 sub-agents [PENDIENTE pricing] | ❌ | N0-N1 (cost-mode) | activo |

**Nota crítica:** los pricing marcados con `confirmar pricing actual` o `[PENDIENTE]` requieren WebSearch antes de comprometer Routing Policy. Memoria CEO indica que mi knowledge cutoff es may-2025 — verificar abril 2026 antes de cementar.

### data_api — APIs de datos

| action_id | Provider | Side effects | Estado |
|---|---|---|---|
| `api.amazon_sp_api` | Amazon | reversible | activo (Rana Walk) |
| `api.helium_10` | Helium 10 | none | activo (Rana Walk) |
| `api.supabase_query` | Supabase | reversible | activo |
| `api.dian_consulta` | DIAN Colombia | none (read-only) | candidato (FaberLoom) |
| `api.sat_consulta` | SAT México | none (read-only) | candidato (FaberLoom) |
| `api.sii_consulta` | SII Chile | none (read-only) | candidato (FaberLoom) |
| `api.sefaz_consulta` | SEFAZ Brasil | none (read-only) | candidato (FaberLoom) |
| `api.afip_consulta` | AFIP Argentina | none (read-only) | [PENDIENTE — schema confirmado en Kimi #3 SIN DATOS] |

### communication_api — Comunicación

| action_id | Provider | Side effects | Estado |
|---|---|---|---|
| `comm.gmail_send` | Google | irreversible | candidato |
| `comm.gmail_search` | Google | none | candidato |
| `comm.whatsapp_business_send` | Meta | irreversible | candidato (FaberLoom MVP) |
| `comm.whatsapp_business_template` | Meta | irreversible | candidato (FaberLoom MVP) |
| `comm.slack_send` | Slack | irreversible | candidato |

### tool_local — Herramientas locales

| action_id | Descripción | Side effects | Estado |
|---|---|---|---|
| `tool.regex_extract` | Tier 0 deterministic — regex extraction | none | activo (Faberloom Tier 0) |
| `tool.xml_parse_dian` | Parser XML UBL 2.1 Colombia | none | activo (Faberloom Tier 0) |
| `tool.xml_parse_sat` | Parser XML CFDI 4.0 México | none | activo (Faberloom Tier 0) |
| `tool.xml_parse_sii` | Parser XML DTE Chile | none | activo (Faberloom Tier 0) |
| `tool.xml_parse_sefaz` | Parser XML NFe 4.00 Brasil | none | activo (Faberloom Tier 0) |
| `tool.pydantic_validate` | Validation con Pydantic v2 | none | activo |
| `tool.bash_execute` | Shell execution sandboxed | reversible | activo (MWT) |
| `tool.python_execute` | Python execution sandboxed | reversible | activo (MWT) |
| `tool.file_read` | Lectura de archivo local | none | activo |
| `tool.file_write` | Escritura de archivo local | reversible | activo |

### tool_browser — Control de navegador / desktop

| action_id | Descripción | Side effects | Estado |
|---|---|---|---|
| `tool.computer_use_screenshot` | Screenshot del desktop | none | activo (Cowork) |
| `tool.computer_use_click` | Click en coordenadas | reversible | activo |
| `tool.computer_use_type` | Typing en input activo | irreversible | activo |
| `tool.claude_in_chrome_navigate` | Navegación en Chrome MCP | reversible | activo |
| `tool.claude_in_chrome_form_input` | Llenar form en Chrome | reversible | activo |

### mcp_server — MCPs registrados

| action_id | MCP | Estado |
|---|---|---|
| `mcp.search_registry` | mcp-registry | activo |
| `mcp.suggest_connectors` | mcp-registry | activo |
| `mcp.search_plugins` | plugins | activo |
| `mcp.suggest_plugin_install` | plugins | activo |
| `mcp.create_scheduled_task` | scheduled-tasks | activo |
| `mcp.cowork_create_artifact` | cowork | activo |
| `mcp.cowork_list_artifacts` | cowork | activo |
| `mcp.workspace_bash` | workspace | activo |
| `mcp.workspace_web_fetch` | workspace | activo |

### kb_access — Acceso a Knowledge Base

| action_id | Descripción | Side effects | Estado |
|---|---|---|---|
| `kb.pgvector_retrieve` | Retrieval semántico vía pgvector | none | activo |
| `kb.pgvector_write` | Escritura vectorizada | reversible | activo |
| `kb.read_file` | Lectura directa de archivo KB | none | activo |
| `kb.search_grep` | Búsqueda regex en KB | none | activo |

---

## Total inventariado

```
llm_provider:        12 (activo: 11, candidato: 1)
data_api:             8 (activo: 3, candidato: 5)
communication_api:    5 (activo: 0, candidato: 5)
tool_local:          10 (activo: 10)
tool_browser:         5 (activo: 5)
mcp_server:           9 (activo: 9)
kb_access:            4 (activo: 4)
─────────────────────────
TOTAL:               53 acciones (47 activo, 6 candidato)
```

---

## Acciones a registrar antes de FaberLoom MVP

Por orden de prioridad para sem 3-9:

| # | Acción | Bloqueador potencial |
|---|---|---|
| 1 | `tool.xml_parse_*` (5 países LATAM) | Validación contra muestras reales — spot-check pendiente |
| 2 | `comm.whatsapp_business_*` | API Business approval Meta — registro empresa |
| 3 | `llm.haiku_45` con confirmation pricing | Verificar pricing actual abril 2026 |
| 4 | `llm.claude_sonnet_46` (integrador MEDIUM) | Verificar pricing |
| 5 | `kb.pgvector_retrieve` con RLS multi-tenant | Validar pgvector ≥0.8.0 en Supabase |
| 6 | `api.dian_consulta` y equivalentes | Acceso a credenciales por país |

---

## Pricing pendientes de verificar (knowledge cutoff Cowork mayo 2025)

Antes de cementar Routing Policy con costos, validar via WebSearch:

| Modelo | Pricing actual conocido | Acción |
|---|---|---|
| Haiku 4.5 | confirmar | WebSearch antes de Fase 2 |
| Claude Sonnet 4.6 | confirmar | WebSearch antes de Fase 2 |
| Kimi K2.6 API managed | desconocido | Verificar provider (Cloudflare Workers AI mencionado) |
| Kimi K2.6 self-host | ~$1500/mes 2×H100 estimado | Validar con quote real GPU provider |
| GPT-5.5 mini | desconocido si existe variante | OpenAI docs |

---

## Cómo se llena este registro (proceso)

```
1. Cada vez que un skill / agente usa una nueva acción:
   - Agregar entrada en este archivo
   - Llenar SCH_ACTION_SPEC.yaml correspondiente en mwt_action_engine/registry/
   - Update changelog

2. Cuando una acción se deprecia:
   - Marcar deprecated_in en SCH_ACTION_SPEC
   - Documentar replaces / replacement
   - Sunset 2 versiones major después (D4)

3. Cuando un provider cambia pricing:
   - Update performance.cost_per_call_usd
   - Trigger ModelFingerprint check (si LLM)
   - Notificar Adaptive Tuner (sem 10+)

4. Auditoría trimestral:
   - Verificar que cada action_id activo tiene tráfico real en OutcomeLedger
   - Acciones sin uso 90 días → candidate to deprecate
```

---

## Limitaciones v1.0

| Limitación | Mitigación |
|---|---|
| Inventario manual | Acceptable v1; automatización via introspection en v2 |
| Pricing depende de docs externas | Verificación pre-Fase 2 via WebSearch obligatorio |
| Algunos `[PENDIENTE]` y "candidato" | Resolver durante sem 3-9 a medida que se implementan |
| 53 acciones es sólo el snapshot — crece con cada skill nuevo | Expected. Mantener disciplina de registry-first |

---

Changelog:
- v1.1 (2026-04-28): +columnas DPA LATAM y accepts_data_class por LLM provider. Self-host Kimi K2.6 separado como `llm.kimi_k2_6_self` (DPA propio, N0-N4). Distinción crítica para D9 enforcement: providers sin DPA managed solo aceptan N0/N1 con cost-mode opt-in.
- v1.0 (2026-04-28): Creación. Inventario inicial 53 acciones (47 activo, 6 candidato). Pricing parcial pendiente de WebSearch pre-Fase 2.
