# SPEC_FB_FUNC_M20_AUTO_UPDATE_v1 -- Ficha Funcional Auto-update Electron
id: SPEC_FB_FUNC_M20_AUTO_UPDATE_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1.md - SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1.md - SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md

---

## CABECERA DE FICHA

MODULO: Auto-update Electron
SUPERFICIE: Desktop (Electron)
SPRINT E1: S4 (desktop -- distribucion/auto-update)
ROLES QUE LO USAN: Operator/Owner (reciben updates); Tecnico (publica releases)
DATA CLASS TIPICA: N0 (artefactos de app, sin datos de tenant)

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
El desktop debe poder actualizarse sin que cada Operator descargue e instale a
mano, y sin romper el trabajo en curso. Un update mal manejado (auto-restart en
medio de una aprobacion) perderia trabajo; un artefacto sin firmar abriria un
vector de ataque. Este modulo distribuye versiones de forma segura y no disruptiva.

### 1.2 A quien le duele
Operator: no quiere reinstalar manualmente ni perder trabajo por un restart
sorpresa. Owner: quiere a su equipo en una version soportada. Tecnico: publica y
controla el rollout (canal beta para 5 tenants).

### 1.3 Cuando aparece
Cuando hay una version nueva publicada, y cuando el backend declara una
min_supported_client_version que deja obsoleta a la version instalada.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Entregar actualizaciones firmadas del desktop de forma automatica, en background y
no disruptiva, con control de canal y de version minima soportada.

### 2.2 Que valor entrega
Equipo siempre en version soportada; instalacion sin friccion; cero perdida de
trabajo por restart; seguridad por artefactos firmados; rollout controlado (beta).

### 2.3 Que pasa si no existe
Versiones fragmentadas y desactualizadas; instalaciones manuales; riesgo de
artefactos no verificados; incompatibilidades cliente-servidor sin control.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
Pipeline de release:
1. electron-builder empaqueta + electron-updater gestiona el update.
2. Artefactos firmados (code signing) por plataforma.
3. Feed HTTPS propio por plataforma y canal (stable/beta).
4. Canal beta apuntado a 5 tenants.
5. El cliente consulta el feed, descarga en background, e instala segun la regla
   no-disruptiva (ver 4/6).

### 3.2 Quien puede crearlo
El equipo tecnico publica releases al feed. El usuario no crea updates; los recibe.

### 3.3 Que necesita para crearse
Build firmado; feed HTTPS por plataforma/canal; asignacion de canal por tenant;
declaracion de min_supported_client_version en el backend.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
Transparente: el cliente chequea el feed, descarga en background. Cuando hay un
update listo, se instala al cerrar la app o cuando el usuario pulsa "Reiniciar e
instalar". Nunca auto-restart en medio de una task.

### 4.2 Como se invoca
Automatico: chequeo periodico del feed + descarga en background. Manual: boton
"Reiniciar e instalar".

### 4.3 Que ve el usuario mientras ocurre
Indicador discreto "actualizacion disponible / descargando"; al estar lista, aviso
"se instalara al cerrar" + boton "Reiniciar e instalar". Si la version quedo por
debajo de min_supported: pantalla de bloqueo con mensaje claro y boton de update.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
El usuario no edita el update. El tecnico configura canal, feed y
min_supported_client_version. El Owner puede (segun politica) optar el tenant al
canal beta.

### 5.2 Que se puede cambiar y que no
Editable (tecnico): version publicada, canal, min_supported_client_version, ritmo
de rollout. No editable (usuario): el contenido del artefacto, la firma, la regla
no-disruptiva.

### 5.3 Que pasa con lo generado previamente
Una version instalada se reemplaza por la nueva al instalar. El estado de la sesion
(M18) y los cursores (M19) se preservan; el update no borra datos locales no
secretos salvo que la migracion lo requiera.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine del update:
```
idle -- trigger: chequeo de feed encuentra version nueva, actor: system --> downloading
downloading -- trigger: descarga completa + firma valida, actor: system --> ready_to_install
ready_to_install -- trigger: usuario cierra la app, actor: usuario --> installing
ready_to_install -- trigger: usuario pulsa Reiniciar e instalar, actor: usuario --> installing
installing -- trigger: instalacion OK --> updated
downloading -- trigger: firma invalida / descarga corrupta, actor: system --> rejected
(version < min_supported_client_version) -- trigger: backend lo declara --> blocked
```

### 6.2 Que dispara el movimiento
Chequeo del feed; descarga + verificacion de firma; cierre de la app o boton del
usuario; declaracion de min_supported por el backend.

### 6.3 Quien puede moverlo
system: chequeo, descarga, verificacion, bloqueo por min_supported. usuario:
decide cuando instalar (cerrar o boton). Nunca auto-restart mid-task.

### 6.4 Que se notifica y a quien
Update listo: aviso discreto al usuario. Version bloqueada (< min_supported):
pantalla de bloqueo con mensaje seguro. Firma invalida: se descarta el update +
alerta tecnica (posible artefacto manipulado).

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Una app actualizada sin reinstalacion manual y sin perder trabajo; aviso claro
cuando debe actualizar.

### 7.2 Que produce para el sistema
Descarga verificada (firma); instalacion al cierre/boton; telemetria de version
instalada por cliente; bloqueo de clientes por debajo de min_supported.

### 7.3 Donde aparece el output
Indicador de update en la app; pantalla de bloqueo si aplica; feed/telemetria de
versiones (lado tecnico).

### 7.4 Que formato tiene
Artefacto firmado por plataforma; feed HTTPS (stable/beta); flag
min_supported_client_version en el backend.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Firma invalida/descarga corrupta: se descarta el update, se reintenta mas tarde,
alerta tecnica (posible manipulacion). Instalacion falla: se conserva la version
anterior funcionando; se reintenta. Version < min_supported: bloqueo con mensaje
seguro y boton de update; no se permite operar hasta actualizar. Update disponible
con task en curso: NO se instala hasta que el usuario cierre o lo pida; antes de
instalar se verifica: sin mutaciones pendientes, WS reconciliado (M19), drafts
guardados (M13).

### 8.2 Como se recupera
Reintento de descarga/instalacion; rollback implicito (queda la version previa si
la instalacion falla); el usuario actualiza desde la pantalla de bloqueo si quedo
por debajo de min_supported.

### 8.3 Quien se entera
Usuario: avisos de update/bloqueo. Tecnico: fallos de firma/instalacion,
distribucion por canal. Nivel: P1 si una version mala llega a stable; P2 fallos
normales de descarga.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Tasa de adopcion por version/canal; fallos de instalacion por plataforma; cuanto
tardan los tenants en actualizar.

### 9.2 Como mejora con el tiempo
Rollout gradual (beta -> stable) segun salud de la version; tuning del ritmo de
distribucion; mejor manejo de instalacion por SO.

### 9.3 Que feedback da el usuario
Implicito: cuando instala (al cierre vs boton). Explicito: reportes de fallo de
update -> revision del artefacto/feed.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
Una version se "retira" dejando de publicarla o subiendo min_supported para
forzar el upgrade. La app no se "borra" via update; se reemplaza.

### 10.2 Que pasa con lo que dependia
Subir min_supported bloquea las versiones viejas hasta que actualicen; el feed deja
de ofrecer versiones retiradas.

### 10.3 Es reversible
Se puede republicar una version previa (rollback de release) si una nueva resulta
mala. La instalacion en la maquina del usuario es reversible reinstalando la
version anterior.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: pipeline de build/sign, feed HTTPS, declaracion backend de
min_supported_client_version. Alimenta a/coordina con: M18 (preservar sesion al
actualizar), M19 (WS reconciliado antes de instalar), M13 (drafts guardados antes
de instalar).

### 11.2 En que orden
Tecnico publica release firmada -> cliente descarga en background -> verifica
firma -> (pre-instalacion: sin mutaciones pendientes + WS reconciliado + drafts
guardados) -> instala al cierre/boton -> updated. min_supported puede forzar el
flujo.

### 11.3 Que rompe si este modulo falla
Sin auto-update controlado: versiones fragmentadas, incompatibilidad cliente-
servidor, riesgo de artefactos no verificados, o perdida de trabajo por restart
mal manejado.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
El usuario ve el estado de update de su app. El tecnico ve la distribucion por
canal/version. No hay datos de tenant en el update (N0).

### 12.2 Que queda en el audit trail D10
El update de la app no es accion de negocio sobre datos del tenant; se registra
telemetria de version (sin PII). Las acciones de negocio que ocurren antes/despues
auditan normalmente (M12).

### 12.3 Que restricciones de datos aplican
Artefactos firmados (code signing) obligatorios; feed HTTPS; verificacion de firma
antes de instalar (se descarta si invalida); nunca auto-restart mid-task; pre-
instalacion exige sin mutaciones pendientes + WS reconciliado + drafts guardados;
min_supported_client_version declarada por backend bloquea clientes obsoletos.

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Desktop (Electron) exclusivamente. La web se actualiza recargando (no aplica
auto-update de artefacto).

### 13.2 Diferencias entre desktop y web
Desktop: distribucion de binarios firmados, canal, min_supported. Web: deploy
server-side, sin instalacion en cliente.

### 13.3 Offline y sincronizacion
La descarga del update requiere conexion; offline no se actualiza. Tras instalar,
el cold start re-sincroniza (M19). El update preserva cursores/sesion salvo
migracion explicita.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE] Definir el host/infra del feed HTTPS propio por plataforma y canal.
2. [PENDIENTE] Confirmar los 5 tenants del canal beta y el criterio de promocion
   beta -> stable.
3. [PENDIENTE] Definir la cadencia de chequeo del feed y la politica de forzado
   cuando min_supported sube (gracia vs bloqueo inmediato).

## CONTRADICCIONES DETECTADAS CON LA KB

1. Sin contradicciones nuevas detectadas. La regla "nunca auto-restart mid-task" y
   el pre-check (sin mutaciones pendientes + WS reconciliado + drafts guardados)
   son consistentes con M13/M19.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones de auto-update
  Electron. electron-builder/updater, artefactos firmados, feed HTTPS por
  plataforma/canal, canal beta 5 tenants, instalacion no disruptiva,
  min_supported_client_version.
