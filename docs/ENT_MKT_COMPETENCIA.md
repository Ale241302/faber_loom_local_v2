# ENT_MKT_COMPETENCIA [CEO-ONLY]
id: ENT_MKT_COMPETENCIA
version: 1.0
status: DRAFT
visibility: [CEO-ONLY]
domain: Marketplace (IDX_MARKETPLACE)
classification: ENTITY — Data pura: análisis competitivo por mercado
aplica_a: [MWT]

refs:
  - ENT_MKT_ICP (validación wedge — sección B9 competidores en mente del buyer)
  - ENT_PROD_COMPARATIVA (diferenciación técnica producto)
  - PLB_EXPERIMENTACION.R5 (trigger competencia que dispara test)
  - ENT_OPS_DEMAND_PLANNING (contexto de mercado para planning)

---

## A. Framework de análisis competitivo

### A1. Tabla por competidor — USA

| Campo | PowerStep | Superfeet | Valsole | Dr Scholl's | [Nuevo entrante] |
|-------|-----------|-----------|---------|-------------|-------------------|
| Marca | PowerStep | Superfeet | Valsole | Dr. Scholl's | [PENDIENTE — detección] |
| Rango de precio | $25-45 | $40-60 | $15-25 | $12-20 | — |
| Rating promedio | [PENDIENTE — Helium 10] | [PENDIENTE — Helium 10] | [PENDIENTE — Helium 10] | [PENDIENTE — Helium 10] | — |
| Review count | [PENDIENTE — Helium 10] | [PENDIENTE — Helium 10] | [PENDIENTE — Helium 10] | [PENDIENTE — Helium 10] | — |
| BSR range | [PENDIENTE — Helium 10] | [PENDIENTE — Helium 10] | [PENDIENTE — Helium 10] | [PENDIENTE — Helium 10] | — |
| Monthly revenue est. | [PENDIENTE — Helium 10/AMZScout] | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | — |
| Wedge/posicionamiento | Mid-premium clínico, orthotic-style | Premium outdoor, rigid support | Budget Amazon, genérico | Mass market, farmacia/retail | — |
| Fortaleza | Reputación clínica, amplio catálogo | Brand equity outdoor, retail distribution | Precio bajo, reviews volume | Brand awareness masivo, distribución retail | — |
| Debilidad | Sin PORON, no heavy-duty específico | Diseñado outdoor no work boots, precio alto | Sin diferenciador técnico, China genérica | Genérico, no para 225+ lbs, commodity | — |

**Nota:** precios son rangos observados. Datos de rating, reviews, BSR y revenue requieren Helium 10 o AMZScout para ser precisos. No inventar.

### A2. Criterio de detección de nuevos entrantes

Un nuevo competidor entra al radar cuando cumple AL MENOS 2 de:
- BSR ≤200 en subcategoría "Shoe Insoles" por más de 30 días
- Review velocity >20 reviews/mes (indica lanzamiento agresivo o manipulación)
- Precio en rango $25-50 (compite directamente con Goliath)
- Claims similares a Rana Walk (work boots, heavy duty, biomechanical)
- Ad spend visible en Sponsored Products/Brands en keywords core de Goliath

---

## B. Posicionamiento relativo

### B1. Mapa perceptual 2×2 — USA

```
Ejes:
  X: Precio (bajo → alto)
  Y: Especialización (genérico → especializado heavy-duty/work)

              ESPECIALIZADO
                   ↑
                   |
                   |    ★ Rana Walk Goliath
                   |        ($37.99, heavy-duty 225+ lbs)
                   |
                   |                    · Superfeet
                   |                      ($40-60, outdoor)
                   |
                   |    · PowerStep
                   |      ($25-45, clínico general)
                   |
     BAJO ─────────┼──────────── ALTO → Precio
                   |
                   |
         · Valsole |
          ($15-25) |
                   |
      · Dr Scholl's|
        ($12-20)   |
                   |
              GENÉRICO

Posiciones: hypothesis — validar con datos de mercado reales.
```

### B2. Posicionamiento por línea Rana Walk

| Línea | Posición esperada vs competidores | Ref |
|-------|----------------------------------|-----|
| Goliath | Premium especializado heavy-duty. Por encima de PowerStep en especialización, debajo de Superfeet en precio. | ENT_PROD_GOL |
| Orbis | Runner recreational. Compite en territorio diferente — vs Superfeet Run, Sof Sole. | ENT_PROD_ORB |
| Velox | Sport performance. Compite vs Superfeet Run premium, Currex. | ENT_PROD_VEL |
| Leopard | Personalización (ShockSphere). Sin competidor directo en insoles con personalización de impacto. | ENT_PROD_LEO |
| Bison | High-impact variado. Overlap con Goliath en work pero con 3 arcos (LOW/MED/HGH). | ENT_PROD_BIS |

Ref → ENT_PROD_COMPARATIVA para diferenciación técnica detallada entre productos Rana Walk.

---

## C. Competitive intelligence triggers

### C1. Qué monitorear

| Señal | Impacto potencial | Acción |
|-------|-------------------|--------|
| Price change (>10%) en competidor top 4 | Afecta percepción de valor Goliath | Evaluar ajuste de precio o messaging |
| New ASIN de competidor en subcategoría | Nuevo competidor o nueva línea | Analizar listing, pricing, diferenciación |
| Review velocity spike (>3x promedio mensual) | Posible manipulación o lanzamiento agresivo | Monitorear, reportar si sospecha manipulación |
| A+ content update en competidor | Cambio de estrategia de messaging | Evaluar si hay insights para nuestro A+ |
| Ad spend shift visible (aparece/desaparece en keywords core) | Cambio de estrategia PPC | Evaluar impacto en CPC y ajustar bids |
| BSR drop significativo en competidor | Competidor ganando tracción | Investigar causa (precio, reviews, ads) |

### C2. Cadencia y método

| Fase | Método | Frecuencia | Responsable |
|------|--------|-----------|-------------|
| Actual (manual) | Revisión manual de listings competidores en Amazon | Mensual | CEO |
| Futuro (herramientas) | Helium 10 Market Tracker / AMZScout competitor monitoring | Semanal automático | Operador |
| Futuro (pipeline) | Alertas automáticas vía AUT (ref → ENT_PLAT_AUTOMATIONS) | Diario | Sistema |

### C3. Trigger de experimentación

Cuando se detecta un cambio competitivo significativo (C1), se evalúa si dispara un test:
- Ref → PLB_EXPERIMENTACION.R5 (regla: cambio de competidor dispara experimento)
- Ejemplo: competidor baja precio 20% → test de nuevo pricing o messaging de valor
- Decisión de test: CEO aprueba

---

## D. Por mercado

### D1. USA — competidores conocidos

Los 4 competidores documentados en A1. Subcategoría: "Shoe Insoles" en Amazon.com.

Slots de expansión:
- [PENDIENTE — Helium 10 top 10 por BSR en subcategoría]
- [PENDIENTE — AMZScout market share analysis]

### D2. Brasil — competidores (hallazgos Gemini v4.4.1)

**Datos indexados como hypothesis — validar en FIMEC/Belo Horizonte (marzo 2026).**

| Campo | Marluvas | Bracol | Importados premium |
|-------|----------|--------|-------------------|
| Tipo | Nacional | Nacional | Importado |
| Rango precio palmilhas | R$ 30-60 | R$ 20-50 | R$ 100+ |
| Material principal | PU genérica | PU anatómica, claims antimicrobianos | Materiales técnicos variados |
| Canales | E-commerce, distribuidores B2B | Mercado Livre, Super EPI, distribuidores | Especializados |
| Posicionamiento | Industrial / Confort — foco en bota, palmilha es accesorio | Mass market — palmilhas de PU como mejora de confort | Premium — alta durabilidad |
| Fortaleza | Distribución B2B masiva, lealtad de marca, integración vertical (bota+palmilha) | Precio accesible, claims antimicrobianos, presencia en e-commerce | Materiales superiores |
| Debilidad | Enfoque primario en la bota; palmilhas son genéricas de PU sin material de impacto premium | Tecnologías básicas (EVA/PU), sin diferenciador técnico real | Escasa penetración en lotes B2B por precio alto |

**Contexto de mercado:**
- Las empresas BR compran calzado como EPI principal. Las palmilhas se venden por separado como mejoras de confort.
- Ningún competidor nacional ofrece material premium de absorción de impacto (PORON XRD o equivalente).
- Goliath con PORON XRD tiene espacio en el rango R$80-120: arriba de nacionales, debajo de importados especializados.
- El buyer es el técnico SSO / compras, no el trabajador. La venta es B2B por lote.

**Competidores adicionales por confirmar:**
- [PENDIENTE — Dr. Scholl's presencia B2B industrial BR: probablemente mínima, verificar]
- [PENDIENTE — marcas brasileñas de palmilhas biomecánicas (no solo genéricas EVA): no identificadas por Gemini]

Confidence: hypothesis
Fuente: Gemini research 2026-03-15. Validar con datos de campo en FIMEC/Expo Proteção.

### D3. Costa Rica — competidores

[PENDIENTE — NO INVENTAR. Mercado local de plantillas genéricas, sin players especializados conocidos]

**Lo que se sabe (hypothesis):**
- Plantillas genéricas de farmacia (Dr. Scholl's importado, marcas blancas)
- No hay competidor especializado en work boots / industrial
- Canal principal: farmacias, ortopedias, tiendas de calzado
- Oportunidad: mercado sin educación sobre plantillas biomecánicas especializadas
- Ref → ENT_MKT_ICP.E (ICP Goliath × CR) para contexto del buyer

**Nota:** los competidores cambian por mercado. El framework de análisis (secciones A-C) es el mismo. Los datos por mercado se llenan independientemente.

---

## Z. Pendientes

| ID | Pendiente | Tipo | Desbloquea |
|----|-----------|------|-----------|
| Z1 | Llenar datos USA con Helium 10/AMZScout (rating, reviews, BSR, revenue) | Research | A1 completo |
| Z2 | Expandir top 10 competidores USA por BSR | Research | A1 + A2 |
| Z3 | Research competidores BR (Marluvas, Bracol, importados) | Research | D2 |
| Z4 | Research competidores CR (farmacias, ortopedias) | Research | D3 |
| Z5 | Validar posiciones en mapa perceptual con datos reales | Research | B1 hypothesis → validated |

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO

Changelog:
- v0.1 (2026-03-14): version: field agregado (normalización Ola A).
- v0.1 (2026-03-14): visibility: INTERNAL + status: DRAFT agregados (Ola B).
- v1.0 (2026-03-15): Expansión completa. 4 secciones: Framework análisis (tabla + criterio nuevos entrantes), Posicionamiento relativo (mapa 2×2 + por línea), CI triggers (monitoreo + cadencia + experimentación), Por mercado (USA datos, BR/CR PENDIENTE). Refs cruzadas a ENT_MKT_ICP, ENT_PROD_COMPARATIVA, PLB_EXPERIMENTACION, ENT_OPS_DEMAND_PLANNING.
