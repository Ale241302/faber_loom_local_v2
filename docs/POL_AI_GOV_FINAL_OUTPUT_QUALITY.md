# POL_AI_GOV_FINAL_OUTPUT_QUALITY — Final Pass Premium Obligatorio
id: POL_AI_GOV_FINAL_OUTPUT_QUALITY
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: POL
subfamilia: AI_GOV
stamp: VIGENTE — 2026-05-01
aprobador: CEO
aplica_a: [MWT, FaberLoom]
refs: SPEC_LLM_ROUTING_ARCHITECTURE v1.3 (Token Ledger campos final_pass_required/executed/shortcut_reason) · SCH_AI_GOV_HANDOFF_DRAFT · ENT_AI_GOV_OUTPUT_PINS · ENT_AI_GOV_GOLDEN_CORPUS_MWT · POL_AI_GOV_DATA_CLASS_PROVIDER · ARCH_AGENT_PRINCIPLES (P3 draft-first, P9 gobernanza embebida)

---

## A. Proposito

Garantiza que todo output **cliente-visible** sea procesado en su pasada final por el modelo mas capaz autorizado para esa skill, independientemente de cuantos modelos baratos lo hayan preparado antes.

**Principio inquebrantable:** la carpinteria la hacen modelos baratos; la entrega visible la pule el mas capaz autorizado. El usuario siempre percibe la mejor calidad disponible. El sistema ahorra atras, no adelante.

---

## B. Scope: que es output cliente-visible

Aplica obligatoriamente a:

| Tipo de output | Razon |
|----------------|-------|
| **client_visible_output** | Todo lo que sale a un usuario externo (cliente B2B, comprador Amazon, PYME FaberLoom) |
| **executive_summary** | Resumenes ejecutivos para CEO o stakeholders externos |
| **quote_cover_email** | Email de cobertura de cotizacion B2B |
| **legal_or_compliance_output** | Reviews legales, CFDI, NF-e, contratos, redlines |
| **high_value_commercial_output** | Propuestas comerciales >USD 5K, listings Amazon nuevos, A+ Content |
| **public_marketing** | Copy publicado: landing, social, listing, blog post |

NO aplica a:
- Outputs internos de carpinteria (drafts intermedios, parsing, OCR cleanup, dedup, traduccion interna).
- Outputs de orquestacion o planning entre subagentes.
- Outputs de evaluacion (judge prompts, eval scoring).
- Outputs de telemetria o reportes internos solo CEO.

---

## C. Estructura del flujo

```
[Input usuario o trigger]
        |
        v
[Carpinteria — modelos baratos: Kimi K2 / Haiku 4.5 / Gemini Flash]
   - Parsing, OCR cleanup, dedup, traduccion interna
   - Borrador inicial, recopilacion de fuentes
        |
        v
[Draft handoff — schema SCH_AI_GOV_HANDOFF_DRAFT]
   - input_classification, gold_match_score, cost_so_far,
     models_used_chain, low_confidence_spans
        |
        v
[Final Pass — modelo strongest_allowed_for_skill]
   - Por defecto: Sonnet 4.6
   - Critico: Opus 4.7
   - Self-host autorizado para N3/N4 si DPA-FULL no disponible
        |
        v
[Output entregado al cliente]
```

---

## D. Modelos por categoria (referencia operativa)

| Categoria | Modelos autorizados | Uso |
|-----------|---------------------|-----|
| **carpinteria_volumen** | Kimi K2 (managed) · Kimi K2 self-host · Qwen3 · DeepSeek v4 Flash | Volumen alto, latencia tolerante 3-8s |
| **carpinteria_latencia** | Haiku 4.5 · Gemini Flash 2.5 | Latencia <1s critica |
| **finalizador_default** | Sonnet 4.6 · GPT-5.5 | 80% de outputs cliente-visibles |
| **finalizador_critico** | Opus 4.7 · GPT-5.5 Pro | Cliente-visible >USD 5K, legal, executive |
| **judge_evaluator** | Sonnet 4.6 (cross-check muestral con Opus 4.7) | Eval mensual + 5-10% sampling |

La lista vigente vive en ENT_PLAT_ACTION_REGISTRY. Esta tabla es referencia operativa con criterio de uso, no el catalogo.

---

## E. Regla de short-circuit por gold sample (palanca de ahorro)

El final pass se puede saltar si y solo si se cumplen TODAS las condiciones:

```yaml
final_pass_shortcut_allowed_if:
  - gold_similarity:        ">=0.90"           # vs ENT_AI_GOV_GOLDEN_CORPUS_MWT
  - no_critical_exception:  true               # sin flags de POL_DETERMINISMO o compliance
  - previous_output_clean:  true               # output similar previo aprobado sin edits
  - same_client_context:    true               # mismo cliente o contexto equivalente
  - data_class:             "<=N1"             # nunca shortcut sobre N2+
```

Si las 5 condiciones se cumplen, el output del carpintero se entrega sin pasar por finalizador. El ledger registra:

```
final_pass_required:        true
final_pass_executed:        false
final_pass_shortcut_reason: "gold_similarity=0.94 + previous_clean + same_client"
```

Si una sola condicion falla → final pass obligatorio.

---

## F. Outcomes del final pass

El final pass produce uno de tres outcomes (registrados en SCH_AI_GOV_HANDOFF_DRAFT):

| Outcome | Definicion | Costo |
|---------|-----------|-------|
| **accept** | Draft del carpintero correcto, finalizador pule estilo/tono. Edit distance <0.2. | tokens del finalizador ~10-20% del total |
| **refine** | Draft aceptable, finalizador reescribe 30-70%. Edit distance 0.2-0.7. | tokens del finalizador ~50% del total |
| **abort_to_human** | Draft inutilizable. Finalizador detecta error factual, alucinacion, o incoherencia que reescribir requiere re-procesar input desde cero. | escalado a CEO con audit |

**Cap de tokens por outcome:**
- `accept`: cap 1.5x tokens estimados.
- `refine`: cap 2.5x tokens estimados.
- `abort_to_human`: cap 1x; el finalizador NO debe gastar tokens reescribiendo si decide abortar. Salida: razon documentada + escalacion.

---

## G. Anti-loop

Si el finalizador hace `abort_to_human` mas de **2 veces** sobre el mismo `parent_request_id` (carpintero retry rule), el sistema escala a humano sin reintentar. Loops infinitos vacian budget mensual; este es el guardrail.

---

## H. Re-pinning post final pass

Si el output del finalizador queda aprobado por CEO (`outcome: approved` en RequestOutcomeEntry, `edit_distance == 0`), el sistema propone agregarlo a ENT_AI_GOV_OUTPUT_PINS. CEO confirma o rechaza. Pin aprobado vincula:
- `task_type` + `skill_id` + `client_context_hash`
- `model_used` (modelo finalizador que produjo)
- `prompt_hash` + `context_hash`

A partir de ese pin, futuras invocaciones con misma firma activan §E (shortcut) si las 5 condiciones se cumplen.

---

## I. Re-evaluacion mensual del pin (torneo)

Pinned outputs se re-evaluan mensualmente:

> "El rey conserva la corona, pero todos los meses hay torneo."

Procedimiento (detallado en ENT_AI_GOV_OUTPUT_PINS):
1. Sandbox corre el modelo pineado vs retadores (modelos nuevos, mas baratos, etc).
2. Judge model + golden_corpus evaluan calidad relativa.
3. Si retador alcanza calidad equivalente con costo ≥40% menor → propuesta de re-pin a CEO.
4. CEO aprueba o rechaza. Pin permanece o se actualiza con cita del torneo.

---

## J. Excepciones documentadas

Casos donde NO se aplica final pass aunque sea cliente-visible:

1. **Output puramente determinístico** (Tier 0, regex/templates, parser estructurado): no requiere LLM final pass.
2. **Output bloqueado por POL_DATA_CLASSIFICATION** que ningun modelo autorizado puede procesar: escala a humano sin generar output IA.
3. **Cliente solicita explicitamente speed > quality** y firma waiver: registrado en audit_event, expira por sesion.

---

## K. Telemetria obligatoria

Todo entry del Token Ledger asociado a output cliente-visible debe llenar (v1.3):
- `final_pass_required: true`
- `final_pass_executed: bool`
- `final_pass_shortcut_reason: string` (si executed=false)

Auditoria mensual sample: 50 outputs cliente-visibles random. Si alguno tiene `final_pass_required: false` y deberia haber sido `true` → bug del clasificador upstream → fix prioridad alta.

---

Changelog:
- v1.0 (2026-05-01): Creacion. Final pass premium obligatorio sobre 6 categorias de output cliente-visible. Short-circuit por gold sample con 5 condiciones AND. Outcomes accept/refine/abort_to_human con caps de tokens. Anti-loop en 2 abort_to_human. Re-pinning post aprobacion. Torneo mensual de pins. Origen: sesion AI_GOV 2026-05-01.
