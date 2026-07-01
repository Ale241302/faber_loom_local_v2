# SPEC_FB_FUNC_M13_DRAFT_HITL_v1 -- Ficha Funcional Draft y Ciclo de Aprobacion HITL
id: SPEC_FB_FUNC_M13_DRAFT_HITL_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1.md - SPEC_FB_FUNC_M14_OUTCOME_LEDGER_v1.md - SPEC_FB_FUNC_M09_RBAC_v1.md - SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1.md - SCH_FB_TASK_ENTITY.md

---

## CABECERA DE FICHA

MODULO: Draft y ciclo de aprobacion HITL (por output)
SUPERFICIE: Desktop (Electron) -- WorkLoom Zona 2 / Web (vista y aprobacion simple)
SPRINT E1: S1B (drafts + ciclo HITL)
ROLES QUE LO USAN: Operator, Supervisor, Admin, Owner (aprueban); Viewer (solo historial)
DATA CLASS TIPICA: N2

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
Maria (Operator) recibe 15-20 drafts por dia de @cotizador. Sin este modulo el
agente no puede enviar nada al cliente -- el workflow se detiene. Con el, Maria
revisa y aprueba en 1-2 minutos lo que el agente preparo, con todo el contexto a
la vista.

### 1.2 A quien le duele
Operator: aprueba ~90% de los drafts diarios. Supervisor (E3+): vigila que
cumplan politica de precios. Owner/Admin: responden por lo que sale al cliente.

### 1.3 Cuando aparece
Cuando un agente cognitivo genera output con requires_human_gate=true. El item
aparece en Zona 2 de la Mesa automaticamente via WebSocket (M15).

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Revisar y aprobar (o editar/rechazar) cada output antes de que salga al cliente,
con aprobacion por output, no por task.

### 2.2 Que valor entrega
Reduce de 8-15 min a 1-2 min el ciclo de revision de un RFQ rutinario; el operador
no busca contexto -- el evidence bundle esta en el panel; garantiza que nada sale
sin gate humano.

### 2.3 Que pasa si no existe
El agente no puede enviar nada; los drafts se acumulan sin salida; el workflow se
detiene completamente.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
N/A -- no se crea manualmente. Aparece automaticamente cuando un agente genera
output con requires_human_gate=true. El sistema arma en paralelo el evidence
bundle (SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1: per-line + per-quote, 18 campos
canonicos = 10 grupos per-line + 10 per-quote) y lo adjunta al draft.

### 3.2 Quien puede crearlo
El agente (system). La aprobacion la ejecuta Operator/Supervisor/Admin/Owner
segun M09; Viewer no aprueba.

### 3.3 Que necesita para crearse
Una task previa, un agente que genero el output, el evidence bundle, y el Voice
Profile del tenant (tono). Aprobacion por output: un task con N outputs genera N
drafts independientes.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
1. Maria abre WorkLoom Zona 2. 2. Ve card con cliente, tipo, confidence HIGH/LOW,
SLA restante. 3. Click en la card. 4. Ve draft completo + evidence bundle (vista
interna). 5. Decide: Aprobar / Editar+Aprobar / Rechazar. 6. Si edita: inline +
dropdown razon del cambio. 7. Al aprobar: el sistema envia y registra audit.

### 4.2 Como se invoca
Automatico -- aparece en Zona 2 cuando el agente termina el draft; badge en
sidebar con contador; Telegram si es urgente (Zona 1).

### 4.3 Que ve el usuario mientras ocurre
Inicial: card "Listo para revisar" en Zona 2. Al click: panel draft + evidence. Al
aprobar: animacion check, la card desaparece. Al editar: modo inline con diff en
tiempo real. Al rechazar: modal razon + card a historial.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
El operador edita inline en el panel de revision. Editable: el texto del draft.
No editable: el evidence bundle (inmutable) y la metadata del caso.

### 5.2 Que se puede cambiar y que no
Editable: cualquier texto del draft. No editable: precio si esta bajo el threshold
de margen del tenant; los datos del evidence bundle; los campos del caso.

### 5.3 Que pasa con lo generado previamente
El draft original se preserva en audit. El draft editado es el que se envia. El
diff (original vs editado) va al Outcome Ledger (M14) como senal de aprendizaje.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine del draft:
```
pending -- trigger: agente comienza a generar, actor: system --> pending
pending -- trigger: agente termina draft, actor: system --> awaiting_approval
awaiting_approval -- trigger: aprobacion, actor: Operator --> approved
awaiting_approval -- trigger: edicion+aprobacion, actor: Operator --> edited
awaiting_approval -- trigger: rechazo, actor: Operator --> rejected
approved/edited -- trigger: sistema envia --> sent
awaiting_approval -- trigger: SLA/timeout vence --> expired
awaiting_approval -- trigger: cancelacion en vuelo, actor: Operator/Owner --> rejected
```

### 6.2 Que dispara el movimiento
Fin de generacion del agente; decision humana (aprobar/editar/rechazar/cancelar);
vencimiento de SLA/timeout; envio por el sistema.

### 6.3 Quien puede moverlo
Operator/Supervisor/Admin/Owner: aprobar/editar/rechazar/cancelar. system: pending
-> awaiting_approval, envio, expiracion. Viewer: no mueve (solo lee).

### 6.4 Que se notifica y a quien
Al aprobar: silencioso (flujo normal). Al rechazar: toast al Operator + log. Al
expirar: badge Zona 1 + Telegram al Operator. Oscillation Counter disparado (ver
9): aviso al Supervisor/Owner de ciclo de revision obligatorio.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Draft enviado al cliente por el canal configurado del tenant. Confirmacion:
"Enviado a [cliente] por [canal]".

### 7.2 Que produce para el sistema
Eventos: `draft.generated`, `draft.approved` o (implicito) edicion, `draft.sent`.
Registro en Outcome Ledger (M14): decision + diff + timestamp + actor_role.
Candidate gold sample si aprobado sin edicion y confidence HIGH (M14). Audit D10.

### 7.3 Donde aparece el output
La card desaparece de Zona 2; aparece en Historial; el cliente recibe el mensaje
por WhatsApp/Gmail.

### 7.4 Que formato tiene
Texto del draft + referencia al evidence_bundle_id; eventos canonicos (M15);
mensaje saliente en el canal.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Fallo de envio: el draft queda en approved_pending_send, badge error en Zona 1,
reintento auto 3x con backoff; si persiste, alerta Telegram al Owner. Fallo de
permisos: "no tenes permiso para aprobar drafts de esta cuenta", la card sigue en
Zona 2 para otro aprobador. Timeout de draft: el draft vive un tiempo configurable
sin accion; al vencer pasa a `expired` (no se auto-envia jamas). Cancelacion en
vuelo: si el agente aun genera, se aborta; si ya esta en awaiting_approval, pasa a
rejected con razon `cancelled`.

### 8.2 Como se recupera
Reintentos de envio con backoff; otro aprobador toma la card; re-generacion del
draft desde la task si fue rechazado por contenido; el operador puede solicitar
re-draft al agente.

### 8.3 Quien se entera
Operator: errores de su revision/envio. Owner: fallos de envio persistentes,
oscillation alerts. Langfuse/Grafana: tasa de aprobacion/edicion/rechazo. Nivel:
P1 fallo de envio recurrente; P2 expiraciones normales.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Aprobacion sin edicion + confidence HIGH: candidate gold sample. Edicion antes de
aprobar: diff al Outcome Ledger. Rechazo: razon del dropdown para ajustar el
skill. Tiempo de decision: alimenta el UserControlProfile (complacency_score).

### 9.2 Como mejora con el tiempo
Oscillation Counter: N aprobaciones consecutivas sin edicion dispara un ciclo de
revision obligatorio (anti-complacencia: evita que el humano apruebe en piloto
automatico). Tras el ciclo, el contador se reinicia. Las senales alimentan el
Learning Thermometer (M14).

### 9.3 Que feedback da el usuario
Implicito: aprobar/editar/rechazar. Explicito: dropdown de razon al editar/
rechazar (tone/data/structure/policy/scope/context). El ciclo de revision
obligatorio fuerza atencion explicita cada N aprobaciones.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
N/A -- los drafts no se eliminan. Se rechazan (rejected) o vencen (expired); ambos
quedan en audit permanentemente.

### 10.2 Que pasa con lo que dependia
Un draft rechazado/expirado no envia nada; la task asociada puede re-generar otro
draft o cerrarse segun el caso.

### 10.3 Es reversible
Un rechazo no se "revierte" (se genera un draft nuevo). Un envio no se deshace
(es accion externa al cliente); una correccion posterior es un mensaje nuevo.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: task (debe existir), agente (genero el draft), evidence bundle
(contextualiza), Voice Profile (tono), M09 (quien aprueba). Alimenta a: Outcome
Ledger (M14), gold sample pipeline (M14), canal de salida, M15 (eventos), M12
(audit). Alternativo: N/A -- HITL es obligatorio.

### 11.2 En que orden
inbound -> task -> skill execution -> draft -> aprobacion HITL -> envio. El diff
de edicion fluye a M14.

### 11.3 Que rompe si este modulo falla
Sin HITL, ningun output puede salir (o saldria sin control); el aprendizaje por
edicion/aprobacion se pierde; Zona 2 se vuelve inutil.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Operator: sus propios drafts. Supervisor: drafts de su equipo. Admin/Owner: todos
los del tenant. Viewer: solo historial, no aprueba. El cliente nunca ve el bundle
completo (solo la vista cliente del evidence bundle). Nunca cross-tenant.

### 12.2 Que queda en el audit trail D10
tenant_id, case_id, draft_id, actor_role_at_decision (ej. Operator), action
(approved/edited/rejected), diff_hash si hubo edicion, channel_sent, timestamp,
sha_chain_prev/curr, human_gate_required=true, human_approver_id.

### 12.3 Que restricciones de datos aplican
Evidence bundle inmutable y con 3 vistas (cliente/interno/audit); el cliente solo
ve la vista filtrada; precio no editable bajo el threshold de margen; data class
N2 tipica; envio solo por canal configurado del tenant; aprobacion HITL
obligatoria (no hay auto-send sin gate en E1).

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Desktop (Electron): superficie primaria para Operator/Supervisor (Zona 2). Web:
accesible para Owner/Admin, uso secundario. Telegram: notificacion binaria que
lleva al desktop para la decision compleja.

### 13.2 Diferencias entre desktop y web
Desktop: edicion inline, diff en tiempo real, atajos de teclado. Web: solo vista y
aprobacion simple, sin edicion inline en E1.

### 13.3 Offline y sincronizacion
No funciona offline -- requiere conexion para validar permisos y enviar por canal.
Si se pierde conexion durante la edicion, el draft se guarda localmente y se
sincroniza al reconectar. No se permiten aprobaciones offline en S1A (M19).

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE] Definir el valor de N del Oscillation Counter (cuantas aprobaciones
   sin edicion disparan el ciclo de revision obligatorio).
2. [PENDIENTE] Definir el timeout/vida del draft sin accion antes de `expired`.
3. [PENDIENTE -- SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1] El bundle declara "18 campos
   canonicos" pero lista 10 grupos per-line + 10 per-quote; confirmar el conteo
   exacto de campos vs grupos para drafts no-cotizacion (ej. follow-up).

## CONTRADICCIONES DETECTADAS CON LA KB

1. Evidence bundle generico vs de cotizacion: SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1 esta
   especificado para outputs de cotizacion. Para drafts no-cotizacion (follow-up,
   consulta) no hay un schema de bundle definido. Se asume el mismo schema reducido;
   requiere confirmacion CEO.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones del ciclo HITL.
  Estados pending/awaiting_approval/approved/edited/rejected/sent/expired;
  aprobacion por output; evidence bundle; Oscillation Counter; diff a M14.
