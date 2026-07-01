# faberloom_func_modulo_06_tenant_isolation.md

Módulos transversales asignados al **AGENTE_6_TENANT_ISOLATION** del swarm de especificación funcional de FaberLoom Foundation Beta E1.

---

## MÓDULO 1 — Tenant Bootstrap

MÓDULO: Tenant Bootstrap
SUPERFICIE: Web (Next.js) + invitación platform-side
SPRINT E1: S1A (schema tenant + RLS) · S10 (onboarding wizard + DPA + bootstrap checks)
ROLES: Owner (obligatorio) · Admin (E3+) · Operator (configurado en paso 7) · FaberLoom platform admin/CEO (invita en E1)
DATA CLASS TÍPICA: N2 (datos de configuración comercial del tenant); N3 cuando se conectan datos de clientes en paso 8

### D1 EXISTENCIA

#### 1.1 Por qué existe
El CEO/Owner de una PYME B2B (ej. Alvaro en MWT) necesita empezar a operar FaberLoom sin depender de un deploy manual ni de un ingeniero. Sin un wizard de bootstrap, el tenant queda en estado no operativo porque faltan datos mínimos (tenant legal, primer Owner con 2FA, mailbox, work-type pack, KB seed, Voice Profile). Con el bootstrap, en menos de 1 hora puede recibir su primer RFQ real y procesarlo en SANDBOX.

#### 1.2 A quién le duele
- **Owner:** debe completar el wizard para activar el tenant; sin esto no puede invitar a su equipo ni procesar inbound.
- **Admin (E3+):** ayuda a configurar pero no puede activar el tenant sin Owner.
- **Operator:** no puede entrar hasta que Owner lo invite y configure Voice Profile.
- **FaberLoom platform admin/CEO:** debe invitar manualmente al primer Owner en E1.

#### 1.3 Cuando aparece
Al inicio de la relación con un nuevo tenant. En E1 la activación requiere invitación manual de la plataforma (PLB §5.B). El wizard se dispara cuando el primer Owner acepta la invitación y hace login con 2FA obligatorio.

### D2 PROPOSITO

#### 2.1 Para qué
Activar un tenant productivo en menos de 1 hora con los datos mínimos para recibir, clasificar y cotizar un RFQ safety footwear B2B en SANDBOX.

#### 2.2 Qué valor entrega
Reduce el time-to-first-RFQ de días/semillas manuales a <1h. Garantiza que los guardrails de seguridad (2FA, RLS, DPA, data class) se apliquen antes de que entre dato real.

#### 2.3 Qué pasa si no existe
El Owner no puede operar. Los agentes system no se seedean. El mailbox no se conecta. Los inbound rebotan o no se rutean. No hay Voice Profile. El equipo no tiene permisos.

### D3 CREACION

#### 3.1 Cómo se crea
El tenant se crea en modo `setup` por un platform admin de FaberLoom vía invitación manual en E1. El Owner la acepta y completa 8 pasos:

1. **Datos del tenant:** nombre legal, commercial_name, subdominio (slug), idioma default, `vertical_spec_object_id` (`safety_footwear` en E1).
2. **Crear primer Owner:** email + password + TOTP 2FA obligatorio + backup codes.
3. **Conectar primer mailbox:** Gmail OAuth (scope send/read) o IMAP/SMTP custom. Watch/poll configurado.
4. **Conectar WhatsApp:** Meta Cloud API — [PENDIENTE — enmienda E-5 PLB difiere WhatsApp a E3; doc SPEC_FB_ROUTINES_v1 en stub].
5. **Seed del work-type pack:** safety footwear por defecto en E1. [PENDIENTE — ENT_FB_WORK_TYPE_PACK_v1 está en stub; detalle del seed no definido].
6. **Curar 5-10 documentos de KB:** catálogo, lista de precios. Wizard upload → parse preview → afirmaciones HIGH/LOW → reindex.
7. **Configurar Voice Profile del primer Operator:** persona + tono + glosario + saludo + firma por user.
8. **Prueba con 1 RFQ real en SANDBOX:** enviar/recibir un email de prueba, verificar que L1 clasifica, que el draft aparece en Zona 3, y que Owner puede aprobar/rechazar sin salir del sandbox.

#### 3.2 Quién puede crearlo
- **Platform admin/CEO de FaberLoom:** crea el tenant en modo setup e invita al Owner. En E1 no hay self-service signup público.
- **Owner:** completa el wizard.
- **Admin:** puede asistir en E3+.

#### 3.3 Qué necesita para crearse
- Invitación manual de plataforma (E1).
- Dominio/subdominio disponible (`mwt.faberloom.com`).
- Credenciales Gmail OAuth aprobadas o IMAP/SMTP custom.
- DPA firmado antes de S10/datos reales (PLB §5.B).
- CEO pre-curado 10-15 RFQs reales/semirreales como golden seed (PLB Sprint 3).
- Work-type pack seed (safety footwear).

### D4 USO DIARIO

#### 4.1 Cómo se usa en el día a día
No es uso diario del Operator. Es un wizard one-time por tenant. Tras completarse, Owner accede a **Settings tenant** para mantener config. Los nuevos usuarios se invitan desde **Usuarios y roles**.

#### 4.2 Cómo se invoca
- Deep link desde email de invitación.
- Navegación a **Settings tenant** si el wizard se reanuda.
- Re-apertura automática al login si faltan pasos bloqueantes.

#### 4.3 Qué ve el usuario mientras ocurre
- Progress bar con 8 pasos y checkmarks.
- Validación inline (subdominio disponible, OAuth success, 2FA QR).
- Sandbox test result (`success`/`warning`/`error`) con detalle de clasificación y draft.
- Botón "Guardar y continuar" / "Completar después".

### D5 EDICION

#### 5.1 Cómo se edita
Post-bootstrap, Owner/Admin editan tenant config en **Settings tenant** (web Next.js):
- Nombre legal/commercial.
- Idioma default.
- Plan tier y addons.
- Subdominio (requiere coord con FB-admin según SPEC_FB_AUTH_TENANT_RBAC §5.2).
- Glossary tenant-wide.
- Mailbox/WhatsApp bindings.
- Voice Profile defaults.

#### 5.2 Qué se puede cambiar y qué no
- **Editable:** commercial_name, idioma, glossary, plan, addons, canales, Voice Profile.
- **No editable por Owner/Admin:** tenant_id/slug (inmutable), legal_name requiere justificación, subdominio requiere FB-admin.
- **No editable por Operator:** config tenant.

#### 5.3 Qué pasa con lo generado previamente
- Cambio de subdominio: redirect 301, sesiones invalidadas.
- Cambio de mailbox: nuevos inbound usan nuevo buzón; histórico conservado.
- Cambio de Voice Profile: no afecta drafts ya aprobados; afecta nuevos drafts.

### D6 MOVIMIENTO Y ESTADO

#### 6.1 Cómo se mueve
State machine del tenant:

```
setup -- trigger: Owner acepta invitación y completa pasos 1-7 mínimos --> active
setup -- trigger: Owner guarda progreso sin completar --> setup (parcial)
setup -- trigger: falla sandbox test o falta DPA --> setup (bloqueado)
active -- trigger: Owner suspende tenant --> suspended
active -- trigger: Owner cancela suscripción --> deprecated/cancelled (E3+)
setup -- trigger: expira invitación sin aceptar --> expired
```

#### 6.2 Qué dispara el movimiento
- Aceptación de invitación (manual).
- Completitud de pasos mínimos + sandbox OK + DPA (auto/manual).
- Suspensión por Owner o platform admin.
- Expiración de invitación (TTL configurable, default 7 días).

#### 6.3 Quién puede moverlo
- **setup → active:** Owner completando wizard + platform admin validando DPA.
- **active → suspended:** Owner o platform admin.
- **setup → expired:** sistema.

#### 6.4 Qué se notifica y a quién
- Invitación enviada: email al Owner.
- Progreso guardado: toast al Owner.
- Sandbox test OK: badge verde + notificación a Owner.
- Falta DPA: banner bloqueante a Owner + platform admin.
- Tenant activo: notificación a Owner + Operator invitado.

### D7 OUTPUT

#### 7.1 Qué produce para el usuario
- Tenant operativo con subdominio resuelto.
- Primer Owner y Operator configurados.
- Mailbox/WhatsApp (E3+) conectados.
- Agentes base en SHADOW (`@router`, `@cotizador` seed).
- KB seed con documentos curados.
- Voice Profile inicial.

#### 7.2 Qué produce para el sistema
- Registro en tabla `tenants` con `tenant_id`, `slug`, `vertical_spec_object_id`, `plan_tier`, `status`.
- Usuario Owner en `users` + `membership` con rol Owner.
- Sesión con 2FA validado en Redis.
- Mailbox row con OAuth tokens cifrados.
- WhatsApp account row (E3+).
- Documents/chunks en KB.
- Agentes system seed en SHADOW.
- Audit D10: `tenant.created`, `user.invited`, `user.2fa_enabled`, `mailbox.connected`, `document.uploaded`, `tenant.activated`.
- Eventos: `auth.login.success`, `tenant.activated`, `mailbox.connected`.

#### 7.3 Dónde aparece el output
- Settings tenant web.
- Mesa de Control desktop una vez activo.
- Audit log.
- Redis session.

#### 7.4 Qué formato tiene
- Config JSON en `tenants.config`.
- Tokens cifrados en secret store.
- Documentos en MinIO/filesystem + chunks en Postgres.
- Eventos JSON con SHA-chain.

### D8 ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
- **Gmail OAuth falla:** wizard muestra error con retry; Owner puede saltar a IMAP/SMTP custom.
- **Subdominio no disponible:** validación inline rechaza.
- **2FA no escaneado:** no avanza al paso 3.
- **Upload de KB falla:** wizard marca paso 6 como pendiente; permite continuar sin KB pero sandbox no clasificará.
- **Sandbox test falla:** estado `setup` (bloqueado); muestra log de error; escala a platform admin.
- **DPA no firmado:** banner bloqueante antes de S10/datos reales.
- **Platform admin no invita:** Owner no puede iniciar self-service en E1.

#### 8.2 Cómo se recupera
- Retry OAuth.
- Re-subir documento.
- Re-configurar Voice Profile.
- Contactar a platform admin para invitación o DPA.
- Sandbox se puede repetir tantas veces como sea necesario.

#### 8.3 Quién se entera
- **Owner:** errores de wizard.
- **Platform admin/CEO:** fallos de sandbox, DPA pendiente, expiración de invitación.
- **Nivel:** P1 configuración, P0 si hay leak o DPA bloqueante con datos reales.

### D9 APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Tiempo por paso del wizard.
- Tasa de abandono por paso.
- Configuraciones default más usadas.
- Errores frecuentes de OAuth/upload.

#### 9.2 Cómo mejora con el tiempo
- Wizard pre-llena valores default según vertical (`safety_footwear`).
- Sugerencias de KB documentos faltantes.
- Detección de mailbox providers más comunes.

#### 9.3 Qué feedback da el usuario
- Completar/check pasos.
- Rechazo/aceptación de sugerencias default.
- Reporte de problemas en sandbox.

### D10 ELIMINACION

#### 10.1 Cómo se elimina
Los tenants no se borran físicamente. Se deprecan/cancelan (PLB: mayoría de objetos se deprecan). En E1 no hay self-cancelación; requiere platform admin.
- **Suspend:** pausa operación, conserva datos.
- **Cancel/deprecate:** marca `status=cancelled`, desactiva canales, conserva audit log.

#### 10.2 Qué pasa con lo que dependía
- Usuarios: no pueden login.
- Agentes: pausados.
- Inbound: rebotan con mensaje de tenant inactivo.
- Datos: conservados según retención (PLB backup + POL_DATA_CLASSIFICATION §M).

#### 10.3 Es reversible
- **Suspendido → activo:** sí, por Owner/platform admin.
- **Cancelado → activo:** no sin proceso de reactivación manual y revisión de datos.

### D11 RELACIONES

#### 11.1 Con qué se relaciona
- **Depende de:** Auth/RBAC (SPEC_FB_AUTH_TENANT_RBAC), Integration Layer, Mailbox, WhatsApp (E3+), KB upload, Agent Factory seed, Voice Profile.
- **Alimenta a:** Mesa de Control, Workspace, Audit log, Eventing/Outbox.
- **Alternativo:** N/A — bootstrap es obligatorio.

#### 11.2 En qué orden
1. Platform admin crea tenant setup.
2. Owner acepta invitación.
3. Auth + 2FA.
4. Canales (mailbox).
5. KB seed.
6. Voice Profile.
7. Sandbox test.
8. Activación.
9. Invitación de Operators.

#### 11.3 Qué rompe si este módulo falla
Todo FaberLoom para ese tenant. Sin tenant activo no hay usuarios, canales, agentes ni tasks.

### D12 COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
- **Owner:** todo el wizard y config.
- **Admin (E3+):** config excepto tokens y DPA firmado.
- **Operator:** solo Voice Profile propio.
- **Platform admin:** metadata tenant, no datos del cliente salvo para soporte con audit.
- **Nunca cross-tenant.**

#### 12.2 Qué queda en el audit trail D10
Campos: `tenant_id`, `user_id` (Owner), `actor_role_at_decision=Owner`, action (`tenant.created`, `tenant.activated`, `mailbox.connected`, `document.uploaded`, `user.invited`), `resource_id` (`tenant_id`/`mailbox_id`/`document_id`), `data_class` (N2), `model_provider` (si aplica), `model_id`, `human_gate_required` (false salvo sandbox), `human_approver_id` (Owner), `timestamp`, `sha_chain`.

#### 12.3 Qué restricciones de datos aplican
- N2 default para config tenant.
- N3/N4 hard-block hasta DPA y consentimiento.
- Tokens OAuth cifrados en reposo.
- 2FA obligatorio Owner.
- DPA firmado antes de S10/datos reales.

### D13 DESKTOP vs WEB

#### 13.1 En cuál superficie vive
Web (Next.js) — wizard de bootstrap y Settings tenant.

#### 13.2 Diferencias entre desktop y web
Desktop no tiene bootstrap; es para operación diaria una vez activo el tenant.

#### 13.3 Offline y sincronización
No aplica; bootstrap requiere conexión para OAuth y validaciones.

---

## MÓDULO 2 — Multi-tenant isolation en runtime

MÓDULO: Multi-tenant isolation en runtime
SUPERFICIE: Transversal (backend/API/worker/DB/cache/storage/memory)
SPRINT E1: S1A (RLS + 5 tests cross-tenant) · S8 (resiliencia full)
ROLES: Técnico — Owner/Admin/Operator/Viewer solo se benefician; platform admin/CEO monitorea leaks.
DATA CLASS TÍPICA: N3 (cross-tenant data); N4 si se procesan datos biométricos.

### D1 EXISTENCIA

#### 1.1 Por qué existe
FaberLoom es multi-tenant SaaS. Sin aislamiento runtime, un bug o una query sin `tenant_id` podría devolver datos de un tenant a otro (ej. cotización de MWT visible para Sonepar). Esto es riesgo regulatorio (LGPD/Ley 1581/Ley 25.326) y de negocio catastrófico.

#### 1.2 A quién le duele
- **CEO/Platform admin:** responsable legal de aislamiento.
- **Owner/Admin:** confían en que sus datos no se mezclan.
- **Operator:** no ve datos de otros tenants.
- **Auditor:** verifica RLS y audit trail.

#### 1.3 Cuando aparece
En cada request, job, query, retrieval, upload, LLM call y evento que toca datos tenant-scoped.

### D2 PROPOSITO

#### 2.1 Para qué
Garantizar que un tenant nunca lee, escribe, procesa ni expone datos de otro tenant en runtime.

#### 2.2 Qué valor entrega
Cumple TIER 1 #1 (RLS Postgres por tenant) y mitiga el riesgo top 1 de RLS leak cross-tenant.

#### 2.3 Qué pasa si no existe
Fuga de datos entre tenants, incumplimiento DPA, kill criteria E1 (≥1 incidente privacy → kill).

### D3 CREACION

#### 3.1 Cómo se crea
No es una entidad que se cree desde UI. Se implementa en S1A:

1. Habilitar RLS en todas las tablas con `tenant_id`.
2. Crear policies `USING (tenant_id = current_setting('app.tenant_id')::uuid)`.
3. Implementar middleware que extrae `tenant_slug` del subdomain y setea `app.tenant_id`.
4. Configurar Redis key prefixes por tenant.
5. Configurar Celery headers/payload `tenant_id`.
6. Configurar MinIO paths tenant-scoped.
7. Configurar pgvector `tenant_id` filters.
8. Configurar LiteLLM context scoping.
9. Configurar Letta namespaces per tenant.
10. Escribir 5 tests cross-tenant en CI.

#### 3.2 Quién puede crearlo
Equipo de ingeniería en S1A. No es acción de usuario.

#### 3.3 Qué necesita para crearse
- Schema con `tenant_id` en todas las tablas.
- Subdomain routing funcionando.
- Redis/Celery/MinIO/pgvector/LiteLLM/Letta configurados.

### D4 USO DIARIO

#### 4.1 Cómo se usa en el día a día
Transparente para el usuario. Cada vez que Maria abre Mesa de Control, el frontend manda `x-tenant-id`; el backend aplica RLS; los datos que ve son solo de su tenant.

#### 4.2 Cómo se invoca
Automático por middleware en cada request/job/evento.

#### 4.3 Qué ve el usuario mientras ocurre
Nada visible en operación normal. Si hay leak detectado, el sistema muestra banner de mantenimiento y notifica.

### D5 EDICION

#### 5.1 Cómo se edita
N/A — es infraestructura. Los `feature_flags` per-tenant (`allow_agent_composition`, `allow_tools_in_skills`, etc.) se editan en Settings tenant o DB por platform admin.

#### 5.2 Qué se puede cambiar y qué no
- **Editable:** tenant plan, addons, feature flags.
- **No editable:** políticas RLS, namespaces, key prefixes.

#### 5.3 Qué pasa con lo generado previamente
N/A.

### D6 MOVIMIENTO Y ESTADO

#### 6.1 Cómo se mueve
N/A — no tiene state machine de usuario. El tenant tiene estados (`setup`/`active`/`suspended`) pero el aislamiento runtime es una propiedad continua.

#### 6.2 Qué dispara el movimiento
N/A.

#### 6.3 Quién puede moverlo
N/A.

#### 6.4 Qué se notifica y a quién
- **Leak detectado:** alerta P0 a platform admin/CEO + Auditor + freeze del tenant afectado.
- **Test CI fallido:** bloqueo de merge, alerta equipo.

### D7 OUTPUT

#### 7.1 Qué produce para el usuario
Confianza de que solo ve datos de su tenant.

#### 7.2 Qué produce para el sistema
- Query results filtrados por RLS.
- Redis keys con prefix tenant.
- Celery jobs con `tenant_id` validado.
- MinIO paths scoped.
- Vector search con `tenant_id` filter.
- LiteLLM context sin bleed.
- Letta profiles aislados por namespace.
- Eventos SHA-chain per tenant.
- Audit entries D10 por cada acceso sensible.

#### 7.3 Dónde aparece el output
Invisible para usuario. Logs y métricas en Grafana/Langfuse.

#### 7.4 Qué formato tiene
- PostgreSQL RLS policies.
- Redis keys: `tenant:{tenant_id}:...`
- MinIO paths: `/tenants/{tenant_id}/...`
- Letta namespaces: `mem:agent:{agent_id}:...`

### D8 ERRORES Y EXCEPCIONES

#### 8.1 Qué pasa si falla
- **PostgreSQL RLS deshabilitado:** query sin `tenant_id` podría leak. Mitigación: `FORCE ROW LEVEL SECURITY` + tests CI.
- **Redis sin prefix:** cache compartido. Mitigación: prefix obligatorio en todos los keys.
- **Celery job con tenant_id stale:** el leak más probable en prod — job reusa `tenant_id` de ejecución anterior por cache de worker.
- **MinIO path traversal:** archivo de otro tenant accesible.
- **Vector search sin tenant_id filter:** chunks cross-tenant en retrieval.
- **LiteLLM log bleed:** prompt de tenant A en log de tenant B.
- **Letta namespace leak:** memoria de agente de otro tenant.

#### 8.2 Cómo se recupera
- **RLS:** reforzar policies + `DISCARD ALL` + `with_tenant_session`.
- **Celery stale tenant_id:** wrapper `with_tenant_session` + `DISCARD ALL` al inicio/fin de cada job.
- **Redis:** audit de keys sin prefix.
- **MinIO:** validar path pertenece al tenant del request.
- **Vector:** pre-filtering `tenant_id` obligatorio.
- **LiteLLM:** taggear cada call con `tenant_id`; logs filtrados.
- **Letta:** namespace estricto.

#### 8.3 Quién se entera
- **Usuario:** nada salvo mantenimiento programado.
- **Platform admin/CEO/Auditor:** alerta P0 en caso de leak.
- **Equipo técnico:** alertas CI.

### D9 APRENDIZAJE

#### 9.1 Qué aprende el sistema de este uso
- Patrones de queries que intentan omitir `tenant_id`.
- Frecuencia de `DISCARD ALL`.
- Resultados de tests cross-tenant.

#### 9.2 Cómo mejora con el tiempo
- Tests CI más exhaustivos.
- Pen-test S11.
- Automatización de detección de keys sin prefix.

#### 9.3 Qué feedback da el usuario
N/A.

### D10 ELIMINACION

#### 10.1 Cómo se elimina
N/A — el aislamiento runtime no se elimina.

#### 10.2 Qué pasa con lo que dependía
N/A.

#### 10.3 Es reversible
N/A.

### D11 RELACIONES

#### 11.1 Con qué se relaciona
- **Depende de:** Auth/Tenant/RBAC, PostgreSQL RLS, Redis, Celery, MinIO, pgvector, LiteLLM, Letta.
- **Alimenta a:** todos los módulos (inbound, task, draft, WorkLoom, agent, skill, rutina, workspace).
- **Alternativo:** N/A.

#### 11.2 En qué orden
Debe existir antes que cualquier otro módulo operativo. Es base de S1A.

#### 11.3 Qué rompe si este módulo falla
Todo FaberLoom. Un leak cross-tenant es kill criteria E1.

### D12 COMPLIANCE Y SEGURIDAD

#### 12.1 Quién puede verlo
- **Platform admin/CEO:** config y alertas.
- **Auditor:** logs de acceso cross-tenant.
- **Usuarios tenant:** no ven mecanismos, solo se benefician.

#### 12.2 Qué queda en el audit trail D10
Cualquier cross-tenant access es P0 crítico y se loguea con:
`tenant_id`, `user_id`, `actor_role_at_decision`, `action=cross_tenant.access_attempted`, `resource_id`, `data_class=N3/N4`, `model_provider`, `model_id`, `human_gate_required=false`, `human_approver_id=null`, `timestamp`, `sha_chain`.

#### 12.3 Qué restricciones de datos aplican
- N3/N4 requieren RLS + DPA.
- Cross-tenant access prohibido salvo audit FB-side con 7 checks privacy (SPEC_FB_AUTH_TENANT_RBAC §3.3).
- Hash chain per tenant.

### D13 DESKTOP vs WEB

#### 13.1 En cuál superficie vive
Transversal — aplica a todas las superficies.

#### 13.2 Diferencias
N/A.

#### 13.3 Offline y sincronización
N/A.

---

## PENDIENTES que requieren decisión CEO

1. **[PENDIENTE — ENT_FB_WORK_TYPE_PACK_v1 está en stub]** Confirmar el contenido exacto del seed del work-type pack safety footwear para el paso 5 del wizard.
2. **[PENDIENTE — doc en stub + enmienda E-5 PLB]** Confirmar si el paso 4 (WhatsApp) se mantiene en el wizard de bootstrap dado que la enmienda E-5 del PLB difiere WhatsApp a E3.
3. **[PENDIENTE — PLB §5.B]** Decidir si el DPA se firma electrónicamente dentro del wizard o fuera de línea antes de S10.
4. **[PENDIENTE — SPEC_FB_AUTH_TENANT_RBAC §11]** Definir el email provider para invitaciones y verificación (SendGrid/SES).
5. **[PENDIENTE — SPEC_FB_ROUTINES_v1 stub]** Definir si las rutinas base del tenant se seedean durante el bootstrap o posteriormente en S5/S6.
6. **[PENDIENTE — PLB enmienda E-4]** Confirmar si el wizard de bootstrap en E1 permite invitar Admin/Supervisor/Viewer o solo Owner/Operator.

## CONTRADICCIONES DETECTADAS CON LA KB

1. **Roles E1:** `SCH_FB_FUNCTIONAL_SPEC_v1` y `SPEC_FB_AUTH_TENANT_RBAC` listan 5 roles canónicos (Owner/Admin/Operator/Supervisor/Viewer), pero `PLB_FB_FOUNDATION_BETA_v1` enmienda E-4 establece 2 roles en E1 (Owner, Operator) y 5 roles en E3. La ficha usa los 5 roles canónicos con nota de la enmienda.
2. **WhatsApp en E1:** El prompt del AGENTE_6 menciona paso 4 "conectar WhatsApp (Meta Cloud API)", pero `PLB_FB_FOUNDATION_BETA_v1` enmienda E-5 difiere WhatsApp Business a E3, dejando email-only en E1-E2. Se marca como pendiente.
3. **Work-type pack seed:** El prompt menciona paso 5 seed safety footwear por defecto en E1, pero `ENT_FB_WORK_TYPE_PACK_v1` está en stub; no hay detalle confirmado.
4. **Número de sprints/orden:** `PLB_FB_FOUNDATION_BETA_v1` enmienda E-1 supersede el orden de los 13 sprints por `SPEC_FB_BUILD_SEQUENCE v2.1`. El SPRINT E1 asignado en esta ficha (S1A/S10) se basa en los contenidos técnicos del PLB, no en la secuencia enmendada, porque `SPEC_FB_BUILD_SEQUENCE` no está en la lista de lectura obligatoria.
