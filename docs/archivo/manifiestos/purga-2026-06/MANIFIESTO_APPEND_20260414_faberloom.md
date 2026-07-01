---
id: MANIFIESTO_APPEND_20260414_vlinte
date: 2026-04-14
session: Vlinte Agent Builder — indexación inicial
aplica_a: [FaberLoom]
---

## Cambios aplicados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| vlinte_agent_builder_spec.md | EDIT — frontmatter KB añadido | id: ENT_VLINTE_AGENT_BUILDER, v1.0, DRAFT, INTERNAL |
| IDX_PRODUCTO.md | EDIT — sección Vlinte añadida | Registra vlinte_agent_builder_spec.md + vlinte_mapa_tiers.html |
| RW_ROOT.md | EDIT — REGISTROS ESPECIALES + version bump | 4.7.2 → 4.7.3. Añadidas 2 entradas Vlinte |
| ENT_GOB_PENDIENTES.md | EDIT — nuevo track Vlinte | v11.7 → v11.8. Pendientes MVP + infra + perfiles empleado virtual |

## Contexto de decisiones (esta sesión)

- 168 agentes virtuales catalogados por Kimi Swarm distribuidos en 9 áreas
- Arquitectura: pgvector 4 capas + Multi-LLM Router T1→T4
- MVP: TrackBot → InfoBot → DailyBriefBot
- Top ROI: CollectionBot (400-600%) → InfoBot → QualifyBot → CompraBot → TrackBot
- Infra recomendada MVP: RunPod L4 $204/mes (Qwen 2.5 14B Q4) + Groq para overflow
- Metáfora de producto: "agencia de staffing virtual" — cliente contrata empleados que aprenden su empresa
- Moat real: KB acumulada (patrones, formatos, voz) — switching cost = pérdida de conocimiento institucional

*Consolidar con MANIFIESTO_CAMBIOS_v2.md en post-sesión.*
