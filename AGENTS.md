# Agent Instructions — FaberLoom SpaceLoom

Este proyecto se desarrolla con un **Agent Harness** autónomo que orquesta agentes
especializados a través de Codex CLI (`codex exec -p fugu`) y mantiene un knowledge
graph con [graphify](https://github.com/safishamsi/graphify).

## Cómo trabajar aquí

1. **No modifiques código a mano sin consultar el harness.** Si llegaste a este repo
   como agente invitado por Kimi, espera a recibir un prompt estructurado del
   orquestador.

2. **Lee el plan vigente** antes de cualquier tarea:
   - `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md`

3. **Respeta el sistema de marca** en `@Diseños`:
   - Paleta fija: `#F4F1ED`, `#1F1E1C`, `#C96442`, `#5A6B7C`, `#FFFFFF`, etc.
   - Tipografía: EB Garamond Italic (voz), Geist (UI), Geist Mono (datos).
   - Iconos: 24×24, stroke 1.75, `currentColor`.
   - Isotipo: nudo 3×3 tejido.

4. **Costuras contract-first** (no negociables):
   - Campos latentes en tablas: `tenant_id`, `actor_id`, `actor_role_at_decision`,
     `routine_version`, `skill_version`, `schema_version`, `source_version`, `approved_by`.
   - Capa `Context(workspace_id, tenant_id=None, user_id=None)` en toda query.
   - `AuditWriter` hoy `audit.jsonl`, mañana outbox/tabla.
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

# [faber_loom_local_vv2] recent context, 2026-07-03 11:08am GMT-5

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (25,383t read) | 2,364,707t work | 99% savings

### Jun 25, 2026
946 11:15p 🔵 SpaceLoom Codebase Structure Mapped: Implementation Already Spans SL0–SL5
### Jun 26, 2026
963 3:37p ⚖️ Plan técnico revisado: CRUD de skills/routines + importador faberloom/ en SpaceLoom
964 3:38p 🔵 Estructura confirmada del proyecto SpaceLoom en faber_loom_local_vv2
965 " 🔵 API de routines en api.py: endpoints existentes y gaps confirmados
966 " 🔵 db.py: funciones de routine existentes y ausencia de update_routine
967 " 🔵 models.py: RoutineCreate definido, RoutineUpdate ausente, esquema DB confirmado
968 " 🔵 skills.py: parser de SKILL.md reutilizable para faberloom_catalog.py
969 " 🔵 build.py: pipeline PyInstaller existente sin soporte para assets faberloom/
970 3:40p 🔵 faberloom/ naming conventions revelan tipos de documentos más allá de skills/agents/templates
971 " 🔵 app.jsx RoutinesView: helpers API existentes, funcionalidad CRUD ausente
972 " 🔵 api_create_routine llama compile_skill_md antes de guardar — riesgo de bloqueo para imports faberloom
973 4:34p ⚖️ Plan Técnico: Rediseño Completo de SpaceLoom hacia FaberLoom Shell
974 " 🔵 Mapa Completo de Endpoints REST de SpaceLoom (app/src/api.py)
975 " 🔵 Estado Real del Modelo de Datos y CSS: Gaps Confirmados para el Rediseño
976 4:35p 🔵 Patrón de Confirmación Explícita en API (confirmation_token) Impacta Diseño HITL
977 6:32p 🟣 SpaceLoom SL0 UI Phase 2 — Rail, RightRail, BudgetChip, ThemeSwitcher Popover
978 6:33p 🔵 SpaceLoom API Backend — All Rail Badge Endpoints Confirmed Implemented
979 6:34p 🔵 SpaceLoom Router Budget Enforcement and WorkLoom Model — Data Contract Details
980 " 🔵 CommandPalette Nav Commands Out of Sync with New Rail Navigation
981 " 🔵 SpaceLoom CSS Layout Architecture — Rail, Frame, Accordion, Responsive Breakpoints
982 6:35p 🔵 SpaceLoom Frontend Architecture — Babel Standalone CDN, No Build Step, Runtime JSX Compilation
983 6:36p 🔵 SpaceLoom Phase 2 Shell Redesign — Technical Audit Initiated
984 6:37p 🟣 SpaceLoom Phase 2 Shell Redesign — Full app.jsx Implementation Confirmed
985 " 🔵 SpaceLoom Graphify Knowledge Graph — Corpus Stats and Import Cycles
986 6:38p 🔵 foundation.jsx — Phase 2 Primitives Confirmed Complete
987 " 🔵 main.css — Phase 2 Styles Explicitly Marked and Fully Implemented
988 " 🔵 Phase 2 Audit Findings — Bugs, Stubs, and Phase Closure Gaps
989 8:08p ⚖️ SpaceLoom Phase 3 Toolset Plan Submitted for Security Audit
990 " 🔵 SpaceLoom Routine Category Previously Derived from source_version Proxy Field
991 " ⚖️ Dual Invocation Architecture: /invoke Endpoint Added Alongside @mention Path
992 " 🔵 SpaceLoom Backend Current State: Phase 3 Gap Analysis from Source Code
993 " 🔵 HITL Gate Enforced in _execute_skill_run but Missing from @mention Approval Check
994 " 🔵 SpaceLoom Knowledge Graph: Context is God Node with 207 Edges, 6 Import Cycles Detected
995 " 🔵 SpaceLoom Build Plan v1.1: Two-Calendar Estimate and Security DoD Hardening via Fugu+Kimi Review
996 8:11p 🔵 Frontend SkillsView/AgentsView Confirmed as Stubs; RoutinesView Has Full CRUD Reusable for Phase 3
997 " 🔵 faberloom_catalog.py Does Not Pass category to create_routine — Uses source_version Instead
998 " 🔵 SKILL.md Injection Detection Has Gaps: No URL, SSRF, or Prompt Injection Canary Checks
999 " 🔵 routine_run HMAC Seal Would Break if Category Added to HMAC Input Fields
### Jul 3, 2026
1157 10:07a ⚖️ Tech Lead Agent Persona and 5-Phase Dev Loop Configured
1158 10:09a 🔵 FaberLoom/SpaceLoom Project Root Structure Confirmed
1159 " 🔵 PowerShell Policy Blocks Conditional Syntax in This Environment
1160 10:10a 🔵 AGENTS.md Contract-First Architecture Constraints for FaberLoom SpaceLoom
1161 " 🔵 SpaceLoom Etapa 1 Development Plan: SL0→SL4 Milestones and Architecture Decisions
1162 " 🔵 Plan/ Directory: Full Planning History with Version Evolution Traced
1163 " 🔵 Graphify Knowledge Graph: 19,442 Nodes, 26,808 Edges, 1,637 Communities — Key Structural Insights
1164 10:11a 🔵 Graph God Nodes and Import Cycles: Context(257 edges) is Core Abstraction, Six Circular Dependencies Detected
1165 " 🔵 app/src/ Module Inventory: Full Implementation Present for SL0→SL5 Milestones
1166 " 🔵 Test Suite is Milestone-Aligned: 25 Test Files Covering SL0→SL5 Plus P0 Security
1167 " 🔵 Database Schema at v20 with All Contract-First Latent Fields Implemented
1168 " 🔵 Extensive docs/ Knowledge Base: 80+ Spec, Policy, Schema, and Design Documents

Access 2365k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>