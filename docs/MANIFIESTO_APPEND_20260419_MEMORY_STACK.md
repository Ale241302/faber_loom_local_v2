# MANIFIESTO_APPEND_20260419_MEMORY_STACK
fecha: 2026-04-19
autor: Claude (Cowork)
tipo: ARQUITECTURA
trigger: CEO `indexa` — decisión stack memoria agentes
aplica_a: [SHARED]

---

## Resumen

Creación de `ENT_PLAT_MEMORY_STACK` como entidad canónica que define la separación entre KB canónica (pgvector) y memoria operativa de agentes (Letta self-hosted). Decisión derivada de swarm de verificación 2026-04-18 contra fuentes primarias de Cloudflare, Letta, Mem0, Zep, Tiger Data y Supabase.

## Archivos creados

- `ENT_PLAT_MEMORY_STACK.md` v1.0 DRAFT — entidad nueva en dominio Plataforma. Stack de memoria: pgvector queda para KB canónica, Letta self-hosted para memoria operativa agentes, pgvectorscale como path de escala futuro. Vectorize/Pinecone/Qdrant descartados para KB. Cloudflare Agent Memory en watch-list hasta GA.

## Archivos modificados

| Archivo | Versión anterior | Versión nueva | Cambios |
|---------|-----------------|---------------|---------|
| IDX_PLATAFORMA.md | — | — | +entrada Memory Stack. Health 22/38 → 23/39. Última revisión 2026-04-13 → 2026-04-19. |
| ENT_GOB_PENDIENTES.md | v11.9 | v12.0 | +CEO-34 (decisión piloto Letta) +CEO-35 (watch CF Agent Memory post-GA). |

## Decisiones clave

1. **pgvector queda** para KB canónica. No migrar a Vectorize/Pinecone/Qdrant. Sweet spot 1-5M vectores con filtros compuestos (4 tiers × 10 dominios × 8 tipos).
2. **Letta self-hosted** como capa de memoria operativa. Apache-2.0, pgvector nativo, cero costo licencia, 11K+ stars. Aprovecha Postgres existente.
3. **pgvectorscale** (Tiger Data, mayo 2025) como path de escala drop-in cuando pgvector exceda 10M vectores o HNSW no quepa en RAM. 471 QPS @ 99% recall en 50M vectores.
4. **Cloudflare Agent Memory** en watch-list. Private beta, sin precio público, lock-in fuerte. Reevaluar post-GA.
5. **Zep Community Edition** descartada (deprecada 2025). Mem0 Pro $249/mes innecesario vs Letta gratis.

## Ámbito del gate

Gate `indexa` ejecutado con checklist PLB_INDEXACION:

```
GATE ✅
✔ Determinismo     — entidad nueva, no duplica ni parchea ENT_PLAT_KNOWLEDGE ni ENT_PLAT_AGENTIC
✔ Tipo             — ENT (entity — data pura inyectable)
✔ Stamp            — DRAFT — Pendiente aprobación CEO
✔ Version          — v1.0 (creación)
✔ Impacto cruzado  — IDX_PLATAFORMA (+entrada), ENT_GOB_PENDIENTES (+CEO-34/35)
✔ Pendientes       — CEO-34 (piloto Letta) + CEO-35 (reevaluar CF Agent Memory post-GA)
✔ Sin inventados   — todos los datos de costos/features de vendors verificados contra fuentes primarias listadas en §I
✔ IDX              — IDX_PLATAFORMA actualizado en el mismo batch
✔ Seguridad        — no amplía superficie de ataque. Letta self-host en mismo Postgres interno, no abre puertos externos nuevos.
```

## Refs activos

- ENT_PLAT_KNOWLEDGE (capa KB canónica — complementaria, no se pisa)
- ENT_PLAT_AGENTIC (arquitectura agentes — MEMORY_STACK provee su capa de estado)
- ENT_PLAT_AGENT_ORCHESTRATION (orquestación — consume memoria operativa)
- ENT_PLAT_LLM_ROUTING (routing modelos — ortogonal)
- PLB_ORCHESTRATOR (FROZEN — solo referenciado)

## Lo que el CEO tiene que decidir

- **CEO-34:** ¿autorizar piloto Letta en `mwt-sprint-active`? 4-6h Ale.
- **CEO-35:** nada inmediato. Solo reevaluación cuando CF Agent Memory salga de private beta.

## Stamp

DRAFT — la entidad queda en DRAFT hasta aprobación CEO explícita del plan de piloto. No se indexa a pgvector en producción hasta promoción a VIGENTE (regla ENT_PLAT_KNOWLEDGE B5).
