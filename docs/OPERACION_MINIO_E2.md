# Operación de MinIO en instancia compartida (E2-6 Fase 1)

**Alcance:** FaberLoom/SpaceLoom Etapa 2 — instancia interna compartida MWT (`187.77.218.102`).  
**Objetivo:** desplegar, operar y recuperar la instancia MinIO dedicada de FaberLoom con sellado por workspace, URLs presigned y ningún bucket público.

**Política de frontend:** no se migra React UMD salvo que un bloqueo real lo exija.

---

## 1. Requisitos previos

- [ ] E2-5 cerrado y estable en producción (`schema_version >= 28`).
- [ ] Acceso SSH al host `187.77.218.102:2222` con privilegios para editar `/opt/faber_loom`.
- [ ] Control de la zona DNS `faberloom.ai`.
- [ ] `mwt-nginx` operando como reverse proxy para `app.faberloom.ai`.
- [ ] Ruta de backup disponible (mismo destino que Postgres, ej. `/opt/backups/faberloom/minio`).
- [ ] Docker Compose v2+ y red externa `mwt_default` creada.

---

## 2. DNS

Crear **solo** registros tipo A con proxy de Cloudflare **apagado (DNS only)**. El proxy de Cloudflare free limita uploads a ~100 MB y rompe presigned URLs.

| Nombre | Tipo | Contenido | Proxy | Uso |
|---|---|---|---|---|
| `minio.faberloom.ai` | A | `187.77.218.102` | DNS only | API S3 + presigned URLs |
| `console.minio.faberloom.ai` | A | `187.77.218.102` | DNS only | Consola web administrativa |

Validar:

```bash
dig +short minio.faberloom.ai
dig +short console.minio.faberloom.ai
```

---

## 3. Host, puertos y firewall

- El contenedor `faberloom-minio` publica:
  - `9100` → puerto S3 interno `9000`.
  - `9101` → puerto de consola interno `9001`.
- `mwt-nginx` escucha en `80/443` y hace `proxy_pass` a `127.0.0.1:9100` / `9101`.
- El firewall del host solo debe exponer `80`, `443`, `2222` y, **solo si es estrictamente necesario para depuración**, `9101` desde IPs autorizadas. Nunca publicar `9100` directamente a Internet sin nginx.

---

## 4. Configuración de `mwt-nginx`

En este host el proxy es el contenedor `mwt-nginx` del stack `/opt/mwt`. Agregar `/opt/mwt/nginx/faberloom-minio.conf` y montarlo en el servicio `nginx` del `docker-compose.yml` de MWT, luego `docker compose up -d nginx`.

### S3 API

```nginx
server {
    listen 443 ssl http2;
    server_name minio.faberloom.ai;

    client_max_body_size 0;
    proxy_buffering off;
    proxy_request_buffering off;

    location / {
        proxy_pass http://127.0.0.1:9100;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}

server {
    listen 80;
    server_name minio.faberloom.ai;
    return 301 https://$server_name$request_uri;
}
```

### Consola web

```nginx
server {
    listen 443 ssl http2;
    server_name console.minio.faberloom.ai;

    client_max_body_size 0;
    proxy_buffering off;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";

    location / {
        proxy_pass http://127.0.0.1:9101;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}

server {
    listen 80;
    server_name console.minio.faberloom.ai;
    return 301 https://$server_name$request_uri;
}
```

Recargar:

```bash
cd /opt/mwt
docker compose up -d nginx
```

Nota: si el certificado es self-signed (`/etc/nginx/ssl/nginx.crt`), los navegadores mostrarán advertencia hasta que se configure Let’s Encrypt u otro emisor.

---

## 5. Secrets y variables de entorno

Editar `/opt/faber_loom/.env`. Ejemplo:

```bash
# Root de MinIO (solo para bootstrap y emergencias)
FL_MINIO_ROOT_USER=FL_MINIO_ROOT_USER_CHANGE_ME_32CHARS
FL_MINIO_ROOT_PASSWORD=FL_MINIO_ROOT_PASSWORD_CHANGE_ME_64CHARS

# Credencial de servicio de faberloom-api (NO usar root)
FL_MINIO_SERVICE_USER=faberloom-api
FL_MINIO_SERVICE_PASSWORD=FL_MINIO_SERVICE_PASSWORD_CHANGE_ME_64CHARS

# Endpoints públicos
FL_MINIO_SERVER_URL=https://minio.faberloom.ai
FL_MINIO_BROWSER_REDIRECT_URL=https://console.minio.faberloom.ai

# La API usa el nombre de servicio dentro de la red de Docker
FL_MINIO_ENDPOINT=faberloom-minio:9000
FL_MINIO_ACCESS_KEY=${FL_MINIO_SERVICE_USER}
FL_MINIO_SECRET_KEY=${FL_MINIO_SERVICE_PASSWORD}
FL_MINIO_SECURE=false

# Límites
FL_MAX_UPLOAD_SIZE_BYTES=524288000      # 500 MB
FL_MAX_GENERATED_SIZE_BYTES=2147483648  # 2 GB
```

**Reglas:**
- Longitud mínima root password: 32 caracteres.
- Longitud mínima service password: 32 caracteres.
- Nunca versionar `.env`.
- Nunca usar root user en `FL_MINIO_ACCESS_KEY/SECRET_KEY`.

---

## 6. Deploy de MinIO

### 6.1 Levantar solo MinIO

```bash
cd /opt/faber_loom
source .env
docker compose up -d faberloom-minio
```

Verificar salud:

```bash
docker compose ps faberloom-minio
docker compose logs --tail 50 faberloom-minio
```

### 6.2 Crear buckets

Desde dentro del contenedor o con `mc` local apuntando a `https://minio.faberloom.ai`:

```bash
mc alias set faberloom https://minio.faberloom.ai "$FL_MINIO_ROOT_USER" "$FL_MINIO_ROOT_PASSWORD"
mc mb faberloom/fl-uploads
mc mb faberloom/fl-generated
```

**Buckets privados siempre.** Verificar que no estén públicos:

```bash
mc anonymous get faberloom/fl-uploads
mc anonymous get faberloom/fl-generated
# Debe decir "Access: private"
```

La API es la única entidad que emite URLs presigned.

### 6.3 Crear usuario de servicio y policy

Policy `faberloom-api-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::*",
        "arn:aws:s3:::fl-uploads",
        "arn:aws:s3:::fl-uploads/*",
        "arn:aws:s3:::fl-generated",
        "arn:aws:s3:::fl-generated/*"
      ]
    }
  ]
}
```

Aplicar:

```bash
mc admin policy create faberloom faberloom-api ./faberloom-api-policy.json
mc admin user add faberloom "$FL_MINIO_SERVICE_USER" "$FL_MINIO_SERVICE_PASSWORD"
mc admin policy attach faberloom faberloom-api --user "$FL_MINIO_SERVICE_USER"
```

### 6.4 Redesplegar API

```bash
cd /opt/faber_loom
docker compose pull api
docker compose up -d api
```

Verificar health:

```bash
curl -s https://app.faberloom.ai/api/health | jq
```

---

## 7. Verificación post-deploy

### 7.1 API ve el storage

```bash
curl -s https://app.faberloom.ai/api/health | jq
# schema_version debe ser 29
```

### 7.2 Flujo end-to-end con un workspace de prueba

1. Crear workspace.
2. `POST /api/workspaces/{id}/objects/presigned-upload` con un PDF pequeño.
3. Subir el archivo a la URL PUT devuelta.
4. `POST /api/workspaces/{id}/objects/confirm`.
5. `GET /api/workspaces/{id}/objects/{id}/url` y descargar.
6. `DELETE /api/workspaces/{id}/objects/{id}?confirmation_token=...`.

### 7.3 Test de fuga

Ejecutar localmente contra una copia de test o contra el entorno de staging:

```bash
pytest app/tests/test_e2_6_object_leak.py -v
```

Resultado esperado: **0 fugas cross-workspace / cross-tenant**.

---

## 8. Backup y restore

### 8.1 Backup nocturno con `mc mirror`

El script automatizado vive en `/opt/faber_loom/scripts/minio-backup.sh` y está en cron diario a las 03:00:

```bash
ls /opt/faber_loom/scripts/minio-backup.sh
sudo cat /var/log/faberloom-minio-backup.log
```

Para reinstalar o modificar:

```bash
crontab -e
# 0 3 * * * /opt/faber_loom/scripts/minio-backup.sh
```

Contenido del script (resumen):

```bash
mc alias set local http://127.0.0.1:9100 "$FL_MINIO_ROOT_USER" "$FL_MINIO_ROOT_PASSWORD"
mc mirror --overwrite --remove local/fl-uploads /opt/backups/faberloom/minio/fl-uploads
mc mirror --overwrite --remove local/fl-generated /opt/backups/faberloom/minio/fl-generated
```

`--remove` mantiene el destino sincronizado; usar con cuidado si se necesita retención point-in-time. En ese caso reemplazar por `mc cp --recursive` con fecha en el path.

### 8.2 Smoke test de restore

Script de referencia ejecutado tras el primer backup:

```bash
mkdir -p /tmp/minio-restore-test
docker run -d --name minio-restore-test -p 9200:9000 -p 9201:9001 \
  -v /tmp/minio-restore-test:/data \
  -e MINIO_ROOT_USER=restoretest \
  -e MINIO_ROOT_PASSWORD=restoretest123 \
  minio/minio:RELEASE.2025-09-07T16-13-09Z server /data --console-address ":9001"

sleep 5
mc alias set restoretest http://127.0.0.1:9200 restoretest restoretest123
mc mb restoretest/fl-uploads
mc mb restoretest/fl-generated
mc mirror /opt/backups/faberloom/minio/fl-uploads restoretest/fl-uploads
mc mirror /opt/backups/faberloom/minio/fl-generated restoretest/fl-generated
mc ls restoretest/fl-uploads
mc ls restoretest/fl-generated

# Limpiar
docker stop minio-restore-test && docker rm minio-restore-test && rm -rf /tmp/minio-restore-test
```

Resultado esperado: ambos buckets son listables y los objetos son legibles.

Documentar el resultado en `harness/reports/` o en el changelog operativo.

---

## 9. Rotación de credenciales de servicio

### 9.1 Cuándo rotar

- Cada 90 días por política.
- Tras sospecha de exposición de `FL_MINIO_SERVICE_PASSWORD`.
- Inmediatamente después de cerrar un incidente de seguridad.

### 9.2 Procedimiento sin downtime

1. Generar nueva contraseña de servicio:

   ```bash
   NEW_PASS=$(openssl rand -base64 48)
   echo "$NEW_PASS"
   ```

2. Crear nuevo usuario en MinIO y asignar la misma policy:

   ```bash
   mc admin user add faberloom faberloom-api-new "$NEW_PASS"
   mc admin policy attach faberloom faberloom-api --user faberloom-api-new
   ```

3. Actualizar `.env`:

   ```bash
   FL_MINIO_SERVICE_PASSWORD="$NEW_PASS"
   ```

4. Redesplegar la API para que tome el nuevo secret:

   ```bash
   cd /opt/faber_loom
   docker compose up -d api
   docker compose logs --tail 20 api
   ```

5. Verificar health y subir un objeto de prueba.

6. Eliminar el usuario anterior:

   ```bash
   mc admin user remove faberloom faberloom-api
   # Si el antiguo se llamaba igual, crear el nuevo con nombre distinto,
   # luego renombrar o volver a crear con la nueva contraseña y borrar el viejo.
   ```

---

## 10. Kill switch

### 10.1 Degradar uploads (mantener la app funcionando)

Editar `.env`:

```bash
FL_MAX_UPLOAD_SIZE_BYTES=0
FL_MAX_GENERATED_SIZE_BYTES=0
```

Redesplegar API:

```bash
cd /opt/faber_loom
docker compose up -d api
```

Todos los `presigned-upload` devolverán `413 Content Too Large`.

### 10.2 Apagar MinIO por completo

```bash
cd /opt/faber_loom
docker compose stop faberloom-minio
```

La API seguirá arrancando porque el lifespan captura el error, pero cualquier operación de storage fallará. No se perderán datos en SQLite; los objetos quedan inaccesibles hasta reiniciar el servicio.

### 10.3 Corte de red de emergencia

Bloquear puertos en el host (ej. con `ufw`):

```bash
sudo ufw deny 9100
sudo ufw deny 9101
sudo ufw reload
```

---

## 11. Rollback

### 11.1 Rollback de código

Si un deploy de la API rompe el storage:

```bash
cd /opt/faber_loom
git log --oneline -5
git checkout <commit-estable>
docker compose build api
docker compose up -d api
```

Último commit estable conocido: el de cierre de E2-5 (`ef502fc`) o el tag correspondiente.

### 11.2 Rollback de datos MinIO

Si se corrompen buckets o se borran objetos por error:

```bash
# Detener MinIO
cd /opt/faber_loom
docker compose stop faberloom-minio

# Restaurar volumen desde backup (ejemplo con rsync)
sudo rsync -avP --delete /opt/backups/faberloom/minio/ /var/lib/docker/volumes/faber_loom_faberloom_minio_data/_data/

# Levantar
docker compose up -d faberloom-minio
```

**Atención:** esto sobrescribe el estado actual. Para recuperación granular preferir `mc cp` de objetos individuales.

---

## 12. Monitoreo de disco

Script `/opt/faber_loom/scripts/minio-disk-alert.sh` corre cada hora y escribe en syslog si el uso de `/var/lib/docker` supera el 80%:

```bash
sudo tail /var/log/faberloom-minio-disk-alert.log
```

Para extender a Slack/email, modificar el script y añadir el webhook/servidor SMTP.

---

## 13. Checklist de emergencia

| Síntoma | Primer paso | Segundo paso |
|---|---|---|
| Uploads rechazados con 413 | Revisar `FL_MAX_UPLOAD_SIZE_BYTES` y tamaño del objeto | Verificar espacio en disco del host |
| Presigned URL no funciona | Confirmar que `minio.faberloom.ai` es DNS-only | Revisar nginx `client_max_body_size 0` |
| API no arranca | `docker compose logs api` | Verificar `FL_MINIO_ENDPOINT` y credenciales |
| Fuga sospechada | Cambiar service password y rotar | Ejecutar `test_e2_6_object_leak.py` y auditar `object` table |
| Consola no carga | Revisar `console.minio.faberloom.ai` DNS-only | Verificar websockets en nginx |
| Backup falla | Revisar espacio en `/opt/backups` | Verificar alias `mc` y credenciales root |

---

## 13. Referencias

- Plan: `Plan/PLAN_DESARROLLO_SPACELOOM_ETAPA2_v1.md`, Anexo A.
- Compose: `docker-compose.yml`.
- Código: `app/src/storage.py`, `app/src/db.py`, `app/src/api.py`.
- Tests: `app/tests/test_e2_6_storage.py`, `app/tests/test_e2_6_object_leak.py`.
