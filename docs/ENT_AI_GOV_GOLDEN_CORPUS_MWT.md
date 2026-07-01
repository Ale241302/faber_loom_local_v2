# ENT_AI_GOV_GOLDEN_CORPUS_MWT — Corpus Golden de Outputs A+ para Evaluacion
id: ENT_AI_GOV_GOLDEN_CORPUS_MWT
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: ENT
subfamilia: AI_GOV
stamp: DRAFT — 2026-05-01
aprobador: CEO
aplica_a: [MWT, FaberLoom]
refs: SPEC_AI_GOV_GOVERNANCE_AND_ROUTING (consumidor primario) · POL_AI_GOV_FINAL_OUTPUT_QUALITY (gold_match_score >=0.90 trigger short-circuit) · ENT_AI_GOV_OUTPUT_PINS (relacion: pin canonico es subset del corpus) · SPEC_LLM_ROUTING_ARCHITECTURE v1.3 (gold samples alimentan L3 Compiler few-shot)

---

## Declaracion

Corpus de **outputs A+ canonicos** que sirve de:
1. **Baseline para evaluacion de modelos** (mensual y on-trigger).
2. **Trigger de short-circuit** del final pass (gold_match_score >=0.90).
3. **Few-shot pool** para el L3 Prompt Compiler (con etiqueta `model_affinity`).
4. **Anclaje anti-drift** para detectar cuando un modelo pineado degrada.

Sin corpus, los benchmarks son teatro: comparas modelos contra ningun estandar. Con corpus, decis "Kimi gano planning, Qwen gano extraccion, Opus sigue mejor en final pass ejecutivo" con datos.

**Estado actual: DRAFT esqueleto.** El poblamiento del corpus (50-100 cases curados por CEO) es trabajo dedicado de sprint pendiente. Este archivo define la **estructura** del corpus y la metodologia de curacion.

---

## Categorias y distribucion objetivo

| Categoria | Cases objetivo | task_type ejemplo | Brand |
|-----------|---------------|-------------------|-------|
| RFQ B2B safety footwear | 20 | rfq_marluvas_industrial · rfq_tecmater_construccion | MWT |
| Ficha tecnica PDF parsing | 10 | parse_marluvas_catalog · parse_tecmater_norma_ca | MWT |
| Cotizacion B2B drafting | 10 | quote_b2b_safety_mexico · quote_b2b_colombia | MWT |
| Traduccion ES <-> PT-BR tecnico | 10 | translate_safety_specs · translate_norma_brasil | MWT |
| Amazon listing optimization | 10 | listing_rana_walk_us · aplus_content_rana_walk | MWT |
| Planning / subagent decomposition | 10 | orchestrate_research · plan_data_pipeline | SHARED |
| Edge / compliance | 10 | cfdi_validation · nfe_parsing · lgpd_redaction | MWT |
| FaberLoom agent outputs | 10 | agent_response_pyme_b2b · skill_compose_response | FaberLoom |
| Custom edge cases | 10 | (bordes detectados en operacion real) | varies |

**Total objetivo: 100 cases.** Minimo viable para arrancar Eval Lab: 50 cases distribuidos proporcionalmente.

**Distribucion por dificultad por categoria (regla):** 30% easy · 50% medium · 20% hard. Easy verifica baseline; medium es donde compiten modelos; hard separa modelos premium de carpinteros.

---

## Schema de un golden_case

```yaml
golden_case:
  case_id:                      uuid
  category:                     string             # ver tabla §Categorias
  task_type:                    string             # alineado con SPEC_LLM_ROUTING task_type
  skill_id:                     string             # skill que lo ejecuta
  brand:                        "MWT" | "FaberLoom" | "SHARED"
  difficulty:                   "easy" | "medium" | "hard"
  data_classification:          "N0" | "N1" | "N2"  # corpus no contiene N3/N4 raw — usar sintetico equivalente
  is_synthetic:                 bool               # true si datos N3/N4 reemplazados por equivalente sintetico

  # === Input fijo (no se modifica, anchor del case) ===
  input:
    raw:                        string | object    # input exacto que recibe el sistema
    context:                    object             # contexto inyectado (KB refs, parametros, idioma)
    canonical_input_hash:       string             # SHA-256 del input para verificar inmutabilidad

  # === Output A+ ===
  expected_output:
    content:                    string
    format:                     "markdown" | "json" | "html" | "plain" | "yaml"
    language:                   string             # ej. "es-CR", "pt-BR", "en-US"
    canonical_output_hash:      string

  # === Criterios de aceptacion (validables) ===
  acceptance_criteria:
    must_contain:               [string]           # frases o claims que el output DEBE contener
    must_not_contain:           [string]           # frases prohibidas (PII, claims falsos, alucinaciones tipicas)
    structural_requirements:    [string]           # ej. "tabla con columnas X,Y,Z" o "JSON con campos a,b,c"
    factual_anchors:                              # claims verificables que deben preservarse
      - claim:                  string
        source:                 string             # KB ref, URL, doc

  # === Restricciones del caso ===
  must_pass:                    [string]           # pruebas duras (ej. "valida XSD CFDI 4.0", "preserva tallas exactas")
  must_not_do:                  [string]           # acciones prohibidas (ej. "no inventar precios", "no traducir codigos producto")

  # === Notas humanas ===
  human_gold_notes:             string             # 2-5 lineas explicando por que este es A+
  edge_cases_covered:           [string]           # bordes que el caso prueba
  curated_by:                   string             # CEO o curador
  curated_at:                   datetime
  approved_by_ceo:              bool

  # === Procedencia (importante: no inventar) ===
  origin:                       "production_real" | "production_synthesized" | "constructed_for_eval"
  origin_run_id:                uuid               # si origin=production*, ref al run real
  original_best_model:          string             # modelo que produjo el output A+ original
  original_prompt_hash:         string             # prompt usado en el run original
  original_run_cost_usd:        float

  # === Estado de uso en Eval Lab ===
  eval_history:
    - eval_run_id:              uuid
      eval_date:                date
      models_tested:            [string]
      scores:                   {model: float}     # score 0..1 por modelo
      winner:                   string
      judge_model:              string

  # === Few-shot pool ===
  used_as_few_shot:             bool               # si se usa en L3 Compiler
  model_affinity:                                  # approval_rate por modelo cuando se usa como few-shot
    claude-sonnet-4-6:          float
    claude-opus-4-7:            float
    gpt-5-5:                    float
    kimi-k2-6:                  float
    # etc

  # === Versionado ===
  version:                      int                # incrementa si CEO revisa y refina
  refresh_trigger:              "calendar_quarterly" | "model_drift_detected" | "ceo_review"
  last_refreshed:               date
```

---

## Reglas de curacion

1. **No sintetizar A+.** Un golden_case sale de produccion real (origin: production_real) o se construye explicitamente con CEO en review (constructed_for_eval). No se infieren A+ retrospectivamente.

2. **CEO aprueba cada case.** `approved_by_ceo: true` es prerequisito. Cases sin aprobacion estan en draft hasta review.

3. **Sin PII real.** Cases con N3/N4 usan equivalentes sinteticos preservando estructura. `is_synthetic: true` queda registrado.

4. **Refresh trigger documentado.** Cases pueden expirar:
   - `calendar_quarterly`: revision trimestral obligatoria.
   - `model_drift_detected`: si los mejores modelos del momento bajan score sobre el case sin razon clara, el case puede estar desactualizado.
   - `ceo_review`: CEO marca para refresh.

5. **No tocar canonical_input_hash y canonical_output_hash sin bumping version.** Si el case cambia, version++. Versiones anteriores se preservan en archivo para auditoria retrospectiva de evals.

6. **Distribucion equilibrada por dificultad.** Si una categoria tiene 80% easy, los benchmarks son inutiles — todos los modelos pasan. CEO valida distribucion al curar.

7. **Bordes deliberados.** Edge cases reales (CFDI con campo opcional, ficha con tabla sin bordes, traduccion con falso amigo) son cases mas valiosos que outputs estandar. Reservar al menos 20% del corpus a bordes.

---

## Procedimiento de eval mensual (referencia, detalle en SPEC_AI_GOV §F)

```
1. Seleccionar subset del corpus (estratificado por categoria + dificultad).
   Tamano: 30-50 cases por run para mantener costo manejable.

2. Para cada case:
   - Correr modelos pineados (defenders) — sus pin actual gana o pierde corona.
   - Correr modelos retadores (challengers) — modelos nuevos, mas baratos, etc.
   - Judge model evalua output vs expected_output con criterios objetivos.
   - Score 0..1 por modelo por case.

3. Aggregar resultados:
   - Score promedio por modelo por categoria.
   - Costo total por modelo.
   - Efficiency = score / cost.

4. Generar propuestas de re-pin:
   - Si retador alcanza score equivalente (>=0.95 del defender) con costo >=40% menor → propuesta a CEO.
   - Si defender mantiene ventaja >=10% en score O costo equivalente → pin se mantiene.

5. CEO revisa propuestas, aprueba o rechaza re-pins.

6. Eval run queda registrado en eval_history de cada case.
```

---

## Anti-patrones

1. **Curar el corpus mirando que modelo gana hoy.** Sesgo confirmatorio. CEO cura outputs A+ por calidad intrinseca, no por modelo que lo produjo.
2. **Reusar prompts del corpus en produccion.** El corpus es eval, no template. Prompts de produccion viven en skills.
3. **Inflar el corpus con outputs aceptables-pero-no-A+.** Mejor 50 cases A+ que 200 cases medianos. Calidad > cantidad.
4. **Saltar cases por costo de eval.** Si el corpus es caro de evaluar mensual, reducir N cases — no saltar el ciclo.

---

## Origen y poblamiento

Estado actual: **esqueleto definido, corpus vacio.**

Triggers de poblamiento:
1. Sprint dedicado de curacion (CEO + curador) post-canonizacion AI_GOV.
2. Captura semi-automatica desde Token Ledger: outputs con `outcome: approved` y `edit_distance: 0` son candidatos. Auto-promocion no, propuesta a CEO si.
3. Edge cases capturados en operacion (ej. RFQ Marluvas con norma especifica, listing rechazado por Amazon que se corrigio).

Meta operativa: 50 cases poblados antes del primer ciclo de Eval Lab.

---

## Lo que esto NO es

- No es un dataset de fine-tuning (corpus pequeno y curado a mano).
- No es benchmark estandar de la industria (LMSys, MMLU). Es benchmark **propio** sobre tareas reales MWT/FB.
- No es libreria de templates (los templates viven en skills).
- No es archivo historico (cases viejos se archivan o refrescan, no acumulan).

---

Changelog:
- v1.0 (2026-05-01): Creacion. Esqueleto definido. Schema golden_case completo. 9 categorias x distribucion objetivo. Reglas de curacion. Procedimiento de eval mensual. Anti-patrones. Estado: DRAFT — corpus vacio pendiente sprint dedicado de curacion CEO. Origen: sesion AI_GOV 2026-05-01.
