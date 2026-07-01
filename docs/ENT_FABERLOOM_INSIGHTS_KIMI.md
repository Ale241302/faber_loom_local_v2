# ENT_FABERLOOM_INSIGHTS_KIMI — Insights Estratégicos Investigación Kimi
id: ENT_FABERLOOM_INSIGHTS_KIMI
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: ENT
stamp: VIGENTE — 2026-04-17
aprobador: CEO
fuente: Investigación Kimi Swarm — 10 dimensiones, 200+ búsquedas, 11,215 líneas
aplica_a: [FaberLoom]

---

## Declaración

11 insights sistémicos derivados de investigación cruzada sobre arquitectura de agentes,
mercado LATAM B2B, stack técnico y adopción en PYMEs. Cada insight trasciende su dimensión
de origen y tiene implicaciones concretas de diseño.

Confidence: High = validado con benchmarks de producción. Medium = inferido con datos indirectos.

---

## I01 — Paradoja del Cuidador Digital
**Confidence:** High

Las PYMEs B2B LATAM no quieren "agentes autónomos" — quieren un "empleado digital confiable"
que nunca tome una iniciativa sin que ellos la sientan como propia.

**Datos:** 53% prefieren "mostly human-led". 73% de deployments exitosos tienen HITL.
Confidence signaling binario HIGH/LOW supera a porcentajes numéricos en velocidad de decisión.

**Implicación de diseño:** FaberLoom debe implementar "deferencia computada": calcular cuándo
preguntar vs cuándo actuar basado no solo en riesgo sino en UserControlProfile. La autonomía
real del backend puede ser alta; la UX debe simular deferencia constante.

---

## I02 — Efecto Supabase
**Confidence:** High

La elección PostgreSQL + pgvector + RLS no es solo técnica — es un diferenciador de ventas.
RLS permite ofrecer "tu propia base de datos" sin overhead operativo.

**Datos:** 46% de PYMEs LATAM tienen medidas de seguridad mínimas. Multas por brechas
hasta $600K USD (CO/MX/CR/PA). Trust es barrera #1 de adopción.

**Implicación de diseño:** Comunicar como "cada cliente tiene su espacio aislado en nuestra
base de datos" en materiales de ventas. Auditable con SQL estándar. SOC 2 Type I refuerza
esta narrativa.

---

## I03 — Trampa del Gold Sample
**Confidence:** High

La métrica relevante no es accuracy de retrieval — es accuracy de acción. Un gold sample
que recupera correctamente pero produce una acción incorrecta en el contexto actual es
peor que no tenerlo.

**Datos:** AgentMemory V4 (96.2%) y Mastra OM (94.87%) usan arquitecturas radicalmente
diferentes pero ambos optimizan retrieval, no outcome. Mem0: 26% mejora con consolidación
inteligente.

**Implicación de diseño:** OutcomeLedger por cliente (ver SPEC_AUTONOMY_CONTROL_ENGINE v1.1).
Gold samples se evalúan por outcome histórico + drift_score, no solo similitud semántica.

---

## I04 — Oscilador de Confianza
**Confidence:** Medium

La curva de adopción de autonomía no es monotónica. Después de N aprobaciones consecutivas,
el sistema debe reducir autonomía temporalmente para forzar verificación humana.

**Datos:** Prompt injection: 84% tasa de éxito en sistemas agenticos. EchoLeak CVE-2025-32711
(zero-click). Sandbagging detection requiere opportunity set completo, no solo ejecuciones.

**Implicación de diseño:** Oscillation Counter con threshold 20 (ver SPEC_AUTONOMY_CONTROL_ENGINE
v1.1). Previene sandbagging del agente Y complacencia del usuario simultáneamente.

---

## I05 — Ventana LATAM
**Confidence:** High

Existe una ventana de 18-24 meses. El "missing middle" entre chatbots básicos ($9.99/mes)
y enterprise AI ($50-200/empleado/año) no está cubierto en LATAM.

**Datos:** Glean: contratos mínimos $100K/año. Moveworks: $100-200/empleado/año.
90% manufactura colombiana sin digitalización robusta. 70% PYMEs panameñas en Excel/papel.
La ventana se cierra cuando Microsoft Copilot baja precio significativamente o Genspark Claw
añade soporte enterprise serio.

**Implicación de diseño:** Roadmap debe priorizar velocidad sobre perfección. MVP funcional
en manos de clientes beta antes de finalizar Mes 2. Precio $29-39/mes flat.

---

## I06 — Costo Oculto de la Similitud
**Confidence:** Medium

pgvector + RLS activo puede degradar performance 10x-50x con múltiples tenants concurrentes.
El índice HNSW no puede aplicar eficientemente WHERE tenant_id = X antes del ANN search.

**Datos:** pgvector HNSW: <20ms para 1M vectores SIN RLS. Sin benchmarks publicados de
pgvector + RLS + 100+ tenants concurrentes.

**Implicación de diseño:** Hacer benchmark propio antes de comprometerse con la arquitectura.
Si latencia excede 50ms: evaluar Pinecone Serverless (namespace filtering nativo) o índices
separados por cluster de tenants.

---

## I07 — Fragilidad del Stack Ideal
**Confidence:** High

El stack FastAPI + Pydantic AI + ARQ + Mem0 + LiteLLM es "mejor en clase" por componente
pero nunca ha sido probado como stack integrado a escala. 40% de proyectos multi-agente
fallan en 6 meses — mitad por breaking changes en dependencias, no por los modelos.

**Datos:** Pydantic AI: v1.0 (ThoughtWorks). ARQ: 1 mantenedor. Mem0: async default en v1.0.0
fue breaking change reciente.

**Implicación de diseño:** Fijar versiones exactas en poetry.lock. Mantener fork interno de
dependencias críticas. 20-30% del esfuerzo de desarrollo a observabilidad y guardrails desde
día 1 — no como complemento posterior.

---

## I08 — Doblaje de Calibración
**Confidence:** Medium

El Promotion Engine debe calibrar dos cosas simultáneamente: calibración estadística (ECE/Brier)
y calibración perceptual (Human Alignment Score).

**Datos:** LLMs sin recalibración: ECE entre 0.15 y 0.40. Target: ECE < 0.05.
PYMEs LATAM: alta aversión al riesgo financiero (31.4% morosidad promedio, 45-67 días cobro).

**Implicación de diseño:** HumanAlignmentScore (ver SPEC_AUTONOMY_CONTROL_ENGINE v1.1).
Si agente reporta HIGH confidence pero usuario rechaza 30%+ → desajuste perceptual bloquea
promoción aunque ECE sea correcto.

---

## I09 — Patrón del Primer Dólar
**Confidence:** High

El verdadero moat de FaberLoom no es la arquitectura técnica — es la memoria acumulada por
cliente. Cada gold sample, cada UserControlProfile, cada OutcomeEntry crea un activo imposible
de replicar.

**Datos:** Mem0: 26% mejora en accuracy sobre plain vector. 63% empresas colombianas sin
automatizar. Ningún competidor (Glean, Moveworks, Genspark) tiene memoria per-cliente
aprendida con gate humano.

**Implicación de diseño:** El sistema de aprendizaje debe garantizar data portability por
compliance PERO hacer que la reinterpretación contextual de esos datos sea irreplicable.
"Puedes llevarte tus datos, no cómo tu agente los entendía."

---

## I10 — Anomalía del Costo
**Confidence:** High

Prompt caching de Anthropic reduce costos 45-90% para prefijos repetitivos. Hace viable
pricing flat por usuario.

**Datos:** Prompt de 50K tokens × 1,000 usos: $150 sin cache / $15.17 con cache 5min (89.9%
ahorro) / $7.59 con cache + API Batch (94.9% ahorro). Break-even en solo 2 lecturas.

**Implicación de diseño:** Pricing flat $29-39/mes con "uso ilimitado", no por token. El
TokenLedger se usa internamente para optimización, nunca para facturación al cliente.
Cuanto más usa el cliente, más gold samples, más valioso el sistema.

---

## I11 — Silencio de la Manufactura
**Confidence:** Medium

90% de PYMEs manufactureras colombianas sin digitalización robusta. Canal natural: WhatsApp,
no web app. El primer sistema que "hable su idioma" y se integre con WhatsApp tiene oportunidad
de captura de mercado sin precedentes.

**Datos:** 72% consumidores LATAM transaccionan vía mensajería. Soluciones enterprise no
bajan a este segmento por modelo de costos. CAC vía WhatsApp: ~$0.02/mensaje. Referral
orgánico alto en ecosistemas PYME locales.

**Implicación de diseño:** Canal primario = WhatsApp Business API. Onboarding dentro de
WhatsApp, no en web. Consola web solo para configuración y review. Integrar en Fase 1 del
roadmap junto con pipeline de consultas.

---

## Resumen por prioridad de acción

| Insight | Prioridad | Acción inmediata |
|---------|-----------|-----------------|
| I05 Ventana LATAM | Crítica | MVP en 60 días — no perfección |
| I10 Anomalía del Costo | Crítica | Estructurar prompts para caching desde día 1 |
| I11 WhatsApp | Alta | Integrar WhatsApp Business API en Fase 1 |
| I02 Efecto Supabase | Alta | Usar RLS como argumento de ventas desde el pitch |
| I03 Trampa Gold Sample | Alta | OutcomeLedger en v2.2 (ver SPEC_AUTONOMY_CONTROL_ENGINE) |
| I07 Fragilidad Stack | Alta | Fijar versiones, 20-30% esfuerzo a observabilidad |
| I01 Cuidador Digital | Media | UserControlProfile en v2.3 |
| I06 pgvector RLS | Media | Benchmark propio antes de escalar a 100+ tenants |
| I09 Primer Dólar | Media | Comunicar "memoria irreplicable" en pitch |
| I04 Oscilador | Media | Oscillation Counter ya integrado en v1.1 |
| I08 Doblaje Calibración | Media | HumanAlignmentScore ya integrado en v1.1 |

---

Changelog:
- v1.0 (2026-04-17): Creación. 11 i