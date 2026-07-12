# Auditoría de cierre — Ola 4 (E4)

**Fecha:** 2026-07-11  
**Base:** rama `e4-agente-vivo`, SCHEMA_VERSION 48  
**Suite:** 724 passed, 12 skipped

## Semáforo por área

| Área | Estado | Evidencia |
|------|--------|-----------|
| Presencia única (E4-4) | 🟢 | `living_agent/presence.py`, `api.py`, `app.jsx` |
| Memoria viva CAPA 1 (E4-5) | 🟢 | `living_agent/memory.py`, tests E4-5 |
| Signup público gated (E4-7) | 🟢 | `auth.py`, `tenant_bootstrap.py`, `test_e4_7_signup_auto.py` |
| Contamination E4 | 🟢 | `test_e4_8_living_agent_hardening.py` |
| Injection briefs / KB | 🟢 | `security/injection.py`, `test_e4_8_living_agent_hardening.py` |
| Health dashboard agente | 🟢 | `health_dashboard.py`, `health_dashboard.jsx` |
| Métricas ACE shadow | 🟢 | `living_agent/planner.py`, `routing_shadow.jsx` |
| Documentación cierre | 🟡 | Este doc; arquitectura en progreso |
| WhatsApp bidireccional (E4-6) | 🟢 | `connectors/whatsapp_outbound.py`, `api.py`, `test_e4_6_whatsapp_outbound.py` |

## Conteo de tests

- Base post-E4-7/E4-8: **713 passed**, 12 skipped.
- Nuevos tests E4-7: 6 (signup auto, defensas, onboarding).
- Nuevos tests E4-8: 6 (contamination, injection, health, ACE).
- Nuevos tests E4-6: 5 (HITL token, fail-closed, 24h window, template token, isolation).

## Deploy

- Rama `e4-agente-vivo` pushed a GitHub.
- VPS actualizada en `/opt/faber_loom` (imagen `faber_loom-api:latest`, puerto host `8200`).
- Health check: `GET http://187.77.218.102:8200/api/health` → 200 OK, schema_version 48.
- Fix frontend JSX: top-level `const`/`let` convertidos a `var` para evitar colisiones de redeclaración en el scope global tras transpilación de Babel standalone; cache bust `?v=20260712`.
- Fix frontend null workspace: `LearningThermometer` ya no dispara `/api/workspaces/null/memory/learning-state` antes de cargar el workspace activo.
- Fix backend shadow-report: cost query usa parsing en Python en lugar de `json_extract()` para ser compatible con PostgreSQL.
- Fix menú lateral: se eliminó el ítem duplicado "Fábrica de skills" (ya existe "Skills").

## Fixes de deploy

- `seed.py`: ws-general usa slug scoped por tenant para evitar colisión de unique global.
- `foundation/core.py`: backfill de columnas `user_id` en `fnd_email_verifications` y `fnd_memory_blocks` antes de aplicar `CORE_SCHEMA`/`_MODULE_SCHEMAS` en SQLite.

## Pendientes humanos

1. Revisar gate comercial en `docs/faberloom/PLB_FB_E4_APERTURA_SIGNUP_v1.md`.
2. Configurar proveedor captcha real antes de abrir signup auto.
