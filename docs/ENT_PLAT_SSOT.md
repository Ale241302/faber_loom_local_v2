# ENT_PLAT_SSOT — Single Source of Truth — Mapa
id: ENT_PLAT_SSOT
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
stamp: VIGENTE — 2026-04-01
aplica_a: [MWT]

---

## A. Propósito

Registro centralizado de todas las fuentes únicas de verdad (SSOTs) del sistema. Cuando hay contradicción entre un SSOT y otro documento que lo referencia, el SSOT gana. Ref → POL_DETERMINISMO (Dato Único).

---

## B. Registro de SSOTs

| # | Concepto | SSOT | Ubicación | Consumido por |
|---|----------|------|-----------|---------------|
| 1 | Estados del expediente | ENT_OPS_STATE_MACHINE | Archivo completo (FROZEN) | Todos los LOTEs, handlers, frontend |
| 2 | Tallas / SKUs / GTINs | rw_sticker_v7_5.html | Artefacto HTML externo | ENT_OPS_TALLAS (ref), ENT_MERCADO_TALLAS |
| 3 | Routing consultas B2B | ENT_PLAT_KNOWLEDGE.E3 | Sección E3 | PLB_INTERACCION_CLIENTE.E, ENT_PLAT_CANALES_CLIENTE.B |
| 4 | Entidades legales | ENT_PLAT_LEGAL_ENTITY.C | Sección C (tabla) | ENT_OPS_EXPEDIENTE, ENT_PLAT_MODULOS, ENT_COMERCIAL_MODELOS |
| 5 | Pricing | ENT_COMERCIAL_PRICING | Archivo completo | PLB_REGISTRO_PROFORMA, SCH_PROFORMA_MWT, simuladores |
| 6 | Costos | ENT_COMERCIAL_COSTOS | Archivo completo | ENT_COMERCIAL_PRICING, financial summary |
| 7 | Model registry LLM | ENT_PLAT_LLM_ROUTING | Archivo completo | PLB_PROMPTING (solo referencia, no duplica) |
| 8 | Artefactos del sistema | ARTIFACT_REGISTRY | Archivo completo | ENT_PLAT_ARTEFACTOS, LOTEs, ArtifactPolicy engine |
| 9 | Schemas | SCHEMA_REGISTRY | Archivo completo | Todos los SCH_ |
| 10 | Design tokens | ENT_PLAT_DESIGN_TOKENS | Archivo completo | Frontend globals.css, LOTEs frontend |
| 11 | Modelos de operación | ENT_COMERCIAL_MODELOS | Archivo completo (v2.0) | SCH_PROFORMA_MWT, DEC_MODE_RENAME, BrandWorkflowPolicy |

---

## C. Reglas

1. **Dato Único**: Si un concepto tiene SSOT declarado, otros archivos solo referencian — nunca duplican datos.
2. **Contradicción**: SSOT gana siempre. El documento que contradice se corrige.
3. **FROZEN**: Un SSOT con status FROZEN no se modifica bajo ninguna circunstancia (R2).
4. **Nuevo SSOT**: Se declara aquí al crearlo. Sin registro aquí, no es SSOT oficial.
5. **Freeze en LOTEs**: Agente trabaja contra versión SSOT vigente al lanzar LOTE. Si SSOT cambia durante ejecución, items que lo consumen → STALE (ref → PLB_ORCHESTRATOR).

---

Changelog:
- v0.1 (2026-03-14): STUB creado.
- v1.0 (2026-04-01): Poblado con 11 SSOTs. Promovido a VIGENTE.
