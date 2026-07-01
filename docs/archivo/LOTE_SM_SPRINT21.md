# LOTE_SM_SPRINT21 — Monitor de Actividad + Role-Based Sidebar
id: LOTE_SM_SPRINT21
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
status: DONE — ejecutado AG-02, migraciones aplicadas en producción 2026-04-01
version: 1.3
sprint: 21
depends_on: LOTE_SM_SPRINT20

---

## Objetivo

Observabilidad interna: extensión EventLog con metadatos de auditoría, UserNotificationState, 3 endpoints activity feed con permisos por rol, sidebar filtrado por rol, 24 tests.

## Fases ejecutadas

- **Fase 0 — Modelos**: EventLog +5 campos (user, proforma, action_source, previous_status, new_status) + 2 índices. UserNotificationState (OneToOne user, last_seen_at). Migraciones 0020-0022 con resolución de 4 incidencias (fake + ALTER manual).
- **Fase 1 — Endpoints**: GET /activity-feed/ (filtros expediente, proforma, event_type, unread_only, paginación 25/100). GET /activity-feed/count/ (slice real, no .count(), cap 99+). POST /activity-feed/mark-seen/ (avanza last_seen_at).
- **Fase 2 — Frontend**: ActivityBadge (polling 60s, pausa document.hidden, 99+). ActivityPanel (20 items, timestamp relativo, highlight unread, navegación a expediente). Sidebar role-based (CEO: 8 items, AGENT: 3, CLIENT: 3).
- **Fase 3 — Tests**: 24 tests en 6 grupos (EventLog extendido, UserNotificationState, Feed, mark-seen, Permisos, Count).

## Permisos centralizados

- `get_visible_events(user)` en activity_permissions.py
- CEO: todo. AGENT: solo expedientes donde operó. CLIENT: solo su subsidiary, excluyendo CEO_ONLY_EVENT_TYPES (cost.registered, commission.invoiced, compensation.noted).

## Archivos no tocados

state_machine/ handlers FROZEN, docker-compose.yml, sizing/, artifact_policy.py

---

Stamp: DONE — Migraciones aplicadas, servidor operativo en producción 2026-04-01
