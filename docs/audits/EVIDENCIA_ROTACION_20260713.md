# Evidencia de rotación de credenciales — E5-2

**ID:** EVIDENCIA_ROTACION_20260713  
**Fecha:** 2026-07-13  
**Responsable:** Kimi Code CLI (agente) / Alejandro  
**Repo commit de referencia:** `de12256`  
**VPS:** `root@187.77.218.102:2222`  

---

## 1. Alcance

Ejecutar rotación controlada de credenciales críticas según `docs/OPERACION_VPS_E3.md`, manteniendo la clave/credencial vieja hasta verificar la nueva (old-key-until-verified).

---

## 2. Checklist de rotación

| Ítem | Estado | Evidencia / comando | Responsable |
|------|--------|---------------------|-------------|
| Backup previo de `/opt/faber_loom` y DB | ✅ | `/opt/faber_loom/backups/faberloom_pre_minio_migrate_20260713_185823.sql.gz` | Ops |
| Rotación par SSH | ✅ | Nuevo par en `/root/rotacion_e5/id_ed25519_e5`, fingerprint `SHA256:7WP/iiqLr12DXRc+RfRSscTUqC/jJ4Qd+8Hv1I2riAw`; llave recogida y activada localmente; llave anterior (`sjoalfaro@gmail.com` / `SHA256:CZD4V25dS6c89cAgNbogpodAy/xopGULcd37Fl58jhg`) eliminada de `/root/.ssh/authorized_keys` | Ops |
| Rotación password Postgres app role | ✅ | `ALTER USER faberloom_app WITH PASSWORD '<new>'`; `.env` actualizado; app reiniciada y conecta OK | Ops |
| Rotación credenciales MinIO service user | ✅ | Nuevo usuario `faberloom-api-v2` con policy `faberloom-api`; R/W verificado; usuario viejo `faberloom-api` eliminado | Ops |
| `.env` fuera de git y permisos 600 | ✅ | `/opt/faber_loom/.env` presente, no en git, permisos 600 | Ops |
| Reinicio servicios post-rotación | ✅ | `docker compose ps` healthy | Ops |

---

## 3. Comandos ejecutados

### SSH
```bash
mkdir -p /root/rotacion_e5 && chmod 700 /root/rotacion_e5
ssh-keygen -t ed25519 -f /root/rotacion_e5/id_ed25519_e5 -N "" -C "faberloom-e5-rotacion-20260713"
cat /root/rotacion_e5/id_ed25519_e5.pub >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
ssh -p 2222 -i /root/rotacion_e5/id_ed25519_e5 -o PreferredAuthentications=publickey -o BatchMode=yes root@localhost echo OK
```

### SSH — recogida y retiro de llave anterior

```bash
# Desde estación de trabajo de Alejandro
scp -P 2222 -i ~/.ssh/id_ed25519 root@187.77.218.102:/root/rotacion_e5/id_ed25519_e5 ~/.ssh/faberloom_rotacion_e5/id_ed25519_e5
scp -P 2222 -i ~/.ssh/id_ed25519 root@187.77.218.102:/root/rotacion_e5/id_ed25519_e5.pub ~/.ssh/faberloom_rotacion_e5/id_ed25519_e5.pub
chmod 600 ~/.ssh/faberloom_rotacion_e5/id_ed25519_e5
ssh-keygen -lf ~/.ssh/faberloom_rotacion_e5/id_ed25519_e5.pub
# Fingerprint nueva: SHA256:7WP/iiqLr12DXRc+RfRSscTUqC/jJ4Qd+8Hv1I2riAw

# Activar localmente la nueva llave (backup de la anterior)
cp ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pre-e5-rotacion-20260713
cp ~/.ssh/id_ed25519.pub ~/.ssh/id_ed25519.pub.pre-e5-rotacion-20260713
cp ~/.ssh/faberloom_rotacion_e5/id_ed25519_e5 ~/.ssh/id_ed25519
cp ~/.ssh/faberloom_rotacion_e5/id_ed25519_e5.pub ~/.ssh/id_ed25519.pub

# Verificar acceso con la nueva llave
ssh -p 2222 -i ~/.ssh/faberloom_rotacion_e5/id_ed25519_e5 root@187.77.218.102 echo OK_E5_KEY

# Retirar llave anterior del servidor
ssh -p 2222 -i ~/.ssh/faberloom_rotacion_e5/id_ed25519_e5 root@187.77.218.102 \
  "sed -i '/sjoalfaro@gmail.com/d' /root/.ssh/authorized_keys"

# Confirmar que la anterior ya no funciona
ssh -p 2222 -o BatchMode=yes -i ~/.ssh/id_ed25519.pre-e5-rotacion-20260713 root@187.77.218.102 echo OLD_OK
# -> Permission denied (publickey,password).

# Confirmar acceso por defecto con la nueva llave
ssh -p 2222 -o BatchMode=yes root@187.77.218.102 echo OK_DEFAULT_E5_KEY
# -> OK_DEFAULT_E5_KEY
```

### Postgres app role
```bash
NEW_PG_PASS=$(openssl rand -base64 32)
docker exec -i faberloom-postgres psql -U faberloom -d faberloom \
  -c "ALTER USER faberloom_app WITH PASSWORD '$NEW_PG_PASS';"
# Actualizar FABERLOOM_POSTGRES_URL en /opt/faber_loom/.env
cd /opt/faber_loom && docker compose up -d api
# Verificación: conexión OK y object count desde app
```

### MinIO service user
```bash
mc alias set mig http://localhost:9100 <root-user> <root-password>
mc admin user add mig faberloom-api-v2 <new-password>
mc admin policy attach mig faberloom-api --user faberloom-api-v2
# Actualizar FL_MINIO_SERVICE_USER/PASSWORD en /opt/faber_loom/.env
cd /opt/faber_loom && docker compose up -d api
# Verificación R/W con nuevo service user OK
mc admin user remove mig faberloom-api
```

---

## 4. Resultado

- **Estado:** COMPLETADO PARCIAL (SSH/Postgres/MinIO rotados; password root VPS y correo no están en scope de este runbook).
- **Observaciones:**
  - La llave SSH privada fue recogida desde `/root/rotacion_e5/id_ed25519_e5` e instalada como `~/.ssh/id_ed25519` (backup en `~/.ssh/id_ed25519.pre-e5-rotacion-20260713`).
  - La llave SSH anterior (`sjoalfaro@gmail.com`) fue eliminada de `/root/.ssh/authorized_keys` y ya no permite acceso (`Permission denied (publickey,password)`).
  - Smoke SSH con la nueva llave por defecto: `OK_DEFAULT_E5_KEY`.
- **Próxima revisión:** 2026-10-13

---

## 5. Referencias

- `docs/OPERACION_VPS_E3.md`
- `docs/audits/EVIDENCIA_MINIO_MIGRACION_20260713.md`
