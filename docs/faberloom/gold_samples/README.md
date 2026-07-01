# Gold Samples — Norte de Calidad para Agentes MWT

Este directorio contiene **gold samples**: ejemplos de output ideales que sirven como:
1. **Few-shot context** inyectado al LLM en hook `pre_llm_call`
2. **Reference de calidad** para CEO al revisar outputs en dashboard
3. **Regression test fixtures** para evaluar drift de calidad post-graduación

Ver `SCH_SKILL_MANIFEST_V2.md` v1.1 sección `metadata.mwt.golden_samples` para el contrato declarativo.

## Convención de naming

`<dominio>_<caso>_<fecha>.md`

Ejemplos:
- `review_response_2026_03.md` — caso de respuesta a review 4-star del Q1 2026
- `review_escalation_2026_02.md` — caso de escalación a CEO por review crítica
- `proforma_marluvas_broker_2026_04.md` — caso de proforma broker con descuento volumen

## Estructura de cada gold sample

Cada archivo sigue el mismo template:

```markdown
---
id: GS_<DOMINIO>_<CASO>_<FECHA>
validates_outputs: [<output_id>, ...]
evaluation_use: reference | regression_test | few_shot
added_by: ceo
added_at: YYYY-MM-DD
context_summary: "Una línea sobre el caso"
---

## Input (cómo se le presentó al agente)

[Texto del input real, anonimizado si es necesario]

## Output ideal (lo que el agente debió generar)

[Texto del output que validó CEO como gold]

## Contexto adicional

[Por qué este caso es ejemplar — qué hizo bien, qué evitó, decisión clave]

## Métricas de outcome

[Qué métrica downstream se movió y cuánto, si se sabe]
```

## Política

- **Solo CEO popula los gold samples.** Validación 18 de SCH_SKILL_MANIFEST_V2 verifica que el path existe; CEO los crea con casos reales.
- **Anonimización obligatoria.** PII de clientes B2B (nombres, emails, datos sensibles) se reemplaza con placeholders consistentes (`<CLIENTE_A>`, `<EMAIL_A>`).
- **Update gradual.** Cuando el agente genera un output excelente y CEO lo valida, puede convertirse en gold sample futuro vía propuesta del meta-agente reflection (futuro Capa 3 aprendizaje).
- **Versionado implícito.** Si un gold sample queda obsoleto (cambio de POL_BRAND_VOICE, nueva regla compliance), se marca `evaluation_use: deprecated` en su frontmatter, no se borra. Trazabilidad histórica.

## Estado actual

Todos los gold samples están **[PENDIENTE — CEO popular]** hasta tener casos reales validados. Los placeholders en este directorio sirven solo para:
- Hacer pasar la validación 18 del compiler durante development
- Documentar el contrato esperado

Cuando empiece Fase 3 SHADOW del SPEC_AGENT_BUILDER_MWT_V1, cada SKILL graduado debe tener al menos 1 gold sample real por output `kind: asset` antes de pasar a ACTIVE.

## Templates esperados (a popular)

Para arrancar la Fase 1 sin bloquear validaciones:

| Archivo | Para qué SKILL | Output validado | Estado |
|---------|----------------|-----------------|--------|
| `review_response_2026_03.md` | SKILL_RW_REVIEW_TRIAGE | response_draft | [PENDIENTE — CEO] |
| `review_escalation_2026_02.md` | SKILL_RW_REVIEW_TRIAGE | escalation_ticket | [PENDIENTE — CEO] |
| `listing_optimizer_es_mx_2026.md` | SKILL_RW_LISTING_OPT | listing_text | [PENDIENTE — CEO] |
| `proforma_broker_2026_04.md` | SKILL_PROFORMA_BUILDER | proforma_html | [PENDIENTE — CEO] |
| `lead_qualified_b2b_2026.md` | SKILL_B2B_LEAD_QUALIFIER | qualification_score, draft_email | [PENDIENTE — CEO] |
| `audit_report_canonical.md` | SKILL_KB_AUDITOR | audit_report | [PENDIENTE — CEO] |

Estos placeholders están escritos en este directorio con frontmatter completo y body `[PENDIENTE — NO INVENTAR]` para no inventar casos. CEO los completa con casos reales cuando arranca cada SKILL.
