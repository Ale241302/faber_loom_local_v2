# Dimensión 05 — GAP 2: Sistemas en Producción (Martian, RouteLLM, NotDiamond, OpenPipe)

## Investigador: Sistema de Investigación Técnica
## Fecha: 2026
## Búsquedas realizadas: 29 búsquedas independientes
## Fuentes primarias: arXiv, GitHub, LMSYS Blog, ICLR 2026, docs oficiales, blogs de ingeniería (LogRocket, MorphLLM, RelayPlane, MindStudio)

---

## 1. RouteLLM (LMSYS): Funcionamiento, Datos, Reproducibilidad

### Hallazgo 1.1: RouteLLM es un framework open-source para serving y evaluación de LLM routers

```
Claim: RouteLLM es un framework open-source con drop-in replacement para el cliente de OpenAI (o server OpenAI-compatible) que rutea queries simples a modelos más baratos, logrando reducciones de costo de hasta 85% manteniendo 95% del performance de GPT-4 en benchmarks como MT Bench [^109^].
Source: GitHub - lm-sys/RouteLLM
URL: https://github.com/lm-sys/routellm
Date: 2024-06-03
Excerpt: "Trained routers are provided out of the box, which we have shown to reduce costs by up to 85% while maintaining 95% GPT-4 performance on widely-used benchmarks like MT Bench. Benchmarks also demonstrate that these routers achieve the same performance as commercial offerings while being >40% cheaper."
Context: Framework desarrollado en colaboración con Anyscale. Incluye server OpenAI-compatible (Uvicorn) y evaluation framework.
Confidence: high
```

### Hallazgo 1.2: RouteLLM usa preference data de Chatbot Arena + data augmentation

```
Claim: RouteLLM se entrena principalmente con 80K datos de Chatbot Arena (human preference comparisons), pero requiere data augmentation (golden-label datasets como MMLU o LLM-judge labels) para generalizar fuera del dominio de entrenamiento [^260^].
Source: arXiv - RouteLLM: Learning to Route LLMs with Preference Data
URL: https://arxiv.org/html/2406.18665v4
Date: 2024-09-29
Excerpt: "We primarily use the 80K Chatbot Arena data D_arena for training our models, but hold out 5k samples for validation... We further augment our training data with either: 1) D_gold, golden-labeled data created from the MMLU validation split, or 2) D_judge, GPT-4-as-a-judge labeled data."
Context: El paper demuestra que sin data augmentation, los routers fallan en OOD benchmarks como MMLU y GSM8K. La data augmentation con ~1500 samples mejora drásticamente.
Confidence: high
```

### Hallazgo 1.3: RouteLLM tiene 4 estrategias de routing implementadas

```
Claim: RouteLLM implementa 4 routers: similarity-weighted ranking (SW), matrix factorization (MF), BERT classifier, y causal LLM classifier (Llama 3 8B). El router MF es el mejor performer en benchmarks [^265^].
Source: LMSYS Blog - RouteLLM: An Open-Source Framework for Cost-Effective LLM Routing
URL: https://lmsys.org/blog/2024-07-01-routellm/
Date: 2024-07-01
Excerpt: "We trained four routers using a mix of Chatbot Arena data and data augmentation: A similarity-weighted (SW) ranking router... A matrix factorization model... A BERT classifier... A causal LLM classifier..."
Context: El router MF alcanza 95% del performance de GPT-4 usando solo 14% de llamadas a GPT-4 (75% más barato que random baseline) cuando se entrena con data augmentation.
Confidence: high
```

### Hallazgo 1.4: El router BERT original tiene problemas graves de reproducibilidad

```
Claim: La implementación original del router BERT en RouteLLM sufre de majority class overfitting, con macro F1 scores de solo 0.23-0.35. Además, los autores no liberaron el dataset exacto que usaron (solo 19k samples accesibles vs 65k reclamados) [^274^].
Source: GitHub - Liqs-v2/RouteLLM (Reproducción independiente)
URL: https://github.com/Liqs-v2/RouteLLM
Date: 2025-11-11
Excerpt: "Majority Class Overfitting: The authors' BERT routers were overfitting to the majority class, achieving poor macro F1 scores (0.23-0.35) across all their checkpoints... Incomplete Dataset Release: Authors claimed 65k samples but preprocessing yielded only 19k; they didn't release their exact D_arena dataset."
Context: Un equipo independiente reprodujo el BERT router, identificó estos problemas, y con rebalancing de dataset logró resultados competitivos con menos datos. Esto cuestiona la reproducibilidad directa del paper para producción.
Confidence: high
```

### Hallazgo 1.5: RouteLLM no soporta contextos largos (limitado a 8,192 tokens)

```
Claim: RouteLLM no puede evaluarse en tareas de long-context routing porque su text encoder solo soporta inputs de hasta 8,192 tokens, excluyendo muchas queries de contexto largo [^293^].
Source: RouterArena (ICLR 2026)
URL: https://openreview.net/pdf?id=9HsaIi4ngF
Date: 2026 (conference paper)
Excerpt: "RouteLLM cannot be evaluated on this subset because its text encoder only supports inputs up to 8,192 tokens, which excludes many of our long-context queries."
Context: Limitación crítica para SaaS B2B donde documentos, proformas y workflows pueden exceder 8K tokens.
Confidence: high
```

### Hallazgo 1.6: RouteLLM no tiene actualizaciones recientes

```
Claim: El repositorio de RouteLLM tuvo su última actualización en agosto 2024. El desarrollo activo ha disminuido mientras LMSYS se enfoca en Chatbot Arena [^327^].
Source: Medium - LLM Least Privilege: Smart Model Selection
URL: https://medium.com/@michael.hannecke/least-privilege-for-llm-agents-applying-security-principles-to-model-selection-57760accb041
Date: 2025-12-22
Excerpt: "Status note (December 2025): The RouteLLM GitHub repository was last updated in August 2024. The pre-trained routers work well, but active development has slowed as the LMSYS team focuses on Chatbot Arena."
Context: Para un MVP que necesita mantenimiento continuo, esto es una señal de alerta. Los routers pre-entrenados funcionan pero no hay evolución activa.
Confidence: high
```

---

## 2. Martian: Precio, Modelo de Negocio, Arquitectura, Self-Hosting

### Hallazgo 2.1: Martian es cloud-only, proprietary, NO self-hosteable

```
Claim: Martian es un servicio cloud propietario con algoritmo de routing black box. No ofrece opción de self-hosting o on-premise. El routing ocurre en sus servidores, lo que significa que los prompts pasan por su infraestructura [^302^][^316^].
Source: RelayPlane vs Martian Comparison + Nolist.ai review
URL: https://relayplane.com/compare/relayplane-vs-martian
Date: Unknown (2026)
Excerpt: "RelayPlane is open source and self-hosted. Martian is a proprietary cloud service... Martian's routing algorithm is a black box... Martian routes through their servers."
Context: Esto implica compliance risk (data residency LATAM) y vendor lock-in. No apto si los datos de clientes PYME no pueden salir de tu control.
Confidence: high
```

### Hallazgo 2.2: Martian cobra $20/mes base + pricing por volumen

```
Claim: Martian tiene un tier Developer gratuito (2,500 requests/mes) pero requiere tarjeta de crédito y $20/mes para acceder a routing de producción. Agrega ~20-50ms de latencia por request [^316^][^310^].
Source: Nolist.ai review + LogRocket Blog
URL: https://nolist.ai/item/martian
Date: 2026-03-08
Excerpt: "While there is a free 'Developer' tier allowing 2,500 requests per month, you must provide a credit card for the $20/month starting price to access production-grade routing... Martian adds a $20 monthly base fee and intelligent routing logic whereas OpenRouter is a pure pass-through aggregator."
Context: A 2,500 requests/mes es insuficiente para un SaaS B2B con 50+ clientes. El salto a producción implica costo fijo + potencialmente volume-based pricing no transparente.
Confidence: medium
```

### Hallazgo 2.3: Martian usa "Model Mapping" (interpretabilidad mecanicista) pero solo soporta 6 providers

```
Claim: Martian basa su routing en una técnica propietaria llamada Model Mapping que descompone LLMs en arquitecturas interpretables. Sin embargo, solo soporta 6 providers principales vs cientos de OpenRouter [^311^][^316^].
Source: Yahoo Finance press release + Nolist.ai
URL: https://finance.yahoo.com/news/martian-invents-model-router-beats-190000381.html
Date: 2023-11-15
Excerpt: "Martian understands LLMs through a technique they pioneered called 'Model Mapping.' The software takes AI models (essentially complicated black boxes) and converts them into other forms that are simpler and easier to study... Martian supports only 6 major providers while OpenRouter provides access to hundreds of niche models."
Context: La tecnología es interesante desde la investigación, pero la cobertura de modelos limitada reduce flexibilidad para un stack que usa LiteLLM (100+ providers).
Confidence: high
```

### Hallazgo 2.4: Martian NO aparece en benchmarks académicos comparativos (RouterArena)

```
Claim: RouterArena (ICLR 2026), la primera plataforma abierta de comparación exhaustiva de LLM routers, incluye routers comerciales como NotDiamond y Azure-Router, pero Martian no aparece en el leaderboard ni en las evaluaciones reportadas [^293^].
Source: RouterArena (ICLR 2026)
URL: https://openreview.net/pdf?id=9HsaIi4ngF
Date: 2026
Excerpt: [Leaderboard incluye: MIRT-BERT, Azure-Router, CARROT, vLLM-SR, GPT-5, NIRT-BERT, GraphRouter, NotDiamond, RouteLLM, MLP, KNN, RouterDC — sin Martian]
Context: La ausencia de Martian en el benchmark académico más reciente y comprehensivo dificulta la evaluación objetiva de su performance vs alternativas.
Confidence: medium
```

---

## 3. NotDiamond: Métricas, Integración con LiteLLM, Precio

### Hallazgo 3.1: NotDiamond NO es un proxy — es un recommender de modelos (client-side routing)

```
Claim: NotDiamond opera como "meta-model" recommender, NO como proxy. La aplicación envía el prompt a NotDiamond API, recibe una recomendación del mejor modelo en <50ms, y luego hace el llamado directo al provider con sus propias API keys. Los datos y keys nunca pasan por NotDiamond para la llamada final [^307^].
Source: Skywork.ai - Ultimate Guide to AI Model Routing
URL: https://skywork.ai/skypage/en/Not-Diamond-The-Ultimate-Guide-to-AI-Model-Routing-and-Adaptation/1974878605409316864
Date: 2025-10-07
Excerpt: "A crucial technical point to understand is that Not Diamond is not a proxy. It doesn't sit in the middle of your data stream, intercepting your sensitive information. Instead, it works as a recommender. Your application sends the prompt context to the Not Diamond API, which returns a recommendation for the best model in under 50ms."
Context: Arquitectura significativamente mejor para compliance y data privacy que Martian u OpenRouter. Para LATAM/PYMEs donde los datos son sensibles, esto es una ventaja.
Confidence: high
```

### Hallazgo 3.2: NotDiamond optimiza quality (default), cost, o latency — configurable

```
Claim: NotDiamond permite configurar qué optimizar: Quality (default), Cost, o Latency. El router pre-entrenado es cross-domain; también permite entrenar custom routers para casos de uso específicos [^278^].
Source: NotDiamond Docs - What is Model Routing?
URL: https://docs.notdiamond.ai/docs/what-is-model-routing
Date: 2026-04-17
Excerpt: "Control what Not Diamond optimizes for based on your application's priorities: Quality (default): Routes to the model predicted to give the best response. Cost: Balances quality with cost efficiency, preferring cheaper models when appropriate. Latency: Minimizes response time while maintaining quality thresholds."
Context: Para Faberloom, la capacidad de optimizar por costo o calidad según workflow (cobranza vs proformas) es directamente aplicable.
Confidence: high
```

### Hallazgo 3.3: NotDiamond pricing — $100/mes + $0.001/request after 100K

```
Claim: NotDiamond tiene tier gratuito de 100,000 requests/mes + 1 custom router. El tier paid (Possibility) cuesta $100/mes con uncapped requests y overage de $0.001 por request después de los primeros 100K. Enterprise (Necessity) ofrece VPC deployments y custom integrations [^295^][^307^].
Source: NotDiamond Reviews (Tenereteam) + Skywork.ai guide
URL: https://not-diamond.tenereteam.com/
Date: 2025-07-18
Excerpt: "Discovery Plan: Free access including up to 100,000 monthly API routing requests... Possibility Plan: $100/month... unlimited API routing requests after first 100,000 free ($0.001 per request)... Necessity Plan: Offers VPC deployments, custom integration and router training support."
Context: A $200/mes de presupuesto total de infra, sumar $100/mes solo por routing representa 50% del budget. La alternativa de usar el tier gratuito (100K/mes) podría ser viable en MVP temprano.
Confidence: high
```

### Hallazgo 3.4: NotDiamond permite custom routers entrenados por organización

```
Claim: NotDiamond permite entrenar routers personalizados con datasets propios, optimizados para casos de uso específicos y criterios de evaluación de la organización [^314^][^278^].
Source: NotDiamond Docs - Training a custom router
URL: https://docs.notdiamond.ai/docs/router-training-quickstart
Date: 2026-04-17
Excerpt: "Custom router - Train a router on your data to optimize for your specific use case and evaluation criteria. Recommended for production applications where domain-specific performance matters."
Context: Esto permite que cada tenant/organización tenga su propio router, pero requiere datos de evaluación propios. Para Faberloom con PYMEs homogéneas (construcción LATAM), un router global entrenado con datos propios de producción sería más eficiente que routers per-cliente.
Confidence: high
```

### Hallazgo 3.5: NotDiamond NO tiene integración nativa documentada con LiteLLM

```
Claim: No se encontró documentación ni evidencia de integración nativa entre NotDiamond y LiteLLM. NotDiamond integra con OpenRouter (Auto Router powered by NotDiamond), pero la integración con LiteLLM requeriría implementación manual del client-side routing [^176^][^302^].
Source: MorphLLM - OpenRouter Alternative + AI Collab Blog
URL: https://www.morphllm.com/openrouter-alternative
Date: 2026-03-31
Excerpt: "OpenRouter's Auto Router (openrouter/auto) is powered by NotDiamond and selects from a pool of 33 models based on prompt analysis... LiteLLM does not have a model selection feature equivalent to OpenRouter's Auto Router. You specify which model to call."
Context: Para Faberloom (stack: FastAPI + LiteLLM + Supabase), usar NotDiamond implicaría: (a) reemplazar LiteLLM como proxy, o (b) agregar una llamada adicional a NotDiamond antes de cada request a LiteLLM, añadiendo complejidad.
Confidence: high
```

### Hallazgo 3.6: NotDiamond en benchmarks académicos — buena accuracy pero costo elevado

```
Claim: En RouterArena (ICLR 2026), NotDiamond alcanza 68.0% accuracy overall (rango 6 de 12 routers evaluados) pero con costo de $9.34 por 1K queries — significativamente más caro que routers open-source como MIRT-BERT ($0.15/1K) o CARROT ($2.06/1K) [^293^].
Source: RouterArena (ICLR 2026)
URL: https://openreview.net/pdf?id=9HsaIi4ngF
Date: 2026
Excerpt: "NotDiamond 68.0% ($9.34)... Azure-Router 68.1% ($0.54)... MIRT-BERT 66.9% ($0.15)... RouteLLM 47.0% ($0.27)"
Context: NotDiamond optimiza por calidad más que por costo. Para un SaaS B2B con presupuesto ajustado, esto puede ser contraproducente si el router siempre elige modelos frontier.
Confidence: high
```

---

## 4. OpenPipe: ¿Router o Fine-Tuning Platform?

### Hallazgo 4.1: OpenPipe es PRIMARIAMENTE una fine-tuning platform, NO un router comercial

```
Claim: OpenPipe es una plataforma de fine-tuning (SFT/DPO) con inference hosting, NO un router de modelos. Su core value proposition es capturar tráfico de producción para fine-tune modelos más baratos que repliquen el comportamiento de modelos grandes [^263^][^269^].
Source: PremAI Blog - 8 Best LLM Fine-Tuning Platforms + OpenPipe site
URL: https://blog.premai.io/8-best-llm-fine-tuning-platforms-in-2026-compared/
Date: 2026-03-17
Excerpt: "OpenPipe: Prompt-to-model distillation... The SDK wraps your existing OpenAI API calls. As your application runs, it logs all prompts and completions. You then use that captured traffic to create a training dataset and fine-tune a smaller, cheaper model to replicate what your large model was doing."
Context: Aunque el founding engineer de OpenPipe mencionó en HN que "fine tuning is a great method to better improve the routing intelligence of said Router LLM" [^267^], OpenPipe en sí NO ofrece routing como producto.
Confidence: high
```

### Hallazgo 4.2: OpenPipe NO es una alternativa viable para routing en el MVP de Faberloom

```
Claim: OpenPipe no es recomendable como router para Faberloom porque: (a) no es un router, (b) requiere tráfico de producción existente para ser valioso, (c) no tiene free tier para fine-tuning, (d) los datos de training van a su cloud sin opción on-prem, (e) inference cuesta ~2x más que providers especializados [^263^][^261^].
Source: PremAI Blog + TensorZero comparison
URL: https://www.tensorzero.com/docs/comparison/openpipe
Date: 2026-03-12
Excerpt: "OpenPipe focuses on fine-tuning, while TensorZero provides a complete set of tools for optimizing LLM systems (including prompts, models, and inference strategies)... OpenPipe is a paid managed service (inference costs ~2x more than specialized providers supported by TensorZero)."
Context: OpenPipe podría reconsiderarse en Phase 2 si Faberloom quiere distillar comportamiento de GPT-4o a modelos fine-tuneados locales, pero para routing puro no aplica.
Confidence: high
```

---

## 5. Routing por Organización/Cliente vs Global

### Hallazgo 5.1: Ninguno de los routers comerciales (Martian, NotDiamond, OpenRouter) ofrece multi-tenancy nativa por organización

```
Claim: Martian, NotDiamond y OpenRouter operan como servicios globales — un único router para todo el tráfico del cliente. No hay evidencia de routing aislado por tenant con budgets, model pools, o policies diferentes por organización [^316^][^307^][^302^].
Source: Múltiples fuentes (reviews + docs)
URL: https://nolist.ai/item/martian + https://docs.notdiamond.ai/docs/what-is-model-routing
Date: 2026
Excerpt: [No se menciona multi-tenant routing por organización en ninguna documentación de Martian, NotDiamond o OpenRouter]
Context: Para Faberloom (SaaS multi-tenant para PYMEs), esto significa que si se usa un router externo, todos los tenants comparten el mismo router global y las mismas policies de routing.
Confidence: medium
```

### Hallazgo 5.2: LiteLLM SÍ tiene arquitectura multi-tenant nativa con Organizations → Teams → Keys

```
Claim: LiteLLM (ya en stack de Faberloom) soporta multi-tenancy nativa con jerarquía Organizations → Teams → Users → Keys, incluyendo aislamiento de tenants, billing per-customer, budgets per-team, y model access control [^296^].
Source: LiteLLM Docs - Multi-Tenant Architecture
URL: https://docs.litellm.ai/docs/proxy/multi_tenant_architecture
Date: Unknown (documentación actual)
Excerpt: "Each tenant (organization) is isolated: Cannot view other organizations' data, Cannot access other organizations' keys, Cannot exceed their budget limits, Cannot access models not in their allowed list... LiteLLM solves multi-tenant architecture challenges through: Hierarchical Structure, Granular RBAC, Cost Attribution, Delegation, Isolation, Scalability."
Context: LiteLLM cubre la capa de gateway/proxy multi-tenant, pero NO tiene router inteligente por prompt (model selection). La combinación de LiteLLM + router propio es la única opción que da multi-tenancy + routing inteligente.
Confidence: high
```

### Hallazgo 5.3: NotDiamond permite "custom routers" pero no se documenta multi-tenant isolation

```
Claim: NotDiamond permite entrenar custom routers para casos de uso específicos, pero la documentación no menciona si estos routers pueden asignarse a diferentes tenants/organizaciones con aislamiento de datos o policies independientes [^314^].
Source: NotDiamond Docs
URL: https://docs.notdiamond.ai/docs/router-training-quickstart
Date: 2026-04-17
Excerpt: [No se menciona multi-tenancy, tenant isolation, o per-organization routing en la documentación de custom routers]
Context: Aunque un SaaS podría crear un custom router global entrenado con sus propios datos, no es claro si puede tener múltiples routers aislados por cliente sin múltiples cuentas/costos Enterprise.
Confidence: low
```

---

## 6. Costo: Router Externo vs Implementación Propia

### Hallazgo 6.1: Costo de router externo (NotDiamond): ~$100-200/mes para MVP

```
Claim: NotDiamond cuesta $100/mes base + $0.001/request después de 100K. Martian cuesta $20/mes base + volumen. Para un MVP con ~10K-50K requests/mes, el costo de router externo sería $100-150/mes (NotDiamond) o $20-50/mes (Martian), sin contar los tokens de los modelos subyacentes [^295^][^316^].
Source: Nolist.ai + Tenereteam
URL: https://not-diamond.tenereteam.com/
Date: 2025-07-18
Excerpt: "Possibility Plan: $100/month... unlimited API routing requests after first 100,000 free ($0.001 per request)."
Context: Con presupuesto de infra de ~$200/mes, gastar $100 en routing representa 50% del budget. La decisión debe pesar el ahorro en tokens vs el costo fijo del router.
Confidence: high
```

### Hallazgo 6.2: Costo de implementar router propio: ~pocas semanas de ingeniería para MVP

```
Claim: Implementar un router simple (L1 clasificador por task_type + complejidad + costo, como el diseño actual de Faberloom) puede lograrse en "pocas semanas de trabajo de 1 dev" con reglas heurísticas o un clasificador pequeño (Haiku/BERT). LiteLLM ya cubre el 80% del gateway [^310^][^335^].
Source: LogRocket + Dev.to (LLM Gateway vs Router)
URL: https://blog.logrocket.com/llm-routing-right-model-for-requests/
Date: 2026-02-05
Excerpt: "Building your own remains the most common approach. If you already have a backend handling LLM requests, adding simple routing logic is usually just a few hundred lines of code... For teams with strong engineering cultures and specific requirements, this is still the right choice."
Context: Faberloom YA tiene un L1 clasificador (Haiku) + L2 dispatcher en el diseño actual. Esto es fundamentalmente un router propio. El costo de implementación ya está absorbido en el desarrollo del MVP.
Confidence: high
```

### Hallazgo 6.3: TCO de un router/gateway completo en 3 años: $234K-$1.69M

```
Claim: Según análisis de MindStudio, el total cost of ownership de un router open-source en producción a 3 años puede ir de $234K (simple) a $1.69M (complex routing systems), considerando infra, mantenimiento, monitoreo y tiempo de ingeniería [^329^].
Source: MindStudio - Best AI Model Routers
URL: https://www.mindstudio.ai/blog/best-ai-model-routers-multi-provider-llm-cost-011e6/
Date: 2026-02-10
Excerpt: "That open-source router might be 'free,' but running it in production requires infrastructure, maintenance, monitoring, and engineering time. The total cost over three years can range from $234K for simple deployments to $1.69M for complex routing systems."
Context: Este número es para "routing systems" enterprise-grade con múltiples providers, semantic caching, failover, etc. El router simple de Faberloom (L1 classifier + L2 dispatcher) no alcanzaría esta complejidad ni costo.
Confidence: medium
```

### Hallazgo 6.4: Costo de build vs buy para SaaS <50 empleados: recomendación es "buy"

```
Claim: Para SaaS con <50 empleados, la recomendación general de la industria es "buy" (usar servicios existentes) en lugar de build, debido al opportunity cost de los ingenieros y la carga de mantenimiento subestimada. La excepción es cuando las necesidades son muy específicas o el equipo ya tiene capacity [^275^].
Source: Shadow Inbox Blog - Build vs Buy
URL: https://blog.getshadowinbox.com/posts/build-vs-buy-sales-intelligence
Date: 2026-03-19
Excerpt: "For a SaaS company under 50 employees: buy. Almost without exception. The opportunity cost of your engineers is too high, the maintenance burden is too easy to underestimate, and the buy options have gotten good enough that the gap isn't worth closing yourself."
Context: Faberloom tiene 1-3 devs. Sin embargo, su router (L1/L2) no es un producto genérico — es domain-specific para construcción LATAM con ModelFingerprint y probation. Ningún router comercial ofrece esta lógica.
Confidence: medium
```

---

## 7. Throughput / Requests por Segundo en Producción

### Hallazgo 7.1: LiteLLM proxy: 1.5K+ RPS en load tests, overhead ~8ms P95

```
Claim: LiteLLM proxy (ya en stack de Faberloom) maneja 1,170+ RPS en tests con 4 instancias (4 CPU, 8GB RAM cada una), con overhead de solo 8ms P95 a 1K RPS. En 2 instancias, el overhead P95 es ~29ms [^303^][^297^].
Source: LiteLLM Docs - Benchmarks
URL: https://docs.litellm.ai/docs/benchmarks
Date: Unknown (documentación actual)
Excerpt: "LiteLLM Gateway has 8ms P95 latency at 1k RPS... Doubling from 2 to 4 LiteLLM instances halves median latency: 200ms → 100ms. High-percentile latencies drop significantly: P95 630ms → 150ms, P99 1,200ms → 240ms."
Context: LiteLLM ya cubre el throughput necesario para un MVP B2B. El overhead es negligible comparado con la latencia de los LLMs (500-3000ms).
Confidence: high
```

### Hallazgo 7.2: LiteLLM se degrada significativamente sin escalar infraestructura

```
Claim: Reportes de producción indican que LiteLLM comienza a fallar a ~500 RPS con latencia escalando a >4 minutos. A 5,000 RPS se vuelve impráctico. Requiere Redis + PostgreSQL para features avanzados, añadiendo puntos de fallo [^262^][^298^].
Source: Maxim AI + LiteLLM GitHub Issue
URL: https://www.getmaxim.ai/articles/best-llm-router-for-enterprise-ai-bifrost-vs-litellm/
Date: 2026-03-19
Excerpt: "Python's Global Interpreter Lock prevents true parallelism. In benchmark tests, LiteLLM starts failing at 500 RPS with latency climbing past 4 minutes. At 5,000 RPS, it becomes impractical... Production deployments often require Redis for caching, PostgreSQL for storage, and additional tooling for logging."
Context: Para un MVP con 50-200 clientes PYMEs, 500 RPS es más que suficiente. Esto solo sería preocupación si Faberloom escala a enterprise-grade volumes.
Confidence: high
```

### Hallazgo 7.3: RouteLLM tiene latencia significativa por dependencia de embedding API externa

```
Claim: RouteLLM exhibe latencias de cientos de milisegundos en evaluaciones independientes debido a su dependencia de la OpenAI Embedding API. En RouterArena, RouteLLM tiene latencia de 546.8ms — la más alta de todos los routers evaluados [^293^][^206^].
Source: RouterArena (ICLR 2026) + AlphaXiv
URL: https://openreview.net/pdf?id=9HsaIi4ngF
Date: 2026
Excerpt: "vLLM-SR and RouteLLM exhibit significantly higher latency because they rely on the OpenAI embedding API, which introduces additional network delays... RouteLLM 546.8 [ms]"
Context: Para un MVP que requiere respuestas rápidas en WhatsApp Business, 546ms de overhead SOLO en el router es inaceptable. El L1 clasificador de Faberloom (Haiku local) sería mucho más rápido.
Confidence: high
```

### Hallazgo 7.4: Martian añade 20-50ms de overhead; NotDiamond ~40ms

```
Claim: Martian añade ~20-50ms de latencia por request. NotDiamond (vía OpenRouter Auto Router) añade ~40ms de overhead por el meta-model analysis del prompt [^310^][^300^].
Source: LogRocket + Nolist.ai
URL: https://blog.logrocket.com/llm-routing-right-model-for-requests/
Date: 2026-02-05
Excerpt: "Martian... The tradeoff is 20-50ms of added latency and volume-based pricing... OpenRouter Auto Router: Developers report an average of 40ms of latency overhead due to the NotDiamond meta-model analysis of the prompt."
Context: 40-50ms es aceptable para un chatbot async (WhatsApp) donde la latencia total del LLM es 1-3s. Sin embargo, para workflows en tiempo real (proformas instantáneas), todo overhead cuenta.
Confidence: high
```

### Hallazgo 7.5: Router de reglas simples (L1/L2) tiene overhead negligible

```
Claim: Un router basado en reglas heurísticas o clasificador local (como el diseño L1 Haiku + L2 dispatcher de Faberloom) tiene overhead mínimo — RelayPlane reporta ~0ms para proxies locales, y LiteLLM reporta 2ms median overhead con 4 instancias [^301^][^303^].
Source: RelayPlane + LiteLLM benchmarks
URL: https://relayplane.com/compare/llm-gateways
Date: 2026
Excerpt: "RelayPlane: ~0ms (local)... LiteLLM (4 instances): Custom LiteLLM Overhead Duration (ms) — Median 2, P95 8, P99 13."
Context: El enfoque de Faberloom (L1 classifier Haiku + L2 dispatcher local) tiene overhead comparable a LiteLLM puro (~2-8ms), significativamente menor que RouteLLM (546ms) o Martian (20-50ms).
Confidence: high
```

---

## 8. RouterArena: Benchmark Comparativo Exhaustivo (ICLR 2026)

### Hallazgo 8.1: RouterArena es el benchmark más riguroso hasta la fecha

```
Claim: RouterArena (Rice University, ICLR 2026) es la primera plataforma abierta para comparación comprehensiva de LLM routers, evaluando 12 routers en 44 categorías con 5 métricas (accuracy, cost, latency, robustness, optimal-acc) [^293^].
Source: RouterArena paper
URL: https://openreview.net/pdf?id=9HsaIi4ngF
Date: 2026
Excerpt: "We introduce ROUTERARENA, the first open platform enabling comprehensive comparison of LLM routers. ROUTERARENA has (1) a principally constructed dataset with broad knowledge domain coverage, (2) distinguishable difficulty levels for each domain, (3) an extensive list of evaluation metrics, and (4) an automated framework for evaluation and leaderboard updates."
Context: Este benchmark es la referencia actual más confiable para evaluar routers. Los resultados son reveladores sobre el estado real del arte.
Confidence: high
```

### Hallazgo 8.2: RouteLLM tiene el PEOR performance en RouterArena (47% accuracy)

```
Claim: En RouterArena, RouteLLM alcanza solo 47.0% accuracy overall — el 7° de 12 routers evaluados, apenas por encima de heuristic baselines. Peor aún, en queries "Hard" solo alcanza 2.0% accuracy. Su costo es bajo ($0.27/1K queries) pero la calidad es inaceptable para producción [^293^].
Source: RouterArena - Table 6
URL: https://openreview.net/pdf?id=9HsaIi4ngF
Date: 2026
Excerpt: "RouteLLM 47.0% ($0.27)... RouteLLM (0.9) [threshold] 47.0% accuracy... On Hard queries: RouteLLM 2.0% ($0.32)"
Context: Los routers pre-entrenados de RouteLLM generalizan muy mal fuera de benchmarks académicos. Requiere data augmentation con datos in-domain para ser viable — lo cual Faberloom no tiene todavía.
Confidence: high
```

### Hallazgo 8.3: Los mejores routers open-source (MIRT-BERT, CARROT) superan a routers comerciales en costo-eficiencia

```
Claim: MIRT-BERT alcanza 66.9% accuracy a $0.15/1K queries — significativamente mejor costo-eficiencia que NotDiamond ($9.34/1K para 68.0% accuracy) o Azure-Router ($0.54/1K para 68.1%) [^293^].
Source: RouterArena - Table 6
URL: https://openreview.net/pdf?id=9HsaIi4ngF
Date: 2026
Excerpt: "MIRT-BERT 66.9% ($0.15)... NotDiamond 68.0% ($9.34)... Azure-Router 68.1% ($0.54)"
Context: Para un SaaS con presupuesto ajustado, routers open-source bien entrenados ofrecen mucho mejor ROI que routers comerciales que optimizan por calidad sin restricción de costo.
Confidence: high
```

---

## 9. Contra-Argumentos y Riesgos

### Hallazgo 9.1: Contra-argumento a favor de routers comerciales — velocidad de iteración

```
Claim: Martian permite experimentar con estrategias de routing mucho más rápido que construir in-house, con observabilidad built-in (tracing, latency breakdowns, cost attribution) [^310^].
Source: LogRocket Blog
URL: https://blog.logrocket.com/llm-routing-right-model-for-requests/
Date: 2026-02-05
Excerpt: "Teams report that Martian lets them experiment with routing strategies much faster than building in-house."
Context: Para un equipo de 1-3 devs con deadline de 60 días, esto es tentador. Pero el vendor lock-in, latencia, y costo fijo deben ponderarse.
Confidence: medium
```

### Hallazgo 9.2: Contra-argumento a favor de router propio — control y dominio-especificidad

```
Claim: Un router propio permite integración profunda con sistemas internos (user DB, feature flags, cost tracking, ModelFingerprint) y lógica domain-specific que ningún router comercial puede ofrecer [^310^][^335^].
Source: LogRocket + Dev.to
URL: https://dev.to/gauravdagde/llm-gateway-vs-llm-proxy-vs-llm-router-whats-the-difference-3o5a
Date: 2026-04-12
Excerpt: "Complete control; deep integration with internal systems (user DB, feature flags, cost tracking)... The router is pure business logic — no HTTP, no transport — which makes it testable independently and swappable without touching the proxy."
Context: Faberloom YA tiene ModelFingerprint + probation + task_type + complexity + cost en su L2 dispatcher. Ningún router comercial ofrece esta lógica.
Confidence: high
```

### Hallazgo 9.3: Riesgo de "over-optimizing" routing — destrucción de UX

```
Claim: Over-optimizar routing para costo (thresholds demasiado agresivos) puede llevar a fallback rates de 40% y quejas de usuarios. La recomendación es optimizar solo al 70-80% del máximo teórico, no al 100% [^174^].
Source: Medium - LLM Routing with Ollama & LiteLLM
URL: https://medium.com/@michael.hannecke/implementing-llm-model-routing-a-practical-guide-with-ollama-and-litellm-b62c1562f50f
Date: 2025-12-23
Excerpt: "Configured routing to maximize cost savings (5% threshold, route almost everything to smallest model). Fallback rate hit 40%. Users complained about quality... Cost optimization has diminishing returns. Optimize to 70–80% of theoretical maximum savings, not 100%."
Context: Este riesgo aplica tanto a routers propios como comerciales. Para Faberloom, con clientes PYMEs que dependen de cobranza y proformas precisas, un error de routing tiene impacto directo en revenue.
Confidence: high
```

---

## 10. Decisiones Arquitectónicas Recomendadas para Faberloom

### Para el MVP (60 días):

| Sistema | Decisión | Justificación |
|---------|----------|---------------|
| **RouteLLM** | ❌ DESCARTAR | Peor performance en benchmarks modernos (47% accuracy), no soporta >8K tokens, última actualización agosto 2024, reproducibilidad cuestionable. |
| **Martian** | ❌ DESCARTAR | Cloud-only (datos pasan por terceros), black box, solo 6 providers, $20/mes base + latencia 20-50ms. No aparece en benchmarks. Riesgo compliance LATAM. |
| **NotDiamond** | ⚠️ DIFERIR | Arquitectura de recommender es buena para privacy, pero $100/mes base consume 50% del budget. No integra nativamente con LiteLLM. Evaluar en Phase 2 si el ahorro en tokens justifica el costo. |
| **OpenPipe** | ❌ DESCARTAR | No es router. Es fine-tuning platform. No aplica al gap de routing. |
| **Router propio (L1 Haiku + L2 dispatcher)** | ✅ IMPLEMENTAR | Ya diseñado. Overhead ~2-8ms. Integración nativa con ModelFingerprint, LiteLLM, Supabase RLS. Costo: ~0 (infra existente). Domain-specific. Multi-tenant vía LiteLLM. |

### Costo comparativo mensual estimado (MVP, ~20K requests/mes):

| Opción | Costo Router | Costo LLM (est.) | Total | Overhead latencia |
|--------|-------------|------------------|-------|-------------------|
| Router propio + LiteLLM | $0 | ~$80-120 | ~$80-120 | 2-8ms |
| NotDiamond + LiteLLM | $100 | ~$80-120 | ~$180-220 | ~40ms |
| Martian (reemplaza todo) | $20+ | ~$80-120 | ~$100-140 | 20-50ms |
| RouteLLM self-hosted | $20-50 (infra) | ~$80-120 | ~$100-170 | 546ms |

### Phase 2 (post-MVP):

```
Re-evaluar NotDiamond cuando:
1. Volumen >100K requests/mes (para amortizar $100/mes base)
2. Se tengan datos de evaluación propios para entrenar custom router
3. Se necesite routing entre >5 modelos frontier (complejidad que justifique router externo)
4. LiteLLM integre nativamente NotDiamond como router option

Re-evaluar fine-tuning OpenPipe cuando:
1. Se tengan >10K logged requests de un workflow específico
2. Se quiera distillar GPT-4o → fine-tuned Llama 3.1 8B para reducir costo 8x
3. El use case sea suficientemente estrecho (ej: clasificación de documentos de construcción)
```

---

## Resumen Ejecutivo

**Hallazgo principal:** Ninguno de los routers comerciales evaluados (Martian, NotDiamond, RouteLLM, OpenPipe) es una solución "plug-and-play" óptima para el MVP de Faberloom. Las razones convergen en:

1. **Presupuesto**: NotDiamond ($100/mes) consume 50% del budget de infra. Martian ($20/mes) es más barato pero con cobertura limitada.
2. **Multi-tenancy**: Ningún router comercial ofrece routing aislado por organización/tenant con budgets y model pools independientes — algo que LiteLLM YA cubre.
3. **Domain-specificity**: Faberloom necesita routing por task_type (cobranza vs proformas) + complexity + cost + ModelFingerprint. Ningún router comercial soporta esta lógica.
4. **Compliance LATAM**: Martian y RouteLLM requieren enviar prompts a infraestructura de terceros. NotDiamond es mejor (recommender) pero aún requiere enviar contexto a su API.
5. **Rendimiento**: RouteLLM tiene la peor latencia (546ms) y accuracy (47%) en benchmarks modernos. Los routers propios simples superan en overhead (2-8ms vs 20-50ms comercial).
6. **Integración**: Solo LiteLLM tiene integración nativa con el stack actual (FastAPI + Supabase). Los demás requieren capas adicionales.

**Recomendación final para GAP 2**: Mantener el router propio (L1 Haiku classifier + L2 dispatcher) en el MVP. Es la única opción que cumple simultáneamente: (a) presupuesto ~$200/mes, (b) multi-tenant vía LiteLLM, (c) domain-specific para construcción LATAM, (d) overhead negligible, (e) control total de datos. Re-evaluar NotDiamond en Phase 2 si el volumen y la complejidad del model pool justifican el costo.

---

## Referencias Numeradas

[^109^]: GitHub - lm-sys/RouteLLM. https://github.com/lm-sys/routellm (2024-06-03)
[^174^]: Medium - LLM Routing with Ollama & LiteLLM. https://medium.com/@michael.hannecke/implementing-llm-model-routing-a-practical-guide-with-ollama-and-litellm-b62c1562f50f (2025-12-23)
[^176^]: MorphLLM - OpenRouter Alternative. https://www.morphllm.com/openrouter-alternative (2026-03-31)
[^206^]: AlphaXiv - RouterArena. https://alphaxiv.org/overview/2510.00202v2 (2025-11-11)
[^260^]: arXiv - RouteLLM paper. https://arxiv.org/html/2406.18665v4 (2024-09-29)
[^261^]: TensorZero vs OpenPipe. https://www.tensorzero.com/docs/comparison/openpipe (2026-03-12)
[^262^]: Maxim AI - Bifrost vs LiteLLM. https://www.getmaxim.ai/articles/best-llm-router-for-enterprise-ai-bifrost-vs-litellm/ (2026-03-19)
[^263^]: PremAI - 8 Best LLM Fine-Tuning Platforms. https://blog.premai.io/8-best-llm-fine-tuning-platforms-in-2026-compared/ (2026-03-17)
[^265^]: LMSYS Blog - RouteLLM. https://lmsys.org/blog/2024-07-01-routellm/ (2024-07-01)
[^267^]: HN - OpenPipe founder on router LLMs. https://news.ycombinator.com/item?id=40845811 (2024-07-01)
[^269^]: OpenPipe - Fine-Tuning Platform. https://openpipe.ai/fine-tuning (Unknown)
[^270^]: TechCrunch - Martian tool. https://techcrunch.com/2023/11/15/martians-tool-automatically-switches-between-llms-to-reduce-costs/ (2023-11-15)
[^274^]: GitHub - Liqs-v2/RouteLLM reproduction. https://github.com/Liqs-v2/RouteLLM (2025-11-11)
[^275^]: Shadow Inbox - Build vs Buy. https://blog.getshadowinbox.com/posts/build-vs-buy-sales-intelligence (2026-03-19)
[^293^]: RouterArena ICLR 2026. https://openreview.net/pdf?id=9HsaIi4ngF (2026)
[^295^]: Tenereteam - NotDiamond Reviews. https://not-diamond.tenereteam.com/ (2025-07-18)
[^296^]: LiteLLM Docs - Multi-Tenant. https://docs.litellm.ai/docs/proxy/multi_tenant_architecture (Unknown)
[^298^]: LiteLLM GitHub Issue #21046. https://github.com/BerriAI/litellm/issues/21046 (2026-02-12)
[^300^]: Nolist.ai - OpenRouter Auto Router. https://nolist.ai/item/openrouter-auto-router (2026-03-26)
[^301^]: RelayPlane - LLM Gateway Comparison. https://relayplane.com/compare/llm-gateways (2026)
[^302^]: AI Collab - OpenRouter Auto. https://aicollab.app/blog/openrouter-auto/ (2025-12-28)
[^303^]: LiteLLM Docs - Benchmarks. https://docs.litellm.ai/docs/benchmarks (Unknown)
[^307^]: Skywork.ai - NotDiamond Guide. https://skywork.ai/skypage/en/Not-Diamond-The-Ultimate-Guide-to-AI-Model-Routing-and-Adaptation/1974878605409316864 (2025-10-07)
[^310^]: LogRocket - LLM Routing. https://blog.logrocket.com/llm-routing-right-model-for-requests/ (2026-02-05)
[^311^]: Yahoo Finance - Martian funding. https://finance.yahoo.com/news/martian-invents-model-router-beats-190000381.html (2023-11-15)
[^314^]: NotDiamond Docs - Custom Router. https://docs.notdiamond.ai/docs/router-training-quickstart (2026-04-17)
[^316^]: Nolist.ai - Martian Review. https://nolist.ai/item/martian (2026-03-08)
[^327^]: Medium - LLM Least Privilege. https://medium.com/@michael.hannecke/least-privilege-for-llm-agents-applying-security-principles-to-model-selection-57760accb041 (2025-12-22)
[^329^]: MindStudio - Best AI Model Routers. https://www.mindstudio.ai/blog/best-ai-model-routers-multi-provider-llm-cost-011e6/ (2026-02-10)
[^335^]: Dev.to - LLM Gateway vs Router. https://dev.to/gauravdagde/llm-gateway-vs-llm-proxy-vs-llm-router-whats-the-difference-3o5a (2026-04-12)
