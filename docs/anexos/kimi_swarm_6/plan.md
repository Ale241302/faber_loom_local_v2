# Plan MWT Swarm #6 — Hybrid Retrieval, KB Quality, Chunking, CLAUDE.md

## Objetivo
Ejecutar investigación en paralelo sobre 4 dimensiones críticas para FaberLoom MVP (60 días, single-agent, stack frozen). Cada dimensión requiere casos production reales 2025-2026, costos concretos, y recomendación directa. No marketing-talk, no teoría sin aterrizaje.

## Stage 1 — Research paralelo (4 sub-agentes)
Cargar skill: `deep-research-swarm` (por agente, inline o by-reference según tamaño).
Cada sub-agente recibe: (1) skill instructions, (2) contexto operativo MWT completo, (3) misión específica de su dimensión.

- **D1** — Hybrid Retrieval con pgvector + BM25 + RRF
- **D2** — KB Quality Monitoring continuo (DeepEval + TruLens)
- **D3** — Chunking strategies "by user query"
- **D4** — CLAUDE.md patterns emergentes 2026

Las 4 tareas son independientes. Se lanzan en paralelo en un solo bloque de `task`.

## Stage 2 — Validación rápida
Revisar que cada dimensión tenga:
- ≥3 casos production reales con métricas
- Recomendación directa (no abstracta)
- Costos cuando aplique

Si falta algo, re-delegar con brief específico.

## Stage 3 — Síntesis ejecutiva
Agente integrador recibe los 4 outputs y produce:
- Tabla de decisiones cross-dimensiones
- Tensiones explícitas
- Roadmap ajustado
- Costos consolidados
- Formato estructurado según prompt original

## Stage 4 — Entrega final
Ensamblar todo en un solo documento markdown estructurado según formato esperado del usuario.

## Notas
- Restricciones comunes (stack frozen, decisiones cerradas) se repiten en cada prompt de sub-agente para autocontención.
- El output final NO es .docx (el usuario pide research bruto + síntesis, no un report formal).
- Idioma: español (igual que el prompt del usuario).
