RUN_ID: KIMI_SWARM_7_ATERRIZAJE_2026-06-12

# D2 - WHATSAPP BUSINESS PLATFORM: ONBOARDING Y COSTOS LATAM (2026)

---

## RESUMEN

Meta migro a modelo de precios **por mensaje entregado** (no por conversacion) el 1 de julio de 2025. El precio depende del **pais del destinatario**, no del remitente: una empresa de Costa Rica enviando a Colombia paga tarifa colombiana ($0.0125 marketing), no la tarifa de CR ($0.0740). El onboarding completo toma **7-14 dias habiles** (Meta verification + BSP setup). Para volumen bajo (~300 msgs/mes), Twilio es el BSP de entrada mas barato (solo markup per-message, sin cuota fija), mientras que Wati ($49/mes) y 360dialog (~$49/mes) incluyen UI. No se encontraron restricciones que impidan a un numero de CR enviar a MX/CO/GT; los unicos paises bloqueados son Crimea, Cuba, Iran, Corea del Norte y Siria. Las service messages (respuestas en ventana 24h) son **gratis ilimitadas** desde noviembre 2024.

---

## HALLAZGOS NUMERADOS

### H1: Modelo de precios vigente 2026 — por mensaje, no por conversacion

1. **El 1 de julio de 2025, Meta depreco el modelo de conversacion y adopto cobro por mensaje de template entregado** [fuente: Landbot Help Center, https://help.landbot.io/article/le7jeofsk0-whats-app-integration-update, 12 Dic 2025, CONF: ALTO — cita documentacion oficial de Meta].
2. **Las service messages (respuestas dentro de la ventana de servicio de 24h) son gratis ilimitadas desde el 1 de noviembre de 2024**; antes solo las primeras 1,000 eran gratis [fuente: SleekFlow Help Center, https://help.sleekflow.io/en_US/whatsapp/pricing, 1 Abr 2026, CONF: ALTO — referencia directa a politica de Meta].
3. **El precio se determina por el pais del destinatario (country code del numero del cliente), NO por la ubicacion del negocio** [fuente: Uptail AI blog, https://www.uptail.ai/blog/whatsapp-business-api-pricing-2026-what-it-costs-and-how-billing-works, 5 Jun 2026, CONF: ALTO — cita documentacion oficial de Meta].
4. **Existe un modelo de subasta "max-price bidding" para mensajes de marketing en rollout durante 2026**, con estimaciones de ahorro del 15-25% para anunciantes que acepten menores tasas de entrega [fuente: SetSmart, https://setsmart.io/blog/whatsapp-business-api-pricing, 20 Abr 2026, CONF: MEDIO — blog de BSP].

### H2: Precios Meta por pais (destinatario) — USD por mensaje entregado, vigentes abril 2026

5. **Colombia**: Marketing $0.0125, Utility $0.0008, Authentication $0.0008, Service: Gratis [fuente: Whautomate tabla de precios completa, https://whautomate.com/whatsapp-business-api-pricing, 1 Abr 2026, CONF: ALTO — datos derivados de rate card oficial de Meta].
6. **Mexico**: Marketing $0.0305, Utility $0.0085, Authentication $0.0085, Service: Gratis [fuente: Whautomate tabla de precios, 1 Abr 2026, CONF: ALTO].
7. **Costa Rica**: Marketing $0.0740, Utility $0.0113, Authentication $0.0113, Service: Gratis [fuente: Whautomate tabla de precios, 1 Abr 2026, CONF: ALTO].
8. **Guatemala**: Marketing $0.0740, Utility $0.0113, Authentication $0.0113, Service: Gratis [fuente: Whautomate tabla de precios, 1 Abr 2026, CONF: ALTO].
9. **Confirmacion cruzada via ManyChat**: Colombia Marketing $0.0144, Utility $0.0009; Mexico Marketing $0.0351, Utility $0.0098 [fuente: ManyChat Help Center, https://help.manychat.com/hc/en-us/articles/14281380243740-WhatsApp-pricing-guide, 1 Abr 2026, CONF: ALTO — BSP oficial].
10. **Nota critica**: Las tarifas difieren ligeramente entre fuentes debido a fechas de actualizacion distintas. Se recomienda verificar siempre la pagina oficial de Meta antes de presupuestar [fuente: Meta WhatsApp Business Platform pricing, https://business.whatsapp.com/products/pricing, consultado Jun 2026, CONF: ALTO].

### H3: Proceso de Business Verification de Meta

11. **Documentos aceptados por Meta**: certificado de constitucion/incorporacion, licencia de negocio, registro fiscal/tributario (VAT/GST), estado de cuenta bancario a nombre de la empresa, factura de servicios (electricidad, agua, internet) [fuente: Brevo Help Center, https://help.brevo.com/hc/en-us/articles/7517984313362, consultado Jun 2026, CONF: ALTO — lista oficial de documentos aceptados por Meta].
12. **Tiempo tipico de verificacion**: 3-10 dias habiles, promedio 4-7 dias; mejor caso 2-5 dias, peor caso hasta 14 dias [fuente: GMCSCO, https://gmcsco.com/whatsapp-business-api-verification-process-2026/, 12 Jun 2026, CONF: MEDIO; confirmado por Reddit r/WhatsappBusinessAPI, https://www.reddit.com/r/WhatsappBusinessAPI/comments/1s2idhc/, 2026, CONF: MEDIO — testimonios de usuarios].
13. **Causas comunes de rechazo**: (a) nombre del negocio inconsistente entre documentos y Business Manager, (b) documentos desactualizados (>3-6 meses), (c) documentos de calidad baja o borrosos, (d) usar documentos personales en vez de empresariales, (e) sitio web inexistente o sin informacion legal, (f) email generico (Gmail/Yahoo) en vez de email corporativo con dominio propio [fuente: ChatArchitect, https://support.chatarchitect.com/books/general-information/page/common-reasons-for-facebook-business-manager-verification-rejection, 16 Abr 2026, CONF: MEDIO; confirmado por Cunnekt, https://www.cunnekt.com/blog/facebook-business-verification-failing.html, 6 Mar 2026, CONF: MEDIO].
14. **Meta verifica en 3 dias habiles como maximo para Meta Verified (badge de pago), pero la Business Verification gratuita puede tomar mas tiempo** [fuente: WhatsApp FAQ oficial, https://faq.whatsapp.com/3872729742954601, consultado Jun 2026, CONF: ALTO].

### H4: Tiempos de aprobacion de templates y display name

15. **Aprobacion de templates**: Tipicamente de 30 minutos a 24 horas. Templates que pasan revision automatica se aprueban en ~15 minutos. Si son marcados para revision humana, toma de 24-48 horas [fuente: WATI Support, https://support.wati.io/en/articles/12320234-understanding-meta-s-latest-updates-on-template-approval, 16 Abr 2026, CONF: MEDIO; confirmado por JestyCRM, https://jestycrm.com/blog/whatsapp-message-template-guidelines-how-to-avoid-meta-rejection, 28 May 2026, CONF: MEDIO].
16. **Aprobacion de display name**: Usualmente 24-72 horas [fuente: Wisemelon, https://wisemelon.ai/blog/whatsapp-display-name-guide, 27 May 2026, CONF: MEDIO].
17. **A partir del 9 de abril de 2025, Meta actualiza automaticamente la categoria del template si detecta un mismatch** (ej: utility que contiene contenido de marketing se reclasifica como marketing y se cobra como tal) [fuente: WATI Support, 16 Abr 2026, CONF: MEDIO].

### H5: Restricciones de numero e internacionalidad

18. **No se encontraron restricciones que impidan a un numero de Costa Rica enviar mensajes de negocio a Mexico, Colombia o Guatemala**. Meta no penaliza por el desajuste entre pais del numero remitente y pais del destinatario [busquedas intentadas: "WhatsApp Business API sender number country different from recipient country restrictions", "WhatsApp Business API international sending number country code sender does not match recipient", "WhatsApp number country code restriction business send internationally penalty quality rating" — ninguna fuente documento restriccion alguna].
19. **Los unicos paises excluidos de WhatsApp Business API son**: Crimea, Cuba, Iran, Corea del Norte y Siria [fuente: AiSensy, https://aisensy.com/tutorials/phone-number-rules-to-apply-for-whatsapp-business-api, consultado Jun 2026, CONF: MEDIO].
20. **El numero de telefono puede ser de cualquier pais**; la restriccion se basa en el numero de WhatsApp del usuario final, no en su ubicacion fisica [fuente: AiSensy, ibid, CONF: MEDIO].

### H6: BSPs — precios y onboarding para volumen bajo

21. **Twilio**: Sin cuota mensual fija; markup de $0.005 por mensaje sobre tarifa Meta. Onboarding: 3-7 dias. Requiere equipo tecnico para desarrollar UI [fuente: EZContact blog, https://ezcontact.ai/en/blog/whatsapp-bsp-comparison/, 19 Abr 2026, CONF: MEDIO; confirmado por Twilio pricing, https://www.twilio.com/en-us/whatsapp/pricing, consultado Jun 2026, CONF: ALTO].
22. **360dialog**: ~$49 USD/mes (€49), sin markup sobre Meta + flat $0.005/msg segun algunas fuentes. Onboarding: 2-5 dias. API-first, sin inbox incluido [fuente: EZContact blog, 19 Abr 2026, CONF: MEDIO; 360dialog docs, https://docs.360dialog.com/partner/get-started/pricing, 5 May 2026, CONF: MEDIO — precios en EUR].
23. **Wati**: $49-$99-$299 USD/mes segun plan. Incluye inbox compartido y chatbot visual. Onboarding: 1-3 dias. Soporte principalmente en ingles [fuente: EZContact blog, 19 Abr 2026, CONF: MEDIO; Sobot blog, https://www.sobot.io/blog/8-best-whatsapp-api-providers-for-businesses-in-2026/, 13 Abr 2026, CONF: MEDIO].
24. **Para volumen bajo (~300 msgs/mes, mix utility/marketing), Twilio es el BSP de entrada mas barato** (~$1.50-6/mes en markup + costo Meta), aunque requiere construir o contratar la interfaz de usuario [fuente: SetSmart blog, 20 Abr 2026, CONF: MEDIO].

### H7: Tier system y limites de mensajeria

25. **Nuevas cuentas no verificadas**: limite de 250 contactos unicos por dia. Tras Business Verification: Tier 1 (1,000/dia), Tier 2 (10,000/dia), Tier 3 (100,000/dia), Unlimited [fuente: Uptail blog, 19 May 2026, CONF: MEDIO — cita documentacion de Meta].
26. **A partir de 2026, Meta evalua cada 6 horas (no cada 24-48h) para ascenso de tier**, permitiendo progresion mas rapida [fuente: Uptail blog, 19 May 2026, CONF: MEDIO].
27. **Los limites de mensajeria son a nivel de Business Portfolio**, no por numero de telefono individual [fuente: Uptail blog, 19 May 2026, CONF: MEDIO — efectivo desde octubre 2025].

---

## TABLA DE DATOS DUROS

### Tabla 1: Tarifas Meta por mensaje entregado (USD) — Abril 2026

| Pais destinatario | Marketing | Utility | Authentication | Service |
|-------------------|-----------|---------|----------------|---------|
| **Colombia** | $0.0125 | $0.0008 | $0.0008 | Gratis* |
| **Mexico** | $0.0305 | $0.0085 | $0.0085 | Gratis* |
| **Costa Rica** | $0.0740 | $0.0113 | $0.0113 | Gratis* |
| **Guatemala** | $0.0740 | $0.0113 | $0.0113 | Gratis* |

\* Service = respuestas dentro de la ventana de 24h despues de que el cliente inicia. Gratis ilimitadas desde Nov 2024.

Fuentes: Whautomate (1 Abr 2026) [CONF: ALTO] + ManyChat (1 Abr 2026) [CONF: ALTO].
Nota: Precios difieren ligeramente entre fuentes por fechas de actualizacion. Usar como referencia.

### Tabla 2: Costo total mensual estimado — 300 conversaciones/mes mixtas (70% utility, 30% marketing)

Escenario: 210 utility + 90 marketing mensuales. Clientes distribuidos: 50% Colombia, 30% Mexico, 20% Guatemala (empresa de CR enviando a esos paises; paga tarifa del destinatario).

| Componente | Calculo | Costo |
|-----------|---------|-------|
| **Meta: Colombia** (105 utility + 45 mkt) | 105 x $0.0008 + 45 x $0.0125 | $0.65 |
| **Meta: Mexico** (63 utility + 27 mkt) | 63 x $0.0085 + 27 x $0.0305 | $1.36 |
| **Meta: Guatemala** (42 utility + 18 mkt) | 42 x $0.0113 + 18 x $0.0740 | $1.81 |
| **Subtotal Meta** | | **$3.82** |
| **Twilio** ($0.005/msg x 300) | | $1.50 |
| **Wati** (plan $49/mes) | | $49.00 |
| **360dialog** (~$49/mes + markup) | | $49.00+ |

| BSP | Costo mensual estimado total | Mejor para |
|-----|---------------------------|------------|
| **Twilio** (solo API, markup per-msg) | ~$5.32 | Equipos tecnicos, volumen muy bajo |
| **Wati** (plan $49/mes + Meta) | ~$52.82 | Equipos no tecnicos que necesitan inbox |
| **360dialog** (~$49/mes + Meta) | ~$52.82+ | Equipos tecnicos que quieren transparencia |
| **API directa (Cloud API sin BSP)** | ~$3.82 | Requiere desarrollar interfaz propia |

Fuentes: calculos propios basados en tarifas Meta + datos BSP de SetSmart/ EZContact/Twilio [CONF: ALTO para tarifas Meta, MEDIO para BSPs].

### Tabla 3: Timeline de onboarding completo

| Fase | Tiempo estimado | Acumulado |
|------|----------------|-----------|
| Preparar documentos y Business Manager | 1-2 dias | Dia 1-2 |
| Meta Business Verification | 3-10 dias habiles (prom 4-7) | Dia 4-12 |
| Crear WABA + verificar numero | 2-5 dias | Dia 6-17 |
| Aprobar display name | 24-72h | Dia 7-19 |
| Crear y aprobar templates (primeros) | 30 min - 24h cada uno | Dia 7-20 |
| **Go-live total** | | **7-20 dias habiles (tipico: 10-15)** |

Fuentes: GMCSCO (12 Jun 2026) [CONF: MEDIO], MyOperator [CONF: MEDIO], GrowthPulse Media (1 May 2026) [CONF: MEDIO].

---

## DATOS NO ENCONTRADOS

- **Restriccion explicita de numero de CR enviando a MX/CO/GT**: Se busco en 4 queries distintas en ingles ("WhatsApp Business API sender number country different from recipient country restrictions", "WhatsApp Business API international sending number country code", "WhatsApp number country code restriction business send internationally penalty quality rating", "WhatsApp Business API phone number country sender recipient different country restrictions"). Ninguna fuente documento restriccion alguna. Las fuentes consultadas indican que el precio se basa en el pais del destinatario, no del remitente, lo que sugiere implicitamente que el envio internacional esta permitido. **INFERENCIA SIN FUENTE DIRECTA: probablemente no hay restriccion**, pero recomendable verificar con Meta directamente antes de comprometerse.

- **Costo exacto de 360dialog para volumen bajo (<1000 msgs/mes)**: La pagina de precios publica planes de partner (€500+/mes), no precios para usuarios finales directos. Se uso estimacion de $49/mes de fuentes secundarias [EZContact, SetSmart].

- **Documentos especificos requeridos para Costa Rica (constitucion de SA, persona juridica)**: No se encontro lista oficial de Meta especifica para Costa Rica. Los documentos genericos aceptados (certificado de constitucion, registro fiscal, factura de servicios) deberian aplicar. Recomendacion: confirmar que la "Personeria Juridica" o "Constitucion de Sociedad Anonima" sea aceptada como "Certificate of Incorporation".

- **Tasa de cambio oficial USD-CRC para facturacion**: Meta soporta 16 monedas de facturacion (USD, EUR, GBP, INR, IDR, MYR, SGD, AED, SAR, ARS, CLP, COP, MXN, PEN, AUD, BRL). **CRC no esta en la lista** [fuente: Whautomate FAQ]. La empresa de CR pagaria en USD.

---

## IMPLICACION OPERATIVA

Para una empresa costarricense vendiendo a PYMEs manufactureras en MX/CO/GT: el costo de mensajeria sera bajo (~$4-7/mes para 300 mensajes mixtos) porque la mayor parte de los destinatarios estan en Colombia y Mexico (tarifas bajas). El cuello de botella no es el costo por mensaje sino el **tiempo de onboarding (10-15 dias habiles)** y la **complejidad tecnica** de integrar el API. Para un piloto manual con 10 prospectos, Twilio ofrece la entrada mas barata; si el equipo no es tecnico, Wati o EZContact son mejores aunque cuesten ~$50/mes. La estrategia deberia maximizar mensajes dentro de la ventana de servicio gratuita (24h) para minimizar costos de template.

---

**Investigacion completada:** 12-Jun-2026  
**Total de busquedas realizadas:** 18 queries independientes en ingles y espanol  
**Fuentes consultadas:** Meta Help Center, WhatsApp FAQ oficial, ManyChat, Twilio, 360dialog, WATI, Whautomate, Uptail, SetSmart, EZContact, SleekFlow, Landbot, ChatArchitect, Cunnekt, Brevo, GMCSCO, Wisemelon, JestyCRM, Reddit r/WhatsappBusinessAPI, blogs de BSPs LATAM.
