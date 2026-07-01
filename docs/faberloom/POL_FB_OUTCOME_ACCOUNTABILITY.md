# POL_FB_OUTCOME_ACCOUNTABILITY — Regla P15 Outcome Accountability en FaberLoom
id: POL_FB_OUTCOME_ACCOUNTABILITY
version: 2.0
status: VIGENTE
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: POL
stamp: VIGENTE — 2026-04-29f (re-scope FB)
aprobador: CEO (sesión Cowork 2026-04-29 + re-scoping 2026-04-29f)
aplica_a: [FaberLoom]
relacionado: ARCH_AGENT_PRINCIPLES.md (extensión P15) · SCH_FB_SKILL_MANIFEST_v2.md · SPEC_FB_AGENT_BUILDER_v1.md · SPEC_AUTONOMY_CONTROL_ENGINE.md

---

## Declaración de la regla

> **P15 — Outcome Accountability.** Todo agente vivo en producción declara y mide su outcome metric primaria. Sin outcome trending observable a 90 días, el agente vuelve a SHADOW para revisión. Producir output sin impacto medible es falsa productividad y cuesta tokens reales.

Esta regla extiende los principios fundacionales (P0-P14) declarados en ARCH_AGENT_PRINCIPLES y se considera **inquebrantable** desde su aprobación.

---

## Contexto: la trampa de la falsa productividad

Derivado del framework de Xavier Mitjana sobre "trampa de productividad con IA" (visualizado en sesión Cowork 2026-04-29). La distinción central:

- **Actividad** ≠ **Impacto**.
- Un agente puede generar 200 runs/día consumiendo $25 en tokens sin producir un solo activo reutilizable, decisión cerrada, ni aprendizaje validado.
- Métricas L0-L1 (runs, tokens, cost) son higiene operacional. NO son evidencia de valor.
- Solo la métrica L5 (outcome de negocio) justifica seguir gastando tokens.

Esta política asegura que ningún agente MWT sobreviva en producción sin justificación económica trazable.

---

## Aplicación operacional

### A. Declaración obligatoria en manifest

Todo SKILL_ con `archetype` en `[skill, workflow, reactive, autonomous, supervisor, routine]` y `status` distinto de `ARCHIVED` declara en su manifest v2 (ver SCH_SKILL_MANIFEST_V2):

```yaml
metadata:
  mwt:
    outcome:
      primary: <métrica de negocio observable>
      baseline_value: <valor pre-agente, [PENDIENTE — NO INVENTAR]>
      target_at_60d: <objetivo cuantificable>
      secondary: [...]
      measurement_cadence: weekly | monthly
```

Sin estos campos, el manifest no compila (validación 6 de SCH_SKILL_MANIFEST_V2).

### B. Tipos de outcome aceptables

Una métrica primaria califica como outcome legítimo si cumple las cuatro condiciones:

| # | Condición | Ejemplo válido | Ejemplo inválido |
|---|-----------|----------------|------------------|
| 1 | Es observable sin agente | TTR review en horas | "número de drafts producidos" |
| 2 | Tiene baseline pre-agente | TTR manual: 28h | "primera vez que medimos esto" |
| 3 | Mueve un KPI de negocio downstream | conversion lift, AHR delta, ticket close time | "tokens consumidos" |
| 4 | Es atribuible al agente con counterfactual razonable | A/B con muestra control | "el negocio creció pero no sabemos si fue el agente" |

Métricas que NO califican (vanity metrics):
- runs/día, tokens/run, API calls
- número de prompts shipped
- "time-saved-claimed-by-AI" sin evidencia
- conversaciones sostenidas
- número de drafts generados (sin seguimiento de uso downstream)

### C. Cadencia de revisión

Por defecto:
- **Día 1 a 30 (SHADOW)**: revisión semanal CEO. Métrica primaria se trackea pero no se evalúa para promoción.
- **Día 31 a 90 (post-graduación a nivel 3)**: revisión mensual CEO. Outcome trending debe mostrar progreso hacia target_at_60d.
- **Día 90+ (estable)**: revisión trimestral. Si outcome estancado o degradante, kill switch activo.

### D. Kill switch automático

El runtime activa kill switch (vuelve agente a SHADOW) cuando se cumple cualquiera:

| Trigger | Definición |
|---------|------------|
| `outcome_no_progress_days: 90` | Métrica primaria sin movimiento positivo en 90 días calendario |
| `outcome_regression_pp: 15` | Métrica primaria empeoró ≥15 puntos porcentuales vs baseline en 30 días |
| `cost_overrun_count: 3` | 3 superaciones de `budget.hard_cap_usd` en 7 días |
| `acceptance_rate_drop_pp: 10` | Acceptance rate cayó ≥10pp en 7 días |

Cuando dispara:
1. SKILL_ pasa de ACTIVE a SHADOW automáticamente
2. Notificación al CEO (canal por definir, default email)
3. Output del agente queda en log, no se publica
4. Manifest queda DRAFT pendiente de revisión

---

## Validación cruzada con principios fundacionales

P15 se complementa con principios existentes:

| Principio existente | Cómo se conecta |
|---------------------|-----------------|
| P3 Draft-first absoluto | outcome se mide a partir del momento en que CEO acepta drafts → sin acceptance no hay outcome |
| P4 Autonomía por evidencia | outcome trending positivo es uno de los criterios de promotion (junto con acceptance, schema, cost) |
| P5 Aprendizaje con gate humano | propuestas de patches al manifest derivadas de outcome data requieren firma CEO antes de aplicar |
| P9 Gobernanza embebida | el kill switch es policy ejecutable, no declarativa |
| P14 Deterministic First | medición de outcome usa parsers/queries deterministas, no LLM evaluation |

P15 NO redefine ninguno; agrega la dimensión de impacto económico que no estaba explícita.

---

## Anti-patterns prohibidos

Los siguientes patrones violan la regla y causan rechazo en validación:

| Anti-pattern | Por qué viola |
|--------------|---------------|
| `outcome.primary: tokens_consumed` | métrica de costo no de impacto |
| `outcome.primary: runs_per_day` | actividad pura |
| `outcome.primary: drafts_generated` | output sin medir uso |
| `outcome.primary: ceo_satisfaction` | no observable, no atribuible counterfactualmente |
| Kill switch `enabled: false` | regla inquebrantable, no opt-out |
| `outcome_no_progress_days > 90` | si está estancado 3 meses, vuelve a SHADOW sí o sí |
| Falta `baseline_value` declarado | sin baseline no hay counterfactual posible |

---

## Heurísticas para CEO al elegir outcome

Cuando declaras outcome de un nuevo SKILL_:

1. **Pregunta**: si este agente desaparece, ¿cuál métrica empeora primero?
2. **Verifica**: ¿puedo medirla sin acceso al agente (en otro sistema o manualmente)?
3. **Cuantifica**: ¿cuál es su valor hoy? Si no lo sé, [PENDIENTE — NO INVENTAR].
4. **Estima**: ¿cuánto debe moverse en 60 días para justificar el costo?
5. **Compromiso**: si no se mueve, ¿estoy dispuesto a apagar el agente?

Si la respuesta a #5 es no, la outcome metric elegida no es la real. Reelegir.

---

## Cómo se aplica retrospectivamente

Los 10 SKILLs en SHADOW actuales no tienen outcome declarado en frontmatter. P15 NO los retira automáticamente — quedan en SHADOW que es estado válido. Pero al migrar al manifest v2, deben declarar outcome o no compilan.

Plan:
- SKILL_RW_REVIEW_TRIAGE migra primero (Fase 1 SPEC_AGENT_BUILDER_MWT_V1) con outcome declarado por CEO
- Resto de SKILLs migran progresivamente, cada uno con su outcome
- Hasta migración, SKILL legacy sin outcome NO puede pasar de SHADOW a ACTIVE

---

## Métricas de salud de la propia regla

Para evitar que P15 se vuelva burocracia:

| Indicador | Threshold saludable |
|-----------|---------------------|
| % de SKILLs ACTIVE con outcome trending positivo a 60 días | > 80% |
| % de SKILLs que fueron a SHADOW por kill switch outcome | < 10% por trimestre |
| Tiempo CEO en revisión semanal | < 30 min |
| Falsos positivos kill switch (volvió y resultó estar bien) | < 5% |

Si la regla genera muchos falsos positivos o consume demasiado tiempo del admin del tenant, ajustar thresholds en `SCH_FB_SKILL_MANIFEST_v2` sin tocar la regla.

---

Stamp: VIGENTE — 2026-04-29f (re-scope FB)

Changelog:
- v1.0 (2026-04-29): creación con scope cross [MWT, FaberLoom]. Regla P15 formalizada. Aplicación obligatoria en manifest v2 (validación 6). 4 condiciones para outcome legítimo. 4 triggers de kill switch automático. Conexión con P3/P4/P5/P9/P14. Anti-patterns prohibidos. Heurísticas CEO. Plan retrospectivo para 10 SKILLs SHADOW del primer tenant.
- **v2.0 (2026-04-29f): re-scope completo a FaberLoom. Renombrado POL_OUTCOME_ACCOUNTABILITY → POL_FB_OUTCOME_ACCOUNTABILITY. La regla aplica a todos los agentes en la plataforma FB, sin importar tenant. Aprobador: CEO sesión re-scoping 2026-04-29f.**
