---
id: SCH_FB_VOICE_PROFILE_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SCH
stamp: VIGENTE 2026-05-07
fecha: 2026-05-07
agente: Cowork (redaccion) + CEO (decision arquitectura)
aplica_a: [FaberLoom]
implementa: SPEC_FB_VOICE_HUMANIZER_v2
relacionado:
  - SPEC_FB_VOICE_HUMANIZER_v2
  - SCH_FB_WS_INSTRUCTIONS_v1
  - POL_FB_VOICE_RESOLUTION_v1
  - SPEC_FB_KNOWLEDGE_ATLAS_v1 (capa L4 Usuario)
---

# SCH_FB_VOICE_PROFILE_v1

## Schema YAML del sabor user (LOC_VOICE_USER_<user_id>.md)

## 1. Proposito

Define la estructura canonica del archivo `LOC_VOICE_USER_<user_id>.md` que contiene el sabor del user (capa L4 del Knowledge Atlas).

Una sola voz por user (decision CEO 2026-05-07 Q1). Evoluciona con HITL signals (decision Q10).

## 2. Schema YAML completo

```yaml
voice_profile:
  user_id: uuid                              # FK a users
  tenant_id: uuid                            # FK a tenants (RLS)
  version: int                               # bump cada vez que aprendizaje implicito modifica el perfil
  bootstrap_method: enum                     # explicit_simple_e1 | csv_analysis_e3 (E1 = explicit_simple_e1 only)
  created_at: ISO8601
  last_updated_at: ISO8601
  last_signal_processed_at: ISO8601?

  # === CORE: el "sabor" del user ===

  persona:
    description: string                      # 1-2 frases libres del user describiendose ("soy directo, valoro precision, evito formalismos vacios")
    base_tone: enum                          # formal | cortes-cercano | directo | casual
    formality_register: enum                 # alto | medio | medio-bajo | bajo

  greetings:
    default_email: string                    # ej: "Buenos dias"
    default_email_continuation: string?      # ej: "Hola de nuevo" cuando hilo es continuo
    default_whatsapp: string                 # ej: "Hola"
    default_whatsapp_continuation: string?   # ej: "" (sin saludo en hilo continuo)
    custom_greetings: array<custom_greeting>?  # opcional, para casos puntuales aprendidos

  closings:
    default_email: string                    # ej: "Saludos cordiales"
    default_whatsapp: string                 # ej: "Saludos"
    custom_closings: array<custom_closing>?

  signature:
    full_email: string                       # firma completa email (multilinea: nombre, cargo, empresa, contacto)
    short_email: string                      # firma corta para hilos largos
    whatsapp: string                         # firma reducida WhatsApp (en general nombre solo)
    inline_signoff: string                   # forma corta inline ("- Alejandro")

  length_preference:
    default: enum                            # concisa | detallada | muy-detallada
    by_intent: object?                       # override por intent (ej: complaint -> detallada)

  vocabulary:
    preferred_terms: array<preferred_term>   # terminos que el user usa de forma consistente
    avoided_terms: array<avoided_term>       # terminos que el user evita ("perfecto", "claro", etc.)
    personal_glossary: array<glossary_entry> # equivalencias personales user > generico

  structural_preferences:
    paragraph_style: enum                    # corto-3-frases | medio | parrafo-largo
    bullet_usage: enum                       # frecuente | moderado | nunca
    nested_clauses: enum                     # frecuente | moderado | nunca
    questions_at_end: bool                   # si el user suele cerrar con pregunta

  channel_specifics:
    whatsapp:
      uses_emoji: bool
      emoji_set: array<string>?              # set restringido si uses_emoji=true
      max_length_chars: int?                 # cap auto-aplicado
    email:
      uses_html_formatting: bool
      uses_bullet_lists: bool

  # === LEARNING SIGNALS (acumulado via HITL) ===

  learning_signals:
    total_signals_captured: int
    signals_since_last_recompute: int
    last_recompute_at: ISO8601?

    pending_candidate_changes: array<voice_candidate>?  # cambios sugeridos pero no aplicados
    # cada voice_candidate tiene:
    #   property: string (saludo | tono | longitud | etc.)
    #   suggested_value: any
    #   confidence: float (0-1)
    #   evidence_count: int (cuantos signals soportan)
    #   evidence_signals: array<signal_id>
    #   action_required: enum (auto_apply | user_confirm | review)

  # === META ===

  privacy_tier: enum                         # PRIVATE_RAW (default L4) | TENANT_DERIVED (si user opto compartir)
  visibility_overrides: array<visibility_override>?  # ej: "user X puede ver mi voice" (default solo el user mismo)

  # === COMPATIBILIDAD HACIA ATRAS (preserva v1) ===

  voice_user_v1_legacy:
    csv_imported: bool                       # E1 = false. E3 podra ser true si hubo CSV upload
    last_csv_import_at: ISO8601?
    detected_patterns_count: int?
```

## 3. Tipos auxiliares

```yaml
custom_greeting:
  context_tag: string                        # ej: "cliente_premium" | "primera_vez"
  greeting_text: string
  applies_when: object                       # condiciones de aplicacion

custom_closing:
  context_tag: string
  closing_text: string
  applies_when: object

preferred_term:
  term: string
  used_for_concept: string                   # ej: "cotizacion" para el concepto generico "documento de precios"
  evidence_count: int

avoided_term:
  term: string
  reason: enum                               # personal | redundant | imprecise | other
  reason_freetext: string?

glossary_entry:
  generic_term: string
  user_preferred_term: string
  examples: array<string>?

voice_candidate:
  candidate_id: uuid
  property: string
  current_value: any
  suggested_value: any
  confidence: float
  evidence_count: int
  evidence_signals: array<signal_id>
  action_required: enum                      # auto_apply (no user input) | user_confirm | review
  detected_at: ISO8601

visibility_override:
  granted_to_user_id: uuid
  scope: enum                                # full | structural_only | metrics_only
  granted_at: ISO8601
```

## 4. Bootstrap E1 (decision CEO 2026-05-07 opcion B)

Cuando un user nuevo es creado en E1, el sistema le presenta UI de configuracion explicita simple:

| Campo UI | Mapeo schema |
|---|---|
| "Como te describes en una frase?" | `persona.description` |
| "Tono base" (dropdown 4 opciones) | `persona.base_tone` |
| "Saludo email default" | `greetings.default_email` |
| "Cierre email default" | `closings.default_email` |
| "Firma email completa" (textarea multilinea) | `signature.full_email` |
| "Saludo WhatsApp" | `greetings.default_whatsapp` |
| "Largo preferido" (dropdown 3 opciones) | `length_preference.default` |
| "Pega 2-3 ejemplos de correos tuyos" (textareas) | NO se persisten en el schema; se procesan para auto-detectar `vocabulary.preferred_terms`, `structural_preferences.paragraph_style`, `structural_preferences.bullet_usage` |

Defaults razonables si el user salta campos:
- base_tone: cortes-cercano
- length_preference.default: concisa
- bullet_usage: moderado

CSV upload completo (analisis de N correos historicos para inicializar todos los campos detectables) queda en `voice_user_v1_legacy.csv_imported = false` y diferido a E3.

## 5. Reglas de validacion

| Regla | Aplicacion |
|---|---|
| `user_id` y `tenant_id` obligatorios | Schema validation strict |
| `version` debe incrementar al modificar | Trigger DB en update |
| `bootstrap_method` solo `explicit_simple_e1` permitido en E1 | Constraint enum runtime |
| `persona.description` 10-500 chars | UI + schema validation |
| `signature.full_email` debe contener al menos nombre completo | UI hint, no hard validation |
| `pending_candidate_changes` max 50 items | Cap operativo, signals adicionales en queue separado |
| `privacy_tier` default `PRIVATE_RAW` | No comparte con otros users del tenant sin opt-in explicito |

## 6. Visibilidad y proteccion

`LOC_VOICE_USER_<user_id>.md` es **propiedad del user**:

- Solo el user mismo puede leer/editar el archivo completo
- Owner+Admin del tenant pueden ver metadatos (version, last_updated_at, total_signals_captured) para soporte/audit, NO contenido
- El sistema (Voice Humanizer skill) tiene read-only access para resolver voice_pack en runtime
- En la UI, el user tiene tab "Mi voz" donde ve y edita su propio profile + ve los pending_candidate_changes

Privacy tiers segun `POL_FB_KR_PRIVACY_TIERS_v1`:
- Default: `PRIVATE_RAW` (capa L4 Knowledge Atlas, nunca cross-tenant)
- Opcional: `TENANT_DERIVED` con redaction si user opta compartir (E2+, no E1)

## 7. Lifecycle

| Evento | Comportamiento |
|---|---|
| User creado en tenant | Voice profile bootstrap UI obligatoria antes de poder operar workspaces |
| User edita campos manualmente | `last_updated_at` bump, `version++` |
| HITL signal procesado | candidate generado, NO se aplica automatico salvo `action_required: auto_apply` (E1: ningun cambio es auto_apply, todos requieren user confirm) |
| User aprueba candidate | aplicado al profile, `version++`, signal asociado marcado como procesado |
| User removido del tenant | profile archived (no eliminado para audit), workspaces controlados por user requieren reasignacion |

## 8. Changelog

- v1.0 (2026-05-07) VIGENTE: Schema inicial. Bootstrap E1 explicit_simple_e1. Compatibilidad hacia atras con voice_user v1 (CSV import). Pendiente E1 wireframe UI bootstrap.

## Stamp

VIGENTE 2026-05-07. Schema canonico del sabor user para Foundation Beta E1. Consumido por SKILL_VOICE_HUMANIZER en runtime via voice_context_resolver. Storage en DB segun SPEC_FB_DATA_MODEL_v1 tabla `voice_profiles`.
