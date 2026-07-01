# ENT_MKT_KEYWORDS
id: ENT_MKT_KEYWORDS
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Marketplace (IDX_MARKETPLACE)
classification: ENTITY — Data pura: keywords por producto × mercado
aplica_a: [MWT]

refs:
  - ENT_MKT_ICP.B5/D5/E5 (buyer language — semillas)
  - SCH_LISTING_AMAZON (assembly — backend terms van a LOC.G7)
  - PLB_ADS (PPC targeting)
  - PLB_EXPERIMENTACION (test copy)
  - PLB_COPY (integración en listings)
  - LOC_{PROD}_{LANG}.G7 (backend terms ensamblados)

---

## A. Estructura por producto × mercado

Cada combinación producto × mercado sigue esta estructura:

```yaml
Producto_Mercado:
  primary_keywords: []        # Top 5-10 por volumen + relevancia
  secondary_keywords: []      # Long-tail, variaciones, sinónimos
  backend_terms: ""           # 250 bytes para Amazon backend (ref → ENT_COMP_AMAZON.B4)
  negative_keywords: []       # Excluir de PPC (irrelevantes, baja conversión)
  competitor_keywords: []     # Keywords de competidores (SOLO para PPC targeting, NUNCA para backend)
  seasonal_keywords: []       # Prime Day, Black Friday, Holiday, Back to Work
  confidence: hypothesis | validated
  source: [PENDIENTE — Helium 10 Cerebro/Magnet | AMZScout | Search Query Performance]
  last_updated: date
```

### Reglas generales de keywords

1. **Backend terms:** 250 bytes máximo. No repetir palabras del título. No competitor brands. Espacios como separador (no comas). Ref → ENT_COMP_AMAZON.B4 para reglas completas.
2. **Competitor keywords:** solo para PPC targeting (Sponsored Products). Nunca en backend terms, título, o bullets. Ref → ENT_COMP_AMAZON.B4 y C1.
3. **Seasonal keywords:** activar en campañas PPC 2-3 semanas antes del evento. Desactivar después.
4. **Negative keywords:** revisar semanalmente en PPC search term reports. Agregar terms que gastan sin convertir.

---

## B. Goliath × USA (EN)

### B1. Semillas de buyer language

Fuente: ENT_MKT_ICP.B5 (buyer language USA). No duplicar — referenciar y expandir.

### B2. Clusters de intención

| Cluster | Intención | Ejemplos de keywords (hypothesis) | Volumen relativo |
|---------|-----------|----------------------------------|-----------------|
| Funcional (contexto de uso) | Busca insoles para su situación de trabajo | "work boot insoles", "insoles for standing all day", "work boot insoles for standing all day" | ALTO |
| Problema (dolor) | Busca solución a un dolor específico | "plantar fasciitis insoles", "insoles for heel pain", "insoles for flat feet" | ALTO |
| Calificador (peso/tamaño) | Busca insoles para persona grande/pesada | "insoles for heavy guys", "insoles for big guys", "insoles 200 lbs", "heavy duty insoles" | MEDIO |
| Material/marca (tech) | Busca material o marca específica | "poron insoles", "poron xrd insoles" | BAJO pero alto intent |
| Comparativo | Busca comparaciones entre marcas | "powerstep vs superfeet", "best insoles for work boots 2026" | MEDIO |
| Reposición | Busca reemplazar plantillas existentes | "replacement insoles for work boots", "insoles that last" | MEDIO |

**Nota:** volúmenes son estimaciones relativas. Validar con Helium 10 Magnet / Cerebro cuando esté activo.

### B3. Primary keywords (hypothesis)

1. work boot insoles
2. insoles for standing all day
3. plantar fasciitis insoles
4. work boot insoles for standing all day
5. insoles for heavy guys
6. heavy duty insoles
7. insoles for flat feet
8. arch support insoles for work boots
9. insoles for heel pain
10. best insoles for work boots

Confidence: hypothesis
Source: ENT_MKT_ICP.B5 buyer language + categoría Amazon knowledge
Validar con: Helium 10 Cerebro (reverse ASIN lookup competidores) + Magnet (keyword research)

### B4. Secondary keywords (hypothesis)

- work boot insoles for big guys
- insoles for 12 hour shifts
- insoles for warehouse workers
- insoles for construction workers
- insoles for heavy person
- plantar fasciitis insoles for heavy person
- arch support for overweight
- steel toe boot insoles
- composite toe boot insoles
- thick insoles for work boots
- shock absorbing insoles
- poron insoles for work boots

### B5. Negative keywords (hypothesis — refinar con PPC data)

- running insoles (diferente use case)
- dress shoe insoles (no es target)
- kids insoles
- women's insoles (si Goliath es unisex, evaluar)
- free insoles
- cheap insoles (si no compete en precio bajo)

### B6. Competitor keywords (PPC targeting only)

- powerstep insoles
- superfeet insoles
- dr scholls work insoles
- valsole insoles
- timberland insoles (brand association)

**REGLA:** estos keywords SOLO se usan en campañas PPC (Sponsored Products targeting). NUNCA en backend terms, título, o bullets. Ref → ENT_COMP_AMAZON.B4.

### B7. Seasonal keywords

| Evento | Keywords | Timing activación |
|--------|----------|-------------------|
| Prime Day | "prime day insoles deal", "insoles prime day" | 2 semanas antes |
| Black Friday | "black friday insoles", "insoles deals" | 2 semanas antes |
| Holiday season | "gift for dad who works on feet", "stocking stuffer work boots" | Noviembre |
| New Year / Back to Work | "new year work boots", "new insoles for work" | Enero |
| HSA/FSA deadline | "hsa eligible insoles", "fsa insoles" [FUTURO — post SIGIS] | Q4 (Oct-Dic) |

### B8. Backend terms

[PENDIENTE — 250 bytes. Ensamblar cuando primary/secondary keywords estén validados con Helium 10]

Ref → LOC_GOL_EN.G7 (hoy dice PENDIENTE). Este campo se llena AQUÍ primero, luego se copia a LOC_GOL_EN.G7 para ensamblaje.

**Lógica de assembly:** tomar keywords de B3 y B4 que NO están en el título del listing. Priorizar por volumen. Eliminar duplicados. Comprimir a 250 bytes.

---

## C. Slots para otros productos y mercados

### C1. Goliath × BR (PT-BR)

Semillas: ENT_MKT_ICP.D5 (buyer language BR)

Primary keywords (hypothesis desde ICP):
- palmilha para bota de segurança
- palmilha para trabalho em pé
- palmilha ergonômica para trabalho
- EPI para conforto
- palmilha bota segurança conforto
- melhor palmilha para quem fica em pé o dia todo

Backend terms: [PENDIENTE — 250 bytes PT-BR. Requiere research específico Amazon.com.br o Mercado Livre]

Confidence: hypothesis
Source: ENT_MKT_ICP.D5

### C2. Goliath × CR (ES)

Semillas: ENT_MKT_ICP.E5 (buyer language CR)

Primary keywords (hypothesis desde ICP):
- plantillas para botas de trabajo
- plantillas para estar de pie todo el día
- plantillas ortopédicas para trabajo
- cómo reducir el cansancio en los pies

Backend terms: [N/A para CR — canal es B2B directo, no marketplace. Keywords son para messaging y copy, no para Amazon backend]

Confidence: hypothesis
Source: ENT_MKT_ICP.E5

### C3. Otros productos × USA

| Producto × Mercado | Status | Trigger de activación |
|-------------------|--------|----------------------|
| Orbis × USA | [PENDIENTE] | Cuando Orbis entre en Fase 2 activa (ref → ENT_PROD_LANZAMIENTO) |
| Velox × USA | [PENDIENTE] | Cuando Velox entre en Fase 2 activa |
| Leopard × USA | [PENDIENTE] | Cuando Leopard entre en roadmap activo |
| Bison × USA | [PENDIENTE] | Cuando Bison entre en roadmap activo |

**Regla:** no pre-crear keywords para productos que no están en pipeline activo. El framework (sección A) está listo para recibir datos cuando se activen.

---

## D. Reglas de gestión

### D1. Keywords son datos vivos

- Se actualizan con cada ciclo de research (mínimo mensual)
- Post-lanzamiento: revisar Search Term Report semanal para descubrir keywords orgánicos
- PPC search term reports alimentan negative keywords y descubren nuevos positives

### D2. Fuente de verdad

- **Este archivo es la fuente canónica de keywords.** Los LOCs consumen de aquí, no al revés.
- Flujo: ENT_MKT_KEYWORDS → LOC_{PROD}_{LANG}.G7 (backend terms) → SCH_LISTING_AMAZON (assembly)
- Si un LOC tiene keywords que no están aquí → migrar aquí y referenciar

### D3. Integración con otros playbooks

- PLB_COPY: keywords informan copy de listings, A+ content, brand story. Ref → PLB_COPY.
- PLB_ADS: keywords alimentan campañas PPC (primary → exact match, secondary → phrase/broad, competitor → product targeting). Ref → PLB_ADS.
- PLB_EXPERIMENTACION: cambios de keywords en listings se testean como experimento. Ref → PLB_EXPERIMENTACION.

---

## Z. Pendientes

| ID | Pendiente | Tipo | Desbloquea |
|----|-----------|------|-----------|
| Z1 | Keyword research Helium 10 Cerebro/Magnet para Goliath USA | Research | B3-B8 validados |
| Z2 | Search Query Performance Report (Seller Central) cuando haya histórico | Dato | B3 hypothesis → validated |
| Z3 | Backend terms assembly Goliath USA (250 bytes) | Ensamblaje | B8 + LOC_GOL_EN.G7 |
| Z4 | Keyword research PT-BR para Amazon.com.br o Mercado Livre | Research | C1 completo |
| Z5 | Keywords para Orbis/Velox/Leopard/Bison cuando se activen | Research | C3 completo |

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO

Changelog:
- v0.1 (2026-03-14): version: field agregado (normalización Ola A).
- v0.1 (2026-03-14): visibility: INTERNAL + status: DRAFT agregados (Ola B).
- v1.0 (2026-03-15): Expansión completa. Estructura por producto×mercado (YAML). Goliath×USA con clusters de intención, primary/secondary/negative/competitor/seasonal keywords, backend terms slot. Goliath×BR y ×CR con semillas desde ICP. Slots para otros productos. Reglas de gestión y flujo de fuente de verdad. Refs cruzadas a ENT_MKT_ICP, SCH_LISTING_AMAZON, PLB_ADS, PLB_EXPERIMENTACION, PLB_COPY, ENT_COMP_AMAZON.
