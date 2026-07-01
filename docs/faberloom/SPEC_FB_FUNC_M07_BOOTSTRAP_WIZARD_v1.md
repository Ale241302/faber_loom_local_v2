# SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1 -- Ficha Funcional Bootstrap Wizard de Tenant
id: SPEC_FB_FUNC_M07_BOOTSTRAP_WIZARD_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_AUTH_TENANT_RBAC_v1.md - SPEC_FB_TENANT_BOOTSTRAP_SEED_v1.md - SPEC_FB_FUNC_M08_AUTH_SESSION_v1.md - SPEC_FB_FUNC_M11_D9_POLICY_GATE_v1.md - SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1.md - SCH_FB_VOICE_PROFILE_v1.md

---

## CABECERA DE FICHA

MODULO: Bootstrap wizard de tenant
SUPERFICIE: Web (Next.js) -- invitacion platform-side
SPRINT E1: S1A (schema tenant + RLS) / S10 (onboarding wizard + DPA + bootstrap checks)
ROLES QUE LO USAN: Owner (ejecuta), FaberLoom platform admin/CEO (invita en E1), Operator (configurado en paso 7); Admin/Supervisor/Viewer son E3+ (enmienda E-4)
DATA CLASS TIPICA: N2 (config comercial del tenant); escala a N3 al conectar datos de clientes en paso 6/8

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
El Owner de una PYME B2B (ej. Alvaro en MWT) necesita activar FaberLoom sin
depender de un deploy manual ni de un ingeniero. Sin wizard de bootstrap el
tenant queda inoperativo: faltan datos minimos (entidad legal, primer Owner
con 2FA, mailbox, work-type pack, KB seed, Voice Profile, DPA). Con el wizard
el Owner pasa de cero a procesar su primer RFQ real en SANDBOX en < 1 hora.

### 1.2 A quien le duele
Owner: debe completar el wizard para activar el tenant; sin esto no puede
invitar equipo ni procesar inbound.
FaberLoom platform admin/CEO: en E1 invita manualmente al primer Owner (no hay
self-service signup publico, PLB Sec.5.B).
Operator: no puede entrar hasta que Owner lo invite y configure su Voice Profile.

### 1.3 Cuando aparece
Al inicio de la relacion con un tenant nuevo. El wizard se dispara cuando el
primer Owner acepta la invitacion de plataforma y hace login con 2FA obligatorio.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Activar un tenant productivo con los datos minimos para recibir, clasificar y
cotizar un RFQ en SANDBOX, aplicando los guardrails de seguridad antes de que
entre dato real.

### 2.2 Que valor entrega
Reduce el time-to-first-RFQ de dias/semillas manuales a < 1 hora. Garantiza
que 2FA, RLS, DPA y data class se apliquen antes del primer dato de cliente.

### 2.3 Que pasa si no existe
El Owner no puede operar. Los agentes system no se seedean en shadow, el
mailbox no se conecta, los inbound rebotan, no hay Voice Profile, el equipo no
tiene permisos. La activacion exige intervencion manual de ingenieria por tenant.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
El tenant se crea en estado `setup` por un platform admin de FaberLoom via
invitacion manual (E1). El Owner la acepta y completa los pasos:

1. Datos del tenant: nombre legal, commercial_name, subdominio (slug), idioma
   default, vertical_spec_object_id (`safety_footwear` en E1).
2. Crear primer Owner: email + password + TOTP 2FA obligatorio + backup codes
   (ver M08).
3. Conectar mailbox: Gmail OAuth (scope send/read) o IMAP/SMTP custom; watch/poll
   configurado.
4. Conectar canales WhatsApp BSP: [PENDIENTE -- enmienda E-5 PLB difiere WhatsApp
   Business a E3; en E1-E2 el wizard ofrece email-only]. Paso visible pero
   marcado "disponible en E3".
5. KB upload: curar 5-10 documentos (catalogo, lista de precios). Flujo upload ->
   parse preview -> afirmaciones HIGH/LOW -> reindex.
6. Voice Profile del primer Operator: persona + tono + glosario + saludo + firma.
7. DPA: firma del Data Processing Agreement antes de habilitar datos reales N3
   (gate de M11/D9). [PENDIENTE -- decidir si firma e-sign in-wizard u offline].
8. Seed de agentes system en shadow: `@router`, `@cotizador` (origin=system,
   inmutables) creados en estado shadow.
9. Sandbox test: enviar/recibir 1 RFQ de prueba; verificar que L1 clasifica
   (M10), que el draft aparece en Zona 3, y que Owner aprueba/rechaza sin salir
   del sandbox.
10. Go-live: completados pasos minimos + sandbox OK + DPA -> tenant `active`.

### 3.2 Quien puede crearlo
Platform admin/CEO de FaberLoom crea el tenant en `setup` e invita al Owner.
Owner completa el wizard. Admin asiste solo en E3+.

### 3.3 Que necesita para crearse
Invitacion manual de plataforma (E1); subdominio disponible
(`mwt.faberloom.com`); credenciales Gmail OAuth aprobadas o IMAP/SMTP; DPA
firmado antes de datos reales (Sec.5.B); 10-15 RFQs pre-curados por CEO como
golden seed; work-type pack seed. Si falta algo, el paso se marca pendiente y
el wizard permite "Guardar y continuar" salvo en gates bloqueantes (DPA, 2FA).

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
No es uso diario. Es un wizard one-time por tenant. Tras completarse, Owner
accede a Settings tenant para mantener config; los usuarios nuevos se invitan
desde Usuarios y roles (ver M09).

### 4.2 Como se invoca
Deep link desde el email de invitacion. Re-apertura automatica al login si
quedan pasos bloqueantes. Navegacion a Settings tenant si se reanuda.

### 4.3 Que ve el usuario mientras ocurre
Inicial: progress bar con los 10 pasos y checkmarks.
En proceso: validacion inline (subdominio disponible, OAuth success, 2FA QR,
parse preview de KB).
Completado: sandbox test result (success/warning/error) con detalle de
clasificacion y draft; badge verde de tenant activo.
Error: banner por paso con el detalle y boton de retry.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
Post-bootstrap, Owner/Admin editan la config en Settings tenant (web): nombre
commercial, idioma, plan y addons, glosario tenant-wide, bindings de mailbox,
Voice Profile defaults. El subdominio requiere coordinacion con FB-admin
(SPEC_FB_AUTH_TENANT_RBAC Sec.5.2).

### 5.2 Que se puede cambiar y que no
Editable: commercial_name, idioma, glosario, plan, addons, canales, Voice Profile.
No editable: tenant_id/slug (inmutable), legal_name (requiere justificacion),
subdominio (requiere FB-admin). El Operator no edita config del tenant.

### 5.3 Que pasa con lo generado previamente
Cambio de subdominio: redirect 301, sesiones invalidadas. Cambio de mailbox:
nuevos inbound usan el nuevo buzon, historico conservado. Cambio de Voice
Profile: no afecta drafts ya aprobados; afecta drafts nuevos.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
State machine del tenant:
```
setup -- trigger: Owner completa pasos 1-3,5-6 minimos + sandbox OK + DPA, actor: Owner+platform_admin --> active
setup -- trigger: Owner guarda progreso parcial, actor: Owner --> setup (parcial)
setup -- trigger: falla sandbox o falta DPA, actor: system --> setup (bloqueado)
setup -- trigger: invitacion expira sin aceptar, actor: system --> expired
active -- trigger: Owner/platform suspende, actor: Owner/platform_admin --> suspended
active -- trigger: cancela suscripcion (E3+), actor: Owner --> cancelled
```

### 6.2 Que dispara el movimiento
Aceptacion de invitacion (manual); completitud de pasos minimos + sandbox OK +
DPA (mixto); suspension (manual); expiracion de invitacion (TTL default 7 dias).

### 6.3 Quien puede moverlo
setup -> active: Owner completando wizard + platform admin validando DPA.
active -> suspended: Owner o platform admin. setup -> expired: system.

### 6.4 Que se notifica y a quien
Invitacion enviada: email al Owner. Progreso guardado: toast. Sandbox OK: badge
verde + notificacion al Owner. Falta DPA: banner bloqueante al Owner + platform
admin. Tenant activo: notificacion al Owner y al Operator invitado.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Tenant operativo con subdominio resuelto; primer Owner y Operator configurados;
mailbox conectado; agentes base en shadow; KB seed; Voice Profile inicial.

### 7.2 Que produce para el sistema
Fila en `tenants` (tenant_id, slug, vertical_spec_object_id, plan_tier, status);
Owner en `users` + `membership`; sesion 2FA en Redis; mailbox row con tokens
OAuth cifrados; documents/chunks en KB; agentes system seed en shadow.
Eventos/audit D10: `tenant.created`, `user.invited`, `user.2fa_enabled`,
`mailbox.connected`, `document.uploaded`, `tenant.activated`.

### 7.3 Donde aparece el output
Settings tenant (web); Mesa de Control (desktop) una vez activo; audit log;
sesion Redis.

### 7.4 Que formato tiene
Config JSON en `tenants.config`; tokens cifrados en secret store; documentos en
MinIO/filesystem + chunks en Postgres; eventos JSON con SHA-chain.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Gmail OAuth falla (paso 3): wizard muestra error con retry; Owner puede saltar a
IMAP/SMTP custom.
Falla en el paso 4 (canales WhatsApp): en E1 el paso esta diferido (E-5); si se
intenta, el wizard lo marca "no disponible en E1" y permite continuar sin
bloquear (email-only es suficiente para go-live).
Subdominio no disponible: validacion inline rechaza.
2FA no escaneado: no avanza al paso 3 (gate duro).
Upload KB falla (paso 5): paso queda pendiente; permite continuar pero el
sandbox no clasificara bien.
Sandbox test falla (paso 9): tenant en `setup` (bloqueado), muestra log, escala
a platform admin.
DPA no firmado (paso 7): banner bloqueante antes de habilitar datos reales N3.

### 8.2 Como se recupera
El wizard persiste el progreso por paso (ver 13.3): retomar = reabrir deep link
o login, el wizard salta al primer paso incompleto. Retry de OAuth, re-subir
documento, re-configurar Voice Profile, repetir sandbox cuantas veces sea
necesario. Para invitacion/DPA: contactar al platform admin.

### 8.3 Quien se entera
Owner: errores del wizard. Platform admin/CEO: fallos de sandbox, DPA pendiente,
expiracion de invitacion. Nivel: P1 config; P0 si hay leak o DPA bloqueante con
dato real ya ingresado.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Tiempo por paso; tasa de abandono por paso; configuraciones default mas usadas;
errores frecuentes de OAuth/upload.

### 9.2 Como mejora con el tiempo
El wizard pre-llena defaults segun vertical (`safety_footwear`); sugiere
documentos de KB faltantes; detecta providers de mailbox comunes.

### 9.3 Que feedback da el usuario
Implicito: completar/saltar pasos. Explicito: aceptar/rechazar sugerencias
default; reportar problemas en sandbox.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
Los tenants no se borran fisicamente: se deprecan/cancelan. En E1 no hay
self-cancelacion; requiere platform admin. Suspend pausa la operacion y conserva
datos; cancel/deprecate marca `status=cancelled`, desactiva canales y conserva
audit log.

### 10.2 Que pasa con lo que dependia
Usuarios no pueden login; agentes pausados; inbound rebota con "tenant inactivo";
datos conservados segun retencion (PLB backup + POL_DATA_CLASSIFICATION).

### 10.3 Es reversible
Suspendido -> activo: si (Owner/platform admin). Cancelado -> activo: no sin
proceso de reactivacion manual y revision de datos.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: Auth/RBAC (M08, M09), Aislamiento multi-tenant (M16, RLS de S1A),
Integration Layer, Mailbox, KB upload, Agent Factory seed, Voice Profile, D9
Policy Gate (M11, gate de DPA).
Alimenta a: Mesa de Control, Workspace, Audit (M12), Eventing/Outbox (M15).
Alternativo: N/A -- el bootstrap es obligatorio.

### 11.2 En que orden
platform admin crea setup -> Owner acepta -> Auth+2FA (M08) -> canales -> KB seed
-> Voice Profile -> DPA (M11) -> seed agentes shadow -> sandbox -> activacion ->
invitar Operators (M09).

### 11.3 Que rompe si este modulo falla
Todo FaberLoom para ese tenant: sin tenant activo no hay usuarios, canales,
agentes ni tasks.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Owner: todo el wizard y la config. Admin (E3+): config excepto tokens y DPA
firmado. Operator: solo su Voice Profile. Platform admin: metadata del tenant,
no datos de cliente salvo soporte con audit. Nunca cross-tenant.

### 12.2 Que queda en el audit trail D10
tenant_id, user_id (Owner), actor_role_at_decision=Owner, action
(tenant.created / tenant.activated / mailbox.connected / document.uploaded /
user.invited), resource_id (tenant_id/mailbox_id/document_id), data_class (N2),
model_provider/model_id (si aplica), human_gate_required (false salvo sandbox),
human_approver_id (Owner), timestamp, sha_chain_prev/sha_chain_curr.

### 12.3 Que restricciones de datos aplican
N2 default para config; N3/N4 hard-block hasta DPA firmado y consentimiento
(gate M11/D9); tokens OAuth cifrados en reposo; 2FA obligatorio Owner;
Anthropic-only con DPA vigente (TIER 1).

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Web (Next.js) -- el wizard de bootstrap y Settings tenant viven solo en web.

### 13.2 Diferencias entre desktop y web
El desktop (Electron) no tiene bootstrap: es para la operacion diaria una vez el
tenant esta activo. La governance y configuracion inicial son exclusivas de web.

### 13.3 Offline y sincronizacion
No aplica offline: el bootstrap requiere conexion para OAuth y validaciones.
Persistencia entre sesiones del wizard: cada paso completado se guarda en
`tenants.config` (server-side) con marca de paso; al reabrir, el wizard lee el
estado y salta al primer paso incompleto. Datos sensibles (tokens) se persisten
cifrados; el password/2FA secret no se guarda en claro entre sesiones.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE -- enmienda E-5 PLB] Paso 4 (canales WhatsApp BSP): confirmar si se
   mantiene visible-pero-diferido o se oculta en E1-E2 (email-only).
2. [PENDIENTE -- PLB Sec.5.B] DPA: definir si la firma es e-sign in-wizard
   (paso 7) u offline antes de S10. Afecta el gate de go-live.
3. [PENDIENTE -- SPEC_FB_AUTH_TENANT_RBAC Sec.11] Definir el email provider para
   invitaciones y verificacion (SendGrid/SES).
4. [PENDIENTE -- ENT_FB_WORK_TYPE_PACK_v1] Confirmar el contenido exacto del seed
   work-type pack safety footwear (paso 5).
5. [PENDIENTE -- SPEC_FB_ROUTINES_v1] Definir si las rutinas base se seedean en el
   bootstrap o despues en S5/S6.

## CONTRADICCIONES DETECTADAS CON LA KB

1. WhatsApp en bootstrap vs email-only E1: el prompt incluye "canales WhatsApp
   BSP" en el paso 4, pero PLB enmienda E-5 difiere WhatsApp Business a E3. Se
   especifica como paso diferido; requiere resolucion CEO.
2. Roles en el wizard: SCH_FB_FUNCTIONAL_SPEC lista 5 roles canonicos, pero PLB
   enmienda E-4 reduce E1 a Owner/Operator. La ficha usa 5 roles con nota E3+.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones del bootstrap
  wizard de tenant. Base de referencia: SCH_FB_FUNCTIONAL_SPEC_v1, ejemplo M06
  (Tenant Bootstrap), SPEC_FB_TENANT_BOOTSTRAP_SEED_v1.
