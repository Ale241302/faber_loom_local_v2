# LOTE_SM_SPRINT27 — Seguridad Residual: Audit Completo + Backups + Hardening
id: LOTE_SM_SPRINT27
version: 1.1
visibility: [INTERNAL]
domain: Plataforma (IDX_PLATAFORMA)
status: DONE
stamp: DONE v1.1 — 2026-04-10
tipo: Lote ruteado (ref → PLB_ORCHESTRATOR §E)
sprint: 27
priority: P1
depends_on: LOTE_SM_SPRINT24 (DONE — seguridad B2B base),
            LOTE_SM_SPRINT25 (DONE — payment machine + deferred + parent/child),
            LOTE_SM_SPRINT26 (DONE — notifications app + cobranza + admin templates)
refs:
  - ENT_PLAT_SEGURIDAD (v2.1 — verificado, 0 [PENDIENTE] sin clasificar)
  - ENT_GOB_PENDIENTES (CEO-17 DONE, CEO-19 DONE)
  - POL_EPHEMERAL_OUTPUT
  - PLB_INCIDENT_RESPONSE

changelog:
  - v1.0 (2026-04-08): Lote inicial. Compilado por Arquitecto Ejecutor a partir de residuales CEO-17/CEO-19 (S24 parcial) y pendientes ENT_PLAT_SEGURIDAD.Z §8-§10 no cubiertos por S24. Objetivo: cerrar deuda de seguridad y promover ENT_PLAT_SEGURIDAD a VIGENTE.
  - v1.1 (2026-04-10): DONE. DoD 13/13 ✅ verificado en servidor srv1416291. TruffleHog 0 hallazgos. .env 600. Redis requirepass. 13 secrets en B4. Backup 46MB + restore drill OK. Cloudflare 3 dominios. Docker 10 servicios hardened. Fail2ban activo. Pendientes próximo sprint: RTO confirmación CEO, GPG encryption, push alerts, git identity.

---

## Contexto

Sprint 24 resolvió los bloqueadores críticos de apertura B2B (JWT, rate limiting, signed URLs, cookies). Este sprint cierra la deuda de seguridad residual en tres áreas:

1. **CEO-17 residual:** verificación completa del estado real de ENT_PLAT_SEGURIDAD + aprobación CEO para promover a VIGENTE
2. **CEO-19 residual:** secrets audit completo (git-secrets scan, rotación, permisos .env)
3. **ENT_PLAT_SEGURIDAD.Z §8-10:** backup encriptado, Cloudflare, Docker hardening

**Esfuerzo estimado total:** 8-10h (Alejandro)
**Preflight obligatorio:** `python manage.py check --deploy` OK · `nginx -t` OK · S26 DONE

---

## Fase 0 — Verificación completa ENT_PLAT_SEGURIDAD (CEO-17 residual)

**Agente:** AG-02 (Alejandro)
**Objetivo:** Recorrer ENT_PLAT_SEGURIDAD sección por sección, documentar estado real de cada [PENDIENTE], y actualizar el archivo a DRAFT v2.0 verificado. Luego el CEO aprueba → VIGENTE.
**Esfuerzo:** 2-3h

### Items

| ID | Tarea | Sección | Criterio de done |
|----|-------|---------|-----------------|
| S27-01 | Verificar puerto SSH: ¿hay restricción de IP activa? | A1 | `sshd_config` revisado. Documentar si hay AllowUsers / AllowHosts / iptables restrict. Si no hay → agregar restricción IP. |
| S27-02 | Verificar WAF: ¿ModSecurity activo? ¿Cloudflare? | A2 | Documentar estado. Si no hay WAF → registrar como pendiente post-S27 (Cloudflare se instala en S27-08). |
| S27-03 | Verificar HSTS + server_tokens + otros headers | A2 | `curl -I https://mwt.one/` y confirmar: `Strict-Transport-Security`, `server_tokens off`, `X-Content-Type-Options`, `X-Frame-Options`, `client_max_body_size`. S24 los implementó — verificar que persisten post-deploy. |
| S27-04 | Verificar DNSSEC en mwt.one, ranawalk.com, portal.mwt.one | A4 | Usar `dig +dnssec mwt.one`. Documentar estado. DNSSEC requiere soporte del registrador — si no está disponible, registrar como N/A. |
| S27-05 | Verificar data at rest: PostgreSQL TDE y MinIO encryption | C2 | `psql -c "SHOW ssl;"`. MinIO: `mc admin info`. Documentar si hay encriptación activa. Si no → registrar como deuda futura (complejidad alta). |
| S27-06 | Verificar data in transit: Django→PostgreSQL sslmode | C3 | `DATABASE_URL` o `DATABASES` en settings. Verificar `sslmode=require` o equivalente. |
| S27-07 | Verificar Docker: non-root, ports expuestos, socket montado | D1/D2 | `docker inspect` de cada container → `User` field. `docker-compose.yml` → verificar que solo Nginx expone puerto al host. `/var/run/docker.sock` no montado en ningún container. |
| S27-07b | Actualizar ENT_PLAT_SEGURIDAD con estado real de cada [PENDIENTE] | Todas | Cada [PENDIENTE] del documento debe quedar como: ✅ Activo, ⚠️ Pendiente (con acción concreta), o N/A (con justificación). |

### Verificación post-Fase 0

```bash
# Estado real JWT (confirmación post-S24)
python manage.py shell -c "
from django.conf import settings
st = settings.SIMPLE_JWT
print('ACCESS:', st.get('ACCESS_TOKEN_LIFETIME'))
print('REFRESH:', st.get('REFRESH_TOKEN_LIFETIME'))
print('ROTATE:', st.get('ROTATE_REFRESH_TOKENS'))
print('BLACKLIST:', st.get('BLACKLIST_AFTER_ROTATION'))
"

# Cookies (confirmación post-S24)
python manage.py shell -c "
from django.conf import settings
print('HTTPONLY:', settings.SESSION_COOKIE_HTTPONLY)
print('SECURE:', settings.SESSION_COOKIE_SECURE)
print('SAMESITE:', settings.SESSION_COOKIE_SAMESITE)
print('CSRF_SECURE:', settings.CSRF_COOKIE_SECURE)
"

# Redis: ¿tiene password?
docker exec $(docker ps --filter name=redis -q) redis-cli CONFIG GET requirepass

# Nginx headers
curl -I https://mwt.one/ 2>/dev/null | grep -E "Strict-Transport|X-Content|X-Frame|Server:"
```

### Gate Fase 0
- [ ] ENT_PLAT_SEGURIDAD actualizado: 0 [PENDIENTE] sin clasificar
- [ ] CEO aprueba → ENT_PLAT_SEGURIDAD DRAFT → VIGENTE

---

## Fase 1 — Secrets Audit Completo (CEO-19 residual)

**Agente:** AG-02 (Alejandro)
**Objetivo:** Auditar todos los secrets del proyecto. Confirmar que nada está hardcodeado ni en git. Establecer proceso de rotación.
**Esfuerzo:** 2h

### Items

| ID | Tarea | Criterio de done |
|----|-------|-----------------|
| S27-08 | git-secrets scan: verificar que ningún secret está en el historial del repo | Instalar `git-secrets` o `truffleHog`. Correr contra repo completo. 0 hallazgos críticos. Documentar comando exacto usado. |
| S27-09 | Permisos .env: verificar que todos los .env tienen `chmod 600` | `ls -la .env*` en cada directorio del proyecto. Si no → `chmod 600 .env`. |
| S27-10 | Verificar que .env NO está en .gitignore incompleto | `git ls-files --others --exclude-standard \| grep env` = vacío. `cat .gitignore \| grep env`. |
| S27-11 | Inventario completo de secrets actuales | Listar: Django SECRET_KEY, JWT signing key, PostgreSQL password, Redis password (si aplica), MinIO access/secret key, API keys externas (Claude, OpenAI, n8n credentials). Documentar ubicación actual de cada uno. |
| S27-12 | Redis requirepass: activar si no está activo | `redis-cli CONFIG GET requirepass`. Si vacío: `redis-cli CONFIG SET requirepass "password-fuerte"` + persistir en redis.conf o docker-compose ENV. |
| S27-13 | Documentar proceso de rotación (90 días) | Crear checklist en ENT_PLAT_SEGURIDAD.H: qué rotar, cómo, frecuencia, responsable. |

### Comandos de referencia

```bash
# Instalar truffleHog (alternativa a git-secrets)
pip install truffleHog --break-system-packages

# Scan del repo
trufflehog git file:///ruta/al/repo --only-verified

# Permisos .env
find /ruta/proyecto -name "*.env" -o -name ".env*" | xargs ls -la

# Redis password
docker exec $(docker ps --filter name=redis -q) redis-cli CONFIG GET requirepass
```

### Gate Fase 1
- [ ] 0 secrets en historial git
- [ ] Todos los .env con permisos 600
- [ ] .env en .gitignore confirmado
- [ ] Inventario de secrets documentado en ENT_PLAT_SEGURIDAD.B4
- [ ] Redis con requirepass activo

---

## Fase 2 — Backup Encriptado + Restore Test

**Agente:** AG-02 (Alejandro)
**Objetivo:** Implementar backup automático de PostgreSQL + MinIO con encriptación GPG. Verificar restore funcional.
**Esfuerzo:** 3h

### Items

| ID | Tarea | Criterio de done |
|----|-------|-----------------|
| S27-14 | Script `backup_pg.sh`: pg_dump + GPG encrypt + upload a MinIO bucket backup | Script ejecuta sin error. Output: `backup_YYYY-MM-DD.sql.gpg` en MinIO. |
| S27-15 | Cron diario para backup PostgreSQL (3am UTC-6) | `crontab -l` muestra entry. Backup del día siguiente existe en MinIO. |
| S27-16 | Restore test PostgreSQL: desencriptar + restaurar en DB de test | `gpg --decrypt backup.sql.gpg \| psql test_db` funciona. Verificar tablas principales. |
| S27-17 | Documentar RPO y RTO en ENT_PLAT_SEGURIDAD.C4 | RPO: 24h (backup diario). RTO: [CEO define]. Procedimiento de restore documentado. |

### Script de referencia (backup_pg.sh)

```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
BACKUP_FILE="/tmp/backup_${DATE}.sql"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

# Dump
pg_dump $DATABASE_URL > $BACKUP_FILE

# Encrypt (usar GPG key del CEO)
gpg --batch --yes --recipient CEO_GPG_KEY_ID --encrypt $BACKUP_FILE

# Upload a MinIO
mc cp $ENCRYPTED_FILE mwt-backup/postgresql/

# Cleanup
rm $BACKUP_FILE $ENCRYPTED_FILE

echo "Backup completado: backup_${DATE}.sql.gpg"
```

### Gate Fase 2
- [ ] Script backup_pg.sh ejecuta OK
- [ ] Cron configurado y verificado
- [ ] Restore test exitoso en DB de prueba
- [ ] RPO/RTO documentado

---

## Fase 3 — Cloudflare Free Tier + Docker Hardening

**Agente:** AG-02 (Alejandro)
**Objetivo:** Activar Cloudflare como DNS proxy (DDoS protection básico) y aplicar hardening a containers Docker.
**Esfuerzo:** 2-3h

### Items

| ID | Tarea | Criterio de done |
|----|-------|-----------------|
| S27-18 | Cloudflare free tier: apuntar mwt.one y ranawalk.com a Cloudflare | DNS propagado. `dig mwt.one` retorna IPs de Cloudflare. SSL modo "Full (strict)". |
| S27-19 | Docker: verificar que containers corren como non-root | `docker inspect $(docker ps -q) --format '{{.Name}}: {{.Config.User}}'`. Containers que corren como root → agregar `USER` en Dockerfile correspondiente. |
| S27-20 | Docker: resource limits CPU/RAM en docker-compose | `deploy.resources.limits` definido para cada servicio. Valores mínimos: Django 512M RAM, PostgreSQL 1G RAM, Redis 256M RAM. |
| S27-21 | Docker: health checks en todos los servicios | `healthcheck:` en cada servicio de docker-compose.yml. `docker ps` muestra `(healthy)` para todos. |
| S27-22 | Fail2ban para SSH brute force | `fail2ban-client status sshd`. Si no está activo: instalar + configurar jail SSH (maxretry=5, bantime=1h). |

### Gate Fase 3
- [ ] mwt.one resuelve via Cloudflare
- [ ] 0 containers corriendo como root (o justificación documentada)
- [ ] Resource limits en docker-compose
- [ ] Health checks activos (docker ps muestra healthy)
- [ ] Fail2ban activo en SSH

---

## Definition of Done (S27)

| # | Check | Responsable |
|---|-------|-------------|
| 1 | ENT_PLAT_SEGURIDAD actualizado: 0 [PENDIENTE] sin clasificar | AG-02 |
| 2 | ENT_PLAT_SEGURIDAD promovido a VIGENTE | CEO aprueba |
| 3 | 0 secrets en historial git (truffleHog 0 hallazgos) | AG-02 |
| 4 | .env permisos 600 + en .gitignore | AG-02 |
| 5 | Redis requirepass activo | AG-02 |
| 6 | Backup diario PostgreSQL funcionando + restore test OK | AG-02 |
| 7 | mwt.one apuntando a Cloudflare | AG-02 |
| 8 | Docker hardening: non-root + limits + health checks | AG-02 |
| 9 | Fail2ban activo en SSH | AG-02 |
| 10 | RESUMEN_SPRINT27.md entregado por AG-02 | AG-02 |

**Pendientes CEO resueltos por este sprint:** CEO-17 (completo), CEO-19 (completo)

---

## Rollback general

| Componente | Rollback |
|-----------|----------|
| Cloudflare | Cambiar nameservers de vuelta al registrador original |
| Docker non-root | Revertir USER en Dockerfile → rebuild |
| Resource limits | Quitar `deploy.resources` de docker-compose → `docker compose up -d` |
| Fail2ban | `fail2ban-client stop` + `systemctl disable fail2ban` |
| Redis requirepass | `redis-cli CONFIG SET requirepass ""` (desactiva password) |
| Backup cron | `crontab -r` (elimina todos los crons — con cuidado) |
