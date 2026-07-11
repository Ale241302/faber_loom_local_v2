# Agent Instructions — FaberLoom SpaceLoom

Este proyecto se desarrolla con un **Agent Harness** autónomo que orquesta agentes
especializados a través de Codex CLI (`codex exec -p fugu`) y mantiene un knowledge
graph con [graphify](https://github.com/safishamsi/graphify).

## Cómo trabajar aquí

1. **No modifiques código a mano sin consultar el harness.** Si llegaste a este repo
   como agente invitado por Kimi, espera a recibir un prompt estructurado del
   orquestador.

2. **Lee el plan vigente** antes de cualquier tarea:
   - `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1.md`

3. **Respeta el sistema de marca** en `@Diseños`:
   - Paleta fija: `#F4F1ED`, `#1F1E1C`, `#C96442`, `#5A6B7C`, `#FFFFFF`, etc.
   - Tipografía: EB Garamond Italic (voz), Geist (UI), Geist Mono (datos).
   - Iconos: 24×24, stroke 1.75, `currentColor`.
   - Isotipo: nudo 3×3 tejido.

4. **Costuras contract-first** (no negociables):
   - Campos latentes en tablas: `tenant_id`, `actor_id`, `actor_role_at_decision`,
     `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by`.
   - Capa `Context(workspace_id, tenant_id=None, user_id=None)` en toda query; helpers críticos
     deben llamar `enforce_tenant_scoped(ctx)` (fail-closed).
   - `AuditWriter` hoy `audit.jsonl`, mañana outbox/tabla; eventos llevan `correlation_id`.
   - Auth/session convergencia: cookie HttpOnly `faberloom_at` + `GET /api/me`; no leer JWT desde
     `localStorage`.
   - Tenant canario permanente (`workspace.is_canary=1`, `tenant_id='canary'`) es gate obligatorio
     para E2-3.
   - Segundo gate gold: hard fields requieren `verified_by` distinto de `approved_by`.
   - Router abstrae proveedor; BYO-key hoy, keys gestionadas mañana.

5. **Riesgos P0** — cualquier violación detiene el hito:
   - Envío/borrado sin HITL (doble confirmación).
   - Injection por contenido (email/PDF/HTML/Excel/SKILL.md).
   - Fuga cross-workspace.
   - Dato inventado sin fuente en KB.

6. **Knowledge graph:**
   - Antes de responder preguntas de arquitectura, lee `graphify-out/GRAPH_REPORT.md`.
   - Después de modificar código, ejecuta `graphify update .`.

## Estructura de carpetas

- `app/` — aplicación SpaceLoom (FastAPI + pywebview + React UMD).
- `harness/` — orquestador y prompts del agent harness.
- `harness/agents/` — outputs de cada agente senior.
- `harness/reports/` — auditorías y evaluaciones.
- `Plan/` — planes de desarrollo.
- `Diseños/` — sistema de marca, tipografía, iconografía y shell.
- `graphify-out/` — knowledge graph generado (no editar a mano).

## Comandos útiles

```bash
# Activar entorno
source .venv/Scripts/activate

# Actualizar knowledge graph
graphify update .

# Correr harness manualmente (modo fases SLx)
python harness/orchestrator.py

# Correr harness en modo loop (SPEC→PLAN→DELEGAR/IMPLEMENTAR→VERIFICAR→REPORTAR)
python harness/loop_orchestrator.py init-config
python harness/loop_orchestrator.py run --title "Título" --description "Descripción del ticket"

# Correr app en desarrollo (después de SL0)
cd app && python -m uvicorn src.main:app --reload
```


<claude-mem-context>
# Memory Context

# [faber_loom_local_vv2] recent context, 2026-07-10 10:37am GMT-5

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (18,194t read) | 791,678t work | 98% savings

### Jul 5, 2026
S366 Cleanup of dead localStorage token code in app.jsx and related files after P0 HttpOnly cookie migration (Jul 5, 11:44 PM)
S367 FaberLoom auth cleanup — complete HttpOnly-cookie migration in web UI (app.jsx, fnd_core.jsx, foundation/core.py) (Jul 5, 11:45 PM)
S415 Audit of 5 claimed P0 blockers in FaberLoom codebase — verification against actual code (Jul 5, 11:47 PM)
### Jul 8, 2026
S417 Resume session after context compaction — verify VPS deploy of P0 fixes #1, #3, #4 and confirm production health (Jul 8, 9:31 AM)
1425 9:56a 🔴 P0 #1: Signup payload field mismatch fixed
1426 " 🔴 P0 #3: faster-whisper and ffmpeg added to Docker runtime
1430 10:07a 🔵 Full test suite passes: 509 passed, 12 skipped after all P0 fixes
1431 10:08a ✅ Six P0 fix files staged for commit
1432 10:09a ✅ P0 fixes committed to main — SHA 1c95879
1433 " ✅ P0 fixes pushed to GitHub — faber_loom_local_v2 main
1434 " 🔵 FaberLoom VPS stack: FastAPI + PostgreSQL + MinIO on shared mwt_default network
1435 " 🔵 VPS SSH access: 187.77.218.102 port 2222, alias "faberloom"
1436 " 🔵 VPS compose working directory is /opt/faber_loom, not /opt/faberloom
1437 " 🔴 Signup Form Field Mismatch Fixed
1438 " 🔴 faster-whisper and ffmpeg Added to Docker Runtime
1439 " 🔴 Audit Trail Added for Identity Mutations and Key-Access Grants
1440 " ✅ P0 Fixes Deployed to VPS at /opt/faber_loom
1441 10:16a 🔵 VPS SSH Access Configuration
S416 Fix P0 blockers #1, #3, #4 → push to GitHub → deploy to VPS (continued session after context compaction) (Jul 8, 10:16 AM)
S418 Fix P0 blockers #1, #3, #4 → push to GitHub → deploy to VPS → verify in production (COMPLETE) (Jul 8, 10:16 AM)
1442 10:19a ✅ VPS Docker Image faber_loom-api:latest Successfully Rebuilt
1443 10:21a ✅ faberloom-api Container Recreated with P0 Fix Image
1444 " 🔵 Production API Health Confirmed Post-Deploy — Schema v34, PostgreSQL Connection Rollbacks Observed
1445 " 🔵 All Three P0 Fixes Verified Inside Running Production Container
1446 " ⚖️ Memory Note Written: system-workspace-seed-for-audit Pattern
1447 10:25a ✅ Project Memory Index Initialized at memory/MEMORY.md
S421 User override to fix all deferred P0s and deploy to VPS — primary session now investigating key_broker.py and draft_engine._build_evidence_pack to implement P0-5 (Jul 8, 10:25 AM)
1448 10:29a ⚖️ Full E3 Milestone Completion Tasked — All Hitos E3-0 Through E3-6
1450 " 🔵 send_message in imap.py Is the Active SMTP Path — Explicitly No HITL, smtp.py Fully Orphaned
1449 10:30a 🔵 SMTP Connector (smtp.py) Is Orphaned — Mail Send Endpoint Uses Different send_message Function
1451 10:31a 🔄 api.py Import Changed to Wire connectors/smtp.py — Call Sites Not Yet Updated
1452 10:32a ⚖️ E3 Full-Completion Sprint Initiated
1454 10:33a 🔴 E3-0 P0-2: Mail Send Rewired Through Hardened smtp.send_email Connector
1453 10:46a 🟣 E3-0 SMTP HITL Connector Tests All Green
1455 10:48a 🔵 ObjectStore: Dual-Backend Architecture (MinIO + Memory Fallback)
1456 " 🔵 E3-3 Key Broker Architecture: CLOSED Default + Content Read Seams Mapped
1457 " ⚖️ E3 Full-Completion Mandate Issued — All Six Milestones Must Reach DoD
1458 11:00a 🟣 check_canary_isolation_postgres.py — N-tenant generalized leak checker added (E3-1)
1459 " 🟣 http_evidence_fetcher upgraded with real SSRF guard — _assert_public_url blocks private/loopback/link-local IPs
1460 " 🔵 Primary session re-applied already-committed E3-4 edits — duplicate commit attempt produced same SHA 195d976
1461 11:16a ⚖️ FaberLoom E3 Full-Completion Sprint Initiated
1463 " 🟣 P0-4 Committed: RLS Canary Generalized to All Tenants + SSRF Hardening on C0-2 Fetcher
1464 11:17a 🟣 Full Test Suite Green After E3 Sprint — 520 Passed, 0 Failures
1465 11:21a 🔵 VPS Deployment Target Identified — SSH on Port 2222, Already at Latest main
1462 11:22a 🟣 E3-2 Generalized N-Tenant RLS Canary Tests Created and Passing
1466 " 🟣 E3 Sprint Commits Pushed to GitHub and Deployed to VPS
1467 11:28a 🟣 API Container Rebuilt and Restarted on VPS with E3 Sprint Code
1468 11:31a 🟣 Production API Health Verified — All E3 New Symbols Import Clean on VPS
1469 11:33a ✅ E3 Audit Document Updated with Remediation Status — 7 P0s Closed, 3 Remain Architecture-Dependent
1470 11:34a ✅ E3 Remediation Audit Doc Committed and Pushed — Sprint Paper Trail Complete
1471 11:37a ✅ E3 P0 Remediation Status Saved to Claude Project Memory File
1473 " ⚖️ User Overrides Architecture-Risk Deferral — Orders P0-5, P0-7, E3-5/E3-6 to Be Solved and Deployed
S422 User override: "no importa soluciona esos errores y vps" — implement all deferred P0s (P0-5, P0-7, E3-5, E3-6) regardless of architectural risk, deploy to VPS (Jul 8, 11:37 AM)
S419 FaberLoom E3 full-completion sprint — close all partially-done milestones (E3-0 through E3-6) with no gaps, blockers, or partial states (Jul 8, 11:37 AM)
1472 " ✅ Claude Project MEMORY.md Index Updated with E3 P0 Remediation Entry
S420 User override: "no importa soluciona esos errores y vps" — implement P0-5 (key broker on reads), P0-7 (object payload encryption), E3-5 presets builder, E3-6 billing, and deploy all to VPS (Jul 8, 11:48 AM)
1474 11:50a 🟣 P0-5: `resolve_read_level` Added to key_broker.py — Safe Read Mediation Without Bricking Reads
1475 11:51a 🟣 P0-5: Key Broker Imports Wired into draft_engine.py
1476 " 🟣 P0-5 Complete: Key Broker Gate Wired into _build_evidence_pack in draft_engine.py
1477 11:52a ⚖️ P0 Security Items Deferred Due to Architecture Risk on Live Data

Access 792k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>