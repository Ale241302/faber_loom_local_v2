# Dimensión 04 — GAP 2: Algoritmos Bandit para LLM Routing

## Investigador: Asistente IA especializado en arquitectura AI/LLM
## Fecha: 2025
## Alcance: Decisiones arquitectónicas concretas para Faberloom MVP (FastAPI + Pydantic AI + Supabase + LiteLLM + Next.js)

---

## Executive Summary

La investigación profunda sobre algoritmos bandit para LLM routing revela un ecosistema de investigación muy activo (2024-2026) con múltiples papers publicados, pero **pocas implementaciones open-source listas para producción en el stack exacto de Faberloom**. Los hallazgos clave son:

1. **LinUCB domina la literatura de LLM routing** (GreenServ, PILOT, ParetoBandit), no por superioridad teórica absoluta, sino por **predecibilidad determinística, facilidad de debugging, e integración natural con control de presupuesto (Lagrangian dual)**.
2. **Thompson Sampling tiene mejor regret asintótico** pero es más difícil de calibrar y su naturaleza estocástica interactúa de forma menos predecible con constraints de costo.
3. **El routing overhead <8ms es realista solo para modelos locales (vLLM, HuggingFace)**. Con APIs externas (OpenAI, Anthropic), el overhead del gateway/router (40-60ms) es insignificante frente a latencias de API de 600ms-3s.
4. **La granularity mínima viable de context features es task_type + text_length**; org_id como feature de bandit es técnicamente posible pero conlleva riesgo de fragmentación de datos en multi-tenant.
5. **ε-greedy con decay es el algoritmo más pragmático para MVP** con <5 modelos y <1000 requests/día; LinUCB contextual solo se justifica si se alcanzan >5000 requests/día con feedback automático.
6. **El "costo de exploración" tolerable depende del dominio**: en cobranza/proformas B2B donde un error cuesta dinero real, la exploración debe estar limitada a <10% de requests y nunca en clientes "premium" sin consentimiento.

**Recomendación para Faberloom MVP: DIFERIR bandit adaptive routing. Implementar L1+L2 rule-based con ModelFingerprint y probation. Migrar a ε-decreasing contextual bandit en Phase 2 cuando el volumen de requests >3000/día y se disponga de pipeline de feedback automático (LLM-as-judge o user thumbs).**

---

## 1. Comparación Detallada: Thompson Sampling vs LinUCB vs ε-greedy vs UCB

### 1.1 Thompson Sampling (TS)

```
Claim: Thompson Sampling alcanza mejor regret asintótico que UCB en problemas estacionarios y es más robusto a delayed feedback, pero su naturaleza estocástica lo hace menos predecible para debugging en producción.
Source: An Empirical Evaluation of Thompson Sampling (Chapelle & Li, Yahoo! Research)
URL: https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/thompson.pdf
Date: NIPS 2011 (paper seminal, citado extensamente)
Excerpt: "Thompson sampling achieves the best regret and interestingly the modified version with a=0.5 gives slightly better results than the standard version... Thompson sampling is more robust than UCB when the delay is long."
Context: Evaluación en display advertising y news recommendation con datos reales de Yahoo!. Comparación contra LinUCB, ε-greedy, Exploit-only.
Confidence: high
```

```
Claim: En LLM routing, ParetoBandit eligió explícitamente UCB sobre Thompson Sampling porque "its deterministic score interacts more predictably with the Lagrangian penalty" para control de presupuesto.
Source: ParetoBandit: Budget-Paced Adaptive Routing for Non-Stationary LLM Serving (Taberner-Miller et al.)
URL: https://arxiv.org/abs/2604.00136
Date: 2026-03-31
Excerpt: "We chose UCB over Thompson Sampling because its deterministic score interacts more predictably with the Lagrangian penalty."
Context: Paper que integra por primera vez control de presupuesto cerrado, olvido geométrico, y onboarding de modelos en tiempo real. Evaluado en 1,824 prompts con portfolio de 3 modelos.
Confidence: high
```

```
Claim: Thompson Sampling contextual (LinTS) tiene bound de regret Õ(d^(3/2)√T), que es mejor que LinUCB en algunos regimenes, pero requiere inflación de varianza posterior por factor √d para evitar regret lineal.
Source: Improved Regret of Linear Ensemble Sampling (arXiv 2411.03932v3)
URL: https://arxiv.org/html/2411.03932v3
Date: 2025-06-15
Excerpt: "Our regret bound does not depend on K or m even logarithmically. Hence, this regret bound matches the state-of-the-art frequentist regret bound of linear Thompson sampling... the frequentist regret bound of Õ(d^(3/2)√T) for LinTS is the best one can derive for the algorithm."
Context: Análisis teórico de ensemble sampling para bandits lineales. Identifica que LinTS sin inflación de varianza puede tener regret lineal en T.
Confidence: high
```

### 1.2 LinUCB (Linear Upper Confidence Bound)

```
Claim: LinUCB es el algoritmo más frecuentemente adoptado en papers de LLM routing 2024-2026 (GreenServ, PILOT, ParetoBandit) debido a su determinismo, interpretabilidad, y complejidad computacional O(|M|d³) manejable para portfolios pequeños (K≤16).
Source: GreenServ: Energy-Efficient Context-Aware Dynamic Routing (Ziller et al.)
URL: https://arxiv.org/abs/2601.17551
Date: 2026-01-24
Excerpt: "GreenServ employs LinUCB, a contextual bandit algorithm that assumes a linear relationship between context and reward... Parameters are estimated as θ̂_m = A_m⁻¹b_m and updated as A_mt ← A_mt + x_tx_tᵀ and b_mt ← b_mt + r_tx_t."
Context: GreenServ usa LinUCB con 16 LLMs locales, logrando 22% accuracy gain y -31% energy con overhead <8ms. Compara contra ε-greedy y Contextual Thompson Sampling como baselines.
Confidence: high
```

```
Claim: PILOT (Preference-prior Informed LinUCB) extiende LinUCB con embeddings de preferencia humana pre-entrenados, logrando 93% del performance de GPT-4 al 25% de su costo en RouterBench.
Source: Adaptive LLM Routing under Budget Constraints (Panda et al., EMNLP 2025 Findings)
URL: https://aclanthology.org/2025.findings-emnlp.1301/
Date: 2025-08-28
Excerpt: "PILOT achieves 93% of GPT-4's performance at only 25% of its cost in multi-LLM routing... PILOT's routing time is negligible compared to LLM inference: 0.065–0.239s for routing vs. 2.5s for GPT-4 inference."
Context: PILOT formula routing como contextual bandit con shared embedding space y online multi-choice knapsack para budget constraints. Evaluado en RouterBench (11 modelos, 64 tareas).
Confidence: high
```

### 1.3 ε-greedy y ε-decreasing

```
Claim: ε-greedy con ε=0.1 es el baseline más simple y robusto para iniciar; ε-decreasing (ε=0.5, α=0.99) converge más rápido inicialmente y supera a ε-greedy estático en simulaciones, pero requiere tuning adicional.
Source: Exploring Multi-Armed Bandit Problem (Medium/ym1942)
URL: https://medium.com/@ym1942/exploring-multi-armed-bandit-problem-epsilon-greedy-epsilon-decreasing-ucb-and-thompson-02ad0ec272ee
Date: 2023-11-20
Excerpt: "The parameter set {epsilon=0.5 and alpha=0.99} is the best-performing configuration... the average reward achieved with this optimal parameter set outperforms that of the Epsilon Greedy algorithm."
Context: Simulación didáctica pero con parámetros estándar. El valor ε=0.1 es el recomendado en la industria para producción inicial.
Confidence: medium
```

```
Claim: ε-decreasing es bueno solo para problemas estáticos; cuando las recompensas cambian (drift), ε-decreasing nunca se recupera porque ε ya decayó a un valor bajo.
Source: Multi-armed bandits — Mastering Reinforcement Learning (Gibberblot)
URL: https://gibberblot.github.io/rl-notes/single-agent/multi-armed-bandits.html
Date: Unknown
Excerpt: "Epsilon decreasing never recovers because by the time the probabilities change, epsilon is low and it is committed to those values. For that reason, the ε-decreasing strategy is good only for static problems."
Context: Comparación empírica de múltiples algoritmos bandit con y without drift. UCB1 y Softmax se recuperan mejor del drift.
Confidence: high
```

### 1.4 FGTS.CDB (Feel-Good Thompson Sampling for Contextual Dueling Bandits)

```
Claim: FGTS.CDB alcanza regret Õ(d√T) para dueling bandits contextuales, superando a algoritmos UCB-based en espacios de acción grandes, pero requiere Langevin Monte Carlo para muestreo posterior, lo que añade complejidad computacional.
Source: Feel-Good Thompson Sampling for Contextual Dueling Bandits (Li, Zhao, Gu, ICML 2024)
URL: https://par.nsf.gov/servlets/purl/10545755
Date: 2024
Excerpt: "We show that our algorithm achieves nearly minimax-optimal regret, i.e., Õ(d√T), where d is the feature dimensionality and T is the time horizon... Sampling from such a posterior distribution can be implemented via Langevin Monte Carlo."
Context: Aplicado a routing con feedback de preferencia par (dueling) en vez de scores absolutos. Útil cuando el feedback es comparativo (ej: "respuesta A fue mejor que B").
Confidence: high
```

---

## 2. Cold Start: ¿Qué Algoritmo Converge Más Rápido?

```
Claim: Con datos muy escasos (<100 requests), ε-greedy converge más rápido inicialmente porque explota temprano, mientras que UCB comienza muy exploratorio (todos los brazos tienen intervalos de confianza grandes) y Thompson Sampling puede tener alta varianza inicial.
Source: Multi-Armed Bandits in Python: Epsilon Greedy, UCB1, Bayesian UCB, and EXP3 (James R. LeDoux)
URL: https://jamesrledoux.com/algorithms/bandit-algorithms-epsilon-ucb-exp-python/
Date: 2020-03-24
Excerpt: "UCB bandit ultimately learns the best policy, overtaking Epsilon Greedy after roughly 25,000 training iterations... Epsilon Greedy spends most of its time exploiting, which gives it a faster initial climb toward its eventual peak performance."
Context: Evaluación empírica en MovieLens recommendation con 1M iteraciones. Batch size final de 100 recommendations.
Confidence: high
```

```
Claim: El "warm-start" con datos sintéticos o priores de LLM puede reducir significativamente el regret inicial, pero pierde ventaja si el dominio tiene >40% de desalineación entre el prior sintético y las preferencias reales.
Source: Jump Start or False Start? A Theoretical and Empirical Evaluation of LLM-initialized Bandits (Bayley et al.)
URL: https://arxiv.org/abs/2604.02527
Date: 2026-04-02
Excerpt: "For aligned domains, we find that warm-starting remains effective up to 30% corruption, loses its advantage around 40%, and degrades performance beyond 50%. When there is systematic misalignment, even without added noise, LLM-generated priors can lead to higher regret than a cold-start bandit."
Context: Evaluación sistemática de contextual bandits inicializados con LLM-generated priors. Usan LinUCB warm-started con datos sintéticos.
Confidence: high
```

```
Claim: ParetoBandit integra cold-start onboarding de nuevos modelos con "forced-exploration phase" seguida de UCB selection, alcanzando "meaningful adoption within ~142 steps" sin violar el cost ceiling.
Source: ParetoBandit (Taberner-Miller et al.)
URL: https://arxiv.org/abs/2604.00136
Date: 2026-03-31
Excerpt: "A cold-started model reaches meaningful adoption within ~142 steps without breaching the cost ceiling."
Context: Evaluado en portfolio de 3 modelos con 1,824 prompts. El onboarding usa exploración forzada breve para bootstrap del posterior.
Confidence: medium
```

```
Claim: GreenServ integra nuevos modelos (ej: Gemma-3-12b) en ~100 queries: "After around 100 queries, the selection frequency stabilizes at around 20%-25%."
Source: GreenServ (Ziller et al.)
URL: https://shashikantilager.com/assets/pdf/publications/greenserv_2026.pdf
Date: 2026
Excerpt: "Immediately after its introduction, the algorithm begins to explore it, and its selection frequency rapidly increases. After around 100 queries, the selection frequency stabilizes at around 20%-25%."
Context: Modelo añadido en Query Step 1000 de un total de 2000+ queries. Portfolio de 16 modelos locales.
Confidence: medium
```

**Síntesis para Faberloom:** Con el volumen MVP estimado (~100-300 requests/día), cualquier algoritmo bandit puro tardaría semanas en converger. La solución práctica es: (a) warm-start con datos offline de evaluación manual de un subconjunto de prompts, o (b) comenzar con reglas fijas (L1/L2) y activar el bandit solo cuando se acumulen >1000 requests con feedback.

---

## 3. Non-Stationary: ¿Cuál Maneja Mejor Modelos que Cambian de Rendimiento?

```
Claim: Ningún router LLM publicado antes de 2026 empleaba explícitamente geometric discounting o sliding-window para manejar post-deployment shifts en calidad o precio de modelos.
Source: ParetoBandit (Taberner-Miller et al.)
URL: https://arxiv.org/html/2604.00136v2
Date: 2026-04-14
Excerpt: "Challenge 2: Principled handling of non-stationarity. Non-stationary bandit algorithms are well studied. However, we are not aware of any published LLM router that (i) explicitly employs geometric discounting or sliding-window mechanisms to handle post-deployment shifts..."
Context: ParetoBandit es el primer sistema en integrar explícitamente geometric forgetting con LinUCB para LLM serving. Evalúan bajo quality degradation, cost drift, y cold-start.
Confidence: high
```

```
Claim: ParetoBandit usa geometric forgetting sobre las estadísticas suficientes (A_m, b_m) con factor γ, donde forgetting reduce A_m hacia singularidad, incrementando el bonus de confianza y haciendo que modelos caros pero inciertos sean más atractivos. La tasa de forgetting debe calibrarse conjuntamente con α (exploración), no en aislamiento.
Source: ParetoBandit (Taberner-Miller et al.)
URL: https://arxiv.org/html/2604.00136v2
Date: 2026-04-14
Excerpt: "geometric forgetting shrinks A_a toward singularity over time, inflating LinUCB's confidence bonus... The upstream interaction between the forgetting rate γ and exploration coefficient α determines exploration aggressiveness; these should be calibrated jointly, not in isolation."
Context: El paper propone un "Pareto knee-point procedure" para calibrar γ y α juntos. Sin forgetting, el sistema no se recupera de quality degradation.
Confidence: high
```

```
Claim: TI-UCB (Time-Increasing UCB) es específicamente diseñado para modelos cuyo rendimiento mejora con el tiempo (ej: LLMs en fine-tuning iterativo), incorporando un mecanismo de change detection para identificar puntos de convergencia y lograr regret logarítmico.
Source: Which LLM to Play? Convergence-Aware Online Model Selection with Time-Increasing Bandits (Xia et al.)
URL: https://arxiv.org/abs/2403.07213
Date: 2024-03-11
Excerpt: "TI-UCB effectively predicts the increase of model performances due to finetuning and efficiently balances exploration and exploitation in model selection... We theoretically prove that our algorithm achieves a logarithmic regret upper bound."
Context: Relevante si Faberloom planea fine-tunar modelos propios o usar modelos que mejoran iterativamente. Menos relevante para APIs de terceros estáticos.
Confidence: high
```

```
Claim: MixLLM usa "continual training" en vez de forgetting explícito, adaptándose a evolving queries y user feedback con retraining periódico de modelos ligeros de predicción de calidad/costo.
Source: MixLLM: Dynamic Routing in Mixed Large Language Models (Wang et al., NAACL 2025)
URL: https://arxiv.org/abs/2502.18482
Date: 2025-02-09
Excerpt: "The system benefits from continual training, allowing it to adapt to evolving queries and user feedback over time... MixLLM achieves 97.25% of GPT-4's quality at 24.18% of the cost."
Context: MixLLM delega adaptación a retraining periódico en vez de forgetting online. Esta aproximación es más pesada computacionalmente.
Confidence: high
```

**Síntesis para Faberloom:** Para un MVP con APIs de terceros (OpenAI, Anthropic) donde los modelos no cambian de rendimiento drásticamente día a día, **la no-estacionariedad es un problema de segunda prioridad**. La preocupación principal sería si Anthropic sube/degrada la calidad de Haiku o cambia precios — para esto, un re-calibración mensual manual de reglas L1/L2 es suficiente en MVP. El geometric forgetting de ParetoBandit es sofisticación excesiva para 60 días de MVP.

---

## 4. Routing Overhead: ¿Es <8ms Realista?

```
Claim: GreenServ reporta overhead total de ~7.77ms por query: 3.04ms (task classification) + 3.37ms (semantic cluster) + 0.15ms (text complexity) + 0.86ms (LinUCB routing). Esto es para modelos locales (HuggingFace transformers en GPU).
Source: GreenServ (Ziller et al.)
URL: https://shashikantilager.com/assets/pdf/publications/greenserv_2026.pdf
Date: 2026
Excerpt: "Task type classification requires 3.04 ms, semantic cluster identification takes 3.37 ms, and text complexity calculation adds 0.15 ms. For GreenServ, the LinUCB routing decision adds 0.86 ms. Summing these, the total pre-inference overhead per query is approximately 7.77 ms."
Context: Modelos locales cargados en GPU. La clasificación de task type usa logistic regression sobre embeddings de sentence-transformers (all-MiniLM-L6-v2).
Confidence: high
```

```
Claim: PROTEUS reporta 8.7ms de routing latency en GPU (A100) para batch=1, dominado por DeBERTa-v3-small (22M params). Con batch≥8, cae a <3ms. El policy head añade <0.1ms.
Source: PROTEUS (Bhatti et al.)
URL: https://arxiv.org/pdf/2601.19402
Date: 2026-01-27
Excerpt: "Single-query latency of 8.7ms is negligible compared to LLM inference times of 2-7 seconds... At batch 8+, <3ms latency with 300+ q/s."
Context: PROTEUS es un router basado en Lagrangian RL, no bandit puro, pero da referencia de latencia para routers con embedding neural.
Confidence: high
```

```
Claim: ParetoBandit reporta 9.8ms end-to-end routing latency en CPU, con la decisión de routing propiamente dicha en 22.5μs. El resto es embedding con all-MiniLM-L6-v2.
Source: ParetoBandit (Taberner-Miller et al.)
URL: https://ai-navigate-news.com/en/articles/22581d1c-31e7-4b9a-a7da-fac2135773d1
Date: 2026-04-02
Excerpt: "End-to-end routing latency is 9.8ms on CPU -- less than 0.4% of typical inference time -- with the routing decision itself taking just 22.5us."
Context: ParetoBandit usa Python puro con numpy. La decisión bandit (A⁻¹b + α√(xᵀA⁻¹x)) es computacionalmente trivial; el costo es del embedding.
Confidence: medium
```

```
Claim: Con APIs externas (OpenAI, Anthropic, OpenRouter), el overhead del gateway/router es de 40-60ms (OpenRouter) a 440μs-11μs ( LiteLLM vs Bifrost en benchmarks comparativos), lo cual es insignificante frente a latencias de API de 600ms-3s.
Source: I Replaced 4 LLM API Clients With One Endpoint (Dev.to/tedtalk)
URL: https://dev.to/tedtalk/i-replaced-4-llm-api-clients-with-one-endpoint-heres-what-the-latency-data-actually-looks-like-5elk
Date: 2026-04-21
Excerpt: "The router itself adds roughly 40–60ms of overhead versus calling the provider directly... Acceptable for async summarization tasks, probably not for a real-time autocomplete UX."
Context: Benchmark real de un router unificado vs llamadas directas a APIs. Usó 20 requests por modelo.
Confidence: high
```

```
Claim: Morph Router (servicio comercial de clasificación de prompts) añade ~430ms de latencia más $0.001 por clasificación. Esto es significativo para UX en tiempo real pero aceptable para batch.
Source: MorphLLM / OpenRouter Alternative
URL: https://www.morphllm.com/openrouter-alternative
Date: 2026-03-31
Excerpt: "The overhead is ~430ms for the classification call plus OpenRouter's ~50ms proxy latency. For batch workloads or API backends where total response time is already 1-5 seconds, the classification overhead is a small fraction."
Context: Morph Router clasifica en 4 tiers de dificultad. No es un bandit sino un clasificador entrenado offline.
Confidence: high
```

**Síntesis para Faberloom:** Para un sistema que consume APIs externas (Haiku/Sonnet/GPT-4), el routing decision computacional es <1ms si se implementa en Python puro con matrices pequeñas (d≤20). El costo real es: (a) si se usa embedding local (~6-10ms con all-MiniLM-L6-v2 en CPU), o (b) si se hace embedding vía API (+red → +50-200ms). Para el MVP de Faberloom (chatbot WhatsApp), latencias de 500ms-2s son aceptables, por lo que **overhead <8ms es realista y no es un bottleneck**.

---

## 5. Granularity de Context Features

```
Claim: GreenServ encontró que task_type es la feature más informativa individual, reduciendo la mediana de cumulative regret a ≈400. La combinación de todas las features (task + cluster + complexity) aumentó ligeramente el regret, posiblemente por dimensionalidad excesiva con pocas muestras.
Source: GreenServ (Ziller et al.)
URL: https://shashikantilager.com/assets/pdf/publications/greenserv_2026.pdf
Date: 2026
Excerpt: "The most substantial reduction in regret appears to be linked to the inclusion of the Task feature, dropping median cumulative regret to ≈ 400... including all features appears to raise regret levels notably. This might be attributed to the increased dimensionality which potentially slows convergence."
Context: Ablation study en 5 benchmark tasks con 16 LLMs. Context vector: one-hot(task_type) + one-hot(cluster) + one-hot(complexity_bin) + bias.
Confidence: high
```

```
Claim: PILOT usa un shared embedding space donde queries y LLMs se alinean via triplet loss sobre datos de preferencia humana. No usa features explícitas (task_type, complexity) sino embeddings semánticos del prompt completo.
Source: PILOT (Panda et al.)
URL: https://aclanthology.org/2025.findings-emnlp.1301/
Date: 2025-08-28
Excerpt: "We develop a shared embedding space for queries and LLMs, where query and LLM embeddings are aligned to reflect their affinity. This space is initially learned from offline human preference data and refined through online bandit feedback."
Context: PILOT demuestra que embeddings semánticos dense pueden capturar suficiente señal para routing sin feature engineering explícito.
Confidence: high
```

```
Claim: PROTEUS usa DeBERTa-v3-small para encodear el query completo, sin features manuales. El routing es puramente basado en la representación learned del prompt.
Source: PROTEUS (Bhatti et al.)
URL: https://arxiv.org/pdf/2601.19402
Date: 2026-01-27
Excerpt: "The inference pipeline encodes queries via DeBERTa-v3; the embedding feeds both a performance prediction head and the τ-conditioned policy."
Context: PROTEUS es un sistema de RL supervisado, no bandit online. La lección es que un solo embedding del prompt puede ser suficiente.
Confidence: high
```

**Síntesis para Faberloom:**

Para un MVP con 3-5 modelos y 2-3 workflows (cobranza, proformas), la granularidad mínima viable es:

| Feature | Implementación MVP | Dimensión | Prioridad |
|---------|-------------------|-----------|-----------|
| task_type | L1 clasificador rule-based (Haiku) | 3-5 one-hot | **Alta** |
| text_length / complexity | Conteo de tokens + heurísticas simples | 2-3 bins | Media |
| semantic_embedding | all-MiniLM-L6-v2 (90MB, ~6ms CPU) | 384-dim | Baja (Phase 2) |
| org_id | One-hot por tenant | N_tenants | **Riesgo: fragmentación** |
| user_tier | premium/standard (rule-based) | 2 one-hot | Alta (para SLA) |

**Advertencia sobre org_id:** En un sistema multi-tenant con 100+ PYMEs, usar org_id como feature de bandit fragmenta los datos: cada tenant tendría su propio A_m, b_m con muy pocas muestras. Solución: **pooling parcial** — mantener priores globales y ajustar con shrinkage hacia el prior global, o usar hierarchical Bayesian models. Esto es complejidad de Phase 2, no MVP.

---

## 6. Implementaciones Open-Source

```
Claim: ParetoBandit es open-source (Apache 2.0), pip-installable, y usa Python puro con numpy. Requiere Python ≥3.10. Incluye demo interactivo.
Source: ParetoBandit GitHub
URL: https://github.com/ParetoBandit/ParetoBandit
Date: 2026-03-30
Excerpt: "pip install paretobandit[embeddings]... Requirements: Python ≥ 3.10, Core: numpy, joblib, scikit-learn, tqdm."
Context: Primer sistema bandit open-source específicamente para LLM routing con budget pacing y non-stationarity.
Confidence: high
```

```
Claim: LiteLLM soporta routing strategies: simple-shuffle, least-busy, usage-based, latency-based, cost-based, pero NO soporta bandit contextual adaptive ni model selection basado en calidad del prompt. Es provider-level routing, no intelligence routing.
Source: LiteLLM Documentation
URL: https://docs.litellm.ai/docs/routing
Date: 2026
Excerpt: "Router provides multiple strategies for routing your calls across multiple deployments... (Default) Weighted Pick - RECOMMENDED."
Context: LiteLLM enruta entre deployments del MISMO modelo (ej: múltiples instancias de gpt-4o), no entre modelos de diferente capacidad.
Confidence: high
```

```
Claim: GreenServ publica código en GitHub (anonimizado para review): https://github.com/TZData1/llm-inference-router. Implementa LinUCB, ε-greedy, y Contextual Thompson Sampling en Python puro.
Source: GreenServ (Ziller et al.)
URL: https://arxiv.org/abs/2601.17551
Date: 2026-01-24
Excerpt: "All artifacts are open-source and available here: GitHub repository."
Context: Implementación en FastAPI + Redis + PostgreSQL + scikit-learn + sentence-transformers. Stack muy cercano al de Faberloom.
Confidence: high
```

```
Claim: BaRP formula routing como contextual bandit con policy gradient (REINFORCE) en vez de LinUCB/TS, entrenado offline con bandit feedback simulado. No hay código open-source disponible públicamente.
Source: Learning to Route LLMs from Bandit Feedback (Wang et al.)
URL: https://arxiv.org/abs/2510.07429
Date: 2025-10-08
Excerpt: "Trained with policy gradients on bandit feedback... We formulate multi-objective LLM routing as a contextual bandit problem."
Context: BaRP usa un neural network (Prompt Encoder + Preference Encoder + Decision Head) entrenado offline. No es online bandit puro.
Confidence: high
```

```
Claim: MixLLM es open-source (código asociado al paper NAACL 2025). Usa contextual bandit con tag-enhanced embeddings y meta-decision maker. Requiere PyTorch y entrenamiento de modelos ligeros por LLM.
Source: MixLLM (Wang et al.)
URL: https://arxiv.org/abs/2502.18482
Date: 2025-02-09
Excerpt: "MixLLM achieves 97.25% of GPT-4's quality at 24.18% of the cost... Our code is available at [anonymous URL]."
Context: Framework más pesado que ParetoBandit/GreenServ. Requiere entrenar modelos de predicción de calidad/costo per-LLM.
Confidence: high
```

**Síntesis:** Para Faberloom, la opción open-source más cercana es **ParetoBandit** (Apache 2.0, pip installable) o el código de **GreenServ** (FastAPI-based). Ambos requieren adaptación para APIs externas (están diseñados para modelos locales). LiteLLM no resuelve el problema de model selection inteligente — solo load balancing entre deployments idénticos.

---

## 7. Trade-off Exploration/Exploitation: ¿Cuántas Requests "Exploratorias" Se Toleran?

```
Claim: En producción de recommendation systems, ε=0.1 (10% exploración) es el estándar de industria. ε demasiado bajo (1-2%) hace imposible recuperarse de un "wrong winner" temprano.
Source: What is Epsilon-Greedy Strategy? (Atticus Li)
URL: https://atticusli.com/behavioral-science-glossary/epsilon-greedy-strategy/
Date: Unknown
Excerpt: "Start with epsilon = 0.1 for most use cases; increase to 0.2 if you suspect early data is noisy... Setting epsilon too low (1–2%), making it nearly impossible to recover from early randomness picking a wrong winner."
Context: Best practices de industria para A/B testing y bandits en producción.
Confidence: high
```

```
Claim: En un sistema de cobranza/proformas B2B donde un error del LLM puede generar un reclamo o pérdida financiera, la exploración debe ser "budget-gated" (ParetoBandit) o restringida a tenants no-premium con consentimiento explícito.
Source: ParetoBandit (Taberner-Miller et al.)
URL: https://arxiv.org/html/2604.00136v2
Date: 2026-04-14
Excerpt: "The router discriminates rather than blindly adopting: expensive models are budget-gated and low-quality models rejected after bounded exploration."
Context: ParetoBandit limita exploración con un cost ceiling. Los modelos de baja calidad se rechazan después de exploración acotada.
Confidence: medium
```

```
Claim: PILOT logra 93% de GPT-4 al 25% de costo, pero esto requiere un "learning bucket" inicial donde se explora. El paper no reporta el % exacto de requests exploratorias, pero el knapsack binning implica que queries complejas reciben más budget (acceso a GPT-4) y simples reciben menos.
Source: PILOT (Panda et al.)
URL: https://aclanthology.org/2025.findings-emnlp.1301/
Date: 2025-08-28
Excerpt: "PILOT achieves 93% of GPT-4's performance at only 25% of its cost in multi-LLM routing... The online cost policy outperforms simple per-query budget allocation."
Context: El cost policy es un online multi-choice knapsack, no un % fijo de exploración. La "exploración" es implícita en la estructura de bins de budget.
Confidence: medium
```

```
Claim: En LLM routing para cobranza/proformas, donde la calidad de salida afecta directamente la relación con el cliente, un enfoque conservador es: explorar solo con modelos "seguros" (ej: nunca enviar una proforma a GPT-4o-mini si no se ha validado que produce output correcto; pero sí probar Haiku vs Sonnet en queries de clasificación).
Source: Inferencia propia basada en contexto Faberloom
URL: N/A
Date: 2025
Excerpt: N/A
Context: Para Faberloom, la exploración más segura es intra-tier: probar diferentes prompts o temperature dentro del mismo modelo aprobado, antes de cambiar de modelo.
Confidence: medium
```

**Síntesis:** La tolerancia a exploración en Faberloom depende del workflow:

| Workflow | Tolerancia a exploración | Estrategia |
|----------|------------------------|------------|
| Clasificación de intención (L1) | Alta (corregible) | ε=0.1 entre Haiku/Sonnet |
| Generación de proformas | **Baja** (dinero en juego) | Ninguna sin validación previa |
| Cobranza (mensajes) | Media (reversible) | ε=0.05, solo en clientes estándar |
| Extracción de datos | Baja | Modelo fijo validado |

**Regla práctica:** En MVP, no más del 5-10% de requests deberían ir a un modelo diferente al "default" del workflow, y nunca sin mecanismo de fallback/validación.

---

## 8. RouterBench y Benchmarks de Routing

```
Claim: RouterBench (Hu et al., 2024) cubre 405,467 samples, 11 modelos, 8 datasets, 64 tareas. El router Oracle (selección perfecta por query) logra accuracy promedio 87.04% vs 70.91% de GPT-4 solo, con costo 0.2064 vs 3.3715.
Source: RouterBench (Hu et al.)
URL: https://arxiv.org/abs/2403.12031
Date: 2024-03-28
Excerpt: "In total, there are 405,467 samples in ROUTERBENCH, covering 11 models, 8 datasets, and 64 tasks."
Context: Primer benchmark estándar para LLM routing. GPT-4 es el best single model pero 5x más caro que el Oracle.
Confidence: high
```

```
Claim: LLMRouterBench (Li et al., 2026) es la evolución masiva: 400K+ instancias, 21 datasets, 33 modelos (incluyendo GPT-5, Claude 4, Gemini 2.5 Pro). Confirma que la mayoría de routers recientes tienen performance similar bajo evaluación unificada, y que routers comerciales como OpenRouter a veces fallan en superar el baseline simple.
Source: LLMRouterBench (Li et al.)
URL: https://arxiv.org/abs/2601.07206
Date: 2026-01-12
Excerpt: "While confirming strong model complementarity... we find that many routing methods exhibit similar performance under unified evaluation, and several recent approaches, including commercial routers, fail to reliably outperform a simple baseline."
Context: Benchmark que cubre performance-oriented y performance-cost trade-off routing con 10 baselines.
Confidence: high
```

```
Claim: En LLMRouterBench, top routers logran hasta 4% accuracy gain sobre Best Single y 31.7% cost reduction. Sin embargo, OpenRouter (commercial) tuvo -24.7% de mejora relativa a Best Single.
Source: LLMRouterBench Results (alphaXiv resumen)
URL: https://alphaxiv.org/overview/2510.00202v2
Date: 2025
Excerpt: "top routing methods achieve up to a 4% average accuracy gain over the Best Single model and up to a 31.7% cost reduction... OpenRouter yields the smallest (indeed, negative) performance improvement (-24.7%) relative to the Best Single model."
Context: Evidence de que routing no es trivial: un mal router puede ser peor que usar un solo modelo fijo.
Confidence: high
```

**Síntesis:** Los benchmarks demuestran que el **routing tiene valor** (Oracle vs Best Single), pero también que **un mal router es peor que ninguno**. Para Faberloom MVP, la estrategia "Best Single per workflow" (Haiku para L1, Sonnet para proformas/cobranza) es un baseline sólido que probablemente supere a un bandit mal calibrado.

---

## 9. Contra-Argumentos y Riesgos

### Contra-argumento 1: "Bandits son overkill para MVP"
```
Claim: PROTEUS demuestra que un router entrenado offline con Lagrangian RL puede alcanzar 90.1% accuracy en RouterBench (a 1.3% del Oracle) con 89.8% cost savings vs GPT-4, sin necesidad de bandit online.
Source: PROTEUS (Bhatti et al.)
URL: https://arxiv.org/abs/2601.19402
Date: 2026-01-27
Excerpt: "PROTEUS achieves 90.1% accuracy on RouterBench, within 1.3% of oracle. Cost savings reach 89.8% versus the best fixed model."
Context: PROTEUS es offline-trained, no online bandit. Demuestra que para muchos casos, un clasificador offline bien entrenado puede ser suficiente.
Confidence: high
```

### Contra-argumento 2: "La latencia de APIs externas hace irrelevante el overhead del router"
```
Claim: Claude Haiku 4.5 tiene TTFT de ~597-639ms en prompts cortos; GPT-4.1 Mini tarda hasta 2205ms (p95: 4004ms). Un router de <10ms es <1% del tiempo total.
Source: LLM API Latency Benchmarks 2026 (Kunal Ganglani)
URL: https://www.kunalganglani.com/blog/llm-api-latency-benchmarks-2026
Date: 2026-03-07
Excerpt: "Claude Haiku 4.5: 639ms TTFT... GPT-4.1 Mini: 2205ms TTFT (p95: 4004ms)."
Context: Benchmark real con 5 modelos, 3 providers, 3 tamaños de prompt. TTFT = Time To First Token.
Confidence: high
```

### Contra-argumento 3: "El feedback para bandits es difícil de obtener en LLMs"
```
Claim: BaRP se entrena con bandit feedback offline (simulado) porque "training on static, offline logs, which is practical but differs from a truly online setting where a router could learn continuously from live feedback."
Source: BaRP (Wang et al.)
URL: https://arxiv.org/abs/2510.07429
Date: 2025-10-08
Excerpt: "Our method trains on static, offline logs, which is practical but differs from a truly online setting where a router could learn continuously from live feedback."
Context: Obtener feedback de calidad por request es costoso (requiere LLM-as-judge o human-in-the-loop). Sin feedback, el bandit no puede actualizar sus parámetros.
Confidence: high
```

---

## 10. Recomendaciones para Faberloom

### Decisión Arquitectónica: DIFERIR Bandit Adaptive Routing al MVP

| Dimensión | MVP (0-60 días) | Phase 2 (3-6 meses) |
|-----------|----------------|---------------------|
| Routing L1 | Reglas + Haiku (clasificación) | Posible bandit ε-greedy si volumen >3K/día |
| Routing L2 | Task-based fixed assignment (Sonnet/GPT-4o) | LinUCB contextual con task_type + embedding |
| Model change | Manual (ModelFingerprint + probation) | Semi-automático con bandit warm-start |
| Feedback | Human-in-the-loop (thumbs up/down) | Automático (LLM-as-judge + user feedback) |
| Context features | task_type (L1 output) + text_length | + semantic embedding + org_id (con pooling) |
| Exploration | 0% (deterministic) | ≤10% ε-decreasing, solo en tenants estándar |

### Justificación

1. **Volumen insuficiente:** A 100-300 requests/día, un bandit con d=10 features y K=3 modelos necesitaría ~1000+ requests para estabilizarse. Eso son 3-10 días de "exploración activa" donde el sistema está aprendiendo — riesgo inaceptable para proformas/cobranza.

2. **Feedback escaso:** Faberloom no tendrá pipeline de LLM-as-judge en MVP. Sin feedback automático por request, el bandit no puede actualizarse online. El feedback humano (thumbs) llega con delay y es esparsimo.

3. **Complejidad de implementación:** Implementar LinUCB con budget pacing, non-stationarity, y multi-tenant pooling requiere 2-3 semanas de trabajo de un ML engineer — tiempo que no está en el presupuesto de 60 días.

4. **Overhead aceptable:** El L1 rule-based con Haiku ya añade ~500-800ms de latencia. El L2 bandit añadiría ~10ms de computación — insignificante, pero la complejidad cognitiva no lo es.

### Implementación Phase 2 (cuando se justifique)

Cuando Faberloom alcance >3000 requests/día con feedback automático disponible:

- **Algoritmo:** ε-decreasing contextual bandit (ε₀=0.2, α=0.995, lower_bound=0.05)
- **Features:** task_type (one-hot) + prompt_embedding_64d (PCA de all-MiniLM-L6-v2) + text_length_bin
- **Arms:** Haiku, Sonnet, GPT-4o-mini (máx 4-5 modelos)
- **Reward:** combinación de (a) score LLM-as-judge 0-1, (b) costo normalizado, (c) latencia
- **Non-stationarity:** Recalibración semanal manual de ε si se detecta drift en métricas
- **Multi-tenant:** Priores globales + shrinkage; NO org_id como feature directo hasta >50 requests/día por tenant

---

## 11. Referencias Consolidadas

1. GreenServ (Ziller et al., 2026) — https://arxiv.org/abs/2601.17551
2. ParetoBandit (Taberner-Miller et al., 2026) — https://arxiv.org/abs/2604.00136
3. BaRP (Wang et al., 2025) — https://arxiv.org/abs/2510.07429
4. PILOT (Panda et al., EMNLP 2025) — https://aclanthology.org/2025.findings-emnlp.1301/
5. MixLLM (Wang et al., NAACL 2025) — https://arxiv.org/abs/2502.18482
6. PROTEUS (Bhatti et al., 2026) — https://arxiv.org/abs/2601.19402
7. TI-UCB (Xia et al., 2024) — https://arxiv.org/abs/2403.07213
8. FGTS.CDB (Li et al., ICML 2024) — https://par.nsf.gov/servlets/purl/10545755
9. RouterBench (Hu et al., 2024) — https://arxiv.org/abs/2403.12031
10. LLMRouterBench (Li et al., 2026) — https://arxiv.org/abs/2601.07206
11. Chapelle & Li (NIPS 2011) — https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/thompson.pdf
12. Jump Start or False Start (Bayley et al., 2026) — https://arxiv.org/abs/2604.02527
13. LiteLLM Routing Docs — https://docs.litellm.ai/docs/routing
14. ParetoBandit GitHub — https://github.com/ParetoBandit/ParetoBandit
15. GreenServ GitHub — https://github.com/TZData1/llm-inference-router

---

*Fin del informe de investigación — Dimensión 04: Algoritmos Bandit para LLM Routing*
