# SPEC_FB_BUILD_SEQUENCE -- Propuesta secuencial de desarrollo FaberLoom (v3)

id: SPEC_FB_BUILD_SEQUENCE
version: 3.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: SPEC
stamp: DRAFT -- 2026-06-13 -- v3.0: etapa 2 genérica, skills no predefinidos, cotización como ejemplo, hitos 2a/2b
aprobador: CEO (Alvaro) -- firma pendiente
fuente: SPEC_FB_BUILD_SEQUENCE_v2.1 + corrección sesión 2026-06-12 ("cotización es ejemplo, no mandato")
aplica_a: [FaberLoom, MWT]
relacionado: docs/archivo/SPEC_FB_BUILD_SEQUENCE_v2.1_A1_SUPERSEDED.md (v2.1 A1 SUPERSEDED · histórico) - SPEC_FB_EVOLUTION_ROADMAP_v1.md - PLB_FB_FOUNDATION_BETA_v1.md - ENT_FB_INSIGHTS_KIMI_SWARM_7_ATERRIZAJE_v1.md - AUDIT_FB_MODULAR_2026-06-11_v1.md

---

## 0. Acto administrativo previo (no opcional)

Este documento, al firmarse, **supersede el ORDEN DE BUILD** de:
- SPEC_FB_BUILD_SEQUENCE_v2.1 (y toda versión anterior)
- PLB_FB_FOUNDATION_BETA v1.3.2 (los 13 sprints como secuencia; sus contenidos técnicos se reutilizan donde se indica)
- SPEC_FABERLOOM_MVP sección "Roadmap Post-MVP" (Fases 1-6)

NO supersede: kill criteria del PLB (se reutilizan adaptados), TIER 1 items aplicables a single-tenant, decisiones CEO firmadas que no contradigan esta secuencia (Anthropic-only, HITL absoluto, N0-N2, Hostinger KVM 8).

Razón: a 2026-06-13 la secuencia v2.1 fosilizó la cotización de calzado de seguridad como mandato del producto. Esa cotización fue un **ejemplo** que ilustró el flujo desde abril 2026; en la v3.0 vuelve a ser ejemplo, no mandato. El sistema de skills que se construye es genérico — el uso real (no el plan) define qué skills corren.

---

## 1. Principios de la secuencia

1. **Cada etapa produce algo que MWT usa en operación real esa misma etapa.** Nada se construye para un usuario hipotético.
2. **El gate entre etapa técnica y etapa comercial es comercial, no técnico.** La capa corporativa (E3) no arranca porque E2 funcione; arranca porque E2.5 encontró compradores.
3. **Router delgado, sin arena.** La justificación del router en E1 NO es ahorro de tokens (Kimi #4: break-even 9,524 drafts/mes, LOW confidence a volumen beta). Es: clasificación data-class fail-closed + savings ledger como instrumento de medición futura. Tabla de scoring A MANO. La arena llega cuando haya tráfico que medir (post-E3).
4. **Métrica primaria de E1-E2: horas de fundador ahorradas por semana**, no USD de LLM. El gasto caro de MWT es atención del CEO.
5. **Profundidad antes que amplitud** (regla heredada del ROADMAP). Factories, voice profile, multi-buzón, onboarding self-service: diferidos a E3+.
6. **SPEC freeze:** desde la firma de este doc hasta cerrar E2, no se indexa ningún SPEC_FB nuevo. Cada sesión FB produce código verificado o conversación con prospecto, o no ocurre.
7. **El plan no predefine qué skills; el uso sí exige que haya uso.** La protección contra "plataforma sin caso" es el gate real, no el mandato del contenido.

---

## 2. Recursos y presupuesto de atención

| Recurso | Asignación | Nota |
|---|---|---|
| Alejandro (AG-02/AG-07) | dev principal FB, dedicación a definir en kickoff [PENDIENTE - % real] | si MWT necesita frontend/copy, FB cede -- declararlo, no descubrirlo |
| CEO (Alvaro) | max 6 h/sem FB total | 2h supervisión/demo + 2h curaduría-aprobaciones + 2h E2.5 concierge |
| Agentes IA (Claude Code/Cowork) | pares de Alejandro en implementación | bajo Karpathy rules |
| Infra | KVM 8 ya decidido | containers recortados (ver E1) |

Si Alejandro no puede comprometer un mínimo estable [PENDIENTE - definir, sugerido >=15 h/sem], la secuencia completa se recalibra ANTES de arrancar, no a mitad.

---

## 3. Secuencia

### E0 -- Consolidación (1 semana, solo CEO + Cowork, cero código)

Entregables:
1. Firma de este doc (o su corrección) como secuencia única.
2. Nota de supersede en PLB_FB_FOUNDATION_BETA (changelog, sin borrar contenido -- Regla 3 KB).
3. Resolución del [PENDIENTE] de conciliación declarado en SPEC_FB_EVOLUTION_ROADMAP sección F.
4. Lista cerrada del alcance E1 (qué entra y qué NO).
5. Confirmación de dedicación de Alejandro.

Gate de salida: un solo documento gobierna el orden de build; dedicación dev confirmada por escrito.

---

### E1 -- SpaceLoom + Routing (el sustrato) · 3-4 semanas

> Equivale a F1 del ROADMAP. Reutiliza Sprint 1A y Sprint 2 del PLB, recortados a single-tenant interno.

**Semana 1 -- Infra mínima (S1A recortado):**
- KVM 8 + Docker Compose con 6 containers: caddy, web, api, worker, postgres, redis. (litellm como librería, no container; grafana/loki/prometheus/minio DESCARTADOS en favor de observabilidad gestionada -- logging JSON estructurado a disco + Langfuse Cloud free tier para trazas LLM desde el día 1)
- Schema con tenant_id + RLS desde el día 1 (barato ahora, carísimo después) pero SIN permission matrix de 5 roles: 2 roles (Owner, Operator), auth simple httpOnly, 2FA solo Owner
- Audit log append-only básico
- Backup pg_dump diario + restore test demostrado (no negociable, es 1 día)
- SIN landing pública, SIN CI/CD completo (lint + tests en pre-commit basta), SIN invitaciones
- Schemas físicos completos: savings ledger, gold samples, conversaciones, workspace_members, scheduled_jobs, client_map (SCH_FB_CORE_TABLES v1)

**Semana 2 -- KB pipeline (S2 del PLB casi íntegro):**
- Upload + parsers PDF/Excel/MD + chunker + FTS/pg_trgm (decisión firmada #12, matizada: contexto-first para docs KB, FTS secundario para SKUs)
- Wizard verificación afirmaciones HIGH/LOW
- Paralelo CEO (bloque de 3h, calendarizado): curaduría 10-15 RFQs reales Marluvas como golden seed
- Bloque de investigación: reproducir 5 RFQs históricas usando SOLO la KB (inv. #2); eval set 30-50 Q&A reales (inv. #1); correr parsers Tier 0 contra golden set (inv. #5)

**Semanas 3-4 -- Router + chat:**
- Router como pre-call hook en LiteLLM: clasifica tier + data-class allow-list fail-closed + preset/curva Eco-Balanceado-Sport + tabla de scoring manual + savings ledger (registra costo real vs baseline estimado; NO optimiza todavía)
- 1 agente conversacional draft-first contra la KB MWT
- UNA vista de chat + WebSocket. UI fea a propósito.
- Caso real que cruza: consultas operativas reales del CEO contra la KB (las que hoy hace en Cowork)
- Gold samples capturados desde el día 1 (cada respuesta usable = ejemplo futuro)

**Gate de salida E1 (las 5 fitness de F1 + 1):**
1. Clasifica tier <20ms
2. Allow-list por data_class fail-closed verificado con test
3. Responde con grounding de la KB sin alucinar (validado contra 10 consultas con respuesta conocida)
4. Savings ledger reporta costo vs baseline estimado
5. Contamination test: tenant seed #2 no ve nada del #1
6. **El CEO usó el workspace para trabajo real >=3 días/semana durante 2 semanas seguidas** (si ni vos lo usás, nadie lo va a usar)

Kill/replan E1: si en semana 6 desde kickoff el gate no está, se congela FB 90 días y las horas van a Rana Walk/B2B. Sin excepción ni "una semana más".

---

### E2 -- Sistema de skills genérico (el valor) · 4-5 semanas

> Equivale a F2 del ROADMAP. Reutiliza S3-S5 del PLB (engine, skills system, Tier 0, evidence bundle) sin factories. **El sistema no presupone qué skills; el uso define el contenido.**

**Hito 2a (semanas 5-6): primer skill end-to-end**
- Engine ejecutor genérico que lee SkillSpec de markdown versionado (heredado S3, enmendado: skill = markdown + tools allowlist + schema de salida, capa fina sobre SDK estándar): timeout + cost cap, NO HTTP externo, NO code exec
- Tier 0 determinístico con las reglas que el primer skill real use. Las 14 reglas pan-LATAM del MVP: diferidas; se construyen cuando el uso las pida.
- UN skill real que el CEO delegue de verdad (puede ser cotización, seguimiento a cliente, respuesta a RFQ, resumen de cuenta — lo que aparezca en semanas 1-2 de E1). El flujo: entra algo real -> draft -> aprobás -> sale.
- Evidence bundle con SHA-256 (S4)

**Hito 2b (semanas 7-8): Inbox + Mesa + segundo skill**
- Inbox agregador (IMAP buzones propios, app password — cero verificación per swarm)
- Clasificador + entity resolution (client_map seed + freemail list + triage que alimenta el mapa automáticamente)
- Mesa de Control mínima: cola de drafts, aprobar/descartar/iterar (patrón 3 botones) + captura del porqué
- UN canal de salida: email desde buzón MWT (SMTP/DWD — verificación Google evitable). WhatsApp Business DIFERIDO a E3 (el trámite Meta corre en paralelo si es gratis, pero no bloquea)
- Segundo skill de clase de tarea distinta (≥2 clases distintas para cerrar E2)
- Aprendizaje mínimo: CTA indexar + cola de candidatos (la curación sofisticada espera volumen)

**Semana 9 (buffer):**
- Si hito 2a se atrasó, el buffer es para 2a.
- Si 2a cerró, tercer skill o refinamiento del engine.

**Gate de salida E2:**
1. >=10 outputs reales cliente-facing aprobados y enviados, de >=2 clases de tarea distintas. Las clases las nombra el ledger después de que existan, no el plan antes.
2. Edit rate <40% en los últimos 20 (umbral heredado de kill criteria PLB, adaptado)
3. Reducción de tiempo medida con cronómetro (no auto-reportada): >=5x vs manual
4. Costo IA por tarea aprobada <USD 0.50
5. Cero incidentes de envío a destinatario equivocado

Kill/replan E2: edit rate sostenido >=60% en 30 drafts = el modelo no genera drafts útiles para este operador -> congelar y replantear (criterio #3 del PLB, intacto).

**Diseño de referencia (no mandato):** los docs específicos de cotización (QUOTING_SOURCE_OF_TRUTH, taxonomía de excepciones RFQ, parsers Tier 0 de facturas LATAM) son buenos si la cotización aparece — que probablemente aparezca, es la operación de MWT — pero ningún sprint los construye "porque estaban en el plan". Se construyen cuando el uso los pida, en el flujo normal.

---

### E2.5 -- Validación comercial concierge (PARALELA: semanas 2-6, solo CEO, 2 h/sem)

> No depende de código. No espera a E2. Es la etapa que decide si E3 existe.

- Oferta a 10 PYMEs B2B NO-amigas (contactos de industria sirven; amistades no): "mandame tus facturas vencidas o tu RFQ por WhatsApp, te devuelvo los mensajes de cobranza / la proforma lista en 24h". CEO + Claude por detrás, cero plataforma.
- Registro simple por prospecto: uso semana 1, uso semana 2, reacción a precio ($39/mes ancla, banda $30-50), objeciones textuales.
- Prioridad: CR/GT/CO-corporativo (legal manejable). MX: abogado antes del primer cliente pago (LFPDPPP 2025 exige contrato de encargado).

**Gate (decide E3):**
- >=4/10 lo usan 2 semanas seguidas Y >=3/10 aceptan pagar algo concreto -> E3 se planifica con esos 3 como design partners pagos.
- <3/10 con intención de pago -> E3 NO se construye. FaberLoom queda como herramienta interna de MWT (resultado bueno, no consolación) y se re-evalúa en 6 meses con los datos de uso interno.

---

### E3 -- Espacios de trabajo (el lente) · 2-3 semanas

> La UI del lente sobre datos que ya existen scoped desde E1 (workspace_id en tablas, membresía en queries server-side). No se construyen pantallas específicas de workspace: 5 superficies parametrizadas por scope.

- Tabs Bandeja/Iteración/KB/Histórico filtrados por workspace
- Scope bar visible, salida al global en un click
- Herencia de anatomía SpaceLoom (misma anatomía, distinto scope)
- Sugerencias por cuenta (fijados + recientes de la cuenta)
- CTA indexar con default L3 (en SpaceLoom global el CTA pregunta L1/L2/L3/L4; en workspace ya sabe dónde va)
- Modo Aprendizaje completo: promoción del router con regla N>=30 (recién acá hay volumen), vigencias con scheduler, conflictos de fuente

Gate: operar 2+ cuentas reales (Sondel + otra) puramente desde sus workspaces una semana, sin volver al global para nada operativo.

---

### E4 -- Grupos de trabajo (los otros humanos) · acá se parte en dos

**4a Multi-usuario interno (sin gate comercial):**
- Alejandro y quien siga como operadores — membresía, 2 roles, columna Delegado de la Mesa, lock optimista, invitaciones. Se construye sí o sí.

**4b Multi-tenant externo (CON gate E2.5):**
- Design partners pagos, onboarding, DPA, 5 roles, WhatsApp Business API, pricing validado contra lo que aceptaron pagar. Solo si el concierge dio >=3 con intención de pago. Si 4b se cuela sin gate, volvimos al pecado de mayo.

---

### E5 -- Amplitud post-validación (nombrada, no diseñada)

> APIs abiertas, MCP FaberLoom-en-MWT, segundo vertical, Agent Factory, Skill Factory, Voice Profile completo, arena/eval, Knowledge River L3+, catálogo de verticales, tiers Enterprise/Government. **No se planifica hoy.** Depende de cómo termine E4b. Se deja una línea en el doc: "existe, no se diseña hasta cerrar E4b".

---

## 4. Línea de tiempo consolidada

| Semana | Track técnico | Track comercial (CEO 2h/sem) |
|---|---|---|
| 0 | E0 consolidación | confirmar lista de 10 prospectos |
| 1 | E1: infra mínima + schemas | -- |
| 2 | E1: KB pipeline + golden RFQs + investigaciones | E2.5 arranca: primeras 5 ofertas |
| 3-4 | E1: router + chat -> GATE E1 | E2.5: 5 ofertas restantes, seguimiento |
| 5-6 | E2: hito 2a (primer skill end-to-end) | E2.5: cierre y medición -> GATE E2.5 |
| 7-8 | E2: hito 2b (Inbox + Mesa + segundo skill) | (resultado E2.5 ya conocido) |
| 9 | buffer / refinamiento -> GATE E2 | decisión E3/E4: planificar con design partners o cerrar en interno |
| 10-12 | E3: lente + workspaces | -- |
| 13-14 | E4a: multi-usuario interno | -- |
| 15+ | E4b condicional | -- |

Total a sistema interno en producción: ~9 semanas. Total a decisión SaaS sí/no: semana 6 (antes de terminar de construir -- ese es el punto).

---

## 5. Reglas inquebrantables de esta secuencia

1. Ningún gate se declara cumplido sin el caso real que lo prueba.
2. E4b no arranca sin gate E2.5 aprobado. "Los agentes ya funcionan" no es argumento.
3. SPEC freeze hasta cierre E2.
4. Los 3 amigos del plan original pueden ser testers de E1-E2 (feedback de producto) pero NO cuentan para el gate E2.5 (validación de mercado).
5. Si Rana Walk o B2B Marluvas demandan las horas de FB en una semana dada, FB cede esa semana y el plan se corre -- se anota, no se compensa trabajando de más.
6. El plan no predefine qué skills; el gate exige que haya uso real. "Sin preconceptos" no puede degenerar en "plataforma sin caso".

---

## Nota sobre la cotización de calzado de seguridad

La cotización de calzado de seguridad fue el **ejemplo** que ilustró el flujo desde abril 2026. En las versiones v1/v2 del plan se fosilizó como mandato, lo que hacía parecer que FaberLoom era un cotizador de calzado. En la v3.0 vuelve a ser **primer candidato natural**: probablemente aparezca porque es la operación de MWT, pero el sistema no la prescribe. Si otro usuario agarra la herramienta, hará otras cosas — y la maquinaria no debe saber ni importarle.

Los docs de diseño específico de cotización (ENT_QUOTING_SOURCE_OF_TRUTH, SCH_FB_QUOTE_EVIDENCE_BUNDLE, los 15 exception codes) siguen VIGENTES como **diseño de referencia**. Se construyen cuando el uso los pida, en el flujo normal, no porque estén en el plan.

---

Changelog:
- v3.0 (2026-06-13): Re-corte de etapas: E2 genérica (sistema de skills, no cotización), E3 = lente/workspace, E4a = multi-usuario interno, E4b = multi-tenant externo (condicional), E5 = amplitud nombrada sin diseñar. Cotización pasa de mandato a ejemplo/primer candidato natural. Gates agnósticos de clase de tarea (>=10 outputs de >=2 clases). Hito 2a/2b explícitos. Track concierge E2.5 sigue paralelo. Cero cambios en E1 (intacto).
- v2.1 (2026-06-10): E3 item 4 cambia de observabilidad self-host a gestionada; self-host solo por exigencia contractual. Alineado con enmienda ARCHETYPE v1.1 + VOICE_HUMANIZER v2.1.
- v2.0 (2026-06-10): Creación como propuesta secuencial post EVAL_STRAT. Supersede orden de build de PLB v1.3.1 y MVP Fases 1-6. 4 etapas + E2.5 comercial paralela.

> ORDEN/TIMELINE SUPERSEDED 2026-06-22 por PLAN_DESARROLLO_FABERLOOM_v5 seccion 0. Contenido tecnico reutilizable se conserva.
