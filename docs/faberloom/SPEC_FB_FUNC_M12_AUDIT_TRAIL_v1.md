# SPEC_FB_FUNC_M12_AUDIT_TRAIL_v1 -- Ficha Funcional Audit Trail D10
id: SPEC_FB_FUNC_M12_AUDIT_TRAIL_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE -- 2026-06-24
aprobador: CEO
aplica_a: [FaberLoom]
relacionado: SCH_FB_FUNCTIONAL_SPEC_v1.md - SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1.md - SPEC_FB_FUNC_M11_D9_POLICY_GATE_v1.md - SPEC_FB_FUNC_M13_DRAFT_HITL_v1.md - SPEC_FB_FUNC_M16_TENANT_ISOLATION_v1.md

---

## CABECERA DE FICHA

MODULO: Audit trail D10 (hash chain inmutable)
SUPERFICIE: Backend (transversal) / Web (export compliance)
SPRINT E1: S1B (audit append-only + hash chain)
ROLES QUE LO USAN: Owner/Admin (consulta/export), Auditor; Operator/Viewer ven su scope
DATA CLASS TIPICA: N2 (metadata de decisiones); referencia a casos de cualquier clase

---

## DIMENSION 1 -- EXISTENCIA

### 1.1 Por que existe
Cada decision de un agente o de un humano sobre datos del tenant debe ser
reconstruible y a prueba de manipulacion. Sin un audit inmutable, ante una
disputa comercial o una auditoria regulatoria no se puede demostrar quien decidio
que, con que modelo, sobre que dato. El Owner lo siente el dia que un cliente
reclama una cotizacion: necesita evidencia firme, no logs editables.

### 1.2 A quien le duele
Owner/Admin: deben poder demostrar trazabilidad. Auditor: verifica la integridad
de la cadena. Platform admin/CEO: responde por compliance. Operator: su decision
queda registrada (proteccion y responsabilidad).

### 1.3 Cuando aparece
En cada accion auditable: clasificacion, gate de politica, generacion de draft,
aprobacion/edicion/rechazo humano, envio, cambios de rol, conexiones de canal.

---

## DIMENSION 2 -- PROPOSITO

### 2.1 Para que
Registrar cada accion sensible en una cadena de hash inmutable por tenant, append
-only, exportable para compliance.

### 2.2 Que valor entrega
Trazabilidad a prueba de manipulacion; deteccion de alteracion (ruptura de
cadena); evidencia para disputas y auditorias; soporte al evidence bundle de
cotizaciones (SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1).

### 2.3 Que pasa si no existe
Las decisiones serian logs editables sin garantia de integridad; imposible probar
quien hizo que; incumplimiento de requisitos de auditabilidad.

---

## DIMENSION 3 -- CREACION

### 3.1 Como se crea
El audit no se crea por UI: cada accion auditable escribe una entrada. Por
entrada se calcula sha_chain_curr = hash(payload + sha_chain_prev), encadenando
por chain_id = tenant_id + audit_domain. Campos canonicos de la entrada:
tenant_id, case_id, action_id, data_class, task_type, model_provider, model_id,
model_version, orchestrator_policy_pool_hash, prompt_hash, output_hash,
human_gate_required, human_approver_id, sha_chain_prev, sha_chain_curr, seq_no,
chain_id.

### 3.2 Quien puede crearlo
El sistema (app) inserta entradas. Nadie las crea/edita manualmente. El app role
de DB tiene INSERT pero NO UPDATE/DELETE sobre la tabla audit.

### 3.3 Que necesita para crearse
La accion fuente y su contexto (caso, modelo, hashes); el sha_chain_prev del
ultimo nodo del chain_id; el seq_no siguiente.

---

## DIMENSION 4 -- USO DIARIO

### 4.1 Como se usa en el dia a dia
Transparente en la operacion: se escribe sola. Owner/Admin/Auditor la consultan
cuando investigan un caso o preparan un export. Un job diario valida la integridad
de cada hash chain.

### 4.2 Como se invoca
Escritura: automatica por cada accion auditable. Lectura: vista de audit (web),
filtrable por caso/fecha/actor. Export: boton de export per-tenant.

### 4.3 Que ve el usuario mientras ocurre
Inicial: lista cronologica de entradas con caso, actor, accion, modelo, timestamp.
En proceso (export): spinner + barra de progreso. Completado: archivo de export +
reporte de validacion de cadena (OK / ruptura detectada). Error: badge si la
validacion diaria detecta una ruptura.

---

## DIMENSION 5 -- EDICION

### 5.1 Como se edita
No se edita. El audit es append-only. Una correccion se modela como una NUEVA
entrada que referencia la anterior, nunca como un UPDATE.

### 5.2 Que se puede cambiar y que no
Nada es editable. Triggers BEFORE UPDATE/DELETE fallan la operacion. El app role
carece de UPDATE/DELETE. Inmutable por diseno.

### 5.3 Que pasa con lo generado previamente
Permanece intacto para siempre. Cualquier intento de alterar una entrada rompe la
cadena (sha_chain) y lo detecta el job de validacion.

---

## DIMENSION 6 -- MOVIMIENTO Y ESTADO

### 6.1 Como se mueve
No tiene state machine de usuario: cada entrada es un nodo terminal en la cadena.
La cadena solo crece (append-only). Estado de salud del chain: `valid` /
`broken` (detectado por validacion).

### 6.2 Que dispara el movimiento
Cada accion auditable agrega un nodo. El job diario evalua la salud de la cadena.

### 6.3 Quien puede moverlo
Solo el sistema agrega nodos. Nadie puede reordenar, editar ni borrar.

### 6.4 Que se notifica y a quien
Ruptura de cadena detectada por el job diario: alerta P0 al Owner + platform
admin + auditor (posible manipulacion o corrupcion). Export listo: notificacion al
solicitante.

---

## DIMENSION 7 -- OUTPUT

### 7.1 Que produce para el usuario
Vista de audit consultable y un export per-tenant para compliance, con reporte de
validacion de integridad.

### 7.2 Que produce para el sistema
Fila append-only en la tabla audit con los 18 campos canonicos y el sha_chain;
resultado del job diario de validacion; el evidence bundle de cotizaciones se
ancla a esta cadena (SCH_FB_QUOTE_EVIDENCE_BUNDLE_v1).

### 7.3 Donde aparece el output
Vista de audit (web); archivo de export (CSV/JSON/firmado); reporte de validacion;
referencia desde el evidence bundle.

### 7.4 Que formato tiene
Entrada JSON/row con los 18 campos; sha_chain_prev/curr; export en formato
estandar para auditores [PENDIENTE -- definir formato exacto]; firma opcional del
export.

---

## DIMENSION 8 -- ERRORES Y EXCEPCIONES

### 8.1 Que pasa si falla
Intento de UPDATE/DELETE: la operacion falla por trigger (defensa en profundidad)
y por el app role sin esos privilegios. Ruptura de cadena detectada: estado
`broken`, alerta P0, congela exports hasta investigar. Falla al escribir una
entrada (DB caida): la accion fuente debe fallar-closed o reintentar via outbox
(M15) para no perder el registro; nunca se completa una accion auditable sin su
entrada de audit.

### 8.2 Como se recupera
Ruptura: investigacion forense (identificar el seq_no donde rompe, comparar con
backup); no se "repara" reescribiendo (eso seria manipular) -- se documenta el
incidente y se determina causa. Escritura fallida: el outbox reintenta la entrada;
si el outbox tampoco persiste, la accion fuente se revierte.

### 8.3 Quien se entera
Owner/platform admin/auditor: ruptura (P0). Equipo tecnico: fallos de escritura.
Langfuse/Grafana: metricas del job de validacion.

---

## DIMENSION 9 -- APRENDIZAJE

### 9.1 Que aprende el sistema de este uso
Volumen de acciones auditables por tipo; patrones de acceso al audit; frecuencia
de exports.

### 9.2 Como mejora con el tiempo
Optimizacion de indices de consulta; particionado por audit_domain; el contenido
de las entradas no se "aprende" (es registro factual inmutable).

### 9.3 Que feedback da el usuario
N/A directo. Indirecto: el auditor reporta si faltan campos para su revision ->
se agregan en versiones futuras del schema (sin tocar entradas pasadas).

---

## DIMENSION 10 -- ELIMINACION

### 10.1 Como se elimina
No se elimina. El audit se conserva segun la politica de retencion del tenant
(POL_DATA_CLASSIFICATION). Ni siquiera al cancelar un tenant se borra durante el
periodo de retencion legal.

### 10.2 Que pasa con lo que dependia
N/A -- el audit es el registro final; otros modulos dependen de el, no al reves.

### 10.3 Es reversible
N/A -- append-only e inmutable por diseno.

---

## DIMENSION 11 -- RELACIONES

### 11.1 Con que se relaciona
Recibe de: todos los modulos que generan acciones auditables (M07-M16). Alimenta
a: vista de audit, export de compliance, evidence bundle de cotizaciones, M16
(aislamiento: chain por tenant). Depende de: outbox (M15) para no perder
escrituras; M16 (RLS scoping).

### 11.2 En que orden
Accion (cualquier modulo) -> escritura de entrada audit (misma transaccion /
outbox) -> hash chain -> validacion diaria -> export bajo demanda.

### 11.3 Que rompe si este modulo falla
Sin audit no hay trazabilidad ni evidencia; el evidence bundle de cotizaciones
pierde su ancla; compliance no es demostrable.

---

## DIMENSION 12 -- COMPLIANCE Y SEGURIDAD

### 12.1 Quien puede verlo
Owner/Admin: el audit del tenant (Admin segun matriz M09, pendiente de scope).
Auditor: cadena completa + validacion. Operator/Viewer: solo el audit de sus
propias acciones. Nunca cross-tenant: chain_id incluye tenant_id.

### 12.2 Que queda en el audit trail D10
Los 18 campos canonicos: tenant_id, case_id, action_id, data_class, task_type,
model_provider, model_id, model_version, orchestrator_policy_pool_hash,
prompt_hash, output_hash, human_gate_required, human_approver_id, sha_chain_prev,
sha_chain_curr, seq_no, chain_id (+ timestamp). Cifras o contenido sensible NO se
copian en claro: se guardan hashes (prompt_hash, output_hash).

### 12.3 Que restricciones de datos aplican
Append-only (triggers + app role sin UPDATE/DELETE); hash chain por tenant_id +
audit_domain; export per-tenant aislado; retencion segun politica; los hashes
evitan exponer N3/N4 en claro dentro del audit. Acceso filtrado por RLS (M16).

---

## DIMENSION 13 -- DESKTOP vs WEB

### 13.1 En cual superficie vive
Backend (escritura, transversal). Web: consulta y export de compliance
(Owner/Admin/Auditor). Desktop: el Operator ve el audit de sus propias acciones.

### 13.2 Diferencias entre desktop y web
Web: consulta completa, export, reporte de validacion. Desktop: vista acotada al
scope del Operator, sin export.

### 13.3 Offline y sincronizacion
La escritura es server-side; si una accion ocurre con conectividad intermitente,
su entrada de audit se persiste via outbox (M15) al reconectar, preservando el
orden (seq_no) y la cadena. No se generan entradas de audit "offline" en cliente.

---

## PENDIENTES que requieren decision CEO

1. [PENDIENTE] Definir el formato exacto del export para auditores externos
   (CSV/JSON firmado) -- coincide con pendiente del evidence bundle v1.1.
2. [PENDIENTE -- M09] Confirmar si Admin ve el audit completo del tenant o solo su
   scope (la matriz lo pone en R).
3. [PENDIENTE -- POL_DATA_CLASSIFICATION] Definir el periodo de retencion legal por
   jurisdiccion LATAM.

## CONTRADICCIONES DETECTADAS CON LA KB

1. Campos de audit: el set de la DIMENSION 12.2 del SCH_FB_FUNCTIONAL_SPEC
   (tenant_id, user_id, actor_role_at_decision, action, resource_id, data_class,
   model_provider, model_id, human_gate_required, human_approver_id, timestamp,
   sha_chain) y el set canonico de 18 campos de esta ficha (con action_id,
   model_version, orchestrator_policy_pool_hash, prompt_hash, output_hash,
   sha_chain_prev/curr, seq_no, chain_id) difieren en granularidad. No se resuelve:
   se documenta que el set de 18 es superset del set del SCH; requiere decision CEO
   sobre cual es el canonico final.

---

Changelog:
- v1.0 (2026-06-24): Creacion. Ficha funcional 13 dimensiones del Audit Trail D10.
  Hash chain por tenant_id+audit_domain, 18 campos canonicos, append-only
  (triggers + app role), job diario de validacion, export per-tenant.
