# SCH_AI_GOV_DUAL_REVIEW_OUTPUT — Schema del Veredicto Final del Dual Review
id: SCH_AI_GOV_DUAL_REVIEW_OUTPUT
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SCH
subfamilia: AI_GOV
stamp: VIGENTE — 2026-05-01
aprobador: CEO
aplica_a: [MWT, FaberLoom]
requires: PLB_AI_GOV_DUAL_REVIEW (consumidor primario)
policies: [POL_AI_GOV_FINAL_OUTPUT_QUALITY, POL_DETERMINISMO]
inherits: ninguno

---

## Proposito

Define la estructura obligatoria del output del Sintetizador en el flujo PLB_AI_GOV_DUAL_REVIEW. Sin este schema, el veredicto puede ser largo, ambiguo, o inutilizable para el decisor — lo que mata el valor del flujo.

El schema garantiza que el veredicto sea: **corto, accionable, verificable, registrable**.

---

## Estructura obligatoria (markdown)

El sintetizador DEBE producir output en este formato exacto:

```markdown
# Resultado de revision cruzada: <problem_id>

## Veredicto
**APROBAR** | **APROBAR CON CAMBIOS** | **RECHAZAR**

(una sola palabra clave en mayusculas + negrita)

## Justificacion del veredicto
2-4 lineas explicando por que el veredicto es ese y no otro.
Si es "RECHAZAR" o "APROBAR CON CAMBIOS", referenciar los hallazgos
P0/P1 que disparan la decision.

## Hallazgos criticos
### P0 (bloqueantes — deben resolverse antes de implementar)
- <hallazgo concreto> — <fix recomendado> — origen: <auditor o sintesis>
- ...

### P1 (alta — deben resolverse o aceptarse explicitamente)
- ...

### P2 (media — pueden aceptarse como deuda tecnica documentada)
- ...

(si una severidad esta vacia: "ninguno". NO inventar para llenar.)

## Cambios obligatorios antes de implementar
Lista numerada de acciones concretas. Cada item debe ser ejecutable
sin ambiguedad. Si no hay cambios obligatorios, escribir "ninguno".

1. <accion concreta>
2. <accion concreta>
...

## Plan final recomendado
Pasos numerados del plan consolidado (proposal del Proponente
+ cambios obligatorios integrados).

1. <paso>
2. <paso>
...

## Tests requeridos

### Unit tests
- <test>

### Contract tests
- <test>

### Integration tests
- <test>

### Regression tests
- <test>

(si una categoria no aplica: "no aplica" + razon en 1 linea)

## Rollback
Pasos exactos para revertir si el cambio falla en produccion.

1. <paso>
2. <paso>
...

## Decisiones abiertas
Items que el sintetizador NO pudo resolver y requieren decision humana.

- <decision pendiente> — <quien debe decidir> — <fecha sugerida>
...

(si no hay: "ninguna")

## Metadata
- problem_id: <id>
- decision_severity: P0 | P1 | P2
- data_classification: N0 | N1 | N2 | N3 | N4
- modelos_usados:
  - proponente: <model_id> (familia: <familia>)
  - auditor:    <model_id> (familia: <familia>)
  - sintetizador: <model_id> (familia: <familia>)
- familias_distintas_verificado: true | false  (debe ser true; si false = bug)
- token_ledger_parent_request_id: <uuid>
- costo_total_usd: <float>
- duracion_minutos: <int>
- timestamp_completado: <ISO 8601>
```

---

## Reglas de validacion

1. **Veredicto unico.** Una sola palabra clave: "APROBAR", "APROBAR CON CAMBIOS", "RECHAZAR". Cualquier variacion ("aprobar parcialmente", "depende", etc.) = output invalido.

2. **Veredicto APROBAR no compatible con P0 sin resolucion.** Si la seccion P0 no esta vacia, el veredicto NO PUEDE ser "APROBAR". Minimo "APROBAR CON CAMBIOS" o "RECHAZAR". Validacion automatica.

3. **Familias distintas obligatorio.** Si `familias_distintas_verificado: false`, el output del flujo se descarta. Bug del orquestador (manual o automatico).

4. **Cada hallazgo P0/P1 debe tener fix recomendado.** Hallazgo sin fix = output invalido. P2 puede no tener fix (deuda tecnica aceptada).

5. **Cambios obligatorios deben coincidir con P0 + P1 aceptados.** Si auditor encontro 5 P0 y sintetizador acepta 3, los 3 deben aparecer en "Cambios obligatorios". Discrepancia = output invalido.

6. **Plan final debe ser ejecutable.** Pasos genericos como "implementar feature" sin detalle = output invalido. Cada paso debe ser accion concreta sobre archivo, sistema, o componente identificable.

7. **Tests requeridos no pueden estar todos como "no aplica".** Al menos una categoria debe tener tests reales. Excepcion documentada: cambios puramente declarativos (markdown KB) — pero incluso ahi debe haber regression test (linter, headers, refs).

8. **Rollback debe ser ejecutable.** "Revertir el commit" es valido si el cambio es atomico. Para cambios con migracion DB, side effects, o data loss: pasos detallados obligatorios.

9. **Decisiones abiertas no pueden mascarar P0.** Si el sintetizador "abre" un P0 como decision pendiente, el veredicto debe ser "RECHAZAR" o "APROBAR CON CAMBIOS" + el P0 listado. NO se aprueba dejando P0 abiertos.

10. **Metadata completa.** Los 9 campos de metadata son obligatorios. Faltante = output invalido.

---

## Anti-patrones del veredicto

| Anti-patron | Por que falla |
|---|---|
| **Veredicto "APROBAR" con 3 P0 listados** | El veredicto contradice los hallazgos. Decisor confundido. |
| **"Plan final recomendado" copiado del proposal sin integrar audit** | Sintetizador no sintetizo, solo concateno. Output sin valor agregado. |
| **Tests todos como "no aplica"** | Cambio sin tests = riesgo no mitigado. Veredicto invalido. |
| **Rollback "revertir si falla"** | No es plan, es deseo. Necesita pasos. |
| **Decisiones abiertas con 10+ items** | El flujo no resolvio nada. Re-armar problem_brief upstream. |
| **Hallazgos P0 con fix "considerar alternativa"** | "Considerar" no es fix. Necesita accion. |
| **Justificacion del veredicto en 1 linea** | Sin justificacion suficiente, el decisor no puede actuar con confianza. Minimo 2-4 lineas. |

---

## Para que sirve este schema mas alla del PLB

1. **Auditoria retrospectiva:** veredictos preservados en `docs/dual_reviews/` permiten revisar cada trimestre cuales decisiones P0 efectivamente evitaron incidentes en produccion vs cuales fueron sobre-revisadas.

2. **Few-shot pool:** veredictos clean (sintetizador acerto + decisor implemento sin re-trabajo) son candidatos a entrar al `ENT_AI_GOV_GOLDEN_CORPUS_MWT` como ejemplo del task_type "dual_review_synthesis".

3. **Pin candidates:** si una combinacion modelo proponente + modelo auditor + modelo sintetizador produce veredictos consistentemente clean en un task_type especifico, el sintetizador puede ser pineado en `ENT_AI_GOV_OUTPUT_PINS` como receta canonica para esa categoria de decision.

4. **Telemetria:** los campos de metadata permiten analisis trimestral del flujo (cuales pares de familias funcionan mejor, costos por categoria, distribucion de veredictos).

---

## Lo que esto NO es

- No es un schema de proposal o de audit (esos son outputs intermedios sin schema canonico — viven solo durante el flujo).
- No es un schema de PR / commit (eso lo cubre POL_CHANGELOG).
- No es archivo historico (cada veredicto es un archivo separado en `docs/dual_reviews/` siguiendo este schema).

---

Changelog:
- v1.0 (2026-05-01): Creacion. Schema markdown estricto del veredicto del Sintetizador. 10 reglas de validacion. 7 anti-patrones documentados. 4 usos secundarios (auditoria retrospectiva, few-shot pool, pin candidates, telemetria). Origen: sesion AI_GOV dual review 2026-05-01.
