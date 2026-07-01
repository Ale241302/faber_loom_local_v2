---
id: DEC_FB_SPACELOOM_FREEZE_SCOPE_v1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: faberloom
type: dec
stamp: DRAFT 2026-06-17 - recomendacion de gobernanza, PENDIENTE ratificacion CEO
fecha: 2026-06-17
agente: Claude (Cowork) - Arquitecto Ejecutor
relacionado_con:
  - SPEC_SPACELOOM_SELFHOSTED_v1.1/v1.2/v1.3, SPEC_SPACELOOM_IMAP_CONNECTOR_v1
  - ARCH_FB_AGENT_RUNTIME_EVAL_v1
  - eval PAUSAR-Y-VALIDAR 2026-06-09
---

# DEC_FB_SPACELOOM_FREEZE_SCOPE_v1
## SpaceLoom self-embedded vs el SPEC freeze de FaberLoom

## Pregunta
El build de SpaceLoom self-embedded, esta DENTRO o FUERA del freeze de FaberLoom (PAUSAR-Y-VALIDAR, 2026-06-09: SaaS multi-tenant en pausa, SPEC freeze hasta cierre E2, portfolio b>a>c)?

## Recomendacion (a ratificar por CEO)

**Compatible con la pausa, con una linea dura entre PLANEAR y CONSTRUIR:**

1. **Lo que la pausa congelo** = el SaaS multi-tenant de FaberLoom (infra, adopcion, SPEC_FB de plataforma). Eso sigue congelado.
2. **SpaceLoom self-embedded NO es eso:** single-user, sin multi-tenant, herramienta personal distribuible. Cae en el "slice interno" que la pausa explicitamente deja seguir, no en el SaaS pausado.
3. **Por eso TODO lo producido entro como DRAFT**, no VIGENTE: son artefactos de PLANEACION (specs, decisiones, research). Planear durante el freeze es legitimo; el freeze prohibe adoptar infra y construir, no pensar.
4. **La linea dura:** escribir codigo de SL0 cruza de planear a CONSTRUIR. Eso SI requiere carve-out explicito del CEO, porque la pausa congelo el construir. Hasta esa ratificacion, SpaceLoom se queda en DRAFT/planeacion.
5. **No se toca** ningun SPEC_FB de plataforma multi-tenant ni FROZEN ni control_surface. El ARCH de runtime quedo con sus decisiones marcadas "propuestas pendientes".

## Decision que se pide al CEO (marcar una)
- [ ] A) Carve-out: autorizar CONSTRUIR SL0 de SpaceLoom self-embedded ya (sale de la pausa como track propio interno).
- [ ] B) Mantener en DRAFT/planeacion hasta el cierre de E2 / test de caso real; no codear aun.
- [ ] C) Otra (especificar).

Recomendacion del ejecutor: **A condicionada** -- autorizar SL0-SL3.5 (core single-user, dogfood propio) como track interno, manteniendo congelado todo lo multi-tenant. Es la opcion que honra la pausa (no construis el SaaS) y a la vez te da la herramienta que justifica el esfuerzo.

## Changelog
- v1.0 (2026-06-17): recomendacion de gobernanza sobre el alcance del freeze frente a SpaceLoom self-embedded. DRAFT, pendiente de ratificacion CEO. No toca FROZEN.
