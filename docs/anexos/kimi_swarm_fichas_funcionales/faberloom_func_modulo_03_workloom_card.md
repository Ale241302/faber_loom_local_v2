# Módulo 03 — Mesa de Control (WorkLoom) + Card de trabajo

## Módulo: Mesa de Control (WorkLoom)

**SUPERFICIE:** Desktop (Electron) — pantalla principal operativa  
**SPRINT E1:** S5  
**ROLES QUE LO USAN:** Operator (uso diario principal), Supervisor (supervisión y override), Admin (configuración visible/read-only contextual), Owner (costos/audit)  
**DATA CLASS TÍPICA:** N1 (metadata operativa), N2 cuando la card contiene resumen de drafts con pricing/margen (hereda del objeto subyacente)  

---

### DIMENSIÓN 1 — EXISTENCIA

#### 1.1 Por qué existe
María (Operator) procesa 20-30 tareas mixtas por día (RFQs, follow-ups, consultas, alertas, drafts por aprobar). Sin WorkLoom, tiene que abrir Gmail, WhatsApp Web, una hoja de cálculo, el CRM y el chat interno para saber qué requiere su atención. Eso genera fatiga de contexto, olvidos y demoras. Sin este módulo, María no sabe qué hacer primero; los drafts del agente se pierden en la bandeja de entrada y las urgencias aparecen tarde.

#### 1.2 A quién le duele
- **Operator:** es la persona que pasa el día entero en esta pantalla.
- **Supervisor:** necesita ver en qué está trabajando su equipo y dónde se atascan los drafts.
- **Owner/Admin:** necesitan ver costos, estado de agentes y posibles cuellos de botella sin entrar a reportes separados.

#### 1.3 Cuando aparece
Cada vez que María abre la app desktop. Además, WorkLoom se actualiza en tiempo real cuando llegan eventos del bus (feed.item.received, draft.generated, draft.ready_for_signature, agent.alarma, freshness.violation).

---

### DIMENSIÓN 2 — PROPÓSITO

#### 2.1 Para qué
Para que toda la cola de trabajo del día esté en un único lugar, ordenada por urgencia real, con acciones directas que permitan a María decidir rápidamente qué atender.

#### 2.2 Qué valor entrega
- Reduce la cantidad de herramientas que María debe revisar de 4-5 a 1.
- Ordena el trabajo por prioridad aprendida + SLA, no por orden de llegada.
- Permite aprobar, iterar o descartar items sin salir de la pantalla principal.

#### 2.3 Qué pasa si no existe
María vuelve a operar desde el inbox de Gmail/WhatsApp; los drafts del agente se acumulan sin revisión, los SLA se vencen y la promesa de "La IA prepara. Vos aportás tu criterio." se rompe porque el criterio humano no tiene bandeja de llegada clara.

---

### DIMENSIÓN 3 — CREACIÓN

#### 3.1 Cómo se crea
N/A — WorkLoom es la pantalla principal del desktop y siempre existe como superficie. No es un objeto que se cree.

#### 3.2 Quién puede crearlo
N/A.

#### 3.3 Qué necesita para crearse
N/A — depende de que existan tareas/drafts/automatizaciones para mostrar. Si no hay nada, la Mesa muestra el estado vacío con mensaje "No hay items pendientes" y sugerencias de Workspace.

---

### DIMENSIÓN 4 — USO DIARIO

#### 4.1 Cómo se usa en el día a día
Flujo típico de María:
1. Abre la app desktop por la mañana; WorkLoom es la pantalla de inicio.
2. Zona 1 (Lo urgente) está expandida por defecto. Revisa si hay alarmas o drafts críticos.
3. Zona 2 (Esperando tu firma) muestra drafts listos para HITL. María las revisa en orden de SLA más próximo.
4. Zona 3 (SANDBOX) aparece expandida solo si hay agentes/skills/rutinas creadas vía Workspace esperando promote. María no puede promover; solo Owner/Admin. Ella ve el badge y puede avisar.
5. Zona 4 (Inbox completo) está plegada por defecto. María la expande si necesita buscar algo que no está en Zona 1/2.
6. Zona 5 (Automatizaciones activas) está plegada. María la revisa para pausar/reactivar rutinas si es necesario.
7. Durante el día, las cards se mueven solas entre zonas vía WebSocket push.
8. Al cerrar, no hay guardado explícito; el estado vive en el servidor.

#### 4.2 Cómo se invoca
- Navegación directa: WorkLoom es la home de la app desktop.
- Notificación: badge en sidebar con contador total de items pendientes.
- Deep link: `faberloom://mesa/zona/2` o similar para llevar a María a una card específica desde una notificación externa (ej. email digest).

#### 4.3 Qué ve el usuario mientras ocurre
- Inicial: zona expandida con cards ordenadas.
- En proceso: spinner sutil en la card cuando el sistema está ejecutando una acción (ej. enviando draft aprobado).
- Completado: animación de check, card desaparece de la zona activa y aparece en historial.
- Error: card se mueve a Zona 1 con badge de error y acción "Ver detalle".

---

### DIMENSIÓN 5 — EDICIÓN

#### 5.1 Cómo se edita
N/A — WorkLoom es una superficie de lectura y acción. No se edita la pantalla en sí.

#### 5.2 Qué se puede cambiar y qué no
- Sí: orden de las zonas plegables (colapsar/expandir), filtros de Zona 4, ordenación dentro de Zona 4.
- No: la lógica de qué entra en cada zona, los SLA, ni los datos de las cards. Esos son propiedades del objeto subyacente (task, draft, automation_run).

#### 5.3 Qué pasa con lo generado previamente
N/A — la Mesa no genera outputs.

---

### DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

#### 6.1 Cómo se mueve
WorkLoom como superficie no tiene state machine propia. Las cards que contiene se mueven según el estado del objeto subyacente:

- Draft `awaiting_approval` → Zona 2.
- Draft con SLA a <30 min o que falló envío → Zona 1.
- Draft `approved` → desaparece de Zona 2, genera evento `draft.sent`.
- Draft `rejected` o `expired` → desaparece de Zona 2, queda en historial.
- Task `running` con alarmas/escalación → Zona 1.
- Task `completed` → desaparece de las zonas activas.
- Automation_run en SANDBOX esperando promote → Zona 3.
- Rutina `active` → Zona 5.
- Rutina `paused`/`failed` → Zona 5 con estado destacado.

#### 6.2 Qué dispara el movimiento
- Automático: eventos del bus (WebSocket push) cuando cambia el estado del objeto subyacente.
- Manual: María ejecuta una acción inline en la card (aprobar, rechazar, pausar rutina) que dispara la transición.

#### 6.3 Quién puede moverlo
- Operator: mueve sus propias cards (aprobar/rechazar sus drafts, pausar sus rutinas).
- Supervisor: puede ver y actuar sobre cards de su equipo.
- Admin/Owner: pueden actuar sobre cualquier card del tenant.
- Viewer: solo lectura.

#### 6.4 Qué se notifica y a quién
- Nuevo item en Zona 1: toast en desktop + badge sidebar. Si es externo urgente, también notificación Telegram al Operator asignado.
- Nuevo draft en Zona 2: badge sidebar y contador en icono de WorkLoom. No toast si no es urgente.
- Item en Zona 3 esperando promote: notificación a Owner/Admin (no a Operator).
- Rutina con error en Zona 5: badge + alerta a Admin/Owner.

---

### DIMENSIÓN 7 — OUTPUT

#### 7.1 Qué produce para el usuario
N/A — WorkLoom es una superficie de lectura y acción. No produce outputs nuevos; muestra los que generan otros módulos.

#### 7.2 Qué produce para el sistema
- Eventos de UI: `feed.item.dispatched` cuando María asigna manualmente un item a un agente.
- Eventos de acción: cuando María aprueba/rechaza/pausa desde una card, se emiten los eventos correspondientes del módulo subyacente (`draft.approved`, `draft.rejected`, `agent.config.updated`, etc.).
- Logs de interacción: tiempo de decisión, zona desde la que se actuó, tipo de acción inline usada (métricas para UserControlProfile).

#### 7.3 Dónde aparece el output
N/A — es la pantalla misma.

#### 7.4 Qué formato tiene
N/A.

---

### DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
- **WebSocket caído:** las cards dejan de actualizarse en tiempo real. María ve un indicador de "sincronización pendiente" y un botón "Reconectar". Las acciones que ella tome se encolan localmente y se sincronizan al reconectar; si hay conflicto, se muestra diff.
- **Error al cargar estado inicial:** se muestra estado de error con botón "Reintentar" y fallback a último snapshot cacheado.
- **Permiso insuficiente:** si María intenta actuar sobre una card de otro usuario sin permiso, el sistema muestra "No tenés permiso para este item" y loguea `permission.denied`.
- **Fallo de envío de draft aprobado:** la card vuelve a Zona 1 con badge de error; el draft queda en estado `approved_pending_send`.

#### 8.2 Cómo se recupera
- Reconexión WebSocket automática con backoff exponencial.
- Re-fetch de estado completo si el gap de eventos supera 24h (`sync_required`).
- Retry de acciones pendientes desde cola local.

#### 8.3 Quién se entera
- Usuario: María ve el indicador de desconexión.
- Owner/Admin: alerta si la desconexión persiste >5 min o si hay items en Zona 1 por fallo técnico.
- Grafana/Langfuse: métricas de latencia y disponibilidad.

---

### DIMENSIÓN 9 — APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Tiempo de decisión por tipo de card y zona.
- Acción más frecuente por tipo de item (aprobar vs editar vs rechazar).
- Qué cards María ignora o deja vencer.
- Patrones de navegación (qué zonas expande primero, qué filtros usa en Zona 4).

#### 9.2 Cómo mejora con el tiempo
- El sistema ajusta el orden dentro de las zonas según prioridad aprendida + SLA.
- Sugiere acciones primarias contextuales en la card basadas en historial.
- Mejora la clasificación de qué entra en Zona 1 vs Zona 2 vs Zona 4.

#### 9.3 Qué feedback da el usuario
- Implícito: click, aprobación, edición, rechazo, tiempo de decisión.
- Explícito: dropdown de razón al rechazar/editar; posibilidad de marcar "No es urgente" para re-clasificar un item de Zona 1 a Zona 2/4.

---

### DIMENSIÓN 10 — ELIMINACIÓN

#### 10.1 Cómo se elimina
N/A — WorkLoom no se elimina. Es la superficie principal.

#### 10.2 Qué pasa con lo que dependía
N/A.

#### 10.3 Es reversible
N/A.

---

### DIMENSIÓN 11 — RELACIONES

#### 11.1 Con qué se relaciona
- Se alimenta de: tasks, drafts, automation_runs, feed_items, agentes, rutinas.
- Consume eventos de: SPEC_FB_EVENTING_AND_OUTBOX_v1.
- Envía acciones a: módulo de drafts (aprobar/editar/rechazar), módulo de agentes (pausar/activar), módulo de rutinas (pausar/activar).
- Relacionado con: Workspace (cuando María abre un item en modo construcción/iteración).

#### 11.2 En qué orden
WorkLoom depende de que existan previamente:
1. Auth + RLS + tenant bootstrap.
2. Tasks y drafts funcionando.
3. Eventing/outbox con WebSocket.
4. Agentes y rutinas (para Zona 3 y Zona 5).

#### 11.3 Qué rompe si este módulo falla
- Si WorkLoom no carga, el día operativo de María se detiene.
- Si el WebSocket no funciona, María opera con datos desactualizados y puede tomar decisiones sobre items ya resueltos.
- Si las acciones inline fallan, el HITL se bloquea y los drafts no salen.

---

### DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
- Operator: ve sus propios drafts y tareas, y las automatizaciones del tenant.
- Supervisor: ve drafts/tareas de su equipo.
- Admin/Owner: ven todo el tenant.
- Viewer: solo lectura de historial y zonas no sensibles.
- RLS asegura que María nunca ve datos de otro tenant.

#### 12.2 Qué queda en el audit trail D10
Toda acción desde WorkLoom genera audit entry con:
- `tenant_id`, `user_id`, `actor_role_at_decision`
- `action` (ej. draft.approved, routine.paused, feed.item.dispatched)
- `resource_id`, `data_class`
- `model_provider`, `model_id` (si aplica)
- `human_gate_required`, `human_approver_id`
- `timestamp`, `sha_chain`

#### 12.3 Qué restricciones de datos aplican
- Data class típica N1-N2.
- Cards con datos N2 (pricing/margen) solo visibles para roles autorizados.
- No se muestran datos N3/N4 en WorkLoom en E1 (TIER 1 #3: N3-N4 prohibidos).

---

### DIMENSIÓN 13 — DESKTOP vs WEB

#### 13.1 En cuál superficie vive
Desktop (Electron) exclusivamente en E1. Es la pantalla principal del trabajador administrativo.

#### 13.2 Diferencias entre desktop y web
- WorkLoom no existe en web en E1.
- Owner/Admin pueden ver algunas métricas de WorkLoom desde dashboards web, pero la acción operativa (aprobar drafts, pausar rutinas) requiere desktop.

#### 13.3 Offline y sincronización
- WorkLoom requiere conexión para funcionar.
- Si se pierde conexión brevemente, las acciones de María se encolan localmente y se sincronizan al reconectar.
- Conflictos: si el estado del servidor cambió mientras María estaba desconectada, se muestra modal de diff con opción de refrescar o forzar su acción.

---

## Módulo: Card de trabajo

**SUPERFICIE:** Desktop (Electron) — WorkLoom  
**SPRINT E1:** S5  
**ROLES QUE LO USAN:** Operator, Supervisor, Admin, Owner, Viewer (solo lectura)  
**DATA CLASS TÍPICA:** N1 (metadata), N2 si incluye pricing/margen (hereda del objeto)  

---

### DIMENSIÓN 1 — EXISTENCIA

#### 1.1 Por qué existe
María procesa 20-30 items por día. Sin una unidad visual clara, tendría que abrir cada item individual para entender qué requiere. La card condensa en 3 segundos la información crítica: cliente, tipo de tarea, canal, confianza, SLA y acción principal.

#### 1.2 A quien le duele
Principalmente Operator. También Supervisor, que necesita escanear rápidamente el trabajo del equipo.

#### 1.3 Cuando aparece
Cada vez que un objeto operativo (task, draft, automation_run, feed_item) necesita atención humana o seguimiento en WorkLoom.

---

### DIMENSIÓN 2 — PROPÓSITO

#### 2.1 Para qué
Para que María entienda en 3 segundos qué requiere ese item y qué tiene que hacer, sin abrirlo.

#### 2.2 Qué valor entrega
- Reduce el tiempo de triage.
- Permite decisiones inline sin navegación profunda.
- Mantiene el foco en la acción, no en la herramienta.

#### 2.3 Qué pasa si no existe
María tiene que abrir cada correo/mensaje/tarea para entender qué hacer. La productividad cae y aumentan los errores de priorización.

---

### DIMENSIÓN 3 — CREACIÓN

#### 3.1 Cómo se crea
N/A — la card se renderiza automáticamente a partir de un objeto subyacente (task, draft, automation_run, feed_item).

#### 3.2 Quién puede crearlo
N/A.

#### 3.3 Qué necesita para crearse
Debe existir el objeto subyacente con metadata suficiente: cliente/remitente, tipo de tarea, canal de origen, confidence, SLA, acción primaria sugerida.

---

### DIMENSIÓN 4 — USO DIARIO

#### 4.1 Cómo se usa en el día a día
María escanea las zonas, lee las cards y decide:
- Click en la card para abrir panel completo/detalle.
- Acción inline directa si está segura (ej. "Aprobar" en draft de bajo riesgo).
- Dejar para más tarde si el SLA lo permite.

#### 4.2 Cómo se invoca
Aparece automáticamente en WorkLoom cuando el objeto subyacente cambia a un estado visible.

#### 4.3 Qué ve el usuario mientras ocurre
- Card compacta con información esencial.
- Badges de estado (confidence HIGH/LOW, SLA restante, tipo de tarea).
- Animación al moverse entre zonas o desaparecer.

---

### DIMENSIÓN 5 — EDICIÓN

#### 5.1 Cómo se edita
N/A — la card es display. La edición ocurre en el panel/detalle del objeto subyacente.

#### 5.2 Qué se puede cambiar y qué no
- No se cambia la card directamente.
- Acciones inline modifican el objeto subyacente (aprobar draft, pausar rutina, descartar alerta).

#### 5.3 Qué pasa con lo generado previamente
N/A.

---

### DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

#### 6.1 Cómo se mueve
La card no tiene state machine propia. Se mueve entre zonas según el estado del objeto subyacente:
- Entra en Zona 1 si es urgente o falló.
- Entra en Zona 2 si es un draft esperando aprobación.
- Entra en Zona 3 si es un objeto en SANDBOX esperando promote.
- Entra en Zona 4 si es inbox general.
- Entra en Zona 5 si representa una automatización activa.
- Desaparece cuando el objeto subyacente es completado, rechazado, expirado o descartado.

#### 6.2 Qué dispara el movimiento
Eventos del bus (`feed.item.received`, `draft.generated`, `draft.approved`, `draft.rejected`, `draft.expired`, `task.status_changed`, `automation.status_changed`).

#### 6.3 Quién puede moverlo
El sistema mueve la card automáticamente. El usuario la mueve indirectamente al ejecutar acciones inline.

#### 6.4 Qué se notifica y a quien
Ver notificaciones de WorkLoom. A nivel card: micro-animaciones y toasts al ejecutar acciones.

---

### DIMENSIÓN 7 — OUTPUT

#### 7.1 Qué produce para el usuario
N/A — la card es representación visual.

#### 7.2 Qué produce para el sistema
- Logs de interacción: qué card se vio, en qué zona, qué acción inline se usó.
- Métricas para UserControlProfile y aprendizaje.

#### 7.3 Dónde aparece el output
En WorkLoom.

#### 7.4 Qué formato tiene
Componente UI de Electron/React.

---

### DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
- Si la metadata de la card está incompleta (falta cliente, tipo, SLA), se muestra con badge "Revisar" y click abre el detalle.
- Si el objeto subyacente fue eliminado mientras la card está visible, la card muestra "Item no disponible" y desaparece al refrescar.

#### 8.2 Cómo se recupera
Re-fetch del estado de WorkLoom.

#### 8.3 Quién se entera
Usuario: visualmente. Admin: si hay cards corruptas recurrentes.

---

### DIMENSIÓN 9 — APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Qué campos de la card María mira primero (eye-tracking opcional, no en E1).
- Qué acciones inline usa más.
- Cuánto tiempo pasa sobre una card antes de decidir.

#### 9.2 Cómo mejora con el tiempo
- Ajuste de qué campos mostrar por tipo de tarea.
- Priorización de acciones inline según frecuencia de uso.

#### 9.3 Qué feedback da el usuario
Implícito: clicks, tiempo de decisión, acciones inline.

---

### DIMENSIÓN 10 — ELIMINACIÓN

#### 10.1 Cómo se elimina
N/A — la card desaparece cuando el objeto subyacente cambia de estado. No se elimina directamente.

#### 10.2 Qué pasa con lo que dependía
N/A.

#### 10.3 Es reversible
N/A.

---

### DIMENSIÓN 11 — RELACIONES

#### 11.1 Con qué se relaciona
- Es representación visual de: tasks, drafts, automation_runs, feed_items.
- Dependiente de: WorkLoom (zona), eventing/outbox (actualizaciones), módulos subyacentes.

#### 11.2 En qué orden
La card requiere que exista el objeto subyacente y el evento que la posicione en una zona.

#### 11.3 Qué rompe si este módulo falla
Si las cards no se renderizan correctamente, María no puede operar WorkLoom.

---

### DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
Misma matriz de permisos que WorkLoom. La card hereda los permisos del objeto subyacente.

#### 12.2 Qué queda en el audit trail D10
Las acciones inline generan audit entries del módulo subyacente. La visualización de la card no genera audit por sí sola.

#### 12.3 Qué restricciones de datos aplican
- No se muestran datos N3/N4 en la card en E1.
- Datos N2 (pricing/margen) se muestran solo si el rol tiene permiso.

---

### DIMENSIÓN 13 — DESKTOP vs WEB

#### 13.1 En cuál superficie vive
Desktop (Electron) en E1.

#### 13.2 Diferencias entre desktop y web
N/A — no hay cards de WorkLoom en web en E1.

#### 13.3 Offline y sincronización
La card puede quedar visible con estado desactualizado si hay desconexión. Se resincroniza al reconectar.

---

## Detalles específicos solicitados

### Mesa de Control

#### ¿Qué criterio define que algo es urgente (Zona 1)?
[PENDIENTE — el criterio exacto de priorización de Zona 1 no está detallado en los docs leídos; se requiere definir thresholds de SLA, confidence, tipo de error y acción externa]

#### ¿Quién decide qué entra en Zona 1?
El sistema decide automáticamente según reglas configuradas en el agente/rutina. Owner/Admin pueden ajustar thresholds generales del tenant.

#### ¿Cómo se ordena dentro de la zona?
Por SLA más próximo primero; luego por prioridad aprendida; luego por hora de llegada.

#### Zona 2 (firma): orden por SLA
Las drafts se ordenan por `expected_completion_by` ascendente. El que se vence primero, primero.

#### ¿Cómo se diferencia de Zona 1?
Zona 1 es para items que requieren atención inmediata (alarma, SLA crítico, error). Zona 2 es para drafts listos para revisar con SLA aún no crítico.

#### Zona 3 (SANDBOX): qué aparece acá
Agentes, skills o rutinas creadas vía Workspace o Agent/Skill Factory que están en estado `shadow`/`sandbox` esperando ser promovidas a `active`/`running`.

#### ¿Quién puede hacer promote desde acá?
Solo Owner/Admin del tenant (TIER 1 #16.10). Operator ve el badge pero no puede promover.

#### Zona 4 (inbox completo): filtros
- Por tipo de item (RFQ, follow-up, consulta, spam, alerta).
- Por canal (Gmail, WhatsApp).
- Por estado (pendiente, auto-resuelto, archivado).
- Por cliente/remitente.
- Por fecha.

#### ¿Cómo se diferencia del resto de zonas?
Zona 4 es un listado completo de TODO lo entrante, sin priorización operativa. Las zonas 1-3 son priorizadas y accionables.

#### Zona 5 (automatizaciones): switches ON/OFF
Cada rutina aparece con switch que refleja su estado `active`/`paused`. María puede pausar/reactivar si tiene permiso. Se muestra: nombre de la rutina, última ejecución, próxima ejecución, estado, contador de éxitos/errores recientes.

#### Panel lateral izquierdo: agentes on/off, aprendizaje en curso
[PENDIENTE — según SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 §8.2, los toggles de agentes on/off y panel de aprendizaje en curso viven en el Workspace, no en la Mesa. Si el prompt del CEO mantiene el panel lateral en WorkLoom, se requiere decisión CEO.]

### Card de trabajo

#### Campos exactos que muestra
- Cliente / remitente.
- Tipo de tarea (RFQ, follow-up, consulta, draft, escalación, rutina, SANDBOX).
- Canal de origen (Gmail, WhatsApp, Workspace).
- Confidence HIGH/LOW.
- SLA restante (timer).
- Acción primaria contextual ("Revisar y aprobar", "Resolver", "Abrir Workspace", "Promover", etc.).
- Badges de estado (urgente, error, sandbox, etc.).

#### Acciones inline en la card
- Aprobar (drafts de bajo riesgo).
- Rechazar (con razón).
- Abrir/Ver detalle.
- Asignar agente.
- Pausar/Reactivar rutina.
- Descartar alerta.
- Promover (solo Owner/Admin en Zona 3).

#### Al hacer click
Abre panel lateral o pantalla completa con el detalle del objeto: draft + evidence bundle, conversación, metadatos, acciones extendidas.

#### Diferencias entre cards según tipo
- **Draft:** cliente, tipo, confidence, SLA, acción "Aprobar/Rechazar".
- **Escalación:** badge de alarma, descripción del problema, acción "Ver detalle".
- **Rutina:** nombre, estado ON/OFF, última ejecución, acción "Pausar/Reactivar".
- **SANDBOX:** objeto propuesto, quién lo creó, acción "Promover" (solo Owner/Admin).

#### Badge de confidence HIGH vs LOW
- HIGH: ≥0.85 (approval_threshold default). Visualización limpia, sin advertencias.
- LOW: <0.85. Badge amarillo/naranja, posible advertencia "Revisar con atención", puede forzar apertura del panel.

#### SLA timer
- Verde: SLA >50% restante.
- Amarillo: SLA entre 20% y 50%.
- Rojo: SLA <20% o vencido.
- Formato: "23 min", "1h 15min", "Vencido".

#### Cómo desaparece
- Al aprobar/rechazar un draft.
- Al completarse/fallarse/cancelarse una task.
- Al expirar un draft.
- Al descartarse una alerta.
- Al promover o deprecar un objeto de SANDBOX.

---

## Lista de PENDIENTEs que requieren decisión CEO

1. [PENDIENTE] Definir el criterio exacto y thresholds para que un item aparezca en Zona 1 (Lo urgente): ¿SLA <30 min? ¿confidence LOW + acción externa? ¿fallo técnico? ¿combinación ponderada?
2. [PENDIENTE] Confirmar si WorkLoom en E1 lleva panel lateral izquierdo con agentes on/off y aprendizaje en curso, o si esos elementos se mantienen en Workspace según SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 §8.2.
3. [PENDIENTE] Definir si Operator puede pausar/reactivar rutinas desde Zona 5 o si esa acción está restringida a Admin/Owner.
4. [PENDIENTE] Especificar el formato exacto del deep link a WorkLoom (`faberloom://mesa/...`) y qué parámetros soporta.
5. [PENDIENTE] Definir la política de reconexión offline: ¿cuánto tiempo se conserva la cola local de acciones? ¿qué pasa con conflictos de aprobación?
6. [PENDIENTE] El documento ENT_FB_INBOUND_TAXONOMY_v1 está en STUB; no se puede detallar los tipos de inbound que filtra Zona 4.
7. [PENDIENTE] El documento SPEC_FB_ROUTINES_v1 está en STUB; no se puede detallar la configuración completa de rutinas en Zona 5.
8. [PENDIENTE] El documento SPEC_FB_WORKSPACE_v1 está en STUB; no se puede detallar el flujo exacto de creación de objetos que luego aparecen en Zona 3.
9. [PENDIENTE] El documento ENT_FB_WORK_TYPE_PACK_v1 está en STUB; no se puede detallar cómo los work-type packs afectan la visualización de cards.

---

## Lista de contradicciones detectadas con la KB

1. **Ubicación de toggles de agentes y panel de aprendizaje:**
   - El prompt del AGENTE_3_WORKLOOM_CARD solicita "Panel lateral izquierdo: agentes on/off, aprendizaje en curso" en WorkLoom.
   - SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 §8.2 (v1.1 actualizado) establece: "los toggles on/off de agentes + el panel de aprendizaje en curso viven en el Workspace como hero (no en Mesa)".
   - Resolución requerida: CEO debe confirmar cuál modelo prevalece para E1.

2. **Número de roles en E1:**
   - PLB_FB_FOUNDATION_BETA_v1 original y SPEC_FB_AUTH_TENANT_RBAC_v1 definen 5 roles canónicos (Owner/Admin/Operator/Supervisor/Viewer).
   - La enmienda E-4 del PLB reduce los roles activos en E1 a 2 (Owner, Operator), con 5 roles entrando en E3.
   - La ficha usa 5 roles porque el prompt del agente lo solicita y la SPEC_FB_AUTH_TENANT_RBAC_v1 vigente todavía documenta 5 roles; sin embargo, para implementación E1 se debe aclarar si se usan 2 o 5.

3. **Mesa Kanban vs lista priorizada:**
   - SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1 §8.1 describe 5 zonas plegables.
   - En §8.4 v1.7 se menciona "Mesa Kanban" con 4 columnas (Crítico · Listo para revisar · Delegado · Error accionable) como parte de la iteración del mockup, mientras que en §8.1 y §8.2 el modelo final es 5 zonas plegables + separación Mesa/Workspace.
   - La ficha adopta el modelo 5 zonas plegables como canon vigente, pero queda registrada la contradicción histórica.

4. **Stack técnico del workflow engine vs Foundation Beta:**
   - SPEC_FABERLOOM_WORKFLOW_ENGINE_v1 propone pg-boss + Inngest + Letta + LangGraph como stack Fase 1.
   - PLB_FB_FOUNDATION_BETA_v1 enmienda E-3 define engine de skills sobre markdown + tools allowlist + SDK estándar, y PLB §2.1 define Celery como worker queue.
   - La ficha no profundiza en el engine de ejecución porque WorkLoom es superficie, pero la contradicción de stack afecta qué eventos y estados espera WorkLoom.

5. **Canales en E1:**
   - PLB_FB_FOUNDATION_BETA_v1 enmienda E-5 reduce E1 a email-only, dejando WhatsApp para E3.
   - El prompt del AGENTE_3_WORKLOOM_CARD menciona WhatsApp como canal de origen en cards.
   - La ficha mantiene el canal genérico en la descripción pero aclara que la disponibilidad real depende de la enmienda E-5.
