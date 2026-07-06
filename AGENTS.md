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

# [faber_loom_local_vv2] recent context, 2026-07-06 11:44am GMT-5

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (23,973t read) | 1,738,647t work | 99% savings

### Jul 3, 2026
1164 10:11a 🔵 Graph God Nodes and Import Cycles: Context(257 edges) is Core Abstraction, Six Circular Dependencies Detected
1165 " 🔵 app/src/ Module Inventory: Full Implementation Present for SL0→SL5 Milestones
1169 11:08a ⚖️ M21 Investigador Web Skill + Tool-Calling Gate — Architecture Brief
1170 11:09a 🔵 skills.py execute_skill() Has No Real Tool Execution — Only LLM Completion
1171 " 🔵 api.py Confirmation Token Gate and Context Architecture Confirmed
1172 11:10a 🔵 _execute_skill_run() Is the M21 Extension Point — Full Synchronous Flow Mapped
1173 " 🔵 SQLite Schema Baseline for M21 — Migration v2 routine/routine_run Tables Confirmed
### Jul 5, 2026
1231 2:29p 🔵 FaberLoom Project Structure Mapped for Security and Gap Audit
1232 2:30p 🔵 FaberLoom Complete Backend Endpoint Map Extracted via AST
1233 " 🚨 Critical Auth Security Gaps: Foundation Router Unprotected, Hardcoded JWT Secret, Auth Bypass Conditions
1234 " 🔵 Frontend Foundation API Client Uses Separate Auth from Main App
1246 11:17p 🔵 FaberLoom Etapa 1 Verified Complete: 278/279 Tests Passing
1247 " ⚖️ FaberLoom Architecture: Single Container — FastAPI + Static React UMD + SQLite
1248 " 🔵 Local Working Copy Corrupted by OneDrive Sync
1249 " 🔵 VPS Infra Project is Legacy Foundation Beta Stack — Safe to Remove After Backup
1250 " 🔵 VPS Docker Project Inventory at 187.77.218.102
1251 " 🔵 Git Working Tree Clean, No index.lock on OneDrive Repo
1252 11:18p 🔵 Previously Corrupted Python Files Are Now Intact and Compilable
1253 " 🔵 VPS SSH Access Confirmed, Docker 29.4.1 Running
1254 " 🔵 JSX Files Intact, Git Working Tree Clean, Dangling Blobs Present but Harmless
1256 " 🔵 VPS Directory Structure and Infra Project Location Confirmed
1257 " 🔵 faberloom-api Runs on mwt_default Network with No Infra Dependencies Confirmed
1258 " 🔵 faber_loom_pgdata Volume Exists Despite SQLite-Only Architecture
1255 11:19p 🔵 Full VPS Container Audit: Key Anomalies Found
1259 " 🔵 96.5GB of Reclaimable Docker Build Cache Found on VPS
1260 11:20p ✅ fb_litellm Container Removed — infra Compose Project Fully Decommissioned
S361 FaberLoom P0 regression fix: Foundation shell broken post-bootstrap (SSO bridge too narrow after hardening) — investigated, fixed, tested, committed, pushed, and deployed to VPS (Jul 5, 11:20 PM)
S360 FaberLoom Etapa 1 verification + VPS Docker cleanup: fix OneDrive corruption, confirm faberloom-api architecture, and clean up legacy infra project (Jul 5, 11:20 PM)
1261 11:23p 🟣 HEAD Commit: P0 Security Hardening — HttpOnly Cookies, Signed Updates, Tenant Isolation
1262 11:24p 🟣 Foundation Bootstrap JWT Bridge: Temporary Auth Bypass Closes After Tenant Setup
1263 11:27p 🟣 M08 Foundation Auth Session: SQLite-Backed Login, TOTP, Session Revocation
1264 " 🔵 Foundation Uses Separate foundation.sqlite3 Database Alongside Main faberloom.sqlite3
1265 " 🔵 Foundation Session Token Resolution and Main App Auth Cookie Architecture
1267 " ✅ 569MB of Dangling Docker Volumes Reclaimed Including faber_loom_pgdata and db_data
1268 " 🔵 fnd_core.jsx Still Reads JWT from localStorage Despite P0 Cookie Migration
1266 11:28p 🟣 M07 Bootstrap Wizard: 4-Step Tenant Initialization Flow (Simplified from 8-Step Django)
1269 11:30p 🔵 Main FaberLoom Auth Configuration: FABERLOOM_USERS JSON, 15min Access Tokens, Fail-Closed SECRET_KEY
1270 11:31p 🔴 P0 Hardening Regression: Foundation Shell Broken Post-Bootstrap — JWT Bridge Too Narrow
1271 11:32p 🔵 Test Environment Uses uv, Not System Python — pytest Not in Python 3.14 System Path
1272 " 🔵 Project Virtual Environment Located at app/.venv with pytest 9.1.1 on Python 3.13
1273 " 🔵 SSO Regression Confirmed: test_sso_bridge Fails with "Foundation session required" After Bootstrap
1274 " 🔴 P0 Regression Fixed: _sso_jwt_context() Added to Foundation core.py for Post-Bootstrap SSO
S362 FaberLoom P0 regression fix: Foundation shell broken post-bootstrap — full cycle complete: fix implemented, 285 tests green, committed 94ad893, pushed to GitHub, deployed to VPS, end-to-end verified in production (Jul 5, 11:33 PM)
S363 FaberLoom P0 SSO regression fix — fully deployed and verified; session now exploring Foundation roles and main-app user state on VPS (Jul 5, 11:38 PM)
S364 FaberLoom P0 SSO regression fix — complete and verified in production; post-fix diagnostics on VPS Foundation roles and main-app user state (Jul 5, 11:39 PM)
S365 FaberLoom: P0 SSO fix deployed + alvaro@muitowork.com added as Foundation owner — all users operational in production (Jul 5, 11:39 PM)
S366 Cleanup of dead localStorage token code in app.jsx and related files after P0 HttpOnly cookie migration (Jul 5, 11:44 PM)
S367 FaberLoom auth cleanup — complete HttpOnly-cookie migration in web UI (app.jsx, fnd_core.jsx, foundation/core.py) (Jul 5, 11:47 PM)
### Jul 6, 2026
1304 11:17a ⚖️ FaberLoom/SpaceLoom Stage 2 Architecture Audit Initiated
1305 " 🔵 FaberLoom Stage 2 Plan v1.6 Full Content Loaded for Audit
1306 " 🔵 Stage 1 Plan v1.1 Amendments Establish Contract-First Seam Requirements
1307 " 🔵 Knowledge Graph Reveals Context Node as Critical System Hub with 126 Inferred Edges
1308 11:18a 🔵 FaberLoom Backend File Structure and Module Sizes Confirmed
1309 " 🔵 Two Parallel Auth Systems Exist — Critical Gap for E2-0 Integration
1310 " 🔵 Context Layer Implemented but Tenant Isolation Has Critical Gap in context_from_request
1311 " 🔵 AuditWriter Implemented Correctly as Dual-Write Pattern (DB + JSONL)
1312 " 🔵 Router Engine Has No Multi-Provider Dispatcher Mode — E2-4 Requires New Architecture
1313 " 🔵 Gold Loop Has Hard-Field Second Gate Implemented; Gold Candidate Data Structure Confirmed

Access 1739k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>