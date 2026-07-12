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

# [faber_loom_local_vv2] recent context, 2026-07-11 11:27am GMT-5

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (26,061t read) | 1,208,248t work | 98% savings

### Jul 5, 2026
S366 Cleanup of dead localStorage token code in app.jsx and related files after P0 HttpOnly cookie migration (Jul 5, 11:44 PM)
S367 FaberLoom auth cleanup — complete HttpOnly-cookie migration in web UI (app.jsx, fnd_core.jsx, foundation/core.py) (Jul 5, 11:45 PM)
S415 Audit of 5 claimed P0 blockers in FaberLoom codebase — verification against actual code (Jul 5, 11:47 PM)
### Jul 8, 2026
S417 Resume session after context compaction — verify VPS deploy of P0 fixes #1, #3, #4 and confirm production health (Jul 8, 9:31 AM)
S416 Fix P0 blockers #1, #3, #4 → push to GitHub → deploy to VPS (continued session after context compaction) (Jul 8, 10:16 AM)
S418 Fix P0 blockers #1, #3, #4 → push to GitHub → deploy to VPS → verify in production (COMPLETE) (Jul 8, 10:16 AM)
S421 User override to fix all deferred P0s and deploy to VPS — primary session now investigating key_broker.py and draft_engine._build_evidence_pack to implement P0-5 (Jul 8, 10:25 AM)
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
### Jul 10, 2026
1626 10:37a ⚖️ Faber Loom E3 Partial Milestones — 9-Block Closure Plan Commissioned
1627 10:38a 🔵 E3 Audit Report Reveals Actual Code State vs. Plan — 10 P0 Blockers, Suite at 546 Passed
1628 10:39a 🔵 app/src Module Map — All E3 Core Modules Confirmed Present at HEAD 457a3f8
1629 " 🔵 Two-Audit Reconciliation: 546→552 Passed — Preliminary vs. Detailed Closure Report Are Different Snapshots
1630 " ⚖️ E3 Plan Architectural Decisions — 12 Binding Choices That Constrain New Code
1631 10:53a ⚖️ Fugu E3 Implementation Plan Approved — Six Open Decisions Resolved
1632 10:54a 🔵 Fugu Project Root Structure and Shell Policy Constraint Identified
1633 " ⚖️ Fugu E3 Implementation Plan Approved — 9-Block Execution Order with Strict Constraints
1634 " ⚖️ D1: PDF Generation Uses fpdf2 (Pure Python), Marked as Non-Fiscal Beta
1635 " ⚖️ D2: BYO API Key Precedence — Tenant Key Wins, Default Tenant Never Surcharges
1636 " ⚖️ D3: Connector Config Uses tenant_settings (Namespaced Keys) + TenantSecretStore for Secrets
1637 " ⚖️ D4: 13 Legacy Skills (Not 14) Classified via Three-Category Rule into ENT_FB_SKILL_CATALOG_v1.1.md
1638 " ⚖️ D5: External Data (ATV/SAT/DIAN URLs, WhatsApp Secrets, Marluvas/Tecmater) Remains [PENDIENTE — NO INVENTAR]
1639 " ⚖️ D6: Fetcher Injected as Explicit Dependency in execute_skill, Following Fail-Closed Pattern
1640 " ⚖️ WhatsApp Webhook Router: Public Endpoint with HMAC Signature Auth, Feature-Flagged
1641 " ⚖️ Database Migrations: v38→v43 Additive Only; v37 and Earlier Are Frozen
1642 10:56a 🔵 Agent Execution Environment Has Blocked Shell and Write Access at Session Start
### Jul 11, 2026
1661 9:24a 🔵 FaberLoom Etapa 4 Plan v2 — "El Agente Vivo" Architecture
1663 9:25a 🔵 FaberLoom E4 Ola 1 Readiness: All Target Artifacts Missing, Codebase Base Confirmed
1664 " 🔵 E4-0 Refactor Target: auto_dispatcher Internal Structure and E3 Infrastructure APIs Verified
1667 9:26a 🔵 E4 Ola 1 Readiness Gaps: Zero E4 Tests, SPEC_E2_5 at v1.0, Ambient Allowlist Not Hardcoded in Code
1668 " 🔵 Git State: On e3-cierre-parciales Branch with 2 Commits Beyond Plan Baseline; E4 Branch Not Yet Created
1669 9:27a 🔵 Frontend State: "Agentes" Rail Item Confirmed at app.jsx:366; Brief/Freshness Footer Absent
1670 9:28a 🟣 Fugu Readiness Report Written: app/.tmp/fugu_o1_readiness.md
1671 " 🔵 Graphify Knowledge Graph Current as of HEAD f5ba733; 28K Nodes Ready for Architecture Decisions
1682 10:13a 🔵 FaberLoom E4-0 Audit Initiated on Branch e4-agente-vivo
1683 10:14a 🔵 E4-0 Test Suite Inventory on Branch e4-agente-vivo
1684 " 🔵 FaberLoom E2 Plan Architecture: Routing Modes and Wave Sequencing
1685 10:15a 🔵 E4-0 Routing Mode Architecture: policy.py, config_cascade.py, and dispatcher_base.py
1686 " 🔵 api.py _SETTING_REGISTRY Includes routing.mode with Validation
1687 " 🔵 E4-0 Test Coverage: Mode Flag, Dispatcher Interface, Presigned Cross-Tenant, Backup Smoke
1691 11:05a 🔵 E4-1 Workspace Briefs — Audit Scope and Architectural Constraints Established
1692 11:06a 🔵 E4-1 Audit Environment: Git Blocked by Policy, All Key Files Confirmed Present
1694 " 🔵 E4-1 briefs.py — Implementation Internals, Two Bugs Identified
1695 " 🔵 key_broker.py — resolve_read_level Semantics Confirmed
1696 11:07a 🔵 Ambient Cycle Brief Integration — Non-Blocking, Pre-Detector, with Implicit INDEX-Level Downgrade
1699 11:08a 🔵 models.py Migration v42 — Schema R13 Fields Confirmed, RLS Applied, Two Indexes Present
1700 " 🔵 E4-1 Test Suite — 8 Tests Cover Core Criteria, 4 Gaps Identified
1703 11:09a 🔵 RLS Policy Uses Strict tenant+workspace Dual Check, WorkspaceBriefPanel is Pure Read-Only
1704 " 🔵 Plan vs Implementation Discrepancy: 404 Instead of 200/pending on Missing Brief
1706 " ⚖️ E4-1 Audit Verdict: BLOCK — Key Broker Does Not Mediate Reads, Invoice Data Exposed by Default

Access 1208k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>