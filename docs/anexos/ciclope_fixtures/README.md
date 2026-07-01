# Anexos · Ciclope Fixtures · suite regresion FaberLoom

Test fixtures YAML generados por **Ciclope (OpenClaw AM MWT)** para validar el sistema FaberLoom contra casos funcionales reales. Estos fixtures son **suite regresion separada** del replay set MVP (definido en `ENT_FB_RFQ_REPLAY_SET_v1`).

> **Regla critica (R4):** estos fixtures NO se usan para entrenar memory packs. Solo validan no-regresion del comportamiento canonico antes de cada deploy.

## Estructura

```
docs/anexos/ciclope_fixtures/
├── r3_cross_industry/
│   ├── case_01.yaml ... case_20.yaml          (20 fixtures multi-industria)
│   ├── SUMMARY.yaml                           (resumen + gaps + cobertura)
│   ├── FaberLoom_Test_Suite_Document.md       (documentacion narrativa)
│   └── README.md (este pendiente)
└── safety_footwear/
    ├── case_sf_01.yaml ... case_sf_10.yaml    (10 fixtures MWT-safety_footwear)
    ├── SUMMARY_safety_footwear.yaml           (resumen + cobertura profile)
    ├── FaberLoom_Safety_Footwear_Suite.md     (doc narrativa)
    └── Safety_Footwear_Fixtures_Document.md   (doc detallada)
```

## r3_cross_industry · 20 fixtures

Generados post-auditoria R3 ChatGPT. Validan **transferibilidad cross-industria** del modelo FaberLoom sin overfit MWT.

| Metrica | Valor |
|---|---|
| Total fixtures | 20 |
| Critical+High | 9 (45%) · cumple ≥30% |
| Industrias cubiertas | 11 (EPP quimico · MRO · ferreteria · medico · electrico · etc) |
| Exception codes usados | 11/15 (73% taxonomia) |
| Compliance profiles invocados | 5/6 (falta safety_footwear · cubierto por suite separada) |
| Privacy tiers | 16 TENANT_DERIVED + 4 RESTRICTED |
| Total assertions | 287 must_pass + 120 must_not_do + 60 edge cases |
| Gaps detectados | 1 (GAP-001 freight_international · low priority) |

## safety_footwear · 10 fixtures MWT

Generados post-indexa-d para validar el profile compliance_checker:safety_footwear (el MAS USADO en produccion real con tenant beta MWT).

| Metrica | Valor |
|---|---|
| Total fixtures | 10 |
| Critical+High | 5 (50%) · cumple ≥30% |
| Sub-verticales cubiertos | 7 (petrolero · construccion · automotriz · manufactura · agro · logistica · ferreteria distribucion) |
| Exception codes usados | 8/15 (53% · vertical-specific) |
| Vocabulario regional MX | 5 terminos · 100% accuracy ("punto" · "bota dielectrica" · "calzado agro" · etc) |
| Compliance rules ejercitadas | 12 (ASTM F2413-18 · NOM-113-STPS-2009 MX · puntera · plantilla · talla MX · ancho · lab · MOQ · margen · cross-brand · multi-SKU · glossary) |
| Privacy tiers | 9 TENANT_DERIVED + 1 GLOBAL_PROMOTABLE (happy path) |
| Total assertions | 145 must_pass + 60 must_not_do + 30 edge cases |
| Gaps detectados | 2 (GAP-SF-001 freight_MX_routes · GAP-SF-002 glossary_punto_CR · ambos low) |

## Total combinado

- **30 fixtures totales** (20 + 10)
- **432 must_pass + 180 must_not_do + 90 edge cases** = **702 assertions verificables programaticamente**
- **3 gaps arquitectonicos detectados** · todos low/medium priority · acotados con workarounds documentados

## Como se usan

```
1. Pre-commit hook: ejecutar suite contra cualquier cambio del sistema
2. Pre-deploy gate: bloquear deploy si cualquier assertion falla
3. Post-deploy validation: ejecutar suite contra entorno production-like
4. Curador review: si fixture nuevo aparece en uso real · curador valida si entra a suite
```

## Lo que NO hacen

- NO entrenar memory packs · NO promover gold samples · NO contaminar pool MVP
- NO reemplazar replay set canonico (60 RFQs reales que CEO extrae Sem 0)
- NO se ejecutan en runtime productivo · solo en CI/CD y staging

## Stamp
VIGENTE 2026-05-02 — 30 fixtures Ciclope canonizados como suite regresion · referenciados desde `ENT_FB_RFQ_REPLAY_SET_v1` §9.
