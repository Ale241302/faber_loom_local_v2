# SPEC_FB_ROUTING_PRESETS -- Presets de ruteo y fabrica de presets (modelo Pedal Commander)

id: SPEC_FB_ROUTING_PRESETS
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (IDX_FB_FOUNDATION_BETA)
type: SPEC
stamp: DRAFT -- 2026-06-10 -- indexado a canonico via sync_fb_routing_indexa.ps1
aprobador: CEO (Alvaro) -- aprueba indexacion 2026-06-10
fuente: research web 2026-06-10 (OpenRouter presets/provider-routing/sovereign-AI, Microsoft Foundry model router, Portkey configs, LiteLLM tags) + sesion Cowork 2026-06-10
aplica_a: [FaberLoom, MWT]
relacionado: SPEC_FB_BUILD_SEQUENCE v2 - POL_DATA_CLASSIFICATION - ENT_FABERLOOM_PRICING_TIERS - ENT_GOB_PENDIENTES (Q7 tenant_model_allowlist) - SPEC_FB_ARCHETYPE (optimiza-vs-sugiere)
reemplaza: SPEC_FB_EVAL_ARENA_v1 como mecanismo de optimizacion (la arena queda archivada como referencia)

---

## 1. Concepto

Tres capas que componen, en jerarquia estricta:

```
ECU (envelope de seguridad)      = POL_DATA_CLASSIFICATION, fail-closed. NO configurable.
  > Preset del tenant (el pedal) = jurisdiccion + providers + curva + caps. Lo elige el Owner.
    > Curva del usuario          = modo eco/balanceado/sport dentro del preset. Lo elige cada usuario.
      > Auto-optimizador         = regla de promocion HITL elige default POR CLASE DE TAREA
                                   dentro del conjunto factible. Sugiere, no aplica.
```

Resolucion en runtime: `feasible = allowed_by_data_class(N) INTERSECT preset.providers INTERSECT curve.tiers` -> pick por task_class. Interseccion de listas, deterministico, <20ms, cada decision auditada con su razon.

## 2. Anatomia de un preset (schema)

Patron de la industria adoptado: preset como configuracion NOMBRADA y VERSIONADA, referenciable como si fuera un modelo (`@preset/ahorro-maximo`), separada del codigo, con rollback (OpenRouter). Vocabulario de provider preferences tomado del estandar de facto: allowlist/blocklist, sort, max_price, data_collection deny, ZDR.

```yaml
preset:
  slug: ahorro-maximo            # referenciable como @preset/ahorro-maximo
  version: 3                     # historial completo, rollback, cambio = evento auditado
  owner_locked: [envelope]       # secciones que solo Owner edita

  envelope:                      # decision de compliance -- SOLO Owner
    jurisdictions: [US, EU]      # o [US, EU, CN_selfhost] con cost-mode opt-in
    providers_allow: [anthropic, openai]      # allowlist explicita
    providers_deny: []                        # blocklist gana sobre allow
    data_collection: deny        # ZDR donde el provider lo ofrezca
    byo_keys: false              # E3+

  curve:                         # el "pedal" -- editable por usuario dentro del envelope
    mode: eco | balanceado | sport | sport_plus
    borderline_policy: cheap | premium
    # ESTE es el parametro que de verdad distingue modos (hallazgo industria):
    # las tareas claramente simples van baratas y las complejas van caras en TODOS los modos;
    # la diferencia es a donde va lo AMBIGUO. eco -> cheap. sport -> premium.

  task_overrides:                # por clase de tarea (patron tags LiteLLM)
    cotizacion: { default: sonnet, escalation: opus }
    cobranza:   { default: haiku,  escalation: sonnet }
    chat_kb:    { default: sonnet, escalation: opus }
    # los defaults aqui son los que la regla de promocion HITL propone actualizar

  caps:
    monthly_budget_usd: 150      # hard stop + alerta 80%
    max_cost_per_task_usd: 0.50
    max_latency_s: 12            # umbral suave: deprioriza, no excluye (patron OpenRouter)

  escalation:
    user_boost_button: true      # "rehacer con el mejor" -- el click es senal gratis
    boost_cap_per_day: 10
```

Merge en runtime: parametros del request hacen shallow-merge sobre el preset (patron OpenRouter). Validacion AL GUARDAR, no en runtime: un preset que viole el envelope de data-class no se puede salvar (ej: providers CN + ceiling N2 = error de lint, no excepcion en produccion).

## 3. Los 4 presets de casa (nivel 0 de la fabrica)

| Preset | Envelope | Curva | Para quien |
|---|---|---|---|
| Conservador | US/EU only, ZDR on | sport (borderline->premium) | regulado, primera impresion, default de onboarding |
| Balanceado | US/EU only | balanceado | default post-confianza; recomendado interactivo |
| Ahorro Maximo | US/EU + cost-mode CN_selfhost para N0-N1 | eco (borderline->cheap) | batch, back-office, sensible al precio |
| Sport+ | US/EU only | sport_plus (siempre el mejor, costo ignorado) | demos, tareas criticas, boost |

Curados y versionados por FaberLoom. El tenant arranca en Conservador (default seguro = decision ya firmada en PRICING_TIERS limitaciones v1.0).

## 4. La fabrica de presets (niveles 1-3)

**Nivel 1 -- Wizard de onboarding (3 preguntas, 0 knobs):**
1. "Tus datos pueden procesarse solo en US/EU, o tambien proveedores chinos/self-host para data no sensible?" -> envelope
2. "Que preferis: maxima calidad, balance, o maximo ahorro?" -> curve
3. "Presupuesto mensual de IA?" -> caps
El wizard COMPONE un preset desde la matriz envelope x curve x caps. El usuario nunca ve nombres de modelos. Anti-pattern prohibido: exponer model picker crudo o mas de ~7 campos.

**Nivel 2 -- Template por vertical:**
El vertical (safety_footwear, legal_practice...) aporta las task_classes y sus defaults razonables. El preset del tenant hereda del template del vertical via copy-on-create (plano, sin cascada -- coherente con la simplificacion de herencia ya acordada).

**Nivel 3 -- Presets derivados por datos (la fabrica continua):**
La regla de promocion HITL (N>=30 tareas de una clase, aprobacion-sin-edicion del modelo barato dentro de X pts del premium) NO toca el preset: genera una PROPUESTA de delta con evidencia adjunta:
> "En cobranza, haiku rindio 94% vs 96% de sonnet en 42 tareas. Cambiar el default ahorra ~$31/mes. [Aplicar] [Ignorar] [Shadow run 2 semanas]"
Owner aprueba -> nueva version del preset (auditada, reversible). Esto implementa optimiza-vs-sugiere de SPEC_FB_ARCHETYPE con HITL como fuente, sin arena.

**Nivel 4 -- Preset builder con IA (chat-first):**
El builder es un SKILL mas de FaberLoom (dogfooding del propio runtime). Patron: IA como compilador de lenguaje natural -> preset.

- **Modo creacion:** entrevista conversacional en vez de formulario. El agente pregunta por la operacion, detecta restricciones implicitas ("manejas datos financieros de clientes -> limita proveedores"; "tu volumen es batch -> eco sirve") y COMPONE el preset. El wizard nivel 1 queda como fallback no-conversacional.
- **Modo tuning:** "estoy gastando mucho en cobranza" -> el agente consulta savings ledger + stats HITL -> propone delta con evidencia. Es el nivel 3 invocable por el usuario, no solo batch semanal.
- **Backtest obligatorio antes de aprobar:** el agente simula el preset propuesto contra los ultimos 30 dias del ledger real del tenant (replay del calculo de costos, sin re-correr LLMs): "habrias gastado $X vs $Y; estas N tareas cambiarian de modelo; tu edit-rate historico en esa clase sube/baja Z pts". Convierte la aprobacion en decision con numeros. Costo de build: bajo (query + aritmetica sobre ledger).
- **Contrato de seguridad del builder:**
  1. Output estructurado contra el JSON schema del preset; pasa por el MISMO lint que una edicion manual; si viola envelope -> rechazo y retry del agente. La IA nunca aplica nada.
  2. Draft llega al Owner con el patron universal de 3 botones (aprobar/descartar/iterar).
  3. Relajar jurisdiccion o providers = paso de confirmacion explicito separado, nunca implicito en un "ok" general.
  4. Audit: `generated_by: ai_preset_builder`, `approved_by: owner`, prompt de origen y backtest adjuntos al evento.
- **Etapa:** el skill builder entra en E2 (necesita ledger con datos y el engine de skills ya vivo); el backtest en E2; la entrevista de onboarding para terceros en E3.

**Guardrails de la fabrica:**
- Lint de presets al guardar (envelope vs data-class, caps coherentes, providers existentes)
- Jurisdiccion y providers: SOLO Owner (firma el DPA). Curva y boost: por usuario. Nunca al reves.
- Cambio de preset = evento de audit con diff
- Maximo 1 preset custom activo por tenant en E3 inicial (evitar zoo de configs)

## 5. Que se construye cuando

| Etapa | Alcance |
|---|---|
| E1 | Schema completo + los 4 presets de casa. Anthropic-only: la curva degenera a haiku/sonnet/opus y el envelope es trivial -- pero el codigo del hook ya resuelve por interseccion, asi que E3 no rediseña nada. Savings ledger registra desde el dia 1. |
| E2 | task_overrides reales (cotizacion, cobranza) + boost button + primeras propuestas nivel 3 con datos HITL propios |
| E3 (condicional gate E2.5) | Wizard nivel 1 + template por vertical nivel 2 + multi-proveedor/multi-jurisdiccion real + cost-mode CN opt-in con consentimiento explicito |

## 6. Por que esto es vendible (y la arena no lo era)

El preset ES la interfaz comercial del diferenciador "tiers de confidencialidad + cost-mode" de PRICING_TIERS: se demuestra en 30 segundos en una llamada ("elegi donde pueden procesar tus datos y cuanto queres gastar; el sistema optimiza adentro de eso y te muestra el ahorro"). Mapea ademas a la practica estandar de la industria (OpenRouter presets/sovereign-AI, Portkey workspaces+residency, Foundry router cost-aware), o sea: comprable sin fe.

---

Changelog:
- v1.0 (2026-06-10): Creacion. 3 capas (ECU/preset/curva) + auto-optimizador HITL. Schema YAML, 4 presets de casa, fabrica niveles 1-4 (nivel 4 = preset builder con IA chat-first + backtest contra ledger), guardrails, fases E1-E3. Reemplaza SPEC_FB_EVAL_ARENA como mecanismo de optimizacion. ASCII puro.
