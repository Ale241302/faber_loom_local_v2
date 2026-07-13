# Evidencia de desbloqueo E5 — 2026-07-13

## Resumen

Se implementaron los 4 ítems de desbloqueo del orden de ejecución E5-DESBLOQUEO,
convirtiendo cada bloqueo en una acción auto-ejecutable o en una acción humana
con evidencia auto-recolectada.

| Bloqueo | Script/test entregado | Acción humana residual |
|---|---|---|
| E5-4 live ATV | `app/scripts/atv_smoke.py` + `docs/RUNBOOK_ATV_CREDENCIALES.md` | CEO configura `.env` con credenciales ATV y corre `atv_smoke.py`. |
| E5-3 H3 PACK 2 | `app/scripts/load_pack2_golden.py` | CEO entrega docs reales Marluvas/Tecmater; operador corre script con `--source-dir`. |
| E5-1 routing | `app/scripts/routing_evidence_report.py` + `run_weekly_reports.py` | Promoción shadow→natural requiere aprobación humana explícita. |
| E5-6 design partner | `app/scripts/onboard_design_partner.py` | Firma del acuerdo de datos beta (`SCH_FB_ACUERDO_DATOS_BETA_v1.md`). |

## Entregables de código

- `app/scripts/atv_smoke.py` — validación sandbox/live ATV con un comando.
- `app/scripts/load_pack2_golden.py` — carga H3 + golden cases sintéticos/reales.
- `app/scripts/routing_evidence_report.py` — reporte operacional read-only.
- `app/scripts/run_weekly_reports.py` + `.sh` — cron semanal soak + routing.
- `app/scripts/onboard_design_partner.py` — tenant, owner y workspace canario.
- Tests:
  - `app/tests/test_e5_1_routing_evidence_report.py` (4 tests)
  - `app/tests/test_e5_1_weekly_reports.py` (1 test)
  - `app/tests/test_e5_3_load_pack2_golden.py` (5 tests)
  - `app/tests/test_e5_6_onboard_design_partner.py` (4 tests)
  - `app/tests/test_e5_4_atv_smoke.py` (1 test)

## Validación

- Suite local E5: **33 passed** (scripts nuevos + tests E5 previos).
- Suite completa: **768 passed, 12 skipped, 0 failed** (`pytest_e5_full_20260713.log` local).
- Graphify: **30,412 nodes / 57,119 edges** actualizado.

## Despliegue VPS

- Host: `187.77.218.102` (SSH puerto 2222, llave Ed25519 rotada en E5-2).
- Commit: `eed0776` en `main`.
- Contenedor `faberloom-api` rebuilt y healthy (`/api/health` → 200).
- Cron instalado en root:

```cron
# FaberLoom weekly soak + routing evidence reports (E5-1/E5-6)
0 9 * * 1 cd /opt/faber_loom && /usr/bin/docker compose exec -T api python /app/app/scripts/run_weekly_reports.py --db-path /data/faberloom.sqlite3 --foundation-db /data/foundation.sqlite3 --out-dir /app/docs/audits >> /var/log/faberloom-weekly.log 2>&1
```

## Reglas de oro aplicadas

- **R1**: Nada sintético se presenta como real; los casos PACK 2 llevan `[SINTETICO]`.
- **R2**: Esquema FROZEN intacto; solo inserciones en columnas existentes.
- **R11/R12**: Context tenant-scoped y audit log en cada mutación.
- **Fail-closed**: scripts requieren `--execute --approved-by` para mutar.
- **HITL**: promoción routing y acuerdo design partner requieren aprobación humana.

## Próximos pasos humanos

1. Configurar `.env` ATV y correr `app/scripts/atv_smoke.py`.
2. Entregar docs Marluvas/Tecmater y correr `app/scripts/load_pack2_golden.py --source-dir <dir>`.
3. Firmar acuerdo design partner y correr `app/scripts/onboard_design_partner.py --execute`.
4. Verificar logs semanales en `/var/log/faberloom-weekly.log`.
