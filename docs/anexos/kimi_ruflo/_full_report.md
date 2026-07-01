# Executive Summary

## Contexto y Alcance

Faberloom, SaaS B2B de cobranza y proformas para PYMEs latinoamericanas, evalúa cuatro gaps arquitectónicos identificados en Ruflo (ex Claude Flow) para decidir qué incorporar, descartar o diferir en su roadmap de 12 meses. El análisis aborda: (1) un tier sub-LLM para tareas determinísticas, (2) routing aprendido por evidencia entre modelos, (3) spawning controlado de sub-skills bajo gate humano, y (4) escalabilidad de pgvector con Row-Level Security (RLS) en entornos multi-tenant. La investigación cruzó literatura académica 2024–2026, benchmarks de producción, y documentación oficial de frameworks para producir recomendaciones con 85% de hallazgos clasificados como alta confianza [^4^].

Una observación estructural atraviesa los cuatro gaps: Faberloom ya opera un sistema de tiers implícito (L1 Haiku clasificador, L2 dispatcher). La pregunta correcta no es si adoptar la arquitectura de Ruflo, sino si optimizar el tier más bajo que hoy consume recursos de LLM para tareas resolubles por expresiones regulares. Esa reframing reduce el riesgo de implementación a casi cero: los cambios son aditivos, no destructivos.

## Resumen de Decisiones

La matriz de decisión consolidada sintetiza las recomendaciones por gap, fase de activación, y condiciones de trigger.

| GAP | Decisión | Fase de Activación | Trigger | Esfuerzo Estimado |
|:---|:---|:---|:---|:---|
| 1 — Tier 0 sub-LLM | **IMPLEMENTAR** | MVP (semana 1) | Siempre activo | ~3 días [^1^] |
| 2 — Routing aprendido | **DIFERIR** | Phase 2 (mes 4–6) | >3,000 req/día × 14 días consecutivos | 2–3 días de preparación hoy [^1^] |
| 3 — Spawning controlado | **DIFERIR** | Fase 6 (mes 10–12) | >3 tools con dependencias complejas | 0 días hoy; evaluación futura [^338^] |
| 4 — pgvector + RLS | **IMPLEMENTAR (stay)** | MVP continuo | Siempre activo | ~1 día de tuning [^4^] |

El balance es dos implementaciones inmediatas y dos diferimientos estratégicos, con cero gaps descartados. Ninguna recomendación requiere re-arquitectura del stack existente (Pydantic AI, LiteLLM, Supabase, FastAPI).

**GAP 1 — Tier 0 sub-LLM.** Implementar un pre-filtro determinístico antes del L1 Haiku reduce costos de tokens en 40–95% y latencia de ~1,100 ms a <100 μs para el 60–80% de tasks simples [^1^][^6^]. La cobertura determinística es inusualmente alta para el mercado LATAM: más del 90% de transacciones B2B usan facturación electrónica estructurada en XML (UBL 2.1, DTE, CFDI, NFe, AFIP) [^201^][^45^], parseable con `xml.etree.ElementTree` en sub-milisegundo sin costo de API. El riesgo de fallo silencioso del regex se mitiga con Pydantic validation obligatorio y fallback a Haiku cuando `confidence < threshold` [^186^][^131^]. LiteLLM pre-call hooks ejecutan el Tier 0 sin modificar el router existente [^183^].

**GAP 2 — Routing aprendido.** Diferir bandit algorithms (LinUCB, Thompson Sampling, ε-greedy) al periodo post-MVP. El cold start es el deal-breaker: Thompson Sampling requiere ~5,000 pulls por brazo para convergencia confiable; Faberloom procesará ~100–300 requests/día en MVP, insuficientes para estabilizar cualquier estimador en menos de 90 días [^383^][^1^]. Ningún router comercial ofrece multi-tenancy nativa con aislamiento por organización [^293^][^302^][^307^]; el router propio L1/L2 con overhead de 2–8 ms [^303^] y LiteLLM Organizations [^296^] satisface el MVP. La acción inmediata es el schema de `outcome_ledger` que acumula observaciones para calentar priors bayesianos cuando el volumen justifique la transición.

**GAP 3 — Spawning controlado.** Mantener arquitectura single-agent en MVP y diferir skill-to-skill delegation a Fase 6. MAST (UC Berkeley, NeurIPS 2025) reporta 41–86.7% tasa de fallo en multi-agente sobre 1,642 trazas [^338^]; single-agent iguala multi-agent en razonamiento multi-hop bajo igual presupuesto de tokens [^336^]. La confiabilidad compuesta de handoffs degrada exponencialmente: diez pasos al 99% producen 90.4% de confiabilidad sistémica [^385^]. Pydantic AI ya cubre delegación vía `@agent.tool` y approval gates nativos [^338^][^482^]; la restricción real es la UX de WhatsApp Business API (3 botones, 20 caracteres, sesión 24h) [^487^][^488^], que canaliza aprobaciones multi-step hacia la consola web.

**GAP 4 — pgvector + RLS.** Consolidar pgvector en Supabase Pro con HNSW default, halfvec quantization, RLS nativa, e índices compuestos `(tenant_id, ...)`. El tipping point es económico, no técnico: ~450K vectores en Supabase Pro + Large ($135/mes) representan el límite del presupuesto MVP (~$200/mes); el salto a 2XL ($435/mes) excede el presupuesto en 118% [^607^][^654^]. Alternativas técnicamente superiores (Qdrant Cloud, Weaviate Flex, pgvectorscale) se evalúan cuando la proyección supere 500K vectores o el timeline alcance 6 meses post-MVP.

Un patrón transversal emerge de los cuatro análisis: *deterministic first, LLM fallback, human gate*. Este patrón —pre-filtro regex antes de Haiku, routing rule-based antes de bandit, single-agent antes de multi-agente— no es simplificación de MVP; es estrategia de producción robusta que reduce tasas de fallo 2–5× frente a saltos directos a la capa inteligente [^5^][^7^]. La elección de LiteLLM en el stack original de Faberloom resultó ser arquitectónicamente más valiosa de lo previsto: conecta tres de los cuatro gaps mediante pre-call hooks, multi-tenancy nativa, y abstracción de embeddings [^296^][^183^][^310^].

El reporte técnico que sigue desarrolla cada gap con benchmarks, comparativas de framework, y tablas de decisión ponderadas. Las recomendaciones están calibradas para un equipo de 1–3 desarrolladores, presupuesto de infraestructura ~$200/mes, y horizonte de MVP de 60 días.
# 1. GAP 1 — Tier 0 sub-LLM: ¿Vale la pena un layer pre-LLM?

## 1.1 Hallazgo

### 1.1.1 Regex/AST puro en Python es ~20,000–220,000× más rápido que Haiku y $0 por request

El L1 Clasificador de Faberloom enruta cada mensaje entrante hacia al menos Claude Haiku 3.5 antes de cualquier decisión de enrutamiento. Ese diseño asume que toda tarea requiere inteligencia semántica. La investigación dimensional demuestra que esa suposición es costosa en latencia y económicamente innecesaria para la mayoría de los casos.

Un pattern de expresión regular compilado en Python stdlib `re` ejecuta en ~5–50 μs por operación sobre strings cortos [^1^]. La misma operación enviada a Claude Haiku 3.5 desde LATAM incurre ~750–1,100 ms de latencia total: Time-To-First-Token (TTFT) mediana de ~480–610 ms [^2^][^3^], generación de ~50 tokens de salida (~200 ms), y roundtrip de red interregional de ~100–250 ms desde hubs de LATAM a US-East. El ratio es ~15,000–220,000× en favor del regex local.

El costo económico sigue la misma asimetría. Un request de clasificación simple en Haiku 3.5 (input ~160 tokens, output ~15 tokens) cuesta $0.000188; un request de validación de formato (RUC, email) cuesta $0.000120 [^4^]. El regex ejecutado localmente cuesta $0. A 500 requests/día con 60% de tasks simples, el gasto en Haiku para tareas resolubles determinísticamente se proyecta en $9–$35/mes [^5^], equivalente al 4.5–17.5% del presupuesto de infraestructura de Faberloom (~$200/mes).

### 1.1.2 60–80% de documentos de cobranza LATAM y 75–90% de proformas son parseables sin LLM gracias a e-invoicing estructurado

La ventaja competitiva más subestimada del mercado objetivo de Faberloom es la madurez de la facturación electrónica en LATAM. Más del 90% de las transacciones B2B en Brasil, Chile, México, Colombia y Argentina utilizan facturación electrónica estructurada en XML [^201^]. Chile alcanzó 97% en 2019; Colombia obligó UBL 2.1 desde 2019 [^45^]; México exige CFDI 4.0 [^81^]; Brasil emite NFe XML con 500+ tags [^95^]; Argentina usa SOAP/XML de AFIP [^46^].

Para Faberloom, esto significa que ~60–70% de las facturas oficiales B2B son archivos XML con schemas publicados [^119^][^84^]. Extraer el monto total de una factura DIAN no requiere LLM: requiere `xml.etree.ElementTree` y una expresión XPath. La latencia es sub-milisegundo; el costo es cero; la accuracy es 100% si el XML es válido. Un sistema híbrido regex-LLM que procesa 95–98% de casos determinísticamente reduce consumo de tokens hasta 95% comparado con pipelines LLM-only [^119^].

Las proformas internas de PYMEs LATAM amplían la cobertura. Provienen de 5–10 proveedores recurrentes, usan plantillas estándar de ERPs locales, y contienen campos numéricos predecibles: SKU, cantidad, precio unitario, subtotal, impuestos, total [^185^]. Los totales aparecen al final; las cantidades usan formato predecible; las monedas son símbolos estandarizados [^120^]. La cobertura determinística para proformas se estima en ~75–90% de campos extraíbles con regex/templates [^185^][^120^].

### 1.1.3 El riesgo real no es precisión sino fallo silencioso: regex sin Pydantic validation es peor que LLM honesto que dice "no estoy seguro"

El contra-argumento más frecuente contra regex-first es la fragilidad ante edge cases: un LLM maneja naturalmente "el martes pasado"; regex requiere patterns adicionales o fallback. Sin embargo, el riesgo operativo real no es que el regex sea menos preciso — en datos estructurados alcanza 89–95% de accuracy [^6^][^27^] — sino que falla sin emitir señal de alarma.

Cuando un regex no encuentra un campo requerido, devuelve `None` y el código continúa. Esta falla silenciosa genera "crashed parsers, silent data corruption, and 3 AM pages for your on-call engineer" [^186^]. En contraste, un LLM con salida estructurada y validación Pydantic puede devolver `"unsure"` como valor explícito, o disparar una `ValidationError` catchable [^131^]. El LLM verbaliza incertidumbre (aunque sea sobre-confiado en promedio [^130^]); el regex es opaco.

La mitigación no es descartar regex, sino empaquetarlo con validación estructurada. Un sistema híbrido que usa regex para extracción rápida, Pydantic para validación de campos requeridos, y LLM como fallback cuando `confidence < threshold` combina la latencia del primero con la robustez del segundo [^210^]. La combinación regex + Pydantic validation + fallback LLM es arquitectónicamente superior a cualquiera de los dos en aislamiento.

## 1.2 Datos y Evidencia

### 1.2.1 Benchmark BI-RADS: regex 18,404× más rápido (1.45 s vs 26,686 s) con accuracy comparable (89.2% vs 87.7%)

El benchmark académico más riguroso comparando regex versus LLM para extracción estructurada proviene del dominio médico: extracción de scores BI-RADS de reportes radiológicos. Sobre un dataset de 7,764 reportes, el enfoque regex requirió 1.45 segundos versus 26,686.44 segundos del enfoque LLM — una ventaja de 18,404.44× en velocidad [^6^]. La accuracy fue comparable: 89.20% para regex versus 87.69% para LLM, con diferencia no estadísticamente significativa (p = 0.56). En un subset de 199 reportes, la ventaja alcanzó 28,120× (0.06 s vs 1,687.20 s) [^6^].

Este benchmark es relevante para Faberloom porque los reportes radiológicos son texto semi-estructurado — análogo a los mensajes de cobranza y emails de proformas. No son JSON estructurado, pero contienen campos estandarizados con valores esperados en rangos conocidos. La conclusión del estudio es explícita: para datos con patterns definidos, regex es óptimo; la ventaja del LLM aparece solo en información no estructurada o contextual.

Un segundo datapoint proviene de Uber Engineering: su sistema GenAI para invoices alcanzó 90% de accuracy general, con solo 35% de invoices alcanzando 99.5% [^184^]. Incluso en escala Uber, no todo el corpus alcanza perfección. Esto valida que un enfoque híbrido — donde los casos perfectamente estructurados se resuelven determinísticamente y el resto recibe atención del LLM — es la estrategia de producción correcta.

### 1.2.2 Costo Haiku para tasks simples: $0.00012–0.00038/request; a 500 req/día = $9–35/mes (5–17% de budget)

Claude Haiku 3.5 cuesta $0.80 por millón de tokens de input y $4.00 por millón de tokens de output [^4^]. Para tasks típicas de Faberloom, un request de extracción de monto/fecha (~230 tokens in, ~50 out) cuesta $0.000384; una clasificación por keywords (~160 in, ~15 out) cuesta $0.000188; una validación de formato RUC/email (~100 in, ~10 out) cuesta $0.000120.

La proyección mensual por volumen se comporta linealmente: a 50 req/día con 60% simples, el costo es ~$1–$3/mes (0.5–1.7% del budget); a 500 req/día, ~$9–$35/mes (4.5–17.3%); a 1,000 req/día, ~$18–$69/mes (9.0–34.5%). El punto crítico no es el costo absoluto — que permanece modesto — sino el **costo de oportunidad** en latencia percibida. Un mensaje de WhatsApp que podría clasificarse en 50 μs mediante regex pero viaja a Haiku añade ~1 segundo de delay al loop de respuesta. En canales conversacionales, 1 segundo de latencia adicional degrada satisfaction mediblemente [^18^]. Además, cada request simple que va a Haiku consume quota de rate-limiting de Anthropic e introduce un punto de fallo de red adicional.

### 1.2.3 Tabla comparativa: regex stdlib vs Haiku vs pyparsing vs Lark

La elección del stack de parsing para Tier 0 no es binaria entre regex y LLM. Existen alternativas intermedias con diferentes trade-offs de expresividad, velocidad y mantenibilidad.

| Métrica | `re` stdlib | Haiku 3.5 | pyparsing | Lark |
|---------|-------------|-----------|-----------|------|
| Latencia por operación | ~5–50 μs [^1^] | ~750–1,100 ms [^2^][^3^] | ~10–100× más lento que `re` [^54^] | ~10–50× más lento que `re` [^59^] |
| Costo por request | $0 | $0.00012–$0.00038 [^4^] | $0 | $0 |
| Madurez del proyecto | 25+ años (CPython C) | 2+ años (Anthropic) | 20+ años | 7+ años |
| Curva de aprendizaje | Baja | Baja (API REST) | Media (DSL propio) | Media (gramáticas EBNF) |
| Caso de uso óptimo | Formatos, PII, keywords | Semántica, contexto, NL ambiguo | Gramáticas complejas, DSLs | AST generation, lenguajes formales |
| Mantenibilidad a 6 meses | Alta (patterns versionados) | Alta (solo prompts) | Media (código DSL) | Media (gramáticas EBNF) |
| Overhead en stack Faberloom | Cero (built-in) | SDK + LiteLLM proxy | +1 dependencia PyPI | +1 dependencia PyPI |
| Veredicto MVP | **Implementar** | Fallback L1 | Diferir | Diferir |

Las alternativas pyparsing y Lark aportan expresividad para gramáticas complejas, pero su latencia es 1–2 órdenes de magnitud superior a `re` y su curva de aprendizaje no se justifica para un equipo de 1–3 desarrolladores con 60 días de MVP. El proyecto flpc/fastre — wrapper Rust que promete 28–68× sobre stdlib `re` — fue evaluado y descartado: es experimental (<1 año, API inestable, cero casos en producción) [^216^][^254^]. El stdlib `re` compilado ya corre en microsegundos; 28× de casi-cero sigue siendo casi-cero, y el riesgo de dependencia experimental supera cualquier ganancia marginal.

GuardrailsAI fue descartado para MVP: puntuación 72/100 en reviews, overhead 100 ms+ (dealbreaker para WhatsApp), lock-in en formato RAIL XML, y conflictos con Pydantic v2 [^187^][^217^]. Instructor — 12.3k GitHub stars — es redundante dado que PydanticAI ya provee validación post-generation con retries [^30^][^40^]. LangChain muestra estadísticas de abandono alarmantes: 45% de desarrolladores nunca lo usan en producción, y 23% de quienes lo adoptaron lo removieron [^169^]. Octomind documentó 12 meses en producción con LangChain seguidos de remoción completa [^173^].

## 1.3 Confidence Level

### 1.3.1 HIGH: Múltiples fuentes independientes (ACM TOPLAS, BI-RADS, Arthur.ai, Datadog, autoridades fiscales LATAM)

La confianza en la recomendación es **HIGH** por convergencia de fuentes independientes. La latencia de regex está respaldada por ACM TOPLAS [^13^], benchmarks de regex en GitHub [^1^], y mediciones de FastAPI [^18^]. La comparación contra Haiku usa AIonX [^3^], Kunal Ganglani [^2^], y pricing de Anthropic [^4^]. El benchmark BI-RADS (7,764 reportes) proporciona evidencia de accuracy comparable [^6^].

La adopción de e-invoicing en LATAM está documentada por autoridades fiscales primarias [^45^][^43^][^81^][^46^][^95^] y estudios transnacionales [^201^][^205^]. El patrón de pre-LLM validation está validado por Arthur.ai [^201^], NeuralStack [^63^], Datadog [^64^], y Authority Partners [^248^].

Ninguna de las tres dimensiones presenta conflictos mayores. Todas convergen en la misma recomendación: implementar Tier 0 con stdlib `re` + Pydantic validation + fallback LLM.

## 1.4 Implicación de Diseño

### 1.4.1 Implementar "Deterministic Pre-filter" como Tier 0 antes del L1 Haiku; stdlib `re` + Pydantic validation + LiteLLM pre-call hooks

Faberloom ya tiene una arquitectura de dos tiers (L1 Haiku como clasificador, L2 Dispatcher por task_type + complexity + cost). La recomendación no es reemplazar esos tiers, sino insertar un Tier 0 determinístico **antes** del L1 existente. Este cambio es aditivo, no destructivo: no requiere modificar el L1 ni el L2, solo interceptar requests que pueden resolverse localmente antes de que lleguen a LiteLLM.

La arquitectura propuesta sigue el patrón de "defensa en profundidad" documentado por VentureBeat como "Layer 1: Deterministic assertions — the pipeline's first gate, using traditional code and regex to validate structural integrity" con principio fail-fast [^58^], y por n8n como "Deterministic Steps & AI Steps" donde los pasos determinísticos corren antes de los pasos AI [^191^]. El concepto académico de "Reflex Fabric" — un sub-LLM layer que intercepta decisiones rutinarias antes de invocar al LLM, logrando 2.4 millones× más rápido que LLM routing (0.0034 ms vs ~600 ms) [^7^] — describe precisamente lo que Faberloom implementaría en Python con stdlib `re`.

La integración con el stack existente consume ~3 días de esfuerzo: 1–2 días para middleware FastAPI con pre-check regex antes del agente Pydantic AI; 0.5 días para configurar `ModelFingerprint` con `tier` en metadata; 0.5 días para LiteLLM pre-call hooks que ya soportan keyword blocking y regex-based detection de sensitive data [^183^]; y 1 día para tests unitarios de patterns. Los requests resueltos en Tier 0 nunca pasan por LiteLLM.

El `ModelFingerprint` de Faberloom debería incluir campos adicionales para tracking de Tier 0: `tier_used` (0/1/2/3), `latency_ms`, `cost_usd` (0 para Tier 0), y `accuracy_score` (validación post-hoc comparando regex contra ground truth o LLM fallback). Esto permite que el sistema "aprenda" cuándo Tier 0 es suficiente y cuándo necesita escalar automáticamente, sentando las bases para el routing aprendido del GAP 2.

### 1.4.2 14 reglas concretas para MVP cobranza: parsers XML por país, validación TIN, extracción email

Basado en los hallazgos de cobertura determinística para LATAM, Faberloom puede implementar las siguientes reglas Tier 0 durante las primeras 3 semanas de desarrollo:

| # | Categoría | Regla | Implementación | Complejidad |
|---|-----------|-------|----------------|-------------|
| 1 | XML Estructurado | Parse DIAN UBL 2.1 (Colombia) | `xml.etree.ElementTree` → extraer `cbc:ID`, `cbc:IssueDate`, `cac:LegalMonetaryTotal/cbc:PayableAmount` | Baja |
| 2 | XML Estructurado | Parse SII DTE (Chile) | `xml.etree.ElementTree` → extraer `Encabezado/IdDoc/TipoDTE`, `Folio`, `FchEmis`, `Totales/MntTotal` | Baja |
| 3 | XML Estructurado | Parse SAT CFDI (México) | `xml.etree.ElementTree` → extraer `@Folio`, `@Fecha`, `cfdi:Emisor/@Rfc`, `cfdi:Receptor/@Rfc`, `cfdi:Total` | Baja |
| 4 | XML Estructurado | Parse AFIP WS (Argentina) | SOAP XML → extraer `Cbte_nro`, `FchCotiz`, `MonCotiz` | Baja |
| 5 | XML Estructurado | Parse NFe (Brasil) | `xml.etree.ElementTree` → extraer `infNFe/ide/nNF`, `infNFe/total/ICMSTot/vNF` | Media |
| 6 | Validación TIN | Validar RUT Chile | `python-stdnum` o implementar MOD 11 con multiplicadores [2,3,4,5,6,7] [^99^][^101^] | Baja |
| 7 | Validación TIN | Validar NIT Colombia | `python-stdnum` o implementar MOD 11 con multiplicadores [41,37,29,23,19,17,13,7,3] [^93^][^96^] | Baja |
| 8 | Validación TIN | Validar CUIT Argentina | Regex formato `\d{2}-?\d{8}-?\d{1}` + validación longitud [^29^] | Baja |
| 9 | Clasificación | Clasificar tipo documento por extensión/tag | `.xml` + tag raíz = tipo documento (no ML) | Baja |
| 10 | Extracción | Extraer monto/fecha de asunto de email | Regex: `r"(?:factura|proforma|recibo)\s*[#N°]\s*(\d+)"` | Baja |
| 11 | Extracción | Extraer cantidades numéricas | `r"(?:cantidad|qty|unidades)[:\s]*(\d+(?:[.,]\d+)?)"` | Baja |
| 12 | Detección | Detectar moneda por símbolo | `$` → USD/COP/CLP/ARS/MXN según país tenant; `S/` → PEN; `R$` → BRL | Baja |
| 13 | Validación | Validar matemática de totales | `sum(line_items) == subtotal` y `subtotal + tax == total` | Baja |
| 14 | Detección | Detectar vencimiento por keywords | `vencido`, `vence el`, `due date` → extraer fecha siguiente | Media |

La cobertura proyectada es ~80–95% determinístico para el workflow de Cobranza y ~75–90% para Proformas [^119^][^84^][^185^][^120^]. El 5–20% restante cae al fallback LLM. Este patrón híbrido está documentado en producción: un sistema de moderación alcanzó 90% de automatización con reglas + ML combinado, logrando 10,000× validación de perfiles más rápida [^35^].

## 1.5 Decisión Recomendada

### 1.5.1 IMPLEMENTAR en MVP (día 1–3 de desarrollo, ~3 días de esfuerzo, reduce costos 40–95%)

La matriz de decisión siguiente evalúa tres alternativas para abordar el GAP 1: (A) mantener la arquitectura actual sin Tier 0, (B) implementar Tier 0 con stdlib `re` + Pydantic, y (C) implementar Tier 0 con un framework externo (GuardrailsAI, Instructor, o librería Rust experimental).

| Criterio | Peso | Alt. A: Sin Tier 0 | Alt. B: `re` + Pydantic | Alt. C: Framework externo |
|----------|------|-------------------|------------------------|--------------------------|
| Latencia p95 | 25% | ~1,100 ms (Haiku) | ~50 μs + 5 ms validation | ~100–200 ms + overhead framework |
| Costo mensual (500 req/día) | 20% | ~$9–$35/mes | ~$2–$7/mes (fallback 20%) | ~$2–$7/mes + costo licencia |
| Esfuerzo implementación | 15% | 0 días | ~3 días | ~5–10 días (curva aprendizaje) |
| Riesgo de fallo silencioso | 20% | Alto (LLM hallucina) | Bajo (Pydantic ValidationError) | Medio (depende del framework) |
| Mantenibilidad a 6 meses | 15% | Alta (solo prompts) | Alta (patterns versionados) | Media (lock-in framework) |
| Riesgo de dependencia experimental | 5% | Nulo | Nulo (stdlib) | Alto (flpc/fastre <1 año) |
| **Score ponderado** | 100% | **2.15/5.0** | **4.75/5.0** | **3.10/5.0** |

**Score detallado:**
- Alt. A (Sin Tier 0): 25%×1 + 20%×1 + 15%×5 + 20%×2 + 15%×4 + 5%×5 = 2.15
- Alt. B (re + Pydantic): 25%×5 + 20%×4 + 15%×4 + 20%×5 + 15%×5 + 5%×5 = 4.75
- Alt. C (Framework externo): 25%×3 + 20%×4 + 15%×3 + 20%×3 + 15%×3 + 5%×2 = 3.10

La Alternativa B domina en todos los criterios ponderados excepto esfuerzo, donde la Alternativa A gana trivialmente por ser el status quo. Los 3 días de esfuerzo de la Alternativa B se amortizan en la primera semana de operación por reducción de latencia percibida y eliminación de dependencia de API externa para decisiones determinísticas.

**Decisión formal: IMPLEMENTAR Tier 0 Deterministic Pre-filter en MVP, Semana 1.**

El patrón arquitectónico no es "regex versus LLM"; es "deterministic first, LLM fallback, human gate". Este patrón aparece validado académicamente como "cascading" (RouteLLM documenta ahorros de hasta 85% manteniendo 95% de calidad de GPT-4) [^10^], en producción enterprise como "sub-LLM layer" (Reflex Fabric, 2.4M× más rápido) [^7^], y como best practice de guardrails pre-LLM (Arthur.ai, Datadog, Authority Partners) [^11^][^64^][^248^].

Para Faberloom, el valor estratégico va más allá del ahorro de costos. El mercado LATAM tiene >90% de e-invoicing estructurado [^201^] — una ventaja competitiva masiva frente a mercados como EE.UU. donde los invoices son PDFs no estructurados. Invertir en parsers XML por país como core competency reduce costos, mejora latencia, y aumenta precisión. Es un diferenciador frente a competidores genéricos que usan LLM para todo.

El desarrollo consume ~3 días: 1–2 días para middleware FastAPI con pre-check regex, 0.5 días para integración PydanticAI con `ModelFingerprint` ampliado, 0.5 días para LiteLLM pre-call hooks, y 1 día para tests unitarios. El impacto proyectado: reducción de 40–95% en costos de tokens para tasks simples, latencia p95 de <100 ms para el 80% de requests determinísticos, y eliminación del punto de fallo de red para decisiones estructurales.
## 2. GAP 2 — Routing Aprendido por Evidencia

### 2.1 Hallazgo

#### 2.1.1 Routing por bandit algorithms supera routing estático en costo-eficiencia, pero requiere ~5,000 requests/brazo para convergencia confiable

La literatura de LLM routing 2024–2026 converge en una conclusión cuantificable: los algoritmos bandit contextual (LinUCB, Thompson Sampling, ε-greedy) superan al routing estático en accuracy y costo cuando operan en régimen de datos suficientes. GreenServ, evaluado sobre 16 modelos locales, reporta +22% en accuracy y −31% en consumo energético con overhead inferior a 8ms [^1^]. PILOT alcanza el 93% del desempeño de GPT-4 al 25% de su costo en RouterBench [^2^]. PROTEUS, entrenado offline con Lagrangian RL, logra 90.1% de accuracy con ahorros de 89.8% en costo versus el mejor modelo fijo [^3^].

Sin embargo, estos resultados operan bajo una premisa que Faberloom no satisface: volumen de requests por brazo suficiente para que el estimador estabilice. Thompson Sampling requiere ~5,000 *pulls* para identificar un brazo 5% superior con confianza estadística; un A/B testing tradicional demandaría ~635,000 muestras para el mismo nivel de certeza [^383^]. LinUCB necesita ~500 rondas para converger y ~15 observaciones contextuales por brazo solo para empatar con métodos de factorización [^321^][^322^]. En la práctica, donde cada brazo representa una combinación de modelo y tipo de tarea, el umbral mínimo de activación se proyecta entre 3,000 y 5,000 requests/día agregados.

#### 2.1.2 Cold start es el deal-breaker para MVP: Faberloom procesará ~100–300 req/día, un bandit puro tardaría semanas en estabilizar

La proyección de volumen del MVP — 100 a 300 requests/día distribuidos entre cobranza, proformas y clasificación de intención — coloca al sistema en régimen de datos extremadamente escasos. GreenServ reporta que un modelo nuevo requiere ~100 queries para estabilizar su frecuencia de selección en un portfolio calibrado [^4^]. ParetoBandit necesita ~142 pasos de exploración forzada antes de que un modelo *cold-started* alcance "adopción significativa" [^5^]. En producción de sistemas de recomendación, Thompson Sampling con priors informativos (ej. *beta*(20, 980) derivado de un CTR histórico del 2%) se mantiene inmóvil hasta acumular 1,000 impresiones [^379^].

Trasladado a Faberloom: con 100 requests/día y 9 brazos efectivos (3 modelos × 3 task_types), cada brazo recibe ~11 observaciones/día. Alcanzar los 1,000 pulls mínimos demandaría ~90 días. Durante ese período, el sistema asignaría requests a modelos potencialmente subóptimos sin garantía de corrección. En cobranza y proformas B2B, donde un error impacta directamente la relación comercial del cliente, este riesgo es inaceptable para un MVP de 60 días.

#### 2.1.3 Ningún router comercial ofrece multi-tenancy nativa con aislamiento por organización

La evaluación de routers comerciales — RouteLLM, Martian, NotDiamond y OpenPipe — revela una carencia crítica: ninguno ofrece routing aislado por tenant con presupuestos, *model pools* y políticas independientes por organización [^316^][^307^][^302^]. Martian opera como servicio cloud propietario de caja negra, sin self-hosting; los prompts atraviesan su infraestructura, generando riesgo de *data residency* incompatible con LATAM [^302^]. NotDiamond funciona como *recommender* client-side — envía el prompt a su API, recibe recomendación en <50ms, y la aplicación ejecuta el llamado directo [^307^] — pero no documenta aislamiento por tenant ni integración nativa con LiteLLM [^176^]. RouteLLM carece de concepto de organización [^109^]. OpenPipe no es un router: es una plataforma de fine-tuning [^263^].

LiteLLM, ya en el stack de Faberloom, implementa multi-tenancy nativa con jerarquía Organizations → Teams → Users → Keys, incluyendo aislamiento de datos, atribución de costos por cliente, límites de presupuesto y control de acceso a modelos por tenant [^296^]. Su limitación es que el routing es *provider-level* (balanceo entre deployments del mismo modelo), no *intelligence-level* (selección entre modelos de diferente capacidad) [^310^]. La combinación de LiteLLM como capa multi-tenant más un router propio (L1/L2) es la única arquitectura que satisface simultáneamente aislamiento por organización y decisión de modelo por calidad de prompt.

### 2.2 Datos y Evidencia

#### 2.2.1 GreenServ (16 LLMs): +22% accuracy, −31% energy, routing overhead <8 ms; pero necesitó ~100 queries para estabilizar

GreenServ es el caso de éxito más documentado en routing de LLMs con bandit contextual. El sistema emplea LinUCB sobre un vector de contexto compuesto por *task_type*, *semantic cluster* y *complexity bin*, ejecutando la decisión de routing en ~0.86ms sobre una cadena total de ~7.77ms [^1^]. El ablation study identifica que *task_type* es la feature más informativa individual, reduciendo la mediana de *regret* acumulado a ≈400. La inclusión de todas las features conjuntamente elevó el *regret*, atribuible a dimensionalidad excesiva con muestras limitadas [^1^].

La lección operativa es doble. Primera: el overhead computacional es despreciable frente a la latencia de APIs externas (Haiku ~597–639ms TTFT; GPT-4.1 Mini hasta 2,205ms p95 [^6^]). Segunda: la convergencia de ~100 queries por brazo asume carga continua en 16 modelos locales. En el MVP con 3 modelos y ~33 observaciones/día por brazo, la estabilización demoraría 3 días — aceptable en velocidad pero no en confianza: 100 muestras proporcionan margen de error del ±10% al 95% de confianza [^389^], insuficiente para discriminar entre modelos frontier con gaps pequeños. El lower bound teórico de *pure exploration* establece que la *sample complexity* crece como Ω(H log(1/δ)), donde H ~ 1/Δ² [^409^]. Si Haiku y Sonnet difieren en solo 3–5% de *win rate* para proformas, H se dispara y el sistema necesita miles de muestras.

#### 2.2.2 RouteLLM reproducibilidad cuestionable: 47% accuracy en RouterArena (ICLR 2026), peor que baseline heurístico

RouterArena (ICLR 2026), el benchmark comparativo más riguroso publicado hasta la fecha, evalúa 12 routers en 44 categorías con 5 métricas unificadas [^293^]. RouteLLM alcanza 47.0% de accuracy general — séptimo lugar de 12 routers. En queries "Hard", colapsa al 2.0% [^293^]. Su latencia de 546.8ms es la más alta de todos los routers evaluados, atribuible a su dependencia de la OpenAI Embedding API [^293^].

Los problemas trascienden el benchmark. Un equipo independiente reprodujo el router BERT e identificó *majority class overfitting* con macro F1 de 0.23–0.35, junto a dataset incompleto: los autores reclamaban 65K muestras pero solo 19K eran accesibles [^274^]. El repositorio no recibe actualizaciones desde agosto de 2024 [^327^]. Adicionalmente, RouteLLM no soporta contextos superiores a 8,192 tokens [^293^] — limitación severa para SaaS B2B donde proformas y contratos pueden exceder esa longitud.

#### 2.2.3 Router propio L1 Haiku + L2 dispatcher: overhead 2–8 ms, multi-tenant vía LiteLLM Organizations, control total de datos

La arquitectura actual de Faberloom — L1 clasificador (Haiku para *intent classification*) + L2 dispatcher — tiene métricas favorables. LiteLLM proxy reporta overhead de 2ms mediana (P95: 8ms) con 4 instancias en load tests de 1,170+ RPS [^303^]. El L1 clasificador añade ~500–800ms de latencia de API, pero esa carga existiría bajo cualquier esquema de routing porque la clasificación de intención es prerequisito independiente.

El control total de datos es diferenciador crítico para PYMEs LATAM. Martian requiere enviar prompts a servidores de terceros [^302^]. NotDiamond exige exponer el contexto del prompt a su API [^307^]. El router propio procesa todo internamente: los datos del cliente nunca salen del perímetro de LiteLLM Organizations + Supabase RLS [^296^].

---

**Tabla 1. Evaluación comparativa de opciones de routing para Faberloom MVP**

| Dimensión | RouteLLM | Martian | NotDiamond | Router Propio (L1/L2) |
|-----------|----------|---------|------------|----------------------|
| Accuracy (RouterArena) | 47.0% [^293^] | No evaluado | 68.0% [^293^] | N/A (rule-based) |
| Costo router/mes | $20–50 (infra) [^109^] | $20+ base [^316^] | $100 base [^295^] | $0 (infra existente) |
| Latencia overhead | 546.8 ms [^293^] | 20–50 ms [^310^] | ~40 ms [^300^] | 2–8 ms [^303^] |
| Multi-tenancy nativa | No | No | No documentado | Sí (LiteLLM) [^296^] |
| Self-hosting / aislamiento de datos | Parcial | No (cloud-only) [^302^] | Client-side recommender | Total |
| Contexto >8K tokens | No soportado [^293^] | No documentado | No documentado | Sí (por diseño) |
| Integración LiteLLM | Requiere adaptación | Requiere reemplazo | Requiere capa adicional [^176^] | Nativa |

Ningún router comercial ofrece simultáneamente bajo costo, baja latencia, multi-tenancy nativa y control total de datos. NotDiamond logra la mejor accuracy evaluable (68.0%) pero a $9.34 por 1K queries [^293^] — un orden de magnitud superior a routers open-source como MIRT-BERT ($0.15/1K) [^293^] — y consume el 50% del presupuesto mensual de infraestructura de Faberloom solo en la cuota base. Martian, aunque más barato ($20/mes), es caja negra con cobertura de solo 6 providers [^311^] y sin presencia en benchmarks académicos. RouteLLM queda descartado por reproducibilidad, mantenimiento y latencia inaceptable para WhatsApp.

---

**Tabla 2. Comparación de algoritmos bandit para routing de LLMs**

| Criterio | Thompson Sampling | LinUCB | ε-greedy decay | UCB1 vanilla |
|----------|---------------------|--------|----------------|--------------|
| Regret asintótico | Óptimo (Õ(d^3/2√T)) [^332^] | Bueno (O(d√T)) | Subóptimo lineal | Subóptimo logarítmico |
| Determinismo / debug | Estocástico (difícil) | Determinístico (fácil) | Semi-determinístico | Determinístico |
| Cold start (<100 pulls) | Lento (alta varianza inicial) | Lento (intervalos grandes) | **Rápido** (explota temprano) [^321^] | Rápido pero inestable [^321^] |
| Muestras para convergencia | ~5,000 pulls/brazo [^383^] | ~500 rondas [^321^] | ~100–200 steps | ~1,000+ pulls |
| Costo computacional/decisión | Moderado | O(|M|d³) — bajo para K≤16 [^1^] | Mínimo | Mínimo |
| Non-stationarity (drift) | Requiere adaptación | Requiere *forgetting* [^5^] | **Nunca se recupera** [^7^] | Requiere *sliding window* |
| Presupuesto / cost ceiling | Interacción impredecible con Lagrangian [^5^] | Interacción predecible [^5^] | Fácil de *gatear* | Fácil de *gatear* |
| Uso en LLM routing 2024–2026 | GreenServ baseline [^1^] | **GreenServ, PILOT, ParetoBandit** [^1^][^2^][^5^] | Walmart producción [^379^] | Raramente usado |

La comparación valida la postura conservadora de Faberloom para el MVP. LinUCB domina la literatura de LLM routing por tres ventajas operativas: determinismo (score reproducible que facilita debugging), interacción predecible con penalizaciones Lagrangianas [^5^], y complejidad computacional manejable para portfolios pequeños [^1^]. PILOT extiende LinUCB con *embeddings* de preferencia humana, alcanzando el 93% del desempeño de GPT-4 al 25% de costo [^2^].

Thompson Sampling ofrece mejor *regret* asintótico pero su naturaleza estocástica interactúa impredeciblemente con restricciones de costo. ParetoBandit eligió explícitamente UCB sobre Thompson Sampling porque "its deterministic score interacts more predictably with the Lagrangian penalty" [^5^]. ε-greedy *decay* converge más rápido inicialmente que UCB — atributo valioso en cold start — pero nunca se recupera de *drift* en las recompensas porque ε decae a un valor irrisorio antes de detectar el cambio [^7^]. Para APIs de terceros donde los modelos no experimentan *drift* diario, esta limitación es secundaria.

La síntesis para Faberloom es que ε-greedy *decay* (ε₀ = 0.3 → 0.05) es el algoritmo de transición más pragmático cuando el volumen justifique activar el aprendizaje: más simple de implementar que LinUCB, insensible a la elección de priors, y fácil de *gatear* por presupuesto. LinUCB contextual completo se reserva para Phase 3+ cuando el sistema acumule >5,000 requests/día.

### 2.3 Confidence Level

**HIGH** para la decisión de mantener routing L1/L2 rule-based en el MVP. La evidencia es convergente en tres dimensiones: (a) los routers comerciales evaluados no satisfacen los requisitos de multi-tenancy, costo o latencia; (b) el overhead del router propio (2–8ms) es competitivo; (c) LiteLLM Organizations ya provee aislamiento por tenant sin costo adicional [^296^][^303^][^293^].

**MEDIUM** para la proyección de bandit adaptativo en Phase 2. Los datos de convergencia varían por *workload*: GreenServ reportó estabilización en ~100 queries para modelos locales con carga continua [^4^], pero ParetoBandit necesitó ~142 pasos en un portfolio de 3 modelos con 1,824 prompts [^5^]. Con d = 10–20 features y K = 3 modelos, el umbral de activación se proyecta entre 3,000 y 5,000 requests/día — cifra que Faberloom no alcanzará en los primeros 6 meses de crecimiento orgánico B2B.

### 2.4 Implicación de Diseño

#### 2.4.1 Mantener L1/L2 rule-based en MVP; diseñar ModelFingerprint como feature de routing (no solo seguridad) para Phase 2

El ModelFingerprint de Faberloom — vector de embedding de comportamiento de 384 dimensiones — debe evolucionar de mecanismo de seguridad a feature de routing contextual. El patrón estándar en producción (Scope, DFPE, Behavioral Fingerprint) emplea *embeddings* de comportamiento principalmente para routing, no para seguridad [^384^][^282^]. Cuando un nuevo modelo llega, el fingerprint compara su comportamiento contra el anterior mediante similitud coseno: valores >0.8 indican modelos de la misma familia, permitiendo transferir el histórico con descuento de 0.5; valores <0.1 señalan familias independientes que requieren cold start completo [^318^][^411^].

ModelFingerprint debe exponer una API interna que permita consultar similitud de modelos no solo para el gate de probation, sino como input al futuro vector de contexto del bandit. La transferencia de histórico mediante priors bayesianos entre tareas relacionadas es un mecanismo establecido en *warm-start* contextual bandits [^377^].

#### 2.4.2 Epsilon-greedy decay (ε = 0.3 → 0.05) como algoritmo de transición cuando se alcancen >3,000 req/día

La decisión de algoritmo para la transición debe privilegiar simplicidad y robustez ante feedback escaso. ε-greedy *decay* satisface ambos criterios: su implementación en Python puro requiere <20 líneas de código, no depende de inversión de matrices (como LinUCB), y su parámetro de exploración decae de forma predecible. La calibración recomendada es ε₀ = 0.3 durante los primeros ~1,000 steps, decaimiento exponencial con α = 0.995 por step, y piso εₘᵢₙ = 0.05 para evitar el *wrong winner* problem [^174^].

La exploración debe ser *budget-gated*: modelos caros solo se exploran si el tenant tiene presupuesto disponible, y modelos de baja calidad se rechazan después de exploración acotada [^5^]. La exploración intra-tier es más segura que inter-tier, particularmente para proformas donde un error tiene impacto financiero directo.

#### 2.4.3 Granularidad global por task_type (NO per-org); RLS per-org se mantiene para seguridad

La tensión entre aprendizaje y seguridad resuelve en dos capas separadas. GreenServ demostró que *task_type* es la feature más informativa para routing, mientras que *org_id* como feature directa fragmenta los datos: con 100 tenants y 9 brazos, cada combinación recibe ~1 observación/día, insuficiente para cualquier estimador [^1^]. DFPE confirma que la granularidad óptima es *subject-level* (task domain), no *organization-level* [^282^]. PURPLE modela interacciones *query-record* y perfiles de usuario, no organizaciones [^392^].

Faberloom debe mantener RLS per-org en Supabase como mecanismo de seguridad. El router de Phase 2 debe operar con features de *task_type* + *query_embedding* + *text_length*, agregando *across-org*. Si un tenant enterprise alcanza >1,000 requests/mes, puede evaluarse *per-org routing* con *pooling* parcial, pero esa sofisticación es Phase 3. La documentación arquitectónica debe dejar explícito este principio para evitar que un desarrollador futuro agregue *org_id* al vector de contexto.

### 2.5 Decisión Recomendada

**⏳ DIFERIR** la implementación de bandit adaptive routing a Phase 2 (trigger: >3,000 requests/día sostenidos por al menos 14 días consecutivos).

**✅ IMPLEMENTAR** en el MVP el schema de OutcomeLedger y el *feedback loop* de preparación:

1. **Tabla `outcome_ledger`**: schema con campos `(request_id, task_type, model_used, prompt_hash, response_hash, latency_ms, cost_usd, user_feedback, llm_judge_score, timestamp, org_id — RLS-isolated)`. Esta tabla no activa el bandit todavía, pero acumula los datos necesarios para calibrarlo.

2. **Feedback loop pasivo**: en cada respuesta del agente, registrar (a) latencia real, (b) costo real vía LiteLLM *spend logs*, (c) *user feedback* (thumbs up/down en WhatsApp o consola web), (d) *LLM-as-judge* score cuando sea factible (Phase 1.5). El reward del futuro bandit será una combinación ponderada de estas cuatro señales.

3. **ModelFingerprint API interna**: exponer endpoint `GET /model/similarity?new={model_id}&reference={baseline_id}` que retorne similitud coseno y recomendación de *transfer* (descuento 0.5 para similitud >0.8, cold start para <0.2). Este endpoint se consume hoy por el sistema de probation; mañana por el sistema de routing.

La preparación tiene un costo de implementación estimado en 2–3 días de trabajo de un desarrollador. El retorno de esta inversión es la eliminación del cold start cuando Phase 2 se active: en lugar de arrancar con un bandit en *tabula rasa*, Faberloom dispondrá de miles de observaciones históricas para inicializar priores informativos.
# 3. GAP 3 — Spawning Controlado de Sub-Skills bajo Gate Humano

## 3.1 Hallazgo

### 3.1.1 Skill-to-skill delegation punto-a-punto es técnicamente viable en Pydantic AI ("agent como tool"), pero la evidencia académica y de producción favorece single-agent para workloads <5 tools

Pydantic AI implementa delegación de agentes nativamente mediante el patrón "agente como herramienta": un agente padre registra una tool cuyo cuerpo interno invoca `await delegate_agent.run(...)` y propaga el uso de tokens vía `ctx.usage` [^338^]. El ecosistema de terceros amplía esta capacidad con paquetes como `subagents-pydantic-ai`, que añade modos sync/async/auto, nested subagents y task cancellation, sin abandonar el runtime de Pydantic AI [^485^]. A nivel de framework, la delegación está resuelta: no constituye un gap técnico.

Sin embargo, la evidencia empírica converge en una conclusión que limita severamente cuándo conviene usarla. Para workloads con menos de cinco herramientas y dos workflows (cobranza, proformas) —el perfil exacto del MVP de Faberloom—, un single-agent con routing L1/L2 iguala o supera a arquitecturas multi-agente en calidad, latencia y costo. Un paper presentado en NeurIPS 2025 demuestra que un single agent con conversaciones multi-turno y reutilización de KV cache simula workflows multi-agente homogéneos con performance comparable y costo sustancialmente menor [^336^]. Microsoft Azure, en su Cloud Adoption Framework, clasifica el single-agent como "el punto de partida más eficiente para casos de baja complejidad" [^325^]. La recomendación práctica de la comunidad de ingeniería es directa: "no sobreutilices multi-agent setups; muchos workflows se resuelven mejor con un solo agente, orquestación fuerte y pocas herramientas de calidad" [^295^].

La implicación para Faberloom es que la viabilidad técnica de la delegación no debe confundirse con su conveniencia estratégica. Pydantic AI puede hacerlo; los datos dicen que, en este momento, no debería.

### 3.1.2 MAST (UC Berkeley, NeurIPS 2025): 41-86.7% tasa de fallo en multi-agente; single-agent supera multi-agent en razonamiento multi-hop bajo igual presupuesto de tokens

El estudio MAST (Multi-Agent System Failure Taxonomy), realizado por el Sky Computing Lab de UC Berkeley y publicado como Spotlight en NeurIPS 2025, analizó 1,642 trazas de ejecución en siete frameworks multi-agente de código abierto [^338^]. Los anotadores expertos (Cohen's Kappa = 0.88) identificaron 14 modos de fallo únicos, agrupados en tres categorías: fallos de especificación y diseño del sistema (~41.8%), desalineación inter-agente (~36.9%), y fallos de verificación y terminación de tareas (~21.3%) [^357^][^360^]. Las tasas de fallo por framework oscilaron entre 41% (el mejor) y 86.7% (el peor), con una media proyectada que sitúa a más del 50% de las ejecuciones multi-agente en rutas de error.

En paralelo, un paper de 2026 sobre razonamiento multi-hop establece que, bajo igual presupuesto de "thinking tokens", los sistemas single-agent consistentemente igualan o superan a los multi-agente [^336^]. El argumento es information-theoretic: por la Data Processing Inequality, un pipeline multi-agente $M = g(C)$ no puede aumentar la información mutua con la respuesta correcta más allá de lo que ya posee el contexto compartido $C$. Las ventajas reportadas de multi-agente se explican mejor por computación no contabilizada y efectos de contexto que por beneficios arquitectónicos inherentes [^336^].

La confiabilidad compuesta de handoffs secuenciales empeora exponencialmente: diez pasos con confiabilidad individual del 99% producen una confiabilidad sistémica del 90.4% ($0.99^{10}$). Veinte pasos al 95% caen al 35.8% ($0.95^{20}$) [^385^]. Para un MVP de 60 días, esta degradación exponencial convierte cada handoff adicional en una apuesta contra la estabilidad del sistema.

### 3.1.3 CONTRADICCIÓN CON BRIEF ORIGINAL: El dato "87% hallucination cascade en 4h" NO es verificable; "4h" es extrapolación, no dato empírico

El brief original de Faberloom cita "87% de hallucination cascade en 4 horas" como justificación para descartar multi-agente en MVP. La investigación exhaustiva de fuentes primarias no localizó ningún paper que reporte esta métrica exacta con ventana temporal de 4 horas. El valor 86.7% existe como límite superior del rango MAST, pero sin temporalidad asociada [^338^]. La cifra "4h" parece provenir de modelos de costo de producción publicados por Cycles (runcycles.io), cuyo autor declara explícitamente: "todas las cifras en dólares de las tablas de costo y escenarios modelados son ilustrativas; no son datos de producción medidos" [^385^].

La resolución de esta contradicción es directa: la decisión de NO usar multi-agente en MVP sigue siendo arquitectónicamente correcta, pero el argumento debe sustituirse por evidencia verificable. El rango 41-86.7% de MAST, el paper de single-agent vs multi-agent de NeurIPS 2025, y el multiplicador de costos 2-5× constituyen una base de argumentación más sólida frente a stakeholders técnicos o inversores. Presentar un dato compuesto como empírico erosiona la credibilidad del equipo si se verifica.

## 3.2 Datos y Evidencia

### 3.2.1 Pydantic AI soporta delegación nativa vía `@agent.tool` con `await delegate_agent.run()`; pydantic-graph funcional pero overkill para 2-3 pasos

La delegación en Pydantic AI opera a nivel de Python, no a nivel de prompt. El agente padre no "razona" dinámicamente sobre qué subagente invocar; el desarrollador define las tools disponibles mediante decoradores `@agent.tool` [^338^]. Esto sacrifica flexibilidad en favor de control explícito: menos magia, más trazabilidad. Para Faberloom, cuyo routing L1→L2 ya es determinístico (Haiku clasifica intención, dispatcher selecciona modelo por `task_type` + `complexity` + `cost`), este trade-off es favorable.

La documentación oficial posiciona `pydantic-graph` —una librería de state machines pura, sin dependencia de `pydantic-ai`— como el "cuarto nivel de complejidad", destinado a "los casos más complejos" [^483^]. Su API está marcada como beta (`/beta/` en la URL de documentación), y las comparativas de framework la califican como "básica" frente a LangGraph, donde los graphs son "core design" [^484^]. Para workflows de dos a tres pasos —el horizonte del MVP de Faberloom—, `pydantic-graph` es overkill. El patrón "agent como tool" o el hand-off programático (llamadas `await` secuenciales con validación de salida) son menos verbosos y mantienen la trazabilidad sin añadir una dependencia beta.

| Capacidad | Pydantic AI nativo | pydantic-graph | LangGraph |
|-----------|-------------------|----------------|-----------|
| Delegación agent-to-agent | ✅ vía `@agent.tool` | ❌ No aplica | ✅ vía `Command(goto=)` |
| Checkpointing/persistencia | ❌ No nativo | ❌ No nativo | ✅ PostgreSQL, SQLite, Redis [^361^] |
| State machine | ❌ No nativo | ✅ Beta | ✅ Core design |
| Curva de aprendizaje | Baja (Pythonic) | Media | Alta (graph concepts) [^484^] |
| Multiplicador de tokens | 1.0× (single-agent) | 1.0× | 1.3-1.8× [^431^] |
| Overhead para 2-3 pasos | Mínimo | Medio | Alto |

La tabla anterior no invita a una elección abstracta entre frameworks, sino a una decisión contextual: para el MVP de Faberloom, la columna relevante es la primera. Pydantic AI nativo cubre la delegación si alguna vez se necesita, sin añadir infraestructura de graphs ni checkpointing. LangGraph, con su multiplicador de tokens de 1.3-1.8× y su curva de aprendizaje alta, es un candidato para Fase 6, no para los próximos 60 días.

### 3.2.2 Human approval nativa: `requires_approval=True` y `ApprovalRequired()`; pero WhatsApp Business API limita a 3 botones/20 chars/sesión 24h

Pydantic AI implementa human-in-the-loop (HITL) nativamente mediante deferred tools. Cuando una tool se declara con `requires_approval=True`, la ejecución del agente termina con un objeto `DeferredToolRequests`. El usuario aprueba o niega, y la ejecución se reanuda con `DeferredToolResults` preservando el `message_history` [^482^]. La granularidad es por tool call, no por workflow completo: en una ejecución con múltiples herramientas, algunas pueden requerir aprobación y otras no [^482^]. Para decisiones condicionales —por ejemplo, aprobar solo si el monto excede un umbral—, el decorador puede elevar `ApprovalRequired` desde dentro de la función de la tool, consultando `RunContext.tool_call_approved` [^482^].

La limitación operativa no está en Pydantic AI, sino en el canal de entrega. WhatsApp Business API impone tres restricciones que condicionan severamente cualquier flujo de aprobación multi-step: máximo tres quick reply buttons por mensaje, texto máximo de 20-25 caracteres por botón, y una ventana de sesión de 24 horas desde el último mensaje del usuario [^487^][^488^]. Fuera de la sesión activa, solo se pueden enviar template messages pre-aprobados por Meta, cuyo proceso de aprobación tarda típicamente 15-30 minutos (automático) o hasta 24 horas (revisión manual) [^489^]. Si un workflow de cobranza requiere aprobación humana y el usuario no responde dentro de las 24 horas, la conversación debe reiniciarse vía template, esperar la respuesta del usuario, y solo entonces reabrir la sesión [^490^]. Esta fricción no tiene workaround técnico: es una regla de plataforma.

La combinación de estas dos realidades —approval granular en Pydantic AI, restricciones severas en WhatsApp— define el problema de diseño que Faberloom debe resolver.

### 3.2.3 10 handoffs al 99% cada uno = 90.4% confiabilidad total; costo multi-agente 2-5× tokens vs single-agent

La matemática de confiabilidad compuesta es implacable. En producción, los sistemas multi-agente observan multiplicadores de costo de 2× a 10× sobre single-agent, con un factor efectivo de 2-3× tras ajustar por reintentos [^385^]. Un workflow de análisis de documentos que consume 10,000 tokens en single-agent requiere ~35,000 tokens en una implementación de cuatro agentes (3.5×) [^385^]. En benchmarks de framework, CrewAI reporta el overhead más alto (~3-4×), LangGraph el más eficiente (~1.3-1.8×), y AutoGen se sitúa en 2-5× [^431^]. El sistema multi-agente de investigación de Anthropic consume ~15× más tokens que interacciones de chat estándar, aunque logró +90% de mejora en calidad para tareas de investigación de alto valor [^424^].

La confiabilidad compuesta se degrada exponencialmente. Si cada handoff individual tiene una confiabilidad del 99%, una cadena de diez handoffs produce una confiabilidad sistémica del 90.4%. Si la confiabilidad por paso cae al 95% —una cifra más realista para LLM calls con variabilidad de prompt—, veinte pasos producen una confiabilidad del 35.8% [^385^]. Para un MVP que debe demostrar fiabilidad a clientes PYME sin tolerancia a fallos visibles, esta degradación exponencial convierte a cada handoff en un riesgo acumulativo.

| Métrica | Single-Agent | Multi-Agente (4 agentes) | Fuente |
|---------|------------|------------------------|--------|
| Tokens por workflow (10K base) | 10,000 | 35,000 | SoftwareSeni benchmark [^385^] |
| Overhead de framework | 1.0× | 1.3-4.0× | Iternal.ai [^431^] |
| Confiabilidad 10 pasos al 99% | 99.0% | 90.4% | Cálculo compuesto [^385^] |
| Confiabilidad 20 pasos al 95% | 95.0% | 35.8% | Cálculo compuesto [^385^] |
| Tasa de fallo MAST (rango) | N/A | 41-86.7% | UC Berkeley [^338^] |
| Mejora calidad vs single-agent | Baseline | +90% (research tasks) | Anthropic [^424^] |

La tabla anterior sintetiza el dilema cuantitativo. La mejora de calidad del +90% reportada por Anthropic es real, pero condicionada a tareas de investigación de alto valor donde el costo extra se justifica. Para workflows de cobranza y proformas B2B —tareas secuenciales, con dependencias fuertes entre pasos, y bajo margen de error tolerable—, el costo-beneficio se invierte. El overhead de tokens de 2-5×, combinado con una confiabilidad compuesta que cae por debajo del 91% en diez pasos, convierte al multi-agente en una elección arriesgada para un MVP con presupuesto de ~$200/mes.

## 3.3 Confidence Level

El nivel de confianza de los hallazgos de este capítulo se clasifica como **HIGH**, basado en cuatro pilares de evidencia verificable:

1. **Literatura académica peer-reviewed**: MAST (UC Berkeley, NeurIPS 2025 Spotlight) con 1,642 trazas, 6 anotadores expertos y Cohen's Kappa = 0.88 [^338^]; paper de single-agent vs multi-agent con razonamiento multi-hop en 7 benchmarks [^336^]; paper "From Spark to Fire" modelando matemáticamente propagación de errores en 6 frameworks [^340^].

2. **Documentación oficial de frameworks**: Pydantic AI docs para delegación nativa y deferred tools [^338^][^482^]; LangGraph docs para checkpointing [^361^]; Meta WhatsApp Business API docs para límites de interacción [^487^][^488^].

3. **Datos de producción y consultoría**: Gartner press release con predicción del 40% de cancelaciones para 2027 [^392^]; análisis de costos de SoftwareSeni basado en datos de producción [^385^]; post de ingeniería de Anthropic sobre su sistema multi-agente de research [^424^].

4. **Verificación cruzada interna**: El dato controvertido "87% en 4h" fue rastreado hasta su origen compuesto (86.7% de MAST + extrapolación temporal de Cycles), confirmándose como no verificable en su forma original. Las fuentes verificables sustentan la misma decisión (NO multi-agente en MVP) con argumentación más sólida.

No se identificaron conflict zones entre las tres dimensiones de investigación (Dim 07, 08, 09). Todas convergen en: mantener single-agent en MVP, diferir skill-to-skill a Fase 6, y usar approval gates por tool (no por cadena) usando capacidades nativas de Pydantic AI.

## 3.4 Implicación de Diseño

### 3.4.1 Mantener single-agent + L1/L2 routing en MVP; diseñar approval gates por tool (no por cadena) usando Pydantic AI nativo

La arquitectura de Faberloom ya implementa un patrón de handoff punto-a-punto en todo excepto el nombre. El L1 (Haiku clasificador) actúa como router agent; el L2 (dispatcher por `task_type` + `complexity` + `cost`) actúa como conditional edge; y el `ModelFingerprint` con probation actúa como audit trail y state validation. Este diseño se alinea con el patrón supervisor-worker de LangGraph [^292^], con el estándar de customer support documentado ("orchestrator-worker is the proven standard... with autonomous resolution rates above 90%") [^396^], y con la recomendación de Watsonx Orchestrate de usar "triage_agent (Router, Not Solver)" con routing conditions determinísticas [^438^].

La implicación práctica es que Faberloom no necesita re-arquitecturar su routing. Necesita (a) mantenerlo, (b) documentarlo explícitamente como un patrón de handoff punto-a-punto, y (c) añadir gates de aprobación humano en los boundaries correctos.

El diseño de approval gates debe operar a nivel de tool, no a nivel de cadena de workflow. Cuando el agente de Faberloom ejecuta una tool de "enviar proforma al cliente" o "registrar cobro como pagado", esa tool individual debe poder declarar `requires_approval=True`. Si el monto supera un umbral configurable por tenant, la tool eleva `ApprovalRequired` con metadatos que incluyen el contexto necesario para la decisión humana [^482^]. Este diseño tiene tres ventajas sobre la aprobación por workflow completo: (1) granularidad mínima viable (solo las actions de alto impacto requieren gate), (2) reanudación simple (el `message_history` se preserva automáticamente en Pydantic AI), y (3) trazabilidad directa (cada aprobación está ligada a una tool call auditable).

El contrato de salida por tool debe incluir metadatos de validación estructurados: un objeto Pydantic que contenga `result`, `confidence` (0-1), `source_references`, `warnings`, `requires_human_review` (bool), y `validation_status` (enum: passed, passed_with_warnings, failed, needs_review) [^482^]. Esta estructura permite que el dispatcher L2 rutee a HITL basado en campos declarativos, no en parsing de texto libre.

### 3.4.2 UX dual: aprobación granular en web console, notificaciones binarias en WhatsApp con links a consola

El análisis de UX para el gate humano revela una asimetría estructural entre los dos canales de Faberloom que no puede resolverse con una solución unificada. La web console (Next.js) permite interfaces ricas: preview de proformas con diff, historial de aprobaciones, botones de acción con labels descriptivos, formularios de edición inline, y estados de progreso visual. WhatsApp Business API, por el contrario, ofrece quick reply buttons con máximo tres opciones, 20-25 caracteres por label, y una sesión de 24 horas que expira sin recuperación automática [^487^][^488^][^490^].

La estrategia de UX dual propuesta para Faberloom es:

**Canal web (primario para aprobación compleja):** El operador humano recibe una notificación en la consola con el contexto completo de la tool pendiente: preview del documento o transacción, metadata del cliente, monto, riesgo de confianza calculado, y botones de acción ricos (Aprobar, Rechazar, Editar antes de aprobar, Escalar a supervisor). La aprobación es síncrona con el backend Pydantic AI: el frontend renderiza el `DeferredToolRequests`, captura la decisión del operador, construye `DeferredToolResults`, y reanuda la ejecución del agente.

**Canal WhatsApp (primario para notificación, secundario para decisión):** El sistema envía un mensaje binario con dos quick reply buttons: "✅ Aprobar" / "❌ Ver en consola". La opción "Aprobar" solo se muestra para acciones de bajo riesgo predefinidas (ej. proforma < $500 para cliente con historial > 6 meses). La opción "Ver en consola" envía un link deep-link a la web console donde el operador toma la decisión con contexto completo. Si la sesión de 24h expira, el sistema envía un template message de reinicio con un solo CTA: "🔗 Revisar pendientes en consola".

Esta asimetría no es una limitación del diseño; es una respuesta a las restricciones de plataforma. Diseñar aprobación granular directamente en WhatsApp —por ejemplo, un workflow de cobranza que requiera "¿aprobar extracción de monto? → ¿aprobar clasificación? → ¿aprobar acción?"— necesitaría tres mensajes separados, cada uno con sus propios 3 botones, y cada uno sujeto a la ventana de 24h. En la consola web, es una sola pantalla. El principio de diseño derivado es: cualquier interacción multi-step va a la consola; WhatsApp solo dispara links a la consola o recibe decisiones binarias de bajo riesgo.

## 3.5 Decisión Recomendada

### 3.5.1 ⏳ DIFERIR a Fase 6 (condición: >3 tools con dependencias complejas o requerimiento de paralelismo); NO envolver en LangGraph para MVP

La decisión para Faberloom es **diferir** la implementación de skill-to-skill delegation y spawning controlado a Fase 6, manteniendo arquitectura single-agent con L1/L2 routing durante el MVP y la fase inmediata posterior.

**Condiciones de activación para reconsiderar en Fase 6:**

- Un workflow requiere más de tres herramientas con lógica de dependencia compleja (ej.: tool B solo si tool A retorna condición X, con ramificación condicional no manejable por dispatch simple).
- Emergen requerimientos de ejecución paralela de skills (ej.: buscar datos de cliente + generar draft de proforma simultáneamente, donde el beneficio de paralelismo supere el overhead de coordinación).
- Existe un requerimiento explícito de aislamiento de contexto entre dominios (ej.: skill de cobranza no debe tener visibilidad de datos de proformas por razones de compliance o confidencialidad).
- El valor del workflow multi-agente excede 10× el costo de tokens extra, validado por métricas de negocio (ej.: reducción de tiempo de resolución de cobranza > 50%).

**Recomendaciones técnicas para la transición a Fase 6:**

Si las condiciones de activación se cumplen, la ruta técnica recomendada no es envolver Pydantic AI en LangGraph —eso añade dos frameworks, curva de aprendizaje alta, y más infraestructura— sino evaluar dos opciones escalonadas:

1. **Opción ligera (Fase 6 temprana):** Usar `subagents-pydantic-ai` (paquete de terceros mantenido por Vstorm) que añade `SubAgentCapability` con modos sync/async/auto sobre el runtime existente de Pydantic AI [^485^]. No requiere cambiar el framework base ni migrar código. La delegación se implementa como tools adicionales del agente padre, preservando type safety y ModelFingerprint.

2. **Opción completa (Fase 6 avanzada):** Evaluar LangGraph como orquestador de workflows, manteniendo Pydantic AI para la lógica individual de cada agente (pattern "Pydantic AI para agente, LangGraph para workflow" que ganó tracción en círculos de ingeniería de producción en 2026) [^484^]. LangGraph ofrece checkpointing nativo en PostgreSQL [^361^], custom edges para routing condicional, subgraphs con TypedDict privado para aislamiento de estado [^292^], y time-travel debugging. Sin embargo, requiere inversión en infraestructura (tablas de checkpoint, configuración de `PostgresSaver`) que excede el presupuesto y el equipo de 1-3 desarrolladores del MVP.

**Frameworks y patrones a descartar explícitamente:**

- **OpenAI Swarm:** Deprecado en marzo 2025, explícitamente marcado como "experimental, educational". OpenAI recomienda migrar al Agents SDK para todos los casos de producción [^409^].
- **CrewAI:** Abstracción demasiado alta; no permite control explícito de ModelFingerprint ni probation. Los handoffs son implícitos vía runtime, no punto-a-punto controlados [^318^].
- **AutoGen Group Chat:** Riesgo de context contamination; topología mesh con propagación rápida de errores (segundo más rápido en el benchmark "From Spark to Fire") [^298^][^340^].

**Resumen de decisión por componente:**

| Componente | Decisión MVP | Fase de upgrade | Condición de activación |
|------------|-------------|-----------------|------------------------|
| Single-agent Pydantic AI | ✅ MANTENER | Baseline permanente | Ninguna |
| Skill-to-skill delegation | ⏳ DIFERIR | Fase 6 | >3 tools con dependencias complejas |
| pydantic-graph | ❌ NO usar | N/A | Overkill para 2-3 pasos |
| LangGraph wrapper | ❌ NO envolver | Fase 6+ (evaluar) | Workflows con múltiples HITL points |
| Human approval por tool | ✅ IMPLEMENTAR | MVP (parcial) | Tools de alto impacto: envío proforma, registro de cobro |
| Approval en WhatsApp | ✅ Binaria (Sí/Ver consola) | MVP | Solo acciones de bajo riesgo predefinidas |
| Approval en web console | ✅ Granular con preview | MVP | Todas las acciones que requieran HITL |

La matriz de decisión confirma que la inversión de diseño del MVP debe concentrarse en dos frentes: (1) fortalecer el single-agent existente con output validators, circuit breakers por skill, y gates de aprobación nativos de Pydantic AI; y (2) diseñar la UX dual web/WhatsApp que canalice la interacción multi-step hacia la consola y preserve WhatsApp para notificaciones binarias. El spawning controlado de sub-skills es técnicamente alcanzable hoy, pero arquitectónicamente innecesario hasta que la complejidad del workload lo justifique con datos de producción.
## 4. GAP 4 — pgvector + RLS a Escala: ¿Aguanta 100+ Tenants?

### 4.1 Hallazgo

#### 4.1.1 El Tipping Point Económico, No Técnico

La pregunta que encabeza este gap — ¿aguanta pgvector con Row-Level Security (RLS) a cien tenants? — está mal formulada. La investigación técnica demuestra que pgvector + RLS resiste la carga de latencia con márgenes holgados hasta al menos un millón de vectores. El bottleneck real no es el motor de búsqueda aproximada, sino el precio del compute en Supabase. En otras palabras: el tipping point es económico, no técnico.

Benchmarks empíricos sobre Docker con 10 k registros muestran que una búsqueda HNSW (Hierarchical Navigable Small World) sin RLS tarda 3–5 ms en percentil 50 (p50); con políticas RLS activas, la latencia sube a 5–6 ms, un overhead del orden del 20% [^4^]. En queries que combinan JOIN a tablas de tenants, el incremento es apenas 0.1 ms (1.25 ms → 1.35 ms) cuando existen índices compuestos con `tenant_id` como leading column [^4^]. Bajo 500 conexiones concurrentes y con composite indexes correctos, la degradación de RLS es "no measurable" en comparación con filtrado a nivel de aplicación [^549^].

A escala de 1 M vectores de 1536 dimensiones, pgvector HNSW reporta p50 ~5 ms y p95 ~12 ms con QPS superiores a 800 y recall@10 de 0.95 [^541^]. Discourse opera pgvector en "thousands of databases" atendiendo "billions of page views", usando halfvec (float16) y bit quantization para reducir storage [^504^]. Ring almacena 100–200 mil millones de embeddings en Amazon RDS for PostgreSQL con pgvector, alcanzando p50 ~200 ms y p95-p99 ~600 ms [^537^]. Si billion-scale es viable, el rango de Faberloom — cientos de miles a pocos millones de vectores — no presenta restricción técnica de latencia.

El problema emerge en el costo de la instancia necesaria para mantener el índice HNSW en memoria. Supabase Pro ($25/mes base) incluye un compute Micro con 1 GB RAM que solo admite ~15 000 vectores HNSW de 1536 dimensiones [^654^]. El siguiente escalón, Large (8 GB RAM), soporta ~224 482 vectores [^654^]. Con halfvec quantization, que reduce el tamaño del vector a la mitad, la capacidad de Large se duplica a ~450 000 vectores [^694^]. Para llegar a 1 M vectores se requiere 2XL (32 GB RAM), que cuesta $410/mes en compute add-on, sumando $435/mes con la base Pro [^607^] [^654^]. Eso supera el presupuesto infraestructural de Faberloom (~$200/mes) en un factor de 2.2×.

La pregunta correcta, entonces, no es si pgvector aguanta, sino cuántos vectores caben dentro del presupuesto. La respuesta, con halfvec en Supabase Pro + Large ($135/mes), es ~450 000 vectores. Ese es el punto de ruptura económico.

#### 4.1.2 Alternativas Técnicamente Superiores, Económicamente Prematuras

El mercado de vector databases dedicadas ofrece alternativas técnicamente más sofisticadas. Qdrant v1.16 (noviembre 2025) introduce Tiered Multitenancy: tenants pequeños comparten un shard fallback; tenants grandes se promueven a shards dedicados sin downtime [^575^] [^577^]. Weaviate posee la arquitectura de multi-tenancy más madura del sector: un shard por tenant, Tenant Controller con estados ACTIVE/INACTIVE/OFFLOADED, y lazy loading que soporta millones de tenants por cluster [^578^]. pgvectorscale, extensión de TimescaleDB, añade StreamingDiskANN y Statistical Binary Quantization, logrando 471 QPS contra 41 QPS de Qdrant en 50 M vectores a 99% recall [^573^] [^566^].

Ninguna de estas ventajas justifica una migración en el MVP de 60 días. El equipo de Faberloom consta de 1–3 desarrolladores sin operaciones dedicadas. Self-hosting Qdrant en un Droplet de DigitalOcean de 16 GB cuesta $96/mes, pero requiere configuración Docker y monitoreo que, a $150/hora de ingeniería, implica un costo oculto de $600–900/mes en tiempo operativo [^473^] [^701^]. Weaviate Cloud Flex arranca en $45/mes de mínimo [^586^], elevando el gasto vectorial ~80% sin beneficio perceptible a 1 M vectores. pgvectorscale no está disponible como extensión pre-instalada en Supabase Cloud al menos hasta julio 2025 [^658^] [^626^], quedando fuera del stack sin migrar de plataforma.

La ventaja comparativa de las alternativas se materializa más allá del millón de vectores o en escenarios de compliance estricto. En el rango MVP, el trade-off es inequívoco: pgvector en Supabase ofrece zero costo de integración, atomicidad transaccional, y RLS nativo que ninguna vector DB dedicada replica [^625^].

#### 4.1.3 Mem0: Capa de Memoria, No Reemplazo de Vector DB

Mem0 aparece ocasionalmente en conversaciones de stack como alternativa a pgvector. La investigación lo descarta categóricamente como reemplazo. Mem0 es un framework de memoria AI (memory layer) que orquesta operaciones CRUD sobre un vector store externo configurado: Qdrant, Chroma, Pinecone, pgvector, Weaviate o FAISS [^583^] [^563^]. En desarrollo usa SQLite; en producción requiere explícitamente un vector DB subyacente [^583^]. Mem0 Platform (managed) cobra $99–299/mes por gestión de memorias, pero no almacena vectores por sí mismo [^598^]. Para Faberloom, Mem0 solo tiene sentido si se añade un feature de "memoria contextual persistente por usuario" que no es parte del MVP. Descartar como reemplazo de pgvector.

### 4.2 Datos y Evidencia

#### 4.2.1 Overhead de RLS en Operaciones Vectoriales

Los datos de overhead provienen de benchmarks controlados en Docker con 10 k registros y de producciones reportadas públicamente.

| Operación | Sin RLS | Con RLS | Overhead | Contexto |
|:---|:---|:---|:---|:---|
| Simple SELECT | — | — | +0.1 ms | `SET LOCAL` por transacción [^4^] |
| JOIN (Docs + Tenants) | 1.25 ms | 1.35 ms | +0.1 ms | Planner optimiza con composite index [^4^] |
| Vector Search HNSW | 3–5 ms | 5–6 ms | ~20% | Aceptable vs schema-per-tenant overhead [^4^] |
| GROUP BY con RLS | — | — | ~2.4× | Mayor impacto en agregaciones complejas [^4^] |
| 500 conexiones concurrentes | — | — | No measurable | Con composite indexes `(tenant_id, ...)` [^549^] |

La tabla confirma que el único escenario donde RLS introduce fricción material es en agregaciones GROUP BY, que duplican latencia. Para Faberloom, donde el patrón dominante es "top-k similares + filtro por tenant_id", el impacto es marginal. El pilar de mitigación es el índice compuesto: benchmarks a 50 M filas y 10 k tenants muestran que sin `tenant_id` como leading column, RLS es dos órdenes de magnitud más lento [^549^]. La recomendación es indexar `(tenant_id, status)` y `(tenant_id, created_at)` además del HNSW sobre el embedding [^505^].

Una tensión técnica documentada por Bytebase es que RLS opera como post-processing filter, lo que puede impedir que el query planner use índices óptimos en joins complejos [^540^]. La contramedida no es abandonar RLS, sino diseñar queries que favorezcan el push-down de predicados o, en casos extremos, usar views con security predicates que el planner resuelve durante la fase de planificación [^540^]. Para el MVP de Faberloom, con queries simples de búsqueda vectorial por tenant, esta tensión no se manifiesta.

#### 4.2.2 Costos de Supabase por Tier de Compute

Supabase estructura su precio en base Pro ($25/mes) más add-ons de compute escalonados. La capacidad de vectores por tier está determinada por la RAM disponible para el índice HNSW, que debe residir principalmente en memoria.

| Tier | RAM | Costo/mes | Vectores HNSW (1536-dim) | Vectores con halfvec | Viable para Faberloom |
|:---|:---|:---|:---|:---|:---|
| Free | 1 GB (Micro) | $0 | ~15 000 | ~30 000 | No: `maintenance_work_mem` cappeado a 32 MB [^690^] |
| Pro base | 1 GB (Micro) | $25 | ~15 000 | ~30 000 | Insuficiente para MVP real |
| Pro + Large | 8 GB | $135 | ~224 000 | ~450 000 | ✅ Dentro de presupuesto |
| Pro + XL | 16 GB | $235 | ~500 000 | ~1 000 000 | ⚠️ Excede $200 en 18% |
| Pro + 2XL | 32 GB | $435 | ~1 000 000 | ~2 000 000 | ❌ Excede $200 en 118% |

Free Tier es un callejón sin salida para pgvector a escala: además del límite de 500 MB de storage, el parámetro `maintenance_work_mem` está cappeado a 32 MB, lo que provoca fallos en la creación de índices IVFFlat/HNSW en datasets de ~18 k vectores de 1536 dimensiones [^690^]. El upgrade a Pro es obligatorio tan pronto como se requiera indexación HNSW viable.

Con halfvec quantization, que reduce storage ~50% con <1% pérdida de recall en embeddings normalizados [^694^], el punto de ruptura del presupuesto se desplaza de ~224 k a ~450 k vectores en el tier Large ($135/mes). Ese rango representa aproximadamente 25–90 tenants activos de PYME B2B LATAM, asumiendo 1 000–18 000 vectores por tenant [^594^] [^631^]. Para Faberloom, que apunta a 8 semanas de MVP con ~50 tenants iniciales, la capacidad está holgada.

#### 4.2.3 Comparativa de Costos: 1 M Vectores / 100 Tenants

Escalar a 100 tenants con ~10 000 vectores cada uno (1 M total) requiere evaluar alternativas.

| Opción | Costo Mensual Estimado | Capacidad 1 M vectores | Multi-tenancy | Notas |
|:---|:---|:---|:---|:---|
| Supabase Pro + pgvector (XL, halfvec) | $235 | ~1 M | RLS nativo [^585^] | Excede presupuesto MVP 18% |
| Supabase Pro + pgvector (2XL) | $435 | ~2 M | RLS nativo | Excede presupuesto 118% |
| Qdrant Cloud Standard 8 GB | $120–200 | 1 M sin compresión, 2 M+ con SQ [^697^] | Tiered Multitenancy [^575^] | Sin RLS SQL; payload filtering |
| Qdrant Cloud 2 GB + Binary Quantization | $30–60 | 8 M+ con BQ [^697^] | Payload filtering | Opción más económica a 1 M |
| Weaviate Cloud Flex | $45–65 | 1 M (RF=2) [^623^] | Shard-per-tenant nativo [^578^] | Mínimo $45; BQ reduce a floor |
| Turbopuffer | $64 | Sin límite práctico [^581^] | Namespaces ilimitados | Mínimo $64; usado por Cursor, Notion |
| Mem0 Platform | $99–299 | Depende de backend | user_id scoping | NO es vector DB [^583^] |
| Qdrant self-hosted (DO 16 GB) | $96 | 10 M+ con BQ [^697^] | Payload filtering | Requiere DevOps; costo oculto $600–900/mes [^701^] |

La interpretación de la tabla revela una jerarquía de decisiones. Supabase pgvector es la opción más barata hasta ~450 k vectores ($135/mes). Entre 450 k y 1 M, Qdrant Cloud 2 GB con Binary Quantization ($30–60/mes) o Weaviate Flex ($45–65/mes) son económicamente competitivas. Turbopuffer ($64/mes mínimo) solo gana a escala de query volume muy alta, porque no cobra por read unit [^581^] [^574^].

Una distinción crítica es que ninguna vector DB dedicada ofrece RLS nativa equivalente a PostgreSQL. Qdrant usa payload filtering con `tenant_id` en metadata; Weaviate usa shard-per-tenant [^585^] [^578^]. La reimplementación de las políticas de seguridad en la capa de aplicación añade riesgo operativo que debe ponderarse contra el ahorro en hosting [^625^].

### 4.3 Confidence Level

**HIGH** para benchmarks técnicos de latencia, throughput y overhead de RLS. Los datos provienen de múltiples fuentes convergentes: benchmarks en Docker [^4^], benchmarks de AWS Aurora [^536^], producciones de Discourse [^504^] y Ring [^537^], y ANN-Benchmarks estándar de la industria [^687^]. La consistencia cross-source es robusta.

**MEDIUM** para proyecciones de costos a 100 tenants. La estimación de 1 000–18 000 vectores por tenant PYME B2B LATAM es una heurística basada en catálogos de 50–500 SKUs [^594^], knowledge bases de 20–100 artículos [^631^], y documentos comerciales históricos. El crecimiento real de tenants solo el mercado lo validará. Los precios de Supabase y Qdrant Cloud son públicos [^607^] [^697^], pero pueden fluctuar.

### 4.4 Implicación de Diseño

#### 4.4.1 Implementar pgvector en Supabase para MVP

La decisión arquitectónica inmediata es consolidar pgvector en Supabase Pro con configuración defensiva: HNSW como índice por defecto (justificado para <50 M vectores, mejor recall incremental, y manejo de inserts continuos sin rebuild) [^469^]; halfvec quantization desde el día uno para doblar capacidad con pérdida mínima de recall [^694^]; RLS como safety net con `tenant_id = current_setting('app.current_tenant')::uuid` [^4^]; e índices compuestos `(tenant_id, status)` y `(tenant_id, created_at)` con `tenant_id` como leading column [^549^].

El esquema debe incluir `tenant_id` como columna adicional aunque RLS ya aísle datos. Esta redundancia defensiva permite que queries con `EXPLAIN ANALYZE` verifiquen que el planner usa el índice compuesto, y actúa como segunda barrera si una política RLS se desactiva accidentalmente [^4^].

#### 4.4.2 Habilitar `hnsw.iterative_scan = relaxed_order`

pgvector 0.8.0 introduce iterative index scans para HNSW e IVFFlat, con dos modos: `strict_order` (garantiza orden exacto por distancia) y `relaxed_order` (permite ligera desviación en orden a cambio de mejor recall) [^501^]. Para Faberloom, donde los workflows filtrarán por `tenant_id` y metadata (estado de documento, rango de fecha), el riesgo de overfiltering — retornar 0 resultados porque el índice HNSW con `ef_search=40` escanea solo 40 nodos y el filtro RLS descarta la mayoría [^506^] — es real. Supabase documenta este escenario y recomienda iterative scan [^639^].

La activación requiere confirmar que la instancia ejecuta pgvector 0.8.0+, disponible tras upgrade de Postgres [^500^]. El parámetro `hnsw.max_scan_tuples` debe ajustarse empíricamente; un punto de partida razonable es 10× el `LIMIT` de la query.

#### 4.4.3 Diseñar Schema con tenant_id como Safety Adicional

El diseño de esquema debe asumir que RLS es el mecanismo de aislamiento principal, pero no el único. La columna `tenant_id` cumple tres funciones: (a) permite composite indexes que el planner necesita para optimizar RLS [^549^]; (b) habilita verificaciones de consistencia periódicas; (c) preserva portabilidad si se migra a un sistema que no soporta RLS nativa [^625^].

Schema-per-tenant debe descartarse explícitamente: EDBT 2026 demuestra que el modelo schema-per-tenant satura el sistema con un solo tenant en workloads TPC-C, y la contención interna lo hace inoperable más allá de ~100 tenants [^10^]. Shared-schema + RLS es el patrón validado por PlanetScale [^657^] y por producciones como Discourse [^504^].

### 4.5 Decisión Recomendada

#### 4.5.1 ✅ IMPLEMENTAR (Stay con pgvector) para MVP; DIFERIR Evaluación de Alternativas a >500 K Vectores o 6 Meses

**Implementar:** pgvector en Supabase Pro + Large ($135/mes) con HNSW, halfvec, RLS nativa, composite indexes, y `iterative_scan = relaxed_order`. Construir una capa de abstracción `VectorStore` desde el día uno para limitar la superficie de futura migración a 50–200 líneas [^473^].

**Diferir:** Evaluación sistemática de Qdrant Cloud, Weaviate Flex, o Turbopuffer hasta que la proyección de vectores supere 500 000 o el timeline llegue a 6 meses post-MVP. Los triggers de reevaluación son: (1) count de vectores >400 k, con benchmark ANN-Benchmarks validando p95 < 100 ms y recall@10 > 0.90 [^687^]; (2) latencia p95 > 100 ms persistente que no mejore con tuning de `ef_search`; (3) nuevos requisitos de compliance que exijan aislamiento físico por tenant.

**Costo oculto de migración anticipada:** Migrar datos de pgvector a Qdrant es técnicamente trivial (1–3 días managed, herramienta oficial `qdrant-migration` [^624^]), pero la reimplementación de RLS en la capa de aplicación y la sincronización dual-documento/vector introducen deuda técnica [^625^]. pgvector preserva atomicidad transaccional: un `INSERT` escribe fila y embedding en la misma tabla; un `DELETE` elimina ambos en la misma transacción [^625^]. Qdrant obliga a "write to both, delete from both", con riesgo de vectores huérfanos si un write falla [^625^].

**Proyección de Costos — Escenario Base Faberloom:**

| Mes | Tenants Activos | Vectores Totales (est.) | Configuración Supabase | Costo Vectorial/mes | Acción |
|:---|:---|:---|:---|:---|:---|
| 0–2 | 5–15 | 10 k–50 k | Pro base ($25) | ~$25 | Crear capa `VectorStore`; halfvec default |
| 3–4 | 20–40 | 100 k–250 k | Pro + Large ($135) | ~$135 | Benchmark ANN; validar p95 < 50 ms |
| 5–6 | 50–80 | 300 k–500 k | Pro + Large ($135) o XL ($235) | $135–235 | **Decisión go/no-go migración** |
| 7–12 | 100+ | 500 k–1 M | XL ($235) o 2XL ($435) | $235–435 | Si >$200/mes sostenido, migrar a Qdrant Cloud 2 GB+BQ ($30–60) |

La proyección asume 1 000–18 000 vectores por tenant PYME B2B LATAM, con crecimiento lineal en tenants durante los primeros 12 meses. El costo marginal de pgvector en Supabase se mantiene plano ($135) hasta ~450 k vectores, momento en que el salto a XL ($235) o 2XL ($435) desplaza la curva de costo hacia arriba. En ese punto, Qdrant Cloud con Binary Quantization ofrece una ruta de escape económica: 8 M+ vectores en un cluster 2 GB a $30–60/mes [^697^], un 75–86% de ahorro versus Supabase 2XL.

El riesgo de lock-in es bajo para los datos (pg_dump/COPY exporta vectores como tipos PostgreSQL estándar [^633^]) pero alto para la semántica de seguridad: las RLS policies no tienen equivalente directo en ninguna vector DB dedicada [^585^]. Mitigar desde el inicio con la capa `VectorStore` y con `tenant_id` explícito en schema reduce el costo de migración semántica.
## 5. Insights Transversales

### 5.1 Patrón Arquitectónico Universal

#### 5.1.1 Los cuatro gaps convergen en un mismo patrón: "Deterministic First → LLM Fallback → Human Gate"

La investigación de los cuatro gaps arquitectónicos revela una regularidad que trasciende cada dominio particular. Tres de los cuatro gaps — y en cierto sentido el cuarto — implementan secuencialmente la misma lógica de defensa en profundidad: resolver primero con la capa determinística más barata y rápida, escalar a la capa inteligente solo cuando la determinística reporta insuficiencia, y delegar a un operador humano cuando la capa inteligente genera incertidumbre o impacto financiero significativo. Este patrón no es una simplificación impuesta por el presupuesto del MVP; es la estrategia de producción que Faberloom ya utiliza implícitamente y que los sistemas de referencia — Ruflo, RouteLLM, Reflex Fabric — documentan explícitamente.

En el GAP 1, el Tier 0 de regex/stdlib `re` intercepta ~60–80% de requests antes de que alcancen Haiku [^119^][^84^]. La latencia de un pattern compilado es ~5–50 μs, contra ~750–1,100 ms de Haiku desde LATAM [^1^][^2^]. La ratio de 20,000–220,000× no es marginal; es la diferencia entre una respuesta sub-milisegundo y una respuesta perceptible al usuario. Cuando regex devuelve `None` o Pydantic eleva `ValidationError`, el sistema no falla silenciosamente; dispara el fallback LLM, que añade robustez semántica al costo de latencia y tokens [^131^][^210^]. Este es el primer eslabón del patrón.

En el GAP 2, el routing L1/L2 rule-based actúa como la capa determinística antes del bandit contextual. El L1 clasifica intención mediante Haiku; el L2 enruta por `task_type` + `complexity` + `cost` con overhead de solo 2–8 ms [^303^]. El bandit adaptive — LinUCB, Thompson Sampling o ε-greedy — es el "LLM fallback" del routing: se activa solo cuando el volumen supera ~3,000 requests/día y el sistema dispone de datos suficientes para que los estimadores estabilicen [^383^][^321^]. Hoy, con ~100–300 requests/día, el routing rule-based es la capa determinística óptima. El gate humano aparece en forma de feedback pasivo: la tabla `outcome_ledger` acumula observaciones que un operador puede auditar antes de que el bandit las consuma como reward [^296^].

En el GAP 3, el single-agent con L1/L2 routing es la capa determinística antes del multi-agente. La evidencia académica verificable — MAST (41–86.7% tasa de fallo en 1,642 trazas) [^338^] y el paper de NeurIPS 2025 sobre single-agent vs multi-agente [^336^] — confirma que la arquitectura actual de Faberloom ya está en el rango de menor riesgo. El spawning controlado de sub-skills es el "LLM fallback" que se activa solo cuando un workflow requiere >3 tools con dependencias complejas o paralelismo justificable, condición que se proyecta para Fase 6, no para el MVP [^338^][^484^]. El gate humano está materializado en Pydantic AI mediante `requires_approval=True` por tool call, no por workflow completo [^482^].

El GAP 4, aunque no encaja directamente en la secuencia de procesamiento de requests, obedece a la misma lógica de "empezar simple, escalar inteligente". pgvector con HNSW es la solución determinística — probada, sin curva de aprendizaje, con RLS nativa. Las alternativas (Qdrant, Weaviate, pgvectorscale) son técnica y económicamente superiores solo más allá del millón de vectores, donde el tipping point económico de Supabase ($135/mes → $435/mes) las hace competitivas [^654^][^607^]. La decisión de "stay" con pgvector es, en este contexto, la elección de la capa determinística correcta para el rango operativo actual.

La pirámide de confiabilidad resultante tiene tres pisos. En la base, el código determinístico (regex, rule-based routing, single-agent, pgvector) resuelve ~80–95% de casos con latencia sub-milisegundo y costo marginal de $0. En el piso intermedio, el LLM (Haiku, Sonnet, futuro bandit, futuro multi-agente) cubre el 5–20% residual con costo y latencia controlados. En la cúspide, el operador humano valida acciones de alto impacto mediante aprobación granular en la consola web [^482^]. Sistemas de producción que omiten la base determinística — los "LLM-first" puros — reportan tasas de fallo 2–5× mayores y costos de tokens multiplicados por factores de 2–10× [^385^][^424^]. El patrón no limita al MVP; lo fortalece.

### 5.2 LiteLLM como Hilo Conector

#### 5.2.1 LiteLLM conecta tres gaps: pre-call hooks (Tier 0), Organizations/Teams/Keys (multi-tenant routing), embeddings abstraction (vector DB migration)

La elección de LiteLLM en el stack original de Faberloom fue catalogada inicialmente como "proxy de APIs de LLM". La investigación transversal revela que esta decisión fue, de hecho, una inversión arquitectónica de mayor alcance: LiteLLM actúa como capa de abstracción multi-propósito que conecta tres de los cuatro gaps sin requerir cambios de infraestructura adicionales.

En el GAP 1, LiteLLM provee *pre-call hooks* que permiten ejecutar código Python antes de enviar el request al proveedor de LLM [^183^]. Esto habilita la implementación de Tier 0 sin middleware adicional: un hook registrado en `litellm_proxy.yaml` ejecuta regex sobre el input, valida con Pydantic, y retorna la respuesta estructurada directamente si la confianza es suficiente. Si falla, el hook pasa el control al LLM subyacente. La integración consume menos de 0.5 días de trabajo y no modifica el agente Pydantic AI [^183^].

En el GAP 2, LiteLLM implementa multi-tenancy nativa mediante la jerarquía Organizations → Teams → Users → API Keys [^296^]. Cada tenant de Faberloom se mapea a una `Organization` en LiteLLM, con presupuestos independientes, *model pools* restringidos, y atribución de costos granular. El routing L1/L2 rule-based de Faberloom opera sobre esta base: el L1 clasifica la intención, el L2 consulta la configuración del tenant en LiteLLM (qué modelos tiene habilitados, cuál es su presupuesto restante), y enruta al deployment correspondiente. Ningún router comercial evaluado — RouteLLM, Martian, NotDiamond — ofrece aislamiento por organización con esta granularidad [^316^][^307^][^302^]. LiteLLM lo provee sin costo adicional.

En el GAP 4, LiteLLM ofrece un endpoint unificado de *embeddings* que abstrae el proveedor de vector DB subyacente. Si Faberloom migra de pgvector a Qdrant o Weaviate en Fase 6, la interfaz de generación de embeddings no cambia: LiteLLM sigue exponiendo `POST /embeddings` con los mismos parámetros (`model`, `input`, `dimensions`) y los mismos headers de autenticación por tenant [^310^]. La capa de abstracción `VectorStore` que Faberloom debe construir desde el día uno (50–200 líneas de código) [^473^] se beneficia de esta estabilidad de interfaz: el cambio de vector DB afecta solo la implementación del store, no la generación de embeddings ni el routing multi-tenant.

La implicación de diseño es documentar explícitamente en la arquitectura de Faberloom que LiteLLM no es un "proxy de modelos", sino una "capa de orquestación multi-propósito". Esta distinción justifica su presencia en el stack más allá del routing de APIs y justifica la inversión en configuración detallada de Organizations/Teams/Keys desde el MVP.

### 5.3 E-invoicing LATAM como Ventaja Competitiva

#### 5.3.1 Más del 90% de PYMEs LATAM usan XML estructurado por mandato fiscal: parsers por país son core competency, no afterthought

La investigación del GAP 1 descubrió una asimetría competitiva que el equipo de Faberloom no había cuantificado: el mercado objetivo opera bajo regímenes de facturación electrónica con cobertura superior al 90% en las principales economías latinoamericanas. Brasil, Chile, México, Colombia y Argentina emiten la mayoría de sus transacciones B2B en XML con schemas publicados y obligatorios: NFe en Brasil [^95^], DTE en Chile (97% desde 2019) [^45^], CFDI 4.0 en México [^81^], UBL 2.1 en Colombia [^45^], y WS de AFIP en Argentina [^46^]. Para un SaaS de cobranza, esto significa que la entrada principal de datos — la factura — ya llega en formato parseable sin inteligencia artificial.

Un competidor genérico que procese todo mediante LLM incurrirá en latencia de ~1 segundo por factura y costo de $0.00012–0.00038 por request [^4^]. Faberloom, con parsers XML específicos por país, procesa la misma factura en <1 ms con costo $0 y accuracy del 100% cuando el XML es válido. La ventaja no es técnica sino estructural: el mercado LATAM ha hecho el trabajo de estandarización que en EE.UU. o Europa aún depende de OCR e interpretación semántica.

Los parsers por país deben construirse como *core competency*, no como *afterthought* post-MVP. La lista de 14 reglas identificadas para el MVP [^119^] incluye cinco parsers XML (DIAN, SII, SAT, AFIP, NFe) que cubren ~60–70% del volumen de documentos oficiales. La inversión es modesta — cada parser requiere 20–40 líneas de `xml.etree.ElementTree` con XPath conocidos — pero el retorno es desproporcionado: eliminación de dependencia de API externa para la mayoría de los documentos, latencia sub-milisegundo, y precisión estructural garantizada por validación contra schema XSD publicado por la autoridad fiscal.

El riesgo operativo de regex — fallo silencioso ante XML malformado o namespaces inesperados — se mitiga con Pydantic validation post-parseo. Si el parser no encuentra `cbc:PayableAmount` o el namespace cambia, el sistema eleva `ValidationError` y dispara fallback al LLM, preservando el patrón "Deterministic First → LLM Fallback" [^210^].

### 5.4 UX Dual Web/WhatsApp

#### 5.4.1 WhatsApp Business API es cuello de botella para todo multi-step: web console para aprobación granular, WhatsApp para notificaciones binarias

La investigación del GAP 3 estableció que WhatsApp Business API no es un canal de aprobación viable para workflows multi-step. Las restricciones son innegociables: máximo tres quick reply buttons por mensaje, 20–25 caracteres por label, y ventana de sesión de 24 horas desde el último mensaje del usuario [^487^][^488^]. Fuera de sesión activa, solo template messages pre-aprobados por Meta son enviables, con latencia de aprobación de 15 minutos a 24 horas [^489^]. Un workflow de cobranza que requiera aprobación secuencial de "extracción de monto → clasificación → acción de envío" necesitaría tres mensajes de WhatsApp separados, cada uno con sus propios límites de botones, y cada uno sujeto a la ventana de 24h. Si el operador no responde en tiempo, la conversación se rompe irreparablemente y debe reiniciarse vía template [^490^].

Esta limitación no es un defecto de implementación de Faberloom; es una restricción de plataforma que condiciona el diseño de toda interacción human-in-the-loop (HITL). La consola web — Next.js con interfaz rica — permite preview de documentos, diff de proformas, botones descriptivos, formularios inline, y estados de progreso visual. Pydantic AI implementa approval nativo por tool mediante `requires_approval=True` y `DeferredToolRequests`, con preservación automática de `message_history` [^482^]. La consola web consume este API directamente: renderiza el request pendiente, captura la decisión del operador, construye `DeferredToolResults`, y reanuda la ejecución del agente.

La estrategia de UX dual es asimétrica por diseño. El canal web es primario para toda aprobación granular o multi-step. El canal WhatsApp es primario para notificaciones binarias de bajo riesgo — "¿Confirmar envío de proforma a cliente habitual por monto < $500?" — con dos quick reply buttons: "✅ Aprobar" y "🔗 Ver en consola". La segunda opción envía un deep-link a la consola donde el operador toma la decisión con contexto completo. Si la sesión de 24h expira, el sistema envía un template message con un solo CTA: "Revisar pendientes en consola".

Este diseño no es una degradación de la experiencia; es una alineación de canal con capacidad. Diseñar aprobación granular directamente en WhatsApp — intentar replicar la consola web dentro de los límites de Meta — generaría frustración operativa y errores de aprobación por falta de contexto. El principio derivado es universal: cualquier interacción que requiera más de una decisión consecutiva o más de 20 caracteres de explicación se canaliza a la consola web; WhatsApp se reserva para notificaciones, alertas, y decisiones binarias predefinidas de bajo riesgo.

### Tabla de Síntesis Transversal

| GAP | Decisión | Fase | Patrón Transversal | Conexión LiteLLM | Riesgo Principal |
|:---|:---|:---|:---|:---|:---|
| GAP 1 — Tier 0 sub-LLM | ✅ Implementar | MVP (día 1–3) | **Deterministic First**: regex → LLM fallback | Pre-call hooks ejecutan Tier 0 antes del proxy [^183^] | Fallo silencioso sin Pydantic validation [^186^] |
| GAP 2 — Routing aprendido | ⏳ Diferir adaptive | Phase 2 (>3,000 req/día) | **LLM Fallback**: rule-based L1/L2 → bandit | Organizations/Teams/Keys para aislamiento por tenant [^296^] | Cold start; datos sparse per-org en MVP [^1^][^383^] |
| GAP 3 — Spawning controlado | ⏳ Diferir multi-agente | Fase 6 | **Human Gate**: approval por tool en web console | N/A directa; UX dual canaliza HITL a consola [^482^] | WhatsApp API limita multi-step a 3 botones/24h [^487^][^488^] |
| GAP 4 — pgvector + RLS | ✅ Stay pgvector | MVP | **Deterministic First**: pgvector hasta tipping point económico | Embeddings endpoint abstrae provider; migra sin cambios [^310^] | Lock-in semántico en RLS policies [^625^] |

La tabla sintetiza cuatro decisiones que, examinadas aisladamente, parecen independientes. En conjunto, revelan una postura arquitectónica coherente: Faberloom optimiza por simplicidad operativa en el MVP, diferencia complejidad inteligente hasta que el volumen y la complejidad del workload la justifiquen con datos, y preserva la capacidad de migración mediante abstracciones delgadas. LiteLLM aparece como hilo conector en tres de los cuatro gaps, lo que refuerza la decisión original de incluirlo en el stack: no es overhead, es infraestructura compartida.

El patrón "Deterministic First → LLM Fallback → Human Gate" no es una restricción del presupuesto de ~$200/mes; es la estrategia que Ruflo, RouteLLM, Reflex Fabric, y los sistemas de producción enterprise documentan como estándar de la industria. La diferencia entre Faberloom y un competidor que implemente LLM puro para todo no será perceptible en un demo de 30 segundos, pero se manifestará en la factura de tokens, en la latencia p95 de WhatsApp, y en la confiabilidad del sistema a los seis meses de operación. Los 3 días de inversión en Tier 0, los 2 días en schema de `outcome_ledger`, y las 50–200 líneas de la capa `VectorStore` son primas de seguro contra la complejidad prematura. En arquitectura de software multi-tenant B2B, la disciplina de empezar simple y escalar inteligente es la única ventaja sostenible.
# 6. Matriz de Decisiones y Roadmap

## 6.1 Cuadro Resumen

### 6.1.1 Tabla final: GAP × Decisión × Fase × Esfuerzo × Impacto

Los cuatro gaps arquitectónicos investigados convergen en un patrón de decisión coherente: dos implementaciones inmediatas que reducen costos y latencia desde el día uno, y dos diferimientos estructurados que acumulan datos de producción antes de activar complejidad adicional. La matriz siguiente condensa las recomendaciones en una vista ejecutiva diseñada para priorización de backlog con 1–3 desarrolladores y un presupuesto de infraestructura de ~$200/mes.

| GAP | Dim | Decisión | Fase | Esfuerzo (días) | Impacto proyectado | Rationale clave |
|:---|:---|:---|:---|:---|:---|:---|
| GAP 1 — Tier 0 sub-LLM | 01, 02, 03 | ✅ **IMPLEMENTAR** | MVP (día 1–3) | ~3 días | Reducción de costos 40–95%; latencia p95 <100 ms para 80% de requests [^1^][^6^] | Regex stdlib `re` (~5–50 μs) es 20,000–220,000× más rápido que Haiku (~750–1,100 ms); 60–80% de documentos LATAM son XML parseables sin LLM [^119^][^201^] |
| GAP 2 — Routing aprendido | 04, 05, 06 | ⏳ **DIFERIR** | Phase 2 (>3,000 req/día) | 2–3 días (preparación MVP) | Habilitación de bandit con datos históricos; eliminación de cold start [^4^][^383^] | Cold start requiere ~5,000 pulls/brazo; a 100–300 req/día el sistema tardaría ~90 días en estabilizar [^5^][^379^] |
| GAP 3 — Spawning controlado | 07, 08, 09 | ⏳ **DIFERIR** | Fase 6 (>3 tools complejas) | 1–2 días (approval gates MVP) | Mitigación de riesgo multi-agente (41–86.7% tasa de fallo); preservación de single-agent estable [^338^][^336^] | MAST (NeurIPS 2025): 41–86.7% fallos en 1,642 trazas; single-agent iguala multi-agent a menor costo [^336^][^385^] |
| GAP 4 — pgvector + RLS | 10, 11, 12 | ✅ **IMPLEMENTAR** (stay pgvector) | MVP | ~2 días (configuración defensiva) | Capacidad hasta ~450K vectores ($135/mes); RLS nativo sin reimplementación [^4^][^654^] | Overhead RLS HNSW ~20% (3–5 ms → 5–6 ms); schema-per-tenant descartado por saturación >100 tenants [^10^][^549^] |

La lectura de la matriz revela una distribución de riesgo intencionalmente asimétrica. Las dos implementaciones inmediatas (GAP 1 y GAP 4) son cambios aditivos que no modifican la arquitectura existente: Tier 0 se inserta antes del L1 Haiku como middleware de pre-filtrado, y pgvector se consolida con configuraciones defensivas (HNSW, halfvec, composite indexes) dentro de la instancia Supabase ya operativa. Ambos tienen esfuerzo medido en días, no semanas, y ambos generan retorno mensurable desde la primera semana de operación. El GAP 1, en particular, es un diferenciador competitivo frente a SaaS genéricos que envían todo a LLM: el mercado LATAM tiene >90% de e-invoicing estructurado [^201^], y un parser XML por país es core competency que ningún competidor extranjero replica sin inversión local.

Los dos diferimientos (GAP 2 y GAP 3) obedecen a la misma lógica de umbral de activación: la tecnología existe, pero el volumen de datos o la complejidad del workload no la justifican en el horizonte de 60 días. La diferencia crítica está en que ambos diferimientos requieren preparación durante el MVP para eliminar fricción en la transición. El GAP 2 exige el schema `OutcomeLedger` y la API interna de `ModelFingerprint` desde el día uno; sin ellos, la activación de Phase 2 enfrenta un cold start de semanas. El GAP 3 exige approval gates por tool usando `requires_approval=True` de Pydantic AI [^482^], que si se omiten en el MVP implican una re-arquitectura de flujos de cobranza y proformas cuando la complejidad eventualmente justifique spawning. En ambos casos, la inversión de preparación es marginal (2–3 días cada uno) frente al costo de no prepararse (re-arquitectura de 1–2 semanas con datos de producción en tránsito).

El único conflicto identificado en la investigación — CZ-001, el dato "87% hallucination cascade en 4h" del brief original versus el rango 41–86.7% de MAST (NeurIPS 2025) [^338^] — no altera ninguna decisión de la matriz, pero sí obliga a actualizar la argumentación técnica en documentos de stakeholder. La decisión de mantener single-agent en MVP sigue siendo correcta; la justificación debe sustituirse por evidencia verificable.

La proyección de costos agregada para el MVP con las dos implementaciones activadas se sitúa entre $135–$160/mes: Supabase Pro + Large ($135/mes) para pgvector con halfvec [^654^], más LiteLLM proxy en infraestructura existente, más la reducción de tokens por Tier 0 que compensa parcialmente el costo de API. Este rango está dentro del presupuesto de ~$200/mes con margen de $40–$65 para imprevistos. El punto de tensión económica proyectado ocurre en el mes 5–6, cuando los vectores activos alcanzan 300K–500K y el equipo debe decidir entre upgrade a XL ($235/mes, +18% sobre budget) o migración a Qdrant Cloud con Binary Quantization ($30–$60/mes, ahorro de 75–86% versus Supabase 2XL) [^697^]. Esa decisión es Phase 2, no MVP.

## 6.2 Próximos Pasos Inmediatos

### 6.2.1 Acciones para semana 1–2 post-research

La transición de investigación a implementación requiere secuenciación estricta por dependencias técnicas. El Tier 0 (GAP 1) debe existir antes de que cualquier otro componente pueda beneficiarse de él; el `OutcomeLedger` (GAP 2) debe escribirse desde el primer request post-MVP para acumular histórico; y la capa `VectorStore` (GAP 4) debe abstraer pgvector antes de que el primer tenant produzca vectores reales. La secuencia propuesta respeta estas dependencias.

**Semana 1: Implementar Tier 0 Deterministic Pre-filter.** El desarrollador asignado construye un middleware FastAPI que intercepta requests antes del agente Pydantic AI, ejecuta pre-checks regex contra 14 reglas definidas (parsers XML por país, validación TIN, extracción email), y aplica Pydantic validation antes de decidir si el request resuelve localmente o asciende a Haiku vía LiteLLM. La integración con LiteLLM pre-call hooks [^183^] permite que los requests Tier 0 nunca generen costo de API. El entregable es un módulo `tier0.py` con tests unitarios que cubren al menos 80% de los casos determinísticos identificados para cobranza y proformas. Esfuerzo: 2–3 días. Bloqueador potencial: acceso a muestras XML reales de cada país para calibrar parsers; mitigación con documentos públicos de autoridades fiscales [^45^][^81^].

**Semana 1 (paralelo): Documentar API interna ModelFingerprint.** El endpoint `GET /model/similarity` debe exponer similitud coseno entre modelos con semántica de transferencia (descuento 0.5 para similitud >0.8, cold start para <0.2) [^318^][^411^]. Esta API se consume hoy por el sistema de probation; mañana por el sistema de routing de Phase 2. La documentación interna debe especificar que `ModelFingerprint` evolucionará de mecanismo de seguridad a feature de contexto del futuro bandit [^384^][^282^]. Esfuerzo: 0.5 días.

**Semana 2: Crear schema OutcomeLedger.** La tabla `(request_id, task_type, model_used, prompt_hash, response_hash, latency_ms, cost_usd, user_feedback, llm_judge_score, timestamp, org_id)` se implementa en Supabase con RLS por `org_id`. No activa bandit todavía, pero acumula las cuatro señales de recompensa futura: latencia real, costo real vía LiteLLM spend logs, user feedback binario, y llm-as-judge score cuando sea factible [^296^]. La granularidad de escritura es una fila por request, sin agregaciones, para maximizar flexibilidad de query analítica posterior. Esfuerzo: 1–1.5 días.

**Semana 2: Configurar pgvector defensivo.** Activar HNSW como índice por defecto, halfvec quantization desde el embedding service [^694^], RLS policies con `tenant_id` como leading column en composite indexes [^549^], y validar que `hnsw.iterative_scan` esté disponible en la instancia Supabase [^501^]. Construir la capa de abstracción `VectorStore` que limita la superficie de migración futura a 50–200 líneas de código. Ejecutar benchmark mínimo ANN-Benchmarks con targets p95 < 100 ms, QPS > 10, recall@10 > 0.90 [^687^]. Esfuerzo: 1.5–2 días.

**Semana 2 (paralelo): Implementar approval gates por tool en Pydantic AI.** Declarar `requires_approval=True` en tools de alto impacto (envío de proforma al cliente, registro de cobro como pagado) [^482^]. Diseñar la UX dual: web console con preview granular, WhatsApp con notificaciones binarias y deep-link a consola para decisiones multi-step [^487^][^488^]. Esfuerzo: 1–2 días.

La suma de esfuerzos críticos para las dos primeras semanas post-research es ~6–8 días de trabajo de un desarrollador, distribuible en paralelo si el equipo tiene 2 desarrolladores. Con 1 desarrollador, la secuencia se extiende a 3 semanas. Esta carga es compatible con un MVP de 60 días que incluye onboarding de tenants, integración WhatsApp Business API, y desarrollo de workflows de cobranza y proformas. La regla de priorización es: cualquier item de backlog que no reduzca costo, latencia o riesgo de fallo en las primeras 4 semanas se mueve a Phase 2.
