---
id: PLB_SPACELOOM_ETAPA1_KICKOFF_PROMPT
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: PLB
stamp: DRAFT — 2026-06-30 — prompt autocontenido para sesiones SpaceLoom Etapa 1
aplica_a: [FaberLoom, MWT]
---

# PLB_SPACELOOM_ETAPA1_KICKOFF_PROMPT_v1

## Contexto

Estás trabajando en **SpaceLoom Etapa 1**, un spike de validación / dogfood interno de MWT.

**Qué es:** app de escritorio single-user, local-first, “telar completo”:
- SpaceLoom (canvas de iteración / chat)
- Routine Hub (skills/rutinas invocables por `@nombre`)
- Router multi-proveedor con BYO-key
- Workspaces con herencia
- KB grounding (MD/TXT/PDF/Excel)
- HITL absoluto + gold loop

**Qué NO es:**
- No es el track canónico de FaberLoom. Ese es **Foundation Beta v1.3.1** (Postgres + RLS + Next.js + 13 sprints).
- No es multi-tenant ni SaaS.
- No es “SpaceLoom” como producto final; SpaceLoom es una superficie del producto.

**Estado actual:**
- SL0–SL4 cerrados en código (221 tests verdes).
- SL5 (correo) diferido.
- Plan y specs base ya existen en `docs/faberloom/`.
- Documentación por sub-hito (SL0, SL1a, SL1b, etc.) aún pendiente.

## Documentos que DEBÉS leer antes de proponer cambios

1. `docs/faberloom/DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md` — decisión que autoriza construir este track.
2. `docs/faberloom/PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` — secuencia SL0–SL4, costuras, riesgos.
3. `docs/faberloom/SPEC_SPACELOOM_ETAPA1_v1.md` — definición del producto.
4. `docs/faberloom/IDX_SPACELOOM_ETAPA1_v1.md` — índice maestro del track.
5. `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md` — registro formal del spike como no canónico.

## Stack

- Backend: Python 3.13 + FastAPI + Pydantic v2
- DB: SQLite + sqlcipher3 + FTS5 (`tenant_id` latente, sin RLS real)
- Frontend: React 18 UMD + Babel standalone + CSS custom
- Desktop: pywebview + PyInstaller
- Auth: JWT simple con `FABERLOOM_USERS`
- LLM: BYOK (OpenAI / Kimi / Anthropic / Google / Ollama)

## Reglas de oro

1. **HITL absoluto:** cero acción irreversible (envío/borrado) sin aprobación explícita.
2. **Sellado por workspace:** lo de un workspace no se cuela en otro.
3. **Cero dato inventado:** todo precio/dato del draft debe trazar a la KB.
4. **Costuras contract-first:** no claves supuestos single-user que obliguen a reescribir en Foundation Beta.
5. **No contaminar el canon:** no mergear código SQLite/pywebview al track Foundation Beta.
6. **No expansion-built:** dejá costuras limpias para Etapa 2-3, pero no construyas el futuro.

## Riesgos P0

- Envío sin HITL → kill.
- Injection por email → test obligatorio antes de liberar correo.
- Fuga cross-workspace → test en SL3.5.
- Dato inventado → sin fuente, sin aprobación.

## Cómo operar en este chat

1. Leé los documentos listados arriba.
2. Verificá si tu tarea toca Foundation Beta; si es así, detenete y consultá.
3. Si tu tafa es de código, respetá los tests existentes (221 passed) y corré `pytest app/tests` antes de finalizar.
4. Si tu tarea es documentación, usá el formato de frontmatter de los docs existentes.
5. No inventes decisiones de CEO; marcá `[PENDIENTE CEO]` cuando corresponda.
6. Actualizá `docs/faberloom/IDX_SPACELOOM_ETAPA1_v1.md` si creás/renombrás archivos del track.

## Tarea típica

> Implementar / revisar / documentar [sub-hito X] de SpaceLoom Etapa 1 respetando el plan, los riesgos P0 y las costuras contract-first.

Antes de escribir código, explicá qué cambios vas a hacer y por qué. Después, entregá el diff y actualizá el índice si corresponde.
