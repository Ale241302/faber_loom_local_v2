# Estado de avance — SpaceLoom Etapa 1 + Camino B Foundation Beta

**Fecha:** 2026-07-06
**Fuentes:** `PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` (v1.0 + Enmienda v1.1), `Plan/CaminoB_FoundationBeta/README.md`, `cierre_etapa1_faberloom.md` (auditoría 2026-06-30), `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md`, código en `app/`.

---

## Resumen ejecutivo

Se cumplieron los dos tracks:

1. **SpaceLoom Etapa 1 (spike E1):** SL0–SL4 cerrados formalmente; SL5 (correo) implementado técnicamente pero diferido/sin cierre formal. Registrado como "SpaceLoom Spike E1" (no canónico, DEC-011).
2. **Camino B Foundation Beta v1.3.1:** el SPINE serial completo (M16→M08→M09→M15→M12→M11→M07) quedó **verde** en el stack canónico Django/Postgres (tests en VPS), y posteriormente **los 14 módulos M07–M20 fueron portados a la app local** (`app/src/foundation/`) sobre FastAPI/SQLite.

Suite actual en `app/`: **342 tests** (vs. 221 al cierre del 2026-06-30). Versión de app: **0.2.0**. Graphify: **25.752 nodos / 35.013 edges / 1.710 comunidades**.

---

## Parte 1 — Plan SpaceLoom Etapa 1 (SL0–SL5)

| Hito | Objetivo del plan | Estado | Qué se hizo |
|---|---|---|---|
| SL0 | Esqueleto + seed | ✅ Cerrado | FastAPI + SQLite + pywebview; modelo de datos con migraciones (`SCHEMA_VERSION 17`); seed workspace `mwt-demo`; costuras contract-first: campos latentes (`tenant_id`, `actor_id`, `routine_version`…), `Context`, `AuditWriter` (audit_log + `audit.jsonl`), tablas `routine`/`routine_run` |
| SL1a | Router mínimo + chat | ✅ Cerrado | `app/src/router/`: prioridad, provider allowlist, budget cap, fallback, cost ledger; BYOK OpenAI/Anthropic/Google/Kimi/Ollama (UI: OpenAI+Kimi); gestión de chats con delete + `confirmation_token` |
| SL1b | Draft real vs mini-KB + HITL | ✅ Cerrado técnico | HITL con `edit_pct` (difflib vs original); cita obligatoria a fuente, bloqueo de citas inválidas, `stale_data_block`, detección de dato inventado; dogfood de 10 drafts (edit_pct prom. 3.66%) |
| SL2a/b/c | Workspaces + KB | ✅ Cerrado | Ingestión MD/TXT/CSV/XLSX/PDF con FTS5; workspaces padre/hijo con herencia (`inherits_kb`, sin cruzar tenant); cita end-to-end campo→doc→sección; canarios de injection (PDF/XLSX/HTML/CSV/KB/SKILL.md); sellado mínimo adelantado (Enmienda §7.2) |
| SL3a | Skills / Routine Hub | ✅ Cerrado | `skills.py` compila SKILL.md a subconjunto del manifest v2; autoría con HITL (crear→aprobar→ejecutar); invocación `@nombre` (`@cotizador`); canario de injection en SKILL.md → 422 |
| SL3b/c | WorkLoom + gold loop | ✅ Cerrado | Cola por urgencia (`workloom.py`); gold loop: captura auto con `edit_pct ≤ 0.2`, promoción, re-feed few-shot; segundo gate `verified_by` para campos duros; descenso de edit_pct demostrado con sesiones sembradas |
| SL3.5 | Sellado + llave graduada | ✅ Cerrado | SQLCipher para workspaces confidenciales (DB separada + passphrase); HMAC por workspace; **test de fuga cross-workspace = 0** (plano y cifrado); backup/export/restore cifrado |
| SL4 | Empaque desktop | ✅ Cerrado (D4 Windows) | PyInstaller + pywebview → `FaberLoom.exe` / `FaberLoom-Setup.exe`; instalador GUI sin terminal; firma (self-signed fallback); auto-update Ed25519 con anti-downgrade y rollback |
| SL5 | Correo IMAP/SMTP | ⚠️ Parcial / diferido | Connector IMAP read-first, `/mail/sync`, `/mail/{id}/draft`, `/mail/{id}/send` con draft aprobado + `confirmation_token` + `idempotency_key` + outbox. Sin cierre formal (PRC-09 diferido). Post-auditoría se agregaron `test_sl5_feature_flag.py`, `test_sl5_mail.py`, `test_sl5_prompt_injection.py` (flag y canarios ya cubiertos) |

## Parte 1.5 — Epics Foundation Beta (E2-x) en `app/`

| Epic | Estado | Qué se cerró | Documento |
|---|---|---|---|
| E2-0 Context + audit + tenant canario | ✅ Cerrado | `Context` con `workspace_id/tenant_id/user_id`; `AuditWriter`; seed canario permanente; runbook Postgres; segundo gate gold. | `docs/CONTEXT_RLS_CONTRACT_E2.md` |
| E2-2 Correo compartido | ✅ Cerrado | Flag `FABERLOOM_SHARED_INSTANCE`; migración v25; bloqueo de fallback IMAP/SMTP por env vars; rotación de credenciales; UI de app-password. | `docs/CORREO_E2_CIERRE.md`, `docs/OPERACION_CORREO_E2.md` |
| E2-3 KB compartida + gold L2→L3 | ✅ Cerrado | Máquina de estados `candidate → active_l2 → l3_pending → l3 / rejected`; herencia KB con preservación de citas; k-anon ≥ 5; gate curador/CEO; verificador independiente en campos duros. | `docs/E2_3_KB_GOLD_CIERRE.md` |

Notas: rebrand SpaceLoom → **FaberLoom** tras SL1a (cubierto por `test_post_sl1a_rebrand.py`). Riesgos P0 del plan verificados en tests: envío sin HITL, injection multi-formato, fuga cross-workspace, dato inventado (`test_p0_security.py` + canarios).

**Gaps que siguen abiertos (procurement/decisiones, no código):** PRC-01/02 datos reales MWT, PRC-03 adopción real (N sin fijar), PRC-05/06/07 certificados de firma, PRC-09 credenciales de correo; decisiones CEO: calendario, licencia FSL, criterio de adopción.

---

## Parte 2 — Camino B Foundation Beta (M07–M20)

### 2.1 SPINE canónico (Django/Postgres) — verde

Según `Plan/CaminoB_FoundationBeta/README.md`, los 7 módulos del SPINE se implementaron y pasaron sus gates en VPS (`pytest --create-db`):

| Módulo | Gate | Tests VPS |
|---|---|---:|
| M16 Tenant Isolation | RLS FORCE + middleware + Redis/Celery/MinIO/Letta por tenant | 12 |
| M08 Auth Session | argon2id + sesiones Redis + TOTP owner + revocación | ✅ |
| M09 RBAC | 5 roles, membership, resolver server-side, hats | ✅ |
| M15 Outbox Streams | outbox + relay Celery + WS fanout + reconexión `?since=` | ✅ |
| M12 Audit Trail | 18 campos, hash chain, append-only, export/validate | 11 |
| M11 D9 Policy Gate | fail-closed, DPA, ceilings, pre-egress con PII | 9 |
| M07 Bootstrap Wizard | wizard 9 pasos, seed agents shadow, activación fail-closed | 8 |

### 2.2 Port local-first a `app/` (FastAPI/SQLite) — 14/14 módulos

Todos los módulos M07–M20 fueron portados de Django a `app/src/foundation/` (BD propia `foundation.sqlite3`, tablas `fnd_*`, rutas `/foundation/*`):

- **Contrato común** (`core.py`): esquema idempotente por `register_schema`, tablas spine compartidas (tenants, users, sessions, roles, audit_log con hash chain, events/outbox), PBKDF2, TOTP stdlib, `require_session`/`require_permission`, `audit_log()` y `emit_event()`. M16 (RLS) se traduce a scoping estricto fail-closed por `tenant_id` en toda query.
- **SPINE:** `m16_tenant_isolation` (+ endpoint de verificación de aislamiento), `m08_auth_session` (login 2 pasos con TOTP, sesiones `fnds_...`), `m09_rbac` (roles/permisos, guardrail ≥1 owner), `m15_outbox_streams` (event log + polling realtime), `m12_audit_trail` (lectura/verify/export, inmutable), `m11_policy_gate` (políticas JSON fail-closed), `m07_bootstrap` (wizard reducido al núcleo local-first).
- **Track operativo:** `m10_classifier` (Tier0 reglas + L1 LLM), `m13_draft_hitl` (máquina de estados + regla four-eyes: aprobador ≠ creador), `m14_outcome_ledger` (outcomes fusionados en una tabla), `m17_memory` (layers working/episodic/persistent en SQLite).
- **Desktop:** `m18_desktop_auth` (device secret cifrado local, port de keytar), `m19_offline_sync` (cursores, delta/full refresh, cola de mutaciones), `m20_auto_update` (canales stable/beta, `min_supported_client_version`, force_update).
- **Frontend:** vistas React UMD dedicadas en `app/static/js/`: `fnd_core.jsx`, `fnd_spine.jsx`, `fnd_ops.jsx`, `fnd_desktop.jsx`, `foundation.jsx`, `foundation_app.jsx` (además del shell `app.jsx`).
- **Tests foundation:** `test_foundation_spine.py`, `test_foundation_ops.py`, `test_foundation_desktop.py` (~61 tests junto con multi-tenant/mail), más `test_tenants_multi.py`, `test_user_isolation.py`, `test_tenant_contamination.py` — multi-tenant real con verificación anti-contaminación.

### 2.3 Multi-tenant y deploy

- Multi-tenant pasó de "campo latente" (estado al 2026-06-30) a **aislamiento real por tenant** en la app local (scoping fail-closed + tests de contaminación cruzada).
- Deploy web del spike: Docker Compose + nginx en VPS (`/opt/faber_loom`, `app.faberloom.ai`), login JWT multi-usuario. Pendientes del manifiesto: renombrar path/dominio a spike, portar aprendizajes a specs canónicos.

---

## Stack actual de `app/`

| Capa | Tecnología |
|---|---|
| Backend | Python 3.13 + FastAPI + Pydantic v2 |
| DB | SQLite (`faberloom.sqlite3` + `foundation.sqlite3`) + sqlcipher3 + FTS5 |
| Frontend | React 18 UMD + Babel standalone + CSS custom (servido por FastAPI) |
| Desktop | pywebview + PyInstaller (instalador GUI, auto-update Ed25519) |
| Auth | JWT (app) + sesiones foundation con TOTP/PBKDF2 |
| LLM | Router BYOK: OpenAI / Anthropic / Google / Kimi / Ollama |
| Deploy | Docker Compose + nginx (VPS Ubuntu 24.04) |
| Tests | 342 tests pytest |

---

## Pendientes consolidados

1. E2-4: routing / ledger / modo auto; continuar el track Foundation Beta.
2. SL5: cierre formal o ratificación del diferimiento; credenciales reales (PRC-09).
3. Datos reales MWT para KB/adopción (PRC-01/02/03) y criterio de adopción N (CEO).
4. Certificados de firma Windows/Mac y llave de update publicable (PRC-05/06/07).
5. Acciones del manifiesto del spike: renombrar path/dominio, `SPEC_FB_SPIKE_E1_LESSONS_LEARNED`, portar 7 aprendizajes a specs canónicos.
6. Decisión CEO de calendario Foundation Beta (8–10 sem. dogfood vs 14–18 distribuible) y sunset del spike cuando Foundation Beta entregue tenant MWT operativo.
