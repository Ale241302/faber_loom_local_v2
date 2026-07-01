AGENTE 7 — COMPETIDOR / CRITICO
==================

RESUMEN EJECUTIVO
-----------------
FaberLoom apuesta a una combinación defensible en teoría — memoria por cliente con gate humano, aislamiento multi-tenant, audit trail inmutable y voz del firmante — pero la mayoría de sus ventajas están en el papel o aplazadas a E3-E5. Meta, Microsoft/HubSpot y Zoho pueden replicar los componentes superficiales (templates B2B, voz, RAG de catálogo) más rápido de lo que FaberLoom puede construirlos. El verdadero foso, si existe, no es técnico: es la curva de aprendizaje acumulada por cliente bajo aprobación humana. El riesgo central es que la fricción del HITL por output sea incompatible con la escala que necesita un SaaS de $79/mes, y que competidores con datos masivos (Meta vía WhatsApp, Microsoft vía Office/LinkedIn) aprendan el patrón de voz y workflow sin pedir permiso. El precio es vulnerable a freemium; el audit trail es overkill para el ICP de PYME; el moat de gold samples tiene un umbral de falsación real que aún no se ha validado.

---

COMPONENTE: Outcome Ledger + gold samples
-----------------

**Por qué existe:**
La arquitectura parte de la crítica a sistemas que optimizan retrieval en lugar de outcome (I03 — Trampa del Gold Sample). FaberLoom no quiere solo recuperar un documento similar; quiere saber si un gold sample aprobado históricamente sigue produciendo una acción correcta en el contexto actual. OutcomeLedger (SPEC_AUTONOMY_CONTROL_ENGINE v1.2) registra por cada uso de un gold sample si fue aprobado, editado o rechazado, con edit_distance, context_hash y drift_score. Gold samples son outputs aprobados con ≤20% edición (ARCH_AGENT_PRINCIPLES P5, P11) y se convierten en memoria persistente solo tras revisión humana explícita. Es el núcleo de la promesa "cada draft aprobado mejora el siguiente".

**Qué produce como moat:**
Crea un activo acumulativo e irreplicable por tenant: el conjunto de decisiones aprobadas de *esa* empresa con *ese* cliente, en *ese* tono y con *esas* reglas comerciales. ARCH_AGENT_PRINCIPLES P13 lo blinda: ningún output, corrección o gold sample de un tenant puede convertirse en gold sample global de FaberLoom ni alimentar mejoras de producto que beneficien a otros tenants. Esto convierte la memoria en propiedad del cliente, no de la plataforma. La defensa comercial es: "puedes llevarte tus datos, no cómo tu agente los entendía" (I09). Además, GoldSampleHealth detecta degradación y retira samples que ya no sirven, lo que reduce el riesgo de "memoria tóxica".

**Cómo funciona la defensa:**
- P5 (Aprendizaje con gate humano): el output aprobado es solo candidate; la promoción a gold sample requiere confirmación/edición humana.
- P13 (Contención): memoria contenida por tenant y por skill; autonomía no transferible entre orgs.
- OutcomeLedger con RLS por org_id; task_type global para routing, pero org_id nunca es feature de aprendizaje cross-tenant (I-RUFLO-09).
- Umbral de falsación en PLAN_DESARROLLO_v5: si tras N≥10 drafts aprobados del mismo cliente el edit_distance no baja ≥30%, no hay moat y se declara explícitamente.

**Cómo se relaciona con la competencia:**
- OpenAI Memory / Claude Projects: memoria a nivel usuario o proyecto, sin gate humano estructurado y sin outcome tracking.
- Mem0 / Mastra OM: optimizan retrieval, no outcome; sin medición de impacto de negocio.
- Fengu (Sakana Fugu): no tiene equivalente a OutcomeLedger; su routing es opaco y no vincula output a decisión humana posterior.
- Meta: podría construir un ledger si levanta datos de WhatsApp Business, pero no tiene el contrato de aprobación humana por output ni el aislamiento explícito por empresa.
- HubSpot Breeze: tiene datos de CRM pero no gold samples con aprobación humana granular vinculada a un workflow de cotización/cobranza específico.

**Dónde es vulnerable:**
- El moat depende de que el cliente edite/corriga suficiente. Si el usuario aprueba sin leer (complacency) o si el edit_distance nunca baja, no se acumula ventaja.
- Meta o Microsoft podrían replicar el *patrón* de ledger con datos de uso masivo, aunque sin el gate humano de FaberLoom.
- P13 prohíbe global learning, lo cual es éticamente correcto pero limita la velocidad de mejora del producto: FaberLoom no se vuelve más inteligente con más tenants.
- El umbral de falsación (30% reducción de edit_distance) aún no se ha validado; si falla, la narrativa de moat colapsa.

---

COMPONENTE: Multi-tenant isolation
-----------------

**Por qué existe:**
FaberLoom es SaaS multi-tenant para PYMEs B2B LATAM. La barrera #1 de adopción es trust (I02): 46% de PYMEs LATAM tienen medidas de seguridad mínimas y las multas por brechas llegan a $600K USD. La narrativa de ventas es "cada cliente tiene su espacio aislado en nuestra base de datos", auditable con SQL estándar.

**Qué produce como moat:**
- RLS (Row-Level Security) en PostgreSQL como source of truth desde día 1, no como capa agregada.
- Data classification N0-N4 (POL_DATA_CLASSIFICATION) con hard block en Action Engine D9: si data_classification supera el ceiling del plan, no se ejecuta.
- Aislamiento absoluto del aprendizaje (P13): org A nunca ve ni hereda lo aprendido por org B.
- Pre-filtering en retrieval (P13 v1.5): el modelo nunca ve datos que el consultante no está autorizado a ver.
- Step-up authentication para datos propios N2+ (scope=user_self).

**Cómo funciona la defensa:**
- `tenant_id` NOT NULL en toda tabla aislable; tenant fluye vía context, nunca headers de cliente (CLAUDE.md).
- Action Engine D5: multi-tenant first-class; RLS a nivel Engine vía org_context.
- D9: routing por data classification, DPA reconocido, cost-mode opt-in solo para N0/N1.
- Segregación per-tenant del proceso de de-anonimización (sandbox/cgroup/microVM, KEK purga post-request).

**Cómo se relaciona con la competencia:**
- Fengu (Sakana Fugu): sin multi-tenant, RLS, data residency ni DPAs con providers del pool; inusable para N3/N4 (F07).
- OpenAI Workspace Agents: tienen workspace isolation, pero no data classification N0-N4 por país, no DPA chain consolidada y no pre-filtering a nivel retrieval.
- HubSpot/Zoho: multi-tenant maduro, pero el control de data residency/modelo no es granular; no permiten opt-in de providers no-DPA solo para datos no sensibles.
- Microsoft Copilot: vive dentro del tenant Microsoft, con DPA enterprise existente, pero no ofrece "tu propia base de datos" como argumento de ventas a PYMEs sin Office 365 enterprise.

**Dónde es vulnerable:**
- pgvector + RLS puede degradar 10x-50x con múltiples tenants concurrentes (I06); el índice HNSW no aplica eficientemente WHERE tenant_id = X antes del ANN search. Sin benchmark propio, el moat técnico se convierte en cuello de botella.
- Costo de Supabase: ~450K vectores fuerzan 2XL ($410/mes), excediendo presupuesto MVP (I-RUFLO-04).
- Si el cliente objetivo es PYME de 5-50 empleados, RLS y data classification son diferenciadores que el comprador no sabe valorar; vende mejor a enterprise/gobierno que al segmento $79/mes.
- Fengu o Anthropic podrían añadir RLS + data classification en 12-18 meses; el diferencial es temporal, no estructural.

---

COMPONENTE: HITL por output
-----------------

**Por qué existe:**
Las PYMEs B2B LATAM no quieren agentes autónomos; quieren un "empleado digital confiable" que nunca tome una iniciativa sin que ellos la sientan como propia (I01). 53% prefieren "mostly human-led" y 73% de deployments exitosos tienen HITL. La filosofía de producto es "La IA prepara. Vos aportás tu criterio."

**Qué produce como moat:**
- Diferenciación frente a competidores que apuestan a auto-ejecución: Intercom Fin, Microsoft Copilot, HubSpot Breeze.
- Genera señales de aprendizaje estructurado (P6 feedback tipificado: tone, data, structure, policy, scope, context) que alimentan OutcomeLedger y gold samples.
- Cumple con AI Act (supervisión humana obligatoria en usos de alto riesgo) y sectores regulados (HIPAA, FINRA, FDCPA, etc.).
- Señalización HIGH/LOW binaria supera a porcentajes numéricos en velocidad de decisión (I01).

**Cómo funciona la defensa:**
- P3 Draft-first absoluto: ningún agente envía comunicación externa, ejecuta transacciones financieras ni modifica datos de clientes sin aprobación explícita. Invariante de Tier 1, sin excepciones.
- P4 Autonomía por evidencia: el agente sube de nivel solo tras demostrar métricas (approval rate ≥80%, edit-light ≥60%, rejection ≤10%, 14 días estables).
- P14 Deterministic First → LLM Fallback → Human Gate: reduce la superficie donde se necesita HITL.
- Oscillation Counter e HumanAlignmentScore previenen complacencia del usuario y desajuste perceptual.

**Cómo se relaciona con la competencia:**
- Microsoft Copilot / HubSpot Breeze: tienden a auto-ejecutar tareas de bajo riesgo para reducir fricción; su ventaja es velocidad, no deferencia.
- Intercom Fin: resuelve tickets sin intervención humana en casos simples; FaberLoom apuesta a siempre preguntar.
- Meta AI en WhatsApp Business: podría ofrecer respuestas sugeridas con aprobación, pero no tiene state machine de agente ni aprendizaje por corrección tipificada.
- Fengu: sin HITL estructurado; routing opaco.

**Dónde es vulnerable:**
- Fricción real: si un competidor logra 95% accuracy en auto-send, el usuario de FaberLoom sentirá que su producto es lento.
- Complacencia del usuario: aprueba sin leer, generando falsos positivos y gold samples de mala calidad; el Oscillation Counter mitiga pero no elimina el problema.
- WhatsApp Business API limita interacción multi-step (máximo 3 quick replies, 24h sesión), lo que dificulta HITL granular en el canal dominante de LATAM (I-RUFLO-08).
- Un competidor con datos masivos (Meta) puede entregar drafts tan buenos que el HITL se vuelva ritual, no valor.

---

COMPONENTE: Voice profile
-----------------

**Por qué existe:**
El output cliente-facing debe sonar como el dueño de la empresa, no como un chatbot genérico. Voice Profile captura el "sabor" del usuario (tono, saludo, cierre, firma, vocabulario, longitud preferida) y lo aplica como último paso de toda cadena cliente-facing (SPEC_FB_VOICE_HUMANIZER_v2).

**Qué produce como moat:**
- Diferenciación emocional: el cliente siente que habla con *Alejandro* de Marluvas, no con una IA anónima.
- Few-shot de drafts aprobados como mejor señal que cualquier declaración de propiedades.
- Regla inquebrantable: "La voz decide CÓMO decirlo. NO decide QUÉ decir."
- Resolution trace propiedad-por-propiedad (diferido E3+) con auditabilidad de qué capa decidió cada propiedad.

**Cómo funciona la defensa:**
- Voice Humanizer es skill SYSTEM mandatory, último paso de cadena lineal.
- Filtros tenant post-generación (banned phrases + glosario) actúan como guardrails.
- Aprendizaje del sabor user vía HITL signals de Mesa, con tipificación dropdown (tono, saludo, longitud, terminología, etc.).
- Privacidad: `LOC_VOICE_USER_<user_id>.md` es propiedad del user; no comparte cross-tenant sin opt-in.

**Cómo se relaciona con la competencia:**
- Meta: tiene acceso a millones de conversaciones de WhatsApp Business y puede inferir tono empresarial; su escala de datos es inalcanzable para FaberLoom.
- Microsoft Copilot: puede aprender tono de emails y documentos de Office/Outlook; su posición en el flujo de trabajo corporativo es dominante.
- OpenAI custom instructions / Claude Projects: permiten declarar tono, pero no aprenden implícitamente de edits con tipificación.
- HubSpot Breeze / Zoho Zia: tienen asistentes de escritura con tono ajustable, aunque no vinculado a un workflow de cotización/cobranza con aprobación humana.

**Dónde es vulnerable:**
- Voz es superficie, no estructura: fácil de replicar con suficientes datos de conversación. Meta puede hacerlo mejor solo con sus datos.
- La resolución property-by-property está diferida a E3+; en E1-E2 la voz es solo "bloque de estilo + few-shot de gold samples", que es replicable.
- El aprendizaje de voz requiere que el usuario edite muchos drafts; si no hay volumen, el perfil se queda en bootstrap simple.
- Si Meta lanza "Voice Match" para WhatsApp Business gratis, el diferenciador desaparece para el canal principal de LATAM.

---

COMPONENTE: StackLoom L0-L4
-----------------

**Por qué existe:**
StackLoom es la "cola epistémica" (PLAN_DESARROLLO_v5) y se apoya en Knowledge River del Knowledge Atlas (SPEC_FB_KNOWLEDGE_ATLAS_v1): un pipeline de 5 capas que transforma fuentes crudas (L0) en context packs (L1), memoria personal (L2), pool colectivo candidato (L3) y verdad firmada/indexada (L4). Responde al problema de que "cada aprendizaje debe encontrar su lugar correcto en el mapa antes de volverse verdad".

**Qué produce como moat:**
- Distingue conocimiento provisional de conocimiento aprobado; evita que un dato incorrecto se propague org-wide.
- Auto-add sí, auto-promote nunca: solo el humano promueve un candidato a L3/L4.
- Knowledge Atlas como consola operativa del capital intelectual: grafo navegable, impact cascade, change simulator.
- Argumento contra "subir el catálogo a Meta Business AI": FaberLoom no solo indexa documentos, decide qué partes se vuelnen accionables, para quién y con qué riesgo.

**Cómo funciona la defensa:**
- L2 pertenece al usuario; L3 pertenece a la organización; L4 es inmutable.
- Curador/comité revisa candidatos antes de promoción.
- Context Pack Trace permite replay de qué chunks entraron al modelo, qué policy version y qué routing.
- StackLoom se activa solo si ≥30 drafts acumulados (PLAN v5), evitando infraestructura antes de señal.

**Cómo se relaciona con la competencia:**
- Meta Business AI / Workspace Agents: suben catálogo/documentos a un RAG genérico sin curación por capas; no distinguen L0 de L4.
- Notion AI / Glean: tienen KB + retrieval, pero no un pipeline de promoción con comité y firma.
- Fengu: no tiene curación de conocimiento ni data residency.
- Microsoft SharePoint Copilot: accede a documentos empresariales pero no genera "verdad firmada" con cambios versionados e impacto.

**Dónde es vulnerable:**
- StackLoom y L3/L4 están diferidos a E3+; en E1-E2 FaberLoom es esencialmente un RAG con HITL. Meta puede igualar eso con un upload de catálogo + respuestas sugeridas.
- El valor de StackLoom depende de que la organización tenga disciplina de curación; PYMEs de 5-50 empleados no suelen tener un "comité de conocimiento".
- "Subir el catálogo a Meta Business AI" es suficiente para el 80% de casos de consulta de precio/stock; la curación L0-L4 es overkill si el problema es solo responder RFQs.
- Si un competidor ofrece "magic index" que auto-promueve con alta precisión, la deferencia humana de FaberLoom puede parecer burocracia.

---

COMPONENTE: Work-type packs
-----------------

**Por qué existe:**
FaberLoom necesita empaquetar casos de uso B2B recurrentes (RFQ/cotización, cobranza, seguimiento, resumen de cuenta, gobernanza de conocimiento — U1-U5 en ENT_FB_VERTICAL_CANDIDATES_v2) como templates reutilizables. Los archetypes arquitectónicos (Generator, Triage, Validator, Orchestrator, Swarm, Reactive — ENT_FB_AGENT_ARCHETYPES_v1) y los sub-agentes atómicos (ENT_FB_SUB_AGENTS_LIBRARY_v1) permiten componer soluciones por vertical sin recrear lógica desde cero.

**Qué produce como moat:**
- Especialización vertical: el primer foco es distribución B2B técnica (EPP, dieléctrica, ferretería industrial, autopartes), donde MWT tiene derecho a ganar y dataset propio (E0 de Marluvas/Tecmater).
- Compliance profiles per vertical (safety_footwear, chemical_PPE, medical_regulated, etc.) con reglas específicas.
- D17: procesos embebidos, variaciones por cliente resueltas con config en data, no con flows duplicados.
- Golden samples obligatorios para outputs kind:asset; el template mejora con uso.

**Cómo funciona la defensa:**
- SCH_FB_SKILL_MANIFEST_v2 con archetype obligatorio y validaciones específicas por tipo de problema.
- Template Factory / Agent Builder como mismo módulo en v1; separación en v2 cuando haya más tenants.
- Sub-agentes atómicos reutilizables cross-template con pool L3 (draft_writer, email_classifier, compliance_checker).
- Kill criteria per sub-agente (STAY/MERGE/FREEZE/BLOCK_AUTONOMY_PROMOTION) para evitar teatro arquitectónico.

**Cómo se relaciona con la competencia:**
- HubSpot Breeze: ya ofrece templates de workflow de ventas, marketing, servicio al cliente; puede copiar un pack de "cotización B2B" en 6-12 meses.
- Zoho Zia: tiene workflow automation y asistente de escritura; Zoho Creator permite construir apps verticales.
- Microsoft Copilot: con Power Automate y Dynamics 365 puede armar flujos de cotización/cobranza; su ventaja es integración nativa con Office y Outlook.
- Salesforce Einstein + Agentforce: líder en CRM workflow; un pack de "account management B2B" es trivial para ellos.
- Meta: menos fuerte en workflows B2B estructurados, pero WhatsApp Business API + catálogo de productos ya cubre "responder por catálogo".

**Dónde es vulnerable:**
- Los packs de casos de uso son commodity: el problema es genérico y los incumbentes tienen más recursos para construirlos.
- El verdadero moat no es el template, sino el conocimiento del cliente acumulado; sin datos, un pack de "cobranza B2B" no diferencia.
- HubSpot o Zoho pueden comprar o construir compliance profiles verticales si ven tracción en LATAM.
- Si el cliente necesita integración con SAP/ERP, los packs de FaberLoom compiten contra integradores y contra los connectors nativos de Microsoft/Salesforce.

---

COMPONENTE: Audit trail D10
-----------------

**Por qué existe:**
Materializa el requisito de trazabilidad inmutable para sectores regulados (gobierno, banca, salud, educación) y cumple LGPD, Ley 1581 CO, Ley 25.326 AR. Cada llamada al Action Engine genera un AuditEntry con hash chain, policy_version_pinned y replay capability (SPEC_ACTION_ENGINE D10, SPEC_AUDIT_MODULE).

**Qué produce como moat:**
- Diferenciador de ventas a enterprise/government: "podés auditar qué modelo procesó qué dato, con qué policy y qué anonimización".
- Model attribution explícito incluyendo orchestrator_policy_pool_hash cuando el routing es opaco (FG-01).
- Auditor read-only API con MFA + audit-of-audit; attestation reports firmados digitalmente por estándar (ISO 27001, SOC 2, LGPD).
- Storage segregado hot/warm/cold con S3 Object Lock / Azure Immutable Blob.

**Cómo funciona la defensa:**
- D10 cementado en contract API desde v1.0; `audit_id` en ActionResult.
- Hash chain: cada entry hashea la anterior; validación periódica detecta tampering.
- Replay capability reproduce la decisión con la policy version vigente en ese momento.
- Retención configurable per-tenant: 7 años Enterprise, 10+ años Government.

**Cómo se relaciona con la competencia:**
- Fengu: no expone qué modelo procesó qué dato por diseño intencional; bloquea compliance bancario (F08).
- OpenAI/Anthropic: tienen logs y usage dashboards, pero no hash chain inmutable ni attestation reports regulatorios.
- HubSpot/Microsoft: tienen audit logs empresariales maduros, pero no a nivel de modelo/data classification/anonimización.
- Zoho: audit logs estándar, no orientados a sectores regulados ni con model attribution.

**Dónde es vulnerable:**
- El ICP de FaberLoom es PYME B2B a $79/mes; esas empresas no piden audit trail inmutable ni pagan por él. El feature vende a Enterprise/Government, no al wedge inicial.
- Implementación real está en Fase 4-5 (post-MVP), semanas 12-20; antes es principalmente contrato/diseño.
- Costo de storage inmutable a escala; sin clientes Enterprise/Government, es overhead que erosiona márgenes.
- Microsoft/Salesforce pueden añadir hash chain + attestation reports a su tier enterprise si el mercado lo pide; tienen más recursos legales y de compliance.
- En LATAM la madurez de compra de compliance técnico es baja; el vendedor gana por precio/velocidad, no por auditabilidad.

---

COMPONENTE: Precio $79/mes
-----------------

**Por qué existe:**
El pricing intenta ocupar el "missing middle" entre chatbots básicos ($9.99/mes) y enterprise AI ($50-200/empleado/año) en LATAM (I05). Pro $79 incluye Confidencial Add-on (N2), audit detallado, DPA chain y cost-mode opt-in. La tesis es que el valor no es "data en LATAM" sino multi-modelo orquestado, memoria cross-sesión, workflow B2B y compliance (SPEC_FABERLOOM_MVP §Diferenciador competitivo).

**Qué produce como moat:**
- Pricing flat con "uso ilimitado", no por token (I10): prompt caching de Anthropic hace viable el margen.
- Tiers de confidencialidad como producto: Starter/Pro/Enterprise/Government.
- Cost-mode opt-in: permite usar DeepSeek/Kimi self-host para N0/N1, reduciendo costo blended hasta 70%.
- Upsell path: Starter $29 → Pro $79 → Enterprise $299 → Government custom.

**Cómo funciona la defensa:**
- Prompt caching (D11) reduce costos 45-90% para prefijos repetidos; break-even en 2 lecturas.
- Routing multi-LLM por tiers (LIGHT/MEDIUM/EXTREME) optimiza costo-calidad.
- Action Engine D9/D10 aplica políticas de data class y audit; el cliente paga por gobernanza, no solo por tokens.
- Costo blended estimado: conservador ~$25/mes Sonnet equiv; mixto ~$15/mes (40% más barato que Claude.ai); agresivo ~$8/mes (70% más barato).

**Cómo se relaciona con la competencia:**
- ChatGPT Plus / Claude Pro: $20/mes, sin memoria cross-sesión por cliente, sin workflow B2B, sin audit, sin DPA chain consolidada.
- HubSpot Breeze: puede incluirse en el bundle de $20-50/seat; el CAC de PYMEs ya dentro de HubSpot es bajísimo.
- Microsoft Copilot: $30/empleado/mes en Microsoft 365; para una PYME con 5 empleados = $150/mes, pero incluye Office + Teams + Outlook.
- Meta: WhatsApp Business API es gratuito o de bajo costo; Meta puede subsidiar IA con publicidad y ofrecer respuestas sugeridas gratis.
- Zoho: Zia y Zoho One a ~$45/empleado/mes con CRM, email, docs; competitivo en precio total de propiedad.

**Dónde es vulnerable:**
- $79/mes es casi 4x el precio de ChatGPT Plus. Para una PYME latina, eso es significativo sin ROI demostrado en 30 días.
- HubSpot puede lanzar Breeze para workflows B2B en su tier gratuito o de $20/seat, destruyendo la ancla de precio.
- Microsoft puede incluir Copilot agents en Office 365 Business por $10-20 más, aprovechando que ya viven en el flujo de trabajo.
- Meta puede ofrecer un agente de respuestas para WhatsApp Business gratis o a $9.99/mes, atacando el canal principal de LATAM.
- El cost-mode opt-in requiere educar al usuario sobre data classification; la mayoría elegirá default seguro, eliminando la ventaja de precio.
- PLAN_DESARROLLO_v5 propone $39 como ancla para E2.5; la estructura actual de $79 Pro puede ser demasiado alta para validar WTP real.

---

HALLAZGOS PRIORITARIOS
-----------------

**P0 (bloquea):**
1. **El moat de gold samples aún no está validado.** PLAN_DESARROLLO_v5 define un umbral de falsación claro (reducción ≥30% de edit_distance tras N≥10 drafts), pero E2 aún no se ejecuta. Si el dato no confirma el moat, la narrativa competitiva entera se debilita frente a competidores con más datos.
2. **HITL por output vs escala de $79/mes es una tensión insostenible.** El producto apuesta a fricción deliberada, pero el precio requiere valor percibido inmediato. Si Meta o HubSpot ofrecen "borrador aprobado en 1 click" con suficiente precisión, el HITL granular de FaberLoom se siente lento sin compensación clara.
3. **Diferenciadores técnicos clave (StackLoom, audit trail D10, voice property-by-property) están en E3+ o Fase 4-5.** Al momento de vender a los primeros clientes beta, FaberLoom es un RAG con HITL y buen aislamiento — replicable por un competidor con recursos.
4. **El precio $79/mes es vulnerable a freemium.** Meta, HubSpot y Microsoft pueden subsidiar IA con otros ingresos y ofrecer funcionalidad comparable a fracción del precio o gratis.

**P1 (importante):**
1. **Multi-tenant isolation escala mal técnicamente sin validación.** pgvector + RLS tiene riesgo de degradación 10x-50x; el costo de Supabase puede erosionar márgenes antes de los 100 tenants. Se necesita benchmark propio y plan B (Pinecone/Qdrant) antes de comprometer arquitectura.
2. **Voice profile es replicable por Meta/Microsoft con sus datos.** La resolución property-by-property está diferida; en E1-E2 el diferenciador es débil. El canal WhatsApp (dominante en LATAM) es territorio Meta.
3. **Work-type packs son commodity; el foso real es el conocimiento del cliente.** Los templates de cotización/cobranza pueden ser copiados por HubSpot Breeze o Zoho Zia en 12-18 meses. FaberLoom debe acumular datos verticales y compliance profiles más rápido de lo que la competencia pueda imitar.
4. **Audit trail D10 es overkill para el ICP de PYME $79.** Vende a Enterprise/Government, pero el wedge inicial no está ahí. Riesgo de invertir en infraestructura de compliance antes de tener demanda real.

**P2 (mejora):**
1. **P13 (aislamiento absoluto del aprendizaje) limita la mejora del producto.** Es correcto éticamente, pero FaberLoom no se vuelve más inteligente con más tenants. Explorar formas de aprendizaje agregado anónimo (k-anonymity, DP-LoRA federado) sin romper P13.
2. **Canal WhatsApp postergado choquea con el vertical ganador.** ENT_FB_VERTICAL_CANDIDATES_v2 identifica distribución B2B técnica como mejor vertical, pero opera por WhatsApp. PLAN v5 dice "no entra en 2026 salvo trámite Meta cerrado". Esto deja a FaberLoom en email para un vertical que vive en WhatsApp.
3. **Narrativa de "DPA chain consolidada" es abstracta para PYMEs.** Simplificar el mensaje de ventas: no vende "DPA", vende "no mandás precios mal y aprobás antes de enviar".
4. **Competencia directa con Fengu/OpenAI es menor que con Microsoft/HubSpot.** Meta y Microsoft tienen posición de canal y bundle; el análisis competitivo debería ponderar más a estos dos que a startups de agents.
