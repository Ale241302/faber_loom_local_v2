---
id: SPEC_FB_VOICE_HUMANIZER_v1
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE 2026-05-02 (canoniza Voice Profile / Humanizer Engine del mockup)
fecha: 2026-05-02
agente: Cowork (redaccion) + CEO (decision arquitectura)
aplica_a: [FaberLoom]
fuente_verdad: docs/anexos/mockups/mockup_e1_full_navigable.html (8 nodos voice + mini view voice + 3 voice candidates en gov)
relacionado:
  - SPEC_FB_KNOWLEDGE_ATLAS_v1.md
  - SPEC_FB_AI_CONTROL_PLANE_v1.md
  - POL_DATA_CLASSIFICATION
---

# SPEC_FB_VOICE_HUMANIZER_v1

## Voice Profile / Humanizer Engine · capability del @router

## 1. Por que existe este documento

Voice Profile no es "tono bonito". Es funcion humanizadora adaptativa que aprende como escribe el usuario y como habla la organizacion · sirve para que los agentes productores (generate_email, generate_quote, format_email, client_reply_draft) escriban drafts con voz consistente sin alterar datos.

Este SPEC canoniza el diseno del mockup donde Voice vive como capability del @router invocada por skills generadores.

## 2. Decision arquitectonica (no negociable)

Voice Profile NO es agente independiente.
Vive como capability del @router:

```
@router
  -> voice_context_resolver
      -> User Voice Profile
      -> Org Voice Profile
      -> Dept Voice Profile
      -> Channel Voice
      -> Recipient Voice
      -> voice_pack (output)
          -> consumido por generate_quote / format_email / etc.
```

Razon: si Voice fuera agente independiente que reescribe todo al final, podria deformar contenido (precios, claims, fechas). Como capability del router, la voz se RESUELVE primero · el agente productor APLICA la voz sabiendo que esta locked en facts.

## 3. Regla inquebrantable

```
La voz decide COMO decirlo.
NO decide QUE decir.
```

| Voice puede cambiar | Voice NO puede cambiar |
|---|---|
| saludo · cierre · longitud · formalidad · estructura · vocabulario · firma | precios · fechas · stock · claims tecnicos · promesas · condiciones comerciales · policies · datos cliente · aprobaciones |

## 4. Precedencia de capas (orden canon)

Si hay conflicto entre capas, gana esta precedencia:

```
1. Policies / compliance
2. Output schema
3. Org Voice
4. Dept Voice
5. User Voice
6. Recipient Voice
7. Channel Voice
```

## 5. Nodos canon (8 en Knowledge Atlas)

| Node ID | Tipo | Status | Que define |
|---|---|---|---|
| AGENT_router | AGENT | VIGENTE | Router central que invoca voice_context_resolver |
| SKILL_voice_context_resolver | SKILL | VIGENTE | Resuelve voice_pack segun firmante/canal/destinatario |
| voice_user_alvaro | VOICE_USER | VIGENTE | Voz personal del firmante (PRIVATE_RAW) |
| voice_org_mwt | VOICE_ORG | SIGNED | Voz institucional (TENANT_DERIVED) · brand + blocked_claims |
| voice_dept_comercial_mx | VOICE_DEPT | VIGENTE | Voz del equipo comercial MX |
| voice_channel_email | VOICE_CHANNEL | VIGENTE | Reglas para email externo |
| voice_recipient_corporate_buyer | VOICE_RECIPIENT | CANDIDATE | Preferencias compradores corporativos |
| voice_pack_output | OUTPUT | USABLE | Pack v1.2 que alimenta skills generadores |

## 6. Onboarding · CSV de enviados

El usuario sube CSV con columnas: `date · to · subject · body · signature · channel · client/company`

Sistema extrae patrones (saludos frecuentes · cierres · longitud · formalidad · terminos preferidos · terminos evitados · estructura · firma · variaciones por canal).

Nada se guarda automaticamente. Cada patron detectado se vuelve `voice_candidate` con acciones: Aplicar / Editar / Solo este canal / Promover a Dept / Descartar.

## 7. Candidates de voz · 3 tipos

| Tipo | Scope | Approval requerido |
|---|---|---|
| VOICE_GREETING_RULE | user | user (auto · va a User Voice) |
| VOICE_TERMINOLOGY_RULE | dept | manager (Comercial MX manager) |
| VOICE_BLOCKED_CLAIM_RULE | org/policy | governance + legal review |

Regla:
```
User Voice no se comparte automaticamente.
Promover User -> Dept o Dept -> Org requiere candidate + aprobacion.
```

## 8. Integration con Context Pack Trace

Voice Overlay aparece como **5ta source** en el step Sources del Context Pack Trace.

VOICE_PACK aparece como **6° item incluido** en el Context Pack Builder con detalle especifico (5 capas + blocked_terms + preferred_terms + confidence).

## 9. Mini view Voice Profile · 5 secciones canon

```
1. Baseline (CSV import + edits · v0.3 · 91% confidence · 248 emails)
2. Reglas activas (greeting/closing/tone/length/signature/preferred/blocked)
3. Ejemplos antes/despues (draft base vs humanized)
4. Aprendizajes pendientes (3 voice candidates con acciones)
5. Test de voz (5 tweaks: mas directo · mas formal · mas corto · menos vendedor · guardar)
+ Onboarding CSV con detected patterns
```

## 10. Que NO esta en este SPEC

- Implementacion del voice_context_resolver runtime (vive en SPEC_ACTION_ENGINE)
- Storage de voice profiles (vive en SPEC_FB_DATA_MODEL_v1.md)
- Promote workflow detallado L2 -> L3 (vive en SPEC_FB_KNOWLEDGE_ATLAS_v1.md seccion Governance)

## 11. Changelog

- v1.0 (2026-05-02) · Canonizacion del Voice Profile / Humanizer Engine del mockup. 8 nodos + mini view + 3 candidates + Voice Overlay en trace.
