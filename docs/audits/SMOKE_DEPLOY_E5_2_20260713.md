# Smoke test de deploy — E5-2

**Fecha:** 2026-07-13  
**VPS:** `root@187.77.218.102:2222`  
**Directorio:** `/opt/faber_loom`  
**Commit deployado:** `f62ae80` (`main`)  
**Tag E4:** `e4-cierre-20260712` → `6d15f97`  
**Suite previa al deploy:** 741 passed / 12 skipped / 0 failed / 33 warnings  
**Responsable:** Kimi Code CLI

---

## 1. Resumen

Deploy de E5-2 completado exitosamente desde `main`. Se incorporaron:

- Detector `stale_backup_smoke` en `app/src/ambient_detectors.py`.
- Script `app/scripts/check_backup_smoke_freshness.py` con `--max-age-hours`, `--json`, `--run-smoke`.
- Soporte para artifacts SQLite (`BACKUP_SMOKE_*.md`, `*.faberloom`) y Postgres (`backups/faberloom_postgres_*.sql.gz`).
- Tests `app/tests/test_e5_2_backup_freshness_detector.py`.
- Dockerfile y `docker-compose.yml` ajustados para incluir `app/scripts` y persistir `docs/audits`.
- Cron nocturno de backup Postgres añadido en el VPS.

Contenedores healthy, schema 48 verificado, backup freshness check verde.

## 2. Pasos ejecutados

```bash
ssh -p 2222 root@187.77.218.102
cd /opt/faber_loom
git pull origin main
docker compose up -d --build
```

## 3. Estado de contenedores

| Contenedor | Estado | Puertos |
|------------|--------|---------|
| `faberloom-api` | Up (healthy) | 8200 → 8000 |
| `faberloom-postgres` | Up (healthy) | 5435 → 5432 |
| `faberloom-minio` | Up (healthy) | 9100 → 9000, 9101 → 9001 |

## 4. Health checks

```bash
curl -fsS http://localhost:8200/api/health
```

Respuesta:

```json
{"status":"ok","app":"FaberLoom","schema_version":48,"database_path":"/data/faberloom.sqlite3"}
```

## 5. Backup smoke freshness

Comando:

```bash
docker compose exec -T api python app/scripts/check_backup_smoke_freshness.py --max-age-hours 48
```

Resultado:

```text
OK: latest backup artifact faberloom_postgres_20260713_181013.sql.gz is 0.0h old (threshold 48h)
```

## 6. Cron configurado

```cron
30 3 * * * cd /opt/faber_loom && docker compose exec -T postgres pg_dump -U faberloom -d faberloom --clean --if-exists --create | gzip > /opt/faber_loom/data/backups/faberloom_postgres_$(date -u +\%Y\%m\%d_\%H\%M\%S).sql.gz && docker compose exec -T api python app/scripts/check_backup_smoke_freshness.py --max-age-hours 48 >> /var/log/faberloom_backup_smoke.log 2>&1
```

## 7. Veredicto

🟢 **Deploy E5-2 exitoso.** Producción corre desde `main` con schema 48, backup smoke verde y cron configurado.

## 8. Pendientes humanos/ops

1. **Ops:** ejecutar runbook `docs/OPERACION_VPS_E3.md` y completar `docs/audits/EVIDENCIA_ROTACION_20260713.md`.
2. **Ops:** ejecutar migración MinIO a prefijo por tenant y completar `docs/audits/EVIDENCIA_MINIO_MIGRACION_20260713.md`.
3. **CEO/AM:** agendar auditoría de capacidades del curador (Skills).
4. **Curador/AM:** ejecutar smoke funcional (login → chat general → brief → shadow-report) con usuario real.
