# Evidencia de migración MinIO a prefijo por tenant — E5-2

**ID:** EVIDENCIA_MINIO_MIGRACION_20260713  
**Fecha:** 2026-07-13  
**Responsable:** [PENDIENTE — Ops / Dev]  
**Repo commit de referencia:** `3cc6514`  
**VPS:** `root@187.77.218.102:2222`  
**Script de migración:** `app/scripts/migrate_minio_objects_to_tenant_prefix.py`

---

## 1. Alcance

Verificar que los objetos de MinIO queden aislados bajo prefijo `tenant/<tenant_id>/`
y que no exista fuga cross-tenant tras la migración.

## 2. Checklist de migración

| Paso | Estado | Evidencia / comando | Responsable |
|------|--------|---------------------|-------------|
| Backup de buckets/objetos MinIO | [ ] | `mc mirror` o snapshot de volumen | Ops |
| Dry-run del script de migración | [ ] | `python app/scripts/migrate_minio_objects_to_tenant_prefix.py --dry-run` | Dev/Ops |
| Revisión conteos origen vs destino | [ ] | Tabla de conteos incluida abajo | Dev/Ops |
| Ejecución real de migración | [ ] | Log del script | Dev/Ops |
| Verificación origen = destino | [ ] | `mc ls --recursive` comparado | Ops |
| Smoke lectura 10 objetos aleatorios | [ ] | Lista de objetos leídos OK | Dev/Ops |
| Cleanup de objetos sin prefijo (post-verificación) | [ ] | Comando y conteos | Ops |

## 3. Conteos

| Bucket | Objetos origen | Objetos migrados | Delta | Verificado |
|--------|---------------|------------------|-------|------------|
| [PENDIENTE] | | | | |

## 4. Smoke de lectura

```bash
# [PENDIENTE — copiar salida de mc cat / mc head para 10 objetos]
```

## 5. Resultado

- **Estado:** [PENDIENTE / COMPLETADO PARCIAL / COMPLETADO]
- **Riesgos residuales:**
- **Próxima revisión:** [fecha + 90 días]

## 6. Referencias

- `app/scripts/migrate_minio_objects_to_tenant_prefix.py`
- `docs/OPERACION_VPS_E3.md`
- `docs/ENT_PLAT_STORAGE.md`
