# PLAN_TRABAJO_E2_FUGU_v3 — Plan de trabajo ejecutable Etapa 2

id: PLAN_TRABAJO_E2_FUGU_v3  
version: 3.0  
status: DRAFT EJECUTABLE  
fecha: 2026-07-06  
autor: Fugu — auditor y arquitecto senior  
base auditada: PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1 v1.6  
alcance: FaberLoom/SpaceLoom Etapa 2 — multi-usuario interno MWT  

---

## 1. Resumen ejecutivo

Etapa 2 convierte FaberLoom/SpaceLoom de una app operativa de usuario único a una instancia interna compartida para MWT: usuarios reales, roles AM/curador/CEO, WorkLoom compartido, KB compartida con sellado, routing gestionado multi-proveedor/local, ledger de costos, ciclo ambiental propositivo e ingesta universal con MinIO.

El camino recomendado es incremental y gateado: primero activar identidad/contexto/auditoría y migrar a Postgres+RLS; luego operar en servidor compartido con datos reales; después introducir roles, HITL multi-user y correo real; recién entonces ampliar KB, routing auto, entidad viva e ingesta universal. El calendario honesto se mantiene: 7–9 semanas para dogfood multi-usuario útil, 14–18 semanas para Etapa 2 completa con QA de sellado, canaries y objetos.

Los riesgos críticos son P0: fuga cross-workspace/cross-rol/cross-tenant, acciones irreversibles sin doble confirmación, injection por contenido compartido, exfiltración de archivos a modelos cloud en workspaces solo-local, cadenas auto sin techo, y contaminación del gold loop entre AMs. Ningún hito posterior debe avanzar si falla el gate de aislamiento o HITL. La recomendación principal es tratar E2-0/E2-1 como una migración de plataforma, no como feature work: primero base transaccional, RLS, Context obligatorio, sesiones robustas, auditoría persistente, tenant canario y pruebas de regresión.

---

## 2. Hallazgos de auditoría

### 2.1 Fortalezas

1. **Secuencia correcta de activación de costuras.** El plan no intenta reescribir el núcleo: activa "'`tenant_id`, `user_id`, `actor_id`, `Context`, `AuditWriter`, router abstraído y versionado de rutinas sobre el runtime FastAPI existente.
2. **Decisiones bloqueantes resueltas.** Postgres+RLS, auth local, despliegue en el host actual, MinIO dedicada, prefijo por workspace y catálogo de capacidades por política eliminan ambigüedades mayores.
3. **Modelo de riesgo P0 explícito.** El plan conserva los invariantes de Etapa 1: irreversibles con HITL, no confiar en contenido ingerido, no fuga entre espacios y no inventar datos sin fuente.
4. **Tenant canario permanente.** Es una buena decisión: con un solo tenant, las pruebas de aislamiento son triviales; el canario fuerza evidencia real de scoping y RLS.
5. **Dogfood temprano.** E2-0→E2-2 produce valor antes de completar toda la ambición multimodal. Esto reduce riesgo de construir infraestructura que el equipo no adopta.
6. **Atribución y ledger del modo auto.** Mostrar solo el modelo final en UI pero conservar cadena completa en evidencia/ledger equilibra UX y auditabilidad.

### 2.2 Gaps técnicos y operativos

1. **Migración SQLite→Postgres+RLS puede ser más grande que E2-0/E2-1.** No basta copiar datos: hay que definir tipos, constraints, defaults, índices, RLS, usuario de app, migraciones repetibles, rollback y verificación por conteos y muestras.
2. **Dos sistemas de auth/foundation deben converger funcionalmente.** El plan decide auth local, pero debe aclarar una única fuente de sesión/usuario para backend, Foundation y frontend. El riesgo no es la decisión, sino dejar puentes temporales vivos.
3. **Context obligatorio necesita enforcement, no convención.** Toda query debe recibir `Context(workspace_id, tenant_id, user_id)`. Se recomienda bloqueo por tests, wrappers de repositorio y lint/checks internos donde aplique.
4. **RLS con un solo tenant real requiere disciplina.** El canario debe existir desde E2-0/E2-1, no esperar a E2-3, porque la migración a Postgres es cuando se debe probar que la DB también bloquea.
5. **MinIO y objetos añaden un segundo plano de autorización.** El sellado no puede depender solo de prefijos bien formados; la API debe validar ownership antes de emitir presigned URLs y registrar auditoría por objeto.
6. **Modo auto aumenta superficie de injection.** El dispatcher no debe recibir instrucciones confiables desde documentos/KB como si fueran sistema. Cada paso debe etiquetar origen, capacidad, presupuesto, workspace allowlist y tipo de acción.
7. **Entidad viva puede convertirse en orquestador oculto.** El plan lo limita bien, pero faltan métricas operativas: volumen máximo de propuestas, deduplicación, backoff y razón auditable de cada item.
8. **Correo real requiere runbook.** Rotación IMAP, app-passwords por AM, prueba real y rollback deben estar documentados antes de activar el flag.

### 2.3 Ambigüedades a cerrar antes de build

- Definir matriz de permisos mínima por rol para WorkLoom, KB, gold loop, rutinas, routing keys, budgets y objetos.
- Definir qué tablas pasan primero a Postgres y cuáles quedan temporalmente en SQLite, si existe transición; recomendación: evitar doble escritura prolongada.
- Definir nomenclatura y semántica de estados de inbox compartido, gold candidate, routine run y objetos.
- Definir presupuesto diario inicial real por usuario/equipo y política de bloqueo al agotarse.
- Definir lista inicial de tipos soportados en ingesta universal y cuáles quedan como “almacenado pero no procesado”.

### 2.4 Conflictos con el stack actual

- Frontend React UMD/Babel permite avanzar rápido, pero E2-4/E2-6 crearán UI compleja; conviene mantener componentes simples y no iniciar migración de build system dentro de Etapa 2 salvo bloqueo real.
- SQLite principal ya no es suficiente para concurrencia, RLS ni auditoría multi-user; debe quedar fuera del camino crítico luego de E2-1.
- Pywebview sigue válido para escritorio interno, pero la fuente de verdad de sesión debe ser web/API; no debe tener bypass especial.

---

## 3. Plan de trabajo desglosado por hito

## E2-0 — Activar costuras + higiene E1

### Objetivo
Preparar el runtime único `app/` para multi-usuario: Context real, audit por actor, auth local coherente, migración base a Postgres planificada/ejecutable, higiene heredada de E1 y pruebas de regresión de invariantes P0.

### Tareas y subtareas
1. **Cerrar higiene documental/mecánica heredada.**
   - Recuperar y versionar `harness/prompts/sl1b_dogfood_prompts.json`.
   - Crear documento de promoción del spike a base E2.
   - Crear lessons learned E1 y aplicar licencia FSL 1.1.
   - Archivar SPINE Django como contrato de referencia, no runtime vivo.
2. **Unificar identidad runtime.**
   - Definir modelo operativo de usuario local, sesión y rol inicial.
   - Eliminar dependencias funcionales de tokens legacy en UI.
   - Asegurar que backend, Foundation y frontend resuelven el mismo usuario.
3. **Activar `Context`.**
   - Hacer que rutas y servicios reciban `workspace_id`, `tenant_id`, `user_id`.
   - Auditar mentalmente familias de queries: workspaces, KB, inbox, routine runs, audit, router, email.
   - Agregar checks de regresión para queries sin scope.
4. **AuditWriter persistente.**
   - Mantener `audit.jsonl` como compatibilidad y agregar escritura a tabla.
   - Registrar actor, rol al momento, workspace, tenant, acción, evidencia y correlación.
5. **Plan/migración SQLite→Postgres.**
   - Definir esquema Postgres compatible con costuras contract-first.
   - Preparar migración repetible con verificación de conteos por tabla.
   - Definir rollback y backup previo.
6. **Tenant canario temprano.**
   - Sembrar tenant `canary` con filas reconocibles donde aplique.
   - Marcarlo fuera de dashboards/gold loop.
7. **Pruebas P0 base.**
   - Re-correr suite E1 esperada.
   - Agregar regresiones para Context, audit por actor, sesión y canario básico.

### Archivos/componentes
`app/src/db.py`, `app/src/context.py`, `app/src/api.py`, `app/src/foundation/*`, `app/src/audit*`, `app/tests/*`, `harness/prompts/sl1b_dogfood_prompts.json`, `Plan/*`, `LICENSE`, scripts de migración.

### Responsable
Dev: implementación y pruebas. CEO: ratificar FSL/promoción si requiere aprobación. Ops: validar backup antes de migración.

### Talla
M.

### Dependencias
Etapa 1 cerrada; decisión de runtime único; acceso a entorno local y VPS para validar migración cuando llegue E2-1.

### Criterio de aceptación / DoD
La app E1 funciona igual con usuario autenticado; cada acción relevante deja auditoría con actor/tenant/workspace; ninguna query crítica opera sin Context; hygiene E1 cerrada; migración Postgres ensayada con conteos; canario disponible para pruebas.

### Riesgo principal
Dejar auth/context en estado híbrido, generando bypasses o scopes inconsistentes.

---

## E2-1 — Servidor compartido + Postgres operativo

### Objetivo
Desplegar la instancia interna compartida en el host definido, con Postgres+RLS propio, datos reales MWT, concurrencia básica y operación segura detrás de mwt-nginx.

### Tareas y subtareas
1. **Infra Postgres propia.**
   - Agregar servicio Postgres al compose `faber_loom` con puerto 5435.
   - Definir variables secretas no versionadas.
   - Configurar backup y restore smoke test.
2. **Migración productiva.**
   - Tomar backup SQLite y estado previo.
   - Ejecutar migración SQLite→Postgres.
   - Verificar conteos por tabla, constraints, índices y datos críticos.
3. **RLS y usuario de app.**
   - Activar policies por tenant/workspace según tabla.
   - Configurar usuario de app sin privilegios de owner.
   - Ejecutar pruebas MWT vs canario en ambas direcciones.
4. **Concurrencia multi-usuario.**
   - Crear usuarios internos iniciales.
   - Validar sesiones simultáneas, edición de workspaces y operaciones de inbox/KB sin pisarse.
5. **Datos reales MWT en KB.**
   - Cargar catálogo, listas de precios, fichas y fuentes reales.
   - Verificar citas con un AM.
6. **Observabilidad mínima.**
   - Logs de API, auditoría, errores DB, healthcheck y espacio en disco.
   - Runbook de backup/restore y despliegue.

### Archivos/componentes
`docker-compose*`, `.env` no versionado, `app/src/db.py`, migraciones, `app/src/context.py`, `app/src/foundation/*`, `app/src/kb*`, `app/tests/*`, documentación de operación.

### Responsable
Dev: migración/app. Ops: despliegue, DNS/proxy/backups. CEO/AM: validar datos reales.

### Talla
L.

### Dependencias
E2-0 completo; acceso al host 187.77.218.102; secretos definidos.

### Criterio de aceptación / DoD
2+ usuarios trabajan simultáneamente sin colisiones; Postgres+RLS es fuente de verdad; canario no filtra filas; KB real cargada y citada; restore smoke test documentado.

### Riesgo principal
RLS mal aplicado o usuario de app con permisos excesivos que convierten el aislamiento en decorativo.

---

## E2-2 — Roles + HITL multi-user + WorkLoom compartido

### Objetivo
Introducir roles reales, cola compartida, asignación, aprobación cruzada, segundo gate de gold y correo real con HITL intacto.

### Tareas y subtareas
1. **Matriz de permisos.**
   - Definir acciones por AM, curador, CEO y admin técnico.
   - Mapear permisos a WorkLoom, KB, rutinas, correo, gold y routing.
2. **Roles y auditoría de decisión.**
   - Persistir `actor_role_at_decision` en acciones relevantes.
   - Asegurar `approved_by` real, no constante.
3. **WorkLoom compartido.**
   - Agregar asignación, urgencia, estados de equipo, reasignación y filtros.
   - Evitar que cambios concurrentes pisen estados.
4. **HITL multi-user.**
   - Implementar aprobación por B de draft creado por A.
   - Mantener doble confirmación para enviar/borrar.
   - Registrar evidencia de decisión.
5. **Segundo gate gold.**
   - Impedir que quien aprueba draft promueva el mismo dato duro a gold.
   - Registrar comité/curador cuando aplique.
6. **Correo real.**
   - Rotar credenciales IMAP Kimi Work.
   - Activar flag de email en instancia compartida.
   - Onboarding por AM con app-password propio.
   - Ejecutar caso real: recibir → draft → aprobar → enviar.
7. **Gate de adopción.**
   - Medir N=10 casos reales voluntarios en 14 días por usuario activo.
   - Registrar fricciones que obliguen a salir de la app.

### Archivos/componentes
`app/src/foundation/*`, `app/src/api.py`, `app/src/email*`, `app/src/inbox*`, `app/src/kb*`, `app/static/js/app.jsx`, `app/static/css/main.css`, `app/tests/*`.

### Responsable
Dev: roles/HITL/UI/tests. Ops: credenciales y flag. CEO/AM/curador: pruebas reales y decisiones de permisos.

### Talla
M.

### Dependencias
E2-1; usuarios reales; correo disponible.

### Criterio de aceptación / DoD
Draft creado por A aprobado por B con rol registrado; enviar/borrar exige doble confirmación; WorkLoom compartido funciona; un correo real E2E completado; canaries multi-user de injection pasan; adopción inicial medible.

### Riesgo principal
Relajar HITL al introducir colaboración o permitir que contenido compartido dispare acciones en sesión de otro usuario.

---

## E2-3 — KB compartida + sellado por rol/workspace

### Objetivo
Construir KB organizacional con herencia org→equipo→workspace, sellado por rol y workspace, tenant canario permanente y gold loop capa 2.

### Tareas y subtareas
1. **Modelo de herencia KB.**
   - Definir niveles org, equipo, workspace y reglas de precedencia.
   - Asegurar que citas y fuente por campo sobreviven a la herencia.
2. **Autorización por rol/workspace.**
   - Aplicar filtros en servicios y RLS donde corresponda.
   - Crear pruebas cross-rol, cross-workspace y cross-tenant.
3. **Tenant canario completo.**
   - Sembrar filas `CANARY_` en todas las tablas Foundation y tablas nuevas relevantes.
   - Ejecutar M16 bidireccional en cada despliegue.
4. **Gold loop L2→L3.**
   - Estados candidate, active, rejected, L3 pending.
   - Enforce k-anon >=5 para promoción cruzada.
   - Comité/curador obligatorio para L3.
5. **Stale/source checks.**
   - Mantener source_to_field_check y stale_data_block.
   - Generar WorkLoom items para fuentes vencidas, sin auto-promoción.
6. **QA de fuga.**
   - Dataset controlado con MWT, workspace A/B y canario.
   - Pruebas negativas: usuario sin rol, workspace equivocado, tenant equivocado.

### Archivos/componentes
`app/src/kb*`, `app/src/context.py`, `app/src/db.py`, `app/src/foundation/*`, `app/src/api.py`, `app/static/js/app.jsx`, `app/tests/*`, scripts de seed canario.

### Responsable
Dev: implementación y QA. CEO/curador: política de gold. AMs: validar utilidad/citas.

### Talla
L.

### Dependencias
E2-2 para roles; E2-1 para Postgres/RLS.

### Criterio de aceptación / DoD
Fuga cross-rol, cross-workspace y cross-tenant = 0; M16 MWT↔canario verde en ambas direcciones; gold L3 requiere segundo gate y k-anon; citas/fuentes se mantienen.

### Riesgo principal
Asumir que el sellado de Etapa 1 local equivale a autorización multi-user real.

---

## E2-4 — Routing gestionado + catálogo + modo auto

### Objetivo
Pasar de BYO-key/manual mínimo a routing administrado con catálogo multi-proveedor/local, budgets, ledger, selector manual y dispatcher auto con guardrails.

### Tareas y subtareas
1. **Catálogo de modelos.**
   - Registrar proveedores cloud y Ollama local.
   - Capturar tags de capacidad, costo, latencia esperada, allowlist y estado.
   - No inferir capacidades no declaradas.
2. **Gestión de keys y budgets.**
   - Guardar keys administradas de forma segura.
   - Budgets por usuario/equipo/workspace y ciclo ambiental.
   - Política de bloqueo al agotar presupuesto.
3. **Ledger de costos.**
   - Registrar request, pasos, modelo, proveedor, tokens/costo estimado, actor, workspace y evidencia.
   - Reportes mínimos para admin.
4. **Modo manual en chat.**
   - Selector por mensaje o workspace.
   - Mostrar disponibilidad según allowlist/capacidad.
5. **Dispatcher modo auto.**
   - Clasificar intención y descomponer tareas.
   - Enforce max pasos, budget cap y allowlist por workspace.
   - Encadenar outputs sin permitir acciones irreversibles.
6. **Atribución auditada.**
   - UI muestra modelo final del entregable.
   - Evidence/ledger conserva cadena completa.
7. **Caso canónico.**
   - PDF → resumen por modelo barato → imagen por modelo `image_gen`.
   - Si no hay modelo de imagen registrado, respuesta honesta de capacidad faltante.

### Archivos/componentes
`app/src/router/engine.py`, `app/src/router/*`, `app/src/api.py`, `app/src/db.py`, `app/static/js/app.jsx`, `app/static/css/main.css`, `app/tests/*`, migraciones/ledger.

### Responsable
Dev: router/UI/ledger/tests. CEO/admin: alta de proveedores, budgets y allowlists. Ops: secretos y modelos locales.

### Talla
L.

### Dependencias
E2-1 para servidor/budgets; puede solaparse parcialmente con E2-3, pero el modo auto no debe liberar antes de gates de aislamiento.

### Criterio de aceptación / DoD
Caso canónico E2E pasa; selector manual usable; ledger muestra cadena completa; UI muestra modelo final; max pasos/budget/allowlist son obligatorios; no hay exfiltración en workspace solo-local.

### Riesgo principal
Dispatcher tratado como agente confiable con capacidad de encadenar costos, herramientas o exfiltración sin límites duros.

---

## E2-5 — Entidad viva / ciclo ambiental

### Objetivo
Agregar ciclo proactivo acotado que revisa workspaces, inbox y KB; detecta problemas; propone items en WorkLoom; nunca ejecuta irreversibles.

### Tareas y subtareas
1. **Scheduler de gobierno.**
   - Ciclo global máximo cada 30 min.
   - Workspace máximo 1 revisión/hora.
   - Ventana 06:00–22:00 America/Bogota con excepciones críticas.
2. **Kill switch y configuración.**
   - Toggle global y por workspace.
   - Budget propio: 5% del diario global por defecto.
   - Tools allowlist solo lectura + creación de items.
3. **Detectores iniciales.**
   - Correos sin draft.
   - Fuentes vencidas.
   - HITL estancado.
   - Rutinas fallidas.
   - Budget por agotarse.
   - Gold candidates sin revisar.
4. **Creación de propuestas WorkLoom.**
   - Deduplicación y prioridad.
   - Evidencia obligatoria.
   - Acción sugerida reversible o revisión humana.
5. **Auditoría y métricas.**
   - Registrar ciclo, workspace, costo, detectores corridos, propuestas y descartes.
   - Métrica: al menos 1 propuesta útil aceptada/semana.
6. **Pruebas de seguridad.**
   - Canaries de contenido compartido.
   - Pruebas de que no puede enviar/borrar/promover gold sin gate.

### Archivos/componentes
`app/src/foundation/*`, `app/src/inbox*`, `app/src/kb*`, `app/src/router/*`, `app/src/api.py`, `app/static/js/app.jsx`, `app/tests/*`, scheduler/config.

### Responsable
Dev: scheduler/detectores/UI/tests. CEO/AM/curador: evaluar utilidad. Ops: monitoreo y kill switch.

### Talla
L.

### Dependencias
E2-2 roles/WorkLoom; E2-3 KB sellada; E2-4 recomendado para budget/ledger completo.

### Criterio de aceptación / DoD
La entidad detecta y propone con evidencia; 0 acciones irreversibles; kill switch probado; presupuesto respetado; al menos una propuesta útil aceptada por semana durante dogfood.

### Riesgo principal
Que el ciclo ambiental se convierta en orquestador autónomo con permisos efectivos superiores a los usuarios.

---

## E2-6 — Ingesta universal + MinIO

### Objetivo
Persistir archivos subidos y generados en MinIO dedicada, sellados por workspace, y procesar tipos soportados mediante pipelines seguros que respetan allowlists del router.

### Tareas y subtareas
1. **Infra MinIO dedicada.**
   - Agregar servicio MinIO a compose `faber_loom`.
   - Configurar dominios `minio.faberloom.ai` y `console.minio.faberloom.ai`.
   - Agregar reverse proxy en mwt-nginx.
   - Crear buckets `fl-uploads` y `fl-generated`.
   - Crear credencial de servicio no-root.
2. **Modelo de objetos.**
   - Metadata DB: bucket, key, workspace, tenant, uploader, tipo, hash, tamaño, origen, estado.
   - Prefijo `ws-{id}/...` y validación API antes de presigned URL.
3. **Upload universal en chat.**
   - UI de adjuntos.
   - Límites de tamaño y bloqueo de ejecutables.
   - Estados: subido, pendiente de ingesta, procesado, fallido.
4. **Pipelines por tipo.**
   - Reusar CSV/XLSX/PDF/MD/TXT.
   - Añadir imagen, audio, video, Word, Access, JSON, SQL según prioridad.
   - Marcar tipos no procesables como almacenados pero no enviados a modelo.
5. **Seguridad de ingesta.**
   - Tratar contenido extraído como no confiable.
   - Canaries para audio transcrito, video, JSON, SQL y tipos existentes.
   - Prohibir que archivo dispare acciones.
6. **Exfiltración y allowlist.**
   - Workspace solo-local impide enviar contenido a modelo cloud.
   - Pipelines consultan la misma política del router.
7. **Objetos generados por IA.**
   - Persistir imágenes, exports y drafts renderizados.
   - Emitir URLs presignadas con expiración.
8. **Backup/restore.**
   - `mc mirror` nocturno.
   - Smoke test de restore antes de datos reales sensibles.

### Archivos/componentes
`docker-compose*`, config mwt-nginx, `app/src/storage*`, `app/src/ingest*`, `app/src/router/*`, `app/src/api.py`, `app/src/db.py`, `app/static/js/app.jsx`, `app/static/css/main.css`, `app/tests/*`.

### Responsable
Dev: storage/ingesta/UI/tests. Ops: DNS/proxy/secrets/backups. CEO/admin: aprobar certificados comerciales al arranque de E2-6.

### Talla
L.

### Dependencias
E2-1 para infra; E2-4 para pipelines con modo auto/allowlist; E2-3 para sellado robusto.

### Criterio de aceptación / DoD
Archivo soportado sube a MinIO sellado; metadata queda auditada; modelo lo procesa respetando allowlist; objetos generados se persisten; fuga de objetos = 0; canaries de ingesta pasan; restore smoke test verde.

### Riesgo principal
Exfiltrar contenido sensible por un pipeline que no respeta workspace allowlist o emitir presigned URLs sin validar scope.

---

## 4. Orden de ejecución recomendado

1. **Sprint 0 — Freeze y preparación.** Confirmar alcance E2, responsables, matriz inicial de roles, calendario y criterios P0. No iniciar features de E2-4/E2-6 antes de cerrar base de identidad/contexto.
2. **E2-0 completo.** Gate: app E1 sigue funcionando con auth, audit actor real, Context obligatorio y migración Postgres ensayada.
3. **E2-1 plataforma compartida.** Gate: Postgres+RLS productivo, canario bidireccional, 2+ usuarios concurrentes, KB real cargada y backup/restore probado.
4. **E2-2 dogfood multi-user.** Gate: roles, WorkLoom compartido, draft A aprobado por B, correo real E2E, canaries multi-user e inicio de medición N=10 casos/14 días.
5. **Sync de adopción.** Si tres casos consecutivos por usuario requieren salir de la app, congelar expansión y corregir fricción antes de E2-5.
6. **E2-3 sellado profundo.** Gate obligatorio antes de entidad viva: cross-rol/workspace/tenant = 0 y gold L3 con segundo gate/k-anon.
7. **E2-4 routing gestionado.** Puede empezar diseño después de E2-1 y construcción parcial en paralelo con E2-3, pero el modo auto no se libera sin allowlists, budgets, max pasos y ledger.
8. **E2-5 entidad viva.** Solo después de roles + sellado. Arrancar desactivada por defecto, activar en pocos workspaces, medir utilidad y costo.
9. **E2-6 MinIO/ingesta.** Infra MinIO puede prepararse desde E2-1; procesamiento multimodal completo debe esperar políticas de router/allowlist. Comprar certificados comerciales al iniciar este hito.
10. **Cierre Etapa 2.** Ejecutar suite completa, canario permanente, restore smoke, pruebas de exfiltración, informe de adopción y runbooks actualizados.

---

## 5. Riesgos y mitigaciones

| Riesgo | Prob. | Impacto | Mitigación | Hito |
|---|---:|---:|---|---|
| Fuga cross-tenant por query sin `tenant_id` | Media | P0 | Context obligatorio, RLS, usuario app limitado, tenant canario bidireccional en CI/despliegue | E2-0/E2-1/E2-3 |
| Fuga cross-workspace/rol | Media | P0 | Matriz de permisos, tests negativos, RLS donde aplique, revisión de endpoints críticos | E2-2/E2-3 |
| Auth híbrida o bypass legacy | Media | Alto | Una fuente de sesión, retirar puentes temporales, tests de acceso anónimo/rol | E2-0/E2-2 |
| Migración SQLite→Postgres incompleta | Media | Alto | Migración repetible, backup, conteos, muestras, rollback, restore smoke | E2-0/E2-1 |
| Usuario DB con privilegios excesivos | Media | P0 | Separar owner/migrator/app user; RLS forzada; pruebas con usuario app | E2-1 |
| HITL debilitado por colaboración | Baja/Media | P0 | Doble confirmación irreversible, `approved_by` real, pruebas A/B usuario | E2-2 |
| Injection por contenido compartido | Media | P0 | Canaries email/PDF/Excel/KB/SKILL.md y nuevos tipos; contenido como dato no instrucciones | E2-2/E2-6 |
| Gold contaminado entre AMs | Media | Alto | Segundo gate, k-anon >=5, comité, auditoría de fuente y promotor | E2-3 |
| Dispatcher auto sin techo de costo/pasos | Media | Alto/P0 | Max pasos, budget cap, ledger, abortos seguros, no irreversibles | E2-4 |
| Exfiltración a modelos cloud | Media | P0 | Allowlist por workspace aplicada en router e ingesta; tests solo-local | E2-4/E2-6 |
| MinIO URL presignada sin scope | Media | P0 | Validación API por tenant/workspace antes de emitir URL; expiración corta; audit | E2-6 |
| Entidad viva ejecuta acción irreversible | Baja | P0 | Tools allowlist solo lectura + creación items, kill switch, tests de prohibición | E2-5 |
| Propuestas ambientales ruidosas | Media | Medio | Deduplicación, backoff, límites por ciclo, métrica de aceptación | E2-5 |
| Complejidad UI en React UMD | Media | Medio | Componentes simples, no migrar build system salvo bloqueo, priorizar flujos críticos | E2-2/E2-4/E2-6 |
| Operación sin runbooks | Media | Alto | Runbooks de deploy, backup, restore, rotación keys, incidentes P0 | E2-1/E2-6 |

---

## 6. Recomendaciones

1. **Convertir E2-0/E2-1 en un “platform gate” formal.** No aceptar features nuevas hasta que Postgres+RLS, Context, audit y auth estén estables.
2. **Introducir el tenant canario desde E2-0, no esperar a E2-3.** E2-3 debe ampliarlo, pero la migración a Postgres debe nacer con prueba real de aislamiento.
3. **Definir una matriz de permisos versionada antes de E2-2.** Debe cubrir WorkLoom, KB, gold, rutinas, routing, objetos y administración.
4. **Separar usuarios DB: owner, migrator y app user.** El app user nunca debe poder saltarse RLS ni modificar policies.
5. **Agregar pruebas negativas como contrato.** Cada endpoint crítico debe probar “usuario correcto ve dato” y “usuario equivocado no ve dato”.
6. **No iniciar migración del frontend durante Etapa 2.** React UMD es imperfecto, pero cambiar build system distrae; solo reconsiderar si E2-4/E2-6 bloquean severamente.
7. **Diseñar el ledger antes del modo auto.** Sin ledger real, no hay forma segura de depurar costos, atribución ni exfiltración.
8. **Tratar todos los archivos y transcripciones como contenido hostil.** Ningún extractor debe producir instrucciones ejecutables; solo datos citables con fuente.
9. **Activar entidad viva en modo dark-launch.** Primero generar propuestas invisibles o solo para admin; luego WorkLoom limitado; después ampliar si la tasa de utilidad lo justifica.
10. **Runbooks obligatorios.** Antes de dogfood multi-user deben existir procedimientos de backup/restore, rotación de secrets, kill switch, incidente de fuga, rollback de deploy y bloqueo de usuario.
11. **Presupuestos y allowlists fail-closed.** Si falta configuración de budget, modelo o capacidad, la respuesta correcta es bloquear o decir que no hay capacidad, nunca improvisar proveedor.
12. **Mantener el principio “una entidad, no fábrica de agentes”.** Los perfiles por AM deben ser configuración versionada dentro de rutinas, no procesos/agentes independientes con permisos propios.

---

## 7. Definición global de terminado para Etapa 2
