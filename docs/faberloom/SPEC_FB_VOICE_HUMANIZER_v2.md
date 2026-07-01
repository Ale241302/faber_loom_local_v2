---
id: SPEC_FB_VOICE_HUMANIZER_v2
version: 2.1
status: VIGENTE (con enmienda v2.1: alcance E1-E2 colapsado, resolucion property-by-property DIFERIDA)
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: SPEC
stamp: VIGENTE 2026-06-10 (v2.0 cierre CEO 2026-05-07; v2.1 enmienda de alcance 2026-06-10)
fecha: 2026-05-07
agente: Cowork (redaccion) + CEO (decision arquitectura) + Gemini (facilitacion iteracion 11 preguntas)
aplica_a: [FaberLoom]
extiende: SPEC_FB_VOICE_HUMANIZER_v1 (canon 2026-05-02)
fuente_verdad:
  - sesion CEO 2026-05-07 (modelo workspaces=cuenta + Voice cross-system)
  - bloque iterado con Gemini 2026-05-07 (11 preguntas Voice Humanizer)
relacionado:
  - SPEC_FB_VOICE_HUMANIZER_v1 (sigue VIGENTE en lo no contradictorio)
  - SCH_FB_VOICE_PROFILE_v1 (schema sabor user)
  - SCH_FB_WS_INSTRUCTIONS_v1 (schema instrucciones workspace)
  - POL_FB_VOICE_RESOLUTION_v1 (politica resolucion property-by-property)
  - SPEC_FB_KNOWLEDGE_ATLAS_v1
  - SPEC_FB_AI_CONTROL_PLANE_v1
  - PLB_FB_FOUNDATION_BETA v1.3.1-FIRMADO (TIER1 #14 Voice Profile)
  - SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT_v1.1
---

# SPEC_FB_VOICE_HUMANIZER_v2

## Voice Humanizer · skill SYSTEM mandatory cross-system con resolucion property-by-property

## 1. Por que existe este documento

`SPEC_FB_VOICE_HUMANIZER_v1` (2026-05-02) canonizo Voice Profile como capability del @router con 5 capas (User / Org / Dept / Channel / Recipient) en orden de precedencia. La sesion 2026-05-07 (modelo workspaces=cuenta) refino el modelo y la iteracion con Gemini cerro 11 preguntas operativas.

Resultado: el modelo conceptual cambia de "5 capas con precedencia jerarquica" a "voz unica del user (sabor) modulada property-by-property por instrucciones del workspace y por ajustes transitorios del output". v2 canoniza esa refinacion.

v1 sigue VIGENTE en todo lo que NO entra en contradiccion (regla inquebrantable, integracion con Context Pack Trace, mini view, candidates de voz, integracion @router).

## 1bis. ENMIENDA v2.1 (2026-06-10) -- Alcance E1-E2 colapsado

Origen: revision de arquitectura 2026-06-10 (post EVAL_STRAT_2026-06-09 + SPEC_FB_BUILD_SEQUENCE v2).
Diagnostico: la maquinaria de resolucion property-by-property (este SPEC + SCH_FB_WS_INSTRUCTIONS + POL_FB_VOICE_RESOLUTION) resuelve un problema que con 1 tenant y 1-2 workspaces no existe. La voz es superficie, no estructura (MARCO_RECTOR prioridad #6): no merece subsistema propio antes de que el sistema produzca outputs.

**Implementacion vigente para E1-E2 (lo UNICO que se construye):**
1. **Bloque de estilo por tenant** inyectado en el system prompt: persona + tono + glosario + saludo (= decision firmada #15 del PLB, intacta) + firma por user. Vive en SCH_FB_VOICE_PROFILE_v1 (que sigue VIGENTE como schema del bloque).
2. **Few-shot de 3-5 drafts aprobados de la misma clase de tarea**, seleccionados de gold samples. Los drafts aprobados via Mesa capturan la voz real implicitamente -- mejor senal que cualquier declaracion de propiedades.
3. **Filtros tenant post-generacion** (banned phrases + glosario): se conservan tal cual (seccion 8). Son constraint, no voz.

**DIFERIDO a E3+ (diseno de referencia, NO implementar):** resolucion property-by-property en runtime, LOC_INSTRUCCIONES_WS por workspace, ajustes transitorios con flag, skill SYSTEM mandatory como paso de cadena, aprendizaje de voz via HITL signals tipificados. Documentos asociados pasan a DEFERRED: SCH_FB_WS_INSTRUCTIONS_v1, POL_FB_VOICE_RESOLUTION_v1.
**Senal de activacion:** un tenant real con >1 voz requerida por workspace, O edit-rate de Mesa atribuible a tono >20% sostenido con el bloque simple + few-shot ya operando.

Las secciones 2-17 de este documento describen el modelo completo y quedan como canon conceptual para cuando la senal dispare. NO gobiernan la implementacion de E1-E2.

## 2. Decision arquitectonica refinada

Voice Humanizer NO es agente independiente (regla canon v1 preservada).

Voice Humanizer ES skill SYSTEM mandatory que corre como ULTIMO paso de toda cadena lineal cliente-facing del agente principal del workspace. Aplica en cualquier canal: email, WhatsApp, futuros (SMS, chat, IVR diferido E3+).

```
agente_principal_del_workspace
  cadena lineal de skills:
    classify_intent
    retrieve_kb
    generate_quote   <- skill productor (genera contenido factual)
    format_output
    voice_humanizer  <- ULTIMO paso obligatorio (modula tono/forma)
  output -> Mesa de Control HITL -> outbound canal
```

Voice Humanizer es del producto FaberLoom (logica core). Tenants editan el knowledge que consume (`LOC_VOICE_USER_*`, `LOC_INSTRUCCIONES_WS_*`), nunca el codigo del skill.

## 3. Regla inquebrantable (preservada de v1)

```
La voz decide COMO decirlo.
NO decide QUE decir.
```

| Voice puede cambiar | Voice NO puede cambiar |
|---|---|
| saludo, cierre, longitud, formalidad, estructura, vocabulario, firma, tono, registro | precios, fechas, stock, claims tecnicos, promesas, condiciones comerciales, policies, datos cliente, aprobaciones, identidad del firmante real |

## 4. Modelo de capas refinado v2 (reemplaza seccion 4 de v1)

v1 declaraba precedencia jerarquica entre 5 capas (Policies > Schema > Org > Dept > User > Recipient > Channel). v2 simplifica:

### 4.1 La voz REAL es una sola: el sabor del user

**Sabor del user** = personalidad unica del firmante. Como humaniza, como itera, como saluda, como cierra. Una sola voz por user. Evoluciona con HITL (no con configuracion explicita avanzada en E1).

Vive en `LOC_VOICE_USER_<user_id>.md` (capa L4 del Knowledge Atlas).

### 4.2 Lo que v1 llamaba "Org/Dept/Channel/Recipient Voice" se reclasifica

| Concepto v1 | Reclasificacion v2 | Razon |
|---|---|---|
| Org Voice | NO es voz, es **knowledge/constraints**. Vive como `POL_BANNED_PHRASES_TENANT.md` + `LOC_GLOSARIO_TENANT.md` en L2. Aplica como filtro post-Voice, no como tono | El tenant define que NO se puede decir y que terminologia usar. El tono lo pone el user que firma |
| Dept Voice | Diferido. En E1 todos los users del tenant operan con su sabor + instrucciones de sus workspaces | Departamentalizacion fina aporta complejidad sin valor en E1 wedge unico |
| Channel Voice | Diferido. Mismo sabor user funciona cross-canal. Voice Humanizer recibe `channel` como parametro y renderiza adaptado (email full vs WhatsApp comprimido) | Canal-especifico es renderizacion, no voz distinta |
| Recipient Voice | Reemplazado por **instrucciones de workspace** (declarativas del dueno del workspace), NO una voz auto-aprendida del recipient | Workspace=cuenta cliente. El dueno declara como hablarle al cliente; no se infiere automaticamente |

### 4.3 Modulacion: instrucciones del workspace

**Instrucciones del workspace** = declaracion explicita del dueno del workspace de que propiedades de la voz se modifican para los outputs de ese workspace.

Vive en `LOC_INSTRUCCIONES_WS_<ws_id>.md` (capa L3 del Knowledge Atlas).

Ejemplo:
```yaml
# LOC_INSTRUCCIONES_WS_SONDEL.md
saludo: "Hola Sondel"
longitud: concisa
banned_phrases: ["estimados", "cordialmente"]
# todo lo no declarado se hereda del user controlador
```

Las instrucciones son **declaracion parcial**: solo se escriben las propiedades que el dueno quiere modificar. El resto pasa intacto del sabor user.

### 4.4 Ajuste transitorio del output

**Ajuste transitorio** = instruccion ad-hoc del operator para UN output especifico, sin persistir en knowledge.

Mecanismo: campo libre en Mesa antes de generar/regenerar draft ("hace este draft mas formal porque el cliente esta enojado"). Voice Humanizer recibe la instruccion como parametro runtime, la aplica sobre el draft, y muestra al user un flag visible: "Aplicado: tono mas formal por instruccion manual".

NO se promueve automaticamente a persistente. Si el operator detecta que las instrucciones del workspace no matizan bien su voz repetidamente, ese loop de feedback es un mecanismo aparte (diferido E2, ver seccion 11).

## 5. Resolucion property-by-property (canon v2)

Para cada propiedad de voz (saludo, cierre, longitud, formalidad, estructura, vocabulario, firma, tono, registro):

```
Si ajuste transitorio del output declara la propiedad -> gana
Sino, si instrucciones del workspace declaran la propiedad -> gana
Sino, hereda del sabor user controlador del workspace
```

Es **property-level merge**, no document-level. Cada propiedad se resuelve independientemente.

Ejemplo concreto:

```
Voz user Alejandro:
  saludo:    "Buenos dias"
  firma:     "Saludos cordiales, Alejandro Faro"
  tono:      formal-cortes
  longitud:  detallada
  glosario:  general

Instrucciones ws_sondel:
  saludo:    "Hola Sondel"     <- declara
  longitud:  concisa            <- declara
  (no declara firma, tono, glosario)

Output ws_sondel firmado por Alejandro:
  saludo:    "Hola Sondel"               <- workspace gana (declarado)
  firma:     "Saludos cordiales, ..."    <- user pasa (workspace no declara)
  tono:      formal-cortes                <- user pasa
  longitud:  concisa                      <- workspace gana
  glosario:  general                      <- user pasa
```

Constraints organizacionales (`POL_BANNED_PHRASES_TENANT`, `LOC_GLOSARIO_TENANT`) se aplican como filtro post-resolucion, NO compiten en el merge. Si el output resultante contiene una banned phrase, el skill regenera o aborta segun severity (ver seccion 8).

Detalle completo de resolucion en `POL_FB_VOICE_RESOLUTION_v1`.

## 6. Workspace bajo control de user

Regla: **todo workspace tiene `controlled_by` (user_id) obligatorio**.

- Workspace bajo control de user X -> outputs heredan sabor user X por default
- Si workspace cambia de controlador (X deja, Y toma), voice base cambia automaticamente al sabor de Y
- Instrucciones del workspace persisten al cambio de controlador (son del workspace, no del user)
- Workspaces multi-asignados (multiple users con permission de operar): voz = sabor del user que firma esa interaccion especifica (default: user que entra a Mesa primero a tomar el item; override "firmar como X" antes de outbound)
- Workspace sin controlador asignado (estado transitorio): cae a placeholder hasta asignacion. NO se permite outbound desde workspace sin controlador.

## 7. Bootstrap del sabor user en E1 (decision CEO 2026-05-07)

**Decision firmada: opcion B.**

E1 inicializa el sabor user con configuracion explicita simple:
- saludo default
- firma
- 2-3 ejemplos pegados manualmente (drafts representativos del user)
- tono base (dropdown: formal / cortes-cercano / directo / casual)
- longitud preferida (dropdown: concisa / detallada / muy detallada)

Analisis automatico del historico de correos via CSV upload (canon v1 seccion 6) queda **diferido a E3** segun TIER1 #14 del plan firmado: "Voice Profile completo (persona + tono + glosario + saludo + firma por user). Learning de muestras E3."

Razon de la diferencia: el wedge unico E1 es validar cotizaciones safety footwear con HITL en 13 semanas. El bootstrap rapido es suficiente para que la voz sea util desde dia 1. El sabor real se acumula via HITL Mesa (que SI esta en E1, ver seccion 9). El analisis profundo del historico es nice-to-have de E3.

Detalle completo: `SPEC_FB_VOICE_BOOTSTRAP_v1` (pendiente redaccion proxima sesion).

## 8. Filtros tenant aplicados post-resolucion

Despues del merge property-by-property, antes de entregar a Mesa, Voice Humanizer aplica dos filtros tenant:

| Filtro | Fuente | Comportamiento si se viola |
|---|---|---|
| Banned phrases tenant | `POL_BANNED_PHRASES_TENANT.md` | Severity HIGH: regenerar fragmento (1 retry); si persiste, marca draft como `BLOCKED_COMPLIANCE` y notifica dueno workspace |
| Banned phrases workspace | declaradas en `LOC_INSTRUCCIONES_WS_*.md` | Severity MEDIUM: regenerar fragmento (1 retry); si persiste, conserva pero flagea visible al operator |
| Glosario tenant (preferred terms) | `LOC_GLOSARIO_TENANT.md` | Sustitucion automatica si match parcial; sin retry |

## 9. Aprendizaje implicito del sabor user (canon v2)

El sabor evoluciona via signals de HITL Mesa. NO via override manual del user (decision Q11 cierre Gemini).

Cada vez que el operator edita un draft en Mesa, el sistema captura:
1. **Diff estructurado** entre draft generado y draft aprobado/editado
2. **Tipificacion del motivo** (decision CEO 2026-05-07: dropdown predefinido + campo libre opcional)
3. **Contexto** (workspace, skill productor, instrucciones aplicadas, ajuste transitorio si hubo)

Tipificacion dropdown E1:
- tono / formalidad
- contenido (no es voz, marca draft para revisar skill productor)
- saludo / cierre
- longitud
- terminologia / glosario
- banned phrase no respetada
- otro (campo libre obligatorio)

El campo libre opcional permite capturar el "porque" en lenguaje natural ("este cliente prefiere mensajes mas cortos"). Este texto va al signal de aprendizaje pero NO se promueve automaticamente.

Detalle completo: `POL_FB_VOICE_LEARNING_v1` (pendiente redaccion proxima sesion).

## 10. Cross-canal: misma voz, distinta renderizacion

Voice Humanizer recibe `channel` como parametro obligatorio. La voz es la misma; la renderizacion se adapta:

| Canal | Renderizacion |
|---|---|
| email | Voz completa: saludo, cuerpo estructurado, firma. Estructura formal segun tono base |
| WhatsApp | Voz comprimida: sin saludo formal cuando hilo es continuo, mas conversacional, mantiene tono base. Firma reducida (nombre, sin cargo en general) |
| SMS / chat (E2+) | Aun mas comprimido. Sin saludos. Mantiene tono base |
| llamada / IVR (E3+) | Voz convertida a TTS prompt. Tono adaptado a oral (frases mas cortas, sin nested clauses) |

UN sabor user, N renderizaciones segun canal. Esto evita inconsistencia entre lo que se escribe por email vs WhatsApp.

## 11. Loop de feedback "instruccion no matiza bien" (diferido E2)

Pregunta residual de la iteracion Gemini: "como reporta el operator al dueno del workspace que las instrucciones actuales no matizan bien su voz".

Mecanismo diferido a E2:

```
Operator edita draft >X% por la misma razon N veces en mismo workspace
   |
   v
Sistema captura signal: "instruccion ws_<id> no matiza voz user_<id> en contexto Y"
   |
   v
Cola "Revision de instrucciones" del dueno del workspace
   |
   v
Dueno revisa con contexto:
   - diff de los edits del operator
   - instruccion del workspace que no se respeto
   - frecuencia del patron
   |
   v
Dueno actualiza LOC_INSTRUCCIONES_WS_<id>.md
   |
   v
Proximos drafts incorporan instruccion actualizada
```

E1 NO implementa esto. En E1 el dueno revisa instrucciones manualmente con frecuencia que el decida. Cuando E2 acumule datos suficientes para calibrar el umbral del signal, se construye la cola.

Detalle: `SPEC_FB_VOICE_FEEDBACK_LOOP_v1` (E2, no en este SPEC).

## 12. Knowledge artifacts requeridos (taxonomia 8 + especiales)

| Archivo | Tipo | Capa | Cardinalidad | Editor |
|---|---|---|---|---|
| `LOC_VOICE_USER_<user_id>.md` | LOC | L4 Usuario | 1 por user | el user (E1: configuracion explicita simple via UI) + sistema (HITL signals) |
| `LOC_INSTRUCCIONES_WS_<ws_id>.md` | LOC | L3 Workspace | 1 por workspace que requiera modulacion | dueno del workspace (controlled_by) |
| `POL_BANNED_PHRASES_TENANT.md` | POL | L2 Tenant | 1 por tenant | Owner+Admin del tenant |
| `LOC_GLOSARIO_TENANT.md` | LOC | L2 Tenant | 1 por tenant | Owner+Admin del tenant |
| `LOC_GLOSARIO_VERTICAL_<vertical>.md` | LOC | L1 Vertical | 1 por vertical | FaberLoom system + tenant Owner extiende con DPA |
| `SCH_FB_VOICE_PROFILE_v1.md` | SCH | System | 1 global | FaberLoom (no editable por tenant) |
| `SCH_FB_WS_INSTRUCTIONS_v1.md` | SCH | System | 1 global | FaberLoom (no editable por tenant) |
| `POL_FB_VOICE_RESOLUTION_v1.md` | POL | System | 1 global | FaberLoom (no editable por tenant) |
| `SKILL_VOICE_HUMANIZER.md` | SKILL | System | 1 global | FaberLoom (no editable por tenant) |

## 13. Que cambia respecto a v1 (delta explicito)

| Aspecto v1 | v2 | Razon |
|---|---|---|
| 5 capas con precedencia jerarquica (Policies > Schema > Org > Dept > User > Recipient > Channel) | 1 voz (sabor user) modulada property-by-property por instrucciones workspace + ajuste transitorio | Decision CEO 2026-05-07: la voz REAL es del user que firma; el resto son constraints o instrucciones declarativas |
| Org/Dept/Channel/Recipient como voces | Reclasificadas: Org/Dept como knowledge constraints (POL_BANNED_PHRASES, LOC_GLOSARIO); Channel como parametro de renderizacion; Recipient como instrucciones declarativas del workspace | Voz es propiedad del firmante, no del receptor ni del canal |
| Onboarding via CSV upload de correos enviados | Diferido E3. E1 = configuracion explicita simple (saludo + firma + 2-3 ejemplos) | TIER1 #14 plan FB firmado: "Learning de muestras E3" |
| Voice como capability del @router | Voice como skill SYSTEM mandatory en cadena lineal del agente del workspace | Compatible TIER1 #15: cadena lineal de skills, no orquestacion |
| Conflictos resueltos por precedencia jerarquica | Conflictos resueltos por declaracion explicita: workspace gana donde declara; user pasa donde workspace no declara | Modelo property-level merge (CSS-like specificity) |

Lo que NO cambia de v1:
- Regla inquebrantable "voz cambia COMO no QUE"
- Voice Humanizer no es agente independiente
- Integracion con Context Pack Trace (Voice Overlay como source)
- Candidates de voz (3 tipos) sigue valido para flujo de promocion knowledge

## 14. Tensiones resueltas con canon previo

| Tension | Resolucion |
|---|---|
| TIER1 #14 plan FB: "Learning de muestras E3" vs onboarding via CSV de v1 | v2 difiere CSV upload a E3, alineado con plan firmado. E1 usa bootstrap simple |
| TIER1 #15: NO sub-agentes ni orquestacion | Voice Humanizer es skill terminal de cadena lineal, no agente. Gemini lo confirmo: "skill que modula a otro skill = pipe de transformacion de texto, no agente orquestado" |
| TIER1 #16 punto 2: skills sin tools externas | Voice Humanizer no requiere tools externas, opera sobre texto en memoria + knowledge L1-L4 del tenant via retrieval interno |
| TIER1 #16 punto 8: NO skills compartidas entre tenants | SKILL_VOICE_HUMANIZER es skill SYSTEM (provisto por FaberLoom platform); knowledge consumido es per-tenant. No viola la regla |
| Adapter pattern (vertical_spec_object) | LOC_GLOSARIO_VERTICAL es L1 read-only cross-tenant del mismo vertical. Knowledge compartido si, skill compartida no (lectura A confirmada en sesion 2026-05-07) |

## 15. Schema simplificado del input/output del skill

Input al skill voice_humanizer:
```yaml
voice_humanizer_input:
  draft_text: string                   # output del skill productor anterior
  channel: enum                        # email | whatsapp | sms | chat | tts
  signing_user_id: uuid                # quien firma (controlled_by del ws o override)
  workspace_id: uuid                   # de donde viene el output
  transient_instruction: string?       # ajuste one-off del operator (opcional)
  resolved_voice_pack:                 # pre-resuelto por voice_context_resolver
    saludo: string
    cierre: string
    firma: string
    tono: enum
    longitud: enum
    glosario_preferido: array<string>
    banned_phrases_user: array<string>
    banned_phrases_workspace: array<string>
    banned_phrases_tenant: array<string>
    workspace_overrides: object        # propiedades declaradas en LOC_INSTRUCCIONES_WS
```

Output del skill:
```yaml
voice_humanizer_output:
  text: string                         # draft humanizado, listo para Mesa
  resolution_trace:                    # property-by-property: que capa decidio cada propiedad
    saludo: source_layer                  # user | workspace | transient
    cierre: source_layer
    firma: source_layer
    tono: source_layer
    longitud: source_layer
  applied_transient: bool              # si hubo ajuste transitorio aplicado
  flags_to_user: array<string>         # ej: "Aplicado: tono mas formal por instruccion manual"
  banned_violations: array<violation>? # si hubo violaciones detectadas (severity > 0)
```

Schema completo en `SCH_FB_VOICE_PROFILE_v1` y `SCH_FB_WS_INSTRUCTIONS_v1`.

## 16. Que NO esta en este SPEC

- Implementacion runtime del voice_context_resolver (vive en `SPEC_ACTION_ENGINE`)
- Storage de voice profiles en DB (vive en `SPEC_FB_DATA_MODEL_v1`)
- Workflow detallado de promocion knowledge L4 -> L3 -> L2 (vive en `SPEC_FB_KNOWLEDGE_RIVER_v1`)
- Bootstrap detallado del sabor user (vive en `SPEC_FB_VOICE_BOOTSTRAP_v1` pendiente)
- Captura y procesamiento de signals HITL (vive en `POL_FB_VOICE_LEARNING_v1` pendiente)
- Loop feedback "instruccion no matiza" (diferido E2)

## 17. Decisiones CEO firmadas (sesion 2026-05-07)

| # | Decision |
|---|---|
| 1 | Una sola voz por user (sabor unico, no variantes formal/casual). Evoluciona con HITL |
| 2 | NO existe voz tenant como tono. Tenant aporta knowledge constraints (banned phrases, glosario) |
| 3 | Voz universal por canal por default. Channel es parametro de renderizacion |
| 4 | Estilo cliente del workspace = instrucciones declarativas explicitas del dueno (no auto-aprendido) |
| 5 | Solo el dueno del workspace edita instrucciones del workspace |
| 6 | Ajuste transitorio = comando libre del operator + flag visible al user |
| 7 | Ajuste transitorio aplica POST-generacion (sobre el draft producido), no afecta contenido factual |
| 8 | NO promocion automatica transitorio -> persistente. Control manual del dueno |
| 9 | Resolucion property-by-property. Workspace gana donde declara; user pasa donde no |
| 10 | Aprendizaje user solo desde edits Mesa (HITL). Captura "porque" via dropdown predefinido + libre opcional |
| 11 | NO override manual del user. Aprendizaje es implicito |
| 12 | Bootstrap E1 = opcion B (configuracion explicita simple). Analisis CSV diferido E3 |
| 13 | Loop feedback "instruccion no matiza" diferido E2 |

## 18. Changelog

- v2.1 (2026-06-10) ENMIENDA: alcance E1-E2 colapsado a bloque de estilo por tenant (SCH_FB_VOICE_PROFILE) + few-shot de gold samples aprobados + filtros tenant post-generacion. Resolucion property-by-property, LOC_INSTRUCCIONES_WS, ajustes transitorios y aprendizaje HITL de voz DIFERIDOS a E3+ con senal de activacion explicita. SCH_FB_WS_INSTRUCTIONS_v1 y POL_FB_VOICE_RESOLUTION_v1 pasan a DEFERRED. Secciones 2-17 se conservan integras como canon conceptual (Regla 3: no se borra contenido aprobado). Origen: revision arquitectura 2026-06-10.
- v2.0 (2026-05-07) VIGENTE: Refinacion modelo conceptual post-sesion CEO 2026-05-07 + iteracion Gemini sobre 11 preguntas. Cambia precedencia jerarquica de v1 a resolucion property-by-property. Reclasifica Org/Dept/Channel/Recipient como knowledge constraints o parametros de renderizacion, NO como voces independientes. Bootstrap E1 = configuracion explicita simple (CSV upload diferido E3). Aprendizaje implicito via HITL signals con tipificacion dropdown + libre opcional. Loop feedback "instruccion no matiza" diferido E2. v1 sigue VIGENTE en lo no contradictorio (regla inquebrantable, candidates, integracion @router conceptual).
- v1.0 (2026-05-02) VIGENTE: Canonizacion del Voice Profile / Humanizer Engine del mockup E1. 8 nodos + mini view + 3 candidates + Voice Overlay en trace.

## Stamp

VIGENTE 2026-05-07. Cierra modelo conceptual de Voice Humanizer para Foundation Beta E1. Listo para consumir por implementacion (PLB_ORCHESTRATOR + Sprint 1A). Schemas detallados en SCH_FB_VOICE_PROFILE_v1 + SCH_FB_WS_INSTRUCTIONS_v1. Politica resolucion en POL_FB_VOICE_RESOLUTION_v1. Pendientes proxima sesion: SPEC_FB_VOICE_BOOTSTRAP_v1 + POL_FB_VOICE_LEARNING_v1.
