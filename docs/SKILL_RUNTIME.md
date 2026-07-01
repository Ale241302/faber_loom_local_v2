# SKILL_RUNTIME — Dashboard de Estado de Skills
id: SKILL_RUNTIME
version: 1.0
status: VIGENTE
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
type: SCH
stamp: VIGENTE — 2026-04-16
aplica_a: [SHARED]

---

## Propósito

Dashboard único de estado operativo para todos los skills MWT.
Este archivo es la capa **AgentRuntime** del sistema — registra qué está pasando con cada skill en tiempo real.
No es AgentSpec (eso vive en `SKILL_*.md`) ni AgentMemory (eso vive en `SKILL_MEM_*.md`).

**Actualizar después de cada ejecución de skill.** Puede actualizarse manualmente o via n8n hook.

---

## Estado de Skills — Tabla Principal

| Skill | Trigger | Estado | Autonomía actual | Última ejecución | Approval rate | Temp. aprendizaje | Memoria |
|-------|---------|--------|-----------------|-----------------|---------------|-------------------|---------|
| SKILL_AMAZON_OPS | `amazon-ops` | SHADOW | PROPONE | — | — | 🔵 | — |
| SKILL_CLIENT_SERVICE | `client-service` | SHADOW | PROPONE | — | — | 🔵 | — |
| SKILL_COMPLIANCE_CHECKER | `compliance-check` | SHADOW | PROPONE | — | — | 🔵 | — |
| SKILL_COPY | `copy` | SHADOW | PROPONE | — | — | 🔵 | — |
| SKILL_DEMAND_FORECASTER | `demand-forecast` | SHADOW | PROPONE | — | — | 🔵 | — |
| SKILL_EXPERIMENT_RUNNER | `experiment` | SHADOW | PROPONE | — | — | 🔵 | — |
| SKILL_HUMANIZE_BRAND | `humanize-brand` | SHADOW | PROPONE | — | — | 🔵 | — |
| SKILL_HUMANIZE_COMMS | `humanize-comms` | SHADOW | PROPONE | — | — | 🔵 | — |
| SKILL_KB_AUDITOR | `kb-audit` | SHADOW | PROPONE | — | — | 🔵 | — |
| SKILL_PROFORMA_BUILDER | `proforma` | SHADOW | PROPONE | — | — | 🔵 | — |

**Temperatura de aprendizaje:**
🔵 Frío (0–2 outputs pendientes) · 🟡 Tibio (3–5) · 🔴 Caliente (6+, consolidar urgente)

**Columna Memoria:** `—` = no existe aún · `SKILL_MEM_{ID}` = archivo activo

---

## Detalle por Skill

### SKILL_AMAZON_OPS
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   EJECUTA_INTERNO
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Pendiente primer ciclo SHADOW
```

### SKILL_CLIENT_SERVICE
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   PROPONE
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Pendiente primer ciclo SHADOW
```

### SKILL_COMPLIANCE_CHECKER
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   EJECUTA_INTERNO
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Pendiente primer ciclo SHADOW
```

### SKILL_COPY
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   PROPONE
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Creado 2026-04-16. Derivado de PLB_COPY. Primer ciclo SHADOW pendiente. Ceiling PROPONE — todo copy pasa compliance antes de publicar.
```

### SKILL_DEMAND_FORECASTER
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   PROPONE
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Pendiente primer ciclo SHADOW
```

### SKILL_EXPERIMENT_RUNNER
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   EJECUTA_INTERNO
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Pendiente primer ciclo SHADOW. Requiere gate PLB_EXPERIMENTACION antes de ejecutar.
```

### SKILL_HUMANIZE_BRAND
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   PROPONE
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Pendiente primer ciclo SHADOW
```

### SKILL_HUMANIZE_COMMS
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   PROPONE
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Pendiente primer ciclo SHADOW
```

### SKILL_KB_AUDITOR
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   AUTO_NOTIFICA
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Pendiente primer ciclo SHADOW. Único skill candidato a AUTO_NOTIFICA por naturaleza auditora.
```

### SKILL_PROFORMA_BUILDER
```
Estado:              SHADOW
Autonomía actual:    PROPONE
Autonomía ceiling:   PROPONE
Ejecuciones total:   0
Ejecuciones SHADOW:  0
Approval rate:       —
Edit-light rate:     —
Rejection rate:      —
Pendientes approval: 0
Outputs sin consolidar: 0
Última ejecución:    —
Próxima revisión:    —
Notas:              Pendiente primer ciclo SHADOW. Márgenes CEO-ONLY — ceiling permanece en PROPONE.
```

---

## Criterios de Promoción de Autonomía

Un skill solo puede subir de nivel de autonomía cuando cumple:

| Condición | Threshold |
|-----------|-----------|
| Ejecuciones en nivel actual | ≥ 10 |
| Approval rate | ≥ 80% |
| Edit-light rate (≤20% edición) | ≥ 60% |
| Rejection rate | ≤ 10% |
| Días estables sin error grave | ≥ 14 |
| AgentMemory activa | Sí |
| Aprobación CEO | Sí (siempre) |

Promoción de SHADOW → ACTIVE: condiciones anteriores con ≥ 3 ejecuciones (threshold reducido para primer nivel).

---

## Criterios de Degradación de Autonomía

Degradación automática (sin aprobación CEO requerida) si:
- Rejection rate > 30% en últimas 5 ejecuciones
- Error grave en acción de alto impacto
- Dependencia KB rota (ref → archivo inexistente o DEPRECATED)

---

## Registro de Ejecuciones

Formato de entrada por ejecución:

```
[YYYY-MM-DD] SKILL_{ID}
  Trigger:     {trigger_word}
  Estado:      {estado al ejecutar}
  Output tipo: {draft | reporte | análisis | acción_interna}
  Feedback:    {approved | approved_with_edits | rejected | escalated}
  Edición %:   {0-100}
  Corrección:  {tono | datos | estructura | policy | scope | —}
  Consolidar:  {sí | no | pendiente}
  Notas:       {observación relevante si aplica}
```

---

## Historial de Cambios de Estado

| Fecha | Skill | Cambio | Razón |
|-------|-------|--------|-------|
| 2026-04-16 | Todos | Creación inicial en SHADOW | Implementación arquitectura AgentSpec/Runtime/Memory |

---

Changelog:
- v1.0 (2026-04-16): Creación. Dashboard único AgentRuntime para 9 skills. Incluye criterios de promoción/degradación, registro de ejecuciones y temperatura de aprendizaje.
