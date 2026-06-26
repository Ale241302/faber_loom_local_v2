# Auditoría Fugu — Veredicto SL2b/c · SL3a · SL3b/c · SL3.5 · SL4 · SL5

**Fecha:** 2026-06-25  
**Rol:** fugu / agente senior integrador  
**Alcance:** validación de la entrega técnica de una sola pasada de SL2b/c, SL3a, SL3b/c, SL3.5, SL4 y SL5 sobre el stack local FastAPI + SQLite.  
**Tests ejecutados:** `pytest app/tests` → **112 passed, 1 warning**.

---

## Resumen ejecutivo

**Veredicto global técnico: `PASS` formal.**

Se implementaron e integraron de una sola pasada:

| Hito | Entregable principal | Tests |
|---|---|---|
| SL2b/c | Ingesta robusta de KB (CSV, XLSX, PDF, MD, TXT), aliases por workspace, validación de labels `[S1]`, stale como blocker | `test_sl2_kb_ingestion.py`, `test_sl2_draft_validation.py` |
| SL3a | Skill Hub: parser/validador de `SKILL.md`, sandbox anti-inyección, rutinas, invocación `@nombre` | `test_sl3a_skills.py` |
| SL3b/c | WorkLoom HITL queue + gold loop: `edit_pct`, approve/reject, gold candidates, promoción | `test_sl3b_workloom_gold.py` |
| SL3.5 | Workspace seal: HMAC SHA-256 por workspace para `kb_source`, `kb_fact`, `draft`, `routine_run` | `test_sl3_5_seal.py` |
| SL4 | Packaging desktop: spec PyInstaller, build script, version file, update firmado | `test_sl4_packaging.py` |
| SL5 | IMAP/SMTP connector: sync read-first, draft vinculado, envío solo tras aprobación HITL | `test_sl5_imap.py` |

Todos los tests del repositorio pasan (`112 passed`). La advertencia de `starlette.testclient` es meramente de deprecación de dependencia y no bloquea el hito.

---

## Veredicto por dimensión

| Dimensión | Veredicto | Justificación |
|---|---|---|
| **SL3a Skill Hub** | **PASS** | `compile_skill_md` extrae frontmatter YAML/JSON, rechaza `<script`, `javascript:`, `import os`, `eval(`, fórmulas Excel y código peligroso. `execute_skill` enruta a través del router existente, retorna `succeeded`/`requires_hitl`/`failed` y genera evidence. `@mention` invoca rutina por trigger y persiste `routine_run`. |
| **SL3b/c WorkLoom + Gold** | **PASS** | `routine_run` almacena `edit_pct`. `approve_routine_run` genera `gold_candidate` cuando `edit_pct <= 0.2`. `reject_routine_run` cancela el run. `promote_gold_candidate` actualiza `learned_output_json`. WorkLoom endpoint lista runs por estado con workspace isolation. |
| **SL3.5 Workspace seal** | **PASS** | Cada workspace tiene `seal_id` único. `routine_run`, `kb_source`, `kb_fact` y `draft` llevan `workspace_hmac` SHA-256 (`seal_id`, `row_id`, `workspace_id`). `list_*` descarta filas con HMAC roto. Tests simulan fugas cross-workspace y son bloqueadas. |
| **SL4 Packaging** | **PASS** | Existe `SpaceLoom.spec` (PyInstaller, `console=False`, incluye `static`), `build.py` con `create_update_manifest`, y archivo `VERSION`. El módulo `app.src.update` mantiene firma/verificación con clave pública pinned, downgrade protection y rollback. |
| **SL5 IMAP/SMTP** | **PASS** | `fetch_unread_messages` lee IMAP y crea `mail_message`. Genera draft vinculado. Envío SMTP retorna `409` sin aprobación y `200` con aprobación. Workspace isolation verificado. Credenciales desde entorno; sin credenciales retorna `503`. |
| **Regresión SL0-SL2** | **PASS** | Los 112 tests incluyen la cobertura previa; no se detectaron regresiones. |

---

## Issues menores / deuda técnica (no bloquean)

1. **Dependencia `httpx2`:** Starlette depreca `httpx` en `TestClient`; se recomienda migrar a `httpx2` para eliminar el warning.
2. **Stack local vs. stack canon E0-E3:** Esta entrega usa FastAPI + SQLite para validar contratos de skills, WorkLoom, sellado y conectores. El plan v6 es agnóstico de stack (STACK-01 pendiente CEO), por lo que los contratos probados aquí son portables, pero la implementación no reemplaza al SPINE de M16/M08/M09/M15/M12/M11.
3. **Gold loop thresholds:** El umbral `edit_pct <= 0.2` es un placeholder razonable; el criterio de promoción final a `ACTIVE` (segundo aprobador, shadow/active) requiere decisión de arquitectura/CEO.
4. **SL5 credenciales reales:** Los tests usan mocks/entorno; la integración real con el mailbox de Kimi Work requiere credenciales IMAP/SMTP y DPA firmado (bloqueante operativo).
5. **Firma de código:** SL4 valida el contrato de update firmado, pero los certificados de firma de código Apple/Microsoft para el ejecutable desktop siguen pendientes.
6. **Eventos y outbox:** Los eventos de skill/gold/mail no pasan aún por un outbox transaccional M15 ni por WebSocket fanout; esto queda para cuando se construya el SPINE.

---

## Mapeo a tracks del plan v6

| Track v6 | Contrato cubierto parcialmente por esta entrega | Gap a cerrar con SPINE |
|---|---|---|
| T1 AI Work Pipeline (M10/M13) | `ActionContext` simplificado via `routine_run`; HITL approve/edit/reject; gold candidate | M10 L1 classifier real, M11 D9 policy gate, M15 outbox, M16 RLS real |
| T2 Learning/Memory (M14/M17) | `OutcomeEntry` mínimo via `gold_candidate` y `edit_pct`; `learned_output_json` | M14 ledger completo, M17 Letta namespaces, MemoryConflictGuard |
| T3 Desktop Runtime (M18/M19/M20) | Contrato de auto-update firmado y version file | Electron app real, offline sync, particiones seguras, keychain |
| T4 Eventing (M15) | No implementado | Outbox transaccional + Redis Streams + WS fanout |
| T0 Bootstrap (M07) | No implementado | Wizard, invitaciones, DPA state, mailbox OAuth, seed skills shadow |

---

## Bloqueantes operativos persistentes

| Bloqueante | Quién debe actuar | Impacto |
|---|---|---|
| Pack de datos MWT reales autorizado y validado por Alvaro | CEO (Alvaro) | Sin datos reales no se puede validar E2 ni calibrar gold threshold |
| Decisiones CEO: scope/freeze E1, licencia FSL, dedicación dev, ¿SL5 in/out?, calendario, criterio de adopción N, cifrado local | CEO (Alvaro) | Bloquean declarar hitos aprobados operativamente |
| Ratificación de STACK-01 (FastAPI/SQLite local vs Django/Postgres vs híbrido) | CEO + arquitecto | Determina si esta implementación se mantiene o se migra |
| Credenciales IMAP reales de Kimi Work | CEO / ops | Bloquea SL5 en producción |
| Presupuesto/certificados de firma de código | CEO / ops | Bloquea SL4 release firmado en desktop |
| DPA firmado para datos N3/N4 | CEO / compliance | Bloquea cualquier salida externa real (SMTP, LLM con PII) |

---

## Recomendación

1. Declarar **SL2b/c, SL3a, SL3b/c, SL3.5, SL4 y SL5 técnicamente aprobados** en el stack local FastAPI/SQLite.
2. No avanzar a tracks paralelos del plan v6 (T0-T4) ni forkear el SPINE hasta que se resuelvan los bloqueantes CEO y se ratifique STACK-01.
3. Una vez resueltos, la primera prioridad es construir el SPINE serial (M16/M08/M09/M15/M12/M11) antes de portar los contratos ya probados a la infraestructura definitiva.

---

## Próximo paso

Pasar el reporte a revisión del CEO y, tras ratificación de scope/stack, iniciar el SPINE serial M16+M08.
