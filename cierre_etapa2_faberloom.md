# CIERRE_ETAPA2_FABERLOOM — Estado de cierre por hito (E2-0 → E2-6)
id: CIERRE_ETAPA2_FABERLOOM
version: 1.0
status: ACTIVE
stamp: 2026-07-07
plan de referencia: PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1 (v1.6)
relacionado: DEC_FB_SPIKE_PROMOTION - LESSONS_LEARNED_E1.md - cierre_etapa1_faberloom.md
commits del cierre: 42c977c · 890b7d4 · e7c6843 · 6e2e5b5 · da69782 · 275caf5
suite: 398 tests verdes desde imagen limpia (2 fallos restantes son del entorno del contenedor de test, no de código)

---

## 0. Resumen ejecutivo

Etapa 2 ("multi-usuario interno") está **funcionalmente construida en los 7 pilares**, con dos
salvedades honestas: (1) el runtime sigue en SQLite — Postgres+RLS quedó en *staging validado*
con el canario, el switch es un hito propio (talla L); (2) tres gates son operativos, no de
código, y deben ejecutarse por humanos: correo end-to-end (H1), carga de KB real (H3, diferida
por decisión CEO), y el periodo de dark-launch del ciclo ambiental (E2-5).

Todo lo demás que el plan pedía existe, corre en producción (app.faberloom.ai, VPS
187.77.218.102, `/opt/faber_loom`) y tiene test que lo respalda.

---

## 1. E2-0 — Activar costuras + higiene E1

**DoD del plan:** app E1 corre idéntica con usuario autenticado; audit por actor; lote higiene commiteado.
**Estado: ✅ CERRADO** (con la parte Postgres promovida a staging — ver E2-1).

### Cómo se resolvió

| Entregable | Archivos | Lógica / funcionamiento |
|---|---|---|
| Context real en toda query | `app/src/context.py`, uso transversal en `app/src/db.py` | Todo acceso a datos pasa por `Context(workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision)`; los helpers exigen `require_scoped_workspace()` / `require_tenant()` (fail-closed). Tests: `test_e2_0_context_enforcement.py`, `test_e2_0_auth_context.py`. |
| Login local + sesión | `app/src/auth.py` | JWT en cookies HttpOnly (`faberloom_at` 60 min + `faberloom_rt` 7 días rotativa). El frontend (`app/static/js/app.jsx: apiFetch`) renueva sesión automáticamente ante 401 vía `POST /api/auth/refresh` y reintenta; si el refresh falla y había sesión previa, recarga una única vez para caer en el login (sin bucles — guard por `faberloom_user` en localStorage). |
| AuditWriter a tabla | `app/src/audit.py`, `app/src/foundation/m12_audit_trail.py` | Eventos a tabla `audit_log` (BD) + espejo JSONL. El audit conserva referencias a workspaces borrados (append-only inmutable), decisión reflejada también en la migración a Postgres (audit_log sin FKs). |
| Higiene E1 | `LICENSE` (FSL 1.1), `harness/prompts/sl1b_dogfood_prompts.json`, `docs/LESSONS_LEARNED_E1.md`, `docs/DEC_FB_SPIKE_PROMOTION.md` | H8/H9 cerrados; H7 formalizado: el deploy del spike se **promueve** (no se renombra) como base física de E2-1. |

---

## 2. E2-1 — Servidor compartido

**DoD del plan:** 2+ usuarios trabajan a la vez sin pisarse; decisión de motor DB ejecutada.
**Estado: 🟡 OPERATIVO con salvedad Postgres** (instancia compartida viva; switch de motor pendiente como hito propio).

### Cómo se resolvió

- **Instancia compartida**: compose `faber_loom` en el VPS (api :8200, `faberloom-postgres` :5435, `faberloom-minio` :9100/9101) detrás de mwt-nginx + Cloudflare (app.faberloom.ai). Multi-usuario real: tenant MWT con 3 usuarios, roles y sesiones concurrentes (foundation M07-M20).
- **Postgres + RLS (Sec.4 #1) — staging ejecutado y validado (2026-07-07):**
  - `app/scripts/sqlite_to_postgres.py`: corregidos 5 defectos reales que impedían la migración — exclusión de shadow tables FTS5, PKs compuestas (una sola cláusula `PRIMARY KEY (a,b)`), `IDENTITY BY DEFAULT` (acepta IDs explícitos de SQLite), creación de tablas multi-pass (el orden por rowid no respeta FKs), `setval` de secuencias tras la carga, y `audit_log` exento de FKs.
  - Migración real corrida contra `faberloom-postgres`: **completa, sin issues, conteos por tabla verificados** (616 filas).
  - `app/scripts/postgres_rls_policies.sql`: sintaxis corregida (`ENABLE` + `FORCE ROW LEVEL SECURITY`), aplicado; rol `faberloom_app` con `NOBYPASSRLS`.
  - **Gate del canario contra RLS: verde en ambas direcciones** (0 filas canary desde scope MWT; 0 filas MWT desde scope canary) — validación a nivel de *policy de Postgres*, no solo de capa app.
  - **Lo que falta** (documentado en `docs/DEC_FB_SPIKE_PROMOTION.md`): `db.py`/foundation usan `sqlite3` directo; el switch de runtime (psycopg, placeholders, FTS→tsvector, corte con freeze de escrituras) es talla L y se ataca como hito dedicado.
- **KB con datos reales (H3)**: diferido por decisión CEO 2026-07-07 ("el 1 déjalo así"). La KB corre con fixtures demo; el cargador está listo para cuando existan los archivos Marluvas/Tecmater.

---

## 3. E2-2 — Roles + HITL multi-user

**DoD del plan:** un draft creado por A es aprobado por B con rol registrado.
**Estado: ✅ CÓDIGO CERRADO · gate H1 pendiente de ejecución humana.**

### Cómo se resolvió

| Entregable | Archivos | Lógica / funcionamiento |
|---|---|---|
| Roles de dominio AM/curador/CEO | `app/src/foundation/core.py` (SYSTEM_ROLES) | `am` (opera drafts/rutinas, sin promoción gold), `curador` (kb.manage + gold.promote — ejerce el segundo gate), `ceo` (aprobación final y políticas). Mapean la semántica del plan sobre el vocabulario de permisos del RBAC (m09). `_sync_system_roles_all_tenants` los re-siembra al arranque: verificado en prod (7 roles). |
| WorkLoom cola compartida | `app/src/workloom.py` (`assign_workloom_item`), `app/src/api.py` (`POST /workloom/assign`, `GET /members`), `app/src/models.py` (migración 30: `assigned_to` en `routine_run` y `draft`; `WorkLoomAssignRequest`), `app/static/js/app.jsx` (WorkloomView) | Asignación y reasignación de items por usuario (select en cada tarjeta de run/draft, poblado con los miembros del tenant), `assigned_to = NULL` des-asigna, urgencia opcional en la misma llamada; fail-closed si el item no pertenece al workspace/tenant. La urgencia ya existía (v10) y se respeta en el orden de la cola. |
| Segundo gate gold | `app/src/gold.py:228` | Quien aprueba el draft no puede ser quien promueve el dato a gold (`approved_by == verified_by` → rechazo). Test: `test_e2_0_gold_second_gate.py`. |
| SL5 correo | `app/src/connectors/imap.py`, `email_account` + `workspace_smtp_config` (passwords cifrados con master key), flag `FABERLOOM_ENABLE_EMAIL_CONNECTOR` | **Activado en producción 2026-07-07** con `info@mwt.one` (IMAP mail.mwt.one:993 verificado — 2189 mensajes; SMTP :465 verificado). Credenciales de `trade@`/`mw_doc@` fallaron autenticación (535) — pendiente rotación/verificación. |

**Gate pendiente (humano):** 1 correo real end-to-end (recibir → draft → aprobar → enviar) desde la UI, con rol registrado. Es HITL por diseño: no se automatiza.

---

## 4. E2-3 — KB compartida + sellado por rol

**DoD del plan:** test de fuga cross-rol y cross-workspace = 0, incluido tenant canario.
**Estado: ✅ CERRADO a nivel app + canario permanente con regresión por deploy; la validación RLS ya corrió en staging (ver E2-1).**

### Cómo se resolvió

- **Canario permanente**: `app/src/seed.py` (`seed_canary_workspace`) siembra el tenant/workspace `canary` (flag `is_canary`) en cada arranque — está vivo en la BD de producción.
- **Regresión por deploy**: `app/scripts/check_canary_isolation.py` (nuevo) — M16-contra-canario bidireccional: para cada tenant (incl. canary) y cada tabla `fnd_*`, el acceso scoped devuelve exactamente sus filas propias, y ninguna fila canary aparece en scope ajeno. Corre dentro de la imagen (`docker run … python app/scripts/check_canary_isolation.py`). Última corrida en prod: **0 fugas en 63 checks (21 tablas × 3 tenants)**. Exit code 1 bloquea deploy.
- **Aislamiento**: `app/src/foundation/m16_tenant_isolation.py` (`isolation_check`, `tenant_scoped`) + tests `test_e2_0_canary_tenant.py`, `test_e2_0_context_enforcement.py`, `test_p0_security.py`.
- **Gold loop capa 2**: `app/src/gold.py` — candidate → active → L3 cross-AM con k-anon y comité (tests E2-3), más el detector ambiental `unreviewed_gold` que empuja candidates estancados a WorkLoom.

---

## 5. E2-4 — Routing gestionado + catálogo + modo auto

**DoD del plan:** caso canónico PDF → resumen (modelo barato) → imagen (image_gen), UI muestra el modelo final y el ledger la cadena completa.
**Estado: ✅ CERRADO — y el caso canónico ya es real, no stub.**

### Cómo se resolvió

| Entregable | Archivos | Lógica / funcionamiento |
|---|---|---|
| Keys admin cifradas | `app/src/router/config_store.py` | Fernet con master key; UI Admin > Router/Proveedores. |
| Catálogo por capacidad | `app/src/routing/catalog.py` | `DEFAULT_MODEL_CAPABILITIES` (text/cheap/vision/code/image_gen/local_only) + `MODEL_QUALITY` (1-3, versionado en git — contrato F1 tiered DEC-006) + `MODEL_CONTEXT_TOKENS` (ventana por modelo). Seed idempotente por workspace desde providers configurados. |
| Routing tiered del modo auto | `catalog.py: resolve_model_for_capability` | **La prioridad manual del admin NO participa en auto** (ENT_PLAT_LLM_ROUTING §D/§F): `low` → CHEAPEST_FIRST; `high` → BEST_FIRST (calidad dentro del budget); `medium` → mejor valor costo/calidad. Filtro por ventana de contexto según tokens estimados del paso (inputs largos van a modelos 128k/256k) y budget estimado con tokens reales. |
| Dispatcher / cadenas | `app/src/routing/auto_dispatcher.py` | Planner LLM (modelo barato) descompone en pasos con complejidad; los pasos intermedios (extraer/resumir) se marcan `low` (modelos baratos) y el paso final lleva la complejidad real (el modelo capaz responde al usuario). Guardrails: max pasos, budget por paso y acumulado, allowlist, fail-closed, HITL intacto. |
| image_gen real | `auto_dispatcher.py: _execute_openai_image_step`, `router/cost.py`, `catalog.py` | `gpt-image-1` vía OpenAI Images API; la imagen se persiste en MinIO `fl-generated` **sellada por workspace** (`create_generated_object`) y el paso devuelve URL presignada (1h); costo plano al ledger. El stub queda como fallback de test. |
| Visión (chat + auto) | `app/src/ingest.py` (`load_image_attachment`, base64, 5MB), `app/src/api.py`, `app/src/router/providers.py` | Adjuntos de imagen viajan como contenido multimodal (OpenAI `image_url` / Anthropic `image` blocks). En modo auto, plan determinista con paso `vision`. |
| Budget por usuario | migración 30 (`user_budget_cap_usd` en `workspace_routing_policy`), `db.py: sum_user_usage_cost`, enforcement en `api.py` | Cap individual (NULL = sin límite); verificado *antes* de gastar (fail-closed, 422 con detalle). En prod: 2 USD/usuario según tenant settings. Lección grabada: todo pre-check que pueda INSERTar (p.ej. `get_routing_policy` crea la fila default) va en su propia `with transaction(conn)` — dejarla abierta anulaba los commits del request (regresión cazada por la suite). |
| Atribución | UI `message-route` + `usage_record`/chain ledger | La UI muestra el modelo del entregable final; la cadena completa (pasos, costos) queda inmutable en el ledger, visible al expandir. |

**Pendiente menor (no gate):** builder/templates de presets (SPEC_FB_ROUTING_PRESETS_v1) — la validación de `preset_id` existe; la UI de builder se difiere.

---

## 6. E2-5 — Entidad viva (ciclo ambiental)

**DoD del plan:** la entidad detecta y propone (0 irreversibles); el equipo acepta ≥1 propuesta útil/semana.
**Estado: ✅ CÓDIGO CERRADO según §1.7 completo · APAGADO en prod por contrato hasta pasar el gate (dark-launch + utilidad).**

### Cómo se resolvió

| Entregable (§1.7.x) | Archivos | Lógica / funcionamiento |
|---|---|---|
| 6 detectores (solo lectura) | `app/src/ambient_detectors.py` | `failed_routine` (24h), `stuck_hitl` (4h), `budget_exhaustion` (>90%), y los 3 nuevos: `mail_without_draft` (unread sin draft >4h), `stale_source` (vigente_hasta vencida o >180 días), `unreviewed_gold` (candidates >48h, con nota de que aplica el segundo gate). |
| Ciclo, ventana, budget (1.7.1) | `app/src/ambient.py` | Scheduler de gobierno (daemon, no cron propio), frecuencia global 30 min / workspace 1h, ventana 06:00-22:00 Bogotá (fuera de ventana solo eventos críticos), budget del ciclo = 5% del budget diario del router. |
| Dark-launch + dedup (1.7.2) | `ambient.py` | Modo observación (propuestas internas sin items visibles) los primeros 14 días; dedup por `hash(detector|target|bucket temporal)` con merge de evidencia en propuestas abiertas <24h. |
| Backoff + circuit breakers (1.7.3) | `ambient.py` (`get_detector_backoff`, `compute_backoff_until`, `disable_detector`) | Backoff `2^n × 60s` (máx 4h) **aplicado en el loop** (skip con `skipped_backoff`); 3 fallos consecutivos → detector `disabled` hasta revisión manual. CB de utilidad (<20% aceptadas, 3 ciclos → auto-pausa) y CB de costo (>150% del budget → `cost_overrun`, detectores restantes se saltan). |
| Métricas (1.7.4) | tabla `ambient_cycle` + `GET /admin/ambient/metrics` | propuestas creadas/visibles/dark, costo, latencia, fallos por detector. |
| Audit + kill switch (1.7.5) | `ambient.py` + endpoints `/admin/ambient/*` | Audit inmutable por ciclo; kill switch global y por workspace, verificado antes de cada detector. |
| **Arranque apagado (Sec.7.1)** | `ambient.py` (seed y scheduler con default `False`), prod: `ambient_config.global_enabled = 0` | Fail-closed: el ciclo NO corre hasta decisión explícita de encendido al iniciar el periodo de dark-launch del gate E2-5. Tests actualizados para encender explícitamente. |

---

## 7. E2-6 — Ingesta universal + MinIO

**DoD del plan:** subir cualquier tipo soportado → objeto sellado en MinIO → el modelo lo procesa respetando allowlist; fuga de objetos = 0; canaries pasan.
**Estado: ✅ CERRADO en lo construible hoy** (audio/video quedan fail-closed sin engine local — decisión honesta, no gap silencioso).

### Cómo se resolvió

| Entregable | Archivos | Lógica / funcionamiento |
|---|---|---|
| MinIO propia | compose `faber_loom` (`faberloom-minio`), `app/src/storage.py` | Buckets `fl-uploads`/`fl-generated`, prefijo `ws-{id}/…` (sellado por workspace), URLs presignadas con expiración, nunca bucket público. CORS: una sola capa (nginx con `proxy_hide_header` — fix 2026-07-07 que destrabó los uploads). |
| Pipeline por tipo | `app/src/ingest.py` | docx, JSON, SQL, **csv/tsv** (sniffer + tabla pipe), **xlsx/xls** (openpyxl read-only, por hoja), **md/txt/html/log** (utf-8→latin-1), imagen (OCR local o **visión multimodal** al modelo), audio/video (whisper: fail-closed honesto si no está el engine), **Access rechazado con mensaje claro** ("exporta a CSV/XLSX"). |
| Objetos generados por IA | `db.py: create_generated_object` | Todo output binario (imágenes de image_gen) persiste en `fl-generated` con metadata en la tabla `object`; la DB guarda solo referencia. |
| Sellado + fugas | tests de objetos (fuga = 0), canaries de injection (docx/JSON) | Extendidos del test de fuga E2-3 al nivel objeto. |
| Exfiltración | `require_local_only` respetado en `ingest.py` y en `resolve_model_for_capability` | Workspace solo-local jamás manda contenido a cloud. |
| UX de adjuntos | `app/static/js/app.jsx`, `main.css` | Chip de adjunto arriba del input; en los mensajes, thumbnail para imágenes (presigned GET) y tarjeta con badge de extensión (PDF/XLSX/DOCX/HTML) para documentos; el texto extraído no ensucia el bubble (queda en DB para el modelo). |

---

## 8. Gates abiertos para declarar Etapa 2 TERMINADA

1. **Switch de runtime a Postgres+RLS** (E2-0/E2-1, talla L): staging listo y validado; falta capa de conexión dual en `db.py`/foundation, FTS→tsvector y corte con freeze. Ver `docs/DEC_FB_SPIKE_PROMOTION.md`.
2. **Correo end-to-end del gate H1** (E2-2, humano): recibir → draft → aprobar → enviar desde la UI con `info@mwt.one` (ya conectado). Rotar/verificar credenciales de `trade@` y `mw_doc@`.
3. **KB real (H3)**: diferido por decisión CEO 2026-07-07; la instancia corre con fixtures demo.
4. **Gate E2-4 (encendido de modo auto para el equipo)** y **gate E2-5 (dark-launch 14 días + utilidad ≥25%)**: el código está; son decisiones operativas de encendido y calibración.
5. Menores: builder de presets (UI), whisper en imagen runtime si se quiere audio/video operativos.

## 9. Seguridad — pendientes de higiene

- Rotar el password root del VPS y las claves de correo compartidas por chat durante esta sesión; migrar SSH a llaves (`PasswordAuthentication no`).
- Las credenciales en BD van cifradas (Fernet/master key); las de `.env` viven solo en el VPS.

---

Changelog:
- v1.0 (2026-07-07): documento de cierre inicial. Refleja commits 42c977c…275caf5, suite 398 verdes, staging Postgres+RLS validado con canario, email connector activado con info@mwt.one.
