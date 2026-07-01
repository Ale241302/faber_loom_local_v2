# SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1 -- Ficha Funcional Sincronizacion Offline y Reconexion (Electron)
id: SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1.md - SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1.md - SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md - SPEC_FB_FRONTEND_REALTIME_STATE_v1.md

---

## CABECERA DE FICHA

MODULO: Sincronizacion offline y reconexion (Electron)
SUPERFICIE: Desktop (Electron)
SPRINT E1: S4 (desktop -- offline/reconexion)
ROLES QUE LO USAN: Operator (uso diario), Supervisor; Owner
DATA CLASS TIPICA: N1-N2 (estado de UI y cursores; no secretos)

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
La conectividad del Operator no siempre es estable. Si al perder y recuperar la
conexion el desktop mostrara estado viejo o permitiera aprobar offline algo que ya
cambio en el server, se enviarian cosas incorrectas. Este modulo garantiza que el
desktop reconcilie su estado antes de dejar accionar.

### 1.2 A quien le duele
Operator: trabaja en condiciones de red variable; necesita confianza de que lo que
ve esta al dia. Owner: no quiere aprobaciones sobre estado obsoleto. Tecnico:
responde por la consistencia cliente-servidor.

### 1.3 Cuando aparece
En el cold start de la app, ante cada desconexion/reconexion, y cuando el cursor
de eventos queda atras.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Reconciliar el estado del desktop con el server al (re)conectar, usando cursores
de evento, y bloquear acciones sensibles hasta que la reconciliacion termine.

### 2.2 Que valor entrega
Estado siempre confiable tras reconexion; sin aprobaciones sobre datos obsoletos;
recuperacion eficiente (delta <=24h) o full refresh cuando hace falta.

### 2.3 Que pasa si no existe
La UI muestra estado viejo; el Operator aprueba/edita sobre datos desincronizados;
se pierden o duplican acciones.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
No es entidad de UI. Es el protocolo de arranque/reconexion del desktop:
1. Persistir en electron-store (NO secretos): last_event_id, last_sync_at,
   tenant_id, client_version.
2. Cold start: mostrar "Sincronizando...", GET /auth/me, full fetch de
   WorkLoom/Workspace, abrir WS con ?since=last_event_id si last_sync_at < 24h.
3. Si gap > 24h o cursor perdido: full refresh del estado.
4. No permitir aprobaciones offline en S1A.

### 3.2 Quien puede crearlo
El sistema (cliente Electron) ejecuta el protocolo. No es accion de usuario.

### 3.3 Que necesita para crearse
Sesion desktop valida (M18); last_event_id/last_sync_at en electron-store; canal
WebSocket del tenant (M15); endpoints de full state.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
Transparente: al abrir o reconectar, el desktop sincroniza y luego habilita la
operacion. El Operator ve un badge "Sincronizando" breve y despues trabaja normal.

### 4.2 Como se invoca
Automatico: cold start de la app; evento de reconexion de red; reapertura del WS.

### 4.3 Que ve el usuario mientras ocurre
Badge "Sincronizando" hasta completar la reconciliacion; acciones sensibles
(aprobar/editar/enviar) deshabilitadas con tooltip "sincronizando..."; al
terminar, la UI se actualiza al estado actual y habilita acciones.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
El protocolo no se edita por usuario. Configurable: la ventana de delta (24h), que
se persiste en electron-store, que acciones se bloquean durante el sync.

### 5.2 Que se puede cambiar y que no
Editable: parametros de sync (ventana, timeouts). No editable: la regla de no
aprobar offline (S1A); que los secretos NO van en electron-store.

### 5.3 Que pasa con lo generado previamente
Tras un full refresh, el estado local viejo se descarta y se reemplaza por el del
server (el server es la verdad). Los cursores se actualizan a last_event_id nuevo.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine de conexion del cliente:
```
cold_start -- trigger: app abre, actor: system --> syncing
syncing -- trigger: last_sync_at < 24h, delta OK, actor: system --> online
syncing -- trigger: gap > 24h o cursor perdido, actor: system --> full_refresh
full_refresh -- trigger: estado completo cargado --> online
online -- trigger: se pierde la red, actor: system --> offline
offline -- trigger: vuelve la red, actor: system --> syncing
```

### 6.2 Que dispara el movimiento
Apertura de la app; resultado del chequeo de delta vs gap; perdida/recuperacion de
red.

### 6.3 Quien puede moverlo
Solo el sistema (cliente). El usuario no fuerza estados (puede reintentar
manualmente la reconexion).

### 6.4 Que se notifica y a quien
Badge "Sincronizando" / "Offline" al Operator. Si la reconciliacion falla
repetidamente: aviso de "sin conexion con el servidor" + acciones bloqueadas.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Estado del desktop reconciliado y confiable; badge de sincronizacion; acciones
habilitadas solo cuando el estado esta al dia.

### 7.2 Que produce para el sistema
Cursores actualizados (last_event_id, last_sync_at) en electron-store; suscripcion
WS reabierta con ?since=last_event_id; full fetch del estado cuando aplica.

### 7.3 Donde aparece el output
electron-store (cursores, no secretos); UI (badge + estado); WebSocket del tenant
(M15).

### 7.4 Que formato tiene
Cursores en electron-store (JSON no secreto); requests de full state; WS con
parametro since.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Gap > 24h (mayor que la retencion del stream, M15): full refresh. Cursor perdido/
corrupto: full refresh. Reconciliacion falla repetidamente: la UI queda en
"offline", acciones sensibles bloqueadas (no se permite aprobar offline en S1A).
Conexion intermitente durante el sync: reintentar; no marcar online hasta
completar la reconciliacion.

### 8.2 Como se recupera
Reintento automatico de reconexion; full refresh si el delta no alcanza; el
usuario puede forzar un re-sync manual. Las mutaciones pendientes (si las hubiera)
se resuelven solo al estar online (no se aplican a ciegas).

### 8.3 Quien se entera
Operator: badge offline/sincronizando. Tecnico: tasa de full refresh, fallos de
reconciliacion. Langfuse/Grafana: metricas de sync.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Frecuencia de desconexiones; cuantas veces el delta alcanza vs full refresh;
duracion tipica del sync.

### 9.2 Como mejora con el tiempo
Tuning de la ventana de delta y de los timeouts; precarga selectiva del estado mas
usado para acelerar el cold start.

### 9.3 Que feedback da el usuario
Implicito: reintentos manuales de reconexion. Explicito: reportes de "se queda
sincronizando" -> revision del protocolo.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
El protocolo no se elimina. Los cursores en electron-store se limpian en logout
(M18). El estado local se descarta en cada full refresh.

### 10.2 Que pasa con lo que dependia
Sin cursores, el siguiente arranque es un cold start con full fetch. No hay datos
huerfanos: el server es la verdad.

### 10.3 Es reversible
N/A -- es un protocolo continuo; el full refresh siempre puede reconstruir estado.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: M15 (eventos/streams + last_event_id), M18 (sesion desktop + electron-
store), endpoints de full state. Alimenta a: M13 (no aprobar offline), toda la UI
del desktop.

### 11.2 En que orden
M18 da la sesion -> M19 sincroniza al (re)conectar -> habilita la operacion (M13 y
demas). El bloqueo de acciones sensibles persiste hasta completar la reconciliacion.

### 11.3 Que rompe si este modulo falla
Sin reconciliacion, el desktop muestra estado obsoleto y permitiria acciones sobre
datos viejos; se pierde la confianza en la Mesa de Control.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
El estado pertenece al tenant/usuario de la sesion. Nunca cross-tenant: el sync
revalida el tenant_id de la sesion (M18/M16) antes de cargar estado.

### 12.2 Que queda en el audit trail D10
El sync en si no es accion auditable de negocio. Las acciones que se ejecutan tras
reconciliar (aprobar/enviar) auditan normalmente (M12). Se puede registrar
metricas de sync sin PII.

### 12.3 Que restricciones de datos aplican
Solo datos no secretos en electron-store (last_event_id, last_sync_at, tenant_id,
client_version); secretos en keychain (M18); no aprobaciones offline en S1A;
acciones bloqueadas hasta reconciliacion completa; revalidacion de tenant antes de
sincronizar.

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Desktop (Electron). La web depende de la pestana abierta y un modelo de reconexion
mas simple (M15); el protocolo de cursores persistentes es propio del desktop.

### 13.2 Diferencias entre desktop y web
Desktop: persistencia de cursores en electron-store, full refresh tras gap,
bloqueo de acciones durante sync. Web: reconexion del WS sin persistencia local
fuerte.

### 13.3 Offline y sincronizacion
Es el modulo de offline/sync por excelencia. Offline: la UI muestra el ultimo
estado conocido en modo lectura, con acciones sensibles deshabilitadas. Online: se
reconcilia con delta (<=24h) o full refresh, y se habilita la operacion.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE] Confirmar exactamente que acciones se permiten en modo lectura
   offline (ver historial, redactar borrador local sin enviar) vs cuales se
   bloquean.
2. [PENDIENTE] Definir el numero de reintentos y backoff de reconexion antes de
   marcar "sin conexion con el servidor".
3. [PENDIENTE -- M15] Confirmar que la retencion del stream (24h) y la ventana de
   delta del cliente coinciden exactamente.

## CONTRADICCIONES DETECTADAS CON LA KB

1. Sin contradicciones nuevas detectadas. La regla "no aprobaciones offline en
   S1A" y el full refresh > 24h son consistentes con M15.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones de sincronizacion
  offline/reconexion Electron. Cursores en electron-store, cold start con full
  fetch + WS since, full refresh si gap>24h, no aprobaciones offline en S1A.
