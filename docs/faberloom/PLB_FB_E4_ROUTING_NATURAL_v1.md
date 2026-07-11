# PLB — Promoción a Routing Natural (E4-2)

## Propósito

Este documento define la gobernanza para promover un workspace de modo
`shadow` a `natural`, y los criterios de degradación automática. El objetivo es
que la promoción sea medible, reversible y siempre aprobada por un humano con
autoridad (owner o curador designado).

## Autonomy Ladder (E4)

| Nivel | Modo routing | Qué hace el agente | Ejemplos |
|---|---|---|---|
| 0 | `shadow` | Planifica, compara, no ejecuta. | Genera `planner_decision_log`; reporte de ahorro proyectado. |
| 1 | — | (reservado) Ejecuta pasos internos con HITL obligatorio. | No usado en E4. |
| 2 | `natural` | Ejecuta planes multi-paso internos (texto, KB, resumen, imagen). | "Resume este PDF y genera una imagen del resumen". |
| 3+ | — | Efecto externo (correo, WhatsApp, factura). | **Bloqueado en E4**: siempre draft-first + HITL. |

## Criterios de promoción shadow → natural

Para que un owner/curador pueda promover un workspace a `natural`:

1. **Tiempo o volumen:** ≥ 2 semanas en `shadow` **o** ≥ 50 decisiones shadow
   registradas en `planner_decision_log`.
2. **Ahorro proyectado ≥ 0:** el costo estimado por el planner es menor o igual
   al costo real del camino manual en la ventana de análisis (14 días por
   defecto).
3. **Cero decisiones absurdas:** revisión manual del curador usando checklist
   (ver abajo) sin hallazgos bloqueantes.
4. **Oscillation Counter:** si el workspace fue degradado de `natural` a
   `shadow` 2 veces, queda en cooldown de 30 días antes de una nueva promoción.

## Checklist de revisión del curador

- [ ] El planner nunca eligió un capability fuera de la allowlist del workspace.
- [ ] Ningún paso shadow proyectó un costo >150% del costo real del paso manual.
- [ ] Las respuestas del camino manual y el plan shadow son equivalentes en
      calidad para una muestra aleatoria (≥5 casos).
- [ ] No hay fugas de datos cross-workspace o cross-tenant en los logs.
- [ ] El workspace no es canario ni de producción crítica sin autorización del
      CEO.

## Degradación automática natural → shadow

Un workspace en `natural` vuelve a `shadow` automáticamente (sin HITL) si:

1. **Overrun de costo:** el costo real de una ventana (24h) supera el costo
   estimado del planner en >150%.
2. **Regeneración elevada:** la tasa de regeneración/rechazo de outputs sube
   >X% vs el baseline manual del workspace (X definido por el curador,
   default 20%).

En ambos casos se escribe un evento de auditoría `living_agent.routing.degraded`
y se notifica al owner del workspace.

## Procedimiento de promoción

1. Owner/curador consulta `GET /api/workspaces/{ws}/routing/promotion-readiness`
   para ver los criterios cuantitativos.
2. Si están verdes, el sistema genera un `confirmation_token` determinista
   (SHA-256 del `workspace_id + "promote-shadow"`).
3. Owner envía `POST /api/workspaces/{ws}/routing/promote` con
   `{"mode": "natural", "confirmation_token": "..."}`.
4. El sistema escribe `routing.mode = natural` a nivel workspace, registra
   `audit_writer` con acción `workspace.routing.promoted` y `approved_by` del owner.

## Rollback

Cualquier owner puede revertir a `shadow` enviando `POST /api/workspaces/{ws}/routing/promote`
con `{"mode": "shadow", "confirmation_token": "..."}` donde el token es
`SHA-256(workspace_id + "rollback-natural")`. La degradación automática no requiere token.

## Endpoints

- `GET /api/workspaces/{ws}/routing/promotion-readiness?days=14` — owner/curador/admin.
- `POST /api/workspaces/{ws}/routing/promote` — owner/curador/admin; body `{mode, confirmation_token}`.
- Degradación automática: el orquestador ejecuta `degrade_workspace_if_needed()` tras cada
  corrida natural; si el costo real de las últimas 24h supera el estimado en >150%,
  el workspace vuelve a `shadow` y se audita `living_agent.routing.degraded`.

## Responsabilidades

- **Curador:** revisión manual, ajuste de umbrales X, excepciones.
- **Owner:** decide promover/rollback, recibe alertas de degradación.
- **Sistema:** mide, loguea, aplica degradación automática, nunca auto-promueve.
