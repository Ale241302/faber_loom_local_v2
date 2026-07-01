# SCH_AI_GOV_HANDOFF_DRAFT — Schema del Handoff Carpintero -> Final Pass
id: SCH_AI_GOV_HANDOFF_DRAFT
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SCH
subfamilia: AI_GOV
stamp: VIGENTE — 2026-05-01
aprobador: CEO
aplica_a: [MWT, FaberLoom]
requires: SPEC_LLM_ROUTING_ARCHITECTURE v1.3 (Token Ledger), POL_AI_GOV_FINAL_OUTPUT_QUALITY, POL_DATA_CLASSIFICATION, ENT_PLAT_ACTION_REGISTRY
policies: [POL_AI_GOV_DATA_CLASS_PROVIDER, POL_AI_GOV_FINAL_OUTPUT_QUALITY, POL_DETERMINISMO]
inherits: ninguno

---

## Proposito

Define la estructura del paquete de informacion que el carpintero (modelo barato) entrega al final pass (modelo caro). Sin este schema, el finalizador pule a ciegas y desperdicia tokens "mejorando" lo que estaba bien o "corrigiendo" hechos correctos.

Este schema cierra el hueco identificado en sesion arquitectonica AI_GOV 2026-05-01 (hueco #4): handoff vacio entre capas.

---

## Slots obligatorios

```yaml
handoff_draft:
  # === Identidad ===
  draft_id:                 uuid
  parent_request_id:        uuid                # raiz de la cadena
  task_type:                string              # ej. "rfq_b2b_safety_footwear", "amazon_listing"
  skill_id:                 string              # skill que orquesto la cadena
  brand_scope:              "MWT" | "FaberLoom"
  org_id:                   string

  # === Carpinteria realizada ===
  carpinteria_chain:
    - role:                 "ocr_cleanup" | "parsing" | "dedup" | "translation_internal" | "draft_initial" | "research_compile"
      model:                string              # ej. "kimi-k2-managed", "haiku-4.5"
      provider_action_id:   string              # ref ENT_PLAT_ACTION_REGISTRY
      tokens_in:            int
      tokens_out:           int
      cost_usd:             float
      latency_ms:           int
      output_summary:       string              # 1-2 lineas de que hizo este step

  # === Estado del draft entregado al finalizador ===
  draft_content:            string              # el draft propiamente dicho
  draft_format:             "markdown" | "json" | "html" | "plain" | "yaml" | "xml"
  draft_language:           "es" | "pt-BR" | "en" | "es-MX" | "es-CO" | "es-CR" | etc
  draft_token_count:        int

  # === Clasificacion de data ===
  input_classification:     "N0" | "N1" | "N2" | "N3" | "N4"   # tier max del input original
  draft_classification:     "N0" | "N1" | "N2" | "N3" | "N4"   # tier del draft (debe ser >= input)
  pii_detected:             bool                # PII en el draft (si true, requiere redaccion antes de output cliente)

  # === Senales de calidad para el finalizador ===
  gold_match_score:         float               # 0..1, similarity vs golden corpus relevante (null si no aplica)
  gold_reference_id:        uuid                # ref ENT_AI_GOV_GOLDEN_CORPUS_MWT (null si no match)
  pinned_output_candidate:  uuid                # ref ENT_AI_GOV_OUTPUT_PINS si hay match (null si no)

  low_confidence_spans:                          # spans del draft con baja confianza, prioridad de review
    - span_start:           int                 # offset en draft_content
      span_end:              int
      reason:                "factual_uncertainty" | "translation_uncertainty" | "ambiguous_input" | "missing_data" | "spec_mismatch"
      confidence:            float              # 0..1
      carpintero_note:       string             # 1 linea de explicacion

  factual_claims:                                # claims verificables que el finalizador NO debe alterar sin razon
    - claim:                 string
      source_ref:            string             # KB ref, URL, o doc adjunto
      verified:              bool

  no_touch_zones:                                # spans que el finalizador NO debe reescribir (datos exactos, codigos, IDs)
    - span_start:           int
      span_end:              int
      reason:                string

  # === Costos acumulados ===
  cost_so_far_usd:          float               # suma de carpinteria_chain
  budget_remaining_usd:     float               # cap restante para el finalizador
  budget_caps_active:       [string]            # ["per_run", "per_skill", "per_org"]

  # === Instrucciones para el finalizador ===
  expected_outcome:         "accept" | "refine_likely" | "uncertain"   # senal del carpintero al finalizador
  finalizer_focus:          [string]            # ["tone", "factual_check", "format", "translation_polish", "compliance_check"]
  forbidden_actions:        [string]            # ["alter_facts", "add_claims", "change_pricing", "translate_no_touch_zones"]

  # === Metadata de auditoria ===
  parent_audit_id:          uuid                # ref SPEC_AUDIT_MODULE
  created_at:               datetime
  carpintero_chain_root_model: string           # primer modelo de la cadena
```

---

## Estructura de la respuesta del finalizador

El final pass devuelve un `handoff_response` que el Engine consume:

```yaml
handoff_response:
  draft_id:                 uuid                # ref draft entrante
  outcome:                  "accept" | "refine" | "abort_to_human"
  final_output:             string              # null si outcome=abort_to_human
  edit_distance:            float               # 0..1 vs draft_content
  changes_summary:          string              # que cambio el finalizador (1-3 lineas)
  no_touch_zones_respected: bool                # debe ser true; si false = bug critico
  facts_altered:            [string]            # lista de claims modificados (debe ser [] si finalizer respeto §F de POL_AI_GOV_FINAL_OUTPUT_QUALITY)
  abort_reason:             string              # solo si outcome=abort_to_human
  finalizer_model:          string
  finalizer_tokens_in:      int
  finalizer_tokens_out:     int
  finalizer_cost_usd:       float
```

---

## Reglas de validacion

1. **`draft_classification` >= `input_classification`**: el carpintero no puede "bajar de tier" un input. N3 input -> draft sigue siendo N3 minimo.

2. **`carpinteria_chain` no puede estar vacia** salvo Tier 0 deterministic (sin LLM). Si lo esta y no hay flag Tier 0, el handoff es bug.

3. **`cost_so_far_usd` debe coincidir** con suma de `cost_usd` de cada step del chain. Drift = bug del Action Engine.

4. **`expected_outcome: "accept"` con `low_confidence_spans` no vacio = inconsistencia.** El carpintero no puede declarar "all good" mientras marca spans inciertos.

5. **`no_touch_zones` deben preservarse byte-perfect.** El finalizador que altera bytes en una no_touch_zone produce `no_touch_zones_respected: false` y el output se rechaza automaticamente; se reintenta una vez.

6. **`facts_altered` no vacio sin razon documentada en `changes_summary` = rechazo automatico.** El finalizador puede cambiar tono, no hechos.

7. **`outcome: "abort_to_human"` requiere `abort_reason` no vacio.** Abort sin razon = bug.

---

## Por que este schema y no algo mas simple

Sin `low_confidence_spans` y `no_touch_zones`, el finalizador tiene dos modos de falla: o reescribe en exceso (gasta tokens "mejorando" lo correcto, alucina cambios sobre datos exactos) o no toca nada (no agrega valor). Estos campos guian al finalizador a focalizar trabajo donde aporta calidad y respetar lo que el carpintero ya verifico.

Sin `factual_claims` con `source_ref`, el finalizador puede "corregir" un claim correcto basado en su training data y romper veracidad. Estos campos son anti-alucinacion del finalizador.

Sin `cost_so_far_usd` y `budget_remaining_usd`, el finalizador no puede decidir cuanto gastar. Outputs criticos requieren mas tokens; outputs de bajo costo deben respetar el cap restante.

---

## Cuando NO usar este schema

- Outputs internos (no cliente-visible) que no pasan por final pass.
- Outputs Tier 0 deterministicos.
- Outputs de un solo modelo (single-shot sin carpinteria previa).

En esos casos el ledger entry queda con `final_pass_required: false` y este schema no aplica.

---

Changelog:
- v1.0 (2026-05-01): Creacion. Schema completo del handoff carpintero -> final pass. 7 reglas de validacion. Anti-alucinacion del finalizador via factual_claims + no_touch_zones. Origen: sesion AI_GOV 2026-05-01 (hueco #4 cierre).
