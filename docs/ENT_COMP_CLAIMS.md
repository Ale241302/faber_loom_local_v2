# ENT_COMP_CLAIMS — Claims y Lenguaje de Producto
id: ENT_COMP_CLAIMS
version: 1.0
status: DRAFT
visibility: [PUBLIC]
domain: Compliance (IDX_COMPLIANCE)
stamp: DRAFT — materializado 2026-04-03
aplica_a: [MWT]

refs:
  - POL_CLAIMS_SCANNER (fuente primaria — scanner, extendido a productos)
  - ENT_COMP_AMAZON.B1 (prohibited claims Amazon listings)
  - ENT_COMP_REGULATORIO.B1 (ANVISA — plantilla confort ≠ dispositivo médico)
  - POL_ROGERS (disclaimer PORON® XRD)
  - ENT_MARCA_SELLO (sello "American Technology Inside")

---

## A. Propósito

Definir qué lenguaje es permitido, restringido y prohibido en toda comunicación de producto Rana Walk: fichas técnicas, listings Amazon, packaging, material B2B, presentaciones, website, A+ Content.

**Principio rector:** Las plantillas Rana Walk son productos de confort ergonómico y biomecánico. NO son dispositivos médicos. Todo claim debe mantenerse dentro del territorio wellness/confort/biomecánico. Si el lenguaje cruza hacia diagnóstico o tratamiento médico, se activan regulaciones FDA (USA), ANVISA (BR), Ministerio de Salud (CR) que hoy NO aplican.

Ref → ENT_COMP_REGULATORIO.B1: "Una palmilha biomecânica para absorção de impacto e conforto que no diagnostica ni trata patologías no requiere registro en ANVISA."

---

## B. Semáforo de Claims — Productos

### B1. ROJO — Prohibido (nunca usar en ningún material)

| Término | Razón | Alternativa | Fuente |
|---------|-------|-------------|--------|
| "Diagnóstico" / "diagnosticar" | Acto médico | "Análisis" / "evaluación" | POL_CLAIMS_SCANNER.D |
| "Tratamiento" / "tratar" | Intervención terapéutica | "Recomendación de producto" | POL_CLAIMS_SCANNER.D |
| "Corrige" / "corrección" (como claim absoluto) | Implica dispositivo correctivo médico | "Redistribuye" / "adapta" / "alinea" | POL_CLAIMS_SCANNER.D |
| "Previene lesiones" / "evita problemas" | Claim médico no sustentado | "Ayuda a reducir" / "designed to help reduce" | POL_CLAIMS_SCANNER.D, ENT_COMP_AMAZON.B1 |
| "Ortopédico" como descriptor del producto | Reclasifica ante FDA/ANVISA | "Biomecánico" | POL_CLAIMS_SCANNER.D, ENT_COMP_REGULATORIO.B1 |
| "Pie plano" / "fascitis" / "pronación severa" | Diagnósticos clínicos | "Arco bajo" / "presión medial alta" / no mencionar | POL_CLAIMS_SCANNER.D |
| "Clínicamente probado" | Requiere evidencia clínica formal | "Basado en medición objetiva" / "basado en datos biomecánicos" | POL_CLAIMS_SCANNER.D |
| "Cura" / "elimina el dolor" | Medical claim directo | "Ayuda a mejorar el confort" | ENT_COMP_AMAZON.B1 |
| "Garantizado que elimina el dolor" | Garantía absoluta | "Designed to help reduce discomfort" | ENT_COMP_AMAZON.B1 |
| "Doctor recommended" (sin endorsement) | Requiere evidencia documentada | No usar sin endorsement verificable | ENT_COMP_AMAZON.B1 |
| "#1 insole" / "la mejor del mundo" | Superlativo no verificable | No usar | ENT_COMP_AMAZON.B1 |
| Comparación denigrante con competidor | "Mejor que [marca]" | No usar — comparaciones denigrantes prohibidas | ENT_COMP_AMAZON.B1 |
| "Patología" / "enfermedad" / "condición médica" | Territorio clínico | No usar — referir a profesional | POL_CLAIMS_SCANNER.D |
| "Prescripción médica" | Acto médico | "Recomendación de producto" | POL_CLAIMS_SCANNER.D |
| "Correctiva" (como paleta emocional o descriptor) | Implica dispositivo correctivo | "Postural" / "inteligente" | Extensión POL_CLAIMS_SCANNER |

### B2. AMARILLO — Uso condicional (reformular según contexto)

| Término original | Reformulación permitida | Nota |
|-----------------|------------------------|------|
| "Corrección postural" | "Alineación postural" o "soporte postural" | Evitar "corrección" aislado. "Alineación" es compliance-safe. |
| "Control de pronación" | "Estabilización medial" o "soporte medial" | "Pronation Control" aparece en contextos LOC. Evaluar migrar a "Medial Stabilization" para blindar. |
| "Anti-pronación" | "Soporte lateral/medial" | Evitar el prefijo clínico "anti-" |
| "Para pie plano" | "Para arco bajo" / "low arch support" | POL_CLAIMS_SCANNER.D da esta alternativa exacta |
| "Previene" (en contexto biomecánico) | "Ayuda a reducir" / "designed to help reduce" | ENT_COMP_AMAZON.B1 patrón aceptado por Amazon |
| "Dolor" (como descriptor de usuario) | "Fatiga" / "discomfort" / "molestia" | Evitar en claims de producto. OK en contexto de buyer persona si no es claim. |
| "Arch support" (para ORB) | NO USAR para ORB — ORB no tiene Arch System. Usar "postural alignment" | ORB = LeapCore + NanoSpread únicamente. Ref → ENT_PROD_ORB.C3 |

### B3. VERDE — Permitido sin restricción

| Término | Contexto válido | Fuente que lo valida |
|---------|----------------|---------------------|
| "Absorción de impacto" / "shock absorption" | Todo producto con LeapCore o PORON | ENT_COMP_REGULATORIO.B1 (claim ergonómico) |
| "Redistribución de presión" | Todo producto con NanoSpread | POL_CLAIMS_SCANNER.C |
| "Soporte de arco" / "arch support" | GOL, LEO, BIS, MAN (que tienen arch technology). NO ORB. | LOC files aprobados |
| "Biomecánico" | Descriptor general de la tecnología | POL_CLAIMS_SCANNER.D (alternativa a "ortopédico") |
| "Retorno de energía" / "energy return" | VEL (ThinBoom), GOL (ThinBoom) | LOC_GOL_EN, LOC_VEL_EN |
| "Estabilidad" / "stability" | Todo producto | Todos los LOC |
| "Confort" / "comfort" | Todo producto | ENT_COMP_REGULATORIO.B1 |
| "Reducción de fatiga" / "reduces fatigue" | Todo producto | ENT_COMP_REGULATORIO.B1 (claim ergonómico aceptado BR) |
| "Alineación permanente" / "Permanent Alignment" | ORB | LOC_ORB_EN (aprobado — no implica acto médico) |
| "Distribución de presión" | Todo producto con NanoSpread | POL_CLAIMS_SCANNER.C |
| "Medición objetiva" / "basado en datos" | Scanner + productos en contexto fitting | POL_CLAIMS_SCANNER.C |
| "Nature-Inspired Engineering" | Brand-level | LOC_GOL_EN.B3, LOC_ORB_EN.B3 |
| "Bi-density" / "bi-densidad" | Descriptor técnico de LeapCore | Dato técnico objetivo |
| "E-TPU" / "PU" / "EVA" | Descriptores de material | Dato técnico objetivo |
| "Low profile" | MAN, VEL | LOC_MAN_EN, LOC_VEL_EN |

---

## C. Obligaciones por Producto

### C1. Disclaimer PORON® XRD (ref → POL_ROGERS)

**Aplica a:** GOL, BIS, MAN, ORC (los 4 usan PORON XRD en C1)

**Texto:** [PENDIENTE — NO INVENTAR. ENT_COMP_ROGERS no tiene texto de disclaimer. Obtener de Rogers Corp.]

**Ubicación:** footer de toda ficha técnica, listing, packaging, y material donde se mencione PORON® XRD.

**Nota:** POL_ROGERS actualmente solo lista GOL y BIS. Necesita actualización para incluir MAN y ORC. Ref → ENT_GOB_PENDIENTES CEO-25.

### C2. Sello "American Technology Inside" (ref → ENT_MARCA_SELLO)

**Aplica a:** GOL, BIS. MAN y ORC tienen B4 en sus entities → ENT_MARCA_SELLO necesita actualización. Ref → ENT_GOB_PENDIENTES CEO-26.

### C3. HSA/FSA Eligibility

**Status:** No inscrito en SIGIS. Ref → ENT_COMP_AMAZON.B3, ENT_GOB_PENDIENTES.

**Regla:** NO hacer claims de elegibilidad HSA/FSA hasta completar inscripción SIGIS.

---

## D. Reglas de Aplicación

1. Todo material de producto (listing, ficha técnica, A+ Content, packaging, presentación B2B, website) debe pasar por semáforo B1-B2-B3 antes de publicación.
2. Si un término está en B1 (ROJO) → bloquear publicación, reemplazar con alternativa.
3. Si un término está en B2 (AMARILLO) → reformular según alternativa antes de publicar.
4. Si hay duda → escalar a CEO. Nunca publicar en duda.
5. PLB_COPY y PLB_ADS deben referenciar este archivo como gate de validación.
6. Todo LOC_{PROD}_{LANG} aprobado se considera compliance-safe — pero verificar contra updates de este archivo.

---

## E. Enforcement

- **Detección:** Término ROJO o AMARILLO sin reformular detectado en material de producto
- **Acción:** Bloquear publicación, revertir claim, reemplazar con alternativa de este archivo
- **Severidad:** HARD para ROJO (puede reclasificar producto). MEDIUM para AMARILLO (riesgo reputacional).

---

Changelog:
- v0.1 (2026-03-14): version: field agregado (normalización Ola A).
- v0.1 (2026-03-14): visibility: ALL + status: DRAFT agregados (Ola B).
- v1.0 (2026-04-03): STUB→DRAFT. Semáforo completo GREEN/YELLOW/RED para lenguaje de producto. Fuentes: POL_CLAIMS_SCANNER, ENT_COMP_AMAZON.B1, ENT_COMP_REGULATORIO.B1. +secciones obligaciones por producto (PORON disclaimer, sello, HSA/FSA). +enforcement. Trigger: preparación fichas técnicas producto v2.
