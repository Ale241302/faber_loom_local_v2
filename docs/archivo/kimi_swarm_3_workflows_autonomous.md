# FaberLoom Runtime — Síntesis Final Ejecutable

> **Investigación:** 9 dimensiones · 200+ búsquedas · 7,643 líneas de evidencia
> **Fecha de síntesis:** 2026-04-22
> **Autor:** Arquitecto de Software — Consolidación Multi-dimensional
> **Output para:** SPEC_WORKFLOW_ENGINE_v1 · SPEC_AGENT_COMPOSITION_v1.1 · Templates · Roadmap Sprint 1-4

---

## SECCIÓN 1: Stack Técnico Final Recomendado

| Componente | Herramienta recomendada | Licencia | Costo mensual | Justificación | Quién lo implementa | Sprint |
|---|---|---|---|---|---|---|
| **Motor workflow Fase 1** | **pg-boss** (npm package sobre Postgres) | MIT | $0 (usa Postgres existente) | 3.4k stars, último release Mar 2026. SKIP LOCKED exactly-once. Cero infra adicional. Curva mínima. Para jobs simples <1s sin sleep/wait. | Backend eng | S1 |
| **Motor workflow Fase 2** | **Inngest self-hosted** (single binary + Postgres) | Apache 2.0 (SDKs) / SSPL (server) | $0 (mismo servidor) | 5.2k stars, último release Apr 2026. Durable execution: step.sleep(1año), step.waitForEvent(), checkpointing automático. Versionado sin migración manual. Agregado solo cuando se necesiten sleeps largos y HITL. | Backend eng | S3-S4 |
| **DSL/Builder Fase 1** | **YAML declarativo** (CNCF Serverless Workflow DSL) + hardcoded templates | N/A | $0 | No hay builder visual en Fase 1. Templates YAML hardcodeados en DB. Source-of-truth en Postgres. Serializable, versionable, LLM-generable. | Backend eng | S1 |
| **DSL/Builder Fase 2** | **React Flow** (36.3k stars, MIT) + YAML bidireccional | MIT | $0 | Librería visual dominante. Canvas tipo Make/n8n. 53.3 kB gzip. TypeScript nativo. Equipo full-time en Berlin. Simplificar para perfil no-técnico 45+. | Frontend eng | S5+ (post-beta) |
| **Runtime durable execution** | **Checkpointing pg-boss** (F1) + **Inngest step memoization** (F2) | — | $0 | pg-boss: estado en Postgres con RLS. Inngest: cada step persiste resultado automáticamente. Workflows dormidos no consumen compute. | Backend eng | S1-S4 |
| **Agent framework/orquestación** | **Letta** (memoria + tools, ya en stack) + **LangGraph** (checkpointing, grafo de estado) + **Claude Agent SDK** (tool use, permisos) | Letta: MIT · LangGraph: MIT · Claude SDK: MIT | $0 (Letta self-host) + LangGraph $0 | Letta ya está en stack para memoria. LangGraph para orquestación multi-paso con PostgresSaver. Claude SDK para allowed_tools + can_use_tool que mapea a 4 modos de autoridad. Ningún framework OSS es multi-tenant nativo; capa custom obligatoria. | Backend eng | S2 |
| **Sandboxing/Contención** | **Capa 1:** Postgres RLS + tenant_id filtering · **Capa 2:** System prompt + policy engine custom · **Capa 3:** seccomp + Landlock (Linux nativo) para parseo | N/A | $0 | "Sandwich de Contención": múltiples capas débiles gratuitas > una capa fuerte costosa. RLS pre-filtering elimina cross-tenant data leak (20% overhead en vector search). Draft-first elimina comunicación inapropiada. E2B Pro ($150/mes) reservado solo para ejecución de código no confiable. | Backend eng | S1 |
| **Observabilidad** | **Langfuse** (Cloud Core o self-host) + **Arize Phoenix** (drift, self-host) | Langfuse: MIT · Phoenix: Apache 2.0 | $29-39/mes (Langfuse Cloud Core 100k events) + $6 (Phoenix VPS) = **$35/mes** | Langfuse: 19k+ stars GitHub, integración nativa OTel con Claude, deep multi-step tracing, cost tracking por tenant/agente/workflow. Phoenix: embedding drift detection. 12 métricas con thresholds definidos (Sección 3). | Backend eng | S2 |
| **Learning loop** | **PatchRAG** (correcciones como patches retrievables) + **few-shot dinámico** con gold samples | N/A | $0 (usa pgvector existente) | Inference-time learning, sin retraining, sin GPU. Correction lag <5 segundos. PatchRAG: 62.3% accuracy promedio, supera baselines basados en entrenamiento. Robustez ante 25% ruido (-2.2% degradación). | Backend eng | S3-S4 |
| **Infra/hosting** | **Hetzner CPX21** (2 vCPU, 4GB) o **Fly.io** | — | $12-20/mes app + $15-25/mes Postgres = **$27-45/mes** | App + pg-boss workers + Inngest single binary en mismo servidor. Postgres + pgvector compartido. Railway alternativa si prefieren managed. | DevOps eng | S1 |

### Veredicto sobre herramientas evaluadas (adoptar / robar patrones / no adoptar)

| Herramienta | Veredicto | Por qué |
|---|---|---|
| **pg-boss** | **ADOPTAR** Fase 1 | MIT, 3.4k stars, usa Postgres existente, curva mínima |
| **Inngest** | **ADOPTAR** Fase 2 | Apache 2.0 SDKs, 5.2k stars, durable execution nativo, single binary |
| **Temporal** | **ROBAR PATRONES** | 19.7k stars, MIT, referente de arquitectura. Overkill para 10k runs/mes. Infra >$50/mes idle |
| **Windmill** | **NO ADOPTAR** (AGPL) | 15.3k stars pero AGPL-3.0 fuerza open-sourcear producto embebido |
| **Trigger.dev v3** | **NO ADOPTAR** self-hosted | 14.6k stars pero 4CPU/8GB min, CRIU experimental en Docker |
| **React Flow** | **ADOPTAR** Fase 2 | 36.3k stars, MIT, ecosistema dominante, equipo full-time |
| **LangGraph** | **ADOPTAR** Fase 1 | 28.2k stars, MIT, checkpointing nativo con PostgresSaver, 8% overhead |
| **Claude Agent SDK** | **ADOPTAR** Fase 1 | 6.5k stars, MIT, allowed_tools + can_use_tool mapea a modos de autoridad |
| **CrewAI** | **EVALUAR Fase 2** | 47.8k stars, MIT, buena abstracción de roles para workflows colaborativos |
| **smolagents** | **ADOPTAR selectivo** | 23k stars, Apache 2.0, CodeAgent 30% más eficiente, requiere sandbox externo |
| **OpenHands** | **NO ADOPTAR** | 68.5k stars, MIT, pero explícitamente NO multi-tenant |
| **Langfuse** | **ADOPTAR** desde día 1 | 19k+ stars, MIT, integración nativa Claude OTel, cost tracking por tenant |
| **E2B Pro** | **RESERVAR** ($150/mes) | Apache 2.0, Firecracker microVM, activar solo para ejecución código no confiable |

---

## SECCIÓN 2: 5 Patrones de Integración Agente↔Workflow para Fase 1

| # | Patrón | Descripción | Cuándo usar | Complejidad | Ejemplo concreto en FaberLoom |
|---|---|---|---|---|---|
| **1** | **Agent-as-step** | El workflow ejecuta un paso que invoca a un agente LLM como función pura. El agente recibe input estructurado, razona, usa tools y devuelve output estructurado. El workflow continúa con el resultado. | Paso que requiere razonamiento natural, clasificación, generación de draft, o decisión "fuzzy" dentro de un proceso determinístico. **Este es el patrón dominante de Fase 1.** | Media | **QualifyBot en cotización B2B:** Workflow de cotización → Paso 3 invoca QualifyBot con datos del lead → Bot analiza intención, consulta catálogo, calcula envío → Retorna `{clasificación: "lead_calificado", confianza: 0.92, recomendación: "APROBADO_CON_CONDICIONES", draft_propuesta, riesgos}` → Workflow continúa con paso 4 (waitForApproval) |
| **2** | **Chat-launches-workflow** | Usuario conversa con agente (Letta). El agente interpreta intención, dispara un workflow asíncrono y reporta progreso. El workflow corre en background; el agente notifica hitos. | Onboarding, solicitudes complejas donde el usuario prefiere lenguaje natural pero el proceso requiere estructura y trazabilidad. | Media | **Cotización por WhatsApp:** Cliente escribe "Necesito cotizar 100 pares de botas" → QualifyBot (Letta) clasifica como lead B2B → Dispara workflow `generar_cotizacion_B2B` async → Responde: "Estoy preparando tu cotización, te aviso en unos segundos..." → Workflow ejecuta pasos 1-4 → NotifierBot envía resultado al cliente cuando termina |
| **3** | **Event-driven notifier** | Un workflow termina o alcanza un milestone y emite un evento. Un agente notifier escucha y decide qué hacer: notificar, escalar, o iniciar otro workflow. | Notificaciones inteligentes post-workflow donde el tono y canal requieren personalización según segmento del cliente. | Media-Baja | **Confirmación post-cotización:** Workflow de cotización termina → Evento `propuesta_enviada` publicado → NotifierBot decide canal (email formal para enterprise, WhatsApp casual para PYME) y tono (amable para VIP, firme para morosos) → Envía confirmación personalizada |
| **4** | **Human-in-the-loop gate** | Workflow pausa en un paso específico con `waitForApproval()`. El output del agente (draft) se presenta a un humano para aprobación explícita antes de continuar. Toda comunicación externa pasa por este gate. | Cualquier acción irreversible con side-effects: enviar email/WhatsApp a cliente, crear factura, cobrar tarjeta, modificar datos. **Regla sagrada: externos siempre draft-first.** | Baja-Media | **Aprobación de propuesta:** ProposalBot genera draft de cotización → Workflow pausa en `waitForApproval()` → Admin recibe notificación: "Revisar cotización #123 por $45,000 MXN" → Puede APROBAR, RECHAZAR_CON_COMENTARIOS o ESCALAR → Si aprueba, workflow continúa con envío real al cliente |
| **5** | **Compuesto: Chat → Agent-as-step → Event notifier** | Cadena completa: (1) Chat clasifica intención → (2) Dispara workflow con agent-as-step → (3) Human-in-the-loop para aprobación → (4) Event-driven notifier para confirmación. Máximo depth_remaining=2. | El 80% de los workflows de FaberLoom Fase 1 usan esta cadena compuesta. Cubre cotización B2B, cobranza y onboarding de clientes. | Media-Alta | **Cotización B2B completa:** Cliente escribe por WhatsApp → QualifyBot clasifica (Chat-launches) → Workflow `generar_cotizacion_B2B` ejecuta: validar input → calcular precio → **ProposalBot como agent-as-step** genera draft → **waitForApproval() HITL** para gerente → Si aprueba: enviar propuesta + registrar CRM → Evento `propuesta_enviada` → **NotifierBot** confirma al cliente por canal preferido. Max depth=2, max iterations=5, timeout budget=5min |

### Mecanismos de loop detection obligatorios (desde día 1)

| Mecanismo | Valor | Implementación |
|---|---|---|
| **Max depth counter** | `depth_remaining: 2` — workflow → agente → NO más agentes | Decrementar en cada handoff; bloquear en 0 |
| **Circuit breaker** | 3 fallos consecutivos → fallback a template estático | Reintentar en 1 hora |
| **Idempotency keys** | Todo evento trigger tiene key única con TTL 7 días | Postgres UNIQUE constraint + ON CONFLICT DO NOTHING |
| **Timeout budget** | 5 minutos por sesión completa | Presupuesto distribuido: workflow 3min + agente 1.5min + notificación 30seg |
| **Max iterations** | 5 contactos por factura en cobranza | En intento #5: escalamiento forzoso a judicial |

---

## SECCIÓN 3: Top 3 Riesgos Arquitectónicos y Mitigación

| # | Riesgo | Probabilidad | Impacto | Mitigación | Owner | Deadline |
|---|---|---|---|---|---|---|
| **1** | **Loop infinito / runaway agent que quema presupuesto LLM** — Un agente entra en ciclo de reintentos iterando sin progreso, consumiendo tokens ilimitadamente. Ejemplo real: agente gastó $83 en reintentos antes de detenerse porque interpretó "timeout" como "probar otro approach". | Media (30%) | **Crítico** — Podría consumir el presupuesto mensual de $150 en horas, dejando a los 3 design partners sin servicio | **Triple contención:** (a) `max_turns=20` y `max_budget_usd=1.0` por query en Claude SDK; (b) `max_steps=15` por defecto en todo agente; (c) Token burn budget de 10,000 tokens por sesión; (d) Kill switch de cost z-score > 4 que pausa tenant automáticamente; (e) Daily spend caps: partner pago $20/día, gratis $5/día. Todos los mecanismos se activan ANTES de que el LLM responda, no después. | Backend eng | S2 (semana 4) |
| **2** | **Cross-tenant data leak via vector search** — Un embedding de documento del tenant A llega al contexto LLM del tenant B porque el retrieval usa post-filtering en lugar de pre-filtering. El LLM "ya vio todo" antes del filtrado. | Baja-Media (20%) | **Crítico** — Violación de privacidad, terminación de contratos, liability legal en LATAM (LGPD, Ley de Protección de Datos Personales) | **Pre-filtering obligatorio con RLS:** (a) Habilitar RLS en TODAS las tablas tenant-scoped (KB, tickets, emails, contacts); (b) `FORCE ROW LEVEL SECURITY` activo; (c) `SET app.tenant_id` en server-side ANTES de toda query vectorial; (d) Connection pool hygiene: `DISCARD ALL` al devolver conexión; (e) NUNCA filtrar por tenant_id desde browser/cliente; (f) Logging de auditoría de todo acceso cross-tenant; (g) ~20% overhead en vector search HNSW aceptable. El anti-patrón de post-filtering está explícitamente prohibido. | Backend eng | S1 (semana 2) |
| **3** | **Deploy de prompt/código roto en beta sin detección temprana** — Un cambio de prompt o versión de modelo rompe silenciosamente un workflow que funcionaba, afectando a los 3 design partners simultáneamente. A escala PYME (10-50 runs/día), un canary al 10% = 1-5 runs/día — estadísticamente insuficiente para detectar en <48h. | Media (35%) | **Alto** — Degradación de calidad invisible hasta que los partners se quejan, pérdida de confianza en beta | **Tenant-level canary + kill switch:** (a) Partner pago (Marluvas) como canary voluntario, monitoreo manual cercano por 48h; (b) Partners gratuitos reciben versión validada; (c) Feature flag que revierte 100% del tráfico en <60 segundos sin deploy; (d) Golden dataset de 50 queries por agente ejecutado en CI antes de cada deploy; (e) Langfuse trace-level con version tag en cada run; (f) Alerta automática si approval rate < 85% en 24h; (g) Post-rollback: ejecutar 5 golden test cases para confirmar versión anterior funciona. | Backend eng | S2 (semana 4) |

---

## SECCIÓN 4: Estimación de Esfuerzo MVP (1 ingeniero senior, 8 semanas)

### Semana 1: pg-boss + infra base
- Lunes-Martes: `npm install pg-boss`, crear tablas automáticas, integrar con connection pool existente
- Miércoles-Jueves: Implementar `with_tenant_session()` wrapper (RLS + `DISCARD ALL`), primer job handler
- Viernes: Job "welcome email" funcional, validar multi-tenancy con 2 tenants de prueba
- **Entregable:** pg-boss corriendo en producción, 1 job operativo, RLS validado

### Semana 2: Templates YAML + serialización
- Lunes-Martes: Schema YAML basado en CNCF Serverless Workflow DSL, validador JSON Schema
- Miércoles-Jueves: 3 templates YAML hardcodeados en DB (ver Sección 5), tabla `workflow_templates`
- Viernes: Endpoint para listar/activar templates por tenant, validación de schema
- **Entregable:** 3 templates cargados en DB, activables por API

### Semana 3: Agent-as-step con Letta + Claude
- Lunes-Martes: Integrar Letta con pg-boss (handoff JSON protocolo v1.0), QualifyBot como primer agente
- Miércoles-Jueves: Implementar authority_level mapping (SEÑALA/PROPONE/EJECUTA_CON_APROBACION/EJECUTA_SOLO) como tabla `agent_authority_config`
- Viernes: Primer workflow end-to-end: template "Cotización B2B" con QualifyBot como paso 3
- **Entregable:** 1 workflow con agente LLM como paso funcional

### Semana 4: Human-in-the-loop básico
- Lunes-Martes: Implementar `waitForApproval()` con polling/polling (Fase 1, no Inngest aún)
- Miércoles-Jueves: UI básica de aprobación (thumbs up/down + comentario), notificación por email/WhatsApp al aprobador
- Viernes: Integrar HITL en workflow de cotización: ProposalBot genera draft → pausa → humano aprueba → envía
- **Entregable:** Workflow de cotización completo con HITL funcional

### Semana 5: Workflow de cobranza + optimización
- Lunes-Martes: Template "Cobranza inteligente" con CollectionBot como agente-as-step
- Miércoles-Jueves: Circuit breaker (3 fallos → fallback), max depth counter, idempotency keys
- Viernes: Loop detection completo, timeout budgets, integration tests
- **Entregable:** 2 workflows funcionales (cotización + cobranza) con defensas anti-loop

### Semana 6: Observabilidad con Langfuse
- Lunes-Martes: Integrar Langfuse SDK (@observe decorator), taggear traces con tenant_id/agent_id/workflow_type
- Miércoles-Jueves: 3 métricas críticas activas: approval rate, token cost per run, latency P95
- Viernes: Alertas P0 → Slack (loop detection, cost z-score > 4), dashboard básico
- **Entregable:** Todos los LLM calls trazados, 3 métricas con alertas

### Semana 7: Feedback UI (thumbs + diff capture)
- Lunes-Martes: Thumbs up/down en cada output del agente con micro-dropdown de razón (<5 segundos)
- Miércoles-Jueves: Captura automática de diffs cuando usuario edita output, banner "Guardar como gold sample" (1 click)
- Viernes: Pipeline de auto-sanitización: PII strip, formato normalize, deduplicación
- **Entregable:** Sistema de feedback operativo, gold samples promovibles

### Semana 8: Integración + testing + documentación
- Lunes-Martes: Integración end-to-end: chat → workflow → agent → HITL → notificación, 50 golden test cases
- Miércoles-Jueves: Testing con design partners, fixes, ajuste de prompts
- Viernes: Documentación técnica, spec del workflow engine, handoff a beta
- **Entregable:** MVP listo para beta, 2-3 workflows funcionales, docs

### Resumen
- **Semanas 1-2:** pg-boss + templates YAML
- **Semanas 3-4:** Agent-as-step + HITL
- **Semanas 5-6:** Cobranza + observabilidad
- **Semanas 7-8:** Feedback + integración + testing
- **Total:** 8 semanas de 1 ingeniero senior (backend Python/Node, experiencia con Postgres y LLMs)
- **Nota:** No hay builder visual en Fase 1. FaberLoom configura workflows por los design partners via API/config files. Builder visual = Fase 2 (mes 3-6).

---

## SECCIÓN 5: 5 Templates de Workflow Pre-armados

Contexto: Design partners en **calzado de seguridad B2B** (Marluvas/Tecmater — calzado industrial para fábricas, construcción, minería).

### Template 1: "Cotización Rápida B2B"

| Campo | Valor |
|---|---|
| **Trigger** | Mensaje de WhatsApp/web con palabras clave: "cotizar", "precio", "presupuesto", "cuánto cuesta" |
| **Pasos** | 1. Validar input (SKU/cantidad detectada) → 2. Consultar stock en inventario → 3. **QualifyBot (agent-as-step)**: Analizar lead, consultar catálogo, calcular envío, generar draft propuesta → 4. **waitForApproval()** — Gerente de ventas revisa draft → 5. Si aprueba: enviar propuesta por WhatsApp/email + registrar en CRM |
| **Agente** | QualifyBot (área: Ventas) |
| **Modo de autoridad** | PROPONE (genera draft, NO ejecuta sin aprobación) |
| **Aprobación humana** | **SÍ** — Todo envío externo de propuesta requiere aprobación del gerente de ventas |
| **SLA** | < 2 minutos desde mensaje del cliente hasta propuesta en bandeja del gerente; < 5 minutos desde aprobación hasta envío al cliente |

### Template 2: "Cobranza Inteligente"

| Campo | Valor |
|---|---|
| **Trigger** | Cron diario 8:00 AM (America/Sao_Paulo) — detecta facturas vencidas hoy |
| **Pasos** | 1. Query facturas vencidas no contactadas hoy → 2. Filtrar (no litigio, no ya cobradas, no contactado hoy) → 3. **CollectionBot (agent-as-step)**: Analizar segmento cliente, historial pagos, decidir tono (suave/firme/ultimátum), canal (email/WhatsApp/SMS), timing, generar draft mensaje → 4. **waitForApproval()** — Supervisor revisa draft → 5. Si aprueba: enviar por canal elegido → 6. Programar verificación en +N días según segmento → 7. Si pasan N días sin pago: re-ejecutar con flag "recordatorio_2" |
| **Agente** | CollectionBot (área: Cobranza) |
| **Modo de autoridad** | PROPONE (genera draft de mensaje, NO envía sin aprobación del supervisor) |
| **Aprobación humana** | **SÍ** — Todo mensaje de cobranza requiere aprobación del supervisor. Auto-approve solo si monto < $5,000 MXN AND confianza > 0.85 AND tono != "ultimátum" |
| **SLA** | < 4 horas desde detección hasta aprobación del supervisor; si no responde en 4h: envía con tono suave por defecto |

### Template 3: "Alerta de Stock Bajo"

| Campo | Valor |
|---|---|
| **Trigger** | Evento: stock de producto baja de umbral configurable (default: 10 unidades) |
| **Pasos** | 1. Detectar producto con stock < umbral → 2. Buscar proveedor asociado al producto → 3. **waitForApproval()** — Admin confirma reposición → 4. Generar orden de compra automática → 5. Enviar WhatsApp + email al proveedor (con datos de OC) → 6. Registrar en sistema de compras |
| **Agente** | Ninguno (proceso determinístico, no requiere LLM) |
| **Modo de autoridad** | N/A |
| **Aprobación humana** | **SÍ** — La generación de orden de compra requiere confirmación del admin/compras antes de enviar al proveedor |
| **SLA** | < 1 minuto desde detección hasta alerta en bandeja; < 5 minutos desde aprobación hasta envío al proveedor |

### Template 4: "Bienvenida a Nuevos Clientes"

| Campo | Valor |
|---|---|
| **Trigger** | Evento: nuevo cliente registrado en el sistema |
| **Pasos** | 1. Detectar nuevo cliente → 2. Enviar mensaje de bienvenida por WhatsApp (template predefinido) → 3. Enviar email de onboarding con catálogo digital adjunto → 4. Programar recordatorio en +7 días para seguimiento de vendedor → 5. Evento `bienvenida_completada` para NotifierBot |
| **Agente** | NotifierBot (área: Marketing/Atención) |
| **Modo de autoridad** | EJECUTA_SOLO (mensaje de bienvenida es bajo riesgo, predefinido) |
| **Aprobación humana** | **NO** — Mensaje de bienvenida es template pre-aprobado, sin personalización LLM |
| **SLA** | < 30 segundos desde registro hasta envío de WhatsApp + email |

### Template 5: "Seguimiento Post-Venta"

| Campo | Valor |
|---|---|
| **Trigger** | Evento: entrega de pedido confirmada (firma digital/confirmación transportista) |
| **Pasos** | 1. Detectar entrega confirmada → 2. Esperar +3 días hábiles → 3. **SurveyBot (agent-as-step)**: Generar mensaje de seguimiento personalizado según tipo de producto (calzado de seguridad para construcción vs fábrica vs minería) → 4. Enviar encuesta de satisfacción por WhatsApp → 5. Si cliente responde: clasificar sentimiento (positivo/negativo/neutro) → 6. Si negativo: crear alerta para servicio al cliente → 7. Si positivo: solicitar reseña en Google/mercado |
| **Agente** | SurveyBot (área: Servicio al Cliente) |
| **Modo de autoridad** | EJECUTA_CON_APROBACIÓN — Mensaje generado por LLM requiere aprobación en primera instancia; después de 5 envíos con >90% thumbs-up, puede graduarse a EJECUTA_SOLO |
| **Aprobación humana** | **SÍ** (primeras 5 ejecuciones) → **NO** (después de 5 con >90% aprobación) |
| **SLA** | < 1 minuto desde trigger + 3 días hasta envío de encuesta; respuesta esperada en 24-48h |

---

## SECCIÓN 6: 3 Cambios al SPEC_FABERLOOM_AGENT_COMPOSITION_v1

| # | Gap detectado | Qué cambia en el spec | Por qué (referencia a investigación) |
|---|---|---|---|
| **1** | **El spec no define el motor de ejecución de workflows** — Describe 168 agentes, 9 áreas funcionales, 4 modos de autoridad, pero no QUÉ ejecuta los workflows ni CÓMO se serializan. | **Agregar sección "Workflow Execution Engine"** con: (a) Motor Fase 1 = pg-boss sobre Postgres existente; (b) Motor Fase 2 = Inngest self-hosted para durable execution; (c) DSL = YAML declarativo basado en CNCF Serverless Workflow DSL; (d) Builder visual = React Flow (Fase 2); (e) Pipeline: YAML → AST/JSON intermedio → Validación → Generador de código motor. Incluir ejemplo de template YAML completo. | Dim01 (pg-boss ganador para Fase 1), Dim02 (YAML + React Flow), Dim03 (durable execution con checkpointing). Insight 3: "pg-boss e Inngest no son excluyentes; son capas diferentes". El spec anticipó los conceptos pero no la implementación. |
| **2** | **El spec no define el protocolo de handoff Agente↔Workflow** — Describe modos de autoridad como abstracción de producto pero no cómo se implementan técnicamente ni el contrato JSON de comunicación. | **Agregar sección "Agent↔Workflow Integration Protocol"** con: (a) 4 patrones de integración (agent-as-step, chat-launches-workflow, event-driven, HITL gate); (b) Protocolo JSON v1.0 de handoff: campos obligatorios (session.*, authority_level, depth_remaining, constraints.max_tool_calls), campos de retorno (agent_result.status, classification, output); (c) Mapeo de 4 modos de autoridad a mecanismos técnicos: SEÑALA = tool call read-only; PROPONE = output a bandeja de aprobación; EJECUTA_CON_APROBACIÓN = waitForApproval(); EJECUTA_SOLO = step normal; (d) Mecanismos anti-loop: max depth=2, circuit breaker=3 fallos, timeout budget=5min; (e) Tabla de configuración `agent_authority_config` en Postgres — cambiar modo es un UPDATE, no un deploy. | Dim06 (4 patrones + protocolo JSON), Dim04 (Claude SDK allowed_tools), Insight 4: "Autoridad como Dial, no como Switch". El spec definió los conceptos; esta investigación los concreta en implementación. |
| **3** | **El spec no define el learning loop** — Describe gold samples como concepto pero no el pipeline de feedback, la técnica de aprendizaje, ni la UI de captura. | **Agregar sección "Learning Loop"** con: (a) Fase 1 = PatchRAG (correcciones como patches retrievables) + few-shot dinámico con gold samples; (b) Fase 2 = LoRA selectivo por tenant; (c) UI de feedback: thumbs up/down (<2 seg), diff capture automático + "Guardar como gold sample" 1-click (<20 seg); (d) Pipeline: feedback → auto-sanitización (PII strip, dedup) → validación de calidad → PatchRAG disponible <5 seg; (e) Cross-tenant: Fase 1 = schema-level insights anonimizados; Fase 2 = DP-LoRA federado (epsilon=3-6); (f) Umbrales: nunca esperar a N feedbacks para PatchRAG; esperar N=50+ gold samples para considerar LoRA. | Dim09 (PatchRAG, few-shot, DP-LoRA), Dim08 (user correction rate >15% = alerta P2), Insight 5: "El Costo del Feedback es la Variable Oculta". El spec mencionó gold samples; esta investigación define el sistema completo. |

**Veredicto sobre el SPEC v1:** El SPEC_FABERLOOM_AGENT_COMPOSITION_v1 es arquitectónicamente sólido. Los gaps no son errores de diseño sino decisiones de implementación pendientes. La recomendación: **no reescribir el spec, sino crear un spec técnico nuevo (SPEC_FABERLOOM_WORKFLOW_ENGINE_v1)** que traduce cada decisión del spec a una decisión técnica concreta.

---

## SECCIÓN 7: Decisiones Ejecutables por Sprint

### Sprint 1: Infra + Motor Base (Semanas 1-2)

| # | Decisión | Owner | Deadline | Criterio de éxito | Dependencias |
|---|---|---|---|---|---|
| 1.1 | Instalar pg-boss en stack existente (npm install, tablas automáticas, connection pool integrado) | Backend eng | Día 3 | Job "welcome_email" ejecuta exitosamente en ambiente de prueba | Acceso a DB producción |
| 1.2 | Implementar `with_tenant_session()` wrapper: `SET app.tenant_id` + `DISCARD ALL` en connection pool | Backend eng | Día 5 | Test de RLS: tenant A no ve datos de tenant B en 100% de queries | 1.1 |
| 1.3 | Crear schema de workflow YAML basado en CNCF Serverless Workflow DSL + validador JSON Schema | Backend eng | Día 7 | YAML de ejemplo pasa validación, genera AST intermedio correcto | — |
| 1.4 | Cargar 3 templates YAML hardcodeados en tabla `workflow_templates` (cotización, cobranza, alerta stock) | Backend eng | Día 8 | Templates listables por API, activables por tenant_id | 1.3 |
| 1.5 | Implementar endpoint REST para listar/activar templates por tenant | Backend eng | Día 10 | Partner de prueba puede activar template con 1 llamada API | 1.2, 1.4 |
| 1.6 | Habilitar RLS en tablas: `knowledge_base_chunks`, `emails`, `tickets`, `contacts`, `invoices` | Backend eng | Día 12 | TODAS las tablas tenant-scoped tienen RLS + FORCE activo | 1.2 |

### Sprint 2: Agentes + HITL (Semanas 3-4)

| # | Decisión | Owner | Deadline | Criterio de éxito | Dependencias |
|---|---|---|---|---|---|
| 2.1 | Integrar Letta con pg-boss: handoff JSON protocolo v1.0 (workflow → agente → workflow) | Backend eng | Día 15 | Primer handoff exitoso: workflow envía contexto, agente responde con output estructurado | 1.1, Letta corriendo |
| 2.2 | Crear tabla `agent_authority_config`: agent_id × tool × mode (SEÑALA/PROPONE/EJECUTA_CON_APROBACIÓN/EJECUTA_SOLO) | Backend eng | Día 17 | Cambiar modo de agente es un UPDATE, requiere <1s, sin deploy | — |
| 2.3 | Implementar QualifyBot: primer agente-as-step en workflow de cotización (consulta catálogo, calcula envío, genera draft) | Backend eng | Día 19 | QualifyBot recibe input estructurado, retorna JSON válido con clasificación + draft | 2.1, 2.2 |
| 2.4 | Implementar `waitForApproval()` con polling: pausa workflow, notificación al aprobador, reanudación con decisión | Backend eng | Día 21 | Workflow pausa > humano aprueba > workflow continúa en <5 segundos | 2.3 |
| 2.5 | Integrar Langfuse: @observe decorator, tags tenant_id/agent_id/workflow_type en cada trace | Backend eng | Día 23 | 100% de LLM calls trazados con metadata correcta | Cuenta Langfuse |
| 2.6 | Implementar 3 métricas críticas: approval rate, token cost per run, latency P95 con alertas a Slack | Backend eng | Día 24 | Métricas calculadas en tiempo real, alertas disparan en thresholds correctos | 2.5 |
| 2.7 | Crear kill switch: feature flag que revierte 100% tráfico a versión estable en <60 segundos | Backend eng | Día 26 | Kill switch testeado: tiempo de reversión medido <60 segundos | — |

### Sprint 3: Cobranza + Defensas + Learning Loop (Semanas 5-6)

| # | Decisión | Owner | Deadline | Criterio de éxito | Dependencias |
|---|---|---|---|---|---|
| 3.1 | Implementar CollectionBot: agente-as-step para workflow de cobranza (segmento, tono, canal, draft) | Backend eng | Día 29 | CollectionBot genera draft de cobranza con tono apropiado según segmento | 2.1, 2.2 |
| 3.2 | Implementar circuit breaker: 3 fallos consecutivos → fallback a template estático, reintentar en 1h | Backend eng | Día 31 | Circuit breaker testeado con simulación de fallo | 3.1 |
| 3.3 | Implementar max depth counter + timeout budget: depth_remaining=2, budget=5min por sesión | Backend eng | Día 33 | Handoff con depth=0 es rechazado, timeout budget agotado aborta graceful | 2.1 |
| 3.4 | Implementar idempotency keys: Postgres UNIQUE constraint + ON CONFLICT DO NOTHING, TTL 7 días | Backend eng | Día 35 | Evento duplicado es ignorado automáticamente, sin side-effects dobles | 1.1 |
| 3.5 | Implementar thumbs up/down en cada output del agente + micro-dropdown de razón (<5 segundos) | Frontend eng | Día 37 | 80%+ de outputs tienen al menos 1 feedback en primera semana de uso | — |
| 3.6 | Implementar captura automática de diffs + banner "Guardar como gold sample" (1 click) | Backend eng | Día 40 | Diff capturado en cada edición, banner visible en <1 segundo post-edición | 3.5 |
| 3.7 | Implementar PatchRAG: almacenar correcciones como patches retrievables en pgvector | Backend eng | Día 42 | Corrección disponible para retrieval en <5 segundos post-promoción | 3.6, pgvector |

### Sprint 4: Integración + Beta Ready (Semanas 7-8)

| # | Decisión | Owner | Deadline | Criterio de éxito | Dependencias |
|---|---|---|---|---|---|
| 4.1 | Ejecutar 50 golden test cases end-to-end: chat → workflow → agent → HITL → notificación | QA eng | Día 45 | >95% de test cases pasan, 0 regressiones críticas | 3.1-3.7 |
| 4.2 | Testing con 3 design partners: sesiones de 2h cada uno, feedback documentado | Product manager | Día 48 | Cada partner tiene al menos 1 workflow activo y funcional | 4.1 |
| 4.3 | Ajuste de prompts basado en feedback de partners (QualifyBot, CollectionBot) | Backend eng | Día 50 | Approval rate >85% en tests con datos reales de partners | 4.2 |
| 4.4 | Documentación: SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md + guía de operación para partners | Tech writer | Día 52 | Documento aprobado por equipo, usable por partners | Todo |
| 4.5 | Deploy a producción estable con monitoreo 24/7 (Langfuse + Slack alerts) | Backend eng | Día 53 | Sistema estable por 48h sin alertas P0/P1 | 4.3 |
| 4.6 | Revisión de sprint: métricas de beta (adoption rate, approval rate, costo por run) | Product manager | Día 56 | Reporte con KPIs baseline para iteración post-beta | 4.5 |

---

## SECCIÓN 8: Presupuesto Mensual Detallado

### Escenario Base (más probable)

| Componente | Mes 1 (S1-S2) | Mes 3 (+S3-S4) | Mes 6 (+Fase 2) | Mes 12 (escala) |
|---|---|---|---|---|
| VPS Hetzner CPX21 (app + workers) | $15 | $15 | $15 | $30 (2x CPX21) |
| Postgres + pgvector (Hetzner/Railway) | $20 | $20 | $20 | $35 |
| Inngest self-hosted (single binary) | $0 | $0 | $0 | $0 (mismo VPS) |
| LLM API (Claude) — 3 partners | $40 | $60 | $80 | $150 |
| Langfuse Cloud Core (100k events) | $29 | $29 | $29 | $49 (plan higher) |
| Arize Phoenix self-host (drift) | $0 | $6 | $6 | $6 |
| Grafana Cloud (alertas, free tier) | $0 | $0 | $0 | $0 |
| AWS Secrets Manager (5 secretos) | $2 | $2 | $2 | $4 |
| **TOTAL ESCENARIO BASE** | **$106** | **$132** | **$152** | **$274** |

### Escenario Optimista (bajo uso, partners satisfechos rápido)

| Componente | Mes 1 | Mes 3 | Mes 6 | Mes 12 |
|---|---|---|---|---|
| VPS Hetzner CPX21 | $15 | $15 | $15 | $15 |
| Postgres + pgvector | $15 | $15 | $15 | $20 |
| LLM API (Claude) | $25 | $35 | $45 | $70 |
| Langfuse Cloud Core | $0 (self-host) | $0 (self-host) | $10 | $29 |
| Arize Phoenix | $0 | $0 | $0 | $6 |
| AWS Secrets Manager | $2 | $2 | $2 | $2 |
| **TOTAL OPTIMISTA** | **$57** | **$67** | **$87** | **$142** |

### Escenario Pesimista (alto uso, incidentes, necesidad de sandboxing VM)

| Componente | Mes 1 | Mes 3 | Mes 6 | Mes 12 |
|---|---|---|---|---|
| VPS Hetzner CPX31 (4 vCPU, 8GB) | $25 | $25 | $25 | $50 (2x) |
| Postgres + pgvector (managed Railway) | $30 | $30 | $30 | $60 |
| LLM API (Claude) — runaway loops | $80 | $100 | $120 | $250 |
| Langfuse Cloud Core | $29 | $29 | $49 | $79 |
| Arize Phoenix + VPS | $6 | $6 | $6 | $6 |
| E2B Pro (sandboxing VM) | $0 | $0 | $150 | $150 |
| AWS Secrets Manager | $2 | $2 | $4 | $8 |
| **TOTAL PESIMISTA** | **$172** | **$192** | **$384** | **$603** |

### Notas presupuestarias

- **Budget mensual objetivo:** $150/mes. El escenario base lo cumple hasta mes 6.
- **Langfuse self-host** (optimista) requiere VPS adicional $5-10/mes pero elimina costo Cloud.
- **E2B Pro** ($150/mes) se activa SOLO si un agente necesita ejecutar código no confiable. Reservado en pesimista.
- **Claude API BYOK** (Bring Your Own Key): en Fase 2, cada tenant puede usar su propia API key, reduciendo costo LLM para FaberLoom.
- **Margen de seguridad:** A mes 6 con 5 tenants activos, el costo por tenant es ~$30/mes. Con precio de $99-299/mes por tenant, el margen bruto es 70-90%.

---

## SECCIÓN 9: Roadmap Visual (Texto)

```
2026                              2027
|----+----+----+----+----+----+----+----+----+----+----+----|
     |         |              |                   |
   ABRIL     JUNIO        SEPTIEBRE           MARZO
   Beta      Fin Beta     Scale              Full product

================================================================================
FASE 1: MVP BETA (8 semanas) — Abril 20 → Junio 14
================================================================================
S1 S2 S3 S4 S5 S6 S7 S8
|==|==|==|==|==|==|==|==|
[====pg-boss + templates====]
       [====agent-as-step + HITL====]
              [====cobranza + defensas====]
                   [====observabilidad====]
                        [====feedback UI====]
                             [====integración + beta====]
Milestones:
  S1 W2: pg-boss en producción, RLS validado
  S2 W4: Primer workflow end-to-end con agente + HITL
  S3 W6: 2 workflows (cotización + cobranza), Langfuse activo
  S4 W8: MVP beta lanzado a 3 design partners

================================================================================
FASE 2: BUILDER + ESCALA (Meses 3-6) — Junio → Septiembre
================================================================================
M3   M4   M5   M6
|====|====|====|====|
[====React Flow builder visual====]
     [====AI-assisted workflow building====]
          [====Inngest self-hosted====]
               [====5 templates → 15 templates====]
Milestones:
  M3: Builder visual simplificado (usuarios power users)
  M4: AI assistant para customización de workflows en español
  M5: Inngest self-hosted para durable execution (sleeps largos)
  M6: 15 templates, 10 tenants, $150-200/mes stack

================================================================================
FASE 3: LEARNING + AUTONOMÍA (Meses 6-12) — Septiembre → Marzo 2027
================================================================================
M7   M8   M9   M10  M11  M12
|====|====|====|====|====|====|
     [====LoRA selectivo por tenant====]
          [====DP-LoRA cross-tenant====]
               [====Autoridad progresiva L1→L3====]
                    [====Marketplace de templates====]
Milestones:
  M8: Primer LoRA adapter entrenado con gold samples de tenant
  M10: Cross-tenant learning con DP-LoRA (schema-level insights)
  M11: Agentes graduados a L2 (monitored autonomy) con >95% confiabilidad
  M12: 50+ templates, 25+ tenants, break-even operativo

================================================================================
HITOS CLAVE (Diamonds)
================================================================================

  ◆ 2026-04-20: Beta launch (3 design partners)
  ◆ 2026-06-14: Fin beta, decisión: ¿continuar/ pivotar?
  ◆ 2026-07-15: Primer pago recurrente ($99/mes)
  ◆ 2026-09-01: 10 tenants activos
  ◆ 2026-10-15: Builder visual público
  ◆ 2026-12-01: 25 tenants, revenue $2,500+/mes
  ◆ 2027-01-15: Break-even operativo
  ◆ 2027-03-01: Series A pitch (50 tenants, $5K MRR, métricas de learning loop)

================================================================================
DEPENDENCIAS CRÍTICAS
================================================================================

  [Langfuse integrado] ──────────────────────────────→ [LoRA Fase 2]
       S2                                                   M8

  [pg-boss estable] ─────────────────────────────────→ [Inngest self-hosted]
       S1                                                   M5

  [5 templates funcionales] ─────────────────────────→ [15 templates]
       S4                                                   M6

  [HITL funcional] ──────────────────────────────────→ [Autoridad progresiva]
       S2                                                   M10

  [PatchRAG operativo] ──────────────────────────────→ [DP-LoRA federado]
       S3                                                   M9
```

---

## SECCIÓN 10: Checklist de Go/No-Go para Beta

### Criterios Técnicos (MUST HAVE — sin excepciones)

| # | Criterio | Método de verificación | Threshold |
|---|---|---|---|
| 10.1 | pg-boss procesa jobs sin pérdida de mensajes | Test de carga: 100 jobs, 0% pérdida | 100% delivery |
| 10.2 | RLS previene acceso cross-tenant en 100% de queries | Penetration test: 50 queries por tenant, 0 leaks | 0 data leaks |
| 10.3 | Workflow de cotización B2B ejecuta end-to-end en <5 minutos | Medición con timestamps de 10 ejecuciones | P95 < 5 min |
| 10.4 | Human-in-the-loop funciona: workflow pausa, notifica, reanuda | Test manual con 3 aprobadores diferentes | 100% success rate |
| 10.5 | Kill switch revierte 100% tráfico en <60 segundos | Test de stress: medir tiempo de reversión | < 60 seg |
| 10.6 | Loop detection previene ciclos infinitos | Simular 3 escenarios de loop, verificar bloqueo | 100% bloqueo |
| 10.7 | Langfuse traza 100% de LLM calls con metadata correcta | Auditoría de traces por 48h | 100% coverage |

### Criterios de Producto (MUST HAVE)

| # | Criterio | Método de verificación | Threshold |
|---|---|---|---|
| 10.8 | 3 design partners tienen al menos 1 workflow activo | Dashboard de activaciones | 3/3 partners |
| 10.9 | Time-to-first-workflow < 3 minutos para admin no-técnico | Test con usuario de 45+ años sin background técnico | < 3 min |
| 10.10 | Approval rate de outputs del agente > 80% en primera semana | Métrica Langfuse: thumbs up / total | > 80% |
| 10.11 | 0 comunicaciones externas enviadas sin aprobación humana | Auditoría de logs: buscar envíos sin waitForApproval | 0 incidentes |
| 10.12 | Costo por run < $0.50 promedio (incluyendo LLM + infra) | Reporte Langfuse cost tracking dividido por # runs | < $0.50/run |

### Criterios de UX (SHOULD HAVE — flexibles)

| # | Criterio | Método de verificación | Threshold |
|---|---|---|---|
| 10.13 | Admin puede activar template sin ayuda técnica | Test de usabilidad: 2/3 usuarios exitosos | > 66% |
| 10.14 | Mensajes de error entendibles (< 30 segundos para resolver) | Test con errores simulados, medir tiempo a resolución | < 30 seg |
| 10.15 | Feedback UI: thumbs usado en > 30% de interacciones | Métrica de adopción de feature | > 30% |

### Criterios de Negocio (NICE TO HAVE)

| # | Criterio | Método de verificación | Threshold |
|---|---|---|---|
| 10.16 | 1 design partner pago renueva para mes 2 | Contrato firmado | 1/1 |
| 10.17 | Stack mensual < $150 en primera beta | Reporte de costos consolidado | < $150 |
| 10.18 | 0 incidentes de seguridad (data leak, unauthorized access) | Auditoría de seguridad | 0 incidentes |

### Regla de decisión Go/No-Go

- **GO (lanzar beta):** 100% de MUST HAVE técnicos (10.1-10.7) + 100% de MUST HAVE producto (10.8-10.12) + ≥2 de 3 SHOULD HAVE (10.13-10.15)
- **NO-GO (postergar 1 semana):** Cualquier MUST HAVE no cumplido
- **NO-GO + replanificar:** >2 MUST HAVE no cumplidos, o cualquier incidente de seguridad

---

## Apéndice A: Evidencia Cruzada por Dimensión

| Dimensión | Hallazgo principal | Confianza | Fuentes |
|---|---|---|---|
| Dim01 (Motores) | pg-boss → Inngest es el roadmap correcto, no Temporal | HIGH | 24 búsquedas, GitHub oficial, pricing verificado |
| Dim02 (DSL) | Visual node-graph + YAML subyacente, React Flow como librería | HIGH | 25 búsquedas, comparativa 7 plataformas, benchmarks UX |
| Dim03 (Durable Execution) | Checkpointing + idempotency keys + sagas con compensación | HIGH | 22 búsquedas, pattern de Stripe, benchmarks Postgres |
| Dim04 (Frameworks Agentes) | Ninguno es multi-tenant nativo; capa custom sobre LangGraph + Claude SDK | HIGH | 24 búsquedas, GitHub stars verificados, licencias confirmadas |
| Dim05 (Sandboxing) | "Sandwich de Contención": RLS + prompt + draft-first > VM costosa | HIGH | 22 búsquedas, CVEs reales, benchmarks RLS |
| Dim06 (Agente↔Workflow) | Workflow-primero, agente-selectivo, 4 patrones de integración | HIGH | 28 búsquedas, Microsoft Azure, Temporal, LangGraph docs |
| Dim07 (Builder UX) | Template-first 70% + AI-assisted 20% + from-scratch 10% | HIGH | 25 búsquedas, HubSpot case study, AARP research |
| Dim08 (Observabilidad) | Langfuse es la mejor opción: MIT, OTel nativo, $29/mes | HIGH | 22 búsquedas, comparativa 6 herramientas, integración Claude verificada |
| Dim09 (Learning Loops) | PatchRAG + few-shot para Fase 1, LoRA selectivo para Fase 2 | HIGH | 20+ búsquedas, paper PatchRAG (arXiv 2026), Intercom case study |
| Cross-verification | 8/13 hallazgos de HIGH confidence, 3 resueltos, 3 LOW | HIGH | Consolidación de 9 dimensiones |
| Insights | 8 insights cruzados, 6 de HIGH confidence | HIGH | Análisis transversal |

## Apéndice B: Documentos Derivados

Este documento de síntesis se traduce DIRECTAMENTE a:

1. **SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md** — Secciones 1, 4, 5, 7
2. **SPEC_FABERLOOM_AGENT_COMPOSITION_v1.1.md** — Sección 6 (3 cambios)
3. **5 templates YAML listos para implementar** — Sección 5
4. **Roadmap Sprint 1-4 con deadlines** — Sección 7
5. **Checklist Go/No-Go para Beta** — Sección 10

---

*Documento generado el 2026-04-22. Basado en 9 dimensiones de investigación, 200+ búsquedas independientes, 7,643 líneas de evidencia verificada contra fuentes primarias (GitHub, documentación oficial, papers académicos, reportes de seguridad). Todos los datos de costo, licencia, estrellas GitHub y última actualización verificados. Stack total: ~$106-132/mes en Fase 1, dentro del budget de $150/mes.*
