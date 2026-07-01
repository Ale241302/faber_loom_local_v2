# AGENTE 6 — PRODUCT MANAGER
## Auditoría de decisiones de producto · FaberLoom Foundation Beta

---

## RESUMEN EJECUTIVO

FaberLoom tiene una base sólida: HITL absoluto, arquitectura de agentes disciplinada, wedge real (MWT/Marluvas) y un plan de 13 semanas con kill conditions claras. Desde la óptica de PM, el riesgo principal no es técnico — es de **priorización y validación comercial**. Hay una tensión entre construir una *foundation beta* configurable y validar un único workflow cliente-facing. Métricas como VCT y kill conditions miden adopción y calidad, pero no miden directamente **disposición a pagar ni generalización del wedge**. El adapter pattern y los work-type packs son arquitectónicamente coherentes, pero en E1 solo se ejercitan con cotización safety footwear; el riesgo de over-engineering es real si no se prueba un segundo tipo de trabajo antes de S13.

---

## COMPONENTE 1 — Wedge safety footwear: es el trabajo más repetitivo y doloroso

**Por qué se tomó esta decisión:**
MWT ya opera como distribuidor B2B de calzado de seguridad (Marluvas/Tecmater). El dolor es real y medible: RFQs técnicos con normas ASTM, variantes de talla/ancho/puntera, listas de precios y clientes multi-país. Es el dataset más rico disponible sin costo de adquisición. La tesis de R3 fue: "MWT es adapter del sistema, no el core" — el core es la disciplina spec-to-quote, no el calzado.

**Qué produce:**
Un caso de uso angosto, repetable y de alto volumen para validar el loop: entrada → clasificación → retrieval → generación de cotización → HITL → envío. Sirve como golden seed para el KB y para gold samples.

**Cómo se mide:**
- VCT = RFQs enviados sin edición material humana y sin errores de auditoría / total RFQs reales en scope beta.
- Edit rate < 40% (kill ≥ 60%).
- ≥4/5 testers usan sin insistencia CEO durante 4 semanas consecutivas.
- ≥50 RFQs reales acumulados a semana 6.

**Cómo se relaciona con el roadmap:**
Es el único workflow cliente-facing validado en E1 (Foundation Beta). E2/E3 habilitan otros workflows (cobranza, seguimiento) y el segundo vertical (distribución B2B técnica adyacente). Si el wedge no valida, el resto del roadmap pierde base.

**Qué hipótesis crítica NO está siendo validada en E1:**
> ¿Es el wedge *transferible* a otros tenants B2B no vinculados a MWT, o es un caso de dolor específico de la operación propia?

E1 valida que MWT coticé más rápido; no valida que un distribuidor de EPP químico, ferretería o autopartes *adopte* el mismo flujo con el mismo dolor. El plan propone testers amigos, pero no un protocolo de medición de dolor por vertical.

---

## COMPONENTE 2 — HITL como diferenciador: los usuarios lo valoran o lo toleran

**Por qué se tomó esta decisión:**
Filosofía de producto: "La IA prepara. Vos aportás tu criterio." ARCH_AGENT_PRINCIPLES P3 establece draft-first absoluto como invariante. La propuesta de valor frente a ChatGPT/Claude puro es que FaberLoom no envía nada sin aprobación, reduce errores comerciales graves y deja traza de auditoría.

**Qué produce:**
Confianza, reducción de errores severos, compliance (evidencia de decisión humana), y un mecanismo de aprendizaje estructurado: cada aprobación/rechazo/corrección alimenta gold samples y skill refinement.

**Cómo se mide:**
- 0 incidentes privacy/irreversibles.
- % aprobado sin edits ≥ 60% (últimas 30).
- Tiempo de aprobación (login→draft aprobado < 2 min en desktop; aprobación móvil ≤ 45s).
- Adopción sin insistencia CEO (métrica de salida TIER 1 #12).

**Cómo se relaciona con el roadmap:**
HITL es permanente. P4 permite subir autonomía en acciones internas, pero P3 veta envío externo autónomo en todos los niveles. El diferenciador no es "sin humano", sino "humano informado y rápido".

**Qué hipótesis crítica NO está siendo validada en E1:**
> ¿Los usuarios *pagarían* por HITL, o lo toleran porque aún no confían en la IA y lo harían gratis con Claude+Gmail?

No hay experimento que contraste HITL obligatorio vs. auto-send selectivo de bajo riesgo. Si los drafts son buenos, HITL puede sentirse fricción; si son malos, HITL puede sentirse revisión doble. No se mide "willingness to pay por el gate".

---

## COMPONENTE 3 — Work-type packs: el adapter pattern es real o es over-engineering

**Por qué se tomó esta decisión:**
Para evitar que FaberLoom quede overfit a MWT, se diseñó `vertical_spec_object` (adapter pattern) que parametriza normas técnicas, variantes dimensionales, certificaciones, compatibilidad y glosario por vertical. Junto con los `architectural_archetype` (Generator, Triage, Validator, Orchestrator, Swarm, Reactive, Skill_package), busca empaquetar tipos de trabajo reutilizables.

**Qué produce:**
Separación entre core universal (spec-to-quote discipline) y dominio específico (safety footwear, EPP químico, MRO). Permite clonar skills/agentes por vertical sin reescribir el motor.

**Cómo se mide:**
- Factory adoption: ≥2/3 tenants amigos crean ≥1 agente o skill custom.
- Tiempo para añadir un nuevo skill/arquetipo.
- Edit rate y VCT por tipo de trabajo.

**Cómo se relaciona con el roadmap:**
E1 construye las factories y el spec object con un solo workflow. E2+ prueba composición jerárquica, tools, y un segundo vertical. El adapter pattern solo paga dividendos si hay ≥2 verticales reales.

**Qué hipótesis crítica NO está siendo validada en E1:**
> ¿Un segundo tipo de trabajo (cobranza, seguimiento, o una vertical distinta a safety footwear) puede configurarse con el adapter pattern sin reescribir código?

En E1 el único workflow validado es cotización safety footwear. No hay tenant que use work-type packs distintos. El adapter pattern puede ser arquitectónicamente correcto pero no validado empíricamente; corre riesgo de ser un costo upfront que no se justifica con el volumen de E1.

---

## COMPONENTE 4 — VCT como métrica: es la métrica correcta para semana 6

**Por qué se tomó esta decisión:**
VCT (Verified Commercial Throughput) conecta actividad del sistema con valor comercial real: RFQs que salen sin edición material y pasan auditoría el mismo día. Evita maquillar con actividad ("100 drafts generados") si no se convierten en outputs comerciales enviados.

**Qué produce:**
Foco en calidad operativa y velocidad. Unifica edit rate, errores severos y throughput en una sola métrica orientada al negocio.

**Cómo se mide:**
VCT = RFQs enviados sin edición material humana y sin errores de auditoría mismo día / total RFQs reales en scope beta.
Meta semana 6: VCT ≥ 30% en ≥ 3 tenants, ≥ 50 RFQs reales, 0 errores severos.

**Cómo se relaciona con el roadmap:**
Es la métrica de salida de E1. Si se cumple, demuestra que el loop comercial funciona con supervisión humana reducida. Si no, se activan kill conditions.

**Qué hipótesis crítica NO está siendo validada en E1:**
> ¿VCT predice retención, pago y product-market fit, o solo predice eficiencia operativa?

Un VCT alto puede significar que los drafts son buenos, pero no que el cliente renueve o pague $79/mes. No hay métrica de salida E1 que vincule VCT con WTP, churn o LOI. La validación comercial (E2.5) corre en paralelo pero no es parte del gate E1.

---

## COMPONENTE 5 — 8 kill conditions: son las condiciones correctas o hay una que falta

**Por qué se tomó esta decisión:**
El plan firmado define 8 kill conditions para evitar el síndrome de "una semana más". Cubren adopción, calidad, costo, incidentes, ROI, disponibilidad y factory adoption. Son relativas al inicio real de cada etapa (corrección de v4/v5).

**Qué produce:**
Disciplina de pivoteo/kill. Evita seguir invirtiendo en un producto que no resuelve dolor real o que no es económicamente viable.

**Cómo se mide:**
Las 8 kill conditions del PLB_FB_FOUNDATION_BETA_v1 son:
1. <3/5 testers ≥3 tareas/sem en sem 6 → no resuelve dolor real.
2. <3/5 testers sin insistencia CEO 4 sem consecutivas → señal "amistad", no fit.
3. Edit rate sostenido ≥60% últimas 30 → modelo no genera drafts útiles.
4. Costo medio >USD 1.00/tarea con caching → economía rota.
5. ≥1 incidente privacy o irreversible → riesgo regulatorio supera valor.
6. Reducción tiempo ≤2x auto-reportado → no hay ROI.
7. Disponibilidad <85% en S10-S11 → arquitectura falla bajo uso real.
8. Cero tenants amigos crearon agente o skill custom → factories no resuelven necesidad real.

**Cómo se relaciona con el roadmap:**
Son los guardrails de Foundation Beta. Si se dispara alguna, se congela/replanta antes de E2/E3.

**Qué hipótesis crítica NO está siendo validada en E1:**
> ¿Qué pasa si los testers usan mucho el producto pero ninguno pagaría por él?

Ninguna de las 8 kill conditions mide directamente **intención de pago, LOI o WTP**. El plan v5 endureció E2.5 a "pago recurrente ≥2 ciclos o LOI firmado", pero eso es gate E2.5, no kill condition de E1. Si Foundation Beta termina con alto VCT y alta adopción pero cero pagos, el kill no se habrá disparado y se tomará la decisión E3 con sesgo de supervivencia.

---

## COMPONENTE 6 — Canales (WhatsApp vs Telegram vs web): la asimetría es correcta

**Por qué se tomó esta decisión:**
El plan original prioriza WhatsApp Business API directo (Meta) + Gmail OAuth/IMAP/SMTP custom + Resend fallback. WhatsApp tiene 72% de penetración en LATAM y es el canal dominante del vertical ideal (distribución B2B técnica). Telegram aparece solo como fallback técnico descartado en favor de consola web + copia manual. Web es la Mesa de Control/Workspace.

**Qué produce:**
Cobertura multi-canal nativa: entrada por email/WhatsApp, revisión y aprobación en web/Mesa, salida por el canal origen del tenant.

**Cómo se mide:**
- % de RFQs por canal (email vs WhatsApp vs webform).
- Latencia P95 inbound→pending < 12s.
- Disponibilidad ≥ 95%.
- % outbound vía Resend < 5% mensual.

**Cómo se relaciona con el roadmap:**
E1 implementa WhatsApp + email. E2+ añade Outlook, webforms, APIs. La asimetría refleja el canal real del mercado objetivo.

**Qué hipótesis crítica NO está siendo validada en E1:**
> ¿Los RFQs B2B de los testers reales llegan principalmente por WhatsApp, o por email/web?

La investigación de verticales (ENT_FB_VERTICAL_CANDIDATES_v2) señala que la distribución B2B técnica opera por WhatsApp, pero el plan v5/PLB E-5 propone empezar E1-E2 con email-only y dejar WhatsApp para E3 mientras el trámite Meta corre en paralelo. Esa tensión no está resuelta: si el dolor vive en WhatsApp, validar con email-only subestima el dolor real y puede dar falso positivo de product-market fit.

---

## COMPONENTE 7 — $79/mes: es el precio correcto para el pain que resuelve

**Por qué se tomó esta decisión:**
El pricing propone Starter $19-29, Pro $59-89 (con Confidencial add-on), Enterprise $249-399, Government custom. $79 es el punto medio del Pro, posicionado vs. Claude/ChatGPT Plus ($20/mes) como diferenciador por HITL, memoria cross-sesión, workflow B2B, DPA chain y cost-mode opt-in.

**Qué produce:**
Una ancla de precio para E2.5 y un modelo de upsell por tier de confidencialidad/add-ons. El Pro targetea 30% de conversión desde Starter.

**Cómo se mide:**
- WTP medido en concierge E2.5 (ancla $39, banda $30-50 según Kimi Swarm 7).
- % Starter → Pro upsell.
- Pago recurrente ≥2 ciclos o LOI firmado.
- Costo IA por tarea aprobada < USD 0.50.

**Cómo se relaciona con el roadmap:**
Pricing es input para E3/E4b (multi-tenant externo con design partners pagos). Si el WTP real está por debajo de $79, el modelo de negocio se rompe antes de escalar.

**Qué hipótesis crítica NO está siendo validada en E1:**
> ¿El ahorro de tiempo y reducción de errores que genera FaberLoom vale $79/mes para una PYME B2B latinoamericana?

El documento ENT_FB_PRICING_TIERS_v1.0 admite explícitamente: "Pricing propuesto sin validación de mercado". La meta de VCT mide eficiencia, no WTP. El concierge E2.5 usará ancla $39 (según Kimi Swarm 7), lo que sugiere que $79 puede ser optimista para el segmento inicial. No hay evidencia de que el dolor resuelto (cotización RFQ) justifique 2-4x el precio de un asistente humano virtual básico en LATAM.

---

## COMPONENTE 8 — Foundation Beta 13 semanas: es suficiente tiempo para invalidar o validar

**Por qué se tomó esta decisión:**
El plan evita tanto la "beta inicial mínima" de 8 semanas (insuficiente para foundation) como un producto completo de 16+ semanas (ya no es MVP). 13 semanas permiten construir la base configurable (multi-email, multi-usuario, Voice Profile, factories, resiliencia) y validar un workflow.

**Qué produce:**
Un sistema interno real con 5 testers, RLS, HITL, audit, factories minimal y resiliencia C. Si valida, la base arquitectónica para E2-E5 está lista.

**Cómo se mide:**
- Gate de salida E1: ≥4/5 testers ≥10 tareas en sem 6; ≥4/5 sin insistencia CEO 4 sem; ≥60% aprobados sin edits; costo <USD 0.50/tarea; 0 incidentes; ≥5x reducción tiempo; disponibilidad ≥95%; ≥2/3 tenants amigos crearon agente/skill custom.

**Cómo se relaciona con el roadmap:**
Foundation Beta es F1 del roadmap extendido. E2 habilita segundo workflow y composición; E3 workspaces; E4 multi-tenant externo condicional a E2.5.

**Qué hipótesis crítica NO está siendo validada en E1:**
> ¿13 semanas bastan para validar *product-market fit*, o solo para validar *product-technical fit*?

Con un solo workflow y 5 testers, 13 semanas pueden validar que el sistema técnico funciona y que MWT lo usa. Pero no dan tiempo para observar churn, renovación, WTP real, segundo vertical, ni efecto de red del aprendizaje. E2.5 (concierge) intenta medir PMF en paralelo, pero no es parte del scope de build ni del gate E1. El riesgo es declarar "Foundation Beta exitosa" basándose en métricas técnicas mientras la hipótesis comercial sigue sin validar.

---

## HALLAZGOS PRIORITARIOS

### P0 (bloquea)

1. **VCT mide eficiencia, no PMF.** La métrica clave de E1 no está vinculada a pago, renovación ni LOI. Si se cumplen 30% VCT y 50 RFQs pero ningún tester paga, Foundation Beta puede ser técnicamente exitosa y comercialmente inviable.
2. **Las kill conditions no incluyen WTP/pago.** Falta una kill condition del tipo: "<X% de testers amigos o prospectos E2.5 con intención de pago verificada a $Y/mes". Sin esto, el equipo no tiene mandato para matar el proyecto por falta de mercado.
3. **Tensión de canal no resuelta.** El vertical ideal opera por WhatsApp (ENT_FB_VERTICAL_CANDIDATES_v2), pero el plan reciente (PLB E-5 / BUILD_SEQUENCE v3) propone email-first E1-E2. Validar con el canal equivocado puede producir falso positivo.

### P1 (importante)

4. **Adapter pattern no ejercitado.** `vertical_spec_object` y `architectural_archetype` son elegantes, pero E1 solo los usa para cotización safety footwear. Se debería forzar un segundo work-type pack (cobranza o seguimiento) antes de S13 para probar que el adapter no es over-engineering.
5. **HITL como diferenciador no está cuantificado.** No hay experimento ni métrica que mida si los usuarios valoran el gate o lo perciben como fricción. Se recomienda medir "tiempo extra por HITL" vs. "percepción de confianza" en survey.
6. **Pricing sin validación de mercado.** $79 Pro es una hipótesis. El concierge E2.5 debería testear anclas $29/$39/$59/$79 para tener curva de demanda antes de fijar tiers.

### P2 (mejora)

7. **Factory adoption es proxy débil de valor.** Que 2/3 tenants creen un skill custom no garantiza que lo usen en producción ni que resuelva dolor. Se podría complementar con "días con uso real del skill custom" o "VCT atribuible a skills custom".
8. **Meta de disponibilidad 95% puede ser baja para B2B comercial.** Para cotizaciones con SLA implícito de "mismo día", 95% permite ~7h/mes de downtime. Evaluar si el target debería ser 99% en S11-S12.
9. **Falta métrica de aprendizaje.** El moat de FaberLoom es que cada draft aprobado mejora el siguiente, pero no hay métrica de salida E1 que muestre que `edit_distance` baja con el uso (ver moat con umbral de falsificación en PLAN_DESARROLLO_FABERLOOM_v5 §6.2).

---

*Reporte generado por Agente 6 — Product Manager · 2026-06-24*
*Fuente: KB canónico C:\dev\mwt-knowledge-hub*
