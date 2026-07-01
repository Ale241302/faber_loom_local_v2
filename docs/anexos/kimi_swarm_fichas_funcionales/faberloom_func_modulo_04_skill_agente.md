# Ficha funcional — Módulo 4: Skill + Agente

> Generada por AGENTE_4_SKILL_AGENTE del swarm de especificación funcional FaberLoom Foundation Beta E1.
> Docs obligatorios leídos: SCH_FB_FUNCTIONAL_SPEC_v1, PLB_FB_FOUNDATION_BETA_v1, SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1, SPEC_FB_AUTH_TENANT_RBAC_v1, SPEC_ACTION_ENGINE, ARCH_AGENT_PRINCIPLES, POL_DATA_CLASSIFICATION, ENT_FB_INBOUND_TAXONOMY_v1 (STUB), SPEC_FB_ROUTINES_v1 (STUB), SPEC_FB_WORKSPACE_v1 (STUB), ENT_FB_WORK_TYPE_PACK_v1 (STUB), SPEC_FABERLOOM_WORKFLOW_ENGINE_v1, SPEC_FABERLOOM_AGENT_COMPOSITION_v1, SCH_FB_TASK_ENTITY, SPEC_FB_EVENTING_AND_OUTBOX_v1.

---

## MÓDULO 1: Skill (capacidad reutilizable)

**MÓDULO:** Skill  
**SUPERFICIE:** Web (Skill Factory) + backend (ejecución vía API invocada desde desktop)  
**SPRINT E1:** S6 (Skill Factory + sandbox + límites duros)  
**ROLES QUE LO USAN:** Owner, Admin (configuración y promoción); Operator (uso indirecto a través del agente)  
**DATA CLASS TÍPICA:** Hereda la del input/task que la ejecuta; RFQ cotización = N2

---

### DIMENSIÓN 1 — EXISTENCIA

#### 1.1 Por qué existe
Alejandro (Owner/Admin del tenant) necesita adaptar cómo @cotizador responde cuando aparece un formato de RFQ o una excepción que el skill system no cubre. Sin Skill Factory, cada ajuste requiere modificar código del agente y redeployar. María (Operator) lo siente cuando un RFQ se clasifica mal o el draft omite un campo nuevo, y no hay forma de enseñarle al sistema sin pasar por desarrollo.

#### 1.2 A quién le duele
- **Owner/Admin:** responsable de crear, clonar, probar y promover skills.
- **Operator:** usa el skill indirectamente a través del agente; siente el efecto cuando un skill mejora o falla.
- **CEO (FaberLoom):** gobierna los 14 límites duros de TIER 1 #16.

#### 1.3 Cuándo aparece
Aparece cuando el tenant necesita una capacidad que no cubre el catálogo system (ej. "clasificar RFQ con formato de cliente X", "validar precio rápido", "formatear salida para WhatsApp") o cuando quiere clonar un skill system y ajustar su prompt/schema.

---

### DIMENSIÓN 2 — PROPÓSITO

#### 2.1 Para qué
Permitir que Owner/Admin del tenant cree, pruebe y promueva capacidades reutilizables (skills) que múltiples agentes puedan ejecutar sin reescribir lógica.

#### 2.2 Qué valor entrega
- Reduce el tiempo de adaptación de semanas a minutos.
- Un mismo skill puede ser usado por varios agentes del tenant.
- Aisla el riesgo: si un skill falla, no cae el agente ni el sistema (TIER 1 #16.14).

#### 2.3 Qué pasa si no existe
Cada agente arrastra su propia lógica embebida; cualquier cambio requiere tocar el agente. La base de conocimiento operativo del tenant queda dispersa y no auditada.

---

### DIMENSIÓN 3 — CREACIÓN

#### 3.1 Cómo se crea
Wizard de 5 pasos en Skill Factory (web):

1. **Origen:** clonar un skill system/tenant existente o crear desde cero.
2. **Identidad:** nombre, descripción y tipo (`classifier`, `generator`, `formatter` únicamente — TIER 1 #16.1).
3. **Prompt template:** system + user prompt con variables `{{input.campo}}`.
4. **Schema input/output:** campos y tipos permitidos (form simple, tipos whitelisted).
5. **Modelo + límites + sandbox:** seleccionar modelo (Haiku 4.5 / Sonnet 4.6), `timeout_ms` (default 30s, máx 60s), `cost_cap_usd` (default USD 0.50, máx USD 2.00) y ejecutar sandbox obligatorio antes de promote (TIER 1 #16.9).

#### 3.2 Quién puede crearlo
- **Owner/Admin** del tenant (TIER 1 #16.10).
- **Nota de roles E1:** PLB enmienda E-4 reduce roles activos en E1 a Owner y Operator; sin embargo TIER 1 #16.10 sigue refiriendo "Owner/Admin". Esto requiere decisión CEO (ver lista de PENDIENTEs).

#### 3.3 Qué necesita para crearse
- Tenant configurado y con DPA Anthropic vigente.
- KB del tenant disponible si el skill va a hacer retrieval interno.
- Al menos un caso de prueba para el sandbox.

---

### DIMENSIÓN 4 — USO DIARIO

#### 4.1 Cómo se usa en el día a día
El skill no se usa directamente desde la Mesa. Se invoca a través de un agente. Owner/Admin entra a Skill Factory para:
- Revisar skills system y clonar los que necesitan ajuste.
- Probar un skill en sandbox antes de promoverlo.
- Pausar o deprecar skills que ya no se usan.

María lo usa indirectamente: cada vez que @cotizador ejecuta, corre una cadena lineal de skills.

#### 4.2 Cómo se invoca
Indirectamente: un agente invoca el skill como paso de su cadena lineal de ejecución. No se invoca con `@mención`.

#### 4.3 Qué ve el usuario mientras ocurre
- En Skill Factory: card del skill con estado, tipo, versión, último sandbox, ejecuciones, costo acumulado.
- En ejecución: el skill no expone UI propia; sus resultados aparecen como output del agente (draft, decisión, tag) en la Mesa o en el Workspace.

---

### DIMENSIÓN 5 — EDICIÓN

#### 5.1 Cómo se edita
Desde Skill Factory, seleccionando el skill. Las ediciones generan una nueva versión (`version` int) sin perder el historial.

#### 5.2 Qué se puede cambiar y qué no
- **En SHADOW:** todo editable (origen ya está fijado al clonar/crear).
- **En ACTIVE:** se puede editar prompt template, schema, modelo, `timeout_ms` y `cost_cap_usd` dentro de los límites duros. No se puede cambiar `skill_type`, `origin`, `tenant_id` ni romper los 14 límites.

[PENDIENTE — KB no detalla si los campos editables en ACTIVE generan automáticamente un nuevo SHADOW o si la edición es directa sobre ACTIVE; requiere decisión de implementación.]

#### 5.3 Qué pasa con lo generado previamente
Las ejecuciones anteriores (`skill_executions`, `llm_calls`, drafts aprobados) quedan vinculadas a la versión que las generó. Las nuevas tareas usan la versión activa.

---

### DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

#### 6.1 State machine
```
SHADOW -- trigger: creado/clonado, actor: Owner/Admin --> SHADOW
SHADOW -- trigger: sandbox exitoso + promote, actor: Owner/Admin --> ACTIVE
ACTIVE -- trigger: pause manual, actor: Owner/Admin --> PAUSED
PAUSED -- trigger: resume manual, actor: Owner/Admin --> ACTIVE
ACTIVE/PAUSED -- trigger: deprecate, actor: Owner/Admin --> DEPRECATED
```

#### 6.2 Qué dispara el movimiento
- Sandbox exitoso + aprobación de Owner/Admin para pasar a ACTIVE.
- Decisión manual de pause/resume.
- Deprecación manual (no se borra; se desactiva para nuevos usos).

#### 6.3 Quién puede moverlo
Owner/Admin (TIER 1 #16.10). Promote bloqueado si no hay ejecución sandbox exitosa registrada en `skills.last_sandbox_test_at`.

#### 6.4 Qué se notifica y a quién
- Promote: toast/evento a Owner/Admin.
- Deprecate: warning en Agent Factory para los agentes que lo usan.
- Fallo de sandbox: notificación a quien lo ejecutó + log en audit.

**Contradicción con KB:** SCH_FB_FUNCTIONAL_SPEC_v1 define estados canónicos de skill como `SHADOW / ACTIVE / PAUSED / DEPRECATED`, pero el schema de PLB_FB_FOUNDATION_BETA_v1 §2.3 usa `('draft','active','deprecated')` sin `paused`. Se requiere alinear schema y estados canónicos.

---

### DIMENSIÓN 7 — OUTPUT

#### 7.1 Qué produce para el usuario
- Para Owner/Admin: un skill versionado, auditable y reusable.
- Para Operator: mejores drafts/decisiones/tags a través del agente que lo usa.

#### 7.2 Qué produce para el sistema
- Registro en `skill_executions` (TIER 1 #16.13).
- Registro en `llm_calls`.
- Eventos: `agent.config.updated` cuando un skill se edita/promueve; no hay un evento `skill.promoted` explícito en los 28 canónicos.
- Candidate gold sample cuando el output del skill se aprueba sin edición (vía el agente).

#### 7.3 Dónde aparece el output
- Skill Factory (web): listado, detalle, sandbox, versions.
- Mesa/Workspace (desktop): como output del agente (draft, decisión, tag).

#### 7.4 Qué formato tiene
- Output JSON validado contra `schema_output`.
- En Skill Factory: card con metadatos + JSON de sandbox.

---

### DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
| Tipo de fallo | Qué ve el usuario | Qué hace el sistema |
|---|---|---|
| Timeout > `timeout_ms` | "El skill tardó demasiado" | Aborta ejecución, marca `task.status=skill_failed`, registra `failed_skill_id` |
| Cost cap excedido | "Costo del skill excedido" | Aborta antes del call o durante, según enforce |
| Schema output inválido | "Respuesta del skill no válida" | `task.status=skill_failed`, error tipificado |
| LLM provider caído/rate limit | "Servicio de IA no disponible" | Retry exponencial 3× con backoff; si persiste, skill_failed |
| Validación TIER 1 #16 | Error de validación en el wizard | Rechaza crear/promover el skill |
| Skill cross-tenant | 403 | RLS/permission denied, audit inmutable |

#### 8.2 Cómo se recupera
- Corregir el skill en SHADOW, reejecutar sandbox y promover.
- Retry manual desde DLQ si fue un error transitorio del provider.
- Si el skill system falla, escalar a FaberLoom support.

#### 8.3 Quién se entera
- Owner/Admin: fallos de sandbox y superaciones de costo.
- Operator: si el fallo afecta una tarea suya (card en Mesa con badge error).
- Langfuse/Grafana: todos los fallos técnicos.

---

### DIMENSIÓN 9 — APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Aprobación sin edición + confidence HIGH → candidate gold sample.
- Edición antes de aprobar → diff en Outcome Ledger (skill refinement).
- Rechazo → razón tipificada (`tone`, `data`, `structure`, `policy`, `scope`, `context`) usada para ajustar prompt/template.
- Tiempo de decisión y tasa de edición → señal de calidad del skill.

#### 9.2 Cómo mejora con el tiempo
Owner/Admin aplica los aprendizajes editando el skill en SHADOW y promoviéndolo. No hay auto-promoción de skills sin gate humano (P5).

#### 9.3 Qué feedback da el usuario
- Implícito: aprobar / editar / rechazar el draft generado por el agente.
- Explícito: dropdown de razón de rechazo/edición.

---

### DIMENSIÓN 10 — ELIMINACIÓN

#### 10.1 Cómo se elimina
Los skills no se borran. Se **deprecan** (estado DEPRECATED). En SHADOW también se puede descartar antes de promover, pero una vez en ACTIVE la eliminación es deprecación.

#### 10.2 Qué pasa con lo que dependía
- Los agentes que lo tenían asignado muestran warning y no pueden ejecutarlo.
- Las ejecuciones históricas permanecen en `skill_executions`.
- Los drafts aprobados generados con ese skill permanecen.

#### 10.3 Es reversible
No. Un skill DEPRECATED no vuelve a ACTIVE. Si se necesita de nuevo, se clona a un nuevo SHADOW.

---

### DIMENSIÓN 11 — RELACIONES

#### 11.1 Con qué se relaciona
- **Alimenta a:** Agent Factory (agentes bindean skills), Engine ejecutor, Action Engine.
- **Depende de:** KB del tenant (retrieval interno), modelo Anthropic, tenant y DPA.
- **Alternativos:** skills system para casos estándar; no hay alternativa a tener una capacidad versionada.

#### 11.2 En qué orden
```
Tenant creado → KB seed → Skill Factory → skill en SHADOW → sandbox → ACTIVE → agente lo bindea → agente en running → task invoca agente → skill se ejecuta
```

#### 11.3 Qué rompe si este módulo falla
- Agent Factory no puede crear agentes funcionales sin skills.
- El engine no puede ejecutar pasos LLM de un agente.
- Toda cadena de cotización que dependa del skill falla.

---

### DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
- **Owner/Admin:** todos los skills del tenant.
- **Operator:** ve skills usados por sus agentes asignados; no accede a Skill Factory salvo que el permission matrix lo permita.
- **Viewer:** solo lectura si se le otorga.
- Nunca cross-tenant.

#### 12.2 Qué queda en el audit trail
Campos D10: `tenant_id`, `user_id`, `actor_role_at_decision`, `action` (create/clone/promote/pause/deprecate/edit), `resource_id` (skill_id), `data_class` (del input/task), `model_provider` (Anthropic), `model_id` (Haiku/Sonnet), `human_gate_required` (true para promote/deprecate), `human_approver_id`, `timestamp`, `sha_chain`.

#### 12.3 Qué restricciones de datos aplican
- Skill hereda `data_class` del task/input.
- N3/N4 no se procesan sin DPA; Action Engine D9 hard-bloquea (POL_DATA_CLASSIFICATION §I).
- Anonimización L0-L3 según data class.

---

### DIMENSIÓN 13 — DESKTOP vs WEB

#### 13.1 En cuál superficie vive
- **Web (Next.js):** Skill Factory completo (crear, clonar, editar, sandbox, promote, deprecar).
- **Backend:** ejecución del skill invocada por API desde el desktop.
- **Desktop (Electron):** el Operator ve el resultado del skill a través del agente (drafts, decisiones, tags).

#### 13.2 Diferencias entre desktop y web
- Web: config, governance, sandbox, costos.
- Desktop: uso operativo del skill vía agente; sin acceso a edición de skills.

#### 13.3 Offline y sincronización
No aplica para Skill Factory (requiere conexión). Los resultados de un skill en ejecución requieren conexión; si falla, el task queda en error y se recupera según D8.

---

## MÓDULO 2: Agente (instancia operativa con identidad)

**MÓDULO:** Agente  
**SUPERFICIE:** Web (Agent Factory) + Desktop (Mesa/Workspace via @mención)  
**SPRINT E1:** S6 (Agent Factory + asignaciones + sandbox)  
**ROLES QUE LO USAN:** Owner/Admin (configuración), Operator (invocación diaria), Supervisor/Viewer (según permisos)  
**DATA CLASS TÍPICA:** Hereda la del task/input; cotización B2B = N2

---

### DIMENSIÓN 1 — EXISTENCIA

#### 1.1 Por qué existe
El skill es abstracto: María no puede "hablarle" a `classify_rfq`. Necesita una instancia con nombre, avatar, canal y autonomía real que responda cuando ella escribe `@cotizador`. Sin agente, María tendría que saber qué skill invocar y en qué orden, lo que rompe la promesa de "La IA prepara. Vos aportás tu criterio."

#### 1.2 A quién le duele
- **Operator (María):** invoca agentes todo el día.
- **Owner/Admin:** configura qué agentes existen, qué skills usan y a quién sirven.
- **CEO:** decide cuánta autonomía se permite.

#### 1.3 Cuándo aparece
Aparece cuando el tenant necesita una entidad operativa visible: `@cotizador`, `@mail_ventas`, `@seguidor_rfq`, etc. Puede crearse desde Agent Factory o propuesto desde Workspace en modo Construcción (SPEC_FB_WORKSPACE_v1 está en STUB; detalles pendientes).

---

### DIMENSIÓN 2 — PROPÓSITO

#### 2.1 Para qué
Dar una identidad operativa a uno o más skills, con canal, autonomía y memoria, para que María pueda invocarlos con `@nombre` sin conocer la lógica interna.

#### 2.2 Qué valor entrega
- Abstrae la complejidad de skills.
- Permite varios agentes con distintos perfiles usando el mismo skill.
- Controla autonomía y riesgo por instancia.

#### 2.3 Qué pasa si no existe
María no tiene a quién llamar; cada tarea requiere manualmente seleccionar skills y secuencias. El sistema no escala más allá de 2-3 flujos.

---

### DIMENSIÓN 3 — CREACIÓN

#### 3.1 Cómo se crea
Wizard de 4 pasos en Agent Factory (web):

1. **Identidad:** nombre, descripción, categoría (Canal / Recurso / Cognitivo / Proceso), avatar, persona/Voice Profile, tono y glosario.
2. **Skills + autonomía:** asignar uno o más skills con orden lineal (drag-drop) y definir el `autonomy_ceiling` máximo permitido.
3. **Canal binding:** email, WhatsApp, workspace/chat interno, usando los canales ya configurados del tenant.
4. **Position assignment:** a quién sirve el agente (qué position/puesto es el `humano_responsable` para HITL y escalamiento).

#### 3.2 Quién puede crearlo
Owner/Admin del tenant (TIER 1 #15, #16). En E1, dada la enmienda E-4 de roles, corresponde definir si Operator puede proponer agentes desde Workspace; esto está pendiente.

#### 3.3 Qué necesita para crearse
- Tenant con canales configurados (Gmail/IMAP/WhatsApp).
- Skills disponibles (system o custom).
- Positions definidas en el tenant para asignar `humano_responsable`.

---

### DIMENSIÓN 4 — USO DIARIO

#### 4.1 Cómo se usa en el día a día
María abre la Mesa o el Workspace y escribe `@cotizador [su pedido]`. El agente ejecuta su cadena lineal de skills y devuelve un draft o decisión. Si requiere HITL, aparece en Zona 2 de la Mesa.

#### 4.2 Cómo se invoca
- `@mención` desde el composer de Workspace o Mesa.
- Automáticamente cuando un inbound llega por un canal asignado (`mailbox.default_agent_id`, `whatsapp.default_agent_id`).
- Desde una rutina (SPEC_FB_ROUTINES_v1 está en STUB).

#### 4.3 Qué ve el usuario mientras ocurre
- Spinner "@cotizador está trabajando".
- Badge de confianza HIGH/LOW.
- Si es draft: card en Zona 2 listo para revisar.
- Si es acción interna (tag, resumen): resultado directo en la interfaz.

---

### DIMENSIÓN 5 — EDICIÓN

#### 5.1 Cómo se edita
Desde Agent Factory (web) o, para cambios por consulta, desde el panel de Workspace (toggles por tarea, no permanentes).

#### 5.2 Qué se puede cambiar y qué no
- **En agente OPEN (custom del tenant):** identidad, skills bindeados, orden, canal, position assignment, autonomy_level dentro del ceiling.
- **En agente SEALED (system):** solo configuración de deployment (position, canal, credentials, autonomy_level dentro del rango sealed). No se puede cambiar identidad ni skills base; para eso hay que forkear (E2+ en algunos planes; en E1 los system skills son inmutables).
- **Inmutables:** `tenant_id`, `origin`, `slug`, `spec_sealed_hash`.

#### 5.3 Qué pasa con lo generado previamente
Las tareas en ejecución continúan con la config previa. Las nuevas invocaciones usan la config actualizada. La memoria episódica conserva el historial.

---

### DIMENSIÓN 6 — MOVIMIENTO Y ESTADO

#### 6.1 State machine
```
shadow -- trigger: creado/configurado, actor: Owner/Admin --> shadow
shadow -- trigger: activado/promovido tras prueba, actor: Owner/Admin --> running
running -- trigger: pause manual o condición de seguridad, actor: Owner/Admin --> paused
paused -- trigger: resume manual, actor: Owner/Admin --> running
running -- trigger: error crítico (3 fallos seguidos, data leak, violación P3) --> error
error -- trigger: resuelto por Owner/Admin --> paused --> running
```

#### 6.2 Qué dispara el movimiento
- Creación en shadow.
- Activación manual o promoción desde SANDBOX (Zona 3).
- Pause/resume manual o por superación de umbrales de riesgo.
- Error crítico automático.

#### 6.3 Quién puede moverlo
Owner/Admin. Promoción de autonomía (L0→L1→...) requiere Owner/Admin y evidencia de métricas (P4).

#### 6.4 Qué se notifica y a quién
- Activación/pausa: evento `agent.config.updated` a usuarios del tenant.
- Error: alerta a Owner/Admin + badge en panel de agentes.
- Promoción de autonomía: notificación a Owner/Admin y, en E3+, al Curator.

**Contradicción con KB:** SCH_FB_FUNCTIONAL_SPEC_v1 lista estados de agente como `shadow / running / paused / error`, pero SPEC_FABERLOOM_AGENT_COMPOSITION_v1 incluye también `archived`. Se requiere alinear.

---

### DIMENSIÓN 7 — OUTPUT

#### 7.1 Qué produce para el usuario
- Drafts listos para HITL (Zona 2).
- Decisiones/tags/resúmenes internos.
- Respuestas directas en Workspace.

#### 7.2 Qué produce para el sistema
- `task` en DB.
- `draft` si genera output cliente-facing.
- Eventos: `agent.iterate.started`, `agent.config.updated`, `agent.alarma`.
- Registros en `agent_runs` / episodic memory.

#### 7.3 Dónde aparece el output
- Mesa Zona 1/2/3 según estado.
- Workspace chat.
- Historial del agente.

#### 7.4 Qué formato tiene
- Draft como card + panel con evidence bundle.
- Decisiones internas como JSON validado contra schema del skill.

---

### DIMENSIÓN 8 — ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
| Tipo de fallo | Qué ve el usuario | Qué hace el sistema |
|---|---|---|
| Agente en `error` | Badge rojo, no responde a `@` | Bloquea invocaciones, notifica Owner/Admin |
| Skill dentro del agente falla | "@cotizador no pudo completar el paso X" | `task.status=skill_failed`, agente sigue disponible para otras tareas (TIER 1 #16.14) |
| Autonomía superada | "Esta acción requiere aprobación" | Redirige a HITL |
| Canal caído | "No se pudo enviar/recibir por [canal]" | Reintenta 3×; si persiste, escala |
| @mención a agente PAUSED/DEPRECATED | "@X está pausado/deprecado" | No ejecuta |

#### 8.2 Cómo se recupera
- Revisar logs en Agent Factory.
- Reconfigurar skill roto o rebajar autonomía.
- Reanudar desde estado paused/error.
- Si es error de canal, revalidar credenciales.

#### 8.3 Quién se entera
- Owner/Admin: errores críticos y cambios de estado.
- Operator: si una tarea suya falla.
- Observability: Langfuse + Grafana.

---

### DIMENSIÓN 9 — APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Aprobaciones, ediciones, rechazos y tiempos de decisión del `humano_responsable`.
- Efectividad por skill binding y orden.
- Patrones de uso de `@mención`.

#### 9.2 Cómo mejora con el tiempo
- Subida de autonomía L0→L1→L2→L3→L4 cuando se cumplen métricas y Owner/Admin aprueba.
- Memoria persistente se alimenta con gold samples aprobados.
- Si cambia el modelo o la policy, ModelFingerprint baja un nivel y obliga a revalidar (P13).

#### 9.3 Qué feedback da el usuario
- Implícito: usar/aprobar/editar/rechazar outputs.
- Explícito: razón de rechazo/edición; "Guardar como gold sample".

---

### DIMENSIÓN 10 — ELIMINACIÓN

#### 10.1 Cómo se elimina
No se borra. Se **pausa** o **depreca** (estado `paused`/`archived`). En E1 se usa principalmente pausa. La eliminación definitiva es deprecación/archivado.

#### 10.2 Qué pasa con lo que dependía
- `@mención` al agente pausado no funciona.
- Tareas en curso terminan con la config previa.
- Agentes que escuchaban el mismo canal pueden quedar sin handler.

#### 10.3 Es reversible
Pausa sí es reversible (`paused → running`). Deprecación/archivado no.

---

### DIMENSIÓN 11 — RELACIONES

#### 11.1 Con qué se relaciona
- **Depende de:** skills, canales del tenant, positions, Voice Profile, memoria Letta.
- **Alimenta a:** tasks, drafts, Mesa, Workspace, rutinas, outbox events.
- **Rompes si falla:** todo workflow cliente-facing; la Mesa no tendría quien procese items.

#### 11.2 En qué orden
```
Tenant → Skills → Agent Factory → Agente en shadow → prueba/SANDBOX → running → @mención o trigger → task → draft HITL → envío
```

#### 11.3 Qué rompe si este módulo falla
- No hay quien ejecute skills.
- Inbound no se rutea.
- Workspace y Mesa no producen outputs accionables.

---

### DIMENSIÓN 12 — COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
- Owner/Admin: todos los agentes del tenant.
- Operator: los agentes asignados a su position o tenant-wide.
- Viewer: solo lectura si se configura.
- Aislamiento por tenant; RLS en todas las queries.

#### 12.2 Qué queda en el audit trail
`tenant_id`, `user_id`, `actor_role_at_decision`, `action` (create/update/pause/resume/promote_autonomy/error), `resource_id` (agent_id), `data_class`, `model_provider`, `model_id`, `human_gate_required`, `human_approver_id`, `timestamp`, `sha_chain`.

#### 12.3 Qué restricciones de datos aplican
- Agente bound a `tenant_id`; todas sus queries pasan por RLS.
- Memoria aislada en namespace Letta `mem:agent:{agent_id}:*`.
- N3/N4 solo con DPA; P3 impide envío externo autónomo aunque el agente esté en L4.

---

### DIMENSIÓN 13 — DESKTOP vs WEB

#### 13.1 En cuál superficie vive
- **Web (Next.js):** Agent Factory (crear, editar, asignar skills/canales/positions, ver métricas).
- **Desktop (Electron):** invocación vía `@mención` en Workspace/Mesa, visualización de resultados, toggles de disponibilidad por consulta.

#### 13.2 Diferencias entre desktop y web
- Web: arquitectura y gobernanza del agente.
- Desktop: uso operativo, HITL, @mención, resultado en Mesa.

#### 13.3 Offline y sincronización
Agente no funciona offline. Si se pierde conexión durante una interacción, el working memory se puede perder; al reconectar se sincroniza el estado de las tareas desde el servidor.

---

## Preguntas específicas del módulo Agente

### Las 4 categorías: Canal / Recurso / Cognitivo / Proceso
Existen exactamente estas cuatro porque modelan todo recurso operable sin fragmentar ni omitir:

| Categoría | Qué hace | Ejemplo | Por qué está |
|---|---|---|---|
| **Canal** | Recibe/envía y responde sobre su canal | `@mail_ventas`, `@wa_+506_8888` | Todo inbound/outbound pasa por un canal |
| **Recurso** | Consultable como base de datos viva | `@kb_marluvas`, `@sap_marluvas` | Skills necesitan contexto de sistemas/documentos |
| **Cognitivo** | LLM-intensivo, produce outputs | `@cotizador` | Donde vive el juicio y la generación de drafts |
| **Proceso** | Cron / reactivo / housekeeping | `@seguidor_rfq`, `@stock_refresh` | Automatizaciones que no requieren input manual |

No se necesitan más porque cualquier objeto operativo encaja en una de estas; menos omitiría canales, recursos o automatizaciones.

### Autonomy ladder L0-L4
- **L0 Shadow:** observa, no emite output visible. Estado inicial obligatorio.
- **L1 Propone:** siempre genera draft y espera aprobación.
- **L2 Ejecuta interno:** acciones internas de bajo impacto (etiquetas, resúmenes) sin aprobación.
- **L3 Auto + notif:** acciones internas reversibles probadas, notifica post-hecho.
- **L4 Auto + excepciones:** flujos internos muy estrechos y probados; CEO/Owner ve excepciones.

**Cómo sube:** con evidencia — ejecuciones mínimas, approval rate ≥80%, edit-light ≥60%, rejection ≤10%, 14 días estables (P4). En E1 la aprobación la da Owner/Admin; el rol Curator entra en E3+.

**Si baja:** cambio de `ModelFingerprint` (provider, modelo, system prompt, tools, policy, retrieval) dispara probation: baja un nivel y debe revalidar antes de restaurar (P13).

### Memoria (Letta)
- **Episodic:** log de cada interacción (input, output, actor, decisiones). Usada para auditoría y replay.
- **Working:** contexto de la sesión activa (intención, archivos adjuntos, resultados intermedios). Se descarta al cerrar/cancelar la tarea.
- **Persistent:** gold samples, patrones aprobados, ajustes de voz. Solo se escribe tras gate humano (P5).

**Quién puede ver la memoria:** Owner/Admin tienen visibilidad completa; Operator solo la memoria de los agentes asignados a su position. Nunca cross-tenant.

[PENDIENTE — SPEC_FB_WORKSPACE_v1 está en STUB: política exacta de persistencia del working memory si el usuario cierra Workspace sin completar la tarea.]

---

## PENDIENTES que requieren decisión CEO

1. **Roles en E1:** PLB enmienda E-4 dice 2 roles (Owner/Operator), pero TIER 1 #16.10 y Agent Factory/Skill Factory siguen refiriendo Owner/Admin para promote. ¿Quién puede crear/promover skills y agentes en E1?
2. **Estados de skill:** ¿se usan los estados canónicos `SHADOW / ACTIVE / PAUSED / DEPRECATED` o el schema `draft / active / deprecated` de PLB? ¿Se agrega `paused` al schema?
3. **Estados de agente:** ¿se incluye `archived` en E1 o solo `shadow / running / paused / error`?
4. **Ubicación del toggle on/off de agentes:** ¿en panel lateral de Mesa (SCH_FB_FUNCTIONAL_SPEC_v1) o en hero de Workspace (SPEC_FB_FOUNDATION_BETA_TIER1_CONSTRAINTS_v1.2)?
5. **Campos editables de un skill ACTIVE:** ¿edición directa sobre ACTIVE genera nueva versión inmediata o pasa a SHADOW? ¿Qué campos son editables en ACTIVE vs SHADOW?
6. **Curator/Learning thermometer:** ¿hay un rol Curator en E1 o toda promoción de aprendizaje la hace Owner? ¿Cuáles son los thresholds exactos del termómetro para skills?
7. **Agente SEALED vs OPEN en E1:** ¿los agentes system son editables/configurables por el tenant? ¿Aplica el fork a OPEN en E1?
8. **Position assignment:** ¿el tenant ya tiene positions definidas al crear el primer agente o el wizard crea la position en el paso 4?
9. **Workspace y Rutinas:** SPEC_FB_WORKSPACE_v1 y SPEC_FB_ROUTINES_v1 están en STUB; se requiere CEO validar flujos de invocación y automatización antes de cerrar S6.

---

## CONTRADICCIONES DETECTADAS con la KB

1. **Roles E1:** PLB enmienda E-4 establece 2 roles activos en E1 (Owner/Operator), pero SPEC_FB_AUTH_TENANT_RBAC_v1 define 4 roles (AM/CURATOR/AUDITOR/CEO), SCH_FB_FUNCTIONAL_SPEC_v1 lista 5 roles (Owner/Admin/Operator/Supervisor/Viewer), y TIER 1 #16.10 y S6 hablan de Owner/Admin para promote.
2. **Skill states vs schema:** SCH_FB_FUNCTIONAL_SPEC_v1 define estados canónicos de skill `SHADOW / ACTIVE / PAUSED / DEPRECATED`; PLB_FB_FOUNDATION_BETA_v1 §2.3 schema `skills.status` solo admite `('draft','active','deprecated')` sin `paused` ni `shadow`.
3. **Agent states:** SCH_FB_FUNCTIONAL_SPEC_v1 define estados de agente `shadow / running / paused / error`; SPEC_FABERLOOM_AGENT_COMPOSITION_v1 agrega `archived` al enum `agent_status`.
4. **Toggle de agentes:** SCH_FB_FUNCTIONAL_SPEC_v1 y TIER1 CONSTRAINTS v1.1 ubican switches on/off de agentes en panel lateral de Mesa; TIER1 CONSTRAINTS v1.2 (actualizado 2026-05-02) los mueve al hero de Workspace.
5. **Autonomy ceiling vs ladder:** SCH_FB_FUNCTIONAL_SPEC_v1 enumera `autonomy ceiling` como `PROPONE / EJECUTA_INTERNO / AUTO_NOTIFICA / AUTO_EXCEPCIONES` (4 niveles), mientras que `autonomy ladder` es L0-L4 (5 niveles). No hay mapeo explícito en los docs leídos.
6. **Workspace/Routines stub:** el prompt asume capacidades del Workspace (3 modos) y Rutinas que aún no están documentadas; los docs correspondientes están en STUB.
7. **Skill Factory vs schema:** TIER 1 #16.9 exige sandbox obligatorio antes de promote, pero PLB schema `skills.status` no tiene un estado `shadow`/`sandbox` explícito; solo `last_sandbox_test_at` indica cumplimiento.

---

*Fin de la ficha funcional del Módulo 4 — Skill + Agente.*
