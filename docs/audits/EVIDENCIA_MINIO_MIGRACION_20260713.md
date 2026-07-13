# Evidencia de migración MinIO a prefijo por tenant — E5-2

**ID:** EVIDENCIA_MINIO_MIGRACION_20260713  
**Fecha:** 2026-07-13  
**Responsable:** Kimi Code CLI (agente) / Alejandro  
**Repo commit de referencia:** `de12256`  
**VPS:** `root@187.77.218.102:2222`  
**Script de migración:** `app/scripts/migrate_minio_tenant_prefix.py`  

---

## 1. Alcance

Migrar todos los objetos de MinIO al layout explícito por tenant (`tenant/<tenant_id>/ws-<workspace_id>/<origin>/<object_id>/<file_name>`), manteniendo los objetos huérfanos en su lugar y moviendo los originales a `_quarantine/`.

---

## 2. Checklist de migración

| Paso | Estado | Evidencia / comando | Responsable |
|------|--------|---------------------|-------------|
| Backup de DB previo | ✅ | `/opt/faber_loom/backups/faberloom_pre_minio_migrate_20260713_185823.sql.gz` | Ops |
| Dry-run del script de migración | ✅ | `python -m app.scripts.migrate_minio_tenant_prefix --dry-run` → 44 planned, 6 orphan, 0 failed | Dev/Ops |
| Revisión conteos origen vs destino | ✅ | Ver sección 3 | Dev/Ops |
| Ejecución real de migración | ✅ | `python -m app.scripts.migrate_minio_tenant_prefix --execute` → 44 migrated, 6 orphan, 0 failed | Dev/Ops |
| Verificación DB actualizada | ✅ | `SELECT count(*) FROM object WHERE object_key LIKE 'tenant/%'` → 44 | Dev/Ops |
| Verificación layout MinIO | ✅ | `fl-uploads tenant count=22`, `fl-generated tenant count=22` | Dev/Ops |
| Cleanup de objetos sin prefijo (post-verificación) | ⏸️ | Pendiente E5-3 (purga de `_quarantine/` tras 7 días verdes) | Ops |

---

## 3. Conteos

| Bucket | Objetos escaneados | Migrados | Huérfanos | Fallidos | Verificado |
|--------|-------------------|----------|-----------|----------|------------|
| fl-uploads + fl-generated | 50 | 44 | 6 | 0 | ✅ |

Huérfanos identificados (sin fila DB):
- `testobj3.png`
- `t-tnt_5d9b14dbab2f4f61b105/ws-ws_517a8f8b08374658964b9cf8f9f34bd9/generated/obj_2ad0d5997dcb40e6a44f076033f098af/step-output.json`
- `t-tnt_5d9b14dbab2f4f61b105/ws-ws_517a8f8b08374658964b9cf8f9f34bd9/generated/obj_406929aa0d80447fa8b64b9b1b7b9e22/step-output.json`
- `t-tnt_5d9b14dbab2f4f61b105/ws-ws_517a8f8b08374658964b9cf8f9f34bd9/generated/obj_50cf7926447449b2aacaf832cc0ad1dc/step-output.json`
- `t-tnt_5d9b14dbab2f4f61b105/ws-ws_517a8f8b08374658964b9cf8f9f34bd9/generated/obj_c0b47d0ad860471099036ac6ddd8676d/imagen-generada-1783957040.png`
- `t-tnt_5d9b14dbab2f4f61b105/ws-ws_517a8f8b08374658964b9cf8f9f34bd9/generated/obj_e3d7fd19e3e44d3889b073c917ae0f4c/step-output.json`

---

## 4. Comandos ejecutados

```bash
# Backup previo
docker exec -i faberloom-postgres pg_dump -U faberloom -d faberloom | gzip \
  > /opt/faber_loom/backups/faberloom_pre_minio_migrate_$(date +%Y%m%d_%H%M%S).sql.gz

# Dry-run (requiere rol con BYPASS RLS; faberloom_app ve 0 filas por RLS)
docker exec --env-file /tmp/migrate.env -i faberloom-api \
  python -m app.scripts.migrate_minio_tenant_prefix \
  --postgres-url "$FABERLOOM_POSTGRES_URL" --dry-run \
  --report /tmp/migration_dryrun_v3.json

# Ejecución real
docker exec --env-file /tmp/migrate.env -i faberloom-api \
  python -m app.scripts.migrate_minio_tenant_prefix \
  --postgres-url "$FABERLOOM_POSTGRES_URL" --execute \
  --report /tmp/migration_execute_v3.json

# Reparación de object_keys tras descubrir que el UPDATE quedó en transacción abierta
# (fix committeado en main; reparación manual con script ad-hoc contra /tmp/migration_execute_v3.json)
```

---

## 5. Resultado

- **Estado:** COMPLETADO (con reparación manual de object_keys documentada).
- **Riesgos residuales:** Los 6 huérfanos permanecen en sus keys originales; no afectan la app. Purga programada en E5-3.
- **Próxima revisión:** 2026-10-13

---

## 6. Referencias

- `app/scripts/migrate_minio_tenant_prefix.py`
- `docs/OPERACION_VPS_E3.md`
- `docs/audits/EVIDENCIA_ROTACION_20260713.md`
