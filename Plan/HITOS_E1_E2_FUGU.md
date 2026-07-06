# Hitos de FaberLoom/SpaceLoom — Etapa 1 + Etapa 2

Resumen de todos los hitos de `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` y `Plan/PLAN_TRABAJO_E2_FUGU_v3.md`, con lo que debe hacerse en cada uno.

---

## Etapa 1: PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1

> App de escritorio single-user, local-first. Telar completo: SpaceLoom + Routine Hub + router + workspaces + KB + HITL. Instalable sin terminal.

### Hito: SL0 — Esqueleto + seed
- **Objetivo:** Tener la app corriendo localmente con un workspace de prueba y datos semilla.
- **Qué se debe hacer:**
  - Bootstrap de la app FastAPI + React.
  - Modelo de datos base.
  - Crear 1 workspace de prueba con datos semilla.
  - Configurar pywebview y static files.
- **Entregable clave:** App vacía que abre y persiste estado local.
- **Dependencias / Gate:** Carve-out del freeze scope ratificado por CEO.
- **Talla:** S

### Hito: SL1a — Router mínimo + chat
- **Objetivo:** Chat funcional con routing mínimo multi-proveedor.
- **Qué se debe hacer:**
  - Integrar 1 proveedor cloud + Ollama opcional.
  - Fallback y costo visible.
  - Budget cap y provider allowlist.
  - Canvas chat básico.
- **Entregable clave:** Chat que responde con modelo seleccionado y muestra costo.
- **Dependencias / Gate:** SL0.
- **Talla:** (parte de SL1 L)

### Hito: SL1b — Primer draft contra mini-KB real + HITL mínimo
- **Objetivo:** Generar el primer draft real contra KB real de MWT, con aprobación/edición/exportación.
- **Qué se debe hacer:**
  - Cargar mini-KB real (precios, fichas, etc.).
  - Generar draft con citas a fuente.
  - Implementar HITL mínimo: aprobar, editar, exportar o enviar.
  - Iniciar medición de adopción (Alvaro dogfooding).
- **Entregable clave:** Alvaro genera un draft real y empieza a usarlo.
- **Dependencias / Gate:** SL1a.
- **Talla:** (parte de SL1 L)

### Hito: SL2a/b/c — Workspaces + KB
- **Objetivo:** Workspaces por cliente con herencia de KB y capacidad de subir documentos.
- **Qué se debe hacer:**
  - Crear/editar workspaces por cliente.
  - Ingesta de MD/TXT/PDF/Excel/CSV.
  - Chunks + FTS5.
  - El agente cita datos reales de la KB; 0 inventado.
  - SL2a incluye test mínimo de fuga workspace A vs B.
- **Entregable clave:** Un draft cita un dato real de la KB y no inventa.
- **Dependencias / Gate:** SL1b.
- **Talla:** L

### Hito: SL3a — Skills / Routine Hub
- **Objetivo:** Crear, aprobar e invocar rutinas/skills con SKILL.md.
- **Qué se debe hacer:**
  - Parser/compiler de SKILL.md (subconjunto de SCH_FB_SKILL_MANIFEST_v2).
  - Sandbox liviano para skills.
  - Autoría asistida: entidad redacta skill → HITL aprueba → guarda.
  - Invocación por `@nombre`.
  - Biblioteca, historial y re-ejecución.
- **Entregable clave:** Crear y correr una skill por `@nombre` end-to-end.
- **Dependencias / Gate:** SL2.
- **Talla:** L

### Hito: SL3b/c — HITL + Gold Loop
- **Objetivo:** Cola de aprobación WorkLoom y captura de aprendizaje (gold candidates).
- **Qué se debe hacer:**
  - WorkLoom: cola por estado/urgencia (aprobar/editar/rechazar + capturar por qué).
  - Evidence bundle por decisión.
  - Gold loop: capturar outputs corregidos como candidates.
  - Medir `edit_pct` por tipo de tarea.
- **Entregable clave:** `edit_pct` de un mismo tipo de tarea baja con el uso.
- **Dependencias / Gate:** SL3a.
- **Talla:** M

### Hito: SL3.5 — Sellado + llave graduada
- **Objetivo:** Garantizar que lo de un workspace no se cuela en otro.
- **Qué se debe hacer:**
  - Índice vs contenido sellado por workspace.
  - Sellado local (HMAC/workspace) sobre KB, rutinas, runs, drafts.
  - Test de fuga cross-workspace = 0.
  - SQLCipher/passphrase para workspaces confidenciales.
- **Entregable clave:** Test de fuga cross-workspace = 0.
- **Dependencias / Gate:** SL3.
- **Talla:** M

### Hito: SL5 — Correo
- **Objetivo:** Connector multi-cuenta, read-first, envío con HITL.
- **Qué se debe hacer:**
  - Conector IMAP/SMTP multi-cuenta.
  - Leer correos y generar drafts.
  - Envío solo tras doble confirmación HITL.
  - Canaries de injection por email.
- **Entregable clave:** Recibir correo → generar draft → enviar solo tras aprobación.
- **Dependencias / Gate:** SL3.5 (recortable).
- **Talla:** M

### Hito: SL4 — Empaque desktop
- **Objetivo:** App firmada para Windows/Mac, instalable con doble clic.
- **Qué se debe hacer:**
  - PyInstaller + pywebview.
  - Firma de código (Apple Developer + cert Windows).
  - Auto-update firmado y verificado.
  - Instalador usable por no-técnico.
- **Entregable clave:** Un no-técnico instala sin ayuda; Etapa 1 DONE.
- **Dependencias / Gate:** SL5 (o SL3.5 si SL5 se difiere).
- **Talla:** M

---

## Etapa 2: PLAN_TRABAJO_E2_FUGU_v3

> Multi-usuario interno para el equipo MWT. Se activan las costuras contract-first de E1: tenant_id, user_id, actor_role, Context, AuditWriter, router abstraído, versionado de rutinas.

### Hito: E2-0 — Activar costuras + higiene E1
- **Objetivo:** Preparar el runtime único `app/` para multi-usuario.
- **Qué se debe hacer:**
  - Recuperar/versionar `harness/prompts/sl1b_dogfood_prompts.json`.
  - Documentar promoción del spike a base E2.
  - Escribir lessons learned E1 y aplicar licencia FSL 1.1.
  - Archivar SPINE Django como contrato de referencia.
  - Unificar identidad runtime (backend, Foundation, frontend resuelven el mismo usuario).
  - Activar `Context(workspace_id, tenant_id, user_id)` en rutas y queries.
  - AuditWriter persistente (tabla + jsonl).
  - Planificar migración SQLite→Postgres con verificación de conteos.
  - Sembrar tenant canario temprano.
  - Re-correr suite E1 y agregar regresiones de Context/audit/sesión.
- **Entregable clave:** App E1 funciona con usuario autenticado; cada acción relevante deja auditoría con actor/tenant/workspace; migración Postgres ensayada.
- **Dependencias / Gate:** Etapa 1 cerrada; decisión de runtime único.
- **Talla:** M

### Hito: E2-1 — Servidor compartido + Postgres operativo
- **Objetivo:** Desplegar instancia interna compartida con Postgres+RLS, datos reales y concurrencia.
- **Qué se debe hacer:**
  - Agregar Postgres al compose `faber_loom` (puerto 5435).
  - Migración productiva SQLite→Postgres con backup/verificación.
  - Activar RLS por tenant/workspace; separar usuarios DB (owner/migrator/app).
  - Pruebas MWT vs canario bidireccionales.
  - Crear usuarios internos iniciales; validar sesiones simultáneas.
  - Cargar KB real MWT (catálogo, listas de precios, fichas) y verificar citas con un AM.
  - Observabilidad mínima: logs, healthchecks, espacio en disco.
  - Runbook de backup/restore/despliegue.
- **Entregable clave:** 2+ usuarios trabajan simultáneamente sin colisiones; Postgres+RLS es fuente de verdad; KB real cargada y citada; restore smoke test documentado.
- **Dependencias / Gate:** E2-0 completo; acceso al host 187.77.218.102; secretos definidos.
- **Talla:** L

### Hito: E2-2 — Roles + HITL multi-user + WorkLoom compartido
- **Objetivo:** Introducir roles reales, cola compartida, aprobación cruzada y correo real.
- **Qué se debe hacer:**
  - Definir matriz de permisos por AM, curador, CEO, admin técnico.
  - Persistir `actor_role_at_decision` y `approved_by` reales.
  - WorkLoom compartido: asignación, urgencia, estados, reasignación, filtros.
  - HITL multi-user: draft de A aprobado por B.
  - Segundo gate gold: quien aprueba draft no puede promover el mismo dato duro a gold.
  - Correo real: rotar IMAP Kimi Work, activar flag, onboarding por AM con app-password, caso E2E real.
  - Medir adopción: N=10 casos reales voluntarios en 14 días por usuario.
- **Entregable clave:** Draft creado por A aprobado por B con rol registrado; correo real E2E; WorkLoom compartido; canaries multi-user pasan.
- **Dependencias / Gate:** E2-1; usuarios reales; correo disponible.
- **Talla:** M

### Hito: E2-3 — KB compartida + sellado por rol/workspace
- **Objetivo:** KB organizacional con herencia org→equipo→workspace y gold loop capa 2.
- **Qué se debe hacer:**
  - Modelo de herencia KB con reglas de precedencia.
  - Autorización por rol/workspace (servicios + RLS).
  - Tenant canario completo en Foundation y tablas relevantes; M16 bidireccional.
  - Gold loop L2→L3: estados candidate/active/rejected/L3 pending; k-anon >=5; comité/curador para L3.
  - Mantener `source_to_field_check` y `stale_data_block`.
  - Dataset controlado y pruebas negativas de fuga.
- **Entregable clave:** Fuga cross-rol/workspace/tenant = 0; M16 MWT↔canario verde; gold L3 requiere segundo gate y k-anon.
- **Dependencias / Gate:** E2-2 para roles; E2-1 para Postgres/RLS.
- **Talla:** L

### Hito: E2-4 — Routing gestionado + catálogo + modo auto
- **Objetivo:** Pasar de BYO-key/manual a routing administrado con catálogo, budgets y dispatcher auto.
- **Qué se debe hacer:**
  - Catálogo de modelos cloud + Ollama local con tags de capacidad, costo, latencia.
  - Gestión segura de keys administradas; budgets por usuario/equipo/workspace.
  - Ledger de costos por request/paso/modelo/proveedor.
  - Selector manual de modelo en chat.
  - Dispatcher auto: clasificar, descomponer, encadenar; max pasos, budget cap, allowlist por workspace.
  - Atribución: UI muestra modelo final; evidence/ledger guarda cadena completa.
  - Caso canónico: PDF → resumen barato → imagen con `image_gen`.
- **Entregable clave:** Caso canónico E2E pasa; ledger muestra cadena completa; UI muestra modelo final; guardrails obligatorios.
- **Dependencias / Gate:** E2-1 para servidor/budgets; puede solaparse parcialmente con E2-3, pero modo auto no libera sin gates de aislamiento.
- **Talla:** L

### Hito: E2-5 — Entidad viva / ciclo ambiental
- **Objetivo:** Ciclo proactivo acotado que revisa workspaces/inbox/KB y propone items en WorkLoom.
- **Qué se debe hacer:**
  - Scheduler de gobierno: ciclo global máx 30 min, workspace máx 1/h, ventana 06:00–22:00 Bogotá.
  - Kill switch global y por workspace; budget propio 5% diario; tools allowlist solo lectura + creación de items.
  - Detectores: correos sin draft, fuentes vencidas, HITL estancado, rutinas fallidas, budget por agotarse, gold candidates sin revisar.
  - Crear propuestas WorkLoom con evidencia, deduplicación y prioridad.
  - Métricas: al menos 1 propuesta útil aceptada/semana.
  - Pruebas de que no ejecuta irreversibles.
- **Entregable clave:** Entidad detecta y propone con evidencia; 0 acciones irreversibles; kill switch probado; métrica de utilidad.
- **Dependencias / Gate:** E2-2 roles/WorkLoom; E2-3 KB sellada; E2-4 recomendado.
- **Talla:** L

### Hito: E2-6 — Ingesta universal + MinIO
- **Objetivo:** Persistir archivos subidos y generados en MinIO dedicada, con pipelines seguros por tipo.
- **Qué se debe hacer:**
  - Infra MinIO en compose `faber_loom`: dominios, buckets `fl-uploads`/`fl-generated`, credencial no-root, proxy mwt-nginx.
  - Modelo de objetos en DB con metadata y prefijo `ws-{id}`.
  - Upload universal en chat con límites de tamaño y bloqueo de ejecutables.
  - Pipelines por tipo: imagen, audio, video, Word, Access, JSON, SQL; reutilizar CSV/XLSX/PDF/MD/TXT.
  - Canaries de ingesta para todos los tipos.
  - Exfiltración: workspace solo-local impide enviar contenido a modelo cloud.
  - Objetos generados por IA persistidos con presigned URLs de expiración.
  - Backup `mc mirror` nocturno + smoke test de restore.
  - Comprar certificados comerciales al arrancar este hito.
- **Entregable clave:** Archivo soportado sube a MinIO sellado; modelo lo procesa respetando allowlist; objetos generados persistidos; fuga de objetos = 0; canaries pasan.
- **Dependencias / Gate:** E2-1 para infra; E2-4 para pipelines con modo auto/allowlist; E2-3 para sellado robusto.
- **Talla:** L

---

## Orden de ejecución recomendado (Etapa 2)

1. **Sprint 0 — Freeze y preparación:** alcance, responsables, matriz de roles, calendario, criterios P0.
2. **E2-0:** base de identidad, Context, audit, higiene E1, migración ensayada.
3. **E2-1:** Postgres+RLS, datos reales, concurrencia, backup/restore.
4. **E2-2:** roles, WorkLoom compartido, HITL cruzado, correo real, adopción inicial.
5. **Sync de adopción:** si 3 casos consecutivos por usuario requieren salir de la app, congelar y corregir fricción antes de E2-5.
6. **E2-3:** KB compartida, sellado profundo, tenant canario, gold L3.
7. **E2-4:** routing gestionado, catálogo, modo auto (diseño desde E2-1, liberación tras E2-3).
8. **E2-5:** entidad viva (solo tras roles + sellado).
9. **E2-6:** MinIO + ingesta universal (infra desde E2-1, procesamiento completo tras E2-4).
10. **Cierre Etapa 2:** suite completa, canario permanente, restore smoke, exfiltración, runbooks.
