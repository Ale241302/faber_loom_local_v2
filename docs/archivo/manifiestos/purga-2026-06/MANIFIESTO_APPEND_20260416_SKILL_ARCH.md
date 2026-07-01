# MANIFIESTO_APPEND_20260416_SKILL_ARCH
fecha: 2026-04-16
autor: Claude (Cowork)
tipo: ARQUITECTURA
aplica_a: [MWT]

---

## Resumen

Implementación de arquitectura AgentSpec/Runtime/Memory para el sistema de Skills de MWT.
Basada en el modelo de agentes Faberloom adaptado a escala markdown + n8n.

## Archivos creados

- `SCH_SKILL.md` — Schema canónico para todos los skills. Define estructura obligatoria, ciclo de vida, flujo de aprendizaje con termómetro y modal de consolidación, y checklist de validación pre-ACTIVE.
- `SKILL_RUNTIME.md` — Dashboard único AgentRuntime. Tracking de estado, autonomía, métricas y temperatura de aprendizaje para los 9 skills.

## Archivos modificados

Todos los SKILL_*.md actualizados a arquitectura AgentSpec:

| Archivo | Versión anterior | Versión nueva | Cambios |
|---------|-----------------|---------------|---------|
| SKILL_AMAZON_OPS | 1.0 DRAFT | 1.1 SHADOW | trigger_word, autonomy_ceiling, escalation_policy, State Machine, Events, Learning Consolidation |
| SKILL_CLIENT_SERVICE | 1.0 DRAFT | 1.1 SHADOW | ídem |
| SKILL_COMPLIANCE_CHECKER | 1.0 DRAFT | 1.1 SHADOW | ídem |
| SKILL_DEMAND_FORECASTER | 2.0 DRAFT | 2.1 SHADOW | ídem |
| SKILL_EXPERIMENT_RUNNER | 1.0 DRAFT | 1.1 SHADOW | ídem |
| SKILL_HUMANIZE_BRAND | 0.2.0 DRAFT | 0.3.0 SHADOW | ídem + corrección de header (visibility, domain, type, stamp) |
| SKILL_HUMANIZE_COMMS | 0.1.0 DRAFT | 0.2.0 SHADOW | ídem |
| SKILL_KB_AUDITOR | 1.0 DRAFT | 1.1 SHADOW | ídem + autonomy_ceiling AUTO_NOTIFICA |
| SKILL_PROFORMA_BUILDER | 1.0 DRAFT | 1.1 SHADOW | ídem + ceiling PROPONE permanente por CEO-ONLY |

## Cambios arquitectónicos introducidos

**Campos nuevos en header de todos los skills:**
- `trigger_word` — palabra clave de activación
- `autonomy_ceiling` — nivel máximo de autonomía posible
- `escalation_policy` — qué hace el skill fuera de scope

**Secciones nuevas en todos los skills:**
- `## State Machine` — estados operativos + transiciones explícitas por skill
- `## Events` — eventos estructurados que emite cada skill (base del learning loop)
- `## Learning Consolidation` — gold samples, patrones, excepciones, trigger de indexación

**Status:** Todos los skills pasan de DRAFT a SHADOW (Nivel 0 — observa, no ejecuta autónomamente aún)

## Flujo de aprendizaje implementado

```
trigger_word → AgentSpec + AgentMemory cargados → ejecución → eventos emitidos
→ termómetro sube → CEO presiona "Indexar Aprendizaje" (indexa-{trigger_word})
→ modal de confirmación → consolida en SKILL_MEM_{ID}.md
```

Temperatura del termómetro: 🔵 Frío (0-2) · 🟡 Tibio (3-5) · 🔴 Caliente (6+)

## Próximos pasos

1. Primer ciclo SHADOW de cada skill con registro en SKILL_RUNTIME.md
2. Crear SKILL_MEM_{ID}.md cuando haya ≥ 5 ejecuciones reales
3. Promover a ACTIVE cuando approval rate ≥ 70% en ≥ 3 ejecuciones SHADOW
