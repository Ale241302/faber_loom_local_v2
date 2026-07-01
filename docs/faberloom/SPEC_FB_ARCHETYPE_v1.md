---
id: SPEC_FB_ARCHETYPE
version: 1.1
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
tipo: spec
last_review: 2026-06-10
stamp: DRAFT -- 2026-06-10 -- v1.1 simplifica Dimension 2 (herencia plana copy-on-create; cascada DIFERIDA)
aplica_a: [FaberLoom, MWT]
---

# SPEC_FB_ARCHETYPE -- El Arquetipo como Unidad Central de Trabajo

> Concepto unificador. Hoy el mismo objeto vive disperso en 4 nombres:
> archetype (AG_AM), template (Knowledge River), Working Profile y "ruta" de routing.
> Este SPEC declara el ARQUETIPO como la unidad canonica que los empaqueta, con sus
> 4 dimensiones: estructura, herencia, evolucion y clasificacion dinamica.
> Origen: sesion de arquitectura funcional Cowork 2026-06-02.

## A. Definicion

Un **arquetipo** es la plantilla reutilizable de "como se hace un tipo de trabajo".
Es la unidad central de FaberLoom (el Knowledge River ya lo insinua: "la unidad central
es el template"). Cada workspace, agente o skill instancia un arquetipo, lo hereda, lo
especializa y lo afina con el uso.

Reconcilia (no reemplaza, unifica vistas de):
- `archetype` AG_AM / AG_AM_MWT (SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT) -- la plantilla de agente.
- `template` (SPEC_FB_KNOWLEDGE_RIVER) -- el activo organizacional reutilizable.
- Working Profile -- como trabaja un objeto (herencia de config + routing override).
- la "ruta" por tipo de informacion (SPEC_FB_EVAL_ARENA) -- una de sus facetas.

## B. Dimension 1 -- Estructura (6 facetas)

Un arquetipo empaqueta 6 facetas. La "ruta" de routing es UNA, no el todo.

| Faceta | Que define | Pieza KB |
|---|---|---|
| Tipo de informacion | que maneja (RFQ, consulta, email) | 6 clases de info |
| Ruta / workflow | que secuencia de pasos (de las 5 rutas) | workflow engine |
| Working Profile | que IAs / tier / umbral (la ruta de routing) | routing override + SPEC_FB_EVAL_ARENA |
| Conocimiento | que fuentes L0 consulta | Knowledge River L0 |
| Schema de salida | que produce | SCH_ |
| Voz / formato | como lo dice | Voice Humanizer |

## C. Dimension 2 -- Herencia (SIMPLIFICADA v1.1: copy-on-create plano)

```
ARQUETIPO (template general)        ej: "cotizacion B2B", "consulta operativa"
   -> instancia                     copy-on-create por tenant/workspace
                                    (config propia COMPLETA, plana, editable, sin enlace vivo al template)
```

**Modelo vigente (hasta >=10 tenants o dolor medido):**
- Dos niveles: template -> instancia. La instancia nace como COPIA completa del template y de ahi en adelante es independiente. Sin resolucion en cascada, sin merge por capas, sin scopes intermedios. Que config aplica = leer UN registro. Debuggeable con un SELECT.
- Cambios al template NO se propagan a instancias existentes (se ofrece "re-sincronizar" manual con diff, gate humano).
- Lo unico que se conserva del modelo en capas desde el dia 1, porque es seguridad y no conveniencia:
  - **Override solo endurece, nunca relaja** seguridad/egress. Preferencias (modelo/umbral/voz) se ajustan en ambas direcciones dentro del ceiling.
  - **model_access = interseccion** (instancia AND tenant AND data-class). Implementado como check de allow-list en el router (SPEC_FB_ROUTING_PRESETS capa ECU/preset), no como cascada de config.

**DIFERIDO (diseno de referencia, NO implementar):** la cascada Global > Org > Team > Workspace > Agente > Key > Request y las 3 capas sealed_base + learned_overlay + manual_overlay quedan documentadas como evolucion para escala. Senal de activacion: >=10 tenants Y casos reales donde la copia plana duplica mantenimiento doloroso (mismo fix manual en >3 instancias). Hasta esa senal, las cascadas de config son donde mueren los multi-tenant: complejidad presente contra beneficio hipotetico.

## D. Dimension 3 -- Evolucion (optimiza o sugiere, por impacto)

El arquetipo es semilla, no jaula: se define inicial y el aprendizaje lo afina. Que el
cambio se auto-aplique o se proponga lo decide el IMPACTO (3 niveles del Knowledge River):

| Impacto del cambio | Accion | Ejemplo | Nivel KR |
|---|---|---|---|
| Bajo / reversible | OPTIMIZA solo (auto, avisa en dashboard) | re-rank gold samples, refresh chunks, budget dinamico | L1 auto |
| Medio | SUGIERE (1 click curador + diff) | cambiar modelo de un tier, nuevo gold sample, ajuste de prompt | L2 firma rapida |
| Alto | SUGIERE con justificacion (2 reviewers + auto-SHADOW 30d) | cambiar ruta, autonomy level, sub-agentes, el arquetipo mismo, ARCH/POL | L3 critico |

Reglas de la evolucion:
- **La sugerencia trae evidencia, no corazonada.** La arena + savings ledger producen la prueba: "en los ultimos 200 casos, modelo X iguala calidad a -60% costo. Cambio? [aprobar/iterar/descartar]".
- **Gate anti-ruido.** Solo sugiere con muestra suficiente + mejora consistente (min_samples del gate). Sin esto, el curador se ahoga en sugerencias triviales y deja de leerlas.
- Lo aprobado se vuelve el nuevo base del arquetipo; lo bueno sube al pool (L3->L4 firmado) y mejora a todos los que heredan.

## E. Dimension 4 -- Clasificacion dinamica (que arquetipo es una consulta)

La ruta es dinamica porque la consulta se clasifica a un arquetipo en runtime, no la
elige el usuario cada vez. Dos preguntas distintas:

### E.1 Runtime: clasificar UNA consulta (capas, de barato/confiable a caro)

| Capa | Quien clasifica | Costo | Cuando |
|---|---|---|---|
| 1. Canal / contexto | el origen ya lo dice (webhook B2B -> cotizacion; upload PDF -> extraccion) | gratis | siempre primero |
| 2. Reglas explicitas | metadata, keywords, hay adjunto?, que tenant? | gratis | lo que el canal no resuelve |
| 3. Clasificador semantico (L1) | embeddings / modelo chico, <20ms | bajo | lo ambiguo |
| 4. Fallback | confianza baja -> pregunta al usuario o cae a arquetipo default seguro | - | solo si 1-3 no deciden |

### E.2 El catalogo de arquetipos (que tipos existen)

- Semilla: el humano/curador define los arquetipos iniciales.
- Descubrimiento: cuando aparece un cluster de consultas que no encaja en ningun arquetipo (huerfanas), el sistema SUGIERE crear uno nuevo, con evidencia. Gate humano (mismo "sugiere" de la Dimension 3).

### E.3 REGLA INQUEBRANTABLE -- tier se adivina, sensibilidad NO

- El **tier funcional** (simple / cotizacion / reasoning) SI puede clasificarse semanticamente; si se equivoca, el costo es suboptimo y recuperable.
- La **sensibilidad del dato** (PUBLIC / PARTNER_B2B / INTERNAL / CEO-ONLY) NUNCA se adivina. Se hereda del canal, el tenant y la metadata -- fuente deterministica, fail-closed a INTERNAL si no se sabe.
- El clasificador propone el arquetipo funcional; la sensibilidad la fija el contexto, no el modelo. El router ya las separa: la sensibilidad recorta la allow-list ANTES que el tier. Adivinar la sensibilidad = agujero de egress.

## F. Quien define -- resumen

```
arquetipo de UNA consulta  -> lo asigna el CLASIFICADOR (canal->reglas->semantico), auto
sensibilidad de la consulta -> la fija el CONTEXTO (canal/tenant/metadata), nunca se adivina
catalogo de arquetipos      -> lo posee el HUMANO/curador (gate); el aprendizaje PROPONE altas
afinado del arquetipo       -> AUTO si es seguro (L1), SUGIERE si cambia el catalogo (L2/L3)
```

## G. Relacion con otros docs

- Unifica: SPEC_FB_VERTICAL_ACCOUNT_MANAGEMENT (archetype), SPEC_FB_KNOWLEDGE_RIVER (template + 5 capas + 3 niveles aprendizaje), SPEC_FB_SKILL_COMPOSITION (3 capas overlay), SPEC_FB_EVAL_ARENA (ruta/routing + arena + savings), SPEC_LLM_ROUTING_ARCHITECTURE (L1 Clasificador), ENT_PLAT_LLM_ROUTING, POL_DATA_CLASSIFICATION (egress fail-closed).
- Candidato a Fase 0 del SPEC_FB_EVOLUTION_ROADMAP (consolidacion pre-codigo): unificar los 4 nombres bajo "arquetipo" antes de implementar.

## H. En el roadmap

| Dimension | Fase |
|---|---|
| Estructura (definir arquetipo semilla, manual) | F1-F2 |
| Herencia (copy-on-create plano) | F2; cascada + learned overlay DIFERIDOS (senal: >=10 tenants + dolor medido) |
| Evolucion (optimiza/sugiere) | F4 (necesita volumen + arena de F3) |
| Clasificacion: canal + reglas | F1 |
| Clasificacion: semantica + descubrimiento de arquetipos | F3-F4 |

## I. Reglas inquebrantables

1. El arquetipo es la unidad central; ruta, working profile, schema y voz son sus facetas, no objetos independientes.
2. Override solo endurece seguridad/egress, nunca relaja.
3. La sugerencia de cambio trae evidencia medida (arena/savings) + muestra suficiente; nunca corazonada ni ruido.
4. tier se clasifica dinamico; sensibilidad se hereda del contexto, fail-closed. Nunca adivinar sensibilidad.
5. Lo bueno aprendido por un objeto se promueve al pool para mejorar el general (no re-aprender aislado).

---

Changelog:
- v1.1 (2026-06-10): Dimension 2 simplificada a copy-on-create plano (template -> instancia independiente, re-sync manual con diff). Cascada de 7 scopes y 3 capas sealed/learned/manual reclasificadas como DIFERIDO con senal de activacion explicita (>=10 tenants + dolor de mantenimiento medido). Se conservan como vigentes desde dia 1 solo las reglas de seguridad: override-solo-endurece y model_access por interseccion (implementadas en el router, no como cascada). Alineado con SPEC_FB_ROUTING_PRESETS v1 (copy-on-create nivel 2 de la fabrica) y revision de arquitectura 2026-06-10. No se borra contenido: la cascada queda como diseno de referencia.
- v1.0 (2026-06-02): Creacion. Concepto unificador "arquetipo" con 4 dimensiones (estructura
  6 facetas + herencia template->clon->overlay + evolucion optimiza/sugiere por impacto +
  clasificacion dinamica con regla tier-vs-sensibilidad). Reconcilia archetype + template +
  working profile + routing. Origen: sesion de arquitectura funcional Cowork 2026-06-02.
  DRAFT en generated_staging, pendiente promocion via sync + indexacion en
  IDX_ARQUITECTURA_FUNDACIONAL + MANIFIESTO. No edita los specs reconciliados (los referencia).
  ASCII puro.
