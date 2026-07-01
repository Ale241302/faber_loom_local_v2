# SCH_FB_FUNCTIONAL_SPEC_v1 -- Plantilla Canonica de Especificacion Funcional
id: SCH_FB_FUNCTIONAL_SPEC_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SCH
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SPEC_FB_AUTH_TENANT_RBAC_v1.md · ARCH_AGENT_PRINCIPLES.md · SPEC_ACTION_ENGINE.md · PLB_FB_FOUNDATION_BETA_v1.md

---

## Proposito

Plantilla para especificar funcionalmente cada modulo de FaberLoom.
Responde las preguntas que Alejandro necesita para implementar.
No es spec tecnica -- es spec funcional desde perspectiva del usuario.

COMO USAR:
1. Copiar esta plantilla
2. Renombrar como FUNC_FB_<MODULO>_v1.md
3. Responder todas las preguntas que aplican
4. Marcar las que no aplican con: N/A -- [razon]
5. Marcar las que faltan dato con: [PENDIENTE -- NO INVENTAR]
6. Indexar cuando el modulo entra en el sprint correspondiente

---

## CABECERA DE FICHA

MODULO: [nombre exacto]
SUPERFICIE: [Desktop | Web | Canal | Transversal]
SPRINT E1: [S1A | S1B | S2 | S3 | S4 | S5 | S6 | S7 | post-E1]
ROLES QUE LO USAN: [Owner | Admin | Operator | Supervisor | Viewer]
DATA CLASS TIPICA: [N0 | N1 | N2 | N3 | N4]

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
Que problema real resuelve. Quien lo siente. Cuando lo siente.
Formato: "[Persona] tiene el problema de [dolor] cuando [situacion].
Sin este modulo, [consecuencia concreta]."

### 1.2 A quien le duele
Roles especificos. Referencia a roles canonicos:
Owner / Admin / Operator / Supervisor / Viewer

### 1.3 Cuando aparece
Que evento o condicion activa la necesidad de este modulo.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Objetivo concreto. Una frase: verbo + resultado.

### 2.2 Que valor entrega
Que gana el usuario. Cuantificable si es posible.

### 2.3 Que pasa si no existe
Costo de no tenerlo. Que hace el usuario hoy sin este modulo.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
Pasos exactos numerados. Indicar superficie. Manual vs automatico.

### 3.2 Quien puede crearlo
Rol(es). Si requiere aprobacion adicional.

### 3.3 Que necesita para crearse
Dependencias previas. Datos requeridos. Si falta algo, que ve el usuario.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
Flujo normal del usuario. Frecuencia tipica.

### 4.2 Como se invoca
Navegacion directa / @mencion / automatico / notificacion / deep link.

### 4.3 Que ve el usuario mientras ocurre
Estado inicial / en proceso / completado / error.
Feedback visual: spinners, toasts, badges, progress bars.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
Pasos exactos. Campos editables. Donde vive la UI de edicion.

### 5.2 Que se puede cambiar y que no
Lista explicita. Por que los inmutables no se pueden cambiar.

### 5.3 Que pasa con lo generado previamente
Outputs ya aprobados: se conservan / se invalidan / se recalculan.
Historial: se preserva / se marca con version anterior.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine completa.
Formato: ESTADO_A -- trigger: [evento], actor: [rol] --> ESTADO_B

### 6.2 Que dispara el movimiento
Manual / automatico / mixto. Para cada transicion.

### 6.3 Quien puede moverlo
Por transicion: que rol, si requiere aprobacion.

### 6.4 Que se notifica y a quien
Canal / destinatario / contenido / urgencia.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Tipo / donde aparece / formato.

### 7.2 Que produce para el sistema
Eventos emitidos / registros en DB / cambios de estado / jobs Celery.

### 7.3 Donde aparece el output
Zona de Mesa (1/2/3/4/5) / Workspace / Canal externo / Solo interno.

### 7.4 Que formato tiene
Texto / card / archivo / evento -- con detalles.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Por tipo de fallo: tecnico / datos / permisos / compliance.
Que ve el usuario. Que hace el sistema.

### 8.2 Como se recupera
Pasos del usuario. Reintentos automaticos. Quien interviene.

### 8.3 Quien se entera
Usuario que lo invoco / Owner-Admin / Langfuse-Grafana.
Nivel: P0 / P1 / P2.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Senales generadas: aprobacion / edicion / rechazo / tiempo de decision.

### 9.2 Como mejora con el tiempo
Que cambia despues de N usos. En que capa aprende.

### 9.3 Que feedback da el usuario
Implicito (aprobar/editar/rechazar) / explicito (dropdown razon).
Cuando se pregunta. Como se procesa.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
Distinguir: desactivar / pausar / deprecar / borrar.
Mayoría de objetos en FaberLoom se DEPRECAN, no se borran.

### 10.2 Que pasa con lo que dependia
Efectos en cascada. Modulos que lo referenciaban.

### 10.3 Es reversible
Si / No y por que.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Modulos que dependen de este / que lo alimentan / alternativos.

### 11.2 En que orden
Que debe existir antes. Que viene despues. Diagrama si es complejo.

### 11.3 Que rompe si este modulo falla
Dependencias criticas. Workflows bloqueados.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Por rol. Restriccion por data_class. Nunca cross-tenant.

### 12.2 Que queda en el audit trail
Campos exactos D10: tenant_id / user_id / actor_role_at_decision /
action / resource_id / data_class / model_provider / model_id /
human_gate_required / human_approver_id / timestamp / sha_chain.

### 12.3 Que restricciones de datos aplican
Data class tipica N0-N4. Providers que pueden procesar.
Si requiere DPA. Anonymization level L0-L3.

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Desktop (Electron): uso diario trabajador administrativo.
Web (Next.js): configuracion y governance Owner/Admin.
Canal: presencia en WhatsApp/Telegram/Gmail.

### 13.2 Diferencias entre desktop y web
Features exclusivos de cada superficie. Por que esa diferencia.

### 13.3 Offline y sincronizacion
Que funciona sin conexion. Como se sincroniza al volver.
Que pasa con conflictos.

---

## REFERENCIAS CANONICAS

Roles: Owner / Admin / Operator / Supervisor / Viewer
Ref: SPEC_FB_AUTH_TENANT_RBAC_v1.md §5.2

Estados de agente: shadow / running / paused / error
Estados de skill: SHADOW / ACTIVE / PAUSED / DEPRECATED
Estados de rutina: sandbox / active / paused / failed / deprecated
Estados de draft: pending / awaiting_approval / approved / edited /
  rejected / sent / expired
Estados de task: created / running / awaiting_approval / completed /
  failed / cancelled

Eventos canonicos (28): ver SPEC_FB_EVENTING_AND_OUTBOX_v1.md §3
Data classification: N0-N4 ver POL_DATA_CLASSIFICATION.md
Autonomy ceiling: PROPONE / EJECUTA_INTERNO / AUTO_NOTIFICA / AUTO_EXCEPCIONES
Autonomy ladder: L0 Shadow / L1 Propone / L2 Ejecuta interno /
  L3 Auto+notif / L4 Auto+excep

Zonas Mesa de Control:
  Zona 1: Lo urgente
  Zona 2: Esperando tu firma (drafts HITL)
  Zona 3: SANDBOX esperando promote
  Zona 4: Inbox completo
  Zona 5: Automatizaciones activas

Inbound 13 tipos: ver ENT_FB_INBOUND_TAXONOMY_v1.md
Work-type packs: ver ENT_FB_WORK_TYPE_PACK_v1.md
Canales: WhatsApp BSP / Telegram Bot / Gmail/IMAP / Desktop

---

## EJEMPLO DE FICHA -- Aprobacion de draft HITL

MODULO: Aprobacion de draft por output
SUPERFICIE: Desktop (Electron) -- WorkLoom Zona 2
SPRINT E1: S3
ROLES QUE LO USAN: Operator, Supervisor, Admin, Owner
DATA CLASS TIPICA: N2

### D1 EXISTENCIA

1.1 Por que existe:
Maria (Operator) recibe 15-20 drafts por dia de @cotizador. Sin este
modulo el agente no puede enviar nada al cliente -- el workflow se
detiene. Con este modulo Maria revisa y aprueba en 1-2 minutos lo
que el agente preparo.

1.2 A quien le duele:
Operator: aprueba 90% de los drafts diarios.
Supervisor: supervisa que los drafts cumplan politica de precios.

1.3 Cuando aparece:
Cuando un agente Cognitivo genera output con requires_human_gate=true.
El item aparece en Zona 2 de la Mesa automaticamente via WebSocket.

### D2 PROPOSITO

2.1 Para que:
Para revisar y aprobar el draft que preparo el agente antes de que
salga al cliente.

2.2 Que valor entrega:
Reduce de 8-15 min a 1-2 min el ciclo de revision de un RFQ rutinario.
El operador no necesita buscar contexto -- todo esta en el panel.

2.3 Que pasa si no existe:
El agente no puede enviar nada. Los drafts se acumulan sin salida.
El workflow se detiene completamente.

### D3 CREACION
N/A -- no se crea manualmente. Aparece automaticamente cuando
un agente genera output con requires_human_gate=true.

### D4 USO DIARIO

4.1 Flujo normal:
1. Maria abre Mesa de Control (desktop, Zona 2)
2. Ve card con: cliente, tipo, confidence HIGH/LOW, SLA restante
3. Hace click en la card
4. Ve draft completo + evidence bundle
5. Decide: Aprobar / Editar+Aprobar / Rechazar
6. Si edita: modifica inline, dropdown razon del cambio
7. Al aprobar: sistema envia y registra audit trail

4.2 Como se invoca:
Automatico -- aparece en Zona 2 cuando agente termina el draft.
Badge en sidebar con contador de items pendientes.
Telegram si el item es urgente (Zona 1).

4.3 Que ve mientras ocurre:
Inicial: card en Zona 2 con badge "Listo para revisar"
Al hacer click: panel con draft + evidence
Al aprobar: animacion check, card desaparece
Al editar: modo inline con diff en tiempo real
Al rechazar: modal razon + card va a historial

### D5 EDICION

5.1 Como se edita:
El operador edita inline en el panel de revision.
Campos editables: texto del draft completo.
Campos no editables: evidence bundle (inmutable), metadata del caso.

5.2 Que se puede cambiar:
Editable: cualquier texto del draft.
No editable: precio si esta bajo threshold de margen del tenant.
No editable: datos del evidence bundle.

5.3 Que pasa con lo generado:
Draft original se preserva en audit trail.
Draft editado es el que se envia.
Diff (original vs editado) va al Outcome Ledger como senal de aprendizaje.

### D6 MOVIMIENTO

6.1 State machine:
pending -- trigger: agente termina draft --> awaiting_approval
awaiting_approval -- trigger: Operator aprueba, actor: Operator --> approved
awaiting_approval -- trigger: Operator edita+aprueba, actor: Operator --> edited
awaiting_approval -- trigger: Operator rechaza, actor: Operator --> rejected
approved/edited -- trigger: sistema envia --> sent
awaiting_approval -- trigger: SLA vence --> expired

6.4 Que se notifica:
Al aprobar: silencioso (flujo normal)
Al rechazar: toast al Operator, log en audit
Al expirar: badge Zona 1 + Telegram al Operator

### D7 OUTPUT

7.1 Para el usuario:
Draft enviado al cliente por canal configurado del tenant.
Confirmacion: "Enviado a [cliente] por [canal]"

7.2 Para el sistema:
Evento: draft.approved o draft.edited
Evento: draft.sent
Registro Outcome Ledger: decision + diff + timestamp + actor_role
Candidate gold sample si aprobado sin edicion y confidence HIGH

7.3 Donde aparece:
Card desaparece de Zona 2.
Aparece en historial (tab Historial de la Mesa).
Cliente recibe mensaje por WhatsApp/Gmail.

### D8 ERRORES

8.1 Que pasa si falla:
Fallo de envio: draft queda en approved_pending_send, Zona 1 badge error.
  Reintento auto 3 veces con backoff exponencial.
  Si persiste: alerta Telegram al Owner.
Fallo permisos: "No tenes permiso para aprobar drafts de esta cuenta."
  Card sigue en Zona 2 para otro Operator.

### D9 APRENDIZAJE

9.1 Que aprende:
Aprobacion sin edicion + confidence HIGH: candidate gold sample
Edicion antes de aprobar: diff capturado en Outcome Ledger
Rechazo: razon del dropdown registrada para ajuste del skill
Tiempo de decision: contribuye a UserControlProfile (complacency_score)

### D10 ELIMINACION
N/A -- los drafts no se eliminan. Se rechazan (rejected) o vencen
(expired). Ambos estados quedan en audit trail permanentemente.

### D11 RELACIONES

11.1 Con que se relaciona:
Depende de: task (debe existir), agente (que genero el draft),
  evidence bundle (que contextualiza), Voice Profile (que da el tono)
Alimenta a: Outcome Ledger, gold sample pipeline, canal de salida
Alternativo: N/A -- HITL es obligatorio, no hay alternativa

11.2 En que orden:
Inbound → task → skill execution → draft → aprobacion HITL → envio

### D12 COMPLIANCE

12.1 Quien puede verlo:
Operator: sus propios drafts
Supervisor: drafts de su equipo
Admin/Owner: todos los drafts del tenant
Viewer: solo historial, no puede aprobar

12.2 Audit trail D10:
tenant_id, case_id, draft_id, actor_role_at_decision (Operator),
action (approved/edited/rejected), diff_hash si hubo edicion,
channel_sent, timestamp, sha_chain_prev, sha_chain_curr,
human_gate_required=true, human_approver_id

### D13 DESKTOP vs WEB

13.1 Superficie:
Desktop (Electron): superficie primaria para Operator/Supervisor.
Web (Next.js): accesible para Owner/Admin pero uso secundario.
Telegram: notificacion binaria, lleva a desktop para decision compleja.

13.2 Diferencias:
Desktop: edicion inline, diff en tiempo real, atajos de teclado.
Web: solo vista y aprobacion simple, sin edicion inline en E1.

13.3 Offline:
No funciona offline -- requiere conexion para validar permisos y
enviar por canal. Si se pierde conexion durante edicion: el draft
se guarda localmente y se sincroniza al reconectar.

---

Changelog:
- v1.0 (2026-06-24): Creacion. 13 dimensiones, ~35 preguntas.
  Referencias canonicas a roles, estados, eventos, zonas, canales.
  Ejemplo de ficha completada (aprobacion de draft HITL).
  Base para fichas funcionales de los 60-70 modulos E1.