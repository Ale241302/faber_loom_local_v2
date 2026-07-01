# SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1 -- Ficha Funcional Aislamiento Multi-tenant (7 capas)
id: SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SPEC_FB_AUTH_TENANT_RBAC_v1.md - SPEC_FB_FUNC_M08_AUTH_SESSION_v1.md - SPEC_FB_FUNC_M17_MEMORY_LETTA_v1.md - SPEC_FB_FUNC_M15_OUTBOX_STREAMS_v1.md - POL_FB_KR_PRIVACY_TIERS_v1.md

---

## CABECERA DE FICHA

MODULO: Aislamiento multi-tenant en runtime (7 capas)
SUPERFICIE: Transversal (DB/cache/worker/storage/vector/LLM/memory)
SPRINT E1: S1A (RLS + 5 tests cross-tenant) -> S8 (resiliencia full)
ROLES QUE LO USAN: Tecnico; usuarios se benefician; platform admin/CEO monitorea leaks
DATA CLASS TIPICA: N3 (cross-tenant data); N4 si hay datos biometricos

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
FaberLoom es multi-tenant. Sin aislamiento runtime, un bug o una query sin
tenant_id podria devolver datos de un tenant a otro (ej. una cotizacion de MWT
visible para otro tenant). Es riesgo regulatorio (LGPD/Ley 1581/Ley 25.326) y de
negocio catastrofico, y kill criteria de E1.

### 1.2 A quien le duele
CEO/Platform admin: responsable legal del aislamiento. Owner/Admin: confian en que
sus datos no se mezclan. Operator: no debe ver datos de otros tenants. Auditor:
verifica RLS y audit.

### 1.3 Cuando aparece
En cada request, job, query, retrieval, upload, LLM call y evento que toca datos
tenant-scoped.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Garantizar que un tenant nunca lee, escribe, procesa ni expone datos de otro
tenant en runtime, en las 7 capas.

### 2.2 Que valor entrega
Cumple TIER 1 (RLS Postgres por tenant) y mitiga el riesgo top 1 de leak
cross-tenant en las 7 superficies de datos.

### 2.3 Que pasa si no existe
Fuga de datos entre tenants, incumplimiento DPA, kill criteria E1 (>=1 incidente
privacy -> kill).

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
No es entidad de UI. Se implementa en S1A, una capa por superficie:
1. PostgreSQL: FORCE ROW LEVEL SECURITY + policies USING (tenant_id =
   current_setting('app.tenant_id')::uuid); SET LOCAL app.tenant_id dentro de
   transaction.atomic().
2. Redis: prefijo obligatorio tenant:{tenant_id}: en todas las keys.
3. Celery: wrapper with_tenant_session + DISCARD ALL fuera de la transaccion,
   tenant_id en el payload, assert al inicio del job.
4. MinIO: paths /tenants/{tenant_id}/... con validacion anti path-traversal.
5. pgvector: indice HNSW por particion de tenant (no global para N2+).
6. LiteLLM: tenant_id en el request context, logs scoped por tenant.
7. Letta: profile separado por tenant, cross-profile bloqueado (M17).
Mas: 5 tests cross-tenant en CI que DEBEN fallar (si pasan, hay leak).

### 3.2 Quien puede crearlo
Equipo de ingenieria en S1A. No es accion de usuario.

### 3.3 Que necesita para crearse
Schema con tenant_id NOT NULL en toda tabla aislable; subdomain routing que
resuelve tenant; Redis/Celery/MinIO/pgvector/LiteLLM/Letta configurados.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
Transparente. Cada vez que Maria abre la Mesa, la sesion (M08) porta el tenant_id;
el middleware setea app.tenant_id; RLS filtra; solo ve datos de su tenant.

### 4.2 Como se invoca
Automatico por middleware en cada request/job/evento. El tenant fluye via context,
NUNCA via headers de cliente manipulables.

### 4.3 Que ve el usuario mientras ocurre
Nada en operacion normal. Si se detecta un leak, banner de mantenimiento y freeze
del tenant afectado.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
N/A -- es infraestructura. Los feature_flags per-tenant (allow_agent_composition,
allow_tools_in_skills, etc.) se editan en Settings tenant o DB por platform admin;
no se filtran a otros tenants.

### 5.2 Que se puede cambiar y que no
Editable: plan, addons, feature flags per-tenant. No editable: las policies RLS,
los namespaces, los key prefixes, la formula de scoping.

### 5.3 Que pasa con lo generado previamente
N/A -- el aislamiento es una propiedad continua, no genera artefactos editables.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
N/A -- no tiene state machine de usuario. El tenant tiene estados (M07) pero el
aislamiento runtime es una propiedad continua. Estado de salud: ok / leak_detected.

### 6.2 Que dispara el movimiento
N/A. La deteccion de leak dispara freeze + alerta.

### 6.3 Quien puede moverlo
N/A. El freeze por leak lo ejecuta el sistema/platform admin.

### 6.4 Que se notifica y a quien
Leak detectado: alerta P0 a platform admin/CEO + auditor + freeze del tenant
afectado. Test cross-tenant de CI que pasa (deberia fallar): bloqueo de merge +
alerta al equipo.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Confianza de que solo ve datos de su tenant.

### 7.2 Que produce para el sistema
Query results filtrados por RLS; Redis keys con prefijo; Celery jobs con tenant_id
validado; MinIO paths scoped; vector search con filtro tenant_id; LiteLLM context
sin bleed; Letta profiles aislados; eventos SHA-chain per tenant; audit por acceso
sensible.

### 7.3 Donde aparece el output
Invisible para el usuario. Logs y metricas en Grafana/Langfuse.

### 7.4 Que formato tiene
Policies RLS; Redis keys tenant:{tenant_id}:...; MinIO paths /tenants/{tenant_id}/
...; Letta namespaces mem:agent:{agent_id}:...; particiones pgvector por tenant.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
PostgreSQL RLS deshabilitado: query sin tenant_id podria leak; mitigacion FORCE
ROW LEVEL SECURITY + tests CI. Redis sin prefix: cache compartido; mitigacion
prefix obligatorio. Celery con tenant_id stale (el leak mas probable en prod: un
worker reusa tenant_id de la ejecucion anterior): mitigacion with_tenant_session +
DISCARD ALL al inicio/fin + assert. MinIO path traversal: validar que el path
pertenece al tenant del request. Vector sin filtro tenant_id: chunks cross-tenant
en retrieval; pre-filtering obligatorio. LiteLLM log bleed: taggear cada call con
tenant_id, logs filtrados. Letta namespace leak: namespace estricto (M17).

### 8.2 Como se recupera
RLS: reforzar policies + DISCARD ALL + with_tenant_session. Celery: wrapper +
DISCARD ALL. Redis/MinIO/Vector/LiteLLM/Letta: las mitigaciones de 8.1. Ante leak
confirmado: freeze del tenant + investigacion forense + notificacion regulatoria
si aplica.

### 8.3 Quien se entera
Usuario: nada salvo mantenimiento. Platform admin/CEO/auditor: alerta P0 ante leak.
Equipo tecnico: alertas de CI.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Patrones de queries que intentan omitir tenant_id; frecuencia de DISCARD ALL;
resultados de los tests cross-tenant.

### 9.2 Como mejora con el tiempo
Tests CI mas exhaustivos; pen-test (S11); deteccion automatica de keys sin prefix.

### 9.3 Que feedback da el usuario
N/A.

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
N/A -- el aislamiento runtime no se elimina ni se desactiva.

### 10.2 Que pasa con lo que dependia
N/A.

### 10.3 Es reversible
N/A.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Depende de: Auth/Tenant/RBAC (M08, M09), PostgreSQL, Redis, Celery, MinIO,
pgvector, LiteLLM, Letta (M17). Alimenta a: TODOS los modulos (inbound, task,
draft, WorkLoom, agente, skill, rutina, eventing M15, memoria M17). Alternativo:
N/A.

### 11.2 En que orden
Debe existir antes que cualquier modulo operativo. Es base de S1A. M08 porta el
tenant_id que este modulo usa para aislar.

### 11.3 Que rompe si este modulo falla
Todo FaberLoom. Un leak cross-tenant es kill criteria E1.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Platform admin/CEO: config y alertas. Auditor: logs de acceso cross-tenant.
Usuarios del tenant: no ven los mecanismos, solo se benefician.

### 12.2 Que queda en el audit trail D10
Cualquier intento cross-tenant es P0 y se loguea: tenant_id, user_id,
actor_role_at_decision, action=cross_tenant.access_attempted, resource_id,
data_class (N3/N4), model_provider, model_id, human_gate_required=false,
human_approver_id=null, timestamp, sha_chain.

### 12.3 Que restricciones de datos aplican
tenant_id NOT NULL en toda tabla aislable; RLS source of truth; tenant via context
nunca via headers de cliente; overrides per-tenant en su propio scope; N3/N4
requieren RLS + DPA; cross-tenant prohibido salvo audit FB-side con 7 checks
privacy; hash chain per tenant; HNSW por particion para N2+.

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Transversal -- aplica a todas las superficies de datos.

### 13.2 Diferencias entre desktop y web
N/A en el mecanismo; tanto desktop como web portan el tenant_id en la sesion (M08)
y reciben solo eventos/datos de su tenant (M15).

### 13.3 Offline y sincronizacion
El aislamiento es server-side; offline el cliente solo tiene datos de su tenant ya
recibidos. La reconexion (M19) revalida el tenant de la sesion antes de
sincronizar; no se mezcla estado de tenants en el cliente.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE] Confirmar los 5 tests cross-tenant exactos del CI (que escenario
   cubre cada uno).
2. [PENDIENTE -- POL_FB_KR_PRIVACY_TIERS_v1] Confirmar el umbral N2+ a partir del
   cual pgvector exige particion por tenant (no global).
3. [PENDIENTE -- SPEC_FB_AUTH_TENANT_RBAC Sec.3.3] Confirmar los 7 checks privacy
   del audit FB-side para acceso cross-tenant excepcional.

## CONTRADICCIONES DETECTADAS CON LA KB

1. Sin contradicciones nuevas detectadas. Las 7 capas son consistentes con TIER 1
   #1 y con las reglas multi-tenant del CLAUDE.md (RLS source of truth, tenant via
   context).

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones del aislamiento
  multi-tenant 7 capas (PostgreSQL RLS, Redis, Celery, MinIO, pgvector, LiteLLM,
  Letta) + 5 tests cross-tenant en CI que deben fallar.
