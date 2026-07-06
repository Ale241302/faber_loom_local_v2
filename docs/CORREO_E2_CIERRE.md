# Cierre formal — Correo en instancia compartida (E2-2)

**Fecha:** 2026-07-06  
**Hito:** E2-2 — Roles + HITL multi-user + WorkLoom compartido  
**Sub-hito:** Correo real con flag en instancia compartida  
**Estado:** ✅ CERRADO (código + runbook + tests)

---

## 1. Decisiones

- **Instancia compartida identificada** mediante `FABERLOOM_SHARED_INSTANCE`.
- **Flag de correo** sigue siendo `FABERLOOM_ENABLE_EMAIL_CONNECTOR`; ambos se exponen en `GET /api/features`.
- **Credenciales por AM**: en instancia compartida se rechaza el fallback a variables de entorno globales (`FABERLOOM_IMAP_*`, `FABERLOOM_SMTP_*`). Cada usuario debe configurar su propia cuenta IMAP y SMTP.
- **App-password obligatoria**: para autenticación tipo `password` se exige `is_app_password=1` en IMAP y SMTP; de lo contrario el backend responde `422`.
- **Rotación controlada**: endpoint `POST /api/workspaces/{id}/admin/imap-config/{account_id}/rotate` actualiza la contraseña, registra `rotated_at` y escribe evento de auditoría `mail.imap_credentials_rotated`.

---

## 2. Entregables

| Entregable | Ubicación | Estado |
|---|---|---|
| Flag de instancia compartida | `app/src/features.py`, `app/src/main.py`, `app/src/models.py` | ✅ |
| Migración v25 (`is_app_password`, `rotated_at`) | `app/src/models.py` | ✅ |
| Bloqueo de fallback legacy en shared mode | `app/src/api.py` (`_resolve_smtp_config`, `api_sync_mail`) | ✅ |
| Endpoint de rotación IMAP | `app/src/api.py` + `app/src/db.py` | ✅ |
| UI app-password checkbox | `app/static/js/app.jsx` | ✅ |
| Tests E2-2 correo compartido | `app/tests/test_e2_2_mail_shared_instance.py` | ✅ |
| Runbook de operación | `docs/OPERACION_CORREO_E2.md` | ✅ |
| Cierre formal | `docs/CORREO_E2_CIERRE.md` | ✅ |

---

## 3. Resultado de tests

```bash
python -m pytest tests/test_e2_2_mail_shared_instance.py tests/test_sl5_mail.py tests/test_sl5_imap.py -v
```

```text
20 passed, 7 warnings in 14.56s
```

- 8 tests nuevos de instancia compartida/app-password/rotación.
- 12 tests SL5 existentes siguen verdes (modo no compartido mantiene compatibilidad).

---

## 4. Pendientes operativos (requieren entorno real)

Los siguientes ítems no pueden ejecutarse en este entorno local sin credenciales reales ni Postgres productivo; quedan para el dogfood en instancia compartida:

1. Generar app-passwords reales por AM en el proveedor de correo.
2. Activar `FABERLOOM_SHARED_INSTANCE=true` y `FABERLOOM_ENABLE_EMAIL_CONNECTOR=true` en producción.
3. Ejecutar caso real: recibir → draft → aprobar → enviar.
4. Probar rotación de credenciales con cuenta real.
5. Ensayar rollback completo y verificar revocación en el proveedor.

---

## 5. Próximos pasos

1. Correr suite completa del proyecto para confirmar regresión cero.
2. Actualizar knowledge graph (`graphify update .`).
3. Validar el runbook con un AM en instancia de staging.
4. Continuar con E2-2 WorkLoom compartido y HITL multi-user.

---

## 6. Notas de seguridad

- El campo `password` nunca se devuelve al frontend; solo `has_password`.
- En instancia compartida un usuario solo puede rotar sus propias credenciales (`403` en caso contrario).
- El fallback a variables de entorno está deshabilitado en shared mode para evitar una única credencial compartida.
- Los eventos de sincronización, draft, envío y rotación se escriben en `audit_log` con `correlation_id` (E2-0).
