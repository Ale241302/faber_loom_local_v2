# PLAN_DESARROLLO_FABERLOOM_ETAPA9_v1 — Ecosistema e integraciones

id: PLAN_FB_ETAPA9
version: 1.0.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLAN
stamp: VIGENTE — 2026-07-12 — plan de la Etapa 9: abrir la plataforma hacia afuera — API pública, webhooks, DMS, agentic commerce y packs por demanda
aprobador: CEO
relacionado: PLAN_FB_ROADMAP_E5_E10_v1 · SPEC_FB_INTEGRATION_LAYER_v1 · SPEC_FB_EVENTING_AND_OUTBOX_v1 · SPEC_FB_DMS_INTEGRATION_v1 · ENT_PLAT_AGENTIC · POL_FABERLOOM_SURFACE_CONTRACT · ENT_FB_WORK_TYPE_PACK_v1

**Cláusula de re-validación:** v1.1 antes de arrancar con la demanda REAL de integraciones de los tenants de E6-E8 — el orden de las olas 2-3 lo deciden los clientes, no el plan.

---

## §0. Naturaleza y decisiones

E9 convierte a FaberLoom de aplicación en plataforma: otros sistemas leen, escriben y se enteran. Todo lo expuesto respeta el contrato de superficie (`POL_FABERLOOM_SURFACE_CONTRACT`) y la seguridad heredada — la API pública es OTRA puerta a las MISMAS reglas, jamás un bypass.

**Decisiones del Arquitecto:**
- **DA9-1. API pública v1: subconjunto curado, versionado por ruta (`/api/v1/`)**, con API keys por tenant con scopes (`read:kb`, `write:tasks`, `read:invoices`...). Las keys son secretos en `TenantSecretStore` (hash en DB, valor mostrado una vez), creadas por el owner con límite por plan. La API interna actual NO se congela: `/api/v1/` es la fachada estable.
- **DA9-2. Webhooks salientes sobre el outbox (M15)** — el mismo bus que alimenta el SSE de E8-2: un solo emisor de eventos, dos transportes (SSE para la UI, webhooks para sistemas). Firma HMAC por endpoint suscriptor, reintentos con backoff, y draft-first NO aplica (son notificaciones de hechos ya ocurridos y aprobados — no efectos nuevos).
- **DA9-3. Agentic commerce: MCP server propio** según `ENT_PLAT_AGENTIC` §C1, exponiendo herramientas read-only + creación de drafts (jamás ejecución externa directa): un agente externo (Claude, etc.) puede consultar catálogo/estado y PROPONER — el HITL del tenant decide. Rol `AI_AGENT` de la spec con permisos mínimos.
- **DA9-4. Pasarela de pago: decisión con datos de E6.** Si ≥30% de facturas se pagan tarde por fricción de transferencia, se integra pasarela (candidata por costos LATAM a evaluar en el hito, `[PENDIENTE — decisión de negocio con datos]`); si no, transferencia+PACK 3 sigue. El hito E9-5 hace la evaluación formal, no presupone la respuesta.
- **DA9-5.** Packs 4-13: se promueven POR DEMANDA de tenants reales (un pack sin usuario es inventario muerto); la fábrica opera como servicio con SLA interno de 2 semanas definición→SHADOW. Rama `e9-ecosistema`.

## §1. Mapa de olas

| Ola | Hitos |
|---|---|
| 1 | E9-0 (API pública + keys), E9-1 (webhooks/outbox) |
| 2 | E9-2 (DMS), E9-3 (MCP/agentic) — orden según demanda real |
| 3 | E9-4 (packs por demanda), E9-5 (evaluación pasarela) |
| 4 | E9-6 (acta) |

## §2. Detalle por hito

### E9-0 — API pública v1 con API keys y scopes

**Objetivo:** un sistema externo del tenant opera contra FaberLoom con credenciales propias, permisos mínimos y límites.

**Tareas:**
1. **Auth de API:** tabla `api_key` (migración vN, campos latentes+RLS): tenant_id, nombre, hash (argon2), scopes JSON, last_used_at, revoked_at. Middleware `require_api_key(scopes)` que resuelve Context desde la key (tenant fijo; user = service principal `api:{key_id}` con rol acotado). Rate limit por key (reusar `rate_limit.py`), cuota por plan (E6-0 features).
2. **Superficie v1 (curada, no espejo):** `GET /api/v1/workspaces`, `GET /api/v1/workspaces/{id}/brief`, `GET/POST /api/v1/kb/search|documents`, `POST /api/v1/tasks` (crea agent_task PLANNED — la ejecución respeta autonomía/HITL del tenant), `GET /api/v1/tasks/{id}`, `GET /api/v1/invoices`, `GET /api/v1/workloom/items`, `POST /api/v1/workloom/items/{id}/approve` (con confirmation_token — el HITL puede venir del sistema del cliente, el token sigue siendo obligatorio). NADA de endpoints de admin/platform por API key.
3. **Contrato publicado:** OpenAPI generada y curada para v1 (`/api/v1/openapi.json`) + `docs/faberloom/SCH_FB_API_PUBLIC_V1.md` (guía con ejemplos, versionado y política de deprecación: 6 meses de aviso).
4. UI: gestión de keys por el owner (crear con scopes, ver last_used, revocar) en tenant_settings.

**Archivos:** `app/src/public_api.py` (router v1), `models.py`, `postgres_rls_policies.sql`, `tenant_settings.jsx` (o vista Vite equivalente post-E8), doc SCH.
**Tests:** `test_e9_0_api_keys.py` (hash, revocación inmediata, scopes fail-closed, rate limit, cuota por plan), `test_e9_0_api_isolation.py` (key de tenant A jamás toca B — el crítico), `test_e9_0_api_hitl.py` (task por API respeta HITL; approve exige token).
**DoD:** un script externo de prueba completa el ciclo: buscar KB → crear task → esperar → aprobar → leer resultado. **Esfuerzo:** 3 sesiones Fugu.

### E9-1 — Webhooks salientes (outbox M15 completo)

**Objetivo:** los sistemas del tenant se enteran de los hechos sin poll.

**Tareas:**
1. Completar el outbox según `SPEC_FB_EVENTING_AND_OUTBOX_v1`: tabla `outbox_event` (si el M15 actual es parcial — verificar primero) con orden garantizado por agregado, y worker de despacho (proceso del ciclo del backend, no del ambiental: es fontanería, no agente).
2. Suscripciones: tabla `webhook_subscription` (tenant_id, url, secret HMAC, event_types JSON, active) gestionada por el owner (UI + API v1). Eventos disponibles: los mismos tipos del SSE de E8-2 + `invoice.sent/paid`, `task.completed`, `pack.promoted`.
3. Entrega: POST firmado (`X-Faberloom-Signature: sha256=...`), timeout 10s, reintentos 5x con backoff exponencial, circuit breaker por endpoint (10 fallos seguidos → suspensión + item WorkLoom al owner). Payload: hecho + ids, NUNCA contenido completo de documentos (el receptor usa la API v1 con su key para leer — así los scopes gobiernan siempre).
4. Log de entregas consultable por el owner (últimas 100, estado, reintentos).

**Archivos:** `app/src/webhooks_out.py`, `foundation/m15_outbox_streams.py` (completar), `models.py` (migraciones), UI de suscripciones.
**Tests:** `test_e9_1_webhook_delivery.py` (firma, reintentos, breaker), `test_e9_1_webhook_isolation.py` (eventos solo del propio tenant), `test_e9_1_payload_minimal.py` (sin contenido, solo hechos+ids).
**DoD:** el sistema de prueba del design partner (o un endpoint de test) recibe eventos firmados de su tenant en vivo. **Esfuerzo:** 2-3 sesiones Fugu.

### E9-2 — Integración DMS

**Objetivo:** los documentos que viven en el DMS del cliente entran al flujo (KB, evidencia, tasks) sin migración forzada.

**Tareas:**
1. Implementar sobre `SPEC_FB_DMS_INTEGRATION_v1` el conector genérico: `app/src/connectors/dms_base.py` (interfaz: list, fetch, metadata, watch por polling delta) + primer adaptador según demanda real del tenant que lo pida (candidatos de la spec; la elección del primer DMS es dato de demanda — el hito arranca cuando exista, DA9-5 aplica).
2. Ingesta: documento del DMS → pipeline KB existente (`assert_safe_kb_source`, clasificación L1, injection guard) con `source_version` = ref del DMS; re-sync detecta cambios (hash) y propone re-ingesta como item WorkLoom (no automática — el conocimiento cambia con gate).
3. Credenciales del DMS por tenant en `TenantSecretStore` (namespace `connectors/dms/`), fail-closed.

**Tests:** `test_e9_2_dms_connector.py` (contra adaptador mock: list/fetch/delta), `test_e9_2_dms_ingest_gate.py` (re-ingesta propone, no ejecuta; injection guard activo).
**DoD:** un tenant real navega y trae documentos de su DMS a su KB con citas verificables. **Esfuerzo:** 2-3 sesiones Fugu (por adaptador).

### E9-3 — Agentic commerce: MCP server y rol AI_AGENT

**Objetivo:** agentes de IA externos (de los clientes del tenant, o del propio tenant) operan contra FaberLoom por un canal diseñado para agentes — proponiendo, jamás ejecutando.

**Tareas:**
1. MCP server (`app/src/mcp_server.py`, transporte HTTP/SSE estándar MCP) autenticado con API keys de E9-0 restringidas al rol `AI_AGENT` (ENT_PLAT_AGENTIC §D3): scopes de solo-lectura + `propose:*`.
2. Herramientas expuestas v1: `search_kb`, `get_workspace_brief`, `list_open_invoices` (agregados), `propose_task` (crea agent_task PLANNED con marca `origin=ai_agent` — SIEMPRE pasa por el HITL del tenant, sin excepción de autonomía: origen agente externo = techo L1), `get_task_status`.
3. Filtros contextuales de la spec (§D1): lo que un AI_AGENT ve está además filtrado por las reglas B2B del tenant (precios/condiciones según el contexto del cliente final — usar la matriz de `ENT_FB_COMMERCIAL_AUTHORITY_MATRIX`).
4. Registro y auditoría: toda llamada MCP → audit con correlation_id + panel de actividad de agentes externos para el owner.
5. Doc: `docs/faberloom/SCH_FB_MCP_SERVER_V1.md` (herramientas, auth, límites, ejemplos con Claude).

**Tests:** `test_e9_3_mcp_tools.py` (contratos de cada tool), `test_e9_3_ai_agent_ceiling.py` (origen ai_agent nunca supera L1; propose jamás ejecuta — el test sagrado del hito), `test_e9_3_mcp_isolation.py`.
**DoD:** una sesión de Claude con la key AI_AGENT de un tenant de prueba consulta el brief y propone una task que aparece en WorkLoom para aprobación. **Esfuerzo:** 3 sesiones Fugu.

### E9-4 — Fábrica como servicio: packs 4-13 por demanda

**Objetivo:** cada pack que un tenant real necesita pasa de DRAFT a SHADOW a ACTIVE con SLA interno.

**Tareas:**
1. Proceso operativo (no código nuevo — la fábrica de E3-4 está completa): solicitud de tenant → sesión de definición (needs-list del pack, patrón E5-3) → materialización SHADOW (≤2 semanas SLA) → dogfood/golden con el tenant → promoción por readiness.
2. Código menor: vista "Packs disponibles" para el owner (catálogo global con estado por pack y botón "solicitar" → item para el equipo) + `pack_request` en el registro de actividad.
3. Objetivo de la etapa: ≥3 packs adicionales ACTIVE en tenants reales (los que la demanda elija — no forzar).

**Tests:** `test_e9_4_pack_request.py` (solicitud crea el flujo; aislamiento).
**DoD:** ≥3 packs nuevos ACTIVE en producción con golden cases reales de sus tenants. **Esfuerzo:** ½ sesión Fugu + operación continua.

### E9-5 — Evaluación formal de pasarela de pago

**Objetivo:** decidir con datos si el cobro necesita pasarela (DA9-4).

**Tareas:** análisis de la cartera E6-E9 (días-a-pago, tasa de vencidas, fricción reportada); si el umbral se cruza: spike de 1 semana con la candidata elegida (sandbox), diseño de integración (webhook de pago → conciliación automática al flujo existente) y decisión CEO documentada en `DEC_FB_PASARELA_PAGO_v1.md`; si no se cruza: decisión de continuar transferencia+PACK 3 documentada igual (una decisión de NO hacer también se archiva).
**DoD:** DEC commiteada con los números que la sustentan; si aplica, plan de integración listo para E10 o banda paralela. **Esfuerzo:** 1 sesión análisis + spike condicional.

### E9-6 — Acta

Contamination + arena + suite verdes (la contamination ahora incluye API keys, webhooks y MCP); `docs/audits/ACTA_ETAPA9_<fecha>.md`; merge a main + tag `e9-cierre`; SCH/SPEC as-built actualizados con changelog; bloques KB.

## §3. Riesgos P0

| Riesgo | Mitigación |
|---|---|
| La API pública se vuelve bypass de HITL/RLS | Fachada sobre las MISMAS funciones internas (jamás SQL propio); tests de aislamiento y HITL por endpoint; scopes fail-closed |
| Webhook filtra contenido | Payload = hechos+ids; el contenido siempre se lee por API con scopes |
| Agente externo ejecuta algo | Techo L1 estructural para origen ai_agent (test sagrado); propose-only |
| Key comprometida | Hash en DB, revocación inmediata, rate limit, last_used visible, rotación documentada |
| Integraciones abren deuda de soporte | Cada integración expuesta entra al SLA de E6-5 con su runbook |

## §4. Gate de salida

API v1 estable con ≥2 integraciones reales de tenants operando; webhooks entregando en producción; ≥3 packs adicionales ACTIVE; MCP demostrado con un agente real; DEC de pasarela archivada; acta commiteada.

## Changelog

- v1.0.0 (2026-07-12): Creación. Decisiones DA9-1..DA9-5; principio "otra puerta a las mismas reglas".
