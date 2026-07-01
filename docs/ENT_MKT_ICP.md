# ENT_MKT_ICP — Ideal Customer Profile por Producto × Mercado
id: ENT_MKT_ICP
status: DRAFT
visibility: [INTERNAL]
version: 1.0
stamp: DRAFT — pendiente aprobación CEO
domain: Marketplace (IDX_MARKETPLACE)
classification: ENTITY — Data pura inyectable
aplica_a: [MWT]

---

## A. Concepto

ICP vivo por producto × mercado × nodo. Dos capas: validada (CEO confirma) + observaciones (sistema detecta). No es documento estático — evoluciona con señales del mercado.

Regla: `confidence: hypothesis` hasta que datos reales lo validen. Ref → POL_DETERMINISMO.

---

## B. Goliath × USA (MWT-CR)

### B1. Ficha de nodo

```
Producto: Goliath (ref → ENT_PROD_GOL)
Mercado: USA (ref → ENT_MERCADO_USA)
Nodo comercial: MWT-CR (seller of record Amazon.com)
Cadena: FACTORY-CN → FBA-US → consumidor final
Certificación requerida: ninguna obligatoria (no es medical device, no es safety footwear)
Elegibilidad HSA/FSA: PENDIENTE inscripción SIGIS (ref → ENT_COMP_CONTENT_RULES.A)
Canal activo: Amazon FBA USA
Precio: $37.99 (premium justificable, no lujo)
Confidence: hypothesis
```

### B2. Wedge

```
Statement: "Work-boot fatigue relief para personas 225+ lbs que pasan todo el día de pie"

Estructura:
  Contexto de búsqueda : work boots + standing all day
  Beneficio comprable  : fatigue relief / impact reduction
  Calificador          : 225+ lbs / heavy duty
  Prueba               : PORON XRD (Rogers Corp) + 5 capas biomecánicas
  
Regla: use-case-led > attribute-led
  ✅ "Work Boot Insoles for Standing All Day — Heavy Duty 225+ lbs"
  ❌ "225+ lbs Heavy Duty Insoles with PORON XRD Biomechanical..."
```

### B3. Buyer — quién es

| Atributo | Valor primario | Alternativas conocidas |
|---|---|---|
| Peso | 225+ lbs | 200-300+ rango amplio |
| Ocupación | Warehouse, construction, factory | Healthcare (emergente), delivery, security |
| Horas de pie | 8-12 horas/turno | 6+ horas mínimo |
| Calzado | Work boots (steel/composite toe) | Safety shoes, nursing shoes |
| Contexto | Turno industrial, superficies duras | Hospital, retail, outdoor |
| Edad | 30-55 (estimado) | [PENDIENTE — validar con datos] |
| Ingreso | Medio-bajo a medio | [PENDIENTE — validar] |

### B4. Pain points — rankeados por hipótesis

| # | Pain point | Evidencia | Confidence |
|---|---|---|---|
| 1 | Fatiga al final del turno / pies destruidos | A9 producto + search terms (standing all day) | hypothesis |
| 2 | Heel pain / dolor de talón | Categoría Amazon (plantar fasciitis cluster) | hypothesis |
| 3 | Plantar fasciitis | Keyword volume alto en categoría | hypothesis |
| 4 | Dolor de rodilla/espalda por impacto | Secundario — mencionado en reviews de competidores | hypothesis |
| 5 | Plantillas genéricas no duran / no funcionan | Objeción recurrente en reviews PowerStep/Superfeet | hypothesis |

### B5. Buyer language — frases de compra

**Búsquedas primarias (contexto de uso):**
- "work boot insoles for standing all day"
- "insoles for heavy guys"
- "best insoles for warehouse workers"
- "insoles for 12 hour shifts"
- "work boot insoles for big guys"

**Búsquedas por dolor:**
- "plantar fasciitis insoles for heavy person"
- "insoles for heel pain 200 lbs"
- "arch support for overweight"
- "insoles for flat feet heavy duty"

**Búsquedas por solución/marca:**
- "powerstep insoles vs superfeet"
- "best insoles for work boots 2026"
- "HSA eligible insoles" [FUTURO — post SIGIS]
- "PORON insoles" [nicho pero alto intent]

**Nota:** frases son hipótesis basadas en conocimiento de categoría. Validar con Search Query Performance y Search Terms Report reales. Ref → AUT-050 cuando esté activo.

### B6. Messaging

Ref → PLB_COPY.Wedge Goliath USA para 3 capas de mensaje, secuencia de bullets, reglas y anti-patterns.

### B7. Objeciones

| Objeción | Frecuencia estimada |
|---|---|
| "Es otra plantilla más" | Alta |
| "Muy caro vs Dr. Scholl's" | Alta |
| "¿Cabe en mi work boot?" | Media |
| "Las plantillas firmes me incomodan" | Media |
| "No confío en marcas que no conozco" | Media |

Ref → PLB_COPY.Anti-patterns Goliath USA para respuestas en copy.

### B8. Purchase triggers

| Trigger | Tipo | Timing |
|---|---|---|
| Dolor crónico que ya no aguanta | Dolor | Todo el año |
| Recomendación de compañero de trabajo | Social proof | Todo el año |
| Doctor le dice que use soporte | Autoridad | Todo el año |
| Plantillas viejas ya no sirven | Reposición | Cada 6-12 meses |
| HSA/FSA balance por expirar | Financiero | Q4 (Oct-Dic) |
| Nuevo trabajo que requiere estar de pie | Vida | Todo el año |
| Prime Day / Black Friday | Promocional | Julio + Noviembre |

### B9. Competidores en la mente del buyer

| Competidor | Posición | Precio | Weakness que Goliath ataca |
|---|---|---|---|
| Dr. Scholl's | Mass market, bajo precio | $12-20 | No es para 225+ lbs, genérico |
| PowerStep | Mid-premium, clínico | $25-45 | Sin PORON, no heavy-duty específico |
| Superfeet | Premium, outdoor-first | $40-60 | Diseñado para outdoor, no work boots |
| Valsole | Budget Amazon | $15-25 | China genérica, sin diferenciador |

Ref → ENT_MKT_COMPETENCIA para análisis completo [CEO-ONLY].

---

## C. Observaciones del sistema (capa automática)

### C1. Taxonomía de señales

| Fuente | Peso base | Ocurrencias mínimas | Decay |
|---|---|---|---|
| amazon_review | 0.9 | 2 | 180 días |
| amazon_search_term | 0.6 | 5 | 90 días |
| amazon_ppc | 0.5 | 10 | 60 días |
| scanner | 0.95 | 1 | 365 días |
| portal_query | 0.7 | 3 | 60 días |
| manual (CEO) | 1.0 | 1 | sin decay |

### C2. Atributos extraíbles (taxonomía cerrada)

job_role, pain_point, weight_range, hours_standing, work_context, shoe_type, purchase_trigger, sentiment, competitor_mentioned.

Atributos fuera de taxonomía → `other_attributes` para revisión CEO.

### C3. Observaciones acumuladas

[VACÍO — se llena cuando AUT-050 esté activo o CEO ingrese manualmente]

---

## D. Goliath × BR (alianza/master distributor)

### D1. Ficha de nodo

```
Producto: Goliath (ref → ENT_PROD_GOL)
Mercado: BR (ref → ENT_MERCADO_BR)
Nodo comercial: [PENDIENTE — alianza con jugador existente calzado seguridad]
Cadena: FACTORY-CN → [nodo logístico BR] → punto de venta / empresa
Certificación requerida: CA (INMETRO), ABNT NBR 16679 para etiquetado
Regulatorio: ANVISA RDC 830 (scanner), LGPD (datos biométricos)
Canal: Retail (farmacia, calzado) + Industrial B2B directo
Precio: [PENDIENTE — CEO define] vs Marluvas genérica como referencia
Confidence: hypothesis
```

### D2. Wedge BR

```
Statement: "Proteção biomecânica para jornadas de 8-12h em bota de segurança — Tecnologia Americana Inside"

Estructura:
  Contexto de búsqueda : bota de segurança + jornada longa de pé
  Beneficio comprable  : redução de fadiga + proteção de impacto
  Calificador          : trabalhadores 100+ kg / carga pesada
  Prueba               : PORON XRD (Rogers Corp) — tecnología americana importada
  
Diferencia vs USA: el peso es menos central como calificador.
  En BR el driver es cumplimiento NR + confort en jornada larga.
  "Tecnologia Americana" pesa MÁS en BR que en USA (premium importado).
```

### D3. Buyer BR — quién es

**Buyer primario: decisor de compra (NO es el usuario final)**

| Atributo | Valor | Nota |
|---|---|---|
| Rol | Técnico SSO / Responsable de segurança / Compras | El trabajador no elige su plantilla — la empresa la compra |
| Motivación | Cumplir NR-6 (EPIs), reducir afastamentos, demostrar cuidado | Regulatorio + productividad + liability |
| Contexto | Indústria, construção, logística, agro | Sectores con NR exigentes |
| Decisión | Por lote, no individual. MOQ aplica | Ref → ENT_COMERCIAL_MODELOS |
| Canal | Distribuidor visitante, feria de segurança, scanner demo | No busca en Amazon — recibe visita del operador |

**Buyer secundario: usuario final (trabajador)**

| Atributo | Valor |
|---|---|
| Peso | Variable — no es calificador principal como en USA |
| Horas de pie | 8-12 horas, turnos rotativos |
| Calzado | Bota de segurança com biqueira (steel/composite toe) |
| Pain point | Fadiga, dor no calcanhar, desconforto na bota rígida |
| Voz | No tiene — la empresa compra por él |

### D4. Pain points BR — rankeados

| # | Pain point | Quién lo siente | Confidence |
|---|---|---|---|
| 1 | Cumplimiento NR / evitar multas por EPI inadecuado | Decisor SSO | hypothesis |
| 2 | Afastamentos / ausentismo por problemas de pie | Decisor SSO + RH | hypothesis |
| 3 | Fadiga al final del turno / productividad | Trabajador + supervisor | hypothesis |
| 4 | Rotación de calzado / durabilidad de plantilla genérica | Compras | hypothesis |
| 5 | Desconforto en bota de segurança rígida | Trabajador | hypothesis |

### D5. Buyer language BR

**Decisor SSO (B2B):**
- "palmilha para bota de segurança"
- "EPI para conforto"
- "reduzir afastamento por problema no pé"
- "palmilha ergonômica para trabalho em pé"
- "NR-6 palmilha"

**Búsqueda online (si Amazon BR):**
- "palmilha para trabalho em pé"
- "palmilha bota segurança conforto"
- "melhor palmilha para quem fica em pé o dia todo"
- "palmilha para trabalhador pesado"

### D6. Messaging BR

Ref → PLB_COPY.Wedge Goliath BR para 3 capas de mensaje y anti-patterns.

### D7. Objeciones BR

| Objeción | Quién la dice |
|---|---|
| "É caro comparado com Marluvas" | Compras |
| "Marca desconhecida no Brasil" | SSO / Compras |
| "Isso não é EPI certificado" | SSO |
| "Já temos fornecedor" | Compras |
| "Parece dura / desconfortável" | Trabajador (feedback) |

Ref → PLB_COPY.Anti-patterns Goliath BR para respuestas.

### D8. Purchase triggers BR

| Trigger | Tipo | Timing |
|---|---|---|
| Renovação anual de EPIs | Presupuesto | Q1 (inicio año fiscal) |
| Auditoria de segurança / fiscalização | Regulatorio | Todo el año |
| Acidente ou quase-acidente | Reactivo | Evento |
| Feria FISP / Expo Proteção / similar | Comercial | Calendario ferias |
| Resultado positivo del scanner demo | Evidencia | Post-visita operador |

---

## E. Goliath × CR (piloto B2B)

### E1. Ficha de nodo

```
Producto: Goliath (ref → ENT_PROD_GOL)
Mercado: CR (ref → ENT_MERCADO_CR)
Nodo comercial: MWT-CR (operación directa — CEO local)
Cadena: FACTORY-CN → bodega CR → punto de venta / empresa
Certificación requerida: [PENDIENTE — MEIC investigar]
Canal: B2B directo (piloto manual con scanner)
Precio: [PENDIENTE — CEO define en CRC]
Confidence: hypothesis
```

### E2. Wedge CR

```
Statement: "Soporte biomecánico para jornadas largas — Ingeniería costarricense con Tecnología Americana"

Estructura:
  Contexto     : trabajo de pie + bota industrial o calzado cerrado
  Beneficio    : reducción de fatiga + protección de impacto
  Calificador  : trabajadores de jornadas 8+ horas
  Prueba       : PORON XRD + "Ingeniería del MedTech Hub de Costa Rica"
  
Diferencia vs USA: peso no es calificador. "100+ kg" menos relevante en CR.
Diferencia vs BR: el ángulo local ("ingeniería costarricense") tiene valor en CR.
  En BR lo importado es premium. En CR lo local + importado es orgullo + calidad.
  ref → ENT_MARCA_ORIGEN: "Ingeniería del MedTech Hub de Costa Rica"
```

### E3. Buyer CR

**Buyer primario: dueño/gerente de empresa pequeña-mediana**

| Atributo | Valor |
|---|---|
| Rol | Dueño, gerente de operaciones, encargado de salud ocupacional |
| Tamaño empresa | 10-100 empleados (PYME industrial) |
| Motivación | Bienestar de empleados + productividad + diferenciarse como empleador |
| Canal | Visita directa del CEO/operador con scanner |
| Decisión | Personal — el dueño decide, no hay departamento de compras formal |

### E4. Pain points CR

| # | Pain point | Confidence |
|---|---|---|
| 1 | Empleados se quejan de dolor de pies / fatiga | hypothesis |
| 2 | Rotación de personal (trabajo duro = gente se va) | hypothesis |
| 3 | No sabe que existe solución especializada (usa plantillas genéricas o nada) | hypothesis |
| 4 | Quiere mejorar condiciones pero opciones locales son limitadas | hypothesis |

### E5. Buyer language CR (ES)

- "plantillas para botas de trabajo"
- "plantillas para estar de pie todo el día"
- "cómo reducir el cansancio en los pies"
- "plantillas ortopédicas para trabajo"

### E6. Messaging CR

Ref → PLB_COPY.Wedge Goliath CR para 3 capas de mensaje y anti-patterns.

### E7. Objeciones CR

| Objeción |
|---|
| "Muy caro" |
| "No conozco la marca" |
| "Ya compramos plantillas en la farmacia" |
| "¿Y si no les gusta a los empleados?" |

Ref → PLB_COPY.Anti-patterns Goliath CR para respuestas.

### E8. Valor del piloto CR para el sistema MWT

Este piloto no es para vender plantillas — es para validar:
- ¿El scan convierte? (attach rate)
- ¿El protocolo es ejecutable sin el CEO? (operator playbook)
- ¿El decisor PYME compra por evidencia o por relación?
- ¿El mensaje "ingeniería CR + tecnología USA" resuena?
- ¿Los datos del scan son capturables y útiles? (outcome linkage)

Ref → PLB_PILOTO_B2B (pendiente GRW-02, trigger: operador CR identificado)

---

## F. Bloques adicionales (placeholder)

| Producto × Mercado | Status | Trigger | Nota |
|---|---|---|---|
| Bison × BR | Placeholder | Cuando Bison entre en roadmap activo | Bison tiene PORON + 3 arcos = candidato natural para BR industrial. Buyer idéntico a Goliath BR pero con fitting personalizado (LOW/MED/HGH) |
| Bison × USA | Placeholder | Cuando Bison lance en Amazon USA | Compite en segmento diferente a Goliath: alto impacto + movimiento variado (construcción, hiking) |
| Leopard × USA | Placeholder | Cuando Leopard lance | Personalización (ShockSphere) = ángulo diferenciador único |
| Orbis × USA | Placeholder | Cuando Orbis lance | Runner recreativo — buyer completamente diferente |
| Velox × USA | Placeholder | Cuando Velox lance | Sport performance — buyer completamente diferente |

---

## Z. Pendientes

| ID | Pendiente | Desbloquea |
|---|---|---|
| Z1 | Validar buyer language USA con Search Query Performance real | B5 pasa de hypothesis a validated |
| Z2 | Inscripción SIGIS para HSA/FSA | Layer 3 USA |
| Z3 | Análisis de reviews reales Goliath (cuando haya 20+) | B3, B4 validados |
| Z4 | Análisis de reviews competidores (PowerStep, Superfeet) | B7, B9 validados |
| Z5 | Research buyer language PT-BR real (cuando alianza BR activa) | D5 validado |
| Z6 | Research competidores BR (Marluvas, Bracol, importados) | D7 validado |
| Z7 | Definir precio Goliath CR en CRC | E1 completo |
| Z8 | Investigar regulatorio MEIC para plantillas en CR | E1 certificación |

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO
Origen: Sesión growth research 2026-03-13 (ref → REPORTE_SESION_GROWTH_RESEARCH_20260313)
