# Cierre Etapa 1 — FaberLoom (ex-SpaceLoom)

**Fecha de auditoría:** 2026-06-30  
**Auditor:** fugu (agente Codex)  
**Plan de referencia:** `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` (v1.0 + Enmienda v1.1)  
**Alcance:** Verificación de cierre de los streams SL0, SL1a, SL1b, SL2, SL3a, SL3b, SL3.5, SL4, SL5.

---

## 0. Contexto y método

- El proyecto fue **rebrandeado de "SpaceLoom" a "FaberLoom"** después de SL1a. Los reportes de cierre y el plan conservan la nomenclatura `SLx`; el código, la DB (`faberloom.sqlite3`), las variables de entorno (`FABERLOOM_*`) y los artefactos de build (`FaberLoom.exe`) ya usan el nombre nuevo. La regresión de rebrand está cubierta por `app/tests/test_post_sl1a_rebrand.py`.
- **Estado del harness** (`harness/state.json`): `completed_phases = [SL0, SL1a, SL1b, SL2a, SL2b/c, SL3a, SL3b/c, SL3.5, SL4, SL5]`; `current_phase = SL5`, `status = needs_review`, `next_phase = E0_CEO_decisions_and_MWT_pack`.
- **Esquema de datos actual:** `SCHEMA_VERSION = 17` (`app/src/models.py:12`).
- **Suite de tests ejecutada en esta auditoría:** `cd app; .venv/Scripts/python.exe -m pytest tests -q` → **221 passed, 1 warning**. El único warning es la deprecación de `httpx` en `starlette.testclient`.
- **Nota metodológica:** existió una auditoría senior (`harness/reports/AUDIT_FUGU_CODEX_SL3_4_5.md`) que declaró la entrega de SL2b/c–SL5 como funcional pero con gaps P0/P1. Varios gaps fueron cerrados posteriormente y están verificados por `app/tests/test_p0_security.py`.
- **Otros archivos solicitados:** se revisó `AGENTS.md` (costuras contract-first y riesgos P0 no negociables), `PROCUREMENT_LEDGER.md` (PRC-01–PRC-09), `app/build.py`, `app/pyproject.toml`, `docs/build/BUILD_DESKTOP.md`, `docs/contracts/latent_fields_matrix.md` y `patch-byok-env-routing.js`. No existe `README.md` en la raíz del repo. `patch-byok-env-routing.js` pertenece a un daemon externo Open Design y confirma un patrón BYOK por variables de entorno (`KIMI_API_KEY`, `DEEPSEEK_API_KEY`, `GROQ_API_KEY`, etc.); no es parte ejecutada por la app `app/src/`, por lo que no se usa como evidencia de cierre de un SL salvo como contexto de routing/BYOK.

### Cobertura de tests observada

| Archivo | Tests |
|---|---:|
| `app/tests/test_sl0_backend.py` | 7 |
| `app/tests/test_sl1a_router.py` | 18 |
| `app/tests/test_sl1a_router_endpoints.py` | 26 |
| `app/tests/test_post_sl1a_rebrand.py` | 8 |
| `app/tests/test_sl1b_kb_drafts.py` | 29 |
| `app/tests/test_sl1b_dogfood_ten_drafts.py` | 1 |
| `app/tests/test_sl2_kb_ingestion.py` | 8 |
| `app/tests/test_sl2_kb_inheritance.py` | 4 |
| `app/tests/test_sl2_citation_e2e.py` | 1 |
| `app/tests/test_sl2_draft_validation.py` | 3 |
| `app/tests/test_sl2_injection_canaries.py` | 5 |
| `app/tests/test_sl2_workspace_seal.py` | 4 |
| `app/tests/test_sl3a_skills.py` | 32 |
| `app/tests/test_routines_crud.py` | 7 |
| `app/tests/test_sl3b_workloom_gold.py` | 19 |
| `app/tests/test_sl3_5_seal.py` | 17 |
| `app/tests/test_sqlcipher_temp.py` | 2 |
| `app/tests/test_sl4_packaging.py` | 12 |
| `app/tests/test_sl5_imap.py` | 6 |
| `app/tests/test_p0_security.py` | 6 |
| `app/tests/test_config_store.py` | 6 |
| **Total** | **221** |

---

## SL0 — Esqueleto + seed

### Estado
**Cerrado** (gate aprobado: `harness/reports/SL0_final_eval.md` → `[APROBADO]`).

### Cómo se cerró
1. Se levantó la app desktop: `app/src/main.py` arranca FastAPI con `lifespan` que inicializa DB + seed, sirve el shell estático y abre la ventana pywebview (`run_desktop`), con fallback HTML si falta `index.html`.
2. Se implementó el modelo de datos base con migraciones versionadas (`_schema_version`) para `workspace`, `kb_source`, `chat`, `message`, `draft`, `audit_log`, `routine`, `routine_run`.
3. `app/src/seed.py` crea el workspace `MWT Demo` (`mwt-demo`) de forma idempotente.
4. Se dejaron costuras contract-first:
   - campos latentes (`tenant_id`, `actor_id`, `actor_role_at_decision`, `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by`);
   - `Context(workspace_id, tenant_id, user_id, actor_id, actor_role_at_decision)`;
   - `AuditWriter` con escritura a `audit_log` y espejo `audit.jsonl`;
   - tablas `routine` y `routine_run`.
5. La UI inicial quedó honesta: composer inerte para SL0, placeholders para vistas futuras y pills con disponibilidad de hitos posteriores.

### Evidencias
- Código: `app/src/main.py`, `app/src/db.py`, `app/src/seed.py`, `app/src/context.py`, `app/src/audit.py`, `app/src/models.py`, `app/static/index.html`, `app/static/js/app.jsx`.
- Tests: `app/tests/test_sl0_backend.py` (health/seed, idempotencia, esquema/campos latentes, auditoría, scoping por tenant).
- Documentos: `docs/contracts/latent_fields_matrix.md`.
- Reportes: `harness/reports/SL0_audit_iter1.md`, `harness/reports/SL0_eval_iter1.md`, `harness/reports/SL0_final_eval.md`.
- Outputs: `harness/agents/SL0_backend_iter1.md`, `SL0_backend_iter2.md`, `SL0_frontend_iter1.md`, `SL0_frontend_iter2.md`, `SL0_brand_iter1.md`.

### Brechas / Blockers
`Ninguna` para el alcance de SL0. Observaciones cosméticas no bloqueantes: el documento `docs/contracts/latent_fields_matrix.md` conserva el título "SpaceLoom SL0" y existieron textos históricos pre-rebrand.

---

## SL1a — Router mínimo + chat

### Estado
**Cerrado** (`harness/reports/SL1a_audit_iter4.md` con PASS y `harness/reports/SL1a_v2_CLOSER_REPORT_v1.md`).

### Cómo se cerró
1. Se creó el router mínimo en `app/src/router/` con prioridad, allowlist, budget cap, fallback y cost ledger (`engine.py`, `providers.py`, `registry.py`, `models.py`, `cost.py`, `config_store.py`).
2. Se cerraron fixes residuales del re-audit: ruteo del mensaje de usuario, fallback model allowlist, budget cap/audit acumulado, mirror de auditoría best-effort, manejo de `NoAllowedModel`, endurecimiento del system prompt y estado visible de gasto/cap.
3. La superficie de proveedores quedó ajustada a OpenAI + Kimi en UI (`_VISIBLE_PROVIDER_SLUGS` en `app/src/api.py`), manteniendo soporte backend para OpenAI, Anthropic, Google, Kimi y Ollama.
4. Se añadieron gestión de conversaciones y garantías HITL:
   - rename con `PATCH /workspaces/{id}/chats/{chat_id}`;
   - delete con `DELETE /workspaces/{id}/chats/{chat_id}` + `confirmation_token`;
   - aislamiento por `workspace_id`/`tenant_id`.

### Evidencias
- Código: `app/src/router/*.py`, `app/src/api.py`, `app/src/db.py`, `app/src/models.py`, `app/static/js/app.jsx`, `app/static/css/main.css`, `app/static/js/icons.jsx`.
- Tests: `app/tests/test_sl1a_router.py`, `app/tests/test_sl1a_router_endpoints.py`, `app/tests/test_config_store.py`.
- Reportes: `harness/reports/SL1a_audit_iter2.md`, `SL1a_audit_iter3.md`, `SL1a_audit_iter4.md`, `SL1a_v2_CLOSER_REPORT_v1.md`, `pytest_sl1a_iter4.log`.
- Outputs: `harness/agents/SL1a_backend.md`, `harness/agents/SL1a_router_design.md`.

### Brechas / Blockers
`Ninguna` para el alcance mínimo. Quedaron fuera por diseño: preset builder, auto-optimizador, backtest y "fábrica de niveles" (Enmienda v1.1 §7.3).

---

## SL1b — Primer draft real contra mini-KB + HITL mínimo

### Estado
**Cerrado técnicamente** (`harness/reports/AUDIT_SL1b_FUGU_v3.md` PASS formal y `harness/reports/SL1b_CLOSER_REPORT_v1.md`).

### Cómo se cerró
1. Se implementó HITL mínimo real con `draft.original_body_md` y `draft.edit_pct`; `approve_draft` calcula el diff aprobado vs. draft original con `difflib.SequenceMatcher`.
2. Se bloqueó la cita inválida: labels desconocidos como `[S9]` generan blocker.
3. Se robusteció `stale_data_block`: fuente vencida o `valid_from` futuro exige confirmación/bloquea.
4. Se añadió detección de datos duros inventados en el `body_md`.
5. Se generó un harness de 10 drafts (`app/tests/test_sl1b_dogfood_ten_drafts.py`) que escribe `harness/reports/SL1b_DOGFOOD_LOG.json`.
6. Se cerraron auditorías Fugu con fixes de update, backup, inyección HTML/JS y frescura de facts.

Métricas documentadas en `SL1b_CLOSER_REPORT_v1.md`:
- 10 drafts generados y aprobados;
- 8 `fully_sourced`;
- 2 con `[PENDIENTE — NO INVENTAR]`;
- `edit_pct` promedio 3.66 %, máximo 12.42 %, mínimo 0.0 %.

### Evidencias
- Código: `app/src/models.py`, `app/src/kb.py`, `app/src/draft_engine.py`, `app/src/api.py`, `app/src/update.py`, `app/src/backup.py`, `app/src/security/injection.py`.
- Tests: `app/tests/test_sl1b_kb_drafts.py`, `app/tests/test_sl1b_dogfood_ten_drafts.py`.
- KB demo: `docs/IDX_COMERCIAL.md`, `docs/ENT_COMERCIAL_PRODUCTOS.md`, `docs/ENT_COMERCIAL_PRECIOS.md`, `docs/ENT_COMERCIAL_STOCK.md`, `docs/ENT_COMERCIAL_EQUIVALENCIAS.md`, `docs/ENT_COMERCIAL_TERMINOS.md`, `docs/ENT_COMERCIAL_RESUMEN_DEMO.csv`.
- Prompts: `harness/prompts/sl1b_dogfood_prompts.json`.
- Reportes: `AUDIT_BLOQUEANTES_SL1b_FUGU_v1.md`, `AUDIT_FIXES_SL1b_FUGU_v1.md`, `AUDIT_SL1b_FUGU_v2.md`, `AUDIT_SL1b_FUGU_v3.md`, `FIXES_SL1b_FUGU_v1_IMPLEMENTATION.md`, `FIXES_SL1b_FUGU_v2_IMPLEMENTATION.md`, `PLAN_SL1b_CLOSER_v1.md`, `SL1b_CLOSER_REPORT_v1.md`, `SL1b_DOGFOOD_LOG.json`.

### Brechas / Blockers
- **PRC-01 abierto:** faltan datos comerciales reales de MWT/Rana Walk. Fallback activo: el draft marca `[PENDIENTE — NO INVENTAR]`. Próximo paso: CEO/Ops entrega batch para `ENT_COMERCIAL_*`.
- El dogfood es sembrado/simulado, no uso voluntario real sostenido con N definido. Próximo paso: CEO fija N y criterio de adopción de la Enmienda v1.1 §7.9.

---

## SL2 (a/b/c) — Workspaces + KB con cita

### Estado
**Cerrado** (`harness/reports/SL2_CLOSER_REPORT_v1.md`).

### Cómo se cerró
1. Se implementó ingestión MD/TXT/CSV/XLSX/PDF con FTS5 y upload robusto.
2. Se añadieron workspaces padre/hijo con `parent_id` e `inherits_kb`; la herencia no cruza tenants.
3. Se implementó cita end-to-end campo → documento → sección mediante `source_sheet`/`source_locator` en el evidence pack.
4. Se reforzó `stale_data_block` en ingestión y drafts.
5. Se propagó `tenant_id` en chunks/facts/sources y se añadieron pruebas cross-tenant.
6. Se implementaron canarios PDF/XLSX/HTML/CSV/KB text/SKILL.md contra JavaScript, macros y hidden instructions.
7. Se adelantó el sellado mínimo requerido por la Enmienda v1.1 §7.2.

### Evidencias
- Código: `app/src/models.py`, `app/src/db.py`, `app/src/kb.py`, `app/src/draft_engine.py`, `app/src/kb_extractors.py`, `app/src/security/injection.py`, `app/src/api.py`.
- Tests: `app/tests/test_sl2_kb_ingestion.py`, `test_sl2_kb_inheritance.py`, `test_sl2_citation_e2e.py`, `test_sl2_draft_validation.py`, `test_sl2_injection_canaries.py`, `test_sl2_workspace_seal.py`.
- Reportes: `harness/reports/PLAN_SL2_CLOSER_v1.md`, `PLAN_SL2_CLOSER_v2.md`, `SL2_CLOSER_REPORT_v1.md`.
- Outputs: `harness/agents/SL2a_backend_iter2.md`, `harness/agents/SL2a_frontend_iter2.md`.

### Brechas / Blockers
- **PRC-02 abierto:** falta corpus real de documentos fuente con procedencia verificable. Fallback activo: fixtures sintéticos con fuente conocida. Próximo paso: CEO/Ops entrega set real.
- La ingesta PDF/XLSX sigue siendo heurística para ciertos casos (p. ej. inferencia de columnas). Próximo paso: definir contrato de schema por proveedor/cliente cuando llegue el corpus real.

---

## SL3a — Skills / Routine Hub

### Estado
**Cerrado** (`harness/reports/SL3a_CLOSER_REPORT_v1.md`).

### Cómo se cerró
1. `app/src/skills.py` compila SKILL.md a un subconjunto canónico del manifest (`name`, `description`, `version`, `metadata`) y separa runtime (`persona`, `tools`, `schema_output`, `triggers`, `instructions`).
2. Se implementó autoría liviana con HITL: crear routine → `approved_by = None`; aprobar → ejecutar con schema output.
3. Se implementó invocación por `@nombre`: `@cotizador` resuelve routine, ejecuta y persiste `routine_run`.
4. Se añadió canario P0 de inyección en SKILL.md: "Ignore previous instructions..." → `422`.
5. Se añadió aislamiento multi-tenant de routines.

### Evidencias
- Código: `app/src/skills.py`, `app/src/api.py`, `app/src/db.py`, `app/src/models.py`.
- Tests: `app/tests/test_sl3a_skills.py`, `app/tests/test_routines_crud.py`.
- Reportes: `harness/reports/PLAN_SL3a_CLOSER_v1.md`, `SL3a_CLOSER_REPORT_v1.md`.

### Brechas / Blockers
- El runtime actual es parser/linter + ejecución a través del router, no un sandbox completo de herramientas. Suficiente para el gate de SL3a; futuro: diseñar sandbox real para `tools_allowlist` si Etapa 2 lo requiere.

---

## SL3b/c — WorkLoom + gold loop

### Estado
**Cerrado** (`harness/reports/SL3b_CLOSER_REPORT_v1.md`).

### Cómo se cerró
1. `app/src/workloom.py::list_workloom_items()` lista `routine_runs`, `drafts` y `gold_candidates` accionables, ordenados por urgencia y fecha.
2. `routine_run.task_type` captura tipo de tarea desde `routine.category`.
3. Se implementó gold loop: captura automática cuando `edit_pct <= 0.2`, promoción, aplicación a schema y re-feed como few-shot examples.
4. Se probó descenso de `edit_pct` por repeticiones sembradas del mismo `task_type`.
5. Se agregó segundo gate para campos duros: promoción de gold con precios/SKUs/stock/márgenes/fechas requiere `verified_by`.
6. Se añadió aislamiento multi-tenant en WorkLoom y gold.

### Evidencias
- Código: `app/src/workloom.py`, `app/src/gold.py`, `app/src/draft_engine.py`, `app/src/db.py`, `app/src/models.py`, `app/src/api.py`.
- Tests: `app/tests/test_sl3b_workloom_gold.py`.
- Reportes: `harness/reports/PLAN_SL3b_CLOSER_v1.md`, `SL3b_CLOSER_REPORT_v1.md`.

### Brechas / Blockers
- **PRC-03 abierto:** falta uso real sostenido para demostrar que `edit_pct` baja con el uso. Fallback activo: sesiones sembradas que prueban el mecanismo.
- El umbral `edit_pct <= 0.2` y la promoción a `ACTIVE` son placeholders. Próximo paso: decisión CEO/arquitectura.

---

## SL3.5 — Sellado + llave graduada

### Estado
**Cerrado** (`harness/reports/SL3_5_CLOSER_REPORT_v1.md`).

### Cómo se cerró
1. Se añadió SQLCipher para workspaces confidenciales: `workspace.confidential`, `workspace.passphrase`, `workspace.workspace_db_path`.
2. `app/src/db.py::connect_workspace_data_db` abre DB separada con `PRAGMA key`; workspaces normales siguen en SQLite plano.
3. `app/src/api.py::get_workspace_db` exige `x-workspace-passphrase` para workspaces confidenciales.
4. Se implementó HMAC por workspace para `kb_source`, `kb_fact` y `draft`.
5. Se probó fuga cross-workspace = 0 en modo plano y cifrado con canarios.
6. Se probó backup/export/restore de workspace cifrado.
7. Se bloqueó herencia cross-tenant y acceso cross-tenant a workspaces confidenciales.

### Evidencias
- Código: `app/src/db.py`, `app/src/api.py`, `app/src/backup.py`, `app/src/seal.py`, `app/src/models.py`.
- Tests: `app/tests/test_sl3_5_seal.py`, `app/tests/test_sqlcipher_temp.py`.
- Reportes: `harness/reports/PLAN_SL3_5_CLOSER_v1.md`, `SL3_5_CLOSER_REPORT_v1.md`.

### Brechas / Blockers
- **PRC-04 abierto:** falta dataset confidencial real. Fallback activo: canarios sintéticos.
- Revisar que `api_seal_check` no devuelva material sensible como `seal_id` en payload de diagnóstico.

---

## SL4 — Empaque desktop

### Estado
**Cerrado para dogfood interno (D4) sobre Windows** (`harness/reports/SL4_CLOSER_REPORT_v1.md`).

### Cómo se cerró
1. PyInstaller + pywebview: `app/FaberLoom.spec`, build script actualizado para artefactos `FaberLoom.exe`/`FaberLoom-Setup.exe` y `console=False`.
2. Instalador sin terminal: `app/src/installer.py` + `app/FaberLoom_Installer.spec`, con GUI tkinter, modo silencioso, instalación en `%LOCALAPPDATA%\Programs`, acceso directo y `uninstall.bat`.
3. Firma de código: `app/build.py --sign` soporta certificado real y fallback self-signed en `app/src/packaging.py`.
4. Auto-update firmado: `app/src/update.py` usa Ed25519, pinned public keys, rechazo de downgrade, bloqueo por mutaciones pendientes y rollback.
5. Backup/export/restore se reutiliza desde SL3.5.
6. Rebrand verificado: `app/tests/test_post_sl1a_rebrand.py` exige `FaberLoom.exe`, `FaberLoom-Setup.exe`, título FaberLoom y migración de directorio legacy.

### Evidencias
- Código: `app/build.py`, `app/src/installer.py`, `app/src/packaging.py`, `app/src/update.py`, `app/src/backup.py`, `app/src/main.py`, `app/VERSION`, `app/pyproject.toml`, `app/FaberLoom.spec`, `app/FaberLoom_Installer.spec`.
- Tests: `app/tests/test_sl4_packaging.py`, `app/tests/test_post_sl1a_rebrand.py` y tests de update en `app/tests/test_sl1b_kb_drafts.py`.
- Docs: `docs/build/BUILD_DESKTOP.md`.
- Reportes: `harness/reports/PLAN_SL4_CLOSER_v1.md`, `SL4_CLOSER_REPORT_v1.md`.
- Ledger: `PROCUREMENT_LEDGER.md` (PRC-05/06/07).

### Brechas / Blockers
- **PRC-05 abierto:** certificado Authenticode Windows. Fallback self-signed verificado.
- **PRC-06 abierto:** Apple Developer + notarización Mac. Mac diferido.
- **PRC-07 abierto:** llave de firma de auto-update publicable. Fallback self-signed verificado.
- Deuda de distribución: build firmado real, CI de `build.py --sign`, smoke en OS destino y revisar exclusión de datos locales del bundle.
- Naming residual: `docs/build/BUILD_DESKTOP.md` y `.spaceloom_rollback` aún usan el nombre histórico; los `.spec` ya fueron renombrados a FaberLoom.

---

## SL5 — Correo (IMAP/SMTP)

### Estado
**Parcial — implementado y probado técnicamente, pero sin cierre formal.**  
`harness/state.json` incluye SL5 en `completed_phases`, pero `current_phase = SL5` y `status = needs_review`. No hay `harness/reports/SL5_CLOSER_REPORT_*.md`. Además, `PROCUREMENT_LEDGER.md` marca PRC-09 como **DIFERIDO**.

### Cómo se cerró
No hay documento formal de cierre. Lo que sí existe implementado:

1. Connector IMAP read-first (`app/src/connectors/imap.py`) con credenciales desde `FABERLOOM_IMAP_*`; sin credenciales devuelve `503`.
2. `POST /api/workspaces/{workspace_id}/mail/sync` crea `mail_message`.
3. `POST /mail/{mail_id}/draft` genera draft vinculado y marca el correo como `drafted`.
4. `POST /mail/{mail_id}/send` exige:
   - draft aprobado;
   - `confirmation_token`;
   - `idempotency_key`;
   - outbox para evitar reenvío;
   - SMTP sólo tras aprobación.
5. Aislamiento por workspace/tenant en list, draft y send.

### Evidencias
- Código: `app/src/connectors/imap.py`, `app/src/api.py` (endpoints `/mail/sync`, `/mail/{id}/draft`, `/mail/{id}/send`), `app/src/models.py`.
- Tests: `app/tests/test_sl5_imap.py` (sync, draft, send sin aprobación, send con aprobación, credenciales faltantes, aislamiento) y `app/tests/test_p0_security.py::test_send_requires_confirmation_and_idempotency_key`.
- Reportes: `harness/reports/AUDIT_SL3_4_5_FUGU_MANUAL.md` (PASS técnico) y `harness/reports/AUDIT_FUGU_CODEX_SL3_4_5.md` (gaps históricos).

### Brechas / Blockers
- Falta `SL5_CLOSER_REPORT`. Próximo paso: correr el CLOSER loop o ratificar formalmente el diferimiento.
- **PRC-09 diferido:** faltan credenciales IMAP/SMTP reales rotadas + OAuth. Sin esto no hay correo real de producción.
- El ledger dice que el connector queda tras `email_connector_enabled=false`, pero no se encontró ningún `email_connector_enabled` en `app/src/`. Próximo paso: implementar feature flag o corregir el ledger.
- Pendiente endurecer parsing de direcciones y sanitización HTML en `app/src/connectors/imap.py` antes de habilitar correo real.

---

## Resumen ejecutivo

| SL | Estado | Evidencia principal | Bloqueante técnico |
|---|---|---|---|
| SL0 | Cerrado | `SL0_final_eval.md`, `test_sl0_backend.py` | Ninguno |
| SL1a | Cerrado | `SL1a_audit_iter4.md`, `SL1a_v2_CLOSER_REPORT_v1.md` | Ninguno |
| SL1b | Cerrado técnico | `AUDIT_SL1b_FUGU_v3.md`, `SL1b_CLOSER_REPORT_v1.md` | Ninguno |
| SL2 | Cerrado | `SL2_CLOSER_REPORT_v1.md` | Ninguno |
| SL3a | Cerrado | `SL3a_CLOSER_REPORT_v1.md` | Ninguno |
| SL3b/c | Cerrado | `SL3b_CLOSER_REPORT_v1.md` | Ninguno |
| SL3.5 | Cerrado | `SL3_5_CLOSER_REPORT_v1.md` | Ninguno |
| SL4 | Cerrado D4 Windows | `SL4_CLOSER_REPORT_v1.md` | Ninguno para dogfood |
| SL5 | Parcial | `test_sl5_imap.py`, auditoría PASS técnica, sin closer | Falta cierre formal + PRC-09/flag |

**Conclusión:** Etapa 1 está funcionalmente implementada y verde en el stack local FastAPI + SQLite: **221 tests pasan**. SL0–SL4 tienen cierre formal. **SL5 es el único stream que no puede declararse plenamente cerrado** porque carece de CLOSER report, está en `needs_review`, su dependencia real PRC-09 está diferida y el feature-flag descrito por el ledger no existe en el código.

El siguiente paso declarado por el harness es `E0_CEO_decisions_and_MWT_pack`: la transición de dogfood técnico a uso/distribución real depende de datos MWT reales y decisiones CEO.

---

## Lista de gaps/blockers cruzados

1. **SL5 sin cierre formal:** falta `harness/reports/SL5_CLOSER_REPORT_*.md`; `state.json` deja SL5 en `needs_review`.
2. **SL5 feature flag ausente:** `PROCUREMENT_LEDGER.md` menciona `email_connector_enabled=false`, pero el código no contiene ese flag.
3. **PRC-01:** datos comerciales reales MWT/Rana Walk.
4. **PRC-02:** corpus real de documentos fuente con procedencia verificable.
5. **PRC-03:** sesiones de uso real para demostrar descenso real de `edit_pct`.
6. **PRC-04:** dataset confidencial real para fuga cross-workspace con datos reales.
7. **PRC-05:** certificado Authenticode Windows.
8. **PRC-06:** Apple Developer + notarización Mac.
9. **PRC-07:** llave de firma auto-update publicable.
10. **PRC-08:** registro de marca FaberLoom/SpaceLoom.
11. **PRC-09:** credenciales IMAP/SMTP reales + OAuth.
12. **Decisiones CEO pendientes:** carve-out/freeze, licencia FSL, dedicación, SL5 in/out, calendario, criterio de adopción N, cifrado obligatorio siempre vs. sólo confidenciales, STACK-01.
13. **Deuda P0/P1 mitigada pero no perfecta:** cross-origin guard existe, pero falta token local/CSRF completo; parser de correo y sanitización HTML deben endurecerse antes de correo real.
14. **Sandbox de tools:** `skills.py` no ejecuta herramientas en sandbox real; futuro de Etapa 2.
15. **Packaging distribuible:** falta build firmado real, smoke de OS destino y revisar que no se empaquen datos locales.
16. **Naming residual:** `docs/build/BUILD_DESKTOP.md` y `.spaceloom_rollback` conservan "SpaceLoom"; los `.spec` ya usan FaberLoom.
