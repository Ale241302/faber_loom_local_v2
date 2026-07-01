# Plan de Ejecución — Inventario de Agent Skills para MWT y FaberLoom

## Objetivo
Construir un inventario priorizado de agent skills del ecosistema abierto (skills.sh, GitHub, Vercel Labs, etc.) útiles para MWT (e-commerce + B2B calzado) y FaberLoom (SaaS multi-agent LATAM).

## Estructura del prompt
- 12 dimensiones de research paralelo
- Cross-verificación con deduplicación, re-scoring, top 10, top 5 gaps
- Entregable: documento markdown consolidado

## Stages

### Stage 1 — Deep Research (12 dimensiones paralelas)
- **Skill:** `deep-research-swarm` (Route B — Focused Search: cada dimensión tiene un foco claro)
- Crear 12 sub-agentes especializados, uno por dimensión
- Cada agente investiga skills.sh, GitHub topics, Vercel Labs CLI, awesome-agent-skills
- Cada agente entrega su dimensión con formato obligatorio (tablas markdown)
- Restricciones críticas: no inventar skills, URLs verificables, no recomendar skills ya instaladas

### Stage 2 — Cross-Verification y Consolidación
- Agente consolidador que recibe las 12 dimensiones
- Ejecuta: deduplicación, re-scoring, top 10 priorizado, top 5 gaps, conflict zones, recomendación final
- Output: markdown consolidado completo

### Stage 3 — Report Writing y Formato Final
- **Skill:** `report-writing` para estructurar y pulir el documento final
- Output final: `.md` entregable listo para el usuario

## Notas
- Dimensiones 1-12 son independientes entre sí → máximo paralelismo
- Stage 2 depende de Stage 1
- Stage 3 depende de Stage 2
- Idioma: español
