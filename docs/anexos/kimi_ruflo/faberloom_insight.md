# Insight Extraction: Faberloom × Ruflo — 4 Gaps Arquitectónicos

## Fecha: 2026-04-26
## Fase: Phase 6 — Insight Extraction

---

## Insight 1: La Arquitectura Actual de Faberloom YA Es un "Tier System" Implícito

**Insight:** Faberloom ya tiene 2 tiers (L1 Haiku, L2 dispatcher). La recomendación de Ruflo no es adoptar 3 tiers nuevos, sino reconocer que el L1 de Faberloom está sobredimensionado: usa Haiku para tareas que regex podría resolver. El verdadero gap no es arquitectónico (no tienen tier system), sino de optimización de costo-latencia en el tier más bajo.

**Derived From:** Dim 01 (latencia 20,000-220,000× regex vs Haiku), Dim 02 (60-80% documentos parseables sin LLM), Dim 03 (stdlib re + Pydantic validation), Dim 05 (router propio 2-8ms overhead)

**Rationale:** Tanto Ruflo como Faberloom usan routing por tiers. Ruflo tiene 3 tiers (WASM lightweight, mid, full Claude). Faberloom tiene 2 tiers (Haiku classifier, dispatcher). La diferencia no es la arquitectura, sino que Ruflo tiene un tier sub-Haiku que Faberloom no explota. El "Agent Booster" de Ruflo en WASM es equivalente a un "Tier 0" que Faberloom puede replicar en Python con stdlib re.

**Implications:** La implementación de Tier 0 no requiere cambio arquitectónico mayor. Es un pre-procesamiento antes del L1 existente. Esto reduce el riesgo de implementación a casi cero.

**Confidence:** High

---

## Insight 2: El "ModelFingerprint" de Faberloom Es Más Valioso para Routing Que para Seguridad

**Insight:** El brief original diseña ModelFingerprint como mecanismo de seguridad (probation al cambiar modelo/policy). Sin embargo, la investigación revela que el patrón estándar en producción (Scope, DFPE, Behavioral Fingerprint) usa embeddings de comportamiento principalmente para routing inteligente, no para seguridad. El fingerprint puede servir como feature del contextual bandit en Phase 2, no solo como gate de aprobación.

**Derived From:** Dim 06 (ModelFingerprint = vector 384-dim de comportamiento, cosine sim >0.8 para transfer), Dim 04 (contextual bandit routing), Dim 05 (router propio con features de contexto)

**Rationale:** Cuando un nuevo modelo llega (ej: Sonnet 4.6), el fingerprint compara su comportamiento contra el modelo anterior. Si similitud >0.8, se transfiere histórico con descuento 0.5. Esto es exactamente lo que necesita el routing aprendido. La infraestructura de fingerprinting ya existe; solo necesita exponerse como feature al futuro sistema de routing.

**Implications:** El ModelFingerprint no debería ser solo un componente de seguridad aislado. Debe diseñarse con una API interna que permita consultar similitud de modelos para el routing de Phase 2. Esto evita duplicación de infraestructura.

**Confidence:** High

---

## Insight 3: La Decisión de NO Multi-Agente en MVP Se Fortalece, Pero el Argumento Debe Cambiar

**Insight:** El brief original justifica NO multi-agente con "40% fallan a 6 meses" (Gartner) y "87% hallucination cascade en 4h" (dato no verificable). La investigación confirma que la decisión es correcta, pero por razones diferentes y más sólidas: (a) single-agent supera multi-agent en razonamiento multi-hop bajo igual presupuesto de tokens (NeurIPS 2025), (b) 41-86.7% tasa de fallo verificable en multi-agente (MAST), (c) 2-5x multiplicador de costos. El argumento del brief original es estadísticamente impreciso y debe actualizarse antes de presentarse a stakeholders.

**Derived From:** Dim 07 (10 handoffs al 99% = 90.4% confiabilidad total), Dim 08 (MAST 41-86.7% fallo, single-agent vs MAS paper), Dim 09 (Gartner 40%, NeurIPS single-agent iguala multi-agent)

**Rationale:** El dato "87% en 4h" es una mezcla de dos fuentes incompatibles: 86.7% de MAST (tasa de fallo en trazas, no temporal) y extrapolación de costo de Cycles blog. Usar este número con stakeholders técnicos o inversores sería desacreditado si se verifica. Es mejor usar la literatura académica verificable.

**Implications:** La documentación de Faberloom (SPEC_FABERLOOM_MVP, ARCH_AGENT_PRINCIPLES) debe actualizar su argumentación contra multi-agente. La decisión sigue siendo la misma (NO multi-agente MVP), pero el "por qué" necesita corregirse.

**Confidence:** High

---

## Insight 4: pgvector + RLS Tiene un "Hidden Tipping Point" en el Costo de Supabase, No en Performance

**Insight:** La preocupación original del GAP 4 es performance a 100+ tenants. Sin embargo, la investigación muestra que el tipping point real es ECONÓMICO, no técnico: pgvector en Supabase maneja 1M vectores sin problemas de latencia (p50 ~5ms, p95 ~20% overhead), pero el costo de Supabase supera $200/mes a ~450K vectores por la necesidad de instancias XL/2XL. El problema no es "¿aguanta?" sino "¿cuánto cuesta?".

**Derived From:** Dim 10 (HNSW p50 ~5ms, 20% RLS overhead), Dim 11 (pgvector $25-35/mes típico), Dim 12 (punto de ruptura ~450K vectores = $135-410/mes)

**Rationale:** El benchmark EDBT 2026 muestra contención en PostgreSQL multi-tenant, pero RLS específicamente añade solo ~20% en vector search. La latencia sigue siendo aceptable (<10ms) para 1M vectores. El verdadero límite es que Supabase free tier cappea maintenance_work_mem a 32MB (índices >20K vectores fallan) y el Pro tier requiere Large compute ($110) para cargas reales. A 1M vectores necesitas 2XL ($410/mes), que supera el presupuesto MVP.

**Implications:** El benchmark que Faberloom debe correr NO es de latencia (eso está resuelto), sino de capacidad de índice por tier de Supabase. Deben testear cuántos vectores caben en cada tier ANTES de escalar tenants.

**Confidence:** High

---

## Insight 5: LiteLLM Es el "Hilo Invisible" Que Conecta 3 de los 4 Gaps

**Insight:** LiteLLM aparece como solución en GAP 1 (pre-call hooks para Tier 0), GAP 2 (multi-tenant routing vía Organizations/Teams/Keys), y GAP 4 (no requiere cambios al migrar vector DB). La elección de LiteLLM en el stack original de Faberloom no fue solo un "LLM proxy", sino una decisión arquitectónica que habilita múltiples optimizaciones futuras. Esto no fue evidente en el diseño original.

**Derived From:** Dim 03 (LiteLLM pre-call hooks), Dim 05 (LiteLLM Organizations → Teams → Keys), Dim 12 (LiteLLM no requiere cambios al migrar vector DB)

**Rationale:** LiteLLM tiene: (a) pre-call hooks para ejecutar regex antes de enviar al LLM, (b) organizaciones/teams/keys que permiten routing por tenant sin reimplementar, (c) embeddings endpoint que abstrae el provider de vector DB subyacente. Si Faberloom migra de pgvector a Qdrant, LiteLLM sigue funcionando igual. Si implementa Tier 0, LiteLLM puede ejecutarlo como hook. Si hace routing por org, LiteLLM ya tiene la estructura.

**Implications:** Faberloom debería documentar explícitamente en su arquitectura que LiteLLM es un "capa de abstracción multi-propósito", no solo un proxy de APIs. Esto justifica su presencia en el stack más allá del "routing de modelos".

**Confidence:** Medium-High

---

## Insight 6: WhatsApp Business API Es el Cuello de Botella de UX para CUALQUIER Feature Multi-Step

**Insight:** La investigación del GAP 3 revela que WhatsApp Business API limita severamente la UX de aprobación multi-step: máximo 3 quick reply buttons, 20 caracteres por botón, sesión de 24h. Esto no es solo un problema para skill-to-skill delegation; es un problema para CUALQUIER feature que requiera decisiones humanas en medio de un workflow (HITL, aprobación de proformas, validación de cobranza). La consola web debe ser el canal principal para interacciones complejas; WhatsApp solo para notificaciones y respuestas binarias.

**Derived From:** Dim 09 (WhatsApp Business API limits), Dim 02 (workflow de cobranza), Dim 07 (handoffs UX)

**Rationale:** Si Faberloom implementa Tier 0 y luego necesita HITL para el 5-20% de casos no resueltos por regex, la aprobación en WhatsApp será frustrante. Un workflow de cobranza que requiera "¿aprobar extracción de monto? → ¿aprobar clasificación? → ¿aprobar acción?" necesita 3 mensajes separados en WhatsApp, pero una sola pantalla en la consola web.

**Implications:** El diseño de UX de Faberloom debe asumir que cualquier interacción multi-step va a la consola web, y WhatsApp solo dispara links a la consola. No se debe diseñar aprobación granular en WhatsApp.

**Confidence:** High

---

## Insight 7: La "E-invoicing Mature" de LATAM Es una Ventaja Estratégica Ignorada

**Insight:** La investigación del GAP 1 descubre que >90% de PYMEs LATAM usan e-invoicing estructurado (XML UBL 2.1 en Colombia, DTE en Chile, CFDI en México, NFe en Brasil, AFIP en Argentina). Esto significa que el mercado objetivo de Faberloom ya tiene sus documentos en formato parseable sin LLM. Esto es una ventaja competitiva MASIVA frente a mercados como EE.UU. donde los invoices son PDFs no estructurados. Faberloom no debería usar LLM para parsing de facturas; debería usar parsers XML específicos por país.

**Derived From:** Dim 02 (autoridades fiscales LATAM, 90%+ e-invoicing), Dim 01 (BI-RADS benchmark: regex 18,404× más rápido)

**Rationale:** Colombia (DIAN), Chile (SII), México (SAT), Brasil (SEFAZ), Argentina (AFIP) todos tienen esquemas XML publicados y obligatorios. Un SaaS de cobranza B2B LATAM que use LLM para parsear XML está desperdiciando dinero y latencia innecesariamente.

**Implications:** Faberloom debería invertir en parsers XML por país como core competency, no como afterthought. Esto reduce costos, mejora latencia, y aumenta precisión. Es un diferenciador frente a competidores genéricos que usan LLM para todo.

**Confidence:** High

---

## Insight 8: El Patrón "Deterministic Pre-filter → LLM Fallback → Human Gate" Es Universal

**Insight:** Tres de los cuatro gaps convergen en el mismo patrón arquitectónico: (1) Tier 0 regex antes de Haiku, (2) Rule-based routing antes de bandit adaptive, (3) Single-agent antes de multi-agente. El patrón común es: "empezar con lo determinístico/barato, fallback a lo inteligente/caro, gate humano al final". Este patrón no es una limitación del MVP; es una estrategia de escalado probada. Ruflo mismo lo usa (WASM pre-filter → tier routing → Claude full).

**Derived From:** Dim 01 (Tier 0 → Haiku), Dim 04 (rule-based L1/L2 → bandit Phase 2), Dim 07 (single-agent → multi-agent Phase 6), Dim 09 (Pydantic AI approval gates)

**Rationale:** Todos los sistemas de producción confiables usan capas de defensa en profundidad. La investigación muestra que los sistemas que saltan directamente a la capa inteligente (LLM puro, bandit puro, swarm puro) tienen tasas de fallo 2-5× mayores.

**Implications:** Faberloom debería documentar este patrón como "Faberloom Principle: Deterministic First" y aplicarlo consistentemente en futuras decisiones arquitectónicas. No es "MVP simplificado", es "producción robusta".

**Confidence:** High

---

## Insight 9: La Granularidad "Per-Org" Es un Anti-Patrón en MVP Multi-Tenant

**Insight:** La investigación del GAP 2 (Dim 06) revela que routing per-org puro es demasiado sparse para MVP con pocos datos por tenant. Sin embargo, la arquitectura de Faberloom ya usa RLS per-org (GAP 4) y memoria per-cliente (brief original). Hay una tensión: la seguridad y aislamiento requieren per-org, pero el aprendizaje requiere agregación. La solución no es eliminar per-org, sino separar dos sistemas: RLS para seguridad (siempre per-org), routing para optimización (task_type global con priors bayesianos informativos).

**Derived From:** Dim 06 (per-org demasiado sparse, task_type global mejor), Dim 10 (RLS per-org es correcto para seguridad), Dim 05 (LiteLLM Organizations multi-tenant)

**Rationale:** GreenServ ablation muestra que `task_type` es la feature más informativa para routing. `org_id` como feature directa fragmenta datos. Pero RLS sin `org_id` sería inseguro. Los dos sistemas coexisten: RLS asegura que los datos no se mezclen; el router aprende de patrones agregados across-org.

**Implications:** El diseño de Faberloom debe mantener RLS per-org (seguridad) y diseñar el futuro routing con features de `task_type` + `query_embedding` (optimización), no con `org_id` directo. Esto debe documentarse para evitar que un desarrollador futuro "optimice" agregando org_id al router.

**Confidence:** High

---

## Summary de Insights

| # | Insight | Confidence | Gap(s) Relacionado(s) |
|---|---------|------------|----------------------|
| 1 | Arquitectura actual YA es tier system; gap es optimización del tier más bajo | High | GAP 1 |
| 2 | ModelFingerprint más valioso para routing que para seguridad | High | GAP 2 |
| 3 | Decisión NO multi-agente correcta, pero argumento debe actualizarse | High | GAP 3 |
| 4 | Tipping point de pgvector es económico, no técnico | High | GAP 4 |
| 5 | LiteLLM conecta 3 gaps como hilo invisible | Medium-High | GAP 1, 2, 4 |
| 6 | WhatsApp API es cuello de botella UX para todo multi-step | High | GAP 3 |
| 7 | E-invoicing LATAM es ventaja competitiva ignorada | High | GAP 1 |
| 8 | Patrón "Deterministic First → LLM Fallback → Human Gate" es universal | High | Todos |
| 9 | Granularidad per-org es anti-patrón en aprendizaje (pero correcta en seguridad) | High | GAP 2, 4 |

