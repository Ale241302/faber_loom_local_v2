---
id: SCH_FB_WS_INSTRUCTIONS_v1
version: 1.1
status: DEFERRED -- diseno de referencia E3+, no gobierna implementacion E1-E2
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SCH
stamp: DEFERRED 2026-06-10 (era VIGENTE 2026-05-07; diferido por enmienda SPEC_FB_VOICE_HUMANIZER v2.1 -- LOC_INSTRUCCIONES_WS no se implementa en E1-E2)
fecha: 2026-05-07
agente: Cowork (redaccion) + CEO (decision arquitectura)
aplica_a: [FaberLoom]
implementa: SPEC_FB_VOICE_HUMANIZER_v2
relacionado:
  - SPEC_FB_VOICE_HUMANIZER_v2
  - SCH_FB_VOICE_PROFILE_v1
  - POL_FB_VOICE_RESOLUTION_v1
  - SPEC_FB_KNOWLEDGE_ATLAS_v1 (capa L3 Workspace)
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1 (account-centric)
---

# SCH_FB_WS_INSTRUCTIONS_v1

## Schema YAML de instrucciones de modulacion del workspace (LOC_INSTRUCCIONES_WS_<ws_id>.md)

## 1. Proposito

Define la estructura canonica del archivo `LOC_INSTRUCCIONES_WS_<ws_id>.md` que contiene las instrucciones declarativas del dueno del workspace para modular la voz user en outputs de ese workspace (capa L3 del Knowledge Atlas).

Decisiones CEO 2026-05-07 que este schema implementa:
- Q4: estilo cliente se constituye como "skill o conjunto de instrucciones persistentes" (declaracion explicita, no auto-aprendido)
- Q5: solo el dueno del workspace edita
- Q9: declaracion parcial - solo se escriben propiedades que se quieren modificar; resto pasa intacto del user

## 2. Schema YAML completo

```yaml
ws_instructions:
  workspace_id: uuid                         # FK a workspaces
  tenant_id: uuid                            # FK a tenants (RLS)
  version: int                               # bump cada edicion del dueno
  declared_by: uuid                          # user_id del dueno actual del workspace
  declared_at: ISO8601
  last_updated_at: ISO8601

  # === CONTEXTO DEL WORKSPACE (descriptivo, no afecta voz) ===

  context:
    description: string                      # 1-2 frases libres del dueno: "Cliente de alto volumen, prefiere comunicacion directa"
    relationship_stage: enum?                # nuevo | activo | maduro | en-disputa | recuperacion (opcional, informa tono)
    relationship_notes: string?              # libre
    cultural_notes: string?                  # ej: "tutea siempre", "espera respuesta en horas habiles MX"

  # === DECLARACION PARCIAL DE PROPIEDADES (CORE) ===
  # Solo se escriben las propiedades que se quieren modificar.
  # Lo no declarado pasa intacto del sabor del user controlador.

  declared_overrides:
    saludo_email: string?                    # ej: "Hola Sondel" (override del user default)
    saludo_email_continuation: string?
    saludo_whatsapp: string?
    cierre_email: string?
    cierre_whatsapp: string?
    tono: enum?                              # formal | cortes-cercano | directo | casual (override base_tone user)
    formality_register: enum?
    longitud: enum?                          # concisa | detallada | muy-detallada
    paragraph_style: enum?
    bullet_usage: enum?

    # Override de firma SOLO si dueno explicitamente lo declara
    # (caso raro: cliente exige formato especifico de firma, ej: numero RFC)
    signature_email_override: string?
    signature_whatsapp_override: string?

  # === CONSTRAINTS ESPECIFICOS DEL WORKSPACE ===

  banned_phrases_workspace: array<banned_phrase>  # frases prohibidas para este workspace
  preferred_terms_workspace: array<preferred_term>  # terminos preferidos especificos
  required_phrases: array<required_phrase>?       # frases que DEBEN aparecer (raro, ej: clausula legal obligatoria)

  # === REGLAS CONDICIONALES (avanzado, opcional E1) ===

  conditional_rules: array<conditional_rule>?
  # cada regla:
  #   when: condicion (intent | sentiment | thread_age | etc.)
  #   then: overrides adicionales

  # === META ===

  enforcement_level: enum                    # strict | recommended (default: strict)
  audit_log_signature_required: bool         # si dueno requiere que cada output documente las instrucciones aplicadas

  # === LIFECYCLE ===

  active: bool                               # si esta vigente
  superseded_by: string?                     # ws_instructions_id que lo reemplaza
  superseded_at: ISO8601?
```

## 3. Tipos auxiliares

```yaml
banned_phrase:
  phrase: string
  case_sensitive: bool
  match_mode: enum                           # exact | contains | regex
  reason: string                             # libre, para audit
  severity: enum                             # high | medium | low (afecta retry behavior, ver SPEC_FB_VOICE_HUMANIZER_v2 seccion 8)
  declared_at: ISO8601
  declared_by: uuid

preferred_term:
  generic_term: string                       # termino que NO usar para este concepto
  workspace_preferred_term: string           # termino que SI usar
  applies_to_concept: string                 # libre
  examples: array<string>?

required_phrase:
  phrase: string
  context: enum                              # always | per_intent | per_thread_state
  context_value: string?                     # ej: intent="quote_request"
  reason: string
  legal_origin: bool                         # si es obligatorio por compliance/contrato

conditional_rule:
  rule_id: uuid
  description: string
  when:
    intent: string?                          # ej: "complaint"
    sentiment: enum?                         # ej: "negative"
    thread_age_days_gt: int?
    thread_state: string?
    operator_role: enum?
  then:                                      # overrides adicionales que aplican si condicion match
    tono: enum?
    longitud: enum?
    saludo_email: string?
    additional_banned_phrases: array<banned_phrase>?
    escalation_required: bool?               # marca el draft para review extra
  priority: int                              # si multiple rules match, mayor priority gana
```

## 4. Declaracion parcial: ejemplos

### 4.1 Ejemplo minimal (solo saludo)

```yaml
ws_instructions:
  workspace_id: ws_sondel
  tenant_id: tenant_mwt
  version: 1
  declared_by: user_alejandro
  declared_at: 2026-05-07T14:30:00-06:00
  last_updated_at: 2026-05-07T14:30:00-06:00

  context:
    description: "Cliente premium MX, prefiere directo y rapido"

  declared_overrides:
    saludo_email: "Hola Sondel"
    # nada mas declarado - todo lo demas pasa del sabor user_alejandro

  banned_phrases_workspace: []
  preferred_terms_workspace: []
  enforcement_level: strict
  active: true
```

### 4.2 Ejemplo intermedio

```yaml
ws_instructions:
  workspace_id: ws_constructora_alfa
  tenant_id: tenant_mwt
  version: 3
  declared_by: user_pedro
  declared_at: 2026-05-07T14:30:00-06:00
  last_updated_at: 2026-05-07T14:30:00-06:00

  context:
    description: "Cliente corporativo grande, area de compras formal"
    relationship_stage: activo
    cultural_notes: "Trato de usted siempre. Comunicacion por email predominante."

  declared_overrides:
    tono: formal
    formality_register: alto
    longitud: detallada
    saludo_email: "Estimados senores"

  banned_phrases_workspace:
    - phrase: "para servirle"
      case_sensitive: false
      match_mode: contains
      reason: "Cliente prefiere terminologia mas profesional"
      severity: medium
      declared_at: 2026-05-07T14:30:00-06:00
      declared_by: user_pedro

  preferred_terms_workspace:
    - generic_term: "cotizacion"
      workspace_preferred_term: "propuesta economica"
      applies_to_concept: "documento de precios"

  enforcement_level: strict
  active: true
```

### 4.3 Ejemplo avanzado (con conditional_rules)

```yaml
ws_instructions:
  workspace_id: ws_distrib_ramirez
  ...

  declared_overrides:
    longitud: concisa

  conditional_rules:
    - rule_id: rule_complaint_handling
      description: "Cuando es queja, escalar a tono mas formal y detallado"
      when:
        intent: "complaint"
        sentiment: "negative"
      then:
        tono: formal
        longitud: detallada
        saludo_email: "Estimado equipo Ramirez"
        escalation_required: true
      priority: 10
```

## 5. Resolucion en runtime

Voice Humanizer combina:
1. `LOC_VOICE_USER_<controller>.md` - sabor base
2. `LOC_INSTRUCCIONES_WS_<workspace>.md` - overrides declarados
3. ajuste transitorio si lo hay - one-off

Resolucion property-by-property segun `POL_FB_VOICE_RESOLUTION_v1`. Si una propiedad esta en `declared_overrides`, gana sobre la del user. Si no esta, el user pasa intacto.

`conditional_rules` se evaluan en runtime contra el contexto del request. Si una rule match, sus `then` overrides se aplican ENCIMA de los `declared_overrides` base (rules ganan sobre overrides estaticos, segun priority).

## 6. Quien edita

Decision CEO Q5: solo el dueno del workspace (`controlled_by`) puede editar `ws_instructions`.

| Rol | Permission |
|---|---|
| Dueno del workspace (controlled_by) | read + write |
| Owner+Admin del tenant | read (audit) + write con override flag (caso raro: gobernanza) |
| Otros users asignados al workspace | read only |
| Users no asignados al workspace | sin acceso (RLS) |

Si workspace cambia de controlador, las instrucciones persisten (son del workspace, no del user). Nuevo controlador puede editarlas.

## 7. Reglas de validacion

| Regla | Aplicacion |
|---|---|
| `workspace_id` y `tenant_id` obligatorios | Schema validation strict |
| `declared_by` debe ser `controlled_by` del workspace al momento de la declaracion | Trigger DB |
| `version` debe incrementar al modificar | Trigger DB |
| `enforcement_level` default `strict` | Si no declarado |
| `banned_phrases_workspace` cada item con severity valida (high/medium/low) | Schema validation |
| `conditional_rules` priority unico dentro del workspace | Constraint runtime |
| Si workspace tipo "system" (lab, fallback): instrucciones opcionales | Lab y fallback workspaces no requieren modulacion |

## 8. Lifecycle

| Evento | Comportamiento |
|---|---|
| Workspace creado | `ws_instructions` opcional. Si no existe, voz pasa 100% del user controlador |
| Dueno crea/edita instrucciones | `version++`, `last_updated_at` bump, signal a Voice Humanizer para invalidate cache |
| Workspace cambia de controlador | Instrucciones persisten. Nuevo controlador puede editar. `declared_by` se actualiza al primer edit del nuevo |
| Workspace archivado | Instrucciones archivadas con el workspace |
| Tenant migra de vertical | Instrucciones se preservan; pueden requerir revision si vertical_unit_type cambia |

## 9. Changelog

- v1.0 (2026-05-07) VIGENTE: Schema inicial. Declaracion parcial property-level. Conditional rules opcionales (uso avanzado E1). Compatible con modelo workspaces=cuenta del adapter pattern.

## Changelog

- v1.1 (2026-06-10) DEFERRED: diferido a E3+ por enmienda SPEC_FB_VOICE_HUMANIZER v2.1 (LOC_INSTRUCCIONES_WS no se implementa en E1-E2). Contenido integro como diseno de referencia.
- v1.0 (2026-05-07) VIGENTE: creacion.

## Stamp

DEFERRED 2026-06-10 (era VIGENTE 2026-05-07). Schema canonico de instrucciones de modulacion workspace para Foundation Beta E1. Consumido por SKILL_VOICE_HUMANIZER en runtime via voice_context_resolver. Storage en DB segun SPEC_FB_DATA_MODEL_v1 tabla `workspace_voice_instructions`.
