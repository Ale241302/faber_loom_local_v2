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

# [faber_loom_local_vv2] recent context, 2026-06-26 8:07pm GMT-5

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision 🚨security_alert 🔐security_note
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (25,668t read) | 1,576,289t work | 98% savings

### Jun 25, 2026
924 11:08p 🔵 SpaceLoom Backend Already Implements SL0–SL5: 26 Modules, SCHEMA_VERSION=8, Full Test Suite
925 " 🔵 SpaceLoom SQLite Migration Chain: 8 Versions Covering Full SL0–SL5 Schema Surface
926 " 🟣 API Security: context_from_request Uses Hardcoded Local Identity in Production, Headers Only in Dev Mode
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
945 11:15p ⚖️ SpaceLoom Etapa 1 Build Plan Established (v1.1 with dual-engine review amendments)
946 " 🔵 SpaceLoom Codebase Structure Mapped: Implementation Already Spans SL0–SL5
947 " 🔵 Graph Report Confirms Contract-First Seams Are Implemented: Context at 191 Edges, AuditEvent at 55
948 " 🟣 SL0 Frontend Shell Implemented: React 18 + FaberLoom Brand System + Contract-First UI Markers
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

Access 1576k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>