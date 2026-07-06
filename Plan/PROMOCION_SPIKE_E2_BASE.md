# Promoción del spike a base E2

**id:** PROMOCION_SPIKE_E2_BASE  
**versión:** 1.0  
**fecha:** 2026-07-06  
**estado:** aprobado para E2  

---

## 1. Resumen

Los siguientes componentes nacieron como spikes o experimentos en E1 y se promueven a base estable para E2:

| Componente | Origen E1 | Estado en E2 | Notas |
|---|---|---|---|
| Foundation Beta (auth/session/tenant/roles) | Spike M07-M20 | Runtime activo | Fuente de verdad de identidad; SSO bridge mantiene compatibilidad con JWT legacy. |
| Workspace seal + HMAC | Spike SL2/SL3 | Runtime activo | Protección de integridad por workspace. |
| Router multi-proveedor | SL1a | Runtime activo | Presupuesto, allowlist, retries y ledger de costo. |
| `SKILL.md` / rutinas | SL3a | Runtime activo | Categorías explícitas y aprobación con Context. |
| KB con citas + gold loop | SL1b/SL3b | Runtime activo | Fuentes requeridas, doble verificación para gold. |
| Inbox/correo | SL5 | Runtime activo | IMAP por workspace, drafts con HITL, outbox con idempotencia. |
| SPINE Django (legacy) | Prototipo anterior | **Archivado como referencia** | No se ejecuta; Foundation reemplaza su funcionalidad. |
| Tenant canario `canary` | Decisión E2-0 | **Runtime permanente** | Workspace sembrado desde E2-0/E2-1 con `is_canary=1`; gate obligatorio para E2-3 (M16 MWT↔canario verde en ambas direcciones). |

---

## 2. Criterios de promoción aplicados

1. **Tests de regresión verdes:** cada componente promovido tiene cobertura de tests en `app/tests/` y la suite completa pasa.
2. **Costuras contract-first:** tablas y APIs incluyen campos latentes de tenant/actor/versión.
3. **Documentación:** existen runbooks o docs de operación (migración Postgres, RLS, correo real).
4. **Riesgos P0 mitigados:** HITL, aislamiento tenant/workspace, no datos inventados, no exfiltración.
5. **Límite explícito:** SPINE Django no se mantiene como runtime; se archiva como contrato de referencia.

---

## 3. Límites y deuda técnica aceptada

- **Frontend sin build step:** se mantiene para no perder velocidad; se monitorea tamaño/tiempo de carga.
- **SQLite en E2-0:** se mantiene como fuente de verdad hasta E2-1; Postgres es planificado y ensayado.
- **Auth local con Foundation:** el bridge legacy permanece durante E2; se evaluará unificación total en E3.

---

## 4. Próximos pasos

1. E2-1: migración productiva a Postgres + RLS.
2. E2-2: roles reales, HITL multi-usuario y correo real.
3. E2-3: KB compartida con sellado y objetos/MinIO.

---

## 5. Referencias

- `Plan/PLAN_TRABAJO_E2_FUGU_v3.md`
- `docs/LESSONS_LEARNED_E1.md`
- `docs/MIGRACION_POSTGRES_E2.md`
