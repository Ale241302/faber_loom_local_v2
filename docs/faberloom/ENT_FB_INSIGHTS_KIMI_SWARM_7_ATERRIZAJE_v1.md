# ENT_FB_INSIGHTS_KIMI_SWARM_7 - Investigacion operativa de aterrizaje (OAuth, WhatsApp, legal, identidad, pricing, inferencia)

id: ENT_FB_INSIGHTS_KIMI_SWARM_7_ATERRIZAJE_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: ENT
stamp: VIGENTE -- 2026-06-13 -- destilado de KIMI_SWARM_7_ATERRIZAJE_2026-06-12 (6 dimensiones, 80+ fuentes, 136 citas). Crudos en docs/anexos/kimi_swarm_7/
aprobador: CEO (Alvaro)
aplica_a: [FaberLoom, MWT]
relacionado: SPEC_FB_BUILD_SEQUENCE v2.1 - PLB_FB_FOUNDATION_BETA v1.3.2 - SCH_FB_CORE_TABLES v1 - AUDIT_FB_MODULAR_2026-06-11

---

## A. Proposito

Hechos externos verificados (junio 2026) que cierran las investigaciones D1-D6 del
plan de aterrizaje, CON su impacto en decisiones ya tomadas. Cada hecho cita fuente
en los crudos (anexos/kimi_swarm_7/). Confianza ALTA salvo nota.

## B. Impacto en decisiones - lo que CAMBIA

| # | Hecho | Decision afectada | Accion |
|---|---|---|---|
| 1 | Enviar desde buzon propio NO requiere verificacion Google: SMTP+app password (5 min, 2FA, vigente jun 2026) o Service Account+DWD con Workspace (30 min). gmail.readonly = scope RESTRICTED = CASA Tier 2 ($540-6,000) + 1-3 meses | PLB E-5 (canales) | Piloto E1-E2: SMTP/DWD para outbound, IMAP app-password para inbound de buzones PROPIOS. PROHIBIDO cualquier scope restricted. La investigacion "lead time OAuth" queda CERRADA: no se necesita |
| 2 | WhatsApp API: service messages (ventana 24h) GRATIS ilimitadas desde nov 2024; 300 msgs/mes mixtos = ~$5/mes via Twilio. Onboarding Meta: 10-15 dias | E3 + skill cobranza | Iniciar business verification Meta YA (es gratis, corre sola). Disenar cobranza para responder DENTRO de ventana 24h (costo cero). Twilio para piloto tecnico |
| 3 | Legal por pais: GT sin ley vigente; CR Ley 8968 (clausulas o consentimiento); CO Ley 1581 PERO datos corporativos puros ESCAPAN del ambito (concepto SIC 23-571469/2024); MX nueva LFPDPPP mar-2025 exige contrato de encargado, sancion hasta $1.8M; BR exige SCCs ANPD | E2.5 concierge + E3 | Concierge: priorizar prospectos CR + GT + CO (datos corporativos). MX requiere contrato de encargado ANTES de cliente pago mexicano -> abogado. Checklist minimo piloto: aviso privacidad + consentimiento simple + DPA Anthropic. TODO requiere validacion abogado local |
| 4 | CRMs maduros (HubSpot/Zendesk/Front/Attio) usan exactamente nuestro patron: dominio exacto + lista freemail excluida (HubSpot: 4,746 dominios) + triage manual para bordes (subdominios, multi-cuenta). Nadie resuelve elegante los bordes | SCH_FB_CORE_TABLES (entity resolution) | Las 6 reglas quedan VALIDADAS por la industria. Accion nueva: importar lista freemail publica como seed de dominios genericos en client_map (S2) |
| 5 | Banda USD 30-50/mes esta poblada: Chately $39, CRMWhata $39, Zoko $40, Cliengo $45. 54% PYMEs LATAM ya usa IA (Microsoft 2025); churn driver = soporte deficiente y costos ocultos, NO precio | E2.5 pricing prueba | Ancla del concierge: $39/mes (centro de banda). La diferenciacion se demuestra en 14-30 dias o se pierde. Transparencia de costos de mensajes = argumento anti-churn |
| 6 | Caching Anthropic: read 0.1x, write 5min 1.25x (break-even 2da lectura), min 1,024 tokens, max 4 breakpoints, TTL renueva con hit. Surcharge >200K tokens DUPLICA input. Tokenizer Opus 4.7+ produce hasta +35% tokens. Tier 4 = $400 acumulados | PLB E-6 (retrieval contexto-first) + savings_ledger | E-6 VALIDADA con numeros oficiales. Regla nueva: context packs <200K tokens SIEMPRE (el surcharge mata el ahorro). Baseline del ledger debe usar el tokenizer del modelo medido (+35% Opus). Subir a Tier 4 temprano: $400 |

## C. Hechos de referencia rapida (precios jun 2026, fuente oficial Anthropic)

| Modelo | Input/Output MTok | Context | Cache read |
|---|---|---|---|
| Haiku 4.5 | $1 / $5 | 200K | $0.10 |
| Sonnet 4.6 | $3 / $15 | 1M | $0.30 |
| Opus 4.8 | $5 / $25 | 1M | $0.50 |
| Fable 5 | $10 / $50 | 1M | $1.00 |

Batch API: -50% adicional, SLA 24h. Tiers por deposito acumulado: $5/$40/$200/$400.
Degradacion contexto largo: efecto observable desde 300-400K (Chroma 2025); Opus mantiene >=80% multi-hop hasta 512K (arxiv 2026-05).

## D. Conflictos entre fuentes (NO resueltos - no presupuestar sobre ellos)

1. Verificacion Google sensitive: oficial 3-5 dias vs realidad 2-8 semanas. (Irrelevante si se evita OAuth de terceros.)
2. Tokens en "production sin verificar": mayoria reporta longevos, hay excepciones. (Evitado por diseno.)
3. Precios Meta WhatsApp: variacion 15% entre BSPs -> verificar pagina oficial Meta antes de presupuestar.
4. CASA Tier 2: $540 a $6,000 segun lab. TAC Security = opcion economica documentada.
5. Leadsales: $84 vs $97-133 segun fuente.

## E. Investigaciones cerradas / abiertas

CERRADAS por este swarm: lead time OAuth (evitable), costos WhatsApp, marco legal piloto, validacion entity resolution, mapa de precios, economia caching (valida E-6).
SIGUEN ABIERTAS (requieren datos internos, E1 sem 2): pricing computable desde KB, eval set retrieval, cobertura Tier 0, golden corpus chat. Y la madre: concierge E2.5.

---

Changelog:
- 2026-06-15 (AUDIT-ROUTING-2026-06-14): Corregido id ENT_FB_INSIGHTS_KIMI_SWARM_7 → ENT_FB_INSIGHTS_KIMI_SWARM_7_ATERRIZAJE_v1. v1.0 se mantiene.
- v1.0 (2026-06-13): Creacion. Destilado de 6 dimensiones + cross-summary del swarm
  KIMI_SWARM_7_ATERRIZAJE_2026-06-12. 6 impactos en decisiones, tabla de precios,
  5 conflictos documentados. Crudos integros en docs/anexos/kimi_swarm_7/. ASCII puro.
