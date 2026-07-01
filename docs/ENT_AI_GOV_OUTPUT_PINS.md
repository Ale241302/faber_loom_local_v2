# ENT_AI_GOV_OUTPUT_PINS — Registro de Outputs Pineados (Recetas Canonicas)
id: ENT_AI_GOV_OUTPUT_PINS
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
type: ENT
subfamilia: AI_GOV
stamp: DRAFT — 2026-05-01
aprobador: CEO
aplica_a: [MWT, FaberLoom]
refs: SPEC_AI_GOV_GOVERNANCE_AND_ROUTING (consumidor) · POL_AI_GOV_FINAL_OUTPUT_QUALITY (re-pinning post approved clean) · SPEC_LLM_ROUTING_ARCHITECTURE v1.3 (Token Ledger campo pinned_output_id, pin_status) · ENT_AI_GOV_GOLDEN_CORPUS_MWT (relacion: pin canonico es subset operativo del corpus)

---

## Declaracion

Registro de **recetas pineadas**: outputs que en su momento salieron A+ y cuya combinacion exacta de modelo + prompt + temperatura + contexto queda canonizada como respuesta default para tareas de la misma firma. El pinning es la palanca de ahorro mas potente del subsistema AI_GOV.

> **Regla operativa inquebrantable:** un pin se respeta en produccion, pero se reta en sandbox. Si Kimi/Qwen/Sonnet logra misma calidad con 40% menos costo, se propone cambio. Si no, Opus sigue. **El rey conserva la corona, pero todos los meses hay torneo.**

Estado actual: **DRAFT — registro vacio.** El poblamiento se hace via promocion desde Token Ledger cuando outputs aprobados clean cumplen criterios.

---

## Schema de un pin

```yaml
output_pin:
  pin_id:                       uuid
  status:                       "active" | "challenged" | "demoted" | "retired"

  # === Firma del pin (lo que define a que tarea aplica) ===
  signature:
    task_type:                  string             # alineado con SPEC_LLM_ROUTING task_type
    skill_id:                   string
    brand:                      "MWT" | "FaberLoom" | "SHARED"
    client_context_hash:        string             # hash del contexto del cliente (idioma, sector, region)
    data_classification:        "N0" | "N1" | "N2" | "N3" | "N4"
    similarity_threshold:       float              # default 0.90 — minimo gold_match_score para activar el pin

  # === Receta pineada ===
  recipe:
    model:                      string             # ej. "claude-opus-4-7"
    model_version:              string             # version exacta cuando fue pineado
    provider_action_id:         string             # ref ENT_PLAT_ACTION_REGISTRY
    prompt_hash:                string             # SHA-256 del prompt compiled
    prompt_template_ref:        string             # ref al template del skill
    temperature:                float
    max_tokens:                 int
    context_template_hash:      string             # hash del context_template usado
    few_shot_refs:              [uuid]             # ref golden_cases usados como few-shot

  # === Origen ===
  origin:
    source_run_id:              uuid               # run real del Token Ledger
    source_ledger_entry_id:     uuid
    source_outcome_entry_id:    uuid               # ref RequestOutcomeEntry
    source_output_hash:         string             # output exacto que el CEO aprobo
    edit_distance_at_origin:    float              # debe ser 0.0 (clean) para ser candidate
    cost_usd_at_origin:         float
    timestamp_origin:           datetime
    approved_by_ceo_at:         datetime

  # === Justificacion ===
  why_pinned:                   string             # 2-5 lineas — por que merece quedar pineado
  unique_value:                 [string]           # que aporta este modelo que otros no podrian

  # === Estado de torneo (re-evaluacion) ===
  tournament:
    last_run_at:                date
    next_run_due:               date               # default: ultima_run + 30 dias
    runs_history:
      - run_id:                 uuid
        run_date:               date
        challengers:            [string]           # modelos retadores corridos
        defender_score:         float              # score del modelo pineado
        defender_cost_usd:      float
        challenger_results:                       # un entry por retador
          - challenger_model:   string
            score:              float
            cost_usd:           float
            score_delta_vs_defender: float        # negativo = challenger peor; positivo = mejor
            cost_delta_pct:     float             # negativo = challenger mas barato
            recommendation:     "keep_pin" | "propose_repin" | "inconclusive"
        ceo_decision:           "keep_pin" | "repin_to_challenger" | "deferred"
        ceo_decision_at:        datetime

  # === Versionado del pin ===
  version:                      int
  superseded_by:                uuid               # null si vigente; pin_id del nuevo si fue desplazado
  superseded_at:                datetime
  retirement_reason:            string             # solo si status=retired
```

---

## Cuando se crea un pin

Un pin candidato se propone cuando se cumplen TODAS las condiciones:

1. Output del run paso por final pass premium (no shortcut).
2. CEO marco el RequestOutcomeEntry como `outcome: approved` con `edit_distance: 0.0`.
3. La firma (task_type + skill_id + client_context_hash + data_classification) NO tiene pin activo.
4. El cost del run fue >USD 0.05 (umbral configurable; pins con costo trivial no aportan ahorro).
5. El task_type aparece >=3 veces en Token Ledger en los ultimos 30 dias (no pinear singletons).

CEO recibe propuesta, aprueba o rechaza explicitamente. Pin sin aprobacion CEO no entra al registro.

---

## Como se usa un pin (short-circuit)

En cada llamada LLM, el L2 Dispatcher consulta:

```python
def find_active_pin(signature):
    candidates = ENT_AI_GOV_OUTPUT_PINS.where(
        signature.task_type == requested.task_type,
        signature.skill_id == requested.skill_id,
        signature.brand == requested.brand,
        signature.data_classification == requested.data_classification,
        status == "active"
    )
    for pin in candidates:
        similarity = compute_context_similarity(
            requested.client_context_hash,
            pin.signature.client_context_hash
        )
        if similarity >= pin.signature.similarity_threshold:
            return pin
    return None
```

Si hay pin activo + similarity >= threshold + las 5 condiciones de POL_AI_GOV_FINAL_OUTPUT_QUALITY §E:
- L2 Dispatcher fuerza `mode: SINGLE` con el modelo del pin.
- L3 Compiler usa el `prompt_hash` y `context_template_hash` del pin.
- Token Ledger registra `pinned_output_id: <pin_id>`, `pin_status: "matched"`, `final_pass_executed: false`, `final_pass_shortcut_reason: "pin_match similarity=0.94"`.

---

## Re-evaluacion mensual (torneo)

Cada pin con `status: active` corre torneo cada 30 dias (`next_run_due`):

```
Procedimiento del torneo:

1. Sandbox aislado del run de produccion. NO afecta usuarios.

2. Subset del corpus (ENT_AI_GOV_GOLDEN_CORPUS_MWT) relevante al task_type del pin.
   Minimo 5 cases, idealmente 10.

3. Defender = modelo del pin con la receta exacta.
   Challengers = ranking de modelos del momento:
     - mismo modelo nueva version (ej. Sonnet 4.6 -> 4.7)
     - alternativas mas baratas que pasaron quality bar reciente (Kimi K2.6, Qwen3.5)
     - modelos nuevos del ecosistema (DeepSeek v5, Gemini 3.5)

4. Mismo prompt + mismo contexto en todos. Variable unica = modelo.

5. Judge model (Sonnet 4.6 default) evalua score 0..1 por output.
   Cross-check con Opus 4.7 sobre 20% sample.

6. Resultado:
   - score_delta_vs_defender < 5% (challenger no mejor o equivalente):
       recommendation: "keep_pin"
   - score_delta_vs_defender >= -5% (challenger igual o mejor)
       AND cost_delta_pct <= -40% (challenger >=40% mas barato):
       recommendation: "propose_repin"
   - cualquier otro caso:
       recommendation: "inconclusive"

7. CEO recibe propuestas. Decide: keep_pin | repin_to_challenger | deferred.

8. Si repin_to_challenger:
   - pin actual: status -> retired, superseded_by = nuevo pin_id
   - nuevo pin: status -> active, version++, origen = run del torneo

9. Resultado del torneo queda en tournament.runs_history del pin.
```

---

## Estados del pin

```
active                  -> pin operativo, short-circuit habilitado
   |
   v retando en sandbox sin desplazarlo
challenged              -> torneo en curso o pendiente decision CEO
   |
   v si retador gana
demoted                 -> pin reemplazado, esta en gracia 7 dias antes de retirement (rollback window)
   |
   v
retired                 -> archivado, no se usa, queda en registro para auditoria historica
```

---

## Anti-dogma

Pin no es dogma:
- Un pin no es vitalicio. Si nunca corre torneo, esta estancado.
- Un pin perdedor no queda por inercia. CEO decide explicitamente; defaultear a "keep" sin runs es prohibido.
- Un pin con 6 meses sin torneo activa alerta automatica al owner.

Pin tampoco es democracia:
- CEO es el aprobador final. Score de judge es input, no decision.
- Re-pin nunca se ejecuta automaticamente. Auto-replace = pin estancado en otra forma.

---

## Anti-patrones

1. **Pinear todo lo que sale clean.** Pins triviales (output corto, costo bajo) saturan el registry sin aportar ahorro. Umbral de costo USD 0.05 minimo.
2. **Pinear sin contexto del cliente en la firma.** Mismo task_type para clientes diferentes con tono/idioma/sector distintos no comparten pin. `client_context_hash` discrimina.
3. **No correr torneo "porque ya gano".** Sin disciplina mensual, los ahorros disponibles se quedan en la mesa. Los modelos baratos mejoran rapido.
4. **Subir threshold de similarity para activar mas el pin.** Threshold default 0.90 protege contra falsos matches. Bajarlo a 0.7 hace que el pin se active en casos donde no aplica → outputs incorrectos.
5. **Re-pin sin re-evaluacion explicita.** Cambiar receta sin correr torneo es bypass del proceso.

---

## Relacion con ENT_AI_GOV_GOLDEN_CORPUS_MWT

El corpus golden es el **estandar de evaluacion**; el pin es la **receta operativa**. Relacion:

- Cada categoria del corpus es un task_type que puede tener pin asociado.
- El corpus se usa para evaluar el pin (torneo) y para validar nuevos candidatos.
- Cuando un pin pasa a retired, la receta se preserva en archivo pero los golden_cases que la evaluaron quedan vinculados via eval_history para auditoria retrospectiva.
- Outputs de produccion que el CEO aprueba clean son candidatos a pin Y candidatos a golden_case (canales separados, ambos requieren review CEO).

---

## Lo que esto NO es

- No es cache de outputs. Es cache de **recetas** (modelo + prompt + parametros).
- No es selector automatico de modelo (eso lo hace L2 Dispatcher consultando este registry).
- No es licencia para saltar final pass. El pin habilita short-circuit del final pass solo cuando POL_AI_GOV_FINAL_OUTPUT_QUALITY §E lo permite.
- No es archivo historico (cases retired se preservan, pero registry operativo solo expone status=active).

---

Changelog:
- v1.0 (2026-05-01): Creacion. Esqueleto definido. Schema output_pin completo. Procedimiento de pinning + torneo mensual + estados. 5 condiciones para crear pin. Anti-dogma y anti-patrones. Estado: DRAFT — registry vacio, poblamiento via promocion desde Token Ledger post-implementacion. Origen: sesion AI_GOV 2026-05-01.
