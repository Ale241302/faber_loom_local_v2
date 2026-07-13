# ENT_GOB_PROTOCOLOS
id: ENT_GOB_PROTOCOLOS
version: 0.2
status: DRAFT
visibility: [INTERNAL]
domain: Gobernanza (IDX_GOBERNANZA)
Protocolos P0-P10 de escalamiento
> **Nota de accesibilidad:** El contenido fuente (RW_07_Protocolos_Pendientes) es un documento externo anterior a la KB. Las reglas documentadas en esta sección son las únicas disponibles para un agente. Cuando se migre el contenido, este playbook se expande y la nota se retira.
aplica_a: [MWT]

---
Changelog:
- v0.1 (2026-03-14): version: field agregado (normalización Ola A).
- v0.1 (2026-03-14): visibility: INTERNAL + status: DRAFT agregados (Ola B).
- v0.2 (2026-07-13): Añadida cadencia trimestral de revisión de backup smoke (E5-2).

---

## Protocolo de cadencia trimestral — backup smoke (E5-2)

**Frecuencia:** Cada 90 días, o tras cualquier incidente de infraestructura.  
**Responsable:** Ops / DevOps (hat `ops`), con revisión del CEO.  
**Objetivo:** Garantizar que el procedimiento de backup/restore de FaberLoom sigue siendo válido y que los reportes de smoke no superan las 48 horas de antigüedad.

### Checklist

1. Verificar que el cron de backup smoke esté activo:
   ```bash
   crontab -l | grep backup_restore_smoke
   ```
2. Confirmar que el último reporte `BACKUP_SMOKE_*.md` tenga menos de 48 horas:
   ```bash
   python app/scripts/check_backup_smoke_freshness.py --max-age-hours 48
   ```
3. Ejecutar un smoke manual si el reporte está stale:
   ```bash
   python app/scripts/backup_restore_smoke.py
   python app/scripts/check_backup_smoke_freshness.py --max-age-hours 48
   ```
4. Revisar que las alertas del detector `stale_backup_smoke` lleguen al ciclo ambiental.
5. Actualizar `docs/audits/EVIDENCIA_ROTACION_<fecha>.md` si la revisión implica rotación de credenciales.
6. Registrar el resultado en este archivo bajo "Registro de ejecuciones".

### Registro de ejecuciones

| Fecha | Responsable | Resultado | Próxima revisión |
|-------|-------------|-----------|------------------|
| 2026-07-13 | Kimi Code CLI / Ops | Parcial: cron backup Postgres configurado, smoke verde, detector `stale_backup_smoke` operativo. Pendiente revisión humana de rotación de credenciales y migración MinIO. | 2026-10-11 |
