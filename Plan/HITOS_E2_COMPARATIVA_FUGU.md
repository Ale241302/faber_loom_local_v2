# Hitos Etapa 2 — Plan original vs Plan de trabajo Fugu

## Resumen ejecutivo

Ambos planes cubren los mismos siete hitos E2-0→E2-6 y mantienen el mismo norte: convertir FaberLoom/SpaceLoom en una instancia interna multi-usuario para MWT, sin saltar a SaaS ni multi-tenant externo. El plan original define la arquitectura, decisiones bloqueantes, gates P0 y alcance contractual de cada hito. El plan de trabajo Fugu traduce esa intención en ejecución: tareas, componentes, responsables, riesgos y criterios de aceptación más operables. No hay hitos nuevos ni eliminados; la diferencia principal es de granularidad y disciplina de gate. Fugu endurece E2-0/E2-1 como “platform gate”, adelanta el tenant canario, exige convergencia de auth/contexto, formaliza runbooks y vuelve explícitos los controles de RLS, permisos, ledger, MinIO y entidad viva.

## Hitos del plan original (PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1)

| Hito | Nombre | Qué se debe hacer | Entregable clave | Dependencias/Gate |
|---|---|---|---|---|
| E2-0 | Activar costuras + higiene E1 | Pasar de costuras latentes a contexto real: "'`workspace`, `tenant`, `user`, auditoría por actor, migración de datos E1, login local y cierre de higiene heredada. | App E1 funcionando igual pero autenticada, con `Context` real, auditoría por actor y lote documental/mecánico E1 cerrado. | Arranca con Etapa 1 DONE y gate de adopción aprobado. Gate: la app no se rompe, auditoría registra actor y la higiene queda commiteada. |
| E2-1 | Servidor compartido | Desplegar instancia self-hosted LAN/VPN para el equipo, ejecutar decisión de motor DB y permitir concurrencia real. | Instancia compartida en host definido, con base transaccional apta para varios usuarios y datos reales MWT. | Depende de E2-0. Gate: 2+ usuarios trabajan simultáneamente sin pisarse. |
| E2-2 | Roles + HITL multi-user | Introducir roles AM/curador/CEO, WorkLoom compartido, asignación de items, aprobación cruzada, segundo gate gold y activación formal de correo. | Draft creado por un usuario y aprobado por otro, con rol y aprobador reales registrados. | Depende de E2-1. Gate: colaboración sin relajar doble confirmación ni HITL; cierre formal de correo real. |
| E2-3 | KB compartida + sellado por rol | Construir KB org→equipo→workspace, aplicar sellado por rol/workspace y activar gold loop capa 2 con comité y k-anon. | KB compartida con herencia, citas/fuentes conservadas, gold L2→L3 controlado y aislamiento verificable. | Depende de E2-2. Gate: fuga cross-rol, cross-workspace y cross-tenant = 0, incluido tenant canario bidireccional. |
| E2-4 | Routing gestionado + catálogo + modo auto | Pasar de BYO-key a keys administradas, catálogo multi-proveedor/local, budgets, ledger, selector manual y dispatcher auto con límites. | Caso canónico PDF→resumen→imagen, UI mostrando modelo final y ledger/evidencia mostrando toda la cadena. | Depende de E2-1. Gate: max pasos, budget cap, allowlist por workspace y atribución auditada obligatorios. |
| E2-5 | Entidad viva | Agregar ciclo ambiental proactivo acotado que revisa workspaces, inbox y KB, detecta problemas y propone items. | Propuestas útiles en WorkLoom con evidencia, sin acciones irreversibles. | Depende de E2-2 + E2-3. Gate: 0 irreversibles y al menos 1 propuesta útil aceptada por semana. |
| E2-6 | Ingesta universal + MinIO | Incorporar MinIO dedicada, subida universal en chat, pipelines por tipo, persistencia de objetos generados y sellado a nivel objeto. | Archivos y objetos IA persistidos en MinIO con metadata, prefijo por workspace, URLs presignadas y pipelines seguros. | Depende de E2-1 para infra y E2-4 para pipelines con modo auto. Gate: fuga de objetos = 0, allowlist respetada y canaries de ingesta pasan. |

## Hitos del plan de trabajo Fugu (PLAN_TRABAJO_E2_FUGU_v3)

| Hito | Nombre | Qué se debe hacer | Entregable clave | Dependencias/Gate |
|---|---|---|---|---|
| E2-0 | Activar costuras + higiene E1 | Convertir el runtime `app/` en base multi-usuario: higiene E1, identidad unificada, `Context` obligatorio, `AuditWriter` persistente, plan de migración Postgres y canario temprano. | Base autenticada con auditoría por actor/tenant/workspace, migración ensayada, canario sembrado y regresiones P0 iniciales. | Depende de Etapa 1 cerrada y runtime único. Gate: E1 sigue funcionando, no hay query crítica sin scope y la migración tiene verificación/rollback. |
| E2-1 | Servidor compartido + Postgres operativo | Desplegar Postgres propio, migrar datos, activar RLS, separar usuario de app, validar concurrencia, cargar KB real y documentar operación. | Postgres+RLS como fuente de verdad, instancia compartida operativa, KB real cargada, backup/restore probado. | Depende de E2-0 y secretos/host. Gate: 2+ usuarios simultáneos, canario MWT↔canary verde y usuario DB sin privilegios excesivos. |
| E2-2 | Roles + HITL multi-user + WorkLoom compartido | Definir matriz de permisos, roles reales, WorkLoom colaborativo, aprobación A→B, segundo gate gold, correo real y medición de adopción. | Cola compartida funcional, email E2E real, `approved_by` y `actor_role_at_decision` reales, adopción inicial medible. | Depende de E2-1. Gate: enviar/borrar mantiene doble confirmación, canaries multi-user pasan y se mide N=10 casos/14 días. |
| E2-3 | KB compartida + sellado por rol/workspace | Diseñar herencia KB, autorización por rol/workspace, canario completo en tablas relevantes, gold L2→L3 y QA negativa de fugas. | KB organizacional sellada, M16 bidireccional permanente, gold con k-anon y comité, citas/fuentes preservadas. | Depende de E2-2 y Postgres/RLS de E2-1. Gate: fugas cross-rol/workspace/tenant = 0 y promoción L3 imposible sin segundo gate. |
| E2-4 | Routing gestionado + catálogo + modo auto | Implementar catálogo de modelos, keys admin, budgets, ledger, selector manual, dispatcher auto, atribución final y caso canónico. | Router administrado con ledger por paso, UI de selección, modo auto limitado y evidencia completa. | Depende de E2-1; diseño puede solaparse con E2-3. Gate: no liberar auto sin ledger, allowlists, max pasos, budget cap y control de exfiltración. |
| E2-5 | Entidad viva / ciclo ambiental | Crear scheduler de gobierno, kill switch, budget propio, detectores iniciales, propuestas WorkLoom, métricas y pruebas de no irreversibilidad. | Ciclo ambiental configurable que propone con evidencia, deduplica, audita costo y puede apagarse por workspace. | Depende de E2-2 y E2-3; E2-4 recomendado para budgets/ledger. Gate: 0 acciones irreversibles, kill switch probado y utilidad semanal demostrada. |
| E2-6 | Ingesta universal + MinIO | Levantar MinIO, dominios/proxy, buckets, metadata de objetos, upload universal, pipelines por tipo, controles de ingesta, allowlist y backup. | Storage de objetos sellado, uploads y generados persistidos, metadata auditada, pipelines seguros y restore smoke verde. | Depende de E2-1, E2-4 y sellado robusto de E2-3. Gate: presigned URLs con scope validado, fuga de objetos = 0 y canaries nuevos/viejos pasan. |

## Diferencias / observaciones

| Tema | Plan original | Plan de trabajo Fugu | Observación de Fugu |
|---|---|---|---|
| Nivel de detalle | Define pilares, decisiones técnicas, riesgos P0 y gates por hito. | Descompone cada hito en tareas, componentes, responsables, DoD y riesgo principal. | El segundo no cambia el alcance; lo vuelve ejecutable y verificable. |
| E2-0/E2-1 | Activación de costuras y servidor compartido aparecen como primeros hitos. | Los convierte en “platform gate”: auth, Context, audit, Postgres, RLS, canario, backup y rollback antes de features. | Correcto: si la base multi-user falla, todo lo demás amplifica fugas y deuda. |
| Tenant canario | Es obligatorio en el gate E2-3 y permanente. | Se recomienda sembrarlo desde E2-0/E2-1 y ampliarlo en E2-3. | Adelantarlo reduce riesgo durante la migración a Postgres+RLS. |
| Auth/sesión | Decide auth local y usuario real. | Explicita convergencia entre backend, Foundation y frontend; advierte contra puentes legacy. | Riesgo crítico: auth híbrida puede crear bypasses aun con roles bien modelados. |
| Context y RLS | `Context` real y Postgres+RLS son contrato de etapa. | Añade enforcement por tests, wrappers/repositorios y usuario DB limitado. | No debe quedar como convención; debe fallar en pruebas si falta scope. |
| Roles y permisos | AM/curador/CEO y segundo gate gold. | Pide matriz versionada para WorkLoom, KB, rutinas, routing, budgets y objetos. | La matriz debe existir antes de E2-2 para evitar permisos implícitos. |
| Correo | Cierre formal y activación del flag en instancia compartida. | Añade rotación IMAP, app-passwords por AM, runbook, caso real y rollback. | Bien: correo es irreversible y toca credenciales reales. |
| KB/gold | Herencia org→equipo→workspace, gold L2→L3, k-anon y comité. | Añade estados explícitos, pruebas negativas y preservación de fuente/cita en herencia. | La herencia no puede degradar trazabilidad por campo. |
| Routing auto | Catálogo, manual/auto, ledger, allowlists y caso PDF→imagen. | Añade diseño previo de ledger, bloqueo fail-closed y no liberar auto antes de aislamiento. | Auto aumenta costo, injection y exfiltración; debe nacer con límites duros. |
| Entidad viva | Ciclo ambiental propositivo con límites, presupuesto, ventana y kill switch. | Añade dark-launch implícito, deduplicación, backoff, métricas de ruido/utilidad y auditoría por ciclo. | Evita que se vuelva un orquestador oculto con permisos excesivos. |
| MinIO/ingesta | MinIO dedicada, prefijo por workspace, presigned URLs y pipelines por tipo. | Añade modelo de metadata, validación API antes de URL, estados de ingesta y restore smoke. | El sellado de objetos es un segundo plano de autorización, no solo una ruta de storage. |
| Frontend | No prescribe migración del stack UI. | Recomienda no migrar React UMD salvo bloqueo real. | Mantener foco: Etapa 2 ya tiene suficiente riesgo de plataforma. |
| Operación | Incluye decisiones de host, puertos, DNS, backup y MinIO. | Exige runbooks de deploy, backup/restore, rotación, kill switch, fuga y rollback. | Dogfood multi-user necesita operación repetible, no solo código funcionando. |

## Conclusión operativa

| Resultado | Lectura |
|---|---|
| Cobertura de hitos | Completa: E2-0 a E2-6 aparecen en ambos planes. |
| Cambios de alcance | No hay expansión funcional neta; Fugu agrega controles, desglose y gates. |
| Mayor endurecimiento | E2-0/E2-1, por tratar identidad, auditoría, Postgres, RLS y Context como prerequisito de plataforma. |
| Mayor riesgo restante | Fugas por scopes incompletos, auth híbrida, dispatcher auto sin aislamiento pleno y objetos MinIO con autorización insuficiente. |
| Recomendación | Ejecutar el plan Fugu como WBS operativo del plan original, manteniendo el original como contrato arquitectónico y de alcance. |
