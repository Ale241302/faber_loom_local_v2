# SPEC_FB_FUNC_M08_AUTH_SESSION_v1 -- Ficha Funcional Autenticacion y Sesion (Web + Electron)
id: SPEC_FB_FUNC_M08_AUTH_SESSION_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_AUTH_TENANT_RBAC_v1.md - SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1.md - SPEC_FB_FUNC_M09_RBAC_v1.md - SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1.md - SPEC_FB_FUNC_M18_ELECTRON_AUTH_v1.md

---

## CABECERA DE FICHA

MODULO: Autenticacion y sesion (web Next.js + desktop Electron)
SUPERFICIE: Transversal (Web + Desktop)
SPRINT E1: S1A (auth + 2FA + sesion server-side)
ROLES QUE LO USAN: Owner (2FA obligatorio), Operator; Admin/Supervisor/Viewer E3+
DATA CLASS TIPICA: N2 (credenciales/sesion); los tokens son secretos cifrados

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
Sin autenticacion confiable cualquiera podria leer drafts, cotizaciones y datos
de cliente del tenant. El Owner siente el riesgo desde el primer login: necesita
una garantia de que solo su gente entra y de que una sesion robada no expone la
operacion. La sesion server-side existe para poder invalidar acceso al instante.

### 1.2 A quien le duele
Owner: responsable de que nadie ajeno entre; su cuenta exige 2FA. Operator:
necesita login simple y estable en el desktop diario. Platform admin: debe poder
cortar una sesion comprometida remotamente.

### 1.3 Cuando aparece
En cada inicio de sesion (web o Electron), en cada request autenticado, y cuando
una sesion debe renovarse, cerrarse o invalidarse.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Autenticar a la persona, ligar la sesion al tenant correcto, y mantener la
sesion server-side para poder revocarla sin esperar expiracion.

### 2.2 Que valor entrega
Acceso seguro multi-superficie; 2FA obligatorio para Owner; revocacion remota
inmediata; tokens locales fuera del alcance de XSS (keychain del SO, no
localStorage).

### 2.3 Que pasa si no existe
Sin sesion server-side no se puede revocar acceso comprometido. Sin 2FA, una
credencial filtrada del Owner compromete todo el tenant. Sin separacion por
particion en Electron, dos tenants comparten cookies.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
La sesion se crea al autenticar:
1. Usuario ingresa email + password.
2. Backend valida credenciales (hash argon2/bcrypt).
3. Si el rol es Owner (o 2FA habilitado): pide TOTP de 6 digitos.
4. Validado el TOTP, se crea una sesion server-side en Redis (session_id ->
   {user_id, tenant_id, role, issued_at, expires_at}).
5. Web: se entrega cookie httpOnly + Secure + SameSite=Strict con el session_id.
6. Electron: el session_id vive en session.fromPartition por tenant; los tokens
   sensibles van a keytar/safeStorage (ver M18).

### 3.2 Quien puede crearlo
Cualquier usuario con membership activo en el tenant. El primer Owner se crea en
el bootstrap (M07, paso 2) con 2FA obligatorio.

### 3.3 Que necesita para crearse
Usuario en `users` + `membership` en el tenant; tenant en estado `active` o
`setup` (para el wizard); para Owner, TOTP enrolado con backup codes.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
El Operator abre el desktop, que reanuda la sesion si sigue valida; si expiro,
pide login. Frecuencia: 1 login por jornada tipica, con reanudacion silenciosa.

### 4.2 Como se invoca
Pantalla de login (web/desktop); reanudacion automatica al abrir el desktop
(GET /auth/me con el session_id de la particion).

### 4.3 Que ve el usuario mientras ocurre
Inicial: formulario de login. En proceso: spinner "Verificando..."; si 2FA,
campo de codigo. Completado: entra a Mesa de Control / Settings. Error: mensaje
especifico (credenciales, 2FA, sesion expirada).

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
El usuario cambia password y re-enrola 2FA desde su perfil (web). El Owner puede
forzar reset de 2FA de un miembro. La sesion no se "edita": se renueva o se
revoca.

### 5.2 Que se puede cambiar y que no
Editable: password, dispositivo TOTP, backup codes, nombre de display.
No editable: user_id, tenant_id de la membership, historial de logins (audit).

### 5.3 Que pasa con lo generado previamente
Al cambiar password o re-enrolar 2FA: todas las sesiones activas del usuario se
invalidan (cleanup en Redis) y se exige re-login en todas las superficies.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine de la sesion:
```
anon -- trigger: credenciales OK, no-2FA, actor: usuario --> authenticated
anon -- trigger: credenciales OK + 2FA requerido, actor: usuario --> pending_2fa
pending_2fa -- trigger: TOTP correcto, actor: usuario --> authenticated
pending_2fa -- trigger: 3 fallos de TOTP, actor: system --> locked
authenticated -- trigger: logout, actor: usuario --> revoked
authenticated -- trigger: expira TTL, actor: system --> expired
authenticated -- trigger: revocacion remota, actor: Owner/platform_admin --> revoked
locked -- trigger: cooldown + reset, actor: usuario/Owner --> anon
```

### 6.2 Que dispara el movimiento
Login, validacion TOTP, logout, expiracion de TTL, revocacion remota, lockout
por fallos.

### 6.3 Quien puede moverlo
Usuario (login/logout); system (expiracion, lockout); Owner/platform admin
(revocacion remota de sesiones de miembros).

### 6.4 Que se notifica y a quien
Lockout por 2FA (3 fallos): alerta al Owner + email al usuario afectado. Login
desde dispositivo nuevo: notificacion al usuario. Revocacion remota: cierre
inmediato de sesion en todas las superficies del usuario.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Sesion activa que da acceso a las superficies segun su rol (M09). Confirmacion
visual de "conectado como [nombre] / [tenant]".

### 7.2 Que produce para el sistema
Registro de sesion en Redis (server-side); cookie httpOnly (web) o entrada en
session.fromPartition (Electron); evento `auth.login.success` / `auth.login.failed`;
audit D10 del login. Tokens locales en keytar/safeStorage (Electron).

### 7.3 Donde aparece el output
Cookie del navegador / particion de Electron; sesion en Redis; audit log; badge
de usuario conectado en la UI.

### 7.4 Que formato tiene
session_id opaco (no JWT con claims sensibles en cliente); registro Redis JSON;
cookie httpOnly+Secure+SameSite=Strict; evento JSON canonico con SHA-chain.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Credenciales invalidas: mensaje generico "email o password incorrectos" (no
revela cual). 2FA incorrecto: contador de intentos; al 3er fallo -> `locked` con
cooldown y alerta al Owner. Sesion expirada: redirect a login conservando deep
link de retorno. Redis caido: las sesiones no validan -> modo degradado, se
exige re-login al recuperar (fail-closed: sin sesion validada, no hay acceso).

### 8.2 Como se recupera
Reset de password via email verificado; reset de 2FA con backup codes o por el
Owner; tras lockout, cooldown configurable y re-intento. Reanudacion de sesion:
GET /auth/me con el session_id valido tras reconexion.

### 8.3 Quien se entera
Usuario: errores de su login. Owner: lockouts y revocaciones de su tenant.
Langfuse/Grafana: tasa de fallos de auth. Nivel: P1 lockout sospechoso; P0 si se
detecta toma de sesion cross-tenant.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Patrones de login (horario, dispositivo); tasa de fallos 2FA; sesiones por
usuario; intentos desde IP/dispositivo nuevos.

### 9.2 Como mejora con el tiempo
Senales para risk-based step-up futuro (no en E1): pedir 2FA extra ante login
anomalo. Ajuste de TTL de sesion segun uso real.

### 9.3 Que feedback da el usuario
Implicito: aceptar/rechazar "recordar este dispositivo". Explicito: reportar
"no fui yo" ante una notificacion de login nuevo -> revoca sesiones.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
Logout = revoca la sesion (delete del registro Redis + limpieza de cookie/
particion). Una cuenta se desactiva (no se borra) desde M09; sus sesiones se
revocan en cascada.

### 10.2 Que pasa con lo que dependia
Logout/revocacion: la persona pierde acceso inmediato en todas las superficies.
Las tasks que tenia abiertas quedan segun M09 (reasignacion). El audit del login
se conserva.

### 10.3 Es reversible
Logout es reversible (volver a loguear). El lockout es reversible tras cooldown/
reset. La revocacion remota exige re-login.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: M07 (creacion del primer Owner y enrolamiento 2FA), M16 (la sesion
porta el tenant_id que alimenta RLS), secret store. Alimenta a: M09 (el rol de
la sesion gobierna permisos), M18 (sesion Electron), todo request autenticado.

### 11.2 En que orden
M07 crea Owner+2FA -> M08 autentica y porta tenant_id -> M16 aplica RLS con ese
tenant_id -> M09 resuelve permisos por rol.

### 11.3 Que rompe si este modulo falla
Sin auth no entra nadie; sin sesion server-side no se revoca; sin tenant_id en
la sesion, M16 no puede aislar -> riesgo de leak.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
El usuario ve su propia sesion. Owner/platform admin ven la lista de sesiones
activas del tenant para poder revocar. Nunca cross-tenant.

### 12.2 Que queda en el audit trail D10
tenant_id, user_id, actor_role_at_decision, action (auth.login.success /
auth.login.failed / auth.2fa.locked / auth.session.revoked), resource_id
(session_id), data_class (N2), human_gate_required (false), human_approver_id
(null o quien revoco), timestamp, sha_chain_prev/sha_chain_curr.

### 12.3 Que restricciones de datos aplican
Password con hash fuerte; 2FA TOTP obligatorio Owner; cookie httpOnly+Secure+
SameSite=Strict (web); tokens locales solo en keytar/safeStorage (nunca
localStorage); sesion server-side revocable; contextIsolation=true,
nodeIntegration=false en Electron (ver M18).

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Transversal. Web: login + governance del Owner. Desktop (Electron): login y
reanudacion de la operacion diaria del Operator.

### 13.2 Diferencias entre desktop y web
Web: cookie httpOnly+SameSite=Strict en el navegador. Electron:
session.fromPartition por tenant, cookies en el main process, tokens en
keytar/safeStorage; contextIsolation=true, nodeIntegration=false (detalle en M18).

### 13.3 Offline y sincronizacion
La validacion de sesion requiere conexion (Redis). Si el desktop pierde
conexion, opera con la sesion ya validada hasta el TTL local corto; al
reconectar revalida con GET /auth/me. No se permiten acciones sensibles offline
en S1A (ver M19).

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE -- SPEC_FB_AUTH_TENANT_RBAC] Definir TTL exacto de sesion server-side
   y politica de "recordar dispositivo".
2. [PENDIENTE] Definir el algoritmo de hash de password (argon2id recomendado) y
   parametros de costo.
3. [PENDIENTE] Definir cooldown exacto del lockout tras 3 fallos de 2FA.

## CONTRADICCIONES DETECTADAS CON LA KB

1. Roles E1: la matriz de roles usa 5 roles canonicos; PLB enmienda E-4 reduce
   E1 a Owner/Operator. La ficha asume 2FA obligatorio para Owner (canonico) y
   marca el resto como E3+.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones de auth y sesion
  web + Electron. Sesion server-side Redis, 2FA TOTP Owner, revocacion remota.
  Detalle Electron en SPEC_FB_FUNC_M18.
