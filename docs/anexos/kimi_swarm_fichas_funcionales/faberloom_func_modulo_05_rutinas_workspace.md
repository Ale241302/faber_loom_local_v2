# FICHA FUNCIONAL — MÓDULOS 9 Y 10

**AGENTE:** AGENTE_5_RUTINAS_WORKSPACE  
**Proyecto:** FaberLoom Foundation Beta E1  
**Docs base:** SCH_FB_FUNCTIONAL_SPEC_v1.md, PLB_FB_FOUNDATION_BETA_v1.md, SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.md, SPEC_FB_AUTH_TENANT_RBAC_v1.md, SPEC_ACTION_ENGINE.md, ARCH_AGENT_PRINCIPLES.md, POL_DATA_CLASSIFICATION.md, ENT_FB_INBOUND_TAXONOMY_v1.md, SPEC_FB_ROUTINES_v1.md, SPEC_FB_WORKSPACE_v1.md, ENT_FB_WORK_TYPE_PACK_v1.md, SPEC_FABERLOOM_WORKFLOW_ENGINE_v1.md, SPEC_FABERLOOM_AGENT_COMPOSITION_v1.md, SCH_FB_TASK_ENTITY.md, SPEC_FB_EVENTING_AND_OUTBOX_v1.md

---

# MÓDULO 9: RUTINA (Agente de Proceso / Automatización)

**MÓDULO:** Rutina  
**SUPERFICIE:** Desktop (Electron — WorkLoom Zona 5) + Web (Next.js — Agent Factory)  
**SPRINT E1:** S5 (Mesa de Control con Zona 5) · S6 (Agent Factory + sandbox + promote) · S7 (Workspace modo Automatización)  
**ROLES QUE LO USAN:** Owner (crear/promover/deprecar), Admin (crear/editar/pausar), Operator (activar/desactivar switch, revisar alertas), Supervisor (revisar runs fallidos), Viewer (solo ver estado en Zona 5)  
**DATA CLASS TÍPICA:** N1 (configuración interna del tenant); los inputs que procesa heredan la data_class del evento disparador (N0-N2 en E1)

---

## DIMENSIÓN 1 — EXISTENCIA

### 1.1 Por qué existe
María (Operator) tiene 20-30 tareas mixtas por día. Sin rutinas, cada mañana debe acordarse de revisar manualmente RFQs pendientes, stock bajo, follow-ups vencidos y alertas de margen. Cuando se olvida, los clientes esperan, los proveedores no se contactan y las oportunidades se pierden. Con rutinas, el sistema ejecuta esas revisiones recurrentes solo, sin que María tenga que iniciar cada tarea.

### 1.2 A quién le duele
- **Operator:** recibe alertas de rutinas en Zona 1/Zona 5; no debe recordar cada chequeo.
- **Supervisor:** debe asegurar que las rutinas no generen ruido ni envíen comunicación externa sin HITL.
- **Owner/Admin:** configuran, promueven de SANDBOX a ACTIVE y aprueban automatizaciones de mayor autonomía.

### 1.3 Cuándo aparece
Aparece cuando el tenant necesita ejecutar una tarea de forma recurrente, reactiva o programada: cada mañana a las 6am, cuando llega un email con cierto asunto, cuando un stock cruza un umbral, o cuando María describe en Workspace "cada vez que pase X, hacé Y".

---

## DIMENSIÓN 2 — PROPÓSITO

### 2.1 Para qué
Para que un agente de Proceso ejecute tareas recurrentes o reactivas bajo condiciones declaradas, siempre dentro del techo de autonomía configurado, y nunca envíe comunicación externa sin aprobación humana.

### 2.2 Qué valor entrega
- Reduce la carga mnémica de María: el sistema vigila por ella.
- Dispara alertas oportunas en Zona 1 antes de que venzan SLAs.
- Acumula evidencia de ejecuciones para decidir si una rutina puede subir de autonomía.

### 2.3 Qué pasa si no existe
María debe recordar cada revisión, usar recordatorios manuales o herramientas externas (calendario, spreadsheets). Las tareas recurrentes se acumulan, los follow-ups se retrasan y el sistema no aprende patrones operativos.

---

## DIMENSIÓN 3 — CREACIÓN

### 3.1 Cómo se crea
Hay dos caminos canónicos en E1:

**Camino 1 — Workspace conversacional (modo Automatización):**
1. María abre Workspace y escribe en lenguaje natural: "Cada vez que llegue un RFQ de cliente Gold sin SKU, avisame por la mañana".
2. El sistema detecta intención de automatización (modo 2) y propone: trigger, condición, acción y canal de alerta.
3. María revisa la propuesta, ajusta thresholds si es necesario y confirma.
4. El sistema crea la rutina en estado `sandbox` y aparece en Zona 3 (SANDBOX esperando promote).
5. Owner/Admin la prueba y promueve a `active` (ver D6).

**Camino 2 — Agent Factory en web (Owner/Admin):**
1. Owner/Admin entra a Agent Factory > Nueva Rutina.
2. Paso 1: nombre, descripción, categoría Proceso, avatar.
3. Paso 2: skill(s) asignados en orden lineal (ej. `clasificar_rfq`, `generar_alert_stock`).
4. Paso 3: trigger (schedule/cron, webhook, evento de sistema, palabra clave en canal).
5. Paso 4: configuración de autonomía, HITL fallback y alert channel.
6. Paso 5: sandbox obligatorio antes de promote (TIER 1 #16.9).

### 3.2 Quién puede crearla
- **Workspace:** Operator puede proponer una rutina; el sistema la crea en `sandbox`.
- **Agent Factory:** Owner o Admin crean directamente. Promote a `active` solo Owner/Admin (TIER 1 #16.10).

### 3.3 Qué necesita para crearse
- Agente base de categoría Proceso configurado.
- Skill(s) disponibles (system o custom) en estado `ACTIVE` o al menos `SHADOW`.
- Trigger válido con idempotency key (para dedup).
- Autonomy ceiling declarado (PROPONE / EJECUTA_INTERNO / AUTO_NOTIFICA / AUTO_EXCEPCIONES).
- Para triggers de canal: mailbox o WhatsApp conectado al tenant.

[PENDIENTE — SPEC_FB_ROUTINES_v1 en stub: detalle exacto de wizard y campos obligatorios por tipo de trigger]

---

## DIMENSIÓN 4 — USO DIARIO

### 4.1 Cómo se usa en el día a día
1. María abre WorkLoom. En Zona 5 ve el listado de rutinas activas con switches ON/OFF.
2. Las rutinas corren en background según su trigger.
3. Cuando una rutina encuentra algo accionable, genera una `task` o un `draft` que aparece en la Mesa (Zona 1 si es urgente, Zona 2 si requiere firma, Zona 4 si es ruido/informativo).
4. María revisa el item y actúa. La rutina continúa programada.
5. Al final del día, María puede pausar una rutina desde Zona 5 si generó mucho ruido.

### 4.2 Cómo se invoca
- **Automática:** por trigger configurado (schedule, evento, webhook, keyword).
- **Manual:** desde Zona 5 con botón "Ejecutar ahora" (solo Owner/Admin/Operator según permiso).
- **Por mención:** en Workspace se puede mencionar `@seguidor_rfq` para forzar una ejecución puntual.

### 4.3 Qué ve el usuario mientras ocurre
- **Inicial:** en Zona 5, card de la rutina con nombre, estado, última ejecución, próxima ejecución, signal-to-noise ratio.
- **En ejecución:** spinner o badge "Ejecutando" en la card; posible toast si requiere atención.
- **Completado:** card actualiza "Última ejecución: hace X min".
- **Error:** badge rojo en Zona 1 + Zona 5; detalle al expandir.
- **Alerta generada:** item aparece en Zona 1/Zona 2 con metadata de la rutina que lo originó.

---

## DIMENSIÓN 5 — EDICIÓN

### 5.1 Cómo se edita
Owner/Admin entra a Agent Factory (web), selecciona la rutina y edita:
- Trigger config (horario, condición, palabra clave).
- Pre_condition.
- Autonomy ceiling.
- Alert channel.
- Skill bindings y runtime config.

Desde Zona 5 (desktop), Operator/Admin solo puede pausar/reanudar o forzar ejecución manual; no editar la lógica.

### 5.2 Qué se puede cambiar y qué no
**En rutina `active`:**
- Se puede cambiar: trigger_config, pre_condition, alert_channel, autonomy_ceiling dentro del rango permitido, runtime config de skills.
- No se puede cambiar: `trigger_kind` (requiere clonar), `tenant_id`, historial de ejecuciones.

**En rutina `sandbox`:**
- Todo es editable hasta promote.

### 5.3 Qué pasa con lo generado previamente
- Runs históricos se preservan en `automation_runs`.
- Cambios en `active` no invalidan runs anteriores; la nueva config aplica desde la siguiente ejecución.
- Si se edita mientras ejecuta, el run en curso termina con la config anterior; el siguiente usa la nueva.

---

## DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

### 6.1 State machine
```
sandbox -- trigger: Owner/Admin aprueba promote tras sandbox exitoso --> active
active  -- trigger: Owner/Admin pausa manualmente --> paused
paused  -- trigger: Owner/Admin reanuda --> active
active  -- trigger: 3 fallos consecutivos del run --> failed
failed  -- trigger: Owner/Admin investiga y reactiva manualmente --> active
active  -- trigger: Owner/Admin depreca --> deprecated
paused  -- trigger: Owner/Admin depreca --> deprecated
failed  -- trigger: Owner/Admin depreca --> deprecated
```

### 6.2 Qué dispara el movimiento
- `sandbox → active`: sandbox exitoso + aprobación Owner/Admin.
- `active → paused`: switch en Zona 5 o Agent Factory.
- `active → failed`: 3 ejecuciones consecutivas con error técnico o compliance.
- Cualquier estado → `deprecated`: decisión Owner/Admin (no se borra, se depreca).

### 6.3 Quién puede moverlo
| Transición | Rol |
|---|---|
| sandbox → active | Owner / Admin |
| active ↔ paused | Owner / Admin / Operator (solo switch en Zona 5) |
| failed → active | Owner / Admin |
| cualquier → deprecated | Owner / Admin |

### 6.4 Qué se notifica y a quién
- Promote a active: toast al Owner/Admin, log en audit.
- Pausa: badge en Zona 5, sin alerta si es manual programada.
- Fallo 1 y 2: log silencioso + contador interno.
- Fallo 3 (`failed`): badge Zona 1 + notificación a Owner/Admin + evento `agent.alarma`.
- Deprecación: evento en audit, card desaparece de Zona 5 (queda en historial).

---

## DIMENSIÓN 7 — OUTPUT

### 7.1 Qué produce para el usuario
- Alerta en Zona 1 si requiere acción urgente.
- Draft en Zona 2 si genera output cliente-facing pendiente de HITL.
- Item informativo en Zona 4 si es ruido/log.
- Card actualizada en Zona 5 con métricas de la rutina.

### 7.2 Qué produce para el sistema
- `automation_run` en DB con `status` (running/completed/failed/cancelled).
- `task` si el output es accionable.
- Eventos canónicos: `feed.item.received` (si dispara por inbound), `draft.generated` (si produce draft), `agent.alarma` (si falla).
- Registro en `skill_executions` si invoca skills.
- Entrada en audit trail D10 con `actor_role_at_decision`.

### 7.3 Dónde aparece el output
- Zona 1 (urgente), Zona 2 (HITL), Zona 4 (inbox/log), Zona 5 (estado de rutinas).
- Alertas por canal configurado (email interno, notificación desktop, Telegram si está habilitado en E3).

### 7.4 Qué formato tiene
- Card en Mesa con: nombre rutina, tipo, canal origen, confidence, SLA restante, acción primaria.
- Registro `automation_run` JSONB con `trigger_payload`, `output`, `cost_usd`, `error_message`.

---

## DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

### 8.1 Qué pasa si falla
**Técnico:**
- Error en skill: skill falla aislada, task=skill_failed, rutina intenta continuar si fail_policy lo permite.
- Worker muere: el run queda `running` hasta timeout; Celery redistribuye con retry.
- DB unreachable: run encolado en DLQ, reintento exponencial.
- LLM timeout: aborta skill, registra costo parcial, incrementa contador de fallos.

**Datos:**
- Trigger recibe payload inesperado: descarta con log, no incrementa contador de fallos si es dedup.
- Clasificación incorrecta: item puede llegar a Zona 4; María puede reclasificar.

**Compliance:**
- Intento de envío externo sin HITL: hard block, run=failed, alerta Owner.
- Data class del input > ceiling del tenant: Action Engine retorna `PlanUpgradeRequired`, no ejecuta.

### 8.2 Cómo se recupera
- Retry automático: hasta 3 intentos con backoff 1s, 5s, 25s.
- DLQ: eventos/runs fallidos visibles en panel admin; Owner/Admin puede reintentar manual.
- Circuit breaker: si una skill falla 3 veces, se abre; las siguientes ejecuciones usan fallback o pausan la rutina.
- María puede pausar la rutina desde Zona 5 mientras se investiga.

### 8.3 Quién se entera
| Fallo | Notificación | Nivel |
|---|---|---|
| 1-2 fallos técnicos | Log + observabilidad | P2 |
| 3 fallos consecutivos (`failed`) | Owner/Admin + badge Zona 1 | P1 |
| Intento de bypass HITL | Owner + audit inmutable | P0 |
| Cross-tenant leak attempt | CEO + auditoría | P0 |

---

## DIMENSIÓN 9 — APRENDIZAJE

### 9.1 Qué aprende el sistema de este uso
- Signal-to-noise ratio: cuántas alertas generó vs cuántas fueron útiles.
- Aprobación/rechazo/edición de drafts generados por la rutina.
- Tiempo de respuesta de María ante alertas de la rutina.
- Razones de pausa manual (ruido, frecuencia, duplicados).

### 9.2 Cómo mejora con el tiempo
- Si ratio ruido/útil es alto, el sistema sugiere ajustar `pre_condition` o threshold.
- Si María aprueba sin editar muchas veces, la rutina puede proponer subir de autonomía (L1→L2, etc.) con aprobación Owner.
- Si hay duplicados, mejora el mecanismo de dedup/idempotency.

### 9.3 Qué feedback da el usuario
- Implícito: pausar, aprobar, editar, rechazar, descartar items generados por la rutina.
- Explícito: dropdown de razón al rechazar o al pausar una rutina ("muy ruidosa", "no aplica a mi caso", "duplicada").

---

## DIMENSIÓN 10 — ELIMINACIÓN

### 10.1 Cómo se elimina
Las rutinas no se borran; se **deprecan**. Owner/Admin en Agent Factory selecciona "Deprecar rutina". La rutina pasa a `deprecated`, deja de ejecutarse y desaparece de Zona 5 (aparece en historial).

### 10.2 Qué pasa con lo que dependía
- Runs históricos se conservan para audit y métricas.
- Tasks/drafts generados por la rutina ya existentes no se eliminan; siguen su propio ciclo.
- Skills que usaba siguen activos si otros agentes las usan.

### 10.3 Es reversible
No. Una vez `deprecated`, no se vuelve a `active`. Se debe clonar como nueva rutina en `sandbox` y promover. Esto preserva el historial inmutable.

---

## DIMENSIÓN 11 — RELACIONES

### 11.1 Con qué se relaciona
- **Agent Factory / Workspace:** donde se crea y edita.
- **Skill:** ejecuta una cadena lineal de skills (TIER 1 #15).
- **Task:** cada ejecución genera un `automation_run` y posiblemente `task` hijas.
- **Mesa de Control:** Zona 5 muestra estado; Zona 1/2/4 reciben outputs.
- **Action Engine:** aplica data classification, timeout, cost cap, HITL gate.
- **Eventing/Outbox:** emite eventos canónicos y garantiza entrega.
- **Audit D10:** registra cada decisión y run.

### 11.2 En qué orden
1. Debe existir el tenant con skills disponibles.
2. Se crea la rutina en `sandbox`.
3. Sandbox exitoso → promote a `active`.
4. El trigger dispara `automation_run`.
5. El run genera task/draft/alerta en Mesa.
6. María actúa; el feedback alimenta aprendizaje.

### 11.3 Qué rompe si este módulo falla
- No se ejecutan revisiones recurrentes; María vuelve a operar manual.
- Si falla silenciosamente, pueden perderse alertas críticas (stock bajo, RFQ vencido).
- Si falla abierto, puede generar ruido masivo en Zona 4 o intentos de envío bloqueados por HITL.

---

## DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

### 12.1 Quién puede verlo
- **Owner/Admin:** todas las rutinas del tenant, historial, config completa.
- **Operator:** rutinas asignadas a su position, switches en Zona 5, runs que la afectan.
- **Supervisor:** rutinas de su equipo, métricas de fallos.
- **Viewer:** solo estado de rutinas activas, sin config ni runs.
- Nunca cross-tenant: RLS filtra por `tenant_id`.

### 12.2 Qué queda en el audit trail D10
Campos exactos por transición/run:
- `tenant_id`
- `user_id` (Owner/Admin/Operator que actuó)
- `actor_role_at_decision`
- `action` (create, edit, promote, pause, resume, deprecate, run_completed, run_failed)
- `resource_id` (rutina_id / automation_run_id)
- `data_class` (máxima del input/proceso)
- `model_provider` / `model_id` (si aplica)
- `human_gate_required` (true si generó draft HITL)
- `human_approver_id` (si hubo aprobación)
- `timestamp`
- `sha_chain_prev` / `sha_chain_curr`

### 12.3 Qué restricciones de datos aplican
- Data class típica N1 (configuración); inputs heredan class del disparador.
- Ninguna rutina envía comunicación externa sin HITL (TIER 1 #2). El motor hardcodea `waitForApproval()` para `external_communication`.
- N3/N4 prohibidos en E1 (TIER 1 #3); si un trigger intenta procesar N3+, Action Engine bloquea.
- DPA Anthropic vigente para calls LLM.

---

## DIMENSIÓN 13 — DESKTOP VS WEB

### 13.1 En cuál superficie vive
- **Desktop (Electron):** uso diario de María. Zona 5 de WorkLoom es la superficie principal para ver estado, pausar/reanudar y ejecutar manualmente.
- **Web (Next.js):** configuración completa en Agent Factory, edición de lógica, promote/deprecate, historial detallado.

### 13.2 Diferencias entre desktop y web
- Desktop: switches ON/OFF, ejecución manual, visualización de alertas generadas. No edita lógica.
- Web: wizard completo, sandbox, promote, edición de trigger/skill/autonomy, historial de runs.

### 13.3 Offline y sincronización
- Las rutinas corren en backend; no dependen del desktop online.
- Si el desktop de María está offline, las alertas se acumulan y se sincronizan al reconectar vía WebSocket/SSE.
- Si el run generó un draft HITL, el draft espera aprobación sin expirar antes del SLA.

[PENDIENTE — SPEC_FB_ROUTINES_v1 en stub: detalle de UI de Zona 5, cantidad mínima de runs sandbox para AUTO_NOTIFICA/AUTO_EXCEPCIONES, y fórmula exacta de signal-to-noise ratio]

---

---

# MÓDULO 10: WORKSPACE CONVERSACIONAL (3 modos)

**MÓDULO:** Workspace conversacional  
**SUPERFICIE:** Desktop (Electron) — WorkLoom/Workspace  
**SPRINT E1:** S7  
**ROLES QUE LO USAN:** Operator (uso operativo diario), Admin/Owner (modos Automatización y Construcción), Supervisor (revisión), Viewer (solo lectura de conversaciones propias si aplica)  
**DATA CLASS TÍPICA:** N1 (consultas operativas); puede escalar a N2 si se adjuntan precios/márgenes; N3/N4 hard-block en E1

---

## DIMENSIÓN 1 — EXISTENCIA

### 1.1 Por qué existe
María necesita hacer trabajo que no entra por la Mesa: responder una consulta compleja de un cliente, investigar un caso, iterar con la IA para refinar una respuesta, o construir una nueva automatización. Sin Workspace, no tiene un lugar unificado para conversar con los agentes, ver qué contexto usa la IA y convertir eso en acciones o automatizaciones.

### 1.2 A quien le duele
- **Operator:** pasa aquí el trabajo exploratorio, las consultas puntuales y la construcción de respuestas que requieren varias iteraciones.
- **Admin/Owner:** usan el modo Construcción para crear agentes/skills y el modo Automatización para definir rutinas.
- **Supervisor:** revisa conversaciones de su equipo para entrenamiento y calidad.

### 1.3 Cuándo aparece
Aparece cuando María necesita:
- Resolver un caso que no está en la Mesa (modo Operacional).
- Describir una regla recurrente en lenguaje natural (modo Automatización).
- Pedir ayuda para crear un agente/skill nuevo porque detecta un gap (modo Construcción).

---

## DIMENSIÓN 2 — PROPÓSITO

### 2.1 Para qué
Para que el usuario construya, itere y automatice con lenguaje natural, siempre bajo HITL, con contexto visible y trazabilidad completa.

### 2.2 Qué valor entrega
- Un solo chat para operar, automatizar y construir.
- Contexto activo visible: la IA muestra qué sabe y qué no incluye.
- Convierte conversaciones en tareas, drafts o automatizaciones en sandbox.

### 2.3 Qué pasa si no existe
María salta entre email, spreadsheets, chat interno y la Mesa. Pierde contexto, repite explicaciones y no puede crear automatizaciones conversacionalmente.

---

## DIMENSIÓN 3 — CREACIÓN

### 3.1 Cómo se crea
El Workspace no se crea manualmente; existe como pantalla del desktop. Las **conversaciones** sí se crean:
1. María hace clic en "Nueva conversación" o presiona atajo.
2. Selecciona o no un contexto activo (KB, caso, archivo).
3. Escribe en el composer.
4. El sistema detecta el modo automáticamente.

### 3.2 Quién puede crearlo
Cualquier usuario con rol Operator o superior puede crear conversaciones. Viewer solo ve conversaciones compartidas/historial.

### 3.3 Qué necesita para crearse
- Sesión activa en el desktop.
- Al menos un agente disponible para mencionar.
- Contexto activo opcional: KB, caso, archivo subido.

---

## DIMENSIÓN 4 — USO DIARIO

### 4.1 Cómo se usa en el día a día
1. María abre Workspace desde el sidebar.
2. Ve conversaciones recientes a la izquierda y el chat central.
3. Escribe una consulta o usa @mención para invocar un agente.
4. El sistema detecta el modo y responde/propone/crea según corresponda.
5. María revisa el contexto activo, edita, aprueba o descarta.
6. Si genera una automatización o agente nuevo, queda en SANDBOX para promoción.

### 4.2 Cómo se invoca
- Navegación directa desde sidebar.
- Botón "Abrir en Workspace" en cards de Mesa o detalle de correo.
- @mención de agente en el composer.
- Deep-link desde notificación.

### 4.3 Qué ve el usuario mientras ocurre
- **Inicial:** panel izquierdo con conversaciones recientes, panel central con chat, panel derecho con tabs Agentes/Skills/Aprendizaje + Contexto activo.
- **En proceso:** streaming de respuesta, spinner, costo estimado, badges de modo detectado.
- **Completado:** respuesta final + acciones rápidas (aprobar, editar, convertir en draft, convertir en rutina, guardar golden sample).
- **Error:** toast con razón y opción de reintentar.

---

## DIMENSIÓN 5 — EDICIÓN

### 5.1 Cómo se edita
- **Mensajes propios:** María puede editar su último mensaje antes de que la IA responda.
- **Respuesta de la IA:** no se edita directamente; se convierte en draft editable en Zona 2 o se abre en el panel de revisión.
- **Contexto activo:** se puede agregar/excluir fuentes desde el panel derecho.
- **Skills ON/OFF por consulta:** toggles temporales en el panel derecho (solo para esa consulta).

### 5.2 Qué se puede cambiar y qué no
- Se puede cambiar: contexto activo, skills activas para la consulta, tono/modo (Económico/Balanceado/Calidad), mensaje propio.
- No se puede cambiar: historial de ejecuciones de agentes, costos ya incurridos, decisión de HITL de otro usuario.

### 5.3 Qué pasa con lo generado previamente
- Si una conversación generó un draft aprobado, el draft queda en historial.
- Si generó una rutina/agente en sandbox, la conversación queda vinculada como provenance.
- Si se edita un mensaje, la conversación puede reejecutarse con el nuevo input.

---

## DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

### 6.1 State machine del modo detectado
```
Nueva conversación -- trigger: usuario escribe --> Modo detectado (Operacional / Automatización / Construcción)

Modo Operacional -- trigger: respuesta generada --> draft/task creada
Modo Operacional -- trigger: usuario itera --> continúa conversación

Modo Automatización -- trigger: sistema propone trigger+acción --> propuesta en sandbox
Modo Automatización -- trigger: usuario confirma --> rutina creada en sandbox

Modo Construcción -- trigger: sistema propone agente/skill --> propuesta en sandbox
Modo Construcción -- trigger: usuario confirma --> agente/skill creado en sandbox

sandbox -- trigger: Owner/Admin aprueba --> active
sandbox -- trigger: Owner/Admin rechaza --> descartado
```

### 6.2 Qué dispara el movimiento
- Detección de modo: palabras clave, estructura de la frase, presencia de @mención, contexto activo.
- Confirmación: botón explícito del usuario antes de crear cualquier objeto en SANDBOX.
- Promoción: Owner/Admin desde Zona 3 o Agent Factory.

### 6.3 Quién puede moverlo
| Transición | Rol |
|---|---|
| Detectar modo y responder | Sistema |
| Confirmar creación en sandbox | Operator / Admin / Owner |
| Promover sandbox → active | Owner / Admin |
| Descartar propuesta | Owner / Admin / Operator que la creó |

### 6.4 Qué se notifica y a quién
- Modo detectado: badge sutil en el composer.
- Propuesta creada en sandbox: toast + aparición en Zona 3.
- Promote: notificación al creador.
- Rechazo: notificación al creador con razón.

---

## DIMENSIÓN 7 — OUTPUT

### 7.1 Qué produce para el usuario
- **Modo Operacional:** respuesta, draft, resumen, o plan de acción.
- **Modo Automatización:** propuesta de rutina + rutina en SANDBOX tras confirmar.
- **Modo Construcción:** propuesta de agente/skill + objeto en SANDBOX tras confirmar.

### 7.2 Qué produce para el sistema
- **Modo Operacional:** `task` + `draft` + eventos `draft.generated`, `task.created`.
- **Modo Automatización:** fila en `automations` (sandbox) + evento `agent.config.updated`.
- **Modo Construcción:** fila en `agents` o `skills` (sandbox) + evento correspondiente.
- En todos los modos: entradas en `skill_executions`, `llm_calls`, `audit_log`.

### 7.3 Dónde aparece el output
- Respuestas/drafts: Zona 2 (HITL) o Zona 4 (informativo).
- Sandbox: Zona 3.
- Estado del sistema: panel derecho Workspace.

### 7.4 Qué formato tiene
- Texto en chat (markdown simplificado).
- Tarjetas de propuesta con campos editables antes de confirmar.
- Drafts con evidence bundle si es output cliente-facing.
- Objetos sandbox con metadata (nombre, tipo, skills, trigger, autonomy).

---

## DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

### 8.1 Qué pasa si falla
**Técnico:**
- LLM timeout: mensaje de error, opción de reintentar con modo Económico.
- Skill falla: se informa en chat, se sugiere otra skill o intervención humana.
- WebSocket caído: la conversación se guarda; al reconectar se sincroniza.

**Datos:**
- Upload de archivo no soportado: rechazo inmediato con lista de tipos aceptados.
- Archivo con data class N3/N4: hard block, no se procesa.

**Permisos:**
- Usuario sin permiso para crear automatización: propuesta va a "pendiente de aprobación" para Owner/Admin.

**Compliance:**
- Intento de generar output externo sin HITL: hard block.

### 8.2 Cómo se recupera
- Reintentar mensaje.
- Cambiar modo manualmente si la detección fue incorrecta.
- Dividir la consulta en pasos más pequeños.
- Escalar a Owner/Admin si la propuesta requiere permisos.

### 8.3 Quién se entera
| Fallo | Notificación | Nivel |
|---|---|---|
| Timeout skill | Usuario + log | P2 |
| Modo detectado incorrecto | Usuario puede corregir | — |
| Permiso insuficiente | Owner/Admin | P2 |
| Data class no permitida | Owner/Admin + audit | P1 |
| Bypass HITL | Owner + audit | P0 |

---

## DIMENSIÓN 9 — APRENDIZAJE

### 9.1 Qué aprende el sistema de este uso
- Correcciones de María a respuestas del Workspace.
- Aprobaciones/rechazos de drafts generados.
- Patrones recurrentes que sugieren crear una regla o automatización.
- Golden samples cuando aprueba sin editar.

### 9.2 Cómo mejora con el tiempo
- PatchRAG trae correcciones previas al contexto de nuevas consultas similares.
- El tab Aprendizaje muestra candidatos a golden samples y reglas.
- Sugerencias de "Crear rutina" cuando detecta un pat repetido ≥N veces.

### 9.3 Qué feedback da el usuario
- Implícito: edita respuesta, aprueba, rechaza, descarta.
- Explícito: thumbs up/down con razón tipificada (tone, data, structure, policy, scope, context).
- En tab Aprendizaje: aprobar/descartar candidatos golden o reglas.

---

## DIMENSIÓN 10 — ELIMINACIÓN

### 10.1 Cómo se elimina
- **Conversación:** María puede archivar una conversación. No se borra; queda en historial.
- **Propuesta en sandbox:** se puede descartar. El objeto sandbox se marca como `rejected` y permanece en audit.
- **Objeto promovido:** se depreca siguiendo el state machine del módulo correspondiente.

### 10.2 Qué pasa con lo que dependía
- Conversación archivada: los objetos creados desde ella siguen vivos.
- Propuesta descartada: no afecta producción.

### 10.3 Es reversible
- Archivar conversación: sí, se puede restaurar desde historial.
- Descartar propuesta: no; se debe crear de nuevo.

---

## DIMENSIÓN 11 — RELACIONES

### 11.1 Con qué se relaciona
- **Mesa de Control:** los outputs accionables van a Zona 1/2/4; Zona 3 recibe objetos sandbox.
- **Agent Factory / Skill Factory:** donde se promueven o editan los objetos creados en modo Construcción.
- **Rutinas:** modo Automatización crea entradas en el módulo Rutina.
- **Action Engine:** ejecuta skills, aplica policies y data classification.
- **Letta:** memoria working/episodic del agente.
- **Eventing/Outbox:** sincroniza cambios en tiempo real.

### 11.2 En qué orden
1. Workspace detecta modo.
2. Opera/crea propuesta.
3. Usuario confirma.
4. Objeto va a sandbox.
5. Owner/Admin promueve.
6. Objeto pasa a activo y puede producir tareas/drafts.

### 11.3 Qué rompe si este módulo falla
- No hay forma de trabajo exploratorio ni iterativo.
- No se pueden crear rutinas ni agentes conversacionalmente.
- Los usuarios vuelven a herramientas externas, rompiendo el flujo HITL centralizado.

---

## DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

### 12.1 Quién puede verlo
- **Operator:** sus conversaciones; no ve conversaciones de otros salvo que sean compartidas.
- **Supervisor:** conversaciones de su equipo.
- **Admin/Owner:** todas las conversaciones del tenant.
- **Viewer:** solo historial propio o compartido, sin crear.
- RLS por tenant; nunca cross-tenant.

### 12.2 Qué queda en el audit trail D10
Por conversación y por acción:
- `tenant_id`, `user_id`, `actor_role_at_decision`
- `action`: workspace.message_sent, workspace.mode_detected, workspace.draft_created, workspace.automation_proposed, workspace.automation_confirmed, workspace.sandbox_promoted
- `resource_id`: conversación_id / draft_id / automation_id / agent_id
- `data_class`, `model_provider`, `model_id`
- `human_gate_required`, `human_approver_id`
- `timestamp`, `sha_chain_prev`, `sha_chain_curr`

### 12.3 Qué restricciones de datos aplican
- Uploads se clasifican automáticamente antes de procesar; N3/N4 hard-block en E1.
- Working memory no persiste sin gate humano (ARCH_AGENT_PRINCIPLES P5).
- Cada conversación hereda ceiling de data class; si un chunk supera el ceiling, se pide elevación.
- DPA Anthropic para calls LLM.

---

## DIMENSIÓN 13 — DESKTOP VS WEB

### 13.1 En cuál superficie vive
**Desktop (Electron) exclusivamente en E1.** Workspace es la pantalla operativa del trabajador administrativo.

### 13.2 Diferencias entre desktop y web
- No existe versión web de Workspace en E1.
- Agent Factory (web) es donde se editan/promueven los objetos creados en Workspace.
- Configuración de tenant y usuarios es web; operación diaria es desktop.

### 13.3 Offline y sincronización
- Workspace requiere conexión para ejecutar skills.
- Si se pierde conexión, el composer guarda borrador local.
- Al reconectar, se sincronizan mensajes y se reanuda streaming si aplica.
- Conflictos: si otro usuario aprobó un draft creado desde Workspace, el chat muestra estado actualizado.

[PENDIENTE — SPEC_FB_WORKSPACE_v1 en stub: detalle exacto de los 3 modos, layout de 3 columnas, tipos de archivo aceptados, tamaño límite, y especificación completa del contexto activo y SpaceLoom en E1]

---

---

# PENDIENTES QUE REQUIEREN DECISIÓN CEO

1. **[PENDIENTE — SPEC_FB_ROUTINES_v1 en stub]** Confirmar wizard completo de creación de rutina y cantidad mínima de runs de prueba para promover rutinas con autonomy AUTO_NOTIFICA / AUTO_EXCEPCIONES.
2. **[PENDIENTE — SPEC_FB_WORKSPACE_v1 en stub]** Confirmar layout final de Workspace (3 columnas vs variante responsive), tipos de archivo permitidos y tamaño máximo de upload.
3. **[PENDIENTE — SPEC_FB_WORKSPACE_v1 en stub]** Definir si SpaceLoom en E1 es solo un botón "Pensar con IA" o requiere panel dedicado, y cómo vuelve el resultado a WorkLoom.
4. **[PENDIENTE — ENT_FB_WORK_TYPE_PACK_v1 en stub]** Confirmar si el work-type pack por defecto en E1 incluye plantillas de rutinas pre-armadas (ej. "seguidor de RFQ", "alerta stock") o solo skills/agentes base.
5. **[PENDIENTE — ENT_FB_INBOUND_TAXONOMY_v1 en stub]** Confirmar si ciertos tipos de inbound (ej. tipo 11 notificación logística) pueden ser manejados 100% por rutinas o siempre requieren HITL.
6. **[PENDIENTE]** Decidir si un Operator puede confirmar una propuesta de rutina en Workspace o si siempre requiere Owner/Admin (impacta permisos y flujo de Zona 3).
7. **[PENDIENTE]** Definir fórmula exacta y threshold de signal-to-noise ratio que dispara sugerencia de ajuste o pausa automática de una rutina.

---

# CONTRADICCIONES DETECTADAS CON LA KB

1. **Roles E1:** El contexto general y SCH_FB_FUNCTIONAL_SPEC_v1 declaran 5 roles canónicos (Owner/Admin/Operator/Supervisor/Viewer). PLB_FB_FOUNDATION_BETA_v1 enmienda E-4 (2026-06-11) reduce E1 a 2 roles (Owner, Operator). La ficha respeta los 5 roles canónicos del spec funcional, pero la implementación E1 debe considerar la enmienda si el CEO la mantiene vigente.
2. **Canales E1:** El contexto general incluye WhatsApp BSP, Telegram Bot, Gmail/IMAP, Desktop app. La enmienda E-5 de PLB_FB_FOUNDATION_BETA_v1 establece email-only en E1-E2, con WhatsApp a E3. La ficha asume multi-canal en descripción pero aplica HITL y restricciones independientemente del canal.
3. **Sub-agentes/multi-agente:** PLB_FB_FOUNDATION_BETA_v1 TIER 1 #15 prohíbe orquestación entre agentes y sub-agentes en E1. SPEC_FABERLOOM_AGENT_COMPOSITION_v1 y SPEC_FABERLOOM_WORKFLOW_ENGINE_v1 describen orquestador + sub-agentes como patrón técnico. SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 actúa como puente: sub-agentes como standalone E1, composición jerárquica E2. La ficha de Rutina respeta single-agent por task y cadena lineal de skills.
4. **Skill Factory y tools:** PLB_FB_FOUNDATION_BETA_v1 TIER 1 #16 prohíbe tools externas y HTTP calls. SPEC_ACTION_ENGINE.md describe bypass mode y ActionRegistry que podrían incluir tools. SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 aclara que wrappers existen pero están bloqueados en runtime de skill E1. La ficha no asigna tools a rutinas en E1.
5. **Workspace lateral panel:** SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 v1.1 (2026-05-02) establece que toggles on/off de agentes y panel de aprendizaje viven en Workspace como hero. VERSIONES POSTERIORES v1.8-v1.9 del mismo doc mueven esos toggles al panel derecho de Workspace y dejan la Mesa solo con trabajo. La ficha sigue la versión más reciente del doc (panel derecho con tabs Agentes/Skills/Aprendizaje).
6. **Estados de rutina:** SCH_FB_FUNCTIONAL_SPEC_v1 lista `sandbox / active / paused / failed / deprecated`. El prompt del AGENTE_5 agrega `running` como estado posible en el state machine. La ficha respeta los estados canónicos del spec; `running` se modela como `automation_run.status`, no como estado de la rutina misma.

---

*Ficha generada por AGENTE_5_RUTINAS_WORKSPACE. No contiene datos inventados; los huecos están marcados como [PENDIENTE] con referencia al documento en stub.*
