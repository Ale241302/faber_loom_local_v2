# Ficha Funcional — Módulo 01: Inbound Gmail/WhatsApp + Clasificación L1

> Generado por AGENTE_1_INBOUND_CLASIFICACION del swarm de especificación funcional de FaberLoom Foundation Beta E1.
> Docs base: SCH_FB_FUNCTIONAL_SPEC_v1.md · PLB_FB_FOUNDATION_BETA_v1.md · SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md · SPEC_FB_AUTH_TENANT_RBAC_v1.md · SPEC_ACTION_ENGINE.md · ARCH_AGENT_PRINCIPLES.md · POL_DATA_CLASSIFICATION.md · ENT_FB_INBOUND_TAXONOMY_v1.md · SPEC_FB_ROUTINES_v1.md · SPEC_FB_WORKSPACE_v1.md · ENT_FB_WORK_TYPE_PACK_v1.md · SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md · SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md · SCH_FB_TASK_ENTITY.md · SPEC_FB_EVENTING_AND_OUTBOX_v1.md.

---

## MÓDULO 1: Inbound Gmail/WhatsApp

**MÓDULO:** Inbound Gmail/WhatsApp (tipos 1-2 del ENT_FB_INBOUND_TAXONOMY_v1)  
**SUPERFICIE:** Canal → Backend → Desktop (WorkLoom)  
**SPRINT E1:** S1A (conexión de canales base) / S5 (Mesa de Control + multi-buzón según PLB §S5)  
**ROLES QUE LO USAN:** Owner (configura canales), Operator (procesa items) — en E1 según enmienda E-4 (2 roles: Owner/Operator); Admin/Supervisor/Viewer son E3+  
**DATA CLASS TÍPICA:** N2 (CONFIDENTIAL) — datos de cliente, pricing, RFQ  

---

### DIMENSIÓN 1 — EXISTENCIA

#### 1.1 Por qué existe
María (Operator) recibe 20-30 tareas mixtas por día entre Gmail y WhatsApp. Cuando le llega un RFQ por WhatsApp tiene que: ver el mensaje, identificar al cliente, copiar/extraer datos, buscar en catálogo, decidir si es urgente, y luego armar una respuesta. Sin este módulo el RFQ queda atrapado en el canal, María debe alternar entre 2-3 herramientas, y los mensajes de alta prioridad se mezclan con spam y newsletters.

#### 1.2 A quién le duele
- **Operator:** es quien sufre el dolor diario de triage manual y pérdida de contexto.
- **Owner:** configura los canales y es responsable de que nada se pierda; siente el costo si un RFQ no se responde a tiempo.
- **Supervisor/Viewer:** E3+; Supervisor mide calidad de respuesta, Viewer solo historial.

#### 1.3 Cuándo aparece
Aparece automáticamente cuando un mensaje o email nuevo ingresa por un canal conectado del tenant (Gmail OAuth / IMAP / WhatsApp BSP / Telegram Bot). El evento disparador es `feed.item.received`.

---

### DIMENSIÓN 2 — PROPÓSITO

#### 2.1 Para qué
Capturar, normalizar y poner en cola todo mensaje entrante para que FaberLoom lo clasifique y ruteé sin que María tenga que abrir cada canal por separado.

#### 2.2 Qué valor entrega
- Unifica la entrada del día en un solo lugar (Mesa de Control Zona 4).
- Reduce el riesgo de RFQs perdidos o respondidos tarde.
- Permite aplicar reglas de negocio (SLA, data class, canal origen) desde el primer segundo.

#### 2.3 Qué pasa si no existe
María debe revisar Gmail y WhatsApp manualmente, copiar información a un CRM/Excel, y decidir qué hacer con cada mensaje. Esto genera duplicados, olvidos y priorización errática.

---

### DIMENSIÓN 3 — CREACIÓN

#### 3.1 Cómo se crea
N/A — el inbound no se crea manualmente. Aparece automáticamente cuando un canal conectado recibe un mensaje. La conexión del canal sí se crea durante el tenant bootstrap o en Settings (web):
1. Owner conecta mailbox Gmail OAuth o cuenta WhatsApp Business.
2. Sistema valida credenciales y comienza a recibir webhooks/pushes/polls.
3. Cada mensaje nuevo se normaliza a un `feed_item`.

#### 3.2 Quién puede crearlo
- Owner del tenant configura el canal.
- En E1, 2 roles: Owner configura; Operator opera.

#### 3.3 Qué necesita para crearse
- Canal conectado y autorizado (Gmail OAuth / IMAP / WhatsApp BSP).
- Tenant activo con RLS habilitado.
- [PENDIENTE — tipos 1-2 exactos del ENT_FB_INBOUND_TAXONOMY_v1 están en stub; no se puede declarar qué representan esos tipos sin indexación del doc].

---

### DIMENSIÓN 4 — USO DIARIO

#### 4.1 Cómo se usa en el día a día
1. María abre WorkLoom (desktop).
2. En Zona 4 (Inbox completo) ve cards de mensajes entrantes con: remitente, preview, canal de origen, timestamp.
3. El sistema ya aplicó Tier 0 + L1 classifier; la card muestra tipo de tarea sugerida y confidence HIGH/LOW.
4. Si el item es accionable (ej. RFQ), se genera una task y, si aplica, un draft que aparece en Zona 2.
5. Si el item es spam/logístico/recurrente, María puede aplicar acciones inline (leer y ocultar, borrar futuros, asignar agente).

#### 4.2 Cómo se invoca
Automático vía:
- Gmail OAuth Watch (push).
- IMAP poll 60s (fallback).
- WhatsApp BSP webhook.
- Telegram bot webhook.

También puede invocarse manualmente desde Workspace con "@mail_X buscá correos no leídos".

#### 4.3 Qué ve el usuario mientras ocurre
- **Inicial:** badge en sidebar con contador de items no vistos.
- **En proceso:** card en Zona 4 con spinner "Clasificando..." durante L1.
- **Completado:** card estabilizada con tipo, confidence, SLA restante, acción primaria contextual.
- **Error:** card con badge rojo "Error de canal" o "No se pudo clasificar".

---

### DIMENSIÓN 5 — EDICIÓN

#### 5.1 Cómo se edita
El Operator puede re-clasificar un inbound mal clasificado desde el panel de detalle del item en Zona 4:
1. Click en la card.
2. Dropdown "Tipo de item".
3. Selecciona nuevo tipo (ej. RFQ → consulta técnica; spam → newsletter).
4. Opcional: ajusta prioridad y agente destino.
5. Confirma. El sistema regenera la task/draft correspondiente.

#### 5.2 Qué se puede cambiar y qué no
- **Editable:** tipo de inbound, prioridad, agente asignado, etiquetas.
- **No editable:** contenido original del mensaje (inmutable por audit), remitente canonicalizado, timestamp de recepción, data class original asignada por el scanner (solo puede elevarse si el usuario confirma step-up).

#### 5.3 Qué pasa con lo generado previamente
- La task anterior se marca como `cancelled` con razón `reclassified`.
- Se crea nueva task con el tipo corregido.
- El diff (tipo original vs tipo corregido) se registra en Outcome Ledger como señal de aprendizaje.
- El item original permanece en histórico audit trail.

---

### DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

#### 6.1 Cómo se mueve (state machine del feed item)
```
received -- trigger: mensaje llega por canal, actor: system --> parsing
parsing -- trigger: parse OK --> classified
parsing -- trigger: parse error, actor: system --> retry
retry -- trigger: reintento exitoso --> classified
retry -- trigger: reintento agotado --> needs_manual_review
classified -- trigger: L1 confidence >= threshold, actor: L1 classifier --> routed_to_task
classified -- trigger: L1 confidence < threshold, actor: L1 classifier --> pending_human_review
routed_to_task -- trigger: task creada --> in_workloom (Zona 2/4/5)
pending_human_review -- trigger: Operator confirma/clasifica --> routed_to_task
pending_human_review -- trigger: Operator descarta --> archived
classified -- trigger: Tier 0 determina spam/logistica --> auto_resolved / spam
```

#### 6.2 Qué dispara el movimiento
- Automático: webhooks, L1 classifier, reglas Tier 0.
- Manual: re-clasificación del Operator.

#### 6.3 Quién puede moverlo
- **system:** transiciones automáticas de parseo/clasificación.
- **Operator:** re-clasificación, descarte, asignación manual.
- **Owner:** override de data class/prioridad.

#### 6.4 Qué se notifica y a quien
- Nuevo item accionable: badge Zona 4 + contador sidebar para Operator.
- Item urgente: badge Zona 1 + notificación push/Telegram según config.
- Error de canal: alerta a Owner.
- Item en pending_human_review: badge Zona 4 destacado.

---

### DIMENSIÓN 7 — OUTPUT

#### 7.1 Qué produce para el usuario
- **Card en Zona 4 (Inbox completo):** muestra remitente, preview, canal, tipo, confidence, SLA restante, acción primaria.
- **Card en Zona 2:** si genera draft HITL.
- **Card en Zona 1:** si se marca como urgente o SLA vencido.
- **Badge de learning:** "Este tipo de correo suele ser X".

#### 7.2 Qué produce para el sistema
- Evento `feed.item.received`.
- Evento `feed.item.dispatched` (al asignar a agente/task).
- Creación de fila en `tasks` con `invocation_mode='webhook'`.
- Registro en `outbox` (outbox pattern transaccional).
- Audit trail D10 con `actor_role_at_decision=SYSTEM`.

#### 7.3 Dónde aparece el output
- Zona 4 por defecto.
- Zona 2 si genera draft.
- Zona 1 si es urgente o falla envío.
- Historial (tab Histórico de la Mesa) después de resolución.

#### 7.4 Qué formato tiene
- `feed_item` en DB (JSONB: remitente, body, attachments, canal, data_class, classification).
- Evento JSON canónico según SPEC_FB_EVENTING_AND_OUTBOX_v1 §4.
- Card UI con campos normalizados.

---

### DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
- **Gmail down / OAuth expirado:**
  - Sistema marca canal como `degraded`.
  - Fallback a IMAP poll si está configurado.
  - Items no recibidos se reintentan con backoff exponencial (1s, 5s, 25s) hasta 3 veces.
  - Badge de error en Zona 5 (Automatizaciones) y alerta a Owner.
- **WhatsApp BSP timeout:**
  - Webhook retorna 500 al BSP para reintento.
  - Si persiste >3 intentos, item va a DLQ y se notifica a Owner.
  - En E1 según enmienda E-5 WhatsApp está diferido a E3; el fallback real es email-only + consola de log.
- **n8n no responde:**
  - Según PLB enmienda E-3, n8n vive **antes** del agente como conector pre-agente.
  - Si n8n falla, el Action Engine aplica Tier 0 determinístico directamente sobre el raw payload.
  - Si Tier 0 no cubre, escala a human review (María clasifica manual).
- **Parseo falla:** item va a `needs_manual_review` en Zona 4.
- **Clasificación L1 retorna data class no permitida (N3/N4):** Action Engine D9 hard-block; item escala a Owner.

#### 8.2 Cómo se recupera
- Reintentos automáticos con backoff.
- Fallback a canal secundario.
- Manual review por Operator/Owner.
- Reconexión de OAuth desde Settings (web).

#### 8.3 Quién se entera
- **Operator:** badge en WorkLoom.
- **Owner:** alerta Telegram/email según config.
- **Sistema:** log en Langfuse/Grafana, DLQ si aplica.
- Nivel: P1 (canal degradado), P0 (cross-tenant leak o data class violation).

---

### DIMENSIÓN 9 — APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Clasificación correcta vs corregida por el Operator.
- Tipo de inbound asignado vs tipo final confirmado.
- Tiempo que pasa un item en Zona 4 antes de acción.
- Acciones inline más usadas por tipo de item.
- Patrones de spam/false positives.

#### 9.2 Cómo mejora con el tiempo
- Tier 0 agrega reglas cuando un pattern se repite ≥N veces.
- Threshold del L1 classifier se ajusta según approval rate de clasificaciones.
- El sistema propone reglas candidate (readhide, trash_future, assign_agent) para aprobación Owner.

#### 9.3 Qué feedback da el usuario
- **Implícito:** aprobar/editar/rechazar drafts.
- **Explícito:** dropdown de razón al re-clasificar (tone / data / structure / policy / scope / context — P6 ARCH_AGENT_PRINCIPLES).
- **Candidatos a regla:** Owner aprueba/descarta desde tab Aprendizaje.

---

### DIMENSIÓN 10 — ELIMINACIÓN

#### 10.1 Cómo se elimina
N/A — el inbound nunca se borra. Puede:
- **Archivarse:** evento `feed.item.archived`; desaparece de Zona 4 pero queda en histórico.
- **Marcarse spam:** se mueve a spam folder; puede recuperarse.
- **Descartarse:** estado terminal; queda en audit trail.

#### 10.2 Qué pasa con lo que dependía
- Si se archiva/descarta un item que ya había generado task, la task se cancela.
- Los drafts dependientes se marcan como `rejected`.

#### 10.3 Es reversible
- Archivar/descartar es reversible por Owner dentro de un período configurable (default 30 días).
- Marcar spam puede revertirse manualmente.

---

### DIMENSIÓN 11 — RELACIONES

#### 11.1 Con qué se relaciona
- **n8n:** conector pre-agente (PLB E-3).
- **Action Engine:** aplica Tier 0 + políticas D9.
- **L1 classifier:** determina tipo/data_class/routing.
- **WorkLoom:** superficie donde María ve el resultado.
- **tasks:** una task se crea a partir de items accionables.
- **drafts:** si el item requiere output cliente-facing.
- **audit_log:** D10.

#### 11.2 En qué orden
```
Canal conectado → mensaje entrante → n8n (pre-proceso opcional) → Action Engine Tier 0 → L1 classifier → ActionContext → L2 Dispatcher → task → draft → WorkLoom Zona 2
```

#### 11.3 Qué rompe si este módulo falla
- Sin inbound: el workflow RFQ → cotización no arranca.
- Sin L1: los items se acumulan en Zona 4 sin routing.
- Sin canal conectado: no entran mensajes.

---

### DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
- **Operator:** items de su tenant asignados a su position; no ve items de otros tenants (RLS).
- **Owner:** todos los items del tenant.
- **Admin/Supervisor/Viewer:** E3+ según enmienda E-4.
- Nunca cross-tenant.

#### 12.2 Qué queda en el audit trail (D10)
Campos canónicos:
- `tenant_id`
- `user_id` (null si system-initiated)
- `actor_role_at_decision`: SYSTEM
- `action`: `feed.item.received` / `feed.item.dispatched` / `feed.item.archived`
- `resource_id`: feed_item_id
- `data_class`: N2
- `model_provider`: Anthropic
- `model_id`: haiku-4.5 / sonnet-4.6 según etapa
- `human_gate_required`: false (recepción no requiere gate)
- `human_approver_id`: null
- `timestamp`
- `sha_chain_prev` / `sha_chain_curr`

#### 12.3 Qué restricciones de datos aplican
- Data class típica N2.
- N3/N4 hard-block en upload según TIER 1 #3.
- Provider Anthropic-only (TIER 1 #10) con DPA vigente.
- Anonymization L2 default para N2.
- RLS en todas las queries.

---

### DIMENSIÓN 13 — DESKTOP VS WEB

#### 13.1 En cuál superficie vive
- **Desktop (Electron — WorkLoom):** operación diaria. María ve cards, re-clasifica, aprueba drafts.
- **Web (Next.js):** configuración de canales (Gmail OAuth, WhatsApp, IMAP) por Owner.
- **Canal:** presencia nativa en Gmail/WhatsApp/Telegram como origen de entrada.

#### 13.2 Diferencias entre desktop y web
- Desktop: trabajo operativo, cards, acciones inline, WebSocket push.
- Web: settings, conexión de canales, audit log, dashboards.

#### 13.3 Offline y sincronización
- Inbound requiere conexión para recibir mensajes.
- Si WorkLoom se desconecta, usa `last_event_id` para reconectar y recuperar eventos ≤24h desde Redis Streams.
- Si gap >24h, servidor responde `sync_required` y se hace re-fetch full state.

---

## MÓDULO 2: Clasificación L1

**MÓDULO:** Clasificación L1 (Action Engine Tier 0 + L1 classifier)  
**SUPERFICIE:** Backend / Desktop (WorkLoom, en modo debug/resultado)  
**SPRINT E1:** S3 (engine ejecutor genérico + Tier 0 + classify_rfq según PLB §S3)  
**ROLES QUE LO USAN:** Operator (recibe outcome), Owner/Admin (configura classifier) — E1: Owner/Operator  
**DATA CLASS TÍPICA:** Hereda del inbound (N2 default)  

---

### DIMENSIÓN 1 — EXISTENCIA

#### 1.1 Por qué existe
Sin L1, el sistema no sabe qué skill debe activar ante un inbound. Cuando María recibe un mensaje, FaberLoom no distingue si es un RFQ, spam, consulta de stock, follow-up o newsletter. El L1 classifier transforma un mensaje crudo en una decisión de routing actionable.

#### 1.2 A quién le duele
- **Operator:** le llegan items correctamente enrutados o mal clasificados.
- **Owner:** debe configurar/ajustar el classifier para que la operación sea confiable.
- **Supervisor:** mide calidad de clasificación; E3+.

#### 1.3 Cuándo aparece
Se ejecuta automáticamente para cada `feed_item` recibido, inmediatamente después del Tier 0 determinístico, antes de crear cualquier task.

---

### DIMENSIÓN 2 — PROPÓSITO

#### 2.1 Para qué
Determinar `task_type` + `data_class` + `skill_id`/`agent_id` de destino, con un confidence score que permita decidir si el item puede enrutarse automáticamente o requiere revisión humana.

#### 2.2 Qué valor entrega
- Reduce triage manual.
- Aplica políticas de datos (D9) antes de invocar cualquier skill.
- Habilita routing automático a `@cotizador`, `@stock_curator`, etc.

#### 2.3 Qué pasa si no existe
María debe leer cada inbound y decidir manualmente qué agente/skill usar. Se pierde escalabilidad y se incrementa el error humano.

---

### DIMENSIÓN 3 — CREACIÓN

#### 3.1 Cómo se crea
N/A — el L1 classifier es un componente del engine. En E1 existe como skill system `classify_rfq` creada automáticamente en tenant bootstrap (`origin='system'`, inmutable). Si el tenant necesita variantes, Owner/Admin pueden clonar el skill system en Skill Factory y ajustar prompt/schema dentro de los 14 límites duros TIER 1 #16.

#### 3.2 Quién puede crearlo
- System lo crea en bootstrap.
- Owner/Admin pueden clonar/editar skills L1 en Skill Factory (S6) con sandbox obligatorio antes de promote.

#### 3.3 Qué necesita para crearse
- Engine ejecutor genérico operativo (S3).
- Skill system `classify_rfq` seed.
- KB del tenant con work-type pack cargado (catálogo safety footwear en E1).

---

### DIMENSIÓN 4 — USO DIARIO

#### 4.1 Cómo se usa en el día a día
1. Llega un inbound.
2. Action Engine aplica **P14 Deterministic First**: reglas Tier 0 (8 reglas LATAM en `apps/api/tier0`) intentan clasificar sin LLM.
3. Si Tier 0 no cubre o confidence < threshold, escala a L1 classifier (Haiku 4.5).
4. L1 produce un `ActionContext` con:
   - `task_type` (ej. rfq, follow_up, spam, consulta_tecnica)
   - `data_class` (N0-N4)
   - `skill_id` / `agent_id` destino
   - `confidence` (0-1)
   - `routing` (zona destino, SLA)
5. Si confidence >= threshold: enruta automáticamente.
6. Si confidence < threshold: item va a pending_human_review en Zona 4.

#### 4.2 Cómo se invoca
Automático por Action Engine en cada inbound. También puede invocarse manualmente desde Workspace con "@router clasificá este correo".

#### 4.3 Qué ve el usuario mientras ocurre
- María no ve la ejecución interna directamente.
- Ve el resultado: card en Zona 4 con badge de tipo, confidence HIGH/LOW, SLA restante.
- En modo Owner/debug puede expandir "Ver cómo clasificó" para ver el ActionContext.

---

### DIMENSIÓN 5 — EDICIÓN

#### 5.1 Cómo se edita
- **Operator:** puede corregir la clasificación de un item específico desde el detalle del feed item (re-clasificar).
- **Owner/Admin:** pueden clonar el skill `classify_rfq` en Skill Factory y ajustar:
  - prompt template,
  - schema output,
  - threshold de confidence,
  - modelo (Haiku/Sonnet),
  - timeout/cost cap.
  Sandbox obligatorio antes de promote (TIER 1 #16.9).

#### 5.2 Qué se puede cambiar y qué no
- **Editable en skill clonado:** prompt, schema, threshold, modelo, timeout, cost cap (dentro de hard caps).
- **No editable en skill system:** spec sellada. Solo clonable.
- **Editable por Operator por item:** tipo de task, prioridad, agente destino.
- **No editable:** log de confianza original, el contenido analizado, el ModelFingerprint asociado.

#### 5.3 Qué pasa con lo generado previamente
- Al cambiar clasificación de un item: task anterior se cancela, se crea nueva task, evento `pattern.candidate.detected`.
- Al editar el skill L1: solo afecta items nuevos; items ya clasificados no se re-procesan salvo que Owner fuerce re-clasificación batch.

---

### DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

#### 6.1 Cómo se mueve (state machine del classifier)
```
idle -- trigger: feed_item recibido, actor: system --> classifying
classifying -- trigger: Tier 0 match --> classified
classifying -- trigger: Tier 0 no match, LLM OK --> classified
classifying -- trigger: LLM timeout/error --> failed
classified -- trigger: confidence >= approval_threshold --> routed_to_task
classified -- trigger: confidence < approval_threshold --> uncertain
uncertain -- trigger: Operator confirma tipo --> routed_to_task
uncertain -- trigger: Operator descarta --> archived
failed -- trigger: retry exitoso --> classifying
failed -- trigger: retries agotados --> manual_review
```

#### 6.2 Qué dispara el movimiento
- Automático: Tier 0 rules, LLM call, confidence threshold.
- Manual: corrección del Operator.

#### 6.3 Quién puede moverlo
- **system:** todas las transiciones automáticas.
- **Operator:** confirma/clasifica items uncertain.
- **Owner:** ajusta threshold/skill.

#### 6.4 Qué se notifica y a quien
- Item uncertain: badge Zona 4 + notificación a Operator.
- Clasificación con data class elevada: alerta a Owner.
- Falla del classifier: alerta P1 a Owner, DLQ si persiste.

---

### DIMENSIÓN 7 — OUTPUT

#### 7.1 Qué produce para el usuario
- Card en WorkLoom con tipo de item, confidence HIGH/LOW, SLA, acción primaria sugerida.
- En modo Owner: panel "Cómo clasificó" con `ActionContext` desplegado.

#### 7.2 Qué produce para el sistema
- `ActionContext` JSON con: `task_type`, `data_class`, `skill_id`, `agent_id`, `confidence`, `routing`, `payload_normalizado`.
- Eventos:
  - `feed.item.dispatched`
  - `task.created`
  - `draft.generated` (si aplica)
  - `pattern.candidate.detected` (si se corrige)
- Registro en `skill_executions` y `llm_calls`.

#### 7.3 Dónde aparece el output
- WorkLoom Zona 4 (item clasificado).
- Zona 2 (draft generado a partir de la clasificación).
- Zona 1 (si urgente).
- Outcome Ledger (señales de aprendizaje).

#### 7.4 Qué formato tiene
- JSON `ActionContext` validado contra schema del skill.
- Card UI con campos normalizados.
- Evento canónico según SPEC_FB_EVENTING_AND_OUTBOX_v1 §4.

---

### DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
- **Clasifica mal N2 como N3:**
  - Action Engine D9 hard-block: si `data_class` > `tenant_plan_ceiling`, retorna `PlanUpgradeRequired`.
  - Item no se procesa automáticamente; escala a Owner para revisión.
- **RFQ clasificado como spam:**
  - Item va a spam folder.
  - María puede recuperarlo desde Zona 4 filtro "Spam" y re-clasificar.
  - Se genera evento `pattern.candidate.detected` para ajustar reglas.
- **L1 confidence muy bajo:**
  - Item queda en `uncertain` / pending_human_review.
  - María clasifica manualmente.
- **LLM timeout / error:**
  - Reintentos (3x con backoff).
  - Si persiste, fallback a Tier 0 + reglas default; si no cubre, escala a humano.

#### 8.2 Cómo se recupera
- Re-clasificación manual.
- Ajuste de threshold/prompt en Skill Factory (Owner/Admin).
- Revisión de reglas Tier 0.
- Promoción de candidatos a reglas desde tab Aprendizaje.

#### 8.3 Quién se entera
- **Operator:** items mal ubicados en Zona 4.
- **Owner:** alertas de configuración, métricas de clasificación.
- **Sistema:** Outcome Ledger, Langfuse traces, DLQ si aplica.

---

### DIMENSIÓN 9 — APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Delta entre clasificación L1 y corrección humana.
- Confidence vs outcome real.
- Tiempo de decisión del Operator.
- Frecuencia de tipos de inbound por canal/hora.
- Patrones de spam/false positives.

#### 9.2 Cómo mejora con el tiempo
- Ajuste dinámico de threshold.
- Agregar reglas a Tier 0 cuando un pattern se repite.
- Actualización del skill L1 clonado con nuevos ejemplos.
- Generación de candidatos a reglas/gold samples.

#### 9.3 Qué feedback da el usuario
- **Implícito:** aceptar/editar/rechazar drafts generados a partir de la clasificación.
- **Explícito:** re-clasificar + dropdown de razón (P6 ARCH_AGENT_PRINCIPLES).
- **Aprendizaje accionable:** Owner aprueba/descarta candidatos en tab Aprendizaje.

---

### DIMENSIÓN 10 — ELIMINACIÓN

#### 10.1 Cómo se elimina
N/A — el L1 classifier es un componente del sistema. El skill system `classify_rfq` no se elimina. Un skill L1 clonado por el tenant puede:
- **Pausarse:** deja de usarse para nuevos items.
- **Deprecarse:** estado terminal, no se puede invocar pero queda en histórico.
- **No borrarse:** FaberLoom depreca, no borra.

#### 10.2 Qué pasa con lo que dependía
- Si se pausa/depreca un skill L1 clonado, los items pasan a usar el skill system default o el siguiente skill activo.
- Las ejecuciones históricas quedan en `skill_executions`.

#### 10.3 Es reversible
- Pausar es reversible.
- Deprecar es reversible por Owner (vuelve a ACTIVE) si no hay incompatibilidad.

---

### DIMENSIÓN 11 — RELACIONES

#### 11.1 Con qué se relaciona
- **Recibe de:** n8n (pre-proceso), Action Engine Tier 0, feed item.
- **Alimenta a:** L2 Dispatcher, task creation, WorkLoom, Outcome Ledger, Agent Memory.
- **Depende de:** Skill Factory (config), KB (contexto), Action Engine (políticas).

#### 11.2 En qué orden
```
feed_item → Tier 0 deterministic → L1 classifier → ActionContext → L2 Dispatcher → task → skill execution → draft → WorkLoom Zona 2
```

#### 11.3 Qué rompe si este módulo falla
- Si L1 no existe: todo inbound queda sin clasificar; acumulación en Zona 4.
- Si L1 clasifica mal: drafts van a skill/agente equivocado; posible envío incorrecto si no hay HITL.
- Si el HITL funciona, el error de L1 se corrige en Zona 2, pero genera fricción operativa.

---

### DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
- **Operator:** resultado aplicado a sus items (tipo, confidence en card).
- **Owner/Admin:** config del skill L1, métricas, debug.
- **Viewer:** E3+, solo historial.
- Todo filtrado por tenant_id (RLS).

#### 12.2 Qué queda en el audit trail (D10)
- `tenant_id`
- `user_id` (null si system-initiated)
- `actor_role_at_decision`: SYSTEM u OPERATOR si corrige
- `action`: `feed.item.dispatched` / `task.created` / `pattern.candidate.detected`
- `resource_id`: feed_item_id / task_id
- `data_class`: heredado del inbound (N2 típico)
- `model_provider`: Anthropic
- `model_id`: haiku-4.5
- `human_gate_required`: false para clasificación; true si genera draft
- `human_approver_id`: null en clasificación automática
- `timestamp`
- `sha_chain_prev` / `sha_chain_curr`

#### 12.3 Qué restricciones de datos aplican
- **P14 Deterministic First:** Tier 0 primero, LLM fallback solo si no cubre.
- **D9 Data Classification Routing:** data class heredado; N3/N4 hard block si supera ceiling.
- **TIER 1 #16:** skill L1 solo puede ser `classifier`, sin tools externas, sin HTTP, sin code exec, timeout ≤60s, cost cap ≤USD 2.00.
- **Anthropic-only** con DPA vigente.

---

### DIMENSIÓN 13 — DESKTOP VS WEB

#### 13.1 En cuál superficie vive
- **Backend:** la clasificación ocurre en el servidor.
- **Desktop (WorkLoom):** María ve el resultado (cards, confidence, acciones).
- **Web (Skill Factory):** Owner/Admin configuran/clonan el skill L1.

#### 13.2 Diferencias entre desktop y web
- Desktop: operación, corrección por item, visualización de outcome.
- Web: configuración del skill, sandbox test, promote, history versions.

#### 13.3 Offline y sincronización
- Clasificación ocurre en backend; desktop recibe eventos vía WebSocket.
- Si WorkLoom está offline, los eventos se acumulan en Redis Streams hasta 24h y se sincronizan al reconectar con `last_event_id`.

---

## PENDIENTES que requieren decisión CEO

1. **[PENDIENTE — doc en stub]** ENT_FB_INBOUND_TAXONOMY_v1.md está como STUB. Se necesita definir los 13 tipos de inbound y, específicamente, qué representan los tipos 1-2 asignados a este módulo (Gmail/WhatsApp).

2. **[PENDIENTE — doc en stub]** ENT_FB_WORK_TYPE_PACK_v1.md está como STUB. Se necesita confirmar el seed del work-type pack "safety footwear" para E1 y cómo impacta las labels de clasificación L1.

3. **[PENDIENTE — contradicción con enmienda E-5]** El prompt pide cubrir inbound WhatsApp, pero PLB_FB_FOUNDATION_BETA_v1.md enmienda E-5 establece "email-only en E1-E2; WhatsApp Business y multi-buzón completo a E3". Se necesita decisión CEO sobre si este módulo en E1 cubre solo Gmail o también WhatsApp.

4. **[PENDIENTE — roles E1]** PLB enmienda E-4 reduce roles E1 a Owner/Operator, pero SCH_FB_FUNCTIONAL_SPEC_v1 y el contexto general mencionan 5 roles canónicos. Se necesita aclarar si las fichas funcionales E1 usan 2 roles (Owner/Operator) o 5 roles con notas de "E3+".

5. **[PENDIENTE — n8n en E1]** Según SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 §3.2 y PLB E-3, n8n vive "antes del agente" en E1. Se necesita confirmar si el flujo inbound E1 incluye n8n obligatoriamente o solo como opción, y cuál es el fallback exacto si n8n no responde.

6. **[PENDIENTE — 13 features del classifier]** El prompt menciona "los 13 features del classifier". No se encontró en los docs de lectura obligatoria una lista de 13 features del L1 classifier. Se requiere el documento o decisión CEO sobre cuáles son.

7. **[PENDIENTE — ActionContext exacto]** El prompt pide que L1 produzca "ActionContext con task_type + data_class + skill_id". El ActionContext de SPEC_ACTION_ENGINE.md §Contract API incluye más campos. Se necesita confirmar el schema mínimo vs completo para E1.

---

## CONTRADICCIONES DETECTADAS CON LA KB

1. **Canales E1: WhatsApp vs email-only**
   - **Prompt/contexto general:** Canales incluyen WhatsApp BSP, Telegram Bot, Gmail/IMAP, Desktop app.
   - **PLB_FB_FOUNDATION_BETA_v1.md enmienda E-5:** "email-only en E1-E2 (Gmail OAuth out; IMAP in para lectura); WhatsApp Business y multi-buzón completo a E3".
   - **Impacto:** La ficha cubre WhatsApp como inbound, pero el plan firmado lo difiere a E3. Esto es una contradicción que requiere resolución CEO.

2. **Roles canónicos: 5 vs 2 en E1**
   - **Contexto general / SCH_FB_FUNCTIONAL_SPEC_v1:** 5 roles canónicos (Owner / Admin / Operator / Supervisor / Viewer).
   - **PLB_FB_FOUNDATION_BETA_v1.md enmienda E-4:** "2 roles en E1 (Owner, Operator); los 5 roles entran en E3".
   - **Impacto:** Las fichas funcionales deben aclarar que Admin/Supervisor/Viewer son E3+ o asumir el plan firmado de 2 roles.

3. **Mesa de Control: panel lateral izquierdo vs Workspace**
   - **Contexto general:** "Panel lateral izquierdo: agentes on/off, aprendizaje en curso".
   - **SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 §8.2:** "los toggles on/off de agentes + el panel de aprendizaje en curso viven en el Workspace como hero (no en Mesa). Mesa queda solo con items que requieren atención (full width sin panel lateral)".
   - **Impacto:** El contexto general contradice el spec puente. Se mantiene lo del spec puente (Workspace) para no contradecir KB vigente.

4. **Skill L1: 14 límites duros vs prompt**
   - **Prompt:** pide que L1 classifier use "P14 Deterministic First, los 13 features del classifier".
   - **PLB TIER 1 #16 / SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1:** establecen 14 límites duros para skills, no 13 features.
   - **Impacto:** No se encontró documento con "13 features del classifier". Se usaron los 14 límites duros como guardrails y se marcó pendiente la lista de 13 features.

5. **Engine de skills: SkillSpec en DB vs markdown versionado**
   - **PLB_FB_FOUNDATION_BETA_v1.md (plan original):** "Engine ejecutor genérico lee SkillSpec de DB, Pydantic dinámico".
   - **PLB enmienda E-3:** "skill = markdown versionado + tools allowlist + schema de salida, ejecutado como capa fina sobre SDK estándar".
   - **Impacto:** El modelo de persistencia del skill cambió. La ficha funcional no necesita decidir implementación, pero la contradicción debe ser resuelta por CEO/arquitecto antes de codificar.

6. **Sub-agentes: permitidos vs bloqueados E1**
   - **SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 §3.1:** sub-agentes como agentes standalone permitidos E1; composición jerárquica bloqueada E1.
   - **PLB_FB_FOUNDATION_BETA_v1.md TIER 1 #15:** "NO sub-agentes".
   - **Impacto:** Contradicción sobre si "sub-agentes" existen en E1. El spec puente aclara que son standalone, no jerárquicos, pero el plan firmado original los prohíbe tajantemente. Requiere clarificación.

---

*Fin de ficha funcional — Módulo 01.*
