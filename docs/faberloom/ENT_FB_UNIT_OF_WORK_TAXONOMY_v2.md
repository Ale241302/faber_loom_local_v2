---
id: ENT_FB_UNIT_OF_WORK_TAXONOMY_v2
version: 2.0
status: VIGENTE
visibility: [INTERNAL]
domain: Plataforma
type: entity
stamp: VIGENTE 2026-07-07 — Foundation Beta E3-4 Wave 0
fecha: 2026-07-07
agente: Kimi Code CLI (implementación E3-4)
aplica_a: [FaberLoom]
status_motivo: |
  Wave 0 requiere una taxonomía canonica mínima para primitivos cross-vertical
  y dimensiones de scope que soporten evidence bundle, autonomía por track record
  y HITL sin inventar nombres por vertical.
relacionado_con:
  - SCH_FB_SKILL_MANIFEST_v2
  - ENT_FB_SKILL_CATALOG_v1
  - POL_FB_OUTCOME_ACCOUNTABILITY.md
  - ARCH_AGENT_PRINCIPLES.md
---

# ENT_FB_UNIT_OF_WORK_TAXONOMY_v2
## Taxonomía canonica de unidades de trabajo y primitivos cross-vertical

## 1. Propósito

Establece el vocabulario mínimo que todo SKILL en FaberLoom debe usar para:
- Declarar su unidad de trabajo y dimensiones de scope.
- Referirse a primitivos cross-vertical sin inventar sinónimos.
- Enrutar evidence bundles y knowledge candidates al scope correcto.
- Graduar autonomía por track record sin violar HITL.

## 2. Primitivos cross-vertical (P01-P18)

Los primitivos existentes P01-P14 se mantienen. Wave 0 añade P15-P18:

| ID | Nombre | Definición |
|---|---|---|
| P15 | `verificar_vigencia_normativa` | Confirmar que norma/arancel/requisito citado sigue vigente; detectar modificaciones. |
| P16 | `rastrear_externo` | Consulta en tiempo real a sistema de tercero no controlado con captura de evidencia (URL + fecha + hash). |
| P17 | `corregir_en_cascada_temporal` | Recálculo retroactivo con dependencias encadenadas (planilla rectificada, notas de crédito, intereses). |
| P18 | `capturar_interaccion_informal` | WhatsApp/verbal/no estructurado → compromiso trazable y citable en KB. |

## 3. Unidad de trabajo canonica

Para Foundation Beta la unidad de trabajo por defecto es `quote`/`proforma` (MWT safety footwear). Los verticales futuros extenderán la taxonomía siguiendo las reglas de v1.

## 4. Dimensiones de scope obligatorias

Toda query que produzca o consuma knowledge candidate debe incluir al menos:

```yaml
access_scope_dimensions_canonicas:
  - tenant_id
  - workspace_id
  - unit_of_work_id       # quote_id / matter_id / project_id / encounter_id
  - client_id             # si el vertical tiene multi-cliente
  - sub_unit_id           # si el vertical tiene sub-unidades
  - data_class            # PRIVATE_RAW | TENANT_DERIVED | GLOBAL_PROMOTABLE | TIER_4
  - action                # read | write | promote | approve
```

## 5. Reglas inquebrantables

1. Todo SKILL declara `unit_of_work` y `scope_dimensions` en su manifest v2.
2. Todo evidence bundle lleva `unit_of_work_id` y `tenant_id`.
3. Knowledge procesal-cliente no sale del `client_id` scope.
4. Knowledge contextual-unit_of_work no sale del `unit_of_work_id` scope.
5. Autonomía por track record nunca desactiva HITL para acciones con efecto externo.
6. `unit_of_work_id` no puede ser `null` en operaciones que producen knowledge candidate.

## 6. Implicaciones para evidence bundle

El evidence bundle generalizado (C0-7) usa `external_evidence.source_locator` para ligar cada fuente a una `unit_of_work_id`. Sin `unit_of_work_id` explícita, el bundle queda en estado `pending_scope` y no es promocionable a KB.

## Changelog
- 2026-07-07 v2.0 VIGENTE: Wave 0 E3-4. Añade P15-P18, scope dimensions obligatorias, reglas de evidence bundle y autonomía.
