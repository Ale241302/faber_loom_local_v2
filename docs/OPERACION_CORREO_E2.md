# Operación de correo en instancia compartida (E2-2)

**Alcance:** FaberLoom/SpaceLoom Etapa 2 — instancia interna compartida MWT.  
**Objetivo:** activar el conector de correo de forma segura, con credenciales por AM (app-password), rotación documentada, caso real end-to-end y rollback controlado.

---

## 1. Requisitos previos

- [ ] E2-0 cerrado: Context, auditoría, tenant canario, roles/permisos.
- [ ] E2-1 operativo: Postgres+RLS, backup/restore probado, instancia compartida desplegada.
- [ ] Variable de entorno `FABERLOOM_SHARED_INSTANCE=true` en `.env`.
- [ ] Variable `FABERLOOM_ENABLE_EMAIL_CONNECTOR=true` para exponer la superficie.
- [ ] Ninguna credencial legacy `FABERLOOM_IMAP_*` / `FABERLOOM_SMTP_*` en el entorno compartido.

---

## 2. Habilitar flag en instancia compartida

1. Editar `.env` en el host:

   ```bash
   FABERLOOM_SHARED_INSTANCE=true
   FABERLOOM_ENABLE_EMAIL_CONNECTOR=true
   ```

2. Validar que `/api/features` reporta ambos flags:

   ```bash
   curl -s https://app.faberloom.ai/api/features | jq
   # {
   #   "email_connector_enabled": true,
   #   "shared_instance": true
   # }
   ```

3. Verificar que el conector **rechaza** credenciales globales:
   - Intentar `POST /api/workspaces/{id}/mail/sync` sin cuentas IMAP configuradas → `503`.
   - Intentar `POST /api/workspaces/{id}/mail/{id}/send` sin SMTP configurado → `503`.

---

## 3. Onboarding de un AM con app-password propia

### 3.1 Generar app-password en el proveedor de correo

- Gmail: https://myaccount.google.com/apppasswords
- Microsoft 365: https://account.live.com/proofs/AppPassword
- Otro proveedor IMAP: usar el mecanismo de contraseñas de aplicación disponible.

**Reglas:**
- Nunca usar la contraseña principal de la cuenta.
- Nunca compartir la app-password con otro usuario ni guardarla fuera de FaberLoom.
- Etiquetarla de forma reconocible, p. ej. `FaberLoom-AM-Alvaro`.

### 3.2 Alta de cuenta IMAP

1. Admin > IMAP del workspace.
2. Completar:
   - Host, puerto, usuario.
   - App-password en el campo de contraseña.
   - Marcar **"Es app-password"**.
   - Marcar **"Solo lectura"**.
   - Carpeta(s): `["INBOX"]` por defecto.
   - Marcar **"Cuenta por defecto"** si es la principal del AM.
3. Guardar.

Validación de seguridad (backend):
- Si `auth_type=password` y `is_app_password=0`, el endpoint devuelve `422` en instancia compartida.

### 3.3 Alta de SMTP saliente

1. Admin > SMTP del workspace.
2. Completar host, puerto, usuario, from email y app-password.
3. Marcar **"Es app-password"**.
4. Probar con **"Probar"**. El backend envía un correo de prueba al usuario autenticado.

---

## 4. Rotación de credenciales IMAP

### 4.1 Cuándo rotar

- Cada 90 días por política.
- Tras cualquier sospecha de exposición.
- Inmediatamente después de cerrar un incidente de credenciales (p. ej. credenciales entregadas a un agente cloud).

### 4.2 Procedimiento

1. Generar una nueva app-password en el proveedor.
2. En FaberLoom, ir a Admin > IMAP.
3. Seleccionar la cuenta y usar **"Rotar credenciales"** (o llamar al endpoint):

   ```bash
   curl -X POST \
     https://app.faberloom.ai/api/workspaces/{workspace_id}/admin/imap-config/{account_id}/rotate \
     -H "Content-Type: application/json" \
     -d '{"password":"nueva-app-password"}'
   ```

4. Verificar que `rotated_at` se actualiza y la próxima sincronización usa la nueva clave.
5. Revocar la app-password anterior en el proveedor.
6. Revisar `audit.jsonl` / tabla `audit_log` por el evento `mail.imap_credentials_rotated`.

### 4.3 Restricciones en instancia compartida

- Un usuario solo puede rotar cuentas cuyo `user_id` coincida con su sesión.
- Intento de rotación ajena → `403`.

---

## 5. Caso real end-to-end: recibir → draft → aprobar → enviar

### 5.1 Recibir

1. El AM presiona **Sincronizar** en la bandeja del workspace.
2. Backend lee solo mensajes no leídos (`UNSEEN`) de la carpeta configurada.
3. El correo se clasifica en categoría (`rfq`, `cobranza`, `soporte`, `seguimiento`, `spam`, `other`) usando solo remitente y asunto — el cuerpo nunca se usa como instrucción.

### 5.2 Generar borrador

1. Seleccionar el correo y presionar **Generar respuesta**.
2. El draft se crea con status `draft` y se vincula al correo (`mail_message.draft_id`).
3. Revisar hard facts, citas y advertencias antes de aprobar.

### 5.3 Aprobar

1. Revisor con rol distinto (o segundo AM/curador) abre el draft.
2. Presiona **Aprobar** con doble confirmación (`confirmed=true`).
3. El draft pasa a status `approved`.

### 5.4 Enviar

1. En el correo, presionar **Enviar**.
2. El endpoint exige:
   - `confirmation_token` determinista.
   - `idempotency_key` único.
   - Draft en status `approved`.
3. Backend envía vía SMTP usando la config del usuario.
4. Se registra `mail.sent` en auditoría con actor, rol y `idempotency_key`.

### 5.5 Criterio de cierre

- [ ] Al menos un correo real recibido, draftado, aprobado y enviado.
- [ ] Auditoría completa: `mail.sync`, `mail.drafted`, `draft.approved`, `mail.sent`.
- [ ] Cero envíos sin aprobación previa.
- [ ] Cero uso de credenciales globales.

---

## 6. Rollback / deshabilitación

### 6.1 Rollback rápido (conservar datos)

1. Poner `FABERLOOM_ENABLE_EMAIL_CONNECTOR=false` y reiniciar.
2. Los endpoints de correo devuelven `404`.
3. Los correos ya sincronizados permanecen en DB pero no se procesan nuevos.

### 6.2 Rollback completo (revocar credenciales)

1. Ejecutar paso 6.1.
2. En Admin > IMAP, eliminar todas las cuentas del workspace.
3. En Admin > SMTP, eliminar la configuración (sobrescribir con vacío o eliminar vía DB/admin).
4. Revocar todas las app-passwords en el proveedor de correo.
5. Purgar `mail_outbox` con status `failed` si contiene datos sensibles:

   ```sql
   DELETE FROM mail_outbox WHERE status = 'failed';
   ```

6. Forzar rotación del secret `FABERLOOM_SECRET_KEY` si hubo riesgo de exfiltración.
7. Verificar en logs que no quedan credenciales en texto plano.

### 6.3 Rollback de despliegue (infra)

1. Restaurar backup SQLite/Postgres previo al cambio.
2. Revertir compose a imagen previa.
3. Confirmar que `FABERLOOM_SHARED_INSTANCE` y `FABERLOOM_ENABLE_EMAIL_CONNECTOR` tienen los valores deseados.

---

## 7. Checklist de cierre formal

- [ ] `FABERLOOM_SHARED_INSTANCE=true` activo y validado.
- [ ] `FABERLOOM_ENABLE_EMAIL_CONNECTOR=true` activo.
- [ ] Credenciales legacy eliminadas del entorno.
- [ ] Cada AM con app-password propia (IMAP + SMTP).
- [ ] Rotación de credenciales probada y auditada.
- [ ] Caso real E2E ejecutado: recibir → draft → aprobar → enviar.
- [ ] Rollback documentado y ensayado.
- [ ] Tests E2-2 de correo pasan.
- [ ] Knowledge graph actualizado.

---

## 8. Referencias

- `docs/ROLES_PERMISSIONS_MATRIX_E2.md`
- `docs/CONTEXT_RLS_CONTRACT_E2.md`
- `docs/AUTH_SESSION_CONVERGENCIA_E2.md`
- `docs/faberloom/SPEC_SPACELOOM_IMAP_CONNECTOR_v1.md`
- `app/tests/test_e2_2_mail_shared_instance.py`
