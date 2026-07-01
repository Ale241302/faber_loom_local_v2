# ENT_COMP_AMAZON — Amazon Account Health & Compliance
id: ENT_COMP_AMAZON
status: DRAFT
visibility: [INTERNAL]
version: 1.0
domain: Compliance (IDX_COMPLIANCE)
classification: ENTITY — Data pura: políticas y reglas de Amazon aplicables a MWT
aplica_a: [MWT]

refs:
  - PLB_OPS_AMAZON (operaciones que consumen estas reglas)
  - PLB_EXPERIMENTACION (cambios de listing validados contra policies)
  - PLB_ADS (advertising policies)
  - POL_CLAIMS_SCANNER (claims scanner validados contra Amazon)
  - POL_ROGERS (uso de marca PORON en Amazon)
  - ENT_COMP_CONTENT_RULES.A (claims permitidos/prohibidos)

---

## A. Account-Level Policies

### A1. Seller Code of Conduct — resumen ejecutivo

Amazon exige que sellers operen con integridad. Principios clave aplicables a MWT:

- **Representación honesta:** no misrepresentar identidad, productos, o condición de los productos
- **Actuar con fairness:** no manipular reviews, ratings, search rankings, ni Buy Box
- **No dañar o abusar:** no amenazar, acosar ni comunicar inapropiadamente con buyers
- **Respetar la plataforma:** no circumvent Amazon systems (review manipulation, fake accounts, rank manipulation)

**Consecuencia de violación:** warning → suspensión temporal → desactivación permanente. No hay apelación garantizada.

### A2. Product authenticity requirements

- Todo producto listado en Amazon DEBE ser auténtico
- MWT vende producto propio → riesgo bajo, pero debe mantener: facturas de proveedor (ref → SCH_PROFORMA_MWT), evidencia de cadena de suministro, Brand Registry activo
- Si un tercero vende producto MWT sin autorización → ref → PLB_OPS_AMAZON.D3 (hijackers)
- Amazon puede solicitar facturas en cualquier momento → tener preparadas

### A3. Pricing policy (fair pricing)

- Amazon prohíbe precios "significativamente más altos" que otros canales o que el precio reciente del mismo producto
- **Impacto MWT:** si Goliath se vende en otro canal (futuro) a precio menor, Amazon puede suprimir el listing por "unfair pricing"
- **Regla operativa:** mantener Amazon como precio igual o menor que cualquier otro canal público
- Ref → ENT_COMERCIAL_PRICING para política de pricing interna

### A4. Multiple accounts policy

- Amazon permite UNA cuenta de seller por persona/entidad salvo aprobación explícita
- MWT-CR opera una cuenta. Si FRANQ-BR necesita cuenta propia → solicitar aprobación de Amazon con justificación de negocio separado
- **Regla:** nunca abrir segunda cuenta sin aprobación previa de Amazon

### A5. Communication policy (buyer-seller messaging)

- Solo se puede contactar buyers a través de Buyer-Seller Messaging de Amazon
- Prohibido: solicitar que compren fuera de Amazon, solicitar datos personales, marketing no solicitado
- Permitido: responder preguntas del buyer, resolver problemas de pedido, solicitar UN review (sin sesgo)
- Ref → PLB_SUPPORT para protocolo completo de comunicación post-venta

---

## B. Listing-Level Policies

### B1. Prohibited claims

Amazon prohíbe claims específicos en listings. Intersección con ref → ENT_COMP_CONTENT_RULES.A y POL_CLAIMS_SCANNER:

| Categoría | Ejemplo prohibido | Regla |
|-----------|------------------|-------|
| Medical claims | "cura plantar fasciitis", "tratamiento médico" | Prohibido salvo que producto sea medical device aprobado FDA |
| Superlativos no verificables | "la mejor plantilla del mundo", "#1 insole" | Prohibido salvo evidencia verificable (ej: Amazon Best Seller badge es auto-generado, no un claim) |
| Garantías absolutas | "garantizado que elimina el dolor" | Prohibido — usar "designed to help reduce..." |
| FDA/medical framing | "doctor recommended" sin evidencia | Prohibido salvo endorsement documentado |
| Competitor disparagement | "mejor que PowerStep" | Prohibido — comparaciones denigrantes |

Ref → POL_ROGERS para uso de marca PORON (Rogers Corp) en Amazon listings.
Ref → POL_CLAIMS_SCANNER para validación automática de claims.

### B2. Image requirements

| Posición | Tipo | Requisitos clave |
|----------|------|-----------------|
| Main image | Producto solo, fondo blanco puro (RGB 255,255,255) | Sin texto, logos, watermarks, bordes. Producto ocupa ≥85% del frame. |
| Images 2-6 | Infographic | Texto overlay permitido. Mostrar features, dimensiones, materiales, comparativas. |
| Images 7-8 | Lifestyle | Producto en uso. Contexto de uso (work boots, standing). |
| Image 9 | Size chart / compatibility | Tabla de tallas o compatibilidad con tipos de calzado. |

**Requisitos técnicos:** mínimo 1000px lado más largo (ideal 2000px), formato JPEG/PNG/TIFF/GIF, sin animación en main image.

Ref → ENT_COMP_CONTENT_RULES.C para guidelines de marca visual que aplican sobre estas reglas.

### B3. SIGIS (Safety, Identity, and Graphics Information System)

- Para elegibilidad HSA/FSA, el producto debe estar inscrito en SIGIS
- Ref → ENT_COMP_CONTENT_RULES.A para estado actual de inscripción SIGIS
- Status: [PENDIENTE — inscripción no iniciada. Ref → ENT_MKT_ICP.B1 nota HSA/FSA]

### B4. Backend search terms rules

| Regla | Detalle |
|-------|--------|
| Límite | 250 bytes (no caracteres — caracteres especiales/acentos ocupan más) |
| No repetir título | Keywords del título ya se indexan — no desperdiciar bytes |
| No competitor brands | Prohibido usar nombres de competidores en backend (ej: "powerstep", "superfeet") |
| No ASINs | Prohibido incluir ASINs de competidores |
| No "by Amazon" | Prohibido claims falsos de asociación |
| Separador | Espacios (no comas) |
| Case | Insensible — no importa mayúsculas |

Ref → ENT_MKT_KEYWORDS para keywords activos y backend terms por producto × mercado.
Ref → LOC_{PROD}_{LANG}.G7 para backend terms ensamblados.

---

## C. Advertising Policies

### C1. Sponsored Products

- Targeting: keywords y product targeting permitidos
- Creative: usa título e imagen del listing — no se puede personalizar
- Restricción: producto debe estar en Buy Box para mostrar ad
- No se pueden usar keywords de competitor brands en ad copy (sí en targeting)

### C2. Sponsored Brands

- Requiere Brand Registry
- Creative personalizable: headline, logo, productos seleccionados
- Headline: no puede incluir claims prohibidos (ref → B1), no exclamaciones excesivas, no presión ("compra ahora o pierde")
- Logo: debe cumplir brand guidelines de Amazon (no fondo transparente en algunos formatos)

### C3. Sponsored Display

- Targeting: audiencias, product targeting, views remarketing
- Creative: auto-generado o custom. Mismas restricciones de claims que B1.
- Restricción: no se puede target audiencias menores de 18 años

### C4. General ad restrictions

- No claims médicos en ads
- No contenido engañoso o misleading
- No landing pages fuera de Amazon (Sponsored Products/Brands van al listing)
- Budget y bidding: sin restricciones de Amazon, pero ref → PLB_ADS para reglas internas MWT

Ref → PLB_ADS para estrategia y gestión de campañas PPC.

---

## D. FBA Policies

### D1. Prep requirements

| Categoría producto | Prep requerido |
|-------------------|---------------|
| Productos en bolsa/bag (como insoles) | Bag transparente sellado con suffocation warning si apertura >5" |
| Productos en caja individual | Caja cerrada, barcode visible |
| Sets/bundles | Empacar como unidad única, label "Sold as set, do not separate" |

**MWT aplica:** insoles empacadas en bolsa individual. Verificar que empaque cumple suffocation warning si bolsa es >5".
Ref → ENT_OPS_EMPAQUE_FISICO para specs de empaque.

### D2. Labeling (FNSKU vs commingled)

| Opción | Descripción | Riesgo | Decisión MWT |
|--------|-------------|--------|-------------|
| FNSKU (stickerless commingled OFF) | Cada unit tiene barcode único de MWT. Amazon no mezcla con inventory de otros sellers. | Bajo | **RECOMENDADO** |
| Commingled (stickerless) | Amazon mezcla tu inventory con otros sellers del mismo UPC. | Alto — si otro seller envía counterfeit, se mezcla con el tuyo | **NO USAR** |

**Regla MWT:** siempre FNSKU. Nunca commingled. Protege autenticidad del producto.

### D3. Shipping requirements

- Envíos a FBA deben cumplir shipping plan de Seller Central
- Cajas: máximo 50 lbs, dimensiones dentro de límites FBA
- Labels: cada caja con shipping label de Amazon
- Carrier: usar Amazon partnered carrier cuando sea cost-effective
- Ref → ENT_OPS_LOGISTICA para cadena completa FACTORY-CN → FBA-US

### D4. Removal/disposal policies

- Se puede crear removal order en cualquier momento
- Costo removal: ~$0.50-1.00/unit (varía por tamaño/peso)
- Costo disposal: ~$0.15-0.30/unit
- Timeline: Amazon procesa removals en 10-14 business days (puede ser más en Q4)
- Ref → PLB_OPS_AMAZON.B5 para protocolo de liquidación

---

## E. Enforcement & Appeals

### E1. Tipos de enforcement

| Nivel | Nombre | Impacto | Reversible |
|-------|--------|---------|-----------|
| 1 | Warning / coaching | Notificación, sin impacto inmediato | N/A — es informativo |
| 2 | Listing suppression | ASIN desactivado, no visible | Sí — corregir issue y reactivar |
| 3 | Listing removal | ASIN eliminado del catálogo | Sí — appeal con evidencia |
| 4 | Account suspension | Cuenta desactivada temporalmente | Sí — Plan of Action (POA) |
| 5 | Account deactivation | Cuenta permanentemente cerrada | Difícil — POA + escalación ejecutiva |

### E2. Framework de appeal por tipo

**Para listing suppression/removal:**
1. Identificar causa exacta (performance notification en Seller Central)
2. Corregir el issue en el listing
3. Abrir case explicando: qué causó el problema, qué se corrigió, qué medidas preventivas se implementaron
4. Adjuntar evidencia si aplica (facturas, imágenes corregidas, etc.)

**Para account suspension:**
1. **NO responder impulsivamente** — tomar 24-48h para preparar POA
2. Plan of Action debe incluir: a) Root cause analysis, b) Corrective actions already taken, c) Preventive measures to avoid recurrence
3. Ser conciso, factual, profesional. No emocional.
4. Enviar vía Performance Notifications en Seller Central
5. Si rechazan primera vez: revisar feedback, mejorar POA, reenviar
6. Escalamiento: ref → PLB_OPS_AMAZON.C2

Ref → PLB_OPS_AMAZON.C (Case Management) para protocolo completo de gestión de cases.

---

## Z. Pendientes

| ID | Pendiente | Tipo | Desbloquea |
|----|-----------|------|-----------|
| Z1 | Verificar prep requirements específicos para categoría insoles | Operativo | D1 compliance |
| Z2 | Confirmar FNSKU setup en cuenta actual | Operativo | D2 compliance |
| Z3 | Inscripción SIGIS para HSA/FSA | Regulatorio | B3 + ENT_MKT_ICP.B1 |

---

Stamp: DRAFT — pendiente aprobación CEO
Vencimiento: [fecha aprobación + 90 días]
Estado: DRAFT
Aprobador final: CEO

Changelog:
- v0.1 (2026-03-14): header normalizado + status: STUB (Ola A).
- v1.0 (2026-03-15): STUB → DRAFT. Framework completo: 5 secciones (Account Policies, Listing Policies, Ad Policies, FBA Policies, Enforcement). Refs cruzadas a PLB_OPS_AMAZON, PLB_EXPERIMENTACION, PLB_ADS, POL_CLAIMS_SCANNER, POL_ROGERS, ENT_COMP_CONTENT_RULES.A.
