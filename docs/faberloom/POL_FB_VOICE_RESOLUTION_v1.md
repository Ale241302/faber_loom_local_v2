---
id: POL_FB_VOICE_RESOLUTION_v1
version: 1.1
status: DEFERRED -- diseno de referencia E3+, no gobierna implementacion E1-E2
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: POL
stamp: DEFERRED 2026-06-10 (era VIGENTE 2026-05-07; diferido por enmienda SPEC_FB_VOICE_HUMANIZER v2.1 -- en E1-E2 la voz es bloque de estilo + few-shot de gold samples; senal de reactivacion: >1 voz por workspace o edit-rate por tono >20% sostenido)
fecha: 2026-05-07
agente: Cowork (redaccion) + CEO (decision arquitectura)
aplica_a: [FaberLoom]
implementa: SPEC_FB_VOICE_HUMANIZER_v2
relacionado:
  - SPEC_FB_VOICE_HUMANIZER_v2
  - SCH_FB_VOICE_PROFILE_v1
  - SCH_FB_WS_INSTRUCTIONS_v1
  - POL_DATA_CLASSIFICATION
---

# POL_FB_VOICE_RESOLUTION_v1

## Politica de resolucion property-by-property de la voz en runtime

## 1. Proposito

Define la politica canonica que SKILL_VOICE_HUMANIZER aplica para resolver cada propiedad de voz en runtime, dada una composicion de:
- sabor del user controlador del workspace (LOC_VOICE_USER)
- instrucciones declaradas del workspace (LOC_INSTRUCCIONES_WS)
- ajuste transitorio del output (parametro runtime opcional)
- constraints organizacionales (POL_BANNED_PHRASES_TENANT, LOC_GLOSARIO_TENANT)

Implementa decisiones CEO 2026-05-07:
- Q9: workspace gana sobre user solo en propiedades declaradas; user pasa intacto donde no hay declaracion
- modelo property-level merge, no document-level

## 2. Principio rector

```
La voz NO se resuelve por precedencia jerarquica monolitica.
La voz se resuelve property-by-property con declaracion explicita.
```

Cada propiedad se resuelve independientemente. El resultado final es la composicion de N propiedades resueltas, no una "voz ganadora".

## 3. Algoritmo de resolucion canonico

Para CADA propiedad `p` de voz (saludo, cierre, longitud, formalidad, estructura, vocabulario, firma, tono, registro, paragraph_style, bullet_usage, etc.):

```
funcion resolver_propiedad(p, contexto):

    1. Si ajuste_transitorio.declares(p):
         return ajuste_transitorio[p]
         source_layer = "transient"

    2. Sino, evaluar conditional_rules del workspace:
         para cada rule en ws_instructions.conditional_rules ordenadas por priority desc:
             si rule.when match(contexto):
                 si rule.then.declares(p):
                     return rule.then[p]
                     source_layer = "ws_conditional_rule_<rule_id>"
                     break

    3. Sino, si ws_instructions.declared_overrides.declares(p):
         return ws_instructions.declared_overrides[p]
         source_layer = "ws_instructions_static"

    4. Sino, si voice_user_controlador.declares(p):
         return voice_user_controlador[p]
         source_layer = "user"

    5. Sino, fallback a defaults del schema (SCH_FB_VOICE_PROFILE_v1)
         return schema_default[p]
         source_layer = "schema_default"
```

## 4. Orden de evaluacion (de mayor a menor especificidad)

```
1. Ajuste transitorio del output (one-off)
2. Conditional rules del workspace (matched, ordered by priority desc)
3. Declared overrides estaticos del workspace
4. Sabor del user controlador
5. Defaults del schema (fallback ultimo)
```

Cada nivel se evalua INDEPENDIENTEMENTE por propiedad. No hay "winner takes all".

## 5. Constraints organizacionales (filtros post-resolucion)

Despues del merge property-by-property, antes de entregar el draft a Mesa, se aplican filtros tenant:

| Filtro | Fuente | Comportamiento |
|---|---|---|
| Banned phrases tenant | `POL_BANNED_PHRASES_TENANT.md` | Severity HIGH: regenerar fragmento (1 retry); si persiste, marca draft `BLOCKED_COMPLIANCE` y notifica dueno |
| Banned phrases workspace | `LOC_INSTRUCCIONES_WS_*.banned_phrases_workspace` | Severity segun declaracion (high/medium/low). High = mismo comportamiento que tenant. Medium = retry, conservar con flag visible si persiste. Low = flag visible al operator, sin retry |
| Required phrases workspace | `LOC_INSTRUCCIONES_WS_*.required_phrases` | Si phrase no aparece, regenerar (1 retry); si persiste, marca `MISSING_REQUIRED_PHRASE` para review en Mesa |
| Glosario tenant (preferred terms) | `LOC_GLOSARIO_TENANT.md` | Sustitucion automatica si match parcial; sin retry |
| Glosario vertical | `LOC_GLOSARIO_VERTICAL_<vertical>.md` (L1) | Sustitucion sugerida (no automatica); flag visible al operator si match |

Constraints NO compiten en el merge property-by-property. Se aplican como filtro despues.

## 6. Resolution trace obligatorio

Voice Humanizer DEBE emitir `resolution_trace` por output que documente, propiedad por propiedad, que capa decidio cada valor. Esto es:

- Auditable: el operator/Owner puede ver "saludo vino de workspace, tono vino de user, longitud vino de ajuste transitorio"
- Debuggable: si una propiedad sale "rara", el trace dice por que
- Promovable a learning signal: si el operator edita una propiedad cuya `source_layer = user`, ese signal va a learning del user; si la edita siendo `source_layer = ws_instructions_static`, va a feedback loop "instruccion no matiza" (E2)

Schema del trace en `voice_humanizer_output.resolution_trace` (ver SPEC_FB_VOICE_HUMANIZER_v2 seccion 15).

## 7. Casos especiales

### 7.1 Workspace sin instrucciones

Si `LOC_INSTRUCCIONES_WS_<ws_id>.md` no existe o esta vacio:
- Toda propiedad se resuelve directo del user controlador
- `source_layer = "user"` para todas
- El draft sale 100% en sabor del user, sin modulacion workspace

### 7.2 User sin voice profile completo

Si user controlador no tiene voice profile (caso anomalo, debe bloquear creacion de workspace):
- Fallback a `schema_default` para todas las propiedades
- Sistema marca alerta a Owner del tenant: "user_X opera workspace sin voice profile"
- Voice Humanizer entrega draft con voz neutra schema-default + flag visible

### 7.3 Multiple users asignados, distinto firmante

Si workspace tiene multiples users asignados y el firmante de un draft especifico no es el `controlled_by`:
- `voice_user_controlador` se resuelve a la voz del FIRMANTE, no del controller
- `ws_instructions` siguen aplicando (son del workspace, no del user)
- Resolution trace marca `signing_user_id` distinto de `workspace.controlled_by` para audit

### 7.4 Conditional rules con multiples matches

Si varias `conditional_rules` matchean el contexto:
- Se evaluan ordenadas por `priority` descendente
- Para cada propiedad `p`, gana el primer rule en orden que la declara
- Si dos rules con misma priority declaran la misma propiedad: error de configuracion, marca alerta al dueno; runtime usa el rule_id menor (determinista)

### 7.5 Ajuste transitorio que viola banned phrases

Si el operator pide via transient_instruction algo que activa una banned phrase tenant:
- Voice Humanizer aplica el ajuste pero el filtro post-resolucion lo bloquea
- Draft marca `TRANSIENT_VIOLATES_TENANT_POLICY`
- Operator ve el conflicto y debe ajustar la instruccion o aceptar la version sin el ajuste

## 8. Que NO permite la politica

| Prohibicion | Razon |
|---|---|
| Override de banned_phrases_tenant via ws_instructions o transient | Compliance tenant prevalece sobre cualquier modulacion |
| Skip de filtros post-resolucion | Constraints son guardrail no negociable |
| Cross-workspace voice merge (ws A toma instrucciones de ws B) | Aislamiento workspace; cross via knowledge imports declarados, no via merge runtime |
| Voice user de tenant A aplicada en tenant B | RLS hard a nivel DB. Cross-tenant access prohibido (TIER1 #16) |
| Modificacion del user voice por instrucciones del workspace | Workspace NO escribe sobre user voice; solo declara overrides para sus outputs |
| Resolucion sin firmante (signing_user_id obligatorio) | Outbound sin firmante humano declarado prohibido (HITL absoluto) |

## 9. Performance y caching

| Aspecto | Politica |
|---|---|
| Cache de `voice_user` profile | TTL 5 min, invalidate en `version++` |
| Cache de `ws_instructions` | TTL 5 min, invalidate en `version++` |
| Cache de constraints tenant (banned_phrases, glosario) | TTL 15 min, invalidate manual por Owner |
| Cache de conditional_rules compilados | TTL workspace lifetime, invalidate en edit |
| Resolucion completa (merge + filtros) | NO cacheable (ajuste transitorio puede ser distinto cada request) |

Latencia objetivo: resolucion completa < 100ms p95 sin LLM call (es merge en memoria + DB lookup). LLM call solo en fase de generacion del skill productor anterior, no en Voice Humanizer.

Voice Humanizer SI usa LLM call solo cuando hay regeneracion (banned phrase violacion + retry). En el flujo normal, Voice Humanizer es un transformador determinista.

## 10. Audit log

Cada output que pasa por Voice Humanizer DEBE registrar en audit log:

```yaml
voice_humanizer_audit:
  trace_id: uuid
  workspace_id: uuid
  signing_user_id: uuid
  controller_user_id: uuid
  ws_instructions_version: int
  voice_user_version: int
  channel: string
  transient_instruction_applied: bool
  transient_instruction_text: string?
  resolution_trace: object
  banned_violations_detected: array<violation>?
  retries_attempted: int
  final_state: enum                        # success | blocked_compliance | missing_required_phrase
  timestamp: ISO8601
  sha256: string                           # hash del output text para evidence
```

Audit log es append-only segun TIER1 #4. Storage en `audit_log` tabla con RLS por tenant.

## 11. Changelog

- v1.1 (2026-06-10) DEFERRED: diferida a E3+ por enmienda SPEC_FB_VOICE_HUMANIZER v2.1 (E1-E2 usa bloque de estilo + few-shot de gold samples; no hay resolucion property-by-property en runtime). Contenido integro como diseno de referencia. Senal de reactivacion en el stamp.
- v1.0 (2026-05-07) VIGENTE: Politica inicial. Resolucion property-by-property con orden 5 niveles. Constraints como filtros post-resolucion. Resolution trace obligatorio para auditabilidad y learning.

## Stamp

VIGENTE 2026-05-07. Politica canonica de resolucion de voz para Foundation Beta E1. Aplicada por SKILL_VOICE_HUMANIZER en cada output cliente-facing. Compatible con TIER1 #4 (audit) + TIER1 #15 (single-agent cadena lineal) + TIER1 #16 (cross-tenant prohibido).
