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

## Pendientes humanos

1. Revisar gate comercial en `docs/faberloom/PLB_FB_E4_APERTURA_SIGNUP_v1.md`.
2. Configurar proveedor captcha real antes de abrir signup auto.
3. ~~Implementar E4-6 WhatsApp Cloud API~~ — completado.
