# Evidencia de rotación de credenciales — E5-2

**ID:** EVIDENCIA_ROTACION_20260713  
**Fecha:** 2026-07-13  
**Responsable:** [PENDIENTE — Ops / CEO]  
**Repo commit de referencia:** `3cc6514`  
**VPS:** `root@187.77.218.102:2222`  

---

## 1. Alcance

Este documento registra la ejecución del runbook de seguridad operativa
`docs/OPERACION_VPS_E3.md` correspondiente a la Etapa 5 (madurez operativa).

## 2. Checklist de rotación

| Ítem | Estado | Evidencia / comando | Responsable |
|------|--------|---------------------|-------------|
| Backup previo de `/opt/faber_loom` y DB | [ ] | `ls -la /opt/backups/faberloom/pre-rotacion-*` | Ops |
| Rotación password root VPS | [ ] | `lastlog` / bitácora del proveedor | Ops |
| SSH solo llaves (`PasswordAuthentication no`) | [ ] | `grep PasswordAuthentication /etc/ssh/sshd_config` | Ops |
| Rotación claves correo compartidas (SMTP/IMAP) | [ ] | `docs/ENT_PLAT_CONNECTORS.md` actualizado | CEO/Ops |
| `.env` fuera de git y permisos 600 | [ ] | `ls -la /opt/faber_loom/.env` | Ops |
| Reinicio servicios post-rotación | [ ] | `docker compose ps` healthy | Ops |

## 3. Comandos ejecutados

```bash
# [PENDIENTE — copiar aquí salida real de cada paso]
```

## 4. Resultado

- **Estado:** [PENDIENTE / COMPLETADO PARCIAL / COMPLETADO]
- **Observaciones:**
- **Próxima revisión:** [fecha + 90 días]

## 5. Referencias

- `docs/OPERACION_VPS_E3.md`
- `docs/ENT_PLAT_CONNECTORS.md`
