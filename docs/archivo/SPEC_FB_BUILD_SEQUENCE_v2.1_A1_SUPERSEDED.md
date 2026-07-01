# SPEC_FB_BUILD_SEQUENCE -- Propuesta secuencial de desarrollo FaberLoom (v2)

> **ARCHIVADO** — A1 SUPERSEDED — reemplazado por `SPEC_FB_BUILD_SEQUENCE_v3.0` (`docs/faberloom/SPEC_FB_BUILD_SEQUENCE_v3.md`). No usar para nuevas referencias.

id: SPEC_FB_BUILD_SEQUENCE_v2.1
version: 2.1
status: ARCHIVADO
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: SPEC
archived_reason: A1
replaced_by: SPEC_FB_BUILD_SEQUENCE_v3.0
stamp: ARCHIVADO — 2026-06-15 — A1 SUPERSEDED
aprobador: CEO (Alvaro) -- aprueba indexacion 2026-06-10; firma de contenido pendiente de cierre de [PENDIENTE] seccion 2
fuente: EVAL_STRAT_2026-06-09 + SPEC_FB_EVOLUTION_ROADMAP v1.0 + PLB_FB_FOUNDATION_BETA v1.3.1 + sesion Cowork 2026-06-10
aplica_a: [FaberLoom, MWT]
relacionado: SPEC_FB_BUILD_SEQUENCE_v3.md (reemplazo canónico) - SPEC_FB_EVOLUTION_ROADMAP_v1.md (fases F0-F6) - PLB_FB_FOUNDATION_BETA_v1.md (sprints heredados) - SPEC_FABERLOOM_MVP.md - ENT_GOB_DECISIONES.md (DEC routing LOW confidence)

---

## 0. Acto administrativo previo (no opcional)

Este documento, al firmarse, **supersede el ORDEN DE BUILD** de:
- PLB_FB_FOUNDATION_BETA v1.3.1 (los 13 sprints como secuencia; sus contenidos tecnicos se reutilizan donde se indica)
- SPEC_FABERLOOM_MVP seccion "Roadmap Post-MVP" (Fases 1-6)

NO supersede: kill criteria del PLB (se reutilizan adaptados), TIER 1 items aplicables a single-tenant, decisiones CEO firmadas que no contradigan esta secuencia (Anthropic-only, HITL absoluto, N0-N2, Hostinger KVM 8).

Razon: a 2026-06-10 coexisten 3 sistemas de etapas vigentes y contradictorios. Un proyecto de este tamano de equipo soporta exactamente uno.

---

## 1. Principios de la secuencia

1. **Cada etapa produce algo que MWT usa en operacion real esa misma etapa.** Nada se construye para un usuario hipotetico.
2. **El gate entre etapa tecnica y etapa comercial es comercial, no tecnico.** La capa corporativa (E3) no arranca porque E2 funcione; arranca porque E2.5 encontro compradores.
3. **Router delgado, sin arena.** La justificacion del router en E1 NO es ahorro de tokens (Kimi #4: break-even 9,524 drafts/mes, LOW confidence a volumen beta). Es: clasificacion data-class fail-closed + savings ledger como instrumento de medicion futura. Tabla de scoring A MANO. La arena llega cuando haya trafico que medir (post-E3).
4. **Metrica primaria de E1-E2: horas de fundador ahorradas por semana**, no USD de LLM. El gasto caro de MWT es atencion del CEO.
5. **Profundidad antes que amplitud** (regla heredada del ROADMAP). Factories, voice profile, multi-buzon, onboarding self-service: diferidos a E3+.
6. **SPEC freeze:** desde la firma de este doc hasta cerrar E2, no se indexa ningun SPEC_FB nuevo. Cada sesion FB produce codigo verificado o conversacion con prospecto, o no ocurre.

---

## 2. Recursos y presupuesto de atencion

| Recurso | Asignacion | Nota |
|---|---|---|
| Alejandro (AG-02/AG-07) | dev principal FB, dedicacion a definir en kickoff [PENDIENTE - % real] | si MWT necesita frontend/copy, FB cede -- declararlo, no descubrirlo |
| CEO (Alvaro) | max 6 h/sem FB total | 2h supervision/demo + 2h curaduria-aprobaciones + 2h E2.5 concierge |
| Agentes IA (Claude Code/Cowork) | pares de Alejandro en implementacion | bajo Karpathy rules |
| Infra | KVM 8 ya decidido | containers recortados (ver E1) |

Si Alejandro no puede comprometer un minimo estable [PENDIENTE - definir, sugerido >=15 h/sem], la secuencia completa se recalibra ANTES de arrancar, no a mitad.

---

## 3. Secuencia

### E0 -- Consolidacion (1 semana, solo CEO + Cowork, cero codigo)

Entregables:
1. Firma de este doc (o su correccion) como secuencia unica.
2. Nota de supersede en PLB_FB_FOUNDATION_BETA (changelog, sin borrar contenido -- Regla 3 KB).
3. Resolucion del [PENDIENTE] de conciliacion declarado en SPEC_FB_EVOLUTION_ROADMAP seccion F.
4. Lista cerrada del alcance E1 (que entra y que NO).
5. Confirmacion de dedicacion de Alejandro.

Gate de salida: un solo documento gobierna el orden de build; dedicacion dev confirmada por escrito.

---

### E1 -- Workspace + router delgado (4 semanas, walking skeleton)

> Equivale a F1 del ROADMAP. Reutiliza Sprint 1A y Sprint 2 del PLB, recortados a single-tenant interno.

**Semana 1 -- Infra minima (S1A recortado):**
- KVM 8 + Docker Compose con 6 containers: caddy, web, api, worker, postgres, redis. (litellm como libreria, no container; grafana/loki/prometheus/minio DESCARTADOS en favor de observabilidad gestionada -- logging JSON estructurado a disco + Langfuse Cloud free tier para trazas LLM desde el dia 1)
- Schema con tenant_id + RLS desde el dia 1 (barato ahora, carisimo despues) pero SIN permission matrix de 5 roles: 2 roles (Owner, Operator), auth simple httpOnly, 2FA solo Owner
- Audit log append-only basico
- Backup pg_dump diario + restore test demostrado (no negociable, es 1 dia)
- SIN landing publica, SIN CI/CD completo (lint + tests en pre-commit basta), SIN invitaciones

**Semana 2 -- KB pipeline (S2 del PLB casi integro):**
- Upload + parsers PDF/Excel/MD + chunker + FTS/pg_trgm (decision firmada #12)
- Wizard verificacion afirmaciones HIGH/LOW
- Paralelo CEO (bloque de 3h, calendarizado): curaduria 10-15 RFQs reales Marluvas como golden seed

**Semanas 3-4 -- Router + chat:**
- Router como pre-call hook en LiteLLM: clasifica tier + data-class allow-list fail-closed + tabla de scoring manual + savings ledger (registra costo real vs baseline premium; NO optimiza todavia)
- 1 agente conversacional draft-first contra la KB MWT
- UNA vista de chat + WebSocket. UI fea a proposito.
- Caso real que cruza: consultas operativas reales del CEO contra la KB (las que hoy hace en Cowork)

**Gate de salida E1 (las 5 fitness de F1 + 1):**
1. Clasifica tier <20ms
2. Allow-list por data_class fail-closed verificado con test
3. Responde con grounding de la KB sin alucinar (validado contra 10 consultas con respuesta conocida)
4. Savings ledger reporta costo vs baseline
5. Contamination test: tenant seed #2 no ve nada del #1
6. **El CEO uso el workspace para trabajo real >=3 dias/semana durante 2 semanas seguidas** (si ni vos lo usas, nadie lo va a usar)

Kill/replan E1: si en semana 6 desde kickoff el gate no esta, se congela FB 90 dias y las horas van a Rana Walk/B2B. Sin excepcion ni "una semana mas".

---

### E2 -- Agentes con profundidad (4-5 semanas)

> Equivale a F2 del ROADMAP. Reutiliza S3-S5 del PLB (engine, skills system, Tier 0, cotizacion, evidence bundle) sin factories.

**Semanas 5-6 -- Engine + skill cotizacion:**
- Engine ejecutor generico que lee SkillSpec de DB (heredado S3): timeout + cost cap, NO HTTP externo, NO code exec
- Tier 0 deterministico SOLO con las reglas que el vertical usa: parser RFQ + validacion TIN CR/CO/MX + montos/moneda/fechas. (Las 14 reglas pan-LATAM del MVP: diferidas. Spot-check del MVP aplica: validar cobertura contra 20 docs reales Marluvas/Tecmater antes de ampliar)
- clasificar_rfq + exception codes (los 15 de S3)
- generar_cotizacion + evidence bundle 8+5 + SHA-256 (S4)

**Semanas 7-8 -- Salida al mundo con HITL:**
- Mesa de Control minima: cola de drafts, aprobar/descartar/iterar (patron 3 botones)
- UN canal de salida: email desde buzon MWT (Gmail OAuth). WhatsApp Business DIFERIDO a E3 (el tramite Meta corre en paralelo si es gratis, pero no bloquea)
- Flujo completo: RFQ real entra -> draft proforma -> CEO aprueba -> sale

**Semana 9 (buffer) -- Cobranza como segundo skill** SOLO si cotizacion ya cerro su gate. Si no, el buffer es para cotizacion.

**Gate de salida E2:**
1. >=5 proformas reales de operacion MWT producidas, aprobadas y enviadas por el sistema
2. Edit rate <40% en las ultimas 10 (umbral heredado de kill criteria PLB, adaptado)
3. Reduccion de tiempo medida con cronometro (no auto-reportada): >=5x vs manual
4. Costo IA por tarea aprobada <USD 0.50
5. Cero incidentes de envio a destinatario equivocado

Kill/replan E2: edit rate sostenido >=60% en 30 drafts = el modelo no genera drafts utiles para este vertical -> congelar y replantear (criterio #3 del PLB, intacto).

---

### E2.5 -- Validacion comercial concierge (PARALELA: semanas 2-6, solo CEO, 2 h/sem)

> No depende de codigo. No espera a E2. Es la etapa que decide si E3 existe.

- Oferta a 10 PYMEs B2B NO-amigas (contactos de industria sirven; amistades no): "mandame tus facturas vencidas o tu RFQ por WhatsApp, te devuelvo los mensajes de cobranza / la proforma lista en 24h". CEO + Claude por detras, cero plataforma.
- Registro simple por prospecto: uso semana 1, uso semana 2, reaccion a precio ($30-50/mes), objeciones textuales.

**Gate (decide E3):**
- >=4/10 lo usan 2 semanas seguidas Y >=3/10 aceptan pagar algo concreto -> E3 se planifica con esos 3 como design partners pagos.
- <3/10 con intencion de pago -> E3 NO se construye. FaberLoom queda como herramienta interna de MWT (resultado bueno, no consolacion) y se re-evalua en 6 meses con los datos de uso interno.

---

### E3 -- Capa corporativa (CONDICIONAL a E2.5; 6-8 semanas; alcance lo definen los design partners)

Solo aqui entran, en orden de demanda real y no de elegancia arquitectonica:
1. Multi-tenant real: segundo tenant de verdad (primer design partner), herencia de config, contamination test suite a fondo (F5 del ROADMAP)
2. Onboarding 4 pasos + DPA legal + 5 roles + invitaciones (S7/S10 del PLB)
3. WhatsApp Business API como canal cliente
4. Observabilidad GESTIONADA (Langfuse Cloud para trazas LLM + uptime externo tipo UptimeRobot + alertas de costo). El stack self-host de S1B (grafana/loki/prometheus/minio) queda descartado salvo exigencia contractual de un cliente: para un equipo de 0.2 devs, operar observabilidad propia para <10 tenants es toil sin retorno. KVM 8 se mantiene como host de la app (decision firmada #1, costo hundido razonable); lo que se elimina es self-hostear el stack de monitoreo
5. Pricing real validado contra lo que los design partners aceptaron pagar (PRICING_TIERS v1.0 se revisa con dato, no se asume)

DIFERIDOS post-E3 (no negociable hasta tener >=3 tenants pagos): Agent Factory, Skill Factory, Voice Profile completo, arena/eval (reemplaza tabla manual del router recien aqui -- F3), Knowledge River L3+, catalogo de verticales, tiers Enterprise/Government, trademark multi-pais.

---

## 4. Linea de tiempo consolidada

| Semana | Track tecnico | Track comercial (CEO 2h/sem) |
|---|---|---|
| 0 | E0 consolidacion | confirmar lista de 10 prospectos |
| 1 | E1: infra minima | -- |
| 2 | E1: KB pipeline + golden RFQs | E2.5 arranca: primeras 5 ofertas |
| 3-4 | E1: router + chat -> GATE E1 | E2.5: 5 ofertas restantes, seguimiento |
| 5-6 | E2: engine + skill cotizacion | E2.5: cierre y medicion -> GATE E2.5 |
| 7-8 | E2: mesa de control + salida email | (resultado E2.5 ya conocido) |
| 9 | buffer / cobranza -> GATE E2 | decision E3: planificar con design partners o cerrar en interno |
| 10+ | E3 condicional | -- |

Total a sistema interno en produccion: ~9 semanas. Total a decision SaaS si/no: semana 6 (antes de terminar de construir -- ese es el punto).

## 5. Reglas inquebrantables de esta secuencia

1. Ningun gate se declara cumplido sin el caso real que lo prueba.
2. E3 no arranca sin gate E2.5 aprobado. "Los agentes ya funcionan" no es argumento.
3. SPEC freeze hasta cierre E2.
4. Los 3 amigos del plan original pueden ser testers de E1-E2 (feedback de producto) pero NO cuentan para el gate E2.5 (validacion de mercado).
5. Si Rana Walk o B2B Marluvas demandan las horas de FB en una semana dada, FB cede esa semana y el plan se corre -- se anota, no se compensa trabajando de mas.

---

Changelog:
- v2.1 (2026-06-10): E3 item 4 cambia de observabilidad self-host (S1B grafana/loki/prometheus/minio) a observabilidad gestionada (Langfuse Cloud + uptime externo); self-host solo por exigencia contractual de cliente. KVM 8 se mantiene como host de app. Alineado con revision de arquitectura 2026-06-10 (enmiendas ARCHETYPE v1.1 + VOICE_HUMANIZER v2.1).
- v2.0 (2026-06-10): Creacion como propuesta secuencial post EVAL_STRAT_2026-06-09. Supersede orden de build de PLB v1.3.1 y MVP Fases 1-6. 4 etapas + E2.5 comercial paralela con gate que condiciona E3. DRAFT pendiente firma CEO. ASCII puro.
