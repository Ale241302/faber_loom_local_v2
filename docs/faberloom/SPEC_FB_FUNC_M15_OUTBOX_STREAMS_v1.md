# SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1 -- Ficha Funcional Outbox Transaccional y Redis Streams
id: SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_EVENTING_AND_OUTBOX_v1.md - SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1.md - SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1.md - SPEC_FB_FRONTEND_REALTIME_STATE_v1.md

---

## CABECERA DE FICHA

MODULO: Outbox transaccional y Redis Streams (eventing)
SUPERFICIE: Backend (transversal) / Desktop+Web (consumo WebSocket)
SPRINT E1: S1B (outbox + streams + WebSocket fanout)
ROLES QUE LO USAN: Tecnico (infra); todos los roles consumen eventos en su UI
DATA CLASS TIPICA: N1-N2 (payload de evento referencia datos del caso)

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
La UI (Mesa de Control) debe reflejar en tiempo real lo que pasa en el backend
(un draft nuevo, una task creada). Si el evento se publica por separado del cambio
de datos, un crash entre ambos deja la UI desincronizada o pierde el evento. El
patron outbox garantiza que el evento se escribe en la misma transaccion que el
dato: o pasan los dos, o ninguno.

### 1.2 A quien le duele
Operator: si un draft no aparece en Zona 2, no lo aprueba (parece que el sistema
no hizo nada). Owner: inconsistencias entre lo que pasa y lo que ve. Tecnico:
responde por la consistencia eventual del sistema.

### 1.3 Cuando aparece
En cada cambio de estado relevante: recepcion de inbound, creacion de task,
generacion/aprobacion/envio de draft.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Entregar eventos de dominio de forma confiable (exactly-once efectivo) desde el
backend a las UIs, con reconexion robusta y aislamiento por tenant.

### 2.2 Que valor entrega
UI consistente y en vivo; cero eventos perdidos por crash (outbox); reconexion sin
perder estado (last_event_id); aislamiento estricto (tenant A no recibe eventos de
B).

### 2.3 Que pasa si no existe
La UI se desincroniza; los drafts no aparecen; los crashes pierden eventos; se
necesita refrescar a mano constantemente.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
Patron outbox: 1. En la misma transaccion que cambia el dato, se inserta el evento
en una tabla `outbox`. 2. Un relay lee el outbox y publica a Redis Streams. 3. Un
WebSocket fanout entrega a las UIs suscritas del tenant. Eventos canonicos en E1:
feed.item.received, feed.item.dispatched, task.created, draft.generated,
draft.approved, draft.sent.

### 3.2 Quien puede crearlo
El sistema (transacciones de negocio escriben al outbox). No es accion de usuario.

### 3.3 Que necesita para crearse
Transaccion de negocio (cambio + insert outbox atomicos); relay corriendo; Redis
Streams disponible; canal WebSocket por tenant.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
Transparente: el Operator ve cards aparecer/cambiar en vivo. El relay publica
continuamente; las UIs consumen el stream de su tenant.

### 4.2 Como se invoca
Automatico: cada cambio de negocio emite su evento. La UI se suscribe al WebSocket
al abrir y pasa su last_event_id.

### 4.3 Que ve el usuario mientras ocurre
Cards que aparecen/se actualizan sin refrescar; badge "Sincronizando" durante la
reconexion (M19); transicion suave al estado actual al reconectar.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
Los eventos no se editan (son hechos). Lo configurable: la retencion del stream
(<=24h), el set de eventos canonicos (cambios via SPEC_FB_EVENTING_AND_OUTBOX).

### 5.2 Que se puede cambiar y que no
Editable: retencion, suscripciones, mapeo evento->UI. No editable: un evento ya
emitido (inmutable); su event_id y orden.

### 5.3 Que pasa con lo generado previamente
Eventos pasados quedan en el stream hasta su TTL (24h) y luego se descartan; el
estado durable vive en Postgres (no en el stream). La UI reconstruye estado desde
DB + eventos recientes.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
Ciclo de vida de un evento:
```
created_in_outbox -- trigger: commit de la transaccion, actor: system --> pending_relay
pending_relay -- trigger: relay publica, actor: system --> in_stream
in_stream -- trigger: WebSocket fanout entrega, actor: system --> delivered
in_stream -- trigger: TTL 24h vence, actor: system --> expired
pending_relay -- trigger: crash del relay --> recovered (relee outbox no publicado)
```

### 6.2 Que dispara el movimiento
Commit de la transaccion; publicacion del relay; entrega WebSocket; vencimiento de
TTL; recuperacion tras crash.

### 6.3 Quien puede moverlo
Solo el sistema. Ningun usuario manipula eventos.

### 6.4 Que se notifica y a quien
Lag del relay o backlog del outbox: alerta tecnica (P1). Gap de cliente > 24h:
la UI solicita re-fetch full (M19). Crash con eventos no publicados: el relay
recupera desde el outbox al reiniciar.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
UI en tiempo real: cards que aparecen y cambian de estado sin refrescar.

### 7.2 Que produce para el sistema
Fila en `outbox` (misma transaccion que el dato); entrada en Redis Streams con
event_id; entrega WebSocket por tenant; eventos canonicos consumidos por M13/M14/
WorkLoom; insumo para M12 (audit) y M19 (reconexion).

### 7.3 Donde aparece el output
Streams de Redis (efimero <=24h); WebSocket del tenant; UIs (desktop/web); estado
durable en Postgres.

### 7.4 Que formato tiene
Evento JSON canonico (event_id, tenant_id, type, payload, timestamp) segun
SPEC_FB_EVENTING_AND_OUTBOX; stream key con prefijo de tenant.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Crash del worker entre el cambio y la publicacion: el evento ya esta en el outbox
(misma transaccion), el relay lo publica al reiniciar -> no se pierde. Eventos
perdidos en crash del worker: se recuperan releyendo el outbox no publicado.
Cliente desconectado > 24h (gap mayor que la retencion): el servidor responde
sync_required y la UI hace re-fetch full del estado (M19). Redis caido: el outbox
acumula; al recuperar, el relay drena el backlog en orden.

### 8.2 Como se recupera
Reconexion con last_event_id (entrega lo perdido <=24h); re-fetch full si gap
>24h; el relay reprocesa el outbox idempotentemente (event_id evita duplicados).

### 8.3 Quien se entera
Operator/Owner: badge "Sincronizando" durante reconexion. Tecnico: lag de relay,
backlog de outbox, Redis down (P1). Langfuse/Grafana: metricas de entrega y lag.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Lag tipico del relay; frecuencia de reconexiones y gaps; volumen de eventos por
tenant/hora.

### 9.2 Como mejora con el tiempo
Ajuste de retencion y particionado del stream; tuning del relay; alertas
proactivas de backlog. El contenido de eventos no se "aprende" (son hechos).

### 9.3 Que feedback da el usuario
N/A directo (infra). Indirecto: reportes de "no me aparecio el draft" -> revision
de entrega/reconexion.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
Los eventos del stream expiran por TTL (24h); no se borran manualmente. El outbox
se purga de filas ya publicadas y confirmadas. El estado durable persiste en DB.

### 10.2 Que pasa con lo que dependia
Tras el TTL, la reconstruccion de estado se hace desde DB (no desde el stream).
Las UIs que necesitan historial usan endpoints de estado, no el stream.

### 10.3 Es reversible
N/A -- los eventos son inmutables y efimeros; el estado durable es la fuente de
verdad reconstruible.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Recibe de: todas las transacciones de negocio (M07-M14). Alimenta a: WorkLoom y
Workspace (UI en vivo), M19 (reconexion offline), M12 (audit puede usar outbox
para no perder escrituras). Depende de: M16 (fanout y keys scoped por tenant),
Postgres (outbox + estado durable), Redis Streams.

### 11.2 En que orden
transaccion de negocio (dato + outbox atomicos) -> relay -> Redis Stream ->
WebSocket fanout por tenant -> UI. Reconexion con last_event_id (M19).

### 11.3 Que rompe si este modulo falla
Sin eventing, la UI no se actualiza en vivo; sin outbox, los crashes pierden
eventos y la UI queda inconsistente; sin fanout por tenant, riesgo de leak de
eventos cross-tenant.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Cada UI recibe solo los eventos de su tenant (fanout por tenant_id). Ningun tenant
recibe eventos de otro. Dentro del tenant, la UI filtra por rol (M09).

### 12.2 Que queda en el audit trail D10
El eventing no reemplaza el audit: las acciones auditables escriben su entrada D10
(M12), idealmente via el mismo patron outbox para no perderlas. El stream en si es
efimero y no es el registro legal.

### 12.3 Que restricciones de datos aplican
WebSocket fanout estricto por tenant_id (tenant A no recibe eventos de B); keys de
stream con prefijo tenant:{tenant_id}: (M16); payload de evento referencia datos
por id, evitando exponer N3/N4 en claro; retencion <=24h.

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Backend (outbox + streams + relay). Desktop y Web consumen el WebSocket para UI en
vivo.

### 13.2 Diferencias entre desktop y web
Misma fuente de eventos; el desktop (Electron) maneja reconexion offline mas
agresivamente (M19); la web depende de la pestana abierta.

### 13.3 Offline y sincronizacion
Es el corazon de la reconexion: la UI guarda last_event_id; al reconectar pide
?since=last_event_id y recibe lo perdido (<=24h); si el gap supera 24h o el cursor
se perdio, full refresh. Detalle de cliente en M19.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE -- SPEC_FB_EVENTING_AND_OUTBOX_v1] El SCH menciona 28 eventos
   canonicos; esta ficha cubre los 6 de E1. Confirmar el set completo y cuales
   activan en E1.
2. [PENDIENTE] Definir la estrategia de idempotencia exacta del relay (dedupe por
   event_id, ventana).
3. [PENDIENTE] Confirmar la retencion exacta del outbox (purga de publicados) vs el
   TTL de 24h del stream.

## CONTRADICCIONES DETECTADAS CON LA KB

1. Numero de eventos canonicos: SCH_FB_FUNCTIONAL_SPEC referencia "28 eventos"
   (SPEC_FB_EVENTING_AND_OUTBOX Sec.3); el prompt enumera 6 para E1. No es
   contradiccion sino subconjunto; se documenta para confirmar el alcance E1.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones del Outbox + Redis
  Streams. Patron outbox transaccional, retencion <=24h, reconexion con
  last_event_id, re-fetch full si gap>24h, WebSocket fanout por tenant.
