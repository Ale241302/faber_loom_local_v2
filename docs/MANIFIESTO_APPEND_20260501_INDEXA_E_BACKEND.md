---
id: MANIFIESTO_APPEND_20260501_INDEXA_E_BACKEND
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza
type: manifiesto_append
stamp: VIGENTE 2026-05-01
fecha: 2026-05-01
agente: Cowork (planificacion + redaccion) + CEO (decisiones + delegaciones tecnicas) + ChatGPT (auditoria R4)
aplica_a: [FaberLoom]
relacionado_con:
  - MANIFIESTO_APPEND_20260430d_AUDIT_RECONCILIATION (indexa-d)
  - 3 archivos nuevos + 2 modificados
---

# MANIFIESTO_APPEND_20260501_INDEXA_E_BACKEND

## Que paso

Quinta indexa post review R4 ChatGPT (Sprint 1 readiness 8.7/10). Cierra arquitectura backend antes del mock v4 + Sprint 1 implementacion.

Sequence completa hasta ahora:
1. **30abr-a Knowledge River** · modelo conocimiento (5 capas · 3 modos gobernanza)
2. **30abr-b P16 Decomposition** · modelo ejecucion (orquestador + sub-agentes atomicos)
3. **30abr-c AM Vertical** · primer SPEC end-to-end aplicando ambos
4. **30abr-d Audit Reconciliation R2+R3** · 6 piezas nuevas + 2 modificadas
5. **01may-e Backend** (ESTA) · 3 nuevos + 2 modificados post review R4

Pendiente:
6. **xx-may-f post mock v4** · integracion visual + UI Curador + ZIPs Ciclope a docs/anexos/

## Resumen ejecutivo · review R4 ChatGPT

| Metrica | Valor |
|---|---|
| Sprint 1 readiness | **8.7/10 con ajustes pre-canonizacion** |
| Archivos limpios (canonizar tal cual) | 1 (Source of Truth v1.1 con micro-aclaracion) |
| Archivos con ajustes quirurgicos | 4 (Replay · Curator · Brand · Vertical Spec) |
| Rechazos | 0 |
| Quirurgicos vs redisenos | 100% quirurgicos · 0% redisenos |

> **Insight central R4:** "el mayor riesgo downstream no es tecnico · es **autoridad semantica mal asignada**. UI inteligente · operacion = error caro con tipografia bonita."

## Decisiones arquitectonicas tomadas en esta indexa

### Decision 1 · Lifecycle estados explicitos para replay set

5 estados canonicos: `candidate · active · pinned_edge · retired · rejected_contaminated`. Sin esto · "Sprint 1 inventaria estados en codigo · la arquitectura ya perdio aunque compile" (R4).

### Decision 2 · Auto-add SI · auto-promote NO

Auto-add desde produccion entra como `candidate`. Auto-promote a `active` SIEMPRE requiere curador. Sin separacion explicita · "alguien en Sprint 1 lo implementa como cola FIFO glorificada" (R4).

### Decision 3 · Suite regresion Ciclope aislada del pool MVP

30 fixtures Ciclope (20 R3 + 10 safety_footwear) son suite regresion separada. NO entrenan memory packs. NO se mezclan con el pool MVP de 60 RFQs reales. Solo validan no-regresion.

### Decision 4 · Curador con cambio de hat registrado

En MWT v1 una sola persona (CEO Alvaro) cubre AM + Curador + CEO. Cada decision registra `actor_role_at_decision` (no solo usuario). Cuando MWT crezca y los roles se separen fisicamente · log historico ya distingue por hat (no requiere refactor).

### Decision 5 · Bloqueo curaduria separado de operacion AM

Si curador no hace freeze 60+ dias · sistema bloquea promociones de candidate samples. Pero NO bloquea operacion AM ni generacion de cotizaciones. R4 explicit: "Bloquear solo aprendizaje/promociones · no operacion AM."

### Decision 6 · FaberLoom es marca/plataforma · NO entidad legal

Entidad legal real: Muito Work Limitada. FaberLoom es brand/plataforma propiedad de Muito Work. Facturas: "Razon social emisora: Muito Work Limitada · Descripcion comercial: Servicio de plataforma FaberLoom / Mesa de Control de Cotizaciones Tecnicas". NUNCA "FaberLoom S.A." o "razon social FaberLoom".

### Decision 7 · Glossary precedencia con limite estricto

Glossary aplica a `intent_parsing · variant_interpretation · use_case_inference`. NO aplica a `certification · compliance · price · stock · supplier_equivalence`. R4 frase canonica: "glossary interpreta lenguaje · no certifica compliance · stock · precio o equivalencia normativa."

### Decision 8 · "bota dielectrica" → INTENT no certificacion directa

Glossary mapea "bota dielectrica" a `requires_electrical_hazard_protection` (intent comercial). Cert ASTM EH lo confirma luego en source of truth. R4 critico: evita "bota dielectrica = ASTM EH certificado por magia semantica."

### Decision 9 · "calzado agro" → USE_CASE no quimico forzoso

"Calzado agro" mapea a `agricultural_use_case`. `chemical_resistance` solo si RFQ lo pide explicito. "Agro" puede ser lodo · humedad · cana · finca · quimicos · o simplemente bota de trabajo rural.

### Decision 10 · "punto" sin pais = ALARMA

Sin pais explicito del cliente · NO inferir talla silenciosamente. Disparar ALARMA o pedir clarificacion. R4 critico: evita inferencias erroneas en clientes CR/CO.

### Decision 11 · AM-promesa como fuente de baja autoridad

Si AM promete dato (flete · plazo · stock) sin respaldo carrier/3PL/source · genera `evidence_gap` en bundle · NO pasa como verdad operacional. Etiquetada explicitamente con autoridad limitada.

### Decision 12 · Linea "NO implica" en cada archivo (R4 bonus 5%/50%)

Cada uno de los 5 archivos cierra con declaracion explicita de que NO implica:
- `RFQ_REPLAY_SET no implica entrenamiento automatico`
- `CURATOR_OPERATING_MODEL no implica bloqueo operativo del AM`
- `BRAND_DUAL_NAMING no implica entidad legal FaberLoom`
- `SOURCE_OF_TRUTH freight no implica integracion carrier en v1`
- `VERTICAL_SPEC glossary no implica certificacion tecnica`

R4 explicit: "es minimo · brutalmente util y mata el 80% de malas interpretaciones antes de que lleguen a codigo."

## Validacion de los 11 votos del CEO (procesados R4)

| # | Voto CEO | Estado |
|---|---|---|
| 1 | Curador retira mensual + review semanal candidatos | ✓ aceptado · preserva split |
| 2 | Replay set extiende auto-add producción | ⚠ aceptado · solo a candidate · NO auto-promote |
| 3 | 30 fixtures Ciclope suite regresion separada · pool MVP = 60 reales Sem 0 | ✓ aceptado |
| 4 | CEO=AM=Curador en MWT v1 | ⚠ aceptado · con `actor_role_at_decision` registrado |
| 5 | Tenants chicos diaria+semanal combinada · mensual freeze obligatorio todos | ✓ aceptado |
| 6 | Warning 35d · bloqueo promociones 60d | ✓ aceptado · solo bloqueo aprendizaje |
| 7 | Footer "powered by FaberLoom" gris | ✓ aceptado |
| 8 | Facturas razon social legal vs descripcion comercial | ⚠ aceptado · separacion estricta |
| 9 | Sub-dominio per tenant mwt.faberloom.com | ✓ aceptado |
| 10 | Glossary case-insensitive Unicode | ✓ aceptado |
| 11 | Regex tolerante `\d+\s*punto[s]?` | ⚠ aceptado · con boundaries `\b` y exclusiones |

7 ✓ + 4 ⚠ con caveat + 0 ✗.

## 5 contradicciones detectadas y resueltas

1. **glossary_overrides vs authority matrix** → precedence solo intent_parsing/variant/use_case · NUNCA certification/compliance/price/stock
2. **Auto-add producción vs privacy TENANT_DERIVED** → entra como candidate · cualquier promote cross-tenant requiere abstraccion + 7 checks privacy
3. **FaberLoom como entidad vs Muito Work Limitada** → marca/plataforma · NO entidad legal
4. **freight_MX_routes low priority** → mantener priority low pero clasificar `commercial_margin_sensitive`
5. **Curador no operador vs CEO=todo en MWT** → separacion FUNCIONAL no fisica · misma persona puede ejercer ambos hats con `actor_role_at_decision`

## Archivos creados/modificados en esta indexa

### Nuevos (3)

| Archivo | Lineas |
|---|---|
| docs/faberloom/ENT_FB_RFQ_REPLAY_SET_v1.md | ~270 |
| docs/faberloom/ENT_FB_CURATOR_OPERATING_MODEL_v1.md | ~240 |
| docs/faberloom/ENT_FB_BRAND_DUAL_NAMING_v1.md | ~210 |

### Modificados (2)

| Archivo | Cambio |
|---|---|
| docs/faberloom/ENT_FB_QUOTING_SOURCE_OF_TRUTH_v1.md | v1.0 → v1.1 · +2 fuentes flete (15 international · 16 MX_routes) · microaclaracion AM-promesa · linea NO implica |
| docs/faberloom/ENT_FB_VERTICAL_SPEC_OBJECT_v1.md | v1.0 → v1.1 · +seccion 8 glossary_overrides safety_footwear (5 terminos · 1 gap · case-insensitive Unicode · regex con boundaries · precedencia con limite) · linea NO implica |

### Bumps (2)

| Archivo | Cambio |
|---|---|
| docs/RW_ROOT.md | v4.8.12 → v4.8.13 + entry changelog |
| docs/DASHBOARD_SNAPSHOT.md | v12.3 → v12.4 + conteos |

### Manifiesto (1)

| Archivo | Lineas |
|---|---|
| docs/MANIFIESTO_APPEND_20260501_INDEXA_E_BACKEND.md (este) | ~280 |

**Total esta indexa: 8 archivos · ~720 lineas nuevas + ~150 lineas modificadas (ampliaciones).**

## Conteos esperados post-indexa

- docs/ raiz: 302 → 303 (+1 manifiesto)
- docs/faberloom/: 21 → 24 (+3 nuevos)
- Repo total: 431 → 435

## Pendientes post-merge

### Inmediato (proxima sesion)

1. **Esperar mock v4 ChatGPT** (en construccion paralelo · brief `chatgpt_v4_build_brief.md`)
2. **Indexa-f post mock v4:** integracion visual al repo + actualizacion UI Curador + mover ZIPs Ciclope a `docs/anexos/ciclope_fixtures/r3_cross_industry/` y `docs/anexos/ciclope_fixtures/safety_footwear/`

### Mediano plazo (Sprint 1 · 6 sem)

3. PLB_ORCHESTRATOR + AG-01 a AG-07 toman SPECs canonizados + replay set + curator model + brand naming como contracts · construyen sub-agentes individuales en SHADOW
4. CEO arma replay set inicial Sem 0 (60 RFQs reales · AI-assisted · CEO marca outcome ganada/perdida/ambigua/edge)
5. CEO ajusta Authority Matrix MWT antes Sem 0 (~30 min · sobre defaults canonicos)
6. CEO inicia rol Curador con cadencia diaria 15min + semanal 60-90min + mensual freeze (en MWT v1 cambia hat · registra `actor_role_at_decision`)
7. Pricing $XXX [PENDIENTE — CEO + finance]

### Diferidos hasta evidencia real

8. SPEC_FB_TEMPLATE_GOVERNANCE_v1 (tablas postgres · eventos · APIs REST) · cuando AG_AM_MWT produzca eventos reales en SHADOW
9. SPEC_FB_AGENT_BUILDER v3.0 P16-native · cuando catalogo + SPEC AM tengan 30-60d de uso real
10. Telar Layer 3b runtime per-output · cuando volumen multi-tenant lo justifique (gate F2)
11. SPEC_FB_GOVERNANCE_UI_v1 (mockups + interacciones) · diferida indexa-f
12. SPEC_FB_REPLAY_SET_IMPLEMENTATION_v1 (DB postgres? S3? algoritmo stratified reservoir) · diferido SPEC tecnico

## Reconciliacion total auditorias R1+R2+R3+R4

| Auditoria | Score · Estado |
|---|---|
| R1 (18-abr) Arquitectonica | 8.5/10 · canonizada |
| R2 (30-abr-d) Post-canonizacion · 7 piezas + 5 reformulaciones | aceptada · canonizada |
| R3 (30-abr-d noche) Funcional multi-industria · 5 industrias · 25 acciones simplificacion mock | aceptada · canonizada (excepto mock v4 pendiente) |
| R4 (01-may) Indexa-e backend · 5 archivos | 8.7/10 · canonizada (esta indexa) |

Cero rechazos en 4 auditorias consecutivas. Modelo arquitectonico FaberLoom validado externamente.

## Diferencial defendible reforzado vs competencia

Tras esta indexa · FaberLoom tiene 11 piezas arquitectonicas que ChatGPT WA / Notion / Linear NO tienen:

1. vertical_spec_object · adapter pattern parametrizable per industria
2. Authority Matrix con 8 NEVER agente solo · operacionalizacion HITL P3
3. Exception Taxonomy 15 excepciones + severity_weight ponderada
4. Evidence Bundle per-line + per-quote · 3 vistas · SHA-chain audit
5. Privacy Tiers 4 niveles con TIER 4 RESTRICTED_SENSITIVE_OR_REGULATED · cumple LFPDPPP/LGPD
6. Compliance Checker 6 perfiles per vertical
7. **Replay Set canonico con lifecycle 5 estados + auto-add solo candidate · suite regresion Ciclope aislada**
8. **Curador organizacional con cadencia + scope + decisiones + cambio de hat registrado**
9. **Brand dual naming · separacion estricta marca/producto/legal**
10. **Source of Truth con 16 fuentes incluyendo flete + AM-promesa baja autoridad**
11. **Glossary regional con precedencia limitada · interpreta lenguaje · NO certifica**

Moat real: **criterio acumulado versionado** (R4 insight) · imposible replicar sin curaduria periodica + tracking decisiones + audit trail.

## Origen de los insights clave R4

ChatGPT R4 (auditor externo · sesion 01-may):

> "el mayor riesgo downstream no es tecnico · es autoridad semantica mal asignada. Dos ejemplos peligrosos: 'bota dielectrica' → ASTM EH certificado · 'punto' sin pais claro → talla inferida silenciosamente. Eso en UI se ve inteligente. En operacion B2B se llama error caro con tipografia bonita."

> "el moat no es tener documentos. Es tener criterio acumulado versionado: regla + evidencia + decision + resultado."

> "agregar a cada archivo una linea final de 'NO implica'. Es minimo · brutalmente util y mata el 80% de malas interpretaciones antes de que lleguen a codigo."

CEO Alvaro (delegacion tecnica · sesion 01-may):
> "indexa la canonizacion de los 5 archivos."

## Stamp
VIGENTE 2026-05-01 — Indexa-e backend cierre arquitectonico previo Sprint 1. 5 piezas canonizadas con ajustes quirurgicos R4. ARCH sealed v1.5 NO tocado · POL_DATA_CLASSIFICATION sealed v1.4 NO tocado · FROZENs intactos. Modelo FaberLoom validado por 4 auditorias externas consecutivas (R1+R2+R3+R4) sin rechazos. Pendiente unico para cerrar todo: indexa-f post mock v4 ChatGPT (visual + UI Curador + organizacion ZIPs Ciclope).
