---
id: IDX_SPACELOOM_ETAPA1
version: 1.0
status: DRAFT
visibility: [INTERNAL]
domain: FaberLoom (docs/faberloom/)
type: INDEX
stamp: DRAFT — 2026-06-30 — índice maestro del track SpaceLoom Etapa 1
aplica_a: [FaberLoom, MWT]
canonical_at: docs/faberloom/IDX_SPACELOOM_ETAPA1.md
mirror_relationship: none
---

# IDX_SPACELOOM_ETAPA1 — Índice del track SpaceLoom Etapa 1

## Propósito

Este es el índice maestro del track **SpaceLoom Etapa 1**: app de escritorio single-user, local-first, construida como spike de validación y dogfood interno de MWT.

**Si arrancás un chat nuevo para trabajar este track:** copiá `PLB_SPACELOOM_ETAPA1_KICKOFF_PROMPT_v1.md` como prompt inicial — es autocontenido y trae el contexto completo.

**Relación con el canon:** este track **no es FaberLoom Foundation Beta**. El track canónico sigue siendo `PLB_FB_FOUNDATION_BETA_v1.md` (Postgres + RLS + Next.js + 13 sprints). SpaceLoom Etapa 1 es un spike no canónico registrado en `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md`.

---

## Estado resumido del track

| Aspecto | Estado |
|---|---|
| Plan base | `PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` DRAFT v1.1 |
| Carve-out freeze | `DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md` DRAFT — **pendiente ratificación CEO** |
| Código | SL0–SL4 cerrados (221 tests verdes); SL5 diferido |
| Documentación | En catch-up: faltan specs/closers por SL |
| Registro de spike | `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md` VIGENTE v1.0 |

---

## Orden de lectura recomendado

### Para entender qué es y por qué existe
1. `DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md` — decisión que autoriza (o no) construir SL0 bajo la pausa de Foundation Beta.
2. `PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` — plan de build con secuencia SL0–SL4, costuras y riesgos.
3. `SPEC_SPACELOOM_ETAPA1_v1.md` — definición del producto: app standalone, telar completo, single-user.
4. `IDX_SPACELOOM_ETAPA1.md` — este índice.
5. `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md` — registro formal del spike como no canónico.

### Para implementar o revisar código
6. `PLB_SPACELOOM_ETAPA1_KICKOFF_PROMPT_v1.md` — prompt autocontenido para sesiones nuevas.
7. Los specs específicos de cada sub-hito (ver tabla más abajo).
8. `harness/reports/*_CLOSER_REPORT_*.md` — cierres formales del código ya construido.

---

## Artefactos del track

### Decisiones
| Documento | Status | Notas |
|---|---|---|
| `DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md` | DRAFT | Pendiente opción A/B/C del CEO |
| `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md` | VIGENTE v1.0 | Registro del spike; vive en raíz del repo |

### Planes
| Documento | Status | Notas |
|---|---|---|
| `PLAN_DESARROLLO_SPACELOOM_ETAPA1_v1.md` | DRAFT v1.1 | Plan de build SL0–SL4 + enmienda Fugu+Kimi |
| `PLB_SPACELOOM_ETAPA1_KICKOFF_PROMPT_v1.md` | DRAFT v1.0 | Prompt para nuevas sesiones |

### Specs madre (ya existen)
| Documento | Status | Rol |
|---|---|---|
| `SPEC_SPACELOOM_ETAPA1_v1.md` | DRAFT v1.0a | Definición del producto y alcance |
| `SPEC_SPACELOOM_SELFHOSTED_v1.1.md` | VIGENTE | Routing + SpaceLoom canvas |
| `SPEC_SPACELOOM_SELFHOSTED_v1.2.md` | VIGENTE | Workspaces + herencia + KB |
| `SPEC_SPACELOOM_SELFHOSTED_v1.3.md` | VIGENTE | Routine Hub + HITL + sellado |
| `SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md` | DRAFT | Correo multi-cuenta read-first |
| `SPEC_FB_ROUTING_PRESETS_v1.md` | VIGENTE | Presets y routing mínimo (compartido con Foundation Beta) |
| `SCH_FB_SKILL_MANIFEST_v2.md` | VIGENTE | Schema de SKILL.md (compartido con Foundation Beta) |
| `SPEC_FB_E0_5_VALIDATION_SLICE_v1.md` | VIGENTE | Criterios de adopción (compartido con Foundation Beta) |

### Specs/closers por sub-hito (pendientes de producir)
| Sub-hito | Documento esperado | Status | Bloqueador |
|---|---|---|---|
| SL0 | `SPEC_SPACELOOM_SL0_v1.md` o `SL0_CLOSER_REPORT_v1.md` | PENDIENTE | Ratificar freeze |
| SL1a | `SPEC_SPACELOOM_SL1a_v1.md` | PENDIENTE | SL0 |
| SL1b | `SPEC_SPACELOOM_SL1b_v1.md` | PENDIENTE | SL1a |
| SL2 | `SPEC_SPACELOOM_SL2_v1.md` | PENDIENTE | SL1b |
| SL3a | `SPEC_SPACELOOM_SL3a_v1.md` | PENDIENTE | SL2 |
| SL3b/c | `SPEC_SPACELOOM_SL3bc_v1.md` | PENDIENTE | SL3a |
| SL3.5 | `SPEC_SPACELOOM_SL3_5_v1.md` | PENDIENTE | SL3 |
| SL5 | `SPEC_SPACELOOM_SL5_v1.md` | DIFERIDO | SL3.5 + credenciales IMAP |
| SL4 | `SPEC_SPACELOOM_SL4_v1.md` | PENDIENTE | SL3.5 (o SL5 si no se difiere) |

> **Nota:** en `harness/reports/` ya existen closers informales (`SL1b_CLOSER_REPORT_v1.md`, `SL2_CLOSER_REPORT_v1.md`, etc.) producto del build. La tabla de arriba se refiere a specs formales en `docs/faberloom/`.

### Evaluaciones y auditorías
| Documento | Tipo | Status |
|---|---|---|
| `EVAL_PLAN_SPACELOOM_FUGU_ULTRA.md` | Evaluación Fugu del plan | VIGENTE |
| `EVAL_PLAN_SPACELOOM_KIMI.md` | Evaluación Kimi del plan | VIGENTE |
| `AUDIT_SPACELOOM_ETAPA1_STRESS_v1.md` | Stress audit del spike | VIGENTE |
| `AUDIT_FB_IDENTITY_NORMALIZER_v1.md` | Audit identidad | DRAFT |
| `AUDIT_FB_SESION_20260615_v1.md` | Audit sesión 2026-06-15 | DRAFT |

---

## Principios que rigen este track

1. **Dogfooded desde SL1.** Alvaro usa el producto desde el primer sub-hito con draft real.
2. **Expansion-ready, no expansion-built.** Costuras limpias para Etapa 2-3.
3. **Una entidad, no fábrica de agentes.** Los agentes son perfiles de config dentro de una Rutina.
4. **HITL absoluto + irreversibles fuera de la entidad.** Cero envío sin aprobación.
5. **Cero dato inventado.** Todo precio/dato del draft trazado a fuente de la KB.

---

## Riesgos P0

- Envío sin HITL → kill del hito.
- Injection por contenido de email → test obligatorio en SL5.
- Fuga cross-workspace → test en SL3.5.
- Dato inventado en draft → sin fuente, no se aprueba.

---

## Trazabilidad de versiones

| Versión | Fecha | Cambio |
|---|---|---|
| v1.0 | 2026-06-30 | Creación del índice. Estado DRAFT hasta ratificación del carve-out. |

---

## Pendientes de este índice

1. Ratificar `DEC_FB_SPACELOOM_FREEZE_SCOPE_v1.md`.
2. Generar specs/closers formales por SL en `docs/faberloom/`.
3. Decidir si `MANIFIESTO_APPEND_20260630_SPACELOOM_SPIKE_E1.md` se mueve a `docs/faberloom/` o se deja en raíz.
4. Actualizar `IDX_GOBERNANZA.md` cuando este índice pase a VIGENTE.
