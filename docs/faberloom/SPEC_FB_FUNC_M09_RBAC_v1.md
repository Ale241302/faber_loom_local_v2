# SPEC_FB_FUNC_M09_RBAC_v1 -- Ficha Funcional RBAC y Permisos
id: SPEC_FB_FUNC_M09_RBAC_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_AUTH_TENANT_RBAC_v1.md - SPEC_FB_FUNC_M08_AUTH_SESSION_v1.md - SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md - SPEC_FB_FUNC_M12_AUDIT_TRAIL_v1.md

---

## CABECERA DE FICHA

MODULO: RBAC y permisos
SUPERFICIE: Transversal (Web + Desktop)
SPRINT E1: S1A (5 roles canonicos + matriz); E1 activa Owner/Operator (enmienda E-4)
ROLES QUE LO USAN: Owner, Admin, Operator, Supervisor, Viewer
DATA CLASS TIPICA: N1 (metadata de membership y roles)

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
Sin RBAC, cualquier miembro del tenant podria aprobar cotizaciones, editar
agentes o ver el audit completo. El Owner siente el problema cuando suma equipo:
necesita que un Operator opere sin tocar configuracion ni governance, y que un
Viewer mire sin poder accionar. Sin permisos, separar "quien hace que" depende de
confianza, no de control.

### 1.2 A quien le duele
Owner: define quien entra y con que poder. Admin (E3+): gestiona usuarios y
config sin tocar facturacion. Operator: solo necesita operar. Supervisor (E3+):
supervisa calidad sin re-configurar. Viewer (E3+): solo lectura.

### 1.3 Cuando aparece
Al invitar un usuario, al asignarle rol(es), y en cada accion donde el permiso
del rol decide si se permite o se bloquea.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Gobernar que puede ver y hacer cada persona por superficie, con minimo privilegio
y multi-rol seleccionable.

### 2.2 Que valor entrega
Separacion de funciones; el Owner delega sin ceder control total; el operativo no
puede romper configuracion; el audit registra el rol vigente en cada decision.

### 2.3 Que pasa si no existe
Todos serian de facto Owner. No habria separacion entre operar, configurar y
auditar; cada accion sensible quedaria sin control de quien la puede ejecutar.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
Los 5 roles son canonicos y se seedean con el tenant (no se crean ad-hoc en E1).
La asignacion se crea al invitar a un usuario:
1. Owner/Admin abre Usuarios y roles (web).
2. Ingresa email + selecciona rol(es).
3. Sistema envia invitacion (ver M08).
4. Al aceptar, se crea la `membership` con los roles asignados.

### 3.2 Quien puede crearlo
Owner: invita y asigna cualquier rol, incluido Admin. Admin (E3+): invita
Operator/Supervisor/Viewer, no puede crear otro Owner. Operator/Supervisor/
Viewer: no invitan.

### 3.3 Que necesita para crearse
Tenant activo; cuota de asientos del plan disponible; email del invitado. Si no
hay asientos, se muestra "limite del plan alcanzado" (gate de plan).

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
Transparente: cada vez que un usuario actua, el backend resuelve el permiso del
rol activo. En desktop, una persona con multi-rol elige el "hat" activo desde un
selector; la UI se adapta al hat.

### 4.2 Como se invoca
Automatico en cada request (autorizacion server-side). El selector de hat se
invoca manualmente en el header del desktop.

### 4.3 Que ve el usuario mientras ocurre
Las superficies/acciones fuera de su rol aparecen ocultas o deshabilitadas con
tooltip "requiere rol [X]". Al cambiar de hat, la UI recarga las superficies
permitidas para ese hat.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
Owner/Admin editan los roles de un miembro en Usuarios y roles: agregar/quitar
rol, cambiar hat permitido, revocar acceso.

### 5.2 Que se puede cambiar y que no
Editable: roles de la membership, estado (activo/suspendido). No editable: la
definicion de los 5 roles canonicos (sellada), el user_id, el historial de
cambios de rol (audit).

### 5.3 Que pasa con lo generado previamente
Cambiar el rol de una persona no reescribe el audit: las decisiones pasadas
conservan el `actor_role_at_decision` que tenian. Si se le quita un permiso, sus
acciones futuras se bloquean, las pasadas quedan validas.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine de la membership:
```
invited -- trigger: usuario acepta, actor: usuario --> active
active -- trigger: Owner/Admin suspende, actor: Owner/Admin --> suspended
suspended -- trigger: Owner/Admin reactiva, actor: Owner/Admin --> active
active -- trigger: Owner/Admin revoca, actor: Owner/Admin --> revoked
invited -- trigger: expira invitacion, actor: system --> expired
```

### 6.2 Que dispara el movimiento
Aceptacion de invitacion; suspension/reactivacion/revocacion por Owner/Admin;
expiracion de invitacion.

### 6.3 Quien puede moverlo
Owner: cualquier membership salvo auto-revocarse si es el ultimo Owner (bloqueo).
Admin (E3+): memberships no-Owner. El sistema: expiracion.

### 6.4 Que se notifica y a quien
Invitacion: email al invitado. Cambio de rol: notificacion al afectado.
Revocacion: cierre de sesiones del afectado (M08) + reasignacion de sus tasks
abiertas (ver 11/8).

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Acceso efectivo a las superficies y acciones de su(s) rol(es). Selector de hat si
es multi-rol.

### 7.2 Que produce para el sistema
Fila `membership` (user_id, tenant_id, roles[], status); resolucion de permisos
por request; evento `user.invited` / `user.role_changed` / `user.revoked`; audit
D10 con actor_role_at_decision.

### 7.3 Donde aparece el output
Usuarios y roles (web); selector de hat (desktop); audit log; gates de permiso en
cada superficie.

### 7.4 Que formato tiene
membership JSON; matriz de permisos rol x superficie (abajo); eventos canonicos.

### 7.5 Matriz de permisos por superficie
Leyenda: F=full, W=write/accion, R=read, - =sin acceso. (E1 activa solo
Owner/Operator; Admin/Supervisor/Viewer entran en E3 por enmienda E-4.)
```
Superficie        | Owner | Admin | Operator | Supervisor | Viewer
------------------|-------|-------|----------|------------|-------
WorkLoom (Mesa)   |   F   |   F   |    W      |     W       |   R
Workspace         |   F   |   F   |    W      |     W       |   R
Agent Factory     |   F   |   W   |    -      |     R       |   -
Skill Factory     |   F   |   W   |    -      |     R       |   -
Audit             |   F   |   R   |    R*     |     R       |   R*
Config (tenant)   |   F   |   W   |    -      |     -       |   -
Usuarios y roles  |   F   |   W** |    -      |     -       |   -
```
Notas: R* = el Operator/Viewer ve solo el audit de sus propias acciones, no el
del tenant completo. W** = Admin gestiona usuarios pero no puede crear Owner ni
tocar facturacion. La aprobacion de drafts (M13) es accion de WorkLoom: Operator/
Supervisor/Admin/Owner aprueban; Viewer no.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Accion sin permiso: bloqueo server-side con 403 y toast "no tenes permiso para
[accion]" (la UI ya deberia ocultarla; el server es la verdad). Remocion del
ultimo Owner: bloqueada con mensaje (debe existir >=1 Owner). Desync UI/server
(la UI muestra algo que el rol no permite): el server rechaza; la UI se corrige.
Remocion de un Operator con tasks abiertas: ver 8.2.

### 8.2 Como se recupera
Tasks abiertas de un Operator removido: pasan a estado `unassigned` y vuelven a
la cola de WorkLoom para que otro Operator (o Supervisor) las tome; los drafts en
`awaiting_approval` que el removido tenia siguen disponibles para otro aprobador
con permiso. Nada se pierde; nada se auto-envia sin aprobacion.

### 8.3 Quien se entera
Owner/Admin: intentos de accion sin permiso recurrentes (posible mala asignacion
de rol). Audit (M12): todo intento bloqueado se registra. Nivel: P2 bloqueo
normal; P1 si un rol intenta repetidamente escalar privilegio.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Frecuencia de bloqueos por rol/superficie; roles que solicitan acciones fuera de
su scope (senal de rol mal asignado).

### 9.2 Como mejora con el tiempo
Sugerencias al Owner: "este Operator pide seguido aprobar config; considera
Admin". No cambia permisos automaticamente.

### 9.3 Que feedback da el usuario
Implicito: intentos bloqueados. Explicito: el Owner ajusta roles segun el patron.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
Un usuario se desactiva/suspende o se revoca; no se borra (audit). Los 5 roles
canonicos no se eliminan.

### 10.2 Que pasa con lo que dependia
Al revocar: sesiones cerradas (M08), tasks reasignadas (8.2), drafts liberados.
El historico de acciones del usuario permanece en audit.

### 10.3 Es reversible
Suspension es reversible (reactivar). Revocacion exige re-invitar. La definicion
de roles es inmutable.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: M08 (la sesion porta el rol), M07 (primer Owner). Alimenta a: todas
las superficies (gate de permiso), M13 (quien aprueba drafts), M12 (audit
registra actor_role_at_decision), M14 (segundo aprobador N2+).

### 11.2 En que orden
M08 autentica -> M09 resuelve permisos -> la superficie permite/bloquea. La
asignacion de roles ocurre en bootstrap (Owner) y luego en Usuarios y roles.

### 11.3 Que rompe si este modulo falla
Sin RBAC, toda accion sensible queda sin control de autoria; el audit pierde el
campo actor_role_at_decision; la separacion operar/configurar/auditar desaparece.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Owner: toda la matriz y todas las memberships. Admin (E3+): memberships no-Owner.
Operator/Supervisor/Viewer: su propio rol. Nunca cross-tenant.

### 12.2 Que queda en el audit trail D10
tenant_id, user_id (actor), actor_role_at_decision, action (user.invited /
user.role_changed / user.revoked / permission.denied), resource_id (membership_id
/ target user_id), data_class (N1), human_gate_required (false), human_approver_id
(quien cambio el rol), timestamp, sha_chain. El cambio de rol es siempre auditado.

### 12.3 Que restricciones de datos aplican
Minimo privilegio por defecto; autorizacion server-side (la UI no es la verdad);
siempre >=1 Owner; el rol vigente al momento de decidir queda congelado en audit;
filtrado por tenant_id (RLS, M16).

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Transversal. Web: gestion de usuarios y roles (Owner/Admin). Desktop: selector de
hat activo y aplicacion de permisos en la operacion.

### 13.2 Diferencias entre desktop y web
Web: la administracion de roles (invitar, revocar, cambiar) vive aqui. Desktop:
solo seleccion de hat y consumo de permisos; no se administran roles desde el
desktop en E1.

### 13.3 Offline y sincronizacion
Los permisos se resuelven server-side; offline no se conceden permisos nuevos.
El hat activo se cachea localmente pero toda accion sensible revalida al
reconectar (ver M19). No se permite cambiar de hat para escalar privilegio
offline.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE -- enmienda E-4] Confirmar si E1 expone solo Owner/Operator en la UI
   de invitacion o muestra los 5 roles con los E3+ deshabilitados.
2. [PENDIENTE -- SPEC_FB_AUTH_TENANT_RBAC Sec.5.2] Confirmar si Admin puede ver el
   audit completo del tenant (matriz lo pone en R) o solo su scope.
3. [PENDIENTE] Definir politica exacta de reasignacion de tasks al revocar un
   Operator (cola general vs Supervisor especifico).

## CONTRADICCIONES DETECTADAS CON LA KB

1. 5 roles vs 2 roles E1: SCH_FB_FUNCTIONAL_SPEC y SPEC_FB_AUTH_TENANT_RBAC
   definen 5 roles; PLB enmienda E-4 activa solo Owner/Operator en E1. La ficha
   especifica los 5 (modulo ES sobre RBAC) y marca cuales activan en E3.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones de RBAC. Matriz de
  permisos 5 roles x 7 superficies; multi-rol con hat activo; reasignacion de
  tasks al revocar.
