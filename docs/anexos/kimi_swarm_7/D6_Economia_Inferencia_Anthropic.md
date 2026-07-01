RUN_ID: KIMI_SWARM_7_ATERRIZAJE_2026-06-12

# D6 - ECONOMIA DE PROMPT CACHING E INFERENCIA ANTHROPIC (2026)

## RESUMEN

La API de Anthropic (junio 2026) ofrece una estructura de precios de tres niveles: Haiku 4.5 ($1/$5), Sonnet 4.6 ($3/$15) y Opus 4.8 ($5/$25), con el reciente lanzamiento de Fable 5 (modelo Mythos-class) a $10/$50. El prompt caching es el mayor optimizador de costos: lectura de cache a 0.1x (90% descuento), con TTL de 5 min (default) o 1 hora (2x costo write). El break-even se alcanza en 1 lectura para 5-min y 2 lecturas para 1h. La Batch API ofrece 50% de descuento adicional con SLA de 24h. Los rate limits varian de 50 RPM (Tier 1) hasta 4,000 RPM (Tier 4), con ITPM de hasta 10M para Opus. Los estudios de degradacion (Chroma 2025, arxiv 2026) muestran que Claude mantiene >=80% accuracy en multi-hop hasta 512K tokens, con degradacion modesta a 1M.

---

## HALLAZGOS NUMERADOS

1. **Precios base vigentes (junio 2026) - Fuente oficial**: Claude Fable 5 $10/$50, Opus 4.8/4.7/4.6 $5/$25, Sonnet 4.6/4.5 $3/$15, Haiku 4.5 $1/$5. Fuente: https://platform.claude.com/docs/en/about-claude/pricing (consultada 2026-06-12). Confianza: ALTO.

2. **Prompt caching pricing multipliers - Fuente oficial**: Cache write 5-min = 1.25x base input, cache write 1h = 2x base input, cache read = 0.1x base input (90% descuento). Fuente: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching (consultada 2026-06-12). Confianza: ALTO.

3. **TTL del cache**: 5 minutos por defecto (se renueva con cada hit), opcion de 1 hora a 2x el costo de write. Fuente: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching (consultada 2026-06-12). Confianza: ALTO.

4. **Break-even de caching**: Un cache write de 5 minutos se paga con 1 lectura (1.25x write vs 0.1x read = ahorro desde la 2da lectura). Un write de 1 hora se paga con 2 lecturas (2x write vs 0.1x read). Fuente: https://platform.claude.com/docs/en/about-claude/pricing (consultada 2026-06-12). Confianza: ALTO.

5. **Minimo de tokens cacheables**: 1,024 tokens para Sonnet/Opus segun documentacion oficial. Opus 4.8 reduce el minimo a 1,024 tokens desde valores mayores en versiones previas. Fuente: https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-8 (consultada 2026-06-12); https://www.vellum.ai/llm-parameters/prompt-caching. Confianza: ALTO.

6. **Limite de breakpoints de cache**: Maximo 4 breakpoints explicitos por request. El auto-caching usa 1 slot. Fuente: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching (consultada 2026-06-12). Confianza: ALTO.

7. **Batch API descuento**: 50% de descuento en input y output tokens. Hasta 10,000 requests por batch. SLA: procesamiento dentro de 24 horas (la mayoria completa en <1h). Fuente: https://platform.claude.com/docs/en/about-claude/pricing (consultada 2026-06-12). Confianza: ALTO.

8. **Rate limits Tier 1 (oficial)**: Opus 4.x: 50 RPM / 500K ITPM / 80K OTPM. Sonnet 4.x: 50 RPM / 30K ITPM / 8K OTPM. Haiku 4.5: 50 RPM / 50K ITPM / 10K OTPM. Fable 5: 50 RPM / 100K ITPM / 20K OTPM. Fuente: https://platform.claude.com/docs/en/api/rate-limits (consultada 2026-06-12). Confianza: ALTO.

9. **Rate limits Tier 4 (oficial)**: Opus 4.x: 4,000 RPM / 10M ITPM / 800K OTPM. Sonnet 4.x: 4,000 RPM / 2M ITPM / 400K OTPM. Haiku 4.5: 4,000 RPM / 4M ITPM / 800K OTPM. Fable 5: 4,000 RPM / 4M ITPM / 800K OTPM. Fuente: https://platform.claude.com/docs/en/api/rate-limits (consultada 2026-06-12). Confianza: ALTO.

10. **Costo de subir de tier**: Tier 1 requiere $5 deposito acumulado, Tier 2 = $40, Tier 3 = $200, Tier 4 = $400. Spend limit mensual: Tier 1/2 = $500, Tier 3 = $1,000, Tier 4 = $200,000. Fuente: https://platform.claude.com/docs/en/api/rate-limits (consultada 2026-06-12). Confianza: ALTO.

11. **Context window maximo**: Fable 5: 1M tokens, Opus 4.8/4.7/4.6: 1M tokens, Sonnet 4.6: 1M tokens, Haiku 4.5: 200K tokens. Fuente: https://platform.claude.com/docs/en/about-claude/pricing (consultada 2026-06-12). Confianza: ALTO.

12. **Degradacion de calidad - MRCR v2 needle-in-haystack**: Opus 4.6 alcanza 76% accuracy en la variante 8-needle a 1M tokens (vs 18.5% de Sonnet 4.5). Fuente: https://www.anthropic.com/news/claude-opus-4-6 (publicado 2026-02-05). Confianza: ALTO (fuente primaria).

13. **Degradacion de calidad - estudio Chroma 2025**: Evaluacion de 18 modelos (incl. Claude 4, GPT-4.1, Gemini 2.5, Qwen3) muestra degradacion universal con longitud. Para 1M-token models, el efecto observable tipicamente aparece entre 300K-400K tokens. Fuente: https://www.trychroma.com/research/context-rot (publicado 2025-07-14). Confianza: MEDIO (estudio independiente reputado).

14. **Degradacion de calidad - estudio multi-hop mayo 2026**: Claude Opus 4.7 mantiene regime "estable" con >=80% accuracy en multi-hop hasta 512K, con degradacion modesta a 1M. GPT-5.5 colapsa entre 512K y 1M. Fuente: https://arxiv.org/html/2605.02173v1 (publicado 2026-05-04). Confianza: ALTO (paper academico arbitrado).

15. **Long-context pricing surcharge**: Para requests >200K tokens, el input rate se duplica (ej. Sonnet 4.6: $3 -> $6 input; Opus 4.6: $5 -> $10 input). Fuente: https://platform.claude.com/docs/en/about-claude/pricing (consultada 2026-06-12). Confianza: ALTO.

16. **Tokenizer de Opus 4.7+**: Usa un nuevo tokenizer que puede producir hasta 35% mas tokens para el mismo texto, aumentando costos efectivos. Fuente: https://platform.claude.com/docs/en/about-claude/pricing (consultada 2026-06-12). Confianza: ALTO.

---

## TABLA DE DATOS DUROS

### Precios por modelo (USD por MTok) - Fuente: docs.anthropic.com, consultada 2026-06-12

| Modelo | Input | 5m Cache Write | 1h Cache Write | Cache Read | Output | Context Window | Max Output |
|--------|-------|----------------|----------------|------------|--------|----------------|------------|
| Claude Fable 5 | $10.00 | $12.50 | $20.00 | $1.00 | $50.00 | 1M | 128K |
| Claude Opus 4.8 | $5.00 | $6.25 | $10.00 | $0.50 | $25.00 | 1M | 128K |
| Claude Opus 4.7 | $5.00 | $6.25 | $10.00 | $0.50 | $25.00 | 1M | 128K |
| Claude Opus 4.6 | $5.00 | $6.25 | $10.00 | $0.50 | $25.00 | 1M | 128K |
| Claude Opus 4.5 | $5.00 | $6.25 | $10.00 | $0.50 | $25.00 | 1M | 128K |
| Claude Sonnet 4.6 | $3.00 | $3.75 | $6.00 | $0.30 | $15.00 | 1M | 128K |
| Claude Sonnet 4.5 | $3.00 | $3.75 | $6.00 | $0.30 | $15.00 | 200K | 64K |
| Claude Haiku 4.5 | $1.00 | $1.25 | $2.00 | $0.10 | $5.00 | 200K | 64K |

**Batch API (50% descuento en input y output)** - Cache read NO aplica descuento batch adicional.

**Long-context surcharge** (>200K input tokens): input rate se duplica (ej. Sonnet 4.6 input pasa a $6/MTok, output a $22.50).

### Rate Limits por Tier (Fuente: docs.anthropic.com, consultada 2026-06-12)

| Tier | Requisito Deposito | Spend Limit Mensual | Opus 4.x RPM/ITPM/OTPM | Sonnet 4.x RPM/ITPM/OTPM | Haiku 4.5 RPM/ITPM/OTPM |
|------|-------------------|--------------------|------------------------|--------------------------|-------------------------|
| Tier 1 | $5 acumulado | $500 | 50 / 500K / 80K | 50 / 30K / 8K | 50 / 50K / 10K |
| Tier 2 | $40 acumulado | $500 | 1,000 / 2M / 200K | 1,000 / 450K / 90K | 1,000 / 450K / 90K |
| Tier 3 | $200 acumulado | $1,000 | 2,000 / 5M / 400K | 2,000 / 800K / 160K | 2,000 / 1M / 200K |
| Tier 4 | $400 acumulado | $200,000 | 4,000 / 10M / 800K | 4,000 / 2M / 400K | 4,000 / 4M / 800K |

### Break-even de Prompt Caching

| Escenario | Costo Write | Costo Read | Lecturas para break-even |
|-----------|-------------|------------|-------------------------|
| 5-min TTL | 1.25x input | 0.1x input | 2 lecturas (ahorro neto desde la 2da) |
| 1-hour TTL | 2.0x input | 0.1x input | 3 lecturas (ahorro neto desde la 3ra) |

**Nota**: El TTL de 5 min se renueva automaticamente con cada cache hit (sin costo adicional de write).

### Degradacion de contexto largo - Datos empiricos

| Estudio | Modelo | Metrica | Resultado | Fecha |
|---------|--------|---------|-----------|-------|
| MRCR v2 (Anthropic) | Opus 4.6 | 8-needle @ 1M | 76% accuracy | Feb 2026 |
| MRCR v2 (Anthropic) | Sonnet 4.5 | 8-needle @ 1M | 18.5% accuracy | Feb 2026 |
| arxiv 2605.02173 | Opus 4.7 | Multi-hop @ 512K | >=80% (regime estable) | May 2026 |
| arxiv 2605.02173 | Opus 4.7 | Multi-hop @ 1M | Degradacion modesta | May 2026 |
| Chroma Context Rot | Claude 4 family | Degradacion observable | 300K-400K threshold | Jul 2025 |
| Chroma Context Rot | 18 modelos SOTA | Degradacion universal | Todos degradan | Jul 2025 |

---

## DATOS NO ENCONTRADOS

- **Costo exacto de "Priority Tier" (tier por encima de Tier 4)**: Se menciona en docs.anthropic.com como requiriendo "committed spend" y contactar a sales, pero no se publican los numeros exactos de RPM/ITPM ni el monto minimo de compromiso. Busquedas intentadas: "Anthropic Priority Tier pricing committed spend", "site:docs.anthropic.com Priority Tier rate limits".

- **Latencia especifica (P50/P99) de la Batch API en minutos/horas**: La documentacion oficial solo indica "within 24 hours" y "most complete in under an hour". No se publican percentiles de latencia. Busquedas intentadas: "Anthropic batch API latency P50 P99", "site:docs.anthropic.com batch processing time".

- **Costo de cache storage por hora (como tiene Gemini)**: Anthropic no cobra storage fee por cache; solo cobra write y read. El pricing de Gemini 3.1 Pro incluye $4.50/MTok/hora de storage fee, pero esto no aplica a Anthropic.

---

## IMPLICACION OPERATIVA

El prompt caching es el lever mas agresivo de costos: con cache hits a 0.1x, un prefix reutilizado 10x dentro del TTL de 5 min reduce el costo input de $3.00 a ~$0.57/MTok promedio (incluyendo el write inicial). Combinado con Batch API (50% off output), el costo efectivo de Sonnet 4.6 para workloads nocturnos con contexto repetido cae a ~$0.30 input + $7.50 output. La eleccion de modelo debe ponderar que Haiku 4.5 es 5x mas barato que Sonnet pero con 200K context limit, mientras que Opus 4.8 ofrece 1M context con mejor retencion a larga distancia (76% vs 18.5% de Sonnet 4.5 en MRCR v2) pero a 5x el costo. Para workloads de agentes con contexto largo (>200K), el long-context surcharge duplica el input rate, haciendo el caching aun mas critico. Tier 4 requiere solo $400 de deposito acumulado para acceder a 4,000 RPM y 10M ITPM en Opus.
