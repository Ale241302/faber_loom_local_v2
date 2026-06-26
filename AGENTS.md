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

# Correr harness manualmente
python harness/orchestrator.py

# Correr app en desarrollo (después de SL0)
cd app && python -m uvicorn src.main:app --reload
```


<claude-mem-context>
# Memory Context

# [faber_loom_local_vv2] recent context, 2026-06-25 11:14pm GMT-5

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (24,196t read) | 1,376,787t work | 98% savings

### Jun 25, 2026
890 4:15p ⚖️ SpaceLoom SL0 Technical Stack Locked: React 18 UMD + pywebview + FastAPI
897 4:16p 🔵 SL0 SpaceLoom Milestone Evaluation — All Tests Passing
894 4:19p 🔵 SL0 Frontend Shell Already Implemented: React 18 UMD + Full Brand System
895 " 🔵 SL0 Backend Confirmed Running: FastAPI + pywebview + SQLite Seed Workspace
896 " 🔵 SL0 API Contract: Context Layer + Audit Writer Pattern Already Implemented
898 " ⚖️ SpaceLoom Etapa 1 Build Plan Established (PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1 v1.1)
899 " 🟣 SL0 Brand Engineering Task: FaberLoom Design System Applied to Frontend
900 " ⚖️ FaberLoom Brand Canon: Typography, Color, and Iconography Tokens Locked
901 4:22p 🔵 SL0 Frontend Already Brand-Compliant: Zero Bare Hex in JSX, One in HTML
902 " 🔴 Fixed Two Brand Token Violations: Hardcoded Hex in Boot SVG and Missing color Inheritance
903 " 🔵 SL0 Frontend Architecture: React 18 UMD + Babel Standalone, No Build Step
904 " 🔵 SpaceLoom Context Architecture — Tenant-Scoping Seam Pattern
905 " 🔵 SpaceLoom Schema — Two-Migration Contract with routine/routine_run Tables
906 " 🔵 AuditWriter Dual-Write Pattern — SQLite Source of Truth + JSONL Mirror
907 " 🔵 SpaceLoom SL0 Frontend — No-Op Shell with Explicit Future Seams
908 " 🔵 SpaceLoom SL0 Test Suite — 6 Tests Covering All DoD Contract Points
909 4:36p ⚖️ SpaceLoom SL1a: Minimal Router + Chat Architecture Specification
910 " 🔵 SpaceLoom SL0 Codebase State Before SL1a Implementation
911 4:37p 🔵 Venv Exists But SDK Install Status Unknown; Policy Blocks Executable Invocations
915 " ⚖️ SpaceLoom SL1a: Minimal Router + Chat Architecture Defined
912 " 🔵 LLM Provider SDKs Not Installed in Venv; httpx Available for Ollama HTTP
918 4:42p ⚖️ SpaceLoom SL1a Router Architecture Designed
916 " 🔵 venv Missing openai and anthropic SDKs Required for Router
917 " ✅ models.py Schema Version Bumped to 3 for SL1a Router Tables
919 4:45p 🔵 SpaceLoom SL0 Codebase Is Already Built and Running
920 " ⚖️ SpaceLoom Build Plan v1.1 Ratified: SL1a/SL1b Split + Router Minimum Scope
921 11:07p ⚖️ SpaceLoom SL0 Architecture: Local-First Python/FastAPI Backend with Contract-First Schema
922 " ⚖️ SpaceLoom Core Data Model: Six Tables with Latent Multi-Tenant Fields from Day 0
923 " ⚖️ SpaceLoom Security P0 Requirements Baked Into SL0 Architecture
924 11:08p 🔵 SpaceLoom Backend Already Implements SL0–SL5: 26 Modules, SCHEMA_VERSION=8, Full Test Suite
925 " 🔵 SpaceLoom SQLite Migration Chain: 8 Versions Covering Full SL0–SL5 Schema Surface
926 " 🟣 API Security: context_from_request Uses Hardcoded Local Identity in Production, Headers Only in Dev Mode
927 " 🔵 SpaceLoom Project Has No Git Repository Initialized
929 " ⚖️ FaberLoom SpaceLoom Etapa 1 Build Plan Established (v1.1)
930 " ⚖️ FaberLoom Brand and Design System Locked for SL0 Implementation
931 " 🟣 SL0 Frontend Shell Task Scoped: index.html + main.css + app.jsx + main.py
928 11:09p 🔵 SL0 Backend Test Suite: 6/6 Passing on Python 3.13.13 via .venv
932 11:10p 🔵 SpaceLoom Backend Already Implements SL1b–SL3b Features (Beyond SL0 Skeleton)
933 " 🔵 SpaceLoom Frontend Shell Already Implemented with Full SL1b React Components
934 " 🔵 Project Has No Git Repository — Version Control Absent
935 11:11p 🔵 Windows OS Error 206: Command Line Too Long When Writing Files via PowerShell Here-String
936 " 🔵 Files Remain at SL1b State — Two Write Attempts Failed with OS Error 206
937 " 🔴 index.html Written Successfully by Splitting into Separate Shell Command
938 " 🟣 main.css Replaced with Minified SL0 Brand Token Stylesheet
939 " 🟣 main.css Completed via Two-Part Write — Full SL0 Shell Stylesheet Now in Place
940 11:12p 🟣 app.jsx SL0 Shell Written in Multi-Chunk Strategy — First Two Chunks Complete
941 11:13p 🟣 SL0 Frontend Shell Fully Written — app.jsx Complete, main.py Patched, CSS Tokens Enforced
942 " 🔵 SL0 Shell Verified: All 4 Static + API Routes Return HTTP 200 via FastAPI TestClient
943 " ✅ Graphify Code Graph Updated — 1388 Nodes, 4010 Edges, 68 Communities
944 " 🔵 Final Content Verification Confirmed — Node.js v22 Present, No Local Build Tooling

Access 1377k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>