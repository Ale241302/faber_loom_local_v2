# Operación E5-1 — Routing shadow→natural

**ID:** OPERACION_E5_ROUTING_20260713  
**Tenant:** MWT (dogfood)  
**Fecha de inicio:** 2026-07-13  
**Responsable:** Curador / CEO  
**Estado:** EN PROGRESO — plantilla de evidencia

---

## Objetivo

Llevar ≥3 workspaces del tenant MWT a modo `natural` estables ≥2 semanas, ejercitar 1 rollback real, y documentar ahorro real medido por el shadow report.

## Checklist de operación

| Ítem | Estado | Evidencia | Fecha |
|---|---|---|---|
| Encender `routing.mode="shadow"` en workspaces activos de MWT | ☐ | API call / settings log | |
| Revisión semanal: shadow report, marcar absurdas | ☐ | Captura shadow report | |
| Workspace #1 cumple umbral (≥2 sem / ≥50 decisiones, ahorro ≥0, 0 absurdas) | ☐ | Token de promoción + audit event | |
| Promover workspace #1 a `natural` con token HITL | ☐ | `workspace.routing.promoted` en audit | |
| Observar 1 semana sin auto-degrade | ☐ | Health dashboard / ACE log | |
| Promover workspace #2 a `natural` | ☐ | Token + audit | |
| Promover workspace #3 a `natural` | ☐ | Token + audit | |
| Ejercitar rollback REAL de un workspace a `shadow` | ☐ | Token `rollback-natural` + `workspace.routing.rollback` | |
| Verificar que no hubo pérdida tras rollback | ☐ | Smoke de runs/decisiones post-rollback | |
| Documentar ahorro real y curva de estabilidad | ☐ | Tabla semanal abajo | |

## Curva semanal

| Semana | Workspaces en shadow | Workspaces en natural | Decisiones shadow | Ahorro proyectado USD | Decisiones absurdas | Acción |
|---|---|---|---|---|---|---|
| S1 | | | | | | |
| S2 | | | | | | |
| S3 | | | | | | |
| S4 | | | | | | |

## Promociones

| Workspace | Token usado | Audit event id | Promoted by | Promoted at |
|---|---|---|---|---|
| | | | | |

## Degradaciones / rollback

| Workspace | Modo anterior | Modo nuevo | Razón | Audit event id | Degraded/rolled back by | Fecha |
|---|---|---|---|---|---|---|
| | | | | | | |

## Lecciones / ajustes de código (si aplica)

_Si la operación revela fricción en el tablero, documentar aquí el bug y el fix, con referencia al commit._

## Sign-off

| Rol | Nombre | Fecha |
|---|---|---|
| Curador | | |
| CEO / Arquitecto | | |
