# Smoke test de deploy — E5-0

**Fecha:** 2026-07-13  
**VPS:** `root@187.77.218.102:2222`  
**Directorio:** `/opt/faber_loom`  
**Commit deployado:** `6d15f97` (`main`)  
**Tag:** `e4-cierre-20260712`  
**Suite previa al deploy:** 728 passed / 12 skipped / 0 failed / 33 warnings  
**Responsable:** Kimi Code CLI

---

## 1. Resumen

Deploy de E5-0 completado exitosamente desde `main`. Contenedores healthy, schema 48 verificado, endpoints críticos responden sin errores 5xx.

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

Health check público (`http://187.77.218.102:8200/api/health`) también responde OK.

## 5. Smoke de endpoints

| Endpoint | Método | Auth | Status esperado | Status real | Observación |
|----------|--------|------|-----------------|-------------|-------------|
| `/api/health` | GET | No | 200 | 200 | Schema 48 |
| `/api/auth/login` | POST | No | 401/422 | 422 | Endpoint existe, validación de campos |
| `/api/me` | GET | No | 401 | 401 | Cookie HttpOnly requerida |
| `/api/workspaces` | GET | No | 401 | 401 | Sesión requerida |

No se observaron errores 500 ni timeouts.

## 6. Veredicto

🟢 **Deploy E5-0 exitoso.** Producción corre desde `main` con schema 48. Los smoke de autenticación/health pasan. Quedan pendientes smoke funcionales de login/chat/brief/shadow-report que requieren credenciales de usuario real y no deben ejecutarse sin HITL.

## 7. Pendientes humanos día 1 de E5

1. **CEO:** iniciar compra certificado ATV.
2. **CEO:** elegir design partner #1.
3. **CEO/AM:** agendar auditoría de capacidades del curador.
4. **Curador/AM:** ejecutar smoke funcional (login → chat general → brief → shadow-report) con usuario real.
