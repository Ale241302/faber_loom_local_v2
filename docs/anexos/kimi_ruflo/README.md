# Anexo Kimi #3 — Ruflo / 4 gaps arquitectónicos

**Tipo:** anexo de research raw — NO indexable a pgvector
**Fuente:** Kimi K2.5 Swarm, 12 dimensiones paralelas, ejecutado 2026-04-26
**Entity principal:** `docs/ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO.md`
**Razón del anexo:** los 12 dim son ~30K tokens cada (~360K tokens totales). Demasiado largos para chunking útil en pgvector. Sirven como referencia consultable manual para auditoría de fuentes o profundización técnica.

## Mapa de archivos

| Archivo | Contenido | Cuándo consultar |
|---|---|---|
| `faberloom_dim01.md` | GAP 1 dim 1/3 — Latencia y costo regex/AST vs Haiku | Validar números de Tier 0 |
| `faberloom_dim02.md` | GAP 1 dim 2/3 — Cobertura determinística docs LATAM | Validar 60-80% e-invoicing claim |
| `faberloom_dim03.md` | GAP 1 dim 3/3 — Stack recomendado (stdlib re + Pydantic) | Validar elección de librerías |
| `faberloom_dim04.md` | GAP 2 dim 1/3 — Bandit algorithms y cold start | Validar trigger >3,000 req/día |
| `faberloom_dim05.md` | GAP 2 dim 2/3 — Routers comerciales (RouteLLM, Martian, NotDiamond) | Validar descarte de routers |
| `faberloom_dim06.md` | GAP 2 dim 3/3 — ModelFingerprint crossover, transferencia histórico | Validar reglas similitud cosine |
| `faberloom_dim07.md` | GAP 3 dim 1/3 — Topologías multi-agente, Ruflo vs alternativas | Validar elección single-agent |
| `faberloom_dim08.md` | GAP 3 dim 2/3 — MAST taxonomy + propagación errores | Validar 41-86.7% claim |
| `faberloom_dim09.md` | GAP 3 dim 3/3 — Pydantic AI HITL + WhatsApp limits | Validar UX dual web/WhatsApp |
| `faberloom_dim10.md` | GAP 4 dim 1/3 — Benchmarks pgvector + RLS | Validar 20% overhead HNSW |
| `faberloom_dim11.md` | GAP 4 dim 2/3 — Alternativas (Qdrant, Weaviate, pgvectorscale, Mem0) | Validar costos comparativos |
| `faberloom_dim12.md` | GAP 4 dim 3/3 — Costos Supabase + plan migración | Validar tipping point $200/mes |
| `faberloom_cross_verification.md` | Anti-alucinación cross-dim, conflict zones | Auditar resolución CZ-001 |
| `faberloom_insight.md` | 9 insights consolidados pre-síntesis | Comparar con I-RUFLO-01..09 finales |
| `_outline.md` | Outline original del documento final | Referencia de estructura |
| `_full_report.md` | Documento final consolidado (673 líneas, 142 footnotes) | Lectura completa con contexto narrativo |

## Limitaciones conocidas

1. **Sin sección References consolidada al final.** Las 142 footnotes únicas están definidas dentro de cada `dim*.md` individual, no en una bibliografía global. Para verificar una footnote `[^N]` específica del `_full_report.md`, hay que buscar en el dim correspondiente.
2. **Fechas anómalas en headers de algunos dim** (ej. "Junio 2026" en `dim01.md` cuando la ejecución fue 2026-04-26). Probable scaffolding del runtime Kimi. No afecta validez de claims, solo trazabilidad temporal.
3. **`_full_report.md` tiene 12 dim resumidos en sus secciones, no completos.** Para detalle completo de research por gap, usar los `dim*.md` individuales.

## No tocar

Estos archivos son artefactos de research del Kimi swarm. No editar contenido — son evidencia histórica de la investigación que produjo `ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO.md`.

Si una corrección es necesaria, hacerla en la entity principal (`ENT_FABERLOOM_INSIGHTS_KIMI_RUFLO.md`) con changelog. Este anexo queda como snapshot inmutable del Kimi #3.
