---
id: SPEC_SPACELOOM_SL1a
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE — 2026-06-30 — cierre formal de SL1a (router mínimo + chat)
aplica_a: [FaberLoom, MWT]
relacionado:
  - PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md
  - SPEC_SPACELOOM_ETAPA1_v1.md
  - SPEC_FB_ROUTING_PRESETS_v1.md
  - IDX_SPACELOOM_ETAPA1_v1.md
---

# SPEC_SPACELOOM_SL1a_v1 — Router mínimo + chat

## Objetivo

Hacer visible y usable el router multi-proveedor en el chat de SpaceLoom, con fallback, budget cap y provider allowlist; más gestión básica de conversaciones.

## Definition of Done

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Router mínimo visible | ✅ | Providers visibles en UI: OpenAI + Kimi. Backend sigue soportando todos. |
| 2 | Fallback funcional | ✅ | Si OpenAI no tiene key y Kimi sí, el router presenta solo Kimi. |
| 3 | Budget cap / allowlist | ✅ | Router elige por prioridad + allowlist + budget cap + fallback. |
| 4 | Gestión de conversaciones | ✅ | Renombrar chat (doble clic / botón editar) y borrar con `confirmation_token` (HITL). |
| 5 | UI de providers sin overflow | ✅ | Cards adaptables, key guardada con `word-break: break-all`. |
| 6 | Tests | ✅ | Suite SL1a 34 passed; suite total 202 passed. |

## Resultados de test

```text
pytest app/tests/test_sl1a_router.py app/tests/test_sl1a_router_endpoints.py -q
34 passed, 1 warning

pytest app/tests -q
202 passed, 1 warning
```

Tests clave:
- `test_provider_surface_visible_is_openai_and_kimi`
- `test_ollama_remains_configurable_when_hidden`
- `test_fallback_uses_kimi_when_openai_has_no_key`
- `test_rename_conversation`
- `test_delete_conversation_requires_confirmation`
- `test_delete_conversation_tenant_isolation`

## Archivos clave

- `app/src/api.py` (`_VISIBLE_PROVIDER_SLUGS`, endpoints chat)
- `app/src/db.py` (`update_chat`, `delete_chat`)
- `app/src/models.py` (`ChatUpdate`)
- `app/src/router/engine.py` (mensaje de fallback)
- `app/static/js/app.jsx`
- `app/static/js/icons.jsx` (icono `edit`)
- `app/static/css/main.css`

## Riesgos P0

- Envío/borrado sin HITL: mitigado — `DELETE /chats/{id}` requiere `confirmation_token`.
- Fuga cross-workspace: mitigado — queries filtran por `tenant_id`.

## Próximo hito

SL1b — Primer draft real contra mini-KB + HITL mínimo.

## Changelog

- v1.0 (2026-06-30): Cierre formal de SL1a a partir de `harness/reports/SL1a_v2_CLOSER_REPORT_v1.md`.
