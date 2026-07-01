# MANIFIESTO_APPEND_20260419_FABERLOOM_BLUEPRINT
fecha: 2026-04-19
autor: Claude (Cowork)
tipo: ARQUITECTURA
trigger: CEO — consolidación blueprint v1 beta en SPEC_ canónico tras 3 rondas de endurecimiento + ronda final de limpieza
aplica_a: [FaberLoom]

---

## Resumen

Persistencia del Blueprint Técnico FaberLoom v1 Beta como `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` en KB. El blueprint vivía solo en transcript de sesión; ahora queda como documento único de verdad, ejecutable, 17 secciones, 968 líneas. Limpieza final elimina toda inconsistencia residual entre ULID y UUIDv7, modelo mixto de `memory_chunk`, placeholders de Sprint 1 y ambigüedades de observabilidad.

## Archivos creados

- `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md` v1.0 DRAFT — blueprint técnico ejecutable para ventana beta 2026-04-20 → 2026-06-14. Cubre: convención UUIDv7 FROZEN, 20 tablas FROZEN distribuidas S1/S2/S3, modelo de identidad (tenant/user_account/department/user_department/session), `memory_chunk` DDL final + 7 índices + 4 policies RLS + retrieval canónico, `docker-compose.dev.yml` (4 contenedores con mocks), `docker-compose.staging.yml` (11 contenedores con Traefik+ACME), Sprint 1 funcional con 9 tablas vía migraciones 0001+0002 y 34 archivos listados, 3 dashboards Grafana obligatorios (`api_http.json`, `rmq_flow.json`, `outbox_health.json`), 8 métricas Prometheus mínimas, 5 alertas obligatorias, tabla de 12 secretos, backup RPO 24h/RTO 2h con restore mensual, 10 jobs operativos con `job_execution UNIQUE(name, scheduled_for)` como lock distribuido sin Redis, taxonomía de `audit_event.action`, matriz procesos obligatorios vs colapsables, checklist binaria de 15 ítems, riesgos cerrados vs abiertos a v1.5.

## Archivos modificados

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `project_faberloom_v1_blueprint.md` (memoria) | EDIT — ubicación actualizada | Nota que blueprint ya no vive solo en transcript, ahora persiste como `SPEC_FABERLOOM_ARCHITECTURE_v1_BLUEPRINT.md`. |
| `MEMORY.md` (índice auto-memory) | EDIT — entrada refrescada | Hook actualizado para reflejar SPEC persistido + decisiones finales UUIDv7 / 11 contenedores staging / 4 dev / Sprint 1 scope. |

## Decisiones clave consolidadas

1. **UUIDv7 client-side** (`uuid_utils`) en lugar de ULID string. Preserva orden temporal y `::uuid` casts válidos en RLS. Elimina contradicción crítica detectada en ronda 3.
2. **20 tablas FROZEN v1** distribuidas: S1 (9 tablas core — identity, sessions, outbox, audit, job_execution), S2 (7 tablas agentes + memoria), S3 (4 tablas compliance + CRM mínimo).
3. **`memory_chunk` final:** `owner_department_id` (NULL salvo scope='dept'), `owner_user_id` (NULL salvo scope='user'), `created_by` (NOT NULL, solo audit — nunca filtro de scope). `CHECK chk_scope_owner` garantiza integridad. 4 policies RLS: `mc_read`, `mc_insert`, `mc_update`, `mc_no_delete`.
4. **Dev (4 contenedores)** vs **staging/prod (11 contenedores)** claramente separados como artifacts. Dev arranca <90s con `LITELLM_MODE=stub`, `AUTH_MODE=devbypass`, `MAIL_MODE=stdout`, `SCHEDULER_ENABLED=false`. Staging activa OIDC real, Traefik ACME, Postmark SMTP, Prometheus+Grafana.
5. **Observabilidad obligatoria staging:** Prometheus + Grafana. Jaeger OFF en S1, entra en S2. 3 dashboards obligatorios + 5 alertas obligatorias para DoD.
6. **SMTP = Postmark** (decidido sin re-debate — deliverability LatAm).
7. **Scheduler distribuido sin Redis:** `job_execution UNIQUE(name, scheduled_for)` como lock natural de Postgres.
8. **Sprint 1 scope funcional** (no placeholder): identity, tenant, sessions, outbox, audit, scheduler, backup, RLS básico. 9 tablas exactas vía migrations `0001_initial.sql` + `0002_outbox_audit_job.sql`. 34 archivos listados. DoD 11 ítems + demo 90 min.
9. **`whatsapp_worker` movido a v1.5** para no inflar container count en beta.
10. **Changelog v1.0 deroga** toda mención previa de ULID, `id TEXT`, policies viejas de `memory_chunk` con `department_id`/`created_by` como filtro de scope, ejemplos con `SET LOCAL app.tenant_id = '<ulid>'`, helper `ulid.py`. Única verdad = el SPEC.

## Ámbito del gate

CEO no invocó `indexa` formal — este MANIFIESTO se genera como cierre de R5 por creación de SPEC mayor. Checklist equivalente:

```
GATE ✅ (post-hoc, cierre de R5)
✔ Determinismo     — SPEC nuevo, no parchea SPEC_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA (lo referencia como input)
✔ Tipo             — SPEC (registro especial fuera de 8 tipos estándar, ver RW_ROOT §Registros Especiales)
✔ Stamp            — DRAFT — Promoción a APPROVED tras validación de 3 design partners pre-S4 (2026-06-14)
✔ Version          — v1.0 (creación)
✔ Impacto cruzado  — referencia SPEC_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA, ARCH_AGENT_PRINCIPLES; no toca FROZENs
✔ Pendientes       — CEO-pending: aprobación arranque Sprint 1 + confirmación window 2026-04-20 → 2026-06-14
✔ Sin inventados   — todas las cifras de RPO/RTO, container counts, métricas Prometheus son decisiones tomadas en sesión
✔ IDX              — IDX_FABERLOOM no existe aún; pendiente crear en próxima indexación o anexar a IDX existente
✔ Seguridad        — RLS session-scoped, 12 secretos tabulados, backup encriptado, leakage tests como CI gate; no amplía superficie de ataque
⚠ Sin indexa explícito — CEO no dijo `indexa`; este cierre es documentación de persistencia, no promoción a VIGENTE
```

## Refs activos

- `SPEC_USER_ADMIN_KNOWLEDGE_FLOW_v1_BETA` v1.0 DRAFT (input — define 4 scopes, 3 roles, OIDC+manual, TTL 90d, leakage CI gate)
- `ARCH_AGENT_PRINCIPLES` (P1–P13 — principios fundacionales, aplican a todo agente MWT y FaberLoom)
- `ENT_PLAT_MEMORY_STACK` (stack memoria — pgvector + Letta self-host path)
- `ENT_PLAT_KNOWLEDGE` (capa KB canónica — complementaria)

## Lo que el CEO tiene que decidir

- **Arranque Sprint 1:** confirmar go para iniciar build con scope definido (identity, tenant, sessions, outbox, audit, scheduler, backup, RLS básico). Ventana beta arranca 2026-04-20.
- **Design partners:** cerrar los 3 del wedge cotización B2B calzado seguridad (2 gratis + 1 pago mínimo) antes del corte S4.
- **Promoción a APPROVED:** requiere validación de los 3 design partners al cierre S4 (2026-06-14).
- **IDX_FABERLOOM:** decidir si se crea como dominio propio en taxonomía MWT o si FaberLoom queda como registro especial de SPEC_ dentro de PLATAFORMA.

## Stamp

DRAFT — SPEC queda en DRAFT. Promoción a APPROVED tras validación de design partners y cierre de los 15 ítems de la checklist binaria §14 del blueprint.
