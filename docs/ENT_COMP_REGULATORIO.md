# ENT_COMP_REGULATORIO
id: ENT_COMP_REGULATORIO
version: 0.1
status: DRAFT
visibility: [PUBLIC]
domain: Compliance (IDX_COMPLIANCE)
Por mercado (ref → ENT_MERCADO_{M} para específicos):
- USA: CBP, SIGIS, Amazon policies
- CR: MEIC (Ley 7623), Ministerio de Salud [PENDIENTE investigar]
- BR: ANVISA, INMETRO, CDC Art.31 — investigación completada (Gemini v4.4.1)
aplica_a: [MWT]

---

## B. Brasil — Regulatorio (hallazgos Gemini v4.4.1)

### B1. ANVISA — NO aplica para palmilha de confort

Una palmilha biomecânica para absorção de impacto e conforto que no diagnostica ni trata patologías **no requiere registro en ANVISA**. Claims como "reduz fadiga" o "absorção de impacto" se consideran claims ergonómicos/de confort y no la convierten en dispositivo médico bajo la RDC 830.

**Importante:** el scanner de presión plantar SÍ puede clasificar como dispositivo Clase I o II bajo RDC 830. [HALLAZGO LLM anterior — verificar con ANVISA antes de comercializar scanner en BR]

### B2. INMETRO / NR-6 — NO aplica si se posiciona como accesorio

El Anexo I de la NR-6 rige los EPIs que requieren Certificado de Aprovação (CA), como el calzado completo. Una plantilla interna vendida de forma separada **no es un EPI autónomo** listado en la NR-6, sino un accesorio.

**Estrategia:** posicionar estrictamente como "Acessório / Palmilha de Conforto". Esto evita la fricción regulatoria del CA. Las empresas pueden ofrecerla a los trabajadores como mejora fuera de las exigencias obligatorias de la NR-6.

ABNT NBR 16679 aplica a etiquetado de calzado de segurança — no a accesorios vendidos por separado.

### B3. LGPD — APLICA para scanner de presión plantar

El escaneo de presión plantar recolecta biometría del pie, clasificado por la LGPD como **dato personal sensible**. Requiere:
- Consentimiento **explícito, libre e informado del trabajador** (no basta la autorización del empleador / técnico de seguridad)
- Base legal: consentimiento del titular (Art. 11, II, a)
- En caso de breach: notificar ANPD (Autoridade Nacional de Proteção de Dados) en 72h
- Ref → PLB_INCIDENT_RESPONSE.B4 para protocolo de notificación
- Ref → ENT_COMP_PRIVACIDAD para política de privacidad general
- [PENDIENTE — crear formulário de consentimiento LGPD para scanner BR]

### B4. Importación

- NCM aplicable: **6406.90.90** (Partes de calçados — palmilhas amovíveis)
- Aranceles: ICMS/IPI [PENDIENTE — tasas exactas según estado de entrada]
- Licencia de importación especial: [PENDIENTE — verificar si NCM requiere LI]

Fuente: Gemini research 2026-03-15. Confidence: hypothesis (requiere confirmación con asesor legal BR para comercialización real).
- MX: NOM, COFEPRIS [PENDIENTE — mercado futuro]

---


## Hallazgos LLM pendientes de verificación
Fuente: REPORTE_SESION_GROWTH_RESEARCH_20260313

- BR: INMETRO Portaria 459 — deadline etiquetado julio 2026 [HALLAZGO LLM — verificar con INMETRO.gov.br antes de actuar]
  Fuente: Gemini vía REPORTE_SESION_GROWTH_RESEARCH_20260313

- BR: LGPD — datos de presión plantar clasificados como datos sensibles. DPO obligatorio para operación scanner [HALLAZGO LLM — verificar con asesor legal BR antes de actuar]
  Fuente: Gemini vía REPORTE_SESION_GROWTH_RESEARCH_20260313

- BR: ANVISA RDC 830/2023 — scanner de presión plantar clasificaría como dispositivo Clase I o II [HALLAZGO LLM — verificar con ANVISA antes de actuar]
  Fuente: Gemini vía REPORTE_SESION_GROWTH_RESEARCH_20260313

---
Changelog:
- v0.1 (2026-03-14): version: field agregado (normalización Ola A).
- v0.1 (2026-03-14): visibility: ALL + status: DRAFT agregados (Ola B).
