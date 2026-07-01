# FaberLoom Foundation Beta E1 — Módulo 02: Task + Draft y aprobación HITL

> Ficha funcional generada por AGENTE_2_TASK_DRAFT del swarm de especificación funcional.
> Docs base leídos: SCH_FB_FUNCTIONAL_SPEC_v1, PLB_FB_FOUNDATION_BETA_v1, SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1, SPEC_FB_AUTH_TENANT_RBAC_v1, SPEC_ACTION_ENGINE, ARCH_AGENT_PRINCIPLES, POL_DATA_CLASSIFICATION, ENT_FB_INBOUND_TAXONOMY_v1 (stub), SPEC_FB_ROUTINES_v1 (stub), SPEC_FB_WORKSPACE_v1 (stub), ENT_FB_WORK_TYPE_PACK_v1 (stub), SPEC_FABERLOOM_WORKFLOW_ENGINE_v1, SPEC_FABERLOOM_AGENT_COMPOSITION_v1, SCH_FB_TASK_ENTITY, SPEC_FB_EVENTING_AND_OUTBOX_v1.

---

## MÓDULO 3 — TASK (unidad de ejecución)

**MÓDULO:** Task  
**SUPERFICIE:** Backend + Desktop (WorkLoom)  
**SPRINT E1:** S3 (engine ejecutor genérico + tabla tasks)  
**ROLES QUE LO USAN:** Owner, Operator (roles Admin / Supervisor / Viewer entran en E3 según enmienda E-4 de PLB_FB_FOUNDATION_BETA_v1.3.2)  
**DATA CLASS TÍPICA:** Hereda del inbound/originador (N2 para RFQ safety footwear B2B)

---

### DIMENSIÓN 1 — EXISTENCIA

#### 1.1 Por qué existe
María (Operator) procesa 20-30 tareas mixtas por día. Sin `task` no hay forma de saber qué está ejecutando el sistema, qué está esperando su aprobación, qué falló y qué ya se completó. Hoy, sin este módulo, María tendría que rastrear manualmente cada RFQ, cada cotización pendiente y cada error en canales separados (email, WhatsApp, hojas de cálculo). Con `task`, cada unidad de trabajo es una fila trackeable con estado, historia y auditoría.

#### 1.2 A quién le duele
- **Operator:** es quien ve y actúa sobre las tareas en la Mesa de Control.
- **Owner:** necesita métricas de throughput, errores y costos por tarea.

#### 1.3 Cuándo aparece
Aparece automáticamente cuando:
- Llega un inbound clasificado (feed.item.received) y el router decide que requiere ejecución.
- Una rutina programada o webhook dispara una ejecución.
- María crea una tarea ad-hoc desde Workspace o Mesa.
- Un flow padre spawnea un nodo hijo.

---

### DIMENSIÓN 2 — PROPÓSITO

#### 2.1 Para qué
Ser la unidad atómica de trabajo trackeable: cada invocación de un agente/skill/flujo queda registrada con estado, input, output, costo, auditoría y HITL granular.

#### 2.2 Qué valor entrega
- María sabe en una sola pantalla qué requiere su atención.
- El sistema puede medir latencia, costo y tasa de aprobación por tipo de tarea.
- Permite HITL por output específico (no por agente entero).

#### 2.3 Qué pasa si no existe
No hay trazabilidad operativa. Los drafts se pierden entre canales, los errores no se recuperan y no hay datos para decidir autonomía.

---

### DIMENSIÓN 3 — CREACIÓN

#### 3.1 Cómo se crea
Existen 4 modos de invocación canónicos (SCH_FB_TASK_ENTITY §Schema):

1. **ad_hoc** — María crea manualmente la tarea desde Workspace o Mesa. Ejemplo: "@cotizador, preparame una respuesta para el cliente ACME que preguntó por botas 6020".
2. **scheduled** — Una rutina de Proceso dispara la tarea por cron. Ejemplo: `@seguidor_rfq` corre a las 6:00 AM y genera tareas de seguimiento para RFQs sin respuesta.
3. **webhook** — Un evento externo (Gmail push, webhook de plataforma) crea la tarea. Ejemplo: llega un nuevo email a `ventas@marluvas.com` y el webhook crea task de clasificación.
4. **flow_node** — Un workflow padre spawnea la tarea como nodo hijo. Ejemplo: workflow de cotización crea sub-tasks `validar_input`, `consultar_stock`, `generar_draft`.

#### 3.2 Quién puede crearlo
- **system** (inbound, webhook, scheduled).
- **Operator / Owner** (ad-hoc).
- **flow** (flow_node).

#### 3.3 Qué necesita para crearse
- `agent_id` (skill o agente que ejecutará).
- `payload` (input JSON acorde al schema del skill).
- `invocation_mode`.
- `tenant_id` (RLS).
- Opcional: `priority`, `parent_task_id`, `flow_node_id`.

Si falta el schema del payload, el engine rechaza la creación antes de encolar.

---

### DIMENSIÓN 4 — USO DIARIO

#### 4.1 Cómo se usa en el día a día
1. María abre WorkLoom (desktop).
2. Ve cards que representan tareas en distintas zonas según su estado:
   - `awaiting_approval` → Zona 2 (Esperando tu firma).
   - `failed` con SLA crítico → Zona 1 (Lo urgente).
   - `running` o `queued` → Zona 4 (Inbox completo) o Zona 1 si es urgente.
3. Hace click en una card para abrir el panel de draft + evidence.
4. Aprueba, edita o rechaza.
5. El sistema mueve la tarea a `completed` o `failed` y actualiza la Mesa en tiempo real.

#### 4.2 Cómo se invoca
- Automático: inbound → router → task.
- Manual: `@agente` en composer de Workspace/Mesa o botón "Nueva tarea".
- Programado: rutinas en Zona 5.
- Por workflow: ejecución de flow padre.

#### 4.3 Qué ve el usuario mientras ocurre
- **Inicial:** card en Zona 4 con spinner "Procesando...".
- **En ejecución:** estado `running`, costo acumulado visible para Owner (Operator no ve costo en E1 según decisión CEO #5 de PLB §5).
- **Awaiting approval:** card migra a Zona 2 con badge "Listo para revisar".
- **Completed:** card desaparece de zonas activas; queda en historial.
- **Failed:** badge de error en Zona 1 o Zona 4 según severidad.

---

### DIMENSIÓN 5 — EDICIÓN

#### 5.1 Cómo se edita
No se edita el objeto `task` directamente. Las modificaciones operativas son:
- **Reasignar:** cambiar `agent_id` o `priority` antes de que arranque (solo Owner/Operator con permiso).
- **Cancelar:** transición `queued`/`awaiting_approval` → `cancelled`.
- **Aprobar/Rechazar/Editar:** acciones sobre el draft asociado, no sobre la task en sí.

#### 5.2 Qué se puede cambiar y qué no
- **Cambiable:** `priority`, `agent_id` (solo en `queued`), `review_notes`, `review_status` (vía flujo HITL).
- **Inmutable:** `invocation_mode`, `invoked_by`, `payload` original, `tenant_id`, `created_at`. Son el contrato de replay/auditoría.

#### 5.3 Qué pasa con lo generado previamente
Outputs aprobados se conservan. Ediciones se guardan como nuevo output con diff auditado. La task original permanece inmutable; los cambios son nuevas transiciones de estado.

---

### DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

#### 6.1 State machine completa
Estados canónicos (SCH_FB_FUNCTIONAL_SPEC_v1 §Referencias canónicas):

```
created -- trigger: sistema/operador crea task --> running
running -- trigger: worker toma la tarea --> awaiting_approval
running -- trigger: ejecución exitosa sin HITL --> completed
running -- trigger: error técnico --> failed
running -- trigger: timeout del worker/skill --> failed (timeout como subclass)
created -- trigger: cancelación manual antes de running --> cancelled
awaiting_approval -- trigger: Operator aprueba --> completed (o continúa ejecución side-effect)
awaiting_approval -- trigger: Operator rechaza --> failed / cancelled
awaiting_approval -- trigger: Operator edita + aprueba --> completed
awaiting_approval -- trigger: SLA vence sin respuesta --> failed / escalated
```

Nota técnica: SCH_FB_TASK_ENTITY.md usa `queued` como estado inicial en lugar de `created` y añade `timeout` como estado separado. En la ficha funcional se usa `created` como estado conceptual al crearse; en DB el schema vigente registra `queued` para el mismo momento.

#### 6.2 Qué dispara el movimiento
- `created → running`: worker Celery hace pickup del job.
- `running → awaiting_approval`: el skill emite output con `requires_human_approval=true`.
- `running → completed`: skill termina sin requerir aprobación.
- `running → failed`: excepción no controlada, skill_failed (TIER 1 #16.14), o timeout.
- `awaiting_approval → completed`: Operator aprueba o edita+aprueba.
- `awaiting_approval → failed`: Operator rechaza o vence SLA.
- `created → cancelled`: Operator/Owner cancela antes de ejecución.

#### 6.3 Quién puede moverlo
| Transición | Rol |
|---|---|
| created → running | system (worker) |
| running → * | system (engine) |
| awaiting_approval → completed/failed | Operator (own) / Owner (tenant-wide) |
| created → cancelled | Operator / Owner |

#### 6.4 Qué se notifica y a quién
- Entra a `awaiting_approval`: badge en Zona 2 + WebSocket push.
- Vence SLA: badge Zona 1 + notificación al Owner/Operator según `position assignment` del agente.
- Falla técnica: log en audit + alerta P1 en observabilidad.

---

### DIMENSIÓN 7 — OUTPUT

#### 7.1 Qué produce para el usuario
- Card en WorkLoom que representa la tarea.
- Draft(s) asociados para aprobación cuando aplica.
- Historial de ejecución con costo, latencia y decisiones.

#### 7.2 Qué produce para el sistema
- Registro en tabla `tasks`.
- `skill_executions` por cada skill ejecutada.
- `llm_calls` por cada llamada a modelo.
- Eventos canónicos correspondientes (ver 7.4).

#### 7.3 Dónde aparece el output
- Zona 1: urgente/falla.
- Zona 2: awaiting_approval.
- Zona 4: inbox completo/historial.
- Panel de detalle al hacer click en card.

#### 7.4 Qué formato tiene
- **Para UI:** card con metadata (cliente, tipo, canal, confidence, SLA, acción primaria).
- **Para sistema:**
  - `tasks.outputs` → JSONB con mapa `{output_id: {value, schema_compliant, persisted_to}}`.
  - Eventos canónicos posibles según SPEC_FB_EVENTING_AND_OUTBOX_v1 §3:
    - `feed.item.dispatched` (cuando inbound se asigna a agente/task).
    - `draft.generated` (cuando task produce draft).
    - `draft.approved`, `draft.edited`, `draft.rejected`, `draft.sent`.
    - `agent.alarma` (cuando task falla y requiere atención).
    - `cost.threshold` (si excede budget).

---

### DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
| Tipo de fallo | Comportamiento | Qué ve María |
|---|---|---|
| Worker muere a mitad | Celery reintenta según `max_retries`. Si persiste → DLQ + task `failed`. | Badge error en Zona 1. |
| LLM timeout | Skill aborta, `task.status=failed`, `error_code=timeout`. | "El agente tardó demasiado. Se escaló." |
| DB unreachable | Transacción falla, task queda `queued`, reintentos con backoff. | Mensaje transitorio; no se pierde la tarea. |
| Skill falla | TIER 1 #16.14: `task.status=skill_failed`, agente NO se cae. | Card en Zona 1 con acción "Reintentar / Escalar". |
| Permisos insuficientes | 403, task no se crea/ejecuta. | "No tenés permiso para ejecutar este agente." |

#### 8.2 Cómo se recupera
- **Retry automático:** Celery `max_retries=2` simple en E1 (SCH_FB_TASK_ENTITY §Limitaciones v1); retry exponencial en E2.
- **DLQ:** eventos/tareas fallidas van a `dead_letter_queue` (PLB §2.1).
- **Reintentar manual:** Owner/Operator puede reenviar una task `failed` a `created`/`queued`.
- **Circuit breaker:** si 3 fallos consecutivos, abre circuito y usa fallback template (SPEC_FABERLOOM_WORKFLOW_ENGINE_v1 §6).

#### 8.3 Quién se entera
- Operator: errores que le corresponden por `position assignment`.
- Owner: alertas P1/P0 por costo, leak, o fallas críticas.
- Observabilidad: Langfuse/Grafana trace + Prometheus alertas.

---

### DIMENSIÓN 9 — APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Tiempo de resolución por tipo de task.
- Tasa de aprobación / edición / rechazo por agente/skill.
- Costo promedio por tarea completada.
- Patrones de falla (timeout, skill_failed, schema invalid).

#### 9.2 Cómo mejora con el tiempo
- Los outputs aprobados sin edición se convierten en candidate gold samples.
- Los diffs de edición alimentan el Outcome Ledger y el skill refinement.
- Las métricas de approval rate habilitan la promoción de autonomía (ARCH_AGENT_PRINCIPLES P4).

#### 9.3 Qué feedback da el usuario
- Implícito: aprobar, editar, rechazar, cancelar.
- Explícito: dropdown de razón al rechazar/editar (ARCH_AGENT_PRINCIPLES P6): `tone`, `data`, `structure`, `policy`, `scope`, `context`.

---

### DIMENSIÓN 10 — ELIMINACIÓN

#### 10.1 Cómo se elimina
No se elimina físicamente. Se cancela (`status=cancelled`) o se archiva en historial. FaberLoom depreca, no borra (SCH_FB_FUNCTIONAL_SPEC_v1 §10.1).

#### 10.2 Qué pasa con lo que dependía
- Drafts asociados quedan como `rejected` o `expired`.
- Sub-tasks hijas se cancelan en cascada si el padre se cancela.
- Los outputs ya enviados no se revierten.

#### 10.3 Es reversible
- `cancelled` no es reversible a `created` directamente; se crea una nueva task.
- `failed` puede reintentarse (nueva ejecución, mismo `task_id` con historial).

---

### DIMENSIÓN 11 — RELACIONES

#### 11.1 Con qué se relaciona
- **Inbound / Rutina / Usuario:** crean la task.
- **Agente + Skill:** ejecutan la task.
- **Celery worker:** consume la task.
- **Draft:** output que requiere HITL.
- **Audit D10:** registra cada transición.
- **Outcome Ledger:** recibe diffs y decisiones.

#### 11.2 En qué orden
```
Inbound / Rutina / Ad-hoc / Flow-node → Task creada → Worker pickup → Skill execution → Draft (si HITL) → Aprobación → Completed/Failed/Cancelled
```

#### 11.3 Qué rompe si este módulo falla
- Toda la Mesa de Control queda sin contenido.
- No hay HITL granular.
- No hay métricas de throughput ni costo.
- El engine no puede ejecutar skills de forma trackeable.

---

### DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
- **Operator:** tasks asignadas a su position / creadas por él.
- **Owner:** todas las tasks del tenant.
- **Viewer:** solo historial (rol no activo en E1 según enmienda E-4).
- Nunca cross-tenant: RLS en `tenant_id`.

#### 12.2 Qué queda en el audit trail D10
Campos obligatorios según SCH_FB_FUNCTIONAL_SPEC_v1 §12.2 y SPEC_ACTION_ENGINE D10:
- `tenant_id`, `user_id`, `actor_role_at_decision`
- `action` (task.created, task.running, task.awaiting_approval, task.completed, task.failed, task.cancelled)
- `resource_id` (task_id)
- `data_class` (heredada del inbound)
- `model_provider`, `model_id` (si aplica)
- `human_gate_required` (true cuando entra a awaiting_approval)
- `human_approver_id` (si hay aprobación)
- `timestamp`, `sha_chain_prev`, `sha_chain_curr`

#### 12.3 Qué restricciones de datos aplican
- Hereda `data_class` del inbound originador.
- RFQ safety footwear B2B = N2 por defecto (pricing, márgenes, datos de cliente).
- N3/N4 prohibidos en E1 (TIER 1 #3 de PLB).
- Solo providers con DPA reconocido (Anthropic-only en E1, decisión CEO #7 PLB §5).

---

### DIMENSIÓN 13 — DESKTOP vs WEB

#### 13.1 En cuál superficie vive
- **Backend:** tabla `tasks`, worker Celery, engine ejecutor.
- **Desktop (Electron):** WorkLoom muestra las cards y permite acciones.
- **Web (Next.js):** Owner puede ver histórico y métricas; no es superficie primaria de operación.

#### 13.2 Diferencias entre desktop y web
- Desktop: cards en zonas, acciones inline, aprobación HITL, notificaciones WebSocket en tiempo real.
- Web: vista de historial + métricas; no se opera el día a día desde web en E1.

#### 13.3 Offline y sincronización
- E1 no funciona offline. Requiere conexión para validar permisos, ejecutar skills y mover estados.
- Si se pierde conexión durante revisión de draft, el borrador se guarda localmente y se sincroniza al reconectar (mismo patrón que ejemplo de plantilla para draft).

---

## MÓDULO 4 — DRAFT Y APROBACIÓN HITL POR OUTPUT

**MÓDULO:** Draft y aprobación HITL por output  
**SUPERFICIE:** Desktop (Electron) — WorkLoom Zona 2  
**SPRINT E1:** S5 (Mesa de Control + HITL + canales)  
**ROLES QUE LO USAN:** Operator, Owner (Admin / Supervisor / Viewer entran en E3 según enmienda E-4 de PLB_FB_FOUNDATION_BETA_v1.3.2)  
**DATA CLASS TÍPICA:** N2

---

### DIMENSIÓN 1 — EXISTENCIA

#### 1.1 Por qué existe
María recibe drafts generados por `@cotizador` y otros agentes Cognitivos. Sin HITL, el agente podría enviar al cliente una cotización con precio incorrecto, tono inapropiado o datos inventados (ARCH_AGENT_PRINCIPLES P3: draft-first absoluto). Hoy, sin este módulo, María tendría que revisar cada respuesta en el canal original (Gmail/WhatsApp) copiando y pegando, sin contexto ni evidence bundle.

#### 1.2 A quién le duele
- **Operator:** aprueba el 90% de los drafts diarios.
- **Owner:** es responsable legal de las comunicaciones externas; necesita audit trail.

#### 1.3 Cuándo aparece
Aparece automáticamente cuando un skill/agente genera un output con `requires_human_gate=true` o `requires_human_approval=true`. El evento `draft.generated` se emite y la card aparece en Zona 2 vía WebSocket.

---

### DIMENSIÓN 2 — PROPÓSITO

#### 2.1 Para qué
Que María revise y apruebe cualquier comunicación externa o acción de alto impacto antes de que salga del sistema.

#### 2.2 Qué valor entrega
Reduce de 8-15 min a 1-2 min el ciclo de revisión de un RFQ rutinario, porque todo el contexto (draft + evidence bundle) está en un solo panel.

#### 2.3 Qué pasa si no existe
El workflow se detiene: P3 prohíbe envío autónomo. Los drafts se acumulan sin salida y María pierde confianza en el agente.

---

### DIMENSIÓN 3 — CREACIÓN

#### 3.1 Cómo se crea
N/A — no se crea manualmente. Se genera automáticamente cuando un skill/agente emite output con `requires_human_gate=true`.

#### 3.2 Quién puede crearlo
El sistema, como resultado de la ejecución de una task.

#### 3.3 Qué necesita para crearse
- Task en ejecución.
- Skill que declare output con `requires_human_approval=true`.
- Evidence bundle asociado (contexto que justifica el draft).
- `human_responsable` resuelto según `position assignment` del agente (ARCH_AGENT_PRINCIPLES glosario).

---

### DIMENSIÓN 4 — USO DIARIO

#### 4.1 Cómo se usa en el día a día
1. María abre WorkLoom; Zona 2 muestra cards "Listo para revisar".
2. Lee la card en 3 segundos: cliente, tipo, confidence HIGH/LOW, SLA restante.
3. Hace click y abre el panel completo: draft + evidence bundle.
4. Decide: **Aprobar**, **Editar+Aprobar**, o **Rechazar**.
5. Si edita, usa modo inline con diff en tiempo real y selecciona razón del cambio.
6. Al aprobar, el sistema envía por el canal configurado y registra audit.

#### 4.2 Cómo se invoca
- Automático: aparece en Zona 2 cuando el agente termina.
- Badge en sidebar con contador de drafts pendientes.
- Notificación si el item es urgente (Zona 1).

#### 4.3 Qué ve el usuario mientras ocurre
- **Inicial:** card en Zona 2 con badge "Listo para revisar".
- **Al abrir:** panel con draft + evidence bundle + acciones.
- **Al aprobar:** animación check, card desaparece de Zona 2.
- **Al editar:** modo inline con diff y dropdown de razón.
- **Al rechazar:** modal para razón tipificada; card va a historial como rechazada.

---

### DIMENSIÓN 5 — EDICIÓN

#### 5.1 Cómo se edita
María edita inline en el panel de revisión. El sistema captura el diff automáticamente.

#### 5.2 Qué se puede cambiar y qué no
- **Editable:** el texto del draft completo (salvo bloques de compliance).
- **No editable:** evidence bundle (inmutable), metadata del caso (origen, trace_id, timestamp).
- [PENDIENTE — definir threshold de margen del tenant y qué campos de pricing quedan bloqueados por política de compliance]

#### 5.3 Qué pasa con lo generado previamente
- Draft original se preserva en audit trail.
- Draft editado es el que se envía.
- Diff (original vs editado) va al Outcome Ledger como señal de aprendizaje.

---

### DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

#### 6.1 State machine completa
Estados canónicos de draft (SCH_FB_FUNCTIONAL_SPEC_v1 §Referencias canónicas):

```
pending -- trigger: agente termina output --> awaiting_approval
awaiting_approval -- trigger: Operator aprueba --> approved
awaiting_approval -- trigger: Operator edita+aprueba --> edited
awaiting_approval -- trigger: Operator rechaza --> rejected
approved/edited -- trigger: sistema envía por canal --> sent
awaiting_approval -- trigger: SLA vence sin decisión --> expired
```

#### 6.2 Qué dispara el movimiento
- `pending → awaiting_approval`: task genera output con HITL.
- `awaiting_approval → approved/edited/rejected`: acción de María.
- `approved/edited → sent`: envío automático post-aprobación por canal configurado (email en E1-E2 según enmienda E-5).
- `awaiting_approval → expired`: vencimiento del SLA configurado.

#### 6.3 Quién puede moverlo
| Transición | Rol |
|---|---|
| pending → awaiting_approval | system |
| awaiting_approval → approved/edited/rejected | Operator (own) / Owner (override) |
| approved/edited → sent | system (post HITL) |
| awaiting_approval → expired | system por timeout |

#### 6.4 Qué se notifica y a quién
- Aprobación: silenciosa (flujo normal), confirmación toast "Enviado a [cliente] por [canal]".
- Rechazo: toast al Operator + log audit.
- Expiración: badge Zona 1 + notificación al Owner/Operator responsable.

---

### DIMENSIÓN 7 — OUTPUT

#### 7.1 Qué produce para el usuario
- Draft enviado al cliente por canal configurado del tenant.
- Confirmación visual de envío.
- Historial de decisión con timestamp y actor.

#### 7.2 Qué produce para el sistema
- Eventos:
  - `draft.generated`
  - `draft.approved` o `draft.edited`
  - `draft.sent`
  - `draft.rejected` (si aplica)
- Registro Outcome Ledger: decisión + diff + timestamp + actor_role.
- Candidate gold sample si aprobó sin edición y confidence HIGH.
- Audit D10 con `human_approver_id`.

#### 7.3 Dónde aparece el output
- Card desaparece de Zona 2.
- Aparece en historial (tab Historial de la Mesa).
- Cliente recibe mensaje por el canal configurado (email en E1-E2; WhatsApp differido a E3 según enmienda E-5).

#### 7.4 Qué formato tiene
- **Para usuario:** draft como texto/body + metadatos del caso.
- **Para sistema:**
  - Registro en tabla `drafts` / `draft_decisions` (schema PLB §2.3).
  - Eventos canónicos de SPEC_FB_EVENTING_AND_OUTBOX_v1 §3.3.
  - Audit entry inmutable con SHA-chain.

---

### DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
| Tipo de fallo | Comportamiento | Qué ve María |
|---|---|---|
| Fallo de envío | Draft queda en `approved_pending_send`; reintento auto 3 veces con backoff. | Badge error en Zona 1. |
| Permisos insuficientes | 403; card sigue en Zona 2 para otro Operator/Owner. | "No tenés permiso para aprobar este draft." |
| Compliance bloquea envío | `draft.signature_blocked`; escala a Owner. | "Bloqueado por política de compliance." |
| Expiración de draft | Estado `expired`; el sistema notifica y ofrece regenerar. | "Este draft venció. ¿Regenerar?" |

#### 8.2 Cómo se recupera
- Fallo de envío: reintentos automáticos; si persisten, alerta al Owner.
- Rechazo: el feedback tipificado se usa para ajustar el skill.
- Expiración: Owner/Operator puede regenerar la task o descartar.

#### 8.3 Quién se entera
- Operator: fallos propios y drafts pendientes.
- Owner: fallos de envío persistentes, bloqueos de compliance, expiraciones masivas.
- Observabilidad: Langfuse trace + Prometheus alertas P1/P2.

---

### DIMENSIÓN 9 — APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Aprobación sin edición + confidence HIGH → candidate gold sample.
- Edición antes de aprobar → diff capturado en Outcome Ledger.
- Rechazo → razón tipificada registrada para ajuste del skill.
- Tiempo de decisión → contribuye a UserControlProfile / complacency_score.

#### 9.2 Cómo mejora con el tiempo
- Gold samples promovidos mejoran few-shot dinámico del skill.
- Diffs frecuentes disparan skill refinement o actualización de contexto (ARCH_AGENT_PRINCIPLES P11).
- Baja tasa de edición habilita promoción de autonomía (P4).

#### 9.3 Qué feedback da el usuario
- Implícito: aprobar / editar / rechazar.
- Explícito: dropdown de razón al rechazar o editar (P6): `tone`, `data`, `structure`, `policy`, `scope`, `context`.

---

### DIMENSIÓN 10 — ELIMINACIÓN

#### 10.1 Cómo se elimina
N/A — los drafts no se eliminan. Se rechazan (`rejected`) o vencen (`expired`). Ambos estados quedan en audit trail permanentemente.

#### 10.2 Qué pasa con lo que dependía
- Si un draft rechazado era output de una task, la task pasa a `failed` o `cancelled`.
- El cliente no recibe nada.
- El feedback alimenta el learning loop.

#### 10.3 Es reversible
- `rejected` no es reversible a `awaiting_approval`; se regenera una nueva task/draft.
- `expired` puede regenerarse manualmente.

---

### DIMENSIÓN 11 — RELACIONES

#### 11.1 Con qué se relaciona
- **Task:** la task produce el draft.
- **Agente:** generó el draft.
- **Evidence bundle:** contextualiza el draft.
- **Voice Profile:** da el tono.
- **Outcome Ledger:** recibe diffs y decisiones.
- **Canal de salida:** envía el draft aprobado.

#### 11.2 En qué orden
```
Inbound → Task → Skill execution → Draft → Aprobación HITL → Envío
```

#### 11.3 Qué rompe si este módulo falla
- P3 se viola o el workflow se congela.
- No se puede enviar comunicación externa.
- No hay señales de aprendizaje (gold samples / diffs).

---

### DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
- **Operator:** sus propios drafts (según position assignment).
- **Owner:** todos los drafts del tenant.
- **Viewer:** solo historial, no puede aprobar (rol no activo en E1 según enmienda E-4).
- Nunca cross-tenant.

#### 12.2 Qué queda en el audit trail D10
Campos obligatorios según ejemplo de SCH_FB_FUNCTIONAL_SPEC_v1 §Ejemplo de ficha:
- `tenant_id`, `case_id`, `draft_id`
- `actor_role_at_decision` (Operator)
- `action` (`approved` / `edited` / `rejected`)
- `diff_hash` si hubo edición
- `channel_sent`
- `timestamp`, `sha_chain_prev`, `sha_chain_curr`
- `human_gate_required=true`
- `human_approver_id`

El draft nunca sale sin `human_approver_id` en D10.

#### 12.3 Qué restricciones de datos aplican
- Data class típica N2 (RFQ B2B con pricing/márgenes).
- HITL absoluto en todo output cliente-facing (TIER 1 #2 de PLB).
- N3/N4 prohibidos en E1 (TIER 1 #3).
- Anthropic-only en E1 (decisión CEO #7 PLB §5).

---

### DIMENSIÓN 13 — DESKTOP vs WEB

#### 13.1 En cuál superficie vive
- **Desktop (Electron):** superficie primaria para Operator/Owner en E1.
- **Web (Next.js):** accesible para Owner/Operator pero uso secundario.
- **Canal externo:** es el destino final del draft aprobado.

#### 13.2 Diferencias entre desktop y web
- Desktop: edición inline, diff en tiempo real, atajos de teclado, notificaciones WebSocket.
- Web: vista y aprobación simple; edición inline limitada o no disponible en E1.

#### 13.3 Offline y sincronización
- No funciona offline — requiere conexión para validar permisos y enviar por canal.
- Si se pierde conexión durante edición, el draft se guarda localmente y se sincroniza al reconectar.

---

## PREGUNTAS ESPECÍFICAS DEL BRIEF PARA DRAFT Y APROBACIÓN HITL

### Cómo aparece: cuándo y cómo llega a Zona 2 de WorkLoom
Aparece cuando una task en ejecución emite un output con `requires_human_gate=true`. El evento `draft.generated` se publica en el outbox, el worker lo pone en Redis Streams, el WebSocket server lo fanout al tenant, y el frontend de WorkLoom muestra la card en Zona 2.

### Qué ve María en la card: campos exactos
- Cliente / remitente.
- Tipo de tarea (ej. "Cotización RFQ").
- Canal de origen (email/WhatsApp en E3; email en E1-E2).
- Confidence HIGH / LOW.
- SLA restante (timer con color).
- Acción primaria contextual: "Revisar y aprobar", "Editar", "Rechazar".

### Qué ve al abrir el draft: panel completo con draft + evidence bundle
- **Draft:** texto completo propuesto por el agente.
- **Evidence bundle:** [PENDIENTE — especificar campos exactos del evidence bundle; SCH_FB_QUOTE_EVIDENCE_BUNDLE no estaba en docs obligatorios de este agente].
- **Metadata:** caso ID, trace ID, canal, costo (Owner only), model provider.
- **Acciones:** Aprobar, Editar+Aprobar, Rechazar.

### Las 3 acciones: Aprobar / Editar+Aprobar / Rechazar — flujo exacto
1. **Aprobar:**
   - María revisa el draft.
   - Click "Aprobar".
   - Sistema registra `draft.approved` en audit con `human_approver_id`.
   - Sistema envía el draft por el canal configurado.
   - Se emite `draft.sent`.
   - Si confidence HIGH y sin edición, se marca como candidate gold sample.

2. **Editar+Aprobar:**
   - María entra a modo inline.
   - Edita el texto (diff capturado).
   - Selecciona razón del cambio (P6).
   - Click "Aprobar cambios".
   - Sistema registra `draft.edited` + diff en Outcome Ledger.
   - Sistema envía el draft editado.

3. **Rechazar:**
   - María click "Rechazar".
   - Modal pide razón tipificada.
   - Sistema registra `draft.rejected` + razón.
   - Task asociada pasa a `failed` o `cancelled`.
   - Feedback alimenta skill refinement.

### Edición inline: qué puede cambiar, qué no puede cambiar y por qué
- **Puede cambiar:** cuerpo del draft, saludos, despedidas, frases de cortesía, ajustes de tono.
- **No puede cambiar:** evidence bundle (es read-only, garantiza trazabilidad), metadata del caso, y campos bloqueados por política del tenant (ej. precio bajo threshold de margen — [PENDIENTE — definir threshold y política]).
- **Por qué:** el evidence bundle es la base de auditoría; modificarlo rompería la trazabilidad de la decisión.

### Quick pass: cómo funciona para drafts de bajo riesgo
[PENDIENTE — no se encontró definición de "Quick pass" en los docs leídos].

### Batch: cómo aprobar múltiples drafts similares de una vez
[PENDIENTE — no se encontró definición de aprobación batch en los docs leídos].

### Oscillation Counter: qué es, cuándo se activa, qué le muestra a María
[PENDIENTE — no se encontró definición de "Oscillation Counter" en los docs leídos].

### Qué pasa si expira: qué ve María, qué hace el sistema
- María ve el draft movido a Zona 1 con badge "Expirado" y botón "Regenerar" o "Descartar".
- El sistema:
  - Cambia estado a `expired`.
  - Emite evento `draft.rejected` o evento específico de expiración [PENDIENTE — confirmar evento canónico para expiración; no está en la lista de 28 eventos].
  - Notifica al Owner/Operator responsable.
  - No envía nada al cliente.

### Desktop vs Web: primariamente desktop, qué pasa si Owner aprueba desde web
- Desktop es la superficie primaria en E1.
- Si Owner aprueba desde web:
  - Puede aprobar/rechazar drafts simples.
  - Edición inline puede ser limitada o no disponible en E1.
  - El flujo de audit es el mismo: se registra `human_approver_id` y rol Owner.

---

## LISTA DE PENDIENTES QUE REQUIEREN DECISIÓN CEO

1. **[PENDIENTE — Campos exactos del evidence bundle]** El panel de draft debe mostrar un evidence bundle, pero el documento SCH_FB_QUOTE_EVIDENCE_BUNDLE no estaba en la lista de lectura obligatoria de este agente. Se requiere definir qué campos se muestran en E1 (PLB §1.2 dice 8+5 campos en E1, 18/18 en E2).

2. **[PENDIENTE — Threshold de margen y campos bloqueados en edición]** ¿Qué campos de pricing/precio pueden editarse y cuáles están bloqueados por política de margen del tenant? Esto afecta D5 EDICIÓN del módulo Draft.

3. **[PENDIENTE — Definición de Quick pass]** No se encontró en KB la funcionalidad "Quick pass para drafts de bajo riesgo". Se requiere decidir si entra en E1 o se deja para E2.

4. **[PENDIENTE — Definición de aprobación Batch]** No se encontró en KB la funcionalidad de "aprobar múltiples drafts similares de una vez". Se requiere decidir si entra en E1.

5. **[PENDIENTE — Definición de Oscillation Counter]** No se encontró en KB el concepto "Oscillation Counter". Se requiere decidir si es un módulo separado o se incorpora al learning loop.

6. **[PENDIENTE — Evento canónico para expiración de draft]** La lista de 28 eventos de SPEC_FB_EVENTING_AND_OUTBOX_v1 no incluye un evento `draft.expired`. Se requiere decidir si se agrega o se mapea a `draft.rejected`.

7. **[PENDIENTE — Roles activos en E1 vs roles de referencia]** PLB enmienda E-4 reduce a 2 roles en E1 (Owner, Operator), pero SCH_FB_FUNCTIONAL_SPEC_v1 y otros docs usan 5 roles canónicos. Se requiere confirmar si las fichas funcionales usan 2 roles para E1 o mantienen 5 como diseño de referencia.

8. **[PENDIENTE — Estados técnicos de task]** SCH_FB_TASK_ENTITY.md usa `queued` y `timeout` como estados técnicos, mientras que SCH_FB_FUNCTIONAL_SPEC_v1 y el brief usan `created` y `failed`. Se requiere confirmar la nomenclatura oficial para UI/UX.

---

## LISTA DE CONTRADICCIONES DETECTADAS CON LA KB

1. **Estados de task:**
   - SCH_FB_FUNCTIONAL_SPEC_v1 §Referencias canónicas y el brief de AGENTE_2 listan estados: `created`, `running`, `awaiting_approval`, `completed`, `failed`, `cancelled`.
   - SCH_FB_TASK_ENTITY.md §Schema y §State machine listan: `queued`, `running`, `awaiting_approval`, `completed`, `failed`, `cancelled`, `timeout`.
   - **Impacto:** hay que decidir si `created`/`queued` son sinónimos y si `timeout` es un estado separado o subclass de `failed`.

2. **Sprint del módulo Draft/HITL:**
   - El ejemplo de ficha en SCH_FB_FUNCTIONAL_SPEC_v1 §Ejemplo de ficha asigna S3 a "Aprobación de draft por output".
   - PLB_FB_FOUNDATION_BETA_v1 §Plan por sprint asigna Mesa de Control + WhatsApp + Email a S5.
   - **Impacto:** la ficha funcional usa S5, pero el ejemplo canónico dice S3. Requiere reconciliación.

3. **Número de roles en E1:**
   - El contexto general y SCH_FB_FUNCTIONAL_SPEC_v1 usan 5 roles: Owner / Admin / Operator / Supervisor / Viewer.
   - PLB_FB_FOUNDATION_BETA_v1 enmienda E-4 reduce a 2 roles activos en E1: Owner, Operator; los 5 roles entran en E3.
   - **Impacto:** las fichas deben aclarar que en E1 operan Owner/Operator y que Admin/Supervisor/Viewer son diseño de referencia para E3.

4. **Canales en E1:**
   - El contexto general menciona WhatsApp BSP y Gmail/IMAP.
   - PLB enmienda E-5 dice E1-E2 son email-only (Gmail OAuth out; IMAP in); WhatsApp Business va a E3.
   - **Impacto:** la ficha de Draft debe reflejar que el canal de envío en E1-E2 es email; WhatsApp está diferido.

5. **Engine de skills / Skill Factory:**
   - PLB original §2.2/§S3 describe engine con SkillSpec en DB + Pydantic dinámico.
   - PLB enmienda E-3 reemplaza eso por skill = markdown versionado + tools allowlist + schema de salida, capa fina sobre SDK estándar.
   - **Impacto:** implementación S3 debe ignorar el modelo Pydantic dinámico del PLB original y seguir enmienda E-3.

6. **Skill state machine:**
   - SCH_FB_FUNCTIONAL_SPEC_v1 §Referencias canónicas lista estados de skill: `SHADOW / ACTIVE / PAUSED / DEPRECATED`.
   - PLB §2.3 schema `skills` lista estados: `draft`, `active`, `deprecated`.
   - **Impacto:** hay inconsistencia en el nombre del estado inicial (`SHADOW` vs `draft`).

7. **Sub-agentes / multi-agente:**
   - PLB TIER 1 #15 prohíbe sub-agentes y orquestación entre agentes en E1.
   - SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 §3.1 dice que los 10 sub-agentes del catálogo están "OPERATIVOS como agentes standalone" y que composición jerárquica está bloqueada E1.
   - ARCH_AGENT_PRINCIPLES P17 (v1.6) habilita Nivel 2 de composición multi-agente bajo condiciones.
   - **Impacto:** tensión entre "prohibido E1" y "habilitado bajo condiciones" en P17. Requiere clarificación de qué nivel de P17 aplica en E1.

---

*Fin de la ficha funcional AGENTE_2_TASK_DRAFT.*
