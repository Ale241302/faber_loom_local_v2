# SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1 -- Ficha Funcional Auth y Sesion Electron
id: SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_FUNC_M08_AUTH_SESSION_v1.md - SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1.md - SPEC_FB_FUNC_M19_OFFLINE_SYNC_v1.md - SPEC_FB_FUNC_M20_AUTO_UPDATE_v1.md

---

## CABECERA DE FICHA

MODULO: Auth y sesion Electron (desktop)
SUPERFICIE: Desktop (Electron)
SPRINT E1: S4 (desktop -- auth/sesion)
ROLES QUE LO USAN: Operator (uso diario), Owner; multi-tenant por particion
DATA CLASS TIPICA: N2 (sesion); tokens son secretos cifrados

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
El desktop es la superficie diaria del Operator. Si los tokens de sesion vivieran
en localStorage, un XSS podria exfiltrarlos y robar la sesion. Electron necesita un
modelo de sesion propio: particion por tenant, cookies en el main process, y
secretos en el keychain del SO. Sin esto, el desktop seria el eslabon debil de
seguridad.

### 1.2 A quien le duele
Operator: necesita login estable y seguro en el desktop. Owner: responde por la
seguridad de la operacion. Tecnico: responde por el hardening de Electron.

### 1.3 Cuando aparece
En cada login/reanudacion en el desktop, y cuando hay mas de un tenant en la misma
maquina (particiones separadas).

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Autenticar y mantener la sesion en Electron de forma segura: particion por tenant,
secretos en keychain, sin tokens en almacenamiento web.

### 2.2 Que valor entrega
Sesion desktop resistente a XSS; aislamiento entre tenants en la misma maquina;
logout que limpia de verdad (particion + keychain).

### 2.3 Que pasa si no existe
Tokens expuestos a XSS; cookies compartidas entre tenants; logout que deja
residuos; superficie de ataque amplia en el cliente.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
La sesion Electron se crea al loguear (sobre el flujo de M08):
1. session.fromPartition('persist:faberloom-{profile}') por tenant.
2. Cookies httpOnly en el main process (no en el renderer).
3. Tokens/secretos locales en keytar/safeStorage (keychain del SO).
4. electron-store solo para config NO secreta.
5. contextIsolation=true, nodeIntegration=false en el BrowserWindow.

### 3.2 Quien puede crearlo
El usuario al loguear en el desktop. La particion se crea/selecciona por tenant
elegido.

### 3.3 Que necesita para crearse
Credenciales validas (M08); 2FA si es Owner; el profile/tenant a usar; keychain
del SO disponible.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
El Operator abre la app; si la sesion de la particion sigue valida, reanuda; si
no, login. Una persona con varios tenants elige el profile (particion) al abrir.

### 4.2 Como se invoca
Apertura de la app (reanudacion); pantalla de login; selector de profile/tenant si
hay varios.

### 4.3 Que ve el usuario mientras ocurre
Inicial: splash + (si hay sesion) "Reanudando..."; si no, login. Completado: Mesa
de Control del tenant. Error: login con mensaje (credenciales/2FA/sesion expirada).

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
El usuario cambia password/2FA via web (M08); en desktop solo cambia el profile
activo o cierra sesion. La config no secreta (preferencias) se edita en
electron-store.

### 5.2 Que se puede cambiar y que no
Editable: profile activo, preferencias no secretas. No editable: el modelo de
particion, la ubicacion de los secretos (keychain), las flags de seguridad
(contextIsolation/nodeIntegration).

### 5.3 Que pasa con lo generado previamente
Cambiar de profile carga otra particion (otra sesion/tenant). Cerrar sesion limpia
la particion + el keychain de ese profile; las preferencias no secretas pueden
conservarse.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine de la sesion desktop:
```
no_session -- trigger: login OK (M08), actor: usuario --> active (particion del tenant)
active -- trigger: app reabre con sesion valida, actor: system --> active (reanudada)
active -- trigger: logout, actor: usuario --> cleared (particion + keychain limpios)
active -- trigger: revocacion remota (M08), actor: Owner/platform_admin --> invalidated
active -- trigger: cambio de profile, actor: usuario --> active (otra particion)
```

### 6.2 Que dispara el movimiento
Login, reanudacion, logout, revocacion remota, cambio de profile.

### 6.3 Quien puede moverlo
Usuario (login/logout/cambio de profile); system (reanudacion); Owner/platform
admin (revocacion remota via M08).

### 6.4 Que se notifica y a quien
Revocacion remota: cierre de la sesion en el desktop. Login en dispositivo nuevo:
notificacion (M08). Cambio de profile: cambio de contexto visible (tenant activo).

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Sesion desktop activa por tenant; acceso a la Mesa de Control con su rol (M09).

### 7.2 Que produce para el sistema
session.fromPartition por tenant; cookies httpOnly en main process; secretos en
keytar/safeStorage; config no secreta en electron-store; evento de login (M08);
audit D10.

### 7.3 Donde aparece el output
Particion de Electron; keychain del SO; sesion server-side en Redis (M08); audit
log.

### 7.4 Que formato tiene
Particion 'persist:faberloom-{profile}'; cookie httpOnly; secreto en keychain;
config JSON no secreta en electron-store.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Keychain no disponible: la app no puede guardar el secreto de forma segura -> no
persiste sesion local, exige re-login (fail-closed, no cae a localStorage).
Particion corrupta: se recrea, exige login. Riesgo localStorage: si por error se
usara, un XSS podria exfiltrar la sesion -> prohibido por diseno; los tokens van
solo a keychain. Revocacion remota: la siguiente revalidacion cierra la sesion.

### 8.2 Como se recupera
Re-login (recrea particion + secreto en keychain); seleccion de otro profile;
recuperacion de password/2FA via web (M08).

### 8.3 Quien se entera
Usuario: errores de login/keychain. Owner: revocaciones. Tecnico: fallos de
keychain/particion. Nivel: P1 si la app cae a almacenamiento inseguro (no deberia
poder); P2 errores normales de login.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Frecuencia de reanudacion vs login; profiles activos por maquina; fallos de
keychain por plataforma.

### 9.2 Como mejora con el tiempo
Tuning de TTL local de reanudacion; mejor manejo de keychain por SO. La seguridad
(flags) no se relaja con el aprendizaje.

### 9.3 Que feedback da el usuario
Implicito: reanudar vs re-loguear. Explicito: "no fui yo" ante login nuevo ->
revoca (M08).

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
Logout limpia la particion + el keychain del profile. Desinstalar la app elimina
particiones locales; los secretos del keychain se limpian en el logout (no quedan
huerfanos).

### 10.2 Que pasa con lo que dependia
Tras logout, el desktop pierde acceso; la sesion server-side se revoca (M08); las
preferencias no secretas pueden conservarse o limpiarse segun el flujo.

### 10.3 Es reversible
Logout es reversible (re-login). La limpieza de secretos no es reversible (hay que
re-autenticar).

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: M08 (flujo de auth y sesion server-side), M16 (la particion porta el
tenant para aislamiento). Alimenta a: M19 (reconexion offline parte de esta
sesion), M20 (auto-update opera sobre esta app), toda la operacion desktop.

### 11.2 En que orden
M08 autentica -> M18 crea la sesion desktop en la particion del tenant -> M19
gestiona reconexion -> M20 actualiza la app sin romper la sesion.

### 11.3 Que rompe si este modulo falla
Sin sesion Electron segura, el desktop no opera o expone tokens; sin particion por
tenant, mezcla de sesiones; sin keychain, no hay persistencia segura.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
El usuario su propia sesion/profile. Owner/platform admin: sesiones activas via
M08 (server-side). Nunca cross-tenant: particiones separadas por tenant.

### 12.2 Que queda en el audit trail D10
La auth se audita en M08 (auth.login.success/failed, session.revoked) con
tenant_id, user_id, actor_role_at_decision, timestamp, sha_chain. El desktop no
crea un audit paralelo: reusa el de M08/M12.

### 12.3 Que restricciones de datos aplican
session.fromPartition por tenant; cookies httpOnly en main process; secretos solo
en keytar/safeStorage; electron-store solo para config no secreta; prohibido
localStorage para tokens (riesgo XSS); contextIsolation=true, nodeIntegration=false;
logout limpia particion + keychain.

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Desktop (Electron) exclusivamente. La web usa el modelo de M08 (cookie httpOnly +
SameSite=Strict en el navegador).

### 13.2 Diferencias entre desktop y web
Desktop: particion por tenant + keychain + flags de hardening de Electron. Web:
cookie httpOnly del navegador, sin keychain ni particiones.

### 13.3 Offline y sincronizacion
La sesion desktop persiste localmente (de forma segura) y permite reanudar; la
validacion contra el server ocurre al reconectar (M19). No se conceden permisos ni
acciones sensibles offline en S1A.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE] Definir el TTL local de reanudacion de la sesion desktop antes de
   exigir revalidacion server-side.
2. [PENDIENTE] Confirmar la convencion exacta de naming del profile en la particion
   ('persist:faberloom-{profile}': profile = tenant_slug o user+tenant).
3. [PENDIENTE] Definir comportamiento si el keychain del SO esta bloqueado/no
   disponible en la plataforma del usuario.

## CONTRADICCIONES DETECTADAS CON LA KB

1. Solapamiento M08/M18: M08 cubre auth web+Electron de forma general y M18
   profundiza Electron. No es contradiccion; M18 es el detalle desktop de M08. Se
   documenta para evitar duplicacion divergente en futuras ediciones.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones de auth/sesion
  Electron. session.fromPartition por tenant, keytar/safeStorage, electron-store
  no-secreto, contextIsolation/nodeIntegration, prohibido localStorage, logout
  limpia particion+keychain.
