# Operación de rotación de credenciales VPS/SSH/correo (E3-0 t.1)

**Alcance:** FaberLoom/SpaceLoom Etapa 3 — cierre de deuda operativa de seguridad del host productivo.  
**Objetivo:** rotar password root, migrar acceso SSH a llaves asimétricas, rotar credenciales de correo compartidas y dejar evidencia auditada en el repo.  
**Host:** `187.77.218.102:2222`  
**Ruta de despliegue:** `/opt/faber_loom`  
**Estado:** procedimiento listo para ejecución con HITL (requiere acceso root y control de DNS/llaves).

---

## 1. Requisitos previos

- [ ] Acceso root al VPS `187.77.218.102:2222` por un canal seguro (consola del proveedor / rescue).
- [ ] Backup reciente de `/opt/faber_loom` (volumen `faber_loom_pgdata` ya no aplica; usar `faberloom.sqlite3`, `foundation.sqlite3`, `.env`, `audit.jsonl`).
- [ ] Control del DNS `faberloom.ai` y de los registros de correo.
- [ ] Llave SSH pública del operador designado (4096 bits, Ed25519 preferido).
- [ ] Ventana de mantenimiento de 30 minutos.

---

## 2. Inventario de secretos a rotar

| Secreto | Ubicación actual | Acción | Evidencia post-rotación |
|---|---|---|---|
| Password root del VPS | Proveedor cloud / estado actual | Generar password aleatorio de 32+ chars, guardar en gestor de secretos | Hash no recuperable; acceso solo por SSH key |
| Claves SSH del host | `~/.ssh/authorized_keys` de root y usuarios deploy | Reemplazar por llaves actuales, eliminar llaves obsoletas | `ssh -p 2222 -i ... root@187.77.218.102` funciona; password login rechazado |
| Credenciales SMTP compartidas | `.env` (`SMTP_*`, `TRADE_EMAIL_*`, `MW_DOC_EMAIL_*`) | Rotar en proveedor de correo y actualizar `.env`; reiniciar API | Test de envío HITL con confirmation token pasa |
| API keys de modelos | `.env` y `TenantSecretStore` | Rotar solo si se sospecha exposición; de lo contrario rotar en ciclo regular | Ledger de rotación en `docs/audits/` |
| MinIO root / service | `.env` (`FL_MINIO_ROOT_*`, `FL_MINIO_SERVICE_*`) | Rotar si se expusieron; sino documentar fecha de próxima rotación | `mc admin user info` confirma nuevas credenciales |

**Nota:** los valores reales no se versionan. Este documento es el procedimiento; las credenciales vivas se guardan en el gestor de secretos designado y en `/opt/faber_loom/.env`.

---

## 3. Backup previo

```bash
ssh -p 2222 root@187.77.218.102

cd /opt/faber_loom
cp .env .env.pre-rotacion-$(date +%Y%m%d-%H%M%S)
mkdir -p /opt/backups/faberloom/pre-rotacion-$(date +%Y%m%d-%H%M%S)
cp faberloom.sqlite3 foundation.sqlite3 audit.jsonl /opt/backups/faberloom/pre-rotacion-$(date +%Y%m%d-%H%M%S)/
docker compose exec faberloom-api python -m app.src.db verify-backup || true
```

---

## 4. Rotar password root

1. Desde consola del proveedor o rescue, generar password fuerte:
   ```bash
   openssl rand -base64 32
   ```
2. Aplicar al usuario root:
   ```bash
   passwd root
   ```
3. Guardar el password en el gestor de secretos; **no en `.env` ni en chat**.
4. Marcar fecha de rotación en el ledger (ver §8).

---

## 5. Migrar SSH a llaves y deshabilitar password

### 5.1 Instalar llaves autorizadas

```bash
ssh -p 2222 root@187.77.218.102

mkdir -p /root/.ssh
chmod 700 /root/.ssh
# Pegar la llave pública del operador designado
nano /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
```

Repetir para el usuario de despliegue (`faberloom-deploy` si existe) en `~/.ssh/authorized_keys`.

### 5.2 Configurar `sshd`

Editar `/etc/ssh/sshd_config` (o `/etc/ssh/sshd_config.d/99-faberloom.conf`):

```text
PermitRootLogin prohibit-password
PasswordAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
```

Validar y recargar:

```bash
sshd -t
systemctl reload sshd
```

### 5.3 Verificar

Desde otra terminal:

```bash
# Debe funcionar con llave
ssh -p 2222 -i ~/.ssh/faberloom_ed25519 root@187.77.218.102

# Debe fallar con password
ssh -p 2222 -o PubkeyAuthentication=no root@187.77.218.102
# -> Permission denied (publickey).
```

---

## 6. Rotar credenciales de correo compartidas

Las cuentas con rotación pendiente documentada son `trade@` y `mw_doc@` (fallaron con 535 en E2). El proveedor de correo real es responsabilidad del CEO/AM; no inventar.

1. Rotar password en el panel del proveedor de correo.
2. Actualizar `.env` en `/opt/faber_loom`:
   ```bash
   cd /opt/faber_loom
   nano .env
   # SMTP_TRADE_PASSWORD=...
   # SMTP_MW_DOC_PASSWORD=...
   # TRADE_EMAIL_PASSWORD=...
   # MW_DOC_EMAIL_PASSWORD=...
   ```
3. Recargar API:
   ```bash
   docker compose up -d faberloom-api
   docker compose logs --tail 30 faberloom-api
   ```
4. Test de envío HITL con confirmation token (no envío directo):
   - Crear un draft de correo en WorkLoom.
   - Aprobar con confirmation token.
   - Verificar recepción en cuenta de prueba.
   - Confirmar en `audit.jsonl` que `actor_id` y `actor_role_at_decision` están presentes.

---

## 7. Verificar `.env` fuera de git y cifrado de secretos

```bash
cd /opt/faber_loom
git status --short .env
# Debe estar ignorado (no mostrar nada).

grep -E "PASSWORD|SECRET|KEY|TOKEN" .env | wc -l
# Contar variables; validar que no haya valores por defecto como "change-me".
```

Secretos de tenant en reposición usan `TenantSecretStore` (`app/src/security/secrets.py`). Verificar que `MASTER_KEY` o `FABERLOOM_MASTER_KEY` esté presente y no sea el valor de ejemplo.

---

## 8. Ledger de rotación

Crear o actualizar `docs/audits/EVIDENCIA_ROTACION_VPS_YYYYMMMDD.md` después de ejecutar, con:

- Fecha/hora de la ventana.
- Operador responsable.
- Componentes rotados (password root, SSH keys, cuentas de correo, etc.).
- Resultado de smoke tests.
- Evidencia de que `PasswordAuthentication no` está activo (`sshd -T | grep passwordauthentication`).
- Sign-off del CEO o responsable de seguridad.

---

## 9. Smoke tests post-rotación

```bash
# 1. SSH key-only
ssh -p 2222 -i ~/.ssh/faberloom_ed25519 root@187.77.218.102 "echo OK"

# 2. API health
curl -fsS https://app.faberloom.ai/api/health || curl -fsS http://187.77.218.102:8000/api/health

# 3. Login y /api/me
curl -fsS -c /tmp/faberloom_cookies.txt -X POST https://app.faberloom.ai/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"[PENDIENTE]","password":"[PENDIENTE]"}'
curl -fsS -b /tmp/faberloom_cookies.txt https://app.faberloom.ai/api/me

# 4. Envío HITL de prueba (usar confirmation token)
# Ver app/static/js/app.jsx -> WorkLoom mail flow.

# 5. Consola MinIO (si aplica)
mc alias set faberloom https://minio.faberloom.ai "$FL_MINIO_ROOT_USER" "$FL_MINIO_ROOT_PASSWORD"
mc ls faberloom
```

---

## 10. Rollback

Si algo falla:

1. Restaurar `.env` desde backup:
   ```bash
   cp .env.pre-rotacion-... .env
   docker compose up -d faberloom-api
   ```
2. Si el acceso SSH se bloquea, usar consola de rescate del proveedor para restaurar `PasswordAuthentication yes` temporalmente.
3. Restaurar SQLite/Foundation desde backup solo en caso de corrupción (la rotación no debería tocar DB).

---

## 11. Sign-off

| Rol | Nombre | Fecha | Estado |
|---|---|---|---|
| Operador | ____________________ | ________ | ☐ |
| CEO/Security owner | ____________________ | ________ | ☐ |
| Smoke test OK | ____________________ | ________ | ☐ |

---

**Referencias:**
- `Plan/PLAN_DESARROLLO_FABERLOOM_ETAPA3_v1.md` §E3-0 t.1.
- `docs/audits/AUDIT_E3_DETAILED_CLOSURE_REPORT_20260708.md` §2.1 y §5.
- `docs/audits/ACTA_ETAPA2_TERMINADA.md` §3.1.
